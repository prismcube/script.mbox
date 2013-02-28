from pvr.gui.WindowImport import *
import pvr.ScanHelper as ScanHelper


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
		self.mNetworkSearch			= 1
		self.mSearchMode			= 0

			
	def onInit( self ) :
		self.SetActivate( True )
		
		self.SetFrontdisplayMessage( 'Edit Transponder' )		
		self.mWinId = xbmcgui.getCurrentWindowId( )

		self.SetSettingWindowLabel( MR_LANG( 'Edit Transponder' ) )
		self.VisibleTuneStatus( False )

		hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07, E_Input08 ]
		if self.mDataCache.GetEmptySatelliteInfo( ) == True :
			self.SetVisibleControls( hideControlIds, False )
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( MR_LANG( 'No satellite data available' ) )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Please reset your device to factory settings' ) )
			dialog.doModal( )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Go to the configuration menu now?' ), MR_LANG( 'When you perform a factory reset,\nall your settings revert to factory defaults' ) )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIGURE, WinMgr.WIN_ID_MAINMENU )
			else :
				WinMgr.GetInstance( ).CloseWindow( )
		else :
			self.mNetworkSearch = ElisPropertyEnum( 'Network Search', self.mCommander ).GetProp( )
			self.mSearchMode = ElisPropertyEnum( 'Channel Search Mode', self.mCommander ).GetProp( )
			ElisPropertyEnum( 'Network Search', self.mCommander ).SetProp( 1 )
			ElisPropertyEnum( 'Channel Search Mode', self.mCommander ).SetProp( 0 )
			self.mEventBus.Register( self )
			self.mAvBlankStatus = self.mDataCache.Get_Player_AVBlank( )
			self.mDataCache.Player_AVBlank( True )
			self.SetVisibleControls( hideControlIds, True )
			self.SetPipScreen( )
			self.LoadNoSignalState( )
			self.InitConfig( )
			self.SetFocusControl( E_Input01 )
			self.SetPipLabel( )
			self.mInitialized = True
		

	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.OpenBusyDialog( )
			ElisPropertyEnum( 'Network Search', self.mCommander ).SetProp( self.mNetworkSearch )
			ElisPropertyEnum( 'Channel Search Mode', self.mCommander ).SetProp( self.mSearchMode )
			self.ResetAllControl( )
			self.SetVideoRestore( )
			self.RestoreAvBlank( )
			self.mEventBus.Deregister( self )
			self.mIsStartedScanHelper = False
			ScanHelper.GetInstance( ).ScanHelper_Stop( self )
			self.CloseBusyDialog( )
			WinMgr.GetInstance( ).CloseWindow( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT :
			pass

		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass
			
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
		if self.IsActivate( ) == False  :
			return
	
		groupId = self.GetGroupId( aControlId )
		
		# Select Satellite
		if groupId == E_Input01 :
			satelliteList = self.mDataCache.GetFormattedSatelliteNameList( )
			dialog = xbmcgui.Dialog( )
			select = dialog.select( MR_LANG( 'Select Satellite' ), satelliteList, False, StringToListIndex( satelliteList, self.GetControlLabel2String( E_Input01 ) ) )

			if select >= 0 and select != self.mSatelliteIndex :
				self.mSatelliteIndex = select
				self.mTransponderIndex = 0
				self.InitConfig( )

		# Select frequency
		elif groupId == E_Input02 :
			if self.mTransponderList and self.mTransponderList[0].mError == 0 :
				frequencylist = []
				for i in range( len( self.mTransponderList ) ) :
					frequencylist.append( '%d MHz' % self.mTransponderList[i].mFrequency )

				dialog = xbmcgui.Dialog( )
				select = dialog.select( MR_LANG( 'Select Frequency' ), frequencylist, False, StringToListIndex( frequencylist, self.GetControlLabel2String( E_Input02 ) ) )

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
			dialog.SetDefaultValue( 0, 0, 0, 0, self.mBand )
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
				
				self.mDataCache.LoadConfiguredTransponder( )
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
					tmplist = []
					tmplist.append( self.mTransponderList[self.mTransponderIndex] )
					ret = self.mCommander.Transponder_Delete( self.mLongitude, self.mBand, tmplist )
					if ret != True :
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Unable to edit the transponder' ) )
						dialog.doModal( )
						self.CloseBusyDialog( )
						return

					# ADD
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
						dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Unable to edit the transponder' ) )
						dialog.doModal( )
						self.CloseBusyDialog( )
						return
					
					self.mDataCache.LoadConfiguredTransponder( )
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
				dialog.SetDialogProperty( MR_LANG( 'Delete transponder' ), MR_LANG( 'Are you sure you want to remove\nthis transponder?' ) )
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
					self.mDataCache.LoadConfiguredTransponder( )			 		
					self.InitConfig( )
					self.CloseBusyDialog( )					
				else :
					return

			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No transponder info available' ), MR_LANG( 'Add a new transponder first' ) )
				dialog.doModal( )

		elif groupId == E_Input08 :
			if self.mTransponderList and self.mTransponderList[0].mError == 0 :
				if self.IsConfiguredSatellite( self.mLongitude, self.mBand ) :
					self.OpenBusyDialog( )
					ScanHelper.GetInstance( ).ScanHelper_Stop( self, False )
					
					transponderList = []
					transponderList.append( self.mTransponderList[self.mTransponderIndex] )

					self.CloseBusyDialog( )
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
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
		if self.IsActivate( ) == False  :
			return
	
		if self.mInitialized == False :
			return
		if self.mLastFocused != aControlId :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId
	

	def InitConfig( self ) :
		self.ResetAllControl( )
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
		self.AddInputControl( E_Input07, MR_LANG( 'Edit Transponder' ), '', MR_LANG( 'Configure your transponder settings' ) )
		self.AddInputControl( E_Input08, MR_LANG( 'Start Channel Search' ), '', MR_LANG( 'Press OK button to start a channel search' ) )
		
		self.InitControl( )
		self.SetEnableControl( E_Input03, False )
		self.SetEnableControl( E_Input04, False )

		visiblecontrolIds = [ E_Input02, E_Input06, E_Input07 ]
		if self.mTransponderList and self.mTransponderList[0].mError == 0 :
			self.SetEnableControls( visiblecontrolIds, True )
		else :
			self.SetEnableControls( visiblecontrolIds, False )

		if self.IsConfiguredSatellite( self.mLongitude, self.mBand ) :
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