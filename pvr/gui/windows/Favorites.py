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
		self.mIsPlaying = False

	def onInit( self ) :
		self.setProperty( 'SetBackgroundColor', '%s' %int( 0x2f2f2f ) )	
		self.mIsPlaying = False
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
		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.StopCheckTimer( )
			self.setProperty( 'SetBackgroundColor', '%s' %int( 0xffffff ) )	
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MAINMENU )


	def onClick( self, aControlId ) :
		pass


	def onFocus( self, aControlId ) :
		pass


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

		count = 0

		xbmcgui.getCurrentWindowId( )		
		if currentID == self.mWinId :
			dialogID = xbmcgui.getCurrentWindowDialogId( )
			#Removed because hangup occurs when radio addon file in favorite
			isPlaying = xbmc.Player().isPlaying()
			LOG_TRACE( 'LAEL98 TEST is plalying=%s' %isPlaying )
			if dialogID == XBMC_WINDOW_DIALOG_INVALID and isPlaying == False :

				if self.mIsPlaying == True :
					self.SetFrontdisplayMessage( MR_LANG('Favorites') )
					xbmc.executebuiltin( "ActivateWindow(favourites)" )
					#Wait for favorites dialog activate
					for loop in range( 25 ) :
						dialogID = xbmcgui.getCurrentWindowDialogId( )
						if dialogID == XBMC_WINDOW_DIALOG_FAVOURITES :
							break
						time.sleep( 0.2 )
				else :
					time.sleep( 0.2 )
					for i in range( 10 ) :
						dialogID = xbmcgui.getCurrentWindowDialogId( )
						isPlaying = xbmc.Player().isPlaying()						

						if dialogID == XBMC_WINDOW_DIALOG_INVALID and isPlaying == False :
							count += 1
							time.sleep( 0.2 )
						else :
							count = 0
							break

					if count >= 10 :
						self.mCheckTimer = None
						self.mIsPlaying = False
						self.setProperty( 'SetBackgroundColor', '%s' %int( 0xffffff ) )	
						WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MAINMENU )
						self.mIsPlaying = False					
						return

			self.mIsPlaying = isPlaying

		else : # go to MediaWindows
			self.SetFrontdisplayMessage( MR_LANG('Media Center') )		
			self.StopCheckTimer( )
			return

		self.RestartCheckTimer( )


