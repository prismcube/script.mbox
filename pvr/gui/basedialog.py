import xbmc
import xbmcgui
import time
import sys

#from decorator import decorator
#from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt

class BaseDialog( xbmcgui.WindowXMLDialog ):
	def __init__( self, *args, **kwargs ):
		xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
		self.win = None

