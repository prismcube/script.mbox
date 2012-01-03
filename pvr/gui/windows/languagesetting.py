
import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import DetailWindow, setWindowBusy
from pvr.gui.basewindow import Action
import pvr.elismgr
from elisproperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.guiconfig import *




class LanguageSetting(DetailWindow):
	def __init__( self, *args, **kwargs ):
		DetailWindow.__init__( self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance().getCommander( )
			

	def onInit(self):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.setHeaderLabel( 'Language Preference' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK | FooterMask.G_FOOTER_ICON_SEARCH_MASK | FooterMask.G_FOOTER_ICON_OK_MASK | FooterMask.G_FOOTER_ICON_RECORD_MASK )

		self.addNormalButtonControl( E_SlideMenuButton01, 'TEST1' )
		self.addNormalButtonControl( E_SlideMenuButton02, 'TEST2' )
		self.addNormalButtonControl( E_SlideMenuButton03, 'TEST3' )

		#visibleControlIds = [ E_SlideMenuButton01, E_SlideMenuButton02, E_SlideMenuButton03 ]
		#self.setVisibleControls( visibleControlIds, True )
		#self.setEnableControls( visibleControlIds, True )
		
		self.initControl( )
		
	def onAction( self, action ):

		actionId = action.getId( )
		focusId = self.getFocusId( )

		if actionId == Action.ACTION_PREVIOUS_MENU:
			pass
		elif actionId == Action.ACTION_SELECT_ITEM:
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR:
			self.resetAllControl( )
			self.close( )

		elif actionId == Action.ACTION_MOVE_LEFT:
			if focusId != 9002 :
				self.setFocusId(9002)
			else :
				self.setFocusId(9000)

		elif actionId == Action.ACTION_MOVE_UP:
			self.controlUp( )

		elif actionId == Action.ACTION_MOVE_DOWN:
			self.controlDown( )


	def onClick( self, controlId ):
		pass

		
	def onFocus( self, controlId ):
		pass
