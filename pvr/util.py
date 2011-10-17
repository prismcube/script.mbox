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


