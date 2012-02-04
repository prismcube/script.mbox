import xbmc
import xbmcgui
import time
import sys

from pvr.gui.BaseWindow import Action
from pvr.gui.BaseDialog import BaseDialog
from pvr.gui.GuiConfig import *

from pvr.Util import GuiLock, GuiLock2, LOG_WARN, LOG_TRACE, LOG_ERR

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
		self.mCtrlEditLabel = None
		self.mCtrlTitleLabel = None
		self.mMaxLength = 0
		self.mType = False
		self.mIsOk = E_DIALOG_STATE_NO

	def onInit( self ) :
		self.mIsOk = E_DIALOG_STATE_NO
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		self.getControl( E_HEADER_LABEL ).setLabel( self.mTitleLabel )
		self.mCtrlEditLabel = self.getControl( E_INPUT_LABEL )
		self.SetInputLabel( )
		self.DrawKeyboard( )
		
		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		LOG_TRACE('ACTION ID=%d' %actionId )
			
		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.mInputLabel = self.mOriginalString
			self.CloseDialog( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mInputLabel = self.mInputLabel[ : len( self.mInputLabel ) - 1 ]
			self.SetInputLabel( )

		elif actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 and ( len( self.mInputLabel ) < self.mMaxLength ) :
			LOG_TRACE('ACTION ID=%d' %actionId )
			inputString ='%d' %(actionId - Action.REMOTE_0 )
			self.mInputLabel += inputString
			self.SetInputLabel( )

		elif actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 and ( len( self.mInputLabel ) < self.mMaxLength ) :
			inputNum =  actionId - Action.ACTION_JUMP_SMS2 + 2
			if inputNum >= 2 and inputNum <= 9 :
				inputString ='%d' %inputNum
				self.mInputLabel += inputString
				self.SetInputLabel( )
		

	def onClick( self, aControlId ):
		focusId = self.getFocusId( )

		LOG_TRACE('focus=%d' %focusId )
			
		if focusId >= E_START_ID_NUMBER and focusId <= E_START_ID_NUMBER+9 and ( len( self.mInputLabel ) < self.mMaxLength ) :
			LOG_TRACE('focus=%d' %focusId )
			inputString ='%d' %(focusId - E_START_ID_NUMBER )
			self.mInputLabel += inputString
			self.SetInputLabel( )

		elif focusId == E_BUTTON_BACK_SPACE :
			if len( self.mInputLabel ) > 0 :
				self.mInputLabel = self.mInputLabel[ : len( self.mInputLabel ) - 1 ]
			self.SetInputLabel( )
		
		elif focusId == E_BUTTON_PREV :
			pass

		elif focusId == E_BUTTON_NEXT :
			pass

		elif focusId == E_BUTTON_DONE :
			self.mIsOk = E_DIALOG_STATE_YES		
			self.CloseDialog( )




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

	@GuiLock
	def SetInputLabel( self ) :
		if self.mType == True :
			hideString = '*' * len( self.mInputLabel )
			self.mCtrlEditLabel.setLabel( hideString )
		else :
			self.mCtrlEditLabel.setLabel( self.mInputLabel )

