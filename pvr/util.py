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




