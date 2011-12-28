import xbmc
import xbmcgui
import time
import sys

from pvr.gui.basewindow import Property
from pvr.util import run_async
import thread

class BaseDialog( xbmcgui.WindowXMLDialog, Property ):
	def __init__( self, *args, **kwargs ):
		xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
		self.win = None
		self.busyCount = 0

	def setBusy(self, busy):
		self.lock.acquire()
		if busy == True:
			self.busyCount += 1
		else :
			self.busyCount -= 1
		self.lock.release()
		
		print 'busyCount= %d' %self.busyCount

		
	def resetBusy( self ) :
		self.busyCount = 0


	def isBusy(self):
		if self.busyCount > 0 :
			return True
		else :
			return False

		

class NormalKeyboard( BaseDialog ):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, *args, **kwargs)
		self.untilThread = False
		self.ctrlCursorId = None

	
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
		self.drawLabel( ).join()


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
	
