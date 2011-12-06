import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import SettingWindow, setWindowBusy
from pvr.gui.basewindow import Action
import pvr.elismgr
from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.guiconfig import *


class TunerConfiguration(SettingWindow):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance().getCommander( )
			
		#self.initialized = False
		#self.lastFocused = -1

	def onInit(self):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.setHeaderLabel( 'Tuner 1 Configuration' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )
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
			#self.resetAllControl( )
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
		pass

		
	def onFocus( self, controlId ):
		pass
