import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as winmgr
import pvr.TunerConfigMgr as configmgr
from pvr.TunerConfigMgr import *
from pvr.gui.GuiConfig import *

from pvr.gui.BaseWindow import SettingWindow
from pvr.gui.BaseWindow import Action
from pvr.gui.windows.OnecableConfiguration2 import OnecableConfiguration2
from pvr.gui.windows.SatelliteConfigSimple import SatelliteConfigSimple

MAX_SATELLITE_CNT = 4

class OnecableConfiguration( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
		self.satelliteCount = 0
		self.satellitelist = []
		

	def onInit( self ):
		self.setHeaderLabel( 'OneCable Configuration' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'OneCable configuration' )

		self.currentSatellite = configmgr.getInstance( ).GetConfiguredSatellitebyIndex( 0 )
		self.loadConfigedSatellite( )

		self.AddLeftLabelButtonControl( E_Input01, 'Configure System' )
		
		listitem = []
		for i in range( self.satelliteCount ) :
			listitem.append( '%d' % ( i + 1 ) )

		self.AddUserEnumControl( E_SpinEx01, 'Number of Satellite', listitem, 0 )

		startId = E_Input02
		for i in range( MAX_SATELLITE_CNT ) :
			self.AddInputControl( startId, 'Satellite %d' % ( i + 1 ), self.satellitelist[i] )
			startId += 100
		
		self.InitControl( )
		self.getControl( E_SpinEx01 + 3 ).selectItem( self.satelliteCount - 1 )
		self.disableControl( )

				
	def onAction( self, action ):

		actionId = action.getId( )
		focusId = self.getFocusId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			if self.satelliteCount > 1 :
				for i in range( self.satelliteCount - 1 ) :
					satellite = configmgr.getInstance( ).GetConfiguredSatellitebyIndex( i + 1 )
					satellite[E_CONFIGURE_SATELLITE_IS_ONECABLE] = self.currentSatellite[E_CONFIGURE_SATELLITE_IS_ONECABLE]
					satellite[E_CONFIGURE_SATELLITE_ONECABLE_PIN] = self.currentSatellite[E_CONFIGURE_SATELLITE_ONECABLE_PIN]
					satellite[E_CONFIGURE_SATELLITE_ONECABLE_MDU] = self.currentSatellite[E_CONFIGURE_SATELLITE_ONECABLE_MDU]
					satellite[E_CONFIGURE_SATELLITE_ONECABLE_LO_FREQ1] = self.currentSatellite[E_CONFIGURE_SATELLITE_ONECABLE_LO_FREQ1]
					satellite[E_CONFIGURE_SATELLITE_ONECABLE_LO_FREQ2] = self.currentSatellite[E_CONFIGURE_SATELLITE_ONECABLE_LO_FREQ2]
					satellite[E_CONFIGURE_SATELLITE_ONECABLE_UBSLOT] = self.currentSatellite[E_CONFIGURE_SATELLITE_ONECABLE_UBSLOT]
					satellite[E_CONFIGURE_SATELLITE_ONECABLE_UBFREQ] = self.currentSatellite[E_CONFIGURE_SATELLITE_ONECABLE_UBFREQ]

			self.ResetAllControl( )
			self.close( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )
			
		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )


	def onClick( self, controlId ):
		groupId = self.GetGroupId( controlId )

		if groupId == E_Input01 :
			position = self.GetControlIdToListIndex( groupId ) - 2
			configmgr.getInstance( ).SetOnecableSatelliteCount( position + 1 )
			self.ResetAllControl( )
			import pvr.Platform 
			scriptDir = pvr.Platform.getPlatform().GetScriptDir()
			OnecableConfiguration2('OnecableConfiguration2.xml', scriptDir).doModal()
		
		elif groupId == E_SpinEx01 :
			self.disableControl( )

		else :
			position = self.GetControlIdToListIndex( groupId ) - 2
			configmgr.getInstance( ).SetCurrentConfigIndex( position )

			self.ResetAllControl( )
				
			import pvr.Platform 
			scriptDir = pvr.Platform.getPlatform().GetScriptDir()
			SatelliteConfigSimple('satelliteconfiguration.xml', scriptDir).doModal()
			
	def onFocus( self, controlId ):
		pass


	def disableControl( self ): 
		for i in range( MAX_SATELLITE_CNT ) :
			if ( self.GetSelectedIndex( E_SpinEx01 ) + 1 ) > i :
				self.SetEnableControl( self.GetListIndextoControlId( 2 + i ), True )
				self.SetVisibleControl( self.GetListIndextoControlId( 2 + i ), True )
			else :
				self.SetEnableControl( self.GetListIndextoControlId( 2 + i ), False )
				self.SetVisibleControl( self.GetListIndextoControlId( 2 + i ), False ) 
		
		
	def loadConfigedSatellite( self ):
		configuredList = []

		configuredList = configmgr.getInstance( ).GetConfiguredSatelliteList( )
		self.satelliteCount = len( configuredList )

		for i in range( MAX_SATELLITE_CNT ) :
			if i < self.satelliteCount :
				self.satellitelist.append( configmgr.getInstance( ).GetFormattedName( int( configuredList[i][2] ), int( configuredList[i][3] ) ) )
			else :
				self.satellitelist.append( '' ) # dummy Data