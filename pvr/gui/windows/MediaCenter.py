import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
from pvr.gui.BaseWindow import BaseWindow, Action
from pvr.gui.GuiConfig import *

MENU_ID_WEATHER					= 0
MENU_ID_PICTURE					= 1
MENU_ID_MUSIC					= 2
MENU_ID_VIDEO					= 3
MENU_ID_PROGRAMS				= 4
MENU_ID_SETTINGS				= 5
MENU_ID_FILEMANEGER				= 6
MENU_ID_PROFILES				= 7
MENU_ID_SYSTEMINFO				= 8

LEFT_MENU_ID = 9000

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
