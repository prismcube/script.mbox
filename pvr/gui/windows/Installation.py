import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
from pvr.gui.BaseWindow import BaseWindow, Action

BUTTON_ID_FIRSTINSTALLATION		= 90101
BUTTON_ID_ANTENNA_SETUP			= 90102
BUTTON_ID_CHANNEL_SEARCH		= 90103
BUTTON_ID_EDIT_SATELLITE		= 90104
BUTTON_ID_EDIT_TRANSPONDER		= 90105
BUTTON_ID_CONFIGURE				= 90106
BUTTON_ID_CAS					= 90107

class Installation( BaseWindow ):
	def __init__( self, *args, **kwargs ):
		BaseWindow.__init__( self, *args, **kwargs )


	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.close( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.close( )


	def onClick( self, aControlId ) :
		if aControlId == BUTTON_ID_FIRSTINSTALLATION : # First Installation
			pass

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
			pass

 
	def onFocus( self, aControlId ):
		pass
