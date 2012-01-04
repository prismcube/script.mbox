
import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
from pvr.gui.GuiConfig import *

from pvr.gui.BaseWindow import SettingWindow, Action


class ChannelSearch( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
			
		self.mInitialized = False
		self.mLastFocused = -1

	def onInit(self):
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		self.SetHeaderLabel( 'Channel Scan' )
		self.SetFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )

		self.AddLeftLabelButtonControl( E_Input01, 'Automatic Scan', 'Running automatic scan.' )
		self.AddLeftLabelButtonControl( E_Input02, 'Manual Scan', 'Running manual scan.' )

		self.InitControl( )
		self.ShowDescription( self.getFocusId( ) )
		self.mInitialized = True

		
	def onAction( self, aAction ):

		actionId = aAction.getId( )
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
			


	def onClick( self, aControlId ):
		if aControlId == E_Input01 + 1 :
			self.ResetAllControl( )
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_AUTOMATIC_SCAN )
			
		elif aControlId == E_Input02 + 1 :
			self.ResetAllControl( )
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_MANUAL_SCAN )
			

	def onFocus( self, aControlId ):
		if self.mInitialized == False :
			return

		if ( self.mLastFocused != aControlId ) :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId
