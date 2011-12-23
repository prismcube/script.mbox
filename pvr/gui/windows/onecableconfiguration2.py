import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
import pvr.tunerconfigmgr as configmgr
from pvr.tunerconfigmgr import *
from pvr.gui.guiconfig import *
import pvr.elismgr

from pvr.gui.basewindow import SettingWindow
from pvr.gui.basewindow import Action
from elisproperty import ElisPropertyInt


class OneCableConfiguration2( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
		self.commander = pvr.elismgr.getInstance().getCommander()
		self.satelliteCount = 0
		self.satellitelist = []
		self.scrList = [ 'SCR(0)', 'SCR(1)', 'SCR(2)', 'SCR(3)', 'SCR(4)', 'SCR(5)', 'SCR(6)', 'SCR(7)' ]

	def onInit( self ):
		self.tunerIndex = configmgr.getInstance( ).getCurrentTunerIndex( )
	
		self.setHeaderLabel( 'OneCable Configuration' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'OneCable configuration' )

		self.currentSatellite = configmgr.getInstance( ).getCurrentConfiguredSatellite( )

		self.addEnumControl( E_SpinEx01, 'MDU' )

		pinCode = ElisPropertyInt( 'Tuner%d Pin Code' % ( self.tunerIndex + 1 ), self.commander ).getProp( )
		self.addInputControl( E_Input01, 'Tuner %d PIN-Code' % ( self.tunerIndex + 1 ), '%d' % pinCode, 0 )

		tunerScr = ElisPropertyInt( 'Tuner%d SCR' % ( self.tunerIndex + 1 ), self.commander ).getProp( )
		self.addUserEnumControl( E_SpinEx02, 'Tuner %d' % ( self.tunerIndex + 1 ), self.scrList, tunerScr )

		tunerFrequency = ElisPropertyInt( 'Tuner%d SCR Frequency' % ( self.tunerIndex + 1 ), self.commander ).getProp( )
		self.addUserEnumControl( E_SpinEx03, 'Tuner %d Frequency' % ( self.tunerIndex + 1 ), E_LIST_ONE_CABLE_TUNER_FREQUENCY, getOneCableTunerFrequencyIndex( '%d' % tunerFrequency ) )
		self.initControl( )

				
	def onAction( self, action ):

		actionId = action.getId( )
		focusId = self.getFocusId( )
		groupId = self.getGroupId( focusId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			if xbmcgui.Dialog( ).yesno('Configure', 'Are you sure?') == 1 :
				ElisPropertyInt( 'Tuner%d Pin Code' % ( self.tunerIndex + 1 ), self.commander ).setProp( int( self.getControl( E_Input01 + 3 ).getListItem(0).getLabel2( ) ) )
				ElisPropertyInt( 'Tuner%d SCR' % ( self.tunerIndex + 1 ), self.commander ).setProp( self.getSelectedIndex( E_SpinEx02 ) ) 
				ElisPropertyInt( 'Tuner%d SCR Frequency' % ( self.tunerIndex + 1 ), self.commander ).setProp( int( E_LIST_ONE_CABLE_TUNER_FREQUENCY[self.getSelectedIndex( E_SpinEx03 )] ))
				
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

		if groupId == E_Input01 :
			self.controlkeypad( groupId, actionId )


	def onClick( self, controlId ):
		groupId = self.getGroupId( controlId )

		if( groupId == E_SpinEx01 ) :
			self.controlSelect( )
			self.currentSatellite[E_CONFIGURE_SATELLITE_ONECABLE_MDU] = '%d' % self.getSelectedIndex( E_SpinEx01 )
			
		elif( groupId == E_Input01 ) :
			self.controlSelect( )
			self.currentSatellite[E_CONFIGURE_SATELLITE_ONECABLE_PIN] = self.getControl( E_Input01 + 3 ).getListItem( 0 ).getLabel2( )

		elif( groupId == E_SpinEx02 ) :
			self.currentSatellite[E_CONFIGURE_SATELLITE_ONECABLE_UBSLOT] = '%d' % self.getSelectedIndex( E_SpinEx02 )

		elif( groupId == E_SpinEx03 ) :
			self.currentSatellite[E_CONFIGURE_SATELLITE_ONECABLE_UBFREQ] = E_LIST_ONE_CABLE_TUNER_FREQUENCY[self.getSelectedIndex( E_SpinEx03 )]
		print 'dhkim test currentSatellite = %s' % self.currentSatellite


	def onFocus( self, controlId ):
		pass