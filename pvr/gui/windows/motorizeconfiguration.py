import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
import pvr.tunerconfigmgr as configmgr
#from  pvr.tunerconfigmgr import *
from pvr.gui.guiconfig import *

from pvr.gui.basewindow import SettingWindow
from pvr.gui.basewindow import Action
#import pvr.elismgr
#from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt
#from pvr.elisevent import ElisEnum

#E_MAIN_GROUP_ID	= 9000

class MotorizeConfiguration( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
		self.tunerIndex = 0

	def onInit(self):
		self.setHeaderLabel( 'Motorize Configuration' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )

		self.addInputControl( E_Input01, 'My Longitude', '100.0 E', None )
		self.addInputControl( E_Input02, 'My Latitude', '000.0 N', None )
		self.addLeftLabelButtonControl( E_Input03, 'Reference Position to Null ', None )
		self.addLeftLabelButtonControl( E_Input04, 'Configure Satellites ', None)

		self.tunerIndex = configmgr.getInstance( ).getCurrentTunerIndex( ) + 1
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'USALS configuration : Tuner %s' % ( self.tunerIndex ) )
		
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
		if controlId == E_Input04 + 1 :
			self.resetAllControl( )
			winmgr.getInstance().showWindow( winmgr.WIN_ID_TUNER_CONFIGURATION )
			

	def onFocus( self, controlId ):
		pass

