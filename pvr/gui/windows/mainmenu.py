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



class MainMenu(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		print 'lael98 check %d %s' %(currentframe().f_lineno, currentframe().f_code.co_filename)    
		print 'args=%s' % args[0]

	def onInit(self):
		if not self.win:
			self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
	
	def onAction(self, action):
		id = action.getId()
	
		if id == Action.ACTION_PREVIOUS_MENU:
			print 'lael98 check action menu'
		elif id == Action.ACTION_SELECT_ITEM:
			print 'lael98 check ation select'
		elif id == Action.ACTION_PARENT_DIR:			
			print 'lael98 check ation back'
			winmgr.getInstance().showWindow( winmgr.WIN_ID_NULLWINDOW )			

	def onClick(self, controlId):
		print "onclick(): control %d" % controlId
		if controlId == 70301:
			winmgr.getInstance().showWindow( winmgr.WIN_ID_LANGUAGE_SETTING )
		elif  controlId == 70302:
			winmgr.getInstance().showWindow( winmgr.WIN_ID_PARENTAL_LOCK )
		elif  controlId == 70303:
			winmgr.getInstance().showWindow( winmgr.WIN_ID_RECORDING_OPTIONS )
		

	def onFocus(self, controlId):
		print "onFocus(): control %d" % controlId


