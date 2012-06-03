from pvr.gui.WindowImport import *

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

E_CONTROL_ENABLE  = 'enable'
E_CONTROL_VISIBLE = 'visible'
E_CONTROL_LABEL   = 'label'
E_CONTROL_POSY    = 'posy'

E_DEFAULT_POSY = 25
E_PROGRESS_WIDTH_MAX = 980
E_BUTTON_GROUP_PLAYPAUSE = 450

E_INDEX_FIRST_RECORDING = 0
E_INDEX_SECOND_RECORDING = 1
E_INDEX_JUMP_MAX = 100

E_TAG_COLOR_RED   = '[COLOR red]'
E_TAG_COLOR_GREEN = '[COLOR green]'
E_TAG_COLOR_END   = '[/COLOR]'

class TimeShiftPlate(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)

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


	"""
	def __del__(self):
		LOG_TRACE( 'destroyed TimeshiftPlate' )

		# end thread CurrentTimeThread()
		self.mEnableThread = False
	"""
	

	def onInit(self):
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId )
		LOG_TRACE( 'winID[%d]'% self.mWinId )

		self.mCtrlImgRec1           = self.getControl(  10 )
		self.mCtrlLblRec1           = self.getControl(  11 )
		self.mCtrlImgRec2           = self.getControl(  15 )
		self.mCtrlLblRec2           = self.getControl(  16 )
		self.mCtrlImgRewind	        = self.getControl(  31 )
		self.mCtrlImgForward        = self.getControl(  32 )
		self.mCtrlLblSpeed          = self.getControl(  33 )
		self.mCtrlProgress          = self.getControl( 201 )
		self.mCtrlBtnCurrent        = self.getControl( 202 )
		self.mCtrlLblMode           = self.getControl( 203 )
		self.mCtrlEventClock        = self.getControl( 211 )
		self.mCtrlLblTSStartTime    = self.getControl( 221 )
		self.mCtrlLblTSEndTime      = self.getControl( 222 )

		self.mCtrlBtnVolume         = self.getControl( 401 )
		self.mCtrlBtnStartRec       = self.getControl( 402 )
		#self.mCtrlBtnStopRec        = self.getControl( 403 )
		self.mCtrlBtnRewind         = self.getControl( 404 )
		self.mCtrlBtnPlay           = self.getControl( 405 )
		self.mCtrlBtnPause          = self.getControl( 406 )
		self.mCtrlBtnStop           = self.getControl( 407 )
		self.mCtrlBtnForward        = self.getControl( 408 )
		self.mCtrlBtnJumpRR         = self.getControl( 409 )
		self.mCtrlBtnJumpFF         = self.getControl( 410 )
		self.mCtrlBtnBookMark       = self.getControl( 411 )

		#test
		self.mCtrlLblTest          = self.getControl( 35 )

		self.mFlag_OnEvent = True
		self.mTimeshift_staTime = 0.0
		self.mTimeshift_curTime = 0.0
		self.mTimeshift_endTime = 0.0
		self.mSpeed = 100	#normal
		self.mLocalTime = 0
		self.mTimeShiftExcuteTime = 0
		self.mUserMoveTime = 0
		self.mUserMoveTimeBack = 0
		self.mFlagUserMove = False
		self.mAccelator = 0
		self.mINSTime = 0
		self.mRepeatTimeout = 1
		self.mAsyncShiftTimer = None
		self.mAutomaticHideTimer = None

		self.ShowRecording( )
		
		self.mTimeShiftExcuteTime = self.mDataCache.Datetime_GetLocalTime()

		self.InitLabelInfo( )
		self.InitTimeShift( )

		label = self.GetModeValue( )
		self.UpdateLabelGUI( self.mCtrlLblMode.getId(), label )

		self.GetNextSpeed( E_ONINIT )
		
		if self.mSpeed != 0 :
			self.UpdateLabelGUI( self.mCtrlBtnPlay.getId(), False )
			self.UpdateLabelGUI( self.mCtrlBtnPause.getId(), True )
		else :
			self.UpdateLabelGUI( self.mCtrlBtnPlay.getId(), True )
			self.UpdateLabelGUI( self.mCtrlBtnPause.getId(), False )
		self.setFocusId( E_BUTTON_GROUP_PLAYPAUSE )

		self.mEventBus.Register( self )

		#run thread
		self.mEnableThread = True
		self.CurrentTimeThread()

		if self.mAutomaticHide == True :
			self.StartAutomaticHide()

		LOG_TRACE( 'Leave' )


	def onAction(self, aAction):
		id = aAction.getId()
		self.GlobalAction( id )
		
		if id == Action.ACTION_PREVIOUS_MENU or id == Action.ACTION_PARENT_DIR:
			LOG_TRACE( 'esc close : [%s] [%s]'% (aAction, id) )
			self.Close()
			"""
			WinMgr.GetInstance().GetWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW ).Close()
			WinMgr.GetInstance().GetWindow( WinMgr.WIN_ID_MAINMENU ).Close()
			"""
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_NULLWINDOW )


		elif id >= Action.REMOTE_0 and id <= Action.REMOTE_9 :
			self.KeySearch( id-Action.REMOTE_0 )

		elif id >= Action.ACTION_JUMP_SMS2 and id <= Action.ACTION_JUMP_SMS9 :
			rKey = id - (Action.ACTION_JUMP_SMS2 - 2)
			self.KeySearch( rKey )

		elif id == Action.ACTION_SELECT_ITEM:
			LOG_TRACE( '===== select [%s]' % id )

		elif id == Action.ACTION_MOVE_LEFT :
			self.GetFocusId()
			if self.mFocusId == self.mCtrlBtnCurrent.getId():
				self.mUserMoveTimeBack = self.mUserMoveTime
				self.mUserMoveTime = -10
				self.mFlagUserMove = True
				self.StopAutomaticHide()
				self.RestartAsyncMove()

				LOG_TRACE('left moveTime[%s]'% self.mUserMoveTime )
			else :
				self.RestartAutomaticHide()

		elif id == Action.ACTION_MOVE_RIGHT:
			self.GetFocusId()
			if self.mFocusId == self.mCtrlBtnCurrent.getId():
				self.mUserMoveTimeBack = self.mUserMoveTime
				self.mUserMoveTime = 10
				self.mFlagUserMove = True
				self.StopAutomaticHide()
				self.RestartAsyncMove()

				LOG_TRACE('right moveTime[%s]'% self.mUserMoveTime )
			else :
				self.RestartAutomaticHide()

		elif id == Action.ACTION_PAGE_DOWN:
			LOG_TRACE('key down')
			if self.mDataCache.mStatusIsArchive :
				LOG_TRACE('Archive playing now')
				return -1

			prevChannel = None
			prevChannel = self.mDataCache.Channel_GetPrev( self.mDataCache.Channel_GetCurrent( ) ) #self.mCommander.Channel_GetPrev( )
			if prevChannel :
				self.mDataCache.Channel_SetCurrent( prevChannel.mNumber, prevChannel.mServiceType )			
				#self.mCommander.Channel_SetCurrent( prevChannel.mNumber, prevChannel.mServiceType )
				self.onClick( self.mCtrlBtnStop.getId() )
				
			
		elif id == Action.ACTION_PAGE_UP:
			LOG_TRACE('key up')
			if self.mDataCache.mStatusIsArchive :
				LOG_TRACE('Archive playing now')
				return -1

			nextChannel = None
			nextChannel = self.mDataCache.Channel_GetNext( self.mDataCache.Channel_GetCurrent( ) )
			if nextChannel :
				self.mDataCache.Channel_SetCurrent( nextChannel.mNumber, nextChannel.mServiceType )
				#self.mCommander.Channel_SetCurrent( nextChannel.mNumber, nextChannel.mServiceType )
				self.onClick( self.mCtrlBtnStop.getId() )

		elif id == Action.ACTION_CONTEXT_MENU:
			if self.mMode == ElisEnum.E_MODE_PVR :
				pass
			else :
				self.Close( )
				WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )

		elif id == Action.ACTION_STOP :
			self.onClick( self.mCtrlBtnStop.getId() )

		#test
		elif id == 104 : #scroll up
			self.ShowRecording()
			#self.UpdateLabelGUI( self.mCtrlImgRec1.getId(), True )
		elif id == 105 :
			#self.UpdateLabelGUI( self.mCtrlImgRec1.getId(), False )
			pass


	def onClick(self, aControlId):
		LOG_TRACE( 'control %d' % aControlId )

		if aControlId >= self.mCtrlBtnRewind.getId() and aControlId <= self.mCtrlBtnJumpFF.getId() :

			if aControlId == self.mCtrlBtnPlay.getId() :
				self.RestartAutomaticHide()
			else :
				self.StopAutomaticHide()


			self.TimeshiftAction( aControlId )


		elif aControlId == self.mCtrlBtnVolume.getId():
			self.GlobalAction( Action.ACTION_MUTE )
			self.StopAutomaticHide()
		
		elif aControlId == self.mCtrlBtnStartRec.getId() :
			runningCount = self.ShowRecording()
			LOG_TRACE( 'runningCount[%s]' %runningCount)

			isOK = False
			GuiLock2(True)
			if  runningCount < 1 :
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
				time.sleep(1.5)
				self.ShowRecording()
				self.mDataCache.mCacheReload = True

		elif aControlId == self.mCtrlBtnBookMark.getId():
			self.ShowDialog( aControlId )


	def onFocus(self, aControlId):
		#LOG_TRACE( 'control %d' % controlId )
		pass


	@GuiLock
	def onEvent(self, aEvent):
		LOG_TRACE( 'Enter' )

		if self.mWinId == xbmcgui.getCurrentWindowId():
			if aEvent.getName() == ElisEventPlaybackEOF.getName() :
				#aEvent.printdebug()
				LOG_TRACE( 'mType[%d]' %(aEvent.mType ) )

				if self.mFlag_OnEvent != True :
					LOG_TRACE('ignore event, mFlag_OnEvent[%s]'% self.mFlag_OnEvent)
					return -1

				if aEvent.mType == ElisEnum.E_EOF_START :
					#self.TimeshiftAction( self.mCtrlBtnPlay.getId() )
					LOG_TRACE( 'EventRecv EOF_START' )

				elif aEvent.mType == ElisEnum.E_EOF_END :
					LOG_TRACE( 'EventRecv EOF_STOP' )
					if self.mMode == ElisEnum.E_MODE_PVR :
						#pass
						xbmc.executebuiltin('xbmc.Action(stop)')

			elif aEvent.getName() == ElisEventRecordingStarted.getName() or \
				 aEvent.getName() == ElisEventRecordingStopped.getName() :
				time.sleep(1.5)
				self.ShowRecording()
				self.mDataCache.mCacheReload = True
				LOG_TRACE('Receive Event[%s]'% aEvent.getName() )


		else:
			LOG_TRACE( 'TimeshiftPlate winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId()) )


		LOG_TRACE( 'Leave' )


	def ShowDialog( self, aFocusId ) :
		LOG_TRACE( 'Enter' )

		head = ''
		line1= ''
		if aFocusId == self.mCtrlBtnBookMark.getId( ) :
			head = 'BookMark'
			line1= 'test'

		GuiLock2(True)
		dialog = xbmcgui.Dialog().ok( head, line1 )
		GuiLock2(False)

		LOG_TRACE( 'Leave' )


	def TimeshiftAction( self, aFocusId ):
		LOG_TRACE( 'Enter' )

		ret = False

		if aFocusId == self.mCtrlBtnPlay.getId() :
			if self.mMode == ElisEnum.E_MODE_LIVE :
				#ret = self.mDataCache.Player_StartTimeshiftPlayback( ElisEnum.E_PLAYER_TIMESHIFT_START_PAUSE, 0 )
				ret = self.mDataCache.Player_Resume()

			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				ret = self.mDataCache.Player_Resume()

			elif self.mMode == ElisEnum.E_MODE_PVR:
				ret = self.mDataCache.Player_Resume()

			LOG_TRACE( 'play_resume() ret[%s]'% ret )
			if ret :
				if self.mSpeed != 100:
					#_self.mDataCache.Player_SetSpeed( 100 )
					self.UpdateLabelGUI( self.mCtrlImgRewind.getId(), False )
					self.UpdateLabelGUI( self.mCtrlImgForward.getId(), False )
					self.UpdateLabelGUI( self.mCtrlLblSpeed.getId(), '' )

				self.mIsPlay = FLAG_PAUSE

				label = self.GetModeValue( )
				self.UpdateLabelGUI( self.mCtrlLblMode.getId(), label )
				# toggle
				self.UpdateLabelGUI( self.mCtrlBtnPlay.getId(), False )
				self.UpdateLabelGUI( self.mCtrlBtnPause.getId(), True )
				self.setFocusId( E_BUTTON_GROUP_PLAYPAUSE )

		elif aFocusId == self.mCtrlBtnPause.getId() :
			if self.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.mDataCache.Player_StartTimeshiftPlayback( ElisEnum.E_PLAYER_TIMESHIFT_START_PAUSE, 0 )

			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				ret = self.mDataCache.Player_Pause()
			elif self.mMode == ElisEnum.E_MODE_PVR :
				ret = self.mDataCache.Player_Pause()

			LOG_TRACE( 'play_pause() ret[%s]'% ret )
			if ret :
				self.mIsPlay = FLAG_PLAY

				# toggle
				self.UpdateLabelGUI( self.mCtrlBtnPlay.getId(), True )
				self.UpdateLabelGUI( self.mCtrlBtnPause.getId(), False )
				self.setFocusId( E_BUTTON_GROUP_PLAYPAUSE )

		elif aFocusId == self.mCtrlBtnStop.getId() :
			third = 3
			gobackID = WinMgr.WIN_ID_NULLWINDOW
			while third :
				if self.mMode == ElisEnum.E_MODE_LIVE :
					ret = self.mDataCache.Player_Stop()
					gobackID = WinMgr.WIN_ID_LIVE_PLATE
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )

				elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
					ret = self.mDataCache.Player_Stop()
					gobackID = WinMgr.WIN_ID_LIVE_PLATE

				elif self.mMode == ElisEnum.E_MODE_PVR :
					ret = self.mDataCache.Player_Stop()
					if self.mDataCache.mStatusIsArchive :
						gobackID = WinMgr.WIN_ID_ARCHIVE_WINDOW
					else :
						gobackID = WinMgr.WIN_ID_LIVE_PLATE
					self.mDataCache.SetKeyDisabled( False )

				third -= 1
				LOG_TRACE( 'play_stop() ret[%s] try[%d]'% (ret,third) )
				if ret :
					break
				else:
					time.sleep(0.5)

			self.UpdateLabelGUI( self.mCtrlProgress.getId(), 0 )
			self.mProgress_idx = 0.0

			#self.RecordingStopAll( )
			self.Close()
			WinMgr.GetInstance().ShowWindow( gobackID )
			return

		elif aFocusId == self.mCtrlBtnRewind.getId() :
			nextSpeed = 100
			nextSpeed = self.GetNextSpeed( aFocusId )

			if self.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.mDataCache.Player_StartTimeshiftPlayback( ElisEnum.E_PLAYER_TIMESHIFT_START_REWIND, 0 )
				#ret = self.mDataCache.Player_SetSpeed( nextSpeed )

			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				ret = self.mDataCache.Player_SetSpeed( nextSpeed )

			elif self.mMode == ElisEnum.E_MODE_PVR :
				ret = self.mDataCache.Player_SetSpeed( nextSpeed )

			if ret :
				LOG_TRACE( 'play_rewind() ret[%s], player_SetSpeed[%s]'% (ret, nextSpeed) )

			#resume by toggle
			"""
			if self.mIsPlay == FLAG_PLAY :
				self.UpdateLabelGUI( self.mCtrlBtnPlay.getId(), True )
				self.UpdateLabelGUI( self.mCtrlBtnPause.getId(), False )
			"""
			self.UpdateLabelGUI( self.mCtrlBtnPlay.getId(), True )
			self.UpdateLabelGUI( self.mCtrlBtnPause.getId(), False )


		elif aFocusId == self.mCtrlBtnForward.getId() :
			nextSpeed = 100
			nextSpeed = self.GetNextSpeed( aFocusId )

			if self.mMode == ElisEnum.E_MODE_LIVE :
				#ret = self.mDataCache.Player_StartTimeshiftPlayback( ElisEnum.E_PLAYER_TIMESHIFT_START_REWIND, 0 )
				ret = self.mDataCache.Player_SetSpeed( nextSpeed )

			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				ret = self.mDataCache.Player_SetSpeed( nextSpeed )

			elif self.mMode == ElisEnum.E_MODE_PVR :
				ret = self.mDataCache.Player_SetSpeed( nextSpeed )

			if ret :
				LOG_TRACE( 'play_forward() ret[%s] player_SetSpeed[%s]'% (ret, nextSpeed) )

			#resume by toggle
			"""
			if self.mIsPlay == FLAG_PLAY :
				self.UpdateLabelGUI( self.mCtrlBtnPlay.getId(), True )
				self.UpdateLabelGUI( self.mCtrlBtnPause.getId(), False )
			"""
			self.UpdateLabelGUI( self.mCtrlBtnPlay.getId(), True )
			self.UpdateLabelGUI( self.mCtrlBtnPause.getId(), False )


		elif aFocusId == self.mCtrlBtnJumpRR.getId() :
			prevJump = self.mTimeshift_playTime - 10000
			if prevJump < self.mTimeshift_staTime :
				prevJump = self.mTimeshift_staTime + 1000
			ret = self.mDataCache.Player_JumpToIFrame( prevJump )
			LOG_TRACE('JumpRR ret[%s]'% ret )

		elif aFocusId == self.mCtrlBtnJumpFF.getId() :
			nextJump = self.mTimeshift_playTime + 10000
			if nextJump > self.mTimeshift_endTime :
				nextJump = self.mTimeshift_endTime - 1000
			ret = self.mDataCache.Player_JumpToIFrame( nextJump )
			LOG_TRACE('JumpFF ret[%s]'% ret )

		time.sleep(0.5)
		self.InitTimeShift()

		LOG_TRACE( 'Leave' )


	def InitLabelInfo(self) :
		#LOG_TRACE( 'currentChannel[%s]' % self.mCurrentChannel )

		self.mEventCopy = []

		self.UpdateLabelGUI( self.mCtrlLblMode.getId(),        '' )
		self.UpdateLabelGUI( self.mCtrlEventClock.getId(),     '' )
		self.UpdateLabelGUI( self.mCtrlProgress.getId(),        0 )
		self.UpdateLabelGUI( self.mCtrlLblTSStartTime.getId(), '' )
		self.UpdateLabelGUI( self.mCtrlLblTSEndTime.getId(),   '' )
		self.UpdateLabelGUI( self.mCtrlLblSpeed.getId(),       '' )
		self.UpdateLabelGUI( self.mCtrlImgRewind.getId(),   False )
		self.UpdateLabelGUI( self.mCtrlImgForward.getId(),  False )
		self.UpdateLabelGUI( self.mCtrlBtnCurrent.getId(),     '', E_CONTROL_LABEL )
		self.UpdateLabelGUI( self.mCtrlBtnCurrent.getId(),      0, E_CONTROL_POSY )

		self.mLocalTime = self.mDataCache.Datetime_GetLocalTime()


	@GuiLock
	def UpdateLabelGUI( self, aCtrlID = None, aValue = None, aExtra = None ) :
		LOG_TRACE( 'Enter' )

		if aCtrlID == self.mCtrlBtnVolume.getId( ) :
			self.mCtrlBtnVolume.setVisible( aValue )

		elif aCtrlID == self.mCtrlBtnStartRec.getId( ) :
			if aExtra == E_CONTROL_ENABLE :
				self.mCtrlBtnStartRec.setEnabled( aValue )
			elif aExtra == E_CONTROL_VISIBLE :
				self.mCtrlBtnStartRec.setVisible( aValue )

		elif aCtrlID == self.mCtrlBtnRewind.getId( ) :
			self.mCtrlBtnRewind.setVisible( aValue )

		elif aCtrlID == self.mCtrlBtnPlay.getId( ) :
			self.mCtrlBtnPlay.setVisible( aValue )

		elif aCtrlID == self.mCtrlBtnPause.getId( ) :
			self.mCtrlBtnPause.setVisible( aValue )

		elif aCtrlID == self.mCtrlBtnStop.getId( ) :
			self.mCtrlBtnStop.setVisible( aValue )

		elif aCtrlID == self.mCtrlBtnForward.getId( ) :
			self.mCtrlBtnForward.setVisible( aValue )

		elif aCtrlID == self.mCtrlImgRewind.getId( ) :
			self.mCtrlImgRewind.setVisible( aValue )

		elif aCtrlID == self.mCtrlImgForward.getId( ) :
			self.mCtrlImgForward.setVisible( aValue )

		elif aCtrlID == self.mCtrlEventClock.getId( ) :
			self.mCtrlEventClock.setLabel( aValue )

		elif aCtrlID == self.mCtrlProgress.getId( ) :
			self.mCtrlProgress.setPercent( aValue )

		elif aCtrlID == self.mCtrlBtnCurrent.getId( ) :
			if aExtra == E_CONTROL_LABEL:
				self.mCtrlBtnCurrent.setLabel( aValue )
			elif aExtra == E_CONTROL_POSY:
				self.mCtrlBtnCurrent.setPosition( aValue, E_DEFAULT_POSY )

		elif aCtrlID == self.mCtrlLblTSStartTime.getId( ) :
			self.mCtrlLblTSStartTime.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblTSEndTime.getId( ) :
			self.mCtrlLblTSEndTime.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblSpeed.getId( ) :
			self.mCtrlLblSpeed.setLabel( aValue )

		elif aCtrlID == self.mCtrlImgRec1.getId( ) :
			self.mWin.setProperty( 'ViewRecord1', aValue )

		elif aCtrlID == self.mCtrlImgRec2.getId( ) :
			self.mWin.setProperty( 'ViewRecord2', aValue )

		elif aCtrlID == self.mCtrlLblRec1.getId( ) :
			self.mCtrlLblRec1.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblRec2.getId( ) :
			self.mCtrlLblRec2.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblMode.getId( ) :
			self.mCtrlLblMode.setLabel( aValue )


		elif aCtrlID == self.mCtrlLblTest.getId( ) :
			self.mCtrlLblTest.setLabel( aValue )

		LOG_TRACE( 'Leave' )


	def InitTimeShift( self, loop = 0 ) :
		LOG_TRACE('Enter')

		status = None
		status = self.mDataCache.Player_GetStatus()
		LOG_TRACE('----------------------------------play[%s]'% self.mIsPlay)
		retList = []
		retList.append( status )
		LOG_TRACE( 'player_GetStatus[%s]'% ClassToList( 'convert', retList ) )

		if status :
			flag_Rewind  = False
			flag_Forward = False
			lbl_speed = ''
			lbl_timeS = ''
			lbl_timeP = ''
			lbl_timeE = ''

			#play mode
			self.mMode = status.mMode

			#test label
			#test = TimeToString(status.mPlayTimeInMs/1000, TimeFormatEnum.E_HH_MM_SS)
			#lblTest = 'current:[%s] currentToTime[%s] timeout[%s]'% (status.mPlayTimeInMs, test, self.mRepeatTimeout)
			#self.UpdateLabelGUI( self.mCtrlLblTest.getId(), lblTest )


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


			#Speed label
			self.mSpeed  = status.mSpeed

			if self.mSpeed != 0 :
				self.mRepeatTimeout = 100.0 / abs(self.mSpeed)
				if self.mRepeatTimeout < 0.1 :
					self.mRepeatTimeout = 0.1


			lbl_timeS = TimeToString( (self.mTimeshift_staTime/1000.0), TimeFormatEnum.E_HH_MM_SS)
			lbl_timeP = TimeToString( (self.mTimeshift_curTime/1000.0), TimeFormatEnum.E_HH_MM_SS)
			lbl_timeE = TimeToString( (self.mTimeshift_endTime/1000.0), TimeFormatEnum.E_HH_MM_SS)

			if lbl_timeS != '' :
				self.UpdateLabelGUI( self.mCtrlLblTSStartTime.getId(), lbl_timeS )
			if lbl_timeP != '' :
				self.UpdateLabelGUI( self.mCtrlBtnCurrent.getId(), lbl_timeP, E_CONTROL_LABEL )
			if lbl_timeE != '' :
				self.UpdateLabelGUI( self.mCtrlLblTSEndTime.getId(), lbl_timeE )


		LOG_TRACE('Leave')


	def GetNextSpeed(self, aFocusId):
		LOG_TRACE('Enter')

		LOG_TRACE( 'mSpeed[%s]'% self.mSpeed )
		ret = 0
		if aFocusId == self.mCtrlBtnRewind.getId():

			if self.mSpeed == -12800 :
				ret = -12800
			elif self.mSpeed == -6400 :
				ret = -12800
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
			elif self.mSpeed == 12800 :
				ret = 6400

		elif aFocusId == self.mCtrlBtnForward.getId():
			if self.mSpeed == -12800 :
				ret = -6400
			elif self.mSpeed == -6400 :
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
			elif self.mSpeed == 100 :
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
				ret = 12800
			elif self.mSpeed == 12800 :
				ret = 12800

		elif aFocusId == E_ONINIT :
			ret = self.mSpeed

		else:
			ret = 100 #default

		lspeed = ''
		flagFF = False
		flagRR = False
		if ret == 100 :
			lspeed = ''
		else :
			lspeed = '%sx'% ( abs(ret) / 100)

			if ret > 100 :
				flagFF = True
				flagRR = False
			else :
				flagFF = False
				flagRR = True

		self.UpdateLabelGUI( self.mCtrlImgRewind.getId(), flagRR )
		self.UpdateLabelGUI( self.mCtrlImgForward.getId(), flagFF )
		self.UpdateLabelGUI( self.mCtrlLblSpeed.getId(), lspeed )

		LOG_TRACE('Leave')
		return ret


	def GetModeValue( self ) :
		LOG_TRACE('Enter')

		labelMode = ''
		buttonHide= True
		if self.mMode == ElisEnum.E_MODE_LIVE :
			labelMode = 'LIVE'
		elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
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

		self.UpdateLabelGUI( self.mCtrlBtnStartRec.getId(), buttonHide, E_CONTROL_VISIBLE )
		LOG_TRACE('Leave')

		return labelMode


	@RunThread
	def CurrentTimeThread(self):
		LOG_TRACE( 'begin_start thread' )

		loop = 0
		while self.mEnableThread:
			#LOG_TRACE( 'repeat <<<<' )

			#update localTime
			self.mLocalTime = self.mDataCache.Datetime_GetLocalTime()
			lbl_localTime = TimeToString( self.mLocalTime, TimeFormatEnum.E_AW_HH_MM)
			self.UpdateLabelGUI( self.mCtrlEventClock.getId(), lbl_localTime )

			if self.mIsPlay != FLAG_STOP :
				self.InitTimeShift( )
				self.UpdateLocalTime( loop )

			time.sleep(self.mRepeatTimeout)
			

		LOG_TRACE( 'leave_end thread' )


	def UpdateLocalTime(self, loop = 0):
		LOG_TRACE( 'Enter' )

		try :
			lbl_timeE = ''
			lbl_timeP = ''
			curTime = 0

			#calculate current position
			totTime = self.mTimeshift_endTime - self.mTimeshift_staTime
			curTime = self.mTimeshift_curTime - self.mTimeshift_staTime

			if totTime > 0 and curTime >= 0 :
				self.mProgress_idx = (curTime / float(totTime))  * 100.0

				LOG_TRACE( 'curTime[%s] totTime[%s]'% ( curTime,totTime ) )
				LOG_TRACE( 'curTime[%s] idx[%s] endTime[%s]'% ( self.mTimeshift_curTime, self.mProgress_idx, self.mTimeshift_endTime ) )

				if self.mProgress_idx > 100 :
					self.mProgress_idx = 100
				elif self.mProgress_idx < 0 :
					self.mProgress_idx = 0

				#progress drawing
				posx = int( self.mProgress_idx * self.mProgressbarWidth / 100 )
				self.UpdateLabelGUI( self.mCtrlBtnCurrent.getId(), posx, E_CONTROL_POSY )
				self.UpdateLabelGUI( self.mCtrlProgress.getId(), self.mProgress_idx )
				LOG_TRACE( 'progress endTime[%s] idx[%s] posx[%s]'% (self.mTimeshift_endTime, self.mProgress_idx, posx) )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		LOG_TRACE( 'leave' )


	def ShowRecording( self ) :
		LOG_TRACE('Enter')

		isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )
		LOG_TRACE('isRunRecCount[%s]'% isRunRec)

		strLabelRecord1 = ''
		strLabelRecord2 = ''
		setPropertyRecord1   = 'False'
		setPropertyRecord2   = 'False'
		if isRunRec == 1 :
			setPropertyRecord1 = 'True'
			recInfo = self.mDataCache.Record_GetRunningRecordInfo( E_INDEX_FIRST_RECORDING )
			strLabelRecord1 = '%04d %s'% (int(recInfo.mChannelNo), recInfo.mChannelName)

		elif isRunRec == 2 :
			setPropertyRecord1 = 'True'
			setPropertyRecord2 = 'True'
			recInfo = self.mDataCache.Record_GetRunningRecordInfo( E_INDEX_FIRST_RECORDING )
			strLabelRecord1 = '%04d %s'% (int(recInfo.mChannelNo), recInfo.mChannelName)
			recInfo = self.mDataCache.Record_GetRunningRecordInfo( E_INDEX_SECOND_RECORDING )
			strLabelRecord2 = '%04d %s'% (int(recInfo.mChannelNo), recInfo.mChannelName)

		btnValue = False
		if isRunRec >= 1 :
			btnValue = False
		else :
			btnValue = True

		self.UpdateLabelGUI( self.mCtrlLblRec1.getId(), strLabelRecord1 )
		self.UpdateLabelGUI( self.mCtrlLblRec2.getId(), strLabelRecord2 )
		self.UpdateLabelGUI( self.mCtrlImgRec1.getId(), setPropertyRecord1 )
		self.UpdateLabelGUI( self.mCtrlImgRec2.getId(), setPropertyRecord2 )
		self.UpdateLabelGUI( self.mCtrlBtnStartRec.getId(), btnValue, E_CONTROL_ENABLE )

		return isRunRec

		LOG_TRACE('Leave')


	def RecordingStopAll( self ) :
		LOG_TRACE('Enter')

		RunningRecordCount = self.mCommander.Record_GetRunningRecorderCount()
		LOG_ERR('RunningRecordCount=%s'% RunningRecordCount )

		for i in range( int(RunningRecordCount) ) :
			recInfo = self.mDataCache.Record_GetRunningRecordInfo( i )
			if recInfo :
				#recInfo.printdebug()
				ret = self.mDataCache.Timer_StopRecordingByRecordKey( recInfo.mRecordKey )
				LOG_TRACE('record key[%s] stop[%s]'% (recInfo.mRecordKey, ret) )

		if RunningRecordCount :
			self.mDataCache.mCacheReload = True

		LOG_TRACE('Leave')
		

	def Close( self ):
		LOG_TRACE('Enter')

		self.mEventBus.Deregister( self )

		self.mEnableThread = False
		self.CurrentTimeThread().join()

		self.StopAsyncMove()
		self.StopAutomaticHide()

		LOG_TRACE('Leave')


	def SetAutomaticHide( self, aHide=True ) :
		self.mAutomaticHide = aHide


	def GetAutomaticHide( self ) :
		return self.mAutomaticHide

	
	def AsyncAutomaticHide( self ) :
		if self.mSpeed == 100 :
			xbmc.executebuiltin('xbmc.Action(previousmenu)')
			LOG_TRACE('HIDE : TimeShiftPlate')


	def RestartAutomaticHide( self ) :
		self.StopAutomaticHide()
		self.StartAutomaticHide()

	
	def StartAutomaticHide( self ) :
		prop = ElisPropertyEnum( 'Playback Banner Duration', self.mCommander )
		bannerTimeout = prop.GetProp()
		self.mAutomaticHideTimer = threading.Timer( bannerTimeout, self.AsyncAutomaticHide )
		self.mAutomaticHideTimer.start()


	def StopAutomaticHide( self ) :
		if self.mAutomaticHideTimer and self.mAutomaticHideTimer.isAlive() :
			self.mAutomaticHideTimer.cancel()
			del self.mAutomaticHideTimer
			
		self.mAutomaticHideTimer = None


	def RestartAsyncMove( self ) :
		self.StopAsyncMove( )
		self.StartAsyncMove( )


	def StartAsyncMove( self ) :
		self.mAsyncShiftTimer = threading.Timer( 0.5, self.AsyncUpdateCurrentMove ) 				
		self.mAsyncShiftTimer.start()

		self.mFlagUserMove = False
		self.mAccelator += 1
		LOG_TRACE('1================Accelator[%s]'% self.mAccelator )


	def StopAsyncMove( self ) :
		if self.mAsyncShiftTimer and self.mAsyncShiftTimer.isAlive() :
			self.mAsyncShiftTimer.cancel()
			del self.mAsyncShiftTimer

		self.mAsyncShiftTimer  = None


	#TODO : must be need timeout schedule
	def AsyncUpdateCurrentMove( self ) :
		try :
			if self.mFlagUserMove != True :
				#if self.mAccelator > 2 :
					#self.mUserMoveTime = int( self.mUserMoveTime * (1.5 ** self.mAccelator) / 10000 )

				self.mUserMoveTime = self.mUserMoveTime * self.mAccelator
				frameJump = self.mTimeshift_playTime + (self.mUserMoveTime * 1000)
				if frameJump > self.mTimeshift_endTime :
					frameJump = self.mTimeshift_endTime - 1000
				elif frameJump < self.mTimeshift_staTime :
					frameJump = self.mTimeshift_staTime + 1000

				ret = self.mDataCache.Player_JumpToIFrame( frameJump )
				LOG_TRACE('2============frameJump[%s] accelator[%s] MoveSec[%s] ret[%s]'% (frameJump,self.mAccelator,(self.mUserMoveTime/10000),ret) )

				self.mFlagUserMove = False
				self.mAccelator = 0
				self.mUserMoveTime = 0

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def KeySearch( self, aKey ) :
		LOG_TRACE( 'Enter' )

		if aKey == 0 :
			return -1

		self.mFlag_OnEvent = False

		GuiLock2(True)
		dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_TIMESHIFT_JUMP )
		dialog.SetDialogProperty( str(aKey), E_INDEX_JUMP_MAX, None )
		dialog.doModal()
		GuiLock2(False)

		self.mFlag_OnEvent = True

		isOK = dialog.IsOK()
		if isOK == E_DIALOG_STATE_YES :

			move = dialog.GetMoveToJump()
			LOG_TRACE('=========== MoveToJump[%s]'% move)
			if move :
				ret = self.mDataCache.Player_JumpToIFrame( int(move) )

		LOG_TRACE( 'Leave' )


