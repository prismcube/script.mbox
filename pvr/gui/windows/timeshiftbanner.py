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
import thread

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
		self.eventBus.register( self )
		self.commander = pvr.elismgr.getInstance().getCommander()

		self.currentChannel=[]
		self.progress_idx = 0.0
		self.progress_max = 0.0

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
		print "onclick(): control %d" % controlId

		if controlId >= self.ctrlBtnRewind.getId() and controlId <= self.ctrlBtnForward.getId() :
			self.timeshiftAction(controlId)
		
			ret = self.commander.player_GetStatus()
			print 'player_status[%s]'% ret

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
		self.eventCopy = event

		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		#print 'eventCopy[%s]'% self.eventCopy

		if xbmcgui.getCurrentWindowId() == self.win : #13009
			self.updateONEvent(self.eventCopy)
		else:
			print 'show screen is another windows page[%s]'% xbmcgui.getCurrentWindowId()


	def timeshiftAction(self, focusId):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)		

		if focusId == self.ctrlBtnPlay.getId():
			ret = self.commander.player_Pause()

			self.isPlay = True
			self.ctrlBtnPlay.setVisible(False)
			self.ctrlBtnPause.setVisible(True)

		elif focusId == self.ctrlBtnPause.getId():
			ret = self.commander.player_Resume()

			self.isPlay = False
			self.ctrlBtnPlay.setVisible(True)
			self.ctrlBtnPause.setVisible(False)

		elif focusId == self.ctrlBtnStop.getId():
			self.ctrlProgress.setPercent(0)
			self.progress_idx = 0.0
			self.progress_max = 0.0

			ret = self.commander.player_Stop()

			self.untilThread = False
			self.updateLocalTime().join()
			self.close( )

			winmgr.getInstance().showWindow( winmgr.WIN_ID_NULLWINDOW )

		elif focusId == self.ctrlBtnRewind.getId():
			pass
			#get speed
			#ret = self.commander.player_SetSpeed()
			#self.initTimeShift()

		elif focusId == self.ctrlBtnForward.getId():
			pass
			#get speed
			#ret = self.commander.player_SetSpeed()
			#self.initTimeShift()

	def updateONEvent(self, event):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'event[%s]'% event


	def initLabelInfo(self):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'currentChannel[%s]' % self.currentChannel
		
		# todo 
		self.eventCopy = []
		#self.ctrlLblTSStartTime.setLabel('')
		self.ctrlLblTSEndTime.setLabel('')

		self.epgClock = []
		self.epgClock = self.commander.datetime_GetLocalTime()
		print 'epgClock[%s]'% self.epgClock

		self.initTimeShift()

	def initTimeShift(self) :
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		ret = []
		ret = self.commander.player_GetStatus()
		#todo, pending status
		self.curTime = 0
		self.timeshift_curTime = 0.0
		self.timeshift_endTime = 0.0
		"""
		if pendingStatus == True :
			self.ctrlBtnPlay.setVisible(False)
			self.ctrlBtnPause.setVisible(True)

		else:
			self.ctrlBtnPlay.setVisible(True)
			self.ctrlBtnPause.setVisible(False)
		"""
		if ret != []:
			self.timeshift_curTime = int(ret[4]) / 1000.0
			self.timeshift_endTime = int(ret[5]) / 1000.0
			#self.timeshift_curTime = 0.0
			#self.timeshift_endTime = 50
			

		ret = ''
		ret = epgInfoClock(4, 0, self.timeshift_endTime)
		self.ctrlLblTSEndTime.setLabel(ret)

		self.progress_max = self.timeshift_endTime

	@run_async
	def updateLocalTime(self):
		print '[%s():%s]begin_start thread'% (currentframe().f_code.co_name, currentframe().f_lineno)
		#print 'untilThread[%s] self.progress_max[%s]' % (self.untilThread, self.progress_max)

		nowTime = time.time()
		while self.untilThread:
			#print '[%s():%s]repeat'% (currentframe().f_code.co_name, currentframe().f_lineno)

			#local clock
			if self.epgClock != [] :
				if is_digit(self.epgClock[0]):
					ret = epgInfoClock(3, nowTime, int(self.epgClock[0]))
					self.ctrlEventClock.setLabel(ret[0])

				else:
					print 'value error epgClock[%s]' % ret

			#progress
			if self.isPlay == True:
				if self.progress_max > 0:
					print 'progress_idx[%s] getPercent[%s]' % (self.progress_idx, self.ctrlProgress.getPercent())

					self.ctrlProgress.setPercent(self.progress_idx)

					pastTime = self.timeshift_curTime + self.curTime

					self.progress_idx = ( pastTime / self.progress_max * 100)
					if self.progress_idx > 100:
						self.progress_idx = 100

					if pastTime > self.progress_max :
						pastTime = self.progress_max
					ret = epgInfoClock(4, 0, pastTime)
					self.ctrlBtnCurrent.setLabel(ret)

					posx = int (self.progress_idx * 650 / 100)
					self.ctrlBtnCurrent.setPosition( posx, 25 )
					self.curTime += 1

					print 'posx[%s] [%s] [%s]'% (posx, pastTime, pastTime/self.progress_max)
				else:
					print 'value error progress_max[%s]' % self.progress_max
			else:
				pass

			time.sleep(1)

		print '[%s():%s]leave_end thread'% (currentframe().f_code.co_name, currentframe().f_lineno)


	def updateServiceType(self, tvType):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'serviceType[%s]' % tvType


			

	def showEPGDescription(self, focusid, event):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		
		
		

