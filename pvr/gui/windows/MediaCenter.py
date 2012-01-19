import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
from pvr.gui.BaseWindow import BaseWindow, Action
from pvr.gui.GuiConfig import *

BUTTON_ID_WEATHER				= 90101
BUTTON_ID_PICTURE				= 90102
BUTTON_ID_MUSIC					= 90103
BUTTON_ID_VIDEO					= 90104
BUTTON_ID_PROGRAMS				= 90105
BUTTON_ID_SETTINGS				= 90106
BUTTON_ID_FILEMANEGER			= 90107
BUTTON_ID_PROFILES				= 90108
BUTTON_ID_SYSTEMINFO			= 90109

class MediaCenter( BaseWindow ):
	def __init__( self, *args, **kwargs ):
		BaseWindow.__init__( self, *args, **kwargs )


	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId )

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( 'Media Center' )

		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.close( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.close( )


	def onClick( self, aControlId ) :
		pass

 
	def onFocus( self, aControlId ):
		pass
