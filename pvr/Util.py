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

gSettings = xbmcaddon.Addon(id="script.mbox")

gLogOut = 0
gThreads = odict()

E_LOG_NORMAL = 0
E_LOG_WARN   = 37
E_LOG_ERR    = 31
E_LOG_DEBUG  = 33

E_AW_DD_MM_YYYY			= 0

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
	MLOG( E_LOG_DEBUG, msg )


def LOG_ERR( msg ):
	MLOG( E_LOG_ERR, msg )


def LOG_WARN( msg ):
	MLOG( E_LOG_WARN, msg )


def MLOG( level=0, msg=None ) :
	curframe = inspect.currentframe()
	calframe = inspect.getouterframes(curframe, 2)
	filePath = calframe[2][1]


	filename = os.path.basename( filePath )
	lineno   = calframe[2][2]
	filefunc = calframe[2][3]

	#if level >= 0 and level <= 18 :
	if level == 0 or level == E_LOG_DEBUG or gLogOut == 0 :
		print '[%s() %s:%s]%s'% (filefunc, filename, lineno, msg)

	else :
		print '\033[1;%sm[%s() %s:%s]%s\033[1;m'% (level, filefunc, filename, lineno, msg)



def LOG_INIT( ):
	
	#mbox.ini -- path : xbmc_root / script.mbox / mbox.ini
	import re, xbmcaddon, shutil
	rd=0
	#self.fd=0
	#inifile = 'mbox.ini'
	logpath = ''
	logfile = ''
	logmode = ''
	inifile = ''
	scriptDir = xbmcaddon.Addon('script.mbox').getAddonInfo('path')

	try:
		inifile = os.path.join(scriptDir, 'mbox.ini')

		rd = open( inifile, 'r' )
		for line in rd.readlines() :
			ret   = re.sub( '\n', '', line )
			value = re.split( '=', ret )
			if value[0] == 'log_path' :
				logpath = value[1]
			elif value[0] == 'log_file' :
				logfile = value[1]
			elif value[0] == 'log_mode' :
				logmode = value[1]

		print 'inifile[%s] logmod[%s] logfile[%s] rd[%s]'% (inifile, logmode, logfile, rd )

	except Exception, e:
		print 'exception[%s]'% e
		logmode = 'stdout'
		logfile = os.path.join(scriptDir, 'default.log')
		print 'inifile[%s] logmod[%s] logfile[%s] rd[%s]'% (inifile, logmode, logfile, rd )


	"""
	TODO : make logfile for user
	if log_mode == 'stdout' :
		#default : redirect to standard out

		#sys.stdout = self.f = StringIO.StringIO()
		pass

	else :

		#backup
		if os.path.isfile(logfile) :
			backup = logfile + '.bak'
			shutil.copyfile(logfile, backup)

		#log open
		try :
			self.fd = open( logfile, 'w+' )
		except Exception, e :
			print 'Err[%s] logfile[%s]'% ( e, logfile )
	"""

def GetSetting( aID ) :
	global gSettings
	LOG_TRACE('')
	return gSettings.getSetting( aID )


def SetSetting( aID, aValue ) :
	global gSettings	
	gSettings.setSetting( aID, aValue )


def TimeToString( aTime, aFlag=0 ) :
	if aFlag == E_AW_DD_MM_YYYY :
		return time.strftime("%a, %d.%m.%Y", time.gmtime( aTime ) )
	else :
		strTime = time.strftime('%a, %d.%m.%Y', aTime )
		LOG_TRACE('strTime=%s' %strTime )
		return strTime

