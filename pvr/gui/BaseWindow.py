from pvr.gui.GuiConfig import *
from decorator import decorator
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
import pvr.ElisMgr
from ElisEnum import ElisEnum
import pvr.DataCacheMgr
import pvr.TunerConfigMgr 
from pvr.Util import RunThread, SetLock, SetLock2 
import pvr.Platform
from pvr.XBMCInterface import XBMC_GetVolume

import sys
import os
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

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
	if pvr.Platform.GetPlatform( ).GetXBMCVersion( ) < 12.0 :
		ACTION_PARENT_DIR		= 9		#Back	
	else :
		ACTION_PARENT_DIR		= 92		#Back 	


	ACTION_PREVIOUS_MENU		= 10 	#ESC
	ACTION_SHOW_INFO			= 11	# i(epg)
	ACTION_PAUSE				= 12	#space
	ACTION_STOP					= 13	#x
	ACTION_NEXT_ITEM			= 14	#>
	ACTION_PREV_ITEM			= 15	#<
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
	ACTION_PLAYER_FORWARD		= 77	#f
	ACTION_PLAYER_REWIND		= 78	#r
	ACTION_PLAYER_PLAY			= 79	#p 
	
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

	ACTION_MBOX_XBMC			= 400
	ACTION_MBOX_TVRADIO			= 401
	ACTION_MBOX_RECORD			= 402
	ACTION_MBOX_REWIND			= 403
	ACTION_MBOX_FF				= 404
	ACTION_MBOX_ARCHIVE			= 405
	ACTION_MBOX_SUBTITLE		= 406
	ACTION_MBOX_NUMLOCK			= 407
	ACTION_MBOX_TEXT			= 408

	ACTION_RELOAD_SKIN			= 34	#q
	ACTION_BUILT_IN_FUNCTION	= 122	#m
	ACTION_SHOW_GUI				= 18	#tab --> xbmc


	# re defined for another platform
	if not pvr.Platform.GetPlatform( ).IsPrismCube( ) :
		ACTION_MBOX_XBMC			= ACTION_SHOW_GUI
		ACTION_MBOX_TVRADIO			= ACTION_BUILT_IN_FUNCTION
		ACTION_MBOX_RECORD			= ACTION_PLAYER_REWIND
		ACTION_MBOX_REWIND			= ACTION_PREV_ITEM
		ACTION_MBOX_FF				= ACTION_NEXT_ITEM
		ACTION_MBOX_ARCHIVE			= ACTION_PLAYER_FORWARD


class Property( object ) :

	def GetListItemProperty( self, aListItem, aName ) :
		p = aListItem.getProperty( aName )
		if p is not None :
			return p.decode( 'utf-8' )


	def SetListItemProperty( self, aListItem, aName, aValue ) :
		if aListItem and aName and not aValue is None :
			aListItem.setProperty( aName, aValue )
		else:
			log.debug('ERR listItem=%s name=%s value=%s' % ( aListItem, aName, aValue ) )


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
		self.mParentID = -1
		self.mPlatform = pvr.Platform.GetPlatform( )


	@classmethod
	def GetName( cls ):
		return cls.__name__


	def SetParentID( self, aWindowID ) :
		self.mParentID = aWindowID


	def GetParentID( self ) :
		return self.mParentID


	def GetFocusId( self ) :
		self.mFocusId = self.getFocusId( )
		return self.mFocusId


	def GlobalAction( self, aActionId ) :
		mExecute = False
		if self.mDataCache.GetRunningHiddenTest( ) and aActionId == Action.ACTION_MBOX_FF :
			self.mDataCache.SetRunningHiddenTest( False )

		if self.mDataCache.GetMediaCenter( ) :
			if aActionId == Action.ACTION_PREVIOUS_MENU or aActionId == Action.ACTION_PARENT_DIR :
				#blocking action key during Channel_SetCurrentSync()
				mExecute = False
			else :
				mExecute = True

		if aActionId == Action.ACTION_MUTE :
			self.UpdateVolume( 0 )
			mExecute = True

		elif aActionId == Action.ACTION_VOLUME_UP :
			self.UpdateVolume( VOLUME_STEP )
			mExecute = True

		elif aActionId == Action.ACTION_VOLUME_DOWN :
			self.UpdateVolume( -VOLUME_STEP )
			mExecute = True

		elif E_SUPPORT_USE_KEY_Q and aActionId == Action.ACTION_RELOAD_SKIN :
			import pvr.gui.WindowMgr as WinMgr
			WinMgr.GetInstance( ).ReloadWindow( WinMgr.GetInstance( ).mLastId, WinMgr.WIN_ID_NULLWINDOW )
			mExecute = True

		return mExecute


	def SetPipScreen( self ) :
		from pvr.GuiHelper import GetInstanceSkinPosition
		ctrlImgVideoPos = self.getControl( E_SETTING_PIP_SCREEN_IMAGE )

		h = ctrlImgVideoPos.getHeight( )
		w = ctrlImgVideoPos.getWidth( )
		x, y = list( ctrlImgVideoPos.getPosition( ) )
		
		x, y, w, h = pvr.GuiHelper.GetInstanceSkinPosition( ).GetPipPosition( x, y, w, h )

		self.mDataCache.Player_SetVIdeoSize( x, y + 1, w, h - 2 )

		self.SetRadioScreen( )


	def SetRadioScreen( self, aType = -1 ) :
		radio = 'False'
		state = False
		if aType == -1 :
			aType = self.mDataCache.Zappingmode_GetCurrent( ).mServiceType

		if aType == ElisEnum.E_SERVICE_TYPE_RADIO :
			radio = 'True'
			state = True

		self.setProperty( 'TVRadio', radio )
		#LOG_TRACE('--------------radio--property[%s] type[%s]'% ( radio, aType ) )
		return radio


	def SetVideoRestore( self ) :
		self.mCommander.Player_SetVIdeoSize( 0, 0, 1280, 720 )


	def LoadNoSignalState( self ) :
		if self.mDataCache.GetLockedState( ) == ElisEnum.E_CC_FAILED_SCRAMBLED_CHANNEL :
			self.setProperty( 'Signal', 'Scramble' )
			state = 'Scramble'
		elif self.mDataCache.GetLockedState( ) == ElisEnum.E_CC_FAILED_NO_SIGNAL :
			self.setProperty( 'Signal', 'False' )
			state = 'False'
		else :
			self.setProperty( 'Signal', 'True' )
			state = 'True'


	def VisibleTuneStatus( self , aFlag ) :
		self.getControl( E_SETTING_LABEL_PIP_NO_SIGNAL ).setVisible( aFlag )
		self.getControl( E_SETTING_LABEL_PIP_SCRAMBLED ).setVisible( aFlag )


	def UpdateVolume( self, aVolumeStep = -1 ) :
		volume = 0
		if self.mPlatform.IsPrismCube( ) :
			volume =  XBMC_GetVolume( )		
		else :
			volume = self.mCommander.Player_GetVolume( )
			if aVolumeStep != -1 :
				if aVolumeStep == 0 :
					if self.mCommander.Player_GetMute( ) :
						self.mCommander.Player_SetMute( False )
						return
					else :
						volume = aVolumeStep

				else :
					volume += aVolumeStep / 2

		LOG_TRACE( 'GET VOLUME=%d' %volume )

		if volume > MAX_VOLUME :
			volume = MAX_VOLUME

		if volume <= 0 :
			volume = 0
			self.mCommander.Player_SetMute( True )
		else :
			if self.mCommander.Player_GetMute( ) :
				self.mCommander.Player_SetMute( False )
			self.mCommander.Player_SetVolume( volume )


	def UpdateControlListSelectItem( self, aListControl, aIdx = 0 ) :
		startTime = time.time()
		loopTime = 0.0
		sleepTime = 0.01
		while loopTime < 1.5 :
			aListControl.selectItem( aIdx )
			if aIdx == aListControl.getSelectedPosition( ) :
				break
			time.sleep( sleepTime )
			loopTime += sleepTime

		#LOG_TRACE('-----------control[%s] idx setItem time[%s]'% ( aListControl.getId( ), ( time.time() - startTime ) ) )


	def UpdateSetFocus( self, aControlId ) :
		startTime = time.time()
		loopTime = 0.0
		sleepTime = 0.01
		while loopTime < 1.5 :
			self.setFocusId( aControlId )
			if aControlId == self.getFocusId( ) :
				break
			time.sleep( sleepTime )
			loopTime += sleepTime

		#LOG_TRACE('-----------control[%s] setFocus time[%s]'% ( aControlId, ( time.time() - startTime ) ) )


	def SetMediaCenter( self ) :
		self.mDataCache.SetMediaCenter( True )
		self.mCommander.AppMediaPlayer_Control( 1 )


	def CheckMediaCenter( self ) :
		if self.mDataCache.GetMediaCenter( ) == True :
			self.mCommander.AppMediaPlayer_Control( 0 )
			#current channel re-zapping
			iChannel = self.mDataCache.Channel_GetCurrent( )
			if iChannel :
				self.mDataCache.Channel_InvalidateCurrent( )
				self.mDataCache.Channel_SetCurrentSync( iChannel.mNumber, iChannel.mServiceType )

			self.UpdateVolume( )
			pvr.gui.WindowMgr.GetInstance( ).CheckGUISettings( )
			self.mDataCache.SetMediaCenter( False )

		self.SetRadioScreen( )


	def OpenBusyDialog( self ) :
		xbmc.executebuiltin( "ActivateWindow(busydialog)" )


	def CloseBusyDialog( self ) :
		xbmc.executebuiltin( "Dialog.Close(busydialog)" )


	def NotificationDialog( self, aMsg1, aMsg2, aTimeMs = 2000, aImage = '' ) :
		command = 'Notification(%s,%s,%s,%s)'% ( aMsg1, aMsg2, aTimeMs, aImage )
		xbmc.executebuiltin( command )


	def NotAvailAction( self ) :
		self.setProperty( 'NotAvail', 'True' )
		loopTime = 0.01
		sleepTime = 0.2
		while loopTime < 0.5 :
			if loopTime > sleepTime :
				#LOG_TRACE( '-------loopTime[%s]'% loopTime )
				self.setProperty( 'NotAvail', 'False' )
				if self.getProperty( 'NotAvail' ) == 'False' :
					break

			time.sleep( 0.05 )
			loopTime += 0.05

		if self.getProperty( 'NotAvail' ) != 'False' :
			self.setProperty( 'NotAvail', 'False' )
			LOG_TRACE( '-------confirm again : setProperty False' )


	def SetPipLabel( self ) :
		self.getControl( E_SETTING_LABEL_PIP_NO_SIGNAL ).setLabel( MR_LANG( '[I]No Signal[/I] ' ) )
		self.getControl( E_SETTING_LABEL_PIP_SCRAMBLED ).setLabel( MR_LANG( '[I]Scrambled[/I] ' ) )


class ControlItem :
	# Setting Window
	E_UNDEFINE								= 0
	E_SETTING_ENUM_CONTROL					= 1
	E_SETTING_USER_ENUM_CONTROL				= 2
	E_SETTING_INPUT_CONTROL					= 3
	E_SETTING_PREV_NEXT_BUTTON				= 4


	def __init__( self, aControlType, aControlId, aProperty, aListItems, aSelecteItem, aDescription ) :
		self.mEnable	= True
		self.mControlType = aControlType	
		self.mControlId  = aControlId
		self.mProperty = aProperty		# E_SETTING_ENUM_CONTROL : propery, E_SETTING_INPUT_CONTROL : input type
		self.mListItems = aListItems
		self.mSelecteItem = aSelecteItem
		self.mDescription = aDescription
	

class SettingWindow( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mControlList = []
		self.mTunerMgr = pvr.TunerConfigMgr.GetInstance( )


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
		del self.mControlList[:]


	def SetSettingWindowLabel( self, aLabel ) :
		self.getControl( E_SETTING_MINI_TITLE ).setLabel( MR_LANG( 'Installation' ) )
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


	def AddInputControl( self, aControlId , aTitleLabel, aInputLabel, aDescription=None ) :
		listItems = []
		listItem = xbmcgui.ListItem( aTitleLabel, aInputLabel )
		listItems.append( listItem )
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_INPUT_CONTROL, aControlId, None, listItems, None, aDescription ) )


	def AddPrevNextButton( self, aDescriptionNext, aDescriptionPrev ) :
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_PREV_NEXT_BUTTON, E_FIRST_TIME_INSTALLATION_NEXT, None, None, None, aDescriptionNext ) )
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_PREV_NEXT_BUTTON, E_FIRST_TIME_INSTALLATION_PREV, None, None, None, aDescriptionPrev ) ) 		


	def AddNextButton( self, aDescriptionNext ) :
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_PREV_NEXT_BUTTON, E_FIRST_TIME_INSTALLATION_NEXT, None, None, None, aDescriptionNext ) )


	def ShowDescription( self, aFocusId ) :
		count = len( self.mControlList )

		for i in range( count ) :
			ctrlItem = self.mControlList[i]
			if self.HasControlItem( ctrlItem, aFocusId ) :
				if ctrlItem.mDescription == None :
					return False
				self.getControl( E_SETTING_DESCRIPTION ).setLabel( ctrlItem.mDescription )
		return False


	def EditDescription( self, aControlId, aDescription ) :
		count = len( self.mControlList )
		for i in range( count ) :
			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, aControlId ) :
				ctrlItem.mDescription = aDescription


	def setDefaultControl( self ) :
		if self.mControlList[0].mEnable :
			self.setFocusId( self.mControlList[0].mControlId )
		else :
			for i in range( self.GetControlListSize( ) ) :
				if self.mControlList[i].mEnable :
					self.setFocusId( self.mControlList[i].mControlId )
					break


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


class LivePlateWindow( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mControls = {}

	def InitControl( self ) :
		for i in range( 1, E_CTRL_BTN_INFO_MAX+1 ) :
			controlId = E_CTRL_GROUP_INFO + i
			ctrl = self.getControl( controlId )
			self.mControls[controlId] = ctrl


	def SetVisibleControls( self, aControls, aVisible ) :
		for controlId in aControls :
			ctrl = self.mControls.get( controlId, None )
			if ctrl :
				ctrl.setVisible( aVisible )


	def SetEnableControl( self, aControlId, aEnable ) :
		ctrl = self.mControls.get( aControlId, None )
		if ctrl :
			ctrl.setEnabled( aEnable )



