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
			self.setProperty(name, value)
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


class ControlItem:
	E_UNDEFINE				= 0
	E_BUTTON_CONTROL		= 1
	E_ENUM_CONTROL			= 2

	def __init__( self, controlType, controlId, property, listItems ):	
		self.controlType = controlType	
		self.controlId  = controlId
		self.property = property
		self.listItems = listItems
		self.enable	= True
	

class SettingWindow(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		self.controlList = []

	def initControl(self):
		for ctrlItem in self.controlList:
			if ctrlItem.controlType == ctrlItem.E_ENUM_CONTROL :
				control = self.getControl( ctrlItem.controlId + 3 )
				control.addItems( ctrlItem.listItems )
				control.selectItem( ctrlItem.property.getPropIndex() )
				

	def addButtonControl( self, controlId ):
		self.controlList.append( ControlItem( ControlItem.E_BUTTON_CONTROL, controlId,   None, None ) )


	def addEnumControl( self, controlId, propName ):
		property = ElisPropertyEnum( propName )
		listItems = []

		for i in range( property.getIndexCount() ):
			listItem = xbmcgui.ListItem(property.getName(), property.getPropStringByIndex( i ),"-", "-", "-")
			listItems.append(listItem)

		self.controlList.append( ControlItem( ControlItem.E_ENUM_CONTROL, controlId, property, listItems ) )


	def hasControlItem( self, ctrlItem, controlId  ) :
		if ctrlItem.controlType == ctrlItem.E_ENUM_CONTROL :
			if ctrlItem.controlId == controlId or ctrlItem.controlId + 1 == controlId or ctrlItem.controlId + 2 == controlId or ctrlItem.controlId + 3 == controlId  :
				return True
		else :
			if ctrlItem.controlId == controlId :
				return True

		return False

	def getPrevId( self, controlId ) :
		count = len( self.controlList )
		prevId = -1
		found = False

		for i in range( count ) :
			ctrlItem = self.controlList[i]

			if ctrlItem.controlId == controlId :
				found = True
				if prevId > 0 :
					return prevId
				continue

			if ctrlItem.enable :
				prevId = ctrlItem.controlId

		return prevId

	def getNextId( self, controlId ) :
		count = len( self.controlList )
		nextId = -1
		found = False

		
		for i in range( count ) :
			ctrlItem = self.controlList[i]

			if ctrlItem.enable and  nextId <= 0 :
				nextId = ctrlItem.controlId

			if ctrlItem.enable and  found == True :
				return ctrlItem.controlId

			if ctrlItem.controlId == controlId :
				found = True
				continue

		return nextId
		

	def getSelectedIndex( self, controlId ) :

		count = len( self.controlList )

		for i in range( count ) :

			ctrlItem = self.controlList[i]		
			if self.hasControlItem( ctrlItem, controlId ) :
				if ctrlItem.controlType == ctrlItem.E_ENUM_CONTROL :
					control = self.getControl( ctrlItem.controlId + 3 )
					return control.getSelectedPosition()

		return -1

	def getGroupId( self, controlId ) :

		count = len( self.controlList )

		for i in range( count ) :

			ctrlItem = self.controlList[i]
			if ctrlItem.controlType == ctrlItem.E_ENUM_CONTROL :
				if ctrlItem.controlId == controlId or ctrlItem.controlId + 1 == controlId or ctrlItem.controlId + 2 == controlId or ctrlItem.controlId + 3 == controlId  :
					return ctrlItem.controlId
			else :
				if ctrlItem.controlId == controlId :
					return ctrlItem.controlId

		return -1
		

	def setEnableControl( self, controlId, enable ) :

		count = len( self.controlList )

		for i in range( count ) :
			ctrlItem = self.controlList[i]
			if controlId == ctrlItem.controlId :
				control = self.getControl( controlId )
				control.setEnabled( enable )
				ctrlItem.enable = enable
				return True

		return False
	

	def controlSelect	( self ) :
	
		focusId = self.getFocusId( )
		count = len( self.controlList )

		for i in range( count ) :
			ctrlItem = self.controlList[i]		
			if self.hasControlItem( ctrlItem, focusId ) :
				if ctrlItem.controlType == ctrlItem.E_ENUM_CONTROL :
					control = self.getControl( ctrlItem.controlId + 3 )
					ctrlItem.property.setPropIndex( control.getSelectedPosition() )
					return True

		return False


	def controlUp( self ) :

		focusId = self.getFocusId( )
		groupId = self.getGroupId( focusId )
		prevId = self.getPrevId( groupId )

		if prevId > 0 and groupId != prevId :
			self.setFocusId( prevId )
			return True

		return False


	def controlDown( self ) :

		focusId = self.getFocusId( )
		groupId = self.getGroupId( focusId )
		nextId = self.getNextId( groupId )

		if nextId > 0 and groupId != nextId :
			self.setFocusId( nextId )
			return True

		return False


