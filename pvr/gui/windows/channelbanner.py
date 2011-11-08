#
#  MythBox for XBMC - http://mythbox.googlecode.com
#  Copyright (C) 2011 analogue@yahoo.com
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
import xbmc
import xbmcgui
import sys
import time

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import BaseWindow
from pvr.gui.basewindow import Action

import pvr.elismgr
from pvr.elisevent import ElisAction, ElisEnum
from pvr.net.net import EventRequest

#from threading import Thread
from pvr.util import run_async, is_digit, Mutex #, synchronized, sync_instance
import thread

#debug log
import logging
from inspect import currentframe

log = logging.getLogger('mythbox.ui')
mlog = logging.getLogger('mythbox.method')


class ChannelBanner(BaseWindow):
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

		self.mutex = thread.allocate_lock()


		#push push test test

		#time track
		#from threading import Thread
		#self.timeTrack = threading.Thread(target = self.updateEPGProgress)
		self.untilThread = True

	def __del__(self):
		print '[%s():%s] destroyed ChannelBanner'% (currentframe().f_code.co_name, currentframe().f_lineno)

		# end thread updateEPGProgress()
		self.untilThread = False

	def onInit(self):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		if not self.win:
			self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())

		#get channel
		self.currentChannel = self.commander.channel_GetCurrent()
		self.oldCh = self.currentChannel[0]

		#get event
		#request = EventRequest(self)
		self.ctrlChannelNumber  = self.getControl( 600 )
		self.ctrlChannelName    = self.getControl( 601 )
		self.ctrlServiceTypeImg1= self.getControl( 603 )
		self.ctrlServiceTypeImg2= self.getControl( 604 )
		self.ctrlServiceTypeImg3= self.getControl( 605 )
		self.ctrlEventClock     = self.getControl( 610 )
		self.ctrlEventName      = self.getControl( 703 )
		self.ctrlEventStartTime = self.getControl( 704 )
		self.ctrlEventEndTime   = self.getControl( 705 )

		self.ctrlProgress = self.getControl(707)
		#self.ctrlProgress = xbmcgui.ControlProgress(100, 250, 125, 75)
		#self.ctrlProgress(self.Progress)

		self.ctrlEventClock.setLabel('')
		self.updateChannelLabel()

	
		#run thread
		self.updateEPGProgress()

		self.imgData  = 'channelbanner\data.png'
		self.imgDolby = 'channelbanner\dolbydigital.png'
		self.imgHD    = 'channelbanner\OverlayHD.png'
		


	def onAction(self, action):
		id = action.getId()
		
		if id == Action.ACTION_PREVIOUS_MENU:
			print 'youn check action menu'

		elif id == Action.ACTION_SELECT_ITEM:
			print '<<<<< test youn: ID[%s]' % id
			log.debug('youn:%s' % id)

	
		elif id == Action.ACTION_PARENT_DIR:
			print 'youn check ation back'
			winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_LIST_WINDOW )
#			winmgr.getInstance().showWindow( winmgr.WIN_ID_NULLWINDOW )
#			winmgr.shutdown()

			# end thread updateEPGProgress()
			self.untilThread = False

		elif id == Action.ACTION_MOVE_DOWN:
			print 'onAction():ACTION_NEXT_ITEM control %d' % id
			next_ch = self.commander.channel_GetNext()
			print 'next_ch[%s]' % next_ch

			channelNumber = next_ch[0]
			if is_digit(channelNumber):
				ret = self.commander.channel_SetCurrent( int(channelNumber) )

				if ret[0].upper() == 'TRUE' :
					self.currentChannel = self.commander.channel_GetCurrent()
					self.updateChannelLabel()
					self.oldCh = channelNumber
			else:
				print 'No Channel next_ch[%s]'% next_ch

			if is_digit(next_ch[3]):
				self.updateServiceType(int(next_ch[3]))



		elif id == Action.ACTION_MOVE_UP:
			print 'onAction():ACTION_PREV_ITEM control %d' % id
			priv_ch = self.commander.channel_GetPrev()
			print 'priv_ch[%s]' % priv_ch

			channelNumber = priv_ch[0]
			if is_digit(channelNumber):
				ret = self.commander.channel_SetCurrent( int(channelNumber) )

				if ret[0].upper() == 'TRUE' :
					self.currentChannel = self.commander.channel_GetCurrent()
					self.updateChannelLabel()
			else:
				print 'No Channel priv_ch[%s]'% priv_ch

			if is_digit(priv_ch[3]):
				self.updateServiceType(int(priv_ch[3]))


		else:
			print 'youn check action unknown id=%d' % id


	def onClick(self, controlId):
		print "onclick(): control %d" % controlId
		

	def onFocus(self, controlId):
		print "onFocus(): control %d" % controlId

	def onEvent(self, event):
		eventCopy = event

		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'eventCopy[%s]'% eventCopy

		"""
		while 1:
			if self.mutex.locked() == True:
				time.sleep(0.1)
				continue
			else:
				break
		"""
		if self.mutex.locked() == False:
			self.updateONEvent(eventCopy)

	def updateONEvent(self, event):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'event[%s]' %event
		
		if not event[2]:		
			self.ctrlEventName.setLabel('no name')
		else:
			self.ctrlEventName.setLabel(event[2])
			print 'event6[%s] event7[%s]'% (event[6], event[7])

			if is_digit(event[7]):
				self.progress_max = int(event[7])
				print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

				if is_digit(event[6]):
					self.updateEPGTime(int(event[6]), int(event[7]))
					print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
				else:
					print 'value error EPGTime start[%s]' % event[6]
			else:
				print 'value error EPGTime duration[%s]' % event[7]


	def updateEPGTime(self, startTime, duration):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		# How about slowly time(West) at localoffset...? 
		"""
		while 1:
			if self.mutex.locked() == False:
				self.mutex.acquire()
				print 'acquire, locked[%s]'% self.mutex.locked()
				timeZone = self.commander.datetime_GetLocalOffset()
				self.mutex.release()
				print 'release, locked[%s]'% self.mutex.locked()
				break
			time.sleep(0.5)
		"""

		timeZone = self.commander.datetime_GetLocalOffset()
		
		print '========= startTime[%s] duration[%s] offset[%s]'% (startTime, duration, timeZone[0])

		localOffset = 0
		if (is_digit(timeZone[0]) == True):
			localOffset = int(timeZone[0])

		epgStartTime = startTime + localOffset
		epgEndTime =  startTime + duration + localOffset

		startTime_hh = time.strftime('%H', time.gmtime(epgStartTime) )
		startTime_mm = time.strftime('%M', time.gmtime(epgStartTime) )
		endTime_hh = time.strftime('%H', time.gmtime(epgEndTime) )
		endTime_mm = time.strftime('%M', time.gmtime(epgEndTime) )

		str_startTime = str ('%02s:%02s'% (startTime_hh,startTime_mm) )
		str_endTime = str ('%02s:%02s'% (endTime_hh,endTime_mm) )

		self.ctrlEventStartTime.setLabel(str_startTime)
		self.ctrlEventEndTime.setLabel(str_endTime)

		print 'epgStart[%s] epgEndTime[%s]'% (epgStartTime, epgEndTime)
		print 'epgStart[%s] epgEndTime[%s]'% (time.strftime('%x %X',time.gmtime(epgStartTime)), time.strftime('%x %X',time.gmtime(epgEndTime)) )
		print 'start[%s] end[%s]'%(str_startTime, str_endTime)
		print 'hh[%s] mm[%s] hh[%s] mm[%s]' % (startTime_hh, startTime_mm, endTime_hh, endTime_mm)

	@run_async
	def updateEPGProgress(self):
		print '[%s():%s]start thread <<<< begin'% (currentframe().f_code.co_name, currentframe().f_lineno)
		#print 'untilThread[%s] self.progress_max[%s]' % (self.untilThread, self.progress_max)

		while self.untilThread:
			print '[%s():%s]repeat <<<<'% (currentframe().f_code.co_name, currentframe().f_lineno)

			if self.progress_max > 0:
				print 'progress_idx[%s] getPercent[%s]' % (self.progress_idx, self.ctrlProgress.getPercent())

				self.ctrlProgress.setPercent(self.progress_idx)

				self.progress_idx += 100.0 / self.progress_max
				if self.progress_idx > 100:
					self.progress_idx = 100
			else:
				print 'value error progress_max[%s]' % self.progress_max


			print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
			
			time.sleep(1)

			self.updateLocalTime()
		

	def updateLocalTime(self):
		#from pvr.util import Mutex
		#tmux = Mutex()
		#tmux.lock()

		#self.mutex.acquire()
		#self.Mutex.acquire()

		print 'locked[%s]'% self.mutex.locked()
		if self.mutex.locked() == False:
			self.mutex.acquire()

			epgClock = self.commander.datetime_GetLocalTime()
			self.mutex.release()
		#self.Mutex.release()


			if is_digit(epgClock[0]):
				strClock = time.strftime('%a. %H:%M', time.gmtime(long(epgClock[0])) )
				self.ctrlEventClock.setLabel(strClock)
				print 'epgClock[%s]'% strClock
			else:
				print 'value error epgClock[%s]' % epgClock[0]


		#self.mutex.noti()
		#tmux.unlock()
		#l.release()


	def updateChannelLabel(self):
		print '[%s():%s] <<<< begin'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'currentChannel[%s]' % self.currentChannel

		
		if( self.currentChannel[0] == 'NULL' ) :
			print 'has no channel'
		
			# todo 
			# show message box : has no channnel
		else :

			self.ctrlProgress.setPercent(0)
			self.progress_idx = 0.0
			self.progress_max = 0.0

			self.ctrlChannelNumber.setLabel( self.currentChannel[1] )
			self.ctrlChannelName.setLabel( self.currentChannel[2] )
			self.ctrlEventName.setLabel('')
			self.ctrlEventStartTime.setLabel('00:00')
			self.ctrlEventEndTime.setLabel('00:00')

			self.ctrlServiceTypeImg1.setImage('')
			self.ctrlServiceTypeImg2.setImage('')
			self.ctrlServiceTypeImg3.setImage('')
			
			print '[%s():%s]Initialize Label'% (currentframe().f_code.co_name, currentframe().f_lineno)

	def updateServiceType(self, Type):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'serviceType[%s]' % Type

		if Type == ElisEnum.E_TYPE_DATA:
			self.ctrlServiceTypeImg1.setImage(self.imgData)
			
		elif Type == ElisEnum.E_mHasDolbyDigital:
			self.ctrlServiceTypeImg2.setImage(self.imgHD)

		elif Type == ElisEnum.E_HasHDVideo:
			self.ctrlServiceTypeImg3.setImage(self.imgDolby)

		else:
			print 'unknown ElisEnum Type[%s]'% Type
		

