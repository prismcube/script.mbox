import xbmc
import xbmcgui
import sys
import time
import os
import shutil
import weakref

from pvr.gui.GuiConfig import *
from gui.BaseWindow import BaseWindow
from inspect import currentframe
from elementtree import ElementTree
from util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR
import pvr.Platform
import pvr.DataCacheMgr
from pvr.XBMCInterface import XBMC_GetCurrentSkinName, XBMC_GetResolution, XBMC_GetSkinZoom
from pvr.Util import SetLock, SetLock2
import pvr.gui.DialogMgr as DiaMgr

WIN_ID_ROOTWINDOW 					= 0
WIN_ID_NULLWINDOW 					= 1
WIN_ID_MAINMENU 					= 2
WIN_ID_CHANNEL_LIST_WINDOW			= 3
WIN_ID_LIVE_PLATE					= 4
WIN_ID_CONFIGURE					= 5
WIN_ID_ANTENNA_SETUP				= 6
WIN_ID_TUNER_CONFIGURATION			= 7
WIN_ID_CONFIG_SIMPLE				= 8
WIN_ID_CONFIG_MOTORIZED_12			= 9
WIN_ID_CONFIG_MOTORIZED_USALS		= 10
WIN_ID_CONFIG_ONECABLE				= 12
WIN_ID_CONFIG_ONECABLE_2			= 13
WIN_ID_CONFIG_DISEQC_10				= 14
WIN_ID_CONFIG_DISEQC_11				= 15
WIN_ID_CHANNEL_SEARCH				= 16
WIN_ID_AUTOMATIC_SCAN				= 17
WIN_ID_MANUAL_SCAN					= 18
WIN_ID_TIMESHIFT_PLATE				= 19
WIN_ID_CHANNEL_EDIT_WINDOW			= 20
WIN_ID_EDIT_SATELLITE				= 21
WIN_ID_EDIT_TRANSPONDER				= 22
WIN_ID_ARCHIVE_WINDOW				= 23
WIN_ID_SYSTEM_INFO					= 24
WIN_ID_INSTALLATION					= 25
WIN_ID_MEDIACENTER					= 26
WIN_ID_EPG_WINDOW					= 27
WIN_ID_CONDITIONAL_ACCESS			= 28
WIN_ID_FIRST_INSTALLATION			= 29
WIN_ID_TIMER_WINDOW					= 30
WIN_ID_INFO_PLATE					= 31
#WIN_ID_FAVORITE_ADDONS				= 32
WIN_ID_FAVORITES					= 32
WIN_ID_SYSTEM_UPDATE				= 33
WIN_ID_HELP							= 34



WIN_ID_HIDDEN_TEST					= 99

WIN_ID_TIMESHIFT_INFO_PLATE			= 101
WIN_ID_TIMESHIFT_INFO_PLATE1		= 102
WIN_ID_TIMESHIFT_INFO_PLATE2		= 103

gWindowMgr = None

import sys
import os
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

def GetInstance( ) :
	global gWindowMgr
	if not gWindowMgr :
		print 'Create instance'
		gWindowMgr = WindowMgr( )
	else :
		pass

	return gWindowMgr


class WindowMgr( object ) :
	def __init__( self ) :
		#print 'check %d %s' %( currentframe().f_lineno, currentframe().f_code.co_filename )

		self.mScriptDir = pvr.Platform.GetPlatform( ).GetScriptDir( )
		print 'scriptDir= %s' %self.mScriptDir

		self.mDefaultLanguage = xbmc.getLanguage( )
		self.mSkinName = XBMC_GetCurrentSkinName( )
		
		self.mLastId			= -1
		self.mSkinFontPath		= []
		self.mScriptFontPath	= []
		self.mSkinDir			= []
		self.mListDir			= []
		self.mWindows			= {}
		self.mRootWindow		= None
		self.LoadSkinPosition( )

		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.mCommander.Player_SetVIdeoSize( 0, 0, 1280, 720 )

		self.AddDefaultFont( )		
		self.CopyIncludeFile( )

		self.RootWindow( )
		
		self.CreateAllWindows( )

		DiaMgr.GetInstance( )


	def GetCurrentWindow( self ) :
		return weakref.proxy( self.mWindows[self.mLastId] )


	def GetWindow( self, aWindowId ) :
		LOG_TRACE( 'GetWindow ID=%d' % aWindowId )
		try :
			return weakref.proxy( self.mWindows[aWindowId] )
		except Exception, ex :
			LOG_ERR( 'Exception %s' % ex )
			return None


	def GetLastWindowID( self ) :
		return self.mLastId


	def ShowRootWindow( self ) :
		LOG_TRACE( '------------------------ START ROOT WINDOW --------------------------' )	
		self.mLastId = WIN_ID_NULLWINDOW		
		self.mRootWindow.doModal( )
		LOG_TRACE( '------------------------ END ROOT WINDOW --------------------------' )	


	def ShowWindow( self, aWindowId, aParentId=0 ) :
		try :
			if aWindowId <= 0 :
				LOG_ERR( 'Invalid Window ID=%d' %aWindowId )
				return
				
			currentId = self.mLastId
			
			if currentId > 0 :
				LOG_TRACE( 'LastWindow=%s' %self.mWindows[currentId].GetName( ) )		
				if aParentId == 0 :
					self.mWindows[aWindowId].SetParentID( currentId )
				elif aParentId > 0 :
					self.mWindows[aWindowId].SetParentID( aParentId )				
				else :
					LOG_ERR( 'Invalid Parent Window ID=%d' %aParentId )
					self.mWindows[aWindowId].SetParentID( WIN_ID_NULLWINDOW )
				SetLock2( True )
				self.mLastId = aWindowId
				SetLock2( False )


				if E_SUPPORT_SINGLE_WINDOW_MODE == True :
					LOG_TRACE( 'CurrentWindow=%d' %(self.mLastId * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID ) )
					self.mRootWindow.setProperty( 'CurrentWindow', '%d' %(self.mLastId * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID ) )
					self.mWindows[aWindowId].onInit( )				
				else :
					self.mWindows[self.mLastId].ClearRelayAction( )
					self.mWindows[currentId].close( )
					self.mWindows[currentId].SetActivate( False )
					if E_WINDOW_ATIVATE_MODE == E_MODE_DOMODAL :					
						xbmc.executebuiltin('xbmc.Action(dvbres21)')				

			else :
				LOG_ERR( 'Has no valid last window id=%d' %self.mLastId )

			LOG_ERR( 'ShowWindow ID=%s' %self.mWindows[aWindowId].GetName( ) )
			#self.mLastId = aWindowId
			#self.mWindows[aWindowId].doModal( )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )
			self.mLastId = WIN_ID_NULLWINDOW


	def CloseWindow( self ) :
		try :
			currentId = self.mLastId
			if currentId  > 0 :
				parentId = self.mWindows[currentId].GetParentID( )			
				LOG_ERR( 'LastWindow=%s' %self.mWindows[currentId].GetName( ) )		
				if parentId > 0 :
					LOG_ERR( 'ShowWindow=%s' %self.mWindows[parentId].GetName( ) )
					SetLock2( True )					
					self.mLastId = parentId					
					SetLock2( False )

					if E_SUPPORT_SINGLE_WINDOW_MODE == True :					
						LOG_TRACE( 'CurrentWindow=%d' %(self.mLastId * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID ) )
						self.mRootWindow.setProperty( 'CurrentWindow', '%d' %(self.mLastId * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID ) )
						self.mWindows[currentId].onInit( )									
					else :
						self.mWindows[currentId].close( )
						self.mWindows[currentId].SetActivate( False )
						if E_WINDOW_ATIVATE_MODE == E_MODE_DOMODAL :										
							xbmc.executebuiltin('xbmc.Action(dvbres21)')
					
					#self.mWindows[parentId].doModal( )
				else :				
					LOG_ERR( 'ShowWindow=%s' %self.mWindows[WIN_ID_NULLWINDOW].GetName( ) )	
					self.mLastId = WIN_ID_NULLWINDOW

					if E_SUPPORT_SINGLE_WINDOW_MODE == True :					
						LOG_TRACE( 'CurrentWindow=%d' %(self.mLastId * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID ) )
						self.mRootWindow.setProperty( 'CurrentWindow', '%d' %(self.mLastId * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID ) )
						self.mWindows[aWindowId].onInit( )									
					
					#self.mWindows[WIN_ID_NULLWINDOW].doModal( )	

			else :
				LOG_ERR( 'Invaild Window ID=%d' %currentId )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )
			self.mLastId = WIN_ID_NULLWINDOW


	def RootWindow( self ) :
		from pvr.gui.windows.RootWindow import RootWindow
		if E_SUPPORT_SINGLE_WINDOW_MODE == True :
			self.mRootWindow = RootWindow( 'SingleRootWindow.xml', self.mScriptDir )
		else :
			self.mRootWindow = RootWindow( 'RootWindow.xml', self.mScriptDir )		


	def CreateAllWindows( self ) :
		LOG_TRACE( 'Create All Windows mScriptDir=%s' %self.mScriptDir )
		try:
			
			"""
			for attr, val in self.mWindows[WIN_ID_NULLWINDOW].__dict__.items( ) :
				LOG_TRACE('NAME=%s type=%s' %(attr, type(val) ) )
			
			import inspect
			for member in inspect.getmembers( self.mWindows[WIN_ID_NULLWINDOW] ) :
				LOG_TRACE( 'member=%s' %member[0] )
			"""
			from pvr.gui.windows.NullWindow import NullWindow
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_NULLWINDOW] = NullWindow( self.mRootWindow )
			else :
				self.mWindows[WIN_ID_NULLWINDOW] = NullWindow( 'NullWindow.xml', self.mScriptDir )

				
			LOG_ERR( '---------------- self.mWindows[WIN_ID_NULLWINDOW] id=%s' %self.mWindows[WIN_ID_NULLWINDOW] )

			from pvr.gui.windows.MainMenu import MainMenu
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_MAINMENU] = MainMenu( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_MAINMENU]=MainMenu( 'MainMenu.xml', self.mScriptDir )

			from pvr.gui.windows.ChannelListWindow import ChannelListWindow
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_CHANNEL_LIST_WINDOW] = ChannelListWindow( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_CHANNEL_LIST_WINDOW]=ChannelListWindow( 'ChannelListWindow.xml', self.mScriptDir )

			from pvr.gui.windows.LivePlate import LivePlate
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_LIVE_PLATE] = LivePlate( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_LIVE_PLATE]=LivePlate( 'LivePlate.xml', self.mScriptDir )

			from pvr.gui.windows.TimeshiftPlate import TimeShiftPlate
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_TIMESHIFT_PLATE] = TimeShiftPlate( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_TIMESHIFT_PLATE]=TimeShiftPlate( 'TimeshiftPlate.xml', self.mScriptDir )

			from pvr.gui.windows.Configure import Configure	
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_CONFIGURE] = Configure( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_CONFIGURE]=Configure( 'Configure.xml', self.mScriptDir )
			
			from pvr.gui.windows.Installation import Installation	
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_INSTALLATION] = Installation( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_INSTALLATION]=Installation( 'Installation.xml', self.mScriptDir )
			
			from pvr.gui.windows.AntennaSetup import AntennaSetup
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_ANTENNA_SETUP] = AntennaSetup( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_ANTENNA_SETUP]=AntennaSetup( 'AntennaSetup.xml', self.mScriptDir )
			
			from pvr.gui.windows.TunerConfiguration import TunerConfiguration
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_TUNER_CONFIGURATION] = TunerConfiguration( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_TUNER_CONFIGURATION]=TunerConfiguration( 'TunerConfiguration.xml', self.mScriptDir )
			
			from pvr.gui.windows.SatelliteConfigSimple import SatelliteConfigSimple
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_CONFIG_SIMPLE] = SatelliteConfigSimple( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_CONFIG_SIMPLE]=SatelliteConfigSimple( 'SatelliteConfigSimple.xml', self.mScriptDir )
			
			from pvr.gui.windows.SatelliteConfigMotorizedUsals import SatelliteConfigMotorizedUsals
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_CONFIG_MOTORIZED_USALS] = SatelliteConfigMotorizedUsals( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_CONFIG_MOTORIZED_USALS]=SatelliteConfigMotorizedUsals( 'SatelliteConfigMotorizedUsals.xml', self.mScriptDir )
			
			from pvr.gui.windows.SatelliteConfigMotorized12 import SatelliteConfigMotorized12
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_CONFIG_MOTORIZED_12] = SatelliteConfigMotorized12( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_CONFIG_MOTORIZED_12]=SatelliteConfigMotorized12( 'SatelliteConfigMotorized12.xml', self.mScriptDir )

			from pvr.gui.windows.SatelliteConfigOnecable import SatelliteConfigOnecable
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_CONFIG_ONECABLE] = SatelliteConfigOnecable( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_CONFIG_ONECABLE]=SatelliteConfigOnecable( 'SatelliteConfigOnecable.xml', self.mScriptDir )
			
			from pvr.gui.windows.SatelliteConfigOnecable2 import SatelliteConfigOnecable2
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_CONFIG_ONECABLE_2] = SatelliteConfigOnecable2( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_CONFIG_ONECABLE_2]=SatelliteConfigOnecable2( 'SatelliteConfigOnecable2.xml', self.mScriptDir )
			
			from pvr.gui.windows.SatelliteConfigDisEqc10 import SatelliteConfigDisEqC10
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_CONFIG_DISEQC_10] = SatelliteConfigDisEqC10( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_CONFIG_DISEQC_10]=SatelliteConfigDisEqC10( 'SatelliteConfigDisEqC10.xml', self.mScriptDir )
			
			from pvr.gui.windows.SatelliteConfigDisEqc11 import SatelliteConfigDisEqC11
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_CONFIG_DISEQC_11] = SatelliteConfigDisEqC11( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_CONFIG_DISEQC_11]=SatelliteConfigDisEqC11( 'SatelliteConfigDisEqC11.xml', self.mScriptDir )
			
			from pvr.gui.windows.ChannelSearch import ChannelSearch
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_CHANNEL_SEARCH] = ChannelSearch( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_CHANNEL_SEARCH]=ChannelSearch( 'ChannelSearch.xml', self.mScriptDir )
			
			from pvr.gui.windows.AutomaticScan import AutomaticScan	
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_AUTOMATIC_SCAN] = AutomaticScan( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_AUTOMATIC_SCAN]=AutomaticScan( 'AutomaticScan.xml', self.mScriptDir )
			
			from pvr.gui.windows.ManualScan import ManualScan
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_MANUAL_SCAN] = ManualScan( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_MANUAL_SCAN]=ManualScan( 'ManualScan.xml', self.mScriptDir )
			
			from pvr.gui.windows.EditSatellite import EditSatellite
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_EDIT_SATELLITE] = EditSatellite( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_EDIT_SATELLITE]=EditSatellite( 'EditSatellite.xml', self.mScriptDir )
			
			from pvr.gui.windows.EditTransponder import EditTransponder
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_EDIT_TRANSPONDER] = EditTransponder( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_EDIT_TRANSPONDER]=EditTransponder( 'EditTransponder.xml', self.mScriptDir )

			"""
			#from pvr.gui.windows.channeleditwindow import ChannelEditWindow
			#ChannelEditWindow( 'channeleditwindow.xml', self.mScriptDir )
			"""

			from pvr.gui.windows.SystemInfo import SystemInfo
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_SYSTEM_INFO] = SystemInfo( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_SYSTEM_INFO]=SystemInfo( 'SystemInfo.xml', self.mScriptDir )
			
			from pvr.gui.windows.ArchiveWindow import ArchiveWindow
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_ARCHIVE_WINDOW] = ArchiveWindow( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_ARCHIVE_WINDOW]=ArchiveWindow( 'ArchiveWindow.xml', self.mScriptDir )
			
			from pvr.gui.windows.EPGWindow import EPGWindow
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_EPG_WINDOW] = EPGWindow( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_EPG_WINDOW]=EPGWindow( 'EPGWindow.xml', self.mScriptDir )
			
			from pvr.gui.windows.MediaCenter import MediaCenter
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_MEDIACENTER] = MediaCenter( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_MEDIACENTER]=MediaCenter( 'MediaCenter.xml', self.mScriptDir )

			from pvr.gui.windows.ConditionalAccess import ConditionalAccess
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_CONDITIONAL_ACCESS] = ConditionalAccess( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_CONDITIONAL_ACCESS]=ConditionalAccess( 'ConditionalAccess.xml', self.mScriptDir ) 

			from pvr.gui.windows.FirstInstallation import FirstInstallation
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_FIRST_INSTALLATION] = FirstInstallation( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_FIRST_INSTALLATION]=FirstInstallation( 'FirstInstallation.xml', self.mScriptDir )

			from pvr.gui.windows.TimerWindow import TimerWindow
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_TIMER_WINDOW] = TimerWindow( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_TIMER_WINDOW]=TimerWindow( 'TimerWindow.xml', self.mScriptDir )

			from pvr.gui.windows.InfoPlate import InfoPlate
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_INFO_PLATE] = InfoPlate( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_INFO_PLATE]=InfoPlate( 'LivePlate.xml', self.mScriptDir )

			"""
			from pvr.gui.windows.FavoriteAddons import FavoriteAddons
			self.mWindows[WIN_ID_FAVORITE_ADDONS]=FavoriteAddons( 'FavoriteAddons.xml', self.mScriptDir )
			"""
			
			from pvr.gui.windows.Favorites import Favorites
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_FAVORITES] = Favorites( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_FAVORITES]=Favorites( 'Favorites.xml', self.mScriptDir )
			

			from pvr.gui.windows.Help import Help
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_HELP] = Help( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_HELP]=Help( 'Help.xml', self.mScriptDir )
			
			from pvr.gui.windows.SystemUpdate import SystemUpdate
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_SYSTEM_UPDATE] = SystemUpdate( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_SYSTEM_UPDATE]=SystemUpdate( 'SystemUpdate.xml', self.mScriptDir )

			from pvr.HiddenTest import HiddenTest
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.mWindows[WIN_ID_HIDDEN_TEST] = HiddenTest( self.mRootWindow  )
			else :
				self.mWindows[WIN_ID_HIDDEN_TEST]=HiddenTest( 'HiddenTest.xml', self.mScriptDir )


			"""
			#test
			from pvr.gui.windows.TimeshiftInfoPlate import TimeShiftInfoPlate
			self.mWindows[WIN_ID_TIMESHIFT_INFO_PLATE]=TimeShiftInfoPlate( 'TimeshiftInfoPlate.xml', self.mScriptDir )

			from pvr.gui.windows.TimeshiftInfoPlate1 import TimeShiftInfoPlate1
			self.mWindows[WIN_ID_TIMESHIFT_INFO_PLATE1]=TimeShiftInfoPlate1( 'TimeshiftInfoPlate1.xml', self.mScriptDir )

			from pvr.gui.windows.TimeshiftInfoPlate2 import TimeShiftInfoPlate2
			self.mWindows[WIN_ID_TIMESHIFT_INFO_PLATE2]=TimeShiftInfoPlate2( 'TimeshiftInfoPlate2.xml', self.mScriptDir )
			

			from pvr.gui.windows.test1 import Test1
			Test1('MyPics.xml', self.mScriptDir ).doModal( )
			"""

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def ResetAllWindows( self ) :
		#self.mWindows[ WIN_ID_MAINMENU ].close( )
		self.mWindows.clear( )
		self.CreateAllWindows( )


	def ReloadWindow( self, aWindowId = WIN_ID_LIVE_PLATE, aParentId = WIN_ID_NULLWINDOW ) :
		LOG_TRACE('-----------------------------last[%s] reload[%s]'% (self.mLastId, aWindowId) )

		if pvr.Platform.GetPlatform( ).IsPrismCube( ) :
			self.CopyIncludeFile( )
			xbmc.executebuiltin('XBMC.ReloadSkin()')		

		else :
			for id in self.mWindows :
				self.mWindows[id].close( )

			self.CheckSkinChange( )
			self.CopyIncludeFile( )
			self.AddDefaultFont( )		
			xbmc.executebuiltin('XBMC.ReloadSkin()')		
			self.ResetAllWindows( )
			#self.RootWindow( )
			self.ShowWindow( aWindowId, aParentId )


	def CheckGUISettings( self ) :
		self.LoadSkinPosition( )
		if self.CheckSkinChange( ) or self.CheckFontChange( ) :
			if not pvr.Platform.GetPlatform( ).IsPrismCube( ) :
				self.ReloadWindow( self.mLastId, WIN_ID_NULLWINDOW )
				LOG_TRACE( '----------------------- reload for platform[%s]'% pvr.Platform.GetPlatform( ).GetName( ) )
				return True

			self.CopyIncludeFile( )		
			self.AddDefaultFont( )
			pvr.DataCacheMgr.GetInstance( ).SetChannelReloadStatus( True )

			return True

		return False
			

	def CheckSkinChange( self ) :
	
		currentSkinName = XBMC_GetCurrentSkinName( )
		if self.mSkinName != currentSkinName :
			LOG_TRACE( 'change skin name' )
			self.mSkinName = currentSkinName
			return True

		return False


	def CheckFontChange( self ) :
		return False


	def LoadSkinPosition( self ) :
		if not pvr.Platform.GetPlatform( ).IsPrismCube( ) :
			return

		resInfo = XBMC_GetResolution( )
		skinzoom = XBMC_GetSkinZoom( )

		LOG_TRACE( 'resInfo=%s' %resInfo )
		LOG_TRACE( 'skinzoom=%s' %skinzoom )
		
		pvr.GuiHelper.GetInstanceSkinPosition( ).SetPosition( resInfo[0], resInfo[1], resInfo[2], resInfo[3],skinzoom)#( left, top, right, bottom, skinzoom )		


	def CopyIncludeFile( self ) :
		skinName = self.mSkinName
		print 'skinName=%s' %skinName

		self.mScriptDir = pvr.Platform.GetPlatform().GetScriptDir( )

		mboxInclude = 'mbox_includes.xml'

		if E_SUPPORT_SINGLE_WINDOW_MODE == True :
			mboxInclude = 'mbox_single_includes.xml'
		
		if skinName.lower() == 'default' or skinName.lower() == 'skin.confluence' :
			mboxIncludePath = os.path.join( pvr.Platform.GetPlatform().GetScriptDir( ), 'resources', 'skins', 'Default', '720p', mboxInclude )

		else : 
			mboxIncludePath = os.path.join( pvr.Platform.GetPlatform().GetScriptDir( ), 'resources', 'skins', skinName, '720p', mboxInclude )

			if not os.path.isfile( mboxIncludePath ) :
				mboxIncludePath = os.path.join( pvr.Platform.GetPlatform().GetScriptDir( ), 'resources', 'skins', 'Default', '720p', mboxInclude )			
			
		print 'mboxIncludePath=%s' %mboxIncludePath	

		skinIncludePath = os.path.join( pvr.Platform.GetPlatform().GetSkinDir( ), '720p', mboxInclude )
		print 'skinIncludePath=%s' %skinIncludePath	
		shutil.copyfile( mboxIncludePath, skinIncludePath )


	def GetSkinXMLPath( self ) :
		skinName = self.mSkinName
		print 'skinName=%s' %skinName
		
		scriptDir = pvr.Platform.GetPlatform().GetScriptDir( )
		
		if skinName.lower() == 'default' or skinName.lower() == 'skin.confluence' :
			skinXMLPath = os.path.join( pvr.Platform.GetPlatform().GetScriptDir( ), 'resources', 'skins', 'Default', '720p')
		
		else : 
			skinXMLPath = os.path.join( pvr.Platform.GetPlatform().GetScriptDir( ), 'resources', 'skins', skinName, '720p' )
		
		return skinXMLPath


	def AddDefaultFont( self ) :
		self.mSkinFontPath = xbmc.translatePath( "special://skin/fonts/" )
		self.mScriptFontPath = os.path.join( os.getcwd() , "resources" , "fonts" )
		self.mSkinDir = xbmc.translatePath( "special://skin/" )
		self.mListDir = os.listdir( self.mSkinDir )

		self.AddFont( "font35_title", "DejaVuSans-Bold.ttf", "35" )
		self.AddFont( "font12_title", "DejaVuSans-Bold.ttf", "16" )


	def GetFontsXML( self ) :

		fontPaths = []

		try:
			for subDir in self.mListDir :
				subDir = os.path.join( self.mSkinDir, subDir )
				
				if os.path.isdir( subDir ) :
					fontXml = os.path.join( subDir, "Font.xml" )
					
					if os.path.exists( fontXml ) :
						fontPaths.append( fontXml )

		except:
			print 'Err : GetFontsXML Error'
			return []

		return fontPaths


	def HasFontInstalled( self, aFontXMLPath, aFontName ) :
		name = "<name>%s</name>" % aFontName

		if not name in file( aFontXMLPath, "r" ).read( ) :
			print '%s font is not installed!' %aFontName
			return False
			
		else:
			print '%s font already installed!' %aFontName

		return True


	def AddFont( self, aFontName, aFileName, aSize, aStyle="", aAspect="" ) :

		try :
			needReloadSkin = False
			fontPaths = self.GetFontsXML( )

			if fontPaths:
				for fontXMLPath in fontPaths :
					if not self.HasFontInstalled( fontXMLPath, aFontName ) :
						tree = ElementTree.parse( fontXMLPath )
						root = tree.getroot( )

						for sets in root.getchildren( ) :
							sets.findall( "font" )[ -1 ].tail = "\n\t\t"
							new = ElementTree.SubElement( sets, "font" )
							new.text, new.tail = "\n\t\t\t", "\n\t"

							subNew1=ElementTree.SubElement( new, "name" )
							subNew1.text = aFontName
							subNew1.tail = "\n\t\t\t"
							subNew2=ElementTree.SubElement( new, "aFileName" )
							subNew2.text = ( aFileName, "Arial.ttf" )[ sets.attrib.get( "id" ) == "Arial" ]
							subNew2.tail = "\n\t\t\t"
							subNew3=ElementTree.SubElement( new, "size" )
							subNew3.text = aSize
							subNew3.tail = "\n\t\t\t"
							lastElement = subNew3

							if aStyle in [ "normal", "bold", "italics", "bolditalics" ] :
								subNew4=ElementTree.SubElement( new ,"style" )
								subNew4.text = aStyle
								subNew4.tail = "\n\t\t\t"
								lastElement = subNew4
							if aAspect :    
								subNew5=ElementTree.SubElement( new, "aspect" )
								subNew5.text = aAspect
								subNew5.tail = "\n\t\t\t"
								lastElement = subNew5
							needReloadSkin = True

							lastElement.tail = "\n\t\t"
						tree.write( fontXMLPath )
						needReloadSkin = True
		except :
			print 'Error AddFontErr'

		if needReloadSkin :
			if not os.path.exists( os.path.join( self.mSkinFontPath, aFileName ) ) and os.path.exists( os.path.join( self.mScriptFontPath, aFileName ) ):
				shutil.copyfile( os.path.join( self.mScriptFontPath, aFileName ), os.path.join( self.mSkinFontPath, aFileName ) )

			xbmc.executebuiltin( "XBMC.ReloadSkin()" )
			return True

		return False


	def GetLanguageList( self ) :
		#LOG_TRACE( 'lael98 language list #1 = %s' %xbmc.translatePath( 'special://skin/language' ) )
		#LOG_TRACE( 'lael98 language list #2 = %s' %xbmc.translatePath( 'special://xbmc/language/' ) )		
		#return os.listdir( xbmc.translatePath( 'special://skin/language' ) )
		languageList =  os.listdir( xbmc.translatePath( 'special://xbmc/language/' ) )
		languageList.sort()
		return languageList
		#self.mRecordList.sort( self.ByTitle )		


