from pvr.gui.WindowImport import *


class ChannelSearch( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mIsCloseing = False
		self.mNoChannel = False


	def onInit( self ) :
		self.SetActivate( True )
		self.SetFrontdisplayMessage( 'Channel Search' )		
		self.mWinId = xbmcgui.getCurrentWindowId( )

		self.SetSettingWindowLabel( MR_LANG( 'Channel Search' ) )

		self.SetPipScreen( )
		self.LoadNoSignalState( )

		self.AddInputControl( E_Input01, MR_LANG( 'Automatic scan' ), '', MR_LANG( 'Search TV and radio channels without entering any satellite information' ) )
		self.AddInputControl( E_Input02, MR_LANG( 'Manual scan' ), '', MR_LANG( 'Scan channels on specific transponder by setting frequency, symbol rate, polarization, etc' ) )

		self.InitControl( )
		self.SetFocusControl( E_Input01 )
		self.SetPipLabel( )

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

		if self.mDataCache.GetEmptySatelliteInfo( ) == True :
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( MR_LANG( 'No satellite data available' ) )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Please reset your device to factory settings' ) )
			dialog.doModal( )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Go to the configuration menu now?' ), MR_LANG( 'When you perform a factory reset,\nall your settings revert to factory defaults' ) )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.mIsCloseing = True
				self.ResetAllControl( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIGURE, WinMgr.WIN_ID_MAINMENU )
			else :
				self.mIsCloseing = True
				self.ResetAllControl( )
				WinMgr.GetInstance( ).CloseWindow( )


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.mIsCloseing = False
			self.ResetAllControl( )
			self.SetVideoRestore( )
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )				

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )


	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
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
		if self.IsActivate( ) == False  :
			return
	
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
