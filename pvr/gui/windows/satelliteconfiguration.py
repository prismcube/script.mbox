import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
import pvr.tunerconfigmgr as configmgr
from pvr.gui.basewindow import SettingWindow, setWindowBusy
from pvr.gui.basewindow import Action
import pvr.elismgr
from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.guiconfig import *



class SatelliteConfiguration( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance().getCommander( )
			
		self.tunerType = 0
		self.currentSatellite = 0
		self.longitude = 0
		self.currentSatellite = []

	def onInit( self ):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.tunerIndex = configmgr.getInstance( ).getCurrentTunerIndex( ) + 1
		self.tunertype = E_LIST_TUNER_TYPE[ configmgr.getInstance( ).getCurrentTunerType( ) ]
		self.longitude = configmgr.getInstance( ).getCurrentLongitue( )
		self.currentSatellite = configmgr.getInstance( ).getCurrentConfiguredSatellite( )
		
		self.setHeaderLabel( 'Satellite Configuration' )
		
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Satellite Config : Tuner %s - %s' % ( self.tunerIndex, self.tunertype ) )

		self.initConfig( )
		self.initControl( )
		#self.disableControl( )
		#self.initialized = True

		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )
		
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
			pass
			
		elif actionId == Action.ACTION_MOVE_UP :
			self.controlUp( )
			#self.showDescription( focusId )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.controlDown( )
			#self.showDescription( focusId )


	def onClick( self, controlId ):
		#winmgr.getInstance().showWindow( winmgr.WIN_ID_TUNER_CONFIGURATION )
		pass

		
	def onFocus( self, controlId ):
		pass

	def initConfig( self ) :
	
		self.addInputControl( E_Input01, 'Satellite' , configmgr.getInstance( ).getFormattedName( self.longitude ), None )
		self.addUserEnumControl( E_SpinEx01, 'LNB Setting', self.currentSatellite[9] )
		self.addInputControl( E_Input02, 'LNB Frequency', '9750 / 10600 / 11700 (MHz)', None )
		#self.addUserEnumControl( E_SpinEx02, '22KHz Control', self.currentSatellite[] )

	
		'''
		self.addUserEnumControl( E_SpinEx01, 'DiSEqC 1.0 Switch', USER_ENUM_LIST_DISEQC_1_0_SWITCH )
		self.addUserEnumControl( E_SpinEx02, 'DiSEqC Repeat', USER_ENUM_LIST_ON_OFF )
		self.addUserEnumControl( E_SpinEx03, 'Transponder', USER_ENUM_LIST_TRANSPONDER )
		self.addLeftLabelButtonControl( E_Input05, 'Save', None )
		
		visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input05 ]
		self.setVisibleControls( visibleControlIds, True )
		self.setEnableControls( visibleControlIds, True )

		hideControlIds = [ E_SpinEx04 ]
		self.setVisibleControls( hideControlIds, False )
		'''	
		#disableControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04 ]



