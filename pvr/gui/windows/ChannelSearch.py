
import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.GuiConfig import *
from ElisProperty import ElisPropertyEnum
import pvr.ElisMgr

from pvr.gui.BaseWindow import SettingWindow, Action

E_PIP_PICTURE_ID = 301

class ChannelSearch( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
			
	def onInit(self):
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		self.mCtrlImgVideoPos = self.getControl( E_PIP_PICTURE_ID )

		h = self.mCtrlImgVideoPos.getHeight( )
		w = self.mCtrlImgVideoPos.getWidth( )
		pos = list( self.mCtrlImgVideoPos.getPosition( ) )
		x = pos[0]
		y = pos[1]
		ret = self.mCommander.Player_SetVIdeoSize( x, y, w, h ) 

		self.SetSettingWindowLabel( 'Channel Scan' )

		self.AddInputControl( E_Input01, 'Automatic Scan', '', 'Running automatic scan.' )
		self.AddInputControl( E_Input02, 'Manual Scan', '', 'Running manual scan.' )

		self.InitControl( )
		self.ShowDescription( self.getFocusId( ) )
		self.mInitialized = True

		
	def onAction( self, aAction ):

		actionId = aAction.getId( )
		focusId = self.getFocusId( )

		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
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
			self.ShowDescription( focusId )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )
			self.ShowDescription( focusId )
			


	def onClick( self, aControlId ):
		groupId = self.GetGroupId( aControlId )
		if groupId == E_Input01 :
			if self.CheckConfiguredSatellite( ) == False :
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'ERROR', 'No Configured Satellite.' )
	 			dialog.doModal( )
			else :
				self.ResetAllControl( )
				WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_AUTOMATIC_SCAN )
			
		elif groupId == E_Input02 :
			if self.CheckConfiguredSatellite( ) == False :
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'ERROR', 'No Configured Satellite.' )
	 			dialog.doModal( )
				
			else :
				self.ResetAllControl( )
				WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_MANUAL_SCAN )
				

	def onFocus( self, aControlId ):
		if self.mInitialized == False :
			return

		if self.mLastFocused != aControlId :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId


	def CheckConfiguredSatellite( self ) :
		property = ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander )
		if property.GetProp( ) == E_TUNER_SEPARATED :
			configuredsatellite = self.mCommander.Satelliteconfig_GetList( E_TUNER_1 )
			for config in configuredsatellite :
				if config.mError < 0 :
					return False

			configuredsatellite = self.mCommander.Satelliteconfig_GetList( E_TUNER_2 )
			for config in configuredsatellite :
				if config.mError < 0 :
					return False

			return True
			
		elif property.GetProp( ) == E_TUNER_LOOPTHROUGH :
			configuredsatellite = self.mCommander.Satelliteconfig_GetList( E_TUNER_1 )
			for config in configuredsatellite :
				if config.mError < 0 :
					return False

			return True