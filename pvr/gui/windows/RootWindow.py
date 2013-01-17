from pvr.gui.WindowImport import *


class RootWindow( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		

	def onInit( self ) :
		#self.mWinId = xbmcgui.getCurrentWindowId( )
		#self.mWin = xbmcgui.Window( self.mWinId )

		LOG_TRACE('LAEL98 TEST self.mInitialized' )
		print 'self.mInitialized=%s' %self.mInitialized
		if self.mInitialized == False :
			if E_SUPPROT_HBBTV == True :
				self.mCommander.AppHBBTV_Ready( 0 )
			self.mInitialized = True
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).doModal( )
			
			"""
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )
			WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).mLastId ).doModal( )
			"""

		else :
			WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).GetLastWindowID( ) ).doModal( )

		
	def onAction( self, aAction ) :
		LOG_TRACE( 'RealyAction TEST action=%d' %aAction.getId() )

		relayAction = RelayAction( aAction.getId() )
		WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).GetLastWindowID( ) ).SetRelayAction( relayAction )


		"""
		actionId = aAction.getId( )
		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR:
			LOG_ERR( '------------- Root Window -------------' )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
		"""
			
				
	def onClick( self, aControlId ) :
		LOG_TRACE( '' )	
		
 
	def onFocus( self, aControlId ) :
		LOG_TRACE( '' )

