from pvr.gui.WindowImport import *


E_INSTALLATION_BASE_ID			=  WinMgr.WIN_ID_INSTALLATION * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 

MENU_ID_FIRSTINSTALLATION		= 0
MENU_ID_ANTENNA_SETUP			= 1
MENU_ID_CHANNEL_SEARCH			= 2
MENU_ID_EDIT_SATELLITE			= 3
MENU_ID_EDIT_TRANSPONDER		= 4
MENU_ID_CONFIGURE				= 5
MENU_ID_CAS						= 6
MENU_ID_UPDATE					= 7
MENU_ID_ADVANCED				= 8

MAIN_LIST_ID					= E_INSTALLATION_BASE_ID + 9000

E_INSTALLATION_DEFAULT_FOCUS_ID	=  MAIN_LIST_ID


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
		MR_LANG( 'Update' ),
		MR_LANG( 'Advanced' ) ]

		self.mDescriptionList = [
		MR_LANG( 'Take the following steps for getting your PRISMCUBE RUBY ready for use' ),
		MR_LANG( 'Select the cable connection type on your STB and configure DiSEqC setup' ),
		MR_LANG( 'Perform a quick and easy automatic channel scan or search channels manually' ),
		MR_LANG( 'Add, delete or rename satellites' ),
		MR_LANG( 'Add new transponders or edit the transponders already exist' ),
		MR_LANG( 'Configure the general settings for your digital satellite receiver' ),
		MR_LANG( 'Setup Smartcard or CI-Module configuration for watching pay channels' ),
		MR_LANG( 'Get the latest updates on your PRISMCUBE RUBY' ),
		MR_LANG( 'Set the advanced preferences that can customize the box to your specific needs' ) ]

		self.SetActivate( True )
		self.SetSingleWindowPosition( E_INSTALLATION_BASE_ID )
		self.SetFrontdisplayMessage( MR_LANG('Installation') )
		self.SetHeaderTitle( MR_LANG( 'Installation' ) )
		self.SetPipScreen( )
		groupItems = []

		for i in range( len( self.mLeftGroupItems ) ) :
			groupItems.append( xbmcgui.ListItem( self.mLeftGroupItems[i], self.mDescriptionList[i] ) )

		self.mCtrlLeftGroup = self.getControl( MAIN_LIST_ID )
		self.mCtrlLeftGroup.addItems( groupItems )
		self.setFocusId( MAIN_LIST_ID )


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.SetVideoRestore( )
			WinMgr.GetInstance( ).CloseWindow( )


	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
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

		elif selectedId == MENU_ID_ADVANCED :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ADVANCED )

	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return


