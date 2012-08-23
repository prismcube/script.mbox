from pvr.gui.WindowImport import *
import pvr.ScanHelper as ScanHelper


class SatelliteConfigMotorized12( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mCurrentSatellite = None
		self.mTransponderList = None
		self.mSelectedIndexLnbType = None
		self.mSelectedTransponderIndex = 0
		self.tunerIndex = E_TUNER_1
		self.mHasTransponder = False


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mEventBus.Register( self )
		ScanHelper.GetInstance( ).ScanHelper_Start( self.mWin )

		self.tunerIndex = self.mTunerMgr.GetCurrentTunerNumber( )
		self.mCurrentSatellite = self.mTunerMgr.GetCurrentConfiguredSatellite( )
		self.mTransponderList = self.mDataCache.GetFormattedTransponderList( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType )
		self.mSelectedTransponderIndex = 0

		self.SetSettingWindowLabel( MR_LANG( 'Satellite Configuration' ) )
		self.LoadNoSignalState( )

		self.mSelectedIndexLnbType = self.mCurrentSatellite.mLnbType
		self.InitConfig( )
		ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self.mWin, self.mCurrentSatellite, self.mDataCache.GetTransponderListByIndex( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType, self.mSelectedTransponderIndex ) )
		self.mInitialized = True
		self.setDefaultControl( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_PARENT_DIR :
			self.OpenBusyDialog( )
			self.ResetAllControl( )
			ScanHelper.GetInstance( ).ScanHelper_Stop( self.mWin )
			self.CloseBusyDialog( )
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

		#Satellite
		if groupId == E_Input01 :
			satelliteList = self.mDataCache.GetFormattedSatelliteNameList( )
			dialog = xbmcgui.Dialog()
 			ret = dialog.select( MR_LANG( 'Select Satellite' ), satelliteList )

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
	 			tempIndex = dialog.select( MR_LANG( 'Select Transponder' ), self.mTransponderList )
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
			dialog.SetDialogProperty( MR_LANG( 'Position Limit' ), MR_LANG( 'Are you sure to apply the position limit above?' ) )
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

		# Store Position and Exit
		elif groupId == E_Input06 :
			self.OpenBusyDialog( )
			self.mCommander.Motorized_SavePosition( self.tunerIndex, self.mTunerMgr.GetCurrentConfigIndex( ) + 1 )
			self.ResetAllControl( )
			ScanHelper.GetInstance( ).ScanHelper_Stop( self.mWin )
			self.CloseBusyDialog( )
			WinMgr.GetInstance( ).CloseWindow( )
			return

		ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self.mWin, self.mCurrentSatellite, self.mDataCache.GetTransponderListByIndex( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType, self.mSelectedTransponderIndex ) )


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
		freq = self.mDataCache.GetTransponderListByIndex( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType, self.mSelectedTransponderIndex ).mFrequency
		if aEvent.mFrequency == freq :			
			ScanHelper.GetInstance( ).ScanHerper_Progress( self.mWin, aEvent.mSignalStrength, aEvent.mSignalQuality, aEvent.mIsLocked )


	def InitConfig( self ) :
		self.ResetAllControl( )

		self.AddInputControl( E_Input01, MR_LANG( 'Satellite' ), self.mDataCache.GetFormattedSatelliteName( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType ), MR_LANG( 'Select the satellite that your receiver is locked into' ) )
		self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'LNB Type' ), E_LIST_LNB_TYPE, self.mSelectedIndexLnbType, MR_LANG( 'Select an appropriate LNB for the selected satellite' ) )

		if self.mSelectedIndexLnbType == ElisEnum.E_LNB_SINGLE :
			self.AddUserEnumControl( E_SpinEx02, MR_LANG( 'LNB Frequency' ), E_LIST_SINGLE_FREQUENCY, getSingleFrequenceIndex( self.mCurrentSatellite.mLowLNB ), MR_LANG( 'Select the LNB frequency to the LNB you are using' ) )
		else :
			lnbFrequency = '%d / %d / %d' % ( self.mCurrentSatellite.mLowLNB, self.mCurrentSatellite.mHighLNB, self.mCurrentSatellite.mLNBThreshold )
			self.AddInputControl( E_Input02, MR_LANG( 'LNB Frequency' ), lnbFrequency, MR_LANG( 'Select the LNB frequency to the LNB you are using' ) )

		self.AddUserEnumControl( E_SpinEx03, MR_LANG( '22KHz Control' ), USER_ENUM_LIST_ON_OFF, self.mCurrentSatellite.mFrequencyLevel, MR_LANG( 'Set On/Off switching between 2 separate LNB feeds' ) )	

		if self.mTransponderList :
			self.AddInputControl( E_Input03, MR_LANG( 'Transponder' ), self.mTransponderList[ self.mSelectedTransponderIndex ], MR_LANG( 'Select an appropriate transponder from the list' ) )
			self.mHasTransponder = True			
		else :
			self.AddInputControl( E_Input03, MR_LANG( 'Transponder' ), MR_LANG( 'None' ), MR_LANG( 'Select an appropriate transponder from the list' ) )			
			self.mHasTransponder = False

		self.AddInputControl( E_Input04, MR_LANG( 'Rotate Satellite Dish' ), '', MR_LANG( 'Rotates the antenna to east or west' ) )
		self.AddUserEnumControl( E_SpinEx04, MR_LANG( 'Position Limit' ), E_LIST_MOTORIZE_ACTION, 0, MR_LANG( 'Set the east and west limits of the motor' ) )
		self.AddInputControl( E_Input05, MR_LANG( ' - Set Position Limit' ), '', MR_LANG( 'Press the OK button to apply the position limit' ) )
		self.AddInputControl( E_Input06, MR_LANG( 'Store Position and Exit' ), '', MR_LANG( 'Save the antenna\'s position and exit' ) )

		if self.mSelectedIndexLnbType == ElisEnum.E_LNB_SINGLE :
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_Input01, E_Input03, E_Input04, E_Input05, E_Input06 ]
			hideControlIds = [ E_SpinEx05, E_SpinEx06, E_Input02 ]
		else :
			visibleControlIds = [ E_SpinEx01, E_SpinEx03, E_SpinEx04, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05, E_Input06 ]
			hideControlIds = [ E_SpinEx02, E_SpinEx06, E_SpinEx05 ]
			
		self.SetVisibleControls( visibleControlIds, True )
		self.SetEnableControls( visibleControlIds, True )

		self.SetVisibleControls( hideControlIds, False )

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
