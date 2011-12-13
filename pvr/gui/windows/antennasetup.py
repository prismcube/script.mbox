
import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
import pvr.tunerconfigmgr as configmgr
from  pvr.tunerconfigmgr import *
from pvr.gui.guiconfig import *

from pvr.gui.basewindow import SettingWindow, setWindowBusy
from pvr.gui.basewindow import Action
import pvr.elismgr
from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt
from pvr.elisevent import ElisEnum

E_MAIN_GROUP_ID	= 9000

class AntennaSetup( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
		self.commander = pvr.elismgr.getInstance( ).getCommander( )
			
		#self.ctrlMainGroup = None
		self.initialized = False
		self.lastFocused = -1
		#self.tunerIndex = 0

	def onInit(self):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.setHeaderLabel( 'Antenna & Satellite Setup' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )

		self.addEnumControl( E_SpinEx01, 'Tuner2 Connect Type' , 'Select tuner 2 connection type.' )
		self.addEnumControl( E_SpinEx02, 'Tuner2 Signal Config', 'Select tuner 2 configuration.' )
		self.addEnumControl( E_SpinEx03, 'Tuner1 Type', 'Setup tuner 1.' )
		self.addLeftLabelButtonControl( E_Input01, ' - Tuner 1 Configuration', 'Go to Tuner 1 Configure.' )
		self.addEnumControl( E_SpinEx04, 'Tuner2 Type', 'Setup tuner 2.' )
		self.addLeftLabelButtonControl( E_Input02, ' - Tuner 2 Configuration', 'Go to Tuner 2 Configure.' )

		self.initControl( )
		self.showDescription( self.getFocusId( ) )
		self.disableControl( )
		self.initialized = True


	def onAction( self, action ):

		actionId = action.getId( )
		focusId = self.getFocusId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.resetAllControl( )
			self.close( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.controlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.controlRight( )				

		elif actionId == Action.ACTION_MOVE_UP :
			self.controlUp( )
			self.showDescription( focusId )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.controlDown( )
			self.showDescription( focusId )
			


	def onClick( self, controlId ):
		self.disableControl( )
		if controlId == E_Input01 + 1 or controlId == E_Input02 + 1 :
			if controlId == E_Input01 + 1 :
				configmgr.getInstance().setCurrentTunerIndex( 0 ) 
				configmgr.getInstance().setCurrentTunerType( self.getSelectedIndex( E_SpinEx03 ) )
			elif controlId == E_Input02 + 1 :
				configmgr.getInstance().setCurrentTunerIndex( 1 )
				configmgr.getInstance().setCurrentTunerType( self.getSelectedIndex( E_SpinEx04 ) )

			
			if self.getSelectedIndex( E_SpinEx03 ) == E_SIMPLE_LNB :
				configmgr.getInstance( ).load( )
				configuredList = configmgr.getInstance( ).getConfiguredSatellite( )
				configmgr.getInstance( ).setCurrentLongitue( int( configuredList[0][2] ) )
				self.resetAllControl( )
				winmgr.getInstance().showWindow( winmgr.WIN_ID_SATELLITE_CONFIGURATION )
			
			elif self.getSelectedIndex( E_SpinEx03 ) == E_MOTORIZED_1_2  or self.getSelectedIndex( E_SpinEx03 ) == E_MOTORIZED_USALS :
				self.resetAllControl( )
				winmgr.getInstance().showWindow( winmgr.WIN_ID_MOTORIZE_CONFIGURATION )
			else :
				self.resetAllControl( )
				winmgr.getInstance().showWindow( winmgr.WIN_ID_TUNER_CONFIGURATION )
			

	def onFocus( self, controlId ):
		if self.initialized == False :
			return
		if ( self.lastFocused != controlId ) :
			self.showDescription( controlId )
			self.lastFocused = controlId

	def disableControl( self ):
		selectedIndex1 = self.getSelectedIndex( E_SpinEx01 )
		if ( selectedIndex1 == 1 ) :
			self.setEnableControl( E_SpinEx02, False )
			self.getControl( E_SpinEx02 + 3 ).selectItem( 0 )
		else :
			self.setEnableControl( E_SpinEx02, True )

		selectedIndex2 = self.getSelectedIndex( E_SpinEx02 )	
		if ( selectedIndex2 == 0 ) :
			self.setEnableControl( E_SpinEx04, False )
			self.setEnableControl( E_Input02, False )
			self.getControl( E_SpinEx04 + 3 ).selectItem( self.getSelectedIndex( E_SpinEx03 ) )
		else :
			self.setEnableControl( E_SpinEx04, True)
			self.setEnableControl( E_Input02, True )

