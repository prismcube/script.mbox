from pvr.gui.WindowImport import *


E_BUTTON_OK		= 301
E_HEADER		= 100
E_BODY_LABEL_1	= 200
E_BODY_LABEL_2	= 300
E_BODY_LABEL_3	= 400


class DialogPopupOK( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mTitle			= ''
		self.mLabel1		= ''
		self.mLabel2		= ''
		self.mLabel3		= ''
		self.mStayCount		= 0
		self.mIsOk			= None
		self.mAutoClose		= False
		self.mAutoCloseTime = 5
		self.mClosed		= False
		self.mButtonVisible = True
		self.mDialogType    = 'popup'


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.getControl( E_HEADER ).setLabel( self.mTitle )
		self.getControl( E_BODY_LABEL_1 ).setLabel( self.mLabel1 )
		self.getControl( E_BODY_LABEL_2 ).setLabel( self.mLabel2 )
		self.getControl( E_BODY_LABEL_3 ).setLabel( self.mLabel3 )
		if not self.GetButtonVisible( ) :
			self.getControl( E_BUTTON_OK ).setVisible( False )

		self.mStayCount = self.GetStayCount( )
		if self.mAutoClose :
			thread = threading.Timer( 0.3, self.AutoClose )
			thread.start( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.mIsOk = actionId
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			if self.mStayCount < 1 :
				self.mClosed = True
				self.CloseDialog( )

			self.mStayCount -= 1

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_STOP :
			self.mClosed = True
			self.CloseDialog( )

		elif actionId == Action.ACTION_PLAYER_PLAY or actionId == Action.ACTION_PAUSE :
			self.mClosed = True
			self.CloseDialog( )


	def onClick( self, aControlId ) :
		if aControlId == E_BUTTON_OK :
			if self.mStayCount < 1 :
				self.mClosed = True
				self.CloseDialog( )

			self.mStayCount -= 1


	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowDialogId( ) :

			if aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
				LOG_TRACE( 'ElisEventPlaybackEOF mType[%d]'% ( aEvent.mType ) )

				if aEvent.mType == ElisEnum.E_EOF_END :
					LOG_TRACE( 'EventRecv EOF_END' )
					xbmc.executebuiltin('xbmc.Action(stop)')


	def SetDialogProperty( self, aTitle='', aLabel1='', aLabel2='', aLabel3='' ) :
		self.mTitle = aTitle
		self.mLabel1 = aLabel1
		self.mLabel2 = aLabel2
		self.mLabel3 = aLabel3
		self.mDialogType = 'popup'
		if self.mLabel2 == '' and self.mLabel3 == '' :
			self.mLabel2 = self.mLabel1
			self.mLabel1 = ''


	def SetDialogType( self, aPopupType = 'popup' ) :
		self.mDialogType = aPopupType


	def SetButtonVisible( self, aVisible = True ) :
		self.mButtonVisible = aVisible


	def GetButtonVisible( self ) :
		return self.mButtonVisible


	def GetStayCount( self ) :
		return self.mStayCount


	def SetStayCount( self, aCount = 0 ) :
		self.mStayCount = aCount


	def GetCloseStatus( self ) :
		return self.mIsOk


	def SetAutoCloseTime( self, aTime ) :
		self.mAutoClose = True
		self.mAutoCloseTime = aTime
		if self.mAutoCloseTime <= 0 :
			self.mAutoClose = False


	def AutoClose( self ) :
		self.mCtrlLabel2 = self.getControl( E_BODY_LABEL_2 )
		for i in range( self.mAutoCloseTime * 5 ) :
			if self.mClosed :
				return

			if self.mDialogType == 'update' :
				countdown = int( self.mAutoCloseTime - int( i / 5 ) )
				label = '%s%s'% ( MR_LANG( 'Rebooting in %s second(s)' ) % countdown, ING )
				self.mCtrlLabel2.setLabel( label )

			time.sleep( 0.2 )

		try :
			self.CloseDialog( )
		except Exception, ex :
			LOG_TRACE( 'except close dialog' )


