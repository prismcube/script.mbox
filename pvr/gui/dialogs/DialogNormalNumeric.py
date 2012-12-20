from pvr.gui.WindowImport import *


E_INPUT_LABEL			= 102
E_BUTTON_DONE			= 121
E_BUTTON_BACK_SPACE		= 123
E_BUTTON_PREV			= 120
E_BUTTON_NEXT			= 122
E_START_ID_NUMBER		= 110
E_HEADER_LABEL			= 101


class DialogNormalNumeric( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mInputLabel = ''
		self.mTitleLabel = ''
		self.mOriginalString = ''
		self.mCtrlEditLabel = None
		self.mCtrlTitleLabel = None
		self.mMaxLength = 0
		self.mCheckFirstInput = False
		self.mInputString = ''
		self.mType = False
		self.mIsOk = E_DIALOG_STATE_NO


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mIsOk = E_DIALOG_STATE_NO
		self.getControl( E_HEADER_LABEL ).setLabel( self.mTitleLabel )
		self.mCtrlEditLabel = self.getControl( E_INPUT_LABEL )
		self.mCheckFirstInput = True
		self.SetInputLabel( )
		self.mCheckFirstInput = False
		self.DrawKeyboard( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU :
			if self.mIsOk != E_DIALOG_STATE_YES :
				self.mInputLabel = self.mOriginalString
			self.CloseDialog( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_PARENT_DIR :
			if len( self.mInputLabel ) < 1 :
				self.mIsOk = E_DIALOG_STATE_CANCEL
				self.CloseDialog( )
			else :
				self.mInputLabel = self.mInputLabel[ : len( self.mInputLabel ) - 1 ]
				self.mInputString = ''
				self.SetInputLabel( )

		elif actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 :
			self.mInputString = '%d' % ( int( actionId ) - Action.REMOTE_0 )
			self.mInputLabel += self.mInputString
			self.SetInputLabel( )

		elif actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :
			inputNum =  actionId - Action.ACTION_JUMP_SMS2 + 2
			if inputNum >= 2 and inputNum <= 9 :
				self.mInputString = '%d' % inputNum
				self.mInputLabel += self.mInputString
				self.SetInputLabel( )

		elif actionId == Action.ACTION_PAGE_UP or actionId == Action.ACTION_PAGE_DOWN :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.CloseDialog( )


	def onClick( self, aControlId ) :
		focusId = self.getFocusId( )

		LOG_TRACE( 'focus=%d' % focusId )

		if focusId >= E_START_ID_NUMBER and focusId <= E_START_ID_NUMBER + 9 :
			LOG_TRACE( 'focus=%d' % focusId )
			self.mInputString ='%d' % ( focusId - E_START_ID_NUMBER )
			self.mInputLabel += self.mInputString
			self.SetInputLabel( )

		elif focusId == E_BUTTON_BACK_SPACE :
			if len( self.mInputLabel ) > 0 :
				self.mInputLabel = self.mInputLabel[ : len( self.mInputLabel ) - 1 ]
			self.mInputString = ''
			self.SetInputLabel( )

		elif focusId == E_BUTTON_PREV :
			pass

		elif focusId == E_BUTTON_NEXT :
			pass

		elif focusId == E_BUTTON_DONE :
			self.mIsOk = E_DIALOG_STATE_YES
			xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )


	def onFocus( self, aControlId ) :
		pass


	def IsOK( self ) :
		return self.mIsOk


	def SetDialogProperty( self, aTitle, aString, aMaxLength, aType=False ) :
		self.mInputLabel = aString
		if self.mInputLabel == '0' :
			self.mInputLabel = ''
		self.mOriginalString = aString
		self.mTitleLabel = aTitle
		self.mMaxLength = aMaxLength
		self.mType = aType


	def GetString( self ) :
		if self.mInputLabel == '' :
			return self.mOriginalString
		return self.mInputLabel


	def DrawKeyboard( self ):
		for i in range( 10 ) :
			self.getControl( E_START_ID_NUMBER + i ).setLabel( '%d' % i )


	def SetInputLabel( self ) :
		if self.mCheckFirstInput == False :
			self.mCheckFirstInput = True
			self.mInputLabel = self.mInputString
		if len( self.mInputLabel ) > self.mMaxLength :
			self.mInputLabel = self.mInputLabel[0:self.mMaxLength]
		if self.mType == True :
			hideString = '*' * len( self.mInputLabel )
			self.mCtrlEditLabel.setLabel( hideString )
		else :
			self.mCtrlEditLabel.setLabel( self.mInputLabel )

