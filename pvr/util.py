import os
import sys
import time
import xbmcgui

from decorator import decorator
from odict import odict
from threading import RLock

from inspect import currentframe

__workersByName = odict()

def clearWorkers():
	__workersByName.clear()


def hasPendingWorkers():
	for workerName, worker in __workersByName.items():
		print 'worker name=%s' %workerName
		if worker:
			if worker.isAlive():
				print 'worker is live'
				return True
	return False
 

def waitForWorkersToDie(timeout=None):
	print 'Total threads spawned = %d' % len(__workersByName)
	for workerName, worker in __workersByName.items():
		if worker:
			if worker.isAlive():
				print 'Waiting for thread %s to die...' % workerName
				worker.join(timeout)
				if worker.isAlive():
					print 'Thread %s still alive after timeout' %workerName
	print 'Done waiting for threads to die'

def requireDir(dir):
	if not os.path.exists(dir):
		os.makedirs(dir)
	return dir


@decorator
def run_async(func, *args, **kwargs):
	from threading import Thread
	worker = Thread(target = func, name=func.__name__, args = args, kwargs = kwargs)
	__workersByName[worker.getName()] = worker
	worker.start()
	return worker

@decorator
def catchall(func, *args, **kw):
	try:
		return func(*args, **kw)
	except Exception, ex:
		print 'CATCHALL: Caught exception %s on method %s' % (str(ex), func.__name__)


@decorator
def catchall_ui(func, *args, **kw):
	try:
		return func(*args, **kw)
	except Exception, ex:
		log.error(sys.exc_info())
		log.exception('CATCHALL_UI: Caught %s exception %s on method %s' % (type(ex), str(ex), func.__name__))
		msg1 = str(ex)
		msg2 = ''
		msg3 = ''
		n = 45
		if len(msg1) > n:
			msg2 = msg1[n:]
			msg1 = msg1[:n]
		if len(msg2) > n:
			msg3 = msg2[n:]
			msg2 = msg2[:n]
		xbmcgui.Dialog().ok('Error: %s' % func.__name__, msg1, msg2, msg3)

def is_digit(str):
	try:
		tmp = float(str)
		return True
	except ValueError:
		return False

@decorator
def synchronized(func):
	"""Synchronizes method invocation on an object using the method name as the mutex"""
	
	def wrapper(self,*__args,**__kw):
		try:
			rlock = self.__get__('_sync_lock_%s' % func.__name__)
			#rlock = self._sync_lock
		except AttributeError:
			from threading import RLock
			rlock = self.__dict__.setdefault('_sync_lock_%s' % func.__name__, RLock())
		rlock.acquire()
		try:
			return func(self,*__args,**__kw)
		finally:
			rlock.release()

	wrapper.__name__ = func.__name__
	wrapper.__dict__ = func.__dict__
	wrapper.__doc__ = func.__doc__
	return wrapper

@decorator
def sync_instance(func):
	"""Synchronizes method invocation on an object using the object instance as the mutex"""
	
	def wrapper(self,*__args,**__kw):
		try:
			rlock = self._sync_lock
		except AttributeError:
			from threading import RLock
			rlock = self.__dict__.setdefault('_sync_lock', RLock())
		rlock.acquire()
		try:
			return func(self,*__args,**__kw)
		finally:
			rlock.release()
	        
	wrapper.__name__ = func.__name__
	wrapper.__dict__ = func.__dict__
	wrapper.__doc__ = func.__doc__
	return wrapper


class NativeTranslator(object):
    
    def __init__(self, scriptPath, defaultLanguage=None, *args, **kwargs):
        import xbmcaddon
        self.addon = xbmcaddon.Addon('script.mbox')
        
    def get(self, id):
        """
        Alias for getLocalizedString(...)

        @param id: translation id
        @type id: int
        @return: translated text
        @rtype: unicode
        """
        # if id is a string, assume no need to lookup translation
        if isinstance(id, basestring):
            return id
        else:
            return self.addon.getLocalizedString(id)
     
    def toList(self, someMap):
        """
        @param someMap: dict with translation ids as values. Keys are ignored
        @return: list of strings containing translations
        """
        result = []
        for key in someMap.keys():
            result.append(self.get(someMap[key]))
        return result
    


import threading
import thread



class Mutex(threading.Thread):
	def __init__(self, condition):
		threading.Thread.__init__(self)
		self.condition = condition

		self.mutex = thread.allocate_lock()
		#self.mutex = threading.RLock()
		#self.notify = threading.Condition()

	def lock(self):
		print '[%s():%s]mutex_lock'% (currentframe().f_code.co_name, currentframe().f_lineno)
		self.mutex.acquire()
		#self.notify.acquire()

	def noti(self):
		print '[%s():%s]mutex_notify'% (currentframe().f_code.co_name, currentframe().f_lineno)
		self.notify.notify()

	def unlock(self):
		print '[%s():%s]mutex_unlock'% (currentframe().f_code.co_name, currentframe().f_lineno)

#		if self.mutex.locked():
		self.mutex.release()

		#self.notify.release()


def epgInfoTime(timeZone, startTime, duration):
	
	localOffset = 0
	if (is_digit(timeZone) == True):
		localOffset = int(timeZone)

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

def epgInfoClock(flag, nowTime, epgClock):
	pastTime = time.time() - nowTime

	strClock = []
	stbClock = int(epgClock) + pastTime

	if flag == 1:
		strClock.append( time.strftime('%a, %d.%m.%Y', time.gmtime(stbClock) ) )
		if int(pastTime) % 2 == 0:
			strClock.append( time.strftime('%H:%M', time.gmtime(stbClock) ) )
		else:
			strClock.append( time.strftime('%H %M', time.gmtime(stbClock) ) )

	elif flag == 2:
		strClock.append( time.strftime('%a. %H:%M', time.gmtime(stbClock) ) )

	elif flag == 3:
		strClock.append( time.strftime('%H:%M:%S', time.gmtime(stbClock) ) )


	print 'epgClock[%s:%s]'% (strClock, time.strftime('%S', time.gmtime(stbClock)) )
	return strClock

def epgInfoComponentImage(component):
	print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
	from elisenum import ElisEnum
	tmpcom = component[0]
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

