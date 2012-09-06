from pvr.gui.WindowImport import *


# Control IDs
LABEL_ID_TRANSPONDER_INFO		= 404
PROGRESS_ID_SCAN				= 200
LIST_ID_TV						= 400
LIST_ID_RADIO					= 402
BUTTON_ID_CANCEL				= 300


# Scan MODE
E_SCAN_NONE					= 0
E_SCAN_SATELLITE			= 1
E_SCAN_TRANSPONDER			= 2


class DialogChannelSearch( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mScanMode = E_SCAN_NONE
		self.mIsFinished = True
		self.mTransponderList = []
		self.mConfiguredSatelliteList = []
		self.mLongitude = 0
		self.mBand = 0
		self.mSatelliteFormatedName = MR_LANG( 'Unknown' )


	def onInit( self ) :
		self.mDataCache.Player_AVBlank( True, True )

		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mIsFinished = False	
		self.mTimer = None

		self.mNewTVChannelList = []
		self.mNewRadioChannelList = []

		self.mTvListItems = []
		self.mRadioListItems =[]

		self.getControl( LIST_ID_TV ).reset( )
		self.getControl( LIST_ID_RADIO ).reset( )

		self.mCtrlProgress = self.getControl( PROGRESS_ID_SCAN )
		self.mCtrlTransponderInfo = self.getControl( LABEL_ID_TRANSPONDER_INFO )		

		self.mEventBus.Register( self )	

		self.ScanStart( )
		self.DrawItem( )

		self.AbortDialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		self.AbortDialog.SetDialogProperty( MR_LANG( 'Abort Channel Search' ), MR_LANG( 'Do you want to stop the channel scan?' ) )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.ScanAbort( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_PARENT_DIR :
			self.ScanAbort( )

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

		if focusId == BUTTON_ID_CANCEL :
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
		self.mConfiguredSatelliteList = aConfiguredSatelliteList
		config = self.mConfiguredSatelliteList[0]
		self.mLongitude = config.mLongitude
		self.mBand = config.mBand
		self.mScanMode = E_SCAN_SATELLITE 
		self.mSatelliteFormatedName = self.mDataCache.GetFormattedSatelliteName( self.mLongitude , self.mBand  )


	def SetTransponder( self, aLongitude, aBand, aTransponderList ) :
		self.mScanMode = E_SCAN_TRANSPONDER	
		self.mLongitude = aLongitude
		self.mBand = aBand		
		self.mTransponderList = aTransponderList
		self.mSatelliteFormatedName = self.mDataCache.GetFormattedSatelliteName( self.mLongitude , self.mBand  )


	def ScanStart( self ) :
		if self.mScanMode == E_SCAN_SATELLITE :
			ret = self.mCommander.Channelscan_BySatelliteList( self.mConfiguredSatelliteList )

			if ret == False :
				self.mEventBus.Deregister( self )
				self.ReTune( )
				self.CloseDialog( )
				self.mDataCache.Player_AVBlank( False, True )
				self.ReLoadChannelList( )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Channel search has failed to complete' ) )				
				dialog.doModal( )

		elif self.mScanMode == E_SCAN_TRANSPONDER :
			ret = self.mCommander.Channel_SearchByCarrier( self.mLongitude, self.mBand, self.mTransponderList )
			if ret == False :
				self.mEventBus.Deregister( self )
				self.CloseDialog( )
				self.mDataCache.Player_AVBlank( False, True )
				self.ReLoadChannelList( )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Channel search has failed to complete' ) )				
				dialog.doModal( )
		else :
			self.mIsFinished = True


	def ScanAbort( self ) :
		if self.mIsFinished == False :
			self.AbortDialog.doModal( )

			if self.AbortDialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.mCommander.Channelscan_Abort( )
				self.mIsFinished = True

			elif self.AbortDialog.IsOK( ) == E_DIALOG_STATE_NO : 
				return
				
			elif self.AbortDialog.IsOK( ) == E_DIALOG_STATE_CANCEL :
				return
 
		if self.mIsFinished == True :
			self.mEventBus.Deregister( self )
			if self.mScanMode == E_SCAN_SATELLITE :
				self.ReTune( )
			self.CloseDialog( )
			self.mDataCache.Player_AVBlank( False, False )
			self.ReLoadChannelList( )


	@GuiLock
	def onEvent( self, aEvent ) :
		if xbmcgui.getCurrentWindowDialogId( ) == self.mWinId :

			if aEvent.getName( ) == ElisEventScanAddChannel.getName( ) :
				self.UpdateAddChannel( aEvent )

			elif aEvent.getName( ) == ElisEventScanProgress.getName( ) :
				self.UpdateScanProgress( aEvent )


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

			strTransponderInfo = '%s - %d Mhz - %s - %d MS/s ' %( self.mSatelliteFormatedName, aEvent.mCarrier.mDVBS.mFrequency, strPol, aEvent.mCarrier.mDVBS.mSymbolRate )
			self.mCtrlTransponderInfo.setLabel( strTransponderInfo )

		elif aEvent.mCarrier.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBT :
			pass

		elif aEvent.mCarrier.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBC :
			pass

		if aEvent.mFinished and aEvent.mCurrentIndex >= aEvent.mAllCount :
			self.mCtrlProgress.setPercent( 100 )
			self.mTimer = threading.Timer( 0.5, self.ShowResult )
			self.mTimer.start( )


	def UpdateAddChannel( self, aEvent ) :
		if aEvent.mIChannel.mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
			self.mNewTVChannelList.append( aEvent.mIChannel )
		elif aEvent.mIChannel.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
			self.mNewRadioChannelList.append( aEvent.mIChannel )
		else : 
			LOG_ERR( 'Unknown service type = %s' % aEvent.mIChannel.mServiceType )
		self.DrawItem( )


	def ShowResult( self ) :
		tvCount = len( self.mTvListItems )
		radioCount = len( self.mRadioListItems )
		searchResult = MR_LANG( 'TV Channels : %d \nRadio Channels : %d' ) %( tvCount, radioCount )

		try :
			self.AbortDialog.close( )
		except Exception, ex :
			LOG_TRACE( 'except close dialog' )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( MR_LANG( 'Channel Search Result' ), searchResult )
		dialog.doModal( )
		self.mIsFinished = True


	def ReLoadChannelList( self ) :
		self.mDataCache.LoadZappingmode( )
		self.mDataCache.LoadZappingList( )
		self.mDataCache.LoadChannelList( 0, ElisEnum.E_SERVICE_TYPE_TV, ElisEnum.E_MODE_ALL, ElisEnum.E_SORT_BY_NUMBER )


	def ReTune( self ) :
		channel = self.mDataCache.Channel_GetCurrent( )
		if channel == None or channel.mError != 0 :
			LOG_ERR( 'Load Channel_GetCurrent None' )
		else :
			self.mCommander.Channel_InvalidateCurrent( )
			self.mDataCache.Channel_SetCurrent( channel.mNumber, channel.mServiceType )

