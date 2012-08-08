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

		if self.mDataCache.GetEmptySatelliteInfo( ) == True :
			hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( MR_LANG( 'Has no configured satellite' ) )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Satellite Infomation is empty. Please Reset STB' ) )
			dialog.doModal( )
			WinMgr.GetInstance( ).CloseWindow( )
		else :
			hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, True )
			self.SetPipScreen( )
			self.LoadNoSignalState( )
			self.InitConfig( )
			self.mInitialized = True
			self.SetFocusControl( E_Input01 )
		

	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.ResetAllControl( )
			self.SetVideoRestore( )
			WinMgr.GetInstance( ).CloseWindow( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			self.SetVideoRestore( )
			WinMgr.GetInstance( ).CloseWindow( )

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
 			select = dialog.select( MR_LANG( 'Select satellite you want to edit' ), satelliteList )

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
	 			select = dialog.select( MR_LANG( 'Select frequency you want to set to' ), frequencylist )

	 			if select >= 0 and select != self.mTransponderIndex :
		 			self.mTransponderIndex = select
		 			self.InitConfig( )

	 		else :
		 		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Information' ), MR_LANG( 'Satellite has no transponder info.\nFirst add new transponder' ) )
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
					dialog.SetDialogProperty( MR_LANG( 'ERROR' ), MR_LANG( 'Transponder Add Fail' ) )
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
						dialog.SetDialogProperty( MR_LANG( 'ERROR' ), MR_LANG( 'Transponder Edit Fail' ) )
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
						dialog.SetDialogProperty( MR_LANG( 'ERROR' ), MR_LANG( 'Transponder Edit Fail' ) )
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
				dialog.SetDialogProperty( MR_LANG( 'Information' ), MR_LANG( 'Satellite has no transponder info.\nFirst add new transponder' ) )
	 			dialog.doModal( )

	 	# Delete Transponder
	 	elif groupId == E_Input06 :
	 		if self.mTransponderList and self.mTransponderList[0].mError == 0 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( MR_LANG( 'Delete transpnder' ), MR_LANG( 'Do you want to remove this transponder?' ) )
				dialog.doModal( )

				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					self.OpenBusyDialog( )				
			 		tmplist = []
			 		tmplist.append( self.mTransponderList[self.mTransponderIndex] )
			 		ret = self.mCommander.Transponder_Delete( self.mLongitude, self.mBand, tmplist )
			 		if ret != True :
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( MR_LANG( 'ERROR' ), MR_LANG( 'Transponder Delete Fail' ) )
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
				dialog.SetDialogProperty( MR_LANG( 'Information' ), MR_LANG( 'Satellite has no transponder info.\nFirst add new transponder' ) )
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
		self.AddInputControl( E_Input01, MR_LANG( 'Satellite' ), satellitename, MR_LANG( 'Choose a satellite from the list' ) )

		self.mTransponderList = self.mDataCache.GetTransponderListBySatellite( self.mLongitude, self.mBand )

		if self.mTransponderList and self.mTransponderList[0].mError == 0 :
			self.AddInputControl( E_Input02, MR_LANG( 'Frequency' ), '%d MHz' % self.mTransponderList[self.mTransponderIndex].mFrequency, MR_LANG( 'Select a frequency from the list' ) )
			self.AddInputControl( E_Input03, MR_LANG( 'Symbol Rate' ), '%d KS/s' % self.mTransponderList[self.mTransponderIndex].mSymbolRate )

			property = ElisPropertyEnum( 'Polarisation', self.mCommander )
			self.AddInputControl( E_Input04, MR_LANG( 'Polarization' ), property.GetPropStringByIndex( self.mTransponderList[self.mTransponderIndex].mPolarization ) )
		else :
			self.AddInputControl( E_Input02, MR_LANG( 'Frequency' ), MR_LANG( 'None' ), MR_LANG( 'Select a frequency from the list' ) )
			self.AddInputControl( E_Input03, MR_LANG( 'Symbol Rate' ), MR_LANG( 'None' ) )
			self.AddInputControl( E_Input04, MR_LANG( 'Polarization' ), MR_LANG( 'None' ) )

		self.AddInputControl( E_Input05, MR_LANG( 'Add Transponder' ), '', MR_LANG( 'Here you can add a new transponder' ) )
		self.AddInputControl( E_Input06, MR_LANG( 'Delete Transponder' ), '', MR_LANG( 'You can delete a selected transponder here' ) )
		self.AddInputControl( E_Input07, MR_LANG( 'Edit Transponder' ), '', MR_LANG( 'Configure your transponder' ) )
		
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
