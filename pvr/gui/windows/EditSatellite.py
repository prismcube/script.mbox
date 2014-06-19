from pvr.gui.WindowImport import *


E_EDIT_SATELLITE_BASE_ID				=  WinMgr.WIN_ID_EDIT_SATELLITE * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID


class EditSatellite( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mSatelliteIndex	= 0
		self.mLongitude			= 0
		self.mBand				= 0
		self.mName				= None


	def onInit( self ) :
		self.SetSingleWindowPosition( E_EDIT_SATELLITE_BASE_ID )
		self.SetFrontdisplayMessage( MR_LANG('Edit Satellite') )
		self.mName = MR_LANG( 'Unknown' )
		self.SetSettingWindowLabel( MR_LANG( 'Edit Satellite' ) )
		self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'Installation' ), MR_LANG( 'Edit Satellite' ) ) )

		hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
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
			self.SetVisibleControls( hideControlIds, True )
			self.SetPipScreen( )
			#self.LoadNoSignalState( )
			self.InitConfig( )
			#self.SetFocusControl( E_Input01 )
			self.SetDefaultControl( )
			#self.SetPipLabel( )
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
			select = dialog.select( MR_LANG( 'Select Satellite' ), satelliteList, False, self.mSatelliteIndex )
			if select >= 0 and select != self.mSatelliteIndex :
				self.mSatelliteIndex = select
				self.InitConfig( )

		# Edit Satellite Name
		elif groupId == E_Input03 :
			kb = xbmc.Keyboard( self.mName, MR_LANG( 'Enter New Satellite Name' ), False )
			kb.setHiddenInput( False )
			kb.doModal( )
			if kb.isConfirmed( ) :
				self.OpenBusyDialog( )
				ret = self.mCommander.Satellite_ChangeName( self.mLongitude, self.mBand, kb.getText( ) )
				if ret :
					self.mDataCache.LoadAllSatellite( )
					self.InitConfig( )
					self.CloseBusyDialog( )
		 		else :
		 			self.CloseBusyDialog( )
		 			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Unable to change satellite name' ) )
		 			dialog.doModal( )
 				
		# Add New Satellite
		elif groupId == E_Input04 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_ADD_NEW_SATELLITE )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				longitude, band, satelliteName = dialog.GetValue( )
				if self.CheckSameAllSatellite( longitude, band ) == True :
					self.OpenBusyDialog( )
					ret = self.mCommander.Satellite_Add( longitude, band, satelliteName )
					if ret :
						self.mDataCache.LoadAllSatellite( )
						self.mSatelliteIndex = self.GetEditedPosition( longitude, band )
						self.InitConfig( )
						self.CloseBusyDialog( )
			 		else :
			 			self.CloseBusyDialog( )
			 			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Unable to add a new satellite in the list' ) )
			 			dialog.doModal( )
			 	else :
			 		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Same satellite already exists' ) )
		 			dialog.doModal( )
				 
		# Delete Satellite
		elif groupId == E_Input05 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Delete Satellite' ), MR_LANG( 'Are you sure you want to remove%s this satellite?' )% NEW_LINE )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				if self.CheckConfiguredSatellite( self.mLongitude, self.mBand ) == False :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Unable to remove the satellite from the list' ), MR_LANG( 'Delete configured satellite first' ) )
		 			dialog.doModal( )
					return
				self.OpenBusyDialog( )
				ret = self.mCommander.Satellite_Delete( self.mLongitude, self.mBand )
				if ret :
					self.mSatelliteIndex = 0
					self.mDataCache.LoadAllSatellite( )
					self.mDataCache.Channel_DeleteBySatellite( self.mLongitude, self.mBand )
					self.mDataCache.Channel_ReLoad( )
					self.mDataCache.LoadConfiguredSatellite( )
					self.mDataCache.LoadAllTransponder( )
					self.InitConfig( )
					self.CloseBusyDialog( )
		 		else :
		 			self.CloseBusyDialog( )
		 			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Unable to remove the satellite from the list' ) )
		 			dialog.doModal( )


	def onFocus( self, aControlId ):
		if self.mInitialized :
			self.ShowDescription( aControlId )


	def InitConfig( self ) :
		self.ResetAllControl( )
		self.GetSatelliteInfo( self.mSatelliteIndex )
		satellitename = self.mDataCache.GetFormattedSatelliteName( self.mLongitude , self.mBand )

		self.AddInputControl( E_Input01, MR_LANG( 'Satellite' ), satellitename, MR_LANG( 'Select a satellite you want to change settings' ) )
		longitude = self.GetFormattedLongitude( self.mLongitude , self.mBand )
		self.AddInputControl( E_Input02, MR_LANG( 'Longitude' ), longitude )
		self.AddInputControl( E_Input03, MR_LANG( 'Rename' ), '', MR_LANG( 'Change the name of the satellite you selected' ) )
		self.AddInputControl( E_Input04, MR_LANG( 'Add Satellite' ), '', MR_LANG( 'Add a new satellite to the list' ) )
		self.AddInputControl( E_Input05, MR_LANG( 'Delete Satellite' ), '', MR_LANG( 'Delete a satellite from the list' ) )
		
		self.InitControl( )
		self.SetEnableControl( E_Input02, False )
		self.DisableControl( )
		self.mInitialized = True
		self.SetDefaultControl( )


	def	GetSatelliteInfo( self, aIndex ) :
		satellite = self.mDataCache.GetSatelliteByIndex( aIndex )
		self.mLongitude = satellite.mLongitude
		self.mBand		= satellite.mBand
		self.mName		= satellite.mName

		
	def DisableControl( self ) :		
		if self.mSatelliteIndex == 0 :
			self.SetEnableControl( E_Input05, False )
		else :
			self.SetEnableControl( E_Input05, True )


	def GetFormattedLongitude( self, aLongitude, aBand ) :
		dir = 'E'
		tmpLongitude = aLongitude
		if tmpLongitude > 1800 :
			dir = 'W'
			tmpLongitude = 3600 - tmpLongitude

		formattedName = '%d.%d %s' % ( int( tmpLongitude / 10 ), tmpLongitude % 10, dir )
		return formattedName


	def CheckSameAllSatellite( self, aLongitude, aBand ) :
		AllSatelliteList = self.mDataCache.GetAllSatelliteList( )
		for satellite in AllSatelliteList :
			if satellite.mLongitude == aLongitude and satellite.mBand == aBand :
				return False
		return True


	def CheckConfiguredSatellite( self, aLongitude, aBand ) :
		configuredSatelliteList = self.mDataCache.Satellite_GetConfiguredList( )
		if configuredSatelliteList and configuredSatelliteList[0].mError == 0 :
			for satellite in configuredSatelliteList :
				if satellite.mLongitude == aLongitude and satellite.mBand == aBand :
					return False
			return True
		else :
			return True


	def GetEditedPosition( self, aLongitude, aBand ) :
		satellitelist = self.mDataCache.GetAllSatelliteList( )
		for i in range( len( satellitelist ) ) :
			if satellitelist[i].mLongitude == aLongitude and satellitelist[i].mBand == aBand :
				return i

		return 0
