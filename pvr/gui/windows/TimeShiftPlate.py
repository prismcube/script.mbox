from pvr.gui.WindowImport import *
import time, math

E_TIMESHIFT_PLATE_BASE_ID = WinMgr.WIN_ID_TIMESHIFT_PLATE * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 


#control ids
E_CONTROL_ID_IMAGE_RECORDING1 		= E_TIMESHIFT_PLATE_BASE_ID + 10
E_CONTROL_ID_LABEL_RECORDING1 		= E_TIMESHIFT_PLATE_BASE_ID + 11
E_CONTROL_ID_IMAGE_RECORDING2 		= E_TIMESHIFT_PLATE_BASE_ID + 15
E_CONTROL_ID_LABEL_RECORDING2 		= E_TIMESHIFT_PLATE_BASE_ID + 16
#E_CONTROL_ID_PROGRESS_REVIEW		= E_TIMESHIFT_PLATE_BASE_ID + 200
E_CONTROL_ID_PROGRESS 				= E_TIMESHIFT_PLATE_BASE_ID + 201
E_CONTROL_ID_BUTTON_CURRENT 		= E_TIMESHIFT_PLATE_BASE_ID + 202
E_CONTROL_ID_LABEL_CURRENT 		 	= E_TIMESHIFT_PLATE_BASE_ID + 204
E_CONTROL_ID_LABEL_MODE 			= E_TIMESHIFT_PLATE_BASE_ID + 203
E_CONTROL_ID_EVENT_CLOCK 			= E_TIMESHIFT_PLATE_BASE_ID + 211
E_CONTROL_ID_LABEL_TS_START_TIME 	= E_TIMESHIFT_PLATE_BASE_ID + 221
E_CONTROL_ID_LABEL_TS_END_TIME 		= E_TIMESHIFT_PLATE_BASE_ID + 222
E_CONTROL_ID_LIST_SHOW_BOOKMARK		= E_TIMESHIFT_PLATE_BASE_ID + 500
E_CONTROL_ID_BUTTON_VOLUME 			= E_BASE_WINDOW_ID + 3701
E_CONTROL_ID_BUTTON_START_RECORDING = E_BASE_WINDOW_ID + 3702
E_CONTROL_ID_BUTTON_REWIND 			= E_BASE_WINDOW_ID + 3704
E_CONTROL_ID_BUTTON_PLAY 			= E_BASE_WINDOW_ID + 3705
E_CONTROL_ID_BUTTON_PAUSE 			= E_BASE_WINDOW_ID + 3706
E_CONTROL_ID_BUTTON_STOP 			= E_BASE_WINDOW_ID + 3707
E_CONTROL_ID_BUTTON_FORWARD 		= E_BASE_WINDOW_ID + 3708
E_CONTROL_ID_BUTTON_JUMP_RR 		= E_BASE_WINDOW_ID + 3709
E_CONTROL_ID_BUTTON_JUMP_FF 		= E_BASE_WINDOW_ID + 3710
E_CONTROL_ID_BUTTON_BOOKMARK 		= E_BASE_WINDOW_ID + 3711
E_CONTROL_ID_IMAGE_XPEED 			= E_BASE_WINDOW_ID + 3760

E_CONTROL_ID_IMAGE_BOOKMARK_POINT   = E_TIMESHIFT_PLATE_BASE_ID + 600
E_CONTROL_ID_IMAGE_BOOKMARK_CURRENT = E_TIMESHIFT_PLATE_BASE_ID + 701

E_CONTROL_ID_HOTKEY_GROUP 			= E_TIMESHIFT_PLATE_BASE_ID + 509
E_CONTROL_ID_HOTKEY_RED_IMAGE 		= E_TIMESHIFT_PLATE_BASE_ID + 511
E_CONTROL_ID_HOTKEY_RED_LABEL 		= E_TIMESHIFT_PLATE_BASE_ID + 512
E_CONTROL_ID_HOTKEY_GREEN_IMAGE 	= E_TIMESHIFT_PLATE_BASE_ID + 521
E_CONTROL_ID_HOTKEY_GREEN_LABEL 	= E_TIMESHIFT_PLATE_BASE_ID + 522
E_CONTROL_ID_HOTKEY_YELLOW_IMAGE 	= E_TIMESHIFT_PLATE_BASE_ID + 531
E_CONTROL_ID_HOTKEY_YELLOW_LABEL 	= E_TIMESHIFT_PLATE_BASE_ID + 532
E_CONTROL_ID_HOTKEY_BLUE_IMAGE 		= E_TIMESHIFT_PLATE_BASE_ID + 541
E_CONTROL_ID_HOTKEY_BLUE_LABEL 		= E_TIMESHIFT_PLATE_BASE_ID + 542

E_EXTENDED_TINY_REWIND  = E_CONTROL_ID_BUTTON_REWIND  + 1000
E_EXTENDED_TINY_FORWARD = E_CONTROL_ID_BUTTON_FORWARD + 1000

#value enum
FLAG_CLOCKMODE_ADMYHM  = 1
FLAG_CLOCKMODE_AHM     = 2
FLAG_CLOCKMODE_HMS     = 3
FLAG_CLOCKMODE_HHMM    = 4
FLAG_CLOCKMODE_INTTIME = 5

FLAG_TIMESHIFT_CLOSE = True
FLAG_STOP  = 0
FLAG_PLAY  = 1
FLAG_PAUSE = 2

E_ONINIT = None

#control position
E_CURRENT_POSX  = 0
E_CURRENT_POSY  = 0
E_PROGRESS_WIDTH_MAX = 0

E_INDEX_FIRST_RECORDING = 0
E_INDEX_SECOND_RECORDING = 1

E_DEFAULT_TRACK_MOVE = 10	#mili sec
E_DEFAULT_COUNT_AUTO_CHAPTER = 10
E_DEFAULT_LIMIT_SECOND = 10
E_MOVE_BY_TIME = 0
E_MOVE_BY_MARK = 1
E_ACCELATOR_START_INPUT = 20
E_ACCELATOR_SHIFT_SECTION = 60

E_PENDING_REPEAT_LIMIT = 10

E_TINY_XSPEED = [ 25, 50, 120 ]
E_TINY_XSPEED_SUPPORT = True


class TimeShiftPlate( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )

		self.mCurrentChannel=[]
		self.mProgress_idx = 0.0
		self.mInitCurTime = 0.0
		self.mTimeshift_staTime = 0.0
		self.mTimeshift_curTime = 0.0
		self.mTimeshift_endTime = 1.0
		self.mEventID = 0
		self.mMode = ElisEnum.E_MODE_LIVE
		self.mIsPlay = FLAG_PLAY
		self.mFlag_OnEvent = True

		self.mAsyncShiftTimer = None
		self.mAutomaticHideTimer = None
		self.mAutomaticHide = True
		self.mStartTimeShowed = False
		self.mPrekey = None
		self.mOnBlockTimer_GreenKey = 0


	def onInit( self ) :
		playingRecord = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW ).GetPlayingRecord( )
		if playingRecord :
			self.SetFrontdisplayMessage( playingRecord.mRecordName )
		else :
			self.mDataCache.Frontdisplay_SetCurrentMessage( )

		if self.mPlatform.GetProduct( ) == PRODUCT_OSCAR and ( not playingRecord ) :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Not support' ) )
			dialog.doModal( )
			WinMgr.GetInstance( ).CloseWindow( )
			return

		self.mWinId = xbmcgui.getCurrentWindowId( )
		LOG_TRACE( 'winID[%d]'% self.mWinId )

		self.mCtrlImgRec1           = self.getControl( E_CONTROL_ID_IMAGE_RECORDING1 )
		self.mCtrlLblRec1           = self.getControl( E_CONTROL_ID_LABEL_RECORDING1 )
		self.mCtrlImgRec2           = self.getControl( E_CONTROL_ID_IMAGE_RECORDING2 )
		self.mCtrlLblRec2           = self.getControl( E_CONTROL_ID_LABEL_RECORDING2 )
		#self.mCtrlProgressReview    = self.getControl( E_CONTROL_ID_PROGRESS_REVIEW )
		self.mCtrlProgress          = self.getControl( E_CONTROL_ID_PROGRESS )
		self.mCtrlBtnCurrent        = self.getControl( E_CONTROL_ID_BUTTON_CURRENT )
		self.mCtrlLblCurrent        = self.getControl( E_CONTROL_ID_LABEL_CURRENT )
		self.mCtrlLblMode           = self.getControl( E_CONTROL_ID_LABEL_MODE )
		#self.mCtrlEventClock        = self.getControl( E_CONTROL_ID_EVENT_CLOCK )
		self.mCtrlLblTSStartTime    = self.getControl( E_CONTROL_ID_LABEL_TS_START_TIME )
		self.mCtrlLblTSEndTime      = self.getControl( E_CONTROL_ID_LABEL_TS_END_TIME )

		self.mCtrlBtnVolume         = self.getControl( E_CONTROL_ID_BUTTON_VOLUME )
		self.mCtrlBtnStartRec       = self.getControl( E_CONTROL_ID_BUTTON_START_RECORDING )
		self.mCtrlBtnRewind         = self.getControl( E_CONTROL_ID_BUTTON_REWIND )
		self.mCtrlBtnPlay           = self.getControl( E_CONTROL_ID_BUTTON_PLAY )
		self.mCtrlBtnPause          = self.getControl( E_CONTROL_ID_BUTTON_PAUSE )
		self.mCtrlBtnStop           = self.getControl( E_CONTROL_ID_BUTTON_STOP )
		self.mCtrlBtnForward        = self.getControl( E_CONTROL_ID_BUTTON_FORWARD )
		self.mCtrlBtnJumpRR         = self.getControl( E_CONTROL_ID_BUTTON_JUMP_RR )
		self.mCtrlBtnJumpFF         = self.getControl( E_CONTROL_ID_BUTTON_JUMP_FF )
		self.mCtrlBtnBookMark       = self.getControl( E_CONTROL_ID_BUTTON_BOOKMARK )
		self.mCtrlBookMarkList      = self.getControl( E_CONTROL_ID_LIST_SHOW_BOOKMARK )
		self.mCtrlImgXpeed          = self.getControl( E_CONTROL_ID_IMAGE_XPEED )
		self.mCtrlImgCurrent        = self.getControl( E_CONTROL_ID_IMAGE_BOOKMARK_CURRENT )

		self.mFlag_OnEvent = True
		self.mIsTimeshiftPending = False
		self.mSpeed = 100	#normal
		self.mLocalTime = 0
		self.mUserMoveTime = 0
		self.mTotalUserMoveTime = 0
		self.mFlagUserMove = False
		self.mAccelator = 0
		self.mAsyncMove = 0
		self.mRepeatTimeout = 1
		self.mAsyncShiftTimer = None
		self.mAutomaticHideTimer = None
		self.mServiceType = ElisEnum.E_SERVICE_TYPE_TV
		self.mThumbnailHash = {}
		self.mThumbnailList = []
		self.mBookmarkList = []
		self.mPlayingRecordInfo = None
		self.mBookmarkButton = self.mDataCache.GetBookmarkButton( )
		self.mJumpToOffset = []
		self.mAccelatorSection = {}
		self.mLimitInput = E_ACCELATOR_START_INPUT
		self.mLimitShift = E_ACCELATOR_SHIFT_SECTION
		self.mPosProgress = [] 
		self.mIsShowDialog = False
		self.mStartTimeShowed = False
		self.mIsPlay = FLAG_PLAY
		self.mOldPlayTime = 0
		self.mOldStartTime = 0
		self.mIsLeftOnTimeshift = False

		self.mLocalTime = self.mDataCache.Datetime_GetLocalTime( )
		self.mBannerTimeout = self.mDataCache.GetPropertyPlaybackBannerTime( )
		#isSwap? show media surface
		if self.mDataCache.PIP_GetSwapStatus( ) :
			self.mDataCache.PIP_SwapWindow( False, False )

		self.SetRadioScreen( )
		self.ShowRecordingInfo( )

		self.InitLabelInfo( )
		self.InitTimeShift( )

		#run thread
		self.mEventBus.Register( self )
		self.mEnableLocalThread = True
		self.mThreadProgress = self.PlayProgressThread( )
		self.WaitToBuffering( )

		label = self.GetModeValue( )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_MODE, label )

		isShowSlide = self.InitPreviousAction( )
		self.InitAccelatorSection( )

		self.mPrekey = None
		if self.mInitialized == False :
			self.mAutomaticHide = True
			self.mInitialized = True

		if not isShowSlide :
			self.RestartAutomaticHide( )
		self.mOnBlockTimer_GreenKey = time.time( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.GetFocusId( )
			if self.mFocusId != E_CONTROL_ID_BUTTON_CURRENT :
				self.setFocusId( E_CONTROL_ID_BUTTON_CURRENT )
				self.RestartAutomaticHide( )
				return

			self.Close( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

		elif actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 :
			self.MoveToSeekFrame( int( actionId ) - Action.REMOTE_0 )

		elif actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :
			rKey = actionId - ( Action.ACTION_JUMP_SMS2 - 2 )
			self.MoveToSeekFrame( rKey )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_BUTTON_CURRENT :
				#if self.mSpeed != 100 :
				#	return

				self.mUserMoveTime = -1
				self.mFlagUserMove = True
				self.StopAutomaticHide( )

				if self.mIsLeftOnTimeshift :
					self.StopAsyncMove( )
					self.StartAsyncMoveByTime( True )
				else :
					self.RestartAsyncMove( )
				#LOG_TRACE('left moveTime[%s]'% self.mUserMoveTime )

			elif self.mFocusId == E_CONTROL_ID_LIST_SHOW_BOOKMARK :
				self.StopAutomaticHide( )
				self.UpdateControlGUI( E_CONTROL_ID_IMAGE_BOOKMARK_CURRENT )

			else :
				self.RestartAutomaticHide( )


		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_BUTTON_CURRENT :
				#if self.mSpeed != 100 :
				#	return

				self.mUserMoveTime = 1
				self.mFlagUserMove = True
				self.StopAutomaticHide( )
				self.RestartAsyncMove( )
				#LOG_TRACE('right moveTime[%s]'% self.mUserMoveTime )

			elif self.mFocusId == E_CONTROL_ID_LIST_SHOW_BOOKMARK :
				self.StopAutomaticHide( )
				self.UpdateControlGUI( E_CONTROL_ID_IMAGE_BOOKMARK_CURRENT )

			else :
				self.RestartAutomaticHide( )

		elif actionId == Action.ACTION_MOVE_UP :
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_BUTTON_CURRENT or \
			   self.mFocusId == E_CONTROL_ID_LIST_SHOW_BOOKMARK :
				self.StopAutomaticHide( )

				self.UpdatePropertyGUI( 'iButtonShow', E_TAG_FALSE )
				#self.UpdateBookmarkByPoint( )
				if self.mFocusId == E_CONTROL_ID_LIST_SHOW_BOOKMARK :
					self.UpdateControlGUI( E_CONTROL_ID_IMAGE_BOOKMARK_CURRENT )
				else :
					self.RestartAutomaticHide( )

			else :
				self.RestartAutomaticHide( )

		elif actionId == Action.ACTION_MOVE_DOWN :
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_BUTTON_CURRENT :
				self.StopAutomaticHide( )

				if self.getProperty( 'iButtonShow' ) == E_TAG_TRUE :
					self.UpdatePropertyGUI( 'iButtonShow', E_TAG_FALSE )
					#self.UpdateBookmarkByPoint( )

				if self.mFocusId != E_CONTROL_ID_LIST_SHOW_BOOKMARK :
					self.RestartAutomaticHide( )

			elif self.mFocusId >= E_CONTROL_ID_BUTTON_VOLUME and self.mFocusId <= E_CONTROL_ID_BUTTON_BOOKMARK :
				self.StopAutomaticHide( )
				self.UpdatePropertyGUI( 'iButtonShow', E_TAG_TRUE )
				time.sleep( 0.2 )
				if self.mSpeed == 100 :
					self.UpdateSetFocus( E_CONTROL_ID_BUTTON_JUMP_RR )
				else :
					ret = self.ShowButtonFocus( )

			else :
				self.RestartAutomaticHide( )


		elif actionId == Action.ACTION_PAGE_DOWN :
			if self.mMode == ElisEnum.E_MODE_PVR :
				self.onClick( E_CONTROL_ID_BUTTON_JUMP_RR )
				return

			prevChannel = None
			prevChannel = self.mDataCache.Channel_GetPrev( self.mDataCache.Channel_GetCurrent( ) )
			if prevChannel :
				self.mDataCache.Channel_SetCurrent( prevChannel.mNumber, prevChannel.mServiceType, None, True )			
				nextWindow = WinMgr.WIN_ID_LIVE_PLATE
				if self.mMode == ElisEnum.E_MODE_PVR :
					nextWindow = WinMgr.WIN_ID_ARCHIVE_WINDOW
				else :
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )

				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( nextWindow, WinMgr.WIN_ID_NULLWINDOW )
				
			
		elif actionId == Action.ACTION_PAGE_UP :
			if self.mMode == ElisEnum.E_MODE_PVR :
				self.onClick( E_CONTROL_ID_BUTTON_JUMP_FF )
				return

			nextChannel = None
			nextChannel = self.mDataCache.Channel_GetNext( self.mDataCache.Channel_GetCurrent( ) )
			if nextChannel :
				self.mDataCache.Channel_SetCurrent( nextChannel.mNumber, nextChannel.mServiceType, None, True )
				nextWindow = WinMgr.WIN_ID_LIVE_PLATE
				if self.mMode == ElisEnum.E_MODE_PVR :
					nextWindow = WinMgr.WIN_ID_ARCHIVE_WINDOW
				else :
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )

				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( nextWindow, WinMgr.WIN_ID_NULLWINDOW )


		elif actionId == Action.ACTION_CONTEXT_MENU :
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_LIST_SHOW_BOOKMARK :
				self.ShowDialog( E_CONTROL_ID_LIST_SHOW_BOOKMARK )
				return

			if self.mMode == ElisEnum.E_MODE_PVR :
				self.Close( )
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_INFO_PLATE ).SetAutomaticHide( True )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_INFO_PLATE )
			else :
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )

		elif actionId == Action.ACTION_PLAYER_PLAY :
			if self.mSpeed == 100 :
				self.onClick( E_CONTROL_ID_BUTTON_PAUSE )
			else :
				self.onClick( E_CONTROL_ID_BUTTON_PLAY )

		elif actionId == Action.ACTION_STOP :
			self.onClick( E_CONTROL_ID_BUTTON_STOP )

		elif actionId == Action.ACTION_MBOX_REWIND :
			if self.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
				return

			self.onClick( E_CONTROL_ID_BUTTON_REWIND )

		elif actionId == Action.ACTION_MBOX_FF : #no service
			if self.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
				return

			self.onClick( E_CONTROL_ID_BUTTON_FORWARD )

		elif actionId == Action.ACTION_MBOX_RECORD :
			#self.DialogPopup( E_CONTROL_ID_BUTTON_START_RECORDING )
			self.TimeshiftAction( E_CONTROL_ID_BUTTON_STOP )
			xbmc.executebuiltin('xbmc.Action(DVBRecord)')

		elif actionId == Action.ACTION_MBOX_ARCHIVE :
			if not HasAvailableRecordingHDD( ) :
				return

			self.Close( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_MBOX_TEXT :
			if not self.mDataCache.Teletext_Show( ) :
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).DialogPopupOK( actionId )
			else :
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW, WinMgr.WIN_ID_NULLWINDOW )
				return

		elif actionId == Action.ACTION_MBOX_SUBTITLE :
			ret = ShowSubtitle( )
			if ret > -1 :
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
				return
			elif ret == -2 :
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).DialogPopupOK( actionId )

		elif actionId == Action.ACTION_SHOW_INFO :
			if self.mMode == ElisEnum.E_MODE_PVR :
				msg = MR_LANG( 'Try again after stopping playback' )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), msg )
				dialog.doModal( )
			else :
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EPG_WINDOW, WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_COLOR_GREEN :
			if ( time.time( ) - self.mOnBlockTimer_GreenKey ) <= 1 :
				LOG_TRACE( 'blocking time Green key' )
				return

			self.mOnBlockTimer_GreenKey = time.time( )

			if self.mMode == ElisEnum.E_MODE_PVR :
				self.StopAutomaticHide( )
				self.DoContextAction( CONTEXT_ACTION_ADD_TO_BOOKMARK )

			elif self.mMode != ElisEnum.E_MODE_PVR and self.mDataCache.GetLinkageService(  ):
				#self.TimeshiftAction( E_CONTROL_ID_BUTTON_STOP )
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).ShowLinkageChannels( )

		elif actionId == Action.ACTION_COLOR_YELLOW :
			self.ShowDialog( E_CONTROL_ID_BUTTON_SETTING_FORMAT )

		elif actionId == Action.ACTION_COLOR_BLUE :
			self.ShowDialog( E_CONTROL_ID_BUTTON_PIP )


	def onClick( self, aControlId ):
		if aControlId >= E_CONTROL_ID_BUTTON_REWIND and aControlId <= E_CONTROL_ID_BUTTON_JUMP_FF :
			self.StopAutomaticHide( )
			ret = self.TimeshiftAction( aControlId )
			if ret == -1 :
				LOG_TRACE( '----------- timeshift fault' )
				self.ShowDialogByPlayFault( )
				return

			if aControlId == E_CONTROL_ID_BUTTON_PLAY or aControlId == E_CONTROL_ID_BUTTON_PAUSE :
				aControlId = E_CONTROL_ID_BUTTON_PLAY
				if self.mIsPlay == FLAG_PAUSE :
					aControlId = E_CONTROL_ID_BUTTON_PAUSE
					self.RestartAutomaticHide( )

			if self.getProperty( 'iButtonShow' ) == E_TAG_TRUE :
				self.UpdateSetFocus( aControlId )
				LOG_TRACE('----------focus[%s]'% aControlId )

		elif aControlId == E_CONTROL_ID_BUTTON_VOLUME :
			self.GlobalAction( Action.ACTION_MUTE )
			#xbmc.executebuiltin('xbmc.Action(mute)')
			self.StopAutomaticHide( )

		elif aControlId == E_CONTROL_ID_BUTTON_START_RECORDING :
			#self.DialogPopup( E_CONTROL_ID_BUTTON_START_RECORDING )
			self.TimeshiftAction( E_CONTROL_ID_BUTTON_STOP )
			xbmc.executebuiltin('xbmc.Action(DVBRecord)')

		elif aControlId == E_CONTROL_ID_BUTTON_BOOKMARK :
			self.StopAutomaticHide( )
			self.ShowDialog( E_CONTROL_ID_BUTTON_BOOKMARK )
			#self.RestartAutomaticHide( )

		elif aControlId == E_CONTROL_ID_LIST_SHOW_BOOKMARK :
			if self.mMode == ElisEnum.E_MODE_PVR : 
				self.DoContextAction( CONTEXT_ACTION_RESUME_FROM )


	def onFocus( self, aControlId ):
		pass


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			#LOG_TRACE( '---------CHECK onEVENT winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId( )) )
			if aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
				LOG_TRACE( 'ElisEventPlaybackEOF mType[%d]'% ( aEvent.mType ) )

				if self.mFlag_OnEvent != True :
					return -1

				if aEvent.mType == ElisEnum.E_EOF_START :
					self.TimeshiftAction( E_CONTROL_ID_BUTTON_PLAY )
					LOG_TRACE( 'EventRecv EOF_START' )

				elif aEvent.mType == ElisEnum.E_EOF_END :
					LOG_TRACE( 'EventRecv EOF_END' )
					#xbmc.executebuiltin('xbmc.Action(stop)')  <-- if show busyDialog then can not onAction
					thread = threading.Timer( 0.1, self.TimeshiftAction, [E_CONTROL_ID_BUTTON_STOP] )
					thread.start( )

			elif aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or \
				 aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :

				self.ShowRecordingInfo( )
				self.RestartAutomaticHide( )
				#self.mDataCache.SetChannelReloadStatus( True )

			elif aEvent.getName( ) == ElisEventChannelChangedByRecord.getName( ) :
				xbmc.executebuiltin('xbmc.Action(previousmenu)')

			elif aEvent.getName( ) == ElisEventJpegEncoded.getName( ) :
				#self.ShowBookmark( )
				LOG_TRACE('--------------------------onEvent[%s]'% aEvent.getName() )
				self.UpdateBookmarkByThumbnail( aEvent.mRecordKey, aEvent.mTimeMS )

			elif aEvent.getName( ) == ElisEventViewTimerStatus.getName( ) :
				if aEvent.mResult == ElisEnum.E_VIEWTIMER_SUCCESS :
					thread = threading.Timer( 0.1, self.TimeshiftAction, [E_CONTROL_ID_BUTTON_STOP] )
					thread.start( )

		else:
			LOG_TRACE( 'TimeshiftPlate winID[%d] this winID[%d]'% ( self.mWinId, xbmcgui.getCurrentWindowId( ) ) )


	def InitPreviousAction( self ) :
		isShowSlide = False
		#LOG_TRACE( '--------------------------getLabel[%s]'% self.getControl( E_CONTROL_ID_HOTKEY_GREEN_LABEL ) )
		hasLinkageService = self.mDataCache.GetLinkageService( )

		if E_V1_2_APPLY_TEXTWIDTH_LABEL :
			ctrlGreen  = self.getControl( E_CONTROL_ID_HOTKEY_GREEN_LABEL )
			ctrlYellow = self.getControl( E_CONTROL_ID_HOTKEY_YELLOW_LABEL )
			ctrlBlue   = self.getControl( E_CONTROL_ID_HOTKEY_BLUE_LABEL )
			lblGreen   = ctrlGreen.getLabel( )
			lblYellow  = ctrlYellow.getLabel( )
			lblBlue    = ctrlBlue.getLabel( )

			txtGreen = MR_LANG( 'Bookmark' )
			if self.mMode != ElisEnum.E_MODE_PVR and hasLinkageService :
				txtGreen = MR_LANG( 'Multi-Feed' )

			ResizeImageWidthByTextSize( ctrlGreen, self.getControl( E_CONTROL_ID_HOTKEY_GREEN_IMAGE ), txtGreen, self.getControl( ( E_CONTROL_ID_HOTKEY_GREEN_IMAGE - 1 ) ) )
			ResizeImageWidthByTextSize( ctrlYellow, self.getControl( E_CONTROL_ID_HOTKEY_YELLOW_IMAGE ), MR_LANG( 'A / V' ), self.getControl( ( E_CONTROL_ID_HOTKEY_YELLOW_IMAGE - 1 ) ) )
			ResizeImageWidthByTextSize( ctrlBlue, self.getControl( E_CONTROL_ID_HOTKEY_BLUE_IMAGE ), MR_LANG( 'PIP' ), self.getControl( ( E_CONTROL_ID_HOTKEY_BLUE_IMAGE - 1 ) ) )
			if lblGreen and len( lblGreen ) > 9 or \
			   lblYellow and len( lblYellow ) > 9 or \
			   lblBlue and len( lblBlue ) > 9 :
				self.getControl( E_CONTROL_ID_HOTKEY_GROUP ).setPosition( -20, 0 )
				#LOG_TRACE( '-----------------------------------rePosition, [%s] [%s] [%s]'% (lblGreen,lblYellow,lblBlue) )

		self.UpdatePropertyGUI( E_XML_PROPERTY_HOTKEY_RED,    E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_HOTKEY_YELLOW, E_TAG_TRUE )
		if E_V1_2_APPLY_PIP :
			self.UpdatePropertyGUI( E_XML_PROPERTY_HOTKEY_BLUE,   E_TAG_TRUE )

		visible = E_TAG_FALSE
		if self.mMode == ElisEnum.E_MODE_PVR : 
			visible = E_TAG_TRUE
			if not E_V1_2_APPLY_TEXTWIDTH_LABEL :
				iRussian = E_TAG_FALSE
				if XBMC_GetCurrentLanguage( ) == 'Russian' :
					iRussian = E_TAG_TRUE
				self.UpdatePropertyGUI( 'iHotkeyGreenRussian', '%s'% iRussian )

		else :
			if hasLinkageService :
				visible = E_TAG_TRUE
		self.UpdatePropertyGUI( E_XML_PROPERTY_HOTKEY_GREEN,   visible )

		if self.mPrekey :
			self.setFocusId( E_CONTROL_ID_BUTTON_CURRENT )
			#self.UpdateSetFocus( E_CONTROL_ID_BUTTON_CURRENT, 5 )

			if self.mPrekey == Action.ACTION_MBOX_REWIND :
				self.onClick( E_CONTROL_ID_BUTTON_REWIND )

			elif self.mPrekey == Action.ACTION_MBOX_FF :
				self.onClick( E_CONTROL_ID_BUTTON_FORWARD )

			elif self.mPrekey == Action.ACTION_PAGE_UP :
				self.onClick( E_CONTROL_ID_BUTTON_JUMP_FF )

			elif self.mPrekey == Action.ACTION_PAGE_DOWN :
				self.onClick( E_CONTROL_ID_BUTTON_JUMP_RR )

			elif self.mPrekey == Action.ACTION_PAUSE or self.mPrekey == Action.ACTION_PLAYER_PLAY :
				ret = True
				if self.mSpeed == 100 :
					ret = self.onClick( E_CONTROL_ID_BUTTON_PAUSE )
				else :
					ret = self.onClick( E_CONTROL_ID_BUTTON_PLAY )

				if ret == -1 :
					LOG_TRACE( '----------- timeshift fault' )
					self.ShowDialogByPlayFault( )
					return

			elif self.mPrekey == Action.ACTION_MOVE_LEFT or self.mPrekey == Action.ACTION_MOVE_RIGHT :
				self.StopAutomaticHide( )

				ret = self.TimeshiftAction( E_CONTROL_ID_BUTTON_PLAY )
				if ret == -1 :
					LOG_TRACE( '----------- timeshift fault' )
					self.ShowDialogByPlayFault( )
					return

				self.InitTimeShift( )

				self.mUserMoveTime = -1
				if self.mPrekey == Action.ACTION_MOVE_RIGHT :
					self.mUserMoveTime = 1

				#self.mFlagUserMove = True
				self.StopAutomaticHide( )
				self.StartAsyncMoveByTime( True )
				self.mDataCache.Frontdisplay_SetIcon( ElisEnum.E_ICON_PLAY, 1 )
				self.mDataCache.Frontdisplay_SetIcon( ElisEnum.E_ICON_PAUSE, 0 )

				self.mIsLeftOnTimeshift = True

				self.setFocusId( E_CONTROL_ID_BUTTON_CURRENT )
				#self.UpdateSetFocus( E_CONTROL_ID_BUTTON_CURRENT, 5 )
				#LOG_TRACE( '-----------play focus[%s]'% self.getFocusId( ) )

			elif self.mPrekey == E_DEFAULT_ACTION_CLICK_EVENT + CONTEXT_ACTION_SHOW_BOOKMARK :
				self.setFocusId( E_CONTROL_ID_BUTTON_BOOKMARK )
				self.UpdatePropertyGUI( 'iButtonShow', E_TAG_TRUE )
				self.onClick( E_CONTROL_ID_BUTTON_BOOKMARK )
				isShowSlide = True


		else :
			self.setFocusId( E_CONTROL_ID_BUTTON_CURRENT )
			#self.UpdateSetFocus( E_CONTROL_ID_BUTTON_CURRENT )
			self.ShowButtonFocus( )

			status = E_CONTROL_ID_BUTTON_PAUSE
			if self.mSpeed == 100 :
				status = E_CONTROL_ID_BUTTON_PLAY
			elif self.mSpeed < 0 :
				status = E_CONTROL_ID_BUTTON_REWIND
			elif self.mSpeed > 100 or self.mSpeed in E_TINY_XSPEED :
				status = E_CONTROL_ID_BUTTON_FORWARD

			self.GetNextSpeed( E_ONINIT )
			self.ShowStatusByButton( status )


		LOG_TRACE('default focus[%s]'% self.getFocusId( ) )
		return isShowSlide


	def TimeshiftAction( self, aFocusId ) :
		ret = False

		if aFocusId == E_CONTROL_ID_BUTTON_PLAY :
			if self.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.mDataCache.Player_StartTimeshiftPlayback( ElisEnum.E_PLAYER_TIMESHIFT_START_PAUSE, 0 )
				if not ret :
					ret = -1

			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				ret = self.mDataCache.Player_Resume( )

			elif self.mMode == ElisEnum.E_MODE_PVR :
				ret = self.mDataCache.Player_Resume( )

			LOG_TRACE( 'play_resume( ) ret[%s]'% ret )

			if ret == True :
				self.mIsPlay = FLAG_PAUSE
				label = self.GetModeValue( )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_MODE, label )
				# toggle
				self.UpdateControlGUI( E_CONTROL_ID_BUTTON_PLAY, False )
				self.UpdateControlGUI( E_CONTROL_ID_BUTTON_PAUSE, True )

				#blocking release
				#if self.mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
				#	self.SetBlockingButtonEnable( True )

		elif aFocusId == E_CONTROL_ID_BUTTON_PAUSE :
			if self.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.mDataCache.Player_StartTimeshiftPlayback( ElisEnum.E_PLAYER_TIMESHIFT_START_PAUSE, 0 )
				if not ret :
					ret = -1

			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				ret = self.mDataCache.Player_Pause( )

			elif self.mMode == ElisEnum.E_MODE_PVR :
				ret = self.mDataCache.Player_Pause( )

			LOG_TRACE( 'play_pause( ) ret[%s]'% ret )
			if ret == True :
				self.mIsPlay = FLAG_PLAY

				# toggle
				self.UpdateControlGUI( E_CONTROL_ID_BUTTON_PLAY, True )
				self.UpdateControlGUI( E_CONTROL_ID_BUTTON_PAUSE, False )

				#blocking
				#if self.mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
				#	self.SetBlockingButtonEnable( False )

		elif aFocusId == E_CONTROL_ID_BUTTON_STOP :
			visible = E_TAG_TRUE
			#LOG_TRACE('---------------------------status[%s]'% self.mMode )
			if self.mMode == ElisEnum.E_MODE_LIVE :
				visible = E_TAG_FALSE
				self.mIsPlay = FLAG_STOP
				ret = self.mDataCache.Player_Stop( )
				self.Close( )
				#WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
				#WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE, WinMgr.WIN_ID_NULLWINDOW )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				visible = E_TAG_FALSE
				self.mIsPlay = FLAG_STOP
				ret = self.mDataCache.Player_Stop( )
				self.Close( )
				#WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE, WinMgr.WIN_ID_NULLWINDOW )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

			elif self.mMode == ElisEnum.E_MODE_PVR :
				visible = E_TAG_FALSE
				self.mIsPlay = FLAG_STOP
				ret = self.mDataCache.Player_Stop( )
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )

			self.UpdatePropertyGUI( 'iButtonShow', visible )
			return

		elif aFocusId == E_CONTROL_ID_BUTTON_REWIND :
			if self.mSpeed <= -6400 :
				return 

			nextSpeed = 100
			nextSpeed = self.GetNextSpeed( aFocusId )

			ret = 0
			if self.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.mDataCache.Player_SetSpeed( nextSpeed )

			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				ret = self.mDataCache.Player_SetSpeed( nextSpeed )

			elif self.mMode == ElisEnum.E_MODE_PVR :
				ret = self.mDataCache.Player_SetSpeed( nextSpeed )

			LOG_WARN( 'status =%d ret[%s], player_SetSpeed[%s]'% ( self.mMode , ret, nextSpeed ) )
			if ret :
				self.mIsPlay = FLAG_PLAY
				#LOG_WARN( 'status =%d ret[%s], player_SetSpeed[%s]'% ( self.mMode , ret, nextSpeed ) )

		elif aFocusId == E_CONTROL_ID_BUTTON_FORWARD :
			if self.mSpeed >= 6400 :
				return 

			nextSpeed = 100
			nextSpeed = self.GetNextSpeed( aFocusId )

			if self.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.mDataCache.Player_SetSpeed( nextSpeed )

			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				ret = self.mDataCache.Player_SetSpeed( nextSpeed )

			elif self.mMode == ElisEnum.E_MODE_PVR :
				ret = self.mDataCache.Player_SetSpeed( nextSpeed )

			LOG_WARN( 'status =%d ret[%s], player_SetSpeed[%s]'% ( self.mMode , ret, nextSpeed ) )
			if ret :
				self.mIsPlay = FLAG_PLAY
				#LOG_WARN( 'status =%d ret[%s], player_SetSpeed[%s]'% ( self.mMode , ret, nextSpeed ) )

		elif aFocusId == E_CONTROL_ID_BUTTON_JUMP_RR :
			#if self.mSpeed == 0 :
			#	return

			#self.JumpToTrack( aFocusId )
			self.RestartAsyncMove( aFocusId )

		elif aFocusId == E_CONTROL_ID_BUTTON_JUMP_FF :
			#if self.mSpeed == 0 :
			#	return

			#self.JumpToTrack( aFocusId )
			self.RestartAsyncMove( aFocusId )

		if ret :
			self.ShowStatusByButton( aFocusId )

		return ret


	def InitLabelInfo( self ) :
		global E_CURRENT_POSX, E_CURRENT_POSY, E_PROGRESS_WIDTH_MAX
		E_PROGRESS_WIDTH_MAX = self.mCtrlProgress.getWidth( )
		E_CURRENT_POSX  = int( self.getProperty( 'currentPosX' ) )
		E_CURRENT_POSY  = int( self.getProperty( 'currentPosY' ) ) + 4
		#LOG_TRACE('---------getWidth[%s] pos[%s,%s] curr[%s,%s]'% ( E_PROGRESS_WIDTH_MAX, E_CURRENT_POSX, E_CURRENT_POSY ) )

		self.InitTimeShift( )
		visiblePoint = E_TAG_FALSE
		if self.mMode == ElisEnum.E_MODE_PVR :
			visiblePoint = E_TAG_TRUE
			#self.mBookmarkButton = self.mDataCache.GetBookmarkButton( )

		self.setProperty( 'BookMarkPointShow', visiblePoint )

		self.InitBookmarkThumnail( )
		self.mEventCopy = []
		self.UpdatePropertyGUI( 'iButtonShow', E_TAG_FALSE )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_MODE,          '' )

		#self.UpdateControlGUI( E_CONTROL_ID_LABEL_TS_START_TIME, '' )
		#self.UpdateControlGUI( E_CONTROL_ID_LABEL_TS_END_TIME,   '' )
		#self.UpdateControlGUI( E_CONTROL_ID_PROGRESS,             0 )
		#self.UpdateControlGUI( E_CONTROL_ID_BUTTON_CURRENT, '', E_TAG_LABEL )
		#self.UpdateControlGUI( E_CONTROL_ID_BUTTON_CURRENT, E_CURRENT_POSY, E_TAG_POSY )
		self.UpdateProgress( )

		visible = True
		zappingMode = self.mDataCache.Zappingmode_GetCurrent( )
		if zappingMode and zappingMode.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
			self.mServiceType = ElisEnum.E_SERVICE_TYPE_RADIO
			visible = False

		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_REWIND, visible, E_TAG_VISIBLE )
		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_FORWARD , visible, E_TAG_VISIBLE )
		self.UpdatePropertyGUI( 'IsShift', 'False' )


	def SetBlockingButtonEnable( self, aValue ) :
		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_REWIND, aValue, E_TAG_ENABLE )
		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_FORWARD, aValue, E_TAG_ENABLE )
		strValue = '%s'% aValue


	def UpdateControlGUI( self, aCtrlID = None, aValue = None, aExtra = None ) :
		#LOG_TRACE( 'Enter control[%s] value[%s] extra[%s]'% (aCtrlID, aValue, aExtra) )

		if aCtrlID == E_CONTROL_ID_BUTTON_VOLUME :
			self.mCtrlBtnVolume.setVisible( aValue )

		elif aCtrlID == E_CONTROL_ID_BUTTON_START_RECORDING :
			if aExtra == E_TAG_ENABLE :
				self.mCtrlBtnStartRec.setEnabled( aValue )
			elif aExtra == E_TAG_VISIBLE :
				self.mCtrlBtnStartRec.setVisible( aValue )

		elif aCtrlID == E_CONTROL_ID_BUTTON_PLAY :
			self.mCtrlBtnPlay.setVisible( aValue )

		elif aCtrlID == E_CONTROL_ID_BUTTON_PAUSE :
			self.mCtrlBtnPause.setVisible( aValue )

		elif aCtrlID == E_CONTROL_ID_BUTTON_STOP :
			self.mCtrlBtnStop.setVisible( aValue )

		elif aCtrlID == E_CONTROL_ID_BUTTON_REWIND :
			if aExtra == E_TAG_ENABLE :
				self.mCtrlBtnRewind.setEnabled( aValue )
			elif aExtra == E_TAG_VISIBLE :
				self.mCtrlBtnRewind.setVisible( aValue )

		elif aCtrlID == E_CONTROL_ID_BUTTON_FORWARD :
			if aExtra == E_TAG_ENABLE :
				self.mCtrlBtnForward.setEnabled( aValue )
			elif aExtra == E_TAG_VISIBLE :
				self.mCtrlBtnForward.setVisible( aValue )

		#elif aCtrlID == E_CONTROL_ID_EVENT_CLOCK :
		#	self.mCtrlEventClock.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_PROGRESS :
			self.mCtrlProgress.setPercent( aValue )

		#elif aCtrlID == E_CONTROL_ID_PROGRESS_REVIEW :
		#	self.mCtrlProgressReview.setPercent( aValue )

		elif aCtrlID == E_CONTROL_ID_BUTTON_CURRENT :
			if aExtra == E_TAG_LABEL:
				#self.mCtrlBtnCurrent.setLabel( aValue )
				self.mCtrlLblCurrent.setLabel( aValue )
			elif aExtra == E_TAG_POSY:
				self.mCtrlBtnCurrent.setPosition( aValue + E_CURRENT_POSX, E_CURRENT_POSY )
				self.mCtrlLblCurrent.setPosition( aValue + E_CURRENT_POSX + 5, E_CURRENT_POSY + 10 )
			elif aExtra == E_TAG_ENABLE:
				self.mCtrlBtnCurrent.setEnabled( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_TS_START_TIME :
			self.mCtrlLblTSStartTime.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_TS_END_TIME :
			self.mCtrlLblTSEndTime.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_RECORDING1 :
			self.mCtrlLblRec1.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_RECORDING2 :
			self.mCtrlLblRec2.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_MODE :
			self.mCtrlLblMode.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_BUTTON_BOOKMARK :
			if aExtra == E_TAG_VISIBLE :
				self.mCtrlBtnBookMark.setVisible( aValue )

		elif aCtrlID == E_CONTROL_ID_IMAGE_BOOKMARK_CURRENT :
			idx = self.mCtrlBookMarkList.getSelectedPosition( )
			if self.mBookmarkList and len( self.mBookmarkList ) > 0 :
				controlId = self.mDataCache.GetBookmarkHash( self.mBookmarkList[idx].mOffset )
				if controlId == -1 :
					controlId = 0

				pos = self.mBookmarkButton[controlId].getPosition( )
				self.mCtrlImgCurrent.setPosition( pos[0], 0 )
				#LOG_TRACE( 'refresh idx[%s] controlid[%s] pos[%s]'% ( idx, controlId, pos ) )

		"""
		elif aCtrlID == E_CONTROL_ID_BUTTON_JUMP_RR :
			if aExtra == E_TAG_ENABLE:
				self.mCtrlBtnJumpRR.setEnabled( aValue )

		elif aCtrlID == E_CONTROL_ID_BUTTON_JUMP_FF :
			if aExtra == E_TAG_ENABLE:
				self.mCtrlBtnJumpFF.setEnabled( aValue )
		"""


	def UpdatePropertyGUI( self, aPropertyID = None, aValue = None ) :
		#LOG_TRACE( 'Enter property[%s] value[%s]'% (aPropertyID, aValue) )
		if aPropertyID == None :
			return

		self.setProperty( aPropertyID, aValue )


	def ShowStatusByButton( self, aFocusId ) :
		iRew = E_TAG_FALSE
		iPly = E_TAG_FALSE
		iPau = E_TAG_FALSE
		iStp = E_TAG_FALSE
		iFwd = E_TAG_FALSE

		if aFocusId == E_CONTROL_ID_BUTTON_REWIND :
			pass
			#iRew = E_TAG_TRUE
		elif aFocusId == E_CONTROL_ID_BUTTON_PLAY :
			iPly = E_TAG_TRUE
		elif aFocusId == E_CONTROL_ID_BUTTON_PAUSE :
			iPau = E_TAG_TRUE
		elif aFocusId == E_CONTROL_ID_BUTTON_STOP :
			iStp = E_TAG_TRUE
		elif aFocusId == E_CONTROL_ID_BUTTON_FORWARD :
			pass
			#iFwd = E_TAG_TRUE

		self.UpdatePropertyGUI( 'iPlayerRewind',  iRew )
		self.UpdatePropertyGUI( 'iPlayerResume',  iPly )
		self.UpdatePropertyGUI( 'iPlayerPause',   iPau )
		self.UpdatePropertyGUI( 'iPlayerStop',    iStp )
		self.UpdatePropertyGUI( 'iPlayerForward', iFwd )


	def ShowButtonFocus( self ) :
		ret = False
		if self.getProperty( 'iButtonShow' ) != E_TAG_TRUE :
			return ret

		focus = E_CONTROL_ID_BUTTON_PLAY
		if self.mSpeed == 100 :
			focus = E_CONTROL_ID_BUTTON_PAUSE
		elif self.mSpeed < 0 :
			focus = E_CONTROL_ID_BUTTON_REWIND
		elif self.mSpeed > 100 :
			focus = E_CONTROL_ID_BUTTON_FORWARD

		ret = self.UpdateSetFocus( focus )
		#LOG_TRACE('------set button focus[%s] ret[%s]'% ( focus, ret ) )
		return ret


	@SetLock
	def InitTimeShift( self, loop = 0 ) :
		status = None
		status = self.mDataCache.Player_GetStatus( )
		#retList = []
		#retList.append( status )
		#LOG_TRACE( 'player_GetStatus[%s]'% ClassToList( 'convert', retList ) )

		if status and status.mError == 0 :
			flag_Rewind  = False
			flag_Forward = False
			lbl_speed = ''
			lbl_timeS = ''
			lbl_timeP = ''
			lbl_timeE = ''

			self.mIsTimeshiftPending = status.mIsTimeshiftPending

			#play mode
			self.mMode = status.mMode

			#test label
			#test = TimeToString(status.mPlayTimeInMs/1000, TimeFormatEnum.E_HH_MM_SS)
			#lblTest = 'current:[%s] currentToTime[%s] timeout[%s]'% (status.mPlayTimeInMs, test, self.mRepeatTimeout)
			#self.UpdateControlGUI( self.mCtrlLblTest.getId( ), lblTest )


			#progress data
			#self.mTimeshift_staTime = 0.0
			#self.mTimeshift_curTime = 0.0
			#self.mTimeshift_endTime = 0.0
			self.mTimeshift_playTime= status.mPlayTimeInMs
			self.mTimeshift_staTime = status.mStartTimeInMs
			self.mTimeshift_curTime = status.mPlayTimeInMs
			self.mTimeshift_endTime = status.mEndTimeInMs

			tempStartTime   = self.mTimeshift_staTime / 1000.0
			tempCurrentTime = self.mTimeshift_curTime / 1000.0
			tempEndTime     = self.mTimeshift_endTime / 1000.0

			if status.mMode == ElisEnum.E_MODE_TIMESHIFT :
				if status.mEndTimeInMs :
					self.mTimeshift_endTime = status.mEndTimeInMs   #/ 1000.0

				if status.mPlayTimeInMs < 1 :
					self.mTimeshift_curTime = self.mInitCurTime
					#tempCurrentTime = self.mInitCurTime

				localTime = self.mDataCache.Datetime_GetLocalTime( )
				"""
				duration = ( self.mTimeshift_endTime - self.mTimeshift_staTime ) / 1000.0
				tempStartTime = localTime - duration
				tempCurrentTime = tempStartTime + ( self.mTimeshift_curTime / 1000.0 )
				tempEndTime = localTime
				"""

				duration = int( self.mTimeshift_endTime / 1000.0 )
				if tempStartTime < 1 :
					tempStartTime = localTime - duration
					tempCurrentTime = tempStartTime + int( self.mTimeshift_curTime / 1000.0 )
				else :
					tempStartTime += localTime - duration
					tempCurrentTime = ( localTime - duration ) + int( tempCurrentTime )
				tempEndTime = localTime
				#LOG_TRACE( '----------------start_o[%s] start_c[%s]'% ( int( self.mTimeshift_staTime / 1000.0 ), tempStartTime ) )

				if self.mOldPlayTime > 0 and self.mAccelator == 0 :
					if ( status.mSpeed in E_TINY_XSPEED ) or status.mSpeed == 100 :
						if self.mOldPlayTime > tempCurrentTime :
							tempCurrentTime = self.mOldPlayTime

				if self.mOldStartTime > 0 and self.mAccelator == 0 :
					if self.mOldStartTime > tempStartTime :
						tempStartTime = self.mOldStartTime

			elif status.mMode == ElisEnum.E_MODE_PVR :
				if self.mPlayingRecordInfo and self.mPlayingRecordInfo.mError == 0 :
					self.mTimeshift_endTime = self.mPlayingRecordInfo.mDuration * 1000
					tempEndTime = self.mPlayingRecordInfo.mDuration

				else :
					self.mTimeshift_staTime = 0.0
					self.mTimeshift_endTime = status.mEndTimeInMs
					tempEndTime = status.mEndTimeInMs / 1000

				#LOG_TRACE( 'resetting pvr start[%s] end[%s]'% ( self.mTimeshift_staTime, self.mTimeshift_endTime ) )


			#Speed label
			self.mSpeed  = status.mSpeed

			if self.mSpeed != 0 :
				self.mRepeatTimeout = 1
				if self.mSpeed == 100 :
					self.mRepeatTimeout = 1
				elif self.mSpeed in E_TINY_XSPEED :
					self.mRepeatTimeout = 0.5
				else :
					self.mRepeatTimeout = 100.0 / abs(self.mSpeed)

				if self.mRepeatTimeout < 0.1 :
					self.mRepeatTimeout = 0.1

			timeFormat = TimeFormatEnum.E_HH_MM_SS
			if status.mMode == ElisEnum.E_MODE_PVR :
				timeFormat = TimeFormatEnum.E_AH_MM_SS

			lbl_timeS = TimeToString( tempStartTime  , TimeFormatEnum.E_HH_MM_SS )
			lbl_timeP = TimeToString( tempCurrentTime, timeFormat )
			lbl_timeE = TimeToString( tempEndTime    , timeFormat )

			if lbl_timeS != '' :
				self.mInitCurTime = tempEndTime / 1000000
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_TS_START_TIME, lbl_timeS )
				self.UpdateControlGUI( E_CONTROL_ID_BUTTON_CURRENT, lbl_timeP, E_TAG_LABEL )
				self.mOldStartTime = tempStartTime
			if lbl_timeP != '' and status.mSpeed != 0 :
				self.UpdateControlGUI( E_CONTROL_ID_BUTTON_CURRENT, lbl_timeP, E_TAG_LABEL )
				self.mOldPlayTime = tempCurrentTime
			if lbl_timeE != '' :
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_TS_END_TIME, lbl_timeE )

			#if tempStartTime > 0 :
			#	self.mStartTimeShowed = True

			#LOG_TRACE('mStartTimeShowed[%s] start[%s] curr[%s]'% ( self.mStartTimeShowed, tempStartTime, tempCurrentTime ) )
			self.GetNextSpeed( E_ONINIT )

		#if self.mMode == ElisEnum.E_MODE_TIMESHIFT and self.mSpeed == 100 :
		#	self.InitAccelatorSection( )


	def GetNextSpeed( self, aFocusId ) :
		#LOG_TRACE( 'mSpeed[%s]'% self.mSpeed )
		ret = 0
		if aFocusId == E_CONTROL_ID_BUTTON_REWIND :
			#if self.mSpeed == -12800 :
			#	ret = -12800
			if self.mSpeed == -6400 :
				#ret = -12800
				ret = -6400
			elif self.mSpeed == -3200 :
				ret = -6400
			elif self.mSpeed == -1600 :
				ret = -3200
			elif self.mSpeed == -800 :
				ret = -1600
			elif self.mSpeed == -400 :
				ret = -800
			elif self.mSpeed == -200 :
				ret = -400
			elif self.mSpeed == 100 :
				ret = -200
			elif self.mSpeed == 0 :
				self.mDataCache.Player_Resume( )
				ret = -200
			elif self.mSpeed == 25 :
				ret = -200
			elif self.mSpeed == 50 :
				ret = 25
			elif self.mSpeed == 120 :
				ret = 50
				if not E_TINY_XSPEED_SUPPORT :
					ret = -200
			elif self.mSpeed == 200 :
				ret = 100
				if not E_TINY_XSPEED_SUPPORT :
					ret = 120
			elif self.mSpeed == 400 :
				ret = 200
			elif self.mSpeed == 800 :
				ret = 400
			elif self.mSpeed == 1600 :
				ret = 800
			elif self.mSpeed == 3200 :
				ret = 1600
			elif self.mSpeed == 6400 :
				ret = 3200
			#elif self.mSpeed == 12800 :
			#	ret = 6400

		elif aFocusId == E_CONTROL_ID_BUTTON_FORWARD :
			#if self.mSpeed == -12800 :
			#	ret = -6400
			if self.mSpeed == -6400 :
				ret = -3200
			elif self.mSpeed == -3200 :
				ret = -1600
			elif self.mSpeed == -1600 :
				ret = -800
			elif self.mSpeed == -800 :
				ret = -400
			elif self.mSpeed == -400 :
				ret = -200
			elif self.mSpeed == -200 :
				ret = 100
			elif self.mSpeed == 0 :
				self.mDataCache.Player_Resume( )
				ret = 25
				if not E_TINY_XSPEED_SUPPORT :
					ret = 120
			elif self.mSpeed == 25 :
				ret = 50
			elif self.mSpeed == 50 :
				ret = 120
			elif self.mSpeed == 120 :
				ret = 200
			elif self.mSpeed == 100 :
				ret = 200
				if not E_TINY_XSPEED_SUPPORT :
					ret = 120
			elif self.mSpeed == 200 :
				ret = 400
			elif self.mSpeed == 400 :
				ret = 800
			elif self.mSpeed == 800 :
				ret = 1600
			elif self.mSpeed == 1600 :
				ret = 3200
			elif self.mSpeed == 3200 :
				ret = 6400
			elif self.mSpeed == 6400 :
				#ret = 12800
				ret = 6400
			#elif self.mSpeed == 12800 :
			#	ret = 12800

		elif aFocusId == E_ONINIT :
			ret = self.mSpeed

		else :
			ret = 100 #default

		pos = 0
		lspeed = ''
		if ret == 100 or ret == 0 :
			lspeed = ''
		else :
			pos = ret / 100
			if ret % 100 != 0 :
				pos = ret / 100.0
			lspeed = '%sx'% abs( pos )

		posx = int( pos / 2 )
		if posx < -30 : posx = -30
		elif posx > 30: posx = 30

		if ret == 100 :
			self.UpdateControlGUI( E_CONTROL_ID_BUTTON_PLAY, False )
			self.UpdateControlGUI( E_CONTROL_ID_BUTTON_PAUSE, True )
			#LOG_TRACE( '-------Play speed[%s]'% ret)
			self.ShowStatusByButton( E_CONTROL_ID_BUTTON_PLAY )
			self.UpdatePropertyGUI( 'iPlayerXpeed', E_TAG_FALSE )
			self.UpdatePropertyGUI( 'iXpeedArrow', E_TAG_FALSE )

		else :
			self.UpdateControlGUI( E_CONTROL_ID_BUTTON_PLAY, True )
			self.UpdateControlGUI( E_CONTROL_ID_BUTTON_PAUSE, False )
			#self.ShowStatusByButton( None )
			#LOG_TRACE( '-------Pause speed[%s]'% ret)
			if ret != 0 :
				self.mCtrlImgXpeed.setPosition( posx, 3 )
				self.UpdatePropertyGUI( 'iFileXpeed', 'OSD%s.png'% lspeed )

				self.UpdatePropertyGUI( 'iPlayerXpeed', E_TAG_TRUE )
				if ret < 0 :
					self.UpdatePropertyGUI( 'iXpeedArrow', 'Rewind' )
				else :
					self.UpdatePropertyGUI( 'iXpeedArrow', 'Forward' )


		return int( ret )


	def GetModeValue( self ) :
		buttonHide = True

		labelMode = GetStatusModeLabel( self.mMode )
		if self.mMode == ElisEnum.E_MODE_LIVE or self.mMode == ElisEnum.E_MODE_TIMESHIFT :
			labelMode = '[COLOR green]%s[/COLOR]'% MR_LANG( 'TIMESHIFT' )
		elif self.mMode == ElisEnum.E_MODE_PVR :
			buttonHide = False

		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_BOOKMARK, not buttonHide, E_TAG_VISIBLE )
		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_START_RECORDING, buttonHide, E_TAG_VISIBLE )
		return labelMode


	@RunThread
	def PlayProgressThread( self ) :
		count = self.mRepeatTimeout
		loopDelay = 0.02
		while self.mEnableLocalThread :
			if self.mRepeatTimeout <= count :
				#LOG_TRACE( 'repeat time[%s] <<<<'% self.mRepeatTimeout )

				#update localTime
				self.mLocalTime = self.mDataCache.Datetime_GetLocalTime( )

				if self.mIsPlay != FLAG_STOP :
					if not self.mFlagUserMove :
						#self.mProgressReview = self.mProgress_idx
						self.InitTimeShift( )
						self.UpdateProgress( )
				count = 0

			time.sleep( loopDelay )
			count = count + loopDelay

		self.mThreadProgress = None


	def UpdateProgress( self, aUserMoving = 0, aMoveBy = E_MOVE_BY_TIME ) :
		try :
			lbl_timeE = ''
			lbl_timeP = ''

			#calculate current position
			playSize = self.mTimeshift_endTime - self.mTimeshift_staTime
			curTime = self.mTimeshift_curTime - self.mTimeshift_staTime + aUserMoving

			if aMoveBy == E_MOVE_BY_MARK :
				curTime = aUserMoving

			if curTime < 0 :
				curTime = 0

			if playSize > 0 and curTime >= 0 :
				self.mProgress_idx = ( curTime / float( playSize ) )  * 100.0

				#LOG_TRACE( 'curTime[%s] playSize[%s] percent[%s]%%'% ( curTime, playSize, self.mProgress_idx ) )
				#LOG_TRACE( 'staTime[%s] curTime[%s] endTime[%s]'% ( self.mTimeshift_staTime, self.mTimeshift_curTime, self.mTimeshift_endTime ) )

				if self.mProgress_idx > 100 :
					self.mProgress_idx = 100
				elif self.mProgress_idx < 0 :
					self.mProgress_idx = 0

				#progress drawing
				posx = int( self.mProgress_idx * E_PROGRESS_WIDTH_MAX / 100 )
				self.UpdateControlGUI( E_CONTROL_ID_BUTTON_CURRENT, posx, E_TAG_POSY )
				self.UpdateControlGUI( E_CONTROL_ID_PROGRESS, self.mProgress_idx )
				#LOG_TRACE( 'progress endTime[%s] idx[%s] posx[%s]'% (self.mTimeshift_endTime, self.mProgress_idx, posx) )

		except Exception, e :
			LOG_ERR( 'Error exception[%s]'% e )


	#deprecate
	def UpdateProgressReview( self, aUserMoving = 0, aMoveBy = E_MOVE_BY_TIME ) :
		try :
			lbl_timeE = ''
			lbl_timeP = ''

			#calculate current position
			#playSize = self.mTimeshift_endTime - self.mTimeshift_staTime
			#curTime = self.mTimeshift_curTime - self.mTimeshift_staTime + aUserMoving
			playSize = self.mTimeshift_endTime
			curTime = self.mTimeshift_curTime + aUserMoving
			if aMoveBy == E_MOVE_BY_MARK :
				curTime = self.mTimeshift_staTime + aUserMoving
			if curTime < self.mTimeshift_staTime :
				curTime = self.mTimeshift_staTime

			if playSize > 0 and curTime >= 0 :
				self.mProgressReview = (curTime / float(playSize))  * 100.0

				#LOG_TRACE( 'curTime[%s] playSize[%s] idx[%s]'% ( curTime,playSize,self.mProgress_idx ) )
				#LOG_TRACE( 'staTime[%s] curTime[%s] endTime[%s]'% ( self.mTimeshift_staTime, self.mTimeshift_curTime, self.mTimeshift_endTime ) )

				if self.mProgressReview > 100 :
					self.mProgressReview = 100
				elif self.mProgressReview < 0 :
					self.mProgressReview = 0

				#progress drawing
				posx = int( self.mProgressReview * E_PROGRESS_WIDTH_MAX / 100 )
				self.UpdateControlGUI( E_CONTROL_ID_BUTTON_CURRENT, posx, E_TAG_POSY )
				#self.UpdateControlGUI( E_CONTROL_ID_PROGRESS_REVIEW, self.mProgressReview )
				#LOG_TRACE( 'progress endTime[%s] idx[%s] posx[%s]'% (self.mTimeshift_endTime, self.mProgress_idx, posx) )

		except Exception, e :
			LOG_ERR( 'Error exception[%s]'% e )


	def ShowRecordingInfo( self ) :
		isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )
		isRunningTimerList = self.mDataCache.Timer_GetRunningTimers( )
		runningRecordCount = 0

		if isRunningTimerList :
			runningRecordCount = len( isRunningTimerList )
		#LOG_TRACE( "runningRecordCount=%d" %runningRecordCount )

		strLabelRecord1 = ''
		strLabelRecord2 = ''
		setPropertyRecord1   = 'False'
		setPropertyRecord2   = 'False'
		if isRunRec == 1 and runningRecordCount == 1 :
			setPropertyRecord1 = 'True'
			#recInfo = self.mDataCache.Record_GetRunningRecordInfo( E_INDEX_FIRST_RECORDING )
			timer = isRunningTimerList[0]
			iChName   = timer.mName
			iChNumber = timer.mChannelNo
			startTime = timer.mStartTime
			endTime = startTime + timer.mDuration
			recInfo = self.mDataCache.Record_GetRecordInfoByKey( timer.mRecordKey )				
			if recInfo :
				startTime = recInfo.mStartTime
				iChName   = recInfo.mChannelName
				iChNumber = recInfo.mChannelNo

			channel = self.mDataCache.GetChannelByIDs( timer.mSid, timer.mTsid, timer.mOnid )
			iChNumber = recInfo.mChannelNo
			if channel :
				iChNumber = channel.mNumber
				if E_V1_2_APPLY_PRESENTATION_NUMBER :
					iChNumber = self.mDataCache.CheckPresentationNumber( channel )
			strLabelRecord1 = '(%s~%s)  %04d %s'% ( TimeToString( startTime, TimeFormatEnum.E_HH_MM ), TimeToString( endTime, TimeFormatEnum.E_HH_MM ), int( iChNumber ), iChName )

		elif isRunRec == 2 and runningRecordCount == 2 :
			setPropertyRecord1 = 'True'
			setPropertyRecord2 = 'True'
			#recInfo = self.mDataCache.Record_GetRunningRecordInfo( E_INDEX_FIRST_RECORDING )
			timer = isRunningTimerList[0]
			iChName   = timer.mName
			iChNumber = timer.mChannelNo
			startTime = timer.mStartTime
			endTime = startTime + timer.mDuration
			recInfo = self.mDataCache.Record_GetRecordInfoByKey( timer.mRecordKey )				
			if recInfo :
				startTime = recInfo.mStartTime
				iChName   = recInfo.mChannelName
				iChNumber = recInfo.mChannelNo

			channel = self.mDataCache.GetChannelByIDs( timer.mSid, timer.mTsid, timer.mOnid )
			if channel :
				iChNumber = channel.mNumber
				if E_V1_2_APPLY_PRESENTATION_NUMBER :
					iChNumber = self.mDataCache.CheckPresentationNumber( channel )
			strLabelRecord1 = '(%s~%s)  %04d %s'% ( TimeToString( startTime, TimeFormatEnum.E_HH_MM ), TimeToString( endTime , TimeFormatEnum.E_HH_MM ), int( iChNumber ), iChName )

			#recInfo = self.mDataCache.Record_GetRunningRecordInfo( E_INDEX_SECOND_RECORDING )
			timer = isRunningTimerList[1]
			iChName   = timer.mName
			iChNumber = timer.mChannelNo
			startTime = timer.mStartTime
			endTime = startTime + timer.mDuration
			recInfo = self.mDataCache.Record_GetRecordInfoByKey( timer.mRecordKey )				
			if recInfo :
				startTime = recInfo.mStartTime
				iChName   = recInfo.mChannelName
				iChNumber = recInfo.mChannelNo

			channel = self.mDataCache.GetChannelByIDs( timer.mSid, timer.mTsid, timer.mOnid )
			iChNumber = recInfo.mChannelNo
			if channel :
				iChNumber = channel.mNumber
				if E_V1_2_APPLY_PRESENTATION_NUMBER :
					iChNumber = self.mDataCache.CheckPresentationNumber( channel )
			strLabelRecord2 = '(%s~%s)  %04d %s'% ( TimeToString( startTime, TimeFormatEnum.E_HH_MM ), TimeToString( endTime , TimeFormatEnum.E_HH_MM ), int( iChNumber ), iChName )

		btnValue = False
		if isRunRec >= 1 :
			btnValue = False
		else :
			btnValue = True

		self.UpdateControlGUI( E_CONTROL_ID_LABEL_RECORDING1, strLabelRecord1 )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_RECORDING2, strLabelRecord2 )
		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_START_RECORDING, btnValue, E_TAG_ENABLE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_RECORDING1, setPropertyRecord1 )
		self.UpdatePropertyGUI( E_XML_PROPERTY_RECORDING2, setPropertyRecord2 )


	def RecordingStopAll( self ) :
		RunningRecordCount = self.mCommander.Record_GetRunningRecorderCount( )
		LOG_ERR( 'RunningRecordCount=%s'% RunningRecordCount )

		for i in range( int(RunningRecordCount) ) :
			recInfo = self.mDataCache.Record_GetRunningRecordInfo( i )
			if recInfo :
				#recInfo.printdebug( )
				ret = self.mDataCache.Timer_StopRecordingByRecordKey( recInfo.mRecordKey )
				#LOG_TRACE('record key[%s] stop[%s]'% (recInfo.mRecordKey, ret) )

		if RunningRecordCount :
			self.mDataCache.SetChannelReloadStatus( True )


	@RunThread
	def WaitToBuffering( self ) :
		repeatPending = 0
		while self.mEnableLocalThread :
			if self.mIsTimeshiftPending :
				#LOG_TRACE( '-------------pending' )
				repeatPending += 1
				if repeatPending > E_PENDING_REPEAT_LIMIT :
					self.mDataCache.Frontdisplay_PlayPause( )
					LOG_TRACE( '-------------E_PENDING_REPEAT_LIMIT' )
					break

				waitTime = 0
				self.OpenBusyDialog( )
				while waitTime < 5 :
					if not self.mIsTimeshiftPending :
						self.mDataCache.Frontdisplay_PlayPause( )
						LOG_TRACE( '-------------E_PENDING_Release, play normal' )
						break
					time.sleep( 1 )
					waitTime += 1
				self.CloseBusyDialog( )

				#play on
				if not self.mIsTimeshiftPending :
					waitTime = 0
					while waitTime < 5 :
						ret = self.TimeshiftAction( E_CONTROL_ID_BUTTON_PLAY )

						defaultFocus = E_CONTROL_ID_BUTTON_PAUSE
						if self.mPrekey == Action.ACTION_MOVE_LEFT or self.mPrekey == Action.ACTION_MOVE_RIGHT :
							defaultFocus = E_CONTROL_ID_BUTTON_CURRENT

						if self.getProperty( 'iButtonShow' ) == E_TAG_TRUE :
							self.UpdateSetFocus( defaultFocus )

						if self.mSpeed == 100 and ret :
							break
						time.sleep( 1 )
						waitTime += 1
						LOG_TRACE('-----------repeat[%s] focused[%s] '% ( waitTime, defaultFocus ) )

			time.sleep( 1 )
			#LOG_TRACE('------')

		if repeatPending > E_PENDING_REPEAT_LIMIT :
			self.ShowDialogByPlayFault( )


	def ShowDialogByPlayFault( self ) :
		self.TimeshiftAction( E_CONTROL_ID_BUTTON_STOP )
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Timeshift not ready%s Please try again' )% NEW_LINE )
		dialog.SetStayCount( 1 )
		dialog.doModal( )


	def ShowDialog( self, aFocusId ) :
		if aFocusId == E_CONTROL_ID_BUTTON_SETTING_FORMAT or aFocusId == E_CONTROL_ID_BUTTON_PIP :
			thread = threading.Timer( 0.1, self.DoActionHotkeys, [aFocusId] )
			thread.start( )
			return

		thread = threading.Timer( 0.1, self.BookMarkContext, [aFocusId] )
		thread.start( )
		#self.RestartAutomaticHide( )


	def DoActionHotkeys( self, aFocusId ) :
		self.StopAutomaticHide( )

		if aFocusId == E_CONTROL_ID_BUTTON_SETTING_FORMAT :
			DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SET_AUDIOVIDEO ).doModal( )

		elif aFocusId == E_CONTROL_ID_BUTTON_PIP :
			pipDialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP )
			pipDialog.doModal( )
			if pipDialog.GetCloseStatus( ) == Action.ACTION_STOP :
				LOG_TRACE( '[TimeshiftPlate] no automaticHide by pvr/timeshift stop on PIP' )
				return

		self.RestartAutomaticHide( )


	def BookMarkContext( self, aFocusId ) :
		if not self.mPlatform.IsPrismCube( ) :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No %s support' )% self.mPlatform.GetName( ) )
			dialog.doModal( )
			self.RestartAutomaticHide( )
			return

		context = []
		if aFocusId == E_CONTROL_ID_LIST_SHOW_BOOKMARK :
			context.append( ContextItem( MR_LANG( 'Delete' ), CONTEXT_ACTION_DELETE ) )

		else :
			context.append( ContextItem( MR_LANG( 'Add a bookmark' ), CONTEXT_ACTION_ADD_TO_BOOKMARK ) )
			context.append( ContextItem( MR_LANG( 'Start auto-chaptering' ), CONTEXT_ACTION_ADD_AUTO_CHAPTER ) )
			context.append( ContextItem( MR_LANG( 'Show all bookmarks' ), CONTEXT_ACTION_SHOW_LIST ) )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
		dialog.doModal( )

		self.EventReceivedDialog( dialog )

		selectAction = dialog.GetSelectedAction( )
		if selectAction == -1 :
			return

		self.DoContextAction( selectAction )


	def DoContextAction( self, aSelectAction ) :
		if aSelectAction == CONTEXT_ACTION_ADD_TO_BOOKMARK :
			if self.mBookmarkList and len( self.mBookmarkList ) >= E_DEFAULT_BOOKMARK_LIMIT :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'You have reached the maximum number of%s bookmarks allowed' )% NEW_LINE )
				dialog.doModal( )
				return

			if self.mSpeed != 100 :
				self.TimeshiftAction( E_CONTROL_ID_BUTTON_PLAY )

			ret = self.mDataCache.Player_CreateBookmark( )
			if ret :
				self.InitBookmarkThumnail( )

			self.RestartAutomaticHide( )

		elif aSelectAction == CONTEXT_ACTION_DELETE :
			self.DoDeleteBookmarkBySelect( )

		elif aSelectAction == CONTEXT_ACTION_SHOW_LIST :
			playingRecord = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW ).GetPlayingRecord( )

			if playingRecord :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_BOOKMARK )
				dialog.SetDefaultProperty( playingRecord )
				dialog.doModal( )

				if dialog.IsDeleteBookmark( ) :
					self.InitBookmarkThumnail( )

			self.RestartAutomaticHide( )

			#tempList = dialog.GetSelectedList( )
			#LOG_TRACE('------------dialog list[%s]'% tempList )

		elif aSelectAction == CONTEXT_ACTION_ADD_AUTO_CHAPTER :
			if self.mSpeed != 100 :
				self.TimeshiftAction( E_CONTROL_ID_BUTTON_PLAY )

			self.AutoChapterAddBookmark( )
			self.InitBookmarkThumnail( )

		elif aSelectAction == CONTEXT_ACTION_RESUME_FROM :
			self.DoResumeFromBookmark( )


	def DoDeleteBookmarkBySelect( self ) :
		if not self.mPlayingRecordInfo or ( not self.mBookmarkList or len( self.mBookmarkList ) < 1 ) :
			return 

		selectedPos = self.mCtrlBookMarkList.getSelectedPosition( )
		if selectedPos > len( self.mBookmarkList ) - 1 :
			#LOG_TRACE( 'No exist bookmark this, idx[%s]'% selectedPos )
			return

		playOffset = self.mBookmarkList[selectedPos].mOffset
		ret = self.mDataCache.Player_DeleteBookmark( self.mPlayingRecordInfo.mRecordKey, playOffset )
		#LOG_TRACE( 'bookmark delete[%s %s %s %s] ret[%s]'% (self.mPlayingRecordInfo.mRecordKey, selectedPos, playOffset,self.mBookmarkList[selectedPos].mTimeMs,ret ) )
		if ret :
			controlId = self.mDataCache.GetBookmarkHash( playOffset )
			#LOG_TRACE('--------delete--------find controlId[%s]'% controlId )
			if controlId != -1 :
				self.mBookmarkButton[controlId].setVisible( False )
				#LOG_TRACE( 'bookmark unVisible id[%s] pos[%s] //// bookmark idx[%s] offset[%s]'% ( self.mBookmarkButton[controlId].getId(), self.mBookmarkButton[controlId].getPosition( ), selectedPos, playOffset ) )

				self.Flush( )
				self.InitBookmarkThumnail( )
				if self.mBookmarkList and len( self.mBookmarkList ) > 0 :
					nextPos = selectedPos - 1
					if nextPos > -1 and nextPos <= len( self.mBookmarkList ) - 1 :
						self.mCtrlBookMarkList.selectItem( nextPos )
						time.sleep( 0.05 )
						#self.UpdateControlListSelectItem( self.mCtrlBookMarkList, nextPos )
					self.UpdateControlGUI( E_CONTROL_ID_IMAGE_BOOKMARK_CURRENT )

				else :
					self.UpdatePropertyGUI( 'BookMarkShow', 'False' )
					self.setFocusId( E_CONTROL_ID_BUTTON_CURRENT )


	def DoResumeFromBookmark( self ) :
		if self.mBookmarkList == None or len( self.mBookmarkList ) < 1 or self.mBookmarkList[0].mError != 0 :
			return 

		if self.mSpeed != 100 :
			self.TimeshiftAction( E_CONTROL_ID_BUTTON_PLAY )
			#LOG_TRACE( 'Play resume, status is Pause,Forward,Rewind in now' )

		idx = self.mCtrlBookMarkList.getSelectedPosition( )
		playOffset = self.mBookmarkList[idx].mTimeMs
		LOG_TRACE('bookmark idx[%s] pos[%s]'% ( idx, TimeToString( playOffset / 1000, TimeFormatEnum.E_AH_MM_SS ) ) )

		#self.mDataCache.Player_StartInternalRecordPlayback( playingRecord.mRecordKey, playingRecord.mServiceType, playOffset, 100 )
		self.mDataCache.Player_JumpToIFrame( playOffset )


	def AutoChapterAddBookmark( self ) :
		# limit playtime under 30sec
		#mediaTime = self.mTimeshift_endTime - self.mTimeshift_staTime
		#LOG_TRACE( '----------------duration[%s]'% self.mPlayingRecordInfo.mDuration )
		if not self.mPlayingRecordInfo :
			return 

		mediaTime = self.mPlayingRecordInfo.mDuration

		isLimit = False
		count = E_DEFAULT_COUNT_AUTO_CHAPTER + 1
		if mediaTime < E_DEFAULT_LIMIT_SECOND :
			isLimit = True

		elif mediaTime < E_DEFAULT_LIMIT_SECOND * 11 :
			count = divmod( mediaTime, E_DEFAULT_LIMIT_SECOND )[0]

		if count < 2 :
			count = 2

		if isLimit :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Make media length longer than %s secs%s to create a chapter' )% ( 10, NEW_LINE ) )
 			dialog.doModal( )
			return

		self.StopAutomaticHide( )

		self.OpenBusyDialog( )
		restoreCurrent = self.mTimeshift_playTime

		section = mediaTime / count
		#LOG_TRACE( 'mediaTime[%s] section[%s] count[%s]'% ( mediaTime, section, count ) )
		partition = 0
		isFull = False
		#self.mFlagUserMove = True

		for i in range( 1, count ) :
			partition += section * 1000

			#no create end from 10sec
			if ( partition / 1000 ) >= mediaTime - 10 :
				#LOG_TRACE( '-------------no create bookmark barrier( not available end point )!! idx[%s] offsetMs[%s] mediaSize[%s]'% ( i, partition, mediaTime ) )
				break

			lbl_timeS = TimeToString( partition, TimeFormatEnum.E_AH_MM_SS )
			#LOG_TRACE( '------------chapter idx[%s][%s] [%s]'% ( i, partition, lbl_timeS ) )

			ret = False
			retry = 0
			while retry < 3 :
				ret = self.mDataCache.Player_JumpToIFrame( partition )
				#LOG_TRACE('-------------Player_JumpToIFrame ret[%s] no[%s] retry[%s]'% ( ret, i, retry ) )
				if ret :
					break
				else :
					retry += 1
					time.sleep( 3 )

			if ret :
				mBookmarkList = self.mDataCache.Player_GetBookmarkList( self.mPlayingRecordInfo.mRecordKey )
				if mBookmarkList and len( mBookmarkList ) >= E_DEFAULT_BOOKMARK_LIMIT :
					isFull = True
					break

				ret = self.mDataCache.Player_CreateBookmark( )
				#LOG_TRACE('-----------add bookmark ret[%s] no[%s] markTime[%s]'% ( ret, i, partition ) )

			time.sleep( 1 )

			#window close then stop this function
			if not self.mEnableLocalThread :
				break

		self.mDataCache.Player_JumpToIFrame( restoreCurrent )
		#LOG_TRACE( '---------restoreCurrent[%s]'% TimeToString( restoreCurrent, TimeFormatEnum.E_AH_MM_SS ) )
		self.CloseBusyDialog( )

		self.mDataCache.Player_SetSpeed( 100 )
		#self.mFlagUserMove = False

		if isFull :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'You have reached the maximum number of%s bookmarks allowed' )% NEW_LINE )
			dialog.doModal( )

		self.RestartAutomaticHide( )


	def ShowBookmark( self ) :
		#self.StopAutomaticHide( )

		#1.show thumbnail on plate
		self.mCtrlBookMarkList.reset( )
		if len( self.mBookmarkList ) < 1 :
			self.UpdatePropertyGUI( 'BookMarkShow', 'False' )
			LOG_TRACE( 'bookmark None, show False' )
			return

		idxNumber = 0
		listItems = []
		for i in range( len( self.mBookmarkList ) ) :
			idxNumber += 1
			lblOffset = TimeToString( self.mBookmarkList[i].mTimeMs / 1000, TimeFormatEnum.E_AH_MM_SS )
			listItem = xbmcgui.ListItem( '%s'% lblOffset, '%s'% idxNumber )

			thumbIcon = self.mThumbnailHash.get( self.mBookmarkList[i].mTimeMs, -1 )
			if thumbIcon == -1 :
				thumbIcon = E_DEFAULT_THUMBNAIL_ICON

			listItem.setProperty( 'BookMarkThumb', thumbIcon )
			#LOG_TRACE('thumbnail listIdx[%s] file[%s]'% ( i, thumbIcon ) )
			#LOG_TRACE('bookmark timeMs[%s] offset[%s] duration[%s]'% ( self.mBookmarkList[i].mTimeMs, self.mBookmarkList[i].mOffset, self.mPlayingRecordInfo.mDuration ) )

			listItems.append( listItem )

		self.mCtrlBookMarkList.addItems( listItems )
		self.UpdatePropertyGUI( 'BookMarkShow', 'True' )

		#2.show selction icon on progress
		self.UpdateBookmarkByPoint( )


	def UpdateBookmarkByPoint( self ) :
		if not self.mBookmarkList or len( self.mBookmarkList ) < 1 :
			return

		if not self.mPlayingRecordInfo or ( self.mPlayingRecordInfo and self.mPlayingRecordInfo.mDuration < 1 ) :
			LOG_TRACE( 'Error, corrupt record file' )
			return

		revisionX = -10
		for i in range( len( self.mBookmarkList ) ) :
			#ratioX = float( self.mBookmarkList[i].mTimeMs ) / self.mTimeshift_endTime
			ratioX = float( self.mBookmarkList[i].mTimeMs / 1000 ) / self.mPlayingRecordInfo.mDuration

			#if ratioX < 0.02 :
			#	revisionX = -5
			posx = int( E_PROGRESS_WIDTH_MAX * ratioX ) + revisionX
			#LOG_TRACE('--------button id[%s] posx[%s] ratioX[%s] timeMs[%s] duration[%s]'% ( i, posx, ratioX, self.mBookmarkList[i].mTimeMs, self.mPlayingRecordInfo.mDuration ) )
			self.mDataCache.SetBookmarkHash( i, self.mBookmarkList[i].mOffset )
			#LOG_TRACE('-------add---------find controlId[%s]'% i )
			self.mBookmarkButton[i].setPosition( posx, 0 )
			self.mBookmarkButton[i].setVisible( True )
			#LOG_TRACE('pos[%s] ratio[%s]%%'% ( posx, ratioX * 100.0 ) )


	def UpdateBookmarkByThumbnail( self, aRecordKey, aTimeMs ) :
		if not self.mBookmarkList or len( self.mBookmarkList ) < 1 :
			return

		thumbnaillist = []
		thumbnaillist = glob.glob( os.path.join( '/mnt/hdd0/pvr/bookmark/%d'% aRecordKey, 'record_bookmark_%d_*.jpg' % aRecordKey ) )
		if thumbnaillist and len( thumbnaillist ) > 0 :
			for mfile in thumbnaillist :
				try :
					fileTimeMs = int( os.path.basename( mfile ).split('_')[3] )
					if fileTimeMs == aTimeMs :
						LOG_TRACE( '-------------new thumbnail[%s][%s]'% ( fileTimeMs, mfile ) )
						self.mThumbnailHash[fileTimeMs] = mfile

				except Exception, e :
					LOG_ERR( 'Error exception[%s]'% e )
					continue

		idx = 0
		for item in self.mBookmarkList :
			if item.mTimeMs == aTimeMs :
				thumbIcon = self.mThumbnailHash.get( aTimeMs, -1 )
				if thumbIcon != -1 :
					listItem = self.mCtrlBookMarkList.getListItem( idx )
					listItem.setProperty( 'BookMarkThumb', thumbIcon )
					LOG_TRACE( '-------------Refresh find thumb timeMs[%s]'% aTimeMs )
					break

			idx += 1

		xbmc.executebuiltin( 'container.refresh' )


	def InitBookmarkThumnail( self ) :
		self.LoadToBookmark( )
		self.InitShiftPostion( )


	def LoadToBookmark( self ) :
		self.mThumbnailList = []
		self.mBookmarkList = []

		self.mCtrlBookMarkList.reset( )
		if self.mMode != ElisEnum.E_MODE_PVR :
			self.UpdatePropertyGUI( 'BookMarkShow', 'False' )
			return

		playingRecord = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW ).GetPlayingRecord( )
		#LOG_TRACE('--------record[%s]'% playingRecord.mRecordKey )
		if playingRecord == None or playingRecord.mError != 0 :
			self.UpdatePropertyGUI( 'BookMarkShow', 'False' )
			return

		self.mPlayingRecordInfo = playingRecord
		self.mBookmarkList = self.mDataCache.Player_GetBookmarkList( playingRecord.mRecordKey )
		#LOG_TRACE('--------len[%s] [%s]'% ( len( mBookmarkList ), mBookmarkList[0].mError ) )
		if self.mBookmarkList == None or len( self.mBookmarkList ) < 1 or self.mBookmarkList[0].mError != 0 :
			self.UpdatePropertyGUI( 'BookMarkShow', 'False' )
			self.mBookmarkList = []
			return 

		#for item in mBookmarkList :
		#	LOG_TRACE('timeMs[%s]'% item.mTimeMs )

		thumbnaillist = []
		thumbnaillist = glob.glob( os.path.join( '/mnt/hdd0/pvr/bookmark/%d'% playingRecord.mRecordKey, 'record_bookmark_%d_*.jpg' % playingRecord.mRecordKey ) )

		#LOG_TRACE('len[%s] list[%s]'% ( len(thumbnaillist), thumbnaillist ) )
		self.mThumbnailList = []
		self.mThumbnailHash = {}
		if thumbnaillist and len( thumbnaillist ) > 0 :
			for mfile in thumbnaillist :
				try :
					self.mThumbnailHash[int( os.path.basename( mfile ).split('_')[3] )] = mfile
					self.mThumbnailList.append( mfile )

				except Exception, e :
					LOG_ERR( 'Error exception[%s]'% e )
					continue

		#LOG_TRACE('len[%s] hash[%s]'% ( len(self.mThumbnailHash), self.mThumbnailHash ) )
		#LOG_TRACE(' len[%s] bookmarkFile[%s]'% ( len(self.mThumbnailList), self.mThumbnailList ) )
		self.ShowBookmark( )


	def InitShiftPostion( self ) :
		#timeshift or has not bookmark
		mediaTime = self.mTimeshift_endTime - self.mTimeshift_staTime
		section = mediaTime / 10
		offset = 0
		self.mJumpToOffset = []
		#LOG_TRACE( '------------timeshift media[%s] section[%s]'% ( mediaTime, section ) )

		if self.mBookmarkList and len( self.mBookmarkList ) > 0 :
			for item in self.mBookmarkList :
				self.mJumpToOffset.append( item.mTimeMs )
		else :
			self.mJumpToOffset.append( 0 )
			#self.mJumpToOffset.append( self.mTimeshift_staTime )
			for i in range( 1, 10 ) :
				offset += section
				self.mJumpToOffset.append( offset )
			#LOG_TRACE( '------------timeshift jumps[%s]'% self.mJumpToOffset )


	def JumpToTrack( self, aDirection ) :
		self.InitTimeShift( )
		if self.mMode == ElisEnum.E_MODE_TIMESHIFT :
			self.InitShiftPostion( )

		stayOn = 1
		current = self.mTimeshift_playTime - self.mTimeshift_staTime
		idx = 0
		tot = len(self.mJumpToOffset)
		if aDirection == E_CONTROL_ID_BUTTON_JUMP_FF :
			for idx in range( tot ) :
				if current + 10000 < self.mJumpToOffset[idx] :
					#LOG_TRACE('--------------ff idx[%s]'% idx )
					break
		else :
			stayOn = -1
			for idx in range( tot - 1, -1, -1 ) :
				#reasen by revision playing speed, - 10sec
				if current - 10000 > self.mJumpToOffset[idx] :
					#LOG_TRACE('--------------rr idx[%s]'% idx )
					break

		idx = idx + self.mAccelator
		if idx < 0 :
			idx = 0
			self.mAccelator -= stayOn
		elif idx >= tot :
			idx = tot - 1
			self.mAccelator -= stayOn

		jump = self.mJumpToOffset[idx]
		#ret = self.mDataCache.Player_JumpToIFrame( jump )
		#LOG_TRACE('----------current[%s] idx[%s] jump[%s] offset[%s]'% ( current, idx, jump, self.mJumpToOffset ) )

		return jump


	#deprecate
	def InitAccelatorSection( self ) :
		idx = 0
		limitShift = 60

		tempStartTime   = self.mTimeshift_staTime / 1000
		tempCurrentTime = self.mTimeshift_curTime / 1000
		tempEndTime     = self.mTimeshift_endTime / 1000
		duration = tempEndTime - tempStartTime
		section = duration / limitShift

		self.mAccelatorSection = {}
		for i in range( limitShift ) :
			self.mAccelatorSection[i] = section * i


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.mEnableLocalThread = False
		try :
			if self.mThreadProgress :
				self.mThreadProgress.join( )

		except Exception, e :
			LOG_ERR( 'Error exception[%s]'% e )

		#isSwap? swap surface
		if self.mDataCache.PIP_GetSwapStatus( ) :
			self.mDataCache.PIP_SwapWindow( True, False )

		self.Flush( )
		self.StopAsyncMove( )
		self.StopAutomaticHide( )


	def Flush( self ) :
		self.mCtrlBookMarkList.reset( )

		if self.mBookmarkButton and len( self.mBookmarkButton ) > 0 :
			for bookmark in self.mBookmarkList :
				controlId = self.mDataCache.GetBookmarkHash( bookmark.mOffset )
				#LOG_TRACE('--close--------------find controlId[%s]'% controlId )
				if controlId != -1 :
					self.mBookmarkButton[controlId].setVisible( False )
					#LOG_TRACE( 'bookmark unVisible id[%s] pos[%s] //// bookmark idx[%s] offset[%s]'% ( self.mBookmarkButton[controlId].getId(), self.mBookmarkButton[controlId].getPosition( ), controlId, bookmark.mOffset ) )

			self.mDataCache.InitBookmarkHash( )
			self.mDataCache.InitBookmarkButton( )
			self.mDataCache.SetBookmarkButton( self.mBookmarkButton )
			LOG_TRACE('erased Init. bookmark' )


	def SetAutomaticHide( self, aHide=True ) :
		self.mAutomaticHide = aHide


	def GetAutomaticHide( self ) :
		return self.mAutomaticHide


	def AsyncAutomaticHide( self ) :
		if self.mSpeed == 100 :
			xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )
			#LOG_TRACE('HIDE : TimeShiftPlate')


	def RestartAutomaticHide( self ) :
		self.StopAutomaticHide( )
		if self.mAutomaticHide :
			self.StartAutomaticHide( )

	
	def StartAutomaticHide( self ) :
		self.mAutomaticHideTimer = threading.Timer( self.mBannerTimeout, self.AsyncAutomaticHide )
		self.mAutomaticHideTimer.start( )


	def StopAutomaticHide( self ) :
		if self.mAutomaticHideTimer and self.mAutomaticHideTimer.isAlive( ) :
			self.mAutomaticHideTimer.cancel( )
			del self.mAutomaticHideTimer
			
		self.mAutomaticHideTimer = None


	def RestartAsyncMove( self, aMoveTrack = None ) :
		self.UpdatePropertyGUI( 'IsShift', 'True' )
		self.StopAsyncMove( )
		if aMoveTrack :
			self.StartAsyncMoveByMark( aMoveTrack )
		else :
			self.StartAsyncMoveByTime( )


	def StartAsyncMoveByMark( self, aMoveTrack, aStartOnLeft = False ) :
		if aMoveTrack != E_CONTROL_ID_BUTTON_JUMP_FF and aMoveTrack != E_CONTROL_ID_BUTTON_JUMP_RR :
			return

		self.mFlagUserMove = True

		userMovingMs = self.JumpToTrack( aMoveTrack )
		#async idx, apply to second time
		moveTrack = 1
		if aMoveTrack == E_CONTROL_ID_BUTTON_JUMP_RR :
			moveTrack = -1
		self.mAccelator += moveTrack

		self.UpdateProgress( userMovingMs, E_MOVE_BY_MARK )
		#self.UpdateProgressReview( userMovingMs, E_MOVE_BY_MARK )
		#LOG_TRACE( '-----------focusid[%s] moving[%s] accelator[%s]'% ( aMoveTrack, userMovingMs, self.mAccelator ) )

		tempStartTime   = self.mTimeshift_staTime / 1000
		tempCurrentTime = self.mTimeshift_curTime / 1000
		tempEndTime     = self.mTimeshift_endTime / 1000
		timeFormat      = TimeFormatEnum.E_HH_MM_SS
		if self.mMode == ElisEnum.E_MODE_TIMESHIFT :
			duration = ( self.mTimeshift_endTime - self.mTimeshift_staTime ) / 1000
			tempStartTime = self.mLocalTime - duration
			tempCurrentTime = tempStartTime
			tempEndTime =  self.mLocalTime

		elif self.mMode == ElisEnum.E_MODE_PVR :
			tempCurrentTime = 0
			timeFormat = TimeFormatEnum.E_AH_MM_SS

		lblCurrentTime = tempCurrentTime + ( userMovingMs / 1000 )
		self.mAsyncMove = userMovingMs + self.mTimeshift_staTime

		lbl_timeP = TimeToString( lblCurrentTime, timeFormat )
		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_CURRENT, lbl_timeP, E_TAG_LABEL )

		self.mAsyncShiftTimer = threading.Timer( 1, self.AsyncUpdateCurrentMove, [aStartOnLeft] )
		self.mAsyncShiftTimer.start( )


	def StartAsyncMoveByTime( self, aStartOnLeft = False ) :
		self.mFlagUserMove = True

		self.mAccelator += self.mUserMoveTime
		sectionMoving = 0
		current = 0
		arrow = 1

		#restSize = 0
		#section = 0
		#idxSection = 0

		if self.mAccelator < 0 :
			arrow = -1

		if abs( self.mAccelator ) > self.mLimitInput :
			if self.mAccelator > ( self.mLimitShift + self.mLimitInput ) :
				self.mAccelator = self.mLimitShift + self.mLimitInput
			elif self.mAccelator < -( self.mLimitShift + self.mLimitInput ):
				self.mAccelator = -( self.mLimitShift + self.mLimitInput )

			current = self.mLimitInput * E_DEFAULT_TRACK_MOVE
			idxSection = abs( self.mAccelator ) - self.mLimitInput
			idxStart = ( self.mTimeshift_curTime / 1000 ) + current
			restSize = ( self.mTimeshift_endTime / 1000 ) - idxStart

			if self.mAccelator < -self.mLimitInput :
				idxStart = ( self.mTimeshift_curTime / 1000 ) - current
				restSize = idxStart - ( self.mTimeshift_staTime / 1000 )

			if restSize > 3600 :
				self.mLimitShift = 100

			if restSize / self.mLimitShift <= ( E_DEFAULT_TRACK_MOVE * 2 ) :
				self.mLimitShift = E_DEFAULT_TRACK_MOVE * 2

			section = restSize / self.mLimitShift
			sectionMoving = section * idxSection

		else :
			current = self.mAccelator * E_DEFAULT_TRACK_MOVE * arrow

		userMoving = ( current + sectionMoving ) * arrow
		userMovingMs = userMoving * 1000

		self.UpdateProgress( userMovingMs )
		#self.UpdateProgressReview( userMovingMs )
		#LOG_TRACE( '-----------accelator[%s] sectionMoving[%s] moving[%s] movingMs[%s]'% ( self.mAccelator, sectionMoving, userMoving, userMovingMs) )
		#LOG_TRACE( '-----------start[%s] end[%s] curr[%s], current[%s] restSize[%s] section[%s] idx[%s] sectionMoving[%s]'% ( self.mTimeshift_staTime, self.mTimeshift_endTime, self.mTimeshift_curTime, current, restSize, section, idxSection, sectionMoving ) )

		tempStartTime   = self.mTimeshift_staTime / 1000
		tempCurrentTime = self.mTimeshift_curTime / 1000
		tempEndTime     = self.mTimeshift_endTime / 1000
		timeFormat      = TimeFormatEnum.E_HH_MM_SS
		if self.mMode == ElisEnum.E_MODE_TIMESHIFT :
			duration = self.mTimeshift_endTime / 1000
			if tempStartTime < 1 :
				tempStartTime = self.mLocalTime - duration
				tempCurrentTime = tempStartTime + tempCurrentTime
			else :
				tempStartTime += self.mLocalTime - duration
				tempCurrentTime = ( self.mLocalTime - duration ) + tempCurrentTime
			tempEndTime = self.mLocalTime


		elif self.mMode == ElisEnum.E_MODE_PVR :
			timeFormat = TimeFormatEnum.E_AH_MM_SS

		lblCurrentTime = tempCurrentTime + userMoving
		self.mAsyncMove = self.mTimeshift_playTime + userMovingMs

		if self.mAsyncMove >= ( self.mTimeshift_endTime - 1000 ) :
			lblCurrentTime  = tempEndTime - 1
			self.mAsyncMove = self.mTimeshift_endTime - 1000
		elif self.mAsyncMove <= self.mTimeshift_staTime :
			lblCurrentTime  = tempStartTime
			self.mAsyncMove = self.mTimeshift_staTime

		lbl_timeP = TimeToString( lblCurrentTime, timeFormat )
		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_CURRENT, lbl_timeP, E_TAG_LABEL )

		self.mAsyncShiftTimer = threading.Timer( 0.5, self.AsyncUpdateCurrentMove, [aStartOnLeft] )
		self.mAsyncShiftTimer.start( )


	def StopAsyncMove( self ) :
		if self.mAsyncShiftTimer and self.mAsyncShiftTimer.isAlive( ) :
			self.mAsyncShiftTimer.cancel( )
			del self.mAsyncShiftTimer

		self.mAsyncShiftTimer  = None


	def AsyncUpdateCurrentMove( self, aStartOnLeft = False ) :
		try :
			if self.mFlagUserMove :
				if aStartOnLeft :
					ret = self.mDataCache.Player_JumpTo( self.mAsyncMove )
					self.mIsLeftOnTimeshift = False

				else :
					if self.mSpeed != 100 :
						self.mDataCache.Player_Resume( )

					ret = self.mDataCache.Player_JumpToIFrame( self.mAsyncMove )

				self.InitTimeShift( )
				self.mFlagUserMove = False
				self.mAccelator = 0
				self.mUserMoveTime = 0
				self.mAsyncMove = 0
				self.mTotalUserMoveTime = 0
				self.mAccelatorMoving = 0

		except Exception, e :
			LOG_ERR( 'Error exception[%s]'% e )

		self.UpdatePropertyGUI( 'IsShift', 'False' )


	def MoveToSeekFrame( self, aKey ) :
		if aKey == 0 :
			return -1

		self.StopAutomaticHide( )
		self.mFlag_OnEvent = False

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_TIMESHIFT_JUMP )
		dialog.SetDialogProperty( str( aKey ) )
		dialog.doModal( )

		self.mFlag_OnEvent = True

		isOK = dialog.IsOK( )
		if isOK == E_DIALOG_STATE_YES :

			move = dialog.GetMoveToJump( )
			if move :
				if self.mSpeed != 100 :
					self.mDataCache.Player_Resume( )

				ret = self.mDataCache.Player_JumpToIFrame( int( move ) )

		self.RestartAutomaticHide( )


	def GetStatusSpeed( self ) :
		return self.mSpeed


	def GetStatusMode( self ) :
		return self.mMode


