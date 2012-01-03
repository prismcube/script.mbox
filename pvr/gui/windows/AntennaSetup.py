
import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as winmgr
import pvr.tunerconfigmgr as configmgr
from  pvr.tunerconfigmgr import *
from pvr.gui.guiconfig import *

from pvr.gui.basewindow import SettingWindow
from pvr.gui.basewindow import Action
import pvr.ElisMgr
from elisproperty import ElisPropertyEnum, ElisPropertyInt
from elisenum import ElisEnum

from pvr.gui.windows.satelliteconfigsimple import SatelliteConfigSimple
from pvr.gui.windows.motorizeconfiguration import MotorizeConfiguration
from pvr.gui.windows.onecableconfiguration import OneCableConfiguration

E_MAIN_GROUP_ID	= 9000

class AntennaSetup( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
		self.commander = pvr.ElisMgr.getInstance( ).getCommander( )
			
		self.initialized = False
		self.lastFocused = -1

	def onInit(self):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		print '#################### Load Configs ###############################'
		if configmgr.getInstance( ).getNeedLoad( ) == True : 
			configmgr.getInstance( ).loadOriginalTunerConfig( )
		
			configmgr.getInstance( ).load( )
			configmgr.getInstance( ).setNeedLoad( False )
		
		self.setHeaderLabel( 'Antenna & Satellite Setup' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )

		self.AddEnumControl( E_SpinEx01, 'Tuner2 Connect Type', None, 'Select tuner 2 connection type.' )
		self.AddEnumControl( E_SpinEx02, 'Tuner2 Signal Config', None, 'Select tuner 2 configuration.' )
		self.AddEnumControl( E_SpinEx03, 'Tuner1 Type', None, 'Setup tuner 1.' )
		self.AddLeftLabelButtonControl( E_Input01, ' - Tuner 1 Configuration', 'Go to Tuner 1 Configure.' )
		self.AddEnumControl( E_SpinEx04, 'Tuner2 Type', None, 'Setup tuner 2.' )
		self.AddLeftLabelButtonControl( E_Input02, ' - Tuner 2 Configuration', 'Go to Tuner 2 Configure.' )

		self.InitControl( )
		self.ShowDescription( self.getFocusId( ) )
		self.disableControl( )
		self.initialized = True


	def onAction( self, action ):

		actionId = action.getId( )
		focusId = self.getFocusId( )
		print 'dhkim test onAction Button Id = %s' % actionId

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
		
			if xbmcgui.Dialog( ).yesno('Configure', 'Are you sure?') == 1 :
				configmgr.getInstance( ).satelliteconfigSaveList( )
			else :
				configmgr.getInstance( ).restore( )

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
			


	def onClick( self, controlId ):
		self.disableControl( )
		if controlId == E_Input01 + 1 or controlId == E_Input02 + 1 :
		
			configuredList = configmgr.getInstance( ).getConfiguredSatelliteList( )
			if len( configuredList ) <= 0 :
				configmgr.getInstance().addConfiguredSatellite( 0 )

			if controlId == E_Input01 + 1 :
			
				configmgr.getInstance().setCurrentTunerIndex( E_TUNER_1 ) 

			elif controlId == E_Input02 + 1 :

				configmgr.getInstance().setCurrentTunerIndex( E_TUNER_2 )

			if self.GetSelectedIndex( E_SpinEx03 ) == E_SIMPLE_LNB :
				configmgr.getInstance( ).setCurrentConfigIndex
				configmgr.getInstance( ).setCurrentConfigIndex( 0 )
				self.ResetAllControl( )
				
				import pvr.Platform 
				scriptDir = pvr.Platform.getPlatform().GetScriptDir()
				SatelliteConfigSimple('satelliteconfiguration.xml', scriptDir).doModal()
			
			elif self.GetSelectedIndex( E_SpinEx03 ) == E_MOTORIZED_USALS :

				self.ResetAllControl( )
				
				import pvr.Platform 
				scriptDir = pvr.Platform.getPlatform().GetScriptDir()
				MotorizeConfiguration('satelliteconfiguration.xml', scriptDir).doModal()

			elif self.GetSelectedIndex( E_SpinEx03 ) == E_ONE_CABLE :
			
				self.ResetAllControl( )
				
				import pvr.Platform 
				scriptDir = pvr.Platform.getPlatform().GetScriptDir()
				OneCableConfiguration('onecableconfiguration.xml', scriptDir).doModal()

			else :

				self.ResetAllControl( )
				winmgr.getInstance().showWindow( winmgr.WIN_ID_TUNER_CONFIGURATION )
			

		groupId = self.GetGroupId( controlId )
		
		if groupId == E_SpinEx01 or groupId == E_SpinEx02 or groupId == E_SpinEx03 or groupId == E_SpinEx04 :
			self.ControlSelect()

	def onFocus( self, controlId ):
		if self.initialized == False :
			return
		if ( self.lastFocused != controlId ) :
			self.ShowDescription( controlId )
			self.lastFocused = controlId


	def disableControl( self ):
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
