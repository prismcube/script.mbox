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
BUTTON_ID_BACK					= 90800

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


class MainMenu( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mCtrlFavAddonList = None


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.CheckMediaCenter( )
		self.GetPlayerStatus( )
		self.GetFavAddons( )


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
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Try again after stopping all your recordings first' ) )
				dialog.doModal( )
				self.getControl( MAIN_GROUP_ID ).setVisible( True )
			elif self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
				self.getControl( MAIN_GROUP_ID ).setVisible( False )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Try again after stopping all your recordings first' ) )
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
			if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Try again after stopping all your recordings first' ) )
				dialog.doModal( )
			else :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EPG_WINDOW )

		elif aControlId == BUTTON_ID_CHANNEL_LIST : #Channel List
			if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Try again after stopping all your recordings first' ) )
				dialog.doModal( )
			else :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CHANNEL_LIST_WINDOW )

		elif aControlId == BUTTON_ID_FAVORITE_ADDONS :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_FAVORITE_ADDONS )

		elif aControlId >= BUTTON_ID_MEDIA_CENTER and aControlId <= BUTTON_ID_MEDIA_SYS_INFO :
			if self.mDataCache.Record_GetRunningRecorderCount( ) > 0 :
				self.getControl( MAIN_GROUP_ID ).setVisible( False )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Try again after stopping all your recordings first' ) )
				dialog.doModal( )
				self.getControl( MAIN_GROUP_ID ).setVisible( True )

			elif self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
				self.getControl( MAIN_GROUP_ID ).setVisible( False )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Try again after stopping the PVR first' ) )
				dialog.doModal( )
				self.getControl( MAIN_GROUP_ID ).setVisible( True )

			else:
				self.SetMediaCenter( )
				if aControlId == BUTTON_ID_MEDIA_CENTER :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MEDIACENTER )
				#WinMgr.GetInstance( ).Reset( )

		elif aControlId == BUTTON_ID_SYSTEM_INFO :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_SYSTEM_INFO )

		elif aControlId == LIST_ID_FAV_ADDON :
			position = -1
			position = self.mCtrlFavAddonList.getSelectedPosition( )
			if position != -1 :
				self.SetMediaCenter( )
				xbmc.executebuiltin( "runaddon(%s)" % self.mFavAddonsList[ position ].getProperty( 'AddonId' ) )

		elif aControlId == 20 :
			pass
			"""
			import pvr.Launcher
			pvr.Launcher.GetInstance( ).PowerOff()
			"""


	def onFocus( self, aControlId ) :
		if aControlId == E_FAKE_BUTTON :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )


	def GetPlayerStatus( self ) :
		if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
			self.mWin.setProperty( 'IsPVR', 'True' )
		else :
			self.mWin.setProperty( 'IsPVR', 'False' )


	def GetFavAddons( self ) :
		if pvr.Platform.GetPlatform( ).IsPrismCube( ) :
			currentSkinName = xbmc.executehttpapi( "GetGUISetting(3, lookandfeel.skin)" )
			currentSkinName = currentSkinName[4:]
			if currentSkinName == 'skin.confluence' :
				tmpList = xbmc.executehttpapi( "getfavourites()" )
				self.mCtrlFavAddonList = self.getControl( LIST_ID_FAV_ADDON )
				self.mCtrlFavAddonList.reset( )
				if tmpList != '<li>' :
					tmpList = tmpList[4:].split( ':' )
					tmpList = self.SyncAddonsList( tmpList )
					if tmpList :
						self.mFavAddonsList = []
						for i in range( len( tmpList ) ) :
							item = xbmcgui.ListItem(  xbmcaddon.Addon( tmpList[i] ).getAddonInfo( 'name' ) )
							item.setProperty( 'AddonId', tmpList[i] )
							self.mFavAddonsList.append( item )
						self.mCtrlFavAddonList.addItems( self.mFavAddonsList )


	def SyncAddonsList( self, aAddonList ) :
		tmpList = xbmc.executehttpapi( "getaddons()" )
		result = deepcopy( aAddonList )
		if tmpList == '<li>' :
			return None
		else :
			tmpList = tmpList[4:].split( ':' )
			for i in range( len( aAddonList ) ) :
				findaddon = False
				for addon in tmpList :
					if aAddonList[i] == addon :
						findaddon = True
				if findaddon == False :
					del result[i]

		return result
