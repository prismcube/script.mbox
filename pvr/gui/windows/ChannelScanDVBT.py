from pvr.gui.WindowImport import *
import pvr.ScanHelper as ScanHelper


E_CHANNEL_SCAN_DVBT_BASE_ID = WinMgr.WIN_ID_CHANNEL_SCAN_DVBT * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 


E_TUNER_T	= 0
E_TUNER_T2	= 1
E_TUNER_C	= 2


class ChannelScanDVBT( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mIsManualSetup = 0
		self.mDVBT = ElisIDVBTCarrier( )
		#self.mTunerType = E_TUNER_T
		#self.mPlpId = 0
		#self.mHideControl = [ E_Input01, E_Input02, E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05 ]


	def onInit( self ) :
		self.SetActivate( True )
		self.SetFrontdisplayMessage( MR_LANG('DVBT Scan') )		
		self.mWinId = xbmcgui.getCurrentWindowId( )

		self.SetSettingWindowLabel( MR_LANG( 'DVBT Scan' ) )
		self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'Installation' ), MR_LANG( 'Channel Search' ) ) )
		self.SetSingleWindowPosition( E_CHANNEL_SCAN_DVBT_BASE_ID )

		self.SetPipScreen( )

		self.InitConfig( )
		self.mInitialized = True
		self.SetDefaultControl( )


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
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
			self.SetVideoRestore( )
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
		if self.IsActivate( ) == False  :
			return
	
		groupId = self.GetGroupId( aControlId )

		# Manual Setup
		if groupId == E_SpinEx01 :
			self.mIsManualSetup = self.GetSelectedIndex( E_SpinEx01 )
			self.DisableControl( E_SpinEx01 )
			return

		# Frequency		
		if groupId == E_Input01 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( MR_LANG( 'Enter Frequency' ), '%d' % self.mDVBT.mFrequency, 10 )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				#tempval = dialog.GetString( )
				#if int( tempval ) > 13000 :
				#	self.mConfigTransponder.mFrequency = 13000
				#elif int( tempval ) < 3000 :
				#	self.mConfigTransponder.mFrequency = 3000
				#else :
				#	self.mConfigTransponder.mFrequency = int( tempval )
				self.mDVBT.mFrequency = int( dialog.GetString( ) )
				self.SetControlLabel2String( E_Input01, '%d MHz' % self.mDVBT.mFrequency )
			else :
				return

		# plp id		
		if groupId == E_Input02 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( MR_LANG( 'Enter PLP ID' ), '%d' % self.mDVBT.mPLPId, 3 )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				#tempval = dialog.GetString( )
				#if int( tempval ) > 13000 :
				#	self.mConfigTransponder.mFrequency = 13000
				#elif int( tempval ) < 3000 :
				#	self.mConfigTransponder.mFrequency = 3000
				#else :
				#	self.mConfigTransponder.mFrequency = int( tempval )
				self.mDVBT.mPLPId = int( dialog.GetString( ) )
				self.SetControlLabel2String( E_Input02, '%03d' % self.mDVBT.mPLPId )
			else :
				return

		# Bandwidth
		elif groupId == E_SpinEx02 :
			self.mDVBT.mBand = self.GetSelectedIndex( E_SpinEx02 )

		# Tuner type
		elif groupId == E_SpinEx03 :
			self.mDVBT.mIsDVBT2 = self.GetSelectedIndex( E_SpinEx03 )
			self.DisableControl( E_SpinEx03 )

		elif groupId == E_SpinEx04 or groupId == E_SpinEx05 :
			self.ControlSelect( )
			return

		# Start Search
		elif groupId == E_Input03 :
			if self.mDVBT.mIsDVBT2 == E_TUNER_C :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No support' ) )
				dialog.doModal( )
				return
			else :
				self.OpenBusyDialog( )
				ScanHelper.GetInstance( ).ScanHelper_Stop( self, False )
				
				carrierList = []
				carrierList.append( self.GetElisICarrier( ) )

				self.CloseBusyDialog( )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
				dialog.SetCarrier( carrierList )
				dialog.doModal( )
				self.setProperty( 'ViewProgress', 'True' )

		ScanHelper.GetInstance( ).ScanHelper_ChangeContextByCarrier( self, self.GetElisICarrier( ) )


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return

		if self.mInitialized :
			self.ShowDescription( aControlId )


	def onEvent( self, aEvent ) :
		if xbmcgui.getCurrentWindowId( ) == self.mWinId :
			if aEvent.getName( ) == ElisEventTuningStatus.getName( ) :
				self.UpdateStatus( aEvent )


	def UpdateStatus( self, aEvent ) :
		print 'dhkim test aEvent.mFrequency = %s' % aEvent.mFrequency
		if aEvent.mFrequency == self.mDVBT.mFrequency :
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

		self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Search Mode' ), [ MR_LANG( 'Automatic Scan' ), MR_LANG( 'Manual Scan' ) ], self.mIsManualSetup, MR_LANG( 'Select channel search mode' ) )
		self.AddInputControl( E_Input01, MR_LANG( 'Frequency' ), '%d MHz' % self.mDVBT.mFrequency, MR_LANG( 'Input frequency' ), aInputNumberType = TYPE_NUMBER_NORMAL, aMax = 9999999999 )
		self.AddUserEnumControl( E_SpinEx02, 'Bandwidth', [ '6MHz','7MHz','8MHz' ], self.mDVBT.mBand, MR_LANG( 'Select bandwidth' ) )
		self.AddUserEnumControl( E_SpinEx03, 'Tuner Type', [ MR_LANG( 'DVB-T' ), MR_LANG( 'DVB-T2' ), MR_LANG( 'DVB-C' ) ], self.mDVBT.mIsDVBT2, MR_LANG( 'Select tuner type' ) )
		self.AddInputControl( E_Input02, MR_LANG( 'PLP ID' ), '%03d' % self.mDVBT.mPLPId, MR_LANG( 'Input PLP ID' ), aInputNumberType = TYPE_NUMBER_NORMAL, aMax = 255 )
		networkSearchDescription = '%s %s' % ( MR_LANG( 'When set to \'Off\', only the factory default transponders of the satellites you previously selected will be scanned for new channels.'), MR_LANG('If you set to \'On\', both the existing transponders and additional transponders that have not yet been stored to be located are scanned for new channels' ) )
		self.AddEnumControl( E_SpinEx04, 'Network Search', None, networkSearchDescription )
		self.AddEnumControl( E_SpinEx05, 'Channel Search Mode', MR_LANG( 'Search Type' ), MR_LANG( 'Select whether you wish to scan free and scrambled, free only or scrambled only' ) )
		self.AddInputControl( E_Input03, MR_LANG( 'Start Search' ), '', MR_LANG( 'Press OK button to start a channel search' ) )

		self.InitControl( )
		self.DisableControl( )
		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( True )


	def DisableControl( self, aGroupId = None ) :
		if aGroupId == None or aGroupId == E_SpinEx01 :
			if self.mDVBT.mIsDVBT2 == E_TUNER_T2 :
				self.SetEnableControl( E_Input02, True )
			else :
				self.SetEnableControl( E_Input02, False )

		elif aGroupId == None or aGroupId == E_SpinEx01 :
			disablecontrols = [ E_Input01, E_Input02, E_SpinEx02, E_SpinEx03 ]
			if self.mIsManualSetup == 0 :
				self.SetEnableControls( disablecontrols, False )
				ScanHelper.GetInstance( ).ScanHelper_Stop( self )
			else :
				ScanHelper.GetInstance( ).ScanHelper_Start( self )
				ScanHelper.GetInstance( ).ScanHelper_ChangeContextByCarrier( self, self.GetElisICarrier( ) )
				self.SetEnableControls( disablecontrols, True )


	def CallballInputNumber( self, aGroupId, aString ) :
		if aGroupId == E_Input01 :
			self.mDVBT.mFrequency = int( aString )
			self.SetControlLabel2String( aGroupId, aString + ' MHz' )
			#if self.mDVBT.mFrequency >= 9999999999 :
			#	ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex ], self.mConfigTransponder )
		elif aGroupId == E_Input02 :
			self.mDVBT.mPLPId = int( aString )
			self.SetControlLabel2String( aGroupId, '%03d' % int( aString ) )


	def FocusChangedAction( self, aGroupId ) :
		pass
		#if aGroupId == E_Input01 and self.mDVBT.mFrequency < 9999999999 :
		#	self.mDVBT.mFrequency = 3000
		#	self.SetControlLabel2String( E_Input02, '%s MHz' % self.mConfigTransponder.mFrequency )
		#	ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex ], self.mConfigTransponder )
			
		#if aGroupId == E_Input02 and self.mPlpId < 255 :
		#	self.mConfigTransponder.mSymbolRate = 1000
		#	self.SetControlLabel2String( E_Input03, '%s KS/s' % self.mConfigTransponder.mSymbolRate )
		#	ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex ], self.mConfigTransponder )


	def GetElisICarrier( self ) :
		ICarrier = ElisICarrier( )
		if self.mDVBT.mIsDVBT2 == E_TUNER_T or self.mDVBT.mIsDVBT2 == E_TUNER_T2 :
			ICarrier.mCarrierType = ElisEnum.E_CARRIER_TYPE_DVBT
		else :
			ICarrier.mCarrierType = ElisEnum.E_CARRIER_TYPE_DVBC
		self.mDVBT.mBand = self.mDVBT.mBand + 6
		ICarrier.mDVBT = self.mDVBT
		return ICarrier