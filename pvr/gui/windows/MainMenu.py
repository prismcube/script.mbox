import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.BaseWindow import BaseWindow, Action
from inspect import currentframe
import pvr.ElisMgr
from pvr.Util import GuiLock, LOG_TRACE

LIST_ID_MAIN_MENU				= 9000
BUTTON_ID_INSTALLATION			= 90100
BUTTON_ID_ARCHIVE				= 90200
BUTTON_ID_EPG					= 90300
BUTTON_ID_CHANNEL_LIST			= 90400
BUTTON_ID_MEDIA_CENTER			= 90500
BUTTON_ID_SYSTEM_INFO			= 90600

BUTTON_ID_FIRSTINSTALLATION		= 90101
BUTTON_ID_ANTENNA_SETUP			= 90102
BUTTON_ID_CHANNEL_SEARCH		= 90103
BUTTON_ID_EDIT_SATELLITE		= 90104
BUTTON_ID_EDIT_TRANSPONDER		= 90105
BUTTON_ID_CONFIGURE				= 90106
BUTTON_ID_CAS					= 90107


class MainMenu( BaseWindow ):
	def __init__( self, *args, **kwargs ):
		BaseWindow.__init__( self, *args, **kwargs )
		#self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.mStartMediaCenter = False

	def onInit( self ):
		LOG_TRACE('')
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId )
		self.mCtrlMainMenu = self.getControl( LIST_ID_MAIN_MENU )
		WinMgr.GetInstance().CheckSkinChange( )
		self.mStartMediaCenter = False
		if self.mStartMediaCenter == True :
			# command
			self.mStartMediaCenter = False


	def onAction( self, aAction ) :
		LOG_TRACE('')
		id = aAction.getId()
		focusId = self.getFocusId( )

		self.GlobalAction( id )		
		
		LOG_TRACE( "MainMenu onAction(): focusId %d" % focusId )
		if id == Action.ACTION_PREVIOUS_MENU :
			pass
		elif id == Action.ACTION_SELECT_ITEM :
			pass

		elif id == Action.ACTION_PARENT_DIR :			
			LOG_TRACE('action = ACTION_PARENT_DIR' )
			self.close()


	def onClick( self, aControlId ):
		LOG_TRACE("MainMenu onclick(): control %d" % aControlId )
		if aControlId == LIST_ID_MAIN_MENU :
			pass

		elif aControlId == BUTTON_ID_FIRSTINSTALLATION : # First Installation
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( [ 'test11111111111111', 'test222222222222222', 'test33333333', 'test', '1' ] )
 			dialog.doModal( )

		elif aControlId == BUTTON_ID_INSTALLATION :
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_INSTALLATION )

		elif aControlId == BUTTON_ID_MEDIA_CENTER :
			self.mStartMediaCenter = True
			# command
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_MEDIACENTER )

		elif aControlId == BUTTON_ID_ANTENNA_SETUP : # Antenna Setup
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_ANTENNA_SETUP )

		elif aControlId == BUTTON_ID_CHANNEL_SEARCH : # Channel Search
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CHANNEL_SEARCH )

		elif aControlId == BUTTON_ID_EDIT_SATELLITE : # Edit Satellite
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_EDIT_SATELLITE )
			
		elif aControlId == BUTTON_ID_EDIT_TRANSPONDER : # Edit TransPonder
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_EDIT_TRANSPONDER )

		elif aControlId == BUTTON_ID_CONFIGURE : # Config
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CONFIGURE )

		elif aControlId == BUTTON_ID_CAS : # CAS
			#ToDO
			pass

		elif aControlId == BUTTON_ID_CHANNEL_LIST : #Channel List
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CHANNEL_LIST_WINDOW )

		elif aControlId == BUTTON_ID_ARCHIVE :
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW )

		elif aControlId == BUTTON_ID_SYSTEM_INFO :
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_SYSTEM_INFO )

		elif aControlId == BUTTON_ID_EPG :
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_EPG_WINDOW )
			
		elif aControlId == 20 :
			pass
			"""
			self.close()
			import pvr.Launcher
			pvr.Launcher.GetInstance().PowerOff()
			"""

 
	def onFocus( self, aControlId ):
		LOG_TRACE('')
		pass

