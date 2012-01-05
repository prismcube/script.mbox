import xbmc
import xbmcgui
import time
import sys

from pvr.gui.BaseWindow import Property
from pvr.Util import RunThread
import thread

class BaseDialog( xbmcgui.WindowXMLDialog, Property ):
	def __init__( self, *args, **kwargs ):
		xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
		self.mWin = None
		self.mWinId = 0


	def NumericKeyboard( self, aKeyType, aTitle, aString, aMaxLength ) :
		dialog = xbmcgui.Dialog( )
		value = dialog.numeric( aKeyType, aTitle, aString )

		if value == None or value == '' :
			return aString

		if len( value ) > aMaxLength :
			value = value[ len ( value ) - aMaxLength :]
			return value
