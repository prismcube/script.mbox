from pvr.gui.WindowImport import *
from pvr.gui.FTIWindow import FTIWindow
from pvr.XBMCInterface import XBMC_SetSkinZoom


E_ZOOM_BASE_ID				= WinMgr.WIN_ID_ZOOM * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID
E_LABEL_ID_1				= 100 + E_ZOOM_BASE_ID
E_LABEL_ID_2				= 101 + E_ZOOM_BASE_ID


class Zoom( FTIWindow ) :
	def __init__( self, *args, **kwargs ) :
		FTIWindow.__init__( self, *args, **kwargs )
		self.mZoom = XBMC_GetSkinZoom( )


	def onInit( self ) :
		self.SetActivate( True )
		self.SetSingleWindowPosition( E_ZOOM_BASE_ID )
		self.mZoom = int ( XBMC_GetSkinZoom( ) )
		self.getControl( E_LABEL_ID_1 ).setLabel( MR_LANG( 'Remote control up button : Zoom in, Remote control down button : Zoom out ( Current rate : %s )' ) % self.mZoom )
		self.getControl( E_LABEL_ID_2 ).setLabel( MR_LANG( 'Remote control left button : Previous step, Right button : Next step' ) )
		self.mDataCache.Player_VideoBlank( True )
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
				self.Close( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.SetFTIStep( E_STEP_VIDEO_AUDIO )
			self.Close( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.SetFTIStep( E_STEP_ANTENNA )
			self.Close( )

		elif actionId == Action.ACTION_MOVE_UP :
			if self.mZoom == 20 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'You have reached the maximum rate' ) )
	 			dialog.doModal( )
			else :
				self.mZoom += 1

			self.getControl( E_LABEL_ID_1 ).setLabel( MR_LANG( 'Remote control up button : Zoom in, Remote control down button : Zoom out ( Current rate : %s )' ) % self.mZoom )
			XBMC_SetSkinZoom( self.mZoom )

		elif actionId == Action.ACTION_MOVE_DOWN :
			if self.mZoom == -20 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'You have reached the minimum rate' ) )
	 			dialog.doModal( )
			else :
				self.mZoom -= 1

			self.getControl( E_LABEL_ID_1 ).setLabel( MR_LANG( 'Remote control up button : Zoom in, Remote control down button : Zoom out ( Current rate : %s )' ) % self.mZoom )
			XBMC_SetSkinZoom( self.mZoom )


	def onClick( self, aControlId ) :
		pass


	def onFocus( self, aControlId ) :
		pass


	def Close( self ) :
		WinMgr.GetInstance( ).LoadSkinPosition( )
		self.mDataCache.Player_VideoBlank( False )
		WinMgr.GetInstance( ).CloseWindow( )

