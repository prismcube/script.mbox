import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.GuiConfig import *
from pvr.gui.BaseWindow import SettingWindow, Action
from ElisProperty import ElisPropertyEnum
from pvr.Util import LOG_ERR


E_DEFAULT_GOURP_ID		= 9000


class AntennaSetup( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mFirstInstallationType = False

	def onInit( self ) :
		self.getControl( E_DEFAULT_GOURP_ID ).setVisible( False )

		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		if self.mFirstInstallationType == True :
			self.DrawFirstTimeInstallationStep( E_STEP_ANTENNA )
		else :
			self.DrawFirstTimeInstallationStep( None )

		self.SetPipScreen( )
		
		if self.mTunerMgr.GetNeedLoad( ) == True : 
			self.mTunerMgr.LoadOriginalTunerConfig( )
			self.mTunerMgr.Load( )
			self.mTunerMgr.SetNeedLoad( False )

		self.SetSettingWindowLabel( 'Antenna & Satellite Setup' )


		self.AddEnumControl( E_SpinEx01, 'Tuner2 Connect Type', None, 'Select tuner 2 connection type.' )
		self.AddEnumControl( E_SpinEx02, 'Tuner2 Signal Config', None, 'Select tuner 2 configuration.' )
		self.AddEnumControl( E_SpinEx03, 'Tuner1 Type', None, 'Setup tuner 1.' )
		self.AddInputControl( E_Input01, ' - Tuner 1 Configuration', '', 'Go to Tuner 1 Configure.' )
		self.AddEnumControl( E_SpinEx04, 'Tuner2 Type', None, 'Setup tuner 2.' )
		self.AddInputControl( E_Input02, ' - Tuner 2 Configuration','', 'Go to Tuner 2 Configure.' )
		if self.mFirstInstallationType == True :
			self.AddPrevNextButton( )
			self.getControl( E_FIRST_TIME_INSTALLATION_NEXT_LABEL ).setLabel( 'Next' )
		self.setVisibleButton( )

		self.InitControl( )
		self.ShowDescription( )
		self.DisableControl( )
		self.mInitialized = True
		self.SetFocusControl( E_SpinEx01 )
		self.getControl( E_DEFAULT_GOURP_ID ).setVisible( True )

		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )

		self.GlobalAction( actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			if self.mFirstInstallationType == True :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( 'Are you sure?', 'Do you want to stop first time installation?' )
				dialog.doModal( )

				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					self.OpenBusyDialog( )
					if self.CompareConfigurationSatellite( ) == False or self.CompareConfigurationProperty( ) == False :
						self.CancelConfiguration( )
					self.mTunerMgr.SetNeedLoad( True )
					self.ResetAllControl( )
					WinMgr.GetInstance().GetWindow( WinMgr.WIN_ID_FIRST_INSTALLATION ).SetAlreadyClose( True )
					self.close( )
					self.CloseBusyDialog( )
				elif dialog.IsOK( ) == E_DIALOG_STATE_NO :
					return	
				elif dialog.IsOK( ) == E_DIALOG_STATE_CANCEL :
					return

			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( 'Configure', 'Save Configuration?' )
				dialog.doModal( )

				if dialog.IsOK( ) == E_DIALOG_STATE_CANCEL :
					return

				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					self.OpenBusyDialog( )
					if self.CompareConfigurationSatellite( ) == False or self.CompareConfigurationProperty( ) == False :
						self.SaveConfiguration( )
						self.ReTune( )
					
				elif dialog.IsOK( ) == E_DIALOG_STATE_NO :
					self.OpenBusyDialog( )
					if self.CompareConfigurationSatellite( ) == False or self.CompareConfigurationProperty( ) == False :
						self.CancelConfiguration( )
					self.mTunerMgr.SetNeedLoad( True )

				self.ResetAllControl( )
				self.SetVideoRestore( )
				self.close( )
				self.CloseBusyDialog( )
			

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )				

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			self.ShowDescription( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )
			self.ShowDescription( )
			

	def onClick( self, aControlId ) :
		groupId = self.GetGroupId( aControlId )
		if groupId == E_Input01 or groupId == E_Input02 :
			if groupId == E_Input01 :
				self.mTunerMgr.SetCurrentTunerIndex( E_TUNER_1 )
				configcontrol = E_SpinEx03

			elif groupId == E_Input02 :
				self.mTunerMgr.SetCurrentTunerIndex( E_TUNER_2 )
				configcontrol = E_SpinEx04
		
			configuredList = self.mTunerMgr.GetConfiguredSatelliteList( )
			if configuredList and configuredList[0].mError == 0 :
				pass
			else :
				self.mTunerMgr.AddConfiguredSatellite( 0 )

			if self.GetSelectedIndex( configcontrol ) == E_SIMPLE_LNB :
				self.mTunerMgr.SetCurrentConfigIndex( 0 )
				self.ResetAllControl( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_SIMPLE )
			
			elif self.GetSelectedIndex( configcontrol ) == E_MOTORIZE_USALS :
				self.ResetAllControl( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_MOTORIZED_USALS )
				
			elif self.GetSelectedIndex( configcontrol ) == E_ONE_CABLE :
				self.ResetAllControl( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_ONECABLE )

			else :
				self.ResetAllControl( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TUNER_CONFIGURATION )
		
		if groupId == E_SpinEx01 or groupId == E_SpinEx02 :
			self.ControlSelect( )
			self.DisableControl( )

		elif groupId == E_SpinEx03 :
			self.ControlSelect( )
			self.DisableControl( )
			configuredList = self.mTunerMgr.GetConfiguredSatellitebyTunerIndex( E_TUNER_1 ) 
			if configuredList :
				tunertype = self.GetSelectedIndex( E_SpinEx03 )
				for satellite in configuredList :
					self.mTunerMgr.SetTunerTypeFlag( satellite, tunertype )

		elif groupId == E_SpinEx04 :
			self.ControlSelect( )
			self.DisableControl( )
			configuredList = self.mTunerMgr.GetConfiguredSatellitebyTunerIndex( E_TUNER_2 )
			if configuredList :
				tunertype = self.GetSelectedIndex( E_SpinEx04 )
				for satellite in configuredList :
					self.mTunerMgr.SetTunerTypeFlag( satellite, tunertype )

		elif aControlId == E_FIRST_TIME_INSTALLATION_NEXT or aControlId == E_FIRST_TIME_INSTALLATION_PREV :
			self.OpenBusyDialog( )
			if self.CompareConfigurationSatellite( ) == False or self.CompareConfigurationProperty( ) == False :
				self.SaveConfiguration( )
				self.ReTune( )
			self.ResetAllControl( )
			if aControlId == E_FIRST_TIME_INSTALLATION_NEXT :
				WinMgr.GetInstance().GetWindow( WinMgr.WIN_ID_FIRST_INSTALLATION ).SetResultAntennaStep( True )
			else :
				WinMgr.GetInstance().GetWindow( WinMgr.WIN_ID_FIRST_INSTALLATION ).SetResultAntennaStep( False )
			self.close( )
			self.mTunerMgr.SetNeedLoad( True )
			self.CloseBusyDialog( )

		
	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return
		if self.mLastFocused != aControlId :
			self.ShowDescription( )
			self.mLastFocused = aControlId


	def SaveConfiguration( self ) :
		ret = self.mTunerMgr.SatelliteConfigSaveList( )
		self.mTunerMgr.SetNeedLoad( True )
		self.mDataCache.LoadConfiguredSatellite( )
		self.mDataCache.LoadConfiguredTransponder( )


	def CancelConfiguration( self ) :
		self.mTunerMgr.Restore( )
	

	def DisableControl( self ) :
		selectedIndex = self.GetSelectedIndex( E_SpinEx01 )
		if selectedIndex == E_TUNER_LOOPTHROUGH :
			control = self.getControl( E_SpinEx02 + 3 )
			time.sleep( 0.02 )
			control.selectItem( E_SAMEWITH_TUNER )
			self.SetProp( E_SpinEx02, E_SAMEWITH_TUNER )
			self.SetEnableControl( E_SpinEx02, False )
		else :
			self.SetEnableControl( E_SpinEx02, True )

		selectedIndex = self.GetSelectedIndex( E_SpinEx02 )	
		if selectedIndex == E_SAMEWITH_TUNER :
			control = self.getControl( E_SpinEx04 + 3 )
			time.sleep( 0.02 )
			control.selectItem( self.GetSelectedIndex( E_SpinEx03 ) )
			self.SetProp( E_SpinEx04, self.GetSelectedIndex( E_SpinEx03 ) )
			self.SetEnableControl( E_SpinEx04, False )
			self.SetEnableControl( E_Input02, False )

		else :
			self.SetEnableControl( E_SpinEx04, True)
			self.SetEnableControl( E_Input02, True )


	def setVisibleButton( self ) :
		if self.mFirstInstallationType == True :
			self.SetVisibleControl( E_FIRST_TIME_INSTALLATION_NEXT, True )
			self.SetVisibleControl( E_FIRST_TIME_INSTALLATION_PREV, True )
		else :
			self.SetVisibleControl( E_FIRST_TIME_INSTALLATION_NEXT, False )
			self.SetVisibleControl( E_FIRST_TIME_INSTALLATION_PREV, False )			


	def SetWindowType( self, aType ) :
		self.mFirstInstallationType = aType


	def ReTune( self ) :
		channel = self.mDataCache.Channel_GetCurrent( )
		if channel == None or channel.mError != 0 :
			LOG_ERR( 'Load Channel_GetCurrent None' )
		else :
			self.mCommander.Channel_InvalidateCurrent( )
			self.mDataCache.Channel_SetCurrent( channel.mNumber, channel.mServiceType )


	def CompareConfigurationSatellite( self ) :
		configuredList1		= self.mTunerMgr.GetConfiguredSatellitebyTunerIndex( E_TUNER_1 )	
		oriconfiguredList1	= self.mDataCache.Satellite_Get_ConfiguredList_By_TunerIndex( E_TUNER_1 )
		configuredList2		= self.mTunerMgr.GetConfiguredSatellitebyTunerIndex( E_TUNER_2 ) 
		oriconfiguredList2	= self.mDataCache.Satellite_Get_ConfiguredList_By_TunerIndex( E_TUNER_2 )
		if oriconfiguredList1 == None or oriconfiguredList2 == None :
			return False
		
		if self.mTunerMgr.GetCurrentTunerConfigType( ) == E_SAMEWITH_TUNER :
			if len( configuredList1 ) != len( oriconfiguredList1 ) :
				return False
		else :
			if len( configuredList2 ) != len( oriconfiguredList2 ) :
				return False

		if self.mTunerMgr.GetCurrentTunerConfigType( ) == E_SAMEWITH_TUNER :
			for i in range( len( configuredList1 ) ) :
				if configuredList1[i].__dict__ != oriconfiguredList1[i].__dict__ :
					return False

		else :
			for i in range( len( configuredList2 ) ) :
				if configuredList2[i].__dict__ != oriconfiguredList2[i].__dict__ :
					return False

		return True


	def CompareConfigurationProperty( self ) :
		if self.mTunerMgr.GetOriginalTunerConfig( ) != self.mTunerMgr.GetCurrentTunerConfig( ) :
			return False
		return True