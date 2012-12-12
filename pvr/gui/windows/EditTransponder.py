from pvr.gui.WindowImport import *


class EditTransponder( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mTransponderList	= []
		self.mSatelliteIndex	= 0
		self.mTransponderIndex	= 0
		self.mLongitude			= 0
		self.mBand				= 0

			
	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.SetSettingWindowLabel( MR_LANG( 'Edit Transponder' ) )

		hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
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
			self.SetVisibleControls( hideControlIds, True )
			self.SetPipScreen( )
			self.LoadNoSignalState( )
			self.InitConfig( )
			self.SetFocusControl( E_Input01 )
			self.SetPipLabel( )
			self.mInitialized = True
		

	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			self.SetVideoRestore( )
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
			

	def onClick( self, aControlId ) :
		groupId = self.GetGroupId( aControlId )
		
		# Select Satellite
		if groupId == E_Input01 :
			satelliteList = self.mDataCache.GetFormattedSatelliteNameList( )
			dialog = xbmcgui.Dialog( )
			select = dialog.select( MR_LANG( 'Select Satellite' ), satelliteList, False, StringToListIndex( satelliteList, self.GetControlLabel2String( E_Input01 ) ) )

			if select >= 0 and select != self.mSatelliteIndex :
				self.mSatelliteIndex = select
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
					return
				self.mTransponderIndex = 0
				self.mDataCache.LoadConfiguredTransponder( )
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

		
	def onFocus( self, aControlId ) :
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
		self.mTransponderList.sort( self.ByFrequency )

		if self.mTransponderList and self.mTransponderList[0].mError == 0 :
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
		
		self.InitControl( )
		self.SetEnableControl( E_Input03, False )
		self.SetEnableControl( E_Input04, False )

		visiblecontrolIds = [ E_Input02, E_Input06, E_Input07 ]
		if self.mTransponderList and self.mTransponderList[0].mError == 0 :
			self.SetEnableControls( visiblecontrolIds, True )
		else :
			self.SetEnableControls( visiblecontrolIds, False )


	def	GetSatelliteInfo( self, aIndex ) :
		satellite = self.mDataCache.GetSatelliteByIndex( aIndex )
		self.mLongitude = satellite.mLongitude
		self.mBand		= satellite.mBand


	def ByFrequency( self, aArg1, aArg2 ) :
		return cmp( aArg1.mFrequency, aArg2.mFrequency )
