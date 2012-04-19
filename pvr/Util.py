import os, sys, time
import xbmc
import xbmcgui
import xbmcaddon

from decorator import decorator
from odict import odict
from ElisEnum import ElisEnum

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


def GuiLock2( aEnable ):
	global gGuiLock
	if gGuiLock: # prevent nested locks / double lock
		return
	else:
		try:
			gGuiLock = aEnable
			xbmcgui.lock()
		finally:
			xbmcgui.unlock()
			gGuiLock = aEnable
		return


@decorator
def RunThread(func, *args, **kwargs):
	from threading import Thread
	worker = Thread(target = func, name=func.__name__, args = args, kwargs = kwargs)
	gThreads[worker.getName()] = worker
	worker.start()
	return worker


class TimeFormatEnum(object):
	E_AW_DD_MM_YYYY			= 0
	E_HH_MM					= 1
	E_DD_MM_YYYY_HH_MM		= 2
	E_DD_MM_YYYY			= 3
	E_AW_HH_MM				= 4
	E_HH_MM_SS				= 5
	E_WEEK_OF_DAY			= 6
	E_AW_DD_MON				= 7


def TimeToString( aTime, aFlag = 0 ) :
	strTime = ''
	if aFlag == TimeFormatEnum.E_AW_DD_MM_YYYY :
		strTime = time.strftime('%a, %d.%m.%Y', time.gmtime( aTime ) )
	elif aFlag == TimeFormatEnum.E_HH_MM :
		strTime = time.strftime('%H:%M', time.gmtime( aTime ) )
	elif aFlag == TimeFormatEnum.E_DD_MM_YYYY_HH_MM :
		strTime = time.strftime('%d.%m.%Y %H:%M', time.gmtime( aTime ) )
	elif aFlag == TimeFormatEnum.E_AW_DD_MM_YYYY :
		strTime = time.strftime('%a, %d.%m.%Y %H:%M', time.gmtime( aTime ) )
	elif aFlag == TimeFormatEnum.E_DD_MM_YYYY :
		strTime = time.strftime('%d.%m.%Y', time.gmtime( aTime ) )
	elif aFlag == TimeFormatEnum.E_AW_HH_MM :
		strTime = time.strftime('%a, %H:%M', time.gmtime( aTime ) )
	elif aFlag == TimeFormatEnum.E_HH_MM_SS :
		strTime = time.strftime('%H:%M:%S', time.gmtime( aTime ) )
	elif aFlag == TimeFormatEnum.E_WEEK_OF_DAY :
		strTime = time.strftime('%a', time.gmtime( aTime ) )
	elif aFlag == TimeFormatEnum.E_AW_DD_MON :
		strTime = time.strftime('%a. %d %b', time.gmtime( aTime ) )
	else :
		strTime = time.strftime('%a, %d.%m.%Y', aTime )
		#print 'strTime=%s' %strTime

	return strTime


