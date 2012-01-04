import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as winmgr
import pvr.gui.DialogMgr as diamgr
import pvr.TunerConfigMgr as configmgr
from pvr.TunerConfigMgr import *
from pvr.gui.BaseWindow import SettingWindow
from pvr.gui.BaseWindow import Action
import pvr.ElisMgr
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.GuiConfig import *
from ElisEnum import ElisEnum


class SatelliteConfigSimple( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
		self.mCommander = pvr.ElisMgr.getInstance( ).getCommander( )
			
	def onInit( self ):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )
		self.lnbFrequency = None
		self.tunerIndex = configmgr.getInstance( ).GetCurrentTunerIndex( )
		self.currentSatellite = configmgr.getInstance( ).GetCurrentConfiguredSatellite( )
		self.transponderList = configmgr.getInstance( ).GetTransponderList( int( self.currentSatellite[E_CONFIGURE_SATELLITE_LONGITUDE] ), int( self.currentSatellite[E_CONFIGURE_SATELLITE_BANDTYPE] ) )
		self.selectedTransponderIndex = 0
 
		self.setHeaderLabel( 'Satellite Configuration' ) 

		property = ElisPropertyEnum( 'Tuner1 Type', self.mCommander )

		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Satellite Config : Tuner %s - %s' % ( self.tunerIndex + 1, property.getPropString( ) ) )
		self.selectedIndexLnbType = int( self.currentSatellite[ E_CONFIGURE_SATELLITE_LNB_TYPE ] )

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
			self.saveConfig( )
			self.ResetAllControl( )
			self.close( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )
			
		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )


	def onClick( self, controlId ):

		groupId = self.GetGroupId( controlId )
		
		#Satellite
		if groupId == E_Input01 :
			satelliteList = configmgr.getInstance( ).GetFormattedNameList( )
			dialog = xbmcgui.Dialog()
 			ret = dialog.select('Select satellite', satelliteList )

			if ret >= 0 :
	 			satellite = configmgr.getInstance( ).GetSatelliteByIndex( ret )

	 			for i in range( 22 ) :
					self.currentSatellite[ i ] = "0"

				self.currentSatellite[ E_CONFIGURE_SATELLITE_LONGITUDE ] = satellite[0] # Longitude
				self.currentSatellite[ E_CONFIGURE_SATELLITE_BANDTYPE ] = satellite[1]	# Band
				self.currentSatellite[ E_CONFIGURE_SATELLITE_IS_CONFIG_USED ] = "1"		# IsUsed
				self.currentSatellite[ E_CONFIGURE_SATELLITE_LOW_LNB ] = "9750"			# Low
				self.currentSatellite[ E_CONFIGURE_SATELLITE_HIGH_LNB ] = "10600"		# High
				self.currentSatellite[ E_CONFIGURE_SATELLITE_LNB_THRESHOLD ] = "11700"	# Threshold

				self.transponderList = configmgr.getInstance( ).GetTransponderList( int( self.currentSatellite[E_CONFIGURE_SATELLITE_LONGITUDE] ), int( self.currentSatellite[E_CONFIGURE_SATELLITE_BANDTYPE] ) )				
		
				self.initConfig()

		# LNB Setting
		elif groupId == E_SpinEx01 :
			self.selectedIndexLnbType = self.GetSelectedIndex( E_SpinEx01 )
			indexString = '%d' % self.selectedIndexLnbType
			self.currentSatellite[ E_CONFIGURE_SATELLITE_LNB_TYPE ] = indexString
			self.currentSatellite[ E_CONFIGURE_SATELLITE_FREQUENCY_LEVEL ] = "0"			
			
			if self.selectedIndexLnbType == ElisEnum.E_LNB_SINGLE :
				self.currentSatellite[ E_CONFIGURE_SATELLITE_LOW_LNB ] = "5150"	

				
			else :
				self.currentSatellite[ E_CONFIGURE_SATELLITE_LOW_LNB ] = "9750"	
				self.currentSatellite[ E_CONFIGURE_SATELLITE_HIGH_LNB ] = "10600"	
				self.currentSatellite[ E_CONFIGURE_SATELLITE_LNB_THRESHOLD ] = "11700"

			self.initConfig( )

		# LNB Frequency - Spincontrol
 		elif groupId == E_SpinEx02 :
 			position = self.GetSelectedIndex( E_SpinEx02 )
			self.currentSatellite[ E_CONFIGURE_SATELLITE_LOW_LNB ] = E_LIST_SINGLE_FREQUENCY[ position ]


		# LNB Frequency - Inputcontrol
 		elif groupId == E_Input02 :

 			dialog = diamgr.getInstance().getDialog( diamgr.DIALOG_ID_LNB_FREQUENCY )
 			dialog.setFrequency( self.currentSatellite[E_CONFIGURE_SATELLITE_LOW_LNB], self.currentSatellite[E_CONFIGURE_SATELLITE_HIGH_LNB], self.currentSatellite[E_CONFIGURE_SATELLITE_LNB_THRESHOLD] )
 			dialog.doModal( )

			if dialog.isOK() == True :
	 			lowFreq, highFreq, threshFreq  = dialog.getFrequency( )

				self.currentSatellite[E_CONFIGURE_SATELLITE_LOW_LNB] = lowFreq
				self.currentSatellite[E_CONFIGURE_SATELLITE_HIGH_LNB] = highFreq
				self.currentSatellite[E_CONFIGURE_SATELLITE_LNB_THRESHOLD] = threshFreq

				self.initConfig( )


		# 22Khz
 		elif groupId == E_SpinEx03 :
 			indexString = '%d' % self.GetSelectedIndex( E_SpinEx03 )
			self.currentSatellite[ E_CONFIGURE_SATELLITE_FREQUENCY_LEVEL ] = indexString

		# Transponer
 		elif groupId == E_Input03 :
 			dialog = xbmcgui.Dialog()
 			self.selectedTransponderIndex = dialog.select('Select Transponder', self.transponderList )
 			if self.selectedTransponderIndex != -1 :
 				self.initConfig( )
		
	def onFocus( self, controlId ):
		pass


	def initConfig( self ) :
		self.ResetAllControl( )

		self.AddInputControl( E_Input01, 'Satellite' , configmgr.getInstance( ).GetFormattedName( int( self.currentSatellite[E_CONFIGURE_SATELLITE_LONGITUDE] ), int( self.currentSatellite[E_CONFIGURE_SATELLITE_BANDTYPE] ) ) )
		self.AddUserEnumControl( E_SpinEx01, 'LNB Type', E_LIST_LNB_TYPE, self.selectedIndexLnbType )


		if( self.selectedIndexLnbType == ElisEnum.E_LNB_SINGLE ) :
			self.AddUserEnumControl( E_SpinEx02, 'LNB Frequency', E_LIST_SINGLE_FREQUENCY, getSingleFrequenceIndex( self.currentSatellite[ E_CONFIGURE_SATELLITE_LOW_LNB ] ) )
		else :
			self.lnbFrequency = self.currentSatellite[E_CONFIGURE_SATELLITE_LOW_LNB] + ' / ' + self.currentSatellite[ E_CONFIGURE_SATELLITE_HIGH_LNB ] + ' / ' + self.currentSatellite[E_CONFIGURE_SATELLITE_LNB_THRESHOLD]
			self.AddInputControl( E_Input02, 'LNB Frequency', self.lnbFrequency )
		self.AddUserEnumControl( E_SpinEx03, '22KHz Control', USER_ENUM_LIST_ON_OFF, self.currentSatellite[ E_CONFIGURE_SATELLITE_FREQUENCY_LEVEL ] )


		self.AddInputControl( E_Input03, 'Transponder', self.transponderList[self.selectedTransponderIndex] )

		if( self.selectedIndexLnbType == ElisEnum.E_LNB_SINGLE ) :
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input01, E_Input03]
			hideControlIds = [ E_Input02, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_Input04, E_Input05 ]
		else :
			visibleControlIds = [ E_SpinEx01, E_SpinEx03, E_Input01, E_Input02 ]
			hideControlIds = [ E_SpinEx02, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_Input04, E_Input05 ]


			
		self.SetVisibleControls( visibleControlIds, True )
		self.SetEnableControls( visibleControlIds, True )

		self.SetVisibleControls( hideControlIds, False )

		self.InitControl( )
		self.disableControl( )
		

	def disableControl( self ):
		enableControlIds = [ E_Input02, E_SpinEx02, E_SpinEx03 ]
		if ( self.selectedIndexLnbType == ElisEnum.E_LNB_UNIVERSAL ) :
			self.SetEnableControls( enableControlIds, False )
			self.getControl( E_SpinEx03 + 3 ).selectItem( 1 )	# Always On
			
		else :
			self.SetEnableControls( enableControlIds, True )

	def saveConfig( self ) :
		configmgr.getInstance( ).SaveCurrentConfig( self.currentSatellite )
		