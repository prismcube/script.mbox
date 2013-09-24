from pvr.gui.WindowImport import *

E_FAST_SCAN_BASE_ID = WinMgr.WIN_ID_FAST_SCAN * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 


class FastScan( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		#self.mSatelliteIndex = 0
		#self.mFormattedList = None
		#self.mConfiguredSatelliteList = None


	def onInit( self ) :
		self.SetActivate( True )
		self.SetSingleWindowPosition( E_FAST_SCAN_BASE_ID )
		self.SetFrontdisplayMessage( MR_LANG('Fast Scan') )		
		#self.mWinId = xbmcgui.getCurrentWindowId( )

		self.SetSettingWindowLabel( MR_LANG( 'Fast Scan' ) )
		self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'Installation' ), MR_LANG( 'Channel Search' ) ) )

		self.InitConfig( )
		self.SetDefaultControl( )
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
		if self.IsActivate( ) == False  :
			return
	
		#groupId = self.GetGroupId( aControlId )
		
		# Satellite
		#if groupId == E_Input01 :
			
		
		#elif groupId == E_SpinEx01 or groupId == E_SpinEx02 or groupId == E_SpinEx03 :
		#	self.ControlSelect( )


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
		if self.mInitialized :
			self.ShowDescription( aControlId )


	def InitConfig( self ) :
		#self.ResetAllControl( )
		self.AddInputControl( E_Input01, MR_LANG( 'Tuner' ), 'Tuner 1', MR_LANG( 'Select Tuner' ) )
		self.AddInputControl( E_Input02, MR_LANG( 'Provider' ), 'marusys', MR_LANG( 'Select Provider' ) )
		self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'HD List' ), USER_ENUM_LIST_YES_NO, 0, MR_LANG( 'HD LIST' ) )
		self.AddUserEnumControl( E_SpinEx02, MR_LANG( 'Use fastscan channel numbering' ), USER_ENUM_LIST_YES_NO, 0, MR_LANG( 'Use fastscan channel numbering?' ) )
		self.AddUserEnumControl( E_SpinEx03, MR_LANG( 'Use fastscan channel names' ), USER_ENUM_LIST_YES_NO, 0, MR_LANG( 'Use fastscan channel names?' ) )
		self.AddInputControl( E_Input03, MR_LANG( 'Start Search' ), '', MR_LANG( 'Press OK button to start a channel search' ) )
		self.InitControl( )

