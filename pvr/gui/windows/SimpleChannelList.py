from pvr.gui.WindowImport import *
import traceback

E_SIMPLE_CHANNEL_LIST_BASE_ID =  WinMgr.WIN_ID_SIMPLE_CHANNEL_LIST * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID
LIST_ID_BIG_CHANNEL           = E_SIMPLE_CHANNEL_LIST_BASE_ID + 1000
LIST_ID_BIG_GROUP             = E_SIMPLE_CHANNEL_LIST_BASE_ID + 1001
LIST_ID_ZAPPING_GROUP         = E_SIMPLE_CHANNEL_LIST_BASE_ID + 1003

E_NOMAL_UPDATE_TIME = 30
E_SHORT_UPDATE_TIME = 1
E_SHOW_GROUP_LIST = True
E_SIMPLE_CHANNEL_ITEM_HEIGHT = 70

class BackupModeClass( object ) :
	def __init__( self ) :
		self.mZappingTV      = None
		self.mZappingRadio   = None
		self.mGroupIndexTV   = 0
		self.mGroupIndexRadio= 0


class SimpleChannelList( BaseWindow ) :

	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mLock = thread.allocate_lock( )
		self.mChannelList = None
		self.mCurrentChannel = None		
		self.mChannelListHash    = {}
		self.mChannelNumbersHash = {}
		self.mEPGHashTable = {}
		self.mEPGList	= []	
		self.mListItems = []
		self.mItemCount = 8
		self.mBackupMode = BackupModeClass( )
		self.mOffsetTopIndex = 0
	
	def onInit( self ) :
		self.SetFrontdisplayMessage( MR_LANG('Channel List') )
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.CheckMediaCenter( )

		self.mAsyncEPGTimer      = None
		self.mEPGUpdateTimer     = None
		self.mAsyncUpdateTimer   = None
		try :
			self.mAutoConfirm = int( GetSetting( 'AUTO_CONFIRM_CHANNEL' ) )

		except Exception, e :
			LOG_ERR( '[SimpleChannelList] except[%s]'% e )
			self.mAutoConfirm = False

		self.mCtrlBigList   = self.getControl( LIST_ID_BIG_CHANNEL )
		self.mCtrlGroupList = self.getControl( LIST_ID_BIG_GROUP )
		self.mCtrlGroupSlide = self.getControl( LIST_ID_ZAPPING_GROUP )
		#self.SetSingleWindowPosition( E_SIMPLE_CHANNEL_LIST_BASE_ID )
		#self.SetPipScreen( )

		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( )
		self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
		self.mServiceType	 = self.mCurrentMode.mServiceType

		LOG_TRACE( '[SimpleChannelList] ZeppingMode(%d,%d,%d)' %( self.mCurrentMode.mServiceType, self.mCurrentMode.mMode, self.mCurrentMode.mSortingMode ) )
		self.mChannelList = self.mDataCache.Channel_GetList( )

		self.mUserMode         = deepcopy( self.mCurrentMode )
		self.mChangeMode       = None
		self.mGroupIndex       = -1
		self.mUserGroup        = ''
		self.mCurrentGroup     = ''
		self.mListGroupName    = []
		self.mZappingGroupList = [ MR_LANG( 'All Channels' ), [ElisIFavoriteGroup()], [ElisINetworkInfo()], [ElisISatelliteInfo()], [ElisIChannelCASInfo()], [ElisIProviderInfo()] ]
		#self.mZappingGroupList[ ElisEnum.E_MODE_NETWORK ] # reserved
		self.mZappingGroupList[ ElisEnum.E_MODE_SATELLITE ] = self.mDataCache.Satellite_GetConfiguredList( )
		self.mZappingGroupList[ ElisEnum.E_MODE_CAS ]       = self.mDataCache.Fta_cas_GetList( )
		self.mZappingGroupList[ ElisEnum.E_MODE_PROVIDER ]  = self.mDataCache.Provider_GetList( )
		self.mZappingGroupList[ ElisEnum.E_MODE_FAVORITE ]  = self.mDataCache.Favorite_GetList( )

		self.UpdateListAll( )
		loadEpgAll = False
		if not self.mInitialized :
			self.mInitialized = True
			self.mBackupMode.mZappingTV    = deepcopy( self.mCurrentMode )
			self.mBackupMode.mZappingRadio = deepcopy( self.mCurrentMode )
			self.mBackupMode.mGroupIndexTV    = 0
			self.mBackupMode.mGroupIndexRadio = 0
			self.mBackupMode.mZappingRadio.mMode = ElisEnum.E_MODE_ALL
			self.mBackupMode.mZappingRadio.mServiceType = ElisEnum.E_SERVICE_TYPE_RADIO
			self.mBackupMode.mZappingRadio.mSortingMode = self.mCurrentMode.mSortingMode
			listHeight= self.mCtrlBigList.getHeight( )
			self.mItemCount = listHeight / E_SIMPLE_CHANNEL_ITEM_HEIGHT
			loadEpgAll = True

		self.LoadByCurrentEPG( loadEpgAll )

		self.mEventBus.Register( self )
		self.StartEPGUpdateTimer( )

		self.setFocusId( LIST_ID_BIG_CHANNEL )
		self.setProperty( 'ZappingModeInfo', E_TAG_TRUE )
		self.UpdateSelectedPosition( )


	def onAction( self, aAction ) :
		self.GetFocusId( )
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		#LOG_TRACE('onAction=%d' %actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			if self.mChangeMode :
				self.PreviousChannelList( )
				return

			self.Close( )

		elif actionId == Action.ACTION_MOVE_LEFT or actionId == Action.ACTION_MOVE_RIGHT :
			if self.mChangeMode :
				self.PreviousChannelList( )
				return

			self.Close( )

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN or actionId == Action.ACTION_PAGE_UP or actionId == Action.ACTION_PAGE_DOWN :
			if self.mChangeMode :
				self.UpdateGroupSlide( )
				return

			self.RestartAsyncEPG( )

		elif actionId == Action.ACTION_MBOX_TVRADIO :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.ToggleTVRadio( )
				if ret :
					self.SetRadioScreen( self.mServiceType )
					if self.mChangeMode :
						self.PreviousChannelList( )

				else :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No channels available for the selected mode' ) )
					dialog.doModal( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			if self.mFocusId == LIST_ID_BIG_CHANNEL :
				self.Tune( )
			elif self.mFocusId == LIST_ID_BIG_GROUP :
				self.GetSelectGroup( )

		elif actionId == Action.ACTION_MBOX_FF :
			self.UpdateShortCutGroup( 1 )

		elif actionId == Action.ACTION_MBOX_REWIND :
			self.UpdateShortCutGroup( -1 )

		elif actionId == Action.ACTION_COLOR_RED :
			self.UpdateShortCutZapping( ElisEnum.E_MODE_SATELLITE )

		elif actionId == Action.ACTION_COLOR_GREEN :
			self.UpdateShortCutZapping( ElisEnum.E_MODE_CAS )

		elif actionId == Action.ACTION_COLOR_YELLOW :
			self.UpdateShortCutZapping( ElisEnum.E_MODE_PROVIDER )

		elif actionId == Action.ACTION_COLOR_BLUE :
			self.UpdateShortCutZapping( ElisEnum.E_MODE_FAVORITE )


	def onClick( self, aControlId ) :
		pass


	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			if aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
				#if self.mIsUpdateEnable == True	:
				#LOG_TRACE( '[SimpleChannelList] record start/stop event' )
				self.UpdateListAll( True )


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.StopAsyncEPG( )
		self.StopAsyncUpdate( )
		self.StopEPGUpdateTimer( )

		self.SetModeToChange( )
		WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )


	def Flush( self ) :
		self.mEPGList = []
		self.mEPGHashTable = {}


	def ResetControls( self ) :
		self.mListItems = []


	def PreviousChannelList( self ) :
		self.mChangeMode = None
		self.setProperty( 'SimpleChannelGroup', E_TAG_FALSE )
		self.UpdateListToEPG( )
		self.StartEPGUpdateTimer( )
		self.setFocusId( LIST_ID_BIG_CHANNEL )
		lblPath = EnumToString( 'mode', self.mUserMode.mMode )
		#if self.mUserGroup :
		#	lblPath = '%s > %s'% ( lblPath, self.mUserGroup )
		self.setProperty( 'SimpleChannelPath', lblPath )

		slideVisible = E_TAG_FALSE
		groupListSlide = []
		if self.mUserMode.mMode != ElisEnum.E_MODE_ALL :
			slideVisible = E_TAG_TRUE
			for groupName in self.mListGroupName :
				listItem = xbmcgui.ListItem( '%s'% groupName )
				groupListSlide.append( listItem )

		if not groupListSlide or len( groupListSlide ) < 1 :
			slideVisible = E_TAG_FALSE

		self.mCtrlGroupSlide.reset( )
		self.mCtrlGroupSlide.addItems( groupListSlide )
		self.mCtrlGroupSlide.selectItem( self.mGroupIndex )
		self.setProperty( 'ShowGroupSlide', slideVisible )


	def UpdateListAll( self, aLoadChannel = False ) :
		#self.Flush( )
		self.StopEPGUpdateTimer( )

		if aLoadChannel :
			self.ResetControls( )
			self.GetChannelList( )

		self.InitToChannel( )
		self.UpdateList( )
		self.StartEPGUpdateTimer( )
		#threading.Timer( 0.5, self.UpdateSelectedPosition ).start( )


	def InitToChannel( self ) :
		lblPath = EnumToString( 'mode', self.mUserMode.mMode )
		self.mUserGroup = ''
		self.mListGroupName = []
		groupList = self.mZappingGroupList[self.mUserMode.mMode]
		if self.mUserMode.mMode == ElisEnum.E_MODE_SATELLITE :
			self.mUserGroup = self.mUserMode.mSatelliteInfo.mName
			for groupInfo in groupList :
				self.mListGroupName.append( groupInfo.mName )

		elif self.mUserMode.mMode == ElisEnum.E_MODE_CAS :
			self.mUserGroup = self.mUserMode.mCasInfo.mName
			for groupInfo in groupList :
				self.mListGroupName.append( groupInfo.mName )

		elif self.mUserMode.mMode == ElisEnum.E_MODE_PROVIDER :
			self.mUserGroup = self.mUserMode.mProviderInfo.mProviderName
			for groupInfo in groupList :
				self.mListGroupName.append( groupInfo.mProviderName )

		elif self.mUserMode.mMode == ElisEnum.E_MODE_FAVORITE :
			self.mUserGroup = self.mUserMode.mFavoriteGroup.mGroupName
			for groupInfo in groupList :
				self.mListGroupName.append( groupInfo.mGroupName )

		if self.mGroupIndex < 0 :
			loopCount  = 0
			for groupName in self.mListGroupName :
				if groupName == self.mUserGroup :
					self.mGroupIndex   = loopCount
					self.mCurrentGroup = self.mUserGroup
					break

				loopCount += 1

		#if self.mUserGroup :
		#	lblPath = '%s > %s'% ( lblPath, self.mUserGroup )
		self.setProperty( 'SimpleChannelPath', lblPath )

		groupListSlide = []
		slideVisible = E_TAG_FALSE
		if self.mUserMode.mMode != ElisEnum.E_MODE_ALL :
			for groupName in self.mListGroupName :
				listItem = xbmcgui.ListItem( '%s'% groupName )
				groupListSlide.append( listItem )

		if groupListSlide :
			slideVisible = E_TAG_TRUE

		self.mCtrlGroupSlide.reset( )
		self.mCtrlGroupSlide.addItems( groupListSlide )
		self.mCtrlGroupSlide.selectItem( self.mGroupIndex )
		self.setProperty( 'ShowGroupSlide', slideVisible )

		self.mChannelListHash = {}
		self.mChannelNumbersHash = {}
		if self.mChannelList :
			idxCount = 0
			for iChannel in self.mChannelList :
				hashKey = '%d:%d:%d:%d'% ( iChannel.mNumber, iChannel.mSid, iChannel.mTsid, iChannel.mOnid )
				self.mChannelListHash[hashKey] = [iChannel, idxCount]
				self.mChannelNumbersHash[iChannel.mNumber] = iChannel
				idxCount += 1

		LOG_TRACE( '[SimpleChannelList] mChannelListHash[%s] mChannelNumbersHash[%s]'% ( len( self.mChannelListHash ), len( self.mChannelNumbersHash ) ) )


	def GetChannelByIDs( self, aNumber, aSid, aTsid, aOnid, aReqIndex = False ) :
		if not self.mChannelListHash or len( self.mChannelListHash ) < 1 :
			retVal = None
			if aReqIndex :
				retVal = -1
			return retVal

		retValue = 0
		if aReqIndex :
			retValue = 1

		iChannel = self.mChannelListHash.get( '%d:%d:%d:%d'% ( aNumber, aSid, aTsid, aOnid ), None )
		if iChannel :
			iChannel = iChannel[retValue]

		if aReqIndex and iChannel == None :
			iChannel = -1 #none exist index

		return iChannel


	def GetChannelByNumber( self, aNumber ) :
		if not self.mChannelNumbersHash or len( self.mChannelNumbersHash ) < 1 :
			return None

		return self.mChannelNumbersHash.get( aNumber, None )


	def GetEPGByIds( self, aSid, aTsid, aOnid ) :
		return self.mEPGHashTable.get( '%d:%d:%d' %( aSid, aTsid, aOnid ), None )


	def LoadByCurrentEPG( self, aUpdateAll = False ) :
		if not self.mChannelList or len( self.mChannelList ) < 1 :
			LOG_TRACE( '[SimpleChannelList] pass, channelList None' )
			return

		isUpdate = True
		epgList = []
		startTime = time.time()

		if aUpdateAll :
			self.OpenBusyDialog( )
		#self.mLock.acquire( )

		try :
			if aUpdateAll :
				self.mEPGHashTable = {}
				#epgList = self.mDataCache.Epgevent_GetCurrentListByEpgCF( self.mUserMode.mServiceType )
				epgList = self.mDataCache.Epgevent_GetShortListAll( self.mUserMode )
				#LOG_TRACE( '[SimpleChannelList] aUpdateAll[%s] mode[%s] type[%s]'% ( aUpdateAll, self.mUserMode.mMode, self.mUserMode.mServiceType ) )

			else :
				numList = []
				#chNumbers = []
				self.mOffsetTopIndex = GetOffsetPosition( self.mCtrlBigList )
				endCount  = self.mOffsetTopIndex + self.mItemCount
				listCount = len( self.mChannelList )
				for offsetIdx in range( self.mOffsetTopIndex, endCount ) :
					if offsetIdx < listCount :
						chNum = ElisEInteger( )
						chNum.mParam = self.mChannelList[offsetIdx].mNumber
						numList.append( chNum )
						#chNumbers.append( self.mChannelList[offsetIdx].mNumber )

					else :
						#LOG_TRACE( '[SimpleChannelList] limit over, mOffsetTopIndex[%s] offsetIdx[%s] chlen[%s]'% ( self.mOffsetTopIndex, offsetIdx, listCount ) )
						break
				#LOG_TRACE( '[ChannelList] aUpdateAll[%s] mOffsetTopIndex[%s] mItemCount[%s] chlen[%s] numList[%s][%s]'% ( aUpdateAll, self.mOffsetTopIndex, self.mItemCount, listCount, len( numList ), chNumbers ) )

				if numList and len( numList ) > 0 :
					epgList = self.mDataCache.Epgevent_GetShortList( self.mUserMode.mServiceType, numList )

		except Exception, e :
			isUpdate = False
			LOG_ERR( '[SimpleChannelList] except[%s]'% e )

		if not epgList or len( epgList ) < 1 :
			isUpdate = False
			LOG_TRACE( '[SimpleChannelList] get epglist None' )

		if isUpdate :
			for iEPG in epgList :
				self.mEPGHashTable[ '%d:%d:%d'% ( iEPG.mSid, iEPG.mTsid, iEPG.mOnid ) ] = iEPG
				#LOG_TRACE( 'epg [%s %s:%s:%s]'% ( iEPG.mChannelNo, iEPG.mSid, iEPG.mTsid, iEPG.mOnid ) )

			LOG_TRACE( '[SimpleChannelList] epgList COUNT[%s]'% len( epgList ) )

		#self.mLock.release( )
		if aUpdateAll :
			self.CloseBusyDialog( )

		#print '[ChannelList] LoadByCurrentEPG-----testTime[%s]'% ( time.time() - startTime )

		self.UpdateListToEPG( aUpdateAll )


	def UpdateListToEPG( self, aUpdateAll = False, aForce = False ) :
		if not self.mListItems or ( not self.mChannelList ) :
			LOG_TRACE( '[SimpleChannelList] pass, channelList None' )
			return

		startTime = time.time()

		updateStart = GetOffsetPosition( self.mCtrlBigList )
		updateEnd = ( updateStart + self.mItemCount )
		if aUpdateAll :
			updateStart = 0
			updateEnd = len( self.mListItems ) - 1

		#LOG_TRACE( '[ChannelList] offsetTop[%s] idxStart[%s] idxEnd[%s] listHeight[%s] itemCount[%s]'% ( self.GetOffsetPosition( ), updateStart, updateEnd, E_SIMPLE_CHANNEL_ITEM_HEIGHT, self.mItemCount ) )

		if aUpdateAll :
			self.OpenBusyDialog( )

		try :
			updateCount = 0
			strNoEvent = MR_LANG( 'No event' )
			listCount = len( self.mChannelList )
			currentTime = self.mDataCache.Datetime_GetLocalTime( )

			for idx in range( updateStart, updateEnd ) :
				if self.mChannelList and idx < listCount :
					hasEvent = E_TAG_FALSE
					epgName  = strNoEvent
					listItem = self.mListItems[idx]
					iChannel = self.mChannelList[idx]
					epgEvent = self.GetEPGByIds( iChannel.mSid, iChannel.mTsid, iChannel.mOnid )

					if epgEvent :
						hasEvent = E_TAG_TRUE
						epgName  = epgEvent.mEventName
						epgStart = epgEvent.mStartTime + self.mLocalOffset
						listItem.setProperty( 'percent', '%s'% CalculateProgress( currentTime, epgStart, epgEvent.mDuration ) )
						#LOG_TRACE( 'idx[%s] per[%s] ch[%s %s]'% ( idx, CalculateProgress( currentTime, epgStart, epgEvent.mDuration ), iChannel.mNumber, iChannel.mName ) )

					updateCount += 1
					listItem.setLabel2( epgName )
					listItem.setProperty( 'HasEvent', hasEvent )

				else :
					break

			LOG_TRACE( '[SimpleChannelList] UpdateItemsEPG [%s]counts'% updateCount )

		except Exception, e :
			LOG_ERR( '[SimpleChannelList] except[%s]'% e )

		if aUpdateAll :
			self.CloseBusyDialog( )

		#print '[SimpleChannelList] UpdateListToEPG------testTime[%s]'% ( time.time() - startTime )


	def UpdateList( self, aUpdateOnly = False ) :
		if not self.mChannelList or len( self.mChannelList ) < 1 :
			self.mCtrlBigList.reset( )
			self.mListItems = []
			LOG_TRACE( '[SimpleChannelList] pass, Channel list None' )
			return

		loopCount = 0
		strNoEvent = MR_LANG( 'No event' )

		if not self.mListItems :
			self.mListItems = []
			self.mCtrlBigList.reset( )
			currentTime = self.mDataCache.Datetime_GetLocalTime( )
			runningTimers = self.mDataCache.Timer_GetRunningTimers( )
			LOG_TRACE( '[SimpleChannelList] reset items' )

			for iChannel in self.mChannelList :
				iChNumber = iChannel.mNumber
				if E_V1_2_APPLY_PRESENTATION_NUMBER :
					iChNumber = self.mDataCache.CheckPresentationNumber( iChannel )

				tempChannelName = '%04d %s' %( iChNumber, iChannel.mName )
				if self.IsRunningTimer( runningTimers, iChannel ) :
					tempChannelName = '[COLOR=red]%04d %s[/COLOR]' %( iChNumber, iChannel.mName )

				listItem = xbmcgui.ListItem( tempChannelName )

				hasEvent = E_TAG_FALSE
				epgName  = strNoEvent
				epgEvent = self.GetEPGByIds( iChannel.mSid, iChannel.mTsid, iChannel.mOnid )

				if epgEvent :
					hasEvent = E_TAG_TRUE
					epgName  = epgEvent.mEventName
					epgStart = epgEvent.mStartTime + self.mLocalOffset
					listItem.setProperty( 'percent', '%s'% CalculateProgress( currentTime, epgStart, epgEvent.mDuration ) )

				listItem.setLabel2( epgName )
				listItem.setProperty( 'HasEvent', hasEvent )

				#add channel logo
				if E_USE_CHANNEL_LOGO == True :
					logo = '%s_%s'% ( iChannel.mCarrier.mDVBS.mSatelliteLongitude, iChannel.mSid )
					listItem.setProperty( 'ChannelLogo', self.mChannelLogo.GetLogo( logo, self.mServiceType ) )

				loopCount += 1
				self.mListItems.append( listItem )

			self.mCtrlBigList.addItems( self.mListItems )
			LOG_TRACE( '[SimpleChannelList] done, update list item' )

		self.FocusCurrentChannel( )


	def UpdateSelectedPosition( self ) :
		propertyName = 'SelectedPosition'
		selectedPos = self.mCtrlBigList.getSelectedPosition( )
		if self.mChangeMode :
			propertyName = 'SelectedGroup'
			selectedPos = self.mCtrlGroupList.getSelectedPosition( )

		lblPos = 0
		if selectedPos < 0 :
			lblPos = 0
		else :
			lblPos = selectedPos + 1

		if not self.mChangeMode and ( not self.mChannelList ) :
			lblPos = 0

		self.setProperty( propertyName, '%s'% lblPos )


	def FocusCurrentChannel( self ) :
		if not self.mChannelList or ( not self.mCurrentChannel ) :
			self.UpdateSelectedPosition( )
			return

		fucusIndex = self.GetChannelByIDs( self.mCurrentChannel.mNumber, self.mCurrentChannel.mSid, self.mCurrentChannel.mTsid, self.mCurrentChannel.mOnid, True )
		if fucusIndex > -1 :
			self.mCtrlBigList.selectItem( fucusIndex )
			time.sleep( 0.2 )

		self.UpdateSelectedPosition( )


	def IsRunningTimer( self, aRunningTimers, aChannel ) :
		if aRunningTimers == None :
			return False

		for timer in aRunningTimers :
			if timer.mSid == aChannel.mSid  and timer.mTsid == aChannel.mTsid and timer.mOnid == aChannel.mOnid :
				return True

		return False


	def Tune( self ) :
		self.StopEPGUpdateTimer( )	
		selectedPos = self.mCtrlBigList.getSelectedPosition( )

		if selectedPos >= 0 and self.mChannelList and selectedPos < len( self.mChannelList ) :
			iChannel = self.mChannelList[ selectedPos ]

			if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
				self.mDataCache.Player_Stop( )

			else :
				if self.mCurrentChannel.mNumber == iChannel.mNumber :
					self.Close( )
					return

			if not self.mDataCache.Get_Player_AVBlank( ) :
				self.mDataCache.Player_AVBlank( True )

			self.mDataCache.Channel_SetCurrent( iChannel.mNumber, iChannel.mServiceType )
			self.mCurrentChannel = deepcopy( iChannel )

			if self.mAutoConfirm :
				self.Close( )
				return


	def RestartAsyncUpdate( self ) :
		self.StopAsyncUpdate( )
		self.StartAsyncUpdate( )


	def StartAsyncUpdate( self ) :
		self.mAsyncUpdateTimer = threading.Timer( 1, self.UpdateListAll, [True] )
		self.mAsyncUpdateTimer.start( )


	def StopAsyncUpdate( self ) :
		if self.mAsyncUpdateTimer and self.mAsyncUpdateTimer.isAlive( ) :
			self.mAsyncUpdateTimer.cancel( )
			del self.mAsyncUpdateTimer

		self.mAsyncUpdateTimer = None


	def RestartEPGUpdateTimer( self ) :
		self.StopEPGUpdateTimer( )
		self.StartEPGUpdateTimer( )


	def StartEPGUpdateTimer( self ) :
		self.mEPGUpdateTimer = threading.Timer( E_NOMAL_UPDATE_TIME, self.AsyncEPGUpdateTimer )
		self.mEPGUpdateTimer.start( )


	def StopEPGUpdateTimer( self ) :
		if self.mEPGUpdateTimer and self.mEPGUpdateTimer.isAlive( ) :
			self.mEPGUpdateTimer.cancel( )
			del self.mEPGUpdateTimer

		self.mEPGUpdateTimer = None


	def AsyncEPGUpdateTimer( self ) :	
		self.LoadByCurrentEPG( )

		#recall per 30sec
		self.RestartEPGUpdateTimer( )


	def RestartAsyncEPG( self ) :
		self.StopAsyncEPG( )
		self.StartAsyncEPG( )


	def StartAsyncEPG( self ) :
		self.mAsyncEPGTimer = threading.Timer( 0.5, self.UpdateSelectedPosition )
		self.mAsyncEPGTimer.start( )

		if not self.mChangeMode and self.mOffsetTopIndex != GetOffsetPosition( self.mCtrlBigList ) :
			updateEpgInfo = threading.Timer( 0.05, self.LoadByCurrentEPG )
			updateEpgInfo.start( )


	def StopAsyncEPG( self ) :
		if self.mAsyncEPGTimer and self.mAsyncEPGTimer.isAlive( ) :
			self.mAsyncEPGTimer.cancel( )
			del self.mAsyncEPGTimer

		self.mAsyncEPGTimer = None


	def ToggleTVRadio( self ) :
		serviceType = ElisEnum.E_SERVICE_TYPE_TV
		if self.mUserMode.mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
			serviceType = ElisEnum.E_SERVICE_TYPE_RADIO
			self.mBackupMode.mZappingTV    = deepcopy( self.mUserMode )
			self.mBackupMode.mGroupIndexTV = self.mGroupIndex
			self.mUserMode   = deepcopy( self.mBackupMode.mZappingRadio )
			self.mGroupIndex = self.mBackupMode.mGroupIndexRadio
		else :
			self.mBackupMode.mZappingRadio    = deepcopy( self.mUserMode )
			self.mBackupMode.mGroupIndexRadio = self.mGroupIndex
			self.mUserMode   = deepcopy( self.mBackupMode.mZappingTV )
			self.mGroupIndex = self.mBackupMode.mGroupIndexTV

		if self.mDataCache.Channel_GetCount( serviceType ) < 1 :
			LOG_TRACE( '[SimpleChannelList] pass, channel is None' )
			return False

		self.mEventBus.Deregister( self )
		self.StopEPGUpdateTimer( )

		self.mServiceType = serviceType
		#self.mUserMode.mServiceType = serviceType
		self.mZappingGroupList[ ElisEnum.E_MODE_SATELLITE ] = self.mDataCache.Satellite_GetConfiguredList( )
		self.mZappingGroupList[ ElisEnum.E_MODE_CAS ]       = self.mDataCache.Fta_cas_GetList( serviceType )
		self.mZappingGroupList[ ElisEnum.E_MODE_PROVIDER ]  = self.mDataCache.Provider_GetList( FLAG_ZAPPING_CHANGE, serviceType )
		self.mZappingGroupList[ ElisEnum.E_MODE_FAVORITE ]  = self.mDataCache.Favorite_GetList( FLAG_ZAPPING_CHANGE, serviceType )

		self.GetChannelList( )
		self.InitToChannel( )

		#1.default channel, First Channel
		iChannel = None
		channelIndex = 0
		if self.mChannelList and len( self.mChannelList ) > 0 :
			iChannel = self.mChannelList[0]

		#2.find channel, Exist last Channel
		lastChannelProperty = 'Last TV Number'
		if self.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
			lastChannelProperty = 'Last Radio Number'
		lastChannelNumber = ElisPropertyInt( lastChannelProperty, self.mCommander ).GetProp( )

		fChannel = self.GetChannelByNumber( lastChannelNumber )
		if fChannel :
			chIndex = self.GetChannelByIDs( fChannel.mNumber, fChannel.mSid, fChannel.mTsid, fChannel.mOnid, True )
			if chIndex > -1 :
				iChannel = fChannel
				channelIndex = chIndex

		if iChannel :
			self.mCurrentChannel = iChannel
			self.mDataCache.Channel_SetCurrent( iChannel.mNumber, iChannel.mServiceType )
			#LOG_TRACE( '[SimpleChannelList] tune Channel ch[%s %s] type[%s]'% ( iChannel.mNumber, iChannel.mName, iChannel.mServiceType ) )

		self.ResetControls( )
		self.UpdateList( )
		#self.mCtrlBigList.selectItem( channelIndex )
		#self.UpdateSelectedPosition( )
		LOG_TRACE( '[SimpleChannelList] toggle tv/radio' )

		self.StartEPGUpdateTimer( )
		self.mEventBus.Register( self )

		return True


	def UpdateGroupSlide( self, aMove = 0 ) :
		#sync to groupList
		selectPos = self.mCtrlGroupList.getSelectedPosition( )
		totCount = self.mCtrlGroupSlide.size( )
		if selectPos < 0 :
			LOG_TRACE( 'pass, select none' )
			return

		nextIdx = selectPos - 1

		if aMove != 0 :
			#rewind / forward
			nextIdx = aMove - 1
			if nextIdx < 0 :
				nextIdx = totCount - 1
			elif nextIdx >= totCount :
				nextIdx = 0

		else :
			#sync to up / down / page
			if nextIdx < 0 :
				nextIdx = 0
			elif nextIdx >= totCount :
				nextIdx = totCount

		self.mCtrlGroupSlide.selectItem( nextIdx )
		time.sleep( 0.02 )


	def UpdateShortCutGroup( self, aMove = 1 ) :
		if self.mChangeMode : #show group list
			selectPos = self.mCtrlGroupList.getSelectedPosition( )
			if selectPos < 0 :
				LOG_TRACE( 'pass, select none' )
				return
			nextIdx = selectPos + aMove
			totCount = self.mCtrlGroupList.size( )
			#LOG_TRACE( '[SimpleChannelList]listTotal[%s] selectIdx[%s] nextIdx[%s]'% ( totCount, selectPos, nextIdx ) )
			if nextIdx < 1 :
				nextIdx = totCount - 1
			elif nextIdx >= totCount :
				nextIdx = 1
			self.mCtrlGroupList.selectItem( nextIdx )
			nextGroup = self.mCtrlGroupList.getListItem( nextIdx ).getLabel( )
			time.sleep( 0.02 )
			lblPath = EnumToString( 'mode', self.mChangeMode.mMode )
			#if nextGroup :
			#	lblPath = '%s > [COLOR grey3]%s[/COLOR]'% ( lblPath, nextGroup )
			self.setProperty( 'SimpleChannelPath', lblPath )
			self.UpdateGroupSlide( nextIdx )
			return

		if self.mUserMode.mMode == ElisEnum.E_MODE_ALL :
			LOG_TRACE( '[SimpleChannelList] pass, currrent mode All Channels' )
			return

		groupList = self.mZappingGroupList[self.mUserMode.mMode]
		if not groupList or len( groupList ) < 1 :
			LOG_TRACE( '[SimpleChannelList] pass, short cut group None' )
			return

		if not self.mUserGroup :
			LOG_TRACE( '[SimpleChannelList] pass, current group None' )
			return

		nextIdx = self.mGroupIndex + aMove
		if nextIdx < 0 :
			nextIdx = len( self.mListGroupName ) - 1

		if nextIdx >= len( self.mListGroupName ) :
			nextIdx = 0

		if not ( nextIdx < len( self.mListGroupName ) ) :
			LOG_TRACE( '[SimpleChannelList] error, incorrect index' )
			return

		self.mGroupIndex = nextIdx
		nextGroup = self.mListGroupName[nextIdx]
		if self.mUserMode.mMode == ElisEnum.E_MODE_SATELLITE :
			nextGroup = self.mDataCache.GetFormattedSatelliteName( groupList[nextIdx].mLongitude, groupList[nextIdx].mBand )

		lblPath = EnumToString( 'mode', self.mUserMode.mMode )
		#if nextGroup :
		#	lblPath = '%s > [COLOR grey3]%s[/COLOR]'% ( lblPath, nextGroup )

		self.mCtrlGroupSlide.selectItem( nextIdx )
		self.setProperty( 'SimpleChannelPath', lblPath )
		self.RestartAsyncUpdate( )


	def UpdateShortCutZapping( self, aReqMode = ElisEnum.E_MODE_FAVORITE ) :
		if E_SHOW_GROUP_LIST :
			self.ShowGroupListByMode( aReqMode )
			return

		isAvail = False
		groupList = []
		if self.mUserMode.mMode != aReqMode :
			if aReqMode == ElisEnum.E_MODE_ALL :
				isAvail = True

			else :
				groupList = self.mZappingGroupList[aReqMode]
				if groupList and len( groupList ) > 0 :
					isAvail = True

		else :
			self.UpdateShortCutGroup( )

		if not isAvail :
			LOG_TRACE( '[SimpleChannelList] pass, zapping group None' )
			return

		self.mGroupIndex = 0
		self.mUserMode.mMode = aReqMode
		self.UpdateListAll( True )


	def ShowGroupListByMode( self, aReqMode = ElisEnum.E_MODE_FAVORITE ) :
		groupList = self.mZappingGroupList[aReqMode]
		print 'dhkim test groupList = %s' % groupList
		if not groupList or len( groupList ) < 1 :
			groupList = []
			LOG_TRACE( '[SimpleChannelList] pass, zapping group None' )
		#	return

		self.StopEPGUpdateTimer( )

		currGroupName = self.mUserGroup
		if self.mUserMode.mMode == ElisEnum.E_MODE_SATELLITE :
			currGroupName = self.mDataCache.GetFormattedSatelliteName( self.mUserMode.mSatelliteInfo.mLongitude, self.mUserMode.mSatelliteInfo.mBand )

		loopCount  = 0
		currentIdx = 1
		groupListItems = []
		groupListSlide = []
		self.mChangeMode = deepcopy( self.mUserMode )
		self.mChangeMode.mMode = aReqMode
		groupListItems.append( xbmcgui.ListItem( '%s'% self.mZappingGroupList[ElisEnum.E_MODE_ALL] ) )
		for iGroupInfo in groupList :
			groupName  = ''
			loopCount += 1
			fastScan = False

			if aReqMode == ElisEnum.E_MODE_FAVORITE :
				groupName = iGroupInfo.mGroupName
				if iGroupInfo.mServiceType > ElisEnum.E_SERVICE_TYPE_RADIO :
					fastScan = True

			elif aReqMode == ElisEnum.E_MODE_SATELLITE :
				groupName = self.mDataCache.GetFormattedSatelliteName( iGroupInfo.mLongitude, iGroupInfo.mBand )

			elif aReqMode == ElisEnum.E_MODE_CAS :
				groupName = iGroupInfo.mName

			elif aReqMode == ElisEnum.E_MODE_PROVIDER :
				groupName = iGroupInfo.mProviderName

			if not groupName :
				LOG_TRACE( '[SimpleChannelList] pass, empty group name' )
				continue

			if self.mUserMode.mMode != ElisEnum.E_MODE_ALL and groupName == currGroupName :
				currentIdx = loopCount
				#LOG_TRACE( '[SimpleChannelList] current group, currentIdx[%s] groupName[%s]'% ( currentIdx, groupName ) )

			listItem = xbmcgui.ListItem( '%s'% groupName )
			listItem2= xbmcgui.ListItem( '%s'% groupName )
			if fastScan :
				listItem.setProperty( E_XML_PROPERTY_FASTSCAN, E_TAG_TRUE )

			groupListItems.append( listItem )
			groupListSlide.append( listItem2 )

		self.mCtrlGroupList.reset( )
		self.mCtrlGroupList.addItems( groupListItems )
		self.setProperty( 'SimpleChannelGroup', E_TAG_TRUE )
		self.mCtrlGroupList.selectItem( currentIdx )
		self.setFocusId( LIST_ID_BIG_GROUP )

		lblPath = EnumToString( 'mode', aReqMode )
		self.setProperty( 'SimpleChannelPath', lblPath )
		self.setProperty( 'SelectedGroup', '%s'% ( currentIdx + 1 ) )

		self.mCtrlGroupSlide.reset( )
		self.mCtrlGroupSlide.addItems( groupListSlide )
		self.mCtrlGroupSlide.selectItem( currentIdx - 1 )
		slideVisible = E_TAG_FALSE
		if groupListSlide :
			slideVisible = E_TAG_TRUE
		self.setProperty( 'ShowGroupSlide', slideVisible )


	def GetSelectGroup( self ) :
		isAvail = True
		isSelect = -1
		try :
			if not self.mChangeMode :
				raise Exception, '[SimpleChannelList] pass, group mode None'

			groupList = self.mZappingGroupList[self.mChangeMode.mMode]
			if not groupList or len( groupList ) < 1 :
				raise Exception, '[SimpleChannelList] pass, group list None'

			isSelect = self.mCtrlGroupList.getSelectedPosition( )
			LOG_TRACE( '[SimpleChannelList] select group[%s] currIdx[%s]'% ( isSelect, self.mGroupIndex ) )
			if isSelect < 0 :
				raise Exception, '[SimpleChannelList] pass, select None'

			if isSelect == 0 and self.mUserMode.mMode == ElisEnum.E_MODE_ALL :
				lblPath = EnumToString( 'mode', self.mUserMode.mMode )
				self.setProperty( 'SimpleChannelPath', lblPath )
				self.setProperty( 'ShowGroupSlide', E_TAG_FALSE )
				raise Exception, 'pass, select same(all)'

			if self.mChangeMode.mMode == self.mUserMode.mMode :
				if isSelect > 0 and ( isSelect - 1 ) == self.mGroupIndex :
					raise Exception, 'pass, selected same'

		except Exception, e :
			isAvail = False
			LOG_ERR( '[SimpleChannelList] except[%s]'% e )

		if isAvail :
			self.mGroupIndex = 0
			self.mUserMode.mMode = self.mChangeMode.mMode
			if isSelect == 0 :
				self.mUserMode.mMode = ElisEnum.E_MODE_ALL

			else :
				isSelect -= 1

			self.mGroupIndex = isSelect
			self.UpdateListAll( True )

		self.mChangeMode = None
		self.setProperty( 'SimpleChannelGroup', E_TAG_FALSE )
		self.setFocusId( LIST_ID_BIG_CHANNEL )
		self.StartEPGUpdateTimer( )


	def GetChannelList( self ) :
		ret = True

		self.OpenBusyDialog( )
		try :
			channelList = []
			aMode = self.mUserMode.mMode
			aType = self.mUserMode.mServiceType
			aSort = self.mUserMode.mSortingMode

			groupInfo = None
			if aMode != ElisEnum.E_MODE_ALL :
				groupInfo = self.mZappingGroupList[self.mUserMode.mMode][self.mGroupIndex]

			if aMode == ElisEnum.E_MODE_ALL :
				channelList = self.mDataCache.Channel_GetList( FLAG_ZAPPING_CHANGE, aType, aMode, aSort )

			elif aMode == ElisEnum.E_MODE_SATELLITE :
				self.mUserMode.mSatelliteInfo = groupInfo
				channelList = self.mDataCache.Channel_GetListBySatellite( aType, aMode, aSort, groupInfo.mLongitude, groupInfo.mBand )

			elif aMode == ElisEnum.E_MODE_CAS :
				self.mUserMode.mCasInfo = groupInfo
				channelList = self.mDataCache.Channel_GetListByFTACas( aType, aMode, aSort, groupInfo.mCAId )

			elif aMode == ElisEnum.E_MODE_FAVORITE :
				self.mUserMode.mFavoriteGroup = groupInfo
				channelList = self.mDataCache.Channel_GetListByFavorite( aType, aMode, aSort, groupInfo.mGroupName )

			elif aMode == ElisEnum.E_MODE_NETWORK :
				pass

			elif aMode == ElisEnum.E_MODE_PROVIDER :
				self.mUserMode.mProviderInfo = groupInfo
				channelList = self.mDataCache.Channel_GetListByProvider( aType, aMode, aSort, groupInfo.mProviderName )

			self.mChannelList = channelList

		except Exception, e :
			LOG_ERR( '[SimpleChannelList] except[%s]'% e )
			ret = False

		self.CloseBusyDialog( )

		return ret


	def SetModeToChange( self ) :
		isSave = False
		if self.mUserMode.mMode != self.mCurrentMode.mMode or \
		   self.mUserMode.mServiceType != self.mCurrentMode.mServiceType :
			isSave = True

		if self.mCurrentGroup and self.mUserGroup and self.mCurrentGroup != self.mUserGroup :
			isSave = True

		if isSave and self.mChannelList and len( self.mChannelList ) > 0 :
			isSave = True

		else :
			isSave = False

		if isSave :
			self.OpenBusyDialog( )
			ret = self.mDataCache.Zappingmode_SetCurrent( self.mUserMode )
			if ret :
				#data cache re-load
				self.mDataCache.LoadZappingmode( )
				self.mDataCache.LoadZappingList( )
				#self.mDataCache.LoadChannelList( )
				self.mDataCache.RefreshCacheByChannelList( self.mChannelList )
				self.mDataCache.SetChannelReloadStatus( True )
				self.mDataCache.Channel_ResetOldChannelList( )
			self.CloseBusyDialog( )



