from pvr.gui.WindowImport import *


E_BUTTON_OK		= 301
E_HEADER		= 100
E_BODY_LABEL	= 200

TIME_OUT		= 20


class DialogAutoPowerDown( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mTitle		= ''
		self.mCtrlLabel = None
		self.mThread	= None


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mEventBus.Register( self )

		self.mCtrlLabel = self.getControl( E_BODY_LABEL )
		self.getControl( E_HEADER ).setLabel( MR_LANG( 'Warning' ) )
		self.mCtrlLabel.setLabel( MR_LANG( 'Automatic power down after %s sec' ) % TIME_OUT )
		self.mThread = threading.Timer( 0.3, self.AsyncShowTime )
		self.mThread.start( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.Close( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_PARENT_DIR :
			self.Close( )


	def onClick( self, aControlId ) :
		if aControlId == E_BUTTON_OK :
			self.Close( )

		
	def onFocus( self, aControlId ) :
		pass


	@GuiLock
	def onEvent( self, aEvent ) :
		if xbmcgui.getCurrentWindowDialogId( ) == self.mWinId :
			pass
			#if aEvent.getName( ) == ElisEventScanAddChannel.getName( ) :
			#	self.UpdateAddChannel( aEvent )


	def AsyncShowTime( self ) :
		for i in range( TIME_OUT ) :
			if self.mThread == None :
				return
			self.mCtrlLabel.setLabel( MR_LANG( 'Automatic power down after %s sec' ) % ( TIME_OUT - i ) )
			time.sleep( 1 )

		#self.mCommander.System_Shutdown( )
				

	def Close( self ) :
		if self.mThread and self.mThread.isAlive( ) :
			self.mThread.cancel( )
			self.mThread = None
		self.mEventBus.Deregister( self )
		self.CloseDialog( )