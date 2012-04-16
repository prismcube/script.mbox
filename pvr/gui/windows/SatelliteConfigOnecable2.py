import xbmc
import xbmcgui
import sys

import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.GuiConfig import *
from pvr.gui.BaseWindow import SettingWindow, Action
from ElisProperty import ElisPropertyInt


class SatelliteConfigOnecable2( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )

		self.mTunerIndex				= 0
		self.mCurrentSatellite			= []
		self.mCurrentSatellite2			= []
		self.mOneCablesatelliteCount	= 0

		self.mLoadConfig				= True
		
		self.mSavedTunerPin				= [ 0, 0 ]
		self.mSavedTunerScr				= [ 0, 0 ]
		self.mSavedTunerFreq			= [ 0, 0 ]

		self.mTempTunerPin				= [ 0, 0 ]
		self.mTempTunerScr				= [ 0, 0 ]
		self.mTempTunerFreq				= [ 0, 0 ]

	def onInit( self ) :
		self.SetSettingWindowLabel( 'OneCable Configuration' )
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'OneCable configuration' )
		self.mOneCablesatelliteCount = self.mTunerMgr.GetOneCableSatelliteCount( )
		self.mCurrentSatellite = []
		self.mCurrentSatellite2 = []

		if self.mLoadConfig == True :
			self.LoadConfig( )
			self.mLoadConfig = False

		self.InitConfig( )
				
	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )				

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.onClose( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.onClose( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )
			
		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )


	def onClick( self, controlId ) :
		groupId = self.GetGroupId( controlId )

		if groupId == E_SpinEx01 :
			self.ControlSelect( )
			self.DisableControl( )
			
		elif groupId == E_Input01 or groupId == E_Input02 :
			if self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
				dialog.SetDialogProperty( 'Tuner%d Pin Code' % ( self.mTunerIndex + 1 ), '%03d' % self.mTempTunerPin[self.mTunerIndex], 3 )
	 			dialog.doModal( )
	 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
	 				self.mTempTunerPin[self.mTunerIndex] = int( dialog.GetString( ) )

			elif self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
				if groupId == E_Input01 :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
					dialog.SetDialogProperty( 'Tuner1 Pin Code', '%03d' % self.mTempTunerPin[0], 3 )
		 			dialog.doModal( )
		 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
						self.mTempTunerPin[0] = int( dialog.GetString( ) )
					
				elif groupId == E_Input02 :					
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
					dialog.SetDialogProperty( 'Tuner2 Pin Code', '%03d' % self.mTempTunerPin[1], 3 )
		 			dialog.doModal( )
		 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
						self.mTempTunerPin[1] = int( dialog.GetString( ) )

			self.InitConfig( )

	def onFocus( self, aControlId ) :
		pass

	def onClose( self ) :
		if self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
			if self.GetSelectedIndex( E_SpinEx02 ) == self.GetSelectedIndex( E_SpinEx04 ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'ERROR', 'Please set a different value for each tuner.' )
	 			dialog.doModal( )
				return
			if self.GetSelectedIndex( E_SpinEx03 ) == self.GetSelectedIndex( E_SpinEx05 ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'ERROR', 'Please set a different value for each tuner.' )
	 			dialog.doModal( )
				return

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( 'Configure', 'Save Configuration?' )
		dialog.doModal( )
	
		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			self.SaveConfig( )
			
		elif dialog.IsOK( ) == E_DIALOG_STATE_NO :
			self.ReLoadConfig( )

		elif dialog.IsOK( ) == E_DIALOG_STATE_CANCEL :
			return
			
		self.mLoadConfig = True
		self.close( )


	def InitConfig( self ) :
		self.ResetAllControl( )
		
		if self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
			self.AddEnumControl( E_SpinEx01, 'MDU' )
			self.AddInputControl( E_Input01, 'Tuner %d PIN-Code' % ( self.mTunerIndex + 1 ), '%03d' % self.mTempTunerPin[self.mTunerIndex] )
			self.AddUserEnumControl( E_SpinEx02, 'Tuner %d' % ( self.mTunerIndex + 1 ), E_LIST_ONE_CABLE_SCR, self.mTempTunerScr[self.mTunerIndex] )
			self.AddUserEnumControl( E_SpinEx03, 'Tuner %d Frequency' % ( self.mTunerIndex + 1 ), E_LIST_ONE_CABLE_TUNER_FREQUENCY, getOneCableTunerFrequencyIndex( '%d' % self.mTempTunerFreq[self.mTunerIndex] ) )

			disableControls = [ E_Input02, E_SpinEx04, E_SpinEx05 ]
			self.SetVisibleControls( disableControls, False )
			self.SetEnableControls( disableControls, False )

		elif self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
			self.AddEnumControl( E_SpinEx01, 'MDU' )
			self.AddInputControl( E_Input01, 'Tuner1 PIN-Code', '%03d' % self.mTempTunerPin[0] )
			self.AddUserEnumControl( E_SpinEx02, 'Tuner 1', E_LIST_ONE_CABLE_SCR, self.mTempTunerScr[0] )
			self.AddUserEnumControl( E_SpinEx03, 'Tuner 1 Frequency', E_LIST_ONE_CABLE_TUNER_FREQUENCY, getOneCableTunerFrequencyIndex( '%d' % self.mTempTunerFreq[0] ) )

			self.AddInputControl( E_Input02, 'Tuner2 PIN-Code', '%03d' % self.mTempTunerPin[1] )
			self.AddUserEnumControl( E_SpinEx04, 'Tuner 2', E_LIST_ONE_CABLE_SCR, self.mTempTunerScr[1] )
			self.AddUserEnumControl( E_SpinEx05, 'Tuner 2 Frequency', E_LIST_ONE_CABLE_TUNER_FREQUENCY, getOneCableTunerFrequencyIndex( '%d' % self.mTempTunerFreq[1] ) )

		self.InitControl( )
		self.DisableControl( )
		
	def DisableControl( self ) :
		selectedIndex = self.GetSelectedIndex( E_SpinEx01 )
		enableControls = [ E_Input01, E_Input02 ]
		if selectedIndex == 0 :
			if self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
				self.SetEnableControl( E_Input01, False )
			elif self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
				self.SetEnableControls( enableControls, False )
		else :
			if self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
				self.SetEnableControl( E_Input01, True )
			elif self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
				self.SetEnableControls( enableControls, True )

	def LoadConfig( self ) :
		if self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
			self.mTunerIndex = self.mTunerMgr.GetCurrentTunerIndex( )
			
			self.mSavedTunerPin[self.mTunerIndex] = ElisPropertyInt( 'Tuner%d Pin Code' % ( self.mTunerIndex + 1 ), self.mCommander ).GetProp( )
			self.mTempTunerPin[self.mTunerIndex] = self.mSavedTunerPin[self.mTunerIndex]
			
			self.mSavedTunerScr[self.mTunerIndex] =  ElisPropertyInt( 'Tuner%d SCR' % ( self.mTunerIndex + 1 ), self.mCommander ).GetProp( )
			self.mTempTunerScr[self.mTunerIndex] = self.mSavedTunerScr[self.mTunerIndex]
			
			self.mSavedTunerFreq[self.mTunerIndex] = ElisPropertyInt( 'Tuner%d SCR Frequency' % ( self.mTunerIndex + 1 ), self.mCommander ).GetProp( )
			self.mTempTunerFreq[self.mTunerIndex] = self.mSavedTunerFreq[self.mTunerIndex]

		elif self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
			self.mSavedTunerPin[0] = ElisPropertyInt( 'Tuner1 Pin Code', self.mCommander ).GetProp( )
			self.mTempTunerPin[0] = self.mSavedTunerPin[0]

			self.mSavedTunerScr[0] =  ElisPropertyInt( 'Tuner1 SCR' , self.mCommander ).GetProp( )
			self.mTempTunerScr[0] = self.mSavedTunerScr[0]

			self.mSavedTunerFreq[0] = ElisPropertyInt( 'Tuner1 SCR Frequency', self.mCommander ).GetProp( )
			self.mTempTunerFreq[0] = self.mSavedTunerFreq[0]

			self.mSavedTunerPin[1] = ElisPropertyInt( 'Tuner2 Pin Code', self.mCommander ).GetProp( )
			self.mTempTunerPin[1] = self.mSavedTunerPin[1]

			self.mSavedTunerScr[1] =  ElisPropertyInt( 'Tuner2 SCR' , self.mCommander ).GetProp( )
			self.mTempTunerScr[1] = self.mSavedTunerScr[1]

			self.mSavedTunerFreq[1] = ElisPropertyInt( 'Tuner2 SCR Frequency', self.mCommander ).GetProp( )
			self.mTempTunerFreq[1] = self.mSavedTunerFreq[1]

		
	def ReLoadConfig( self ) :
		if self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
			ElisPropertyInt( 'Tuner%d Pin Code' % ( self.mTunerIndex + 1 ), self.mCommander ).SetProp( self.mSavedTunerPin[self.mTunerIndex] )
			ElisPropertyInt( 'Tuner%d SCR' % ( self.mTunerIndex + 1 ), self.mCommander ).SetProp( self.mSavedTunerScr[self.mTunerIndex] )
			ElisPropertyInt( 'Tuner%d SCR Frequency' % ( self.mTunerIndex + 1 ), self.mCommander ).SetProp( self.mSavedTunerFreq[self.mTunerIndex]  )

		elif self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
			ElisPropertyInt( 'Tuner1 Pin Code', self.mCommander ).SetProp( self.mSavedTunerPin[0] )
			ElisPropertyInt( 'Tuner1 SCR' , self.mCommander ).SetProp( self.mSavedTunerScr[0] )
			ElisPropertyInt( 'Tuner1 SCR Frequency', self.mCommander ).SetProp( self.mSavedTunerFreq[0] )
			ElisPropertyInt( 'Tuner2 Pin Code', self.mCommander ).SetProp( self.mSavedTunerPin[1] )
			ElisPropertyInt( 'Tuner2 SCR' , self.mCommander ).SetProp( self.mSavedTunerScr[1] )
			ElisPropertyInt( 'Tuner2 SCR Frequency', self.mCommander ).SetProp( self.mSavedTunerFreq[1] )

	def SaveConfig( self ) :
		if self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
			ElisPropertyInt( 'Tuner%d Pin Code' % ( self.mTunerIndex + 1 ), self.mCommander ).SetProp( self.mTempTunerPin[self.mTunerIndex] )
			ElisPropertyInt( 'Tuner%d SCR' % ( self.mTunerIndex + 1 ), self.mCommander ).SetProp( self.GetSelectedIndex( E_SpinEx02 ) ) 
			ElisPropertyInt( 'Tuner%d SCR Frequency' % ( self.mTunerIndex + 1 ), self.mCommander ).SetProp( int( E_LIST_ONE_CABLE_TUNER_FREQUENCY[ self.GetSelectedIndex( E_SpinEx03 ) ] ) )

			for i in range( self.mOneCablesatelliteCount ) :
				satellite = self.mTunerMgr.GetConfiguredSatellitebyIndex( i )
				
				satellite.mOneCableMDU = self.GetSelectedIndex( E_SpinEx01 )
				satellite.mOneCablePin = int( self.GetControlLabel2String( E_Input01 ) )
				satellite.mOneCableUBSlot = self.GetSelectedIndex( E_SpinEx02 )
				satellite.mOneCableUBFreq = int( E_LIST_ONE_CABLE_TUNER_FREQUENCY[ self.GetSelectedIndex( E_SpinEx03 ) ] )

				self.mCurrentSatellite.append( satellite )

		elif self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
			ElisPropertyInt( 'Tuner1 Pin Code', self.mCommander ).SetProp( self.mTempTunerPin[0] )
			ElisPropertyInt( 'Tuner1 SCR', self.mCommander ).SetProp( self.GetSelectedIndex( E_SpinEx02 ) ) 
			ElisPropertyInt( 'Tuner1 SCR Frequency', self.mCommander ).SetProp( int( E_LIST_ONE_CABLE_TUNER_FREQUENCY[ self.GetSelectedIndex( E_SpinEx03 ) ] ) )

			ElisPropertyInt( 'Tuner2 Pin Code', self.mCommander ).SetProp( self.mTempTunerPin[1] )
			ElisPropertyInt( 'Tuner2 SCR', self.mCommander ).SetProp( self.GetSelectedIndex( E_SpinEx04 ) ) 
			ElisPropertyInt( 'Tuner2 SCR Frequency', self.mCommander ).SetProp( int( E_LIST_ONE_CABLE_TUNER_FREQUENCY[ self.GetSelectedIndex( E_SpinEx05 ) ] ) )

			self.mCurrentSatellite1 = self.mTunerMgr.GetConfiguredSatellitebyTunerIndex( E_TUNER_1 )
			for i in range( self.mOneCablesatelliteCount ) :
				self.mCurrentSatellite1[i].mOneCableMDU = self.GetSelectedIndex( E_SpinEx01 )
				self.mCurrentSatellite1[i].mOneCablePin = int( self.GetControlLabel2String( E_Input01 ) )
				self.mCurrentSatellite1[i].mOneCableUBSlot = self.GetSelectedIndex( E_SpinEx02 )
				self.mCurrentSatellite1[i].mOneCableUBFreq = int( E_LIST_ONE_CABLE_TUNER_FREQUENCY[ self.GetSelectedIndex( E_SpinEx03 ) ] )

			self.mCurrentSatellite2 = self.mTunerMgr.GetConfiguredSatellitebyTunerIndex( E_TUNER_2 )
			for i in range( self.mOneCablesatelliteCount ) :
				self.mCurrentSatellite2[i].mOneCableMDU = self.GetSelectedIndex( E_SpinEx03 )
				self.mCurrentSatellite2[i].mOneCablePin = int( self.GetControlLabel2String( E_Input02 ) )
				self.mCurrentSatellite2[i].mOneCableUBSlot = self.GetSelectedIndex( E_SpinEx04 )
				self.mCurrentSatellite2[i].mOneCableUBFreq = int( E_LIST_ONE_CABLE_TUNER_FREQUENCY[ self.GetSelectedIndex( E_SpinEx05 ) ] )
