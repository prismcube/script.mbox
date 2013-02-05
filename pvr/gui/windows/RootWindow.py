from pvr.gui.WindowImport import *


class RootWindow( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		

	def onInit( self ) :
		#self.mWinId = xbmcgui.getCurrentWindowId( )

		LOG_TRACE('LAEL98 TEST self.mInitialized' )
		print 'self.mInitialized=%s' %self.mInitialized
		if E_WINDOW_ATIVATE_MODE == E_MODE_DOMODAL :
			if self.mInitialized == False :
				self.CheckFirstRun( )
				if E_SUPPROT_HBBTV == True :
					self.mCommander.AppHBBTV_Ready( 0 )
				self.mInitialized = True
				WinMgr.GetInstance( ).mLastId =  WinMgr.WIN_ID_NULLWINDOW
				xbmc.executebuiltin('xbmc.Action(dvbres21)')

		else :
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

		if E_WINDOW_ATIVATE_MODE == E_MODE_DOMODAL :

			if aAction.getId() == Action.ACTION_MBOX_RESERVED21 :
				print 'action show gui : domodal new window'
				if self.mInitialized == False :
					pass
				else :
					print '>>>>>>now domodal'
					WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).GetLastWindowID( ) ).doModal( )
					print '<<<<<<now domodal out'


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

