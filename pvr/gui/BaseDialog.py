from pvr.gui.GuiConfig import *
from pvr.gui.BaseWindow import Property
from elisinterface.ElisProperty import ElisPropertyEnum, ElisPropertyInt
import pvr.ElisMgr
from pvr.gui.BaseWindow import Action
from pvr.Util import RunThread, SetLock, SetLock2
import pvr.Platform
from pvr.XBMCInterface import XBMC_GetVolume, XBMC_GetMute

import sys
import os
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson
    
class BaseDialog( xbmcgui.WindowXMLDialog, Property ) :
	def __init__( self, *args, **kwargs ) :
		xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
		self.mWin = None
		self.mWinId = 0

		self.mLastFocused = -1
		self.mInitialized = False

		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.mEventBus = pvr.ElisMgr.GetInstance( ).GetEventBus( )
		self.mDataCache = pvr.DataCacheMgr.GetInstance( )
		self.mPlatform = pvr.Platform.GetPlatform( )


	@classmethod
	def GetName( cls ) :
		return cls.__name__


	def SetHeaderLabel( self, aLabel ):
		self.getControl( G_DIALOG_HEADER_LABEL_ID ).setLabel( aLabel )


	def SetButtonLabel( self, aControlId, aLabel ) :
		self.getControl( aControlId ).setLabel( aLabel )
	

	def CloseDialog( self ) :
		#self.clearProperty( 'AnimationWaitingDialogOnClose' )
		self.close( )
		time.sleep( 0.2 )


	def SetFrontdisplayMessage( self, aMessage ) :
		self.mDataCache.Frontdisplay_SetMessage( aMessage )


	def GetFocusId( self ):
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

		return mExecute


	def GetAudioStatus( self ) :
		mute, volume = ( False, 0 )
		if self.mDataCache.Get_Player_AVBlank( ) :
			LOG_TRACE( '----------GetAudioStatus avblank' )
			mute = True

		if self.mPlatform.IsPrismCube( ) :
			if self.mPlatform.GetXBMCVersion( ) >= self.mPlatform.GetFrodoVersion( ) :
				if not mute :
					mute = XBMC_GetMute( )
				volume =  XBMC_GetVolume( )

		else :
			if not mute :
				mute = self.mCommander.Player_GetMute( )
			volume = self.mCommander.Player_GetVolume( )

		return mute, volume


	def UpdateVolume( self, aVolumeStep = -1 ) :
		#blocking by avBlank
		if self.mDataCache.Get_Player_AVBlank( ) :
			LOG_TRACE( '----------blocking avblank' )
			return

		volume = 0
		if self.mPlatform.IsPrismCube( ) :
			if self.mPlatform.GetXBMCVersion( ) >= self.mPlatform.GetFrodoVersion( ) and \
			   aVolumeStep == 0 : 
				mute = True
				if self.mCommander.Player_GetMute( ) :
					mute = False
				self.mCommander.Player_SetMute( mute )
				#if XBMC_GetMute( ) != mute :
				#	XBMC_SetVolume( volume, mute )
				#	LOG_TRACE( 'mute sync' )

				return

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
			
		if volume < 0 :
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


	def UpdateSetFocus( self, aControlId, aUserTime = 0 ) :
		ret = False
		startTime = time.time()
		loopTime = 0.0
		sleepTime = 0.01
		while loopTime < ( 1.5 + aUserTime ) :
			self.setFocusId( aControlId )
			if aControlId == self.GetFocusId( ) :
				ret = True
				break
			time.sleep( sleepTime )
			loopTime += sleepTime

		#LOG_TRACE('-----------control[%s] setFocus time[%s]'% ( aControlId, ( time.time() - startTime ) ) )
		return ret


class ControlItem:
	# Setting Window
	E_UNDEFINE								= 0
	E_SETTING_ENUM_CONTROL					= 1
	E_SETTING_USER_ENUM_CONTROL				= 2
	E_SETTING_INPUT_CONTROL					= 3
	E_SETTING_OK_CANCEL_BUTTON				= 4
	E_SETTING_CLOSE_BUTTON					= 5
	E_SETTING_LIST_CONTROL					= 6
	E_LABEL_CONTROL							= 7
	E_CUSTOM_CONTROL						= 99
	

	def __init__( self, aControlType, aControlId, aProperty, aListItems, aSelecteItem, aDescription = None, aInputNumberType = None, aMax = 0 ) :
		self.mControlType		= aControlType	
		self.mControlId			= aControlId
		self.mProperty			= aProperty		# E_SETTING_ENUM_CONTROL : propery, E_SETTING_INPUT_CONTROL : input type
		self.mListItems			= aListItems
		self.mInputNumberType	= aInputNumberType
		self.mMax				= aMax
		
		if self.mControlType == self.E_LABEL_CONTROL :
			self.mEnable		= False
		else :
			self.mEnable		= True
			
		self.mDescription		= aDescription
		self.mSelecteItem		= aSelecteItem
		
		self.mVisible			= True
	

class SettingDialog( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mControlList		= []
		self.mFocusId			= -1
		self.mIsAutomaticHeight	= False
		self.mIsOkCancelType	= False
		self.mResetInput		= True


	def InitControl( self ) :
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_CLOSE_BUTTON, E_SETTING_DIALOG_BUTTON_CLOSE, None, None, None, None ) )	
		self.getControl( E_SETTING_DIALOG_MAIN_GOURP_ID ).setVisible( False )
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
			elif ctrlItem.mControlType == ctrlItem.E_SETTING_LIST_CONTROL :
				control = self.getControl( ctrlItem.mControlId + 2 )
				control.reset( )
				control.addItems( ctrlItem.mListItems )
				control.selectItem( ctrlItem.mSelecteItem )


	def UpdateLocation( self, aExtraX = 0, aExtraY = 0 ) :
		pos = 0	
		for ctrlItem in self.mControlList :
			if ctrlItem.mVisible == False or ctrlItem.mControlId == E_SETTING_DIALOG_BUTTON_CLOSE :
				continue

			if ctrlItem.mControlId == E_SETTING_DIALOG_BUTTON_OK_ID :
				self.getControl( ctrlItem.mControlId ).setPosition( 57,  pos + 93 )
			elif ctrlItem.mControlId == E_SETTING_DIALOG_BUTTON_CANCEL_ID :
				self.getControl( ctrlItem.mControlId ).setPosition( 277, pos + 93 )
			else :
				pos += self.getControl( ctrlItem.mControlId ).getHeight( )
				self.getControl( ctrlItem.mControlId ).setPosition( 0, pos + 33 )
	
		if self.mIsAutomaticHeight == True :
			if self.mIsOkCancelType == True :
				self.getControl( E_SETTING_DIALOG_BACKGROUND_IMAGE_ID ).setHeight( pos + 165 + aExtraY )
			else :
				self.getControl( E_SETTING_DIALOG_BACKGROUND_IMAGE_ID ).setHeight( pos + 135 + aExtraY )

		height = self.getControl( E_SETTING_DIALOG_BACKGROUND_IMAGE_ID ).getHeight( ) + aExtraY
		start_x = E_WINDOW_WIDTH / 2 - 610 / 2
		start_y = E_WINDOW_HEIGHT / 2 - height / 2
		self.getControl( E_SETTING_DIALOG_MAIN_GOURP_ID ).setPosition( start_x, start_y )
		self.getControl( E_SETTING_DIALOG_MAIN_GOURP_ID ).setVisible( True )
	

	def SetAutoHeight( self, mMode ) :
		self.mIsAutomaticHeight = mMode


	def ResetAllControl( self ) :
		del self.mControlList[:]


	def GetControlIdToListIndex( self, aControlId ) :
		count = len( self.mControlList )
		for i in range( count ) :
			if aControlId == self.mControlList[i].mControlId :
				return i

		print 'Unkown ControlId'

		
	def AddEnumControl( self, aControlId, aPropName, aTitleLabel=None, aDescription=None ) :
		property = ElisPropertyEnum( aPropName, self.mCommander )
		listItems = []
		for i in range( property.GetIndexCount( ) ) :
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


	def AddListControl( self, aControlId, aItemList, aSelectItem, aDescription=None ) :	
		listItems = []
		for i in range( len( aItemList ) ) :
			listItem = xbmcgui.ListItem( aItemList[i] )
			listItems.append( listItem )
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_LIST_CONTROL, aControlId, None, listItems, int( aSelectItem ), aDescription ) )


	def AddInputControl( self, aControlId , aTitleLabel, aInputLabel, aDescription = None, aInputNumberType = None, aMax = 0 ) :
		listItems = []
		listItem = xbmcgui.ListItem( aTitleLabel, aInputLabel )
		listItems.append( listItem )
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_INPUT_CONTROL, aControlId, None, listItems, None, aDescription, aInputNumberType, aMax ) )


	def AddOkCanelButton( self ) :
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_OK_CANCEL_BUTTON, E_SETTING_DIALOG_BUTTON_OK_ID, None, None, None, None ) ) 
		self.mControlList.append( ControlItem( ControlItem.E_SETTING_OK_CANCEL_BUTTON, E_SETTING_DIALOG_BUTTON_CANCEL_ID, None, None, None, None ) )
		self.mIsOkCancelType = True


	def AddLabelControl( self, aControlId, aDescription=None ) :
		self.mControlList.append( ControlItem( ControlItem.E_LABEL_CONTROL, aControlId, None, None, None, aDescription ) )


	def AddCustomControl( self, aControlId, aDescription=None ) :
		self.mControlList.append( ControlItem( ControlItem.E_CUSTOM_CONTROL, aControlId, None, None, None, aDescription ) )


	def HasControlItem( self, aCtrlItem, aContgrolId  ) :
		if aCtrlItem.mControlType == aCtrlItem.E_SETTING_ENUM_CONTROL or aCtrlItem.mControlType == aCtrlItem.E_SETTING_USER_ENUM_CONTROL :
			if aCtrlItem.mControlId == aContgrolId or aCtrlItem.mControlId + 1 == aContgrolId or aCtrlItem.mControlId + 2 == aContgrolId or aCtrlItem.mControlId + 3 == aContgrolId  :
				return True

		if aCtrlItem.mControlType == aCtrlItem.E_SETTING_LIST_CONTROL :
			if aCtrlItem.mControlId == aContgrolId or aCtrlItem.mControlId + 1 == aContgrolId or aCtrlItem.mControlId + 2 == aContgrolId :
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

			if ctrlItem.mEnable and ctrlItem.mVisible :
				prevId = ctrlItem.mControlId

		return prevId


	def GetNextId( self, aControlId ) :
		count = len( self.mControlList )
		nextId = -1
		found = False
		
		for i in range( count ) :
			ctrlItem = self.mControlList[i]

			if ctrlItem.mEnable and nextId <= 0  and ctrlItem.mVisible :
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
				elif ctrlItem.mControlType == ctrlItem.E_SETTING_LIST_CONTROL :
					control = self.getControl( ctrlItem.mControlId + 2 )
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
				elif ctrlItem.mControlType == ctrlItem.E_LABEL_CONTROL :
					return self.getControl( ctrlItem.mControlId ).getLabel( )				

		return -1


	def SetControlLabel2String( self, aControlId, aLabel ) :
		count = len( self.mControlList )

		for i in range( count ) :

			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, aControlId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_INPUT_CONTROL :
					self.getControl( ctrlItem.mControlId + 3 ).getSelectedItem( ).setLabel2( aLabel )					

		return -1


	def SetControlLabelString( self, aControlId, aLabel ) :
		count = len( self.mControlList )

		for i in range( count ) :

			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, aControlId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_INPUT_CONTROL or \
				   ctrlItem.mControlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
					self.getControl( ctrlItem.mControlId + 3 ).getSelectedItem( ).setLabel( aLabel )
				elif ctrlItem.mControlType == ctrlItem.E_LABEL_CONTROL :
					self.getControl( ctrlItem.mControlId ).setLabel( aLabel )

		return -1


	def SetListControlTitle( self, aControlId, aLabel ) :
		count = len( self.mControlList )

		for i in range( count ) :

			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, aControlId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_LIST_CONTROL or \
				   ctrlItem.mControlType == ctrlItem.E_SETTING_ENUM_CONTROL or ctrlItem.mControlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
					self.getControl( ctrlItem.mControlId + 1 ).setLabel( aLabel )

		return -1


	def SetListControlItemLabel( self, aControlId, aLabel ) :
		count = len( self.mControlList )

		for i in range( count ) :

			ctrlItem = self.mControlList[i]		
			if self.HasControlItem( ctrlItem, aControlId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_LIST_CONTROL :
					self.getControl( ctrlItem.mControlId + 2 ).getSelectedItem( ).setLabel( aLabel )
				elif ctrlItem.mControlType == ctrlItem.E_SETTING_ENUM_CONTROL or ctrlItem.mControlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
					self.getControl( ctrlItem.mControlId + 3 ).getSelectedItem( ).setLabel2( aLabel )

		return -1


	def GetGroupId( self, aContgrolId ) :

		count = len( self.mControlList )

		for i in range( count ) :

			ctrlItem = self.mControlList[i]
			if ctrlItem.mControlType == ctrlItem.E_SETTING_ENUM_CONTROL or ctrlItem.mControlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
				if ctrlItem.mControlId == aContgrolId or ctrlItem.mControlId + 1 == aContgrolId or ctrlItem.mControlId + 2 == aContgrolId or ctrlItem.mControlId + 3 == aContgrolId :
					return ctrlItem.mControlId

			elif ctrlItem.mControlType == ctrlItem.E_SETTING_LIST_CONTROL :
				if ctrlItem.mControlId == aContgrolId or ctrlItem.mControlId + 1 == aContgrolId or ctrlItem.mControlId + 2 == aContgrolId :
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


	def GetEnableControl( self, aControlId ) :

		count = len( self.mControlList )

		for i in range( count ) :
			ctrlItem = self.mControlList[i]
			if aControlId == ctrlItem.mControlId :
				return ctrlItem.mEnable

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


	def SetFocus( self, aFocusId ) :
		groupId = self.GetGroupId( aFocusId )
		if groupId >= 0 :
			self.setFocusId( groupId )		


	def ControlUp( self, aWin = None ) :	
		self.GetFocusId( )
		groupId = self.GetGroupId( self.mFocusId )
		prevId = self.GetPrevId( groupId )

		if self.GetIsInputNumberType( groupId ) :
			self.mResetInput = True
			if aWin :
				aWin.FocusChangedAction( groupId )

		if prevId > 0 and groupId != prevId :
			self.setFocusId( prevId )
			return True

		return False


	def ControlDown( self, aWin = None ) :
		self.GetFocusId( )
		groupId = self.GetGroupId( self.mFocusId )
		nextId = self.GetNextId( groupId )

		if self.GetIsInputNumberType( groupId ) :
			self.mResetInput = True
			if aWin :
				aWin.FocusChangedAction( groupId )

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
				if ctrlItem.mControlType == ctrlItem.E_SETTING_ENUM_CONTROL or ctrlItem.mControlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
					control = self.getControl( ctrlItem.mControlId + 3 )
					control.selectItem( aPosition )
					return True
				elif ctrlItem.mControlType == ctrlItem.E_SETTING_LIST_CONTROL :
					control = self.getControl( ctrlItem.mControlId + 2 )
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


	def GetListItems( self, aControlId ) :
		count = len( self.mControlList )
		for i in range( count ) :
			ctrlItem = self.mControlList[i]
			if self.HasControlItem( ctrlItem, aControlId ) :
				if ctrlItem.mControlType == ctrlItem.E_SETTING_ENUM_CONTROL or ctrlItem.mControlType == ctrlItem.E_SETTING_USER_ENUM_CONTROL :
					return ctrlItem.mListItems
				elif ctrlItem.mControlType == ctrlItem.E_SETTING_LIST_CONTROL :
					return ctrlItem.mListItems


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

