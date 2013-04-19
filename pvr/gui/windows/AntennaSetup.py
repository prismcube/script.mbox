from pvr.gui.WindowImport import *

E_ANTENNA_SETUP_BASE_ID				=  WinMgr.WIN_ID_ANTENNA_SETUP * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 
E_ANTENNA_SETUP_SUBMENU_LIST_ID		=  E_ANTENNA_SETUP_BASE_ID + 9000


E_ANTENNA_SETUP_DEFAULT_FOCUS_ID	=  E_ANTENNA_SETUP_SUBMENU_LIST_ID



class AntennaSetup( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )


	def onInit( self ) :
		self.SetActivate( True )
		self.SetSingleWindowPosition( E_ANTENNA_SETUP_BASE_ID )
		self.SetFrontdisplayMessage( 'Antenna Setup' )

		self.SetSettingWindowLabel( MR_LANG( 'Antenna and Satellite Setup' ) )
		self.SetPipScreen( )

		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( False )

		connectTypeDescription = '%s %s' % ( MR_LANG( 'When set to \'Separated\', the tuner 2 receives its own signal input'), MR_LANG('however it will receive only the channel level currently being received by the tuner 1 when this is set to \'Loopthrough\'' ) )
		self.AddEnumControl( E_SpinEx01, 'Tuner2 Connect Type', MR_LANG( 'Tuner 2 Connection' ), connectTypeDescription )
		self.AddEnumControl( E_SpinEx02, 'Tuner2 Signal Config', MR_LANG( 'Tuner 2 Signal' ), MR_LANG( 'When set to \'Same with Tuner 1\', both tuners are connected to the same signal source' ) )
		self.AddEnumControl( E_SpinEx03, 'Tuner1 Type', MR_LANG( 'Tuner 1 Control' ), MR_LANG( 'Select a control method for tuner 1' ) )
		self.AddInputControl( E_Input01, MR_LANG( ' - Tuner 1 Configuration' ), '', MR_LANG( 'You can add, delete or configure satellites here' ) )
		self.AddEnumControl( E_SpinEx04, 'Tuner2 Type', MR_LANG( 'Tuner 2 Control' ), MR_LANG( 'Select a control method for tuner 2' ) )
		self.AddInputControl( E_Input02, MR_LANG( ' - Tuner 2 Configuration' ), '', MR_LANG( 'You can add, delete or configure satellites here' ) )

		self.InitControl( )

		#time.sleep( 0.2 )
		self.DisableControl( )
		self.mInitialized = True
		self.SetDefaultControl( )

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


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Save configuration' ), MR_LANG( 'Do you want to save changes before exit?' ) )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.OpenBusyDialog( )
				if self.mTunerMgr.CompareCurrentConfiguredState( ) == False or self.mTunerMgr.CompareConfigurationProperty( ) == False :
					self.SaveConfiguration( )
				self.mTunerMgr.SyncChannelBySatellite( )
				self.mDataCache.Channel_InvalidateCurrent( )
				self.mDataCache.Channel_ReLoad( )
				
			elif dialog.IsOK( ) == E_DIALOG_STATE_NO :
				self.OpenBusyDialog( )
				#if self.mTunerMgr.CompareCurrentConfiguredState( ) == False or self.mTunerMgr.CompareConfigurationProperty( ) == False :
				self.CancelConfiguration( )
				self.mTunerMgr.SyncChannelBySatellite( )
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
		if self.IsActivate( ) == False  :
			return
	
		groupId = self.GetGroupId( aControlId )
		if groupId == E_Input01 or groupId == E_Input02 :
			self.OpenConfigureWindow( groupId )

		else :
			self.ControlSelect( )
			self.DisableControl( groupId )

	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
		if self.mInitialized :
			self.ShowDescription( aControlId )


	def OpenConfigureWindow( self, aGroupId ) :
		if aGroupId == E_Input01 :
			self.mTunerMgr.SetCurrentTunerNumber( E_TUNER_1 )
			configcontrol = E_SpinEx03

		elif aGroupId == E_Input02 :
			self.mTunerMgr.SetCurrentTunerNumber( E_TUNER_2 )
			configcontrol = E_SpinEx04

		if self.mTunerMgr.CompareCurrentConfiguredState( ) == False or self.mTunerMgr.CompareConfigurationProperty( ) == False :
			self.OpenBusyDialog( )
			self.SaveConfiguration( )
			self.mDataCache.Channel_ReTune( )
			self.CloseBusyDialog( )

		if self.GetSelectedIndex( configcontrol ) == E_SIMPLE_LNB :
			self.ResetAllControl( )
			if len( self.mTunerMgr.GetConfiguredSatelliteList( ) ) == 0 :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TUNER_CONFIGURATION )
			else :
				self.mTunerMgr.SetCurrentConfigIndex( 0 )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_SIMPLE )
		
		elif self.GetSelectedIndex( configcontrol ) == E_MOTORIZE_USALS :
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_MOTORIZED_USALS )
			
		elif self.GetSelectedIndex( configcontrol ) == E_ONE_CABLE :
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_ONECABLE )

		else :
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TUNER_CONFIGURATION )


	def SaveConfiguration( self ) :
		self.mTunerMgr.SaveConfiguration( )
		#self.mDataCache.Channel_ReTune( )


	def CancelConfiguration( self ) :
		self.mTunerMgr.CancelConfiguration( )
		self.mDataCache.Channel_ReTune( )


	def CloseWindow( self ) :
		self.mTunerMgr.SetNeedLoad( True )
		self.ResetAllControl( )
		time.sleep( 3 )
		self.CloseBusyDialog( )
		self.SetVideoRestore( )
		WinMgr.GetInstance( ).CloseWindow( )


	def DisableControl( self, aControlID = None ) :
		if aControlID == None or aControlID == E_SpinEx01 :
			if self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
				control = self.getControl( E_SpinEx02 + 3 )
				time.sleep( 0.02 )
				control.selectItem( E_SAMEWITH_TUNER )
				self.SetProp( E_SpinEx02, E_SAMEWITH_TUNER )
				self.SetEnableControl( E_SpinEx02, False )
			else :
				self.SetEnableControl( E_SpinEx02, True )

			if ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( ) == E_ONE_CABLE or ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).GetProp( ) == E_ONE_CABLE :
				self.SetEnableControl( E_SpinEx01, False )
				#self.DisableControl( )

		if aControlID == None or aControlID == E_SpinEx02 or aControlID == E_SpinEx01 :
			selectedIndex = self.mTunerMgr.GetCurrentTunerConfigType( )
			if selectedIndex == E_SAMEWITH_TUNER :
				if self.GetSelectedIndex( E_SpinEx03 ) != self.GetSelectedIndex( E_SpinEx04 ) :
					control = self.getControl( E_SpinEx04 + 3 )
					prop = self.mTunerMgr.GetTunerTypeByTunerIndex( E_TUNER_1 )
					control.selectItem( prop )
					self.SetProp( E_SpinEx04, prop )
				self.SetEnableControl( E_SpinEx04, False )
				self.SetEnableControl( E_Input02, False )
			else :
				self.SetEnableControl( E_SpinEx04, True)
				self.SetEnableControl( E_Input02, True )

		if aControlID == E_SpinEx03 :
			if self.mTunerMgr.GetCurrentTunerConfigType( ) == E_SAMEWITH_TUNER :
				control = self.getControl( E_SpinEx04 + 3 )
				prop = ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( )
				control.selectItem( prop )
				self.SetProp( E_SpinEx04, prop )
				self.SetEnableControl( E_SpinEx04, False )
				self.SetEnableControl( E_Input02, False )
				
			if ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( ) == E_ONE_CABLE :#and self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
				control = self.getControl( E_SpinEx01 + 3 )
				control.selectItem( E_TUNER_LOOPTHROUGH )
				self.SetProp( E_SpinEx01, E_TUNER_LOOPTHROUGH )
				self.SetEnableControl( E_SpinEx01, False )
				self.DisableControl( )
			else :
				self.SetEnableControl( E_SpinEx01, True )

		elif aControlID == E_SpinEx04 :
			if ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).GetProp( ) == E_ONE_CABLE :#and self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
				control = self.getControl( E_SpinEx01 + 3 )
				control.selectItem( E_TUNER_LOOPTHROUGH )
				self.SetProp( E_SpinEx01, E_TUNER_LOOPTHROUGH )
				self.SetEnableControl( E_SpinEx01, False )
				self.DisableControl( )
				self.SetFocusControl( E_SpinEx03 )
			else :
				self.SetEnableControl( E_SpinEx01, True )
			

