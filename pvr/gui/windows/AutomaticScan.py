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
		self.LoadNoSignalState( )

		self.mSatelliteIndex = 0
		self.mFormattedList = None
		self.mConfiguredSatelliteList = None		

		self.LoadFormattedSatelliteNameList( )

		hideControlIds = [ E_Input01, E_Input02, E_SpinEx01, E_SpinEx02 ]
		if self.mConfiguredSatelliteList and self.mConfiguredSatelliteList[0].mError == 0 :
			self.SetVisibleControls( hideControlIds, True )
			self.InitConfig( )
			self.mInitialized = True
			self.SetFocusControl( E_Input01 )
		else :
			self.SetVisibleControls( hideControlIds, False )
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( MR_LANG( 'Has no configured satellite' ) )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'ERROR' ), MR_LANG( 'Has No Configurd Satellite' ) )
			dialog.doModal( )
			WinMgr.GetInstance( ).CloseWindow( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		self.GlobalAction( actionId )
		
		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.ResetAllControl( )
			WinMgr.GetInstance( ).CloseWindow( )
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
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
		
		# Satellite
		if groupId == E_Input01 :
			dialog = xbmcgui.Dialog( )
			select =  dialog.select( MR_LANG( 'Select a satellite you want to scan channels' ), self.mFormattedList )			

			if select >= 0 and select != self.mSatelliteIndex :
				self.mSatelliteIndex = select
			self.SetControlLabel2String( E_Input01, self.mFormattedList[ self.mSatelliteIndex ] )

		# Start Search
		if groupId == E_Input02 :
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
					
		if groupId == E_SpinEx01 or groupId == E_SpinEx02 :
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
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( MR_LANG( 'Has no configured satellite' ) )
		else :
			self.AddInputControl( E_Input01, MR_LANG( 'Satellite' ), self.mFormattedList[self.mSatelliteIndex], MR_LANG( 'Select Satellite(s) you wish to search from' ) )
			self.AddEnumControl( E_SpinEx01, 'Network Search', None, MR_LANG( 'Set your STB to scan channels from multiple TPs' ) )
			self.AddEnumControl( E_SpinEx02, 'Channel Search Mode', None, MR_LANG( 'Select the type of channels you want to search for' ) )
			self.AddInputControl( E_Input02, MR_LANG( 'Search Now' ), '', MR_LANG( 'Perform an automatic channel search' ) )
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
		
