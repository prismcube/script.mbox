import xbmc, xbmcgui, xbmcaddon, sys, os, shutil, time, re, stat
from elisinterface.ElisEnum import ElisEnum
import pvr.Platform
from elisinterface.util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR

try :
	import xml.etree.cElementTree as ElementTree
except Exception, e :
	from elementtree import ElementTree

import urllib
from subprocess import *

gSettings = xbmcaddon.Addon( id="script.mbox" )
gSupportLanguage = [ 'Czech', 'Dutch', 'French', 'German', 'Italian', 'Polish', 'Russian', 'Spanish', 'Turkish', 'Arabic', 'Korean', 'Slovak' ]


def GetSetting( aID ) :
	global gSettings
	return gSettings.getSetting( aID )


def SetSetting( aID, aValue ) :
	global gSettings	
	gSettings.setSetting( aID, aValue )


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

	casInfo = HasCasInfoByChannel( aChannel )
	self.setProperty( E_XML_PROPERTY_CAS, 'True' )
	if casInfo :
		for casName in casInfo :
			aPropertyID = 'iCas' + casName
			self.setProperty( aPropertyID, casName )
	else :
		return


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
		if pmtEvent.mAudioCount > 0 and pmtEvent.mAudioStream[pmtEvent.mAudioSelectedIndex] == ElisEnum.E_AUD_STREAM_DDPLUS :
			ret = True

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


def GetSelectedLongitudeString( aLongitude, aName ) :
	ret = ''

	if aLongitude < 1800 :
		log1 = aLongitude / 10
		log2 = aLongitude - (log1 * 10)
		ret = str( '%d.%d E %s'% (log1, log2, aName ) )

	else:
		aLongitude = 3600 - aLongitude
		log1 = aLongitude / 10
		log2 = aLongitude - (log1 * 10)
		ret = str( '%d.%d W %s' %( log1, log2, aName) )

	return ret


def EnumToString( aType, aValue ) :
	from elisinterface.ElisEnum import ElisEnum
	ret = ''
	if aType == 'type' :
		if aValue == ElisEnum.E_SERVICE_TYPE_TV :
			ret = MR_LANG( 'tv' )
		elif aValue == ElisEnum.E_SERVICE_TYPE_RADIO :
			ret = MR_LANG( 'radio' )
		elif aValue == ElisEnum.E_SERVICE_TYPE_DATA :
			ret = MR_LANG( 'data' )
		elif aValue == ElisEnum.E_SERVICE_TYPE_INVALID :
			ret = MR_LANG( 'type_invalid' )

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

	elif aType == 'sort' :
		if aValue == ElisEnum.E_SORT_BY_DEFAULT :
			ret = MR_LANG( 'default' )
		elif aValue == ElisEnum.E_SORT_BY_ALPHABET :
			ret = MR_LANG( 'alphabet' )
		elif aValue == ElisEnum.E_SORT_BY_CARRIER :
			ret = MR_LANG( 'carrier' )
		elif aValue == ElisEnum.E_SORT_BY_NUMBER :
			ret = MR_LANG( 'number' )
		elif aValue == ElisEnum.E_SORT_BY_HD :
			ret = MR_LANG( 'hd' )

	elif aType == 'Polarization' :
		if aValue == ElisEnum.E_LNB_HORIZONTAL :
			ret = 'Horz'
		elif aValue == ElisEnum.E_LNB_VERTICAL :
			ret = 'Vert'
		elif aValue == ElisEnum.E_LNB_LEFT :
			ret = 'Left'
		elif aValue == ElisEnum.E_LNB_RIGHT :
			ret = 'Righ'

	return ret.upper( )


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
				print 'except[%s]'% e

		#print 'strId[%s]trans[%s]'% (strId, string)
		return string


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


def CreateDirectory( aPath ) :
	if os.path.exists( aPath ) :
		return

	os.makedirs( aPath, 0644 )


def CreateFile( aPath ) :
	try :
		open( aPath, 'w', 0644 )
	except Exception, e :
		LOG_ERR( 'except[%s]'% e )


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
		LOG_ERR( 'except[%s]'% e )

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
		LOG_ERR( 'except[%s]'% e )

	return True


def CheckDirectory( aPath ) :
	return os.path.exists( aPath )


def CheckHdd( ) :
	import pvr.Platform
	import pvr.ElisMgr
	if not pvr.Platform.GetPlatform( ).IsPrismCube( ) :
		return False

	retList = pvr.ElisMgr.GetInstance( ).GetCommander( ).HDD_GetMountPath( )
	if retList and len( retList ) > 0 and retList[0].mError == 0 :
		return True
	else :
		return False


def	HasAvailableRecordingHDD( ) :
	import pvr.gui.DialogMgr as DiaMgr
	if not CheckHdd( ) :
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
		LOG_ERR( 'except[%s] cmd[%s]'% ( e, cmd ) )

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
		LOG_ERR( 'except[%s] cmd[%s]'% ( e, cmd ) )

	return isVerify


def GetDeviceSize( path ) :
	total, used, free = 0, 0, 0

	try :
		st = os.statvfs(path)
		free = st.f_bavail * st.f_frsize
		total = st.f_blocks * st.f_frsize
		used = (st.f_blocks - st.f_bfree) * st.f_frsize

	except Exception, e :
		LOG_TRACE( 'except[%s]'% e )
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
		LOG_TRACE( 'except[%s]'% e )
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
		LOG_TRACE( 'except[%s]'% e )
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
		LOG_ERR( 'except[%s] Could not open[%s]'% ( e, openFile ) )

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
		LOG_ERR( 'except[%s] cmd[%s]'% ( e, aOpenFile ) )

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
		LOG_ERR( 'except[%s] cmd[%s]'% ( e, cmd ) )
		isCopy = False

	return isCopy


def CopyToFile( aSourceFile, aDestFile ) :
	isCopy = True
	try :
		shutil.copyfile( aSourceFile, aDestFile )
		os.system( 'sync' )
		time.sleep( 0.5 )

	except Exception, e :
		LOG_ERR( 'except[%s] source[%s] desc[%s]'% ( e, aSourceFile, aDestFile ) )
		isCopy = False

	return isCopy


def CopyToDirectory( aSourceDirectory, aDestPath ) :
	isCopy = True
	try :
		shutil.copytree( aSourceDirectory, aDestPath )
		os.system( 'sync' )
		time.sleep( 0.5 )

	except Exception, e :
		LOG_ERR( 'except[%s] source[%s] desc[%s]'% ( e, aSourceDirectory, aDestPath ) )
		isCopy = False

	return isCopy


def GetDirectorySize( aPath ) :
	dir_size = 0
	for ( path, dirs, files ) in os.walk( aPath ) :
		for file in files :
			filename = os.path.join( path, file )
			dir_size += os.path.getsize( filename )

	return dir_size 


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
					LOG_ERR( 'except[%s] writeError writefile[%s]'% ( e, aWriteFileName ) )
					isExist = False

			f.close( )

	except IOError, e :
		LOG_ERR( 'except[%s] url[%s]'% ( e, aUrl ) )

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
	tagNames = [ 'VIEW_MODE', 'SORT_MODE', 'EPG_MODE', 'ADDON_VIEW_MODE', 'Addons_Sort', 'RSS_FEED' ]

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


def ReadToCmdBlock( ) :
	cmdBlock = ''
	try :
		rf = open( '/proc/cmdline', 'r' )
		cmdBlock = rf.readline( ).strip( )
		rf.close( )
	except Exception, e :
		LOG_ERR( 'except[%s] file not found[/proc/cmdline]'% e )
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
		LOG_ERR( 'except[%s] cmd1[%s] cmd2[%s]'% ( e, cmd1, cmd2 ) )


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
		LOG_ERR( 'except[%s] cmd1[%s] cmd2[%s]'% ( e, cmd1, cmd2 ) )
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


	def GetPipPosition2( self, aX, aY, aWidth, aHeight ) :
		from pvr.gui.GuiConfig import E_WINDOW_HEIGHT, E_WINDOW_WIDTH
		x = aX
		y = aY
		w = aWidth
		h = aHeight


		x = x * ( E_WINDOW_WIDTH  - ( self.mLeft + ( E_WINDOW_WIDTH  -  self.mRight ) ) ) / float( E_WINDOW_WIDTH )
		y = y * ( E_WINDOW_HEIGHT - ( self.mTop  + ( E_WINDOW_HEIGHT - self.mBottom ) ) ) / float( E_WINDOW_HEIGHT )
		w = w * ( E_WINDOW_WIDTH  - ( self.mLeft + ( E_WINDOW_WIDTH  -  self.mRight ) ) ) / float( E_WINDOW_WIDTH ) - 10
		h = h * ( E_WINDOW_HEIGHT - ( self.mTop  + ( E_WINDOW_HEIGHT - self.mBottom ) ) ) / float( E_WINDOW_HEIGHT ) - 10
		#1280 - ( 28 + ( 1280 - 1256 ) ) / 1280 = 1280 - 52, 1228 / 1280 = 0.959
		#720 - ( 19 + 720 - 705 ) / 720 = 720 - 34 = 0.952

		"""
		x = x * ( E_WINDOW_WIDTH  - ( self.mLeft + ( E_WINDOW_WIDTH  -  self.mRight ) ) ) / float( E_WINDOW_WIDTH )
		y = y * ( E_WINDOW_HEIGHT - ( self.mTop  + ( E_WINDOW_HEIGHT - self.mBottom ) ) ) / float( E_WINDOW_HEIGHT )
		w = w * ( self.mRight / float( E_WINDOW_WIDTH ) ) - 15
		h = h * ( self.mBottom / float( E_WINDOW_HEIGHT ) ) - 10
		"""

		x = x + self.mLeft
		y = y + self.mTop

		x = round( x )
		y = round( y )
		w = round( w )
		h = round( h )
		print '----------------------mLeft[%s] mRight[%s] mTop[%s] bottom[%s] zoom[%s]'% ( self.mLeft, self.mRight, self.mTop, self.mBottom, self.mZoom )
		print '----------------------x[%s] y[%s] w[%s] h[%s]'% ( x, y, w, h )
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
	showStatusWindow = [ WinMgr.WIN_ID_NULLWINDOW, WinMgr.WIN_ID_LIVE_PLATE, WinMgr.WIN_ID_MAINMENU, WinMgr.WIN_ID_PIP_WINDOW ]

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


