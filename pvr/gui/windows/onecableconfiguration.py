import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
import pvr.tunerconfigmgr as configmgr
from pvr.gui.guiconfig import *

from pvr.gui.basewindow import SettingWindow
from pvr.gui.basewindow import Action


class OneCableConfiguration( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
		self.tunerIndex = 0
		self.satelliteCount = 0
		self.satelliteDrawCount = 0
		self.ctrlList = None
		self.satellitelist = []
		

	def onInit( self ):
		self.setHeaderLabel( 'OneCable Configuration' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'OneCable configuration' )
		
		self.loadConfigedSatellite( )
		self.satelliteDrawCount = self.satelliteCount
		self.initConfig( )
		self.getControl( E_SpinEx01 + 3 ).selectItem( self.satelliteDrawCount - 1 )
		
		
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

		if groupId == E_SpinEx01 :
			self.satelliteDrawCount = self.getSelectedIndex( E_SpinEx01 ) + 1
			self.resetAllControl( )
			#self.initConfig( )
			
			
	def onFocus( self, controlId ):
		pass


	def initConfig( self ):
		self.addLeftLabelButtonControl( E_Input01, 'Configure System', None )
		
		listitem = []
		for i in range( self.satelliteCount ) :
			listitem.append( '%d' % ( i + 1 ) )

		self.addUserEnumControl( E_SpinEx01, 'Number of Satellite', listitem, 0, None )

		startId = E_Input02
		for i in range( self.satelliteDrawCount ) :
			self.addInputControl( startId, 'Satellite %d' % ( i + 1 ), self.satellitelist[i], None, None )
			startId += 100
		
		hideControlIds = []
		while( startId >= 0 ) :
			hideControlIds.append( startId )
			if( startId == E_Input05 ) :
				break
			startId += 100
		self.setVisibleControls( hideControlIds, False )
		
		
		self.initControl( )
		

	def loadConfigedSatellite( self ):
		configuredList = []
		tmp = 0

		configuredList = configmgr.getInstance( ).getConfiguredSatelliteList( )
		self.satelliteCount = len( configuredList )

		for config in configuredList :
			tmp += 1
			self.satellitelist.append( configmgr.getInstance( ).getFormattedName( int ( config[ 2 ] ) ) )