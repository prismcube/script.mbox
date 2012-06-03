from pvr.gui.WindowImport import *


class DummyWindow( BaseWindow ):
	def __init__( self, *args, **kwargs ):
		BaseWindow.__init__( self, *args, **kwargs )


	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		time.sleep( 0.5 )
		WinMgr.GetInstance().CloseWindow( )

	def onAction( self, aAction ) :
		id = aAction.getId( )
		focusId = self.getFocusId( )


	def onClick( self, aControlId ):
		LOG_TRACE('')
		pass
		
 
	def onFocus( self, aControlId ):
		LOG_TRACE('')
		pass
