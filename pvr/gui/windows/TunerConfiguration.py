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

		self.tunerIndex = self.mTunerMgr.GetCurrentTunerIndex( )

		if self.tunerIndex == E_TUNER_1 :
			property = ElisPropertyEnum( 'Tuner1 Type', self.mCommander )
		elif self.tunerIndex == E_TUNER_2 : 
			property = ElisPropertyEnum( 'Tuner2 Type', self.mCommander )
		else :
			property = ElisPropertyEnum( 'Tuner1 Type', self.mCommander )
			
		headerLabel = 'Tuner %d Configuration' % ( self.tunerIndex + 1 )

		self.SetSettingWindowLabel( headerLabel )
		
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Tuner %d Configuration : %s' % ( self.tunerIndex + 1, property.GetPropString( ) ) )
		self.InitConfig( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		self.GlobalAction( actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_PARENT_DIR :
			self.getControl( E_MAIN_LIST_ID ).reset( )
			WinMgr.GetInstance().CloseWindow( )

		elif actionId == Action.ACTION_MOVE_LEFT or actionId == Action.ACTION_MOVE_RIGHT :			
			pass
	
		elif actionId == Action.ACTION_MOVE_UP :
			pass

		elif actionId == Action.ACTION_MOVE_DOWN :
			pass


	def onClick( self, aControlId ) :
		if aControlId == E_MAIN_LIST_ID : 
			position = self.getControl( E_MAIN_LIST_ID ).getSelectedPosition( )
			
			configuredList = self.mTunerMgr.GetConfiguredSatelliteList( )

			if self.mConfiguredCount == position :
				if self.mTunerMgr.GetCurrentTunerType( ) == E_DISEQC_1_0 and self.mConfiguredCount > 3 :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( 'ERROR', 'Alreay 4 Satellite Configured' )
		 			dialog.doModal( )
				else :
					dialog = xbmcgui.Dialog( )
					satelliteList = self.mDataCache.GetFormattedSatelliteNameList( )
		 			ret = dialog.select( 'Select satellite', satelliteList )

		 			if ret >= 0 :
		 				self.OpenBusyDialog( )
						self.mTunerMgr.AddConfiguredSatellite( ret )
						self.mTunerMgr.SatelliteConfigSaveList( )
		 				self.ReloadConfigedSatellite( )
		 				self.ReTune( )
		 				self.CloseBusyDialog( )

	 		elif self.mConfiguredCount + 1 == position :
	 			if self.mConfiguredCount <= 0 :
	 				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( 'ERROR', 'Empty Configured Satellite' )
		 			dialog.doModal( )
	 				return
	 			else :
					dialog = xbmcgui.Dialog( )
		 			ret = dialog.select( 'delete satellite', self.mListItems[ 0 : self.mConfiguredCount ] )
 
		 			if ret >= 0 :
		 				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
						dialog.SetDialogProperty( 'Configure', 'Delete Satellite : %s' % self.mListItems[ ret ] )
						dialog.doModal( )

						if dialog.IsOK( ) == E_DIALOG_STATE_YES :
							self.OpenBusyDialog( )
			 				self.mTunerMgr.DeleteConfiguredSatellitebyIndex( ret )
			 				self.mTunerMgr.SatelliteConfigSaveList( )
			 				self.ReTune( )
			 				self.CloseBusyDialog( )
			 				self.ReloadConfigedSatellite( )

			else :		
				config = configuredList[ position ]
				if config :
					self.mTunerMgr.SetCurrentConfigIndex( position )
					self.ResetAllControl( )
					tunertype = self.mTunerMgr.GetCurrentTunerType( )
					
					if tunertype == E_DISEQC_1_0 :
						WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_DISEQC_10 )

					elif tunertype == E_DISEQC_1_1 :
						WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_DISEQC_11 )
					
					elif tunertype == E_MOTORIZE_1_2 :
						WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_MOTORIZED_12 )

					elif tunertype == E_MOTORIZE_USALS :
						WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_MOTORIZED_USALS2 )

				else :
					LOG_ERR( 'ERR : Can not find configured satellite' )


	def onFocus( self, aControlId ) :
		pass


	def InitConfig( self ) :
		self.ReloadConfigedSatellite( )


	def ReloadConfigedSatellite( self ) :
		configuredList = []
		self.mListItems = []

		configuredList = self.mTunerMgr.GetConfiguredSatelliteList( )
		self.mConfiguredCount = 0

		if configuredList :
			for config in configuredList :
				if config.mIsConfigUsed == 1 :
					self.mConfiguredCount = self.mConfiguredCount + 1
					self.mListItems.append( '%s' % self.mDataCache.GetFormattedSatelliteName( config.mSatelliteLongitude, config.mBandType ) )

		self.mListItems.append( 'Add New Satellite' )
		self.mListItems.append( 'Delete Satellite' )
		self.getControl( E_MAIN_LIST_ID ).addItems( self.mListItems )


	def ReTune( self ) :
		iChannel = self.mDataCache.Channel_GetCurrent( )
		if iChannel :
			self.mDataCache.Channel_InvalidateCurrent( )
			self.mDataCache.Channel_SetCurrentSync( iChannel.mNumber, iChannel.mServiceType )
		
