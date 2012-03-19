import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as winmgr
import pvr.gui.DialogMgr as DiaMgr
import pvr.DataCacheMgr as CacheMgr
from pvr.gui.BaseWindow import BaseWindow, Action
from pvr.gui.GuiConfig import *

import pvr.ElisMgr
from ElisAction import ElisAction
from ElisEnum import ElisEnum
from ElisEventBus import ElisEventBus
from ElisEventClass import *

from pvr.Util import RunThread, GuiLock, GuiLock2, LOG_TRACE, LOG_WARN, LOG_ERR, TimeToString, TimeFormatEnum
from pvr.PublicReference import EpgInfoTime, EpgInfoClock, EpgInfoComponentImage, GetSelectedLongitudeString, ClassToList, EnumToString

import pvr.Msg as Msg
import pvr.gui.windows.Define_string as MsgId

import thread, threading, time, os

FLAG_CLOCKMODE_ADMYHM  = 1
FLAG_CLOCKMODE_AHM     = 2
FLAG_CLOCKMODE_HMS     = 3
FLAG_CLOCKMODE_HHMM    = 4
FLAG_CLOCKMODE_INTTIME = 5

E_DEFAULT_POSY = 25
E_PROGRESS_WIDTH_MAX = 980

FLAG_TIMESHIFT_CLOSE = True

class TimeShiftPlate(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)

		#default
		self.mProgressbarWidth = E_PROGRESS_WIDTH_MAX
		self.mCurrentChannel=[]
		self.mProgress_idx = 0.0
		self.mProgress_max = 0.0
		self.mEventID = 0
		self.mMode = ElisEnum.E_MODE_LIVE
		self.mIsPlay = False
		self.mAsyncShiftTimer = None


	def __del__(self):
		LOG_TRACE( 'destroyed TimeshiftPlate' )

		# end thread CurrentTimeThread()
		self.mEnableThread = False

	def onInit(self):
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId )
		LOG_TRACE( 'winID[%d]'% self.mWinId )

		self.mCtrlImgRec            = self.getControl(  10 )
		self.mCtrlImgRewind	        = self.getControl(  31 )
		self.mCtrlImgForward        = self.getControl(  32 )
		self.mCtrlLblSpeed          = self.getControl(  33 )
		self.mCtrlProgress          = self.getControl( 201 )
		self.mCtrlBtnCurrent        = self.getControl( 202 )
		self.mCtrlEventClock        = self.getControl( 211 )
		self.mCtrlLblTSStartTime    = self.getControl( 221 )
		self.mCtrlLblTSEndTime      = self.getControl( 222 )

		self.mCtrlBtnVolume         = self.getControl( 401 )
		self.mCtrlBtnStartRec       = self.getControl( 402 )
		self.mCtrlBtnStopRec        = self.getControl( 403 )
		self.mCtrlBtnRewind         = self.getControl( 404 )
		self.mCtrlBtnPlay           = self.getControl( 405 )
		self.mCtrlBtnPause          = self.getControl( 406 )
		self.mCtrlBtnStop           = self.getControl( 407 )
		self.mCtrlBtnForward        = self.getControl( 408 )
		self.mCtrlBtnJumpRR         = self.getControl( 409 )
		self.mCtrlBtnJumpFF         = self.getControl( 410 )
		self.mCtrlBtnBookMark       = self.getControl( 411 )

		#test
		self.mCtrlLblMode          = self.getControl( 35 )

		self.mTimeshift_staTime = 0.0
		self.mTimeshift_curTime = 0.0
		self.mTimeshift_endTime = 0.0
		self.mSpeed = 100	#normal
		self.mPlayTime = 0
		self.mLocalTime = 0
		self.mTimeShiftExcuteTime = 0
		self.mUserMoveTime = 0
		self.mUserMoveTimeBack = 0
		self.mFlagUserMove = False
		self.mAccelator = 0
		self.mINSTime = 0
		self.mRepeatTimeout = 1

		self.ShowRecording( )
		
		#get channel
		#self.mCurrentChannel = self.mCommander.Channel_GetCurrent()

		self.mTimeShiftExcuteTime = self.mDataCache.Datetime_GetLocalTime()

		self.InitLabelInfo()
		self.InitTimeShift()

		if self.mSpeed != 0 :
			self.TimeshiftAction( self.mCtrlBtnPlay.getId() )
			#self.setFocusId( self.mCtrlBtnPlay.getId() )
		else :
			self.TimeshiftAction( self.mCtrlBtnPause.getId() )
			#self.setFocusId( self.mCtrlBtnPause.getId() )

		#self.mEventBus.Register( self )

		#run thread
		self.mEnableThread = True
		self.CurrentTimeThread()

		self.mAsyncShiftTimer = None

		LOG_TRACE( 'Leave' )

	def onAction(self, aAction):
		id = aAction.getId()
		self.GlobalAction( id )				
		
		if id == Action.ACTION_PREVIOUS_MENU or id == Action.ACTION_PARENT_DIR:
			LOG_TRACE( 'esc close' )
			#self.mEnableThread = False
			#self.CurrentTimeThread().join()
			#self.Close()
			self.TimeshiftAction( self.mCtrlBtnStop.getId(), FLAG_TIMESHIFT_CLOSE )

		elif id == Action.ACTION_SELECT_ITEM:
			LOG_TRACE( '===== select [%s]' % id )

		elif id == Action.ACTION_MOVE_LEFT :
			self.GetFocusId()
			if self.mFocusId == self.mCtrlBtnCurrent.getId():
				self.mUserMoveTimeBack = self.mUserMoveTime
				self.mUserMoveTime = -10
				self.mFlagUserMove = True
				#TODO : must be need timeout schedule
				self.RestartAsyncMove()
				#self.mCommander.Player_JumpByIFrame( -10000 )
				LOG_TRACE('left moveTime[%s]'% self.mUserMoveTime )

		elif id == Action.ACTION_MOVE_RIGHT:
			self.GetFocusId()
			if self.mFocusId == self.mCtrlBtnCurrent.getId():
				self.mUserMoveTimeBack = self.mUserMoveTime
				self.mUserMoveTime = 10
				self.mFlagUserMove = True
				#TODO : must be need timeout schedule
				self.RestartAsyncMove()
				#self.mCommander.Player_JumpByIFrame( 10000 )
				LOG_TRACE('right moveTime[%s]'% self.mUserMoveTime )

		#test
		elif id == 104 : #scroll up
			self.ShowRecording()
		elif id == 105 :
			pass

	def onClick(self, aControlId):
		LOG_TRACE( 'control %d' % aControlId )

		if aControlId >= self.mCtrlBtnRewind.getId() and aControlId <= self.mCtrlBtnJumpFF.getId() :
			self.TimeshiftAction( aControlId )

		elif aControlId == self.mCtrlBtnVolume.getId():
			self.GlobalAction( Action.ACTION_MUTE )
		
		elif aControlId == self.mCtrlBtnStartRec.getId() :
			runningCount = self.ShowRecording()
			LOG_TRACE( 'runningCount=%d' %runningCount)

			GuiLock2(True)
			if  runningCount < 2 :
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
				dialog.doModal()

				isOK = dialog.IsOK()
				if isOK == E_DIALOG_STATE_YES :
					self.mCtrlImgRec.setVisible( True )
			else:
				msg = 'Already %d recording(s) running' %runningCount
				xbmcgui.Dialog().ok('Infomation', msg )
			GuiLock2(False)


		elif aControlId == self.mCtrlBtnStopRec.getId() :
			runningCount = self.ShowRecording()
			LOG_TRACE( 'runningCount=%d' %runningCount )

			if  runningCount > 0 :
				GuiLock2(True)
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_STOP_RECORD )
				dialog.doModal()
				GuiLock2(False)

			time.sleep(1.5)
			self.ShowRecording()

		elif aControlId == self.mCtrlBtnBookMark.getId():
			self.ShowDialog( aControlId )


	def onFocus(self, aControlId):
		#LOG_TRACE( 'control %d' % controlId )
		pass


	@GuiLock
	def onEvent(self, aEvent):
		LOG_TRACE( 'Enter' )
		#aEvent.printdebug()

		if self.mWinId == xbmcgui.getCurrentWindowId():
			if aEvent.getName() == ElisEventCurrentEITReceived.getName() :
				LOG_TRACE( '%d : %d' %(aEvent.mEventId, self.mEventID ) )

				if aEvent.mEventId != self.mEventID :
					ret = None
					ret = self.mCommander.Epgevent_GetPresent( )
					if ret :
						if not self.mEventCopy or \
						ret.mEventId != self.mEventCopy.mEventId or \
						ret.mSid != self.mEventCopy.mSid or \
						ret.mTsid != self.mEventCopy.mTsid or \
						ret.mOnid != self.mEventCopy.mOnid :
							LOG_TRACE('epg DIFFER')
							self.mEventID = aEvent.mEventId
							self.mEventCopy = ret

							#update label
							self.UpdateONEvent( ret )

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


	def TimeshiftAction(self, aFocusId, aClose = None):
		LOG_TRACE( 'Enter' )

		ret = False

		if aFocusId == self.mCtrlBtnPlay.getId() :
			if self.mMode == ElisEnum.E_MODE_LIVE :
				#ret = self.mCommander.Player_StartTimeshiftPlayback( ElisEnum.E_PLAYER_TIMESHIFT_START_PAUSE, 0 )
				ret = self.mCommander.Player_Resume()

			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				ret = self.mCommander.Player_Resume()

			elif self.mMode == ElisEnum.E_MODE_PVR:
				ret = self.mCommander.Player_Resume()

			LOG_TRACE( 'play_resume() ret[%s]'% ret )
			if ret :
				if self.mSpeed != 100:
					#_self.mCommander.Player_SetSpeed( 100 )
					self.UpdateLabelGUI( self.mCtrlImgRewind.getId(), False )
					self.UpdateLabelGUI( self.mCtrlImgForward.getId(), False )
					self.UpdateLabelGUI( self.mCtrlLblSpeed.getId(), '' )

				self.mIsPlay = True

				# toggle
				self.UpdateLabelGUI( self.mCtrlBtnPlay.getId(), False )
				self.UpdateLabelGUI( self.mCtrlBtnPause.getId(), True, True )

		elif aFocusId == self.mCtrlBtnPause.getId() :
			if self.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.mCommander.Player_StartTimeshiftPlayback( ElisEnum.E_PLAYER_TIMESHIFT_START_PAUSE, 0 )

			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				ret = self.mCommander.Player_Pause()
			elif self.mMode == ElisEnum.E_MODE_PVR:
				ret = self.mCommander.Player_Pause()

			LOG_TRACE( 'play_pause() ret[%s]'% ret )
			if ret :
				self.mIsPlay = False

				# toggle
				self.UpdateLabelGUI( self.mCtrlBtnPlay.getId(), True, True )
				self.UpdateLabelGUI( self.mCtrlBtnPause.getId(), False )

		elif aFocusId == self.mCtrlBtnStop.getId() :
			third = 3
			while third :
				if self.mMode == ElisEnum.E_MODE_LIVE :
					ret = self.mCommander.Player_Stop()

				elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
					ret = self.mCommander.Player_Stop()

				elif self.mMode == ElisEnum.E_MODE_PVR :
					ret = self.mCommander.Player_Stop()

				third -= 1
				LOG_TRACE( 'play_stop() ret[%s] try[%d]'% (ret,third) )
				if ret :
					break
				else:
					time.sleep(0.5)


			if aClose :
				self.UpdateLabelGUI( self.mCtrlProgress.getId(), 0 )
				self.mProgress_idx = 0.0
				self.mProgress_max = 0.0

				self.mEnableThread = False
				self.CurrentTimeThread().join()
				self.Close()
				#winmgr.GetInstance().ShowWindow( winmgr.WIN_ID_NULLWINDOW )
			else :
				self.mSpeed = 100	#normal
				self.mPlayTime = 0
				self.mLocalTime = 0
				self.mUserMoveTime = 0
				self.mUserMoveTimeBack = 0
				self.InitLabelInfo()
				self.mIsPlay = True
				self.UpdateLabelGUI( self.mCtrlBtnPlay.getId(), False )
				self.UpdateLabelGUI( self.mCtrlBtnPause.getId(), True )

		elif aFocusId == self.mCtrlBtnRewind.getId() :
			nextSpeed = 100
			nextSpeed = self.GetSpeedValue( aFocusId )

			if self.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.mCommander.Player_StartTimeshiftPlayback( ElisEnum.E_PLAYER_TIMESHIFT_START_REWIND, 0 )
				#ret = self.mCommander.Player_SetSpeed( nextSpeed )

			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				ret = self.mCommander.Player_SetSpeed( nextSpeed )

			elif self.mMode == ElisEnum.E_MODE_PVR :
				ret = self.mCommander.Player_SetSpeed( nextSpeed )

			if ret :
				LOG_TRACE( 'play_rewind() ret[%s], player_SetSpeed[%s]'% (ret, nextSpeed) )

			#resume by toggle
			if self.mIsPlay :
				#self.mIsPlay = False
				self.UpdateLabelGUI( self.mCtrlBtnPlay.getId(), True )
				self.UpdateLabelGUI( self.mCtrlBtnPause.getId(), False )

		elif aFocusId == self.mCtrlBtnForward.getId() :
			nextSpeed = 100
			nextSpeed = self.GetSpeedValue( aFocusId )

			if self.mMode == ElisEnum.E_MODE_LIVE :
				#ret = self.mCommander.Player_StartTimeshiftPlayback( ElisEnum.E_PLAYER_TIMESHIFT_START_REWIND, 0 )
				ret = self.mCommander.Player_SetSpeed( nextSpeed )

			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				ret = self.mCommander.Player_SetSpeed( nextSpeed )

			elif self.mMode == ElisEnum.E_MODE_PVR :
				ret = self.mCommander.Player_SetSpeed( nextSpeed )

			if ret :
				LOG_TRACE( 'play_forward() ret[%s] player_SetSpeed[%s]'% (ret, nextSpeed) )

			#resume by toggle
			if self.mIsPlay :
				#self.mIsPlay = False
				self.UpdateLabelGUI( self.mCtrlBtnPlay.getId(), True )
				self.UpdateLabelGUI( self.mCtrlBtnPause.getId(), False )

		elif aFocusId == self.mCtrlBtnJumpRR.getId() :
			"""
			self.mUserMoveTimeBack = self.mUserMoveTime
			self.mUserMoveTime -= 10

			if self.mTimeshift_playTime :
				ret = self.mCommander.Player_JumpToIFrame( self.mTimeshift_playTime-10000 )
				LOG_TRACE('JumpRR ret[%s]'% ret )
			"""
			ret = self.mCommander.Player_JumpToIFrame( self.mTimeshift_playTime-10000 )
			LOG_TRACE('JumpRR ret[%s]'% ret )

		elif aFocusId == self.mCtrlBtnJumpFF.getId() :
			"""
			self.mUserMoveTimeBack = self.mUserMoveTime
			self.mUserMoveTime += 10

			if self.mTimeshift_playTime :
				ret = self.mCommander.Player_JumpToIFrame( self.mTimeshift_playTime+10000 )
				LOG_TRACE('JumpFF ret[%s]'% ret )
			"""
			ret = self.mCommander.Player_JumpToIFrame( self.mTimeshift_playTime+10000 )
			LOG_TRACE('JumpFF ret[%s]'% ret )

		time.sleep(0.5)
		self.InitTimeShift()

		LOG_TRACE( 'Leave' )


	def UpdateONEvent(self, aEvent) :
		LOG_TRACE( 'Enter' )
		#aEvent.printdebug()

		LOG_TRACE( 'Leave' )


	def InitLabelInfo(self) :
		#LOG_TRACE( 'currentChannel[%s]' % self.mCurrentChannel )
		self.mEventCopy = []
		self.UpdateLabelGUI( self.mCtrlEventClock.getId(),     '' )
		self.UpdateLabelGUI( self.mCtrlProgress.getId(),        0 )
		self.UpdateLabelGUI( self.mCtrlLblTSStartTime.getId(), '' )
		self.UpdateLabelGUI( self.mCtrlLblTSEndTime.getId(),   '' )
		self.UpdateLabelGUI( self.mCtrlLblSpeed.getId(),       '' )
		self.UpdateLabelGUI( self.mCtrlImgRewind.getId(),   False )
		self.UpdateLabelGUI( self.mCtrlImgForward.getId(),  False )
		self.UpdateLabelGUI( self.mCtrlBtnCurrent.getId(),     '', True )

		self.mLocalTime = self.mDataCache.Datetime_GetLocalTime()
		self.InitTimeShift()

	@GuiLock
	def UpdateLabelGUI( self, aCtrlID = None, aValue = None, aExtra = None ) :
		LOG_TRACE( 'Enter' )

		if aCtrlID == self.mCtrlBtnVolume.getId( ) :
			self.mCtrlBtnVolume.setVisible( aValue )

		elif aCtrlID == self.mCtrlBtnStartRec.getId( ) :
			self.mCtrlBtnStartRec.setEnabled( aValue )

		elif aCtrlID == self.mCtrlBtnStopRec.getId( ) :
			self.mCtrlBtnStopRec.setEnabled( aValue )

		elif aCtrlID == self.mCtrlBtnRewind.getId( ) :
			self.mCtrlBtnRewind.setVisible( aValue )

		elif aCtrlID == self.mCtrlBtnPlay.getId( ) :
			self.mCtrlBtnPlay.setVisible( aValue )
			if aExtra :
				time.sleep(0.050)
				self.setFocusId( aCtrlID )

		elif aCtrlID == self.mCtrlBtnPause.getId( ) :
			self.mCtrlBtnPause.setVisible( aValue )
			if aExtra :
				time.sleep(0.050)
				self.setFocusId( aCtrlID )

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
			self.mCtrlBtnCurrent.setLabel( aValue )
			if aExtra :
				self.mCtrlBtnCurrent.setPosition( 0, E_DEFAULT_POSY )

		elif aCtrlID == self.mCtrlLblTSStartTime.getId( ) :
			self.mCtrlLblTSStartTime.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblTSEndTime.getId( ) :
			self.mCtrlLblTSEndTime.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblSpeed.getId( ) :
			self.mCtrlLblSpeed.setLabel( aValue )

		elif aCtrlID == self.mCtrlImgRec.getId( ) :
			self.mCtrlImgRec.setVisible( aValue )



		elif aCtrlID == self.mCtrlLblMode.getId( ) :
			self.mCtrlLblMode.setLabel( aValue )

		LOG_TRACE( 'Leave' )

	def InitTimeShift( self, loop = 0 ) :
		LOG_TRACE('Enter')

		status = None
		status = self.mCommander.Player_GetStatus()
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

			lblMode = ''
			if self.mMode == ElisEnum.E_MODE_LIVE :
				lblMode = 'LIVE'
			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				lblMode = 'TIMESHIFT'
			elif self.mMode == ElisEnum.E_MODE_PVR :
				lblMode = 'PVR'
			elif self.mMode == ElisEnum.E_MODE_EXTERNAL_PVR :
				lblMode = 'EXTERNAL_PVR'
			elif self.mMode == ElisEnum.E_MODE_MULTIMEDIA :
				lblMode = 'MULTIMEDIA'
			else :
				lblMode = 'UNKNOWN'

			test = EpgInfoClock(FLAG_CLOCKMODE_HMS, status.mPlayTimeInMs/1000, 0)
			lblMode = 'mode:' + lblMode + ' current:[%s] currentToTime[%s] timeout[%s]'% (status.mPlayTimeInMs, test[0], self.mRepeatTimeout)
			self.UpdateLabelGUI( self.mCtrlLblMode.getId(), lblMode )


			#progress info
			#self.mTimeshift_staTime = 0.0
			#self.mTimeshift_curTime = 0.0
			#self.mTimeshift_endTime = 0.0
			self.mTimeshift_playTime= status.mPlayTimeInMs

			#start,endtime when timeshift
			if self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				#strTime to timeT
				"""
				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, self.mTimeShiftExcuteTime, 0)
				self.mTimeshift_staTime = EpgInfoClock(FLAG_CLOCKMODE_INTTIME, 0, ret[0])
				self.mTimeshift_curTime = self.mTimeshift_staTime
				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, self.mLocalTime, 0)
				endtime = EpgInfoClock(FLAG_CLOCKMODE_INTTIME, 0, ret[0]) + loop
				self.mProgress_max = endtime

				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, self.mTimeshift_staTime, 0)
				lbl_timeS = ret[0]

				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, endtime, 0)
				lbl_timeE = ret[0]
				"""
				if status.mStartTimeInMs :
					self.mTimeshift_staTime = status.mStartTimeInMs / 1000.0
				if status.mPlayTimeInMs :
					self.mTimeshift_curTime = status.mPlayTimeInMs / 1000.0
				if status.mEndTimeInMs :
					self.mTimeshift_endTime = status.mEndTimeInMs / 1000.0
					self.mProgress_max = self.mTimeshift_endTime

				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, self.mTimeshift_staTime, 0)
				lbl_timeS = ret[0]
				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, self.mTimeshift_curTime, 0)
				lbl_timeP = ret[0]
				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, self.mTimeshift_endTime, 0)
				lbl_timeE = ret[0]


			else :
				self.mPlayTime = 0
				self.mTimeshift_staTime = status.mStartTimeInMs / 1000.0
				self.mTimeshift_curTime = status.mPlayTimeInMs  / 1000.0
				self.mTimeshift_endTime = status.mEndTimeInMs   / 1000.0
				self.mProgress_max = self.mTimeshift_endTime

				#test
				#self.mTimeshift_curTime = 0.0
				#self.mTimeshift_endTime = 50
				lbl_timeS = EpgInfoClock(FLAG_CLOCKMODE_HHMM, self.mTimeshift_staTime, 0)
				lbl_timeP = EpgInfoClock(FLAG_CLOCKMODE_HHMM, self.mTimeshift_curTime, 0)
				lbl_timeE = EpgInfoClock(FLAG_CLOCKMODE_HHMM, self.mTimeshift_endTime, 0)
				


			#Speed label
			self.mSpeed  = status.mSpeed

			if self.mSpeed != 0 :
				self.mRepeatTimeout = 100.0 / abs(self.mSpeed)
				if self.mRepeatTimeout < 0.1 :
					self.mRepeatTimeout = 0.1

			"""
			if self.mSpeed == 100 :
				flag_Rewind  = False
				flag_Forward = False
				lbl_speed = ''
				self.mRepeatTimeout = 1 #sec

			elif self.mSpeed >= 120 and self.mSpeed <= 12800:
				flag_Rewind  = False
				flag_Forward = True

				if self.mSpeed == 120 :
					lbl_speed = '1.2x'
				elif self.mSpeed == 160 :
					lbl_speed = '1.6x'
				elif self.mSpeed == 200 :
					lbl_speed = '2x'
				elif self.mSpeed == 400 :
					lbl_speed = '4x'
				elif self.mSpeed == 800 :
					lbl_speed = '8x'
				elif self.mSpeed == 1600 :
					lbl_speed = '16x'
				elif self.mSpeed == 3200 :
					lbl_speed = '32x'
				elif self.mSpeed == 6400 :
					lbl_speed = '64x'
				elif self.mSpeed == 12800 :
					lbl_speed = '128x'

			elif self.mSpeed <= -200 and self.mSpeed >= -12800:
				flag_Rewind  = True
				flag_Forward = False

				if self.mSpeed == -200 :
					lbl_speed = '2x'
				elif self.mSpeed == -400 :
					lbl_speed = '4x'
				elif self.mSpeed == -800 :
					lbl_speed = '8x'
				elif self.mSpeed == -1600 :
					lbl_speed = '16x'
				elif self.mSpeed == -3200 :
					lbl_speed = '32x'
				elif self.mSpeed == -6400 :
					lbl_speed = '64x'
				elif self.mSpeed == -12800 :
					lbl_speed = '128x'


			self.UpdateLabelGUI( self.mCtrlImgRewind.getId(), flag_Rewind )
			self.UpdateLabelGUI( self.mCtrlImgForward.getId(), flag_Forward )
			self.UpdateLabelGUI( self.mCtrlLblSpeed.getId(), lbl_speed )
			"""

			if lbl_timeS != '' :
				self.UpdateLabelGUI( self.mCtrlLblTSStartTime.getId(), lbl_timeS )
			if lbl_timeP != '' :
				self.UpdateLabelGUI( self.mCtrlBtnCurrent.getId(), lbl_timeP )
			if lbl_timeE != '' :
				self.UpdateLabelGUI( self.mCtrlLblTSEndTime.getId(), lbl_timeE )



		LOG_TRACE('Leave')

	def GetSpeedValue(self, aFocusId):
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


	@RunThread
	def CurrentTimeThread(self):
		LOG_TRACE( 'begin_start thread' )

		loop = 0
		while self.mEnableThread:
			#LOG_TRACE( 'repeat <<<<' )

			#update localTime
			self.mLocalTime = self.mDataCache.Datetime_GetLocalTime()
			lbl_localTime = EpgInfoClock(FLAG_CLOCKMODE_AHM, self.mLocalTime, 0)
			self.mCtrlEventClock.setLabel( lbl_localTime[0] )
			#self.mCtrlEventClock.setLabel( TimeToString( self.mLocalTime, TimeFormatEnum.E_HH_MM ) )

			"""
			if self.mSpeed != 0 :
				self.InitTimeShift( )
				self.UpdateLocalTime( loop )
				time.sleep(self.mRepeatTimeout)
			#loop += 1
			else :
				time.sleep(1)
			"""
			self.InitTimeShift( )
			self.UpdateLocalTime( loop )
			time.sleep(self.mRepeatTimeout)
			

		LOG_TRACE( 'leave_end thread' )

	@GuiLock
	def UpdateLocalTime(self, loop = 0):
		LOG_TRACE( 'Enter' )
		#LOG_TRACE( 'untilThread[%s] self.mProgress_max[%s]' % (self.mEnableThread, self.mProgress_max) )

		try :
			lbl_timeE = ''
			lbl_timeP = ''

			#start,endtime when timeshift
			if self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				"""
				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, self.mLocalTime, 0)
				endtime = EpgInfoClock(FLAG_CLOCKMODE_INTTIME, 0, ret[0]) + loop
				
				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, endtime, 0)
				lbl_timeE = ret[0]

				#calculate current position
				self.mProgress_max = endtime
				pastTime = self.mTimeshift_curTime + self.mPlayTime + self.mUserMoveTime
				self.mProgress_idx = ( float(pastTime) / self.mProgress_max * 100 )
				LOG_TRACE( 'pastTime[%s] idx[%s] max[%s] move[%s]'% (pastTime, self.mProgress_idx, self.mProgress_max, self.mUserMoveTime ) )

				if self.mProgress_idx > 100 or self.mProgress_idx < 0 :
					self.mUserMoveTime = self.mUserMoveTimeBack
					pastTime = self.mTimeshift_curTime + self.mPlayTime + self.mUserMoveTimeBack
					self.mProgress_idx = ( float(pastTime) / self.mProgress_max * 100 )

				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, pastTime, 0)
				lbl_timeP = ret[0]
				"""
				#calculate current position
				pastTime = self.mTimeshift_curTime + self.mUserMoveTime
				self.mProgress_idx = ( float(pastTime) / self.mProgress_max * 100 )
				if self.mProgress_idx > 100 or self.mProgress_idx < 0 :
					self.mUserMoveTime = self.mUserMoveTimeBack
					pastTime = self.mTimeshift_curTime + self.mUserMoveTime
					self.mProgress_idx = ( float(pastTime) / self.mProgress_max * 100 )

				LOG_TRACE( 'pastTime[%s] idx[%s] max[%s]'% ( pastTime, self.mProgress_idx, self.mProgress_max ) )

			else:
				#calculate current position
				pastTime = self.mTimeshift_curTime + self.mPlayTime
				self.mProgress_idx = ( pastTime / self.mProgress_max * 100 )
				LOG_TRACE( 'pastTime[%s] idx[%s] max[%s]'% ( pastTime, self.mProgress_idx, self.mProgress_max ) )

				#lbl_timeP = EpgInfoClock(FLAG_CLOCKMODE_HHMM, pastTime, 0)

			if self.mProgress_idx > 100:
				self.mProgress_idx = 100
			elif self.mProgress_idx < 0 :
				self.mProgress_idx = 0

			if pastTime > self.mProgress_max :
				pastTime = self.mProgress_max
				self.InitTimeShift( loop )

			#increase play time
			if self.mFlagUserMove == False and self.mIsPlay == True:
				if self.mSpeed != 100:
					self.InitTimeShift( loop )

				self.mPlayTime += 1
				#LOG_TRACE( 'posx[%s] [%s] [%s]'% (posx, pastTime, pastTime/self.mProgress_max) )

			#if self.mMode == ElisEnum.E_MODE_TIMESHIFT :
			#	self.mCtrlLblTSEndTime.setLabel( lbl_timeE )

			#progress drawing
			LOG_TRACE( 'progress max[%s] idx[%s] percent[%s]'% (self.mProgress_max, self.mProgress_idx, self.mCtrlProgress.getPercent()) )
			self.mCtrlProgress.setPercent( self.mProgress_idx )
			posx = int( self.mProgress_idx * self.mProgressbarWidth / 100 )
			self.mCtrlBtnCurrent.setPosition( posx, E_DEFAULT_POSY )
			#self.mCtrlBtnCurrent.setLabel( lbl_timeP )


		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		LOG_TRACE( 'leave' )



	def updateServiceType(self, aTvType):
		LOG_TRACE( 'serviceType[%s]' % aTvType )

	def showEPGDescription(self, aFocusid, aEvent):
		LOG_TRACE( '' )

	def ShowRecording( self ) :
		LOG_TRACE('Enter')

		isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )
		LOG_TRACE('isRunRecCount[%s]'% isRunRec)

		imgValue = False
		btnValue = False
		if isRunRec > 0 :
			imgValue = True
		else :
			imgValue = False
		self.UpdateLabelGUI( self.mCtrlImgRec.getId(), imgValue )

		if isRunRec >= 2 :
			btnValue = False
		else :
			btnValue = True
		self.UpdateLabelGUI( self.mCtrlBtnStartRec.getId(), btnValue )

		return isRunRec

		LOG_TRACE('Leave')

		
	def Close( self ):
		#self.mEventBus.Deregister( self )
		#self.TimeshiftAction(self.mCtrlBtnStop.getId())
		#self.mCommander.Player_Stop()
		self.StopAsyncMove()
		self.close()

	def RestartAsyncMove( self ) :
		self.StopAsyncMove( )
		self.StartAsyncMove( )


	def StartAsyncMove( self ) :
		self.mAsyncShiftTimer = threading.Timer( 0.1, self.AsyncUpdateCurrentMove ) 				
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
				if self.mAccelator > 2 :
					#self.mUserMoveTime = int( self.mUserMoveTime * (1.5 ** self.mAccelator) / 10000 )
					self.mUserMoveTime = self.mUserMoveTime * self.mAccelator
				frameJump = self.mTimeshift_playTime + self.mUserMoveTime * 1000
				ret = self.mCommander.Player_JumpToIFrame( frameJump )
				LOG_TRACE('2============frameJump[%s] accelator[%s] ret[%s]'% (frameJump,self.mAccelator,ret) )
				if ret :
					self.InitTimeShift()
					self.UpdateLocalTime()

				self.mFlagUserMove = True
				self.mAccelator = 0

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )
		

