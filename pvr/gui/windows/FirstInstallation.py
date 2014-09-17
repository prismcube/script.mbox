from pvr.gui.WindowImport import *
from pvr.gui.FTIWindow import FTIWindow
from pvr.XBMCInterface import XBMC_SetSkinZoom
import pvr.ScanHelper as ScanHelper
from elementtree import ElementTree

E_FIRST_INSTALLATION_BASE_ID = WinMgr.WIN_ID_FIRST_INSTALLATION * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID
FILE_PROVIDER	= xbmcaddon.Addon( 'script.mbox' ).getAddonInfo( 'path' ) + '/Provider.xml'
FILE_TERRESTRIAL = xbmcaddon.Addon( 'script.mbox' ).getAddonInfo( 'path' ) + '/terrestrial.xml'

E_SEARCH_AUTO		=	0
E_SEARCH_MANUAL		=	1
E_SEARCH_FAST		=	2

E_TUNER_T	= 0
E_TUNER_T2	= 1
E_TUNER_C	= 2


class FirstInstallation( FTIWindow ) :
	def __init__( self, *args, **kwargs ) :
		FTIWindow.__init__( self, *args, **kwargs )
		self.mPrevStepNum				= E_STEP_SELECT_LANGUAGE
		self.mAudioLanguageList			= []
		for i in range( ElisPropertyEnum( 'Audio Language', self.mCommander ).GetIndexCount( ) ) :
			self.mAudioLanguageList.append( ElisPropertyEnum( 'Audio Language', self.mCommander ).GetPropStringByIndex( i, False ) )
		self.mIsChannelSearch			= False
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

		self.mChannelSearchMode			= E_SEARCH_AUTO
		self.mSatelliteIndex			= 0
		self.mTransponderList			= []
		self.mTransponderIndex			= 0
		self.mConfigTransponder			= None
		self.mIsManualTp				= 0
		self.mIsReloadChannelSearchStep = False
		self.mOPDescr					= 'None'
		self.mUseHDList					= 0
		self.mProviderStruct			= ElisFastScanProviderInfo( )

		self.mIsManualSetup = 0
		self.mDVBT_Manual = ElisIDVBTCarrier( )
		self.mDVBT_Auto = []
		self.mTerrestrial = 'None'
		self.mTunerType		= E_TUNER_T
		self.SetTerrestriaInfo( 0 )
		self.mBackaudiolang				= ElisPropertyEnum( 'Audio Language', self.mCommander ).GetProp( )

		if self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_DUAL :
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
		else :
			self.mTuner1Control	= ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( )


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.SetSingleWindowPosition( E_FIRST_INSTALLATION_BASE_ID )
		self.SetFrontdisplayMessage( MR_LANG('First Installation') )
		self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'Installation' ), MR_LANG( 'First Installation' ) ) )

		self.SetFirstInstallation( True )
		if self.mReloadSkinPosition :
			WinMgr.GetInstance( ).LoadSkinPosition( )
			self.mReloadSkinPosition = False
			ElisPropertyEnum( 'Audio Language', self.mCommander ).SetProp( self.mBackaudiolang )

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
		self.mEventBus.Register( self )
		self.mInitialized = True


	def onAction( self, aAction ) :
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
					if ret >= 0 and ret != currentindex :
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
				self.mBackaudiolang = ElisPropertyEnum( 'Audio Language', self.mCommander ).GetProp( )
				xbmc.executebuiltin( 'ActivateWindow(screencalibration)', True )
				self.mReloadSkinPosition = True
				if self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_SINGLE or self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_DUAL :
					self.SetFTIStep( E_STEP_ANTENNA )
				elif self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBT :
					self.SetFTIStep( E_STEP_CHANNEL_SEARCH_CONFIG_DVBT )
				self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( False )

			elif groupId == E_Input01 :
				self.ShowHdmiFormat( )

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
				self.mBackaudiolang = ElisPropertyEnum( 'Audio Language', self.mCommander ).GetProp( )
				xbmc.executebuiltin( 'ActivateWindow(screencalibration)', True )
				self.mReloadSkinPosition = True
				self.SetFTIStep( E_STEP_VIDEO_AUDIO )
				self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( False )
				return

		elif self.GetFTIStep( ) == E_STEP_CHANNEL_SEARCH_CONFIG :
			self.ChannelSearchConfig( groupId )

		elif self.GetFTIStep( ) == E_STEP_CHANNEL_SEARCH_CONFIG_FAST :
			self.ChannelSearchConfigFast( groupId )

		elif self.GetFTIStep( ) == E_STEP_CHANNEL_SEARCH_CONFIG_DVBT :
			self.ChannelSearchConfigDVBT( groupId )
			if groupId == E_FIRST_TIME_INSTALLATION_PREV :
				self.OpenBusyDialog( )
				self.StopScanHelper( )
				self.CloseBusyDialog( )
				xbmc.executebuiltin( 'ActivateWindow(screencalibration)', True )
				self.mReloadSkinPosition = True
				self.SetFTIStep( E_STEP_VIDEO_AUDIO )
				self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( False )
				return

		elif self.GetFTIStep( ) == E_STEP_DATE_TIME :
			self.TimeSetting( groupId )

		elif self.GetFTIStep( ) == E_STEP_RESULT :
			if groupId == E_FIRST_TIME_INSTALLATION_NEXT :
				self.Close( )

		if groupId == E_FIRST_TIME_INSTALLATION_PREV :
			#self.mEventBus.Deregister( self )
			self.OpenBusyDialog( )
			self.StopScanHelper( )
			self.CloseBusyDialog( )
			self.SetListControl( self.mPrevStepNum )


	def onFocus( self, aControlId ) :
		if self.mInitialized :
			self.ShowDescription( aControlId )


	def onEvent( self, aEvent ) :
		if xbmcgui.getCurrentWindowId( ) == self.mWinId :
			if self.GetFTIStep( ) == E_STEP_CHANNEL_SEARCH_CONFIG or self.GetFTIStep( ) == E_STEP_CHANNEL_SEARCH_CONFIG_DVBT :
				if aEvent.getName( ) == ElisEventTuningStatus.getName( ) :
					self.UpdateStatus( aEvent )


	def UpdateStatus( self, aEvent ) :
		if self.GetFTIStep( ) == E_STEP_CHANNEL_SEARCH_CONFIG :
			currentFreq = self.mConfigTransponder.mFrequency
		elif self.GetFTIStep( ) == E_STEP_CHANNEL_SEARCH_CONFIG_DVBT :
			currentFreq = self.mDVBT_Manual.mFrequency

		if aEvent.mFrequency == currentFreq :
			ScanHelper.GetInstance( ).ScanHerper_Progress( self, aEvent.mSignalStrength, aEvent.mSignalQuality, aEvent.mIsLocked )
			if aEvent.mIsLocked :
				self.mDataCache.Player_AVBlank( False )


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

		#self.mEventBus.Deregister( self )
		self.StopScanHelper( )
		self.CloseBusyDialog( )
		WinMgr.GetInstance( ).CloseWindow( )


	def SetListControl( self, aStep, aSetFocus=True ) :
		self.ResetAllControl( )
		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( False )
		
		self.SetFTIStep( aStep )
		self.DrawFTIStep( aStep )
		self.SetPrevNextButtonLabel( aStep )

		if aStep == E_STEP_SELECT_LANGUAGE :
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
			lblSelect = ElisPropertyEnum( 'HDMI Format', self.mCommander ).GetPropString( )
			self.AddInputControl( E_Input01, 'HDMI Format', lblSelect, MR_LANG( 'Set the display\'s HDMI resolution' ) )
			self.AddPrevNextButton( MR_LANG( 'Go to the antenna and satellite setup page' ), MR_LANG( 'Go back to the language setup page' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_Input01 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			time.sleep( 0.2 )
			self.SetDefaultControl( )

		elif aStep == E_STEP_ANTENNA :
			self.mPrevStepNum = E_STEP_VIDEO_AUDIO
			self.LoadTunerProperty( )			
			self.getControl( E_SETTING_HEADER_TITLE ).setLabel( MR_LANG( 'Antenna and Satellite Setup' ) )

			if self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_SINGLE :
				self.AddUserEnumControl( E_SpinEx03, MR_LANG( 'Tuner 1 Control' ), E_LIST_TUNER_CONTROL, self.mTuner1Control, MR_LANG( 'Select a control method for tuner 1' ) )

				visibleControlIds = [ E_SpinEx03 ]
				self.SetVisibleControls( visibleControlIds, True )
				self.SetEnableControls( visibleControlIds, True )

				hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
				self.SetVisibleControls( hideControlIds, False )
			else :
				connectTypeDescription = '%s %s' % ( MR_LANG( 'When set to \'Separated\', the tuner 2 receives its own signal input'), MR_LANG('however it will receive only the channel level currently being received by the tuner 1 when this is set to \'Loopthrough\'' ) )
				self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Tuner Connection' ), E_LIST_TUNER_CONNECTION, self.mTunerConnection, connectTypeDescription )
				self.AddUserEnumControl( E_SpinEx02, MR_LANG( 'Tuner 2 Signal' ), E_LIST_TUNER2_SIGNAL, self.mTunerSignal, MR_LANG( 'When set to \'Same with Tuner 1\', both tuners are connected to the same signal source' ) )
				self.AddUserEnumControl( E_SpinEx03, MR_LANG( 'Tuner 1 Control' ), E_LIST_TUNER_CONTROL, self.mTuner1Control, MR_LANG( 'Select a control method for tuner 1' ) )
				self.AddUserEnumControl( E_SpinEx04, MR_LANG( 'Tuner 2 Control' ), E_LIST_TUNER_CONTROL, self.mTuner2Control, MR_LANG( 'Select a control method for tuner 2' ) )
				
				visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
				self.SetVisibleControls( visibleControlIds, True )
				self.SetEnableControls( visibleControlIds, True )

				hideControlIds = [ E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
				self.SetVisibleControls( hideControlIds, False )

			self.AddPrevNextButton( MR_LANG( 'Go to the satellite configuration page' ), MR_LANG( 'Go back to the video and audio setup page' ) )

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
			self.AddUserEnumControl( E_SpinEx02, MR_LANG( 'Search Mode' ), [ MR_LANG( 'Automatic Scan' ), MR_LANG( 'Manual Scan' ), MR_LANG( 'Fast Scan' ) ], self.mChannelSearchMode, MR_LANG( 'Select channel scan mode' ) )
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

		elif aStep == E_STEP_CHANNEL_SEARCH_CONFIG_FAST :
			self.mPrevStepNum = E_STEP_CHANNEL_SEARCH_CONFIG
			self.getControl( E_SETTING_HEADER_TITLE ).setLabel( MR_LANG( 'Channel Search Setup' ) )
			self.AddInputControl( E_Input01, MR_LANG( 'Provider' ), self.mOPDescr, MR_LANG( 'Select a provider you want to scan channels from' ) )
			self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'HD List' ), USER_ENUM_LIST_YES_NO, self.mUseHDList, MR_LANG( 'Enable/Disable HD List option' ) )
			self.AddPrevNextButton( MR_LANG( 'Go to the time and date setup page' ), MR_LANG( 'Go back to the channel search setup page' ) )

			visibleControlIds = [ E_SpinEx01, E_Input01 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			time.sleep( 0.2 )
			self.DisableControl( )

		elif aStep == E_STEP_CHANNEL_SEARCH_CONFIG_DVBT :
			self.mPrevStepNum = E_STEP_VIDEO_AUDIO
			self.getControl( E_SETTING_HEADER_TITLE ).setLabel( MR_LANG( 'Channel Search Setup' ) )

			if self.mTunerType == E_TUNER_T or self.mTunerType == E_TUNER_T2 :
				self.AddUserEnumControl( E_SpinEx07, MR_LANG( 'Channel Search' ), USER_ENUM_LIST_YES_NO, self.mIsChannelSearch, MR_LANG( 'Do you want to perform a channel search in the first installation?' ) )
				self.AddUserEnumControl( E_SpinEx03, 'Tuner Type', [ MR_LANG( 'DVB-T' ), MR_LANG( 'DVB-T2' ) ], self.mTunerType, MR_LANG( 'Select tuner type' ) )
				#self.AddUserEnumControl( E_SpinEx03, 'Tuner Type', [ MR_LANG( 'DVB-T' ), MR_LANG( 'DVB-T2' ), MR_LANG( 'DVB-C' ) ], self.mTunerType, MR_LANG( 'Select tuner type' ) )
				self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Search Mode' ), [ MR_LANG( 'Automatic Scan' ), MR_LANG( 'Manual Scan' ) ], self.mIsManualSetup, MR_LANG( 'Select channel search mode' ) )
				self.AddInputControl( E_Input04, MR_LANG( 'Terrestrial frequency list' ), self.mTerrestrial, MR_LANG( 'Select Terrerstrial' ) )
				self.AddInputControl( E_Input01, MR_LANG( 'Frequency' ), '%d KHz' % self.mDVBT_Manual.mFrequency, MR_LANG( 'Input frequency' ), aInputNumberType = TYPE_NUMBER_NORMAL, aMax = 9999999 )
				self.AddUserEnumControl( E_SpinEx02, 'Bandwidth', [ '6MHz','7MHz','8MHz' ], self.mDVBT_Manual.mBand, MR_LANG( 'Select bandwidth' ) )				
				self.AddInputControl( E_Input02, MR_LANG( 'PLP ID' ), '%03d' % self.mDVBT_Manual.mPLPId, MR_LANG( 'Input PLP ID' ), aInputNumberType = TYPE_NUMBER_NORMAL, aMax = 999 )
				self.AddEnumControl( E_SpinEx04, 'Antenna 5V', MR_LANG( 'Enable 5V for active antenna' ), MR_LANG( 'Select enable 5v for active antenna' ) )
				networkSearchDescription = '%s %s' % ( MR_LANG( 'When set to \'Off\', only the factory default transponders of the satellites you previously selected will be scanned for new channels.'), MR_LANG('If you set to \'On\', both the existing transponders and additional transponders that have not yet been stored to be located are scanned for new channels' ) )
				self.AddEnumControl( E_SpinEx05, 'Network Search', None, networkSearchDescription )
				self.AddEnumControl( E_SpinEx06, 'Channel Search Mode', MR_LANG( 'Search Type' ), MR_LANG( 'Select whether you wish to scan free and scrambled, free only or scrambled only' ) )
				self.AddPrevNextButton( MR_LANG( 'Go to the time and date setup page' ), MR_LANG( 'Go back to the channel search setup page' ) )

				visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input01, E_Input02, E_Input04 ]
				self.SetVisibleControls( visibleControlIds, True )
				self.SetEnableControls( visibleControlIds, True )
				hideControlIds = [ E_Input03, E_Input05 ]
				self.SetVisibleControls( hideControlIds, False )

			elif self.mTunerType == E_TUNER_C :
				self.AddUserEnumControl( E_SpinEx03, 'Tuner Type', [ MR_LANG( 'DVB-T' ), MR_LANG( 'DVB-T2' ), MR_LANG( 'DVB-C' ) ], self.mTunerType, MR_LANG( 'Select tuner type' ) )
				self.AddInputControl( E_Input01, MR_LANG( 'Not support' ), '', MR_LANG( 'Not support' ) )
				self.AddPrevNextButton( MR_LANG( 'Go to the time and date setup page' ), MR_LANG( 'Go back to the channel search setup page' ) )

				visibleControlIds = [ E_SpinEx03, E_Input01 ]
				self.SetVisibleControls( visibleControlIds, True )
				self.SetEnableControls( visibleControlIds, True )
				hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_SpinEx07, E_Input02, E_Input03, E_Input04, E_Input05 ]
				self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			time.sleep( 0.2 )
			self.DisableControl( )
			self.SetDefaultControl( )

		elif aStep == E_STEP_DATE_TIME :
			if self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_SINGLE or self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_DUAL :
				self.mPrevStepNum = E_STEP_CHANNEL_SEARCH_CONFIG
			elif self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBT :
				self.mPrevStepNum = E_STEP_CHANNEL_SEARCH_CONFIG_DVBT
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
			self.AddPrevNextButton( MR_LANG( 'Go to the summary page of first installation' ), MR_LANG( 'Go back to the channel search setup page' ) )

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
			if self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_SINGLE :
				return

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
				self.SetEnableControls( visibleControlIds, False )
				self.StopScanHelper( )
				return
			else :
				self.SetEnableControls( visibleControlIds, True )

			visibleControlIds = [ E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input02, E_Input03 ]
			if self.mChannelSearchMode != E_SEARCH_MANUAL :
				self.SetEnableControls( visibleControlIds, False )
				self.StopScanHelper( )
			else :
				self.SetEnableControls( visibleControlIds, True )
				#self.mEventBus.Register( self )
				self.StartScanHelper( )

				if self.mConfigTransponder.mFECMode == 0 :
					self.getControl( E_SpinEx04 + 3 ).getListItem( 0 ).setLabel2( MR_LANG( 'Automatic' ) )
					self.getControl( E_SpinEx04 + 3 ).selectItem( 0 )
					self.SetEnableControl( E_SpinEx04, False )
				else :
					self.SetProp( E_SpinEx04, 0 )
					self.getControl( E_SpinEx04 + 3 ).getListItem( 0 ).setLabel2( MR_LANG( 'QPSK 1/2' ) )
					self.SetEnableControl( E_SpinEx04, True )

		elif self.GetFTIStep( ) == E_STEP_CHANNEL_SEARCH_CONFIG_FAST :
			if self.mProviderStruct.mHasHDList == 0 :
				self.SetEnableControl( E_SpinEx01, False )
			else :
				self.SetEnableControl( E_SpinEx01, True )

		elif self.GetFTIStep( ) == E_STEP_CHANNEL_SEARCH_CONFIG_DVBT :
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_Input01, E_Input02, E_Input03, E_Input04 ]
			if self.GetSelectedIndex( E_SpinEx07 ) == 0 :
				self.SetEnableControls( visibleControlIds, False )
				self.StopScanHelper( )
				return
			else :
				self.SetEnableControls( visibleControlIds, True )

			if aControlID == None or aControlID == E_SpinEx01 or aControlID == E_SpinEx03 :
				disablecontrols = [ E_Input01, E_Input02, E_SpinEx02 ]
				if self.mIsManualSetup == 0 :
					self.SetEnableControls( disablecontrols, False )
					self.SetEnableControl( E_Input04, True )
					ScanHelper.GetInstance( ).ScanHelper_Stop( self )
				else :
					ScanHelper.GetInstance( ).ScanHelper_Start( self )
					ScanHelper.GetInstance( ).ScanHelper_ChangeContextByCarrier( self, self.GetElisICarrier( ) )
					self.SetEnableControls( disablecontrols, True )
					self.SetEnableControl( E_Input04, False )
					if self.mTunerType == E_TUNER_T2 :
						self.SetEnableControl( E_Input02, True )
					else :
						self.SetEnableControl( E_Input02, False )

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
			if self.mChannelSearchMode == E_SEARCH_MANUAL and select == 0 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Scanning multiple satellites at the same time%s cannot be done in manual channel search' )% NEW_LINE )
				dialog.doModal( )
				return

			if select >= 0 and select != self.mSatelliteIndex :
				self.mSatelliteIndex	= select
				self.mTransponderIndex	= 0
				self.SetListControl( E_STEP_CHANNEL_SEARCH_CONFIG, False )
				if self.mChannelSearchMode == E_SEARCH_MANUAL :
					self.StartScanHelper( )

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
				self.SetListControl( E_STEP_CHANNEL_SEARCH_CONFIG, False )
				self.StartScanHelper( )

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
				self.StartScanHelper( )

		elif aControlId == E_SpinEx01 :
			if self.GetSelectedIndex( E_SpinEx01 ) == 0 :
				self.mIsChannelSearch = False
			else :
				self.mIsChannelSearch = True
			self.DisableControl( )

		elif aControlId == E_SpinEx02 :
			self.mChannelSearchMode = self.GetSelectedIndex( E_SpinEx02 )
			self.DisableControl( )

		elif aControlId == E_SpinEx03 :
			if self.GetSelectedIndex( E_SpinEx03 ) == 0 :
				self.mConfigTransponder.mFECMode = ElisEnum.E_FEC_UNDEFINED		
			else :
				self.mConfigTransponder.mFECMode = ElisEnum.E_DVBS2_QPSK_1_2
	
			self.DisableControl( )
			self.StartScanHelper( )

		elif aControlId == E_SpinEx04 :
			self.ControlSelect( )
			property = ElisPropertyEnum( 'FEC', self.mCommander )
			self.mConfigTransponder.mFECMode = property.GetProp( )
			self.StartScanHelper( )

		elif aControlId == E_SpinEx05 :
			self.mConfigTransponder.mPolarization = self.GetSelectedIndex( E_SpinEx05 )
			self.StartScanHelper( )

		elif aControlId == E_SpinEx06 or aControlId == E_SpinEx07 :
			self.ControlSelect( )

		elif aControlId == E_FIRST_TIME_INSTALLATION_NEXT :
			#self.mEventBus.Deregister( self )
			self.OpenBusyDialog( )
			self.StopScanHelper( )
			self.CloseBusyDialog( )
			if self.mIsChannelSearch == True :
				if len( self.mConfiguredSatelliteList ) > 0 and self.mHasTansponder == True :
					if self.mChannelSearchMode == E_SEARCH_AUTO :
						channelList = self.mDataCache.Channel_GetList( )
						if channelList and channelList[0].mError == 0 :
							ret = self.mDataCache.Channel_DeleteAll( )
							self.mDataCache.Channel_Save( )
							self.mDataCache.Channel_ReLoad( False )
							if ret :
								if not self.mDataCache.Get_Player_AVBlank( ) :
									self.mDataCache.Player_AVBlank( True )
								self.mDataCache.Channel_InvalidateCurrent( )

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

					elif self.mChannelSearchMode == E_SEARCH_MANUAL :
						if self.mSatelliteIndex == 0 :
							dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
							dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Scanning multiple satellites at the same time%s cannot be done in manual channel search' ) % NEW_LINE )
							dialog.doModal( )
							return
						else :
							transponderList = []
				 			config = self.mConfiguredSatelliteList[ self.mSatelliteIndex - 1 ]
							transponderList.append( self.mConfigTransponder )

							dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
							dialog.SetTransponder( config.mSatelliteLongitude, config.mBandType, transponderList, self.mIsManualTp )
							dialog.doModal( )

					elif self.mChannelSearchMode == E_SEARCH_FAST :
						self.SetListControl( E_STEP_CHANNEL_SEARCH_CONFIG_FAST )
						return
						
				else :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No configured satellite or transponder available' ) )
					dialog.doModal( )

				self.SetListControl( E_STEP_DATE_TIME )
			else :
				self.SetListControl( E_STEP_DATE_TIME )


	def ChannelSearchConfigFast( self, aControlId ) :
		if aControlId == E_Input01 :
			providerList = self.GetProviderList( )
			if providerList :
				dialog = xbmcgui.Dialog( )
				ret = dialog.select( MR_LANG( 'Select Provider' ), providerList, False, StringToListIndex( providerList, self.mOPDescr ) )
				if ret >= 0 :
					if self.SetProviderInfo( ret ) :
						self.SetListControl( E_STEP_CHANNEL_SEARCH_CONFIG_FAST, False )
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No provider file found' ) )
				dialog.doModal( )

		elif aControlId == E_SpinEx01 :
			self.mUseHDList = self.GetSelectedIndex( E_SpinEx01 )

		elif aControlId == E_FIRST_TIME_INSTALLATION_NEXT :
			if self.mProviderStruct and self.mOPDescr != 'None' :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
				providerlist = []
				temp = deepcopy( self.mProviderStruct )
				temp.mHasHDList = self.mUseHDList
				providerlist.append( temp )
				dialog.SetProvider( self.GetTunerIndex( self.mProviderStruct.mLongitude, self.mProviderStruct.mBand ), 0, 0, providerlist )
				dialog.doModal( )
				self.SetListControl( E_STEP_DATE_TIME )
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Please select a provider first' ) )
				dialog.doModal( )


	def StartScanHelper( self ) :
		if self.mSatelliteIndex != 0 :
			if self.mIsScanHelperStart == False :
				ScanHelper.GetInstance( ).ScanHelper_Start( self )
				self.mIsScanHelperStart = True
			ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex - 1 ], self.mConfigTransponder )

		else :
			self.StopScanHelper( )


	def StopScanHelper( self ) :
		self.mIsScanHelperStart = False
		ScanHelper.GetInstance( ).ScanHelper_Stop( self )


	def GetTunerIndex( self, aSatellite, aBand ) :
		if self.mDataCache.GetTunerIndexBySatellite( aSatellite, aBand ) == E_CONFIGURED_TUNER_2 :
			return E_TUNER_2
		else :
			return E_TUNER_1


	def GetProviderList( self ) :
		if not os.path.exists( FILE_PROVIDER ) :
			return None

		try :
			tree = ElementTree.parse( FILE_PROVIDER )
			root = tree.getroot( )
			nameList = []

			for provider in root.findall( 'Provider' ) :
				for name in provider.findall( 'OPDescription' ) :
					nameList.append( name.text.encode( 'utf-8' ) )

			if len( nameList ) > 0 :
				return nameList
			else :
				return None

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return None


	def SetProviderInfo( self, aIndex ) :
		if not os.path.exists( FILE_PROVIDER ) :
			return False

		try :
			tree = ElementTree.parse( FILE_PROVIDER )
			root = tree.getroot( )

			provider = root.getchildren( )[ aIndex ]

			self.mOPDescr = provider.find( 'OPDescription' ).text.encode( 'utf-8' )
			self.mUseHDList = self.GetHDListEnum( provider.find( 'HDList' ).text.encode( 'utf-8' ) )

			struct = ElisFastScanProviderInfo( )
			struct.reset( )
			struct.mName			= provider.find( 'SatelliteName' ).text.encode( 'utf-8' )
			struct.mLongitude		= int( provider.find( 'SatelliteLongitude' ).text.encode( 'utf-8' ) )
			struct.mBand			= self.GetBandEnum( provider.find( 'SatelliteBand' ).text.encode( 'utf-8' ) )
			struct.mTransponderId	= int( provider.find( 'TransponderId' ).text.encode( 'utf-8' ) )
			struct.mFrequency		= int( provider.find( 'Frequency' ).text.encode( 'utf-8' ) )
			struct.mSymbolRate		= int( provider.find( 'Symbolrate' ).text.encode( 'utf-8' ) )
			struct.mPolarization	= self.GetPolEnum( provider.find( 'Polarization' ).text.encode( 'utf-8' ) )
			struct.mFEC				= self.GetFECEnum( provider.find( 'FECMode' ).text.encode( 'utf-8' ) )
			struct.mPid				= int( provider.find( 'Pid' ).text.encode( 'utf-8' ) )
			struct.mPidDescr		= provider.find( 'PidDescription' ).text.encode( 'utf-8' )
			struct.mOPIndetifier	= int( provider.find( 'OPIndetifier' ).text.encode( 'utf-8' ) )
			struct.mOPDescr			= provider.find( 'OPDescription' ).text.encode( 'utf-8' )
			struct.mHasHDList		= self.GetHDListEnum( provider.find( 'HDList' ).text.encode( 'utf-8' ) )

			self.mProviderStruct = struct
			self.mProviderStruct.printdebug( )
			return True

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return False


	def GetBandEnum( self, aBand ) :
		if aBand == 'BAND_KU' :
			return ElisEnum.E_BAND_KU
		elif aBand == 'BAND_C' :
			return ElisEnum.E_BAND_C
		else :
			return ElisEnum.E_BAND_UNDEFINED


	def GetPolEnum( self, aPol ) :
		if aPol == 'LNB_HORIZONTAL' :
			return ElisEnum.E_LNB_HORIZONTAL
		else :
			return ElisEnum.E_LNB_VERTICAL


	def GetFECEnum( self, aFEC ) :
		if aFEC == 'DVBS_1_2' :
			return ElisEnum.E_DVBS_1_2
		elif aFEC == 'DVBS_2_3' :
			return ElisEnum.E_DVBS_2_3
		elif aFEC == 'DVBS_3_4' :
			return ElisEnum.E_DVBS_3_4
		elif aFEC == 'DVBS_5_6' :
			return ElisEnum.E_DVBS_5_6
		elif aFEC == 'DVBS_7_8' :
			return ElisEnum.E_DVBS_7_8
		elif aFEC == 'DVBS2_QPSK_1_2' :
			return ElisEnum.E_DVBS2_QPSK_1_2
		elif aFEC == 'DVBS2_QPSK_3_5' :
			return ElisEnum.E_DVBS2_QPSK_3_5
		elif aFEC == 'DVBS2_QPSK_2_3' :
			return ElisEnum.E_DVBS2_QPSK_2_3
		elif aFEC == 'DVBS2_QPSK_3_4' :
			return ElisEnum.E_DVBS2_QPSK_3_4
		elif aFEC == 'DVBS2_QPSK_4_5' :
			return ElisEnum.E_DVBS2_QPSK_4_5
		elif aFEC == 'DVBS2_QPSK_5_6' :
			return ElisEnum.E_DVBS2_QPSK_5_6
		elif aFEC == 'DVBS2_QPSK_8_9' :
			return ElisEnum.E_DVBS2_QPSK_8_9
		elif aFEC == 'DVBS2_QPSK_9_10' :
			return ElisEnum.E_DVBS2_QPSK_9_10
		elif aFEC == 'DVBS2_8PSK_3_5' :
			return ElisEnum.E_DVBS2_8PSK_3_5
		elif aFEC == 'DVBS2_8PSK_2_3' :
			return ElisEnum.E_DVBS2_8PSK_2_3
		elif aFEC == 'DVBS2_8PSK_3_4' :
			return ElisEnum.E_DVBS2_8PSK_3_4
		elif aFEC == 'DVBS2_8PSK_5_6' :
			return ElisEnum.E_DVBS2_8PSK_5_6
		elif aFEC == 'DVBS2_8PSK_8_9' :
			return ElisEnum.E_DVBS2_8PSK_8_9
		elif aFEC == 'DVBS2_8PSK_9_10' :
			return ElisEnum.E_DVBS2_8PSK_9_10


	def GetHDListEnum( self, aHDList ) :
		if aHDList == 'true' :
			return 1
		else :
			return 0


	def ChannelSearchConfigDVBT( self, aControlId ) :
		# Tuner type
		if aControlId == E_SpinEx07 :
			if self.GetSelectedIndex( E_SpinEx07 ) == 0 :
				self.mIsChannelSearch = False
			else :
				self.mIsChannelSearch = True
			self.DisableControl( )
			return

		elif aControlId == E_SpinEx03 :
			if ( self.mTunerType == E_TUNER_T or self.mTunerType == E_TUNER_T2 ) and self.GetSelectedIndex( E_SpinEx03 ) == E_TUNER_C :
				isChanged = True
			elif ( self.GetSelectedIndex( E_SpinEx03 ) == E_TUNER_T or self.GetSelectedIndex( E_SpinEx03 ) == E_TUNER_T2 ) and self.mTunerType == E_TUNER_C :
				isChanged = True
			else :
				isChanged = False

			self.mTunerType = self.GetSelectedIndex( E_SpinEx03 )
			if isChanged :
				self.SetListControl( E_STEP_CHANNEL_SEARCH_CONFIG_DVBT )
			else :
				self.DisableControl( )
			return

		if self.mTunerType == E_TUNER_T or self.mTunerType == E_TUNER_T2 :
			self.OperationDVBT( aControlId )
		elif self.mTunerType == E_TUNER_C :
			self.OperationDVBC( aControlId )


	def OperationDVBT( self, aControlId ) :
		# Manual Setup
		if aControlId == E_SpinEx01 :
			self.mIsManualSetup = self.GetSelectedIndex( E_SpinEx01 )
			self.DisableControl( E_SpinEx01 )
			return

		# Terrestrial list
		elif aControlId == E_Input04 :
			terrestrialList = self.GetTerrestriaList( )
			if terrestrialList :
				dialog = xbmcgui.Dialog( )
				ret = dialog.select( MR_LANG( 'Select Terrestrial' ), terrestrialList, False, StringToListIndex( terrestrialList, self.mTerrestrial ) )
				if ret >= 0 :
					if self.SetTerrestriaInfo( ret ) :
						self.SetControlLabel2String( E_Input04, self.mTerrestrial )
						#self.InitConfig( )
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'list not found' ) )
				dialog.doModal( )
			return

		# Frequency
		elif aControlId == E_Input01 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( MR_LANG( 'Enter Frequency' ), '%d' % self.mDVBT_Manual.mFrequency, 7 )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				#tempval = dialog.GetString( )
				#if int( tempval ) > 13000 :
				#	self.mConfigTransponder.mFrequency = 13000
				#elif int( tempval ) < 3000 :
				#	self.mConfigTransponder.mFrequency = 3000
				#else :
				#	self.mConfigTransponder.mFrequency = int( tempval )
				self.mDVBT_Manual.mFrequency = int( dialog.GetString( ) )
				self.SetControlLabel2String( E_Input01, '%d KHz' % self.mDVBT_Manual.mFrequency )
			else :
				return

		# plp id
		elif aControlId == E_Input02 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( MR_LANG( 'Enter PLP ID' ), '%d' % self.mDVBT_Manual.mPLPId, 3 )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				#tempval = dialog.GetString( )
				#if int( tempval ) > 13000 :
				#	self.mConfigTransponder.mFrequency = 13000
				#elif int( tempval ) < 3000 :
				#	self.mConfigTransponder.mFrequency = 3000
				#else :
				#	self.mConfigTransponder.mFrequency = int( tempval )
				self.mDVBT_Manual.mPLPId = int( dialog.GetString( ) )
				self.SetControlLabel2String( E_Input02, '%03d' % self.mDVBT_Manual.mPLPId )
			else :
				return

		# Bandwidth
		elif aControlId == E_SpinEx02 :
			self.mDVBT_Manual.mBand = self.GetSelectedIndex( E_SpinEx02 )

		elif aControlId == E_SpinEx04 or aControlId == E_SpinEx05 or aControlId == E_SpinEx06 :
			self.ControlSelect( )
			return

		# Start Search
		elif aControlId == E_FIRST_TIME_INSTALLATION_NEXT :
			if self.mIsChannelSearch == True :
				self.OpenBusyDialog( )
				ScanHelper.GetInstance( ).ScanHelper_Stop( self, False )

				if self.mIsManualSetup == 1 :
					carrierList = []
					carrierList.append( self.GetElisICarrier( ) )

					self.CloseBusyDialog( )
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
					dialog.SetCarrier( carrierList )
					dialog.doModal( )
					self.SetListControl( E_STEP_DATE_TIME )
					return
					#self.setProperty( 'ViewProgress', 'True' )

				elif self.mIsManualSetup == 0 :
					if self.mTerrestrial == 'None' or len( self.mDVBT_Auto ) == 0 :
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Select terrestrial first' ) )
						dialog.doModal( )
						self.CloseBusyDialog( )
						return

					self.CloseBusyDialog( )
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
					dialog.SetCarrier( self.mDVBT_Auto )
					dialog.doModal( )
					self.SetListControl( E_STEP_DATE_TIME )
					return
			else :
				ScanHelper.GetInstance( ).ScanHelper_Stop( self, False )
				self.CloseBusyDialog( )
				self.SetListControl( E_STEP_DATE_TIME )
				return

		ScanHelper.GetInstance( ).ScanHelper_ChangeContextByCarrier( self, self.GetElisICarrier( ) )


	def OperationDVBC( self, aControlId ) :
		# Start Search
		if aControlId == E_FIRST_TIME_INSTALLATION_NEXT :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Not support' ) )
			dialog.doModal( )
			self.SetListControl( E_STEP_DATE_TIME )
			return


	def GetElisICarrier( self ) :
		ICarrier = ElisICarrier( )
		if self.mTunerType == E_TUNER_T or self.mTunerType == E_TUNER_T2 :
			ICarrier.mCarrierType = ElisEnum.E_CARRIER_TYPE_DVBT
		else :
			ICarrier.mCarrierType = ElisEnum.E_CARRIER_TYPE_DVBC
		temp = deepcopy( self.mDVBT_Manual )
		temp.mBand = temp.mBand + 6
		if self.mTunerType == E_TUNER_T2 :
			temp.mIsDVBT2 = 1
		else :
			temp.mIsDVBT2 = 0
		ICarrier.mDVBT = temp
		temp.printdebug( )
		return ICarrier


	def SetTerrestriaInfo( self, aIndex ) :
		if not os.path.exists( FILE_TERRESTRIAL ) :
			return False

		try :
			self.mDVBT_Auto = []
			tree = ElementTree.parse( FILE_TERRESTRIAL )
			root = tree.getroot( )

			terrestrial = root.getchildren( )[ aIndex ]
			self.mTerrestrial = terrestrial.get( 'name' ).encode( 'utf-8' )

			for terrestrial in terrestrial.findall( 'transponder' ) :
				ICarrier = ElisICarrier( )
				ICarrier.mCarrierType = ElisEnum.E_CARRIER_TYPE_DVBT
				IDVBTCarrier = ElisIDVBTCarrier( )
				IDVBTCarrier.mFrequency = int( float( terrestrial.get( 'centre_frequency' ) ) / float( 1000 ) )
				IDVBTCarrier.mBand = 8 - int( terrestrial.get( 'bandwidth' ) )
				try :
					IDVBTCarrier.mIsDVBT2 = int( terrestrial.get( 'type' ) )
				except :
					IDVBTCarrier.mIsDVBT2 = 0
				if IDVBTCarrier.mIsDVBT2 == E_TUNER_T2 :
					IDVBTCarrier.mPLPId = int( terrestrial.get( 'plp_id' ) )
				IDVBTCarrier.printdebug()
				ICarrier.mDVBT = IDVBTCarrier
				self.mDVBT_Auto.append( ICarrier )

			return True
		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			self.mDVBT_Auto = []
			self.mTerrestrial = 'None'
			return False


	def GetTerrestriaList( self ) :
		if not os.path.exists( FILE_TERRESTRIAL ) :
			return None

		try :
			tree = ElementTree.parse( FILE_TERRESTRIAL )
			root = tree.getroot( )
			nameList = []

			for terrestrial in root.findall( 'terrestrial' ) :
				if terrestrial.get( 'name' ) != None :
					nameList.append( terrestrial.get( 'name' ).encode( 'utf-8' ) )

			if len( nameList ) > 0 :
				return nameList
			else :
				return None

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return None


	def CallballInputNumber( self, aGroupId, aString ) :
		if self.GetFTIStep( ) == E_STEP_CHANNEL_SEARCH_CONFIG :
			if aGroupId == E_Input02 :
				if self.mIsManualTp == 0 :
					self.mIsManualTp = 1
				self.mConfigTransponder.mFrequency = int( aString )
				self.SetControlLabel2String( aGroupId, aString + ' MHz' )
				if self.mConfigTransponder.mFrequency >= 3000 :
					self.StartScanHelper( )

			elif aGroupId == E_Input03 :
				self.mConfigTransponder.mSymbolRate = int( aString )
				self.SetControlLabel2String( aGroupId, aString + ' KS/s' )
				if self.mConfigTransponder.mSymbolRate >= 1000 :
					self.StartScanHelper( )

		elif self.GetFTIStep( ) == E_STEP_CHANNEL_SEARCH_CONFIG_DVBT :
			if aGroupId == E_Input01 :
				self.mDVBT_Manual.mFrequency = int( aString )
				self.SetControlLabel2String( aGroupId, aString + ' KHz' )
				if self.mDVBT_Manual.mFrequency < 10000000 :
					ScanHelper.GetInstance( ).ScanHelper_ChangeContextByCarrier( self, self.GetElisICarrier( ) )
			elif aGroupId == E_Input02 :
				self.mDVBT_Manual.mPLPId = int( aString )
				self.SetControlLabel2String( aGroupId, '%s' % self.mDVBT_Manual.mPLPId )
				if self.mDVBT_Manual.mPLPId < 1000 :
					ScanHelper.GetInstance( ).ScanHelper_ChangeContextByCarrier( self, self.GetElisICarrier( ) )


	def FocusChangedAction( self, aGroupId ) :
		if self.GetFTIStep( ) == E_STEP_CHANNEL_SEARCH_CONFIG :
			if aGroupId == E_Input02 and self.mConfigTransponder.mFrequency < 3000 :
				self.mConfigTransponder.mFrequency = 3000
				self.SetControlLabel2String( E_Input02, '%s MHz' % self.mConfigTransponder.mFrequency )
				self.StartScanHelper( )
				
			elif aGroupId == E_Input03 and self.mConfigTransponder.mSymbolRate < 1000 :
				self.mConfigTransponder.mSymbolRate = 1000
				self.SetControlLabel2String( E_Input03, '%s KS/s' % self.mConfigTransponder.mSymbolRate )
				self.StartScanHelper( )

		elif self.GetFTIStep( ) == E_STEP_CHANNEL_SEARCH_CONFIG_DVBT :
			if aGroupId == E_Input02 :
				self.SetControlLabel2String( aGroupId, '%03d' % self.mDVBT_Manual.mPLPId )


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
		if self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_DUAL :
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
		else :
			ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).SetProp( self.mTuner1Control )


	def LoadTunerProperty( self ) :
		if self.mPlatform.GetTunerType( ) == TUNER_TYPE_DVBS_DUAL :
			if ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( ) == E_ONE_CABLE :
				self.mTunerConnection		= E_TUNER_ONECABLE
				self.mTunerSignal			= E_SAMEWITH_TUNER
			else :
				self.mTunerConnection		= ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander ).GetProp( )
				self.mTunerSignal			= ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander ).GetProp( )
				self.mTuner1Control			= ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( )
				self.mTuner2Control			= ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).GetProp( )
		else :
			self.mTuner1Control	= ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( )

