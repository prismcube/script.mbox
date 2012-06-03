from pvr.gui.WindowImport import *


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

class MediaCenter( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( 'Media Center' )

		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.SetVideoRestore( )
			WinMgr.GetInstance().CloseWindow( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			self.SetVideoRestore( )
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.SetVideoRestore( )
			WinMgr.GetInstance().CloseWindow( )


	def onClick( self, aControlId ) :
		pass
		
 
	def onFocus( self, aControlId ) :
		pass
