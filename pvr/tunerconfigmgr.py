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

from elisaction import ElisAction
from elisenum import ElisEnum


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
		self.configuredList = []
		self.configuredSatelliteList = []
		self.currentTuner = 0
		self.currentLongitude = 0
		self.currentTunerType = 0

	def getCurrentTunerIndex( self ) :
		return self.currentTuner

	def setCurrentTunerIndex( self, currentTuner) :
		self.currentTuner = currentTuner


	def getCurrentConfiguredSatellite( self ) :
		for config in self.configuredList :
			if int( config[0] ) == self.currentTuner and int( config[2] ) == self.currentLongitude :
				return config

		return None

	def setCurrentTunerType( self, tunerType ) :
		self.currentTunerType = tunerType


	def getCurrentTunerType( self ) :
		return self.currentTunerType


	def setCurrentLongitue( self, longitude ) :
		self.currentLongitude = longitude
		

	def getCurrentLongitue( self ) :
		return self.currentLongitude

	def getConfiguredSatellite( self ) :
		return self.configuredList


	def reset( self ) :

		self.currentTuner  = 0
		self.currentLongitude  = 0
		self.currentTunerType = 0


	def load( self ) :
	
		"""
			[TunerIndex, SlotNumber, SatelliteLongitude, BandType, FrequencyLevel, DisEqc11, DisEqcMode, DisEqcRepeat,
				IsConfigUsed, LnbType, MotorizedType, LowLNB, HighLNB, LNBThreshold, MotorizedData,
				IsOneCable, OneCablePin, OneCableMDU, OneCableLoFreq1, OneCableLoFreq2, OneCableUBSlot, OneCableUBFreq]	
		"""
		self.configuredList = []
		self.configuredList = self.commander.satelliteconfig_GetList( self.currentTuner )		

		"""
			[Longitude, Band, Name]
		"""
		self.configuredSatelliteList = []
		self.configuredSatelliteList = self.commander.satellite_GetConfiguredList( ElisEnum.SATELLITE_BY_LONGITUDE)		
	

	def getFormattedName( self, longitude ) :
	
		found = False	

		for satellite in self.configuredSatelliteList :
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
		satellitelist = []
		formattedlist = []
		satellitelist = self.commander.satellite_GetList( ElisEnum.E_SORT_INSERTED)
		for satellite in satellitelist :
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

		for satellite in self.configuredSatelliteList :
			if longitude == int( satellite[0] ) :
				found = True
				break

		if found == True :
			tmptransponderList = self.commander.transponder_GetList( int( satellite[0] ), int( satellite[1] ) )

		for i in range( len( tmptransponderList ) ) :
			transponderList.append( '%s' % ( i + 1 ) + ' ' + tmptransponderList[i][0] + ' MHz / ' + tmptransponderList[i][1] + ' KS/s' )
		return transponderList
		
