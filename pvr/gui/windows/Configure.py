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
 
		leftGroupItems			= [ 'Language', 'Parental', 'Recording Option', 'Audio Setting', 'HDMI Setting', 'Network Setting', 'Time Setting', 'Format HDD', 'Factory Reset', 'Etc' ]
		descriptionList			= [ 'DESC Language', 'DESC Parental', 'DESC Recording Option', 'DESC Audio Setting', 'DESC HDMI Setting', 'DESC Network Setting', 'DESC Time Setting', 'DESC Format HDD', 'DESC Factory Reset', 'DESC Etc' ]
	
		self.mCtrlLeftGroup 	= None
		self.mGroupItems 		= []
		self.mLastFocused 		= E_SUBMENU_LIST_ID
		self.mPrevListItemID 	= 0

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
		self.apList				= []
		self.mHiddenSsid		= 'None'
		self.mUseHiddenId		= NOT_USE_HIDDEN_SSID
		self.mCurrentSsid		= 'None'
		self.mUseEncrypt		= NOT_USE_PASSWORD_ENCRYPT
		self.mEncriptType		= ENCRIPT_TYPE_WEP
		self.mPasswordType		= PASSWORD_TYPE_ASCII
		self.mPassWord 			= None
		self.mReLoadWifi		= False
		

		for i in range( len( leftGroupItems ) ) :
			self.mGroupItems.append( xbmcgui.ListItem( leftGroupItems[i], descriptionList[i] ) )


	def onInit( self ) :
		self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( False )
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mCtrlLeftGroup = self.getControl( E_SUBMENU_LIST_ID )
		self.mCtrlLeftGroup.addItems( self.mGroupItems )

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( 'Configure' )

		position = self.mCtrlLeftGroup.getSelectedPosition( )
		self.mCtrlLeftGroup.selectItem( position )
		self.mIpParser = IpParser( )
		self.mWireless = WirelessParser( )
		self.LoadIp( )
		self.LoadWifi( )
		SetCurrentNetworkType( self.mUseNetworkType )
		self.SetListControl( )
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
				self.mReLoadTime = True
				self.mVisibleParental = False
				self.SetListControl( )
			elif focusId != E_SUBMENU_LIST_ID :
				self.ControlUp( )
	
		elif actionId == Action.ACTION_MOVE_DOWN :
			if focusId == E_SUBMENU_LIST_ID and selectedId != self.mPrevListItemID :
				self.mPrevListItemID = selectedId
				self.mReLoadIp = True
				self.mReLoadTime = True
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
			self.DisableControl( E_LANGUAGE )
			self.ControlSelect( )
			return

		elif selectedId == E_NETWORK_SETTING :
			if groupId == E_SpinEx05 :
				self.mUseNetworkType = self.GetSelectedIndex( E_SpinEx05 )
				self.SetListControl( )
			elif groupId == E_Input06 :
				context = []
				context.append( ContextItem( 'Internal Test', PING_TEST_INTERNAL ) )
				context.append( ContextItem( 'External Test', PING_TEST_EXTERNAL ) )				
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
				dialog.SetProperty( context )
				dialog.doModal( )
				contextAction = dialog.GetSelectedAction( )
				if contextAction < 0 :
					return
				if contextAction == PING_TEST_INTERNAL :
					self.ShowProgress( 'Now Test...', 10 )
					if PingTestInternal( ) == True :
						state = 'Connected Default Rauter'
					else :
						state = 'Disconnected Default Rauter'
				else :
					addr = InputKeyboard( E_INPUT_KEYBOARD_TYPE_NO_HIDE, 'Address', '', 30 )
					self.ShowProgress( 'Now Test...', 10 )
					if PingTestExternal( addr ) == True :
						state = 'External ping test success'
					else :
						state = 'External ping test failed'
				try :		
					self.mProgress.SetResult( True )
				except Exception, e :
					LOG_ERR( 'Error exception[%s]' % e )
				time.sleep( 1.5 )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'Complete', 'Network State : %s' % state )
	 			dialog.doModal( )

			elif self.mUseNetworkType == NETWORK_ETHERNET :
				self.IpSetting( groupId )
			elif self.mUseNetworkType == NETWORK_WIRELESS :
				self.WifiSetting( groupId )

		elif selectedId == E_TIME_SETTING :
			self.TimeSetting( groupId )
			return

		elif selectedId == E_PARENTAL and self.mVisibleParental == False and groupId == E_Input01 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
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
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( 'ERROR', 'ERROR PIN Code' )
		 			dialog.doModal( )
			return

		elif selectedId == E_PARENTAL and groupId == E_Input02 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( 'New PIN Code', '', 4, True )
 			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				newpin = dialog.GetString( )
				if newpin == '' or len( newpin ) != 4 :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( 'ERROR', 'Input 4 digit' )
		 			dialog.doModal( )
					return
			else :
				return

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( 'Confirm PIN Code', '', 4, True )
 			dialog.doModal( )

 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
 				confirm = dialog.GetString( )
 				if confirm == '' :
 					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( 'ERROR', 'New PIN codes do not match' )
		 			dialog.doModal( )
 					return
				if int( newpin ) != int( confirm ) :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
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
 				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'ERROR', 'No selected reset' )
		 		dialog.doModal( )
		 		return
		 	else :
		 		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( 'Reset', 'Are you sure?' )
				dialog.doModal( )

				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					ret1 = True
					ret2 = True
					ret3 = True
					self.ShowProgress( 'Now Reset...', 15 )
				 	if resetChannel == 1 :
				 		ret = self.mCommander.System_SetDefaultChannelList( )
				 		self.mDataCache.LoadChannelList( )
				 		self.mDataCache.LoadAllSatellite( )

				 	if resetFavoriteAddons == 1 :
				 		pass

				 	if resetSystem == 1 :
				 		ret1 = self.mCommander.System_FactoryReset( )	
			 		try :
			 			if ret1 == True and ret2 == True and ret3 == True :
							self.mProgress.SetResult( True )
							time.sleep( 1.5 )
							dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
							dialog.SetDialogProperty( 'Confirm', 'Reset system Success' )
				 			dialog.doModal( )
						else :
							dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
							dialog.SetDialogProperty( 'ERROR', 'Reset system Fail' )
				 			dialog.doModal( )
							
					except Exception, e :
						LOG_ERR( 'Error exception[%s]' % e )

					if resetSystem == 1 :	
				 		ElisPropertyEnum( 'Reset Configure Setting', self.mCommander ).ResetHash( )
				 		self.SetListControl( )

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
					self.mReLoadWifi = True
					self.mVisibleParental = False
				self.SetListControl( )


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

			hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06 ]
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

			hideControlIds = [ E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input03, E_Input04, E_Input05, E_Input06 ]
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

			hideControlIds = [ E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06 ]
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

			hideControlIds = [ E_SpinEx04, E_SpinEx05,  E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return


		elif selectedId == E_HDMI_SETTING :
			self.AddEnumControl( E_SpinEx01, 'HDMI Format' )
			self.AddEnumControl( E_SpinEx02, 'Show 4:3', 'TV Screen Format' )
			self.AddEnumControl( E_SpinEx03, 'HDMI Color Space' )
			self.AddEnumControl( E_SpinEx04, 'TV System' )
			
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return


		elif selectedId == E_NETWORK_SETTING :
			self.AddUserEnumControl( E_SpinEx05, 'Select Network', USER_ENUM_LIST_NETWORK_TYPE, self.mUseNetworkType )
			self.AddInputControl( E_Input06, ' - Network Test', '' )
			if self.mUseNetworkType == NETWORK_WIRELESS :
				self.AddInputControl( E_Input01, 'Search and Select AP', self.mCurrentSsid )
				self.AddUserEnumControl( E_SpinEx01, 'Use hidden ssid', USER_ENUM_LIST_ON_OFF, self.mUseHiddenId )
				self.AddInputControl( E_Input02, ' - hidden ssid', self.mHiddenSsid )
				self.AddUserEnumControl( E_SpinEx02, 'Use Encrypt', USER_ENUM_LIST_ON_OFF, self.mUseEncrypt )
				self.AddUserEnumControl( E_SpinEx03, ' - Encrypt Type', USER_ENUM_LIST_ENCRIPT_TYPE, self.mEncriptType )
				self.AddUserEnumControl( E_SpinEx04, 'Password Type', USER_ENUM_LIST_PASSWORD_TYPE, self.mPasswordType )
				self.AddInputControl( E_Input03, 'Password', StringToHidden( self.mPassWord ) )
				self.AddInputControl( E_Input04, 'Connect Current Ap', '' )

				visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04, E_Input06 ]
				self.SetVisibleControls( visibleControlIds, True )
				self.SetEnableControls( visibleControlIds, True )

				hideControlIds = [ E_Input05 ]
				self.SetVisibleControls( hideControlIds, False )
				
				self.InitControl( )
				self.DisableControl( E_WIFI )
				self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )

			else :
				if self.mReLoadIp == True :
					self.ReLoadIp( )
					self.mReLoadIp = False
					
				self.AddUserEnumControl( E_SpinEx01, 'Network Type', USER_ENUM_LIST_DHCP_STATIC, self.mTempNetworkType )
				self.AddInputControl( E_Input01, 'IP Address', self.mTempIpAddr )
				self.AddInputControl( E_Input02, 'Subnet Mask', self.mTempSubNet )
				self.AddInputControl( E_Input03, 'Gateway', self.mTempGateway )
				self.AddInputControl( E_Input04, 'DNS', self.mTempDns )
				self.AddInputControl( E_Input05, 'Apply', '' )

				visibleControlIds = [ E_SpinEx01, E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06 ]
				self.SetVisibleControls( visibleControlIds, True )
				self.SetEnableControls( visibleControlIds, True )

				hideControlIds = [ E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
				self.SetVisibleControls( hideControlIds, False )
				
				self.InitControl( )
				self.DisableControl( E_ETHERNET )
				self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )


		elif selectedId == E_TIME_SETTING :
			setupChannelNumber = ElisPropertyInt( 'Time Setup Channel Number', self.mCommander ).GetProp( )
			self.mSetupChannel = self.mDataCache.Channel_GetSearch( setupChannelNumber )
			self.mHasChannel = True
			if self.mSetupChannel :
				channelName = self.mSetupChannel.mName
			else :
				channellist = self.mDataCache.Channel_GetList( )
				if channellist :
					self.mSetupChannel = channellist[0]
					channelName = self.mSetupChannel.mName
				else :
					self.mHasChannel = False
					channelName = 'None'
					ElisPropertyEnum( 'Time Mode', self.mCommander ).SetProp( TIME_MANUAL )

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

			hideControlIds = [ E_SpinEx04, E_SpinEx05, E_Input05, E_Input06 ]
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

			hideControlIds = [ E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06 ]
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

			hideControlIds = [ E_SpinEx04 , E_SpinEx05, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06 ]
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

			hideControlIds = [ E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06 ]
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


	def LoadIp( self ) :
		self.LoadNetworkType( )
		self.LoadNetworkAddress( )


	def LoadNetworkType( self ) :
		ret = self.mIpParser.LoadNetworkType( )
		if ret == True :
			self.mSavedNetworkType	= self.mIpParser.GetNetworkType( )
			self.mTempNetworkType	= self.mIpParser.GetNetworkType( )
		else :
			self.mSavedNetworkType	= NET_DHCP
			self.mTempNetworkType	= NET_DHCP
			LOG_ERR( 'Can not read network type(dhcp/static)' )


	def LoadNetworkAddress( self ) :		
		ret = self.mIpParser.LoadNetworkAddress( )

		if ret == True :
			self.mSavedIpAddr, self.mSavedSubNet, self.mSavedGateway, self.mSavedDns = self.mIpParser.GetNetworkAddress( )
			self.mTempIpAddr,  self.mTempSubNet,  self.mTempGateway,  self.mTempDns  = self.mIpParser.GetNetworkAddress( )
		else :
			self.mSavedIpAddr	= 'None'
			self.mTempIpAddr	= 'None'
			self.mSavedSubNet	= 'None'
			self.mTempSubNet	= 'None'
			self.mSavedGateway	= 'None'
			self.mTempGateway	= 'None'
			self.mSavedDns		= 'None'
			self.mTempDns		= 'None'
			LOG_ERR( 'Can not read ip address' )


	def SaveIp( self ) :
		SetCurrentNetworkType( self.mUseNetworkType )
		self.ShowProgress( 'Setting Network...', 15 )
		ret = self.mIpParser.SetNetwork( self.mTempNetworkType, self.mTempIpAddr, self.mTempSubNet, self.mTempGateway, self.mTempDns )
		if ret == False :
			try :
				self.mProgress.SetResult( True )
				time.sleep( 1.5 )

			except Exception, e :
				LOG_ERR( 'Error exception[%s]' % e )

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( 'Error', 'Network Set Fail' )
 			dialog.doModal( )
		else :
			if self.mTempNetworkType == NET_DHCP :
				self.mSavedNetworkType = self.mTempNetworkType
				self.LoadNetworkAddress( )
				try :
					self.mProgress.SetResult( True )
					time.sleep( 1.5 )

				except Exception, e :
					LOG_ERR( 'Error exception[%s]' % e )
				self.SetListControl( )
			else :
				self.mSavedIpAddr = self.mTempIpAddr
				self.mSavedSubNet = self.mTempSubNet
				self.mSavedGateway = self.mTempGateway
				self.mSavedDns = self.mTempDns
				self.mSavedNetworkType = self.mTempNetworkType
	 			try :
					self.mProgress.SetResult( True )
					time.sleep( 1.5 )

				except Exception, e :
					LOG_ERR( 'Error exception[%s]' % e )


	def ReLoadIp( self ) :
		self.mTempIpAddr			= self.mSavedIpAddr
		self.mTempSubNet			= self.mSavedSubNet
		self.mTempGateway			= self.mSavedGateway
		self.mTempDns				= self.mSavedDns
		self.mTempNetworkType		= self.mSavedNetworkType


	def IpSetting( self, aControlId ) :
		if aControlId == E_SpinEx01 :
			if self.mTempNetworkType == NET_DHCP :
				self.mTempNetworkType = NET_STATIC
			else :
				self.mTempNetworkType = NET_DHCP
			self.SetListControl( )
			
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
			self.SaveIp( )


	def ShowIpInputDialog( self, aIpAddr ) :
		if aIpAddr == 'None' :
			aIpAddr = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_IP, 'Input Ip', '0.0.0.0' )
		else :
			aIpAddr = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_IP, 'Input Ip', aIpAddr )

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
			self.LoadSavedTime( )
			oriChannel = self.mDataCache.Channel_GetCurrent( )
		 	self.SetTimeProperty( )	
 			
			if ElisPropertyEnum( 'Time Mode', self.mCommander ).GetProp( ) == TIME_AUTOMATIC :
				ElisPropertyInt( 'Time Setup Channel Number', self.mCommander ).SetProp( self.mSetupChannel.mNumber )
				self.mDataCache.Channel_SetCurrent( self.mSetupChannel.mNumber, self.mSetupChannel.mServiceType ) # Todo After : using ServiceType to different way
				ElisPropertyEnum( 'Time Installation', self.mCommander ).SetProp( 1 )

				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_FORCE_PROGRESS )
				dialog.SetDialogProperty( 10, 'Setting Time...', ElisEventTimeReceived.getName( ) )
				dialog.doModal( )

				if dialog.GetResult( ) == False :
					self.ReLoadTimeSet( )

				self.mDataCache.LoadTime( )
				self.SetListControl( )
				ElisPropertyEnum( 'Time Installation', self.mCommander ).SetProp( 0 )
				self.mDataCache.Channel_SetCurrent( oriChannel.mNumber, oriChannel.mServiceType ) # Todo After : using ServiceType to different way
			else :
				sumtime = self.mDate + '.' + self.mTime
				t = time.strptime( sumtime, '%d.%m.%Y.%H:%M' )
				ret = self.mCommander.Datetime_SetSystemUTCTime( int( time.mktime( t ) ) )
				self.mDataCache.LoadTime( )


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


	def WifiSetting( self, aControlId ) :
		if aControlId == E_SpinEx01 or aControlId == E_SpinEx02 :
			self.mUseHiddenId = self.GetSelectedIndex( E_SpinEx01 )
			self.mUseEncrypt = self.GetSelectedIndex( E_SpinEx02 )
			self.DisableControl( E_WIFI )

		elif aControlId == E_SpinEx03 or aControlId == E_SpinEx04 :
			self.mEncriptType	= self.GetSelectedIndex( E_SpinEx03 )
			self.mPasswordType	= self.GetSelectedIndex( E_SpinEx04 )

		elif aControlId == E_Input01 :
			self.ShowProgress( 'Scan Ap...', 30 )
			dev = self.mWireless.getWlandevice( )
			if dev == None :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'Error', 'Can not found device' )
	 			dialog.doModal( )
	 			return

			self.apList = self.mWireless.ScanAp( dev )
			try :
				self.mProgress.SetResult( True )
			except Exception, e :
				LOG_ERR( 'Error exception[%s]' % e )
			time.sleep( 1.5 )
			dialog = xbmcgui.Dialog( )
			if self.apList == None :
				ret = dialog.select( 'Select Ap', [ 'No Ap list' ] )
			else :
				apNameList = []
				for ap in self.apList :
					apNameList.append( ap[0] + ' -   quality:%s Encrypt:%s' % ( ap[1], ap[2] ) )
				dialog = xbmcgui.Dialog( )
	 			ret = dialog.select( 'Select Ap', apNameList )
				if ret >= 0 :
	 				self.mCurrentSsid = self.apList[ret][0]
	 				self.SetControlLabel2String( E_Input01, self.mCurrentSsid )

	 	elif aControlId == E_Input02 :
			self.mHiddenSsid = InputKeyboard( E_INPUT_KEYBOARD_TYPE_NO_HIDE, 'SSID', self.mHiddenSsid, 30 )
			self.SetControlLabel2String( E_Input02, self.mHiddenSsid )

	 	elif aControlId == E_Input03 :
	 		self.mPassWord = InputKeyboard( E_INPUT_KEYBOARD_TYPE_HIDE, 'Password', self.mPassWord, 30 )
			self.SetControlLabel2String( E_Input03, StringToHidden( self.mPassWord ) )

	 	elif aControlId == E_Input04 :
			SetCurrentNetworkType( self.mUseNetworkType )
			dev = self.mWireless.getWlandevice( )
	 		if self.apList == None or dev == None :
	 			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'Error', 'Can not found Ap or device' )
	 			dialog.doModal( )
	 			return

	 		self.ShowProgress( 'Setting Wifi...', 20 )
	 		ret1 = self.mWireless.WriteWpaSupplicant( self.mUseHiddenId, self.mHiddenSsid, self.mCurrentSsid, self.mUseEncrypt, self.mEncriptType, self.mPasswordType, self.mPassWord )
			ret2 = self.mWireless.ConnectWifi( dev )
			try :
				self.mProgress.SetResult( True )
				time.sleep( 1.5 )
			except Exception, e :
				LOG_ERR( 'Error exception[%s]' % e )
			if ret1 == False :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'Error', 'WriteWpaSupplicant write fail' )
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
			
