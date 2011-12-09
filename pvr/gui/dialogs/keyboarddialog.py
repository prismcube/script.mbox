import xbmc
import xbmcgui
import time
import sys

from pvr.gui.basedialog import BaseDialog
from pvr.gui.basewindow import Action

class KeyboardDialog( BaseDialog ):
	def __init__( self, *args, **kwargs ):
		BaseDialog.__init__( self, *args, **kwargs )
		self.controlList = []

	def onInit( self ):
		pass

		
	def onAction( self, action ):
		actionId = action.getId( )
		focusId = self.getFocusId( )
	
		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			print 'dhkim test action controlid = %d' % focusId
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
		
		
		
	def onFocus( self, controlId ):
		pass
	
