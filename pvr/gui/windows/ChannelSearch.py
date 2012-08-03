from pvr.gui.WindowImport import *


class ChannelSearch( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		self.SetSettingWindowLabel( 'Channel Scan' )

		self.SetPipScreen( )
		self.LoadNoSignalState( )

		self.AddInputControl( E_Input01, 'Automatic Scan', '', 'Running automatic scan.' )
		self.AddInputControl( E_Input02, 'Manual Scan', '', 'Running manual scan.' )

		self.InitControl( )
		self.mInitialized = True
		self.SetFocusControl( E_Input01 )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.ResetAllControl( )
			self.SetVideoRestore( )
			WinMgr.GetInstance().CloseWindow( )			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			self.SetVideoRestore( )
			WinMgr.GetInstance().CloseWindow( )

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
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_AUTOMATIC_SCAN )
			
		elif groupId == E_Input02 :
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MANUAL_SCAN )
				

	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return

		if self.mLastFocused != aControlId :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId
