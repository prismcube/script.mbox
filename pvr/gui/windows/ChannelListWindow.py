from pvr.gui.WindowImport import *

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
FLAG_MODE_JUMP      = True

#slide index
E_SLIDE_ACTION_MAIN     = 0
E_SLIDE_ACTION_SUB      = 1
E_SLIDE_ALLCHANNEL      = 0
E_SLIDE_MENU_SATELLITE  = 1
E_SLIDE_MENU_FTACAS     = 2
E_SLIDE_MENU_FAVORITE   = 3
#E_SLIDE_MENU_EDITMODE   = 4
#E_SLIDE_MENU_DELETEALL  = 5
E_SLIDE_MENU_BACK       = 5

#color tag
E_TAG_COLOR_RED   = '[COLOR red]'
E_TAG_COLOR_GREY  = '[COLOR grey]'
E_TAG_COLOR_GREY3 = '[COLOR grey3]'
E_TAG_COLOR_END   = '[/COLOR]'
#string tag
E_TAG_ENABLE  = 'enable'
E_TAG_VISIBLE = 'visible'
E_TAG_SELECT  = 'select'
E_TAG_LABEL   = 'label'
E_TAG_TRUE    = 'True'
E_TAG_FALSE   = 'False'

#xml property name
E_XML_PROPERTY_SUBTITLE  = 'HasSubtitle'
E_XML_PROPERTY_DOLBY     = 'HasDolby'
E_XML_PROPERTY_HD        = 'HasHD'
E_XML_PROPERTY_MARK      = 'mark'
E_XML_PROPERTY_CAS       = 'icas'
E_XML_PROPERTY_LOCK      = 'lock'
E_XML_PROPERTY_RECORDING = 'rec'


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
		self.mEnableThread = False

 
	def onAction(self, aAction):
		id = aAction.getId()
		
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

		#header
		self.mCtrlLblPath1            = self.getControl( 21 )
		self.mCtrlGroupOpt            = self.getControl( 500 )
		self.mCtrlBtnOpt              = self.getControl( 501 )
		self.mCtrlLblOpt1             = self.getControl( 502 )
		self.mCtrlLblOpt2             = self.getControl( 503 )

		#main menu
		self.mCtrlGroupMainmenu       = self.getControl( 100 )
		self.mCtrlBtnMenu             = self.getControl( 101 )
		self.mCtrlListMainmenu        = self.getControl( 102 )

		#sub menu list
		self.mCtrlGroupSubmenu        = self.getControl( 9001 )
		self.mCtrlListSubmenu         = self.getControl( 112 )

		#sub menu btn
		self.mCtrlRdoTV               = self.getControl( 113 )
		self.mCtrlRdoRadio            = self.getControl( 114 )
		self.mCtrlBtnEdit             = self.getControl( 115 )
		self.mCtrlBtnDelAll           = self.getControl( 116 )

		#ch list
		self.mCtrlGroupCHList         = self.getControl( 49 )
		self.mCtrlListCHList          = self.getControl( 50 )

		#info
		self.mCtrlChannelName         = self.getControl( 303 )
		self.mCtrlEventName           = self.getControl( 304 )
		self.mCtrlEventTime           = self.getControl( 305 )
		self.mCtrlProgress            = self.getControl( 306 )
		self.mCtrlLongitudeInfo       = self.getControl( 307 )
		self.mCtrlCareerInfo          = self.getControl( 308 )
		self.mCtrlLockedInfo          = self.getControl( 309 )
		self.mCtrlGroupComponentData  = self.getControl( 310 )
		self.mCtrlGroupComponentDolby = self.getControl( 311 )
		self.mCtrlGroupComponentHD    = self.getControl( 312 )
		self.mCtrlSelectItem          = self.getControl( 401 )

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
		self.mMoveFlag = False
		self.mMoveItem = []

		self.SetPipScreen( )

		self.UpdateLabelGUI( self.mCtrlBtnDelAll.getId( ), MR_LANG('Delete All Channel') )

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
		self.ShowRecording( )

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
			self.UpdateLabelGUI( self.mCtrlChannelName.getId( ), label )

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

		self.UpdateLabelInfo( )

		#Event Register
		self.mEventBus.Register( self )

		#run thread
		self.mEnableThread = True
		self.CurrentTimeThread( )

		self.mAsyncTuneTimer = None
		#endtime = time.time( )
		#print '==================== TEST TIME[ONINIT] END[%s] loading[%s]'% (endtime, endtime-starttime )

	def onAction(self, aAction):
		id = aAction.getId( )

		self.GlobalAction( id )		

		if id >= Action.REMOTE_0 and id <= Action.REMOTE_9:
			self.KeySearch( id-Action.REMOTE_0 )

		elif id >= Action.ACTION_JUMP_SMS2 and id <= Action.ACTION_JUMP_SMS9 :
			rKey = id - (Action.ACTION_JUMP_SMS2 - 2)
			self.KeySearch( rKey )

		elif id == Action.ACTION_PREVIOUS_MENU or id == Action.ACTION_PARENT_DIR:
			#LOG_TRACE( 'goto previous menu' )
			self.SetGoBackWindow( )

		elif id == Action.ACTION_SELECT_ITEM:
			self.GetFocusId( )
			#LOG_TRACE( 'item select, action ID[%s]'% id )

			if self.mFocusId == self.mCtrlListMainmenu.getId( ) :
				position = self.mCtrlListMainmenu.getSelectedPosition( )

				if position == E_SLIDE_MENU_BACK :
					self.mCtrlListCHList.setEnabled(True)
					self.setFocusId( self.mCtrlGroupCHList.getId( ) )

				else :
					self.SubMenuAction( E_SLIDE_ACTION_MAIN, position )

		elif id == Action.ACTION_MOVE_RIGHT :
			pass

		elif id == Action.ACTION_MOVE_LEFT :
			self.GetFocusId( )
			if self.mFocusId == self.mCtrlListCHList.getId( ) :
				self.GetSlideMenuHeader( FLAG_SLIDE_OPEN )
				self.mSlideOpenFlag = True

		elif id == Action.ACTION_MOVE_UP or id == Action.ACTION_MOVE_DOWN or \
			 id == Action.ACTION_PAGE_UP or id == Action.ACTION_PAGE_DOWN :
			self.GetFocusId( )
			if self.mFocusId == self.mCtrlListCHList.getId( ) or self.mFocusId == E_CONTROL_ID_SCROLLBAR :
				if self.mMoveFlag :
					self.SetEditChanneltoMove( FLAG_OPT_MOVE_UPDOWN, id )
					return

				else :
					self.RestartAsyncEPG( )

			if self.mFocusId == self.mCtrlListMainmenu.getId( ) :
				position = self.mCtrlListMainmenu.getSelectedPosition( )
				self.SubMenuAction( E_SLIDE_ACTION_MAIN, position )

			elif self.mFocusId == self.mCtrlBtnOpt :
				self.mCtrlListCHList.setEnabled( True )
				self.setFocusId( self.mCtrlGroupCHList.getId( ) )


		elif id == Action.ACTION_CONTEXT_MENU :
			#LOG_TRACE( 'popup opt' )
			self.PopupOpt( )


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
					self.UpdateLabelInfo()
				else :
					self.RecordingStop()

		elif id == Action.ACTION_MBOX_XBMC :
			self.SetGoBackWindow( WinMgr.WIN_ID_MEDIACENTER )

		elif id == Action.ACTION_MBOX_ARCHIVE :
			#self.Close( )
			self.mDataCache.mSetFromParentWindow = WinMgr.WIN_ID_NULLWINDOW
			self.SetGoBackWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW )
			#WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW )

		elif id == Action.ACTION_MBOX_RECORD :
			if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
				if self.mChannelList or len(self.mChannelList) > 0 :
					self.RecordingStart()




		elif id == 13: #'x'
			#this is test
			LOG_TRACE( 'language[%s]'% xbmc.getLanguage( ) )


	def onClick(self, aControlId):
		#LOG_TRACE( 'onclick focusID[%d]'% aControlId )

		if aControlId == self.mCtrlListCHList.getId( ) :
			if self.mViewMode == WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW :
				try:
					if self.mMoveFlag :
						self.SetEditChanneltoMove( FLAG_OPT_MOVE_OK )
						return

					#Mark mode
					if self.mIsMark == True :
						idx = self.mCtrlListCHList.getSelectedPosition( )
						self.SetEditMarkupGUI( idx )

						GuiLock2( True )
						self.setFocusId( self.mCtrlGroupCHList.getId( ) )
						self.mCtrlListCHList.selectItem( idx+1 )
						GuiLock2( False )

						self.mCtrlSelectItem.setLabel( str('%s'% (idx+1) ) )

					#Turn mode
					#else :
					#	self.SetChannelTune( )

				except Exception, e:
					LOG_TRACE( 'Error except[%s]'% e )

			else :
				if self.mChannelList :
					self.SetChannelTune( )

		elif aControlId == self.mCtrlBtnMenu.getId( ) or aControlId == self.mCtrlListMainmenu.getId( ) :
			#list view
			pass

		elif aControlId == self.mCtrlListSubmenu.getId( ) :
			#list action
			position = self.mZappingMode
			self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )

			#slide close
			GuiLock2( True )
			self.mCtrlListCHList.setEnabled(True)
			self.setFocusId( self.mCtrlGroupCHList.getId( ) )
			GuiLock2( False )

		elif aControlId == self.mCtrlBtnOpt.getId( ):
			self.PopupOpt( )

		elif aControlId == self.mCtrlBtnEdit.getId( ):
			self.SetGoBackEdit( )

		elif aControlId == self.mCtrlBtnDelAll.getId( ):
			ret = self.SetDeleteAll( )

			if ret == E_DIALOG_STATE_YES :
				self.mListItems = None
				self.mChannelList = None
				self.mNavEpg = None
				self.mNavChannel = None

				self.InitSlideMenuHeader( )

				self.mCtrlListCHList.reset( )
				self.InitChannelList( )

				#clear label
				self.ResetLabel( )
				self.UpdateLabelInfo( )

				#slide close
				GuiLock2( True )
				self.mCtrlListCHList.setEnabled(True)
				self.setFocusId( self.mCtrlGroupCHList.getId( ) )
				GuiLock2( False )


		elif aControlId == self.mCtrlRdoTV.getId( ):
			self.SetModeChanged( FLAG_MODE_TV )

		elif aControlId == self.mCtrlRdoRadio.getId( ):
			self.SetModeChanged( FLAG_MODE_RADIO )


	def onFocus(self, controlId):
		#LOG_TRACE( 'control %d' % controlId )
		pass

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
			self.mCtrlListCHList.selectItem(0)
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
			self.UpdateLabelGUI( self.mCtrlRdoTV.getId( ),   True, E_TAG_SELECT )
			self.UpdateLabelGUI( self.mCtrlRdoRadio.getId( ),False, E_TAG_SELECT )
		else :
			self.UpdateLabelGUI( self.mCtrlRdoTV.getId( ),   False, E_TAG_SELECT )
			self.UpdateLabelGUI( self.mCtrlRdoRadio.getId( ),True, E_TAG_SELECT )

		#slide close
		self.mCtrlListCHList.setEnabled(True)
		self.setFocusId( self.mCtrlGroupCHList.getId( ) )



	def SetGoBackEdit( self ) :
		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			self.mViewMode = WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW

			try :
				#Event UnRegister
				#self.mEventBus.Deregister( self )
				self.InitSlideMenuHeader( )
				self.RefreshSlideMenu( )

				#clear label
				self.ResetLabel( )
				self.UpdateLabelInfo( )

				self.mCtrlListCHList.reset( )
				self.InitChannelList( )

				ret = self.mDataCache.Channel_Backup( )
				#LOG_TRACE( 'channelBackup[%s]'% ret )

				#slide close
				GuiLock2( True )
				self.mCtrlListCHList.setEnabled(True)
				self.setFocusId( self.mCtrlGroupCHList.getId( ) )
				GuiLock2( False )

			except Exception, e :
				LOG_TRACE( 'Error except[%s]'% e )

		else :
			self.SetGoBackWindow( )


	def SetGoBackWindow( self, aGoToWindow = None ) :
		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			ret = False
			ret = self.SaveSlideMenuHeader( )
			if ret != E_DIALOG_STATE_CANCEL :
				self.mEnableThread = False
				#self.CurrentTimeThread( ).join( )
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
				self.mListItems = None
				self.mCtrlListCHList.reset( )
				self.InitSlideMenuHeader( FLAG_ZAPPING_CHANGE )
				self.InitChannelList( )

				#initialize get epg event
				self.mIsSelect = False
				self.InitEPGEvent( )

				#clear label
				self.ResetLabel( )
				self.UpdateLabelInfo( )
				self.mFlag_EditChanged = False
				self.mMoveFlag = False

				#slide close
				GuiLock2( True )
				self.mCtrlListCHList.setEnabled(True)
				self.setFocusId( self.mCtrlGroupCHList.getId( ) )
				GuiLock2( False )

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
							self.UpdateLabelInfo( )


			elif aEvent.getName() == ElisEventRecordingStarted.getName() or \
				 aEvent.getName() == ElisEventRecordingStopped.getName() :
				self.mRecChannel1 = []
				self.mRecChannel2 = []
				self.ShowRecording()
				self.mDataCache.mCacheReload = True
				self.mListItems = None
				self.InitChannelList( )

				#ToDo
				"""
				if aEvent.getName() == ElisEventRecordingStarted.getName() :
					msg1 = MR_LANG('Recording Started')
				else :
					msg1 = MR_LANG('Recording Ended')

				msg2 = MR_LANG('Reload Channel List...')
				
				self.AlarmDialog( msg1, msg2 )
				"""

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
					self.UpdateLabelInfo( )
					break
				chindex += 1

			if self.mChannelList == None:
				label = MR_LANG('Empty Channels')
				self.UpdateLabelGUI( self.mCtrlChannelName.getId( ), label )
				return 

			GuiLock2( True )
			self.mCtrlListCHList.selectItem( chindex )
			xbmc.sleep( 50 )
			GuiLock2( False )

			#chNumber = aJumpNumber
			iChannel = ElisIChannel( )
			iChannel.reset()
			iChannel.mNumber = int(aJumpNumber)
			iChannel.mServiceType = deepcopy(self.mChannelListServiceType)

			#LOG_TRACE('JumpChannel: num[%s] type[%s]'% (iChannel.mNumber, iChannel.mServiceType) )

		else:
			if self.mChannelList == None:
				label = MR_LANG('Empty Channels')
				self.UpdateLabelGUI( self.mCtrlChannelName.getId( ), label )
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
			#if self.mPincodeEnter == FLAG_MASK_NONE :
			if self.mCurrentChannel == iChannel.mNumber :
				ret = False
				ret = self.SaveSlideMenuHeader( )
				if ret != E_DIALOG_STATE_CANCEL :
					self.mEnableThread = False
					#self.CurrentTimeThread( ).join( )
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
			self.mCtrlSelectItem.setLabel( str('%s'% pos ) )
			#LOG_TRACE('chinfo: num[%s] type[%s] name[%s] pos[%s]'% (ch.mNumber, ch.mServiceType, ch.mName, pos) )

			self.ResetLabel( )
			self.UpdateLabelInfo( )


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
			self.mCtrlLblPath1.setLabel( label )

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
		#self.setFocusId( self.mCtrlListSubmenu.getId( ) )


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
				self.mDataCache.LoadZappingmode( )
				self.mDataCache.LoadZappingList( )
				self.mDataCache.LoadChannelList( )
				LOG_TRACE ('cache re-load')

			elif answer == E_DIALOG_STATE_NO :
				self.mIsSave = FLAG_MASK_NONE
				isSave = self.mDataCache.Channel_Restore( True )
				LOG_TRACE( 'Restore[%s]'% isSave )


		return answer


	def InitSlideMenuHeader( self, aZappingMode = FLAG_ZAPPING_LOAD ) :
		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			self.mDataCache.SetSkipChannelToDBTable( False )
			#opt btn blind
			self.UpdateLabelGUI( self.mCtrlGroupOpt.getId( ), False )
			self.UpdateLabelGUI( self.mCtrlRdoTV.getId( ), True, E_TAG_ENABLE )
			self.UpdateLabelGUI( self.mCtrlRdoRadio.getId( ), True, E_TAG_ENABLE )
			self.UpdateLabelGUI( self.mCtrlBtnEdit.getId( ), MR_LANG('Edit Channel'), E_TAG_LABEL )

		else :
			self.mDataCache.SetSkipChannelToDBTable( True )
			#opt btn visible
			self.UpdateLabelGUI( self.mCtrlGroupOpt.getId( ), True )
			self.UpdateLabelGUI( self.mCtrlRdoTV.getId( ), False, E_TAG_ENABLE )
			self.UpdateLabelGUI( self.mCtrlRdoRadio.getId( ), False, E_TAG_ENABLE )
			self.UpdateLabelGUI( self.mCtrlBtnEdit.getId( ), MR_LANG('Save Channel'), E_TAG_LABEL )
			return

		if self.mFlag_DeleteAll :
			self.mZappingMode           = ElisEnum.E_MODE_ALL
			self.mChannelListSortMode   = ElisEnum.E_SORT_BY_DEFAULT
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
		list_Mainmenu.append( MR_LANG('Back') )
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
		self.UpdateLabelGUI( self.mCtrlLblPath1.getId( ), label )

		#get channel list by last on zapping mode, sorting, service type
		self.mNavChannel = None
		self.mChannelList = None

		if self.mFlag_EditChanged :
			self.mChannelList = self.mDataCache.Channel_GetList( self.mFlag_EditChanged, self.mChannelListServiceType, self.mZappingMode, self.mChannelListSortMode )
		else :
			#### first get is used cache, reason by fast load ###
			self.mChannelList = self.mDataCache.Channel_GetList( )


		"""
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
			self.UpdateLabelGUI( self.mCtrlChannelName.getId( ), label )
			return 

		lblColorS = E_TAG_COLOR_GREY
		lblColorE = E_TAG_COLOR_END
		if self.mListItems == None :
			self.mListItems = []

			for iChannel in self.mChannelList:
				try:
					if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
						#skip ch
						#if iChannel.mSkipped == True :
						#	continue
						listItem = xbmcgui.ListItem( '%04d %s'%( iChannel.mNumber, iChannel.mName ) )
					else :
						#skip ch
						if iChannel.mSkipped == True :
							lblColorS = E_TAG_COLOR_GREY3
						else:
							lblColorS = E_TAG_COLOR_GREY

						listItem = xbmcgui.ListItem( '%s%04d %s%s'%( lblColorS, iChannel.mNumber, iChannel.mName, lblColorE ) )

				except Exception, e:
					LOG_TRACE( '=========== except[%s]'% e )

				if iChannel.mLocked  : listItem.setProperty( E_XML_PROPERTY_LOCK, E_TAG_TRUE )
				if iChannel.mIsCA    : listItem.setProperty( E_XML_PROPERTY_CAS,  E_TAG_TRUE )
				if self.mRecCount :
					if self.mRecChannel1 :
						if iChannel.mNumber == self.mRecChannel1[0] : listItem.setProperty(E_XML_PROPERTY_RECORDING, E_TAG_TRUE)
					if self.mRecChannel2 :
						if iChannel.mNumber == self.mRecChannel2[0] : listItem.setProperty(E_XML_PROPERTY_RECORDING, E_TAG_TRUE)

				self.mListItems.append(listItem)

		GuiLock2( True )
		self.mCtrlListCHList.addItems( self.mListItems )
		GuiLock2( False )


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

		GuiLock2( True )
		self.mCtrlListCHList.selectItem( iChannelIdx )
		xbmc.sleep( 50 )

		#select item idx, print GUI of 'current / total'
		self.mCurrentPosition = iChannelIdx
		self.mCtrlSelectItem.setLabel( str('%s'% (iChannelIdx+1) ) )
		GuiLock2( False )

		#endtime = time.time( )
		#print '==================== TEST TIME[LIST] END[%s] loading[%s]'% (endtime, endtime-starttime )


	def ResetLabel(self):
		if self.mChannelListServiceType == ElisEnum.E_SERVICE_TYPE_TV:
			self.mCtrlRdoTV.setSelected( True )
			self.mCtrlRdoRadio.setSelected( False )
		elif self.mChannelListServiceType == ElisEnum.E_SERVICE_TYPE_RADIO:
			self.mCtrlRdoTV.setSelected( False )
			self.mCtrlRdoRadio.setSelected( True )

		self.mCtrlProgress.setPercent(0)
		self.mCtrlProgress.setVisible(False)
		self.mPincodeEnter = FLAG_MASK_NONE

		self.mCtrlSelectItem.setLabel( str('%s'% (self.mCtrlListCHList.getSelectedPosition( )+1) ) )
		self.mCtrlEventName.setLabel('')
		self.mCtrlEventTime.setLabel('')
		self.mCtrlLongitudeInfo.setLabel('')
		self.mCtrlCareerInfo.setLabel('')
		self.mCtrlLockedInfo.setVisible(False)
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
	def UpdateLabelGUI( self, aCtrlID = None, aValue = None, aExtra = None ) :
		#LOG_TRACE( 'Enter control[%s] value[%s]'% (aCtrlID, aValue) )

		if aCtrlID == self.mCtrlChannelName.getId( ) :
			self.mCtrlChannelName.setLabel( aValue )

		elif aCtrlID == self.mCtrlLongitudeInfo.getId( ) :
			self.mCtrlLongitudeInfo.setLabel( aValue )

		elif aCtrlID == self.mCtrlCareerInfo.getId( ) :
			self.mCtrlCareerInfo.setLabel( aValue )

		elif aCtrlID == self.mCtrlEventName.getId( ) :
			self.mCtrlEventName.setLabel( aValue )

		elif aCtrlID == self.mCtrlEventTime.getId( ) :
			self.mCtrlEventTime.setLabel( aValue )

		elif aCtrlID == self.mCtrlLockedInfo.getId( ) :
			self.mCtrlLockedInfo.setVisible( aValue )

		elif aCtrlID == self.mCtrlGroupComponentData.getId( ) :
			self.mWin.setProperty( E_XML_PROPERTY_SUBTITLE, aValue )

		elif aCtrlID == self.mCtrlGroupComponentDolby.getId( ) :
			self.mWin.setProperty( E_XML_PROPERTY_DOLBY, aValue )

		elif aCtrlID == self.mCtrlGroupComponentHD.getId( ) :
			self.mWin.setProperty( E_XML_PROPERTY_HD, aValue )

		elif aCtrlID == self.mCtrlGroupOpt.getId( ) :
			self.mCtrlGroupOpt.setVisible( aValue )

		elif aCtrlID == self.mCtrlLblPath1.getId( ) :
			self.mCtrlLblPath1.setLabel( aValue )

		elif aCtrlID == self.mCtrlRdoTV.getId( ) :
			if aExtra == E_TAG_SELECT :
				self.mCtrlRdoTV.setSelected( aValue )
			elif aExtra == E_TAG_ENABLE :
				self.mCtrlRdoTV.setEnabled( aValue )

		elif aCtrlID == self.mCtrlRdoRadio.getId( ) :
			if aExtra == E_TAG_SELECT :
				self.mCtrlRdoRadio.setSelected( aValue )
			elif aExtra == E_TAG_ENABLE :
				self.mCtrlRdoRadio.setEnabled( aValue )

		elif aCtrlID == self.mCtrlBtnEdit.getId( ) :
			if aExtra == E_TAG_ENABLE :
				self.mCtrlBtnEdit.setEnabled( aValue )
			elif aExtra == E_TAG_LABEL :
				self.mCtrlBtnEdit.setLabel( aValue )

		elif aCtrlID == self.mCtrlBtnDelAll.getId( ) :
			self.mCtrlBtnDelAll.setLabel( aValue )


	def UpdateLabelInfo( self ):
		if self.mNavChannel :
			#update channel name
			if self.mIsSelect == True :
				strType = self.UpdateServiceType( self.mNavChannel.mServiceType )
				label = '%s - %s'% (strType, self.mNavChannel.mName)
				self.UpdateLabelGUI( self.mCtrlChannelName.getId( ), label )

			#update longitude info
			satellite = self.mDataCache.Satellite_GetByChannelNumber( self.mNavChannel.mNumber, -1, True )
			if not satellite :
				#LOG_TRACE('Fail GetByChannelNumber by Cache')
				satellite = self.mDataCache.Satellite_GetByChannelNumber( self.mNavChannel.mNumber, self.mNavChannel.mServiceType, True )

			if satellite :
				label = GetSelectedLongitudeString( satellite.mLongitude, satellite.mName )
				self.UpdateLabelGUI( self.mCtrlLongitudeInfo.getId( ), label )
			else :
				self.UpdateLabelGUI( self.mCtrlLongitudeInfo.getId( ), '' )

			#update lock-icon visible
			if self.mNavChannel.mLocked :
				#self.mPincodeEnter |= FLAG_MASK_ADD
				self.UpdateLabelGUI( self.mCtrlLockedInfo.getId( ), True )


			#update career info
			if self.mNavChannel.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBS:
				value1 = self.mNavChannel.mCarrier.mDVBS.mPolarization
				value2 = self.mNavChannel.mCarrier.mDVBS.mFrequency
				value3 = self.mNavChannel.mCarrier.mDVBS.mSymbolRate

				polarization = EnumToString( 'Polarization', value1 )
				careerLabel = '%s MHz, %s KS/S, %s'% (value2, value3, polarization)
				self.UpdateLabelGUI( self.mCtrlCareerInfo.getId( ), careerLabel )

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
				self.UpdateLabelGUI( self.mCtrlEventTime.getId( ), label )
				self.UpdateLabelGUI( self.mCtrlEventName.getId( ), self.mNavEpg.mEventName )
				self.mCtrlProgress.setVisible( True )

				#component
				setPropertyList = []
				setPropertyList = GetPropertyByEPGComponent( self.mNavEpg )
				self.UpdateLabelGUI( self.mCtrlGroupComponentData.getId(),  setPropertyList[0] )
				self.UpdateLabelGUI( self.mCtrlGroupComponentDolby.getId(), setPropertyList[1] )
				self.UpdateLabelGUI( self.mCtrlGroupComponentHD.getId(),    setPropertyList[2] )


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
	def CurrentTimeThread( self ) :
		loop = 0
		while self.mEnableThread:
			#LOG_TRACE( 'repeat <<<<' )
			if  ( loop % 10 ) == 0 :
				self.UpdateLocalTime( )

			time.sleep(1)
			loop += 1


	@GuiLock
	def UpdateLocalTime( self ) :
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
				self.mCtrlListCHList.selectItem(idx)
				xbmc.sleep( 50 )

				listItem = self.mCtrlListCHList.getListItem(idx)
				cmd = ''
				ret = ''
				#icon toggle
				if aCmd.lower( ) == 'lock' :

					#lock toggle: disable
					if aEnabled :
						listItem.setProperty(E_XML_PROPERTY_LOCK, E_TAG_TRUE)
						cmd = 'Lock'
					else :
						listItem.setProperty(E_XML_PROPERTY_LOCK, E_TAG_FALSE)
						cmd = 'UnLock'

					retList = []
					retList.append( self.mChannelList[idx] )
					ret = self.mDataCache.Channel_Lock( aEnabled, retList )


				#label color
				elif aCmd.lower( ) == 'skip' :
					#strip tag [COLOR ...]label[/COLOR]
					label1 = self.mCtrlListCHList.getSelectedItem( ).getLabel( )
					label2 = re.findall('\](.*)\[', label1)
					if aEnabled :
						label3= str('%s%s%s'%( E_TAG_COLOR_GREY3, label2[0], E_TAG_COLOR_END ) )
						cmd = 'Skip'
					else :
						label3= str('%s%s%s'%( E_TAG_COLOR_GREY, label2[0], E_TAG_COLOR_END ) )
						cmd = 'UnSkip'
					self.mCtrlListCHList.getSelectedItem( ).setLabel(label3)
					#LOG_TRACE( 'idx[%s] 1%s 2%s 3%s'% (idx, label1,label2,label3) )

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
					label = str('%s%s %s%s'%( E_TAG_COLOR_GREY, number, name, E_TAG_COLOR_END ) )
					self.mCtrlListCHList.getSelectedItem( ).setLabel(label)

					self.mCtrlListCHList.selectItem(idxM)
					xbmc.sleep( 50 )
					self.mCtrlListCHList.getSelectedItem( ).setLabel(labelM)
					continue
				
				#LOG_TRACE( 'set[%s] idx[%s] ret[%s]'% (cmd,idx,ret) )

				#mark remove
				listItem.setProperty(E_XML_PROPERTY_MARK, E_TAG_FALSE)

			#recovery last focus
			self.mCtrlListCHList.selectItem(lastPos)


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

			GuiLock2( True )
			for idx in self.mMarkList :
				i = int(idx)
				listItem = self.mCtrlListCHList.getListItem( i )
				listItem.setProperty(E_XML_PROPERTY_MARK, E_TAG_TRUE)

			self.mCtrlListCHList.selectItem(self.mMarkList[0])
			self.setFocusId( self.mCtrlGroupCHList.getId( ) )

			self.mCtrlLblOpt1.setLabel('[B]OK[/B]')
			self.mCtrlLblOpt2.setLabel('[B]OK[/B]')
			GuiLock2( False )

			#LOG_TRACE ('========= move Init ===' )

		elif aMode == FLAG_OPT_MOVE_OK :
			self.mMoveFlag = False
			self.mCtrlLblOpt1.setLabel('[B]Opt Edit[/B]')
			self.mCtrlLblOpt2.setLabel('[B]Opt Edit[/B]')

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

				GuiLock2( True )
				listItem = self.mCtrlListCHList.getListItem( i )
				xbmc.sleep( 50 )

				listItem.setProperty( E_XML_PROPERTY_LOCK, E_TAG_FALSE )
				listItem.setProperty( E_XML_PROPERTY_CAS,  E_TAG_FALSE )

				label = str('%s%04d %s%s'%( E_TAG_COLOR_GREY, number, name, E_TAG_COLOR_END ) )
				listItem.setLabel(label)

				if lock : listItem.setProperty( E_XML_PROPERTY_LOCK, E_TAG_TRUE )
				if icas : listItem.setProperty( E_XML_PROPERTY_CAS, E_TAG_TRUE )
				listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_TRUE )
				xbmc.sleep( 50 )
				GuiLock2( False )


			#6. erase old mark
			GuiLock2( True )
			if aMove == Action.ACTION_MOVE_UP or aMove == Action.ACTION_MOVE_DOWN :
				listItem = self.mCtrlListCHList.getListItem(oldmark)
				xbmc.sleep( 50 )
				listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_FALSE )
				self.setFocusId( self.mCtrlGroupCHList.getId( ) )

			else:
				for idx in range(len(self.mMarkList) ) :
					idxOld = oldmark + idx
					if idxOld > (len(self.mListItems) )-1 : 
						#LOG_TRACE('old idx[%s] i[%s]'% (oldmark, idx) )
						continue
					listItem = self.mCtrlListCHList.getListItem( idxOld )
					listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_FALSE )
					self.setFocusId( self.mCtrlGroupCHList.getId( ) )
					xbmc.sleep( 50 )
			GuiLock2( False )

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


	def DoContextAdtion( self, aMode, aContextAction, aGroupName = '' ) :
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
				GuiLock2( True )
				self.setFocusId( self.mCtrlGroupCHList.getId( ) )
				self.mCtrlSelectItem.setLabel( str('%s'% (self.mCtrlListCHList.getSelectedPosition( )+1) ) )
				GuiLock2( False )

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
				GuiLock2( True )
				#xbmc.executebuiltin('xbmc.Container.SetViewMode(50)')
				xbmc.executebuiltin('xbmc.Container(50).Update')
				xbmc.sleep( 50 )
				self.mCtrlListCHList.selectItem(idx)
				
				self.setFocusId( self.mCtrlGroupCHList.getId( ) )
				GuiLock2( False )
			return

		elif aContextAction == CONTEXT_ACTION_ADD_TO_FAV :
			cmd = 'add'
			self.SetEditDoAction( cmd, True, aGroupName )

		elif aContextAction == CONTEXT_ACTION_CREATE_GROUP_FAV :
			cmd = 'Create'
			if aGroupName :
				ret = self.mDataCache.Favoritegroup_Create( aGroupName, self.mChannelListServiceType )	#default : ElisEnum.E_SERVICE_TYPE_TV
				if ret :
					self.GetFavoriteGroup( )

		elif aContextAction == CONTEXT_ACTION_RENAME_FAV :
			cmd = 'Rename'
			name = re.split(':', aGroupName)
			ret = self.mDataCache.Favoritegroup_ChangeName( name[1], self.mChannelListServiceType, name[2] )
			if ret :
				self.GetFavoriteGroup( )

		elif aContextAction == CONTEXT_ACTION_DELETE_FAV :
			cmd = 'Remove'
			ret = self.mDataCache.Favoritegroup_Remove( aGroupName, self.mChannelListServiceType )
			if ret :
				self.GetFavoriteGroup( )

			self.mZappingMode == ElisEnum.E_MODE_ALL
			self.RefreshSlideMenu( E_SLIDE_ALLCHANNEL, ElisEnum.E_MODE_ALL, True )


		self.mMarkList = []
		GuiLock2( True )
		self.setFocusId( self.mCtrlGroupCHList.getId( ) )
		GuiLock2( False )


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
					lblItem = '%s'% MR_LANG('Add to Fav. Group')
					context.append( ContextItem( lblItem, CONTEXT_ACTION_ADD_TO_FAV  ) )
				else:
					#label   = '%s\t%s'% ( MR_LANG('Add to Fav. Group'), MR_LANG('None') )
					#lblItem = str('%s%s%s'%( E_TAG_COLOR_GREY3, label, E_TAG_COLOR_END ) )
					lblItem = '%s'% MR_LANG('Create New Group')
					context.append( ContextItem( lblItem, CONTEXT_ACTION_CREATE_GROUP_FAV  ) )

			else :
				head =  MR_LANG('Infomation')
				line1 = MR_LANG('Empty Channels')

				xbmcgui.Dialog( ).ok(head, line1)
				return


		elif aMode == FLAG_OPT_GROUP :
			if not self.mChannelList :
				context = []

			context.append( ContextItem( MR_LANG('Create New Group'), CONTEXT_ACTION_CREATE_GROUP_FAV ) )

			if self.mEditFavorite:
				context.append( ContextItem( '%s'% MR_LANG('Rename Fav. Group'), CONTEXT_ACTION_RENAME_FAV ) )
				context.append( ContextItem( '%s'% MR_LANG('Delete Fav. Group'), CONTEXT_ACTION_DELETE_FAV ) )


		GuiLock2( True )
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
 		dialog.doModal( )
 		GuiLock2( False )

		selectedAction = dialog.GetSelectedAction( )
		if selectedAction == -1 :
			#LOG_TRACE('CANCEL by context dialog')
			return

		if (not self.mEditFavorite) and (selectedAction == CONTEXT_ACTION_ADD_TO_FAV) :
			#can not add to Fav : no favorite group
			#LOG_TRACE('Disabled! Fav is empty, Can not add to Fav : selectedAction[%s]'% selectedAction)
			return

		if ((not self.mEditFavorite) and (selectedAction == CONTEXT_ACTION_RENAME_FAV) ) or \
		   ((not self.mEditFavorite) and (selectedAction == CONTEXT_ACTION_DELETE_FAV) ) :
			#can not rename / delete : no favorite group
			#LOG_TRACE('Disabled Fav is empty, Can not Rename or Delete Fav : selectedAction[%s]'% selectedAction)
			return
		#--------------------------------------------------------------- section 1

		grpIdx = -1
		groupName = None

		# add Fav, Ren Fav, Del Fav ==> popup select group
		if selectedAction == CONTEXT_ACTION_ADD_TO_FAV or \
		   selectedAction == CONTEXT_ACTION_RENAME_FAV or \
		   selectedAction == CONTEXT_ACTION_DELETE_FAV :
 			title = ''
 			if selectedAction == CONTEXT_ACTION_ADD_TO_FAV :   title = MR_LANG('Add to Fav. Group')
 			elif selectedAction == CONTEXT_ACTION_RENAME_FAV : title = MR_LANG('Rename Fav. Group')
 			elif selectedAction == CONTEXT_ACTION_DELETE_FAV : title = MR_LANG('Delete Fav. Group')

 			grpIdx = xbmcgui.Dialog().select(title, self.mEditFavorite)
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
		#--------------------------------------------------------------- section 2

		self.DoContextAdtion( aMode, selectedAction, groupName )
		self.mIsSave |= FLAG_MASK_ADD

		if selectedAction == CONTEXT_ACTION_CREATE_GROUP_FAV or \
			selectedAction == CONTEXT_ACTION_RENAME_FAV or \
			selectedAction == CONTEXT_ACTION_DELETE_FAV :

			self.GetFavoriteGroup( )
			#self.mCtrlListMainmenu.selectItem( E_SLIDE_MENU_FAVORITE )
			if self.mCtrlListMainmenu.getSelectedPosition( ) == E_SLIDE_MENU_FAVORITE :
				self.SubMenuAction( E_SLIDE_ACTION_MAIN, E_SLIDE_MENU_FAVORITE )


	def PopupOpt( self ) :
		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW :
			mode = FLAG_OPT_LIST
			if self.mZappingMode == ElisEnum.E_MODE_FAVORITE :
				mode = FLAG_OPT_GROUP
			else :
				mode = FLAG_OPT_LIST

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
			self.UpdateLabelInfo( )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	"""
	def AlarmDialog( self, aMsg1='', aMsg2='' ) :
		prop = ElisPropertyEnum( 'Channel Banner Duration', self.mCommander )
		bannerTimeout = prop.GetProp()
		self.mAsyncDialogShowTimer = threading.Timer( bannerTimeout, self.ShowInfoDialog( aMsg1, aMsg2 ) )
		self.mAsyncDialogShowTimer.start( )


	def ShowInfoDialog( self, aMsg1='', aMsg2='' ) :
		self.ALARM = int( params.get( "alarm", "0" ) )	
		xbmc.executebuiltin( "AlarmClock(LatestAdded,%s,%d,true)" % ( command, self.ALARM, ) )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( aMsg1, aMsg2 )
		dialog.doModal( )
	"""


	def KeySearch( self, aKey ) :
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
						self.mCtrlListCHList.selectItem(pos)
						xbmc.sleep( 20 )

						self.mCtrlSelectItem.setLabel( str('%s'% pos ) )
						self.ResetLabel( )
						self.UpdateLabelInfo( )

				else :
					self.SetChannelTune( int(inputNumber) )


	def RecordingStop( self ) :
		isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )

		isOK = False
		defaultType = ElisEnum.E_SERVICE_TYPE_TV
		defaultMode = ElisEnum.E_MODE_ALL
		defaultSort = ElisEnum.E_SORT_BY_NUMBER
		if isRunRec > 0 :
			GuiLock2( True )
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_STOP_RECORD )
			dialog.doModal( )
			GuiLock2( False )

			isOK = dialog.IsOK()
			if isOK == E_DIALOG_STATE_YES :
				isOK = True
				if self.mDataCache.GetChangeDBTableChannel( ) != -1 :
					isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )
					#self.mDataCache.Channel_GetZappingList( )

					if isRunRec > 0 :
						#use zapping table, in recording
						self.mDataCache.mChannelListDBTable = E_TABLE_ZAPPING
						self.mDataCache.LoadChannelList( FLAG_ZAPPING_LOAD, defaultType, defaultMode, defaultSort, E_REOPEN_TRUE  )

					else :
						self.mDataCache.mChannelListDBTable = E_TABLE_ALLCHANNEL
						self.mDataCache.LoadChannelList( FLAG_ZAPPING_LOAD, defaultType, defaultMode, defaultSort, E_REOPEN_TRUE  )

		if isOK == True :
			self.mDataCache.mCacheReload = True
			self.mDataCache.LoadChannelList( FLAG_ZAPPING_CHANGE, defaultType, defaultMode, defaultSort, E_REOPEN_TRUE  )
			self.ShowRecording( )
			self.ReloadChannelList( )


	def RecordingStart( self ) :
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
			self.ShowRecording()
			self.ReloadChannelList( )


	def ShowRecording( self ) :
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

			if self.mDataCache.GetChangeDBTableChannel( ) != -1 :
				defaultType = ElisEnum.E_SERVICE_TYPE_TV
				defaultMode = ElisEnum.E_MODE_ALL
				defaultSort = ElisEnum.E_SORT_BY_NUMBER
				#self.mDataCache.Channel_GetZappingList( )
				#time.sleep(0.5)
				if isRunRec > 0 :
					self.UpdateLabelGUI( self.mCtrlBtnEdit.getId( ), False, E_TAG_ENABLE )
					#use zapping table, in recording
					self.mDataCache.mChannelListDBTable = E_TABLE_ZAPPING
					self.mDataCache.mCacheReload = True
					self.mDataCache.LoadChannelList( FLAG_ZAPPING_LOAD, defaultType, defaultMode, defaultSort, E_REOPEN_TRUE  )

				else :
					self.UpdateLabelGUI( self.mCtrlBtnEdit.getId( ), True, E_TAG_ENABLE )
					#use all channel table, not recording
					self.mDataCache.mChannelListDBTable = E_TABLE_ALLCHANNEL
					self.mDataCache.mCacheReload = True
					self.mDataCache.LoadChannelList( FLAG_ZAPPING_LOAD, defaultType, defaultMode, defaultSort, E_REOPEN_TRUE  )
					#LOG_TRACE('--------------load channel len[%s]'% len(self.mChannelList) )


			return isRunRec

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def ReloadChannelList( self ) :
		time.sleep(0.5)
		self.mListItems = None
		self.mCtrlListCHList.reset( )
		self.InitSlideMenuHeader( FLAG_ZAPPING_CHANGE )
		self.RefreshSlideMenu( E_SLIDE_ALLCHANNEL, ElisEnum.E_MODE_ALL, True )
		self.InitChannelList( )

		"""
		#initialize get epg event
		self.mIsSelect = False
		self.InitEPGEvent( )

		#clear label
		self.ResetLabel( )
		self.UpdateLabelInfo( )
		"""
		self.mFlag_EditChanged = False
		self.mMoveFlag = False

		#slide close
		self.mCtrlListCHList.setEnabled(True)
		self.setFocusId( self.mCtrlGroupCHList.getId( ) )

