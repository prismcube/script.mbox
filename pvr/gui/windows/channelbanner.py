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
from pvr.gui.basewindow import BaseWindow
from pvr.gui.basewindow import Action
from inspect import currentframe
import pvr.elismgr

import logging

log = logging.getLogger('mythbox.ui')
mlog = logging.getLogger('mythbox.method')


class ChannelBanner(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		print 'f_lineno[%d] co_filename[%s]' %(currentframe().f_lineno, currentframe().f_code.co_filename)    
		print 'args[0]=[%s]' % args[0]
		print 'args[1]=[%s]' % args[1]

		self.lastFocusId = None
		self.eventBus = pvr.elismgr.getInstance().getEventBus()
		self.eventBus.register( self )
		self.commander = pvr.elismgr.getInstance().getCommander()

		self.currentChannel=[]
		
		#push push test test

	def onInit(self):
		print 'ChannelBanner #0'	
		if not self.win:
			self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())

		self.currentChannel = self.commander.getCurrentChannel()

		self.ctrlChannelNumber = self.getControl( 600 )
		self.ctrlChannelName = self.getControl( 601 )
		self.ctrlEventName = self.getControl( 703 )

		print 'current channel[%s]' % self.currentChannel[0]
		print 'ChannelBanner #1'
		if( self.currentChannel[0] == 'NULL' ) :
			print 'has no channel'
			print 'ChannelBanner #2'			
			# todo 
			# show message box : has no channnel
		else :
			print 'ChannelBanner #3'		
			self.ctrlChannelNumber.setLabel( self.currentChannel[1] )
			self.ctrlChannelName.setLabel( self.currentChannel[2] )
			self.ctrlEventName.setLabel('no event')
		

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

		else:
			print 'youn check action unknown id=%d' % id

	def onClick(self, controlId):
		print "onclick(): control %d" % controlId

	def onFocus(self, controlId):
		print "onFocus(): control %d" % controlId

	def onEvent(self, event):
		print 'ChannelBanner =%s' %event


