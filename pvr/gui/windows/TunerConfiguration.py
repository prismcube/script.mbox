import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.TunerConfigMgr as ConfigMgr
from  pvr.TunerConfigMgr import *
from pvr.gui.GuiConfig import *
from pvr.gui.BaseWindow import SettingWindow, Action
import pvr.ElisMgr

from pvr.gui.windows.SatelliteConfigDisEqc10 import SatelliteConfigDisEqC10
from pvr.gui.windows.SatelliteConfigDisEqc11 import SatelliteConfigDisEqC11
from pvr.gui.windows.SatelliteConfigMotorized12 import SatelliteConfigMotorized12
from pvr.gui.windows.SatelliteConfigMotorizedUsals import SatelliteConfigMotorizedUsals

E_MAIN_LIST_ID = 9000

class TunerConfiguration( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs)
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.listItems= []
			
	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		self.tunerIndex = ConfigMgr.GetInstance().GetCurrentTunerIndex( )

		if self.tunerIndex == E_TUNER_1 :
			property = ElisPropertyEnum( 'Tuner1 Type', self.mCommander )
		elif self.tunerIndex == E_TUNER_2 : 
			property = ElisPropertyEnum( 'Tuner2 Type', self.mCommander )
		else :
			print 'Error : unknown Tuner'
			property = ElisPropertyEnum( 'Tuner1 Type', self.mCommander )
			
		headerLabel = 'Tuner %d Configuration' % ( self.tunerIndex + 1 )
		self.SetHeaderLabel( headerLabel )
		self.SetFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )
		
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Tuner %d Configuration : %s' % ( self.tunerIndex + 1, property.GetPropString( ) ) )
		self.InitConfig( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
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


	def onClick( self, aControlId ):
		if aControlId == E_MAIN_LIST_ID : 
			position = self.getControl( E_MAIN_LIST_ID ).getSelectedPosition( )
			
			configuredList = ConfigMgr.GetInstance().GetConfiguredSatelliteList( )
			
			if ( len( configuredList ) ) == position or len( configuredList ) == 0 :
				dialog = xbmcgui.Dialog()
				satelliteList = ConfigMgr.GetInstance( ).GetFormattedNameList( )
	 			ret = dialog.select('Select satellite', satelliteList )

	 			if ret >= 0 :
					ConfigMgr.GetInstance().AddConfiguredSatellite( ret )
	 				self.ReloadConfigedSatellite()
	 				
			else :		
				config = configuredList[ position ]
				if config != [] :
					ConfigMgr.GetInstance( ).SetCurrentConfigIndex( position )
					self.ResetAllControl( )
					tunertype = ConfigMgr.GetInstance( ).GetCurrentTunerType( )
					
					import pvr.Platform 
					scriptDir = pvr.Platform.GetPlatform().GetScriptDir()
					
					if tunertype == E_DISEQC_1_0 :
						SatelliteConfigDisEqC10('SatelliteConfiguration.xml', scriptDir).doModal()

					elif tunertype == E_DISEQC_1_1 :
						SatelliteConfigDisEqC11('SatelliteConfiguration.xml', scriptDir).doModal()

					elif tunertype == E_ONE_CABLE :
						pass

					elif tunertype == E_MOTORIZED_1_2 :
						SatelliteConfigMotorized12('SatelliteConfiguration.xml', scriptDir).doModal()

					elif tunertype == E_MOTORIZED_USALS :
						SatelliteConfigMotorizedUsals('SatelliteConfiguration.xml', scriptDir).doModal()

				
				else :
					print 'ERR : Can not find configured satellite'


	def onFocus( self, aControlId ):
		pass


	def InitConfig( self ):
		self.ReloadConfigedSatellite()


	def ReloadConfigedSatellite( self ):
		configuredList = []
		self.listItems = []

		configuredList = ConfigMgr.GetInstance( ).GetConfiguredSatelliteList( )

		for config in configuredList :
			self.listItems.append( xbmcgui.ListItem( '%s' % ConfigMgr.GetInstance( ).GetFormattedName( config.mSatelliteLongitude, config.mBandType ) ) )

		self.listItems.append( xbmcgui.ListItem( 'Add New Satellite' ) )
		self.getControl( E_MAIN_LIST_ID ).addItems( self.listItems )

		
