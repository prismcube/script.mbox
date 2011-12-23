import xbmc
import xbmcgui
import time
import sys

from pvr.gui.basewindow import Property
from pvr.util import run_async


class BaseDialog( xbmcgui.WindowXMLDialog, Property ):
	def __init__( self, *args, **kwargs ):
		xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
		

class NormalKeyboard( BaseDialog ):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, *args, **kwargs)
		self.untilThread = False
		self.ctrlCursorId = None

	
	def drawLabel( self ):
		while self.untilThread :
			'''
			self.getControl( self.ctrlLabelId ).setLabel( self.tempstring2 )
			time.sleep( 0.5 )
			self.getControl( self.ctrlLabelId ).setLabel( self.tempstring1 )
			time.sleep( 0.5 )
			'''
	@run_async
	def drawLabel( self ) :
		while self.untilThread :
			self.getControl( self.ctrlCursorId ).setVisible( False )
			time.sleep( 0.3 )
			self.getControl( self.ctrlCursorId ).setVisible( True )
			time.sleep( 0.3 )


	def makelabel( self, controlId, cursorId, string, position ):
		self.ctrlCursorId = cursorId
		preTmpstr = string[ : position]
		postTmpstr = string[ position : ]
		labelString = preTmpstr + ' ' + postTmpstr
		cursorString = preTmpstr + '|' + postTmpstr
		self.getControl( controlId ).setLabel( labelString )
		self.getControl( self.ctrlCursorId ).setLabel( cursorString )

	def stopKeyboardCursor( self ):
		self.untilThread = False
		self.drawLabel().join()

	def startKeyboardCursor( self ):
		self.untilThread = True
	
class HideNormalKeyboard( NormalKeyboard ):

	def makelabel( self, controlId, string, position ):
		#self.ctrlLabelId = controlId
		preTmpstr = '*' * position
		postTmpstr = '*' * ( len( string[ position : ] ) )
		self.string = preTmpstr + ' ' + postTmpstr 

class NumericKeyboard( BaseDialog ):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, *args, **kwargs)
	