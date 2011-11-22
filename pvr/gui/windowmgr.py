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

from gui.basewindow import BaseWindow
from inspect import currentframe

WIN_ID_NULLWINDOW 					= 1
WIN_ID_MAINMENU 					= 2
WIN_ID_CHANNEL_LIST_WINDOW			= 3
WIN_ID_CHANNEL_BANNER				= 4
WIN_ID_LANGUAGE_SETTING				= 5
WIN_ID_PARENTAL_LOCK				= 6
WIN_ID_RECORDING_OPTIONS			= 7




__windowmgr = None

def getInstance():
	global __windowmgr
	if not __windowmgr:
		print 'lael98 check create instance'
		__windowmgr = WindowMgr()
	else:
		print 'lael98 check already windowmgr is created'

	return __windowmgr



class WindowMgr(object):
	def __init__(self):
		print 'lael98 check %d %s' %(currentframe().f_lineno, currentframe().f_code.co_filename)

		import pvr.platform 
		self.scriptDir = pvr.platform.getPlatform().getScriptDir()
		print 'lael98 test scriptDir= %s' %self.scriptDir

		from pvr.gui.windows.nullwindow import NullWindow
		from pvr.gui.windows.mainmenu import MainMenu
		from pvr.gui.windows.channellistwindow import ChannelListWindow
		from pvr.gui.windows.channelbanner import ChannelBanner
		from pvr.gui.windows.languagesetting  import LanguageSetting
		from pvr.gui.windows.parentallock  import ParentalLock		
		
		self.windows = {
			WIN_ID_NULLWINDOW 					: NullWindow('nullwindow.xml', self.scriptDir ),
			WIN_ID_MAINMENU						: MainMenu('mainmenu.xml', self.scriptDir ),
			WIN_ID_CHANNEL_LIST_WINDOW			: ChannelListWindow('channellistwindow.xml', self.scriptDir ),
			WIN_ID_CHANNEL_BANNER				: ChannelBanner('channelbanner.xml', self.scriptDir ),
			WIN_ID_LANGUAGE_SETTING				: LanguageSetting('languagesetting.xml', self.scriptDir ),			
			WIN_ID_PARENTAL_LOCK				: ParentalLock('parentallock.xml', self.scriptDir ),
		}


	def showWindow( self, windowId ):
		print'lael98 check %d %s winid=%d' %(currentframe().f_lineno, currentframe().f_code.co_filename, windowId)    
		try:
 			self.lastId = windowId
			self.windows[windowId].doModal()

		except:
			print "can not find window"

	def shutdown(self):
		print 'windowmgr shutdown'
		self.windows[WIN_ID_NULLWINDOW].close()
		self.windows[WIN_ID_MAINMENU].close()
		self.windows[WIN_ID_CHANNEL_LIST_WINDOW].close()
		self.windows[WIN_ID_CHANNEL_BANNER].close()
		self.windows[WIN_ID_LANGUAGE_SETTING].close()		
		self.windows[WIN_ID_PARENTAL_LOCK].close()		


