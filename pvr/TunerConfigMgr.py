import xbmc
import xbmcgui
import sys
import time
from copy import deepcopy

from ElisAction import ElisAction
from ElisEnum import ElisEnum
import pvr.ElisMgr
from ElisProperty import ElisPropertyEnum
from ElisClass import *

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
		
		self.mAllSatelliteList = []

		self.mOnecableSatelliteCount = 0


	def GetCurrentTunerIndex( self ) :
		return self.mCurrentTuner


	def SetCurrentTunerIndex( self, aCurrentTuner ) :
		self.mCurrentTuner = aCurrentTuner


	def GetCurrentConfiguredSatellite( self ) :

		if self.mCurrentTuner == E_TUNER_1 :	
			return self.mConfiguredList1[ self.mCurrentConfigIndex ]
			
		elif self.mCurrentTuner == E_TUNER_2:
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

		
	def Reset( self ) :
		self.mCurrentTuner  = 0
		self.mCurrentConfigIndex = 0
		self.mCurrentTunerType = 0
		self.mOnecableSatelliteCount = 0

	def Restore( self ) :
		property = ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander )
		property.SetProp( self.mOrgTuner2ConnectType )
		property = ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander )
		property.SetProp( self.mOrgTuner2Config )
		property = ElisPropertyEnum( 'Tuner1 Type', self.mCommander )
		property.SetProp( self.mOrgTuner1Type )
		property = ElisPropertyEnum( 'Tuner2 Type', self.mCommander )		
		property.SetProp( self.mOrgTuner2Type )

		# After Retore
		self.LoadOriginalTunerConfig()


	def SatelliteConfigSaveList( self ) :
		self.mCommander.Satelliteconfig_DeleteAll( )
		
		tunerType = self.GetCurrentTunerType( )
		configuredList = self.GetConfiguredSatelliteList( )
		for i in range( len( configuredList ) ) :
			if tunerType == E_SIMPLE_LNB or tunerType == E_DISEQC_1_0 or tunerType == E_DISEQC_1_1 :
				configuredList[i].mMotorizedType = 0
				configuredList[i].mIsOneCable = 0
				
			elif tunerType == E_MOTORIZED_1_2 :
				configuredList[i].mMotorizedType = 1
				configuredList[i].mIsOneCable = 0

			elif tunerType == E_MOTORIZED_USALS :
				configuredList[i].mMotorizedType = 2
				configuredList[i].mIsOneCable = 0
				
			elif tunerType == E_ONE_CABLE :
				configuredList[i].mMotorizedType = 0
				configuredList[i].mIsOneCable = 1
		
		
		if self.GetCurrentTunerConfigType( ) == E_SAMEWITH_TUNER and tunerType != E_ONE_CABLE:
		
			self.mConfiguredList2 = deepcopy( self.mConfiguredList1 )


			count = len ( self.mConfiguredList2 )
			for i in range( count ) :
				self.mConfiguredList2[i].mTunerIndex = E_TUNER_2


		count = len ( self.mConfiguredList1 )
		for i in range( count ) :
			self.mConfiguredList1[i].mSlotNumber = i
		

		count = len ( self.mConfiguredList2 )
		for i in range( count ) :
			self.mConfiguredList2[i].mSlotNumber = i

		""" FOR TEST """
		for satellite in self.mConfiguredList1 :
			satellite.printdebug()
		
		for satellite in self.mConfiguredList2 :
			satellite.printdebug()
		
		self.mCommander.Satelliteconfig_SaveList( self.mConfiguredList1 )
		self.mCommander.Satelliteconfig_SaveList( self.mConfiguredList2 )


	def Load( self ) :
		# Get All Satellite List ( mLongitude, mBand, mName )
		self.mAllSatelliteList = []
		self.mAllSatelliteList = self.mCommander.Satellite_GetList( ElisEnum.E_SORT_INSERTED )

		# Get Configured Satellite List Tuner 1
		self.mConfiguredList1 = []
		self.mConfiguredList1 = self.mCommander.Satelliteconfig_GetList( E_TUNER_1 )

		if len( self.mConfiguredList1 ) == 0 :		# If empty list to return, add one default satellite
			self.mConfiguredList1.append( self.GetDefaultConfig( ) )

		# Get Configured Satellite List Tuner 2
		self.mConfiguredList2 = []
		self.mConfiguredList2 = self.mCommander.Satelliteconfig_GetList( E_TUNER_2 )			

		if len( self.mConfiguredList2 ) == 0 :		# If empty list to return, add one default satellite
			self.mConfiguredList2.append( self.GetDefaultConfig( ) )
			

	def GetFormattedName( self, aLongitude, aBand ) :
	
		found = False	

		for satellite in self.mAllSatelliteList :
			if aLongitude == satellite.mLongitude and aBand == satellite.mBand :
				found = True
				break

		if found == True :
			dir = 'E'

			tmpLongitude  = aLongitude
			if tmpLongitude > 1800 :
				dir = 'W'
				tmpLongitude = 3600 - aLongitude

			formattedName = '%d.%d %s %s' % ( int( tmpLongitude / 10 ), tmpLongitude % 10, dir, satellite.mName )
			return formattedName

		return 'UnKnown'

	def GetFormattedNameList( self ) :
		formattedlist = []	
		for satellite in self.mAllSatelliteList :
			dir = 'E'

			tmpLongitude  = satellite.mLongitude
			if tmpLongitude > 1800 :
				dir = 'W'
				tmpLongitude = 3600 - satellite.mLongitude

			formattedName = '%d.%d %s %s' %( int( tmpLongitude / 10 ), tmpLongitude % 10, dir, satellite.mName )
			formattedlist.append( formattedName )

		return formattedlist

	def GetTransponderList( self, aLongitude, aBand ) :
		tmptransponderList = []
		transponderList = []
		found = False	
		for satellite in self.mAllSatelliteList :
			if aLongitude == satellite.mLongitude and aBand == satellite.mBand :
				found = True
				break

		if found == True :
			tmptransponderList = self.mCommander.Transponder_GetList( satellite.mLongitude, satellite.mBand )

		for i in range( len( tmptransponderList ) ) :
			transponderList.append( '%d %d MHz %d KS/s' % ( ( i + 1 ), tmptransponderList[i].mFrequency, tmptransponderList[i].mSymbolRate ) )
		return transponderList


	def GetSatelliteByIndex( self, aIndex ) :
		return self.mAllSatelliteList[ aIndex ]


	def LoadOriginalTunerConfig( self ) :
		property = ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander )
		self.mOrgTuner2ConnectType = property.GetProp()
		property = ElisPropertyEnum( 'Tuner2 Signal Config', self.mCommander )
		self.mOrgTuner2Config = property.GetProp()
		property = ElisPropertyEnum( 'Tuner1 Type', self.mCommander )
		self.mOrgTuner1Type = property.GetProp()
		property = ElisPropertyEnum( 'Tuner2 Type', self.mCommander )		
		self.mOrgTuner2Type = property.GetProp()


	def GetDefaultConfig( self ) :
		config = ElisISatelliteConfig( )
		config.reset( )
		config.mTunerIndex = 0
		config.mSlotNumber = 0
		config.mSatelliteLongitude = self.mAllSatelliteList[0].mLongitude
		config.mBandType = self.mAllSatelliteList[0].mBand
		config.mFrequencyLevel = 0
		config.mDisEqc11 = 0
		config.mDisEqcMode = 0
		config.mDisEqcRepeat = 0
		config.mIsConfigUsed = 1
		config.mLnbType = 0
		config.mMotorizedType = 0
		config.mLowLNB = 9750
		config.mHighLNB = 10600
		config.mLNBThreshold = 11700
		config.mMotorizedData = 0
		config.mIsOneCable = 0
		config.mOneCablePin = 0
		config.mOneCableMDU = 0
		config.mOneCableLoFreq1 = 0
		config.mOneCableLoFreq2 = 0
		config.mOneCableUBSlot = 0
		config.mOneCableUBFreq = 1284
		
		return config

	def SetNeedLoad( self, aNeedLoad ) :
		self.mNeedLoad = aNeedLoad

	def GetNeedLoad( self ) :
		return self.mNeedLoad

	def updateSimpleLNB( self ) :
		pass
	
	def updateDiseqc10( self ) :
		pass

	def updateDiseqc11( self ) :
		pass

	def updateMotorized12( self  )	 :
		pass

	def updateMotorizedUSALS( self ) :
		pass

	def updateOneCable( self ) :
		pass
