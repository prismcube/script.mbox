from pvr.gui.GuiConfig import *
from elisinterface.ElisProperty import ElisPropertyEnum, ElisPropertyInt
import pvr.TunerConfigMgr
from pvr.gui.BaseWindow import BaseWindow
from pvr.gui.BaseWindow import Action


class ControlItem :
	# Setting Window
	E_UNDEFINE								= 0
	E_SETTING_ENUM_CONTROL					= 1
	E_SETTING_USER_ENUM_CONTROL				= 2
	E_SETTING_INPUT_CONTROL					= 3
	E_SETTING_PREV_NEXT_BUTTON				= 4


	def __init__( self, aControlType, aControlId, aProperty, aListItems, aSelecteItem, aDescription = None, aInputNumberType = None, aMax = 0 ) :
		self.mEnable			= True
		self.mControlType		= aControlType	
		self.mControlId 		= aControlId
		self.mProperty			= aProperty		# E_SETTING_ENUM_CONTROL : propery, E_SETTING_INPUT_CONTROL : input type
		self.mListItems			= aListItems
		self.mSelecteItem		= aSelecteItem
		self.mDescription		= aDescription
		self.mInputNumberType	= aInputNumberType
		self.mMax				= aMax
	

class SettingWindow( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mControlList	= []
		self.mTunerMgr		= pvr.TunerConfigMgr.GetInstance( )
		self.mResetInput	= True


	def InitControl( self ) :
		pos = 0
		for ctrlItem in self.mControlList :
			if ctrlItem.mControlType == ctrlItem.E_SETTING_ENUM_CONTROL :
				selectedItem = ctrlItem.mProperty.GetPropIndex( )
				control = self.getControl( ctrlItem.mControlId + 3 )
				control.reset( )
				control.addItems( ctrlItem.mListItems )
				control.selectItem( selectedItem )
			elif ctrlItem.mControlType == ctrlItem.E_SETTING_INPUT_CONTROL :
				control = self.getControl( ctrlItem.mControlId + 3 )
				control.reset( )
				control.addItems( ctrlItem.mListItems )
			elif ctrlItem.mControlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
				control = self.getControl( ctrlItem.mControlId + 3 )
				control.reset( )
				control.addItems( ctrlItem.mListItems )
				control.selectItem( ctrlItem.mSelecteItem )

			if ctrlItem.mControlId != E_FIRST_TIME_INSTALLATION_PREV and ctrlItem.mControlId != E_FIRST_TIME_INSTALLATION_NEXT :
				pos += self.getControl( ctrlItem.mControlId ).getHeight( )
				self.getControl( ctrlItem.mControlId ).setPosition( 0, pos )


	def ResetAllControl( self ) :
		self.mControlList = []


	def SetSettingWindowLabel( self, aLabel ) :
		#self.getControl( E_SETTING_MINI_TITLE ).setLabel( MR_LANG( 'Installation' ) )
		self.getControl( E_SETTING_HEADER_TITLE ).setLabel( aLabel )

		
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


	def AddEnumControl( self, aControlId, aPropName, aTitleLabel = None, aDescription = None ) :
		property = ElisPropertyEnum( aPropName, self.mCommander )
		listItems = []
		for i in range( property.GetIndexCount( ) ) :
			if aTitleLabel == None :
				listItem = xbmcgui.ListItem( property.GetName( ), property.GetPropStringByIndex( i ) )
			else :
				listItem = xbmcgui.ListItem( aTitleLabel, property.GetPropStringByIndex( i ) )
			listItems.append( listItem )
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_ENUM_CONTROL, aControlId, property, listItems, None, aDescription ) )

	
	def AddUserEnumControl( self, aControlId, aTitleLabel, aInputType, aSelectItem, aDescription=None ) :	
		listItems = []

		for i in range( len( aInputType ) ) :
			listItem = xbmcgui.ListItem( aTitleLabel, aInputType[i] )
			listItems.append( listItem )
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_USER_ENUM_CONTROL, aControlId, None, listItems, int( aSelectItem ), aDescription ) )


	def AddInputControl( self, aControlId , aTitleLabel, aInputLabel, aDescription = None, aInputNumberType = None, aMax = 0 ) :
		listItems = []
		listItem = xbmcgui.ListItem( aTitleLabel, aInputLabel )
		listItems.append( listItem )
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_INPUT_CONTROL, aControlId, None, listItems, None, aDescription, aInputNumberType, aMax ) )


	def AddPrevNextButton( self, aDescriptionNext, aDescriptionPrev ) :
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_PREV_NEXT_BUTTON, E_FIRST_TIME_INSTALLATION_PREV, None, None, None, aDescriptionPrev ) ) 		
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_PREV_NEXT_BUTTON, E_FIRST_TIME_INSTALLATION_NEXT, None, None, None, aDescriptionNext ) )


	def AddNextButton( self, aDescriptionNext ) :
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_PREV_NEXT_BUTTON, E_FIRST_TIME_INSTALLATION_NEXT, None, None, None, aDescriptionNext ) )


	def ShowDescription( self, aFocusId, aCustomId=0 ) :
		count = len( self.mControlList )

		for i in range( count ) :
			ctrlItem = self.mControlList[i]
			if self.HasControlItem( ctrlItem, aFocusId ) :
				if ctrlItem.mDescription == None :
					return False
				if aCustomId > 0 :
					self.getControl( aCustomId ).setLabel( ctrlItem.mDescription )				
				else :
					self.getControl( E_SETTING_DESCRIPTION ).setLabel( ctrlItem.mDescription )
		return False


	def EditDescription( self, aControlId, aDescription ) :
		count = len( self.mControlList )
		for i in range( count ) :
			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, aControlId ) :
				ctrlItem.mDescription = aDescription


	def SetDefaultControl( self ) :
		if self.mDataCache.GetDelaySettingWindow( ) :
			time.sleep( 1 )
			self.mDataCache.SetDelaySettingWindow( False )

		if ElisPropertyEnum( 'First Installation', self.mCommander ).GetProp( ) == 0 :
			if self.mControlList[0].mEnable :
				self.setFocusId( self.mControlList[0].mControlId + 1 )
			else :
				for i in range( self.GetControlListSize( ) ) :
					if self.mControlList[i].mEnable :
						self.setFocusId( self.mControlList[i].mControlId + 1 )
						return
		else :
			self.setFocusId( E_FIRST_TIME_INSTALLATION_NEXT )


	def HasControlItem( self, aCtrlItem, aContgrolId ) :
		if aCtrlItem.mControlType == aCtrlItem.E_SETTING_ENUM_CONTROL or aCtrlItem.mControlType == aCtrlItem.E_SETTING_USER_ENUM_CONTROL :
			if aCtrlItem.mControlId == aContgrolId or aCtrlItem.mControlId + 1 == aContgrolId or aCtrlItem.mControlId + 2 == aContgrolId or aCtrlItem.mControlId + 3 == aContgrolId  :
				return True
		elif aCtrlItem.mControlType == aCtrlItem.E_SETTING_INPUT_CONTROL :
			if aCtrlItem.mControlId == aContgrolId or aCtrlItem.mControlId + 1 == aContgrolId or aCtrlItem.mControlId + 3 == aContgrolId :	
				return True
		else :
			if aCtrlItem.mControlId == aContgrolId :
				return True

		return False


	def GetPrevId( self, aControlId ) :
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


	def GetNextId( self, aControlId ) :
		count = len( self.mControlList )
		nextId = -1
		found = False

		for i in range( count ) :
			ctrlItem = self.mControlList[i]

			if ctrlItem.mEnable and nextId <= 0 :
				nextId = ctrlItem.mControlId

			if ctrlItem.mEnable and found == True :
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
					return control.getSelectedPosition( )

		return -1


	def GetControlLabel2String( self, aControlId ) :
		count = len( self.mControlList )
		for i in range( count ) :
			ctrlItem = self.mControlList[i]
			if self.HasControlItem( ctrlItem, aControlId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_INPUT_CONTROL :
					return self.getControl( ctrlItem.mControlId + 3 ).getSelectedItem( ).getLabel2( )

		return -1


	def GetControlLabelString( self, aControlId ) :
		count = len( self.mControlList )
		for i in range( count ) :
			ctrlItem = self.mControlList[i]
			if self.HasControlItem( ctrlItem, aControlId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_INPUT_CONTROL :
					return self.getControl( ctrlItem.mControlId + 3 ).getSelectedItem( ).getLabel( )

		return -1


	def SetControlLabel2String( self, aControlId, aLabel ) :
		count = len( self.mControlList )

		for i in range( count ) :

			ctrlItem = self.mControlList[i]
			if self.HasControlItem( ctrlItem, aControlId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_INPUT_CONTROL :
					controllabel = self.getControl( ctrlItem.mControlId + 3 ).getSelectedItem( )
					if controllabel :
						controllabel.setLabel2( aLabel )
					
		return


	def SetControlLabelString( self, aControlId, aLabel ) :
		count = len( self.mControlList )

		for i in range( count ) :

			ctrlItem = self.mControlList[i]
			if self.HasControlItem( ctrlItem, aControlId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_INPUT_CONTROL :
					self.getControl( ctrlItem.mControlId + 3 ).getSelectedItem( ).setLabel( aLabel )

		return
		

	def GetGroupId( self, aContgrolId ) :
		count = len( self.mControlList )

		for i in range( count ) :

			ctrlItem = self.mControlList[i]
			if ctrlItem.mControlType == ctrlItem.E_SETTING_ENUM_CONTROL or ctrlItem.mControlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
				if ctrlItem.mControlId == aContgrolId or ctrlItem.mControlId + 1 == aContgrolId or ctrlItem.mControlId + 2 == aContgrolId or ctrlItem.mControlId + 3 == aContgrolId :
					return ctrlItem.mControlId

			elif ctrlItem.mControlType == ctrlItem.E_SETTING_INPUT_CONTROL :
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


	def SetFocusControl( self, aControlId ) :
		count = len( self.mControlList )

		for i in range( count ) :
			ctrlItem = self.mControlList[i]
			if aControlId == ctrlItem.mControlId :
				self.setFocusId( ctrlItem.mControlId )
				return True

		return False


	def ControlSelect( self ) :
		self.GetFocusId( )
		count = len( self.mControlList )

		for i in range( count ) :
			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, self.mFocusId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_ENUM_CONTROL :
					control = self.getControl( ctrlItem.mControlId + 3 )
					time.sleep( 0.02 )
					ctrlItem.mProperty.SetPropIndex( control.getSelectedPosition( ) )
					return True
					
		return False


	def ControlUp( self, aWin = None, aControlId = None ) :
		self.GetFocusId( )
		if aControlId :
			groupId = aControlId
		else :
			groupId = self.GetGroupId( self.mFocusId )
		prevId = self.GetPrevId( groupId )

		if self.GetIsInputNumberType( groupId ) :
			self.mResetInput = True
			if aWin :
				aWin.FocusChangedAction( groupId )

		if prevId > 0 and groupId != prevId :
			if groupId == E_FIRST_TIME_INSTALLATION_NEXT and prevId == E_FIRST_TIME_INSTALLATION_PREV :
				self.ControlUp( None, E_FIRST_TIME_INSTALLATION_PREV )
				return

			if prevId == E_FIRST_TIME_INSTALLATION_PREV :
				self.setFocusId( E_FIRST_TIME_INSTALLATION_NEXT )
			else :
				self.setFocusId( prevId )
			return True

		return False


	def ControlDown( self, aWin = None, aControlId = None ) :
		self.GetFocusId( )
		if aControlId :
			groupId = aControlId
		else :
			groupId = self.GetGroupId( self.mFocusId )
		nextId = self.GetNextId( groupId )

		if self.GetIsInputNumberType( groupId ) :
			self.mResetInput = True
			if aWin :
				aWin.FocusChangedAction( groupId )

		if nextId > 0 and groupId != nextId :
			if groupId == E_FIRST_TIME_INSTALLATION_PREV and nextId == E_FIRST_TIME_INSTALLATION_NEXT :
				self.ControlDown( None, E_FIRST_TIME_INSTALLATION_NEXT )
				return

			if nextId == E_FIRST_TIME_INSTALLATION_PREV :
				self.setFocusId( E_FIRST_TIME_INSTALLATION_NEXT )
			else :
				self.setFocusId( nextId )
			return True

		return False

	def ControlLeft( self ) :
		self.GetFocusId( )
		count = len( self.mControlList )

		for i in range( count ) :
			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, self.mFocusId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_ENUM_CONTROL or ctrlItem.mControlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
					if self.mFocusId % 10 == 2 :
						self.setFocusId( self.mFocusId - 1 )
						return


	def ControlRight( self ) :
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


	def SetProp( self, aControlId, aValue ) :
		count = len( self.mControlList )

		for i in range( count ) :
			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, aControlId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_ENUM_CONTROL :
					ctrlItem.mProperty.SetProp( aValue )
					return True


	def GetIsInputNumberType( self , aControlId ) :
		count = len( self.mControlList )
		for i in range( count ) :
			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, aControlId ) :
				if ctrlItem.mInputNumberType == None :
					return False
				else :
					return True

	
	def GetInputNumberType( self , aControlId ) :
		count = len( self.mControlList )
		for i in range( count ) :
			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, aControlId ) :
				return ctrlItem.mInputNumberType


	def GetControlMaxValue( self, aControlId ) :
		count = len( self.mControlList )
		for i in range( count ) :
			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, aControlId ) :
				return ctrlItem.mMax


	def GetControlMaxRange( self, aControlId ) :
		count = len( self.mControlList )
		for i in range( count ) :
			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, aControlId ) :
				string = '%d' % ctrlItem.mMax
				return len( string )


	def GlobalSettingAction( self, aWin, aAction ) :
		groupid = self.GetGroupId( self.getFocusId( ) )
		if self.GetInputNumberType( groupid ) == TYPE_NUMBER_NORMAL :
			if ( aAction >= Action.REMOTE_0 and aAction <= Action.REMOTE_9 ) or ( aAction >= Action.ACTION_JUMP_SMS2 and aAction <= Action.ACTION_JUMP_SMS9 ) :
				value = self.GetControlLabel2String( groupid )
				value = self.ParseNumber( value )
				if self.mResetInput == True or len( value ) == self.GetControlMaxRange( groupid ) :
					value = ''
					self.mResetInput = False

				if aAction >= Action.REMOTE_0 and aAction <= Action.REMOTE_9 :
					label = '%d' % int( value + '%d' % ( int( aAction ) - Action.REMOTE_0 ) )
	
				elif aAction >= Action.ACTION_JUMP_SMS2 and aAction <= Action.ACTION_JUMP_SMS9 :
					label = '%d' % int( value + '%d' % ( aAction - Action.ACTION_JUMP_SMS2 + 2 ) )

				if int( label ) > self.GetControlMaxValue( groupid ) :
					label = '%d' % self.GetControlMaxValue( groupid )

				if value != label :
					aWin.CallballInputNumber( groupid, label )


	def ParseNumber( self, aString ) :
		string = aString.split( )
		return string[0]
