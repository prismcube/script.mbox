import xbmc
import xbmcgui
import sys
import time
import os
import shutil
import weakref

from pvr.gui.GuiConfig import *
from pvr.gui.BaseWindow import BaseWindow
from inspect import currentframe
from elisinterface.util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR
import pvr.Platform
import pvr.DataCacheMgr
from pvr.XBMCInterface import XBMC_GetCurrentSkinName, XBMC_GetResolution, XBMC_GetSkinZoom
from pvr.Util import SetLock, SetLock2
import pvr.gui.DialogMgr as DiaMgr
import pvr.ScanHelper as ScanHelper


try :
	import xml.etree.cElementTree as ElementTree
except Exception, e :
	from elementtree import ElementTree

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
WIN_ID_FAVORITES					= 32
WIN_ID_SYSTEM_UPDATE				= 33
WIN_ID_EPG_SEARCH					= 34
WIN_ID_ZOOM							= 35
WIN_ID_SIMPLE_CHANNEL_LIST			= 36
WIN_ID_FAST_SCAN					= 37
WIN_ID_PIP_WINDOW					= 38
WIN_ID_ADVANCED						= 39


WIN_ID_HIDDEN_TEST					= 99

WIN_ID_TIMESHIFT_INFO_PLATE			= 101
WIN_ID_TIMESHIFT_INFO_PLATE1		= 102
WIN_ID_TIMESHIFT_INFO_PLATE2		= 103

WIN_ID_LIST_WINDOW_SETTING_WINDOW = [
	WIN_ID_ANTENNA_SETUP, WIN_ID_CONFIG_SIMPLE, WIN_ID_CONFIG_MOTORIZED_12, WIN_ID_CONFIG_MOTORIZED_USALS,
	WIN_ID_CONFIG_ONECABLE, WIN_ID_CONFIG_ONECABLE_2, WIN_ID_CONFIG_DISEQC_10, WIN_ID_CONFIG_DISEQC_11,
	WIN_ID_CHANNEL_SEARCH, WIN_ID_AUTOMATIC_SCAN, WIN_ID_MANUAL_SCAN, WIN_ID_TUNER_CONFIGURATION,
	WIN_ID_EDIT_SATELLITE, WIN_ID_EDIT_TRANSPONDER, WIN_ID_CONDITIONAL_ACCESS, WIN_ID_SYSTEM_UPDATE,
	WIN_ID_FIRST_INSTALLATION, WIN_ID_INSTALLATION, WIN_ID_CONFIGURE, WIN_ID_ADVANCED ]

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
		#LOG_TRACE( 'GetWindow ID=%d' % aWindowId )
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

				LOG_TRACE( 'CurrentWindow=%d' % ( self.mLastId * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID ) )

				self.mRootWindow.setProperty( 'CurrentWindow', '%d' % ( self.mLastId * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID ) )
				#self.mWindows[WIN_ID_PIP_WINDOW].PIP_Check( )
				DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).PIP_Check( )
				self.mWindows[aWindowId].onInit( )

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

					LOG_TRACE( 'CurrentWindow=%d' % ( self.mLastId * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID ) )

					self.mRootWindow.setProperty( 'CurrentWindow', '%d' % ( self.mLastId * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID ) )
					DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).PIP_Check( )
					self.mWindows[parentId].onInit( )
					
				else :
					LOG_ERR( 'ShowWindow=%s' %self.mWindows[WIN_ID_NULLWINDOW].GetName( ) )	
					self.mLastId = WIN_ID_NULLWINDOW

					LOG_TRACE( 'CurrentWindow=%d' %(self.mLastId * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID ) )
					self.mRootWindow.setProperty( 'CurrentWindow', '%d' %(self.mLastId * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID ) )
					DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).PIP_Check( )
					self.mWindows[aWindowId].onInit( )
					
					#self.mWindows[WIN_ID_NULLWINDOW].doModal( )	

			else :
				LOG_ERR( 'Invaild Window ID=%d' %currentId )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )
			self.mLastId = WIN_ID_NULLWINDOW


	def RootWindow( self ) :
		from pvr.gui.windows.RootWindow import RootWindow
		self.mRootWindow = RootWindow( 'SingleRootWindow.xml', self.mScriptDir )


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
			from pvr.gui.windows.MainMenu import MainMenu
			from pvr.gui.windows.ChannelListWindow import ChannelListWindow
			from pvr.gui.windows.LivePlate import LivePlate
			from pvr.gui.windows.TimeShiftPlate import TimeShiftPlate
			from pvr.gui.windows.Configure import Configure
			from pvr.gui.windows.Installation import Installation
			from pvr.gui.windows.TunerConfiguration import TunerConfiguration
			from pvr.gui.windows.SatelliteConfigSimple import SatelliteConfigSimple
			from pvr.gui.windows.SatelliteConfigMotorizedUsals import SatelliteConfigMotorizedUsals
			from pvr.gui.windows.SatelliteConfigMotorized12 import SatelliteConfigMotorized12
			from pvr.gui.windows.SatelliteConfigMotorized12 import SatelliteConfigMotorized12
			from pvr.gui.windows.SatelliteConfigOnecable import SatelliteConfigOnecable
			from pvr.gui.windows.SatelliteConfigOnecable2 import SatelliteConfigOnecable2
			from pvr.gui.windows.SatelliteConfigDisEqC10 import SatelliteConfigDisEqC10
			from pvr.gui.windows.SatelliteConfigDisEqC11 import SatelliteConfigDisEqC11
			from pvr.gui.windows.ChannelSearch import ChannelSearch
			from pvr.gui.windows.AutomaticScan import AutomaticScan	
			from pvr.gui.windows.ManualScan import ManualScan
			from pvr.gui.windows.EditSatellite import EditSatellite
			from pvr.gui.windows.EditTransponder import EditTransponder
			from pvr.gui.windows.SystemInfo import SystemInfo
			from pvr.gui.windows.ArchiveWindow import ArchiveWindow
			from pvr.gui.windows.EPGWindow import EPGWindow
			from pvr.gui.windows.MediaCenter import MediaCenter
			from pvr.gui.windows.ConditionalAccess import ConditionalAccess
			from pvr.gui.windows.TimerWindow import TimerWindow
			from pvr.gui.windows.InfoPlate import InfoPlate
			from pvr.gui.windows.Favorites import Favorites
			from pvr.gui.windows.SystemUpdate import SystemUpdate
			from pvr.gui.windows.EPGSearchWindow import EPGSearchWindow
			from pvr.gui.windows.Zoom import Zoom
			from pvr.gui.windows.SimpleChannelList import SimpleChannelList
			from pvr.gui.windows.FastScan import FastScan
			from pvr.gui.windows.Advanced import Advanced
			from pvr.gui.windows.AntennaSetup import AntennaSetup
			from pvr.gui.windows.FirstInstallation import FirstInstallation
			#from pvr.gui.windows.PIPWindow import PIPWindow
			from pvr.HiddenTest import HiddenTest

			self.mWindows[WIN_ID_NULLWINDOW] = NullWindow( self.mRootWindow )
			LOG_ERR( '---------------- self.mWindows[WIN_ID_NULLWINDOW] id=%s' %self.mWindows[WIN_ID_NULLWINDOW] )
			self.mWindows[WIN_ID_MAINMENU] = MainMenu( self.mRootWindow )
			self.mWindows[WIN_ID_CHANNEL_LIST_WINDOW] = ChannelListWindow( self.mRootWindow )
			self.mWindows[WIN_ID_LIVE_PLATE] = LivePlate( self.mRootWindow )
			self.mWindows[WIN_ID_TIMESHIFT_PLATE] = TimeShiftPlate( self.mRootWindow )
			self.mWindows[WIN_ID_CONFIGURE] = Configure( self.mRootWindow )
			self.mWindows[WIN_ID_INSTALLATION] = Installation( self.mRootWindow )
			self.mWindows[WIN_ID_ANTENNA_SETUP] = AntennaSetup( self.mRootWindow )
			self.mWindows[WIN_ID_TUNER_CONFIGURATION] = TunerConfiguration( self.mRootWindow )
			self.mWindows[WIN_ID_CONFIG_SIMPLE] = SatelliteConfigSimple( self.mRootWindow )
			self.mWindows[WIN_ID_CONFIG_MOTORIZED_USALS] = SatelliteConfigMotorizedUsals( self.mRootWindow )
			self.mWindows[WIN_ID_CONFIG_MOTORIZED_12] = SatelliteConfigMotorized12( self.mRootWindow )
			self.mWindows[WIN_ID_CONFIG_ONECABLE] = SatelliteConfigOnecable( self.mRootWindow )
			self.mWindows[WIN_ID_CONFIG_ONECABLE_2] = SatelliteConfigOnecable2( self.mRootWindow )
			self.mWindows[WIN_ID_CONFIG_DISEQC_10] = SatelliteConfigDisEqC10( self.mRootWindow )
			self.mWindows[WIN_ID_CONFIG_DISEQC_11] = SatelliteConfigDisEqC11( self.mRootWindow )
			self.mWindows[WIN_ID_CHANNEL_SEARCH] = ChannelSearch( self.mRootWindow )
			self.mWindows[WIN_ID_AUTOMATIC_SCAN] = AutomaticScan( self.mRootWindow )
			self.mWindows[WIN_ID_MANUAL_SCAN] = ManualScan( self.mRootWindow )
			self.mWindows[WIN_ID_EDIT_SATELLITE] = EditSatellite( self.mRootWindow )
			self.mWindows[WIN_ID_EDIT_TRANSPONDER] = EditTransponder( self.mRootWindow )
			self.mWindows[WIN_ID_SYSTEM_INFO] = SystemInfo( self.mRootWindow )
			self.mWindows[WIN_ID_ARCHIVE_WINDOW] = ArchiveWindow( self.mRootWindow )
			self.mWindows[WIN_ID_EPG_WINDOW] = EPGWindow( self.mRootWindow )
			self.mWindows[WIN_ID_MEDIACENTER] = MediaCenter( self.mRootWindow )
			self.mWindows[WIN_ID_CONDITIONAL_ACCESS] = ConditionalAccess( self.mRootWindow )
			self.mWindows[WIN_ID_FIRST_INSTALLATION] = FirstInstallation( self.mRootWindow )
			self.mWindows[WIN_ID_TIMER_WINDOW] = TimerWindow( self.mRootWindow )
			self.mWindows[WIN_ID_INFO_PLATE] = InfoPlate( self.mRootWindow )
			self.mWindows[WIN_ID_FAVORITES] = Favorites( self.mRootWindow )
			self.mWindows[WIN_ID_SYSTEM_UPDATE] = SystemUpdate( self.mRootWindow )
			self.mWindows[WIN_ID_EPG_SEARCH] = EPGSearchWindow( self.mRootWindow )
			self.mWindows[WIN_ID_ZOOM] = Zoom( self.mRootWindow )
			self.mWindows[WIN_ID_SIMPLE_CHANNEL_LIST] = SimpleChannelList( self.mRootWindow )
			self.mWindows[WIN_ID_FAST_SCAN] = FastScan( self.mRootWindow  )
			#self.mWindows[WIN_ID_PIP_WINDOW] = PIPWindow( self.mRootWindow  )
			self.mWindows[WIN_ID_HIDDEN_TEST] = HiddenTest( self.mRootWindow )
			self.mWindows[WIN_ID_ADVANCED] = Advanced( self.mRootWindow )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		pvr.DataCacheMgr.GetInstance( ).SetRootWindow( self.mRootWindow )
		pvr.DataCacheMgr.GetInstance( ).SharedChannel_AddWindow( WIN_ID_SIMPLE_CHANNEL_LIST )
		pvr.DataCacheMgr.GetInstance( ).SharedChannel_AddWindow( WIN_ID_EPG_WINDOW )		
		
		ScanHelper.GetInstance( ).SetRootWindow( self.mRootWindow )


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
			self.GetWindow( WIN_ID_SIMPLE_CHANNEL_LIST ).ResetControls( )

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


