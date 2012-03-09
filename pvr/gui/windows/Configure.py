import xbmc
import xbmcgui
import sys
import time

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DiaMgr
import pvr.DataCacheMgr as CacheMgr
from pvr.gui.BaseWindow import SettingWindow, Action
import pvr.ElisMgr
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
from ElisEventBus import ElisEventBus
from pvr.gui.GuiConfig import *
from pvr.Util import RunThread, GuiLock, GuiLock2, MLOG, LOG_WARN, LOG_TRACE, LOG_ERR, TimeToString, TimeFormatEnum
from ElisClass import *

E_DHCP_OFF		= 0
E_DHCP_ON		= 1
TIME_AUTOMATIC	= 0
TIME_MANUAL		= 1

class Configure( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
 
		leftGroupItems			= [ 'Language', 'Parental', 'Recording Option', 'Audio Setting', 'HDMI Setting', 'IP Setting', 'Time Setting', 'Format HDD', 'Factory Reset', 'Etc' ]
		descriptionList			= [ 'DESC Language', 'DESC Parental', 'DESC Recording Option', 'DESC Audio Setting', 'DESC HDMI Setting', 'DESC IP Setting', 'DESC Time Setting', 'DESC Format HDD', 'DESC Factory Reset', 'DESC Etc' ]
	
		self.mCtrlLeftGroup 	= None
		self.mGroupItems 		= []
		self.mLastFocused 		= E_SUBMENU_LIST_ID
		self.mPrevListItemID 	= 0

		self.mSavedIpAddr		= 0
		self.mSavedSubNet		= 0
		self.mSavedGateway		= 0
		self.mSavedDns			= 0

		self.mTempIpAddr		= 0
		self.mTempSubNet		= 0
		self.mTempGateway		= 0
		self.mTempDns			= 0

		self.mReLoadIp			= False
		self.mVisibleParental	= False

		self.mDate				= '1/1/1999'
		self.mTime				= '12:59'
		self.mSetupChannel		= None
		self.mHasChannel		= False
		self.mFinishEndSetTime	= False
		self.ProgressOpen		= False

		for i in range( len( leftGroupItems ) ) :
			self.mGroupItems.append( xbmcgui.ListItem( leftGroupItems[i], descriptionList[i] ) )


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mEventBus.Register( self )

		self.mCtrlLeftGroup = self.getControl( E_SUBMENU_LIST_ID )
		self.mCtrlLeftGroup.addItems( self.mGroupItems )

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( 'Configure' )

		position = self.mCtrlLeftGroup.getSelectedPosition( )
		self.mCtrlLeftGroup.selectItem( position )
		self.SetListControl( )
		self.LoadIp( )
		self.mInitialized = True
		self.mVisibleParental = False
		self.mReLoadIp = False

	def onAction( self, aAction ) :

		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )

		self.GlobalAction( actionId )
		
		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.mInitialized = False
			self.close( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mInitialized = False
			self.close( )

		elif actionId == Action.ACTION_MOVE_UP :
			if focusId == E_SUBMENU_LIST_ID and selectedId != self.mPrevListItemID :
				self.mPrevListItemID = selectedId
				self.mReLoadIp = True
				self.mVisibleParental = False
				self.SetListControl( )
			elif focusId != E_SUBMENU_LIST_ID :
				self.ControlUp( )
	
		elif actionId == Action.ACTION_MOVE_DOWN :
			if focusId == E_SUBMENU_LIST_ID and selectedId != self.mPrevListItemID :
				self.mPrevListItemID = selectedId
				self.mReLoadIp = True
				self.mVisibleParental = False
				self.SetListControl( )
			elif focusId != E_SUBMENU_LIST_ID :
				self.ControlDown( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			if focusId != E_SUBMENU_LIST_ID and ( ( focusId % 10 ) == 1 ) :
				self.setFocusId( E_SUBMENU_LIST_ID )
			else :
				self.ControlLeft( )
				
		elif actionId == Action.ACTION_MOVE_RIGHT :
			if focusId == E_SUBMENU_LIST_ID :
				self.setFocusId( E_SETUPMENU_GROUP_ID )
					
			elif focusId != E_SUBMENU_LIST_ID and ( focusId % 10 ) == 2 :
				self.setFocusId( E_SUBMENU_LIST_ID )
			elif focusId != E_SUBMENU_LIST_ID and ( focusId % 10 ) == 1 :
				self.ControlRight( )
			

	def onClick( self, aControlId ) :
		groupId = self.GetGroupId( aControlId )
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		
		if selectedId == E_LANGUAGE :
			self.DisableControl( selectedId )
			self.ControlSelect( )
			return

		elif selectedId == E_IP_SETTING :
			self.IpSetting( groupId )
			return

		elif selectedId == E_TIME_SETTING :
			self.TimeSetting( groupId )
			return

		elif selectedId == E_PARENTAL and self.mVisibleParental == False and groupId == E_Input01 :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( 'PIN Code 4 digit', '', 4, True )
 			dialog.doModal( )
 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
 				tempval = dialog.GetString( )
 				if tempval == '' :
 					return
				if int( tempval ) == ElisPropertyInt( 'PinCode', self.mCommander ).GetProp( ) :
					self.mVisibleParental = True
					self.DisableControl( E_PARENTAL )
				else :
					dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( 'ERROR', 'ERROR PIN Code' )
		 			dialog.doModal( )
			return

		elif selectedId == E_PARENTAL and groupId == E_Input02 :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( 'New PIN Code', '', 4, True )
 			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				newpin = dialog.GetString( )
				if newpin == '' or len( newpin ) != 4 :
					dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( 'ERROR', 'Input 4 digit' )
		 			dialog.doModal( )
					return
			else :
				return

			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( 'Confirm PIN Code', '', 4, True )
 			dialog.doModal( )

 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
 				confirm = dialog.GetString( )
 				if confirm == '' :
 					dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( 'ERROR', 'New PIN codes do not match' )
		 			dialog.doModal( )
 					return
				if int( newpin ) != int( confirm ) :
					dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( 'ERROR', 'New PIN codes do not match' )
		 			dialog.doModal( )
					return
			else :
				return
				
			ElisPropertyInt( 'PinCode', self.mCommander ).SetProp( int( newpin ) )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( 'Success', 'Pin codes change success' )
 			dialog.doModal( )

 		elif selectedId == E_FACTORY_RESET and groupId == E_Input01 :
 			resetChannel = ElisPropertyEnum( 'Reset Channel List', self.mCommander ).GetProp( )
 			resetFavoriteAddons = ElisPropertyEnum( 'Reset Favorite Add-ons', self.mCommander ).GetProp( )
 			resetSystem = ElisPropertyEnum( 'Reset Configure Setting', self.mCommander ).GetProp( )
 			if ( resetChannel | resetFavoriteAddons | resetSystem ) == 0 :
 				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'ERROR', 'No selected reset' )
		 		dialog.doModal( )
		 		return
		 	else :
		 		dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( 'Reset', 'Are you sure?' )
				dialog.doModal( )

				if dialog.IsOK() == E_DIALOG_STATE_YES :
				 	if resetChannel == 1 :
				 		self.mCommander.System_SetDefaultChannelList( )
				 		self.mDataCache.LoadAllSatellite( )

				 	elif resetFavoriteAddons == 1 :
				 		pass

				 	elif resetSystem == 1 :
				 		self.mCommander.System_FactoryReset( )
				 		gPropertyEnumHash = {}

		else :
			self.ControlSelect( )


	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return

		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		if ( self.mLastFocused != aControlId ) or ( selectedId != self.mPrevListItemID ) :
			if aControlId == E_SUBMENU_LIST_ID :
				if self.mLastFocused != aControlId :
					self.mLastFocused = aControlId
				if selectedId != self.mPrevListItemID :
					self.mPrevListItemID =selectedId
					self.mReLoadIp = True
					self.mVisibleParental = False
				self.SetListControl( )


	def onEvent( self, aEvent ) :
		if self.ProgressOpen == True :
			if aEvent.getName( ) == ElisEventTimeReceived.getName( ) :
				self.mFinishEndSetTime	= True


	def SetListControl( self ) :
		self.ResetAllControl( )
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( False )
		
		if selectedId == E_LANGUAGE :

			self.AddEnumControl( E_SpinEx01, 'Language' )
			self.AddEnumControl( E_SpinEx02, 'Audio Language' )
			self.AddEnumControl( E_SpinEx03, 'Subtitle Language' )
			self.AddEnumControl( E_SpinEx04, 'Secondary Subtitle Language' )
			self.AddEnumControl( E_SpinEx05, 'Hearing Impaired' )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			self.DisableControl( E_LANGUAGE )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return
			
			
		elif selectedId == E_PARENTAL :	
			self.AddInputControl( E_Input01, 'Enable Setting Menu', '' )
			self.AddEnumControl( E_SpinEx01, 'Lock Mainmenu', ' - Lock Mainmenu' )
			self.AddEnumControl( E_SpinEx02, 'Age Restricted', ' - Age Restricted' )
			self.AddInputControl( E_Input02, ' - Change PIn Code', '' )

			visibleControlIds = [ E_SpinEx01, E_Input01, E_SpinEx02, E_Input02 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			self.DisableControl( E_PARENTAL )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return


		elif selectedId == E_RECORDING_OPTION :

			self.AddEnumControl( E_SpinEx01, 'Automatic Timeshift' )
			self.AddEnumControl( E_SpinEx02, 'Default Rec Duration' )
			self.AddEnumControl( E_SpinEx03, 'Pre-Rec Time' )
			self.AddEnumControl( E_SpinEx04, 'Post-Rec Time' )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return

			
		elif selectedId == E_AUDIO_SETTING :
			self.AddEnumControl( E_SpinEx01, 'Audio Dolby' )
			self.AddEnumControl( E_SpinEx02, 'Audio HDMI' )
			self.AddEnumControl( E_SpinEx03, 'Audio Delay' )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03 ]
			self.SetEnableControls( visibleControlIds, True )
			self.SetVisibleControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx04, E_SpinEx05,  E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return


		elif selectedId == E_HDMI_SETTING :
			self.AddEnumControl( E_SpinEx01, 'HDMI Format' )
			self.AddEnumControl( E_SpinEx02, 'Show 4:3' )
			self.AddEnumControl( E_SpinEx03, 'HDMI Color Space' )
			self.AddEnumControl( E_SpinEx04, 'TV System' )
			
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return

		
		elif selectedId == E_IP_SETTING :
			if self.mReLoadIp == True :
				self.ReLoadIp( )
				self.mReLoadIp = False
				
			self.AddEnumControl( E_SpinEx01, 'DHCP' )
			self.AddInputControl( E_Input01, 'IP Address', '%d.%d.%d.%d' % MakeHexToIpAddr( self.mTempIpAddr ) )
			self.AddInputControl( E_Input02, 'Subnet Mask', '%d.%d.%d.%d' % MakeHexToIpAddr( self.mTempSubNet ) )
			self.AddInputControl( E_Input03, 'Gateway', '%d.%d.%d.%d' % MakeHexToIpAddr( self.mTempGateway ) )
			self.AddInputControl( E_Input04, 'DNS', '%d.%d.%d.%d' % MakeHexToIpAddr( self.mTempDns ) )

			dhcp = ElisPropertyEnum( 'DHCP', self.mCommander ).GetProp( )
			if dhcp == E_DHCP_OFF :
				self.AddInputControl( E_Input05, 'Save', '' )
			elif dhcp == E_DHCP_ON :
				self.AddInputControl( E_Input05, 'Get IP Address', '' )

			visibleControlIds = [ E_SpinEx01, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			self.DisableControl( E_IP_SETTING )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return


		elif selectedId == E_TIME_SETTING :
			setupChannelNumber = ElisPropertyInt( 'Time Setup Channel Number', self.mCommander ).GetProp( )
			self.mSetupChannel = self.mDataCache.Channel_GetSearch( setupChannelNumber )
			if self.mSetupChannel :
				self.mHasChannel = True
				channelName = self.mSetupChannel.mName
			else :
				channellist = self.mDataCache.Channel_GetList( )
				if channellist :
					self.mSetupChannel = channellist[0]
					channelName = self.mSetupChannel.mName
				else :
					self.mHasChannel = False
					channelName = 'None'

			self.AddEnumControl( E_SpinEx01, 'Time Mode' )			
			self.AddInputControl( E_Input01, 'Channel', channelName )
			self.mDate = TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_DD_MM_YYYY )
			self.AddInputControl( E_Input02, 'Date', self.mDate )
			self.mTime = TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_HH_MM )
			self.AddInputControl( E_Input03, 'Time', self.mTime )
			self.AddEnumControl( E_SpinEx02, 'Local Time Offset' )
			self.AddEnumControl( E_SpinEx03, 'Summer Time' )
			self.AddInputControl( E_Input04, 'Apply', '' )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input01, E_Input02, E_Input03, E_Input04 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx04, E_SpinEx05, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			self.DisableControl( E_TIME_SETTING )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )	
			return
			

		elif selectedId == E_FORMAT_HDD :	
			self.AddEnumControl( E_SpinEx01, 'Disk Format Type' )
			self.AddInputControl( E_Input01, 'Start HDD Format', '' )
			
			visibleControlIds = [ E_SpinEx01, E_Input01 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return
			

		elif selectedId == E_FACTORY_RESET :	
			self.AddEnumControl( E_SpinEx01, 'Reset Channel List' )
			self.AddEnumControl( E_SpinEx02, 'Reset Favorite Add-ons' )
			self.AddEnumControl( E_SpinEx03, 'Reset Configure Setting' )
		
			self.AddInputControl( E_Input01, 'Start Reset', '' )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input01 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx04 , E_SpinEx05, E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return
			

		elif selectedId == E_ETC :	
			self.AddEnumControl( E_SpinEx01, 'Channel Banner Duration' )	#	Erase channel list yes/no
			self.AddEnumControl( E_SpinEx02, 'Playback Banner Duration' )	#	Erase custom menu yes/no

			visibleControlIds = [ E_SpinEx01, E_SpinEx02 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return
			

		else :
			LOG_ERR( 'Can not find selected ID' )


	def DisableControl( self, aSelectedItem ):
		if aSelectedItem == E_LANGUAGE :
			selectedIndex = self.GetSelectedIndex( E_SpinEx03 )
			visibleControlIds = [ E_SpinEx04, E_SpinEx05 ]
			if selectedIndex == 0 :
				self.SetEnableControls( visibleControlIds, False )
			else :
				self.SetEnableControls( visibleControlIds, True )
		elif aSelectedItem == E_IP_SETTING :
			dhcp = ElisPropertyEnum( 'DHCP', self.mCommander ).GetProp( )
			visibleControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04 ]
			if dhcp == E_DHCP_ON :
				self.SetEnableControls( visibleControlIds, False )
			elif dhcp == E_DHCP_OFF :
				self.SetEnableControls( visibleControlIds, True )

		elif aSelectedItem == E_PARENTAL :
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_Input02 ]
			if self.mVisibleParental == True :
				self.SetEnableControls( visibleControlIds, True )
			else :
				self.SetEnableControls( visibleControlIds, False )

		elif aSelectedItem == E_TIME_SETTING :
			if self.mHasChannel == False :
				ElisPropertyEnum( 'Time Mode', self.mCommander ).SetProp( TIME_MANUAL )
				self.SetEnableControl( E_SpinEx01, False )
				self.SetEnableControl( E_Input01, False )
			else :
				selectedIndex = self.GetSelectedIndex( E_SpinEx01 )
				if selectedIndex == TIME_AUTOMATIC :
					self.SetEnableControl( E_Input02, False )
					self.SetEnableControl( E_Input03, False )
					self.SetEnableControl( E_Input01, True )
				else :
					self.SetEnableControl( E_Input01, False )
					self.SetEnableControl( E_Input02, True )
					self.SetEnableControl( E_Input03, True )


	def LoadIp( self ) :
		ipAddress = ElisPropertyInt( 'IpAddress', self.mCommander ).GetProp( )
		self.mSavedIpAddr = ipAddress
		self.mTempIpAddr = ipAddress
		subnet = ElisPropertyInt( 'SubNet', self.mCommander ).GetProp( )
		self.mSavedSubNet = subnet
		self.mTempSubNet = subnet
		gateway = ElisPropertyInt( 'Gateway', self.mCommander ).GetProp( )
		self.mSavedGateway = gateway
		self.mTempGateway = gateway
		dns = ElisPropertyInt( 'DNS', self.mCommander ).GetProp( )
		self.mSavedDns = dns
		self.mTempDns = dns


	def SaveIp( self ) :
		self.mSavedIpAddr = self.mTempIpAddr
		ElisPropertyInt( 'IpAddress', self.mCommander ).SetProp( self.mSavedIpAddr )

		self.mSavedSubNet = self.mTempSubNet
		ElisPropertyInt( 'SubNet', self.mCommander ).SetProp( self.mSavedSubNet )

		self.mSavedGateway = self.mTempGateway
		ElisPropertyInt( 'Gateway', self.mCommander ).SetProp( self.mSavedGateway )

		self.mSavedDns = self.mTempDns
		ElisPropertyInt( 'DNS', self.mCommander ).SetProp( self.mSavedDns )
		self.mCommander.NetWork_SaveSetting( )


	def ReLoadIp( self ) :
		self.mTempIpAddr	= self.mSavedIpAddr
		self.mTempSubNet	= self.mSavedSubNet
		self.mTempGateway	= self.mSavedGateway
		self.mTempDns		= self.mSavedDns


	def IpSetting( self, aControlId ) :
		if aControlId == E_SpinEx01 :
			self.ControlSelect( )
			if ElisPropertyEnum( 'DHCP', self.mCommander ).GetProp( ) == E_DHCP_OFF :
				self.SetControlLabelString( E_Input05, 'Save' )
			elif ElisPropertyEnum( 'DHCP', self.mCommander ).GetProp( ) == E_DHCP_ON :
				self.SetControlLabelString( E_Input05, 'Get IP Address' )
			self.DisableControl( E_IP_SETTING )
			
		elif aControlId == E_Input01 :		# IpAddr
			self.mTempIpAddr = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_IP, 'Input Ip Address', '%d.%d.%d.%d' % MakeHexToIpAddr( self.mTempIpAddr ) )
			self.mTempIpAddr = MakeStringToHex( self.mTempIpAddr )
			self.SetListControl( )

		elif aControlId == E_Input02 :		# SubNet
			self.mTempSubNet = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_IP, 'Input Subnet Mask', '%d.%d.%d.%d' % MakeHexToIpAddr( self.mTempSubNet ) )
			self.mTempSubNet = MakeStringToHex( self.mTempSubNet )
			self.SetListControl( )

		elif aControlId == E_Input03 :		# Gateway
			self.mTempGateway = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_IP, 'Input Gateway', '%d.%d.%d.%d' % MakeHexToIpAddr( self.mTempGateway ) )
			self.mTempGateway = MakeStringToHex( self.mTempGateway )
			self.SetListControl( )

		elif aControlId == E_Input04 :		# DNS
			self.mTempDns = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_IP, 'Input DNS', '%d.%d.%d.%d' % MakeHexToIpAddr( self.mTempDns ) )
			self.mTempDns = MakeStringToHex( self.mTempDns )
			self.SetListControl( )

		elif aControlId == E_Input05 :
			if ElisPropertyEnum( 'DHCP', self.mCommander ).GetProp( ) == E_DHCP_OFF :
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( 'Configure', 'Save Ip?' )
				dialog.doModal( )

				if dialog.IsOK() == E_DIALOG_STATE_YES :
					self.SaveIp( )

			elif ElisPropertyEnum( 'DHCP', self.mCommander ).GetProp( ) == E_DHCP_ON :
				pass


	def TimeSetting( self, aControlId ) :
		if aControlId == E_SpinEx01 :
			self.DisableControl( E_TIME_SETTING )
			return
				
		elif aControlId == E_Input01 :
			dialog = xbmcgui.Dialog( )
			channelList = self.mDataCache.Channel_GetList( )
			channelNameList = []
			for channel in channelList :
				channelNameList.append( channel.mName )
 			ret = dialog.select( 'Select Channel', channelNameList )

			if ret >= 0 :
				self.mSetupChannel = channelList[ ret ]
				self.SetControlLabel2String( E_Input01, self.mSetupChannel.mName )
			return

		elif aControlId == E_Input02 :
			self.mDate = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_DATE, 'Input Date', self.mDate )
			self.SetControlLabel2String( E_Input02, self.mDate )
			return
			
		elif aControlId == E_Input03 :
			self.mTime = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_TIME, 'Input Time', self.mTime )
			self.SetControlLabel2String( E_Input03, self.mTime )		
			return
			
		elif aControlId == E_Input04 :
			oriTimeMode = ElisPropertyEnum( 'Time Mode', self.mCommander ).GetProp( )
			oriLocalTimeOffset = ElisPropertyEnum( 'Local Time Offset', self.mCommander ).GetProp( )
			oriSummerTime = ElisPropertyEnum( 'Summer Time', self.mCommander ).GetProp( )
			ElisPropertyEnum( 'Time Mode', self.mCommander ).SetPropIndex( self.GetSelectedIndex( E_SpinEx01 ) )
			ElisPropertyEnum( 'Local Time Offset', self.mCommander ).SetPropIndex( self.GetSelectedIndex( E_SpinEx02) )
			ElisPropertyEnum( 'Summer Time', self.mCommander ).SetPropIndex( self.GetSelectedIndex( E_SpinEx03 ) )
 			
			if ElisPropertyEnum( 'Time Mode', self.mCommander ).GetProp( ) == TIME_AUTOMATIC :
				oriChannel = self.mDataCache.Channel_GetCurrent( )
				ElisPropertyInt( 'Time Setup Channel Number', self.mCommander ).SetProp( self.mSetupChannel.mNumber )
				self.mDataCache.Channel_SetCurrent( self.mSetupChannel.mNumber, self.mSetupChannel.mServiceType ) # Todo After : using ServiceType to different way
				ElisPropertyEnum( 'Time Installation', self.mCommander ).SetProp( 1 )

				progress = Progress( 'Setting Time...' )
				self.ProgressOpen = True
				progress.Update( 0 )
				for i in range( 10 ) :
					time.sleep( 1 )
					progress.Update( ( i + 1 ) * 10 )

					if progress.IsCanceled( ) == True :
						progress.Close( )
						break

					if self.mFinishEndSetTime == True :
						progress.Update( 100, 'Complete time set' )
						progress.Close( )
						self.SetListControl( )
						break
						
				if self.mFinishEndSetTime == False and progress.IsCanceled( ) != True :
						progress.Update( 100, 'Time set fail' )
						progress.Close( )
						ElisPropertyEnum( 'Time Mode', self.mCommander ).SetProp( oriTimeMode )
						ElisPropertyEnum( 'Local Time Offset', self.mCommander ).SetProp( oriLocalTimeOffset )
						ElisPropertyEnum( 'Summer Time', self.mCommander ).SetProp( oriSummerTime )

				self.ProgressOpen = False
				self.mFinishEndSetTime = False
				ElisPropertyEnum( 'Time Installation', self.mCommander ).SetProp( 0 )
				self.mDataCache.Channel_SetCurrent( oriChannel.mNumber, oriChannel.mServiceType) # Todo After : using ServiceType to different way
				return
				
			else :
				return
				# Todo System Date Setting

		

