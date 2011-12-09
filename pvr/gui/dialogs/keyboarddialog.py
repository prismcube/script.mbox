import xbmc
import xbmcgui
import time
import sys

from pvr.gui.basewindow import BaseDialog


class KeyboardDialog(BaseDialog):
	def __init__(self, *args, **kwargs):
		BaseDialog.__init__(self, *args, **kwargs)
		self.controlList = []

	def onInit( self ):
		pass
		
	def onAction( self, action ):	
		pass

	def onClick( self, controlId ):
		pass
		
	def onFocus( self, controlId ):
		pass

	
