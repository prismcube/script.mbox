from pvr.gui.WindowImport import *

MAIN_GROUP_ID					= 9100

BUTTON_ID_INSTALLATION			= 90100
BUTTON_ID_ARCHIVE				= 90200
BUTTON_ID_EPG					= 90300
BUTTON_ID_CHANNEL_LIST			= 90400
BUTTON_ID_MEDIA_CENTER			= 90500
BUTTON_ID_SYSTEM_INFO			= 90600
BUTTON_ID_BACK					= 90700
BUTTON_ID_HIDDEN_TEST			= 90800

BUTTON_ID_MEDIA_WEATHER	        = 90501
BUTTON_ID_MEDIA_PICTURES        = 90502
BUTTON_ID_MEDIA_MUSICS	        = 90503
BUTTON_ID_MEDIA_VIDEOS	        = 90504
BUTTON_ID_MEDIA_PROGRAMS        = 90505
BUTTON_ID_MEDIA_SETTINGS        = 90506
BUTTON_ID_MEDIA_FILE_MGR        = 90507
BUTTON_ID_MEDIA_PROFILES        = 90508
BUTTON_ID_MEDIA_SYS_INFO        = 90509

BUTTON_ID_FIRSTINSTALLATION		= 90101
BUTTON_ID_ANTENNA_SETUP			= 90102
BUTTON_ID_CHANNEL_SEARCH		= 90103
BUTTON_ID_EDIT_SATELLITE		= 90104
BUTTON_ID_EDIT_TRANSPONDER		= 90105
BUTTON_ID_CONFIGURE				= 90106
BUTTON_ID_CAS					= 90107


class MainMenu( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mStartMediaCenter = False


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		if self.mStartMediaCenter == True :
			self.mCommander.AppMediaPlayer_Control( 0 )
			WinMgr.GetInstance( ).CheckGUISettings( )
			self.UpdateVolume( )

			self.mStartMediaCenter = False
			#current channel re-zapping
			iChannel = self.mDataCache.Channel_GetCurrent( )
			if iChannel :
				self.mDataCache.Channel_InvalidateCurrent( )
				self.mDataCache.Channel_SetCurrentSync( iChannel.mNumber, iChannel.mServiceType )

		self.getPlayerStatus( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_PARENT_DIR :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_MBOX_XBMC :
			self.onClick( BUTTON_ID_MEDIA_CENTER )

		elif actionId == Action.ACTION_MBOX_ARCHIVE :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW )

		elif actionId == Action.ACTION_SHOW_INFO :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EPG_WINDOW )


	def onClick( self, aControlId ) :
		LOG_TRACE("MainMenu onclick(): control %d" % aControlId )
		if aControlId >= BUTTON_ID_INSTALLATION and aControlId <= BUTTON_ID_CAS :
			if self.mDataCache.Record_GetRunningRecorderCount( ) > 0 :
				self.getControl( MAIN_GROUP_ID ).setVisible( False )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'Attention', 'Please stop the recordings first' )
				dialog.doModal( )
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

		elif aControlId == BUTTON_ID_ARCHIVE :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW )

		elif aControlId == BUTTON_ID_EPG :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EPG_WINDOW )

		elif aControlId == BUTTON_ID_CHANNEL_LIST : #Channel List
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CHANNEL_LIST_WINDOW )

		elif aControlId >= BUTTON_ID_MEDIA_CENTER and aControlId <= BUTTON_ID_MEDIA_SYS_INFO :
			if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
				self.getControl( MAIN_GROUP_ID ).setVisible( False )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Please stop the Personal Video Recording first' ) )
				dialog.doModal( )
				self.getControl( MAIN_GROUP_ID ).setVisible( True )

			else:
				self.mStartMediaCenter = True
				self.mCommander.AppMediaPlayer_Control( 1 )
				if aControlId == BUTTON_ID_MEDIA_CENTER :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MEDIACENTER )
				#WinMgr.GetInstance( ).Reset( )

		elif aControlId == BUTTON_ID_SYSTEM_INFO :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_SYSTEM_INFO )

		elif aControlId == 20 :
			pass
			"""
			import pvr.Launcher
			pvr.Launcher.GetInstance( ).PowerOff()
			"""


	def onFocus( self, aControlId ) :
		LOG_TRACE('')
		pass


	def getPlayerStatus( self ) :
		if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
			self.mWin.setProperty( 'IsPVR', 'True' )
		else :
			self.mWin.setProperty( 'IsPVR', 'False' )

