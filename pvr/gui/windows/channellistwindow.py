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
from inspect import currentframe
from pvr.util import catchall
import pvr.elismgr



class ChannelListWindow(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		self.commander = pvr.elismgr.getCommander()		
		print 'lael98 check %d %s' %(currentframe().f_lineno, currentframe().f_code.co_filename)    
		print 'args=%s' % args[0]

	def onInit(self):
		if not self.win:
			self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
		
		self.listcontrol = self.getControl( 50 )
		self.listItems = []

		print 'ChannelListWindow lael98 before add list'		
		for i in range(5000):
			channelNumber = i+1
			listItem = xbmcgui.ListItem("%04d Chanenl Name(%d)"%(channelNumber, channelNumber),"test", "-", "-", "-")
			self.listItems.append(listItem)
		
		self.listcontrol.addItems( self.listItems )


	def onAction(self, action):
		id = action.getId()
	
		if id == Action.ACTION_PREVIOUS_MENU:
			print 'ChannelListWindow lael98 check action menu'
		elif id == Action.ACTION_SELECT_ITEM:
			print 'ChannelListWindow lael98 check ation select %d' %id
		elif id == Action.ACTION_PARENT_DIR:
			print 'ChannelListWindow lael98 check ation back'
			winmgr.getInstance().showWindow( winmgr.WIN_ID_NULLWINDOW )	


	def onClick(self, controlId):
		print "ChannelListWindow onclick(): control %d" % controlId	
		if controlId == self.listcontrol.getId() :
			print "ChannelListWindow onclick(): control %d" % controlId
			print "ChannelListWindow getid=%d" %self.listcontrol.getId()
			label = self.listcontrol.getSelectedItem().getLabel()
			print "ChannelListWindow laebel=%s" %label[:4]
			self.commander.setCurrentChannel( int(label[:4]) )

	def onFocus(self, controlId):
		print "onFocus(): control %d" % controlId


