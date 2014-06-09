from pvr.gui.GuiConfig import *
from pvr.gui.SettingWindow import SettingWindow
from elisinterface.ElisProperty import ElisPropertyEnum
import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DiaMgr
from types import * 


LIST_FTI_WINDOWSID		= [ WinMgr.WIN_ID_TUNER_CONFIGURATION, WinMgr.WIN_ID_CONFIG_SIMPLE, WinMgr.WIN_ID_CONFIG_MOTORIZED_12, WinMgr.WIN_ID_CONFIG_MOTORIZED_USALS, WinMgr.WIN_ID_CONFIG_ONECABLE, WinMgr.WIN_ID_CONFIG_ONECABLE_2, WinMgr.WIN_ID_CONFIG_DISEQC_10, WinMgr.WIN_ID_CONFIG_DISEQC_11 ]

gFTIStepNumber			= E_STEP_SELECT_LANGUAGE
gAntennaStepList		= []
gAntennaCurrentStep		= 0


class FTIWindow( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )


	def SetFirstInstallation( self, aFlag ) :
		if aFlag :
			ElisPropertyEnum( 'First Installation', self.mCommander ).SetProp( 0x2b )
			if E_SUPPORT_SINGLE_WINDOW_MODE :
				self.setProperty( 'IsFTI', 'True' )
			else :
				self.SetFTIWindowProperty( True )
		else :
			if not self.mDataCache.GetStanbyClosing( ) :
				ElisPropertyEnum( 'First Installation', self.mCommander ).SetProp( 0 )

			if E_SUPPORT_SINGLE_WINDOW_MODE :
				self.setProperty( 'IsFTI', 'False' )
			else :
				self.SetFTIWindowProperty( False )


	def GetFirstInstallation( self ) :
		if ElisPropertyEnum( 'First Installation', self.mCommander ).GetProp( ) == 0 :
			return False
		else :
			return True


	def SetFTIStep( self, aStep ) :
		global gFTIStepNumber
		gFTIStepNumber = aStep


	def GetFTIStep( self ) :
		global gFTIStepNumber
		return gFTIStepNumber


	def SetFTIWindowProperty( self, aFlag ) :
		if aFlag :
			for winId in LIST_FTI_WINDOWSID :
				WinMgr.GetInstance( ).GetWindow( winId ).setProperty( 'IsFTI', 'True' )
		else :
			for winId in LIST_FTI_WINDOWSID :
				WinMgr.GetInstance( ).GetWindow( winId ).setProperty( 'IsFTI', 'False' )


	def DrawFTIStep( self, aStep ) :
		if aStep == E_STEP_CHANNEL_SEARCH_CONFIG_FAST or aStep == E_STEP_CHANNEL_SEARCH_CONFIG_DVBT :
			aStep = E_STEP_CHANNEL_SEARCH_CONFIG

		elif aStep == E_STEP_DATE_TIME :
			aStep = 4

		elif aStep == E_STEP_RESULT :
			aStep = 5

		for i in range( E_FTI_MAX_STEP ) :
			if i == aStep :
				self.getControl( E_FIRST_TIME_INSTALLATION_STEP_IMAGE + i ).setVisible( True )
			else :
				self.getControl( E_FIRST_TIME_INSTALLATION_STEP_IMAGE + i ).setVisible( False )
				self.getControl( E_FIRST_TIME_INSTALLATION_STEP_IMAGE_BACK + i ).setVisible( True )


	def SetPrevNextButtonLabel( self, aStep ) :
		if aStep == E_STEP_SELECT_LANGUAGE :
			self.SetVisibleControl( E_FIRST_TIME_INSTALLATION_PREV, False )
			self.getControl( E_FIRST_TIME_INSTALLATION_NEXT_LABEL ).setLabel( MR_LANG( 'Next' ) )
		elif aStep == E_STEP_RESULT :
			self.getControl( E_FIRST_TIME_INSTALLATION_PREV_LABEL ).setLabel( MR_LANG( 'Previous' ) )
			self.getControl( E_FIRST_TIME_INSTALLATION_NEXT_LABEL ).setLabel( MR_LANG( 'Finish' ) )
		else :
			self.SetVisibleControl( E_FIRST_TIME_INSTALLATION_PREV, True )
			self.getControl( E_FIRST_TIME_INSTALLATION_PREV_LABEL ).setLabel( MR_LANG( 'Previous' ) )
			self.getControl( E_FIRST_TIME_INSTALLATION_NEXT_LABEL ).setLabel( MR_LANG( 'Next' ) )


	def SetFTIGuiType( self ) :
		if self.GetFirstInstallation( ) :
			self.DrawFTIStep( E_STEP_ANTENNA )
			self.SetPrevNextButtonLabel( E_STEP_ANTENNA )


	def GetIsLastStep( self ) :
		global gAntennaStepList
		global gAntennaCurrentStep
		if ( gAntennaCurrentStep + 1 ) == len( gAntennaStepList ) :
			return True
		else :
			return False


	def GetAntennaNextStepWindowId( self ) :
		global gAntennaStepList
		global gAntennaCurrentStep
		if ( gAntennaCurrentStep + 1 ) == len( gAntennaStepList ) :
			self.SetFTIStep( E_STEP_CHANNEL_SEARCH_CONFIG )
			self.mTunerMgr.SaveConfiguration( )
			self.mTunerMgr.SyncChannelBySatellite( )
			self.mDataCache.Channel_ReLoad( )
			self.mDataCache.Channel_ReTune( )
			self.mTunerMgr.SetNeedLoad( True )
			winId = WinMgr.WIN_ID_FIRST_INSTALLATION
		else :
			gAntennaCurrentStep = gAntennaCurrentStep + 1

			if type( gAntennaStepList[ gAntennaCurrentStep ] ) == ListType :
				self.mTunerMgr.SetCurrentTunerNumber( gAntennaStepList[ gAntennaCurrentStep ][0] )
				self.mTunerMgr.SetCurrentConfigIndex( gAntennaStepList[ gAntennaCurrentStep ][1] )
				winId = gAntennaStepList[ gAntennaCurrentStep ][2]
			else :
				winId = gAntennaStepList[ gAntennaCurrentStep ]

		self.CloseBusyDialog( )
		return winId


	def GetAntennaPrevStepWindowId( self ) :
		global gAntennaStepList
		global gAntennaCurrentStep
		gAntennaCurrentStep = gAntennaCurrentStep - 1
		if type( gAntennaStepList[ gAntennaCurrentStep ] ) == ListType :
			self.mTunerMgr.SetCurrentTunerNumber( gAntennaStepList[ gAntennaCurrentStep ][0] )
			self.mTunerMgr.SetCurrentConfigIndex( gAntennaStepList[ gAntennaCurrentStep ][1] )
			winId = gAntennaStepList[ gAntennaCurrentStep ][2]
		else :
			winId = gAntennaStepList[ gAntennaCurrentStep ]

		self.CloseBusyDialog( )
		return winId


	def MakeAntennaSetupStepList( self ) :
		global gAntennaStepList
		global gAntennaCurrentStep
		self.OpenBusyDialog( )
		self.mTunerMgr.SaveConfiguration( )
		self.mDataCache.Channel_ReTune( )

		gAntennaStepList = []
		gAntennaStepList.append( WinMgr.WIN_ID_FIRST_INSTALLATION )
		configuredsatellitecnt = []
		tuner1ConfiguredSatellites = self.mTunerMgr.GetConfiguredSatelliteListbyTunerIndex( E_TUNER_1 )
		tuner2ConfiguredSatellites = self.mTunerMgr.GetConfiguredSatelliteListbyTunerIndex( E_TUNER_2 )
		if self.mTunerMgr.GetCurrentTunerConfigType( ) == E_DIFFERENT_TUNER :
			if self.mPlatform.GetProduct( ) == PRODUCT_OSCAR :
				loopcount = 1
			else :
				loopcount = 2
			configuredsatellitecnt.append( len( tuner1ConfiguredSatellites ) )
			configuredsatellitecnt.append( len( tuner2ConfiguredSatellites ) )
		else :
			loopcount = 1
			configuredsatellitecnt.append( len( tuner1ConfiguredSatellites ) )

		for tunerindex in range( loopcount ) :
			prop = ElisPropertyEnum( 'Tuner%s Type' % ( tunerindex + 1 ), self.mCommander ).GetProp( )

			if prop == E_MOTORIZE_USALS :
				gAntennaStepList.append( [ tunerindex, 0 , WinMgr.WIN_ID_CONFIG_MOTORIZED_USALS ] )
				gAntennaStepList.append( [ tunerindex, 0, WinMgr.WIN_ID_TUNER_CONFIGURATION ] )
				configWindowId = WinMgr.WIN_ID_CONFIG_SIMPLE
	
				for satelliteindex in range( configuredsatellitecnt[ tunerindex ] ) :
					gAntennaStepList.append( [ tunerindex, satelliteindex, configWindowId ] )

			elif prop == E_ONE_CABLE :
				gAntennaStepList.append( [ tunerindex, 0 , WinMgr.WIN_ID_CONFIG_ONECABLE ] )
				if configuredsatellitecnt[ tunerindex ] != 0 :
					gAntennaStepList.append( [ tunerindex, 0 , WinMgr.WIN_ID_CONFIG_ONECABLE_2 ] )

					configWindowId = WinMgr.WIN_ID_CONFIG_SIMPLE
					for satelliteindex in range( configuredsatellitecnt[ tunerindex ] ) :
						gAntennaStepList.append( [ tunerindex, satelliteindex, configWindowId ] )

			else :
				if prop == E_DISEQC_1_0 :
					configWindowId = WinMgr.WIN_ID_CONFIG_DISEQC_10
					if tunerindex == E_TUNER_1 and configuredsatellitecnt[ E_TUNER_1 ] > 4 :
						configuredsatellitecnt[ E_TUNER_1 ] = 4
					elif tunerindex == E_TUNER_2 and configuredsatellitecnt[ E_TUNER_2 ] > 4 :
						configuredsatellitecnt[ E_TUNER_2 ] = 4
				elif prop == E_DISEQC_1_1 :
					configWindowId = WinMgr.WIN_ID_CONFIG_DISEQC_11
				elif prop == E_MOTORIZE_1_2 :
					configWindowId = WinMgr.WIN_ID_CONFIG_MOTORIZED_12
				elif prop == E_SIMPLE_LNB :
					configWindowId = WinMgr.WIN_ID_CONFIG_SIMPLE

				gAntennaStepList.append( [ tunerindex, 0, WinMgr.WIN_ID_TUNER_CONFIGURATION ] )
				for satelliteindex in range( configuredsatellitecnt[ tunerindex ] ) :
					gAntennaStepList.append( [ tunerindex, satelliteindex, configWindowId ] )

		self.SetAntennaCurrentCount( 0 )
		self.CloseBusyDialog( )


	def GetAntennaCurrentCount( self ) :
		return gAntennaCurrentStep


	def SetAntennaCurrentCount( self, aCount ) :
		global gAntennaCurrentStep
		gAntennaCurrentStep = aCount


	def SetFTIPrevNextButton( self ) :
		if self.GetIsLastStep( ) :
			self.AddPrevNextButton( MR_LANG( 'Go to the channel search setup page' ), MR_LANG( 'Go back to the previous satellite configuration page' ) )
		else :
			self.AddPrevNextButton( MR_LANG( 'Go to the next satellite configuration page' ), MR_LANG( 'Go back to the previous satellite configuration page' ) )


	def CloseFTI( self ) :
		self.SetFTIStep( E_STEP_SELECT_LANGUAGE )
		self.mTunerMgr.CancelConfiguration( )
		self.mDataCache.Channel_ReTune( )
		self.SetParentID( WinMgr.WIN_ID_MAINMENU )
		self.mTunerMgr.SetNeedLoad( True )
		self.SetVideoRestore( )
		self.SetFirstInstallation( False )

