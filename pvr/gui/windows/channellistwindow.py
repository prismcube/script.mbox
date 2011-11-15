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

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import BaseWindow, setWindowBusy
from pvr.gui.basewindow import Action
from pvr.elisevent import ElisEnum
from inspect import currentframe
from pvr.util import catchall, is_digit, run_async, epgInfoTime, epgInfoClock, epgInfoComponentImage
import pvr.elismgr

import thread, time


class ChannelListWindow(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance().getCommander()		

		self.eventBus = pvr.elismgr.getInstance().getEventBus()
		self.eventBus.register( self )
		self.mutex = thread.allocate_lock()

		self.currentChannel = -1
		self.channelList = []
		self.listItems = []
		self.commander.channel_GetList( ElisEnum.E_TYPE_TV, ElisEnum.E_MODE_ALL, ElisEnum.E_SORT_BY_DEFAULT, self.channelList )

		for ch in self.channelList:
			listItem = xbmcgui.ListItem("%04d %s"%( int(ch[0]), ch[2]),"-", "-", "-", "-")
			self.listItems.append(listItem)


	def __del__(self):
		print '[%s():%s] destroyed ChannelBanner'% (currentframe().f_code.co_name, currentframe().f_lineno)

		# end thread updateEPGProgress()
		self.untilThread = False


	def onInit(self):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		if not self.win:
			self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())

		self.ctrlEventClock     = self.getControl( 103 )
		self.ctrlChannelName    = self.getControl( 303 )
		self.ctrlEventName      = self.getControl( 304 )
		self.ctrlEventTime      = self.getControl( 305 )
		self.ctrlProgress       = self.getControl( 306 )
		self.ctrlSateliteInfo   = self.getControl( 307 )
		self.ctrlCareerInfo     = self.getControl( 308 )
		self.ctrlServiceTypeImg1= self.getControl( 310 )
		self.ctrlServiceTypeImg2= self.getControl( 311 )
		self.ctrlServiceTypeImg3= self.getControl( 312 )
		
		self.ctrlSelectItem     = self.getControl( 401 )

		self.listcontrol        = self.getControl( 50 )
		self.listcontrol.addItems( self.listItems )

		self.currentChannelInfo = self.commander.channel_GetCurrent()
		self.currentChannel = int(self.currentChannelInfo[0])

		#detected to last focus
		chindex = 0;
		if self.currentChannel > 0 :
			for ch in self.channelList:
				if int(ch[0]) == self.currentChannel :
					break
				chindex += 1

			self.listcontrol.selectItem( chindex )


		self.imgData  = 'channelbanner/data.png'
		self.imgDolby = 'channelbanner/dolbydigital.png'
		self.imgHD    = 'channelbanner/OverlayHD.png'
		self.ctrlEventClock.setLabel('')
		self.initLabelInfo()

		#run thread
		self.untilThread = True
		self.updateLocalTime()


	def onAction(self, action):
 		
		id = action.getId()
		
		if id == Action.ACTION_PREVIOUS_MENU:
			print 'ChannelListWindow lael98 check action menu'
		elif id == Action.ACTION_SELECT_ITEM:
			print '<<<<< test youn: action ID[%s]' % id
			print 'tv_guide_last_selected[%s]' % action.getId()
			
		elif id == Action.ACTION_PARENT_DIR:
			print 'lael98 check ation back'
			winmgr.getInstance().showWindow( winmgr.WIN_ID_NULLWINDOW )	

			self.listcontrol.reset()

		else: print'Unconsumed key: %s' % action.getId()


	def onClick(self, controlId):
		print "ChannelListWindow onclick(): control %d" % controlId	
		if controlId == self.listcontrol.getId() :
			label = self.listcontrol.getSelectedItem().getLabel()
			channelNumbr = int(label[:4])
			ret = self.commander.channel_SetCurrent( channelNumbr )

			if ret[0].upper() == 'TRUE' :
				if self.currentChannel == channelNumbr :
					self.untilThread = False
					winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_BANNER )

				self.currentChannel = channelNumbr
				self.currentChannelInfo = self.commander.channel_GetCurrent()

			self.ctrlSelectItem.setLabel(str('%s / %s'% (self.listcontrol.getSelectedPosition() + 1, len(self.listItems))) )
			self.initLabelInfo()

	def onFocus(self, controlId):
		print "onFocus(): control %d" % controlId


	def onEvent(self, event):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno),
		print 'event[%s]'% event
		
		if xbmcgui.getCurrentWindowId() == 13002 :
			self.updateLabelInfo(event)
		else:
			print 'show screen is another windows page[%s]'% xbmcgui.getCurrentWindowId()
		


	def initLabelInfo(self):
		print 'currentChannel[%s]' % self.currentChannel
		
		if( self.currentChannelInfo != [] ) :

			self.ctrlProgress.setPercent(0)
			self.ctrlProgress.setVisible(False)
			self.progress_idx = 0.0
			self.progress_max = 0.0

			self.ctrlSelectItem.setLabel(str('%s / %s'% (self.listcontrol.getSelectedPosition() + 1, len(self.listItems))) )
			self.ctrlChannelName.setLabel('')
			self.ctrlEventName.setLabel('')
			self.ctrlEventTime.setLabel('')
			self.ctrlSateliteInfo.setLabel('')
			self.ctrlCareerInfo.setLabel('')
			self.ctrlServiceTypeImg1.setImage('')
			self.ctrlServiceTypeImg2.setImage('')
			self.ctrlServiceTypeImg3.setImage('')

			self.updateLabelInfo([])
			#self.currentChannelInfo = []

		else:
			print 'has no channel'
		
			# todo 
			# show message box : has no channnel


	def updateServiceType(self, tvType):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'serviceType[%s]' % tvType


		if tvType == ElisEnum.E_TYPE_TV:
			return 'TV'
		elif tvType == ElisEnum.E_TYPE_RADIO:pass
		elif tvType == ElisEnum.E_TYPE_DATA:pass
		else:
			return 'etc'
			print 'unknown ElisEnum tvType[%s]'% tvType

	def updateLabelInfo(self, event):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'ch info[%s]'% self.currentChannelInfo

		if self.currentChannelInfo != []:
			self.epgClock = self.commander.datetime_GetLocalTime()

			if is_digit(self.currentChannelInfo[3]):
				serviceType = int(self.currentChannelInfo[3])
				ret = self.updateServiceType(serviceType)
				if ret != None:
					self.ctrlChannelName.setLabel( str('%s - %s'% (ret, self.currentChannelInfo[2])) )


		if event != []:
			#update epgName uiID(304)
			self.ctrlEventName.setLabel(event[2])

			#update epgTime uiID(305)
			if is_digit(event[7]):
				self.progress_max = int(event[7])
				print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

				if is_digit(event[6]):
					timeZone = self.commander.datetime_GetLocalOffset()
					ret = epgInfoTime(timeZone[0], int(event[6]), int(event[7]))
					print 'epgInfoTime[%s]'% ret
					if ret != []:
						self.ctrlEventTime.setLabel(str('%s%s'% (ret[0], ret[1])))

				else:
					print 'value error EPGTime start[%s]' % event[6]
			else:
				print 'value error EPGTime duration[%s]' % event[7]

			#visible progress
			self.ctrlProgress.setVisible(True)

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


		#self.ctrlSateliteInfo.setLabel()
		#self.ctrlCareerInfo.setLabel()


		list_ = []
		#ret = self.commander.satellite_GetConfiguredList(0, list_)
		#ret = self.commander.satellite_GetList(0, list_)
		#ret = self.commander.satellite_GetByChannelNumber(int(self.currentChannelInfo[0]), int(self.currentChannelInfo[3]))
		#ret = self.commander.satelliteconfig_GetList(0, list_)
		ret = self.commander.satellite_Get(192, 1)
		print 'ret[%s] list_[%s]'% (ret, list_)


	@run_async
	def updateLocalTime(self):
		print '[%s():%s]begin_start thread'% (currentframe().f_code.co_name, currentframe().f_lineno)

		nowTime = time.time()
		while self.untilThread:
			print '[%s():%s]repeat <<<<'% (currentframe().f_code.co_name, currentframe().f_lineno)

			#progress
			if self.progress_max > 0:
				print 'progress_idx[%s] getPercent[%s]' % (self.progress_idx, self.ctrlProgress.getPercent())

				self.ctrlProgress.setPercent(self.progress_idx)

				self.progress_idx += 100.0 / self.progress_max
				if self.progress_idx > 100:
					self.progress_idx = 100
			else:
				print 'value error progress_max[%s]' % self.progress_max


			#local clock
			if is_digit(self.epgClock[0]):
				ret = epgInfoClock(1, nowTime, int(self.epgClock[0]))
				self.ctrlEventClock.setLabel(ret)

			else:
				print 'value error epgClock[%s]' % ret

			time.sleep(1)

		print '[%s():%s]leave_end thread'% (currentframe().f_code.co_name, currentframe().f_lineno)

