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
import time
import sys

from decorator import decorator
from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt

class Action(object):
	ACTION_NONE					= 0
	ACTION_MOVE_LEFT			= 1
	ACTION_MOVE_RIGHT			= 2
	ACTION_MOVE_UP				= 3
	ACTION_MOVE_DOWN			= 4
	ACTION_PAGE_UP				= 5
	ACTION_PAGE_DOWN			= 6
	ACTION_SELECT_ITEM			= 7
	ACTION_HIGHLIGHT_ITEM		= 8
	ACTION_PARENT_DIR			= 9
	ACTION_PREVIOUS_MENU		= 10
	ACTION_SHOW_INFO			= 11
	ACTION_PAUSE				= 12
	ACTION_STOP					= 13
	ACTION_NEXT_ITEM			= 14
	ACTION_PREV_ITEM			= 15
	ACTION_FORWARD				= 16 
	ACTION_REWIND				= 17 
	REMOTE_0					= 58
	REMOTE_1					= 59
	REMOTE_2					= 60
	REMOTE_3					= 61
	REMOTE_4					= 62
	REMOTE_5					= 63
	REMOTE_6					= 64
	REMOTE_7					= 65
	REMOTE_8					= 66
	REMOTE_9					= 67
	ACTION_PLAYER_FORWARD		= 77
	ACTION_PLAYER_REWIND		= 78
	ACTION_PLAYER_PLAY			= 79

@decorator
def setWindowBusy(func, *args, **kwargs):
	window = args[0]
	try:
		window.setBusy(True)
		result = func(*args, **kwargs)
	finally:
		window.setBusy(False)
	return result


class Property(object):
    
	def getListItemProperty(self, listItem, name):
		p = listItem.getProperty(name)
		if p is not None:
			return p.decode('utf-8')
        
	def setListItemProperty(self, listItem, name, value):
		if listItem and name and not value is None:
			listItem.setProperty(name, value)
		else:
			log.debug('Setting listitem with a None: listItem=%s name=%s value=%s' % (listItem, name, value))

	def updateListItemProperty(self, listItem, name, value):
			self.setListItemProperty(listItem, name, value)
			listItem.setThumbnailImage('%s' + str(time.clock()))   

	def setWindowProperty(self, name, value):
		if self.win and name and not value is None:
			self.win.setProperty(name, value)
		else:
			print 'Setting window property with a None: win=%s name=%s value=%s' % (self.win, name, value)

	def selectListItemAtIndex(self, listbox, index):
		if index < 0: 
			index = 0
		listbox.selectItem(index)
		maxtries = 100
		cnt = 0
		while listbox.getSelectedPosition() != index and cnt < maxtries:
			cnt += 1
			print "waiting for item select to happen...%d" % cnt
			time.sleep(0.1)
		if cnt == maxtries:
			print "timeout waiting for item select to happen"


class BaseWindow(xbmcgui.WindowXML, Property):
	def __init__(self, *args, **kwargs):
		xbmcgui.WindowXML.__init__(self, *args, **kwargs)
		self.win = None        
		self.closed = False

class BaseDialog(xbmcgui.WindowXMLDialog, Property):
	def __init__(self, *args, **kwargs):
		xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)
		self.win = None        


from gui.basewindow import BaseWindow

class SettingWindow(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)

	def creatPropertyEnum(self, enumList, enumProperty ) :
		for i in range( enumProperty.getIndexCount() ):
			listItem = xbmcgui.ListItem(enumProperty.getName(), enumProperty.getPropStringByIndex( i ),"-", "-", "-")
			enumList.append(listItem)

	def controlUp( self, navigationIds, navId ) :
		count = len( navigationIds )

		if count < 2 :
			return False

		for i in range( count ) :
			if i == 0 :
				if navigationIds[0] == navId :
					self.win.setFocusId( navigationIds[count-1] )					
					return True
			else :
				if navigationIds[i] == navId :
					self.win.setFocusId( navigationIds[i-1] )
					return True
				
		print 'ERR : can not find next focus control'
		return False
	

	def controlDown( self, navigationIds, navId ) :
		count = len( navigationIds )

		if count < 2 :
			return False

		for i in range( count ) :
			if i == count-1 :
				if navigationIds[i] == navId :
					self.win.setFocusId( navigationIds[0] )					
					return True
			else :
				if navigationIds[i] == navId :
					self.win.setFocusId( navigationIds[i+1] )
					return True
				
		print 'ERR : can not find next focus control'
		return False
	
