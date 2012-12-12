from pvr.gui.WindowImport import *
import pvr.TunerConfigMgr as ConfigMgr


class AntennaSetup( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.getControl( E_SUBMENU_LIST_ID ).setVisible( False )

		self.SetSettingWindowLabel( MR_LANG( 'Antenna and Satellite Setup' ) )
		self.SetPipScreen( )
		self.LoadNoSignalState( )

		if self.mDataCache.GetFristInstallation( ) == True :
			self.DrawFirstTimeInstallationStep( E_STEP_ANTENNA )
		else :
			self.DrawFirstTimeInstallationStep( None )

		self.AddEnumControl( E_SpinEx01, 'Tuner2 Connect Type', MR_LANG( 'Tuner 2 Connection' ), MR_LANG( 'When set to \'Separated\', the tuner 2 receives its own signal input however it will receive only the channel level currently being received by the tuner 1 when this is set to \'Loopthrough\'' ) )
		self.AddEnumControl( E_SpinEx02, 'Tuner2 Signal Config', MR_LANG( 'Tuner 2 Signal' ), MR_LANG( 'When set to \'Same with Tuner 1\', both tuners are connected to the same signal source' ) )
		self.AddEnumControl( E_SpinEx03, 'Tuner1 Type', MR_LANG( 'Tuner 1 Control' ), MR_LANG( 'Select a control method for tuner 1' ) )
		self.AddInputControl( E_Input01, MR_LANG( ' - Tuner 1 Configuration' ), '', MR_LANG( 'You can add, delete or configure satellites here' ) )
		self.AddEnumControl( E_SpinEx04, 'Tuner2 Type', None, MR_LANG( 'Select a control method for tuner 2' ) )
		self.AddInputControl( E_Input02, MR_LANG( ' - Tuner 2 Configuration' ), '', MR_LANG( 'You can add, delete or configure satellites here' ) )

		if self.mDataCache.GetFristInstallation( ) == True :
			self.AddPrevNextButton( MR_LANG( 'Go to the channel search setup page' ), MR_LANG( 'Go back to the video and audio setup page' ) )
			self.getControl( E_FIRST_TIME_INSTALLATION_NEXT_LABEL ).setLabel( MR_LANG( 'Next' ) )
			self.getControl( E_FIRST_TIME_INSTALLATION_PREV_LABEL ).setLabel( MR_LANG( 'Previous' ) )

		self.getControl( E_SUBMENU_LIST_ID ).setVisible( True )

		self.setVisibleButton( )
		self.InitControl( )
		time.sleep( 0.2 )
		self.DisableControl( )
		self.setDefaultControl( )
		self.SetPipLabel( )
		self.mInitialized = True

		if self.mDataCache.GetEmptySatelliteInfo( ) == True :
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( MR_LANG( 'No satellite data available' ) )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Please reset your device to factory settings' ) )
			dialog.doModal( )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Go to the configuration menu now?' ), MR_LANG( 'When you perform a factory reset,\nall your settings revert to factory defaults' ) )
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
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			if self.mDataCache.GetFristInstallation( ) == True :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( MR_LANG( 'Exit installation' ), MR_LANG( 'Are you sure you want to quit the first installation?' ) )
				dialog.doModal( )

				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					self.OpenBusyDialog( )
					if self.CompareCurrentConfiguredState( ) == False or self.CompareConfigurationProperty( ) == False :
						self.CancelConfiguration( )
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_FIRST_INSTALLATION ).mStepNum = E_STEP_SELECT_LANGUAGE
					self.SetParentID( WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_FIRST_INSTALLATION ).GetParentID( ) )
					self.mDataCache.SetFristInstallation( False )
					self.mTunerMgr.SyncChannelBySatellite( )
					self.mDataCache.Channel_ReLoad( )
					self.mDataCache.Player_AVBlank( False )
					self.CloseWindow( )

			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( MR_LANG( 'Save configuration' ), MR_LANG( 'Do you want to save changes before exit?' ) )
				dialog.doModal( )

				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					self.OpenBusyDialog( )
					if self.CompareCurrentConfiguredState( ) == False or self.CompareConfigurationProperty( ) == False :
						self.SaveConfiguration( )
					self.mTunerMgr.SyncChannelBySatellite( )
					self.mDataCache.Channel_ReLoad( )
					
				elif dialog.IsOK( ) == E_DIALOG_STATE_NO :
					self.OpenBusyDialog( )
					if self.CompareCurrentConfiguredState( ) == False or self.CompareConfigurationProperty( ) == False :
						self.CancelConfiguration( )
				else :
					return

				self.CloseWindow( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )				

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )


	def onClick( self, aControlId ) :
		groupId = self.GetGroupId( aControlId )
		if groupId == E_Input01 or groupId == E_Input02 :
			self.OpenConfigureWindow( groupId )

		if groupId == E_SpinEx01 or groupId == E_SpinEx02 :
			self.ControlSelect( )
			self.DisableControl( groupId )

		elif groupId == E_SpinEx03 :
			self.ControlSelect( )
			self.DisableControl( groupId )

		elif groupId == E_SpinEx04 :
			self.ControlSelect( )

		elif aControlId == E_FIRST_TIME_INSTALLATION_NEXT or aControlId == E_FIRST_TIME_INSTALLATION_PREV :
			self.OpenBusyDialog( )
			if self.CompareCurrentConfiguredState( ) == False or self.CompareConfigurationProperty( ) == False :
				self.SaveConfiguration( )
			self.ResetAllControl( )
			if aControlId == E_FIRST_TIME_INSTALLATION_NEXT :
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_FIRST_INSTALLATION ).SetResultAntennaStep( True )
			else :
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_FIRST_INSTALLATION ).SetResultAntennaStep( False )
			self.mTunerMgr.SetNeedLoad( True )
			self.CloseBusyDialog( )
			WinMgr.GetInstance( ).CloseWindow( )

		
	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return
		if self.mLastFocused != aControlId :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId


	def OpenConfigureWindow( self, aGroupId ) :
		if aGroupId == E_Input01 :
			self.mTunerMgr.SetCurrentTunerNumber( E_TUNER_1 )
			configcontrol = E_SpinEx03

		elif aGroupId == E_Input02 :
			self.mTunerMgr.SetCurrentTunerNumber( E_TUNER_2 )
			configcontrol = E_SpinEx04

		if self.CompareCurrentConfiguredState( ) == False or self.CompareConfigurationProperty( ) == False :
			self.OpenBusyDialog( )
			self.SaveConfiguration( )
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
		self.mTunerMgr.SatelliteConfigSaveList( )
		self.mDataCache.LoadConfiguredSatellite( )
		self.mDataCache.LoadConfiguredTransponder( )
		self.ReTune( )


	def CancelConfiguration( self ) :
		self.mTunerMgr.Restore( )
		self.mDataCache.LoadConfiguredSatellite( )
		self.mDataCache.LoadConfiguredTransponder( )
		self.ReTune( )


	def CloseWindow( self ) :
		self.mTunerMgr.SetNeedLoad( True )
		self.ResetAllControl( )
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


	def setVisibleButton( self ) :
		if self.mDataCache.GetFristInstallation( ) == True :
			self.SetVisibleControl( E_FIRST_TIME_INSTALLATION_NEXT, True )
			self.SetVisibleControl( E_FIRST_TIME_INSTALLATION_PREV, True )
		else :
			self.SetVisibleControl( E_FIRST_TIME_INSTALLATION_NEXT, False )
			self.SetVisibleControl( E_FIRST_TIME_INSTALLATION_PREV, False )


	def ReTune( self ) :
		channel = self.mDataCache.Channel_GetCurrent( )
		if channel == None or channel.mError != 0 :
			LOG_ERR( 'Load Channel_GetCurrent None' )
		else :
			self.mCommander.Channel_InvalidateCurrent( )
			self.mDataCache.Channel_SetCurrent( channel.mNumber, channel.mServiceType )


	def CompareCurrentConfiguredState( self ) :
		configuredList1		= self.mTunerMgr.GetConfiguredSatelliteListbyTunerIndex( E_TUNER_1 )	
		currentconfiguredList1	= self.mDataCache.GetConfiguredSatelliteListByTunerIndex( E_TUNER_1 )
		configuredList2		= self.mTunerMgr.GetConfiguredSatelliteListbyTunerIndex( E_TUNER_2 ) 
		currentconfiguredList2	= self.mDataCache.GetConfiguredSatelliteListByTunerIndex( E_TUNER_2 )
		if currentconfiguredList1 == None or currentconfiguredList2 == None or len( configuredList1 ) == 0 or len( configuredList1 ) == 0 :
			return False

		if len( configuredList1 ) != len( currentconfiguredList1 ) :
			return False
		if self.mTunerMgr.GetCurrentTunerConfigType( ) == E_SAMEWITH_TUNER :
			if len( configuredList2 ) != len( currentconfiguredList2 ) :
				return False
			
		if self.mTunerMgr.GetCurrentTunerConfigType( ) == E_SAMEWITH_TUNER :
			for i in range( len( configuredList1 ) ) :
				if configuredList1[i].__dict__ != currentconfiguredList1[i].__dict__ :
					return False
		else :
			for i in range( len( configuredList1 ) ) :
				if configuredList1[i].__dict__ != currentconfiguredList1[i].__dict__ :
					return False
			for i in range( len( configuredList2 ) ) :
				if configuredList2[i].__dict__ != currentconfiguredList2[i].__dict__ :
					return False
		return True


	def CompareConfigurationProperty( self ) :
		if self.mTunerMgr.GetOriginalTunerConfig( ) != self.mTunerMgr.GetCurrentTunerConfig( ) :
			return False
		return True

