import xbmc
import xbmcgui
import time
import sys

from pvr.gui.basedialog import NumericKeyboard
from pvr.gui.basewindow import Action
import pvr.gui.dialogmgr as diamgr

E_INPUT_LABEL			= 4
E_DIALOG_HEADER			= 1
E_BUTTON_DONE			= 21
E_BUTTON_BACK_SPACE		= 23
E_BUTTON_PREV			= 20
E_BUTTON_NEXT			= 22

E_START_ID_NUMBER		= 10

class DialogNumeric( NumericKeyboard ) :
	def __init__( self, *args, **kwargs ) :
		NumericKeyboard.__init__( self, *args, **kwargs )
		
		self.inputLabel = None
		self.titleLabel = None
		self.ctrlEditLabel = 0
		self.isOk = False

	def onInit( self ) :
		"""
		self.getControl( E_DIALOG_HEADER ).setLabel( diamgr.getInstance().getTitleLabel( ) )
		self.inputLabel = diamgr.getInstance().getDefaultText( )
		"""
		self.isOk = False
		self.getControl( E_DIALOG_HEADER ).setLabel( self.getTitleLabel( ) )
		self.ctrlEditLabel = self.getControl( E_INPUT_LABEL )
		self.ctrlEditLabel.setLabel( self.inputLabel )
		self.drawKeyboard( )
		
		
	def onAction( self, action ) :
		actionId = action.getId( )
		focusId = self.getFocusId( )

		
		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.close( )
		

	def onClick( self, controlId ):
		focusId = self.getFocusId( )
		
		if( focusId >= E_START_ID_NUMBER and focusId <= 19 ) :
			self.inputLabel += self.getControl( focusId ).getLabel( )

		elif( focusId == E_BUTTON_BACK_SPACE ) :
			self.inputLabel = self.inputLabel[ : len( self.inputLabel ) - 1 ]
		
		elif( focusId == E_BUTTON_PREV ) :
			pass

		elif( focusId == E_BUTTON_NEXT ) :
			pass

		elif( focusId == E_BUTTON_DONE ) :
			self.isOk = True
			self.close( )

		self.ctrlEditLabel.setLabel( self.inputLabel )

	def isOK( self ) :
		return self.isOk

	def onFocus( self, controlId ):
		pass


	def drawKeyboard( self ):
		for i in range( 10 ) :
			self.getControl( E_START_ID_NUMBER + i ).setLabel( '%s' % i )

	def getNumber( self ) :
		return self.inputLabel


	def setNumber( self, number ) :
		self.inputLabel = number

	def getTitleLabel( self ) :
		return self.titleLabel

	def setTiteLabel( self, titleLabel ) :
		self.titleLabel = titleLabel

