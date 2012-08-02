from ElisEnum import ElisEnum
import pvr.DataCacheMgr
import pvr.ElisMgr
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
from ElisClass import ElisISatelliteConfig
from pvr.gui.GuiConfig import *


gTunerConfigMgr = None


def GetInstance( ) :
	global gTunerConfigMgr
	if not gTunerConfigMgr :
		print 'lael98 check create instance'
		gTunerConfigMgr = TunerConfigMgr( )
		
	else :
		print 'lael98 check already TunerConfigMgr is created'
		
	return gTunerConfigMgr


class TunerConfigMgr( object ) :
	def __init__( self ) :
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.mDataCache = pvr.DataCacheMgr.GetInstance( )

		self.mDiseqc10List1 = []
		self.mDiseqc10List2 = []
		self.mDiseqc11List1 = []
		self.mDiseqc11List2 = []
		self.mMotorizeList1 = []
		self.mMotorizeList2 = []
		self.mMotorizeUsalsList1 = []
		self.mMotorizeUsalsList2 = []
		self.mOneCableList1 = []
		self.mOneCableList2 = []
		self.mSimpleLnbList1 = []
		self.mSimpleLnbList2 = []
		
		self.mConfiguredList1 = []
		self.mConfiguredList2 = []		
		self.mCurrentTuner = 0
		self.mCurrentConfigIndex = 0
		self.mCurrentTunerType = 0
		self.mNeedLoad = True

		self.mOrgConfiguredList1 = []
		self.mOrgConfiguredList2 = []

		self.mOrgTuner2ConnectType = 0
		self.mOrgTuner2Config = 0
		self.mOrgTuner1Type = 0
		self.mOrgTuner2Type = 0

		self.mOrgMDU = 0
		self.mOrgTuner1PinCode = 0
		self.mOrgTuner2PinCode = 0
		self.mOrgTuner1SCR = 0
		self.mOrgTuner2SCR = 0
		self.mOrgTuner1SCRFreq = 0
		self.mOrgTuner2SCRFreq = 0
		
		self.mOrgMyLongitude = 0
		self.mOrgMyLatitude = 0
		
		self.mAllSatelliteList = []
		self.mOriginalTunerConfig = []
		self.mOnecableSatelliteCount = 0

		self.mFirstInstallation	 = False


	def GetCurrentTunerIndex( self ) :
		return self.mCurrentTuner


	def SetCurrentTunerIndex( self, aCurrentTuner ) :
		self.mCurrentTuner = aCurrentTuner


	def GetCurrentConfiguredSatellite( self ) :
		if self.mCurrentTuner == E_TUNER_1 :	
			return self.mConfiguredList1[ self.mCurrentConfigIndex ]
			
		elif self.mCurrentTuner == E_TUNER_2 :
			return self.mConfiguredList2[ self.mCurrentConfigIndex ]
			
		else :
			LOG_ERR( 'ERROR : can not find configured satellite' )
	
		return None


	def GetConfiguredSatelliteList( self ) :
		if self.mCurrentTuner == E_TUNER_1 :
			return self.mConfiguredList1

		elif self.mCurrentTuner == E_TUNER_2 :
			return self.mConfiguredList2

		else :
			LOG_ERR( 'ERROR : unknown tuner' )
			return self.mConfiguredList1


	def GetConfiguredSatellitebyIndex( self, aSatelliteIndex ) :
		if self.mCurrentTuner == E_TUNER_1 :
			if self.mConfiguredList1 :
				return self.mConfiguredList1[ aSatelliteIndex ]
			else :
				return None

		elif self.mCurrentTuner == E_TUNER_2:
			if self.mConfiguredList2 :
				return self.mConfiguredList2[ aSatelliteIndex ]	
			else :
				return None
		else :
			LOG_ERR( 'ERROR : can not find configured satellite' )
	
		return None


	def GetCurrentTunerType( self ) :
		if self.mCurrentTuner == E_TUNER_1 :	
			property = ElisPropertyEnum( 'Tuner1 Type', self.mCommander )
			return property.GetProp( )

		elif self.mCurrentTuner == E_TUNER_2:
			property = ElisPropertyEnum( 'Tuner2 Type', self.mCommander )
			return property.GetProp( )


	def GetCurrentTunerConnectionType( self ) :
		property = ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander )
		return property.GetProp( )


	def GetCurrentTunerConfigType( self ) :
		property = ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander )
		return property.GetProp( )


	def SetCurrentConfigIndex( self, aCurrentConfigIndex ) :
		self.mCurrentConfigIndex = aCurrentConfigIndex


	def GetCurrentConfigIndex( self ) :
		return self.mCurrentConfigIndex


	def GetConfiguredSatellitebyTunerIndex( self, aTunerIndex ) :
		if aTunerIndex == E_TUNER_1 :
			return self.mConfiguredList1

		elif aTunerIndex == E_TUNER_2 :
			return self.mConfiguredList2

		else :
			LOG_ERR( 'ERROR : unknown tuner' )
			return self.mConfiguredList1
			

	def SetOnecableSatelliteCount( self, aCount ) :
		self.mOnecableSatelliteCount = aCount


	def GetOneCableSatelliteCount( self ) :
		return self.mOnecableSatelliteCount
			

	def AddConfiguredSatellite( self, aIndex ) :
		config = self.GetDefaultConfig( )
		config.mSatelliteLongitude = self.mAllSatelliteList[ aIndex ].mLongitude
		config.mBandType = self.mAllSatelliteList[ aIndex ].mBand

		if self.mConfiguredList1 == None :
			self.mConfiguredList1 = []

		if self.mConfiguredList2 == None :
			self.mConfiguredList2 = []

		if self.GetCurrentTunerConfigType( ) == E_SAMEWITH_TUNER :
			self.mConfiguredList1.append( config )

		elif self.GetCurrentTunerConfigType( ) == E_DIFFERENT_TUNER :
			if self.GetCurrentTunerIndex( ) == E_TUNER_1 :
				self.mConfiguredList1.append( config )

			elif self.GetCurrentTunerIndex( ) == E_TUNER_2 :
				config.mTunerIndex = 1
				self.mConfiguredList2.append( config )


	def DeleteConfiguredSatellitebyIndex( self, aIndex ) :
		if self.GetCurrentTunerConfigType( ) == E_SAMEWITH_TUNER :
			del self.mConfiguredList1[ aIndex ]

		elif self.GetCurrentTunerConfigType( ) == E_DIFFERENT_TUNER :

			if self.GetCurrentTunerIndex( ) == E_TUNER_1 :
				del self.mConfiguredList1[ aIndex ]

			elif self.GetCurrentTunerIndex( ) == E_TUNER_2 :
				del self.mConfiguredList2[ aIndex ]


	def Reset( self ) :
		self.mCurrentTuner  = 0
		self.mCurrentConfigIndex = 0
		self.mCurrentTunerType = 0
		self.mOnecableSatelliteCount = 0


	def Restore( self ) :
		# Tuner
		ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander ).SetProp( self.mOrgTuner2ConnectType )
		ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander ).SetProp( self.mOrgTuner2Config )
		ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).SetProp( self.mOrgTuner1Type )
		ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).SetProp( self.mOrgTuner2Type )	

		# Onecable
		ElisPropertyEnum( 'MDU', self.mCommander ).SetProp( self.mOrgMDU )
		ElisPropertyInt( 'Tuner1 Pin Code', self.mCommander ).SetProp( self.mOrgTuner1PinCode )
		ElisPropertyInt( 'Tuner2 Pin Code', self.mCommander ).SetProp( self.mOrgTuner2PinCode )
		ElisPropertyInt( 'Tuner1 SCR', self.mCommander ).SetProp( self.mOrgTuner1SCR )
		ElisPropertyInt( 'Tuner2 SCR', self.mCommander ).SetProp( self.mOrgTuner2SCR )
		ElisPropertyInt( 'Tuner1 SCR Frequency', self.mCommander ).SetProp( self.mOrgTuner1SCRFreq )
		ElisPropertyInt( 'Tuner2 SCR Frequency', self.mCommander ).SetProp( self.mOrgTuner2SCRFreq )

		# Motorized
		ElisPropertyInt( 'MyLongitude', self.mCommander ).SetProp( self.mOrgMyLongitude )
		ElisPropertyInt( 'MyLatitude', self.mCommander ).SetProp( self.mOrgMyLatitude )

		self.mCommander.Satelliteconfig_DeleteAll( ) 
		if self.mOrgConfiguredList1 :
			self.mCommander.Satelliteconfig_SaveList( self.mOrgConfiguredList1 )
			
		if self.mOrgConfiguredList2 :
			self.mCommander.Satelliteconfig_SaveList( self.mOrgConfiguredList2 )


	def SetTunerTypeFlag( self, aSatellite, aType ) :
		if aType == E_DISEQC_1_0 :
			aSatellite.mMotorizedType = ElisEnum.E_MOTORIZED_OFF
			aSatellite.mIsOneCable = 0
			aSatellite.mMotorizedData = 0
			if aSatellite.mSlotNumber > 3 :
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
			
		elif aType == E_MOTORIZE_1_2 :
			aSatellite.mMotorizedType = ElisEnum.E_MOTORIZED_ON
			aSatellite.mIsOneCable = 0
			aSatellite.mMotorizedData = aSatellite.mSlotNumber + 1
			aSatellite.mIsConfigUsed = 1

		elif aType == E_MOTORIZE_USALS :
			aSatellite.mMotorizedType = ElisEnum.E_MOTORIZED_USALS
			aSatellite.mIsOneCable = 0
			aSatellite.mMotorizedData = 0
			aSatellite.mIsConfigUsed = 1
			
		elif aType == E_ONE_CABLE :
			aSatellite.mMotorizedType = ElisEnum.E_MOTORIZED_OFF
			aSatellite.mIsOneCable = 1
			aSatellite.mMotorizedData = 0
			aSatellite.mIsConfigUsed = 1


	def SatelliteSetFlag( self, aSatelliteList, aTunerType ) :
		if aSatelliteList :
			for i in range( len( aSatelliteList ) ) :
				aSatelliteList[i].mSlotNumber = i
				self.SetTunerTypeFlag( aSatelliteList[i], aTunerType )


	def SatelliteConfigSaveList( self ) :
		LOG_TRACE( 'Save Satellite Config List!' )
		self.mCommander.Satelliteconfig_DeleteAll( ) 
		tuner1Type = ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( )
		#self.mConfiguredList1 = self.GetConfiguredSatellitebyTunerIndex( E_TUNER_1 )
		if self.mConfiguredList1 :
			self.SatelliteSetFlag( self.mConfiguredList1, tuner1Type )

		if self.GetCurrentTunerConfigType( ) == E_SAMEWITH_TUNER :
			self.mConfiguredList2 = deepcopy( self.mConfiguredList1 )
			if self.mConfiguredList2 :
				for i in range( len( self.mConfiguredList2 ) ) :
					self.mConfiguredList2[i].mTunerIndex = E_TUNER_2

		else :
			tuner2Type = ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).GetProp( )
			#configuredList2 = self.GetConfiguredSatellitebyTunerIndex( E_TUNER_2 )
			if self.mConfiguredList2 :
				self.SatelliteSetFlag( self.mConfiguredList2, tuner2Type )

		ret1 = False
		ret2 = False
		if self.mConfiguredList1 :
			ret1 = self.mCommander.Satelliteconfig_SaveList( self.mConfiguredList1 )
		if self.mConfiguredList2 :
			ret2 = self.mCommander.Satelliteconfig_SaveList( self.mConfiguredList2 )


		if self.mConfiguredList1 and ret1 :
			for satellite in self.mConfiguredList1 :
				satellite.printdebug( )
		if self.mConfiguredList2 and ret2 :
			for satellite in self.mConfiguredList2 :
				satellite.printdebug( )


	def Load( self ) :
		print 'dhkim test Start Tuner Load!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
		# Get All Satellite List ( mLongitude, mBand, mName )
		self.mAllSatelliteList = self.mDataCache.GetAllSatelliteList( )
		
		# Get Configured Satellite List Tuner 1
		self.mConfiguredList1 = deepcopy( self.mDataCache.GetConfiguredSatelliteListByTunerIndex( E_TUNER_1 ) )

		# Get Configured Satellite List Tuner 2
		self.mConfiguredList2 = deepcopy( self.mDataCache.GetConfiguredSatelliteListByTunerIndex( E_TUNER_2 ) )

		self.mDiseqc10List1			= deepcopy( self.mConfiguredList1 )
		self.SatelliteSetFlag( self.mDiseqc10List1, E_DISEQC_1_0 )
		self.mDiseqc10List2			= deepcopy( self.mConfiguredList2 )
		self.SatelliteSetFlag( self.mDiseqc10List2, E_DISEQC_1_0 )
		self.mDiseqc11List1			= deepcopy( self.mConfiguredList1 )
		self.SatelliteSetFlag( self.mDiseqc11List1, E_DISEQC_1_1 )
		self.mDiseqc11List2			= deepcopy( self.mConfiguredList2 )
		self.SatelliteSetFlag( self.mDiseqc11List2, E_DISEQC_1_1 )
		self.mMotorizeList1			= deepcopy( self.mConfiguredList1 )
		self.SatelliteSetFlag( self.mMotorizeList1, E_MOTORIZE_1_2 )
		self.mMotorizeList2			= deepcopy( self.mConfiguredList2 )
		self.SatelliteSetFlag( self.mMotorizeList2, E_MOTORIZE_1_2 )
		self.mMotorizeUsalsList1	= deepcopy( self.mConfiguredList1 )
		self.SatelliteSetFlag( self.mMotorizeUsalsList1, E_MOTORIZE_USALS )
		self.mMotorizeUsalsList2	= deepcopy( self.mConfiguredList2 )
		self.SatelliteSetFlag( self.mMotorizeUsalsList2, E_MOTORIZE_USALS )

		self.mOneCableList1			= []
		self.mOneCableList2			= []
		
		if self.mConfiguredList1 :
			self.mOneCableList1 = deepcopy( self.mConfiguredList1 )
			if len( self.mOneCableList1 ) > MAX_SATELLITE_CNT_ONECABLE :
				self.mOneCableList1 = self.mOneCableList1[0:2]
		else :
			self.mOneCableList1.append( self.GetDefaultConfig( ) )
		self.SatelliteSetFlag( self.mOneCableList1, E_ONE_CABLE )

		if self.mConfiguredList2 :
			self.mOneCableList2 = deepcopy( self.mConfiguredList2 )
			if len( self.mOneCableList2 ) > MAX_SATELLITE_CNT_ONECABLE :
				self.mOneCableList2 = self.mOneCableList2[0:2]
		else :
			self.mOneCableList2.append( self.GetDefaultConfig( ) )
		self.SatelliteSetFlag( self.mOneCableList2, E_ONE_CABLE )

		self.mSimpleLnbList1		= []
		self.mSimpleLnbList2		= []
		if self.mConfiguredList1 :
			self.mSimpleLnbList1.append( self.mConfiguredList1[0] )
		else :
			self.mSimpleLnbList1.append( self.GetDefaultConfig( ) )
		self.SatelliteSetFlag( self.mSimpleLnbList1, E_SIMPLE_LNB )

		if self.mConfiguredList2 :
			self.mSimpleLnbList2.append( self.mConfiguredList2[0] )
		else :
			self.mSimpleLnbList2.append( self.GetDefaultConfig( ) )
		self.SatelliteSetFlag( self.mSimpleLnbList2, E_SIMPLE_LNB )

		self.SelectCurrentSatelliteList( E_TUNER_1, ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( ) )
		self.SelectCurrentSatelliteList( E_TUNER_2, ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).GetProp( ) )

		self.mOrgConfiguredList1 = deepcopy( self.mConfiguredList1 )
		self.mOrgConfiguredList2 = deepcopy( self.mConfiguredList2 )

		if self.mConfiguredList1 :
			print 'dhkim test loaded tuner current list!!!!!!!!!!!!!!!!!!'
			for satellite in self.mConfiguredList1 :
				satellite.printdebug( )

		if self.mConfiguredList2 :
			print 'dhkim test loaded tuner current list!!!!!!!!!!!!!!!!!!'
			for satellite in self.mConfiguredList2 :
				satellite.printdebug( )
		print 'dhkim test End Tuner Load!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'


	def SelectCurrentSatelliteList( self, aTunerNumber, aTunerType ) :
		if aTunerNumber == E_TUNER_1 :
			if aTunerType == E_DISEQC_1_0 :
				self.mConfiguredList1 = self.mDiseqc10List1
			elif aTunerType == E_DISEQC_1_1 :
				self.mConfiguredList1 = self.mDiseqc11List1
			elif aTunerType == E_MOTORIZE_1_2 :
				self.mConfiguredList1 = self.mMotorizeList1
			elif aTunerType == E_MOTORIZE_USALS :
				self.mConfiguredList1 = self.mMotorizeUsalsList1
			elif aTunerType == E_ONE_CABLE :
				self.mConfiguredList1 = self.mOneCableList1
			elif aTunerType == E_SIMPLE_LNB :
				self.mConfiguredList1 = self.mSimpleLnbList1
		elif aTunerNumber == E_TUNER_2 :
			if aTunerType == E_DISEQC_1_0 :
				self.mConfiguredList2 = self.mDiseqc10List2
			elif aTunerType == E_DISEQC_1_1 :
				self.mConfiguredList2 = self.mDiseqc11List2
			elif aTunerType == E_MOTORIZE_1_2 :
				self.mConfiguredList2 = self.mMotorizeList2
			elif aTunerType == E_MOTORIZE_USALS :
				self.mConfiguredList2 = self.mMotorizeUsalsList2
			elif aTunerType == E_ONE_CABLE :
				self.mConfiguredList2 = self.mOneCableList2
			elif aTunerType == E_SIMPLE_LNB :
				self.mConfiguredList2 = self.mSimpleLnbList2
		else :
			LOG_ERR( 'Invalid Tuner Number : %s' % aTunerNumber )


	def LoadOriginalSatelliteConfigListByTunerNumber( self, aTunerNumber ) :
		if aTunerNumber == E_TUNER_1 :
			return self.mOrgConfiguredList1
		elif aTunerNumber == E_TUNER_2 :
			return self.mOrgConfiguredList2
		else :
			LOG_ERR( 'Invalid Tuner Number : %s' % aTunerNumber )
			return self.mOrgConfiguredList1


	def LoadOriginalTunerConfig( self ) :
		# Tuner
		self.mOrgTuner2ConnectType = ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander ).GetProp( )
		self.mOrgTuner2Config = ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander ).GetProp( )
		self.mOrgTuner1Type = ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( )
		self.mOrgTuner2Type = ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).GetProp( )

		# Onecable
		self.mOrgMDU			= ElisPropertyEnum( 'MDU', self.mCommander).GetProp( )
		self.mOrgTuner1PinCode	= ElisPropertyInt( 'Tuner1 Pin Code', self.mCommander ).GetProp( )
		self.mOrgTuner2PinCode	= ElisPropertyInt( 'Tuner2 Pin Code', self.mCommander ).GetProp( )
		self.mOrgTuner1SCR		= ElisPropertyInt( 'Tuner1 SCR', self.mCommander ).GetProp( )
		self.mOrgTuner2SCR		= ElisPropertyInt( 'Tuner2 SCR', self.mCommander ).GetProp( )
		self.mOrgTuner1SCRFreq	= ElisPropertyInt( 'Tuner1 SCR Frequency', self.mCommander ).GetProp( )
		self.mOrgTuner2SCRFreq	= ElisPropertyInt( 'Tuner2 SCR Frequency', self.mCommander ).GetProp( )

		# Motorized
		self.mOrgMyLongitude	= ElisPropertyInt( 'MyLongitude', self.mCommander ).GetProp( )
		self.mOrgMyLatitude		= ElisPropertyInt( 'MyLatitude', self.mCommander ).GetProp( )

		self.mOriginalTunerConfig = []
		self.mOriginalTunerConfig.append( self.mOrgTuner2ConnectType )
		self.mOriginalTunerConfig.append( self.mOrgTuner2Config )
		self.mOriginalTunerConfig.append( self.mOrgTuner1Type )
		self.mOriginalTunerConfig.append( self.mOrgTuner2Type )
		self.mOriginalTunerConfig.append( self.mOrgMDU )
		self.mOriginalTunerConfig.append( self.mOrgTuner1PinCode )
		self.mOriginalTunerConfig.append( self.mOrgTuner2PinCode )
		self.mOriginalTunerConfig.append( self.mOrgTuner1SCR )
		self.mOriginalTunerConfig.append( self.mOrgTuner2SCR )
		self.mOriginalTunerConfig.append( self.mOrgTuner1SCRFreq )
		self.mOriginalTunerConfig.append( self.mOrgTuner2SCRFreq )
		self.mOriginalTunerConfig.append( self.mOrgMyLongitude )
		self.mOriginalTunerConfig.append( self.mOrgMyLatitude )


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


	def GetOriginalTunerConfig( self ) :
		return self.mOriginalTunerConfig
		

	def GetDefaultConfig( self ) :
		config = ElisISatelliteConfig( )
		config.reset( )
		config.mSatelliteLongitude = self.mAllSatelliteList[0].mLongitude
		config.mBandType = self.mAllSatelliteList[0].mBand
		config.mIsConfigUsed = 1
		config.mLowLNB = 9750
		config.mHighLNB = 10600
		config.mLNBThreshold = 11700
		return config


	def SetNeedLoad( self, aNeedLoad ) :
		self.mNeedLoad = aNeedLoad


	def GetNeedLoad( self ) :
		return self.mNeedLoad


	def SetFristInstallation( self, aEnable ) :
		self.mFirstInstallation = aEnable


	def GetFristInstallation( self ) :
		return self.mFirstInstallation


