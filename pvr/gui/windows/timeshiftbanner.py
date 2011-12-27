import xbmc
import xbmcgui
import sys
import time

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import BaseWindow
from pvr.gui.basewindow import Action

import pvr.elismgr
from elisaction import ElisAction
from elisenum import ElisEnum


#from threading import Thread
from pvr.util import run_async, is_digit, Mutex, epgInfoTime, epgInfoClock, epgInfoComponentImage, GetSelectedLongitudeString #, synchronized, sync_instance
import thread, threading

#debug log
import logging
from inspect import currentframe

log = logging.getLogger('mythbox.ui')
mlog = logging.getLogger('mythbox.method')


class TimeShiftBanner(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		print 'f_coname[%s] f_lineno[%d] co_filename[%s]' %(currentframe().f_code.co_name, currentframe().f_lineno, currentframe().f_code.co_filename)    
		print 'args[0]=[%s]' % args[0]
		print 'args[1]=[%s]' % args[1]

		self.lastFocusId = None
		self.eventBus = pvr.elismgr.getInstance().getEventBus()
		#self.eventBus.register( self )
		self.commander = pvr.elismgr.getInstance().getCommander()

		#default
		self.progressbarWidth = 650
		self.currentChannel=[]
		self.progress_idx = 0.0
		self.progress_max = 0.0
		self.eventID = 0
		self.mMode = ElisEnum.E_MODE_LIVE

		#push push test test

		#time track


	def __del__(self):
		print '[%s():%s] destroyed ChannelBanner'% (currentframe().f_code.co_name, currentframe().f_lineno)

		# end thread updateLocalTime()
		self.untilThread = False

	def onInit(self):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		if not self.win:
			self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())

			self.ctrlImgRewind		= self.getControl(  31 )
			self.ctrlImgForward		= self.getControl(  32 )
			self.ctrlLblSpeed		= self.getControl(  33 )
			self.ctrlProgress		= self.getControl( 201 )
			self.ctrlBtnCurrent		= self.getControl( 202 )
			self.ctrlEventClock		= self.getControl( 211 )
			self.ctrlLblTSStartTime	= self.getControl( 221 )
			self.ctrlLblTSEndTime	= self.getControl( 222 )

			self.ctrlBtnVolume		= self.getControl( 402 )
			self.ctrlBtnRecord		= self.getControl( 403 )
			self.ctrlBtnRewind		= self.getControl( 404 )
			self.ctrlBtnPlay		= self.getControl( 405 )
			self.ctrlBtnPause		= self.getControl( 406 )
			self.ctrlBtnStop		= self.getControl( 407 )
			self.ctrlBtnForward		= self.getControl( 408 )

			#test
			#self.ctrlBtnTest		= self.getControl( 409 )

		self.mSpeed = 100	#normal
		self.ctrlEventClock.setLabel('')
		self.ctrlProgress.setPercent(0)
		
		#get channel
		#self.currentChannel = self.commander.channel_GetCurrent()

		self.initLabelInfo()
	

		#run thread
		self.isPlay = False
		self.untilThread = True
		self.updateLocalTime()


	def onAction(self, action):
		id = action.getId()
		focusid = self.getFocusId()
		
		if id == Action.ACTION_PREVIOUS_MENU:
			print 'youn check action menu'

		elif id == Action.ACTION_SELECT_ITEM:
			print '===== test youn: ID[%s]' % id
			log.debug('youn:%s' % id)
	
		elif id == Action.ACTION_PARENT_DIR:
			print 'youn check ation back'

			# end thread updateLocalTime()
			self.untilThread = False
			self.updateLocalTime().join()

			self.close( )
#			winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_LIST_WINDOW )
#			winmgr.getInstance().showWindow( winmgr.WIN_ID_NULLWINDOW )
#			winmgr.shutdown()


		elif id == Action.ACTION_PAGE_UP:
			self.channelTune(id)

		elif id == Action.ACTION_PAGE_DOWN:
			self.channelTune(id)

		elif id == Action.ACTION_MUTE:
			self.updateVolume(id)
		
		else:
			#print 'youn check action unknown id=%d' % id
			#self.channelTune(id)
			pass


	def onClick(self, controlId):
		print 'onclick(): control %d' % controlId

		if controlId >= self.ctrlBtnRewind.getId() and controlId <= self.ctrlBtnForward.getId() :
		#if controlId >= self.ctrlBtnRewind.getId() and controlId <= self.ctrlBtnTest.getId() :
			#self.initTimeShift()
			self.timeshiftAction(controlId)
		

		elif controlId == self.ctrlBtnRecord.getId():
			self.timeshiftAction(controlId)

		elif controlId == self.ctrlBtnVolume.getId():
			self.timeshiftAction(controlId)
			ret = self.commander.player_GetStatus()
			print 'player_status[%s]'% ret




	def onFocus(self, controlId):
		#print "onFocus(): control %d" % controlId
		pass

	def onEvent(self, event):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		if self.win :
			msg = event[0]
			
			if msg == 'Elis-CurrentEITReceived' :

				if int(event[4]) != self.eventID :			
					ret = self.commander.epgevent_GetPresent( )
					if len( ret ) > 0 :
						self.eventCopy = event
						self.eventID = int( event[4] )
						self.updateONEvent( ret )

					#ret = self.commander.epgevent_Get(self.eventID, int(event[1]), int(event[2]), int(event[3]), int(self.epgClock[0]) )
			else :
				print 'event unknown[%s]'% event
		else:
			print 'show screen is another windows page[%s]'% xbmcgui.getCurrentWindowId()

		
	def timeshiftAction(self, focusId):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)		

		ret = False

		if focusId == self.ctrlBtnPlay.getId():
			if self.mMode == ElisEnum.E_MODE_LIVE:
				#ret = self.commander.player_StartTimeshiftPlayback(ElisEnum.E_PLAYER_TIMESHIFT_START_PAUSE,0)
				ret = self.commander.player_Resume()
			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT:
				ret = self.commander.player_Resume()
			elif self.mMode == ElisEnum.E_MODE_PVR:
				ret = self.commander.player_Resume()

			if ret[0] == 'TRUE':
				print 'play ret[%s]'% ret

				if self.mSpeed != 100:
					self.commander.player_SetSpeed(100)
					self.ctrlImgRewind.setVisible(False)
					self.ctrlImgForward.setVisible(False)
					self.ctrlLblSpeed.setLabel('')

				self.isPlay = True

				# toggle
				#self.ctrlBtnPlay.setVisible(False)
				#self.ctrlBtnPause.setVisible(True)


		elif focusId == self.ctrlBtnPause.getId():
		#elif focusId == self.ctrlBtnTest.getId():
			if self.mMode == ElisEnum.E_MODE_LIVE:
				ret = self.commander.player_StartTimeshiftPlayback(ElisEnum.E_PLAYER_TIMESHIFT_START_PAUSE,0)
			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT:
				ret = self.commander.player_Pause()
			elif self.mMode == ElisEnum.E_MODE_PVR:
				ret = self.commander.player_Pause()

			if ret[0] == 'TRUE':
				print 'pause ret[%s]'% ret
				self.isPlay = False
				# toggle
				#self.ctrlBtnPlay.setVisible(True)
				#self.ctrlBtnPause.setVisible(False)

		elif focusId == self.ctrlBtnStop.getId():

			if self.mMode == ElisEnum.E_MODE_LIVE:
				ret = self.commander.player_Stop()
			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT:
				ret = self.commander.player_Stop()
			elif self.mMode == ElisEnum.E_MODE_PVR:
				ret = self.commander.player_Stop()

			if ret[0] == 'TRUE':
				print 'stop ret[%s]'% ret
				self.ctrlProgress.setPercent(0)
				self.progress_idx = 0.0
				self.progress_max = 0.0

				self.untilThread = False
				self.updateLocalTime().join()
				self.close( )

				winmgr.getInstance().showWindow( winmgr.WIN_ID_NULLWINDOW )

		elif focusId == self.ctrlBtnRewind.getId():
			nextSpeed = 100
			nextSpeed = self.getSpeedValue(focusId)

			if self.mMode == ElisEnum.E_MODE_LIVE:
				ret = self.commander.player_StartTimeshiftPlayback(ElisEnum.E_PLAYER_TIMESHIFT_START_REWIND,0)
				#ret = self.commander.player_SetSpeed(nextSpeed)
			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT:
				ret = self.commander.player_SetSpeed(nextSpeed)
			elif self.mMode == ElisEnum.E_MODE_PVR:
				ret = self.commander.player_SetSpeed(nextSpeed)

			if ret[0] == 'TRUE':
				print 'rewind ret[%s], player_SetSpeed[%s]'% (ret, nextSpeed)

		elif focusId == self.ctrlBtnForward.getId():
			nextSpeed = 100
			nextSpeed = self.getSpeedValue(focusId)

			if self.mMode == ElisEnum.E_MODE_LIVE:
				#ret = self.commander.player_StartTimeshiftPlayback(ElisEnum.E_PLAYER_TIMESHIFT_START_REWIND,0)
				ret = self.commander.player_SetSpeed(nextSpeed)
			elif self.mMode == ElisEnum.E_MODE_TIMESHIFT:
				ret = self.commander.player_SetSpeed(nextSpeed)
			elif self.mMode == ElisEnum.E_MODE_PVR:
				ret = self.commander.player_SetSpeed(nextSpeed)

			if ret[0] == 'TRUE':
				print 'forward ret[%s] player_SetSpeed[%s]'% (ret, nextSpeed)

		time.sleep(0.5)
		self.initTimeShift()

	def updateONEvent(self, event):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'event[%s]'% event


	def initLabelInfo(self):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'currentChannel[%s]' % self.currentChannel
		
		# todo 
		self.eventCopy = []
		self.ctrlLblTSStartTime.setLabel('')
		self.ctrlLblTSEndTime.setLabel('')

		self.epgClock = []
		self.epgClock = self.commander.datetime_GetLocalTime()
		print 'epgClock[%s]'% self.epgClock

		self.initTimeShift()

	def initTimeShift(self) :
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		status = []
		status = self.commander.player_GetStatus()

		print 'player_GetStatus[%s]'% status
		
		if len(status) == 11:
			#play mode
			self.mMode = int(status[0])

			#progress info
			self.curTime = 0
			self.timeshift_staTime = 0.0
			self.timeshift_curTime = 0.0
			self.timeshift_endTime = 0.0

			self.timeshift_staTime = int(status[3]) / 1000.0
			self.timeshift_curTime = int(status[4]) / 1000.0
			self.timeshift_endTime = int(status[5]) / 1000.0
			#test
			#self.timeshift_curTime = 0.0
			#self.timeshift_endTime = 50

			ret = ''
			ret = epgInfoClock(4, self.timeshift_staTime, 0)
			self.ctrlLblTSStartTime.setLabel(ret)
			#print 'staTime[%s] ret[%s]'% (self.timeshift_staTime, ret)

			ret = ''
			ret = epgInfoClock(4, self.timeshift_endTime, 0)
			self.ctrlLblTSEndTime.setLabel(ret)

			self.progress_max = self.timeshift_endTime


			#Speed label
			self.mSpeed = int(status[6])

			if self.mSpeed == 100 :
				self.ctrlImgRewind.setVisible(False)
				self.ctrlImgForward.setVisible(False)
				self.ctrlLblSpeed.setLabel('')

			elif self.mSpeed >= 200 and self.mSpeed <= 1000:
				self.ctrlImgRewind.setVisible(False)
				self.ctrlImgForward.setVisible(True)

				if self.mSpeed == 200 :
					self.ctrlLblSpeed.setLabel('2x')
				elif self.mSpeed == 300 :
					self.ctrlLblSpeed.setLabel('4x')
				elif self.mSpeed == 400 :
					self.ctrlLblSpeed.setLabel('8x')
				elif self.mSpeed == 600 :
					self.ctrlLblSpeed.setLabel('16x')
				elif self.mSpeed == 800 :
					self.ctrlLblSpeed.setLabel('24x')
				elif self.mSpeed == 1000 :
					self.ctrlLblSpeed.setLabel('32x')

			elif self.mSpeed <= -200 and self.mSpeed >= -1000:
				self.ctrlImgRewind.setVisible(True)
				self.ctrlImgForward.setVisible(False)

				if self.mSpeed == -200 :
					self.ctrlLblSpeed.setLabel('2x')
				elif self.mSpeed == -300 :
					self.ctrlLblSpeed.setLabel('4x')
				elif self.mSpeed == -400 :
					self.ctrlLblSpeed.setLabel('8x')
				elif self.mSpeed == -600 :
					self.ctrlLblSpeed.setLabel('16x')
				elif self.mSpeed == -800 :
					self.ctrlLblSpeed.setLabel('24x')
				elif self.mSpeed == -1000 :
					self.ctrlLblSpeed.setLabel('32x')

			"""
			#pending status
			mIsTimeshiftPending = int(status[7])
			if mIsTimeshiftPending == True :
				self.isPlay = True
				self.ctrlBtnPlay.setVisible(False)
				self.ctrlBtnPause.setVisible(True)

			else :
				self.isPlay = False
				self.ctrlBtnPlay.setVisible(True)
				self.ctrlBtnPause.setVisible(False)
			"""



	def getSpeedValue(self, focusId):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		print 'mSpeed[%s]'% self.mSpeed
		ret = 0
		if focusId == self.ctrlBtnRewind.getId():

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

		elif focusId == self.ctrlBtnForward.getId():
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
		

	@run_async
	def updateLocalTime(self):
		print '[%s():%s]begin_start thread'% (currentframe().f_code.co_name, currentframe().f_lineno)
		#print 'untilThread[%s] self.progress_max[%s]' % (self.untilThread, self.progress_max)

		loop = 0
		rLock = threading.RLock()
		while self.untilThread:
			#print '[%s():%s]repeat'% (currentframe().f_code.co_name, currentframe().f_lineno)

			#local clock
			rLock.acquire()
			if  ( loop % 10 ) == 0 :

				isExcept = False
				try:
					ret = self.commander.datetime_GetLocalTime( )
					localTime = int( ret[0] )

				except Exception, e:
					print 'Error e[%s] datetime_GetLocalTime()'% e
					isExcept = True
					rLock.release()

				#local clock
				if isExcept == False :
					rLock.release()
					ret = epgInfoClock(2, localTime, loop)
					self.ctrlEventClock.setLabel(ret[0])


			#progress
			if self.isPlay == True:
				if self.mSpeed != 100:
					self.initTimeShift()
				if self.progress_max > 0:
					try :
						print 'progress_idx[%s] getPercent[%s]' % (self.progress_idx, self.ctrlProgress.getPercent())

						self.ctrlProgress.setPercent(self.progress_idx)

						pastTime = self.timeshift_curTime + self.curTime

						self.progress_idx = ( pastTime / self.progress_max * 100)
						if self.progress_idx > 100:
							self.progress_idx = 100

						if pastTime > self.progress_max :
							pastTime = self.progress_max
							self.initTimeShift()

						ret = epgInfoClock(4, pastTime, 0)
						self.ctrlBtnCurrent.setLabel(ret)

						posx = int (self.progress_idx * self.progressbarWidth / 100)
						self.ctrlBtnCurrent.setPosition( posx, 25 )

					except Exception, e :
						print 'Error Exception[%s] progress'% e

					self.curTime += 1
					#print 'posx[%s] [%s] [%s]'% (posx, pastTime, pastTime/self.progress_max)

				else:
					print 'value error progress_max[%s]' % self.progress_max

			else:
				pass

			loop += 1
			time.sleep(1)

		print '[%s():%s]leave_end thread'% (currentframe().f_code.co_name, currentframe().f_lineno)


	def updateServiceType(self, tvType):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'serviceType[%s]' % tvType


			

	def showEPGDescription(self, focusid, event):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		
		
		

