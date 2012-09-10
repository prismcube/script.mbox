from pvr.gui.WindowImport import *


class ChannelSearch( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mIsCloseing = False
		self.mNoChannel = False


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		self.SetSettingWindowLabel( MR_LANG( 'Channel Search' ) )

		self.SetPipScreen( )
		self.LoadNoSignalState( )

		self.AddInputControl( E_Input01, MR_LANG( 'Automatic Scan' ), '', MR_LANG( 'Search TV & Radio channels without entering any satellite information' ) )
		self.AddInputControl( E_Input02, MR_LANG( 'Manual Scan' ), '', MR_LANG( 'Scan channels on specific transponder by setting frequency, symbol rate, polarization, etc' ) )

		self.InitControl( )
		self.SetFocusControl( E_Input01 )

		if self.mIsCloseing == False :
			if self.CheckNoChannel( ) :
				self.mNoChannel = True
			else :
				self.mNoChannel = False
		else :
			if self.mNoChannel == False :
				if self.CheckNoChannel( ) :
					self.mDataCache.Channel_TuneDefault( )
					self.mDataCache.Player_AVBlank( False )
					self.mNoChannel = False
				else :
					self.mDataCache.Player_AVBlank( True )
		
		self.mInitialized = True


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.mIsCloseing = False
			self.ResetAllControl( )
			self.SetVideoRestore( )
			WinMgr.GetInstance( ).CloseWindow( )			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mIsCloseing = False
			self.ResetAllControl( )
			self.SetVideoRestore( )
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )				

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )


	def onClick( self, aControlId ) :
		groupId = self.GetGroupId( aControlId )
		if groupId == E_Input01 :
			self.mIsCloseing = True
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_AUTOMATIC_SCAN )
			
		elif groupId == E_Input02 :
			self.mIsCloseing = True
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MANUAL_SCAN )
				

	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return

		if self.mLastFocused != aControlId :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId


	def CheckNoChannel( self ) :
		if self.mDataCache.Channel_GetList( ) :
			return True
		else :
			return False