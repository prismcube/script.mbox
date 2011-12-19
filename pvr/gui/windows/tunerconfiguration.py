import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
import pvr.tunerconfigmgr as configmgr
from  pvr.tunerconfigmgr import *
from pvr.gui.guiconfig import *
from pvr.gui.basewindow import SettingWindow, setWindowBusy
from pvr.gui.basewindow import Action
from elisenum import ElisEnum
import pvr.elismgr
from elisproperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.windows.satelliteconfigdiseqc10 import SatelliteConfigDisEqC10
from pvr.gui.windows.satelliteconfigdiseqc11 import SatelliteConfigDisEqC11
from pvr.gui.windows.satelliteconfigonecable import SatelliteConfigOneCable
from pvr.gui.windows.satelliteconfigmotorizedusals import SatelliteConfigMotorizedUsals


E_MAIN_LIST_ID = 9000

class TunerConfiguration( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance( ).getCommander( )
		self.listItems= []
			
	def onInit( self ):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.tunerIndex = configmgr.getInstance().getCurrentTunerIndex( )
		if configmgr.getInstance().getCurrentTunerIndex( ) == E_TUNER_1 : 
			property = ElisPropertyEnum( 'Tuner1 Type' )
		elif configmgr.getInstance().getCurrentTunerIndex( ) == E_TUNER_2 :
			property = ElisPropertyEnum( 'Tuner2 Type' )
			
		self.tunertype = configmgr.getInstance( ).getCurrentTunerType( )
		
		headerLabel = 'Tuner %d Configuration' % ( self.tunerIndex + 1 )
		self.setHeaderLabel( headerLabel )
		
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Tuner %d Configuration : %s' % ( self.tunerIndex + 1, property.getPropStringByIndex( self.tunertype ) ) )
		
		self.initConfig( )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )		


	def onAction( self, action ):

		actionId = action.getId( )
		focusId = self.getFocusId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_PARENT_DIR :
			self.getControl( E_MAIN_LIST_ID ).reset( )
			self.close( )

		elif actionId == Action.ACTION_MOVE_LEFT or actionId == Action.ACTION_MOVE_RIGHT :			
			pass
	
		elif actionId == Action.ACTION_MOVE_UP :
			pass

		elif actionId == Action.ACTION_MOVE_DOWN :
			pass


	def onClick( self, controlId ):
		if controlId == E_MAIN_LIST_ID : 
			position = self.getControl( E_MAIN_LIST_ID ).getSelectedPosition( )

			configuredList = configmgr.getInstance().getConfiguredSatelliteList( )
			
			if ( len( configuredList ) ) == position or len( configuredList ) == 0 :
				dialog = xbmcgui.Dialog()
				satelliteList = configmgr.getInstance( ).getFormattedNameList( )
	 			ret = dialog.select('Select satellite', satelliteList )

	 			if ret >= 0 :
					configmgr.getInstance().addConfiguredSatellite( ret )
	 				self.reloadConfigedSatellite()
	 				

			else :		
				config = configuredList[ position ]
				if config != [] :
					configmgr.getInstance( ).setCurrentConfigIndex( position )
					self.resetAllControl( )
					import pvr.platform 
					scriptDir = pvr.platform.getPlatform().getScriptDir()
					
					if self.tunertype == E_DISEQC_1_0 :
						SatelliteConfigDisEqC10('satelliteconfiguration.xml', scriptDir).doModal()

					elif self.tunertype == E_DISEQC_1_1 :
						SatelliteConfigDisEqC11('satelliteconfiguration.xml', scriptDir).doModal()

					elif self.tunertype == E_ONE_CABLE :
						SatelliteConfigOneCable('satelliteconfiguration.xml', scriptDir).doModal()

					elif self.tunertype == E_MOTORIZED_1_2 :
						pass

					elif self.tunertype == E_MOTORIZED_USALS :
						SatelliteConfigMotorizedUsals('satelliteconfiguration.xml', scriptDir).doModal()

				
				else :
					print 'ERR : Can not find configured satellite'


	def onFocus( self, controlId ):
		pass


	def initConfig( self ):
		self.reloadConfigedSatellite()


	def reloadConfigedSatellite( self ):
		configuredList = []
		self.listItems = []

		configuredList = configmgr.getInstance( ).getConfiguredSatelliteList( )

		for config in configuredList :
			self.listItems.append( xbmcgui.ListItem( '%s' %configmgr.getInstance( ).getFormattedName( int ( config[ 2 ] ) ) ) )

		self.listItems.append( xbmcgui.ListItem( 'Add New Satellite' ) )
		self.getControl( E_MAIN_LIST_ID ).addItems( self.listItems )

		
