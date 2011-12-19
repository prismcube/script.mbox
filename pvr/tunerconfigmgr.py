import xbmc
import xbmcgui
import sys
import time


E_CONFIGURE_SATELLITE_TUNER_INDEX 		= 0
E_CONFIGURE_SATELLITE_SLOT_NUMBER		= 1
E_CONFIGURE_SATELLITE_LONGITUDE			= 2
E_CONFIGURE_SATELLITE_BANDTYPE			= 3
E_CONFIGURE_SATELLITE_FREQUENCY_LEVEL	= 4
E_CONFIGURE_SATELLITE_DISEQC_11			= 5
E_CONFIGURE_SATELLITE_DISEQC_MODE		= 6
E_CONFIGURE_SATELLITE_DISEQC_REPEAT		= 7
E_CONFIGURE_SATELLITE_IS_CONFIG_USED	= 8
E_CONFIGURE_SATELLITE_LNB_TYPE			= 9
E_CONFIGURE_SATELLITE_MOTORIZED_TYPE	= 10
E_CONFIGURE_SATELLITE_LOW_LNB			= 11
E_CONFIGURE_SATELLITE_HIGH_LNB			= 12
E_CONFIGURE_SATELLITE_LNB_THRESHOLD		= 13
E_CONFIGURE_SATELLITE_MOTORIZED_DATA	= 14
E_CONFIGURE_SATELLITE_IS_ONECABLE		= 15
E_CONFIGURE_SATELLITE_ONECABLE_PIN		= 16
E_CONFIGURE_SATELLITE_ONECABLE_MDU		= 17
E_CONFIGURE_SATELLITE_ONECABLE_LO_FREQ1 = 18
E_CONFIGURE_SATELLITE_ONECABLE_LO_FREQ2 = 19
E_CONFIGURE_SATELLITE_ONECABLE_UBSLOT	= 20
E_CONFIGURE_SATELLITE_ONECABLE_UBFREQ	= 21

#TUNER TYPE
E_SIMPLE_LNB					= 0
E_DISEQC_1_0					= 1
E_DISEQC_1_1					= 2
E_MOTORIZED_1_2					= 3
E_MOTORIZED_USALS				= 4
E_ONE_CABLE						= 5

#TUNER CONNECTION TYPE
E_TUNER_SEPARATED				= 0
E_TUNER_LOOPTHROUGH				= 1

#TUNER CONFIG TYPE
E_SAMEWITH_TUNER				= 0
E_DIFFERENT_TUNER				= 1


#TUNER
E_TUNER_1						= 0
E_TUNER_2						= 1
E_TUNER_MAX						= 2

from elisaction import ElisAction
from elisenum import ElisEnum
import pvr.elismgr
from elisproperty import ElisPropertyEnum


gTunerConfigMgr = None

def getInstance():
	global gTunerConfigMgr
	if not gTunerConfigMgr:
		print 'lael98 check create instance'
		gTunerConfigMgr = TunerConfigMgr()
	else:
		print 'lael98 check already TunerConfigMgr is created'

	return gTunerConfigMgr


class TunerConfigMgr( object ):
	def __init__( self ):
		self.commander = pvr.elismgr.getInstance( ).getCommander( )	
		self.configuredList1 = []
		self.configuredList2 = []		
		self.currentTuner = 0
		self.currentConfigIndex = 0
		self.currentTunerType = 0
		self.connectionType = 0
		self.configType = 0
		self.needLoad = False

		self.orgTuner2ConnectType = 0
		self.orgTuner2Config = 0
		self.orgTuner1Tupe = 0
		self.orgTuner2Type = 0
		
		self.allsatellitelist = []

	def getCurrentTunerIndex( self ) :
		return self.currentTuner


	def setCurrentTunerIndex( self, currentTuner) :
		self.currentTuner = currentTuner


	def getCurrentConfiguredSatellite( self ) :

		if self.currentTuner == E_TUNER_1 :	
			return self.configuredList1[self.currentConfigIndex]
		elif self.currentTuner == E_TUNER_2:
			return self.configuredList2[self.currentConfigIndex]		
		else :
			print 'ERROR : can not find configured satellite'
	
		return None

	def setCurrentTunerType( self, tunerType ) :
		self.currentTunerType = tunerType


	def getCurrentTunerType( self ) :
		return self.currentTunerType

	def setCurrentTunerConnectionType( self, connectionType ) :
		self.connectionType = connectionType

	def getCurrentTunerConnectionType( self ) :
		return self.connectionType

	def setCurrentTunerConfigType( self, configType ) :
		self.configType = configType

	def getCurrentTunerConfigType( self ) :
		return self.configType

	def setCurrentConfigIndex( self, currentConfigIndex ) :
		self.currentConfigIndex = currentConfigIndex
		
	def getCurrentConfigIndex( self ) :
		return self.currentConfigIndex



	def getConfiguredSatelliteList( self ) :
		if self.currentTuner == E_TUNER_1 :
			return self.configuredList1
		elif self.currentTuner == E_TUNER_2 :
			return self.configuredList2
		else :
			print 'ERROR : unknown tuner'
			return self.configuredList1

	def addConfiguredSatellite( self, index ) :

		config = ["0", "0", self.allsatellitelist[index][0], self.allsatellitelist[index][1], "0", "0", "0", "0",
				  "1", "0", "0", "9750", "10600", "11700", "0", "0", "0", "0", "0", "0", "0", "0" ]


		if self.getCurrentTunerConfigType( ) == E_SAMEWITH_TUNER :
			self.configuredList1.append( config )
		
		elif self.getCurrentTunerConfigType( ) == E_DIFFERENT_TUNER :

			if self.getCurrentTunerIndex( ) == E_TUNER_1 :
				self.configuredList1.append( config )

			elif self.getCurrentTunerIndex( ) == E_TUNER_2 :
				self.configuredList2.append( config )

		
	def reset( self ) :

		self.currentTuner  = 0
		self.currentConfigIndex  = 0
		self.currentTunerType = 0

	def restore( self ) :

		property = ElisPropertyEnum( 'Tuner2 Connect Type', self.commander )
		property.setPropIndex( self.orgTuner2ConnectType )
		property = ElisPropertyEnum( 'Tuner2 Signal Config', self.commander )
		property.setPropIndex( self.orgTuner2Config )
		property = ElisPropertyEnum( 'Tuner1 Type' )
		property.setPropIndex( self.orgTuner1Type )
		property = ElisPropertyEnum( 'Tuner2 Type' )		
		property.setPropIndex( self.orgTuner2Type )


		print '#################### After Retore ###############################'
		self.loadOriginalTunerConfig()
		print '###########################################################'
		
	def save( self ) :
		pass

	def load( self ) :
	
		"""
			[TunerIndex, SlotNumber, SatelliteLongitude, BandType, FrequencyLevel, DisEqc11, DisEqcMode, DisEqcRepeat,
				IsConfigUsed, LnbType, MotorizedType, LowLNB, HighLNB, LNBThreshold, MotorizedData,
				IsOneCable, OneCablePin, OneCableMDU, OneCableLoFreq1, OneCableLoFreq2, OneCableUBSlot, OneCableUBFreq]	
		"""
		self.configuredList1 = []
		self.configuredList1 = self.commander.satelliteconfig_GetList( E_TUNER_1 )		

		self.configuredList2 = []
		self.configuredList2 = self.commander.satelliteconfig_GetList( E_TUNER_2 )		

		"""
			[Longitude, Band, Name]
		"""
		#self.configuredSatelliteList = []
		#self.configuredSatelliteList = self.commander.satellite_GetConfiguredList( ElisEnum.E_SORT_LONGITUDE )		

		self.allsatellitelist = []
		self.allsatellitelist = self.commander.satellite_GetList( ElisEnum.E_SORT_INSERTED )
	

	def getFormattedName( self, longitude ) :
	
		found = False	

		for satellite in self.allsatellitelist :
			if longitude == int( satellite[0] ) :
				found = True
				break

		if found == True :
			dir = 'E'

			tmpLongitude  = longitude
			if tmpLongitude > 1800 :
				dir = 'W'
				tmpLongitude = 3600 - longitude

			formattedName = '%d.%d %s %s' %( int( tmpLongitude/10 ), tmpLongitude%10, dir, satellite[2] )
			return formattedName

		return 'UnKnown'

	def getFormattedNameList( self ) :
		formattedlist = []	
		for satellite in self.allsatellitelist :
			dir = 'E'

			tmpLongitude  = int( satellite[0] )
			if tmpLongitude > 1800 :
				dir = 'W'
				tmpLongitude = 3600 - int( satellite[0] )

			formattedName = '%d.%d %s %s' %( int( tmpLongitude/10 ), tmpLongitude%10, dir, satellite[2] )
			formattedlist.append( formattedName )

		return formattedlist

	def getTransponderList( self, longitude ) :
		tmptransponderList = []
		transponderList = []
		found = False	

		for satellite in self.allsatellitelist :
			if longitude == int( satellite[0] ) :
				found = True
				break

		if found == True :
			tmptransponderList = self.commander.transponder_GetList( int( satellite[0] ), int( satellite[1] ) )

		for i in range( len( tmptransponderList ) ) :
			transponderList.append( '%s' % ( i + 1 ) + ' ' + tmptransponderList[i][0] + ' MHz / ' + tmptransponderList[i][1] + ' KS/s' )
		return transponderList


	def getSatelliteByIndex( self, index ) :
		return self.allsatellitelist[index]

	def loadOriginalTunerConfig( self ) :

		property = ElisPropertyEnum( 'Tuner2 Connect Type', self.commander )
		self.orgTuner2ConnectType = property.getPropIndex()
		property = ElisPropertyEnum( 'Tuner2 Signal Config', self.commander )
		self.orgTuner2Config = property.getPropIndex()
		property = ElisPropertyEnum( 'Tuner1 Type' )
		self.orgTuner1Type = property.getPropIndex()
		property = ElisPropertyEnum( 'Tuner2 Type' )		
		self.orgTuner2Type = property.getPropIndex()


		print 'tuner2ConnectType=%d' %self.orgTuner2ConnectType
		print 'self.tuner2Config=%d' %self.orgTuner2Config
		print 'self.tuner1Type=%d' %self.orgTuner1Type
		print 'self.tuner2Type=%d' %self.orgTuner2Type



		"""
			[TunerIndex, SlotNumber, SatelliteLongitude, BandType, FrequencyLevel, DisEqc11, DisEqcMode, DisEqcRepeat,
				IsConfigUsed, LnbType, MotorizedType, LowLNB, HighLNB, LNBThreshold, MotorizedData,
				IsOneCable, OneCablePin, OneCableMDU, OneCableLoFreq1, OneCableLoFreq2, OneCableUBSlot, OneCableUBFreq]	
		"""

	def saveCurrentConfig( self, configuredSatellite ) :
		if self.currentTuner == E_TUNER_1 :	
			self.configuredList1[self.currentConfigIndex] = configuredSatellite
			print 'dhkim test saveCurrentConfig = %s' % self.configuredList1[self.currentConfigIndex]
		elif self.currentTuner == E_TUNER_2:
			self.configuredList2[self.currentConfigIndex] = configuredSatellite
		else :
			print 'ERROR : can not find configured satellite'
	

	def setNeedLoad( self, needLoad ) :
		self.needLoad = needLoad

	def getNeedLoad( self ) :
		return self.needLoad

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

