from pvr.gui.WindowImport import *
from pvr.gui.FTIWindow import FTIWindow

E_CONFIG_ONECABLE_BASE_ID = WinMgr.WIN_ID_CONFIG_ONECABLE * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 


class SatelliteConfigOnecable( FTIWindow ) :
	def __init__( self, *args, **kwargs ) :
		FTIWindow.__init__( self, *args, **kwargs )
		self.mSatelliteCount = 0
		self.mSatelliteNamelist = []
		self.mCurrentSatellite = None
		

	def onInit( self ) :
		self.SetActivate( True )
		
		self.mWinId = xbmcgui.getCurrentWindowId( )

		tunerIndex = self.mTunerMgr.GetCurrentTunerNumber( )
		self.SetSettingWindowLabel( MR_LANG( 'Tuner %d Config : OneCable' ) % ( tunerIndex + 1 ) )
		self.LoadNoSignalState( )
		self.LoadConfigedSatellite( )
		self.mCurrentSatellite = self.mTunerMgr.GetConfiguredSatellitebyIndex( 0 )
		
		self.AddInputControl( E_Input01, MR_LANG( 'Initial Setup' ), '', MR_LANG( 'Configure the initial settings for OneCable' ) )
		
		listitem = []
		for i in range( MAX_SATELLITE_CNT_ONECABLE ) :
			listitem.append( '%d' % ( i + 1 ) )

		self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Number of Satellites' ), listitem, 0, MR_LANG( 'Select number of satellites for OneCable' ) )

		startId = E_Input02
		for i in range( MAX_SATELLITE_CNT_ONECABLE ) :
			self.AddInputControl( startId, MR_LANG( 'Satellite %d' ) % ( i + 1 ), self.mSatelliteNamelist[i], MR_LANG( 'Press OK button to setup %s' ) % (self.mSatelliteNamelist[i]) )
			startId += 100

		if self.GetFirstInstallation( ) :
			self.SetFTIPrevNextButton( )
			self.SetEnableControl( E_Input01, False )
		else :
			self.SetEnableControl( E_Input01, True )

		self.InitControl( )
		self.getControl( E_SpinEx01 + 3 ).selectItem( self.mSatelliteCount - 1 )
		time.sleep( 0.2 )
		self.DisableControl( )
		self.setDefaultControl( )
		self.SetPipLabel( )
		self.SetFTIGuiType( )
		self.mInitialized = True


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			if self.GetFirstInstallation( ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( MR_LANG( 'Exit installation' ), MR_LANG( 'Are you sure you want to quit the first installation?' ) )
				dialog.doModal( )

				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					self.OpenBusyDialog( )
					self.CloseAction( )
					self.CloseFTI( )
					self.ResetAllControl( )
					self.CloseBusyDialog( )
					WinMgr.GetInstance( ).CloseWindow( )
			else :
				self.CloseAction( )
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
		if self.IsActivate( ) == False  :
			return
	
		groupId = self.GetGroupId( aControlId )

		if aControlId == E_FIRST_TIME_INSTALLATION_PREV :
			self.OpenBusyDialog( )
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( self.GetAntennaPrevStepWindowId( ), WinMgr.WIN_ID_MAINMENU )
			return

		elif aControlId == E_FIRST_TIME_INSTALLATION_NEXT :
			self.OpenBusyDialog( )
			self.CloseAction( )
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( self.GetAntennaNextStepWindowId( ), WinMgr.WIN_ID_MAINMENU )
			return

		if groupId == E_Input01 :
			if len( self.mTunerMgr.GetConfiguredSatelliteList( ) ) == 0 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No configured satellite available' ) )
	 			dialog.doModal( )
			else :
				self.CloseAction( )
				self.ResetAllControl( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_ONECABLE_2 )
		
		elif groupId == E_SpinEx01 :
			self.DisableControl( )

		else :
			position = self.GetControlIdToListIndex( groupId ) - 2
			if position == 0 :
				if self.mSatelliteNamelist[0] == MR_LANG( 'None' ) :
					self.AddNewSatellite( 0 )
				else :
					self.mTunerMgr.SetCurrentConfigIndex( 0 )
					self.ResetAllControl( )
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_SIMPLE )
			else :
				if self.mSatelliteNamelist[0] == MR_LANG( 'None' ) :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Select a satellite name for satellite 1 first' ) )
		 			dialog.doModal( )
		 			return
		 		if self.mSatelliteNamelist[1] == MR_LANG( 'None' ) :
					self.AddNewSatellite( 1 )
				else :
					self.mTunerMgr.SetCurrentConfigIndex( 1 )
					self.ResetAllControl( )
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_SIMPLE )
		 			

	def AddNewSatellite( self, aPosition ) :
		dialog = xbmcgui.Dialog( )
		satelliteList = self.mDataCache.GetFormattedSatelliteNameList( )
		ret = dialog.select(  MR_LANG( 'Select Satellite' ), satelliteList )
		if ret >= 0 :
			self.OpenBusyDialog( )
			if self.mTunerMgr.CheckSameSatellite( ret ) :
				self.mTunerMgr.AddConfiguredSatellite( ret )
				self.ResetAllControl( )
				if self.GetFirstInstallation( ) :
					bakupCount = self.GetAntennaCurrentCount( )
					self.MakeAntennaSetupStepList( )
					self.SetAntennaCurrentCount( bakupCount )
					self.CloseBusyDialog( )
					self.onInit( )
				else :
					self.mTunerMgr.SaveConfiguration( )
					self.mDataCache.Channel_ReTune( )
					self.LoadConfigedSatellite( )
					self.mTunerMgr.SetCurrentConfigIndex( aPosition )
					self.CloseBusyDialog( )
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_SIMPLE )
		 	else :
		 		self.CloseBusyDialog( )
		 		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Same name of satellite already exists' ) )
	 			dialog.doModal( )


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
		if self.mInitialized == False :
			return
		if self.mLastFocused != aControlId :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId


	def DisableControl( self ) : 
		position = self.GetSelectedIndex( E_SpinEx01 ) + 1
		self.mTunerMgr.SetOnecableSatelliteCount( position )
		for i in range( MAX_SATELLITE_CNT_ONECABLE ) :
			if ( self.GetSelectedIndex( E_SpinEx01 ) + 1 ) > i :
				self.SetEnableControl( self.GetListIndextoControlId( 2 + i ), True )
				self.SetVisibleControl( self.GetListIndextoControlId( 2 + i ), True )
			else :
				self.SetEnableControl( self.GetListIndextoControlId( 2 + i ), False )
				self.SetVisibleControl( self.GetListIndextoControlId( 2 + i ), False ) 


	def LoadConfigedSatellite( self ) :
		self.mSatelliteNamelist = []

		configuredList = self.mTunerMgr.GetConfiguredSatelliteList( )
		self.mSatelliteCount = len( configuredList )

		for i in range( MAX_SATELLITE_CNT_ONECABLE ) :
			if i < self.mSatelliteCount :
				self.mSatelliteNamelist.append( self.mDataCache.GetFormattedSatelliteName( configuredList[i].mSatelliteLongitude, configuredList[i].mBandType ) )
			else :
				self.mSatelliteNamelist.append( MR_LANG( 'None' ) )


	def CloseAction( self ) :
		if self.mSatelliteCount > 1 :
			for i in range( self.mSatelliteCount - 1 ) :
				satellite = self.mTunerMgr.GetConfiguredSatellitebyIndex( i + 1 )
				satellite.mIsOneCable = self.mCurrentSatellite.mIsOneCable
				satellite.mOneCablePin = self.mCurrentSatellite.mOneCablePin
				satellite.mOneCableMDU = self.mCurrentSatellite.mOneCableMDU
				satellite.mOneCableLoFreq1 = self.mCurrentSatellite.mOneCableLoFreq1
				satellite.mOneCableLoFreq2 = self.mCurrentSatellite.mOneCableLoFreq2
				satellite.mOneCableUBSlot = self.mCurrentSatellite.mOneCableUBSlot
				satellite.mOneCableUBFreq = self.mCurrentSatellite.mOneCableUBFreq

		if self.mTunerMgr.GetOneCableSatelliteCount( ) < self.mSatelliteCount :
			for i in range( self.mSatelliteCount ) :
				if self.mTunerMgr.GetOneCableSatelliteCount( ) < ( i + 1 ) :
					self.mTunerMgr.DeleteConfiguredSatellitebyIndex( i )
					if self.GetFirstInstallation( ) :
						bakupCount = self.GetAntennaCurrentCount( )
						self.MakeAntennaSetupStepList( )
						self.SetAntennaCurrentCount( bakupCount )

