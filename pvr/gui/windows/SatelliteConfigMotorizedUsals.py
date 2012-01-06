import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.TunerConfigMgr as ConfigMgr
from pvr.gui.GuiConfig import *
from pvr.gui.BaseWindow import SettingWindow, Action


class SatelliteConfigMotorizedUsals( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )

	def onInit(self):
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		tunerIndex = ConfigMgr.GetInstance( ).GetCurrentTunerIndex( )
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'USALS configuration : Tuner %s' % ( tunerIndex + 1 ) )
	
		self.SetHeaderLabel( 'Motorize Configuration' )
		self.SetFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )

		self.AddInputControl( E_Input01, 'My Longitude', '100.0 E' )
		self.AddInputControl( E_Input02, 'My Latitude', '000.0 N' )
		self.AddLeftLabelButtonControl( E_Input03, 'Reference Position to Null' )
		self.AddLeftLabelButtonControl( E_Input04, 'Configure Satellites' )

		visibleControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04 ]
		hideControlIds = [ E_Input05, E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06 ]
			
		self.SetVisibleControls( visibleControlIds, True )
		self.SetEnableControls( visibleControlIds, True )

		self.SetVisibleControls( hideControlIds, False )
		
		self.InitControl( )
		
	def onAction( self, aAction ):
		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			self.close( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			pass
			
		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )


	def onClick( self, aControlId ):
		groupId = self.GetGroupId( aControlId )

		# My Longitude
		if groupId == E_Input01 :
			pass

		# My Latitude
		elif groupId == E_Input02 :
			pass
			
		# Reference Position to Null
		elif groupId == E_Input03 :
			pass
			
		# Configure Satellites
		elif groupId == E_Input04 :
			self.ResetAllControl( )
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_TUNER_CONFIGURATION )
			
	def onFocus( self, controlId ):
		pass

