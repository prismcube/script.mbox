import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
from pvr.gui.BaseWindow import BaseWindow, Action
import pvr.TunerConfigMgr as ConfigMgr
from inspect import currentframe
from pvr.Util import GuiLock

LIST_ID_MAIN_MENU				= 9000
BUTTON_ID_FIRSTINSTALLATION		= 90101
BUTTON_ID_ANTENNA_SETUP			= 90102
BUTTON_ID_CHANNEL_SEARCH		= 90103
BUTTON_ID_EDIT_SATELLITE		= 90104
BUTTON_ID_EDIT_TRANSPONDER		= 90105
BUTTION_ID_CONFIGURE			= 90106
BUTTON_ID_CAS					= 90107

class MainMenu( BaseWindow ):
	def __init__( self, *args, **kwargs ):
		BaseWindow.__init__( self, *args, **kwargs )
		print 'lael98 check %d %s' %( currentframe().f_lineno, currentframe().f_code.co_filename )    
		print 'args=%s' % args[0]


	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId  )
		self.mCtrlMainMenu = self.getControl( LIST_ID_MAIN_MENU )
		WinMgr.GetInstance().CheckSkinChange( )


	@GuiLock
	def onAction( self, aAction ):
		id = aAction.getId()
		
		print "MainMenu onAction(): aAction %d" % id
		focusId = self.getFocusId( )
		print "MainMenu onAction(): focusId %d" % focusId
		if id == Action.ACTION_PREVIOUS_MENU :
			print 'lael98 check action menu'
		elif id == Action.ACTION_SELECT_ITEM :
			pass

		elif id == Action.ACTION_PARENT_DIR :			
			print 'lael98 check ation back'
			self.close()

	@GuiLock			
	def onClick( self, aControlId ):
		print "MainMenu onclick(): control %d" % aControlId
		if aControlId == LIST_ID_MAIN_MENU :
			pass

		elif aControlId == BUTTON_ID_FIRSTINSTALLATION : # First Installation
			pass

		elif aControlId == BUTTON_ID_ANTENNA_SETUP : # Antenna Setup
			ConfigMgr.GetInstance( ).SetNeedLoad( True )		
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_ANTENNA_SETUP )

		elif aControlId == BUTTON_ID_CHANNEL_SEARCH : # Channel Search
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CHANNEL_SEARCH )

		elif aControlId == BUTTON_ID_EDIT_SATELLITE : # Edit Satellite
			#ToDO
			pass

		elif aControlId == BUTTON_ID_EDIT_TRANSPONDER : # Edit TransPonder
			#ToDO
			pass

		elif aControlId == BUTTION_ID_CONFIGURE : # Config
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CONFIGURE )

		elif aControlId == BUTTON_ID_CAS : # CAS
			#ToDO
			pass
			
		elif aControlId == 20 :
			self.close()
			import pvr.Launcher
			pvr.Launcher.GetInstance().PowerOff()

	@GuiLock
	def onFocus( self, aControlId ):
		pass

