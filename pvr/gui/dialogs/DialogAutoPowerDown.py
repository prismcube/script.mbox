from pvr.gui.WindowImport import *


E_HEADER		= 100
E_BODY_LABEL	= 200

TIME_OUT		= 60


class DialogAutoPowerDown( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mTitle					= ''
		self.mCtrlLabel 			= None
		self.mThread				= None
		self.mEnableLocalThread 	= False


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.mEventBus.Register( self )

		self.mCtrlLabel = self.getControl( E_BODY_LABEL )
		self.getControl( E_HEADER ).setLabel( MR_LANG( 'Automatic Power Down' ) )
		self.mCtrlLabel.setLabel( MR_LANG( 'Start automatic power down after %s sec' ) % TIME_OUT )
		self.mEnableLocalThread = True
		self.mThread = self.AsyncShowTime( )


	def onAction( self, aAction ) :
		pass


	def onClick( self, aControlId ) :
		pass

		
	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		if xbmcgui.getCurrentWindowDialogId( ) == self.mWinId :
			if aEvent.getName( ) == ElisEventPowerSaveEnd.getName( ) :
				thread = threading.Timer( 0.5, self.Close )
				thread.start( )


	@RunThread
	def AsyncShowTime( self ) :
		for i in range( TIME_OUT ) :
			time.sleep( 1 )
			if self.mEnableLocalThread == False :
				return
			self.mCtrlLabel.setLabel( MR_LANG( 'Start automatic power down after %s sec' ) % ( TIME_OUT - i ) )

		self.mDataCache.System_Shutdown( )
		thread = threading.Timer( 0.5, self.Close )
		thread.start( )
				

	def Close( self ) :
		if self.mThread and self.mEnableLocalThread == True :
			self.mEnableLocalThread = False
			self.mThread.join( )
		self.mEventBus.Deregister( self )
		self.CloseDialog( )
