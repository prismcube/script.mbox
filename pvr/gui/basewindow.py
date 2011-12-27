import xbmc
import xbmcgui
import time
import sys

from decorator import decorator
from elisproperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.guiconfig import *
import pvr.elismgr
import pvr.gui.dialogmgr
import threading

class Action(object):
	ACTION_NONE					= 0
	ACTION_MOVE_LEFT			= 1		#Left Arrow
	ACTION_MOVE_RIGHT			= 2		#Right Arrow
	ACTION_MOVE_UP				= 3		#Up Arrow
	ACTION_MOVE_DOWN			= 4		#Down Arrow
	ACTION_PAGE_UP				= 5		#PageUP --> Channel Up
	ACTION_PAGE_DOWN			= 6		#PageDown --> Channel Down
	ACTION_SELECT_ITEM			= 7		# OK
	ACTION_HIGHLIGHT_ITEM		= 8	
	ACTION_PARENT_DIR			= 9		#Back
	ACTION_PREVIOUS_MENU		= 10 	#ESC
	ACTION_SHOW_INFO			= 11	# i
	ACTION_PAUSE				= 12	#space
	ACTION_STOP					= 13
	ACTION_NEXT_ITEM			= 14
	ACTION_PREV_ITEM			= 15
	ACTION_FORWARD				= 16 
	ACTION_REWIND				= 17 
	REMOTE_0					= 58	#0
	REMOTE_1					= 59	#1
	REMOTE_2					= 60	#2
	REMOTE_3					= 61	#3
	REMOTE_4					= 62	#4
	REMOTE_5					= 63	#5
	REMOTE_6					= 64	#6
	REMOTE_7					= 65	#7
	REMOTE_8					= 66	#8
	REMOTE_9					= 67	#9
	ACTION_PLAYER_FORWARD		= 77
	ACTION_PLAYER_REWIND		= 78
	ACTION_PLAYER_PLAY			= 79
	
	ACTION_VOLUME_UP			= 88	#Plus
	ACTION_VOLUME_DOWN			= 89	#Minus
	ACTION_MUTE					= 91	#F8

	

@decorator
def setWindowBusy(func, *args, **kwargs):
	window = args[0]
	print 'check busy'
	try:
		try :
			print 'check busy #1'
			window.setBusy(True)
			print 'check busy #2'
			result = func(*args, **kwargs)
			print 'check busy #3'
		except Exception, ex:
			print 'Error publishing event ex=%s' %ex

	finally :
		print 'check busy #4'	
		window.setBusy(False)
		print 'check busy #5'

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
		self.recBusy = 0
		self.rLock = threading.RLock()		

	def setFooter( self, footermask ):
		self.footerGroupId = FooterMask.G_FOOTER_GROUP_STARTID
		for i in range( FooterMask.G_NUM_OF_FOOTER_ICON ):
			if not( footermask & ( 1 << i ) ):
				self.ctrlfooterGroup = self.getControl( self.footerGroupId )
				self.ctrlfooterGroup.setVisible( False )
			self.footerGroupId += FooterMask.G_FOOTER_GROUP_IDGAP

	def setHeaderLabel( self, label ):
		self.getControl( HeaderDefine.G_HEADER_LABEL_ID ).setLabel( label )


	def setBusy(self, busy):
		self.rLock.acquire()
		if busy == True:
			self.recBusy += 1
		else :
			self.recBusy -= 1
		self.rLock.release()
		
		print 'recBusy= %d' %self.recBusy

		"""
		print 'set busy #1'
		self.setProperty('busy', ('false', 'true')[busy])
		print 'set busy #2'
		"""
		
	def resetBusy( self ) :
		self.recBusy = 0
			
	def isBusy(self):
		if self.recBusy > 0 :
			return True
		else :
			return False

		"""
		busy = self.getProperty('busy')
		print 'isbusy = %s' %busy
		ret =  busy and busy == 'true'
		print 'ret=%d' %ret
		"""


class ControlItem:
	# Setting Window
	E_UNDEFINE								= 0
	E_SETTING_ENUM_CONTROL					= 1
	E_SETTING_USER_ENUM_CONTROL				= 2
	E_SETTING_INPUT_CONTROL					= 3
	E_SETTING_LEFT_LABEL_BUTTON_CONTROL		= 4

	# Detail Window
	E_DETAIL_NORMAL_BUTTON_CONTROL			= 5


	def __init__( self, controlType, controlId, property, listItems, selecteItem, stringType, maxLength, description ):	
		self.controlType = controlType	
		self.controlId  = controlId
		self.property = property		# E_SETTING_ENUM_CONTROL : propery, E_SETTING_INPUT_CONTROL : input type, E_DETAIL_NORMAL_BUTTON_CONTROL : Label
		self.listItems = listItems
		self.enable	= True
		self.description = description
		self.selecteItem = selecteItem
		self.stringType = stringType
		self.maxLength = maxLength
	

class SettingWindow( BaseWindow ):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		self.controlList = []
		self.commander = pvr.elismgr.getInstance().getCommander()		


	def initControl( self ):
		pos = 0
		for ctrlItem in self.controlList:
			if ctrlItem.controlType == ctrlItem.E_SETTING_ENUM_CONTROL :
				selectedItem = ctrlItem.property.getPropIndex()
				control = self.getControl( ctrlItem.controlId + 3 )
				control.addItems( ctrlItem.listItems )
				control.selectItem( selectedItem )
			elif ctrlItem.controlType == ctrlItem.E_SETTING_INPUT_CONTROL :
				control = self.getControl( ctrlItem.controlId + 3 )
				control.addItems( ctrlItem.listItems )
			elif ctrlItem.controlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
				control = self.getControl( ctrlItem.controlId + 3 )
				control.addItems( ctrlItem.listItems )
				control.selectItem( ctrlItem.selecteItem )
			elif ctrlItem.controlType == ctrlItem.E_SETTING_LEFT_LABEL_BUTTON_CONTROL :
				control = self.getControl( ctrlItem.controlId + 3 )
				control.addItems( ctrlItem.listItems )

			self.getControl(ctrlItem.controlId).setPosition(0, ( pos * 40 ) + 50 )
			pos += 1	

	def resetAllControl( self ):
		del self.controlList[:]


	def getControlIdToListIndex( self, controlId ) :
		count = len( self.controlList )
		for i in range( count ) :
			if controlId == self.controlList[i].controlId :
				return i

		print 'Unkown ControlId'


	def getListIndextoControlId( self, listindex ) :
		return self.controlList[listindex].controlId


	def getControlListSize( self ) :
		return len( self.controlList )


	def addEnumControl( self, controlId, propName, titleLabel=None, description=None ):
		property = ElisPropertyEnum( propName, self.commander )
		listItems = []

		for i in range( property.getIndexCount() ):
			if titleLabel == None :
				listItem = xbmcgui.ListItem( property.getName(), property.getPropStringByIndex( i ), "-", "-", "-" )
			else :
				listItem = xbmcgui.ListItem( titleLabel, property.getPropStringByIndex( i ), "-", "-", "-" )
			listItems.append( listItem )

		self.controlList.append( ControlItem( ControlItem.E_SETTING_ENUM_CONTROL, controlId, property, listItems, None, None, None, description ) )

	
	def addUserEnumControl( self, controlId, titleLabel, inputType, selectItem, description=None ):	
		listItems = []

		for i in range( len( inputType ) ):
			listItem = xbmcgui.ListItem( titleLabel, inputType[i], "-", "-", "-" )
			listItems.append( listItem )
		self.controlList.append( ControlItem( ControlItem.E_SETTING_USER_ENUM_CONTROL, controlId, None, listItems, int( selectItem ), None, None, description ) )

	def addInputControl( self, controlId , titleLabel, inputLabel, inputType=None, stringType=None, maxLength=None, description=None ):
		listItems = []
		listItem = xbmcgui.ListItem( titleLabel, inputLabel, "-", "-", "-" )
		listItems.append( listItem )
		self.controlList.append( ControlItem( ControlItem.E_SETTING_INPUT_CONTROL, controlId, inputType, listItems, None, None, None, description ) )

	def addLeftLabelButtonControl( self, controlId, inputString, description=None ):
		listItems = []
		listItem = xbmcgui.ListItem( inputString, '', "-", "-", "-" )
		listItems.append( listItem )
		self.controlList.append( ControlItem( ControlItem.E_SETTING_LEFT_LABEL_BUTTON_CONTROL, controlId, None, listItems, None, None, None, description ) )

	def showDescription( self, controlId ):
		count = len( self.controlList )

		for i in range( count ) :
			ctrlItem = self.controlList[i]		
			if self.hasControlItem( ctrlItem, controlId ) :
				if ctrlItem.description == None :
					return False
				self.getControl( E_SETTING_DESCRIPTION ).setLabel( ctrlItem.description )
		return False

	# Input Contol Type num (numeric KeyPad)
	# 0 : ShowAndGetNumber				(default format: #)          
	# 1 : ShowAndGetDate				(default format: DD/MM/YYYY)
	# 2 : ShowAndGetTime				(default format: HH:MM)
	# 3 : ShowAndGetIPAddress			(default format: #.#.#.#) 
	# 4 : Dhkim Define Normal Keyboard	( xbmc.Keyboard( default, heading, hidden = False) )
	# 5 : Dhkim Define Normal Keyboard	( xbmc.Keyboard( default, heading, hidden = True) )

	def inputSetup( self, ctrlItem ):
		keyType = ctrlItem.property
		if ( keyType == None ) :
			return
		"""
		import pvr.platform 
		scriptDir = pvr.platform.getPlatform().getScriptDir()
		from pvr.gui.dialogs.dialogkeyboard import DialogKeyboard
		KeyboardDialog('keyboarddialog.xml', scriptDir).doModal()
		"""

		if( keyType == 4 ) :
			kb = xbmc.Keyboard( ctrlItem.listItems[0].getLabel2( ), ctrlItem.listItems[0].getLabel( ), False )
			kb.doModal( )
			if( kb.isConfirmed( ) ) :
				ctrlItem.listItems[0].setLabel2( kb.getText( ) )
				#ctrlItem.listItems[0] = xbmcgui.ListItem( ctrlItem.listItems[0].getLabel( ), ctrlItem.listItems[0].getLabel2( ), "-", "-", "-" )
			return True

		elif( keyType == 5 ) :
			kb = xbmc.Keyboard( ctrlItem.listItems[0].getLabel2( ), ctrlItem.listItems[0].getLabel( ), True )
			kb.doModal( )
			if( kb.isConfirmed( ) ) :
				ctrlItem.listItems[0].setLabel2( kb.getText( ) )
				#ctrlItem.listItems[0] = xbmcgui.ListItem( ctrlItem.listItems[0].getLabel( ), ctrlItem.listItems[0].getLabel2( ), "-", "-", "-" )
			return True

		elif ( keyType == 0 ) :
			'''
			dialog = pvr.gui.dialogmgr.getInstance().getDialog( pvr.gui.dialogmgr.DIALOG_ID_NUMERIC )
			dialog.setTiteLabel( ctrlItem.listItems[0].getLabel( ) )
			dialog.setNumber( ctrlItem.listItems[0].getLabel2( ) )
			dialog.doModal( )

			if dialog.isOK() == True :
				ctrlItem.listItems[0].setLabel2( dialog.getNumber( ) )
			'''
			dialog = pvr.gui.dialogmgr.getInstance( ).getDialog( pvr.gui.dialogmgr.DIALOG_ID_KEYBOARD )
			dialog.setTiteLabel( ctrlItem.listItems[0].getLabel( ) )
			dialog.setText( ctrlItem.listItems[0].getLabel2( ) )
			dialog.doModal( )

			if dialog.isOK() == True :
				ctrlItem.listItems[0].setLabel2( dialog.getText( ) )
		
		else :
			dialog = xbmcgui.Dialog( )
			value = dialog.numeric( keyType, ctrlItem.listItems[0].getLabel( ), ctrlItem.listItems[0].getLabel2( ) )
			ctrlItem.listItems[0].setLabel2( value )
			#trlItem.listItems[0] = xbmcgui.ListItem( ctrlItem.listItems[0].getLabel( ), ctrlItem.listItems[0].getLabel2( ), "-", "-", "-" )
			return True

		return	False


	def deleteChar( self, controlId ):
		pass


	def hasControlItem( self, ctrlItem, controlId  ):
		if ctrlItem.controlType == ctrlItem.E_SETTING_ENUM_CONTROL or ctrlItem.controlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
			if ctrlItem.controlId == controlId or ctrlItem.controlId + 1 == controlId or ctrlItem.controlId + 2 == controlId or ctrlItem.controlId + 3 == controlId  :
				return True
		elif ctrlItem.controlType == ctrlItem.E_SETTING_INPUT_CONTROL or ctrlItem.controlType == ctrlItem.E_SETTING_LEFT_LABEL_BUTTON_CONTROL :
			if ctrlItem.controlId == controlId or ctrlItem.controlId + 1 == controlId  or ctrlItem.controlId + 3 == controlId :	
				return True
		else :
			if ctrlItem.controlId == controlId :
				return True

		return False

	def getPrevId( self, controlId ):
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

	def getNextId( self, controlId ):
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
		

	def getSelectedIndex( self, controlId ):

		count = len( self.controlList )

		for i in range( count ) :

			ctrlItem = self.controlList[i]		
			if self.hasControlItem( ctrlItem, controlId ) :
				if ctrlItem.controlType == ctrlItem.E_SETTING_ENUM_CONTROL or ctrlItem.controlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
					control = self.getControl( ctrlItem.controlId + 3 )
					time.sleep( 0.02 )
					return control.getSelectedPosition()

		return -1

	def getGroupId( self, controlId ):

		count = len( self.controlList )

		for i in range( count ) :

			ctrlItem = self.controlList[i]
			if ctrlItem.controlType == ctrlItem.E_SETTING_ENUM_CONTROL or ctrlItem.controlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
				if ctrlItem.controlId == controlId or ctrlItem.controlId + 1 == controlId or ctrlItem.controlId + 2 == controlId or ctrlItem.controlId + 3 == controlId :
					return ctrlItem.controlId

			elif ctrlItem.controlType == ctrlItem.E_SETTING_INPUT_CONTROL or ctrlItem.controlType == ctrlItem.E_SETTING_LEFT_LABEL_BUTTON_CONTROL :
				if ctrlItem.controlId == controlId or ctrlItem.controlId + 1 == controlId  or ctrlItem.controlId + 3 == controlId :	
					return ctrlItem.controlId
			else :
				if ctrlItem.controlId == controlId :
					return ctrlItem.controlId
				
		return -1
		

	def setEnableControl( self, controlId, enable ):

		count = len( self.controlList )

		for i in range( count ) :
			ctrlItem = self.controlList[i]
			if controlId == ctrlItem.controlId :
				control = self.getControl( controlId )
				control.setEnabled( enable )
				ctrlItem.enable = enable
				return True

		return False

	def setEnableControls( self, controlIds, enable ) :
		for controlId in controlIds :
			self.setEnableControl( controlId, enable )


	def setVisibleControl( self, controlId, visible ):
		control = self.getControl( controlId )
		control.setVisible( visible )


	def setVisibleControls( self, controlIds, visible ) :
		for controlId in controlIds :
			self.setVisibleControl( controlId, visible )


	def controlSelect( self ):
	
		focusId = self.getFocusId( )
		count = len( self.controlList )

		for i in range( count ) :
			ctrlItem = self.controlList[i]		
			if self.hasControlItem( ctrlItem, focusId ) :
				if ctrlItem.controlType == ctrlItem.E_SETTING_ENUM_CONTROL :
					control = self.getControl( ctrlItem.controlId + 3 )
					time.sleep( 0.02 )
					ctrlItem.property.setPropIndex( control.getSelectedPosition() )
					return True

				elif ctrlItem.controlType == ctrlItem.E_SETTING_INPUT_CONTROL :
					self.inputSetup( ctrlItem )
					return True
				elif ctrlItem.controlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
					return True
				elif ctrlItem.controlType == ctrlItem.E_SETTING_LEFT_LABEL_BUTTON_CONTROL :
					ret =  xbmcgui.Dialog( ).yesno('Configure', 'Are you sure?')	# return yes = 1, no = 0

				elif ctrlItem.controlType == ctrlItem.E_SETTING_NO_PROP_ENUM_CONTROL :
					return True

		return False


	def	controlkeypad( self, controlId, actionId ) :
		print 'dhkim test keypad = %d' % actionId
		#num start 58->30
		number = self.getControl( controlId + 3 ).getListItem(0).getLabel2( )
		self.getControl( controlId + 3 ).getListItem(0).setLabel2( number + chr( actionId - 10 ) )


	def controlUp( self ):

		focusId = self.getFocusId( )
		groupId = self.getGroupId( focusId )
		prevId = self.getPrevId( groupId )

		if prevId > 0 and groupId != prevId :
			self.setFocusId( prevId )
			return True

		return False


	def controlDown( self ):

		focusId = self.getFocusId( )
		groupId = self.getGroupId( focusId )
		nextId = self.getNextId( groupId )

		if nextId > 0 and groupId != nextId :
			self.setFocusId( nextId )
			return True

		return False

	def controlLeft( self ):

		focusId = self.getFocusId( )
		count = len( self.controlList )

		for i in range( count ) :
			ctrlItem = self.controlList[i]		
			if self.hasControlItem( ctrlItem, focusId ) :
				if ctrlItem.controlType == ctrlItem.E_SETTING_ENUM_CONTROL or ctrlItem.controlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
					if focusId % 10 == 2 :
						self.setFocusId( focusId - 1 )
						return

	
	def controlRight( self ):

		focusId = self.getFocusId( )
		count = len( self.controlList )

		for i in range( count ) :
			ctrlItem = self.controlList[i]		
			if self.hasControlItem( ctrlItem, focusId ) :
				if ctrlItem.controlType == ctrlItem.E_SETTING_ENUM_CONTROL or ctrlItem.controlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
					if focusId % 10 == 1 :
						self.setFocusId( focusId + 1 )
						return
						

	def selectPosition( self, controlId, position ) :

		count = len( self.controlList )

		for i in range( count ) :
			ctrlItem = self.controlList[i]		
			if self.hasControlItem( ctrlItem, controlId ) :
				if ctrlItem.controlType == ctrlItem.E_SETTING_ENUM_CONTROL :
					control = self.getControl( ctrlItem.controlId + 3 )
					control.selectItem( position )
					return True

		return False

	def setProp( self, controlId, value ):
	
		count = len( self.controlList )

		for i in range( count ) :
			ctrlItem = self.controlList[i]		
			if self.hasControlItem( ctrlItem, controlId ) :
				if ctrlItem.controlType == ctrlItem.E_SETTING_ENUM_CONTROL :
					ctrlItem.property.setProp( value )
					return True
	

class DetailWindow(SettingWindow):


	def initControl( self ):
		pos = 0
		for ctrlItem in self.controlList:
			if ctrlItem.controlType == ctrlItem.E_DETAIL_NORMAL_BUTTON_CONTROL :
				self.getControl(ctrlItem.controlId + 1).setLabel(ctrlItem.property)
			'''
			elif ctrlItem.controlType == ctrlItem.E_SETTING_LEFT_LABEL_BUTTON_CONTROL :
				control = self.getControl( ctrlItem.controlId + 3 )
				control.addItems( ctrlItem.listItems )
			'''
			self.getControl(ctrlItem.controlId).setPosition(0, ( pos * 40 ) )
			pos += 1


	def addNormalButtonControl( self, controlId, inputString ):
		self.controlList.append( ControlItem( ControlItem.E_DETAIL_NORMAL_BUTTON_CONTROL, controlId, inputString, None, None, None, None, None ) )


	def getGroupId( self, controlId ):
		count = len( self.controlList )
		
		for i in range( count ) :

			ctrlItem = self.controlList[i]
			if ctrlItem.controlType == ctrlItem.E_DETAIL_NORMAL_BUTTON_CONTROL :
				if ctrlItem.controlId == controlId or ctrlItem.controlId + 1 == controlId:
					return ctrlItem.controlId
			
		return -1

	def hasControlItem( self, ctrlItem, controlId  ):
		if ctrlItem.controlType == ctrlItem.E_DETAIL_NORMAL_BUTTON_CONTROL :
			if ctrlItem.controlId == controlId or ctrlItem.controlId + 1 :
				return True

		return False


	def controlSelect( self ):
		focusId = self.getFocusId( )
		count = len( self.controlList )

		for i in range( count ) :
			ctrlItem = self.controlList[i]		
			if self.hasControlItem( ctrlItem, focusId ) :
				if ctrlItem.controlType == ctrlItem.E_DETAIL_NORMAL_BUTTON_CONTROL :
					pass
				
		return False


	def controlLeft( self ):
		pass


	def controlRight( self ):
		pass


