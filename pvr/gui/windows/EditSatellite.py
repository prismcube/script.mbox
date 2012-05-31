from pvr.gui.WindowImport import *


E_DEFAULT_GOURP_ID		= 9000


class EditSatellite( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mSatelliteIndex	= 0
		self.mLongitude			= 0
		self.mBand				= 0
		self.mName				= 'Unkown'
			
	def onInit( self ) :
		self.getControl( E_DEFAULT_GOURP_ID ).setVisible( False )	
		if self.mDataCache.GetEmptySatelliteInfo( ) == True :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( 'Error', 'Satellite Infomation is empty. Please Reset STB' )
			dialog.doModal( )
			WinMgr.GetInstance().CloseWindow( )
			return

		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		
		self.SetPipScreen( )	
		self.InitConfig( )
		self.SetSettingWindowLabel( 'Edit Satellite' )
		self.mInitialized = True
		self.SetFocusControl( E_Input01 )
		self.getControl( E_DEFAULT_GOURP_ID ).setVisible( True )
		
		
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

	 	# Edit Satellite Name
		elif groupId == E_Input03 :
			kb = xbmc.Keyboard( self.mName, 'Satellite Name', False )
			kb.setHiddenInput( False )
			kb.doModal( )
			if kb.isConfirmed( ) :
				ret = self.mCommander.Satellite_ChangeName( self.mLongitude, self.mBand, kb.getText( ) )
				if ret != True :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( 'ERROR', 'Satellite Edit Name Fail' )
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
					dialog.SetDialogProperty( 'ERROR', 'Satellite Add Fail' )
		 			dialog.doModal( )
		 			return
 				self.mDataCache.LoadAllSatellite( )
				self.InitConfig( )
			else :
				return
				 
		# Delete Satellite
		elif groupId == E_Input05 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( 'Confirm', 'Do you want to delete satellite?' )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				ret = self.mCommander.Satellite_Delete( self.mLongitude, self.mBand )
				if ret != True :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( 'ERROR', 'Satellite Delete Fail' )
		 			dialog.doModal( )
		 			return
				self.mSatelliteIndex = 0
				self.mDataCache.LoadAllSatellite( )
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
		self.AddInputControl( E_Input01, 'Satellite', satellitename, 'Select satellite.' )
		longitude = self.GetFormattedLongitude( self.mLongitude , self.mBand )
		self.AddInputControl( E_Input02, 'Longitude', longitude )
		self.AddInputControl( E_Input03, 'Edit Satellite Name', '', 'Edit satellite name.' )
		self.AddInputControl( E_Input04, 'Add New Satellite', '', 'Add new satellite.' )
		self.AddInputControl( E_Input05, 'Delete Satellite', '', 'Delete satellite.' )
		
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