from pvr.gui.WindowImport import *

E_CONTROL_ID_IMAGE_LISTMODE				= 10
E_CONTROL_ID_LABEL_CHANNEL_PATH			= 21
E_CONTROL_ID_GROUP_OPT					= 500
E_CONTROL_ID_BUTTON_OPT					= 501
E_CONTROL_ID_LABEL_OPT1					= 502
E_CONTROL_ID_LABEL_OPT2					= 503
E_CONTROL_ID_GROUP_MAINMENU 			= 100
E_CONTROL_ID_BUTTON_MAINMENU 			= 101
E_CONTROL_ID_LIST_MAINMENU				= 102
E_CONTROL_ID_GROUP_SUBMENU				= 9001
E_CONTROL_ID_LIST_SUBMENU				= 112
E_CONTROL_ID_RADIO_SERVICETYPE_TV		= 113
E_CONTROL_ID_RADIO_SERVICETYPE_RADIO	= 114
E_CONTROL_ID_GROUP_CHANNEL_LIST			= 49
E_CONTROL_ID_LIST_CHANNEL_LIST			= 50
E_CONTROL_ID_LABEL_CHANNEL_NAME			= 303
E_CONTROL_ID_LABEL_EPG_NAME				= 304
E_CONTROL_ID_LABEL_EPG_TIME				= 305
E_CONTROL_ID_PROGRESS_EPG				= 306
E_CONTROL_ID_LABEL_LONGITUDE_INFO		= 307
E_CONTROL_ID_LABEL_CAREER_INFO			= 308
E_CONTROL_ID_GROUP_LOCKED_INFO			= 309
E_CONTROL_ID_GROUP_COMPONENT_DATA		= 310
E_CONTROL_ID_GROUP_COMPONENT_DOLBY		= 311
E_CONTROL_ID_GROUP_COMPONENT_HD			= 312
E_CONTROL_ID_LABEL_SELECT_NUMBER		= 401
E_CONTROL_ID_GROUP_HELPBOX				= 600

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
FLAG_CLOCKMODE_ADMYHM   = 1
FLAG_CLOCKMODE_AHM      = 2
FLAG_CLOCKMODE_HMS      = 3
FLAG_CLOCKMODE_HHMM     = 4
FLAG_MODE_JUMP         = True

#slide index
E_SLIDE_ACTION_MAIN     = 0
E_SLIDE_ACTION_SUB      = 1
E_SLIDE_ALLCHANNEL      = 0
E_SLIDE_MENU_SATELLITE  = 1
E_SLIDE_MENU_FTACAS     = 2
E_SLIDE_MENU_FAVORITE   = 3
E_SLIDE_MENU_BACK       = 5

E_CONTROL_FOCUSED       = 9991
E_SLIDE_CLOSE           = 9999

#string tag
E_TAG_ENABLE  = 'enable'
E_TAG_VISIBLE = 'visible'
E_TAG_SELECT  = 'select'
E_TAG_LABEL   = 'label'
E_TAG_TRUE    = 'True'
E_TAG_FALSE   = 'False'
E_TAG_SET_SELECT_POSITION = 'selectItem'
E_TAG_GET_SELECT_POSITION = 'getItem'
E_TAG_ADD_ITEM = 'addItem'

#xml property name
E_XML_PROPERTY_SUBTITLE  = 'HasSubtitle'
E_XML_PROPERTY_DOLBY     = 'HasDolby'
E_XML_PROPERTY_HD        = 'HasHD'
E_XML_PROPERTY_MARK      = 'mark'
E_XML_PROPERTY_CAS       = 'icas'
E_XML_PROPERTY_LOCK      = 'lock'
E_XML_PROPERTY_RECORDING = 'rec'
E_XML_PROPERTY_SKIP      = 'skip'
E_XML_PROPERTY_EDITINFO  = 'helpbox'

#dialog menu
CONTEXT_ACTION_LOCK				= 1 
CONTEXT_ACTION_UNLOCK			= 2
CONTEXT_ACTION_SKIP				= 3
CONTEXT_ACTION_UNSKIP			= 4
CONTEXT_ACTION_DELETE			= 5
CONTEXT_ACTION_MOVE				= 6
CONTEXT_ACTION_ADD_TO_FAV		= 7
CONTEXT_ACTION_CREATE_GROUP_FAV	= 10
CONTEXT_ACTION_RENAME_FAV		= 11
CONTEXT_ACTION_DELETE_FAV		= 12
CONTEXT_ACTION_ADD_TO_CHANNEL	= 13
CONTEXT_ACTION_SAVE_EXIT		= 14
CONTEXT_ACTION_MENU_EDIT_MODE	= 20
CONTEXT_ACTION_MENU_DELETEALL	= 22

#xml control id
E_CONTROL_ID_SCROLLBAR = 61

class ChannelListWindow( BaseWindow ) :

	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )

		#submenu list
		self.mListAllChannel= []
		self.mListSatellite = []
		self.mListCasList   = []
		self.mListFavorite  = []
		self.mElisZappingModeInfo = None
		self.mElisSetZappingModeInfo = None
		self.mLastMainSlidePosition = 0
		self.mLastSubSlidePosition = 0
		self.mSelectMainSlidePosition = 0
		self.mSelectSubSlidePosition = 0
		self.mCurrentPosition = 0
		self.mLastChannel = None
		self.mListItems = None

		self.mEventId = 0
		self.mLocalTime = 0
		self.mAsyncTuneTimer = None

		self.mPropertyAge = 0
		self.mPropertyPincode = -1
		self.mPincodeEnter = FLAG_MASK_NONE
		self.mViewMode = WinMgr.WIN_ID_CHANNEL_LIST_WINDOW


	"""
	def __del__(self):
		LOG_TRACE( 'destroyed ChannelList' )

		# end thread
		self.mEnableLocalThread = False

 
	def onAction(self, aAction):
		id = aAction.getId( )
		
		if id == Action.ACTION_PREVIOUS_MENU or id == Action.ACTION_PARENT_DIR:
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_NULLWINDOW )			

		elif id == 104 : #scroll up
			xbmc.executebuiltin('XBMC.ReloadSkin()')
		elif id == Action.ACTION_SELECT_ITEM : 
			xbmc.executebuiltin('XBMC.ReloadSkin()')

	def SetAutomaticHide( self, aHide=True ) :
		self.mAutomaticHide = aHide

	def GetAutomaticHide( self ) :
		return self.mAutomaticHide
	"""

	def onInit(self):
		LOG_TRACE( 'Enter' )

		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		LOG_TRACE( 'winID[%d]'% self.mWinId)

		#starttime = time.time( )
		#print '==================== TEST TIME[ONINIT] START[%s]'% starttime

		self.mCtrlImageListMode          = self.getControl( E_CONTROL_ID_IMAGE_LISTMODE )

		#header
		self.mCtrlLabelChannelPath       = self.getControl( E_CONTROL_ID_LABEL_CHANNEL_PATH )
		self.mCtrlGroupOpt               = self.getControl( E_CONTROL_ID_GROUP_OPT )
		self.mCtrlButtonOpt              = self.getControl( E_CONTROL_ID_BUTTON_OPT )
		self.mCtrlLabelOpt1              = self.getControl( E_CONTROL_ID_LABEL_OPT1 )
		self.mCtrlLabelOpt2              = self.getControl( E_CONTROL_ID_LABEL_OPT2 )

		#main menu
		self.mCtrlGroupMainmenu          = self.getControl( E_CONTROL_ID_GROUP_MAINMENU )
		self.mCtrlButtonMainMenu         = self.getControl( E_CONTROL_ID_BUTTON_MAINMENU )
		self.mCtrlListMainmenu           = self.getControl( E_CONTROL_ID_LIST_MAINMENU )

		#sub menu list
		self.mCtrlGroupSubmenu           = self.getControl( E_CONTROL_ID_GROUP_SUBMENU )
		self.mCtrlListSubmenu            = self.getControl( E_CONTROL_ID_LIST_SUBMENU )

		#sub menu btn
		self.mCtrlRadioServiceTypeTV     = self.getControl( E_CONTROL_ID_RADIO_SERVICETYPE_TV )
		self.mCtrlRadioServiceTypeRadio  = self.getControl( E_CONTROL_ID_RADIO_SERVICETYPE_RADIO )

		#ch list
		self.mCtrlGroupCHList            = self.getControl( E_CONTROL_ID_GROUP_CHANNEL_LIST )
		self.mCtrlListCHList             = self.getControl( E_CONTROL_ID_LIST_CHANNEL_LIST )

		#info
		self.mCtrlLabelChannelName       = self.getControl( E_CONTROL_ID_LABEL_CHANNEL_NAME )
		self.mCtrlLabelEPGName           = self.getControl( E_CONTROL_ID_LABEL_EPG_NAME )
		self.mCtrlLabelEPGTime           = self.getControl( E_CONTROL_ID_LABEL_EPG_TIME )
		self.mCtrlProgress               = self.getControl( E_CONTROL_ID_PROGRESS_EPG )
		self.mCtrlLabelLongitudeInfo     = self.getControl( E_CONTROL_ID_LABEL_LONGITUDE_INFO )
		self.mCtrlLabelCareerInfo        = self.getControl( E_CONTROL_ID_LABEL_CAREER_INFO )
		self.mCtrlLabelLockedInfo        = self.getControl( E_CONTROL_ID_GROUP_LOCKED_INFO )
		self.mCtrlGroupComponentData     = self.getControl( E_CONTROL_ID_GROUP_COMPONENT_DATA )
		self.mCtrlGroupComponentDolby    = self.getControl( E_CONTROL_ID_GROUP_COMPONENT_DOLBY )
		self.mCtrlGroupComponentHD       = self.getControl( E_CONTROL_ID_GROUP_COMPONENT_HD )
		self.mCtrlLabelSelectItem        = self.getControl( E_CONTROL_ID_LABEL_SELECT_NUMBER )
		#self.mCtrlGroupHelpBox           = self.getControl( E_CONTROL_ID_GROUP_HELPBOX )


		self.mIsSelect = False
		self.mIsMark = True
		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		self.mChannelListServiceType = ElisEnum.E_SERVICE_TYPE_INVALID
		self.mChannelListSortMode = ElisEnum.E_SORT_BY_DEFAULT
		self.mZappingMode = ElisEnum.E_MODE_ALL
		self.mZappingName = ''
		self.mChannelList = []
		self.mRecCount = 0
		self.mRecChannel1 = []
		self.mRecChannel2 = []
		self.mNavEpg = None
		self.mNavChannel = None
		self.mCurrentChannel = None
		self.mSlideOpenFlag = False
		self.mFlag_EditChanged = False
		self.mFlag_ModeChanged = False
		self.mFlag_DeleteAll = False

		#edit mode
		self.mIsSave = FLAG_MASK_NONE
		self.mMarkList = []
		self.mEditFavorite = []
		self.mEditChannelList = []
		self.mMoveFlag = False
		self.mMoveItem = []

		self.SetPipScreen( )

		#self.UpdateControlGUI( E_CONTROL_ID_BUTTON_DELETEALL, MR_LANG('Delete All Channel') )

		self.mPropertyAge = ElisPropertyEnum( 'Age Limit', self.mCommander ).GetProp( )
		self.mPropertyPincode = ElisPropertyInt( 'PinCode', self.mCommander ).GetProp( )
		if self.mDataCache.mCacheReload :
			self.mListItems = None
			self.mDataCache.mCacheReload = False

		#initialize get cache
		zappingmode = None
		zappingmode = self.mDataCache.Zappingmode_GetCurrent( )
		if zappingmode :
			self.mElisSetZappingModeInfo = deepcopy( zappingmode )
		else :
			self.mElisSetZappingModeInfo = ElisIZappingMode()


		self.mEventBus.Register( self )

		#run thread
		self.LoadingThread( )
		self.mEnableLocalThread = True
		self.EPGProgressThread( )

		self.mAsyncTuneTimer = None
		#endtime = time.time( )
		#print '==================== TEST TIME[ONINIT] END[%s] loading[%s]'% (endtime, endtime-starttime )


	def onAction(self, aAction):
		id = aAction.getId( )

		self.GlobalAction( id )

		if id >= Action.REMOTE_0 and id <= Action.REMOTE_9:
			self.SetTuneByNumber( id-Action.REMOTE_0 )

		elif id >= Action.ACTION_JUMP_SMS2 and id <= Action.ACTION_JUMP_SMS9 :
			rKey = id - (Action.ACTION_JUMP_SMS2 - 2)
			self.SetTuneByNumber( rKey )

		elif id == Action.ACTION_PREVIOUS_MENU or id == Action.ACTION_PARENT_DIR:
			#LOG_TRACE( 'goto previous menu' )
			self.SetGoBackWindow( )

		elif id == Action.ACTION_SELECT_ITEM:
			self.GetFocusId( )
			#LOG_TRACE( 'item select, action ID[%s]'% id )

			if self.mFocusId == E_CONTROL_ID_LIST_MAINMENU :
				position = self.mCtrlListMainmenu.getSelectedPosition( )
				self.SubMenuAction( E_SLIDE_ACTION_MAIN, position )

		elif id == Action.ACTION_MOVE_RIGHT :
			pass

		elif id == Action.ACTION_MOVE_LEFT :
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_LIST_CHANNEL_LIST :
				self.GetSlideMenuHeader( FLAG_SLIDE_OPEN )
				self.mSlideOpenFlag = True

		elif id == Action.ACTION_MOVE_UP or id == Action.ACTION_MOVE_DOWN or \
			 id == Action.ACTION_PAGE_UP or id == Action.ACTION_PAGE_DOWN :
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_LIST_CHANNEL_LIST or self.mFocusId == E_CONTROL_ID_SCROLLBAR :
				if self.mMoveFlag :
					self.SetEditChanneltoMove( FLAG_OPT_MOVE_UPDOWN, id )
					return

				else :
					self.RestartAsyncEPG( )

			if self.mFocusId == E_CONTROL_ID_LIST_MAINMENU :
				position = self.mCtrlListMainmenu.getSelectedPosition( )
				self.SubMenuAction( E_SLIDE_ACTION_MAIN, position )

			elif self.mFocusId == self.mCtrlButtonOpt :
				self.UpdateControlGUI( E_SLIDE_CLOSE )


		elif id == Action.ACTION_CONTEXT_MENU :
			self.ShowContextMenu( )


		elif id == Action.ACTION_STOP :
			if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :

				status = self.mDataCache.Player_GetStatus()
				if status.mMode :
					self.mDataCache.SetKeyDisabled( False )
					ret = self.mDataCache.Player_Stop()

					iChannel = self.mDataCache.Channel_GetCurrent( )
					LOG_TRACE('-------------------iChannel[%s]'% iChannel )
					if iChannel :
						self.mNavChannel = iChannel
						self.mCurrentChannel = iChannel.mNumber

					self.mIsSelect == True
					self.UpdateChannelAndEPG()
				else :
					self.ShowRecordingStopDialog()

		elif id == Action.ACTION_MBOX_XBMC :
			self.SetGoBackWindow( WinMgr.WIN_ID_MEDIACENTER )

		elif id == Action.ACTION_MBOX_ARCHIVE :
			if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
				self.mDataCache.mSetFromParentWindow = WinMgr.WIN_ID_NULLWINDOW
				self.SetGoBackWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW )

		elif id == Action.ACTION_SHOW_INFO :
			if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
				self.mDataCache.mSetFromParentWindow = WinMgr.WIN_ID_NULLWINDOW
				self.SetGoBackWindow( WinMgr.WIN_ID_EPG_WINDOW )

		elif id == Action.ACTION_MBOX_RECORD :
			if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
				if self.mChannelList or len(self.mChannelList) > 0 :
					self.ShowRecordingStartDialog()




		elif id == 13: #'x'
			#this is test
			LOG_TRACE( 'language[%s]'% xbmc.getLanguage( ) )


	def onClick(self, aControlId):
		#LOG_TRACE( 'onclick focusID[%d]'% aControlId )

		if aControlId == E_CONTROL_ID_LIST_CHANNEL_LIST :
			if self.mViewMode == WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW :
				try:
					if self.mMoveFlag :
						self.SetEditChanneltoMove( FLAG_OPT_MOVE_OK )
						return

					#Mark mode
					if self.mIsMark == True :
						if self.mChannelList :
							idx = self.mCtrlListCHList.getSelectedPosition( )
							self.SetEditMarkupGUI( idx )

							self.UpdateControlGUI( E_CONTROL_FOCUSED, E_CONTROL_ID_GROUP_CHANNEL_LIST )
							self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, idx+1, E_TAG_SET_SELECT_POSITION )
							self.UpdateControlGUI( E_CONTROL_ID_LABEL_SELECT_NUMBER, str('%s'% (idx+1) ) )

				except Exception, e:
					LOG_TRACE( 'Error except[%s]'% e )

			else :
				if self.mChannelList :
					self.SetChannelTune( )

		elif aControlId == E_CONTROL_ID_BUTTON_MAINMENU or aControlId == E_CONTROL_ID_LIST_MAINMENU :
			#slide main view
			pass

		elif aControlId == E_CONTROL_ID_LIST_SUBMENU :
			#list action
			position = self.mZappingMode
			self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )

			self.UpdateControlGUI( E_SLIDE_CLOSE )

		elif aControlId == E_CONTROL_ID_BUTTON_OPT:
			self.ShowContextMenu( )

		elif aControlId == E_CONTROL_ID_RADIO_SERVICETYPE_TV:
			self.SetModeChanged( FLAG_MODE_TV )

		elif aControlId == E_CONTROL_ID_RADIO_SERVICETYPE_RADIO:
			self.SetModeChanged( FLAG_MODE_RADIO )


	def onFocus(self, controlId):
		#LOG_TRACE( 'control %d' % controlId )
		pass


	@RunThread
	def LoadingThread( self ):
		self.ShowRecordingInfo( )

		#initialize get channel list
		self.InitSlideMenuHeader( )

		try :
			label = ''
			#first get is used cache, reason by fast load
			iChannel = self.mDataCache.Channel_GetCurrent( )

			status = self.mDataCache.Player_GetStatus()
			if status.mMode == ElisEnum.E_MODE_TIMESHIFT :
				if iChannel :
					self.mNavChannel = iChannel
					self.mCurrentChannel = iChannel.mNumber
					label = 'TIMESHIFT - P%04d.%s' %(iChannel.mNumber, iChannel.mName )

			elif status.mMode == ElisEnum.E_MODE_PVR :
				if self.mDataCache.mRecInfo :
					label = 'PVR - P%04d.%s' %(self.mDataCache.mRecInfo.mChannelNo, self.mDataCache.mRecInfo.mChannelName )
			else :
				#Live
				if iChannel :
					self.mNavChannel = iChannel
					self.mCurrentChannel = iChannel.mNumber

					strType = self.UpdateServiceType( iChannel.mServiceType )
					label = '%s - %s'% (strType, iChannel.mName)
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, label )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		self.InitChannelList( )

		#clear label
		self.ResetLabel( )

		#initialize get epg event
		#self.InitEPGEvent( )
		try :
			iEPG = None
			iEPG = self.mDataCache.Epgevent_GetPresent()
			if iEPG and iEPG.mEventName != 'No Name':
				self.mNavEpg = iEPG

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		self.UpdateChannelAndEPG( )


	def SetDeleteAll( self ) :
		ret = E_DIALOG_STATE_NO

		#ask save question
		head =  MR_LANG('Confirm')
		line1 = MR_LANG('Delete All Channel')

		GuiLock2( True )
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( head, line1 )
		dialog.doModal( )
		GuiLock2( False )

		ret = dialog.IsOK( )

		#answer is yes
		if ret == E_DIALOG_STATE_YES :
			isBackup = self.mDataCache.Channel_Backup( )
			isDelete = self.mDataCache.Channel_DeleteAll( )
			if isDelete :
				self.mDataCache.Player_AVBlank( True, False )
				self.mDataCache.Channel_InvalidateCurrent( )
				self.mDataCache.Frontdisplay_SetMessage('NoChannel')
				self.mFlag_DeleteAll = True

		return ret


	def SetModeChanged( self, aType = FLAG_MODE_TV) :
		if self.mChannelListServiceType != aType :
			self.mFlag_EditChanged = True
			self.mFlag_ModeChanged = True
			self.mChannelListServiceType = aType
			self.mElisZappingModeInfo.mServiceType = aType

			self.InitSlideMenuHeader( FLAG_ZAPPING_CHANGE )
			self.RefreshSlideMenu( E_SLIDE_ALLCHANNEL, ElisEnum.E_MODE_ALL, True )

			self.mCtrlListCHList.reset( )
			self.InitChannelList( )
			self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, 0, E_TAG_SET_SELECT_POSITION )
			self.mFlag_EditChanged = False

			#### data cache re-load ####
			self.mDataCache.LoadChannelList( FLAG_ZAPPING_CHANGE, aType, ElisEnum.E_MODE_ALL, ElisEnum.E_SORT_BY_NUMBER  )

			if aType == FLAG_MODE_TV :
				self.mCurrentChannel = None

			elif aType == FLAG_MODE_RADIO :
				if self.mCurrentChannel :
					self.mLastChannel = self.mCurrentChannel

			#initialize get epg event
			self.mIsSelect = False
			self.InitEPGEvent( )


		if aType == FLAG_MODE_TV :
			self.UpdateControlGUI( E_CONTROL_ID_RADIO_SERVICETYPE_TV,   True, E_TAG_SELECT )
			self.UpdateControlGUI( E_CONTROL_ID_RADIO_SERVICETYPE_RADIO,False, E_TAG_SELECT )
		else :
			self.UpdateControlGUI( E_CONTROL_ID_RADIO_SERVICETYPE_TV,   False, E_TAG_SELECT )
			self.UpdateControlGUI( E_CONTROL_ID_RADIO_SERVICETYPE_RADIO,True, E_TAG_SELECT )

		self.UpdateControlGUI( E_SLIDE_CLOSE )



	def SetGoBackEdit( self ) :
		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			self.mViewMode = WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW

			try :
				self.mEventBus.Deregister( self )
				self.mDataCache.SetSkipChannelView( True )
				self.ReloadChannelList( )

				#clear label
				self.ResetLabel( )
				self.UpdateChannelAndEPG( )

				ret = self.mDataCache.Channel_Backup( )
				#LOG_TRACE( 'channelBackup[%s]'% ret )


			except Exception, e :
				LOG_TRACE( 'Error except[%s]'% e )

		else :
			self.SetGoBackWindow( )


	def SetGoBackWindow( self, aGoToWindow = None ) :
		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			ret = False
			ret = self.SaveSlideMenuHeader( )
			if ret != E_DIALOG_STATE_CANCEL :
				self.mEnableLocalThread = False
				self.mCtrlListCHList.reset( )
				self.Close( )

				if aGoToWindow :
					WinMgr.GetInstance( ).ShowWindow( aGoToWindow )
				else :
					WinMgr.GetInstance().CloseWindow( )

			LOG_TRACE( 'go out Cancel' )

		else :
			ret = False
			ret = self.SaveEditList( )
			if ret != E_DIALOG_STATE_CANCEL :
				self.mViewMode = WinMgr.WIN_ID_CHANNEL_LIST_WINDOW
				self.mEventBus.Register( self )
				self.mDataCache.SetSkipChannelView( False )
				self.ReloadChannelList( )
				self.mFlag_EditChanged = False
				self.mMoveFlag = False

				#initialize get epg event
				self.mIsSelect = False
				self.InitEPGEvent( )

				#clear label
				self.ResetLabel( )
				self.UpdateChannelAndEPG( )


	@GuiLock
	def onEvent(self, aEvent):
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			#LOG_TRACE('Receive Event[%s]'% aEvent.getName() )

			if aEvent.getName( ) == ElisEventCurrentEITReceived.getName( ) :

				if self.mNavChannel == None:
					return -1

				if self.mNavChannel.mSid != aEvent.mSid or self.mNavChannel.mTsid != aEvent.mTsid or self.mNavChannel.mOnid != aEvent.mOnid :
					return -1
		
				if aEvent.mEventId != self.mEventId :
					if self.mIsSelect == True :
						#on select, clicked
						iEPG = None
						sid  = self.mNavChannel.mSid
						tsid = self.mNavChannel.mTsid
						onid = self.mNavChannel.mOnid
						iEPG = self.mDataCache.Epgevent_GetCurrent( sid, tsid, onid )
						if iEPG == None or iEPG.mError != 0 :
							return -1

						self.mEventId = aEvent.mEventId

						if not self.mNavEpg or \
						   iEPG.mEventId != self.mNavEpg.mEventId or \
						   iEPG.mSid != self.mNavEpg.mSid or \
						   iEPG.mTsid != self.mNavEpg.mTsid or \
						   iEPG.mOnid != self.mNavEpg.mOnid :

							#LOG_TRACE('epg DIFFER')
							self.mNavEpg = iEPG

							#update label
							self.ResetLabel( )
							self.UpdateChannelAndEPG( )

			elif aEvent.getName() == ElisEventRecordingStarted.getName() or \
				 aEvent.getName() == ElisEventRecordingStopped.getName() :
				self.mRecChannel1 = []
				self.mRecChannel2 = []
				#LOG_TRACE('<<<<<<<<<<<<<<<<<<<<< ChannelList <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
				self.ShowRecordingInfo( )
				self.ReloadChannelList( )
				self.mFlag_EditChanged = False
				self.mMoveFlag = False

			if aEvent.getName() == ElisEventPlaybackEOF.getName() :
				if aEvent.mType == ElisEnum.E_EOF_END :
					#LOG_TRACE( 'EventRecv EOF_STOP' )
					xbmc.executebuiltin('xbmc.Action(stop)')

			elif aEvent.getName() == ElisEventChannelChangeResult.getName() :
				ch = self.mDataCache.Channel_GetCurrent( )
				isLimit = False
				if self.mNavEpg :
					isLimit = AgeLimit( self.mPropertyAge, self.mNavEpg.mAgeRating )

				if ch.mLocked or isLimit :
					WinMgr.GetInstance().GetWindow( WinMgr.WIN_ID_NULLWINDOW ).PincodeDialogLimit( self.mPropertyPincode )

		else:
			LOG_TRACE( 'channellist winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId( ) ) )


	def SetChannelTune( self, aJumpNumber = None ) :
		#Turn in
		self.mIsSelect = True

		if aJumpNumber:
			#detected to jump focus
			chindex = 0
			for ch in self.mChannelList:
				if ch.mNumber == aJumpNumber :
					self.mNavChannel = ch
					self.ResetLabel( )
					self.UpdateChannelAndEPG( )
					break
				chindex += 1

			if self.mChannelList == None:
				label = MR_LANG('Empty Channels')
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, label )
				return 

			self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, chindex, E_TAG_SET_SELECT_POSITION )
			xbmc.sleep( 50 )

			#chNumber = aJumpNumber
			"""
			iChannel = ElisIChannel( )
			iChannel.reset()
			iChannel.mNumber = int(aJumpNumber)
			iChannel.mServiceType = deepcopy(self.mChannelListServiceType)
			"""
			iChannel = self.mChannelList[int(aJumpNumber)]

			#LOG_TRACE('JumpChannel: num[%s] type[%s]'% (iChannel.mNumber, iChannel.mServiceType) )

		else:
			if self.mChannelList == None:
				label = MR_LANG('Empty Channels')
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, label )
				return 

			idx = self.mCtrlListCHList.getSelectedPosition( )
			iChannel = self.mChannelList[idx]


		if self.mFlag_ModeChanged :
			self.mFlag_ModeChanged = False
			isBlank = False
			if iChannel.mServiceType == FLAG_MODE_RADIO : 	isBlank = True
			else : 											isBlank = False
			self.mDataCache.Player_VideoBlank( isBlank, False )


		if self.mDataCache.mStatusIsArchive :
			self.mDataCache.mStatusIsArchive = False
			self.mDataCache.Player_Stop()

		ret = False
		ret = self.mDataCache.Channel_SetCurrent( iChannel.mNumber, iChannel.mServiceType )

		#LOG_TRACE( 'MASK[%s] ret[%s]'% (self.mPincodeEnter, ret) )
		if ret == True :
			#if self.mCurrentChannel == iChannel.mNumber :
			if self.mDataCache.mOldChannel.mNumber == iChannel.mNumber and \
			   self.mDataCache.mOldChannel.mServiceType == iChannel.mServiceType :
				ret = False
				ret = self.SaveSlideMenuHeader( )
				if ret != E_DIALOG_STATE_CANCEL :
					self.mEnableLocalThread = False
					#self.EPGProgressThread( ).join( )
					self.Close( )

					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE, WinMgr.WIN_ID_NULLWINDOW )				
					return

				LOG_TRACE( 'go out Cancel' )

		ch = None
		ch = self.mDataCache.Channel_GetCurrent( )
		if ch :
			self.mNavChannel = ch
			self.mCurrentChannel = self.mNavChannel.mNumber
			self.mCurrentPosition = self.mCtrlListCHList.getSelectedPosition( )
			pos = self.mCurrentPosition + 1
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_SELECT_NUMBER, str('%s'% pos ) )
			#LOG_TRACE('chinfo: num[%s] type[%s] name[%s] pos[%s]'% (ch.mNumber, ch.mServiceType, ch.mName, pos) )

			self.ResetLabel( )
			self.UpdateChannelAndEPG( )


	def RefreshSlideMenu( self, aMainIndex = E_SLIDE_ALLCHANNEL, aSubIndex = ElisEnum.E_MODE_ALL, aForce = None ) :
		self.mCtrlListMainmenu.selectItem( aMainIndex )
		xbmc.sleep( 50 )
		self.SubMenuAction( E_SLIDE_ACTION_MAIN, aMainIndex, aForce )

		self.mCtrlListSubmenu.selectItem( 0 )
		xbmc.sleep( 50 )
		self.SubMenuAction( E_SLIDE_ACTION_SUB, aSubIndex, aForce )


	@GuiLock
	def SubMenuAction(self, aAction, aMenuIndex, aForce = None):
		if self.mFlag_DeleteAll :
			return

		retPass = False

		if aAction == E_SLIDE_ACTION_MAIN:
			testlistItems = []
			if aMenuIndex == 0 :
				self.mZappingMode = ElisEnum.E_MODE_ALL
				for itemList in range( len(self.mListAllChannel) ) :
					testlistItems.append( xbmcgui.ListItem(self.mListAllChannel[itemList]) )

			elif aMenuIndex == 1 :
				self.mZappingMode = ElisEnum.E_MODE_SATELLITE
				if self.mListSatellite :
					for itemClass in self.mListSatellite:
						ret = GetSelectedLongitudeString( itemClass.mLongitude, itemClass.mName )
						testlistItems.append( xbmcgui.ListItem(ret) )

			elif aMenuIndex == 2 :
				self.mZappingMode = ElisEnum.E_MODE_CAS
				if self.mListCasList :
					for itemClass in self.mListCasList:
						ret = '%s(%s)'% ( itemClass.mName, itemClass.mChannelCount )
						testlistItems.append( xbmcgui.ListItem(ret) )

			elif aMenuIndex == 3 :
				self.mZappingMode = ElisEnum.E_MODE_FAVORITE
				if self.mListFavorite :
					for itemClass in self.mListFavorite:
						testlistItems.append( xbmcgui.ListItem(itemClass.mGroupName) )
				else:
					testlistItems.append( xbmcgui.ListItem( MR_LANG('None') ) )

			if testlistItems != [] :
				#submenu update
				self.mCtrlListSubmenu.reset( )
				self.mCtrlListSubmenu.addItems( testlistItems )

				if aMenuIndex == self.mSelectMainSlidePosition :
					self.mCtrlListSubmenu.selectItem( self.mSelectSubSlidePosition )

		elif aAction == E_SLIDE_ACTION_SUB:
			if aForce == None and self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
				if self.mSelectMainSlidePosition == self.mCtrlListMainmenu.getSelectedPosition( ) and \
				   self.mSelectSubSlidePosition == self.mCtrlListSubmenu.getSelectedPosition( ) :
					LOG_TRACE( 'aready select!!!' )
					return

			zappingName = ''
			if aMenuIndex == ElisEnum.E_MODE_ALL :
				position   = self.mCtrlListSubmenu.getSelectedPosition( )
				if position == 0:
					sortingMode = ElisEnum.E_SORT_BY_NUMBER
				elif position == 1:
					sortingMode = ElisEnum.E_SORT_BY_ALPHABET
				elif position == 2:
					sortingMode = ElisEnum.E_SORT_BY_HD

				self.mChannelListSortMode = sortingMode
				retPass = self.GetChannelList( self.mChannelListServiceType, self.mZappingMode, sortingMode, 0, 0, 0, '' )

			elif aMenuIndex == ElisEnum.E_MODE_SATELLITE:
				if self.mListSatellite :
					idx_Satellite = self.mCtrlListSubmenu.getSelectedPosition( )
					item = self.mListSatellite[idx_Satellite]
					zappingName = item.mName
					retPass = self.GetChannelList( self.mChannelListServiceType, self.mZappingMode, self.mChannelListSortMode, item.mLongitude, item.mBand, 0, '' )
					#LOG_TRACE( 'cmd[channel_GetListBySatellite] idx_Satellite[%s] mLongitude[%s] band[%s]'% ( idx_Satellite, item.mLongitude, item.mBand ) )

			elif aMenuIndex == ElisEnum.E_MODE_CAS:
				if self.mListCasList :
					idxFtaCas = self.mCtrlListSubmenu.getSelectedPosition( )
					zappingName = self.mListCasList[idxFtaCas].mName
					if idxFtaCas == 0 :
						caid = ElisEnum.E_FTA_CHANNEL
					elif idxFtaCas == 1 :
						caid = ElisEnum.E_MEDIAGUARD
					elif idxFtaCas == 2 :
						caid = ElisEnum.E_VIACCESS
					elif idxFtaCas == 3 :
						caid = ElisEnum.E_NAGRA
					elif idxFtaCas == 4 :
						caid = ElisEnum.E_IRDETO
					elif idxFtaCas == 5 :
						caid = ElisEnum.E_CRYPTOWORKS
					elif idxFtaCas == 6 :
						caid = ElisEnum.E_BETADIGITAL
					elif idxFtaCas == 7 :
						caid = ElisEnum.E_NDS
					elif idxFtaCas == 8 :
						caid = ElisEnum.E_CONAX
					else :
						caid = ElisEnum.E_OTHERS

					retPass = self.GetChannelList( self.mChannelListServiceType, self.mZappingMode, self.mChannelListSortMode, 0, 0, caid, '' )
					#LOG_TRACE( 'cmd[channel_GetListByFTACas] idxFtaCas[%s]'% idxFtaCas )

			elif aMenuIndex == ElisEnum.E_MODE_FAVORITE:
				if self.mListFavorite : 
					idx_Favorite = self.mCtrlListSubmenu.getSelectedPosition( )
					item = self.mListFavorite[idx_Favorite]
					zappingName = item.mGroupName
					retPass = self.GetChannelList( self.mChannelListServiceType, self.mZappingMode, self.mChannelListSortMode, 0, 0, 0, item.mGroupName )
					#LOG_TRACE( 'cmd[channel_GetListByFavorite] idx_Favorite[%s] list_Favorite[%s]'% ( idx_Favorite, item.mGroupName ) )

			if retPass == False :
				return

			if self.mMoveFlag :
				#do not refresh UI
				return
			
			#channel list update
			self.mMarkList = []
			self.mListItems = None
			self.mCtrlListCHList.reset( )
			self.InitChannelList( )

			#path tree, Mainmenu/Submanu
			self.mSelectMainSlidePosition = self.mCtrlListMainmenu.getSelectedPosition( )
			self.mSelectSubSlidePosition = self.mCtrlListSubmenu.getSelectedPosition( )

			label = ''
			label1 = EnumToString('mode', self.mZappingMode)
			label2 = zappingName
			label3 = EnumToString('sort', self.mChannelListSortMode)

			if self.mZappingMode == ElisEnum.E_MODE_ALL :
				label = '%s [COLOR grey3]>[/COLOR] sort by %s'% (label1.upper( ),label3.title( ) )
			else :
				label = '%s [COLOR grey3]>[/COLOR] %s [COLOR grey2]/ sort by %s[/COLOR]'% (label1.upper( ),label2.title( ),label3.title( ) )
			self.mCtrlLabelChannelPath.setLabel( label )

			#current zapping backup
			#self.mDataCache.Channel_Backup( )


	def GetChannelList(self, aType, aMode, aSort, aLongitude, aBand, aCAid, aFavName ):
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


		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )
			return False

		return True


	def GetSlideMenuHeader(self, aMode) :
		idx1 = 0
		idx2 = 0

		if aMode == FLAG_SLIDE_INIT :

			#self.mElisZappingModeInfo.printdebug( )
			#LOG_TRACE( 'satellite[%s]'% ClassToList( 'convert', self.mListSatellite ) )
			#LOG_TRACE( 'ftacas[%s]'   % ClassToList( 'convert', self.mListCasList ) )
			#LOG_TRACE( 'favorite[%s]' % ClassToList( 'convert', self.mListFavorite ) )

			zInfo_mode = self.mElisZappingModeInfo.mMode
			zInfo_sort = self.mElisZappingModeInfo.mSortingMode
			zInfo_type = self.mElisZappingModeInfo.mServiceType
			zInfo_name = ''

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
				zInfo_name = self.mElisZappingModeInfo.mSatelliteInfo.mName

				for item in self.mListSatellite :
					if zInfo_name == item.mName :
						break
					idx2 += 1

			elif zInfo_mode == ElisEnum.E_MODE_CAS :
				idx1 = 2
				zInfo_name = self.mElisZappingModeInfo.mCasInfo.mName

				for item in self.mListCasList :
					if zInfo_name == item.mName :
						break
					idx2 += 1

			elif zInfo_mode == ElisEnum.E_MODE_FAVORITE :
				idx1 = 3
				zInfo_name = self.mElisZappingModeInfo.mFavoriteGroup.mGroupName
				if self.mListFavorite :
					for item in self.mListFavorite :
						if zInfo_name == item.mGroupName :
							break
						idx2 += 1

			self.mZappingName = zInfo_name
			self.mSelectMainSlidePosition = idx1
			self.mSelectSubSlidePosition = idx2

		elif aMode == FLAG_SLIDE_OPEN :
			idx1 = self.mSelectMainSlidePosition
			idx2 = self.mSelectSubSlidePosition


		self.mCtrlListMainmenu.selectItem( idx1 )
		self.SubMenuAction(E_SLIDE_ACTION_MAIN, idx1)
		self.mCtrlListSubmenu.selectItem( idx2 )
		#self.UpdateControlGUI( E_CONTROL_FOCUSED, E_CONTROL_ID_LIST_SUBMENU )


	def SaveSlideMenuHeader( self ) :
		"""
		LOG_TRACE( 'mode[%s] sort[%s] type[%s] mpos[%s] spos[%s]'% ( \
			self.mZappingMode,                \
			self.mChannelListSortMode,        \
			self.mChannelListServiceType,     \
			self.mSelectMainSlidePosition,    \
			self.mSelectSubSlidePosition      \
		)
		self.mListSatellite[self.mSelectSubSlidePosition].printdebug( )
		self.mListCasList[self.mSelectSubSlidePosition].printdebug( )
		self.mListFavorite[self.mSelectSubSlidePosition].printdebug( )
		"""

		changed = False
		answer = E_DIALOG_STATE_NO


		if self.mSelectMainSlidePosition != self.mLastMainSlidePosition or \
		   self.mSelectSubSlidePosition != self.mLastSubSlidePosition :
			changed = True

		if self.mElisSetZappingModeInfo.mServiceType != self.mChannelListServiceType :
			changed = True

		if self.mFlag_DeleteAll :
			changed = True

		#is change?
		if changed :
			try :
				GuiLock2( True )
				#ask save question
				label1 = EnumToString( 'mode', self.mZappingMode )
				label2 = self.mCtrlListSubmenu.getSelectedItem( ).getLabel( )

				head =  MR_LANG('Setting - to change zapping mode')
				line1 = '%s / %s'% ( label1.title( ), label2.title( ) )
				line2 = MR_LANG('Do you want to save channels?')
				posLine = abs( 100 - len(line1) )

				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( head, str('%s\n\n%s'% (line1.center(posLine), line2) ) )
				dialog.doModal( )
				GuiLock2( False )

				answer = dialog.IsOK( )

				#answer is yes
				if answer == E_DIALOG_STATE_YES :
					#re-configuration class
					self.mElisSetZappingModeInfo.reset( )
					self.mElisSetZappingModeInfo.mMode = self.mZappingMode
					self.mElisSetZappingModeInfo.mSortingMode = self.mChannelListSortMode
					self.mElisSetZappingModeInfo.mServiceType = self.mChannelListServiceType

					if self.mSelectMainSlidePosition == 1 :
						groupInfo = self.mListSatellite[self.mSelectSubSlidePosition]
						self.mElisSetZappingModeInfo.mSatelliteInfo = groupInfo
						
					elif self.mSelectMainSlidePosition == 2 :
						groupInfo = self.mListCasList[self.mSelectSubSlidePosition]
						self.mElisSetZappingModeInfo.mCasInfo = groupInfo
					
					elif self.mSelectMainSlidePosition == 3 :
						groupInfo = self.mListFavorite[self.mSelectSubSlidePosition]
						self.mElisSetZappingModeInfo.mFavoriteGroup = groupInfo

					iZappingList = []
					iZappingList.append( self.mElisSetZappingModeInfo )
					"""
					LOG_TRACE( '1. zappingMode[%s] sortMode[%s] serviceType[%s]'%  \
						( EnumToString('mode', self.mZappingMode),                 \
						  EnumToString('sort', self.mChannelListSortMode),         \
						  EnumToString('type', self.mChannelListServiceType) ) )
					LOG_TRACE( '2. zappingMode[%s] sortMode[%s] serviceType[%s]'%          \
						( EnumToString('mode', self.mElisSetZappingModeInfo.mMode),        \
						  EnumToString('sort', self.mElisSetZappingModeInfo.mSortingMode), \
						  EnumToString('type', self.mElisSetZappingModeInfo.mServiceType) ) )
					"""

					#save zapping mode
					self.mDataCache.Channel_Save( )
					ret = self.mDataCache.Zappingmode_SetCurrent( iZappingList )
					if ret :
						#### data cache re-load ####
						self.mDataCache.LoadZappingmode( )
						self.mDataCache.LoadZappingList( )
						self.mDataCache.LoadChannelList( )
						#LOG_TRACE ('===================== save yes: cache re-load')

				elif answer == E_DIALOG_STATE_NO :
					#zapping changed then will re-paint list items for cache
					self.mListItems = None
					if self.mFlag_DeleteAll : 
						#restore backup zapping
						isRestore = self.mDataCache.Channel_Restore( True )
						self.mDataCache.Channel_Save( )
						LOG_TRACE( 'Restore[%s]'% isRestore )


					#self.mDataCache.Channel_SetCurrent( self.mCurrentChannel.mNumber, self.mCurrentChannel.mServiceType )
					#### data cache re-load ####
					self.mDataCache.LoadZappingmode( )
					self.mDataCache.LoadZappingList( )
					self.mDataCache.LoadChannelList( )
					#LOG_TRACE ('===================== save no: cache re-load')

					iChannel = self.mDataCache.Channel_GetCurrent( )
					if iChannel.mNumber != self.mCurrentChannel or iChannel.mServiceType != self.mChannelListServiceType :
						self.mDataCache.Channel_SetCurrent( iChannel.mNumber, iChannel.mServiceType )

					if iChannel.mServiceType == ElisEnum.E_SERVICE_TYPE_TV or self.mFlag_DeleteAll == True :
						self.mDataCache.Player_AVBlank( False, False )

					elif iChannel.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
						self.mDataCache.Player_AVBlank( True, False )
						

			except Exception, e :
				LOG_TRACE( 'Error exception[%s]'% e )


		return answer


	def SaveEditList( self ) :
		answer = E_DIALOG_STATE_NO

		#is change?
		if self.mIsSave :
			#ask save question
			head =  MR_LANG('Confirm')
			line1 = MR_LANG('Do you want to save channels?')

			GuiLock2( True )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( head, line1 )
			dialog.doModal( )
			GuiLock2( False )

			answer = dialog.IsOK( )

			#answer is yes
			if answer == E_DIALOG_STATE_YES :
				self.mIsSave = FLAG_MASK_NONE
				self.mFlag_EditChanged = True
				isSave = self.mDataCache.Channel_Save( )

				#### data cache re-load ####
				self.mDataCache.SetSkipChannelView( False )
				self.mDataCache.LoadZappingmode( )
				self.mDataCache.LoadZappingList( )
				self.mDataCache.LoadChannelList( )
				LOG_TRACE ('save[%s] cache re-load'% isSave)

			elif answer == E_DIALOG_STATE_NO :
				self.mIsSave = FLAG_MASK_NONE
				isSave = self.mDataCache.Channel_Restore( True )
				self.mDataCache.Channel_Save( )
				LOG_TRACE( 'Restore[%s]'% isSave )

		return answer


	def InitSlideMenuHeader( self, aZappingMode = FLAG_ZAPPING_LOAD ) :
		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			#opt btn blind
			self.UpdateControlGUI( E_CONTROL_ID_IMAGE_LISTMODE, True )
			self.UpdateControlGUI( E_CONTROL_ID_GROUP_OPT, False )
			self.UpdateControlGUI( E_CONTROL_ID_RADIO_SERVICETYPE_TV, True, E_TAG_ENABLE )
			self.UpdateControlGUI( E_CONTROL_ID_RADIO_SERVICETYPE_RADIO, True, E_TAG_ENABLE )
			self.UpdateControlGUI( E_CONTROL_ID_GROUP_HELPBOX, E_TAG_FALSE )

		else :
			#opt btn visible
			self.UpdateControlGUI( E_CONTROL_ID_IMAGE_LISTMODE, False )
			self.UpdateControlGUI( E_CONTROL_ID_GROUP_OPT, True )
			self.UpdateControlGUI( E_CONTROL_ID_RADIO_SERVICETYPE_TV, False, E_TAG_ENABLE )
			self.UpdateControlGUI( E_CONTROL_ID_RADIO_SERVICETYPE_RADIO, False, E_TAG_ENABLE )
			self.UpdateControlGUI( E_CONTROL_ID_GROUP_HELPBOX, E_TAG_TRUE )

		if self.mFlag_DeleteAll :
			self.mZappingMode            = ElisEnum.E_MODE_ALL
			self.mChannelListSortMode    = ElisEnum.E_SORT_BY_DEFAULT
			self.mChannelListServiceType = ElisEnum.E_SERVICE_TYPE_TV

			self.mCtrlListSubmenu.reset( )
			testlistItems = []
			testlistItems.append(xbmcgui.ListItem( MR_LANG('None') ) )
			self.mCtrlListSubmenu.addItems( testlistItems )

			return

		#main/sub menu init
		GuiLock2( True )
		self.mCtrlListMainmenu.reset( )
		self.mCtrlListSubmenu.reset( )
		GuiLock2( False )

		#get last zapping mode
		if aZappingMode == FLAG_ZAPPING_LOAD :
			try:
				if self.mFlag_EditChanged :
					zappingMode = self.mDataCache.Zappingmode_GetCurrent( FLAG_ZAPPING_CHANGE )
				else :
					zappingMode = self.mDataCache.Zappingmode_GetCurrent( )

				if zappingMode != None and zappingMode.mError == 0 :
					self.mZappingMode            = zappingMode.mMode
					self.mChannelListSortMode    = zappingMode.mSortingMode
					self.mChannelListServiceType = zappingMode.mServiceType
					self.mElisZappingModeInfo    = zappingMode
				else :
					#set default
					self.mZappingMode            = ElisEnum.E_MODE_ALL
					self.mChannelListSortMode    = ElisEnum.E_SORT_BY_DEFAULT
					self.mChannelListServiceType = ElisEnum.E_SERVICE_TYPE_TV
					zappingMode                  = ElisIZappingMode()
					self.mElisZappingModeInfo    = zappingMode
					LOG_TRACE( 'Fail GetCurrent!!! [set default ZappingMode]' )

			except Exception, e:
				#set default
				self.mZappingMode            = ElisEnum.E_MODE_ALL
				self.mChannelListSortMode    = ElisEnum.E_SORT_BY_DEFAULT
				self.mChannelListServiceType = ElisEnum.E_SERVICE_TYPE_TV
				zappingMode                  = ElisIZappingMode()
				self.mElisZappingModeInfo    = zappingMode
				LOG_TRACE( 'Error exception[%s] [set default ZappingMode]'% e )


		list_Mainmenu = []
		list_Mainmenu.append( MR_LANG('All CHANNELS') )
		list_Mainmenu.append( MR_LANG('SATELLITE')    )
		list_Mainmenu.append( MR_LANG('FTA/CAS')      )
		list_Mainmenu.append( MR_LANG('FAVORITE')     )
		list_Mainmenu.append( MR_LANG('MODE') )
		#list_Mainmenu.append( MR_LANG('Back') )
		testlistItems = []
		for item in range( len(list_Mainmenu) ) :
			testlistItems.append( xbmcgui.ListItem(list_Mainmenu[item]) )

		self.mCtrlListMainmenu.addItems( testlistItems )


		#sort list, This is fixed
		self.mListAllChannel = []
		self.mListAllChannel.append( 'sort by Number' )
		self.mListAllChannel.append( 'sort by Alphabet' )
		self.mListAllChannel.append( 'sort by HD/SD' )

		try :
			if self.mFlag_EditChanged :
				#satellite list
				self.mListSatellite = self.mDataCache.Satellite_GetConfiguredList( )

				#FTA list
				self.mListCasList = self.mDataCache.Fta_cas_GetList( self.mChannelListServiceType )

				#Favorite list
				self.mListFavorite = self.mDataCache.Favorite_GetList(FLAG_ZAPPING_CHANGE, self.mChannelListServiceType )

			else:
				self.mListSatellite = self.mDataCache.Satellite_GetConfiguredList( )
				self.mListCasList = self.mDataCache.Fta_cas_GetList( )
				self.mListFavorite = self.mDataCache.Favorite_GetList( )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


		testlistItems = []
		if self.mZappingMode == ElisEnum.E_MODE_ALL :
			for item in range(len(self.mListAllChannel) ) :
				testlistItems.append(xbmcgui.ListItem(self.mListAllChannel[item]) )

		elif self.mZappingMode == ElisEnum.E_MODE_SATELLITE :
			if self.mListSatellite :
				for item in self.mListSatellite:
					ret = GetSelectedLongitudeString( item.mLongitude, item.mName )
					testlistItems.append(xbmcgui.ListItem(ret) )

		elif self.mZappingMode == ElisEnum.E_MODE_CAS :
			if self.mListCasList :
				for item in self.mListCasList:
					ret = '%s(%s)'% ( item.mName, item.mChannelCount )
					testlistItems.append(xbmcgui.ListItem( ret ) )

		elif self.mZappingMode == ElisEnum.E_MODE_FAVORITE :
			if self.mListFavorite :
				for item in self.mListFavorite:
					testlistItems.append(xbmcgui.ListItem( item.mGroupName ) )

		self.mCtrlListSubmenu.addItems( testlistItems )


		self.GetSlideMenuHeader( FLAG_SLIDE_INIT )
		self.mLastMainSlidePosition = self.mSelectMainSlidePosition
		self.mLastSubSlidePosition = self.mSelectSubSlidePosition

		#path tree, Mainmenu/Submanu
		label = ''
		label1 = EnumToString('mode', self.mZappingMode)
		label2 = self.mZappingName
		label3 = EnumToString('sort', self.mChannelListSortMode)
		if self.mZappingMode == ElisEnum.E_MODE_ALL :
			label = '%s [COLOR grey3]>[/COLOR] sort by %s'% ( label1.upper( ),label3.title( ) )
		else :
			label = '%s [COLOR grey3]>[/COLOR] %s [COLOR grey2]/ sort by %s[/COLOR]'% ( label1.upper( ),label2.title( ),label3.title( ) )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_PATH, label )

		#get channel list by last on zapping mode, sorting, service type
		self.mNavChannel = None
		self.mChannelList = None

		self.mChannelList = self.mDataCache.Channel_GetList( True, self.mChannelListServiceType, self.mZappingMode, self.mChannelListSortMode )

		"""
		LOG_TRACE('>>>>>>>>>>>>>>>>>>>>>>>>>flag_editChange[%s] len[%s] datachche[%s]'% (self.mFlag_EditChanged, len(self.mChannelList), len(self.mDataCache.mChannelList) ))
		lblSkip = 'skipped'
		if self.mDataCache.mSkip :
			lblSkip = 'all'
		LOG_TRACE( '>>>>>>>>>>>>>>>>>>>>>>>>>> table[%s]'% lblSkip)
		if self.mChannelList :
			LOG_TRACE( 'zappingMode[%s] sortMode[%s] serviceType[%s]'% \
				( EnumToString('mode', self.mZappingMode),             \
				  EnumToString('sort', self.mChannelListSortMode),     \
				  EnumToString('type', self.mChannelListServiceType) ) )
			LOG_TRACE( 'len[%s] ch[%s]'% (len(self.mChannelList),ClassToList( 'convert', self.mChannelList ) ) )
		"""


	def InitChannelList(self):
		#starttime = time.time( )
		#print '==================== TEST TIME[LIST] START[%s]'% starttime

		#no channel is set Label comment
		if self.mChannelList == None:
			label = MR_LANG('Empty Channels')
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, label )
			return 

		if self.mListItems == None :
			self.mListItems = []

			for iChannel in self.mChannelList:
				listItem = xbmcgui.ListItem( '%04d %s'%( iChannel.mNumber, iChannel.mName ) )

				if iChannel.mLocked  : listItem.setProperty( E_XML_PROPERTY_LOCK, E_TAG_TRUE )
				if iChannel.mIsCA    : listItem.setProperty( E_XML_PROPERTY_CAS,  E_TAG_TRUE )
				if self.mRecCount :
					if self.mRecChannel1 :
						if iChannel.mNumber == self.mRecChannel1[0] : listItem.setProperty(E_XML_PROPERTY_RECORDING, E_TAG_TRUE)
					if self.mRecChannel2 :
						if iChannel.mNumber == self.mRecChannel2[0] : listItem.setProperty(E_XML_PROPERTY_RECORDING, E_TAG_TRUE)

				if self.mViewMode == WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW and iChannel.mSkipped == True : listItem.setProperty( E_XML_PROPERTY_SKIP, E_TAG_TRUE )

				self.mListItems.append(listItem)

		self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, self.mListItems, E_TAG_ADD_ITEM )


		#get last channel
		iChannel = None
		if self.mListItems == None :
			iChannel = self.mDataCache.Channel_GetCurrent( FLAG_ZAPPING_CHANGE )
		else :
			iChannel = self.mDataCache.Channel_GetCurrent( )

		if iChannel :
			self.mNavChannel = iChannel
			self.mCurrentChannel = self.mNavChannel.mNumber

		#detected to last focus
		iChannelIdx = 0
		for iChannel in self.mChannelList:
			if iChannel.mNumber == self.mCurrentChannel :
				break
			iChannelIdx += 1

		self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, iChannelIdx, E_TAG_SET_SELECT_POSITION )
		xbmc.sleep( 50 )

		#select item idx, print GUI of 'current / total'
		self.mCurrentPosition = iChannelIdx
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_SELECT_NUMBER, str('%s'% (iChannelIdx+1) ) )

		#endtime = time.time( )
		#print '==================== TEST TIME[LIST] END[%s] loading[%s]'% (endtime, endtime-starttime )


	def ResetLabel(self):
		if self.mChannelListServiceType == ElisEnum.E_SERVICE_TYPE_TV:
			self.mCtrlRadioServiceTypeTV.setSelected( True )
			self.mCtrlRadioServiceTypeRadio.setSelected( False )
		elif self.mChannelListServiceType == ElisEnum.E_SERVICE_TYPE_RADIO:
			self.mCtrlRadioServiceTypeTV.setSelected( False )
			self.mCtrlRadioServiceTypeRadio.setSelected( True )

		self.mCtrlProgress.setPercent(0)
		self.mCtrlProgress.setVisible(False)
		self.mPincodeEnter = FLAG_MASK_NONE

		self.mCtrlLabelSelectItem.setLabel( str('%s'% (self.mCtrlListCHList.getSelectedPosition( )+1) ) )
		self.mCtrlLabelEPGName.setLabel('')
		self.mCtrlLabelEPGTime.setLabel('')
		self.mCtrlLabelLongitudeInfo.setLabel('')
		self.mCtrlLabelCareerInfo.setLabel('')
		self.mCtrlLabelLockedInfo.setVisible(False)
		self.mWin.setProperty( E_XML_PROPERTY_SUBTITLE, E_TAG_FALSE )
		self.mWin.setProperty( E_XML_PROPERTY_DOLBY,    E_TAG_FALSE )
		self.mWin.setProperty( E_XML_PROPERTY_HD,       E_TAG_FALSE )


	def InitEPGEvent( self ) :
		try :
			if self.mIsSelect == True :
				if not self.mNavChannel :
					LOG_TRACE('No Channels')
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
					chNumber = self.mChannelList[idx].mNumber

					for iChannel in self.mChannelList:
						if iChannel.mNumber == chNumber :
							self.mNavChannel = None
							self.mNavChannel = iChannel

							sid  = iChannel.mSid
							tsid = iChannel.mTsid
							onid = iChannel.mOnid
							iEPG = None
							iEPG = self.mDataCache.Epgevent_GetCurrent( sid, tsid, onid )
							#iEPGList = self.mDataCache.Epgevent_GetCurrentByChannelFromEpgCF( sid, tsid, onid )
							if iEPG == None or iEPG.mError != 0 :
								self.mNavEpg = 0

							self.mNavEpg = iEPG
							
		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def UpdateServiceType( self, aTvType ):
		label = ''
		if aTvType == ElisEnum.E_SERVICE_TYPE_TV:
			label = 'TV'
		elif aTvType == ElisEnum.E_SERVICE_TYPE_RADIO:
			label = 'RADIO'
		elif aTvType == ElisEnum.E_SERVICE_TYPE_DATA:
			label = 'DATA'
		else:
			label = 'etc'
			LOG_TRACE( 'unknown ElisEnum tvType[%s]'% aTvType )

		return label


	@GuiLock
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

		elif aCtrlID == E_CONTROL_ID_GROUP_COMPONENT_DATA :
			self.mWin.setProperty( E_XML_PROPERTY_SUBTITLE, aValue )

		elif aCtrlID == E_CONTROL_ID_GROUP_COMPONENT_DOLBY :
			self.mWin.setProperty( E_XML_PROPERTY_DOLBY, aValue )

		elif aCtrlID == E_CONTROL_ID_GROUP_COMPONENT_HD :
			self.mWin.setProperty( E_XML_PROPERTY_HD, aValue )

		elif aCtrlID == E_CONTROL_ID_GROUP_OPT :
			self.mCtrlGroupOpt.setVisible( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_CHANNEL_PATH :
			self.mCtrlLabelChannelPath.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_RADIO_SERVICETYPE_TV :
			if aExtra == E_TAG_SELECT :
				self.mCtrlRadioServiceTypeTV.setSelected( aValue )
			elif aExtra == E_TAG_ENABLE :
				self.mCtrlRadioServiceTypeTV.setEnabled( aValue )

		elif aCtrlID == E_CONTROL_ID_RADIO_SERVICETYPE_RADIO :
			if aExtra == E_TAG_SELECT :
				self.mCtrlRadioServiceTypeRadio.setSelected( aValue )
			elif aExtra == E_TAG_ENABLE :
				self.mCtrlRadioServiceTypeRadio.setEnabled( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_SELECT_NUMBER :
			self.mCtrlLabelSelectItem.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_IMAGE_LISTMODE :
			self.mCtrlImageListMode.setVisible( aValue )

		elif aCtrlID == E_CONTROL_ID_LIST_CHANNEL_LIST :
			if aExtra == E_TAG_SET_SELECT_POSITION :
				self.mCtrlListCHList.selectItem( aValue )
			elif aExtra == E_TAG_ENABLE :
				self.mCtrlListCHList.setEnabled( aValue )
			elif aExtra == E_TAG_ADD_ITEM :
				self.mCtrlListCHList.addItems( aValue )

		elif aCtrlID == E_CONTROL_FOCUSED :
			self.setFocusId( aValue )

		elif aCtrlID == E_SLIDE_CLOSE :
			self.mCtrlListCHList.setEnabled( True )
			self.setFocusId( E_CONTROL_ID_GROUP_CHANNEL_LIST )

		elif aCtrlID == E_CONTROL_ID_GROUP_HELPBOX :
			self.mWin.setProperty( E_XML_PROPERTY_EDITINFO, aValue )


	def UpdateChannelAndEPG( self ) :
		if self.mNavChannel :
			#update channel name
			if self.mIsSelect == True :
				strType = self.UpdateServiceType( self.mNavChannel.mServiceType )
				label = '%s - %s'% (strType, self.mNavChannel.mName)
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, label )

			#update longitude info
			satellite = self.mDataCache.Satellite_GetByChannelNumber( self.mNavChannel.mNumber, -1 )
			if not satellite :
				#LOG_TRACE('Fail GetByChannelNumber by Cache')
				satellite = self.mDataCache.Satellite_GetByChannelNumber( self.mNavChannel.mNumber, self.mNavChannel.mServiceType )

			if satellite :
				label = GetSelectedLongitudeString( satellite.mLongitude, satellite.mName )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_LONGITUDE_INFO, label )
			else :
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_LONGITUDE_INFO, '' )

			#update lock-icon visible
			if self.mNavChannel.mLocked :
				#self.mPincodeEnter |= FLAG_MASK_ADD
				self.UpdateControlGUI( E_CONTROL_ID_GROUP_LOCKED_INFO, True )


			#update career info
			if self.mNavChannel.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBS:
				value1 = self.mNavChannel.mCarrier.mDVBS.mPolarization
				value2 = self.mNavChannel.mCarrier.mDVBS.mFrequency
				value3 = self.mNavChannel.mCarrier.mDVBS.mSymbolRate

				polarization = EnumToString( 'Polarization', value1 )
				careerLabel = '%s MHz, %s KS/S, %s'% (value2, value3, polarization)
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_CAREER_INFO, careerLabel )

			elif self.mNavChannel.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBT:
				pass
			elif self.mNavChannel.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBC:
				pass
			elif self.mNavChannel.mCarrierType == ElisEnum.E_CARRIER_TYPE_INVALID:
				pass
				
			"""
			#is cas?
			if self.mNavChannel.mIsCA == True:
				#scrambled
				self.mPincodeEnter |= FLAG_MASK_ADD
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
				self.UpdateControlGUI( E_CONTROL_ID_GROUP_COMPONENT_DATA,  setPropertyList[0] )
				self.UpdateControlGUI( E_CONTROL_ID_GROUP_COMPONENT_DOLBY, setPropertyList[1] )
				self.UpdateControlGUI( E_CONTROL_ID_GROUP_COMPONENT_HD,    setPropertyList[2] )


				"""
				#is Age? agerating check
				isLimit = AgeLimit( self.mPropertyAge, self.mNavEpg.mAgeRating )
				if isLimit == True :
					self.mPincodeEnter |= FLAG_MASK_ADD
					LOG_TRACE( 'AgeLimit[%s]'% isLimit )
				"""

			except Exception, e:
				LOG_TRACE( 'Error exception[%s]'% e )


		else:
			LOG_TRACE( 'event null' )


	@RunThread
	def EPGProgressThread( self ) :
		loop = 0
		while self.mEnableLocalThread :
			#LOG_TRACE( 'repeat <<<<' )
			if  ( loop % 10 ) == 0 :
				self.UpdateProgress( )

			time.sleep(1)
			loop += 1


	@GuiLock
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


	@GuiLock
	def SetEditDoAction( self, aCmd, aEnabled = True, aGroupName = '' ) :
		lastPos = self.mCtrlListCHList.getSelectedPosition( )

		try:
			#1.set current position item
			if len(self.mMarkList) < 1 :
				self.SetEditMarkupGUI(lastPos)

			#2.set mark list all
			for idx in self.mMarkList :
				self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, idx, E_TAG_SET_SELECT_POSITION )
				xbmc.sleep( 50 )

				listItem = self.mCtrlListCHList.getListItem(idx)
				cmd = ''
				ret = ''
				#icon toggle
				if aCmd.lower( ) == 'lock' :

					#lock toggle: disable
					if aEnabled :
						listItem.setProperty( E_XML_PROPERTY_LOCK, E_TAG_TRUE )
						cmd = 'Lock'
					else :
						listItem.setProperty( E_XML_PROPERTY_LOCK, E_TAG_FALSE )
						cmd = 'UnLock'

					retList = []
					retList.append( self.mChannelList[idx] )
					ret = self.mDataCache.Channel_Lock( aEnabled, retList )


				#label color
				elif aCmd.lower( ) == 'skip' :
					#skip toggle: disable
					if aEnabled :
						listItem.setProperty( E_XML_PROPERTY_SKIP, E_TAG_TRUE )
						cmd = 'Skip'
					else :
						listItem.setProperty( E_XML_PROPERTY_SKIP, E_TAG_FALSE )
						cmd = 'UnSkip'

					retList = []
					retList.append( self.mChannelList[idx] )
					ret = self.mDataCache.Channel_Skip( aEnabled, retList )

				elif aCmd.lower( ) == 'add' :
					number = self.mChannelList[idx].mNumber
					cmd = 'AddChannel to Group'
					if aGroupName :
						ret = self.mDataCache.Favoritegroup_AddChannel( aGroupName, number, self.mChannelListServiceType )
					else :
						ret = 'group None'

				elif aCmd.lower( ) == 'del' :
					number = self.mChannelList[idx].mNumber
					#LOG_TRACE('delete by Fav grp[%s] ch[%s]'% (aGroupName, number) )
					cmd = 'RemoveChannel to Group'
					if aGroupName :
						ret = self.mDataCache.Favoritegroup_RemoveChannel( aGroupName, number, self.mChannelListServiceType )
					else :
						ret = 'group None'

				elif aCmd.lower( ) == 'delete' :
					cmd = aCmd.title( )
					retList = []
					retList.append( self.mChannelList[lastPos] )
					ret = self.mDataCache.Channel_Delete( retList )

				elif aCmd.lower( ) == 'move' :
					cmd = 'Move'
					idxM= idx + aEnabled
					if idxM < 0 : continue

					#exchange name
					labelM = self.mCtrlListCHList.getSelectedItem( ).getLabel( )
					name = self.mChannelList[idxM].mName
					number=self.mChannelList[idxM].mNumber
					label = str('%s%s'%( number, name ) )
					self.mCtrlListCHList.getSelectedItem( ).setLabel( label )

					self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, idxM, E_TAG_SET_SELECT_POSITION )

					xbmc.sleep( 50 )
					self.mCtrlListCHList.getSelectedItem( ).setLabel( labelM )
					continue
				
				#LOG_TRACE( 'set[%s] idx[%s] ret[%s]'% (cmd,idx,ret) )

				#mark remove
				listItem.setProperty(E_XML_PROPERTY_MARK, E_TAG_FALSE)

			#recovery last focus
			self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, lastPos, E_TAG_SET_SELECT_POSITION )


		except Exception, e:
			LOG_TRACE( 'Error except[%s]'% e )


	def SetEditChanneltoMove(self, aMode, aMove = None, aGroupName = None ) :
		if aMode == FLAG_OPT_MOVE :
		
			number = 0
			retList = []
			markList= []

			if not self.mMarkList :
				lastPos = self.mCtrlListCHList.getSelectedPosition( )
				self.mMarkList.append( lastPos )
				#LOG_TRACE('last position[%s]'% lastPos )
			
			self.mMarkList.sort( )

			chidx = int(self.mMarkList[0])
			number = self.mChannelList[chidx].mNumber

			#LOG_TRACE('1====mark[%s] ch[%s]'% (self.mMarkList, ClassToList('convert',self.mChannelList) ) )

			#2. make listing of ichannel in marked idx
			for idx in self.mMarkList :
				i = int(idx)
				retList.append( self.mChannelList[i] )

			#3. update mark list (sorted)
			for i in range(len(self.mMarkList) ) :
				markList.append( int(self.mMarkList[0])+i )
			#LOG_TRACE('mark: new[%s] old[%s]'% (markList, self.mMarkList) )

			#4. init channel list
			ret = False
			if self.mZappingMode == ElisEnum.E_MODE_FAVORITE :
				if aGroupName :
					ret = self.mDataCache.FavoriteGroup_MoveChannels( aGroupName, chidx, self.mChannelListServiceType, retList )
					#LOG_TRACE( '==========group========' )
			else :
				ret = self.mDataCache.Channel_Move( self.mChannelListServiceType, number, retList )

			if ret :
				self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )

			self.mMarkList = []
			self.mMarkList = deepcopy(markList)

			#LOG_TRACE('2====mark[%s] ch[%s]'% (self.mMarkList, ClassToList('convert',self.mChannelList) ) )
			self.mMoveFlag = True

			for idx in self.mMarkList :
				i = int(idx)
				listItem = self.mCtrlListCHList.getListItem( i )
				listItem.setProperty(E_XML_PROPERTY_MARK, E_TAG_TRUE)

			self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, self.mMarkList[0], E_TAG_SET_SELECT_POSITION )
			self.UpdateControlGUI( E_CONTROL_FOCUSED, E_CONTROL_ID_GROUP_CHANNEL_LIST )

			self.mCtrlLabelOpt1.setLabel('[B]OK[/B]')
			self.mCtrlLabelOpt2.setLabel('[B]OK[/B]')

			#LOG_TRACE ('========= move Init ===' )

		elif aMode == FLAG_OPT_MOVE_OK :
			self.mMoveFlag = False
			self.mCtrlLabelOpt1.setLabel('[B]Opt Edit[/B]')
			self.mCtrlLabelOpt2.setLabel('[B]Opt Edit[/B]')

			self.mMarkList = []
			self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )

			#LOG_TRACE ('========= move End ===' )

		elif aMode == FLAG_OPT_MOVE_UPDOWN :
			updown= 0
			loopS = 0
			loopE = 0
			retList = []
			markList= []
			lastmark = len(self.mMarkList) - 1
			oldmark = 0

			#1. get number
			if aMove == Action.ACTION_MOVE_UP :	
				updown = -1
				chidx = self.mMarkList[0] + updown
				loopS = chidx
				loopE = self.mMarkList[lastmark]
				oldmark = loopE

			elif aMove == Action.ACTION_MOVE_DOWN :	
				updown = 1
				chidx = self.mMarkList[0] + updown
				loopS = self.mMarkList[0]
				loopE = self.mMarkList[lastmark] + updown
				oldmark = loopS

			elif aMove == Action.ACTION_PAGE_UP :	
				updown = -13
				chidx = self.mMarkList[0] + updown
				loopS = chidx
				loopE = self.mMarkList[lastmark] + updown
				oldmark = self.mMarkList[0]

			elif aMove == Action.ACTION_PAGE_DOWN :	
				updown = 13
				chidx = self.mMarkList[0] + updown
				loopS = self.mMarkList[0] + updown
				loopE = self.mMarkList[lastmark] + updown
				oldmark = self.mMarkList[0]


			if chidx < 0 or chidx > ( (len(self.mListItems)-1) - len(self.mMarkList) ) :
				#LOG_TRACE('list limit, do not PAGE MOVE!! idx[%s]'% chidx)
				return
			number = self.mChannelList[chidx].mNumber

			if loopS < 0 : loopS = 0
			elif loopE > (len(self.mListItems) )-1 : loopE = len(self.mListItems)-1
			#LOG_TRACE('1====mark[%s] ch[%s]'% (self.mMarkList, ClassToList('convert',self.mChannelList) ) )

			#2. get retList
			for idx in self.mMarkList :
				i = int(idx)
				retList.append( self.mChannelList[i] )

			#3. update mark list
			if (int(self.mMarkList[0]) + updown) > (len(self.mListItems) )-1 :
				#LOG_TRACE('list limit, do not PAGE MOVE!! idx[%s]'% (int(self.mMarkList[0]) + updown) )
				return
			for idx in self.mMarkList :
				idxNew = int(idx) + updown
				markList.append( idxNew )
			self.mMarkList = []
			self.mMarkList = markList

			#4. init channel list
			answer = False
			if self.mZappingMode == ElisEnum.E_MODE_FAVORITE :
				if aGroupName :
					answer = self.mDataCache.FavoriteGroup_MoveChannels( aGroupName, chidx, self.mChannelListServiceType, retList )
					#LOG_TRACE( '==========group========' )
			else :
				answer = self.mDataCache.Channel_Move( self.mChannelListServiceType, number, retList )

			if answer :
				self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )
			#LOG_TRACE('2====mark[%s] ch[%s]'% (self.mMarkList, ClassToList('convert',self.mChannelList) ) )
			#LOG_TRACE('loopS[%s] loopE[%s]'% (loopS, loopE) )

			#5. refresh section, label move
			for i in range(loopS, loopE+1) :
				number = self.mChannelList[i].mNumber
				name = self.mChannelList[i].mName
				icas = self.mChannelList[i].mIsCA
				lock = self.mChannelList[i].mLocked
				skip = self.mChannelList[i].mSkipped

				GuiLock2( True )
				listItem = self.mCtrlListCHList.getListItem( i )
				xbmc.sleep( 50 )

				#listItem.setProperty( E_XML_PROPERTY_LOCK, E_TAG_FALSE )
				#listItem.setProperty( E_XML_PROPERTY_CAS,  E_TAG_FALSE )

				if skip : listItem.setProperty( E_XML_PROPERTY_SKIP, E_TAG_TRUE )
				if lock : listItem.setProperty( E_XML_PROPERTY_LOCK, E_TAG_TRUE )
				if icas : listItem.setProperty( E_XML_PROPERTY_CAS, E_TAG_TRUE )
				listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_TRUE )
				xbmc.sleep( 50 )
				GuiLock2( False )


			#6. erase old mark
			if aMove == Action.ACTION_MOVE_UP or aMove == Action.ACTION_MOVE_DOWN :
				listItem = self.mCtrlListCHList.getListItem(oldmark)
				xbmc.sleep( 50 )
				listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_FALSE )
				self.UpdateControlGUI( E_CONTROL_FOCUSED, E_CONTROL_ID_GROUP_CHANNEL_LIST )

			else:
				for idx in range(len(self.mMarkList) ) :
					idxOld = oldmark + idx
					if idxOld > (len(self.mListItems) )-1 : 
						#LOG_TRACE('old idx[%s] i[%s]'% (oldmark, idx) )
						continue
					listItem = self.mCtrlListCHList.getListItem( idxOld )
					listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_FALSE )
					self.UpdateControlGUI( E_CONTROL_FOCUSED, E_CONTROL_ID_GROUP_CHANNEL_LIST )
					xbmc.sleep( 50 )

		#LOG_TRACE( 'Leave' )


	def SetEditMarkupGUI( self, aPos ) :
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


	def GetFavoriteGroup( self ) :
		self.mListFavorite = self.mDataCache.Favorite_GetList( FLAG_ZAPPING_CHANGE, self.mChannelListServiceType )
		self.mEditFavorite = []
		if self.mListFavorite :
			for item in self.mListFavorite:
				#copy to favoriteGroup
				self.mEditFavorite.append( item.mGroupName )


	def GetChannelListName( self ) :
		allChannel = self.mDataCache.Channel_GetList( FLAG_ZAPPING_CHANGE, self.mChannelListServiceType, ElisEnum.E_MODE_ALL, self.mChannelListSortMode, True )
		self.mEditChannelList = []
		if allChannel :
			for item in allChannel:
				#copy to ChannelList
				label = '%04d %s'% ( item.mNumber, item.mName )
				self.mEditChannelList.append( label )


	def DoContextAdtion( self, aMode, aContextAction, aGroupName = '', aNumber = -1 ) :
		if aContextAction == CONTEXT_ACTION_LOCK :
			cmd = 'lock'
			self.SetEditDoAction( cmd, True )

		elif aContextAction == CONTEXT_ACTION_UNLOCK :
			cmd = 'lock'
			self.SetEditDoAction( cmd, False)

		elif aContextAction == CONTEXT_ACTION_SKIP :
			cmd = 'skip'
			self.SetEditDoAction( cmd, True )

		elif aContextAction == CONTEXT_ACTION_UNSKIP :
			cmd = 'skip'
			self.SetEditDoAction( cmd, False )

		elif aContextAction == CONTEXT_ACTION_DELETE :
			if aMode == FLAG_OPT_LIST :
				cmd = 'delete'

				if self.mMarkList :
					try:
						retList = []
						for idx in self.mMarkList :
							#retList.append( self.mChannelList[idx] )
							chNum = ElisEInteger( )
							chNum.mParam = self.mChannelList[idx].mNumber
							retList.append( chNum )

						#ret = self.mDataCache.Channel_Delete( retList )
						ret = self.mDataCache.Channel_DeleteByNumber( int(self.mChannelListServiceType), retList )

					except Exception, e:
						LOG_TRACE( 'Error except[%s]'% e )
				else :
					self.SetEditDoAction( cmd, False )

				self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )
				self.mListItems = None

				self.mMarkList = []
				self.UpdateControlGUI( E_CONTROL_FOCUSED, E_CONTROL_ID_GROUP_CHANNEL_LIST )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_SELECT_NUMBER, str('%s'% (self.mCtrlListCHList.getSelectedPosition( )+1) ) )

				return

			else :
				cmd = 'del'
				#idxThisFavorite = self.mCtrlListSubmenu.getSelectedPosition( )
				#aGroupName = self.mListFavorite[idxThisFavorite].mGroupName
				aGroupName = self.mCtrlListSubmenu.getSelectedItem( ).getLabel( )

			self.SetEditDoAction( cmd, True, aGroupName )
			self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )

		elif aContextAction == CONTEXT_ACTION_MOVE :
			cmd = 'move'
			self.SetEditChanneltoMove(FLAG_OPT_MOVE, None, aGroupName )
			if self.mMarkList :
				idx = int(self.mMarkList[0])
				#xbmc.executebuiltin('xbmc.Container.SetViewMode(50)')
				xbmc.executebuiltin('xbmc.Container(50).Update')
				xbmc.sleep( 50 )
				self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, idx, E_TAG_SET_SELECT_POSITION )
				self.UpdateControlGUI( E_CONTROL_FOCUSED, E_CONTROL_ID_GROUP_CHANNEL_LIST )

			return

		elif aContextAction == CONTEXT_ACTION_ADD_TO_FAV :
			cmd = 'add'
			self.SetEditDoAction( cmd, True, aGroupName )

		elif aContextAction == CONTEXT_ACTION_ADD_TO_CHANNEL :
			cmd = 'addChannel'
			if aGroupName and aNumber != -1 :
				ret = self.mDataCache.Favoritegroup_AddChannel( aGroupName, aNumber, self.mChannelListServiceType )
				self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )

		elif aContextAction == CONTEXT_ACTION_CREATE_GROUP_FAV :
			cmd = 'Create'
			if aGroupName :
				ret = self.mDataCache.Favoritegroup_Create( aGroupName, self.mChannelListServiceType )	#default : ElisEnum.E_SERVICE_TYPE_TV
				if ret :
					self.GetFavoriteGroup( )
				self.RefreshSlideMenu( self.mSelectMainSlidePosition, self.mSelectSubSlidePosition, True )

		elif aContextAction == CONTEXT_ACTION_RENAME_FAV :
			cmd = 'Rename'
			if aGroupName :
				name = re.split(':', aGroupName)
				ret = self.mDataCache.Favoritegroup_ChangeName( name[1], self.mChannelListServiceType, name[2] )
				if ret :
					self.GetFavoriteGroup( )
				self.RefreshSlideMenu( self.mSelectMainSlidePosition, self.mSelectSubSlidePosition, True )

		elif aContextAction == CONTEXT_ACTION_DELETE_FAV :
			cmd = 'Remove'
			if aGroupName :
				ret = self.mDataCache.Favoritegroup_Remove( aGroupName, self.mChannelListServiceType )
				if ret :
					self.GetFavoriteGroup( )

				self.RefreshSlideMenu( self.mSelectMainSlidePosition, self.mSelectSubSlidePosition, True )

		elif aContextAction == CONTEXT_ACTION_SAVE_EXIT :
			self.SetGoBackWindow( )
			return

		elif aContextAction == CONTEXT_ACTION_MENU_EDIT_MODE :
			isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )
			if isRunRec > 0 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG('Warning'), MR_LANG('Now recording...') )
	 			dialog.doModal( )

	 		else :
				self.SetGoBackEdit( )

			return

		elif aContextAction == CONTEXT_ACTION_MENU_DELETEALL :
			if self.mFlag_DeleteAll :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG('Warning'), MR_LANG('Already Delete All') )
	 			dialog.doModal( )

	 		else :
				ret = self.SetDeleteAll( )

				if ret == E_DIALOG_STATE_YES :
					self.mChannelList = None
					self.mNavEpg = None
					self.mNavChannel = None
					self.ReloadChannelList( )
					#clear label
					self.ResetLabel( )
					self.UpdateChannelAndEPG( )

			return


		self.mMarkList = []
		self.UpdateControlGUI( E_CONTROL_FOCUSED, E_CONTROL_ID_GROUP_CHANNEL_LIST )


	def EditSettingWindowContext( self, aMode, aMove = None ) :
		#try:
		if self.mMoveFlag :
			self.SetEditChanneltoMove( FLAG_OPT_MOVE_OK )
			return

		self.GetFavoriteGroup( )

		#default context item
		context = []
		if self.mChannelList :
			context.append( ContextItem( MR_LANG('Lock'),   CONTEXT_ACTION_LOCK ) )
			context.append( ContextItem( MR_LANG('Unlock'), CONTEXT_ACTION_UNLOCK ) )
			context.append( ContextItem( MR_LANG('Skip'),   CONTEXT_ACTION_SKIP ) )
			context.append( ContextItem( MR_LANG('Unskip'), CONTEXT_ACTION_UNSKIP  ) )
			context.append( ContextItem( MR_LANG('Delete'), CONTEXT_ACTION_DELETE ) )
			context.append( ContextItem( MR_LANG('Move'),   CONTEXT_ACTION_MOVE ) )


		if aMode == FLAG_OPT_LIST :

			if self.mChannelList :

				if self.mEditFavorite:
					context.append( ContextItem( '%s'% MR_LANG('Add to Fav. Group'), CONTEXT_ACTION_ADD_TO_FAV  ) )
					context.append( ContextItem( '%s'% MR_LANG('Create New Group'), CONTEXT_ACTION_CREATE_GROUP_FAV  ) )
					context.append( ContextItem( '%s'% MR_LANG('Rename Fav. Group'), CONTEXT_ACTION_RENAME_FAV ) )
					context.append( ContextItem( '%s'% MR_LANG('Delete Fav. Group'), CONTEXT_ACTION_DELETE_FAV ) )
				else:
					context.append( ContextItem( '%s'% MR_LANG('Create New Group'), CONTEXT_ACTION_CREATE_GROUP_FAV  ) )

			else :
				head =  MR_LANG('Infomation')
				line1 = MR_LANG('Empty Channels')

				xbmcgui.Dialog( ).ok(head, line1)
				return


		elif aMode == FLAG_OPT_GROUP :
			if not self.mChannelList :
				context = []

			context.append( ContextItem( '%s'% MR_LANG('Add Channel Fav. Group'), CONTEXT_ACTION_ADD_TO_CHANNEL ) )
			context.append( ContextItem( '%s'% MR_LANG('Rename Fav. Group'), CONTEXT_ACTION_RENAME_FAV ) )

		context.append( ContextItem( '%s'% MR_LANG('Save Exit'), CONTEXT_ACTION_SAVE_EXIT ) )


		GuiLock2( True )
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
 		dialog.doModal( )
 		GuiLock2( False )

		selectedAction = dialog.GetSelectedAction( )
		if selectedAction == -1 :
			#LOG_TRACE('CANCEL by context dialog')
			return

		if ( (not self.mChannelList)  and (selectedAction == CONTEXT_ACTION_ADD_TO_CHANNEL) ) or \
		   ( (not self.mEditFavorite) and (selectedAction == CONTEXT_ACTION_ADD_TO_FAV) ) or \
		   ( (not self.mEditFavorite) and (selectedAction == CONTEXT_ACTION_RENAME_FAV) ) or \
		   ( (not self.mEditFavorite) and (selectedAction == CONTEXT_ACTION_DELETE_FAV) ) :
			return


		#--------------------------------------------------------------- dialog 2
		grpIdx = -1
		groupName = None
		addNumber = -2

		if selectedAction == CONTEXT_ACTION_ADD_TO_CHANNEL :
			self.GetChannelListName( )
			grpIdx = xbmcgui.Dialog().select( labelString, self.mEditChannelList )
			groupName = self.mEditFavorite[self.mSelectSubSlidePosition]
			if grpIdx == -1 :
				#LOG_TRACE('CANCEL by context dialog')
				return

			addNumber = grpIdx + 1


		# add Fav, Ren Fav, Del Fav ==> popup select group
		if selectedAction == CONTEXT_ACTION_ADD_TO_FAV or \
		   selectedAction == CONTEXT_ACTION_RENAME_FAV or \
		   selectedAction == CONTEXT_ACTION_DELETE_FAV :
 			title = ''
 			if selectedAction == CONTEXT_ACTION_ADD_TO_FAV :   title = MR_LANG('Add to Fav. Group')
 			elif selectedAction == CONTEXT_ACTION_RENAME_FAV : title = MR_LANG('Rename Fav. Group')
 			elif selectedAction == CONTEXT_ACTION_DELETE_FAV : title = MR_LANG('Delete Fav. Group')

 			grpIdx = xbmcgui.Dialog().select( title, self.mEditFavorite )
 			groupName = self.mEditFavorite[grpIdx]
 			#LOG_TRACE('---------------grpIdx[%s] fav[%s]'% (grpIdx,groupName) )

			if grpIdx == -1 :
				#LOG_TRACE('CANCEL by context dialog')
				return

			if selectedAction == CONTEXT_ACTION_DELETE_FAV :
				head = MR_LANG('Delete Fav. Group')
				line1 = '%s'% groupName
				line2 = '%s'% MR_LANG('Do you want to delete?')
				posLine = abs( 100 - len(line1) )

				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( head, str('%s\n\n%s'% (line1.center(posLine), line2)) )
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
				label = MR_LANG('Create New Group')

			elif selectedAction == CONTEXT_ACTION_RENAME_FAV :
				#rename
				default = groupName
				result = '%d'%grpIdx + ':' + groupName + ':'
				label = MR_LANG('Rename Fav. Group')

			kb = xbmc.Keyboard( default, label, False )
			kb.doModal( )

			name = ''
			name = kb.getText( )
			if name :
				groupName = result + name

		#LOG_TRACE('mode[%s] btn[%s] groupName[%s]'% (aMode, selectedAction, groupName) )
		#--------------------------------------------------------------- context end

		self.DoContextAdtion( aMode, selectedAction, groupName, addNumber )
		self.mIsSave |= FLAG_MASK_ADD

		if selectedAction == CONTEXT_ACTION_CREATE_GROUP_FAV or \
			selectedAction == CONTEXT_ACTION_RENAME_FAV or \
			selectedAction == CONTEXT_ACTION_DELETE_FAV :

			self.GetFavoriteGroup( )
			#self.mCtrlListMainmenu.selectItem( E_SLIDE_MENU_FAVORITE )
			if self.mCtrlListMainmenu.getSelectedPosition( ) == E_SLIDE_MENU_FAVORITE :
				self.SubMenuAction( E_SLIDE_ACTION_MAIN, E_SLIDE_MENU_FAVORITE )


	def ShowContextMenu( self ) :
		mode = FLAG_OPT_LIST
		if self.mZappingMode == ElisEnum.E_MODE_FAVORITE :
			mode = FLAG_OPT_GROUP

		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			context = []
			context.append( ContextItem( MR_LANG('Edit Channel'), CONTEXT_ACTION_MENU_EDIT_MODE ) )
			context.append( ContextItem( MR_LANG('Delete All Channel'), CONTEXT_ACTION_MENU_DELETEALL ) )

			GuiLock2( True )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context )
	 		dialog.doModal( )
	 		GuiLock2( False )

			selectedAction = dialog.GetSelectedAction( )
			if selectedAction == -1 :
				#LOG_TRACE('CANCEL by context dialog')
				return

			self.DoContextAdtion( mode, selectedAction )

		else :
			self.EditSettingWindowContext( mode )


	def Close( self ):
		self.mEventBus.Deregister( self )
		self.StopAsyncEPG( )

		self.SetVideoRestore( )
		#WinMgr.GetInstance().CloseWindow( )


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
			self.mIsSelect = False
			self.InitEPGEvent( )
			self.ResetLabel( )
			self.UpdateChannelAndEPG( )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )



	def SetTuneByNumber( self, aKey ) :
		if self.mChannelList == None:
			return -1

		if aKey == 0 :
			return -1

		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW:

			GuiLock2( True )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_JUMP )
			if self.mNavEpg:
				dialog.SetDialogProperty( str(aKey), E_INPUT_MAX, self.mChannelList, self.mNavEpg.mStartTime )
			else :
				dialog.SetDialogProperty( str(aKey), E_INPUT_MAX, self.mChannelList )
			dialog.doModal( )
			GuiLock2( False )

			isOK = dialog.IsOK( )
			if isOK == E_DIALOG_STATE_YES :
				inputNumber = dialog.GetChannelLast( )
				#LOG_TRACE( 'Jump chNum[%s] currentCh[%s]'% (inputNumber,self.mCurrentChannel) )

				if int(self.mCurrentChannel) == int(inputNumber) :
					ch = None
					ch = self.mDataCache.Channel_GetCurrent( )
					if ch :
						self.mNavChannel = ch
						self.mCurrentChannel = self.mNavChannel.mNumber
						pos = self.mCurrentPosition
						self.UpdateControlGUI( E_CONTROL_ID_LIST_CHANNEL_LIST, pos, E_TAG_SET_SELECT_POSITION )
						xbmc.sleep( 20 )

						self.UpdateControlGUI( E_CONTROL_ID_LABEL_SELECT_NUMBER, str('%s'% pos ) )
						self.ResetLabel( )
						self.UpdateChannelAndEPG( )

				else :
					self.SetChannelTune( int(inputNumber) )


	def ShowRecordingStartDialog( self ) :
		runningCount = self.mDataCache.Record_GetRunningRecorderCount( )

		isOK = False
		GuiLock2(True)
		if runningCount < 2 :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
			dialog.doModal()

			isOK = dialog.IsOK()
			if isOK == E_DIALOG_STATE_YES :
				isOK = True
		else:
			msg = 'Already [%s] recording(s) running' %runningCount
			xbmcgui.Dialog().ok('Infomation', msg )
		GuiLock2(False)

		if isOK :
			self.mDataCache.mCacheReload = True


	def ShowRecordingStopDialog( self ) :
		isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )

		isOK = False
		if isRunRec > 0 :
			GuiLock2( True )
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_STOP_RECORD )
			dialog.doModal( )
			GuiLock2( False )

			isOK = dialog.IsOK()
			if isOK == E_DIALOG_STATE_YES :
				isOK = True

		if isOK == True :
			self.mDataCache.mCacheReload = True



	def ShowRecordingInfo( self ) :
		try:
			isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )
			#LOG_TRACE('isRunRecCount[%s]'% isRunRec)
			self.mRecCount = isRunRec

			if isRunRec == 1 :
				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 0 )
				recNum  = int(recInfo.mChannelNo)
				recName = recInfo.mChannelName
				self.mRecChannel1.append( recNum )
				self.mRecChannel1.append( recName )

			elif isRunRec == 2 :
				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 0 )
				recNum  = int(recInfo.mChannelNo)
				recName = recInfo.mChannelName
				self.mRecChannel1.append( recNum )
				self.mRecChannel1.append( recName )

				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 1 )
				recNum  = int(recInfo.mChannelNo)
				recName = recInfo.mChannelName
				self.mRecChannel2.append( recNum )
				self.mRecChannel2.append( recName )


		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def ReloadChannelList( self, aInit = FLAG_ZAPPING_LOAD ) :
		self.mListItems = None
		self.mCtrlListCHList.reset( )
		self.InitSlideMenuHeader( aInit )
		self.RefreshSlideMenu( E_SLIDE_ALLCHANNEL, ElisEnum.E_MODE_ALL, True )
		self.InitChannelList( )
		self.UpdateControlGUI( E_SLIDE_CLOSE )

