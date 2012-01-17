import xbmc
import xbmcgui
import sys

import pvr.gui.DialogMgr as DiaMgr
import pvr.TunerConfigMgr as ConfigMgr
from pvr.gui.GuiConfig import *
from pvr.gui.BaseWindow import SettingWindow, Action
import pvr.ElisMgr
from ElisProperty import ElisPropertyInt


class SatelliteConfigOnecable2( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mCommander = pvr.ElisMgr.GetInstance().GetCommander()
		self.mTunerIndex				= 0
		self.mCurrentSatellite			= []
		self.mCurrentSatellite2			= []
		self.mOneCablesatelliteCount	= 0

		self.mLoadConfig				= True
		
		self.mSavedTunerPin				= [ 0, 0 ]
		self.mSavedTunerScr				= [ 0, 0 ]
		self.mSavedTunerFreq			= [ 0, 0 ]

	def onInit( self ) :
		self.SetSettingWindowLabel( 'OneCable Configuration' )
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'OneCable configuration' )
		self.mOneCablesatelliteCount = ConfigMgr.GetInstance( ).GetOneCableSatelliteCount( )
		self.mCurrentSatellite = []
		self.mCurrentSatellite2 = []

		if self.mLoadConfig == True :
			self.LoadConfig( )
			self.mLoadConfig = False

		else :
			return

		if ConfigMgr.GetInstance( ).GetCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
			self.AddEnumControl( E_SpinEx01, 'MDU' )

			pinCode = ElisPropertyInt( 'Tuner%d Pin Code' % ( self.mTunerIndex + 1 ), self.mCommander ).GetProp( )
			self.AddInputControl( E_Input01, 'Tuner %d PIN-Code' % ( self.mTunerIndex + 1 ), '%d' % pinCode )

			tunerScr = ElisPropertyInt( 'Tuner%d SCR' % ( self.mTunerIndex + 1 ), self.mCommander ).GetProp( )
			self.AddUserEnumControl( E_SpinEx02, 'Tuner %d' % ( self.mTunerIndex + 1 ), E_LIST_ONE_CABLE_SCR, tunerScr )

			tunerFrequency = ElisPropertyInt( 'Tuner%d SCR Frequency' % ( self.mTunerIndex + 1 ), self.mCommander ).GetProp( )
			self.AddUserEnumControl( E_SpinEx03, 'Tuner %d Frequency' % ( self.mTunerIndex + 1 ), E_LIST_ONE_CABLE_TUNER_FREQUENCY, getOneCableTunerFrequencyIndex( '%d' % tunerFrequency ) )

			disableControls = [ E_Input02, E_SpinEx04, E_SpinEx05 ]
			self.SetVisibleControls( disableControls, False )
			self.SetEnableControls( disableControls, False )

		elif ConfigMgr.GetInstance( ).GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
			self.AddEnumControl( E_SpinEx01, 'MDU' )

			pinCode = ElisPropertyInt( 'Tuner1 Pin Code', self.mCommander ).GetProp( )
			self.AddInputControl( E_Input01, 'Tuner1 PIN-Code', '%d' % pinCode )

			tunerScr = ElisPropertyInt( 'Tuner1 SCR', self.mCommander ).GetProp( )
			self.AddUserEnumControl( E_SpinEx02, 'Tuner 1', E_LIST_ONE_CABLE_SCR, tunerScr )

			tunerFrequency = ElisPropertyInt( 'Tuner1 SCR Frequency', self.mCommander ).GetProp( )
			self.AddUserEnumControl( E_SpinEx03, 'Tuner 1 Frequency', E_LIST_ONE_CABLE_TUNER_FREQUENCY, getOneCableTunerFrequencyIndex( '%d' % tunerFrequency ) )

			pinCode = ElisPropertyInt( 'Tuner2 Pin Code', self.mCommander ).GetProp( )
			self.AddInputControl( E_Input02, 'Tuner2 PIN-Code', '%d' % pinCode )

			tunerScr = ElisPropertyInt( 'Tuner2 SCR', self.mCommander ).GetProp( )
			self.AddUserEnumControl( E_SpinEx04, 'Tuner 2', E_LIST_ONE_CABLE_SCR, tunerScr )

			tunerFrequency = ElisPropertyInt( 'Tuner2 SCR Frequency', self.mCommander ).GetProp( )
			self.AddUserEnumControl( E_SpinEx05, 'Tuner 2 Frequency', E_LIST_ONE_CABLE_TUNER_FREQUENCY, getOneCableTunerFrequencyIndex( '%d' % tunerFrequency ) )

		self.InitControl( )
		self.DisableControl( )
				
	def onAction( self, aAction ) :
		actionId = aAction.getId( )

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
			if ConfigMgr.GetInstance( ).GetCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
				pinCode = ElisPropertyInt( 'Tuner%d Pin Code' % ( self.mTunerIndex + 1 ), self.mCommander ).GetProp( )
				self.SetControlLabel2String( E_Input01, NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_NUMBER, 'Tuner%d Pin Code' % ( self.mTunerIndex + 1 ), '%d' % pinCode, 3 ) )

			elif ConfigMgr.GetInstance( ).GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
				if groupId == E_Input01 :
					pinCode = ElisPropertyInt( 'Tuner1 Pin Code', self.mCommander ).GetProp( )
					self.SetControlLabel2String( E_Input01, NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_NUMBER, 'Tuner1 Pin Code', '%d' % pinCode, 3 ) )

				elif groupId == E_Input02 :					
					pinCode = ElisPropertyInt( 'Tuner2 Pin Code', self.mCommander ).GetProp( )
					self.SetControlLabel2String( E_Input02, NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_NUMBER, 'Tuner2 Pin Code', '%d' % pinCode, 3 ) )

		if ConfigMgr.GetInstance( ).GetCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
			for i in range( self.mOneCablesatelliteCount ) :
				self.mCurrentSatellite.append( ConfigMgr.GetInstance( ).GetConfiguredSatellitebyIndex( i ) )
				
				self.mCurrentSatellite[i].mOneCableMDU = self.GetSelectedIndex( E_SpinEx01 )
					
				self.mCurrentSatellite[i].mOneCablePin = self.GetControlLabel2String( E_Input01 )
					
				self.mCurrentSatellite[i].mOneCableUBSlot = self.GetSelectedIndex( E_SpinEx02 )

				self.mCurrentSatellite[i].mOneCableUBFreq = int( E_LIST_ONE_CABLE_TUNER_FREQUENCY[ self.GetSelectedIndex( E_SpinEx03 ) ] )

		elif ConfigMgr.GetInstance( ).GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
			for i in range( self.mOneCablesatelliteCount ) :
				self.mCurrentSatellite.append( ConfigMgr.GetInstance( ).GetConfiguredSatellitebyIndex( i ) )
				
				self.mCurrentSatellite[i].mOneCableMDU = self.GetSelectedIndex( E_SpinEx01 )
					
				self.mCurrentSatellite[i].mOneCablePin = self.GetControlLabel2String( E_Input01 )
					
				self.mCurrentSatellite[i].mOneCableUBSlot = self.GetSelectedIndex( E_SpinEx02 )

				self.mCurrentSatellite[i].mOneCableUBFreq = int( E_LIST_ONE_CABLE_TUNER_FREQUENCY[ self.GetSelectedIndex( E_SpinEx03 ) ] )

			self.mCurrentSatellite2 = ConfigMgr.GetInstance( ).GetConfiguredSatellitebyTunerIndex( 1 )
			for i in range( self.mOneCablesatelliteCount ) :
				self.mCurrentSatellite2[i].mOneCableMDU = self.GetSelectedIndex( E_SpinEx01 )
					
				self.mCurrentSatellite2[i].mOneCablePin = self.GetControlLabel2String( E_Input02 )
					
				self.mCurrentSatellite2[i].mOneCableUBSlot = self.GetSelectedIndex( E_SpinEx04 )

				self.mCurrentSatellite2[i].mOneCableUBFreq = int( E_LIST_ONE_CABLE_TUNER_FREQUENCY[ self.GetSelectedIndex( E_SpinEx05 ) ] )

			
	def onFocus( self, aControlId ) :
		pass

	def onClose( self ) :
		if ConfigMgr.GetInstance( ).GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
			if self.GetSelectedIndex( E_SpinEx02 ) == self.GetSelectedIndex( E_SpinEx04 ) :
				dialog = xbmcgui.Dialog()
				dialog.ok( 'ERROR', 'Please set a different value for each tuner.' )
				return
			if self.GetSelectedIndex( E_SpinEx03 ) == self.GetSelectedIndex( E_SpinEx05 ) :
				dialog = xbmcgui.Dialog()
				dialog.ok( 'ERROR', 'Please set a different value for each tuner.' )
				return

		dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( 'Configure', 'Save Configuration?' )
		dialog.doModal( )
	
		if dialog.IsOK() == E_DIALOG_STATE_YES :
			if ConfigMgr.GetInstance( ).GetCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
				ElisPropertyInt( 'Tuner%d Pin Code' % ( self.mTunerIndex + 1 ), self.mCommander ).SetProp( int( self.GetControlLabel2String( E_Input01 ) ) )
				ElisPropertyInt( 'Tuner%d SCR' % ( self.mTunerIndex + 1 ), self.mCommander ).SetProp( self.GetSelectedIndex( E_SpinEx02 ) ) 
				ElisPropertyInt( 'Tuner%d SCR Frequency' % ( self.mTunerIndex + 1 ), self.mCommander ).SetProp( int( E_LIST_ONE_CABLE_TUNER_FREQUENCY[ self.GetSelectedIndex( E_SpinEx03 ) ] ) )
				
			elif ConfigMgr.GetInstance( ).GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
				ElisPropertyInt( 'Tuner1 Pin Code', self.mCommander ).SetProp( int( self.GetControlLabel2String( E_Input01 ) ) )
				ElisPropertyInt( 'Tuner1 SCR', self.mCommander ).SetProp( self.GetSelectedIndex( E_SpinEx02 ) ) 
				ElisPropertyInt( 'Tuner1 SCR Frequency', self.mCommander ).SetProp( int( E_LIST_ONE_CABLE_TUNER_FREQUENCY[ self.GetSelectedIndex( E_SpinEx03 ) ] ) )
				ElisPropertyInt( 'Tuner2 Pin Code', self.mCommander ).SetProp( int( self.GetControlLabel2String( E_Input02 ) ) )
				ElisPropertyInt( 'Tuner2 SCR', self.mCommander ).SetProp( self.GetSelectedIndex( E_SpinEx04 ) ) 
				ElisPropertyInt( 'Tuner2 SCR Frequency', self.mCommander ).SetProp( int( E_LIST_ONE_CABLE_TUNER_FREQUENCY[ self.GetSelectedIndex( E_SpinEx05 ) ] ) )	

		elif dialog.IsOK() == E_DIALOG_STATE_NO :
			self.ReLoadConfig( )

		elif dialog.IsOK() == E_DIALOG_STATE_CANCEL :
			return
			
		self.ResetAllControl( )
		self.mLoadConfig = True
		self.close( )

		
	def DisableControl( self ) :
		selectedIndex = self.GetSelectedIndex( E_SpinEx01 )
		enableControls = [ E_Input01, E_Input02 ]
		if ( selectedIndex == 0 ) :
			if ConfigMgr.GetInstance( ).GetCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
				self.SetEnableControl( E_Input01, False )
			elif ConfigMgr.GetInstance( ).GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
				self.SetEnableControls( enableControls, False )
		else :
			if ConfigMgr.GetInstance( ).GetCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
				self.SetEnableControl( E_Input01, True )
			elif ConfigMgr.GetInstance( ).GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
				self.SetEnableControls( enableControls, True )

	def LoadConfig( self ) :
		if ConfigMgr.GetInstance( ).GetCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
			self.mTunerIndex = ConfigMgr.GetInstance( ).GetCurrentTunerIndex( )
			
			self.mSavedTunerPin[self.mTunerIndex] = ElisPropertyInt( 'Tuner%d Pin Code' % ( self.mTunerIndex + 1 ), self.mCommander ).GetProp( )

			self.mSavedTunerScr[self.mTunerIndex] =  ElisPropertyInt( 'Tuner%d SCR' % ( self.mTunerIndex + 1 ), self.mCommander ).GetProp( )

			self.mSavedTunerFreq[self.mTunerIndex] = ElisPropertyInt( 'Tuner%d SCR Frequency' % ( self.mTunerIndex + 1 ), self.mCommander ).GetProp( )

		elif ConfigMgr.GetInstance( ).GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
			self.mSavedTunerPin[0] = ElisPropertyInt( 'Tuner1 Pin Code', self.mCommander ).GetProp( )

			self.mSavedTunerScr[0] =  ElisPropertyInt( 'Tuner1 SCR' , self.mCommander ).GetProp( )

			self.mSavedTunerFreq[0] = ElisPropertyInt( 'Tuner1 SCR Frequency', self.mCommander ).GetProp( )

			self.mSavedTunerPin[1] = ElisPropertyInt( 'Tuner2 Pin Code', self.mCommander ).GetProp( )

			self.mSavedTunerScr[1] =  ElisPropertyInt( 'Tuner2 SCR' , self.mCommander ).GetProp( )

			self.mSavedTunerFreq[1] = ElisPropertyInt( 'Tuner2 SCR Frequency', self.mCommander ).GetProp( )

	def ReLoadConfig( self ) :
		if ConfigMgr.GetInstance( ).GetCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
			ElisPropertyInt( 'Tuner%d Pin Code' % ( self.mTunerIndex + 1 ), self.mCommander ).SetProp( self.mSavedTunerPin[self.mTunerIndex] )
			ElisPropertyInt( 'Tuner%d SCR' % ( self.mTunerIndex + 1 ), self.mCommander ).SetProp( self.mSavedTunerScr[self.mTunerIndex] )
			ElisPropertyInt( 'Tuner%d SCR Frequency' % ( self.mTunerIndex + 1 ), self.mCommander ).SetProp( self.mSavedTunerFreq[self.mTunerIndex]  )

		elif ConfigMgr.GetInstance( ).GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
			ElisPropertyInt( 'Tuner1 Pin Code', self.mCommander ).SetProp( self.mSavedTunerPin[0] )
			ElisPropertyInt( 'Tuner1 SCR' , self.mCommander ).SetProp( self.mSavedTunerScr[0] )
			ElisPropertyInt( 'Tuner1 SCR Frequency', self.mCommander ).SetProp( self.mSavedTunerFreq[0] )
			ElisPropertyInt( 'Tuner2 Pin Code', self.mCommander ).SetProp( self.mSavedTunerPin[1] )
			ElisPropertyInt( 'Tuner2 SCR' , self.mCommander ).SetProp( self.mSavedTunerScr[1] )
			ElisPropertyInt( 'Tuner2 SCR Frequency', self.mCommander ).SetProp( self.mSavedTunerFreq[1] )