from pvr.gui.WindowImport import *
import xbmcgui

E_MAIN_MENU_BASE_ID				=  WinMgr.WIN_ID_MAINMENU * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 

MAIN_GROUP_ID					= E_MAIN_MENU_BASE_ID + 9100
LABEL_ID_SUB_DESCRIPTION		= E_MAIN_MENU_BASE_ID + 100
BUTTON_ID_FAVORITE_EXTRA		= E_MAIN_MENU_BASE_ID + 101
BUTTON_ID_POWER					= E_MAIN_MENU_BASE_ID + 102

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
BUTTON_ID_MEDIA_ADDON_MGR       = E_MAIN_MENU_BASE_ID + 90609
BUTTON_ID_MEDIA_SYS_INFO        = E_MAIN_MENU_BASE_ID + 90610

BUTTON_ID_FIRSTINSTALLATION		= E_MAIN_MENU_BASE_ID + 90101
BUTTON_ID_ANTENNA_SETUP			= E_MAIN_MENU_BASE_ID + 90102
BUTTON_ID_CHANNEL_SEARCH		= E_MAIN_MENU_BASE_ID + 90103
BUTTON_ID_EDIT_SATELLITE		= E_MAIN_MENU_BASE_ID + 90104
BUTTON_ID_EDIT_TRANSPONDER		= E_MAIN_MENU_BASE_ID + 90105
BUTTON_ID_CONFIGURE				= E_MAIN_MENU_BASE_ID + 90106
BUTTON_ID_CAS					= E_MAIN_MENU_BASE_ID + 90107
BUTTON_ID_UPDATE				= E_MAIN_MENU_BASE_ID + 90108

BUTTON_ID_CHANNEL_LIST_FAVORITE = E_MAIN_MENU_BASE_ID + 90412
BUTTON_ID_CHANNEL_LIST_LIST		= E_MAIN_MENU_BASE_ID + 90413
BUTTON_ID_CHANNEL_LIST_EDIT		= E_MAIN_MENU_BASE_ID + 90414


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
		

	def onInit( self ) :
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
			MR_LANG( 'Manage your XBMC add-ons' ),
			MR_LANG( 'Display detailed information about your system status' ) ]

		self.setFocusId( E_MAIN_MENU_DEFAULT_FOCUS_ID )	
		self.SetActivate( True )
		self.SetSingleWindowPosition( E_MAIN_MENU_BASE_ID )
		self.SetVisibleRss( )
		self.SetFrontdisplayMessage( MR_LANG('Main Menu') )
		self.mWinId = xbmcgui.getCurrentWindowId( )

		if self.mDataCache.GetMediaCenter( ) == True :
			self.mDataCache.SetAVBlankByArchive( False )
		self.CheckMediaCenter( )

		iChannel = self.mDataCache.Channel_GetCurrent( )
		if self.mDataCache.GetSearchNewChannel( ) :
			self.mDataCache.SetSearchNewChannel( False )
			pvr.GlobalEvent.GetInstance( ).CheckParentLock( E_PARENTLOCK_INIT )
			#LOG_TRACE('---------------------------------------parentLock newCheck')


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False :
			return

		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_PARENT_DIR :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_MBOX_XBMC :
			self.onClick( BUTTON_ID_MEDIA_CENTER )

		elif actionId == Action.ACTION_MBOX_ARCHIVE :
			if HasAvailableRecordingHDD( ) == False :
				return	
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_SHOW_INFO :
			if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
				msg = MR_LANG( 'Try again after stopping all your recordings first' )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), msg )
				dialog.doModal( )
			else :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EPG_WINDOW )

		elif actionId == Action.ACTION_COLOR_BLUE :
			DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).doModal( )


	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return

		LOG_TRACE("MainMenu onclick(): control %d" % aControlId )
		if aControlId >= BUTTON_ID_INSTALLATION and aControlId <= BUTTON_ID_UPDATE :
			if self.mDataCache.Player_GetStatus( ).mMode != ElisEnum.E_MODE_LIVE or self.mDataCache.Record_GetRunningRecorderCount( ) > 0 :
				if self.mPlatform.GetXBMCVersion( ) < self.mPlatform.GetFrodoVersion( ) :
					self.getControl( MAIN_GROUP_ID ).setVisible( False )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Try again after stopping playback, recordings%s and timeshift' )% NEW_LINE )
				dialog.doModal( )
				if self.mPlatform.GetXBMCVersion( ) < self.mPlatform.GetFrodoVersion( ) :
					self.getControl( MAIN_GROUP_ID ).setVisible( True )
			else :
				self.mDataCache.LoadTimerList( )
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
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )

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

		elif aControlId == BUTTON_ID_CHANNEL_LIST_FAVORITE :
			self.ShowFavoriteGroup( )

		elif aControlId == BUTTON_ID_CHANNEL_LIST_LIST :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CHANNEL_LIST_WINDOW )

		elif aControlId == BUTTON_ID_CHANNEL_LIST_EDIT :
			self.GoToEditChannelList( )

		elif aControlId == BUTTON_ID_POWER :

			context = []
			context.append( ContextItem( MR_LANG( 'Active Standby' ), 1 ) )
			context.append( ContextItem( MR_LANG( 'Deep Standby' ), 2 ) )
			#context.append( ContextItem( MR_LANG( 'Restart GUI' ), 0 ) )
			context.append( ContextItem( MR_LANG( 'Restart System' ), 3 ) )

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context )
			dialog.doModal( )
			contextAction = dialog.GetSelectedAction( )

			if contextAction == 0 :
				self.setProperty( 'RestartGUI', 'true' )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
				#self.mDataCache.Splash_StartAndStop( 1 )
				#self.mCommander.Player_SetMute( True )
				pvr.ElisMgr.GetInstance().Shutdown( )
				xbmc.executebuiltin( 'Settings.Save' )
				os.system( 'killall -9 xbmc.bin' )
			elif contextAction == 1 :
				self.mCommander.System_StandbyMode( 1 )
			elif contextAction == 2 :
				self.mCommander.System_StandbyMode( 0 )
			elif contextAction == 3 :
				isDownload = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_SYSTEM_UPDATE ).GetStatusFromFirmware( )
				if isDownload :
					msg = MR_LANG( 'Try again after completing firmware update' )
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Attention' ), msg )
					dialog.doModal( )
					return

				self.mDataCache.System_Reboot( )

		elif ( aControlId >= BUTTON_ID_MEDIA_CENTER and aControlId <= BUTTON_ID_MEDIA_SYS_INFO ) or aControlId == BUTTON_ID_FAVORITE_EXTRA  :
			isDownload = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_SYSTEM_UPDATE ).GetStatusFromFirmware( )
			if isDownload :
				msg = MR_LANG( 'Try again after completing firmware update' )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), msg )
				dialog.doModal( )
				return

			status = self.mDataCache.Player_GetStatus( )
			if status.mMode != ElisEnum.E_MODE_LIVE :
				if status.mMode == ElisEnum.E_MODE_PVR :
					msg = MR_LANG( 'Try again after stopping playback' )
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Attention' ), msg )
					dialog.doModal( )
					return

				self.mDataCache.Player_Stop( )

			if not CheckHdd( ) :
				msg = MR_LANG( 'Installing and executing XBMC add-ons%s may not work properly without an internal HDD' )% NEW_LINE
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), msg )
				dialog.doModal( )

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
			elif aControlId == BUTTON_ID_MEDIA_ADDON_MGR :
				xbmc.executebuiltin( 'ActivateWindow(AddonBrowser)' )
				LOG_TRACE( 'BUTTON_ID_MEDIA_ADDON_MGR' )
			elif aControlId == BUTTON_ID_MEDIA_SYS_INFO :
				xbmc.executebuiltin( 'ActivateWindow(SystemInfo)' )
			elif aControlId == BUTTON_ID_FAVORITE_EXTRA :				
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_FAVORITES )
				
		elif aControlId == BUTTON_ID_SYSTEM_INFO :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_SYSTEM_INFO )

		elif aControlId == BUTTON_ID_HELP :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_HELP )
			dialog.doModal( )


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return

		if aControlId >= BUTTON_ID_FIRSTINSTALLATION and aControlId <= BUTTON_ID_UPDATE :
			self.getControl( LABEL_ID_SUB_DESCRIPTION ).setLabel( self.mSubDescriptionInstall[ aControlId - 1 - BUTTON_ID_INSTALLATION ] )

		elif aControlId >= BUTTON_ID_MEDIA_WEATHER and aControlId <= BUTTON_ID_MEDIA_SYS_INFO :
			self.getControl( LABEL_ID_SUB_DESCRIPTION ).setLabel( self.mSubDescriptionMedia[ aControlId - 1 - BUTTON_ID_MEDIA_CENTER ] )			

		elif aControlId == BUTTON_ID_FAVORITE_EXTRA :
			self.getControl( LABEL_ID_SUB_DESCRIPTION ).setLabel( MR_LANG( 'Access your favorites in a convenient way' ) )

		elif aControlId == BUTTON_ID_POWER :
			self.getControl( LABEL_ID_SUB_DESCRIPTION ).setLabel( MR_LANG( 'Restart XBMC or switch STB to standby mode' ) )

		elif aControlId == BUTTON_ID_CHANNEL_LIST_LIST :
			self.getControl( LABEL_ID_SUB_DESCRIPTION ).setLabel( MR_LANG( 'Display a list of your TV/radio channels' ) )

		elif aControlId == BUTTON_ID_CHANNEL_LIST_EDIT :
			self.getControl( LABEL_ID_SUB_DESCRIPTION ).setLabel( MR_LANG( 'Delete, rename and lock your channels' ) )

		elif aControlId == BUTTON_ID_CHANNEL_LIST_FAVORITE :
			self.getControl( LABEL_ID_SUB_DESCRIPTION ).setLabel( MR_LANG( 'Get fast access to your favorite channels' ) )


	def SetVisibleRss( self ) :
		if int( GetSetting( 'RSS_FEED' ) ) == 1 :
			self.setProperty( 'RssShow', 'True' )
		else :
			self.setProperty( 'RssShow', 'False' )


	def ShowFavoriteGroup( self ) :
		zappingmode = self.mDataCache.Zappingmode_GetCurrent( )

		#check AllChannels
		allChannels = self.mDataCache.Channel_GetAllChannels( zappingmode.mServiceType, True )
		if not allChannels or len( allChannels ) < 1 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No channels available' ) )
			dialog.doModal( )
			return

		#check fav groups
		favoriteGroup = self.mDataCache.Favorite_GetList( FLAG_ZAPPING_CHANGE, zappingmode.mServiceType )
		if not favoriteGroup or len( favoriteGroup ) < 1 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No favorite group available' ) )
			dialog.doModal( )
			return

		#favoriteList = [MR_LANG( 'All Channels' )]
		iFavGroup = ElisIFavoriteGroup( )
		iFavGroup.mGroupName = MR_LANG( 'All Channels' )
		iFavGroup.mServiceType = zappingmode.mServiceType
		favoriteList = [ iFavGroup ]
		for item in favoriteGroup :
			#favoriteList.append( item.mGroupName )
			favoriteList.append( item )

		currentIdx = 0
		if zappingmode.mMode == ElisEnum.E_MODE_FAVORITE :
			favName = zappingmode.mFavoriteGroup.mGroupName
			for idx in range( 1, len( favoriteList ) ) :
				if favName == favoriteList[idx].mGroupName :
					currentIdx = idx
					break

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SELECT )
		dialog.SetPreviousBlocking( False )
		dialog.SetDefaultProperty( MR_LANG( 'Favorite group' ), favoriteList, E_MODE_FAVORITE_GROUP, E_SELECT_ONLY, currentIdx )
		dialog.doModal( )

		isSelect = dialog.GetSelectedList( )

		#isSelect = xbmcgui.Dialog( ).select( MR_LANG( 'Favorite group' ), favoriteList, False, currentIdx )
		LOG_TRACE('---------------select[%s]'% isSelect )
		if isSelect < 0 or isSelect == currentIdx :
			LOG_TRACE( 'back, cancel or same' )
			return


		isSame = False
		if isSelect == 0 :
			#if zappingmode.mMode == ElisEnum.E_MODE_ALL :
			#	isSame = True

			zappingmode.mMode = ElisEnum.E_MODE_ALL

		else :
			isSelect -= 1
			favName = favoriteGroup[isSelect].mGroupName
			iChannelList = self.mDataCache.Channel_GetListByFavorite( zappingmode.mServiceType, ElisEnum.E_MODE_FAVORITE, zappingmode.mSortingMode, favName )
			if not iChannelList or len( iChannelList ) < 1 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( favName, MR_LANG( 'No channels available' ) )
				dialog.doModal( )
				return

			#if zappingmode.mMode == ElisEnum.E_MODE_FAVORITE and zappingmode.mFavoriteGroup == favName :
			#	isSame = True

			zappingmode.mMode = ElisEnum.E_MODE_FAVORITE
			zappingmode.mFavoriteGroup = favoriteGroup[isSelect]


		if isSame :
			LOG_TRACE( 'Already changed' )
			return


		#set change
		ret = self.mDataCache.Zappingmode_SetCurrent( zappingmode )
		if ret :
			self.OpenBusyDialog( )
			self.mDataCache.Channel_Save( )

			#data cache re-load
			self.mDataCache.LoadZappingmode( )
			self.mDataCache.LoadZappingList( )
			self.mDataCache.LoadChannelList( )
			self.mDataCache.SetChannelReloadStatus( True )
			self.mDataCache.Channel_ResetOldChannelList( )

			self.CloseBusyDialog( )

			# channel tune, default 1'st
			iChannelList = self.mDataCache.Channel_GetList( )
			if iChannelList and len( iChannelList ) > 0 :
				iChannel = self.mDataCache.Channel_GetCurrent( )
				if iChannel and iChannel.mError == 0 :
					fChannel = self.mDataCache.Channel_GetCurr( iChannel.mNumber )
					if fChannel and fChannel.mError == 0 :
						iChannel = fChannel
					else :
						iChannel = iChannelList[0]
				else :
					iChannel = iChannelList[0]

				self.mDataCache.Channel_SetCurrent( iChannel.mNumber, iChannel.mServiceType, None, True )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE, WinMgr.WIN_ID_NULLWINDOW )

		else :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( 'Error', MR_LANG( 'Failed to change favorite group' ) )
			dialog.doModal( )


	def GoToEditChannelList( self ) :
		iHead = ''
		iLine = ''
		isError = False
		isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )
		if isRunRec > 0 :
			isError = True
			iHead = MR_LANG( 'Attention' )
			iLine = MR_LANG( 'Try again after stopping all your recordings first' )

		zappingmode = self.mDataCache.Zappingmode_GetCurrent( )
		if self.mDataCache.Channel_GetCount( zappingmode.mServiceType ) < 1 :
			isError = True
			iHead = MR_LANG( 'Error' )
			iLine = MR_LANG( 'Your channel list is empty' )

		if isError :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( iHead, iLine )
			dialog.doModal( )
			return

		WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_CHANNEL_LIST_WINDOW ).SetEditMode( True )
		WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CHANNEL_LIST_WINDOW )


