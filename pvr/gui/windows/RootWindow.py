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
			self.CheckFirstRun( )
			if E_SUPPROT_HBBTV == True :
				self.mCommander.AppHBBTV_Ready( 0 )
			self.mInitialized = True
			if self.mPlatform.GetXBMCVersion( ) < self.mPlatform.GetFrodoVersion( ) :
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).doModal( )
			else :
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).show( )
			
			"""
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )
			WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).mLastId ).doModal( )
			"""

		else :
			if self.mPlatform.GetXBMCVersion( ) < self.mPlatform.GetFrodoVersion( ) :
				WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).GetLastWindowID( ) ).doModal( )
			else :
				WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).GetLastWindowID( ) ).show( )


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


	def CheckFirstRun( self ) :
		if CheckDirectory( '/tmp/isrunning' ) :
			self.mCommander.AppMediaPlayer_Control( 0 )
			iChannel = self.mDataCache.Channel_GetCurrent( )
			if iChannel :
				self.mDataCache.Channel_InvalidateCurrent( )
				self.mDataCache.Channel_SetCurrentSync( iChannel.mNumber, iChannel.mServiceType )

			self.UpdateVolume( )
			pvr.gui.WindowMgr.GetInstance( ).CheckGUISettings( )
			self.mDataCache.SetMediaCenter( False )
		else :
			os.system( 'touch /tmp/isrunning' )

