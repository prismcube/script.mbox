from pvr.gui.GuiConfig import *
import pvr.ElisMgr
import pvr.ChannelLogoMgr
from elisinterface.ElisEnum import ElisEnum
import pvr.DataCacheMgr
import pvr.Platform
from pvr.XBMCInterface import XBMC_GetVolume, XBMC_SetVolume, XBMC_GetMute, XBMC_GetCurrentLanguage
from pvr.Util import SetLock, SetLock2

import sys
import os
import copy

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
	if pvr.Platform.GetPlatform( ).GetXBMCVersion( ) < pvr.Platform.GetPlatform( ).GetFrodoVersion( ) :
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

	ACTION_COLOR_RED			= 410
	ACTION_COLOR_GREEN			= 411
	ACTION_COLOR_YELLOW			= 412
	ACTION_COLOR_BLUE			= 413

	ACTION_RELOAD_SKIN			= 34	#q
	ACTION_BUILT_IN_FUNCTION	= 122	#m
	ACTION_SHOW_GUI				= 18	#tab --> xbmc


	ACTION_MBOX_RESERVED21		= 431
	ACTION_MBOX_RESERVED22		= 432
	ACTION_MBOX_RESERVED23		= 433

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


class RelayAction( object ) :
	def __init__( self, aActionId ) :
		self.mActionId = aActionId
		
	def getId( self ) :
		return self.mActionId


class SingleWindow( object ) :
	def __init__( self, *args, **kwargs ) :
			self.mRootWindow = args[0]

	def getProperty( self, aKey ) :
		return self.mRootWindow.getProperty( aKey )

	def setProperty( self, aKey, aValue ) :
		self.mRootWindow.setProperty( aKey, aValue )

	def getControl( self, aControlId ) :
		control = self.mRootWindow.getControl( aControlId )
		#LOG_TRACE( 'aControlId=%d control=%s' %( aControlId, control ) )
		return control
		
	def setFocusId( self, aControlId ) :
		self.mRootWindow.setFocusId( aControlId )	

	def getFocusId( self ) :
		return self.mRootWindow.getFocusId( )	

	def addControl( self, aControl ) :
		return self.mRootWindow.addControl( aControl )

	def removeControl( self, aControl ) :
		return self.mRootWindow.removeControl( aControl )	


class XMLWindow( xbmcgui.WindowXML ) :
	def __init__( self, *args, **kwargs ) :
		xbmcgui.WindowXML.__init__( self, *args, **kwargs )

BaseObjectWindow = SingleWindow


class BaseWindow( BaseObjectWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseObjectWindow.__init__( self, *args, **kwargs )
		self.BaseInit( )

	def SetRootWindow( self, aRootWindow ) :
		self.mRootWindow = aRootWindow		
		

	def BaseInit( self ):
		self.mWin = None
		self.mWinId = 0
		self.mClosed = False

		self.mFocusId = -1
		self.mLastFocused = -1
		self.mInitialized = False
		
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.mEventBus = pvr.ElisMgr.GetInstance( ).GetEventBus( )
		self.mDataCache = pvr.DataCacheMgr.GetInstance( )
		self.mChannelLogo = pvr.ChannelLogoMgr.GetInstance( )
		self.mParentID = -1
		self.mPlatform = pvr.Platform.GetPlatform( )
		self.mIsActivate = False
		self.mRelayAction = None
		self.setProperty( 'IsCustomWindow', 'True' )
		self.mLargeListPos = 120


	@classmethod
	def GetName( cls ):
		return cls.__name__


	def SetHeaderTitle( self, aLabel, isDefaultControlId = 1 ) :
		if isDefaultControlId == 0 :
			self.getControl( E_ARCHIVE_HEADER_TITLE ).setLabel( aLabel )
		else :
			self.getControl( E_DEFAULT_HEADER_TITLE ).setLabel( aLabel )


	def SetRelayAction( self, aAction ) :
		return
		LOG_TRACE( 'RelayAction TEST = %d' %aAction.getId() )
		self.mRelayAction = aAction
		LOG_TRACE( 'RelayAction TEST = %d' %self.mRelayAction.getId() )

	def ClearRelayAction( self ) :
		LOG_TRACE( 'RelayAction TEST' )	
		self.mRelayAction = None


	def DoRelayAction( self ) :
		LOG_TRACE( 'RelayAction TEST' )
		if self.mRelayAction :
			LOG_TRACE( 'RelayAction TEST = %d' %self.mRelayAction.getId() )
			self.onAction( self.mRelayAction )
			LOG_TRACE( 'RelayAction TEST' )
			self.mRelayAction = None
	
		LOG_TRACE( 'RelayAction TEST' )

		
	def SetParentID( self, aWindowID ) :
		self.mParentID = aWindowID


	def GetParentID( self ) :
		return self.mParentID


	def GetFocusId( self ) :
		self.mFocusId = self.getFocusId( )
		return self.mFocusId


	def SetFrontdisplayMessage( self, aMessage ) :
		self.mDataCache.Frontdisplay_SetMessage( aMessage )


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

		if E_SUPPORT_USE_KEY_Q and aActionId == Action.ACTION_RELOAD_SKIN :
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
		if aType == -1 :
			aType = self.mDataCache.Zappingmode_GetCurrent( ).mServiceType

		if aType == ElisEnum.E_SERVICE_TYPE_RADIO :
			radio = 'True'

		self.setProperty( 'TVRadio', radio )
		#LOG_TRACE('--------------radio--property[%s] type[%s]'% ( radio, aType ) )


	def SetVideoRestore( self ) :
		self.mCommander.Player_SetVIdeoSize( 0, 0, 1280, 720 )

	"""
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
	"""

	"""
	def VisibleTuneStatus( self , aFlag ) :
		self.getControl( E_SETTING_LABEL_PIP_NO_SIGNAL ).setVisible( aFlag )
		self.getControl( E_SETTING_LABEL_PIP_SCRAMBLED ).setVisible( aFlag )
	"""


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
				#if XBMC_GetMute( ) != mute :
				#	mute = True
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

		if volume <= 0 :
			volume = 0
			self.mCommander.Player_SetMute( True )
		else :
			if self.mCommander.Player_GetMute( ) :
				self.mCommander.Player_SetMute( False )
			self.mCommander.Player_SetVolume( volume )


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
			if aControlId == self.getFocusId( ) :
				ret = True
				break
			time.sleep( sleepTime )
			loopTime += sleepTime

		#LOG_TRACE('-----------control[%s] setFocus time[%s]'% ( aControlId, ( time.time() - startTime ) ) )
		return ret


	def SetMediaCenter( self, aNowPlay=False ) :
		#import pvr.gui.WindowMgr as WinMgr
		if aNowPlay == True :
			self.mDataCache.SetMediaCenter( True )
			self.mCommander.AppMediaPlayer_Control( 1 )
		else :
			import pvr.gui.DialogMgr as DiaMgr
			DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).PIP_Check( E_PIP_STOP )
			self.mDataCache.SetDelaySettingWindow( True )

		#by doliyu for manual service start.
		xbmc.executebuiltin("Custom.StartStopService(Start)", False)


	def CheckMediaCenter( self ) :
		if self.mDataCache.GetMediaCenter( ) == True :
			self.mCommander.AppMediaPlayer_Control( 0 )
			#current channel re-zapping
			iChannel = self.mDataCache.Channel_GetCurrent( )
			channelList = self.mDataCache.Channel_GetList( )
			if iChannel and channelList and len( channelList ) > 0 :
				iEPG = self.mDataCache.Epgevent_GetPresent( )
				if self.mDataCache.GetStatusByParentLock( ) and ( not self.mDataCache.GetPincodeDialog( ) ) and \
				   channelList and len( channelList ) > 0 and iChannel and iChannel.mLocked or self.mDataCache.GetParentLock( iEPG ) :
					#pvr.GlobalEvent.GetInstance( ).CheckParentLock( E_PARENTLOCK_INIT )
					self.mDataCache.Player_AVBlank( True )
					self.mDataCache.Channel_InvalidateCurrent( )
					self.mDataCache.Channel_SetCurrentSync( iChannel.mNumber, iChannel.mServiceType )
					self.mDataCache.Player_AVBlank( True )
					LOG_TRACE( '----------------------------------------------ch lock' )

				else :
					self.mDataCache.Channel_InvalidateCurrent( )
					self.mDataCache.Channel_SetCurrentSync( iChannel.mNumber, iChannel.mServiceType )
					self.mDataCache.SetParentLockPass( True )

			self.mDataCache.SetMediaCenter( False )
			self.UpdateMediaCenterVolume( )
			self.mDataCache.SyncMute( )

		self.SetRadioScreen( )


	def UpdateMediaCenterVolume( self ) :
		if self.mDataCache.Get_Player_AVBlank( ) :
			LOG_TRACE( '----------blocking avblank' )
			return

		volume = 0
		if self.mPlatform.IsPrismCube( ) :
			if self.mPlatform.GetXBMCVersion( ) >= self.mPlatform.GetFrodoVersion( ) :
				volume = XBMC_GetVolume( )

		else :
			volume = self.mCommander.Player_GetVolume( )

		LOG_TRACE( 'GET VOLUME=%d' %volume )
		self.mCommander.Player_SetVolume( volume )


	def OpenBusyDialog( self ) :
		xbmc.executebuiltin( 'ActivateWindow(busydialog)' )


	def CloseBusyDialog( self ) :
		xbmc.executebuiltin( 'Dialog.Close(busydialog)' )


	def NotificationDialog( self, aMsg1, aMsg2, aTimeMs = 2000, aImage = '' ) :
		command = 'Notification(%s,%s,%s,%s)'% ( aMsg1, aMsg2, aTimeMs, aImage )
		xbmc.executebuiltin( command )


	def EventReceivedDialog( self, aDialog ) :
		ret = aDialog.GetCloseStatus( )
		if ret == Action.ACTION_PLAYER_PLAY :
			xbmc.executebuiltin('xbmc.Action(play)')

		elif ret == Action.ACTION_STOP :
			xbmc.executebuiltin('xbmc.Action(stop)')


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


	def ShowPIP( self ) :
		if E_V1_2_APPLY_PIP :
			import pvr.gui.DialogMgr as DiaMgr
			pipDlg = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP )

			if pipDlg.PIP_Available( ) :
				pipDlg.doModal( )


	def HasDefaultRecordPath( self, aRequestAsk = True ) :
		from pvr.GuiHelper import CheckHdd
		import pvr.gui.DialogMgr as DiaMgr
		from elisinterface.ElisProperty import ElisPropertyEnum

		isAvail = E_DEFAULT_RECORD_PATH_NOT_AVAILABLE
		hddStatus = CheckHdd( )
		defPath = ElisPropertyEnum( 'Record Default Path Change', self.mCommander ).GetProp( )
		LOG_TRACE( 'Record Default Path Change enum[%s] hdd[%s]'% ( defPath, hddStatus ) )

		if defPath == 0 : #'Internal'
			if hddStatus :
				isAvail = E_DEFAULT_RECORD_PATH_RESERVED
			else :
				isAvail = E_DEFAULT_RECORD_PATH_NOT_AVAILABLE

		elif defPath == 1 : #'Network'
			netVolumeList = self.mDataCache.Record_GetNetworkVolume( True )
			if netVolumeList and len( netVolumeList ) > 0 :
				isDefaultSet = False
				for netVolume in netVolumeList :
					if netVolume.mIsDefaultSet :
						if netVolume.mOnline and ( not netVolume.mReadOnly ) :
							isAvail = E_DEFAULT_RECORD_PATH_RESERVED
						else :
							isAvail = E_DEFAULT_RECORD_PATH_NOT_SELECT

						isDefaultSet = True
						break

				if not isDefaultSet :
					isAvail = E_DEFAULT_RECORD_PATH_NOT_SELECT

			else :
				isAvail = E_DEFAULT_RECORD_PATH_NOT_AVAILABLE

			if isAvail != E_DEFAULT_RECORD_PATH_RESERVED and hddStatus :
				isAvail = E_DEFAULT_RECORD_PATH_RESERVED

		else :
			isAvail = E_DEFAULT_RECORD_PATH_NOT_SELECT

		isConfiguration = False
		if aRequestAsk :
			if isAvail != E_DEFAULT_RECORD_PATH_RESERVED :
				lblTitle = MR_LANG( 'No recording path' )
				lblLine  = MR_LANG( 'Do you want to set the recording path now?' )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( lblTitle, lblLine )
				dialog.doModal( )
				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					isConfiguration = True

		LOG_TRACE( 'recordPathAvail[%s] gotoConfig[%s]'% ( isAvail, isConfiguration ) )
		return isAvail, isConfiguration


	def SetSingleWindowPosition( self, aWindowId ) :
		import pvr.gui.WindowMgr as WinMgr
		#import pvr.gui.DialogMgr as DiaMgr
		#DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).PIP_Check( )

		overlayImage = self.getControl( E_SETTING_PIP_SCREEN_IMAGE )
		radioImage = self.getControl( E_SETTING_PIP_RADIO_IMAGE )
		nosignalLabel = self.getControl( E_SETTING_LABEL_PIP_NO_SIGNAL )
		scrambleLabel = self.getControl( E_SETTING_LABEL_PIP_SCRAMBLED )
		noServiceLabel = self.getControl( E_SETTING_LABEL_NO_SERVICE )
		settingControlGroup = self.getControl( E_SETTING_CONTROL_GROUPID )

		if aWindowId == WinMgr.WIN_ID_FIRST_INSTALLATION * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingBackground', 'True' )
			self.setProperty( 'DafultBackgroundImage', 'True' )
			self.setProperty( 'SettingPIG', 'True' )
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
			for i in range( len( visibleControlIds ) ) :
				self.getControl( visibleControlIds[i] ).setVisible( True )
				self.getControl( visibleControlIds[i] ).setEnabled( True )

			hideControlIds = [ E_SpinEx08, E_Input06, E_Input07, E_Input08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )

			overlayImage.setPosition( 857, 170 )
			overlayImage.setWidth( 352 )
			overlayImage.setHeight( 198 )
			
			radioImage.setPosition( 857, 170 )
			radioImage.setWidth( 352 )
			radioImage.setHeight( 198 )
			
			nosignalLabel.setPosition( 930, 250 )
			scrambleLabel.setPosition( 930, 250 )
			noServiceLabel.setPosition( 930, 250 )

			settingControlGroup.setPosition( 80, 120 )

		elif aWindowId == WinMgr.WIN_ID_CONFIGURE * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingBackground', 'True' )
			self.setProperty( 'DafultBackgroundImage', 'True' )
			self.setProperty( 'SettingPIG', 'False' )
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			for i in range( len( visibleControlIds ) ) :
				self.getControl( visibleControlIds[i] ).setVisible( True )

			hideControlIds = [ E_SpinEx08, E_Input08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )

			settingControlGroup.setPosition( 380, 110 )

		elif aWindowId == WinMgr.WIN_ID_ADVANCED * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingBackground', 'True' )
			self.setProperty( 'DafultBackgroundImage', 'True' )
			self.setProperty( 'SettingPIG', 'False' )
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05 ]
			for i in range( len( visibleControlIds ) ) :
				self.getControl( visibleControlIds[i] ).setVisible( True )

			hideControlIds = [ E_SpinEx06, E_SpinEx07, E_SpinEx08, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07, E_Input08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )

			settingControlGroup.setPosition( 380, 110 )

		elif aWindowId == WinMgr.WIN_ID_ANTENNA_SETUP * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingBackground', 'True' )
			self.setProperty( 'DafultBackgroundImage', 'True' )
			self.setProperty( 'SettingPIG', 'True' )
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_Input01, E_Input02 ]
			for i in range( len( visibleControlIds ) ) :
				self.getControl( visibleControlIds[i] ).setVisible( True )
				self.getControl( visibleControlIds[i] ).setEnabled( True )

			hideControlIds = [ E_SpinEx05, E_SpinEx06, E_SpinEx07, E_SpinEx08, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07, E_Input08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )

			overlayImage.setPosition( 857, 170 )
			overlayImage.setWidth( 352 )
			overlayImage.setHeight( 198 )

			radioImage.setPosition( 857, 170 )
			radioImage.setWidth( 352 )
			radioImage.setHeight( 198 )

			nosignalLabel.setPosition( 930, 250 )
			scrambleLabel.setPosition( 930, 250 )
			noServiceLabel.setPosition( 930, 250 )

			largeListPos = self.mLargeListPos
			largePos = self.getProperty( 'SettingsLargeListPos' )

			if largePos :
				largeListPos = int( largePos )
			LOG_TRACE( 'largePos=%d' %largeListPos )

			settingControlGroup.setPosition( 80, largeListPos )

		elif aWindowId == WinMgr.WIN_ID_DVBT_TUNER_SETUP * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingBackground', 'True' )
			self.setProperty( 'DafultBackgroundImage', 'True' )
			self.setProperty( 'SettingPip', 'True' )
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_Input01 ]
			for i in range( len( visibleControlIds ) ) :
				self.getControl( visibleControlIds[i] ).setVisible( True )
				self.getControl( visibleControlIds[i] ).setEnabled( True )

			hideControlIds = [ E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_SpinEx08, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07, E_Input08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )

			overlayImage.setPosition( 857, 170 )
			overlayImage.setWidth( 352 )
			overlayImage.setHeight( 198 )

			radioImage.setPosition( 857, 170 )
			radioImage.setWidth( 352 )
			radioImage.setHeight( 198 )

			nosignalLabel.setPosition( 930, 250 )
			scrambleLabel.setPosition( 930, 250 )
			noServiceLabel.setPosition( 930, 250 )

			settingControlGroup.setPosition( 80, 120 )

		elif aWindowId == WinMgr.WIN_ID_CONFIG_DISEQC_10 * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID or \
			aWindowId == WinMgr.WIN_ID_CONFIG_DISEQC_11 * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID or \
			aWindowId == WinMgr.WIN_ID_CONFIG_MOTORIZED_12 * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID or \
			aWindowId == WinMgr.WIN_ID_CONFIG_SIMPLE * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingPIG', 'True' )
			self.setProperty( 'SettingBackground', 'True' )
			
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_SpinEx08, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06 ]
			for i in range( len( visibleControlIds ) ) :
				self.getControl( visibleControlIds[i] ).setVisible( True )
				self.getControl( visibleControlIds[i] ).setEnabled( True )

			hideControlIds = [ E_Input07, E_Input08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )

		elif aWindowId == WinMgr.WIN_ID_TUNER_CONFIGURATION * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingPIG', 'True' )
			self.setProperty( 'SettingBackground', 'True' )

			hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_SpinEx08, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07, E_Input08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )

		elif aWindowId == WinMgr.WIN_ID_CONFIG_MOTORIZED_USALS * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingPIG', 'True' )
			self.setProperty( 'SettingBackground', 'True' )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_Input01, E_Input02, E_Input03, E_Input04 ]
			for i in range( len( visibleControlIds ) ) :
				self.getControl( visibleControlIds[i] ).setVisible( True )
				self.getControl( visibleControlIds[i] ).setEnabled( True )

			hideControlIds = [ E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_SpinEx08, E_Input05, E_Input06, E_Input07, E_Input08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )

		elif aWindowId == WinMgr.WIN_ID_CONFIG_ONECABLE * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingPIG', 'True' )
			self.setProperty( 'SettingBackground', 'True' )

			visibleControlIds = [ E_SpinEx01, E_Input01, E_Input02, E_Input03 ]
			for i in range( len( visibleControlIds ) ) :
				self.getControl( visibleControlIds[i] ).setVisible( True )
				self.getControl( visibleControlIds[i] ).setEnabled( True )

			hideControlIds = [ E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_SpinEx08, E_Input04, E_Input05, E_Input06, E_Input07, E_Input08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )

		elif aWindowId == WinMgr.WIN_ID_CONFIG_ONECABLE_2 * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingPIG', 'True' )
			self.setProperty( 'SettingBackground', 'True' )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input01, E_Input02, E_Input03, E_Input04 ]
			for i in range( len( visibleControlIds ) ) :
				self.getControl( visibleControlIds[i] ).setVisible( True )
				self.getControl( visibleControlIds[i] ).setEnabled( True )

			hideControlIds = [ E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_SpinEx08, E_Input05, E_Input06, E_Input07, E_Input08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )

		elif aWindowId == WinMgr.WIN_ID_CHANNEL_SEARCH * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingBackground', 'True' )
			self.setProperty( 'DafultBackgroundImage', 'True' )
			self.setProperty( 'SettingPIG', 'True' )
			visibleControlIds = [ E_Input01, E_Input02, E_Input03 ]
			for i in range( len( visibleControlIds ) ) :
				self.getControl( visibleControlIds[i] ).setVisible( True )
				self.getControl( visibleControlIds[i] ).setEnabled( True )

			hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_SpinEx08, E_Input04, E_Input05, E_Input06, E_Input07, E_Input08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )

			overlayImage.setPosition( 857, 170 )
			overlayImage.setWidth( 352 )
			overlayImage.setHeight( 198 )

			radioImage.setPosition( 857, 170 )
			radioImage.setWidth( 352 )
			radioImage.setHeight( 198 )

			nosignalLabel.setPosition( 930, 250 )
			scrambleLabel.setPosition( 930, 250 )
			noServiceLabel.setPosition( 930, 250 )

			settingControlGroup.setPosition( 80, 120 )

		elif aWindowId == WinMgr.WIN_ID_CHANNEL_SCAN_DVBT * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingBackground', 'True' )
			self.setProperty( 'DafultBackgroundImage', 'True' )
			self.setProperty( 'SettingPip', 'True' )
			visibleControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05 ]
			for i in range( len( visibleControlIds ) ) :
				self.getControl( visibleControlIds[i] ).setVisible( True )
				self.getControl( visibleControlIds[i] ).setEnabled( True )

			hideControlIds = [ E_SpinEx06, E_SpinEx07, E_SpinEx08, E_Input05, E_Input06, E_Input07, E_Input08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )

			overlayImage.setPosition( 857, 170 )
			overlayImage.setWidth( 352 )
			overlayImage.setHeight( 198 )

			radioImage.setPosition( 857, 170 )
			radioImage.setWidth( 352 )
			radioImage.setHeight( 198 )

			nosignalLabel.setPosition( 930, 250 )
			scrambleLabel.setPosition( 930, 250 )
			noServiceLabel.setPosition( 930, 250 )

			settingControlGroup.setPosition( 80, 120 )

		elif aWindowId == WinMgr.WIN_ID_AUTOMATIC_SCAN * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingBackground', 'True' )
			self.setProperty( 'SettingPIG', 'True' )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_Input01, E_Input02 ]
			for i in range( len( visibleControlIds ) ) :
				self.getControl( visibleControlIds[i] ).setVisible( True )
				self.getControl( visibleControlIds[i] ).setEnabled( True )

			hideControlIds = [ E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_SpinEx08, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07, E_Input08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )

		elif aWindowId == WinMgr.WIN_ID_MANUAL_SCAN * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingBackground', 'True' )
			self.setProperty( 'SettingPIG', 'True' )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_Input01, E_Input02, E_Input03, E_Input04 ]
			for i in range( len( visibleControlIds ) ) :
				self.getControl( visibleControlIds[i] ).setVisible( True )
				self.getControl( visibleControlIds[i] ).setEnabled( True )

			hideControlIds = [ E_SpinEx07, E_SpinEx08, E_Input05, E_Input06, E_Input07, E_Input08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )

		elif aWindowId == WinMgr.WIN_ID_FAST_SCAN * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingBackground', 'True' )
			self.setProperty( 'SettingPIG', 'True' )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_Input01, E_Input02, E_Input03 ]
			for i in range( len( visibleControlIds ) ) :
				self.getControl( visibleControlIds[i] ).setVisible( True )
				self.getControl( visibleControlIds[i] ).setEnabled( True )

			hideControlIds = [ E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_SpinEx08, E_Input04, E_Input05, E_Input06, E_Input07, E_Input08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )

		elif aWindowId == WinMgr.WIN_ID_EDIT_SATELLITE * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingBackground', 'True' )
			self.setProperty( 'DafultBackgroundImage', 'True' )
			self.setProperty( 'SettingPIG', 'True' )
			visibleControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
			for i in range( len( visibleControlIds ) ) :
				self.getControl( visibleControlIds[i] ).setVisible( True )
				self.getControl( visibleControlIds[i] ).setEnabled( True )

			hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_SpinEx08, E_Input06, E_Input07, E_Input08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )

			overlayImage.setPosition( 857, 170 )
			overlayImage.setWidth( 352 )
			overlayImage.setHeight( 198 )

			radioImage.setPosition( 857, 170 )
			radioImage.setWidth( 352 )
			radioImage.setHeight( 198 )

			nosignalLabel.setPosition( 930, 250 )
			scrambleLabel.setPosition( 930, 250 )
			noServiceLabel.setPosition( 930, 250 )

			settingControlGroup.setPosition( 80, 120 )

		elif aWindowId == WinMgr.WIN_ID_EDIT_TRANSPONDER * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingBackground', 'True' )
			self.setProperty( 'DafultBackgroundImage', 'True' )
			self.setProperty( 'SettingPIG', 'True' )
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07, E_Input08 ]
			for i in range( len( visibleControlIds ) ) :
				self.getControl( visibleControlIds[i] ).setVisible( True )
				self.getControl( visibleControlIds[i] ).setEnabled( True )

			hideControlIds = [ E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_SpinEx08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )

			overlayImage.setPosition( 857, 170 )
			overlayImage.setWidth( 352 )
			overlayImage.setHeight( 198 )

			radioImage.setPosition( 857, 170 )
			radioImage.setWidth( 352 )
			radioImage.setHeight( 198 )

			nosignalLabel.setPosition( 930, 250 )
			scrambleLabel.setPosition( 930, 250 )
			noServiceLabel.setPosition( 930, 250 )

			settingControlGroup.setPosition( 80, 120 )

		elif aWindowId == WinMgr.WIN_ID_CONDITIONAL_ACCESS * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingBackground', 'True' )
			self.setProperty( 'DafultBackgroundImage', 'True' )
			self.setProperty( 'SettingPIG', 'True' )
			visibleControlIds = [ E_Input01, E_Input02, E_SpinEx01 ]
			for i in range( len( visibleControlIds ) ) :
				self.getControl( visibleControlIds[i] ).setVisible( True )
				self.getControl( visibleControlIds[i] ).setEnabled( True )

			hideControlIds = [ E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_SpinEx08, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07, E_Input08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )

			overlayImage.setPosition( 857, 170 )
			overlayImage.setWidth( 352 )
			overlayImage.setHeight( 198 )

			radioImage.setPosition( 857, 170 )
			radioImage.setWidth( 352 )
			radioImage.setHeight( 198 )

			nosignalLabel.setPosition( 930, 250 )
			scrambleLabel.setPosition( 930, 250 )
			noServiceLabel.setPosition( 930, 250 )

			settingControlGroup.setPosition( 80, 120 )

		elif aWindowId == WinMgr.WIN_ID_SYSTEM_UPDATE * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingBackground', 'True' )
			self.setProperty( 'DafultBackgroundImage', 'True' )
			self.setProperty( 'SettingPIG', 'True' )
			visibleControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			for i in range( len( visibleControlIds ) ) :
				self.getControl( visibleControlIds[i] ).setVisible( True )
				self.getControl( visibleControlIds[i] ).setEnabled( True )

			hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_SpinEx08, E_Input08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )

			overlayImage.setPosition( 857, 170 )
			overlayImage.setWidth( 352 )
			overlayImage.setHeight( 198 )

			radioImage.setPosition( 857, 170 )
			radioImage.setWidth( 352 )
			radioImage.setHeight( 198 )

			nosignalLabel.setPosition( 930, 250 )
			scrambleLabel.setPosition( 930, 250 )
			noServiceLabel.setPosition( 930, 250 )

			settingControlGroup.setPosition( 80, 120 )

		elif aWindowId == WinMgr.WIN_ID_INSTALLATION * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingBackground', 'True' )
			self.setProperty( 'DafultBackgroundImage', 'True' )
			self.setProperty( 'SettingPIG', 'True' )
			hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_SpinEx08, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07, E_Input08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )
			
			overlayImage.setPosition( 362, 112 )
			overlayImage.setWidth( 798 )
			overlayImage.setHeight( 446 )

			radioImage.setPosition( 362, 112 )
			radioImage.setWidth( 798 )
			radioImage.setHeight( 446 )

			nosignalLabel.setPosition( 645, 313 )
			scrambleLabel.setPosition( 645, 313 )
			noServiceLabel.setPosition( 645, 313 )

		elif aWindowId == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingPIG', 'True' )
			self.setProperty( 'DafultBackgroundImage', 'True' )

			overlayImage.setPosition( 850, 113 )
			overlayImage.setWidth( 352 )
			overlayImage.setHeight( 198 )

			radioImage.setPosition( 850, 113 )
			radioImage.setWidth( 352 )
			radioImage.setHeight( 198 )

			nosignalLabel.setPosition( 925, 197 )
			scrambleLabel.setPosition( 925, 197 )
			noServiceLabel.setPosition( 925, 197 )

		elif aWindowId == WinMgr.WIN_ID_ARCHIVE_WINDOW * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			if self.getProperty( 'ViewMode' ) == 'common' :
				self.setProperty( 'SettingPIG', 'True' )

				overlayImage.setPosition( 850, 118 )
				overlayImage.setWidth( 352 )
				overlayImage.setHeight( 198 )

				radioImage.setPosition( 850, 118 )
				radioImage.setWidth( 352 )
				radioImage.setHeight( 198 )

				nosignalLabel.setPosition( 925, 205 )
				scrambleLabel.setPosition( 925, 205 )
				noServiceLabel.setPosition( 925, 205 )
			else :
				self.setProperty( 'SettingPIG', 'False' )

		elif ( aWindowId == WinMgr.WIN_ID_EPG_WINDOW * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID ) or \
			( aWindowId == WinMgr.WIN_ID_EPG_SEARCH * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID ) :
			if self.getProperty( 'EPGMode' ) == 'grid' :
				self.setProperty( 'SettingPIG', 'False' )
				self.setProperty( 'DafultBackgroundImage', 'False' )
			else :
				self.setProperty( 'SettingPIG', 'True' )
				self.setProperty( 'DafultBackgroundImage', 'True' )
												
				overlayImage.setPosition( 849, 118 )
				overlayImage.setWidth( 350 )
				overlayImage.setHeight( 198 )

				radioImage.setPosition( 849, 118 )
				radioImage.setWidth( 350 )
				radioImage.setHeight( 198 )

				nosignalLabel.setPosition( 922, 203 )
				scrambleLabel.setPosition( 922, 203 )
				noServiceLabel.setPosition( 922, 203 )

		elif aWindowId == WinMgr.WIN_ID_TIMER_WINDOW * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingPIG', 'True' )
			self.setProperty( 'DafultBackgroundImage', 'True' )

			overlayImage.setPosition( 849, 118 )
			overlayImage.setWidth( 350 )
			overlayImage.setHeight( 198 )

			radioImage.setPosition( 849, 118 )
			radioImage.setWidth( 350 )
			radioImage.setHeight( 198 )

			nosignalLabel.setPosition( 922, 203 )
			scrambleLabel.setPosition( 922, 203 )
			noServiceLabel.setPosition( 922, 203 )

		elif aWindowId == WinMgr.WIN_ID_SYSTEM_INFO * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'DafultBackgroundImage', 'True' )

		elif aWindowId == WinMgr.WIN_ID_LIVE_PLATE * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingBackground', 'False' )
			self.setProperty( 'DafultBackgroundImage', 'False' )
			self.setProperty( 'SettingPIG', 'False' )
			#for i in range( E_CTRL_BTN_INFO_MAX ) :
			#	self.getControl( E_CONTROL_ID_BUTTON_DESCRIPTION_INFO + i ).setVisible( True )

		elif aWindowId == WinMgr.WIN_ID_INFO_PLATE * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID :
			self.setProperty( 'SettingBackground', 'False' )
			self.setProperty( 'DafultBackgroundImage', 'False' )
			self.setProperty( 'SettingPIG', 'False' )
			for i in range( E_CTRL_BTN_INFO_MAX ) :
				self.getControl( E_CONTROL_ID_BUTTON_DESCRIPTION_INFO + i ).setVisible( True )

		else :
			self.setProperty( 'SettingBackground', 'False' )
			self.setProperty( 'DafultBackgroundImage', 'False' )
			self.setProperty( 'SettingPIG', 'False' )
			hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_SpinEx08, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07, E_Input08 ]
			for i in range( len( hideControlIds ) ) :
				self.getControl( hideControlIds[i] ).setVisible( False )


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
			
