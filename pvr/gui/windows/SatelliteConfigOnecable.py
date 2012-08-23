from pvr.gui.WindowImport import *


class SatelliteConfigOnecable( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mSatelliteCount = 0
		self.mSatelliteNamelist = []
		self.mCurrentSatellite = None
		

	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		
		self.SetSettingWindowLabel( MR_LANG( 'OneCable Configuration' ) )
		self.LoadNoSignalState( )
#		self.getControl( E_SETTING_DESCRIPTION ).setLabel( MR_LANG( 'OneCable configuration' ) )

		self.LoadConfigedSatellite( )
		self.mCurrentSatellite = self.mTunerMgr.GetConfiguredSatellitebyIndex( 0 )
		
		self.AddInputControl( E_Input01, MR_LANG( 'Initial Setup' ), '', MR_LANG( 'Configure the initial settings for OneCable' ) )
		
		listitem = []
		for i in range( MAX_SATELLITE_CNT_ONECABLE ) :
			listitem.append( '%d' % ( i + 1 ) )

		self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Number of Satellites' ), listitem, 0, MR_LANG( 'Select number of satellites for OneCable' ) )

		startId = E_Input02
		for i in range( MAX_SATELLITE_CNT_ONECABLE ) :
			self.AddInputControl( startId, MR_LANG( 'Satellite %d' ) % ( i + 1 ), self.mSatelliteNamelist[i], MR_LANG( 'Press the OK button to setup %d' ) % (i + 1) )
			startId += 100

		self.InitControl( )
		self.getControl( E_SpinEx01 + 3 ).selectItem( self.mSatelliteCount - 1 )
		self.DisableControl( )
		self.mInitialized = True
		self.setDefaultControl( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_PARENT_DIR :
			if self.mSatelliteCount > 1 :
				for i in range( self.mSatelliteCount - 1 ) :
					satellite = self.mTunerMgr.GetConfiguredSatellitebyIndex( i + 1 )
					satellite.mIsOneCable = self.mCurrentSatellite.mIsOneCable
					satellite.mOneCablePin = self.mCurrentSatellite.mOneCablePin
					satellite.mOneCableMDU = self.mCurrentSatellite.mOneCableMDU
					satellite.mOneCableLoFreq1 = self.mCurrentSatellite.mOneCableLoFreq1
					satellite.mOneCableLoFreq2 = self.mCurrentSatellite.mOneCableLoFreq2
					satellite.mOneCableUBSlot = self.mCurrentSatellite.mOneCableUBSlot
					satellite.mOneCableUBFreq = self.mCurrentSatellite.mOneCableUBFreq

			if self.mTunerMgr.GetOneCableSatelliteCount( ) < self.mSatelliteCount :
				for i in range( self.mSatelliteCount ) :
					if self.mTunerMgr.GetOneCableSatelliteCount( ) < ( i + 1 ) :
						self.mTunerMgr.DeleteConfiguredSatellitebyIndex( i )

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

		if groupId == E_Input01 :
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_ONECABLE_2 )
		
		elif groupId == E_SpinEx01 :
			self.DisableControl( )

		else :
			position = self.GetControlIdToListIndex( groupId ) - 2
			self.mTunerMgr.SetCurrentConfigIndex( position )
			self.ResetAllControl( )
			if self.mSatelliteNamelist[position] == MR_LANG( 'None' ) :
				self.mTunerMgr.AddConfiguredSatellite( 0 )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_SIMPLE )


	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return
		if self.mLastFocused != aControlId :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId


	def DisableControl( self ) : 
		position = self.GetSelectedIndex( E_SpinEx01 ) + 1
		self.mTunerMgr.SetOnecableSatelliteCount( position )
		for i in range( MAX_SATELLITE_CNT_ONECABLE ) :
			if ( self.GetSelectedIndex( E_SpinEx01 ) + 1 ) > i :
				self.SetEnableControl( self.GetListIndextoControlId( 2 + i ), True )
				self.SetVisibleControl( self.GetListIndextoControlId( 2 + i ), True )
			else :
				self.SetEnableControl( self.GetListIndextoControlId( 2 + i ), False )
				self.SetVisibleControl( self.GetListIndextoControlId( 2 + i ), False ) 


	def LoadConfigedSatellite( self ) :
		self.mSatelliteNamelist = []

		configuredList = self.mTunerMgr.GetConfiguredSatelliteList( )
		self.mSatelliteCount = len( configuredList )

		for i in range( MAX_SATELLITE_CNT_ONECABLE ) :
			if i < self.mSatelliteCount :
				self.mSatelliteNamelist.append( self.mDataCache.GetFormattedSatelliteName( configuredList[i].mSatelliteLongitude, configuredList[i].mBandType ) )
			else :
				self.mSatelliteNamelist.append( MR_LANG( 'None' ) )

