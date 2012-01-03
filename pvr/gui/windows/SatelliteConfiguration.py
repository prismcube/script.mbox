import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as winmgr
import pvr.gui.dialogmgr as diamgr
import pvr.tunerconfigmgr as configmgr
from pvr.tunerconfigmgr import *
from pvr.gui.basewindow import SettingWindow
from pvr.gui.basewindow import Action
import pvr.ElisMgr
from elisproperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.guiconfig import *
from elisenum import ElisEnum


class SatelliteConfiguration( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs)
		self.mCommander = pvr.ElisMgr.getInstance().getCommander( )
			
		self.tunerType = 0
		self.currentSatellite = 0
		self.longitude = 0
		self.currentSatellite = []
		self.selectedIndexLnbType = 0
		self.transponderList = []
		self.lnbFrequency = ''
		#self.initialized = False

	def onInit( self ):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.tunerIndex = configmgr.getInstance( ).getCurrentTunerIndex( ) + 1
		self.tunertype = configmgr.getInstance( ).getCurrentTunerType( )
		self.longitude = configmgr.getInstance( ).getCurrentLongitue( )
		self.currentSatellite = configmgr.getInstance( ).getCurrentConfiguredSatellite( )
		self.transponderList = configmgr.getInstance( ).getTransponderList( self.longitude )
		self.setHeaderLabel( 'Satellite Configuration' ) 
		
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Satellite Config : Tuner %s - %s' % ( self.tunerIndex, E_LIST_TUNER_TYPE[ self.tunertype ] ) )
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
		if( controlId == E_SpinEx01 + 1 or controlId == E_SpinEx01 + 2 ) :
			self.selectedIndexLnbType = self.GetSelectedIndex( E_SpinEx01 )
			self.initConfig( )
			
		elif( controlId == E_Input01 + 1 ) :
			satelliteList = configmgr.getInstance( ).getFormattedNameList( )
			dialog = xbmcgui.Dialog()
 			ret = dialog.select('Select satellite', satelliteList )

 		elif( controlId == E_Input03 + 1 ) :
 			dialog = xbmcgui.Dialog()
 			ret = dialog.select('Select Transponder', self.transponderList )

 		elif( controlId == E_Input02 + 1 ) :
 			diamgr.getInstance().showDialog( diamgr.DIALOG_ID_LNB_FREQUENCY )

		
	def onFocus( self, controlId ):
		pass

	def initConfig( self ) :
		self.ResetAllControl( )

		# Common	
		self.AddInputControl( E_Input01, 'Satellite' , configmgr.getInstance( ).getFormattedName( self.longitude ) )
		self.AddUserEnumControl( E_SpinEx01, 'LNB Setting', E_LIST_LNB_TYPE, self.selectedIndexLnbType )
		if( self.selectedIndexLnbType == 1 ) :
			self.AddUserEnumControl( E_SpinEx02, 'LNB Frequency', E_LIST_SINGLE_FREQUENCY, getSingleFrequenceIndex( self.currentSatellite[ E_CONFIGURE_SATELLITE_LOW_LNB ] ) )
		else :
			self.lnbFrequency = self.currentSatellite[E_CONFIGURE_SATELLITE_LOW_LNB] + ' / ' + self.currentSatellite[ E_CONFIGURE_SATELLITE_HIGH_LNB ] + ' / ' + self.currentSatellite[E_CONFIGURE_SATELLITE_LNB_THRESHOLD]
			self.AddInputControl( E_Input02, 'LNB Frequency', self.lnbFrequency )
		self.AddUserEnumControl( E_SpinEx03, '22KHz Control', USER_ENUM_LIST_ON_OFF, self.currentSatellite[ E_CONFIGURE_SATELLITE_FREQUENCY_LEVEL ] )

		if( self.tunertype == E_SIMPLE_LNB ) :
			self.AddInputControl( E_Input03, 'Transponder', self.transponderList[0] )
			self.AddLeftLabelButtonControl( E_Input04, 'Save' )

			if( self.selectedIndexLnbType == ElisEnum.E_LNB_SINGLE ) :
				visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input01, E_Input03, E_Input04 ]
				hideControlIds = [ E_Input02, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_Input05 ]
			else :
				visibleControlIds = [ E_SpinEx01, E_SpinEx03, E_Input01, E_Input02, E_Input03, E_Input04 ]
				hideControlIds = [ E_SpinEx02, E_SpinEx04, E_SpinEx05, E_SpinEx06, E_Input05 ]

		elif( self.tunertype == E_DISEQC_1_0 ) :
			self.AddUserEnumControl( E_SpinEx04, 'DiSEqC 1.0 Switch', E_LIST_DISEQC_MODE, self.currentSatellite[ E_CONFIGURE_SATELLITE_DISEQC_MODE ] )
			self.AddUserEnumControl( E_SpinEx05, 'DiSEqC Repeat', USER_ENUM_LIST_ON_OFF, self.currentSatellite[ E_CONFIGURE_SATELLITE_DISEQC_REPEAT ] )
			self.AddInputControl( E_Input03, 'Transponder', self.transponderList[0] )
			self.AddLeftLabelButtonControl( E_Input04, 'Save' )

			if( self.selectedIndexLnbType == ElisEnum.E_LNB_SINGLE ) :
				visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input01, E_Input03, E_Input04 ]
				hideControlIds = [ E_Input02, E_SpinEx06, E_Input05 ]
			else :
				visibleControlIds = [ E_SpinEx01, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04 ]
				hideControlIds = [ E_SpinEx02, E_SpinEx06, E_Input05 ]

		elif( self.tunertype == E_DISEQC_1_1 ) :
			self.AddUserEnumControl( E_SpinEx04, 'Committed Switch', E_LIST_COMMITTED_SWITCH, self.currentSatellite[ E_CONFIGURE_SATELLITE_DISEQC_MODE ] )
			self.AddUserEnumControl( E_SpinEx05, 'Uncommitted Switch', E_LIST_UNCOMMITTED_SWITCH, self.currentSatellite[ E_CONFIGURE_SATELLITE_DISEQC_11 ] )
			self.AddUserEnumControl( E_SpinEx06, 'DiSEqC Repeat', USER_ENUM_LIST_ON_OFF, self.currentSatellite[ E_CONFIGURE_SATELLITE_DISEQC_REPEAT ] )
			self.AddInputControl( E_Input03, 'Transponder', self.transponderList[0] )
			self.AddLeftLabelButtonControl( E_Input04, 'Save', None )

			if( self.selectedIndexLnbType == ElisEnum.E_LNB_SINGLE ) :
				visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input01, E_Input03, E_Input04, E_SpinEx06 ]
				hideControlIds = [ E_Input02, E_Input05 ]
			else :
				visibleControlIds = [ E_SpinEx01, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04, E_SpinEx06 ]
				hideControlIds = [ E_SpinEx02, E_Input05 ]

		elif( self.tunertype == E_ONE_CABLE ) :
			self.AddInputControl( E_Input03, 'Transponder', self.transponderList[0], None, None )
			self.AddLeftLabelButtonControl( E_Input04, 'Move Antenna', None )
			self.AddUserEnumControl( E_SpinEx04, 'Action', E_LIST_ONE_CABLE_ACTION, 0 )
			self.AddLeftLabelButtonControl( E_Input05, 'Store Position and Exit', None )

			if( self.selectedIndexLnbType == ElisEnum.E_LNB_SINGLE ) :
				visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_Input01, E_Input03, E_Input04, E_Input05 ]
				hideControlIds = [ E_Input02, E_SpinEx05, E_SpinEx06 ]
			else :
				visibleControlIds = [ E_SpinEx01, E_SpinEx03, E_SpinEx04, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
				hideControlIds = [ E_SpinEx02, E_SpinEx05, E_SpinEx06 ]

		elif( self.tunertype == E_MOTORIZED_1_2 ) :
			self.AddInputControl( E_Input03, 'Transponder', self.transponderList[0], None, None )
			self.AddLeftLabelButtonControl( E_Input04, 'Go to the Position', None )
			self.AddLeftLabelButtonControl( E_Input05, 'Save', None )

			if( self.selectedIndexLnbType == ElisEnum.E_LNB_SINGLE ) :
				visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input01, E_Input03, E_Input04, E_Input05 ]
				hideControlIds = [ E_Input02, E_SpinEx04, E_SpinEx05, E_SpinEx06 ]
			else :
				visibleControlIds = [ E_SpinEx01, E_SpinEx03, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
				hideControlIds = [ E_SpinEx02, E_SpinEx04, E_SpinEx05, E_SpinEx06 ]
			
		elif( self.tunertype == E_MOTORIZED_USALS ) :
			self.AddInputControl( E_Input03, 'Transponder', self.transponderList[0], None, None )
			self.AddLeftLabelButtonControl( E_Input04, 'Go to the Position', None )
			self.AddLeftLabelButtonControl( E_Input05, 'Save', None )

			if( self.selectedIndexLnbType == ElisEnum.E_LNB_SINGLE ) :
				visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input01, E_Input03, E_Input04, E_Input05 ]
				hideControlIds = [ E_Input02, E_SpinEx04, E_SpinEx05, E_SpinEx06 ]
			else :
				visibleControlIds = [ E_SpinEx01, E_SpinEx03, E_Input01, E_Input02, E_Input03, E_Input04, E_Input05 ]
				hideControlIds = [ E_SpinEx02, E_SpinEx04, E_SpinEx05, E_SpinEx06 ]
		
			
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

		'''
		selectedIndex2 = self.GetSelectedIndex( E_SpinEx02 )	
		if ( selectedIndex2 == 0 ) :
			self.SetEnableControl( E_SpinEx04, False )
			self.SetEnableControl( E_Input02, False )
			self.getControl( E_SpinEx04 + 3 ).selectItem( self.GetSelectedIndex( E_SpinEx03 ) )
		else :
			self.SetEnableControl( E_SpinEx04, True)
			self.SetEnableControl( E_Input02, True )
		'''
