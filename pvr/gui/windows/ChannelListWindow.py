from pvr.gui.WindowImport import *

E_CHANNEL_LIST_BASE_ID					=  WinMgr.WIN_ID_CHANNEL_LIST_WINDOW * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 

#xml control id
E_CONTROL_ID_LABEL_CHANNEL_PATH			= E_CHANNEL_LIST_BASE_ID + 21
E_CONTROL_ID_LABEL_CHANNEL_SORT			= E_CHANNEL_LIST_BASE_ID + 22
E_CONTROL_ID_SCROLLBAR_CHANNEL			= E_CHANNEL_LIST_BASE_ID + 61
E_CONTROL_ID_SCROLLBAR_SUBMENU			= E_CHANNEL_LIST_BASE_ID + 203
E_CONTROL_ID_GROUP_MAINMENU 			= E_CHANNEL_LIST_BASE_ID + 100
E_CONTROL_ID_BUTTON_MAINMENU 			= E_CHANNEL_LIST_BASE_ID + 101
E_CONTROL_ID_LIST_MAINMENU				= E_CHANNEL_LIST_BASE_ID + 102
E_CONTROL_ID_BUTTON_SORTING				= E_CHANNEL_LIST_BASE_ID + 103
E_CONTROL_ID_GROUP_SUBMENU				= E_CHANNEL_LIST_BASE_ID + 9001
E_CONTROL_ID_LIST_SUBMENU				= E_CHANNEL_LIST_BASE_ID + 112
E_CONTROL_ID_RADIOBUTTON_TV				= E_CHANNEL_LIST_BASE_ID + 113
E_CONTROL_ID_RADIOBUTTON_RADIO			= E_CHANNEL_LIST_BASE_ID + 114
E_CONTROL_ID_GROUP_CHANNEL_LIST			= E_CHANNEL_LIST_BASE_ID + 49
E_CONTROL_ID_LIST_CHANNEL_LIST			= E_CHANNEL_LIST_BASE_ID + 50
E_CONTROL_ID_LABEL_CHANNEL_NAME			= E_CHANNEL_LIST_BASE_ID + 303
E_CONTROL_ID_LABEL_EPG_NAME				= E_CHANNEL_LIST_BASE_ID + 304
E_CONTROL_ID_LABEL_EPG_TIME				= E_CHANNEL_LIST_BASE_ID + 305
E_CONTROL_ID_PROGRESS_EPG				= E_CHANNEL_LIST_BASE_ID + 306
E_CONTROL_ID_LABEL_LONGITUDE_INFO		= E_CHANNEL_LIST_BASE_ID + 307
E_CONTROL_ID_LABEL_CAREER_INFO			= E_CHANNEL_LIST_BASE_ID + 308
E_CONTROL_ID_GROUP_LOCKED_INFO			= E_CHANNEL_LIST_BASE_ID + 309
E_CONTROL_ID_LABEL_SELECT_NUMBER		= E_CHANNEL_LIST_BASE_ID + 401
E_CONTROL_ID_GROUP_HELPBOX				= E_CHANNEL_LIST_BASE_ID + 600

FLAG_MASK_ADD    = 0x01
FLAG_MASK_NONE   = 0x00
FLAG_MODE_TV     = ElisEnum.E_SERVICE_TYPE_TV
FLAG_MODE_RADIO  = ElisEnum.E_SERVICE_TYPE_RADIO
FLAG_MODE_DATA   = ElisEnum.E_SERVICE_TYPE_DATA
FLAG_SLIDE_OPEN  = 0
FLAG_SLIDE_INIT  = 1
FLAG_OPT_LIST    = 0
FLAG_OPT_GROUP   = 1
FLAG_OPT_MOVE    = 2
FLAG_OPT_MOVE_OK = 3
FLAG_OPT_MOVE_UPDOWN = 4
FLAG_OPT_MOVE_EXIT = 5
FLAG_CLOCKMODE_ADMYHM   = 1
FLAG_CLOCKMODE_AHM      = 2
FLAG_CLOCKMODE_HMS      = 3
FLAG_CLOCKMODE_HHMM     = 4
FLAG_MODE_JUMP         = True

E_MODE_CHANNEL_LIST = 1

#slide index
E_SLIDE_ACTION_MAIN     = 0
E_SLIDE_ACTION_SUB      = 1
E_SLIDE_ACTION_SORT     = 99
E_SLIDE_MENU_ALLCHANNEL = 0
E_SLIDE_MENU_SATELLITE  = 1
E_SLIDE_MENU_FTACAS     = 2
E_SLIDE_MENU_FAVORITE   = 3
E_SLIDE_MENU_MODE       = 4

E_CONTROL_FOCUSED       = E_CHANNEL_LIST_BASE_ID + 9991
E_SLIDE_CLOSE           = E_CHANNEL_LIST_BASE_ID + 9999

E_CHANNEL_LIST_DEFAULT_FOCUS_ID			=  E_CONTROL_ID_GROUP_CHANNEL_LIST

class SlidePosition( object ) :
	def __init__( self ) :
		self.mMain = 0
		self.mSub = 0

	def debugList( self ) :
		retList = []
		retList.append( self.mMain )
		retList.append( self.mSub )
		return retList


class ChannelListWindow( BaseWindow ) :

	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )

		#submenu list
		self.mListAllChannel= []
		self.mListSatellite = []
		self.mListCasList   = []
		self.mListFavorite  = []
		self.mLoadMode = None
		self.mLoadSlidePos = SlidePosition( )
		self.mCurrentPosition = 0
		self.mLastChannel = None
		self.mListItems = None
		self.mPlayProgressThread = None
		self.mEnableProgressThread = False

		self.mEventId = 0
		self.mLocalTime = 0
		self.mAsyncTuneTimer = None

		self.mAgeLimit = 0
		self.mViewMode = WinMgr.WIN_ID_CHANNEL_LIST_WINDOW


	def onInit(self):
		LOG_TRACE( 'Enter' )
		self.setFocusId( E_CHANNEL_LIST_DEFAULT_FOCUS_ID )

		self.SetSingleWindowPosition( E_CHANNEL_LIST_BASE_ID )

		self.SetActivate( True )
		self.SetFrontdisplayMessage( 'Channel List' )
		
		self.mWinId = xbmcgui.getCurrentWindowId( )
		LOG_TRACE( 'winID[%d]'% self.mWinId)

		#starttime = time.time( )
		#print '==================== TEST TIME[ONINIT] START[%s]'% starttime

		#path
		self.mCtrlLabelChannelPath       = self.getControl( E_CONTROL_ID_LABEL_CHANNEL_PATH )
		self.mCtrlLabelChannelSort       = self.getControl( E_CONTROL_ID_LABEL_CHANNEL_SORT )

		#main menu
		self.mCtrlListMainmenu           = self.getControl( E_CONTROL_ID_LIST_MAINMENU )
		self.mCtrlButtonSorting          = self.getControl( E_CONTROL_ID_BUTTON_SORTING )

		#sub menu list
		self.mCtrlListSubmenu            = self.getControl( E_CONTROL_ID_LIST_SUBMENU )

		#sub menu btn
		self.mCtrlRadioButtonTV          = self.getControl( E_CONTROL_ID_RADIOBUTTON_TV )
		self.mCtrlRadioButtonRadio       = self.getControl( E_CONTROL_ID_RADIOBUTTON_RADIO )

		#info
		self.mCtrlLabelChannelName       = self.getControl( E_CONTROL_ID_LABEL_CHANNEL_NAME )
		self.mCtrlLabelEPGName           = self.getControl( E_CONTROL_ID_LABEL_EPG_NAME )
		self.mCtrlLabelEPGTime           = self.getControl( E_CONTROL_ID_LABEL_EPG_TIME )
		self.mCtrlProgress               = self.getControl( E_CONTROL_ID_PROGRESS_EPG )
		self.mCtrlLabelLongitudeInfo     = self.getControl( E_CONTROL_ID_LABEL_LONGITUDE_INFO )
		self.mCtrlLabelCareerInfo        = self.getControl( E_CONTROL_ID_LABEL_CAREER_INFO )
		self.mCtrlLabelLockedInfo        = self.getControl( E_CONTROL_ID_GROUP_LOCKED_INFO )
		self.mCtrlLabelSelectItem        = self.getControl( E_CONTROL_ID_LABEL_SELECT_NUMBER )
		#self.mCtrlGroupHelpBox           = self.getControl( E_CONTROL_ID_GROUP_HELPBOX )
		#self.mCtrlLabelMiniTitle         = self.getControl( E_SETTING_MINI_TITLE )

		#ch list
		self.mCtrlGroupCHList            = self.getControl( E_CONTROL_ID_GROUP_CHANNEL_LIST )
		self.mCtrlListCHList             = self.getControl( E_CONTROL_ID_LIST_CHANNEL_LIST )

		self.mCtrlListCHList.reset( )

		self.mIsTune = False
		self.mIsMark = True
		self.mNeedSlidePosUpdate = True
		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		self.mUserSlidePos = SlidePosition( )
		self.mLastSlidePos = SlidePosition( )
		self.mPrevSlidePos = SlidePosition( )
		self.mZappingName = ''
		self.mChannelList = []
		self.mChannelListHash = {}
		self.mRecCount = 0
		self.mRecordInfo1 = None
		self.mRecordInfo2 = None
		self.mNavEpg = None
		self.mNavChannel = None
		self.mCurrentChannel = None
		self.mFlag_EditChanged = False
		self.mFlag_ModeChanged = False
		self.mFlag_DeleteAll = False
		self.mRefreshCurrentChannel = False

		#edit mode
		self.mIsSave = FLAG_MASK_NONE
		self.mMarkList = []
		self.mFavoriteGroupList = []
		self.mMoveFlag = False
		self.mMoveItem = []
		self.mItemCount = 0
		self.mIsPVR = False

		self.mEventBus.Register( self )
		self.SetPipScreen( )
		self.LoadNoSignalState( )

		self.mItemHeight = int( self.getProperty( 'ItemHeight' ) )
		self.mAgeLimit = self.mDataCache.GetPropertyAge( )

		if self.mDataCache.GetChannelReloadStatus( ) :
			self.mListItems = None
			self.mDataCache.LoadZappingList( )

		#self.mDataCache.SetChannelReloadStatus( False )

		#initialize get cache
		zappingmode = None
		zappingmode = self.mDataCache.Zappingmode_GetCurrent( )
		if zappingmode :
			if zappingmode.mSortingMode == ElisEnum.E_SORT_BY_DEFAULT :
				zappingmode.mSortingMode = ElisEnum.E_SORT_BY_NUMBER
			self.mLoadMode = deepcopy( zappingmode )
		else :
			self.mLoadMode = deepcopy( ElisIZappingMode( ) )

		self.mUserMode  = deepcopy( self.mLoadMode )
		self.mLastMode  = deepcopy( self.mLoadMode )
		self.mPrevMode  = deepcopy( self.mLoadMode )
		

		#initialize get channel list
		self.InitSlideMenuHeader( )
		self.Initialize( )

		#run thread
		self.mEnableProgressThread = True
		self.mPlayProgressThread = self.EPGProgressThread( )

		self.mAsyncTuneTimer = None
		#endtime = time.time( )
		#print '==================== TEST TIME[ONINIT] END[%s] loading[%s]'% (endtime, endtime-starttime )



	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 :
			self.TuneByNumber( int( actionId ) - Action.REMOTE_0 )

		elif actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :
			rKey = actionId - ( Action.ACTION_JUMP_SMS2 - 2 )
			self.TuneByNumber( rKey )

		elif actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			#LOG_TRACE( 'goto previous menu' )
			if self.mMoveFlag :
				self.SetMoveMode( FLAG_OPT_MOVE_OK, actionId )
			else :
				self.GoToPreviousWindow( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			self.GetFocusId( )
			#LOG_TRACE( 'item select, action ID[%s]'% actionId )
			if self.mFocusId == E_CONTROL_ID_LIST_MAINMENU :
				position = self.mCtrlListMainmenu.getSelectedPosition( )
				if position == E_SLIDE_MENU_ALLCHANNEL :
					self.SubMenuAction( E_SLIDE_ACTION_SUB )
					self.UpdateControlGUI( E_SLIDE_CLOSE )

				else :
					self.SubMenuAction( E_SLIDE_ACTION_MAIN, position )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_LIST_MAINMENU :
				position = self.mCtrlListMainmenu.getSelectedPosition( )
				if position == E_SLIDE_MENU_ALLCHANNEL :
					self.UpdateControlGUI( E_SLIDE_CLOSE )

			elif self.mFocusId == E_CONTROL_ID_BUTTON_MAINMENU :
				self.UpdateControlGUI( E_CONTROL_FOCUSED, E_CONTROL_ID_LIST_MAINMENU )
				self.SetSlideMenuHeader( FLAG_SLIDE_OPEN )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.GetFocusId( )
			LOG_TRACE('--------------focus[%s]'% self.mFocusId )
			if self.mFocusId == E_CONTROL_ID_LIST_CHANNEL_LIST or self.mFocusId == 49 :
				self.SetSlideMenuHeader( FLAG_SLIDE_OPEN )

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN or \
			 actionId == Action.ACTION_PAGE_UP or actionId == Action.ACTION_PAGE_DOWN :
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_LIST_CHANNEL_LIST or self.mFocusId == E_CONTROL_ID_SCROLLBAR_CHANNEL :
				if self.mMoveFlag :
					self.SetMoveMode( FLAG_OPT_MOVE_UPDOWN, actionId )
					return
				else :
					self.RestartAsyncEPG( )

			elif self.mFocusId == E_CONTROL_ID_LIST_MAINMENU :
				position = self.mCtrlListMainmenu.getSelectedPosition( )
				self.SubMenuAction( E_SLIDE_ACTION_MAIN, position )

			elif self.mFocusId == E_CONTROL_ID_BUTTON_MAINMENU :
				self.setFocusId( E_CONTROL_ID_BUTTON_SORTING )


		elif actionId == Action.ACTION_CONTEXT_MENU :
			self.ShowContextMenu( )


		elif actionId == Action.ACTION_STOP :
			if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :

				status = self.mDataCache.Player_GetStatus( )
				if status.mMode :
					ret = self.mDataCache.Player_Stop( )

					iChannel = self.mDataCache.Channel_GetCurrent( )
					LOG_TRACE( '-------------------iChannel[%s]'% iChannel )
					if iChannel :
						self.mNavChannel = iChannel
						self.mCurrentChannel = iChannel.mNumber

					self.mIsTune == True
					self.UpdateChannelAndEPG( )
				else :
					self.ShowRecordingStopDialog( )

		elif actionId == Action.ACTION_MBOX_ARCHIVE :
			if HasAvailableRecordingHDD( ) == False :
				return
				
			if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
				self.GoToPreviousWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW )

		elif actionId == Action.ACTION_SHOW_INFO :
			if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
				if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
					msg = MR_LANG( 'Try again after stopping all your recordings first' )
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Attention' ), msg )
					dialog.doModal( )
				else :
					self.GoToPreviousWindow( WinMgr.WIN_ID_EPG_WINDOW )

		elif actionId == Action.ACTION_MBOX_RECORD :
			if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
				if self.mChannelList or len( self.mChannelList ) > 0 :
					self.ShowRecordingStartDialog( )

		elif actionId == Action.ACTION_MBOX_TVRADIO :
			if self.mUserMode.mServiceType == FLAG_MODE_TV :
				self.DoModeChange( FLAG_MODE_RADIO )
			else :
				self.DoModeChange( FLAG_MODE_TV )



	def onClick(self, aControlId):
		LOG_TRACE( 'onclick focusID[%d]'% aControlId )
		if self.IsActivate( ) == False  :
			return

		if aControlId == E_CONTROL_ID_LIST_CHANNEL_LIST :
			if self.mViewMode == WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW :
				try:
					if self.mMoveFlag :
						self.SetMoveMode( FLAG_OPT_MOVE_OK )
						return

					#Mark mode
					if self.mIsMark == True :
						if self.mChannelList :
							idx = self.mCtrlListCHList.getSelectedPosition( )
							self.SetMark( idx )

							self.UpdateControlGUI( E_CONTROL_FOCUSED, E_CONTROL_ID_GROUP_CHANNEL_LIST )
							self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, idx+1, E_TAG_SET_SELECT_POSITION )
							self.UpdateControlGUI( E_CONTROL_ID_LABEL_SELECT_NUMBER, str( '%s'% (idx+1) ) )

				except Exception, e:
					LOG_TRACE( 'Error except[%s]'% e )

			else :
				if self.mChannelList :
					self.TuneChannel( )


		elif aControlId == E_CONTROL_ID_BUTTON_SORTING :
			self.SubMenuAction( E_SLIDE_ACTION_SUB, E_SLIDE_ACTION_SORT, True )


		elif aControlId == E_CONTROL_ID_BUTTON_MAINMENU or aControlId == E_CONTROL_ID_LIST_MAINMENU :
			#slide main view
			LOG_TRACE('-----------hidden button[%s]'% aControlId )
			pass

		elif aControlId == E_CONTROL_ID_LIST_MAINMENU :
			position = self.mCtrlListMainmenu.getSelectedPosition( )
			LOG_TRACE('-----------------main idx[%s]'% position )
			if position == E_SLIDE_MENU_ALLCHANNEL :
				LOG_TRACE('-----------------click AllChannel' )
				#list action
				self.SubMenuAction( E_SLIDE_ACTION_SUB )
				self.UpdateControlGUI( E_SLIDE_CLOSE )

		elif aControlId == E_CONTROL_ID_LIST_SUBMENU :
			#list action
			self.SubMenuAction( E_SLIDE_ACTION_SUB )
			self.UpdateControlGUI( E_SLIDE_CLOSE )

		elif aControlId == E_CONTROL_ID_RADIOBUTTON_TV :
			self.DoModeChange( FLAG_MODE_TV )

		elif aControlId == E_CONTROL_ID_RADIOBUTTON_RADIO :
			self.DoModeChange( FLAG_MODE_RADIO )


	def onFocus(self, controlId):
		#LOG_TRACE( 'control %d' % controlId )
		if self.IsActivate( ) == False  :
			return


	def LoadChannelListHash( self ) :
		self.mChannelListHash = {}
		if self.mChannelList and len( self.mChannelList ) > 0 :
			for i in range( len( self.mChannelList ) ) :
				chNumber = self.mChannelList[i].mNumber
				self.mChannelListHash[chNumber] = self.mChannelList[i]

		LOG_TRACE( '-------------------hash len[%s]'% len(self.mChannelListHash) )


	def Initialize( self ):
		self.LoadRecordingInfo( )

		#already cache load
		self.mChannelList = self.mDataCache.Channel_GetList( )
		self.LoadChannelListHash( )
		label = ''
		try :
			#first get is used cache, reason by fast load
			iChannel = self.mDataCache.Channel_GetCurrent( )

			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_LIVE :	#show pip
				self.setProperty( 'PvrPlay', 'False' )
			else :
				self.setProperty( 'PvrPlay', 'True' )

			if status.mMode == ElisEnum.E_MODE_TIMESHIFT :
				if iChannel :
					self.mNavChannel = iChannel
					self.mCurrentChannel = iChannel.mNumber
					label = 'TIMESHIFT - P%04d.%s' %(iChannel.mNumber, iChannel.mName )

			elif status.mMode == ElisEnum.E_MODE_PVR :
				playingRecord = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW ).GetPlayingRecord( )
				if playingRecord and playingRecord.mError == 0 :
					self.mIsPVR = True
					label = 'PVR - P%04d.%s' %( playingRecord.mChannelNo, playingRecord.mRecordName )

			else :
				#Live
				if iChannel :
					self.mNavChannel = iChannel
					self.mCurrentChannel = iChannel.mNumber

					label = '%s - %s'% ( EnumToString( 'type', iChannel.mServiceType ).upper(), iChannel.mName )

			self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, label )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		#clear label
		self.ResetLabel( )
		self.UpdateChannelList( )

		#initialize get epg event
		#self.Epgevent_GetCurrent( )
		try :
			iEPG = None
			#iEPG = self.mDataCache.Epgevent_GetPresent( )
			iEPG = self.mDataCache.GetEpgeventCurrent( )
			if iEPG and iEPG.mError == 0:
				self.mNavEpg = iEPG
				self.mDataCache.Frontdisplay_SetIcon( ElisEnum.E_ICON_HD, iEPG.mHasHDVideo )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		self.UpdateChannelAndEPG( )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, label )


	def DoDeleteAll( self ) :
		ret = E_DIALOG_STATE_NO

		#ask save question
		head = MR_LANG( 'Delete all channels' )
		line1 = MR_LANG( 'Are you sure you want to remove\nall your TV and radio channels?' )
		if self.mUserMode.mMode == ElisEnum.E_MODE_FAVORITE :
			line1 = MR_LANG( 'Are you sure you want to remove\nall channels from this favorite group?' )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( head, line1 )
		dialog.doModal( )

		ret = dialog.IsOK( )

		#answer is yes
		if ret == E_DIALOG_STATE_YES :
			if self.mUserMode.mMode == ElisEnum.E_MODE_FAVORITE :
				self.LoadFavoriteGroupList( )
				favName = self.mFavoriteGroupList[self.mUserSlidePos.mSub]
				LOG_TRACE( '------------------favName[%s]'% favName )
				if favName :
					iChannelList = self.mDataCache.Channel_GetListByFavorite( self.mUserMode.mServiceType, self.mUserMode.mMode, self.mUserMode.mSortingMode, favName )
					if iChannelList and len( iChannelList ) > 0 :
						numList = []
						for iChannel in iChannelList :
							chNum = ElisEInteger( )
							chNum.mParam = iChannel.mNumber
							numList.append( chNum )
						self.mDataCache.Channel_Backup( )
						self.mIsSave = FLAG_MASK_ADD
						self.mDataCache.Favoritegroup_RemoveChannelByNumber( favName, self.mUserMode.mServiceType, numList )

			else :
				isBackup = self.mDataCache.Channel_Backup( )
				isDelete = self.mDataCache.Channel_DeleteAll( )
				if isDelete :
					self.mFlag_DeleteAll = True

		return ret


	def DoModeChange( self, aType = FLAG_MODE_TV ) :
		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW :
			LOG_TRACE( 'Editing now...' )
			return

		if self.mUserMode.mServiceType != aType and self.mDataCache.Channel_GetCount( aType ) > 0 :
			tmpUserMode = deepcopy( self.mUserMode )
			self.mUserMode = deepcopy( self.mLastMode )
			tmpUserSlidePos = deepcopy( self.mUserSlidePos )
			self.mUserSlidePos = deepcopy( self.mLastSlidePos )

			self.mFlag_EditChanged = True
			self.mFlag_ModeChanged = True
			self.mUserMode.mServiceType = aType
			aMode = self.mUserMode.mMode
			aSort = self.mUserMode.mSortingMode
			if self.mUserMode.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO and aSort == ElisEnum.E_SORT_BY_HD :
				self.mUserMode.mSortingMode = ElisEnum.E_SORT_BY_NUMBER

			self.ResetLabel( )
			self.mCtrlListCHList.reset( )
			self.InitSlideMenuHeader( FLAG_SLIDE_OPEN )
			self.RefreshSlideMenu( self.mUserSlidePos.mMain, self.mUserSlidePos.mSub, True )
			#self.UpdateChannelList( )

			self.mFlag_EditChanged = False
			self.mLastMode = deepcopy( tmpUserMode )
			self.mLastSlidePos = deepcopy( tmpUserSlidePos )

			self.SetRadioScreen( aType )
			propertyName = 'Last TV Number'
			if aType == ElisEnum.E_SERVICE_TYPE_RADIO :
				propertyName = 'Last Radio Number'

			lastChannelNumber = ElisPropertyInt( propertyName, self.mCommander ).GetProp( )
			self.TuneChannel( lastChannelNumber )

			#initialize get epg event
			self.mFlag_ModeChanged = False

		else :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No channels available for the selected mode' ) )
			dialog.doModal( )


		if self.mUserMode.mServiceType == FLAG_MODE_TV :
			self.UpdateControlGUI( E_CONTROL_ID_RADIOBUTTON_TV,   True, E_TAG_SELECT )
			self.UpdateControlGUI( E_CONTROL_ID_RADIOBUTTON_RADIO,False, E_TAG_SELECT )
		else :
			self.UpdateControlGUI( E_CONTROL_ID_RADIOBUTTON_TV,   False, E_TAG_SELECT )
			self.UpdateControlGUI( E_CONTROL_ID_RADIOBUTTON_RADIO,True, E_TAG_SELECT )

		self.UpdateControlGUI( E_SLIDE_CLOSE )


	def GoToEditWindow( self ) :
		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			self.mViewMode = WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW

			try :
				#self.mEventBus.Deregister( self )
				self.mDataCache.SetChangeDBTableChannel( E_TABLE_ALLCHANNEL )

				self.mDataCache.SetSkipChannelView( True )

				self.mPrevMode = deepcopy( self.mUserMode )
				self.mPrevSlidePos = deepcopy( self.mUserSlidePos )
				"""
				# default mode AllChannel : enter EditMode
				self.mUserMode.mMode = ElisEnum.E_MODE_ALL
				self.mUserMode.mSortingMode = ElisEnum.E_SORT_BY_NUMBER
				self.mUserSlidePos.mMain = E_SLIDE_MENU_ALLCHANNEL
				self.mUserSlidePos.mSub  = 0
				"""

				self.UpdateControlListSelectItem( self.mCtrlListMainmenu, self.mUserSlidePos.mMain )
				self.UpdateControlListSelectItem( self.mCtrlListSubmenu, self.mUserSlidePos.mSub )
				#LOG_TRACE( 'IN: slide[%s,%s]--get[%s, %s]--------1'% (self.mUserSlidePos.mMain, self.mUserSlidePos.mSub, self.mCtrlListMainmenu.getSelectedPosition( ), self.mCtrlListSubmenu.getSelectedPosition( ) ) )

				self.mListItems = None
				self.mCtrlListCHList.reset( )
				self.InitSlideMenuHeader( FLAG_SLIDE_OPEN )
				self.SubMenuAction( E_SLIDE_ACTION_SUB, 0, True )
				self.UpdateControlGUI( E_SLIDE_CLOSE )

				#clear label
				self.ResetLabel( )
				self.UpdateChannelAndEPG( )

				ret = self.mDataCache.Channel_Backup( )
				#LOG_TRACE( 'channelBackup[%s]'% ret )


			except Exception, e :
				LOG_TRACE( 'Error except[%s]'% e )

		else :
			self.GoToPreviousWindow( )


	def GoToPreviousWindow( self, aGoToWindow = None ) :
		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			ret = False
			ret = self.SaveSlideMenuHeader( )
			if ret != E_DIALOG_STATE_CANCEL :
				if self.mFlag_DeleteAll and ret == E_DIALOG_STATE_YES :
					if not self.mDataCache.Get_Player_AVBlank( ) :
						self.mDataCache.Player_AVBlank( True )
					#self.mDataCache.SetLockedState( ElisEnum.E_CC_FAILED_NO_SIGNAL )

				self.Close( )

				if aGoToWindow :
					WinMgr.GetInstance( ).ShowWindow( aGoToWindow, WinMgr.WIN_ID_NULLWINDOW )
				else :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW, WinMgr.WIN_ID_NULLWINDOW )

			LOG_TRACE( 'go out window' )

		else :
			if self.mMarkList :
				LOG_TRACE( '-------marklist[%s]'% self.mMarkList )
				self.ClearMark( )
				self.mMarkList = []

			else :
				ret = False
				ret = self.SaveEditList( )
				if ret != E_DIALOG_STATE_CANCEL :
					self.mViewMode = WinMgr.WIN_ID_CHANNEL_LIST_WINDOW
					self.mFlag_EditChanged = False
					self.mMoveFlag = False
					#self.mEventBus.Register( self )
					getTable = E_TABLE_ALLCHANNEL
					if self.mRecCount > 0 :
						getTable = E_TABLE_ZAPPING
					self.mDataCache.SetChangeDBTableChannel( getTable )

					#LOG_TRACE( 'slidePos: user[%s,%s] prev[%s,%s]'% (self.mUserSlidePos.mMain, self.mUserSlidePos.mSub, self.mPrevSlidePos.mMain, self.mPrevSlidePos.mSub ) )
					#LOG_TRACE( 'mode: user[%s,%s] prev[%s,%s]'% (self.mUserMode.mServiceType, self.mUserMode.mSortingMode, self.mPrevMode.mServiceType, self.mPrevMode.mSortingMode ) )
					self.mDataCache.SetSkipChannelView( False )
					self.mUserMode = deepcopy( self.mPrevMode )
					self.mUserSlidePos = deepcopy( self.mPrevSlidePos )
					self.SubMenuAction( E_SLIDE_ACTION_MAIN, self.mUserSlidePos.mMain )

					self.UpdateControlListSelectItem( self.mCtrlListMainmenu, self.mUserSlidePos.mMain )
					self.UpdateControlListSelectItem( self.mCtrlListSubmenu, self.mUserSlidePos.mSub )
					#LOG_TRACE( 'OUT: slide[%s,%s]--get[%s, %s]--------1'% (self.mUserSlidePos.mMain, self.mUserSlidePos.mSub, self.mCtrlListMainmenu.getSelectedPosition( ), self.mCtrlListSubmenu.getSelectedPosition( ) ) )

					self.mListItems = None
					self.mCtrlListCHList.reset( )
					self.InitSlideMenuHeader( FLAG_SLIDE_OPEN )
					self.SubMenuAction( E_SLIDE_ACTION_SUB, 0, True )
					self.UpdateControlGUI( E_SLIDE_CLOSE )

					#initialize get epg event
					self.mIsTune = False
					self.Epgevent_GetCurrent( )

					#clear label
					self.ResetLabel( )
					self.UpdateChannelAndEPG( )


	def onEvent(self, aEvent):
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			#LOG_TRACE( 'Receive Event[%s]'% aEvent.getName( ) )

			if aEvent.getName( ) == ElisEventCurrentEITReceived.getName( ) :
				if self.mNavChannel == None:
					#LOG_TRACE('--epg not------ch none')
					return -1

				if self.mNavChannel.mSid != aEvent.mSid or self.mNavChannel.mTsid != aEvent.mTsid or self.mNavChannel.mOnid != aEvent.mOnid :
					#LOG_TRACE('--epg not------eventid no match')
					return -1

				if aEvent.mEventId != self.mEventId :
					if self.mIsTune == True :
						iEPG = None
						#sid  = self.mNavChannel.mSid
						#tsid = self.mNavChannel.mTsid
						#onid = self.mNavChannel.mOnid
						#iEPG = self.mDataCache.Epgevent_GetPresent( )
						iEPG = self.mDataCache.GetEpgeventCurrent( )
						
						if iEPG == None or iEPG.mError != 0 :
							return -1

						self.mEventId = aEvent.mEventId

						if not self.mNavEpg or \
						   iEPG.mEventId != self.mNavEpg.mEventId or \
						   iEPG.mSid != self.mNavEpg.mSid or \
						   iEPG.mTsid != self.mNavEpg.mTsid or \
						   iEPG.mOnid != self.mNavEpg.mOnid :

							#LOG_TRACE( 'epg DIFFER' )
							self.mNavEpg = iEPG
							self.mDataCache.Frontdisplay_SetIcon( ElisEnum.E_ICON_HD, iEPG.mHasHDVideo )

							#update label
							self.ResetLabel( )
							self.UpdateChannelAndEPG( )

			elif aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or \
				 aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :

				oldRecInfo1 = deepcopy( self.mRecordInfo1 )
				oldRecInfo2 = deepcopy( self.mRecordInfo2 )
				self.LoadRecordingInfo( )
				if self.mViewMode == WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW and self.mChannelList and len( self.mChannelList ) > 0 :
					self.UpdateRecordInfo( oldRecInfo1, oldRecInfo2 )

				else :
					self.ReloadChannelList( )
					self.mFlag_EditChanged = False
					self.mMoveFlag = False

			elif aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
				if aEvent.mType == ElisEnum.E_EOF_END :
					#LOG_TRACE( 'EventRecv EOF_STOP' )
					xbmc.executebuiltin( 'xbmc.Action(stop)' )

			elif aEvent.getName( ) == ElisEventChannelChangedByRecord.getName( ) :
				self.UpdateChannelList( )

		else:
			LOG_TRACE( 'channellist winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId( ) ) )


	def TuneChannel( self, aJumpNumber = None ) :
		#Turn in
		self.mIsTune = True

		if aJumpNumber:

			iChannel = self.mChannelListHash.get( int(aJumpNumber), None ) 
			if iChannel == None :
				return
			#LOG_TRACE( 'JumpChannel: num[%s] Name[%s] type[%s] aNum[%s]'% (iChannel.mNumber, iChannel.mName, iChannel.mServiceType, aJumpNumber) )

			#detected to jump focus
			chindex = 0
			isFind = False
			for ch in self.mChannelList :
				if ch.mNumber == aJumpNumber :
					self.mNavChannel = ch
					isFind = True
					self.ResetLabel( )
					self.UpdateChannelAndEPG( )
					break
				else :
					chindex += 1

			if isFind == False :
				chindex = 0
				iChannel = self.mChannelList[0]

			self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, chindex, E_TAG_SET_SELECT_POSITION )

		else:
			if self.mChannelList == None:
				label = MR_LANG( 'No Channel' )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, label )
				return 

			idx = self.mCtrlListCHList.getSelectedPosition( )
			iChannel = self.mChannelList[idx]

		"""
		if self.mFlag_ModeChanged :
			isBlank = False
			if iChannel.mServiceType == FLAG_MODE_RADIO :
				isBlank = True
			else :
				isBlank = False
			self.mDataCache.Player_VideoBlank( isBlank )
		"""

		if self.mIsPVR :
			self.mIsPVR = False
			self.mDataCache.Player_Stop( )

		ret = self.mDataCache.Channel_SetCurrent( iChannel.mNumber, iChannel.mServiceType, self.mChannelListHash )
		if ret :
			oldChannel = self.mDataCache.Channel_GetOldChannel( )
			#LOG_TRACE( 'oldch: num[%s] type[%s] name[%s] re[%s]'% ( oldChannel.mNumber, oldChannel.mServiceType, oldChannel.mName, self.mRefreshCurrentChannel ) )
			if oldChannel and not self.mRefreshCurrentChannel and \
			   oldChannel.mName == iChannel.mName and \
			   oldChannel.mNumber == iChannel.mNumber and \
			   oldChannel.mServiceType == iChannel.mServiceType :
				ret = False
				ret = self.SaveSlideMenuHeader( )
				if ret != E_DIALOG_STATE_CANCEL :
					self.Close( )
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE, WinMgr.WIN_ID_NULLWINDOW )				
					return

				LOG_TRACE( 'No exit by pressing the cancel button' )

		#refresh info
		if iChannel :
			self.mNavChannel = iChannel
			self.mCurrentChannel = iChannel.mNumber
			self.mCurrentPosition = self.mCtrlListCHList.getSelectedPosition( )
			pos = self.mCurrentPosition + 1
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_SELECT_NUMBER, str( '%s'% pos ) )
			LOG_TRACE( 'chinfo: num[%s] type[%s] name[%s] pos[%s]'% (iChannel.mNumber, iChannel.mServiceType, iChannel.mName, pos) )

			self.ResetLabel( )
			self.UpdateChannelAndEPG( )


	def RefreshSlideMenu( self, aMainIndex = E_SLIDE_MENU_ALLCHANNEL, aSubIndex = 0, aForce = None ) :
		self.UpdateControlListSelectItem( self.mCtrlListMainmenu, aMainIndex )
		self.UpdateControlListSelectItem( self.mCtrlListSubmenu, aSubIndex )
		self.SubMenuAction( E_SLIDE_ACTION_MAIN, aMainIndex )
		self.SubMenuAction( E_SLIDE_ACTION_SUB, 0, aForce )


	def SubMenuAction( self, aAction = E_SLIDE_ACTION_MAIN, aMenuIndex = 0, aForce = None ) :
		#if self.mFlag_DeleteAll :
		#	return

		retPass = False

		if aAction == E_SLIDE_ACTION_MAIN:
			testlistItems = []

			if aMenuIndex == E_SLIDE_MENU_ALLCHANNEL :
				testlistItems.append( xbmcgui.ListItem( '' ) )

			elif aMenuIndex == E_SLIDE_MENU_SATELLITE :
				if self.mListSatellite :
					for itemClass in self.mListSatellite:
						ret = GetSelectedLongitudeString( itemClass.mLongitude, itemClass.mName )
						testlistItems.append( xbmcgui.ListItem( ret ) )
				else :
					testlistItems.append( xbmcgui.ListItem( MR_LANG( 'None' ) ) )

			elif aMenuIndex == E_SLIDE_MENU_FTACAS :
				if self.mListCasList :
					for itemClass in self.mListCasList:
						ret = '%s(%s)'% ( itemClass.mName, itemClass.mChannelCount )
						testlistItems.append( xbmcgui.ListItem( ret ) )
				else :
					testlistItems.append( xbmcgui.ListItem( MR_LANG( 'None' ) ) )

			elif aMenuIndex == E_SLIDE_MENU_FAVORITE :
				if self.mListFavorite :
					for itemClass in self.mListFavorite :
						testlistItems.append( xbmcgui.ListItem( itemClass.mGroupName ) )
				else :
					testlistItems.append( xbmcgui.ListItem( MR_LANG( 'None' ) ) )

			if testlistItems != [] :
				#submenu update
				self.mCtrlListSubmenu.reset( )
				self.mCtrlListSubmenu.addItems( testlistItems )

				if aMenuIndex == self.mUserSlidePos.mMain :
					self.mCtrlListSubmenu.selectItem( self.mUserSlidePos.mSub )


		elif aAction == E_SLIDE_ACTION_SUB :
			idxMain = self.mCtrlListMainmenu.getSelectedPosition( )
			idxSub  = self.mCtrlListSubmenu.getSelectedPosition( )
			zappingName = ''
			if aForce == None and self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
				if self.mUserSlidePos.mMain == idxMain and \
				   self.mUserSlidePos.mSub == idxSub :
					LOG_TRACE( 'already selected!!!' )
					return

			if aMenuIndex == E_SLIDE_ACTION_SORT :
				nextSort = ElisEnum.E_SORT_BY_NUMBER
				if self.mUserMode.mSortingMode == ElisEnum.E_SORT_BY_NUMBER :
					nextSort = ElisEnum.E_SORT_BY_ALPHABET
				elif self.mUserMode.mSortingMode == ElisEnum.E_SORT_BY_ALPHABET :
					nextSort = ElisEnum.E_SORT_BY_HD
					if self.mUserMode.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
						nextSort = ElisEnum.E_SORT_BY_NUMBER

				idxMain = self.mUserSlidePos.mMain
				idxSub  = self.mUserSlidePos.mSub

				lblSort = EnumToString( 'sort', nextSort )
				self.mUserMode.mSortingMode = nextSort
				#LOG_TRACE('----nextSort[%s] user: type[%s] mode[%s] sort[%s]'% (nextSort,self.mUserMode.mServiceType, self.mUserMode.mMode,self.mUserMode.mSortingMode) )

				label = '%s : %s'% ( MR_LANG( 'sort' ).upper(), lblSort.upper() )
				self.UpdateControlGUI( E_CONTROL_ID_BUTTON_SORTING, label )


			if idxMain == E_SLIDE_MENU_ALLCHANNEL :
				self.mUserMode.mMode = ElisEnum.E_MODE_ALL
				retPass = self.GetChannelList( self.mUserMode.mServiceType, self.mUserMode.mMode, self.mUserMode.mSortingMode, 0, 0, 0, '' )
				#LOG_TRACE('All Channel ret[%s] idx[%s,%s]'% ( retPass, idxMain, idxSub ) )

			elif idxMain == E_SLIDE_MENU_SATELLITE :
				if self.mListSatellite :
					item = self.mListSatellite[idxSub]
					zappingName = item.mName
					self.mUserMode.mMode = ElisEnum.E_MODE_SATELLITE
					retPass = self.GetChannelList( self.mUserMode.mServiceType, self.mUserMode.mMode, self.mUserMode.mSortingMode, item.mLongitude, item.mBand, 0, '' )
					#LOG_TRACE( 'cmd[channel_GetListBySatellite] idx_Satellite[%s] mLongitude[%s] band[%s]'% ( idxSub, item.mLongitude, item.mBand ) )

			elif idxMain == E_SLIDE_MENU_FTACAS :
				if self.mListCasList :
					zappingName = self.mListCasList[idxSub].mName
					caid = self.mListCasList[idxSub].mCAId
					self.mUserMode.mMode = ElisEnum.E_MODE_CAS
					retPass = self.GetChannelList( self.mUserMode.mServiceType, self.mUserMode.mMode, self.mUserMode.mSortingMode, 0, 0, caid, '' )
					#LOG_TRACE( 'cmd[channel_GetListByFTACas] idxFtaCas[%s]'% idxSub )

			elif idxMain == E_SLIDE_MENU_FAVORITE :
				if self.mListFavorite : 
					item = self.mListFavorite[idxSub]
					zappingName = item.mGroupName
					self.mUserMode.mMode = ElisEnum.E_MODE_FAVORITE
					retPass = self.GetChannelList( self.mUserMode.mServiceType, self.mUserMode.mMode, self.mUserMode.mSortingMode, 0, 0, 0, item.mGroupName )
					#LOG_TRACE( 'cmd[channel_GetListByFavorite] idx_Favorite[%s] list_Favorite[%s]'% ( idxSub, item.mGroupName ) )


			if retPass == False :
				return

			if self.mMoveFlag :
				#do not refresh UI
				return

			#channel list update
			self.mMarkList = []
			self.mListItems = None
			self.mCtrlListCHList.reset( )
			self.UpdateChannelList( )

			#path tree, Mainmenu/Submanu
			self.mUserSlidePos.mMain = idxMain
			self.mUserSlidePos.mSub  = idxSub

			lblChannelPath = EnumToString( 'mode', self.mUserMode.mMode ).upper( )
			if zappingName :
				lblChannelPath = '%s > %s'% ( lblChannelPath, zappingName )

			lblChannelSort = MR_LANG( 'Sorted by %s' )% EnumToString( 'sort', self.mUserMode.mSortingMode )

			self.mCtrlLabelChannelPath.setLabel( lblChannelPath )
			self.mCtrlLabelChannelSort.setLabel( lblChannelSort )

			#current zapping backup
			#self.mDataCache.Channel_Backup( )


	def GetChannelList( self, aType, aMode, aSort, aLongitude, aBand, aCAid, aFavName ):
		try :
			if aMode == ElisEnum.E_MODE_ALL :
				self.mChannelList = self.mDataCache.Channel_GetList( FLAG_ZAPPING_CHANGE, aType, aMode, aSort )

			elif aMode == ElisEnum.E_MODE_SATELLITE :
				self.mChannelList = self.mDataCache.Channel_GetListBySatellite( aType, aMode, aSort, aLongitude, aBand )

			elif aMode == ElisEnum.E_MODE_CAS :
				self.mChannelList = self.mDataCache.Channel_GetListByFTACas( aType, aMode, aSort, aCAid )
				
			elif aMode == ElisEnum.E_MODE_FAVORITE :
				self.mChannelList = self.mDataCache.Channel_GetListByFavorite( aType, aMode, aSort, aFavName )

			elif aMode == ElisEnum.E_MODE_NETWORK :
				pass

			self.LoadChannelListHash( )


		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )
			return False

		return True


	def SetSlideMenuHeader( self, aMode ) :
		idx1 = 0
		idx2 = 0
		zInfo_name = ''

		if aMode == FLAG_SLIDE_INIT :

			#self.mUserMode.printdebug( )
			#LOG_TRACE( 'satellite[%s]'% ClassToList( 'convert', self.mListSatellite ) )
			#LOG_TRACE( 'ftacas[%s]'   % ClassToList( 'convert', self.mListCasList ) )
			#LOG_TRACE( 'favorite[%s]' % ClassToList( 'convert', self.mListFavorite ) )

			zInfo_mode = self.mUserMode.mMode
			zInfo_sort = self.mUserMode.mSortingMode
			zInfo_type = self.mUserMode.mServiceType

			if zInfo_mode == ElisEnum.E_MODE_ALL :
				idx1 = 0
				if zInfo_sort == ElisEnum.E_SORT_BY_NUMBER :
					idx2 = 0
				elif zInfo_sort == ElisEnum.E_SORT_BY_ALPHABET :
					idx2 = 1
				elif zInfo_sort == ElisEnum.E_SORT_BY_HD :
					idx2 = 2
				else :
					idx2 = 0

			elif zInfo_mode == ElisEnum.E_MODE_SATELLITE :
				idx1 = 1
				zInfo_name = self.mUserMode.mSatelliteInfo.mName

				for item in self.mListSatellite :
					if zInfo_name == item.mName :
						break
					idx2 += 1

			elif zInfo_mode == ElisEnum.E_MODE_CAS :
				idx1 = 2
				zInfo_name = self.mUserMode.mCasInfo.mName

				for item in self.mListCasList :
					if zInfo_name == item.mName :
						break
					idx2 += 1

			elif zInfo_mode == ElisEnum.E_MODE_FAVORITE :
				idx1 = 3
				zInfo_name = self.mUserMode.mFavoriteGroup.mGroupName
				if self.mListFavorite :
					for item in self.mListFavorite :
						if zInfo_name == item.mGroupName :
							break
						idx2 += 1

			self.mUserSlidePos.mMain = idx1
			self.mUserSlidePos.mSub  = idx2

			if self.mNeedSlidePosUpdate :
				self.mLoadSlidePos = deepcopy( self.mUserSlidePos )
				self.mNeedSlidePosUpdate = False

		elif aMode == FLAG_SLIDE_OPEN :
			idx1 = self.mUserSlidePos.mMain
			idx2 = self.mUserSlidePos.mSub

		self.UpdateControlListSelectItem( self.mCtrlListMainmenu, idx1 )
		self.UpdateControlListSelectItem( self.mCtrlListSubmenu, idx2 )
		self.SubMenuAction( E_SLIDE_ACTION_MAIN, idx1 )
		#self.UpdateControlGUI( E_CONTROL_FOCUSED, E_CONTROL_ID_LIST_SUBMENU )

		return zInfo_name


	def SaveSlideMenuHeader( self ) :
		"""
		LOG_TRACE( 'mode[%s] sort[%s] type[%s] mpos[%s] spos[%s]'% ( \
			self.mUserMode.mMode,                \
			self.mUserMode.mSortingMode,        \
			self.mUserMode.mServiceType,     \
			self.mUserSlidePos.mMain,    \
			self.mUserSlidePos.mSub      \
		)
		self.mListSatellite[self.mUserSlidePos.mSub].printdebug( )
		self.mListCasList[self.mUserSlidePos.mSub].printdebug( )
		self.mListFavorite[self.mUserSlidePos.mSub].printdebug( )
		"""

		#self.mLoadMode.printdebug()
		#LOG_TRACE('--------pos[%s] [%s]'% (self.mLoadSlidePos.debugList(), self.mUserSlidePos.debugList()) )
		#self.mUserMode.printdebug()
		
		changed = False
		saveNoAsk = False
		answer = E_DIALOG_STATE_NO

		if self.mLoadSlidePos.mMain != self.mUserSlidePos.mMain or \
		   self.mLoadSlidePos.mSub != self.mUserSlidePos.mSub :
			saveNoAsk = True
			changed = True

		if self.mLoadMode.mMode != self.mUserMode.mMode or \
		   self.mLoadMode.mSortingMode != self.mUserMode.mSortingMode or \
		   self.mLoadMode.mServiceType != self.mUserMode.mServiceType :
			saveNoAsk = True
			changed = True

		if self.mFlag_DeleteAll :
			changed = True

		if self.mIsSave :
			changed = True

		#is change?
		if changed :
			try :
				if saveNoAsk :
					answer = E_DIALOG_STATE_YES

				else :
					#ask save question
					#label1 = EnumToString( 'mode', self.mUserMode.mMode )
					#label2 = self.mCtrlListSubmenu.getSelectedItem( ).getLabel( )

					#head = 
					#line1 = MR_LANG( 'Do you want to save changes?' )
					#line2 = '- %s / %s'% ( label1.lower( ), label2.lower( ) )

					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
					dialog.SetDialogProperty( MR_LANG( 'Save Result' ), MR_LANG( 'Do you want to save changes before exit?' ) )
					dialog.doModal( )

					answer = dialog.IsOK( )

				#if answer is yes
				if answer == E_DIALOG_STATE_YES :
					#re-configuration class
					self.mLoadMode.reset( )
					self.mLoadMode.mMode = self.mUserMode.mMode
					self.mLoadMode.mSortingMode = self.mUserMode.mSortingMode
					self.mLoadMode.mServiceType = self.mUserMode.mServiceType

					if self.mUserSlidePos.mMain == 1 :
						groupInfo = self.mListSatellite[self.mUserSlidePos.mSub]
						self.mLoadMode.mSatelliteInfo = groupInfo
						
					elif self.mUserSlidePos.mMain == 2 :
						groupInfo = self.mListCasList[self.mUserSlidePos.mSub]
						self.mLoadMode.mCasInfo = groupInfo
					
					elif self.mUserSlidePos.mMain == 3 :
						groupInfo = self.mListFavorite[self.mUserSlidePos.mSub]
						self.mLoadMode.mFavoriteGroup = groupInfo

					"""
					LOG_TRACE( '1. zappingMode[%s] sortMode[%s] serviceType[%s]'%  \
						( EnumToString( 'mode', self.mUserMode.mMode),                 \
						  EnumToString( 'sort', self.mUserMode.mSortingMode),         \
						  EnumToString( 'type', self.mUserMode.mServiceType) ) )
					LOG_TRACE( '2. zappingMode[%s] sortMode[%s] serviceType[%s]'%          \
						( EnumToString( 'mode', self.mLoadMode.mMode),        \
						  EnumToString( 'sort', self.mLoadMode.mSortingMode), \
						  EnumToString( 'type', self.mLoadMode.mServiceType) ) )
					"""

					#save zapping mode
					self.mDataCache.Channel_Save( )
					self.mDataCache.Channel_GetAllChannels( self.mUserMode.mServiceType, False )

					if self.mChannelList == None or len( self.mChannelList ) < 1 :
						#### data cache re-load ####
						self.mDataCache.LoadZappingmode( )
						self.mDataCache.LoadZappingList( )
						self.mDataCache.LoadChannelList( )

					else :
						ret = self.mDataCache.Zappingmode_SetCurrent( self.mLoadMode )
						if ret :
							#### data cache re-load ####
							self.mDataCache.LoadZappingmode( )
							self.mDataCache.LoadZappingList( )
							self.mDataCache.LoadChannelList( )
							#LOG_TRACE ( '===================== save yes: cache re-load' )

							if self.mFlag_ModeChanged :
								isBlank = False
								lastServiceType = 'Last TV Number'
								if self.mUserMode.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
									isBlank = True
									lastServiceType = 'Last Radio Number'

								#self.mDataCache.Player_VideoBlank( isBlank )
								lastChannelNumber = ElisPropertyInt( lastServiceType, self.mCommander ).GetProp( )
								ret = self.mDataCache.Channel_SetCurrent( lastChannelNumber, self.mUserMode.mServiceType )

								LOG_TRACE( 'last Channel[%s]'% lastChannelNumber )
								if not ret :
									if self.mChannelList and len( self.mChannelList ) > 0 :
										self.mDataCache.Channel_SetCurrent( 1, self.mUserMode.mServiceType )


				elif answer == E_DIALOG_STATE_NO :
					#zapping changed then will re-paint list items for cache
					self.mListItems = None
					if self.mFlag_DeleteAll or self.mIsSave : 
						#restore backup zapping
						isRestore = self.mDataCache.Channel_Restore( True )
						self.mDataCache.Channel_Save( )
						LOG_TRACE( 'Restore[%s]'% isRestore )


					#self.mDataCache.Channel_SetCurrent( self.mCurrentChannel.mNumber, self.mCurrentChannel.mServiceType )
					#### data cache re-load ####
					self.mDataCache.LoadZappingmode( )
					self.mDataCache.LoadZappingList( )
					self.mDataCache.LoadChannelList( )
					#LOG_TRACE ( '===================== save no: cache re-load' )

					iChannel = self.mDataCache.Channel_GetCurrent( )
					if iChannel and iChannel.mError == 0 :
						if iChannel.mNumber != self.mCurrentChannel or iChannel.mServiceType != self.mUserMode.mServiceType :
							self.mDataCache.Channel_SetCurrent( iChannel.mNumber, iChannel.mServiceType )

						if iChannel.mServiceType == ElisEnum.E_SERVICE_TYPE_TV or self.mFlag_DeleteAll == True :
							if self.mDataCache.Get_Player_AVBlank( ) :
								self.mDataCache.Player_AVBlank( False )

						elif iChannel.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
							if not self.mDataCache.Get_Player_AVBlank( ) :
								self.mDataCache.Player_AVBlank( True )
						

			except Exception, e :
				LOG_TRACE( 'Error exception[%s]'% e )


		return answer


	def SaveEditList( self ) :
		answer = E_DIALOG_STATE_NO

		#is change?
		if self.mIsSave :
			#ask save question
			head = MR_LANG( 'Save Result' )
			line1 = MR_LANG( 'Do you want to save changes?' )

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( head, line1 )
			dialog.doModal( )

			answer = dialog.IsOK( )

			#answer is yes
			if answer == E_DIALOG_STATE_YES :
				self.mIsSave = FLAG_MASK_NONE
				self.mFlag_EditChanged = True
				isSave = self.mDataCache.Channel_Save( )
				self.mDataCache.Channel_GetAllChannels( self.mUserMode.mServiceType, False )

				#### data cache re-load ####
				self.mDataCache.SetSkipChannelView( False )
				self.mDataCache.LoadZappingmode( )
				self.mDataCache.LoadZappingList( )
				self.mDataCache.LoadChannelList( )
				LOG_TRACE ( 'save[%s] cache re-load'% isSave)

				if self.mRefreshCurrentChannel :
					self.TuneChannel( self.mRefreshCurrentChannel )
					self.mRefreshCurrentChannel = False

			elif answer == E_DIALOG_STATE_NO :
				self.mIsSave = FLAG_MASK_NONE
				isSave = self.mDataCache.Channel_Restore( True )
				self.mDataCache.Channel_Save( )
				LOG_TRACE( 'Restore[%s]'% isSave )

		return answer


	def InitSlideMenuHeader( self, aInitLoad = FLAG_SLIDE_INIT ) :
		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			#opt btn blind
			#self.UpdateControlGUI( E_SETTING_MINI_TITLE, MR_LANG( 'Channel List' ) )
			self.UpdateControlGUI( E_CONTROL_ID_RADIOBUTTON_TV, True, E_TAG_ENABLE )
			self.UpdateControlGUI( E_CONTROL_ID_RADIOBUTTON_RADIO, True, E_TAG_ENABLE )
			self.UpdatePropertyGUI( E_XML_PROPERTY_EDITINFO, E_TAG_FALSE )
			self.UpdatePropertyGUI( E_XML_PROPERTY_MOVE, E_TAG_FALSE )

		else :
			#opt btn visible
			#self.UpdateControlGUI( E_SETTING_MINI_TITLE, MR_LANG( 'Edit Channel List' ) )
			self.UpdateControlGUI( E_CONTROL_ID_RADIOBUTTON_TV, False, E_TAG_ENABLE )
			self.UpdateControlGUI( E_CONTROL_ID_RADIOBUTTON_RADIO, False, E_TAG_ENABLE )
			self.UpdatePropertyGUI( E_XML_PROPERTY_EDITINFO, E_TAG_TRUE )
	
		#main/sub menu init
		self.mCtrlListMainmenu.reset( )
		self.mCtrlListSubmenu.reset( )

		list_Mainmenu = []
		list_Mainmenu.append( MR_LANG( 'All CHANNELS' ) )
		list_Mainmenu.append( MR_LANG( 'SATELLITE' )    )
		list_Mainmenu.append( MR_LANG( 'FTA/CAS' )      )
		list_Mainmenu.append( MR_LANG( 'FAVORITES' )    )
		list_Mainmenu.append( MR_LANG( 'MODE' ) )
		#list_Mainmenu.append( MR_LANG( 'Back' ) )
		testlistItems = []
		for item in range( len(list_Mainmenu) ) :
			testlistItems.append( xbmcgui.ListItem(list_Mainmenu[item]) )

		self.mCtrlListMainmenu.addItems( testlistItems )


		try :
			if self.mFlag_EditChanged :
				#satellite list
				self.mListSatellite = self.mDataCache.Satellite_GetConfiguredList( )

				#FTA list
				self.mListCasList = self.mDataCache.Fta_cas_GetList( self.mUserMode.mServiceType )

				#Favorite list
				self.mListFavorite = self.mDataCache.Favorite_GetList( FLAG_ZAPPING_CHANGE, self.mUserMode.mServiceType )

			else :
				self.mListSatellite = self.mDataCache.Satellite_GetConfiguredList( )
				self.mListCasList = self.mDataCache.Fta_cas_GetList( )
				self.mListFavorite = self.mDataCache.Favorite_GetList( )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


		testlistItems = []

		if self.mUserMode.mMode == ElisEnum.E_MODE_ALL :
			#for item in range( len( self.mListAllChannel ) ) :
			#	testlistItems.append( xbmcgui.ListItem( self.mListAllChannel[item] ) )
			testlistItems.append( xbmcgui.ListItem( '' ) )

		if self.mUserMode.mMode == ElisEnum.E_MODE_SATELLITE :
			if self.mListSatellite :
				for item in self.mListSatellite:
					ret = GetSelectedLongitudeString( item.mLongitude, item.mName )
					testlistItems.append(xbmcgui.ListItem( ret ) )

		elif self.mUserMode.mMode == ElisEnum.E_MODE_CAS :
			if self.mListCasList :
				for item in self.mListCasList :
					ret = '%s(%s)'% ( item.mName, item.mChannelCount )
					testlistItems.append(xbmcgui.ListItem( ret ) )

		elif self.mUserMode.mMode == ElisEnum.E_MODE_FAVORITE :
			if self.mListFavorite :
				for item in self.mListFavorite :
					testlistItems.append(xbmcgui.ListItem( item.mGroupName ) )

		self.mCtrlListSubmenu.addItems( testlistItems )

		self.mNavChannel = None
		self.mChannelList = None

		zappingName = self.SetSlideMenuHeader( aInitLoad )

		#path tree, Mainmenu/Submenu
		lblChannelPath = EnumToString( 'mode', self.mUserMode.mMode ).upper( )
		if zappingName :
			lblChannelPath = '%s > %s'% ( lblChannelPath, zappingName )

		lblSort = EnumToString( 'sort', self.mUserMode.mSortingMode )
		lblChannelSort = MR_LANG( 'Sorted by %s' )% lblSort
		lblButtonSort = '%s : %s'% ( MR_LANG( 'sort' ).upper(), lblSort.upper() )

		self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_PATH, lblChannelPath )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_SORT, lblChannelSort )
		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_SORTING,     lblButtonSort )

		"""
		label1 = EnumToString( 'mode', self.mUserMode.mMode )
		label2 = zappingName
		label3 = EnumToString( 'sort', self.mUserMode.mSortingMode )
		if self.mUserMode.mMode == ElisEnum.E_MODE_ALL :
			label = '%s [COLOR grey3]>[/COLOR] sort by %s'% ( label1.upper( ),label3.title( ) )
		else :
			label = '%s [COLOR grey3]>[/COLOR] %s [COLOR grey2]/ sort by %s[/COLOR]'% ( label1.upper( ),label2.title( ),label3.title( ) )
		"""


		"""
		lblSkip = 'skipped'
		lblTable= 'all'
		if self.mDataCache.mSkip :
			lblSkip = 'all'
		if self.mDataCache.mChannelListDBTable :
			lblTable = 'zapping'
		LOG_TRACE( '>>>>>>>>>>>>>>>>>>>>>>>>>> skip[%s] table[%s]'% (lblSkip, lblTable) )
		LOG_TRACE( 'zappingMode[%s] sortMode[%s] serviceType[%s]'% \
			( EnumToString( 'mode', self.mUserMode.mMode),             \
			  EnumToString( 'sort', self.mUserMode.mSortingMode),     \
			  EnumToString( 'type', self.mUserMode.mServiceType) ) )
		if self.mChannelList :
			LOG_TRACE( '>>>>>>>>>>>>>>>>>>>>>>>>>flag_editChange[%s] len[%s] datachche[%s]'% (self.mFlag_EditChanged, len(self.mChannelList), len(self.mDataCache.mChannelList) ))
			#LOG_TRACE( 'len[%s] ch[%s]'% (len(self.mChannelList),ClassToList( 'convert', self.mChannelList ) ) )
		else :
			LOG_TRACE( '>>>>>>>>>>>>>>>>>>>>>>>>>flag_editChange[%s] len[%s] datachche[%s]'% (self.mFlag_EditChanged, self.mChannelList, self.mDataCache.mChannelList ))
		"""


	def UpdateChannelList( self ) :
		#starttime = time.time( )
		#print '==================== TEST TIME[LIST] START[%s]'% starttime

		#no channel is set Label comment
		self.mCtrlListCHList.reset( )
		if E_SUPPORT_FRODO_EMPTY_LISTITEM :
			xbmcgui.Window( 10000 ).setProperty( 'isEmpty', E_TAG_FALSE )

		if self.mChannelList == None :
			if self.mFlag_DeleteAll :
				self.mListItems = None
				label = MR_LANG( 'No Channel' )			
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, label )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_SELECT_NUMBER, '0' )

			if E_SUPPORT_FRODO_EMPTY_LISTITEM :
				self.mListItems = []
				listItem = xbmcgui.ListItem( 'empty channel' )
				self.mListItems.append( listItem )
				self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, self.mListItems, E_TAG_ADD_ITEM )
				xbmcgui.Window( 10000 ).setProperty( 'isEmpty', E_TAG_TRUE )
				self.mListItems = None

			return 

		reloadPos = False
		if self.mListItems == None or self.mDataCache.GetChannelReloadStatus( ) == True :
			self.mListItems = []
			reloadPos = True
			self.mCtrlListCHList.reset( )
			self.mDataCache.SetChannelReloadStatus( False )

			for iChannel in self.mChannelList :
				listItem = xbmcgui.ListItem( '%04d %s'%( iChannel.mNumber, iChannel.mName ) )

				if iChannel.mLocked : 
					listItem.setProperty( E_XML_PROPERTY_LOCK, E_TAG_TRUE )
				if iChannel.mIsCA : 
					listItem.setProperty( E_XML_PROPERTY_CAS,  E_TAG_TRUE )
				if self.mRecCount :
					if self.mRecordInfo1 :
						if iChannel.mSid == self.mRecordInfo1.mServiceId and \
						   iChannel.mName == self.mRecordInfo1.mChannelName and \
						   iChannel.mNumber == self.mRecordInfo1.mChannelNo :
							listItem.setProperty( E_XML_PROPERTY_RECORDING, E_TAG_TRUE )
							LOG_TRACE('----------match rec[%s %s]'% ( iChannel.mNumber, iChannel.mName ) )
					if self.mRecordInfo2 :
						if iChannel.mSid == self.mRecordInfo2.mServiceId and \
						   iChannel.mName == self.mRecordInfo2.mChannelName and \
						   iChannel.mNumber == self.mRecordInfo2.mChannelNo :
							listItem.setProperty( E_XML_PROPERTY_RECORDING, E_TAG_TRUE )
							LOG_TRACE('----------match rec[%s %s]'% ( iChannel.mNumber, iChannel.mName ) )

				if self.mViewMode == WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW and iChannel.mSkipped == True : 
					listItem.setProperty( E_XML_PROPERTY_SKIP, E_TAG_TRUE )

				self.mListItems.append( listItem )

		self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, self.mListItems, E_TAG_ADD_ITEM )

		#get last channel
		iChannel = None
		iChannel = self.mDataCache.Channel_GetCurrent( reloadPos )
		if iChannel :
			self.mNavChannel = iChannel
			self.mCurrentChannel = self.mNavChannel.mNumber

		#detected to last focus
		isFind = False
		iChannelIdx = 0
		for iChannel in self.mChannelList :
			if iChannel.mNumber == self.mCurrentChannel :
				isFind = True
				break
			iChannelIdx += 1

		if isFind == False :
			iChannelIdx = 0

		self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, iChannelIdx, E_TAG_SET_SELECT_POSITION )
		time.sleep( 0.02 )

		#select item idx, print GUI of 'current / total'
		self.mCurrentPosition = iChannelIdx
		label = '%s - %s'% ( EnumToString( 'type', self.mNavChannel.mServiceType ).upper( ), self.mNavChannel.mName )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_SELECT_NUMBER, '%s'% ( iChannelIdx + 1 ) )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, label )
		#LOG_TRACE('-----------curr[%s]'% (iChannelIdx + 1) )

		#endtime = time.time( )
		#print '==================== TEST TIME[LIST] END[%s] loading[%s]'% (endtime, endtime-starttime )


	def ResetLabel( self ) :
		if self.mUserMode.mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
			self.mCtrlRadioButtonTV.setSelected( True )
			self.mCtrlRadioButtonRadio.setSelected( False )
		elif self.mUserMode.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
			self.mCtrlRadioButtonTV.setSelected( False )
			self.mCtrlRadioButtonRadio.setSelected( True )

		self.mCtrlProgress.setPercent( 0 )
		self.mCtrlProgress.setVisible( False )

		self.mCtrlLabelSelectItem.setLabel( str( '%s'% ( self.mCtrlListCHList.getSelectedPosition( ) + 1 ) ) )
		self.mCtrlLabelEPGName.setLabel( '' )
		self.mCtrlLabelEPGTime.setLabel( '' )
		self.mCtrlLabelLongitudeInfo.setLabel( '' )
		self.mCtrlLabelCareerInfo.setLabel( '' )
		self.mCtrlLabelLockedInfo.setVisible(False)
		self.UpdatePropertyGUI( E_XML_PROPERTY_SUBTITLE, E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_DOLBY,    E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_HD,       E_TAG_FALSE )


	def Epgevent_GetCurrent( self ) :
		try :
			if self.mIsTune == True :
				if not self.mNavChannel :
					LOG_TRACE( 'No Channel' )
					return

				sid  = self.mNavChannel.mSid
				tsid = self.mNavChannel.mTsid
				onid = self.mNavChannel.mOnid
				iEPG = None
				iEPG = self.mDataCache.Epgevent_GetCurrent( sid, tsid, onid )
				if iEPG == None or iEPG.mError != 0 :
					return

				self.mNavEpg = iEPG
				#iEPG.printdebug( )

			else :
				if self.mChannelList :
					idx = self.mCtrlListCHList.getSelectedPosition( )
					iChannel = self.mChannelList[idx]
					chNumber = iChannel.mNumber

					#for iChannel in self.mChannelList:
					#	if iChannel.mNumber == chNumber :
					#iChannel = self.mChannelListHash.get( chNumber )
					#if iChannel :
					self.mNavChannel = None
					self.mNavChannel = iChannel

					sid  = iChannel.mSid
					tsid = iChannel.mTsid
					onid = iChannel.mOnid
					iEPG = None
					#iEPG = self.mDataCache.Epgevent_GetCurrent( sid, tsid, onid )
					#iEPGList = self.mDataCache.Epgevent_GetCurrentByChannelFromEpgCF( sid, tsid, onid )
					iEPG = self.mDataCache.Epgevent_GetCurrent( sid, tsid, onid )
					LOG_TRACE( '----chNum[%s] chName[%s] sid[%s] tsid[%s] onid[%s] epg[%s] gmtTime[%s]'% (iChannel.mNumber, iChannel.mName, sid, tsid, onid, iEPG, self.mDataCache.Datetime_GetGMTTime( ) ) )
					if iEPG == None or iEPG.mError != 0 :
						self.mNavEpg = 0

					self.mNavEpg = iEPG
							
		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def UpdateControlGUI( self, aCtrlID = None, aValue = None, aExtra = None ) :
		#LOG_TRACE( 'Enter control[%s] value[%s]'% (aCtrlID, aValue) )

		if aCtrlID == E_CONTROL_ID_LABEL_CHANNEL_NAME :
			self.mCtrlLabelChannelName.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_LONGITUDE_INFO :
			self.mCtrlLabelLongitudeInfo.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_CAREER_INFO :
			self.mCtrlLabelCareerInfo.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_EPG_NAME :
			self.mCtrlLabelEPGName.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_EPG_TIME :
			self.mCtrlLabelEPGTime.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_GROUP_LOCKED_INFO :
			self.mCtrlLabelLockedInfo.setVisible( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_CHANNEL_PATH :
			self.mCtrlLabelChannelPath.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_CHANNEL_SORT :
			self.mCtrlLabelChannelSort.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_BUTTON_SORTING :
			self.mCtrlButtonSorting.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_RADIOBUTTON_TV :
			if aExtra == E_TAG_SELECT :
				self.mCtrlRadioButtonTV.setSelected( aValue )
			elif aExtra == E_TAG_ENABLE :
				self.mCtrlRadioButtonTV.setEnabled( aValue )

		elif aCtrlID == E_CONTROL_ID_RADIOBUTTON_RADIO :
			if aExtra == E_TAG_SELECT :
				self.mCtrlRadioButtonRadio.setSelected( aValue )
			elif aExtra == E_TAG_ENABLE :
				self.mCtrlRadioButtonRadio.setEnabled( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_SELECT_NUMBER :
			self.mCtrlLabelSelectItem.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LIST_CHANNEL_LIST :
			if aExtra == E_TAG_SET_SELECT_POSITION :
				self.UpdateControlListSelectItem( self.mCtrlListCHList, aValue )
				#self.mCtrlListCHList.selectItem( aValue )
			elif aExtra == E_TAG_ENABLE :
				self.mCtrlListCHList.setEnabled( aValue )
			elif aExtra == E_TAG_ADD_ITEM :
				self.mCtrlListCHList.addItems( aValue )

		elif aCtrlID == E_CONTROL_FOCUSED :
			self.setFocusId( aValue )

		elif aCtrlID == E_SLIDE_CLOSE :
			self.mCtrlListCHList.setEnabled( True )
			self.setFocusId( E_CONTROL_ID_GROUP_CHANNEL_LIST )

		elif aCtrlID == E_SETTING_MINI_TITLE :
			self.mCtrlLabelMiniTitle.setLabel( aValue )


	def UpdatePropertyGUI( self, aPropertyID = None, aValue = None ) :
		#LOG_TRACE( 'Enter property[%s] value[%s]'% (aPropertyID, aValue) )
		if aPropertyID == None :
			return

		if aPropertyID == E_XML_PROPERTY_EDITINFO or aPropertyID == E_XML_PROPERTY_MOVE :
			rootWinow = xbmcgui.Window( 10000 )
			rootWinow.setProperty( aPropertyID, aValue )			
			
		else :
			self.setProperty( aPropertyID, aValue )


	def UpdateChannelAndEPG( self ) :
		if self.mChannelList == None or len(self.mChannelList) < 1 :
			return

		if self.mNavChannel :
			#update channel name
			if self.mIsTune == True :
				#strType = self.UpdateServiceType( self.mNavChannel.mServiceType )
				label = '%s - %s'% ( EnumToString( 'type', self.mNavChannel.mServiceType ).upper(), self.mNavChannel.mName )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, label )

			#update longitude info
			satellite = self.mDataCache.Satellite_GetByChannelNumber( self.mNavChannel.mNumber, -1 )
			if not satellite :
				#LOG_TRACE( 'Fail GetByChannelNumber by Cache' )
				satellite = self.mDataCache.Satellite_GetByChannelNumber( self.mNavChannel.mNumber, self.mNavChannel.mServiceType )

			if satellite :
				label = GetSelectedLongitudeString( satellite.mLongitude, satellite.mName )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_LONGITUDE_INFO, label )
			else :
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_LONGITUDE_INFO, '' )

			#update lock-icon visible
			if self.mNavChannel.mLocked :
				self.UpdateControlGUI( E_CONTROL_ID_GROUP_LOCKED_INFO, True )


			#update career info
			if self.mNavChannel.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBS:
				value1 = self.mNavChannel.mCarrier.mDVBS.mPolarization
				value2 = self.mNavChannel.mCarrier.mDVBS.mFrequency
				value3 = self.mNavChannel.mCarrier.mDVBS.mSymbolRate

				polarization = EnumToString( 'Polarization', value1 )
				careerLabel = '%s MHz, %s KS/S, %s'% (value2, value3, polarization)
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_CAREER_INFO, careerLabel )

			elif self.mNavChannel.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBT :
				pass
			elif self.mNavChannel.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBC :
				pass
			elif self.mNavChannel.mCarrierType == ElisEnum.E_CARRIER_TYPE_INVALID :
				pass
				
			"""
			#is cas?
			if self.mNavChannel.mIsCA == True:
				#scrambled
				#ToDO : pincode
			"""


		#update epgName uiID(304)
		if self.mNavEpg :
			try :

				startTime = TimeToString( self.mNavEpg.mStartTime + self.mLocalOffset, TimeFormatEnum.E_HH_MM )
				endTime   = TimeToString( self.mNavEpg.mStartTime + self.mNavEpg.mDuration + self.mLocalOffset, TimeFormatEnum.E_HH_MM )
				label = '%s - %s'% (startTime, endTime)
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_TIME, label )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_NAME, self.mNavEpg.mEventName )
				self.mCtrlProgress.setVisible( True )

				#component
				setPropertyList = []
				setPropertyList = GetPropertyByEPGComponent( self.mNavEpg )
				self.UpdatePropertyGUI( E_XML_PROPERTY_SUBTITLE, setPropertyList[0] )
				self.UpdatePropertyGUI( E_XML_PROPERTY_DOLBY,    setPropertyList[1] )
				self.UpdatePropertyGUI( E_XML_PROPERTY_HD,       setPropertyList[2] )

			except Exception, e:
				LOG_TRACE( 'Error exception[%s]'% e )


		else:
			LOG_TRACE( 'event null' )


	@RunThread
	def EPGProgressThread( self ) :
		loop = 0
		while self.mEnableProgressThread :
			#LOG_TRACE( 'repeat <<<<' )
			if  ( loop % 200 ) == 0 :
				self.UpdateProgress( )
			
			time.sleep( 0.05 )
			loop += 1


	def UpdateProgress( self ) :
		try:
			self.mLocalTime = self.mDataCache.Datetime_GetLocalTime( )

			if self.mNavEpg :
				startTime = self.mNavEpg.mStartTime + self.mLocalOffset
				endTime   = startTime + self.mNavEpg.mDuration
				pastDuration = endTime - self.mLocalTime

				if self.mLocalTime > endTime: #Already past
					self.mCtrlProgress.setPercent( 100 )
					return

				elif self.mLocalTime < startTime :
					self.mCtrlProgress.setPercent( 0 )
					return

				if pastDuration < 0 :
					pastDuration = 0

				if self.mNavEpg.mDuration > 0 :
					percent = 100 - ( pastDuration * 100.0 / self.mNavEpg.mDuration )
				else :
					percent = 0

				#LOG_TRACE( 'percent=%d'% percent )
				self.mCtrlProgress.setPercent( percent )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )
			#self.mLocalTime = 0


	def ShowMoveToGUI( self, aStart, aEnd, aInit = False ) :
		self.mListItems = []
		showList = self.mNewChannelList
		if aInit :
			showList = self.mChannelList
			#self.mCtrlListCHList.reset( )

		for i in range( aStart, aEnd ) :
			iChannel = showList[i]
			if iChannel == None : continue

			#listItem = xbmcgui.ListItem( '%04d %s'%( iChannel.mNumber, iChannel.mName ) )
			isFind = False
			for item in self.mMoveList :
				if iChannel.mNumber == item.mNumber : 
					listItem = xbmcgui.ListItem( '[COLOR white]%04d %s[/COLOR]'% ( iChannel.mNumber, iChannel.mName ), 'MOVE' )
					listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_TRUE )
					#LOG_TRACE( 'move idx[%s] [%04d %s]'% ( i, iChannel.mNumber, iChannel.mName ) )
					isFind = True
					break

			if not isFind :
				listItem = xbmcgui.ListItem( '%04d %s'% ( iChannel.mNumber, iChannel.mName ) )
			if iChannel.mLocked  : listItem.setProperty( E_XML_PROPERTY_LOCK, E_TAG_TRUE )
			if iChannel.mIsCA    : listItem.setProperty( E_XML_PROPERTY_CAS,  E_TAG_TRUE )
			if iChannel.mSkipped : listItem.setProperty( E_XML_PROPERTY_SKIP, E_TAG_TRUE )
			#LOG_TRACE( 'move idx[%s] [%04d %s]'% ( i, iChannel.mNumber, iChannel.mName ) )

			self.mListItems.append(listItem)

		self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, self.mListItems, E_TAG_ADD_ITEM )


	def SetMoveMode( self, aMode, aMove = None ) :
		if aMode == FLAG_OPT_MOVE :
			self.OpenBusyDialog( )
			try :
				self.mMoveList = []
				self.mRefreshCurrentIdx = -1
				self.mNewChannelList = deepcopy( self.mChannelList )
				listHeight = self.mCtrlListCHList.getHeight( )
				self.mItemCount = listHeight / self.mItemHeight
				#LOG_TRACE( 'listHeight[%d] itemHeight[%d] itemCount[%d]'% (listHeight, self.mItemHeight, self.mItemCount) )

				if not self.mMarkList :
					lastPos = self.mCtrlListCHList.getSelectedPosition( )
					self.mMarkList.append( lastPos )
					LOG_TRACE( 'last position[%s]'% lastPos )
				
				self.mMarkList.sort( )
				#LOG_TRACE( '1====mark[%s]'% self.mMarkList )

				#2. make listing of ichannel in marked idx
				idxFirst = int(self.mMarkList[0])
				self.mMoveList.append( self.mNewChannelList[idxFirst] )
				for idx in range( 1, len(self.mMarkList) ) :
					i = int( self.mMarkList[idx] )
					nextIdx = idxFirst + idx
					item = self.mNewChannelList.pop( i )
					self.mNewChannelList.insert( nextIdx, item )
					self.mMoveList.append( item )
					self.mMarkList[idx] = nextIdx

				#find current channel
				for i in range( len( self.mMarkList ) ) :
					idx = self.mMarkList[i]
					if self.mNewChannelList[idx].mNumber == self.mCurrentChannel :
						self.mRefreshCurrentIdx = i
				LOG_TRACE( 'mRefreshCurrentIdx[%s]'% self.mRefreshCurrentIdx )


				self.mMoveFlag = True
				self.mListItems = []
				chCount = len(self.mNewChannelList)
				self.mViewFirst = idxFirst
				self.mViewEnd = idxFirst + self.mItemCount

				#show, top ~ bottom
				if chCount < self.mItemCount :
					self.mViewFirst = 0
					self.mViewEnd   = chCount

				elif chCount - idxFirst < self.mItemCount :
					self.mViewFirst = chCount - self.mItemCount
					self.mViewEnd = chCount


				#LOG_TRACE( '2====mark[%s] view[%s]~[%s]'% (self.mMarkList, self.mViewFirst, self.mViewEnd) )

				self.ShowMoveToGUI( self.mViewFirst, self.mViewEnd )
				self.UpdatePropertyGUI( E_XML_PROPERTY_MOVE, E_TAG_TRUE )

			except Exception, e:
				LOG_TRACE( 'Error except[%s]'% e )

			self.CloseBusyDialog( )

		elif aMode == FLAG_OPT_MOVE_OK :
			self.OpenBusyDialog( )
			try :
				self.UpdatePropertyGUI( E_XML_PROPERTY_MOVE, E_TAG_FALSE )

				idxFirst = self.mMarkList[0]

				makeNumber = idxFirst + 1
				makeFavidx = idxFirst + 1
				#LOG_TRACE( 'insert makeFavidx[%s], makeNumber[%s]'% (makeFavidx, makeNumber) )
				#LOG_TRACE( 'mark[%s]'% self.mMarkList )

				idxCurrent = -1
				ret = False
				if self.mUserMode.mMode == ElisEnum.E_MODE_FAVORITE :
					groupName = self.mFavoriteGroupList[self.mUserSlidePos.mSub]
					if groupName :
						ret = self.mDataCache.FavoriteGroup_MoveChannels( groupName, makeFavidx, self.mUserMode.mServiceType, self.mMoveList )
						#LOG_TRACE( '==========group========[%s]'% groupName )
				else :
					ret = self.mDataCache.Channel_Move( self.mUserMode.mServiceType, makeNumber, self.mMoveList )

					if ret and self.mRefreshCurrentIdx != -1 :
						idxCurrent = self.mMarkList[self.mRefreshCurrentIdx]
						#LOG_TRACE( 'move idx[%s] num[%s] name[%s]'% ( idxCurrent, self.mNewChannelList[idxCurrent].mNumber, self.mNewChannelList[idxCurrent].mName) )


				#LOG_TRACE( 'move[%s]'% ret )

				if ret :
					ret = self.mDataCache.Channel_Save( )
					#LOG_TRACE( 'save[%s]'% ret )

				self.mMarkList = []
				self.mMoveList = []
				self.mListItems = None
				self.SubMenuAction( E_SLIDE_ACTION_SUB )
				self.mMoveFlag = False

				if idxCurrent != -1 :
					self.mRefreshCurrentChannel = self.mChannelList[idxCurrent].mNumber
					#LOG_TRACE( 'after idx[%s] num[%s] name[%s]'% ( idxCurrent, self.mChannelList[idxCurrent].mNumber, self.mChannelList[idxCurrent].mName) )

				self.mCtrlListCHList.reset( )
				self.ShowMoveToGUI( 0, len( self.mChannelList ), True )
				#LOG_TRACE ( '========= move exit ===mark[%s] view[%s]~[%s]'% (self.mMarkList, self.mViewFirst, self.mViewEnd) )


				self.mCtrlListCHList.setVisible( False )

				self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, self.mViewEnd - 1, E_TAG_SET_SELECT_POSITION )
				self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, idxFirst, E_TAG_SET_SELECT_POSITION )
				time.sleep( 0.15 )
				self.mCtrlListCHList.setVisible( True )

			except Exception, e:
				LOG_TRACE( 'Error except[%s]'% e )

			self.CloseBusyDialog( )
			#LOG_TRACE ( '========= move End ===' )

		elif aMode == FLAG_OPT_MOVE_EXIT :
			self.mMoveFlag = False
			self.mListItems = None
			self.UpdatePropertyGUI( E_XML_PROPERTY_MOVE, E_TAG_FALSE )

			self.mNewChannelList = self.mChannelList
			self.ShowMoveToGUI( 0, len( self.mChannelList ) )
			self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, self.mLastPos, E_TAG_SET_SELECT_POSITION )

		elif aMode == FLAG_OPT_MOVE_UPDOWN :
			updown= 0
			moveidx = 0
			markList= []
			lastidx = len(self.mMarkList) - 1

			#1. moving
			if aMove == Action.ACTION_MOVE_UP :	
				updown = -1
				moveidx = self.mMarkList[0] + updown

			elif aMove == Action.ACTION_MOVE_DOWN :	
				updown = 1
				moveidx = self.mMarkList[lastidx] + updown

			elif aMove == Action.ACTION_PAGE_UP :	
				updown = -self.mItemCount
				moveidx = self.mMarkList[0] + updown

			elif aMove == Action.ACTION_PAGE_DOWN :	
				updown = self.mItemCount
				moveidx = self.mMarkList[lastidx] + updown

			# barrier blocking
			if moveidx < 0 or moveidx > len( self.mNewChannelList ) - 1 :
				LOG_TRACE( 'List limit, DO NOT move!! moveidx[%s]'% moveidx)
				return

			#pop moveList
			popidx = self.mMarkList[0]
			for idx in self.mMoveList :
				item = self.mNewChannelList.pop( popidx )
				#LOG_TRACE( 'pop idx[%s] item[%s] len[%s]'% (popidx, item.mNumber, len(self.mNewChannelList)) )


			#update index in moveList
			for idx in self.mMarkList :
				idxNew = int(idx) + updown
				markList.append( idxNew )
			self.mMarkList = []
			self.mMarkList = markList
			insertPos = self.mMarkList[0]

			#insert moveList
			for i in range(len(self.mMoveList)) :
				idx = lastidx - i
				self.mNewChannelList.insert(insertPos, self.mMoveList[idx])

			#LOG_TRACE( 'insert idx[%s] item[%s] len[%s]'% (insertPos, self.mNewChannelList[insertPos].mNumber, len(self.mNewChannelList)) )

			#show top ~ bottom
			if self.mMarkList[0] < self.mViewFirst or self.mMarkList[lastidx] >= self.mViewEnd :
				self.mViewFirst = self.mViewFirst + updown
				self.mViewEnd   = self.mViewEnd   + updown
				#LOG_TRACE( 'changed view item' )

			bottom = len(self.mNewChannelList)
			if self.mViewEnd > bottom :
				self.mViewFirst = bottom - self.mItemCount
				self.mViewEnd = bottom

			#LOG_TRACE( 'view Top[%s]~Bot[%s] insertPos[%s]'% (self.mViewFirst, self.mViewEnd, insertPos) )
			self.ShowMoveToGUI( self.mViewFirst, self.mViewEnd )

			#select item idx, print GUI of 'current / total'
			pos = '%s'% ( self.mViewFirst + 1 )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_SELECT_NUMBER, pos )



	def SetMark( self, aPos ) :
		idx = 0
		isExist = False

		#aready mark is mark delete
		for i in self.mMarkList :
			if i == aPos :
				self.mMarkList.pop(idx)
				isExist = True
			idx += 1

		#do not exist is append mark
		if isExist == False : 
			self.mMarkList.append( aPos )

		listItem = self.mCtrlListCHList.getListItem(aPos)

		#mark toggle: disable/enable
		if listItem.getProperty(E_XML_PROPERTY_MARK) == E_TAG_TRUE : 
			listItem.setProperty(E_XML_PROPERTY_MARK, E_TAG_FALSE)
		else :
			listItem.setProperty(E_XML_PROPERTY_MARK, E_TAG_TRUE)


	def ClearMark( self ) :
		if self.mMarkList == None or len( self.mMarkList ) < 1 or \
		   self.mChannelList == None or len( self.mChannelList ) < 1 :
			return

		for pos in self.mMarkList :
			self.mCtrlListCHList.getListItem( pos ).setProperty( E_XML_PROPERTY_MARK, E_TAG_FALSE )


	def LoadFavoriteGroupList( self ) :
		self.mListFavorite = self.mDataCache.Favorite_GetList( FLAG_ZAPPING_CHANGE, self.mUserMode.mServiceType )
		self.mFavoriteGroupList = []
		if self.mListFavorite :
			for item in self.mListFavorite :
				#copy to favoriteGroup
				self.mFavoriteGroupList.append( item.mGroupName )


	def AddFavoriteChannels( self, aChannelList = None, aGroupName = '' ) :
		if aChannelList == None or len( aChannelList ) < 1 :
			return self.mDataCache.Channel_GetList( FLAG_ZAPPING_CHANGE, self.mUserMode.mServiceType, ElisEnum.E_MODE_ALL, self.mUserMode.mSortingMode )

		else :
			if aGroupName == None or aGroupName == '' :
				self.mMarkList = []
				return

			numList = []
			lastPos = self.mCtrlListCHList.getSelectedPosition( )
			for idx in self.mMarkList :
				chNum = ElisEInteger( )
				chNum.mParam = aChannelList[idx].mNumber
				numList.append( chNum )

			if not numList or len( numList ) < 1 :
				LOG_TRACE( 'Selection failed!!!' )
				return

			ret = self.mDataCache.Favoritegroup_AddChannelByNumber( aGroupName, self.mUserMode.mServiceType, numList )
			LOG_TRACE( 'contextAction ret[%s]'% ret )

			self.mMarkList = []
			self.mListItems = None
			self.SubMenuAction( E_SLIDE_ACTION_SUB )
			self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, lastPos, E_TAG_SET_SELECT_POSITION )


	def DoContextAction( self, aMode, aContextAction, aGroupName = '' ) :
		ret = ''
		numList = []
		isIncludeRec = False
		isIncludeTimer = False
		lastPos = self.mCtrlListCHList.getSelectedPosition( )
		#LOG_TRACE( 'groupName[%s] lastPos[%s]'% ( aGroupName, lastPos) )

		if self.mChannelList :
			#1.no mark : set current position item
			if not self.mMarkList :
				self.mMarkList.append( lastPos )

			#2.set mark : list all
			isRefreshCurrentChannel = False
			for idx in self.mMarkList :
				chNum = ElisEInteger( )
				chNum.mParam = self.mChannelList[idx].mNumber
				numList.append( chNum )

				if self.mCurrentChannel == self.mChannelList[idx].mNumber :
					isRefreshCurrentChannel = True

				#check rec item
				if self.mRecCount :
					if self.mRecordInfo1 and \
					   ( self.mRecordInfo1.mServiceId == self.mChannelList[idx].mSid and \
					   self.mRecordInfo1.mChannelName == self.mChannelList[idx].mName and \
					   self.mRecordInfo1.mChannelNo == self.mChannelList[idx].mNumber ) or \
					   self.mRecordInfo2 and \
					   ( self.mRecordInfo2.mServiceId == self.mChannelList[idx].mSid and \
					   self.mRecordInfo2.mChannelName == self.mChannelList[idx].mName and \
					   self.mRecordInfo2.mChannelNo == self.mChannelList[idx].mNumber ) :
						isIncludeRec = True
				LOG_TRACE('mRecCount[%s] rec1[%s] rec2[%s] isRec[%s]'% (self.mRecCount, self.mRecordInfo1, self.mRecordInfo2, isIncludeRec) )

			if not numList or len( numList ) < 1 :
				LOG_TRACE( 'MarkList failed!!!' )
				return


		if aContextAction == CONTEXT_ACTION_LOCK :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_INPUT_PINCODE )
			dialog.SetTitleLabel( MR_LANG( 'Enter your PIN code' ) )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				ret = self.mDataCache.Channel_LockByNumber( True, int(self.mUserMode.mServiceType), numList )
			else :
				return

		elif aContextAction == CONTEXT_ACTION_UNLOCK :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_INPUT_PINCODE )
			dialog.SetTitleLabel( MR_LANG( 'Enter your PIN code' ) )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				ret = self.mDataCache.Channel_LockByNumber( False, int(self.mUserMode.mServiceType), numList )
			else :
				return

		elif aContextAction == CONTEXT_ACTION_SKIP :
			ret = self.mDataCache.Channel_SkipByNumber( True, int(self.mUserMode.mServiceType), numList )

		elif aContextAction == CONTEXT_ACTION_UNSKIP :
			ret = self.mDataCache.Channel_SkipByNumber( False, int(self.mUserMode.mServiceType), numList )

		elif aContextAction == CONTEXT_ACTION_ADD_TO_FAV :
			if aGroupName : 
				ret = self.mDataCache.Favoritegroup_AddChannelByNumber( aGroupName, self.mUserMode.mServiceType, numList )
			else :
				ret = 'group None'

		elif aContextAction == CONTEXT_ACTION_DELETE :
			#check added Timer
			mTimerList = []
			timerList = self.mDataCache.Timer_GetTimerList( )
			if timerList and len( timerList ) > 0 :
				for iTimer in timerList :
					for idx in self.mMarkList :
						if iTimer.mSid == self.mChannelList[idx].mSid and \
						   iTimer.mTsid == self.mChannelList[idx].mTsid and \
						   iTimer.mOnid == self.mChannelList[idx].mOnid :
							isIncludeTimer = True
							LOG_TRACE('timerCh[%s %s] mark idx[%s] ch[%s %s]'% (iTimer.mChannelNo, iTimer.mName, idx, self.mChannelList[idx].mNumber, self.mChannelList[idx].mName) )
							mTimerList.append( iTimer )

			LOG_TRACE('isRec[%s] isTimer[%s]'% (isIncludeRec, isIncludeTimer) )
			if isIncludeRec or isIncludeTimer :
				msg = MR_LANG( 'Are you sure you want to delete the channels\nincluding currently recording or reserved?' )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( MR_LANG( 'Delete channels' ), msg )
				dialog.doModal( )

				answer = dialog.IsOK( )
				if answer == E_DIALOG_STATE_YES :
					#delete timer
					for iTimer in mTimerList :
						self.mDataCache.Timer_DeleteTimer( iTimer.mTimerId )
				else :
					#cancel for appended lastpos
					if self.mMarkList and len( self.mMarkList ) < 2 :
						self.mMarkList = []
					return


				"""
				elif answer == E_DIALOG_STATE_NO :
					#no delete timer and channel
					for iTimer in mTimerList :
						tmpList = deepcopy( numList )
						for idx in range( len( tmpList ) ) :
							if tmpList[idx].mParam == iTimer.mChannelNo :
								numList.pop( idx )
				"""


			if aMode == FLAG_OPT_LIST :
				ret = self.mDataCache.Channel_DeleteByNumber( int( self.mUserMode.mServiceType ), 1, numList )

				#reset Tune by Next Channel
				if ret and isRefreshCurrentChannel :
					afterCount = len( self.mChannelList ) - len( numList )
					if afterCount < 1 :
						self.mRefreshCurrentChannel = False
					else :
						if self.mCurrentChannel < afterCount :
							self.mRefreshCurrentChannel = self.mCurrentChannel
						elif self.mCurrentChannel == afterCount :
							self.mRefreshCurrentChannel = int( self.mCurrentChannel ) - 1
						else :
							self.mRefreshCurrentChannel = afterCount

			else :
				aGroupName = self.mFavoriteGroupList[self.mUserSlidePos.mSub]
				if aGroupName :
					ret = self.mDataCache.Favoritegroup_RemoveChannelByNumber( aGroupName, self.mUserMode.mServiceType, numList )
				else :
					ret = 'group None'

		elif aContextAction == CONTEXT_ACTION_MOVE :
			self.mLastPos = lastPos
			self.SetMoveMode(FLAG_OPT_MOVE, None )
			return

		elif aContextAction == CONTEXT_ACTION_CREATE_GROUP_FAV :
			if aGroupName :
				ret = self.mDataCache.Favoritegroup_Create( aGroupName, self.mUserMode.mServiceType )	#default : ElisEnum.E_SERVICE_TYPE_TV
				if ret :
					self.LoadFavoriteGroupList( )
				#self.RefreshSlideMenu( self.mUserSlidePos.mMain, self.mUserSlidePos.mSub, True )
				return

		elif aContextAction == CONTEXT_ACTION_RENAME_FAV :
			if aGroupName :
				name = re.split( ':', aGroupName)
				ret = self.mDataCache.Favoritegroup_ChangeName( name[1], self.mUserMode.mServiceType, name[2] )
				if ret :
					self.LoadFavoriteGroupList( )

				#self.SubMenuAction( E_SLIDE_ACTION_MAIN, E_SLIDE_MENU_FAVORITE )
				#LOG_TRACE( 'pos main[%s] sub[%s]'% (self.mUserSlidePos.mMain, self.mUserSlidePos.mSub ) )
				return

		elif aContextAction == CONTEXT_ACTION_DELETE_FAV :
			if aGroupName :
				ret = self.mDataCache.Favoritegroup_Remove( aGroupName, self.mUserMode.mServiceType )
				if ret :
					self.LoadFavoriteGroupList( )
					LOG_TRACE( 'favRemove after favList ori[%s] edit[%s]'% (self.mListFavorite, self.mFavoriteGroupList))

				self.SubMenuAction( E_SLIDE_ACTION_MAIN, E_SLIDE_MENU_FAVORITE )
				#LOG_TRACE( 'pos main[%s] sub[%s]'% (self.mUserSlidePos.mMain, self.mUserSlidePos.mSub ) )

		elif aContextAction == CONTEXT_ACTION_MENU_EDIT_MODE :
			isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )
			if isRunRec > 0 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Try again after stopping all your recordings first' ) )
	 			dialog.doModal( )

	 		else :
				self.GoToEditWindow( )

			return

		elif aContextAction == CONTEXT_ACTION_MENU_DELETEALL :
			isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )
			isNotAvail = 0
			aTitle = ''
			lblLine = ''
			if isRunRec > 0 :
				isNotAvail = 1
				aTitle = MR_LANG( 'Attention' )
				lblLine = MR_LANG( 'Try again after stopping all your recordings first' )

			elif self.mFlag_DeleteAll or not self.mChannelList or len( self.mChannelList ) < 1:
				isNotAvail = 1
				aTitle = MR_LANG( 'Error' )
				lblLine = MR_LANG( 'Your channel list is empty' )

			if isNotAvail :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( aTitle, lblLine )
	 			dialog.doModal( )

	 		else :
				ret = self.DoDeleteAll( )

				if ret == E_DIALOG_STATE_YES :
					self.mChannelList = None
					self.mNavEpg = None
					self.mNavChannel = None
					self.LoadChannelListHash( )
					self.ReloadChannelList( )
					#clear label
					self.ResetLabel( )
					self.UpdateChannelAndEPG( )
			return

		LOG_TRACE( 'contextAction ret[%s]'% ret )

		self.mMarkList = []
		self.mListItems = None
		self.SubMenuAction( E_SLIDE_ACTION_SUB )
		#recovery last focus
		self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, lastPos, E_TAG_SET_SELECT_POSITION )
		#self.UpdateControlGUI( E_CONTROL_FOCUSED, E_CONTROL_ID_GROUP_CHANNEL_LIST )


	def ShowEditContextMenu( self, aMode, aMove = None ) :
		#try:
		if self.mMoveFlag :
			self.SetMoveMode( FLAG_OPT_MOVE_OK )
			return

		self.LoadFavoriteGroupList( )
		LOG_TRACE( 'favList ori[%s] edit[%s]'% (self.mListFavorite, self.mFavoriteGroupList))

		#default context item
		context = []
		if self.mChannelList and len( self.mChannelList ) > 0 :
			context.append( ContextItem( MR_LANG( 'Lock' ),   CONTEXT_ACTION_LOCK ) )
			context.append( ContextItem( MR_LANG( 'Unlock' ), CONTEXT_ACTION_UNLOCK ) )
			context.append( ContextItem( MR_LANG( 'Skip' ),   CONTEXT_ACTION_SKIP ) )
			context.append( ContextItem( MR_LANG( 'Unskip' ), CONTEXT_ACTION_UNSKIP  ) )


		if aMode == FLAG_OPT_LIST :
			if self.mChannelList and len( self.mChannelList ) > 0 :
				context.append( ContextItem( MR_LANG( 'Delete' ), CONTEXT_ACTION_DELETE ) )
				context.append( ContextItem( MR_LANG( 'Move' ),   CONTEXT_ACTION_MOVE ) )

				if self.mFavoriteGroupList :
					context.append( ContextItem( '%s'% MR_LANG( 'Add to favorite group' ), CONTEXT_ACTION_ADD_TO_FAV  ) )
					context.append( ContextItem( '%s'% MR_LANG( 'Create favorite group' ), CONTEXT_ACTION_CREATE_GROUP_FAV  ) )
					context.append( ContextItem( '%s'% MR_LANG( 'Rename favorite group' ), CONTEXT_ACTION_RENAME_FAV ) )
					context.append( ContextItem( '%s'% MR_LANG( 'Delete favorite group' ), CONTEXT_ACTION_DELETE_FAV ) )
				else:
					context.append( ContextItem( '%s'% MR_LANG( 'Create favorite group' ), CONTEXT_ACTION_CREATE_GROUP_FAV  ) )

			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Your channel list is empty' ) )
				dialog.doModal( )
				return


		elif aMode == FLAG_OPT_GROUP :
			if self.mChannelList and len( self.mChannelList ) > 0 :
				context.append( ContextItem( MR_LANG( 'Delete' ), CONTEXT_ACTION_DELETE ) )
				context.append( ContextItem( MR_LANG( 'Move' ),   CONTEXT_ACTION_MOVE ) )
			else :
				context = []

			context.append( ContextItem( '%s'% MR_LANG( 'Add to this favorite group' ), CONTEXT_ACTION_ADD_TO_CHANNEL ) )
			if not self.mChannelList :
				context.append( ContextItem( MR_LANG( 'Remove from this group' ), CONTEXT_ACTION_DELETE ) )	
			context.append( ContextItem( '%s'% MR_LANG( 'Rename favorite group' ), CONTEXT_ACTION_RENAME_FAV ) )

		context.append( ContextItem( '%s'% MR_LANG( 'Save and exit' ), CONTEXT_ACTION_SAVE_EXIT ) )


		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
 		dialog.doModal( )

		selectedAction = dialog.GetSelectedAction( )
		if selectedAction == -1 :
			#LOG_TRACE( 'CANCEL by context dialog' )
			return

		if ( (not self.mFavoriteGroupList) and (selectedAction == CONTEXT_ACTION_ADD_TO_CHANNEL) ) or \
		   ( (not self.mFavoriteGroupList) and (selectedAction == CONTEXT_ACTION_ADD_TO_FAV) ) or \
		   ( (not self.mFavoriteGroupList) and (selectedAction == CONTEXT_ACTION_RENAME_FAV) ) or \
		   ( (not self.mFavoriteGroupList) and (selectedAction == CONTEXT_ACTION_DELETE_FAV) ) :
			return

		if selectedAction == CONTEXT_ACTION_SAVE_EXIT :
			self.GoToPreviousWindow( )
			return

		#--------------------------------------------------------------- dialog 2
		grpIdx = -1
		groupName = None

		if selectedAction == CONTEXT_ACTION_ADD_TO_CHANNEL :
			channelList = self.AddFavoriteChannels( )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SELECT )
			dialog.SetDefaultProperty( MR_LANG( 'Select channels you want to add to this group' ), channelList, E_MODE_CHANNEL_LIST )
			dialog.doModal( )
			groupName = self.mFavoriteGroupList[self.mUserSlidePos.mSub]
			self.mMarkList = dialog.GetSelectedList( )
			#LOG_TRACE('-------add group[%s]-----dialog list[%s]'% ( groupName, self.mMarkList ) )

			if self.mMarkList == None or len( self.mMarkList ) < 1 :
				LOG_TRACE( 'Cancelled by context dialog' )
				return


		# add Fav, Ren Fav, Del Fav ==> popup select group
		if selectedAction == CONTEXT_ACTION_ADD_TO_FAV or \
		   selectedAction == CONTEXT_ACTION_RENAME_FAV or \
		   selectedAction == CONTEXT_ACTION_DELETE_FAV :
 			title = ''
 			if selectedAction == CONTEXT_ACTION_ADD_TO_FAV :   title = MR_LANG( 'Select a fav group you want to add channels to' )
 			elif selectedAction == CONTEXT_ACTION_RENAME_FAV : title = MR_LANG( 'Select a fav group you want to rename' )
 			elif selectedAction == CONTEXT_ACTION_DELETE_FAV : title = MR_LANG( 'Select a fav group you want to remove' )

 			grpIdx = xbmcgui.Dialog( ).select( title, self.mFavoriteGroupList )
 			groupName = self.mFavoriteGroupList[grpIdx]
 			#LOG_TRACE( '---------------grpIdx[%s] fav[%s]'% (grpIdx,groupName) )

			if grpIdx == -1 :
				#LOG_TRACE( 'CANCEL by context dialog' )
				return

			if selectedAction == CONTEXT_ACTION_DELETE_FAV :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( MR_LANG( 'Delete favorite group' ), MR_LANG( 'Are you sure you want to remove\n%s?' ) % groupName )
				dialog.doModal( )

				answer = dialog.IsOK( )

				#answer is yes
				if answer != E_DIALOG_STATE_YES :
					return

			grpIdx = selectedAction

		# Ren Fav, Del Fav ==> popup input group Name
		if selectedAction == CONTEXT_ACTION_CREATE_GROUP_FAV or \
		   selectedAction == CONTEXT_ACTION_RENAME_FAV :
			label = ''
			default = ''
			if selectedAction == CONTEXT_ACTION_CREATE_GROUP_FAV :
				#create
				result = ''
				label = MR_LANG( 'Enter name for new favorite group' )

			elif selectedAction == CONTEXT_ACTION_RENAME_FAV :
				#rename
				default = groupName
				result = '%d'%grpIdx + ':' + groupName + ':'
				label = MR_LANG( 'Enter new name for this favorite group' )

			kb = xbmc.Keyboard( default, label, False )
			kb.doModal( )

			name = ''
			name = kb.getText( )
			if name :
				if selectedAction == CONTEXT_ACTION_RENAME_FAV and groupName == name :
					LOG_TRACE( 'can not fav.rename : same name' )
					return

				groupName = result + name

			else :
				LOG_TRACE('no favName or cencel')
				return

		#LOG_TRACE( 'mode[%s] btn[%s] groupName[%s]'% (aMode, selectedAction, groupName) )
		#--------------------------------------------------------------- context end

		if selectedAction == CONTEXT_ACTION_ADD_TO_CHANNEL :
			self.AddFavoriteChannels( channelList, groupName )
		else :
			self.DoContextAction( aMode, selectedAction, groupName )

		self.mIsSave |= FLAG_MASK_ADD

		if selectedAction == CONTEXT_ACTION_CREATE_GROUP_FAV or \
			selectedAction == CONTEXT_ACTION_RENAME_FAV or \
			selectedAction == CONTEXT_ACTION_DELETE_FAV :

			self.LoadFavoriteGroupList( )
			#self.UpdateControlListSelectItem( self.mCtrlListMainmenu, E_SLIDE_MENU_FAVORITE )
			if self.mUserSlidePos.mMain == E_SLIDE_MENU_FAVORITE :
				self.SubMenuAction( E_SLIDE_ACTION_MAIN, E_SLIDE_MENU_FAVORITE, True )
			#else :
			#	self.RefreshSlideMenu( self.mUserSlidePos.mMain, self.mUserSlidePos.mSub, True )


	def ShowContextMenu( self ) :
		mode = FLAG_OPT_LIST
		if self.mUserMode.mMode == ElisEnum.E_MODE_FAVORITE :
			mode = FLAG_OPT_GROUP

		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			context = []
			context.append( ContextItem( MR_LANG( 'Edit channels' ), CONTEXT_ACTION_MENU_EDIT_MODE ) )
			context.append( ContextItem( MR_LANG( 'Delete all channels' ), CONTEXT_ACTION_MENU_DELETEALL ) )

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context )
	 		dialog.doModal( )

			selectedAction = dialog.GetSelectedAction( )
			if selectedAction == -1 :
				#LOG_TRACE( 'CANCEL by context dialog' )
				return

			self.DoContextAction( mode, selectedAction )

		else :
			self.ShowEditContextMenu( mode )


	def Close( self ):
		self.mEventBus.Deregister( self )
		if self.mEnableProgressThread == True and self.mPlayProgressThread :
			self.mEnableProgressThread = False				
			self.mPlayProgressThread.join( )

		self.StopAsyncEPG( )
		self.SetVideoRestore( )
		#WinMgr.GetInstance( ).CloseWindow( )


	def RestartAsyncEPG( self ) :
		self.StopAsyncEPG( )
		self.StartAsyncEPG( )


	def StartAsyncEPG( self ) :
		self.mAsyncTuneTimer = threading.Timer( 0.5, self.AsyncUpdateCurrentEPG ) 				
		self.mAsyncTuneTimer.start( )


	def StopAsyncEPG( self ) :
		if self.mAsyncTuneTimer	and self.mAsyncTuneTimer.isAlive( ) :
			self.mAsyncTuneTimer.cancel( )
			del self.mAsyncTuneTimer

		self.mAsyncTuneTimer  = None


	def AsyncUpdateCurrentEPG( self ) :
		try :
			self.mIsTune = False
			self.ResetLabel( )
			self.Epgevent_GetCurrent( )
			self.UpdateChannelAndEPG( )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )



	def TuneByNumber( self, aKey ) :
		if self.mChannelList == None :
			return -1

		if aKey == 0 :
			return -1

		if self.mViewMode != WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			return -1

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_JUMP )
		dialog.SetDialogProperty( str( aKey ), self.mChannelListHash, True )
		dialog.doModal( )

		isOK = dialog.IsOK( )
		if isOK == E_DIALOG_STATE_YES :
			inputNumber = dialog.GetChannelLast( )
			#LOG_TRACE( 'Jump chNum[%s] currentCh[%s]'% (inputNumber,self.mCurrentChannel) )

			if int( self.mCurrentChannel ) == int( inputNumber ) :
				ch = None
				ch = self.mDataCache.Channel_GetCurrent( )
				LOG_TRACE( 'aJump num[%s] name[%s] current[%s]'% ( ch.mNumber, ch.mName, self.mCurrentChannel ) )
				if ch :
					self.mNavChannel = ch
					#self.mCurrentChannel = self.mNavChannel.mNumber
					pos = self.mCurrentPosition
					self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, pos, E_TAG_SET_SELECT_POSITION )
					#time.sleep( 0.02 )

					self.UpdateControlGUI( E_CONTROL_ID_LABEL_SELECT_NUMBER, str( '%s'% (int( pos ) + 1 ) ) )
					self.ResetLabel( )
					self.UpdateChannelAndEPG( )

			else :
				self.TuneChannel( int(inputNumber) )


	def ShowRecordingStartDialog( self ) :
		isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )

		if HasAvailableRecordingHDD( ) == False :
			return

		isChangeDuration = False
		if self.mRecordInfo1 or self.mRecordInfo2 :
			pos = self.mCurrentPosition
			if self.mCtrlListCHList.getListItem( pos ).getProperty( E_XML_PROPERTY_RECORDING ) == E_TAG_TRUE :
				isChangeDuration = True

		isOK = False
		if isRunRec < 2 or isChangeDuration :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
			dialog.doModal( )

			isOK = dialog.IsOK( )
			if isOK == E_DIALOG_STATE_YES :
				isOK = True

			if dialog.IsOK( ) == E_DIALOG_STATE_ERROR and dialog.GetConflictTimer( ) :
				RecordConflict( dialog.GetConflictTimer( ) )

		else:
			msg = MR_LANG( 'You have reached the maximum number of\nrecordings allowed' )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), msg )
			dialog.doModal( )	

		if isOK :
			self.mDataCache.SetChannelReloadStatus( True )


	def ShowRecordingStopDialog( self ) :
		isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )

		isOK = False
		if isRunRec > 0 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_STOP_RECORD )
			dialog.doModal( )

			isOK = dialog.IsOK( )
			if isOK == E_DIALOG_STATE_YES :
				isOK = True

		if isOK == True :
			self.mDataCache.SetChannelReloadStatus( True )


	def LoadRecordingInfo( self ) :
		self.mRecordInfo1 = None
		self.mRecordInfo2 = None

		try:
			self.mRecCount = self.mDataCache.Record_GetRunningRecorderCount( )
			#LOG_TRACE( 'isRunRecCount[%s]'% isRunRec)

			if self.mRecCount == 1 :
				self.mRecordInfo1 = self.mDataCache.Record_GetRunningRecordInfo( 0 )

			elif self.mRecCount == 2 :
				self.mRecordInfo1 = self.mDataCache.Record_GetRunningRecordInfo( 0 )
				self.mRecordInfo2 = self.mDataCache.Record_GetRunningRecordInfo( 1 )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def UpdateRecordInfo( self, aOldRecInfo1, aOldRecInfo2 ) :
		try :
			iChannel = None

			if aOldRecInfo1 :
				iChannel = self.mDataCache.Channel_GetByOne( aOldRecInfo1.mServiceId )
				LOG_TRACE('num[%s] name[%s]'% (iChannel.mNumber, iChannel.mName) )
				if iChannel : 
					pos = int( iChannel.mNumber ) - 1
					self.mCtrlListCHList.getListItem( pos ).setProperty( E_XML_PROPERTY_RECORDING, E_TAG_FALSE )

			if aOldRecInfo2 :
				iChannel = self.mDataCache.Channel_GetByOne( aOldRecInfo2.mServiceId )
				if iChannel : 
					pos = int( iChannel.mNumber ) - 1
					self.mCtrlListCHList.getListItem( pos ).setProperty( E_XML_PROPERTY_RECORDING, E_TAG_FALSE )

			if self.mRecordInfo1  :
				iChannel = self.mDataCache.Channel_GetByOne( self.mRecordInfo1.mServiceId )
				if iChannel : 
					LOG_TRACE('num[%s] name[%s] lenList[%s]'% (iChannel.mNumber, iChannel.mName, len(self.mChannelList) ) )
					pos = int( iChannel.mNumber ) - 1
					self.mCtrlListCHList.getListItem( pos ).setProperty( E_XML_PROPERTY_RECORDING, E_TAG_TRUE )

			if self.mRecordInfo2 :
				iChannel = self.mDataCache.Channel_GetByOne( self.mRecordInfo2.mServiceId )
				if iChannel : 
					pos = int( iChannel.mNumber ) - 1
					self.mCtrlListCHList.getListItem( pos ).setProperty( E_XML_PROPERTY_RECORDING, E_TAG_TRUE )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def ReloadChannelList( self, aInit = FLAG_SLIDE_OPEN ) :
		self.mListItems = None
		self.mCtrlListCHList.reset( )
		self.InitSlideMenuHeader( aInit )
		mainIdx = self.mUserSlidePos.mMain
		subIdx  = self.mUserSlidePos.mSub
		self.RefreshSlideMenu( mainIdx, subIdx, True )
		self.UpdateControlGUI( E_SLIDE_CLOSE )


