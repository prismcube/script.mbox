import xbmc
import xbmcgui
import sys
import time
from copy import deepcopy


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

from ElisAction import ElisAction
from ElisEnum import ElisEnum
import pvr.ElisMgr
from ElisProperty import ElisPropertyEnum

gTunerConfigMgr = None

def GetInstance():
	global gTunerConfigMgr
	if not gTunerConfigMgr:
		print 'lael98 check create instance'
		gTunerConfigMgr = TunerConfigMgr()
	else:
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

	"""
	def setCurrentTunerType( self, tunerType ) :
		self.mCurrentTunerType = tunerType
	"""


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

		config = ["0", "0", self.mAllSatelliteList[aIndex][0], self.mAllSatelliteList[aIndex][1], "0", "0", "0", "0",
				  "1", "0", "0", "9750", "10600", "11700", "0", "0", "0", "0", "0", "0", "0", "1284" ]


		if self.GetCurrentTunerConfigType( ) == E_SAMEWITH_TUNER :
			self.mConfiguredList1.append( config )
		
		elif self.GetCurrentTunerConfigType( ) == E_DIFFERENT_TUNER :

			if self.GetCurrentTunerIndex( ) == E_TUNER_1 :
				self.mConfiguredList1.append( config )

			elif self.GetCurrentTunerIndex( ) == E_TUNER_2 :
				config [E_CONFIGURE_SATELLITE_TUNER_INDEX]= "1"
				self.mConfiguredList2.append( config )

		
	def Reset( self ) :

		self.mCurrentTuner  = 0
		self.mCurrentConfigIndex  = 0
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
				#configuredList[i][E_CONFIGURE_SATELLITE_MOTORIZED_TYPE] = 0
				configuredList[i][E_CONFIGURE_SATELLITE_IS_ONECABLE] = 0
				
			elif tunerType == E_MOTORIZED_1_2 or tunerType == E_MOTORIZED_USALS :
				#configuredList[i][E_CONFIGURE_SATELLITE_MOTORIZED_TYPE] = 0
				configuredList[i][E_CONFIGURE_SATELLITE_IS_ONECABLE] = 0
				
			elif tunerType == E_ONE_CABLE :
				#configuredList[i][E_CONFIGURE_SATELLITE_MOTORIZED_TYPE] = 0
				configuredList[i][E_CONFIGURE_SATELLITE_IS_ONECABLE] = 1
		
		
		if self.GetCurrentTunerConfigType( ) == E_SAMEWITH_TUNER and tunerType != E_ONE_CABLE:
		
			self.mConfiguredList2 = deepcopy( self.mConfiguredList1 )


			count = len ( self.mConfiguredList2 )
			for i in range( count ) :
				self.mConfiguredList2[i][0] = '%d' % E_TUNER_2


		count = len ( self.mConfiguredList1 )
		for i in range( count ) :
			self.mConfiguredList1[i][1] = '%d' % i
		

		count = len ( self.mConfiguredList2 )
		for i in range( count ) :
			self.mConfiguredList2[i][1] = '%d' % i


		print 'satelliteconfig 1 %s' %self.mConfiguredList1
		print 'satelliteconfig 2 %s' %self.mConfiguredList2

		
		self.mCommander.Satelliteconfig_SaveList( self.mConfiguredList1 )
		self.mCommander.Satelliteconfig_SaveList( self.mConfiguredList2 )


	def Load( self ) :

		"""
			[Longitude, Band, Name]
		"""
		self.mAllSatelliteList = []
		self.mAllSatelliteList = self.mCommander.Satellite_GetList( ElisEnum.E_SORT_INSERTED )

		print 'dhkim test Tuner Load = %s' % self.mAllSatelliteList.printdebug()
	
		self.mConfiguredList1 = []
		self.mConfiguredList1 = self.mCommander.Satelliteconfig_GetList( E_TUNER_1 )

		print 'configuredList1 len=%d' % len( self.mConfiguredList1 )

		if len( self.mConfiguredList1 ) == 0 or ( len( self.mConfiguredList1 ) == 1 and len( self.mConfiguredList1[0] ) == 0 ) :

			config = ["0", "0", self.mAllSatelliteList[0][0], self.mAllSatelliteList[0][1], "0", "0", "0", "0",
						"1", "0", "0", "9750", "10600", "11700", "0", "0", "0", "0", "0", "0", "0", "1284" ]

			self.mConfiguredList1.append( config )

		print 'configuredList1 =%s' % self.mConfiguredList1


		self.mConfiguredList2 = []
		self.mConfiguredList2 = self.mCommander.Satelliteconfig_GetList( E_TUNER_2 )		
		print 'configuredList2 len=%d' %len( self.mConfiguredList2 )		

		if len( self.mConfiguredList2 ) == 0 or ( len( self.mConfiguredList2 ) == 1 and len( self.mConfiguredList2[0] ) == 0 ) :
			config = ["1", "0", self.mAllSatelliteList[0][0], self.mAllSatelliteList[0][1], "0", "0", "0", "0",
					  "1", "0", "0", "9750", "10600", "11700", "0", "0", "0", "0", "0", "0", "0", "1284" ]
		
			self.mConfiguredList2.append( config )

		print 'configuredList2 =%s' % self.mConfiguredList2

	

	def GetFormattedName( self, aLongitude, aBand ) :
	
		found = False	

		for satellite in self.mAllSatelliteList :
			if aLongitude == int( satellite[0] ) and aBand == int( satellite[1] ) :
				found = True
				break

		if found == True :
			dir = 'E'

			tmpLongitude  = aLongitude
			if tmpLongitude > 1800 :
				dir = 'W'
				tmpLongitude = 3600 - aLongitude

			formattedName = '%d.%d %s %s' % ( int( tmpLongitude / 10 ), tmpLongitude % 10, dir, satellite[2] )
			return formattedName

		return 'UnKnown'

	def GetFormattedNameList( self ) :
		formattedlist = []	
		for satellite in self.mAllSatelliteList :
			dir = 'E'

			tmpLongitude  = int( satellite[0] )
			if tmpLongitude > 1800 :
				dir = 'W'
				tmpLongitude = 3600 - int( satellite[0] )

			formattedName = '%d.%d %s %s' %( int( tmpLongitude / 10 ), tmpLongitude % 10, dir, satellite[2] )
			formattedlist.append( formattedName )

		return formattedlist

	def GetTransponderList( self, aLongitude, aBand ) :
		tmptransponderList = []
		transponderList = []
		found = False	

		for satellite in self.mAllSatelliteList :
			if aLongitude == int( satellite[0] ) and aBand == int( satellite[1] ):
				found = True
				break

		if found == True :
			tmptransponderList = self.mCommander.Transponder_GetList( int( satellite[0] ), int( satellite[1] ) )

		for i in range( len( tmptransponderList ) ) :
			transponderList.append( '%s' % ( i + 1 ) + ' ' + tmptransponderList[i][0] + ' MHz / ' + tmptransponderList[i][1] + ' KS/s' )
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


		print 'tuner2ConnectType=%d' % self.mOrgTuner2ConnectType
		print 'self.tuner2Config=%d' % self.mOrgTuner2Config
		print 'self.tuner1Type=%d' % self.mOrgTuner1Type
		print 'self.tuner2Type=%d' % self.mOrgTuner2Type


	def SaveCurrentConfig( self, aConfiguredSatellite ) :
		if self.mCurrentTuner == E_TUNER_1 :	
			self.mConfiguredList1[self.mCurrentConfigIndex] = aConfiguredSatellite
		elif self.mCurrentTuner == E_TUNER_2:
			self.mConfiguredList2[self.mCurrentConfigIndex] = aConfiguredSatellite
		else :
			print 'ERROR : can not find configured satellite'
	
	def SaveConfigbyIndex( self, aTunerIndex, aSatelliteIndex, aConfiguredSatellite ) :
		if aTunerIndex == E_TUNER_1 :	
			self.mConfiguredList1[aSatelliteIndex] = aConfiguredSatellite
		elif aTunerIndex == E_TUNER_2:
			self.mConfiguredList2[aSatelliteIndex] = aConfiguredSatellite
		else :
			print 'ERROR : can not find configured satellite'


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
