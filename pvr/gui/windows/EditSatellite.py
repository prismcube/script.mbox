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

		self.SetHeaderLabel( 'Edit Satellite' )
		self.SetFooter( FooterMask.G_FOOTER_ICON_BACK_MASK )

		self.InitConfig( )
		self.mInitialized = True
		
		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.ResetAllControl( )
			self.close( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
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
 			ret = dialog.select( 'Select satellite', satelliteList )

			if ret >= 0 :
	 			self.mSatelliteIndex = ret
	 			self.InitConfig( )

	 	# Edit Satellite Name
		elif groupId == E_Input03 :
			satellite = ConfigMgr.GetInstance( ).GetSatelliteByIndex( self.mSatelliteIndex )
			kb = xbmc.Keyboard( satellite.mName, 'Satellite Name', False )
			kb.doModal( )
			if( kb.isConfirmed( ) ) :
				ConfigMgr.GetInstance( ).EditSatellite( satellite.mLongitude, satellite.mBand, kb.getText( ) )
				self.InitConfig( )

		# Add New Satellite
		elif groupId == E_Input04 :
			kb = xbmc.Keyboard( '', 'Satellite Name', False )
			kb.doModal( )
			if( kb.isConfirmed( ) ) :
				satelliteName = kb.getText( )
				
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_ADD_NEW_SATELLITE )
 				dialog.doModal( )

				if dialog.IsOK() == True :
					longitude, band = dialog.GetValue( )
					ConfigMgr.GetInstance( ).AddSatellite( longitude, band, satelliteName )
					self.InitConfig( )
				else :
					return
				 
		# Delete Satellite
		elif groupId == E_Input05 :
			if xbmcgui.Dialog( ).yesno('Confirm', 'Do you want to delete satellite?') == 1 :
				satellite = ConfigMgr.GetInstance( ).GetSatelliteByIndex( self.mSatelliteIndex )
				ConfigMgr.GetInstance( ).DeleteSatellite( satellite.mLongitude, satellite.mBand )
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
		self.AddInputControl( E_Input01, 'Satellite', satellitename, None, None, None, 'Select satellite.' )
		longitude = ConfigMgr.GetInstance( ).GetFormattedLongitude( satellite.mLongitude , satellite.mBand )
		self.AddInputControl( E_Input02, 'Longitude', longitude )
		self.AddLeftLabelButtonControl( E_Input03, 'Edit Satellite Name', 'Edit satellite name.' )
		self.AddLeftLabelButtonControl( E_Input04, 'Add New Satellite', 'Add new satellite.' )
		self.AddLeftLabelButtonControl( E_Input05, 'Delete Satellite', 'Delete satellite.' )
		
		self.InitControl( )
		self.ShowDescription( self.getFocusId( ) )
		self.SetEnableControl( E_Input02, False )
		self.DisableControl( )
		
	def DisableControl( self ) :
		
		if self.mSatelliteIndex == 0 :
			self.SetEnableControl( E_Input05, False )
			
		else :
			self.SetEnableControl( E_Input05, True )

