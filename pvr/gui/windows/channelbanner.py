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
from pvr.util import run_async, is_digit, Mutex, epgInfoTime, epgInfoClock, epgInfoComponentImage, GetSelectedLongitudeString #, synchronized, sync_instance
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

		#push push test test

		#time track
		#from threading import Thread
		#self.timeTrack = threading.Thread(target = self.updateLocalTime)

	def __del__(self):
		print '[%s():%s] destroyed ChannelBanner'% (currentframe().f_code.co_name, currentframe().f_lineno)

		# end thread updateLocalTime()
		self.untilThread = False

	def onInit(self):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		if not self.win:
			self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())

			#get event
			#request = EventRequest(self)
			self.ctrlChannelNumber  = self.getControl( 601 )
			self.ctrlChannelName    = self.getControl( 602 )
			self.ctrlServiceType    = self.getControl( 603 )
			self.ctrlServiceTypeImg1= self.getControl( 604 )
			self.ctrlServiceTypeImg2= self.getControl( 605 )
			self.ctrlServiceTypeImg3= self.getControl( 606 )
			self.ctrlEventClock     = self.getControl( 610 )
			self.ctrlLongitudeInfo  = self.getControl( 701 )
			self.ctrlEventName      = self.getControl( 703 )
			self.ctrlEventStartTime = self.getControl( 704 )
			self.ctrlEventEndTime   = self.getControl( 705 )
			self.ctrlProgress       = self.getControl( 707 )
			self.ctrlEventDescGroup = self.getControl( 800 )
			self.ctrlEventDescText1 = self.getControl( 801 )
			self.ctrlEventDescText2 = self.getControl( 802 )
			#self.ctrlProgress = xbmcgui.ControlProgress(100, 250, 125, 75)
			#self.ctrlProgress(self.Progress)

			self.imgTV    = 'tv.png'
			self.toggleFlag=False
			self.ctrlEventClock.setLabel('')

		#get channel
		self.currentChannel = self.commander.channel_GetCurrent()

		self.initLabelInfo()
	
		if is_digit(self.currentChannel[3]):
			self.updateServiceType(int(self.currentChannel[3]))


		#run thread
		self.untilThread = True
		self.updateLocalTime()

		#get epg event right now, as this windows open
		ret = []
		ret=self.commander.epgevent_GetPresent()
		if ret != []:
			self.eventCopy=['epgevent_GetPresent'] + ret
			self.updateONEvent(self.eventCopy)
		print 'epgevent_GetPresent[%s]'% self.eventCopy


	def onAction(self, action):
		id = action.getId()
		
		if id == Action.ACTION_PREVIOUS_MENU:
			print 'youn check action menu'

		elif id == Action.ACTION_SELECT_ITEM:
			print '<<<<< test youn: ID[%s]' % id
			log.debug('youn:%s' % id)
			self.showEPGDescription(self.eventCopy)

	
		elif id == Action.ACTION_PARENT_DIR:
			print 'youn check ation back'

			# end thread updateLocalTime()
			self.untilThread = False
			self.updateLocalTime().join()

			winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_LIST_WINDOW )
#			winmgr.getInstance().showWindow( winmgr.WIN_ID_NULLWINDOW )
#			winmgr.shutdown()


		elif id == Action.ACTION_MOVE_DOWN:
			print 'onAction():ACTION_NEXT_ITEM control %d' % id
			next_ch = self.commander.channel_GetNext()
			print 'next_ch[%s]' % next_ch

			channelNumber = next_ch[0]
			if is_digit(channelNumber):
				ret = self.commander.channel_SetCurrent( int(channelNumber) )

				if ret[0].upper() == 'TRUE' :
					self.currentChannel = self.commander.channel_GetCurrent()
					self.initLabelInfo()

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
					self.initLabelInfo()

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
		self.eventCopy = event

		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		#print 'eventCopy[%s]'% self.eventCopy

		if xbmcgui.getCurrentWindowId() == 13003 :
			self.updateONEvent(self.eventCopy)
		else:
			print 'show screen is another windows page[%s]'% xbmcgui.getCurrentWindowId()


	def updateONEvent(self, event):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'event[%s]'% event

		if event != []:
			#epg name
			if event[2] != '':
				print '[%s():%s]%s'% (currentframe().f_code.co_name, currentframe().f_lineno,event[2])
				try:
					self.ctrlEventName.setLabel(event[2])
				except Exception, ex:
					print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
					print 'CATCHALL_UI: Caught  exception %s' % str(ex)
			else:
				self.ctrlEventName.setLabel('')

			#epg time
			if is_digit(event[7]):
				self.progress_max = int(event[7])

				if is_digit(event[6]):
					timeZone = self.commander.datetime_GetLocalOffset()
					ret = epgInfoTime(timeZone[0], int(event[6]), int(event[7]))
					if ret != []:
						print 'ret[%s]'% ret
						self.ctrlEventStartTime.setLabel(ret[0])
						self.ctrlEventEndTime.setLabel(ret[1])
				
					print 'event6[%s] event7[%s]'% (event[6], event[7])
				else:
					print 'value error EPGTime start[%s]' % event[6]
			else:
				print 'value error EPGTime duration[%s]' % event[7]

			#component
			ret = epgInfoComponentImage(int(event[9]))
			if len(ret) == 1:
				self.ctrlServiceTypeImg1.setImage(ret[0])
			elif len(ret) == 2:
				self.ctrlServiceTypeImg1.setImage(ret[0])
				self.ctrlServiceTypeImg2.setImage(ret[1])
			elif len(ret) == 3:
				self.ctrlServiceTypeImg1.setImage(ret[0])
				self.ctrlServiceTypeImg2.setImage(ret[1])
				self.ctrlServiceTypeImg3.setImage(ret[2])
			else:
				self.ctrlServiceTypeImg1.setImage('')
				self.ctrlServiceTypeImg2.setImage('')
				self.ctrlServiceTypeImg3.setImage('')

		else:
			print 'event null'

	@run_async
	def updateLocalTime(self):
		print '[%s():%s]start thread <<<< begin'% (currentframe().f_code.co_name, currentframe().f_lineno)
		#print 'untilThread[%s] self.progress_max[%s]' % (self.untilThread, self.progress_max)

		nowTime = time.time()
		while self.untilThread:
			print '[%s():%s]repeat'% (currentframe().f_code.co_name, currentframe().f_lineno)

			#progress
			if self.progress_max > 0:
				print 'progress_idx[%s] getPercent[%s]' % (self.progress_idx, self.ctrlProgress.getPercent())

				self.ctrlProgress.setPercent(self.progress_idx)

				self.progress_idx += 100.0 / self.progress_max
				if self.progress_idx > 100:
					self.progress_idx = 100
			else:
				print 'value error progress_max[%s]' % self.progress_max


			print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

			#local clock
			if is_digit(self.epgClock[0]):
				ret = epgInfoClock(2, nowTime, int(self.epgClock[0]))
				self.ctrlEventClock.setLabel(ret[0])

			else:
				print 'value error epgClock[%s]' % ret
			
			time.sleep(1)

		print '[%s():%s]end thread <<<< begin'% (currentframe().f_code.co_name, currentframe().f_lineno)

	def initLabelInfo(self):
		print '[%s():%s]Initialize Label'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'currentChannel[%s]' % self.currentChannel
		
		if( self.currentChannel != [] ) :

			self.ctrlProgress.setPercent(0)
			self.progress_idx = 0.0
			self.progress_max = 0.0
			self.eventCopy = []
			self.toggleFlag= False

			self.ctrlChannelNumber.setLabel( self.currentChannel[1] )
			self.ctrlChannelName.setLabel( self.currentChannel[2] )
			self.ctrlLongitudeInfo.setLabel('')
			self.ctrlEventName.setLabel('')
			self.ctrlEventStartTime.setLabel('')
			self.ctrlEventEndTime.setLabel('')

			self.ctrlServiceType.setImage('')
			self.ctrlServiceTypeImg1.setImage('')
			self.ctrlServiceTypeImg2.setImage('')
			self.ctrlServiceTypeImg3.setImage('')
			self.ctrlEventDescGroup.setVisible(False)
			self.ctrlEventDescText1.reset()
			self.ctrlEventDescText2.reset()

			self.epgClock = self.commander.datetime_GetLocalTime()
			
			longitude = self.commander.satellite_GetByChannelNumber(int(self.currentChannel[0]), int(self.currentChannel[3]))
			ret = GetSelectedLongitudeString(longitude)
			self.ctrlLongitudeInfo.setLabel(ret)


		else:
			print 'has no channel'
		
			# todo 
			# show message box : has no channnel


	def updateServiceType(self, tvType):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'serviceType[%s]' % tvType


		if tvType == ElisEnum.E_TYPE_TV:
			self.ctrlServiceType.setImage(self.imgTV)
		elif tvType == ElisEnum.E_TYPE_RADIO:pass
		elif tvType == ElisEnum.E_TYPE_DATA:pass
		else:
			self.ctrlServiceType.setImage('')
			print 'unknown ElisEnum tvType[%s]'% tvType


			

	def showEPGDescription(self, event):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		if event != []:
			print '[%s][%s][%s][%s][%s]' % (event[1], event[3], event[4], event[5], event[6])
			msgDescription = self.commander.epgevent_GetDescription(
							int(event[1]), #eventId
							int(event[3]), #sid
							int(event[4]), #tsid
							int(event[5]), #onid
							int(event[6])) #startTime

			print 'msgDescription[%s]' % msgDescription

			if msgDescription[0] != 'NULL':
				msg = msgDescription[1]
			else:
				print 'No value Description  \'NULL\''
				msg = ''

			self.ctrlEventDescText1.setText(event[2])
			self.ctrlEventDescText2.setText(msg)

		else:
			print 'event is None'
			self.ctrlEventDescText1.setText('')
			self.ctrlEventDescText2.setText('')

		if self.toggleFlag == True:
			self.ctrlEventDescText1.reset()
			self.ctrlEventDescText2.reset()
			self.ctrlEventDescGroup.setVisible(False)
			self.toggleFlag = False
		else:
			self.ctrlEventDescGroup.setVisible(True)
			self.toggleFlag = True
			
		
		#self.ctrlEventDescription.setVisibleCondition('[Control.IsVisible(100)]',True)
		#self.ctrlEventDescription.setEnabled(True)
		

