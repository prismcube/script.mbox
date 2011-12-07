import xbmc
import xbmcgui
import sys
import time

import pvr.elismgr
from pvr.elisevent import ElisAction, ElisEnum



gTunerConfigMgr = None

def getInstance():
	global gTunerConfigMgr
	if not gTunerConfigMgr:
		print 'lael98 check create instance'
		gTunerConfigMgr = TunerConfigMgr()
	else:
		print 'lael98 check already TunerConfigMgr is created'

	return gTunerConfigMgr


class TunerConfigMgr(object):
	def __init__(self):
		self.commander = pvr.elismgr.getInstance().getCommander( )	
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
			if int( config[0] ) == self.currentTuneer and int( config[2] ) == self.currentLongitude :
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
		self.commander.satelliteconfig_GetList( self.currentTuner, self.configuredList  )		

		"""
			[Longitude, Band, Name]
		"""
		self.configuredSatelliteList = []
		self.commander.satellite_GetConfiguredList( ElisEnum.SATELLITE_BY_LONGITUDE, self.configuredSatelliteList  )		
	

	def getFormattedName( self, longitude ) :
	
		found = False	

		for satellite in self.configuredSatelliteList :
			print 'satellite name= %s' %satellite[2]
			if longitude == int( satellite[0] ) :  #satellite[0]=longitue
				found = True
				break

		if found == True :

			dir = 'E'

			tmpLongitude  = longitude
			if tmpLongitude > 1800 :
				dir = 'W'
				tmpLongitude = 3600 - longitude

			
			formattedName = '%d.%d %s %s' %( int( tmpLongitude/10 ), tmpLongitude%10, dir, satellite[2] )
			print 'formattedName = %s' %formattedName

			return formattedName

		return 'UnKnown'


