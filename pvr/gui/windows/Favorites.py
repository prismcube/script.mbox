from pvr.gui.WindowImport import *
import sys
import os

E_FAVORITES_BASE_ID = WinMgr.WIN_ID_FAVORITES * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID

XBMC_WINDOW_DIALOG_FAVOURITES		= 10134
E_TIMEOUT_INTERVAL					= 0.5


class Favorites( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mCheckTimer = None

	def onInit( self ) :
		self.SetActivate( True )

		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.SetFrontdisplayMessage( MR_LANG('Favorites') )
		xbmc.executebuiltin( "ActivateWindow(favourites)" )
		#Wait for favorites dialog activate
		for loop in range( 25 ) :
			dialogID = xbmcgui.getCurrentWindowDialogId( )
			if dialogID == XBMC_WINDOW_DIALOG_FAVOURITES :
				LOG_TRACE( 'FAV TEST loop=%d' %loop )
				break
			time.sleep( 0.2 )

		self.RestartCheckTimer( )

	
	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return

		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.StopCheckTimer( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MAINMENU )


	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return

	def RestartCheckTimer( self, aTimeout=E_TIMEOUT_INTERVAL ) :
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Restart' )
		self.StopCheckTimer( )
		self.StartCheckTimer( )


	def StartCheckTimer( self, aTimeout=E_TIMEOUT_INTERVAL ) :
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Start' )	
		self.mCheckTimer = threading.Timer( aTimeout, self.AsyncCheckTimer )
		self.mCheckTimer.start( )
	

	def StopCheckTimer( self ) :
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Stop' )	
		if self.mCheckTimer and self.mCheckTimer.isAlive( ) :
			self.mCheckTimer.cancel( )
			del self.mCheckTimer
			
		self.mCheckTimer = None


	def AsyncCheckTimer( self ) :	
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Async' )	
		if self.mCheckTimer == None :
			LOG_WARN( 'EPG update timer expired' )
			return

		currentID = xbmcgui.getCurrentWindowId( )
		if currentID == self.mWinId :
			dialogID = xbmcgui.getCurrentWindowDialogId( )
			#remove because of hangup when radio addon file is favorite 
			"""
			if dialogID == XBMC_WINDOW_DIALOG_INVALID :
				LOG_TRACE( 'FAV TEST break' )
				self.mCheckTimer = None
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MAINMENU )
				return
			"""
		else : # go to MediaWindows
			self.SetFrontdisplayMessage( MR_LANG('Media Center') )		
			self.StopCheckTimer( )
			return

		self.RestartCheckTimer( )


