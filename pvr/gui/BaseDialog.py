import xbmc
import xbmcgui
import time
import sys

from pvr.gui.BaseWindow import Property
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
import pvr.ElisMgr
from pvr.gui.GuiConfig import *
from pvr.Util import RunThread, GuiLock, GuiLock2, MLOG, LOG_WARN, LOG_TRACE, LOG_ERR

class BaseDialog( xbmcgui.WindowXMLDialog, Property ):
	def __init__( self, *args, **kwargs ):
		xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
		self.mWin = None
		self.mWinId = 0


	def NumericKeyboard( self, aKeyType, aTitle, aString, aMaxLength ) :
		dialog = xbmcgui.Dialog( )
		value = dialog.numeric( aKeyType, aTitle, aString )
		if value == None or value == '' :
			return aString

		if len( value ) > aMaxLength :
			value = value[ len ( value ) - aMaxLength :]
		return value

	def SetHeaderLabel( self, aLabel ):
		self.getControl( HeaderDefine.G_DIALOG_HEADER_LABEL_ID ).setLabel( aLabel )
	

	def CloseDialog( self ) :
		self.clearProperty( 'AnimationWaitingDialogOnClose' )
		time.sleep( 0.3 )
		self.close( )


	def GetFocusId( self ):
		GuiLock2( True )
		self.mFocusId = self.getFocusId()
		GuiLock2( False )


class ControlItem:
	# Setting Window
	E_UNDEFINE								= 0
	E_SETTING_ENUM_CONTROL					= 1
	E_SETTING_USER_ENUM_CONTROL				= 2
	E_SETTING_INPUT_CONTROL					= 3
	E_SETTING_LEFT_LABEL_BUTTON_CONTROL		= 4
	E_SETTING_OK_CANCEL_BUTTON				= 5
	

	def __init__( self, aControlType, aControlId, aProperty, aListItems, aSelecteItem, aDescription ):	
		self.mControlType = aControlType	
		self.mControlId  = aControlId
		self.mProperty = aProperty		# E_SETTING_ENUM_CONTROL : propery, E_SETTING_INPUT_CONTROL : input type
		self.mListItems = aListItems
		self.mEnable	= True
		self.mDescription = aDescription
		self.mSelecteItem = aSelecteItem
	

class SettingDialog( BaseDialog ):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, *args, **kwargs)
		self.mControlList = []
		self.mCommander = pvr.ElisMgr.GetInstance().GetCommander()
		self.mFocusId = -1


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

			if ctrlItem.mControlId == E_SettingDialogOk :
				self.getControl( ctrlItem.mControlId ).setPosition( 57, ( ( pos + 1 ) * 40 ) + 160 )

			elif ctrlItem.mControlId == E_SettingDialogCancel :
				self.getControl( ctrlItem.mControlId ).setPosition( 277, ( pos * 40 ) + 160 )
				
			else :
				self.getControl( ctrlItem.mControlId ).setPosition( 0, ( pos * 40 ) + 175 )
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
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_ENUM_CONTROL, aControlId, property, listItems, None, aDescription ) )

	
	def AddUserEnumControl( self, aControlId, aTitleLabel, aInputType, aSelectItem, aDescription=None ):	
		listItems = []

		for i in range( len( aInputType ) ):
			listItem = xbmcgui.ListItem( aTitleLabel, aInputType[i], "-", "-", "-" )
			listItems.append( listItem )
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_USER_ENUM_CONTROL, aControlId, None, listItems, int( aSelectItem ), aDescription ) )


	def AddInputControl( self, aControlId , aTitleLabel, aInputLabel, aInputType=None, aDescription=None ):
		listItems = []
		listItem = xbmcgui.ListItem( aTitleLabel, aInputLabel, "-", "-", "-" )
		listItems.append( listItem )
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_INPUT_CONTROL, aControlId, aInputType, listItems, None, aDescription ) )


	def AddLeftLabelButtonControl( self, aControlId, aInputString, aDescription=None ):
		listItems = []
		listItem = xbmcgui.ListItem( aInputString, '', "-", "-", "-" )
		listItems.append( listItem )
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_LEFT_LABEL_BUTTON_CONTROL, aControlId, None, listItems, None, aDescription ) )


	def AddOkCanelButton( self ) :
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_OK_CANCEL_BUTTON, E_SettingDialogOk, None, None, None, None ) ) 
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_OK_CANCEL_BUTTON, E_SettingDialogCancel, None, None, None, None ) )


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

	def GetControlLabel2String( self, aControlId ) :
		count = len( self.mControlList )

		for i in range( count ) :

			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, aControlId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_INPUT_CONTROL :
					return self.getControl( ctrlItem.mControlId + 3 ).getSelectedItem( ).getLabel2( )

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
					return True

				elif ctrlItem.mControlType == ctrlItem.E_SETTING_NO_PROP_ENUM_CONTROL :
					return True

		return False


	def ControlUp( self ) :	
		self.GetFocusId( )
		#if self.mFocusId == E_SettingDialogCancel :
		#	self.mFocusId = self.mFocusId - 1

		groupId = self.GetGroupId( self.mFocusId )
		prevId = self.GetPrevId( groupId )

		if prevId > 0 and groupId != prevId :
			self.setFocusId( prevId )
			return True

		return False


	def ControlDown( self ):
		self.GetFocusId( )
		#if self.mFocusId == E_SettingDialogOk :
		#	self.mFocusId = self.mFocusId + 1

		groupId = self.GetGroupId( self.mFocusId )
		nextId = self.GetNextId( groupId )

		if nextId > 0 and groupId != nextId :
			self.setFocusId( nextId )
			return True

		return False

	def ControlLeft( self ):
		self.GetFocusId( )
		count = len( self.mControlList )

		for i in range( count ) :
			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, self.mFocusId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_ENUM_CONTROL or ctrlItem.mControlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
					if self.mFocusId % 10 == 2 :
						self.setFocusId( self.mFocusId - 1 )
						return


	def ControlRight( self ):
		self.GetFocusId( )
		count = len( self.mControlList )

		for i in range( count ) :
			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, self.mFocusId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_ENUM_CONTROL or ctrlItem.mControlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
					if self.mFocusId % 10 == 1 :
						self.setFocusId( self.mFocusId + 1 )
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