from pvr.gui.WindowImport import *


class RootWindow( BaseWindow ):
	def __init__( self, *args, **kwargs ):
		BaseWindow.__init__( self, *args, **kwargs )

		self.mInitialized = False

	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		if self.mInitialized == False :
			if E_SUPPROT_HBBTV == True :
				self.mCommander.AppHBBTV_Ready( 0 )
			self.SendLocalOffsetToXBMC( )
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )
			WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).mLastId ).doModal()
			self.mInitialized = True
			self.mEventBus.Register( self )			
		else :
			WinMgr.GetInstance( ).GetWindow(WinMgr.GetInstance( ).mLastId).doModal( )

		
	def onAction( self, aAction ) :
		pass
		"""
		actionId = aAction.getId( )
		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR:
			LOG_ERR( '------------- Root Window -------------' )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
		"""
			
				
	def onClick( self, aControlId ):
		pass
		
 
	def onFocus( self, aControlId ):
		LOG_TRACE('')
		pass

	def onEvent(self, aEvent):
		if aEvent.getName() == ElisEventTimeReceived.getName( ) :
			self.SendLocalOffsetToXBMC( )


	def SendLocalOffsetToXBMC( self ) :
		LOG_TRACE( '--------------' )
		if WinMgr.E_ADD_XBMC_HTTP_FUNCTION == True :
			localOffset = self.mDataCache.Datetime_GetLocalOffset( )
			xbmc.executehttpapi( 'setlocaloffset(%d)' %localOffset )

		LOG_TRACE( '--------------' )

