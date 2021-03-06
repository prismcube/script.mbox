from pvr.gui.WindowImport import *


MAX_SATELLITE_CNT = 4


class SatelliteConfigOnecable( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mSatelliteCount = 0
		self.mSatellitelist = []
		self.mCurrentSatellite = None
		

	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		
		self.SetSettingWindowLabel( 'OneCable Configuration' )
		self.getControl( E_SETTING_DESCRIPTION ).setLabel( 'OneCable configuration' )

		self.mCurrentSatellite = self.mTunerMgr.GetConfiguredSatellitebyIndex( 0 )
		self.LoadConfigedSatellite( )

		self.AddInputControl( E_Input01, 'Configure System', '' )
		
		listitem = []
		for i in range( self.mSatelliteCount ) :
			listitem.append( '%d' % ( i + 1 ) )

		self.AddUserEnumControl( E_SpinEx01, 'Number of Satellite', listitem, 0 )

		startId = E_Input02
		for i in range( MAX_SATELLITE_CNT ) :
			self.AddInputControl( startId, 'Satellite %d' % ( i + 1 ), self.mSatellitelist[i] )
			startId += 100
		
		self.InitControl( )
		self.getControl( E_SpinEx01 + 3 ).selectItem( self.mSatelliteCount - 1 )
		self.DisableControl( )

				
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

			self.ResetAllControl( )
			WinMgr.GetInstance().CloseWindow( )

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
			position = self.GetSelectedIndex( E_SpinEx01 ) + 1
			self.mTunerMgr.SetOnecableSatelliteCount( position )
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_ONECABLE_2 )
		
		elif groupId == E_SpinEx01 :
			self.DisableControl( )

		else :
			position = self.GetControlIdToListIndex( groupId ) - 2
			self.mTunerMgr.SetCurrentConfigIndex( position )
			self.ResetAllControl( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIG_SIMPLE )
			
	def onFocus( self, aControlId ) :
		pass


	def DisableControl( self ) : 
		for i in range( MAX_SATELLITE_CNT ) :
			if ( self.GetSelectedIndex( E_SpinEx01 ) + 1 ) > i :
				self.SetEnableControl( self.GetListIndextoControlId( 2 + i ), True )
				self.SetVisibleControl( self.GetListIndextoControlId( 2 + i ), True )
			else :
				self.SetEnableControl( self.GetListIndextoControlId( 2 + i ), False )
				self.SetVisibleControl( self.GetListIndextoControlId( 2 + i ), False ) 
		
		
	def LoadConfigedSatellite( self ) :
		configuredList = []

		configuredList = self.mTunerMgr.GetConfiguredSatelliteList( )
		if configuredList and configuredList[0].mError == 0 :
			self.mSatelliteCount = len( configuredList )

			for i in range( MAX_SATELLITE_CNT ) :
				if i < self.mSatelliteCount :
					self.mSatellitelist.append( self.mDataCache.GetFormattedSatelliteName( configuredList[i].mSatelliteLongitude, configuredList[i].mBandType ) )
				else :
					self.mSatellitelist.append( '' ) # dummy Data
		else :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( 'ERROR', 'Save Configuration Fail' )
 			dialog.doModal( )
 			self.ResetAllControl( )
			WinMgr.GetInstance().CloseWindow( )
