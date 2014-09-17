from pvr.gui.WindowImport import *

PROGRESS_SCAN		= 400
LABEL_PERCENT		= 100
LABEL_STRING		= 200
LABEL_PAGE			= 201

class DialogForceProgress( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mLimitTime 		= 10
		self.mTitle				= None
		self.mStepPage			= None
		self.mEventName			= None
		self.mFinish			= False
		self.mGetEvent			= False

		self.mCtrlLabelPercent	= None
		self.mCtrlLabelString	= None
		self.mCtrlProgress		= None
		self.mCtrlLabelPage		= None


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.mEventBus.Register( self )

		self.mCtrlLabelPercent	= self.getControl( LABEL_PERCENT )
		self.mCtrlLabelString	= self.getControl( LABEL_STRING )
		self.mCtrlLabelPage		= self.getControl( LABEL_PAGE )
		self.mCtrlProgress		= self.getControl( PROGRESS_SCAN )

		self.mCtrlLabelString.setLabel( self.mTitle	)
		self.mCtrlLabelPage.setLabel( self.mStepPage )
		self.mCtrlLabelPercent.setLabel( MR_LANG( 'Waiting' ) + ' - 0 %' )
		self.DrawProgress( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.CloseDialog( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass


	def onClick( self, aControlId ) :
		pass


	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowDialogId( ) :
			if aEvent.getName( ) == self.mEventName :
				self.mFinish	= True
				self.mGetEvent	= True


	def SetDialogProperty( self, aLimitTime, aTitle, aEventName = None, aPage = '' ) :
		self.mLimitTime = aLimitTime
		self.mTitle		= aTitle
		self.mEventName = aEventName
		self.mFinish	= False
		self.mGetEvent	= False
		self.mStepPage  = aPage


	def DrawProgress( self ) :
		i = 1
		while self.mFinish == False :
			percent = float( 100.0 / self.mLimitTime * i )
			if percent < 95 or self.mEventName != None :
				if percent <= 1.0 :
					percent = 1.0
				self.mCtrlLabelPercent.setLabel( MR_LANG( 'Waiting' ) + ' - %.1f %%' % percent )
				self.mCtrlProgress.setPercent( percent )
			
			if self.mEventName != None and percent > 100 :
				self.mGetEvent = False
				self.mCtrlLabelString.setLabel( MR_LANG( '%s timed out' ) % self.mTitle )
				break

			i = i + 1
			time.sleep( 1 )

		if self.mGetEvent == False and self.mEventName != None :
			self.mCtrlLabelString.setLabel( MR_LANG( '%s timed out' ) % self.mTitle )
		else :
			self.mCtrlLabelString.setLabel( MR_LANG( '%s completed' ) % self.mTitle )

		self.Close( )


	def Close( self ) :
		self.mCtrlLabelPercent.setLabel( MR_LANG( 'Waiting' ) + ' - 100 %' )
		self.mCtrlProgress.setPercent( 100 )
		self.mEventBus.Deregister( self )
		time.sleep( 1 )
		self.CloseDialog( )


	def GetResult( self ) :
		return self.mFinish


	def SetResult( self, aResult ) :
		self.mFinish = aResult
