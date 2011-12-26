<<<<<<< HEAD

import xbmc
import xbmcgui
import time
import sys

from pvr.gui.basedialog import NormalKeyboard
from pvr.gui.basewindow import Action
import pvr.gui.dialogmgr as diamgr

E_INPUT_LABEL			= 310
E_CURSOR_LABEL			= 400
E_DIALOG_HEADER			= 311
E_BUTTON_DONE			= 300
E_BUTTON_BACK_SPACE		= 8
E_RADIO_SHIFT			= 302
E_RADIO_CAPSLOCK		= 303
E_RADIO_SYMBOLS			= 304
E_BUTTON_IP_INPUT		= 307
E_BUTTON_SPACE			= 32
E_BUTTON_PREV			= 305
E_BUTTON_NEXT			= 306

E_NUM_OF_NUMBER			= 10
E_START_ID_NUMBER		= 48
E_NUM_OF_ALPHABET		= 26
E_START_ID_ALPHABET		= 65

E_ASCIICODE_LOWER_A		= 0x61
E_ASCIICODE_UPPER_A		= 0x41

class DialogKeyPad( NormalKeyboard ) :
	def __init__( self, *args, **kwargs ) :
		NormalKeyboard.__init__( self, *args, **kwargs )

		self.inputLabel = None
		self.titleLabel = None
		self.ctrlEditLabel = 0
		self.cursorPosition = 0
		
	def onInit( self ):
		self.isOk = False
		self.ctrlEditLabel = self.getControl( E_INPUT_LABEL )
		self.getControl( E_DIALOG_HEADER ).setLabel( self.getTitleLabel( ) )
		self.cursorPosition = len( self.inputLabel )
		self.drawKeyboard( )
		self.startKeyboardCursor( )
		self.makelabel( E_INPUT_LABEL, E_CURSOR_LABEL, self.inputLabel, self.cursorPosition )
		self.drawLabel( )

		
	def onAction( self, action ):
		actionId = action.getId( )
		focusId = self.getFocusId( )
	
		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.stopKeyboardCursor( )
			self.close( )

		elif actionId == Action.ACTION_MOVE_UP :
			pass
	
		elif actionId == Action.ACTION_MOVE_DOWN :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT :
			pass
				
		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass


	def onClick( self, controlId ):
		focusId = self.getFocusId( )
		
		if( focusId >= E_START_ID_NUMBER and focusId <= 57 ) or ( focusId >= E_START_ID_ALPHABET and focusId <= 90 ) :
			tmpstr1 = self.inputLabel[ : self.cursorPosition ]
			temstr2 = self.inputLabel[ self.cursorPosition : ]
			self.inputLabel = tmpstr1 + self.getControl( focusId ).getLabel( ) + temstr2
			self.cursorPosition = self.cursorPosition + 1
		
		elif( focusId == E_RADIO_SHIFT ) :
			self.drawKeyboard( )

		elif( focusId == E_BUTTON_BACK_SPACE ) :
			if( self.cursorPosition != 0 ) :
				tmpstr1 = self.inputLabel[ : self.cursorPosition - 1 ]
				temstr2 = self.inputLabel[ self.cursorPosition : ]
				self.inputLabel = tmpstr1 + temstr2
				self.cursorPosition = self.cursorPosition - 1

		elif( focusId == E_RADIO_SYMBOLS ) :
			self.drawKeyboard( )

		elif( focusId == E_BUTTON_SPACE ) :
			tmpstr1 = self.inputLabel[ : self.cursorPosition ]
			temstr2 = self.inputLabel[ self.cursorPosition : ]
			self.inputLabel = tmpstr1 + ' ' + temstr2
			self.cursorPosition = self.cursorPosition + 1

		elif( focusId == E_BUTTON_PREV ) :
			if( self.cursorPosition != 0 ) :
				self.cursorPosition = self.cursorPosition - 1

		elif( focusId == E_BUTTON_NEXT ) :
			if( self.cursorPosition != len( self.inputLabel ) ) :
				self.cursorPosition = self.cursorPosition + 1

		elif( focusId == E_BUTTON_DONE ) :
			self.stopKeyboardCursor( )
			self.isOk = True
			self.close( )
		self.makelabel( E_INPUT_LABEL, E_CURSOR_LABEL, self.inputLabel, self.cursorPosition )


	def onFocus( self, controlId ):
		pass


	def drawKeyboard( self ):

		if self.getControl( E_RADIO_SYMBOLS ).isSelected( ) == True :
			for i in range( E_NUM_OF_NUMBER ) :
				self.getControl( E_START_ID_NUMBER + i ).setLabel( chr ( 0x21 + i ) )
			for i in range( 5 ) : 
				self.getControl( E_START_ID_ALPHABET + i ).setLabel( chr ( 0x2b + i ) )
			for i in range( 7 ) : 
				self.getControl( E_START_ID_ALPHABET + 5 + i ).setLabel( chr ( 0x3a + i ) )
			for i in range( 6 ) : 
				self.getControl( E_START_ID_ALPHABET + 12 + i ).setLabel( chr ( 0x5b + i ) )
			for i in range( 4 ) : 
				self.getControl( E_START_ID_ALPHABET + 18 + i ).setLabel( chr ( 0x7b + i ) )
			for i in range( 4 ) : 
				self.getControl( E_START_ID_ALPHABET + 22 + i ).setLabel( '' )
			return
			
		for i in range( E_NUM_OF_NUMBER ) :
			self.getControl( E_START_ID_NUMBER + i ).setLabel( '%s' % i )
		for i in range( E_NUM_OF_ALPHABET ) :
			if self.getControl( E_RADIO_SHIFT ).isSelected( ) == False :
				self.getControl( E_START_ID_ALPHABET + i ).setLabel( chr ( E_ASCIICODE_LOWER_A + i ) )
			else :
				self.getControl( E_START_ID_ALPHABET + i ).setLabel( chr ( E_ASCIICODE_UPPER_A + i ) )


	def isOK( self ) :
		return self.isOk

	def getText( self ) :
		return self.inputLabel

	def setText( self, text ) :
		self.inputLabel = text

	def getTitleLabel( self ) :
		return self.titleLabel

	def setTiteLabel( self, titleLabel ) :
		self.titleLabel = titleLabel
=======

import xbmc
import xbmcgui
import time
import sys

from pvr.gui.basedialog import NormalKeyboard
from pvr.gui.basewindow import Action
import pvr.gui.dialogmgr as diamgr

E_INPUT_LABEL			= 310
E_CURSOR_LABEL			= 400
E_DIALOG_HEADER			= 311
E_BUTTON_DONE			= 300
E_BUTTON_BACK_SPACE		= 8
E_RADIO_SHIFT			= 302
E_RADIO_CAPSLOCK		= 303
E_RADIO_SYMBOLS			= 304
E_BUTTON_IP_INPUT		= 307
E_BUTTON_SPACE			= 32
E_BUTTON_PREV			= 305
E_BUTTON_NEXT			= 306

E_NUM_OF_NUMBER			= 10
E_START_ID_NUMBER		= 48
E_NUM_OF_ALPHABET		= 26
E_START_ID_ALPHABET		= 65

E_ASCIICODE_LOWER_A		= 0x61
E_ASCIICODE_UPPER_A		= 0x41

class DialogKeyPad( NormalKeyboard ) :
	def __init__( self, *args, **kwargs ) :
		NormalKeyboard.__init__( self, *args, **kwargs )

		self.inputLabel = None
		self.titleLabel = None
		self.ctrlEditLabel = 0
		self.cursorPosition = 0
		
	def onInit( self ):
		self.isOk = False
		self.ctrlEditLabel = self.getControl( E_INPUT_LABEL )
		self.getControl( E_DIALOG_HEADER ).setLabel( self.getTitleLabel( ) )
		self.cursorPosition = len( self.inputLabel )
		self.drawKeyboard( )
		self.startKeyboardCursor( )
		self.makelabel( E_INPUT_LABEL, E_CURSOR_LABEL, self.inputLabel, self.cursorPosition )
		self.drawLabel( )

		
	def onAction( self, action ):
		actionId = action.getId( )
		focusId = self.getFocusId( )
	
		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.stopKeyboardCursor( )
			self.close( )

		elif actionId == Action.ACTION_MOVE_UP :
			pass
	
		elif actionId == Action.ACTION_MOVE_DOWN :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT :
			pass
				
		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass


	def onClick( self, controlId ):
		focusId = self.getFocusId( )
		
		if( focusId >= E_START_ID_NUMBER and focusId <= 57 ) or ( focusId >= E_START_ID_ALPHABET and focusId <= 90 ) :
			tmpstr1 = self.inputLabel[ : self.cursorPosition ]
			temstr2 = self.inputLabel[ self.cursorPosition : ]
			self.inputLabel = tmpstr1 + self.getControl( focusId ).getLabel( ) + temstr2
			self.cursorPosition = self.cursorPosition + 1
		
		elif( focusId == E_RADIO_SHIFT ) :
			self.drawKeyboard( )

		elif( focusId == E_BUTTON_BACK_SPACE ) :
			if( self.cursorPosition != 0 ) :
				tmpstr1 = self.inputLabel[ : self.cursorPosition - 1 ]
				temstr2 = self.inputLabel[ self.cursorPosition : ]
				self.inputLabel = tmpstr1 + temstr2
				self.cursorPosition = self.cursorPosition - 1

		elif( focusId == E_RADIO_SYMBOLS ) :
			self.drawKeyboard( )

		elif( focusId == E_BUTTON_SPACE ) :
			tmpstr1 = self.inputLabel[ : self.cursorPosition ]
			temstr2 = self.inputLabel[ self.cursorPosition : ]
			self.inputLabel = tmpstr1 + ' ' + temstr2
			self.cursorPosition = self.cursorPosition + 1

		elif( focusId == E_BUTTON_PREV ) :
			if( self.cursorPosition != 0 ) :
				self.cursorPosition = self.cursorPosition - 1

		elif( focusId == E_BUTTON_NEXT ) :
			if( self.cursorPosition != len( self.inputLabel ) ) :
				self.cursorPosition = self.cursorPosition + 1

		elif( focusId == E_BUTTON_DONE ) :
			self.stopKeyboardCursor( )
			self.isOk = True
			self.close( )
		self.makelabel( E_INPUT_LABEL, E_CURSOR_LABEL, self.inputLabel, self.cursorPosition )


	def onFocus( self, controlId ):
		pass


	def drawKeyboard( self ):

		if self.getControl( E_RADIO_SYMBOLS ).isSelected( ) == True :
			for i in range( E_NUM_OF_NUMBER ) :
				self.getControl( E_START_ID_NUMBER + i ).setLabel( chr ( 0x21 + i ) )
			for i in range( 5 ) : 
				self.getControl( E_START_ID_ALPHABET + i ).setLabel( chr ( 0x2b + i ) )
			for i in range( 7 ) : 
				self.getControl( E_START_ID_ALPHABET + 5 + i ).setLabel( chr ( 0x3a + i ) )
			for i in range( 6 ) : 
				self.getControl( E_START_ID_ALPHABET + 12 + i ).setLabel( chr ( 0x5b + i ) )
			for i in range( 4 ) : 
				self.getControl( E_START_ID_ALPHABET + 18 + i ).setLabel( chr ( 0x7b + i ) )
			for i in range( 4 ) : 
				self.getControl( E_START_ID_ALPHABET + 22 + i ).setLabel( '' )
			return
			
		for i in range( E_NUM_OF_NUMBER ) :
			self.getControl( E_START_ID_NUMBER + i ).setLabel( '%s' % i )
		for i in range( E_NUM_OF_ALPHABET ) :
			if self.getControl( E_RADIO_SHIFT ).isSelected( ) == False :
				self.getControl( E_START_ID_ALPHABET + i ).setLabel( chr ( E_ASCIICODE_LOWER_A + i ) )
			else :
				self.getControl( E_START_ID_ALPHABET + i ).setLabel( chr ( E_ASCIICODE_UPPER_A + i ) )


	def isOK( self ) :
		return self.isOk

	def getText( self ) :
		return self.inputLabel

	def setText( self, text ) :
		self.inputLabel = text

	def getTitleLabel( self ) :
		return self.titleLabel

	def setTiteLabel( self, titleLabel ) :
		self.titleLabel = titleLabel
>>>>>>> 7e9a82e07fbd5643d279da06044e472568991e68
 