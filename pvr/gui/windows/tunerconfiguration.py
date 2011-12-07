import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import SettingWindow, setWindowBusy
from pvr.gui.basewindow import Action
import pvr.elismgr
from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.guiconfig import *

E_MAIN_LIST_ID = 9000

class TunerConfiguration(SettingWindow):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance().getCommander( )
			
		#self.initialized = False
		#self.lastFocused = -1

		self.testSatelliteList = [ '19.2 E ASTRA1', 'TEST SATELLITE #1', 'TEST SATELLITE #2', 'TEST SATELLITE #3', 'Add New Satellite' ]
		self.tunerType = 'DiSEqC 1.0'

	def onInit(self):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.setHeaderLabel( 'Tuner 1 Configuration' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Tuner Configuration : %s' % self.tunerType )

		self.getControl( E_MAIN_LIST_ID ).addItems( self.testSatelliteList )
		'''
		self.addEnumControl( E_SpinEx01, 'Tuner2 Connect Type' , 'Select tuner 2 connection type.' )
		self.addEnumControl( E_SpinEx02, 'Tuner2 Signal Config', 'Select tuner 2 configuration.' )
		self.addEnumControl( E_SpinEx03, 'Tuner1 Type', 'Setup tuner 1.' )
		self.addEnumControl( E_SpinEx04, 'Tuner2 Type', 'Setup tuner 2.' )
		self.addLeftLabelButtonControl( E_Input01, 'Satellite Configure', 'Go to Setellite Setup.' )

		self.initControl( )
		self.showDescription( self.getFocusId( ) )
		self.disableControl( )
		self.initialized = True
		'''
		
	def onAction( self, action ):

		actionId = action.getId( )
		focusId = self.getFocusId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.getControl( E_MAIN_LIST_ID ).reset( )
			self.close( )

		elif actionId == Action.ACTION_MOVE_LEFT or actionId == Action.ACTION_MOVE_RIGHT:			
			pass
			
		elif actionId == Action.ACTION_MOVE_UP :
			pass
			#self.controlUp( )
			#self.showDescription( focusId )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			pass
			#self.controlDown( )
			#self.showDescription( focusId )


	def onClick( self, controlId ):
		winmgr.getInstance().showWindow( winmgr.WIN_ID_SATELLITE_CONFIGURATION )
		pass

		
	def onFocus( self, controlId ):
		pass
