import xbmc
import xbmcgui
import time
import sys

#from decorator import decorator
#from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.basewindow import Property

class BaseDialog( xbmcgui.WindowXMLDialog, Property ):
	def __init__( self, *args, **kwargs ):
		xbmcgui.WindowXMLDialog.__init__( self, *args, **kwargs )
		self.win = None

