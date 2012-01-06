import os
import sys
import time
import xbmcgui


from inspect import currentframe
__file__ = os.path.basename( currentframe().f_code.co_filename )

def EpgInfoTime(aLocalOffset, aStartTime, aDuration):

	epgStartTime = aStartTime + aLocalOffset
	epgEndTime =  aStartTime + aDuration + aLocalOffset

	startTime_hh = time.strftime('%H', time.gmtime(epgStartTime) )
	startTime_mm = time.strftime('%M', time.gmtime(epgStartTime) )
	endTime_hh = time.strftime('%H', time.gmtime(epgEndTime) )
	endTime_mm = time.strftime('%M', time.gmtime(epgEndTime) )

	str_startTime = str ('%02s:%02s -'% (startTime_hh,startTime_mm) )
	str_endTime = str ('%02s:%02s'% (endTime_hh,endTime_mm) )

	print 'epgStart[%s] epgEndTime[%s]'% (epgStartTime, epgEndTime)
	print 'epgStart[%s] epgEndTime[%s]'% (time.strftime('%x %X',time.gmtime(epgStartTime)), time.strftime('%x %X',time.gmtime(epgEndTime)) )
	print 'start[%s] end[%s]'%(str_startTime, str_endTime)
	print 'hh[%s] mm[%s] hh[%s] mm[%s]' % (startTime_hh, startTime_mm, endTime_hh, endTime_mm)

	ret = []
	ret.append(str_startTime)
	ret.append(str_endTime)

	return ret

def EpgInfoClock(aFlag, aNowTime, aStrTime):

	strClock = []
	
	if aFlag == 1:
		strClock.append( time.strftime('%a, %d.%m.%Y', time.gmtime(aNowTime) ) )
		if aStrTime % 2 == 0:
			strClock.append( time.strftime('%H:%M', time.gmtime(aNowTime) ) )
		else :
			strClock.append( time.strftime('%H %M', time.gmtime(aNowTime) ) )

	elif aFlag == 2:
		strClock.append( time.strftime('%a. %H:%M', time.gmtime(aNowTime) ) )

	elif aFlag == 3:
		strClock.append( time.strftime('%H:%M:%S', time.gmtime(aNowTime) ) )

	elif aFlag == 4:
		hour =  aNowTime / 3600
		min  = (aNowTime % 3600) / 60
		sec  = (aNowTime % 3600) % 60
		ret = '%d:%02d:%02d' % ( hour, min, sec )
		return ret

	elif aFlag == 5:
		import re
		ret = re.split(':', aStrTime)
		timeT = int(ret[0]) * 3600 + int(ret[1]) * 60 + int(ret[2])
		return timeT

	#print 'epgClock[%s:%s]'% (strClock, time.strftime('%S', time.gmtime(stbClock)) )
	return strClock

def EpgInfoComponentImage(aEpg):
	print '[%s():%s]'% (__file__, currentframe().f_lineno)
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

	print '[%s():%s]component flag[%s]'% (__file__, currentframe().f_lineno, tempFile)

	imgData  = 'confluence/IconTeletext.png'
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
		print '[%s():%s]unknown component image'% (__file__, currentframe().f_lineno)

	return imagelist

def GetSelectedLongitudeString(aLongitude, aName):
	print '[%s():%s]'% (__file__, currentframe().f_lineno)

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

	print ret
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

def AgeLimit(aCmd, aAgerating):
	from ElisProperty import ElisPropertyEnum

	property = ElisPropertyEnum( 'Age Limit', aCmd )
	#print 'TTTTTTTTTTTTTTT[%s][%s][%s]'% ( agerating, property.getProp(), property.getPropString() )

	isWatch = True
	limit = property.GetProp()
	if limit == 0 :
		#no limit
		isLimit = False

	else:
		if limit <= aAgerating :
			#limitted
			isLimit = True
		else:
			isLimit = False

	return isLimit

def ClassToList( aMode, aClass ) :

	if aClass :
		list = []
		for item in aClass :
			req = []
			item.appendReqBuffer( req )
			list.append( req )
	
		if aMode == 'print' :
			print '[%s():%s]%s'% (__file__, currentframe().f_lineno, list)
		elif aMode == 'convert' :
			return list

