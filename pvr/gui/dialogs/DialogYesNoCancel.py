from pvr.gui.WindowImport import *


E_BUTTON_YES	= 301
E_BUTTON_NO		= 302
E_BUTTON_CLOSE	= 303
E_HEADER		= 100
E_BODY_LABEL_1	= 200


class DialogYesNoCancel( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mIsOk = E_DIALOG_STATE_CANCEL
		self.mTitle = ''
		self.mLabel = ''
		self.mAutoCloseFlag = False
		self.mAutoCloseTime = 0
		self.mDefaultFocusYes = False


	def onInit( self ) :
		self.mIsOk = E_DIALOG_STATE_CANCEL
		self.getControl( E_HEADER ).setLabel( self.mTitle )
		self.getControl( E_BODY_LABEL_1 ).setLabel( self.mLabel )
		self.mClosedFlag = False
		self.IsStandByClose( )

		if self.mAutoCloseFlag :
			thread = threading.Timer( 0.3, self.AutoClose )
			thread.start( )

		if self.mDefaultFocusYes :
			self.setFocusId( E_BUTTON_YES )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.mAutoCloseFlag = False
			self.Close( )


	def onClick( self, aControlId ) :
		if aControlId == E_BUTTON_YES :
			self.mIsOk = E_DIALOG_STATE_YES
		elif aControlId == E_BUTTON_NO :
			self.mIsOk = E_DIALOG_STATE_NO
		elif aControlId == E_BUTTON_CLOSE :
			self.mIsOk = E_DIALOG_STATE_CANCEL
		self.mAutoCloseFlag = False
		self.Close( )


	def IsOK( self ) :
		return self.mIsOk


	def onFocus( self, aControlId ) :
		pass


	def Close( self ) :
		self.mClosedFlag = True
		self.CloseDialog( )


	def SetDialogProperty( self, aTitle = '', aLabel = '', aDefaultClose = False ) :
		self.mTitle = aTitle
		self.mLabel = aLabel
		self.mDefaultIsOk = aDefaultClose


	def IsStandByClose( self ) :
		if self.mDataCache.GetStanbyClosing( ) :
			time.sleep( 0.5 )
			if self.mDefaultIsOk :
				self.mIsOk = E_DIALOG_STATE_YES
			else :
				self.mIsOk = E_DIALOG_STATE_NO
			self.mAutoCloseFlag = False
			self.Close( )


	def SetAutoCloseProperty( self, aFlag = False, aTime = 0, aIsYes = False ) :
		self.mAutoCloseFlag = aFlag
		self.mAutoCloseTime = aTime
		self.mDefaultFocusYes = aIsYes
		if aIsYes :
			self.mIsOk = E_DIALOG_STATE_YES


	def AutoClose( self ) :
		if not self.mAutoCloseFlag :
			LOG_TRACE( 'mAutoCloseFlag[%s] GetStanbyClosing[%s]'% ( self.mAutoCloseFlag, self.mDataCache.GetStanbyClosing( ) ) )
			return

		loopCount = self.mAutoCloseTime * 10
		while loopCount > 0 :
			if not self.mAutoCloseFlag :
				LOG_TRACE( '[AutoClose] selected, break auto close' )
				loopCount = -1
				break

			if ( loopCount % 10 ) == 0 :
				LOG_TRACE( '[AutoClose] %s second'% ( loopCount / 10 ) )

			loopCount -= 2
			time.sleep( 0.2 )

		LOG_TRACE( '[AutoClose] Closed' )
		if not self.mClosedFlag :
			self.Close( )


