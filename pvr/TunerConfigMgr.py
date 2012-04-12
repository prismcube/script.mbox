import xbmc
import xbmcgui
import sys
import time
from copy import deepcopy

from ElisAction import ElisAction
from ElisEnum import ElisEnum
import pvr.DataCacheMgr
import pvr.ElisMgr
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
from ElisClass import *
from pvr.gui.GuiConfig import *
from pvr.Util import LOG_WARN, LOG_TRACE, LOG_ERR

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
		self.mConfiguredList1 = []
		self.mConfiguredList2 = []		
		self.mCurrentTuner = 0
		self.mCurrentConfigIndex = 0
		self.mCurrentTunerType = 0
		self.mNeedLoad = False

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
			print 'ERROR : can not find configured satellite'
	
		return None


	def GetConfiguredSatellitebyIndex( self, aSatelliteIndex ) :
		if self.mCurrentTuner == E_TUNER_1 :	
			return self.mConfiguredList1[ aSatelliteIndex ]

		elif self.mCurrentTuner == E_TUNER_2:
			return self.mConfiguredList2[ aSatelliteIndex ]		

		else :
			print 'ERROR : can not find configured satellite'
	
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

	
	def GetConfiguredSatelliteList( self ) :
		if self.mCurrentTuner == E_TUNER_1 :
			return self.mConfiguredList1

		elif self.mCurrentTuner == E_TUNER_2 :
			return self.mConfiguredList2

		else :
			print 'ERROR : unknown tuner'
			return self.mConfiguredList1


	def GetConfiguredSatellitebyTunerIndex( self, aTunerIndex ) :
		if aTunerIndex == E_TUNER_1 :
			return self.mConfiguredList1

		elif aTunerIndex == E_TUNER_2 :
			return self.mConfiguredList2

		else :
			print 'ERROR : unknown tuner'
			return self.mConfiguredList1
			

	def SetOnecableSatelliteCount( self, aCount ) :
		self.mOnecableSatelliteCount = aCount


	def GetOneCableSatelliteCount( self ) :
		return self.mOnecableSatelliteCount
			

	def AddConfiguredSatellite( self, aIndex ) :
		config = self.GetDefaultConfig( )
		config.mSatelliteLongitude = self.mAllSatelliteList[ aIndex ].mLongitude
		config.mBandType = self.mAllSatelliteList[ aIndex ].mBand

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


	def SetTunerTypeFlag( self, aSatellite, aType ) :
		if aType == E_SIMPLE_LNB or aType == E_DISEQC_1_0 or aType == E_DISEQC_1_1 :
			aSatellite.mMotorizedType = ElisEnum.E_MOTORIZED_OFF
			aSatellite.mIsOneCable = 0
			aSatellite.mMotorizedData = 0
			
		elif aType == E_MOTORIZE_1_2 :
			aSatellite.mMotorizedType = ElisEnum.E_MOTORIZED_ON
			aSatellite.mIsOneCable = 0


		elif aType == E_MOTORIZE_USALS :
			aSatellite.mMotorizedType = ElisEnum.E_MOTORIZED_USALS
			aSatellite.mIsOneCable = 0
			aSatellite.mMotorizedData = 0
			
		elif aType == E_ONE_CABLE :
			aSatellite.mMotorizedType = ElisEnum.E_MOTORIZED_OFF
			aSatellite.mIsOneCable = 1
			aSatellite.mMotorizedData = 0


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


	def SatelliteConfigSaveList( self ) :
		self.mCommander.Satelliteconfig_DeleteAll( ) 
		
		tuner1Type = ElisPropertyEnum( 'Tuner1 Type', self.mCommander ).GetProp( )
		configuredList1 = self.GetConfiguredSatellitebyTunerIndex( E_TUNER_1 )
		for i in range( len( configuredList1 ) ) :
			configuredList1[i].mSlotNumber = i
			if tuner1Type == E_MOTORIZE_1_2 :
				configuredList1[i].mMotorizedData = configuredList1[i].mSlotNumber + 1
		
		if self.GetCurrentTunerConfigType( ) == E_SAMEWITH_TUNER and tuner1Type != E_ONE_CABLE :
			self.mConfiguredList2 = deepcopy( self.mConfiguredList1 )
			count = len ( self.mConfiguredList2 )
			for i in range( count ) :
				self.mConfiguredList2[i].mTunerIndex = E_TUNER_2

		else :
			tuner2Type = ElisPropertyEnum( 'Tuner2 Type', self.mCommander ).GetProp( )
			configuredList2 = self.GetConfiguredSatellitebyTunerIndex( E_TUNER_2 )
			for i in range( len( configuredList2 ) ) :
				configuredList2[i].mSlotNumber = i
				if tuner2Type == E_MOTORIZE_1_2 :
					configuredList2[i].mMotorizedData = configuredList2[i].mSlotNumber + 1

		ret1 = self.mCommander.Satelliteconfig_SaveList( self.mConfiguredList1 )
		ret2 = self.mCommander.Satelliteconfig_SaveList( self.mConfiguredList2 )
		"""
		for satellite in self.mConfiguredList1 :
			satellite.printdebug()
		for satellite in self.mConfiguredList2 :
			satellite.printdebug()
		"""
		if ret1 == True and ret2 == True :
			return True
		elif ret1 == False or ret2 == False :
			self.mCommander.Satelliteconfig_SaveList( self.mDataCache.Satellite_Get_ConfiguredList_By_TunerIndex( E_TUNER_1 ) )
			self.mCommander.Satelliteconfig_SaveList( self.mDataCache.Satellite_Get_ConfiguredList_By_TunerIndex( E_TUNER_2 ) )
			return False
			

	def Load( self ) :
		# Get All Satellite List ( mLongitude, mBand, mName )
		self.mAllSatelliteList = self.mDataCache.Satellite_Get_All_SatelliteList( )
		
		# Get Configured Satellite List Tuner 1
		self.mConfiguredList1 = deepcopy( self.mDataCache.Satellite_Get_ConfiguredList_By_TunerIndex( E_TUNER_1 ) )
		if self.mConfiguredList1 and self.mConfiguredList1[0].mError == 0 :
			pass
		else :	# If empty list to return, add one default satellite
			self.mConfiguredList1 = []
			config = self.GetDefaultConfig( )
			config.mSatelliteLongitude = self.mAllSatelliteList[ 0 ].mLongitude
			config.mBandType = self.mAllSatelliteList[ 0 ].mBand
			self.mConfiguredList1.append( config )
		
		# Get Configured Satellite List Tuner 2
		self.mConfiguredList2 = deepcopy( self.mDataCache.Satellite_Get_ConfiguredList_By_TunerIndex( E_TUNER_2 ) )
		if self.mConfiguredList2 and self.mConfiguredList2[0].mError == 0 :
			pass
		else :	# If empty list to return, add one default satellite
			self.mConfiguredList2 = []
			config = self.GetDefaultConfig( )
			config.mSatelliteLongitude = self.mAllSatelliteList[ 0 ].mLongitude
			config.mBandType = self.mAllSatelliteList[ 0 ].mBand
			self.mConfiguredList2.append( config )


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