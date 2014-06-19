from pvr.gui.WindowImport import *
from pvr.gui.FTIWindow import FTIWindow

E_TUNER_CONFIGURATION_BASE_ID = WinMgr.WIN_ID_TUNER_CONFIGURATION * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 

E_MAIN_LIST_ID		= 9000 + E_TUNER_CONFIGURATION_BASE_ID
E_DESCRIPTION_ID	= 1003 + E_BASE_WINDOW_ID


class TunerConfiguration( FTIWindow ) :
	def __init__( self, *args, **kwargs ) :
		FTIWindow.__init__( self, *args, **kwargs )
		self.mListItems			= []
		self.mConfiguredCount	= 0
		self.mCtrlMainList		= None


	def onInit( self ) :
		self.SetSingleWindowPosition( E_TUNER_CONFIGURATION_BASE_ID )
		self.mCtrlMainList = self.getControl( E_MAIN_LIST_ID )
		self.tunerIndex = self.mTunerMgr.GetCurrentTunerNumber( )	
		headerLabel = MR_LANG( 'Tuner %d Config : %s' ) % ( self.tunerIndex + 1, self.mTunerMgr.GetCurrentTunerTypeString( ) )
		self.SetSettingWindowLabel( headerLabel )
		if self.getProperty( 'IsFTI' ) == 'True' :
			self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'Installation' ), MR_LANG( 'First Installation' ) ) )
		else :
			self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'Installation' ), MR_LANG( 'Antenna Setup' ) ) )
		self.LoadConfigedSatellite( )
		self.SetFTIGuiType( )
		if self.GetFirstInstallation( ) :
			self.setFocusId( E_FIRST_TIME_INSTALLATION_NEXT )
		else :
			self.setFocusId( E_MAIN_LIST_ID )
		self.mInitialized = True


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		if self.GlobalAction( actionId ) :
			return

		if self.GetFirstInstallation( ) :
			self.onActionFTI( actionId )
		else :
			self.onActionNormal( actionId )

		if actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN :
			if focusId == E_MAIN_LIST_ID :
				position = self.mCtrlMainList.getSelectedPosition( )
				desc = self.mListItems[ position ].getLabel2( )
				self.getControl( E_DESCRIPTION_ID ).setLabel( desc )


	def onActionNormal( self, aActionId ) :
		if aActionId == Action.ACTION_PREVIOUS_MENU or aActionId == Action.ACTION_PARENT_DIR :
			self.mCtrlMainList.reset( )
			WinMgr.GetInstance( ).CloseWindow( )


	def onActionFTI( self, aActionId ) :
		if aActionId == Action.ACTION_PREVIOUS_MENU or aActionId == Action.ACTION_PARENT_DIR :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Exit Installation' ), MR_LANG( 'Are you sure you want to quit the first installation?' ), True )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.OpenBusyDialog( )
				self.CloseFTI( )
				self.mCtrlMainList.reset( )
				time.sleep( 3 )
				self.CloseBusyDialog( )
				WinMgr.GetInstance( ).CloseWindow( )


	def onClick( self, aControlId ) :
		if aControlId == E_MAIN_LIST_ID : 
			position = self.mCtrlMainList.getSelectedPosition( )

			if self.mConfiguredCount == position :
				if self.mTunerMgr.GetCurrentTunerType( ) == E_DISEQC_1_0 and self.mConfiguredCount >= E_MAX_SATELLITE_COUNT :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty(  MR_LANG( 'Error' ),  MR_LANG( 'You can only have 4 satellites for DiSEqC 1.0' ) )
		 			dialog.doModal( )
		 		elif self.mTunerMgr.GetCurrentTunerType( ) == E_SIMPLE_LNB and self.mConfiguredCount > 0 :
		 			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty(  MR_LANG( 'Error' ),  MR_LANG( 'You can only have 1 satellite for Simple LNB' ) )
		 			dialog.doModal( )
				else :
					dialog = xbmcgui.Dialog( )
					satelliteList = self.mDataCache.GetFormattedSatelliteNameList( )
					ret = dialog.select(  MR_LANG( 'Add Satellite' ), satelliteList )

					if ret >= 0 :
						self.OpenBusyDialog( )
						satellite = self.mDataCache.GetSatelliteByIndex( ret )
						
						if self.mTunerMgr.CheckSameSatellite( satellite.mLongitude, satellite.mBand ) :
							self.mTunerMgr.AddConfiguredSatellite( ret )
							self.AfterAction( )
							if self.GetFirstInstallation( ) :
								bakupCount = self.GetAntennaCurrentCount( )
								self.MakeAntennaSetupStepList( )
								self.SetAntennaCurrentCount( bakupCount )
					 	else :
					 		self.CloseBusyDialog( )
					 		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
							dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Same name of satellite already exists' ) )
				 			dialog.doModal( )

	 		elif self.mConfiguredCount + 1 == position :
	 			if self.mConfiguredCount <= 0 :
	 				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty(  MR_LANG( 'Error' ),  MR_LANG( 'No configured satellite available' ) )
		 			dialog.doModal( )
	 			else :
					dialog = xbmcgui.Dialog( )
					satelliteList = []
					for i in range( len( self.mListItems ) ) :
						satelliteList.append( self.mListItems[i].getLabel( ) )
						
					ret = dialog.select(  MR_LANG( 'Delete Satellite' ), satelliteList[ 0 : self.mConfiguredCount ] )
 
		 			if ret >= 0 :
		 				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
						dialog.SetDialogProperty(  MR_LANG( 'Delete Satellite' ),  MR_LANG( 'Are you sure you want to remove%s%s?' ) % ( NEW_LINE, satelliteList[ ret ] ) )
						dialog.doModal( )

						if dialog.IsOK( ) == E_DIALOG_STATE_YES :
							self.OpenBusyDialog( )
							self.mTunerMgr.DeleteConfiguredSatellitebyIndex( ret )
							self.AfterAction( )
							if self.GetFirstInstallation( ) :
								bakupCount = self.GetAntennaCurrentCount( )
								self.MakeAntennaSetupStepList( )
								self.SetAntennaCurrentCount( bakupCount )

			else :
				if self.GetFirstInstallation( ) :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty(  MR_LANG( 'Attention' ),  MR_LANG( 'Press Next button to setup satellites' ) )
		 			dialog.doModal( )
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

						elif tunertype == E_MOTORIZE_USALS or tunertype == E_SIMPLE_LNB :
							WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_SIMPLE )

					else :
						LOG_ERR( 'ERR : Could not find configured satellite' )

		elif aControlId == E_FIRST_TIME_INSTALLATION_PREV :
			self.OpenBusyDialog( )
			WinMgr.GetInstance( ).ShowWindow( self.GetAntennaPrevStepWindowId( ), WinMgr.WIN_ID_MAINMENU )

		elif aControlId == E_FIRST_TIME_INSTALLATION_NEXT :
			self.OpenBusyDialog( )
			WinMgr.GetInstance( ).ShowWindow( self.GetAntennaNextStepWindowId( ), WinMgr.WIN_ID_MAINMENU )


	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return

		if aControlId == E_FIRST_TIME_INSTALLATION_PREV :
			self.getControl( E_DESCRIPTION_ID ).setLabel( MR_LANG( 'Go back to the previous satellite configuration page' ) )
		elif aControlId == E_FIRST_TIME_INSTALLATION_NEXT :
			if self.GetIsLastStep( ) :
				self.getControl( E_DESCRIPTION_ID ).setLabel( MR_LANG( 'Go to the Channel Search page' ) )
			else :
				self.getControl( E_DESCRIPTION_ID ).setLabel( MR_LANG( 'Go to the next satellite configuration page' ) )


	def LoadConfigedSatellite( self ) :
		configuredList = []
		self.mListItems = []

		configuredList = self.mTunerMgr.GetConfiguredSatelliteList( )
		self.mConfiguredCount = 0

		if len( configuredList ) > 0 :
			for config in configuredList :
				if config.mIsConfigUsed == 1 :
					self.mConfiguredCount = self.mConfiguredCount + 1
					satelliteName = self.mDataCache.GetFormattedSatelliteName( config.mSatelliteLongitude, config.mBandType )

					if self.GetFirstInstallation( ) :
						description = MR_LANG( 'Press Next button to setup satellites' )
					else :
						description = MR_LANG( 'Press OK button to setup %s' ) % satelliteName

					self.mListItems.append( xbmcgui.ListItem( '%s' % satelliteName, description ) )

		self.mListItems.append( xbmcgui.ListItem( MR_LANG( 'Add Satellite' ), MR_LANG( 'Add a new satellite to your satellite list' ) ) )
		self.mListItems.append( xbmcgui.ListItem( MR_LANG( 'Delete Satellite' ), MR_LANG( 'Delete a satellite from your list' ) ) )
		self.mCtrlMainList.addItems( self.mListItems )
		self.getControl( E_DESCRIPTION_ID ).setLabel( self.mListItems[0].getLabel2( ) )


	def AfterAction( self ) :
		self.mTunerMgr.SaveConfiguration( )
		self.mDataCache.Channel_ReTune( )
		self.LoadConfigedSatellite( )
		self.CloseBusyDialog( )

