import xbmc
import xbmcgui
import time
import sys

from pvr.gui.BaseWindow import Property

class BaseDialog( xbmcgui.WindowXMLDialog, Property ):
	def __init__( self, *args, **kwargs ):
		xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
		self.mWin = None
		self.mWinId = 0


	def NumericKeyboard( self, aKeyType, aTitle, aString, aMaxLength ) :
		print 'dhkim test aKeyType = %d, aTitle = %s, aString = %s, aMaxLength = %d' % ( aKeyType, aTitle, aString, aMaxLength )
		dialog = xbmcgui.Dialog( )
		value = dialog.numeric( aKeyType, aTitle, aString )
		print 'dhkim test value = %s' % value
		if value == None or value == '' :
			return aString

		if len( value ) > aMaxLength :
			value = value[ len ( value ) - aMaxLength :]
		return value

	def CloseDialog( self ) :
		self.clearProperty( 'AnimationWaitingDialogOnClose' )
		time.sleep( 0.3 )
		self.close( )