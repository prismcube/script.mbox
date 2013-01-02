from pvr.gui.WindowImport import *


class AutomaticScan( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mSatelliteIndex = 0
		self.mFormattedList = None
		self.mConfiguredSatelliteList = None


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		self.SetSettingWindowLabel( 'Automatic Scan' )
		
		self.mSatelliteIndex = 0
		self.mFormattedList = None
		self.mConfiguredSatelliteList = None		

		self.LoadFormattedSatelliteNameList( )

		hideControlIds = [ E_Input01, E_Input02, E_SpinEx01, E_SpinEx02 ]
		if self.mConfiguredSatelliteList and self.mConfiguredSatelliteList[0].mError == 0 :
			self.LoadNoSignalState( )
			self.SetVisibleControls( hideControlIds, True )
			self.InitConfig( )
			self.SetFocusControl( E_Input01 )
			self.SetPipLabel( )
			self.mInitialized = True
		else :
			self.SetVisibleControls( hideControlIds, False )
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( MR_LANG( 'No configured satellite available' ) )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Make sure that the antenna setting is correct' ) )
			dialog.doModal( )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Go to the antenna setup page now?' ), MR_LANG( 'Add satellites and set LNB parameters' ) )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ANTENNA_SETUP, WinMgr.WIN_ID_MAINMENU )
			else :
				WinMgr.GetInstance( ).CloseWindow( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		if self.GlobalAction( actionId ) :
			return
		
		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			WinMgr.GetInstance( ).CloseWindow( )

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
		
		# Satellite
		if groupId == E_Input01 :
			dialog = xbmcgui.Dialog( )
			select =  dialog.select( MR_LANG( 'Select Satellite' ), self.mFormattedList )

			if select >= 0 and select != self.mSatelliteIndex :
				self.mSatelliteIndex = select
			self.SetControlLabel2String( E_Input01, self.mFormattedList[ self.mSatelliteIndex ] )

		# Start Search
		elif groupId == E_Input02 :
			if self.mSatelliteIndex == 0 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
				dialog.SetConfiguredSatellite( self.mConfiguredSatelliteList )
				dialog.doModal( )
			else :
				configuredSatelliteList = []
				config = self.mConfiguredSatelliteList[ self.mSatelliteIndex - 1 ]

				configuredSatelliteList.append( config )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
				dialog.SetConfiguredSatellite( configuredSatelliteList )				
				dialog.doModal( )
		
		elif groupId == E_SpinEx01 or groupId == E_SpinEx02 :
			self.ControlSelect( )


	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return
		if self.mLastFocused != aControlId :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId


	def InitConfig( self ) :
		self.ResetAllControl( )
		count = len( self.mFormattedList )
		if count <= 1 :
			hideControlIds = [ E_Input01, E_SpinEx01, E_SpinEx02, E_Input02 ]
			self.SetVisibleControls( hideControlIds, False )
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( MR_LANG( 'No configured satellite available' ) )
		else :
			self.AddInputControl( E_Input01, MR_LANG( 'Satellite' ), self.mFormattedList[self.mSatelliteIndex], MR_LANG( 'Select the satellite on which the transponder you wish to scan is located' ) )
			self.AddEnumControl( E_SpinEx01, 'Network Search', None, MR_LANG( 'When set to \'Off\', only the factory default transponders of the satellites you previously selected will be scanned for new channels. If you set to \'On\', both the existing transponders and additional transponders that have not yet been stored to be located are scanned for new channels' ) )
			self.AddEnumControl( E_SpinEx02, 'Channel Search Mode', MR_LANG( 'Search Type' ), MR_LANG( 'Select whether you wish to scan free and scrambled, free only or scrambled only' ) )
			self.AddInputControl( E_Input02, MR_LANG( 'Start Search' ), '', MR_LANG( 'Press OK button to start a channel search' ) )
			self.InitControl( )

	
	def LoadFormattedSatelliteNameList( self ) :
		self.mConfiguredSatelliteList = self.mDataCache.Satellite_GetConfiguredList( )
		if self.mConfiguredSatelliteList and self.mConfiguredSatelliteList[0].mError == 0 :
			pass
		else :
			return
		self.mFormattedList = []
		self.mFormattedList.append( MR_LANG( 'All' ) )

		for config in self.mConfiguredSatelliteList :
			self.mFormattedList.append( self.mDataCache.GetFormattedSatelliteName( config.mLongitude, config.mBand ) )
		
