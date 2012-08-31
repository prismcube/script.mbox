from pvr.gui.WindowImport import *
if sys.platform != 'win32' :
	from pvr.IpParser import *

E_LANGUAGE				= 0
E_PARENTAL				= 1
E_RECORDING_OPTION		= 2
E_AUDIO_SETTING			= 3
E_HDMI_SETTING			= 4
E_NETWORK_SETTING		= 5
E_TIME_SETTING			= 6
E_FORMAT_HDD			= 7
E_FACTORY_RESET			= 8
E_ETC					= 9
E_ETHERNET				= 100
E_WIFI					= 101

PING_TEST_INTERNAL		= 0
PING_TEST_EXTERNAL		= 1


class Configure( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )

		leftGroupItems			= [
		MR_LANG( 'Language' ),
		MR_LANG( 'Parental Control' ),
		MR_LANG( 'Recording Option' ),
		MR_LANG( 'Audio Setting' ),
		MR_LANG( 'HDMI Setting' ),
		MR_LANG( 'Network Setting' ),
		MR_LANG( 'Time Setting' ),
		MR_LANG( 'HDD Format' ),
		MR_LANG( 'Factory Reset' ),
		MR_LANG( 'Miscellaneous' ) ]
		
		self.mDescriptionList	= [
		MR_LANG( 'Set the STB language preferences' ),
		MR_LANG( 'Set limits on your kids\' STB use' ),
		MR_LANG( 'Adjust settings for recording in STB' ),
		MR_LANG( 'Set the system\'s digital audio output settings' ),
		MR_LANG( 'Set the output settings for TVs that support HDMI cable' ),
		MR_LANG( 'Set up or change network connections including wireless' ),
		MR_LANG( 'Adjust settings related to the system\'s date and time' ),
		MR_LANG( 'Delete eveything off your hard drive' ),
		MR_LANG( 'Restore the system software to its default settings' ),
		MR_LANG( 'Adjust additional settings for STB including fan speed control' ) ]

		self.mCtrlLeftGroup 	= None
		self.mGroupItems 		= []
		self.mLastFocused 		= E_SUBMENU_LIST_ID
		self.mPrevListItemID 	= -1

		self.mUseNetworkType	= NETWORK_ETHERNET

		self.mSavedNetworkType	= NET_DHCP
		self.mSavedIpAddr		= 'None'
		self.mSavedSubNet		= 'None'
		self.mSavedGateway		= 'None'
		self.mSavedDns			= 'None'

		self.mTempNetworkType	= NET_DHCP
		self.mTempIpAddr		= 'None'
		self.mTempSubNet		= 'None'
		self.mTempGateway		= 'None'
		self.mTempDns			= 'None'

		self.mReLoadIp			= False
		self.mVisibleParental	= False

		self.mDate				= 0
		self.mTime				= 0
		self.mSetupChannel		= None
		self.mHasChannel		= False

		self.mSavedTimeMode		= TIME_MANUAL
		self.mSavedTimeChannel	= 0
		self.mSavedLocalOffset	= 0
		self.mSavedSummerTime	= 0

		self.mIpParser			= None
		self.mProgress			= None

		self.mWireless			= None
		self.mHiddenSsid		= 'None'
		self.mUseHiddenId		= NOT_USE_HIDDEN_SSID
		self.mCurrentSsid		= 'None'
		self.mUseEncrypt		= NOT_USE_PASSWORD_ENCRYPT
		self.mEncriptType		= ENCRIPT_TYPE_WEP
		self.mPasswordType		= PASSWORD_TYPE_ASCII
		self.mPassWord 			= None

		for i in range( len( leftGroupItems ) ) :
			self.mGroupItems.append( xbmcgui.ListItem( leftGroupItems[i] ) )


	def onInit( self ) :
		self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( False )

		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mCtrlLeftGroup = self.getControl( E_SUBMENU_LIST_ID )
		self.mCtrlLeftGroup.addItems( self.mGroupItems )

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( MR_LANG( 'Installation' ) )

		position = self.mCtrlLeftGroup.getSelectedPosition( )
		self.mCtrlLeftGroup.selectItem( position )
		if sys.platform != 'win32' :
			self.mIpParser = IpParser( )
			self.mWireless = WirelessParser( )
			self.LoadEhternetInformation( )
			self.LoadWifi( )
			self.mUseNetworkType = GetCurrentNetworkType( )

		self.mVisibleParental = False
		self.mReLoadIp = False
		self.SetListControl( )
		self.mInitialized = True
		self.mPrevListItemID = -1


	def Close( self ) :
		self.mInitialized = False
		self.ResetAllControl( )
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( '' )
		self.SetVideoRestore( )
		WinMgr.GetInstance( ).CloseWindow( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		self.GlobalAction( actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.Close( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_PARENT_DIR :
			self.Close( )

		elif actionId == Action.ACTION_MOVE_UP :
			if focusId == E_SUBMENU_LIST_ID and selectedId != self.mPrevListItemID :
				self.mPrevListItemID = selectedId
				self.mReLoadIp = True
				self.mVisibleParental = False
				self.mUseNetworkType = GetCurrentNetworkType( )
				self.SetListControl( )
			elif focusId != E_SUBMENU_LIST_ID :
				self.ControlUp( )

		elif actionId == Action.ACTION_MOVE_DOWN :
			if focusId == E_SUBMENU_LIST_ID and selectedId != self.mPrevListItemID :
				self.mPrevListItemID = selectedId
				self.mReLoadIp = True
				self.mVisibleParental = False
				self.mUseNetworkType = GetCurrentNetworkType( )
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
				self.setDefaultControl( )
			elif focusId != E_SUBMENU_LIST_ID and ( focusId % 10 ) == 1 :
				self.ControlRight( )


	def onClick( self, aControlId ) :
		groupId = self.GetGroupId( aControlId )
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		
		if selectedId == E_LANGUAGE :
			self.DisableControl( E_LANGUAGE )
			self.ControlSelect( )
			return

		elif selectedId == E_NETWORK_SETTING :
			if sys.platform == 'win32' :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Not support Win32' ) )
	 			dialog.doModal( )
	 			return

			if groupId == E_SpinEx05 :
				self.mUseNetworkType = self.GetSelectedIndex( E_SpinEx05 )
				self.SetListControl( )
				self.setDefaultControl( )

			elif groupId == E_Input06 :
				context = []
				context.append( ContextItem( MR_LANG( 'Internal Network Test' ), PING_TEST_INTERNAL ) )
				context.append( ContextItem( MR_LANG( 'External Network Test' ), PING_TEST_EXTERNAL ) )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
				dialog.SetProperty( context )
				dialog.doModal( )
				contextAction = dialog.GetSelectedAction( )
				if contextAction < 0 :
					return
				if contextAction == PING_TEST_INTERNAL :
					self.ShowProgress( MR_LANG( 'Testing...' ), 10 )
					time.sleep( 1 )
					if PingTestInternal( ) == True :
						state = MR_LANG( 'Connected to the default router' )
					else :
						state = MR_LANG( 'Disconnected from the default router' )
				else :
					addr = InputKeyboard( E_INPUT_KEYBOARD_TYPE_NO_HIDE, MR_LANG( 'Enter an IP address for ping test' ), '', 30 )
					self.ShowProgress( MR_LANG( 'Testing...' ), 10 )
					time.sleep( 1 )
					if PingTestExternal( addr ) == True :
						state = MR_LANG( 'External ping test has passed' )
					else :
						state = MR_LANG( 'External ping test has failed' )
				try :
					self.mProgress.SetResult( True )
				except Exception, e :
					LOG_ERR( 'Error exception[%s]' % e )
				time.sleep( 1.5 )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Test Result' ), MR_LANG( 'Network State : %s' ) % state )
				dialog.doModal( )

			elif self.mUseNetworkType == NETWORK_ETHERNET :
				self.EthernetSetting( groupId )
			elif self.mUseNetworkType == NETWORK_WIRELESS :
				self.WifiSetting( groupId )

		elif selectedId == E_TIME_SETTING :
			self.TimeSetting( groupId )
			return

		elif selectedId == E_PARENTAL and self.mVisibleParental == False and groupId == E_Input01 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( MR_LANG( 'Enter 4-digit PIN code' ), '', 4, True )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				tempval = dialog.GetString( )
				if tempval == '' :
					return
				if int( tempval ) == ElisPropertyInt( 'PinCode', self.mCommander ).GetProp( ) :
					self.mVisibleParental = True
					self.DisableControl( E_PARENTAL )
				else :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Sorry, that PIN code does not match' ) )					
		 			dialog.doModal( )
			return

		elif selectedId == E_PARENTAL and groupId == E_Input02 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( MR_LANG( 'Enter your new PIN code' ), '', 4, True )			
 			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				newpin = dialog.GetString( )
				if newpin == '' or len( newpin ) != 4 :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( '4-digit PIN code is required' ) )
		 			dialog.doModal( )
					return
			else :
				return

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( MR_LANG( 'Confirm PIN code' ), '', 4, True )
			dialog.doModal( )

 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
 				confirm = dialog.GetString( )
 				if confirm == '' :
 					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'New PIN code does not match' ) )
		 			dialog.doModal( )
 					return
				if int( newpin ) != int( confirm ) :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'New PIN code does not match' ) )
		 			dialog.doModal( )
					return
			else :
				return

			ElisPropertyInt( 'PinCode', self.mCommander ).SetProp( int( newpin ) )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Change PIN code' ), MR_LANG( 'Your PIN code has been changed successfully' ) )
 			dialog.doModal( )

 		elif selectedId == E_FACTORY_RESET and groupId == E_Input01 :
 			"""
 			#resetChannel = ElisPropertyEnum( 'Reset Channel List', self.mCommander ).GetProp( )
 			#resetFavoriteAddons = ElisPropertyEnum( 'Reset Favorite Add-ons', self.mCommander ).GetProp( )
 			#resetSystem = ElisPropertyEnum( 'Reset Configure Setting', self.mCommander ).GetProp( )
 			if ( resetChannel | resetFavoriteAddons | resetSystem ) == 0 :
 				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No reset options selected' ) )
		 		dialog.doModal( )
		 		return
		 	else :
		 	"""
	 		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'WARNING' ), MR_LANG( 'THIS WILL RESTORE TO FACTORY SETTINGS\nDO YOU WANT TO CONTINUE?' ) )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.OpenBusyDialog( )
				ret1 = False
				ret2 = False
				#self.ShowProgress( MR_LANG( 'Now restoring...' ), 30 )
				ret1 = self.mCommander.System_SetDefaultChannelList( )
				ret2 = self.mCommander.System_FactoryReset( )
				self.mDataCache.LoadChannelList( )
				self.mDataCache.LoadAllSatellite( )

				if self.mDataCache.mChannelList and len( self.mDataCache.mChannelList ) >= 0 :
					self.mDataCache.Channel_SetCurrent( self.mDataCache.mChannelList[0].mNumber, ElisEnum.E_SERVICE_TYPE_TV )

				self.CloseBusyDialog( )

				if ret1 == True and ret2 == True :
					#self.mProgress.SetResult( True )
					#time.sleep( 1 )
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Reset your STB Settings' ), MR_LANG( 'Settings have been restored to factory default' ) )
		 			dialog.doModal( )

		 			from ElisProperty import ResetHash
					ResetHash( )
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_FIRST_INSTALLATION, WinMgr.WIN_ID_MAINMENU )
				else :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Factory reset has failed to complete' ) )
		 			dialog.doModal( )

				self.SetListControl( )

		else :
			self.ControlSelect( )


	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )

		if aControlId == E_SUBMENU_LIST_ID :
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
		else :
			self.ShowDescription( aControlId )

		if ( self.mLastFocused != aControlId ) or ( selectedId != self.mPrevListItemID ) :
			if aControlId == E_SUBMENU_LIST_ID :
				if self.mLastFocused != aControlId :
					self.mLastFocused = aControlId
				if selectedId != self.mPrevListItemID :
					self.mPrevListItemID =selectedId
					self.mReLoadIp = True
					self.mVisibleParental = False
				self.SetListControl( )


	def SetListControl( self ) :
		self.ResetAllControl( )
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( False )

		if selectedId == E_LANGUAGE :
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddEnumControl( E_SpinEx01, 'Language', MR_LANG( 'Menu Language' ), MR_LANG( 'Select the language for the menu to be in' ) )
			self.AddEnumControl( E_SpinEx02, 'Audio Language', None, MR_LANG( 'Select the language that you wish to listen to' ) )
			self.AddEnumControl( E_SpinEx03, 'Subtitle Language', None, MR_LANG( 'Select the language for the subtitle to be in' ) )
			self.AddEnumControl( E_SpinEx04, 'Secondary Subtitle Language', None, MR_LANG( 'Select the language for the secondary subtitle to be in' ) )
			self.AddEnumControl( E_SpinEx05, 'Hearing Impaired', None, MR_LANG( 'Set the hearing impaired function' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			time.sleep( 0.2 )
			self.DisableControl( E_LANGUAGE )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return

		elif selectedId == E_PARENTAL :	
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddInputControl( E_Input01, MR_LANG( 'Edit Parental Settings' ), '', MR_LANG( 'Enter your PIN code to change the parental settings' ) )
			self.AddEnumControl( E_SpinEx01, 'Lock Mainmenu', MR_LANG( ' - Lock Main Menu' ), MR_LANG( 'Set a restriction for the main menu' ) )
			self.AddEnumControl( E_SpinEx02, 'Age Restricted', MR_LANG( ' - Age Limit'), MR_LANG( 'Set an access restriction to chosen channels' ) )
			self.AddInputControl( E_Input02, MR_LANG( ' - Change PIN Code' ), '', MR_LANG( 'Change the current PIN code' ) )

			visibleControlIds = [ E_SpinEx01, E_Input01, E_SpinEx02, E_Input02 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input03, E_Input04, E_Input05, E_Input06 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			time.sleep( 0.2 )
			self.DisableControl( E_PARENTAL )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return

		elif selectedId == E_RECORDING_OPTION :
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddEnumControl( E_SpinEx01, 'Automatic Timeshift', None, MR_LANG( 'When set to "On", the STB automatically start recording, either the channel that is already selected when the STB was turned on from standby, or when a different channel is selected' ) )
			self.AddEnumControl( E_SpinEx02, 'Timeshift Buffer Size', None, MR_LANG( 'Select the preferred size of timeshift buffer' ) )
			self.AddEnumControl( E_SpinEx03, 'Default Rec Duration', None, MR_LANG( 'Select recording duration for a channel that has no EPG info' ) )
			self.AddEnumControl( E_SpinEx04, 'Pre-Rec Time', None, MR_LANG( 'Set the pre-recording time for a EPG channel' ) )
			self.AddEnumControl( E_SpinEx05, 'Post-Rec Time', None, MR_LANG( 'Set the post-recording time for a EPG channel' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return

		elif selectedId == E_AUDIO_SETTING :
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddEnumControl( E_SpinEx01, 'Audio Dolby', MR_LANG( 'Dolby Audio' ), MR_LANG( 'When set to "On", Dolby Digital audio will be selected automatically when broadcast' ) )
			self.AddEnumControl( E_SpinEx02, 'Audio HDMI', None, MR_LANG( 'Set the Audio HDMI format' ) )
			self.AddEnumControl( E_SpinEx03, 'Audio Delay', None, MR_LANG( 'Select a delay time for audio' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03 ]
			self.SetEnableControls( visibleControlIds, True )
			self.SetVisibleControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx04, E_SpinEx05,  E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return

		elif selectedId == E_HDMI_SETTING :
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddEnumControl( E_SpinEx01, 'HDMI Format', None, MR_LANG( 'Set the display\'s HDMI resolution' ) )
			self.AddEnumControl( E_SpinEx02, 'Show 4:3', MR_LANG( 'TV Screen Format' ), MR_LANG( 'Select the display format for TV screen' ) )
			self.AddEnumControl( E_SpinEx03, 'HDMI Color Space', None, MR_LANG( 'Set RGB or YUV for HDMI Color Space' ) )
			self.AddEnumControl( E_SpinEx04, 'TV System', None, MR_LANG( 'Set your TV system format' ) )
			
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return

		elif selectedId == E_NETWORK_SETTING :
			self.AddUserEnumControl( E_SpinEx05, MR_LANG( 'Network Connection' ), USER_ENUM_LIST_NETWORK_TYPE, self.mUseNetworkType, MR_LANG( 'Select Ethernet or Wireless for your network connection' ) )
			#self.AddInputControl( E_Input06, MR_LANG( ' - Connection Test' ), '', MR_LANG( 'Determine your network connection is accessible' ) )

			if self.mUseNetworkType == NETWORK_WIRELESS :
				self.AddInputControl( E_Input01, MR_LANG( 'Search AP' ), self.mCurrentSsid, MR_LANG( 'Search Access Points around your STB' ) )
				self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Hidden SSID' ), USER_ENUM_LIST_ON_OFF, self.mUseHiddenId, MR_LANG( 'Enable hidden Subsystem Identification (SSID)' ) )
				self.AddInputControl( E_Input02, MR_LANG( ' - Set Hidden SSID' ), self.mHiddenSsid, MR_LANG( 'Enter the hidden SSID you wish to use' ) )
				self.AddUserEnumControl( E_SpinEx02, MR_LANG( 'Encryption' ), USER_ENUM_LIST_ON_OFF, self.mUseEncrypt, MR_LANG( 'Enable encryption for a secure wireless data transmissions' ) )
				self.AddUserEnumControl( E_SpinEx03, MR_LANG( ' - Encryption Method' ), USER_ENUM_LIST_ENCRIPT_TYPE, self.mEncriptType, MR_LANG( 'Select an encryption method for your network' ) )
				self.AddUserEnumControl( E_SpinEx04, MR_LANG( ' - Encryption Key Type' ), USER_ENUM_LIST_PASSWORD_TYPE, self.mPasswordType, MR_LANG( 'Set ASCII/HEX mode for your key' ) )
				self.AddInputControl( E_Input03, MR_LANG( ' - Set Encryption Key' ), StringToHidden( self.mPassWord ), MR_LANG( 'Enter the encryption key for wireless connection' ) )
				self.AddInputControl( E_Input04, MR_LANG( 'Apply' ), '', MR_LANG( 'Press the OK button to connect to the AP you have chosen' ) )

				visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04 ]
				self.SetVisibleControls( visibleControlIds, True )
				self.SetEnableControls( visibleControlIds, True )

				hideControlIds = [ E_Input05, E_Input06 ]
				self.SetVisibleControls( hideControlIds, False )
				
				self.InitControl( )
				time.sleep( 0.2 )
				self.DisableControl( E_WIFI )
				self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )

			else :
				if self.mReLoadIp == True :
					self.ReLoadEthernetIp( )
					self.mReLoadIp = False
					
				self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Assign IP Address' ), USER_ENUM_LIST_DHCP_STATIC, self.mTempNetworkType, MR_LANG( 'When set to "DHCP", your IP address will be automatically allocated by the DHCP server' ) )
				self.AddInputControl( E_Input01, MR_LANG( 'IP Address' ), self.mTempIpAddr, MR_LANG( 'Enter your IP address' ) )
				self.AddInputControl( E_Input02, MR_LANG( 'Subnet Mask' ), self.mTempSubNet, MR_LANG( 'Enter your subnet mask' ) )
				self.AddInputControl( E_Input03, MR_LANG( 'Gateway' ), self.mTempGateway, MR_LANG( 'Enter your gateway' ) )
				self.AddInputControl( E_Input04, MR_LANG( 'DNS' ), self.mTempDns, MR_LANG( 'Enter the DNS server address' ) )
				self.AddInputControl( E_Input05, MR_LANG( 'Apply') , '', MR_LANG( 'Press the OK button to save the IP address settings' ) )

				visibleControlIds = [ E_SpinEx01, E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06 ]
				self.SetVisibleControls( visibleControlIds, True )
				self.SetEnableControls( visibleControlIds, True )

				hideControlIds = [ E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
				self.SetVisibleControls( hideControlIds, False )
				
				self.InitControl( )
				time.sleep( 0.2 )
				self.DisableControl( E_ETHERNET )
				self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )

			if self.GetGroupId( self.getFocusId( ) ) != E_SpinEx05 :
				self.getControl( E_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )

		elif selectedId == E_TIME_SETTING :
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			setupChannelNumber = ElisPropertyInt( 'Time Setup Channel Number', self.mCommander ).GetProp( )
			self.mSetupChannel = self.mDataCache.Channel_GetByNumber( setupChannelNumber )
			self.mHasChannel = True
			if self.mSetupChannel and self.mSetupChannel.mError == 0 :
				channelName = self.mSetupChannel.mName
			else :
				channelList = self.mDataCache.Channel_GetList( )
				if channelList :
					self.mSetupChannel = channelList[0]
					channelName = self.mSetupChannel.mName
				else :
					self.mHasChannel = False
					channelName = MR_LANG( 'None' )
					ElisPropertyEnum( 'Time Mode', self.mCommander ).SetProp( TIME_MANUAL )

			self.AddEnumControl( E_SpinEx01, 'Time Mode', MR_LANG( 'Time & Date' ), MR_LANG( 'When set to "Automatic", the time and date will be obtained by the receiver automatically from a specific channel that you select' ) )
			self.AddInputControl( E_Input01, MR_LANG( 'Channel' ), channelName, MR_LANG( 'Select a channel you want to set your time and date by' ) )
			self.mDate = TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_DD_MM_YYYY )
			self.AddInputControl( E_Input02, MR_LANG( 'Date' ), self.mDate, MR_LANG( 'Enter today\'s date' ) )
			self.mTime = TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_HH_MM )
			self.AddInputControl( E_Input03, MR_LANG( 'Time' ), self.mTime, MR_LANG( 'Set the local time' ) )
			self.AddEnumControl( E_SpinEx02, 'Local Time Offset', None, MR_LANG( 'Set the time zone that will be the basis for the date and time display' ) )
			self.AddEnumControl( E_SpinEx03, 'Summer Time', None, MR_LANG( 'When set to "Automatic", the system automatically change over to and from summer and winter time' ) )
			self.AddInputControl( E_Input04, MR_LANG( 'Apply' ), '', MR_LANG( 'Press the OK button to save settings' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input01, E_Input02, E_Input03, E_Input04 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx04, E_SpinEx05, E_Input05, E_Input06 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			time.sleep( 0.2 )
			self.DisableControl( E_TIME_SETTING )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )	
			return

		elif selectedId == E_FORMAT_HDD :
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddEnumControl( E_SpinEx01, 'Disk Format Type', MR_LANG( 'File System' ), MR_LANG( 'Select a disk file system format for your hard drive' ) )
			self.AddInputControl( E_Input01, MR_LANG( 'Format HDD Now' ), '', MR_LANG( 'Press the OK button to format your hard drive' ) )

			visibleControlIds = [ E_SpinEx01, E_Input01 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return

		elif selectedId == E_FACTORY_RESET :
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			#self.AddEnumControl( E_SpinEx01, 'Reset Channel List', None, MR_LANG( 'Your channel list will be restored to default' ) )
			#self.AddEnumControl( E_SpinEx02, 'Reset Favorite Add-ons', None, MR_LANG( 'All your favorite add-ons will be deleted after factory reset' ) )
			#self.AddEnumControl( E_SpinEx03, 'Reset Configure Setting', MR_LANG( 'Reset Configuration Setting' ), MR_LANG( 'User settings you have set will be restored to default' ) )
			self.AddInputControl( E_Input01, MR_LANG( 'Start Factory Reset'), '', MR_LANG( 'Restore your system to the default based on settings you configured' ) )

			visibleControlIds = [ E_Input01 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 , E_SpinEx05, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return

		elif selectedId == E_ETC :
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddEnumControl( E_SpinEx01, 'Deep Standby', None, MR_LANG( 'When set to "On", the system automatically switches to standby mode after a period of inactivity to help reduce the amount of electricity used' ) )
			self.AddEnumControl( E_SpinEx02, 'Fan Control', None, MR_LANG( 'Adjust the fan speed level for your system' ) )
			self.AddEnumControl( E_SpinEx03, 'Channel Banner Duration', MR_LANG( 'Channel Banner Time' ), MR_LANG( 'Set the time the channel info is to be displayed when zapping' ) )		#	Erase channel list yes/no
			self.AddEnumControl( E_SpinEx04, 'Playback Banner Duration', MR_LANG( 'Playback Banner Time' ), MR_LANG( 'Set the time for the playback info to be displayed on the screen' ) )	#	Erase custom menu yes/no

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return

		else :
			LOG_ERR( 'Can not find selected ID' )


	def DisableControl( self, aSelectedItem ) :
		if aSelectedItem == E_LANGUAGE :
			selectedIndex = self.GetSelectedIndex( E_SpinEx03 )
			visibleControlIds = [ E_SpinEx04, E_SpinEx05 ]
			if selectedIndex == 0 :
				self.SetEnableControls( visibleControlIds, False )
			else :
				self.SetEnableControls( visibleControlIds, True )
		elif aSelectedItem == E_ETHERNET :
			visibleControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04 ]
			if self.mTempNetworkType == NET_DHCP :
				self.SetEnableControls( visibleControlIds, False )
			else :
				self.SetEnableControls( visibleControlIds, True )

		elif aSelectedItem == E_WIFI :
			if self.mUseHiddenId == NOT_USE_HIDDEN_SSID :
				self.SetEnableControl( E_Input01, True )
				self.SetEnableControl( E_Input02, False )
			else :
				self.SetEnableControl( E_Input01, False )
				self.SetEnableControl( E_Input02, True )

			if self.mUseEncrypt == NOT_USE_PASSWORD_ENCRYPT :
				self.SetEnableControl( E_SpinEx03, False )
			else :
				self.SetEnableControl( E_SpinEx03, True )
				
		elif aSelectedItem == E_PARENTAL :
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_Input02 ]
			if self.mVisibleParental == True :
				self.SetEnableControls( visibleControlIds, True )
			else :
				self.SetEnableControls( visibleControlIds, False )

		elif aSelectedItem == E_TIME_SETTING :
			if self.mHasChannel == False :
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


	def LoadEhternetInformation( self ) :
		self.LoadEthernetType( )
		self.LoadEthernetAddress( )


	def LoadEthernetType( self ) :
		ret = self.mIpParser.LoadEthernetType( )
		if ret == True :
			self.mSavedNetworkType	= self.mIpParser.GetEthernetType( )
			self.mTempNetworkType	= self.mIpParser.GetEthernetType( )
		else :
			self.mSavedNetworkType	= NET_DHCP
			self.mTempNetworkType	= NET_DHCP
			LOG_ERR( 'Can not read network type( dhcp/static )' )


	def LoadEthernetAddress( self ) :
		self.mIpParser.LoadEthernetAddress( )
		if GetCurrentNetworkType( ) != NETWORK_ETHERNET :
			self.mSavedIpAddr, self.mSavedSubNet, self.mSavedGateway, self.mSavedDns = 'None', 'None', 'None', 'None'
			self.mTempIpAddr,  self.mTempSubNet,  self.mTempGateway,  self.mTempDns  = 'None', 'None', 'None', 'None'
		else :
			self.mSavedIpAddr, self.mSavedSubNet, self.mSavedGateway, self.mSavedDns = self.mIpParser.GetEthernetAddress( )
			self.mTempIpAddr,  self.mTempSubNet,  self.mTempGateway,  self.mTempDns  = self.mIpParser.GetEthernetAddress( )


	def ConnectEthernet( self ) :
		self.OpenBusyDialog( )
		ret = self.mIpParser.SetEthernet( self.mTempNetworkType, self.mTempIpAddr, self.mTempSubNet, self.mTempGateway, self.mTempDns )
		SetCurrentNetworkType( NETWORK_ETHERNET )
		if ret == False :
			self.CloseBusyDialog( )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Network setup has failed to complete' ) )
 			dialog.doModal( )
		else :
			if self.mTempNetworkType == NET_DHCP :
				self.mSavedNetworkType = self.mTempNetworkType
				self.LoadEthernetAddress( )
				SetIpAddressProperty( self.mSavedIpAddr, self.mSavedSubNet, self.mSavedGateway, self.mSavedDns )
				self.CloseBusyDialog( )
				self.SetListControl( )
			else :
				self.mSavedIpAddr = self.mTempIpAddr
				self.mSavedSubNet = self.mTempSubNet
				self.mSavedGateway = self.mTempGateway
				self.mSavedDns = self.mTempDns
				self.mSavedNetworkType = self.mTempNetworkType
				SetIpAddressProperty( self.mSavedIpAddr, self.mSavedSubNet, self.mSavedGateway, self.mSavedDns )
				self.CloseBusyDialog( )


	def ReLoadEthernetIp( self ) :
		self.mTempIpAddr			= self.mSavedIpAddr
		self.mTempSubNet			= self.mSavedSubNet
		self.mTempGateway			= self.mSavedGateway
		self.mTempDns				= self.mSavedDns
		self.mTempNetworkType		= self.mSavedNetworkType


	def EthernetSetting( self, aControlId ) :
		if aControlId == E_SpinEx01 :
			if self.mTempNetworkType == NET_DHCP :
				self.mTempNetworkType = NET_STATIC
			else :
				self.mTempNetworkType = NET_DHCP
			self.DisableControl( E_ETHERNET )
			
		elif aControlId == E_Input01 :
			self.mTempIpAddr = self.ShowIpInputDialog( self.mTempIpAddr )
			self.SetListControl( )

		elif aControlId == E_Input02 :
			self.mTempSubNet = self.ShowIpInputDialog( self.mTempSubNet )
			self.SetListControl( )

		elif aControlId == E_Input03 :
			self.mTempGateway = self.ShowIpInputDialog( self.mTempGateway )
			self.SetListControl( )

		elif aControlId == E_Input04 :
			self.mTempDns = self.ShowIpInputDialog( self.mTempDns )
			self.SetListControl( )

		elif aControlId == E_Input05 :
			if self.mTempNetworkType == NET_STATIC :
				if self.mTempIpAddr == 'None' or self.mTempSubNet == 'None' or self.mTempGateway == 'None' or self.mTempDns == 'None' :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
#					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Not enough information' ) )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Invalid IP address' ) )					
					dialog.doModal( )
					return
			self.ConnectEthernet( )


	def WifiSetting( self, aControlId ) :
		apList = []
		if aControlId == E_SpinEx01 or aControlId == E_SpinEx02 :
			self.mUseHiddenId = self.GetSelectedIndex( E_SpinEx01 )
			self.mUseEncrypt = self.GetSelectedIndex( E_SpinEx02 )
			self.DisableControl( E_WIFI )

		elif aControlId == E_SpinEx03 or aControlId == E_SpinEx04 :
			self.mEncriptType	= self.GetSelectedIndex( E_SpinEx03 )
			self.mPasswordType	= self.GetSelectedIndex( E_SpinEx04 )

		elif aControlId == E_Input01 :
			self.OpenBusyDialog( )
			dev = self.mWireless.GetWifidevice( )
			if dev == None :
				self.CloseBusyDialog( )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Devices not found' ) )
				dialog.doModal( )
				return

			apList = self.mWireless.ScanWifiAP( dev )
			self.CloseBusyDialog( )
			dialog = xbmcgui.Dialog( )
			if apList == None :
				ret = dialog.select( MR_LANG( 'Select AP' ), [ MR_LANG( 'No AP list' ) ] )
			else :
				apNameList = []
				for ap in apList :
					apNameList.append( ap[0] + MR_LANG( ' -   quality : %s Encryption : %s' ) % ( ap[1], ap[2] ) )
				dialog = xbmcgui.Dialog( )
				ret = dialog.select( MR_LANG( 'Select AP' ), apNameList )
				if ret >= 0 :
					self.mCurrentSsid = apList[ret][0]
					self.SetControlLabel2String( E_Input01, self.mCurrentSsid )

		elif aControlId == E_Input02 :
			self.mHiddenSsid = InputKeyboard( E_INPUT_KEYBOARD_TYPE_NO_HIDE, MR_LANG( 'Enter your SSID' ), self.mHiddenSsid, 30 )
			self.SetControlLabel2String( E_Input02, self.mHiddenSsid )

		elif aControlId == E_Input03 :
			self.mPassWord = InputKeyboard( E_INPUT_KEYBOARD_TYPE_HIDE, MR_LANG( 'Enter an encryption key' ), self.mPassWord, 30 )
			self.SetControlLabel2String( E_Input03, StringToHidden( self.mPassWord ) )

		elif aControlId == E_Input04 :
			dev = self.mWireless.GetWifidevice( )
			if apList == None or dev == None :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'AP or devices not found' ) )
				dialog.doModal( )
				return

			self.OpenBusyDialog( )
			ret1 = self.mWireless.WriteWpaSupplicant( self.mUseHiddenId, self.mHiddenSsid, self.mCurrentSsid, self.mUseEncrypt, self.mEncriptType, self.mPasswordType, self.mPassWord )
			ret2 = self.mWireless.ConnectWifi( dev )
			SetCurrentNetworkType( NETWORK_WIRELESS )
			addressIp, addressMask, addressGateway, addressNameServer = GetNetworkAddress( dev )
			SetIpAddressProperty( addressIp, addressMask, addressGateway, addressNameServer )
			self.CloseBusyDialog( )
			if ret1 == False :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'STB was unable to save the Wifi configuration' ) )
			dialog.doModal( )


	def LoadWifi( self ) :
		if self.mWireless.LoadWpaSupplicant( ) == True :
			self.mCurrentSsid		= self.mWireless.GetCurrentSsid( )
			self.mUseEncrypt		= self.mWireless.GetUseEncrypt( )
			if self.mUseEncrypt == True :
				self.mEncriptType	= self.mWireless.GetEncryptType( )
			self.mPasswordType		= self.mWireless.GetPasswordType( )
			self.mPassWord 			= self.mWireless.GetPassword( )
		else :
			LOG_ERR( 'Load Wpa Supplicant Fail' )


	def ShowIpInputDialog( self, aIpAddr ) :
		if aIpAddr == 'None' :
			aIpAddr = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_IP, MR_LANG( 'Enter an IP address' ), '0.0.0.0' )			
		else :
			aIpAddr = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_IP, MR_LANG( 'Enter an IP address' ), aIpAddr )
			
		return aIpAddr


	@RunThread
	def ShowProgress( self, aString, aTime ) :
		self.mProgress = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_FORCE_PROGRESS )
		self.mProgress.SetDialogProperty( aTime, aString )
		self.mProgress.doModal( )
		return


	def TimeSetting( self, aControlId ) :
		if aControlId == E_SpinEx01 :
			self.DisableControl( E_TIME_SETTING )

		elif aControlId == E_Input01 :
			dialog = xbmcgui.Dialog( )
			channelList = self.mDataCache.Channel_GetList( )
			channelNameList = []
			for channel in channelList :
				channelNameList.append( channel.mName )

			ret = dialog.select( MR_LANG( 'Select a channel to set your time by' ), channelNameList )

			if ret >= 0 :
				self.mSetupChannel = channelList[ ret ]
				self.SetControlLabel2String( E_Input01, self.mSetupChannel.mName )

		elif aControlId == E_Input02 :
			self.mDate = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_DATE, MR_LANG( 'Enter today\'s date' ), self.mDate )
			self.SetControlLabel2String( E_Input02, self.mDate )

		elif aControlId == E_Input03 :
			self.mTime = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_TIME, MR_LANG( 'Enter your local time' ), self.mTime )
			self.SetControlLabel2String( E_Input03, self.mTime )		
			return

		elif aControlId == E_Input04 :
			self.LoadSavedTime( )
			oriChannel = self.mDataCache.Channel_GetCurrent( )
			self.SetTimeProperty( )
			mode = ElisPropertyEnum( 'Time Mode', self.mCommander ).GetProp( )

			if mode == TIME_AUTOMATIC :
				ElisPropertyInt( 'Time Setup Channel Number', self.mCommander ).SetProp( self.mSetupChannel.mNumber )
				self.mDataCache.Channel_SetCurrent( self.mSetupChannel.mNumber, self.mSetupChannel.mServiceType ) # Todo After : using ServiceType to different way
				ElisPropertyEnum( 'Time Installation', self.mCommander ).SetProp( 1 )

				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_FORCE_PROGRESS )
				dialog.SetDialogProperty( 15, MR_LANG( 'Setting Time...' ), ElisEventTimeReceived.getName( ) )
				dialog.doModal( )
				self.OpenBusyDialog( )
				if dialog.GetResult( ) == False :
					self.ReLoadTimeSet( )

				self.mDataCache.LoadTime( )
				self.SetListControl( )
				ElisPropertyEnum( 'Time Installation', self.mCommander ).SetProp( 0 )
				self.mDataCache.Channel_SetCurrent( oriChannel.mNumber, oriChannel.mServiceType ) # Todo After : using ServiceType to different way
			else :
				self.OpenBusyDialog( )
				sumtime = self.mDate + '.' + self.mTime
				t = time.strptime( sumtime, '%d.%m.%Y.%H:%M' )
				ret = self.mCommander.Datetime_SetSystemUTCTime( int( time.mktime( t ) ) )
				self.mDataCache.LoadTime( )

			self.CloseBusyDialog( )
			if mode == TIME_AUTOMATIC and dialog.GetResult( ) == False :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Time Setting Fail' ) )
				dialog.doModal( )


	def LoadSavedTime( self ) :
		self.mSavedTimeChannel	= ElisPropertyInt( 'Time Setup Channel Number', self.mCommander ).GetProp( )
		self.mSavedTimeMode		= ElisPropertyEnum( 'Time Mode', self.mCommander ).GetProp( )
		self.mSavedLocalOffset	= ElisPropertyEnum( 'Local Time Offset', self.mCommander ).GetProp( )
		self.mSavedSummerTime	= ElisPropertyEnum( 'Summer Time', self.mCommander ).GetProp( )


	def SetTimeProperty( self ) :
		ElisPropertyEnum( 'Time Mode', self.mCommander ).SetPropIndex( self.GetSelectedIndex( E_SpinEx01 ) )
		ElisPropertyEnum( 'Summer Time', self.mCommander ).SetPropIndex( self.GetSelectedIndex( E_SpinEx03 ) )
		ElisPropertyEnum( 'Local Time Offset', self.mCommander ).SetPropIndex( self.GetSelectedIndex( E_SpinEx02) )
		localOffset = ElisPropertyEnum( 'Local Time Offset', self.mCommander ).GetProp( )
		self.mCommander.Datetime_SetLocalOffset( localOffset )


	def ReLoadTimeSet( self ) :
		ElisPropertyEnum( 'Time Mode', self.mCommander ).SetProp( self.mSavedTimeMode )
		ElisPropertyEnum( 'Summer Time', self.mCommander ).SetProp( self.mSavedSummerTime )
		ElisPropertyInt( 'Time Setup Channel Number', self.mCommander ).SetProp( self.mSavedTimeChannel )
		ElisPropertyEnum( 'Local Time Offset', self.mCommander ).SetProp( self.mSavedLocalOffset )
		self.getControl( E_SpinEx01 + 3 ).selectItem( ElisPropertyEnum( 'Time Mode', self.mCommander ).GetPropIndex( ) )
		self.getControl( E_SpinEx02 + 3 ).selectItem( ElisPropertyEnum( 'Summer Time', self.mCommander ).GetPropIndex( ) )
		self.getControl( E_SpinEx03 + 3 ).selectItem( ElisPropertyEnum( 'Local Time Offset', self.mCommander ).GetPropIndex( ) )
		self.mCommander.Datetime_SetLocalOffset( self.mSavedLocalOffset )

