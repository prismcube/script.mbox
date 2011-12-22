import xbmc
import xbmcgui
import sys
from copy import deepcopy

import pvr.gui.windowmgr as winmgr
import pvr.gui.dialogmgr as diamgr
import pvr.tunerconfigmgr as configmgr
from  pvr.tunerconfigmgr import *
from pvr.gui.guiconfig import *

from pvr.gui.basewindow import SettingWindow
from pvr.gui.basewindow import Action
import pvr.elismgr


class AutomaticScan( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
		self.commander = pvr.elismgr.getInstance( ).getCommander( )
			
		self.initialized = False
		self.lastFocused = -1
		self.allsatellitelist = []
		self.selectedSatelliteIndex = 0


	def onInit(self):

		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.setHeaderLabel( 'Channel Scan' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )

		self.selectedSatelliteIndex = 0
		self.allsatellitelist = []
		
		self.allsatellitelist = self.commander.satellite_GetList( ElisEnum.E_SORT_INSERTED )
		self.loadFormattedSatelliteNameList()

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
	
		groupId = self.getGroupId( controlId )
		
		#Satellite
		if groupId == E_Input01 :
			dialog = xbmcgui.Dialog( )
			self.selectedSatelliteIndex = dialog.select('Select satellite', self.formattedList )
			self.initConfig( )

		#Start Search
		if groupId == E_Input02 :
			if self.selectedSatelliteIndex == 0 : #ToDO : All Channel Search
				print 'ToDO : All Chanenl Search'
			else :
				satelliteList = []
				satellite = self.configuredList[self.selectedSatelliteIndex -1]
				print 'longitude=%s bandtype=%s' %( satellite[E_CONFIGURE_SATELLITE_LONGITUDE], satellite[E_CONFIGURE_SATELLITE_BANDTYPE] )

				satelliteList.append( satellite )
	 			dialog = diamgr.getInstance().getDialog( diamgr.DIALOG_ID_CHANNEL_SEARCH )
	 			dialog.scanBySatellite( satelliteList )
	 			dialog.doModal( )
								
				#self.commander.channelscan_BySatellite( int(config[E_CONFIGURE_SATELLITE_LONGITUDE]), int(config[E_CONFIGURE_SATELLITE_BANDTYPE]))
				


	def onFocus( self, controlId ):
		if self.initialized == False :
			return
		if ( self.lastFocused != controlId ) :
			self.showDescription( controlId )
			self.lastFocused = controlId


	def initConfig( self ) :

		self.resetAllControl( )
		count = len( self.formattedList )
		
		if count <= 1 :
			hideControlIds = [ E_Input01, E_SpinEx01, E_SpinEx02, E_Input02 ]
			self.setVisibleControls( hideControlIds, False )
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Has no configured satellite' )

		else :
			self.addInputControl( E_Input01, 'Satellite', self.formattedList[self.selectedSatelliteIndex], None, 'Select satellite' )
			self.addEnumControl( E_SpinEx01, 'Network Search', 'Network Search' )
			self.addEnumControl( E_SpinEx02, 'Channel Search Mode', 'Channel Search Mode' )
			self.addLeftLabelButtonControl( E_Input02, 'Start Search', 'Start Search' )
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


	def loadFormattedSatelliteNameList( self ) :

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
		self.formattedList.append('All')

		for config in self.configuredList :
			self.formattedList.append( self.getFormattedName( int(config[E_CONFIGURE_SATELLITE_LONGITUDE]) ) )


