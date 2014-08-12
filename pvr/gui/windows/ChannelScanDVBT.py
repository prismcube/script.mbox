from pvr.gui.WindowImport import *
import pvr.ScanHelper as ScanHelper


E_CHANNEL_SCAN_DVBT_BASE_ID = WinMgr.WIN_ID_CHANNEL_SCAN_DVBT * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 


E_TUNER_T	= 0
E_TUNER_T2	= 1
E_TUNER_C	= 2

FILE_TERRESTRIAL = xbmcaddon.Addon( 'script.mbox' ).getAddonInfo( 'path' ) + '/terrestrial.xml'


class ChannelScanDVBT( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mIsManualSetup	= 0
		self.mDVBT_Manual	= ElisIDVBTCarrier( )
		self.mDVBT_Auto		= []
		self.mTerrestria	= 'None'
		self.mEnable5v		= 0
		self.mTunerType		= E_TUNER_T
		self.SetTerrestrialInfo( 0 )


	def onInit( self ) :
		self.SetFrontdisplayMessage( MR_LANG('Channel Search') )		
		self.mWinId = xbmcgui.getCurrentWindowId( )

		self.SetSettingWindowLabel( MR_LANG( 'Channel Search' ) )
		self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'Installation' ), MR_LANG( 'Channel Search' ) ) )
		self.SetSingleWindowPosition( E_CHANNEL_SCAN_DVBT_BASE_ID )

		self.SetPipScreen( )

		self.InitConfig( )
		self.mInitialized = True
		self.SetDefaultControl( )


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
		groupId = self.GetGroupId( aControlId )

		# Tuner type
		if groupId == E_SpinEx03 :
			if ( self.mTunerType == E_TUNER_T or self.mTunerType == E_TUNER_T2 ) and self.GetSelectedIndex( E_SpinEx03 ) == E_TUNER_C :
				isChanged = True
			elif ( self.GetSelectedIndex( E_SpinEx03 ) == E_TUNER_T or self.GetSelectedIndex( E_SpinEx03 ) == E_TUNER_T2 ) and self.mTunerType == E_TUNER_C :
				isChanged = True
			else :
				isChanged = False

			self.mTunerType = self.GetSelectedIndex( E_SpinEx03 )
			if isChanged :
				self.InitConfig( )
			else :
				self.DisableControl( )
			return

		if self.mTunerType == E_TUNER_T or self.mTunerType == E_TUNER_T2 :
			self.OperationDVBT( groupId )
		elif self.mTunerType == E_TUNER_C :
			self.OperationDVBC( groupId )


	def OperationDVBT( self, aGroupId ) :
		# Manual Setup
		if aGroupId == E_SpinEx01 :
			self.mIsManualSetup = self.GetSelectedIndex( E_SpinEx01 )
			self.DisableControl( E_SpinEx01 )
			return

		# Terrestrial list
		elif aGroupId == E_Input04 :
			terrestrialList = self.GetTerrestriaList( )
			if terrestrialList :
				dialog = xbmcgui.Dialog( )
				ret = dialog.select( MR_LANG( 'Select Terrestrial' ), terrestrialList, False, StringToListIndex( terrestrialList, self.mTerrestrial ) )
				if ret >= 0 :
					if self.SetTerrestrialInfo( ret ) :
						self.SetControlLabel2String( E_Input04, self.mterrestrial )
						#self.InitConfig( )
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'List not found' ) )
				dialog.doModal( )
			return

		# Frequency		
		elif aGroupId == E_Input01 :
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
		elif aGroupId == E_Input02 :
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
		elif aGroupId == E_SpinEx02 :
			self.mDVBT_Manual.mBand = self.GetSelectedIndex( E_SpinEx02 )

		elif aGroupId == E_SpinEx04 :
			self.mEnable5v = self.GetSelectedIndex( E_SpinEx04 )

		elif aGroupId == E_SpinEx05 or aGroupId == E_SpinEx06 :
			self.ControlSelect( )
			return

		# Start Search
		elif aGroupId == E_Input03 :
			self.OpenBusyDialog( )
			ScanHelper.GetInstance( ).ScanHelper_Stop( self, False )

			if self.mIsManualSetup == 1 :
				carrierList = []
				carrierList.append( self.GetElisICarrier( ) )

				self.CloseBusyDialog( )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
				dialog.SetCarrier( carrierList )
				dialog.doModal( )
				self.setProperty( 'ViewProgress', 'True' )

			elif self.mIsManualSetup == 0 :
				if self.mterrestrial == 'None' or len( self.mDVBT_Auto ) == 0 :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Select terrestrial first' ) )
					dialog.doModal( )
					self.CloseBusyDialog( )
					return

				self.CloseBusyDialog( )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
				dialog.SetCarrier( self.mDVBT_Auto )
				dialog.doModal( )
				return

		ScanHelper.GetInstance( ).ScanHelper_ChangeContextByCarrier( self, self.GetElisICarrier( ) )


	def OperationDVBC( self, aGroupId ) :
		pass


	def onFocus( self, aControlId ) :
		if self.mInitialized :
			self.ShowDescription( aControlId )


	def onEvent( self, aEvent ) :
		if xbmcgui.getCurrentWindowId( ) == self.mWinId :
			if aEvent.getName( ) == ElisEventTuningStatus.getName( ) :
				aEvent.printdebug()
				self.UpdateStatus( aEvent )


	def UpdateStatus( self, aEvent ) :
		if aEvent.mFrequency == self.mDVBT_Manual.mFrequency :
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

		if self.mTunerType == E_TUNER_T or self.mTunerType == E_TUNER_T2 :
			self.AddUserEnumControl( E_SpinEx03, 'Tuner Type', [ MR_LANG( 'DVB-T' ), MR_LANG( 'DVB-T2' ), MR_LANG( 'DVB-C' ) ], self.mTunerType, MR_LANG( 'Select tuner type' ) )
			self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Search Mode' ), [ MR_LANG( 'Automatic Scan' ), MR_LANG( 'Manual Scan' ) ], self.mIsManualSetup, MR_LANG( 'Select channel search mode' ) )
			self.AddInputControl( E_Input04, MR_LANG( 'Terrestrial frequency list' ), self.mterrestrial, MR_LANG( 'Select Terrerstrial' ) )
			self.AddInputControl( E_Input01, MR_LANG( 'Frequency' ), '%d KHz' % self.mDVBT_Manual.mFrequency, MR_LANG( 'Input frequency' ), aInputNumberType = TYPE_NUMBER_NORMAL, aMax = 9999999 )
			self.AddUserEnumControl( E_SpinEx02, 'Bandwidth', [ '6MHz','7MHz','8MHz' ], self.mDVBT_Manual.mBand, MR_LANG( 'Select bandwidth' ) )		
			self.AddInputControl( E_Input02, MR_LANG( 'PLP ID' ), '%03d' % self.mDVBT_Manual.mPLPId, MR_LANG( 'Input PLP ID' ), aInputNumberType = TYPE_NUMBER_NORMAL, aMax = 999 )
			self.AddUserEnumControl( E_SpinEx04, MR_LANG( 'Enable 5V for active antenna' ), USER_ENUM_LIST_ON_OFF, self.mEnable5v, MR_LANG( 'Select enable 5v for active antenna' ) )		
			networkSearchDescription = '%s %s' % ( MR_LANG( 'When set to \'Off\', only the factory default transponders of the satellites you previously selected will be scanned for new channels.'), MR_LANG('If you set to \'On\', both the existing transponders and additional transponders that have not yet been stored to be located are scanned for new channels' ) )
			self.AddEnumControl( E_SpinEx05, 'Network Search', None, networkSearchDescription )
			self.AddEnumControl( E_SpinEx06, 'Channel Search Mode', MR_LANG( 'Search Type' ), MR_LANG( 'Select whether you wish to scan free and scrambled, free only or scrambled only' ) )
			self.AddInputControl( E_Input03, MR_LANG( 'Start Search' ), '', MR_LANG( 'Press OK button to start a channel search' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_Input01, E_Input02, E_Input03, E_Input04 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

		elif self.mTunerType == E_TUNER_C :
			self.AddUserEnumControl( E_SpinEx03, 'Tuner Type', [ MR_LANG( 'DVB-T' ), MR_LANG( 'DVB-T2' ), MR_LANG( 'DVB-C' ) ], self.mTunerType, MR_LANG( 'Select tuner type' ) )
			self.AddInputControl( E_Input01, MR_LANG( 'Not supported' ), '', MR_LANG( 'Not supported' ) )

			visibleControlIds = [ E_SpinEx03, E_Input01 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_Input02, E_Input03, E_Input04 ]
			self.SetVisibleControls( hideControlIds, False )

		self.InitControl( )
		self.DisableControl( )
		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( True )


	def DisableControl( self, aGroupId = None ) :
		if aGroupId == None or aGroupId == E_SpinEx01 or aGroupId == E_SpinEx03 :
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


	def CallballInputNumber( self, aGroupId, aString ) :
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
		#if aGroupId == E_Input01 and self.mDVBT_Manual.mFrequency < 9999999999 :
		#	self.mDVBT_Manual.mFrequency = 3000
		#	self.SetControlLabel2String( E_Input02, '%s MHz' % self.mConfigTransponder.mFrequency )
		#	ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex ], self.mConfigTransponder )
			
		if aGroupId == E_Input02 :
			self.SetControlLabel2String( aGroupId, '%03d' % self.mDVBT_Manual.mPLPId )
		#	self.SetControlLabel2String( E_Input03, '%s KS/s' % self.mConfigTransponder.mSymbolRate )
		#	ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mConfiguredSatelliteList[ self.mSatelliteIndex ], self.mConfigTransponder )


	def GetElisICarrier( self ) :
		ICarrier = ElisICarrier( )
		if self.mTunerType == E_TUNER_T or self.mTunerType == E_TUNER_T2 :
			ICarrier.mCarrierType = ElisEnum.E_CARRIER_TYPE_DVBT
		else :
			ICarrier.mCarrierType = ElisEnum.E_CARRIER_TYPE_DVBC
		temp = deepcopy( self.mDVBT_Manual )
		temp.mBand = temp.mBand + 6
		ICarrier.mDVBT = temp
		temp.printdebug( )
		return ICarrier


	def SetTerrestrialInfo( self, aIndex ) :
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
			self.mTerrestria = 'None'
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
