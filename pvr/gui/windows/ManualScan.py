import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DiaMgr
import pvr.TunerConfigMgr as configMgr
from  pvr.TunerConfigMgr import *
from pvr.gui.GuiConfig import *
from ElisEnum import ElisEnum

from pvr.gui.BaseWindow import SettingWindow, Action

class ManualScan( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
			
		self.mSelectedSatelliteIndex = 0
		self.mSelectedTransponderIndex = 0		
		self.mAllSatellitelist = []
		self.mTransponderList = []

		self.mFormattedSatelliteList = []
		self.mFormattedTransponderList = []

		self.mIsManualSetup = 0
		self.mConfigTransponder = None


	def onInit(self):
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		self.SetSettingWindowLabel( 'Manual Scan' )
		self.mIsManualSetup = 0
		
		self.mSelectedSatelliteIndex = 0
		self.mSelectedTransponderIndex = 0		
		self.mAllSatellitelist = []
		self.mConfiguredSatelliteList = []
		
		self.mAllSatellitelist = self.mCommander.Satellite_GetList( ElisEnum.E_SORT_INSERTED )
		self.LoadFormattedSatelliteNameList()

		self.LoadFormattedTransponderNameList( )

		self.SetConfigTransponder( )

		self.InitConfig( )
		
		self.ShowDescription( self.getFocusId( ) )
		self.mInitialized = True

		
	def onAction( self, aAction ):

		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		self.GlobalAction( actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.ResetAllControl( )
			self.close( )
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mConfigTransponder.printdebug()
			self.ResetAllControl( )
			self.close( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )				

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			self.ShowDescription( focusId )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )
			self.ShowDescription( focusId )
			

	def onClick( self, aControlId ):

		groupId = self.GetGroupId( aControlId )

		# Satellite		
		if groupId == E_Input01 :
			dialog = xbmcgui.Dialog( )
			select = dialog.select('Select satellite', self.mFormattedSatelliteList )

			if select >= 0:
				self.mSelectedSatelliteIndex = select
				self.mSelectedTransponderIndex = 0
				self.LoadFormattedTransponderNameList( )
				self.SetConfigTransponder( )
				self.InitConfig( )

		# Transponder
		elif groupId == E_Input02 :
			if self.mIsManualSetup == 0 :
				dialog = xbmcgui.Dialog( )
				select = dialog.select('Select Transponder', self.mFormattedTransponderList )

				if select >=0 :
					self.mSelectedTransponderIndex = select
					self.SetConfigTransponder( )
					self.InitConfig( )

			else :
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
				dialog.SetDialogProperty( 'Frequency', '%d' % self.mConfigTransponder.mFrequency, 5 )
	 			dialog.doModal( )
	 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
	 				tempval = dialog.GetString( )
					if int( tempval ) > 13000 :
						self.mConfigTransponder.mFrequency = 13000
					elif int( tempval ) < 3000 :
						self.mConfigTransponder.mFrequency = 3000
					else :
						self.mConfigTransponder.mFrequency = int( tempval )

					self.SetControlLabel2String( E_Input02, '%d MHz' % self.mConfigTransponder.mFrequency )

		# Symbol Rate
		elif groupId == E_Input03 :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( 'Symbol Rate', '%d' % self.mConfigTransponder.mSymbolRate, 5 )
 			dialog.doModal( )
 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
 				tempval = dialog.GetString( )
				if int( tempval ) > 60000 :
					self.mConfigTransponder.mSymbolRate = 60000
				elif int( tempval ) < 1000 :
					self.mConfigTransponder.mSymbolRate = 1000
				else :
					self.mConfigTransponder.mSymbolRate = int( tempval )

				self.SetControlLabel2String( E_Input03, '%d KS/s' % self.mConfigTransponder.mSymbolRate )

		# Start Search
		elif groupId == E_Input04 : #ToDO : Have to support manual input
			transponderList = []
			config = self.mConfiguredSatelliteList[self.mSelectedSatelliteIndex]

			transponderList.append( self.mConfigTransponder )

			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
			dialog.SetTransponder( config.mSatelliteLongitude, config.mBandType, transponderList )
			dialog.doModal( )

		# Manual Setup
		elif groupId == E_SpinEx01 :
			self.mIsManualSetup = self.GetSelectedIndex( E_SpinEx01 )
			self.InitConfig( )

		# DVB Type
		elif groupId == E_SpinEx02 :
			if self.GetSelectedIndex( E_SpinEx02 ) == 0 :
				self.mConfigTransponder.mFECMode = ElisEnum.E_FEC_UNDEFINED		
			else :
				self.mConfigTransponder.mFECMode = ElisEnum.E_DVBS2_QPSK_1_2
	
			self.DisableControl( )

		# FEC
		elif groupId == E_SpinEx03 :
			self.ControlSelect( )
			property = ElisPropertyEnum( 'FEC', self.mCommander )
			self.mConfigTransponder.mFECMode = property.GetProp( )
		
		elif groupId == E_SpinEx04 :
			self.mConfigTransponder.mPolarization = self.GetSelectedIndex( E_SpinEx04 )

		elif groupId == E_SpinEx05 or groupId == E_SpinEx06   :
			self.ControlSelect( )


	def onFocus( self, aControlId ):
		if self.mInitialized == False :
			return

		if self.mLastFocused != aControlId :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId


	def InitConfig( self ) :

		self.ResetAllControl( )	

		count = len( self.mFormattedSatelliteList )
		
		if count <= 0 :
			hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04, E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06 ]
			self.SetVisibleControls( hideControlIds, False )
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Has no configured satellite' )

		else :
			self.AddInputControl( E_Input01, 'Satellite', self.mFormattedSatelliteList[self.mSelectedSatelliteIndex], 'Select satellite' )
			self.AddUserEnumControl( E_SpinEx01, 'Custom Setup', USER_ENUM_LIST_ON_OFF, self.mIsManualSetup )

			if self.mIsManualSetup == 0 :
				self.AddInputControl( E_Input02, ' - Select Transponder Frequency', '%d MHz' % self.mConfigTransponder.mFrequency, 'Select Transponder Frequency' )
			else :
				self.AddInputControl( E_Input02, ' - Set Frequency', '%d MHz' % self.mConfigTransponder.mFrequency, 'Input Manual Frequency' )
			# Frequency
#			self.AddInputControl( E_Input03, ' - Set Frequency', '', 'Input Manual Frequency' )
			
			# DVB Type
			self.AddEnumControl( E_SpinEx02, 'DVB Type', ' - DVB Type', 'Select DVB Type' )

			if self.mConfigTransponder.mFECMode == ElisEnum.E_FEC_UNDEFINED :
				self.SetProp( E_SpinEx02, 0 )
			else :
				self.SetProp( E_SpinEx02, 1 )

			# FEC
			self.AddEnumControl( E_SpinEx03, 'FEC', ' - FEC', 'Select FEC' )
			self.SetProp( E_SpinEx03, self.mConfigTransponder.mFECMode )

			# POL
			self.AddEnumControl( E_SpinEx04, 'Polarisation', ' - Polarization', 'Select Polarization' )
			self.SetProp( E_SpinEx04, self.mConfigTransponder.mPolarization )

			# Symbolrate
			self.AddInputControl( E_Input03, ' - Symbol Rate', '%d KS/s' % self.mConfigTransponder.mSymbolRate , 'Select Symbol Rate' )
			
			self.AddEnumControl( E_SpinEx05, 'Network Search', None, 'Select Network Search' )
			self.AddEnumControl( E_SpinEx06, 'Channel Search Mode',None, 'Select Channel Search Mode' )
			self.AddInputControl( E_Input04, 'Start Search', '', 'Start Search' )

			self.InitControl( )
			self.DisableControl( )


	def GetFormattedName( self, aLongitude, aBand ) :
	
		found = False	

		for satellite in self.mAllSatellitelist :
			if aLongitude == satellite.mLongitude and aBand == satellite.mBand :
				found = True
				break

		if found == True :
			dir = 'E'

			tmpLongitude  = aLongitude
			if tmpLongitude > 1800 :
				dir = 'W'
				tmpLongitude = 3600 - aLongitude

			formattedName = '%d.%d %s %s' %( int( tmpLongitude / 10 ), tmpLongitude % 10, dir, satellite.mName )
			return formattedName

		return 'UnKnown'


	def LoadFormattedSatelliteNameList( self ) :

		configuredSatelliteList1 = []
		configuredSatelliteList1 = self.mCommander.Satelliteconfig_GetList( E_TUNER_1 )		

		configuredSatelliteList2 = []
		configuredSatelliteList2 = self.mCommander.Satelliteconfig_GetList( E_TUNER_2 )		

		property = ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander )

		self.mConfiguredSatelliteList = deepcopy( configuredSatelliteList1 )
		
		if property.GetProp( ) == E_DIFFERENT_TUNER :
			for config in configuredSatelliteList2 :
				find = False
				for compare in configuredSatelliteList1 :
					if config.mSatelliteLongitude == compare.mSatelliteLongitude and config.mBandType == compare.mBandType:
						find = True
						break

				if find == False :
					self.mConfiguredSatelliteList.append( config )


		self.mFormattedSatelliteList = []
		for config in self.mConfiguredSatelliteList :
			self.mFormattedSatelliteList.append( self.GetFormattedName( config.mSatelliteLongitude, config.mBandType ) )


	def LoadFormattedTransponderNameList( self ) :

		satellite = self.mAllSatellitelist[self.mSelectedSatelliteIndex]

		self.mTransponderList = []
		self.mTransponderList = self.mCommander.Transponder_GetList( satellite.mLongitude, satellite.mBand )

		self.mFormattedTransponderList = []
		
		for i in range( len( self.mTransponderList ) ) :
			self.mTransponderList[i].printdebug()
			#self.mFormattedTransponderList.append( '%d' % ( i + 1 ) + ' %d' % self.mTransponderList[i].mFrequency + ' MHz /' + ' %d' % self.mTransponderList[i].mSymbolRate + ' KS/s' )
			self.mFormattedTransponderList.append( '%d' % self.mTransponderList[i].mFrequency + ' MHz' )


	def SetConfigTransponder( self ) :
		self.mConfigTransponder = ElisITransponderInfo( )
		self.mConfigTransponder.reset( )
		self.mConfigTransponder.mFrequency = self.mTransponderList[self.mSelectedTransponderIndex].mFrequency
		self.mConfigTransponder.mFECMode = self.mTransponderList[self.mSelectedTransponderIndex].mFECMode
		self.mConfigTransponder.mSymbolRate = self.mTransponderList[self.mSelectedTransponderIndex].mSymbolRate
		self.mConfigTransponder.mPolarization = self.mTransponderList[self.mSelectedTransponderIndex].mPolarization
		self.mConfigTransponder.mTsid = self.mTransponderList[self.mSelectedTransponderIndex].mTsid
		self.mConfigTransponder.mOnid = self.mTransponderList[self.mSelectedTransponderIndex].mOnid
		self.mConfigTransponder.mNid = self.mTransponderList[self.mSelectedTransponderIndex].mNid


	def DisableControl( self ) :
#		disablecontrols = [ E_SpinEx02, E_SpinEx03, E_SpinEx04, E_Input03, E_Input03 ]
		disablecontrols = [ E_SpinEx02, E_SpinEx03, E_SpinEx04, E_Input03 ]
		if self.mIsManualSetup == 0 :
			self.SetEnableControls( disablecontrols, False )
			#self.SetEnableControl( E_Input02, True )
		else :
			self.SetEnableControls( disablecontrols, True )
			#self.SetEnableControl( E_Input02, False )

			if self.mConfigTransponder.mFECMode == 0 :
				self.getControl( E_SpinEx03 + 3 ).getListItem( 0 ).setLabel2( 'Automatic' )
				self.getControl( E_SpinEx03 + 3 ).selectItem( 0 )
				self.SetEnableControl( E_SpinEx03, False )
			else :
				self.SetProp( E_SpinEx03, 0 )
				self.getControl( E_SpinEx03 + 3 ).getListItem( 0 ).setLabel2( 'QPSK 1/2' )
				self.SetEnableControl( E_SpinEx03, True )
		
