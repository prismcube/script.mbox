import xbmc
import xbmcgui
import sys

import pvr.gui.DialogMgr as DiaMgr
import pvr.TunerConfigMgr as ConfigMgr
from pvr.gui.GuiConfig import *
from pvr.gui.BaseWindow import SettingWindow, Action


class EditSatellite( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )

		self.mInitialized = False
		self.mSatelliteIndex = 0
		self.mLastFocused = -1
			
	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		if ConfigMgr.GetInstance( ).GetNeedLoad( ) == True : 
			ConfigMgr.GetInstance( ).LoadOriginalTunerConfig( )
			ConfigMgr.GetInstance( ).Load( )		
			ConfigMgr.GetInstance( ).SetNeedLoad( False )

	
		self.InitConfig( )
		self.SetSettingWindowLabel( 'Edit Satellite' )
		self.mInitialized = True
		
		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.ResetAllControl( )
			ConfigMgr.GetInstance( ).SetNeedLoad( True )
			self.close( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			ConfigMgr.GetInstance( ).SetNeedLoad( True )
			self.close( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			pass

		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass
			
		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			self.ShowDescription( focusId )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )
			self.ShowDescription( focusId )


	def onClick( self, aControlId ) :
		groupId = self.GetGroupId( aControlId )
		
		# Select Satellite
		if groupId == E_Input01 :
			satelliteList = ConfigMgr.GetInstance( ).GetFormattedNameList( )
			dialog = xbmcgui.Dialog()
 			select = dialog.select( 'Select satellite', satelliteList )

			if select >= 0 and select != self.mSatelliteIndex :
	 			self.mSatelliteIndex = select
	 			self.InitConfig( )

	 	# Edit Satellite Name
		elif groupId == E_Input03 :
			satellite = ConfigMgr.GetInstance( ).GetSatelliteByIndex( self.mSatelliteIndex )
			kb = xbmc.Keyboard( satellite.mName, 'Satellite Name', False )
			kb.doModal( )
			if( kb.isConfirmed( ) ) :
				ret = ConfigMgr.GetInstance( ).EditSatellite( satellite.mLongitude, satellite.mBand, kb.getText( ) )
				print 'dhkim test Edit Satellite return val = %s' % ret
				self.InitConfig( )

		# Add New Satellite
		elif groupId == E_Input04 :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_ADD_NEW_SATELLITE )
 			dialog.doModal( )

			if dialog.IsOK() == E_DIALOG_STATE_YES :
				longitude, band, satelliteName = dialog.GetValue( )
				ret = ConfigMgr.GetInstance( ).AddSatellite( longitude, band, satelliteName )

				print 'dhkim test  Add New Satellite return val = %s' % ret
				if ret == True :
					dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( 'ERROR', 'ok' )
		 			dialog.doModal( )
		 		else :
		 			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( 'ERROR', 'fail' )
		 			dialog.doModal( )
				self.InitConfig( )
			else :
				return
				 
		# Delete Satellite
		elif groupId == E_Input05 :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( 'Confirm', 'Do you want to delete satellite?' )
			dialog.doModal( )

			if dialog.IsOK() == E_DIALOG_STATE_YES :
				satellite = ConfigMgr.GetInstance( ).GetSatelliteByIndex( self.mSatelliteIndex )
				ret = ConfigMgr.GetInstance( ).DeleteSatellite( satellite.mLongitude, satellite.mBand )
				print 'dhkim test Delete Satellite return val = %s' % ret
				self.mSatelliteIndex = 0
				self.InitConfig( )
			else :
				return
		
	def onFocus( self, aControlId ):
		if self.mInitialized == False :
			return
		if ( self.mLastFocused != aControlId ) :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId


	def InitConfig( self ) :
		self.ResetAllControl( )

		ConfigMgr.GetInstance( ).ReloadAllSatelliteList( )
		satellite = ConfigMgr.GetInstance( ).GetSatelliteByIndex( self.mSatelliteIndex )
		satellitename = ConfigMgr.GetInstance( ).GetFormattedName( satellite.mLongitude , satellite.mBand )
		self.AddInputControl( E_Input01, 'Satellite', satellitename, 'Select satellite.' )
		longitude = ConfigMgr.GetInstance( ).GetFormattedLongitude( satellite.mLongitude , satellite.mBand )
		self.AddInputControl( E_Input02, 'Longitude', longitude )
		self.AddInputControl( E_Input03, 'Edit Satellite Name', '', 'Edit satellite name.' )
		self.AddInputControl( E_Input04, 'Add New Satellite', '', 'Add new satellite.' )
		self.AddInputControl( E_Input05, 'Delete Satellite', '', 'Delete satellite.' )
		
		self.InitControl( )
		self.ShowDescription( self.getFocusId( ) )
		self.SetEnableControl( E_Input02, False )
		self.DisableControl( )
		
	def DisableControl( self ) :
		
		if self.mSatelliteIndex == 0 :
			self.SetEnableControl( E_Input05, False )
			
		else :
			self.SetEnableControl( E_Input05, True )

