from pvr.gui.WindowImport import *

class SystemUpdate( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mIsCloseing = False
		self.mNoChannel = False


	def onInit( self )  :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.SetSettingWindowLabel( MR_LANG( 'Update' ) )

		self.SetPipScreen( )
		self.LoadNoSignalState( )

		IsState = self.Provisioning( )
		self.AddInputControl( E_Input01, MR_LANG( 'System Update' ), IsState, MR_LANG( 'System, OS, MBox Update' ) )

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
			self.Close( )
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mIsCloseing = False
			self.ResetAllControl( )
			self.SetVideoRestore( )
			self.Close( )

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
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'TEST Server check' ) )
 			dialog.doModal( )
			
		elif groupId == E_Input02 :
			self.mIsCloseing = True
			self.ResetAllControl( )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'TEST Server check' ) )
 			dialog.doModal( )


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


	def Provisioning( self ) :
		#ToDO, received rss data

		download = GetURLpage( 'http://192.168.100.142/RSS/update.xml' )
		LOG_TRACE( '%s'% download )

		soup, nodes = parseStringInXML( download, 'filename' )
		filename = os.path.basename( nodes[0] )
		name = os.path.splitext( filename )
		print filename, name

		soup, nodes = parseStringInXML( download, 'description' )
		for item in nodes :
			print item


		ret = MR_LANG( 'No one' )
		return ret



	def Close( self ) :
		WinMgr.GetInstance( ).CloseWindow( )



