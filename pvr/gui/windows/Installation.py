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


class Installation( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mCtrlLeftGroup = None
		self.mLeftGroupItems = []
		self.mDescriptionList = []


	def onInit( self ) :
		self.SetTitleDes( )
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


	def SetTitleDes( self ) :
		self.mLeftGroupItems = []
		self.mDescriptionList = []

		self.mLeftGroupItems.append( MR_LANG( 'First Installation' ) )
		self.mDescriptionList.append( MR_LANG( 'Take the following steps for getting your PRISMCUBE RUBY ready for use' ) )

		self.mLeftGroupItems.append( MR_LANG( 'Antenna Setup' ) )
		self.mDescriptionList.append( MR_LANG( 'Select the cable connection type on your STB and configure DiSEqC setup' ) )

		self.mLeftGroupItems.append( MR_LANG( 'Channel Search' ) )
		self.mDescriptionList.append( MR_LANG( 'Perform a quick and easy automatic channel scan or search channels manually' ) )

		if self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_SINGLE or self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_DUAL :
			self.mLeftGroupItems.append( MR_LANG( 'Edit Satellite' ) )
			self.mDescriptionList.append( MR_LANG( 'Add, delete or rename satellites' ) )

			self.mLeftGroupItems.append( MR_LANG( 'Edit Transponder' ) )
			self.mDescriptionList.append( MR_LANG( 'Add new transponders or edit the transponders already exist' ) )

		self.mLeftGroupItems.append( MR_LANG( 'Configuration' ) )
		self.mDescriptionList.append( MR_LANG( 'Configure the general settings for your digital satellite receiver' ) )

		self.mLeftGroupItems.append( MR_LANG( 'CAS' ) )
		self.mDescriptionList.append( MR_LANG( 'Setup Smartcard or CI-Module configuration for watching pay channels' ) )

		self.mLeftGroupItems.append( MR_LANG( 'Update' ) )
		self.mDescriptionList.append( MR_LANG( 'Get the latest updates on your PRISMCUBE RUBY' ) )

		self.mLeftGroupItems.append( MR_LANG( 'Advanced' ) )
		self.mDescriptionList.append( MR_LANG( 'Set the advanced preferences that can customize the box to your specific needs' ) )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.SetVideoRestore( )
			WinMgr.GetInstance( ).CloseWindow( )


	def onClick( self, aControlId ) :
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		if self.mPlatform.GetTunerType( ) != TUNER_TYPE_DVBS_SINGLE and self.mPlatform.GetTunerType( ) != TUNER_TYPE_DVBS_DUAL :
			if selectedId > MENU_ID_CHANNEL_SEARCH :
				selectedId = selectedId + 2

		if selectedId == MENU_ID_FIRSTINSTALLATION :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_FIRST_INSTALLATION )

		elif selectedId == MENU_ID_ANTENNA_SETUP :
			if self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_SINGLE or self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_DUAL :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ANTENNA_SETUP )
			elif self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBT :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_DVBT_TUNER_SETUP )

		elif selectedId == MENU_ID_CHANNEL_SEARCH :
			if self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_SINGLE or self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_DUAL :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CHANNEL_SEARCH )
			elif self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBT :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CHANNEL_SCAN_DVBT )

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
		pass

