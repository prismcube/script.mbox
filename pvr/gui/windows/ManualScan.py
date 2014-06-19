from pvr.gui.WindowImport import *
import pvr.ScanHelper as ScanHelper

E_MANUAL_SCAN_BASE_ID = WinMgr.WIN_ID_MANUAL_SCAN * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 


class ManualScan( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mSatelliteIndex			= 0
		self.mTransponderIndex			= 0
		self.mTransponderList			= []
		self.mIsManualSetup 			= 0

		self.mFormattedList				= []
		self.mConfigTransponder			= None
		self.mHasTansponder				= False
		self.mAvBlankStatus				= False


	def onInit( self ) :
		self.SetFrontdisplayMessage( MR_LANG('Manual Scan') )		
		self.mWinId = xbmcgui.getCurrentWindowId( )

		self.SetSettingWindowLabel( MR_LANG( 'Manual Scan' ) )
		self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'Installation' ), MR_LANG( 'Channel Search' ) ) )

		self.mIsManualSetup = 0
		self.mSatelliteIndex = 0
		self.mTransponderIndex = 0
		self.mConfiguredSatelliteList = []
		self.LoadFormattedSatelliteNameList( )
		self.SetSingleWindowPosition( E_MANUAL_SCAN_BASE_ID )

		hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06 ]
		if len( self.mConfiguredSatelliteList ) > 0 :
			self.mAvBlankStatus = self.mDataCache.Get_Player_AVBlank( )
			self.mDataCache.Player_AVBlank( True )
			self.mEventBus.Register( self )
			self.SetVisibleControls( hideControlIds, True )
			self.LoadTransponderList( )
			self.SetConfigTransponder( )
			self.InitConfig( )
			ScanHelper.GetInstance( ).ScanHelper_Start( self )
			ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex ], self.mConfigTransponder )
			self.mInitialized = True
			self.SetDefaultControl( )
		else :
			self.SetVisibleControls( hideControlIds, False )
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( MR_LANG( 'No configured satellite available' ) )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Make sure your antenna is properly set up' ) )
 			dialog.doModal( )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Go to the antenna setup page now?' ), MR_LANG( 'To receive a strong satellite signal,%s add satellites and set LNB parameters correctly' )% NEW_LINE )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ANTENNA_SETUP, WinMgr.WIN_ID_MAINMENU )
			else :
				WinMgr.GetInstance( ).CloseWindow( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )

		self.GlobalSettingAction( self, actionId )
		
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.OpenBusyDialog( )
			self.ResetAllControl( )
			self.mEventBus.Deregister( self )
			ScanHelper.GetInstance( ).ScanHelper_Stop( self )
			self.CloseBusyDialog( )
			if self.mAvBlankStatus :
				if not self.mDataCache.Get_Player_AVBlank( ) :
					self.mDataCache.Player_AVBlank( True )
			else :
				if self.mDataCache.Get_Player_AVBlank( ) :
					self.mDataCache.Player_AVBlank( False )

			WinMgr.GetInstance( ).CloseWindow( )

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

		# Satellite		
		if groupId == E_Input01 :
			dialog = xbmcgui.Dialog( )
			select = dialog.select( MR_LANG( 'Select Satellite' ), self.mFormattedList, False,  self.mSatelliteIndex )

			if select >= 0 :
				self.mSatelliteIndex = select
				self.mTransponderIndex = 0
				self.LoadTransponderList( )
				self.SetConfigTransponder( )
				self.InitConfig( )
			else :
				return

		# Transponder
		elif groupId == E_Input02 :
			if self.mIsManualSetup == 0 :
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
					self.SetConfigTransponder( )
					self.InitConfig( )
				else :
					return

			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
				dialog.SetDialogProperty( MR_LANG( 'Enter TP Frequency' ), '%d' % self.mConfigTransponder.mFrequency, 5 )
				dialog.doModal( )
				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					tempval = dialog.GetString( )
					if int( tempval ) > 13000 :
						self.mConfigTransponder.mFrequency = 13000
					elif int( tempval ) < 3000 :
						self.mConfigTransponder.mFrequency = 3000
					else :
						self.mConfigTransponder.mFrequency = int( tempval )

					self.SetControlLabel2String( E_Input02, '%d MHz' % self.mConfigTransponder.mFrequency )
				else :
					return

		# Symbol Rate
		elif groupId == E_Input03 :
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
			else :
				return

		# Start Search
		elif groupId == E_Input04 :
			self.OpenBusyDialog( )
			ScanHelper.GetInstance( ).ScanHelper_Stop( self, False )
			
			transponderList = []
 			config = self.mConfiguredSatelliteList[ self.mSatelliteIndex ]
			transponderList.append( self.mConfigTransponder )

			self.CloseBusyDialog( )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
			dialog.SetTransponder( config.mSatelliteLongitude, config.mBandType, transponderList, self.mIsManualSetup )
			dialog.doModal( )
			self.setProperty( 'ViewProgress', 'True' )

		# Manual Setup
		elif groupId == E_SpinEx01 :
			self.mIsManualSetup = self.GetSelectedIndex( E_SpinEx01 )
			self.InitConfig( )
			return

		# DVB Type
		elif groupId == E_SpinEx02 :
			if self.GetSelectedIndex( E_SpinEx02 ) == 0 :
				self.mConfigTransponder.mFECMode = ElisEnum.E_FEC_UNDEFINED		
			else :
				self.mConfigTransponder.mFECMode = ElisEnum.E_DVBS2_QPSK_1_2
	
			self.DisableControl( )

		# FEC
		elif groupId == E_SpinEx03 :
			self.ControlSelect( )
			property = ElisPropertyEnum( 'FEC', self.mCommander )
			self.mConfigTransponder.mFECMode = property.GetProp( )

		# Polarization
		elif groupId == E_SpinEx04 :
			self.mConfigTransponder.mPolarization = self.GetSelectedIndex( E_SpinEx04 )

		elif groupId == E_SpinEx05 or groupId == E_SpinEx06   :
			self.ControlSelect( )
			return

		ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex ], self.mConfigTransponder )


	def onFocus( self, aControlId ) :
		if self.mInitialized :
			self.ShowDescription( aControlId )


	def onEvent( self, aEvent ) :
		if xbmcgui.getCurrentWindowId( ) == self.mWinId :
			if aEvent.getName( ) == ElisEventTuningStatus.getName( ) :
				self.UpdateStatus( aEvent )


	def UpdateStatus( self, aEvent ) :
		if aEvent.mFrequency == self.mConfigTransponder.mFrequency :
			ScanHelper.GetInstance( ).ScanHerper_Progress( self, aEvent.mSignalStrength, aEvent.mSignalQuality, aEvent.mIsLocked )
			if aEvent.mIsLocked :
				if self.mDataCache.Get_Player_AVBlank( ) :
					self.mDataCache.Player_AVBlank( False )
			else :
				if not self.mDataCache.Get_Player_AVBlank( ) :
					self.mDataCache.Player_AVBlank( True )


	def InitConfig( self ) :
		self.ResetAllControl( )
		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( False )

		self.AddInputControl( E_Input01, MR_LANG( 'Satellite' ), self.mFormattedList[ self.mSatelliteIndex ], MR_LANG( 'Select the satellite on which the transponder you wish to scan is located' ) )
		self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Custom Setup' ), USER_ENUM_LIST_ON_OFF, self.mIsManualSetup, MR_LANG( 'Enable/Disable custom setup' ) )

		if self.mIsManualSetup == 0 :
			description = MR_LANG( 'Select the transponder frequency for the selected satellite' )
		else :
			description = MR_LANG( 'Enter the transponder frequency for the selected satellite' )
			
		self.AddInputControl( E_Input02, MR_LANG( ' - Transponder Frequency' ), '%d MHz' % self.mConfigTransponder.mFrequency, description, aInputNumberType = TYPE_NUMBER_NORMAL, aMax = 13000 )

		# DVB Type
		self.AddEnumControl( E_SpinEx02, 'DVB Type', MR_LANG( ' - DVB Type' ), MR_LANG( 'Select the Digital Video Broadcasting type for the selected satellite' ) )

		if self.mConfigTransponder.mFECMode == ElisEnum.E_FEC_UNDEFINED :
			self.SetProp( E_SpinEx02, 0 )
		else :
			self.SetProp( E_SpinEx02, 1 )

		# FEC
		self.AddEnumControl( E_SpinEx03, 'FEC', MR_LANG( ' - FEC' ), MR_LANG( 'Select the error control mode of data transmission for the selected satellite' ) )
		self.SetProp( E_SpinEx03, self.mConfigTransponder.mFECMode )

		# POL
		self.AddEnumControl( E_SpinEx04, 'Polarisation', MR_LANG( ' - Polarization' ), MR_LANG( 'Select the direction of the electrical and magnetic fields of signals for the satellite above' ) )
		self.SetProp( E_SpinEx04, self.mConfigTransponder.mPolarization )

		# Symbolrate
		self.AddInputControl( E_Input03, MR_LANG( ' - Symbol Rate' ), '%d KS/s' % self.mConfigTransponder.mSymbolRate , MR_LANG( 'Set the amount of data, that is transmitted per second in the data stream' ), aInputNumberType = TYPE_NUMBER_NORMAL, aMax = 60000 )
		networkSearchDescription = '%s %s' % ( MR_LANG( 'When set to \'Off\', only the factory default transponders of the satellites you previously selected will be scanned for new channels.'), MR_LANG('If you set to \'On\', both the existing transponders and additional transponders that have not yet been stored to be located are scanned for new channels' ) )
		self.AddEnumControl( E_SpinEx05, 'Network Search', None, networkSearchDescription )
		self.AddEnumControl( E_SpinEx06, 'Channel Search Mode', MR_LANG( 'Search Type' ), MR_LANG( 'Select whether you wish to scan free and scrambled, free only or scrambled only' ) )
		self.AddInputControl( E_Input04, MR_LANG( 'Start Search' ), '', MR_LANG( 'Press OK button to start a channel search' ) )

		self.InitControl( )
		self.DisableControl( )
		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( True )


	def LoadFormattedSatelliteNameList( self ) :
		self.mConfiguredSatelliteList = []

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
			self.mFormattedList = []
			for config in self.mConfiguredSatelliteList :
				self.mFormattedList.append( self.mDataCache.GetFormattedSatelliteName( config.mSatelliteLongitude, config.mBandType ) )


	def LoadTransponderList( self ) :
		satellite = self.mConfiguredSatelliteList[ self.mSatelliteIndex ]
		self.mTransponderList = []
		self.mTransponderList = self.mDataCache.GetTransponderListBySatellite( satellite.mSatelliteLongitude, satellite.mBandType )
		if self.mTransponderList and self.mTransponderList[0].mError == 0 :
			self.mTransponderList.sort( self.ByFrequency )
			self.mHasTansponder = True
		else :
			self.mHasTansponder = False


	def ByFrequency( self, aArg1, aArg2 ) :
		return cmp( aArg1.mFrequency, aArg2.mFrequency )


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


	def DisableControl( self ) :
		disablecontrols = [ E_Input02, E_Input03, E_Input04, E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06 ]
		if self.mHasTansponder :
			self.SetEnableControls( disablecontrols, True )

			disablecontrols = [ E_SpinEx02, E_SpinEx03, E_SpinEx04, E_Input03 ]
			if self.mIsManualSetup == 0 :
				self.SetEnableControls( disablecontrols, False )
			else :
				self.SetEnableControls( disablecontrols, True )

				if self.mConfigTransponder.mFECMode == 0 :
					self.getControl( E_SpinEx03 + 3 ).getListItem( 0 ).setLabel2( MR_LANG( 'Automatic' ) )
					self.getControl( E_SpinEx03 + 3 ).selectItem( 0 )
					self.SetEnableControl( E_SpinEx03, False )
				else :
					self.SetProp( E_SpinEx03, 0 )
					self.getControl( E_SpinEx03 + 3 ).getListItem( 0 ).setLabel2( MR_LANG( 'QPSK 1/2' ) )
					self.SetEnableControl( E_SpinEx03, True )
		else :
			self.SetEnableControls( disablecontrols, False )


	def CallballInputNumber( self, aGroupId, aString ) :
		if aGroupId == E_Input02 :
			if self.mIsManualSetup == 0 :
				self.mIsManualSetup = 1
				self.InitConfig( )
			self.mConfigTransponder.mFrequency = int( aString )
			self.SetControlLabel2String( aGroupId, aString + ' MHz' )
			if self.mConfigTransponder.mFrequency >= 3000 :
				ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex ], self.mConfigTransponder )

		elif aGroupId == E_Input03 :
			self.mConfigTransponder.mSymbolRate = int( aString )
			self.SetControlLabel2String( aGroupId, aString + ' KS/s' )
			if self.mConfigTransponder.mSymbolRate >= 1000 :
				ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex ], self.mConfigTransponder )


	def FocusChangedAction( self, aGroupId ) :
		if aGroupId == E_Input02 and self.mConfigTransponder.mFrequency < 3000 :
			self.mConfigTransponder.mFrequency = 3000
			self.SetControlLabel2String( E_Input02, '%s MHz' % self.mConfigTransponder.mFrequency )
			ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex ], self.mConfigTransponder )
			
		elif aGroupId == E_Input03 and self.mConfigTransponder.mSymbolRate < 1000 :
			self.mConfigTransponder.mSymbolRate = 1000
			self.SetControlLabel2String( E_Input03, '%s KS/s' % self.mConfigTransponder.mSymbolRate )
			ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex ], self.mConfigTransponder )

