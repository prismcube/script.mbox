import xbmc
import xbmcgui
import time
import sys

from decorator import decorator
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.GuiConfig import *
import pvr.ElisMgr
import pvr.DataCacheMgr
import pvr.TunerConfigMgr
import thread
from pvr.Util import RunThread, GuiLock, GuiLock2, MLOG, LOG_WARN, LOG_TRACE, LOG_ERR

class Action(object) :
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

	ACTION_CONTEXT_MENU			= 117   # infokey - guid/title

	ACTION_JUMP_SMS2			= 142
	ACTION_JUMP_SMS3			= 143
	ACTION_JUMP_SMS4			= 144
	ACTION_JUMP_SMS5			= 145
	ACTION_JUMP_SMS6			= 146
	ACTION_JUMP_SMS7			= 147
	ACTION_JUMP_SMS8			= 148
	ACTION_JUMP_SMS9			= 149
	

class Property(object) :

	def GetListItemProperty(self, aListItem, aName) :
		p = aListItem.getProperty(aName)
		if p is not None:
			return p.decode('utf-8')


	def SetListItemProperty(self, aListItem, aName, aValue) :
		if aListItem and aName and not aValue is None:
			aListItem.setProperty(aName, aValue)
		else:
			log.debug('ERR listItem=%s name=%s value=%s' % (aListItem, aName, aValue))


class BaseWindow( xbmcgui.WindowXML, Property ) :

	def __init__( self, *args, **kwargs ) :
		xbmcgui.WindowXML.__init__( self, *args, **kwargs )
		self.mWin = None
		self.mWinId = 0
		self.mClosed = False

		self.mFocusId = -1
		self.mLastFocused = -1
		self.mInitialized = False
		
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.mEventBus = pvr.ElisMgr.GetInstance( ).GetEventBus( )
		self.mDataCache = pvr.DataCacheMgr.GetInstance( )

	@classmethod
	def GetName(cls):
		return cls.__name__


	def GetFocusId( self ) :
		GuiLock2( True )
		self.mFocusId = self.getFocusId( )
		GuiLock2( False )
		return self.mFocusId


	def GlobalAction( self, aActionId ) :
	
		if aActionId == Action.ACTION_MUTE:
			self.UpdateVolume( )

		elif aActionId == Action.ACTION_VOLUME_UP:
			self.UpdateVolume( )

		elif aActionId == Action.ACTION_VOLUME_DOWN:
			self.UpdateVolume( )


	def SetPipScreen( self ) :
		ctrlImgVideoPos = self.getControl( E_SETTING_PIP_SCREEN_IMAGE )

		h = ctrlImgVideoPos.getHeight( )
		w = ctrlImgVideoPos.getWidth( )
		x, y = list( ctrlImgVideoPos.getPosition( ) )
		ret = self.mCommander.Player_SetVIdeoSize( x, y, w, h )


	def SetVideoRestore( self ) :
		ret = self.mCommander.Player_SetVIdeoSize( 0, 0, 1280, 720 )


	#@GuiLock
	def UpdateVolume( self ) :

		GuiLock2(True)
		retVolume = xbmc.executehttpapi('getvolume()')
		GuiLock2(False)
		volume = int( retVolume[4:] )
		LOG_TRACE('GET VOLUME=%d' %volume )

		if volume > MAX_VOLUME :
			volume = MAX_VOLUME

		if volume < 0 :
			volume = 0
			self.mCommander.Player_SetMute( True )
		else :
			if self.mCommander.Player_GetMute( ) == True :
				self.mCommander.Player_SetMute( False )
			self.mCommander.Player_SetVolume( volume )


	def OpenBusyDialog( self ) :
		#self.setProperty( 'BusyDialogBackground', 'True' )
		xbmc.executebuiltin( "ActivateWindow(busydialog)" )


	def CloseBusyDialog( self ) :
		#self.setProperty( 'BusyDialogBackground', 'False' )
		xbmc.executebuiltin( "Dialog.Close(busydialog)" )


class ControlItem :
	# Setting Window
	E_UNDEFINE								= 0
	E_SETTING_ENUM_CONTROL					= 1
	E_SETTING_USER_ENUM_CONTROL				= 2
	E_SETTING_INPUT_CONTROL					= 3
	E_SETTING_PREV_NEXT_BUTTON				= 4


	def __init__( self, aControlType, aControlId, aProperty, aListItems, aSelecteItem, aDescription ) :	
		self.mControlType = aControlType	
		self.mControlId  = aControlId
		self.mProperty = aProperty		# E_SETTING_ENUM_CONTROL : propery, E_SETTING_INPUT_CONTROL : input type
		self.mListItems = aListItems
		self.mEnable	= True
		self.mDescription = aDescription
		self.mSelecteItem = aSelecteItem
	

class SettingWindow( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__(self, *args, **kwargs)
		self.mControlList = []
		self.mTunerMgr = pvr.TunerConfigMgr.GetInstance( )


	def InitControl( self ) :
		pos = 0
		for ctrlItem in self.mControlList:
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

			if ctrlItem.mControlId == E_FIRST_TIME_INSTALLATION_PREV :
				self.getControl( ctrlItem.mControlId ).setPosition( 0,  470 )
			elif ctrlItem.mControlId == E_FIRST_TIME_INSTALLATION_NEXT :
				self.getControl( ctrlItem.mControlId ).setPosition( 690, 470 )
			else :
				pos += self.getControl( ctrlItem.mControlId ).getHeight( )
				self.getControl( ctrlItem.mControlId ).setPosition( 0, pos )


	def ResetAllControl( self ) :
		del self.mControlList[:]


	def SetSettingWindowLabel( self, aLabel ) :
		self.getControl( E_SETTING_MINI_TITLE ).setLabel( aLabel )
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


	def AddEnumControl( self, aControlId, aPropName, aTitleLabel=None, aDescription=None ) :
		property = ElisPropertyEnum( aPropName, self.mCommander )
		listItems = []
		for i in range( property.GetIndexCount() ) :
			if aTitleLabel == None :
				listItem = xbmcgui.ListItem( property.GetName(), property.GetPropStringByIndex( i ) )
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


	def AddInputControl( self, aControlId , aTitleLabel, aInputLabel, aDescription=None ) :
		listItems = []
		listItem = xbmcgui.ListItem( aTitleLabel, aInputLabel )
		listItems.append( listItem )
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_INPUT_CONTROL, aControlId, None, listItems, None, aDescription ) )


	def AddPrevNextButton( self ) :
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_PREV_NEXT_BUTTON, E_FIRST_TIME_INSTALLATION_PREV, None, None, None, None ) ) 
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_PREV_NEXT_BUTTON, E_FIRST_TIME_INSTALLATION_NEXT, None, None, None, None ) )


	def AddNextButton( self ) :
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_PREV_NEXT_BUTTON, E_FIRST_TIME_INSTALLATION_NEXT, None, None, None, None ) )


	def ShowDescription( self ) :
		self.GetFocusId( )
		count = len( self.mControlList )

		for i in range( count ) :
			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, self.mFocusId ) :
				if ctrlItem.mDescription == None :
					return False
				self.getControl( E_SETTING_DESCRIPTION ).setLabel( ctrlItem.mDescription )
		return False


	def HasControlItem( self, aCtrlItem, aContgrolId  ) :
		if aCtrlItem.mControlType == aCtrlItem.E_SETTING_ENUM_CONTROL or aCtrlItem.mControlType == aCtrlItem.E_SETTING_USER_ENUM_CONTROL :
			if aCtrlItem.mControlId == aContgrolId or aCtrlItem.mControlId + 1 == aContgrolId or aCtrlItem.mControlId + 2 == aContgrolId or aCtrlItem.mControlId + 3 == aContgrolId  :
				return True
		elif aCtrlItem.mControlType == aCtrlItem.E_SETTING_INPUT_CONTROL :
			if aCtrlItem.mControlId == aContgrolId or aCtrlItem.mControlId + 1 == aContgrolId  or aCtrlItem.mControlId + 3 == aContgrolId :	
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
					self.getControl( ctrlItem.mControlId + 3 ).getSelectedItem( ).setLabel2( aLabel )
					
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
				self.setFocusId( ctrlItem.mControlId + 1 )
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


	def ControlUp( self ) :

		self.GetFocusId( )
		groupId = self.GetGroupId( self.mFocusId )
		prevId = self.GetPrevId( groupId )

		if prevId > 0 and groupId != prevId :
			self.setFocusId( prevId )
			return True

		return False


	def ControlDown( self ) :

		self.GetFocusId( )
		groupId = self.GetGroupId( self.mFocusId )
		nextId = self.GetNextId( groupId )

		if nextId > 0 and groupId != nextId :
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
	

	def DrawFirstTimeInstallationStep( self, aStep ) :
		if aStep == None :
			for i in range( FIRST_TIME_INSTALLATION_STEP ) :
				self.getControl( E_FIRST_TIME_INSTALLATION_STEP_IMAGE_BACK + i ).setVisible( False )
				self.getControl( E_FIRST_TIME_INSTALLATION_STEP_IMAGE + i ).setVisible( False )
		else :
			for i in range( FIRST_TIME_INSTALLATION_STEP ) :
				if i == aStep :
					self.getControl( E_FIRST_TIME_INSTALLATION_STEP_IMAGE + i ).setVisible( True )
				else :
					self.getControl( E_FIRST_TIME_INSTALLATION_STEP_IMAGE + i ).setVisible( False )
				self.getControl( E_FIRST_TIME_INSTALLATION_STEP_IMAGE_BACK + i ).setVisible( True )


	def ScanHelper_Start( self ) :
		self.mCommander.ScanHelper_Start( )
		self.setProperty( 'ViewProgress', 'True' )


	def ScanHelper_ChangeContext( self, aSatellite, aTp ) :
		if aSatellite and aTp :
			self.ScanHerper_Progress( 0, 0, 0 )
			transpondertemp = []
			transpondertemp.append( aTp )
			satellitetemp = []
			satellitetemp.append( aSatellite )
			self.mCommander.ScanHelper_ChangeContext( transpondertemp, satellitetemp )
		else :
			LOG_ERR( 'ScanHelper_ChangeContext : Satellite or Tp is None' )


	def ScanHelper_ChangeContextByCarrier( self, aTp ) :
		if aTp :
			self.ScanHerper_Progress( 0, 0, 0 )
			transpondertemp = []
			transpondertemp.append( aTp )
			self.mCommander.ScanHelper_ChangeContextByCarrier( transpondertemp )
		else :
			LOG_ERR( 'ScanHelper_ChangeContextByCarrier : Tp is None' )


	def ScanHelper_Stop( self ) :
		self.mCommander.ScanHelper_Stop( True )
		self.setProperty( 'ViewProgress', 'False' )

	def ScanHerper_Progress( self, aStrength, aQuality, aLocked ) :
		if aLocked == False :
			aQuality = 0
		else :
			if aQuality > 100 :
				aQuality = 100
			elif aQuality < 0 :
				aQuality = 0
		if aStrength > 100 :
			aStrength = 100
		elif aStrength < 0 :
			aStrength = 0

		self.getControl( E_SCAN_HELPER_LABEL_STRENGTH ).setLabel( str( '%s %%' % aStrength ) )
		self.getControl( E_SCAN_HELPER_LABEL_QUALITY ).setLabel( str( '%s %%' % aQuality ) )
		
		self.getControl( E_SCAN_HELPER_PROGRESS_STRENGTH ).setPercent( aStrength )
		self.getControl( E_SCAN_HELPER_PROGRESS_QUALITY ).setPercent( aQuality )