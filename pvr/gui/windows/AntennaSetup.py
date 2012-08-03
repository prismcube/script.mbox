from pvr.gui.WindowImport import *
import pvr.TunerConfigMgr as ConfigMgr


class AntennaSetup( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.getControl( E_SUBMENU_LIST_ID ).setVisible( False )

		self.SetSettingWindowLabel( 'Antenna & Satellite Setup' )
		self.SetPipScreen( )

		if self.mDataCache.GetEmptySatelliteInfo( ) == True :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( 'Error', 'Satellite Infomation is empty. Please Reset STB' )
			dialog.doModal( )
			WinMgr.GetInstance( ).CloseWindow( )

		if ConfigMgr.GetInstance( ).GetFristInstallation( ) == True :
			self.DrawFirstTimeInstallationStep( E_STEP_ANTENNA )
		else :
			self.DrawFirstTimeInstallationStep( None )

		self.getControl( E_SUBMENU_LIST_ID ).setVisible( True )
		
		if self.mTunerMgr.GetNeedLoad( ) == True : 
			self.mTunerMgr.LoadOriginalTunerConfig( )
			self.mTunerMgr.Load( )
			self.mTunerMgr.SetNeedLoad( False )

		self.AddEnumControl( E_SpinEx01, 'Tuner2 Connect Type', None, 'Select tuner 2 connection type.' )
		self.AddEnumControl( E_SpinEx02, 'Tuner2 Signal Config', None, 'Select tuner 2 configuration.' )
		self.AddEnumControl( E_SpinEx03, 'Tuner1 Type', None, 'Setup tuner 1.' )
		self.AddInputControl( E_Input01, ' - Tuner 1 Configuration', '', 'Go to Tuner 1 Configure.' )
		self.AddEnumControl( E_SpinEx04, 'Tuner2 Type', None, 'Setup tuner 2.' )
		self.AddInputControl( E_Input02, ' - Tuner 2 Configuration','', 'Go to Tuner 2 Configure.' )
		if ConfigMgr.GetInstance( ).GetFristInstallation( ) == True :
			self.AddPrevNextButton( )
			self.getControl( E_FIRST_TIME_INSTALLATION_NEXT_LABEL ).setLabel( 'Next' )
		self.setVisibleButton( )
		self.InitControl( )
		self.DisableControl( )
		self.mInitialized = True
		self.SetFocusControl( E_SpinEx01 )
		
		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )

		self.GlobalAction( actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			if ConfigMgr.GetInstance( ).GetFristInstallation( ) == True :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( 'Are you sure?', 'Do you want to stop first time installation?' )
				dialog.doModal( )

				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					self.OpenBusyDialog( )
					if self.CompareConfigurationSatellite( ) == False or self.CompareConfigurationProperty( ) == False :
						self.CancelConfiguration( )
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_FIRST_INSTALLATION ).mStepNum = E_STEP_SELECT_LANGUAGE
					self.SetParentID( WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_FIRST_INSTALLATION ).GetParentID( ) )
					self.mTunerMgr.SetNeedLoad( True )
					ConfigMgr.GetInstance( ).SetFristInstallation( False )
					self.CloseBusyDialog( )
					self.ResetAllControl( )
					self.SetVideoRestore( )
					WinMgr.GetInstance( ).CloseWindow( )
				elif dialog.IsOK( ) == E_DIALOG_STATE_NO :
					return	
				elif dialog.IsOK( ) == E_DIALOG_STATE_CANCEL :
					return

			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( 'Configure', 'Save Configuration?' )
				dialog.doModal( )

				if dialog.IsOK( ) == E_DIALOG_STATE_CANCEL :
					return

				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					self.OpenBusyDialog( )
					if self.CompareCurrentConfiguredState( ) == False or self.CompareConfigurationProperty( ) == False :
						self.SaveConfiguration( )
					
				elif dialog.IsOK( ) == E_DIALOG_STATE_NO :
					self.OpenBusyDialog( )
					if self.CompareConfigurationSatellite( ) == False or self.CompareConfigurationProperty( ) == False :
						self.CancelConfiguration( )
				self.mTunerMgr.SetNeedLoad( True )
				self.ResetAllControl( )
				self.SetVideoRestore( )
				self.CloseBusyDialog( )
				WinMgr.GetInstance( ).CloseWindow( )
			

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
			if groupId == E_Input01 :
				self.mTunerMgr.SetCurrentTunerIndex( E_TUNER_1 )
				configcontrol = E_SpinEx03

			elif groupId == E_Input02 :
				self.mTunerMgr.SetCurrentTunerIndex( E_TUNER_2 )
				configcontrol = E_SpinEx04

			#if self.CompareConfigurationSatellite( ) == False or self.CompareConfigurationProperty( ) == False :
			if self.CompareCurrentConfiguredState( ) == False :
				self.OpenBusyDialog( )
				self.SaveConfiguration( )
				self.ReTune( )
				self.CloseBusyDialog( )

			if self.GetSelectedIndex( configcontrol ) == E_SIMPLE_LNB :
				self.mTunerMgr.SetCurrentConfigIndex( 0 )
				self.ResetAllControl( )
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
		
		if groupId == E_SpinEx01 or groupId == E_SpinEx02 :
			self.ControlSelect( )
			self.DisableControl( groupId )

		elif groupId == E_SpinEx03 :
			self.ControlSelect( )
			self.DisableControl( groupId )
			self.mTunerMgr.SelectCurrentSatelliteList( E_TUNER_1, ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( ) )

		elif groupId == E_SpinEx04 :
			self.ControlSelect( )
			self.mTunerMgr.SelectCurrentSatelliteList( E_TUNER_2, ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).GetProp( ) )
			

		elif aControlId == E_FIRST_TIME_INSTALLATION_NEXT or aControlId == E_FIRST_TIME_INSTALLATION_PREV :
			self.OpenBusyDialog( )
			if self.CompareConfigurationSatellite( ) == False or self.CompareConfigurationProperty( ) == False :
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


	def DisableControl( self, aControlID = None ) :
		if aControlID == None or aControlID == E_SpinEx01 :
			selectedIndex = ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander ).GetProp( )
			if selectedIndex == E_TUNER_LOOPTHROUGH :
				control = self.getControl( E_SpinEx02 + 3 )
				time.sleep( 0.02 )
				control.selectItem( E_SAMEWITH_TUNER )
				self.SetProp( E_SpinEx02, E_SAMEWITH_TUNER )
				self.SetEnableControl( E_SpinEx02, False )
			else :
				self.SetEnableControl( E_SpinEx02, True )

		if aControlID == None or aControlID == E_SpinEx02 or aControlID == E_SpinEx01 :
			selectedIndex = ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander ).GetProp( )
			if selectedIndex == E_SAMEWITH_TUNER :
				if self.GetSelectedIndex( E_SpinEx03 ) != self.GetSelectedIndex( E_SpinEx04 ) :
					control = self.getControl( E_SpinEx04 + 3 )
					prop = ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( )
					control.selectItem( prop )
					self.SetProp( E_SpinEx04, prop )
				self.SetEnableControl( E_SpinEx04, False )
				self.SetEnableControl( E_Input02, False )
			else :
				self.SetEnableControl( E_SpinEx04, True)
				self.SetEnableControl( E_Input02, True )

		if aControlID == E_SpinEx03 :
			selectedIndex = ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander ).GetProp( )
			if selectedIndex == E_SAMEWITH_TUNER :
				control = self.getControl( E_SpinEx04 + 3 )
				prop = ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( )
				control.selectItem( prop )
				self.SetProp( E_SpinEx04, prop )
				self.SetEnableControl( E_SpinEx04, False )
				self.SetEnableControl( E_Input02, False )


	def setVisibleButton( self ) :
		if ConfigMgr.GetInstance( ).GetFristInstallation( ) == True :
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


	def CompareConfigurationSatellite( self ) :
		configuredList1		= self.mTunerMgr.GetConfiguredSatellitebyTunerIndex( E_TUNER_1 )	
		oriconfiguredList1	= self.mTunerMgr.LoadOriginalSatelliteConfigListByTunerNumber( E_TUNER_1 )
		configuredList2		= self.mTunerMgr.GetConfiguredSatellitebyTunerIndex( E_TUNER_2 ) 
		oriconfiguredList2	= self.mTunerMgr.LoadOriginalSatelliteConfigListByTunerNumber( E_TUNER_2 )
		if oriconfiguredList1 == None or oriconfiguredList2 == None :
			print 'dhkim test CompareConfigurationSatellite False!!!!'
			return False

		if self.mTunerMgr.GetCurrentTunerConfigType( ) == E_SAMEWITH_TUNER :
			if len( configuredList1 ) != len( oriconfiguredList1 ) :
				print 'dhkim test CompareConfigurationSatellite False!!!!'
				return False
		else :
			if len( configuredList1 ) != len( oriconfiguredList1 ) :
				print 'dhkim test CompareConfigurationSatellite False!!!!'
				return False
			if len( configuredList2 ) != len( oriconfiguredList2 ) :
				print 'dhkim test CompareConfigurationSatellite False!!!!'
				return False
			
		if self.mTunerMgr.GetCurrentTunerConfigType( ) == E_SAMEWITH_TUNER :
			for i in range( len( configuredList1 ) ) :
				if configuredList1[i].__dict__ != oriconfiguredList1[i].__dict__ :
					print 'dhkim test CompareConfigurationSatellite False!!!!'
					return False
		else :
			for i in range( len( configuredList1 ) ) :
				if configuredList1[i].__dict__ != oriconfiguredList1[i].__dict__ :
					print 'dhkim test CompareConfigurationSatellite False!!!!'
					return False
			for i in range( len( configuredList2 ) ) :
				if configuredList2[i].__dict__ != oriconfiguredList2[i].__dict__ :
					print 'dhkim test CompareConfigurationSatellite False!!!!'
					return False
		print 'dhkim test CompareConfigurationSatellite True!!!!'
		return True


	def CompareCurrentConfiguredState( self ) :
		configuredList1		= self.mTunerMgr.GetConfiguredSatellitebyTunerIndex( E_TUNER_1 )	
		currentconfiguredList1	= self.mDataCache.GetConfiguredSatelliteListByTunerIndex( E_TUNER_1 )
		configuredList2		= self.mTunerMgr.GetConfiguredSatellitebyTunerIndex( E_TUNER_2 ) 
		currentconfiguredList2	= self.mDataCache.GetConfiguredSatelliteListByTunerIndex( E_TUNER_2 )
		if currentconfiguredList1 == None or currentconfiguredList2 == None :
			print 'dhkim test CompareCurrentConfiguredState False 1 !!!!'
			return False

		if self.mTunerMgr.GetCurrentTunerConfigType( ) == E_SAMEWITH_TUNER :
			if len( configuredList1 ) != len( currentconfiguredList1 ) :
				print 'dhkim test CompareCurrentConfiguredState False 2 !!!!'
				return False
		else :
			if len( configuredList1 ) != len( currentconfiguredList1 ) :
				print 'dhkim test CompareCurrentConfiguredState False 3 !!!!'
				return False
			if len( configuredList2 ) != len( currentconfiguredList2 ) :
				print 'dhkim test CompareCurrentConfiguredState False 4 !!!'
				return False
			
		if self.mTunerMgr.GetCurrentTunerConfigType( ) == E_SAMEWITH_TUNER :
			for i in range( len( configuredList1 ) ) :
				if configuredList1[i].__dict__ != currentconfiguredList1[i].__dict__ :
					print 'dhkim test diff!!!!!!!!!!!!!!!!!'
					configuredList1[i].printdebug( )
					print 'dhkim test ---------------------'
					currentconfiguredList1[i].printdebug( )
					print 'dhkim test CompareCurrentConfiguredState  5 False!!!!'
					return False
		else :
			for i in range( len( configuredList1 ) ) :
				if configuredList1[i].__dict__ != currentconfiguredList1[i].__dict__ :
					print 'dhkim test CompareCurrentConfiguredState  6 False!!!!'
					return False
			for i in range( len( configuredList2 ) ) :
				if configuredList2[i].__dict__ != currentconfiguredList2[i].__dict__ :
					print 'dhkim test CompareCurrentConfiguredState  7 False!!!!'
					return False
		print 'dhkim test CompareCurrentConfiguredState True!!!!'
		return True


	def CompareConfigurationProperty( self ) :
		if self.mTunerMgr.GetOriginalTunerConfig( ) != self.mTunerMgr.GetCurrentTunerConfig( ) :
			print 'dhkim test CompareConfigurationProperty False!!!!'
			return False
		print 'dhkim test CompareConfigurationProperty True!!!!'
		return True
