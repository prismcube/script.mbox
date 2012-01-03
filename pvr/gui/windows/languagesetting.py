
import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as winmgr
from pvr.gui.BaseWindow import Action
import pvr.ElisMgr
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.guiconfig import *




class LanguageSetting(DetailWindow):
	def __init__( self, *args, **kwargs ):
		DetailWindow.__init__( self, *args, **kwargs)
		self.mCommander = pvr.ElisMgr.getInstance().getCommander( )
			

	def onInit(self):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.setHeaderLabel( 'Language Preference' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK | FooterMask.G_FOOTER_ICON_SEARCH_MASK | FooterMask.G_FOOTER_ICON_OK_MASK | FooterMask.G_FOOTER_ICON_RECORD_MASK )

		self.AddNormalButtonControl( E_SlideMenuButton01, 'TEST1' )
		self.AddNormalButtonControl( E_SlideMenuButton02, 'TEST2' )
		self.AddNormalButtonControl( E_SlideMenuButton03, 'TEST3' )

		#visibleControlIds = [ E_SlideMenuButton01, E_SlideMenuButton02, E_SlideMenuButton03 ]
		#self.SetVisibleControls( visibleControlIds, True )
		#self.SetEnableControls( visibleControlIds, True )
		
		self.InitControl( )
		
	def onAction( self, action ):

		actionId = action.getId( )
		focusId = self.getFocusId( )

		if actionId == Action.ACTION_PREVIOUS_MENU:
			pass
		elif actionId == Action.ACTION_SELECT_ITEM:
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR:
			self.ResetAllControl( )
			self.close( )

		elif actionId == Action.ACTION_MOVE_LEFT:
			if focusId != 9002 :
				self.setFocusId(9002)
			else :
				self.setFocusId(9000)

		elif actionId == Action.ACTION_MOVE_UP:
			self.ControlUp( )

		elif actionId == Action.ACTION_MOVE_DOWN:
			self.ControlDown( )


	def onClick( self, controlId ):
		pass

		
	def onFocus( self, controlId ):
		pass
