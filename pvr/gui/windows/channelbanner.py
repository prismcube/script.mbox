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
from inspect import currentframe

import pvr.elismgr
from pvr.net.net import EventRequest
#from pvr.net.net import EventServer, EventHandler, EventRequest

#from threading import Thread
import threading
import logging

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

		#push push test test

		#time track
		#from threading import Thread
		self.timeTrack = threading.Thread(target = self.func_Progress)
		self.untilThread = True

	def __del__(self):
		print '[%s():%s] destroyed ChannelBanner'% (currentframe().f_code.co_name, currentframe().f_lineno)

		# end thread func_progress()
		self.untilThread = False

	def onInit(self):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		if not self.win:
			self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())

		#get channel
		self.currentChannel = self.commander.channel_GetCurrent()

		#get event
		#request = EventRequest(self)

		self.ctrlChannelNumber = self.getControl( 600 )
		self.ctrlChannelName = self.getControl( 601 )
		self.ctrlEventName = self.getControl( 703 )
		self.ctrlEventStartTime = self.getControl( 704 )
		self.ctrlEventEndTime = self.getControl( 705 )

		self.ctrlProgress = self.getControl(707)
		#self.ctrlProgress = xbmcgui.ControlProgress(100, 250, 125, 75)
		#self.ctrlProgress(self.Progress)
		self.ctrlProgress.setPercent(0)
		self.progress_idx = 0
		self.progress_max = 0
		

		print 'currentChannel[%s]' % self.currentChannel
		if( self.currentChannel[0] == 'NULL' ) :
			print 'has no channel'
		
			# todo 
			# show message box : has no channnel
		else :
			print 'ChannelBanner #3'		
			self.ctrlChannelNumber.setLabel( self.currentChannel[1] )
			self.ctrlChannelName.setLabel( self.currentChannel[2] )
			self.ctrlEventName.setLabel('')
			self.ctrlEventStartTime.setLabel('00:00')
			self.ctrlEventEndTime.setLabel('00:00')

			print '[%s():%s]start thread, func_progress()'% (currentframe().f_code.co_name, currentframe().f_lineno)
			self.timeTrack.start()

		"""
		stbTime_GMT    = self.commander.datetime_GetGMTTime()
		stbTime_offset = self.commander.datetime_GetLocalOffset()
		stbTime_local  = self.commander.datetime_GetLocalTime()
		print 'GMT    time[%s]' % stbTime_GMT
		print 'offset time[%s]' % stbTime_offset
		print 'local  time[%s]' % stbTime_local
		print '%s' % time.strftime('%a, %d.%m.%Y %I:%M', time.gmtime(int(stbTime_GMT[0])) )
		print '%s' % time.strftime('%a, %d.%m.%Y %I:%M', time.gmtime(int(stbTime_offset[0])) )
		print '%s' % time.strftime('%a, %d.%m.%Y %I:%M', time.gmtime(int(stbTime_local[0])) )
		"""

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

			# end thread func_progress()
			self.untilThread = False

		else:
			print 'youn check action unknown id=%d' % id


	def onClick(self, controlId):
		print "onclick(): control %d" % controlId
		

	def onFocus(self, controlId):
		print "onFocus(): control %d" % controlId

	def onEvent(self, event):
		print 'ChannelBanner =%s' %event

		if not event[2]:		
			self.ctrlEventName.setLabel('no name')
		else:
			self.ctrlEventName.setLabel(event[2])

		if not event[6]: pass
		else:
			print 'event6[%s] event7[%s]'% (event[6], event[7])
			self.func_timeData(int(event[6]), int(event[7]))
			self.progress_max = int(event[7])
	

	def func_timeData(self, startTime, duration):
		print '<<<<<<<< startTime[%s] duration[%s]'% (startTime, duration)

		# How about slowly time(West) at localoffset...? 
		timezone_sec = self.commander.datetime_GetLocalOffset()

		startTime_hh = time.strftime('%H', time.gmtime(startTime + int(timezone_sec[0])) )
		startTime_mm = time.strftime('%M', time.gmtime(startTime + int(timezone_sec[0])) )
		endTime_hh = time.strftime('%H', time.gmtime((startTime+duration) + int(timezone_sec[0])) )
		endTime_mm = time.strftime('%M', time.gmtime((startTime+duration) + int(timezone_sec[0])) )

		str_startTime = str ('%02s:%02s'% (startTime_hh,startTime_mm) )
		str_endTime = str ('%02s:%02s'% (endTime_hh,endTime_mm) )

		self.ctrlEventStartTime.setLabel(str_startTime)
		self.ctrlEventEndTime.setLabel(str_endTime)

	def func_Progress(self):
		print '[%s():%s] <<<< begin'% (currentframe().f_code.co_name, currentframe().f_lineno)
		while self.untilThread:
			#select.select([self.progress_start], [], [], 0.5 )
#			if self.progress_max:

			print 'progress_max[%s]'% self.progress_max


			print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
			print self.ctrlProgress.getPercent()
			print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

			print 'progress_idx[%s]' % self.progress_idx
			self.ctrlProgress.setPercent(self.progress_idx)

			self.progress_idx += 10  #(self.progress_max / 100)
			if self.progress_idx > 100:
				self.progress_idx = 100


			time.sleep(10)
			print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		


