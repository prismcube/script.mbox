from pvr.gui.WindowImport import *


E_MAIN_LIST_ID = 9000


class TunerConfiguration( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs)
		self.mListItems = []
		self.mConfiguredCount = 0


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.tunerIndex = self.mTunerMgr.GetCurrentTunerNumber( )	
		headerLabel = MR_LANG( 'Tuner %d Config : %s' ) % ( self.tunerIndex + 1, self.mTunerMgr.GetCurrentTunerTypeString( ) )		
		self.SetSettingWindowLabel( headerLabel )
		self.LoadNoSignalState( )
		self.LoadConfigedSatellite( )
		self.SetPipLabel( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		self.GlobalAction( actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.getControl( E_MAIN_LIST_ID ).reset( )
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass			

		elif actionId == Action.ACTION_MOVE_LEFT or actionId == Action.ACTION_MOVE_RIGHT :
			pass

		elif actionId == Action.ACTION_MOVE_UP :
			pass

		elif actionId == Action.ACTION_MOVE_DOWN :
			pass


	def onClick( self, aControlId ) :
		if aControlId == E_MAIN_LIST_ID : 
			position = self.getControl( E_MAIN_LIST_ID ).getSelectedPosition( )

			if self.mConfiguredCount == position :
				if self.mTunerMgr.GetCurrentTunerType( ) == E_DISEQC_1_0 and self.mConfiguredCount > 3 :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty(  MR_LANG( 'Attention' ),  MR_LANG( 'You can only have 4 satellites for DiSEqC 1.0' ) )
		 			dialog.doModal( )
				else :
					dialog = xbmcgui.Dialog( )
					satelliteList = self.mDataCache.GetFormattedSatelliteNameList( )
	 				ret = dialog.select(  MR_LANG( 'Add Satellite' ), satelliteList )

					if ret >= 0 :
						self.OpenBusyDialog( )
						if self.CheckSameSatellite( ret ) :
							self.mTunerMgr.AddConfiguredSatellite( ret )
							self.AfterAction( )
					 	else :
					 		self.CloseBusyDialog( )
					 		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
							dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Same satellite already configured' ) )
				 			dialog.doModal( )

	 		elif self.mConfiguredCount + 1 == position :
	 			if self.mConfiguredCount <= 0 :
	 				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty(  MR_LANG( 'Error' ),  MR_LANG( 'There is no satellite left in the list' ) )
		 			dialog.doModal( )
	 			else :
					dialog = xbmcgui.Dialog( )
					satelliteList = []
					for i in range( len( self.mListItems ) ) :
						satelliteList.append( self.mListItems[i].getLabel( ) )
						
		 			ret = dialog.select(  MR_LANG( 'Delete Satellite' ), satelliteList[ 0 : self.mConfiguredCount ] )
 
		 			if ret >= 0 :
		 				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
						dialog.SetDialogProperty(  MR_LANG( 'Delete Satellite' ),  MR_LANG( 'Do you want to remove %s?' ) % satelliteList[ ret ] )						
						dialog.doModal( )

						if dialog.IsOK( ) == E_DIALOG_STATE_YES :
							self.OpenBusyDialog( )
							self.mTunerMgr.DeleteConfiguredSatellitebyIndex( ret )
							self.AfterAction( )

			else :
				config = self.mTunerMgr.GetConfiguredSatelliteList( )[ position ]
				if config :
					self.mTunerMgr.SetCurrentConfigIndex( position )
					tunertype = self.mTunerMgr.GetCurrentTunerType( )

					if tunertype == E_DISEQC_1_0 :
						WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_DISEQC_10 )

					elif tunertype == E_DISEQC_1_1 :
						WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_DISEQC_11 )

					elif tunertype == E_MOTORIZE_1_2 :
						WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_MOTORIZED_12 )

					elif tunertype == E_MOTORIZE_USALS :
						WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_SIMPLE )

				else :
					LOG_ERR( 'ERR : Can not find configured satellite' )


	def onFocus( self, aControlId ) :
		pass


	def LoadConfigedSatellite( self ) :
		configuredList = []
		self.mListItems = []

		configuredList = self.mTunerMgr.GetConfiguredSatelliteList( )
		self.mConfiguredCount = 0

		for config in configuredList :
			if config.mIsConfigUsed == 1 :
				self.mConfiguredCount = self.mConfiguredCount + 1
				satelliteName = self.mDataCache.GetFormattedSatelliteName( config.mSatelliteLongitude, config.mBandType )
				self.mListItems.append( xbmcgui.ListItem( '%s' % satelliteName, MR_LANG( 'Press the OK button to setup %s' ) % satelliteName ) )

		self.mListItems.append( xbmcgui.ListItem( MR_LANG( 'Add Satellite' ), MR_LANG( 'Add a new satellite to your satellite list' ) ) )
		self.mListItems.append( xbmcgui.ListItem( MR_LANG( 'Delete Satellite' ), MR_LANG( 'Delete a satellite from your list' ) ) )
		self.getControl( E_MAIN_LIST_ID ).addItems( self.mListItems )


	def AfterAction( self ) :
		self.mTunerMgr.SatelliteConfigSaveList( )
		self.ReTune( )
		self.mDataCache.LoadConfiguredSatellite( )
		self.mDataCache.LoadConfiguredTransponder( )
		self.LoadConfigedSatellite( )
		self.CloseBusyDialog( )


	def ReTune( self ) :
		iChannel = self.mDataCache.Channel_GetCurrent( )
		if iChannel :
			self.mDataCache.Channel_InvalidateCurrent( )
			self.mDataCache.Channel_SetCurrentSync( iChannel.mNumber, iChannel.mServiceType )


	def CheckSameSatellite( self, aIndex ) :
		ConfiguredSatelliteList = self.mTunerMgr.GetConfiguredSatelliteList( )
		AllSatelliteList = self.mDataCache.GetAllSatelliteList( )
		for satellite in ConfiguredSatelliteList :
			if satellite.mSatelliteLongitude == AllSatelliteList[aIndex].mLongitude and satellite.mBandType == AllSatelliteList[aIndex].mBand :
				return False
		return True