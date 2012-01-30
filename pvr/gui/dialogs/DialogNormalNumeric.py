import xbmc
import xbmcgui
import time
import sys

from pvr.gui.BaseWindow import Action
from pvr.gui.BaseDialog import BaseDialog
from pvr.gui.GuiConfig import *

from pvr.Util import LOG_TRACE

E_INPUT_LABEL			= 4
E_BUTTON_DONE			= 21
E_BUTTON_BACK_SPACE		= 23
E_BUTTON_PREV			= 20
E_BUTTON_NEXT			= 22
E_START_ID_NUMBER		= 10
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
		
		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.mInputLabel = self.mOriginalString
			self.CloseDialog( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mInputLabel = self.mInputLabel[ : len( self.mInputLabel ) - 1 ]
			self.SetInputLabel( )

		elif actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 and ( len( self.mInputLabel ) < self.mMaxLength ) :
			self.mInputLabel += self.getControl( 10 + ( actionId - 58 ) ).getLabel( )
			self.SetInputLabel( )
		

	def onClick( self, aControlId ):
		focusId = self.getFocusId( )
		
		if focusId >= E_START_ID_NUMBER and focusId <= 19 and ( len( self.mInputLabel ) < self.mMaxLength ) :
			self.mInputLabel += self.getControl( focusId ).getLabel( )

		elif focusId == E_BUTTON_BACK_SPACE :
			self.mInputLabel = self.mInputLabel[ : len( self.mInputLabel ) - 1 ]
		
		elif focusId == E_BUTTON_PREV :
			pass

		elif focusId == E_BUTTON_NEXT :
			pass

		elif focusId == E_BUTTON_DONE :
			self.mIsOk = E_DIALOG_STATE_YES		
			self.CloseDialog( )

		self.SetInputLabel( )


	def onFocus( self, aControlId ) :
		pass


	def IsOK( self ) :
		return self.mIsOk


	def SetDialogProperty( self, aTitle, aString, aMaxLength, aType=False ) :
		self.mInputLabel = aString
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
		if self.mType == True :
			hideString = '*' * len( self.mInputLabel )
			self.mCtrlEditLabel.setLabel( hideString )
		else :
			self.mCtrlEditLabel.setLabel( self.mInputLabel )