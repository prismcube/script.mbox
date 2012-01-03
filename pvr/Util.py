import os
import sys
import time
import xbmcgui

from decorator import decorator
from odict import odict
from threading import RLock

from inspect import currentframe

gThreads = odict()

def ClearThreads( ):
	gThreads.clear()


def HasPendingThreads():
	for threadName, worker in gThreads.items():
		print 'worker name=%s' %threadName
		if worker:
			if worker.isAlive():
				print 'worker is live'
				return True
	return False
 

def WaitUtileThreadsJoin(timeout=None):
	print 'Total threads = %d' % len(gThreads)
	for threadName, worker in gThreads.items():
		if worker:
			if worker.isAlive():
				print 'wait until %s to join' % threadName
				worker.join(timeout)
				if worker.isAlive():
					print 'Thread %s still alive after timeout' %threadName
	print 'Done waiting for threads to die'

def MakeDir(dir):
	if not os.path.exists(dir):
		os.makedirs(dir)
	return dir

gGuiLock = False


@decorator
def GuiLock(func, *args, **kw):
	"""
	Decorator for setting/unsetting the xbmcgui lock on method
	entry and exit.
	"""
	global gGuiLock
	if gGuiLock: # prevent nested locks / double lock
		return func(*args, **kw)    
	else:
		try:
			gGuiLock = True
			xbmcgui.lock()
			result = func(*args, **kw)

		finally:
			xbmcgui.unlock()
			gGuiLock = False
		return result


@decorator
def RunThread(func, *args, **kwargs):
	from threading import Thread
	worker = Thread(target = func, name=func.__name__, args = args, kwargs = kwargs)
	gThreads[worker.getName()] = worker
	worker.start()
	return worker






import threading
import thread



class Mutex(threading.Thread):
	def __init__(self, aCondition):
		threading.Thread.__init__(self)
		self.mCondition = aCondition

		self.mutex = thread.allocate_lock()

	def Lock(self):
		print '[%s():%s]mutex_lock'% (currentframe().f_code.co_name, currentframe().f_lineno)
		self.mutex.acquire()
		#self.notify.acquire()

	def Notify(self):
		print '[%s():%s]mutex_notify'% (currentframe().f_code.co_name, currentframe().f_lineno)
		self.notify.notify()

	def Unlock(self):
		print '[%s():%s]mutex_unlock'% (currentframe().f_code.co_name, currentframe().f_lineno)
		self.mutex.release()



def epgInfoTime(localOffset, startTime, duration):
	
	epgStartTime = startTime + localOffset
	epgEndTime =  startTime + duration + localOffset

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

def epgInfoClock(flag, nowTime, strTime):

	strClock = []
	
	if flag == 1:
		strClock.append( time.strftime('%a, %d.%m.%Y', time.gmtime(nowTime) ) )
		if strTime % 2 == 0:
			strClock.append( time.strftime('%H:%M', time.gmtime(nowTime) ) )
		else :
			strClock.append( time.strftime('%H %M', time.gmtime(nowTime) ) )

	elif flag == 2:
		strClock.append( time.strftime('%a. %H:%M', time.gmtime(nowTime) ) )

	elif flag == 3:
		strClock.append( time.strftime('%H:%M:%S', time.gmtime(nowTime) ) )

	elif flag == 4:
		hour =  nowTime / 3600
		min  = (nowTime % 3600) / 60
		sec  = (nowTime % 3600) % 60
		ret = '%d:%02d:%02d' % ( hour, min, sec )
		return ret

	elif flag == 5:
		import re
		ret = re.split(':', strTime)
		timeT = int(ret[0]) * 3600 + int(ret[1]) * 60 + int(ret[2])
		return timeT

	#print 'epgClock[%s:%s]'% (strClock, time.strftime('%S', time.gmtime(stbClock)) )
	return strClock

def epgInfoComponentImage(component):
	print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
	from elisenum import ElisEnum
	tmpcom = []
	tmpcom = component
	tempFile = 0x00
	if (int(tmpcom[0]) == 1): #== ElisEnum.E_HasHDVideo:                # 1<<0
		tempFile |= 0x01
	if (int(tmpcom[1]) == 1): #== ElisEnum.E_Has16_9Video:              # 1<<1
		pass
	if (int(tmpcom[2]) == 1 ): #== ElisEnum.E_HasStereoAudio:            # 1<<2
		pass
	if (int(tmpcom[3]) == 1): #== ElisEnum.E_mHasMultichannelAudio:     # 1<<3
		pass
	if (int(tmpcom[4]) == 1): #== ElisEnum.E_mHasDolbyDigital:          # 1<<4
		tempFile |= 0x02
	if (int(tmpcom[5]) == 1): #== ElisEnum.E_mHasSubtitles:             # 1<<5
		tempFile |= 0x04
	if (int(tmpcom[6]) == 1): #== ElisEnum.E_mHasHardOfHearingAudio:    # 1<<6
		pass
	if (int(tmpcom[7]) == 1): #== ElisEnum.E_mHasHardOfHearingSub:      # 1<<7
		pass
	if (int(tmpcom[8]) == 1):#== ElisEnum.E_mHasVisuallyImpairedAudio: # 1<<8
		pass

	print 'component[%s] tempFile[%s]' % (component, tempFile)

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
		print 'unknown component image'

	return imagelist

def GetSelectedLongitudeString(longitude_str):
	print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

	ret = ''
	if longitude_str != []:
		longitude = int(longitude_str[0])

		if longitude < 1800 :
			log1 = longitude / 10
			log2 = longitude - (log1 * 10)
			ret = str('%d.%d E %s'% (log1, log2, longitude_str[2]))
	
		else:
			longitude = 3600 - longitude;
			log1 = longitude / 10
			log2 = longitude - (log1 * 10)
			ret = str('%d.%d W %s'% (log1, log2, longitude_str[2]))

	print ret
	return ret

def enumToString(type, value):
	from elisenum import ElisEnum

	ret = ''
	if type == 'type' :
		if value == ElisEnum.E_TYPE_TV :
			ret = 'tv'
		elif value == ElisEnum.E_TYPE_RADIO :
			ret = 'radio'
		elif value == ElisEnum.E_TYPE_DATA :
			ret = 'data'
		elif value == ElisEnum.E_TYPE_INVALID :
			ret = 'type_invalid'

	elif type == 'mode' :
		if value == ElisEnum.E_MODE_ALL :
			ret = 'ALL Channels'
		elif value == ElisEnum.E_MODE_FAVORITE :
			ret = 'favorite'
		elif value == ElisEnum.E_MODE_NETWORK :
			ret = 'network'
		elif value == ElisEnum.E_MODE_SATELLITE :
			ret = 'satellite'
		elif value == ElisEnum.E_MODE_CAS :
			ret = 'fta/cas'

	elif type == 'sort' :
		if value == ElisEnum.E_SORT_BY_DEFAULT :
			ret = 'default'
		elif value == ElisEnum.E_SORT_BY_ALPHABET :
			ret = 'alphabet'
		elif value == ElisEnum.E_SORT_BY_CARRIER :
			ret = 'carrier'
		elif value == ElisEnum.E_SORT_BY_NUMBER :
			ret = 'number'
		elif value == ElisEnum.E_SORT_BY_HD :
			ret = 'hd'

	elif type == 'Polarization' :
		if value == ElisEnum.E_LNB_HORIZONTAL :
			ret = 'Horz'
		elif value == ElisEnum.E_LNB_VERTICAL :
			ret = 'Vert'
		elif value == ElisEnum.E_LNB_LEFT :
			ret = 'Left'
		elif value == ElisEnum.E_LNB_RIGHT :
			ret = 'Righ'

	return ret.upper()

def ageLimit(cmd, agerating):
	from elisproperty import ElisPropertyEnum
	
	property = ElisPropertyEnum( 'Age Limit', cmd )
	#print 'TTTTTTTTTTTTTTT[%s][%s][%s]'% ( agerating, property.getProp(), property.getPropString() )

	isWatch = True
	limit = property.getProp()
	if limit == 0 :
		#no limit
		isLimit = False

	else:
		if limit <= agerating :
			#limitted
			isLimit = True
		else:
			isLimit = False

	return isLimit
