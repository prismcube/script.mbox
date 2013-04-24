from pvr.gui.WindowImport import *
from pvr.gui.FTIWindow import FTIWindow


E_ZOOM_BASE_ID				= WinMgr.WIN_ID_ZOOM * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID
E_LABEL_ID_1				= 100 + E_ZOOM_BASE_ID
E_LABEL_ID_2				= 101 + E_ZOOM_BASE_ID
E_LABEL_ID_3				= 102 + E_ZOOM_BASE_ID
E_LABEL_ID_4				= 103 + E_ZOOM_BASE_ID


class Zoom( FTIWindow ) :
	def __init__( self, *args, **kwargs ) :
		FTIWindow.__init__( self, *args, **kwargs )


	def onInit( self ) :
		self.SetActivate( True )
		self.SetSingleWindowPosition( E_ZOOM_BASE_ID )
		self.getControl( E_LABEL_ID_1 ).setLabel( MR_LANG( 'Left : previous step' ) )
		self.getControl( E_LABEL_ID_2 ).setLabel( MR_LANG( 'Left : previous step' ) )
		self.getControl( E_LABEL_ID_3 ).setLabel( MR_LANG( 'Left : previous step' ) )
		self.getControl( E_LABEL_ID_4 ).setLabel( MR_LANG( 'Left : previous step' ) )
		self.mInitialized = True


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False :
			return

		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Exit installation' ), MR_LANG( 'Are you sure you want to quit the first installation?' ), True )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.SetFTIStep( E_STEP_SELECT_LANGUAGE )
				self.SetParentID( WinMgr.WIN_ID_MAINMENU )
				self.SetVideoRestore( )
				WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_MBOX_REWIND :
			self.SetFTIStep( E_STEP_VIDEO_AUDIO )
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_MBOX_FF :
			self.SetFTIStep( E_STEP_ANTENNA )
			WinMgr.GetInstance( ).CloseWindow( )


	def onClick( self, aControlId ) :
		pass


	def onFocus( self, aControlId ) :
		pass

