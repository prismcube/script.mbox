import os
import sys
import xbmc
import xbmcgui
import xbmcaddon
import time

import pvr.gui.DialogMgr as DiaMgr
from inspect import currentframe
import pvr.ElisMgr
import pvr.gui.WindowMgr as WindowMgr
from pvr.Util import RunThread, HasPendingThreads, WaitUtileThreadsJoin
import pvr.NetConfig as NetConfig

		
gLauncher = None

def GetInstance():
	global gLauncher
	if not gLauncher:
		gLauncher = Launcher()
	return gLauncher

class Launcher(object):

	def __init__(self):
		self.mShutdownReceived = False
		self.mShutdowning = False		

	def Run(self):
		try:
			try:
				time.sleep(1)
				self.InitElisMgr()
				self.DoElisTest()				
				self.InitWindowMgr()
				self.WaitShutdown()
			except Exception, ex:
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'Error', 'Exception: %s' % str( ex ) )
	 			dialog.doModal( )
		finally:
			print 'Launcher end'


	def InitElisMgr(self):
		pvr.ElisMgr.GetInstance().Run()
		print 'test lael98'
		self.mCommander = pvr.ElisMgr.GetInstance().GetCommander()
		self.mCommander.SetElisReady( NetConfig.myIp)



	def InitWindowMgr(self):
		pvr.gui.WindowMgr.GetInstance().ShowWindow( WindowMgr.WIN_ID_NULLWINDOW )


	def PowerOff( self ) :
		self.Shutdown()
		xbmc.executebuiltin('xbmc.Quit')


	def Shutdown(self):
		print '------------->shut down %d' %self.mShutdowning
		if not self.mShutdowning:
			self.mShutdowning = True
			print '------------->shut mShutdowning=%d abortRequested=%d' %(self.mShutdowning,xbmc.abortRequested)
			
			pvr.ElisMgr.GetInstance().Shutdown()

			if HasPendingThreads():
				WaitUtileThreadsJoin(10.0) # in seconds
			
			print '------------->shut do end'
		print '<-------------shut down'

	def WaitShutdown(self):
		cnt = 0
		print '<-------------> wait shutdown'		
		while not xbmc.abortRequested :
			time.sleep(1)
			cnt += 1

		print '<-------------> wait before shutdown'
		self.Shutdown()
		print '<-------------> wait after shutdown'		

	def DoElisTest(self):
		pass
		"""
		test = ElisTest()
		test.testAll()
		"""


