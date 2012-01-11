import xbmc
import xbmcgui
import sys

import pvr.gui.DialogMgr as DiaMgr
import pvr.TunerConfigMgr as ConfigMgr
from pvr.gui.GuiConfig import *
from pvr.gui.BaseWindow import SettingWindow, Action
from ElisEnum import ElisEnum
from ElisProperty import ElisPropertyEnum
import pvr.ElisMgr


class EditTransponder( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )

		self.mInitialized = False
		self.mSatelliteIndex = 0
		self.mTransponderIndex = 0
		self.mLastFocused = -1
		self.mTransponderList = []
			
	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		if ConfigMgr.GetInstance( ).GetNeedLoad( ) == True : 
			ConfigMgr.GetInstance( ).LoadOriginalTunerConfig( )
			ConfigMgr.GetInstance( ).Load( )		
			ConfigMgr.GetInstance( ).SetNeedLoad( False )

		self.SetHeaderLabel( 'Edit Transponder' )
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

	 	# Select frequency
	 	elif groupId == E_Input02 :
	 		frequencylist = []
	 		for i in range( len( self.mTransponderList ) ) :
	 			frequencylist.append( '%d MHz' % self.mTransponderList[i].mFrequency )

	 		dialog = xbmcgui.Dialog()
 			ret = dialog.select( 'Select Transponder', frequencylist )

 			if ret >= 0 :
	 			self.mTransponderIndex = ret
	 			self.InitConfig( )




	 	# Delete Transponder
	 	elif groupId == E_Input06 :
	 		if xbmcgui.Dialog( ).yesno('Confirm', 'Do you want to delete transponder?') == 1 :
		 		satellite = ConfigMgr.GetInstance( ).GetSatelliteByIndex( self.mSatelliteIndex )
		 		tmplist = []
		 		tmplist.append( self.mTransponderList[self.mTransponderIndex] )
		 		self.mCommander.Transponder_Delete( satellite.mLongitude,  satellite.mBand,  tmplist )
		 		xbmc.sleep(2)
		 		self.mTransponderIndex = 0
				self.InitConfig( )
			else :
				return
		"""
	 	# Edit Satellite Name
		if groupId == E_Input03 :
			satellite = ConfigMgr.GetInstance( ).GetSatelliteByIndex( self.mSatelliteIndex )
			kb = xbmc.Keyboard( satellite.mName, 'Satellite Name', False )
			kb.doModal( )
			if( kb.isConfirmed( ) ) :
				ConfigMgr.GetInstance( ).EditSatellite( satellite.mLongitude, satellite.mBand, kb.getText( ) )
				self.InitConfig( )

		# Add New Satellite
		if groupId == E_Input04 :
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
		if groupId == E_Input05 :
			satellite = ConfigMgr.GetInstance( ).GetSatelliteByIndex( self.mSatelliteIndex )
			ConfigMgr.GetInstance( ).DeleteSatellite( satellite.mLongitude, satellite.mBand )
			self.mSatelliteIndex = 0
			self.InitConfig( )
		"""
	def onFocus( self, aControlId ):
		if self.mInitialized == False :
			return
		if ( self.mLastFocused != aControlId ) :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId


	def InitConfig( self ) :
		self.ResetAllControl( )

		satellite = ConfigMgr.GetInstance( ).GetSatelliteByIndex( self.mSatelliteIndex )
		satellitename = ConfigMgr.GetInstance( ).GetFormattedName( satellite.mLongitude , satellite.mBand )
		self.AddInputControl( E_Input01, 'Satellite', satellitename, None, None, None, 'Select satellite.' )

		self.mTransponderList = self.mCommander.Transponder_GetList( satellite.mLongitude, satellite.mBand )
		print 'dhkim test list transponder = %s' % self.mTransponderList
		print 'dhkim test len transponder = %d' % len( self.mTransponderList )
		"""
		for test
		"""
		for trans in self.mTransponderList :
			trans.printdebug()
		self.AddInputControl( E_Input02, 'Frequency', '%d MHz' % self.mTransponderList[self.mTransponderIndex].mFrequency, None, None, None, 'Select Frequency.' )
		self.AddInputControl( E_Input03, 'Symbol Rate', '%d KS/s' % self.mTransponderList[self.mTransponderIndex].mSymbolRate )

		property = ElisPropertyEnum( 'Polarisation', self.mCommander )
		self.AddInputControl( E_Input04, 'Polarization', property.GetPropStringByIndex( self.mTransponderList[self.mTransponderIndex].mPolarization ) )
		self.AddLeftLabelButtonControl( E_Input05, 'Add New Transponder', 'Add new transponder.' )
		self.AddLeftLabelButtonControl( E_Input06, 'Delete Transponder', 'Delete transponder.' )
		self.AddLeftLabelButtonControl( E_Input07, 'Edit Transponder', 'Edit transponder.' )
		
		self.InitControl( )
		self.ShowDescription( self.getFocusId( ) )
		self.SetEnableControl( E_Input03, False )
		self.SetEnableControl( E_Input04, False )

