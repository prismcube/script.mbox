import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
import pvr.tunerconfigmgr as configmgr
from pvr.gui.basewindow import SettingWindow, setWindowBusy
from pvr.gui.basewindow import Action
from pvr.elisevent import ElisEnum
import pvr.elismgr
from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.guiconfig import *

E_MAIN_LIST_ID = 9000

class TunerConfiguration(SettingWindow):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance().getCommander( )
			
		self.initialized = False
		#self.lastFocused = -1

		#self.listItems = [ '19.2 E ASTRA1', 'TEST SATELLITE #1', 'TEST SATELLITE #2', 'TEST SATELLITE #3' ]
		self.tunerType = 'DiSEqC 1.0'

	def onInit(self):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		configmgr.getInstance().load( );
		
		self.tunerIndex = configmgr.getInstance().getCurrentTunerIndex( )
		print 'Tunserconfiguration:onInit tuner index=%d' %self.tunerIndex
		headerLabel = 'Tuner %d Configuration' % ( self.tunerIndex + 1 )
		print 'Tunserconfiguration:onInit headerLabel=%s' %headerLabel
		self.setHeaderLabel( headerLabel )

		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Tuner Configuration : DisEqc 1.0'  )
		
		self.initConfig( )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )		


		'''
		self.addEnumControl( E_SpinEx01, 'Tuner2 Connect Type' , 'Select tuner 2 connection type.' )
		self.addEnumControl( E_SpinEx02, 'Tuner2 Signal Config', 'Select tuner 2 configuration.' )
		self.addEnumControl( E_SpinEx03, 'Tuner1 Type', 'Setup tuner 1.' )
		self.addEnumControl( E_SpinEx04, 'Tuner2 Type', 'Setup tuner 2.' )
		self.addLeftLabelButtonControl( E_Input01, 'Satellite Configure', 'Go to Setellite Setup.' )

		self.initControl( )
		self.showDescription( self.getFocusId( ) )
		self.disableControl( )
		self.initialized = True
		'''


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

		elif actionId == Action.ACTION_MOVE_LEFT or actionId == Action.ACTION_MOVE_RIGHT:			
			pass

			
		elif actionId == Action.ACTION_MOVE_UP :
			pass

			
		elif actionId == Action.ACTION_MOVE_DOWN :
			pass


	def onClick( self, controlId ):
		if controlId == E_MAIN_LIST_ID : 
			position = self.getControl( E_MAIN_LIST_ID ).getSelectedPosition()

			configuredList = configmgr.getInstance().getConfiguredSatellite( )

			if ( len( configuredList ) ) == position or len( configuredList ) == 0 :
				# ToDO : Show add new saatellite Window
				print 'ToDO : Show add new saatellite Window'

			else :

				config = configuredList[ position ]

				if config != [] :
					configmgr.getInstance().setCurrentLongitue( int( config[ 2 ] ) ) #config[2] == longitude
					winmgr.getInstance().showWindow( winmgr.WIN_ID_SATELLITE_CONFIGURATION )
				else :
					print 'ERR : Can not find configured satellite'



	def onFocus( self, controlId ):
		pass


	def initConfig( self ):

		configuredList = []
		satelliteList = []

		self.listItems = []

		print 'Tunserconfiguration:initConfig tuner index=%d' %self.tunerIndex

		configuredList = configmgr.getInstance().getConfiguredSatellite( )

		for config in configuredList :
			print 'config tunerindex= %d' %int(config[0])
			self.listItems.append( xbmcgui.ListItem('%s' %configmgr.getInstance().getFormattedName( int ( config[2] ) ) ) )


		self.listItems.append( xbmcgui.ListItem( 'Add New Satellite' ) )
		self.getControl( E_MAIN_LIST_ID ).addItems( self.listItems )


		
