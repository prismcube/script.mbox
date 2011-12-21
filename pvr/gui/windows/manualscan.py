import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
import pvr.tunerconfigmgr as configmgr
from  pvr.tunerconfigmgr import *
from pvr.gui.guiconfig import *

from pvr.gui.basewindow import SettingWindow
from pvr.gui.basewindow import Action


class ManualScan( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
		self.commander = pvr.elismgr.getInstance( ).getCommander( )
			
		self.initialized = False
		self.lastFocused = -1
		self.selectedIndex = 0
		self.allsatellitelist = []		


	def onInit(self):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.setHeaderLabel( 'Manual Scan' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )

		self.selectedIndex = 0
		self.allsatellitelist = []
		
		self.allsatellitelist = self.commander.satellite_GetList( ElisEnum.E_SORT_INSERTED )
		self.loadFormattedNameList()
		
		self.initConfig( )
		
		self.showDescription( self.getFocusId( ) )
		self.initialized = True

		
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
			self.showDescription( focusId )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.controlDown( )
			self.showDescription( focusId )
			


	def onClick( self, controlId ):
		#Satellite
		if groupId == E_Input01 :
			dialog = xbmcgui.Dialog( )
			self.selectedIndex = dialog.select('Select satellite', self.formattedList )
			self.initConfig( )

			

	def onFocus( self, controlId ):
		if self.initialized == False :
			return
		if ( self.lastFocused != controlId ) :
			self.showDescription( controlId )
			self.lastFocused = controlId


	def initConfig( self ) :

		self.resetAllControl( )	

		count = len( self.formattedList )
		
		if count <= 0 :
			hideControlIds = [ E_Input01, E_Input02, E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06 ]
			self.setVisibleControls( hideControlIds, False )
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Has no configured satellite' )

		else :
			self.addInputControl( E_Input01, 'Satellite', self.formattedList[self.selectedIndex], None, 'Select satellite' )
			self.addInputControl( E_Input02, 'Transponder Frequency', '11111', None, 'Select Transponder Frequency' )
			self.addEnumControl( E_SpinEx01, 'DVB Type', 'Select DVB type' )
			self.addEnumControl( E_SpinEx02, 'FEC', 'Select FEC' )
			self.addEnumControl( E_SpinEx03, 'Polarisation', 'Select Polarization' )
			self.addEnumControl( E_SpinEx04, 'Symbol Rate', 'Select Symbol Rate' )
			self.addEnumControl( E_SpinEx05, 'Network Search', 'Select Network Search' )
			self.addEnumControl( E_SpinEx06, 'Channel Search Mode', 'Network Search' )			
			self.addLeftLabelButtonControl( E_Input03, 'Start Search', 'Start Search' )
			self.initControl( )


	def getFormattedName( self, longitude ) :
	
		found = False	

		for satellite in self.allsatellitelist :
			if longitude == int( satellite[0] ) :
				found = True
				break

		if found == True :
			dir = 'E'

			tmpLongitude  = longitude
			if tmpLongitude > 1800 :
				dir = 'W'
				tmpLongitude = 3600 - longitude

			formattedName = '%d.%d %s %s' %( int( tmpLongitude/10 ), tmpLongitude%10, dir, satellite[2] )
			return formattedName

		return 'UnKnown'


	def loadFormattedNameList( self ) :

		configuredList1 = []
		configuredList1 = self.commander.satelliteconfig_GetList( E_TUNER_1 )		

		configuredList2 = []
		configuredList2 = self.commander.satelliteconfig_GetList( E_TUNER_2 )		

		property = ElisPropertyEnum( 'Tuner2 Signal Config', self.commander )

		self.configuredList = deepcopy( configuredList1 )
		
		if property.getProp( ) == E_DIFFERENT_TUNER :
			for config in configuredList2 :
				find = False
				for compare in configuredList1 :
					if config[E_CONFIGURE_SATELLITE_LONGITUDE] == compare[E_CONFIGURE_SATELLITE_LONGITUDE] :
						find = True
						break

				if find == False :
					self.configuredList.append( config )


		self.formattedList = []
		for config in self.configuredList :
			self.formattedList.append( self.getFormattedName( int(config[E_CONFIGURE_SATELLITE_LONGITUDE]) ) )
	
