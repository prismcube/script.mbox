import xbmc
import xbmcgui
import sys
from copy import deepcopy

import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.BaseWindow import SettingWindow, Action
from ElisProperty import ElisPropertyEnum
from pvr.gui.GuiConfig import *


class AutomaticScan( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mSatelliteIndex = 0


	def onInit(self) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		self.SetSettingWindowLabel( 'Automatic Scan' )

		self.mSatelliteIndex = 0
		self.mFormattedList = []
		self.mConfiguredSatelliteList = []		
		
		self.LoadFormattedSatelliteNameList()
		self.InitConfig( )
		self.ShowDescription( self.getFocusId( ) )
		self.mInitialized = True

		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
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
			self.ShowDescription( focusId )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )
			self.ShowDescription( focusId )
			

	def onClick( self, aControlId ):
		groupId = self.GetGroupId( aControlId )
		
		# Satellite
		if groupId == E_Input01 :
			dialog = xbmcgui.Dialog( )
			select =  dialog.select('Select satellite', self.mFormattedList )

			if select >= 0 and select != self.mSatelliteIndex :
				self.mSatelliteIndex = select
			
			self.InitConfig( )

		# Start Search
		if groupId == E_Input02 :
			if self.mSatelliteIndex == 0 :
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
				dialog.SetConfiguredSatellite( self.mConfiguredSatelliteList )
				dialog.doModal( )

			else :
				configuredSatelliteList = []
				config = self.mConfiguredSatelliteList[ self.mSatelliteIndex - 1 ]

				configuredSatelliteList.append( config )
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CHANNEL_SEARCH )
				dialog.SetConfiguredSatellite( self.mConfiguredSatelliteList )				
				dialog.doModal( )
					
		if groupId == E_SpinEx01 or groupId == E_SpinEx02 :
			self.ControlSelect( )

	def onFocus( self, aControlId ):
		if self.mInitialized == False :
			return

		if self.mLastFocused != aControlId :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId


	def InitConfig( self ) :
		self.ResetAllControl( )
		count = len( self.mFormattedList )
		if count <= 1 :
			hideControlIds = [ E_Input01, E_SpinEx01, E_SpinEx02, E_Input02 ]
			self.SetVisibleControls( hideControlIds, False )
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Has no configured satellite' )

		else :
			self.AddInputControl( E_Input01, 'Satellite', self.mFormattedList[self.mSatelliteIndex], 'Select satellite' )
			self.AddEnumControl( E_SpinEx01, 'Network Search', None, 'Network Search' )
			self.AddEnumControl( E_SpinEx02, 'Channel Search Mode', None, 'Channel Search Mode' )
			self.AddInputControl( E_Input02, 'Start Search', '','Start Search' )
			self.InitControl( )

	
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


		self.mFormattedList = []
		self.mFormattedList.append( 'All' )

		for config in self.mConfiguredSatelliteList :
			self.mFormattedList.append( self.mDataCache.Satellite_GetFormattedName( config.mSatelliteLongitude, config.mBandType ) )
			
