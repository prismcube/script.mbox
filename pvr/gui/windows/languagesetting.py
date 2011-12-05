
import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import SettingWindow, setWindowBusy
from pvr.gui.basewindow import Action
import pvr.elismgr
from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.guiconfig import *


class LanguageSetting(SettingWindow):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance().getCommander( )
			

	def onInit(self):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.setHeaderLabel( 'Language Preference' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK | FooterMask.G_FOOTER_ICON_SEARCH_MASK | FooterMask.G_FOOTER_ICON_OK_MASK | FooterMask.G_FOOTER_ICON_RECORD_MASK )
		
	
	def onAction( self, action ):

		actionId = action.getId( )
		focusId = self.getFocusId( )

		if actionId == Action.ACTION_PREVIOUS_MENU:
			pass
		elif actionId == Action.ACTION_SELECT_ITEM:
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR:
			self.close( )

		elif actionId == Action.ACTION_MOVE_LEFT:
			print '# 1dhkim test focusId = %d' % focusId
			if focusId != 9002 :
				print 'dhkim test focusId = %d' % focusId
				self.setFocusId(9002)
			else :
				self.setFocusId(9000)

		elif actionId == Action.ACTION_MOVE_UP:
			pass

		elif actionId == Action.ACTION_MOVE_DOWN:
			pass


	def onClick( self, controlId ):
		pass

		
	def onFocus( self, controlId ):
		pass
