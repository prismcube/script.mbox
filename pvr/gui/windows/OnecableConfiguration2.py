import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as winmgr
import pvr.tunerconfigmgr as configmgr
from pvr.tunerconfigmgr import *
from pvr.gui.guiconfig import *
import pvr.ElisMgr

from pvr.gui.basewindow import SettingWindow
from pvr.gui.basewindow import Action
from elisproperty import ElisPropertyInt


class OneCableConfiguration2( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
		self.commander = pvr.ElisMgr.getInstance().getCommander()
		self.satelliteCount = 0
		self.satellitelist = []
		self.scrList = [ 'SCR(0)', 'SCR(1)', 'SCR(2)', 'SCR(3)', 'SCR(4)', 'SCR(5)', 'SCR(6)', 'SCR(7)' ]
		self.satelliteCount = 0
		self.tunerIndex = 0
		self.currentSatellite = []
		self.currentSatellite2 = []
		

	def onInit( self ):
		self.setHeaderLabel( 'OneCable Configuration' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'OneCable configuration' )
		self.oneCablesatelliteCount = configmgr.getInstance( ).getOneCableSatelliteCount( )
		self.currentSatellite = []
		self.currentSatellite2 = []

		if configmgr.getInstance( ).getCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
			self.tunerIndex = configmgr.getInstance( ).getCurrentTunerIndex( )

			self.AddEnumControl( E_SpinEx01, 'MDU' )

			pinCode = ElisPropertyInt( 'Tuner%d Pin Code' % ( self.tunerIndex + 1 ), self.commander ).getProp( )
			self.AddInputControl( E_Input01, 'Tuner %d PIN-Code' % ( self.tunerIndex + 1 ), '%d' % pinCode, 0, 1, 3 )

			tunerScr = ElisPropertyInt( 'Tuner%d SCR' % ( self.tunerIndex + 1 ), self.commander ).getProp( )
			self.AddUserEnumControl( E_SpinEx02, 'Tuner %d' % ( self.tunerIndex + 1 ), self.scrList, tunerScr )

			tunerFrequency = ElisPropertyInt( 'Tuner%d SCR Frequency' % ( self.tunerIndex + 1 ), self.commander ).getProp( )
			self.AddUserEnumControl( E_SpinEx03, 'Tuner %d Frequency' % ( self.tunerIndex + 1 ), E_LIST_ONE_CABLE_TUNER_FREQUENCY, getOneCableTunerFrequencyIndex( '%d' % tunerFrequency ) )

			disableControls = [ E_Input02, E_SpinEx04, E_SpinEx05 ]
			self.SetVisibleControls( disableControls, False )
			self.SetEnableControls( disableControls, False )

		elif configmgr.getInstance( ).getCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
			self.AddEnumControl( E_SpinEx01, 'MDU' )

			pinCode = ElisPropertyInt( 'Tuner1 Pin Code', self.commander ).getProp( )
			self.AddInputControl( E_Input01, 'Tuner1 PIN-Code', '%d' % pinCode, 0, 1, 4 )

			tunerScr = ElisPropertyInt( 'Tuner1 SCR', self.commander ).getProp( )
			self.AddUserEnumControl( E_SpinEx02, 'Tuner 1', self.scrList, tunerScr )

			tunerFrequency = ElisPropertyInt( 'Tuner1 SCR Frequency', self.commander ).getProp( )
			self.AddUserEnumControl( E_SpinEx03, 'Tuner 1 Frequency', E_LIST_ONE_CABLE_TUNER_FREQUENCY, getOneCableTunerFrequencyIndex( '%d' % tunerFrequency ) )

			pinCode = ElisPropertyInt( 'Tuner2 Pin Code', self.commander ).getProp( )
			self.AddInputControl( E_Input02, 'Tuner2 PIN-Code', '%d' % pinCode, 0, 1, 4 )

			tunerScr = ElisPropertyInt( 'Tuner2 SCR', self.commander ).getProp( )
			self.AddUserEnumControl( E_SpinEx04, 'Tuner 2', self.scrList, tunerScr )

			tunerFrequency = ElisPropertyInt( 'Tuner2 SCR Frequency', self.commander ).getProp( )
			self.AddUserEnumControl( E_SpinEx05, 'Tuner 2 Frequency', E_LIST_ONE_CABLE_TUNER_FREQUENCY, getOneCableTunerFrequencyIndex( '%d' % tunerFrequency ) )

		self.InitControl( )
		self.disableControl( )
				
	def onAction( self, action ):
		actionId = action.getId( )
		focusId = self.getFocusId( )
		groupId = self.GetGroupId( focusId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.onClose( );

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

		if groupId == E_SpinEx01 :
			self.ControlSelect( )
			self.disableControl( )
			
		elif groupId == E_Input01 or groupId == E_Input02 :
			self.ControlSelect( )

		if configmgr.getInstance( ).getCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
			for i in range( self.oneCablesatelliteCount ) :
				self.currentSatellite.append( configmgr.getInstance( ).getConfiguredSatellitebyIndex( i ) )
				
				self.currentSatellite[i][E_CONFIGURE_SATELLITE_ONECABLE_MDU] = '%d' % self.GetSelectedIndex( E_SpinEx01 )
					
				self.currentSatellite[i][E_CONFIGURE_SATELLITE_ONECABLE_PIN] = self.getControl( E_Input01 + 3 ).getListItem( 0 ).getLabel2( )
					
				self.currentSatellite[i][E_CONFIGURE_SATELLITE_ONECABLE_UBSLOT] = '%d' % self.GetSelectedIndex( E_SpinEx02 )

				self.currentSatellite[i][E_CONFIGURE_SATELLITE_ONECABLE_UBFREQ] = E_LIST_ONE_CABLE_TUNER_FREQUENCY[self.GetSelectedIndex( E_SpinEx03 )]

		elif configmgr.getInstance( ).getCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
			for i in range( self.oneCablesatelliteCount ) :
				self.currentSatellite.append( configmgr.getInstance( ).getConfiguredSatellitebyIndex( i ) )
				
				self.currentSatellite[i][E_CONFIGURE_SATELLITE_ONECABLE_MDU] = '%d' % self.GetSelectedIndex( E_SpinEx01 )
					
				self.currentSatellite[i][E_CONFIGURE_SATELLITE_ONECABLE_PIN] = self.getControl( E_Input01 + 3 ).getListItem( 0 ).getLabel2( )
					
				self.currentSatellite[i][E_CONFIGURE_SATELLITE_ONECABLE_UBSLOT] = '%d' % self.GetSelectedIndex( E_SpinEx02 )

				self.currentSatellite[i][E_CONFIGURE_SATELLITE_ONECABLE_UBFREQ] = E_LIST_ONE_CABLE_TUNER_FREQUENCY[self.GetSelectedIndex( E_SpinEx03 )]

			self.currentSatellite2 = configmgr.getInstance( ).getConfiguredSatellitebyTunerIndex( 1 )
			for i in range( self.oneCablesatelliteCount ) :

				self.currentSatellite2[i][E_CONFIGURE_SATELLITE_ONECABLE_MDU] = '%d' % self.GetSelectedIndex( E_SpinEx01 )
					
				self.currentSatellite2[i][E_CONFIGURE_SATELLITE_ONECABLE_PIN] = self.getControl( E_Input02 + 3 ).getListItem( 0 ).getLabel2( )
					
				self.currentSatellite2[i][E_CONFIGURE_SATELLITE_ONECABLE_UBSLOT] = '%d' % self.GetSelectedIndex( E_SpinEx04 )

				self.currentSatellite2[i][E_CONFIGURE_SATELLITE_ONECABLE_UBFREQ] = E_LIST_ONE_CABLE_TUNER_FREQUENCY[self.GetSelectedIndex( E_SpinEx05 )]

			
	def onFocus( self, controlId ):
		pass

	def onClose( self ):
		if xbmcgui.Dialog( ).yesno('Configure', 'Are you sure?') == 1 :
			if configmgr.getInstance( ).getCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
				ElisPropertyInt( 'Tuner%d Pin Code' % ( self.tunerIndex + 1 ), self.commander ).SetProp( int( self.getControl( E_Input01 + 3 ).getListItem(0).getLabel2( ) ) )
				ElisPropertyInt( 'Tuner%d SCR' % ( self.tunerIndex + 1 ), self.commander ).SetProp( self.GetSelectedIndex( E_SpinEx02 ) ) 
				ElisPropertyInt( 'Tuner%d SCR Frequency' % ( self.tunerIndex + 1 ), self.commander ).SetProp( int( E_LIST_ONE_CABLE_TUNER_FREQUENCY[self.GetSelectedIndex( E_SpinEx03 )] ) )
			elif configmgr.getInstance( ).getCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
				ElisPropertyInt( 'Tuner1 Pin Code', self.commander ).SetProp( int( self.getControl( E_Input01 + 3 ).getListItem(0).getLabel2( ) ) )
				ElisPropertyInt( 'Tuner1 SCR', self.commander ).SetProp( self.GetSelectedIndex( E_SpinEx02 ) ) 
				ElisPropertyInt( 'Tuner1 SCR Frequency', self.commander ).SetProp( int( E_LIST_ONE_CABLE_TUNER_FREQUENCY[self.GetSelectedIndex( E_SpinEx03 )] ) )
				ElisPropertyInt( 'Tuner2 Pin Code', self.commander ).SetProp( int( self.getControl( E_Input02 + 3 ).getListItem(0).getLabel2( ) ) )
				ElisPropertyInt( 'Tuner2 SCR', self.commander ).SetProp( self.GetSelectedIndex( E_SpinEx04 ) ) 
				ElisPropertyInt( 'Tuner2 SCR Frequency', self.commander ).SetProp( int( E_LIST_ONE_CABLE_TUNER_FREQUENCY[self.GetSelectedIndex( E_SpinEx05 )] ) )	
			
		self.ResetAllControl( )
		self.close( )


	def saveConfig( self ) :
		if configmgr.getInstance( ).getCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
			for i in range( self.oneCablesatelliteCount ) :
				configmgr.getInstance( ).saveConfigbyIndex( 0, i, self.currentSatellite[i] )

		elif configmgr.getInstance( ).getCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
			for i in range( self.oneCablesatelliteCount ) :
				configmgr.getInstance( ).saveConfigbyIndex( 0, i, self.currentSatellite[i] )
				configmgr.getInstance( ).saveConfigbyIndex( 1, i, self.currentSatellite2[i] )

		
	def disableControl( self ):
		selectedIndex = self.GetSelectedIndex( E_SpinEx01 )
		enableControls = [ E_Input01, E_Input02 ]
		if ( selectedIndex == 0 ) :
			if configmgr.getInstance( ).getCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
				self.SetEnableControl( E_Input01, False )
			elif configmgr.getInstance( ).getCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
				self.SetEnableControls( enableControls, False )
		else :
			if configmgr.getInstance( ).getCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
				self.SetEnableControl( E_Input01, True )
			elif configmgr.getInstance( ).getCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
				self.SetEnableControls( enableControls, True )
