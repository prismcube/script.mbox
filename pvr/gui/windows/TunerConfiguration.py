import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as winmgr
import pvr.TunerConfigMgr as configmgr
from  pvr.TunerConfigMgr import *
from pvr.gui.GuiConfig import *
from pvr.gui.BaseWindow import SettingWindow
from pvr.gui.BaseWindow import Action
from ElisEnum import ElisEnum
import pvr.ElisMgr
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.windows.satelliteconfigdiseqc10 import SatelliteConfigDisEqC10
from pvr.gui.windows.satelliteconfigdiseqc11 import SatelliteConfigDisEqC11
from pvr.gui.windows.satelliteconfigmotorized12 import SatelliteConfigMotorized12
from pvr.gui.windows.satelliteconfigmotorizedusals import SatelliteConfigMotorizedUsals


E_MAIN_LIST_ID = 9000

class TunerConfiguration( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs)
		self.mCommander = pvr.ElisMgr.getInstance( ).getCommander( )
		self.listItems= []
			
	def onInit( self ):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.tunerIndex = configmgr.getInstance().GetCurrentTunerIndex( )

		if self.tunerIndex == E_TUNER_1 :
			property = ElisPropertyEnum( 'Tuner1 Type', self.mCommander )
		elif self.tunerIndex == E_TUNER_2 : 
			property = ElisPropertyEnum( 'Tuner2 Type', self.mCommander )
		else :
			print 'Error : unknown Tuner'
			property = ElisPropertyEnum( 'Tuner1 Type', self.mCommander )
			
		headerLabel = 'Tuner %d Configuration' % ( self.tunerIndex + 1 )
		self.setHeaderLabel( headerLabel )
		
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Tuner %d Configuration : %s' % ( self.tunerIndex + 1, property.getPropString( ) ) )
		
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

			configuredList = configmgr.getInstance().GetConfiguredSatelliteList( )
			
			if ( len( configuredList ) ) == position or len( configuredList ) == 0 :
				dialog = xbmcgui.Dialog()
				satelliteList = configmgr.getInstance( ).GetFormattedNameList( )
	 			ret = dialog.select('Select satellite', satelliteList )

	 			if ret >= 0 :
					configmgr.getInstance().AddConfiguredSatellite( ret )
	 				self.reloadConfigedSatellite()
	 				

			else :		
				config = configuredList[ position ]
				if config != [] :
					configmgr.getInstance( ).SetCurrentConfigIndex( position )
					self.ResetAllControl( )
					import pvr.Platform 
					scriptDir = pvr.Platform.getPlatform().GetScriptDir()

					tunertype = configmgr.getInstance( ).GetCurrentTunerType( )
					
					if tunertype == E_DISEQC_1_0 :
						SatelliteConfigDisEqC10('satelliteconfiguration.xml', scriptDir).doModal()

					elif tunertype == E_DISEQC_1_1 :
						SatelliteConfigDisEqC11('satelliteconfiguration.xml', scriptDir).doModal()

					elif tunertype == E_ONE_CABLE :
						pass

					elif tunertype == E_MOTORIZED_1_2 :
						SatelliteConfigMotorized12('satelliteconfiguration.xml', scriptDir).doModal()

					elif tunertype == E_MOTORIZED_USALS :
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

		configuredList = configmgr.getInstance( ).GetConfiguredSatelliteList( )

		for config in configuredList :
			self.listItems.append( xbmcgui.ListItem( '%s' %configmgr.getInstance( ).GetFormattedName( int( config[ 2 ] ), int( config[ 3 ] ) ) ) )

		self.listItems.append( xbmcgui.ListItem( 'Add New Satellite' ) )
		self.getControl( E_MAIN_LIST_ID ).addItems( self.listItems )

		
