import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.GuiConfig import *
from pvr.gui.BaseWindow import SettingWindow, Action
from ElisProperty import ElisPropertyEnum


class ChannelSearch( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		self.SetPipScreen( )
		self.SetSettingWindowLabel( 'Channel Scan' )

		self.AddInputControl( E_Input01, 'Automatic Scan', '', 'Running automatic scan.' )
		self.AddInputControl( E_Input02, 'Manual Scan', '', 'Running manual scan.' )

		self.InitControl( )
		self.ShowDescription( )
		self.mInitialized = True


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.ResetAllControl( )
			self.SetVideoRestore( )
			self.close( )
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			self.SetVideoRestore( )
			self.close( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )				

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			self.ShowDescription( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )
			self.ShowDescription( )


	def onClick( self, aControlId ) :
		groupId = self.GetGroupId( aControlId )
		if groupId == E_Input01 :
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_AUTOMATIC_SCAN )
			
		elif groupId == E_Input02 :
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MANUAL_SCAN )
				

	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return

		if self.mLastFocused != aControlId :
			self.ShowDescription( )
			self.mLastFocused = aControlId