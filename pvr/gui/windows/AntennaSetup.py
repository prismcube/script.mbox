import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.TunerConfigMgr as ConfigMgr
import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.GuiConfig import *
from pvr.gui.BaseWindow import SettingWindow, Action

E_DEFAULT_GOURP_ID		= 9000


class AntennaSetup( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		

	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.SetPipScreen( )
		
		if ConfigMgr.GetInstance( ).GetNeedLoad( ) == True : 
			ConfigMgr.GetInstance( ).LoadOriginalTunerConfig( )
			ConfigMgr.GetInstance( ).Load( )
			ConfigMgr.GetInstance( ).SetNeedLoad( False )
		
		self.SetSettingWindowLabel( 'Antenna & Satellite Setup' )

		self.getControl( E_DEFAULT_GOURP_ID ).setVisible( False )
		self.AddEnumControl( E_SpinEx01, 'Tuner2 Connect Type', None, 'Select tuner 2 connection type.' )
		self.AddEnumControl( E_SpinEx02, 'Tuner2 Signal Config', None, 'Select tuner 2 configuration.' )
		self.AddEnumControl( E_SpinEx03, 'Tuner1 Type', None, 'Setup tuner 1.' )
		self.AddInputControl( E_Input01, ' - Tuner 1 Configuration', '', 'Go to Tuner 1 Configure.' )
		self.AddEnumControl( E_SpinEx04, 'Tuner2 Type', None, 'Setup tuner 2.' )
		self.AddInputControl( E_Input02, ' - Tuner 2 Configuration','', 'Go to Tuner 2 Configure.' )
	
		self.InitControl( )
		self.ShowDescription( )
		self.DisableControl( )
		self.mInitialized = True
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
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( 'Configure', 'Save Configuration?' )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				ConfigMgr.GetInstance( ).SatelliteConfigSaveList( )
				ConfigMgr.GetInstance( ).SetNeedLoad( True )
				self.mDataCache.LoadConfiguredSatellite( )
				self.mDataCache.LoadConfiguredTransponder( )
				
			elif dialog.IsOK( ) == E_DIALOG_STATE_NO :
				ConfigMgr.GetInstance( ).Restore( )
				ConfigMgr.GetInstance( ).SetNeedLoad( True )
				self.mDataCache.LoadConfiguredSatellite( )
				self.mDataCache.LoadConfiguredTransponder( )
				
			elif dialog.IsOK( ) == E_DIALOG_STATE_CANCEL :
				return

			self.ResetAllControl( )
			self.SetVideoRestore( )
			self.close( )

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
		self.DisableControl( )
		groupId = self.GetGroupId( aControlId )
		if groupId == E_Input01 or groupId == E_Input02 :
		
			configuredList = ConfigMgr.GetInstance( ).GetConfiguredSatelliteList( )
			if len( configuredList ) <= 0 :
				ConfigMgr.GetInstance( ).AddConfiguredSatellite( 0 )

			if groupId == E_Input01 :
			
				ConfigMgr.GetInstance( ).SetCurrentTunerIndex( E_TUNER_1 )
				configcontrol = E_SpinEx03

			elif groupId == E_Input02 :

				ConfigMgr.GetInstance( ).SetCurrentTunerIndex( E_TUNER_2 )
				configcontrol = E_SpinEx04

			if self.GetSelectedIndex( configcontrol ) == E_SIMPLE_LNB :
				ConfigMgr.GetInstance( ).SetCurrentConfigIndex( 0 )
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
		
		if groupId == E_SpinEx01 or groupId == E_SpinEx02 or groupId == E_SpinEx03 or groupId == E_SpinEx04 :
			self.ControlSelect( )

	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return
		if self.mLastFocused != aControlId :
			self.ShowDescription( )
			self.mLastFocused = aControlId


	def DisableControl( self ) :
		selectedIndex1 = self.GetSelectedIndex( E_SpinEx01 )
		if ( selectedIndex1 == 1 ) :
			self.SetEnableControl( E_SpinEx02, False )
			self.getControl( E_SpinEx02 + 3 ).selectItem( 0 )
		else :
			self.SetEnableControl( E_SpinEx02, True )

		selectedIndex2 = self.GetSelectedIndex( E_SpinEx02 )	
		if ( selectedIndex2 == 0 ) :
			self.SetEnableControl( E_SpinEx04, False )
			self.SetEnableControl( E_Input02, False )
			self.getControl( E_SpinEx04 + 3 ).selectItem( self.GetSelectedIndex( E_SpinEx03 ) )
		else :
			self.SetEnableControl( E_SpinEx04, True)
			self.SetEnableControl( E_Input02, True )
