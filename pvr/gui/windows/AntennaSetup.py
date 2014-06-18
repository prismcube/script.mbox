from pvr.gui.WindowImport import *

E_ANTENNA_SETUP_BASE_ID				=  WinMgr.WIN_ID_ANTENNA_SETUP * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 
E_ANTENNA_SETUP_SUBMENU_LIST_ID		=  E_ANTENNA_SETUP_BASE_ID + 9000


E_ANTENNA_SETUP_DEFAULT_FOCUS_ID	=  E_ANTENNA_SETUP_SUBMENU_LIST_ID


class AntennaSetup( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		if ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( ) == E_ONE_CABLE :
			self.mTunerConnection		= E_TUNER_ONECABLE
			self.mTunerSignal			= E_SAMEWITH_TUNER
			self.mTuner1Control			= E_DISEQC_1_0
			self.mTuner2Control			= E_DISEQC_1_0
		else :
			self.mTunerConnection		= ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander ).GetProp( )
			self.mTunerSignal			= ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander ).GetProp( )
			self.mTuner1Control			= ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( )
			self.mTuner2Control			= ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).GetProp( )


	def onInit( self ) :
		self.SetActivate( True )
		self.SetSingleWindowPosition( E_ANTENNA_SETUP_BASE_ID )
		self.SetFrontdisplayMessage( MR_LANG('Antenna Setup') )

		self.SetSettingWindowLabel( MR_LANG( 'Antenna and Satellite Setup' ) )
		self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'Installation' ), MR_LANG( 'Antenna Setup' ) ) )
		self.SetPipScreen( )

		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( False )
		self.LoadTunerProperty( )

		if self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_SINGLE :
			self.AddUserEnumControl( E_SpinEx03, MR_LANG( 'Tuner 1 Control' ), E_LIST_TUNER_CONTROL, self.mTuner1Control, MR_LANG( 'Select a control method for tuner 1' ) )
			self.AddInputControl( E_Input01, MR_LANG( ' - Tuner 1 Configuration' ), '', MR_LANG( 'You can add, delete or configure satellites here' ) )
			hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx04, E_Input02 ]
			self.SetVisibleControls( hideControlIds, False )

		else :
			connectTypeDescription = '%s %s' % ( MR_LANG( 'When set to \'Separated\', the tuner 2 receives its own signal input'), MR_LANG('however it will receive only the channel level currently being received by the tuner 1 when this is set to \'Loopthrough\'' ) )
			self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Tuner Connection' ), E_LIST_TUNER_CONNECTION, self.mTunerConnection, connectTypeDescription )
			self.AddUserEnumControl( E_SpinEx02, MR_LANG( 'Tuner 2 Signal' ), E_LIST_TUNER2_SIGNAL, self.mTunerSignal, MR_LANG( 'When set to \'Same with Tuner 1\', both tuners are connected to the same signal source' ) )
			self.AddUserEnumControl( E_SpinEx03, MR_LANG( 'Tuner 1 Control' ), E_LIST_TUNER_CONTROL, self.mTuner1Control, MR_LANG( 'Select a control method for tuner 1' ) )
			self.AddInputControl( E_Input01, MR_LANG( ' - Tuner 1 Configuration' ), '', MR_LANG( 'You can add, delete or configure satellites here' ) )
			self.AddUserEnumControl( E_SpinEx04, MR_LANG( 'Tuner 2 Control' ), E_LIST_TUNER_CONTROL, self.mTuner2Control, MR_LANG( 'Select a control method for tuner 2' ) )
			self.AddInputControl( E_Input02, MR_LANG( ' - Tuner 2 Configuration' ), '', MR_LANG( 'You can add, delete or configure satellites here' ) )

		self.InitControl( )
		self.DisableControl( )
		self.mInitialized = True
		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( True )

		if self.mDataCache.GetEmptySatelliteInfo( ) == True :
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( MR_LANG( 'No satellite data available' ) )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Please reset your device to factory settings' ) )
			dialog.doModal( )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Go to the configuration menu now?' ), MR_LANG( 'When you perform a factory reset,%s all your settings revert to factory defaults' )% NEW_LINE )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.ResetAllControl( )
				self.SetVideoRestore( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIGURE, WinMgr.WIN_ID_MAINMENU )
			else :
				self.ResetAllControl( )
				self.SetVideoRestore( )
				WinMgr.GetInstance( ).CloseWindow( )
		else :
			if self.mTunerMgr.GetNeedLoad( ) == True : 
				self.mTunerMgr.LoadOriginalTunerConfig( )
				self.mTunerMgr.Load( )
				self.mTunerMgr.SetNeedLoad( False )

		self.SetDefaultControl( )


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Save Configuration' ), MR_LANG( 'Do you want to save changes before exit?' ) )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.SetVideoRestore( )
				self.OpenBusyDialog( )
				self.SetTunerProperty( )
				if self.mTunerMgr.CompareCurrentConfiguredState( ) == False or self.mTunerMgr.CompareConfigurationProperty( ) == False :
					self.SaveConfiguration( )
					self.mTunerMgr.SyncChannelBySatellite( )
					self.mDataCache.Channel_InvalidateCurrent( )
					self.mDataCache.Channel_ReLoad( )
				
			elif dialog.IsOK( ) == E_DIALOG_STATE_NO :
				self.SetVideoRestore( )
				self.OpenBusyDialog( )
				if self.mTunerMgr.CompareCurrentConfiguredState( ) == False or self.mTunerMgr.CompareConfigurationProperty( ) == False :
					self.mTunerMgr.CancelConfiguration( )
					self.mTunerMgr.SyncChannelBySatellite( )
					self.mDataCache.Channel_ReTune( )

			else :
				return

			self.CloseWindow( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )				

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )


	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False :
			return
	
		groupId = self.GetGroupId( aControlId )
		if groupId == E_Input01 or groupId == E_Input02 :
			self.OpenConfigureWindow( groupId )

		else :
			if groupId == E_SpinEx01 :
				self.mTunerConnection = self.GetSelectedIndex( E_SpinEx01 )
			elif groupId == E_SpinEx02 :
				self.mTunerSignal = self.GetSelectedIndex( E_SpinEx02 )
			elif groupId == E_SpinEx03 :
				self.mTuner1Control = self.GetSelectedIndex( E_SpinEx03 )
			elif groupId == E_SpinEx04 :
				self.mTuner2Control = self.GetSelectedIndex( E_SpinEx04 )
			self.DisableControl( groupId )


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False :
			return
	
		if self.mInitialized :
			self.ShowDescription( aControlId )


	def OpenConfigureWindow( self, aGroupId ) :
		self.SetTunerProperty( )
		if aGroupId == E_Input01 :
			self.mTunerMgr.SetCurrentTunerNumber( E_TUNER_1 )

		elif aGroupId == E_Input02 :
			self.mTunerMgr.SetCurrentTunerNumber( E_TUNER_2 )

		if self.mTunerMgr.CompareCurrentConfiguredState( ) == False or self.mTunerMgr.CompareConfigurationProperty( ) == False :
			self.OpenBusyDialog( )
			self.SaveConfiguration( )
			self.mDataCache.Channel_ReTune( )
			self.CloseBusyDialog( )

		if self.mTunerMgr.GetCurrentTunerType( ) == E_SIMPLE_LNB :
			self.ResetAllControl( )
			if len( self.mTunerMgr.GetConfiguredSatelliteList( ) ) == 0 :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TUNER_CONFIGURATION )
			else :
				self.mTunerMgr.SetCurrentConfigIndex( 0 )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_SIMPLE )
		
		elif self.mTunerMgr.GetCurrentTunerType( ) == E_MOTORIZE_USALS :
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_MOTORIZED_USALS )
			
		elif self.mTunerMgr.GetCurrentTunerType( ) == E_ONE_CABLE :
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_ONECABLE )

		else :
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TUNER_CONFIGURATION )


	def SaveConfiguration( self ) :
		self.mTunerMgr.SaveConfiguration( )
		#self.mDataCache.Channel_ReTune( )


	def CloseWindow( self ) :
		self.mTunerMgr.SetNeedLoad( True )
		self.ResetAllControl( )
		self.CloseBusyDialog( )
		WinMgr.GetInstance( ).CloseWindow( )


	def DisableControl( self, aControlID = None ) :
		if self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_SINGLE :
			return
		if aControlID == None or aControlID == E_SpinEx01 :
			if self.mTunerConnection == E_TUNER_LOOPTHROUGH or self.mTunerConnection == E_TUNER_ONECABLE :
				control = self.getControl( E_SpinEx02 + 3 )
				time.sleep( 0.02 )
				control.selectItem( E_SAMEWITH_TUNER )
				self.mTunerSignal = E_SAMEWITH_TUNER
				self.SetEnableControl( E_SpinEx02, False )
				if self.mTunerConnection == E_TUNER_ONECABLE :
					self.SetEnableControl( E_SpinEx03, False )
				else :
					self.SetEnableControl( E_SpinEx03, True )
			else :
				self.SetEnableControl( E_SpinEx02, True )
				self.SetEnableControl( E_SpinEx03, True )

		if aControlID == None or aControlID == E_SpinEx02 or aControlID == E_SpinEx01 :
			if self.mTunerSignal == E_SAMEWITH_TUNER :
				if self.GetSelectedIndex( E_SpinEx03 ) != self.GetSelectedIndex( E_SpinEx04 ) :
					control = self.getControl( E_SpinEx04 + 3 )
					control.selectItem( self.mTuner1Control )
					self.mTuner2Control = self.mTuner1Control
				self.SetEnableControl( E_SpinEx04, False )
				self.SetEnableControl( E_Input02, False )
			else :
				self.SetEnableControl( E_SpinEx04, True)
				self.SetEnableControl( E_Input02, True )

		if aControlID == E_SpinEx03 :
			if self.mTunerSignal == E_SAMEWITH_TUNER :
				control = self.getControl( E_SpinEx04 + 3 )
				control.selectItem( self.mTuner1Control )
				self.mTuner2Control = self.mTuner1Control
				self.SetEnableControl( E_SpinEx04, False )
				self.SetEnableControl( E_Input02, False )


	def SetTunerProperty( self ) :
		if self.mTunerConnection == E_TUNER_ONECABLE :
			ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander ).SetProp( E_TUNER_LOOPTHROUGH )
			ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander ).SetProp( self.mTunerSignal )
			ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).SetProp( E_ONE_CABLE )
			ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).SetProp( E_ONE_CABLE )
		else :
			ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander ).SetProp( self.mTunerConnection )
			ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander ).SetProp( self.mTunerSignal )
			ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).SetProp( self.mTuner1Control )
			ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).SetProp( self.mTuner2Control )


	def LoadTunerProperty( self ) :
		if ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( ) == E_ONE_CABLE :
			self.mTunerConnection		= E_TUNER_ONECABLE
			self.mTunerSignal			= E_SAMEWITH_TUNER
		else :
			self.mTunerConnection		= ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander ).GetProp( )
			self.mTunerSignal			= ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander ).GetProp( )
			self.mTuner1Control			= ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( )
			self.mTuner2Control			= ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).GetProp( )

