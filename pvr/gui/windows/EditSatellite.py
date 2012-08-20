from pvr.gui.WindowImport import *


class EditSatellite( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mSatelliteIndex	= 0
		self.mLongitude			= 0
		self.mBand				= 0
		self.mName				= MR_LANG( 'Unkown' )


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.SetSettingWindowLabel( MR_LANG( 'Edit Satellite' ) )

		hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
		if self.mDataCache.GetEmptySatelliteInfo( ) == True :
			self.SetVisibleControls( hideControlIds, False )
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( MR_LANG( 'Has no configured satellite' ) )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No satellite infomation is available. Please reset your STB' ) )
			dialog.doModal( )
			WinMgr.GetInstance( ).CloseWindow( )
		else :
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
 			select = dialog.select( MR_LANG( 'Select Satellite' ), satelliteList ) 			

			if select >= 0 and select != self.mSatelliteIndex :
				self.mSatelliteIndex = select
				self.InitConfig( )

		# Edit Satellite Name
		elif groupId == E_Input03 :
			kb = xbmc.Keyboard( self.mName, MR_LANG( 'Enter a new name' ), False )			
			kb.setHiddenInput( False )
			kb.doModal( )
			if kb.isConfirmed( ) :
				ret = self.mCommander.Satellite_ChangeName( self.mLongitude, self.mBand, kb.getText( ) )
				if ret != True :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'You were unable to change the satellite name' ) )
		 			dialog.doModal( )
		 			return
 				self.mDataCache.LoadAllSatellite( )
				self.InitConfig( )

		# Add New Satellite
		elif groupId == E_Input04 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_ADD_NEW_SATELLITE )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				longitude, band, satelliteName = dialog.GetValue( )
				ret = self.mCommander.Satellite_Add( longitude, band, satelliteName )
				if ret != True :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'You were unable to add a new satellite in the list' ) )
		 			dialog.doModal( )
		 			return
 				self.mDataCache.LoadAllSatellite( )
				self.InitConfig( )
			else :
				return
				 
		# Delete Satellite
		elif groupId == E_Input05 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Delete satellite' ), MR_LANG( 'Do you want to remove this satellite?' ) )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				ret = self.mCommander.Satellite_Delete( self.mLongitude, self.mBand )
				if ret != True :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'You were unable to remove the satellite from the list' ) )
		 			dialog.doModal( )
		 			return
				self.mSatelliteIndex = 0
				self.mDataCache.LoadAllSatellite( )
				self.mDataCache.LoadConfiguredSatellite( )
				self.mDataCache.LoadConfiguredTransponder( )
				self.InitConfig( )
			else :
				return


	def onFocus( self, aControlId ):
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
		longitude = self.GetFormattedLongitude( self.mLongitude , self.mBand )
		self.AddInputControl( E_Input02, MR_LANG( 'Longitude' ), longitude )
		self.AddInputControl( E_Input03, MR_LANG( 'Change Satellite Name' ), '', MR_LANG( 'Change the satellite name in the list' ) )
		self.AddInputControl( E_Input04, MR_LANG( 'Add Satellite' ), '', MR_LANG( 'Add a new satellite to the list' ) )
		self.AddInputControl( E_Input05, MR_LANG( 'Delete Satellite' ), '', MR_LANG( 'Delete a satellite from the list' ) )
		
		self.InitControl( )
		self.SetEnableControl( E_Input02, False )
		self.DisableControl( )


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
		tmpLongitude  = aLongitude
		if tmpLongitude > 1800 :
			dir = 'W'
			tmpLongitude = 3600 - aLongitude

		formattedName = '%d.%d %s' % ( int( tmpLongitude / 10 ), tmpLongitude % 10, dir )
		return formattedName
