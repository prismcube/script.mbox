import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.BaseWindow import BaseWindow, Action
import pvr.ElisMgr
from pvr.gui.GuiConfig import *

MENU_ID_FIRSTINSTALLATION		= 0
MENU_ID_ANTENNA_SETUP			= 1
MENU_ID_CHANNEL_SEARCH			= 2
MENU_ID_EDIT_SATELLITE			= 3
MENU_ID_EDIT_TRANSPONDER		= 4
MENU_ID_CONFIGURE				= 5
MENU_ID_CAS						= 6

class Installation( BaseWindow ):
	def __init__( self, *args, **kwargs ):
		BaseWindow.__init__( self, *args, **kwargs )

		self.leftGroupItems = [ 'First Installation', 'Antenna Setup', 'Channel Search', 'Edit Satellite', 'Edit Transponder', 'Configure', 'CAS' ]
		self.descriptionList	 = [ 'Desc First Installation', 'Desc Antenna Setup', 'Desc Channel Search', 'Desc Edit Satellite', 'Desc Edit Transponder', 'Desc Configure', 'Desc CAS' ]
		#self.icon = [ 'special://skin/backgrounds/appearance.jpg', 'special://skin/backgrounds/videos.jpg', 'special://skin/backgrounds/music.jpg', 'special://skin/backgrounds/pictures.jpg', 'special://skin/backgrounds/weather.jpg', 'special://skin/backgrounds/addons.jpg', 'special://skin/backgrounds/network.jpg' ]

		self.mCtrlLeftGroup = 0
		
		
	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId )

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( 'Installation' )
		
		groupItems = []
		
		for i in range( len( self.leftGroupItems ) ) :
			#groupItems.append( xbmcgui.ListItem( self.leftGroupItems[i], self.descriptionList[i], self.icon[i] ) )
			groupItems.append( xbmcgui.ListItem( self.leftGroupItems[i], self.descriptionList[i] ) )
			
		self.mCtrlLeftGroup = self.getControl( 9000 )
		self.mCtrlLeftGroup.addItems( groupItems )

		self.mCtrlImgVideoPos = self.getControl( 8899 )

		h = self.mCtrlImgVideoPos.getHeight()
		w = self.mCtrlImgVideoPos.getWidth()
		pos=list(self.mCtrlImgVideoPos.getPosition())
		x = pos[0]
		y = pos[1]
		#LOG_TRACE('==========h[%s] w[%s] x[%s] y[%s]'% (h,w,x,y) )

		ret = self.mCommander.Player_SetVIdeoSize( x, y, w, h )
		
	
	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.SetVideoRestore( )
			self.close( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.SetVideoRestore( )
			self.close( )


	def onClick( self, aControlId ) :
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		
		if selectedId == MENU_ID_FIRSTINSTALLATION : # First Installation
			pass

		elif selectedId == MENU_ID_ANTENNA_SETUP : # Antenna Setup
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_ANTENNA_SETUP )

		elif selectedId == MENU_ID_CHANNEL_SEARCH : # Channel Search
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CHANNEL_SEARCH )

		elif selectedId == MENU_ID_EDIT_SATELLITE : # Edit Satellite
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_EDIT_SATELLITE )
			
		elif selectedId == MENU_ID_EDIT_TRANSPONDER : # Edit TransPonder
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_EDIT_TRANSPONDER )

		elif selectedId == MENU_ID_CONFIGURE : # Config
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CONFIGURE )

		elif selectedId == MENU_ID_CAS : # CAS
			ret = self.mCommander.Cicam_IsInserted( CAS_SLOT_NUM_1 )
			if ret == True :
				WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CONDITIONAL_ACCESS )
			else :
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'ERROR', 'SMART card not inserted' )
	 			dialog.doModal( )

 
	def onFocus( self, aControlId ):
		pass
