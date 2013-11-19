from pvr.gui.WindowImport import *
from pvr.gui.FTIWindow import FTIWindow
from pvr.XBMCInterface import XBMC_SetSkinZoom
import pvr.ScanHelper as ScanHelper

E_FIRST_INSTALLATION_BASE_ID = WinMgr.WIN_ID_FIRST_INSTALLATION * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 


class FirstInstallation( FTIWindow ) :
	def __init__( self, *args, **kwargs ) :
		FTIWindow.__init__( self, *args, **kwargs )
		self.mPrevStepNum				= E_STEP_SELECT_LANGUAGE
		self.mAudioLanguageList			= []
		self.mIsChannelSearch			= True
		self.mConfiguredSatelliteList 	= []
		self.mFormattedList				= []
		self.mSatelliteIndex			= 0

		self.mDate						= 0
		self.mTime						= 0
		self.mSetupChannel				= None
		self.mHasChannel				= False

		self.mAsyncVideoSetThread		= None

		self.mStepImage					= []
		self.mBusyVideoSetting			= False
		self.mReloadSkinPosition		= False

		self.mIsManualSetup				= 0
		self.mSatelliteIndex			= 0
		self.mTransponderList			= []
		self.mTransponderIndex			= 0
		self.mConfigTransponder			= None
		self.mIsManualTp				= 0
		self.mIsReloadChannelSearchStep = False

		if ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( ) == E_ONE_CABLE :
			self.mTunerConnection		= E_TUNER_ONECABLE
			self.mTunerSignal			= E_SAMEWITH_TUNER
			self.mTuner1Control			= E_DISEQC_1_0
			self.mTuner2Control			= E_DISEQC_1_0
		else :
			self.mTunerConnection		= ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander ).GetProp( )
			self.mTunerSignal			= ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander ).GetProp( )
			self.mTuner1Control			= ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( )
			self.mTuner2Control			= ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).GetProp( )


	def onInit( self ) :
		self.SetActivate( True )
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.SetSingleWindowPosition( E_FIRST_INSTALLATION_BASE_ID )
		self.SetFrontdisplayMessage( MR_LANG('First Installation') )
		self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'Installation' ), MR_LANG( 'First Installation' ) ) )

		self.SetFirstInstallation( True )
		if self.mReloadSkinPosition :
			WinMgr.GetInstance( ).LoadSkinPosition( )
			self.mReloadSkinPosition = False

		self.SetPipScreen( )
		self.SetListControl( self.GetFTIStep( ) )
		
		if self.mDataCache.GetEmptySatelliteInfo( ) == True :
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( MR_LANG( 'No satellite data available' ) )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Please reset your device to factory settings' ) )
			dialog.doModal( )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Go to the configuration menu now?' ), MR_LANG( 'When you perform a factory reset,%s all your settings revert to factory defaults' )% NEW_LINE )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.SetVideoRestore( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIGURE, WinMgr.WIN_ID_MAINMENU )
			else :
				self.SetVideoRestore( )
				WinMgr.GetInstance( ).CloseWindow( )

		self.SetParentID( WinMgr.WIN_ID_MAINMENU )
		self.mInitialized = True


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return

		actionId = aAction.getId( )
		focusId = self.getFocusId( )

		self.GlobalSettingAction( self, actionId )
		
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			if self.GetFTIStep( ) == E_STEP_RESULT :
				return
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Exit Installation' ), MR_LANG( 'Are you sure you want to quit the first installation?' ), True )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.Close( )
			elif dialog.IsOK( ) == E_DIALOG_STATE_NO :
				return	
			elif dialog.IsOK( ) == E_DIALOG_STATE_CANCEL :
				return

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( self )

		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( self )


	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
		groupId = self.GetGroupId( aControlId )

		if self.GetFTIStep( ) == E_STEP_SELECT_LANGUAGE :
			if groupId == E_FIRST_TIME_INSTALLATION_NEXT :
				self.SetListControl( E_STEP_VIDEO_AUDIO )
			else :
				if groupId == E_Input01 :
					menuLanguageList = WinMgr.GetInstance( ).GetLanguageList( )
					dialog = xbmcgui.Dialog( )
					currentindex = StringToListIndex( menuLanguageList, self.GetControlLabel2String( E_Input01 ) )
					ret = dialog.select( MR_LANG( 'Select Menu Language' ), menuLanguageList, False, currentindex )
					if ret >= 0 :
						if not self.mPlatform.IsPrismCube( ) :
							dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
							dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No support %s' ) % self.mPlatform.GetName( ) )
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
							prop = GetXBMCLanguageToProp( menuLanguageList[ ret ] )
							ElisPropertyEnum( 'Language', self.mCommander ).SetProp( prop )
							self.mInitialized = False
							time.sleep( 0.5 )
							XBMC_SetCurrentLanguage( menuLanguageList[ ret ] )
						
				elif groupId == E_Input02 :
					dialog = xbmcgui.Dialog( )
					ret = dialog.select( MR_LANG( 'Select Audio Language' ), self.mAudioLanguageList, False, StringToListIndex( self.mAudioLanguageList, self.GetControlLabel2String( E_Input02 ) ) )
					if ret >= 0 :
						ElisPropertyEnum( 'Audio Language', self.mCommander ).SetPropIndex( ret )
						self.SetControlLabel2String( E_Input02, self.mAudioLanguageList[ ret ] )

		elif self.GetFTIStep( ) == E_STEP_VIDEO_AUDIO :
			if groupId == E_FIRST_TIME_INSTALLATION_NEXT :
				xbmc.executebuiltin( 'ActivateWindow(screencalibration)' )
				self.mReloadSkinPosition = True
				self.SetFTIStep( E_STEP_ANTENNA )
				self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( False )

			elif groupId == E_SpinEx03 :
				if self.mBusyVideoSetting :
					return
				if self.mAsyncVideoSetThread :
					self.mAsyncVideoSetThread.cancel( )
					self.mAsyncVideoSetThread = None

				self.mAsyncVideoSetThread = threading.Timer( 3, self.AsyncVideoSetting )
				self.mAsyncVideoSetThread.start( )

			elif groupId == E_SpinEx01 or groupId == E_SpinEx02 :
				self.ControlSelect( )

		elif self.GetFTIStep( ) == E_STEP_ANTENNA :
			if groupId == E_SpinEx01 :
				self.mTunerConnection = self.GetSelectedIndex( E_SpinEx01 )
				self.DisableControl( groupId )

			elif groupId == E_SpinEx02 :
				self.mTunerSignal = self.GetSelectedIndex( E_SpinEx02 )
				self.DisableControl( groupId )

			elif groupId == E_SpinEx03 :
				self.mTuner1Control = self.GetSelectedIndex( E_SpinEx03 )
				self.DisableControl( groupId )

			elif groupId == E_SpinEx04 :
				self.mTuner2Control = self.GetSelectedIndex( E_SpinEx04 )
				self.DisableControl( groupId )

			elif groupId == E_FIRST_TIME_INSTALLATION_NEXT :
				self.SetTunerProperty( )
				self.GotoAntennaNextStep( )

			elif groupId == E_FIRST_TIME_INSTALLATION_PREV :
				xbmc.executebuiltin( 'ActivateWindow(screencalibration)' )
				self.mReloadSkinPosition = True
				self.SetFTIStep( E_STEP_VIDEO_AUDIO )
				self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( False )
				return

		elif self.GetFTIStep( ) == E_STEP_CHANNEL_SEARCH_CONFIG :
			self.ChannelSearchConfig( groupId )

		elif self.GetFTIStep( ) == E_STEP_DATE_TIME :
			self.TimeSetting( groupId )

		elif self.GetFTIStep( ) == E_STEP_RESULT :
			if groupId == E_FIRST_TIME_INSTALLATION_NEXT :
				self.Close( )

		if groupId == E_FIRST_TIME_INSTALLATION_PREV :
			self.mEventBus.Deregister( self )
			self.OpenBusyDialog( )
			ScanHelper.GetInstance( ).ScanHelper_Stop( self )
			self.CloseBusyDialog( )
			self.SetListControl( self.mPrevStepNum )


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
		if self.mInitialized :
			self.ShowDescription( aControlId )


	def onEvent( self, aEvent ) :
		if xbmcgui.getCurrentWindowId( ) == self.mWinId and self.GetFTIStep( ) == E_STEP_CHANNEL_SEARCH_CONFIG :
			if aEvent.getName( ) == ElisEventTuningStatus.getName( ) :
				self.UpdateStatus( aEvent )


	def UpdateStatus( self, aEvent ) :
		if aEvent.mFrequency == self.mConfigTransponder.mFrequency :
			ScanHelper.GetInstance( ).ScanHerper_Progress( self, aEvent.mSignalStrength, aEvent.mSignalQuality, aEvent.mIsLocked )
			if aEvent.mIsLocked :
			#	if self.mDataCache.Get_Player_AVBlank( ) :
				self.mDataCache.Player_AVBlank( False )
			#else :
			#	if not self.mDataCache.Get_Player_AVBlank( ) :
			#		self.mDataCache.Player_AVBlank( True )


	def Close( self ) :
		self.SetVideoRestore( )
		self.OpenBusyDialog( )
		self.mInitialized = False
		self.SetFTIStep( E_STEP_SELECT_LANGUAGE )
		self.SetFirstInstallation( False )
		self.mTunerMgr.SetNeedLoad( True )
		self.mTunerMgr.SyncChannelBySatellite( )
		self.mDataCache.Channel_ReLoad( )
		if self.GetFTIStep( ) == E_STEP_ANTENNA :
			self.SetTunerProperty( )
			self.mTunerMgr.SaveConfiguration( )
			self.mDataCache.Channel_TuneDefault( )

		self.mEventBus.Deregister( self )
		ScanHelper.GetInstance( ).ScanHelper_Stop( self )
		self.CloseBusyDialog( )
		WinMgr.GetInstance( ).CloseWindow( )


	def SetListControl( self, aStep, aSetFocus=True ) :
		self.ResetAllControl( )
		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( False )
		
		self.SetFTIStep( aStep )
		self.DrawFTIStep( aStep )
		self.SetPrevNextButtonLabel( aStep )

		if aStep == E_STEP_SELECT_LANGUAGE :
			for i in range( ElisPropertyEnum( 'Audio Language', self.mCommander ).GetIndexCount( ) ) :
				self.mAudioLanguageList.append( ElisPropertyEnum( 'Audio Language', self.mCommander ).GetPropStringByIndex( i, False ) )
			self.mPrevStepNum = E_STEP_SELECT_LANGUAGE
			self.getControl( E_SETTING_HEADER_TITLE ).setLabel( MR_LANG( 'Language Setup' ) )
			self.AddInputControl( E_Input01, MR_LANG( 'Menu Language' ), XBMC_GetCurrentLanguage( ), MR_LANG( 'Select the language you want the menu to be in' ) )
			self.AddInputControl( E_Input02, MR_LANG( 'Audio Language' ), self.mAudioLanguageList[ ElisPropertyEnum( 'Audio Language', self.mCommander ).GetPropIndex( ) ], MR_LANG( 'Select the language that you wish to listen to' ) )
			self.AddNextButton( MR_LANG( 'Go to the video and audio setup page' ) )

			visibleControlIds = [ E_Input01, E_Input02 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			time.sleep( 0.2 )
			self.SetDefaultControl( )

		elif aStep == E_STEP_VIDEO_AUDIO :
			self.mPrevStepNum = E_STEP_SELECT_LANGUAGE
			self.getControl( E_SETTING_HEADER_TITLE ).setLabel( MR_LANG( 'Video and Audio Setup' ) )
			self.AddEnumControl( E_SpinEx01, 'Show 4:3', MR_LANG( 'TV Screen Format' ), MR_LANG( 'Select the display format for TV screen' ) )
			self.AddEnumControl( E_SpinEx02, 'Audio Dolby', MR_LANG('Dolby Audio'), MR_LANG( 'When set to \'On\', Dolby Digital audio will be selected automatically when broadcast' ) )
			self.AddEnumControl( E_SpinEx03, 'HDMI Format', None, MR_LANG( 'Select the display\'s HDMI resolution' ) )
			self.AddPrevNextButton( MR_LANG( 'Go to the antenna and satellite setup page' ), MR_LANG( 'Go back to the language setup page' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			time.sleep( 0.2 )
			self.SetDefaultControl( )

		elif aStep == E_STEP_ANTENNA :
			self.mPrevStepNum = E_STEP_VIDEO_AUDIO
			self.LoadTunerProperty( )
			connectTypeDescription = '%s %s' % ( MR_LANG( 'When set to \'Separated\', the tuner 2 receives its own signal input'), MR_LANG('however it will receive only the channel level currently being received by the tuner 1 when this is set to \'Loopthrough\'' ) )
			self.getControl( E_SETTING_HEADER_TITLE ).setLabel( MR_LANG( 'Antenna and Satellite Setup' ) )
			self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Tuner Connection' ), E_LIST_TUNER_CONNECTION, self.mTunerConnection, connectTypeDescription )
			self.AddUserEnumControl( E_SpinEx02, MR_LANG( 'Tuner 2 Signal' ), E_LIST_TUNER2_SIGNAL, self.mTunerSignal, MR_LANG( 'When set to \'Same with Tuner 1\', both tuners are connected to the same signal source' ) )
			self.AddUserEnumControl( E_SpinEx03, MR_LANG( 'Tuner 1 Control' ), E_LIST_TUNER_CONTROL, self.mTuner1Control, MR_LANG( 'Select a control method for tuner 1' ) )
			self.AddUserEnumControl( E_SpinEx04, MR_LANG( 'Tuner 2 Control' ), E_LIST_TUNER_CONTROL, self.mTuner2Control, MR_LANG( 'Select a control method for tuner 2' ) )
			self.AddPrevNextButton( MR_LANG( 'Go to the satellite configuration page' ), MR_LANG( 'Go back to the video and audio setup page' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			time.sleep( 0.2 )
			self.DisableControl( )
			self.SetDefaultControl( )
			
			if self.mTunerMgr.GetNeedLoad( ) == True :
				self.mTunerMgr.LoadOriginalTunerConfig( )
				self.mTunerMgr.Load( )
				self.mTunerMgr.SetNeedLoad( False )

		elif aStep == E_STEP_CHANNEL_SEARCH_CONFIG :
			self.mPrevStepNum = E_STEP_ANTENNA
			self.getControl( E_SETTING_HEADER_TITLE ).setLabel( MR_LANG( 'Channel Search Setup' ) )
			self.mIsManualTp = 0
			self.LoadFormattedSatelliteNameList( )
			self.LoadTransponderList( )
			self.SetConfigTransponder( )
			self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Channel Search' ), USER_ENUM_LIST_YES_NO, self.mIsChannelSearch, MR_LANG( 'Do you want to perform a channel search in the first installation?' ) )
			self.AddInputControl( E_Input01, MR_LANG( 'Satellite' ), self.mFormattedList[ self.mSatelliteIndex ], MR_LANG( 'Select the satellite on which the transponder you wish to scan is located' ) )			
			self.AddUserEnumControl( E_SpinEx02, MR_LANG( 'Manual Setup' ), USER_ENUM_LIST_ON_OFF, self.mIsManualSetup, MR_LANG( 'Enable/Disable Manual scan' ) )
			description = MR_LANG( 'Select or enter the transponder frequency for the selected satellite' )
			self.AddInputControl( E_Input02, MR_LANG( ' - Transponder Frequency' ), '%d MHz' % self.mConfigTransponder.mFrequency, description, aInputNumberType = TYPE_NUMBER_NORMAL, aMax = 13000 )
			self.AddEnumControl( E_SpinEx03, 'DVB Type', MR_LANG( ' - DVB Type' ), MR_LANG( 'Select the Digital Video Broadcasting type for the selected satellite' ) )

			if self.mConfigTransponder.mFECMode == ElisEnum.E_FEC_UNDEFINED :
				self.SetProp( E_SpinEx03, 0 )
			else :
				self.SetProp( E_SpinEx03, 1 )

			self.AddEnumControl( E_SpinEx04, 'FEC', MR_LANG( ' - FEC' ), MR_LANG( 'Select the error control mode of data transmission for the selected satellite' ) )
			self.SetProp( E_SpinEx04, self.mConfigTransponder.mFECMode )

			self.AddEnumControl( E_SpinEx05, 'Polarisation', MR_LANG( ' - Polarization' ), MR_LANG( 'Select the direction of the electrical and magnetic fields of signals for the satellite above' ) )
			self.SetProp( E_SpinEx05, self.mConfigTransponder.mPolarization )

			self.AddInputControl( E_Input03, MR_LANG( ' - Symbol Rate' ), '%d KS/s' % self.mConfigTransponder.mSymbolRate , MR_LANG( 'Set the amount of data, that is transmitted per second in the data stream' ), aInputNumberType = TYPE_NUMBER_NORMAL, aMax = 60000 )

			networkSearchDescription = '%s %s' % ( MR_LANG( 'When set to \'Off\', only the factory default transponders of the satellites you previously selected will be scanned for new channels.'), MR_LANG('If you set to \'On\', both the existing transponders and additional transponders that have not yet been stored to be located are scanned for new channels' ) )
			self.AddEnumControl( E_SpinEx06, 'Network Search', None, networkSearchDescription )
			self.AddEnumControl( E_SpinEx07, 'Channel Search Mode', MR_LANG( 'Search Type' ), MR_LANG( 'Select whether you wish to scan free and scrambled, free only or scrambled only' ) )
			self.AddPrevNextButton( MR_LANG( 'Go to the time and date setup page' ), MR_LANG( 'Go back to the antenna and satellite setup page' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input01, E_Input02, E_Input03 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_Input04, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			time.sleep( 0.2 )
			self.DisableControl( )
			if aSetFocus :
				self.SetDefaultControl( )

		elif aStep == E_STEP_DATE_TIME :
			self.mPrevStepNum = E_STEP_CHANNEL_SEARCH_CONFIG
			self.getControl( E_SETTING_HEADER_TITLE ).setLabel( MR_LANG( 'Time and Date Setup' ) )

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
					self.SetEnableControl( E_SpinEx02, False )
					self.SetEnableControl( E_SpinEx03, False )

			self.AddEnumControl( E_SpinEx01, 'Time Mode', MR_LANG( 'Time and Date' ), MR_LANG( 'When set to \'Automatic\', the time will be obtained by the receiver automatically from a specific channel that you select') )
			self.AddInputControl( E_Input01, MR_LANG( 'Channel' ), channelName, MR_LANG( 'Select a channel you want to set your time and date by' ) )
			self.mDate = TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_DD_MM_YYYY )
			self.AddInputControl( E_Input02, MR_LANG( 'Date' ), self.mDate, MR_LANG( 'Enter today\'s date' ) )
			self.mTime = TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_HH_MM )
			self.AddInputControl( E_Input03, MR_LANG( 'Time' ), self.mTime, MR_LANG( 'Set the local time' ) )
			self.AddEnumControl( E_SpinEx02, 'Local Time Offset', None, MR_LANG( 'Set the time zone that will be the basis for the date and time display' ) )
			self.AddEnumControl( E_SpinEx03, 'Summer Time', None, MR_LANG( 'When set to \'Automatic\', the system automatically change over to and from summer and winter time' ) )
			self.AddInputControl( E_Input04, MR_LANG( 'Apply' ), '', MR_LANG( 'Press OK button to save time settings' ) )
			self.AddPrevNextButton( MR_LANG( 'Go to the summary of first installation page' ), MR_LANG( 'Go back to the channel search setup page' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input01, E_Input02, E_Input03, E_Input04 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )
			self.InitControl( )
			time.sleep( 0.2 )
			self.DisableControl( )
			self.SetDefaultControl( )

		elif aStep == E_STEP_RESULT :
			self.mPrevStepNum = E_STEP_DATE_TIME
			self.getControl( E_SETTING_HEADER_TITLE ).setLabel( MR_LANG( 'Summary of First Installation' ) )
			self.AddInputControl( E_Input01, MR_LANG( 'Menu Language' ), MR_LANG( XBMC_GetCurrentLanguage( ) ) )
			self.mDate = TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_DD_MM_YYYY )
			self.AddInputControl( E_Input02, MR_LANG( 'Date' ), self.mDate )
			self.mTime = TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_HH_MM )
			self.AddInputControl( E_Input03, MR_LANG( 'Time' ), self.mTime )
			cntChannel = self.mDataCache.Channel_GetCount( ElisEnum.E_SERVICE_TYPE_TV )
			cntRadio = self.mDataCache.Channel_GetCount( ElisEnum.E_SERVICE_TYPE_RADIO )
			if cntChannel == None :
				cntChannel = 0
			if cntRadio == None :
				cntRadio = 0
			self.AddInputControl( E_Input04, MR_LANG( 'Number of your TV Channels' ), '%d' % cntChannel )
			self.AddInputControl( E_Input05, MR_LANG( 'Number of your Radio Channels' ), '%d' % cntRadio )
			self.AddPrevNextButton( MR_LANG( 'Exit the first installation' ), MR_LANG( 'Go back to the time and date setup page' ) )

			visibleControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, False )

			hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			time.sleep( 0.2 )
			self.setFocusId( E_FIRST_TIME_INSTALLATION_NEXT )

		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( True )


	def GotoAntennaNextStep( self ) :
		self.MakeAntennaSetupStepList( )
		WinMgr.GetInstance( ).ShowWindow( self.GetAntennaNextStepWindowId( ), WinMgr.WIN_ID_MAINMENU )


	def DisableControl( self, aControlID = None ) :
		if self.GetFTIStep( ) == E_STEP_ANTENNA :
			if aControlID == None or aControlID == E_SpinEx01 :
				if self.mTunerConnection == E_TUNER_LOOPTHROUGH or self.mTunerConnection == E_TUNER_ONECABLE :
					control = self.getControl( E_SpinEx02 + 3 )
					time.sleep( 0.02 )
					control.selectItem( E_SAMEWITH_TUNER )
					self.mTunerSignal = E_SAMEWITH_TUNER
					self.SetEnableControl( E_SpinEx02, False )
					if self.mTunerConnection == E_TUNER_ONECABLE :
						self.SetEnableControl( E_SpinEx03, False )
					else :
						self.SetEnableControl( E_SpinEx03, True )
				else :
					self.SetEnableControl( E_SpinEx02, True )
					self.SetEnableControl( E_SpinEx03, True )

			if aControlID == None or aControlID == E_SpinEx02 or aControlID == E_SpinEx01 :
				if self.mTunerSignal == E_SAMEWITH_TUNER :
					if self.GetSelectedIndex( E_SpinEx03 ) != self.GetSelectedIndex( E_SpinEx04 ) :
						control = self.getControl( E_SpinEx04 + 3 )
						control.selectItem( self.mTuner1Control )
						self.mTuner2Control = self.mTuner1Control
					self.SetEnableControl( E_SpinEx04, False )
				else :
					self.SetEnableControl( E_SpinEx04, True)

			if aControlID == E_SpinEx03 :
				if self.mTunerSignal == E_SAMEWITH_TUNER :
					control = self.getControl( E_SpinEx04 + 3 )
					control.selectItem( self.mTuner1Control )
					self.mTuner2Control = self.mTuner1Control
					self.SetEnableControl( E_SpinEx04, False )

		elif self.GetFTIStep( ) == E_STEP_CHANNEL_SEARCH_CONFIG :
			visibleControlIds = [ E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input01, E_Input02, E_Input03 ]
			if self.GetSelectedIndex( E_SpinEx01 ) == 0 :
				self.getControl( E_SpinEx02 + 3 ).selectItem( 0 )
				self.mIsManualSetup = 0
				self.SetEnableControls( visibleControlIds, False )
			else :
				self.SetEnableControls( visibleControlIds, True )

			if self.mSatelliteIndex == 0 :
				visibleControlIds = [ E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input02, E_Input03 ]
				self.getControl( E_SpinEx02 + 3 ).selectItem( 0 )
				self.mIsManualSetup = 0
				self.SetEnableControls( visibleControlIds, False )
				return

			visibleControlIds = [ E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input02, E_Input03 ]
			if self.mIsManualSetup == 0 :
				self.SetEnableControls( visibleControlIds, False )
				ScanHelper.GetInstance( ).ScanHelper_Stop( self )
			else :
				self.SetEnableControls( visibleControlIds, True )
				self.mEventBus.Register( self )
				ScanHelper.GetInstance( ).ScanHelper_Start( self )
				ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex - 1 ], self.mConfigTransponder )

				if self.mConfigTransponder.mFECMode == 0 :
					self.getControl( E_SpinEx04 + 3 ).getListItem( 0 ).setLabel2( MR_LANG( 'Automatic' ) )
					self.getControl( E_SpinEx04 + 3 ).selectItem( 0 )
					self.SetEnableControl( E_SpinEx04, False )
				else :
					self.SetProp( E_SpinEx04, 0 )
					self.getControl( E_SpinEx04 + 3 ).getListItem( 0 ).setLabel2( MR_LANG( 'QPSK 1/2' ) )
					self.SetEnableControl( E_SpinEx04, True )

		elif self.GetFTIStep( ) == E_STEP_DATE_TIME :
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
				self.mBusyVideoSetting = False
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
			control = self.getControl( E_SpinEx03 + 3 )
			control.selectItem( prop )

		self.mBusyVideoSetting = False


	def LoadFormattedSatelliteNameList( self ) :
		self.mConfiguredSatelliteList = []
		self.mFormattedList = []

		configuredSatelliteList1 = self.mDataCache.GetConfiguredSatelliteListByTunerIndex( E_TUNER_1 )
		configuredSatelliteList2 = self.mDataCache.GetConfiguredSatelliteListByTunerIndex( E_TUNER_2 )

		if configuredSatelliteList1 and configuredSatelliteList1[0].mError == 0 :
			self.mConfiguredSatelliteList = deepcopy( configuredSatelliteList1 )

		if self.mTunerMgr.GetCurrentTunerConfigType( ) == E_DIFFERENT_TUNER :
			if configuredSatelliteList1 :
				if configuredSatelliteList2 and configuredSatelliteList2[0].mError == 0 :
					for config in configuredSatelliteList2 :
						find = False
						for compare in configuredSatelliteList1 :
							if ( config.mSatelliteLongitude == compare.mSatelliteLongitude ) and ( config.mBandType == compare.mBandType ) :
								find = True
								break

						if find == False :
							self.mConfiguredSatelliteList.append( config )
			else :
				if configuredSatelliteList2 :
					self.mConfiguredSatelliteList = deepcopy( configuredSatelliteList2 )

		if len( self.mConfiguredSatelliteList ) > 0 :
			self.mFormattedList.append( MR_LANG( 'All' ) )
			for config in self.mConfiguredSatelliteList :
				self.mFormattedList.append( self.mDataCache.GetFormattedSatelliteName( config.mSatelliteLongitude, config.mBandType ) )
		else :
			self.mFormattedList.append( MR_LANG( 'None' ) )


	def LoadTransponderList( self ) :
		if self.mSatelliteIndex == 0 :
			tmp = self.mSatelliteIndex
		else :
			tmp = self.mSatelliteIndex - 1

		if len( self.mConfiguredSatelliteList ) > 0 :
			satellite = self.mConfiguredSatelliteList[ tmp ]
			self.mTransponderList = []
			self.mTransponderList = self.mDataCache.GetTransponderListBySatellite( satellite.mSatelliteLongitude, satellite.mBandType )
			if self.mTransponderList and self.mTransponderList[0].mError == 0 :
				self.mTransponderList.sort( self.ByFrequency )
				self.mHasTansponder = True
			else :
				self.mHasTansponder = False
		else :
			self.mHasTansponder = False


	def SetConfigTransponder( self ) :
		self.mConfigTransponder = ElisITransponderInfo( )
		self.mConfigTransponder.reset( )
		if self.mHasTansponder == True :	
			self.mConfigTransponder.mFrequency = self.mTransponderList[self.mTransponderIndex].mFrequency
			self.mConfigTransponder.mFECMode = self.mTransponderList[self.mTransponderIndex].mFECMode
			self.mConfigTransponder.mSymbolRate = self.mTransponderList[self.mTransponderIndex].mSymbolRate
			self.mConfigTransponder.mPolarization = self.mTransponderList[self.mTransponderIndex].mPolarization
			self.mConfigTransponder.mTsid = self.mTransponderList[self.mTransponderIndex].mTsid
			self.mConfigTransponder.mOnid = self.mTransponderList[self.mTransponderIndex].mOnid
			self.mConfigTransponder.mNid = self.mTransponderList[self.mTransponderIndex].mNid


	def ByFrequency( self, aArg1, aArg2 ) :
		return cmp( aArg1.mFrequency, aArg2.mFrequency )


	def ChannelSearchConfig( self, aControlId ) :
		if aControlId == E_Input01 :
			dialog = xbmcgui.Dialog( )
			select =  dialog.select( MR_LANG( 'Select Satellite' ), self.mFormattedList )
			if select >= 0 and select != self.mSatelliteIndex :
				self.mSatelliteIndex	= select
				self.mTransponderIndex	= 0
				self.SetListControl( E_STEP_CHANNEL_SEARCH_CONFIG, False )
			#self.SetControlLabel2String( E_Input01, self.mFormattedList[ self.mSatelliteIndex ] )

		elif aControlId == E_Input02 :
			formattedTransponderList = []
			for i in range( len( self.mTransponderList ) ) :
				if self.mTransponderList[i].mPolarization == ElisEnum.E_LNB_HORIZONTAL :
	 				polarization = MR_LANG( 'Horizontal' )
	 			else :
	 				polarization = MR_LANG( 'Vertical' )
				formattedTransponderList.append( '%dMHz   %dKS/s   %s' % ( self.mTransponderList[i].mFrequency, self.mTransponderList[i].mSymbolRate, polarization ) )
			dialog = xbmcgui.Dialog( )
			select = dialog.select( MR_LANG( 'Select Transponder' ), formattedTransponderList, False, self.mTransponderIndex )

			if select >=0 :
				self.mTransponderIndex = select
				#self.SetConfigTransponder( )
				self.SetListControl( E_STEP_CHANNEL_SEARCH_CONFIG, False )
				ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex - 1 ], self.mConfigTransponder )

		elif aControlId == E_Input03 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( MR_LANG( 'Enter Symbol Rate' ), '%d' % self.mConfigTransponder.mSymbolRate, 5 )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				tempval = dialog.GetString( )
				if int( tempval ) > 60000 :
					self.mConfigTransponder.mSymbolRate = 60000
				elif int( tempval ) < 1000 :
					self.mConfigTransponder.mSymbolRate = 1000
				else :
					self.mConfigTransponder.mSymbolRate = int( tempval )

				self.SetControlLabel2String( E_Input03, '%d KS/s' % self.mConfigTransponder.mSymbolRate )
				ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex - 1 ], self.mConfigTransponder )

		elif aControlId == E_SpinEx01 :
			if self.GetSelectedIndex( E_SpinEx01 ) == 0 :
				self.mIsChannelSearch = False
			else :
				self.mIsChannelSearch = True
			self.DisableControl( )

		elif aControlId == E_SpinEx02 :
			self.mIsManualSetup = self.GetSelectedIndex( E_SpinEx02 )
			self.DisableControl( )

		elif aControlId == E_SpinEx03 :
			if self.GetSelectedIndex( E_SpinEx03 ) == 0 :
				self.mConfigTransponder.mFECMode = ElisEnum.E_FEC_UNDEFINED		
			else :
				self.mConfigTransponder.mFECMode = ElisEnum.E_DVBS2_QPSK_1_2
	
			self.DisableControl( )
			ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex - 1 ], self.mConfigTransponder )

		elif aControlId == E_SpinEx04 :
			self.ControlSelect( )
			property = ElisPropertyEnum( 'FEC', self.mCommander )
			self.mConfigTransponder.mFECMode = property.GetProp( )
			ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex - 1 ], self.mConfigTransponder )

		elif aControlId == E_SpinEx05 :
			self.mConfigTransponder.mPolarization = self.GetSelectedIndex( E_SpinEx05 )
			ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex - 1 ], self.mConfigTransponder )

		elif aControlId == E_SpinEx06 or aControlId == E_SpinEx07 :
			self.ControlSelect( )

		elif aControlId == E_FIRST_TIME_INSTALLATION_NEXT :
			self.mEventBus.Deregister( self )
			self.OpenBusyDialog( )
			ScanHelper.GetInstance( ).ScanHelper_Stop( self )
			self.CloseBusyDialog( )
			if self.mIsChannelSearch == True :
				if self.mConfiguredSatelliteList :
					if self.mIsManualSetup == 0 :
						channelList = self.mDataCache.Channel_GetList( )
						if channelList and channelList[0].mError == 0 :
							ret = self.mDataCache.Channel_DeleteAll( )
							self.mDataCache.Channel_Save( )
							self.mDataCache.Channel_ReLoad( False )
							if ret :
								if not self.mDataCache.Get_Player_AVBlank( ) :
									self.mDataCache.Player_AVBlank( True )
								self.mDataCache.Channel_InvalidateCurrent( )
								#self.mDataCache.Frontdisplay_SetMessage( 'NoChannel' )

						if self.mSatelliteIndex == 0 :
							dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
							dialog.SetConfiguredSatellite( self.mDataCache.Satellite_GetConfiguredList( ) )
							dialog.doModal( )			
						else :
							configuredSatelliteList = []
							config = ElisISatelliteInfo( )
							config.mLongitude = self.mConfiguredSatelliteList[ self.mSatelliteIndex - 1 ].mSatelliteLongitude
							config.mBand = self.mConfiguredSatelliteList[ self.mSatelliteIndex - 1 ].mBandType
							config.mName = self.mDataCache.GetSatelliteName( config.mLongitude, config.mBand )

							configuredSatelliteList.append( config )
							dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
							dialog.SetConfiguredSatellite( configuredSatelliteList )				
							dialog.doModal( )
					else :
						transponderList = []
			 			config = self.mConfiguredSatelliteList[ self.mSatelliteIndex - 1 ]
						transponderList.append( self.mConfigTransponder )

						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
						dialog.SetTransponder( config.mSatelliteLongitude, config.mBandType, transponderList, self.mIsManualTp )
						dialog.doModal( )
						
				else :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No configured satellite available' ) )
					dialog.doModal( )

				self.SetListControl( E_STEP_DATE_TIME )
			else :
				self.SetListControl( E_STEP_DATE_TIME )


	def CallballInputNumber( self, aGroupId, aString ) :
		if self.GetFTIStep( ) == E_STEP_CHANNEL_SEARCH_CONFIG :
			if aGroupId == E_Input02 :
				if self.mIsManualTp == 0 :
					self.mIsManualTp = 1
				self.mConfigTransponder.mFrequency = int( aString )
				self.SetControlLabel2String( aGroupId, aString + ' MHz' )
				if self.mConfigTransponder.mFrequency >= 3000 :
					ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex - 1 ], self.mConfigTransponder )

			elif aGroupId == E_Input03 :
				self.mConfigTransponder.mSymbolRate = int( aString )
				self.SetControlLabel2String( aGroupId, aString + ' KS/s' )
				if self.mConfigTransponder.mSymbolRate >= 1000 :
					ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex - 1 ], self.mConfigTransponder )


	def FocusChangedAction( self, aGroupId ) :
		if self.GetFTIStep( ) == E_STEP_CHANNEL_SEARCH_CONFIG :
			if aGroupId == E_Input02 and self.mConfigTransponder.mFrequency < 3000 :
				self.mConfigTransponder.mFrequency = 3000
				self.SetControlLabel2String( E_Input02, '%s MHz' % self.mConfigTransponder.mFrequency )
				ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex - 1 ], self.mConfigTransponder )
				
			elif aGroupId == E_Input03 and self.mConfigTransponder.mSymbolRate < 1000 :
				self.mConfigTransponder.mSymbolRate = 1000
				self.SetControlLabel2String( E_Input03, '%s KS/s' % self.mConfigTransponder.mSymbolRate )
				ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex - 1 ], self.mConfigTransponder )


	def TimeSetting( self, aControlId ) :
		if aControlId == E_SpinEx01 :
			self.DisableControl( )

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

		elif aControlId == E_Input04 :
			oriSetupChannel = ElisPropertyInt( 'Time Setup Channel Number', self.mCommander ).GetProp( )
			oriTimeMode = ElisPropertyEnum( 'Time Mode', self.mCommander ).GetProp( )
			oriLocalTimeOffset = ElisPropertyEnum( 'Local Time Offset', self.mCommander ).GetProp( )	
			oriSummerTime = ElisPropertyEnum( 'Summer Time', self.mCommander ).GetProp( )
			oriChannel = self.mDataCache.Channel_GetCurrent( )

			ElisPropertyEnum( 'Time Mode', self.mCommander ).SetPropIndex( self.GetSelectedIndex( E_SpinEx01 ) )
			ElisPropertyEnum( 'Local Time Offset', self.mCommander ).SetPropIndex( self.GetSelectedIndex( E_SpinEx02) )
			ElisPropertyEnum( 'Summer Time', self.mCommander ).SetPropIndex( self.GetSelectedIndex( E_SpinEx03 ) )
			localOffset = ElisPropertyEnum( 'Local Time Offset', self.mCommander ).GetProp( )
			self.mCommander.Datetime_SetLocalOffset( localOffset )

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
					ElisPropertyEnum( 'Time Mode', self.mCommander ).SetProp( oriTimeMode )
					ElisPropertyEnum( 'Summer Time', self.mCommander ).SetProp( oriSummerTime )
					ElisPropertyInt( 'Time Setup Channel Number', self.mCommander ).SetProp( oriSetupChannel )
					ElisPropertyEnum( 'Local Time Offset', self.mCommander ).SetProp( oriLocalTimeOffset )
					self.getControl( E_SpinEx01 + 3 ).selectItem( ElisPropertyEnum( 'Time Mode', self.mCommander ).GetPropIndex( ) )
					self.getControl( E_SpinEx02 + 3 ).selectItem( ElisPropertyEnum( 'Summer Time', self.mCommander ).GetPropIndex( ) )
					self.getControl( E_SpinEx03 + 3 ).selectItem( ElisPropertyEnum( 'Local Time Offset', self.mCommander ).GetPropIndex( ) )
					self.mCommander.Datetime_SetLocalOffset( oriLocalTimeOffset )

				self.mDataCache.LoadTime( )
				self.SetListControl( E_STEP_DATE_TIME )
				ElisPropertyEnum( 'Time Installation', self.mCommander ).SetProp( 0 )
				self.mDataCache.Channel_SetCurrent( oriChannel.mNumber, oriChannel.mServiceType) # Todo After : using ServiceType to different way
			else :
				self.OpenBusyDialog( )
				sumtime = self.mDate + '.' + self.mTime
				t = time.strptime( sumtime, '%d.%m.%Y.%H:%M' )
				ret = self.mCommander.Datetime_SetSystemUTCTime( int( time.mktime( t ) ) )
				globalEvent = pvr.GlobalEvent.GetInstance( )
				globalEvent.SendLocalOffsetToXBMC( )

			self.CloseBusyDialog( )
			if mode == TIME_AUTOMATIC and dialog.GetResult( ) == False :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No time info was given by that channel' ) )
				dialog.doModal( )

		elif aControlId == E_FIRST_TIME_INSTALLATION_NEXT :
				self.SetListControl( E_STEP_RESULT )


	def SetTunerProperty( self ) :
		if self.mTunerConnection == E_TUNER_ONECABLE :
			ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander ).SetProp( E_TUNER_LOOPTHROUGH )
			ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander ).SetProp( self.mTunerSignal )
			ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).SetProp( E_ONE_CABLE )
			ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).SetProp( E_ONE_CABLE )
		else :
			ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander ).SetProp( self.mTunerConnection )
			ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander ).SetProp( self.mTunerSignal )
			ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).SetProp( self.mTuner1Control )
			ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).SetProp( self.mTuner2Control )


	def LoadTunerProperty( self ) :
		if ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( ) == E_ONE_CABLE :
			self.mTunerConnection		= E_TUNER_ONECABLE
			self.mTunerSignal			= E_SAMEWITH_TUNER
		else :
			self.mTunerConnection		= ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander ).GetProp( )
			self.mTunerSignal			= ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander ).GetProp( )
			self.mTuner1Control			= ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( )
			self.mTuner2Control			= ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).GetProp( )

