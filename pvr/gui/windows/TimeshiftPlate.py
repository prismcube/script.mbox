import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as winmgr
from pvr.gui.BaseWindow import BaseWindow, Action
from pvr.gui.GuiConfig import *

import pvr.ElisMgr
from ElisAction import ElisAction
from ElisEnum import ElisEnum
from ElisEventBus import ElisEventBus
from ElisEventClass import *

from pvr.Util import RunThread, RunThread, GuiLock, LOG_TRACE, LOG_WARN, LOG_ERR
from pvr.PublicReference import EpgInfoTime, EpgInfoClock, EpgInfoComponentImage, GetSelectedLongitudeString, ClassToList

import thread, threading, time, os

#debug log
import logging
from inspect import currentframe

FLAG_CLOCKMODE_ADMYHM = 1
FLAG_CLOCKMODE_AHM    = 2
FLAG_CLOCKMODE_HMS    = 3
FLAG_CLOCKMODE_HHMM   = 4
FLAG_CLOCKMODE_INTTIME= 5

class TimeShiftPlate(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		LOG_TRACE('')
		LOG_TRACE( 'args[0]=[%s]' % args[0] )
		LOG_TRACE( 'args[1]=[%s]' % args[1] )

		self.mLastFocusId = None
		self.mEventBus = pvr.ElisMgr.GetInstance().GetEventBus()
		self.mCommander = pvr.ElisMgr.GetInstance().GetCommander()

		#default
		self.mProgressbarWidth = 980
		self.mCurrentChannel=[]
		self.mProgress_idx = 0.0
		self.mProgress_max = 0.0
		self.mEventID = 0
		self.mMode = ElisEnum.E_MODE_LIVE
		self.mIsPlay = False

		#push push test test

		#time track


	def __del__(self):
		LOG_TRACE( 'destroyed TimeshiftPlate' )

		# end thread UpdateLocalTime()
		self.mUntilThread = False

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
		self.mCtrlEventClock.setLabel('')
		self.mCtrlProgress.setPercent(0)
		
		#get channel
		#self.mCurrentChannel = self.mCommander.Channel_GetCurrent()

		self.mTimeShiftExcuteTime = self.mCommander.Datetime_GetLocalTime()

		self.InitLabelInfo()
		self.TimeshiftAction( self.mCtrlBtnPause.getId() )

		#self.mEventBus.Register( self )

		#run thread
		self.mUntilThread = True
		self.UpdateLocalTime()

	def onAction(self, aAction):
		id = aAction.getId()
		
		if id == Action.ACTION_PREVIOUS_MENU:
			LOG_TRACE( 'youn check action menu' )

		elif id == Action.ACTION_SELECT_ITEM:
			LOG_TRACE( '===== test youn: ID[%s]' % id )
	
		elif id == Action.ACTION_PARENT_DIR:
			LOG_TRACE( 'youn check ation back' )

			# end thread UpdateLocalTime()
			self.mUntilThread = False
			self.UpdateLocalTime().join()

			self.close( )
#			winmgr.GetInstance().showWindow( winmgr.WIN_ID_CHANNEL_LIST_WINDOW )
#			winmgr.GetInstance().showWindow( winmgr.WIN_ID_NULLWINDOW )
#			winmgr.shutdown()
		
		else:
			#LOG_TRACE( 'youn check action unknown id=%d' % id )
			#self.ChannelTune(id)
			pass


	def onClick(self, aControlId):
		LOG_TRACE( 'control %d' % aControlId )

		if aControlId >= self.mCtrlBtnRewind.getId() and aControlId <= self.mCtrlBtnForward.getId() :
		#if aControlId >= self.mCtrlBtnRewind.getId() and aControlId <= self.mCtrlBtnTest.getId() :
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
		LOG_TRACE( '' )
		aEvent.printdebug()

		if self.mWinId == xbmcgui.getCurrentWindowId():

			if aEvent.getName() == ElisEventCurrentEITReceived.getName() :
				if aEvent.mEventId != self.mEventID :
					ret = None
					ret = self.mCommander.Epgevent_GetPresent( )
					if ret :
						self.mEventCopy = event
						self.mEventID = aEvent.mEventId
						self.UpdateONEvent( ret )

					#ret = self.mCommander.Epgevent_Get(self.mEventID, aEvent.mSid, aEvent.mTsid, aEvent.mOnid, self.mLocalTime )
			else :
				LOG_TRACE( 'event unknown[%s]'% aEvent.getName() )
		else:
			LOG_TRACE( 'TimeshiftPlate winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId()) )

		
	def TimeshiftAction(self, aFocusId):
		LOG_TRACE( '' )

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

			if ret :
				LOG_TRACE( 'play_pause() ret[%s]'% ret )
				self.mIsPlay = False

				# toggle
				#self.mCtrlBtnPlay.setVisible( True )
				#self.mCtrlBtnPause.setVisible( False )

		elif aFocusId == self.mCtrlBtnStop.getId() :

			if self.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.mCommander.Player_Stop()

			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				ret = self.mCommander.Player_Stop()

			elif self.mMode == ElisEnum.E_MODE_PVR :
				ret = self.mCommander.Player_Stop()

			if ret :
				LOG_TRACE( 'play_stop() ret[%s]'% ret )
				self.mCtrlProgress.setPercent( 0 )
				self.mProgress_idx = 0.0
				self.mProgress_max = 0.0

				self.mUntilThread = False
				self.UpdateLocalTime().join()
				self.close( )

				winmgr.GetInstance().ShowWindow( winmgr.WIN_ID_NULLWINDOW )

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

	def UpdateONEvent(self, aEvent) :
		LOG_TRACE( '' )
		aEvent.printdebug()


	def InitLabelInfo(self) :
		#LOG_TRACE( 'currentChannel[%s]' % self.mCurrentChannel )
		
		# todo 
		self.mEventCopy = []
		self.mCtrlLblTSStartTime.setLabel('')
		self.mCtrlLblTSEndTime.setLabel('')

		self.mLocalTime = self.mCommander.Datetime_GetLocalTime()
		self.InitTimeShift()

	def InitTimeShift(self, loop = 0) :
		LOG_TRACE( '' )

		status = None
		status = self.mCommander.Player_GetStatus()
		if status :
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
				label1 = ret[0]

				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, endtime, 0)
				label2 = ret[0]


			else :
				self.mPlayTime = 0
				self.mTimeshift_staTime = status.mStartTimeInMs / 1000.0
				self.mTimeshift_curTime = status.mPlayTimeInMs  / 1000.0
				self.mTimeshift_endTime = status.mEndTimeInMs   / 1000.0
				self.mProgress_max = self.mTimeshift_endTime
				#test
				#self.mTimeshift_curTime = 0.0
				#self.mTimeshift_endTime = 50
				label1 = EpgInfoClock(FLAG_CLOCKMODE_HHMM, self.mTimeshift_staTime, 0)
				label2 = EpgInfoClock(FLAG_CLOCKMODE_HHMM, self.mTimeshift_endTime, 0)
				

			self.mCtrlLblTSStartTime.setLabel(label1)
			self.mCtrlLblTSEndTime.setLabel(label2)
			#LOG_TRACE( 'staTime[%s] ret[%s]'% (self.mTimeshift_staTime, ret) )

			

			#Speed label
			self.mSpeed = status.mSpeed

			if self.mSpeed == 100 :
				self.mCtrlImgRewind.setVisible(False)
				self.mCtrlImgForward.setVisible(False)
				self.mCtrlLblSpeed.setLabel('')

			elif self.mSpeed >= 200 and self.mSpeed <= 1000:
				self.mCtrlImgRewind.setVisible(False)
				self.mCtrlImgForward.setVisible(True)

				if self.mSpeed == 200 :
					self.mCtrlLblSpeed.setLabel('2x')
				elif self.mSpeed == 300 :
					self.mCtrlLblSpeed.setLabel('4x')
				elif self.mSpeed == 400 :
					self.mCtrlLblSpeed.setLabel('8x')
				elif self.mSpeed == 600 :
					self.mCtrlLblSpeed.setLabel('16x')
				elif self.mSpeed == 800 :
					self.mCtrlLblSpeed.setLabel('24x')
				elif self.mSpeed == 1000 :
					self.mCtrlLblSpeed.setLabel('32x')

			elif self.mSpeed <= -200 and self.mSpeed >= -1000:
				self.mCtrlImgRewind.setVisible(True)
				self.mCtrlImgForward.setVisible(False)

				if self.mSpeed == -200 :
					self.mCtrlLblSpeed.setLabel('2x')
				elif self.mSpeed == -300 :
					self.mCtrlLblSpeed.setLabel('4x')
				elif self.mSpeed == -400 :
					self.mCtrlLblSpeed.setLabel('8x')
				elif self.mSpeed == -600 :
					self.mCtrlLblSpeed.setLabel('16x')
				elif self.mSpeed == -800 :
					self.mCtrlLblSpeed.setLabel('24x')
				elif self.mSpeed == -1000 :
					self.mCtrlLblSpeed.setLabel('32x')


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


		if self.mIsPlay == True :
			self.mCtrlBtnPlay.setVisible(False)
			self.mCtrlBtnPause.setVisible(True)
		else :
			self.mCtrlBtnPlay.setVisible(True)
			self.mCtrlBtnPause.setVisible(False)


	def GetSpeedValue(self, aFocusId):
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

		return ret
		

	@RunThread
	def UpdateLocalTime(self):
		LOG_TRACE( 'begin_start thread' )
		#LOG_TRACE( 'untilThread[%s] self.mProgress_max[%s]' % (self.mUntilThread, self.mProgress_max) )

		loop = 0
		rLock = threading.RLock()
		while self.mUntilThread:
			#LOG_TRACE( 'repeat' )


			#local clock
			rLock.acquire()
			if  ( loop % 10 ) == 0 :

				isExcept = False
				try:
					self.mLocalTime = self.mCommander.Datetime_GetLocalTime()

				except Exception, e:
					LOG_TRACE( 'except[%s]'% e )
					isExcept = True
					rLock.release()

				#local clock
				if isExcept == False :
					rLock.release()
					loop = 0
					ret = EpgInfoClock(FLAG_CLOCKMODE_AHM, self.mLocalTime, 0)
					self.mCtrlEventClock.setLabel(ret[0])



			#start,endtime when timeshift
			if self.mMode == ElisEnum.E_MODE_TIMESHIFT :
				#endtime = self.mLocalTime + loop
				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, self.mLocalTime, 0)
				endtime = EpgInfoClock(FLAG_CLOCKMODE_INTTIME, 0, ret[0]) + loop
				
				self.mProgress_max = endtime

				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, endtime, 0)
				self.mCtrlLblTSEndTime.setLabel(ret[0])

				#calculate current position
				pastTime = self.mTimeshift_curTime + self.mPlayTime
				#idxmax = self.mProgress_max - self.mTimeshift_staTime
				#self.mProgress_idx = ( float(self.mPlayTime) / idxmax ) * 100
				#LOG_TRACE( 'pastTime[%s] idx[%s] max[%s]'% ( self.mPlayTime, self.mProgress_idx, idxmax ) )

				self.mProgress_idx = ( float(pastTime) / self.mProgress_max * 100 )
				LOG_TRACE( 'pastTime[%s] idx[%s] max[%s]'% ( pastTime, self.mProgress_idx, self.mProgress_max ) )

				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, pastTime, 0)
				label = ret[0]

			else:
				#calculate current position
				pastTime = self.mTimeshift_curTime + self.mPlayTime
				self.mProgress_idx = ( pastTime / self.mProgress_max * 100 )
				LOG_TRACE( 'pastTime[%s] idx[%s] max[%s]'% ( pastTime, self.mProgress_idx, self.mProgress_max ) )

				label = ''
				label = EpgInfoClock(FLAG_CLOCKMODE_HHMM, pastTime, 0)


			if self.mProgress_idx > 100:
				self.mProgress_idx = 100

			if pastTime > self.mProgress_max :
				pastTime = self.mProgress_max
				self.InitTimeShift( loop )


			#increase play time
			if self.mIsPlay == True:
				if self.mSpeed != 100:
					self.InitTimeShift( loop )

				self.mPlayTime += 1
				#LOG_TRACE( 'posx[%s] [%s] [%s]'% (posx, pastTime, pastTime/self.mProgress_max) )


			#progress drawing
			if self.mProgress_max > 0:
				try :
					LOG_TRACE( 'progress_idx[%s] getPercent[%s]' % (self.mProgress_idx, self.mCtrlProgress.getPercent()) )

					self.mCtrlProgress.setPercent( self.mProgress_idx )

					posx = int( self.mProgress_idx * self.mProgressbarWidth / 100 )
					self.mCtrlBtnCurrent.setPosition( posx, 25 )
					self.mCtrlBtnCurrent.setLabel( label )

				except Exception, e :
					LOG_TRACE( 'Error Exception[%s] progress'% e )

			else:
				LOG_TRACE( 'value error progress_max[%s]' % self.mProgress_max )



			loop += 1
			time.sleep(1)

		LOG_TRACE( 'leave_end thread' )


	def updateServiceType(self, aTvType):
		LOG_TRACE( 'serviceType[%s]' % aTvType )

	def showEPGDescription(self, aFocusid, aEvent):
		LOG_TRACE( '' )

		
		
		

