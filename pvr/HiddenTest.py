from pvr.gui.WindowImport import *
import pvr.HiddenTestMgr as TestMgr

TEST_ZAPPING_NULL = 0
TEST_ZAPPING_EPG = 1
TEST_WINDOWS = 2

class HiddenTest( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mStopflag = True
		self.mZappingTime = 5
		self.mCtrlLabel = None

	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mCtrlLabel = self.getControl( 100 )
		self.TestFunction( )
		self.mStopflag = True

	def onAction( self, aAction ) :
		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.mStopflag = False
			self.ZappingTestNull( ).join( )
			WinMgr.GetInstance( ).CloseWindow( )
	
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mStopflag = False
			self.ZappingTestNull( ).join( )
			WinMgr.GetInstance( ).CloseWindow( )


	def onClick( self, aControlId ):
		LOG_TRACE('')
		pass
		
 
	def onFocus( self, aControlId ):
		LOG_TRACE('')
		pass


	def TestFunction( self ) :
		context = []
		context.append( ContextItem( 'Zapping Test : TestWindow', TEST_ZAPPING_NULL ) )
		context.append( ContextItem( 'Zapping Test : EPGWindow', TEST_ZAPPING_EPG ) )
		context.append( ContextItem( 'Window Moving Test', TEST_WINDOWS ) )				
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
		dialog.doModal( )
		contextAction = dialog.GetSelectedAction( )
		if contextAction < 0 :
			return
		if contextAction == TEST_ZAPPING_NULL or TEST_ZAPPING_EPG :
			self.ZappingTest( contextAction )
		elif contextAction == TEST_WINDOWS :
			pass


	def ZappingTest( self , aType ) :
		if self.mDataCache.Channel_GetList( ) :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( 'Zapping Time', '%d' % self.mZappingTime, 2 )
 			dialog.doModal( )
 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.mZappingTime = int( dialog.GetString( ) )
			if aType == TEST_ZAPPING_EPG :
				TestMgr.GetInstance( ).SetZappingTime( self.mZappingTime )
				TestMgr.GetInstance( ).ZappingTestEPG( )
			else :
				
				self.ZappingTestNull( )
				
		else :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( 'Error', 'Channel List is Empty' )
			dialog.doModal( )
			return


	@RunThread
	def ZappingTestNull( self ) :
		current = self.mDataCache.Channel_GetCurrent( )
		while self.mStopflag :
			nextChannel = self.mDataCache.Channel_GetNext( current )
			self.mDataCache.Channel_SetCurrent( nextChannel.mNumber, nextChannel.mServiceType )
			self.mCtrlLabel.setLabel( 'Now Zapping %d : %s ... ' % ( nextChannel.mNumber, nextChannel.mName ) )
			current = nextChannel
			time.sleep( self.mZappingTime )
