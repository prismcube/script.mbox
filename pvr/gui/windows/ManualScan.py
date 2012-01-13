import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DlgMgr
import pvr.TunerConfigMgr as configMgr
from  pvr.TunerConfigMgr import *
from pvr.gui.GuiConfig import *
from ElisEnum import ElisEnum


from pvr.gui.BaseWindow import SettingWindow, Action

class ManualScan( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
			
		self.mInitialized = False
		self.mLastFocused = -1
		self.mSelectedSatelliteIndex = 0
		self.mSelectedTransponderIndex = 0		
		self.mAllSatellitelist = []
		self.mTransponderList = []

		self.mFormattedSatelliteList = []
		self.mFormattedTransponderList = []


	def onInit(self):
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		self.SetSettingWindowLabel( 'Manual Scan' )
		
		self.mSelectedSatelliteIndex = 0
		self.mSelectedTransponderIndex = 0		
		self.mAllSatellitelist = []
		self.mConfiguredSatelliteList = []		
		
		self.mAllSatellitelist = self.mCommander.Satellite_GetList( ElisEnum.E_SORT_INSERTED )
		self.LoadFormattedSatelliteNameList()

		self.LoadFormattedTransponderNameList( )		

		self.InitConfig( )
		
		self.ShowDescription( self.getFocusId( ) )
		self.mInitialized = True

		
	def onAction( self, aAction ):

		actionId = aAction.getId( )
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
			


	def onClick( self, aControlId ):

		groupId = self.GetGroupId( aControlId )

		#Satellite		
		if groupId == E_Input01 :
			dialog = xbmcgui.Dialog( )
			select = dialog.select('Select satellite', self.mFormattedSatelliteList )

			if self.mSelectedSatelliteIndex != select and select >= 0:
				self.mSelectedSatelliteIndex = select
				self.mSelectedTransponderIndex = 0
				self.LoadFormattedTransponderNameList( )
				self.InitConfig( )

		#Transponder
		elif groupId == E_Input02 :
			dialog = xbmcgui.Dialog( )
			select = dialog.select('Select Transponder', self.mFormattedTransponderList )

			print 'select = %d %d' %(self.mSelectedTransponderIndex, select)

			if select >=0 and self.mSelectedTransponderIndex != select :
				self.mSelectedTransponderIndex = select
				self.InitConfig( )

		#Start Search
		elif groupId == E_Input03 : #ToDO : Have to support manual input
			transponderList = []
			config = self.mConfiguredSatelliteList[self.mSelectedSatelliteIndex]
			print 'longitude=%d bandtype=%d' %( config.mSatelliteLongitude, config.mBandType )

			transponder = self.mTransponderList[self.mSelectedTransponderIndex]
			print 'ManualScan #0 index=%d transponder=%s' %(self.mSelectedTransponderIndex, transponder )
			transponderList.append( transponder )
			print 'ManualScan #1'
			dialog = DlgMgr.GetInstance().GetDialog( DlgMgr.DIALOG_ID_CHANNEL_SEARCH )
			print 'ManualScan #2'			
			dialog.SetTransponder( config.mSatelliteLongitude, config.mBandType, transponderList )
			print 'ManualScan #3'			
			dialog.doModal( )

		if groupId == E_SpinEx05 or groupId == E_SpinEx06   :
			self.ControlSelect( )


	def onFocus( self, aControlId ):
		if self.mInitialized == False :
			return

		if ( self.mLastFocused != aControlId ) :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId


	def InitConfig( self ) :

		self.ResetAllControl( )	

		count = len( self.mFormattedSatelliteList )
		
		if count <= 0 :
			hideControlIds = [ E_Input01, E_Input02,E_Input03, E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_SpinEx06 ]
			self.SetVisibleControls( hideControlIds, False )
			self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Has no configured satellite' )

		else :
			self.AddInputControl( E_Input01, 'Satellite', self.mFormattedSatelliteList[self.mSelectedSatelliteIndex], None, None, None, 'Select satellite' )
			self.AddInputControl( E_Input02, 'Transponder Frequency', self.mFormattedTransponderList[self.mSelectedTransponderIndex], None, None, None, 'Select Transponder Frequency' )


			#DVB Type
			self.AddEnumControl( E_SpinEx01, 'DVB Type', None, 'Select DVB Type' )
			transponder  =  self.mTransponderList [ self.mSelectedTransponderIndex ]

			if transponder.mFECMode <= ElisEnum.E_DVBS_7_8 :
				self.SetProp( E_SpinEx01, 0 )
			else :
				self.SetProp( E_SpinEx01, 1 )


			#FEC
			self.AddEnumControl( E_SpinEx02, 'FEC', None, 'Select FEC' )
			self.SetProp( E_SpinEx02, transponder.mFECMode )

			#POL
			self.AddEnumControl( E_SpinEx03, 'Polarisation', None,'Select Polarization' )
			self.SetProp( E_SpinEx03, transponder.mPolarization )

			#Symbolrate
			self.AddEnumControl( E_SpinEx04, 'Symbol Rate', None, 'Select Symbol Rate' )
			self.SetProp( E_SpinEx04, transponder.mSymbolRate )
			
			self.AddEnumControl( E_SpinEx05, 'Network Search', None, 'Select Network Search' )
			self.AddEnumControl( E_SpinEx06, 'Channel Search Mode',None, 'Select Channel Search Mode' )
			self.AddLeftLabelButtonControl( E_Input03, 'Start Search', 'Start Search' )

			self.InitControl( )
			


	def GetFormattedName( self, aLongitude, aBand ) :
	
		found = False	

		for satellite in self.mAllSatellitelist :
			if aLongitude == satellite.mLongitude and aBand == satellite.mBand :
				found = True
				break

		if found == True :
			dir = 'E'

			tmpLongitude  = aLongitude
			if tmpLongitude > 1800 :
				dir = 'W'
				tmpLongitude = 3600 - aLongitude

			formattedName = '%d.%d %s %s' %( int( tmpLongitude/10 ), tmpLongitude%10, dir, satellite.mName )
			return formattedName

		return 'UnKnown'


	def LoadFormattedSatelliteNameList( self ) :

		configuredSatelliteList1 = []
		configuredSatelliteList1 = self.mCommander.Satelliteconfig_GetList( E_TUNER_1 )		

		configuredSatelliteList2 = []
		configuredSatelliteList2 = self.mCommander.Satelliteconfig_GetList( E_TUNER_2 )		

		property = ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander )

		self.mConfiguredSatelliteList = deepcopy( configuredSatelliteList1 )
		
		if property.GetProp( ) == E_DIFFERENT_TUNER :
			for config in configuredSatelliteList2 :
				find = False
				for compare in configuredSatelliteList1 :
					if config.mSatelliteLongitude == compare.mSatelliteLongitude and config.mBandType == compare.mBandType:
						find = True
						break

				if find == False :
					self.mConfiguredSatelliteList.append( config )


		self.mFormattedSatelliteList = []
		for config in self.mConfiguredSatelliteList :
			self.mFormattedSatelliteList.append( self.GetFormattedName( config.mSatelliteLongitude, config.mBandType ) )


	def LoadFormattedTransponderNameList( self ) :

		satellite = self.mAllSatellitelist[self.mSelectedSatelliteIndex]

		self.mTransponderList = []
		self.mTransponderList = self.mCommander.Transponder_GetList( satellite.mLongitude, satellite.mBand )

		self.mFormattedTransponderList = []
		
		for i in range( len( self.mTransponderList ) ) :
			self.mFormattedTransponderList.append( '%d' % ( i + 1 ) + ' %d' % self.mTransponderList[i].mFrequency + ' MHz /' + ' %d' % self.mTransponderList[i].mSymbolRate + ' KS/s' )

	
