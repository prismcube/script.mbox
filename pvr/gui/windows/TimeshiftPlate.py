from pvr.gui.WindowImport import *
import time

#control ids
E_CONTROL_ID_IMAGE_RECORDING1 		= 10
E_CONTROL_ID_LABEL_RECORDING1 		= 11
E_CONTROL_ID_IMAGE_RECORDING2 		= 15
E_CONTROL_ID_LABEL_RECORDING2 		= 16
E_CONTROL_ID_IMAGE_REWIND 			= 31
E_CONTROL_ID_IMAGE_FORWARD 			= 32
E_CONTROL_ID_LABEL_SPEED 			= 33
E_CONTROL_ID_PROGRESS 				= 201
E_CONTROL_ID_BUTTON_CURRENT 		= 202
E_CONTROL_ID_LABEL_MODE 			= 203
E_CONTROL_ID_EVENT_CLOCK 			= 211
E_CONTROL_ID_LABEL_TS_START_TIME 	= 221
E_CONTROL_ID_LABEL_TS_END_TIME 		= 222
E_CONTROL_ID_LIST_SHOW_BOOKMARK		= 500
E_CONTROL_ID_BUTTON_VOLUME 			= 3701
E_CONTROL_ID_BUTTON_START_RECORDING = 3702
E_CONTROL_ID_BUTTON_REWIND 			= 3704
E_CONTROL_ID_BUTTON_PLAY 			= 3705
E_CONTROL_ID_BUTTON_PAUSE 			= 3706
E_CONTROL_ID_BUTTON_STOP 			= 3707
E_CONTROL_ID_BUTTON_FORWARD 		= 3708
E_CONTROL_ID_BUTTON_JUMP_RR 		= 3709
E_CONTROL_ID_BUTTON_JUMP_FF 		= 3710
E_CONTROL_ID_BUTTON_BOOKMARK 		= 3711

#value enum
E_CONTROL_ENABLE  = 'enable'
E_CONTROL_VISIBLE = 'visible'
E_CONTROL_LABEL   = 'label'
E_CONTROL_POSY    = 'posy'

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

E_DEFAULT_POSY = 25
E_PROGRESS_WIDTH_MAX = 980

E_INDEX_FIRST_RECORDING = 0
E_INDEX_SECOND_RECORDING = 1

class TimeShiftPlate( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )

		#default
		self.mProgressbarWidth = E_PROGRESS_WIDTH_MAX
		self.mCurrentChannel=[]
		self.mProgress_idx = 0.0
		self.mEventID = 0
		self.mMode = ElisEnum.E_MODE_LIVE
		self.mIsPlay = FLAG_PLAY
		self.mFlag_OnEvent = True

		self.mAsyncShiftTimer = None
		self.mAutomaticHideTimer = None	
		self.mAutomaticHide = True

		self.mStartTimeShowed = False

		self.mPrekey = None


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		LOG_TRACE( 'winID[%d]'% self.mWinId )

		self.mStartTimeShowed = False

		self.mCtrlImgRec1           = self.getControl( E_CONTROL_ID_IMAGE_RECORDING1 )
		self.mCtrlLblRec1           = self.getControl( E_CONTROL_ID_LABEL_RECORDING1 )
		self.mCtrlImgRec2           = self.getControl( E_CONTROL_ID_IMAGE_RECORDING2 )
		self.mCtrlLblRec2           = self.getControl( E_CONTROL_ID_LABEL_RECORDING2 )
		self.mCtrlImgRewind	        = self.getControl( E_CONTROL_ID_IMAGE_REWIND )
		self.mCtrlImgForward        = self.getControl( E_CONTROL_ID_IMAGE_FORWARD )
		self.mCtrlLblSpeed          = self.getControl( E_CONTROL_ID_LABEL_SPEED )
		self.mCtrlProgress          = self.getControl( E_CONTROL_ID_PROGRESS )
		self.mCtrlBtnCurrent        = self.getControl( E_CONTROL_ID_BUTTON_CURRENT )
		self.mCtrlLblMode           = self.getControl( E_CONTROL_ID_LABEL_MODE )
		self.mCtrlEventClock        = self.getControl( E_CONTROL_ID_EVENT_CLOCK )
		self.mCtrlLblTSStartTime    = self.getControl( E_CONTROL_ID_LABEL_TS_START_TIME )
		self.mCtrlLblTSEndTime      = self.getControl( E_CONTROL_ID_LABEL_TS_END_TIME )

		self.mCtrlBtnVolume         = self.getControl( E_CONTROL_ID_BUTTON_VOLUME )
		self.mCtrlBtnStartRec       = self.getControl( E_CONTROL_ID_BUTTON_START_RECORDING )
		#self.mCtrlBtnStopRec        = self.getControl( 403 )
		self.mCtrlBtnRewind         = self.getControl( E_CONTROL_ID_BUTTON_REWIND )
		self.mCtrlBtnPlay           = self.getControl( E_CONTROL_ID_BUTTON_PLAY )
		self.mCtrlBtnPause          = self.getControl( E_CONTROL_ID_BUTTON_PAUSE )
		self.mCtrlBtnStop           = self.getControl( E_CONTROL_ID_BUTTON_STOP )
		self.mCtrlBtnForward        = self.getControl( E_CONTROL_ID_BUTTON_FORWARD )
		self.mCtrlBtnJumpRR         = self.getControl( E_CONTROL_ID_BUTTON_JUMP_RR )
		self.mCtrlBtnJumpFF         = self.getControl( E_CONTROL_ID_BUTTON_JUMP_FF )
		self.mCtrlBtnBookMark       = self.getControl( E_CONTROL_ID_BUTTON_BOOKMARK )
		self.mCtrlBookMarkList      = self.getControl( E_CONTROL_ID_LIST_SHOW_BOOKMARK )

		#test
		self.mCtrlLblTest          = self.getControl( 35 )

		self.mFlag_OnEvent = True
		self.mTimeshift_staTime = 0.0
		self.mTimeshift_curTime = 0.0
		self.mTimeshift_endTime = 0.0
		self.mIsTimeshiftPending = False
		self.mSpeed = 100	#normal
		self.mLocalTime = 0
		self.mTimeShiftExcuteTime = 0
		self.mUserMoveTime = 0
		self.mUserMoveTimeBack = 0
		self.mFlagUserMove = False
		self.mAccelator = 0
		self.mRepeatTimeout = 1
		self.mAsyncShiftTimer = None
		self.mAutomaticHideTimer = None
		self.mServiceType = ElisEnum.E_SERVICE_TYPE_TV
		self.mBookmarkButton = []
		self.mBookmarkIdx = 0
		self.mThumbnailList = []
		self.mBookmarkList = []

		self.mLocalTime = self.mDataCache.Datetime_GetLocalTime( )

		self.SetRadioScreen( )
		self.ShowRecordingInfo( )
		self.mTimeShiftExcuteTime = self.mDataCache.Datetime_GetLocalTime( )


		self.InitLabelInfo( )
		self.InitTimeShift( )

		label = self.GetModeValue( )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_MODE, label )

		self.GetNextSpeed( E_ONINIT )

		if self.mPrekey :
			if self.mPrekey == Action.ACTION_MBOX_REWIND :
				self.onClick( E_CONTROL_ID_BUTTON_REWIND )

			elif self.mPrekey == Action.ACTION_MBOX_FF :
				self.onClick( E_CONTROL_ID_BUTTON_FORWARD )

			elif self.mPrekey == Action.ACTION_PAUSE or self.mPrekey == Action.ACTION_PLAYER_PLAY :
				self.mWin.setProperty( 'IsXpeeding', 'False' )
				if self.mSpeed == 100 :
					self.onClick( E_CONTROL_ID_BUTTON_PAUSE )
				else :
					self.onClick( E_CONTROL_ID_BUTTON_PLAY )

			self.mPrekey = None

		else :
			defaultFocus = E_CONTROL_ID_BUTTON_PLAY
			if self.mSpeed == 100 :
				defaultFocus = E_CONTROL_ID_BUTTON_PAUSE

			self.UpdateSetFocus( defaultFocus )

		self.InitShowThumnail( )

		#run thread
		self.mEventBus.Register( self )

		self.mEnableLocalThread = True
		self.mThreadProgress = self.PlayProgressThread( )
		self.WaitToBuffering( )

		if self.mAutomaticHide == True :
			self.StartAutomaticHide( )

		self.mInitialized = True


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.Close( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

		elif actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 :
			self.MoveToSeekFrame( int( actionId ) - Action.REMOTE_0 )

		elif actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :
			rKey = actionId - ( Action.ACTION_JUMP_SMS2 - 2 )
			self.MoveToSeekFrame( rKey )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass


		elif actionId == Action.ACTION_MOVE_LEFT :
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_BUTTON_CURRENT :
				self.mUserMoveTimeBack = self.mUserMoveTime
				self.mUserMoveTime = -10
				self.mFlagUserMove = True
				self.StopAutomaticHide( )
				self.RestartAsyncMove( )
				#LOG_TRACE('left moveTime[%s]'% self.mUserMoveTime )

			elif self.mFocusId == E_CONTROL_ID_LIST_SHOW_BOOKMARK :
				self.StopAutomaticHide( )

			else :
				self.RestartAutomaticHide( )


		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_BUTTON_CURRENT :
				self.mUserMoveTimeBack = self.mUserMoveTime
				self.mUserMoveTime = 10
				self.mFlagUserMove = True
				self.StopAutomaticHide( )
				self.RestartAsyncMove( )
				#LOG_TRACE('right moveTime[%s]'% self.mUserMoveTime )

			elif self.mFocusId == E_CONTROL_ID_LIST_SHOW_BOOKMARK :
				self.StopAutomaticHide( )

			else :
				self.RestartAutomaticHide( )


		elif actionId == Action.ACTION_MOVE_UP :
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_BUTTON_CURRENT :
				self.StopAutomaticHide( )

			else :
				self.RestartAutomaticHide( )

		elif actionId == Action.ACTION_MOVE_DOWN :
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_BUTTON_CURRENT :
				self.StopAutomaticHide( )

			else :
				self.RestartAutomaticHide( )


		elif actionId == Action.ACTION_PAGE_DOWN :
			if self.mMode == ElisEnum.E_MODE_PVR :
				#LOG_TRACE('Archive playing now')
				return -1

			prevChannel = None
			prevChannel = self.mDataCache.Channel_GetPrev( self.mDataCache.Channel_GetCurrent( ) )
			if prevChannel :
				self.mDataCache.Channel_SetCurrent( prevChannel.mNumber, prevChannel.mServiceType )			
				nextWindow = WinMgr.WIN_ID_LIVE_PLATE
				if self.mMode == ElisEnum.E_MODE_PVR :
					nextWindow = WinMgr.WIN_ID_ARCHIVE_WINDOW
				else :
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )

				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( nextWindow, WinMgr.WIN_ID_NULLWINDOW )
				
			
		elif actionId == Action.ACTION_PAGE_UP :
			if self.mMode == ElisEnum.E_MODE_PVR :
				#LOG_TRACE('Archive playing now')
				return -1

			nextChannel = None
			nextChannel = self.mDataCache.Channel_GetNext( self.mDataCache.Channel_GetCurrent( ) )
			if nextChannel :
				self.mDataCache.Channel_SetCurrent( nextChannel.mNumber, nextChannel.mServiceType )
				nextWindow = WinMgr.WIN_ID_LIVE_PLATE
				if self.mMode == ElisEnum.E_MODE_PVR :
					nextWindow = WinMgr.WIN_ID_ARCHIVE_WINDOW
				else :
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )

				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( nextWindow, WinMgr.WIN_ID_NULLWINDOW )


		elif actionId == Action.ACTION_CONTEXT_MENU :
			if self.mMode == ElisEnum.E_MODE_PVR :
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_INFO_PLATE )
			else :
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )

		elif actionId == Action.ACTION_PLAYER_PLAY :
			self.mWin.setProperty( 'IsXpeeding', 'False' )
			if self.mSpeed == 100 :
				self.onClick( E_CONTROL_ID_BUTTON_PAUSE )
			else :
				self.onClick( E_CONTROL_ID_BUTTON_PLAY )

		elif actionId == Action.ACTION_STOP :
			self.onClick( E_CONTROL_ID_BUTTON_STOP )

		elif actionId == Action.ACTION_MBOX_REWIND :
			if self.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO or self.mSpeed == 0 :
				return

			self.onClick( E_CONTROL_ID_BUTTON_REWIND )

		elif actionId == Action.ACTION_MBOX_FF : #no service
			if self.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO or self.mSpeed == 0 :
				return

			self.onClick( E_CONTROL_ID_BUTTON_FORWARD )

		elif actionId == Action.ACTION_MBOX_RECORD :
			from pvr.GuiHelper import HasAvailableRecordingHDD
			if HasAvailableRecordingHDD( ) == False :
				return
				
			if self.mMode == ElisEnum.E_MODE_PVR :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Try again after stopping the PVR first' ) )
				dialog.doModal( )
			else :
				self.onClick( E_CONTROL_ID_BUTTON_START_RECORDING )

		elif actionId == Action.ACTION_MBOX_ARCHIVE :
			from pvr.GuiHelper import HasAvailableRecordingHDD
			if HasAvailableRecordingHDD( ) == False :
				return
				
			self.Close( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_SHOW_INFO :
			self.Close( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EPG_WINDOW, WinMgr.WIN_ID_NULLWINDOW )


	def onClick( self, aControlId ):
		if aControlId >= E_CONTROL_ID_BUTTON_REWIND and aControlId <= E_CONTROL_ID_BUTTON_JUMP_FF :
			self.StopAutomaticHide( )
			self.TimeshiftAction( aControlId )

			if aControlId == E_CONTROL_ID_BUTTON_PLAY or aControlId == E_CONTROL_ID_BUTTON_PAUSE :
				aControlId = E_CONTROL_ID_BUTTON_PLAY
				if self.mIsPlay == FLAG_PAUSE :
					aControlId = E_CONTROL_ID_BUTTON_PAUSE
					self.RestartAutomaticHide( )

			self.UpdateSetFocus( aControlId )
			LOG_TRACE('----------focus[%s]'% aControlId )

		elif aControlId == E_CONTROL_ID_BUTTON_VOLUME :
			self.GlobalAction( Action.ACTION_MUTE )
			#xbmc.executebuiltin('xbmc.Action(mute)')
			self.StopAutomaticHide( )
		
		elif aControlId == E_CONTROL_ID_BUTTON_START_RECORDING :	
			from pvr.GuiHelper import HasAvailableRecordingHDD
			if HasAvailableRecordingHDD( ) == False :
				return
				
			runningCount = self.mDataCache.Record_GetRunningRecorderCount( )

			isOK = False
			if  runningCount < 1 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
				dialog.doModal( )

				isOK = dialog.IsOK( )
				if isOK == E_DIALOG_STATE_YES :
					isOK = True

				if dialog.IsOK( ) == E_DIALOG_STATE_ERROR and dialog.GetConflictTimer( ) :
					from pvr.GuiHelper import RecordConflict
					RecordConflict( dialog.GetConflictTimer( ) )
					
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'You have reached the maximum number of\nrecordings allowed' ) )
				dialog.doModal( )

			if isOK :
				self.mDataCache.mCacheReload = True

		elif aControlId == E_CONTROL_ID_BUTTON_BOOKMARK :
			self.StopAutomaticHide( )
			self.ShowDialog( aControlId )
			#self.RestartAutomaticHide( )

		elif aControlId == E_CONTROL_ID_LIST_SHOW_BOOKMARK :
			self.DoContextAction( CONTEXT_ACTION_RESUME_FROM )

		"""
		elif self.mBookmarkButton and len( self.mBookmarkButton ) > 0 and \
			 aControlId >= self.mBookmarkButton[0].getId( ) and \
			 aControlId <= self.mBookmarkButton[len(self.mBookmarkButton)-1].getId( ) :
			self.DoContextAction( CONTEXT_ACTION_RESUME_FROM )
		"""

	def onFocus( self, aControlId ):
		#LOG_TRACE( 'control %d' % controlId )
		pass


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			#LOG_TRACE( '---------CHECK onEVENT winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId( )) )
			if aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
				LOG_TRACE( 'ElisEventPlaybackEOF mType[%d]'% ( aEvent.mType ) )

				if self.mFlag_OnEvent != True :
					return -1

				if aEvent.mType == ElisEnum.E_EOF_START :
					self.mCtrlImgRewind.setVisible( False )
					self.mCtrlImgForward.setVisible( False )
					self.mCtrlLblSpeed.setLabel( '' )
					self.TimeshiftAction( E_CONTROL_ID_BUTTON_PLAY )
					LOG_TRACE( 'EventRecv EOF_START' )

				elif aEvent.mType == ElisEnum.E_EOF_END :
					LOG_TRACE( 'EventRecv EOF_END' )
					xbmc.executebuiltin('xbmc.Action(stop)')
					#self.TimeshiftAction( E_CONTROL_ID_BUTTON_STOP )

			elif aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or \
				 aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
				self.ShowRecordingInfo( )
				self.mDataCache.mCacheReload = True

		else:
			LOG_TRACE( 'TimeshiftPlate winID[%d] this winID[%d]'% ( self.mWinId, xbmcgui.getCurrentWindowId( ) ) )


	def TimeshiftAction( self, aFocusId ) :
		ret = False

		if aFocusId == E_CONTROL_ID_BUTTON_PLAY :
			if self.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.mDataCache.Player_StartTimeshiftPlayback( ElisEnum.E_PLAYER_TIMESHIFT_START_PAUSE, 0 )

			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				ret = self.mDataCache.Player_Resume( )

			elif self.mMode == ElisEnum.E_MODE_PVR :
				ret = self.mDataCache.Player_Resume( )

			LOG_TRACE( 'play_resume( ) ret[%s]'% ret )
			#if ret :
			if self.mSpeed != 100 :
				#_self.mDataCache.Player_SetSpeed( 100 )
				self.UpdateControlGUI( E_CONTROL_ID_IMAGE_REWIND, False )
				self.UpdateControlGUI( E_CONTROL_ID_IMAGE_FORWARD, False )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_SPEED, '' )

			self.mIsPlay = FLAG_PAUSE

			label = self.GetModeValue( )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_MODE, label )
			# toggle
			self.UpdateControlGUI( E_CONTROL_ID_BUTTON_PLAY, False )
			self.UpdateControlGUI( E_CONTROL_ID_BUTTON_PAUSE, True )
			self.mWin.setProperty( 'IsXpeeding', 'True' )

			#blocking release
			if self.mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
				self.SetBlockingButtonEnable( True )

		elif aFocusId == E_CONTROL_ID_BUTTON_PAUSE :
			if self.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.mDataCache.Player_StartTimeshiftPlayback( ElisEnum.E_PLAYER_TIMESHIFT_START_PAUSE, 0 )

			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				ret = self.mDataCache.Player_Pause( )

			elif self.mMode == ElisEnum.E_MODE_PVR :
				ret = self.mDataCache.Player_Pause( )

			LOG_TRACE( 'play_pause( ) ret[%s]'% ret )
			if ret :
				self.mIsPlay = FLAG_PLAY

				# toggle
				self.UpdateControlGUI( E_CONTROL_ID_BUTTON_PLAY, True )
				self.UpdateControlGUI( E_CONTROL_ID_BUTTON_PAUSE, False )
				self.mWin.setProperty( 'IsXpeeding', 'True' )

				#blocking
				if self.mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
					self.SetBlockingButtonEnable( False )

		elif aFocusId == E_CONTROL_ID_BUTTON_STOP :
			if self.mMode == ElisEnum.E_MODE_LIVE :
				self.mIsPlay = FLAG_STOP
				ret = self.mDataCache.Player_Stop( )
				self.Close( )
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE, WinMgr.WIN_ID_NULLWINDOW )
				
			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				ret = self.mDataCache.Player_Stop( )
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE, WinMgr.WIN_ID_NULLWINDOW )

			elif self.mMode == ElisEnum.E_MODE_PVR :
				ret = self.mDataCache.Player_Stop( )
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )

			return

		elif aFocusId == E_CONTROL_ID_BUTTON_REWIND :
			if self.mSpeed == 0 or self.mSpeed <= -6400 :
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

			if ret :
				self.mIsPlay = FLAG_PLAY
				#LOG_WARN( 'status =%d ret[%s], player_SetSpeed[%s]'% ( self.mMode , ret, nextSpeed ) )

		elif aFocusId == E_CONTROL_ID_BUTTON_FORWARD :
			if self.mSpeed == 0 or self.mSpeed >= 6400 :
				return 

			nextSpeed = 100
			nextSpeed = self.GetNextSpeed( aFocusId )

			if self.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.mDataCache.Player_SetSpeed( nextSpeed )

			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				ret = self.mDataCache.Player_SetSpeed( nextSpeed )

			elif self.mMode == ElisEnum.E_MODE_PVR :
				ret = self.mDataCache.Player_SetSpeed( nextSpeed )

			if ret :
				self.mIsPlay = FLAG_PLAY
				#LOG_WARN( 'status =%d ret[%s], player_SetSpeed[%s]'% ( self.mMode , ret, nextSpeed ) )

		elif aFocusId == E_CONTROL_ID_BUTTON_JUMP_RR :
			if self.mSpeed == 0 :
				return

			self.InitTimeShift( )
			prevJump = self.mTimeshift_playTime - 10000
			if prevJump < self.mTimeshift_staTime :
				prevJump = self.mTimeshift_staTime + 1000
			ret = self.mDataCache.Player_JumpToIFrame( prevJump )
			#LOG_TRACE('JumpRR ret[%s]'% ret )

		elif aFocusId == E_CONTROL_ID_BUTTON_JUMP_FF :
			if self.mSpeed == 0 :
				return

			self.InitTimeShift( )
			nextJump = self.mTimeshift_playTime + 10000
			if nextJump > self.mTimeshift_endTime :
				nextJump = self.mTimeshift_endTime - 1000
			ret = self.mDataCache.Player_JumpToIFrame( nextJump )
			#LOG_TRACE('JumpFF ret[%s]'% ret )

		return ret


	def InitLabelInfo(self) :
		self.mEventCopy = []
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_MODE,          '' )
		self.UpdateControlGUI( E_CONTROL_ID_EVENT_CLOCK,         '' )
		self.UpdateControlGUI( E_CONTROL_ID_PROGRESS,             0 )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_TS_START_TIME, '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_TS_END_TIME,   '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_SPEED,         '' )
		self.UpdateControlGUI( E_CONTROL_ID_IMAGE_REWIND,     False )
		self.UpdateControlGUI( E_CONTROL_ID_IMAGE_FORWARD,    False )
		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_CURRENT,     '', E_CONTROL_LABEL )
		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_CURRENT,      0, E_CONTROL_POSY )

		visible = True
		zappingMode = self.mDataCache.Zappingmode_GetCurrent( )
		if zappingMode and zappingMode.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
			self.mServiceType = ElisEnum.E_SERVICE_TYPE_RADIO
			visible = False

		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_REWIND, visible, E_CONTROL_VISIBLE )
		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_FORWARD , visible, E_CONTROL_VISIBLE )


	def SetBlockingButtonEnable( self, aValue ) :
		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_REWIND, aValue, E_CONTROL_ENABLE )
		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_FORWARD, aValue, E_CONTROL_ENABLE )
		strValue = '%s'% aValue
		self.mWin.setProperty( 'IsXpeeding', strValue )


	def UpdateControlGUI( self, aCtrlID = None, aValue = None, aExtra = None ) :
		#LOG_TRACE( 'Enter control[%s] value[%s] extra[%s]'% (aCtrlID, aValue, aExtra) )

		if aCtrlID == E_CONTROL_ID_BUTTON_VOLUME :
			self.mCtrlBtnVolume.setVisible( aValue )

		elif aCtrlID == E_CONTROL_ID_BUTTON_START_RECORDING :
			if aExtra == E_CONTROL_ENABLE :
				self.mCtrlBtnStartRec.setEnabled( aValue )
			elif aExtra == E_CONTROL_VISIBLE :
				self.mCtrlBtnStartRec.setVisible( aValue )

		elif aCtrlID == E_CONTROL_ID_BUTTON_PLAY :
			self.mCtrlBtnPlay.setVisible( aValue )

		elif aCtrlID == E_CONTROL_ID_BUTTON_PAUSE :
			self.mCtrlBtnPause.setVisible( aValue )

		elif aCtrlID == E_CONTROL_ID_BUTTON_STOP :
			self.mCtrlBtnStop.setVisible( aValue )

		elif aCtrlID == E_CONTROL_ID_BUTTON_REWIND :
			if aExtra == E_CONTROL_ENABLE :
				self.mCtrlBtnRewind.setEnabled( aValue )
			elif aExtra == E_CONTROL_VISIBLE :
				self.mCtrlBtnRewind.setVisible( aValue )

		elif aCtrlID == E_CONTROL_ID_BUTTON_FORWARD :
			if aExtra == E_CONTROL_ENABLE :
				self.mCtrlBtnForward.setEnabled( aValue )
			elif aExtra == E_CONTROL_VISIBLE :
				self.mCtrlBtnForward.setVisible( aValue )

		elif aCtrlID == E_CONTROL_ID_IMAGE_REWIND :
			self.mCtrlImgRewind.setVisible( aValue )

		elif aCtrlID == E_CONTROL_ID_IMAGE_FORWARD :
			self.mCtrlImgForward.setVisible( aValue )

		elif aCtrlID == E_CONTROL_ID_EVENT_CLOCK :
			self.mCtrlEventClock.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_PROGRESS :
			self.mCtrlProgress.setPercent( aValue )

		elif aCtrlID == E_CONTROL_ID_BUTTON_CURRENT :
			if aExtra == E_CONTROL_LABEL:
				self.mCtrlBtnCurrent.setLabel( aValue )
			elif aExtra == E_CONTROL_POSY:
				self.mCtrlBtnCurrent.setPosition( aValue, E_DEFAULT_POSY )
			elif aExtra == E_CONTROL_ENABLE:
				self.mCtrlBtnCurrent.setEnabled( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_TS_START_TIME :
			self.mCtrlLblTSStartTime.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_TS_END_TIME :
			self.mCtrlLblTSEndTime.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_SPEED :
			self.mCtrlLblSpeed.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_RECORDING1 :
			self.mCtrlLblRec1.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_RECORDING2 :
			self.mCtrlLblRec2.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_MODE :
			self.mCtrlLblMode.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_BUTTON_BOOKMARK :
			if aExtra == E_CONTROL_VISIBLE :
				self.mCtrlBtnBookMark.setVisible( aValue )


		"""
		elif aCtrlID == E_CONTROL_ID_BUTTON_JUMP_RR :
			if aExtra == E_CONTROL_ENABLE:
				self.mCtrlBtnJumpRR.setEnabled( aValue )

		elif aCtrlID == E_CONTROL_ID_BUTTON_JUMP_FF :
			if aExtra == E_CONTROL_ENABLE:
				self.mCtrlBtnJumpFF.setEnabled( aValue )
		"""


	def UpdatePropertyGUI( self, aPropertyID = None, aValue = None ) :
		#LOG_TRACE( 'Enter property[%s] value[%s]'% (aPropertyID, aValue) )
		if aPropertyID == None :
			return

		self.mWin.setProperty( aPropertyID, aValue )


	def UpdateSetFocus( self, aControlId = E_CONTROL_ID_BUTTON_PLAY ) :
		startTime = time.time()
		loopTime = 0.0
		sleepTime = 0.01
		while loopTime < 1.5 :
			self.setFocusId( aControlId )
			if aControlId == self.getFocusId( ) :
				break
			time.sleep( sleepTime )
			loopTime += sleepTime

		#LOG_TRACE('-----------control[%s] setFocus time[%s]'% ( aControlId, ( time.time() - startTime ) ) )


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

			if status.mStartTimeInMs :
				self.mTimeshift_staTime = status.mStartTimeInMs #/ 1000.0
			if status.mPlayTimeInMs :
				self.mTimeshift_curTime = status.mPlayTimeInMs  #/ 1000.0
			if status.mEndTimeInMs :
				self.mTimeshift_endTime = status.mEndTimeInMs   #/ 1000.0

			tempStartTime   = self.mTimeshift_staTime / 1000
			tempCurrentTime = self.mTimeshift_curTime / 1000
			tempEndTime     = self.mTimeshift_endTime / 1000

			if status.mMode == ElisEnum.E_MODE_TIMESHIFT :
				localTime = self.mDataCache.Datetime_GetLocalTime( )
				duration = (self.mTimeshift_endTime - self.mTimeshift_staTime) / 1000
				tempStartTime = localTime - duration
				tempCurrentTime = tempStartTime + (self.mTimeshift_curTime / 1000 )
				tempEndTime =  localTime


			#Speed label
			self.mSpeed  = status.mSpeed

			if self.mSpeed != 0 :
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
				if self.mStartTimeShowed == False :
					self.UpdateControlGUI( E_CONTROL_ID_LABEL_TS_START_TIME, lbl_timeS )
			if lbl_timeP != '' :
				self.UpdateControlGUI( E_CONTROL_ID_BUTTON_CURRENT, lbl_timeP, E_CONTROL_LABEL )
			if lbl_timeE != '' :
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_TS_END_TIME, lbl_timeE )

			if tempStartTime > 0 :
				self.mStartTimeShowed = True

			self.GetNextSpeed( E_ONINIT )


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
			elif self.mSpeed == 100 or self.mSpeed == 0 :
				ret = -200
			elif self.mSpeed == 120 :
				ret = 100
			elif self.mSpeed == 160 :
				ret = 120
			elif self.mSpeed == 200 :
				ret = 100 #160
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
			elif self.mSpeed == 100 or self.mSpeed == 0 :
				ret = 200 #120
			elif self.mSpeed == 120 :
				ret = 160
			elif self.mSpeed == 160 :
				ret = 200
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

		lspeed = ''
		flagFF = False
		flagRR = False
		if ret == 100 or ret == 0 :
			lspeed = ''
		else :
			lspeed = '%sx'% ( abs(ret) / 100)
			if ret > 100 :
				flagFF = True
				flagRR = False
			else :
				flagFF = False
				flagRR = True

		self.UpdateControlGUI( E_CONTROL_ID_IMAGE_REWIND,  flagRR )
		self.UpdateControlGUI( E_CONTROL_ID_IMAGE_FORWARD, flagFF )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_SPEED,   lspeed )

		if ret == 100 :
			self.UpdateControlGUI( E_CONTROL_ID_BUTTON_PLAY, False )
			self.UpdateControlGUI( E_CONTROL_ID_BUTTON_PAUSE, True )
			self.mWin.setProperty( 'IsXpeeding', 'True' )
			#LOG_TRACE( '-------Play----------------------speed[%s]'% ret)

		else :
			self.UpdateControlGUI( E_CONTROL_ID_BUTTON_PLAY, True )			
			self.UpdateControlGUI( E_CONTROL_ID_BUTTON_PAUSE, False )
			self.mWin.setProperty( 'IsXpeeding', 'False' )
			#LOG_TRACE( '-------Pause----------------------speed[%s]'% ret)

		return ret


	def GetModeValue( self ) :
		labelMode = ''
		buttonHide= True

		if self.mMode == ElisEnum.E_MODE_LIVE or self.mMode == ElisEnum.E_MODE_TIMESHIFT :
			labelMode = E_TAG_COLOR_GREEN + 'TIMESHIFT' + E_TAG_COLOR_END
		elif self.mMode == ElisEnum.E_MODE_PVR :
			labelMode = E_TAG_COLOR_RED + 'PVR' + E_TAG_COLOR_END
			buttonHide= False
		elif self.mMode == ElisEnum.E_MODE_EXTERNAL_PVR :
			labelMode = 'EXTERNAL_PVR'
		elif self.mMode == ElisEnum.E_MODE_MULTIMEDIA :
			labelMode = 'MULTIMEDIA'
		else :
			labelMode = 'UNKNOWN'

		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_BOOKMARK, not buttonHide, E_CONTROL_VISIBLE )
		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_START_RECORDING, buttonHide, E_CONTROL_VISIBLE )
		return labelMode


	@RunThread
	def PlayProgressThread( self ) :
		count = 0
		while self.mEnableLocalThread :
			if int( self.mRepeatTimeout / 0.02 ) <= count :
				LOG_TRACE( 'repeat <<<<' )

				#update localTime
				self.mLocalTime = self.mDataCache.Datetime_GetLocalTime( )
				lbl_localTime = TimeToString( self.mLocalTime, TimeFormatEnum.E_AW_HH_MM )
				self.UpdateControlGUI( E_CONTROL_ID_EVENT_CLOCK, lbl_localTime )

				if self.mIsPlay != FLAG_STOP :
					self.InitTimeShift( )
					self.UpdateProgress( )
				count = 0

			#time.sleep( self.mRepeatTimeout )
			time.sleep( 0.02 )
			count = count + 1
			

	def UpdateProgress( self, loop = 0 ):
		try :
			lbl_timeE = ''
			lbl_timeP = ''
			curTime = 0

			#calculate current position
			totTime = self.mTimeshift_endTime - self.mTimeshift_staTime
			curTime = self.mTimeshift_curTime - self.mTimeshift_staTime

			if totTime > 0 and curTime >= 0 :
				self.mProgress_idx = (curTime / float(totTime))  * 100.0

				#LOG_TRACE( 'curTime[%s] totTime[%s]'% ( curTime,totTime ) )
				#LOG_TRACE( 'curTime[%s] idx[%s] endTime[%s]'% ( self.mTimeshift_curTime, self.mProgress_idx, self.mTimeshift_endTime ) )

				if self.mProgress_idx > 100 :
					self.mProgress_idx = 100
				elif self.mProgress_idx < 0 :
					self.mProgress_idx = 0

				#progress drawing
				posx = int( self.mProgress_idx * self.mProgressbarWidth / 100 )
				self.UpdateControlGUI( E_CONTROL_ID_BUTTON_CURRENT, posx, E_CONTROL_POSY )
				self.UpdateControlGUI( E_CONTROL_ID_PROGRESS, self.mProgress_idx )
				#LOG_TRACE( 'progress endTime[%s] idx[%s] posx[%s]'% (self.mTimeshift_endTime, self.mProgress_idx, posx) )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def ShowDialog( self, aFocusId ) :
		if aFocusId == E_CONTROL_ID_BUTTON_BOOKMARK :
			if not self.mPlatform.IsPrismCube( ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'No support %s' )% self.mPlatform.GetName( ) )
				dialog.doModal( )
				self.RestartAutomaticHide( )
				return

			self.BookMarkContext( )


	def EventReceivedDialog( self, aDialog ) :
		ret = aDialog.GetCloseStatus( )
		if ret == Action.ACTION_PLAYER_PLAY :
			xbmc.executebuiltin('xbmc.Action(play)')

		elif ret == Action.ACTION_STOP :
			xbmc.executebuiltin('xbmc.Action(stop)')


	def BookMarkContext( self ) :
		context = []
		context.append( ContextItem( MR_LANG( 'Add bookmark' ), CONTEXT_ACTION_ADD_TO_BOOKMARK ) )
		context.append( ContextItem( MR_LANG( 'Add To AutoChapter' ), CONTEXT_ACTION_ADD_AUTO_CHAPTER ) )
		context.append( ContextItem( MR_LANG( 'Show bookmark list' ), CONTEXT_ACTION_SHOW_LIST ) )

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
			self.mDataCache.Player_CreateBookmark( )
			self.InitShowThumnail( )
			self.RestartAutomaticHide( )

		elif aSelectAction == CONTEXT_ACTION_SHOW_LIST :
			playingRecord = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW ).GetPlayingRecord( )

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_BOOKMARK )
			dialog.SetDefaultProperty( playingRecord )
			dialog.doModal( )
			self.RestartAutomaticHide( )
			#tempList = dialog.GetSelectedList( )
			#LOG_TRACE('------------dialog list[%s]'% tempList )

		elif aSelectAction == CONTEXT_ACTION_ADD_AUTO_CHAPTER :
			self.AutoChapterAddBookmark( )
			self.InitShowThumnail( )

		elif aSelectAction == CONTEXT_ACTION_RESUME_FROM :
			self.StartBookmarkPlayback( )


	def StartBookmarkPlayback( self ) :
		if self.mBookmarkList == None or len( self.mBookmarkList ) < 1 or self.mBookmarkList[0].mError != 0 :
			return 

		if self.mSpeed != 100 :
			LOG_TRACE( 'Can not jump to iFrame(bookmark), status is Pause,Forward,Rewind in now' )
			return

		#playOffset = self.mBookmarkList[self.mBookmarkIdx].mTimeMs
		idx = self.mCtrlBookMarkList.getSelectedPosition( )
		playOffset = self.mBookmarkList[idx].mTimeMs
		LOG_TRACE('bookmark idx[%s] pos[%s]'% ( idx, TimeToString( playOffset / 1000, TimeFormatEnum.E_AH_MM_SS ) ) )

		#self.mDataCache.Player_StartInternalRecordPlayback( playingRecord.mRecordKey, playingRecord.mServiceType, playOffset, 100 )
		self.mDataCache.Player_JumpToIFrame( playOffset )


	def AutoChapterAddBookmark( self ) :
		# limit playtime under 30sec
		mediaTime = self.mTimeshift_endTime - self.mTimeshift_staTime
		if ( mediaTime / 1000 ) < 30 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Make media length longer than 30 secs to create a chapter' ) )
 			dialog.doModal( )
			return

		self.StopAutomaticHide( )

		self.OpenBusyDialog( )
		restoreCurrent = self.mTimeshift_playTime

		section = mediaTime / 10
		partition = 0
		for i in range( 1, 10 ) :
			partition += section
			lbl_timeS = TimeToString( partition, TimeFormatEnum.E_AH_MM_SS )
			#LOG_TRACE( '------------chapter idx[%s][%s] [%s]'% ( i, partition, lbl_timeS ) )
			ret = self.mDataCache.Player_JumpToIFrame( partition )
			if ret :
				self.mDataCache.Player_CreateBookmark( )

			time.sleep(0.5)

			#window close then stop this function
			if not self.mEnableLocalThread :
				break

		self.mDataCache.Player_JumpToIFrame( restoreCurrent )
		LOG_TRACE( '---------restoreCurrent[%s]'% TimeToString( restoreCurrent, TimeFormatEnum.E_AH_MM_SS ) )
		self.CloseBusyDialog( )

		self.RestartAutomaticHide( )


	def ShowBookmark( self ) :
		#self.StopAutomaticHide( )

		self.mCtrlBookMarkList.reset( )
		if len( self.mBookmarkList ) < 1 :
			self.UpdatePropertyGUI( 'BookMarkShow', 'False' )
			LOG_TRACE( 'bookmark None, show False' )
			return

		listItems = []
		for i in range( len( self.mBookmarkList ) ) :
			lblOffset = TimeToString( self.mBookmarkList[i].mTimeMs / 1000, TimeFormatEnum.E_AH_MM_SS )
			listItem = xbmcgui.ListItem( '%s'% lblOffset )
			listItem.setProperty( 'BookMarkThumb', self.mThumbnailList[i] )
			#LOG_TRACE('show listIdx[%s] file[%s]'% ( i, self.mThumbnailList[i] ) )

			listItems.append( listItem )
		self.mCtrlBookMarkList.addItems( listItems )

		self.UpdatePropertyGUI( 'BookMarkShow', 'True' )


	def ShowRecordingInfo( self ) :
		isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )

		strLabelRecord1 = ''
		strLabelRecord2 = ''
		setPropertyRecord1   = 'False'
		setPropertyRecord2   = 'False'
		if isRunRec == 1 :
			setPropertyRecord1 = 'True'
			recInfo = self.mDataCache.Record_GetRunningRecordInfo( E_INDEX_FIRST_RECORDING )
			strLabelRecord1 = '%04d %s'% ( int( recInfo.mChannelNo ), recInfo.mChannelName )

		elif isRunRec == 2 :
			setPropertyRecord1 = 'True'
			setPropertyRecord2 = 'True'
			recInfo = self.mDataCache.Record_GetRunningRecordInfo( E_INDEX_FIRST_RECORDING )
			strLabelRecord1 = '%04d %s'% ( int( recInfo.mChannelNo ), recInfo.mChannelName )
			recInfo = self.mDataCache.Record_GetRunningRecordInfo( E_INDEX_SECOND_RECORDING )
			strLabelRecord2 = '%04d %s'% ( int( recInfo.mChannelNo ), recInfo.mChannelName )

		btnValue = False
		if isRunRec >= 1 :
			btnValue = False
		else :
			btnValue = True

		self.UpdateControlGUI( E_CONTROL_ID_LABEL_RECORDING1, strLabelRecord1 )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_RECORDING2, strLabelRecord2 )
		self.UpdateControlGUI( E_CONTROL_ID_BUTTON_START_RECORDING, btnValue, E_CONTROL_ENABLE )
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
			self.mDataCache.mCacheReload = True


	@RunThread
	def WaitToBuffering( self ) :
		while self.mEnableLocalThread :
			if self.mIsTimeshiftPending :
				waitTime = 0
				self.OpenBusyDialog( )
				while waitTime < 5 :
					if not self.mIsTimeshiftPending :
						break
					time.sleep( 1 )
					waitTime += 1
				self.CloseBusyDialog( )

				#play on
				if not self.mIsTimeshiftPending :
					waitTime = 0
					while waitTime < 5 :
						ret = self.TimeshiftAction( E_CONTROL_ID_BUTTON_PLAY )
						self.UpdateSetFocus( E_CONTROL_ID_BUTTON_PAUSE )

						if self.mSpeed == 100 and ret :
							break
						time.sleep( 1 )
						waitTime += 1
						#LOG_TRACE('-----------repeat[%s] focused[%s] '% ( waitTime + 1,ret ) )

			time.sleep( 1 )


	def InitShowThumnail( self ) :
		#ToDO
		if self.mMode != ElisEnum.E_MODE_PVR :
			self.UpdatePropertyGUI( 'BookMarkShow', 'False' )
			self.mCtrlBookMarkList.reset( )
			return

		playingRecord = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW ).GetPlayingRecord( )
		#LOG_TRACE('--------record[%s]'% playingRecord.mRecordKey )
		if playingRecord == None or playingRecord.mError != 0 :
			self.UpdatePropertyGUI( 'BookMarkShow', 'False' )
			self.mCtrlBookMarkList.reset( )
			return

		mBookmarkList = self.mDataCache.Player_GetBookmarkList( playingRecord.mRecordKey )
		#LOG_TRACE('--------len[%s] [%s]'% ( len( mBookmarkList ), mBookmarkList[0].mError ) )
		if mBookmarkList == None or len( mBookmarkList ) < 1 or mBookmarkList[0].mError != 0 :
			self.UpdatePropertyGUI( 'BookMarkShow', 'False' )
			self.mCtrlBookMarkList.reset( )
			return 

		#for item in mBookmarkList :
		#	LOG_TRACE('timeMs[%s]'% item.mTimeMs )

		self.mThumbnailList = []
		thumbnaillist = []
		thumbnaillist = glob.glob( os.path.join( '/mnt/hdd0/pvr/bookmark/%d'% playingRecord.mRecordKey, 'record_bookmark_%d_*.jpg' % playingRecord.mRecordKey ) )

		#LOG_TRACE('len[%s] list[%s]'% ( len(thumbnaillist), thumbnaillist ) )
		thumbnailHash = {}
		if thumbnaillist and len( thumbnaillist ) > 0 :
			for mfile in thumbnaillist :
				try :
					thumbnailHash[int( os.path.basename(mfile).split('_')[3] )] = mfile
				except Exception, ex :
					LOG_ERR( 'Exception %s'% ex )
					continue

		#LOG_TRACE('len[%s] hash[%s]'% ( len(thumbnailHash), thumbnailHash ) )
		thumCount = len( mBookmarkList ) - 1
		self.mThumbnailList = []
		self.mBookmarkList = []
		oldidx = -1
		for num in range( 10 ) :
			idx = thumCount * num / 10
			if idx == oldidx :
				continue

			oldidx = idx
			mfile = thumbnailHash.get( mBookmarkList[idx].mTimeMs, None )
			if mfile :
				self.mThumbnailList.append( mfile )
				self.mBookmarkList.append( mBookmarkList[idx] )
			#LOG_TRACE(' idx[%s] num[%s] max[%s] file[%s]'% (idx, num, thumCount, mfile ) )

		LOG_TRACE(' len[%s] bookmarkFile[%s]'% ( len(self.mThumbnailList), self.mThumbnailList ) )
		self.ShowBookmark( )


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.mEnableLocalThread = False
		if self.mThreadProgress :
			self.mThreadProgress.join( )

		"""
		if self.mBookmarkButton and len( self.mBookmarkButton ) > 0 :
			for i in range( len( self.mBookmarkButton ) ) :
				LOG_TRACE('mBookmarkButton[%s] [%s]'% ( i, self.mBookmarkButton[i] ) )
				self.removeControl( self.mBookmarkButton[i] )
		"""

		self.StopAsyncMove( )
		self.StopAutomaticHide( )


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
		self.StartAutomaticHide( )

	
	def StartAutomaticHide( self ) :
		prop = ElisPropertyEnum( 'Playback Banner Duration', self.mCommander )
		bannerTimeout = prop.GetProp( )
		self.mAutomaticHideTimer = threading.Timer( bannerTimeout, self.AsyncAutomaticHide )
		self.mAutomaticHideTimer.start( )


	def StopAutomaticHide( self ) :
		if self.mAutomaticHideTimer and self.mAutomaticHideTimer.isAlive( ) :
			self.mAutomaticHideTimer.cancel( )
			del self.mAutomaticHideTimer
			
		self.mAutomaticHideTimer = None


	def RestartAsyncMove( self ) :
		self.StopAsyncMove( )
		self.StartAsyncMove( )


	def StartAsyncMove( self ) :
		self.mAsyncShiftTimer = threading.Timer( 0.5, self.AsyncUpdateCurrentMove ) 				
		self.mAsyncShiftTimer.start( )

		self.mFlagUserMove = False
		self.mAccelator += 1


	def StopAsyncMove( self ) :
		if self.mAsyncShiftTimer and self.mAsyncShiftTimer.isAlive( ) :
			self.mAsyncShiftTimer.cancel( )
			del self.mAsyncShiftTimer

		self.mAsyncShiftTimer  = None


	#TODO : must be need timeout schedule
	def AsyncUpdateCurrentMove( self ) :
		try :
			if self.mFlagUserMove != True :
				#if self.mAccelator > 2 :
					#self.mUserMoveTime = int( self.mUserMoveTime * ( 1.5 ** self.mAccelator) / 10000 )

				self.mUserMoveTime = self.mUserMoveTime * self.mAccelator
				frameJump = self.mTimeshift_playTime + ( self.mUserMoveTime * 1000 )
				if frameJump > self.mTimeshift_endTime :
					frameJump = self.mTimeshift_endTime - 1000
				elif frameJump < self.mTimeshift_staTime :
					frameJump = self.mTimeshift_staTime + 1000

				ret = self.mDataCache.Player_JumpToIFrame( frameJump )
				#LOG_TRACE('2============frameJump[%s] accelator[%s] MoveSec[%s] ret[%s]'% ( frameJump, self.mAccelator, ( self.mUserMoveTime / 10000 ), ret ) )

				self.mFlagUserMove = False
				self.mAccelator = 0
				self.mUserMoveTime = 0
				self.InitTimeShift( )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def MoveToSeekFrame( self, aKey ) :
		if aKey == 0 :
			return -1

		self.mFlag_OnEvent = False

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_TIMESHIFT_JUMP )
		dialog.SetDialogProperty( str( aKey ), E_INDEX_JUMP_MAX, None )
		dialog.doModal( )

		self.mFlag_OnEvent = True

		isOK = dialog.IsOK( )
		if isOK == E_DIALOG_STATE_YES :

			move = dialog.GetMoveToJump( )
			if move :
				ret = self.mDataCache.Player_JumpToIFrame( int( move ) )



