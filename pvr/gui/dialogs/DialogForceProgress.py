from pvr.gui.WindowImport import *


# Control IDs

PROGRESS_SCAN		= 400
LABEL_PERCENT		= 100
LABEL_STRING		= 200


class DialogForceProgress( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )	
		self.mLimitTime 		= 10
		self.mTitle				= 'Wait'
		self.mEventName			= None
		self.mFinish			= False

		self.mCtrlLabelPercent	= None
		self.mCtrlLabelString	= None
		self.mCtrlProgress		= None
		

	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mEventBus.Register( self )

		self.mCtrlLabelPercent	= self.getControl( LABEL_PERCENT )
		self.mCtrlLabelString	= self.getControl( LABEL_STRING )
		self.mCtrlProgress		= self.getControl( PROGRESS_SCAN )

		self.mCtrlLabelString.setLabel( self.mTitle	)
		self.mCtrlLabelPercent.setLabel( '0' )
		self.DrawProgress( )
		
		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.CloseDialog( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
			
		elif actionId == Action.ACTION_PARENT_DIR :
			self.CloseDialog( )
			

	def onClick( self, aControlId ) :
		pass


	def onFocus( self, aControlId ) :
		pass


	@GuiLock
	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowDialogId( ) :
			if aEvent.getName( ) == self.mEventName :
				self.mFinish = True

	
	def SetDialogProperty( self, aLimitTime=10, aTitle='Wait', aEventName=None ) :
		self.mLimitTime = aLimitTime
		self.mTitle		= aTitle
		self.mEventName = aEventName
		self.mFinish	= False


	def DrawProgress( self ) :
		for i in range( self.mLimitTime ) :
			percent = 100 / self.mLimitTime * i
			self.mCtrlLabelPercent.setLabel( '%d' % percent )
			self.mCtrlProgress.setPercent( percent )
			time.sleep( 1 )			

			if self.mFinish == True :
#				self.mCtrlLabelString.setLabel( '%s Set complete' % self.mTitle )
				self.mCtrlLabelString.setLabel( '%s completed' % self.mTitle )				
				self.Close( )
				break

#		self.mCtrlLabelString.setLabel( '%s Progress Time Over' % self.mTitle )
		self.mCtrlLabelString.setLabel( '%s timed out' % self.mTitle )
		self.Close( )


	def Close( self ) :
		self.mCtrlLabelPercent.setLabel( '100' )
		self.mCtrlProgress.setPercent( 100 )
		time.sleep( 1 )
		self.mEventBus.Deregister( self )
		self.CloseDialog( )


	def GetResult( self ) :
		return self.mFinish


	def SetResult( self, aResult ) :
		self.mFinish = aResult