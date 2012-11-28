from pvr.gui.WindowImport import *

MENU_ID_FIRSTINSTALLATION		= 0
MENU_ID_ANTENNA_SETUP			= 1
MENU_ID_CHANNEL_SEARCH			= 2
MENU_ID_EDIT_SATELLITE			= 3
MENU_ID_EDIT_TRANSPONDER		= 4
MENU_ID_CONFIGURE				= 5
MENU_ID_CAS						= 6
MENU_ID_UPDATE					= 7

MAIN_LIST_ID					= 9000


class Installation( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mCtrlLeftGroup = None


	def onInit( self ) :
		self.mLeftGroupItems = [
		MR_LANG( 'First Installation' ),
		MR_LANG( 'Antenna Setup' ),
		MR_LANG( 'Channel Search' ),
		MR_LANG( 'Edit Satellite' ),
		MR_LANG( 'Edit Transponder' ),
		MR_LANG( 'Configuration' ),
		MR_LANG( 'CAS' ),
		MR_LANG( 'Update' )]

		self.mDescriptionList = [
		MR_LANG( 'You can setup Language, Video, Audio, Antenna, Satellite, Channel, Time and Date in the First Installation' ),
		MR_LANG( 'Antenna Setup enables you to configure Tuner 1 and Tuner 2' ),
		MR_LANG( 'Channel Search menu allows you to scan channels automatically or manually' ),
		MR_LANG( 'You can add or delete a satellite here' ),
		MR_LANG( 'Here you can add or delete transponders' ),
		MR_LANG( 'Most of STB settings can be configured via the GUI under Configuration' ),
		MR_LANG( 'The Conditional Access System allows you to setup Smartcard configurations' ),
		MR_LANG( 'Get the latest updates on your PRISMCUBE RUBY' )]
	
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( MR_LANG( 'Installation' ) )
		self.SetPipScreen( )
		self.LoadNoSignalState( )
		groupItems = []

		for i in range( len( self.mLeftGroupItems ) ) :
			groupItems.append( xbmcgui.ListItem( self.mLeftGroupItems[i], self.mDescriptionList[i] ) )

		self.mCtrlLeftGroup = self.getControl( MAIN_LIST_ID )
		self.mCtrlLeftGroup.addItems( groupItems )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.SetVideoRestore( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MAINMENU )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass


	def onClick( self, aControlId ) :
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )

		if selectedId == MENU_ID_FIRSTINSTALLATION :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_FIRST_INSTALLATION )

		elif selectedId == MENU_ID_ANTENNA_SETUP :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ANTENNA_SETUP )

		elif selectedId == MENU_ID_CHANNEL_SEARCH :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CHANNEL_SEARCH )

		elif selectedId == MENU_ID_EDIT_SATELLITE :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EDIT_SATELLITE )

		elif selectedId == MENU_ID_EDIT_TRANSPONDER :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EDIT_TRANSPONDER )

		elif selectedId == MENU_ID_CONFIGURE :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIGURE )

		elif selectedId == MENU_ID_CAS :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONDITIONAL_ACCESS )

		elif selectedId == MENU_ID_UPDATE :
			if self.mPlatform.IsPrismCube( ) :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_SYSTEM_UPDATE )
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Not support Win32' ) )
				dialog.doModal( )

	def onFocus( self, aControlId ) :
		pass

