from pvr.gui.WindowImport import *
import pvr.ScanHelper as ScanHelper


E_CHANNEL_SCAN_DVBT_BASE_ID = WinMgr.WIN_ID_CHANNEL_SCAN_DVBT * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 


E_TUNER_T	= 0
E_TUNER_T2	= 1
E_TUNER_C	= 2

FILE_TERRESTRIA = xbmcaddon.Addon( 'script.mbox' ).getAddonInfo( 'path' ) + '/terrestria.xml'


class ChannelScanDVBT( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mIsManualSetup = 0
		self.mDVBT_Manual = ElisIDVBTCarrier( )
		self.mDVBT_Auto = []
		self.mTerrestria = 'None'
		self.SetTerrestriaInfo( 0 )


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

		# Terrestria list
		elif groupId == E_Input04 :
			terrestriaList = self.GetTerrestriaList( )
			if terrestriaList :
				dialog = xbmcgui.Dialog( )
				ret = dialog.select( MR_LANG( 'Select Terrestria' ), terrestriaList, False, StringToListIndex( terrestriaList, self.mTerrestria ) )
				if ret >= 0 :
					if self.SetTerrestriaInfo( ret ) :
						self.SetControlLabel2String( E_Input04, self.mTerrestria )
						#self.InitConfig( )
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'list not found' ) )
				dialog.doModal( )
			return

		# Frequency		
		elif groupId == E_Input01 :
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
		elif groupId == E_Input02 :
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
		elif groupId == E_SpinEx02 :
			self.mDVBT_Manual.mBand = self.GetSelectedIndex( E_SpinEx02 )

		# Tuner type
		elif groupId == E_SpinEx03 :
			self.mDVBT_Manual.mIsDVBT2 = self.GetSelectedIndex( E_SpinEx03 )
			self.DisableControl( E_SpinEx03 )

		elif groupId == E_SpinEx04 or groupId == E_SpinEx05 :
			self.ControlSelect( )
			return

		# Start Search
		elif groupId == E_Input03 :
			if self.mDVBT_Manual.mIsDVBT2 == E_TUNER_C :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No support' ) )
				dialog.doModal( )
				return

			else :
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
					if self.mTerrestria == 'None' or len( self.mDVBT_Auto ) == 0 :
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Select terrestria first' ) )
						dialog.doModal( )
						self.CloseBusyDialog( )
						return
					
					self.CloseBusyDialog( )
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
					dialog.SetCarrier( self.mDVBT_Auto )
					dialog.doModal( )
					return

		ScanHelper.GetInstance( ).ScanHelper_ChangeContextByCarrier( self, self.GetElisICarrier( ) )


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return

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

		self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Search Mode' ), [ MR_LANG( 'Automatic Scan' ), MR_LANG( 'Manual Scan' ) ], self.mIsManualSetup, MR_LANG( 'Select channel search mode' ) )
		self.AddInputControl( E_Input04, MR_LANG( 'Terrestrial frequency list' ), self.mTerrestria, MR_LANG( 'Select Terrerstria' ) )		
		self.AddInputControl( E_Input01, MR_LANG( 'Frequency' ), '%d KHz' % self.mDVBT_Manual.mFrequency, MR_LANG( 'Input frequency' ), aInputNumberType = TYPE_NUMBER_NORMAL, aMax = 9999999 )
		self.AddUserEnumControl( E_SpinEx02, 'Bandwidth', [ '6MHz','7MHz','8MHz' ], self.mDVBT_Manual.mBand, MR_LANG( 'Select bandwidth' ) )
		self.AddUserEnumControl( E_SpinEx03, 'Tuner Type', [ MR_LANG( 'DVB-T' ), MR_LANG( 'DVB-T2' ), MR_LANG( 'DVB-C' ) ], self.mDVBT_Manual.mIsDVBT2, MR_LANG( 'Select tuner type' ) )
		self.AddInputControl( E_Input02, MR_LANG( 'PLP ID' ), '%03d' % self.mDVBT_Manual.mPLPId, MR_LANG( 'Input PLP ID' ), aInputNumberType = TYPE_NUMBER_NORMAL, aMax = 999 )
		networkSearchDescription = '%s %s' % ( MR_LANG( 'When set to \'Off\', only the factory default transponders of the satellites you previously selected will be scanned for new channels.'), MR_LANG('If you set to \'On\', both the existing transponders and additional transponders that have not yet been stored to be located are scanned for new channels' ) )
		self.AddEnumControl( E_SpinEx04, 'Network Search', None, networkSearchDescription )
		self.AddEnumControl( E_SpinEx05, 'Channel Search Mode', MR_LANG( 'Search Type' ), MR_LANG( 'Select whether you wish to scan free and scrambled, free only or scrambled only' ) )
		self.AddInputControl( E_Input03, MR_LANG( 'Start Search' ), '', MR_LANG( 'Press OK button to start a channel search' ) )

		self.InitControl( )
		self.DisableControl( )
		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( True )


	def DisableControl( self, aGroupId = None ) :
		if aGroupId == None or aGroupId == E_SpinEx03 :
			if self.mDVBT_Manual.mIsDVBT2 == E_TUNER_T2 :
				self.SetEnableControl( E_Input02, True )
			else :
				self.SetEnableControl( E_Input02, False )

		if aGroupId == None or aGroupId == E_SpinEx01 :
			disablecontrols = [ E_Input01, E_Input02, E_SpinEx02, E_SpinEx03 ]
			if self.mIsManualSetup == 0 :
				self.SetEnableControls( disablecontrols, False )
				self.SetEnableControl( E_Input04, True )
				ScanHelper.GetInstance( ).ScanHelper_Stop( self )
			else :
				ScanHelper.GetInstance( ).ScanHelper_Start( self )
				ScanHelper.GetInstance( ).ScanHelper_ChangeContextByCarrier( self, self.GetElisICarrier( ) )
				self.SetEnableControls( disablecontrols, True )
				self.SetEnableControl( E_Input04, False )


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
		if self.mDVBT_Manual.mIsDVBT2 == E_TUNER_T or self.mDVBT_Manual.mIsDVBT2 == E_TUNER_T2 :
			ICarrier.mCarrierType = ElisEnum.E_CARRIER_TYPE_DVBT
		else :
			ICarrier.mCarrierType = ElisEnum.E_CARRIER_TYPE_DVBC
		temp = deepcopy( self.mDVBT_Manual )
		temp.mBand = temp.mBand + 6
		ICarrier.mDVBT = temp
		temp.printdebug( )
		return ICarrier


	def SetTerrestriaInfo( self, aIndex ) :
		if not os.path.exists( FILE_TERRESTRIA ) :
			return False

		try :
			self.mDVBT_Auto = []
			tree = ElementTree.parse( FILE_TERRESTRIA )
			root = tree.getroot( )

			terrestria = root.getchildren( )[ aIndex ]
			self.mTerrestria = terrestria.get( 'name' ).encode( 'utf-8' )

			for terrestria in terrestria.findall( 'transponder' ) :
				ICarrier = ElisICarrier( )
				ICarrier.mCarrierType = ElisEnum.E_CARRIER_TYPE_DVBT
				IDVBTCarrier = ElisIDVBTCarrier( )
				IDVBTCarrier.mFrequency = int( float( terrestria.get( 'centre_frequency' ) ) / float( 1000 ) )
				IDVBTCarrier.mBand = 8 - int( terrestria.get( 'bandwidth' ) )
				try :
					IDVBTCarrier.mIsDVBT2 = int( terrestria.get( 'type' ) )
				except :
					IDVBTCarrier.mIsDVBT2 = 0
				if IDVBTCarrier.mIsDVBT2 == E_TUNER_T2 :
					IDVBTCarrier.mPLPId = int( terrestria.get( 'plp_id' ) )
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
		if not os.path.exists( FILE_TERRESTRIA ) :
			return None

		try :
			tree = ElementTree.parse( FILE_TERRESTRIA )
			root = tree.getroot( )
			nameList = []

			for terrestria in root.findall( 'terrestrial' ) :
				if terrestria.get( 'name' ) != None :
					nameList.append( terrestria.get( 'name' ).encode( 'utf-8' ) )

			if len( nameList ) > 0 :
				return nameList
			else :
				return None

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return None
