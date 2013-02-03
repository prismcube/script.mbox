from pvr.gui.WindowImport import *

MAIN_GROUP_ID					= 9100
LIST_ID_FAV_ADDON				= 9050

BUTTON_ID_INSTALLATION			= 90100
BUTTON_ID_ARCHIVE				= 90200
BUTTON_ID_EPG					= 90300
BUTTON_ID_CHANNEL_LIST			= 90400
BUTTON_ID_FAVORITE_ADDONS		= 90500
BUTTON_ID_MEDIA_CENTER			= 90600
BUTTON_ID_SYSTEM_INFO			= 90700
BUTTON_ID_HELP					= 90800

BUTTON_ID_MEDIA_WEATHER	        = 90601
BUTTON_ID_MEDIA_PICTURES        = 90602
BUTTON_ID_MEDIA_MUSICS	        = 90603
BUTTON_ID_MEDIA_VIDEOS	        = 90604
BUTTON_ID_MEDIA_PROGRAMS        = 90605
BUTTON_ID_MEDIA_SETTINGS        = 90606
BUTTON_ID_MEDIA_FILE_MGR        = 90607
BUTTON_ID_MEDIA_PROFILES        = 90608
BUTTON_ID_MEDIA_SYS_INFO        = 90609

BUTTON_ID_FIRSTINSTALLATION		= 90101
BUTTON_ID_ANTENNA_SETUP			= 90102
BUTTON_ID_CHANNEL_SEARCH		= 90103
BUTTON_ID_EDIT_SATELLITE		= 90104
BUTTON_ID_EDIT_TRANSPONDER		= 90105
BUTTON_ID_CONFIGURE				= 90106
BUTTON_ID_CAS					= 90107
BUTTON_ID_UPDATE				= 90108


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


	def onInit( self ) :
		self.SetActivate( True )
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
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_HELP )

		elif aControlId == 20 :
			pass
			"""
			import pvr.Launcher
			pvr.Launcher.GetInstance( ).PowerOff()
			"""


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
		if aControlId == E_FAKE_BUTTON :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )


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
						
