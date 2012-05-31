from pvr.gui.WindowImport import *


class RootWindow( BaseWindow ):
	def __init__( self, *args, **kwargs ):
		BaseWindow.__init__( self, *args, **kwargs )


	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		LOG_TRACE('')
		WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )		


	def onAction( self, aAction ) :
		LOG_TRACE('')
		id = aAction.getId( )
		focusId = self.getFocusId( )
		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR:
			LOG_ERR( '------------- Root Window -------------' )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
			
				
	def onClick( self, aControlId ):
		LOG_TRACE('')
		pass
		
 
	def onFocus( self, aControlId ):
		LOG_TRACE('')
		pass

