
import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as winmgr
from pvr.gui.GuiConfig import *

from pvr.gui.BaseWindow import SettingWindow
from pvr.gui.BaseWindow import Action


class ChannelSearch( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
			
		self.initialized = False
		self.lastFocused = -1

	def onInit(self):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.setHeaderLabel( 'Channel Scan' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )

		self.AddLeftLabelButtonControl( E_Input01, 'Automatic Scan', 'Running automatic scan.' )
		self.AddLeftLabelButtonControl( E_Input02, 'Manual Scan', 'Running manual scan.' )

		self.InitControl( )
		self.ShowDescription( self.getFocusId( ) )
		self.initialized = True

		
	def onAction( self, action ):

		actionId = action.getId( )
		focusId = self.getFocusId( )

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
			


	def onClick( self, controlId ):
		if controlId == E_Input01 + 1 :
			self.ResetAllControl( )
			winmgr.getInstance().showWindow( winmgr.WIN_ID_AUTOMATIC_SCAN )
			
		elif controlId == E_Input02 + 1 :
			self.ResetAllControl( )
			winmgr.getInstance().showWindow( winmgr.WIN_ID_MANUAL_SCAN )
			

	def onFocus( self, controlId ):
		if self.initialized == False :
			return
		if ( self.lastFocused != controlId ) :
			self.ShowDescription( controlId )
			self.lastFocused = controlId
