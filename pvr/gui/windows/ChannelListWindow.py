from pvr.gui.WindowImport import *

E_CHANNEL_LIST_BASE_ID					=  WinMgr.WIN_ID_CHANNEL_LIST_WINDOW * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 

#xml control id
E_CONTROL_ID_LABEL_CHANNEL_PATH			= E_CHANNEL_LIST_BASE_ID + 21
E_CONTROL_ID_LABEL_CHANNEL_SORT			= E_CHANNEL_LIST_BASE_ID + 22
E_CONTROL_ID_SCROLLBAR_CHANNEL			= E_CHANNEL_LIST_BASE_ID + 61
E_CONTROL_ID_SCROLLBAR_SUBMENU			= E_CHANNEL_LIST_BASE_ID + 503
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

#misc option
E_CONTROL_ID_BUTTON_SEARCH				= E_CHANNEL_LIST_BASE_ID + 201
E_CONTROL_ID_RADIOBUTTON_AUTOCONFIRM	= E_CHANNEL_LIST_BASE_ID + 121
E_CONTROL_ID_RADIOBUTTON_SHOW_EPGINFO	= E_CHANNEL_LIST_BASE_ID + 122
E_CONTROL_ID_RADIOBUTTON_SEARCH_ALL		= E_CHANNEL_LIST_BASE_ID + 123

E_BUTTON_ID_FAKE_ALLCHANNELS			= E_CHANNEL_LIST_BASE_ID + 700

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
FLAG_CLOCKMODE_ADMYHM = 1
FLAG_CLOCKMODE_AHM    = 2
FLAG_CLOCKMODE_HMS    = 3
FLAG_CLOCKMODE_HHMM   = 4
FLAG_MODE_JUMP     = True
FLAG_USE_COLOR_KEY = True

#slide index
E_SLIDE_ACTION_MAIN     = 0
E_SLIDE_ACTION_SUB      = 1
E_SLIDE_ACTION_SORT     = 99
E_SLIDE_MENU_ALLCHANNEL = 0
E_SLIDE_MENU_SATELLITE  = 1
E_SLIDE_MENU_FTACAS     = 2
E_SLIDE_MENU_PROVIDER   = 3
E_SLIDE_MENU_FAVORITE   = 4
E_SLIDE_MENU_MODE       = 5

E_CONTROL_FOCUSED       = E_CHANNEL_LIST_BASE_ID + 9991
E_SLIDE_CLOSE           = E_CHANNEL_LIST_BASE_ID + 9999

E_CHANNEL_LIST_DEFAULT_FOCUS_ID	=  E_CONTROL_ID_GROUP_CHANNEL_LIST


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
		self.mListProvider  = []
		self.mTempGroupSubmenu  = []
		self.mListShortCutGroup = []
		self.mLoadMode = None
		self.mLoadSlidePos = SlidePosition( )
		self.mCurrentPosition = 0
		self.mListItems = None
		self.mPlayProgressThread = None
		self.mEnableProgressThread = False

		self.mEventId = 0
		self.mLocalTime = 0
		self.mAsyncTuneTimer = None

		self.mAgeLimit = 0
		self.mViewMode = WinMgr.WIN_ID_CHANNEL_LIST_WINDOW
		self.mSetEditMode = False

		self.mEPGList = []
		self.mEPGHashTable = {}
		self.mOffsetTopIndex = 0
		self.mNavOffsetTopIndex = 0
		self.mLock = thread.allocate_lock( )

		self.mItemCount = 13
		self.mListHeight= 540


	def onInit(self):
		self.SetSingleWindowPosition( E_CHANNEL_LIST_BASE_ID )

		self.SetFrontdisplayMessage( MR_LANG('Channel List') )
		self.SetHeaderTitle( MR_LANG( 'Channel List' ) )
		
		self.mWinId = xbmcgui.getCurrentWindowId( )
		LOG_TRACE( '[ChannelList] winID[%d]'% self.mWinId)

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
		self.mCtrlLabelSelectItem        = self.getControl( E_CONTROL_ID_LABEL_SELECT_NUMBER )
		#self.mCtrlGroupHelpBox           = self.getControl( E_CONTROL_ID_GROUP_HELPBOX )
		#self.mCtrlLabelMiniTitle         = self.getControl( E_SETTING_MINI_TITLE )

		#misc option
		self.mCtrlButtonSearch           = self.getControl( E_CONTROL_ID_BUTTON_SEARCH )
		self.mCtrlRadioButtonAutoConfirm = self.getControl( E_CONTROL_ID_RADIOBUTTON_AUTOCONFIRM )
		self.mCtrlRadioButtonShowEPGInfo = self.getControl( E_CONTROL_ID_RADIOBUTTON_SHOW_EPGINFO )
		#self.mCtrlRadioButtonSearchAll   = self.getControl( E_CONTROL_ID_RADIOBUTTON_SEARCH_ALL )

		#ch list
		self.mCtrlGroupCHList            = self.getControl( E_CONTROL_ID_GROUP_CHANNEL_LIST )
		self.mCtrlListCHList             = self.getControl( E_CONTROL_ID_LIST_CHANNEL_LIST )

		#self.mCtrlListCHList.reset( )
		isUpdatePosition = self.InitCurrentPosition( )

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
		self.mChannelListHashIDs = {}
		self.mChannelListForMove = []
		self.mRecCount = 0
		self.mRecordInfo1 = None
		self.mRecordInfo2 = None
		self.mNavEpg = None
		self.mNavChannel = None
		self.mCurrentChannel = None
		self.mFlag_EditChanged = False
		self.mFlag_ModeChanged = False
		self.mFlag_DeleteAll = False
		self.mFlag_DeleteAll_Fav = False
		self.mTimerListHash = {}
		self.mLastChannel = None
		self.mLastChannelList = []
		self.mLastChannelListHash = {}
		self.mTPListByChannelHash = {}
		self.mZappingChange = False
		self.mMaxChannelNum = E_INPUT_MAX
		self.mSearchList = []
		self.mSearchKeyword = ''
		self.mAutoConfirm = False
		self.mShowEPGInfo = False
		self.mEPGHashTable = {}

		#edit mode
		self.mIsSave = FLAG_MASK_NONE
		self.mMarkList = []
		self.mFavoriteGroupList = []
		self.mMoveFlag = False
		self.mMoveItem = []
		self.mIsPVR = False
		self.mSetMarkCount = 0
		self.mRestoreTuneChannel = self.mDataCache.Channel_GetCurrent( )

		self.mEventBus.Register( self )
		self.SetPipScreen( )

		self.mItemHeight = int( self.getProperty( 'ItemHeight' ) )
		self.mAgeLimit = self.mDataCache.GetPropertyAge( )

		if self.mDataCache.GetChannelReloadStatus( ) :
			isUpdatePosition = True
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
		self.Initialize( isUpdatePosition )

		#run thread
		self.mEnableProgressThread = True
		self.mPlayProgressThread = self.EPGProgressThread( )

		self.mAsyncTuneTimer = None
		self.mAsyncSortTimer = None

		self.setFocusId( E_CHANNEL_LIST_DEFAULT_FOCUS_ID )
		#endtime = time.time( )
		#print '==================== TEST TIME[ONINIT] END[%s] loading[%s]'% (endtime, endtime-starttime )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 :
			self.TuneByNumber( int( actionId ) - Action.REMOTE_0 )

		elif actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :
			rKey = actionId - ( Action.ACTION_JUMP_SMS2 - 2 )
			self.TuneByNumber( rKey )

		elif actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			#LOG_TRACE( '[ChannelList] goto previous menu' )
			self.GetFocusId( )
			if self.mFocusId != E_CONTROL_ID_LIST_CHANNEL_LIST and self.mFocusId != E_CONTROL_ID_SCROLLBAR_CHANNEL :
				self.UpdateControlGUI( E_SLIDE_CLOSE )
				return

			if self.mMoveFlag :
				#self.SetMoveMode( FLAG_OPT_MOVE_OK, actionId )
				self.SetMoveMode( FLAG_OPT_MOVE_EXIT, actionId )
			else :
				self.GoToPreviousWindow( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			return

			#deprecated, no use select action
			self.GetFocusId( )
			#LOG_TRACE( '[ChannelList] item select, action ID[%s]'% actionId )
			if self.mFocusId == E_CONTROL_ID_LIST_MAINMENU :
				position = self.mCtrlListMainmenu.getSelectedPosition( )
				if position == E_SLIDE_MENU_ALLCHANNEL :
					self.SubMenuAction( E_SLIDE_ACTION_SUB )
					self.UpdateControlGUI( E_SLIDE_CLOSE )

				else :
					self.SubMenuAction( E_SLIDE_ACTION_MAIN, position )

		elif actionId == Action.ACTION_MBOX_FF :
			self.UpdateShortCutGroup( 1 )

		elif actionId == Action.ACTION_MBOX_REWIND :
			self.UpdateShortCutGroup( -1 )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.GetFocusId( )
			if self.mMoveFlag :
				self.setFocusId( E_CONTROL_ID_LIST_CHANNEL_LIST )
				return
			
			if self.mFocusId == E_CONTROL_ID_LIST_MAINMENU :
				position = self.mCtrlListMainmenu.getSelectedPosition( )
				if position == E_SLIDE_MENU_ALLCHANNEL :
					self.UpdateControlGUI( E_SLIDE_CLOSE )

			elif self.mFocusId == E_CONTROL_ID_BUTTON_MAINMENU :
				self.UpdateControlGUI( E_CONTROL_FOCUSED, E_CONTROL_ID_LIST_MAINMENU )
				self.SetSlideMenuHeader( FLAG_SLIDE_OPEN )

			elif self.mFocusId == E_CONTROL_ID_LIST_CHANNEL_LIST or self.mFocusId == 49 :
				position = self.mCtrlListMainmenu.getSelectedPosition( )
				if position == E_SLIDE_MENU_MODE :
					self.mCtrlListMainmenu.selectItem( self.mUserSlidePos.mMain )
					self.mCtrlListSubmenu.selectItem( self.mUserSlidePos.mSub )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.GetFocusId( )
			if self.mMoveFlag :
				self.setFocusId( E_CONTROL_ID_LIST_CHANNEL_LIST )
				return

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

			elif self.mFocusId == E_CONTROL_ID_BUTTON_SORTING :
				mSort = self.mUserMode.mSortingMode
				if self.mUserMode.mMode == ElisEnum.E_MODE_FAVORITE :
					mSort = ElisEnum.E_SORT_BY_NUMBER
					LOG_TRACE( '[ChannelList] fixed sort by number in Favorite Group' )

				lblSort = EnumToString( 'sort', mSort )
				lblButtonSort = '%s : %s'% ( MR_LANG( 'Sort' ), lblSort )
				self.UpdateControlGUI( E_CONTROL_ID_BUTTON_SORTING, lblButtonSort )

		elif actionId == Action.ACTION_CONTEXT_MENU :
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_SCROLLBAR_CHANNEL or self.mFocusId == E_CONTROL_ID_SCROLLBAR_SUBMENU :
				return

			self.ShowContextMenu( )

		elif actionId == Action.ACTION_STOP :
			if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :

				status = self.mDataCache.Player_GetStatus( )
				if status.mMode :
					ret = self.mDataCache.Player_Stop( )

					iChannel = self.mDataCache.Channel_GetCurrent( )
					if iChannel :
						self.mNavChannel = iChannel
						self.mCurrentChannel = iChannel.mNumber

					self.mIsTune == True
					self.UpdateChannelAndEPG( )
				else :
					self.ShowRecordingStopDialog( )

		elif actionId == Action.ACTION_MBOX_ARCHIVE :
			if not HasAvailableRecordingHDD( ) :
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
				isAvail, isConfiguration = self.HasDefaultRecordPath( False )
				if isAvail != E_DEFAULT_RECORD_PATH_RESERVED :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'No recording path' ), MR_LANG( 'Please check your recording path setting' ) )
					dialog.doModal( )
					return

				if self.mChannelList or len( self.mChannelList ) > 0 :
					self.ShowRecordingStartDialog( )

		elif actionId == Action.ACTION_MBOX_TVRADIO :
			if self.mUserMode.mServiceType == FLAG_MODE_TV :
				self.DoModeChange( FLAG_MODE_RADIO )
			else :
				self.DoModeChange( FLAG_MODE_TV )

		elif actionId == Action.ACTION_COLOR_RED :
			self.UpdateShortCutZapping( E_SLIDE_MENU_SATELLITE )

		elif actionId == Action.ACTION_COLOR_GREEN :
			self.UpdateShortCutZapping( E_SLIDE_MENU_FTACAS )

		elif actionId == Action.ACTION_COLOR_YELLOW :
			self.UpdateShortCutZapping( E_SLIDE_MENU_PROVIDER )

		elif actionId == Action.ACTION_COLOR_BLUE :
			self.UpdateShortCutZapping( E_SLIDE_MENU_FAVORITE )


	def onClick(self, aControlId):
		if aControlId == E_CONTROL_ID_LIST_CHANNEL_LIST :
			if self.mViewMode == WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW :
				try:
					if self.mMoveFlag :
						self.SetMoveMode( FLAG_OPT_MOVE_OK )
						return

					#selection mode
					if self.mIsMark == True :
						if self.mChannelList :
							idx = self.mCtrlListCHList.getSelectedPosition( )
							self.SetMark( idx )
							#LOG_TRACE( '[ChannelList] select idx[%s]'% self.mMarkList )
							self.UpdateControlGUI( E_CONTROL_FOCUSED, E_CONTROL_ID_GROUP_CHANNEL_LIST )
							self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, idx+1, E_TAG_SET_SELECT_POSITION )
							self.UpdateControlGUI( E_CONTROL_ID_LABEL_SELECT_NUMBER, str( '%s'% (idx+1) ) )

				except Exception, e:
					LOG_ERR( '[ChannelList] except[%s]'% e )

			else :
				if self.mChannelList :
					self.TuneChannel( )


		elif aControlId == E_CONTROL_ID_BUTTON_SORTING :
			if self.mUserMode.mMode == ElisEnum.E_MODE_FAVORITE :
				LOG_TRACE( '[ChannelList] can not sort in Favorite Group' )

				lblSort = EnumToString( 'sort', ElisEnum.E_SORT_BY_NUMBER )
				label = '%s : %s'% ( MR_LANG( 'Sort' ), lblSort )
				self.UpdateControlGUI( E_CONTROL_ID_BUTTON_SORTING, label )
				return

			self.UpdateSort( )


		elif aControlId == E_CONTROL_ID_BUTTON_MAINMENU or aControlId == E_CONTROL_ID_LIST_MAINMENU :
			#slide main view
			LOG_TRACE('[ChannelList] hidden button[%s]'% aControlId )
			pass

		elif aControlId == E_CONTROL_ID_LIST_MAINMENU :
			position = self.mCtrlListMainmenu.getSelectedPosition( )
			#LOG_TRACE('[ChannelList] main idx[%s]'% position )
			if position == E_SLIDE_MENU_ALLCHANNEL :
				LOG_TRACE('[ChannelList] click AllChannel' )
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

		elif aControlId == E_BUTTON_ID_FAKE_ALLCHANNELS :
			self.SubMenuAction( E_SLIDE_ACTION_SUB )
			self.UpdateControlGUI( E_SLIDE_CLOSE )

		elif aControlId == E_CONTROL_ID_BUTTON_SEARCH :
			self.UpdateControlGUI( E_SLIDE_CLOSE )
			self.mCtrlListMainmenu.selectItem( self.mUserSlidePos.mMain )
			self.mCtrlListSubmenu.selectItem( self.mUserSlidePos.mSub )
			self.ShowSearchDialog( )

		elif aControlId == E_CONTROL_ID_RADIOBUTTON_AUTOCONFIRM :
			self.mAutoConfirm = self.mCtrlRadioButtonAutoConfirm.isSelected( )
			#LOG_TRACE( '--------------------------autoConfirm[%s]'% self.mAutoConfirm )
			SetSetting( 'AUTO_CONFIRM_CHANNEL', '%s'% int( self.mAutoConfirm ) )

		elif aControlId == E_CONTROL_ID_RADIOBUTTON_SHOW_EPGINFO :
			self.mShowEPGInfo = self.mCtrlRadioButtonShowEPGInfo.isSelected( )
			showEPGInfo = False
			if self.mShowEPGInfo :
				showEPGInfo = True
				self.LoadByCurrentEPG( )

			self.UpdatePropertyGUI( 'ShowExtendInfo', '%s'% showEPGInfo )
			self.UpdateChannelNameWithEPG( True, True )
			self.UpdateControlGUI( E_SLIDE_CLOSE )
			SetSetting( 'SHOW_EPGINFO_CHANNEL', '%s'% int( self.mShowEPGInfo ) )


	def onFocus(self, controlId):
		pass


	def SetEditMode( self, aMode = False ) :
		self.mSetEditMode = aMode


	def InitCurrentPosition( self ) :
		isFail = True
		if not self.mInitialized :
			LOG_TRACE( '[ChannelList] passed, not selected position by first load' )
			return isFail

		try :
			iChannel = self.mDataCache.Channel_GetCurrent( )
			if iChannel :
				chIndex = self.GetChannelByIDs( iChannel.mNumber, iChannel.mSid, iChannel.mTsid, iChannel.mOnid, True )
				#if self.mChannelList and len( self.mChannelList ) > chIndex and self.mCtrlListCHList.getSelectedPosition( ) != chIndex :
				if chIndex > -1 and self.mChannelList and len( self.mChannelList ) > chIndex :
					#self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, chIndex, E_TAG_SET_SELECT_POSITION )
					self.mCtrlListCHList.selectItem( chIndex )
					LOG_TRACE( '[ChannelList] sync position[%s] to current channel[%s %s]'% ( chIndex, iChannel.mNumber, iChannel.mName ) )

					label = '%s - %s'% ( EnumToString( 'type', iChannel.mServiceType ), iChannel.mName )
					if not self.mChannelList or len( self.mChannelList ) < 1 :
						label = MR_LANG( 'No Channel' )

					self.mNavChannel = iChannel
					self.UpdateChannelAndEPG( )
					self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, label )
					isFail = False

		except Exception, e :
			LOG_ERR( '[ChannelList] except[%s]'% e )

		return isFail


	def LoadChannelListHash( self ) :
		self.mChannelListHash = {}
		self.mChannelListHashIDs = {}
		self.mChannelListForMove = []
		self.mTPListByChannelHash = {}
		self.mMaxChannelNum = E_INPUT_MAX

		if self.mChannelList and len( self.mChannelList ) > 0 :
			idxCount = 0
			for iChannel in self.mChannelList :
				chNumber = iChannel.mNumber
				self.mChannelListHash[chNumber] = iChannel
				self.mChannelListForMove.append( chNumber )

				channelKey = '%d:%d:%d:%d'% ( iChannel.mNumber, iChannel.mSid, iChannel.mTsid, iChannel.mOnid )
				self.mChannelListHashIDs[channelKey] = [iChannel, idxCount]

				self.mTPListByChannelHash[iChannel.mNumber] = self.mDataCache.GetTunerIndexBySatellite( iChannel.mCarrier.mDVBS.mSatelliteLongitude, iChannel.mCarrier.mDVBS.mSatelliteBand )
				#LOG_TRACE( '[ChannelList] ch[%s %s] tpNum[%s]'% ( iChannel.mNumber, iChannel.mName, self.mTPListByChannelHash.get( iChannel.mNumber, None ) ) )

				if E_V1_2_APPLY_PRESENTATION_NUMBER :
					chNumber = self.mDataCache.CheckPresentationNumber( iChannel, self.mUserMode )

				if chNumber > self.mMaxChannelNum :
					self.mMaxChannelNum = chNumber

				idxCount += 1
		LOG_TRACE( '[ChannelList] load channel hash len[%s] maxNum[%s]'% ( len( self.mChannelListHash ), self.mMaxChannelNum ) )

		self.mTimerListHash = {}
		timerList = self.mDataCache.Timer_GetTimerList( )
		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW :
			timerList = self.mDataCache.GetTimerList( )

		if timerList and len( timerList ) > 0 :
			for timer in timerList :
				timerKey = '%d:%d:%d:%d'% ( timer.mChannelNo, timer.mSid, timer.mTsid, timer.mOnid )
				self.mTimerListHash[timerKey] = timer
				#LOG_TRACE( '[ChannelList] timerKey[%s] tch[%s] tName[%s]'% ( timerKey, timer.mChannelNo, timer.mName ) )

		LOG_TRACE( '[ChannelList] timer hash len[%s]'% len( self.mTimerListHash ) )


	def LoadByCurrentEPG( self, aUpdateAll = False ) :
		if not self.mShowEPGInfo or self.mViewMode == WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW :
			LOG_TRACE( '[ChannelList] passed, edit mode or not EPGInfo' )
			return

		isUpdate = True
		epgList = []
		startTime = time.time()

		if aUpdateAll :
			self.OpenBusyDialog( )
		#self.mLock.acquire( )

		try :
			if self.mChannelList and len( self.mChannelList ) > 0 :
				if aUpdateAll :
					self.mEPGHashTable = {}
					#epgList = self.mDataCache.Epgevent_GetCurrentListByEpgCF( self.mUserMode.mServiceType )
					epgList = self.mDataCache.Epgevent_GetShortListAll( self.mUserMode )
					#LOG_TRACE( '[ChannelList] aUpdateAll[%s] mode[%s] type[%s]'% ( aUpdateAll, self.mUserMode.mMode, self.mUserMode.mServiceType ) )

				else :
					numList = []
					#chNumbers = []
					self.mNavOffsetTopIndex = GetOffsetPosition( self.mCtrlListCHList )
					listCount = len( self.mChannelList )
					endCount = self.mNavOffsetTopIndex + self.mItemCount
					for offsetIdx in range( self.mNavOffsetTopIndex, endCount ) :
						if offsetIdx < listCount :
							chNum = ElisEInteger( )
							chNum.mParam = self.mChannelList[offsetIdx].mNumber
							numList.append( chNum )
							#chNumbers.append( self.mChannelList[offsetIdx].mNumber )

						else :
							#LOG_TRACE( '[ChannelList] limit over, mOffsetTopIndex[%s] offsetIdx[%s] chlen[%s]'% ( self.mNavOffsetTopIndex, offsetIdx, listCount ) )
							break
					#LOG_TRACE( '[ChannelList] aUpdateAll[%s] mOffsetTopIndex[%s] mItemCount[%s] chlen[%s] numList[%s][%s]'% ( aUpdateAll, self.mOffsetTopIndex, self.mItemCount, listCount, len( numList ), chNumbers ) )

					if numList and len( numList ) > 0 :
						epgList = self.mDataCache.Epgevent_GetShortList( self.mUserMode.mServiceType, numList )

		except Exception, e :
			isUpdate = False
			LOG_ERR( '[ChannelList] except[%s]'% e )

		if not epgList or len( epgList ) < 1 :
			isUpdate = False
			LOG_TRACE( '[ChannelList] get epglist None' )

		if isUpdate :
			for iEPG in epgList :
				self.mEPGHashTable[ '%d:%d:%d'% ( iEPG.mSid, iEPG.mTsid, iEPG.mOnid ) ] = iEPG
				#LOG_TRACE( 'epg [%s %s:%s:%s]'% ( iEPG.mChannelNo, iEPG.mSid, iEPG.mTsid, iEPG.mOnid ) )

			LOG_TRACE( '[ChannelList] epgList COUNT[%s]'% len( epgList ) )

		#self.mLock.release( )
		if aUpdateAll :
			self.CloseBusyDialog( )

		#print '[ChannelList] LoadByCurrentEPG-----testTime[%s]'% ( time.time() - startTime )

		self.UpdateChannelNameWithEPG( aUpdateAll )


	def GetTimerByIDs( self, aNumber, aSid, aTsid, aOnid ) :
		if not self.mTimerListHash or len( self.mTimerListHash ) < 1 :
			return None
		return self.mTimerListHash.get( '%d:%d:%d:%d' %( aNumber, aSid, aTsid, aOnid ), None )


	def GetChannelByIDs( self, aNumber, aSid, aTsid, aOnid, aReqIndex = False ) :
		if not self.mChannelListHashIDs or len( self.mChannelListHashIDs ) < 1 :
			retVal = None
			if aReqIndex :
				retVal = -1
			return retVal

		retValue = 0
		if aReqIndex :
			retValue = 1

		iChannels = self.mChannelListHashIDs.get( '%d:%d:%d:%d' %( aNumber, aSid, aTsid, aOnid ), None )
		if iChannels :
			iChannels = iChannels[retValue]

		if aReqIndex and iChannels == None :
			iChannels = -1 #none exist index

		return iChannels


	def GetEPGByIds( self, aSid, aTsid, aOnid ) :
		return self.mEPGHashTable.get( '%d:%d:%d' %( aSid, aTsid, aOnid ), None )


	def Initialize( self, aUpdatePosition = False ):
		self.mDataCache.LoadTimerList( )
		self.LoadRecordingInfo( )

		#cache load
		self.mChannelList = self.mDataCache.Channel_GetList( )
		self.LoadChannelListHash( )

		label = ''

		try :
			self.mAutoConfirm = int( GetSetting( 'AUTO_CONFIRM_CHANNEL' ) )
		except Exception, e :
			LOG_ERR( '[ChannelList] except[%s]'% e )
			self.mAutoConfirm = False
			SetSetting( 'AUTO_CONFIRM_CHANNEL', '0' )

		try :
			self.mShowEPGInfo = int( GetSetting( 'SHOW_EPGINFO_CHANNEL' ) )
		except Exception, e :
			LOG_ERR( '[ChannelList] except[%s]'% e )
			self.mShowEPGInfo = False
			SetSetting( 'SHOW_EPGINFO_CHANNEL', '0' )

		if not self.mInitialized :
			aUpdatePosition = True
			self.mInitialized = True
			self.mListHeight= self.mCtrlListCHList.getHeight( )
			self.mItemCount = self.mListHeight / self.mItemHeight
			#thread = threading.Timer( 0, self.LoadByCurrentEPG, [True] )
			#thread.start( )
		LOG_TRACE( '[ChannelList]updatePosition[%s]'% aUpdatePosition )

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
					label = '%s - P%04d.%s' %( MR_LANG( 'TIMESHIFT' ), iChannel.mNumber, iChannel.mName )

			elif status.mMode == ElisEnum.E_MODE_PVR :
				playingRecord = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW ).GetPlayingRecord( )
				if playingRecord and playingRecord.mError == 0 :
					self.mIsPVR = True
					label = '%s - P%04d.%s' %( MR_LANG( 'Playback' ), playingRecord.mChannelNo, playingRecord.mRecordName )

			else :
				#Live
				if iChannel :
					self.mNavChannel = iChannel
					self.mCurrentChannel = iChannel.mNumber

					label = '%s - %s'% ( EnumToString( 'type', iChannel.mServiceType ), iChannel.mName )
					if iChannel.mServiceType == ElisEnum.E_SERVICE_TYPE_INVALID :
						if not self.mChannelList or len( self.mChannelList ) < 1 :
							label = MR_LANG( 'No Channel' )

			self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, label )

		except Exception, e :
			LOG_ERR( '[ChannelList] except[%s]'% e )

		#clear label
		self.ResetLabel( )
		self.LoadByCurrentEPG( )

		startOnEdit = False
		if self.mSetEditMode :
			startOnEdit       = True
			self.mSetEditMode = False
			self.GoToEditWindow( )
		else :
			self.UpdateChannelList( aUpdatePosition )
			self.mOffsetTopIndex = GetOffsetPosition( self.mCtrlListCHList )
			self.mNavOffsetTopIndex = self.mOffsetTopIndex

		#init navChannel by focus
		self.mNavEpg = None
		self.mNavChannel = None
		if self.mListItems and self.mChannelList and len( self.mChannelList ) > 0 :
			focusIdx = self.mCtrlListCHList.getSelectedPosition( )
			if focusIdx < len( self.mChannelList ) :
				self.mNavChannel = self.mChannelList[focusIdx]
				self.mCurrentChannel = self.mNavChannel.mNumber
				#LOG_TRACE( '[ChannelList] focus len[%s] idx[%s] ch[%s %s]'% ( len( self.mChannelList ), focusIdx, self.mNavChannel.mNumber, self.mNavChannel.mName ) )

				#initialize get epg event
				try :
					#iEPG = self.mDataCache.Epgevent_GetPresent( )
					iEPG = self.mDataCache.GetEpgeventCurrent( )

					if iEPG and iEPG.mSid == self.mNavChannel.mSid and iEPG.mTsid == self.mNavChannel.mTsid and iEPG.mOnid == self.mNavChannel.mOnid :
						self.mNavEpg = iEPG
						self.mDataCache.Frontdisplay_SetIcon( ElisEnum.E_ICON_HD, iEPG.mHasHDVideo )

				except Exception, e :
					LOG_ERR( '[ChannelList] except[%s]'% e )

				#LOG_TRACE( '[ChannelList] epg[%s]'% self.mNavEpg )

		self.UpdateChannelAndEPG( )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, label )

		searchEnable = True
		if not self.mChannelList :
			searchEnable = False

		self.mCtrlButtonSearch.setEnabled( searchEnable )
		self.UpdateControlGUI( E_CONTROL_ID_RADIOBUTTON_AUTOCONFIRM, self.mAutoConfirm )
		self.UpdateControlGUI( E_CONTROL_ID_RADIOBUTTON_SHOW_EPGINFO, self.mShowEPGInfo )
		showEPGInfo = E_TAG_FALSE
		if self.mShowEPGInfo :
			showEPGInfo = E_TAG_TRUE
			self.UpdateChannelNameWithEPG( )

		if startOnEdit :
			showEPGInfo = E_TAG_FALSE
		self.UpdatePropertyGUI( 'ShowExtendInfo', showEPGInfo )


	def DoDeleteAll( self ) :
		ret = E_DIALOG_STATE_NO

		#ask save question
		head = MR_LANG( 'Delete All Channels' )
		line1 = MR_LANG( 'Are you sure you want to remove%s all your TV and radio channels?' )% NEW_LINE
		if self.mUserMode.mMode == ElisEnum.E_MODE_FAVORITE :
			line1 = MR_LANG( 'Are you sure you want to remove%s all channels from this favorite group?' )% NEW_LINE

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( head, line1 )
		dialog.doModal( )

		ret = dialog.IsOK( )

		#answer is yes
		if ret == E_DIALOG_STATE_YES :
			self.OpenBusyDialog( )
			isBackup = self.mDataCache.Channel_Backup( )

			if self.mUserMode.mMode == ElisEnum.E_MODE_FAVORITE :
				self.LoadFavoriteGroupList( )
				idxSub = self.mUserSlidePos.mSub
				if self.mFavoriteGroupList and len( self.mFavoriteGroupList ) > idxSub :
					favName = self.mFavoriteGroupList[idxSub]
					LOG_TRACE( '[ChannelList] delete favName[%s]'% favName )
					if favName :
						iChannelList = self.mDataCache.Channel_GetListByFavorite( self.mUserMode.mServiceType, self.mUserMode.mMode, self.mUserMode.mSortingMode, favName )
						if iChannelList and len( iChannelList ) > 0 :
							numList = []
							for iChannel in iChannelList :
								chNum = ElisEInteger( )
								chNum.mParam = iChannel.mNumber
								numList.append( chNum )

							self.mFlag_DeleteAll_Fav = True
							favType = self.GetServiceTypeByFavoriteGroup( favName )
							self.mDataCache.Favoritegroup_RemoveChannelByNumber( favName, favType, numList )
					else :
						LOG_TRACE( '[ChannelList] except, no favName idx[%s] favList[%s]'% ( idxSub, self.mFavoriteGroupList ) )

				else :
					LOG_TRACE( '[ChannelList] except, no favGroups idx[%s] favList[%s]'% ( idxSub, self.mFavoriteGroupList ) )


			elif self.mUserMode.mMode == ElisEnum.E_MODE_SATELLITE :
				idxSub = self.mUserSlidePos.mSub
				if self.mUserMode and self.mListSatellite and len( self.mListSatellite ) > idxSub :
					groupInfo = self.mListSatellite[idxSub]
					isDelete = self.mDataCache.Channel_DeleteBySatellite( groupInfo.mLongitude, groupInfo.mBand )
					#LOG_TRACE( '[ChannelList] Channel_DeleteBySatellite ret[%s] longitude[%s] band[%s]'% ( isDelete, groupInfo.mLongitude, groupInfo.mBand ) )

					if isDelete :
						self.mFlag_DeleteAll_Fav = True

				else :
					LOG_TRACE( '[ChannelList] except, no satellite idx[%s] satelliteList[%s]'% ( idxSub, self.mListSatellite ) )

			elif self.mUserMode.mMode == ElisEnum.E_MODE_PROVIDER :
				idxSub = self.mUserSlidePos.mSub
				if self.mUserMode and self.mListProvider and len( self.mListProvider ) > idxSub :
					iProvider = self.mListProvider[idxSub]
					LOG_TRACE( '[ChannelList] delete provider[%s]'% iProvider.mProviderName )
					iChannelList = self.mDataCache.Channel_GetListByProvider( self.mUserMode.mServiceType, self.mUserMode.mMode, self.mUserMode.mSortingMode, iProvider.mProviderName )
					if iChannelList and len( iChannelList ) > 0 :
						numList = []
						for iChannel in iChannelList :
							chNum = ElisEInteger( )
							chNum.mParam = iChannel.mNumber
							numList.append( chNum )

						isDelete = self.mDataCache.Channel_DeleteByNumber( self.mUserMode.mServiceType, 1, numList )
						#LOG_TRACE( '[ChannelList] Channel_DeleteByProvider ret[%s] mProviderName[%s] mType[%s] chLen[%s]'% ( isDelete, iProvider.mProviderName, iProvider.mServiceType, len( numList ) ) )
						if isDelete :
							self.mFlag_DeleteAll_Fav = True

							#default mode allchannels
							self.mUserMode.mMode = ElisEnum.E_MODE_ALL
							self.mUserSlidePos.mMain = E_SLIDE_ACTION_MAIN

				else :
					LOG_TRACE( '[ChannelList] except, no provider idx[%s] providerList[%s]'% ( idxSub, self.mListProvider ) )

			else :
				isDelete = self.mDataCache.Channel_DeleteAll( False )
				if isDelete :
					self.mFlag_DeleteAll = True

			self.CloseBusyDialog( )

		return ret


	def DoModeChange( self, aType = FLAG_MODE_TV ) :
		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW :
			LOG_TRACE( '[ChannelList] Editing now...' )
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
			#self.mCtrlListCHList.reset( )
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
			self.mDataCache.Channel_ResetOldChannelList( )

			thread = threading.Timer( 0, self.LoadByCurrentEPG )
			thread.start( )
			LOG_TRACE( '[ChannelList] epgList hash len[%s]'% len( self.mEPGHashTable ) )

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
		if self.mFlag_DeleteAll :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Your channel list is empty' ) )
			dialog.doModal( )
			return

		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			self.mViewMode = WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW

			try :
				#self.mEventBus.Deregister( self )
				self.mDataCache.LoadTimerList( )
				self.mDataCache.SetChangeDBTableChannel( E_TABLE_ALLCHANNEL )

				self.mDataCache.SetSkipChannelView( True )

				self.mPrevMode = deepcopy( self.mUserMode )
				self.mPrevSlidePos = deepcopy( self.mUserSlidePos )

				self.mLastChannelList = []
				if self.mChannelList and len( self.mChannelList ) > 0 :
					for iChannel in self.mChannelList :
						self.mLastChannelList.append( iChannel )
				self.mLastChannel = deepcopy( self.mChannelListHash.get( self.mCurrentChannel, None ) )
				self.mRestoreTuneChannel = self.mDataCache.Channel_GetCurrent( )

				if self.mLastChannel == None :
					iChannel = self.mDataCache.Channel_GetCurrent( )
					if not iChannel :
						if self.mChannelList and len( self.mChannelList ) > 0 :
							iChannel = self.mChannelList[0]
					self.mLastChannel = iChannel

				if self.mLastChannel :
					LOG_TRACE( '[ChannelList] edit in----current[%s] last ch[%s %s]'% ( self.mCurrentChannel, self.mLastChannel.mNumber, self.mLastChannel.mName ) )

				"""
				# default mode AllChannel : enter EditMode
				self.mUserMode.mMode = ElisEnum.E_MODE_ALL
				self.mUserMode.mSortingMode = ElisEnum.E_SORT_BY_NUMBER
				self.mUserSlidePos.mMain = E_SLIDE_MENU_ALLCHANNEL
				self.mUserSlidePos.mSub  = 0
				"""

				self.UpdateControlListSelectItem( self.mCtrlListMainmenu, self.mUserSlidePos.mMain )
				self.UpdateControlListSelectItem( self.mCtrlListSubmenu, self.mUserSlidePos.mSub )
				#LOG_TRACE( '[ChannelList] IN: slide[%s,%s]--get[%s, %s]--------1'% (self.mUserSlidePos.mMain, self.mUserSlidePos.mSub, self.mCtrlListMainmenu.getSelectedPosition( ), self.mCtrlListSubmenu.getSelectedPosition( ) ) )

				self.mListItems = None
				#self.mCtrlListCHList.reset( )
				self.InitSlideMenuHeader( FLAG_SLIDE_OPEN )
				self.SubMenuAction( E_SLIDE_ACTION_SUB, 0, True )
				self.UpdateControlGUI( E_SLIDE_CLOSE )

				#default channelView
				if self.mShowEPGInfo :
					self.UpdatePropertyGUI( 'ShowExtendInfo', E_TAG_FALSE )

				#clear label
				self.ResetLabel( )
				self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'Channel List' ), '[COLOR ffff4444]%s[/COLOR]'% MR_LANG( 'Edit Channels' ) ) )
				self.UpdateChannelAndEPG( )

				ret = self.mDataCache.Channel_Backup( )
				#LOG_TRACE( '[ChannelList] channelBackup[%s]'% ret )

			except Exception, e :
				LOG_ERR( '[ChannelList] except[%s]'% e )
				self.mMarkList = []
				self.GoToPreviousWindow( )
				LOG_TRACE( '[ChannelList] restore mViewMode[%s]'% self.mViewMode )

		else :
			self.GoToPreviousWindow( )


	def GoToPreviousWindow( self, aGoToWindow = None ) :
		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			if self.mSearchList and len( self.mSearchList ) > 0 :
				self.mSearchList = []
				#self.mChannelList = self.mInstanceBackup
				self.SubMenuAction( E_SLIDE_ACTION_SUB, 0, True )
				LOG_TRACE( '[ChannelList] Restore channel from search' )
				return

			ret = False
			ret = self.SaveSlideMenuHeader( )
			if ret != E_DIALOG_STATE_CANCEL :
				if self.mFlag_DeleteAll or self.mFlag_DeleteAll_Fav :
					self.mDataCache.Channel_ResetOldChannelList( )

				if self.mFlag_DeleteAll and ret == E_DIALOG_STATE_YES :
					if not self.mDataCache.Get_Player_AVBlank( ) :
						self.mDataCache.Player_AVBlank( True )

				self.Close( )
				#2626 qm issue, can not show pip on blank(main channel avblank, scramble, ...), m/w problem
				#if TuneAndFastExit :
				#	DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).TuneChannelByExternal( None,True )

				if aGoToWindow :
					WinMgr.GetInstance( ).ShowWindow( aGoToWindow, WinMgr.WIN_ID_NULLWINDOW )
				else :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW, WinMgr.WIN_ID_NULLWINDOW )

				LOG_TRACE( '[ChannelList] Close to exit' )

		else :
			if self.mMarkList :
				LOG_TRACE( '[ChannelList] marklist[%s]'% self.mMarkList )
				self.ClearMark( )
				self.mMarkList = []

			else :
				if self.mSearchList and len( self.mSearchList ) > 0 :
					self.mSearchList = []
					#self.mChannelList = self.mInstanceBackup
					self.SubMenuAction( E_SLIDE_ACTION_SUB, 0, True )
					LOG_TRACE( '[ChannelList] Restore channel from search' )
					return

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

					#LOG_TRACE( '[ChannelList] slidePos: user[%s,%s] prev[%s,%s]'% (self.mUserSlidePos.mMain, self.mUserSlidePos.mSub, self.mPrevSlidePos.mMain, self.mPrevSlidePos.mSub ) )
					#LOG_TRACE( '[ChannelList]     mode: user[%s,%s] prev[%s,%s]'% (self.mUserMode.mServiceType, self.mUserMode.mSortingMode, self.mPrevMode.mServiceType, self.mPrevMode.mSortingMode ) )
					self.mDataCache.SetSkipChannelView( False )
					self.mUserMode = deepcopy( self.mPrevMode )
					self.mUserSlidePos = deepcopy( self.mPrevSlidePos )

					self.SubMenuAction( E_SLIDE_ACTION_MAIN, self.mUserSlidePos.mMain )

					self.UpdateControlListSelectItem( self.mCtrlListMainmenu, self.mUserSlidePos.mMain )
					self.UpdateControlListSelectItem( self.mCtrlListSubmenu, self.mUserSlidePos.mSub )
					#LOG_TRACE( '[ChannelList] OUT: slide[%s,%s]--get[%s, %s]--------1'% (self.mUserSlidePos.mMain, self.mUserSlidePos.mSub, self.mCtrlListMainmenu.getSelectedPosition( ), self.mCtrlListSubmenu.getSelectedPosition( ) ) )

					#if self.mLastChannel :
					#	LOG_TRACE( '[ChannelList] EDIT OUT, Save[%s] last ch[%s %s]'% ( ret, self.mLastChannel.mNumber, self.mLastChannel.mName ) )

					if ret != E_DIALOG_STATE_YES :
						currChannel = self.mDataCache.Channel_GetCurrent( )
						if self.mRestoreTuneChannel and currChannel and self.mRestoreTuneChannel != currChannel :
							self.mLastChannel = self.mRestoreTuneChannel
							self.mCurrentChannel = self.mLastChannel.mNumber
							self.mDataCache.Channel_SetCurrent( self.mLastChannel.mNumber, self.mLastChannel.mServiceType )
							#LOG_TRACE( '[ChannelList] restore tune last ch[%s %s]'% ( self.mLastChannel.mNumber, self.mLastChannel.mName ) )
						#else :
						#	LOG_TRACE( '[ChannelList] backup last None' )

					self.mListItems = None
					#self.mCtrlListCHList.reset( )
					self.InitSlideMenuHeader( FLAG_SLIDE_OPEN )
					self.SubMenuAction( E_SLIDE_ACTION_SUB, 0, True )

					self.UpdateControlGUI( E_SLIDE_CLOSE )

					#initialize get epg event
					self.mIsTune = False
					self.Epgevent_GetCurrent( )

					#restore epgView
					if self.mShowEPGInfo :
						self.UpdatePropertyGUI( 'ShowExtendInfo', E_TAG_TRUE )

					#clear label
					self.ResetLabel( )
					self.SetHeaderTitle( MR_LANG( 'Channel List' ) )
					self.UpdateChannelAndEPG( )

				else :
					self.mLastChannel = None


	def onEvent(self, aEvent):
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			#LOG_TRACE( '[ChannelList] Receive Event[%s]'% aEvent.getName( ) )

			if aEvent.getName( ) == ElisEventCurrentEITReceived.getName( ) :
				if self.mNavChannel == None:
					#LOG_TRACE('[ChannelList] epg not------ch none')
					return -1

				if self.mNavChannel.mSid != aEvent.mSid or self.mNavChannel.mTsid != aEvent.mTsid or self.mNavChannel.mOnid != aEvent.mOnid :
					#LOG_TRACE('[ChannelList] epg not------eventid no match')
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

							#LOG_TRACE( '[ChannelList] epg different' )
							self.mNavEpg = iEPG
							self.mDataCache.Frontdisplay_SetIcon( ElisEnum.E_ICON_HD, iEPG.mHasHDVideo )
							self.mEPGHashTable[ '%d:%d:%d' %( iEPG.mSid, iEPG.mTsid, iEPG.mOnid) ] = iEPG

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
					#LOG_TRACE( '[ChannelList] EventRecv EOF_STOP' )
					xbmc.executebuiltin( 'xbmc.Action(stop)' )

			elif aEvent.getName( ) == ElisEventChannelChangedByRecord.getName( ) :
				self.UpdateChannelList( )

			elif aEvent.getName( ) == ElisPMTReceivedEvent.getName( ) :
				self.UpdatePropertyByCacheData( E_XML_PROPERTY_TELETEXT )
				self.UpdatePropertyByCacheData( E_XML_PROPERTY_SUBTITLE )
				self.UpdatePropertyByCacheData( E_XML_PROPERTY_DOLBYPLUS )

			elif aEvent.getName( ) == ElisEventChannelDBUpdate.getName( ) :
				self.UpdateChannelByDBUpdateEvent( aEvent )

		#else :
		#	LOG_TRACE( '[ChannelList] channellist winID[%d] this winID[%d]'% ( self.mWinId, xbmcgui.getCurrentWindowId( ) ) )


	def TuneChannel( self, aJumpNumber = None ) :
		#Turn in
		self.mIsTune = True

		if aJumpNumber :
			iChannel = self.mChannelListHash.get( int(aJumpNumber), None ) 
			if iChannel == None :
				return
			LOG_TRACE( '[ChannelList] JumpChannel: ch[%s %s] type[%s] aJumpNum[%s]'% ( iChannel.mNumber, iChannel.mName, iChannel.mServiceType, aJumpNumber ) )

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

		if self.mIsPVR :
			self.mIsPVR = False
			self.mDataCache.Player_Stop( )

		currentChannel = self.mDataCache.Channel_GetCurrent( True )

		isSameChannel = False
		if currentChannel and currentChannel.mServiceType == iChannel.mServiceType and \
		   ( not self.mZappingChange ) and currentChannel.mNumber == iChannel.mNumber and \
		   currentChannel.mSid == iChannel.mSid and currentChannel.mTsid == iChannel.mTsid and \
		   currentChannel.mOnid == iChannel.mOnid :
			isSameChannel = True

		#LOG_TRACE( '[ChannelList] issame[%s] modeChange[%s]'% ( isSameChannel, self.mZappingChange ) )
		self.mZappingChange = False
		ret = False
		if isSameChannel :
			ret = True
		else :
			if iChannel.mLocked or iChannel.mIsCA :
				if not self.mDataCache.Get_Player_AVBlank( ) :
					self.mDataCache.Player_AVBlank( True )

			ret = self.mDataCache.Channel_SetCurrent( iChannel.mNumber, iChannel.mServiceType, self.mChannelListHash )		

		if ret :
			#if ( not isSameChannel ) and ( not self.mDataCache.Get_Player_AVBlank( ) ):
			#	self.mDataCache.Player_AVBlank( True )

			if self.mAutoConfirm :
				isSameChannel = True

			if isSameChannel :
				if self.mSearchList and len( self.mSearchList ) > 0 :
					self.mSearchList = []
					#self.mChannelList = self.mInstanceBackup
					self.SubMenuAction( E_SLIDE_ACTION_SUB, 0, True )
					#self.mDataCache.SetChannelReloadStatus( True )
					LOG_TRACE( '[ChannelList] Restore channel from search' )

				ret = self.SaveSlideMenuHeader( )
				if ret != E_DIALOG_STATE_CANCEL :
					self.Close( )
					#if TuneAndFastExit :
					#	DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).TuneChannelByExternal( None,True )
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE, WinMgr.WIN_ID_NULLWINDOW )				
					return

				LOG_TRACE( '[ChannelList] No exit by pressing the cancel button' )


		#refresh info
		if iChannel :
			self.mNavChannel = iChannel
			self.mCurrentChannel = iChannel.mNumber
			self.mCurrentPosition = self.mCtrlListCHList.getSelectedPosition( )
			pos = self.mCurrentPosition + 1
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_SELECT_NUMBER, str( '%s'% pos ) )
			#LOG_TRACE( '[ChannelList] chinfo: num[%s] type[%s] name[%s] pos[%s]'% ( iChannel.mNumber, iChannel.mServiceType, iChannel.mName, pos ) )

			self.ResetLabel( )
			self.UpdateChannelAndEPG( )


	def RefreshSlideMenu( self, aMainIndex = E_SLIDE_MENU_ALLCHANNEL, aSubIndex = 0, aForce = None ) :
		self.UpdateControlListSelectItem( self.mCtrlListMainmenu, aMainIndex )
		self.UpdateControlListSelectItem( self.mCtrlListSubmenu, aSubIndex )
		self.SubMenuAction( E_SLIDE_ACTION_MAIN, aMainIndex )
		self.SubMenuAction( E_SLIDE_ACTION_SUB, 0, aForce )


	def SubMenuAction( self, aAction = E_SLIDE_ACTION_MAIN, aMenuIndex = 0, aForce = None, aKeyword = '' ) :
		#if self.mFlag_DeleteAll :
		#	return

		retPass = False
		zappingName = ''

		if aAction == E_SLIDE_ACTION_MAIN:
			testlistItems = []
			scListGroup = []
			mSort = self.mUserMode.mSortingMode

			if aMenuIndex == E_SLIDE_MENU_ALLCHANNEL :
				testlistItems.append( xbmcgui.ListItem( '' ) )

			elif aMenuIndex == E_SLIDE_MENU_SATELLITE :
				if self.mListSatellite :
					for groupInfo in self.mListSatellite :
						ret = self.mDataCache.GetFormattedSatelliteName( groupInfo.mLongitude, groupInfo.mBand )
						testlistItems.append( xbmcgui.ListItem( ret ) )
						scListGroup.append( ret )
				else :
					testlistItems.append( xbmcgui.ListItem( MR_LANG( 'None' ) ) )

			elif aMenuIndex == E_SLIDE_MENU_FTACAS :
				if self.mListCasList :
					for groupInfo in self.mListCasList :
						scListGroup.append( groupInfo.mName )
						ret = '%s(%s)'% ( groupInfo.mName, groupInfo.mChannelCount )
						testlistItems.append( xbmcgui.ListItem( ret ) )
				else :
					testlistItems.append( xbmcgui.ListItem( MR_LANG( 'None' ) ) )

			elif aMenuIndex == E_SLIDE_MENU_PROVIDER :
				if self.mListProvider :
					for groupInfo in self.mListProvider :
						scListGroup.append( groupInfo.mProviderName )
						listItem = xbmcgui.ListItem( '%s'% groupInfo.mProviderName )
						testlistItems.append( listItem )
				else :
					testlistItems.append( xbmcgui.ListItem( MR_LANG( 'None' ) ) )

			elif aMenuIndex == E_SLIDE_MENU_FAVORITE :
				if self.mListFavorite :
					for groupInfo in self.mListFavorite :
						scListGroup.append( groupInfo.mGroupName )
						listItem = xbmcgui.ListItem( '%s'% groupInfo.mGroupName )
						if groupInfo.mServiceType > ElisEnum.E_SERVICE_TYPE_RADIO :
							listItem.setProperty( E_XML_PROPERTY_FASTSCAN, E_TAG_TRUE )

						testlistItems.append( listItem )
				else :
					testlistItems.append( xbmcgui.ListItem( MR_LANG( 'None' ) ) )

				mSort = ElisEnum.E_SORT_BY_NUMBER
				LOG_TRACE( '[ChannelList] fixed sort by number in Favorite Group' )

			lblSort = EnumToString( 'sort', mSort )
			lblButtonSort = '%s : %s'% ( MR_LANG( 'Sort' ), lblSort )
			self.UpdateControlGUI( E_CONTROL_ID_BUTTON_SORTING, lblButtonSort )

			if testlistItems != [] :
				#submenu update
				self.mCtrlListSubmenu.reset( )
				self.mCtrlListSubmenu.addItems( testlistItems )
				self.mTempGroupSubmenu = scListGroup

				if aMenuIndex == self.mUserSlidePos.mMain :
					self.mCtrlListSubmenu.selectItem( self.mUserSlidePos.mSub )

			return


		elif aAction == E_SLIDE_ACTION_SUB :
			#LOG_TRACE( '[ChannelList] mode: user[%s,%s %s] prev[%s,%s %s]'% (self.mUserMode.mServiceType, self.mUserMode.mSortingMode, self.mUserMode.mMode, self.mPrevMode.mServiceType, self.mPrevMode.mSortingMode, self.mPrevMode.mMode ) )		
			#LOG_TRACE( '[ChannelList]  OUT: slide[%s,%s]--get[%s, %s]--------1'% (self.mUserSlidePos.mMain, self.mUserSlidePos.mSub, self.mCtrlListMainmenu.getSelectedPosition( ), self.mCtrlListSubmenu.getSelectedPosition( ) ) )			

			idxMain = self.mCtrlListMainmenu.getSelectedPosition( )
			idxSub  = self.mCtrlListSubmenu.getSelectedPosition( )
			if aForce == True :
				idxMain = self.mUserSlidePos.mMain
				idxSub  = self.mUserSlidePos.mSub

			if aForce == None and self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
				#if self.mUserMode.mMode == idxMain :
				if self.mUserSlidePos.mMain == idxMain and \
				   self.mUserSlidePos.mSub == idxSub :
					LOG_TRACE( '[ChannelList] already selected!!!' )
					return

			if aMenuIndex == E_SLIDE_ACTION_SORT :
				pass

			if idxMain == E_SLIDE_MENU_ALLCHANNEL :
				self.mUserMode.mMode = ElisEnum.E_MODE_ALL
				retPass = self.GetChannelList( self.mUserMode.mServiceType, self.mUserMode.mMode, self.mUserMode.mSortingMode, 0, 0, 0, '', '', aKeyword )
				#LOG_TRACE('[ChannelList] All Channel ret[%s] idx[%s,%s]'% ( retPass, idxMain, idxSub ) )

			elif idxMain == E_SLIDE_MENU_SATELLITE :
				if self.mListSatellite :
					groupInfo   = self.mListSatellite[idxSub]
					zappingName = self.mDataCache.GetSatelliteName( groupInfo.mLongitude, groupInfo.mBand )
					self.mUserMode.mMode = ElisEnum.E_MODE_SATELLITE
					self.mUserMode.mSatelliteInfo = groupInfo
					retPass = self.GetChannelList( self.mUserMode.mServiceType, self.mUserMode.mMode, self.mUserMode.mSortingMode, groupInfo.mLongitude, groupInfo.mBand, 0, '', '', aKeyword )
					#LOG_TRACE( '[ChannelList] cmd[channel_GetListBySatellite] idx_Satellite[%s] mLongitude[%s] band[%s]'% ( idxSub, groupInfo.mLongitude, groupInfo.mBand ) )

			elif idxMain == E_SLIDE_MENU_FTACAS :
				if self.mListCasList :
					groupInfo   = self.mListCasList[idxSub]
					zappingName = groupInfo.mName
					caid = groupInfo.mCAId
					self.mUserMode.mMode = ElisEnum.E_MODE_CAS
					self.mUserMode.mCasInfo = groupInfo
					retPass = self.GetChannelList( self.mUserMode.mServiceType, self.mUserMode.mMode, self.mUserMode.mSortingMode, 0, 0, caid, '', '', aKeyword )
					#LOG_TRACE( '[ChannelList] cmd[channel_GetListByFTACas] idxFtaCas[%s]'% idxSub )

			elif idxMain == E_SLIDE_MENU_FAVORITE :
				if self.mListFavorite :
					groupInfo = self.mListFavorite[idxSub]
					zappingName = groupInfo.mGroupName
					self.mUserMode.mMode = ElisEnum.E_MODE_FAVORITE
					self.mUserMode.mFavoriteGroup = groupInfo
					retPass = self.GetChannelList( self.mUserMode.mServiceType, self.mUserMode.mMode, self.mUserMode.mSortingMode, 0, 0, 0, groupInfo.mGroupName, '', aKeyword )
					#LOG_TRACE( '[ChannelList] cmd[channel_GetListByFavorite] idx_Favorite[%s] list_Favorite[%s]'% ( idxSub, groupInfo.mGroupName ) )

			elif idxMain == E_SLIDE_MENU_PROVIDER :
				if self.mListProvider and len( self.mListProvider ) > idxSub :
					groupInfo = self.mListProvider[idxSub]
					zappingName = groupInfo.mProviderName
					self.mUserMode.mMode = ElisEnum.E_MODE_PROVIDER
					self.mUserMode.mProviderInfo = groupInfo
					retPass = self.GetChannelList( self.mUserMode.mServiceType, self.mUserMode.mMode, self.mUserMode.mSortingMode, 0, 0, 0, '', groupInfo.mProviderName, aKeyword )
					#LOG_TRACE( '[ChannelList] cmd[channel_GetListByProvider] idx_Provider[%s] list_Provider[%s]'% ( idxSub, zappingName ) )

		if aKeyword :
			nameColumn = ' > '
			if idxMain == E_SLIDE_MENU_ALLCHANNEL :
				nameColumn = ''
			zappingName += '%s%s \'%s\''% ( nameColumn, MR_LANG( 'Search' ), aKeyword )
			if self.mSearchList and len( self.mSearchList ) > 0 :
				self.mChannelList = self.mSearchList
				self.LoadChannelListHash( )

			else :
				retPass = False
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'No results found' ), MR_LANG( 'Could not find any results for that search' ) )
				dialog.doModal( )

			LOG_TRACE('[ChannelList] Channel Search ret[%s]'% retPass )

		else :
			self.mSearchList = []


		if retPass == False :
			return

		if self.mMoveFlag :
			#do not refresh UI
			return

		#channel list update
		self.mMarkList = []
		self.mListItems = None
		self.mSetMarkCount = 0
		self.mListShortCutGroup = []
		self.mDataCache.Channel_ResetOldChannelList( )
		#self.mCtrlListCHList.reset( )

		self.LoadByCurrentEPG( )
		self.UpdateChannelList( )
		self.RestartAsyncEPG( )

		#init select tune by if exist current channel
		self.mZappingChange = True
		try :
			if self.mNavChannel and self.mChannelList and len( self.mChannelList ) > 0 :
				iChannel = self.mChannelList[self.mCtrlListCHList.getSelectedPosition( )]
				if self.mNavChannel.mServiceType == iChannel.mServiceType and \
				   self.mNavChannel.mNumber == iChannel.mNumber and \
				   self.mNavChannel.mSid == iChannel.mSid and self.mNavChannel.mTsid == iChannel.mTsid and \
				   self.mNavChannel.mOnid == iChannel.mOnid :
					self.mZappingChange = False
					#LOG_TRACE( '[ChannelList] mZappingChange true -> false' )
		except Exception, e :
			LOG_ERR( 'except[%s]'% e )

		#path tree, Mainmenu/Submanu
		self.mUserSlidePos.mMain = idxMain
		self.mUserSlidePos.mSub  = idxSub

		sortEnable   = True
		searchEnable = True
		mSort = self.mUserMode.mSortingMode
		if self.mUserMode.mMode == ElisEnum.E_MODE_FAVORITE or self.mSearchList :
			sortEnable = False
			mSort = ElisEnum.E_SORT_BY_NUMBER
			LOG_TRACE( '[ChannelList] fixed sort by number in Favorite Group' )

		if not self.mChannelList :
			searchEnable = False

		self.mCtrlButtonSorting.setEnabled( sortEnable )
		self.mCtrlButtonSearch.setEnabled( searchEnable )

		lblChannelPath = EnumToString( 'mode', self.mUserMode.mMode )
		if zappingName :
			lblChannelPath = '%s > %s'% ( lblChannelPath, zappingName )

		lblChannelSort = MR_LANG( 'Sorted by %s' )% EnumToString( 'sort', mSort )

		self.mCtrlLabelChannelPath.setLabel( lblChannelPath )
		self.mCtrlLabelChannelSort.setLabel( lblChannelSort )

		#shortCut listUp
		self.mListShortCutGroup = deepcopy( self.mTempGroupSubmenu )

		#current zapping backup
		#self.mDataCache.Channel_Backup( )
		#LOG_TRACE( '[ChannelList] mode: user[%s,%s %s] prev[%s,%s %s]'% ( self.mUserMode.mServiceType, self.mUserMode.mSortingMode, self.mUserMode.mMode, self.mPrevMode.mServiceType, self.mPrevMode.mSortingMode, self.mPrevMode.mMode ) )


	def GetChannelList( self, aType, aMode, aSort, aLongitude=0, aBand=0, aCAid=0, aFavName='', aProvider='', aKeyword = '' ) :
		ret = True
		self.OpenBusyDialog( )
		try :
			instanceList = []
			LOG_TRACE( '[ChannelList] search keyword[%s]'% aKeyword )

			if aMode == ElisEnum.E_MODE_ALL :
				instanceList = self.mDataCache.Channel_GetList( FLAG_ZAPPING_CHANGE, aType, aMode, aSort, aKeyword )

			elif aMode == ElisEnum.E_MODE_SATELLITE :
				instanceList = self.mDataCache.Channel_GetListBySatellite( aType, aMode, aSort, aLongitude, aBand, aKeyword )

			elif aMode == ElisEnum.E_MODE_CAS :
				instanceList = self.mDataCache.Channel_GetListByFTACas( aType, aMode, aSort, aCAid, aKeyword )
				
			elif aMode == ElisEnum.E_MODE_FAVORITE :
				instanceList = self.mDataCache.Channel_GetListByFavorite( aType, aMode, aSort, aFavName, aKeyword )

			elif aMode == ElisEnum.E_MODE_NETWORK :
				pass

			elif aMode == ElisEnum.E_MODE_PROVIDER :
				instanceList = self.mDataCache.Channel_GetListByProvider( aType, aMode, aSort, aProvider, aKeyword )


			if aKeyword :
				self.mSearchList = instanceList

			else :
				self.mChannelList = instanceList
				self.LoadChannelListHash( )
				


		except Exception, e :
			LOG_ERR( 'Error exception[%s]'% e )
			ret = False

		self.CloseBusyDialog( )
		return ret


	def SetSlideMenuHeader( self, aMode ) :
		idx1 = 0
		idx2 = 0
		zInfo_name = ''

		if aMode == FLAG_SLIDE_INIT :

			#self.mUserMode.printdebug( )
			#LOG_TRACE( '[ChannelList] satellite[%s]'% ClassToList( 'convert', self.mListSatellite ) )
			#LOG_TRACE( '[ChannelList] ftacas[%s]'   % ClassToList( 'convert', self.mListCasList ) )
			#LOG_TRACE( '[ChannelList] favorite[%s]' % ClassToList( 'convert', self.mListFavorite ) )

			zInfo_mode = self.mUserMode.mMode
			zInfo_sort = self.mUserMode.mSortingMode
			zInfo_type = self.mUserMode.mServiceType

			if zInfo_mode == ElisEnum.E_MODE_ALL :
				idx1 = E_SLIDE_MENU_ALLCHANNEL
				if zInfo_sort == ElisEnum.E_SORT_BY_NUMBER :
					idx2 = 0
				elif zInfo_sort == ElisEnum.E_SORT_BY_ALPHABET :
					idx2 = 1
				elif zInfo_sort == ElisEnum.E_SORT_BY_HD :
					idx2 = 2
				else :
					idx2 = 0

			elif zInfo_mode == ElisEnum.E_MODE_SATELLITE :
				idx1 = E_SLIDE_MENU_SATELLITE
				#ToDO : is matched by longitude,band ?
				#zInfo_name = self.mUserMode.mSatelliteInfo.mName
				zInfo_name = self.mDataCache.GetSatelliteName( self.mUserMode.mSatelliteInfo.mLongitude, self.mUserMode.mSatelliteInfo.mBand )

				for groupInfo in self.mListSatellite :
					if zInfo_name == self.mDataCache.GetSatelliteName( groupInfo.mLongitude, groupInfo.mBand ) :
						break
					idx2 += 1

			elif zInfo_mode == ElisEnum.E_MODE_CAS :
				idx1 = E_SLIDE_MENU_FTACAS
				zInfo_name = self.mUserMode.mCasInfo.mName

				for groupInfo in self.mListCasList :
					if zInfo_name == groupInfo.mName :
						break
					idx2 += 1

			elif zInfo_mode == ElisEnum.E_MODE_FAVORITE :
				idx1 = E_SLIDE_MENU_FAVORITE
				zInfo_name = self.mUserMode.mFavoriteGroup.mGroupName
				if self.mListFavorite :
					for groupInfo in self.mListFavorite :
						if zInfo_name == groupInfo.mGroupName :
							break
						idx2 += 1

			elif zInfo_mode == ElisEnum.E_MODE_PROVIDER :
				idx1 = E_SLIDE_MENU_PROVIDER
				zInfo_name = self.mUserMode.mProviderInfo.mProviderName
				if self.mListProvider :
					for groupInfo in self.mListProvider :
						if zInfo_name == groupInfo.mProviderName :
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

		#self.UpdateControlListSelectItem( self.mCtrlListMainmenu, idx1 )
		#self.UpdateControlListSelectItem( self.mCtrlListSubmenu, idx2 )
		self.mCtrlListMainmenu.selectItem( idx1 )
		self.mCtrlListSubmenu.selectItem( idx2 )
		self.SubMenuAction( E_SLIDE_ACTION_MAIN, idx1 )
		#self.UpdateControlGUI( E_CONTROL_FOCUSED, E_CONTROL_ID_LIST_SUBMENU )

		return zInfo_name


	def SaveSlideMenuHeader( self ) :
		"""
		LOG_TRACE( '[ChannelList] mode[%s] sort[%s] type[%s] mpos[%s] spos[%s]'% ( \
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
		#LOG_TRACE('[ChannelList] pos[%s] [%s]'% ( self.mLoadSlidePos.debugList(), self.mUserSlidePos.debugList() ) )
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

		if self.mFlag_DeleteAll or self.mFlag_DeleteAll_Fav :
			saveNoAsk = False
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
					if self.mFlag_DeleteAll_Fav :
						self.mUserSlidePos.mMain = E_SLIDE_MENU_ALLCHANNEL
						self.mLoadMode.mMode = ElisEnum.E_MODE_ALL
						self.GetChannelList( self.mLoadMode.mServiceType, self.mLoadMode.mMode, self.mLoadMode.mSortingMode )
						#if self.mChannelList :
						#	LOG_TRACE( '[ChannelList] deleteBy[Groups] reload len[%s]'% len ( self.mChannelList ) )

					if self.mUserSlidePos.mMain == E_SLIDE_MENU_SATELLITE :
						groupInfo = self.mListSatellite[self.mUserSlidePos.mSub]
						if groupInfo :
							groupInfo.mName = self.mDataCache.GetSatelliteName( groupInfo.mLongitude, groupInfo.mBand )
						self.mLoadMode.mSatelliteInfo = groupInfo

					elif self.mUserSlidePos.mMain == E_SLIDE_MENU_FTACAS :
						groupInfo = self.mListCasList[self.mUserSlidePos.mSub]
						self.mLoadMode.mCasInfo = groupInfo

					elif self.mUserSlidePos.mMain == E_SLIDE_MENU_FAVORITE :
						groupInfo = self.mListFavorite[self.mUserSlidePos.mSub]
						self.mLoadMode.mFavoriteGroup = groupInfo

					elif self.mUserSlidePos.mMain == E_SLIDE_MENU_PROVIDER :
						groupInfo = self.mListProvider[self.mUserSlidePos.mSub]
						self.mLoadMode.mProviderInfo = groupInfo
						#LOG_TRACE( '[ChannelList] save provider[%s]'% groupInfo )


					"""
					LOG_TRACE( '[ChannelList] 1. zappingMode[%s] sortMode[%s] serviceType[%s]'%  \
						( EnumToString( 'mode', self.mUserMode.mMode),                \
						  EnumToString( 'sort', self.mUserMode.mSortingMode),         \
						  EnumToString( 'type', self.mUserMode.mServiceType) ) )
					LOG_TRACE( '[ChannelList] 2. zappingMode[%s] sortMode[%s] serviceType[%s]'%  \
						( EnumToString( 'mode', self.mLoadMode.mMode),        \
						  EnumToString( 'sort', self.mLoadMode.mSortingMode), \
						  EnumToString( 'type', self.mLoadMode.mServiceType) ) )
					"""

					#save zapping mode
					if self.mIsSave or \
					   self.mFlag_DeleteAll or self.mFlag_DeleteAll_Fav :
						self.mDataCache.Channel_Save( )
						self.mDataCache.Channel_GetAllChannels( self.mUserMode.mServiceType, False )
						self.mDataCache.SetChannelReloadStatus( True )
						LOG_TRACE( '[ChannelList] save and reload all Channels' )

					#rule : fav or satellite
					if self.mFlag_DeleteAll_Fav :
						if not self.mChannelList or len( self.mChannelList ) < 1 :
							self.mFlag_DeleteAll = True
							LOG_TRACE( '[ChannelList] deleteBy[Groups] ch list None, avblank' )

						else :
							currIdx = 0
							if self.mCurrentChannel and self.mCurrentChannel <= len( self.mChannelList ) :
								currIdx = int( self.mCurrentChannel ) - 1

							self.mLastChannel = self.mChannelList[currIdx]
							self.UpdateLastChannel( True )
							#LOG_TRACE( '[ChannelList] deleteBy[Groups]----last[%s] reTune[%s %s]'% ( self.mCurrentChannel, self.mLastChannel.mNumber, self.mLastChannel.mName ) )
							self.mLastChannel = None

					#rule : public
					if ( not self.mFlag_DeleteAll ) and ( self.mChannelList == None or len( self.mChannelList ) < 1 ) :
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
							#self.mDataCache.LoadChannelList( )
							self.mDataCache.RefreshCacheByChannelList( self.mChannelList )
							WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_SIMPLE_CHANNEL_LIST ).ResetControls( )
							#LOG_TRACE( '[ChannelList] ===================== save yes: cache re-load' )

							if self.mFlag_ModeChanged :
								isBlank = False
								lastServiceType = 'Last TV Number'
								if self.mUserMode.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
									isBlank = True
									lastServiceType = 'Last Radio Number'

								lastChannelNumber = ElisPropertyInt( lastServiceType, self.mCommander ).GetProp( )
								ret = self.mDataCache.Channel_SetCurrent( lastChannelNumber, self.mUserMode.mServiceType )

								#LOG_TRACE( '[ChannelList] last Channel[%s]'% lastChannelNumber )
								if not ret :
									if self.mChannelList and len( self.mChannelList ) > 0 :
										self.mDataCache.Channel_SetCurrent( 1, self.mUserMode.mServiceType )


				elif answer == E_DIALOG_STATE_NO :
					#zapping changed then will re-paint list items for cache
					self.mListItems = None
					self.OpenBusyDialog( )
					try :
						if self.mFlag_DeleteAll or self.mIsSave or self.mFlag_DeleteAll_Fav : 
							#restore backup zapping
							isRestore = self.mDataCache.Channel_Restore( True )
							self.mDataCache.Channel_Save( )
							LOG_TRACE( '[ChannelList] isRestore[%s]'% isRestore )

						#self.mDataCache.Channel_SetCurrent( self.mCurrentChannel.mNumber, self.mCurrentChannel.mServiceType )
						#### data cache re-load ####
						self.mDataCache.LoadZappingmode( )
						self.mDataCache.LoadZappingList( )
						self.mDataCache.LoadChannelList( )
						#LOG_TRACE( '[ChannelList] ===================== save no: cache re-load' )

					except Exception, e :
						LOG_ERR( '[ChannelList] except[%s]'% e )
					self.CloseBusyDialog( )

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
				LOG_ERR( '[ChannelList] except[%s]'% e )


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
				self.OpenBusyDialog( )
				try :
					self.mUserMode = deepcopy( self.mPrevMode )
					self.mDataCache.Zappingmode_SetCurrent( self.mUserMode )
					isSave = self.mDataCache.Channel_Save( )
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_SIMPLE_CHANNEL_LIST ).ResetControls( )

					#### data cache re-load ####
					self.mDataCache.SetSkipChannelView( False )
					self.mDataCache.LoadZappingmode( )
					self.mDataCache.LoadZappingList( )
					self.mDataCache.LoadChannelList( )
					self.mDataCache.Channel_GetAllChannels( self.mUserMode.mServiceType, False )
					LOG_TRACE ( 'save[%s] cache re-load'% isSave)
				except Exception, e :
					LOG_ERR( 'except[%s]'% e )
				self.CloseBusyDialog( )

			elif answer == E_DIALOG_STATE_NO :
				self.mIsSave = FLAG_MASK_NONE
				isSave = self.mDataCache.Channel_Restore( True )
				self.mDataCache.Channel_Save( )
				LOG_TRACE( '[ChannelList] isRestore[%s]'% isSave )

		return answer


	def UpdateLastChannel( self, aForce = False ) :
		ret = False
		isChange = False
		isChangeNumber = False
		lastCount = 0
		currCount = 0
		lastCh = self.mLastChannel
		currCh = self.mDataCache.Channel_GetCurrent( )
		fChannel = self.mDataCache.Channel_GetCurrent( )

		if self.mLastChannelList :
			lastCount = len( self.mLastChannelList )
		if self.mChannelList :
			currCount = len( self.mChannelList )

		if lastCount != currCount or self.mLastChannelList != self.mChannelList :
			isChange = True

		if lastCh and currCh and lastCh.mNumber != currCh.mNumber :
			isChange = True

		if lastCh :
			isChange = True

			try :
				channelList = self.mDataCache.Channel_GetListByIDs( lastCh.mServiceType, lastCh.mTsid, lastCh.mOnid, lastCh.mSid )
				if channelList and len( channelList ) > 0 :
					for iChannel in channelList :
						#LOG_TRACE( '[ChannelList] Channel_GetListByIDs[%s %s]'% ( iChannel.mNumber, iChannel.mName ) )
						if iChannel.mCarrier.mDVBS.mSatelliteLongitude == lastCh.mCarrier.mDVBS.mSatelliteLongitude and \
						   iChannel.mCarrier.mDVBS.mFrequency == lastCh.mCarrier.mDVBS.mFrequency and \
						   iChannel.mCarrier.mDVBS.mSymbolRate == lastCh.mCarrier.mDVBS.mSymbolRate and \
						   iChannel.mCarrier.mDVBS.mSatelliteBand == lastCh.mCarrier.mDVBS.mSatelliteBand and \
						   iChannel.mCarrier.mDVBS.mPolarization == lastCh.mCarrier.mDVBS.mPolarization :
							LOG_TRACE( '[ChannelList] 0. changed Number : old ch[%s %s] last ch[%s %s]'% ( lastCh.mNumber, lastCh.mName, iChannel.mNumber, iChannel.mName ) )
							lastCh = None
							isChangeNumber = True
							self.mLastChannel = iChannel
							break

			except Exception, e :
				LOG_ERR( '[ChannelList] except[%s]'% e )
				lastCh = self.mLastChannel


		#LOG_TRACE( '[ChannelList] refresh isChange[%s] current[%s]'% ( isChange, self.mCurrentChannel ) )
		#if currCh and lastCh :
		#	LOG_TRACE( '[ChannelList] curr[%s %s]'% ( currCh.mNumber, currCh.mName ) )
		#	LOG_TRACE( '[ChannelList] last[%s %s]'% ( lastCh.mNumber, lastCh.mName ) )

		if ( not aForce ) and ( not isChange ) :
			LOG_TRACE( '[ChannelList] no changed' )
			return

		#LOG_TRACE( '[ChannelList] find lastCh[%s]'% lastCh )
		defaultTune = True
		if lastCh :
			#LOG_TRACE( '[ChannelList] 1. last ch[%s] name[%s]'% ( lastCh.mNumber, lastCh.mName ) )

			fChannel = self.GetChannelByIDs( lastCh.mNumber, lastCh.mSid, lastCh.mTsid, lastCh.mOnid )
			if not fChannel :
				#delete(skip)? then current is prev(array) ch
				if E_V1_2_APPLY_PRESENTATION_NUMBER :
					idx = int( lastCh.mPresentationNumber ) - 1
					#LOG_TRACE( '2. tune channel skip or delete : find lastCh idx[%s] len[%s] fCh[%s]'% ( idx, len( self.mChannelList ), fChannel ) )

					if self.mChannelList and idx < len( self.mChannelList ) :
						fChannel = self.mChannelList[idx]
						#if fChannel :
						#	LOG_TRACE( '[ChannelList] 2. tune channel skip or delete : find update idx[%s] len[%s] fCh[%s]'% ( idx, len( self.mChannelList ), fChannel ) )

				else :
					fChannel = self.mDataCache.Channel_GetCurr( lastCh.mNumber )

			if fChannel :
				#LOG_TRACE( '[ChannelList] 3. find update last fChannel[%s %s]'% ( fChannel.mNumber, fChannel.mName ) )
				if aForce or fChannel.mNumber != lastCh.mNumber or \
				   fChannel.mServiceType != lastCh.mServiceType or \
				   fChannel.mSid != lastCh.mSid or fChannel.mTsid != lastCh.mTsid or fChannel.mOnid != lastCh.mOnid :
					defaultTune = False
					ret = self.mDataCache.Channel_SetCurrent( fChannel.mNumber, fChannel.mServiceType )
					#LOG_TRACE( '[ChannelList] 4. refresh tune ch[%s] name[%s]'% ( fChannel.mNumber, fChannel.mName ) )

		if defaultTune :
			LOG_TRACE( '[ChannelList] 5. last None, refresh tune default' )

			#1. find setCurrent channel
			fChannel = self.mDataCache.Channel_GetCurrent( True )
			if isChangeNumber :
				fChannel = self.mLastChannel

			#2. first tune
			if not fChannel :
				if self.mChannelList and len( self.mChannelList ) > 0 :
					#self.TuneChannel( self.mChannelList[0].mNumber )
					fChannel = self.mChannelList[0]

			if fChannel :
				ret = self.mDataCache.Channel_SetCurrent( fChannel.mNumber, fChannel.mServiceType )

			else :
				if not self.mDataCache.Get_Player_AVBlank( ) :
					self.mDataCache.Player_AVBlank( True )


		if ret and fChannel :
			LOG_TRACE( '[ChannelList] 6. finished last update : check current channel and setTune Done' )
			return fChannel

			#deprecated
			#first tune
			if self.mChannelList and len( self.mChannelList ) > 0 :
				#self.TuneChannel( self.mChannelList[0].mNumber )
				fChannel = self.mChannelList[0]
				self.mDataCache.Channel_SetCurrent( fChannel.mNumber, fChannel.mServiceType )
				LOG_TRACE( '[ChannelList] 7. default tune : check current channel and default first setTune' )

			else :
				if not self.mDataCache.Get_Player_AVBlank( ) :
					self.mDataCache.Player_AVBlank( True )
					LOG_TRACE( '[ChannelList] channelList is None' )


	def InitSlideMenuHeader( self, aInitLoad = FLAG_SLIDE_INIT ) :
		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			#opt btn blind
			#self.UpdateControlGUI( E_SETTING_MINI_TITLE, MR_LANG( 'Channel List' ) )
			self.UpdateControlGUI( E_CONTROL_ID_RADIOBUTTON_TV, True, E_TAG_ENABLE )
			self.UpdateControlGUI( E_CONTROL_ID_RADIOBUTTON_RADIO, True, E_TAG_ENABLE )
			self.UpdatePropertyGUI( E_XML_PROPERTY_EDITINFO, E_TAG_FALSE )
			self.UpdatePropertyGUI( E_XML_PROPERTY_MOVE, E_TAG_FALSE )
			self.mCtrlRadioButtonShowEPGInfo.setEnabled( True )

		else :
			#opt btn visible
			#self.UpdateControlGUI( E_SETTING_MINI_TITLE, MR_LANG( 'Edit Channel List' ) )
			self.UpdateControlGUI( E_CONTROL_ID_RADIOBUTTON_TV, False, E_TAG_ENABLE )
			self.UpdateControlGUI( E_CONTROL_ID_RADIOBUTTON_RADIO, False, E_TAG_ENABLE )
			self.UpdatePropertyGUI( E_XML_PROPERTY_EDITINFO, E_TAG_TRUE )
			self.mCtrlRadioButtonShowEPGInfo.setEnabled( False )

		#main/sub menu init
		self.mCtrlListMainmenu.reset( )
		self.mCtrlListSubmenu.reset( )

		list_Mainmenu = []
		list_Mainmenu.append( MR_LANG( 'All CHANNELS' ) )
		list_Mainmenu.append( MR_LANG( 'SATELLITE' )    )
		list_Mainmenu.append( MR_LANG( 'FTA/CAS' )      )
		list_Mainmenu.append( MR_LANG( 'PROVIDER' )    )
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

				#Provider list
				self.mListProvider = self.mDataCache.Provider_GetList( FLAG_ZAPPING_CHANGE, self.mUserMode.mServiceType )

			else :
				self.mListSatellite = self.mDataCache.Satellite_GetConfiguredList( )
				self.mListCasList = self.mDataCache.Fta_cas_GetList( )
				self.mListFavorite = self.mDataCache.Favorite_GetList( )
				self.mListProvider = self.mDataCache.Provider_GetList( FLAG_ZAPPING_CHANGE, self.mUserMode.mServiceType )

		except Exception, e :
			LOG_ERR( '[ChannelList] except[%s]'% e )


		testlistItems = []
		self.mTempGroupSubmenu = []
		if self.mUserMode.mMode == ElisEnum.E_MODE_ALL :
			#for item in range( len( self.mListAllChannel ) ) :
			#	testlistItems.append( xbmcgui.ListItem( self.mListAllChannel[item] ) )
			testlistItems.append( xbmcgui.ListItem( '' ) )

		if self.mUserMode.mMode == ElisEnum.E_MODE_SATELLITE :
			if self.mListSatellite :
				for groupInfo in self.mListSatellite :
					ret = self.mDataCache.GetFormattedSatelliteName( groupInfo.mLongitude, groupInfo.mBand )
					self.mTempGroupSubmenu.append( ret )
					testlistItems.append( xbmcgui.ListItem( ret ) )

		elif self.mUserMode.mMode == ElisEnum.E_MODE_CAS :
			if self.mListCasList :
				for groupInfo in self.mListCasList :
					self.mTempGroupSubmenu.append( groupInfo.mName )
					ret = '%s(%s)'% ( groupInfo.mName, groupInfo.mChannelCount )
					testlistItems.append( xbmcgui.ListItem( ret ) )

		elif self.mUserMode.mMode == ElisEnum.E_MODE_FAVORITE :
			if self.mListFavorite :
				for groupInfo in self.mListFavorite :
					self.mTempGroupSubmenu.append( groupInfo.mGroupName )
					listItem = xbmcgui.ListItem( '%s'% groupInfo.mGroupName )
					if groupInfo.mServiceType > ElisEnum.E_SERVICE_TYPE_RADIO :
						listItem.setProperty( E_XML_PROPERTY_FASTSCAN, E_TAG_TRUE )

					testlistItems.append( listItem )

		elif self.mUserMode.mMode == ElisEnum.E_MODE_PROVIDER :
			if self.mListProvider :
				for groupInfo in self.mListProvider :
					self.mTempGroupSubmenu.append( groupInfo.mProviderName )
					listItem = xbmcgui.ListItem( '%s'% groupInfo.mProviderName )
					testlistItems.append( listItem )


		self.mCtrlListSubmenu.addItems( testlistItems )
		zappingName = self.SetSlideMenuHeader( aInitLoad )

		self.mNavChannel  = None
		self.mChannelList = None

		#path tree, Mainmenu/Submenu
		sortEnable   = True
		searchEnable = True
		mSort = self.mUserMode.mSortingMode
		if self.mUserMode.mMode == ElisEnum.E_MODE_FAVORITE :
			sortEnable = False
			mSort = ElisEnum.E_SORT_BY_NUMBER
			LOG_TRACE( '[ChannelList] fixed sort by number in Favorite Group' )

		if not self.mChannelList :
			searchEnable = False

		self.mCtrlButtonSorting.setEnabled( sortEnable )
		self.mCtrlButtonSearch.setEnabled( searchEnable )

		lblChannelPath = EnumToString( 'mode', self.mUserMode.mMode )
		if zappingName :
			lblChannelPath = '%s > %s'% ( lblChannelPath, zappingName )

		lblSort = EnumToString( 'sort', mSort )
		lblChannelSort = MR_LANG( 'Sorted by %s' )% lblSort
		lblButtonSort = '%s : %s'% ( MR_LANG( 'Sort' ), lblSort )

		self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_PATH, lblChannelPath )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_SORT, lblChannelSort )
		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_SORTING,     lblButtonSort )

		#shortCut listUp
		self.mListShortCutGroup = deepcopy( self.mTempGroupSubmenu )

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
		LOG_TRACE( '[ChannelList] >>>>>>>>>>>>>>>>>>>>>>>>>> skip[%s] table[%s]'% (lblSkip, lblTable) )
		LOG_TRACE( '[ChannelList] zappingMode[%s] sortMode[%s] serviceType[%s]'% \
			( EnumToString( 'mode', self.mUserMode.mMode),             \
			  EnumToString( 'sort', self.mUserMode.mSortingMode),     \
			  EnumToString( 'type', self.mUserMode.mServiceType) ) )
		if self.mChannelList :
			LOG_TRACE( '[ChannelList] >>>>>>>>>>>>>>>>>>>>>>>>>flag_editChange[%s] len[%s] datachche[%s]'% (self.mFlag_EditChanged, len(self.mChannelList), len(self.mDataCache.mChannelList) ))
			#LOG_TRACE( '[ChannelList] len[%s] ch[%s]'% (len(self.mChannelList),ClassToList( 'convert', self.mChannelList ) ) )
		else :
			LOG_TRACE( '[ChannelList] >>>>>>>>>>>>>>>>>>>>>>>>>flag_editChange[%s] len[%s] datachche[%s]'% (self.mFlag_EditChanged, self.mChannelList, self.mDataCache.mChannelList ))
		"""


	def UpdateChannelByDBUpdateEvent( self, aEvent = None ) :
		if not aEvent :
			LOG_TRACE( 'aEvent is none' )
			return

		if aEvent.mUpdateType == 0 :
			#ToDO : All updated db, reload channelList
			pass
			return

		if not self.mChannelList or ( not self.mListItems ) :
			LOG_TRACE( 'Can not update channel info, channellist is None' )
			return

		selected = self.mCtrlListCHList.getSelectedPosition( )
		count = len( self.mChannelList )
		
		for i in range(len( self.mChannelList )):
			channel = self.mChannelList[i]
			if channel and channel.mNumber == aEvent.mChannelNo :
				isCas = E_TAG_FALSE
				if channel.mIsCA :
					isCas = E_TAG_TRUE

				#update listItem
				listItem = self.mCtrlListCHList.getListItem( i )
				listItem.setProperty( E_XML_PROPERTY_CAS, isCas )
				if i == selected :
					UpdateCasInfo( self, channel )
				break


	def UpdateChannelList( self, aUpdatePosition = True ) :
		#starttime = time.time( )
		#print '==================== TEST TIME[LIST] START[%s]'% starttime

		#no channel is set Label comment
		if E_SUPPORT_FRODO_EMPTY_LISTITEM :
			self.mCtrlListCHList.reset( )
			xbmcgui.Window( 10000 ).setProperty( 'isEmpty', E_TAG_FALSE )

		if self.mChannelList == None :
			self.mCtrlListCHList.reset( )
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

			#self.mDataCache.RefreshCacheByChannelList( self.mChannelList )

			for iChannel in self.mChannelList :
				hdLabel = ''
				if iChannel.mIsHD :
					hdLabel = E_TAG_COLOR_HD_LABEL

				iChNumber = iChannel.mNumber
				if E_V1_2_APPLY_PRESENTATION_NUMBER :
					iChNumber = self.mDataCache.CheckPresentationNumber( iChannel, self.mUserMode )

				epgEvent = None
				channelName = '%s'% iChannel.mName
				if self.mShowEPGInfo and self.mViewMode != WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW :
					epgEvent = self.GetEPGByIds( iChannel.mSid, iChannel.mTsid, iChannel.mOnid )
					if epgEvent :
						channelName = '%s %s(%s)%s'% ( iChannel.mName, E_TAG_COLOR_YELLOW, epgEvent.mEventName, E_TAG_COLOR_END )

				listItem = xbmcgui.ListItem( '%04d'% iChNumber, '%s %s'% ( channelName, hdLabel ) )
				if len( iChannel.mName ) > 30 :
					listItem.setLabel2( '%s'% iChannel.mName )
					listItem.setProperty( 'iHDLabel', hdLabel )

				iAlign = E_TAG_FALSE
				if iChNumber > 9999 :
					iAlign = E_TAG_TRUE
				listItem.setProperty( 'iAlign', iAlign )

				if iChannel.mLocked : 
					listItem.setProperty( E_XML_PROPERTY_LOCK, E_TAG_TRUE )
				if iChannel.mIsCA : 
					listItem.setProperty( E_XML_PROPERTY_CAS,  E_TAG_TRUE )
				if iChannel.mIsHD and E_V1_1_HD_ICON_USE :
					listItem.setProperty( E_XML_PROPERTY_IHD, E_TAG_TRUE )

				if self.mRecCount :
					if self.mRecordInfo1 :
						if iChannel.mSid == self.mRecordInfo1.mServiceId and \
						   iChannel.mName == self.mRecordInfo1.mChannelName and \
						   iChannel.mNumber == self.mRecordInfo1.mChannelNo :
							listItem.setProperty( E_XML_PROPERTY_RECORDING, E_TAG_TRUE )
							#LOG_TRACE('[ChannelList] match rec[%s %s]'% ( iChannel.mNumber, iChannel.mName ) )
					if self.mRecordInfo2 :
						if iChannel.mSid == self.mRecordInfo2.mServiceId and \
						   iChannel.mName == self.mRecordInfo2.mChannelName and \
						   iChannel.mNumber == self.mRecordInfo2.mChannelNo :
							listItem.setProperty( E_XML_PROPERTY_RECORDING, E_TAG_TRUE )
							#LOG_TRACE('[ChannelList] match rec[%s %s]'% ( iChannel.mNumber, iChannel.mName ) )

				if self.mViewMode == WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW and iChannel.mSkipped == True : 
					listItem.setProperty( E_XML_PROPERTY_SKIP, E_TAG_TRUE )

				mTPnum = self.mTPListByChannelHash.get( iChannel.mNumber, -1 )
				if mTPnum == E_CONFIGURED_TUNER_1 :
					listItem.setProperty( E_XML_PROPERTY_TUNER1, E_TAG_TRUE )
				elif mTPnum == E_CONFIGURED_TUNER_2 :
					listItem.setProperty( E_XML_PROPERTY_TUNER2, E_TAG_TRUE )
				elif mTPnum == E_CONFIGURED_TUNER_1_2 :
					listItem.setProperty( E_XML_PROPERTY_TUNER1_2, E_TAG_TRUE )

				if epgEvent :
					listItem.setProperty( 'percent', '%s'% self.GetEPGDurationProgress( epgEvent.mStartTime, epgEvent.mDuration ) )
					listItem.setProperty( 'iPos', E_TAG_TRUE )

				self.mListItems.append( listItem )

			self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, self.mListItems, E_TAG_ADD_ITEM )

		iChannel = None
		#refresh sync tune and current focus
		#if self.mLastChannel :
		#	LOG_TRACE( '[ChannelList] focus update lastCh[%s %s]'% ( self.mLastChannel.mNumber, self.mLastChannel.mName ) )
		#else :
		#	LOG_TRACE( '[ChannelList] last None' )

		if self.mLastChannel and self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			LOG_TRACE( '[ChannelList] check last channel' )
			iChannel = self.UpdateLastChannel( )
			self.mLastChannel = None

		#get last channel
		if not iChannel :
			iChannel = self.mDataCache.Channel_GetCurrent( reloadPos )
			#LOG_TRACE( '[ChannelList] Channel_GetCurrent ch[%s %s]'% ( iChannel.mNumber, iChannel.mName ) )

		if iChannel :
			self.mNavChannel = iChannel
			self.mCurrentChannel = self.mNavChannel.mNumber
			#LOG_TRACE( '[ChannelList] current channel[%s] name[%s]'% ( iChannel.mNumber, iChannel.mName ) )

		#detected to last focus
		iChannelIdx = 0
		if E_V1_2_APPLY_PRESENTATION_NUMBER :
			if self.mNavChannel :
				iChannel = self.GetChannelByIDs( self.mNavChannel.mNumber, self.mNavChannel.mSid, self.mNavChannel.mTsid, self.mNavChannel.mOnid )
				if iChannel and self.mChannelList and len( self.mChannelList ) > 0 :
					#find array index
					#iChannelIdx = int( iChannel.mPresentationNumber ) - 1
					try :
						iChannelIdx = self.mChannelList.index( iChannel )
					except Exception, e :
						LOG_ERR( 'except[%s] default tune first'% e )
						iChannelIdx = 0

		else :
			isFind = False
			for iChannel in self.mChannelList :
				if self.mNavChannel :
					if iChannel.mServiceType == self.mNavChannel.mServiceType and \
					   iChannel.mSid == self.mNavChannel.mSid and iChannel.mTsid == self.mNavChannel.mTsid and \
					   iChannel.mOnid == self.mNavChannel.mOnid and iChannel.mNumber == self.mNavChannel.mNumber :
						isFind = True
						break

				iChannelIdx += 1

			if isFind == False :
				iChannelIdx = 0

		if aUpdatePosition :
			self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, iChannelIdx, E_TAG_SET_SELECT_POSITION )
			time.sleep( 0.02 )

		#select item idx, print GUI of 'current / total'
		self.mCurrentPosition = iChannelIdx
		label = '%s - %s'% ( EnumToString( 'type', self.mNavChannel.mServiceType ), self.mNavChannel.mName )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_SELECT_NUMBER, '%s'% ( iChannelIdx + 1 ) )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, label )
		#LOG_TRACE('[ChannelList] curr[%s]'% (iChannelIdx + 1) )

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
		self.UpdatePropertyGUI( 'EPGDescription', '' )
		self.UpdatePropertyGUI( 'EPGDuration', '' )
		self.UpdatePropertyGUI( 'EPGAgeRating', '' )
		self.UpdatePropertyGUI( 'HasAgeRating', 'None' )
		self.UpdatePropertyGUI( E_XML_PROPERTY_TELETEXT, E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_SUBTITLE, E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_DOLBY,    E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_DOLBYPLUS,E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_HD,       E_TAG_FALSE )
		#self.UpdatePropertyGUI( E_XML_PROPERTY_CAS,      E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_IMOVE,    E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_LOCK,     E_TAG_FALSE )
		self.UpdatePropertyGUI( 'iHDLabel', '' )
		if E_V1_1_HD_ICON_USE :
			self.UpdatePropertyGUI( E_XML_PROPERTY_IHD,  E_TAG_FALSE )


	def Epgevent_GetCurrent( self ) :
		try :
			if self.mIsTune == True :
				if not self.mNavChannel :
					LOG_TRACE( '[ChannelList] No Channel' )
					return

				sid  = self.mNavChannel.mSid
				tsid = self.mNavChannel.mTsid
				onid = self.mNavChannel.mOnid
				iEPG = None
				iEPG = self.mDataCache.Epgevent_GetCurrent( sid, tsid, onid )
				if iEPG == None or iEPG.mError != 0 :
					return

				self.mNavEpg = iEPG
				self.mEPGHashTable[ '%d:%d:%d' %( iEPG.mSid, iEPG.mTsid, iEPG.mOnid) ] = iEPG
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
					#LOG_TRACE( '[ChannelList] chNum[%s] chName[%s] sid[%s] tsid[%s] onid[%s] epg[%s] gmtTime[%s]'% ( iChannel.mNumber, iChannel.mName, sid, tsid, onid, iEPG, self.mDataCache.Datetime_GetGMTTime( ) ) )
					if iEPG == None or iEPG.mError != 0 :
						self.mNavEpg = 0
					else :
						self.mEPGHashTable[ '%d:%d:%d' %( iEPG.mSid, iEPG.mTsid, iEPG.mOnid) ] = iEPG

					self.mNavEpg = iEPG
							
		except Exception, e :
			LOG_ERR( '[ChannelList] except[%s]'% e )


	def UpdateControlGUI( self, aCtrlID = None, aValue = None, aExtra = None ) :
		#LOG_TRACE( '[ChannelList] Enter control[%s] value[%s]'% ( aCtrlID, aValue ) )
		if aCtrlID == E_CONTROL_ID_LABEL_CHANNEL_NAME :
			if self.mViewMode != WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW: 		
				self.mCtrlLabelChannelName.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_LONGITUDE_INFO :
			self.mCtrlLabelLongitudeInfo.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_CAREER_INFO :
			self.mCtrlLabelCareerInfo.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_EPG_NAME :
			self.mCtrlLabelEPGName.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_EPG_TIME :
			self.mCtrlLabelEPGTime.setLabel( aValue )

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

		elif aCtrlID == E_CONTROL_ID_RADIOBUTTON_AUTOCONFIRM :
			self.mCtrlRadioButtonAutoConfirm.setSelected( aValue )

		elif aCtrlID == E_CONTROL_ID_RADIOBUTTON_SHOW_EPGINFO :
			self.mCtrlRadioButtonShowEPGInfo.setSelected( aValue )

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

		#elif aCtrlID == E_SETTING_MINI_TITLE :
			#self.mCtrlLabelMiniTitle.setLabel( aValue )


	def UpdatePropertyByCacheData( self, aPropertyID = None ) :
		pmtEvent = self.mDataCache.GetCurrentPMTEvent( self.mNavChannel )
		ret = UpdatePropertyByCacheData( self, pmtEvent, aPropertyID )

		return ret


	def UpdatePropertyGUI( self, aPropertyID = None, aValue = None ) :
		#LOG_TRACE( '[ChannelList] Enter property[%s] value[%s]'% ( aPropertyID, aValue ) )
		if aPropertyID == None :
			return False

		if aPropertyID == E_XML_PROPERTY_EDITINFO or aPropertyID == E_XML_PROPERTY_MOVE :
			rootWinow = xbmcgui.Window( 10000 )
			rootWinow.setProperty( aPropertyID, aValue )

		else :
			self.setProperty( aPropertyID, aValue )


	def UpdateChannelAndEPG( self ) :
		if self.mChannelList == None or len( self.mChannelList ) < 1 :
			return

		if self.mNavChannel :
			#update channel name
			if self.mIsTune == True :
				#strType = self.UpdateServiceType( self.mNavChannel.mServiceType )
				label = '%s - %s'% ( EnumToString( 'type', self.mNavChannel.mServiceType ), self.mNavChannel.mName )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, label )

			#update longitude info
			satellite = self.mDataCache.Satellite_GetByChannelNumber( self.mNavChannel.mNumber, -1 )
			if not satellite :
				#LOG_TRACE( '[ChannelList] Fail GetByChannelNumber by Cache' )
				satellite = self.mDataCache.Satellite_GetByChannelNumber( self.mNavChannel.mNumber, self.mNavChannel.mServiceType )

			if satellite :
				label = self.mDataCache.GetFormattedSatelliteName( satellite.mLongitude, satellite.mBand )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_LONGITUDE_INFO, label )
			else :
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_LONGITUDE_INFO, '' )

			#update lock-icon visible
			if self.mNavChannel.mLocked :
				self.UpdatePropertyGUI( E_XML_PROPERTY_LOCK, E_TAG_TRUE )


			#update career info
			if self.mNavChannel.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBS:
				value1 = self.mNavChannel.mCarrier.mDVBS.mPolarization
				value2 = self.mNavChannel.mCarrier.mDVBS.mFrequency
				value3 = self.mNavChannel.mCarrier.mDVBS.mSymbolRate

				polarization = EnumToString( 'Polarization', value1 )
				careerLabel = '%s MHz, %s KS/S, %s'% (value2, value3, polarization)
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_CAREER_INFO, careerLabel )

			elif self.mNavChannel.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBT :
				value2 = self.mNavChannel.mCarrier.mDVBS.mFrequency
				#value3 = self.mNavChannel.mCarrier.mDVBS.mBand
				careerLabel = '%s KHz' % value2
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_CAREER_INFO, careerLabel )

			elif self.mNavChannel.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBC :
				pass

			elif self.mNavChannel.mCarrierType == ElisEnum.E_CARRIER_TYPE_INVALID :
				pass

			#update cas info
			UpdateCasInfo( self, self.mNavChannel )
				
			"""
			#is cas?
			if self.mNavChannel.mIsCA == True:
				#scrambled
				#ToDO : pincode
			"""
		else :
			self.UpdatePropertyGUI( E_XML_PROPERTY_CAS, E_TAG_FALSE )

		#component
		self.UpdatePropertyByCacheData( E_XML_PROPERTY_TELETEXT )
		isSubtitle = self.UpdatePropertyByCacheData( E_XML_PROPERTY_SUBTITLE )
		if not isSubtitle :
			self.UpdatePropertyGUI( E_XML_PROPERTY_SUBTITLE, HasEPGComponent( self.mNavEpg, ElisEnum.E_HasSubtitles ) )
		if not self.UpdatePropertyByCacheData( E_XML_PROPERTY_DOLBYPLUS ) :
			self.UpdatePropertyGUI( E_XML_PROPERTY_DOLBY,HasEPGComponent( self.mNavEpg, ElisEnum.E_HasDolbyDigital ) )
		self.UpdatePropertyGUI( E_XML_PROPERTY_HD,       HasEPGComponent( self.mNavEpg, ElisEnum.E_HasHDVideo ) )

		#age info
		UpdatePropertyByAgeRating( self, self.mNavEpg )

		try :
			if self.mNavEpg :
				startTime = TimeToString( self.mNavEpg.mStartTime + self.mLocalOffset, TimeFormatEnum.E_HH_MM )
				endTime   = TimeToString( self.mNavEpg.mStartTime + self.mNavEpg.mDuration + self.mLocalOffset, TimeFormatEnum.E_HH_MM )
				label = '%s - %s'% ( startTime, endTime )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_TIME, label )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_NAME, self.mNavEpg.mEventName )
				self.mCtrlProgress.setVisible( True )

				desc = MR_LANG( 'No description' )
				if self.mNavEpg.mEventDescription and self.mNavEpg.mEventDescription != '(null)' :
					desc = '%s\n\n%s'% ( self.mNavEpg.mEventName, self.mNavEpg.mEventDescription )

				self.UpdatePropertyGUI( 'EPGDescription', desc )
				self.UpdatePropertyGUI( 'EPGDuration', '%sm'% ( self.mNavEpg.mDuration / 60 ) )

			if self.mShowEPGInfo and self.mViewMode != WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW :
				newOffsetTopIndex = GetOffsetPosition( self.mCtrlListCHList )
				#LOG_TRACE( '[ChannelList] topIdx old[%s] now[%s]'% ( self.mOffsetTopIndex, newOffsetTopIndex ) )
				if self.mNavOffsetTopIndex == newOffsetTopIndex :
					if self.mNavEpg and self.mNavChannel :
						channelName = '%s'% self.mNavChannel.mName
						epgEvent = self.GetEPGByIds( self.mNavChannel.mSid, self.mNavChannel.mTsid, self.mNavChannel.mOnid )
						if epgEvent :
							channelName = '%s %s(%s)%s'% ( self.mNavChannel.mName, E_TAG_COLOR_YELLOW, epgEvent.mEventName, E_TAG_COLOR_END )

						iChNumber = self.mNavChannel.mNumber
						if E_V1_2_APPLY_PRESENTATION_NUMBER :
							iChNumber = self.mDataCache.CheckPresentationNumber( self.mNavChannel, self.mUserMode )

						chIndex = self.GetChannelByIDs( self.mNavChannel.mNumber, self.mNavChannel.mSid, self.mNavChannel.mTsid, self.mNavChannel.mOnid, True )
						if chIndex > -1 and chIndex < len( self.mChannelList ) :
							hdLabel = ''
							if self.mNavChannel.mIsHD :
								hdLabel = E_TAG_COLOR_HD_LABEL

							listItem = self.mCtrlListCHList.getListItem( chIndex )
							listItem.setLabel2( '%s %s'% ( channelName, hdLabel ) )

							if len( self.mNavChannel.mName ) > 30 :
								listItem.setLabel2( '%s'% self.mNavChannel.mName )
								listItem.setProperty( 'iHDLabel', hdLabel )

							if epgEvent :
								listItem.setProperty( 'percent', '%s'% self.GetEPGDurationProgress( epgEvent.mStartTime, epgEvent.mDuration ) )
								listItem.setProperty( 'iPos', E_TAG_TRUE )
							else :
								listItem.setProperty( 'iPos', E_TAG_FALSE )

						#LOG_TRACE( '[ChannelList] update epg, more info mode, navChannel[%s %s]'% ( iChNumber, channelName ) )

				else :
					self.LoadByCurrentEPG( )
					#self.UpdateChannelNameWithEPG( )

				self.mOffsetTopIndex = newOffsetTopIndex


			else :
				LOG_TRACE( '[ChannelList] event null' )

		except Exception, e:
			LOG_ERR( '[ChannelList] except[%s]'% e )


	def GetEPGDurationProgress( self, aEPGStartTime = 0, aEPGDuration = 0 ) :
		percent      = 0
		startTime    = aEPGStartTime + self.mLocalOffset
		endTime      = startTime + aEPGDuration
		pastDuration = endTime - self.mLocalTime

		if aEPGDuration > 0 :
			percent = 100 - ( abs( pastDuration ) * 100.0 / aEPGDuration )

		if self.mLocalTime > endTime : #Already past
			percent = 100

		elif self.mLocalTime < startTime :
			percent = 0

		if pastDuration < 0 :
			pastDuration = 0

		return percent


	def UpdateChannelNameWithEPG( self, aUpdateAll = False, aForce = False ) :
		if not aForce and ( self.mViewMode == WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW ) :
			LOG_TRACE( '[ChannelList] passed, edit mode' )
			return

		if not self.mListItems or ( not self.mChannelList ) :
			LOG_TRACE( '[ChannelList] passed, channelList None' )
			return

		startTime = time.time()

		updateStart = GetOffsetPosition( self.mCtrlListCHList )
		updateEnd = ( updateStart + self.mItemCount )
		if aUpdateAll :
			updateStart = 0
			updateEnd = len( self.mListItems ) - 1

		#LOG_TRACE( '[ChannelList] offsetTop[%s] idxStart[%s] idxEnd[%s] listHeight[%s] itemCount[%s]'% ( GetOffsetPosition( self.mCtrlListCHList ), updateStart, updateEnd, self.mListHeight, self.mItemCount ) )

		if aUpdateAll :
			self.OpenBusyDialog( )

		try :
			updateCount = 0
			listCount = len( self.mChannelList )
			#for listItem in self.mListItems :
			for idx in range( updateStart, updateEnd ) :
				if self.mChannelList and idx < listCount :
					listItem = self.mListItems[idx]
					iChannel = self.mChannelList[idx]
					channelName = '%s'% iChannel.mName

					if self.mShowEPGInfo :
						epgEvent = self.GetEPGByIds( iChannel.mSid, iChannel.mTsid, iChannel.mOnid )
						if epgEvent :
							channelName = '%s %s(%s)%s'% ( iChannel.mName, E_TAG_COLOR_YELLOW, epgEvent.mEventName, E_TAG_COLOR_END )
							listItem.setProperty( 'percent', '%s'% self.GetEPGDurationProgress( epgEvent.mStartTime, epgEvent.mDuration ) )
							listItem.setProperty( 'iPos', E_TAG_TRUE )
						else :
							listItem.setProperty( 'iPos', E_TAG_FALSE )

					listItem.setLabel2( channelName )
					updateCount += 1

				else :
					break

			LOG_TRACE( '[ChannelList] UpdateChannelNameWithEPG [%s]counts'% updateCount )

		except Exception, e :
			LOG_ERR( '[ChannelList] except[%s]'% e )

		if aUpdateAll :
			self.CloseBusyDialog( )

		#print '[ChannelList] UpdateChannelNameWithEPG------testTime[%s]'% ( time.time() - startTime )


	@RunThread
	def EPGProgressThread( self ) :
		loop = 0
		while self.mEnableProgressThread :
			#LOG_TRACE( '[ChannelList] repeat <<<<' )
			if ( loop % 50 ) == 0 : # 10sec
				self.UpdateProgress( )

			if self.mShowEPGInfo and ( loop % 300 ) == 0 : # 60sec
				self.LoadByCurrentEPG( )
				self.RestartAsyncEPG( )

			time.sleep( 0.2 )
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

				#LOG_TRACE( '[ChannelList] percent[%s]'% percent )
				self.mCtrlProgress.setPercent( percent )

		except Exception, e :
			LOG_ERR( '[ChannelList] except[%s]'% e )
			#self.mLocalTime = 0


	def ShowMoveToGUI( self, aStart, aEnd, aInit = False ) :
		self.mListItems = []

		for i in range( aStart, aEnd ) :
			iChannel = self.mChannelListHash.get( self.mNewChannelList[ i ], None )
			if aInit :
				iChannel = self.mChannelList[ i ]

			if iChannel == None : continue

			iChNumber = iChannel.mNumber
			if E_V1_2_APPLY_PRESENTATION_NUMBER :
				iChNumber = self.mDataCache.CheckPresentationNumber( iChannel, self.mUserMode )

			hdLabel = ''
			if iChannel.mIsHD :
				if len( iChannel.mName ) < 31 :
					hdLabel = E_TAG_COLOR_HD_LABEL

			isFind = False
			for chNumber in self.mMoveList :
				objChannel = self.mChannelListHash.get( chNumber, None )
				if objChannel and iChannel.mNumber == objChannel.mNumber : 
					listItem = xbmcgui.ListItem( '%04d'% iChNumber, '[COLOR white]%s[/COLOR] %s'% ( iChannel.mName, hdLabel ) )
					listItem.setProperty( E_XML_PROPERTY_IMOVE, E_TAG_TRUE )
					#listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_TRUE )
					#LOG_TRACE( '[Edit] move idx[%s] [%04d %s]'% ( i, iChannel.mNumber, iChannel.mName ) )
					isFind = True
					break

			if not isFind :
				listItem = xbmcgui.ListItem( '%04d'% iChNumber, '%s %s'% ( iChannel.mName, hdLabel ) )

			iAlign = E_TAG_FALSE
			if iChNumber > 9999 :
				iAlign = E_TAG_TRUE
			listItem.setProperty( 'iAlign', iAlign )

			if len( iChannel.mName ) > 30 : listItem.setProperty( 'iHDLabel', hdLabel )
			if iChannel.mLocked  : listItem.setProperty( E_XML_PROPERTY_LOCK, E_TAG_TRUE )
			if iChannel.mIsCA    : listItem.setProperty( E_XML_PROPERTY_CAS,  E_TAG_TRUE )
			if iChannel.mSkipped : listItem.setProperty( E_XML_PROPERTY_SKIP, E_TAG_TRUE )
			if iChannel.mIsHD and E_V1_1_HD_ICON_USE :
				listItem.setProperty( E_XML_PROPERTY_IHD, E_TAG_TRUE )

			mTPnum = self.mTPListByChannelHash.get( iChannel.mNumber, -1 )
			if mTPnum == E_CONFIGURED_TUNER_1 :
				listItem.setProperty( E_XML_PROPERTY_TUNER1,  E_TAG_TRUE )
			elif mTPnum == E_CONFIGURED_TUNER_2 :
				listItem.setProperty( E_XML_PROPERTY_TUNER2,  E_TAG_TRUE )
			elif mTPnum == E_CONFIGURED_TUNER_1_2 :
				listItem.setProperty( E_XML_PROPERTY_TUNER1_2, E_TAG_TRUE )

			#LOG_TRACE( '[Edit] move idx[%s] [%04d %s]'% ( i, iChannel.mNumber, iChannel.mName ) )
			self.mListItems.append( listItem )

		self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, self.mListItems, E_TAG_ADD_ITEM )


	def GetInputNumber( self, aDefaultNo = '', aFlag = -1 ) :
		if aFlag == FLAG_OPT_MOVE :
			moveNum = 1
			idxFirst = self.mMarkList[0]
			if self.mMarkList[0] > 0 :
				iChannel = self.mChannelListHash.get( self.mNewChannelList[idxFirst - 1], None )
				if iChannel :
					moveNum = iChannel.mNumber
					if E_V1_2_APPLY_PRESENTATION_NUMBER :
						moveNum = self.mDataCache.CheckPresentationNumber( iChannel, self.mUserMode )

			aDefaultNo = '%s'% moveNum

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
		dialog.SetDialogProperty( MR_LANG( 'Enter a number to insert after' ), aDefaultNo, 5, False )
		dialog.doModal( )
		ret = 0
		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			tempval = dialog.GetString( )
			if len( tempval ) < 1 or int( tempval ) > 99999 :
				ret = 0
			else :
				ret = int( tempval )

		return ret


	def SetMoveMode( self, aMode, aMove = None ) :
		if aMode == FLAG_OPT_MOVE :
			self.OpenBusyDialog( )
			try :
				self.mMoveList = []
				self.mNewChannelList = deepcopy( self.mChannelListForMove )
				self.mRestoreTuneChannel = self.mDataCache.Channel_GetCurrent( True )
				#LOG_TRACE( '[Edit] move in current[%s %s]'% ( self.mRestoreTuneChannel.mNumber, self.mRestoreTuneChannel.mName ) )
				#LOG_TRACE( '[Edit] len channelList[%s] newList[%s] hash[%s]'% ( len(self.mChannelList), len(self.mNewChannelList), len(self.mChannelListHash) ) )

				#self.mListHeight= self.mCtrlListCHList.getHeight( )
				#self.mItemCount = self.mListHeight / self.mItemHeight
				#LOG_TRACE( '[Edit] listHeight[%d] itemHeight[%d] itemCount[%d]'% (self.mListHeight, self.mItemHeight, self.mItemCount) )

				if not self.mMarkList :
					lastPos = self.mCtrlListCHList.getSelectedPosition( )
					self.mMarkList.append( lastPos )
					LOG_TRACE( '[Edit] last position[%s]'% lastPos )

				#self.mMarkList.sort( )
				LOG_TRACE( '[Edit] 1. selection[%s]'% self.mMarkList )
				self.mMarkListBackup = deepcopy( self.mMarkList )

				#2. make listing of ichannel in marked idx
				for idx in self.mMarkList :
					self.mMoveList.append( self.mNewChannelList[idx] )
				self.mMarkList.sort( )
				idxFirst = self.mMarkList[0]
				#LOG_TRACE( '[Edit] markList[%s] moveList[%s] idxFirst[%s]'% ( self.mMarkList, self.mMoveList, idxFirst ) )
				for idx in range( len( self.mMarkList ) ) :
					nextIdx = idxFirst + idx
					findIdx = self.mNewChannelList.index( self.mMoveList[idx] )
					delNum  = self.mNewChannelList.pop( findIdx )
					self.mNewChannelList.insert( nextIdx, self.mMoveList[idx] )
					#LOG_TRACE( 'pop : findIdx[%s] chNum[%s] delIdx[%s]    insert : nextIdx[%s] chNum[%s]'% ( findIdx, self.mMoveList[idx], delNum, nextIdx, self.mMoveList[idx] ) )
				#LOG_TRACE( 'newList[%s]'% self.mNewChannelList )
				LOG_TRACE( '[Edit] 2. selection[%s] move[%s]'% ( self.mMarkList, self.mMoveList ) )

				self.mMoveFlag = True
				self.mListItems = []
				chCount = len( self.mNewChannelList )
				self.mViewFirst = idxFirst
				self.mViewEnd = idxFirst + self.mItemCount

				#show, top ~ bottom
				if chCount < self.mItemCount :
					self.mViewFirst = 0
					self.mViewEnd   = chCount

				elif chCount - idxFirst < self.mItemCount :
					self.mViewFirst = chCount - self.mItemCount
					self.mViewEnd = chCount

				LOG_TRACE( '[Edit] 3. selection[%s] view[%s]~[%s]'% ( self.mMarkList, self.mViewFirst, self.mViewEnd ) )
				self.ShowMoveToGUI( self.mViewFirst, self.mViewEnd )
				self.UpdatePropertyGUI( E_XML_PROPERTY_MOVE, E_TAG_TRUE )

			except Exception, e:
				LOG_ERR( '[Edit] except[%s]'% e )

			self.CloseBusyDialog( )

		elif aMode == FLAG_OPT_MOVE_OK :
			self.OpenBusyDialog( )
			try :
				idxFirst = self.mMarkList[0]

				makeNumber = idxFirst + 1
				makeFavidx = idxFirst + 1
				#LOG_TRACE( '[Edit] insert makeFavidx[%s], makeNumber[%s]'% ( makeFavidx, makeNumber ) )
				#LOG_TRACE( '[Edit] selection[%s]'% self.mMarkList )

				#moveList = []
				#for objChannel in self.mMoveList :
				#	moveList.append( objChannel.mNumber )
				#LOG_TRACE( '[Edit] moveList[%s]'% moveList )

				moveList = []
				for chNumber in self.mMoveList :
					item = self.mChannelListHash.get( chNumber, None )
					if item :
						moveList.append( item )

				idxCurrent = -1
				isMoved = False
				if self.mUserMode.mMode == ElisEnum.E_MODE_FAVORITE :
					groupName = self.mFavoriteGroupList[self.mUserSlidePos.mSub]
					if groupName :
						favType = self.GetServiceTypeByFavoriteGroup( groupName )
						if favType > ElisEnum.E_SERVICE_TYPE_RADIO and self.mDataCache.Favorite_GetLCN( groupName ) :
							moveNum = '%s'% moveList[0].mPresentationNumber
							if idxFirst > 0 :
								#iChannel = self.mDataCache.Channel_GetByNumber( self.mNewChannelList[idxFirst], True )
								iChannel = self.mChannelListHash.get( self.mNewChannelList[idxFirst - 1], None )
								if iChannel :
									moveNum = '%s'% ( iChannel.mPresentationNumber + 1 )
							else :
								moveNum = '1'

							makeFavidx = self.GetInputNumber( '1', FLAG_OPT_MOVE )
							LOG_TRACE( '[Edit] fastScan move inputNum[%s]'% makeFavidx )
							if not makeFavidx :
								LOG_TRACE( '[Edit] input fail' )
								self.CloseBusyDialog( )
								return

						isMoved = self.mDataCache.FavoriteGroup_MoveChannels( groupName, makeFavidx, favType, moveList )
						#LOG_TRACE( '[Edit] group[%s] type[%s]'% ( groupName, favType ) )
				else :
					isMoved = self.mDataCache.Channel_Move( self.mUserMode.mServiceType, makeNumber, moveList )

				LOG_TRACE( '[Edit] move[%s]'% isMoved )

				if isMoved :
					ret = self.mDataCache.Channel_Save( )
					LOG_TRACE( '[Edit] save[%s]'% ret )

				self.UpdatePropertyGUI( E_XML_PROPERTY_MOVE, E_TAG_FALSE )

				self.mMarkList = []
				self.mMoveList = []
				self.mSetMarkCount = 0
				self.mListItems = None
				self.SubMenuAction( E_SLIDE_ACTION_SUB )
				self.mMoveFlag = False

				self.mCtrlListCHList.reset( )
				self.ShowMoveToGUI( 0, len( self.mChannelList ), True )
				#LOG_TRACE ( '[Edit] move exit ===selection[%s] view[%s]~[%s]'% (self.mMarkList, self.mViewFirst, self.mViewEnd) )

				self.mCtrlListCHList.setVisible( False )

				self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, self.mViewEnd - 1, E_TAG_SET_SELECT_POSITION )
				self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, idxFirst, E_TAG_SET_SELECT_POSITION )
				time.sleep( 0.15 )
				self.mCtrlListCHList.setVisible( True )

				if self.mRestoreTuneChannel and self.mChannelList and len( self.mChannelList ) > 0 :
					iCurrent = None
					for iChannel in self.mChannelList :
						if self.mRestoreTuneChannel.mName == iChannel.mName and \
						   self.mRestoreTuneChannel.mSid  == iChannel.mSid and \
						   self.mRestoreTuneChannel.mTsid == iChannel.mTsid and \
						   self.mRestoreTuneChannel.mOnid == iChannel.mOnid :
							iCurrent = iChannel
							break

					if iCurrent :
						self.mCurrentChannel = iCurrent.mNumber
						self.mLastChannel = iCurrent
						ret = self.mDataCache.Channel_SetCurrent( iCurrent.mNumber, iCurrent.mServiceType )
				#LOG_TRACE( '[Edit] move exit, current[%s %s] last[%s %s]'% ( self.mRestoreTuneChannel.mNumber, self.mRestoreTuneChannel.mName, self.mLastChannel.mNumber, self.mLastChannel.mName ) )

			except Exception, e:
				LOG_ERR( '[Edit] except[%s]'% e )

			self.CloseBusyDialog( )
			self.UpdateControlGUI( E_SLIDE_CLOSE )
			#LOG_TRACE ( '[Edit] ========= move End ===' )

		elif aMode == FLAG_OPT_MOVE_EXIT :
			idxFirst = self.mMarkList[0]
			self.mMoveFlag = False
			self.mListItems = None
			self.mMarkList = []
			self.mMoveList = []
			self.mSetMarkCount = 0
			self.mCtrlListCHList.reset( )
			self.UpdatePropertyGUI( E_XML_PROPERTY_MOVE, E_TAG_FALSE )

			self.ShowMoveToGUI( 0, len( self.mChannelList ), True )
			#self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, self.mLastPos, E_TAG_SET_SELECT_POSITION )
			if self.mMarkListBackup and len( self.mMarkListBackup ) > 0 :
				for idx in self.mMarkListBackup :
					self.SetMark( idx )

			self.mCtrlListCHList.setVisible( False )
			self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, self.mViewEnd - 1, E_TAG_SET_SELECT_POSITION )
			self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, idxFirst, E_TAG_SET_SELECT_POSITION )
			time.sleep( 0.15 )
			self.mCtrlListCHList.setVisible( True )
			self.UpdateControlGUI( E_SLIDE_CLOSE )
			self.mMarkListBackup = []

		elif aMode == FLAG_OPT_MOVE_UPDOWN :
			updown= 0
			topPos = 0
			markList= []
			lastidx = len( self.mMarkList ) - 1

			#1. moving
			try :
				topPos = self.mMarkList[0]
				markCount = len( self.mMarkList  )
				channelCount = len( self.mNewChannelList )
				maxShowCount = self.mItemCount

				if channelCount <= self.mItemCount :
					maxShowCount = channelCount

				if aMove == Action.ACTION_MOVE_UP :
					if topPos == 0 :
						return
					updown = -1

					if topPos + updown < self.mViewFirst:	
						self.mViewFirst =  self.mViewFirst + updown

				elif aMove == Action.ACTION_MOVE_DOWN :	
					updown = 1
					if topPos + markCount + updown > channelCount :
						return
					if topPos + markCount + updown > self.mViewFirst + maxShowCount :					
						self.mViewFirst =  self.mViewFirst + updown

				elif aMove == Action.ACTION_PAGE_UP :	
					if topPos == 0 :
						return
					if topPos - maxShowCount < 0 :
						updown = -topPos
						self.mViewFirst =  self.mViewFirst + updown
					else :
						updown = -maxShowCount
						self.mViewFirst =  self.mViewFirst + updown

				elif aMove == Action.ACTION_PAGE_DOWN :
					if topPos + markCount == channelCount :
						return

					if topPos + markCount + maxShowCount > channelCount :
						updown = channelCount - ( topPos + markCount  )
						#updown = topPos + maxShowCount + markCount - ( channelCount + markCount )
					else :
						updown = maxShowCount

					self.mViewFirst =  self.mViewFirst + updown

				elif aMove == Action.ACTION_CONTEXT_MENU :
					if not self.mMoveList or len( self.mMoveList ) < 1 :
						LOG_TRACE( 'None move list' )
						return

					inputNum = self.GetInputNumber( '1', FLAG_OPT_MOVE )
					if inputNum < 1 or inputNum == topPos :
						LOG_TRACE( 'same position or Input wrong' )
						return

					if topPos > inputNum :
						#up
						if topPos == 0 :
							LOG_TRACE( 'limit move position top over' )
							return

						if topPos - inputNum - markCount < markCount :
							updown = -topPos + ( inputNum - 1 )
						else :
							updown = -( topPos - inputNum + markCount )

					else :
						if markCount + inputNum > channelCount :
							updown = channelCount - ( topPos + markCount )
						else :
							updown = inputNum - ( topPos + markCount )

					LOG_TRACE( 'move input[%s] topPos[%s] updown[%s] viewFirst[%s]'% ( inputNum, topPos, updown, self.mViewFirst ) )
					if updown == 0 :
						LOG_TRACE( 'no move same position' )
					if topPos + updown < 0 :
						LOG_TRACE( 'limit move position top over' )
						updown = -topPos + 1

					self.mViewFirst = self.mViewFirst + updown

				LOG_TRACE( 'topPos[%s] updown[%s] viewFirst[%s]'% ( topPos, updown, self.mViewFirst ) )

 			except Exception, e :
 				LOG_ERR( '[Edit] except[%s]'% e )
				#import traceback
				#LOG_ERR( 'traceback=%s' %traceback.format_exc() )
 
			#pop moveList
			popidx = self.mMarkList[0]
			ctrlItem = []
			for idx in self.mMoveList :
				item = self.mNewChannelList.pop( popidx )

			#update index in moveList
			for idx in self.mMarkList :
				idxNew = int( idx ) + updown
				markList.append( idxNew )
			self.mMarkList = []
			self.mMarkList = markList
			insertPos = self.mMarkList[0]

			#insert moveList
			for i in range( len( self.mMoveList ) ) :
				idx = lastidx - i
				self.mNewChannelList.insert( insertPos, self.mMoveList[idx] )
			
			#if ( topPos + updown) < self.mViewFirst or ( topPos +  updown)  >= self.mViewEnd :
			#	self.mViewFirst = self.mViewFirst + updown

			if self.mViewFirst < 0 :
				self.mViewFirst = 0

			self.mViewEnd = self.mViewFirst +  maxShowCount

			bottom = len( self.mNewChannelList )
			if self.mViewEnd > bottom :
				LOG_TRACE( '[Edit] Limit bottom over' )
				self.mViewFirst = bottom - maxShowCount
				self.mViewEnd = bottom

			#LOG_TRACE( '[Edit] self.mViewFirst=%d self.mViewEnd=%d' %(self.mViewFirst, self.mViewEnd ) )
			#LOG_TRACE( '[Edit] view Top[%s]~Bot[%s] insertPos[%s]'% ( self.mViewFirst, self.mViewEnd, insertPos ) )
			self.ShowMoveToGUI( self.mViewFirst, self.mViewEnd )

			#select item idx, print GUI of 'current / total'
			pos = '%s'% ( int( self.mMarkList[0] )  + 1 )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_SELECT_NUMBER, pos )


	def SetMark( self, aPos ) :
		idx = 0
		isExist = False

		for i in self.mMarkList :
			if i == aPos :
				self.mMarkList.pop(idx)
				isExist = True
			idx += 1

		if isExist == False : 
			self.mMarkList.append( aPos )

		iChannel = self.mChannelList[ aPos ]
		listItem = self.mCtrlListCHList.getListItem( aPos )

		hdLabel = ''
		if iChannel.mIsHD :
			hdLabel = E_TAG_COLOR_HD_LABEL

		if listItem.getProperty( E_XML_PROPERTY_MARK ) == E_TAG_TRUE : 
			listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_FALSE )
			if len( iChannel.mName ) > 30 :
				listItem.setProperty( 'iHDLabel', hdLabel )
				listItem.setLabel2( '%s'% iChannel.mName )
			else :
				listItem.setLabel2( '%s %s'% ( iChannel.mName, hdLabel ) )

		else :
			self.mSetMarkCount += 1
			listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_TRUE )
			numLabel = ''
			#numLabel= '  [COLOR white]#%s[/COLOR]'% self.mSetMarkCount
			hdLabel = ' %s%s'% ( hdLabel, numLabel )
			chName = '%s%s'% ( iChannel.mName, hdLabel )
			if len( iChannel.mName ) > 30 :
				chName = '%s'% iChannel.mName
				listItem.setProperty( 'iHDLabel', hdLabel )

			listItem.setLabel2( chName )


	def ClearMark( self ) :
		self.mSetMarkCount = 0
		if self.mMarkList == None or len( self.mMarkList ) < 1 or \
		   self.mChannelList == None or len( self.mChannelList ) < 1 :
			return

		for pos in self.mMarkList :
			iChannel = self.mChannelList[ pos ]
			hdLabel = ''
			if iChannel.mIsHD :
				if len( iChannel.mName ) < 31 :
					hdLabel = E_TAG_COLOR_HD_LABEL

			listItem = self.mCtrlListCHList.getListItem( pos )
			listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_FALSE )
			listItem.setLabel2( '%s %s'% ( iChannel.mName, hdLabel ) )
			if len( iChannel.mName ) > 30 :
				listItem.setProperty( 'iHDLabel', hdLabel )


	def SetListItemToGUI( self, aProperty = None, aValue = E_TAG_FALSE ) :
		if not self.mMarkList or len( self.mMarkList ) < 1 :
			LOG_TRACE( '[Edit] No has markList' )
			return

		if not aProperty :
			LOG_TRACE( '[Edit] No property' )

		intValue = 0
		if aValue == E_TAG_TRUE :
			intValue = 1

		for pos in self.mMarkList :
			#icon update
			listItem = self.mCtrlListCHList.getListItem( pos )
			listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_FALSE )
			listItem.setProperty( aProperty, aValue )

			#data update
			if self.mChannelList and len( self.mChannelList ) > pos :
				if aProperty == E_XML_PROPERTY_LOCK :
					self.mChannelList[pos].mLocked = intValue
				elif aProperty == E_XML_PROPERTY_SKIP :
					self.mChannelList[pos].mSkipped = intValue

		self.mMarkList = []


	def LoadFavoriteGroupList( self ) :
		self.mListFavorite = self.mDataCache.Favorite_GetList( FLAG_ZAPPING_CHANGE, self.mUserMode.mServiceType )
		self.mFavoriteGroupList = []
		if self.mListFavorite :
			for groupInfo in self.mListFavorite :
				#copy to favoriteGroup
				self.mFavoriteGroupList.append( groupInfo.mGroupName )


	def GetFavoriteGroup( self, aGroupName = None ) :
		if not aGroupName :
			LOG_TRACE( '[Edit] request groupName None' )
			return

		if not self.mListFavorite or len( self.mListFavorite ) < 1 :
			LOG_TRACE( '[Edit] FavoriteGroup List None' )
			return

		favGroup = None
		for groupInfo in self.mListFavorite :
			if groupInfo.mGroupName == aGroupName :
				favGroup = groupInfo
				break

		return favGroup


	def GetServiceTypeByFavoriteGroup( self, aGroupName ) :
		favType = self.mUserMode.mServiceType
		favGroup = self.GetFavoriteGroup( aGroupName )
		if favGroup :
			favType = favGroup.mServiceType

		return favType


	def AddFavoriteChannels( self, aChannelList = None, aGroupName = '', aSelectList = [], aMode = FLAG_OPT_LIST ) :
		if aChannelList == None or len( aChannelList ) < 1 :
			return self.mDataCache.Channel_GetList( FLAG_ZAPPING_CHANGE, self.mUserMode.mServiceType, ElisEnum.E_MODE_ALL, self.mUserMode.mSortingMode, '', True )

		else :
			if aGroupName == None or aGroupName == '' :
				LOG_TRACE( '[Edit] Can not add to Channel favGroup, No selected favGroup' )
				return

			numList = []
			lastPos = self.mCtrlListCHList.getSelectedPosition( )
			for idx in aSelectList :
				chNum = ElisEInteger( )
				chNum.mParam = aChannelList[idx].mNumber
				numList.append( chNum )

			if not numList or len( numList ) < 1 :
				LOG_TRACE( '[Edit] Selection failed!!!' )
				return

			favType = self.GetServiceTypeByFavoriteGroup( aGroupName )
			ret = self.mDataCache.Favoritegroup_AddChannelByNumber( aGroupName, favType, numList )
			LOG_TRACE( '[Edit] Favoritegroup_AddChannelByNumber[%s]'% ret )

			isReload = False
			#if aMode == FLAG_OPT_LIST :
			#	isReload = True

			#else :
			if self.mFavoriteGroupList and len( self.mFavoriteGroupList ) > self.mUserSlidePos.mSub and \
			   self.mFavoriteGroupList[self.mUserSlidePos.mSub] == aGroupName :
				isReload = True

			if self.mSearchList :
				isReload = False


			if isReload :
				self.mMarkList = []
				self.mListItems = None
				self.SubMenuAction( E_SLIDE_ACTION_SUB )
				self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, lastPos, E_TAG_SET_SELECT_POSITION )

			else :
				pass
				#self.SetListItemToGUI( E_XML_PROPERTY_MARK, E_TAG_FALSE )


	def DoContextActionByGroup( self, aContextAction, aGroupName = '' ) :
		ret = False
		refreshForce = False

		if aContextAction == CONTEXT_ACTION_CREATE_GROUP_FAV :
			if aGroupName :
				idx = self.mDataCache.Favoritegroup_Create( aGroupName, self.mUserMode.mServiceType )	#default : ElisEnum.E_SERVICE_TYPE_TV
				#LOG_TRACE('[Edit] create fav[%s] ret[%s]'% ( aGroupName, idx ) )
				if idx != -1 :
					ret = True

		elif aContextAction == CONTEXT_ACTION_RENAME_FAV :
			if aGroupName :
				name = re.split( ':', aGroupName)
				favType = self.GetServiceTypeByFavoriteGroup( name[1] )
				ret = self.mDataCache.Favoritegroup_ChangeName( name[1], favType, name[2] )

		elif aContextAction == CONTEXT_ACTION_DELETE_FAV :
			if aGroupName :
				favType = self.GetServiceTypeByFavoriteGroup( aGroupName )
				ret = self.mDataCache.Favoritegroup_Remove( aGroupName, favType )
				#LOG_TRACE( '[Edit] favRemove after favList ori[%s] edit[%s]'% (self.mListFavorite, self.mFavoriteGroupList))
				refreshForce = True

		elif aContextAction == CONTEXT_ACTION_DELETE_FAV_CURRENT :
			if not self.mFavoriteGroupList or len( self.mFavoriteGroupList ) < 1 :
				return

			aGroupName = self.mFavoriteGroupList[self.mUserSlidePos.mSub]
			if aGroupName :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( MR_LANG( 'Delete Favorite Group' ), MR_LANG( 'Are you sure you want to remove%s%s?' ) % ( NEW_LINE, aGroupName ) )
				dialog.doModal( )

				answer = dialog.IsOK( )

				#answer is yes
				if answer != E_DIALOG_STATE_YES :
					return answer

				favType = self.GetServiceTypeByFavoriteGroup( aGroupName )
				ret = self.mDataCache.Favoritegroup_Remove( aGroupName, favType )


		if ret :
			self.LoadFavoriteGroupList( )
			#LOG_TRACE('[Edit] favlist[%s]'% self.mFavoriteGroupList )
			if aContextAction == CONTEXT_ACTION_DELETE_FAV_CURRENT :
				self.mUserSlidePos.mMain = E_SLIDE_MENU_ALLCHANNEL
				self.mUserSlidePos.mSub = 0
				self.mMarkList = []
				self.mListItems = None
				self.RefreshSlideMenu( self.mUserSlidePos.mMain, self.mUserSlidePos.mSub, True )

		if self.mUserSlidePos.mMain == E_SLIDE_MENU_FAVORITE or refreshForce :
			self.SubMenuAction( E_SLIDE_ACTION_MAIN, E_SLIDE_MENU_FAVORITE, True )
			#LOG_TRACE( '[Edit] pos main[%s] sub[%s]'% (self.mUserSlidePos.mMain, self.mUserSlidePos.mSub ) )

			#re-print current path
			if self.mFavoriteGroupList and len( self.mFavoriteGroupList ) > self.mUserSlidePos.mSub :
				lblChannelPath = EnumToString( 'mode', self.mUserMode.mMode )
				zappingName = self.mFavoriteGroupList[self.mUserSlidePos.mSub]
				if self.mSearchList and len( self.mSearchList ) > 0 :
					zappingName += '> %s\'%s\''% ( MR_LANG( 'Search' ), self.mSearchKeyword )

				if zappingName :
					lblChannelPath = '%s > %s'% ( lblChannelPath, zappingName )
					self.mCtrlLabelChannelPath.setLabel( lblChannelPath )


	def DoContextAction( self, aMode, aContextAction, aGroupName = '' ) :
		ret = ''
		numList = []
		timerList = []
		isNomark = False
		isRefresh = True
		isIncludeRec = False
		isIncludeTimer = False
		lastPos = self.mCtrlListCHList.getSelectedPosition( )
		#LOG_TRACE( '[Edit] groupName[%s] lastPos[%s]'% ( aGroupName, lastPos ) )

		if self.mChannelList :
			#1.no selection : set current position item
			if not self.mMarkList :
				isNomark = True
				self.mMarkList.append( lastPos )

			#2.set selection : list all
			isRefreshCurrentChannel = False
			for idx in self.mMarkList :
				iChannel = self.mChannelList[idx]
				chNum = ElisEInteger( )
				chNum.mParam = iChannel.mNumber
				numList.append( chNum )

				if not isIncludeTimer :
					iTimer = self.GetTimerByIDs( iChannel.mNumber, iChannel.mSid, iChannel.mTsid, iChannel.mOnid )
					if iTimer :
						isIncludeTimer = True
						#LOG_TRACE( '[Edit] exist timerCh[%s %s] iChannel[%s %s]'% ( iTimer.mChannelNo, iTimer.mName, iChannel.mNumber, iChannel.mName ) )

				#check rec item
				if self.mRecCount :
					if self.mRecordInfo1 and \
					   ( self.mRecordInfo1.mServiceId == iChannel.mSid and \
					   self.mRecordInfo1.mChannelName == iChannel.mName and \
					   self.mRecordInfo1.mChannelNo == iChannel.mNumber ) or \
					   self.mRecordInfo2 and \
					   ( self.mRecordInfo2.mServiceId == iChannel.mSid and \
					   self.mRecordInfo2.mChannelName == iChannel.mName and \
					   self.mRecordInfo2.mChannelNo == iChannel.mNumber ) :
						isIncludeRec = True
				#LOG_TRACE('[Edit] mRecCount[%s] rec1[%s] rec2[%s] isRec[%s]'% (self.mRecCount, self.mRecordInfo1, self.mRecordInfo2, isIncludeRec) )

			if not numList or len( numList ) < 1 :
				LOG_TRACE( '[Edit] MarkList failed!!!' )
				return


		if aContextAction == CONTEXT_ACTION_LOCK :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_INPUT_PINCODE )
			dialog.SetTitleLabel( MR_LANG( 'Enter PIN Code' ) )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				ret = self.mDataCache.Channel_LockByNumber( True, int(self.mUserMode.mServiceType), numList )
				if ret :
					isRefresh = False
					self.SetListItemToGUI( E_XML_PROPERTY_LOCK, E_TAG_TRUE )
			else :
				return

		elif aContextAction == CONTEXT_ACTION_UNLOCK :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_INPUT_PINCODE )
			dialog.SetTitleLabel( MR_LANG( 'Enter PIN Code' ) )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				ret = self.mDataCache.Channel_LockByNumber( False, int(self.mUserMode.mServiceType), numList )
				if ret :
					isRefresh = False
					self.SetListItemToGUI( E_XML_PROPERTY_LOCK, E_TAG_FALSE )
			else :
				return

		elif aContextAction == CONTEXT_ACTION_SKIP :
			#blocking all skip
			if len( numList ) >= len( self.mChannelList ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Skipping all channels is not allowed' ) )
				dialog.doModal( )
				return

			ret = self.mDataCache.Channel_SkipByNumber( True, int(self.mUserMode.mServiceType), numList )
			if ret :
				isRefresh = False
				self.SetListItemToGUI( E_XML_PROPERTY_SKIP, E_TAG_TRUE )

		elif aContextAction == CONTEXT_ACTION_UNSKIP :
			ret = self.mDataCache.Channel_SkipByNumber( False, int(self.mUserMode.mServiceType), numList )
			if ret :
				isRefresh = False
				self.SetListItemToGUI( E_XML_PROPERTY_SKIP, E_TAG_FALSE )

		elif aContextAction == CONTEXT_ACTION_ADD_TO_FAV :
			if aGroupName :
				favType = self.GetServiceTypeByFavoriteGroup( aGroupName )
				ret = self.mDataCache.Favoritegroup_AddChannelByNumber( aGroupName, favType, numList )
				if ret :
					isRefresh = False
					self.SetListItemToGUI( E_XML_PROPERTY_MARK, E_TAG_FALSE )
				#LOG_TRACE('[Edit] num ret[%s] len[%s] list[%s] markList[%s]'% ( ret, len(numList), ClassToList('convert',numList), self.mMarkList ) )
			else :
				ret = 'group None'

		elif aContextAction == CONTEXT_ACTION_DELETE :
			#LOG_TRACE('[Edit] isRec[%s] isTimer[%s]'% ( isIncludeRec, isIncludeTimer ) )
			if isIncludeRec or isIncludeTimer :
				msg = MR_LANG( 'Are you sure you want to delete the channels%s including currently recording or reserved?' )% NEW_LINE
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( MR_LANG( 'Delete Channels' ), msg )
				dialog.doModal( )

				answer = dialog.IsOK( )
				if answer != E_DIALOG_STATE_YES :
					if isNomark :
						self.mMarkList = []
					return

			if aMode == FLAG_OPT_LIST :
				ret = self.mDataCache.Channel_DeleteByNumber( int( self.mUserMode.mServiceType ), 1, numList )
				#LOG_TRACE( '[Edit] isRefresh[%s] ret[%s]'% ( isRefreshCurrentChannel, ret ) )

			else :
				aGroupName = self.mFavoriteGroupList[self.mUserSlidePos.mSub]
				if aGroupName :
					favType = self.GetServiceTypeByFavoriteGroup( aGroupName )
					ret = self.mDataCache.Favoritegroup_RemoveChannelByNumber( aGroupName, favType, numList )
					#LOG_TRACE( '[Edit] isRefresh[%s] ret[%s]'% ( isRefreshCurrentChannel, ret ) )

				else :
					ret = 'group None'

		elif aContextAction == CONTEXT_ACTION_MOVE :
			self.mLastPos = lastPos
			self.SetMoveMode( FLAG_OPT_MOVE, None )
			return

		elif aContextAction == CONTEXT_ACTION_CHANGE_NAME :
			if aGroupName :
				#toDO : update just channel name instead of refresh
				name = re.split( ':', aGroupName )
				self.mDataCache.Channel_ChangeChannelName( int( name[0] ), self.mUserMode.mServiceType, name[2] )
				#LOG_TRACE( '[Edit] ch[%s] old[%s] new[%s]'% ( name[0], name[1], name[2] ) )

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

			elif self.mFlag_DeleteAll or not self.mChannelList or len( self.mChannelList ) < 1 :
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

		elif aContextAction == CONTEXT_ACTION_HOTKEYS :
			self.ShowHotkeys( )

		LOG_TRACE( '[Edit] contextAction ret[%s]'% ret )

		if isRefresh :
			self.mMarkList = []
			self.mListItems = None
			self.SubMenuAction( E_SLIDE_ACTION_SUB )

			#recovery last focus
			self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, lastPos, E_TAG_SET_SELECT_POSITION )

		"""
		lastTop = self.mCtrlListCHList.getOffsetPosition( )
		if lastTop < 0 :
			lastTop = 0
		self.mCtrlListCHList.setVisible( False )
		self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, lastTop, E_TAG_SET_SELECT_POSITION )
		self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, lastPos, E_TAG_SET_SELECT_POSITION )
		time.sleep( 0.15 )
		self.mCtrlListCHList.setVisible( True )
		self.UpdateControlGUI( E_SLIDE_CLOSE )
		"""


	def ShowEditContextMenu( self, aMode, aMove = None ) :
		#try:
		if self.mMoveFlag :
			if self.mUserMode.mMode == ElisEnum.E_MODE_FAVORITE :
				groupName = self.mFavoriteGroupList[self.mUserSlidePos.mSub]
				if groupName :
					favType = self.GetServiceTypeByFavoriteGroup( groupName )
					if favType > ElisEnum.E_SERVICE_TYPE_RADIO and self.mDataCache.Favorite_GetLCN( groupName ) :
						LOG_TRACE( 'FastScanGroup is press OK after insert LCN number' )
						return

			#All Channel, normalGroup only
			context = []
			context.append( ContextItem( MR_LANG( 'Insert' ), CONTEXT_ACTION_INSERT_NUMBER ) )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context )
	 		dialog.doModal( )

			selectedAction = dialog.GetSelectedAction( )
			if selectedAction == -1 :
				#LOG_TRACE( 'CANCEL by context dialog' )
				return

			self.SetMoveMode( FLAG_OPT_MOVE_UPDOWN, Action.ACTION_CONTEXT_MENU )
			return

		self.LoadFavoriteGroupList( )
		#LOG_TRACE( '[Edit] favList ori[%s] edit[%s]'% (self.mListFavorite, self.mFavoriteGroupList))

		#default context item
		context = []
		if self.mChannelList and len( self.mChannelList ) > 0 :
			context.append( ContextItem( MR_LANG( 'Lock' ),   CONTEXT_ACTION_LOCK ) )
			context.append( ContextItem( MR_LANG( 'Unlock' ), CONTEXT_ACTION_UNLOCK ) )
			context.append( ContextItem( MR_LANG( 'Skip' ),   CONTEXT_ACTION_SKIP ) )
			context.append( ContextItem( MR_LANG( 'Unskip' ), CONTEXT_ACTION_UNSKIP  ) )
			context.append( ContextItem( MR_LANG( 'Delete' ), CONTEXT_ACTION_DELETE ) )
			if self.mUserMode.mMode == ElisEnum.E_MODE_ALL or self.mUserMode.mMode == ElisEnum.E_MODE_FAVORITE :
				context.append( ContextItem( MR_LANG( 'Move' ),   CONTEXT_ACTION_MOVE ) )
			context.append( ContextItem( MR_LANG( 'Rename' ), CONTEXT_ACTION_CHANGE_NAME ) )

		if not self.mMarkList :
		#if ( self.mChannelList and len( self.mChannelList ) > 0 ) or E_SEARCH_ALL :
			context.append( ContextItem( MR_LANG( 'Search' ), CONTEXT_ACTION_CHANNEL_SEARCH ) )

		if aMode == FLAG_OPT_GROUP :
			context.append( ContextItem( '%s'% MR_LANG( 'Add channels to this group' ), CONTEXT_ACTION_ADD_TO_CHANNEL ) )

		if self.mFavoriteGroupList and len( self.mFavoriteGroupList ) > 0 :
			context.append( ContextItem( '%s'% MR_LANG( 'Add channels to favorite group' ), CONTEXT_ACTION_ADD_TO_FAV  ) )

		context.append( ContextItem( '%s'% MR_LANG( 'Create favorite group' ), CONTEXT_ACTION_CREATE_GROUP_FAV  ) )

		if self.mFavoriteGroupList and len( self.mFavoriteGroupList ) > 0 :
			context.append( ContextItem( '%s'% MR_LANG( 'Rename favorite group' ), CONTEXT_ACTION_RENAME_FAV ) )
			context.append( ContextItem( '%s'% MR_LANG( 'Delete favorite group' ), CONTEXT_ACTION_DELETE_FAV ) )

		#if not self.mChannelList :
		#	context.append( ContextItem( MR_LANG( 'Delete this favorite group' ), CONTEXT_ACTION_DELETE_FAV_CURRENT ) )

		context.append( ContextItem( '%s'% MR_LANG( 'Save and exit' ), CONTEXT_ACTION_SAVE_EXIT ) )


		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
 		dialog.doModal( )

		selectedAction = dialog.GetSelectedAction( )
		if selectedAction == -1 :
			LOG_TRACE( '[Edit] Close context dialog by CANCEL' )
			return

		#Not available
		if ( (not self.mFavoriteGroupList) and (selectedAction == CONTEXT_ACTION_ADD_TO_CHANNEL) ) or \
		   ( (not self.mFavoriteGroupList) and (selectedAction == CONTEXT_ACTION_ADD_TO_FAV) ) or \
		   ( (not self.mFavoriteGroupList) and (selectedAction == CONTEXT_ACTION_RENAME_FAV) ) or \
		   ( (not self.mFavoriteGroupList) and (selectedAction == CONTEXT_ACTION_DELETE_FAV) ) :
			LOG_TRACE( '[Edit] Not Available, FavoriteGroup is None' )
			return

		if selectedAction == CONTEXT_ACTION_SAVE_EXIT :
			self.GoToPreviousWindow( )
			return

		elif selectedAction == CONTEXT_ACTION_CHANNEL_SEARCH :
			self.ShowSearchDialog( )
			return


		#--------------------------------------------------------------- dialog 2
		grpIdx = -1
		groupName = None
		mMarkList = deepcopy( self.mMarkList )
		channelList = self.mChannelList

		#if aMode == FLAG_OPT_LIST and self.mChannelList :
		#1.no selection : set current position item
		if not mMarkList :
			lastPos = self.mCtrlListCHList.getSelectedPosition( )
			mMarkList.append( lastPos )

		#if selectedAction == CONTEXT_ACTION_ADD_TO_CHANNEL or \
		#   ( aMode == FLAG_OPT_GROUP and selectedAction == CONTEXT_ACTION_ADD_TO_FAV ) :
		if selectedAction == CONTEXT_ACTION_ADD_TO_CHANNEL :
			channelList = self.AddFavoriteChannels( )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SELECT )
			dialog.SetPreviousBlocking( False )
			dialog.SetDefaultProperty( MR_LANG( 'Add Channels to This Favorite Group' ), channelList, E_MODE_CHANNEL_LIST )
			dialog.doModal( )
			groupName = self.mFavoriteGroupList[self.mUserSlidePos.mSub]

			actionId = dialog.GetCloseStatus( )
			if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
				LOG_TRACE( '[Edit] Cancelled back or previous' )
				return

			mMarkList = dialog.GetSelectedList( )
			#LOG_TRACE( '[Edit] add group[%s]-----dialog list[%s]'% ( groupName, self.mMarkList ) )

			if mMarkList == None or len( mMarkList ) < 1 :
				LOG_TRACE( '[Edit] Cancelled by context dialog, No select' )
				return

		# add Fav, Ren Fav, Del Fav ==> popup select group
		if selectedAction == CONTEXT_ACTION_ADD_TO_FAV or \
		   selectedAction == CONTEXT_ACTION_RENAME_FAV or \
		   selectedAction == CONTEXT_ACTION_DELETE_FAV :
			title = ''
			groupList = deepcopy( self.mFavoriteGroupList )
			if selectedAction == CONTEXT_ACTION_ADD_TO_FAV :   title = MR_LANG( 'Add Channels to Favorite Group' )
			elif selectedAction == CONTEXT_ACTION_RENAME_FAV : title = MR_LANG( 'Rename Favorite Group' )
			elif selectedAction == CONTEXT_ACTION_DELETE_FAV : 
				title = MR_LANG( 'Delete Favorite Group' )
				if aMode == FLAG_OPT_GROUP :
					groupList = []
					currGroup = ''
					if self.mFavoriteGroupList :
						currGroup = self.mFavoriteGroupList[self.mUserSlidePos.mSub]
					for favGroup in self.mFavoriteGroupList :
						if favGroup == currGroup :
							LOG_TRACE( '[Edit] blocked group self' )
							continue
						groupList.append( favGroup )

			grpIdx = xbmcgui.Dialog( ).select( title, groupList )
			if grpIdx == -1 :
				LOG_TRACE( '[Edit] Close dialog by CANCEL' )
				return

			groupName = groupList[grpIdx]
			#LOG_TRACE( '[Edit] grpIdx[%s] fav[%s]'% ( grpIdx,groupName ) )

			if selectedAction == CONTEXT_ACTION_DELETE_FAV :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( MR_LANG( 'Delete Favorite Group' ), MR_LANG( 'Are you sure you want to remove%s%s?' ) % ( NEW_LINE,  groupName ) )
				dialog.doModal( )

				answer = dialog.IsOK( )

				#answer is yes
				if answer != E_DIALOG_STATE_YES :
					LOG_TRACE( '[Edit] No delete favGroup' )
					return

			grpIdx = selectedAction

		# Ren Fav, Del Fav ==> popup input group Name
		if selectedAction == CONTEXT_ACTION_CREATE_GROUP_FAV or \
		   selectedAction == CONTEXT_ACTION_RENAME_FAV or \
		   selectedAction == CONTEXT_ACTION_CHANGE_NAME :
			label = ''
			default = ''
			if selectedAction == CONTEXT_ACTION_CREATE_GROUP_FAV :
				#create
				result = ''
				label = MR_LANG( 'Enter Favorite Group Name' )

			elif selectedAction == CONTEXT_ACTION_RENAME_FAV :
				#rename
				default = groupName
				result = '%d'%grpIdx + ':' + groupName + ':'
				label = MR_LANG( 'Enter New Favorite Group Name' )

			elif selectedAction == CONTEXT_ACTION_CHANGE_NAME :
				idx = self.mCtrlListCHList.getSelectedPosition( )
				groupName = self.mChannelList[idx].mName
				default = groupName
				result = '%d'%self.mChannelList[idx].mNumber + ':' + default + ':'
				label = MR_LANG( 'Enter New Channel Name' )

			kb = xbmc.Keyboard( default, label, False )
			kb.doModal( )

			isConfirmed = kb.isConfirmed( )
			name = kb.getText( )
			if not isConfirmed or name == None or name == '' :
				LOG_TRACE('[Edit] No favName or cencel')
				return

			if selectedAction == CONTEXT_ACTION_RENAME_FAV and groupName == name or \
			   selectedAction == CONTEXT_ACTION_CHANGE_NAME and groupName == name :
				LOG_TRACE( '[Edit] could not rename fav. : same name exists' )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'That name already exists' ) )
				dialog.doModal( )
				return

			symbolPattern = '\'|\"|\%|\^|\&|\*|\`'
			if bool( re.search( symbolPattern, name, re.IGNORECASE ) ) :
				#LOG_TRACE( '[Edit] invalid characters : %s'% symbolPattern )
				LOG_TRACE( '[Edit] invalid characters' )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'That name contains invalid characters' ) )
				dialog.doModal( )
				return

			groupName = result + name


		#LOG_TRACE( '[Edit] mode[%s] btn[%s] groupName[%s]'% (aMode, selectedAction, groupName) )
		#--------------------------------------------------------------- context end

		if selectedAction == CONTEXT_ACTION_ADD_TO_CHANNEL or selectedAction == CONTEXT_ACTION_ADD_TO_FAV :
			self.AddFavoriteChannels( channelList, groupName, mMarkList, aMode )

		elif selectedAction == CONTEXT_ACTION_CREATE_GROUP_FAV or \
			selectedAction == CONTEXT_ACTION_RENAME_FAV or \
			selectedAction == CONTEXT_ACTION_DELETE_FAV or \
			selectedAction == CONTEXT_ACTION_DELETE_FAV_CURRENT :
			self.DoContextActionByGroup( selectedAction, groupName )

		else :
			self.DoContextAction( aMode, selectedAction, groupName )

		self.mIsSave |= FLAG_MASK_ADD


	def ShowContextMenu( self ) :
		mode = FLAG_OPT_LIST
		if self.mUserMode.mMode == ElisEnum.E_MODE_FAVORITE :
			mode = FLAG_OPT_GROUP

		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			context = []
			context.append( ContextItem( MR_LANG( 'Edit' ), CONTEXT_ACTION_MENU_EDIT_MODE ) )
			context.append( ContextItem( MR_LANG( 'Search' ), CONTEXT_ACTION_CHANNEL_SEARCH ) )
			lblLine = MR_LANG( 'Delete all' )
			if self.mUserMode and self.mUserMode.mMode == ElisEnum.E_MODE_SATELLITE :
				idxSub = self.mUserSlidePos.mSub
				if self.mListSatellite and len( self.mListSatellite ) > idxSub :
					groupInfo = self.mListSatellite[idxSub]
					satelliteName = self.mDataCache.GetSatelliteName( groupInfo.mLongitude, groupInfo.mBand )
					lblLine = '%s %s'% ( lblLine, satelliteName )

			elif self.mUserMode and self.mUserMode.mMode == ElisEnum.E_MODE_FAVORITE :
				self.LoadFavoriteGroupList( )
				idxSub = self.mUserSlidePos.mSub
				if self.mFavoriteGroupList and len( self.mFavoriteGroupList ) > idxSub :
					favName = self.mFavoriteGroupList[idxSub]
					if favName :
						lblLine = '%s %s'% ( lblLine, favName )

			elif self.mUserMode and self.mUserMode.mMode == ElisEnum.E_MODE_PROVIDER :
				idxSub = self.mUserSlidePos.mSub
				if self.mListProvider and len( self.mListProvider ) > idxSub :
					iProvider = self.mListProvider[idxSub]
					if iProvider :
						lblLine = '%s %s'% ( lblLine, iProvider.mProviderName )

			context.append( ContextItem( lblLine, CONTEXT_ACTION_MENU_DELETEALL ) )
			context.append( ContextItem( MR_LANG( 'Hotkeys' ), CONTEXT_ACTION_HOTKEYS ) )

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context )
	 		dialog.doModal( )

			selectedAction = dialog.GetSelectedAction( )
			if selectedAction == -1 :
				LOG_TRACE( '[ChannelList] Close dialog by CANCEL' )
				return

			if selectedAction == CONTEXT_ACTION_CHANNEL_SEARCH :
				self.ShowSearchDialog( )
				return

			self.DoContextAction( mode, selectedAction )

		else :
			self.ShowEditContextMenu( mode )


	def ShowSearchDialog( self ) :
		kb = xbmc.Keyboard( self.mSearchKeyword, MR_LANG( 'Enter Search Keywords' ), False )
		kb.doModal( )

		if not kb.isConfirmed( ) :
			LOG_TRACE( '[ChannelList] Fail to search channel, keyword none' )
			return

		keyword = kb.getText( )
		LOG_TRACE( 'keyword len=%d' %len( keyword ) )
		if len( keyword ) < MININUM_KEYWORD_SIZE :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'A keyword must be at least %d characters long' ) % MININUM_KEYWORD_SIZE )
			dialog.doModal( )
			return

		symbolPattern = '\'|\"|\%|\^|\&|\*|\`'
		if bool( re.search( symbolPattern, keyword, re.IGNORECASE ) ) :
			#LOG_TRACE( '[Edit] invalid characters : %s'% symbolPattern )
			LOG_TRACE( '[Edit] invalid characters' )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'That name contains invalid characters' ) )
			dialog.doModal( )
			return

		LOG_TRACE( '[ChannelList] search keyword[%s]'% keyword )
		self.mSearchKeyword = keyword
		self.SubMenuAction( E_SLIDE_ACTION_SUB, 0, True, keyword )


	def Close( self ):
		self.mEventBus.Deregister( self )
		if self.mEnableProgressThread == True and self.mPlayProgressThread :
			self.mEnableProgressThread = False				
			self.mPlayProgressThread.join( )

		threading.Timer( 0, self.StopAsyncEPG ).start( )
		threading.Timer( 0, self.StopAsyncSort ).start( )
		self.SetVideoRestore( )
		#WinMgr.GetInstance( ).CloseWindow( )


	def ShowHotkeys( self ) :
		context = [ ( 'OSDPlayNF_Rotated.png', '', MR_LANG( 'Extra Options' ) ), ( 'OSDOK.png', '', MR_LANG( 'Tune In' ) ), ( 'OSDRewindNF.png', '', MR_LANG( 'Previous Group' ) ), ( 'OSDForwardNF.png', '', MR_LANG( 'Next Group' ) ), ( 'OSDRecordNF.png', '', MR_LANG ( 'Start Recording' ) ), ( 'OSDStopNF.png', '', MR_LANG( 'Stop Recording' ) ), ( 'OSDTVRadioNF.png', '', MR_LANG( 'TV/Radio' ) ), ( 'OSDBackNF.png', 'OSDMenuNF.png', MR_LANG( 'Go Back' ) ) ]

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_HOTKEYS )
		dialog.SetProperty( context )
		dialog.doModal( )


	def RestartAsyncEPG( self ) :
		self.StopAsyncEPG( )
		self.StartAsyncEPG( )


	def StartAsyncEPG( self ) :
		self.mAsyncTuneTimer = threading.Timer( 0.5, self.AsyncUpdateCurrentEPG )
		self.mAsyncTuneTimer.start( )

		if self.mViewMode != WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW and self.mNavOffsetTopIndex != GetOffsetPosition( self.mCtrlListCHList ) :
			updateEpgInfo = threading.Timer( 0.05, self.LoadByCurrentEPG )
			updateEpgInfo.start( )


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
			LOG_ERR( '[ChannelList] except[%s]'% e )



	def TuneByNumber( self, aKey ) :
		if self.mChannelList == None :
			return -1

		if aKey == 0 :
			return -1

		if self.mViewMode != WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			return -1

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_JUMP )
		dialog.SetDialogProperty( str( aKey ), self.mChannelListHash, True, self.mMaxChannelNum, self.mUserMode.mMode )
		dialog.doModal( )

		isOK = dialog.IsOK( )
		if isOK == E_DIALOG_STATE_YES :
			inputNumber = dialog.GetChannelLast( )
			#LOG_TRACE( '[ChannelList] Jump chNum[%s] currentCh[%s]'% ( inputNumber, self.mCurrentChannel ) )

			if int( self.mCurrentChannel ) == int( inputNumber ) :
				ch = None
				ch = self.mDataCache.Channel_GetCurrent( )
				#LOG_TRACE( '[ChannelList] aJump num[%s] name[%s] current[%s]'% ( ch.mNumber, ch.mName, self.mCurrentChannel ) )
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
				if int( inputNumber ) > 0 :
					self.TuneChannel( int( inputNumber ) )
					#LOG_TRACE( '[ChannelList] setTune' )


	def ShowRecordingStartDialog( self ) :
		isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )

		if not HasAvailableRecordingHDD( ) :
			return

		isChangeDuration = False
		if self.mRecordInfo1 or self.mRecordInfo2 :
			pos = self.mCurrentPosition
			if self.mCtrlListCHList.getListItem( pos ).getProperty( E_XML_PROPERTY_RECORDING ) == E_TAG_TRUE :
				isChangeDuration = True

		isOK = False
		if isRunRec < E_MAX_RECORD_COUNT or isChangeDuration :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
			dialog.doModal( )

			isOK = dialog.IsOK( )
			if isOK == E_DIALOG_STATE_YES :
				isOK = True

			if dialog.IsOK( ) == E_DIALOG_STATE_ERROR and dialog.GetConflictTimer( ) :
				RecordConflict( dialog.GetConflictTimer( ) )

		else:
			msg = MR_LANG( 'You have reached the maximum number of%s recordings allowed' )% NEW_LINE
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
			#LOG_TRACE( '[ChannelList] isRunRecCount[%s]'% isRunRec )

			if self.mRecCount == 1 :
				self.mRecordInfo1 = self.mDataCache.Record_GetRunningRecordInfo( 0 )

			elif self.mRecCount == 2 :
				self.mRecordInfo1 = self.mDataCache.Record_GetRunningRecordInfo( 0 )
				self.mRecordInfo2 = self.mDataCache.Record_GetRunningRecordInfo( 1 )

		except Exception, e :
			LOG_ERR( '[ChannelList] except[%s]'% e )


	def UpdateRecordInfo( self, aOldRecInfo1, aOldRecInfo2 ) :
		try :
			iChannel = None

			if aOldRecInfo1 :
				iChannel = self.mDataCache.Channel_GetByOneForRecording( aOldRecInfo1.mServiceId )
				#LOG_TRACE('[ChannelList] num[%s] name[%s]'% (iChannel.mNumber, iChannel.mName) )
				if iChannel : 
					pos = int( iChannel.mNumber ) - 1
					self.mCtrlListCHList.getListItem( pos ).setProperty( E_XML_PROPERTY_RECORDING, E_TAG_FALSE )

			if aOldRecInfo2 :
				iChannel = self.mDataCache.Channel_GetByOneForRecording( aOldRecInfo2.mServiceId )
				if iChannel : 
					pos = int( iChannel.mNumber ) - 1
					self.mCtrlListCHList.getListItem( pos ).setProperty( E_XML_PROPERTY_RECORDING, E_TAG_FALSE )

			if self.mRecordInfo1  :
				iChannel = self.mDataCache.Channel_GetByOneForRecording( self.mRecordInfo1.mServiceId )
				if iChannel : 
					#LOG_TRACE('[ChannelList] num[%s] name[%s] lenList[%s]'% ( iChannel.mNumber, iChannel.mName, len(self.mChannelList) ) )
					pos = int( iChannel.mNumber ) - 1
					self.mCtrlListCHList.getListItem( pos ).setProperty( E_XML_PROPERTY_RECORDING, E_TAG_TRUE )

			if self.mRecordInfo2 :
				iChannel = self.mDataCache.Channel_GetByOneForRecording( self.mRecordInfo2.mServiceId )
				if iChannel : 
					pos = int( iChannel.mNumber ) - 1
					self.mCtrlListCHList.getListItem( pos ).setProperty( E_XML_PROPERTY_RECORDING, E_TAG_TRUE )

		except Exception, e :
			LOG_ERR( '[ChannelList] except[%s]'% e )


	def ReloadChannelList( self, aInit = FLAG_SLIDE_OPEN ) :
		self.mListItems = None
		#self.mCtrlListCHList.reset( )
		self.InitSlideMenuHeader( aInit )
		mainIdx = self.mUserSlidePos.mMain
		subIdx  = self.mUserSlidePos.mSub
		self.RefreshSlideMenu( mainIdx, subIdx, True )
		self.UpdateControlGUI( E_SLIDE_CLOSE )


	def UpdateSort( self ) :
		nextSort = ElisEnum.E_SORT_BY_NUMBER
		if self.mUserMode.mSortingMode == ElisEnum.E_SORT_BY_NUMBER :
			nextSort = ElisEnum.E_SORT_BY_ALPHABET
		elif self.mUserMode.mSortingMode == ElisEnum.E_SORT_BY_ALPHABET :
			nextSort = ElisEnum.E_SORT_BY_HD
			if self.mUserMode.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
				nextSort = ElisEnum.E_SORT_BY_NUMBER

		self.mUserMode.mSortingMode = nextSort
		#LOG_TRACE('[ChannelList] nextSort[%s] user: type[%s] mode[%s] sort[%s]'% (nextSort,self.mUserMode.mServiceType, self.mUserMode.mMode,self.mUserMode.mSortingMode) )

		lblSort = EnumToString( 'sort', nextSort )
		label = '%s : %s'% ( MR_LANG( 'Sort' ), lblSort )
		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_SORTING, label )

		self.RestartAsyncSort( )


	def RestartAsyncSort( self ) :
		self.StopAsyncSort( )
		self.StartAsyncSort( )


	def StartAsyncSort( self ) :
		self.mAsyncSortTimer = threading.Timer( 1, self.SubMenuAction, [E_SLIDE_ACTION_SUB, E_SLIDE_ACTION_SORT, True] )
		self.mAsyncSortTimer.start( )


	def StopAsyncSort( self ) :
		if self.mAsyncSortTimer and self.mAsyncSortTimer.isAlive( ) :
			self.mAsyncSortTimer.cancel( )
			del self.mAsyncSortTimer

		self.mAsyncSortTimer = None


	def UpdateShortCutGroup( self, aMove = 1 ) :
		if self.mUserMode.mMode == ElisEnum.E_MODE_ALL :
			LOG_TRACE( '[ChannelList] pass, currrent mode All Channels' )
			return

		if self.mMoveFlag :
			LOG_TRACE( '[ChannelList] pass, edit mode and move' )
			return

		if not self.mListShortCutGroup or len( self.mListShortCutGroup ) < 1 :
			LOG_TRACE( '[ChannelList] pass, short cut group None' )
			return

		self.GetFocusId( )
		if self.mFocusId != E_CONTROL_ID_LIST_CHANNEL_LIST :
			LOG_TRACE( '[ChannelList] pass, opened slide' )
			return

		currentGroup = ''
		if self.mUserSlidePos.mSub < len( self.mListShortCutGroup ) :
			currentGroup = self.mListShortCutGroup[self.mUserSlidePos.mSub]

		if not currentGroup :
			LOG_TRACE( '[ChannelList] pass, current group None' )
			return

		countIdx = 0
		currentIdx = -1
		for groupName in self.mListShortCutGroup :
			if groupName == currentGroup :
				currentIdx = countIdx
				break

			countIdx += 1

		if currentIdx < 0 :
			LOG_TRACE( '[ChannelList] pass, can not find current group' )
			return

		nextGroup = currentGroup
		nextIdx = currentIdx + aMove
		if nextIdx < 0 :
			nextIdx = len( self.mListShortCutGroup ) - 1

		if nextIdx >= len( self.mListShortCutGroup ) :
			nextIdx = 0

		if not ( nextIdx < len( self.mListShortCutGroup ) ) :
			LOG_TRACE( '[ChannelList] error, incorrect index' )
			return

		nextGroup = self.mListShortCutGroup[nextIdx]

		self.mUserSlidePos.mSub = nextIdx
		self.mCtrlListSubmenu.selectItem( nextIdx )

		lblChannelPath = EnumToString( 'mode', self.mUserMode.mMode )
		if nextGroup :
			lblChannelPath = '%s > [COLOR grey2]%s[/COLOR]'% ( lblChannelPath, nextGroup )

		self.mCtrlLabelChannelPath.setLabel( lblChannelPath )

		self.RestartAsyncSort( )


	def UpdateShortCutZapping( self, aReqMode = E_SLIDE_MENU_FAVORITE ) :
		if not FLAG_USE_COLOR_KEY :
			LOG_TRACE( '[ChannelList] pass, no support key' )
			return

		if self.mMoveFlag :
			LOG_TRACE( '[ChannelList] pass, edit mode and move' )
			return

		self.GetFocusId( )
		if self.mFocusId != E_CONTROL_ID_LIST_CHANNEL_LIST :
			LOG_TRACE( '[ChannelList] pass, opened slide' )
			return

		if self.mUserSlidePos.mMain != aReqMode :
			if ( aReqMode == E_SLIDE_MENU_SATELLITE and self.mListSatellite and len( self.mListSatellite ) > 0 ) or \
			   ( aReqMode == E_SLIDE_MENU_FTACAS and self.mListCasList and len( self.mListCasList ) > 0 ) or \
			   ( aReqMode == E_SLIDE_MENU_PROVIDER and self.mListProvider and len( self.mListProvider ) > 0 ) or \
			   ( aReqMode == E_SLIDE_MENU_FAVORITE and self.mListFavorite and len( self.mListFavorite ) > 0 ) :
				self.mUserSlidePos.mMain = aReqMode
				self.mUserSlidePos.mSub = 0
				self.mCtrlListMainmenu.selectItem( aReqMode )
				self.mCtrlListSubmenu.selectItem( 0 )
				time.sleep( 0.2 )
				self.SubMenuAction( E_SLIDE_ACTION_MAIN, aReqMode )
				self.SubMenuAction( E_SLIDE_ACTION_SUB, E_SLIDE_ACTION_SORT, True )

		else :
			self.UpdateShortCutGroup( )

