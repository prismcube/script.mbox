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
		self.leftGroupItems = [ 'Weather', 'Picture', 'Music', 'Video', 'Programs', 'Settings', 'File Manager', 'Profiles', 'System Info' ]
		self.descriptionList	 = [ 'Desc Weather', 'Desc Picture', 'Desc Music', 'Desc Video', 'Desc Programs', 'Desc Settings', 'Desc File Manager', 'Desc Profiles', 'Desc System Info' ]
		self.icon = [ 'special://skin/backgrounds/appearance.jpg', 'special://skin/backgrounds/videos.jpg', 'special://skin/backgrounds/music.jpg', 'special://skin/backgrounds/pictures.jpg', 'special://skin/backgrounds/weather.jpg', 'special://skin/backgrounds/addons.jpg', 'special://skin/backgrounds/network.jpg', 'special://skin/backgrounds/network.jpg', 'special://skin/backgrounds/network.jpg' ]

		self.mCtrlLeftGroup = 0


	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId )

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( 'Media Center' )

		groupItems = []
		
		for i in range( len( self.leftGroupItems ) ) :
			groupItems.append( xbmcgui.ListItem( self.leftGroupItems[i], self.descriptionList[i], self.icon[i] ) )
			
		self.mCtrlLeftGroup = self.getControl( LEFT_MENU_ID )
		self.mCtrlLeftGroup.addItems( groupItems )

		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.close( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.close( )


	def onClick( self, aControlId ) :
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )

		if selectedId == MENU_ID_WEATHER :
			xbmc.executebuiltin( 'ActivateWindow(Weather)' )

		elif selectedId == MENU_ID_PICTURE :
			xbmc.executebuiltin( 'ActivateWindow(Pictures)' )

		elif selectedId == MENU_ID_MUSIC :
			xbmc.executebuiltin( 'ActivateWindow(Music)' )

		elif selectedId == MENU_ID_VIDEO :
			xbmc.executebuiltin( 'ActivateWindow(Videos)' )
			
		elif selectedId == MENU_ID_PROGRAMS :
			xbmc.executebuiltin( 'ActivateWindow(Programs,Addons,return)' )

		elif selectedId == MENU_ID_SETTINGS :
			xbmc.executebuiltin( 'ActivateWindow(Settings)' )

		elif selectedId == MENU_ID_FILEMANEGER :
			xbmc.executebuiltin( 'ActivateWindow(FileManager)' )

		elif selectedId == MENU_ID_PROFILES :
			xbmc.executebuiltin( 'ActivateWindow(Profiles)' )

		elif selectedId == MENU_ID_SYSTEMINFO :
			xbmc.executebuiltin( 'ActivateWindow(SystemInfo)' )
 
	def onFocus( self, aControlId ):
		pass
