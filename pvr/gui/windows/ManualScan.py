from pvr.gui.WindowImport import *
import pvr.ScanHelper as ScanHelper


class ManualScan( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mSatelliteIndex			= 0
		self.mTransponderIndex			= 0
		self.mTransponderList			= []

		self.mFormattedList	= []
		self.mIsManualSetup				= 0
		self.mConfigTransponder			= None
		self.mHasTansponder				= False


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		self.mEventBus.Register( self )
		ScanHelper.GetInstance( ).ScanHelper_Start( self.mWin )

		self.SetSettingWindowLabel( 'Manual Scan' )
		self.mIsManualSetup = 0
		
		self.mSatelliteIndex = 0
		self.mTransponderIndex = 0		
		self.mConfiguredSatelliteList = []
		
		self.LoadFormattedSatelliteNameList( )
		if len( self.mConfiguredSatelliteList ) > 0 :
			if self.getControl( E_SETTING_DESCRIPTION ).getLabel( ) == 'Has no configured satellite' :
				hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06 ]
				self.SetVisibleControls( hideControlIds, True )
			self.LoadTransponderList( )
			self.SetConfigTransponder( )
			self.InitConfig( )
			self.mInitialized = True
			self.SetFocusControl( E_Input01 )
			ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self.mWin, self.mConfiguredSatelliteList[ self.mSatelliteIndex ], self.mConfigTransponder )
		else :
			hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06 ]
			self.SetVisibleControls( hideControlIds, False )
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Has no configured satellite' )
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( 'ERROR', 'Has No Configurd Satellite' )
 			dialog.doModal( )
			WinMgr.GetInstance().CloseWindow( )

		
	def onAction( self, aAction ) :

		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		self.GlobalAction( actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.ResetAllControl( )
			ScanHelper.GetInstance( ).ScanHelper_Stop( self.mWin )
			WinMgr.GetInstance().CloseWindow( )
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			ScanHelper.GetInstance( ).ScanHelper_Stop( self.mWin )
			WinMgr.GetInstance().CloseWindow( )

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

		# Satellite		
		if groupId == E_Input01 :
			dialog = xbmcgui.Dialog( )
			select = dialog.select('Select satellite', self.mFormattedList )

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
					formattedTransponderList.append( '%d' % self.mTransponderList[i].mFrequency + ' MHz' )
				dialog = xbmcgui.Dialog( )
				select = dialog.select('Select Transponder', formattedTransponderList )

				if select >=0 :
					self.mTransponderIndex = select
					self.SetConfigTransponder( )
					self.InitConfig( )
				else :
					return

			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
				dialog.SetDialogProperty( 'Frequency', '%d' % self.mConfigTransponder.mFrequency, 5 )
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
			dialog.SetDialogProperty( 'Symbol Rate', '%d' % self.mConfigTransponder.mSymbolRate, 5 )
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
		elif groupId == E_Input04 : #ToDO : Have to support manual input
			ScanHelper.GetInstance( ).ScanHelper_Stop( self.mWin, False )
			transponderList = []
 			config = self.mConfiguredSatelliteList[ self.mSatelliteIndex ]

			transponderList.append( self.mConfigTransponder )

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
			dialog.SetTransponder( config.mSatelliteLongitude, config.mBandType, transponderList )
			dialog.doModal( )
			ScanHelper.GetInstance( ).ScanHelper_Start( self.mWin )

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

		ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self.mWin, self.mConfiguredSatelliteList[ self.mSatelliteIndex ], self.mConfigTransponder )


	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return

		if self.mLastFocused != aControlId :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId


	@GuiLock
	def onEvent( self, aEvent ) :
		if xbmcgui.getCurrentWindowId( ) == self.mWinId :
			if aEvent.getName( ) == ElisEventTuningStatus.getName( ) :
				self.UpdateStatus( aEvent )


	def UpdateStatus( self, aEvent ) :
		if aEvent.mFrequency == self.mConfigTransponder.mFrequency :
			ScanHelper.GetInstance( ).ScanHerper_Progress( self.mWin, aEvent.mSignalStrength, aEvent.mSignalQuality, aEvent.mIsLocked )


	def InitConfig( self ) :
		self.ResetAllControl( )	

		self.AddInputControl( E_Input01, 'Satellite', self.mFormattedList[ self.mSatelliteIndex ], 'Select satellite' )
		self.AddUserEnumControl( E_SpinEx01, 'Custom Setup', USER_ENUM_LIST_ON_OFF, self.mIsManualSetup, 'Control Custom Setup' )

		if self.mIsManualSetup == 0 :
			self.AddInputControl( E_Input02, ' - Select Transponder Frequency', '%d MHz' % self.mConfigTransponder.mFrequency, 'Select Transponder Frequency' )
		else :
			self.AddInputControl( E_Input02, ' - Set Frequency', '%d MHz' % self.mConfigTransponder.mFrequency, 'Input Manual Frequency' )

		# DVB Type
		self.AddEnumControl( E_SpinEx02, 'DVB Type', ' - DVB Type', 'Select DVB Type' )

		if self.mConfigTransponder.mFECMode == ElisEnum.E_FEC_UNDEFINED :
			self.SetProp( E_SpinEx02, 0 )
		else :
			self.SetProp( E_SpinEx02, 1 )

		# FEC
		self.AddEnumControl( E_SpinEx03, 'FEC', ' - FEC', 'Select FEC' )
		self.SetProp( E_SpinEx03, self.mConfigTransponder.mFECMode )

		# POL
		self.AddEnumControl( E_SpinEx04, 'Polarisation', ' - Polarization', 'Select Polarization' )
		self.SetProp( E_SpinEx04, self.mConfigTransponder.mPolarization )

		# Symbolrate
		self.AddInputControl( E_Input03, ' - Symbol Rate', '%d KS/s' % self.mConfigTransponder.mSymbolRate , 'Select Symbol Rate' )
		
		self.AddEnumControl( E_SpinEx05, 'Network Search', None, 'Select Network Search' )
		self.AddEnumControl( E_SpinEx06, 'Channel Search Mode',None, 'Select Channel Search Mode' )
		self.AddInputControl( E_Input04, 'Start Search', '', 'Start Search' )

		self.InitControl( )
		self.DisableControl( )


	def LoadFormattedSatelliteNameList( self ) :
		self.mConfiguredSatelliteList = []

		configuredSatelliteList1 = self.mDataCache.GetConfiguredSatelliteListByTunerIndex( E_TUNER_1 )
		configuredSatelliteList2 = self.mDataCache.GetConfiguredSatelliteListByTunerIndex( E_TUNER_2 )

		if configuredSatelliteList1 and configuredSatelliteList1[0].mError == 0 :
			self.mConfiguredSatelliteList = deepcopy( configuredSatelliteList1 )

		if self.mTunerMgr.GetCurrentTunerConfigType( ) == E_DIFFERENT_TUNER :
			if configuredSatelliteList2 and configuredSatelliteList2[0].mError == 0 :
				for config in configuredSatelliteList2 :
					find = False
					for compare in configuredSatelliteList1 :
						if ( config.mSatelliteLongitude == compare.mSatelliteLongitude ) and ( config.mBandType == compare.mBandType ) :
							find = True
							break

					if find == False :
						self.mConfiguredSatelliteList.append( config )

		if len( self.mConfiguredSatelliteList ) > 0 :
			self.mFormattedList = []
			for config in self.mConfiguredSatelliteList :
				self.mFormattedList.append( self.mDataCache.GetFormattedSatelliteName( config.mSatelliteLongitude, config.mBandType ) )


	def LoadTransponderList( self ) :
		satellite = self.mConfiguredSatelliteList[ self.mSatelliteIndex ]
		self.mTransponderList = []
		self.mTransponderList = self.mDataCache.GetTransponderListBySatellite( satellite.mSatelliteLongitude, satellite.mBandType )
		if self.mTransponderList and self.mTransponderList[0].mError == 0 :
			self.mHasTansponder = True
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


	def DisableControl( self ) :	
		disablecontrols = [ E_SpinEx02, E_SpinEx03, E_SpinEx04, E_Input03 ]
		if self.mIsManualSetup == 0 :
			self.SetEnableControls( disablecontrols, False )
		else :
			self.SetEnableControls( disablecontrols, True )

			if self.mConfigTransponder.mFECMode == 0 :
				self.getControl( E_SpinEx03 + 3 ).getListItem( 0 ).setLabel2( 'Automatic' )
				self.getControl( E_SpinEx03 + 3 ).selectItem( 0 )
				self.SetEnableControl( E_SpinEx03, False )
			else :
				self.SetProp( E_SpinEx03, 0 )
				self.getControl( E_SpinEx03 + 3 ).getListItem( 0 ).setLabel2( 'QPSK 1/2' )
				self.SetEnableControl( E_SpinEx03, True )

		if self.mHasTansponder == False :
			disablecontrols = [ E_Input02, E_Input03, E_Input04, E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06 ]
			self.SetEnableControls( disablecontrols, False )
