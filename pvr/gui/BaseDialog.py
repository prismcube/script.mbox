import xbmc
import xbmcgui
import time
import sys

from pvr.gui.basewindow import Property
from pvr.util import RunThread
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

	def numericKeyboard( self, keyType, title, string, maxLength ) :
		dialog = xbmcgui.Dialog( )
		value = dialog.numeric( keyType, title, string )
		if value != None :
			if len( value ) > maxLength :
				value = value[ len ( value ) - maxLength :]
			return value
		else :
			print 'ERROR : Numeric Dialog Value is : %s' % value
			return value
			
	
