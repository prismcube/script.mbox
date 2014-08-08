from elisinterface.ElisEnum import ElisEnum
import pvr.DataCacheMgr
import pvr.ElisMgr
from elisinterface.ElisProperty import ElisPropertyEnum, ElisPropertyInt
from elisinterface.ElisClass import ElisISatelliteConfig
from pvr.gui.GuiConfig import *


gTunerConfigMgr = None


def GetInstance( ) :
	global gTunerConfigMgr
	if not gTunerConfigMgr :
		gTunerConfigMgr = TunerConfigMgr( )
	return gTunerConfigMgr


class TunerConfigMgr( object ) :
	def __init__( self ) :
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.mDataCache = pvr.DataCacheMgr.GetInstance( )

		self.mAllSatelliteList			= []

		self.mDiseqc10List1				= []
		self.mDiseqc10List2				= []
		self.mDiseqc11List1				= []
		self.mDiseqc11List2				= []
		self.mMotorizeList1				= []
		self.mMotorizeList2				= []
		self.mMotorizeUsalsList1		= []
		self.mMotorizeUsalsList2		= []
		self.mOneCableList1				= []
		self.mOneCableList2				= []
		self.mSimpleLnbList1			= []
		self.mSimpleLnbList2			= []
			
		self.mCurrentTunerNumber		= 0
		self.mCurrentConfigIndex		= 0
		self.mNeedLoad					= True

		self.mOrgConfiguredList1		= []
		self.mOrgConfiguredList2		= []
		self.mOriginalTunerConfig		= []
		
		self.mOnecableSatelliteCount	= 0
		self.mFirstInstallation	 		= False


	def GetCurrentTunerNumber( self ) :
		return self.mCurrentTunerNumber


	def SetCurrentTunerNumber( self, aCurrentTuner ) :
		self.mCurrentTunerNumber = aCurrentTuner


	def GetCurrentTunerType( self ) :
		return self.GetTunerTypeByTunerIndex( self.GetCurrentTunerNumber( ) )


	def GetCurrentTunerTypeString( self ) :
		tunerNumber = self.GetCurrentTunerNumber( )
		if tunerNumber == E_TUNER_1 :
			return ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetPropString( )
		elif tunerNumber == E_TUNER_2 :
			return ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).GetPropString( )
		else :
			LOG_ERR( 'Invalid Tuner Index : %s' % aTunerIndex )	


	def GetTunerTypeByTunerIndex( self, aTunerIndex ) :
		if aTunerIndex == E_TUNER_1 :
			return ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( )
		elif aTunerIndex == E_TUNER_2 :
			return ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).GetProp( )
		else :
			LOG_ERR( 'Invalid Tuner Index : %s' % aTunerIndex )


	def GetCurrentTunerConnectionType( self ) :
		if pvr.Platform.GetPlatform( ).GetTunerType( ) == TUNER_TYPE_DVBS_DUAL :
			return ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander ).GetProp( )
		else :
			return E_TUNER_SEPARATED


	def GetCurrentTunerConfigType( self ) :
		return ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander ).GetProp( )


	def GetConfiguredSatelliteList( self ) :
		return self.GetCurrentSatelliteList( self.GetCurrentTunerNumber( ) )


	def GetConfiguredSatelliteListbyTunerIndex( self, aTunerIndex ) :
		return self.GetCurrentSatelliteList( aTunerIndex )


	def GetCurrentConfiguredSatellite( self ) :
		return self.GetCurrentSatelliteList( self.GetCurrentTunerNumber( ) )[ self.GetCurrentConfigIndex( ) ]


	def GetConfiguredSatellitebyIndex( self, aSatelliteIndex ) :
		configuredsatellitelist = self.GetConfiguredSatelliteList( )
		if len( configuredsatellitelist ) > 0 :
			return configuredsatellitelist[ aSatelliteIndex ]
		else :
			return None


	def SetCurrentConfigIndex( self, aCurrentConfigIndex ) :
		self.mCurrentConfigIndex = aCurrentConfigIndex


	def GetCurrentConfigIndex( self ) :
		return self.mCurrentConfigIndex


	def AddConfiguredSatellite( self, aIndex ) :
		config = self.GetMakedConfiguredSatellite( aIndex )
		tmpTunerConfiguredList = self.GetConfiguredSatelliteList( )
		tmpTunerConfiguredList.append( config )


	def GetMakedConfiguredSatellite( self, aIndex ) :
		config = ElisISatelliteConfig( )
		config.reset( )
		config.mSatelliteLongitude = self.mAllSatelliteList[ aIndex ].mLongitude
		config.mBandType = self.mAllSatelliteList[ aIndex ].mBand
		config.mIsConfigUsed = 1
		config.mUSALSLongitude = 0

		if config.mBandType == ElisEnum.E_BAND_C :
			config.mLnbType = ElisEnum.E_LNB_SINGLE
			config.mLowLNB = 5150
			config.mHighLNB = 0
			config.mLNBThreshold = 0
		else :
			config.mLnbType = ElisEnum.E_LNB_UNIVERSAL
			config.mLowLNB = 9750
			config.mHighLNB = 10600
			config.mLNBThreshold = 11700

		return config


	def DeleteConfiguredSatellitebyIndex( self, aIndex ) :
		del self.GetConfiguredSatelliteList( )[ aIndex ]


	def Load( self ) :
		self.mAllSatelliteList = self.mDataCache.GetAllSatelliteList( )

		tmpTuner1ConfiguredList = deepcopy( self.mDataCache.GetConfiguredSatelliteListByTunerIndex( E_TUNER_1 ) )
		tmpTuner2ConfiguredList = deepcopy( self.mDataCache.GetConfiguredSatelliteListByTunerIndex( E_TUNER_2 ) )
		if tmpTuner1ConfiguredList == None :
			tmpTuner1ConfiguredList = []
		if tmpTuner2ConfiguredList == None :
			tmpTuner2ConfiguredList = []

		self.mOrgConfiguredList1 = deepcopy( tmpTuner1ConfiguredList )
		self.mOrgConfiguredList2 = deepcopy( tmpTuner2ConfiguredList )

		self.mDiseqc10List1			= deepcopy( tmpTuner1ConfiguredList )
		self.SatelliteSetFlag( self.mDiseqc10List1, E_TUNER_1, E_DISEQC_1_0 )
		self.mDiseqc10List2			= deepcopy( tmpTuner2ConfiguredList )
		self.SatelliteSetFlag( self.mDiseqc10List2, E_TUNER_2, E_DISEQC_1_0 )
		self.mDiseqc11List1			= deepcopy( tmpTuner1ConfiguredList )
		self.SatelliteSetFlag( self.mDiseqc11List1, E_TUNER_1, E_DISEQC_1_1 )
		self.mDiseqc11List2			= deepcopy( tmpTuner2ConfiguredList )
		self.SatelliteSetFlag( self.mDiseqc11List2, E_TUNER_2, E_DISEQC_1_1 )
		self.mMotorizeList1			= deepcopy( tmpTuner1ConfiguredList )
		self.SatelliteSetFlag( self.mMotorizeList1, E_TUNER_1, E_MOTORIZE_1_2 )
		self.mMotorizeList2			= deepcopy( tmpTuner2ConfiguredList )
		self.SatelliteSetFlag( self.mMotorizeList2, E_TUNER_2, E_MOTORIZE_1_2 )
		self.mMotorizeUsalsList1	= deepcopy( tmpTuner1ConfiguredList )
		self.SatelliteSetFlag( self.mMotorizeUsalsList1, E_TUNER_1, E_MOTORIZE_USALS )
		self.mMotorizeUsalsList2	= deepcopy( tmpTuner2ConfiguredList )
		self.SatelliteSetFlag( self.mMotorizeUsalsList2, E_TUNER_2, E_MOTORIZE_USALS )
		self.mOneCableList1			= deepcopy( tmpTuner1ConfiguredList )
		self.mOneCableList2 		= deepcopy( tmpTuner2ConfiguredList )
		if len( self.mOneCableList1 ) > MAX_SATELLITE_CNT_ONECABLE :
			self.mOneCableList1 = self.mOneCableList1[0:2]
		if len( self.mOneCableList2 ) > MAX_SATELLITE_CNT_ONECABLE :
			self.mOneCableList2 = self.mOneCableList2[0:2]
		self.SatelliteSetFlag( self.mOneCableList1, E_TUNER_1, E_ONE_CABLE )
		self.SatelliteSetFlag( self.mOneCableList2, E_TUNER_2, E_ONE_CABLE )
		self.mSimpleLnbList1 = []
		self.mSimpleLnbList2 = []
		if len( tmpTuner1ConfiguredList ) > 0 :	
			self.mSimpleLnbList1 = [ tmpTuner1ConfiguredList[0] ]
		if len( tmpTuner2ConfiguredList ) > 0 :	
			self.mSimpleLnbList2 = [ tmpTuner2ConfiguredList[0] ]
		self.SatelliteSetFlag( self.mSimpleLnbList1, E_TUNER_1, E_SIMPLE_LNB )
		self.SatelliteSetFlag( self.mSimpleLnbList2, E_TUNER_2, E_SIMPLE_LNB )


	def SaveConfiguration( self ) :
		if not self.mDataCache.GetStanbyClosing( ) :
			self.SatelliteConfigSaveList( )
		self.mDataCache.LoadConfiguredSatellite( )


	def CancelConfiguration( self ) :
		if not self.mDataCache.GetStanbyClosing( ) :
			self.Restore( )
		self.mDataCache.LoadConfiguredSatellite( )


	def SatelliteConfigSaveList( self ) :
		LOG_TRACE( 'Save Satellite Config List!' )
		self.mCommander.Satelliteconfig_DeleteAll( ) 

		tuner1ConfiguredList = self.GetCurrentSatelliteList( E_TUNER_1 )
		tuner2ConfiguredList = self.GetCurrentSatelliteList( E_TUNER_2 )

		if len( tuner1ConfiguredList ) > 0 :
			self.SatelliteSetFlag( tuner1ConfiguredList, E_TUNER_1, self.GetTunerTypeByTunerIndex( E_TUNER_1 ) )

		if self.GetCurrentTunerConfigType( ) == E_SAMEWITH_TUNER :
			tuner2ConfiguredList = deepcopy( tuner1ConfiguredList )
			if tuner2ConfiguredList :
				for i in range( len( tuner2ConfiguredList ) ) :
					tuner2ConfiguredList[i].mTunerIndex = E_TUNER_2
					#if self.GetTunerTypeByTunerIndex( E_TUNER_1 ) == E_ONE_CABLE :
					#	tuner2ConfiguredList[i].mOneCablePin		= ElisPropertyInt( 'Tuner2 Pin Code', self.mCommander ).GetProp( )
					#	tuner2ConfiguredList[i].mOneCableUBSlot		= ElisPropertyInt( 'Tuner2 SCR' , self.mCommander ).GetProp( )
					#	tuner2ConfiguredList[i].mOneCableUBFreq		= ElisPropertyInt( 'Tuner2 SCR Frequency', self.mCommander ).GetProp( )
				
		else :
			if len( tuner2ConfiguredList ) > 0 :
				self.SatelliteSetFlag( tuner2ConfiguredList, E_TUNER_2, self.GetTunerTypeByTunerIndex( E_TUNER_2 ) )

		"""
		for st in tuner1ConfiguredList :
			st.printdebug( )

		for st in tuner2ConfiguredList :
			st.printdebug( )
		"""

		if len( tuner1ConfiguredList ) > 0 :
			self.mCommander.Satelliteconfig_SaveList( tuner1ConfiguredList )
		if len( tuner2ConfiguredList ) > 0 :
			self.mCommander.Satelliteconfig_SaveList( tuner2ConfiguredList )


	def Restore( self ) :
		ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander ).SetProp( self.mOriginalTunerConfig[0] )
		ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander ).SetProp( self.mOriginalTunerConfig[1] )
		ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).SetProp( self.mOriginalTunerConfig[2] )
		ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).SetProp( self.mOriginalTunerConfig[3] )	

		ElisPropertyEnum( 'MDU', self.mCommander ).SetProp( self.mOriginalTunerConfig[4] )
		ElisPropertyInt( 'Tuner1 Pin Code', self.mCommander ).SetProp( self.mOriginalTunerConfig[5] )
		ElisPropertyInt( 'Tuner2 Pin Code', self.mCommander ).SetProp( self.mOriginalTunerConfig[6] )
		ElisPropertyInt( 'Tuner1 SCR', self.mCommander ).SetProp( self.mOriginalTunerConfig[7] )
		ElisPropertyInt( 'Tuner2 SCR', self.mCommander ).SetProp( self.mOriginalTunerConfig[8] )
		ElisPropertyInt( 'Tuner1 SCR Frequency', self.mCommander ).SetProp( self.mOriginalTunerConfig[9] )
		ElisPropertyInt( 'Tuner2 SCR Frequency', self.mCommander ).SetProp( self.mOriginalTunerConfig[10] )

		ElisPropertyInt( 'MyLongitude', self.mCommander ).SetProp( self.mOriginalTunerConfig[11] )
		ElisPropertyInt( 'MyLatitude', self.mCommander ).SetProp( self.mOriginalTunerConfig[12] )

		self.mCommander.Satelliteconfig_DeleteAll( ) 
		if len( self.mOrgConfiguredList1 ) > 0 :
			self.mCommander.Satelliteconfig_SaveList( self.mOrgConfiguredList1 )
			
		if len( self.mOrgConfiguredList2 ) > 0 :
			self.mCommander.Satelliteconfig_SaveList( self.mOrgConfiguredList2 )


	def SatelliteSetFlag( self, aSatelliteList, aTunerNumber, aTunerType ) :
		if len( aSatelliteList ) > 0 :
			for i in range( len( aSatelliteList ) ) :
				aSatelliteList[i].mTunerIndex = aTunerNumber
				aSatelliteList[i].mSlotNumber = i
				self.SetTunerTypeFlag( aSatelliteList[i], aTunerType )


	def SetTunerTypeFlag( self, aSatellite, aType ) :
		if aType == E_DISEQC_1_0 :
			aSatellite.mMotorizedType = ElisEnum.E_MOTORIZED_OFF
			aSatellite.mIsOneCable = 0
			aSatellite.mMotorizedData = 0
			aSatellite.mDisEqc11 = 0
			if aSatellite.mSlotNumber >= E_MAX_SATELLITE_COUNT :
				aSatellite.mIsConfigUsed = 0
			else :
				aSatellite.mIsConfigUsed = 1

		elif aType == E_DISEQC_1_1 :
			aSatellite.mMotorizedType = ElisEnum.E_MOTORIZED_OFF
			aSatellite.mIsOneCable = 0
			aSatellite.mMotorizedData = 0
			aSatellite.mIsConfigUsed = 1
			
		elif aType == E_SIMPLE_LNB :
			aSatellite.mMotorizedType = ElisEnum.E_MOTORIZED_OFF
			aSatellite.mIsOneCable = 0
			aSatellite.mMotorizedData = 0
			aSatellite.mIsConfigUsed = 1
			aSatellite.mDisEqc11 = 0
			aSatellite.mDisEqcMode = 0
			aSatellite.mDisEqcRepeat = 0
			
		elif aType == E_MOTORIZE_1_2 :
			aSatellite.mMotorizedType = ElisEnum.E_MOTORIZED_ON
			aSatellite.mIsOneCable = 0
			aSatellite.mMotorizedData = aSatellite.mSlotNumber + 1
			aSatellite.mIsConfigUsed = 1
			aSatellite.mFrequencyLevel = 0
			"""
			aSatellite.mDisEqc11 = 0
			aSatellite.mDisEqcMode = 0
			aSatellite.mDisEqcRepeat = 0
			"""

		elif aType == E_MOTORIZE_USALS :
			aSatellite.mMotorizedType = ElisEnum.E_MOTORIZED_USALS
			aSatellite.mIsOneCable = 0
			aSatellite.mMotorizedData = 0
			aSatellite.mIsConfigUsed = 1
			aSatellite.mFrequencyLevel = 0
			"""
			aSatellite.mDisEqc11 = 0
			aSatellite.mDisEqcMode = 0
			aSatellite.mDisEqcRepeat = 0
			"""
			
		elif aType == E_ONE_CABLE :
			aSatellite.mMotorizedType = ElisEnum.E_MOTORIZED_OFF
			aSatellite.mIsOneCable = 1
			aSatellite.mMotorizedData = 0
			aSatellite.mIsConfigUsed = 1
			aSatellite.mDisEqc11 = 0
			aSatellite.mDisEqcMode = 0
			aSatellite.mDisEqcRepeat = 0


	def GetCurrentSatelliteList( self, aTunerNumber ) :
		if aTunerNumber == E_TUNER_1 :
			tunertype =  self.GetTunerTypeByTunerIndex( E_TUNER_1 )
			if tunertype == E_DISEQC_1_0 :
				return self.mDiseqc10List1
			elif tunertype == E_DISEQC_1_1 :
				return self.mDiseqc11List1
			elif tunertype == E_MOTORIZE_1_2 :
				return self.mMotorizeList1
			elif tunertype == E_MOTORIZE_USALS :
				return self.mMotorizeUsalsList1
			elif tunertype == E_ONE_CABLE :
				return self.mOneCableList1
			elif tunertype == E_SIMPLE_LNB :
				return self.mSimpleLnbList1
		elif aTunerNumber == E_TUNER_2 :
			tunertype =  self.GetTunerTypeByTunerIndex( E_TUNER_2 )
			if tunertype == E_DISEQC_1_0 :
				return self.mDiseqc10List2
			elif tunertype == E_DISEQC_1_1 :
				return self.mDiseqc11List2
			elif tunertype == E_MOTORIZE_1_2 :
				return self.mMotorizeList2
			elif tunertype == E_MOTORIZE_USALS :
				return self.mMotorizeUsalsList2
			elif tunertype == E_ONE_CABLE :
				return self.mOneCableList2
			elif tunertype == E_SIMPLE_LNB :
				return self.mSimpleLnbList2
		else :
			LOG_ERR( 'Invalid Tuner Number : %s' % aTunerNumber )


	def GetOriginalConfiguredListByTunerNumber( self, aTunerNumber ) :
		if aTunerNumber == E_TUNER_1 :
			return self.mOrgConfiguredList1
		elif aTunerNumber == E_TUNER_2 :
			return self.mOrgConfiguredList2
		else :
			LOG_ERR( 'Invalid Tuner Number : %s' % aTunerNumber )


	def LoadOriginalTunerConfig( self ) :
		self.mOriginalTunerConfig = self.GetCurrentTunerConfig( )


	def GetOriginalTunerConfig( self ) :
		return self.mOriginalTunerConfig


	def GetCurrentTunerConfig( self ) :
		currentTunerConfig = []
		currentTunerConfig.append( ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander ).GetProp( ) )
		currentTunerConfig.append( ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander ).GetProp( ) )
		currentTunerConfig.append( ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( ) )
		currentTunerConfig.append( ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).GetProp( ) )
		currentTunerConfig.append( ElisPropertyEnum( 'MDU', self.mCommander ).GetProp( ) )
		currentTunerConfig.append( ElisPropertyInt( 'Tuner1 Pin Code', self.mCommander ).GetProp( ) )
		currentTunerConfig.append( ElisPropertyInt( 'Tuner2 Pin Code', self.mCommander ).GetProp( ) )
		currentTunerConfig.append( ElisPropertyInt( 'Tuner1 SCR', self.mCommander ).GetProp( ) )
		currentTunerConfig.append( ElisPropertyInt( 'Tuner2 SCR', self.mCommander ).GetProp( ) )
		currentTunerConfig.append( ElisPropertyInt( 'Tuner1 SCR Frequency', self.mCommander ).GetProp( ) )
		currentTunerConfig.append( ElisPropertyInt( 'Tuner2 SCR Frequency', self.mCommander ).GetProp( ) )
		currentTunerConfig.append( ElisPropertyInt( 'MyLongitude', self.mCommander ).GetProp( ) )
		currentTunerConfig.append( ElisPropertyInt( 'MyLatitude', self.mCommander ).GetProp( ) )
		return currentTunerConfig


	def SetNeedLoad( self, aNeedLoad ) :
		self.mNeedLoad = aNeedLoad


	def GetNeedLoad( self ) :
		return self.mNeedLoad


	def SetOnecableSatelliteCount( self, aCount ) :
		self.mOnecableSatelliteCount = aCount


	def GetOneCableSatelliteCount( self ) :
		#return len( self.GetConfiguredSatelliteList( ) )
		return self.mOnecableSatelliteCount


	def CheckSameSatellite( self, aLongitude, aBand ) :
		ConfiguredSatelliteList = self.GetConfiguredSatelliteList( )
		if len( ConfiguredSatelliteList ) > 0 :
			for satellite in ConfiguredSatelliteList :
				if satellite.mSatelliteLongitude == aLongitude and satellite.mBandType == aBand :
					return False
		return True


	def SyncChannelBySatellite( self ) :
		if self.mDataCache.GetStanbyClosing( ) :
			return
		channelSatelliteList = self.mDataCache.Satellite_GetListByChannel( )
		configuredSatelliteList = self.mDataCache.Satellite_GetConfiguredList( )
		channelSave = False

		if channelSatelliteList :
			if configuredSatelliteList :
				for channelSatellite in channelSatelliteList :
					findSatellite = False
					for configuredSatellite in configuredSatelliteList :
						if channelSatellite.mLongitude == configuredSatellite.mLongitude and channelSatellite.mBand == configuredSatellite.mBand :
							findSatellite = True
							break
					if findSatellite == False :
						channelSave = True
						self.mDataCache.Channel_DeleteBySatellite( channelSatellite.mLongitude, channelSatellite.mBand, False )

				if channelSave :
					self.mDataCache.Channel_Save( )

				if self.mDataCache.Channel_GetList( ) :
					return
				else :
					self.mDataCache.Player_AVBlank( True )
					return

			self.mDataCache.Channel_DeleteAll( )
			self.mDataCache.Channel_Save( )
			self.mDataCache.Channel_ReLoad( False )
			if not self.mDataCache.Get_Player_AVBlank( ) :
				self.mDataCache.Player_AVBlank( True )


	def CompareCurrentConfiguredState( self ) :
		configuredList1			= self.GetOriginalConfiguredListByTunerNumber( E_TUNER_1 )
		currentconfiguredList1	= self.GetCurrentSatelliteList( E_TUNER_1 )
		configuredList2			= self.GetOriginalConfiguredListByTunerNumber( E_TUNER_2 )
		currentconfiguredList2	= self.GetCurrentSatelliteList( E_TUNER_2 )
		if len( currentconfiguredList1 ) == 0 or len( currentconfiguredList2 ) == 0 or len( configuredList1 ) == 0 or len( configuredList1 ) == 0 :
			return False

		if len( configuredList1 ) != len( currentconfiguredList1 ) :
			return False
		if len( configuredList2 ) != len( currentconfiguredList2 ) :
			return False
			
		if self.GetCurrentTunerConfigType( ) == E_SAMEWITH_TUNER :
			for i in range( len( configuredList1 ) ) :
				if configuredList1[i].__dict__ != currentconfiguredList1[i].__dict__ :
					return False
		else :
			for i in range( len( configuredList1 ) ) :
				if configuredList1[i].__dict__ != currentconfiguredList1[i].__dict__ :
					return False
			for i in range( len( configuredList2 ) ) :
				if configuredList2[i].__dict__ != currentconfiguredList2[i].__dict__ :
					return False

		return True


	def CompareConfigurationProperty( self ) :
		if self.GetOriginalTunerConfig( ) != self.GetCurrentTunerConfig( ) :
			return False
		return True
