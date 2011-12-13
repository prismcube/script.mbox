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
		self.tempstring1 = None
		self.tempstring2 = None
		self.ctrlLabelId = None
		
	@run_async
	def drawLabel( self ):
		while self.untilThread :
			self.getControl( self.ctrlLabelId ).setLabel( self.tempstring2 )
			time.sleep( 0.5 )
			self.getControl( self.ctrlLabelId ).setLabel( self.tempstring1 )
			time.sleep( 0.5 )

	def makelabel( self, controlId, string, position ):
		self.ctrlLabelId = controlId
		preTmpstr = string[ : position]
		postTmpstr = string[ position : ]
		self.tempstring1 = preTmpstr + '|' + postTmpstr
		self.tempstring2 = preTmpstr + ' ' + postTmpstr 

	def stopKeyboardCursor( self ):
		self.untilThread = False
		self.drawLabel().join()

	def startKeyboardCursor( self ):
		self.untilThread = True
	
class HideNormalKeyboard( NormalKeyboard ):

	def makelabel( self, controlId, string, position ):
		self.ctrlLabelId = controlId
		preTmpstr = '*' * position
		postTmpstr = '*' * ( len( string[ position : ] ) )
		self.tempstring1 = preTmpstr + '|' + postTmpstr
		self.tempstring2 = preTmpstr + ' ' + postTmpstr 

class NumericKeyboard( BaseDialog ):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, *args, **kwargs)
	