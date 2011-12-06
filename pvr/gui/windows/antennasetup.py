
import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import SettingWindow, setWindowBusy
from pvr.gui.basewindow import Action
import pvr.elismgr
from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.guiconfig import *

E_MAIN_GROUP_ID		= 9000

class AntennaSetup(SettingWindow):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance().getCommander( )
			
		self.ctrlMainGroup = None
		self.initialized = False
		self.lastFocused = -1

	def onInit(self):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.ctrlMainGroup = self.getControl( E_MAIN_GROUP_ID )
		self.ctrlMainGroup.setVisible(False)

		self.setHeaderLabel( 'Antenna & Satellite Setup' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )

		self.addEnumControl( E_SpinEx01, 'Tuner2 Connect Type' , 'Select tuner 2 connection type.')
		self.addEnumControl( E_SpinEx02, 'Tuner2 Signal Config', 'Select tuner 2 configuration.' )
		self.addEnumControl( E_SpinEx03, 'Tuner1 Type', 'Setup tuner 1' )
		self.addEnumControl( E_SpinEx04, 'Tuner2 Type', 'Setup tuner 2' )

		#visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
		#self.setVisibleControls( visibleControlIds, True )
		#self.setEnableControls( visibleControlIds, True )

		self.initControl( )
		self.showDescription( self.getFocusId( ) )
		self.disableControl( )
		self.initialized = True
		self.ctrlMainGroup.setVisible(True)
		
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

		elif actionId == Action.ACTION_MOVE_LEFT or actionId == Action.ACTION_MOVE_RIGHT:			
			if( ( focusId % 10 ) == 2 ) :
				self.setFocusId( focusId - 1 )
			elif( ( focusId % 10 ) == 1 ) :
				self.setFocusId( focusId + 1 )				

		elif actionId == Action.ACTION_MOVE_UP :
			self.controlUp( )
			self.showDescription( focusId )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.controlDown( )
			self.showDescription( focusId )


	def onClick( self, controlId ):
		self.disableControl( )

		
	def onFocus( self, controlId ):
		if self.initialized == False :
			return
		if ( self.lastFocused != controlId ) :
			self.showDescription( controlId )
			self.lastFocused = controlId

	def disableControl( self ):
		selectedIndex1 = self.getSelectedIndex( E_SpinEx01 )
		if ( selectedIndex1 == 1 ) :
			self.setEnableControl( E_SpinEx02, False )
			self.getControl( E_SpinEx02 + 3 ).selectItem( 0 )
		else :
			self.setEnableControl( E_SpinEx02, True )

		selectedIndex2 = self.getSelectedIndex( E_SpinEx02 )	
		if ( selectedIndex2 == 0 ) :
			self.setEnableControl( E_SpinEx04, False )
			self.getControl( E_SpinEx04 + 3 ).selectItem( self.getSelectedIndex( E_SpinEx03 ) )
		else :
			self.setEnableControl( E_SpinEx04, True)

