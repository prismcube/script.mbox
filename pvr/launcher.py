import os
import sys
import xbmc
import xbmcgui
import xbmcaddon
import time

from inspect import currentframe
from pvr.bus import EventBus
import pvr.elismgr
import pvr.gui.windowmgr as windowmgr
from pvr.util import run_async, hasPendingWorkers, waitForWorkersToDie
from pvr.elistest import ElisTest
import pvr.net.netconfig as netconfig

		
__launcher = None

def getInstance():
	global __launcher
	if not __launcher:
		__launcher = Launcher()
	return __launcher

class Launcher(object):

	def __init__(self):
		self.isFailed = False
		self.status = 'Init'
		self.shutdownReceived = False
		self.shutdowning = False		

	def run(self):
		try:
			try:
				time.sleep(1)
				#self.bootstrapSettings()
				self.initElisMgr()
				self.doElisTest()				
				self.initWindowMgr()
				self.waitShutdown()
			except Exception, ex:
				if not self.isFailed:
					self.failure(ex)
		finally:
			print 'Launcher end'

	def failure(self, cause):
		msg = 'Status:%s - Error: %s' % (self.status, cause)
		print 'lael98 log %s' %msg
		xbmcgui.Dialog().ok('Error', 'Status: %s' % self.status, 'Exception: %s' % str(cause))

	def initElisMgr(self):
		self.stage = 'Init ElisMgr'
		pvr.elismgr.getInstance().run()
		print 'test lael98'
		self.commander = pvr.elismgr.getInstance().getCommander()
		self.commander.setElisReady(netconfig.myIp)


	def initWindowMgr(self):
		pvr.gui.windowmgr.getInstance().showWindow( windowmgr.WIN_ID_NULLWINDOW )


	def powerOff( self ) :
		self.shutdown()
		xbmc.executebuiltin('xbmc.Quit')


	def shutdown(self):
		print '------------->shut down %d' %self.shutdowning
		if not self.shutdowning:
			self.shutdowning = True
			print '------------->shut shutdowning=%d abortRequested=%d' %(self.shutdowning,xbmc.abortRequested)
			
			pvr.elismgr.getInstance().shutdown()

			if hasPendingWorkers():
				waitForWorkersToDie(10.0) # in seconds
			
			print '------------->shut do end'
		print '<-------------shut down'

	def waitShutdown(self):
		cnt = 0
		print '<-------------> wait shutdown'		
		while not xbmc.abortRequested :
			time.sleep(1)
			cnt += 1

		print '<-------------> wait before shutdown'
		self.shutdown()
		print '<-------------> wait after shutdown'		

	def doElisTest(self):
		test = ElisTest()
		test.testAll()

	def bootstrapSettings(self):
		self.stage = 'Initializing Settings'
		self.platform = None
		self.bootstrapPlatform()

		from pvr.util import NativeTranslator
		import pvr.msg as m
		self.translator = NativeTranslator(self.platform.getScriptDir())
		print 'translator[%s]'% self.translator.get(m.LOCALIZE_TEST)

	def bootstrapPlatform(self):
		self.stage = 'Initializing Platform'
		import pvr.platform
		self.platform = pvr.platform.getPlatform()
		self.platform.addLibsToSysPath()
		sys.setcheckinterval(0)
		cacheDir = self.platform.getCacheDir()
		from pvr.util import requireDir
		requireDir(cacheDir)
		
		print 'MBox %s Initialized' % self.platform.addonVersion()

