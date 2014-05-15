from pvr.gui.WindowImport import *
from subprocess import *
import pvr.Platform
if E_USE_OLD_NETWORK :
	import pvr.IpParser as NetMgr
else :
	import pvr.NetworkMgr as NetMgr
from urllib import urlencode
import urllib2 as urllib

E_CONFIGURE_BASE_ID				=  WinMgr.WIN_ID_CONFIGURE * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 
E_CONFIGURE_SETUPMENU_GROUP_ID	=  E_CONFIGURE_BASE_ID + 9010
E_CONFIGURE_SUBMENU_LIST_ID		=  E_CONFIGURE_BASE_ID + 9000
E_CONFIGURE_SETTING_DESCRIPTION	=  E_CONFIGURE_BASE_ID + 1003


E_CONFIGURE_DEFAULT_FOCUS_ID    =  E_CONFIGURE_SUBMENU_LIST_ID
E_GROUP_ID_SHOW_INFO            =  E_CONFIGURE_BASE_ID + 1300
E_PROGRESS_NETVOLUME            =  E_CONFIGURE_BASE_ID + 1301
E_LABEL_ID_USE_INFO             =  E_CONFIGURE_BASE_ID + 1302

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
HDD_RESERVED_USE		= 70


class Configure( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mCtrlLeftGroup 		= None
		self.mGroupItems 			= []
		self.mLastFocused 			= E_CONFIGURE_SUBMENU_LIST_ID
		self.mPrevListItemID 		= 0

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
		self.mUseStatic				= NET_DHCP

		self.mCheckNetworkTimer		= None
		self.mStateNetLink			= 'Busy'

		self.mEnableLocalThread	 	= False
		self.mProgressThread		= None

		self.mVideoOutput			= E_VIDEO_HDMI

		self.mAnalogAscpect			= E_16_9
		self.mUpdateNotify 			= int( GetSetting( 'UPDATE_NOTIFY' ) )

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
		self.mWinId = xbmcgui.getCurrentWindowId( )

		leftGroupItems			= [
		MR_LANG( 'Language' ),
		MR_LANG( 'Parental Control' ),
		MR_LANG( 'Recording Option' ),
		MR_LANG( 'Audio Setting' ),
		MR_LANG( 'Video Setting' ),
		MR_LANG( 'Network Setting' ),
		MR_LANG( 'Time Setting' ),
		MR_LANG( 'EPG Setting' ),
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
		MR_LANG( 'Configure EPG grabber settings' ),
		MR_LANG( 'Delete everything off your hard drive' ),
		MR_LANG( 'Restore your system to factory settings' ),
		MR_LANG( 'Change additional settings for PRISMCUBE RUBY' ) ]
	
		self.setFocusId( E_CONFIGURE_DEFAULT_FOCUS_ID )
		self.SetActivate( True )
		self.SetSingleWindowPosition( E_CONFIGURE_BASE_ID )
		self.SetFrontdisplayMessage( MR_LANG('Configuration') )
		self.SetHeaderTitle( "%s - %s" % ( MR_LANG( 'Installation' ), MR_LANG( 'Configuration' ) ) )

		self.MakeLanguageList( )

		self.mCtrlLeftGroup = self.getControl( E_CONFIGURE_SUBMENU_LIST_ID )
		self.mCtrlLeftGroup.addItems( self.mGroupItems )
		
		if self.mPrevListItemID != -1 :
			self.mCtrlLeftGroup.selectItem( self.mPrevListItemID )

		self.mVisibleParental = False
		self.mReLoadEthernetInformation = True

		self.mUseNetworkType = NetMgr.GetInstance( ).GetCurrentServiceType( )
		NetMgr.GetInstance( ).SetIsConfigureWindow( True )

		self.mAnalogAscpect = ElisPropertyEnum( 'TV Aspect', self.mCommander ).GetProp( )
		self.mVideoOutput	= self.mDataCache.GetVideoOutput( )
		self.mHDDStatus     = True

		self.SetListControl( )
		self.StartCheckNetworkTimer( )
		self.mInitialized = True
		self.CloseBusyDialog( )

		self.mEventBus.Register( self )


	def Close( self ) :
		self.mEventBus.Deregister( self )
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

		elif actionId == Action.ACTION_PAGE_UP or actionId == Action.ACTION_PAGE_DOWN :
			if focusId == E_CONFIGURE_SUBMENU_LIST_ID and selectedId != self.mPrevListItemID :
				self.mPrevListItemID = selectedId
				self.mReLoadEthernetInformation = True
				self.mVisibleParental = False
				self.SetListControl( )

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
				if ret >= 0 and ret != currentindex:
					if not self.mPlatform.IsPrismCube( ) :
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No %s support' ) % self.mPlatform.GetName( ) )
						dialog.doModal( )
						return

					isDownload = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_SYSTEM_UPDATE ).GetStatusFromFirmware( )
					if isDownload :
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( MR_LANG( 'Change Menu Language' ), MR_LANG( 'Try again after completing firmware update' ) )
						dialog.doModal( )
						return

					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
					dialog.SetDialogProperty( MR_LANG( 'Change Menu Language' ), MR_LANG( 'Do you want to continue?' ), MR_LANG( 'please wait after pressing OK button' ) )
					dialog.doModal( )

					if dialog.IsOK( ) == E_DIALOG_STATE_YES :
						prop = GetXBMCLanguageToPropLanguage( menuLanguageList[ ret ] )
						ElisPropertyEnum( 'Language', self.mCommander ).SetProp( prop )
						prop = GetXBMCLanguageToPropAudioLanguage( menuLanguageList[ ret ] )
						ElisPropertyEnum( 'Audio Language', self.mCommander ).SetProp( prop )
						self.mInitialized = False
						self.StopCheckNetworkTimer( )
						time.sleep( 0.5 )
						XBMC_SetCurrentLanguage( menuLanguageList[ ret ] )
						self.mDataCache.SetChannelReloadStatus( True )
						WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_SIMPLE_CHANNEL_LIST ).ResetControls( )

			elif groupId == E_Input02 :
				dialog = xbmcgui.Dialog( )
				ret = dialog.select( MR_LANG( 'Select Audio Language' ), self.mAudioLanguageList, False, StringToListIndex( self.mAudioLanguageList, self.GetControlLabel2String( E_Input02 ) ) )
				if ret >= 0 :
					ElisPropertyEnum( 'Audio Language', self.mCommander ).SetPropIndex( ret )
					self.SetControlLabel2String( E_Input02, self.mAudioLanguageList[ ret ] )

			elif groupId == E_Input03 :
				dialog = xbmcgui.Dialog( )
				ret = dialog.select( MR_LANG( 'Select Subtitle Language' ), self.mSubtitleLanguageList, False, StringToListIndex( self.mSubtitleLanguageList, self.GetControlLabel2String( E_Input03 ) ) )
				if ret >= 0 :
					ElisPropertyEnum( 'Subtitle Language', self.mCommander ).SetPropIndex( ret )
					self.SetControlLabel2String( E_Input03, self.mSubtitleLanguageList[ ret ] )
					self.DisableControl( E_LANGUAGE )

			elif groupId == E_Input04 :
				dialog = xbmcgui.Dialog( )
				ret = dialog.select( MR_LANG( 'Select Secondary Subtitle Language' ), self.mSubtitleLanguageList_S, False, StringToListIndex( self.mSubtitleLanguageList_S, self.GetControlLabel2String( E_Input04 ) ) )
				if ret >= 0 :
					ElisPropertyEnum( 'Secondary Subtitle Language', self.mCommander ).SetPropIndex( ret )
					self.SetControlLabel2String( E_Input04, self.mSubtitleLanguageList_S[ ret ] )

			elif groupId == E_SpinEx01 :
				self.ControlSelect( )

		elif selectedId == E_HDMI_SETTING :
			if groupId == E_SpinEx01 :
				self.mVideoOutput = self.GetSelectedIndex( E_SpinEx01 )
				self.mDataCache.SetVideoOutput( self.mVideoOutput )
				self.SetListControl( )
				return

			elif self.mVideoOutput == E_VIDEO_ANALOG and groupId == E_SpinEx02 :
				self.ControlSelect( )
				time.sleep( 0.02 )
				self.mAnalogAscpect = self.GetSelectedIndex( E_SpinEx02 )
				self.SetListControl( ) 

			elif self.mVideoOutput == E_VIDEO_HDMI and groupId == E_Input01 :
				self.ShowHdmiFormat( )

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
				self.OpenBusyDialog( )
				self.SetListControl( )
				self.CloseBusyDialog( )

			elif self.mUseNetworkType == NETWORK_ETHERNET :
				self.EthernetSetting( groupId )
			elif self.mUseNetworkType == NETWORK_WIRELESS :
				self.WifiSetting( groupId )

		elif selectedId == E_TIME_SETTING :
			self.TimeSetting( groupId )

		elif selectedId == E_EPG :
			if groupId == E_SpinEx01 or groupId == E_SpinEx03 :
				self.ControlSelect( )
				self.DisableControl( E_EPG )

			elif groupId == E_SpinEx02 :
				self.ControlSelect( )

			elif groupId == E_Input01 :
				timeT = '%02d:%02d' % ( ( self.mEpgGrabinngTime / 3600 ), ( self.mEpgGrabinngTime % 3600 / 60 ) )
				timeT = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_TIME, MR_LANG( 'Enter Start Time' ), timeT )
				tmptime = timeT.split( ':' )
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
					if tmp == 0 :
						#self.mEpgFavGroup = 10000
						ElisPropertyInt( 'Auto EPG Favorite Group', self.mCommander ).SetProp( 255 )
					else :
						self.mEpgFavGroup = tmp - 1
						ElisPropertyInt( 'Auto EPG Favorite Group', self.mCommander ).SetProp( self.mEpgFavGroup )
					self.SetListControl( )

		elif selectedId == E_PARENTAL and self.mVisibleParental == False and groupId == E_Input01 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( MR_LANG( 'Enter PIN Code' ), '', 4, True )
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
			dialog.SetDialogProperty( MR_LANG( 'Enter New PIN Code' ), '', 4, True )
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
			dialog.SetDialogProperty( MR_LANG( 'Confirm PIN Code' ), '', 4, True )
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
			dialog.SetDialogProperty( MR_LANG( 'Change PIN Code' ), MR_LANG( 'Your PIN code has been changed successfully' ) )
 			dialog.doModal( )

 		elif selectedId == E_FACTORY_RESET and groupId == E_Input01 :
	 		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Performing a system reset?' ), MR_LANG( 'All channels and configuration settings%s including antenna will be lost' ) % NEW_LINE )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.mCommander.Player_SetMute( True )
				self.mProgressThread = self.ShowProgress( '%s%s' % ( MR_LANG( 'Now restoring' ), ING ), 30 )
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
	 			from elisinterface.ElisProperty import ResetHash
				ResetHash( )
				self.mDataCache.SetDefaultByFactoryReset( )
				globalEvent = pvr.GlobalEvent.GetInstance( )
				globalEvent.SendLocalOffsetToXBMC( )
				self.mInitialized = False
				self.mVideoOutput = E_VIDEO_HDMI
				self.ResetAllControl( )
				self.StopCheckNetworkTimer( )
				self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( '' )
				self.SetDefaultVolume( )
				self.CloseProgress( )
				self.mDataCache.Channel_TuneDefault( False )
				NetMgr.GetInstance( ).SetIsConfigureWindow( False )
				#WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_FIRST_INSTALLATION, WinMgr.WIN_ID_MAINMENU )
				ElisPropertyEnum( 'First Installation', self.mCommander ).SetProp( 0x2b )
				#dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				#dialog.SetDialogProperty( MR_LANG( 'Restart Required' ), MR_LANG( 'Your system must be restarted%s in order to complete the system reset' ) % NEW_LINE )
				#dialog.doModal( )
				mHead = MR_LANG( 'Please wait' )
				mLine = MR_LANG( 'System is restarting' ) + '...'
				xbmc.executebuiltin( 'Notification( %s, %s, 3000, DefaultIconInfo.png )'% ( mHead, mLine ) )
				time.sleep( 2 )
	 			xbmc.executebuiltin( "Custom.SetLanguage(%s,onlyxml)" % GetPropLanguageToXBMCLanguage( ElisPropertyEnum( 'Language', self.mCommander ).GetProp( ) ) )
				self.mDataCache.System_Reboot( )

		elif selectedId == E_FACTORY_RESET and groupId == E_Input02 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Performing a XBMC reset?' ), MR_LANG( 'All your XBMC addons and userdata will be lost' ) )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				isDownload = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_SYSTEM_UPDATE ).GetStatusFromFirmware( )
				if isDownload :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Try again after completing firmware update' ) )
					dialog.doModal( )
					return

				#dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				#dialog.SetDialogProperty( MR_LANG( 'Restart Required' ), MR_LANG( 'Your system must be restarted%s in order to complete the XBMC reset' ) % NEW_LINE )
				#dialog.doModal( )
				mHead = MR_LANG( 'Please wait' )
				mLine = MR_LANG( 'System is restarting' ) + '...'
				xbmc.executebuiltin( 'Notification( %s, %s, 3000, DefaultIconInfo.png )'% ( mHead, mLine ) )
				time.sleep( 1.5 )
				#ElisPropertyEnum( 'Language', self.mCommander ).SetProp( ElisEnum.E_ENGLISH )
	 			os.system( 'touch /config/resetXBMC' )
	 			self.mDataCache.System_Reboot( )

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
						self.mProgressThread = self.ShowProgress( '%s%s'% ( MR_LANG( 'Formatting HDD' ), ING ), 120 )
						self.mCommander.Format_Media_Archive( )
						self.CloseProgress( )

				elif groupId == E_Input02 :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
					dialog.SetDialogProperty( MR_LANG( 'WARNING' ), MR_LANG( 'Formatting recording partition%s cannot be undone!' )% NEW_LINE )
					dialog.doModal( )
					if dialog.IsOK( ) == E_DIALOG_STATE_YES :
						self.mProgressThread = self.ShowProgress( '%s%s'% ( MR_LANG( 'Formatting HDD' ), ING ), 60 )
						self.mCommander.Format_Record_Archive( )
						self.CloseProgress( )

				elif groupId == E_Input03 :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
					dialog.SetDialogProperty( MR_LANG( 'Format your hard disk drive?' ), MR_LANG( 'Everything on your hard drive will be erased' ) )
					dialog.doModal( )
					if dialog.IsOK( ) == E_DIALOG_STATE_YES :
						self.DedicatedFormat( )

			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Could not find a hard drive' ) )
	 			dialog.doModal( )

		elif selectedId == E_RECORDING_OPTION :
			if groupId == E_Input01 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_MOUNT_MANAGER )
				dialog.doModal( )
				defVolume = dialog.GetDefaultVolume( )
				self.mNetVolumeList = dialog.GetNetworkVolumes( )
				lblSelect, useInfo, lblPercent, lblOnline = self.GetVolumeInfo( defVolume )
				self.SetControlLabel2String( E_Input02, lblSelect )
				self.setProperty( 'NetVolumeConnect', lblOnline )
				self.setProperty( 'NetVolumeUse', lblPercent )
				self.getControl( E_PROGRESS_NETVOLUME ).setPercent( useInfo )
				ResetPositionVolumeInfo( self, lblPercent, 815, E_GROUP_ID_SHOW_INFO, E_LABEL_ID_USE_INFO )

				defProperty = 0
				defVolumeIdx = 99
				selectEnable = False
				if self.mNetVolumeList and len( self.mNetVolumeList ) > 0 :
					selectEnable = True
					if defVolume and defVolume.mOnline and ( not defVolume.mReadOnly ) :
						idxCount = 0
						for netVolume in self.mNetVolumeList :
							if netVolume.mIndexID == defVolume.mIndexID :
								defProperty = 1
								defVolumeIdx = idxCount
								break

							idxCount += 1

					else :
						ElisPropertyEnum( 'Record Default Path Change', self.mCommander ).SetProp( 0 )
						LOG_TRACE( '[Configure] changed default HDD, default volume is Not online or readonly' )

				# 1. change defvolume from manager(edited,deleted)
				if self.mSelectVolume != defVolumeIdx :
					self.mSelectVolume = defVolumeIdx
					ElisPropertyEnum( 'Record Default Path Change', self.mCommander ).SetProp( defProperty )
					#LOG_TRACE( '[Configure] defProperty[%s]'% defProperty )

				enableControlIds = [E_Input02, E_Input03]
				self.SetEnableControls( enableControlIds, selectEnable )


			elif groupId == E_Input02 :
				self.ShowNetworkVolume( )

			elif groupId == E_Input03 :
				self.RefreshByVolumeList( )

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


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			if aEvent.getName( ) == ElisEventUSBNotifyDetach.getName( ) or \
			   aEvent.getName( ) == ElisEventUSBNotifyAttach.getName( ) :
				if E_SUPPORT_EXTEND_RECORD_PATH :
					if self.mCtrlLeftGroup.getSelectedPosition( ) == E_RECORDING_OPTION :
						self.SetListControl( )
					else :
						self.mNetVolumeList = self.mDataCache.Record_GetNetworkVolume( )


	def ShowHdmiFormat( self ) :
		hdmiList = []
		selectIdx = ElisPropertyEnum( 'HDMI Format', self.mCommander ).GetPropIndex( )
		propCount = ElisPropertyEnum( 'HDMI Format', self.mCommander ).GetIndexCount( )
		for i in range( propCount ) :
			propName = ElisPropertyEnum( 'HDMI Format', self.mCommander ).GetPropStringByIndex( i )
			hdmiList.append( ContextItem( propName, i ) )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( hdmiList, selectIdx )
		dialog.doModal( )

		selectAction = dialog.GetSelectedAction( )
		#LOG_TRACE( '------select hdmi[%s] name[%s]'% ( selectAction, hdmiList[selectAction].mDescription ) )

		if selectAction > -1 :
			ElisPropertyEnum( 'HDMI Format', self.mCommander ).SetPropIndex( selectAction )
			self.SetControlLabel2String( E_Input01, hdmiList[selectAction].mDescription )

			time.sleep(1)
			self.VideoRestore( selectIdx, hdmiList[selectIdx].mDescription )
			DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).PIP_SetPositionSync( True )


	def VideoRestore( self, aRestoreIdx, aRestoreValue ) :
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_VIDEO_RESTORE )
		dialog.doModal( )

		if dialog.IsOK( ) != E_DIALOG_STATE_YES :
			ElisPropertyEnum( 'HDMI Format', self.mCommander ).SetPropIndex( aRestoreIdx )
			self.SetControlLabel2String( E_Input01, aRestoreValue )

		self.mDataCache.Frontdisplay_ResolutionByIdentified( )


	def GetVolumeInfo( self, aNetVolume = None ) :
		lblSelect = MR_LANG( 'None' )
		lblOnline = E_TAG_FALSE
		useFree   = self.mFreeHDD
		useTotal  = self.mTotalHDD
		useInfo   = 0
		if self.mHDDStatus :
			lblSelect = MR_LANG( 'HDD' )
			lblOnline = E_TAG_TRUE

		if aNetVolume :
			lblOnline = E_TAG_FALSE
			lblSelect = os.path.basename( aNetVolume.mMountPath )
			if aNetVolume.mOnline :
				lblOnline = E_TAG_TRUE
			useFree = aNetVolume.mFreeMB
			if aNetVolume.mTotalMB > 0 :
				useTotal = aNetVolume.mTotalMB

		else :
			#hdd not
			if useTotal < 1 :
				lblOnline = E_TAG_FALSE

		if useTotal > 0 :
			useInfo = int( ( ( 1.0 * ( useTotal - useFree ) ) / useTotal ) * 100 )

		lblByte = '%sMB'% useFree
		if useFree > 1024 :
			lblByte = '%sGB'% ( useFree / 1024 )
		elif useFree < 0 :
			lblByte = '%sKB'% ( useFree * 1024 )
		lblPercent = '%s%%, %s %s'% ( useInfo, lblByte, MR_LANG( 'Free' ) )

		isShowVolumeInfo = E_TAG_TRUE
		if not self.mHDDStatus and ( not aNetVolume ) :
			isShowVolumeInfo = E_TAG_FALSE
		self.setProperty( 'NetVolumeInfo', isShowVolumeInfo )

		return lblSelect, useInfo, lblPercent, lblOnline


	def GetVolumeContext( self, aVolumeID = -1 ) :
		trackList = []
		if self.mHDDStatus :
			trackList.append( ContextItem( MR_LANG( 'Internal HDD' ), 99 ) )

		trackIndex = 0
		if self.mNetVolumeList and len( self.mNetVolumeList ) > 0 :
			for netVolume in self.mNetVolumeList :
				getPath = netVolume.mRemoteFullPath
				urlType = urlparse.urlparse( getPath ).scheme
				urlHost, urlPort, urlUser, urlPass, urlPath, urlFile, urlSize = GetParseUrl( getPath )
				lblStatus = ''
				lblType = 'local'
				if urlType :
					lblType = '%s'% urlType.upper()
				else :
					if netVolume.mMountPath and bool( re.search( '%s\w\d+'% E_DEFAULT_PATH_USB_POSITION, netVolume.mMountPath, re.IGNORECASE ) ) :
						lblType = 'USB'

				if not netVolume.mOnline :
					lblStatus = '-%s'% MR_LANG( 'Disconnected' )
				if netVolume.mReadOnly :
					lblStatus = '-%s'% MR_LANG( 'Read only' )

				#lblPath = '[%s]%s%s'% ( lblType, urlHost, os.path.dirname( urlPath ) )
				lblPath = '[%s]%s%s'% ( lblType, os.path.basename( netVolume.mMountPath ), lblStatus )
				if lblStatus :
					lblPath = '[COLOR ff2E2E2E]%s[/COLOR]'% lblPath
				#LOG_TRACE('mountPath idx[%s] urlType[%s] mRemotePath[%s] mMountPath[%s] isDefault[%s]'% ( trackIndex, urlType, netVolume.mRemotePath, netVolume.mMountPath, netVolume.mIsDefaultSet ) )

				if aVolumeID > -1 :
					if netVolume.mIndexID == aVolumeID :
						self.mSelectVolume = trackIndex
						LOG_TRACE( '[ManaulTimer] Edit Timer, get volumeID[%s]'% aVolumeID )
				else :
					if netVolume.mIsDefaultSet :
						LOG_TRACE( '[ManaulTimer] find Default volume, mnt[%s]'% netVolume.mMountPath )

				trackList.append( ContextItem( lblPath, trackIndex ) )
				trackIndex += 1

		else :
			self.mNetVolumeList = []
			LOG_TRACE( 'Record_GetNetworkVolume none' )

		return trackList


	def ShowNetworkVolume( self ) :
		trackList = self.GetVolumeContext( )
		if not trackList or len( trackList ) < 1 :
			LOG_TRACE( '[ManaulTimer] Nothing in the mount list' )
			return

		selectedIdx = 0
		if self.mHDDStatus and self.mSelectVolume != 99 :
			selectedIdx = self.mSelectVolume + 1
		else :
			selectedIdx = self.mSelectVolume

		if selectedIdx < 0 :
			selectedIdx = 0

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( trackList, selectedIdx )
		dialog.doModal( )

		selectAction = dialog.GetSelectedAction( )
		if selectAction < 0 :
			LOG_TRACE( '[Configure] cancel, previous back' )
			return

		if selectAction == self.mSelectVolume :
			LOG_TRACE( '[Configure] pass, select same' )
			return


		defVolume = None
		defProperty = 0 #E_DEFAULT_PATH_INTERNAL_HDD
		if selectAction == 99 :
			if self.mNetVolumeList and len( self.mNetVolumeList ) > 0 :
				for netVolume in self.mNetVolumeList :
					if netVolume.mIsDefaultSet :
						netVolume.mIsDefaultSet = 0
						self.mDataCache.Record_SetDefaultVolume( netVolume )
						LOG_TRACE( '[Configure] clear default volume[%s]'% netVolume.mMountPath )
						break
		elif selectAction < len( self.mNetVolumeList ) :
			netVolume = self.mNetVolumeList[selectAction]
			if not netVolume.mOnline or netVolume.mReadOnly :
				lblLine = MR_LANG( 'Read only folder' )
				if not netVolume.mOnline :
					lblLine = MR_LANG( 'Inaccessible folder' )

				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), lblLine )
				dialog.doModal( )
				return

			defVolume = deepcopy( netVolume )
			defVolume.mIsDefaultSet = 1
			defProperty = 1 #E_DEFAULT_PATH_NETWORK_VOLUME
			self.mDataCache.Record_SetDefaultVolume( defVolume )
			LOG_TRACE( '[Configure] changed default volume[%s]'% defVolume.mMountPath )

		self.mSelectVolume = selectAction
		self.mNetVolumeList = self.mDataCache.Record_GetNetworkVolume( )
		ElisPropertyEnum( 'Record Default Path Change', self.mCommander ).SetProp( defProperty )

		lblSelect, useInfo, lblPercent, lblOnline = self.GetVolumeInfo( defVolume )
		self.SetControlLabel2String( E_Input02, lblSelect )
		self.setProperty( 'NetVolumeConnect', lblOnline )
		self.setProperty( 'NetVolumeUse', lblPercent )
		self.getControl( E_PROGRESS_NETVOLUME ).setPercent( useInfo )
		ResetPositionVolumeInfo( self, lblPercent, 815, E_GROUP_ID_SHOW_INFO, E_LABEL_ID_USE_INFO )


	def RefreshByVolumeList( self ) :
		volumeList = self.mDataCache.Record_GetNetworkVolume( )
		if not volumeList or len( volumeList ) < 1 :
			LOG_TRACE( '[MountManager] passed, volume list None' )
			return

		xbmc.executebuiltin( 'ActivateWindow(busydialog)' )

		RemoveDirectory( E_DEFAULT_NETWORK_VOLUME_SHELL )
		volumeCount = len( volumeList )
		defVolume = None
		count = 0
		failCount = 0
		failItem = ''
		os.system( 'echo \"#!/bin/sh\" >> %s'% E_DEFAULT_NETWORK_VOLUME_SHELL  )
		for netVolume in self.mNetVolumeList :
			os.system( 'echo \"/bin/umount -fl %s\" >> %s'% ( netVolume.mMountPath, E_DEFAULT_NETWORK_VOLUME_SHELL ) )
		os.system( 'echo \"rm -rf %s; mkdir -p %s\" >> %s'% ( E_DEFAULT_PATH_SMB_POSITION, E_DEFAULT_PATH_SMB_POSITION, E_DEFAULT_NETWORK_VOLUME_SHELL ) )
		os.system( 'echo \"rm -rf %s; mkdir -p %s\" >> %s'% ( E_DEFAULT_PATH_NFS_POSITION, E_DEFAULT_PATH_NFS_POSITION, E_DEFAULT_NETWORK_VOLUME_SHELL ) )
		os.system( 'echo \"rm -rf %s; mkdir -p %s\" >> %s'% ( E_DEFAULT_PATH_FTP_POSITION, E_DEFAULT_PATH_FTP_POSITION, E_DEFAULT_NETWORK_VOLUME_SHELL ) )

		self.SetControlLabelString( E_Input03, '' )
		self.setProperty( 'NetVolumeInfo', E_TAG_FALSE )
		for netVolume in volumeList :
			count += 1
			cmd = netVolume.mMountCmd
			lblRet = MR_LANG( 'OK' )
			lblLabel = '[%s/%s]%s'% ( count, volumeCount, os.path.basename( netVolume.mMountPath ) )
			if netVolume.mIsDefaultSet :
				defVolume = netVolume
			self.SetControlLabel2String( E_Input03, lblLabel )

			mntHistory = ExecuteShell( 'mount' )
			if mntHistory and ( not bool( re.search( '%s'% netVolume.mMountPath, mntHistory, re.IGNORECASE ) ) ) :
				RemoveDirectory( netVolume.mMountPath )

			if not mntHistory or ( not bool( re.search( '%s'% netVolume.mMountPath, mntHistory, re.IGNORECASE ) ) ) :
				mntPath = MountToSMB( netVolume.mRemoteFullPath, netVolume.mMountPath, False )
				if not mntPath :
					mntHistory = ExecuteShell( 'mount' )
					if not mntHistory or ( not bool( re.search( '%s'% netVolume.mMountPath, mntHistory, re.IGNORECASE ) ) ) :
						lblRet = MR_LANG( 'Fail' )
						failCount += 1
						failItem += '\n%s'% os.path.basename( netVolume.mMountPath )
						os.system( '/bin/umount -fl %s; rm -rf %s'% ( netVolume.mMountPath, netVolume.mMountPath ) )

			lblLabel = '%s%s'% ( lblRet, lblLabel )
			self.SetControlLabel2String( E_Input03, lblLabel )
			os.system( 'echo \"mkdir -p %s\" >> %s'% ( netVolume.mMountPath, E_DEFAULT_NETWORK_VOLUME_SHELL ) )
			os.system( 'echo \"%s\" >> %s'% ( cmd, E_DEFAULT_NETWORK_VOLUME_SHELL ) )
			os.system( 'sync' )
			time.sleep( 1 )

		os.system( 'chmod 755 %s'% E_DEFAULT_NETWORK_VOLUME_SHELL )
		os.system( 'sync' )
		xbmc.executebuiltin( 'Dialog.Close(busydialog)' )
		self.SetControlLabelString( E_Input03, MR_LANG( 'Refresh Record Path' ) )
		self.SetControlLabel2String( E_Input03, '' )

		lblSelect, useInfo, lblPercent, lblOnline = self.GetVolumeInfo( defVolume )
		self.SetControlLabel2String( E_Input02, lblSelect )
		self.setProperty( 'NetVolumeConnect', lblOnline )
		self.setProperty( 'NetVolumeUse', lblPercent )
		self.getControl( E_PROGRESS_NETVOLUME ).setPercent( useInfo )
		#self.setProperty( 'NetVolumeInfo', E_TAG_TRUE )
		ResetPositionVolumeInfo( self, lblPercent, 815, E_GROUP_ID_SHOW_INFO, E_LABEL_ID_USE_INFO )
		self.mDataCache.Record_RefreshNetworkVolume( )

		if failCount :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Fail' ), failItem[1:] )
			dialog.doModal( )


	def SetListControl( self ) :
		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( False )
		self.ResetAllControl( )
		self.WaitInitialize( )
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		self.setProperty( 'NetVolumeInfo', E_TAG_FALSE )

		if selectedId == E_LANGUAGE :
			self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddInputControl( E_Input01, MR_LANG( 'Menu Language' ), XBMC_GetCurrentLanguage( ), MR_LANG( 'Select the language you want the menu to be in' ) )
			self.AddInputControl( E_Input02, MR_LANG( 'Audio Language' ), self.mAudioLanguageList[ ElisPropertyEnum( 'Audio Language', self.mCommander ).GetPropIndex( ) ], MR_LANG( 'Select the language that you wish to listen to' ) )
			self.AddInputControl( E_Input03, MR_LANG( 'Subtitle Language' ), self.mSubtitleLanguageList[ ElisPropertyEnum( 'Subtitle Language', self.mCommander ).GetPropIndex( ) ], MR_LANG( 'Select the language for the subtitle to be in' ) )
			self.AddInputControl( E_Input04, MR_LANG( 'Secondary Subtitle Language' ), self.mSubtitleLanguageList_S[ ElisPropertyEnum( 'Secondary Subtitle Language', self.mCommander ).GetPropIndex( ) ], MR_LANG( 'Select the language for the secondary subtitle to be in' ) )
			self.AddEnumControl( E_SpinEx01, 'Hearing Impaired', None, MR_LANG( 'Set the hearing impaired function' ) )

			visibleControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_SpinEx01 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			self.WaitInitialize( )
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

			hideControlIds = [ E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			self.WaitInitialize( )
			self.DisableControl( E_PARENTAL )

		elif selectedId == E_RECORDING_OPTION :
			self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			if pvr.Platform.GetPlatform( ).GetProduct( ) != PRODUCT_OSCAR :
				self.AddEnumControl( E_SpinEx01, 'Automatic Timeshift', None, MR_LANG( 'When set to \'On\', your PRISMCUBE RUBY automatically start a timeshift recording when a different channel is selected' ) )
				self.AddEnumControl( E_SpinEx02, 'Timeshift Buffer Size', None, MR_LANG( 'Select the preferred size of timeshift buffer' ) )				
			self.AddEnumControl( E_SpinEx03, 'Default Rec Duration', None, MR_LANG( 'Select recording duration for a channel that has no EPG info' ) )
			self.AddEnumControl( E_SpinEx04, 'Pre-Rec Time', None, MR_LANG( 'Set the pre-recording time for a EPG channel' ) )
			self.AddEnumControl( E_SpinEx05, 'Post-Rec Time', None, MR_LANG( 'Set the post-recording time for a EPG channel' ) )

			if pvr.Platform.GetPlatform( ).GetProduct( ) != PRODUCT_OSCAR :
				visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05 ]
				hideControlIds = [ E_SpinEx06, E_SpinEx07, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			else :
				visibleControlIds = [ E_SpinEx03, E_SpinEx04, E_SpinEx05 ]
				hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx06, E_SpinEx07, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]

			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			if E_SUPPORT_EXTEND_RECORD_PATH :
				#ToDO : default path, get mount path
				self.mFreeHDD  = 0
				self.mTotalHDD = 0
				self.mSelectVolume = -1
				defaultPath = MR_LANG( 'None' )
				self.mHDDStatus = CheckHdd( )
				if self.mHDDStatus :
					self.mTotalHDD = self.mCommander.Record_GetPartitionSize( )
					self.mFreeHDD  = self.mCommander.Record_GetFreeMBSize( )
					self.mSelectVolume = 99
					defaultPath = MR_LANG( 'HDD' )

				defVolume = None
				disableControlIds = [ E_Input02, E_Input03 ]
				self.mNetVolumeList = self.mDataCache.Record_GetNetworkVolume( )
				if self.mNetVolumeList and len( self.mNetVolumeList ) > 0 :
					disableControlIds = []
					idxCount = 0
					for netVolume in self.mNetVolumeList :
						LOG_TRACE( '[Configure] idxCount[%s] volume[%s] isDefault[%s]'% ( idxCount, netVolume.mMountPath, netVolume.mIsDefaultSet ) )
						if netVolume.mIsDefaultSet :
							if not netVolume.mOnline or netVolume.mReadOnly :
								ElisPropertyEnum( 'Record Default Path Change', self.mCommander ).SetProp( 0 )
								LOG_TRACE( '[Configure] changed default HDD, default volume is Not online or readonly' )
							else :
								defaultPath = os.path.basename( netVolume.mMountPath )
								defVolume = netVolume
								self.mSelectVolume = idxCount
								break
						idxCount += 1

				self.AddInputControl( E_Input01, MR_LANG( 'Add/Remove Record Path' ), '', MR_LANG( 'Add or remove a record storage location' ) )
				self.AddInputControl( E_Input02, MR_LANG( 'Current Record Path' ), defaultPath, MR_LANG( 'Select a directory where the recorded files will be stored' ) )
				self.AddInputControl( E_Input03, MR_LANG( 'Refresh Record Path' ), '', MR_LANG( 'Remount your record storage directory' ) )
				visibleControlIds = [ E_Input01, E_Input02, E_Input03 ]
				hideControlIds.remove( E_Input01 )
				hideControlIds.remove( E_Input02 )
				hideControlIds.remove( E_Input03 )

				self.SetVisibleControls( visibleControlIds, True )
				self.SetEnableControls( visibleControlIds, True )
				time.sleep( 0.2 )
				if disableControlIds :
					self.SetEnableControls( disableControlIds, False )

				lblSelect, useInfo, lblPercent, lblOnline = self.GetVolumeInfo( defVolume )
				self.setProperty( 'NetVolumeConnect', lblOnline )
				self.setProperty( 'NetVolumeUse', lblPercent )
				self.getControl( E_PROGRESS_NETVOLUME ).setPercent( useInfo )
				ResetPositionVolumeInfo( self, lblPercent, 815, E_GROUP_ID_SHOW_INFO, E_LABEL_ID_USE_INFO )

				#self.setProperty( 'NetVolumeInfo', E_TAG_TRUE )

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

			hideControlIds = [ E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )

		elif selectedId == E_HDMI_SETTING :
			self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Video Output' ), USER_ENUM_LIST_VIDEO_OUTPUT, self.mVideoOutput, MR_LANG( 'Select HDMI or Analog for your video output' ) )
			
			if self.mVideoOutput == E_VIDEO_HDMI :
				lblSelect = ElisPropertyEnum( 'HDMI Format', self.mCommander ).GetPropString( )
				self.AddInputControl( E_Input01, 'HDMI Format', lblSelect, MR_LANG( 'Set the display\'s HDMI resolution' ) )
				self.AddEnumControl( E_SpinEx03, 'Show 4:3', MR_LANG( ' - TV Screen Format' ), MR_LANG( 'Select the display format for TV screen' ) )
				self.AddEnumControl( E_SpinEx04, 'HDMI Color Space', MR_LANG( ' - HDMI Color Space' ), MR_LANG( 'Set RGB or YUV for HDMI color space' ) )

				visibleControlIds = [ E_SpinEx01, E_Input01, E_SpinEx03, E_SpinEx04 ]
				self.SetVisibleControls( visibleControlIds, True )
				self.SetEnableControls( visibleControlIds, True )

				hideControlIds = [ E_SpinEx02, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
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

				hideControlIds = [ E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
				self.SetVisibleControls( hideControlIds, False )

				self.InitControl( )

		elif selectedId == E_NETWORK_SETTING :
			if self.mPlatform.IsPrismCube( ) :
				if self.mUseNetworkType == NETWORK_WIRELESS :
					self.LoadWifiInformation( )
					self.AddUserEnumControl( E_SpinEx05, MR_LANG( 'Network Connection' ), USER_ENUM_LIST_NETWORK_TYPE, self.mUseNetworkType, MR_LANG( 'Select Ethernet or wireless for your network connection' ) )
					self.AddInputControl( E_Input07, MR_LANG( 'Network Link' ), self.mStateNetLink, MR_LANG( 'Show network link status' ) )
					self.AddInputControl( E_Input01, MR_LANG( 'Search Wifi' ), self.mCurrentSsid, MR_LANG( 'Search for available wireless connections' ) )
					self.AddInputControl( E_Input02, MR_LANG( 'IP Address' ), self.mWifiAddress )
					self.AddInputControl( E_Input03, MR_LANG( 'Subnet Mask' ), self.mWifiSubnet )
					self.AddInputControl( E_Input04, MR_LANG( 'Gateway' ), self.mWifiGateway )
					self.AddInputControl( E_Input05, MR_LANG( 'DNS' ), self.mWifiDns )
					self.AddInputControl( E_Input06, MR_LANG( 'Manual Wifi Setup' ), '', MR_LANG( 'Press OK button to setup wireless network manually' ) )

					visibleControlIds = [ E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input07, E_Input06 ]
					self.SetVisibleControls( visibleControlIds, True )
					self.SetEnableControls( visibleControlIds, True )

					hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx06, E_SpinEx07 ]
					self.SetVisibleControls( hideControlIds, False )
					
					self.InitControl( )
					self.WaitInitialize( )
					self.DisableControl( E_WIFI )
				else :
					if self.mReLoadEthernetInformation == True :
						self.LoadEthernetInformation( )
						self.mReLoadEthernetInformation = False

					self.AddUserEnumControl( E_SpinEx05, MR_LANG( 'Network Connection' ), USER_ENUM_LIST_NETWORK_TYPE, self.mUseNetworkType, MR_LANG( 'Select Ethernet or wireless for your network connection' ) )
					self.AddInputControl( E_Input07, MR_LANG( 'Network Link' ), self.mStateNetLink, MR_LANG( 'Show network link status' ) )
					self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Assign IP Address' ), USER_ENUM_LIST_DHCP_STATIC, self.mEthernetConnectMethod, MR_LANG( 'When set to \'DHCP\', your IP address will be automatically allocated by the DHCP server' ) )
					self.AddInputControl( E_Input01, MR_LANG( 'IP Address' ), self.mEthernetIpAddress, MR_LANG( 'Enter your IP address' ) )
					self.AddInputControl( E_Input02, MR_LANG( 'Subnet Mask' ), self.mEthernetNetmask, MR_LANG( 'Enter your subnet mask' ) )
					self.AddInputControl( E_Input03, MR_LANG( 'Gateway' ), self.mEthernetGateway, MR_LANG( 'Enter your gateway' ) )
					self.AddInputControl( E_Input04, MR_LANG( 'DNS' ), self.mEthernetNamesServer, MR_LANG( 'Enter the DNS server address' ) )
					self.AddInputControl( E_Input05, MR_LANG( 'Apply') , '', MR_LANG( 'Press OK button to save the IP address settings' ) )

					visibleControlIds = [ E_SpinEx01, E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input07 ]
					self.SetVisibleControls( visibleControlIds, True )
					self.SetEnableControls( visibleControlIds, True )

					hideControlIds = [ E_Input06, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx06, E_SpinEx07 ]
					self.SetVisibleControls( hideControlIds, False )
					
					self.InitControl( )
					self.WaitInitialize( )
					self.DisableControl( E_ETHERNET )

				self.SetEnableControl( E_Input07, False )
				if self.GetGroupId( self.getFocusId( ) ) != E_SpinEx05 :
					self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )

			else :
				hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 , E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
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

			hideControlIds = [ E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			self.WaitInitialize( )
			self.DisableControl( E_TIME_SETTING )

		elif selectedId == E_EPG :
			self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )

			self.mEpgGrabinngTime = ElisPropertyInt( 'EPG Grabbing Time', self.mCommander ).GetProp( )
			self.mEpgFavGroup = ElisPropertyInt( 'Auto EPG Favorite Group', self.mCommander ).GetProp( )
			self.mEpgStartChannel = ElisPropertyInt( 'Auto EPG Start Channel', self.mCommander ).GetProp( )
			self.mEpgEndChannel = ElisPropertyInt( 'Auto EPG End Channel', self.mCommander ).GetProp( )
			groupName = MR_LANG( 'None' )

			zappingmode = self.mDataCache.Zappingmode_GetCurrent( )
			chCount = self.mDataCache.Channel_GetCount( zappingmode.mServiceType )
			if not chCount or chCount < 1 :
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
					if ElisPropertyInt( 'Auto EPG Favorite Group', self.mCommander ).GetProp( ) == 255 :
						groupName = MR_LANG( 'All' )
					else :
						if self.mEpgFavGroup >= len( favoriteGroup ) :
							self.mEpgFavGroup = 0
							ElisPropertyInt( 'Auto EPG Favorite Group', self.mCommander ).SetProp( 0 )
						groupName = favoriteGroup[ self.mEpgFavGroup ].mGroupName

				if self.mEpgStartChannel > chCount or self.mEpgEndChannel > chCount :
					self.mEpgStartChannel = 1
					self.mEpgEndChannel = 1
					ElisPropertyInt( 'Auto EPG Start Channel', self.mCommander ).SetProp( self.mEpgStartChannel )
					ElisPropertyInt( 'Auto EPG End Channel', self.mCommander ).SetProp( self.mEpgEndChannel )

			self.AddEnumControl( E_SpinEx01, 'Auto EPG', MR_LANG( 'Automatic EPG grabber' ), MR_LANG( 'When set to \'On\', the system automatically start to collect EPG data' ) )
			self.AddEnumControl( E_SpinEx02, 'EPG Grab Interval', MR_LANG( 'Grab Interval' ), MR_LANG( 'Adjust EPG scan interval for each channel' ) )
			self.AddEnumControl( E_SpinEx03, 'Auto EPG Channel', MR_LANG( 'Grab Mode' ), MR_LANG( 'Select which channels to grab EPG data from' ) )
			self.AddInputControl( E_Input01, MR_LANG( 'Start Time' ), '%02d:%02d' % ( ( self.mEpgGrabinngTime / 3600 ), ( self.mEpgGrabinngTime % 3600 / 60 ) ), MR_LANG( 'Set a starting time for EPG grabber' ) )
			self.AddInputControl( E_Input02, MR_LANG( 'Start and End Channel' ), '%s ~ %s'% ( self.mEpgStartChannel, self.mEpgEndChannel ) , MR_LANG( 'Select the channels for which you want to grab EPG data' ) )
			self.AddInputControl( E_Input03, MR_LANG( 'Favorite Group' ), groupName, MR_LANG( 'Select a favorite group for EPG grabbing' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input01, E_Input02, E_Input03 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			self.WaitInitialize( )
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

			hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )

		elif selectedId == E_FACTORY_RESET :
			self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddInputControl( E_Input01, MR_LANG( 'Reset System Configuration'), '', MR_LANG( 'Restore all settings and data to factory default (excluding XBMC)' ) )
			self.AddInputControl( E_Input02, MR_LANG( 'Reset XBMC Settings'), '', MR_LANG( 'Delete all your XBMC addons and settings' ) )

			visibleControlIds = [ E_Input01, E_Input02 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 , E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )

		elif selectedId == E_ETC :
			self.getControl( E_CONFIGURE_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddEnumControl( E_SpinEx01, 'Deep Standby', None, MR_LANG( 'When set to \'On\', the system switches to deep standby mode if you press \'Standby\' button to help reduce the amount of electricity used' ) )
			self.AddEnumControl( E_SpinEx02, 'Power Save Mode', None, MR_LANG( 'Set the time for switching into standby mode when not being used' ) )
			if self.mPlatform.GetProduct( ) != PRODUCT_OSCAR :
				self.AddEnumControl( E_SpinEx03, 'Fan Control', None, MR_LANG( 'Adjust the fan speed level for your system' ) )
			self.AddEnumControl( E_SpinEx04, 'Channel Banner Duration', MR_LANG( 'Channel Banner Time' ), MR_LANG( 'Set the time for the channel info to be displayed when zapping' ) )		#	Erase channel list yes/no
			self.AddEnumControl( E_SpinEx05, 'Playback Banner Duration', MR_LANG( 'Playback Banner Time' ), MR_LANG( 'Set the time for the playback info to be displayed on the screen' ) )	#	Erase custom menu yes/no
			if self.mPlatform.GetProduct( ) != PRODUCT_OSCAR :
				self.AddEnumControl( E_SpinEx06, 'HDD Sleep Mode', MR_LANG( 'HDD Sleep Mode' ), MR_LANG( 'When set to \'On\', the hard drive is turned off when the system goes into active standby mode' ) )
			if E_V1_1_UPDATE_NOTIFY :
				self.AddUserEnumControl( E_SpinEx07, MR_LANG( 'Update Notification' ), USER_ENUM_LIST_UPDATE_NOTIFY, self.mUpdateNotify, MR_LANG( 'Adjust notification frequency for firmware update' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			self.SetVisibleControls( hideControlIds, False )

			if self.mPlatform.GetProduct( ) == PRODUCT_OSCAR :
				self.SetVisibleControl( E_SpinEx03, False )
				self.SetVisibleControl( E_SpinEx06, False )

			if not E_V1_1_UPDATE_NOTIFY :
				self.SetVisibleControl( E_SpinEx07, False )

			self.InitControl( )

		else :
			LOG_ERR( 'Could not find the selected ID' )

		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( True )


	def DisableControl( self, aSelectedItem ) :
		if aSelectedItem == E_LANGUAGE :
			#selectedIndex = self.GetSelectedIndex( E_SpinEx02 )
			subTitleValue = ElisPropertyEnum( 'Subtitle Language', self.mCommander ).GetProp( )
			visibleControlIds = [ E_Input04, E_SpinEx01 ]
			if subTitleValue == 0 :
				self.SetEnableControls( visibleControlIds, False )
				control = self.getControl( E_SpinEx01 + 3 )
				self.WaitInitialize( )
				control.selectItem( 0 )
				self.SetProp( E_SpinEx01, 0 )
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
					self.WaitInitialize( )
					localTimeOffsetControl.selectItem( ElisPropertyEnum( 'Local Time Offset', self.mCommander ).GetIndexByProp( 0 ) )
					summerTimeControl.selectItem( SUMMER_TIME_OFF )
					
					self.SetEnableControl( E_Input01, False )
					self.SetEnableControl( E_Input02, True )
					self.SetEnableControl( E_Input03, True )
					self.SetEnableControl( E_SpinEx02, False )
					self.SetEnableControl( E_SpinEx03, False )

		elif aSelectedItem == E_EPG :
			visiblecontrols = [ E_SpinEx02, E_SpinEx03, E_Input01, E_Input02, E_Input03 ]
			if self.GetSelectedIndex( E_SpinEx01 ) == 1 :
				self.SetEnableControls( visiblecontrols, False )
			else :
				self.SetEnableControls( visiblecontrols, True )

				selectedIndex = self.GetSelectedIndex( E_SpinEx03 )
				if selectedIndex == 0 :
					self.SetEnableControl( E_Input02, True )
					self.SetEnableControl( E_Input03, False )
				else :
					self.SetEnableControl( E_Input02, False )
					self.SetEnableControl( E_Input03, True )


	def NotifyFindPrismcubeCom( self, aIP ) :
		try :
			data = {'ip' : str( aIP ) }
			data = urlencode( data )
			f = urllib.urlopen("http://www.fwupdater.com/prismcube/index.html", data, 3)

		except Exception, err:
			LOG_TRACE( '[Find]' )
			LOG_TRACE( str(err) )


	def LoadEthernetInformation( self ) :
		self.mEthernetConnectMethod = NetMgr.GetInstance( ).GetEthernetMethod( )
		self.mEthernetIpAddress, self.mEthernetNetmask, self.mEthernetGateway, self.mEthernetNamesServer = NetMgr.GetInstance( ).GetNetworkAddress( NETWORK_ETHERNET )


	def ConnectEthernet( self ) :
		self.mProgressThread = self.ShowProgress( '%s%s'% ( MR_LANG( 'Now connecting' ), ING ), 20 )
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

			self.NotifyFindPrismcubeCom( self.mEthernetIpAddress )
			
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
			if E_SUPPORT_EXTEND_RECORD_PATH :
				netVolumeList = self.mDataCache.Record_GetNetworkVolume( True )
				if netVolumeList and len( netVolumeList ) > 0 :
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW ).DoRefreshNetVolume( True )


	def WifiSetting( self, aControlId ) :
		apList = []

		if aControlId == E_Input01 :
			self.mProgressThread = self.ShowProgress( '%s%s' % ( MR_LANG( 'Now searching' ), ING ), 30 )
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
				apNameList.append( ap[0] + MR_LANG( '    - Strength :%s, Encryption : %s' ) % ( ap[1], ap[2] ) )
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
					if E_SUPPORT_EXTEND_RECORD_PATH :
						netVolumeList = self.mDataCache.Record_GetNetworkVolume( True )
						if netVolumeList and len( netVolumeList ) > 0 :
							WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW ).DoRefreshNetVolume( True )


	def ConnectCurrentWifi( self ) :
		if self.mEncryptType != ENCRYPT_OPEN :
			dialog = xbmc.Keyboard( self.mPassWord, MR_LANG( 'Enter Encryption Key' ), True )
			dialog.setHiddenInput( True )
			dialog.doModal( )
			if( dialog.isConfirmed( ) ) :
				self.mPassWord = dialog.getText( )
				#self.mPassWord = InputKeyboard( E_INPUT_KEYBOARD_TYPE_HIDE, MR_LANG( 'Enter Encryption Key' ), self.mPassWord, 48 )
				if self.mEncryptType == ENCRYPT_TYPE_WPA and ( len( self.mPassWord ) < 8 or len( self.mPassWord ) > 64 ) :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'The password must be between 8 and 64 characters' ) )
					dialog.doModal( )
					return
				if self.mEncryptType == ENCRYPT_TYPE_WEP and  len( self.mPassWord ) < 5 :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'The password length is invalid' ) )
					dialog.doModal( )
					return
			else :
				return
	
		self.mProgressThread = self.ShowProgress( '%s%s'% ( MR_LANG( 'Now connecting' ), ING ), 30 )
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
				#self.LoadWifiAddress( )
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
			aIpAddr = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_IP, MR_LANG( 'Enter IP Address' ), '0.0.0.0' )
		else :
			aIpAddr = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_IP, MR_LANG( 'Enter IP Address' ), aIpAddr )
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
			self.mDate = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_DATE, MR_LANG( 'Enter Today\'s Date' ), self.mDate )
			self.SetControlLabel2String( E_Input02, self.mDate )

		elif aControlId == E_Input03 :
			self.mTime = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_TIME, MR_LANG( 'Enter Local Time' ), self.mTime )
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
				dialog.SetDialogProperty( 20, '%s%s'% ( MR_LANG( 'Setting Time' ), ING ), ElisEventTimeReceived.getName( ) )
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
		try :
			self.SetControlLabel2String( E_Input07, self.mStateNetLink )
		except Exception, e :
			LOG_ERR( 'Error exception[%s] : Bad timing access control' % e )


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
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Could not find backup data' ) )
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
		self.mProgressThread = self.ShowProgress( '%s%s'% ( MR_LANG( 'Now backing up your user data' ), ING ), 30 )
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
		maxsize = self.GetMaxMediaSize( )
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( MR_LANG( 'Maximum Partition Size' ), MR_LANG( 'Maximum media partition size' ) + ' : %s GB' % maxsize )
		dialog.doModal( )

		mediadefault = 100
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
		dialog.SetDialogProperty( MR_LANG( 'Enter Media Partition Size in GB' ), '%s' % mediadefault , 4 )
		dialog.doModal( )
		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			mediadefault = dialog.GetString( )

		if maxsize < int( mediadefault ) :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Partition size not valid' ) )
			dialog.doModal( )
			return

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( MR_LANG( 'Your Media Partition is %s GB' ) % mediadefault, MR_LANG( 'Start formatting HDD?' ) )
		dialog.doModal( )
		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			self.OpenBusyDialog( )
			ElisPropertyInt( 'MediaRepartitionSize', self.mCommander ).SetProp( int( mediadefault ) * 1024 )
			ElisPropertyEnum( 'HDDRepartition', self.mCommander ).SetProp( 1 )
			self.mDataCache.Player_AVBlank( True )
			if self.mUseUsbBackup :
				self.MakeBackupScript( )
				CreateDirectory( E_DEFAULT_BACKUP_PATH )
				os.system( 'touch %s/isUsbBackup' % E_DEFAULT_BACKUP_PATH )
			self.mCommander.Make_Dedicated_HDD( )


	def GetMaxMediaSize( self ) :
		try :
			size = 0
			device = '/dev/sda'
			cmd = "fdisk -ul %s | awk '/Disk/ {print $3,$4}'" % device
			if sys.version_info < ( 2, 7 ) :
				p = Popen( cmd, shell=True, stdout=PIPE )
				size = p.stdout.read( ).strip( )
				p.stdout.close( )
			else :
				p = Popen( cmd, shell=True, stdout=PIPE, close_fds=True )
				( size, err ) = p.communicate( )
				size = size.strip( )

			size = re.sub( ',', '', size )
			size = int( size.split( '.' )[0] )

			if size > HDD_RESERVED_USE :
				return size - HDD_RESERVED_USE
			else :
				return 0

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return 0


	def MakeBackupScript( self ) :
		try :
			scriptFile = '%s.sh' % E_DEFAULT_BACKUP_PATH
			fd = open( scriptFile, 'w' )
			if fd :
				fd.writelines( '#!/bin/sh\n' )
				#fd.writelines( 'modprobe usb_storage\n' )
				#fd.writelines( 'sleep 3\n' )
				#fd.writelines( 'mount /dev/sdb1 /media/usb/sdb1\n' )
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

		elif aGroupId == E_SpinEx07 :
			self.mUpdateNotify = self.GetSelectedIndex( E_SpinEx07 )
			SetSetting( 'UPDATE_NOTIFY', '%d' % self.mUpdateNotify )
			if self.mUpdateNotify == 1 :
				SetSetting( 'UPDATE_NOTIFY_COUNT', '0' )

		else :
			self.ControlSelect( )


	def ShowFavoriteGroup( self ) :
		zappingmode = self.mDataCache.Zappingmode_GetCurrent( )

		#check AllChannels
		chCount = self.mDataCache.Channel_GetCount( zappingmode.mServiceType )
		if not chCount or chCount < 1 :
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

		iFavGroup = ElisIFavoriteGroup( )
		iFavGroup.mGroupName = MR_LANG( 'All' )
		favoriteList = [ iFavGroup ]
		for iFavGroup in favoriteGroup :
			favoriteList.append( iFavGroup )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_GROUP )
		dialog.SetDefaultProperty( E_MODE_FAVORITE_GROUP, MR_LANG( 'Select Favorite Group' ), favoriteList, self.mEpgFavGroup + 1 )
		dialog.doModal( )

		isSelect = dialog.GetSelectedList( )
		if isSelect >= 0 :
			return isSelect
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
		ret = dialog.select( MR_LANG( 'Start Channel Number' ), channelList, False, 0 )
		if ret >= 0 :
			self.mEpgStartChannel = allChannels[ ret ].mNumber
		else :
			return
		ret = dialog.select( MR_LANG( 'End Channel Number' ), channelList, False, 0 )
		if ret >= 0 :
			self.mEpgEndChannel = allChannels[ ret ].mNumber
		else :
			return

		if self.mEpgStartChannel > self.mEpgEndChannel :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Invalid channel number' ) )
			dialog.doModal( )
			return

		ElisPropertyInt( 'Auto EPG Start Channel', self.mCommander ).SetProp( self.mEpgStartChannel )
		ElisPropertyInt( 'Auto EPG End Channel', self.mCommander ).SetProp( self.mEpgEndChannel )
		self.SetListControl( )


	def MakeLanguageList ( self ) :
		self.mAudioLanguageList		= []
		self.mSubtitleLanguageList	= []
		self.mSubtitleLanguageList_S	= []

		for i in range( ElisPropertyEnum( 'Audio Language', self.mCommander ).GetIndexCount( ) ) :
			self.mAudioLanguageList.append( ElisPropertyEnum( 'Audio Language', self.mCommander ).GetPropStringByIndex( i, False ) )
		for i in range( ElisPropertyEnum( 'Subtitle Language', self.mCommander ).GetIndexCount( ) ) :
			subtitle = ElisPropertyEnum( 'Subtitle Language', self.mCommander ).GetPropStringByIndex( i, False )
			if subtitle == 'Disable' :
				self.mSubtitleLanguageList.append( MR_LANG( 'Disable' ) )
			else :
				self.mSubtitleLanguageList.append( subtitle )
		for i in range( ElisPropertyEnum( 'Secondary Subtitle Language', self.mCommander ).GetIndexCount( ) ) :
			secondarySubtitle = ElisPropertyEnum( 'Secondary Subtitle Language', self.mCommander ).GetPropStringByIndex( i, False )
			if secondarySubtitle == 'Disable' :
				self.mSubtitleLanguageList_S.append( MR_LANG( 'Disable' ) )
			else :
				self.mSubtitleLanguageList_S.append( secondarySubtitle )


	def WaitInitialize( self ) :
		if self.mInitialized :
			time.sleep( 0.02 )
		else :
			time.sleep( 0.2 )

