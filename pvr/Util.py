import os
import sys
import time
import xbmcgui
import xbmc
import xbmcaddon
import time

from decorator import decorator
from odict import odict
from threading import RLock

from inspect import currentframe
import inspect
from ElisEnum import ElisEnum

gThreads = odict()

E_LOG_NORMAL = 0
E_LOG_ERR    = 2
E_LOG_WARN   = 1
E_LOG_DEBUG  = 0
E_DEBUG_LEVEL = E_LOG_DEBUG

class TimeFormatEnum(object):
	E_AW_DD_MM_YYYY			= 0
	E_HH_MM					= 1
	E_DD_MM_YYYY_HH_MM		= 2
	E_DD_MM_YYYY			= 3
	E_AW_HH_MM				= 4
	E_HH_MM_SS				= 5
	E_WEEK_OF_DAY			= 6
	E_AW_DD_MON				= 7
	

def TimeToString( aTime, aFlag=0 ) :
	if aFlag == TimeFormatEnum.E_AW_DD_MM_YYYY :
		return time.strftime("%a, %d.%m.%Y", time.gmtime( aTime ) )
	elif aFlag == TimeFormatEnum.E_HH_MM :		
		return time.strftime("%02H:%02M", time.gmtime( aTime ) )	
	elif aFlag == TimeFormatEnum.E_DD_MM_YYYY_HH_MM :
		return time.strftime("%d.%m.%Y %H:%M", time.gmtime( aTime ) )		
	elif aFlag == TimeFormatEnum.E_AW_DD_MM_YYYY :
		return time.strftime("%a, %d.%m.%Y %H:%M", time.gmtime( aTime ) )		
	elif aFlag == TimeFormatEnum.E_DD_MM_YYYY :
		return time.strftime("%d.%m.%Y", time.gmtime( aTime ) )
	elif aFlag == TimeFormatEnum.E_AW_HH_MM :
		return time.strftime("%a, %H:%M", time.gmtime( aTime ) )
	elif aFlag == TimeFormatEnum.E_HH_MM_SS :
		return time.strftime("%H:%M:%S", time.gmtime( aTime ) )
	elif aFlag == TimeFormatEnum.E_WEEK_OF_DAY :
		return time.strftime("%a", time.gmtime( aTime ) )			
	elif aFlag == TimeFormatEnum.E_AW_DD_MON :
		return time.strftime("%a. %d %b", time.gmtime( aTime ) )			
	else :
		strTime = time.strftime('%a, %d.%m.%Y', aTime )
		LOG_TRACE('strTime=%s' %strTime )
		return strTime


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


"""
def LOG_TRACE( msg ):
	MLOG( E_LOG_DEBUG, msg )


def LOG_ERR( msg ):
	MLOG( E_LOG_ERR, msg )


def LOG_WARN( msg ):
	MLOG( E_LOG_WARN, msg )


def MLOG( level=0, msg=None ) :
	if E_DEBUG_LEVEL > level :
		return

	curframe = inspect.currentframe()
	calframe = inspect.getouterframes(curframe, 2)
	filePath = calframe[2][1]


	filename = os.path.basename( filePath )
	lineno   = calframe[2][2]
	filefunc = calframe[2][3]

	#if filename != 'ChannelListWindow.py' :
	#	return

	#if level >= 0 and level <= 18 :
	if gLogOut == 0 :
		print '[%s() %s:%s]%s'% (filefunc, filename, lineno, msg)

	else :
		color = 33 #black
		if level == E_LOG_ERR :
			color = 31 #red
		elif level == E_LOG_WARN :
			color = 37 #green ?
		print '\033[1;%sm[%s() %s:%s]%s\033[1;m'% (color, filefunc, filename, lineno, msg)

	del calframe
	del curframe
"""

