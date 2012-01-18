import xbmc
import xbmcgui
import sys

import pvr.gui.DialogMgr as DiaMgr
import pvr.TunerConfigMgr as ConfigMgr
from pvr.gui.GuiConfig import *
from pvr.gui.BaseWindow import SettingWindow, Action
import pvr.ElisMgr

from ElisProperty import ElisPropertyEnum
from ElisEnum import ElisEnum


class SatelliteConfigDisEqC10( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.mCurrentSatellite = None
		self.mTransponderList = None
		self.mSelectedTransponderIndex = 0
		self.mSelectedIndexLnbType = 0

			
	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		tunerIndex = ConfigMgr.GetInstance( ).GetCurrentTunerIndex( )
		self.mCurrentSatellite = ConfigMgr.GetInstance( ).GetCurrentConfiguredSatellite( )
		self.mTransponderList = ConfigMgr.GetInstance( ).GetTransponderList( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType )
		self.mSelectedTransponderIndex = 0

		self.SetSettingWindowLabel( 'Satellite Configuration' )
		
		if tunerIndex == E_TUNER_1 :
			property = ElisPropertyEnum( 'Tuner1 Type', self.mCommander )
		elif tunerIndex == E_TUNER_2 : 
			property = ElisPropertyEnum( 'Tuner2 Type', self.mCommander )
		else :
			print 'Error : unknown Tuner'
			property = ElisPropertyEnum( 'Tuner1 Type', self.mCommander )
 				
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Satellite Config : Tuner %d - %s' % ( tunerIndex + 1, property.GetPropString( ) ) )
		self.mSelectedIndexLnbType = self.mCurrentSatellite.mLnbType
		self.InitConfig( )
		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )

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
			satelliteList = ConfigMgr.GetInstance( ).GetFormattedNameList( )
			dialog = xbmcgui.Dialog()
 			ret = dialog.select('Select satellite', satelliteList )

			if ret >= 0 :
	 			satellite = ConfigMgr.GetInstance( ).GetSatelliteByIndex( ret )

	 			for i in range( 22 ) :
					self.mCurrentSatellite.reset( )

				self.mCurrentSatellite.mSatelliteLongitude 	= satellite.mLongitude		# Longitude
				self.mCurrentSatellite.mBandType 			= satellite.mBand			# Band
				self.mCurrentSatellite.mIsConfigUsed 		= 1							# IsUsed
				self.mCurrentSatellite.mLowLNB 				= 9750						# Low
				self.mCurrentSatellite.mHighLNB 			= 10600						# High
				self.mCurrentSatellite.mLNBThreshold		= 11700						# Threshold

				self.mTransponderList = ConfigMgr.GetInstance( ).GetTransponderList( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType )				
		
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

		# DiSEqC 1.0 Switch
		elif groupId == E_SpinEx04 :
			self.mCurrentSatellite.mDisEqcMode = self.GetSelectedIndex( E_SpinEx04 )

		# DiSEqC Repeat
		elif groupId == E_SpinEx05 :
			self.mCurrentSatellite.mDisEqcRepeat = self.GetSelectedIndex( E_SpinEx05 )

		# Transponer
 		elif groupId == E_Input03 :
 			dialog = xbmcgui.Dialog()
 			self.mSelectedTransponderIndex = dialog.select( 'Select Transponder', self.mTransponderList )
 			if self.mSelectedTransponderIndex != -1 :
 				self.InitConfig( )
		
	def onFocus( self, aControlId ):
		pass


	def InitConfig( self ) :
		self.ResetAllControl( )

		self.AddInputControl( E_Input01, 'Satellite' , ConfigMgr.GetInstance( ).GetFormattedName( self.mCurrentSatellite.mSatelliteLongitude, self.mCurrentSatellite.mBandType ) )
		self.AddUserEnumControl( E_SpinEx01, 'LNB Type', E_LIST_LNB_TYPE, self.mSelectedIndexLnbType )

		if self.mSelectedIndexLnbType == ElisEnum.E_LNB_SINGLE :
			self.AddUserEnumControl( E_SpinEx02, 'LNB Frequency', E_LIST_SINGLE_FREQUENCY, getSingleFrequenceIndex( self.mCurrentSatellite.mLowLNB ) )
		else :
			lnbFrequency = '%d / %d / %d' % ( self.mCurrentSatellite.mLowLNB, self.mCurrentSatellite.mHighLNB, self.mCurrentSatellite.mLNBThreshold )
			self.AddInputControl( E_Input02, 'LNB Frequency', lnbFrequency )

		self.AddUserEnumControl( E_SpinEx03, '22KHz Control', USER_ENUM_LIST_ON_OFF, self.mCurrentSatellite.mFrequencyLevel )
		self.AddUserEnumControl( E_SpinEx04, 'DiSEqC 1.0 Switch', E_LIST_DISEQC_MODE, self.mCurrentSatellite.mDisEqcMode )
		self.AddUserEnumControl( E_SpinEx05, 'DiSEqC Repeat', USER_ENUM_LIST_ON_OFF, self.mCurrentSatellite.mDisEqcRepeat )
		self.AddInputControl( E_Input03, 'Transponder', self.mTransponderList[ self.mSelectedTransponderIndex ] )

		if self.mSelectedIndexLnbType == ElisEnum.E_LNB_SINGLE :
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input01, E_Input03 ]
			hideControlIds = [ E_Input02, E_SpinEx06, E_Input04, E_Input05 ]
		else :
			visibleControlIds = [ E_SpinEx01, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input01, E_Input02, E_Input03 ]
			hideControlIds = [ E_SpinEx02, E_SpinEx06, E_Input04, E_Input05 ]
			
		self.SetVisibleControls( visibleControlIds, True )
		self.SetEnableControls( visibleControlIds, True )

		self.SetVisibleControls( hideControlIds, False )
		self.InitControl( )
		self.DisableControl( )


	def DisableControl( self ) :
		enableControlIds = [ E_Input02, E_SpinEx02, E_SpinEx03 ]
		if self.mSelectedIndexLnbType == ElisEnum.E_LNB_UNIVERSAL :
			self.SetEnableControls( enableControlIds, False )
			self.getControl( E_SpinEx03 + 3 ).selectItem( 1 )	# Always On
			
		else :
			self.SetEnableControls( enableControlIds, True )
