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
from pvr.util import catchall
import pvr.elismgr


class ChannelListWindow(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance().getCommander()		

		self.currentChannel = -1
		self.channelList = []
		self.listItems = []
		self.commander.getChannelList( ElisEnum.E_TYPE_TV, ElisEnum.E_MODE_ALL, ElisEnum.E_SORT_BY_DEFAULT, self.channelList )

		current = self.commander.getCurrentChannel()
		if current[0].upper() != 'NULL' :
			self.currentChannel = int(current[0])

		for ch in self.channelList:
			listItem = xbmcgui.ListItem("%04d %s"%( int(ch[0]), ch[2]),"-", "-", "-", "-")
			self.listItems.append(listItem)

	def onInit(self):
		if not self.win:
			self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())

		self.listcontrol = self.getControl( 50 )
		self.listcontrol.addItems( self.listItems )

		chindex = 0;
		if self.currentChannel > 0 :
			for ch in self.channelList:
				if int(ch[0]) == self.currentChannel :
					break
				chindex += 1

			self.listcontrol.selectItem( chindex )


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

		else: print'Unconsumed key: %s' % action.getId()


	def onClick(self, controlId):
		print "ChannelListWindow onclick(): control %d" % controlId	
		if controlId == self.listcontrol.getId() :
			label = self.listcontrol.getSelectedItem().getLabel()
			channelNumbr = int(label[:4])
			ret = self.commander.setCurrentChannel( channelNumbr )

			if ret[0].upper() == 'TRUE' :
				if self.currentChannel == channelNumbr :
					winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_BANNER )

				self.currentChannel = channelNumbr


	def onFocus(self, controlId):
		print "onFocus(): control %d" % controlId



