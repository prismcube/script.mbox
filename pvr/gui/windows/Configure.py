from pvr.gui.WindowImport import *
import pvr.Platform
if E_USE_OLD_NETWORK :
	import pvr.IpParser as NetMgr
else :
	import pvr.NetworkMgr as NetMgr

E_CONFIGURE_BASE_ID				=  WinMgr.WIN_ID_CONFIGURE * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 
E_CONFIGURE_SETUPMENU_GROUP_ID	=  E_CONFIGURE_BASE_ID + 9010
E_CONFIGURE_SUBMENU_LIST_ID		=  E_CONFIGURE_BASE_ID + 9000
E_CONFIGURE_SETTING_DESCRIPTION	=  E_CONFIGURE_BASE_ID + 1003


E_CONFIGURE_DEFAULT_FOCUS_ID	=  E_CONFIGURE_SUBMENU_LIST_ID


E_LANGUAGE				= 0
E_PARENTAL				= 1
E_RECORDING_OPTION		= 2
E_AUDIO_SETTING			= 3
E_HDMI_SETTING			= 4
E_NETWORK_SETTING		= 5
E_TIME_SETTING			= 6
E_EPG					= 7
E_FORMAT_HDD			= 8
E_FACTORY_RESET			= 9
E_ETC					= 10

E_ETHERNET				= 100
E_WIFI					= 101


TIME_SEC_CHECK_NET_STATUS = 0.05


class Configure( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mCtrlLeftGroup 		= None
		self.mGroupItems 			= []
		self.mLastFocused 			= E_CONFIGURE_SUBMENU_LIST_ID
		self.mPrevListItemID 		= -1

		self.mUseNetworkType		= NETWORK_ETHERNET

		self.mEthernetConnectMethod	= NET_DHCP
		self.mEthernetIpAddress		= 'None'
		self.mEthernetNetmask		= 'None'
		self.mEthernetGateway		= 'None'
		self.mEthernetNamesServer	= 'None'

		self.mReLoadEthernetInformation	= False
		self.mVisibleParental		= False

		self.mDate					= 0
		self.mTime					= 0
		self.mSetupChannel			= None
		self.mHasChannel			= False

		self.mSavedTimeMode			= TIME_MANUAL
		self.mSavedTimeChannel		= 0
		self.mSavedLocalOffset		= 0
		self.mSavedSummerTime		= 0

		#self.mIpParser				= None
		self.mProgress				= None

		self.mWireless				= None
		self.mHiddenSsid			= 'None'
		self.mUseHiddenId			= NOT_USE_HIDDEN_SSID
		self.mCurrentSsid			= 'None'
		self.mEncryptType			= ENCRYPT_TYPE_WEP
		self.mPassWord 				= ''
		self.mWifiAddress			= 'None'
		self.mWifiSubnet			= 'None'
		self.mWifiGateway			= 'None'
		self.mWifiDns				= 'None'
		self.mUseStatic				= False

		self.mCheckNetworkTimer		= None
		self.mStateNetLink			= 'Busy'

		self.mEnableLocalThread	 	= False
		self.mProgressThread		= None

		self.mVideoOutput			= E_VIDEO_HDMI
		self.mAnalogAscpect			= E_16_9
		self.mRssfeed				= int( GetSetting( 'RSS_FEED' ) )

		self.mUseUsbBackup			= False
		self.mAsyncVideoSetThread	= None
		self.mBusyVideoSetting		= False

		self.mEpgGrabinngTime		= 10800
		self.mEpgStartChannel		= 1
		self.mEpgEndChannel			= 1
		self.mEpgFavGroup			= 0


	def onInit( self ) :
		self.OpenBusyDialog( )
		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( False )

		leftGroupItems			= [
		MR_LANG( 'Language' ),
		MR_LANG( 'Parental Control' ),
		MR_LANG( 'Recording Option' ),
		MR_LANG( 'Audio Setting' ),
		MR_LANG( 'Video Setting' ),
		MR_LANG( 'Network Setting' ),
		MR_LANG( 'Time Setting' ),
		MR_LANG( 'EPG' ),
		MR_LANG( 'HDD Format' ),
		MR_LANG( 'Factory Reset' ),
		MR_LANG( 'Miscellaneous' ) ]

		self.mGroupItems = []
		for i in range( len( leftGroupItems ) ) :
			self.mGroupItems.append( xbmcgui.ListItem( leftGroupItems[i] ) )
		
		self.mDescriptionList	= [
		MR_LANG( 'Change your PRISMCUBE RUBY language preferences' ),
		MR_LANG( 'Set limits on your kids\' digital satellite receiver use' ),
		MR_LANG( 'Adjust general recording settings' ),
		MR_LANG( 'Set the system\'s digital audio output settings' ),
		MR_LANG( 'Setup the output settings for TVs that support HDMI cable' ),
		MR_LANG( 'Configure internet connection settings' ),
		MR_LANG( 'Adjust settings related to the system\'s date and time' ),
		MR_LANG( 'Setup the EPG grabbing' ),
		MR_LANG( 'Delete everything off your hard drive' ),
		MR_LANG( 'Restore your system to factory settings' ),
		MR_LANG( 'Change additional settings for PRISMCUBE RUBY' ) ]
	
		self.setFocusId( E_CONFIGURE_DEFAULT_FOCUS_ID )
		self.SetActivate( True )
		self.SetSingleWindowPosition( E_CONFIGURE_BASE_ID )
		self.SetFrontdisplayMessage( 'Configuration' )
		self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'Installation' ), MR_LANG( 'Configuration' ) ) )

		self.mCtrlLeftGroup = self.getControl( E_CONFIGURE_SUBMENU_LIST_ID )
		self.mCtrlLeftGroup.addItems( self.mGroupItems )
		
		if self.mPrevListItemID != -1 :
			self.mCtrlLeftGroup.selectItem( self.mPrevListItemID )

		self.mVisibleParental = False
		self.mReLoadEthernetInformation = True

		self.mUseNetworkType = NetMgr.GetInstance( ).GetCurrentServiceType( )
		NetMgr.GetInstance( ).SetIsConfigureWindow( True )

		self.SetListControl( )
		self.StartCheckNetworkTimer( )
		self.mInitialized = True
		self.CloseBusyDialog( )
		

	def Close( self ) :
		if self.mAsyncVideoSetThread :
			self.mAsyncVideoSetThread.cancel( )
			self.mAsyncVideoSetThread = None
		self.OpenBusyDialog( )
		self.StopCheckNetworkTimer( )
		self.mInitialized = False
		self.ResetAllControl( )
		NetMgr.GetInstance( ).SetIsConfigureWindow( False )
		self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( '' )
		self.CloseBusyDialog( )
		WinMgr.GetInstance( ).CloseWindow( )


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.Close( )

		elif actionId == Action.ACTION_MOVE_UP :
			if focusId == E_CONFIGURE_SUBMENU_LIST_ID and selectedId != self.mPrevListItemID :
				self.mPrevListItemID = selectedId
				self.mReLoadEthernetInformation = True
				self.mVisibleParental = False
				self.SetListControl( )
			if focusId != E_CONFIGURE_SUBMENU_LIST_ID :
				self.ControlUp( )

		elif actionId == Action.ACTION_MOVE_DOWN :
			if focusId == E_CONFIGURE_SUBMENU_LIST_ID and selectedId != self.mPrevListItemID :
				self.mPrevListItemID = selectedId
				self.mReLoadEthernetInformation = True
				self.mVisibleParental = False
				self.SetListControl( )
			if focusId != E_CONFIGURE_SUBMENU_LIST_ID :
				self.ControlDown( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			if focusId != E_CONFIGURE_SUBMENU_LIST_ID and ( ( focusId % 10 ) == 1 ) :
				self.setFocusId( E_CONFIGURE_SUBMENU_LIST_ID )
			else :
				self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			if focusId == E_CONFIGURE_SUBMENU_LIST_ID :
				self.SetDefaultControl( )
			elif focusId != E_CONFIGURE_SUBMENU_LIST_ID and ( focusId % 10 ) == 1 :
				self.ControlRight( )


	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return

		groupId = self.GetGroupId( aControlId )
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )

		if selectedId == E_LANGUAGE :
			if groupId == E_Input01 :
				menuLanguageList = WinMgr.GetInstance( ).GetLanguageList( )
				dialog = xbmcgui.Dialog( )
				currentindex = StringToListIndex( menuLanguageList, self.GetControlLabel2String( E_Input01 ) )
				ret = dialog.select( MR_LANG( 'Select Menu Language' ), menuLanguageList, False, currentindex )
				if ret >= 0 and currentindex != ret :
					if not self.mPlatform.IsPrismCube( ) :
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No support %s' ) % self.mPlatform.GetName( ) )
						dialog.doModal( )
						return

					isDownload = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_SYSTEM_UPDATE ).GetStatusFromFirmware( )
					if isDownload :
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( MR_LANG( 'Change Language' ), MR_LANG( 'Try again after completing firmware update' ) )
						dialog.doModal( )
						return

					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
					dialog.SetDialogProperty( MR_LANG( 'Change Language' ), MR_LANG( 'Do you want to continue?' ), MR_LANG( 'please wait after pressing OK button' ) )
					dialog.doModal( )

					if dialog.IsOK( ) == E_DIALOG_STATE_YES :
						self.mInitialized = False
						self.StopCheckNetworkTimer( )
						import time
						time.sleep( 0.5 )
						XBMC_SetCurrentLanguage( menuLanguageList[ ret ] )

			elif groupId == E_SpinEx02 :
				self.DisableControl( E_LANGUAGE )
				self.ControlSelect( )
			else :
				self.ControlSelect( )

		elif selectedId == E_HDMI_SETTING :
			if groupId == E_SpinEx01 :
				self.mVideoOutput = self.GetSelectedIndex( E_SpinEx01 )
				self.SetListControl( )
				return

			elif self.mVideoOutput == E_VIDEO_ANALOG and groupId == E_SpinEx02 :
				self.ControlSelect( )
				time.sleep( 0.02 )
				self.mAnalogAscpect = self.GetSelectedIndex( E_SpinEx02 )
				self.SetListControl( ) 

			elif self.mVideoOutput == E_VIDEO_HDMI and groupId == E_SpinEx02 :
				if self.mBusyVideoSetting :
					return
				if self.mAsyncVideoSetThread :
					self.mAsyncVideoSetThread.cancel( )
					self.mAsyncVideoSetThread = None

				self.mAsyncVideoSetThread = threading.Timer( 0.5, self.AsyncVideoSetting )
				self.mAsyncVideoSetThread.start( )

			else :
				self.ControlSelect( )

		elif selectedId == E_NETWORK_SETTING :
			if not self.mPlatform.IsPrismCube( ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Not support Win32' ) )
	 			dialog.doModal( )
	 			return

			if groupId == E_SpinEx05 :
				self.mUseNetworkType = self.GetSelectedIndex( E_SpinEx05 )
				self.SetListControl( )
				self.SetDefaultControl( )

			elif self.mUseNetworkType == NETWORK_ETHERNET :
				self.EthernetSetting( groupId )
			elif self.mUseNetworkType == NETWORK_WIRELESS :
				self.WifiSetting( groupId )

		elif selectedId == E_TIME_SETTING :
			self.TimeSetting( groupId )

		elif selectedId == E_EPG :
			if groupId == E_SpinEx01 or groupId == E_SpinEx02 :
				self.ControlSelect( )

			elif groupId == E_SpinEx03 :
				self.ControlSelect( )
				self.DisableControl( E_EPG )

			elif groupId == E_Input01 :
				time = '%02d:%02d' % ( ( self.mEpgGrabinngTime / 3600 ), ( self.mEpgGrabinngTime % 3600 / 60 ) )
				time = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_TIME, MR_LANG( 'Enter your EPG grabbing time' ), time )
				tmptime = time.split( ':' )
				intTime = int( tmptime[0] ) * 3600 + int( tmptime[1] ) * 60
				if self.mEpgGrabinngTime != intTime :
					self.mEpgGrabinngTime = intTime
					ElisPropertyInt( 'EPG Grabbing Time', self.mCommander ).SetProp( self.mEpgGrabinngTime )
					self.SetControlLabel2String( E_Input01, '%02d:%02d' % ( ( self.mEpgGrabinngTime / 3600 ), ( self.mEpgGrabinngTime % 3600 / 60 ) ) )

			elif groupId == E_Input02 :
				self.SetStartEndChannel( )

			elif groupId == E_Input03 :
				tmp = self.ShowFavoriteGroup( )
				if tmp != -1 :
					self.mEpgFavGroup = tmp
					ElisPropertyInt( 'Auto EPG Favorite Group', self.mCommander ).SetProp( self.mEpgFavGroup )
					self.SetListControl( )

		elif selectedId == E_PARENTAL and self.mVisibleParental == False and groupId == E_Input01 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( MR_LANG( 'Enter your PIN code' ), '', 4, True )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				tempval = dialog.GetString( )
				if len( tempval ) != 4 :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'The PIN code must be 4-digit long' ) )
		 			dialog.doModal( )
		 			return
				if int( tempval ) == ElisPropertyInt( 'PinCode', self.mCommander ).GetProp( ) :
					self.mVisibleParental = True
					self.DisableControl( E_PARENTAL )
				else :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Sorry, that\'s an incorrect PIN code' ) )					
		 			dialog.doModal( )


		elif selectedId == E_PARENTAL and groupId == E_SpinEx02 :
			self.ControlSelect( )
			propertyAge = ElisPropertyEnum( 'Age Limit', self.mCommander ).GetProp( )
			self.mDataCache.SetPropertyAge( propertyAge )

			channelList = self.mDataCache.Channel_GetList( )
			iChannel = self.mDataCache.Channel_GetCurrent( )
			if channelList and len( channelList ) > 0 and ( iChannel and ( not iChannel.mLocked ) ) :
				self.mDataCache.SetSearchNewChannel( True )
				#LOG_TRACE('-------------------re setting ageLimit check')

		elif selectedId == E_PARENTAL and groupId == E_Input02 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( MR_LANG( 'Enter new PIN code' ), '', 4, True )			
 			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				newpin = dialog.GetString( )
				if len( newpin ) != 4 :
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
 				if len( confirm ) != 4 :
 					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'The PIN code must be 4-digit long' ) )
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
			dialog.SetDialogProperty( MR_LANG( 'Performing a factory reset?' ), MR_LANG( 'All settings will be restored to factory default' ) )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.mCommander.Player_SetMute( True )
				self.mProgressThread = self.ShowProgress( MR_LANG( 'Now restoring...' ), 30 )
				self.mCommander.System_SetDefaultChannelList( )
				self.mCommander.System_FactoryReset( )
				self.mDataCache.LoadAllSatellite( )
				self.mDataCache.LoadConfiguredSatellite( )
				self.mDataCache.LoadAllTransponder( )
				self.mDataCache.LoadChannelList( )
				iZapping = self.mDataCache.Zappingmode_GetCurrent( )
				if iZapping and iZapping.mError == 0 :
					self.mDataCache.Channel_GetAllChannels( iZapping.mServiceType, False )
				self.mDataCache.SetChannelReloadStatus( True )
	 			from ElisProperty import ResetHash
				ResetHash( )
				self.mDataCache.SetDefaultByFactoryReset( )
				globalEvent = pvr.GlobalEvent.GetInstance( )
				globalEvent.SendLocalOffsetToXBMC( )
				self.mInitialized = False
				self.ResetAllControl( )
				self.StopCheckNetworkTimer( )
				self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( '' )
				self.SetDefaultVolume( )
				self.CloseProgress( )
				self.mDataCache.Channel_TuneDefault( False )
				NetMgr.GetInstance( ).SetIsConfigureWindow( False )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_FIRST_INSTALLATION, WinMgr.WIN_ID_MAINMENU )

		elif selectedId == E_FORMAT_HDD :
			if CheckHdd( ) :
				if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Try again after stopping your playback' ) )
					dialog.doModal( )
				elif groupId == E_Input01 :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
					dialog.SetDialogProperty( MR_LANG( 'WARNING' ), MR_LANG( 'Formatting media partition%s cannot be undone!' )% NEW_LINE )
					dialog.doModal( )
					if dialog.IsOK( ) == E_DIALOG_STATE_YES :
						self.mProgressThread = self.ShowProgress( MR_LANG( 'Formatting HDD...' ), 120 )
						self.mCommander.Format_Media_Archive( )
						self.CloseProgress( )
				elif groupId == E_Input02 :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
					dialog.SetDialogProperty( MR_LANG( 'WARNING' ), MR_LANG( 'Formatting recording partition%s cannot be undone!' )% NEW_LINE )
					dialog.doModal( )
					if dialog.IsOK( ) == E_DIALOG_STATE_YES :
						self.mProgressThread = self.ShowProgress( MR_LANG( 'Formatting HDD...' ), 60 )
						self.mCommander.Format_Record_Archive( )
						self.CloseProgress( )
				elif groupId == E_Input03 :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
					dialog.SetDialogProperty( MR_LANG( 'Format hard disk drive?' ), MR_LANG( 'Everything on your hard drive will be erased' ) )
					dialog.doModal( )
					if dialog.IsOK( ) == E_DIALOG_STATE_YES :
						self.DedicatedFormat( )
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Cannot find a hard drive' ) )
	 			dialog.doModal( )

	 	elif selectedId == E_ETC :
	 		self.ETCSetting( groupId )

		else :
			self.ControlSelect( )


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
		if self.mInitialized == False :
			return

		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		if aControlId == E_CONFIGURE_SUBMENU_LIST_ID :
			self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			if self.mPrevListItemID != selectedId :
				self.mPrevListItemID = selectedId
				self.mReLoadEthernetInformation = True
				self.mVisibleParental = False
				self.SetListControl( )

		else :
			self.ShowDescription( aControlId, E_CONFIGURE_SETTING_DESCRIPTION )


	def AsyncVideoSetting( self ) :
		self.mBusyVideoSetting = True
		restoreValue = ElisPropertyEnum( 'HDMI Format', self.mCommander ).GetProp( )
		self.ControlSelect( )
		if restoreValue != ElisPropertyEnum( 'HDMI Format', self.mCommander ).GetProp( ) :
			self.VideoRestore( restoreValue )
		else :
			self.mBusyVideoSetting = False


	def VideoRestore( self, aRestoreValue ) :
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_VIDEO_RESTORE )
		dialog.doModal( )

		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			hdmiFormat = ElisPropertyEnum( 'HDMI Format', self.mCommander ).GetPropString( )
			if hdmiFormat == 'Automatic' :
				return
			iconIndex = ElisEnum.E_ICON_1080i
			if hdmiFormat == '1080p' :
				iconIndex = ElisEnum.E_ICON_1080p
			#elif hdmiFormat == '1080p-25' :
			#	iconIndex = ElisEnum.E_ICON_1080p
			elif hdmiFormat == '720p' :
				iconIndex = ElisEnum.E_ICON_720p
			elif hdmiFormat == '576p' :
				iconIndex = -1
			self.mDataCache.Frontdisplay_Resolution( iconIndex )
		else :
			ElisPropertyEnum( 'HDMI Format', self.mCommander ).SetProp( aRestoreValue )
			prop = ElisPropertyEnum( 'HDMI Format', self.mCommander ).GetPropIndex( )
			control = self.getControl( E_SpinEx02 + 3 )
			control.selectItem( prop )

		self.mBusyVideoSetting = False


	def SetListControl( self ) :
		self.ResetAllControl( )
		time.sleep( 0.02 )
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( False )

		if selectedId == E_LANGUAGE :
			self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddInputControl( E_Input01, MR_LANG( 'Menu Language' ), XBMC_GetCurrentLanguage( ), MR_LANG( 'Select the language you want the menu to be in' ) )
			self.AddEnumControl( E_SpinEx01, 'Audio Language', None, MR_LANG( 'Select the language that you wish to listen to' ) )
			self.AddEnumControl( E_SpinEx02, 'Subtitle Language', None, MR_LANG( 'Select the language for the subtitle to be in' ) )
			self.AddEnumControl( E_SpinEx03, 'Secondary Subtitle Language', None, MR_LANG( 'Select the language for the secondary subtitle to be in' ) )
			self.AddEnumControl( E_SpinEx04, 'Hearing Impaired', None, MR_LANG( 'Set the hearing impaired function' ) )

			visibleControlIds = [ E_Input01, E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx05, E_SpinEx06, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			time.sleep( 0.02 )
			self.DisableControl( E_LANGUAGE )

		elif selectedId == E_PARENTAL :	
			self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddInputControl( E_Input01, MR_LANG( 'Edit Parental Settings' ), '', MR_LANG( 'Enter your PIN code to change the parental settings' ) )
			self.AddEnumControl( E_SpinEx01, 'Lock Mainmenu', MR_LANG( ' - Lock Main Menu' ), MR_LANG( 'Set a restriction for the main menu' ) )
			self.AddEnumControl( E_SpinEx02, 'Age Limit', MR_LANG( ' - Age Limit'), MR_LANG( 'Set an access restriction to chosen channels' ) )
			self.AddInputControl( E_Input02, MR_LANG( ' - Change PIN Code' ), '', MR_LANG( 'Change your PIN code' ) )

			visibleControlIds = [ E_SpinEx01, E_Input01, E_SpinEx02, E_Input02 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			time.sleep( 0.02 )
			self.DisableControl( E_PARENTAL )

		elif selectedId == E_RECORDING_OPTION :
			self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddEnumControl( E_SpinEx01, 'Automatic Timeshift', None, MR_LANG( 'When set to \'On\', your PRISMCUBE RUBY automatically start a timeshift recording when a different channel is selected' ) )
			self.AddEnumControl( E_SpinEx02, 'Timeshift Buffer Size', None, MR_LANG( 'Select the preferred size of timeshift buffer' ) )
			self.AddEnumControl( E_SpinEx03, 'Default Rec Duration', None, MR_LANG( 'Select recording duration for a channel that has no EPG info' ) )
			self.AddEnumControl( E_SpinEx04, 'Pre-Rec Time', None, MR_LANG( 'Set the pre-recording time for a EPG channel' ) )
			self.AddEnumControl( E_SpinEx05, 'Post-Rec Time', None, MR_LANG( 'Set the post-recording time for a EPG channel' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx06, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )

		elif selectedId == E_AUDIO_SETTING :
			self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddEnumControl( E_SpinEx01, 'Audio Dolby', MR_LANG( 'Dolby Audio' ), MR_LANG( 'When set to \'On\', Dolby Digital audio will be selected automatically when broadcast' ) )
			self.AddEnumControl( E_SpinEx02, 'Audio HDMI', None, MR_LANG( 'Set the Audio HDMI format' ) )
			self.AddEnumControl( E_SpinEx03, 'Audio Delay', None, MR_LANG( 'Select a delay time for audio' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03 ]
			self.SetEnableControls( visibleControlIds, True )
			self.SetVisibleControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx04, E_SpinEx05, E_SpinEx06, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )

		elif selectedId == E_HDMI_SETTING :
			self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Video Output' ), USER_ENUM_LIST_VIDEO_OUTPUT, self.mVideoOutput, MR_LANG( 'Select HDMI or Analog for your video output' ) )
			
			if self.mVideoOutput == E_VIDEO_HDMI :
				self.AddEnumControl( E_SpinEx02, 'HDMI Format', MR_LANG( ' - HDMI Format' ), MR_LANG( 'Set the display\'s HDMI resolution' ) )
				self.AddEnumControl( E_SpinEx03, 'Show 4:3', MR_LANG( ' - TV Screen Format' ), MR_LANG( 'Select the display format for TV screen' ) )
				self.AddEnumControl( E_SpinEx04, 'HDMI Color Space', MR_LANG( ' - HDMI Color Space' ), MR_LANG( 'Set RGB or YUV for HDMI color space' ) )
				
				visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
				self.SetVisibleControls( visibleControlIds, True )
				self.SetEnableControls( visibleControlIds, True )

				hideControlIds = [ E_SpinEx05, E_SpinEx06, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
				self.SetVisibleControls( hideControlIds, False )

				self.InitControl( )
			else :
				self.AddEnumControl( E_SpinEx02, 'TV Aspect', MR_LANG( ' - TV Aspect Ratio' ), MR_LANG( 'Set aspect ratio of your TV' ) )
				if self.mAnalogAscpect == E_16_9 :
					self.AddEnumControl( E_SpinEx03, 'Picture 16:9', MR_LANG( ' - Picture Format' ), MR_LANG( 'Set picture format according to TV aspect ratio' ) )
				else :
					self.AddEnumControl( E_SpinEx03, 'Picture 4:3', MR_LANG( ' - Picture Format' ), MR_LANG( 'Set picture format according to TV aspect ratio' ) )

				visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03 ]
				self.SetVisibleControls( visibleControlIds, True )
				self.SetEnableControls( visibleControlIds, True )

				hideControlIds = [ E_SpinEx04, E_SpinEx05, E_SpinEx06, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
				self.SetVisibleControls( hideControlIds, False )

				self.InitControl( )

		elif selectedId == E_NETWORK_SETTING :
			if self.mPlatform.IsPrismCube( ) :
				self.OpenBusyDialog( )
				self.AddUserEnumControl( E_SpinEx05, MR_LANG( 'Network Connection' ), USER_ENUM_LIST_NETWORK_TYPE, self.mUseNetworkType, MR_LANG( 'Select ethernet or wireless for your network connection' ) )
				self.AddInputControl( E_Input07, MR_LANG( 'Network Link' ), self.mStateNetLink, MR_LANG( 'Show network link status' ) )
				if self.mUseNetworkType == NETWORK_WIRELESS :
					self.LoadWifiInformation( )
					self.AddInputControl( E_Input01, MR_LANG( 'Search Wifi' ), self.mCurrentSsid, MR_LANG( 'Search for available wireless connections' ) )
					self.AddInputControl( E_Input02, MR_LANG( 'IP Address' ), self.mWifiAddress )
					self.AddInputControl( E_Input03, MR_LANG( 'Subnet Mask' ), self.mWifiSubnet )
					self.AddInputControl( E_Input04, MR_LANG( 'Gateway' ), self.mWifiGateway )
					self.AddInputControl( E_Input05, MR_LANG( 'DNS' ), self.mWifiDns )
					self.AddInputControl( E_Input06, MR_LANG( 'Manual Wifi Setup' ), '', MR_LANG( 'Press OK button to setup wireless network manually' ) )

					visibleControlIds = [ E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input07, E_Input06 ]
					self.SetVisibleControls( visibleControlIds, True )
					self.SetEnableControls( visibleControlIds, True )

					hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx06 ]
					self.SetVisibleControls( hideControlIds, False )
					
					self.InitControl( )
					time.sleep( 0.02 )
					self.DisableControl( E_WIFI )
				else :
					if self.mReLoadEthernetInformation == True :
						self.LoadEthernetInformation( )				
						self.mReLoadEthernetInformation = False

					self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Assign IP Address' ), USER_ENUM_LIST_DHCP_STATIC, self.mEthernetConnectMethod, MR_LANG( 'When set to \'DHCP\', your IP address will be automatically allocated by the DHCP server' ) )
					self.AddInputControl( E_Input01, MR_LANG( 'IP Address' ), self.mEthernetIpAddress, MR_LANG( 'Enter your IP address' ) )
					self.AddInputControl( E_Input02, MR_LANG( 'Subnet Mask' ), self.mEthernetNetmask, MR_LANG( 'Enter your subnet mask' ) )
					self.AddInputControl( E_Input03, MR_LANG( 'Gateway' ), self.mEthernetGateway, MR_LANG( 'Enter your gateway' ) )
					self.AddInputControl( E_Input04, MR_LANG( 'DNS' ), self.mEthernetNamesServer, MR_LANG( 'Enter the DNS server address' ) )
					self.AddInputControl( E_Input05, MR_LANG( 'Apply') , '', MR_LANG( 'Press OK button to save the IP address settings' ) )

					visibleControlIds = [ E_SpinEx01, E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input07 ]
					self.SetVisibleControls( visibleControlIds, True )
					self.SetEnableControls( visibleControlIds, True )

					hideControlIds = [ E_Input06, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx06 ]
					self.SetVisibleControls( hideControlIds, False )
					
					self.InitControl( )
					time.sleep( 0.02 )
					self.DisableControl( E_ETHERNET )

				self.SetEnableControl( E_Input07, False )
				if self.GetGroupId( self.getFocusId( ) ) != E_SpinEx05 :
					self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )

				self.CloseBusyDialog( )

			else :
				hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 , E_SpinEx05, E_SpinEx06, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
				self.SetVisibleControls( hideControlIds, False )
				self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( MR_LANG( 'Not Supported' ) )
				self.InitControl( )

		elif selectedId == E_TIME_SETTING :
			self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			setupChannelNumber = ElisPropertyInt( 'Time Setup Channel Number', self.mCommander ).GetProp( )
			self.mSetupChannel = self.mDataCache.Channel_GetByNumber( setupChannelNumber )
			self.mHasChannel = True
			if self.mSetupChannel and self.mSetupChannel.mError == 0 :
				channelName = self.mSetupChannel.mName
			else :
				channelList = self.mDataCache.Channel_GetList( )
				if channelList and channelList[0].mError == 0 :
					self.mSetupChannel = channelList[0]
					channelName = self.mSetupChannel.mName
				else :
					self.mHasChannel = False
					channelName = MR_LANG( 'None' )
					ElisPropertyEnum( 'Time Mode', self.mCommander ).SetProp( TIME_MANUAL )
				
			self.AddEnumControl( E_SpinEx01, 'Time Mode', MR_LANG( 'Time and Date' ), MR_LANG( 'When set to \'Automatic\', the time and date will be obtained automatically from the channel that you select' ) )
			self.AddInputControl( E_Input01, MR_LANG( 'Channel' ), channelName, MR_LANG( 'Select a channel you want to set your time and date by' ) )
			self.mDate = TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_DD_MM_YYYY )
			self.AddInputControl( E_Input02, MR_LANG( 'Date' ), self.mDate, MR_LANG( 'Enter today\'s date' ) )
			self.mTime = TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_HH_MM )
			self.AddInputControl( E_Input03, MR_LANG( 'Time' ), self.mTime, MR_LANG( 'Set the local time' ) )
			self.AddEnumControl( E_SpinEx02, 'Local Time Offset', None, MR_LANG( 'Set the time zone that will be the basis for the date and time display' ) )
			self.AddEnumControl( E_SpinEx03, 'Summer Time', None, MR_LANG( 'When set to \'Automatic\', the system automatically change over to summer time' ) )
			self.AddInputControl( E_Input04, MR_LANG( 'Apply' ), '', MR_LANG( 'Press OK button to save time settings' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input01, E_Input02, E_Input03, E_Input04 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx04, E_SpinEx05, E_SpinEx06, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			time.sleep( 0.02 )
			self.DisableControl( E_TIME_SETTING )

		elif selectedId == E_EPG :
			self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )

			self.mEpgGrabinngTime = ElisPropertyInt( 'EPG Grabbing Time', self.mCommander ).GetProp( )
			self.mEpgFavGroup = ElisPropertyInt( 'Auto EPG Favorite Group', self.mCommander ).GetProp( )
			self.mEpgStartChannel = ElisPropertyInt( 'Auto EPG Start Channel', self.mCommander ).GetProp( )
			self.mEpgEndChannel = ElisPropertyInt( 'Auto EPG End Channel', self.mCommander ).GetProp( )
			groupName = MR_LANG( 'None' )

			zappingmode = self.mDataCache.Zappingmode_GetCurrent( )
			allChannels = self.mDataCache.Channel_GetAllChannels( zappingmode.mServiceType, True )
			if not allChannels or len( allChannels ) < 1 :
				groupName = MR_LANG( 'None' )
				self.mEpgStartChannel = 1
				self.mEpgEndChannel = 1
				ElisPropertyInt( 'Auto EPG Start Channel', self.mCommander ).SetProp( self.mEpgStartChannel )
				ElisPropertyInt( 'Auto EPG End Channel', self.mCommander ).SetProp( self.mEpgEndChannel )
			else :
				favoriteGroup = self.mDataCache.Favorite_GetList( FLAG_ZAPPING_CHANGE, zappingmode.mServiceType )
				if not favoriteGroup or len( favoriteGroup ) < 1 :
					groupName = MR_LANG( 'None' )
				else :
					if self.mEpgFavGroup >= len( favoriteGroup ) :
						self.mEpgFavGroup = 0
						ElisPropertyInt( 'Auto EPG Favorite Group', self.mCommander ).SetProp( 0 )
					groupName = favoriteGroup[ self.mEpgFavGroup ].mGroupName

				if self.mEpgStartChannel > len( allChannels ) or self.mEpgEndChannel > len( allChannels ) :
					self.mEpgStartChannel = 1
					self.mEpgEndChannel = 1
					ElisPropertyInt( 'Auto EPG Start Channel', self.mCommander ).SetProp( self.mEpgStartChannel )
					ElisPropertyInt( 'Auto EPG End Channel', self.mCommander ).SetProp( self.mEpgEndChannel )

			
			self.AddEnumControl( E_SpinEx01, 'Auto EPG', MR_LANG( 'Auto EPG grabbing' ), MR_LANG( 'When set to \'On\', the system automatically grabbin EPG' ) )
			self.AddEnumControl( E_SpinEx02, 'EPG Grab Interval', None, MR_LANG( 'Select EPG grabbing interval time' ) )
			self.AddEnumControl( E_SpinEx03, 'Auto EPG Channel', None, MR_LANG( 'Select EPG grabinng type' ) )
			self.AddInputControl( E_Input01, MR_LANG( 'EPG grabbing time' ), '%02d:%02d' % ( ( self.mEpgGrabinngTime / 3600 ), ( self.mEpgGrabinngTime % 3600 / 60 ) ), MR_LANG( 'Input EPG grabinng time' ) )
			self.AddInputControl( E_Input02, MR_LANG( 'Auto EPG channel setting' ), MR_LANG( 'Start Channel Num : %s, End Channel Num : %s' ) % ( self.mEpgStartChannel, self.mEpgEndChannel ) , MR_LANG( 'Select EPG grabinng start channel and end channel' ) )
			self.AddInputControl( E_Input03, MR_LANG( 'Auto EPG group setting' ), groupName, MR_LANG( 'Select EPG grabinng favoriate name' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input01, E_Input02, E_Input03 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx04, E_SpinEx05, E_SpinEx06,  E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			time.sleep( 0.2 )
			self.DisableControl( E_EPG )

		elif selectedId == E_FORMAT_HDD :
			self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddInputControl( E_Input01, MR_LANG( 'Format Media Partition' ), '', MR_LANG( 'Press OK button to remove everything in the media partition' ) )
			self.AddInputControl( E_Input02, MR_LANG( 'Format Recording Partition' ), '', MR_LANG( 'Press OK button to remove everything in the recording partition' ) )
			self.AddInputControl( E_Input03, MR_LANG( 'Format Hard Drive' ), '', MR_LANG( 'Press OK button to erase your hard disk drive' ) )

			visibleControlIds = [ E_Input01, E_Input02, E_Input03 ]
			self.SetVisibleControls( visibleControlIds, True )

			if CheckHdd( ) :
				self.SetEnableControls( visibleControlIds, True )
			else :
				self.SetEnableControls( visibleControlIds, False )

			hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )

		elif selectedId == E_FACTORY_RESET :
			self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddInputControl( E_Input01, MR_LANG( 'Start Factory Reset'), '', MR_LANG( 'Go to first installation after restoring system to the factory default' ) )

			visibleControlIds = [ E_Input01 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 , E_SpinEx05, E_SpinEx06, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )

		elif selectedId == E_ETC :
			self.mRssfeed				= int( GetSetting( 'RSS_FEED' ) )

			self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddEnumControl( E_SpinEx01, 'Deep Standby', None, MR_LANG( 'When set to \'On\', the system switches to deep standby mode if you press \'Standby\' button to help reduce the amount of electricity used' ) )
			self.AddEnumControl( E_SpinEx02, 'Power Save Mode', None, MR_LANG( 'Set the time for switching into standby mode when not being used' ) )
			self.AddEnumControl( E_SpinEx03, 'Fan Control', None, MR_LANG( 'Adjust the fan speed level for your system' ) )
			self.AddEnumControl( E_SpinEx04, 'Channel Banner Duration', MR_LANG( 'Channel Banner Time' ), MR_LANG( 'Set the time for the channel info to be displayed when zapping' ) )		#	Erase channel list yes/no
			self.AddEnumControl( E_SpinEx05, 'Playback Banner Duration', MR_LANG( 'Playback Banner Time' ), MR_LANG( 'Set the time for the playback info to be displayed on the screen' ) )	#	Erase custom menu yes/no
			self.AddUserEnumControl( E_SpinEx06, MR_LANG( 'RSS Feed' ), USER_ENUM_LIST_ON_OFF, self.mRssfeed, MR_LANG( 'Enable RSS feed in the main menu' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )

		else :
			LOG_ERR( 'Cannot find selected ID' )

		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( True )


	def DisableControl( self, aSelectedItem ) :
		if aSelectedItem == E_LANGUAGE :
			selectedIndex = self.GetSelectedIndex( E_SpinEx02 )
			visibleControlIds = [ E_SpinEx03, E_SpinEx04 ]
			if selectedIndex == 0 :
				self.SetEnableControls( visibleControlIds, False )
				control = self.getControl( E_SpinEx04 + 3 )
				time.sleep( 0.02 )
				control.selectItem( 0 )
				self.SetProp( E_SpinEx04, 0 )
			else :
				self.SetEnableControls( visibleControlIds, True )

		elif aSelectedItem == E_ETHERNET :
			visibleControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04 ]
			if self.mEthernetConnectMethod == NET_DHCP :
				self.SetEnableControls( visibleControlIds, False )
			else :
				self.SetEnableControls( visibleControlIds, True )

		elif aSelectedItem == E_WIFI :
			visibleControlIds = [ E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetEnableControls( visibleControlIds, False )
			if not E_USE_OLD_NETWORK :
				self.SetEnableControl( E_Input06, False )
				
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
				self.SetEnableControl( E_SpinEx02, False )
				self.SetEnableControl( E_SpinEx03, False )
			else :
				selectedIndex = self.GetSelectedIndex( E_SpinEx01 )
				if selectedIndex == TIME_AUTOMATIC :
					self.SetEnableControl( E_Input02, False )
					self.SetEnableControl( E_Input03, False )
					self.SetEnableControl( E_Input01, True )
					self.SetEnableControl( E_SpinEx02, True )
					self.SetEnableControl( E_SpinEx03, True )
				else :
					localTimeOffsetControl = self.getControl( E_SpinEx02 + 3 )
					summerTimeControl = self.getControl( E_SpinEx03 + 3 )
					time.sleep( 0.02 )
					localTimeOffsetControl.selectItem( ElisPropertyEnum( 'Local Time Offset', self.mCommander ).GetIndexByProp( 0 ) )
					summerTimeControl.selectItem( SUMMER_TIME_OFF )
					
					self.SetEnableControl( E_Input01, False )
					self.SetEnableControl( E_Input02, True )
					self.SetEnableControl( E_Input03, True )
					self.SetEnableControl( E_SpinEx02, False )
					self.SetEnableControl( E_SpinEx03, False )

		elif aSelectedItem == E_EPG :
			selectedIndex = self.GetSelectedIndex( E_SpinEx03 )
			if selectedIndex == 0 :
				self.SetEnableControl( E_Input02, True )
				self.SetEnableControl( E_Input03, False )
			else :
				self.SetEnableControl( E_Input02, False )
				self.SetEnableControl( E_Input03, True )


	def LoadEthernetInformation( self ) :
		self.mEthernetConnectMethod = NetMgr.GetInstance( ).GetEthernetMethod( )
		self.mEthernetIpAddress, self.mEthernetNetmask, self.mEthernetGateway, self.mEthernetNamesServer = NetMgr.GetInstance( ).GetNetworkAddress( NETWORK_ETHERNET )


	def ConnectEthernet( self ) :
		self.mProgressThread = self.ShowProgress( MR_LANG( 'Now connecting...' ), 20 )
		NetMgr.GetInstance( ).WriteEthernetConfig( self.mEthernetConnectMethod, self.mEthernetIpAddress, self.mEthernetNetmask, self.mEthernetGateway, self.mEthernetNamesServer )
		NetMgr.GetInstance( ).DisConnectWifi( )
		NetMgr.GetInstance( ).DeleteConfigFile( )
		time.sleep( 0.5 )
		ret = NetMgr.GetInstance( ).ConnectEthernet( self.mEthernetConnectMethod, self.mEthernetIpAddress, self.mEthernetNetmask, self.mEthernetGateway, self.mEthernetNamesServer )
		time.sleep( 1 )
		if ret == False :
			self.CloseProgress( )
			time.sleep( 0.5 )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Network setup failed to complete' ) )
 			dialog.doModal( )
		else :
			self.LoadEthernetInformation( )
			NetMgr.GetInstance( ).SetNetworkProperty( self.mEthernetIpAddress, self.mEthernetNetmask, self.mEthernetGateway, self.mEthernetNamesServer )
			self.mReLoadEthernetInformation = True
			self.SetListControl( )
			self.CloseProgress( )


	def EthernetSetting( self, aControlId ) :
		if aControlId == E_SpinEx01 :
			if self.mEthernetConnectMethod == NET_DHCP :
				self.mEthernetConnectMethod = NET_STATIC
			else :
				self.mEthernetConnectMethod = NET_DHCP
			self.DisableControl( E_ETHERNET )
			
		elif aControlId == E_Input01 :
			self.mEthernetIpAddress = self.ShowIpInputDialog( self.mEthernetIpAddress )
			self.SetListControl( )

		elif aControlId == E_Input02 :
			self.mEthernetNetmask = self.ShowIpInputDialog( self.mEthernetNetmask )
			self.SetListControl( )

		elif aControlId == E_Input03 :
			self.mEthernetGateway = self.ShowIpInputDialog( self.mEthernetGateway )
			self.SetListControl( )

		elif aControlId == E_Input04 :
			self.mEthernetNamesServer = self.ShowIpInputDialog( self.mEthernetNamesServer )
			self.SetListControl( )

		elif aControlId == E_Input05 :
			if self.mEthernetConnectMethod == NET_STATIC :
				if self.mEthernetIpAddress == 'None' or self.mEthernetNetmask == 'None' or self.mEthernetGateway == 'None' or self.mEthernetNamesServer == 'None' :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Invalid IP address' ) )					
					dialog.doModal( )
					return

			self.ConnectEthernet( )


	def WifiSetting( self, aControlId ) :
		apList = []

		if aControlId == E_Input01 :
			self.mProgressThread = self.ShowProgress( MR_LANG( 'Now searching...' ), 30 )
			time.sleep( 0.5 )
			if NetMgr.GetInstance( ).LoadSetWifiTechnology( ) == False :
				self.CloseProgress( )
				time.sleep( 0.5 )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Wifi device not found' ) )
				dialog.doModal( )
				return

			apList = NetMgr.GetInstance( ).GetSearchedWifiApList( )
			
			if len( apList ) == 0 :
				self.CloseProgress( )
				time.sleep( 0.5 )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Wifi service not found' ) )
				dialog.doModal( )
				return
			self.CloseProgress( )

			dialog = xbmcgui.Dialog( )
			apNameList = []
			for ap in apList :
				apNameList.append( ap[0] + MR_LANG( '    - Strength : %s Encryption : %s' ) % ( ap[1], ap[2] ) )
			dialog = xbmcgui.Dialog( )
			ret = dialog.select( MR_LANG( 'Select Wifi' ), apNameList )
			if ret >= 0 :
				if self.mCurrentSsid != apList[ret][0] :
					self.mUseStatic = NET_DHCP
					self.mUseHiddenId = NOT_USE_HIDDEN_SSID
					self.mCurrentSsid = apList[ret][0]
				self.mEncryptType = NetMgr.GetInstance( ).ApInfoToEncrypt( apList[ret][2] )
				self.SetControlLabel2String( E_Input01, self.mCurrentSsid )
				self.ConnectCurrentWifi( )

		elif aControlId == E_Input06 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_MENUAL_WIFI )
			dialog.SetDefaultValue( self.mCurrentSsid, self.mUseStatic, self.mWifiAddress, self.mWifiSubnet, self.mWifiGateway, self.mWifiDns, self.mUseHiddenId, self.mHiddenSsid, self.mEncryptType )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.mUseStatic, self.mWifiAddress, self.mWifiSubnet, self.mWifiGateway, self.mWifiDns, self.mUseHiddenId, self.mHiddenSsid, self.mEncryptType = dialog.GetValue( )
				if self.mUseHiddenId == USE_HIDDEN_SSID :
					self.mCurrentSsid = self.mHiddenSsid
				if self.mCurrentSsid == 'None' and self.mUseHiddenId == NOT_USE_HIDDEN_SSID :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'SSID not configured' ) )					
					dialog.doModal( )
				else :
					self.ConnectCurrentWifi( )


	def ConnectCurrentWifi( self ) :
		if self.mEncryptType != ENCRYPT_OPEN :
			dialog = xbmc.Keyboard( self.mPassWord, MR_LANG( 'Enter an encryption key' ), True )
			dialog.setHiddenInput( True )
			dialog.doModal( )
			if( dialog.isConfirmed( ) ) :
				self.mPassWord = dialog.getText( )
				#self.mPassWord = InputKeyboard( E_INPUT_KEYBOARD_TYPE_HIDE, MR_LANG( 'Enter an encryption key' ), self.mPassWord, 48 )
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
			else :
				return
	
		self.mProgressThread = self.ShowProgress( MR_LANG( 'Now connecting...' ), 30 )
		time.sleep( 0.5 )
		#self.mUseStatic = aUseStatic
		#self.mUseHiddenId = aUseHiddenSSID

		if NetMgr.GetInstance( ).LoadSetWifiTechnology( ) :
			if E_USE_OLD_NETWORK == False :
				ret1 = NetMgr.GetInstance( ).WriteWifiConfigFile( self.mCurrentSsid, self.mPassWord, self.mUseHiddenId )
				ret2 = NetMgr.GetInstance( ).WriteWifiConfig( self.mCurrentSsid, self.mPassWord, self.mUseHiddenId )
				ret3 = NetMgr.GetInstance( ).LoadWifiService( )
			else :				
				ret1 = NetMgr.GetInstance( ).WriteWifiInterfaces( self.mUseStatic, self.mWifiAddress, self.mWifiSubnet, self.mWifiGateway, self.mWifiDns )
				ret2 = NetMgr.GetInstance( ).WriteWpaSupplicant( self.mUseHiddenId, self.mHiddenSsid, self.mCurrentSsid, self.mEncryptType, self.mPassWord )
				ret3 = NetMgr.GetInstance( ).ConnectWifi( )
			
			if ret1 == False or ret2 == False or ret3 == False :
				self.CloseProgress( )
				time.sleep( 0.5 )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Wifi setup failed to complete' ) )
				dialog.doModal( )
			else :
				# use Connman
				wifi = NetMgr.GetInstance( ).GetCurrentWifiService( )
				ret1 = NetMgr.GetInstance( ).SetServiceConnect( wifi, True )
				ret2 = NetMgr.GetInstance( ).VerifiedState( wifi )
				ret3 = NetMgr.GetInstance( ).SetAutoConnect( wifi, False )
				time.sleep( 1 )
				NetMgr.GetInstance( ).DisConnectEthernet( )
				# use Connman

				time.sleep( 0.5 )
				self.LoadWifiAddress( )
				NetMgr.GetInstance( ).SetNetworkProperty( self.mWifiAddress, self.mWifiSubnet, self.mWifiGateway, self.mWifiDns )
				self.SetListControl( )
				self.CloseProgress( )
				if ret1 == False or ret2 == False or ret3 == False :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Wifi setup failed to complete' ) )
					dialog.doModal( )
				
		else :
			self.CloseProgress( )
			time.sleep( 0.5 )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Wifi device not found' ) )
			dialog.doModal( )
			return


	def LoadWifiInformation( self ) :
		tmpSSID = self.mCurrentSsid
		self.mCurrentSsid = NetMgr.GetInstance( ).GetConfiguredSSID( )
		if self.mCurrentSsid == None :
			self.mCurrentSsid = tmpSSID
		tmpPasswd = self.mPassWord
		self.mPassWord = NetMgr.GetInstance( ).GetConfiguredPassword( )
		if self.mPassWord == None :
			self.mPassWord = tmpPasswd
		self.mEncryptType = NetMgr.GetInstance( ).GetWifiEncryptType( )
		self.mUseStatic	  = NetMgr.GetInstance( ).GetWifiUseStatic( )
		self.mUseHiddenId = NetMgr.GetInstance( ).GetWifiUseHiddenSsid( )
		if self.mUseHiddenId == USE_HIDDEN_SSID :
			self.mHiddenSsid = self.mCurrentSsid
		self.LoadWifiAddress( )


	def LoadWifiAddress( self ) :
		self.mWifiAddress, self.mWifiSubnet, self.mWifiGateway, self.mWifiDns = NetMgr.GetInstance( ).GetNetworkAddress( NETWORK_WIRELESS )


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
				dialog.SetDialogProperty( 20, MR_LANG( 'Setting time...' ), ElisEventTimeReceived.getName( ) )
				dialog.doModal( )
				self.OpenBusyDialog( )
				if dialog.GetResult( ) == False :
					self.ReLoadTimeSet( )

				self.mDataCache.LoadTime( )
				self.SetListControl( )
				ElisPropertyEnum( 'Time Installation', self.mCommander ).SetProp( 0 )
				self.mDataCache.Channel_SetCurrent( oriChannel.mNumber, oriChannel.mServiceType ) # Todo After : using ServiceType to different way
				self.CloseBusyDialog( )
			else :
				self.OpenBusyDialog( )
				try :
					sumtime = self.mDate + '.' + self.mTime
					t = time.strptime( sumtime, '%d.%m.%Y.%H:%M' )
					ret = self.mCommander.Datetime_SetSystemUTCTime( int( time.mktime( t ) ) )
					globalEvent = pvr.GlobalEvent.GetInstance( )
					globalEvent.SendLocalOffsetToXBMC( )
				except Exception, e :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Invalid input' ) )
					dialog.doModal( )
				self.CloseBusyDialog( )
			
			if mode == TIME_AUTOMATIC and dialog.GetResult( ) == False :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No time info was given by that channel' ) )
				dialog.doModal( )

			if mute == False :
				thread = threading.Timer( 0.3, self.SyncVolume )
				thread.start( )


	def SyncVolume ( self ) :
		self.mCommander.Player_SetMute( False )
		self.mDataCache.SyncMute( )


	def SetDefaultVolume( self ) :
		#volume : 75db
		LOG_TRACE( '>>>>>>>> Default init : Volume <<<<<<<<' )
		self.mCommander.Player_SetMute( False )
		if XBMC_GetMute( ) :
			xbmc.executebuiltin( 'Mute( )' )
		self.mCommander.Player_SetVolume( DEFAULT_VOLUME )
		XBMC_SetVolumeByBuiltin( DEFAULT_VOLUME, False )


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
		self.mStateNetLink = NetMgr.GetInstance( ).CheckInternetState( )
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
		count = 0
		while self.mEnableLocalThread :
			if self.mCtrlLeftGroup.getSelectedPosition( ) == E_NETWORK_SETTING :
				if ( count % 50 ) == 0 :
					self.CheckNetworkStatus( )
			count = count + 1
			time.sleep( TIME_SEC_CHECK_NET_STATUS )


	def DedicatedFormat( self ) :
		self.mUseUsbBackup = False
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( MR_LANG( 'Backup data?' ), MR_LANG( 'To backup your user data and XBMC add-ons,%s insert a USB flash memory' )% NEW_LINE )
		dialog.doModal( )
		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			if CheckDirectory( '/mnt/hdd0/program/.xbmc/userdata' ) and CheckDirectory( '/mnt/hdd0/program/.xbmc/addons' ) :
				self.BackupAndFormat( )
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Cannot find backup data' ) )
				dialog.doModal( )
		else :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Start formatting without making a backup?' ), MR_LANG( 'Formatting HDD cannot be undone!' ) )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.MakeDedicate( )


	def BackupAndFormat( self ) :
		usbpath = self.mDataCache.USB_GetMountPath( )
		if usbpath :
			size_addons = GetDirectorySize( '/mnt/hdd0/program/.xbmc/addons' )
			size_udata = GetDirectorySize( '/mnt/hdd0/program/.xbmc/userdata' )
			usbfreesize = GetDeviceSize( usbpath )
			if ( size_addons + size_udata ) > usbfreesize :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Not enough space on USB flash memory' ) )
				dialog.doModal( )
			else :
				self.CopyBackupData( usbpath )
		else :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Please insert a USB flash memory' ) )
			dialog.doModal( )


	def CopyBackupData( self, aUsbpath ) :
		self.mProgressThread = self.ShowProgress( MR_LANG( 'Now backing up your user data...' ), 30 )
		if CheckDirectory( aUsbpath + '/RubyBackup/' ) :
			RemoveDirectory( aUsbpath + '/RubyBackup/' )

		ret_udata = CopyToDirectory( '/mnt/hdd0/program/.xbmc/userdata', aUsbpath + '/RubyBackup/userdata' )
		ret_addons = CopyToDirectory( '/mnt/hdd0/program/.xbmc/addons', aUsbpath + '/RubyBackup/addons' )
		if ret_udata and ret_addons :
			self.CloseProgress( )
			time.sleep( 0.5 )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Start formatting HDD?' ), MR_LANG( 'Press OK button to format your HDD now' ) )
			dialog.doModal( )
			self.mUseUsbBackup = True
			self.MakeDedicate( )
		else :
			self.CloseProgress( )
			time.sleep( 0.5 )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Data backup failed' ) )
			dialog.doModal( )


	def MakeDedicate( self ) :
		mediasize = 100
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
		dialog.SetDialogProperty( MR_LANG( 'Enter the size of the media partition in GB' ), '%s' % mediasize , 3 )
		dialog.doModal( )
		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			mediasize = dialog.GetString( )
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( MR_LANG( 'Media partition will be %s GB' ) % mediasize, MR_LANG( 'Start formatting HDD?' ) )
		dialog.doModal( )
		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			self.OpenBusyDialog( )
			ElisPropertyInt( 'MediaRepartitionSize', self.mCommander ).SetProp( int( mediasize ) * 1024 )
			ElisPropertyEnum( 'HDDRepartition', self.mCommander ).SetProp( 1 )
			self.mDataCache.Player_AVBlank( True )
			if self.mUseUsbBackup :
				self.MakeBackupScript( )
			self.mCommander.Make_Dedicated_HDD( )


	def MakeBackupScript( self ) :
		try :
			scriptFile = '%s.sh' % E_DEFAULT_BACKUP_PATH
			fd = open( scriptFile, 'w' )
			if fd :
				fd.writelines( '#!/bin/sh\n' )
				fd.writelines( 'modprobe usb_storage\n' )
				fd.writelines( 'sleep 3\n' )
				fd.writelines( 'mount /dev/sdb1 /media/usb/sdb1\n' )
				usbpath = self.mDataCache.USB_GetMountPath( )
				fd.writelines( 'mkdir -p /mnt/hdd0/program/.xbmc/userdata\n' )
				fd.writelines( 'mkdir -p /mnt/hdd0/program/.xbmc/addons\n' )
				fd.writelines( 'cp -rf %s/RubyBackup/userdata/* /mnt/hdd0/program/.xbmc/userdata/\n' % usbpath )
				fd.writelines( 'cp -rf %s/RubyBackup/addons/* /mnt/hdd0/program/.xbmc/addons/\n' % usbpath )
				fd.close( )
				os.chmod( scriptFile, 0755 )

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )


	def ETCSetting( self, aGroupId ) :
		if aGroupId == E_SpinEx02 :
	 		self.ControlSelect( )
	 		self.mCommander.Power_Save_Mode( )

		elif aGroupId == E_SpinEx04 :
			self.ControlSelect( )
			propertyBanner = ElisPropertyEnum( 'Channel Banner Duration', self.mCommander ).GetProp( )
			self.mDataCache.SetPropertyChannelBannerTime( propertyBanner )

		elif aGroupId == E_SpinEx05 :
			self.ControlSelect( )
			propertyBanner = ElisPropertyEnum( 'Playback Banner Duration', self.mCommander ).GetProp( )
			self.mDataCache.SetPropertyPlaybackBannerTime( propertyBanner )

		elif aGroupId == E_SpinEx06 :
			if self.mRssfeed :
				self.mRssfeed = 0
			else :
				self.mRssfeed = 1
			SetSetting( 'RSS_FEED', '%d' % self.mRssfeed )

		else :
			self.ControlSelect( )


	def ShowFavoriteGroup( self ) :
		zappingmode = self.mDataCache.Zappingmode_GetCurrent( )

		#check AllChannels
		allChannels = self.mDataCache.Channel_GetAllChannels( zappingmode.mServiceType, True )
		if not allChannels or len( allChannels ) < 1 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No channels available' ) )
			dialog.doModal( )
			return -1

		#check fav groups
		favoriteGroup = self.mDataCache.Favorite_GetList( FLAG_ZAPPING_CHANGE, zappingmode.mServiceType )
		if not favoriteGroup or len( favoriteGroup ) < 1 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No favorite group available' ) )
			dialog.doModal( )
			return -1

		favoriteList = []
		for item in favoriteGroup :
			favoriteList.append( item.mGroupName )

		dialog = xbmcgui.Dialog( )
		ret = dialog.select( MR_LANG( 'Favorite group' ), favoriteList, False, self.mEpgFavGroup )
		if ret >= 0 :
			return ret
		else :
			return -1


	def SetStartEndChannel( self ) :
		zappingmode = self.mDataCache.Zappingmode_GetCurrent( )

		#check AllChannels
		allChannels = self.mDataCache.Channel_GetAllChannels( zappingmode.mServiceType, True )
		if not allChannels or len( allChannels ) < 1 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No channels available' ) )
			dialog.doModal( )
			return

		channelList = []
		for channel in allChannels :
			channelList.append( '%s %s' % ( channel.mNumber, channel.mName ) )

		dialog = xbmcgui.Dialog( )
		ret = dialog.select( MR_LANG( 'Select start channel' ), channelList, False, 0 )
		if ret >= 0 :
			self.mEpgStartChannel = allChannels[ ret ].mNumber
		else :
			return
		ret = dialog.select( MR_LANG( 'Select end channel' ), channelList, False, 0 )
		if ret >= 0 :
			self.mEpgEndChannel = allChannels[ ret ].mNumber
		else :
			return

		if self.mEpgStartChannel > self.mEpgEndChannel :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'end channel available ' ) )
			dialog.doModal( )
			return

		ElisPropertyInt( 'Auto EPG Start Channel', self.mCommander ).SetProp( self.mEpgStartChannel )
		ElisPropertyInt( 'Auto EPG End Channel', self.mCommander ).SetProp( self.mEpgEndChannel )
		self.SetListControl( )
