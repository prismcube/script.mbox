from pvr.gui.WindowImport import *
import pvr.Platform

if pvr.Platform.GetPlatform( ).IsPrismCube( ) :
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

TIME_SEC_CHECK_NET_STATUS = 3


class Configure( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )


		self.mCtrlLeftGroup 	= None
		self.mGroupItems 		= []
		self.mLastFocused 		= E_SUBMENU_LIST_ID
		self.mPrevListItemID 	= -1

		self.mRunningNetwork	= False
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
		self.mEncryptType		= ENCRYPT_TYPE_WEP
		self.mPassWord 			= None

		self.mCheckNetworkTimer	= None
		self.mStateNetLink		= 'Busy'

		self.mEnableLocalThread = False
		self.mProgressThread	= None


	def onInit( self ) :
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

		self.mGroupItems 		= []
		for i in range( len( leftGroupItems ) ) :
			self.mGroupItems.append( xbmcgui.ListItem( leftGroupItems[i] ) )
	
		self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( False )

		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mCtrlLeftGroup = self.getControl( E_SUBMENU_LIST_ID )
		self.mCtrlLeftGroup.addItems( self.mGroupItems )

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( MR_LANG( 'Installation' ) )

		position = self.mCtrlLeftGroup.getSelectedPosition( )
		self.mCtrlLeftGroup.selectItem( position )
		if self.mPlatform.IsPrismCube( ) :
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
		self.StartCheckNetworkTimer( )


	def Close( self ) :
		self.StopCheckNetworkTimer( )
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

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.Close( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_MOVE_UP :
			if focusId == E_SUBMENU_LIST_ID and selectedId != self.mPrevListItemID :
				self.mPrevListItemID = selectedId
				self.mReLoadIp = True
				self.mVisibleParental = False
				#self.StopCheckNetworkTimer( )
				if self.mPlatform.IsPrismCube( ) :
					self.mUseNetworkType = GetCurrentNetworkType( )
				self.SetListControl( )
			elif focusId != E_SUBMENU_LIST_ID :
				self.ControlUp( )

		elif actionId == Action.ACTION_MOVE_DOWN :
			if focusId == E_SUBMENU_LIST_ID and selectedId != self.mPrevListItemID :
				self.mPrevListItemID = selectedId
				self.mReLoadIp = True
				self.mVisibleParental = False
				#self.StopCheckNetworkTimer( )
				if self.mPlatform.IsPrismCube( ) :
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
			if groupId == E_Input01 :
				menuLanguageList = WinMgr.GetInstance( ).GetLanguageList( )
				dialog = xbmcgui.Dialog( )
				ret = dialog.select( MR_LANG( 'Select Menu Language' ), menuLanguageList, False, StringToListIndex( menuLanguageList, self.GetControlLabel2String( E_Input01 ) ) )
				if ret >= 0 :
					if not self.mPlatform.IsPrismCube( ) :
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'No support %s' ) % self.mPlatform.GetName( ) )
						dialog.doModal( )
						return

					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Change Language' ), MR_LANG( 'Please be patience after pressing the OK button' ), MR_LANG( 'It will take some time to bring up display changes' ) )
					dialog.doModal( )
					self.mInitialized = False
					self.mLastFocused = -1
					WinMgr.GetInstance( ).SetCurrentLanguage( menuLanguageList[ ret ] )
			else :
				self.DisableControl( E_LANGUAGE )
				self.ControlSelect( )
			return

		elif selectedId == E_NETWORK_SETTING :
			if not self.mPlatform.IsPrismCube( ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Not support Win32' ) )
	 			dialog.doModal( )
	 			return

			if groupId == E_SpinEx05 :
				self.mUseNetworkType = self.GetSelectedIndex( E_SpinEx05 )
				self.SetListControl( )
				self.setDefaultControl( )

			elif self.mUseNetworkType == NETWORK_ETHERNET :
				self.EthernetSetting( groupId )
			elif self.mUseNetworkType == NETWORK_WIRELESS :
				self.WifiSetting( groupId )

		elif selectedId == E_TIME_SETTING :
			self.TimeSetting( groupId )
			return

		elif selectedId == E_PARENTAL and self.mVisibleParental == False and groupId == E_Input01 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( MR_LANG( 'Enter your PIN code' ), '', 4, True )
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
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Sorry, that\'s an incorrect PIN code' ) )					
		 			dialog.doModal( )
			return

		elif selectedId == E_PARENTAL and groupId == E_Input02 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( MR_LANG( 'Enter new PIN code' ), '', 4, True )			
 			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				newpin = dialog.GetString( )
				if newpin == '' or len( newpin ) != 4 :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'The PIN code must be 4-digit long' ) )
		 			dialog.doModal( )
					return
			else :
				return

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( MR_LANG( 'Confirm your PIN code' ), '', 4, True )
			dialog.doModal( )

 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
 				confirm = dialog.GetString( )
 				if confirm == '' :
 					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Sorry, that PIN code does not match' ) )
		 			dialog.doModal( )
 					return
				if int( newpin ) != int( confirm ) :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Sorry, that PIN code does not match' ) )
		 			dialog.doModal( )
					return
			else :
				return

			ElisPropertyInt( 'PinCode', self.mCommander ).SetProp( int( newpin ) )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Change PIN code' ), MR_LANG( 'Your PIN code has been changed successfully' ) )
 			dialog.doModal( )

 		elif selectedId == E_FACTORY_RESET and groupId == E_Input01 :
	 		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'WARNING' ), MR_LANG( 'DO YOU WANT TO RESET TO FACTORY SETTINGS?' ) )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.mDataCache.Player_AVBlank( True )
				self.mProgressThread = self.ShowProgress( MR_LANG( 'Now restoring...' ), 20 )
				self.mCommander.System_SetDefaultChannelList( )
				self.mCommander.System_FactoryReset( )
				self.mDataCache.LoadAllSatellite( )
				self.mDataCache.Channel_ReLoad( )
	 			from ElisProperty import ResetHash
				ResetHash( )
				self.mInitialized = False
				self.ResetAllControl( )
				self.getControl( E_SETTING_DESCRIPTION ).setLabel( '' )
				self.CloseProgress( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_FIRST_INSTALLATION, WinMgr.WIN_ID_MAINMENU )

		elif selectedId == E_FORMAT_HDD :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'WARNING' ), MR_LANG( 'DO YOU WANT TO FORMAT TO YOUR HDD DRIVE?' ) )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				if groupId == E_Input01 :
					LOG_TRACE( 'Format_Media_Archive Start' )
					self.mCommander.Format_Media_Archive( )
					LOG_TRACE( 'Format_Media_Archive Stop' )
				elif groupId == E_Input02 :
					LOG_TRACE( 'Format_Record_Archive Start' )
					self.mCommander.Format_Record_Archive( )
					LOG_TRACE( 'Format_Record_Archive Stop' )
				elif groupId == E_Input03 :
					LOG_TRACE( 'Make_Dedicated_HDD Start' )
					self.mCommander.Make_Dedicated_HDD( )
					LOG_TRACE( 'Make_Dedicated_HDD Stop' )

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
					#self.StopCheckNetworkTimer( )
				self.SetListControl( )


	def SetListControl( self ) :
		self.ResetAllControl( )
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( False )

		if selectedId == E_LANGUAGE :
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddInputControl( E_Input01, MR_LANG( 'Menu Language' ), WinMgr.GetInstance( ).GetCurrentLanguage( ), MR_LANG( 'Select the language you want the menu to be in' ) )
			self.AddEnumControl( E_SpinEx01, 'Audio Language', None, MR_LANG( 'Select the language that you wish to listen to' ) )
			self.AddEnumControl( E_SpinEx02, 'Subtitle Language', None, MR_LANG( 'Select the language for the subtitle to be in' ) )
			self.AddEnumControl( E_SpinEx03, 'Secondary Subtitle Language', None, MR_LANG( 'Select the language for the secondary subtitle to be in' ) )
			self.AddEnumControl( E_SpinEx04, 'Hearing Impaired', None, MR_LANG( 'Set the hearing impaired function' ) )

			visibleControlIds = [ E_Input01, E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx05, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
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
			self.AddInputControl( E_Input02, MR_LANG( ' - Change PIN Code' ), '', MR_LANG( 'Change your PIN code' ) )

			visibleControlIds = [ E_SpinEx01, E_Input01, E_SpinEx02, E_Input02 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			time.sleep( 0.2 )
			self.DisableControl( E_PARENTAL )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return

		elif selectedId == E_RECORDING_OPTION :
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddEnumControl( E_SpinEx01, 'Automatic Timeshift', None, MR_LANG( 'When set to \'On\', the STB automatically start a timeshift recording when a different channel is selected' ) )
			self.AddEnumControl( E_SpinEx02, 'Timeshift Buffer Size', None, MR_LANG( 'Select the preferred size of timeshift buffer' ) )
			self.AddEnumControl( E_SpinEx03, 'Default Rec Duration', None, MR_LANG( 'Select recording duration for a channel that has no EPG info' ) )
			self.AddEnumControl( E_SpinEx04, 'Pre-Rec Time', None, MR_LANG( 'Set the pre-recording time for a EPG channel' ) )
			self.AddEnumControl( E_SpinEx05, 'Post-Rec Time', None, MR_LANG( 'Set the post-recording time for a EPG channel' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return

		elif selectedId == E_AUDIO_SETTING :
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddEnumControl( E_SpinEx01, 'Audio Dolby', MR_LANG( 'Dolby Audio' ), MR_LANG( 'When set to \'On\', Dolby Digital audio will be selected automatically when broadcast' ) )
			self.AddEnumControl( E_SpinEx02, 'Audio HDMI', None, MR_LANG( 'Set the Audio HDMI format' ) )
			self.AddEnumControl( E_SpinEx03, 'Audio Delay', None, MR_LANG( 'Select a delay time for audio' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03 ]
			self.SetEnableControls( visibleControlIds, True )
			self.SetVisibleControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx04, E_SpinEx05,  E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
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

			hideControlIds = [ E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return

		elif selectedId == E_NETWORK_SETTING :
			self.AddUserEnumControl( E_SpinEx05, MR_LANG( 'Network Connection' ), USER_ENUM_LIST_NETWORK_TYPE, self.mUseNetworkType, MR_LANG( 'Select Ethernet or Wireless for your network connection' ) )
			self.AddInputControl( E_Input07, MR_LANG( 'Network Link' ), self.mStateNetLink, MR_LANG( 'Show network link status' ) )
			if self.mUseNetworkType == NETWORK_WIRELESS :
				self.AddInputControl( E_Input01, MR_LANG( 'Search AP' ), self.mCurrentSsid, MR_LANG( 'Search Access Points around your STB' ) )
				self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Hidden SSID' ), USER_ENUM_LIST_ON_OFF, self.mUseHiddenId, MR_LANG( 'Enable hidden Subsystem Identification (SSID)' ) )
				self.AddInputControl( E_Input02, MR_LANG( ' - Set Hidden SSID' ), self.mHiddenSsid, MR_LANG( 'Enter the hidden SSID you wish to use' ) )
				self.AddInputControl( E_Input03, MR_LANG( 'Set Encryption Key' ), StringToHidden( self.mPassWord ), MR_LANG( 'Enter the encryption key for wireless connection' ) )
				self.AddInputControl( E_Input04, MR_LANG( 'Apply' ), '', MR_LANG( 'Press the OK button to connect to the AP you have chosen' ) )

				visibleControlIds = [ E_SpinEx01, E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04, E_Input07 ]
				self.SetVisibleControls( visibleControlIds, True )
				self.SetEnableControls( visibleControlIds, True )

				hideControlIds = [ E_SpinEx02, E_SpinEx03, E_SpinEx04, E_Input05, E_Input06 ]
				self.SetVisibleControls( hideControlIds, False )
				
				self.InitControl( )
				time.sleep( 0.2 )
				self.DisableControl( E_WIFI )
				self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )

			else :
				if self.mReLoadIp == True :
					self.ReLoadEthernetIp( )
					self.mReLoadIp = False
					
				self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Assign IP Address' ), USER_ENUM_LIST_DHCP_STATIC, self.mTempNetworkType, MR_LANG( 'When set to \'DHCP\', your IP address will be automatically allocated by the DHCP server' ) )
				self.AddInputControl( E_Input01, MR_LANG( 'IP Address' ), self.mTempIpAddr, MR_LANG( 'Enter your IP address' ) )
				self.AddInputControl( E_Input02, MR_LANG( 'Subnet Mask' ), self.mTempSubNet, MR_LANG( 'Enter your subnet mask' ) )
				self.AddInputControl( E_Input03, MR_LANG( 'Gateway' ), self.mTempGateway, MR_LANG( 'Enter your gateway' ) )
				self.AddInputControl( E_Input04, MR_LANG( 'DNS' ), self.mTempDns, MR_LANG( 'Enter the DNS server address' ) )
				self.AddInputControl( E_Input05, MR_LANG( 'Apply') , '', MR_LANG( 'Press the OK button to save the IP address settings' ) )

				visibleControlIds = [ E_SpinEx01, E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
				self.SetVisibleControls( visibleControlIds, True )
				self.SetEnableControls( visibleControlIds, True )

				hideControlIds = [ E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
				self.SetVisibleControls( hideControlIds, False )
				
				self.InitControl( )
				time.sleep( 0.2 )
				self.DisableControl( E_ETHERNET )
				self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )

			self.SetEnableControl( E_Input07, False )
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

			self.AddEnumControl( E_SpinEx01, 'Time Mode', MR_LANG( 'Time & Date' ), MR_LANG( 'When set to \'Automatic\', the time and date will be obtained automatically from the channel that you select' ) )
			self.AddInputControl( E_Input01, MR_LANG( 'Channel' ), channelName, MR_LANG( 'Select a channel you want to set your time and date by' ) )
			self.mDate = TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_DD_MM_YYYY )
			self.AddInputControl( E_Input02, MR_LANG( 'Date' ), self.mDate, MR_LANG( 'Enter today\'s date' ) )
			self.mTime = TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_HH_MM )
			self.AddInputControl( E_Input03, MR_LANG( 'Time' ), self.mTime, MR_LANG( 'Set the local time' ) )
			self.AddEnumControl( E_SpinEx02, 'Local Time Offset', None, MR_LANG( 'Set the time zone that will be the basis for the date and time display' ) )
			self.AddEnumControl( E_SpinEx03, 'Summer Time', None, MR_LANG( 'When set to \'Automatic\', the system automatically change over to summer time' ) )
			self.AddInputControl( E_Input04, MR_LANG( 'Apply' ), '', MR_LANG( 'Press the OK button to save time settings' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input01, E_Input02, E_Input03, E_Input04 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx04, E_SpinEx05, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			time.sleep( 0.2 )
			self.DisableControl( E_TIME_SETTING )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )	
			return

		elif selectedId == E_FORMAT_HDD :
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddInputControl( E_Input01, MR_LANG( 'Media Archive Format' ), '', MR_LANG( 'Press the OK button to remove everything in the Media Archive' ) )
			self.AddInputControl( E_Input02, MR_LANG( 'Record Archive Format' ), '', MR_LANG( 'Press the OK button to remove everything in the Record Archive' ) )
			self.AddInputControl( E_Input03, MR_LANG( 'HDD Format' ), '', MR_LANG( 'Press the OK button to erase your hard drive' ) )

			visibleControlIds = [ E_Input01, E_Input02, E_Input03 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return

		elif selectedId == E_FACTORY_RESET :
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddInputControl( E_Input01, MR_LANG( 'Start Factory Reset'), '', MR_LANG( 'Go to First Installation after restoring system to the factory default' ) )

			visibleControlIds = [ E_Input01 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 , E_SpinEx05, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return

		elif selectedId == E_ETC :
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddEnumControl( E_SpinEx01, 'Deep Standby', None, MR_LANG( 'When set to \'On\', the system switches to deep standby mode when you press the \'Power\' button to help reduce the amount of electricity used' ) )
			self.AddEnumControl( E_SpinEx02, 'Power Save Mode', None, MR_LANG( 'Set the time for swithcing into standby mode when not being used' ) )
			self.AddEnumControl( E_SpinEx03, 'Fan Control', None, MR_LANG( 'Adjust the fan speed level for your system' ) )
			self.AddEnumControl( E_SpinEx04, 'Channel Banner Duration', MR_LANG( 'Channel Banner Time' ), MR_LANG( 'Set the time for the channel info to be displayed when zapping' ) )		#	Erase channel list yes/no
			self.AddEnumControl( E_SpinEx05, 'Playback Banner Duration', MR_LANG( 'Playback Banner Time' ), MR_LANG( 'Set the time for the playback info to be displayed on the screen' ) )	#	Erase custom menu yes/no

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return

		else :
			LOG_ERR( 'Can not find selected ID' )


	def DisableControl( self, aSelectedItem ) :
		if aSelectedItem == E_LANGUAGE :
			selectedIndex = self.GetSelectedIndex( E_SpinEx02 )
			visibleControlIds = [ E_SpinEx03, E_SpinEx04 ]
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

			if self.mEncryptType == ENCRYPT_OPEN :
				self.SetEnableControl( E_Input03, False )
			else :
				self.SetEnableControl( E_Input03, True )
				
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
		self.mProgressThread = self.ShowProgress( MR_LANG( 'Now connecting...' ), 15 )
		ret = self.mIpParser.SetEthernet( self.mTempNetworkType, self.mTempIpAddr, self.mTempSubNet, self.mTempGateway, self.mTempDns )
		SetCurrentNetworkType( NETWORK_ETHERNET )
		if ret == False :
			time.sleep( 1.5 )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Network setup has failed to complete' ) )
 			dialog.doModal( )
		else :
			if self.mTempNetworkType == NET_DHCP :
				self.mSavedNetworkType = self.mTempNetworkType
				self.LoadEthernetAddress( )
				SetIpAddressProperty( self.mSavedIpAddr, self.mSavedSubNet, self.mSavedGateway, self.mSavedDns )
				self.SetListControl( )
			else :
				self.mSavedIpAddr = self.mTempIpAddr
				self.mSavedSubNet = self.mTempSubNet
				self.mSavedGateway = self.mTempGateway
				self.mSavedDns = self.mTempDns
				self.mSavedNetworkType = self.mTempNetworkType
				SetIpAddressProperty( self.mSavedIpAddr, self.mSavedSubNet, self.mSavedGateway, self.mSavedDns )
		self.CloseProgress( )


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
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Invalid IP address' ) )					
					dialog.doModal( )
					return
			self.mRunningNetwork = True
			self.ConnectEthernet( )
			self.mRunningNetwork = False


	def WifiSetting( self, aControlId ) :
		apList = []
		if aControlId == E_SpinEx01 :
			self.mUseHiddenId = self.GetSelectedIndex( E_SpinEx01 )
			self.DisableControl( E_WIFI )

		elif aControlId == E_Input01 :
			self.mRunningNetwork = True
			dev = self.mWireless.GetWifidevice( )
			if dev == None :
				time.sleep( 1.5 )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Devices not found' ) )
				dialog.doModal( )
				self.mRunningNetwork = False
				return
			self.mProgressThread = self.ShowProgress( MR_LANG( 'Now search...' ), 15 )
			apList = self.mWireless.ScanWifiAP( dev )
			self.CloseProgress( )
			time.sleep( 1.5 )
			dialog = xbmcgui.Dialog( )
			if apList == None :
				ret = dialog.select( MR_LANG( 'Select AP' ), [ MR_LANG( 'No AP list' ) ] )
			else :
				apNameList = []
				for ap in apList :
					apNameList.append( ap[0] + MR_LANG( '    - quality : %s Encryption : %s' ) % ( ap[1], ap[2] ) )
				dialog = xbmcgui.Dialog( )
				ret = dialog.select( MR_LANG( 'Select AP' ), apNameList )
				if ret >= 0 :
					self.mCurrentSsid = apList[ret][0]
					self.mEncryptType = self.mWireless.ApInfoToEncrypt( apList[ret][2] )
					self.SetControlLabel2String( E_Input01, self.mCurrentSsid )
					self.DisableControl( E_WIFI )
			self.mRunningNetwork = False

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
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'AP or devices not found' ) )
				dialog.doModal( )
				return
			if self.mEncryptType == ENCRYPT_TYPE_WPA and ( len( self.mPassWord ) < 8 or len( self.mPassWord ) > 64 ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'The password must be between 8 and 64 characters' ) )
				dialog.doModal( )
				return
			if self.mEncryptType == ENCRYPT_TYPE_WEP and  len( self.mPassWord ) < 6 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'The password length is invalid' ) )
				dialog.doModal( )
				return
			self.mRunningNetwork = True
			self.mProgressThread = self.ShowProgress( MR_LANG( 'Now connecting...' ), 30 )
			ret1 = self.mWireless.WriteWpaSupplicant( self.mUseHiddenId, self.mHiddenSsid, self.mCurrentSsid, self.mEncryptType, self.mPassWord )
			ret2 = self.mWireless.ConnectWifi( dev )
			SetCurrentNetworkType( NETWORK_WIRELESS )
			addressIp, addressMask, addressGateway, addressNameServer = GetNetworkAddress( dev )
			SetIpAddressProperty( addressIp, addressMask, addressGateway, addressNameServer )
			self.CloseProgress( )
			if ret1 == False or ret2 == False :
				time.sleep( 1.5 )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'STB was unable to save the Wifi configuration' ) )
				dialog.doModal( )
			self.mRunningNetwork = False


	def LoadWifi( self ) :
		if self.mWireless.LoadWpaSupplicant( ) == True :
			self.mCurrentSsid		= self.mWireless.GetCurrentSsid( )
			self.mEncryptType		= self.mWireless.GetEncryptType( )
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


	def CloseProgress( self ) :
		self.mProgress.SetResult( True )
		self.mProgressThread.join( )


	def TimeSetting( self, aControlId ) :
		if aControlId == E_SpinEx01 :
			self.DisableControl( E_TIME_SETTING )

		elif aControlId == E_Input01 :
			dialog = xbmcgui.Dialog( )
			channelList = self.mDataCache.Channel_GetList( )
			channelNameList = []
			for channel in channelList :
				channelNameList.append( channel.mName )

			ret = dialog.select( MR_LANG( 'Select Channel' ), channelNameList, False, StringToListIndex( channelNameList, self.GetControlLabel2String( E_Input01 ) ) )

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
			mute = self.mCommander.Player_GetMute( )
			self.mCommander.Player_SetMute( True )

			self.LoadSavedTime( )
			oriChannel = self.mDataCache.Channel_GetCurrent( )
			self.SetTimeProperty( )
			mode = ElisPropertyEnum( 'Time Mode', self.mCommander ).GetProp( )

			if mode == TIME_AUTOMATIC :
				ElisPropertyInt( 'Time Setup Channel Number', self.mCommander ).SetProp( self.mSetupChannel.mNumber )
				self.mDataCache.Channel_SetCurrent( self.mSetupChannel.mNumber, self.mSetupChannel.mServiceType ) # Todo After : using ServiceType to different way
				ElisPropertyEnum( 'Time Installation', self.mCommander ).SetProp( 1 )

				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_FORCE_PROGRESS )
				dialog.SetDialogProperty( 14, MR_LANG( 'Setting Time...' ), ElisEventTimeReceived.getName( ) )
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
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Automatic time setup has failed because' ), MR_LANG( 'no time info was given by the channel you selected' ) )
				dialog.doModal( )

			if mute == False :
				self.mCommander.Player_SetMute( False )


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


	def CheckNetworkStatus( self ) :
		self.mStateNetLink = xbmc.getInfoLabel( 'System.internetstate' )
		LOG_TRACE( 'Network State = %s' % self.mStateNetLink )
		self.SetControlLabel2String( E_Input07, self.mStateNetLink )


	def StartCheckNetworkTimer( self ) :
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Start' )
		self.mEnableLocalThread = True
		self.mCheckNetworkTimer = self.AsyncCheckNetworkTimer( )
		
	

	def StopCheckNetworkTimer( self ) :
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Stop' )
		self.mEnableLocalThread = False				
		self.mCheckNetworkTimer.join( )


	@RunThread
	def AsyncCheckNetworkTimer( self ) :
		while self.mEnableLocalThread :
			LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Async' )	
			if self.mRunningNetwork == False and self.mCtrlLeftGroup.getSelectedPosition( ) == E_NETWORK_SETTING :
				self.CheckNetworkStatus( )
			time.sleep( TIME_SEC_CHECK_NET_STATUS )