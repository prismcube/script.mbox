from pvr.gui.WindowImport import *
from pvr.GuiHelper import GetImageByEPGComponent, GetSelectedLongitudeString, ClassToList


FLAG_CLOCKMODE_ADMYHM  = 1
FLAG_CLOCKMODE_AHM     = 2
FLAG_CLOCKMODE_HMS     = 3
FLAG_CLOCKMODE_HHMM    = 4
FLAG_CLOCKMODE_INTTIME = 5

FLAG_TIMESHIFT_CLOSE = True
FLAG_STOP  = 0
FLAG_PLAY  = 1
FLAG_PAUSE = 2

E_DEFAULT_POSY = 0
E_PROGRESS_WIDTH_MAX = 380

E_BUTTON_GROUP_PLAYPAUSE = 450
E_BUTTON_GROUP_PLAYPLATE = 400
E_BUTTON_GROUP_INFOPLATE = 620

E_INDEX_FIRST_RECORDING = 0
E_INDEX_SECOND_RECORDING = 1
E_INDEX_JUMP_MAX = 100

NEXT_EPG		= 0
PREV_EPG 		= 1

NEXT_CHANNEL	= 0
PREV_CHANNEL	= 1
CURR_CHANNEL	= 2

CONTEXT_ACTION_VIDEO_SETTING = 1 
CONTEXT_ACTION_AUDIO_SETTING = 2

E_IMG_ICON_LOCK   = 'IconLockFocus.png'
E_IMG_ICON_ICAS   = 'IconCas.png'
E_IMG_ICON_TV     = 'tv.png'
E_IMG_ICON_RADIO  = 'icon_radio.png'

E_TAG_COLOR_WHITE = '[COLOR white]'
E_TAG_COLOR_RED   = '[COLOR red]'
E_TAG_COLOR_GREEN = '[COLOR green]'
E_TAG_COLOR_END   = '[/COLOR]'

class TimeShiftInfoPlate(BaseWindow):
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
		self.mFlag_OnEventEPGReceive = True
		self.mShowExtendInfo = False

		self.mAsyncShiftTimer = None
		self.mAutomaticHideTimer = None	
		self.mAutomaticHide = True


	def __del__(self):
		LOG_TRACE( 'destroyed TimeshiftPlate' )

		# end thread CurrentTimeThread()
		self.mEnableThread = False

	"""
	def onAction(self, aAction):
		id = aAction.getId()
		
		if id == Action.ACTION_PREVIOUS_MENU or id == Action.ACTION_PARENT_DIR:
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_NULLWINDOW )			

		elif id == 104 : #scroll up
			xbmc.executebuiltin('XBMC.ReloadSkin()')

	def SetAutomaticHide( self, aHide=True ) :
		self.mAutomaticHide = aHide

	def GetAutomaticHide( self ) :
		return self.mAutomaticHide
	"""



	def onInit(self):
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId )
		LOG_TRACE( 'winID[%d]'% self.mWinId )

		self.mCtrlImgRec1              = self.getControl( 110 )
		self.mCtrlLblRec1              = self.getControl( 111 )
		self.mCtrlImgRec2              = self.getControl( 115 )
		self.mCtrlLblRec2              = self.getControl( 116 )

		self.mCtrlProgress             = self.getControl( 201 )
		self.mCtrlBtnCurrent           = self.getControl( 202 )
		self.mCtrlLblMode              = self.getControl( 203 )
		self.mCtrlLblStatus            = self.getControl( 204 )
		self.mCtrlLblTSStartTime       = self.getControl( 221 )
		self.mCtrlLblTSEndTime         = self.getControl( 222 )

		self.mCtrlImgRewind	           = self.getControl( 231 )
		self.mCtrlImgForward           = self.getControl( 232 )
		self.mCtrlLblSpeed             = self.getControl( 233 )

		#self.mCtrlBtnStopRec          = self.getControl( 403 )
		self.mCtrlBtnRewind            = self.getControl( 404 )
		self.mCtrlBtnPlay              = self.getControl( 405 )
		self.mCtrlBtnPause             = self.getControl( 406 )
		self.mCtrlBtnStop              = self.getControl( 407 )
		self.mCtrlBtnForward           = self.getControl( 408 )
		self.mCtrlBtnJumpRR            = self.getControl( 409 )
		self.mCtrlBtnJumpFF            = self.getControl( 410 )
		self.mCtrlBtnExInfo            = self.getControl( 621 )
		self.mCtrlBtnBookMark          = self.getControl( 622 )
		self.mCtrlBtnStartRec          = self.getControl( 624 )
		self.mCtrlBtnMute              = self.getControl( 625 )
		self.mCtrlBtnSettingFormat     = self.getControl( 627 )

		#chinfo
		self.mCtrlLblChannelNumber     = self.getControl( 601 )
		self.mCtrlLblChannelName       = self.getControl( 602 )
		self.mCtrlImgServiceType       = self.getControl( 603 )
		self.mCtrlImgServiceTypeImg1   = self.getControl( 604 )
		self.mCtrlImgServiceTypeImg2   = self.getControl( 605 )
		self.mCtrlImgServiceTypeImg3   = self.getControl( 606 )
		self.mCtrlImgLocked            = self.getControl( 651 )
		self.mCtrlImgICas              = self.getControl( 652 )

		#epginfo
		self.mCtrlLblLongitudeInfo     = self.getControl( 701 )
		self.mCtrlLblEventName         = self.getControl( 703 )
		self.mCtrlLblEventStartTime    = self.getControl( 704 )
		self.mCtrlLblEventEndTime      = self.getControl( 705 )
		self.mCtrlProgressEPG          = self.getControl( 707 )
		self.mCtrlLblLocalClock        = self.getControl( 711 )
		self.mCtrlBtnPrevEpg           = self.getControl( 702 )
		self.mCtrlBtnNextEpg           = self.getControl( 706 )

		#epg description box
		self.mCtrlGropEventDescGroup   = self.getControl( 800 )
		self.mCtrlTxtBoxEventDescText1 = self.getControl( 801 )
		self.mCtrlTxtBoxEventDescText2 = self.getControl( 802 )

		#entire
		self.mCtrlGroupPlay             = self.getControl( 300 )
		self.mCtrlGroupInfo             = self.getControl(  10 )


		#test
		self.mCtrlLblTest              = self.getControl( 35 )

		self.mFlag_OnEvent = True
		self.mFlag_OnEventEPGReceive = True
		self.mTimeshift_staTime = 0.0
		self.mTimeshift_curTime = 0.0
		self.mTimeshift_endTime = 0.0
		self.mSpeed = 100	#normal
		self.mLocalTime = 0
		self.mUserMoveTime = 0
		self.mUserMoveTimeBack = 0
		self.mFlagUserMove = False
		self.mAccelator = 0
		self.mINSTime = 0
		self.mRepeatTimeout = 1
		self.mAsyncShiftTimer = None
		self.mAutomaticHideTimer = None
		self.mShowExtendInfo = False
		self.mShowGroupInfo = False
		self.mShowGroupPlay = True

		self.mImgTV    = E_IMG_ICON_TV
		self.mEventID = 0
		self.mEventCopy = None
		self.mEPGList = None
		self.mEPGListIdx = 0

		self.UpdateLabelGUI( self.mCtrlGroupInfo.getId(), False )

		self.ShowRecording( )

		self.mLocalTime = self.mDataCache.Datetime_GetLocalTime()

		self.InitLabelInfo()
		self.InitTimeShift()
		#ToDo get info : ch, epg in PVR? or TimeShift?
		self.InitInfoChannelEPG()
		
		self.UpdateONEvent( self.mEventCopy )

		label = self.GetModeValue( )
		self.UpdateLabelGUI( self.mCtrlLblMode.getId(), label )
		
		if self.mSpeed != 0 :
			self.TimeshiftAction( self.mCtrlBtnPlay.getId() )
		else :
			self.TimeshiftAction( self.mCtrlBtnPause.getId() )
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

			if self.mShowExtendInfo ==  True :
				self.ShowDialog( self.mCtrlBtnExInfo.getId(), False )
				return

			if not self.mShowGroupPlay :
				self.mShowGroupPlay = True
				self.UpdateLabelGUI( self.mCtrlGroupPlay.getId(), True )
				self.UpdateLabelGUI( self.mCtrlGroupInfo.getId(), False )
				self.setFocusId( E_BUTTON_GROUP_PLAYPLATE )

				self.RestartAutomaticHide()
				return

			self.Close()
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

			if self.mFocusId == self.mCtrlBtnPrevEpg.getId():
				self.EPGNavigation( PREV_EPG )


			if self.mFocusId >= self.mCtrlBtnExInfo.getId() and self.mFocusId <= self.mCtrlBtnSettingFormat.getId() or \
			   self.mFocusId == self.mCtrlBtnPrevEpg.getId() or self.mFocusId == self.mCtrlBtnNextEpg.getId() :
				if self.mAutomaticHideTimer :
					self.StopAutomaticHide()

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

			if self.mFocusId == self.mCtrlBtnNextEpg.getId():
				self.EPGNavigation( NEXT_EPG )

			if self.mFocusId >= self.mCtrlBtnExInfo.getId() and self.mFocusId <= self.mCtrlBtnSettingFormat.getId() or \
			   self.mFocusId == self.mCtrlBtnPrevEpg.getId() or self.mFocusId == self.mCtrlBtnNextEpg.getId() :
				if self.mAutomaticHideTimer :
					self.StopAutomaticHide()

		elif id == Action.ACTION_PAGE_UP:
			LOG_TRACE('key up')
			self.ChannelTune( NEXT_CHANNEL )


		elif id == Action.ACTION_PAGE_DOWN:
			LOG_TRACE('key down')
			self.ChannelTune( PREV_CHANNEL )

			
		elif id == Action.ACTION_CONTEXT_MENU:
			self.StopAutomaticHide()

			if self.mShowGroupPlay :
				self.mShowGroupPlay = False
				self.UpdateLabelGUI( self.mCtrlGroupPlay.getId(), False )
				self.UpdateLabelGUI( self.mCtrlGroupInfo.getId(), True )
				self.setFocusId( E_BUTTON_GROUP_INFOPLATE )
			else :
				self.onClick( self.mCtrlBtnExInfo.getId() )


		elif id == Action.ACTION_STOP :
			self.onClick( self.mCtrlBtnStop.getId() )

		#test
		elif id == 104 : #scroll up
			#self.ShowRecording()
			#self.UpdateLabelGUI( self.mCtrlImgRec1.getId(), True )
			xbmc.executebuiltin('XBMC.ReloadSkin()')

		elif id == 105 :
			#self.UpdateLabelGUI( self.mCtrlImgRec1.getId(), False )
			pass


	def onClick(self, aControlId):
		LOG_TRACE( 'control %d' % aControlId )

		if aControlId >= self.mCtrlBtnRewind.getId() and aControlId <= self.mCtrlBtnJumpFF.getId() :

			if aControlId == self.mCtrlBtnPlay.getId() :
				#self.mAutomaticHide = True
				self.RestartAutomaticHide()
			else :
				#self.mAutomaticHide = False
				self.StopAutomaticHide()


			self.TimeshiftAction( aControlId )


		elif aControlId == self.mCtrlBtnMute.getId():
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

		elif aControlId == self.mCtrlBtnExInfo.getId():
			if self.mShowExtendInfo :
				self.RestartAsyncMove()
			else :
				self.StopAutomaticHide()

			self.ShowDialog( aControlId, not self.mShowExtendInfo )

		elif aControlId == self.mCtrlBtnBookMark.getId():
			self.ShowDialog( aControlId )

		elif aControlId == self.mCtrlBtnSettingFormat.getId():
			self.ShowDialog( aControlId )


	def onFocus(self, aControlId):
		#LOG_TRACE( 'control %d' % controlId )
		pass


	@GuiLock
	def onEvent(self, aEvent):
		LOG_TRACE( 'Enter' )

		if self.mWinId == xbmcgui.getCurrentWindowId():

			if self.mFlag_OnEvent != True :
				LOG_TRACE('ignore event, mFlag_OnEvent[%s]'% self.mFlag_OnEvent)
				return -1

			if aEvent.getName() == ElisEventPlaybackEOF.getName() :
				#aEvent.printdebug()
				LOG_TRACE( 'mType[%d]' %(aEvent.mType ) )

				if aEvent.mType == ElisEnum.E_EOF_START :
					#self.TimeshiftAction( self.mCtrlBtnPlay.getId() )
					LOG_TRACE( 'EventRecv EOF_START' )

				elif aEvent.mType == ElisEnum.E_EOF_END :
					#self.TimeshiftAction( self.mCtrlBtnStop.getId() )
					LOG_TRACE( 'EventRecv EOF_STOP' )

			elif aEvent.getName() == ElisEventCurrentEITReceived.getName() :
				if self.mFlag_OnEventEPGReceive :
					self.UpdateEPGList( aEvent )

			elif aEvent.getName() == ElisEventRecordingStarted.getName() or \
				 aEvent.getName() == ElisEventRecordingStopped.getName() :
				time.sleep(1.5)
				self.ShowRecording()
				self.mDataCache.mCacheReload = True
				LOG_TRACE('Receive Event[%s]'% aEvent.getName() )

		else:
			LOG_TRACE( 'TimeshiftPlate winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId()) )

		LOG_TRACE( 'Leave' )


	def TimeshiftAction(self, aFocusId, aClose = None):
		LOG_TRACE( 'Enter' )

		ret = False
		clickButton = ''

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

				clickButton = 'Play'

		elif aFocusId == self.mCtrlBtnPause.getId() :
			if self.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.mDataCache.Player_StartTimeshiftPlayback( ElisEnum.E_PLAYER_TIMESHIFT_START_PAUSE, 0 )

			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				ret = self.mDataCache.Player_Pause()
			elif self.mMode == ElisEnum.E_MODE_PVR:
				ret = self.mDataCache.Player_Pause()

			LOG_TRACE( 'play_pause() ret[%s]'% ret )
			if ret :
				self.mIsPlay = FLAG_PLAY

				# toggle
				self.UpdateLabelGUI( self.mCtrlBtnPlay.getId(), True )
				self.UpdateLabelGUI( self.mCtrlBtnPause.getId(), False )
				self.setFocusId( E_BUTTON_GROUP_PLAYPAUSE )
				clickButton = 'Pause'

		elif aFocusId == self.mCtrlBtnStop.getId() :
			third = 3
			gobackID = WinMgr.WIN_ID_NULLWINDOW
			while third :
				if self.mMode == ElisEnum.E_MODE_LIVE :
					ret = self.mDataCache.Player_Stop()
					gobackID = WinMgr.WIN_ID_LIVE_PLATE

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
				if nextSpeed == 100 :
					if self.mSpeed == 0 : clickButton = 'Pause'
					else : clickButton = 'Play'
				elif nextSpeed < 100 : clickButton = 'Rewind'
				elif nextSpeed > 100 : clickButton = 'Forward'


			#resume by toggle
			if self.mIsPlay == FLAG_PLAY :
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
				if nextSpeed == 100 :
					if self.mSpeed == 0 : clickButton = 'Pause'
					else : clickButton = 'Play'
				elif nextSpeed < 100 : clickButton = 'Rewind'
				elif nextSpeed > 100 : clickButton = 'Forward'

			#resume by toggle
			if self.mIsPlay == FLAG_PLAY :
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
		self.UpdateLabelGUI( self.mCtrlLblStatus.getId(), clickButton.upper() )
		self.InitTimeShift()

		LOG_TRACE( 'Leave' )


	def InitLabelInfo(self) :
		#LOG_TRACE( 'currentChannel[%s]' % self.mCurrentChannel )

		self.UpdateLabelGUI( self.mCtrlLblMode.getId(),        '' )
		self.UpdateLabelGUI( self.mCtrlLblLocalClock.getId(),     '' )
		self.UpdateLabelGUI( self.mCtrlProgress.getId(),        0 )
		self.UpdateLabelGUI( self.mCtrlLblTSStartTime.getId(), '' )
		self.UpdateLabelGUI( self.mCtrlLblTSEndTime.getId(),   '' )
		self.UpdateLabelGUI( self.mCtrlLblSpeed.getId(),       '' )
		self.UpdateLabelGUI( self.mCtrlImgRewind.getId(),   False )
		self.UpdateLabelGUI( self.mCtrlImgForward.getId(),  False )
		self.UpdateLabelGUI( self.mCtrlBtnCurrent.getId(),     '', 'lbl' )
		self.UpdateLabelGUI( self.mCtrlBtnCurrent.getId(),      0, 'pos' )

		#Chnnel, EPG
		self.mEventCopy = None
		self.UpdateLabelGUI( self.mCtrlLblChannelNumber.getId(),      '' )
		self.UpdateLabelGUI( self.mCtrlLblChannelName.getId(),        '' )
		self.UpdateLabelGUI( self.mCtrlTxtBoxEventDescText1.getId(),  '' )
		self.UpdateLabelGUI( self.mCtrlTxtBoxEventDescText2.getId(),  '' )
		self.UpdateLabelGUI( self.mCtrlGropEventDescGroup.getId(), False )
		self.UpdateLabelGUI( self.mCtrlLblLongitudeInfo.getId(),      '' )
		self.UpdateLabelGUI( self.mCtrlProgressEPG.getId(),            0 )

		self.UpdateLabelGUI( self.mCtrlLblEventName.getId(),          '' )
		self.UpdateLabelGUI( self.mCtrlLblEventStartTime.getId(),     '' )
		self.UpdateLabelGUI( self.mCtrlLblEventEndTime.getId(),       '' )
		self.UpdateLabelGUI( self.mCtrlImgLocked.getId(),             '' )
		self.UpdateLabelGUI( self.mCtrlImgICas.getId(),               '' )
		self.UpdateLabelGUI( self.mCtrlImgServiceType.getId(),        '' )
		self.UpdateLabelGUI( self.mCtrlImgServiceTypeImg1.getId(),    '' )
		self.UpdateLabelGUI( self.mCtrlImgServiceTypeImg2.getId(),    '' )
		self.UpdateLabelGUI( self.mCtrlImgServiceTypeImg3.getId(),    '' )

		self.mLocalTime = self.mDataCache.Datetime_GetLocalTime()

	#@GuiLock
	def UpdateLabelGUI( self, aCtrlID = None, aValue = None, aExtra = None ) :
		LOG_TRACE( 'Enter id[%s] value[%s]'% (aCtrlID, aValue) )

		if aCtrlID == self.mCtrlBtnMute.getId( ) :
			self.mCtrlBtnMute.setVisible( aValue )

		elif aCtrlID == self.mCtrlBtnStartRec.getId( ) :
			if aExtra == 'enable' :
				self.mCtrlBtnStartRec.setEnabled( aValue )
			elif aExtra == 'visible' :
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

		elif aCtrlID == self.mCtrlLblLocalClock.getId( ) :
			self.mCtrlLblLocalClock.setLabel( aValue )

		elif aCtrlID == self.mCtrlProgress.getId( ) :
			self.mCtrlProgress.setPercent( aValue )

		elif aCtrlID == self.mCtrlBtnCurrent.getId( ) :
			if aExtra == 'lbl':
				self.mCtrlBtnCurrent.setLabel( aValue )
			elif aExtra == 'pos':
				self.mCtrlBtnCurrent.setPosition( aValue, E_DEFAULT_POSY )

		elif aCtrlID == self.mCtrlLblTSStartTime.getId( ) :
			self.mCtrlLblTSStartTime.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblTSEndTime.getId( ) :
			self.mCtrlLblTSEndTime.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblSpeed.getId( ) :
			self.mCtrlLblSpeed.setLabel( aValue )

		elif aCtrlID == self.mCtrlImgRec1.getId( ) :
			self.mCtrlImgRec1.setVisible( aValue )

		elif aCtrlID == self.mCtrlImgRec2.getId( ) :
			self.mCtrlImgRec2.setVisible( aValue )

		elif aCtrlID == self.mCtrlLblRec1.getId( ) :
			self.mCtrlLblRec1.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblRec2.getId( ) :
			self.mCtrlLblRec2.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblMode.getId( ) :
			self.mCtrlLblMode.setLabel( aValue )

		#----------- ch, epg ctrl -----------------
		elif aCtrlID == self.mCtrlLblChannelNumber.getId( ) :
			self.mCtrlLblChannelNumber.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblChannelName.getId( ) :
			self.mCtrlLblChannelName.setLabel( aValue )

		elif aCtrlID == self.mCtrlTxtBoxEventDescText1.getId( ) :
			self.mCtrlTxtBoxEventDescText1.setText( aValue )

		elif aCtrlID == self.mCtrlTxtBoxEventDescText2.getId( ) :
			self.mCtrlTxtBoxEventDescText2.setText( aValue )

		elif aCtrlID == self.mCtrlGropEventDescGroup.getId( ) :
			self.mCtrlGropEventDescGroup.setVisible( aValue )

		elif aCtrlID == self.mCtrlLblLongitudeInfo.getId( ) :
			self.mCtrlLblLongitudeInfo.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblEventName.getId( ) :
			self.mCtrlLblEventName.setLabel( aValue )

		elif aCtrlID == self.mCtrlProgressEPG.getId( ) :
			self.mCtrlProgress.setPercent( aValue )

		elif aCtrlID == self.mCtrlLblEventStartTime.getId( ) :
			self.mCtrlLblEventStartTime.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblEventEndTime.getId( ) :
			self.mCtrlLblEventEndTime.setLabel( aValue )

		elif aCtrlID == self.mCtrlImgLocked.getId( ) :
			self.mCtrlImgLocked.setImage( aValue )

		elif aCtrlID == self.mCtrlImgICas.getId( ) :
			self.mCtrlImgICas.setImage( aValue )

		elif aCtrlID == self.mCtrlImgServiceType.getId( ) :
			self.mCtrlImgServiceType.setImage( aValue )

		elif aCtrlID == self.mCtrlImgServiceTypeImg1.getId( ) :
			self.mCtrlImgServiceTypeImg1.setImage( aValue )

		elif aCtrlID == self.mCtrlImgServiceTypeImg2.getId( ) :
			self.mCtrlImgServiceTypeImg2.setImage( aValue )

		elif aCtrlID == self.mCtrlImgServiceTypeImg3.getId( ) :
			self.mCtrlImgServiceTypeImg3.setImage( aValue )

		elif aCtrlID == self.mCtrlBtnPrevEpg.getId( ) :
			if aExtra == 'enable' :
				self.mCtrlBtnPrevEpg.setEnabled( aValue )
			elif aExtra == 'visible' :
				self.mCtrlBtnPrevEpg.setVisible( aValue )

		elif aCtrlID == self.mCtrlBtnNextEpg.getId( ) :
			if aExtra == 'enable' :
				self.mCtrlBtnNextEpg.setEnabled( aValue )
			elif aExtra == 'visible' :
				self.mCtrlBtnNextEpg.setVisible( aValue )

		elif aCtrlID == self.mCtrlGroupInfo.getId( ) :
			self.mCtrlGroupInfo.setVisible( aValue )

		elif aCtrlID == self.mCtrlGroupPlay.getId( ) :
			self.mCtrlGroupPlay.setVisible( aValue )

		elif aCtrlID == self.mCtrlLblStatus.getId( ) :
			self.mCtrlLblStatus.setLabel( aValue )



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


			#progress info
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
				self.UpdateLabelGUI( self.mCtrlBtnCurrent.getId(), lbl_timeP, 'lbl' )
			if lbl_timeE != '' :
				self.UpdateLabelGUI( self.mCtrlLblTSEndTime.getId(), lbl_timeE )


		LOG_TRACE('Leave')

	def GetNextSpeed(self, aFocusId):
		LOG_TRACE('Enter')

		LOG_TRACE( 'mSpeed[%s]'% self.mSpeed )
		nextSpeed = 0
		if aFocusId == self.mCtrlBtnRewind.getId():

			if self.mSpeed == -12800 :
				nextSpeed = -12800
			elif self.mSpeed == -6400 :
				nextSpeed = -12800
			elif self.mSpeed == -3200 :
				nextSpeed = -6400
			elif self.mSpeed == -1600 :
				nextSpeed = -3200
			elif self.mSpeed == -800 :
				nextSpeed = -1600
			elif self.mSpeed == -400 :
				nextSpeed = -800
			elif self.mSpeed == -200 :
				nextSpeed = -400
			elif self.mSpeed == 100 :
				nextSpeed = -200
			elif self.mSpeed == 120 :
				nextSpeed = 100
			elif self.mSpeed == 160 :
				nextSpeed = 120
			elif self.mSpeed == 200 :
				nextSpeed = 100 #160
			elif self.mSpeed == 400 :
				nextSpeed = 200
			elif self.mSpeed == 800 :
				nextSpeed = 400
			elif self.mSpeed == 1600 :
				nextSpeed = 800
			elif self.mSpeed == 3200 :
				nextSpeed = 1600
			elif self.mSpeed == 6400 :
				nextSpeed = 3200
			elif self.mSpeed == 12800 :
				nextSpeed = 6400

		elif aFocusId == self.mCtrlBtnForward.getId():
			if self.mSpeed == -12800 :
				nextSpeed = -6400
			elif self.mSpeed == -6400 :
				nextSpeed = -3200
			elif self.mSpeed == -3200 :
				nextSpeed = -1600
			elif self.mSpeed == -1600 :
				nextSpeed = -800
			elif self.mSpeed == -800 :
				nextSpeed = -400
			elif self.mSpeed == -400 :
				nextSpeed = -200
			elif self.mSpeed == -200 :
				nextSpeed = 100
			elif self.mSpeed == 100 :
				nextSpeed = 200 #120
			elif self.mSpeed == 120 :
				nextSpeed = 160
			elif self.mSpeed == 160 :
				nextSpeed = 200
			elif self.mSpeed == 200 :
				nextSpeed = 400
			elif self.mSpeed == 400 :
				nextSpeed = 800
			elif self.mSpeed == 800 :
				nextSpeed = 1600
			elif self.mSpeed == 1600 :
				nextSpeed = 3200
			elif self.mSpeed == 3200 :
				nextSpeed = 6400
			elif self.mSpeed == 6400 :
				nextSpeed = 12800
			elif self.mSpeed == 12800 :
				nextSpeed = 12800
		else:
			nextSpeed = 100 #default

		labelSpeed = ''
		flagFF = False
		flagRR = False
		if nextSpeed != 100 :
			labelSpeed = '%sx'% ( abs(nextSpeed) / 100)
			if nextSpeed > 100 :
				flagFF = True
				flagRR = False
			else :
				flagFF = False
				flagRR = True

		self.UpdateLabelGUI( self.mCtrlImgRewind.getId(), flagRR )
		self.UpdateLabelGUI( self.mCtrlImgForward.getId(), flagFF )
		self.UpdateLabelGUI( self.mCtrlLblSpeed.getId(), labelSpeed )

		LOG_TRACE('Leave')
		return nextSpeed

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

		self.UpdateLabelGUI( self.mCtrlBtnStartRec.getId(), buttonHide, 'visible' )
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
			self.UpdateLabelGUI( self.mCtrlLblLocalClock.getId(), lbl_localTime )

			if not self.mEPGList :
				loop = (int(self.mLocalTime) / 1000) % 10
				if loop == 0 :
					self.GetEPGList()
					self.EPGListMove( )

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
				LOG_TRACE( 'curTime[%s] idx[%s] endTime[%s]'% ( self.mTimeshift_staTime, self.mProgress_idx, self.mTimeshift_endTime ) )

				if self.mProgress_idx > 100 :
					self.mProgress_idx = 100
				elif self.mProgress_idx < 0 :
					self.mProgress_idx = 0

				#progress drawing
				posx = int( self.mProgress_idx * self.mProgressbarWidth / 100 )
				self.UpdateLabelGUI( self.mCtrlBtnCurrent.getId(), posx, 'pos' )
				self.UpdateLabelGUI( self.mCtrlProgress.getId(), self.mProgress_idx )
				LOG_TRACE( 'progress endTime[%s] idx[%s] posx[%s]'% (self.mTimeshift_endTime, self.mProgress_idx, posx) )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		LOG_TRACE( 'leave' )


	def updateServiceType(self, aTvType):
		LOG_TRACE( 'serviceType[%s]' % aTvType )

	def ShowRecording( self ) :
		LOG_TRACE('Enter')

		isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )
		LOG_TRACE('isRunRecCount[%s]'% isRunRec)

		recLabel1 = ''
		recLabel2 = ''
		recImg1   = False
		recImg2   = False
		if isRunRec == 1 :
			recImg1 = True
			recInfo = self.mDataCache.Record_GetRunningRecordInfo( E_INDEX_FIRST_RECORDING )
			recLabel1 = '%04d %s'% (int(recInfo.mChannelNo), recInfo.mChannelName)

		elif isRunRec == 2 :
			recImg1 = True
			recImg2 = True
			recInfo = self.mDataCache.Record_GetRunningRecordInfo( E_INDEX_FIRST_RECORDING )
			recLabel1 = '%04d %s'% (int(recInfo.mChannelNo), recInfo.mChannelName)
			recInfo = self.mDataCache.Record_GetRunningRecordInfo( E_INDEX_SECOND_RECORDING )
			recLabel2 = '%04d %s'% (int(recInfo.mChannelNo), recInfo.mChannelName)

		btnValue = False
		if isRunRec >= 1 :
			btnValue = False
		else :
			btnValue = True

		self.UpdateLabelGUI( self.mCtrlLblRec1.getId(), recLabel1 )
		self.UpdateLabelGUI( self.mCtrlImgRec1.getId(), recImg1 )
		self.UpdateLabelGUI( self.mCtrlLblRec2.getId(), recLabel2 )
		self.UpdateLabelGUI( self.mCtrlImgRec2.getId(), recImg2 )
		self.UpdateLabelGUI( self.mCtrlBtnStartRec.getId(), btnValue, 'enable' )

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


	#----------------------------- Channel, EPG ---------------------------
	def ChannelTune(self, aDir):
		LOG_TRACE( 'Enter' )

		if self.mDataCache.mStatusIsArchive :
			LOG_TRACE('Archive playing now')

		else:
			isStop = False
			if aDir == PREV_CHANNEL:
				prevChannel = None
				prevChannel = self.mDataCache.Channel_GetPrev( self.mDataCache.Channel_GetCurrent( ) ) #self.mCommander.Channel_GetPrev( )
				if prevChannel :
					self.mDataCache.Channel_SetCurrent( prevChannel.mNumber, prevChannel.mServiceType )			
					isStop = True

			elif aDir == NEXT_CHANNEL:
				nextChannel = None
				nextChannel = self.mDataCache.Channel_GetNext( self.mDataCache.Channel_GetCurrent( ) )
				if nextChannel :
					self.mDataCache.Channel_SetCurrent( nextChannel.mNumber, nextChannel.mServiceType )
					isStop = True

			if isStop :
				self.onClick( self.mCtrlBtnStop.getId() )

		LOG_TRACE('Leave')


	def EPGListMove( self ) :
		LOG_TRACE( 'Enter' )

		try :
			LOG_TRACE('ch[%s] len[%s] idx[%s]'% (self.mCurrentChannel.mNumber, len(self.mEPGList),self.mEPGListIdx) )
			iEPG = self.mEPGList[self.mEPGListIdx]

			if iEPG :
				self.mEventCopy = iEPG
				self.UpdateONEvent( iEPG )

				retList = []
				retList.append( iEPG )
				LOG_TRACE( 'idx[%s] epg[%s]'% (self.mEPGListIdx, ClassToList( 'convert', retList )) )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		LOG_TRACE( 'Leave' )


	def EPGNavigation(self, aDir ):
		LOG_TRACE('Enter')

		if self.mEPGList :
			lastIdx = len(self.mEPGList) - 1
			if aDir == NEXT_EPG:
				if self.mEPGListIdx+1 > lastIdx :
					self.mEPGListIdx = lastIdx
				else :
					self.mEPGListIdx += 1


			elif aDir == PREV_EPG:
				if self.mEPGListIdx-1 < 0 :
					self.mEPGListIdx = 0
				else :
					self.mEPGListIdx -= 1

			self.EPGListMove()

		LOG_TRACE('Leave')


	def GetEPGList( self ) :
		LOG_TRACE( 'Enter' )

		#stop onEvent
		self.mFlag_OnEvent = False

		try :
			ch = self.mCurrentChannel

			if self.mEventCopy == None :
				if not ch :
					LOG_TRACE('No Channels')
					return

				iEPG = None
				iEPG = self.mDataCache.Epgevent_GetCurrent( ch.mSid, ch.mTsid, ch.mOnid, True )
				if iEPG and iEPG.mEventName != 'No Name':
					self.mEventCopy = iEPG

				else :
					#receive onEvent
					self.mFlag_OnEvent = True
					return -1

			if ch :
				self.mEPGList = None

				#Live EPG
				gmtFrom  = self.mEventCopy.mStartTime
				#gmtFrom  = self.mTimeshift_curTime
				gmtUntil = gmtFrom + ( 3600 * 24 * 7 )
				maxCount = 100
				iEPGList = None
				iEPGList = self.mDataCache.Epgevent_GetListByChannel( ch.mSid, ch.mTsid, ch.mOnid, gmtFrom, gmtUntil, maxCount, True )
				time.sleep(0.05)
				LOG_TRACE('==================')
				LOG_TRACE('iEPGList[%s] ch[%d] sid[%d] tid[%d] oid[%d] from[%s] until[%s]'% (iEPGList, ch.mNumber, ch.mSid, ch.mTsid, ch.mOnid, time.asctime(time.localtime(gmtFrom)), time.asctime(time.localtime(gmtUntil))) )
				#LOG_TRACE('=============epg len[%s] list[%s]'% (len(ret),ClassToList('convert', ret )) )
				if iEPGList :
					self.mEPGList = iEPGList
					self.mFlag_ChannelChanged = False
				else :
					LOG_TRACE('EPGList is None\nLeave')
					#receive onEvent
					self.mFlag_OnEvent = True
					return -1

				LOG_TRACE('event[%s]'% self.mEventCopy )
				retList=[]
				retList.append(self.mEventCopy)
				LOG_TRACE('==========[%s]'% ClassToList('convert', retList) )
				LOG_TRACE('EPGList len[%s] [%s]'% (len(self.mEPGList), ClassToList('convert', self.mEPGList)) )
				LOG_TRACE('onEvent[%s] list[%s]'% (self.mEventCopy, self.mEPGList))
				idx = 0
				self.mEPGListIdx = -1
				for item in self.mEPGList :
					#LOG_TRACE('idx[%s] item[%s]'% (idx, item) )
					if 	item.mEventId == self.mEventCopy.mEventId and \
						item.mSid == self.mEventCopy.mSid and \
						item.mTsid == self.mEventCopy.mTsid and \
						item.mOnid == self.mEventCopy.mOnid :

						self.mEPGListIdx = idx

						retList=[]
						retList.append(item)
						LOG_TRACE('SAME NOW EPG idx[%s] [%s]'% (idx, ClassToList('convert', retList)) )

						break

					idx += 1

				#search not current epg
				if self.mEPGListIdx == -1 : 
					self.mEPGListIdx = 0
					LOG_TRACE('SEARCH NOT CURRENT EPG, idx=0')

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		#receive onEvent
		self.mFlag_OnEvent = True

		LOG_TRACE( 'Leave' )

	def UpdateONEvent(self, aEvent = None):
		LOG_TRACE( 'Enter' )

		ch = self.mCurrentChannel

		if ch :
			try :
				#satellite
				label = ''
				if self.mMode == ElisEnum.E_MODE_PVR :
					label = 'Archive'
				else :
					satellite = self.mDataCache.Satellite_GetByChannelNumber( ch.mNumber, -1, True )
					if satellite :
						label = GetSelectedLongitudeString( satellite.mLongitude, satellite.mName )
				self.UpdateLabelGUI( self.mCtrlLblLongitudeInfo.getId(), label )

				#lock,cas
				if ch.mLocked :
					self.UpdateLabelGUI( self.mCtrlImgLocked.getId(), E_IMG_ICON_LOCK )

				if ch.mIsCA :
					self.UpdateLabelGUI( self.mCtrlImgICas.getId(), E_IMG_ICON_ICAS )

				#type
				imgfile = ''
				if ch.mServiceType == ElisEnum.E_SERVICE_TYPE_TV: 		imgfile = E_IMG_ICON_TV
				elif ch.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO:	imgfile = E_IMG_ICON_RADIO
				elif ch.mServiceType == ElisEnum.E_SERVICE_TYPE_DATA:	pass
				else:
					LOG_TRACE( 'unknown ElisEnum tvType[%s]'% ch.mServiceType )
				self.UpdateLabelGUI( self.mCtrlImgServiceType.getId(), imgfile )

			except Exception, e :
				LOG_TRACE( 'Error exception[%s]'% e )


		if aEvent :
			try :
				#epg name
				self.UpdateLabelGUI( self.mCtrlLblEventName.getId(), aEvent.mEventName )

				label = TimeToString( aEvent.mStartTime, TimeFormatEnum.E_HH_MM )
				self.UpdateLabelGUI( self.mCtrlLblEventStartTime.getId(), label )
				label = TimeToString( aEvent.mStartTime + aEvent.mDuration, TimeFormatEnum.E_HH_MM )
				self.UpdateLabelGUI( self.mCtrlLblEventEndTime.getId(),   label )

				LOG_TRACE( 'mStartTime[%s] mDuration[%s]'% (aEvent.mStartTime, aEvent.mDuration) )


				#component
				imglist = []
				img = GetImageByEPGComponent( aEvent, ElisEnum.E_HasSubtitles )
				if img:
					imglist.append(img)
				img = GetImageByEPGComponent( aEvent, ElisEnum.E_HasDolbyDigital )
				if img:
					imglist.append(img)
				img = GetImageByEPGComponent( aEvent, ElisEnum.E_HasHDVideo )
				if img:
					imglist.append(img)

				if len(imglist) == 1:
					self.UpdateLabelGUI( self.mCtrlImgServiceTypeImg1.getId(), imglist[0] )
				elif len(imglist) == 2:
					self.UpdateLabelGUI( self.mCtrlImgServiceTypeImg1.getId(), imglist[0] )
					self.UpdateLabelGUI( self.mCtrlImgServiceTypeImg2.getId(), imglist[1] )
				elif len(imglist) == 3:
					self.UpdateLabelGUI( self.mCtrlImgServiceTypeImg1.getId(), imglist[0] )
					self.UpdateLabelGUI( self.mCtrlImgServiceTypeImg2.getId(), imglist[1] )
					self.UpdateLabelGUI( self.mCtrlImgServiceTypeImg3.getId(), imglist[2] )
				else:
					self.UpdateLabelGUI( self.mCtrlImgServiceTypeImg1.getId(), '' )
					self.UpdateLabelGUI( self.mCtrlImgServiceTypeImg2.getId(), '' )
					self.UpdateLabelGUI( self.mCtrlImgServiceTypeImg3.getId(), '' )


			except Exception, e:
				LOG_TRACE( 'Error exception[%s]'% e )

		else:
			LOG_TRACE( 'aEvent null' )

		LOG_TRACE( 'Leave' )


	def UpdateEPGList(self, aEvent):
		#LOG_TRACE( 'Enter' )

		ch = self.mCurrentChannel	

		if ch == None :
			LOG_TRACE('ignore event, currentChannel None, [%s]'% ch)
			return -1
		
		if ch.mSid != aEvent.mSid or ch.mTsid != aEvent.mTsid or ch.mOnid != aEvent.mOnid :
			#LOG_TRACE('ignore event, same event')
			return -1

		LOG_TRACE( 'eventid:new[%d] old[%d]' %(aEvent.mEventId, self.mEventID ) )
		#aEvent.printdebug()

		if aEvent.mEventId != self.mEventID :
			iEPG = None
			iEPG = self.mDataCache.Epgevent_GetCurrent( ch.mSid, ch.mTsid, ch.mTsid, ch.mOnid )
			if iEPG and iEPG.mEventName != 'No Name':
				LOG_TRACE('-----------------------')
				#iEPG.printdebug()

				if not self.mEventCopy or \
				iEPG.mEventId != self.mEventCopy.mEventId or \
				iEPG.mSid != self.mEventCopy.mSid or \
				iEPG.mTsid != self.mEventCopy.mTsid or \
				iEPG.mOnid != self.mEventCopy.mOnid :
					LOG_TRACE('epg DIFFER, id[%s]'% iEPG.mEventId)
					self.mEventID = aEvent.mEventId
					self.mEventCopy = iEPG
					#update label
					self.UpdateONEvent( iEPG )

					#check : new event?
					if self.mEPGList :
						#1. aready exist? search in EPGList
						idx = 0
						self.mEPGListIdx = -1
						for item in self.mEPGList :
							if 	item.mEventId == self.mEventCopy.mEventId and \
								item.mSid == self.mEventCopy.mSid and \
								item.mTsid == self.mEventCopy.mTsid and \
								item.mOnid == self.mEventCopy.mOnid :

								self.mEPGListIdx = idx
								LOG_TRACE('Received ONEvent : EPGList idx moved(current idx)')

								iEPGList=[]
								iEPGList.append(item)
								LOG_TRACE('1.Aready Exist: NOW EPG idx[%s] [%s]'% (idx, ClassToList('convert', iEPGList)) )
								break

							idx += 1

						#2. new epg, append to EPGList
						if self.mEPGListIdx == -1 :
							LOG_TRACE('new EPG received, not exist in EPGList')
							oldLen = len(self.mEPGList)
							idx = 0
							for idx in range(len(self.mEPGList)) :
								if self.mEventCopy.mStartTime < self.mEPGList[idx].mStartTime :
									break

							self.mEPGListIdx = idx
							self.mEPGList = self.mEPGList[:idx]+[self.mEventCopy]+self.mEPGList[idx:]
							LOG_TRACE('append new idx[%s], epgTotal:oldlen[%s] newlen[%s]'% (idx, oldLen, len(self.mEPGList)) )
							LOG_TRACE('list[%s]'% ClassToList('convert',self.mEPGList) )


		#LOG_TRACE( 'Leave' )
		
	def ShowDialog( self, aFocusId, aVisible = False ) :
		LOG_TRACE( 'Enter' )

		head = ''
		line1= ''
		if aFocusId == self.mCtrlBtnBookMark.getId( ) :
			head = 'BookMark'
			line1= 'test'

			GuiLock2(True)
			dialog = xbmcgui.Dialog().ok( head, line1 )
			GuiLock2(False)

		elif aFocusId == self.mCtrlBtnExInfo.getId() :
			if aVisible == True :
				LOG_TRACE('')
				if self.mEventCopy :
					self.UpdateLabelGUI( self.mCtrlTxtBoxEventDescText1.getId(), self.mEventCopy.mEventName )
					self.UpdateLabelGUI( self.mCtrlTxtBoxEventDescText2.getId(), self.mEventCopy.mEventDescription )
					self.UpdateLabelGUI( self.mCtrlGropEventDescGroup.getId(),  True )
					
				else:
					LOG_TRACE( 'event is None' )
					self.UpdateLabelGUI( self.mCtrlTxtBoxEventDescText1.getId(), '' )
					self.UpdateLabelGUI( self.mCtrlTxtBoxEventDescText2.getId(), '' )
					self.UpdateLabelGUI( self.mCtrlGropEventDescGroup.getId(),  True )

			else :
				LOG_TRACE('')		
				self.mCtrlTxtBoxEventDescText1.reset()
				self.mCtrlTxtBoxEventDescText2.reset()
				self.UpdateLabelGUI( self.mCtrlGropEventDescGroup.getId(),  False )

			self.mShowExtendInfo = aVisible


		elif aFocusId == self.mCtrlBtnSettingFormat.getId() :
			context = []
			context.append( ContextItem( 'Video Format', CONTEXT_ACTION_VIDEO_SETTING ) )
			context.append( ContextItem( 'Audio Track',  CONTEXT_ACTION_AUDIO_SETTING ) )

			GuiLock2( True )
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context )
			dialog.doModal( )
			GuiLock2( False )

			selectAction = dialog.GetSelectedAction( )
			if selectAction == -1 :
				LOG_TRACE('CANCEL by context dialog')
				return

			if selectAction == CONTEXT_ACTION_AUDIO_SETTING :
				GuiLock2( True )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SET_LIVE_PLATE )
				dialog.SetValue( selectAction )
	 			dialog.doModal( )
	 			GuiLock2( False )

	 		else :
				getCount = self.mDataCache.Audiotrack_GetCount( )
				selectIdx= self.mDataCache.Audiotrack_GetSelectedIndex( )
				#LOG_TRACE('AudioTrack count[%s] select[%s]'% (getCount, selectIdx) )

				context = []
				for idx in range(getCount) :
					idxTrack = self.mDataCache.Audiotrack_Get( idx )
					#LOG_TRACE('getTrack name[%s] lang[%s]'% (idxTrack.mName, idxTrack.mLang) )
					if selectIdx == idx :
						label = '%s%s-%s%s' % (E_TAG_COLOR_WHITE,idxTrack.mName,idxTrack.mLang,E_TAG_COLOR_END)
					else :
						label = '%s%s-%s%s' % (E_TAG_COLOR_GREY,idxTrack.mName,idxTrack.mLang,E_TAG_COLOR_END)

					context.append( ContextItem( label ) )

				GuiLock2( True )
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
				dialog.SetProperty( context )
				dialog.doModal( )
				GuiLock2( False )

				selectIdx2 = dialog.GetSelectedIndex( )
				self.mDataCache.Audiotrack_select( selectIdx2 )

				LOG_TRACE('Select[%s --> %s]'% (selectAction, selectIdx2) )


		LOG_TRACE( 'Leave' )

	def InitInfoChannelEPG( self ):
		LOG_TRACE('Enter')

		self.mCurrentChannel = ElisIChannel()
		self.mEventCopy = ElisIEPGEvent()

		#get ch
		if self.mMode == ElisEnum.E_MODE_PVR :
			if self.mDataCache.mRecInfo :
				self.mCurrentChannel.mServiceType = recInfo.mServiceType
				self.mCurrentChannel.mNumber      = recInfo.mChannelNo
				self.mCurrentChannel.mName        = recInfo.mChannelName
				self.mCurrentChannel.mLocked      = recInfo.mLocked

				#self.mEventCopy.mStartTime = recInfo.mStartTime
				#self.mEventCopy.mDuration  = recInfo.mDuration
				#self.mEventCopy.mAgeRating = recInfo.mAgeRating
				self.mFlag_OnEventEPGReceive = False
				iEPG = self.mDataCache.RecordItem_GetEventInfo(recInfo.mRecordKey)
				if iEPG :
					if iEPG.mSid == 0 and iEPG.mTsid == 0 and iEPG.mOnid == 0 and iEPG.mEventId == 0 :
						self.mEventCopy.mName = ''

					else :
						self.mEventCopy = iEPG

					iEPGList = []
					iEPGList.append(iEPG)
					self.mEPGList = iEPGList
					LOG_TRACE('pvr epg[%s]'% ClassToList('convert', iEPGList) )

			#disable control epg
			self.UpdateLabelGUI( self.mCtrlBtnPrevEpg.getId(), False, 'enable' )
			self.UpdateLabelGUI( self.mCtrlBtnNextEpg.getId(), False, 'enable' )


		else :
			self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )

			#get epg
			self.GetEPGList()
			try :
				iEPG = None
				iEPG = self.mDataCache.Epgevent_GetPresent()
				if iEPG and iEPG.mEventName != 'No Name':
					self.mEventCopy = iEPG

			except Exception, e :
				LOG_TRACE( 'Error exception[%s]'% e )

			#enable control epg
			self.UpdateLabelGUI( self.mCtrlBtnPrevEpg.getId(), True, 'enable' )
			self.UpdateLabelGUI( self.mCtrlBtnNextEpg.getId(), True, 'enable' )

		if self.mCurrentChannel :
			self.UpdateLabelGUI( self.mCtrlLblChannelNumber.getId(), '%s'% self.mCurrentChannel.mNumber )
			self.UpdateLabelGUI( self.mCtrlLblChannelName.getId(),   self.mCurrentChannel.mName )


		LOG_TRACE( 'Leave' )

		
	def Close( self ):
		LOG_TRACE('Enter')

		self.mEventBus.Deregister( self )

		self.mEnableThread = False
		self.CurrentTimeThread().join()

		self.StopAsyncMove()
		self.StopAutomaticHide()

		WinMgr.GetInstance().CloseWindow( )
		LOG_TRACE('Leave')

	def SetAutomaticHide( self, aHide=True ) :
		self.mAutomaticHide = aHide


	def GetAutomaticHide( self ) :
		return self.mAutomaticHide

	
	def AsyncAutomaticHide( self ) :
		pass
		#if self.mSpeed == 100 :
		#	xbmc.executebuiltin('xbmc.Action(previousmenu)')
		#	LOG_TRACE('HIDE : TimeShiftPlate')

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

