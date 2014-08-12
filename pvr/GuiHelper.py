import xbmc, xbmcgui, xbmcaddon, sys, os, shutil, time, re, stat
from elisinterface.ElisEnum import ElisEnum
from pvr.Product import *
import pvr.Platform
from elisinterface.util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR

try :
	import xml.etree.cElementTree as ElementTree
except Exception, e :
	from elementtree import ElementTree

import urlparse, urllib
from subprocess import *

#gSettings = xbmcaddon.Addon( id="script.mbox" )
gSupportLanguage = [ 'Czech', 'Dutch', 'French', 'German', 'Italian', 'Polish', 'Russian', 'Spanish', 'Turkish', 'Arabic', 'Korean', 'Slovak', 'Ukrainian' ]


def GetSetting( aID ) :
	#global gSettings
	#return gSettings.getSetting( aID )
	return xbmcaddon.Addon( 'script.mbox' ).getSetting( aID )


def SetSetting( aID, aValue ) :
	#global gSettings
	#gSettings.setSetting( aID, aValue )
	xbmcaddon.Addon( 'script.mbox' ).setSetting( aID, aValue )


def RecordConflict( aInfo ) :
	import pvr.DataCacheMgr
	dataCache = pvr.DataCacheMgr.GetInstance( )
	import pvr.gui.DialogMgr as DiaMgr
	from pvr.Util import TimeToString, TimeFormatEnum

	label = [ '', '', '' ]
	
	try :
		if aInfo[0].mError == -1 :
			label[0] = MR_LANG( 'No EPG information available' )
		else :
			conflictNum = len( aInfo ) - 1
			if conflictNum > 2 :
				conflictNum = 2

			label[0] = MR_LANG( 'That recording conflicts with' )

			for i in range( conflictNum ) :
				timer = dataCache.Timer_GetById( aInfo[ i + 1 ].mParam )
				if timer :
					timer.printdebug( )
					time = '%s~%s' % ( TimeToString( timer.mStartTime, TimeFormatEnum.E_HH_MM ), TimeToString( timer.mStartTime + timer.mDuration, TimeFormatEnum.E_HH_MM ) )
					channelNum = '%04d' % timer.mChannelNo
					epgName = timer.mName
					label[i+1] = channelNum + ' ' + time + ' ' +  epgName

	except Exception, ex :
		print "Exception %s" %ex
					
	dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
	dialog.SetDialogProperty( MR_LANG( 'Error' ), label[0], label[1], label[2] )
	dialog.doModal( )


def HasCasInfoByChannel( aChannel ) :
	if not aChannel or aChannel.mError != 0 :
		#LOG_TRACE('----casCheck--------ch None')
		return

	casInfo = []

	if aChannel.mIsCA & ElisEnum.E_MEDIAGUARD :
		casInfo.append( 'S' ) #SECA MediaGuard

	if aChannel.mIsCA & ElisEnum.E_VIACCESS :
		casInfo.append( 'V' ) #Viaccess

	if aChannel.mIsCA & ElisEnum.E_NAGRA :
		casInfo.append( 'N' ) #Nagra

	if aChannel.mIsCA & ElisEnum.E_IRDETO :
		casInfo.append( 'I' ) #Irdeto

	if aChannel.mIsCA & ElisEnum.E_CONAX :
		casInfo.append( 'CO' ) #Conax

	if aChannel.mIsCA & ElisEnum.E_CRYPTOWORKS :
		casInfo.append( 'CW' ) #Cryptoworks

	if aChannel.mIsCA & ElisEnum.E_NDS :
		casInfo.append( 'ND' ) #NDS

	if aChannel.mIsCA & ElisEnum.E_BETADIGITAL :
		casInfo.append( 'B' ) #Betadigital

	if aChannel.mIsCA & ElisEnum.E_DRECRYPT :
		casInfo.append( 'DC' ) #DRECript

	if aChannel.mIsCA & ElisEnum.E_VERIMATRIX :
		casInfo.append( 'VM' ) #Verimatrix

	if aChannel.mIsCA & ElisEnum.E_OTHERS :
		casInfo.append( 'O' ) #Others

	LOG_TRACE('----------mask[%s] CasInfo[%s]'% ( aChannel.mIsCA, casInfo ) )
	return casInfo


def UpdateCasInfo( self, aChannel ) :
	from pvr.gui.GuiConfig import E_XML_PROPERTY_CAS

	if not aChannel or aChannel.mError != 0 :
		self.setProperty( 'iCasB', '' )
		self.setProperty( 'iCasI', '' )
		self.setProperty( 'iCasS', '' )
		self.setProperty( 'iCasV', '' )
		self.setProperty( 'iCasN', '' )
		self.setProperty( 'iCasCW', '' )
		self.setProperty( 'iCasND', '' )
		self.setProperty( 'iCasCO', '' )
		self.setProperty( 'iCasDC', '' )
		self.setProperty( 'iCasVM', '' )
		self.setProperty( 'iCasO', '' )
		return

	if aChannel.mIsCA > 0 :
		self.setProperty( E_XML_PROPERTY_CAS, 'True' )	

	if aChannel.mIsCA & ElisEnum.E_MEDIAGUARD :
		self.setProperty( 'iCasS', 'S' )		
	else :
		self.setProperty( 'iCasS', '' )	

	if aChannel.mIsCA & ElisEnum.E_VIACCESS :
		self.setProperty( 'iCasV', 'V' )
	else :
		self.setProperty( 'iCasV', '' )		

	if aChannel.mIsCA & ElisEnum.E_NAGRA :
		self.setProperty( 'iCasN', 'N' )	
	else :
		self.setProperty( 'iCasN', '' )	
	
	if aChannel.mIsCA & ElisEnum.E_IRDETO :
		self.setProperty( 'iCasI', 'I' )	
	else :
		self.setProperty( 'iCasI', '' )

	if aChannel.mIsCA & ElisEnum.E_CONAX :
		self.setProperty( 'iCasCO', 'CO' )	
	else :
		self.setProperty( 'iCasCO', '' )	

	if aChannel.mIsCA & ElisEnum.E_CRYPTOWORKS :
		self.setProperty( 'iCasCW', 'CW' )	
	else :
		self.setProperty( 'iCasCW', '' )	
	
	if aChannel.mIsCA & ElisEnum.E_NDS :
		self.setProperty( 'iCasND', 'ND' )	
	else :
		self.setProperty( 'iCasND', '' )	

	if aChannel.mIsCA & ElisEnum.E_BETADIGITAL :
		self.setProperty( 'iCasB', 'B' )	
	else :
		self.setProperty( 'iCasB', '' )	

	if aChannel.mIsCA & ElisEnum.E_DRECRYPT :
		self.setProperty( 'iCasDC', 'DC' )	
	else :
		self.setProperty( 'iCasDC', '' )	

	if aChannel.mIsCA & ElisEnum.E_VERIMATRIX :
		self.setProperty( 'iCasVM', 'VM' )	
	else :
		self.setProperty( 'iCasVM', '' )	
	
	if aChannel.mIsCA & ElisEnum.E_OTHERS :
		self.setProperty( 'iCasO', 'O' )	
	else :
		self.setProperty( 'iCasO', '' )	
	
	"""
	casInfo = []	
	casInfo = HasCasInfoByChannel( aChannel )
	self.setProperty( E_XML_PROPERTY_CAS, 'True' )
	if casInfo :
		for casName in casInfo :
			aPropertyID = 'iCas' + casName
			self.setProperty( aPropertyID, casName )
	else :
		return
	"""


def HasEPGComponent( aEPG, aFlag ) :
	if not aEPG or aEPG.mError != 0 :
		return 'False'

	if aFlag == ElisEnum.E_HasHDVideo :
		return ( 'True', 'False' ) [ aEPG.mHasHDVideo == 0 ]

	elif aFlag == ElisEnum.E_Has16_9Video :
		return ( 'True', 'False' ) [ aEPG.mHas16_9Video == 0 ]	

	elif aFlag == ElisEnum.E_HasStereoAudio :
		return ( 'True', 'False' ) [ aEPG.mHasStereoAudio == 0 ]	

	elif aFlag == ElisEnum.E_HasMultichannelAudio :
		return ( 'True', 'False' ) [ aEPG.mHasMultichannelAudio == 0 ]		

	elif aFlag == ElisEnum.E_HasDolbyDigital :
		return ( 'True', 'False' ) [ aEPG.mHasDolbyDigital == 0 ]		
	
	elif aFlag == ElisEnum.E_HasSubtitles :
		return ( 'True', 'False' ) [ aEPG.mHasSubtitles == 0 ]		
	
	elif aFlag == ElisEnum.E_HasHardOfHearingAudio :
		return ( 'True', 'False' ) [ aEPG.mHasHardOfHearingAudio == 0 ]		
	
	elif aFlag == ElisEnum.E_HasHardOfHearingSub :
		return ( 'True', 'False' ) [ aEPG.mHasHardOfHearingSub == 0 ]		
	
	elif aFlag == ElisEnum.E_HasVisuallyImpairedAudio :
		return ( 'True', 'False' ) [ aEPG.mHasVisuallyImpairedAudio == 0 ]		

	else :
		return 'False'

	return 'False'


def UpdatePropertyByCacheData( self, pmtEvent, aPropertyID = None ) :
	if not pmtEvent :
		LOG_TRACE( '---------------pmtEvent None' )
		return False

	ret = False
	if aPropertyID == 'HasTeletext' :
		if pmtEvent.mTTXCount > 0 :
			#LOG_TRACE( '-------------- Teletext updated by PMT cache' )
			ret = True

	elif aPropertyID == 'HasSubtitle' :
		if pmtEvent.mSubCount > 0 :
			#LOG_TRACE( '-------------- Subtitle updated by PMT cache' )
			ret = True

	elif aPropertyID == 'HasDolbyPlus' :
		#LOG_TRACE( 'pmt selected[%s] AudioStreamType[%s]'% ( pmtEvent.mAudioSelectedIndex, pmtEvent.mAudioStream[pmtEvent.mAudioSelectedIndex] ) )

		for i in range( len(pmtEvent.mAudioStream )) :
			if pmtEvent.mAudioStream[i] == ElisEnum.E_AUD_STREAM_DDPLUS : 
				ret = True
				break

	elif aPropertyID == 'HasDolby' :
		for i in range( len(pmtEvent.mAudioStream )) :
			if pmtEvent.mAudioStream[i] == ElisEnum.E_AUD_STREAM_AC3 : 
				ret = True
				break

	self.setProperty( aPropertyID, '%s'% ret )
	return ret


def UpdatePropertyByAgeRating( self, aEPG ) :
	#age info
	hasAgeRating = 'False'
	if aEPG and aEPG.mAgeRating > 0 :
		alignx = ''
		ctag = 'grey'
		hasAgeRating = 'True'
		if aEPG.mAgeRating <= 7 :
			alignx = ' '
			ctag = 'green'
		elif aEPG.mAgeRating > 7 and aEPG.mAgeRating < 18 :
			ctag = 'yellow'
		else :
			ctag = 'red'

		self.setProperty( 'EPGAgeRating', '[COLOR %s]%s%s[/COLOR]'% ( ctag, alignx, aEPG.mAgeRating ) )
	self.setProperty( 'HasAgeRating', hasAgeRating )


def EnumToString( aType, aValue ) :
	from elisinterface.ElisEnum import ElisEnum
	ret = ''
	if aType == 'type' :
		if aValue == ElisEnum.E_SERVICE_TYPE_TV :
			ret = MR_LANG( 'TV' )
		elif aValue == ElisEnum.E_SERVICE_TYPE_RADIO :
			ret = MR_LANG( 'Radio' )
		elif aValue == ElisEnum.E_SERVICE_TYPE_DATA :
			ret = MR_LANG( 'Data' )
		elif aValue == ElisEnum.E_SERVICE_TYPE_INVALID :
			ret = MR_LANG( 'Type_Invalid' )

	elif aType == 'mode' :
		if aValue == ElisEnum.E_MODE_ALL :
			ret = MR_LANG( 'All Channels' )
		elif aValue == ElisEnum.E_MODE_FAVORITE :
			ret = MR_LANG( 'Favorite' )
		elif aValue == ElisEnum.E_MODE_NETWORK :
			ret = MR_LANG( 'Network' )
		elif aValue == ElisEnum.E_MODE_SATELLITE :
			ret = MR_LANG( 'Satellite' )
		elif aValue == ElisEnum.E_MODE_CAS :
			ret = MR_LANG( 'FTA/CAS' )
		elif aValue == ElisEnum.E_MODE_PROVIDER :
			ret = MR_LANG( 'Provider' )

	elif aType == 'sort' :
		if aValue == ElisEnum.E_SORT_BY_DEFAULT :
			ret = MR_LANG( 'Default' )
		elif aValue == ElisEnum.E_SORT_BY_ALPHABET :
			ret = MR_LANG( 'Alphabet' )
		elif aValue == ElisEnum.E_SORT_BY_CARRIER :
			ret = MR_LANG( 'Carrier' )
		elif aValue == ElisEnum.E_SORT_BY_NUMBER :
			ret = MR_LANG( 'Number' )
		elif aValue == ElisEnum.E_SORT_BY_HD :
			ret = MR_LANG( 'HD' )

	elif aType == 'Polarization' :
		if aValue == ElisEnum.E_LNB_HORIZONTAL :
			ret = 'Horz'
		elif aValue == ElisEnum.E_LNB_VERTICAL :
			ret = 'Vert'
		elif aValue == ElisEnum.E_LNB_LEFT :
			ret = 'Left'
		elif aValue == ElisEnum.E_LNB_RIGHT :
			ret = 'Right'

	return ret


def AgeLimit( aPropertyAge, aEPGAge, aAgeGurantee ) :
	isLimit = False
	if aPropertyAge == 0 :
		#no limit
		isLimit = False

	else:
		#limitted
		if aPropertyAge <= aEPGAge :
			isLimit = True
			if aAgeGurantee >= aEPGAge :
				isLimit = False

		else:
			isLimit = False

	return isLimit


def ClassToList( aMode, aClassList ) :

	if aClassList :
		ilist = []
		for item in aClassList :
			req = []
			item.appendReqBuffer( req )
			ilist.append( req )
	
		if aMode == 'print' :
			LOG_TRACE( '%s'% ilist)
		elif aMode == 'convert' :
			return ilist


def ParseLabelToCh( aMode, aLabel ) :
	import re
	import pvr.gui.WindowMgr as WinMgr
	#aLabel = '[COLOR grey]1065 NGC2[/COLOR]'

	parse2 = 0

	if aMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
		parse2 = re.findall( '[0-9]\w*', aLabel )

	else :
		parse1 = re.split( ' ', aLabel )
		parse2 = re.findall( '[0-9]\w*', parse1[1] )

	#LOG_TRACE('===========aLabel[%s] parse2[%s]'% (aLabel,parse2[0]) )

	return int( parse2[0] )


gLanguage = xbmcaddon.Addon( id = 'script.mbox' )


def Strings( aStringID, aReplacements = None ) :
	#string = xbmcaddon.Addon(id = 'script.mbox').getLocalizedString(aStringID)
	string = gLanguage.getLocalizedString( aStringID )
	if aReplacements is not None :
		return string % aReplacements
	else :
		return string


def StringToListIndex( aList, aString ) :
	for i in range( len( aList ) ) :
		if aList[i].lower( ) == aString.lower( ) :
			return i

	LOG_ERR( 'Could not find any list items : %s' % aString )
	return 0


gMRStringHash = {}
gCacheMRLanguage = None


def GetInstance( ) :
	global gCacheMRLanguage
	if not gCacheMRLanguage :
		gCacheMRLanguage = CacheMRLanguage( )
	else:
		pass
		#print 'youn check already windowmgr is created'

	return gCacheMRLanguage


class CacheMRLanguage( object ) :
	def __init__( self ) :
		self.mStrLanguage = None

		scriptDir = xbmcaddon.Addon( 'script.mbox' ).getAddonInfo( 'path' )
		#xmlFile = '%s/pvr/gui/windows/MboxStrings.xml' %scriptDir
		xmlFile = '%s/resources/language/English/strings.xml' %scriptDir
		#LOG_TRACE( 'xmlFile[%s]'% xmlFile )

		self.mDefaultCodec = sys.getdefaultencoding( )
		print '---------mDefaultCodec[%s]'% self.mDefaultCodec

		parseTree = ElementTree.parse( xmlFile )
		treeRoot = parseTree.getroot( )
		global gMRStringHash
		for node in treeRoot.findall( 'string' ) :
			gMRStringHash[ node.text ] = int( node.get( 'id' ) )

		#LOG_ERR('============cache Language'!


	def StringTranslate( self, string = None ) :
		strId = gMRStringHash.get( string, None )
		#print 'strId[%s] string[%s]'% (strId, string)
		if strId :
			xmlString = Strings( strId )

			try :
				#print 'xml_string[%s] id[%s] parse[%s]'% (string, strId, xmlString)
				if xmlString == "" or xmlString == None :
					LOG_ERR( 'Could not find string' )
					return string

				string = xmlString
				if not pvr.Platform.GetPlatform( ).IsPrismCube( ) :
					string = xmlString.encode( 'utf-8' )

			except Exception, e :
				print 'Exception[%s]'% e

		#print 'strId[%s]trans[%s]'% (strId, string)
		return string.replace( '%n', '\r\n' )


gStrLanguage = GetInstance( )


def MR_LANG( aString ) :
	if xbmc.getLanguage() not in gSupportLanguage :
		return aString

	return gStrLanguage.StringTranslate( aString )
	#return aString


gSkinPosition = None


def GetInstanceSkinPosition( ):
	global gSkinPosition
	if not gSkinPosition :
		gSkinPosition = GuiSkinPosition( )
	return gSkinPosition


def CreateDirectory( aPath, aPermitPath = None ) :
	if os.path.exists( aPath ) :
		return

	os.makedirs( aPath, 0755 )
	if aPermitPath :
		shutil.copystat( aPermitPath, aPath )


def CreateFile( aPath ) :
	isAble = True
	try :
		open( aPath, 'w', 0644 )

	except Exception, e :
		isAble = False
		LOG_ERR( 'Exception[%s]'% e )

	return isAble


def RemoveDirectory( aPath ) :
	if not os.path.exists( aPath ) :
		return

	ret = False
	try :
		mode = os.stat( aPath ).st_mode
		if stat.S_ISDIR( mode ) :
			shutil.rmtree( aPath )
			ret = True
		elif stat.S_ISREG( mode ) :
			os.unlink( aPath )
			ret = True
		else :
			LOG_TRACE( 'Could not remove, non type file[%s]'% aPath )

	except Exception, e :
		LOG_ERR( 'Exception[%s]'% e )

	return ret


def RemoveUnzipFiles( aUsbPath, aZipFile = False, aReqFile = False ) :
	fileList = None

	try :
		if aZipFile :
			if not CheckDirectory( aZipFile ) :
				#LOG_TRACE('not exist unzipfile[%s]'% aZipFile )
				return False
			fileList = GetUnpackFiles( aZipFile )

			if not fileList or len( fileList ) < 1 :
				#LOG_TRACE( 'no delete files' )
				return False

			for iFile in fileList :
				if iFile[0].strip( ) :
					delFile = '%s/%s'% ( aUsbPath, iFile[0].strip( ) )
					RemoveDirectory( delFile )
					#LOG_TRACE('delete file[%s]'% delFile )

		else :
			if not CheckDirectory( aReqFile ) :
				#LOG_TRACE('not exist reqFile[%s]'% aReqFile )
				return False

			fd = open( aReqFile, 'r' )
			fileList = fd.readlines( )
			fd.close( )

			if not fileList or len( fileList ) < 1 :
				#LOG_TRACE( 'no delete files' )
				return False

			for iFile in fileList :
				if iFile.strip( ) :
					delFile = '%s/%s'% ( aUsbPath, iFile.strip( ) )
					RemoveDirectory( delFile )
					#LOG_TRACE('delete file[%s]'% delFile )

	except Exception, e :
		LOG_ERR( 'Exception[%s]'% e )

	return True


def CheckDirectory( aPath, isDir = False ) :
	isExist = os.path.exists( aPath )
	if isDir :
		mode = os.stat( aPath ).st_mode
		if stat.S_ISDIR( mode ) :
			isExist = True
		else :
			isExist = False

	return isExist


def CheckHdd( aMicroSD = False ) :
	import pvr.ElisMgr
	mCount = 2
	if aMicroSD :
		if not pvr.Platform.GetPlatform( ).IsPrismCube( ) or \
		   pvr.Platform.GetPlatform( ).GetProduct( ) == PRODUCT_OSCAR :
			mCount = 0	#1: microSD, 3: deadcated format HDD

	isMounted = False
	retList = pvr.ElisMgr.GetInstance( ).GetCommander( ).HDD_GetMountPath( )
	if retList and len( retList ) > mCount and retList[0].mError == 0 :
		isMounted = True

	return isMounted


def	HasAvailableRecordingHDD( aCheckVolume = True, aMicroSD = False ) :
	import pvr.gui.DialogMgr as DiaMgr
	from pvr.gui.GuiConfig import E_SUPPORT_EXTEND_RECORD_PATH
	import pvr.DataCacheMgr
	dataCache = pvr.DataCacheMgr.GetInstance( )

	if not CheckHdd( aMicroSD ) :
		if E_SUPPORT_EXTEND_RECORD_PATH and aCheckVolume and dataCache.Record_GetNetworkVolume( True ) :
			return True

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Hard disk drive not detected' ) )
		dialog.doModal( )
		return False

	return True


def CheckEthernet( aEthName ) :
	status = 'down'
	cmd = 'cat /sys/class/net/%s/operstate'% aEthName
	try :
		if sys.version_info < ( 2, 7 ) :
			p = Popen( cmd, shell=True, stdout=PIPE )
			status = p.stdout.read( ).strip( )
			p.stdout.close( )
		else :
			p = Popen( cmd, shell=True, stdout=PIPE, close_fds=True )
			( status, err ) = p.communicate( )
			status = status.strip( )
		
		LOG_TRACE('-------------linkStatus[%s]'% status )

	except Exception, e :
		LOG_ERR( 'Exception[%s] cmd[%s]'% ( e, cmd ) )

	return status


def CheckMD5Sum( aSourceFile, aMd5 = None, aResult = False ) :
	isVerify = False
	cmd = 'md5sum %s |awk \'{print $1}\''% aSourceFile

	if not os.path.exists( aSourceFile ) :
		LOG_TRACE( '------------file not found[%s]'% aSourceFile )
		return isVerify

	try :
		if sys.version_info < ( 2, 7 ) :			
			p = Popen( cmd, shell=True, stdout=PIPE )
			readMd5 = p.stdout.read( ).strip( )
			p.stdout.close( )
		else :
			p = Popen( cmd, shell=True, stdout=PIPE, close_fds=True )
			( readMd5, err ) = p.communicate( )
			readMd5 = readMd5.strip( )

		LOG_TRACE('-------------checkMd5[%s] sourceMd5[%s]'% ( readMd5, aMd5 ) )
		if aMd5 :
			if readMd5 == aMd5 :
				isVerify = True
		else :
			isVerify = readMd5

		if aResult :
			isVerify = ( isVerify, readMd5, aMd5 )

	except Exception, e :
		LOG_ERR( 'Exception[%s] cmd[%s]'% ( e, cmd ) )

	return isVerify


def GetDeviceSize( path ) :
	total, used, free = 0, 0, 0

	try :
		st = os.statvfs(path)
		free = st.f_bavail * st.f_frsize
		total = st.f_blocks * st.f_frsize
		used = (st.f_blocks - st.f_bfree) * st.f_frsize

	except Exception, e :
		LOG_TRACE( 'Exception[%s]'% e )
		total, used, free = 0, 0, 0

	#return (total, used, free)
	return free


def GetUnpackSize( aZipFile ) :
	total = 0

	fileList = GetUnpackFiles( aZipFile )
	if fileList :
		for item in fileList :
			total += item[0]

	return total


def GetFileSize( aFile ) :
	fsize = 0
	try :
		fsize = os.stat( aFile )[stat.ST_SIZE]
	
	except Exception, e :
		LOG_TRACE( 'Exception[%s]'% e )
		fsize = -1

	return fsize


def GetUnpackFiles( aZipFile ) :
	tFile = '/mtmp/test'
	#cmd = "unzip -l /mnt/hdd0/program/download/update.2012.10.10.zip | awk '{print $1, $4}' > %s"% tFile
	cmd = "unzip -l %s | awk '{print $1, $4}' > %s"% ( aZipFile, tFile )
	fileList = []
	try :
		os.system( cmd )
		os.system( 'sync' )
		time.sleep( 0.2 )
		f = open( tFile, 'r' )
		ret = f.readlines()
		f.close()

		for line in ret :
			pars = re.split(' ', line )
			if pars[0].isdigit( ) :
				pars[0] = int( pars[0] )
				pars[1] = pars[1].rstrip( )
				if pars[0] == 0 :
					#pars[0] = 4096	#directory size block
					continue

				if pars[1] and os.path.splitext( pars[1] )[1] == '.md5' :
					continue

				#pars[1] = re.sub( '\n', '', pars[1] )
				if pars[1] :
					fileList.append( pars )

	except Exception, e :
		LOG_TRACE( 'Exception[%s]'% e )
		return False

	return fileList


def GetUnpackFilenames( aZipFile ) :
	tFile = '/mtmp/test'
	cmd = "unzip -l %s | awk '{print $1, $4}' > %s" % ( aZipFile, tFile )
	fileList = []
	try :
		os.system( cmd )
		os.system( 'sync' )
		time.sleep( 0.2 )
		f = open( tFile, 'r' )
		ret = f.readlines( )
		f.close( )

		for line in ret :
			pars = re.split(' ', line )
			if pars[0].isdigit( ) :
				pars[0] = int( pars[0] )
				pars[1] = pars[1].rstrip( )

				if pars[1] :
					fileList.append( pars[1] )

	except Exception, e :
		LOG_TRACE( 'Exception[%s]'% e )
		return False

	return fileList


def GetUnpackByMD5( aFile ) :
	value = ''
	openFile = '%s.md5'% aFile
	if not CheckDirectory( openFile ) :
		return False

	try :
		fp = open( openFile, 'r' )
		ret = fp.readline( ).strip( )
		fp.close( )

		pars = re.split(' ', ret )
		if pars and len( pars ) > 0 :
			value = pars[0].strip()

	except Exception, e :
		LOG_ERR( 'Exception[%s] Could not open[%s]'% ( e, openFile ) )

	return value


def GetUnpackDirectory( aZipFile ) :
	unzipDir = False

	fileList = GetUnpackFiles( aZipFile )
	if fileList and len( fileList ) > 0 and fileList[0][0] == 4096 and fileList[0][1] :
		LOG_TRACE( '---------------size[%s] dirName[%s]'% ( fileList[0][0], fileList[0][1] ) )
		unzipDir = fileList[0][1].strip( '/' )

	return unzipDir


def GetFileRead( aOpenFile ) :
	readLines = ''
	try :
		fp = open( aOpenFile, 'r' )
		readLines = fp.readline( ).strip( )
		fp.close( )

	except Exception, e :
		LOG_ERR( 'Exception[%s] cmd[%s]'% ( e, aOpenFile ) )

	return readLines


def GetCurrentVersion( ) :
	parse = ['Version', 'Date']
	retInfo = []
	for ele in parse :
		cmd = 'cat /etc/release.info | awk -F= \'/%s/ {print $2}\'' % ele
		if sys.version_info < ( 2, 7 ) :
			p = Popen( cmd, shell=True, stdout=PIPE )
			ret = p.stdout.read( ).strip( )
			p.stdout.close( )
		else :
			p = Popen( cmd, shell=True, stdout=PIPE, close_fds=True )
			( ret, err ) = p.communicate( )
			ret = ret.strip( )
		
		retInfo.append( ret )
		#print 'ret[%s]'% ret

	return retInfo


def UnpackToUSB( aZipFile, aUsbPath, aUnpackSize = 0, aUnzipPath = 'update_ruby' ) :
	isCopy = False
	cmd = 'unzip -o %s -d %s'% ( aZipFile, aUsbPath )

	if not os.path.exists( aUsbPath ) :
		LOG_TRACE( '------------check usb[%s]'% aUsbPath )
		return isCopy

	#RemoveDirectory( '%s/%s'% ( aUsbPath, aUnzipPath ) )
	RemoveUnzipFiles( aUsbPath, False, aUnzipPath )
	usbSize = GetDeviceSize( aUsbPath )
	if usbSize <= aUnpackSize :
		return -1

	try :
		LOG_TRACE( 'execute cmd[%s]'% cmd )
		returnCode = os.system( cmd )
		LOG_TRACE( '--------------unzip returnCode[%s]'% returnCode )
		#ToDo : why return forced -1 ????
		#if returnCode == 0 :
		#	isCopy = True
		isCopy = True

		os.system( 'sync' )
		time.sleep( 0.5 )

	except Exception, e :
		LOG_ERR( 'Exception[%s] cmd[%s]'% ( e, cmd ) )
		isCopy = False

	return isCopy


def CopyToFile( aSourceFile, aDestFile ) :
	isCopy = True
	try :
		shutil.copyfile( aSourceFile, aDestFile )
		os.system( 'sync' )
		time.sleep( 0.5 )

	except Exception, e :
		LOG_ERR( 'Exception[%s] source[%s] desc[%s]'% ( e, aSourceFile, aDestFile ) )
		isCopy = False

	return isCopy


def CopyToDirectory( aSourceDirectory, aDestPath ) :
	isCopy = True
	try :
		shutil.copytree( aSourceDirectory, aDestPath )
		os.system( 'sync' )
		time.sleep( 0.5 )

	except Exception, e :
		LOG_ERR( 'Exception[%s] source[%s] desc[%s]'% ( e, aSourceDirectory, aDestPath ) )
		isCopy = False

	return isCopy


def GetDirectorySize( aPath ) :
	dir_size = 0
	for ( path, dirs, files ) in os.walk( aPath ) :
		for file in files :
			try :
				filename = os.path.join( path, file )
				dir_size += os.path.getsize( filename )
			except Exception, e :
				LOG_ERR( 'except file get size error filename = %s' % filename )

	return dir_size


def GetDirectoryAllFilePathList( aPathList, aExceptList = [] ) :
	path_ret = []
	exthash = {}
	for dName in aExceptList :
		exthash[dName] = dName

	dirCount = 0
	fileCount = 0
	for pathlist in aPathList :
		ePath = ''
		if CheckDirectory( pathlist ) :
			for ( path, dirs, files ) in os.walk( pathlist ) :
				if exthash.get( path, -1 ) == path :
					ePath = path
					LOG_TRACE( '----------------------copy exceptFile[%s]'% path )
					continue

				if ePath : # not copy subdirectories
					if len( ePath ) < len( path ) and ePath == path[:len(ePath)] :
						#LOG_TRACE( '----------------------copy exceptFile[%s]'% path )
						continue

				path_ret.append( path )
				dirCount += 1
				for file in files :
					filename = os.path.join( path, file )
					path_ret.append( filename )
					fileCount += 1

		else :
			LOG_ERR( 'path not exists = %s' % pathlist )
	print '---------------------------dirCount[%s] fileCount[%s]'% (dirCount, fileCount)
	return path_ret


def GetDirectoryAllFileCount( aPathList ) :
	count = 0
	for pathlist in aPathList :
		if not os.path.exists( pathlist ) :
			LOG_ERR( 'path not exists = %s' % pathlist )
		else :
			for ( path, dirs, files ) in os.walk( pathlist ) :
				count = count + 1
				for file in files :
					count = count + 1

	return count


def GetURLpage( aUrl, aWriteFileName = None ) :
	isExist = False
	try :
		#f = urllib.urlopen( url )
		f = urllib.URLopener( ).open( aUrl )
		if f :
			isExist = True
			if aWriteFileName :
				try :
					fd = open( aWriteFileName, 'w' )
					fd.write( f.read( ) )
					fd.close( )
				except Exception, e :
					LOG_ERR( 'Exception[%s] writeError writefile[%s]'% ( e, aWriteFileName ) )
					isExist = False

			f.close( )

	except IOError, e :
		LOG_ERR( 'Exception[%s] url[%s]'% ( e, aUrl ) )

	return isExist


def ParseStringInXML( xmlFile, tagNames, aRootName = 'software', tagNames2 = '' ) :
	lists = []
	#if os.path.exists(xmlFile) :
	if xmlFile :
		parseTree = ElementTree.parse( xmlFile )
		treeRoot = parseTree.getroot( )

		for node in treeRoot.findall( aRootName ) :
			lines = []
			for tagName in tagNames :
				if node.findall( tagName ) :
					descList = []
					scriptList=[]
					for element in node.findall( tagName ) :
						#elementry = [ str(element.text), '%s\r\n'% str(element) ]
						elementry = str( element.text )
						if tagName == 'description' or tagName == 'action' :
							descList.append( elementry )

						elif tagName == 'script' :
							script_elementry = []
							for _tagName in tagNames2 :
								ele = ''
								for sub_node in element.getchildren( ) :
									if sub_node.tag == _tagName :
										ele = str( sub_node.text )

								script_elementry.append( ele )
							scriptList.append( script_elementry )

						else :
							lines.append( elementry )

					if descList and len( descList ) :
						lines.append( descList )

					if scriptList and len( scriptList ) :
						lines.append( scriptList )

				else :
					lines.append('')

			#LOG_TRACE( 'parse[%s]'% lines )
			if lines :
				lists.append( lines )

	if lists == [] or len( lists ) < 1 :
		lists = None

	return lists


def ParseStringInPattern( aToken, aData ) :
	aData = re.sub( ' ', '', aData )
	return re.split( aToken, aData.strip( ) )


def SetDefaultSettingInXML( ) :
	mboxDir = xbmcaddon.Addon( 'script.mbox' ).getAddonInfo( 'path' )
	xmlFile = '%s/resources/settings.xml' % mboxDir
	#LOG_TRACE('-----dir[%s] file[%s]'% (mboxDir, xmlFile ) )
	tagNames = [ 'VIEW_MODE', 'SORT_MODE', 'EPG_MODE', 'ADDON_VIEW_MODE', 'Addons_Sort', 'RSS_FEED', 'AUTO_CONFIRM_CHANNEL', 'DISPLAY_CLOCK_NULL', 'DISPLAY_CLOCK_VFD', 'DISPLAY_EVENT_LIVE', 'DISPLAY_EXTEND' ]

	if not CheckDirectory( xmlFile ) :
		LOG_TRACE( 'error, file not found settings.xml[%s]'% xmlFile )
		return False

	ret = False
	parseTree = ElementTree.parse( xmlFile )
	treeRoot = parseTree.getroot( )

	for node in treeRoot.findall( 'setting' ) :
		for tagName in tagNames :
			if node.get( 'id' ) == tagName :
				default = int( node.get( 'default' ) )
				LOG_TRACE( 'id[%s] value : [%s] -> [%s]'% ( tagName, GetSetting( tagName ), default ) )
				SetSetting( tagName, '%d'% default )
				ret = True

	return ret


def GetParseUrl( reqUrl = '', isGetSize = False ) :
	urlPort = ''
	urlSize = 0

	parseObj = urlparse.urlparse( reqUrl )
	urlType = parseObj.scheme	#type : 'ftp', 'sftp', 'zeroconf', 'smb',...  ''(null) is local path

	#init default port
	if urlType == 'ftp' :
		urlPort = '21'
	#elif urlType == 'smb' :
	#	urlPort = '139'

	urlHost = parseObj.hostname
	urlPort = parseObj.port
	urlUser = parseObj.username
	urlPass = parseObj.password
	bPath = os.path.basename( parseObj.path )
	gPath = parseObj.path.replace( bPath, '' )
	urlPath = urllib.unquote( gPath )
	urlFile = urllib.unquote( os.path.basename( reqUrl ) )

	#LOG_TRACE( 'bPath[%s] gPath[%s]'% ( bPath, gPath ) )
	LOG_TRACE( 'host[%s] port[%s] user[%s] pass[%s] path[%s] file[%s]'% ( urlHost, urlPort, urlUser, urlPass, urlPath, urlFile ) )

	if isGetSize and urlType == 'ftp' :
		urlPath = re.sub( '^/', '', urlPath )
		if urlHost and urlPort and urlUser and os.path.join( urlPath, urlFile ) :
			urlSize = GetFileSizeFromFTP( '', urlHost, urlPort, urlUser, urlPass, urlPath, urlFile )

	return urlHost, urlPort, urlUser, urlPass, urlPath, urlFile, urlSize


def GetParseUrl_FTP( reqUrl = '', isGetSize = False ) :
	ftpUser = ''
	ftpPass = ''
	ftpHost = ''
	ftpPort = '21'
	ftpPath = ''
	ftpFile = ''
	ftpSize = 0
	#pattern = '^ftp:\/\/(.*):(.*)@(.*)'
	#sample = 'ftp://youn:@192.168.101.89:21/repository.bluecop.xbmc-plugins.zip'

	ftp_pattern = '^ftp:\/\/(.*)'
	p = re.search( ftp_pattern, reqUrl, re.IGNORECASE )
	if not bool( p ) :
		return ftpHost, ftpPort, ftpUser, ftpPass, ftpPath, ftpFile, ftpSize

	ret = re.findall( ftp_pattern, p.group() )
	if not ret or len( ret ) < 1 :
		return ftpHost, ftpPort, ftpUser, ftpPass, ftpPath, ftpFile, ftpSize

	url = ret[0]
	ret = re.split( '/', url )
	if not ret or len( ret ) < 2 :
		return ftpHost, ftpPort, ftpUser, ftpPass, ftpPath, ftpFile, ftpSize

	idline = ret[0]
	for i in range( 1, len( ret ) ) :
		ftpPath = os.path.join( ftpPath, ret[i] )

	ftpFile = os.path.basename( ftpPath )
	ftpPath = os.path.dirname( ftpPath )
	#LOG_TRACE( 'path[%s] file[%s]'% ( ftpPath, ftpFile ) )

	#ret[0]?, id:pass@url:port
	id_pattern = '(.*):(.*)@(.*)'
	p = re.search( id_pattern, idline, re.IGNORECASE )
	if bool( p ) :
		ret = re.findall( id_pattern, p.group() )
		if ret :
			ftpUser = ret[0][0]
			ftpPass = ret[0][1]
			ftpHost = ret[0][2]
	else :
		ftpHost = line
	#LOG_TRACE( 'id[%s] pw[%s] url[%s]'% ( ftpUser, ftpPass, ftpHost ) )

	#ftpHost?, url:port
	port_pattern = '(.*):(\d+)'
	p = re.search( port_pattern, ftpHost, re.IGNORECASE )
	if bool( p ) :
		ret = re.findall( port_pattern, p.group() )
		if ret :
			ftpHost = ret[0][0]
			ftpPort = ret[0][1]

	#LOG_TRACE( 'url[%s] port[%s]'% ( ftpHost, ftpPort ) )

	if isGetSize :
		if ftpHost and ftpPort and ftpUser and os.path.join( ftpPath, ftpFile ) :
			ftpSize = GetFileSizeFromFTP( '', ftpHost, ftpPort, ftpUser, ftpPass, ftpPath, ftpFile )

	LOG_TRACE( 'host[%s] port[%s] user[%s] pass[%s] path[%s] file[%s] size[%s]'% ( ftpHost, ftpPort, ftpUser, ftpPass, ftpPath, ftpFile, ftpSize ) )
	return ftpHost, ftpPort, ftpUser, ftpPass, ftpPath, ftpFile, ftpSize


def GetFileSizeFromFTP( aFilePath = '', ftpHost='', ftpPort='', ftpUser='', ftpPass='', ftpPath='', ftpFile='' ) :
	from ftplib import FTP

	if not aFilePath :
		aFilePath = os.path.join( ftpPath, ftpFile )

	if not aFilePath :
		return 0

	size = 0
	ftp = FTP()
	try :
		ftp.connect( ftpHost, ftpPort )
		ftp.login( ftpUser, ftpPass )
		size = ftp.size( aFilePath )
		ftp.close()
	except Exception, e :
		print 'Exception[%s]'% e

	return size


def ReadToCmdBlock( ) :
	cmdBlock = ''
	try :
		rf = open( '/proc/cmdline', 'r' )
		cmdBlock = rf.readline( ).strip( )
		rf.close( )
	except Exception, e :
		LOG_ERR( 'Exception[%s] file not found[/proc/cmdline]'% e )
		cmdBlock = ''

	LOG_TRACE( '/proc/cmdline[%s]'% cmdBlock )
	return cmdBlock


def GetBlockByUpdateSection( aSize, aChecksum = True ) :
	if aChecksum and aSize < 1 :
		return -1

	cmdBlock = ReadToCmdBlock( )
	if not cmdBlock or len( cmdBlock ) < 1 :
		return -2

	pattern = '\d+[A-Za-z]@\d+[A-Za-z]\(update\)'
	pattern2= '\d+[A-Za-z]@\d+[A-Za-z]'
	sections = 'mtdparts=(.*),\-\(extra\)'

	ret = re.findall( sections, cmdBlock )[0]
	LOG_TRACE( 'section[%s]'% ret )

	parseWords = re.split(',', ret )
	LOG_TRACE( 'list[%s]'% parseWords )

	if not parseWords or len( parseWords ) < 1 :
		LOG_TRACE( 'err!!' )

	mtdNumber = 0
	sizeBlock = 0
	offset = 0
	isError = True
	for mtdName in parseWords :
		ret = re.findall( pattern, mtdName )
		if ret and len( ret ) > 0 :
			LOG_TRACE( 'len[%s] find[%s]'% ( len(ret), ret[0] ) )
			ret = re.findall( pattern2, ret[0] )
			defines = re.split( '@', ret[0] )
			sizeBlock = defines[0]
			offset = defines[1]
			isError = False
			break
		mtdNumber += 1

	if isError :
		return -2

	unit = sizeBlock[len(sizeBlock)-1]
	sizeT = int( sizeBlock[:len(sizeBlock)-1] )
	sizeByte = 0
	if unit.lower() == 'k' :
		sizeByte = sizeT * 1024
	elif unit.lower() == 'm' :
		sizeByte = sizeT * 1024 * 1024

	LOG_TRACE( '------updateSection : sizeT[%s], unit[%s], sizeByte[%s]'% ( sizeT,unit,sizeByte ) )

	if aChecksum and sizeByte < aSize :
		return -3

	return mtdNumber


def InitFlash( ) :
	mtdNumber = GetBlockByUpdateSection( 0, False )
	if mtdNumber < 0 :
		return mtdNumber

	try :
		cmd1 = 'flash_erase /dev/mtd%s 0 0'% mtdNumber
		returnCode = os.system( cmd1 )
		os.system( 'sync' )
		time.sleep( 0.5 )
		LOG_TRACE( '---------erase cmd1[%s] returnCode[%s]'% ( cmd1, returnCode ) )

	except Exception, e :
		LOG_ERR( 'Exception[%s] cmd1[%s] cmd2[%s]'% ( e, cmd1, cmd2 ) )


def SetWriteToFlash( aFile ) :
	if not CheckDirectory( aFile ) :
		return -1

	imgSize = os.stat( aFile )[stat.ST_SIZE]
	mtdNumber = GetBlockByUpdateSection( imgSize )
	if mtdNumber < 0 :
		return mtdNumber

	isWrite = -4
	try :
		cmd1 = 'flash_erase /dev/mtd%s 0 0'% mtdNumber
		#cmd2 = 'nandwrite -a -p -b 4 /dev/mtd%s %s'% ( mtdNumber, aFile )
		cmd2 = 'nandwrite -p /dev/mtd%s %s'% ( mtdNumber, aFile )

		returnCode = os.system( cmd1 )
		os.system( 'sync' )
		time.sleep( 0.5 )
		LOG_TRACE( '---------erase cmd1[%s] returnCode[%s]'% ( cmd1, returnCode ) )

		returnCode = os.system( cmd2 )
		os.system( 'sync' )
		time.sleep( 0.5 )
		LOG_TRACE( '---------write cmd2[%s] returnCode[%s]'% ( cmd2, returnCode ) )

		#ToDo : why return forced -1 ????
		#if returnCode == 0 :
		#	isWrite = True
		isWrite = True

	except Exception, e :
		LOG_ERR( 'Exception[%s] cmd1[%s] cmd2[%s]'% ( e, cmd1, cmd2 ) )
		isWrite = -4

	return isWrite


def GetImgPath( aUnzipList, aFindFile ) :
	if not CheckDirectory( aUnzipList ) :
		return False

	fd = open( aUnzipList, 'r' )
	fileList = fd.readlines( )
	fd.close( )

	if not fileList or len( fileList ) < 1 :
		LOG_TRACE( 'no files' )
		return False

	imgFile = ''
	for iFile in fileList :
		if os.path.basename( iFile.strip( ) ) == aFindFile :
			imgFile = iFile.strip()
			break

	return imgFile


def CheckUSBTypeNTFS( aMountPath, aToken ) :
	isNTFS = False
	cmd = "mount | awk '/%s/ {print $5}'" % aToken
	ret = ''
	if sys.version_info < ( 2, 7 ) :
		p = Popen( cmd, shell=True, stdout=PIPE )
		ret = p.stdout.read( ).strip( )
		p.stdout.close( )

	else :
		p = Popen( cmd, shell=True, stdout=PIPE, close_fds=True )
		( ret, err ) = p.communicate( )
		ret = ret.strip( )

	if ret.strip( ).lower( ) == 'tntfs' or ret.strip( ).lower( ) == 'ntfs' :
		isNTFS = True
	else :
		isNTFS = False

	return isNTFS


def GetMountByDeviceSize( aDevSize = 0 ) :
	cmd = "fdisk -l | grep Disk | awk '/%s/ {print $2,$5}' | awk -F': ' '{print $1}'"% aDevSize
	devName = ExecuteShell( cmd )
	ret = []
	if devName :
		cmd = "mount | awk '/%s/ {print $3}'"% os.path.basename( devName )
		ret = ExecuteShell( cmd ).split( '\n' )
	return ret


def GetMountPathByDevice( aDevice = 3, aDevName = None, aReqDevice = False ) :
	#aDevice 1: mmc, 2: usb memory, 3: hdd
	mountPos = ''
	if aDevName :
		cmd = "mount | awk '/%s/ {print $3}'"% os.path.basename( aDevName )
		ret = ExecuteShell( cmd ).split( '\n' )
		if ret :
			if len( ret[0].split('/')[1:] ) > 2 :
				mountPos = os.path.dirname( ret[0] )
			else :
				mountPos = ret[0]

			if aReqDevice :
				cmd = "mount | awk '/%s/ {print $1}'"% os.path.basename( aDevName )
				dev = ExecuteShell( cmd ).split( '\n' )
				mountDev = 'None'
				if dev and bool( re.search( '/dev/sd', dev[0], re.IGNORECASE ) ) :
					mountDev = '/dev/sda'
					mountPos = [mountDev,mountPos]					
				elif dev and bool( re.search( '/dev/mmc', dev[0], re.IGNORECASE ) ) :
					mountDev = '/dev/mmc'
					mountPos = [mountDev,mountPos]

		if not mountPos: #check partitions
			cmd = ''
			if aDevName == '/dev/mmc' :
				cmd = "cat /proc/partitions |awk '/%s/ {print $4}'"% 'mmc'
			elif bool( re.search( '/dev/sd', aDevName, re.IGNORECASE ) ) :
				cmd = "cat /proc/partitions |awk '/%s/ {print $4}'"% 'sd'

			if cmd :
				ret = ExecuteShell( cmd ).split( '\n' )
				for partition in ret :
					if partition == 'mmc' :
						mountDev = '/dev/mmc'
						mountPos = '/media/mmc'
						isFind = True
						return mountPos

					elif bool( re.search( 'sd', partition, re.IGNORECASE ) ) :
						mountDev = '/dev/%s'% partition
						mountPos = '/media/hdd0'
						return mountPos

		#LOG_TRACE( '---------------find dev[%s] mnt[%s]'% ( aDevName, mountPos) )

	if aDevice == 1 :
		cmd = "mount | awk '/mmc/ {print $3}'"
		mountPos = ExecuteShell( cmd ).rstrip( )

	elif aDevice == 3 :
		cmd = "mount | awk '/hdd0/ {print $3}'"
		ret = ExecuteShell( cmd ).split( '\n' )
		if ret :
			mountPos = ret[0]

	return mountPos


def GetMountExclusiveDevice( aElementSize = None ) :
	hddinfo = "cat /proc/scsi/sg/device_strs | awk '$1~/[^\<no]/ {print $1}'"
	hddsize = "fdisk -l | grep Disk | awk '/sd/ {print $2,$5}' | awk -F': ' '{print $1,$2}'"
	mmcsize = "fdisk -l | grep Disk | awk '/mmc/ {print $5}'"
	hdddev = '/dev/sda'
	if aElementSize :
		hddsize = "fdisk -l | grep Disk | awk '/%s/ {print $5}'"% os.path.basename( aElementSize )
		return ExecuteShell( hddsize )
	hddinfo_ = ExecuteShell( hddinfo ).split( '\n' )
	hddsize_ = ExecuteShell( hddsize ).split( '\n' )
	mmcsize_ = ExecuteShell( mmcsize ).rstrip( )
	LOG_TRACE( 'mmcsize[%s] hddsize[%s] hddinfo[%s]'% ( mmcsize_, hddsize_, hddinfo_ ) )

	mmcsize = '0Byte'
	hddsize = '0Byte'
	hddinfo = 'unknown'
	mntinfo = []

	try :
		if mmcsize_ :
			iSize = int(mmcsize_)
			if iSize < ( 1000000 * 1000 ) :
				mmcsize = '%0.1fMb'% float( 1.0 * iSize / 1000000 )
			else :
				mmcsize = '%0.1fGb'% float( 1.0 * iSize / ( 1000000 * 1000 ) )

			mntinfo.append( [MR_LANG( 'Micro SD Card' ), mmcsize, '/dev/mmc'] )

	except Exception, e :
		LOG_ERR( 'Exception[%s]'% e )

	try :
		if hddsize_ :
			#ToDO : usb hdd, usb memory ? big size is hdd
			#iSize = hddsize_[0]
			#if len( hddsize_ ) > 1 :
			#	if hddsize_[0] < hddsize_[1] :
			#		iSize = hddsize_[1]

			if len( hddsize_ ) > 1 :
				#mntinfo = [[],[]]
				#mntinfo[0].append( [] )
				idx = 0
				for ele in hddsize_ :
					ret = ele.split(' ')
					#LOG_TRACE( '-----ele[%s] ret[%s]'% (ele,ret) )
					vendor = hddinfo_[idx] #vendor
					usbdev = ret[0] #dev
					iSize = int( ret[1] )
					sSize = '%0.1fGb'% float( 1.0 * iSize / ( 1000000 * 1000 ) )
					if iSize < ( 1000000 * 1000 ) :
						sSize = '%0.1fMb'% float( 1.0 * iSize / 1000000 )
					usbsize = sSize  #size
					mntinfo.append( [vendor,usbsize,usbdev] )
					idx += 1

			else :
				ret = hddsize_[0].split( ' ' )
				#LOG_TRACE( '----%s'% (ret) )
				iSize = int(ret[1])
				sSize = '%0.1fGb'% float( 1.0 * iSize / ( 1000000 * 1000 ) )
				if iSize < ( 1000000 * 1000 ) :
					sSize = '%0.1fMb'% float( 1.0 * iSize / 1000000 )

				vendor = hddinfo_[0]
				usbdev = ret[0]
				usbsize = sSize
				mntinfo.append( [vendor,usbsize,usbdev] )

	except Exception, e :
		LOG_ERR( 'Exception[%s]'% e )

	#LOG_TRACE( '----------mntinfo[%s]'% mntinfo )

	return mntinfo


def CheckMountType( aMountPath ) :
	mntType = ''
	try :
		mpos = aMountPath.split('/')
		aToken= mpos[-1]
		cmd = "mount | awk '/%s/ {print $5}'"% aToken
		if sys.version_info < ( 2, 7 ) :
			p = Popen( cmd, shell=True, stdout=PIPE )
			ret = p.stdout.read( ).strip( )
			p.stdout.close( )

		else :
			p = Popen( cmd, shell=True, stdout=PIPE, close_fds=True )
			( ret, err ) = p.communicate( )
			mntType = ret.strip( )

	except Exception, e :
		LOG_ERR( 'Exception[%s]'% e )
		mntType = ''

	return mntType


def ExecuteShell( cmd = '' ) :
	if not cmd :
		return ''

	if sys.version_info < ( 2, 7 ) :
		p = Popen( cmd, shell=True, stdout=PIPE )
		ret = p.stdout.read( ).strip( )
		p.stdout.close( )
	else :
		p = Popen( cmd, shell=True, stdout=PIPE, close_fds=True )
		( ret, err ) = p.communicate( )
		ret = ret.strip( )

		#LOG_TRACE( 'ExecuteShell ret[%s] err[%s]'% ( ret, err ) )
		if err :
			ret = False

	return ret


def IsIPv4( address ) :
	if not address :
		return False

	# check if string is valid ipv4 address
	if address.replace( '.', '' ).strip( '1234567890' ) :
		return False

	octets = address.split( '.' )
	if len(octets) != 4 :
		return False

	for octet in octets :
		try :
			int( octet )
		except :
			return False

		if int( octet ) > 255 :
			return False

	return True


def GetSharedDirectoryByHost( aHostName = '', aReqPath = '' ) :
	if not aHostName or ( not aReqPath ) :
		LOG_TRACE( 'no name host' )
		return ''

	mountPath = ''
	cmd = '/usr/bin/smbclient -YNL "%s"|awk \'$1-/^#/ {print $0}\''% aHostName
	result = ExecuteShell( cmd )
	result = result.split( '\n' )
	if not result :
		result = []

	pubDirs = {}
	for idx in range( len( result ) ) :
		if result[idx] :
			if result[idx][0] == '#' :
				pubDirs[ result[idx][1:] ] = True

	if not pubDirs :
		LOG_TRACE( 'no shared directory' )
		return mountPath

	reqPath = aReqPath.split('/')
	if reqPath and len( reqPath ) > 0 :
		isFind = False
		for rpath in reqPath :
			mountPath += '%s/'% rpath
			if rpath and pubDirs.get( rpath, None ) :
				isFind = True
				break
		if not isFind :
			mountPath = ''

	LOG_TRACE( 'len[%s] pubDirs[%s] mountPath[%s]'% ( len( pubDirs ), pubDirs, mountPath )	)
	return mountPath


def MountToSMB( aUrl, aSmbPath = '/media/smb', isCheck = True ) :
	urlType = urlparse.urlparse( aUrl ).scheme
	urlHost, urlPort, urlUser, urlPass, urlPath, urlFile, urlSize = GetParseUrl( aUrl )
	zipFile = ''
	hostip = urlHost

	if not IsIPv4( urlHost ) :
		ExecuteShell( 'net cache flush' )
		hostip = ExecuteShell( 'net lookup %s'% urlHost )
		if not hostip :
			#LOG_TRACE( 'lookup fail' )
			return zipFile

		if not IsIPv4( hostip ) :
			return zipFile

	#remotePath = '//%s'% os.path.join( '%s'% hostip, os.path.dirname( urlPath )[1:] )
	#LOG_TRACE( 'smbPath[%s]'% smbPath )

	mntHistory = ExecuteShell( 'mount' )
	if not mntHistory :
		return zipFile

	#ret = re.search( 'type cifs', mntHistory, re.IGNORECASE )
	ret = re.search( '%s'% aSmbPath, mntHistory, re.IGNORECASE )
	if bool( ret ) :
		LOG_TRACE( 'already mount cifs, umount %s'% aSmbPath )
		os.system( '/bin/umount -fl %s'% aSmbPath )
		os.system( 'sync' )
		time.sleep( 2 )

	CreateDirectory( aSmbPath )

	remotePath = '//%s%s'% ( hostip, os.path.dirname( urlPath ) )
	cmd = 'mount -t cifs -o username=%s,password=%s %s %s'% ( urlUser, urlPass, remotePath, aSmbPath )
	if urlType == 'smb' :
		remotePath = '//%s%s'% ( hostip, os.path.dirname( urlPath ) )
		cmd = 'mount -t cifs -o username=%s,password=%s %s %s'% ( urlUser, urlPass, remotePath, aSmbPath )
	elif urlType == 'nfs' :
		remotePath = '%s:%s'% ( hostip, os.path.dirname( urlPath ) )
		cmd = 'mount -t nfs %s %s -o nolock,mountvers=4'% ( remotePath, aSmbPath )
	elif urlType == 'ftp' :
		remotePath = '%s:%s'% ( hostip, os.path.dirname( urlPath ) )
		cmd = 'modprobe fuse && curlftpfs %s %s -o user=%s:%s,allow_other'% ( remotePath, aSmbPath, urlUser, urlPass )

	LOG_TRACE( 'remotePath[%s] mountPath[%s] cmd[%s]'% ( remotePath, aSmbPath, cmd ) )

	if ExecuteShell( cmd ) :
		# result something? maybe error
		LOG_TRACE( 'Fail to mount: cmd[%s]'% cmd )
		return zipFile

	else :
		# mount check confirm
		mntHistory = ExecuteShell( 'mount' )
		if not mntHistory or ( not bool( re.search( '%s'% aSmbPath, mntHistory, re.IGNORECASE ) ) ) :
			LOG_TRACE( 'Fail to mount: cmd[%s]'% cmd )
			return zipFile

	zipFile = '%s/%s'% ( aSmbPath, urlFile )
	if isCheck and ( not CheckDirectory( zipFile ) ) :
		LOG_TRACE( 'file not found zipPath[%s]'% zipFile )
		zipFile = ''

	return zipFile


def RefreshMountToSMB( aNetVolume ) :
	failCount = 0
	failItem = ''

	if not aNetVolume :
		return failCount, failItem

	#1. mount scan : not exist? delete leave directory
	mntHistory = ExecuteShell( 'mount' )
	if mntHistory and ( not bool( re.search( '%s'% aNetVolume.mMountPath, mntHistory, re.IGNORECASE ) ) ) :
		RemoveDirectory( aNetVolume.mMountPath )

	#2. read only? unmount refresh
	cPattern = re.sub( '/', '\/', aNetVolume.mMountPath )
	readOnlyCheck = 'cat /proc/mounts |awk \'$2-/%s/ {print $4}\'|awk -F"," \'{print $1}\''% cPattern
	#LOG_TRACE( 'cmd[%s] result[%s]'% ( readOnlyCheck, ExecuteShell( readOnlyCheck ) ) )
	if mntHistory and bool( re.search( '%s'% aNetVolume.mMountPath, mntHistory, re.IGNORECASE ) ) and \
	   ExecuteShell( readOnlyCheck ) == 'ro' :
		os.system( '/bin/umount -fl %s; rm -rf %s'% ( aNetVolume.mMountPath, aNetVolume.mMountPath ) )
		time.sleep( 0.1 )
		mntHistory = ''
		LOG_TRACE( '[NAS] umount, check read only' )

	#3. retry mount
	if not mntHistory or ( not bool( re.search( '%s'% aNetVolume.mMountPath, mntHistory, re.IGNORECASE ) ) ) :
		mntPath = MountToSMB( aNetVolume.mRemoteFullPath, aNetVolume.mMountPath, False )
		if not mntPath :
			mntHistory = ExecuteShell( 'mount' )
			if not mntHistory or ( not bool( re.search( '%s'% aNetVolume.mMountPath, mntHistory, re.IGNORECASE ) ) ) :
				failCount += 1
				failItem += '%s'% os.path.basename( aNetVolume.mMountPath )

		#LOG_TRACE( '[NAS] mount[%s] ret[%s]'% ( aNetVolume.mMountPath, lblRet ) )

	#4. writable check
	mntHistory = ExecuteShell( 'mount' )
	if mntHistory and bool( re.search( '%s'% aNetVolume.mMountPath, mntHistory, re.IGNORECASE ) ) :
		checkFile = '%s/writableCheck'% aNetVolume.mMountPath
		if CreateFile( checkFile ) :
			RemoveDirectory( checkFile )
			LOG_TRACE( '[NAS] done, writable' )
		else :
			#read only?
			os.system( '/bin/mount -o ro,remount %s'% aNetVolume.mMountPath )
			LOG_TRACE( '[NAS] remount, readonly' )

	#time.sleep( 0.5 )
	return failCount, failItem


def CheckEthernetType( ) :
	from pvr.gui.GuiConfig import E_USE_OLD_NETWORK
	if E_USE_OLD_NETWORK :
		import pvr.IpParser as NetMgr
	else :
		import pvr.NetworkMgr as NetMgr

	nType = NetMgr.GetInstance( ).GetCurrentServiceType( )
	return nType


def CheckNetworkStatus( ) :
	from pvr.gui.GuiConfig import NETWORK_ETHERNET
	retValue   = False
	linkStatus = 'down'

	nType = CheckEthernetType( )
	if nType == NETWORK_ETHERNET :
		linkStatus = CheckEthernet( 'eth0' )

	else :
		from pvr.XBMCInterface import XBMC_CheckNetworkStatus
		wifiRet = XBMC_CheckNetworkStatus( )
		if wifiRet == 'Connected' or wifiRet == 'Busy' :
			linkStatus = 'up'
		#LOG_TRACE('network wifi ret[%s] link[%s]'% ( wifiRet, linkStatus ) )

	if linkStatus != 'down' :
		retValue = True

	LOG_TRACE( 'network type[%s] link[%s] ret[%s]'% ( nType, linkStatus, retValue ) )
	return retValue


class GuiSkinPosition( object ) :
	def __init__( self ) :
		self.mLeft	 = 0
		self.mTop	 = 0
		self.mRight	 = 0
		self.mBottom = 0
		self.mZoom	 = 0


	def GetPipPosition( self, aX, aY, aWidth, aHeight ) :
		from pvr.gui.GuiConfig import E_WINDOW_HEIGHT, E_WINDOW_WIDTH
		if self.mZoom != 0 :
			w = aWidth  / float( 100 ) * ( 100 + self.mZoom )
			h = aHeight / float( 100 ) * ( 100 + self.mZoom )
			y = ( ( E_WINDOW_HEIGHT - ( E_WINDOW_HEIGHT / float( 100 ) * ( 100 + self.mZoom ) ) ) / float( 2 ) ) + ( ( aY / float( 100 ) ) * ( 100 + self.mZoom ) )
			x = ( ( E_WINDOW_WIDTH  - ( E_WINDOW_WIDTH  / float( 100 ) * ( 100 + self.mZoom ) ) ) / float( 2 ) ) + ( ( aX / float( 100 ) ) * ( 100 + self.mZoom ) )
		else :
			x = aX
			y = aY
			w = aWidth
			h = aHeight

		x = x * ( E_WINDOW_WIDTH  - ( self.mLeft + ( E_WINDOW_WIDTH  -  self.mRight ) ) ) / float( E_WINDOW_WIDTH )
		y = y * ( E_WINDOW_HEIGHT - ( self.mTop  + ( E_WINDOW_HEIGHT - self.mBottom ) ) ) / float( E_WINDOW_HEIGHT )
		w = w * ( E_WINDOW_WIDTH  - ( self.mLeft + ( E_WINDOW_WIDTH  -  self.mRight ) ) ) / float( E_WINDOW_WIDTH )
		h = h * ( E_WINDOW_HEIGHT - ( self.mTop  + ( E_WINDOW_HEIGHT - self.mBottom ) ) ) / float( E_WINDOW_HEIGHT )

		x = x + self.mLeft
		y = y + self.mTop

		x = round( x )
		y = round( y )
		w = round( w )
		h = round( h )
		return int( x ), int( y ), int( w ), int( h )


	def SetPosition( self, aLeft, aTop, aRight, aBottom, aZoom ) :
		self.mLeft	 = aLeft
		self.mTop	 = aTop
		self.mRight	 = aRight
		self.mBottom = aBottom
		self.mZoom	 = aZoom


def ShowSubtitle( ) :
	import pvr.DataCacheMgr
	import pvr.gui.DialogMgr as DiaMgr
	from pvr.gui.GuiConfig import ContextItem
	from elisinterface.ElisEnum import ElisEnum
	dataCache = pvr.DataCacheMgr.GetInstance( )

	ret = -2
	subTitleCount = dataCache.Subtitle_GetCount( )
	if subTitleCount > 0 :
		isShowing = False
		if dataCache.Subtitle_IsShowing( ) :
			dataCache.Subtitle_Hide( )
			isShowing = True

		selectedSubtitle = dataCache.Subtitle_GetSelected( )

		#if selectedSubtitle :
		#	selectedSubtitle.printdebug( )

		context = []
		structSubTitle = []
		selectedIndex = -1
		isExistDVB = False

		for i in range( subTitleCount ) :
			structSubTitle.append( dataCache.Subtitle_Get( i ) )
			if structSubTitle[i].mSubtitleType == ElisEnum.E_SUB_DVB :
				isExistDVB = True

		for i in range( subTitleCount ) :
			i_index = subTitleCount - i - 1
			if isExistDVB and structSubTitle[i_index].mSubtitleType != ElisEnum.E_SUB_DVB :
				structSubTitle.remove( structSubTitle[i_index] )		

		subTitleCount = len( structSubTitle )
		for i in range( subTitleCount ) :
			#if isExistDVB and structSubTitle[i].mSubtitleType != ElisEnum.E_SUB_DVB :
			#	structSubTitle.pop( i )
			#	continue

			#structSubTitle[i].printdebug( )

			if selectedSubtitle :
				if selectedSubtitle.mPid == structSubTitle[i].mPid and selectedSubtitle.mPageId == structSubTitle[i].mPageId and selectedSubtitle.mSubId == structSubTitle[i].mSubId :
					selectedIndex = i
					LOG_TRACE( '-----------------selected subtitle idx[%s]'% i )

			if structSubTitle[i].mSubtitleType == ElisEnum.E_SUB_DVB :
				subType = 'DVB'
			else :
				subType = 'TTX'
			LOG_TRACE( 'structSubTitle[i].mLanguage = %s'% structSubTitle[i] )
			LOG_TRACE( 'structSubTitle[i].mLanguage[0] = %d '% len( structSubTitle[i].mLanguage ) )
			if structSubTitle[i].mSubtitleType != ElisEnum.E_SUB_DVB and structSubTitle[i].mLanguage == '' :
				ten = ( structSubTitle[i].mSubId / 16 )
				one = ( structSubTitle[i].mSubId % 16 )

				context.append( ContextItem( subType + ' Subtitle ' +  '( Page: ' + str(structSubTitle[i].mPageId) + str(ten) + str(one) + ')', i ) )
			else :	
				context.append( ContextItem( subType + ' Subtitle ' + structSubTitle[i].mLanguage, i ) )

		subTitleCount = len( structSubTitle )
		context.append( ContextItem( MR_LANG( 'Disable subtitle' ), subTitleCount ) )

		if selectedIndex < 0 :
			selectedIndex = subTitleCount

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context, selectedIndex )
		dialog.doModal( )

		selectAction = dialog.GetSelectedAction( )
		if selectAction == -1 and isShowing :
			dataCache.Subtitle_Show( )

		elif selectAction >= 0 and subTitleCount > selectAction :
			dataCache.Subtitle_Select( structSubTitle[ selectAction ].mPid, structSubTitle[ selectAction ].mPageId, structSubTitle[ selectAction ].mSubId )
			dataCache.Subtitle_Show( )

		elif selectAction == subTitleCount :
			dataCache.Subtitle_Select( 0x1fff, 0, 0 )
			dataCache.Subtitle_Hide( )

		ret = selectAction

	return ret


def GetStatusModeLabel( aMode ) :
	labelMode = ''

	if aMode == ElisEnum.E_MODE_LIVE :
		labelMode = '[COLOR white]%s[/COLOR]'% MR_LANG( 'LIVE' )
	elif aMode == ElisEnum.E_MODE_TIMESHIFT :
		labelMode = '[COLOR green]%s[/COLOR]'% MR_LANG( 'TIMESHIFT' )
	elif aMode == ElisEnum.E_MODE_PVR :
		labelMode = '[COLOR red]%s[/COLOR]'% MR_LANG( 'PLAYBACK' )
	elif aMode == ElisEnum.E_MODE_EXTERNAL_PVR :
		labelMode = '%s'% MR_LANG( 'EXTERNAL PLAYBACK' )
	elif aMode == ElisEnum.E_MODE_MULTIMEDIA :
		labelMode = '%s'% MR_LANG( 'MULTIMEDIA' )
	else :
		labelMode = '%s'% MR_LANG( 'UNKNOWN' )

	return labelMode


def AsyncShowStatus( aStatus ) :
	import pvr.gui.WindowMgr as WinMgr
	showStatusWindow = [ WinMgr.WIN_ID_NULLWINDOW, WinMgr.WIN_ID_LIVE_PLATE, WinMgr.WIN_ID_MAINMENU ]

	rootWinow = xbmcgui.Window( 10000 )
	rootWinow.setProperty( 'PlayStatusLabel', '%s'% aStatus )

	loopCount = 0
	while loopCount <= 5 :
		if WinMgr.GetInstance( ).GetLastWindowID( ) not in showStatusWindow :
			break

		rootWinow.setProperty( 'PlayStatus', 'True' )
		time.sleep( 0.2 )
		rootWinow.setProperty( 'PlayStatus', 'False' )
		time.sleep( 0.2 )
		loopCount += 0.4

	rootWinow.setProperty( 'PlayStatus', 'False' )
	rootWinow.setProperty( 'PlayStatusLabel', '' )


def ResizeImageWidthByTextSize( aControlIdText, aControlIdImage, aText = '', aControlIdGroup = None ) :
	if not aControlIdImage :
		return
	if aText == '' and ( not aControlIdText ) :
		return
	"""
	if aControlIdText :
		LOG_TRACE( 'control txtControl[%s]'% aControlIdText.getId( ) )
	if aControlIdImage :
		LOG_TRACE( 'control imgControl[%s]'% aControlIdImage.getId( ) )
	if aControlIdGroup :
		LOG_TRACE( 'control grpControl[%s]'% aControlIdGroup.getId( ) )
	"""

	lblText = ''
	if aText == '' and aControlIdText :
		lblText = '%s'% aControlIdText.getLabel( )
	if aText != '' :
		lblText = '%s'% aText

	#LOG_TRACE( '---------text[%s]'% lblText )
	if lblText != '' :
		mWidth = aControlIdText.CalcTextWidth( lblText )
		aControlIdImage.setWidth( int( mWidth ) + 7 )
		aControlIdText.setWidth( int( mWidth ) + 7 )
		aControlIdText.setLabel( lblText )
		if aControlIdGroup :
			aControlIdGroup.setWidth( int( mWidth ) + 7 )
			#LOG_TRACE( '-------group width' )
		#LOG_TRACE( 'resize image label[%s] width[%s]'% ( lblText, int( mWidth ) ) )


def ResetPositionVolumeInfo( self, aTextLabel, aBaseWidth, aShowGroupID, aCalcTextID ) :
	if aTextLabel :
		width = self.getControl( aCalcTextID ).CalcTextWidth( aTextLabel )
		posw = aBaseWidth - ( 185 + width )
		self.getControl( aShowGroupID ).setPosition( int( posw ), 0 )


def KillScript( aId ) :
	try :
		pids = [ pid for pid in os.listdir( '/proc' ) if pid.isdigit( ) ]
		for pid in pids :
			if ( os.path.exists( '/proc/%s/stat' % pid ) ) :
				f = open( os.path.join( '/proc', pid, 'stat' ), 'rb' )
				data = f.readlines( )

				data = str( data[0] )
				data = data.strip( )
				data = data.split( )
				if data[3] == str( aId ) :
					KillScript( int( data[0] ) )

		os.system( 'kill -9 %s' % aId )
	except Exception, e :
		LOG_ERR( 'Error exception[%s]' % e )


def GetXBMCLanguageToPropLanguage( aLanguage ) :
	aLanguage = aLanguage.lower( )
	if aLanguage == 'English'.lower( ) or aLanguage == 'English (US)'.lower( ) :
		return ElisEnum.E_ENGLISH

	elif aLanguage == 'German'.lower( ) :
		return ElisEnum.E_DEUTSCH

	elif aLanguage == 'French'.lower( ) :
		return ElisEnum.E_FRENCH

	elif aLanguage == 'Italian'.lower( ) :
		return ElisEnum.E_ITALIAN

	elif aLanguage == 'Spanish'.lower( ) or aLanguage == 'Spanish (Argentina)'.lower( ) or aLanguage == 'Spanish (Mexico)'.lower( ) :
		return ElisEnum.E_SPANISH

	elif aLanguage == 'Czech'.lower( ) :
		return ElisEnum.E_CZECH

	elif aLanguage == 'Dutch'.lower( ) :
		return ElisEnum.E_DUTCH

	elif aLanguage == 'Polish'.lower( ) :
		return ElisEnum.E_POLISH

	elif aLanguage == 'Turkish'.lower( ) :
		return ElisEnum.E_TURKISH

	elif aLanguage == 'Russian'.lower( ) :
		return ElisEnum.E_RUSSIAN

	else :
		return ElisEnum.E_ENGLISH


def GetPropLanguageToXBMCLanguage( aProp ) :
	if aProp == ElisEnum.E_ENGLISH :
		return 'English'

	elif aProp == ElisEnum.E_DEUTSCH :
		return 'German'

	elif aProp == ElisEnum.E_FRENCH :
		return 'French'

	elif aProp == ElisEnum.E_ITALIAN :
		return 'Italian'

	elif aProp == ElisEnum.E_SPANISH :
		return 'Spanish'

	elif aProp == ElisEnum.E_CZECH :
		return 'Czech'

	elif aProp == ElisEnum.E_DUTCH :
		return 'Dutch'

	elif aProp == ElisEnum.E_POLISH :
		return 'Polish'

	elif aProp == ElisEnum.E_TURKISH :
		return 'Turkish'

	elif aProp == ElisEnum.E_RUSSIAN :
		return 'Russian'

	else :
		return 'German'


def GetXBMCLanguageToPropAudioLanguage( aLanguage ) :
	aLanguage = aLanguage.lower( )
	if aLanguage == 'Dutch'.lower( ) :
		return ElisEnum.E_DUTCH

	elif aLanguage == 'German'.lower( ) :
		return ElisEnum.E_DEUTSCH

	elif aLanguage == 'English'.lower( ) or aLanguage == 'English (US)'.lower( ) :
		return ElisEnum.E_ENGLISH

	elif aLanguage == 'French'.lower( ) :
		return ElisEnum.E_FRENCH

	elif aLanguage == 'Italian'.lower( ) :
		return ElisEnum.E_ITALIAN

	elif aLanguage == 'Spanish'.lower( ) or aLanguage == 'Spanish (Argentina)'.lower( ) or aLanguage == 'Spanish (Mexico)'.lower( ) :
		return ElisEnum.E_SPANISH

	elif aLanguage == 'Czech'.lower( ) :
		return ElisEnum.E_CZECH

	elif aLanguage == 'Polish'.lower( ) :
		return ElisEnum.E_POLISH

	elif aLanguage == 'Turkish'.lower( ) :
		return ElisEnum.E_TURKISH

	elif aLanguage == 'Russian'.lower( ) :
		return ElisEnum.E_RUSSIAN

	elif aLanguage == 'Arabic'.lower( ) :
		return ElisEnum.E_ARABIC

	elif aLanguage == 'Greek'.lower( ) :
		return ElisEnum.E_GREEK

	elif aLanguage == 'Danish'.lower( ) :
		return ElisEnum.E_DANISH

	elif aLanguage == 'Swedish'.lower( ) :
		return ElisEnum.E_SWEDISH

	elif aLanguage == 'Norwegian'.lower( ) :
		return ElisEnum.E_NORWEGIAN

	elif aLanguage == 'Korean'.lower( ) :
		return ElisEnum.E_KOREAN

	elif aLanguage == 'Finnish'.lower( ) :
		return ElisEnum.E_FINNISH

	elif aLanguage == 'Portuguese'.lower( ) or aLanguage == 'Portuguese (Brazil)'.lower( ) :
		return ElisEnum.E_PORTUGUESE

	elif aLanguage == 'Basque'.lower( ) :
		return ElisEnum.E_BASQUE

	elif aLanguage == 'Bulgarian'.lower( ) :
		return ElisEnum.E_BULGARIAN

	elif aLanguage == 'Croatian'.lower( ) :
		return ElisEnum.E_CROATIAN

	elif aLanguage == 'Estonian'.lower( ) :
		return ElisEnum.E_ESTONIAN

	elif aLanguage == 'Hebrew'.lower( ) :
		return ElisEnum.E_HEBREW

	elif aLanguage == 'Hungarian'.lower( ) :
		return ElisEnum.E_HUNGARIAN

	elif aLanguage == 'Latvian'.lower( ) :
		return ElisEnum.E_LATVIAN

	elif aLanguage == 'Lithuanian'.lower( ) :
		return ElisEnum.E_LITHUANIAN

	elif aLanguage == 'Persian (Iran)'.lower( ) :
		return ElisEnum.E_PERSIAN

	elif aLanguage == 'Romanian'.lower( ) :
		return ElisEnum.E_ROMANIAN

	elif aLanguage == 'Serbian'.lower( ) or aLanguage == 'Serbian (Cyrillic)'.lower( ) :
		return ElisEnum.E_SERBIAN

	elif aLanguage == 'Slovak'.lower( ) :
		return ElisEnum.E_SLOVAK

	elif aLanguage == 'Slovenian'.lower( ) :
		return ElisEnum.E_SLOVENIAN

	elif aLanguage == 'Thai'.lower( ) :
		return ElisEnum.E_TAI

	else :
		return ElisEnum.E_ENGLISH


def GetOffsetPosition( aControlList ) :
	pos = aControlList.getOffsetPosition( )
	if pos < 0 :
		pos = 0
	return pos


def CalculateProgress( aCurrentTime, aEpgStart, aDuration  ) :
	percent = 0
	startTime = aEpgStart
	endTime = aEpgStart + aDuration

	pastDuration = endTime - aCurrentTime

	if aCurrentTime > endTime : #past
		return 100

	elif aCurrentTime < startTime : #future
		return 0

	if pastDuration < 0 : #past
		pastDuration = 0

	if aDuration > 0 :
		percent = 100 - ( pastDuration * 100.0 / aDuration )

	else :
		percent = 0

	#LOG_TRACE( 'Percent[%s]'% percent )
	return percent


def GetXBMCResolutionWeightBySkin( ) :
	defHeight = 720

	try :
		xmlFile = os.path.join( xbmcaddon.Addon( xbmc.getSkinDir() ).getAddonInfo( 'path'), 'addon.xml' )
		parseTree = ElementTree.parse( xmlFile )
		treeRoot = parseTree.getroot( )
		getHeight = ''
		for node in treeRoot.findall( 'extension' ) :
			#LOG_TRACE( 'id[%s] text[%s]'% ( node.get( 'point' ), node.text ) )
			if getHeight : break
			for ele in node :
				#LOG_TRACE( 'id[%s] tag[%s]'% ( ele.get( 'height' ), ele.tag ) )
				if ele.tag.lower() == 'res' :
					getHeight = ele.get( 'height' )
					break

		if getHeight :
			defHeight = int( getHeight )

	except Exception, e :
		defHeight = 720
		LOG_ERR( 'Exception[%s]'% e )

	resWeight = int( defHeight ) / 720.0

	return resWeight


