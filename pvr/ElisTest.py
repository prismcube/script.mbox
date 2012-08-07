

from ElisProperty import ElisPropertyEnum, ElisPropertyInt
import pvr.ElisMgr
from ElisAction import ElisAction
from ElisEnum import ElisEnum


class ElisTest( object ) :
	def __init__( self ) :
		self.mCommander = pvr.ElisMgr.GetInstance().getCommander( )


	def testAll( self ) :
		#self.testPropEnum()
		#self.testPropInt()
		#self.testSatelliteconfig_DeleteAll()
		#self.testSatelliteConfigSaveList()
		#self.testChannelScanBySatellite()
		#self.testChannelScanByCarriers()
		#self.testChannellistByZapping()
		pass


	def testPropEnum( self ) :
		prop = ElisPropertyEnum( 'Last ServiceType', self.mCommander )
		print 'prop test %s' %prop.getProp( )
		print 'prop test (TV): %s' %prop.getPropStringByIndex( 0 )
		print 'prop test (Radio): %s' %prop.getPropStringByIndex( 1 )		
		print 'prop test (Last ServiceType): %s' %prop.getName( )
		print 'prop test (TV or Radio): %s' %prop.getPropString( )
		prop.SetProp( 2 )
		print 'prop test 2 Radio : %d %s' %( prop.getProp( ), prop.getPropString( ) )
		prop.SetPropIndex( 0 )
		print 'prop test 1 TV : %d %s' %( prop.getProp( ), prop.getPropString( ) )
		prop.SetPropString( 'Radio' )
		print 'prop test 2 Radio : %d %s' %( prop.getProp( ), prop.getPropString( ) )


	def testPropInt( self ) :
		"""
		propInt = ElisPropertyInt( 'Audio Volume', self.mCommander  )
		print 'propint test =%d' %propInt.getProp( )
		propInt.SetProp( 30 )
		print 'propint test =%d' %propInt.getProp( )
		"""


	def testChannelScanBySatellite( self ) :
		self.mCommander.channelscan_BySatellite( 192, ElisEnum.E_BAND_KU )


	def testChannelScanByCarriers( self ) :
		prop = ElisPropertyEnum( 'Channel Search Mode', self.mCommander )
		prop.SetProp( 0 )
		carriers = [[11303,22000,ElisEnum.E_LNB_HORIZONTAL,ElisEnum.E_DVBS2_8PSK_2_3, 0, 0, 0 ] ]
		self.mCommander.channelscan_ByCarriers( 192, ElisEnum.E_BAND_KU, carriers )


	def testSatelliteconfig_DeleteAll( self ) :
		self.mCommander.satelliteconfig_DeleteAll( )


	#ConfiguredSatellite : [TunerIndex, SlotNumber, SatelliteLongitude, BandType, FrequencyLevel, DisEqc11, DisEqcMode, DisEqcRepeat,
	#				   IsConfigUsed, LnbType, MotorizedType, LowLNB, HighLNB, LNBThreshold, MotorizedData,
	#				   IsOneCable, OneCablePin, OneCableMDU, OneCableLoFreq1, OneCableLoFreq2, OneCableUBSlot, OneCableUBFreq]
	def testSatelliteConfigSaveList( self ) :
		configuredList = [[0,1,130,ElisEnum.E_BAND_KU,0,ElisEnum.E_SWITCH_DISABLED,ElisEnum.E_SWITCH_2OF4,0,
						1, ElisEnum.E_LNB_UNIVERSAL,0,9750,10600,11700,0,
						0,0,0,0,0,0,0],
						[1,1,130,ElisEnum.E_BAND_KU,0,ElisEnum.E_SWITCH_DISABLED,ElisEnum.E_SWITCH_2OF4,0,
						1, ElisEnum.E_LNB_UNIVERSAL,0,9750,10600,11700,0,
						0,0,0,0,0,0,0]]
		print 'config=%s' %configuredList
		self.mCommander.satelliteconfig_SaveList( configuredList )


	def testChannellistByZapping( self ) :
		chlist = self.mCommander.channel_GetList( ElisEnum.E_TYPE_TV, ElisEnum.E_MODE_ALL, ElisEnum.E_SORT_BY_DEFAULT )
		print 'chlist[%s]'% chlist
	

