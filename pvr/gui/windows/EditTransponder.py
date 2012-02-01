import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DiaMgr
import pvr.TunerConfigMgr as ConfigMgr
from pvr.gui.BaseWindow import SettingWindow, Action
import pvr.ElisMgr
from ElisClass import *
from ElisProperty import ElisPropertyEnum
from pvr.gui.GuiConfig import *


class EditTransponder( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
 
		self.mTransponderList = []
		self.mInitialized 		= False
		self.mSatelliteIndex 	= 0
		self.mTransponderIndex = 0
		self.mLastFocused 		= -1

			
	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		if ConfigMgr.GetInstance( ).GetNeedLoad( ) == True : 
			ConfigMgr.GetInstance( ).LoadOriginalTunerConfig( )
			ConfigMgr.GetInstance( ).Load( )		
			ConfigMgr.GetInstance( ).SetNeedLoad( False )

		self.InitConfig( )
		self.SetSettingWindowLabel( 'Edit Transponder' )
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
			dialog = xbmcgui.Dialog( )
 			select = dialog.select( 'Select satellite', satelliteList )

			if select >= 0 and select != self.mSatelliteIndex :
	 			self.mSatelliteIndex = select
	 			self.InitConfig( )

	 	# Select frequency
	 	elif groupId == E_Input02 :
	 		if len( self.mTransponderList ) <= 0 :
	 			xbmcgui.Dialog( ).ok( 'Information', 'Satellite has no transponder info.\nFirst add new transponder' )
	 		else :
		 		frequencylist = []
		 		for i in range( len( self.mTransponderList ) ) :
		 			frequencylist.append( '%d MHz' % self.mTransponderList[i].mFrequency )

		 		dialog = xbmcgui.Dialog( )
	 			select = dialog.select( 'Select Transponder', frequencylist )

	 			if select >= 0 and select != self.mTransponderIndex :
		 			self.mTransponderIndex = select
		 			self.InitConfig( )

		# Add Transponder
		elif groupId == E_Input05 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SET_TRANSPONDER )
 			dialog.SetDefaultValue( 0, 0, 0, 0 )
 			dialog.doModal( )

 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				frequency, fec, polarization, simbolrate = dialog.GetValue( )
 			
 				newTransponder = ElisITransponderInfo( )
 				newTransponder.reset( )
 				newTransponder.mFrequency = frequency
				newTransponder.mSymbolRate = simbolrate
				newTransponder.mPolarization = polarization
				newTransponder.mFECMode = fec
 				
 				tmplist = []
		 		tmplist.append( newTransponder )
		 		satellite = ConfigMgr.GetInstance( ).GetSatelliteByIndex( self.mSatelliteIndex )
 				self.mCommander.Transponder_Add( satellite.mLongitude, satellite.mBand, tmplist )
 				self.mTransponderIndex = 0
				self.InitConfig( )
			else :
				return

		# Edit Transponder
		elif groupId == E_Input07 :
			if len( self.mTransponderList ) <= 0 :
	 			xbmcgui.Dialog( ).ok( 'Information', 'Satellite has no transponder info.\nFirst add new transponder' )
	 		else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SET_TRANSPONDER )
	 			dialog.SetDefaultValue( self.mTransponderList[self.mTransponderIndex].mFrequency, self.mTransponderList[self.mTransponderIndex].mFECMode, self.mTransponderList[self.mTransponderIndex].mPolarization, self.mTransponderList[self.mTransponderIndex].mSymbolRate)
	 			dialog.doModal( )

	 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
	 				satellite = ConfigMgr.GetInstance( ).GetSatelliteByIndex( self.mSatelliteIndex )
	 				
					# Delete
					tmplist = []
			 		tmplist.append( self.mTransponderList[self.mTransponderIndex] )
			 		self.mCommander.Transponder_Delete( satellite.mLongitude, satellite.mBand, tmplist )
					
	 				# ADD
					frequency, fec, polarization, simbolrate = dialog.GetValue( )
	 			
	 				newTransponder = ElisITransponderInfo( )
	 				newTransponder.reset( )
	 				newTransponder.mFrequency = frequency
					newTransponder.mSymbolRate = simbolrate
					newTransponder.mPolarization = polarization
					newTransponder.mFECMode = fec
	 				
	 				tmplist = []
			 		tmplist.append( newTransponder )
			 		
	 				ret = self.mCommander.Transponder_Add( satellite.mLongitude, satellite.mBand, tmplist )
	 				self.mTransponderIndex = 0
					self.InitConfig( )
				else :
					return

	 	# Delete Transponder
	 	elif groupId == E_Input06 :
	 		if len( self.mTransponderList ) <= 0 :
	 			xbmcgui.Dialog( ).ok( 'Information', 'Satellite has no transponder info.\nFirst add new transponder' )
	 		else :
		 		if xbmcgui.Dialog( ).yesno('Confirm', 'Do you want to delete transponder?') == 1 :
			 		satellite = ConfigMgr.GetInstance( ).GetSatelliteByIndex( self.mSatelliteIndex )
			 		tmplist = []
			 		tmplist.append( self.mTransponderList[self.mTransponderIndex] )
			 		self.mCommander.Transponder_Delete( satellite.mLongitude, satellite.mBand, tmplist )
			 		self.mTransponderIndex = 0
					self.InitConfig( )
				else :
					return
		
	def onFocus( self, aControlId ):
		if self.mInitialized == False :
			return
		if self.mLastFocused != aControlId :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId
	

	def InitConfig( self ) :
		self.ResetAllControl( )

		satellite = ConfigMgr.GetInstance( ).GetSatelliteByIndex( self.mSatelliteIndex )
		satellitename = ConfigMgr.GetInstance( ).GetFormattedName( satellite.mLongitude , satellite.mBand )
		self.AddInputControl( E_Input01, 'Satellite', satellitename, 'Select satellite.' )

		self.mTransponderList = self.mCommander.Transponder_GetList( satellite.mLongitude, satellite.mBand )

		for i in range( len( self.mTransponderList ) ) :
 			if self.mTransponderList[i].mError < 0 :
 				self.mTransponderList = []

		if len( self.mTransponderList ) <= 0 :
			self.AddInputControl( E_Input02, 'Frequency', 'None', 'Select Frequency.' )
			self.AddInputControl( E_Input03, 'Symbol Rate', 'None' )

			property = ElisPropertyEnum( 'Polarisation', self.mCommander )
			self.AddInputControl( E_Input04, 'Polarization', 'None' )

		else :
			self.AddInputControl( E_Input02, 'Frequency', '%d MHz' % self.mTransponderList[self.mTransponderIndex].mFrequency, 'Select Frequency.' )
			self.AddInputControl( E_Input03, 'Symbol Rate', '%d KS/s' % self.mTransponderList[self.mTransponderIndex].mSymbolRate )

			property = ElisPropertyEnum( 'Polarisation', self.mCommander )
			self.AddInputControl( E_Input04, 'Polarization', property.GetPropStringByIndex( self.mTransponderList[self.mTransponderIndex].mPolarization ) )

		self.AddInputControl( E_Input05, 'Add New Transponder', '', 'Add new transponder.' )
		self.AddInputControl( E_Input06, 'Delete Transponder', '', 'Delete transponder.' )
		self.AddInputControl( E_Input07, 'Edit Transponder', '', 'Edit transponder.' )
		
		self.InitControl( )
		self.ShowDescription( self.getFocusId( ) )
		self.SetEnableControl( E_Input03, False )
		self.SetEnableControl( E_Input04, False )
