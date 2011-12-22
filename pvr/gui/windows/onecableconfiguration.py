import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
import pvr.tunerconfigmgr as configmgr
from pvr.gui.guiconfig import *

from pvr.gui.basewindow import SettingWindow
from pvr.gui.basewindow import Action
from pvr.gui.windows.onecableconfiguration2 import OneCableConfiguration2

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
			self.resetAllControl( )
			import pvr.platform 
			scriptDir = pvr.platform.getPlatform().getScriptDir()
			OneCableConfiguration2('onecableconfiguration2.xml', scriptDir).doModal()
		
		elif groupId == E_SpinEx01 :
			self.disableControl( )
			
			
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
				self.satellitelist.append( configmgr.getInstance( ).getFormattedName( int ( configuredList[i][2] ) ) )
			else :
				self.satellitelist.append( '' ) # dummy Data