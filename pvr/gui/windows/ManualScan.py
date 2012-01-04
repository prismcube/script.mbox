import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as winmgr
import pvr.gui.DialogMgr as diamgr
import pvr.TunerConfigMgr as configmgr
from  pvr.TunerConfigMgr import *
from pvr.gui.GuiConfig import *
from ElisEnum import ElisEnum


from pvr.gui.BaseWindow import SettingWindow
from pvr.gui.BaseWindow import Action


class ManualScan( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
		self.mCommander = pvr.ElisMgr.getInstance( ).getCommander( )
			
		self.initialized = False
		self.lastFocused = -1
		self.selectedSatelliteIndex = 0
		self.selectedTransponderIndex = 0		
		self.allsatellitelist = []
		self.transponderList = []

		self.formattedSatelliteList = []
		self.formattedTransponderList = []


	def onInit(self):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.setHeaderLabel( 'Manual Scan' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )

		self.selectedSatelliteIndex = 0
		self.selectedTransponderIndex = 0		
		self.allsatellitelist = []
		
		self.allsatellitelist = self.mCommander.satellite_GetList( ElisEnum.E_SORT_INSERTED )
		self.loadFormattedSatelliteNameList()

		self.loadFormattedTransponderNameList( )		

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
			select = dialog.select('Select satellite', self.formattedSatelliteList )

			if self.selectedSatelliteIndex != select and select >= 0:
				self.selectedSatelliteIndex = select
				self.selectedTransponderIndex = 0
				self.loadFormattedTransponderNameList( )
				self.initConfig( )

		#Transponder
		elif groupId == E_Input02 :
			dialog = xbmcgui.Dialog( )
			select = dialog.select('Select Transponder', self.formattedTransponderList )

			print 'select = %d %d' %(self.selectedTransponderIndex, select)

			if select >=0 and self.selectedTransponderIndex != select :
				self.selectedTransponderIndex = select
				self.initConfig( )

		#Start Search
		elif groupId == E_Input03 : #ToDO : Have to support manual input
			transponderList = []
			satellite = self.configuredSatelliteList[self.selectedSatelliteIndex]
			print 'longitude=%s bandtype=%s' %( satellite[E_CONFIGURE_SATELLITE_LONGITUDE], satellite[E_CONFIGURE_SATELLITE_BANDTYPE] )

			transponder = self.transponderList[self.selectedTransponderIndex]
			print 'ManualScan #0 index=%d transponder=%s' %(self.selectedTransponderIndex, transponder )
			transponderList.append( transponder )
			print 'ManualScan #1'
			dialog = diamgr.getInstance().getDialog( diamgr.DIALOG_ID_CHANNEL_SEARCH )
			print 'ManualScan #2'			
			dialog.setTransponder( int( satellite[E_CONFIGURE_SATELLITE_LONGITUDE]), int( satellite[E_CONFIGURE_SATELLITE_BANDTYPE] ), transponderList )
			print 'ManualScan #3'			
			dialog.doModal( )

		if groupId == E_SpinEx05 or groupId == E_SpinEx06   :
			self.ControlSelect( )


	def onFocus( self, controlId ):
		if self.initialized == False :
			return
		if ( self.lastFocused != controlId ) :
			self.ShowDescription( controlId )
			self.lastFocused = controlId


	def initConfig( self ) :

		self.ResetAllControl( )	

		count = len( self.formattedSatelliteList )
		
		if count <= 0 :
			hideControlIds = [ E_Input01, E_Input02,E_Input03, E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06 ]
			self.SetVisibleControls( hideControlIds, False )
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Has no configured satellite' )

		else :
			self.AddInputControl( E_Input01, 'Satellite', self.formattedSatelliteList[self.selectedSatelliteIndex], None, 'Select satellite' )
			self.AddInputControl( E_Input02, 'Transponder Frequency', self.formattedTransponderList[self.selectedTransponderIndex], None, 'Select Transponder Frequency' )


			#DVB Type
			self.AddEnumControl( E_SpinEx01, 'DVB Type', None, 'Select DVB Type' )
			transponder  =  self.transponderList [ self.selectedTransponderIndex ]

			fecMode = int( transponder[3] )
			if fecMode <= ElisEnum.E_DVBS_7_8 :
				self.SetProp( E_SpinEx01, 0 )
			else :
				self.SetProp( E_SpinEx01, 1 )


			#FEC
			self.AddEnumControl( E_SpinEx02, 'FEC', None, 'Select FEC' )
			self.SetProp( E_SpinEx02, fecMode )

			#POL
			polarization = int( transponder[2] )
			self.AddEnumControl( E_SpinEx03, 'Polarisation', None,'Select Polarization' )
			self.SetProp( E_SpinEx03, polarization )

			#Symbolrate
			symbolrate = int( transponder[1] )			
			self.AddEnumControl( E_SpinEx04, 'Symbol Rate', None, 'Select Symbol Rate' )
			self.SetProp( E_SpinEx04, symbolrate )
			
			self.AddEnumControl( E_SpinEx05, 'Network Search', None, 'Select Network Search' )
			self.AddEnumControl( E_SpinEx06, 'Channel Search Mode',None, 'Select Channel Search Mode' )
			self.AddLeftLabelButtonControl( E_Input03, 'Start Search', 'Start Search' )

			self.InitControl( )
			


	def GetFormattedName( self, longitude , band ) :
	
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


		self.formattedSatelliteList = []
		for config in self.configuredSatelliteList :
			self.formattedSatelliteList.append( self.GetFormattedName( int(config[E_CONFIGURE_SATELLITE_LONGITUDE]), int(config[E_CONFIGURE_SATELLITE_BANDTYPE]) ) )


	def loadFormattedTransponderNameList( self ) :

		satellite = self.allsatellitelist[self.selectedSatelliteIndex]

		self.transponderList = []
		self.transponderList = self.mCommander.transponder_GetList( int( satellite[0] ), int( satellite[1]  ) )

		self.formattedTransponderList = []
		
		for i in range( len( self.transponderList ) ) :
			self.formattedTransponderList.append( '%s' % ( i + 1 ) + ' ' + self.transponderList[i][0] + ' MHz / ' + self.transponderList[i][1] + ' KS/s' )

	
