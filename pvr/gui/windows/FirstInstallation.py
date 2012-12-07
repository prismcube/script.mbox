from pvr.gui.WindowImport import *
import pvr.TunerConfigMgr as ConfigMgr


class FirstInstallation( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mStepNum					= 	E_STEP_SELECT_LANGUAGE
		self.mPrevStepNum				= 	E_STEP_SELECT_LANGUAGE
		self.mAudioLanguageList			=	[]
		self.mIsChannelSearch			=	False
		self.mConfiguredSatelliteList 	=	[]
		self.mFormattedList				=	[]
		self.mSatelliteIndex			=	0
		self.mLastFocused				=	-1

		self.mDate				= 0
		self.mTime				= 0
		self.mSetupChannel		= None
		self.mHasChannel		= False

		self.mStepImage			= []

		for i in range( ElisPropertyEnum( 'Audio Language', self.mCommander ).GetIndexCount( ) ) :
			self.mAudioLanguageList.append( ElisPropertyEnum( 'Audio Language', self.mCommander ).GetPropStringByIndex( i ) )


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		self.getControl( E_SETTING_MINI_TITLE ).setLabel( MR_LANG( 'Installation' ) )
		self.SetPipScreen( )
		self.LoadNoSignalState( )
		self.SetListControl( self.mStepNum )
		self.SetPipLabel( )
		self.mLastFocused = self.getFocusId( )
		self.mInitialized = True
		if self.mDataCache.GetEmptySatelliteInfo( ) == True :
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( MR_LANG( 'No satellite data is available' ) )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No satellite data is available\nPlease factory reset your STB' )	)
			dialog.doModal( )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Do you want to go to configuration?' ) )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.ResetAllControl( )
				self.SetVideoRestore( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIGURE, WinMgr.WIN_ID_MAINMENU )
			else :
				self.ResetAllControl( )
				self.SetVideoRestore( )
				WinMgr.GetInstance( ).CloseWindow( )

		self.mDataCache.SetFristInstallation( True )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		if self.GlobalAction( actionId ) :
			return


		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			if self.mStepNum == E_STEP_RESULT :
				return
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Abort Installation' ), MR_LANG( 'Do you want to quit the first installation?' ) )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.Close( )
			elif dialog.IsOK( ) == E_DIALOG_STATE_NO :
				return	
			elif dialog.IsOK( ) == E_DIALOG_STATE_CANCEL :
				return

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )


	def onClick( self, aControlId ) :
		groupId = self.GetGroupId( aControlId )

		if self.mStepNum == E_STEP_SELECT_LANGUAGE :
			if groupId == E_FIRST_TIME_INSTALLATION_NEXT :
				self.setFocusId( E_FAKE_BUTTON )
				time.sleep( 0.3 )
				self.SetListControl( E_STEP_VIDEO_AUDIO )
			else :
				if groupId == E_Input01 :
					menuLanguageList = WinMgr.GetInstance( ).GetLanguageList( )
					dialog = xbmcgui.Dialog( )
					currentindex = StringToListIndex( menuLanguageList, self.GetControlLabel2String( E_Input01 ) )
					ret = dialog.select( MR_LANG( 'Select Menu Language' ), menuLanguageList, False, currentindex )
					if ret >= 0 and currentindex != ret :
						if not self.mPlatform.IsPrismCube( ) :
							dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
							dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'No support %s' ) % self.mPlatform.GetName( ) )
							dialog.doModal( )
							return

						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( MR_LANG( 'Change Language' ), MR_LANG( 'Please be patience after pressing the OK button' ), MR_LANG( 'It will take some time to bring up display changes' ) )
						dialog.doModal( )
						self.mInitialized = False
						self.OpenBusyDialog( )
						WinMgr.GetInstance( ).SetCurrentLanguage( menuLanguageList[ ret ] )
						
				elif groupId == E_Input02 :
					dialog = xbmcgui.Dialog( )
					ret = dialog.select( MR_LANG( 'Select Audio Language' ), self.mAudioLanguageList, False, StringToListIndex( self.mAudioLanguageList, self.GetControlLabel2String( E_Input02 ) ) )
					if ret >= 0 :
						ElisPropertyEnum( 'Audio Language', self.mCommander ).SetPropIndex( ret )
						self.SetControlLabel2String( E_Input02, self.mAudioLanguageList[ ret ] )

		elif self.mStepNum == E_STEP_VIDEO_AUDIO :
			if groupId == E_FIRST_TIME_INSTALLATION_NEXT :
				self.OpenAntennaSetupWindow( )
			else :
				self.ControlSelect( )

		elif self.mStepNum == E_STEP_CHANNEL_SEARCH_CONFIG :
			self.ChannelSearchConfig( groupId )

		elif self.mStepNum == E_STEP_DATE_TIME :
			self.TimeSetting( groupId )

		elif self.mStepNum == E_STEP_RESULT :
			if groupId == E_FIRST_TIME_INSTALLATION_NEXT :
				self.Close( )

		if groupId == E_FIRST_TIME_INSTALLATION_PREV :
			if self.mStepNum == E_STEP_CHANNEL_SEARCH_CONFIG :
				self.OpenAntennaSetupWindow( )
			else :
				self.setFocusId( E_FAKE_BUTTON )
				time.sleep( 0.3 )
				self.SetListControl( self.mPrevStepNum )


	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return
		if self.mLastFocused != aControlId :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId


	def Close( self ) :
		self.OpenBusyDialog( )
		self.ResetAllControl( )
		self.mStepNum = E_STEP_SELECT_LANGUAGE
		self.mDataCache.SetFristInstallation( False )
		self.mTunerMgr.SyncChannelBySatellite( )
		self.mDataCache.Channel_ReLoad( )
		self.mDataCache.Player_AVBlank( False )
		self.CloseBusyDialog( )
		self.SetVideoRestore( )
		if self.mStepNum == E_STEP_RESULT :
			self.mDataCache.Channel_TuneDefault( )
		WinMgr.GetInstance( ).CloseWindow( )


	def OpenAntennaSetupWindow( self ) :
		WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ANTENNA_SETUP )


	def SetResultAntennaStep( self, aResult ) :
		if aResult == True :
			self.mStepNum = E_STEP_CHANNEL_SEARCH_CONFIG
		else :
			self.mStepNum = E_STEP_VIDEO_AUDIO		


	def SetListControl( self, aStep ) :
		self.ResetAllControl( )
		self.mStepNum = aStep
		self.DrawFirstTimeInstallationStep( self.mStepNum )

		if self.mStepNum == E_STEP_SELECT_LANGUAGE :
			self.mPrevStepNum = E_STEP_SELECT_LANGUAGE
			self.getControl( E_SETTING_HEADER_TITLE ).setLabel( MR_LANG( 'Language Setup' ) )
			self.AddInputControl( E_Input01, MR_LANG( 'Menu Language' ), MR_LANG( WinMgr.GetInstance( ).GetCurrentLanguage( ) ), MR_LANG( 'Select the language you want the menu to be in' ) )
			self.AddInputControl( E_Input02, MR_LANG( 'Audio Language' ), self.mAudioLanguageList[ ElisPropertyEnum( 'Audio Language', self.mCommander ).GetPropIndex( ) ], MR_LANG( 'Select the language that you wish to listen to' ) )
			self.AddNextButton( MR_LANG( 'Go to the Video and Audio Setup page' ) )
			self.SetPrevNextButtonLabel( )

			visibleControlIds = [ E_Input01, E_Input02 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx01, E_SpinEx02, E_Input03, E_Input04, E_Input05, E_SpinEx03 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			self.setDefaultControl( )
			return

		elif self.mStepNum == E_STEP_VIDEO_AUDIO :
			self.mPrevStepNum = E_STEP_SELECT_LANGUAGE
			self.getControl( E_SETTING_HEADER_TITLE ).setLabel( MR_LANG( 'Video and Audio Setup' ) )
			self.AddEnumControl( E_SpinEx01, 'Show 4:3', MR_LANG( 'TV Screen Format' ), MR_LANG( 'Select the display format for TV screen' ) )
			self.AddEnumControl( E_SpinEx02, 'Audio Dolby', MR_LANG('Dolby Audio'), MR_LANG( 'When set to \'On\', Dolby Digital audio will be selected automatically when broadcast' ) )
			self.AddEnumControl( E_SpinEx03, 'HDMI Format', None, MR_LANG( 'Select the display\'s HDMI resolution' ) )
			self.AddPrevNextButton( MR_LANG( 'Go to the Antenna and Satellite Setup page' ), MR_LANG( 'Go back to the Language Setup page' ) )
			self.SetPrevNextButtonLabel( )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			self.setDefaultControl( )
			return

		elif self.mStepNum == E_STEP_CHANNEL_SEARCH_CONFIG :
			self.mPrevStepNum = E_STEP_VIDEO_AUDIO
			self.getControl( E_SETTING_HEADER_TITLE ).setLabel( MR_LANG( 'Channel Search Setup' ) )
			self.LoadFormattedSatelliteNameList( )
			self.AddUserEnumControl( E_SpinEx01, 'Channel Search', USER_ENUM_LIST_YES_NO, self.mIsChannelSearch, MR_LANG( 'Do you want to perform a channel search in the First Installation?' ) )
			self.AddInputControl( E_Input01, MR_LANG( 'Satellite' ), self.mFormattedList[ self.mSatelliteIndex ], MR_LANG( 'Select the satellite you wish to search from' ) )
			self.AddEnumControl( E_SpinEx02, 'Network Search', None, MR_LANG( 'When set to \'On\', new channels are searched from existing transponders and the additional transponders stored by transponder network however if you set this option to \'Off\', only the transponder you selected will be searched' ) )
			self.AddEnumControl( E_SpinEx03, 'Channel Search Mode', MR_LANG( 'Search Mode' ), MR_LANG( 'Select the type of channel you want to search for' ) )
			self.AddPrevNextButton( MR_LANG( 'Go to the Time and Date Setup page' ), MR_LANG( 'Go back to the Antenna and Satellite Setup page' ) )
			self.SetPrevNextButtonLabel( )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input01 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			time.sleep( 0.2 )
			self.DisableControl( self.mStepNum )
			self.setDefaultControl( )
			return

		elif self.mStepNum == E_STEP_DATE_TIME :
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

			self.AddEnumControl( E_SpinEx01, 'Time Mode', MR_LANG( 'Time and Date' ), MR_LANG( 'When set to \'Automatic\', the time will be obtained by the receiver automatically from a specific channel that you select') )
			self.AddInputControl( E_Input01, MR_LANG( 'Channel' ), channelName, MR_LANG( 'Select a channel you want to set your time and date by' ) )
			self.mDate = TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_DD_MM_YYYY )
			self.AddInputControl( E_Input02, MR_LANG( 'Date' ), self.mDate, MR_LANG( 'Enter today\'s date' ) )
			self.mTime = TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_HH_MM )
			self.AddInputControl( E_Input03, MR_LANG( 'Time' ), self.mTime, MR_LANG( 'Enter the local time' ) )
			self.AddEnumControl( E_SpinEx02, 'Local Time Offset', None, MR_LANG( 'Set the time zone that will be the basis for the date and time display' ) )
			self.AddEnumControl( E_SpinEx03, 'Summer Time', None, MR_LANG( 'When set to \'Automatic\', the system automatically change over to and from summer and winter time' ) )
			self.AddInputControl( E_Input04, MR_LANG( 'Apply' ), '', MR_LANG( 'Press the OK button to save time settings' ) )
			self.AddPrevNextButton( MR_LANG( 'Go to the Summary of First Installation page' ), MR_LANG( 'Go back to the Channel Search Setup page' ) )
			self.SetPrevNextButtonLabel( )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input01, E_Input02, E_Input03, E_Input04 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )
			self.InitControl( )
			time.sleep( 0.2 )
			self.DisableControl( self.mStepNum )
			self.setDefaultControl( )

			return

		elif self.mStepNum == E_STEP_RESULT :
			self.mPrevStepNum = E_STEP_DATE_TIME
			self.getControl( E_SETTING_HEADER_TITLE ).setLabel( MR_LANG( 'Summary of First Installation' ) )
			self.AddInputControl( E_Input01, MR_LANG( 'Menu Language' ), MR_LANG( WinMgr.GetInstance( ).GetCurrentLanguage( ) ) )
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
			self.AddPrevNextButton( MR_LANG( 'Return to the Installation page' ), MR_LANG( 'Go back to the Time and Date Setup page' ) )
			self.SetPrevNextButtonLabel( )

			visibleControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, False )

			hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )
			self.setDefaultControl( )
			return


	def SetPrevNextButtonLabel( self ) :
		if self.mStepNum == E_STEP_SELECT_LANGUAGE :
			self.SetVisibleControl( E_FIRST_TIME_INSTALLATION_PREV, False )
			self.getControl( E_FIRST_TIME_INSTALLATION_NEXT_LABEL ).setLabel( MR_LANG( 'Next' ) )

		elif self.mStepNum == E_STEP_RESULT :
			self.getControl( E_FIRST_TIME_INSTALLATION_PREV_LABEL ).setLabel( MR_LANG( 'Previous' ) )
			self.getControl( E_FIRST_TIME_INSTALLATION_NEXT_LABEL ).setLabel( MR_LANG( 'Finish' ) )

		else :
			self.SetVisibleControl( E_FIRST_TIME_INSTALLATION_PREV, True )
			self.getControl( E_FIRST_TIME_INSTALLATION_PREV_LABEL ).setLabel( MR_LANG( 'Previous' ) )
			self.getControl( E_FIRST_TIME_INSTALLATION_NEXT_LABEL ).setLabel( MR_LANG( 'Next' ) )


	def DisableControl( self, aStep ) :
		if self.mStepNum == E_STEP_CHANNEL_SEARCH_CONFIG :
			visibleControlIds = [ E_SpinEx02, E_SpinEx03, E_Input01 ]
			if self.GetSelectedIndex( E_SpinEx01 ) == 0 :
				self.SetEnableControls( visibleControlIds, False )
			else :
				self.SetEnableControls( visibleControlIds, True )

		elif self.mStepNum == E_STEP_DATE_TIME :
			if self.mHasChannel == False :
				self.SetEnableControl( E_SpinEx01, False )
				self.SetEnableControl( E_Input01, False )
			else :
				selectedIndex = self.GetSelectedIndex( E_SpinEx01 )
				if selectedIndex == TIME_AUTOMATIC :
					self.SetEnableControl( E_Input02, False )
					self.SetEnableControl( E_Input03, False )
					self.SetEnableControl( E_Input01, True )
					self.SetEnableControl( E_SpinEx02, True )
					self.SetEnableControl( E_SpinEx03, True )
				else :
					control = self.getControl( E_SpinEx02 + 3 )
					control1 = self.getControl( E_SpinEx03 + 3 )
					time.sleep( 0.02 )
					control.selectItem( ElisPropertyEnum( 'Local Time Offset', self.mCommander ).GetIndexByProp( 0 ) )
					control1.selectItem( SUMMER_TIME_OFF )
					
					self.SetEnableControl( E_Input01, False )
					self.SetEnableControl( E_Input02, True )
					self.SetEnableControl( E_Input03, True )					
					self.SetEnableControl( E_SpinEx02, False )
					self.SetEnableControl( E_SpinEx03, False )



	def LoadFormattedSatelliteNameList( self ) :
		self.mConfiguredSatelliteList = self.mDataCache.Satellite_GetConfiguredList( )
		self.mFormattedList = []
		if self.mConfiguredSatelliteList == None :
			self.mFormattedList.append( MR_LANG( 'None' ) )
		else :
			self.mFormattedList.append( MR_LANG( 'All' ) )
			for config in self.mConfiguredSatelliteList :
				self.mFormattedList.append( self.mDataCache.GetFormattedSatelliteName( config.mLongitude, config.mBand ) )


	def ChannelSearchConfig( self, aControlId ) :
		if aControlId == E_Input01 :
			dialog = xbmcgui.Dialog( )
			select =  dialog.select( MR_LANG( 'Select Satellite' ), self.mFormattedList )
			if select >= 0 and select != self.mSatelliteIndex :
				self.mSatelliteIndex = select
			self.SetControlLabel2String( E_Input01, self.mFormattedList[ self.mSatelliteIndex ] )

		elif aControlId == E_FIRST_TIME_INSTALLATION_NEXT :
			if self.mIsChannelSearch == True :
				if self.mConfiguredSatelliteList :
					if self.mSatelliteIndex == 0 :
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
						dialog.SetConfiguredSatellite( self.mConfiguredSatelliteList )
						dialog.doModal( )
						self.OpenBusyDialog( )
						zappingMode = self.mDataCache.Zappingmode_GetCurrent( True )		
						self.mDataCache.Channel_GetAllChannels( zappingMode.mServiceType, False )
						self.CloseBusyDialog( )				
						
					else :
						configuredSatelliteList = []
						config = self.mConfiguredSatelliteList[ self.mSatelliteIndex - 1 ]

						configuredSatelliteList.append( config )
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
						dialog.SetConfiguredSatellite( configuredSatelliteList )				
						dialog.doModal( )
						
						self.OpenBusyDialog( )
						zappingMode = self.mDataCache.Zappingmode_GetCurrent( True )		
						self.mDataCache.Channel_GetAllChannels( zappingMode.mServiceType, False )
						self.CloseBusyDialog( )				
						
				else :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'There is no configured satellite in the list' ) )
					dialog.doModal( )

				self.setFocusId( E_FAKE_BUTTON )
				time.sleep( 0.3 )
				self.SetListControl( E_STEP_DATE_TIME )
			else :
				self.setFocusId( E_FAKE_BUTTON )
				time.sleep( 0.3 )
				self.SetListControl( E_STEP_DATE_TIME )

		elif aControlId == E_SpinEx01 :
			if self.GetSelectedIndex( E_SpinEx01 ) == 0 :
				self.mIsChannelSearch = False
			else :
				self.mIsChannelSearch = True
			self.DisableControl( self.mStepNum )

		elif aControlId == E_SpinEx02 or aControlId == E_SpinEx03 :
			self.ControlSelect( )


	def TimeSetting( self, aControlId ) :
		if aControlId == E_SpinEx01 :
			self.DisableControl( self.mStepNum )

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
			self.mDate = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_DATE, MR_LANG( 'Today\'s date' ), self.mDate )
			self.SetControlLabel2String( E_Input02, self.mDate )

		elif aControlId == E_Input03 :
			self.mTime = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_TIME, MR_LANG( 'Local time' ), self.mTime )
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
				dialog.SetDialogProperty( 10, MR_LANG( 'Setting Time...' ), ElisEventTimeReceived.getName( ) )
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
				globalEvent = pvr.GlobalEvent.GetInstance()
				globalEvent.SendLocalOffsetToXBMC()

			self.CloseBusyDialog( )
			if mode == TIME_AUTOMATIC and dialog.GetResult( ) == False :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Automatic time setup has failed because' ), MR_LANG( 'no time info was given by the channel you selected' ) )
				dialog.doModal( )

		elif aControlId == E_FIRST_TIME_INSTALLATION_NEXT :
				self.setFocusId( E_FAKE_BUTTON )
				time.sleep( 0.3 )
				self.SetListControl( E_STEP_RESULT )
