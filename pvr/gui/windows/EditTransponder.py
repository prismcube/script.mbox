from pvr.gui.WindowImport import *
import pvr.ScanHelper as ScanHelper


E_EDIT_TRANSPONDER_BASE_ID				=  WinMgr.WIN_ID_EDIT_TRANSPONDER * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID


class EditTransponder( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mTransponderList		= []
		self.mSatelliteIndex		= 0
		self.mTransponderIndex		= 0
		self.mLongitude				= 0
		self.mBand					= 0
		self.mIsStartedScanHelper	= False
		self.mAvBlankStatus			= False
		self.mSearchRange			= 0

			
	def onInit( self ) :
		self.SetSingleWindowPosition( E_EDIT_TRANSPONDER_BASE_ID )
		self.SetFrontdisplayMessage( MR_LANG('Edit Transponder') )		
		self.mWinId = xbmcgui.getCurrentWindowId( )

		self.SetSettingWindowLabel( MR_LANG( 'Edit Transponder' ) )
		self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'Installation' ), MR_LANG( 'Edit Transponder') ) )
		
		hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07, E_Input08 ]

		if self.mDataCache.GetEmptySatelliteInfo( ) == True :
			self.SetVisibleControls( hideControlIds, False )
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( MR_LANG( 'No satellite data available' ) )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Please reset your device to factory settings' ) )
			dialog.doModal( )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Go to the configuration menu now?' ), MR_LANG( 'When you perform a factory reset,%s all your settings revert to factory defaults' )% NEW_LINE )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIGURE, WinMgr.WIN_ID_MAINMENU )
			else :
				WinMgr.GetInstance( ).CloseWindow( )
		else :
			self.mEventBus.Register( self )
			self.mAvBlankStatus = self.mDataCache.Get_Player_AVBlank( )
			self.mDataCache.Player_AVBlank( True )
			self.SetVisibleControls( hideControlIds, True )
			self.SetPipScreen( )
			self.InitConfig( )
			self.mInitialized = True
			self.SetDefaultControl( )
		

	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.OpenBusyDialog( )
			self.ResetAllControl( )
			self.mEventBus.Deregister( self )
			self.mIsStartedScanHelper = False
			ScanHelper.GetInstance( ).ScanHelper_Stop( self )
			self.CloseBusyDialog( )
			self.SetVideoRestore( )
			self.RestoreAvBlank( )
			WinMgr.GetInstance( ).CloseWindow( )
			
		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )


	def onEvent( self, aEvent ) :
		if xbmcgui.getCurrentWindowId( ) == self.mWinId :
			if aEvent.getName( ) == ElisEventTuningStatus.getName( ) :
				self.UpdateStatus( aEvent )


	def UpdateStatus( self, aEvent ) :
		freq = self.mDataCache.GetTransponderListByIndex( self.mLongitude, self.mBand, self.mTransponderIndex ).mFrequency
		if aEvent.mFrequency == freq :
			ScanHelper.GetInstance( ).ScanHerper_Progress( self, aEvent.mSignalStrength, aEvent.mSignalQuality, aEvent.mIsLocked )
			if aEvent.mIsLocked :
				if self.mDataCache.Get_Player_AVBlank( ) :
					self.mDataCache.Player_AVBlank( False )
			else :
				if not self.mDataCache.Get_Player_AVBlank( ) :
					self.mDataCache.Player_AVBlank( True )
			

	def onClick( self, aControlId ) :
		groupId = self.GetGroupId( aControlId )
		
		# Select Satellite
		if groupId == E_Input01 :
			satelliteList = self.mDataCache.GetFormattedSatelliteNameList( )
			dialog = xbmcgui.Dialog( )
			select = dialog.select( MR_LANG( 'Select Satellite' ), satelliteList, False, self.mSatelliteIndex )

			if select >= 0 and select != self.mSatelliteIndex :
				self.mSatelliteIndex = select
				self.mTransponderIndex = 0
				self.InitConfig( )

		# Select frequency
		elif groupId == E_Input02 :
			if self.mTransponderList and self.mTransponderList[0].mError == 0 :
				frequencylist = []
				for i in range( len( self.mTransponderList ) ) :
					if self.mTransponderList[i].mPolarization == ElisEnum.E_LNB_HORIZONTAL :
		 				polarization = MR_LANG( 'Horizontal' )
		 			else :
		 				polarization = MR_LANG( 'Vertical' )
					frequencylist.append( '%dMHz   %dKS/s   %s' % ( self.mTransponderList[i].mFrequency, self.mTransponderList[i].mSymbolRate, polarization ) )

				dialog = xbmcgui.Dialog( )
				select = dialog.select( MR_LANG( 'Select Frequency' ), frequencylist, False, self.mTransponderIndex )

				if select >= 0 and select != self.mTransponderIndex :
					self.mTransponderIndex = select
					self.InitConfig( )

			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No transponder info available' ), MR_LANG( 'Add a new transponder first' ) )
				dialog.doModal( )

		# Add Transponder
		elif groupId == E_Input05 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SET_TRANSPONDER )
			dialog.SetDefaultValue( 3000, 0, 0, 1000, self.mBand )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.OpenBusyDialog( )
				frequency, fec, polarization, simbolrate = dialog.GetValue( )

				newTransponder = ElisITransponderInfo( )
				newTransponder.reset( )
				newTransponder.mFrequency = frequency
				newTransponder.mSymbolRate = simbolrate
				newTransponder.mPolarization = polarization
				newTransponder.mFECMode = fec

				tmplist = []
				tmplist.append( newTransponder )
				ret = self.mCommander.Transponder_Add( self.mLongitude, self.mBand, tmplist )
				if ret != True :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Unable to add the transponder' ) )
					dialog.doModal( )
					self.CloseBusyDialog( )
					return
				
				self.mDataCache.LoadAllTransponder( )
				self.mTransponderIndex = self.GetEditedPosition( frequency )
				self.InitConfig( )
				self.CloseBusyDialog( )
			else :
				return

		# Edit Transponder
		elif groupId == E_Input07 :
			if self.mTransponderList and self.mTransponderList[0].mError == 0 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SET_TRANSPONDER )
				dialog.SetDefaultValue( self.mTransponderList[self.mTransponderIndex].mFrequency, self.mTransponderList[self.mTransponderIndex].mFECMode, self.mTransponderList[self.mTransponderIndex].mPolarization, self.mTransponderList[self.mTransponderIndex].mSymbolRate, self.mBand )
				dialog.doModal( )

				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					self.OpenBusyDialog( )

					# ADD
					frequency, fec, polarization, simbolrate = dialog.GetValue( )

					newTransponder = ElisITransponderInfo( )
					newTransponder.reset( )
					newTransponder.mFrequency = frequency
					newTransponder.mSymbolRate = simbolrate
					newTransponder.mPolarization = polarization
					newTransponder.mFECMode = fec

					tmplist_Add = []
					tmplist_Add.append( newTransponder )

					ret = self.mCommander.Transponder_Add( self.mLongitude, self.mBand, tmplist_Add )
					if ret != True :
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Unable to edit the transponder' ) )
						dialog.doModal( )
						self.CloseBusyDialog( )
						return

					# DELETE
					tmplist_Delete = []
					tmplist_Delete.append( self.mTransponderList[self.mTransponderIndex] )
					ret = self.mCommander.Transponder_Delete( self.mLongitude, self.mBand, tmplist_Delete )
					if ret != True :
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Unable to edit the transponder' ) )
						dialog.doModal( )
						self.mCommander.Transponder_Delete( self.mLongitude, self.mBand, tmplist_Add )
					
					self.mDataCache.LoadAllTransponder( )
					self.mTransponderIndex = self.GetEditedPosition( frequency )
					self.InitConfig( )
					self.CloseBusyDialog( )
				else :
					return

			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No transponder info available' ), MR_LANG( 'Add a new transponder first' ) )
				dialog.doModal( )

		# Delete Transponder
		elif groupId == E_Input06 :
			if self.mTransponderList and self.mTransponderList[0].mError == 0 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( MR_LANG( 'Delete Transponder' ), MR_LANG( 'Are you sure you want to remove%s this transponder?' )% NEW_LINE )
				dialog.doModal( )

				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					self.OpenBusyDialog( )
					tmplist = []
					tmplist.append( self.mTransponderList[self.mTransponderIndex] )
					ret = self.mCommander.Transponder_Delete( self.mLongitude, self.mBand, tmplist )
					if ret != True :
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Unable to delete the transponder' ) )
						dialog.doModal( )
						self.CloseBusyDialog( )
						return
					self.mTransponderIndex = 0
					self.mDataCache.LoadAllTransponder( )
					self.InitConfig( )
					self.CloseBusyDialog( )
				else :
					return

			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No transponder info available' ), MR_LANG( 'Add a new transponder first' ) )
				dialog.doModal( )

		elif groupId == E_SpinEx01 :
			self.ControlSelect( )

		elif groupId == E_SpinEx02 :
			self.mSearchRange = self.GetSelectedIndex( E_SpinEx02 )
			return

		elif groupId == E_Input08 :
			if self.mTransponderList and self.mTransponderList[0].mError == 0 :
				if self.IsConfiguredSatellite( self.mLongitude, self.mBand ) :
					self.OpenBusyDialog( )
					ScanHelper.GetInstance( ).ScanHelper_Stop( self, False )
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
					self.CloseBusyDialog( )

					if self.mSearchRange :
						configuredSatelliteList = []
						config = ElisISatelliteInfo( )
						config.mLongitude	= self.mLongitude
						config.mBand		= self.mBand
						config.mName		= self.mDataCache.GetSatelliteName( self.mLongitude, self.mBand )
						configuredSatelliteList.append( config )
						dialog.SetConfiguredSatellite( configuredSatelliteList )
						dialog.doModal( )
						self.mCommander.ScanHelper_Start( )
					else :
						transponderList = []
						transponderList.append( self.mTransponderList[self.mTransponderIndex] )
						dialog.SetTransponder( self.mLongitude, self.mBand, transponderList )
						dialog.doModal( )

					self.setProperty( 'ViewProgress', 'True' )
					self.InitConfig( )

				else :
					satellitename = self.mDataCache.GetFormattedSatelliteName( self.mLongitude , self.mBand )
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Satellite %s is not configured' ) % satellitename, MR_LANG( 'Configure the satellite first before you scan channels' ) )
					dialog.doModal( )
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No transponder info available' ), MR_LANG( 'Add a new transponder first' ) )
				dialog.doModal( )

		
	def onFocus( self, aControlId ) :
		if self.mInitialized :
			self.ShowDescription( aControlId )
	

	def InitConfig( self ) :
		self.ResetAllControl( )
		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( False )
		
		self.GetSatelliteInfo( self.mSatelliteIndex )
		satellitename = self.mDataCache.GetFormattedSatelliteName( self.mLongitude , self.mBand )
		self.AddInputControl( E_Input01, MR_LANG( 'Satellite' ), satellitename, MR_LANG( 'Select a satellite you want to change settings' ) )

		self.mTransponderList = self.mDataCache.GetTransponderListBySatellite( self.mLongitude, self.mBand )

		if self.mTransponderList and self.mTransponderList[0].mError == 0 :
			self.mTransponderList.sort( self.ByFrequency )
			self.AddInputControl( E_Input02, MR_LANG( 'Frequency' ), '%d MHz' % self.mTransponderList[self.mTransponderIndex].mFrequency, MR_LANG( 'Select the frequency of the data stream, in which the channel is encoded' ) )
			self.AddInputControl( E_Input03, MR_LANG( 'Symbol Rate' ), '%d KS/s' % self.mTransponderList[self.mTransponderIndex].mSymbolRate )

			property = ElisPropertyEnum( 'Polarisation', self.mCommander )
			self.AddInputControl( E_Input04, MR_LANG( 'Polarization' ), property.GetPropStringByIndex( self.mTransponderList[self.mTransponderIndex].mPolarization ) )
		else :
			self.AddInputControl( E_Input02, MR_LANG( 'Frequency' ), MR_LANG( 'None' ), MR_LANG( 'Select the frequency of the data stream, in which the channel is encoded' ) )
			self.AddInputControl( E_Input03, MR_LANG( 'Symbol Rate' ), MR_LANG( 'None' ) )
			self.AddInputControl( E_Input04, MR_LANG( 'Polarization' ), MR_LANG( 'None' ) )

		self.AddInputControl( E_Input05, MR_LANG( 'Add Transponder' ), '', MR_LANG( 'Add a new transponder to the list' ) )
		self.AddInputControl( E_Input06, MR_LANG( 'Delete Transponder' ), '', MR_LANG( 'Delete a transponder from the list' ) )
		self.AddInputControl( E_Input07, MR_LANG( 'Edit' ), '', MR_LANG( 'Configure your transponder settings' ) )
		networkSearchDescription = '%s %s' % ( MR_LANG( 'When set to \'Off\', only the factory default transponders of the satellites you previously selected will be scanned for new channels.'), MR_LANG('If you set to \'On\', both the existing transponders and additional transponders that have not yet been stored to be located are scanned for new channels' ) )
		self.AddEnumControl( E_SpinEx01, 'Network Search', None, networkSearchDescription )
		self.AddUserEnumControl( E_SpinEx02, MR_LANG( 'Search Range' ), USER_ENUM_LIST_SEARCH_RANGE, self.mSearchRange, MR_LANG( 'Select the transponder frequency range for channel search' ) )
		self.AddInputControl( E_Input08, MR_LANG( 'Start Channel Search' ), '', MR_LANG( 'Press OK button to start a channel search' ) )
		
		self.InitControl( )
		self.SetEnableControl( E_Input03, False )
		self.SetEnableControl( E_Input04, False )

		visiblecontrolIds = [ E_Input02, E_Input06, E_Input07 ]
		if self.mTransponderList and self.mTransponderList[0].mError == 0 :
			self.SetEnableControls( visiblecontrolIds, True )
		else :
			self.SetEnableControls( visiblecontrolIds, False )
			self.SetDefaultControl( )

		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( True )

		if self.IsConfiguredSatellite( self.mLongitude, self.mBand ) and self.mTransponderList and self.mTransponderList[0].mError == 0 :
			if self.mIsStartedScanHelper == False :
				ScanHelper.GetInstance( ).ScanHelper_Start( self )
				self.mIsStartedScanHelper = True

			configuredsatellite = self.GetConfiguredSatellite( self.mLongitude, self.mBand )
			if configuredsatellite :
				ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, configuredsatellite, self.mTransponderList[self.mTransponderIndex] )
		else :
			if self.mIsStartedScanHelper :
				ScanHelper.GetInstance( ).ScanHelper_Stop( self )
				self.mIsStartedScanHelper = False


	def	GetSatelliteInfo( self, aIndex ) :
		satellite = self.mDataCache.GetSatelliteByIndex( aIndex )
		self.mLongitude = satellite.mLongitude
		self.mBand		= satellite.mBand


	def ByFrequency( self, aArg1, aArg2 ) :
		return cmp( aArg1.mFrequency, aArg2.mFrequency )


	def GetEditedPosition( self, aFrequency ) :
		transponderlist = self.mDataCache.GetTransponderListBySatellite( self.mLongitude, self.mBand )
		transponderlist.sort( self.ByFrequency )
		for i in range( len( transponderlist ) ) :
			if transponderlist[i].mFrequency == aFrequency :
				return i

		return 0


	def IsConfiguredSatellite( self, aLongitude, aBand ) :
		configuredSatelliteList = self.mDataCache.Satellite_GetConfiguredList( )
		if configuredSatelliteList and configuredSatelliteList[0].mError == 0 :
			for satellite in configuredSatelliteList :
				if satellite.mLongitude == aLongitude and satellite.mBand == aBand :
					return True
		else :
			return False
			
		return False


	def GetConfiguredSatellite( self, aLongitude, aBand ) :
		configuredSatellite = self.mDataCache.GetConfiguredSatelliteListByTunerIndex( E_TUNER_1 )
		for satellite in configuredSatellite :
			if satellite.mSatelliteLongitude == aLongitude and satellite.mBandType == aBand :
				return satellite

		configuredSatellite = self.mDataCache.GetConfiguredSatelliteListByTunerIndex( E_TUNER_2 )
		for satellite in configuredSatellite :
			if satellite.mSatelliteLongitude == aLongitude and satellite.mBandType == aBand :
				return satellite

		return None


	def RestoreAvBlank( self ) :
		if self.mAvBlankStatus :
			if not self.mDataCache.Get_Player_AVBlank( ) :
				self.mDataCache.Player_AVBlank( True )
		else :
			if self.mDataCache.Get_Player_AVBlank( ) :
				self.mDataCache.Player_AVBlank( False )
