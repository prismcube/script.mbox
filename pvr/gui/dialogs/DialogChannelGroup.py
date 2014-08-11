from pvr.gui.WindowImport import *
import time

E_CONTROL_ID_LIST2 = E_BASE_WINDOW_ID + 3960

DIALOG_BUTTON_CLOSE_ID = 3901
DIALOG_HEADER_LABEL_ID = 3902
DIALOG_LABEL_POS_ID = 3903
DIALOG_BUTTON_OK_ID = 3904


class DialogChannelGroup( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )	
		self.mIsOk = None
		self.mListItems = []
		self.mDefaultList = []
		self.mTitle = ''
		self.mDefaultFocus = 0
		self.mListType = E_MODE_DEFAULT_LIST
		self.mZappingGroupList = [ MR_LANG( 'All Channels' ), [ElisIFavoriteGroup()], [ElisINetworkInfo()], [ElisISatelliteInfo()], [ElisIChannelCASInfo()], [ElisIProviderInfo()] ]
		self.mTitleMode = [ MR_LANG( 'All Channels' ), MR_LANG( 'Favorite group' ), MR_LANG( 'Network' ), MR_LANG( 'Satellite' ), MR_LANG( 'FTA/CAS' ), MR_LANG( 'Provider' ) ]
		self.mChangeMode = ElisEnum.E_MODE_ALL

	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.setProperty( 'DialogDrawFinished', E_TAG_FALSE )

		self.mCurrentIdx   = -1
		self.mLastSelected = -1
		self.mCtrlList = self.getControl( E_CONTROL_ID_LIST2 )
		self.mCtrlPos =  self.getControl( DIALOG_LABEL_POS_ID )

		if self.mListType == E_MODE_ZAPPING_GROUP :
			self.InitGroup( )
			self.setProperty( 'ZappingModeInfo', E_TAG_TRUE )

		else :
			self.DrawDefault( )

		#self.mEventBus.Register( self )

		self.setProperty( 'DialogDrawFinished', E_TAG_TRUE )
		self.setFocusId( E_CONTROL_ID_LIST2 )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.mIsOk = actionId
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.mLastSelected = -1
			self.Close( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT or actionId == Action.ACTION_MOVE_RIGHT :
			pass

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN or \
			 actionId == Action.ACTION_PAGE_UP or actionId == Action.ACTION_PAGE_DOWN :

			idx = self.mCtrlList.getSelectedPosition( )
			self.mCtrlPos.setLabel( '%s'% ( idx + 1 ) )

		elif actionId == Action.ACTION_STOP :
			self.mLastSelected = -1
			self.Close( )

		elif actionId == Action.ACTION_PLAYER_PLAY or actionId == Action.ACTION_PAUSE :
			self.mLastSelected = -1
			self.Close( )

		elif actionId == Action.ACTION_COLOR_RED :
			self.DrawItemByGroups( ElisEnum.E_MODE_SATELLITE )

		elif actionId == Action.ACTION_COLOR_GREEN :
			self.DrawItemByGroups( ElisEnum.E_MODE_CAS )

		elif actionId == Action.ACTION_COLOR_YELLOW :
			self.DrawItemByGroups( ElisEnum.E_MODE_PROVIDER )

		elif actionId == Action.ACTION_COLOR_BLUE :
			self.DrawItemByGroups( ElisEnum.E_MODE_FAVORITE )


	def onClick( self, aControlId ) :
		if aControlId == DIALOG_BUTTON_CLOSE_ID :
			self.mLastSelected = -1
			self.Close( )

		elif aControlId == E_CONTROL_ID_LIST2 :
			self.SelectItem( )
			self.Close( )

		elif aControlId == DIALOG_BUTTON_OK_ID :
			self.Close( )


	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowDialogId( ) :
			if aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or \
			   aEvent.getName( ) == ElisEventRecordingStopped.getName( ) or \
			   aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
				xbmc.executebuiltin('xbmc.Action(stop)')


	def DrawDefault( self ) :
		self.mCtrlList.reset( )
		self.getControl( DIALOG_HEADER_LABEL_ID ).setLabel( self.mTitle )

		if not self.mDefaultList or len( self.mDefaultList ) < 1 :
			LOG_TRACE( 'No item' )
			return

		if self.mListType == E_MODE_FAVORITE_GROUP :
			for iFavGroup in self.mDefaultList :
				listItem = xbmcgui.ListItem( '%s'% iFavGroup.mGroupName )
				if iFavGroup.mServiceType > ElisEnum.E_SERVICE_TYPE_RADIO :
					listItem.setProperty( E_XML_PROPERTY_FASTSCAN, E_TAG_TRUE )

				self.mListItems.append( listItem )

		else :
			#default list
			for item in self.mDefaultList :
				listItem = xbmcgui.ListItem( '%s'% item )
				self.mListItems.append( listItem )

		self.mCtrlList.addItems( self.mListItems )
		self.mCtrlList.selectItem( self.mDefaultFocus )
		self.mCtrlPos.setLabel( '%s'% ( self.mDefaultFocus + 1 ) )


	def DrawItemByGroups( self, aReqMode = None ) :
		if self.mListType != E_MODE_ZAPPING_GROUP :
			LOG_TRACE( 'pass, not zapping group. List type default' )
			return

		self.mCtrlList.reset( )
		self.mListItems = []
		self.mDefaultList = []

		if not aReqMode :
			aReqMode = self.mZappingMode.mMode

		self.getControl( DIALOG_HEADER_LABEL_ID ).setLabel( self.mTitleMode[ aReqMode ] )
		defaultFocus = self.LoadToGroup( aReqMode )

		if defaultFocus > -1 :
			self.mCurrentIdx = defaultFocus
			self.mCtrlList.addItems( self.mListItems )
			self.mCtrlList.selectItem( defaultFocus )
			#idx = self.mCtrlList.getSelectedPosition( )

		self.mCtrlPos.setLabel( '%s'% ( defaultFocus + 1 ) )


	def SelectItem( self ) :
		idx = 0
		isExist = False

		if not self.mDefaultList or len( self.mDefaultList ) < 1 or \
		   not self.mListItems or len( self.mListItems ) < 1 :
			return

		aPos = self.mCtrlList.getSelectedPosition( )
		self.mLastSelected = aPos


	def SetDefaultProperty( self, aListType = E_MODE_DEFAULT_LIST, aTitle = 'SELECT', aList = None, aDefaultFocus = 0 ) :
		self.mTitle = aTitle
		self.mDefaultList = aList
		self.mDefaultFocus = aDefaultFocus
		self.mListType = aListType


	def GetSelectedList( self ) :
		return self.mLastSelected


	def GetCloseStatus( self ) :
		return self.mIsOk


	def Close( self ) :
		#self.mEventBus.Deregister( self )
		if self.mListType == E_MODE_ZAPPING_GROUP :
			isFail = self.DoChangeToZappingMode( )
			if isFail :
				LOG_TRACE( 'Failed change, try again or another' )
				return

		self.CloseDialog( )


	def InitGroup( self ) :
		self.mZappingMode = self.mDataCache.Zappingmode_GetCurrent( )
		self.mChangeMode = self.mZappingMode.mMode

		self.mZappingGroupList[ ElisEnum.E_MODE_FAVORITE ]  = self.mDataCache.Favorite_GetList( )
		#self.mZappingGroupList[ ElisEnum.E_MODE_NETWORK ] # reserved
		self.mZappingGroupList[ ElisEnum.E_MODE_SATELLITE ] = self.mDataCache.Satellite_GetConfiguredList( )
		self.mZappingGroupList[ ElisEnum.E_MODE_CAS ]       = self.mDataCache.Fta_cas_GetList( )
		self.mZappingGroupList[ ElisEnum.E_MODE_PROVIDER ]  = self.mDataCache.Provider_GetList( )

		if self.mZappingMode.mMode == ElisEnum.E_MODE_ALL :
			self.mChangeMode = ElisEnum.E_MODE_FAVORITE

		self.DrawItemByGroups( self.mChangeMode )


	def LoadToGroup( self, aMode = ElisEnum.E_MODE_FAVORITE ) :

		#check AllChannels
		"""
		allChannels = self.mDataCache.Channel_GetAllChannels( self.mZappingMode.mServiceType, True )
		if not allChannels or len( allChannels ) < 1 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No channels available' ) )
			dialog.doModal( )
			return -1
		"""
		if not self.mZappingGroupList[aMode] or len( self.mZappingGroupList[aMode] ) < 1 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No group available' ) )
			dialog.doModal( )
			return -1

		#check fav groups
		countIdx = 0
		currentIdx = 0
		currGroup = ''
		self.mChangeMode = aMode
		self.mDefaultList = [self.mZappingGroupList[ElisEnum.E_MODE_ALL]]
		self.mListItems.append( xbmcgui.ListItem( '%s'% self.mZappingGroupList[ElisEnum.E_MODE_ALL] ) )
		for iGroupInfo in self.mZappingGroupList[aMode] :
			groupName = ''
			countIdx += 1
			fastScan = False

			if aMode == ElisEnum.E_MODE_FAVORITE :
				groupName = iGroupInfo.mGroupName
				currGroup = self.mZappingMode.mFavoriteGroup.mGroupName
				if iGroupInfo.mServiceType > ElisEnum.E_SERVICE_TYPE_RADIO :
					fastScan = True

			elif aMode == ElisEnum.E_MODE_SATELLITE :
				groupName = self.mDataCache.GetFormattedSatelliteName( iGroupInfo.mLongitude, iGroupInfo.mBand )
				currGroup = self.mDataCache.GetFormattedSatelliteName( self.mZappingMode.mSatelliteInfo.mLongitude, self.mZappingMode.mSatelliteInfo.mBand )

			elif aMode == ElisEnum.E_MODE_CAS :
				groupName = iGroupInfo.mName
				currGroup = self.mZappingMode.mCasInfo.mName

			elif aMode == ElisEnum.E_MODE_PROVIDER :
				groupName = iGroupInfo.mProviderName
				currGroup = self.mZappingMode.mProviderInfo.mProviderName

			if not groupName :
				LOG_TRACE( 'passed, empty group name' )
				continue

			if self.mZappingMode.mMode != ElisEnum.E_MODE_ALL and groupName == currGroup :
				currentIdx = countIdx
				LOG_TRACE( '------------------currentIdx[%s] groupName[%s]'% ( currentIdx, groupName ) )

			listItem = xbmcgui.ListItem( '%s'% groupName )
			if fastScan :
				listItem.setProperty( E_XML_PROPERTY_FASTSCAN, E_TAG_TRUE )

			self.mListItems.append( listItem )
			self.mDefaultList.append( groupName )

		return currentIdx


	def DoChangeToZappingMode( self ) :
		isFail = False
		lblLine = MR_LANG( 'Could not change the group' )

		isSelect = self.mLastSelected

		LOG_TRACE('---------------select[%s] defaultIdx[%s]'% ( isSelect, self.mCurrentIdx ) )
		if isSelect < 0 :
			LOG_TRACE( 'passed, back or cancel' )
			return isFail

		LOG_TRACE( '----------------changeMode[%s] currentMode[%s]'% ( self.mChangeMode, self.mZappingMode.mMode ) )
		if isSelect == 0 :
			if self.mZappingMode.mMode == ElisEnum.E_MODE_ALL :
				LOG_TRACE( 'passed, select same(all)' )
				return isFail

			self.mChangeMode = ElisEnum.E_MODE_ALL

		if self.mChangeMode == self.mZappingMode.mMode :
			if isSelect == self.mCurrentIdx :
				LOG_TRACE( 'passed, selected same' )
				return isFail

		xbmc.executebuiltin( 'ActivateWindow(busydialog)' )

		try :
			groupInfo = []
			instanceList = []
			zappingmode = deepcopy( self.mZappingMode )

			zappingmode.mMode = self.mChangeMode
			zappingGroup = self.mZappingGroupList[self.mChangeMode]
			if self.mChangeMode != ElisEnum.E_MODE_ALL :
				isSelect -= 1
				groupInfo = zappingGroup[isSelect]

			aKeyword  = ''
			aInstance = True
			aMode = zappingmode.mMode
			aType = zappingmode.mServiceType
			aSort = zappingmode.mSortingMode

			if self.mChangeMode == ElisEnum.E_MODE_ALL :
				instanceList = self.mDataCache.Channel_GetList( FLAG_ZAPPING_CHANGE, aType, aMode, aSort, aKeyword, aInstance )

			elif self.mChangeMode == ElisEnum.E_MODE_SATELLITE :
				zappingmode.mSatelliteInfo = groupInfo
				instanceList = self.mDataCache.Channel_GetListBySatellite( aType, aMode, aSort, groupInfo.mLongitude, groupInfo.mBand, aKeyword, aInstance )

			elif self.mChangeMode == ElisEnum.E_MODE_CAS :
				zappingmode.mCasInfo = groupInfo
				instanceList = self.mDataCache.Channel_GetListByFTACas( aType, aMode, aSort, groupInfo.mCAId, aKeyword, aInstance )

			elif self.mChangeMode == ElisEnum.E_MODE_FAVORITE :
				zappingmode.mFavoriteGroup = groupInfo
				instanceList = self.mDataCache.Channel_GetListByFavorite( aType, aMode, aSort, groupInfo.mGroupName, aKeyword, aInstance )

			elif self.mChangeMode == ElisEnum.E_MODE_NETWORK :
				pass

			elif self.mChangeMode == ElisEnum.E_MODE_PROVIDER :
				zappingmode.mProviderInfo = groupInfo
				instanceList = self.mDataCache.Channel_GetListByProvider( aType, aMode, aSort, groupInfo.mProviderName, aKeyword, aInstance )

			if not instanceList or len( instanceList ) < 1 :
				isFail = True
				lblLine = MR_LANG( 'No channels available' )
				raise Exception, 'Failed, No channels available'

			#set change
			ret = self.mDataCache.Zappingmode_SetCurrent( zappingmode )
			if ret :
				self.mDataCache.Channel_Save( )

				#data cache re-load
				self.mDataCache.LoadZappingmode( )
				self.mDataCache.LoadZappingList( )
				#self.mDataCache.LoadChannelList( )
				self.mDataCache.RefreshCacheByChannelList( instanceList )
				self.mDataCache.SetChannelReloadStatus( True )
				self.mDataCache.Channel_ResetOldChannelList( )

				# channel tune, default 1'st
				iChannelList = self.mDataCache.Channel_GetList( )
				if iChannelList and len( iChannelList ) > 0 :
					iChannel = self.mDataCache.Channel_GetCurrent( )
					if iChannel and iChannel.mError == 0 :
						fChannel = self.mDataCache.Channel_GetCurr( iChannel.mNumber )
						if fChannel and fChannel.mError == 0 :
							iChannel = fChannel
						else :
							iChannel = iChannelList[0]
					else :
						iChannel = iChannelList[0]

					self.mDataCache.Channel_SetCurrent( iChannel.mNumber, iChannel.mServiceType, None, True )

				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE, WinMgr.WIN_ID_NULLWINDOW )

			else :
				isFail = True
				lblLine = MR_LANG( 'Failed to change the group' )
				raise Exception, 'Failed Zappingmode_SetCurrent'

		except Exception, e :
			LOG_ERR( 'Exception[%s]'% e )
			isFail = True

		xbmc.executebuiltin( 'Dialog.Close(busydialog)' )

		if isFail :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), lblLine )
			dialog.doModal( )

		return isFail


