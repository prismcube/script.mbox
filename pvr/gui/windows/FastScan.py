from pvr.gui.WindowImport import *
from elementtree import ElementTree

E_FAST_SCAN_BASE_ID = WinMgr.WIN_ID_FAST_SCAN * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID

FILE_PROVIDER	= xbmcaddon.Addon( 'script.mbox' ).getAddonInfo( 'path' ) + '/Provider.xml'


class FastScan( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mProviderStruct	= ElisFastScanProviderInfo( )
		
		self.mTunerIndex		= E_TUNER_1
		self.mUseHDList			= 0
		self.mUseNumbering		= 0
		self.mUseNaming			= 0

		self.mOPDescr			= 'None'


	def onInit( self ) :
		self.SetSingleWindowPosition( E_FAST_SCAN_BASE_ID )
		self.SetFrontdisplayMessage( MR_LANG('Fast Scan') )		

		self.SetSettingWindowLabel( MR_LANG( 'Fast Scan' ) )
		self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'Installation' ), MR_LANG( 'Channel Search' ) ) )

		self.InitConfig( )
		self.SetDefaultControl( )
		self.mInitialized = True
		self.SetDefaultControl( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		if self.GlobalAction( actionId ) :
			return
		
		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			WinMgr.GetInstance( ).CloseWindow( )

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
		
		# TunerIndex
		if groupId == E_Input01 :
			dialog = xbmcgui.Dialog( )
			ret = dialog.select( MR_LANG( 'Select Tuner' ), [ MR_LANG( 'Tuner 1' ), MR_LANG( 'Tuner 2' ) ], False, self.mTunerIndex )
			if ret >= 0 and self.mTunerIndex != ret :
				self.mTunerIndex = ret
				self.SetControlLabel2String( E_Input01, self.GetTunerNumToString( self.mTunerIndex ) )

		# Provider
		if groupId == E_Input02 :
			providerList = self.GetProviderList( )
			if providerList :
				dialog = xbmcgui.Dialog( )
				ret = dialog.select( MR_LANG( 'Select Provider' ), providerList, False, StringToListIndex( providerList, self.mOPDescr ) )
				if ret >= 0 :
					if self.SetProviderInfo( ret ) :
						self.InitConfig( )
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No provider file found' ) )
				dialog.doModal( )
			

		# Start Scan
		if groupId == E_Input03 :
			if self.mProviderStruct and self.mOPDescr != 'None' :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
				providerlist = []
				temp = deepcopy( self.mProviderStruct )
				temp.mHasHDList = self.mUseHDList
				providerlist.append( temp )
				dialog.SetProvider( self.mTunerIndex, self.mUseNumbering, self.mUseNaming, providerlist )
				dialog.doModal( )
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Please select a provider first' ) )
				dialog.doModal( )

		elif groupId == E_SpinEx01 :
			self.mUseHDList = self.GetSelectedIndex( E_SpinEx01 )

		elif groupId == E_SpinEx02 :
			self.ControlSelect( )


	def onFocus( self, aControlId ) :
		if self.mInitialized :
			self.ShowDescription( aControlId )


	def InitConfig( self ) :
		self.ResetAllControl( )
		self.AddInputControl( E_Input01, MR_LANG( 'Tuner' ), self.GetTunerNumToString( self.mTunerIndex ), MR_LANG( 'Select a tuner you want to search' ) )
		self.AddInputControl( E_Input02, MR_LANG( 'Provider' ), self.mOPDescr, MR_LANG( 'Select a provider you want to scan channels from' ) )
		self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'HD List' ), USER_ENUM_LIST_YES_NO, self.mUseHDList, MR_LANG( 'Enable/Disable HD List option' ) )
		self.AddEnumControl( E_SpinEx02, 'LCN Search', MR_LANG( 'Logical Channel Numbering' ), MR_LANG( 'Display user presentation of service numbers in a familiar form or sequentially' ) )
		self.AddInputControl( E_Input03, MR_LANG( 'Start Search' ), '', MR_LANG( 'Press OK button to start a channel search' ) )
		self.InitControl( )
		self.DisableControl( )


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


	def GetTunerNumToString( self, aTunerIndex ) :
		if aTunerIndex == E_TUNER_1 :
			return MR_LANG( 'Tuner 1' )
		else :
			return MR_LANG( 'Tuner 2' )


	def DisableControl( self ) :
		if self.mPlatform.GetTunerType( ) != TUNER_TYPE_DVBS_DUAL :
			self.SetEnableControl( E_Input01, False )
		if self.mProviderStruct.mHasHDList == 0 :
			self.SetEnableControl( E_SpinEx01, False )
		else :
			self.SetEnableControl( E_SpinEx01, True )
