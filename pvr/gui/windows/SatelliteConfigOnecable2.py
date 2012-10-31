from pvr.gui.WindowImport import *


class SatelliteConfigOnecable2( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mTunerIndex				= 0
		self.mOneCablesatelliteCount	= 0

		self.mLoadConfig				= True
		
		self.mSavedTunerPin				= [ 0, 0 ]
		self.mSavedTunerScr				= [ 0, 0 ]
		self.mSavedTunerFreq			= [ 0, 0 ]

		self.mTempTunerPin				= [ 0, 0 ]
		self.mTempTunerScr				= [ 0, 0 ]
		self.mTempTunerFreq				= [ 0, 0 ]


	def onInit( self ) :
		tunerIndex = self.mTunerMgr.GetCurrentTunerNumber( )
		self.SetSettingWindowLabel( MR_LANG( 'Tuner %d Config : OneCable' ) % ( tunerIndex + 1 ) )
		self.LoadNoSignalState( )
		self.mOneCablesatelliteCount = self.mTunerMgr.GetOneCableSatelliteCount( )

		if self.mLoadConfig == True :
			self.LoadConfig( )
			self.mLoadConfig = False

		self.InitConfig( )
		self.mInitialized = True
		self.setDefaultControl( )
		self.SetPipLabel( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )				

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.Close( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

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
				dialog.SetDialogProperty( MR_LANG( 'Tuner %d PIN code' ) % ( self.mTunerIndex + 1 ), '%03d' % self.mTempTunerPin[self.mTunerIndex], 3 )
				dialog.doModal( )
				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					self.mTempTunerPin[self.mTunerIndex] = int( dialog.GetString( ) )

			elif self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
				if groupId == E_Input01 :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
					dialog.SetDialogProperty( MR_LANG( 'Tuner 1 PIN code' ), '%03d' % self.mTempTunerPin[0], 3 )
					dialog.doModal( )
					if dialog.IsOK( ) == E_DIALOG_STATE_YES :
						self.mTempTunerPin[0] = int( dialog.GetString( ) )

				elif groupId == E_Input02 :					
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
					dialog.SetDialogProperty( MR_LANG( 'Tuner 2 PIN code' ), '%03d' % self.mTempTunerPin[1], 3 )
					dialog.doModal( )
					if dialog.IsOK( ) == E_DIALOG_STATE_YES :
						self.mTempTunerPin[1] = int( dialog.GetString( ) )

			self.InitConfig( )


	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return
		if self.mLastFocused != aControlId :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId


	def Close( self ) :
		if self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
			if self.GetSelectedIndex( E_SpinEx02 ) == self.GetSelectedIndex( E_SpinEx04 ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Please set a different value for each tuner' ) )
				dialog.doModal( )
				return
			if self.GetSelectedIndex( E_SpinEx03 ) == self.GetSelectedIndex( E_SpinEx05 ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Please set a different value for each tuner' ) )
				dialog.doModal( )
				return

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( MR_LANG( 'Save configuration' ), MR_LANG( 'Do you want to save changes before exit?' ) )
		dialog.doModal( )

		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			self.SaveConfig( )

		elif dialog.IsOK( ) == E_DIALOG_STATE_NO :
			self.ReLoadConfig( )

		elif dialog.IsOK( ) == E_DIALOG_STATE_CANCEL :
			return

		self.mLoadConfig = True
		WinMgr.GetInstance( ).CloseWindow( )


	def InitConfig( self ) :
		self.ResetAllControl( )
		tunertype = self.mTunerMgr.GetCurrentTunerConnectionType( )
		if tunertype == E_TUNER_SEPARATED :
			self.AddEnumControl( E_SpinEx01, 'MDU', None, MR_LANG( 'When set to \'On\', multiple TVs within the same storied building with a single or two dish antennas will receive Direct-to-Home service' ) )
			self.AddInputControl( E_Input01, MR_LANG( 'Tuner %d PIN Code' ) % ( self.mTunerIndex + 1 ), '%03d' % self.mTempTunerPin[self.mTunerIndex], MR_LANG( 'Enter your PIN code for Tuner %d' ) % ( self.mTunerIndex + 1 ) )
			self.AddUserEnumControl( E_SpinEx02, MR_LANG( 'Tuner %d SCR' ) % ( self.mTunerIndex + 1 ), E_LIST_ONE_CABLE_SCR, self.mTempTunerScr[self.mTunerIndex], MR_LANG( 'Select number of Single Cable Routers for Tuner %d' ) % ( self.mTunerIndex + 1 ) )
			self.AddUserEnumControl( E_SpinEx03, MR_LANG( 'Tuner %d Frequency' ) % ( self.mTunerIndex + 1 ), E_LIST_ONE_CABLE_TUNER_FREQUENCY, getOneCableTunerFrequencyIndex( '%d' % self.mTempTunerFreq[self.mTunerIndex] ), MR_LANG( 'Select the frequency for Tuner %d' ) % ( self.mTunerIndex + 1 ) )

			disableControls = [ E_Input02, E_SpinEx04, E_SpinEx05 ]
			self.SetVisibleControls( disableControls, False )
			self.SetEnableControls( disableControls, False )

		elif tunertype == E_TUNER_LOOPTHROUGH :
			self.AddEnumControl( E_SpinEx01, 'MDU', None, MR_LANG( 'When set to \'On\', multiple TVs within the same storied building with a single or two dish antennas will receive Direct-to-Home service' ) )
			self.AddInputControl( E_Input01, MR_LANG( 'Tuner 1 PIN Code' ), '%03d' % self.mTempTunerPin[0], MR_LANG( 'Enter your PIN code for Tuner 1' ) )
			self.AddUserEnumControl( E_SpinEx02, MR_LANG( 'Tuner 1 SCR' ), E_LIST_ONE_CABLE_SCR, self.mTempTunerScr[0], MR_LANG( 'Select number of Single Cable Routers for Tuner 1' ) )
			self.AddUserEnumControl( E_SpinEx03, MR_LANG( 'Tuner 1 Frequency' ), E_LIST_ONE_CABLE_TUNER_FREQUENCY, getOneCableTunerFrequencyIndex( '%d' % self.mTempTunerFreq[0] ), MR_LANG( 'Select the frequency for Tuner 1' ) )

			self.AddInputControl( E_Input02, MR_LANG( 'Tuner 2 PIN Code' ), '%03d' % self.mTempTunerPin[1], MR_LANG( 'Enter your PIN code for Tuner 2' ) )			
			self.AddUserEnumControl( E_SpinEx04, MR_LANG( 'Tuner 2 SCR' ), E_LIST_ONE_CABLE_SCR, self.mTempTunerScr[1], MR_LANG( 'Select number of Single Cable Routers for Tuner 2' ) )			
			self.AddUserEnumControl( E_SpinEx05, MR_LANG( 'Tuner 2 Frequency' ), E_LIST_ONE_CABLE_TUNER_FREQUENCY, getOneCableTunerFrequencyIndex( '%d' % self.mTempTunerFreq[1] ), MR_LANG( 'Select the frequency for Tuner 2' ) )

			disableControls = [ E_Input02, E_SpinEx04, E_SpinEx05 ]
			self.SetVisibleControls( disableControls, True )
			self.SetEnableControls( disableControls, True )

		self.InitControl( )
		self.DisableControl( )


	def DisableControl( self ) :
		tunertype = self.mTunerMgr.GetCurrentTunerConnectionType( )
		selectedIndex = self.GetSelectedIndex( E_SpinEx01 )
		enableControls = [ E_Input01, E_Input02 ]
		if selectedIndex == 0 :
			if tunertype == E_TUNER_SEPARATED :
				self.SetEnableControl( E_Input01, False )
			else :
				self.SetEnableControls( enableControls, False )
		else :
			if tunertype == E_TUNER_SEPARATED :
				self.SetEnableControl( E_Input01, True )
			else :
				self.SetEnableControls( enableControls, True )


	def LoadConfig( self ) :
		if self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_SEPARATED :
			self.mTunerIndex = self.mTunerMgr.GetCurrentTunerNumber( )

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

		elif self.mTunerMgr.GetCurrentTunerConnectionType( ) == E_TUNER_LOOPTHROUGH :
			ElisPropertyInt( 'Tuner1 Pin Code', self.mCommander ).SetProp( self.mTempTunerPin[0] )
			ElisPropertyInt( 'Tuner1 SCR', self.mCommander ).SetProp( self.GetSelectedIndex( E_SpinEx02 ) ) 
			ElisPropertyInt( 'Tuner1 SCR Frequency', self.mCommander ).SetProp( int( E_LIST_ONE_CABLE_TUNER_FREQUENCY[ self.GetSelectedIndex( E_SpinEx03 ) ] ) )

			ElisPropertyInt( 'Tuner2 Pin Code', self.mCommander ).SetProp( self.mTempTunerPin[1] )
			ElisPropertyInt( 'Tuner2 SCR', self.mCommander ).SetProp( self.GetSelectedIndex( E_SpinEx04 ) ) 
			ElisPropertyInt( 'Tuner2 SCR Frequency', self.mCommander ).SetProp( int( E_LIST_ONE_CABLE_TUNER_FREQUENCY[ self.GetSelectedIndex( E_SpinEx05 ) ] ) )

			tuner1ConfigList = self.mTunerMgr.GetConfiguredSatelliteListbyTunerIndex( E_TUNER_1 )
			for i in range( self.mOneCablesatelliteCount ) :
				tuner1ConfigList[i].mOneCableMDU = self.GetSelectedIndex( E_SpinEx01 )
				tuner1ConfigList[i].mOneCablePin = int( self.GetControlLabel2String( E_Input01 ) )
				tuner1ConfigList[i].mOneCableUBSlot = self.GetSelectedIndex( E_SpinEx02 )
				tuner1ConfigList[i].mOneCableUBFreq = int( E_LIST_ONE_CABLE_TUNER_FREQUENCY[ self.GetSelectedIndex( E_SpinEx03 ) ] )

			tuner2ConfigList = self.mTunerMgr.GetConfiguredSatelliteListbyTunerIndex( E_TUNER_2 )
			for i in range( self.mOneCablesatelliteCount ) :
				tuner2ConfigList[i].mOneCableMDU = self.GetSelectedIndex( E_SpinEx03 )
				tuner2ConfigList[i].mOneCablePin = int( self.GetControlLabel2String( E_Input02 ) )
				tuner2ConfigList[i].mOneCableUBSlot = self.GetSelectedIndex( E_SpinEx04 )
				tuner2ConfigList[i].mOneCableUBFreq = int( E_LIST_ONE_CABLE_TUNER_FREQUENCY[ self.GetSelectedIndex( E_SpinEx05 ) ] )
