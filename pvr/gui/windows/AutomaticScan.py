from pvr.gui.WindowImport import *


class AutomaticScan( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mSatelliteIndex = 0
		self.mFormattedList = None
		self.mConfiguredSatelliteList = None


	def onInit(self) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		self.SetSettingWindowLabel( 'Automatic Scan' )

		self.mSatelliteIndex = 0
		self.mFormattedList = None
		self.mConfiguredSatelliteList = None		

		self.LoadFormattedSatelliteNameList( )

		if self.mConfiguredSatelliteList and self.mConfiguredSatelliteList[0].mError == 0 :
			if self.getControl( E_SETTING_DESCRIPTION ).getLabel( ) == 'Has no configured satellite' :
				hideControlIds = [ E_Input01, E_Input02, E_SpinEx01, E_SpinEx02 ]
				self.SetVisibleControls( hideControlIds, True )
			self.InitConfig( )
			self.mInitialized = True
			self.SetFocusControl( E_Input01 )
		else :
			hideControlIds = [ E_Input01, E_Input02, E_SpinEx01, E_SpinEx02 ]
			self.SetVisibleControls( hideControlIds, False )
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Has no configured satellite' )
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( 'ERROR', 'Has No Configurd Satellite' )
 			dialog.doModal( )
			WinMgr.GetInstance().CloseWindow( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		self.GlobalAction( actionId )
		
		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.ResetAllControl( )
			WinMgr.GetInstance().CloseWindow( )
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			WinMgr.GetInstance().CloseWindow( )

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
			select =  dialog.select( 'Select satellite', self.mFormattedList )

			if select >= 0 and select != self.mSatelliteIndex :
				self.mSatelliteIndex = select
			self.SetControlLabel2String( E_Input01, self.mFormattedList[ self.mSatelliteIndex ] )

		# Start Search
		if groupId == E_Input02 :
			if self.mSatelliteIndex == 0 :
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
				dialog.SetConfiguredSatellite( self.mConfiguredSatelliteList )
				dialog.doModal( )

			else :
				configuredSatelliteList = []
				config = self.mConfiguredSatelliteList[ self.mSatelliteIndex - 1 ]

				configuredSatelliteList.append( config )
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
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
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Has no configured satellite' )

		else :
			try :
				self.AddInputControl( E_Input01, 'Satellite', self.mFormattedList[self.mSatelliteIndex], 'Select satellite' )
				self.AddEnumControl( E_SpinEx01, 'Network Search', None, 'Network Search' )
				self.AddEnumControl( E_SpinEx02, 'Channel Search Mode', None, 'Channel Search Mode' )
				self.AddInputControl( E_Input02, 'Start Search', '','Start Search' )
				self.InitControl( )
			except Exception, ex :
				LOG_TRACE('Error exception[%s]'% ex)
	
	def LoadFormattedSatelliteNameList( self ) :
		self.mConfiguredSatelliteList = self.mDataCache.Satellite_GetConfiguredList( )
		if self.mConfiguredSatelliteList and self.mConfiguredSatelliteList[0].mError == 0 :
			pass
		else :
 			return
		self.mFormattedList = []
		self.mFormattedList.append( 'All' )

		for config in self.mConfiguredSatelliteList :
			self.mFormattedList.append( self.mDataCache.GetFormattedSatelliteName( config.mLongitude, config.mBand ) )
		
