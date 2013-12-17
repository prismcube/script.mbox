from pvr.gui.WindowImport import *

E_SELECT_TUNER_BASE_ID = WinMgr.WIN_ID_SELECT_TUNER * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 


class SelectTuner( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )


	def onInit( self ) :
		self.SetActivate( True )
		self.SetSingleWindowPosition( E_SELECT_TUNER_BASE_ID )
		self.SetFrontdisplayMessage( MR_LANG( 'Select Tuner' ) )
		self.SetSettingWindowLabel( MR_LANG( 'Select Tuner' ) )
		self.SetHeaderTitle( "%s - %s" % ( MR_LANG( 'Installation' ), MR_LANG( 'Select Tuner' ) ) )

		self.SetPipScreen( )

		self.mTunerList = self.mDataCache.GetDVBTunerList( )
		hasDVBS = False
		count = 0
		for tuner in self.mTunerList :
			if tuner.mTunerType == ElisEnum.E_DVB_TUNER_DVBS :
				if hasDVBS == True :
					continue
				self.AddInputControl( E_Input01+count*100, MR_LANG( 'Tuner' ), MR_LANG( 'DVB-S2' ), MR_LANG( 'Search TV and radio channels without entering any satellite information' ) )
				hasDVBS = True
				
			elif tuner.mTunerType == ElisEnum.E_DVB_TUNER_DVBT :
				self.AddInputControl( E_Input01+count*100, MR_LANG( 'Tuner' ), MR_LANG( 'DVB-T' ) , MR_LANG( 'Search TV and radio channels without entering any satellite information' ) )
			elif tuner.mTunerType == ElisEnum.E_DVB_TUNER_DVBC :
				self.AddInputControl( E_Input01+count*100, MR_LANG( 'Tuner' ), MR_LANG( 'DVB-C' ) , MR_LANG( 'Search TV and radio channels without entering any satellite information' ) )
			elif tuner.mTunerType == ElisEnum.E_DVB_TUNER_DVBTC :				
				self.AddInputControl( E_Input01+count*100, MR_LANG( 'Tuner' ), MR_LANG( 'DVB-T(DVB-C)' ), MR_LANG( 'Search TV and radio channels without entering any satellite information' ) )

			count +=  1

		hideCount = 5-count
		hideControlIds = []
		for i in range( hideCount ) :
			hideControlIds.append( E_Input01+(count + i)*100 )
		self.SetVisibleControls( hideControlIds, False )

		self.InitControl( )
		self.mInitialized = True
		self.SetDefaultControl( )


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			self.SetVideoRestore( )
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )				

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )


	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False :
			return
		"""
		groupId = self.GetGroupId( aControlId )
		if groupId == E_Input01 :
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_AUTOMATIC_SCAN )
			
		elif groupId == E_Input02 :
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MANUAL_SCAN )

		elif groupId == E_Input03 :
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_FAST_SCAN )
		"""

	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False :
			return
	
		if self.mInitialized :
			self.ShowDescription( aControlId )

