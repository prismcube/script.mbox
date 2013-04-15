from pvr.gui.WindowImport import *

E_LIVE_PLATE_BASE_ID					=  WinMgr.WIN_ID_LIVE_PLATE * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 


E_CONTROL_ID_IMAGE_RECORDING1 			= E_LIVE_PLATE_BASE_ID + 10
E_CONTROL_ID_LABEL_RECORDING1 			= E_LIVE_PLATE_BASE_ID + 11
E_CONTROL_ID_IMAGE_RECORDING2 			= E_LIVE_PLATE_BASE_ID + 15
E_CONTROL_ID_LABEL_RECORDING2 			= E_LIVE_PLATE_BASE_ID + 16
E_CONTROL_ID_BUTTON_PREV_EPG 			= E_LIVE_PLATE_BASE_ID + 702
E_CONTROL_ID_BUTTON_NEXT_EPG 			= E_LIVE_PLATE_BASE_ID + 706
E_CONTROL_ID_LABEL_CHANNEL_NUMBER		= E_LIVE_PLATE_BASE_ID + 601
E_CONTROL_ID_LABEL_CHANNEL_NAME			= E_LIVE_PLATE_BASE_ID + 602
E_CONTROL_ID_IMAGE_SERVICETYPE_TV		= E_LIVE_PLATE_BASE_ID + 603
E_CONTROL_ID_IMAGE_SERVICETYPE_RADIO	= E_LIVE_PLATE_BASE_ID + 604
E_CONTROL_ID_GROUP_COMPONENT_DATA		= E_LIVE_PLATE_BASE_ID + 605
E_CONTROL_ID_GROUP_COMPONENT_DOLBY 		= E_LIVE_PLATE_BASE_ID + 606
E_CONTROL_ID_GROUP_COMPONENT_HD			= E_LIVE_PLATE_BASE_ID + 607
#E_CONTROL_ID_IMAGE_LOCKED 				= E_LIVE_PLATE_BASE_ID + 651
#E_CONTROL_ID_IMAGE_ICAS 				= E_LIVE_PLATE_BASE_ID + 652
E_CONTROL_ID_LABEL_LONGITUDE_INFO		= E_LIVE_PLATE_BASE_ID + 701
E_CONTROL_ID_LABEL_EPG_NAME				= E_LIVE_PLATE_BASE_ID + 703
E_CONTROL_ID_LABEL_EPG_STARTTIME		= E_LIVE_PLATE_BASE_ID + 704
E_CONTROL_ID_LABEL_EPG_ENDTIME			= E_LIVE_PLATE_BASE_ID + 705
E_CONTROL_ID_PROGRESS_EPG 				= E_LIVE_PLATE_BASE_ID + 707


E_LIVE_PLATE_DEFAULT_FOCUS_ID			=  E_BASE_WINDOW_ID + 3621


E_CONTROL_DEFAULT_HIDE = [ 

	E_CONTROL_ID_BUTTON_BOOKMARK
]

FLAG_MASK_ADD  = 0x01
FLAG_MASK_NONE = 0x00
FLAG_CLOCKMODE_ADMYHM  = 1
FLAG_CLOCKMODE_AHM     = 2
FLAG_CLOCKMODE_HMS     = 3
FLAG_CLOCKMODE_HHMM    = 4
FLAG_CLOCKMODE_INTTIME = 5

NEXT_EPG		= 0
PREV_EPG 		= 1

CURR_CHANNEL	= 0
NEXT_CHANNEL	= 1
PREV_CHANNEL	= 2
INIT_CHANNEL	= 3


E_NOMAL_BLINKING_TIME	= 0.2
E_MAX_BLINKING_COUNT	=  10

class LivePlate( LivePlateWindow ) :
	def __init__( self, *args, **kwargs ) :
		LivePlateWindow.__init__( self, *args, **kwargs )

		self.mRecordBlinkingTimer	= None	
		self.mLocalTime = 0
		self.mCurrentChannel = None
		self.mLastChannel = None
		self.mFakeChannel = None
		self.mZappingMode = None
		self.mFlag_OnEvent = True
		self.mPincodeConfirmed = False

		self.mAutomaticHideTimer = None	
		self.mAsyncEPGTimer = None
		self.mAsyncTuneTimer = None	
		self.mAutomaticHide = True
		self.mEnableLocalThread = False
		self.mEnableBlickingTimer = False		
		self.mRecordBlinkingCount = E_MAX_BLINKING_COUNT
		

	def onInit( self ) :
		self.mEnableBlickingTimer = False
		self.setFocusId( E_LIVE_PLATE_DEFAULT_FOCUS_ID )
		self.SetActivate( True )
		self.mDataCache.Frontdisplay_SetCurrentMessage( )
		
		self.mWinId = xbmcgui.getCurrentWindowId( )

		self.SetBlinkingProperty( 'None' )
		self.mRecordBlinkingCount = 0
		
		self.SetSingleWindowPosition( E_LIVE_PLATE_BASE_ID )
		LOG_TRACE( 'winID[%d]'% self.mWinId)

		self.mCtrlLblRec1              = self.getControl( E_CONTROL_ID_LABEL_RECORDING1 )
		self.mCtrlLblRec2              = self.getControl( E_CONTROL_ID_LABEL_RECORDING2 )

		#channel, epg info
		self.mCtrlLblChannelNumber     = self.getControl( E_CONTROL_ID_LABEL_CHANNEL_NUMBER )
		self.mCtrlLblChannelName       = self.getControl( E_CONTROL_ID_LABEL_CHANNEL_NAME )
		self.mCtrlLblLongitudeInfo     = self.getControl( E_CONTROL_ID_LABEL_LONGITUDE_INFO )
		self.mCtrlLblEventName         = self.getControl( E_CONTROL_ID_LABEL_EPG_NAME )
		self.mCtrlLblEventStartTime    = self.getControl( E_CONTROL_ID_LABEL_EPG_STARTTIME )
		self.mCtrlLblEventEndTime      = self.getControl( E_CONTROL_ID_LABEL_EPG_ENDTIME )
		self.mCtrlProgress             = self.getControl( E_CONTROL_ID_PROGRESS_EPG )

		#button icon
		self.mCtrlBtnPrevEpg           = self.getControl( E_CONTROL_ID_BUTTON_PREV_EPG )
		self.mCtrlBtnNextEpg           = self.getControl( E_CONTROL_ID_BUTTON_NEXT_EPG )

		self.CheckMediaCenter( )
		#self.LoadNoSignalState( )

		self.InitControl( )
		self.SetVisibleControls( E_CONTROL_DEFAULT_HIDE, False )

		self.mFlag_OnEvent = True
		self.mFlag_ChannelChanged = False
		self.mCurrentEPG = None
		self.mEPGList = None
		self.mEPGListIdx = 0
		self.mJumpNumber = 0
		self.mZappingMode = None
		self.mEventId = 0

		self.mAsyncEPGTimer = None
		self.mAsyncTuneTimer = None
		self.mAutomaticHideTimer = None
		self.mLoopCount = 0
		self.mShowOpenWindow = None
		self.mIsShowDialog = False
		self.mEnableCasInfo = False

		self.mBannerTimeout = self.mDataCache.GetPropertyChannelBannerTime( )
		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )

		self.mZappingMode = self.mDataCache.Zappingmode_GetCurrent( )
		if not self.mZappingMode :
			self.mZappingMode = ElisIZappingMode( )

		#get channel
		self.ChannelTune( INIT_CHANNEL )
		self.LoadInit( )

		#run thread

		self.mEventBus.Register( self )
		self.mEnableLocalThread = True
		self.EPGProgressThread( )

		if self.mPincodeConfirmed :
			self.mPincodeConfirmed = False
			if self.mInitialized == False :
				self.mInitialized = True
				thread = threading.Timer( 0.3, self.ShowPincodeDialog )
				thread.start( )
				self.mAutomaticHide = True
			else :
				self.mDataCache.SetAVBlankByChannel( )


		self.RestartAutomaticHide( )


	def onAction( self, aAction ) :
		LOG_TRACE( 'action=%d' %aAction.getId( ) )	
		if self.IsActivate( ) == False  :
			LOG_TRACE( 'SKIP' )		
			return
	
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 :
			self.SetTuneByNumber( int( actionId ) - Action.REMOTE_0 )

		elif actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :
			rKey = actionId - ( Action.ACTION_JUMP_SMS2 - 2 )
			self.SetTuneByNumber( rKey )

		elif actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.Close( )
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_TIMESHIFT :
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).SetAutomaticHide( True )			
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE, WinMgr.WIN_ID_NULLWINDOW )
			else :
				if self.mShowOpenWindow == WinMgr.WIN_ID_ARCHIVE_WINDOW :
					if HasAvailableRecordingHDD( ) == False :
						return
						
					self.Close( )
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )

				else :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_SELECT_ITEM :
			return
			self.StopAutomaticHide( )
			self.SetAutomaticHide( False )
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_BUTTON_MUTE :
				self.GlobalAction( Action.ACTION_MUTE  )
			elif self.mFocusId == E_CONTROL_ID_BUTTON_PREV_EPG :
				self.EPGNavigation( PREV_EPG )

			elif self.mFocusId == E_CONTROL_ID_BUTTON_NEXT_EPG :
				self.EPGNavigation( NEXT_EPG )

			else :
				self.DialogPopup( self.mFocusId )


		elif actionId == Action.ACTION_CONTEXT_MENU :
			self.StopAutomaticHide( )
			self.DialogPopup( E_CONTROL_ID_BUTTON_DESCRIPTION_INFO )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.RestartAutomaticHide( )
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_BUTTON_PREV_EPG :			
				self.EPGNavigation( PREV_EPG )
				self.StopAutomaticHide( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.RestartAutomaticHide( )
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_BUTTON_NEXT_EPG :
				self.EPGNavigation( NEXT_EPG )
				self.StopAutomaticHide( )

		elif actionId == Action.ACTION_MOVE_UP :
			self.RestartAutomaticHide( )
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_BUTTON_NEXT_EPG or self.mFocusId == E_CONTROL_ID_BUTTON_PREV_EPG :
				self.StopAutomaticHide( )

		elif actionId == Action.ACTION_MOVE_DOWN :
			self.RestartAutomaticHide( )
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_BUTTON_NEXT_EPG or self.mFocusId == E_CONTROL_ID_BUTTON_PREV_EPG :
				self.StopAutomaticHide( )

		elif actionId == Action.ACTION_PAGE_UP :
			self.ChannelTune( NEXT_CHANNEL )
			self.RestartAutomaticHide( )

		elif actionId == Action.ACTION_PAGE_DOWN :
			self.ChannelTune( PREV_CHANNEL )
			self.RestartAutomaticHide( )

		elif actionId == Action.ACTION_MBOX_XBMC :
			if self.GetBlinkingProperty( ) != 'None' :
				LOG_TRACE( '------------22----try recording' )
				return

			status = self.mDataCache.Player_GetStatus( ) 
			if status.mMode != ElisEnum.E_MODE_LIVE :
				self.mDataCache.Player_Stop( )
				
			self.SetMediaCenter( )
			self.Close( )
			#WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MEDIACENTER, WinMgr.WIN_ID_LIVE_PLATE )
			xbmc.executebuiltin( 'ActivateWindow(Home)' )

		elif actionId == Action.ACTION_MBOX_ARCHIVE :
			if HasAvailableRecordingHDD( ) == False :
				return
				
			self.Close( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_SHOW_INFO :
			self.Close( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EPG_WINDOW )

		elif actionId == Action.ACTION_MBOX_RECORD :
			self.DialogPopup( E_CONTROL_ID_BUTTON_START_RECORDING )

		elif actionId == Action.ACTION_STOP :
			status = None
			status = self.mDataCache.Player_GetStatus( )
			if status and status.mError == 0 and status.mMode :
				ret = self.mDataCache.Player_Stop( )
			else :
				self.StopAutomaticHide( )
				self.DialogPopup( E_CONTROL_ID_BUTTON_STOP_RECORDING )

		elif actionId == Action.ACTION_PAUSE or actionId == Action.ACTION_PLAYER_PLAY :
			if self.mDataCache.GetLockedState( ) == ElisEnum.E_CC_FAILED_NO_SIGNAL :
				return -1

			if HasAvailableRecordingHDD( ) == False :
				return

			self.Close( )
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = actionId
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )

		elif actionId == Action.ACTION_MBOX_REWIND :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_TIMESHIFT :
				self.Close( )
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = actionId
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )

		elif actionId == Action.ACTION_MBOX_FF :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_TIMESHIFT :
				self.Close( )
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = actionId
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )

		elif actionId == Action.ACTION_MBOX_TVRADIO :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.mDataCache.ToggleTVRadio( )
				if ret :
					self.SetRadioScreen( )
					self.mZappingMode = self.mDataCache.Zappingmode_GetCurrent( )
					self.ChannelTune( INIT_CHANNEL )
				else :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No channels available for the selected mode' ) )
					dialog.doModal( )

		elif actionId == Action.ACTION_MBOX_TEXT :
			self.DialogPopup( E_CONTROL_ID_BUTTON_TELETEXT )

		elif actionId == Action.ACTION_MBOX_SUBTITLE :
			self.DialogPopup( E_CONTROL_ID_BUTTON_SUBTITLE )

		elif actionId == Action.ACTION_COLOR_YELLOW :
			self.StopAutomaticHide( )
			self.DoContextAction( CONTEXT_ACTION_AUDIO_SETTING )
			self.RestartAutomaticHide( )

		elif actionId == Action.ACTION_COLOR_BLUE :
			self.StopAutomaticHide( )
			self.DoContextAction( CONTEXT_ACTION_VIDEO_SETTING )
			self.RestartAutomaticHide( )


	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return

		self.StopAutomaticHide( )
		if aControlId == E_CONTROL_ID_BUTTON_MUTE :
			self.GlobalAction( Action.ACTION_MUTE  )
		elif aControlId == E_CONTROL_ID_BUTTON_PREV_EPG :
			self.SetAutomaticHide( False )
			self.EPGNavigation( PREV_EPG )

		elif aControlId == E_CONTROL_ID_BUTTON_NEXT_EPG :
			self.SetAutomaticHide( False )
			self.EPGNavigation( NEXT_EPG )
		else :
			self.DialogPopup( aControlId )


	def onFocus(self, aControlId):
		if self.IsActivate( ) == False  :
			return


	def LoadInit( self ):
		#1. Show epg information
		try :
			if self.mCurrentChannel :
				iEPG = None
				iEPG = self.mDataCache.Epgevent_GetPresent( )
				#iEPG = self.mDataCache.GetEpgeventCurrent( )
				self.mCurrentEPG = None

				if iEPG and iEPG.mError == 0 :
					if self.mCurrentChannel.mSid == iEPG.mSid and self.mCurrentChannel.mTsid == iEPG.mTsid and self.mCurrentChannel.mOnid == iEPG.mOnid : 
						self.mCurrentEPG = iEPG
						self.UpdateEpgGUI( self.mCurrentEPG )
						LOG_TRACE('-----------------init pmt')
				else :
					self.UpdateComponentGUI( self.mCurrentEPG )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		#2. Show recording Info
		self.ShowRecordingInfo( )		

		#3. Show Front disply
		if self.mCurrentEPG :
			self.mDataCache.Frontdisplay_SetIcon( ElisEnum.E_ICON_HD, iEPG.mHasHDVideo )

		self.UpdatePropertyGUI( 'InfoPlateName', E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_HOTKEY_RED,    E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_HOTKEY_GREEN,  E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_HOTKEY_YELLOW, E_TAG_TRUE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_HOTKEY_BLUE,   E_TAG_TRUE )


	def onEvent(self, aEvent):
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			#LOG_TRACE( '---------CHECK onEVENT winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId( )) )
			channel = self.mCurrentChannel
			if self.mFlag_OnEvent != True :
				#LOG_TRACE('ignore event, mFlag_OnEvent[%s]'% self.mFlag_OnEvent)
				return -1

			if channel == None :
				#LOG_TRACE('ignore event, currentChannel None, [%s]'% channel)
				return -1

			if aEvent.getName( ) == ElisEventCurrentEITReceived.getName( ) :
				if channel.mNumber != self.mFakeChannel.mNumber :
					#LOG_TRACE('ignore event, Channel: current[%s] fake[%s]'% (channel.mNumber, self.mFakeChannel.mNumber) )
					return -1

				if channel.mSid != aEvent.mSid or channel.mTsid != aEvent.mTsid or channel.mOnid != aEvent.mOnid :
					#LOG_TRACE('ignore event, same event')
					return -1

				if self.mCurrentEPG == None or aEvent.mEventId != self.mEventId :
					#LOG_TRACE('id[%s] old[%s] currentEpg[%s]'% ( aEvent.mEventId, self.mEventId, self.mCurrentEPG) )
					self.mEventId = aEvent.mEventId
					self.Epgevent_GetCurrent( channel.mSid, channel.mTsid, channel.mOnid )

			#elif aEvent.getName( ) == ElisEventChannelChangeResult.getName( ) :
			#	self.Epgevent_GetCurrent( channel.mSid, channel.mTsid, channel.mOnid )
			#	LOG_TRACE('----------------------------receive epg')

			elif aEvent.getName( ) == ElisPMTReceivedEvent.getName( ) :
				#LOG_TRACE( "--------- received ElisPMTReceivedEvent-----------" )
				self.UpdatePropertyByCacheData( E_XML_PROPERTY_TELETEXT )
				self.UpdatePropertyByCacheData( E_XML_PROPERTY_SUBTITLE )
				self.UpdatePropertyByCacheData( E_XML_PROPERTY_DOLBYPLUS )

			elif aEvent.getName( ) == ElisEventChannelChangeResult.getName( ) :
				iEPG = self.mDataCache.GetEpgeventCurrent( )
				self.UpdateChannelAndEPG( iEPG )

			elif aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
				if aEvent.mType == ElisEnum.E_EOF_END :
					LOG_TRACE( '---------CHECK onEVENT[%s] stop'% aEvent.getName( ) )
					xbmc.executebuiltin('xbmc.Action(stop)')

			elif aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or \
				 aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :

				if aEvent.getName( ) == ElisEventRecordingStarted.getName( ) :
					self.mRecordBlinkingCount = 0
					self.StopBlinkingIconTimer( )
					self.SetBlinkingProperty( 'None' )

 				self.ShowRecordingInfo( )
				self.RestartAutomaticHide( )

			elif aEvent.getName( ) == ElisEventChannelChangedByRecord.getName( ) :
				self.mJumpNumber = aEvent.mChannelNo
				self.ChannelTune( CURR_CHANNEL )
				LOG_TRACE('event[%s] tune[%s] type[%s]'% ( aEvent.getName( ), aEvent.mChannelNo, aEvent.mServiceType ) )

			#elif aEvent.getName( ) == ElisEventTuningStatus.getName( ) :
			#	LOG_TRACE('TunerNo[%s] locked[%s] quality[%s] strength[%s] frequency[%s]'% ( \
			#			aEvent.mTunerNo, aEvent.mIsLocked, aEvent.mSignalQuality, aEvent.mSignalStrength, aEvent.mFrequency ) )
				#ToDo
				#xbmcgui.Dialog( ).ok( MR_LANG('Information'), MR_LANG('No Signal') )

		else:
			LOG_TRACE( 'LivePlate winID[%d] this winID[%d]'% ( self.mWinId, xbmcgui.getCurrentWindowId( ) ) )


	def ChannelTune( self, aDir, aInitChannel = 0 ):
		if aDir == PREV_CHANNEL :
			prevChannel = self.mDataCache.Channel_GetPrev( self.mFakeChannel )
			if prevChannel == None or prevChannel.mError != 0 :
				return -1

			SetLock2(True)
			self.mFakeChannel = prevChannel
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NUMBER, ( '%s'% self.mFakeChannel.mNumber ) )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, self.mFakeChannel.mName )
			SetLock2(False)
			
			self.RestartAsyncTune( )

		elif aDir == NEXT_CHANNEL :
			nextChannel = self.mDataCache.Channel_GetNext( self.mFakeChannel )
			if nextChannel == None or nextChannel.mError != 0 :
				return -1

			SetLock2(True)
			self.mFakeChannel = nextChannel
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NUMBER, ( '%s'% self.mFakeChannel.mNumber ) )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, self.mFakeChannel.mName )
			SetLock2(False)

			self.RestartAsyncTune( )

		elif aDir == CURR_CHANNEL :
			jumpChannel = self.mDataCache.Channel_GetCurr( self.mJumpNumber )
			if jumpChannel == None or jumpChannel.mError != 0 :
				return -1
				
			SetLock2(True)
			self.mFakeChannel = jumpChannel
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NUMBER, ( '%s'% self.mFakeChannel.mNumber ) )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, self.mFakeChannel.mName )
			SetLock2(False)
			
			self.RestartAsyncTune( )

		elif aDir == INIT_CHANNEL :
			currNumber = ''
			currName = MR_LANG( 'No Channel' )
			iChannel = self.mDataCache.Channel_GetCurrent( )
			if iChannel == None or iChannel.mError != 0 :
				SetLock2(True)
				self.mCurrentChannel = None
				self.mFakeChannel =	None
				self.mLastChannel =	None
				self.mCurrentEPG = None
				SetLock2(False)				

			else :
				SetLock2(True)			
				self.mCurrentChannel = iChannel
				self.mFakeChannel    = iChannel
				self.mLastChannel    = iChannel
				currNumber = '%s'% self.mFakeChannel.mNumber
				currName = self.mFakeChannel.mName
				SetLock2(False)

			self.InitControlGUI( )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NUMBER, currNumber )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, currName )
			self.UpdateChannelGUI( )
			return


	def EPGListMoveToIndex( self ) :
		try :
			iEPG = self.mEPGList[self.mEPGListIdx]
			if iEPG :
				self.InitControlGUI( )
				SetLock2(True)
				self.mCurrentEPG = iEPG
				self.mFlag_OnEvent = False
				SetLock2(False)

				self.UpdateChannelAndEPG( iEPG )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def EPGNavigation( self, aDir ):
		if self.mEPGList :
			lastIdx = len( self.mEPGList ) - 1
			if aDir == NEXT_EPG :
				if self.mEPGListIdx + 1 > lastIdx :
					self.mEPGListIdx = lastIdx
				else :
					self.mEPGListIdx += 1

			elif aDir == PREV_EPG:
				if self.mEPGListIdx - 1 < 0 :
					self.mEPGListIdx = 0
				else :
					self.mEPGListIdx -= 1

			self.EPGListMoveToIndex( )


	@SetLock
	def Epgevent_GetCurrent( self, aSid, aTsid, aOnid ) :
		iEPG = None
		#iEPG = self.mDataCache.Epgevent_GetPresent( )
		iEPG = self.mDataCache.GetEpgeventCurrent( )
		if iEPG == None or iEPG.mError != 0 :
			return -1

		self.UpdateChannelAndEPG( iEPG )

		if not self.mCurrentEPG or \
		   iEPG.mEventId != self.mCurrentEPG.mEventId or \
		   iEPG.mSid != self.mCurrentEPG.mSid or \
		   iEPG.mTsid != self.mCurrentEPG.mTsid or \
		   iEPG.mOnid != self.mCurrentEPG.mOnid or \
		   iEPG.mAgeRating != self.mCurrentEPG.mAgeRating or \
		   iEPG.mStartTime != self.mCurrentEPG.mStartTime or \
		   iEPG.mDuration != self.mCurrentEPG.mDuration :
			#update label
			self.mCurrentEPG = iEPG
			self.mDataCache.Frontdisplay_SetIcon( ElisEnum.E_ICON_HD, iEPG.mHasHDVideo )
			#LOG_TRACE('epg DIFFER, event id[%s] current id[%s]'% (iEPG.mEventId, self.mCurrentEPG.mEventId) )
			#LOG_TRACE('-----------------------update epg[%s]'% iEPG.mEventName)

			#check : new event?
			if self.mEPGList :
				#1. aready exist? search in EPGList
				idx = 0
				self.mEPGListIdx = -1
				for item in self.mEPGList :
					#LOG_TRACE('idx[%s] item[%s]'% (idx, item) )
					if item and \
					 	item.mEventId == self.mCurrentEPG.mEventId and \
						item.mSid == self.mCurrentEPG.mSid and \
						item.mTsid == self.mCurrentEPG.mTsid and \
						item.mOnid == self.mCurrentEPG.mOnid :

						self.mEPGListIdx = idx
						#LOG_TRACE('Received ONEvent : EPGList idx moved(current idx)')

						#iEPGList=[]
						#iEPGList.append(item)
						#LOG_TRACE('1.Aready Exist: NOW EPG idx[%s] [%s]'% (idx, ClassToList('convert', iEPGList)) )
						break

					idx += 1

				#2. new epg, append to EPGList
				if self.mEPGListIdx == -1 :
					#LOG_TRACE('new EPG received, not exist in EPGList')
					oldLen = len( self.mEPGList )
					idx = 0
					for idx in range( len( self.mEPGList ) ) :
						if self.mCurrentEPG.mStartTime < self.mEPGList[idx].mStartTime :
							break

					self.mEPGListIdx = idx
					self.mEPGList = self.mEPGList[:idx]+[self.mCurrentEPG]+self.mEPGList[idx:]
					#LOG_TRACE('append new idx[%s], epgTotal:oldlen[%s] newlen[%s]'% (idx, oldLen, len(self.mEPGList)) )


	def GetEPGListByChannel( self ) :
		#do not receive onEvent
		self.mFlag_OnEvent = False
		try :
			channel = self.mCurrentChannel

			if self.mCurrentEPG == None or self.mCurrentEPG.mError != 0 :
				if not channel :
					#LOG_TRACE( 'No Channel' )
					return

				iEPG = None
				#iEPG = self.mDataCache.Epgevent_GetCurrent( channel.mSid, channel.mTsid, channel.mOnid )
				#iEPG = self.mDataCache.Epgevent_GetPresent( )
				iEPG = self.mDataCache.GetEpgeventCurrent( )
				if iEPG == None or iEPG.mError != 0 :
					#receive onEvent
					self.mFlag_OnEvent = True
					return -1
				else :
					self.mCurrentEPG = iEPG

			if channel :
				self.mEPGList = None
				iEPGList = None

				#self.mEPGList = self.mDataCache.Epgevent_GetListByChannelFromEpgCF(  channel.mSid,  channel.mTsid,  channel.mOnid )
				gmtFrom  = self.mDataCache.Datetime_GetLocalTime( )
				gmtUntil = gmtFrom + ( 3600 * 24 * 7 )
				maxCount = 100
				#self.mEPGList = self.mDataCache.Epgevent_GetListByChannel( channel.mSid, channel.mTsid, channel.mOnid, gmtFrom, gmtUntil, maxCount )
				self.mEPGList = self.mCommander.Epgevent_GetList( channel.mSid, channel.mTsid, channel.mOnid, gmtFrom, gmtUntil, maxCount )
				#LOG_TRACE('mSid[%s] mTsid[%s] mOnid[%s] gmtFrom[%s] gmtUntil[%s]'% ( channel.mSid, channel.mTsid, channel.mOnid, gmtFrom, gmtUntil ) )
				if self.mEPGList == None or self.mEPGList[0].mError != 0 :
					self.mFlag_OnEvent = True
					LOG_TRACE( 'EPGList is None\nLeave [%s]'% self.mEPGList )
					return -1

				#LOG_TRACE('-------------------------------------epgList len[%s]'% len( self.mEPGList ) )

				self.mFlag_ChannelChanged = False

				idx = 0
				self.mEPGListIdx = -1
				for item in self.mEPGList :
					#LOG_TRACE( 'idx[%s] item[%s] event[%s]'% ( idx, item, self.mCurrentEPG ) )
					if item != None and item.mError == 0 and \
					   self.mCurrentEPG != None and self.mCurrentEPG.mError == 0 :
						if item.mEventId == self.mCurrentEPG.mEventId and \
							item.mSid == self.mCurrentEPG.mSid and \
							item.mTsid == self.mCurrentEPG.mTsid and \
							item.mOnid == self.mCurrentEPG.mOnid :

							self.mEPGListIdx = idx
							break

					idx += 1

				#search not current epg
				if self.mEPGListIdx == -1 : 
					self.mEPGListIdx = 0
					#LOG_TRACE('SEARCH NOT CURRENT EPG, idx=0')

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		#receive onEvent
		self.mFlag_OnEvent = True


	def UpdateChannelAndEPG( self, aEpg = None ):
		self.UpdateChannelGUI( )
		self.UpdateEpgGUI( aEpg )


	def UpdateChannelGUI( self ) :
		ch = self.mCurrentChannel
		if ch :
			try :
				#satellite
				label = self.mDataCache.GetModeInfoByZappingMode( ch )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_LONGITUDE_INFO, label )

				#lock,cas
				if ch.mLocked :
					self.UpdatePropertyGUI( E_XML_PROPERTY_LOCK, E_TAG_TRUE )

				self.mEnableCasInfo = False
				if ch.mIsCA :
					self.UpdatePropertyGUI( E_XML_PROPERTY_CAS, E_TAG_TRUE )
					casInfo = HasCasInfoByChannel( ch )
					if casInfo and len( casInfo ) > 1 :
						self.mEnableCasInfo = True
						self.ShowCasInfoThread( casInfo )

					elif casInfo and len( casInfo ) == 1 :
						self.UpdatePropertyGUI( 'iCasInfo', casInfo[0] )

					else :
						self.UpdatePropertyGUI( 'iCasInfo', '' )

				mTPnum = self.mDataCache.Channel_GetViewingTuner( )
				if mTPnum == 0 :
					self.UpdatePropertyGUI( E_XML_PROPERTY_TUNER1, E_TAG_TRUE )
				elif mTPnum == 1 :
					self.UpdatePropertyGUI( E_XML_PROPERTY_TUNER2, E_TAG_TRUE )

	
			except Exception, e :
				LOG_TRACE( 'Error exception[%s]'% e )


	def UpdateEpgGUI( self, aEpg ) :
		self.UpdateComponentGUI( aEpg )

		if aEpg :
			try :
				#epg name
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_NAME, deepcopy( aEpg.mEventName ) )

				#start,end
				label = TimeToString( aEpg.mStartTime + self.mLocalOffset, TimeFormatEnum.E_HH_MM )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_STARTTIME, label )
				label = TimeToString( aEpg.mStartTime + aEpg.mDuration + self.mLocalOffset, TimeFormatEnum.E_HH_MM )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_ENDTIME,   label )

			except Exception, e:
				LOG_TRACE( 'Error exception[%s]'% e )

		else :
			LOG_TRACE( 'event null' )


	def UpdateComponentGUI( self, aEpg ) :
		self.UpdatePropertyByCacheData( E_XML_PROPERTY_TELETEXT )
		isSubtitle = self.UpdatePropertyByCacheData( E_XML_PROPERTY_SUBTITLE )
		if not isSubtitle :
			self.UpdatePropertyGUI( E_XML_PROPERTY_SUBTITLE, HasEPGComponent( aEpg, ElisEnum.E_HasSubtitles ) )
		if not self.UpdatePropertyByCacheData( E_XML_PROPERTY_DOLBYPLUS ) :
			self.UpdatePropertyGUI( E_XML_PROPERTY_DOLBY,HasEPGComponent( aEpg, ElisEnum.E_HasDolbyDigital ) )
		self.UpdatePropertyGUI( E_XML_PROPERTY_HD,       HasEPGComponent( aEpg, ElisEnum.E_HasHDVideo ) )


	@RunThread
	def ShowCasInfoThread( self, aCasInfo ) :
		while self.mEnableCasInfo :
			for item in aCasInfo :
				self.UpdatePropertyGUI( 'iCasInfo', item )

				loopCount = 0
				while loopCount < 3 :
					if not self.mEnableCasInfo :
						break
					loopCount += 0.5
					time.sleep( 0.5 )

			time.sleep( 0.5 )
		self.UpdatePropertyGUI( 'iCasInfo', '' )


	@RunThread
	def EPGProgressThread( self ):
		while self.mEnableLocalThread :
			#LOG_TRACE( 'repeat <<<<' )
			self.mLocalTime = self.mDataCache.Datetime_GetLocalTime( )

			if ( self.mLocalTime % 10 ) == 0 or self.mLoopCount == 3 :
				if self.mFlag_ChannelChanged or self.mEPGList == None :
					self.GetEPGListByChannel( )
				self.UpdateProgress( )

			time.sleep(1)
			self.mLoopCount += 1


	def UpdateProgress( self ) :
		try:
			if self.mCurrentEPG :
				startTime = self.mCurrentEPG.mStartTime + self.mLocalOffset
				endTime   = startTime + self.mCurrentEPG.mDuration
				pastDuration = endTime - self.mLocalTime

				if self.mLocalTime > endTime : #past
					self.mCtrlProgress.setPercent( 100 )
					return

				elif self.mLocalTime < startTime : #future
					self.mCtrlProgress.setPercent( 0 )
					return

				if pastDuration < 0 : #past
					pastDuration = 0

				if self.mCurrentEPG.mDuration > 0 :
					percent = 100 - ( pastDuration * 100.0 / self.mCurrentEPG.mDuration )
				else :
					percent = 0

				self.mCtrlProgress.setPercent( percent )
				#LOG_TRACE('progress percent[%s]'% percent)

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def InitControlGUI( self ) :
		self.UpdateControlGUI( E_CONTROL_ID_PROGRESS_EPG,          0 )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_LONGITUDE_INFO, '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_NAME,       '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_STARTTIME,  '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_ENDTIME,    '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_LONGITUDE_INFO, '' )

		tvValue = E_TAG_TRUE
		raValue = E_TAG_FALSE
		if self.mCurrentChannel :
			if self.mCurrentChannel.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
				tvValue = E_TAG_FALSE
				raValue = E_TAG_TRUE
		else :
			tvValue = E_TAG_FALSE
			raValue = E_TAG_FALSE

		self.UpdatePropertyGUI( E_XML_PROPERTY_TV,       tvValue )
		self.UpdatePropertyGUI( E_XML_PROPERTY_RADIO,    raValue )
		self.UpdatePropertyGUI( E_XML_PROPERTY_LOCK,     E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_CAS,      E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_FAV,      E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_TELETEXT, E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_SUBTITLE, E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_DOLBY,    E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_DOLBYPLUS,E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_HD,       E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_TUNER1,   E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_TUNER2,   E_TAG_FALSE )
		self.UpdatePropertyGUI( 'iCasInfo', '' )
		self.mEnableCasInfo = False


	def UpdateControlGUI( self, aCtrlID = None, aValue = None, aExtra = None ) :
		#LOG_TRACE( 'Enter control[%s] value[%s]'% (aCtrlID, aValue) )
		if aCtrlID == E_CONTROL_ID_LABEL_CHANNEL_NUMBER :
			self.mCtrlLblChannelNumber.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_CHANNEL_NAME :
			self.mCtrlLblChannelName.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_LONGITUDE_INFO :
			self.mCtrlLblLongitudeInfo.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_EPG_NAME :
			self.mCtrlLblEventName.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_EPG_STARTTIME :
			self.mCtrlLblEventStartTime.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_EPG_ENDTIME :
			self.mCtrlLblEventEndTime.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_PROGRESS_EPG :
			self.mCtrlProgress.setPercent( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_RECORDING1 :
			self.mCtrlLblRec1.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_RECORDING2 :
			self.mCtrlLblRec2.setLabel( aValue )

		#elif aCtrlID == E_CONTROL_ID_BUTTON_START_RECORDING :
		#	self.mCtrlBtnStartRec.setEnabled( aValue )


	def UpdatePropertyByCacheData( self, aPropertyID = None ) :
		pmtEvent = self.mDataCache.GetCurrentPMTEvent( self.mCurrentChannel )
		ret = UpdatePropertyByCacheData( self, pmtEvent, aPropertyID )
		return ret


	def UpdatePropertyGUI( self, aPropertyID = None, aValue = None ) :
		#LOG_TRACE( 'Enter property[%s] value[%s]'% (aPropertyID, aValue) )
		if aPropertyID == None :
			return False

		self.setProperty( aPropertyID, aValue )


	def DialogPopup( self, aAction ) :
		if self.mIsShowDialog == False :
			thread = threading.Timer( 0.1, self.ShowDialog, [aAction] )
			thread.start( )
		else :
			LOG_TRACE( 'Already opened, Dialog' )


	def ShowDialog( self, aFocusId, aVisible = False ) :
		self.mIsShowDialog = True
		self.StopAutomaticHide( )
		self.SetAutomaticHide( True )

		if aFocusId == E_CONTROL_ID_BUTTON_TELETEXT :
			if not self.mPlatform.IsPrismCube( ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No support %s' ) % self.mPlatform.GetName( ) )
				dialog.doModal( )
				self.mIsShowDialog = False
				self.RestartAutomaticHide( )
				return

			if self.mDataCache.GetLockedState( ) != ElisEnum.E_CC_SUCCESS :
				self.mIsShowDialog = False
				self.RestartAutomaticHide( )
				return

			if not self.mDataCache.Teletext_Show( ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'No teletext' ), MR_LANG( 'No teletext available' ) )
				dialog.doModal( )
			else :
				self.mIsShowDialog = False
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
				return

		elif aFocusId == E_CONTROL_ID_BUTTON_SUBTITLE :
			if not self.mPlatform.IsPrismCube( ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No support %s' ) % self.mPlatform.GetName( ) )
				dialog.doModal( )
				self.RestartAutomaticHide( )
				self.mIsShowDialog = False
				return

			if self.mDataCache.GetLockedState( ) != ElisEnum.E_CC_SUCCESS :
				LOG_TRACE( '---------Status Signal[%s]'% self.mDataCache.GetLockedState( ) )
				self.mIsShowDialog = False
				self.RestartAutomaticHide( )
				return

			ret = ShowSubtitle( )
			if ret > -1 :
				self.mIsShowDialog = False
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
				return

			elif ret == -2 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'No subtitle' ), MR_LANG( 'No subtitle available' ) )
				dialog.doModal( )

		elif aFocusId == E_CONTROL_ID_BUTTON_DESCRIPTION_INFO :
			if self.mCurrentEPG and self.mCurrentChannel and \
			   self.mCurrentChannel.mSid == self.mCurrentEPG.mSid and \
			   self.mCurrentChannel.mTsid == self.mCurrentEPG.mTsid and \
			   self.mCurrentChannel.mOnid == self.mCurrentEPG.mOnid :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_EXTEND_EPG )
				dialog.SetEPG( self.mCurrentEPG )
				dialog.SetEPGList( self.mEPGList, self.mEPGListIdx )
				dialog.doModal( )

		elif aFocusId == E_CONTROL_ID_BUTTON_START_RECORDING :
			status = self.mDataCache.GetLockedState( )
			if status != ElisEnum.E_CC_SUCCESS :
				statusSignal = MR_LANG( 'No Signal' )
				if status == ElisEnum.E_CC_FAILED_SCRAMBLED_CHANNEL :
					statusSignal = MR_LANG( 'Scrambled' )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), statusSignal )
				dialog.doModal( )
				self.mIsShowDialog = False
				self.RestartAutomaticHide( )
				return

			if RECORD_WIDTHOUT_ASKING == True :
				if self.GetBlinkingProperty( ) != 'None' :
					self.mIsShowDialog = False
					self.RestartAutomaticHide( )
					return

				self.StartRecordingWithoutAsking( )
			else :
				self.ShowRecordingStartDialog( )
		
		elif aFocusId == E_CONTROL_ID_BUTTON_STOP_RECORDING :
			self.ShowRecordingStopDialog( )

		elif aFocusId == E_CONTROL_ID_BUTTON_SETTING_FORMAT :
			self.ShowAudioVideoContext( )

		self.RestartAutomaticHide( )
		self.mIsShowDialog = False


	def StartRecordingWithoutAsking( self ) :
		runningCount = self.mDataCache.Record_GetRunningRecorderCount( )
		#LOG_TRACE( 'runningCount[%s]' %runningCount)
		if HasAvailableRecordingHDD( ) == False :
			return

		mTimer = self.mDataCache.GetRunnigTimerByChannel( )
		isOK = False

		if mTimer :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
			dialog.doModal( )

			isOK = dialog.IsOK( )
			if isOK == E_DIALOG_STATE_YES :
				self.ShowRecordingInfo( )

			if dialog.IsOK( ) == E_DIALOG_STATE_ERROR and dialog.GetConflictTimer( ) :
				RecordConflict( dialog.GetConflictTimer( ) )

			return 

		elif runningCount < 2 :
			copyTimeshift = 0
			otrInfo = self.mDataCache.Timer_GetOTRInfo( )
			localTime = self.mDataCache.Datetime_GetLocalTime( )				
			
			#check ValidEPG
			hasValidEPG = False
			if otrInfo.mHasEPG :
				if localTime >= otrInfo.mEventStartTime  and localTime < otrInfo.mEventEndTime :
					hasValidEPG = True

			if hasValidEPG == False :
				otrInfo.mHasEPG = False
				prop = ElisPropertyEnum( 'Default Rec Duration', self.mCommander )
				otrInfo.mExpectedRecordDuration = prop.GetProp( )
				otrInfo.mEventStartTime = localTime
				otrInfo.mEventEndTime = localTime +	otrInfo.mExpectedRecordDuration
				otrInfo.mEventName = self.mDataCache.Channel_GetCurrent( ).mName

			if otrInfo.mTimeshiftAvailable :
				if otrInfo.mHasEPG == True :			
					timeshiftRecordSec = int( otrInfo.mTimeshiftRecordMs/1000 )
					LOG_TRACE( 'mTimeshiftRecordMs=%dMs : %dSec' %(otrInfo.mTimeshiftRecordMs, timeshiftRecordSec ) )
				
					copyTimeshift  = localTime - otrInfo.mEventStartTime
					LOG_TRACE( 'copyTimeshift #3=%d' %copyTimeshift )
					if copyTimeshift > timeshiftRecordSec :
						copyTimeshift = timeshiftRecordSec
					LOG_TRACE( 'copyTimeshift #4=%d' %copyTimeshift )

			LOG_TRACE( 'copyTimeshift=%d' %copyTimeshift )

			if copyTimeshift <  0 or copyTimeshift > 12*3600 : #12hour * 60min * 60sec
				copyTimeshift = 0

			#expectedDuration =  self.mEndTime - self.mStartTime - copyTimeshift
			expectedDuration = otrInfo.mEventEndTime - localTime - 5 # 5sec margin

			LOG_TRACE( 'expectedDuration=%d' %expectedDuration )

			if expectedDuration < 0:
				LOG_ERR( 'Error : Already Passed' )
				expectedDuration = 0

			ret = self.mDataCache.Timer_AddOTRTimer( False, expectedDuration, copyTimeshift, otrInfo.mEventName, True, 0, 0,  0, 0 )

			#if ret[0].mParam == -1 or ret[0].mError == -1 :
			LOG_ERR( 'StartDialog ret=%s ' %ret )
			if ret and ( ret[0].mParam == -1 or ret[0].mError == -1 ) :	
				LOG_ERR( 'StartDialog ' )
				#RecordConflict( ret )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
				dialog.doModal( )

				if dialog.IsOK( ) == E_DIALOG_STATE_ERROR and dialog.GetConflictTimer( ) :
					RecordConflict( dialog.GetConflictTimer( ) )

			else :
				isOK = True

		else:
			msg = MR_LANG( 'You have reached the maximum number of%s recordings allowed'% NEW_LINE )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), msg )
			dialog.doModal( )

		if isOK :
			LOG_TRACE( 'STOP automatic hide' )
			self.StopAutomaticHide( )

			self.SetBlinkingProperty( 'True' )
			self.mRecordBlinkingCount = E_MAX_BLINKING_COUNT
			self.mEnableBlickingTimer = True			
			self.StartBlinkingIconTimer( )
			
			self.mDataCache.SetChannelReloadStatus( True )


	def RestartBlinkingIconTimer( self, aTimeout=E_NOMAL_BLINKING_TIME ) :
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Restart' )
		self.StopBlinkingIconTimer( )
		self.StartBlinkingIconTimer( aTimeout )


	def StartBlinkingIconTimer( self, aTimeout=E_NOMAL_BLINKING_TIME ) :
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Start' )	
		self.mRecordBlinkingTimer  = threading.Timer( aTimeout, self.AsyncBlinkingIcon )
		self.mRecordBlinkingTimer.start( )
	

	def StopBlinkingIconTimer( self ) :
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Stop' )	
		if self.mRecordBlinkingTimer and self.mRecordBlinkingTimer.isAlive( ) :
			self.mRecordBlinkingTimer.cancel( )
			del self.mRecordBlinkingTimer
			
		self.mRecordBlinkingTimer = None


	def AsyncBlinkingIcon( self ) :	
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Async' )	
		if self.mRecordBlinkingTimer == None or self.mEnableBlickingTimer == False:
			self.SetBlinkingProperty( 'None' )		
			LOG_WARN( 'Blinking Icon update timer expired' )
			return
			
		if self.mRecordBlinkingCount  <=  0 :
			LOG_TRACE( '++++++++++++++++++++++++++++++++++++ blinking count  is zero' )
			self.SetBlinkingProperty( 'None' )			
			return


		if self.GetBlinkingProperty( ) == 'True' :
			self.SetBlinkingProperty( 'False' )
		else :
			self.SetBlinkingProperty( 'True' )

		self.mRecordBlinkingCount = self.mRecordBlinkingCount  -1
		
		self.RestartBlinkingIconTimer( )


	def ShowRecordingStartDialog( self ) :
		runningCount = self.mDataCache.Record_GetRunningRecorderCount( )
		#LOG_TRACE( 'runningCount[%s]' %runningCount)

		if HasAvailableRecordingHDD( ) == False :
			return

		mTimer = self.mDataCache.GetRunnigTimerByChannel( )

		isOK = False
		if runningCount < 2 or mTimer :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
			dialog.doModal( )

			isOK = dialog.IsOK( )
			if isOK == E_DIALOG_STATE_YES :
				isOK = True

			if dialog.IsOK( ) == E_DIALOG_STATE_ERROR and dialog.GetConflictTimer( ) :
				RecordConflict( dialog.GetConflictTimer( ) )

		else :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'You have reached the maximum number of%s recordings allowed' )% NEW_LINE )
			dialog.doModal( )

		if isOK :
			self.mDataCache.SetChannelReloadStatus( True )
			if mTimer :
				self.ShowRecordingInfo( )


	def ShowRecordingStopDialog( self ) :
		runningCount = self.mDataCache.Record_GetRunningRecorderCount( )
		#LOG_TRACE( 'runningCount[%s]' %runningCount )

		isOK = False
		if runningCount > 0 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_STOP_RECORD )
			dialog.doModal( )

			isOK = dialog.IsOK( )
			if isOK == E_DIALOG_STATE_YES :
				isOK = True

		if isOK :
			self.mDataCache.SetChannelReloadStatus( True )


	def ShowAudioVideoContext( self ) :
		context = []
		context.append( ContextItem( 'Video format', CONTEXT_ACTION_VIDEO_SETTING ) )
		context.append( ContextItem( 'Audio track',  CONTEXT_ACTION_AUDIO_SETTING ) )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
		dialog.doModal( )

		selectAction = dialog.GetSelectedAction( )
		if selectAction == -1 :
			return

		self.DoContextAction( selectAction )


	def DoContextAction( self, aSelectAction ) :
		status = self.mDataCache.GetLockedState( )
		if status != ElisEnum.E_CC_SUCCESS :
			statusSignal = MR_LANG( 'No Signal' )
			if status == ElisEnum.E_CC_FAILED_SCRAMBLED_CHANNEL :
				statusSignal = MR_LANG( 'Scrambled' )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Attention' ), statusSignal )
			dialog.doModal( )
			return

		if aSelectAction == CONTEXT_ACTION_VIDEO_SETTING :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SET_AUDIOVIDEO )
			dialog.SetValue( aSelectAction )
 			dialog.doModal( )

 		elif aSelectAction == CONTEXT_ACTION_AUDIO_SETTING :
			getCount = self.mDataCache.Audiotrack_GetCount( )
			selectIdx= self.mDataCache.Audiotrack_GetSelectedIndex( )

			context = []
			iSelectAction = 0
			for idx in range(getCount) :
				idxTrack = self.mDataCache.Audiotrack_Get( idx )
				#LOG_TRACE('getTrack name[%s] lang[%s]'% (idxTrack.mName, idxTrack.mLang) )
				label = '%s-%s'% ( idxTrack.mName, idxTrack.mLang )

				context.append( ContextItem( label, iSelectAction ) )
				iSelectAction += 1

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context, selectIdx )
			dialog.doModal( )

			selectIdx2 = dialog.GetSelectedAction( )
			self.mDataCache.Audiotrack_select( selectIdx2 )
			#LOG_TRACE('Select[%s --> %s]'% (aSelectAction, selectIdx2) )


 	def ShowRecordingInfo( self ) :
 		#LOG_TRACE( '---------ShowRecInfo------' )
		try:
			runningRecordCount = 0
			isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )
			isRunningTimerList = self.mDataCache.Timer_GetRunningTimers( )

			if isRunningTimerList :
				runningRecordCount = len( isRunningTimerList )

			#LOG_TRACE( "runningRecordCount=%d" %runningRecordCount )

			strLabelRecord1 = ''
			strLabelRecord2 = ''
			setPropertyRecord1 = 'False'
			setPropertyRecord2 = 'False'
			if isRunRec == 1 and runningRecordCount == 1 :
				setPropertyRecord1 = 'True'
				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 0 )
				timer = isRunningTimerList[0]
				strLabelRecord1 = '(%s~%s)  %04d %s'% ( TimeToString( timer.mStartTime, TimeFormatEnum.E_HH_MM ), TimeToString( ( timer.mStartTime + timer.mDuration) , TimeFormatEnum.E_HH_MM ), int( recInfo.mChannelNo ), recInfo.mChannelName )

			elif isRunRec == 2 and runningRecordCount == 2 :
				setPropertyRecord1 = 'True'
				setPropertyRecord2 = 'True'
				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 0 )
				timer = isRunningTimerList[0]
				strLabelRecord1 = '(%s~%s)  %04d %s'% ( TimeToString( timer.mStartTime, TimeFormatEnum.E_HH_MM ), TimeToString( ( timer.mStartTime + timer.mDuration) , TimeFormatEnum.E_HH_MM ), int( recInfo.mChannelNo ), recInfo.mChannelName )
				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 1 )
				timer = isRunningTimerList[1]
				strLabelRecord2 = '(%s~%s)  %04d %s'% ( TimeToString( timer.mStartTime, TimeFormatEnum.E_HH_MM ), TimeToString( ( timer.mStartTime + timer.mDuration) , TimeFormatEnum.E_HH_MM ), int( recInfo.mChannelNo ), recInfo.mChannelName )

			btnValue = True
			if isRunRec >= 2 :
				btnValue = False

			self.UpdateControlGUI( E_CONTROL_ID_LABEL_RECORDING1, strLabelRecord1 )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_RECORDING2, strLabelRecord2 )
			self.UpdatePropertyGUI( E_XML_PROPERTY_RECORDING1, setPropertyRecord1 )
			self.UpdatePropertyGUI( E_XML_PROPERTY_RECORDING2, setPropertyRecord2 )
			#self.UpdateControlGUI( E_CONTROL_ID_BUTTON_START_RECORDING, btnValue )
			self.SetEnableControl( E_CONTROL_ID_BUTTON_START_RECORDING, btnValue )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def Close( self ) :
		self.mEnableBlickingTimer = False	
		self.mEPGList = []
		self.mEventBus.Deregister( self )
		self.mEnableLocalThread = False
		self.mEnableCasInfo = False

		self.StopBlinkingIconTimer( )
		self.SetBlinkingProperty( 'None' )

		#self.StopAsyncTune( )
		if self.mAsyncTuneTimer	and self.mAsyncTuneTimer.isAlive( ) :
			self.mAsyncTuneTimer.join( )

		self.StopAutomaticHide( )


	def SetPincodeRequest( self, aConfirm ) :
		self.mPincodeConfirmed = aConfirm


	def SetAutomaticHide( self, aHide=True ) :
		self.mAutomaticHide = aHide


	def GetAutomaticHide( self ) :
		return self.mAutomaticHide

	
	def AsyncAutomaticHide( self ) :
		#LOG_TRACE('DO WinId=%s'% xbmcgui.getCurrentWindowId( ) )
		#LOG_TRACE('DO DlgWinId=%s'% xbmcgui.getCurrentWindowDialogId( ) )
		if not self.mDataCache.GetPincodeDialog( ) :
			xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )


	def RestartAutomaticHide( self ) :
		self.StopAutomaticHide( )
		if self.mAutomaticHide :
			self.StartAutomaticHide( )

	
	def StartAutomaticHide( self ) :
		#LOG_TRACE('-----hide START')		
		self.mAutomaticHideTimer = threading.Timer( self.mBannerTimeout, self.AsyncAutomaticHide )
		self.mAutomaticHideTimer.start( )


	def StopAutomaticHide( self ) :
		#LOG_TRACE('-----hide STOP')		
		if self.mAutomaticHideTimer and self.mAutomaticHideTimer.isAlive( ) :
			self.mAutomaticHideTimer.cancel( )
			del self.mAutomaticHideTimer
			
		self.mAutomaticHideTimer = None


	def RestartAsyncTune( self ) :
		self.mFlag_ChannelChanged = True
		self.mLoopCount = 0
		self.StopAsyncTune( )
		self.StartAsyncTune( )


	def StartAsyncTune( self ) :
		self.mAsyncTuneTimer = threading.Timer( 0.5, self.AsyncTuneChannel ) 				
		self.mAsyncTuneTimer.start( )


	def StopAsyncTune( self ) :
		if self.mAsyncTuneTimer	and self.mAsyncTuneTimer.isAlive( ) :
			self.mAsyncTuneTimer.cancel( )
			del self.mAsyncTuneTimer

		self.mAsyncTuneTimer  = None


	@SetLock
	def AsyncTuneChannel( self ) :
		try :
			ret = self.mDataCache.Channel_SetCurrent( self.mFakeChannel.mNumber, self.mFakeChannel.mServiceType, None, True )
			#self.mFakeChannel.printdebug( )
			if ret == True :
				self.mDataCache.SetParentLock( True )
				self.mDataCache.SetAVBlankByChannel( self.mFakeChannel )
				self.mCurrentEPG = None
				self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
				self.mFakeChannel = self.mCurrentChannel
				self.mLastChannel = self.mCurrentChannel
				self.InitControlGUI( )
				self.UpdateChannelAndEPG( )

			else :
				LOG_ERR('Tune failed')
			
		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def SetTuneByNumber( self, aKey ) :
		if aKey == 0 :
			return -1

		self.StopAutomaticHide( )
		self.mFlag_OnEvent = False

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_JUMP )
		dialog.SetDialogProperty( str( aKey ) )
		dialog.doModal( )

		self.mFlag_OnEvent = True

		isOK = dialog.IsOK( )
		if isOK == E_DIALOG_STATE_YES :
			inputNumber = dialog.GetChannelLast( )
			#LOG_TRACE('=========== Jump chNum[%s] currentCh[%s]'% (inputNumber,self.mCurrentChannel.mNumber) )

			if self.mCurrentChannel.mNumber != int( inputNumber ) :
				self.mJumpNumber = int( inputNumber )
				self.ChannelTune( CURR_CHANNEL )

		self.RestartAutomaticHide( )


	def ShowPincodeDialog( self ) :
		if self.mDataCache.GetPincodeDialog( ) :
			LOG_TRACE( 'Aleady pincode dialog' )
			return

		self.mDataCache.SetPincodeDialog( True )
		self.mEventBus.Deregister( self )

		if self.mCurrentChannel and self.mCurrentChannel.mLocked :
			if self.mAutomaticHide == True :
				self.StopAutomaticHide( )

			if not self.mDataCache.Get_Player_AVBlank( ) :
				self.mDataCache.Player_AVBlank( True )

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_INPUT_PINCODE )
			dialog.SetTitleLabel( MR_LANG( 'Enter your PIN code' ) )
			dialog.doModal( )

			if dialog.GetNextAction( ) == dialog.E_TUNE_NEXT_CHANNEL :
				self.ChannelTune( NEXT_CHANNEL )
				self.mDataCache.LoadVolumeBySetGUI( )

			elif dialog.GetNextAction( ) == dialog.E_TUNE_PREV_CHANNEL :
				self.ChannelTune( PREV_CHANNEL )
				self.mDataCache.LoadVolumeBySetGUI( )

			elif dialog.GetNextAction( ) == dialog.E_SHOW_EPG_WINDOW :
				xbmc.executebuiltin( 'xbmc.Action(info)' )

			elif dialog.GetNextAction( ) == dialog.E_SHOW_ARCHIVE_WINDOW :
				#from pvr.HiddenTestMgr import SendCommand
				#SendCommand( 'VKEY_ARCHIVE' )
				xbmc.executebuiltin( 'xbmc.Action(DVBArchive)' )

			else :
				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					self.mDataCache.SetParentLock( False )
					if self.mDataCache.Get_Player_AVBlank( ) :
						self.mDataCache.Player_AVBlank( False )
						self.mDataCache.LoadVolumeBySetGUI( )

				LOG_TRACE( 'Has no next action' )
				if self.mAutomaticHide == True :
					self.RestartAutomaticHide( )
		else :
			if self.mDataCache.Get_Player_AVBlank( ) :
				self.mDataCache.Player_AVBlank( False )
				self.mDataCache.LoadVolumeBySetGUI( )

		if WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_LIVE_PLATE : # Still showing 
			self.mEventBus.Register( self )

		self.mDataCache.SetPincodeDialog( False )


	def SetBlinkingProperty( self, aValue ) :
		rootWinow = xbmcgui.Window( 10000 )
		rootWinow.setProperty( 'RecordBlinkingIcon', aValue )


	def GetBlinkingProperty( self ) :
		rootWinow = xbmcgui.Window( 10000 )
		return rootWinow.getProperty( 'RecordBlinkingIcon' )
	
