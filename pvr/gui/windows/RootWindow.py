from pvr.gui.WindowImport import *


class RootWindow( BaseWindow ):
	def __init__( self, *args, **kwargs ):
		BaseWindow.__init__( self, *args, **kwargs )
		self.mNextCommand = 0

	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		LOG_TRACE(' NextCommnad=%d' %( self.mNextCommand ) )
		if self.mInitialized == False :
			self.mInitialized = True
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE, WinMgr.WIN_ID_NULLWINDOW )

		elif self.mNextCommand == WinMgr.E_SKIN_CHECK_COMMAND :
			WinMgr.GetInstance( ).ShowWindow( defaultWindow, parentWindow )			
			
			
		LOG_ERR( 'MediaCenter Nav TEST' )
		
	def onAction( self, aAction ) :
		LOG_TRACE('')
		actionId = aAction.getId( )
		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR:
			LOG_ERR( '------------- Root Window -------------' )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
			
				
	def onClick( self, aControlId ):
		LOG_TRACE('')
		pass
		
 
	def onFocus( self, aControlId ):
		LOG_TRACE('')
		pass

	def SetNextCommand( self, aCommand) :
		self.mNextCommand = aCommand

