import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
import pvr.tunerconfigmgr as configmgr
from pvr.tunerconfigmgr import *
from pvr.gui.guiconfig import *

from pvr.gui.basewindow import SettingWindow
from pvr.gui.basewindow import Action
from pvr.gui.windows.onecableconfiguration2 import OneCableConfiguration2
from pvr.gui.windows.satelliteconfigsimple import SatelliteConfigSimple

MAX_SATELLITE_CNT = 4

class OneCableConfiguration( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
		self.satelliteCount = 0
		self.satellitelist = []
		

	def onInit( self ):
		self.setHeaderLabel( 'OneCable Configuration' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'OneCable configuration' )

		self.currentSatellite = configmgr.getInstance( ).getConfiguredSatellitebyIndex( 0 )
		self.loadConfigedSatellite( )

		self.addLeftLabelButtonControl( E_Input01, 'Configure System' )
		
		listitem = []
		for i in range( self.satelliteCount ) :
			listitem.append( '%d' % ( i + 1 ) )

		self.addUserEnumControl( E_SpinEx01, 'Number of Satellite', listitem, 0 )

		startId = E_Input02
		for i in range( MAX_SATELLITE_CNT ) :
			self.addInputControl( startId, 'Satellite %d' % ( i + 1 ), self.satellitelist[i] )
			startId += 100
		
		self.initControl( )
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
					satellite = configmgr.getInstance( ).getConfiguredSatellitebyIndex( i + 1 )
					satellite[E_CONFIGURE_SATELLITE_IS_ONECABLE] = self.currentSatellite[E_CONFIGURE_SATELLITE_IS_ONECABLE]
					satellite[E_CONFIGURE_SATELLITE_ONECABLE_PIN] = self.currentSatellite[E_CONFIGURE_SATELLITE_ONECABLE_PIN]
					satellite[E_CONFIGURE_SATELLITE_ONECABLE_MDU] = self.currentSatellite[E_CONFIGURE_SATELLITE_ONECABLE_MDU]
					satellite[E_CONFIGURE_SATELLITE_ONECABLE_LO_FREQ1] = self.currentSatellite[E_CONFIGURE_SATELLITE_ONECABLE_LO_FREQ1]
					satellite[E_CONFIGURE_SATELLITE_ONECABLE_LO_FREQ2] = self.currentSatellite[E_CONFIGURE_SATELLITE_ONECABLE_LO_FREQ2]
					satellite[E_CONFIGURE_SATELLITE_ONECABLE_UBSLOT] = self.currentSatellite[E_CONFIGURE_SATELLITE_ONECABLE_UBSLOT]
					satellite[E_CONFIGURE_SATELLITE_ONECABLE_UBFREQ] = self.currentSatellite[E_CONFIGURE_SATELLITE_ONECABLE_UBFREQ]

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

		if groupId == E_Input01 :
			position = self.getControlIdToListIndex( groupId ) - 2
			configmgr.getInstance( ).setOneCableSatelliteCount( position + 1 )
			self.resetAllControl( )
			import pvr.platform 
			scriptDir = pvr.platform.getPlatform().getScriptDir()
			OneCableConfiguration2('onecableconfiguration2.xml', scriptDir).doModal()
		
		elif groupId == E_SpinEx01 :
			self.disableControl( )

		else :
			position = self.getControlIdToListIndex( groupId ) - 2
			configmgr.getInstance( ).setCurrentConfigIndex( position )

			self.resetAllControl( )
				
			import pvr.platform 
			scriptDir = pvr.platform.getPlatform().getScriptDir()
			SatelliteConfigSimple('satelliteconfiguration.xml', scriptDir).doModal()
			
	def onFocus( self, controlId ):
		pass


	def disableControl( self ): 
		for i in range( MAX_SATELLITE_CNT ) :
			if ( self.getSelectedIndex( E_SpinEx01 ) + 1 ) > i :
				self.setEnableControl( self.getListIndextoControlId( 2 + i ), True )
				self.setVisibleControl( self.getListIndextoControlId( 2 + i ), True )
			else :
				self.setEnableControl( self.getListIndextoControlId( 2 + i ), False )
				self.setVisibleControl( self.getListIndextoControlId( 2 + i ), False ) 
		
		
	def loadConfigedSatellite( self ):
		configuredList = []

		configuredList = configmgr.getInstance( ).getConfiguredSatelliteList( )
		self.satelliteCount = len( configuredList )

		for i in range( MAX_SATELLITE_CNT ) :
			if i < self.satelliteCount :
				self.satellitelist.append( configmgr.getInstance( ).getFormattedName( int( configuredList[i][2] ), int( configuredList[i][3] ) ) )
			else :
				self.satellitelist.append( '' ) # dummy Data