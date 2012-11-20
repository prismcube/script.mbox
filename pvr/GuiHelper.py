import xbmcaddon, sys, os, shutil, time, re, stat
from ElisEnum import ElisEnum
import pvr.Platform
from util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR
from elementtree import ElementTree
import urllib
from subprocess import *

gSettings = xbmcaddon.Addon( id="script.mbox" )


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
#			label[0] = MR_LANG( 'Error EPG' )
			label[0] = MR_LANG( 'No EPG Information is available' )
#			label[1] = MR_LANG( 'Can not found EPG Information' )
		else :
			conflictNum = len( aInfo ) - 1
			if conflictNum > 2 :
				conflictNum = 2

			label[0] = MR_LANG( 'The recording you just requested confilcts with' )

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
	dialog.SetDialogProperty( MR_LANG( 'Attention' ), label[0], label[1], label[2] )
	dialog.doModal( )


def GetImageByEPGComponent( aEPG, aFlag ) :
	if aFlag == ElisEnum.E_HasHDVideo and aEPG.mHasHDVideo :
		#return 'OverlayHD.png' #ToDO -> support multi skin
		return ElisEnum.E_HasHDVideo

	elif aFlag == ElisEnum.E_Has16_9Video and aEPG.mHas16_9Video :
		pass

	elif aFlag == ElisEnum.E_HasStereoAudio and aEPG.mHasStereoAudio :
		pass

	elif aFlag == ElisEnum.E_HasMultichannelAudio and aEPG.mHasMultichannelAudio :
		pass

	elif aFlag == ElisEnum.E_HasDolbyDigital and aEPG.mHasDolbyDigital :
		#return 'dolbydigital.png' #ToDO -> support multi skin
		return ElisEnum.E_HasDolbyDigital
	
	elif aFlag == ElisEnum.E_HasSubtitles and aEPG.mHasSubtitles :
		#return 'IconTeletext.png' #ToDO -> support multi skin
		return ElisEnum.E_HasSubtitles
	
	elif aFlag == ElisEnum.E_HasHardOfHearingAudio and aEPG.mHasHardOfHearingAudio :
		pass
	
	elif aFlag == ElisEnum.E_HasHardOfHearingSub and aEPG.mHasHardOfHearingSub :
		pass
	
	elif aFlag == ElisEnum.E_HasVisuallyImpairedAudio and aEPG.mHasVisuallyImpairedAudio :
		pass
	
	else :
		pass

	return 0


def GetPropertyByEPGComponent( aEPG ) :
	setPropertyData  = 'False'
	setPropertyDolby = 'False'
	setPropertyHD    = 'False'
	bitCount = 0
	bitCount += GetImageByEPGComponent( aEPG, ElisEnum.E_HasSubtitles )
	bitCount += GetImageByEPGComponent( aEPG, ElisEnum.E_HasDolbyDigital )
	bitCount += GetImageByEPGComponent( aEPG, ElisEnum.E_HasHDVideo )
	#LOG_TRACE('component bitCount[%s]'% bitCount)

	if bitCount == ElisEnum.E_HasDolbyDigital + ElisEnum.E_HasHDVideo :
		setPropertyData  = 'False'
		setPropertyDolby = 'True'
		setPropertyHD    = 'True'

	elif bitCount == ElisEnum.E_HasHDVideo :
		setPropertyData  = 'False'
		setPropertyDolby = 'False'
		setPropertyHD    = 'True'

	elif bitCount == ElisEnum.E_HasDolbyDigital :
		setPropertyData  = 'False'
		setPropertyDolby = 'True'
		setPropertyHD    = 'False'

	elif bitCount == ElisEnum.E_HasSubtitles :
		setPropertyData  = 'True'
		setPropertyDolby = 'False'
		setPropertyHD    = 'False'

	elif bitCount == ElisEnum.E_HasSubtitles + ElisEnum.E_HasDolbyDigital + ElisEnum.E_HasHDVideo :
		setPropertyData  = 'True'
		setPropertyDolby = 'True'
		setPropertyHD    = 'True'

	elif bitCount == ElisEnum.E_HasSubtitles + ElisEnum.E_HasDolbyDigital :
		setPropertyData  = 'True'
		setPropertyDolby = 'True'
		setPropertyHD    = 'False'

	elif bitCount == ElisEnum.E_HasSubtitles + ElisEnum.E_HasHDVideo :
		setPropertyData  = 'True'
		setPropertyDolby = 'False'
		setPropertyHD    = 'True'

	return [ setPropertyData, setPropertyDolby, setPropertyHD ]


def HasEPGComponent( aEPG, aFlag ) :
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
	from ElisEnum import ElisEnum
	ret = ''
	if aType == 'type' :
		if aValue == ElisEnum.E_SERVICE_TYPE_TV :
			ret = 'tv'
		elif aValue == ElisEnum.E_SERVICE_TYPE_RADIO :
			ret = 'radio'
		elif aValue == ElisEnum.E_SERVICE_TYPE_DATA :
			ret = 'data'
		elif aValue == ElisEnum.E_SERVICE_TYPE_INVALID :
			ret = 'type_invalid'

	elif aType == 'mode' :
		if aValue == ElisEnum.E_MODE_ALL :
			ret = 'ALL Channels'
		elif aValue == ElisEnum.E_MODE_FAVORITE :
			ret = 'favorite'
		elif aValue == ElisEnum.E_MODE_NETWORK :
			ret = 'network'
		elif aValue == ElisEnum.E_MODE_SATELLITE :
			ret = 'satellite'
		elif aValue == ElisEnum.E_MODE_CAS :
			ret = 'fta/cas'

	elif aType == 'sort' :
		if aValue == ElisEnum.E_SORT_BY_DEFAULT :
			ret = 'default'
		elif aValue == ElisEnum.E_SORT_BY_ALPHABET :
			ret = 'alphabet'
		elif aValue == ElisEnum.E_SORT_BY_CARRIER :
			ret = 'carrier'
		elif aValue == ElisEnum.E_SORT_BY_NUMBER :
			ret = 'number'
		elif aValue == ElisEnum.E_SORT_BY_HD :
			ret = 'hd'

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


def AgeLimit( aPropertyAge, aEPGAge ) :
	isLimit = False
	if aPropertyAge == 0 :
		#no limit
		isLimit = False

	else:
		if aPropertyAge <= aEPGAge :
			#limitted
			isLimit = True
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

	LOG_ERR( 'Can not found list item : %s' % aString )
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
					LOG_ERR( 'Can not find string' )
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


def RemoveDirectory( aPath ) :
	if not os.path.exists( aPath ) :
		return

	shutil.rmtree( aPath )


def CheckDirectory( aPath ) :
	if not os.path.exists( aPath ) :
		return False

	return True


def CheckHdd( ) :
	cmd = 'df'
	parsing = Popen( cmd, shell=True, stdout=PIPE )
	parsing = parsing.stdout.read( ).strip( )
	if parsing.count( '/dev/sda' ) >= 3 :
		return True

	return False


def	HasAvailableRecordingHDD( ) :
	import pvr.gui.DialogMgr as DiaMgr
	if CheckHdd( ) == False :
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Hard disk drive not detected' ) )
		dialog.doModal( )
		return False

	return True


def CheckEthernet( aEthName ) :
	status = 'down'
	cmd = 'cat /sys/class/net/%s/operstate'% aEthName
	try :
		p = Popen( cmd, shell=True, stdout=PIPE )
		status = p.stdout.read( ).strip( )
		LOG_TRACE('-------------linkStatus[%s]'% status )

	except Exception, e :
		LOG_ERR( 'except[%s] cmd[%s]'% ( e, cmd ) )

	return status


def CheckMD5Sum( aSourceFile, aMd5 ) :
	isVerify = False
	cmd = 'md5sum %s |awk \'{print $1}\''% aSourceFile

	if not os.path.exists( aSourceFile ) :
		LOG_TRACE( '------------file not found[%s]'% aSourceFile )
		return isVerify

	try :
		p = Popen( cmd, shell=True, stdout=PIPE )
		readMd5 = p.stdout.read( ).strip( )
		LOG_TRACE('-------------checkMd5[%s] sourceMd5[%s]'% ( readMd5, aMd5 ) )
		if readMd5 == aMd5 :
			isVerify = True

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
	tFile = '/tmp/test'
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
				if pars[0] == 0 :
					pars[0] = 4096	#directory size block

				pars[1] = re.sub( '\n', '', pars[1] )
				if pars[1] :
					fileList.append( pars )

	except Exception, e :
		LOG_TRACE( 'except[%s]'% e )
		return False

	return fileList


def GetSTBVersion( ) :
	stbversion = ''
	openFile = '/etc/stbversion'
	try :
		fp = open( openFile, 'r' )
		stbversion = fp.readline( ).strip( )
		fp.close( )

	except Exception, e :
		LOG_ERR( 'except[%s] cmd[%s]'% ( e, openFile ) )

	return stbversion


def UnpackToUSB( aZipFile, aDestPath ) :
	isCopy = False
	cmd = 'unzip -o %s -d %s'% ( aZipFile, aDestPath )

	if not os.path.exists( aDestPath ) :
		LOG_TRACE( '------------check usb[%s]'% aDestPath )
		return isCopy

	RemoveDirectory( '%s/update'% aDestPath )
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


def GetURLpage( aUrl, aWriteFileName = None, aCache = True ) :
	isExist = False
	try :
		#f = urllib.urlopen( url )
		f = urllib.URLopener( ).open( aUrl )
		if f :
			isExist = True
			if aCache and aWriteFileName :
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


def ParseStringInXML( xmlFile, tagNames ) :
	lists = []
	#if os.path.exists(xmlFile) :
	if xmlFile :

		parseTree = ElementTree.parse( xmlFile )
		treeRoot = parseTree.getroot( )

		for node in treeRoot.findall( 'software' ) :
			lines = []
			for tagName in tagNames :
				if node.findall( tagName ) :
					descList = []
					for element in node.findall( tagName ) :
						#elementry = [ str(element.text), '%s\r\n'% str(element) ]
						elementry = str( element.text )
						if tagName == 'description' :
							descList.append( elementry )
						else :
							lines.append( elementry )

					if descList and len( descList ) :
						lines.append( descList )

				else :
					lines.append('')

			LOG_TRACE( 'parse[%s]'% lines )
			if lines :
				lists.append( lines )

	if lists == [] or len( lists ) < 1 :
		lists = None

	return lists


def ParseStringInPattern( aToken, aData ) :
	aData = re.sub( ' ', '', aData )
	return re.split( aToken, aData.strip( ) )


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

