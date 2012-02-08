import xbmc
import xbmcgui
import sys
import time

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.BaseWindow import BaseWindow, Action
from pvr.Util import GuiLock, LOG_TRACE


class DummyWindow( BaseWindow ):
	def __init__( self, *args, **kwargs ):
		BaseWindow.__init__( self, *args, **kwargs )


	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId )

	def onAction( self, aAction ) :
		id = aAction.getId( )
		focusId = self.getFocusId( )

		if id == Action.ACTION_PREVIOUS_MENU:
			self.close()


	def onClick( self, aControlId ):
		LOG_TRACE('')
		
 
	def onFocus( self, aControlId ):
		LOG_TRACE('')
