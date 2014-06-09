from pvr.gui.WindowImport import *


# Control IDs
LABEL_ID_TRANSPONDER_INFO		= 404
LABEL_ID_EXIT_INFO				= 405
PROGRESS_ID_SCAN				= 200
LIST_ID_TV						= 400
LIST_ID_RADIO					= 402
BUTTON_ID_CLOSE					= 104

# Scan MODE
E_SCAN_NONE						= 0
E_SCAN_SATELLITE				= 1
E_SCAN_TRANSPONDER				= 2
E_SCAN_PROVIDER					= 3
E_SCAN_CARRIER					= 4

INVALID_CHANNEL					= 65534


class DialogChannelSearch( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mScanMode					= E_SCAN_NONE
		self.mIsFinished				= True
		self.mIsOpenAbortDialog			= False
		self.mTransponderList			= []
		self.mConfiguredSatelliteList	= []
		self.mCarrierList				= []
		self.mLongitude					= 0
		self.mBand						= 0
		self.mSatelliteFormatedName		= None
		self.mNewTVChannelList			= []
		self.mNewRadioChannelList		= []
		self.mTvListItems				= []
		self.mRadioListItems			= []
		self.mCtrlProgress				= None
		self.mCtrlTransponderInfo		= None
		self.mAbortDialog				= None
		self.mStoreTVChannel			= []
		self.mStoreRadioChannel			= []
		self.mManualTpSearch			= False

		# for fast scan
		self.mTunerIndex 				= E_TUNER_1
		self.mUseNumbering				= 0
		self.mUseNaming					= 0
		self.mProviderStruct 			= None


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.mIsFinished			= False	
		self.mIsOpenAbortDialog		= False

		self.mNewTVChannelList		= []
		self.mNewRadioChannelList	= []
		self.mTvListItems			= []
		self.mRadioListItems		= []
		self.mStoreTVChannel		= []
		self.mStoreRadioChannel		= []

		self.getControl( LIST_ID_TV ).reset( )
		self.getControl( LIST_ID_RADIO ).reset( )
		self.getControl( LABEL_ID_EXIT_INFO ).setLabel( MR_LANG( 'Press [BACK] on the remote to close channel search dialog' ) )

		self.mCtrlProgress = self.getControl( PROGRESS_ID_SCAN )
		self.mCtrlTransponderInfo = self.getControl( LABEL_ID_TRANSPONDER_INFO )		

		self.mEventBus.Register( self )

		self.ScanStart( )
		self.DrawItem( )

		self.mAbortDialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		self.mAbortDialog.SetDialogProperty( MR_LANG( 'Exit Channel Search' ), MR_LANG( 'Are you sure you want to stop the channel scan?' ), True )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			if self.mIsFinished :
				self.mEventBus.Deregister( self )
				self.CloseDialog( )
			else :
				self.ScanAbort( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_MOVE_UP :
			pass

		elif actionId == Action.ACTION_MOVE_DOWN :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT :
			pass

		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass


	def onClick( self, aControlId ) :
		focusId = self.getFocusId( )
		if focusId == BUTTON_ID_CLOSE :
			if self.mIsFinished :
				self.mEventBus.Deregister( self )
				self.CloseDialog( )
			else :
				self.ScanAbort( )


	def onFocus( self, controlId ) :
		pass


	def DrawItem( self ) :		
		count = len( self.mNewTVChannelList )
		for i in range( count ) :
			listItem = xbmcgui.ListItem( self.mNewTVChannelList[i].mName )
			if self.mNewTVChannelList[i].mIsCA :
				listItem.setProperty( 'IsCas', 'True' )
			else :
				listItem.setProperty( 'IsCas', 'False' )
			self.mTvListItems.append( listItem )

		if count > 0 :
			self.getControl( LIST_ID_TV ).addItems( self.mTvListItems )
			lastPosition = len( self.mTvListItems ) - 1
			self.getControl( LIST_ID_TV ).selectItem( lastPosition )

		count = len( self.mNewRadioChannelList )
		for i in range( count ) :
			listItem = xbmcgui.ListItem( self.mNewRadioChannelList[i].mName )
			if self.mNewRadioChannelList[i].mIsCA :
				listItem.setProperty( 'IsCas', 'True' )
			else :
				listItem.setProperty( 'IsCas', 'False' )
			self.mRadioListItems.append( listItem )

		if count > 0 :
			self.getControl( LIST_ID_RADIO ).addItems( self.mRadioListItems )
			lastPosition = len( self.mRadioListItems ) - 1			
			self.getControl( LIST_ID_RADIO ).selectItem( lastPosition  )

		self.mNewTVChannelList = []
		self.mNewRadioChannelList = []


	def SetConfiguredSatellite( self, aConfiguredSatelliteList ) :
		self.mScanMode = E_SCAN_SATELLITE 
		self.mConfiguredSatelliteList = aConfiguredSatelliteList
		config = self.mConfiguredSatelliteList[0]
		self.mLongitude = config.mLongitude
		self.mBand = config.mBand
		self.mSatelliteFormatedName = self.mDataCache.GetFormattedSatelliteName( self.mLongitude , self.mBand  )


	def SetTransponder( self, aLongitude, aBand, aTransponderList, aManualTp=False ) :
		self.mScanMode = E_SCAN_TRANSPONDER	
		self.mLongitude = aLongitude
		self.mBand = aBand
		self.mTransponderList = aTransponderList
		self.mManualTpSearch = aManualTp
		self.mSatelliteFormatedName = self.mDataCache.GetFormattedSatelliteName( self.mLongitude , self.mBand  )


	def SetProvider( self, aTunerIndex, aUseNumbering, aUseNaming, aProviderStruct ) :
		self.mScanMode = E_SCAN_PROVIDER
		self.mTunerIndex = aTunerIndex
		self.mUseNumbering = aUseNumbering
		self.mUseNaming	= aUseNaming
		self.mProviderStruct = aProviderStruct


	def SetCarrier( self, aCarrier ) :
		self.mScanMode = E_SCAN_CARRIER
		self.mCarrierList = aCarrier
		

	def ScanStart( self ) :
		if self.mScanMode == E_SCAN_SATELLITE :
			self.mCommander.Channelscan_BySatelliteList( self.mConfiguredSatelliteList )

		elif self.mScanMode == E_SCAN_TRANSPONDER :
			self.mCommander.Channel_SearchByCarrier( self.mLongitude, self.mBand, self.mTransponderList )

		elif self.mScanMode == E_SCAN_PROVIDER :
			self.mCommander.ChannelScan_StartFastChannelScan( self.mTunerIndex, self.mUseNumbering, self.mUseNaming, self.mProviderStruct )

		elif self.mScanMode == E_SCAN_CARRIER :
			self.mCommander.Channel_Scan( self.mCarrierList )

		else :
			self.mIsFinished = True


	def ScanAbort( self ) :
		self.mIsOpenAbortDialog = True
		self.mAbortDialog.doModal( )
		self.mIsOpenAbortDialog = False
		if self.mAbortDialog.IsOK( ) == E_DIALOG_STATE_YES :
			if self.mScanMode == E_SCAN_PROVIDER :
				self.mCommander.ChannelScan_AbortFastChannelScan( )
			else :
				self.mCommander.Channelscan_Abort( )
			self.LoadChannelSearchedData( )
			self.mEventBus.Deregister( self )
			self.CloseDialog( )
		elif self.mAbortDialog.IsOK( ) == E_DIALOG_STATE_NO :
			return
		elif self.mAbortDialog.IsOK( ) == E_DIALOG_STATE_CANCEL :
			return


	def onEvent( self, aEvent ) :
		if xbmcgui.getCurrentWindowDialogId( ) == self.mWinId or xbmcgui.getCurrentWindowDialogId( ) != XBMC_WINDOW_DIALOG_INVALID :
			if aEvent.getName( ) == ElisEventScanAddChannel.getName( ) :
				self.UpdateAddChannel( aEvent )

			elif aEvent.getName( ) == ElisEventScanProgress.getName( ) :
				self.UpdateScanProgress( aEvent )


	@SetLock
	def UpdateScanProgress( self, aEvent ) :
		percent = 0
		
		if aEvent.mAllCount > 0 :
			percent = int( aEvent.mCurrentIndex * 100 / aEvent.mAllCount )

		if aEvent.mFinished == 0 and ( aEvent.mAllCount < 10 ) and ( aEvent.mCurrentIndex == aEvent.mAllCount ) :
			self.mCtrlProgress.setPercent( 90 )
		else:
			self.mCtrlProgress.setPercent( percent )

		if aEvent.mCarrier.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBS :
			strPol = MR_LANG( 'Vertical' )
			if aEvent.mCarrier.mDVBS.mPolarization == ElisEnum.E_LNB_HORIZONTAL or aEvent.mCarrier.mDVBS.mPolarization == ElisEnum.E_LNB_LEFT :
				strPol = MR_LANG( 'Horizontal' )

			if self.mLongitude != aEvent.mCarrier.mDVBS.mSatelliteLongitude or self.mBand != aEvent.mCarrier.mDVBS.mSatelliteBand :
				self.mLongitude = aEvent.mCarrier.mDVBS.mSatelliteLongitude
				self.mBand = aEvent.mCarrier.mDVBS.mSatelliteBand
				self.mSatelliteFormatedName = self.mDataCache.GetFormattedSatelliteName( self.mLongitude , self.mBand  )
			strTransponderInfo = '%s - %d MHz - %s - %d KS/s ' % ( self.mSatelliteFormatedName, aEvent.mCarrier.mDVBS.mFrequency, strPol, aEvent.mCarrier.mDVBS.mSymbolRate )
			self.mCtrlTransponderInfo.setLabel( strTransponderInfo )

		elif aEvent.mCarrier.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBT :
			strTransponderInfo = 'Frequency %d KHz - Band - %d MHz ' % ( aEvent.mCarrier.mDVBT.mFrequency, aEvent.mCarrier.mDVBT.mBand )
			self.mCtrlTransponderInfo.setLabel( strTransponderInfo )

		elif aEvent.mCarrier.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBC :
			pass

		if aEvent.mFinished and aEvent.mCurrentIndex >= aEvent.mAllCount :
			self.DefaultTuneInSearchedChannel( )

			if self.mIsOpenAbortDialog :
				self.mAbortDialog.close( )
			
			self.mIsFinished = True
			self.LoadChannelSearchedData( )
			self.mCtrlProgress.setPercent( 100 )
			timer = threading.Timer( 0.3, self.ShowResult )
			timer.start( )


	def LoadChannelSearchedData( self ) :
		xbmc.executebuiltin( "ActivateWindow(busydialog)" )
		if len( self.mStoreTVChannel ) > 0 or len( self.mStoreRadioChannel ) > 0 :
			self.mDataCache.Channel_Save( )
			self.mDataCache.LoadZappingList( )
			self.mDataCache.LoadChannelList( )
			iZapping = self.mDataCache.Zappingmode_GetCurrent( )
			if iZapping and iZapping.mError == 0 :
				self.mDataCache.Channel_GetAllChannels( iZapping.mServiceType, False )
			self.mDataCache.SetChannelReloadStatus( True )
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_SIMPLE_CHANNEL_LIST ).ResetControls( )
			iChannel = self.mDataCache.Channel_GetCurrent( True )
			self.mDataCache.mCurrentChannel = iChannel

		if self.mScanMode == E_SCAN_TRANSPONDER or self.mScanMode == E_SCAN_CARRIER :
			self.mCommander.ScanHelper_Start( )

		else :
			if ElisPropertyEnum( 'First Installation', self.mCommander ).GetProp( ) == 0 :
				self.mDataCache.Channel_ReTune( )
			else :
				iChannel = self.mDataCache.Channel_GetCurrent( True )
				self.mDataCache.Channel_TuneDefault( False, iChannel )
		self.NewTransponderAdd( )
		xbmc.executebuiltin( "Dialog.Close(busydialog)" )


	@SetLock
	def UpdateAddChannel( self, aEvent ) :
		if aEvent.mIChannel.mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
			self.mNewTVChannelList.append( aEvent.mIChannel )
			self.mStoreTVChannel.append( aEvent.mIChannel )
		elif aEvent.mIChannel.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
			self.mNewRadioChannelList.append( aEvent.mIChannel )
			self.mStoreRadioChannel.append( aEvent.mIChannel )
		else : 
			LOG_ERR( 'Unknown service type = %s' % aEvent.mIChannel.mServiceType )
		self.DrawItem( )


	def ShowResult( self ) :
		tvCount = len( self.mTvListItems )
		radioCount = len( self.mRadioListItems )
		searchResult = MR_LANG( 'TV channels : %d %sRadio channels : %d' ) % ( tvCount, NEW_LINE, radioCount )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( MR_LANG( 'Channel Search Result' ), searchResult )
		dialog.doModal( )
		

	def DefaultTuneInSearchedChannel( self ) :
		if self.mDataCache.Zappingmode_GetCurrent( ).mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
			if len( self.mStoreTVChannel ) > 0 :
				for channel in self.mStoreTVChannel :
					if not channel.mIsCA :
						self.ChannelTune( channel )
						return

				self.ChannelTune( self.mStoreTVChannel[0] )

		else :
			if len( self.mStoreRadioChannel ) > 0 :
				for channel in self.mStoreRadioChannel :
					if not channel.mIsCA :
						self.ChannelTune( channel )
						return

				self.ChannelTune( self.mStoreRadioChannel[0] )


	def ChannelTune( self, aChannel ) :
		if aChannel.mNumber == INVALID_CHANNEL :
			channel = self.mCommander.Channel_GetByTwolDs( aChannel.mSid, aChannel.mOnid )
			if channel :
				self.mDataCache.Channel_SetCurrent( channel.mNumber, channel.mServiceType, None, True )
		else :
			self.mDataCache.Channel_SetCurrent( aChannel.mNumber, aChannel.mServiceType, None, True )

		self.mDataCache.SetParentLock( True )
		self.mDataCache.SetSearchNewChannel( True )


	def NewTransponderAdd( self ) :
		if self.mManualTpSearch :
			if len( self.mStoreTVChannel ) > 0 or len( self.mStoreRadioChannel ) > 0 :
				self.mDataCache.LoadAllTransponder( )
