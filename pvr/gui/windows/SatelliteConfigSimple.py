from pvr.gui.WindowImport import *
from pvr.gui.FTIWindow import FTIWindow
import pvr.ScanHelper as ScanHelper


CONTEXT_EDIT_SATELLITE_NAME	= 0
CONTEXT_EDIT_LONGITUDE		= 1
CONTEXT_ADD_TRANSPONDER		= 2
CONTEXT_EDIT_TRANSPONDER	= 3
CONTEXT_DELETE_TRANSPONDER	= 4

CONTEXT_LONGITUDE_EAST		= 0
CONTEXT_LONGITUDE_WEST		= 1


class SatelliteConfigSimple( FTIWindow ) :
	def __init__( self, *args, **kwargs ) :
		FTIWindow.__init__( self, *args, **kwargs )
		self.mCurrentSatellite			= None
		self.mTransponderList			= None
		self.mSelectedTransponderIndex	= 0
		self.mSelectedIndexLnbType		= 0
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
		#self.mSelectedTransponderIndex = 0

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

		elif actionId == Action.ACTION_CONTEXT_MENU :
			groupId = self.GetGroupId( self.GetFocusId( ) )
			self.ShowContextMenu( groupId )

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
				self.InitConfig( )
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

		# Committed Switch
		elif groupId == E_SpinEx04 :
			self.mCurrentSatellite.mDisEqcMode = self.GetSelectedIndex( E_SpinEx04 )

		# Uncommitted Switch
		elif groupId == E_SpinEx05 :
			self.mCurrentSatellite.mDisEqc11 = self.GetSelectedIndex( E_SpinEx05 )
		
		# DiSEqC Repeat
		elif groupId == E_SpinEx06 :
			self.mCurrentSatellite.mDisEqcRepeat = self.GetSelectedIndex( E_SpinEx06 )

		elif groupId == E_SpinEx04 :
			self.ControlSelect( )


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

		elif groupId == E_Input04 :
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

		if self.mCurrentSatellite.mMotorizedType == ElisEnum.E_MOTORIZED_USALS :
			self.AddUserEnumControl( E_SpinEx04, MR_LANG( 'Committed Switch' ), E_LIST_COMMITTED_SWITCH, getCommittedSwitchindex( self.mCurrentSatellite.mDisEqcMode ), MR_LANG( 'Select the committed switch number' ) )
			self.AddUserEnumControl( E_SpinEx05, MR_LANG( 'Uncommitted Switch' ), E_LIST_UNCOMMITTED_SWITCH, self.mCurrentSatellite.mDisEqc11, MR_LANG( 'Select the uncommitted switch number' ) )
			self.AddUserEnumControl( E_SpinEx06, MR_LANG( 'DiSEqC Repeat' ), USER_ENUM_LIST_ON_OFF, self.mCurrentSatellite.mDisEqcRepeat, MR_LANG( 'When set to \'On\', DiSEqC repeats its command' ) )


		if self.mTransponderList :
			self.AddInputControl( E_Input03, MR_LANG( 'Transponder' ), self.mTransponderList[ self.mSelectedTransponderIndex ], MR_LANG( 'Set one of the pre-defined transponder frequency and symbol rate to get the best signal strength and quality in order to confirm that your settings are correct' ) )	
		else :
			self.AddInputControl( E_Input03, MR_LANG( 'Transponder' ), MR_LANG( 'None' ), MR_LANG( 'Set one of the pre-defined transponder frequency and symbol rate to get the best signal strength and quality in order to confirm that your settings are correct' ) )

		self.AddEnumControl( E_SpinEx07, 'Network Search', None, MR_LANG( 'When set to \'Off\', only the factory default transponders of the satellites you previously selected will be scanned for new channels. If you set to \'On\', both the existing transponders and additional transponders that have not yet been stored to be located are scanned for new channels' ) )
		
		self.AddInputControl( E_Input04, MR_LANG( 'Start Channel Search' ), '', MR_LANG( 'Press OK button to start a channel search' ) )

		if self.mCurrentSatellite.mMotorizedType == ElisEnum.E_MOTORIZED_USALS :
			if self.mSelectedIndexLnbType == ElisEnum.E_LNB_SINGLE :
				visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_Input01, E_Input03, E_Input04 ]
				hideControlIds = [ E_Input02, E_Input05, E_Input06, E_Input07 ]
			else :
				visibleControlIds = [ E_SpinEx01, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_Input01, E_Input02, E_Input04 ]
				hideControlIds = [ E_SpinEx02,  E_Input05, E_Input06, E_Input07 ]

		else :
			if self.mSelectedIndexLnbType == ElisEnum.E_LNB_SINGLE :
				visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input01, E_Input03, E_Input04 ]
				hideControlIds = [ E_Input02, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_Input05, E_Input06, E_Input07 ]
			else :
				visibleControlIds = [ E_SpinEx01, E_SpinEx03, E_Input01, E_Input02, E_Input04 ]
				hideControlIds = [ E_SpinEx02, E_SpinEx04, E_SpinEx05,  E_SpinEx06, E_Input05, E_Input06, E_Input07 ]

		self.SetVisibleControls( visibleControlIds, True )
		self.SetEnableControls( visibleControlIds, True )

		self.SetVisibleControls( hideControlIds, False )

		if self.GetFirstInstallation( ) :
			self.SetFTIPrevNextButton( )
			self.SetVisibleControl( E_Input04, False )
			self.SetEnableControl( E_Input04, False )

		self.InitControl( )
		self.DisableControl( )
		

	def DisableControl( self ) :
		enableControlIds = [ E_Input02, E_SpinEx02, E_SpinEx03 ]
		if self.mSelectedIndexLnbType == ElisEnum.E_LNB_UNIVERSAL :
			self.SetEnableControls( enableControlIds, False )
		else :
			self.SetEnableControls( enableControlIds, True )


	def RestoreAvBlank( self ) :
		if self.mAvBlankStatus :
			if not self.mDataCache.Get_Player_AVBlank( ) :
				self.mDataCache.Player_AVBlank( True )
		else :
			if self.mDataCache.Get_Player_AVBlank( ) :
				self.mDataCache.Player_AVBlank( False )


	def ShowContextMenu( self, aGroupId ) :
		context = []
		if aGroupId == E_Input01 :
			context.append( ContextItem( MR_LANG( 'Edit Satellite Name' ), CONTEXT_EDIT_SATELLITE_NAME ) )
			context.append( ContextItem( MR_LANG( 'Edit Satellite Longitude' ), CONTEXT_EDIT_LONGITUDE ) )
		elif aGroupId == E_Input03 :
			context.append( ContextItem( MR_LANG( 'Add Transponder' ), CONTEXT_ADD_TRANSPONDER ) )
			if self.mTransponderList :
				context.append( ContextItem( MR_LANG( 'Edit Transponder' ), CONTEXT_EDIT_TRANSPONDER ) )
				context.append( ContextItem( MR_LANG( 'Delete Transponder' ), CONTEXT_DELETE_TRANSPONDER ) )
		else :
			context = None

		if context :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context )
			dialog.doModal( )

			contextAction = dialog.GetSelectedAction( )
			self.DoContextAction( contextAction )


	def DoContextAction( self, aContextAction ) :
		if aContextAction == CONTEXT_EDIT_SATELLITE_NAME :
			kb = xbmc.Keyboard( self.mDataCache.GetSatelliteName( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType ), MR_LANG( 'Enter new name for this satellite' ), False )			
			kb.setHiddenInput( False )
			kb.doModal( )

			if kb.isConfirmed( ) :
				self.mCommander.Satellite_ChangeName( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType, kb.getText( ) )
				self.mDataCache.LoadAllSatellite( )
				self.InitConfig( )

		elif aContextAction == CONTEXT_EDIT_LONGITUDE :
			context = []
			context.append( ContextItem( MR_LANG( 'Longitude Direction : East' ), CONTEXT_LONGITUDE_EAST ) )
			context.append( ContextItem( MR_LANG( 'Longitude Direction : West' ), CONTEXT_LONGITUDE_WEST ) )

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context )
			dialog.doModal( )

			contextAction = dialog.GetSelectedAction( )
			if contextAction != -1 :
				direction = contextAction
			
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SATELLITE_NUMERIC )
				dialog.SetDialogProperty( MR_LANG( 'Longitude degree' ), self.mCurrentSatellite.mSatelliteLongitude )
				dialog.doModal( )

				if dialog.IsOK() == E_DIALOG_STATE_YES :
					#self.mCurrentSatellite.mSatelliteLongitude = dialog.GetNumber( )
					tmpval = dialog.GetNumber( )
					if direction == CONTEXT_LONGITUDE_WEST :
						#self.mCurrentSatellite.mSatelliteLongitude += 1800
						tmpval += 1800
					#self.InitConfig( )
					print 'dhkim test edited longitude = %s' % tmpval

		elif aContextAction == CONTEXT_ADD_TRANSPONDER :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SET_TRANSPONDER )
			dialog.SetDefaultValue( 0, 0, 0, 0, self.mCurrentSatellite.mBandType )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.OpenBusyDialog( )
				frequency, fec, polarization, simbolrate = dialog.GetValue( )

				newTransponder = ElisITransponderInfo( )
				newTransponder.reset( )
				newTransponder.mFrequency = frequency
				newTransponder.mSymbolRate = simbolrate
				newTransponder.mPolarization = polarization
				newTransponder.mFECMode = fec

				tmplist = []
				tmplist.append( newTransponder )
				ret = self.mCommander.Transponder_Add( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType, tmplist )

				if ret != True :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Unable to add the transponder' ) )
					dialog.doModal( )
					self.CloseBusyDialog( )
					return
				
				self.mDataCache.LoadConfiguredTransponder( )
				self.mSelectedTransponderIndex = self.GetEditedPosition( frequency )
				self.mTransponderList = self.mDataCache.GetFormattedTransponderList( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType )
				self.InitConfig( )
				self.CloseBusyDialog( )

		elif aContextAction == CONTEXT_EDIT_TRANSPONDER :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SET_TRANSPONDER )
			transponder = self.mDataCache.GetTransponderListByIndex( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType, self.mSelectedTransponderIndex )
			dialog.SetDefaultValue( transponder.mFrequency, transponder.mFECMode, transponder.mPolarization, transponder.mSymbolRate, self.mCurrentSatellite.mBandType )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.OpenBusyDialog( )
				tmplist = []
				tmplist.append( transponder )
				ret = self.mCommander.Transponder_Delete( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType, tmplist )
				if ret != True :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Unable to edit the transponder' ) )
					dialog.doModal( )
					self.CloseBusyDialog( )
					return

				# ADD
				frequency, fec, polarization, simbolrate = dialog.GetValue( )

				newTransponder = ElisITransponderInfo( )
				newTransponder.reset( )
				newTransponder.mFrequency = frequency
				newTransponder.mSymbolRate = simbolrate
				newTransponder.mPolarization = polarization
				newTransponder.mFECMode = fec

				tmplist = []
				tmplist.append( newTransponder )

				ret = self.mCommander.Transponder_Add( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType, tmplist )
				if ret != True :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Unable to edit the transponder' ) )
					dialog.doModal( )
					self.CloseBusyDialog( )
					return
				
				self.mDataCache.LoadConfiguredTransponder( )
				self.mSelectedTransponderIndex = self.GetEditedPosition( frequency )
				self.mTransponderList = self.mDataCache.GetFormattedTransponderList( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType )
				self.InitConfig( )
				self.CloseBusyDialog( )

		elif aContextAction == CONTEXT_DELETE_TRANSPONDER :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Delete transponder' ), MR_LANG( 'Are you sure you want to remove\nthis transponder?' ) )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.OpenBusyDialog( )
				transponder = self.mDataCache.GetTransponderListByIndex( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType, self.mSelectedTransponderIndex )
				tmplist = []
				tmplist.append( transponder )
				ret = self.mCommander.Transponder_Delete( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType, tmplist )
				if ret != True :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Unable to delete the transponder' ) )
					dialog.doModal( )
					self.CloseBusyDialog( )
					return
				self.mDataCache.LoadConfiguredTransponder( )
				self.mSelectedTransponderIndex = 0
				self.mTransponderList = self.mDataCache.GetFormattedTransponderList( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType )
				self.InitConfig( )
				self.CloseBusyDialog( )

		else :
			LOG_ERR( 'Unknown Context Action' )


	def GetEditedPosition( self, aFrequency ) :
		transponderlist = self.mDataCache.GetTransponderListBySatellite( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType )
		for i in range( len( transponderlist ) ) :
			if transponderlist[i].mFrequency == aFrequency :
				return i

		return 0

