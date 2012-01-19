import xbmc
import xbmcgui
import time
import sys

from pvr.gui.BaseDialog import BaseDialog
from pvr.gui.BaseWindow import Action
from pvr.gui.GuiConfig import *

E_BUTTON_YES	= 301
E_BUTTON_NO		= 302

E_HEADER		= 100

E_BODY_LABEL_1	= 200
E_BODY_LABEL_2	= 201
E_BODY_LABEL_3	= 202

class DialogYesNoCancel( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )	
		self.mIsOk = E_DIALOG_STATE_NO
		self.mTitle = ''
		self.mLabel1 = ''
		self.mLabel2 = ''
		self.mLabel3 = ''


	def onInit( self ) :
		self.mIsOk = E_DIALOG_STATE_NO
		self.getControl( E_HEADER ).setLabel( self.mTitle )
		self.getControl( E_BODY_LABEL_1 ).setLabel( self.mLabel1 )
		self.getControl( E_BODY_LABEL_2 ).setLabel( self.mLabel2 )
		self.getControl( E_BODY_LABEL_3 ).setLabel( self.mLabel3 )		
		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.CloseDialog( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
			
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.CloseDialog( )

	def onClick( self, aControlId ) :
		if aControlId == E_BUTTON_YES :
			self.mIsOk = E_DIALOG_STATE_YES
			self.CloseDialog( )

		elif aControlId == E_BUTTON_NO :
			self.mIsOk = E_DIALOG_STATE_NO
			self.CloseDialog( )

	def IsOK( self ) :
		return self.mIsOk


	def onFocus( self, aControlId ) :
		pass
		

	def SetDialogProperty( self, aTitle='', aLabel1='', aLabel2='', aLabel3='' ) :
		self.mTitle = aTitle
		self.mLabel1 = aLabel1
		self.mLavel2 = aLabel2
		self.mLabel3 = aLabel3

