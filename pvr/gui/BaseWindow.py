import xbmc
import xbmcgui
import time
import sys

from decorator import decorator
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.GuiConfig import *
import pvr.ElisMgr
import pvr.gui.DialogMgr
import thread

from pvr.Util import RunThread

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
	



class Property(object):

	def GetListItemProperty(self, aListItem, aName):
		p = aListItem.getProperty(aName)
		if p is not None:
			return p.decode('utf-8')

	def SetListItemProperty(self, aListItem, aName, aValue):
		if aListItem and aName and not aValue is None:
			aListItem.setProperty(aName, aValue)
		else:
			log.debug('ERR listItem=%s name=%s value=%s' % (aListItem, aName, aValue))


class BaseWindow(xbmcgui.WindowXML, Property):

	def __init__(self, *args, **kwargs):
		xbmcgui.WindowXML.__init__(self, *args, **kwargs)
		self.mWin = None
		self.mWinId = 0
		self.mClosed = False

	def SetFooter( self, aFooterMask ):
		self.mFooterGroupId = FooterMask.G_FOOTER_GROUP_STARTID
		for i in range( FooterMask.G_NUM_OF_FOOTER_ICON ):
			if not( aFooterMask & ( 1 << i ) ):
				self.mCtrlFooterGroup = self.getControl( self.mFooterGroupId )
				self.mCtrlFooterGroup.setVisible( False )
			self.mFooterGroupId += FooterMask.G_FOOTER_GROUP_IDGAP

	def SetHeaderLabel( self, aLabel ):
		self.getControl( HeaderDefine.G_HEADER_LABEL_ID ).setLabel( aLabel )


class ControlItem:
	# Setting Window
	E_UNDEFINE								= 0
	E_SETTING_ENUM_CONTROL					= 1
	E_SETTING_USER_ENUM_CONTROL				= 2
	E_SETTING_INPUT_CONTROL					= 3
	E_SETTING_LEFT_LABEL_BUTTON_CONTROL		= 4

	# Detail Window
	E_DETAIL_NORMAL_BUTTON_CONTROL			= 5


	def __init__( self, aControlType, aControlId, aProperty, aListItems, aSelecteItem, aStringType, aMaxLength, aDescription ):	
		self.mControlType = aControlType	
		self.mControlId  = aControlId
		self.mProperty = aProperty		# E_SETTING_ENUM_CONTROL : propery, E_SETTING_INPUT_CONTROL : input type, E_DETAIL_NORMAL_BUTTON_CONTROL : Label
		self.mListItems = aListItems
		self.mEnable	= True
		self.mDescription = aDescription
		self.mSelecteItem = aSelecteItem
		self.mStringType = aStringType	# 0 : Number, 1 : String
		self.mMaxLength = aMaxLength
	

class SettingWindow( BaseWindow ):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		self.mControlList = []
		self.mCommander = pvr.ElisMgr.GetInstance().GetCommander()


	def InitControl( self ):
		pos = 0
		for ctrlItem in self.mControlList:
			if ctrlItem.mControlType == ctrlItem.E_SETTING_ENUM_CONTROL :
				selectedItem = ctrlItem.mProperty.GetPropIndex()
				control = self.getControl( ctrlItem.mControlId + 3 )
				control.addItems( ctrlItem.mListItems )
				control.selectItem( selectedItem )
			elif ctrlItem.mControlType == ctrlItem.E_SETTING_INPUT_CONTROL :
				control = self.getControl( ctrlItem.mControlId + 3 )
				control.addItems( ctrlItem.mListItems )
			elif ctrlItem.mControlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
				control = self.getControl( ctrlItem.mControlId + 3 )
				control.addItems( ctrlItem.mListItems )
				control.selectItem( ctrlItem.mSelecteItem )
			elif ctrlItem.mControlType == ctrlItem.E_SETTING_LEFT_LABEL_BUTTON_CONTROL :
				control = self.getControl( ctrlItem.mControlId + 3 )
				control.addItems( ctrlItem.mListItems )

			self.getControl( ctrlItem.mControlId ).setPosition( 0, ( pos * 40 ) + 50 )
			pos += 1	

	def ResetAllControl( self ):
		del self.mControlList[:]


	def GetControlIdToListIndex( self, aControlId ) :
		count = len( self.mControlList )
		for i in range( count ) :
			if aControlId == self.mControlList[i].mControlId :
				return i

		print 'Unkown ControlId'


	def GetListIndextoControlId( self, aListIndex ) :
		return self.mControlList[aListIndex].mControlId


	def GetControlListSize( self ) :
		return len( self.mControlList )


	def AddEnumControl( self, aControlId, aPropName, aTitleLabel=None, aDescription=None ):
		property = ElisPropertyEnum( aPropName, self.mCommander )
		listItems = []
		for i in range( property.GetIndexCount() ):
			if aTitleLabel == None :
				listItem = xbmcgui.ListItem( property.GetName(), property.GetPropStringByIndex( i ), "-", "-", "-" )
			else :
				listItem = xbmcgui.ListItem( aTitleLabel, property.GetPropStringByIndex( i ), "-", "-", "-" )
			listItems.append( listItem )
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_ENUM_CONTROL, aControlId, property, listItems, None, None, None, aDescription ) )

	
	def AddUserEnumControl( self, aControlId, aTitleLabel, aInputType, aSelectItem, aDescription=None ):	
		listItems = []

		for i in range( len( aInputType ) ):
			listItem = xbmcgui.ListItem( aTitleLabel, aInputType[i], "-", "-", "-" )
			listItems.append( listItem )
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_USER_ENUM_CONTROL, aControlId, None, listItems, int( aSelectItem ), None, None, aDescription ) )

	def AddInputControl( self, aControlId , aTitleLabel, aInputLabel, aInputType=None, aStringType=None, aMaxLength=None, aDescription=None ):
		listItems = []
		listItem = xbmcgui.ListItem( aTitleLabel, aInputLabel, "-", "-", "-" )
		listItems.append( listItem )
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_INPUT_CONTROL, aControlId, aInputType, listItems, None, aStringType, aMaxLength, aDescription ) )

	def AddLeftLabelButtonControl( self, aControlId, aInputString, aDescription=None ):
		listItems = []
		listItem = xbmcgui.ListItem( aInputString, '', "-", "-", "-" )
		listItems.append( listItem )
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_LEFT_LABEL_BUTTON_CONTROL, aControlId, None, listItems, None, None, None, aDescription ) )

	def ShowDescription( self, aControlId ):
		count = len( self.mControlList )

		for i in range( count ) :
			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, aControlId ) :
				if ctrlItem.mDescription == None :
					return False
				self.getControl( E_SETTING_DESCRIPTION ).setLabel( ctrlItem.mDescription )
		return False

	# Input Contol Type num (numeric KeyPad)
	# 0 : ShowAndGetNumber				(default format: #)          
	# 1 : ShowAndGetDate				(default format: DD/MM/YYYY)
	# 2 : ShowAndGetTime				(default format: HH:MM)
	# 3 : ShowAndGetIPAddress			(default format: #.#.#.#) 
	# 4 : Dhkim Define Normal Keyboard	( xbmc.Keyboard( default, heading, hidden = False) )
	# 5 : Dhkim Define Normal Keyboard	( xbmc.Keyboard( default, heading, hidden = True) )

	def InputSetup( self, aCtrlItem ):
		keyType = aCtrlItem.mProperty
		if keyType == None :
			return

		if keyType == 4 :
			kb = xbmc.Keyboard( aCtrlItem.mListItems[0].getLabel2( ), aCtrlItem.mListItems[0].getLabel( ), False )
			kb.doModal( )
			if( kb.isConfirmed( ) ) :
				aCtrlItem.mListItems[0].setLabel2( kb.getText( ) )
				#aCtrlItem.mListItems[0] = xbmcgui.ListItem( aCtrlItem.mListItems[0].getLabel( ), aCtrlItem.mListItems[0].getLabel2( ), "-", "-", "-" )
			return True

		elif keyType == 5 :
			kb = xbmc.Keyboard( aCtrlItem.mListItems[0].getLabel2( ), aCtrlItem.mListItems[0].getLabel( ), True )
			kb.doModal( )
			if( kb.isConfirmed( ) ) :
				aCtrlItem.mListItems[0].setLabel2( kb.getText( ) )
				#aCtrlItem.mListItems[0] = xbmcgui.ListItem( aCtrlItem.mListItems[0].getLabel( ), aCtrlItem.mListItems[0].getLabel2( ), "-", "-", "-" )
			return True

		else :
		
			dialog = xbmcgui.Dialog( )
			value = dialog.numeric( keyType, aCtrlItem.mListItems[0].getLabel( ), aCtrlItem.mListItems[0].getLabel2( ) )

			if value != None :
				if len( value ) > aCtrlItem.mMaxLength :
					value = value[ len ( value ) - aCtrlItem.mMaxLength :]
				aCtrlItem.mListItems[0].setLabel2( value )


	def HasControlItem( self, aCtrlItem, aContgrolId  ):
		if aCtrlItem.mControlType == aCtrlItem.E_SETTING_ENUM_CONTROL or aCtrlItem.mControlType == aCtrlItem.E_SETTING_USER_ENUM_CONTROL :
			if aCtrlItem.mControlId == aContgrolId or aCtrlItem.mControlId + 1 == aContgrolId or aCtrlItem.mControlId + 2 == aContgrolId or aCtrlItem.mControlId + 3 == aContgrolId  :
				return True
		elif aCtrlItem.mControlType == aCtrlItem.E_SETTING_INPUT_CONTROL or aCtrlItem.mControlType == aCtrlItem.E_SETTING_LEFT_LABEL_BUTTON_CONTROL :
			if aCtrlItem.mControlId == aContgrolId or aCtrlItem.mControlId + 1 == aContgrolId  or aCtrlItem.mControlId + 3 == aContgrolId :	
				return True
		else :
			if aCtrlItem.mControlId == aContgrolId :
				return True

		return False

	def GetPrevId( self, aControlId ):
		count = len( self.mControlList )
		prevId = -1
		found = False

		for i in range( count ) :
			ctrlItem = self.mControlList[i]

			if ctrlItem.mControlId == aControlId :
				found = True
				if prevId > 0 :
					return prevId
				continue

			if ctrlItem.mEnable :
				prevId = ctrlItem.mControlId

		return prevId

	def GetNextId( self, aControlId ):
		count = len( self.mControlList )
		nextId = -1
		found = False

		
		for i in range( count ) :
			ctrlItem = self.mControlList[i]

			if ctrlItem.mEnable and  nextId <= 0 :
				nextId = ctrlItem.mControlId

			if ctrlItem.mEnable and  found == True :
				return ctrlItem.mControlId

			if ctrlItem.mControlId == aControlId :
				found = True
				continue

		return nextId
		

	def GetSelectedIndex( self, aControlId ) :

		count = len( self.mControlList )

		for i in range( count ) :

			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, aControlId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_ENUM_CONTROL or ctrlItem.mControlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
					control = self.getControl( ctrlItem.mControlId + 3 )
					time.sleep( 0.02 )
					return control.getSelectedPosition()

		return -1

	def GetGroupId( self, aContgrolId ) :

		count = len( self.mControlList )

		for i in range( count ) :

			ctrlItem = self.mControlList[i]
			if ctrlItem.mControlType == ctrlItem.E_SETTING_ENUM_CONTROL or ctrlItem.mControlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
				if ctrlItem.mControlId == aContgrolId or ctrlItem.mControlId + 1 == aContgrolId or ctrlItem.mControlId + 2 == aContgrolId or ctrlItem.mControlId + 3 == aContgrolId :
					return ctrlItem.mControlId

			elif ctrlItem.mControlType == ctrlItem.E_SETTING_INPUT_CONTROL or ctrlItem.mControlType == ctrlItem.E_SETTING_LEFT_LABEL_BUTTON_CONTROL :
				if ctrlItem.mControlId == aContgrolId or ctrlItem.mControlId + 1 == aContgrolId  or ctrlItem.mControlId + 3 == aContgrolId :	
					return ctrlItem.mControlId
			else :
				if ctrlItem.mControlId == aContgrolId :
					return ctrlItem.mControlId
				
		return -1
		

	def SetEnableControl( self, aControlId, aEnable ) :

		count = len( self.mControlList )

		for i in range( count ) :
			ctrlItem = self.mControlList[i]
			if aControlId == ctrlItem.mControlId :
				control = self.getControl( aControlId )
				control.setEnabled( aEnable )
				ctrlItem.mEnable = aEnable
				return True

		return False

	def SetEnableControls( self, aControlIds, mEnable ) :
		for controlId in aControlIds :
			self.SetEnableControl( controlId, mEnable )


	def SetVisibleControl( self, aControlId, aVisible ) :
		control = self.getControl( aControlId )
		control.setVisible( aVisible )


	def SetVisibleControls( self, aControlIds, aVisible ) :
		for controlId in aControlIds :
			self.SetVisibleControl( controlId, aVisible )


	def ControlSelect( self ) :
	
		focusId = self.getFocusId( )
		count = len( self.mControlList )

		for i in range( count ) :
			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, focusId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_ENUM_CONTROL :
					control = self.getControl( ctrlItem.mControlId + 3 )
					time.sleep( 0.02 )
					ctrlItem.mProperty.SetPropIndex( control.getSelectedPosition() )
					return True

				elif ctrlItem.mControlType == ctrlItem.E_SETTING_INPUT_CONTROL :
					self.InputSetup( ctrlItem )
					return True
				elif ctrlItem.mControlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
					return True
				elif ctrlItem.mControlType == ctrlItem.E_SETTING_LEFT_LABEL_BUTTON_CONTROL :
					ret =  xbmcgui.Dialog( ).yesno('Configure', 'Are you sure?')	# return yes = 1, no = 0

				elif ctrlItem.mControlType == ctrlItem.E_SETTING_NO_PROP_ENUM_CONTROL :
					return True

		return False


	def ControlUp( self ):

		focusId = self.getFocusId( )
		groupId = self.GetGroupId( focusId )
		prevId = self.GetPrevId( groupId )

		if prevId > 0 and groupId != prevId :
			self.setFocusId( prevId )
			return True

		return False


	def ControlDown( self ):

		focusId = self.getFocusId( )
		groupId = self.GetGroupId( focusId )
		nextId = self.GetNextId( groupId )

		if nextId > 0 and groupId != nextId :
			self.setFocusId( nextId )
			return True

		return False

	def ControlLeft( self ):

		focusId = self.getFocusId( )
		count = len( self.mControlList )

		for i in range( count ) :
			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, focusId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_ENUM_CONTROL or ctrlItem.mControlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
					if focusId % 10 == 2 :
						self.setFocusId( focusId - 1 )
						return


	def ControlRight( self ):

		focusId = self.getFocusId( )
		count = len( self.mControlList )

		for i in range( count ) :
			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, focusId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_ENUM_CONTROL or ctrlItem.mControlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
					if focusId % 10 == 1 :
						self.setFocusId( focusId + 1 )
						return


	def SelectPosition( self, aControlId, aPosition ) :

		count = len( self.mControlList )

		for i in range( count ) :
			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, aControlId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_ENUM_CONTROL :
					control = self.getControl( ctrlItem.mControlId + 3 )
					control.selectItem( aPosition )
					return True

		return False

	def SetProp( self, aControlId, aValue ):
	
		count = len( self.mControlList )

		for i in range( count ) :
			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, aControlId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_ENUM_CONTROL :
					ctrlItem.mProperty.SetProp( aValue )
					return True
	

