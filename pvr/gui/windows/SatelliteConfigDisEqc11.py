from pvr.gui.WindowImport import *
import pvr.ScanHelper as ScanHelper


class SatelliteConfigDisEqC11( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mCurrentSatellite = None
		self.mTransponderList = None
		self.mSelectedTransponderIndex = 0
		self.mSelectedIndexLnbType = 0
		self.mHasTransponder = False
		
		
	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mEventBus.Register( self )
		ScanHelper.GetInstance( ).ScanHelper_Start( self.mWin )

		tunerIndex = self.mTunerMgr.GetCurrentTunerIndex( )
		self.mCurrentSatellite = self.mTunerMgr.GetCurrentConfiguredSatellite( )
		self.mTransponderList = self.mDataCache.GetFormattedTransponderList( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType )
		self.mSelectedTransponderIndex = 0

		self.SetSettingWindowLabel( 'Satellite Configuration' )
		
		if tunerIndex == E_TUNER_1 :
			property = ElisPropertyEnum( 'Tuner1 Type', self.mCommander )
		elif tunerIndex == E_TUNER_2 : 
			property = ElisPropertyEnum( 'Tuner2 Type', self.mCommander )
		else :
			property = ElisPropertyEnum( 'Tuner1 Type', self.mCommander )
 				
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Satellite Config : Tuner %d - %s' % ( tunerIndex + 1, property.GetPropString( ) ) )
		self.mSelectedIndexLnbType = self.mCurrentSatellite.mLnbType
		self.InitConfig( )
		ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self.mWin, self.mCurrentSatellite, self.mDataCache.GetTransponderListByIndex( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType, self.mSelectedTransponderIndex ) )
		
		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )		
		
		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
			
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
		
		#Satellite
		if groupId == E_Input01 :
			satelliteList = self.mDataCache.GetFormattedSatelliteNameList( )
			dialog = xbmcgui.Dialog()
 			ret = dialog.select('Select satellite', satelliteList )

			if ret >= 0 :
	 			satellite = self.mDataCache.GetSatelliteByIndex( ret )

				self.mCurrentSatellite.reset( )
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

 			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_LNB_FREQUENCY )
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

		# Committed Switch
		elif groupId == E_SpinEx04 :
			self.mCurrentSatellite.mDisEqcMode = self.GetSelectedIndex( E_SpinEx04 )

		# Uncommitted Switch
		elif groupId == E_SpinEx05 :
			self.mCurrentSatellite.mDisEqc11 = self.GetSelectedIndex( E_SpinEx05 )
		
		# DiSEqC Repeat
		elif groupId == E_SpinEx06 :
			self.mCurrentSatellite.mDisEqcRepeat = self.GetSelectedIndex( E_SpinEx06 )

 		# Transponer
 		elif groupId == E_Input03 :
 			if self.mTransponderList :
	 			dialog = xbmcgui.Dialog( )
	 			tempIndex = dialog.select( 'Select Transponder', self.mTransponderList )
	 			if tempIndex != -1 :
	 				self.mSelectedTransponderIndex = tempIndex
	 				self.InitConfig( )
	 			else :
	 				return

	 	ScanHelper.GetInstance( ).ScanHelper_ChangeContext( self.mWin, self.mCurrentSatellite, self.mDataCache.GetTransponderListByIndex( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType, self.mSelectedTransponderIndex ) )


	def onFocus( self, aControlId ) :
		pass


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

		self.AddInputControl( E_Input01, 'Satellite' , self.mDataCache.GetFormattedSatelliteName( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType ) )
		self.AddUserEnumControl( E_SpinEx01, 'LNB Type', E_LIST_LNB_TYPE, self.mSelectedIndexLnbType )

		if self.mSelectedIndexLnbType == ElisEnum.E_LNB_SINGLE :
			self.AddUserEnumControl( E_SpinEx02, 'LNB Frequency', E_LIST_SINGLE_FREQUENCY, getSingleFrequenceIndex( self.mCurrentSatellite.mLowLNB ) )
		else :
			lnbFrequency = '%d / %d / %d' % ( self.mCurrentSatellite.mLowLNB, self.mCurrentSatellite.mHighLNB, self.mCurrentSatellite.mLNBThreshold )
			self.AddInputControl( E_Input02, 'LNB Frequency', lnbFrequency )

		self.AddUserEnumControl( E_SpinEx03, '22KHz Control', USER_ENUM_LIST_ON_OFF, self.mCurrentSatellite.mFrequencyLevel )
		self.AddUserEnumControl( E_SpinEx04, 'Committed Switch', E_LIST_COMMITTED_SWITCH, getCommittedSwitchindex( self.mCurrentSatellite.mDisEqcMode ) )
		self.AddUserEnumControl( E_SpinEx05, 'Uncommitted Switch', E_LIST_UNCOMMITTED_SWITCH, self.mCurrentSatellite.mDisEqc11 )
		self.AddUserEnumControl( E_SpinEx06, 'DiSEqC Repeat', USER_ENUM_LIST_ON_OFF, self.mCurrentSatellite.mDisEqcRepeat )
		if self.mTransponderList :
			self.AddInputControl( E_Input03, 'Transponder', self.mTransponderList[ self.mSelectedTransponderIndex ] )
			self.mHasTransponder = True
		else :
			self.AddInputControl( E_Input03, 'Transponder', 'None' )			
			self.mHasTransponder = False
		
		if self.mSelectedIndexLnbType == ElisEnum.E_LNB_SINGLE :
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_Input01, E_Input03]
			hideControlIds = [ E_Input02, E_Input04, E_Input05, E_Input06 ]
		else :
			visibleControlIds = [ E_SpinEx01, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_Input01, E_Input02, E_Input03 ]
			hideControlIds = [ E_SpinEx02, E_Input04, E_Input05, E_Input06 ]
			
		self.SetVisibleControls( visibleControlIds, True )
		self.SetEnableControls( visibleControlIds, True )

		self.SetVisibleControls( hideControlIds, False )

		self.InitControl( )
		self.disableControl( )
		

	def disableControl( self ) :
		enableControlIds = [ E_Input02, E_SpinEx02, E_SpinEx03 ]
		if self.mSelectedIndexLnbType == ElisEnum.E_LNB_UNIVERSAL :
			self.SetEnableControls( enableControlIds, False )
		else :
			self.SetEnableControls( enableControlIds, True )	

		if self.mHasTransponder == False :
			self.SetEnableControl( E_Input03, False )
		else :
			self.SetEnableControl( E_Input03, True )
