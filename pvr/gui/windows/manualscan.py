import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
#import pvr.tunerconfigmgr as configmgr
#from  pvr.tunerconfigmgr import *
from pvr.gui.guiconfig import *

from pvr.gui.basewindow import SettingWindow
from pvr.gui.basewindow import Action


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
		self.addEnumControl( E_SpinEx01, 'DVB Type', None, 'Select DVB type' )
		self.addEnumControl( E_SpinEx02, 'FEC', None, 'Select FEC' )
		self.addEnumControl( E_SpinEx03, 'Polarisation', None, 'Select Polarization' )
		self.addEnumControl( E_SpinEx04, 'Symbol Rate', None, 'Select Symbol Rate' )
		self.addEnumControl( E_SpinEx05, 'Network Search', None, 'Select Network Search' )
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