import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
#import pvr.tunerconfigmgr as configmgr
#from  pvr.tunerconfigmgr import *
from pvr.gui.guiconfig import *

from pvr.gui.basewindow import SettingWindow
from pvr.gui.basewindow import Action
#import pvr.elismgr
#from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt
#from pvr.elisevent import ElisEnum


class ManualScan( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
		#self.commander = pvr.elismgr.getInstance( ).getCommander( )
			
		self.initialized = False
		self.lastFocused = -1

	def onInit(self):
		#self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.setHeaderLabel( 'Manual Scan' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )

		self.addInputControl( E_Input01, 'Satellite', 'TEST', None, 'Select satellite' )
		self.addInputControl( E_Input02, 'Transponder Frequency', '11111', None, 'Select Transponder Frequency' )
		self.addUserEnumControl( E_SpinEx01, 'DVB Type', USER_ENUM_LIST_DVB_TYPE, 0, 'Select DVB type' )
		self.addUserEnumControl( E_SpinEx02, 'FEC', USER_ENUM_LIST_FEC, 0, 'Select FEC' )
		self.addUserEnumControl( E_SpinEx03, 'Polarization', USER_ENUM_LIST_POLARIZATION, 0, 'Select Polarization' )
		self.addUserEnumControl( E_SpinEx04, 'Symbol Rate', USER_ENUM_LIST_SYMBOL_RATE, 0, 'Select Symbol Rate' )
		self.addUserEnumControl( E_SpinEx05, 'Network Search', USER_ENUM_LIST_ON_OFF, 0, 'Select Network Search' )
		self.addLeftLabelButtonControl( E_Input03, 'Start Search', 'Start Search' )

		self.initControl( )
		self.showDescription( self.getFocusId( ) )
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
		pass
			

	def onFocus( self, controlId ):
		if self.initialized == False :
			return
		if ( self.lastFocused != controlId ) :
			self.showDescription( controlId )
			self.lastFocused = controlId