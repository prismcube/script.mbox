from pvr.gui.WindowImport import *


E_BUTTON_OK		= 301
E_HEADER		= 100
E_BODY_LABEL	= 200

TIME_OUT		= 60


class DialogAutoPowerDown( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mTitle		= ''
		self.mCtrlLabel = None
		self.mThread	= None
		self.mEnableLocalThread = True


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mEventBus.Register( self )

		self.mCtrlLabel = self.getControl( E_BODY_LABEL )
		self.getControl( E_HEADER ).setLabel( MR_LANG( 'Attention' ) )
		self.mCtrlLabel.setLabel( MR_LANG( 'Automatic power down after %s sec' ) % TIME_OUT )
		self.mEnableLocalThread = True
		self.mThread = self.AsyncShowTime( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.Close( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_PARENT_DIR :
			pass


	def onClick( self, aControlId ) :
		pass

		
	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		if xbmcgui.getCurrentWindowDialogId( ) == self.mWinId :
			if aEvent.getName( ) == ElisEventPowerSaveEnd.getName( ) :
				xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )


	@RunThread
	def AsyncShowTime( self ) :
		for i in range( TIME_OUT ) :
			time.sleep( 1 )
			if self.mEnableLocalThread == False :
				return
			self.mCtrlLabel.setLabel( MR_LANG( 'Automatic power down after %s sec' ) % ( TIME_OUT - i ) )

		#self.mCommander.System_Shutdown( )
				

	def Close( self ) :
		if self.mThread and self.mEnableLocalThread == True :
			self.mEnableLocalThread = False				
			self.mThread.join( )
		self.mEventBus.Deregister( self )
		self.CloseDialog( )