from pvr.gui.WindowImport import *


class RootWindow( xbmcgui.WindowXML ) :
	def __init__( self, *args, **kwargs ) :
		xbmcgui.WindowXML.__init__( self, *args, **kwargs )
		self.mInitialized = False
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.mEventBus = pvr.ElisMgr.GetInstance( ).GetEventBus( )
		self.mDataCache = pvr.DataCacheMgr.GetInstance( )
		self.mPlatform = pvr.Platform.GetPlatform( )
		self.mReloadControls = False


	def onInit( self ) :
		LOG_TRACE('LAEL98 TEST self.mInitialized' )
		print 'self.mInitialized=%s' %self.mInitialized

		try :
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				if self.mInitialized == False :
					self.CheckFirstRun( )
					self.LoadTimeShiftControl( )
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_EPG_WINDOW ).LoadEPGControls( )					
					if E_SUPPROT_HBBTV == True :
						self.mCommander.AppHBBTV_Ready( 0 )
					self.mInitialized = True
					self.LoadNoSignalState( )
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

				else :
					LOG_TRACE( "Reload Test")
					if self.mReloadControls == True :
						LOG_TRACE( "Reload Test")					
						self.mReloadControls = False
						self.LoadTimeShiftControl( )
						WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_EPG_WINDOW ).LoadEPGControls( )
					
					LOG_TRACE( 'WinMgr.GetInstance( ).GetLastWindowID( )=%d' %WinMgr.GetInstance( ).GetLastWindowID( ) )
					lastWindow = WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).GetLastWindowID( ) )
					LOG_TRACE( 'lastWindow.GetParentID( )=%d' %lastWindow.GetParentID( ) )
					WinMgr.GetInstance( ).ShowWindow( WinMgr.GetInstance( ).GetLastWindowID( ), lastWindow.GetParentID( ) )

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
		#LOG_TRACE( '=========== ROOT ============= action=%d' %aAction.getId( ) )
		#LOG_TRACE( '=========== ROOT ============= getfocus=%d' %self.getFocusId( ) )

		if E_SUPPORT_SINGLE_WINDOW_MODE == True :
			#LOG_TRACE( 'CurrentWindowID=%d focus=%d' %( WinMgr.GetInstance( ).GetLastWindowID(), self.getFocusId( ) ) )
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
						xbmc.executebuiltin('xbmc.Action(dvbres21)')

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
		if CheckDirectory( '/mtmp/isrunning' ) :
			self.mCommander.AppMediaPlayer_Control( 0 )
			iChannel = self.mDataCache.Channel_GetCurrent( )
			if iChannel :
				self.mDataCache.Channel_InvalidateCurrent( )
				self.mDataCache.Channel_SetCurrentSync( iChannel.mNumber, iChannel.mServiceType )

			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).UpdateVolume( )

			pvr.gui.WindowMgr.GetInstance( ).CheckGUISettings( )
			self.mDataCache.SetMediaCenter( False )
		else :
			os.system( 'touch /mtmp/isrunning' )


	def LoadTimeShiftControl( self ) :
		mBookmarkButton = []
		buttonId = WinMgr.WIN_ID_TIMESHIFT_PLATE * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID + 600
		for i in range( 100 ) :
			mBookmarkButton.append( self.getControl( buttonId + i ) )
			mBookmarkButton[i].setVisible( False )

		self.mDataCache.SetBookmarkButton( mBookmarkButton )


	def LoadNoSignalState( self ) :
		if self.mDataCache.GetLockedState( ) == ElisEnum.E_CC_FAILED_SCRAMBLED_CHANNEL :
			self.setProperty( 'Signal', 'Scramble' )
		elif self.mDataCache.GetLockedState( ) == ElisEnum.E_CC_FAILED_NO_SIGNAL :
			self.setProperty( 'Signal', 'False' )
		else :
			self.setProperty( 'Signal', 'True' )
