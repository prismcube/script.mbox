from pvr.gui.WindowImport import *
import pvr.TunerConfigMgr as ConfigMgr


E_FAKE_BUTTON		=	999


class FirstInstallation( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mStepNum					= 	E_STEP_SELECT_LANGUAGE
		self.mPrevStepNum				= 	E_STEP_SELECT_LANGUAGE
		self.mIsChannelSearch			=	False
		self.mConfiguredSatelliteList 	=	[]
		self.mFormattedList				=	[]
		self.mSatelliteIndex			=	0

		self.mDate				= 0
		self.mTime				= 0
		self.mSetupChannel		= None
		self.mHasChannel		= False

		self.mStepImage			= []


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		self.getControl( E_SETTING_MINI_TITLE ).setLabel( 'First Installation' )
		self.SetPipScreen( )
		self.SetListControl( self.mStepNum )
		self.mInitialized = True
		ConfigMgr.GetInstance( ).SetFristInstallation( True )

		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )

		self.GlobalAction( actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			if self.mStepNum == E_STEP_RESULT :
				return
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( 'Are you sure?', 'Do you want to stop first time installation?' )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.Close( )
			elif dialog.IsOK( ) == E_DIALOG_STATE_NO :
				return	
			elif dialog.IsOK( ) == E_DIALOG_STATE_CANCEL :
				return
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			if self.mStepNum == E_STEP_RESULT :
				return
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( 'Are you sure?', 'Do you want to stop first time installation?' )
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
				self.ControlSelect( )
			return

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
		self.ResetAllControl( )
		self.SetVideoRestore( )
		self.mStepNum = E_STEP_SELECT_LANGUAGE
		ConfigMgr.GetInstance( ).SetFristInstallation( False )		
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
			self.getControl( E_SETTING_HEADER_TITLE ).setLabel( 'Select Language' )
			self.AddEnumControl( E_SpinEx01, 'Language', None, 'Select Language & Location' )
			self.AddEnumControl( E_SpinEx02, 'Audio Language' )
			self.AddNextButton( )
			self.SetPrevNextButtonLabel( )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_SpinEx03 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			self.SetFocusControl( E_SpinEx01 )
			return

		elif self.mStepNum == E_STEP_VIDEO_AUDIO :
			self.mPrevStepNum = E_STEP_SELECT_LANGUAGE
			self.getControl( E_SETTING_HEADER_TITLE ).setLabel( 'Video & Audio Setup' )
			self.AddEnumControl( E_SpinEx01, 'Show 4:3', 'TV Screen Format', 'Select Video & Audio Type' )
			self.AddEnumControl( E_SpinEx02, 'Audio Dolby' )
			self.AddEnumControl( E_SpinEx03, 'HDMI Format' )
			self.AddPrevNextButton( )
			self.SetPrevNextButtonLabel( )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			self.SetFocusControl( E_SpinEx01 )
			return

		elif self.mStepNum == E_STEP_CHANNEL_SEARCH_CONFIG :
			self.mPrevStepNum = E_STEP_VIDEO_AUDIO
			self.getControl( E_SETTING_HEADER_TITLE ).setLabel( 'Channel Search Setup' )
			self.LoadFormattedSatelliteNameList( )
			self.AddUserEnumControl( E_SpinEx01, 'Channel Search', USER_ENUM_LIST_YES_NO, self.mIsChannelSearch, 'Select Search Option' )
			self.AddInputControl( E_Input01, 'Satellite', self.mFormattedList[ self.mSatelliteIndex ] )
			self.AddEnumControl( E_SpinEx02, 'Network Search' )
			self.AddEnumControl( E_SpinEx03, 'Channel Search Mode' )
			self.AddPrevNextButton( )
			self.SetPrevNextButtonLabel( )
			
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input01 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			self.SetFocusControl( E_SpinEx01 )
			return

		elif self.mStepNum == E_STEP_DATE_TIME :
			self.mPrevStepNum = E_STEP_CHANNEL_SEARCH_CONFIG
			self.getControl( E_SETTING_HEADER_TITLE ).setLabel( 'Time Setting' )
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
					ElisPropertyEnum( 'Time Mode', self.mCommander ).SetProp( TIME_MANUAL )

			self.AddEnumControl( E_SpinEx01, 'Time Mode', None, 'Select Time Setting Option')			
			self.AddInputControl( E_Input01, 'Channel', channelName )
			self.mDate = TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_DD_MM_YYYY )
			self.AddInputControl( E_Input02, 'Date', self.mDate )
			self.mTime = TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_HH_MM )
			self.AddInputControl( E_Input03, 'Time', self.mTime )
			self.AddEnumControl( E_SpinEx02, 'Local Time Offset' )
			self.AddEnumControl( E_SpinEx03, 'Summer Time' )
			self.AddInputControl( E_Input04, 'Apply', '' )
			self.AddPrevNextButton( )
			self.SetPrevNextButtonLabel( )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input01, E_Input02, E_Input03, E_Input04 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_Input05 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			if self.mHasChannel == False :
				self.SetFocusControl( E_Input02 )
			else :
				self.SetFocusControl( E_SpinEx01 )
			self.DisableControl( self.mStepNum )
			return

		elif self.mStepNum == E_STEP_RESULT :
			self.mPrevStepNum = E_STEP_DATE_TIME
			self.getControl( E_SETTING_HEADER_TITLE ).setLabel( 'Result' )
			self.AddInputControl( E_Input01, 'Language', 'English', 'Check Result' )
			self.mDate = TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_DD_MM_YYYY )
			self.AddInputControl( E_Input02, 'Date', self.mDate )
			self.mTime = TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_HH_MM )
			self.AddInputControl( E_Input03, 'Time', self.mTime )
			channelList = self.mDataCache.Channel_GetList( )
			cntChannel = 0
			cntRadio = 0
			if channelList and channelList[0].mError == 0 :
				for channel in channelList :
					if channel.mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
						cntChannel = cntChannel + 1
					elif channel.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
						cntRadio = cntRadio + 1
			self.AddInputControl( E_Input04, 'TV Channels', '%d' % cntChannel )
			self.AddInputControl( E_Input05, 'Radio Channels', '%d' % cntRadio )
			self.AddPrevNextButton( )
			self.SetPrevNextButtonLabel( )
			
			visibleControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03 ]
			self.SetVisibleControls( hideControlIds, False )
			
			self.InitControl( )
			self.SetFocusControl( E_Input01 )
			return

	def SetPrevNextButtonLabel( self ) :
		if self.mStepNum == E_STEP_SELECT_LANGUAGE :
			self.SetVisibleControl( E_FIRST_TIME_INSTALLATION_PREV, False )
			self.getControl( E_FIRST_TIME_INSTALLATION_NEXT_LABEL ).setLabel( 'Next' )

		elif self.mStepNum == E_STEP_RESULT :
			self.getControl( E_FIRST_TIME_INSTALLATION_NEXT_LABEL ).setLabel( 'Finish' )

		else :
			self.SetVisibleControl( E_FIRST_TIME_INSTALLATION_PREV, True )
			self.getControl( E_FIRST_TIME_INSTALLATION_NEXT_LABEL ).setLabel( 'Next' )


	def DisableControl( self, aStep ) :			
		if self.mStepNum == E_STEP_DATE_TIME :
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


	def LoadFormattedSatelliteNameList( self ) :
		self.mConfiguredSatelliteList = self.mDataCache.Satellite_GetConfiguredList( )
		self.mFormattedList = []
		if self.mConfiguredSatelliteList == None :
			self.mFormattedList.append( 'None' )
		else :
			self.mFormattedList.append( 'All' )

			for config in self.mConfiguredSatelliteList :
				self.mFormattedList.append( self.mDataCache.GetFormattedSatelliteName( config.mLongitude, config.mBand ) )


	def ChannelSearchConfig( self, aControlId ) :
		if aControlId == E_Input01 :
			dialog = xbmcgui.Dialog( )
			select =  dialog.select( 'Select satellite', self.mFormattedList )

			if select >= 0 and select != self.mSatelliteIndex :
				self.mSatelliteIndex = select
			self.SetControlLabel2String( E_Input01, self.mFormattedList[ self.mSatelliteIndex ] )
			
		elif aControlId == E_FIRST_TIME_INSTALLATION_NEXT :
			if self.mIsChannelSearch == True :
				if self.mConfiguredSatelliteList :
					if self.mSatelliteIndex == 0 :
						dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
						dialog.SetConfiguredSatellite( self.mConfiguredSatelliteList )
						dialog.doModal( )
					else :
						configuredSatelliteList = []
						config = self.mConfiguredSatelliteList[ self.mSatelliteIndex - 1 ]

						configuredSatelliteList.append( config )
						dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
						dialog.SetConfiguredSatellite( configuredSatelliteList )				
						dialog.doModal( )
				else :
					dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( 'ERROR', 'Has No Configurd Satellite' )
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
 			ret = dialog.select( 'Select Channel', channelNameList )

			if ret >= 0 :
				self.mSetupChannel = channelList[ ret ]
				self.SetControlLabel2String( E_Input01, self.mSetupChannel.mName )

		elif aControlId == E_Input02 :
			self.mDate = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_DATE, 'Input Date', self.mDate )
			self.SetControlLabel2String( E_Input02, self.mDate )
			
		elif aControlId == E_Input03 :
			self.mTime = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_TIME, 'Input Time', self.mTime )
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
 			
			if ElisPropertyEnum( 'Time Mode', self.mCommander ).GetProp( ) == TIME_AUTOMATIC :
				ElisPropertyInt( 'Time Setup Channel Number', self.mCommander ).SetProp( self.mSetupChannel.mNumber )
				self.mDataCache.Channel_SetCurrent( self.mSetupChannel.mNumber, self.mSetupChannel.mServiceType ) # Todo After : using ServiceType to different way
				ElisPropertyEnum( 'Time Installation', self.mCommander ).SetProp( 1 )

				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_FORCE_PROGRESS )
				dialog.SetDialogProperty( 10, 'Setting Time...', ElisEventTimeReceived.getName( ) )
				dialog.doModal( )

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
				sumtime = self.mDate + '.' + self.mTime
				t = time.strptime( sumtime, '%d.%m.%Y.%H:%M' )
				ret = self.mCommander.Datetime_SetSystemUTCTime( int( time.mktime( t ) ) )
				self.mDataCache.LoadTime( )

		elif aControlId == E_FIRST_TIME_INSTALLATION_NEXT :
				self.setFocusId( E_FAKE_BUTTON )
				time.sleep( 0.3 )
				self.SetListControl( E_STEP_RESULT )
