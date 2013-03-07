from pvr.gui.WindowImport import *

E_MAIN_MENU_BASE_ID				=  WinMgr.WIN_ID_MAINMENU * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 

MAIN_GROUP_ID					= E_MAIN_MENU_BASE_ID + 9100
LIST_ID_FAV_ADDON				= E_MAIN_MENU_BASE_ID + 9050
LABEL_ID_SUB_DESCRIPTION		= E_MAIN_MENU_BASE_ID + 100
BUTTON_ID_FAVORITE_EXTRA		= E_MAIN_MENU_BASE_ID + 101

BUTTON_ID_INSTALLATION			= E_MAIN_MENU_BASE_ID + 90100
BUTTON_ID_ARCHIVE				= E_MAIN_MENU_BASE_ID + 90200
BUTTON_ID_EPG					= E_MAIN_MENU_BASE_ID + 90300
BUTTON_ID_CHANNEL_LIST			= E_MAIN_MENU_BASE_ID + 90400
BUTTON_ID_FAVORITE_ADDONS		= E_MAIN_MENU_BASE_ID + 90500
BUTTON_ID_MEDIA_CENTER			= E_MAIN_MENU_BASE_ID + 90600
BUTTON_ID_SYSTEM_INFO			= E_MAIN_MENU_BASE_ID + 90700
BUTTON_ID_HELP					= E_MAIN_MENU_BASE_ID + 90800

BUTTON_ID_MEDIA_WEATHER	        = E_MAIN_MENU_BASE_ID + 90601
BUTTON_ID_MEDIA_PICTURES        = E_MAIN_MENU_BASE_ID + 90602
BUTTON_ID_MEDIA_MUSICS	        = E_MAIN_MENU_BASE_ID + 90603
BUTTON_ID_MEDIA_VIDEOS	        = E_MAIN_MENU_BASE_ID + 90604
BUTTON_ID_MEDIA_PROGRAMS        = E_MAIN_MENU_BASE_ID + 90605
BUTTON_ID_MEDIA_SETTINGS        = E_MAIN_MENU_BASE_ID + 90606
BUTTON_ID_MEDIA_FILE_MGR        = E_MAIN_MENU_BASE_ID + 90607
BUTTON_ID_MEDIA_PROFILES        = E_MAIN_MENU_BASE_ID + 90608
BUTTON_ID_MEDIA_SYS_INFO        = E_MAIN_MENU_BASE_ID + 90609

BUTTON_ID_FIRSTINSTALLATION		= E_MAIN_MENU_BASE_ID + 90101
BUTTON_ID_ANTENNA_SETUP			= E_MAIN_MENU_BASE_ID + 90102
BUTTON_ID_CHANNEL_SEARCH		= E_MAIN_MENU_BASE_ID + 90103
BUTTON_ID_EDIT_SATELLITE		= E_MAIN_MENU_BASE_ID + 90104
BUTTON_ID_EDIT_TRANSPONDER		= E_MAIN_MENU_BASE_ID + 90105
BUTTON_ID_CONFIGURE				= E_MAIN_MENU_BASE_ID + 90106
BUTTON_ID_CAS					= E_MAIN_MENU_BASE_ID + 90107
BUTTON_ID_UPDATE				= E_MAIN_MENU_BASE_ID + 90108


E_MAIN_MENU_DEFAULT_FOCUS_ID	=  E_MAIN_MENU_BASE_ID + 9000


import sys
import os
if sys.version_info < (2, 7) :
    import simplejson
else:
    import json as simplejson

class MainMenu( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		#self.mCtrlFavAddonList = None
		self.mSubDescriptionInstall = [
			MR_LANG( 'Take the following steps for getting your PRISMCUBE RUBY ready for use' ),
			MR_LANG( 'Select the cable connection type on your STB and configure DiSEqC setup' ),
			MR_LANG( 'Perform a quick and easy automatic channel scan or search channels manually' ),
			MR_LANG( 'Add, delete or rename satellites' ),
			MR_LANG( 'Add new transponders or edit the transponders already exist' ),
			MR_LANG( 'Configure the general settings for your digital satellite receiver' ),
			MR_LANG( 'Setup Smartcard or CI-Module configuration for watching pay channels' ),
			MR_LANG( 'Get the latest updates on your PRISMCUBE RUBY' ) ]

		self.mSubDescriptionMedia = [
			MR_LANG( 'Get current weather and weather forecast for thousands of cities around the world' ),
			MR_LANG( 'Access your picture collection and view them as a slideshow with transition effects' ),
			MR_LANG( 'Browse through your source folders and play music files' ),
			MR_LANG( 'Playback videos from the beginning or resume viewing from the moment you stopped' ),
			MR_LANG( 'Run your installed add-ons which enhance the features and functions of XBMC' ),
			MR_LANG( 'Configure the general settings of XBMC' ),
			MR_LANG( 'Handle your multimedia files in an easy and efficient way' ),
			MR_LANG( 'Handle your multimedia files in an easy and efficient way' ),
			MR_LANG( 'Display detailed information about your system status' ) ]


	def onInit( self ) :
		self.setFocusId( E_MAIN_MENU_DEFAULT_FOCUS_ID )	
		self.SetActivate( True )
		self.SetSingleWindowPosition( E_MAIN_MENU_BASE_ID )
		self.SetVisibleRss( )
		self.SetFrontdisplayMessage( 'Main Menu' )
		self.mWinId = xbmcgui.getCurrentWindowId( )

		if self.mDataCache.GetMediaCenter( ) == True :
			self.mDataCache.SetAVBlankByArchive( False )
		self.CheckMediaCenter( )

		#self.GetFavAddons( )


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return

		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_PARENT_DIR :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_MBOX_XBMC :
			self.onClick( BUTTON_ID_MEDIA_CENTER )

		elif actionId == Action.ACTION_MBOX_ARCHIVE :
			if HasAvailableRecordingHDD( ) == False :
				return	
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW )

		elif actionId == Action.ACTION_SHOW_INFO :
			if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
				msg = MR_LANG( 'Try again after stopping all your recordings first' )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), msg )
				dialog.doModal( )
			else :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EPG_WINDOW )


	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return

		LOG_TRACE("MainMenu onclick(): control %d" % aControlId )
		if aControlId >= BUTTON_ID_INSTALLATION and aControlId <= BUTTON_ID_UPDATE :
			if self.mDataCache.Player_GetStatus( ).mMode != ElisEnum.E_MODE_LIVE or self.mDataCache.Record_GetRunningRecorderCount( ) > 0 :
				if self.mPlatform.GetXBMCVersion( ) < self.mPlatform.GetFrodoVersion( ) :
					self.getControl( MAIN_GROUP_ID ).setVisible( False )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Try again after stopping playback, recordings\nand timeshift' ) )
				dialog.doModal( )
				if self.mPlatform.GetXBMCVersion( ) < self.mPlatform.GetFrodoVersion( ) :
					self.getControl( MAIN_GROUP_ID ).setVisible( True )
			else :
				if aControlId == BUTTON_ID_INSTALLATION :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_INSTALLATION )
				elif aControlId == BUTTON_ID_FIRSTINSTALLATION :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_FIRST_INSTALLATION )
				elif aControlId == BUTTON_ID_ANTENNA_SETUP :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ANTENNA_SETUP )
				elif aControlId == BUTTON_ID_CHANNEL_SEARCH :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CHANNEL_SEARCH )
				elif aControlId == BUTTON_ID_EDIT_SATELLITE :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EDIT_SATELLITE )
				elif aControlId == BUTTON_ID_EDIT_TRANSPONDER :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EDIT_TRANSPONDER )
				elif aControlId == BUTTON_ID_CONFIGURE :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIGURE )
				elif aControlId == BUTTON_ID_CAS :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONDITIONAL_ACCESS )
				elif aControlId == BUTTON_ID_UPDATE :
					if self.mPlatform.IsPrismCube( ) :
						WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_SYSTEM_UPDATE )
					else :
						if self.mPlatform.GetXBMCVersion( ) < self.mPlatform.GetPlatform( ).GetFrodoVersion( ) :
							self.getControl( MAIN_GROUP_ID ).setVisible( False )
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Not support Win32' ) )
						dialog.doModal( )
						if self.mPlatform.GetXBMCVersion( ) < self.mPlatform.GetPlatform( ).GetFrodoVersion( ) :
							self.getControl( MAIN_GROUP_ID ).setVisible( True )


		elif aControlId == BUTTON_ID_ARCHIVE :
			if HasAvailableRecordingHDD( ) == False :
				return
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW )

		elif aControlId == BUTTON_ID_EPG :
			if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
				msg = MR_LANG( 'Try again after stopping playback' )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), msg )
				dialog.doModal( )
			else :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EPG_WINDOW )

		elif aControlId == BUTTON_ID_CHANNEL_LIST : #Channel List
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CHANNEL_LIST_WINDOW )

		elif aControlId == BUTTON_ID_FAVORITE_ADDONS :
			self.SetMediaCenter( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_FAVORITES )
			#WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_FAVORITE_ADDONS )

		elif aControlId >= BUTTON_ID_MEDIA_CENTER and aControlId <= BUTTON_ID_MEDIA_SYS_INFO :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode != ElisEnum.E_MODE_LIVE :
				if status.mMode == ElisEnum.E_MODE_PVR :
					msg = MR_LANG( 'Try again after stopping playback' )
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Attention' ), msg )
					dialog.doModal( )
					return

				self.mDataCache.Player_Stop( )

			self.SetMediaCenter( )
			self.mDataCache.SetAVBlankByArchive( True )
			if aControlId == BUTTON_ID_MEDIA_CENTER :
				xbmc.executebuiltin( 'ActivateWindow(Home)' )			
				#WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MEDIACENTER )
			elif aControlId == BUTTON_ID_MEDIA_WEATHER :
				xbmc.executebuiltin( 'ActivateWindow(Weather)' )
			elif aControlId == BUTTON_ID_MEDIA_PICTURES :
				xbmc.executebuiltin( 'ActivateWindow(Pictures)' )
			elif aControlId == BUTTON_ID_MEDIA_MUSICS :
				xbmc.executebuiltin( 'ActivateWindow(Music)' )
			elif aControlId == BUTTON_ID_MEDIA_VIDEOS :
				xbmc.executebuiltin( 'ActivateWindow(Videos)' )
			elif aControlId == BUTTON_ID_MEDIA_PROGRAMS :
				xbmc.executebuiltin( 'ActivateWindow(Programs,Addons,return)' )
			elif aControlId == BUTTON_ID_MEDIA_SETTINGS :
				xbmc.executebuiltin( 'ActivateWindow(Settings)' )
			elif aControlId == BUTTON_ID_MEDIA_FILE_MGR :
				xbmc.executebuiltin( 'ActivateWindow(FileManager)' )
			elif aControlId == BUTTON_ID_MEDIA_PROFILES :
				xbmc.executebuiltin( 'ActivateWindow(Profiles)' )
			elif aControlId == BUTTON_ID_MEDIA_SYS_INFO :
				xbmc.executebuiltin( 'ActivateWindow(SystemInfo)' )

		elif aControlId == BUTTON_ID_SYSTEM_INFO :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_SYSTEM_INFO )

		elif aControlId == LIST_ID_FAV_ADDON :
			position = -1
			position = self.mCtrlFavAddonList.getSelectedPosition( )
			if position != -1 :
				self.SetMediaCenter( )
				XBMC_RunAddon( self.mFavAddonsList[ position ].getProperty( 'AddonId' ) )

		elif aControlId == BUTTON_ID_HELP :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_HELP )
			dialog.doModal( )

		elif aControlId == 20 :
			pass
			"""
			import pvr.Launcher
			pvr.Launcher.GetInstance( ).PowerOff()
			"""


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return

		if aControlId >= BUTTON_ID_FIRSTINSTALLATION and aControlId <= BUTTON_ID_UPDATE :
			self.getControl( LABEL_ID_SUB_DESCRIPTION ).setLabel( self.mSubDescriptionInstall[ aControlId - 1 - BUTTON_ID_INSTALLATION ] )

		elif aControlId >= BUTTON_ID_MEDIA_WEATHER and aControlId <= BUTTON_ID_MEDIA_SYS_INFO :
			self.getControl( LABEL_ID_SUB_DESCRIPTION ).setLabel( self.mSubDescriptionMedia[ aControlId - 1 - BUTTON_ID_MEDIA_CENTER ] )			

		elif aControlId == BUTTON_ID_FAVORITE_EXTRA :
			self.getControl( LABEL_ID_SUB_DESCRIPTION ).setLabel( MR_LANG( 'Access your favorite in a convenient way' ) )


	def GetFavAddons( self ) :
		if pvr.Platform.GetPlatform( ).IsPrismCube( ) :
			currentSkinName = XBMC_GetCurrentSkinName( )
			if currentSkinName == 'skin.confluence' or currentSkinName == 'Default' :
				favoriteList = XBMC_GetFavAddons( )
				LOG_TRACE( 'lael98 #1 favoriteList=%s' %favoriteList )
				self.mCtrlFavAddonList = self.getControl( LIST_ID_FAV_ADDON )
				self.mCtrlFavAddonList.reset( )
				LOG_TRACE( 'lael98' )
				if len( favoriteList ) > 0 :
					self.mFavAddonsList = []
					LOG_TRACE( 'lael98' )
					for i in range( len( favoriteList ) ) :
						LOG_TRACE( 'lael98 name=%s' %xbmcaddon.Addon( favoriteList[i] ).getAddonInfo( 'name' ) )					
						item = xbmcgui.ListItem(  xbmcaddon.Addon( favoriteList[i] ).getAddonInfo( 'name' ) )
						item.setProperty( 'AddonId', favoriteList[i] )
						self.mFavAddonsList.append( item )
					self.mCtrlFavAddonList.addItems( self.mFavAddonsList )


	def SetVisibleRss( self ) :
		if int( GetSetting( 'RSS_FEED' ) ) == 1 :
			self.setProperty( 'RssShow', 'True' )
		else :
			self.setProperty( 'RssShow', 'False' )
						
