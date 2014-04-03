from pvr.gui.WindowImport import *
import traceback

E_SIMPLE_CHANNEL_LIST_BASE_ID		=  WinMgr.WIN_ID_SIMPLE_CHANNEL_LIST * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID
LIST_ID_BIG_CHANNEL					= E_SIMPLE_CHANNEL_LIST_BASE_ID + 1000


E_NOMAL_UPDATE_TIME				= 30
E_SHORT_UPDATE_TIME				= 1

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
		self.mEPGHashTable = {}
		self.mEPGList	= []	
		self.mListItems = []		
		self.mFirstTune = False
		self.mEPGUpdateTimer = None
		self.mEnableAysncTimer = False
		self.mBackupMode = BackupModeClass( )
	
	def onInit( self ) :
		self.SetActivate( True )
		self.SetFrontdisplayMessage( MR_LANG('Channel List') )
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.CheckMediaCenter( )

		self.mChannelListHash = {}
		self.mChannelNumbersHash = {}
		self.mEnableAysncTimer = True
		self.mFirstTune = False
		self.mEPGUpdateTimer = None
		self.mAsyncUpdateTimer = None
		try :
			self.mAutoConfirm = int( GetSetting( 'AUTO_CONFIRM_CHANNEL' ) )

		except Exception, e :
			LOG_ERR( '[SimpleChannelList] except[%s]'% e )
			self.mAutoConfirm = False

		self.mCtrlBigList = self.getControl( LIST_ID_BIG_CHANNEL )
		#self.SetSingleWindowPosition( E_SIMPLE_CHANNEL_LIST_BASE_ID )
		#self.SetPipScreen( )

		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( )
		self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
		self.mServiceType	 = self.mCurrentMode.mServiceType

		LOG_TRACE( '[SimpleChannelList] ZeppingMode(%d,%d,%d)' %( self.mCurrentMode.mServiceType, self.mCurrentMode.mMode, self.mCurrentMode.mSortingMode ) )
		self.mChannelList = self.mDataCache.Channel_GetList( )

		self.mUserMode         = deepcopy( self.mCurrentMode )
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

		self.UpdateAllEPGList( )

		self.mEventBus.Register( self )

		self.StartEPGUpdateTimer( )

		if not self.mInitialized :
			self.mInitialized = True
			self.mBackupMode.mZappingTV    = deepcopy( self.mCurrentMode )
			self.mBackupMode.mZappingRadio = deepcopy( self.mCurrentMode )
			self.mBackupMode.mGroupIndexTV    = 0
			self.mBackupMode.mGroupIndexRadio = 0
			self.mBackupMode.mZappingRadio.mMode = ElisEnum.E_MODE_ALL
			self.mBackupMode.mZappingRadio.mServiceType = ElisEnum.E_SERVICE_TYPE_RADIO
			self.mBackupMode.mZappingRadio.mSortingMode = self.mCurrentMode.mSortingMode

		self.setFocusId( LIST_ID_BIG_CHANNEL )
		self.setProperty( 'ZappingModeInfo', E_TAG_TRUE )


	def ResetControls( self ) :
		self.mListItems = []


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		self.GetFocusId( )
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		#LOG_TRACE('onAction=%d' %actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR:
			self.Close( )

		elif actionId == Action.ACTION_MOVE_LEFT or actionId == Action.ACTION_MOVE_RIGHT:
			self.Close( )

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN or actionId == Action.ACTION_PAGE_UP  or actionId == Action.ACTION_PAGE_DOWN:
			self.UpdateSelectedPosition( )

		elif actionId == Action.ACTION_MBOX_TVRADIO :
			self.mEventBus.Deregister( self )
			self.StopEPGUpdateTimer( )

			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.ToggleTVRadio( )
				if ret :
					self.SetRadioScreen( self.mServiceType )

				else :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No channels available for the selected mode' ) )
					dialog.doModal( )

			self.StartEPGUpdateTimer( )
			self.mEventBus.Register( self )			

		elif actionId == Action.ACTION_SELECT_ITEM :
			if self.mFocusId  == LIST_ID_BIG_CHANNEL :
				self.Tune( )

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
		#if aControlId  == LIST_ID_BIG_CHANNEL :
		#	self.Tune( )


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			if aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
				#if self.mIsUpdateEnable == True	:
				#LOG_TRACE( '[SimpleChannelList] record start/stop event' )
				self.StopEPGUpdateTimer( )
				self.UpdateListUpdateOnly( )
				self.StartEPGUpdateTimer( E_SHORT_UPDATE_TIME )

			elif aEvent.getName( ) == ElisEventCurrentEITReceived.getName( ) :
				if self.mFirstTune == True :
					self.mFirstTune = False
					#LOG_TRACE( '[SimpleChannelList]--------------- First Tune -----------------' )
					self.StartEPGUpdateTimer( E_SHORT_UPDATE_TIME )			


	def Close( self ) :
		self.mEnableAysncTimer = False
		self.mFirstTune = False
		self.mEventBus.Deregister( self )
		self.StopAsyncUpdate( )
		self.StopEPGUpdateTimer( )

		self.SetModeToChange( )
		WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )


	def Flush( self ) :
		self.mEPGList = []
		self.mEPGHashTable = {}


	def UpdateAllEPGList( self, aLoadChannel = False ) :
		self.Flush( )

		if aLoadChannel :
			self.mEnableAysncTimer = False
			self.ResetControls( )
			self.GetChannelList( )
			self.mEnableAysncTimer = True

		self.Load( )
		self.UpdateList( )
		#threading.Timer( 0.5, self.UpdateSelectedPosition ).start( )


	def Load( self ) :
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
			currentIdx = -1
			for groupName in self.mListGroupName :
				if groupName == self.mUserGroup :
					self.mGroupIndex = loopCount
					self.mCurrentGroup = self.mUserGroup
					break

				loopCount += 1

		if self.mUserGroup :
			lblPath = '%s > %s'% ( lblPath, self.mUserGroup )
		self.setProperty( 'SimpleChannelPath', lblPath )

		self.mChannelListHash = {}
		self.mChannelNumbersHash = {}
		if self.mChannelList :
			idxCount = 0
			for iChannel in self.mChannelList :
				hashKey = '%d:%d:%d:%d'% ( iChannel.mNumber, iChannel.mSid, iChannel.mTsid, iChannel.mOnid )
				self.mChannelListHash[hashKey] = [iChannel, idxCount]
				self.mChannelNumbersHash[iChannel.mNumber] = iChannel
				idxCount += 1

		#self.mLock.acquire( )
		try :
			self.mEPGList = self.mDataCache.Epgevent_GetCurrentListByEpgCF( self.mServiceType )

		except Exception, e :
			LOG_ERR( '[SimpleChannelList] except[%s]'% e )

		#self.mLock.release( )
		if self.mEPGList == None or len ( self.mEPGList ) <= 0 :
			return

		LOG_TRACE( '[SimpleChannelList] self.mEPGList COUNT[%s]'% len( self.mEPGList ) )

		for epg in self.mEPGList :
			hashKey = '%d:%d:%d'% ( epg.mSid, epg.mTsid, epg.mOnid )
			self.mEPGHashTable[ hashKey ] = epg


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


	def UpdateListUpdateOnly( self ) :
		self.UpdateList( True )


	def UpdateList( self, aUpdateOnly=False ) :
		if not self.mChannelList or len( self.mChannelList ) < 1 :
			self.mCtrlBigList.reset( )
			self.mListItems = []
			xbmc.executebuiltin( 'container.refresh' )			
			return

		aUpdateOnly = True
		if not self.mListItems :
			aUpdateOnly = False
			#self.mLock.acquire( )
			self.mListItems = []
			#self.mLock.release( )
		else :
			if len( self.mChannelList ) != len( self.mListItems ) :
				LOG_TRACE( '[SimpleChannelList] UpdateOnly------------>Create' )
				aUpdateOnly = False 
				#self.mLock.acquire( )
				self.mListItems = []
				#self.mLock.release( )

		LOG_TRACE( '[SimpleChannelList] LAEL98 UPDATE CONTAINER aUpdateOnly[%s]'% aUpdateOnly )
				
		currentTime = self.mDataCache.Datetime_GetLocalTime( )
		runningTimers = self.mDataCache.Timer_GetRunningTimers( )		

		strNoEvent = MR_LANG( 'No event' )

		if aUpdateOnly == False :
			self.mListItems = []
			for iChannel in self.mChannelList :
				listItem = xbmcgui.ListItem( '', '' )
				self.mListItems.append( listItem )

			self.mCtrlBigList.addItems( self.mListItems )

		#self.mCtrlBigList.setVisible( False )
		loopCount = 0
		for iChannel in self.mChannelList :
			iChNumber = iChannel.mNumber
			if E_V1_2_APPLY_PRESENTATION_NUMBER :
				iChNumber = self.mDataCache.CheckPresentationNumber( iChannel )

			if self.IsRunningTimer( runningTimers, iChannel ) :
				tempChannelName = '[COLOR=red]%04d %s[/COLOR]' %( iChNumber, iChannel.mName )
			else :
				tempChannelName = '%04d %s' %( iChNumber, iChannel.mName )

			hasEpg = False

			try :
				epgEvent = self.GetEPGByIds( iChannel.mSid, iChannel.mTsid, iChannel.mOnid )

				if self.mListItems and loopCount < len( self.mListItems ) :
					if epgEvent :
						hasEpg = True
						listItem = self.mListItems[loopCount]
						listItem.setLabel( tempChannelName )
						listItem.setLabel2( epgEvent.mEventName )

						epgStart = epgEvent.mStartTime + self.mLocalOffset
						listItem.setProperty( 'HasEvent', E_TAG_TRUE )
						listItem.setProperty( 'Percent', '%s' %self.CalculateProgress( currentTime, epgStart, epgEvent.mDuration  ) )

					else :
						listItem = self.mListItems[loopCount]
						listItem.setLabel( tempChannelName )
						listItem.setLabel2( strNoEvent )
						listItem.setProperty( 'HasEvent', E_TAG_FALSE )

				#add channel logo
				if E_USE_CHANNEL_LOGO == True :
					logo = '%s_%s'% ( iChannel.mCarrier.mDVBS.mSatelliteLongitude, iChannel.mSid )
					listItem.setProperty( 'ChannelLogo', self.mChannelLogo.GetLogo( logo, self.mServiceType ) )

			except Exception, ex :
				LOG_ERR( '[SimpleChannelList] except[%s]'% traceback.format_exc() )

			if aUpdateOnly == True and  loopCount == 8 :
				xbmc.executebuiltin( 'container.refresh' )
				LOG_TRACE( '[SimpleChannelList] LAEL98 UPDATE CONTAINER' )

			loopCount += 1

		xbmc.executebuiltin( 'container.refresh' )
		if not aUpdateOnly :
			self.FocusCurrentChannel( )
		#self.mCtrlBigList.setVisible( True )


	def UpdateSelectedPosition( self ) :
		selectedPos = self.mCtrlBigList.getSelectedPosition( )

		lblPos = 0
		if selectedPos < 0 :
			lblPos = 0
		else :
			lblPos = selectedPos + 1

		self.setProperty( 'SelectedPosition', '%s'% lblPos )


	def FocusCurrentChannel( self ) :
		if not self.mChannelList or ( not self.mCurrentChannel ) :
			return

		fucusIndex = self.GetChannelByIDs( self.mCurrentChannel.mNumber, self.mCurrentChannel.mSid, self.mCurrentChannel.mTsid, self.mCurrentChannel.mOnid, True )
		if fucusIndex > -1 :
			self.mCtrlBigList.selectItem( fucusIndex )

		self.UpdateSelectedPosition( )
		LOG_TRACE( '--------------------ch[%s %s] idx[%s]'% ( self.mCurrentChannel.mNumber, self.mCurrentChannel.mName, fucusIndex ) )


	def CalculateProgress( self, aCurrentTime, aEpgStart, aDuration  ) :
		startTime = aEpgStart
		endTime = aEpgStart + aDuration
		
		pastDuration = endTime - aCurrentTime

		if aCurrentTime > endTime : #past
			return 100

		elif aCurrentTime < startTime : #future
			return 0

		if pastDuration < 0 : #past
			pastDuration = 0

		if aDuration > 0 :
			percent = 100 - ( pastDuration * 100.0 / aDuration )
		else :
			percent = 0

		#LOG_TRACE( '[SimpleChannelList] Percent[%s]'% percent )
		return percent


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
			channel = self.mChannelList[ selectedPos ]
			if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
				self.mDataCache.Player_Stop( )
			else :
				if self.mCurrentChannel.mNumber == channel.mNumber :
					self.Close( )
					return

			if not self.mDataCache.Get_Player_AVBlank( ) :
				self.mDataCache.Player_AVBlank( True )

			self.mDataCache.Channel_SetCurrent( channel.mNumber, channel.mServiceType )
			self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
			self.mFirstTune = True

			if self.mAutoConfirm :
				self.Close( )
				return

		self.RestartEPGUpdateTimer( )


	def RestartEPGUpdateTimer( self, aTimeout=E_NOMAL_UPDATE_TIME ) :
		self.StopEPGUpdateTimer( )
		self.StartEPGUpdateTimer( aTimeout )


	def StartEPGUpdateTimer( self, aTimeout=E_NOMAL_UPDATE_TIME ) :
		self.mEPGUpdateTimer = threading.Timer( aTimeout, self.AsyncEPGUpdateTimer )
		self.mEPGUpdateTimer.start( )
	

	def StopEPGUpdateTimer( self ) :
		if self.mEPGUpdateTimer and self.mEPGUpdateTimer.isAlive( ) :
			self.mEPGUpdateTimer.cancel( )
			del self.mEPGUpdateTimer
			
		self.mEPGUpdateTimer = None


	def AsyncEPGUpdateTimer( self ) :	
		if self.mEPGUpdateTimer == None :
			LOG_WARN( 'EPG update timer expired' )
			return

		if self.mEnableAysncTimer == False :
			LOG_WARN( '[SimpleChannelList]EnableAysncTimer is False' )
			return

		self.Load( )

		self.UpdateListUpdateOnly( )
		self.RestartEPGUpdateTimer( )


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

		self.mServiceType = serviceType
		#self.mUserMode.mServiceType = serviceType
		self.mZappingGroupList[ ElisEnum.E_MODE_SATELLITE ] = self.mDataCache.Satellite_GetConfiguredList( )
		self.mZappingGroupList[ ElisEnum.E_MODE_CAS ]       = self.mDataCache.Fta_cas_GetList( serviceType )
		self.mZappingGroupList[ ElisEnum.E_MODE_PROVIDER ]  = self.mDataCache.Provider_GetList( FLAG_ZAPPING_CHANGE, serviceType )
		self.mZappingGroupList[ ElisEnum.E_MODE_FAVORITE ]  = self.mDataCache.Favorite_GetList( FLAG_ZAPPING_CHANGE, serviceType )

		self.GetChannelList( )
		self.Load( )

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

		return True


	def RestartAsyncUpdate( self ) :
		self.StopAsyncUpdate( )
		self.StartAsyncUpdate( )


	def StartAsyncUpdate( self ) :
		self.mAsyncUpdateTimer = threading.Timer( 1, self.UpdateAllEPGList, [True] )
		self.mAsyncUpdateTimer.start( )


	def StopAsyncUpdate( self ) :
		if self.mAsyncUpdateTimer and self.mAsyncUpdateTimer.isAlive( ) :
			self.mAsyncUpdateTimer.cancel( )
			del self.mAsyncUpdateTimer

		self.mAsyncUpdateTimer = None


	def UpdateShortCutGroup( self, aMove = 1 ) :
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
		if nextGroup :
			lblPath = '%s > [COLOR grey3]%s[/COLOR]'% ( lblPath, nextGroup )

		self.setProperty( 'SimpleChannelPath', lblPath )
		self.RestartAsyncUpdate( )


	def UpdateShortCutZapping( self, aReqMode = ElisEnum.E_MODE_FAVORITE ) :
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
		self.UpdateAllEPGList( True )


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



