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
		self.SetActivate( True )

		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		#self.getControl( E_SETTING_MINI_TITLE ).setLabel( MR_LANG( 'Media Center' ) )
		#LOG_TRACE( '--------------flag[%s]'% self.mDataCache.GetMediaCenter( ) )


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			xbmc.executebuiltin( 'PlayerControl(Stop)' )
			WinMgr.GetInstance( ).CloseWindow( )


	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return

 
	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return


