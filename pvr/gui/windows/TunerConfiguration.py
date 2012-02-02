import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.TunerConfigMgr as ConfigMgr
import pvr.gui.DialogMgr as DiaMgr
from pvr.TunerConfigMgr import *
from pvr.gui.GuiConfig import *
from pvr.gui.BaseWindow import SettingWindow, Action
from ElisProperty import ElisPropertyEnum
import pvr.ElisMgr

E_MAIN_LIST_ID = 9000

class TunerConfiguration( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs)
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.listItems= []
			
	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.tunerIndex = ConfigMgr.GetInstance().GetCurrentTunerIndex( )

		if self.tunerIndex == E_TUNER_1 :
			property = ElisPropertyEnum( 'Tuner1 Type', self.mCommander )
		elif self.tunerIndex == E_TUNER_2 : 
			property = ElisPropertyEnum( 'Tuner2 Type', self.mCommander )
		else :
			print 'Error : unknown Tuner'
			property = ElisPropertyEnum( 'Tuner1 Type', self.mCommander )
			
		headerLabel = 'Tuner %d Configuration' % ( self.tunerIndex + 1 )

		self.SetSettingWindowLabel( headerLabel )
		
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'Tuner %d Configuration : %s' % ( self.tunerIndex + 1, property.GetPropString( ) ) )
		self.InitConfig( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_PARENT_DIR :
			self.getControl( E_MAIN_LIST_ID ).reset( )
			self.close( )

		elif actionId == Action.ACTION_MOVE_LEFT or actionId == Action.ACTION_MOVE_RIGHT :			
			pass
	
		elif actionId == Action.ACTION_MOVE_UP :
			pass

		elif actionId == Action.ACTION_MOVE_DOWN :
			pass


	def onClick( self, aControlId ):
		if aControlId == E_MAIN_LIST_ID : 
			position = self.getControl( E_MAIN_LIST_ID ).getSelectedPosition( )
			
			configuredList = ConfigMgr.GetInstance().GetConfiguredSatelliteList( )

			if len( configuredList ) == position :
				dialog = xbmcgui.Dialog()
				satelliteList = ConfigMgr.GetInstance( ).GetFormattedNameList( )
	 			ret = dialog.select( 'Select satellite', satelliteList )

	 			if ret >= 0 :
					ConfigMgr.GetInstance().AddConfiguredSatellite( ret )
	 				self.ReloadConfigedSatellite()

	 		elif len( configuredList ) + 1 == position :
	 			if len( configuredList ) <= 0 :
	 				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( 'ERROR', 'Empty Configured Satellite' )
		 			dialog.doModal( )
	 				return
	 			else :
					dialog = xbmcgui.Dialog()
		 			ret = dialog.select( 'delete satellite', self.listItems[ 0 : len( configuredList ) ] )
 
		 			if ret >= 0 :
		 				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
						dialog.SetDialogProperty( 'Configure', 'Delete Satellite : %s' % self.listItems[ ret ] )
						dialog.doModal( )

						if dialog.IsOK() == E_DIALOG_STATE_YES :
			 				ConfigMgr.GetInstance().DeleteConfiguredSatellitebyIndex( ret )
			 				self.ReloadConfigedSatellite()

			else :		
				config = configuredList[ position ]
				if config != [] :
					ConfigMgr.GetInstance( ).SetCurrentConfigIndex( position )
					self.ResetAllControl( )
					tunertype = ConfigMgr.GetInstance( ).GetCurrentTunerType( )
					
					if tunertype == E_DISEQC_1_0 :
						WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CONFIG_DISEQC_10 )

					elif tunertype == E_DISEQC_1_1 :
						WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CONFIG_DISEQC_11 )
					
					elif tunertype == E_MOTORIZE_1_2 :
						WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CONFIG_MOTORIZED_12 )

					elif tunertype == E_MOTORIZE_USALS :
						WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CONFIG_MOTORIZED_USALS2 )

				else :
					print 'ERR : Can not find configured satellite'


	def onFocus( self, aControlId ):
		pass


	def InitConfig( self ):
		self.ReloadConfigedSatellite()


	def ReloadConfigedSatellite( self ):
		configuredList = []
		self.listItems = []

		configuredList = ConfigMgr.GetInstance( ).GetConfiguredSatelliteList( )

		for config in configuredList :
			self.listItems.append( '%s' % ConfigMgr.GetInstance( ).GetFormattedName( config.mSatelliteLongitude, config.mBandType ) )

		self.listItems.append( 'Add New Satellite' )
		self.listItems.append( 'Delete Satellite' )
		self.getControl( E_MAIN_LIST_ID ).addItems( self.listItems )

		
