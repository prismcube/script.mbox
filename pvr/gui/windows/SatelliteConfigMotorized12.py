from pvr.gui.WindowImport import *
from pvr.gui.FTIWindow import FTIWindow
import pvr.ScanHelper as ScanHelper


class SatelliteConfigMotorized12( FTIWindow ) :
	def __init__( self, *args, **kwargs ) :
		FTIWindow.__init__( self, *args, **kwargs )
		self.mCurrentSatellite 			= None
		self.mTransponderList 			= None
		self.mSelectedIndexLnbType 		= None
		self.mSelectedTransponderIndex	= 0
		self.tunerIndex					= E_TUNER_1
		self.mHasTransponder			= False
		self.mAvBlankStatus				= False
		self.mNetworkSearch				= 1
		self.mSearchMode				= 0


	def onInit( self ) :
		self.SetActivate( True )
		self.mAvBlankStatus = self.mDataCache.Get_Player_AVBlank( )
		self.mDataCache.Player_AVBlank( True )
		
		self.mWinId = xbmcgui.getCurrentWindowId( )

		self.mEventBus.Register( self )
		ScanHelper.GetInstance( ).ScanHelper_Start( self )

		self.mNetworkSearch = ElisPropertyEnum( 'Network Search', self.mCommander ).GetProp( )
		self.mSearchMode = ElisPropertyEnum( 'Channel Search Mode', self.mCommander ).GetProp( )
		ElisPropertyEnum( 'Network Search', self.mCommander ).SetProp( 1 )
		ElisPropertyEnum( 'Channel Search Mode', self.mCommander ).SetProp( 0 )

		self.mCurrentSatellite = self.mTunerMgr.GetCurrentConfiguredSatellite( )
		self.mTransponderList = self.mDataCache.GetFormattedTransponderList( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType )
		self.mSelectedTransponderIndex = 0

		self.SetSettingWindowLabel( MR_LANG( 'Satellite Configuration' ) )
		self.VisibleTuneStatus( False )

		self.mSelectedIndexLnbType = self.mCurrentSatellite.mLnbType
		self.InitConfig( )
		ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mCurrentSatellite, self.mDataCache.GetTransponderListByIndex( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType, self.mSelectedTransponderIndex ) )
		self.setDefaultControl( )
		self.SetPipLabel( )
		self.SetFTIGuiType( )
		self.mInitialized = True


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			if self.GetFirstInstallation( ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( MR_LANG( 'Exit installation' ), MR_LANG( 'Are you sure you want to quit the first installation?' ) )
				dialog.doModal( )

				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					self.OpenBusyDialog( )
					ElisPropertyEnum( 'Network Search', self.mCommander ).SetProp( self.mNetworkSearch )
					ElisPropertyEnum( 'Channel Search Mode', self.mCommander ).SetProp( self.mSearchMode )
					self.mEventBus.Deregister( self )
					ScanHelper.GetInstance( ).ScanHelper_Stop( self )
					self.RestoreAvBlank( )
					self.CloseFTI( )
					self.CloseBusyDialog( )
					WinMgr.GetInstance( ).CloseWindow( )
			else :
				self.OpenBusyDialog( )
				ElisPropertyEnum( 'Network Search', self.mCommander ).SetProp( self.mNetworkSearch )
				ElisPropertyEnum( 'Channel Search Mode', self.mCommander ).SetProp( self.mSearchMode )
				self.mEventBus.Deregister( self )
				ScanHelper.GetInstance( ).ScanHelper_Stop( self )
				self.RestoreAvBlank( )
				self.CloseBusyDialog( )
				WinMgr.GetInstance( ).CloseWindow( )

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
		if self.IsActivate( ) == False  :
			return
	
		groupId = self.GetGroupId( aControlId )

		#Satellite
		if groupId == E_Input01 :
			satelliteList = self.mDataCache.GetFormattedSatelliteNameList( )
			dialog = xbmcgui.Dialog( )
 			ret = dialog.select( MR_LANG( 'Select Satellite' ), satelliteList, False, StringToListIndex( satelliteList, self.GetControlLabel2String( E_Input01 ) ) )

			if ret >= 0 :
				satellite = self.mDataCache.GetSatelliteByIndex( ret )

				self.mCurrentSatellite.mSatelliteLongitude 	= satellite.mLongitude		# Longitude
				self.mCurrentSatellite.mBandType 			= satellite.mBand			# Band
				self.mCurrentSatellite.mIsConfigUsed 		= 1							# IsUsed
				self.mCurrentSatellite.mLowLNB 				= 9750						# Low
				self.mCurrentSatellite.mHighLNB 			= 10600						# High
				self.mCurrentSatellite.mLNBThreshold		= 11700						# Threshold
				self.mSelectedIndexLnbType					= ElisEnum.E_LNB_UNIVERSAL				

				self.mTransponderList = self.mDataCache.GetFormattedTransponderList( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType )				
				self.mSelectedTransponderIndex = 0
				self.InitConfig()
			else :
				return

		# LNB Setting
		elif groupId == E_SpinEx01 :
			self.mSelectedIndexLnbType = self.GetSelectedIndex( E_SpinEx01 )
			self.mCurrentSatellite.mLnbType = self.mSelectedIndexLnbType
			
			if self.mSelectedIndexLnbType == ElisEnum.E_LNB_SINGLE :
				self.mCurrentSatellite.mLowLNB = 5150

			else :
				self.mCurrentSatellite.mLowLNB = 9750	
				self.mCurrentSatellite.mHighLNB = 10600	
				self.mCurrentSatellite.mLNBThreshold = 11700

			self.InitConfig( )

		# LNB Frequency - Spincontrol
		elif groupId == E_SpinEx02 :
			position = self.GetSelectedIndex( E_SpinEx02 )
			self.mCurrentSatellite.mLowLNB = int( E_LIST_SINGLE_FREQUENCY[ position ] )

		# LNB Frequency - Inputcontrol
		elif groupId == E_Input02 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_LNB_FREQUENCY )
			dialog.SetFrequency( self.mCurrentSatellite.mLowLNB, self.mCurrentSatellite.mHighLNB, self.mCurrentSatellite.mLNBThreshold )
			dialog.doModal( )

			if dialog.IsOK() == E_DIALOG_STATE_YES :
				lowFreq, highFreq, threshFreq  = dialog.GetFrequency( )

				self.mCurrentSatellite.mLowLNB = int ( lowFreq )
				self.mCurrentSatellite.mHighLNB = int ( highFreq )
				self.mCurrentSatellite.mLNBThreshold = int ( threshFreq )

				self.InitConfig( )
			else :
				return

		# 22Khz
		elif groupId == E_SpinEx03 :
			self.mCurrentSatellite.mFrequencyLevel = self.GetSelectedIndex( E_SpinEx03 )

		# Transponer
 		elif groupId == E_Input03 :
 			if self.mTransponderList :
	 			dialog = xbmcgui.Dialog( )
	 			tempIndex = dialog.select( MR_LANG( 'Select Transponder' ), self.mTransponderList, False, StringToListIndex( self.mTransponderList, self.GetControlLabel2String( E_Input03 ) ) )
	 			if tempIndex != -1 :
	 				self.mSelectedTransponderIndex = tempIndex
	 				self.InitConfig( )
	 			else :
	 				return

		# Rotate Satellite Dish
		elif groupId == E_Input04 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_MOVE_ANTENNA )
			dialog.doModal( )
			return

		# Action
		elif groupId == E_SpinEx04 :
			return

		# Antenna Action
		elif groupId == E_Input05 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Rotation limits' ), MR_LANG( 'Do you want to apply the rotation limits above?' ) )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				selected = self.GetSelectedIndex( E_SpinEx04 )
				if selected == 0 :
					self.mCommander.Motorized_ResetLimit( self.tunerIndex )
				elif selected == 1 :
					self.mCommander.Motorized_SetEastLimit( self.tunerIndex )
				elif selected == 2 :			
					self.mCommander.Motorized_SetWestLimit( self.tunerIndex )
			return

		# Store Position
		elif groupId == E_Input06 :
			self.OpenBusyDialog( )
			self.mCommander.Motorized_SavePosition( self.tunerIndex, self.mTunerMgr.GetCurrentConfigIndex( ) + 1 )
			time.sleep( 0.5 )
			self.CloseBusyDialog( )
			return

		elif groupId == E_Input07 :
	 		if self.mTransponderList :
	 			self.OpenBusyDialog( )
				ScanHelper.GetInstance( ).ScanHelper_Stop( self, False )
				
				transponderList = []
				transponderList.append( self.mDataCache.GetTransponderListByIndex( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType, self.mSelectedTransponderIndex ) )

				self.CloseBusyDialog( )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
				dialog.SetTransponder( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType, transponderList )
				dialog.doModal( )
				self.setProperty( 'ViewProgress', 'True' )
	 		else :
	 			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No transponder info available' ), MR_LANG( 'Add a new transponder first' ) )
				dialog.doModal( )

		if aControlId == E_FIRST_TIME_INSTALLATION_PREV :
			self.OpenBusyDialog( )
			self.mEventBus.Deregister( self )
			ScanHelper.GetInstance( ).ScanHelper_Stop( self )
			self.RestoreAvBlank( )
			WinMgr.GetInstance( ).ShowWindow( self.GetAntennaPrevStepWindowId( ), WinMgr.WIN_ID_MAINMENU )
			return

		elif aControlId == E_FIRST_TIME_INSTALLATION_NEXT :
			self.OpenBusyDialog( )
			self.mEventBus.Deregister( self )
			ScanHelper.GetInstance( ).ScanHelper_Stop( self )
			self.RestoreAvBlank( )
			WinMgr.GetInstance( ).ShowWindow( self.GetAntennaNextStepWindowId( ), WinMgr.WIN_ID_MAINMENU )
			return

		ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self, self.mCurrentSatellite, self.mDataCache.GetTransponderListByIndex( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType, self.mSelectedTransponderIndex ) )


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
		if self.mInitialized == False :
			return
		if self.mLastFocused != aControlId :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId



	def onEvent( self, aEvent ) :
		if xbmcgui.getCurrentWindowId( ) == self.mWinId :
			if aEvent.getName( ) == ElisEventTuningStatus.getName( ) :
				self.UpdateStatus( aEvent )


	def UpdateStatus( self, aEvent ) :
		freq = self.mDataCache.GetTransponderListByIndex( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType, self.mSelectedTransponderIndex ).mFrequency
		if aEvent.mFrequency == freq :			
			ScanHelper.GetInstance( ).ScanHerper_Progress( self, aEvent.mSignalStrength, aEvent.mSignalQuality, aEvent.mIsLocked )
			if aEvent.mIsLocked :
				if self.mDataCache.Get_Player_AVBlank( ) :
					self.mDataCache.Player_AVBlank( False )
			else :
				if not self.mDataCache.Get_Player_AVBlank( ) :
					self.mDataCache.Player_AVBlank( True )


	def InitConfig( self ) :
		self.ResetAllControl( )

		self.AddInputControl( E_Input01, MR_LANG( 'Satellite' ), self.mDataCache.GetFormattedSatelliteName( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType ), MR_LANG( 'Select the desired satellite whose signal is to be received by the tuner' ) )
		self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'LNB Type' ), E_LIST_LNB_TYPE, self.mSelectedIndexLnbType, MR_LANG( 'Select the LNB type used in your digital satellite system' ) )

		if self.mSelectedIndexLnbType == ElisEnum.E_LNB_SINGLE :
			self.AddUserEnumControl( E_SpinEx02, MR_LANG( 'LNB Frequency' ), E_LIST_SINGLE_FREQUENCY, getSingleFrequenceIndex( self.mCurrentSatellite.mLowLNB ), MR_LANG( 'Select the LNB frequency to the LNB you are using' ) )
		else :
			lnbFrequency = '%d / %d / %d' % ( self.mCurrentSatellite.mLowLNB, self.mCurrentSatellite.mHighLNB, self.mCurrentSatellite.mLNBThreshold )
			self.AddInputControl( E_Input02, MR_LANG( 'LNB Frequency' ), lnbFrequency, MR_LANG( 'Select the LNB frequency to the LNB you are using' ) )

		self.AddUserEnumControl( E_SpinEx03, MR_LANG( '22KHz Tone Control' ), USER_ENUM_LIST_ON_OFF, self.mCurrentSatellite.mFrequencyLevel, MR_LANG( 'When set to \'On\', LNBs will be switched between low and high band' ) )	

		if self.mTransponderList :
			self.AddInputControl( E_Input03, MR_LANG( 'Transponder' ), self.mTransponderList[ self.mSelectedTransponderIndex ], MR_LANG( 'Set one of the pre-defined transponder frequency and symbol rate to get the best signal strength and quality in order to confirm that your settings are correct' ) )
			self.mHasTransponder = True			
		else :
			self.AddInputControl( E_Input03, MR_LANG( 'Transponder' ), MR_LANG( 'None' ), MR_LANG( 'Set one of the pre-defined transponder frequency and symbol rate to get the best signal strength and quality in order to confirm that your settings are correct' ) )			
			self.mHasTransponder = False

		self.AddInputControl( E_Input04, MR_LANG( 'Rotate Antenna' ), '', MR_LANG( 'You can control the movements of the motorized antenna here' ) )
		self.AddUserEnumControl( E_SpinEx04, MR_LANG( 'Rotation Limits' ), E_LIST_MOTORIZE_ACTION, 0, MR_LANG( 'Set the East and West limit of the DiSEqC motor, in order to protect from damage due to obstacles' ) )
		self.AddInputControl( E_Input05, MR_LANG( ' - Set Limits' ), '', MR_LANG( 'Press OK button to apply the rotation limits for the motor' ) )
		self.AddInputControl( E_Input06, MR_LANG( 'Store Position' ), '', MR_LANG( 'Save satellite positions' ) )
		self.AddInputControl( E_Input07, MR_LANG( 'Start Channel Search' ), '', MR_LANG( 'Press OK button to start a channel search' ) )

		if self.mSelectedIndexLnbType == ElisEnum.E_LNB_SINGLE :
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_Input01, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			hideControlIds = [ E_SpinEx05, E_SpinEx06, E_Input02 ]
		else :
			visibleControlIds = [ E_SpinEx01, E_SpinEx03, E_SpinEx04, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06, E_Input07 ]
			hideControlIds = [ E_SpinEx02, E_SpinEx06, E_SpinEx05 ]
			
		self.SetVisibleControls( visibleControlIds, True )
		self.SetEnableControls( visibleControlIds, True )

		self.SetVisibleControls( hideControlIds, False )

		if self.GetFirstInstallation( ) :
			self.SetFTIPrevNextButton( )
			self.SetVisibleControl( E_Input07, False )
			self.SetEnableControl( E_Input07, False )

		self.InitControl( )
		self.DisableControl( )
		

	def DisableControl( self ) :
		enableControlIds = [ E_Input02, E_SpinEx02, E_SpinEx03 ]
		if ( self.mSelectedIndexLnbType == ElisEnum.E_LNB_UNIVERSAL ) :
			self.SetEnableControls( enableControlIds, False )
		else :
			self.SetEnableControls( enableControlIds, True )

		if self.mHasTransponder == False :
			self.SetEnableControl( E_Input03, False )
		else:
			self.SetEnableControl( E_Input03, True )


	def RestoreAvBlank( self ) :
		if self.mAvBlankStatus :
			if not self.mDataCache.Get_Player_AVBlank( ) :
				self.mDataCache.Player_AVBlank( True )
		else :
			if self.mDataCache.Get_Player_AVBlank( ) :
				self.mDataCache.Player_AVBlank( False )