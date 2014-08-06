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
from elisinterface.util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR
import pvr.NetConfig as NetConfig
import pvr.DataCacheMgr
import pvr.GlobalEvent
import pvr.gui.GuiConfig as GuiConfig
from pvr.GuiHelper import *
from pvr.Product import *

import webinterface
import thread

gLauncher = None

def GetInstance( ):
	global gLauncher
	if not gLauncher:
		gLauncher = Launcher()
	return gLauncher

class Launcher( object ):

	def __init__( self ):
		self.mShutdownReceived = False
		self.mShutdowning = False
		self.mLoadCount = 0

	def Run( self ):
		try:
			try:
				time.sleep( 1 )
				self.InitElisMgr( )
				self.DoElisTest( )
				self.InitCacheMgr( )
				#if GuiConfig.E_SUPPROT_WEBINTERFACE == True :
				if GetSetting( 'WEB_INTERFACE' ) == 'true' :
					self.StartWebInterface( )

				self.InitWindowMgr( )
				self.WaitShutdown( )
			except Exception, ex:
				#dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				#dialog.SetDialogProperty( 'Error', 'Exception: %s' % str( ex ) )
				#dialog.doModal( )
				print 'Error exception[%s]'% ex
				import traceback
				LOG_ERR( 'traceback=%s' %traceback.format_exc() )

				self.mLoadCount += 1
				LOG_TRACE('==============>retry run[%s]'% self.mLoadCount)
				self.mShutdowning = False
				self.Shutdown( )
				time.sleep( 5 )
				self.Run( )
		finally:
			print 'Launcher end'


	def InitElisMgr( self ):
		pvr.ElisMgr.GetInstance( ).Run( )
		print 'test lael98'
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )


	def InitCacheMgr( self ) :
		pvr.DataCacheMgr.GetInstance( )


	def StartWebInterface( self ) :
		#if GuiConfig.E_SUPPROT_WEBINTERFACE == True :
		if GetSetting( 'WEB_INTERFACE' ) == 'true' :
			LOG_TRACE( 'Start Webinterface' )
			thread.start_new_thread( webinterface.index, () )
			thread.start_new_thread( webinterface.streamIndex, () )


	def InitWindowMgr( self ):
		if self.CheckFactoryTest( ) == True :
			strFactoryPath = '/mtmp/script.factorytest'
			#strFactoryPath = '/usr/share/xbmc/addons/script.factorytest'
			#strFactoryPath = '/home/root/.xbmc/addons/script.factorytest'
			print 'FactoryTest : strFactoryPath=%s' %strFactoryPath
			sys.path.append( strFactoryPath )
			sys.path.append(os.path.join( strFactoryPath, 'resources' ) )
			
			import FactoryTestMgr
			FactoryTestMgr.GetInstance( ).Start( strFactoryPath )
			
		else :
			pvr.ElisMgr.GetInstance( ).GetEventBus( ).Register( pvr.GlobalEvent.GetInstance() )		
			pvr.gui.WindowMgr.GetInstance( ).ShowRootWindow( )


	def PowerOff( self ) :
		self.Shutdown( )
		xbmc.executebuiltin( 'xbmc.Quit' )


	def Shutdown( self ):
		print '------------->shut down %d' %self.mShutdowning
		if not self.mShutdowning:
			self.mShutdowning = True
			print '------------->shut mShutdowning=%d abortRequested=%d' %( self.mShutdowning, xbmc.abortRequested )
			
			pvr.ElisMgr.GetInstance().Shutdown( )

			if HasPendingThreads( ):
				WaitUtileThreadsJoin( 10.0 ) # in seconds
			
			print '------------->shut do end'
		print '<-------------shut down'

	def WaitShutdown( self ):
		cnt = 0
		print '<-------------> wait shutdown'		
		while not xbmc.abortRequested :
			time.sleep( 1 )
			cnt += 1

		print '<-------------> wait before shutdown'
		self.Shutdown( )
		print '<-------------> wait after shutdown'		

	def DoElisTest( self ):
		pass
		"""
		test = ElisTest()
		test.testAll()
		"""

	def CheckFactoryTest( self ) :
		# ToDO
		#check from /var/
		ret = os.path.isfile('/mtmp/factorytest')
		return ret
		
