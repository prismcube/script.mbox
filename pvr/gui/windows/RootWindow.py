from pvr.gui.WindowImport import *



#class RootWindow( BaseWindow ) :
class RootWindow( xbmcgui.WindowXML ) :
	def __init__( self, *args, **kwargs ) :
		if E_SUPPORT_SINGLE_WINDOW_MODE == True :
			xbmcgui.WindowXML.__init__( self, *args, **kwargs )
			self.mInitialized = False
			self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
			self.mEventBus = pvr.ElisMgr.GetInstance( ).GetEventBus( )
			self.mDataCache = pvr.DataCacheMgr.GetInstance( )
			self.mPlatform = pvr.Platform.GetPlatform( )
		else :
			BaseWindow.__init__( self, *args, **kwargs )		


	def onInit( self ) :
		#self.mWinId = xbmcgui.getCurrentWindowId( )

		LOG_TRACE('LAEL98 TEST self.mInitialized' )
		print 'self.mInitialized=%s' %self.mInitialized
		try :
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				self.CheckFirstRun( )
				if E_SUPPROT_HBBTV == True :
					self.mCommander.AppHBBTV_Ready( 0 )
				self.mInitialized = True

				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

			else :
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
						
					else :
						if self.mPlatform.GetXBMCVersion( ) < self.mPlatform.GetFrodoVersion( ) :
							WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).GetLastWindowID( ) ).doModal( )
						else :
							WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).GetLastWindowID( ) ).show( )
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def onAction( self, aAction ) :
		LOG_TRACE( '=========== ROOT ============= action=%d' %aAction.getId( ) )
		LOG_TRACE( '=========== ROOT ============= getfocus=%d' %self.getFocusId( ) )		

		if E_SUPPORT_SINGLE_WINDOW_MODE == True :
			LOG_TRACE( 'CurrentWindowID=%d focus=%d' %( WinMgr.GetInstance( ).GetLastWindowID(), self.getFocusId( ) ) )
			WinMgr.GetInstance( ).GetCurrentWindow( ).onAction( aAction )

		else :
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
		if E_SUPPORT_SINGLE_WINDOW_MODE == True :
			WinMgr.GetInstance( ).GetCurrentWindow( ).onClick( aControlId )				
		
 
	def onFocus( self, aControlId ) :
		#LOG_TRACE( '------------------------------###############################------------------------------ focus=%d' %aControlId )
		if E_SUPPORT_SINGLE_WINDOW_MODE == True :		
			#LOG_TRACE( 'CurrentWindowID=%d focus=%d' %( WinMgr.GetInstance( ).GetLastWindowID(), self.getFocusId( ) ) )		
			WinMgr.GetInstance( ).GetCurrentWindow( ).onFocus( aControlId )
		

	def CheckFirstRun( self ) :
		if CheckDirectory( '/tmp/isrunning' ) :
			self.mCommander.AppMediaPlayer_Control( 0 )
			iChannel = self.mDataCache.Channel_GetCurrent( )
			if iChannel :
				self.mDataCache.Channel_InvalidateCurrent( )
				self.mDataCache.Channel_SetCurrentSync( iChannel.mNumber, iChannel.mServiceType )

			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).UpdateVolume( )
			else :
				self.UpdateVolume( )

			pvr.gui.WindowMgr.GetInstance( ).CheckGUISettings( )
			self.mDataCache.SetMediaCenter( False )
		else :
			os.system( 'touch /tmp/isrunning' )

