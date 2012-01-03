import xbmc
import xbmcgui
import sys
from copy import deepcopy

import pvr.gui.WindowMgr as winmgr
import pvr.gui.dialogmgr as diamgr
import pvr.tunerconfigmgr as configmgr
from  pvr.tunerconfigmgr import *
from pvr.gui.guiconfig import *

from pvr.gui.basewindow import SettingWindow
from pvr.gui.basewindow import Action
import pvr.ElisMgr


class AutomaticScan( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
		self.mCommander = pvr.ElisMgr.getInstance( ).getCommander( )
			
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
		
		self.allsatellitelist = self.mCommander.satellite_GetList( ElisEnum.E_SORT_INSERTED )
		self.loadFormattedSatelliteNameList()

		self.initConfig( )

		self.ShowDescription( self.getFocusId( ) )
		self.initialized = True

		
	def onAction( self, action ):

		actionId = action.getId( )
		focusId = self.getFocusId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			self.close( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )				

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			self.ShowDescription( focusId )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )
			self.ShowDescription( focusId )
			


	def onClick( self, controlId ):
	
		groupId = self.GetGroupId( controlId )
		
		#Satellite
		if groupId == E_Input01 :
			dialog = xbmcgui.Dialog( )
			select =  dialog.select('Select satellite', self.formattedList )

			if select >= 0 and select != self.selectedSatelliteIndex :
				self.selectedSatelliteIndex = select
			
			self.initConfig( )

		#Start Search
		if groupId == E_Input02 :
			if self.selectedSatelliteIndex == 0 : #ToDO : All Channel Search
				dialog = diamgr.getInstance().getDialog( diamgr.DIALOG_ID_CHANNEL_SEARCH )
				dialog.setSatellite( self.configuredSatelliteList )
				dialog.doModal( )

			else :
				satelliteList = []
				satellite = self.configuredSatelliteList[self.selectedSatelliteIndex -1]
				print 'longitude=%s bandtype=%s' %( satellite[E_CONFIGURE_SATELLITE_LONGITUDE], satellite[E_CONFIGURE_SATELLITE_BANDTYPE] )

				satelliteList.append( satellite )
				dialog = diamgr.getInstance().getDialog( diamgr.DIALOG_ID_CHANNEL_SEARCH )
				dialog.setSatellite( satelliteList )
				dialog.doModal( )
								

		if groupId == E_SpinEx01 or groupId == E_SpinEx02 :
			self.ControlSelect( )

	def onFocus( self, controlId ):
		if self.initialized == False :
			return
		if ( self.lastFocused != controlId ) :
			self.ShowDescription( controlId )
			self.lastFocused = controlId


	def initConfig( self ) :

		self.ResetAllControl( )
		count = len( self.formattedList )
		
		if count <= 1 :
			hideControlIds = [ E_Input01, E_SpinEx01, E_SpinEx02, E_Input02 ]
			self.SetVisibleControls( hideControlIds, False )
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Has no configured satellite' )

		else :
			self.AddInputControl( E_Input01, 'Satellite', self.formattedList[self.selectedSatelliteIndex], None, 'Select satellite' )
			self.AddEnumControl( E_SpinEx01, 'Network Search', None, 'Network Search' )
			self.AddEnumControl( E_SpinEx02, 'Channel Search Mode', None, 'Channel Search Mode' )
			self.AddLeftLabelButtonControl( E_Input02, 'Start Search', 'Start Search' )
			self.InitControl( )

		
	def getFormattedName( self, longitude, band ) :
	
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

		configuredSatelliteList1 = []
		configuredSatelliteList1 = self.mCommander.satelliteconfig_GetList( E_TUNER_1 )		

		configuredSatelliteList2 = []
		configuredSatelliteList2 = self.mCommander.satelliteconfig_GetList( E_TUNER_2 )		

		property = ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander )

		self.configuredSatelliteList = deepcopy( configuredSatelliteList1 )
		
		if property.getProp( ) == E_DIFFERENT_TUNER :
			for config in configuredSatelliteList2 :
				find = False
				for compare in configuredSatelliteList1 :
					if config[E_CONFIGURE_SATELLITE_LONGITUDE] == compare[E_CONFIGURE_SATELLITE_LONGITUDE] :
						find = True
						break

				if find == False :
					self.configuredSatelliteList.append( config )


		self.formattedList = []
		self.formattedList.append('All')

		for config in self.configuredSatelliteList :
			self.formattedList.append( self.getFormattedName( int(config[E_CONFIGURE_SATELLITE_LONGITUDE]), int(config[E_CONFIGURE_SATELLITE_BANDTYPE]) ) )


