import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import BaseWindow
from pvr.gui.basewindow import Action
from inspect import currentframe


class MainMenu( BaseWindow ):
	def __init__( self, *args, **kwargs ):
		BaseWindow.__init__( self, *args, **kwargs )
		print 'lael98 check %d %s' %( currentframe().f_lineno, currentframe().f_code.co_filename )    
		print 'args=%s' % args[0]


	def onInit( self ):
		print '--------------- testlael98 -----------------'
		if not self.win :
			self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId() )

		winmgr.getInstance().checkSkinChange( )

	
	def onAction( self, action ):
		id = action.getId()
		
		print "MainMenu onAction(): action %d" % id
		focusId = self.getFocusId( )
		print "MainMenu onAction(): focusId %d" % focusId
		
		if id == Action.ACTION_PREVIOUS_MENU :
			print 'lael98 check action menu'
		elif id == Action.ACTION_SELECT_ITEM :
			if focusId == 90301 :
				winmgr.getInstance().showWindow( winmgr.WIN_ID_CONFIGURE )
			elif focusId == 90101 :
				winmgr.getInstance().showWindow( winmgr.WIN_ID_LANGUAGE_SETTING )
			elif focusId == 90102 :
				winmgr.getInstance().showWindow( winmgr.WIN_ID_ANTENNA_SETUP )
			elif focusId == 90103 :
				winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_SEARCH )
			elif focusId == 20 :
				self.close()
				import pvr.launcher
				pvr.launcher.getInstance().powerOff()
		elif id == Action.ACTION_PARENT_DIR :			
			print 'lael98 check ation back'
			self.close()

	def onClick( self, controlId ):
		print "MainMenu onclick(): control %d" % controlId

	def onFocus( self, controlId ):
		print "onFocus(): control %d" % controlId
