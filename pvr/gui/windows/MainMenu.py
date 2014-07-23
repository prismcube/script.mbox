from pvr.gui.WindowImport import *
import xbmcgui
import EPGWindow

E_MAIN_MENU_BASE_ID				=  WinMgr.WIN_ID_MAINMENU * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 

MAIN_GROUP_ID					= E_MAIN_MENU_BASE_ID + 9100
LABEL_ID_SUB_DESCRIPTION		= E_MAIN_MENU_BASE_ID + 100
BUTTON_ID_FAVORITE_EXTRA		= E_MAIN_MENU_BASE_ID + 101
BUTTON_ID_POWER					= E_MAIN_MENU_BASE_ID + 102

BUTTON_ID_INSTALLATION			= E_MAIN_MENU_BASE_ID + 90100
BUTTON_ID_ARCHIVE				= E_MAIN_MENU_BASE_ID + 90200
BUTTON_ID_EPG					= E_MAIN_MENU_BASE_ID + 90300
BUTTON_ID_TIMER					= E_MAIN_MENU_BASE_ID + 90900
BUTTON_ID_CHANNEL_LIST			= E_MAIN_MENU_BASE_ID + 90400
BUTTON_ID_YOUTUBETV				= E_MAIN_MENU_BASE_ID + 90500
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
BUTTON_ID_ADVANCED				= E_MAIN_MENU_BASE_ID + 90109

BUTTON_ID_EPG_GRID				= E_MAIN_MENU_BASE_ID + 90312
BUTTON_ID_EPG_CHANNEL			= E_MAIN_MENU_BASE_ID + 90313
BUTTON_ID_EPG_CURRENT			= E_MAIN_MENU_BASE_ID + 90314
BUTTON_ID_EPG_FOLLOWING			= E_MAIN_MENU_BASE_ID + 90315

BUTTON_ID_TIMER_ADD_MANUAL		= E_MAIN_MENU_BASE_ID + 90912
BUTTON_ID_TIMER_DELETE			= E_MAIN_MENU_BASE_ID + 90913

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
			MR_LANG( 'Get the latest updates on your PRISMCUBE RUBY' ),
			MR_LANG( 'Set the advanced preferences that can customize the box to your specific needs' ) ]

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

		if self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_SINGLE or self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_DUAL :
			self.getControl( BUTTON_ID_EDIT_SATELLITE).setVisible( True )
			self.getControl( BUTTON_ID_EDIT_TRANSPONDER).setVisible( True )
			self.getControl( BUTTON_ID_ANTENNA_SETUP).setVisible( True )
		else :
			self.getControl( BUTTON_ID_EDIT_SATELLITE).setVisible( False )
			self.getControl( BUTTON_ID_EDIT_TRANSPONDER).setVisible( False )
			self.getControl( BUTTON_ID_ANTENNA_SETUP).setVisible( False )

		self.setFocusId( E_MAIN_MENU_DEFAULT_FOCUS_ID )	
		self.SetSingleWindowPosition( E_MAIN_MENU_BASE_ID )
		self.setProperty( 'RssShow', GetSetting( 'RSS_FEED_MAIN_MENU' ) )
		self.setProperty( 'YoutubeTV', GetSetting( 'YOUTUBE_TV' ) )
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
			if not HasAvailableRecordingHDD( ) :
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
		if aControlId >= BUTTON_ID_INSTALLATION and aControlId <= BUTTON_ID_ADVANCED :
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
					#if self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_SINGLE or self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_DUAL :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ANTENNA_SETUP )
					#elif self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBT :
					#	WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_DVBT_TUNER_SETUP )

				elif aControlId == BUTTON_ID_CHANNEL_SEARCH :
					if self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_SINGLE or self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_DUAL :
						WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CHANNEL_SEARCH )
					elif self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBT :
						WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CHANNEL_SCAN_DVBT )

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
				elif aControlId == BUTTON_ID_ADVANCED :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ADVANCED )

		elif aControlId == BUTTON_ID_ARCHIVE :
			if not HasAvailableRecordingHDD( ) :
				return

			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )

		elif aControlId == BUTTON_ID_EPG or ( aControlId >= BUTTON_ID_EPG_GRID and aControlId <= BUTTON_ID_EPG_FOLLOWING ):
			if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
				msg = MR_LANG( 'Try again after stopping playback' )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), msg )
				dialog.doModal( )
			else :
				if aControlId == BUTTON_ID_EPG_GRID :
					SetSetting( 'EPG_MODE','%d' %EPGWindow.E_VIEW_GRID )
				elif aControlId == BUTTON_ID_EPG_CHANNEL :
					SetSetting( 'EPG_MODE','%d' %EPGWindow.E_VIEW_CHANNEL )
				elif aControlId == BUTTON_ID_EPG_CURRENT :
					SetSetting( 'EPG_MODE','%d' %EPGWindow.E_VIEW_CURRENT )
				elif aControlId == BUTTON_ID_EPG_FOLLOWING :
					SetSetting( 'EPG_MODE','%d' %EPGWindow.E_VIEW_FOLLOWING )

				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_EPG_WINDOW ).CheckModeChange()					
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EPG_WINDOW )

		elif aControlId == BUTTON_ID_TIMER or ( aControlId >= BUTTON_ID_TIMER_ADD_MANUAL and aControlId <= BUTTON_ID_TIMER_DELETE ):
			if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
				msg = MR_LANG( 'Try again after stopping playback' )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), msg )
				dialog.doModal( )
			else :
				if aControlId == BUTTON_ID_TIMER :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMER_WINDOW )				
				elif aControlId == BUTTON_ID_TIMER_ADD_MANUAL :
					self.ShowAddTimerDialog()				
				elif aControlId == BUTTON_ID_TIMER_DELETE :
					self.ShowDeleteTimerDialog()

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
				if not self.mDataCache.SavePIPStatus( ) :
					RemoveDirectory( E_VOLITILE_PIP_STATUS_PATH )
					DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).PIP_Check( E_PIP_STOP )

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

		elif ( aControlId >= BUTTON_ID_MEDIA_CENTER and aControlId <= BUTTON_ID_MEDIA_SYS_INFO ) or aControlId == BUTTON_ID_FAVORITE_EXTRA :
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

			if not CheckHdd( True ) :
				msg = MR_LANG( 'Installing and executing XBMC add-ons%s may not work properly without an internal HDD' )% NEW_LINE
				if self.mPlatform.GetProduct( ) == PRODUCT_OSCAR :
					msg = MR_LANG( 'Installing and executing XBMC add-ons%s may not work properly without an external storage' )% NEW_LINE
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), msg )
				dialog.doModal( )

			self.SetMediaCenter( )
			#self.mDataCache.SetAVBlankByArchive( True )
			if aControlId == BUTTON_ID_MEDIA_CENTER :
				xbmc.executebuiltin( 'ActivateWindow(Home)' )
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
				#xbmc.executebuiltin( 'ActivateWindow(Home)' )
				xbmc.executebuiltin( "ActivateWindow(favourites)" )

		# doliyu test youtube start
		elif aControlId == BUTTON_ID_YOUTUBETV :
			if os.path.exists( '/mtmp/crossepg_running' ) :
				mHead = MR_LANG( 'While downloading EPG data' )
				mLine = MR_LANG( 'Not allowed operation' )
				xbmc.executebuiltin( 'Notification(%s, %s, 5000, DefaultIconInfo.png)' % ( mHead, mLine ) )
				return
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).StartYoutubeTV( )
				
		elif aControlId == BUTTON_ID_SYSTEM_INFO :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_SYSTEM_INFO )

		elif aControlId == BUTTON_ID_HELP :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_HELP )
			dialog.doModal( )


	def onFocus( self, aControlId ) :
		if aControlId >= BUTTON_ID_FIRSTINSTALLATION and aControlId <= BUTTON_ID_ADVANCED :
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

		elif aControlId == BUTTON_ID_TIMER_ADD_MANUAL :
			self.getControl( LABEL_ID_SUB_DESCRIPTION ).setLabel( MR_LANG( 'Schedule a particular recording by specifying date, time and channel without using the EPG' ) )

		elif aControlId == BUTTON_ID_TIMER_DELETE :
			self.getControl( LABEL_ID_SUB_DESCRIPTION ).setLabel( MR_LANG( 'Delete the specified timer from the timer list' ) )

		elif aControlId == BUTTON_ID_EPG_GRID :
			self.getControl( LABEL_ID_SUB_DESCRIPTION ).setLabel( MR_LANG( 'Display the EPG of each channel according to timeline' ) )

		elif aControlId == BUTTON_ID_EPG_CHANNEL :
			self.getControl( LABEL_ID_SUB_DESCRIPTION ).setLabel( MR_LANG( 'Display current and future scheduled events on each channel' ) )

		elif aControlId == BUTTON_ID_EPG_CURRENT :
			self.getControl( LABEL_ID_SUB_DESCRIPTION ).setLabel( MR_LANG( 'Display the events currently on air' ) )

		elif aControlId == BUTTON_ID_EPG_FOLLOWING :
			self.getControl( LABEL_ID_SUB_DESCRIPTION ).setLabel( MR_LANG( 'Display the events next on schedule' ) )


	def ShowGroupByZappingMode( self ) :
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_GROUP )
		dialog.SetDefaultProperty( E_MODE_ZAPPING_GROUP )
		dialog.doModal( )


	def ShowFavoriteGroup( self ) :
		zappingmode = self.mDataCache.Zappingmode_GetCurrent( )

		#check AllChannels
		chCount = self.mDataCache.Channel_GetCount( zappingmode.mServiceType )
		if not chCount or chCount < 1 :
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

		currentIdx = 0
		loopCount = 0

		iFavGroup = ElisIFavoriteGroup( )
		iFavGroup.mGroupName = MR_LANG( 'All Channels' )
		favoriteList = [ iFavGroup ]
		for iFavGroup in favoriteGroup :
			loopCount += 1
			favoriteList.append( iFavGroup )
			if zappingmode.mMode == ElisEnum.E_MODE_FAVORITE and \
			   zappingmode.mFavoriteGroup.mGroupName == iFavGroup.mGroupName :
				currentIdx = loopCount

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_GROUP )
		dialog.SetDefaultProperty( E_MODE_FAVORITE_GROUP, MR_LANG( 'Favorite group' ), favoriteList, currentIdx )
		dialog.doModal( )

		isSelect = dialog.GetSelectedList( )

		#isSelect = xbmcgui.Dialog( ).select( MR_LANG( 'Favorite group' ), favoriteList, False, currentIdx )
		LOG_TRACE('---------------select[%s]'% isSelect )
		if isSelect < 0 or isSelect == currentIdx :
			LOG_TRACE( 'back, cancel or same' )
			return

		isFail = False
		iChannelList = []
		lblLine = MR_LANG( 'Failed to change favorite group' )

		self.OpenBusyDialog( )
		try :
			iZappingmode = deepcopy( zappingmode )
			if isSelect == 0 :
				iZappingmode.mMode = ElisEnum.E_MODE_ALL

			else :
				isSelect -= 1
				favName = favoriteGroup[isSelect].mGroupName
				iZappingmode.mMode = ElisEnum.E_MODE_FAVORITE
				iZappingmode.mFavoriteGroup = favoriteGroup[isSelect]
				iChannelList = self.mDataCache.Channel_GetListByFavorite( iZappingmode.mServiceType, ElisEnum.E_MODE_FAVORITE, iZappingmode.mSortingMode, favName, '', True )
				if not iChannelList or len( iChannelList ) < 1 :
					isFail = True
					lblLine = MR_LANG( 'No channels available' )
					raise Exception, 'Failed, No channels available'

			#set change
			ret = self.mDataCache.Zappingmode_SetCurrent( iZappingmode )
			if ret :
				self.mDataCache.Channel_Save( )

				#data cache re-load
				self.mDataCache.LoadZappingmode( )
				self.mDataCache.LoadZappingList( )
				self.mDataCache.LoadChannelList( )
				self.mDataCache.SetChannelReloadStatus( True )
				self.mDataCache.Channel_ResetOldChannelList( )

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
				isFail = True
				lblLine = MR_LANG( 'Failed to change favorite group' )
				raise Exception, 'Failed Zappingmode_SetCurrent'

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )
			isFail = True

		self.CloseBusyDialog( )

		if isFail :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), lblLine )
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


	def ShowAddTimerDialog( self ) :
		"""
		runningCount = self.mDataCache.Record_GetRunningRecorderCount( )
		#LOG_TRACE( 'runningCount[%s]' %runningCount)
		if not HasAvailableRecordingHDD( ) :
			return

		isOK = False
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
		dialog.SetManualMode( True )
		dialog.doModal( )

		isOK = dialog.IsOK( )
		if isOK == E_DIALOG_STATE_YES :
			isOK = True

		if dialog.IsOK( ) == E_DIALOG_STATE_ERROR and dialog.GetConflictTimer( ) :
			RecordConflict( dialog.GetConflictTimer( ) )
		"""
		if not HasAvailableRecordingHDD( ) :
			return

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_ADD_MANUAL_TIMER )
		dialog.EnableSelectChannel( True )

		dialog.SetEPG( None  )
			
		channel =  self.mDataCache.Channel_GetCurrent( )
		dialog.SetChannel( channel )			

		dialog.doModal( )

		if dialog.IsOK( ) == E_DIALOG_STATE_ERROR :
			if dialog.GetConflictTimer( ) == None :
				infoDialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				infoDialog.SetDialogProperty( MR_LANG( 'Error' ), dialog.GetErrorMessage( ) )
				infoDialog.doModal( )
			else :
				RecordConflict( dialog.GetConflictTimer( ) )


	def ShowDeleteTimerDialog( self ) :
		timers = 	self.mDataCache.Timer_GetTimerList( )
		if len( timers  ) < 1:
			msg = MR_LANG( 'There is no valid timer' )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), msg )
			dialog.doModal( )
			return
			

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_BIG_SELECT )
		dialog.SetDefaultProperty( MR_LANG( 'Delete Timer' ), timers )		
		dialog.doModal( )
		selectedList  = dialog.GetSelectedList()
		print 'LAEL98 TEST selectedList=%s' %selectedList
		for timerIndex  in selectedList :
			timer =  timers[timerIndex]
			if timer :
				self.mDataCache.Timer_DeleteTimer( timer.mTimerId )
		


