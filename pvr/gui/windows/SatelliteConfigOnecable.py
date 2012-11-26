from pvr.gui.WindowImport import *


class SatelliteConfigOnecable( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mSatelliteCount = 0
		self.mSatelliteNamelist = []
		self.mCurrentSatellite = None
		

	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

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
			self.AddInputControl( startId, MR_LANG( 'Satellite %d' ) % ( i + 1 ), self.mSatelliteNamelist[i], MR_LANG( 'Press the OK button to setup %s' ) % (self.mSatelliteNamelist[i]) )
			startId += 100

		self.InitControl( )
		self.getControl( E_SpinEx01 + 3 ).selectItem( self.mSatelliteCount - 1 )
		self.DisableControl( )
		self.setDefaultControl( )
		self.SetPipLabel( )
		self.mInitialized = True


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
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

		if groupId == E_Input01 :
			if len( self.mTunerMgr.GetConfiguredSatelliteList( ) ) == 0 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'There is no configured satellite in the list' ) )
	 			dialog.doModal( )
			else :
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
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'You have you config satellite 1 first' ) )
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
		ret = dialog.select(  MR_LANG( 'Add Satellite' ), satelliteList )
		if ret >= 0 :
			self.OpenBusyDialog( )
			if self.mTunerMgr.CheckSameSatellite( ret ) :
				self.mTunerMgr.AddConfiguredSatellite( ret )
				self.mTunerMgr.SatelliteConfigSaveList( )
				self.ReTune( )
				self.mDataCache.LoadConfiguredSatellite( )
				self.mDataCache.LoadConfiguredTransponder( )
				self.LoadConfigedSatellite( )
				self.CloseBusyDialog( )
				self.mTunerMgr.SetCurrentConfigIndex( aPosition )
				self.ResetAllControl( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_SIMPLE )
		 	else :
		 		self.CloseBusyDialog( )
		 		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Same satellite already configured' ) )
	 			dialog.doModal( )


	def onFocus( self, aControlId ) :
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


	def ReTune( self ) :
		iChannel = self.mDataCache.Channel_GetCurrent( )
		if iChannel :
			self.mDataCache.Channel_InvalidateCurrent( )
			self.mDataCache.Channel_SetCurrentSync( iChannel.mNumber, iChannel.mServiceType )

