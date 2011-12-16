import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
import pvr.gui.dialogmgr as diamgr
import pvr.tunerconfigmgr as configmgr
from pvr.tunerconfigmgr import *
from pvr.gui.basewindow import SettingWindow, setWindowBusy
from pvr.gui.basewindow import Action
import pvr.elismgr
from elisproperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.guiconfig import *
from elisenum import ElisEnum


class SatelliteConfigSimple( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance().getCommander( )
			
	def onInit( self ):
		print '------------------------------------- #1'
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		print '------------------------------------- #2'
		self.tunerIndex = configmgr.getInstance( ).getCurrentTunerIndex( )
		print '------------------------------------- #3'		
		self.tunertype = configmgr.getInstance( ).getCurrentTunerType( )
		print '------------------------------------- #4'
		self.currentSatellite = configmgr.getInstance( ).getCurrentConfiguredSatellite( ) 
		print '------------------------------------- #5'	
		self.transponderList = configmgr.getInstance( ).getTransponderList( int( self.currentSatellite[E_CONFIGURE_SATELLITE_LONGITUDE] ) )
 
		
		self.setHeaderLabel( 'Satellite Configuration' ) 
		
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Satellite Config : Tuner %s - %s' % ( self.tunerIndex + 1, E_LIST_TUNER_TYPE[ self.tunertype ] ) )
		self.selectedIndexLnbType = int( self.currentSatellite[ E_CONFIGURE_SATELLITE_LNB_TYPE ] )

		self.initConfig( )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )
		#self.initialized = True
		
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
		if( controlId == E_SpinEx01 + 1 or controlId == E_SpinEx01 + 2 ) :
			self.selectedIndexLnbType = self.getSelectedIndex( E_SpinEx01 )
			
			if self.selectedIndexLnbType == ElisEnum.E_LNB_SINGLE :
				self.currentSatellite[ E_CONFIGURE_SATELLITE_LOW_LNB ] = "5150"	
				
			else :
				self.currentSatellite[ E_CONFIGURE_SATELLITE_LOW_LNB ] = "9750"	
				self.currentSatellite[ E_CONFIGURE_SATELLITE_HIGH_LNB ] = "10600"	
				self.currentSatellite[ E_CONFIGURE_SATELLITE_LNB_THRESHOLD ] = "11700"					

			self.initConfig( )
			
		elif( controlId == E_Input01 + 1 ) :
			satelliteList = configmgr.getInstance( ).getFormattedNameList( )
			dialog = xbmcgui.Dialog()
 			ret = dialog.select('Select satellite', satelliteList )

			if ret >= 0 :
	 			satellite = satelliteList[ret]
				self.currentSatellite[ E_CONFIGURE_SATELLITE_LONGITUDE ] = satellite[0]
				self.initConfig()

 		elif( controlId == E_Input03 + 1 ) :
 			dialog = xbmcgui.Dialog()
 			ret = dialog.select('Select Transponder', self.transponderList )

 		elif( controlId == E_Input02 + 1 ) :
 			diamgr.getInstance().showDialog( diamgr.DIALOG_ID_LNB_FREQUENCY )
 			print 'dhkim test getLabel = %s' % diamgr.getInstance().getResultText( )

		
	def onFocus( self, controlId ):
		pass


	def initConfig( self ) :
		self.resetAllControl( )

		# Common	
		self.addInputControl( E_Input01, 'Satellite' , configmgr.getInstance( ).getFormattedName( int( self.currentSatellite[E_CONFIGURE_SATELLITE_LONGITUDE] ) ), None, None )
		self.addUserEnumControl( E_SpinEx01, 'LNB Setting', E_LIST_LNB_TYPE, self.selectedIndexLnbType, None )
		
		if( self.selectedIndexLnbType == ElisEnum.E_LNB_SINGLE ) :
			self.addUserEnumControl( E_SpinEx02, 'LNB Frequency', E_LIST_SINGLE_FREQUENCY, getSingleFrequenceIndex( self.currentSatellite[ E_CONFIGURE_SATELLITE_LOW_LNB ] ), None )
		else :
			self.lnbFrequency = self.currentSatellite[E_CONFIGURE_SATELLITE_LOW_LNB] + ' / ' + self.currentSatellite[ E_CONFIGURE_SATELLITE_HIGH_LNB ] + ' / ' + self.currentSatellite[E_CONFIGURE_SATELLITE_LNB_THRESHOLD]
			self.addInputControl( E_Input02, 'LNB Frequency', self.lnbFrequency, None, None )
		self.addUserEnumControl( E_SpinEx03, '22KHz Control', USER_ENUM_LIST_ON_OFF, self.currentSatellite[ E_CONFIGURE_SATELLITE_FREQUENCY_LEVEL ], None )


		self.addInputControl( E_Input03, 'Transponder', self.transponderList[0], None, None )
		self.addLeftLabelButtonControl( E_Input04, 'Save', None )

		if( self.selectedIndexLnbType == ElisEnum.E_LNB_SINGLE ) :
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input01, E_Input03, E_Input04 ]
			hideControlIds = [ E_Input02, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_Input05 ]
		else :
			visibleControlIds = [ E_SpinEx01, E_SpinEx03, E_Input01, E_Input02, E_Input03, E_Input04 ]
			hideControlIds = [ E_SpinEx02, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_Input05 ]


			
		self.setVisibleControls( visibleControlIds, True )
		self.setEnableControls( visibleControlIds, True )

		self.setVisibleControls( hideControlIds, False )

		self.initControl( )
		self.disableControl( )
		

	def disableControl( self ):
		enableControlIds = [ E_Input02, E_SpinEx02, E_SpinEx03 ]
		if ( self.selectedIndexLnbType == ElisEnum.E_LNB_UNIVERSAL ) :
			self.setEnableControls( enableControlIds, False )
			self.getControl( E_SpinEx03 + 3 ).selectItem( 1 )	# Always On
			
		else :
			self.setEnableControls( enableControlIds, True )


