import os, sys, time
import xbmcgui
import xbmcaddon
from ElisEnum import ElisEnum
from util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR
#from inspect import currentframe
#__file__ = os.path.basename( currentframe().f_code.co_filename )

gSettings = xbmcaddon.Addon(id="script.mbox")

def GetSetting( aID ) :
	global gSettings
	LOG_TRACE('')
	return gSettings.getSetting( aID )


def SetSetting( aID, aValue ) :
	global gSettings	
	gSettings.setSetting( aID, aValue )


def GetImageByEPGComponent( aEPG, aFlag ) :
	if aFlag == ElisEnum.E_HasHDVideo and aEPG.mHasHDVideo :
		return 'confluence/OverlayHD.png' #ToDO -> support multi skin

	elif aFlag == ElisEnum.E_Has16_9Video and aEPG.mHas16_9Video :
		pass

	elif aFlag == ElisEnum.E_HasStereoAudio and aEPG.mHasStereoAudio :
		pass

	elif aFlag == ElisEnum.E_HasMultichannelAudio and aEPG.mHasMultichannelAudio :
		pass

	elif aFlag == ElisEnum.E_HasDolbyDigital and aEPG.mHasDolbyDigital :
		return 'confluence/dolbydigital.png' #ToDO -> support multi skin
	
	elif aFlag == ElisEnum.E_HasSubtitles and aEPG.mHasSubtitles :
		return 'confluence/OSDPlaylistNF.png' #ToDO -> support multi skin
	
	elif aFlag == ElisEnum.E_HasHardOfHearingAudio and aEPG.mHasHardOfHearingAudio:
		pass
	
	elif aFlag == ElisEnum.E_HasHardOfHearingSub and aEPG.mHasHardOfHearingSub:
		pass
	
	elif aFlag == ElisEnum.E_HasVisuallyImpairedAudio and aEPG.mHasVisuallyImpairedAudio:
		pass
	
	else :
		pass

	return ''


def GetSelectedLongitudeString(aLongitude, aName):
	LOG_TRACE( 'Enter' )

	ret = ''

	if aLongitude < 1800 :
		log1 = aLongitude / 10
		log2 = aLongitude - (log1 * 10)
		ret = str( '%d.%d E %s'% (log1, log2, aName) )

	else:
		aLongitude = 3600 - aLongitude
		log1 = aLongitude / 10
		log2 = aLongitude - (log1 * 10)
		ret = str('%d.%d W %s'% (log1, log2, aName) )

	LOG_TRACE( 'Leave[%s]'% ret )
	return ret


def EnumToString(aType, aValue):
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

	return ret.upper()


def AgeLimit(aPropertyAge, aEPGAge):

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
		parse2 = re.findall('[0-9]\w*', aLabel)

	else :
		parse1 = re.split(' ', aLabel)
		parse2 = re.findall('[0-9]\w*', parse1[1])

	#LOG_TRACE('===========aLabel[%s] parse2[%s]'% (aLabel,parse2[0]) )

	return int(parse2[0])



def MR_LANG( aString ) :
	mStrLanguage = GetInstance()
	return mStrLanguage.StringTranslate(aString)
	#return aString


def Strings(aStringID, aReplacements = None):
	string = xbmcaddon.Addon(id = 'script.mbox').getLocalizedString(aStringID)
	if aReplacements is not None :
		return string % aReplacements
	else :
		return string


def GetCalibration( aX, aY, aWidth, aHeight ) :
	#a1 = xbmc.executehttpapi("GetGUISetting(0, resolutions)")
	temX = 100
	temY = 100
	temA = 100
	temB = 100
	#rate = ( 1280 - 33 ) / float( 1280 ) * 100
	#x = aX * ( 1280 - temX ) / float( 1280 )
	#y = aY * ( 720 - temY ) / float( 720 )
	x = aX - ( aX * temX / float( 1280 ) )
	y = aY - ( aY * temY / float( 1280 ) )
	w = 352 - ( 352 * temX / float( 1280 ) )
	h = 198 - ( 198 * temY / float( 720 ) )

	x = x + temX
	y = y + temY

	print 'dhkim test pos in GetCalibration = %s, %s, %s, %s' % ( x, y, w, h )
	return int( x), int(y), int(w), int(h)


gMRStringHash = {}
gCacheMRLanguage = None
def GetInstance():
	global gCacheMRLanguage
	if not gCacheMRLanguage:
		gCacheMRLanguage = CacheMRLanguage()
	else:
		pass
		#print 'youn check already windowmgr is created'

	return gCacheMRLanguage

class CacheMRLanguage( object ) :
	def __init__( self ):

		from BeautifulSoup import BeautifulSoup

		self.mStrLanguage = None

		scriptDir = xbmcaddon.Addon('script.mbox').getAddonInfo('path')
		xmlFile = '%s/pvr/gui/windows/strings.xml'% scriptDir
		print 'xmlFile[%s]'% xmlFile
		fp = open(xmlFile)
		xml = fp.read()
		fp.close()

		self.mStrLanguage = BeautifulSoup(xml)

		global gMRStringHash
		for node in self.mStrLanguage.findAll('string'):
			gMRStringHash[ node.string ] = int(node['id'])

		LOG_TRACE('============cache Language')

	def StringTranslate(self, string = None):
		strId = gMRStringHash.get(string, None)
		if strId :
			xmlString = Strings( strId )
			print 'xml_string[%s] parse[%s]'% (string, xmlString)
			return xmlString.encode('utf-8')

		else:
			return string


