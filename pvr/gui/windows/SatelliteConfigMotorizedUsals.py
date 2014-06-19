from pvr.gui.WindowImport import *
from pvr.gui.FTIWindow import FTIWindow

E_CONFIG_MOTORIZED_USALS_BASE_ID = WinMgr.WIN_ID_CONFIG_MOTORIZED_USALS * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 


class SatelliteConfigMotorizedUsals( FTIWindow ) :
	def __init__( self, *args, **kwargs ) :
		FTIWindow.__init__( self, *args, **kwargs )
		self.mIsWest = 0
		self.mIsSouth = 0
		self.mLongitude	= 0
		self.mLatitude	= 0
		self.tunerIndex = E_TUNER_1


	def onInit( self ) :
		self.tunerIndex = self.mTunerMgr.GetCurrentTunerNumber( )
		self.SetSettingWindowLabel( MR_LANG( 'Tuner %s Config : Motorized, Usals' ) % ( self.tunerIndex + 1 ) )
		if self.getProperty( 'IsFTI' ) == 'True' :
			self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'Installation' ), MR_LANG( 'First Installation' ) ) )
		else :
			self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'Installation' ), MR_LANG( 'Antenna Setup' ) ) )
		   
		self.GetLongitude( )
		self.GetLatitude( )
		self.SetSingleWindowPosition( E_CONFIG_MOTORIZED_USALS_BASE_ID )
		self.InitConfig( )
		self.SetFTIGuiType( )
		self.mInitialized = True
		self.SetDefaultControl( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			if self.GetFirstInstallation( ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( MR_LANG( 'Exit Installation' ), MR_LANG( 'Are you sure you want to quit the first installation?' ), True )
				dialog.doModal( )

				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					self.OpenBusyDialog( )
					self.SetLongitude( )
					self.SetLatitude( )
					self.CloseFTI( )
					time.sleep( 3 )
					self.CloseBusyDialog( )
					WinMgr.GetInstance( ).CloseWindow( )
			else :
				self.SetLongitude( )
				self.SetLatitude( )
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

		if aControlId == E_FIRST_TIME_INSTALLATION_PREV :
			self.OpenBusyDialog( )
			self.SetLongitude( )
			self.SetLatitude( )
			WinMgr.GetInstance( ).ShowWindow( self.GetAntennaPrevStepWindowId( ), WinMgr.WIN_ID_MAINMENU )

		elif aControlId == E_FIRST_TIME_INSTALLATION_NEXT :
			self.OpenBusyDialog( )
			self.SetLongitude( )
			self.SetLatitude( )
			WinMgr.GetInstance( ).ShowWindow( self.GetAntennaNextStepWindowId( ), WinMgr.WIN_ID_MAINMENU )


	def onFocus( self, aControlId ) :
		if self.mInitialized :
			self.ShowDescription( aControlId )
			

	def InitConfig( self ) :
		self.ResetAllControl( )
		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( False )

		self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'My Longitude Direction' ), E_LIST_MY_LONGITUDE, self.mIsWest, MR_LANG( 'Set the longitude direction for your area' ) )
		tmplongitude = '%03d.%d' % ( ( self.mLongitude / 10 ), self.mLongitude % 10 )
		self.AddInputControl( E_Input01, MR_LANG( 'My Longitude Angle' ), tmplongitude, MR_LANG( 'Enter the longitude angle for your location' ) )
		
		self.AddUserEnumControl( E_SpinEx02, MR_LANG( 'My Latitude Direction' ), E_LIST_MY_LATITUDE, self.mIsSouth, MR_LANG( 'Set the latitude direction for your area' ) )
		tmplatitude = '%03d.%d' % ( ( self.mLatitude / 10 ), self.mLatitude % 10 )
		self.AddInputControl( E_Input02, MR_LANG( 'My Latitude Angle' ), tmplatitude, MR_LANG( 'Enter the latitude angle for your location' ) )
		
		self.AddInputControl( E_Input03, MR_LANG( 'Reference Position to Null' ), '', MR_LANG( 'Rotates the motor to 0 as a reference point' ) )
		self.AddInputControl( E_Input04, MR_LANG( 'Edit Satellite' ), '', MR_LANG( 'Here you can setup satellites for Motorized USALS' ) )

		if self.GetFirstInstallation( ) :
			self.SetFTIPrevNextButton( )
			self.SetEnableControl( E_Input04, False )
		else :
			self.SetEnableControl( E_Input04, True )

		self.InitControl( )
		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( True )


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
			
