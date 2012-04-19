import os, sys, time
import xbmcgui
import xbmcaddon

from util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR
from inspect import currentframe
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


def EpgInfoComponentImage(aEpg):
	LOG_TRACE( 'Enter' )
	from ElisEnum import ElisEnum

	tempFile = 0x00
	if aEpg.mHasHDVideo :              #== ElisEnum.E_HasHDVideo:                # 1<<0
		tempFile |= 0x01
	if aEpg.mHas16_9Video :            #== ElisEnum.E_Has16_9Video:              # 1<<1
		pass
	if aEpg.mHasStereoAudio :          #== ElisEnum.E_HasStereoAudio:            # 1<<2
		pass
	if aEpg.mHasMultichannelAudio :    #== ElisEnum.E_mHasMultichannelAudio:     # 1<<3
		pass
	if aEpg.mHasDolbyDigital :         #== ElisEnum.E_mHasDolbyDigital:          # 1<<4
		tempFile |= 0x02
	if aEpg.mHasSubtitles :            #== ElisEnum.E_mHasSubtitles:             # 1<<5
		tempFile |= 0x04
	if aEpg.mHasHardOfHearingAudio :   #== ElisEnum.E_mHasHardOfHearingAudio:    # 1<<6
		pass
	if aEpg.mHasHardOfHearingSub :     #== ElisEnum.E_mHasHardOfHearingSub:      # 1<<7
		pass
	if aEpg.mHasVisuallyImpairedAudio :#== ElisEnum.E_mHasVisuallyImpairedAudio: # 1<<8
		pass

	LOG_TRACE( 'component flag[%s]'% tempFile )

	imgData  = 'IconTeletext.png'
	imgDolby = 'confluence/dolbydigital.png'
	imgHD    = 'confluence/OverlayHD.png'
	imagelist = []
	if tempFile == 1:
		imagelist.append(imgHD)
	elif tempFile == 2:	
		imagelist.append(imgDolby)
	elif tempFile == 3:	
		imagelist.append(imgDolby)
		imagelist.append(imgHD)
	elif tempFile == 4:	
		imagelist.append(imgData)
	elif tempFile == 5:	
		imagelist.append(imgData)
		imagelist.append(imgHD)
	elif tempFile == 6:	
		imagelist.append(imgData)
		imagelist.append(imgDolby)
	elif tempFile == 7:	
		imagelist.append(imgData)
		imagelist.append(imgDolby)
		imagelist.append(imgHD)
	else:
		LOG_TRACE( 'unknown component image' )

	return imagelist

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
		list = []
		for item in aClassList :
			req = []
			item.appendReqBuffer( req )
			list.append( req )
	
		if aMode == 'print' :
			LOG_TRACE( '%s'% list)
		elif aMode == 'convert' :
			return list

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


def Strings(aStringID, aReplacements = None):
    string = xbmcaddon.Addon(id = 'script.mbox').getLocalizedString(aStringID)
    if aReplacements is not None :
        return string % aReplacements
    else :
        return string

def MR_LANG( aString ) :
	return aString

