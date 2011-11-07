import os
import sys
import time
import xbmcgui

from decorator import decorator
from odict import odict
from threading import RLock


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


