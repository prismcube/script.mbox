import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
from pvr.gui.BaseWindow import BaseWindow, Action
import pvr.TunerConfigMgr as ConfigMgr
from inspect import currentframe


class MainMenu( BaseWindow ):
	def __init__( self, *args, **kwargs ):
		BaseWindow.__init__( self, *args, **kwargs )
		print 'lael98 check %d %s' %( currentframe().f_lineno, currentframe().f_code.co_filename )    
		print 'args=%s' % args[0]


	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId  )
		WinMgr.GetInstance().CheckSkinChange( )

	
	def onAction( self, aAction ):
		id = aAction.getId()
		
		print "MainMenu onaAction(): aAction %d" % id
		focusId = self.getFocusId( )
		print "MainMenu onAction(): focusId %d" % focusId
		
		if id == Action.ACTION_PREVIOUS_MENU :
			print 'lael98 check action menu'
		elif id == Action.ACTION_SELECT_ITEM :
			if focusId == 90301 :
				WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CONFIGURE )
			elif focusId == 90101 :
				WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_LANGUAGE_SETTING )
			elif focusId == 90102 :
				ConfigMgr.GetInstance( ).setNeedLoad( True )
				WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_ANTENNA_SETUP )
			elif focusId == 90103 :
				WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CHANNEL_SEARCH )
			elif focusId == 20 :
				self.close()
				import pvr.Launcher
				pvr.Launcher.GetInstance().PowerOff()
		elif id == Action.ACTION_PARENT_DIR :			
			print 'lael98 check ation back'
			self.close()

	def onClick( self, controlId ):
		print "MainMenu onclick(): control %d" % controlId

	def onFocus( self, controlId ):
		print "onFocus(): control %d" % controlId
