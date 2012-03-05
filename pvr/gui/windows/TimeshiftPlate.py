import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as winmgr
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

class TimeShiftPlate(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)

		#default
		self.mProgressbarWidth = 980
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


		self.mCtrlImgRewind	        = self.getControl(  31 )
		self.mCtrlImgForward        = self.getControl(  32 )
		self.mCtrlLblSpeed          = self.getControl(  33 )
		self.mCtrlProgress          = self.getControl( 201 )
		self.mCtrlBtnCurrent        = self.getControl( 202 )
		self.mCtrlEventClock        = self.getControl( 211 )
		self.mCtrlLblTSStartTime    = self.getControl( 221 )
		self.mCtrlLblTSEndTime      = self.getControl( 222 )

		self.mCtrlBtnVolume         = self.getControl( 402 )
		self.mCtrlBtnRecord         = self.getControl( 403 )
		self.mCtrlBtnRewind         = self.getControl( 404 )
		self.mCtrlBtnPlay           = self.getControl( 405 )
		self.mCtrlBtnPause          = self.getControl( 406 )
		self.mCtrlBtnStop           = self.getControl( 407 )
		self.mCtrlBtnForward        = self.getControl( 408 )

		#test
		#self.mCtrlBtnTest          = self.getControl( 409 )

		self.mSpeed = 100	#normal
		self.mPlayTime = 0
		self.mLocalTime = 0
		self.mTimeShiftExcuteTime = 0
		self.mUserMoveTime = 0
		self.mUserMoveTimeBack = 0
		self.mFlagUserMove = False
		self.mAccelator = 0
		self.mINSTime = 0

		
		#get channel
		#self.mCurrentChannel = self.mCommander.Channel_GetCurrent()

		self.mTimeShiftExcuteTime = self.mDataCache.Datetime_GetLocalTime()

		self.InitLabelInfo()
		self.TimeshiftAction( self.mCtrlBtnPause.getId() )

		#self.mEventBus.Register( self )

		#run thread
		#self.mEnableThread = True
		#self.CurrentTimeThread()

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
			self.TimeshiftAction(self.mCtrlBtnStop.getId())

		elif id == Action.ACTION_SELECT_ITEM:
			LOG_TRACE( '===== select [%s]' % id )

		elif id == Action.ACTION_MOVE_LEFT :
			self.GetFocusId()
			if self.mFocusId == self.mCtrlBtnCurrent.getId():
				self.mUserMoveTimeBack = self.mUserMoveTime
				self.mUserMoveTime -= 10
				self.mFlagUserMove = True
				#TODO : must be need timeout schedule
				self.RestartAsyncMove()
				LOG_TRACE('left moveTime[%s]'% self.mUserMoveTime )

		elif id == Action.ACTION_MOVE_RIGHT:
			self.GetFocusId()
			if self.mFocusId == self.mCtrlBtnCurrent.getId():
				self.mUserMoveTimeBack = self.mUserMoveTime
				self.mUserMoveTime += 10
				self.mFlagUserMove = True
				#TODO : must be need timeout schedule
				self.RestartAsyncMove()
				LOG_TRACE('right moveTime[%s]'% self.mUserMoveTime )



	def onClick(self, aControlId):
		LOG_TRACE( 'control %d' % aControlId )

		if aControlId >= self.mCtrlBtnRewind.getId() and aControlId <= self.mCtrlBtnForward.getId() :
			#self.InitTimeShift()
			self.TimeshiftAction( aControlId )
		
		elif aControlId == self.mCtrlBtnRecord.getId():
			self.TimeshiftAction( aControlId )

		elif aControlId == self.mCtrlBtnVolume.getId():
			self.TimeshiftAction( aControlId )
			#ret = self.mCommander.Player_GetStatus()
			#ret.printdebug()


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


	def TimeshiftAction(self, aFocusId):
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

			if ret :
				LOG_TRACE( 'play_resume() ret[%s]'% ret )

				if self.mSpeed != 100:
					self.mCommander.Player_SetSpeed( 100 )
					self.mCtrlImgRewind.setVisible( False )
					self.mCtrlImgForward.setVisible( False )
					self.mCtrlLblSpeed.setLabel( '' )

				self.mIsPlay = True

				# toggle
				#self.mCtrlBtnPlay.setVisible( False )
				#self.mCtrlBtnPause.setVisible( True )


		elif aFocusId == self.mCtrlBtnPause.getId() :
		#elif aFocusId == self.mCtrlBtnTest.getId() :
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
				#self.mCtrlBtnPlay.setVisible( True )
				#self.mCtrlBtnPause.setVisible( False )

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

			self.mCtrlProgress.setPercent( 0 )
			self.mProgress_idx = 0.0
			self.mProgress_max = 0.0

			self.mEnableThread = False
			self.CurrentTimeThread().join()
			self.Close()

			#winmgr.GetInstance().ShowWindow( winmgr.WIN_ID_NULLWINDOW )

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

		time.sleep(0.5)
		self.InitTimeShift()

		LOG_TRACE( 'Leave' )


	def UpdateONEvent(self, aEvent) :
		LOG_TRACE( 'Enter' )
		#aEvent.printdebug()

		LOG_TRACE( 'Leave' )


	def InitLabelInfo(self) :
		#LOG_TRACE( 'currentChannel[%s]' % self.mCurrentChannel )
		
		# todo 
		self.mEventCopy = []
		GuiLock2(True)
		self.mCtrlEventClock.setLabel('')
		self.mCtrlProgress.setPercent(0)
		self.mCtrlLblTSStartTime.setLabel('')
		self.mCtrlLblTSEndTime.setLabel('')
		GuiLock2(False)

		self.mLocalTime = self.mDataCache.Datetime_GetLocalTime()
		self.InitTimeShift()

	def InitTimeShift(self, loop = 0) :
		LOG_TRACE('Enter')

		status = None
		status = self.mCommander.Player_GetStatus()
		if status :
			flag_Rewind  = False
			flag_Forward = False
			lbl_speed = ''
			lbl_timeS = ''
			lbl_timeE = ''

			retList = []
			retList.append( status )
			LOG_TRACE( 'player_GetStatus[%s]'% ClassToList( 'convert', retList ) )
			#status.printdebug()
		
			#play mode
			self.mMode = status.mMode

			#progress info
			self.mTimeshift_staTime = 0.0
			self.mTimeshift_curTime = 0.0
			self.mTimeshift_endTime = 0.0

			#start,endtime when timeshift
			if self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				#strTime to timeT
				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, self.mTimeShiftExcuteTime, 0)
				self.mTimeshift_staTime = EpgInfoClock(FLAG_CLOCKMODE_INTTIME, 0, ret[0])
				self.mTimeshift_curTime = self.mTimeshift_staTime

				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, self.mLocalTime, 0)
				endtime = EpgInfoClock(FLAG_CLOCKMODE_INTTIME, 0, ret[0]) + loop
				
				#self.mTimeshift_staTime = self.mTimeShiftExcuteTime
				#self.mTimeshift_curTime = self.mTimeShiftExcuteTime
				#endtime = self.mLocalTime + loop
				self.mProgress_max = endtime

				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, self.mTimeshift_staTime, 0)
				lbl_timeS = ret[0]

				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, endtime, 0)
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
				lbl_timeE = EpgInfoClock(FLAG_CLOCKMODE_HHMM, self.mTimeshift_endTime, 0)
				


			#Speed label
			self.mSpeed  = status.mSpeed

			if self.mSpeed == 100 :
				flag_Rewind  = False
				flag_Forward = False
				lbl_speed = ''

			elif self.mSpeed >= 200 and self.mSpeed <= 1000:
				flag_Rewind  = False
				flag_Forward = True

				if self.mSpeed == 200 :
					lbl_speed = '2x'
				elif self.mSpeed == 300 :
					lbl_speed = '4x'
				elif self.mSpeed == 400 :
					lbl_speed = '8x'
				elif self.mSpeed == 600 :
					lbl_speed = '16x'
				elif self.mSpeed == 800 :
					lbl_speed = '24x'
				elif self.mSpeed == 1000 :
					lbl_speed = '32x'

			elif self.mSpeed <= -200 and self.mSpeed >= -1000:
				flag_Rewind  = True
				flag_Forward = False

				if self.mSpeed == -200 :
					lbl_speed = '2x'
				elif self.mSpeed == -300 :
					lbl_speed = '4x'
				elif self.mSpeed == -400 :
					lbl_speed = '8x'
				elif self.mSpeed == -600 :
					lbl_speed = '16x'
				elif self.mSpeed == -800 :
					lbl_speed = '24x'
				elif self.mSpeed == -1000 :
					lbl_speed = '32x'


			"""
			#pending status
			isPending = status.mIsTimeshiftPending
			if isPending == True :
				self.mIsPlay = True
				self.mCtrlBtnPlay.setVisible(False)
				self.mCtrlBtnPause.setVisible(True)

			else :
				self.mIsPlay = False
				self.mCtrlBtnPlay.setVisible(True)
				self.mCtrlBtnPause.setVisible(False)
			"""

			GuiLock2(True)
			self.mCtrlImgRewind.setVisible( flag_Rewind )
			self.mCtrlImgForward.setVisible( flag_Forward )
			self.mCtrlLblSpeed.setLabel( lbl_speed )

			self.mCtrlLblTSStartTime.setLabel( lbl_timeS )
			self.mCtrlLblTSEndTime.setLabel( lbl_timeE )
			GuiLock2(False)


		GuiLock2(True)
		if self.mIsPlay == True :
			self.mCtrlBtnPlay.setVisible(False)
			self.mCtrlBtnPause.setVisible(True)
		else :
			self.mCtrlBtnPlay.setVisible(True)
			self.mCtrlBtnPause.setVisible(False)
		GuiLock2(False)

		LOG_TRACE('Leave')

	def GetSpeedValue(self, aFocusId):
		LOG_TRACE('Enter')

		LOG_TRACE( 'mSpeed[%s]'% self.mSpeed )
		ret = 0
		if aFocusId == self.mCtrlBtnRewind.getId():

			if self.mSpeed == -1000 :
				ret = -1000
			elif self.mSpeed == -800 :
				ret = -1000
			elif self.mSpeed == -600 :
				ret = -800
			elif self.mSpeed == -400 :
				ret = -600
			elif self.mSpeed == -300 :
				ret = -400
			elif self.mSpeed == -200 :
				ret = -300
			elif self.mSpeed == 100 :
				ret = -200
			elif self.mSpeed == 200 :
				ret = 100
			elif self.mSpeed == 300 :
				ret = 200
			elif self.mSpeed == 400 :
				ret = 300
			elif self.mSpeed == 600 :
				ret = 400
			elif self.mSpeed == 800 :
				ret = 600
			elif self.mSpeed == 1000 :
				ret = 800

		elif aFocusId == self.mCtrlBtnForward.getId():
			if self.mSpeed == 100 :
				ret = 200
			elif self.mSpeed == 200 :
				ret = 300
			elif self.mSpeed == 300 :
				ret = 400
			elif self.mSpeed == 400 :
				ret = 600
			elif self.mSpeed == 600 :
				ret = 800
			elif self.mSpeed == 800 :
				ret = 1000
			elif self.mSpeed == 1000 :
				ret = 1000

			elif self.mSpeed == -200 :
				ret = 100
			elif self.mSpeed == -300 :
				ret = -200
			elif self.mSpeed == -400 :
				ret = -300
			elif self.mSpeed == -600 :
				ret = -400
			elif self.mSpeed == -800 :
				ret = -600
			elif self.mSpeed == -1000 :
				ret = -800

		else:
			ret = 100 #default

		LOG_TRACE('Leave')
		return ret


	@RunThread
	def CurrentTimeThread(self):
		LOG_TRACE( 'begin_start thread' )

		loop = 0
		while self.mEnableThread:
			#LOG_TRACE( 'repeat <<<<' )

			if  ( loop % 10 ) == 0 :
				#LOG_TRACE( 'loop=%d' %loop )
				self.mLocalTime = self.mDataCache.Datetime_GetLocalTime()
				#self.UpdateLocalTime( )

			self.UpdateLocalTime( loop )
			#self.RestartAsyncMove()

			time.sleep(1)
			self.mLocalTime += 1
			#loop += 1

		LOG_TRACE( 'leave_end thread' )

	@GuiLock
	def UpdateLocalTime(self, loop = 0):
		LOG_TRACE( 'Enter' )
		#LOG_TRACE( 'untilThread[%s] self.mProgress_max[%s]' % (self.mEnableThread, self.mProgress_max) )

		try :
			lbl_localTime = ''
			lbl_timeE = ''
			lbl_timeP = ''

			#update localTime
			ret = EpgInfoClock(FLAG_CLOCKMODE_AHM, self.mLocalTime, 0)
			lbl_localTime = ret[0]

			#start,endtime when timeshift
			if self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				#endtime = self.mLocalTime + loop
				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, self.mLocalTime, 0)
				endtime = EpgInfoClock(FLAG_CLOCKMODE_INTTIME, 0, ret[0]) + loop
				
				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, endtime, 0)
				lbl_timeE = ret[0]

				#calculate current position
				self.mProgress_max = endtime
				pastTime = self.mTimeshift_curTime + self.mPlayTime + self.mUserMoveTime
				self.mProgress_idx = ( float(pastTime) / self.mProgress_max * 100 )
				LOG_TRACE( 'pastTime[%s] idx[%s] max[%s] move[%s]'% ( pastTime, self.mProgress_idx, self.mProgress_max, self.mUserMoveTime ) )

				if self.mProgress_idx > 100 or self.mProgress_idx < 0 :
					self.mUserMoveTime = self.mUserMoveTimeBack
					pastTime = self.mTimeshift_curTime + self.mPlayTime + self.mUserMoveTimeBack
					self.mProgress_idx = ( float(pastTime) / self.mProgress_max * 100 )

				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, pastTime, 0)
				lbl_timeP = ret[0]

			else:
				#calculate current position
				pastTime = self.mTimeshift_curTime + self.mPlayTime
				self.mProgress_idx = ( pastTime / self.mProgress_max * 100 )
				LOG_TRACE( 'pastTime[%s] idx[%s] max[%s]'% ( pastTime, self.mProgress_idx, self.mProgress_max ) )

				lbl_timeP = EpgInfoClock(FLAG_CLOCKMODE_HHMM, pastTime, 0)

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

			#print label
			self.mCtrlEventClock.setLabel(lbl_localTime)
			if self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				self.mCtrlLblTSEndTime.setLabel( lbl_timeE )

			#progress drawing
			LOG_TRACE( 'progress max[%s] idx[%s] percent[%s]'% (self.mProgress_max, self.mProgress_idx, self.mCtrlProgress.getPercent()) )
			self.mCtrlProgress.setPercent( self.mProgress_idx )
			posx = int( self.mProgress_idx * self.mProgressbarWidth / 100 )
			self.mCtrlBtnCurrent.setPosition( posx, 25 )
			self.mCtrlBtnCurrent.setLabel( lbl_timeP )


		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		LOG_TRACE( 'leave' )



	def updateServiceType(self, aTvType):
		LOG_TRACE( 'serviceType[%s]' % aTvType )

	def showEPGDescription(self, aFocusid, aEvent):
		LOG_TRACE( '' )

		
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

		self.mAccelator += 100
		if self.mAccelator > 200 :
			self.mUserMoveTime = self.mAccelator * (self.mUserMoveTime / abs(self.mUserMoveTime))
		LOG_TRACE('1================Accelator[%s] move[%s]'% (self.mAccelator, self.mUserMoveTime) )

	def StopAsyncMove( self ) :
		if self.mAsyncShiftTimer and self.mAsyncShiftTimer.isAlive() :
			self.mAsyncShiftTimer.cancel()
			del self.mAsyncShiftTimer

		self.mAsyncShiftTimer  = None

	#TODO : must be need timeout schedule
	def AsyncUpdateCurrentMove( self ) :
		try :
			self.UpdateLocalTime()
			self.mFlagUserMove = False
			self.mAccelator = 0

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )
		

