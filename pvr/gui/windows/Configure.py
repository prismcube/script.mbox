import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
from pvr.gui.BaseWindow import SettingWindow, Action
import pvr.ElisMgr
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.GuiConfig import *
from pvr.Util import GuiLock, LOG_TRACE, LOG_ERR

class Configure( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
 
		leftGroupItems			= [ 'Language', 'Parental', 'Recording Option', 'Audio Setting', 'HDMI Setting', 'IP Setting', 'Format HDD', 'Factory Reset', 'Etc' ]
		descriptionList			= [ 'DESC Language', 'DESC Parental', 'DESC Recording Option', 'DESC Audio Setting', 'DESC HDMI Setting', 'DESC IP Setting', 'DESC Format HDD', 'DESC Factory Reset', 'DESC Etc' ]
	
		self.mCtrlLeftGroup 	= None
		self.mGroupItems 		= []
		self.mInitialized 		= False
		self.mLastFocused 		= E_SUBMENU_LIST_ID
		self.mPrevListItemID 	= 0

		for i in range( len( leftGroupItems ) ) :
			self.mGroupItems.append( xbmcgui.ListItem( leftGroupItems[i], descriptionList[i] ) )
			
	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mCtrlLeftGroup = self.getControl( E_SUBMENU_LIST_ID )
		self.mCtrlLeftGroup.addItems( self.mGroupItems )

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( 'Configure' )

		position = self.mCtrlLeftGroup.getSelectedPosition( )
		self.mCtrlLeftGroup.selectItem( position )
		self.SetListControl( )
		self.mInitialized = True

	def onAction( self, aAction ) :

		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )

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
				self.SetListControl( )
			elif focusId != E_SUBMENU_LIST_ID :
				self.ControlUp( )
	
		elif actionId == Action.ACTION_MOVE_DOWN :
			if focusId == E_SUBMENU_LIST_ID and selectedId != self.mPrevListItemID :
				self.mPrevListItemID = selectedId
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
			
		else :
			self.ControlSelect( )

		#elif ctrlItem.mControlType == ctrlItem.E_SETTING_LEFT_LABEL_BUTTON_CONTROL :
		#	ret =  xbmcgui.Dialog( ).yesno('Configure', 'Are you sure?')	# return yes = 1, no = 0
	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		if ( self.mLastFocused != aControlId ) or ( selectedId != self.mPrevListItemID ) :
			if aControlId == E_SUBMENU_LIST_ID :
				self.SetListControl( )
				if self.mLastFocused != aControlId :
					self.mLastFocused = aControlId
				if selectedId != self.mPrevListItemID :
					self.mPrevListItemID =selectedId
		

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
			self.AddEnumControl( E_SpinEx01, 'Lock Mainmenu' )

			pinCode = ElisPropertyInt( 'PinCode', self.mCommander ).GetProp( )
			self.AddInputControl( E_Input01, 'New PIN code', '%d' % pinCode )
			self.AddInputControl( E_Input02, 'Confirmation PIN code', '****' )
			self.AddEnumControl( E_SpinEx02, 'Age Restricted' )
			

			visibleControlIds = [ E_SpinEx01, E_Input01, E_Input02, E_SpinEx02 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
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
			self.AddEnumControl( E_SpinEx01, 'DHCP' )
			
			ipAddress = ElisPropertyInt( 'IpAddress', self.mCommander ).GetProp( )
			self.AddInputControl( E_Input01, 'IP Address', '%d.%d.%d.%d' % MakeHexToIpAddr( ipAddress ) )

			subnet = ElisPropertyInt( 'SubNet', self.mCommander ).GetProp( )
			self.AddInputControl( E_Input02, 'Subnet Mask', '%d.%d.%d.%d' % MakeHexToIpAddr( subnet ) )

			gateway = ElisPropertyInt( 'Gateway', self.mCommander ).GetProp( )
			self.AddInputControl( E_Input03, 'Gateway', '%d.%d.%d.%d' % MakeHexToIpAddr( gateway ) )

			dns = ElisPropertyInt( 'DNS', self.mCommander ).GetProp( )
			self.AddInputControl( E_Input04, 'DNS', '%d.%d.%d.%d' % MakeHexToIpAddr( dns ) )

			self.AddInputControl( E_Input05, '', '' )

			visibleControlIds = [ E_SpinEx01, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			self.DisableControl( E_IP_SETTING )
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
			selectedIndex = self.GetSelectedIndex( E_SpinEx01 )
			visibleControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04 ]
			if selectedIndex == 0 :
				self.SetEnableControls( visibleControlIds, False )
				self.SetControlLabelString( E_Input05, 'Get IP Address' )
			else :
				self.SetEnableControls( visibleControlIds, True )
				self.SetControlLabelString( E_Input05, 'Save' )

	def IpSetting( self, aControlId ) :
		if aControlId == E_SpinEx01 :
			self.DisableControl( E_IP_SETTING )
			self.ControlSelect( )
			
		elif aControlId == E_Input01 :		# IpAddr
			property = ElisPropertyInt( 'IpAddress', self.mCommander )
			ipAddr = property.GetProp( )
			tempval = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_IP, 'Input Ip Address', '%d.%d.%d.%d' % MakeHexToIpAddr( ipAddr ) )
			#property.SetProp( MakeStringToHex( tempval ) )
			self.SetListControl( )

		elif aControlId == E_Input02 :		# SubNet
			property = ElisPropertyInt( 'SubNet', self.mCommander )
			subnet = property.GetProp( )
			tempval = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_IP, 'Input Subnet Mask', '%d.%d.%d.%d' % MakeHexToIpAddr( subnet ) )
			#property.SetProp( MakeStringToHex( tempval ) )
			self.SetListControl( )

		elif aControlId == E_Input03 :		# Gateway
			property = ElisPropertyInt( 'Gateway', self.mCommander )
			gateway = property.GetProp( )
			tempval = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_IP, 'Input Gateway', '%d.%d.%d.%d' % MakeHexToIpAddr( gateway ) )
			#property.SetProp( MakeStringToHex( tempval ) )
			self.SetListControl( )

		elif aControlId == E_Input04 :		# DNS
			property = ElisPropertyInt( 'DNS', self.mCommander )
			dns = property.GetProp( )
			tempval = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_IP, 'Input DNS', '%d.%d.%d.%d' % MakeHexToIpAddr( dns ) )
			#property.SetProp( MakeStringToHex( tempval ) )
			self.SetListControl( )