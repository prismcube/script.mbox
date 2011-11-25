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



class NullWindow(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		print 'lael98 check %d %s' %(currentframe().f_lineno, currentframe().f_code.co_filename)    
		print 'args=%s' % args[0]
		self.lastFocusId = None

	def onInit(self):
		if not self.win:
			self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())

	def onAction(self, action):
		id = action.getId()

		if id == Action.ACTION_PREVIOUS_MENU:
			print 'lael98 check ation menu'
			self.close( )
			winmgr.getInstance().showWindow( winmgr.WIN_ID_MAINMENU )
		elif id == Action.ACTION_PARENT_DIR:
			print 'lael98 check ation parentdir'
		elif id == Action.ACTION_SELECT_ITEM:
			self.close( )
			winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_LIST_WINDOW )
#			winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_BANNER )
			print 'lael98 check ation select'
		else:
			print 'lael98 check ation unknown id=%d' %id

	def onClick(self, controlId):
		print "onclick(): control %s" % controlId

	def onFocus(self, controlId):
		print "onFocus(): control %s" % controlId
		self.lastFocusId = controlId


