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

		self.SetSettingWindowLabel( 'Edit Transponder' )	

		if self.mDataCache.GetEmptySatelliteInfo( ) == True :
			hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Has no configured satellite' )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( 'Error', 'Satellite Infomation is empty. Please Reset STB' )
			dialog.doModal( )
			WinMgr.GetInstance().CloseWindow( )
		else :
			if self.getControl( E_SETTING_DESCRIPTION ).getLabel( ) == 'Has no configured satellite' :
				hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
				self.SetVisibleControls( hideControlIds, True )
			self.SetPipScreen( )
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
			WinMgr.GetInstance().CloseWindow( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			self.SetVideoRestore( )
			WinMgr.GetInstance().CloseWindow( )

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
 			select = dialog.select( 'Select satellite', satelliteList )

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
	 			select = dialog.select( 'Select Transponder', frequencylist )

	 			if select >= 0 and select != self.mTransponderIndex :
		 			self.mTransponderIndex = select
		 			self.InitConfig( )

	 		else :
		 		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'Information', 'Satellite has no transponder info.\nFirst add new transponder' )
	 			dialog.doModal( )

		# Add Transponder
		elif groupId == E_Input05 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SET_TRANSPONDER )
 			dialog.SetDefaultValue( 0, 0, 0, 0, self.mBand )
 			dialog.doModal( )

 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
 				self.OpenBusyDialog( )
				frequency, fec, polarization, simbolrate = dialog.GetValue( )

				# check Already Exist Transponder
 			
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
					dialog.SetDialogProperty( 'ERROR', 'Transponder Add Fail' )
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
						dialog.SetDialogProperty( 'ERROR', 'Transponder Edit Fail' )
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
						dialog.SetDialogProperty( 'ERROR', 'Transponder Edit Fail' )
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
				dialog.SetDialogProperty( 'Information', 'Satellite has no transponder info.\nFirst add new transponder' )
	 			dialog.doModal( )

	 	# Delete Transponder
	 	elif groupId == E_Input06 :
	 		if self.mTransponderList and self.mTransponderList[0].mError == 0 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( 'Confirm', 'Do you want to delete transponder?' )
				dialog.doModal( )

				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					self.OpenBusyDialog( )				
			 		tmplist = []
			 		tmplist.append( self.mTransponderList[self.mTransponderIndex] )
			 		ret = self.mCommander.Transponder_Delete( self.mLongitude, self.mBand, tmplist )
			 		if ret != True :
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( 'ERROR', 'Transponder Delete Fail' )
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
				dialog.SetDialogProperty( 'Information', 'Satellite has no transponder info.\nFirst add new transponder' )
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
		self.AddInputControl( E_Input01, 'Satellite', satellitename, 'Select satellite.' )

		self.mTransponderList = self.mDataCache.GetTransponderListBySatellite( self.mLongitude, self.mBand )

		if self.mTransponderList and self.mTransponderList[0].mError == 0 :
			self.AddInputControl( E_Input02, 'Frequency', '%d MHz' % self.mTransponderList[self.mTransponderIndex].mFrequency, 'Select Frequency.' )
			self.AddInputControl( E_Input03, 'Symbol Rate', '%d KS/s' % self.mTransponderList[self.mTransponderIndex].mSymbolRate )

			property = ElisPropertyEnum( 'Polarisation', self.mCommander )
			self.AddInputControl( E_Input04, 'Polarization', property.GetPropStringByIndex( self.mTransponderList[self.mTransponderIndex].mPolarization ) )
		else :
			self.AddInputControl( E_Input02, 'Frequency', 'None', 'Select Frequency.' )
			self.AddInputControl( E_Input03, 'Symbol Rate', 'None' )
			self.AddInputControl( E_Input04, 'Polarization', 'None' )

		self.AddInputControl( E_Input05, 'Add New Transponder', '', 'Add new transponder.' )
		self.AddInputControl( E_Input06, 'Delete Transponder', '', 'Delete transponder.' )
		self.AddInputControl( E_Input07, 'Edit Transponder', '', 'Edit transponder.' )
		
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
