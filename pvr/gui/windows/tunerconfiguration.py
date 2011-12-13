import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
import pvr.tunerconfigmgr as configmgr
from pvr.gui.guiconfig import *
from pvr.gui.basewindow import SettingWindow, setWindowBusy
from pvr.gui.basewindow import Action
from pvr.elisevent import ElisEnum
import pvr.elismgr
from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt


E_MAIN_LIST_ID = 9000

class TunerConfiguration( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance( ).getCommander( )
			
		#self.initialized = False

	def onInit( self ):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		configmgr.getInstance( ).load( );
		
		self.tunerIndex = configmgr.getInstance().getCurrentTunerIndex( ) + 1
		self.tunertype = E_LIST_TUNER_TYPE[ configmgr.getInstance( ).getCurrentTunerType( ) ]
		headerLabel = 'Tuner %d Configuration' % ( self.tunerIndex )
		self.setHeaderLabel( headerLabel )
		
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Tuner %d Configuration : %s' % ( self.tunerIndex, self.tunertype ) )
		
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

			configuredList = configmgr.getInstance().getConfiguredSatellite( )

			if ( len( configuredList ) ) == position or len( configuredList ) == 0 :
				# ToDO : Show add new saatellite Window
				print 'ToDO : Show add new saatellite Window'

			else :
				config = configuredList[ position ]
				if config != [] :
					configmgr.getInstance( ).setCurrentLongitue( int( config[ 2 ] ) ) #config[2] == longitude
					winmgr.getInstance( ).showWindow( winmgr.WIN_ID_SATELLITE_CONFIGURATION )
				else :
					print 'ERR : Can not find configured satellite'


	def onFocus( self, controlId ):
		pass

	def initConfig( self ):
		configuredList = []
		satelliteList = []
		self.listItems = []

		configuredList = configmgr.getInstance( ).getConfiguredSatellite( )

		for config in configuredList :
			self.listItems.append( xbmcgui.ListItem( '%s' %configmgr.getInstance( ).getFormattedName( int ( config[ 2 ] ) ) ) )

		self.listItems.append( xbmcgui.ListItem( 'Add New Satellite' ) )
		self.getControl( E_MAIN_LIST_ID ).addItems( self.listItems )


		
