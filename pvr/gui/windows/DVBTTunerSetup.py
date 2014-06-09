from pvr.gui.WindowImport import *
import pvr.ScanHelper as ScanHelper


E_DVBT_TUNER_SETUP_BASE_ID = WinMgr.WIN_ID_DVBT_TUNER_SETUP * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 


E_TUNER_DVBC	= 0
E_TUNER_DVBT	= 1
E_TUNER_DVBT2	= 2


class DVBTTunerSetup( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mTunerType = E_TUNER_DVBC
		self.mEnable5v	= 0


	def onInit( self ) :
		self.SetActivate( True )
		self.SetFrontdisplayMessage( MR_LANG('Tuner Setup') )		
		self.mWinId = xbmcgui.getCurrentWindowId( )

		self.SetSettingWindowLabel( MR_LANG( 'Tuner Setup' ) )
		self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'Installation' ), MR_LANG( 'Tuner Setup' ) ) )
		self.SetSingleWindowPosition( E_DVBT_TUNER_SETUP_BASE_ID )

		self.SetPipScreen( )

		self.ResetAllControl( )
		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( False )

		self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Tuner Type' ), [ MR_LANG( 'DVB-C' ), MR_LANG( 'DVB-T' ), MR_LANG( 'DVB-T2' ) ], self.mTunerType, MR_LANG( 'Select tuner type' ) )
		self.AddInputControl( E_Input01, MR_LANG( 'Terrestrial provider' ), 'Iceland: DVB-T Frequencies', MR_LANG( 'Input frequency' ) )
		self.AddUserEnumControl( E_SpinEx02, MR_LANG( 'Enable 5V for active antenna' ), USER_ENUM_LIST_ON_OFF, self.mEnable5v, MR_LANG( 'Select enable 5v for active antenna' ) )

		self.InitControl( )
		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( True )

		self.mInitialized = True
		self.SetDefaultControl( )


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		actionId = aAction.getId( )
		focusId = self.getFocusId( )

		self.GlobalSettingAction( self, actionId )
		
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			self.SetVideoRestore( )
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( self )

		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( self )
		

	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
		groupId = self.GetGroupId( aControlId )

		# Tuner type
		if groupId == E_SpinEx01 :
			self.mTunerType = self.GetSelectedIndex( E_SpinEx01 )

		elif groupId == E_SpinEx02 :
			self.mTunerType = self.GetSelectedIndex( E_SpinEx02 )


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return

		if self.mInitialized :
			self.ShowDescription( aControlId )
