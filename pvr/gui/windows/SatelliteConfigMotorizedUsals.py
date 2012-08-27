from pvr.gui.WindowImport import *


class SatelliteConfigMotorizedUsals( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mIsWest = 0
		self.mIsSouth = 0
		self.mLongitude	= 0
		self.mLatitude	= 0
		self.tunerIndex = E_TUNER_1


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.tunerIndex = self.mTunerMgr.GetCurrentTunerNumber( )
		self.SetSettingWindowLabel( MR_LANG( 'Tuner %s Config : Motorized, Usals' ) % ( self.tunerIndex + 1 ) )
		self.LoadNoSignalState( )
		   
		self.GetLongitude( )
		self.GetLatitude( )
		self.InitConfig( )
		self.mInitialized = True
		self.setDefaultControl( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.SetLongitude( )
			self.SetLatitude( )
			self.ResetAllControl( )
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_PARENT_DIR :
			self.SetLongitude( )
			self.SetLatitude( )
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
		groupId = self.GetGroupId( aControlId )

		# My Longitude
		if groupId == E_SpinEx01 :
			self.mIsWest = self.GetSelectedIndex( E_SpinEx01 )

		# My Latitude
		elif groupId == E_SpinEx02 :
			self.mIsSouth = self.GetSelectedIndex( E_SpinEx02 ) 

		# Set Longitude
		if groupId == E_Input01 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SATELLITE_NUMERIC )
			dialog.SetDialogProperty( MR_LANG( 'Longitude Degree' ), self.mLongitude )
			dialog.doModal( )

			if dialog.IsOK() == E_DIALOG_STATE_YES :
				self.mLongitude = dialog.GetNumber( )
				self.InitConfig( )

		# Set Latitude
		elif groupId == E_Input02 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SATELLITE_NUMERIC )
			dialog.SetDialogProperty( MR_LANG( 'Latitude Degree' ), self.mLatitude )
			dialog.doModal( )

			if dialog.IsOK() == E_DIALOG_STATE_YES :
				self.mLatitude = dialog.GetNumber( )
				self.InitConfig( )

		# Reference Position to Null
		elif groupId == E_Input03 :
			self.mCommander.Motorized_GotoNull( self.tunerIndex )


		# Configure Satellites
		elif groupId == E_Input04 :
			self.SetLongitude( )
			self.SetLatitude( )
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TUNER_CONFIGURATION )


	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return
		if self.mLastFocused != aControlId :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId
			

	def InitConfig( self ) :
		self.ResetAllControl( )

		self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'My Longitude Direction' ), E_LIST_MY_LONGITUDE, self.mIsWest, MR_LANG( 'Set the correct longitude direction for your area' ) )
		tmplongitude = '%03d.%d' % ( ( self.mLongitude / 10 ), self.mLongitude % 10 )
		self.AddInputControl( E_Input01, MR_LANG( 'My Longitude Angle' ), tmplongitude, MR_LANG( 'Enter the longitude angle for your location' ) )
		
		self.AddUserEnumControl( E_SpinEx02, MR_LANG( 'My Latitude Direction' ), E_LIST_MY_LATITUDE, self.mIsSouth, MR_LANG( 'Set the correct latitude direction for your area' ) )
		tmplatitude = '%03d.%d' % ( ( self.mLatitude / 10 ), self.mLatitude % 10 )
		self.AddInputControl( E_Input02, MR_LANG( 'My Latitude Angle' ), tmplatitude, MR_LANG( 'Enter the latitude angle for your location' ) )
		
		self.AddInputControl( E_Input03, MR_LANG( 'Reference Position to Null' ), '', MR_LANG( 'Rotates the moter to 0 as a reference point' ) )
		self.AddInputControl( E_Input04, MR_LANG( 'Edit Satellite' ), '', MR_LANG( 'Here you can setup satellites for Motorized USALS' ) )

		self.InitControl( )

	def GetLongitude( self ) :
		self.mLongitude = ElisPropertyInt( 'MyLongitude', self.mCommander ).GetProp( )

		if self.mLongitude < 1800 :
			self.mIsWest = 0
		else :
			self.mIsWest = 1
		
		if self.mLongitude >= 1800 :
			self.mLongitude = self.mLongitude - 1800
		

	def GetLatitude( self ) :
		self.mLatitude = ElisPropertyInt( 'MyLatitude', self.mCommander ).GetProp( )

		if self.mLatitude < 1800 :
			self.mIsSouth = 0
		else : 
			self.mIsSouth = 1

		if self.mLatitude >= 1800 :
			self.mLatitude = self.mLatitude - 1800


	def SetLongitude( self ) :
		if self.mIsWest == 1 :
			self.mLongitude = self.mLongitude + 1800
		ElisPropertyInt( 'MyLongitude', self.mCommander ).SetProp( self.mLongitude )


	def SetLatitude( self ) :
		if self.mIsSouth == 1 :
			self.mLatitude = self.mLatitude + 1800
		ElisPropertyInt( 'MyLatitude', self.mCommander ).SetProp( self.mLatitude )
			