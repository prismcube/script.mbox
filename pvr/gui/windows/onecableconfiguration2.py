import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
import pvr.tunerconfigmgr as configmgr
from pvr.gui.guiconfig import *

from pvr.gui.basewindow import SettingWindow
from pvr.gui.basewindow import Action


class OneCableConfiguration2( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
		self.satelliteCount = 0
		self.satellitelist = []
		

	def onInit( self ):
		self.tunerIndex = configmgr.getInstance( ).getCurrentTunerIndex( )
	
		self.setHeaderLabel( 'OneCable Configuration' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'OneCable configuration' )


		self.addEnumControl( E_SpinEx01, 'MDU' )
		self.addInputControl( E_Input01, 'Tuner %d PIN-Code' % ( self.tunerIndex + 1 ), '000', 0 )
		self.addUserEnumControl( E_SpinEx02, 'Tuner %d' % ( self.tunerIndex + 1 ), USER_ENUM_LIST_ON_OFF, 0 )
		self.addEnumControl( E_SpinEx03, 'EXR EXU SCR', 'Tuner %d Frequency' % ( self.tunerIndex + 1 ) )
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
			self.controlLeft( )
			
		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.controlRight( )

		elif actionId == Action.ACTION_MOVE_UP :
			self.controlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.controlDown( )


	def onClick( self, controlId ):
		groupId = self.getGroupId( controlId )
		self.controlSelect( )		

	def onFocus( self, controlId ):
		pass