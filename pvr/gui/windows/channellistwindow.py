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

import logging

log = logging.getLogger('mythbox.ui')
mlog = logging.getLogger('mythbox.method')


class ChannelListWindow(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		print 'lael98 check %d %s' %(currentframe().f_lineno, currentframe().f_code.co_filename)    
		print 'args=%s' % args[0]


	def onInit(self):
		if not self.win:
			self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
		
		self.listcontrol = self.getControl( 50 )
		self.listItems = []
		
		for i in range(5000):
			channelNumber = i+1
			listItem = xbmcgui.ListItem("%04d Chanenl Name(%d)"%(channelNumber, channelNumber),"test", "-", "-", "-")
			self.listItems.append(listItem)
		
		self.listcontrol.addItems( self.listItems )


	def onAction(self, action):
		ctl = None
		try:
			ctl = self.getFocus()
		except:
			pass

		actionConsumed = False
		
		id = action.getId()
		
		if id == Action.ACTION_PREVIOUS_MENU:
			print 'lael98 check action menu'
		elif id == Action.ACTION_SELECT_ITEM:
			print '<<<<< test youn: action ID[%s]' % id
			log.debug('<<<<< test youn: action ID[%s]' % id)
			print 'tv_guide_last_selected[%s]' % action.getId()
			
			winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_BANNER )	

		elif id == Action.ACTION_PARENT_DIR:
			print 'lael98 check ation back'
			winmgr.getInstance().showWindow( winmgr.WIN_ID_NULLWINDOW )				

		else: log.debug('Unconsumed key: %s' % action.getId())


        
		if not actionConsumed and ctl:
			self.prevFocus = ctl
        


	def onClick(self, controlId):
		print "onclick(): control %d" % controlId


	def onFocus(self, controlId):
		print "onFocus(): control %d" % controlId



