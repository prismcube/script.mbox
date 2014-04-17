from pvr.gui.WindowImport import *
from pvr.Util import UpdateMonthTranslation, UpdateWeekdayTranslation
from pvr.XBMCInterface import XBMC_GetCurrentLanguage
import time

class RootWindow( xbmcgui.WindowXML ) :
	def __init__( self, *args, **kwargs ) :
		xbmcgui.WindowXML.__init__( self, *args, **kwargs )
		self.mInitialized = False
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.mEventBus = pvr.ElisMgr.GetInstance( ).GetEventBus( )
		self.mDataCache = pvr.DataCacheMgr.GetInstance( )
		self.mPlatform = pvr.Platform.GetPlatform( )
		self.mWaiting = False

	def onInit( self ) :
		LOG_TRACE('LAEL98 TEST self.mInitialized' )

		UpdateMonthTranslation( )
		UpdateWeekdayTranslation( )
		self.mDataCache.SetRootWindowId( xbmcgui.getCurrentWindowId( ) )
		self.syncXBMC( )

		try :
			if E_SUPPORT_SINGLE_WINDOW_MODE == True :
				if self.mInitialized == False :
					self.CheckFirstRun( )
					self.LoadTimeShiftControl( )
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_EPG_WINDOW ).ResetControls( )
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_SIMPLE_CHANNEL_LIST ).ResetControls( )
					if E_SUPPROT_HBBTV == True :
						#self.mCommander.AppHBBTV_Ready( 1 )						
						#self.mCommander.AppHBBTV_Ready( 0 )
						self.mDataCache.Splash_StartAndStop( 0 )
					self.mInitialized = True
					self.LoadNoSignalState( )
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

				else :
					self.LoadTimeShiftControl( )
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_EPG_WINDOW ).ResetControls( )
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_SIMPLE_CHANNEL_LIST ).ResetControls( )
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
			import traceback
			LOG_ERR( 'Exception root window %s traceback = %s' % ( ex, traceback.format_exc( ) ) )


	def onAction( self, aAction ) :
		if E_SUPPORT_SINGLE_WINDOW_MODE == True :
			if WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).mHbbTVShowing == True :
				if aAction.getId( ) != Action.ACTION_PREVIOUS_MENU :
					LOG_ERR("Do nothing in HBBTV Mode");
					return
				else :
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).HbbTV_HideBrowser()
					return
			else :
				if self.mPlatform.GetProduct( ) == PRODUCT_OSCAR and aAction.getId( ) == Action.ACTION_COLOR_BLUE :
					return
				WinMgr.GetInstance( ).GetCurrentWindow( ).onAction( aAction )

		else :
			if E_WINDOW_ATIVATE_MODE == E_MODE_DOMODAL :
				if aAction.getId() == Action.ACTION_MBOX_RESERVED21 :
					if self.mInitialized == False :
						pass
					else :
						WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).GetLastWindowID( ) ).doModal( )
						xbmc.executebuiltin('xbmc.Action(dvbres21)')


	def onClick( self, aControlId ) :
		LOG_TRACE( '' )	
		if E_SUPPORT_SINGLE_WINDOW_MODE == True :
			if WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).mHbbTVShowing == True :
				LOG_ERR("Do nothing in onclick, hbbtv mode is true")
				return
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
		if self.mDataCache.GetLockedState( ) == ElisEnum.E_CC_SUCCESS :
			self.setProperty( 'Signal', 'True' )
		elif self.mDataCache.GetLockedState( ) == ElisEnum.E_CC_FAILED_SCRAMBLED_CHANNEL :
			self.setProperty( 'Signal', 'Scramble' )
		elif self.mDataCache.GetLockedState( ) == ElisEnum.E_CC_FAILED_NO_SIGNAL :
			self.setProperty( 'Signal', 'False' )
		elif self.mDataCache.GetLockedState( ) == ElisEnum.E_CC_FAILED_PROGRAM_NOT_FOUND :
			self.setProperty( 'Signal', 'NoService' )
		else :
			LOG_ERR( 'LoadNoSignalState : Unknown channel status' )


	def syncXBMC( self ) :
		xbmc.executebuiltin( 'PlayerControl(Stop)', True )
		pvr.gui.WindowMgr.GetInstance( ).CheckGUISettings( )
		InitTranslateByEnumList( )
		self.mDataCache.SyncLanguagePropFromXBMC( XBMC_GetCurrentLanguage( ) )
		if self.mDataCache.GetAlarmByViewTimer( ) :
			self.mDataCache.SetAlarmByViewTimer( False )
			mHead = MR_LANG( 'Timer Notification' )
			mLine = MR_LANG( 'Channel is changed by view timer' )
			xbmc.executebuiltin( 'Notification(%s, %s, 3000, DefaultIconInfo.png)'% ( mHead, mLine ) )

		type = self.mDataCache.Zappingmode_GetCurrent( ).mServiceType

		if type == ElisEnum.E_SERVICE_TYPE_RADIO :
			self.setProperty( 'TVRadio', 'true' )
		else :
			self.setProperty( 'TVRadio', 'false' )


	@RunThread
	def GotoNullwindow( self ) :
		curID = xbmcgui.getCurrentWindowDialogId( )
		nextID = curID
		count  = 0
		while curID != 9999 :
			xbmc.executebuiltin( 'xbmc.Action(PreviousMenu)' )
			for i in range( 50 ) : #wait 5sec
				nextID = xbmcgui.getCurrentWindowDialogId( )
				LOG_TRACE( "GotoNullwindow nextID=%d currentWidnow=%d" %(nextID,xbmcgui.getCurrentWindowId()))
				if curID != nextID :
					curID = nextID
					break
				time.sleep( 0.1 )

			count += 1
			if count > 10 : #close maximum dialogi
				break
		windowId = WinMgr.GetInstance( ).GetLastWindowID( )

		if windowId != WinMgr.WIN_ID_NULLWINDOW :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

		self.mWaiting = False

