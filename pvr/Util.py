import os
import sys
import time
import xbmcgui

from decorator import decorator
from odict import odict
from threading import RLock

from inspect import currentframe
import inspect


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




def LOG_TRACE( msg ):
	curframe = inspect.currentframe()
	calframe = inspect.getouterframes(curframe, 2)
	print 'calframe=%s' %calframe
	filePath = calframe[1][1]
	loc = filePath.rfind('\\')

	if loc < 0 :
		loc = filePath.rfind('/')

	if loc < 0 :
		loc= 0
	else :
		loc += 1

	fileName = filePath[loc:]
		
	print 'DEBUG %8d : %s( %s ) -> %s ' %( calframe[1][2], fileName, calframe[1][3], msg )



def LOG_ERR( msg ):
	curframe = inspect.currentframe()
	calframe = inspect.getouterframes(curframe, 2)
	print 'calframe=%s' %calframe
	filePath = calframe[1][1]
	loc = filePath.rfind('\\')

	if loc < 0 :
		loc = filePath.rfind('/')

	if loc < 0 :
		loc= 0
	else :
		loc += 1

	fileName = filePath[loc:]
		
	print 'DEBUG %8d : %s( %s ) -> %s ' %( calframe[1][2], fileName, calframe[1][3], msg )

def LOG_WARN( msg ):
	curframe = inspect.currentframe()
	calframe = inspect.getouterframes(curframe, 2)
	print 'calframe=%s' %calframe
	filePath = calframe[1][1]
	loc = filePath.rfind('\\')

	if loc < 0 :
		loc = filePath.rfind('/')

	if loc < 0 :
		loc= 0
	else :
		loc += 1

	fileName = filePath[loc:]
		
	print 'DEBUG %8d : %s( %s ) -> %s ' %( calframe[1][2], fileName, calframe[1][3], msg )

