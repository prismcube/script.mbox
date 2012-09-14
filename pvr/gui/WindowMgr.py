import xbmc
import xbmcgui
import sys
import time
import os
import shutil
import weakref


from gui.BaseWindow import BaseWindow
from inspect import currentframe
from elementtree import ElementTree
from util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR


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

WIN_ID_HIDDEN_TEST					= 99

WIN_ID_TIMESHIFT_INFO_PLATE			= 101
WIN_ID_TIMESHIFT_INFO_PLATE1		= 102
WIN_ID_TIMESHIFT_INFO_PLATE2		= 103

gWindowMgr = None

E_ADD_XBMC_HTTP_FUNCTION			= True


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

		import pvr.Platform 
		self.mScriptDir = pvr.Platform.GetPlatform( ).GetScriptDir( )
		print 'scriptDir= %s' %self.mScriptDir

		self.mDefaultLanguage = xbmc.getLanguage( )
		currentSkinName = xbmc.executehttpapi( "GetGUISetting(3, lookandfeel.skin)" )
		self.mSkinName = currentSkinName[4:]

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
				
			if self.mLastId > 0 :
				LOG_TRACE( 'LastWindow=%s' %self.mWindows[self.mLastId].GetName( ) )		
				if aParentId == 0 :
					self.mWindows[aWindowId].SetParentID( self.mLastId )
				elif aParentId > 0 :
					self.mWindows[aWindowId].SetParentID( aParentId )				
				else :
					LOG_ERR( 'Invalid Parent Window ID=%d' %aParentId )
					self.mWindows[aWindowId].SetParentID( WIN_ID_NULLWINDOW )
				self.mWindows[self.mLastId].close( )
			else :
				LOG_ERR( 'Has no valid last window id=%d' %self.mLastId )

			LOG_ERR( 'ShowWindow ID=%s' %self.mWindows[aWindowId].GetName( ) )
			self.mLastId = aWindowId
			#self.mWindows[aWindowId].doModal( )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )
			self.mLastId = 0


	def CloseWindow( self ) :
		try :
			if self.mLastId  > 0 :
				parentId = self.mWindows[self.mLastId].GetParentID( )			
				LOG_ERR( 'LastWindow=%s' %self.mWindows[self.mLastId].GetName( ) )		
				self.mWindows[self.mLastId].close( )
				if parentId > 0 :
					self.mLastId = parentId
					LOG_ERR( 'ShowWindow=%s' %self.mWindows[parentId].GetName( ) )									
					self.mWindows[parentId].doModal( )
				else :				
					LOG_ERR( 'ShowWindow=%s' %self.mWindows[WIN_ID_NULLWINDOW].GetName( ) )	
					self.mLastId = WIN_ID_NULLWINDOW					
					#self.mWindows[WIN_ID_NULLWINDOW].doModal( )	

			else :
				LOG_ERR( 'Invaild Window ID=%d' %self.mLastId )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )
			self.mLastId = 0
		

	def RootWindow( self ) :
		from pvr.gui.windows.RootWindow import RootWindow
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
			self.mWindows[WIN_ID_NULLWINDOW] = NullWindow( 'NullWindow.xml', self.mScriptDir )
			LOG_ERR( '---------------- self.mWindows[WIN_ID_NULLWINDOW] id=%s' %self.mWindows[WIN_ID_NULLWINDOW] )

			from pvr.gui.windows.MainMenu import MainMenu
			self.mWindows[WIN_ID_MAINMENU]=MainMenu( 'MainMenu.xml', self.mScriptDir )

			from pvr.gui.windows.ChannelListWindow import ChannelListWindow
			self.mWindows[WIN_ID_CHANNEL_LIST_WINDOW]=ChannelListWindow( 'ChannelListWindow.xml', self.mScriptDir )
			#ChannelListWindow('ChannelListWindow_b.xml', self.mScriptDir ).doModal()

			from pvr.gui.windows.LivePlate import LivePlate
			self.mWindows[WIN_ID_LIVE_PLATE]=LivePlate( 'LivePlate.xml', self.mScriptDir )

			from pvr.gui.windows.TimeshiftPlate import TimeShiftPlate
			self.mWindows[WIN_ID_TIMESHIFT_PLATE]=TimeShiftPlate( 'TimeshiftPlate.xml', self.mScriptDir )

			from pvr.gui.windows.Configure import Configure	
			self.mWindows[WIN_ID_CONFIGURE]=Configure( 'Configure.xml', self.mScriptDir )
			
			from pvr.gui.windows.Installation import Installation	
			self.mWindows[WIN_ID_INSTALLATION]=Installation( 'Installation.xml', self.mScriptDir )
			
			from pvr.gui.windows.AntennaSetup import AntennaSetup
			self.mWindows[WIN_ID_ANTENNA_SETUP]=AntennaSetup( 'AntennaSetup.xml', self.mScriptDir )
			
			from pvr.gui.windows.TunerConfiguration import TunerConfiguration
			self.mWindows[WIN_ID_TUNER_CONFIGURATION]=TunerConfiguration( 'TunerConfiguration.xml', self.mScriptDir )
			
			from pvr.gui.windows.SatelliteConfigSimple import SatelliteConfigSimple
			self.mWindows[WIN_ID_CONFIG_SIMPLE]=SatelliteConfigSimple( 'SatelliteConfigSimple.xml', self.mScriptDir )
			
			from pvr.gui.windows.SatelliteConfigMotorizedUsals import SatelliteConfigMotorizedUsals
			self.mWindows[WIN_ID_CONFIG_MOTORIZED_USALS]=SatelliteConfigMotorizedUsals( 'SatelliteConfigMotorizedUsals.xml', self.mScriptDir )
			
			from pvr.gui.windows.SatelliteConfigMotorized12 import SatelliteConfigMotorized12
			self.mWindows[WIN_ID_CONFIG_MOTORIZED_12]=SatelliteConfigMotorized12( 'SatelliteConfigMotorized12.xml', self.mScriptDir )

			from pvr.gui.windows.SatelliteConfigOnecable import SatelliteConfigOnecable
			self.mWindows[WIN_ID_CONFIG_ONECABLE]=SatelliteConfigOnecable( 'SatelliteConfigOnecable.xml', self.mScriptDir )
			
			from pvr.gui.windows.SatelliteConfigOnecable2 import SatelliteConfigOnecable2
			self.mWindows[WIN_ID_CONFIG_ONECABLE_2]=SatelliteConfigOnecable2( 'SatelliteConfigOnecable2.xml', self.mScriptDir )
			
			from pvr.gui.windows.SatelliteConfigDisEqc10 import SatelliteConfigDisEqC10
			self.mWindows[WIN_ID_CONFIG_DISEQC_10]=SatelliteConfigDisEqC10( 'SatelliteConfigDisEqC10.xml', self.mScriptDir )
			
			from pvr.gui.windows.SatelliteConfigDisEqc11 import SatelliteConfigDisEqC11
			self.mWindows[WIN_ID_CONFIG_DISEQC_11]=SatelliteConfigDisEqC11( 'SatelliteConfigDisEqC11.xml', self.mScriptDir )
			
			from pvr.gui.windows.ChannelSearch import ChannelSearch
			self.mWindows[WIN_ID_CHANNEL_SEARCH]=ChannelSearch( 'ChannelSearch.xml', self.mScriptDir )
			
			from pvr.gui.windows.AutomaticScan import AutomaticScan	
			self.mWindows[WIN_ID_AUTOMATIC_SCAN]=AutomaticScan( 'AutomaticScan.xml', self.mScriptDir )
			
			from pvr.gui.windows.ManualScan import ManualScan
			self.mWindows[WIN_ID_MANUAL_SCAN]=ManualScan( 'ManualScan.xml', self.mScriptDir )
			
			from pvr.gui.windows.EditSatellite import EditSatellite
			self.mWindows[WIN_ID_EDIT_SATELLITE]=EditSatellite( 'EditSatellite.xml', self.mScriptDir )
			
			from pvr.gui.windows.EditTransponder import EditTransponder
			self.mWindows[WIN_ID_EDIT_TRANSPONDER]=EditTransponder( 'EditTransponder.xml', self.mScriptDir )

			"""
			#from pvr.gui.windows.channeleditwindow import ChannelEditWindow
			#ChannelEditWindow( 'channeleditwindow.xml', self.mScriptDir )
			"""

			from pvr.gui.windows.SystemInfo import SystemInfo
			self.mWindows[WIN_ID_SYSTEM_INFO]=SystemInfo( 'SystemInfo.xml', self.mScriptDir )
			
			from pvr.gui.windows.ArchiveWindow import ArchiveWindow
			self.mWindows[WIN_ID_ARCHIVE_WINDOW]=ArchiveWindow( 'ArchiveWindow.xml', self.mScriptDir )
			
			from pvr.gui.windows.EPGWindow import EPGWindow
			self.mWindows[WIN_ID_EPG_WINDOW]=EPGWindow( 'EPGWindow.xml', self.mScriptDir )
			
			from pvr.gui.windows.MediaCenter import MediaCenter
			self.mWindows[WIN_ID_MEDIACENTER]=MediaCenter( 'MediaCenter.xml', self.mScriptDir )

			from pvr.gui.windows.ConditionalAccess import ConditionalAccess
			self.mWindows[WIN_ID_CONDITIONAL_ACCESS]=ConditionalAccess( 'ConditionalAccess.xml', self.mScriptDir ) 

			from pvr.gui.windows.FirstInstallation import FirstInstallation
			self.mWindows[WIN_ID_FIRST_INSTALLATION]=FirstInstallation( 'FirstInstallation.xml', self.mScriptDir )

			from pvr.gui.windows.TimerWindow import TimerWindow
			self.mWindows[WIN_ID_TIMER_WINDOW]=TimerWindow( 'TimerWindow.xml', self.mScriptDir )

			from pvr.gui.windows.InfoPlate import InfoPlate
			self.mWindows[WIN_ID_INFO_PLATE]=InfoPlate( 'LivePlate.xml', self.mScriptDir )

			from pvr.HiddenTest import HiddenTest
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


	def CheckGUISettings( self ) :
		self.LoadSkinPosition( )
		if self.CheckSkinChange( ) or self.CheckFontChange( ) :
			LOG_TRACE( '----------------- Reset -------------- #0' )		
			self.CopyIncludeFile( )
			LOG_TRACE( '----------------- Reset -------------- #1' )		
			self.AddDefaultFont( )
			LOG_TRACE( '----------------- Reset -------------- #3' )
			return True

		return False
			

	def CheckSkinChange( self ) :
		currentSkinName = xbmc.executehttpapi( "GetGUISetting(3, lookandfeel.skin)" )
		print 'skin name=%s : %s' %( self.mSkinName, currentSkinName[4:] )

		if self.mSkinName != currentSkinName[4:] :
			LOG_TRACE( 'change skin name' )
			self.mSkinName = currentSkinName[4:]
			return True
		return False


	def CheckFontChange( self ) :
		return False


	def LoadSkinPosition( self ) :
		if E_ADD_XBMC_HTTP_FUNCTION == True :
			import pvr.Platform
			from pvr.GuiHelper import GetInstanceSkinPosition
	 		LOG_TRACE( '--------------')		
			strResolution = xbmc.executehttpapi( "getresolution( )" )
			LOG_TRACE( '--------------#2')
			LOG_TRACE( 'strResolution=%s' %strResolution )
			resInfo = strResolution[4:].split( ':' )
			LOG_TRACE( 'resInfo=%s' %resInfo )
			#default width=1280 height=720 fixelRate=1.000000 left=0 topt=0 right=1280 bottom=720 zoom=0
			width = int( resInfo[0] )
			height = int( resInfo[1] )
			fixelRate=  float( resInfo[2] )
			left = int( resInfo[3] )
			top = int( resInfo[4] )
			right = int( resInfo[5] )
			bottom = int( resInfo[6] )

			LOG_TRACE( 'width=%d height=%d fixelRate=%f left=%d topt=%d right=%d bottom=%d' %( width, height, fixelRate, left, top, right, bottom ) )
			
			strZoom = xbmc.executehttpapi( "GetGUISetting(0, lookandfeel.skinzoom)" )
			skinzoom = int( strZoom[4:] )
			
			LOG_TRACE( 'zoom=%d' %skinzoom )

			pvr.GuiHelper.GetInstanceSkinPosition( ).SetPosition( left, top, right, bottom, skinzoom )
		else :		

			try :
				import pvr.Platform
				from pvr.GuiHelper import GetInstanceSkinPosition
				from BeautifulSoup import BeautifulSoup
				userDatePath	= pvr.Platform.GetPlatform( ).GetUserDataDir( ) + 'guisettings.xml'
				fp				= open( userDatePath )			
				xml				= fp.read( )
				resolutionInfo	= BeautifulSoup( xml )
				resolution		= resolutionInfo.findAll( 'resolution' )
				left			= int( resolution[1].find( 'left' ).string )
				top				= int( resolution[1].find( 'top' ).string )
				right			= int( resolution[1].find( 'right' ).string )
				bottom			= int( resolution[1].find( 'bottom' ).string )
				zoom			= int( resolutionInfo.find( 'skinzoom' ).string )
				pvr.GuiHelper.GetInstanceSkinPosition( ).SetPosition( left, top, right, bottom, zoom )
				fp.close( )

			except Exception, e :
				if fp.closed == False :
					fp.close( )
				LOG_ERR( 'Error exception[%s]' % e )


	def CopyIncludeFile( self ) :
		import pvr.Platform 

		skinName = self.mSkinName

		print 'skinName=%s' %skinName

		import pvr.Platform 
		self.mScriptDir = pvr.Platform.GetPlatform().GetScriptDir( )

		
		if skinName.lower() == 'default' or skinName.lower() == 'skin.confluence' :
			mboxIncludePath = os.path.join( pvr.Platform.GetPlatform().GetScriptDir( ), 'resources', 'skins', 'Default', '720p', 'mbox_includes.xml' )

		else : 
			mboxIncludePath = os.path.join( pvr.Platform.GetPlatform().GetScriptDir( ), 'resources', 'skins', skinName, '720p', 'mbox_includes.xml' )

			if not os.path.isfile( mboxIncludePath ) :
				mboxIncludePath = os.path.join( pvr.Platform.GetPlatform().GetScriptDir( ), 'resources', 'skins', 'Default', '720p', 'mbox_includes.xml' )			
			
		print 'mboxIncludePath=%s' %mboxIncludePath	

		skinIncludePath = os.path.join( pvr.Platform.GetPlatform().GetSkinDir( ), '720p', 'mbox_includes.xml' )
		print 'skinIncludePath=%s' %skinIncludePath	
		shutil.copyfile( mboxIncludePath, skinIncludePath )


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
		return os.listdir( xbmc.translatePath( 'special://skin/language' ) )


	def GetCurrentLanguage( self ) :
		currentLanguage = xbmc.executehttpapi( "GetGUISetting(3, locale.language)" )
		LOG_TRACE( "Get currentLanguage = %s" % currentLanguage[4:] )
		return currentLanguage[4:]


	def SetCurrentLanguage( self, aLanguage ) :		
		xbmc.executebuiltin( "Custom.SetLanguage(%s)" % aLanguage )
		
