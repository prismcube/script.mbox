import xbmc
import xbmcgui
import sys

import pvr.gui.DialogMgr as DiaMgr
import pvr.TunerConfigMgr as ConfigMgr
from pvr.gui.GuiConfig import *
from pvr.gui.BaseWindow import SettingWindow, Action
from ElisProperty import ElisPropertyEnum
from ElisEnum import ElisEnum


class SatelliteConfigMotorized12( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mCurrentSatellite = None
		self.mTransponderList = None
		self.mSelectedIndexLnbType = None
		self.mSelectedTransponderIndex = 0
		self.tunerIndex = 0
		self.mHasTransponder = False
		
			
	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		
		self.tunerIndex = ConfigMgr.GetInstance( ).GetCurrentTunerIndex( )
		self.mCurrentSatellite = ConfigMgr.GetInstance( ).GetCurrentConfiguredSatellite( )
		self.mTransponderList = self.mDataCache.Satellite_GetFormattedTransponderList( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType )
		self.mSelectedTransponderIndex = 0

		self.SetSettingWindowLabel( 'Satellite Configuration' )
		
		if self.tunerIndex == E_TUNER_1 :
			property = ElisPropertyEnum( 'Tuner1 Type', self.mCommander )
		elif self.tunerIndex == E_TUNER_2 : 
			property = ElisPropertyEnum( 'Tuner2 Type', self.mCommander )
		else :
			property = ElisPropertyEnum( 'Tuner1 Type', self.mCommander )
 
		
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Satellite Config : Tuner %d - %s' % ( self.tunerIndex + 1, property.GetPropString( ) ) )
		self.mSelectedIndexLnbType = self.mCurrentSatellite.mLnbType
		self.InitConfig( )

		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )		
		
		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			self.close( )

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
			satelliteList = self.mDataCache.Satellite_GetFormattedNameList( )
			dialog = xbmcgui.Dialog()
 			ret = dialog.select('Select satellite', satelliteList )

			if ret >= 0 :
	 			satellite = self.mDataCache.Satellite_GetSatelliteByIndex( ret )

				self.mCurrentSatellite.reset( )
				self.mCurrentSatellite.mSatelliteLongitude 	= satellite.mLongitude		# Longitude
				self.mCurrentSatellite.mBandType 			= satellite.mBand			# Band
				self.mCurrentSatellite.mIsConfigUsed 		= 1							# IsUsed
				self.mCurrentSatellite.mLowLNB 				= 9750						# Low
				self.mCurrentSatellite.mHighLNB 			= 10600						# High
				self.mCurrentSatellite.mLNBThreshold		= 11700						# Threshold

				self.mTransponderList = self.mDataCache.Satellite_GetFormattedTransponderList( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType )				
		
				self.InitConfig()

		# LNB Setting
		elif groupId == E_SpinEx01 :
			self.mSelectedIndexLnbType = self.GetSelectedIndex( E_SpinEx01 )
			self.mCurrentSatellite.mLnbType = self.mSelectedIndexLnbType
			self.mCurrentSatellite.mFrequencyLevel = 0
			
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

		# 22Khz
 		elif groupId == E_SpinEx03 :
			self.mCurrentSatellite.mFrequencyLevel = self.GetSelectedIndex( E_SpinEx03 )

		# Transponer
 		elif groupId == E_Input03 :
	 		if self.mTransponderList :
	 			dialog = xbmcgui.Dialog()
	 			self.mSelectedTransponderIndex = dialog.select( 'Select Transponder', self.mTransponderList )
	 			if self.mSelectedTransponderIndex != -1 :
	 				self.InitConfig( )

		# Move Antenna
		elif groupId == E_Input04 :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_MOVE_ANTENNA )
 			dialog.doModal( )

			
		# Action
		elif groupId == E_SpinEx04 :
			pass

		# Antenna Action
		elif groupId == E_Input05 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( 'Configure', 'Are Yor Sure?' )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				selected = self.GetSelectedIndex( E_SpinEx04 )
				if selected == 0 :
					self.mCommander.Motorized_ResetLimit( self.tunerIndex )
				elif selected == 1 :
					self.mCommander.Motorized_SetEastLimit( self.tunerIndex )
				elif selected == 2 :			
					self.mCommander.Motorized_SetWestLimit( self.tunerIndex )

		# Store Position and Exit
		elif groupId == E_Input06 :
			pos = self.mCommander.Satelliteconfig_GetFirstAvailablePos( self.tunerIndex, ConfigMgr.GetInstance( ).GetCurrentConfigIndex( ) )
			ret = self.mCommander.Motorized_SavePosition( self.tunerIndex, pos )
			if ret == True :
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'Confirm', 'Save Position OK' )
	 			dialog.doModal( )
			else :
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'ERROR', 'Save Position Fail' )
	 			dialog.doModal( )


	def onFocus( self, aControlId ) :
		pass


	def InitConfig( self ) :
		self.ResetAllControl( )

		self.AddInputControl( E_Input01, 'Satellite' , self.mDataCache.Satellite_GetFormattedName( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType ) )
		self.AddUserEnumControl( E_SpinEx01, 'LNB Type', E_LIST_LNB_TYPE, self.mSelectedIndexLnbType )

		if self.mSelectedIndexLnbType == ElisEnum.E_LNB_SINGLE :
			self.AddUserEnumControl( E_SpinEx02, 'LNB Frequency', E_LIST_SINGLE_FREQUENCY, getSingleFrequenceIndex( self.mCurrentSatellite.mLowLNB ) )
		else :
			lnbFrequency = '%d / %d / %d' % ( self.mCurrentSatellite.mLowLNB, self.mCurrentSatellite.mHighLNB, self.mCurrentSatellite.mLNBThreshold )
			self.AddInputControl( E_Input02, 'LNB Frequency', lnbFrequency )

		self.AddUserEnumControl( E_SpinEx03, '22KHz Control', USER_ENUM_LIST_ON_OFF, self.mCurrentSatellite.mFrequencyLevel )	

		if self.mTransponderList :
			self.AddInputControl( E_Input03, 'Transponder', self.mTransponderList[ self.mSelectedTransponderIndex ] )
			self.mHasTransponder = True			
		else :
			self.AddInputControl( E_Input03, 'Transponder', 'None' )			
			self.mHasTransponder = False

		self.AddInputControl( E_Input04, 'Move Antenna', '' )
		self.AddUserEnumControl( E_SpinEx04, 'Action', E_LIST_MOTORIZE_ACTION, 0 )
		self.AddInputControl( E_Input05, ' - Action Start', '' )
		self.AddInputControl( E_Input06, 'Store Position and Exit', '' )

		if( self.mSelectedIndexLnbType == ElisEnum.E_LNB_SINGLE ) :
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
			self.getControl( E_SpinEx03 + 3 ).selectItem( 1 )	# Always On
			
		else :
			self.SetEnableControls( enableControlIds, True )

		if self.mHasTransponder == False :
			self.SetEnableControl( E_Input03, False )
		else:
			self.SetEnableControl( E_Input03, True )