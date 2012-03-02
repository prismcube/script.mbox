import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.GuiConfig import *
from pvr.gui.BaseWindow import BaseWindow, Action
from inspect import currentframe
import pvr.ElisMgr
from pvr.Util import LOG_TRACE, LOG_ERR, LOG_WARN, RunThread

LIST_ID_MAIN_MENU				= 9000
BUTTON_ID_INSTALLATION			= 90100
BUTTON_ID_ARCHIVE				= 90200
BUTTON_ID_EPG					= 90300
BUTTON_ID_CHANNEL_LIST			= 90400
BUTTON_ID_MEDIA_CENTER			= 90500
BUTTON_ID_SYSTEM_INFO			= 90600

BUTTON_ID_MEDIA_SETTINGS        = 90506

BUTTON_ID_FIRSTINSTALLATION		= 90101
BUTTON_ID_ANTENNA_SETUP			= 90102
BUTTON_ID_CHANNEL_SEARCH		= 90103
BUTTON_ID_EDIT_SATELLITE		= 90104
BUTTON_ID_EDIT_TRANSPONDER		= 90105
BUTTON_ID_CONFIGURE				= 90106
BUTTON_ID_CAS					= 90107


class MainMenu( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mStartMediaCenter = False


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		self.mCtrlMainMenu = self.getControl( LIST_ID_MAIN_MENU )
		if self.mStartMediaCenter == True :
			self.mCommander.AppMediaPlayer_Control( 0 )
			#WinMgr.GetInstance().CheckSkinChange( )
			self.mStartMediaCenter = False

	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )
		
		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_PARENT_DIR :			
			self.close( )


	def onClick( self, aControlId ) :
		LOG_TRACE("MainMenu onclick(): control %d" % aControlId )
		if aControlId == LIST_ID_MAIN_MENU :
			pass

		elif aControlId == BUTTON_ID_FIRSTINSTALLATION : # First Installation
			pass
			"""
			context = []
			context.append( ContextItem( 'test00000' ) )
			context.append( ContextItem( 'test11111111111111111111111111111111', E_TEST_FUNCTION_1 ) )
			context.append( ContextItem( 'test2222222', E_TEST_FUNCTION_2 ) )
			context.append( ContextItem( 'test333333333', E_TEST_FUNCTION_3 ) )
			context.append( ContextItem( 'test' ) )

			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context )
 			dialog.doModal( )

 			print 'dhkim test Selected Position = %d' % dialog.GetSelectedIndex( )
			"""
			
			#dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CHANNEL_JUMP )
			#dialog.SetDialogProperty( '0', 1005 )
			#dialog.doModal( )

			
		elif aControlId == BUTTON_ID_INSTALLATION :
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_INSTALLATION )

		elif aControlId == BUTTON_ID_MEDIA_CENTER or aControlId == BUTTON_ID_MEDIA_SETTINGS :
			self.mStartMediaCenter = True
			self.mCommander.AppMediaPlayer_Control( 1 )
			if aControlId == BUTTON_ID_MEDIA_CENTER :
				WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_MEDIACENTER )
			WinMgr.GetInstance().Reset( )
	
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
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CONDITIONAL_ACCESS )

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
		
