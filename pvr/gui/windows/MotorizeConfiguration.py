import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
import pvr.tunerconfigmgr as configmgr
from pvr.gui.guiconfig import *

from pvr.gui.basewindow import SettingWindow
from pvr.gui.basewindow import Action


class MotorizeConfiguration( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
		self.tunerIndex = 0

	def onInit(self):
		self.setHeaderLabel( 'Motorize Configuration' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )

		self.addInputControl( E_Input01, 'My Longitude', '100.0 E' )
		self.addInputControl( E_Input02, 'My Latitude', '000.0 N' )
		self.addLeftLabelButtonControl( E_Input03, 'Reference Position to Null' )
		self.addLeftLabelButtonControl( E_Input04, 'Configure Satellites' )

		self.tunerIndex = configmgr.getInstance( ).getCurrentTunerIndex( )
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'USALS configuration : Tuner %s' % ( self.tunerIndex + 1 ) )

		visibleControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04 ]
		hideControlIds = [ E_Input05, E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06 ]
			
		self.setVisibleControls( visibleControlIds, True )
		self.setEnableControls( visibleControlIds, True )

		self.setVisibleControls( hideControlIds, False )
		
		self.initControl( )
		
	def onAction( self, action ):

		actionId = action.getId( )
		focusId = self.getFocusId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.resetAllControl( )
			self.close( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			pass
			
		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass

		elif actionId == Action.ACTION_MOVE_UP :
			self.controlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.controlDown( )


	def onClick( self, controlId ):
		groupId = self.getGroupId( controlId )

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
			self.resetAllControl( )
			winmgr.getInstance().showWindow( winmgr.WIN_ID_TUNER_CONFIGURATION )
			
	def onFocus( self, controlId ):
		pass

