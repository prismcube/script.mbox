

from elisproperty import ElisPropertyEnum, ElisPropertyInt
import pvr.ElisMgr
from elisaction import ElisAction
from elisenum import ElisEnum
class ElisTest(object):
	def __init__(self):
		self.commander = pvr.ElisMgr.getInstance().getCommander()

	def testAll( self ):
		#self.testPropEnum()
		#self.testPropInt()
		#self.testSatelliteconfig_DeleteAll()
		#self.testSatelliteconfigSaveList()
		#self.testChannelScanBySatellite()
		#self.testChannelScanByCarriers()
		#self.testChannellistByZapping()
		pass

	def testPropEnum( self ):
		prop = ElisPropertyEnum( 'Last ServiceType', self.commander )
		print 'prop test %s' %prop.getProp()
		print 'prop test (TV): %s' %prop.getPropStringByIndex( 0 )
		print 'prop test (Radio): %s' %prop.getPropStringByIndex( 1 )		
		print 'prop test (Last ServiceType): %s' %prop.getName()
		print 'prop test (TV or Radio): %s' %prop.getPropString()
		prop.SetProp( 2 )
		print 'prop test 2 Radio : %d %s' %( prop.getProp(), prop.getPropString())
		prop.SetPropIndex( 0 )
		print 'prop test 1 TV : %d %s' %( prop.getProp(), prop.getPropString())
		prop.SetPropString( 'Radio' )
		print 'prop test 2 Radio : %d %s' %( prop.getProp(), prop.getPropString())


	def testPropInt( self ):
		"""
		propInt = ElisPropertyInt( 'Audio Volume', self.commander  )
		print 'propint test =%d' %propInt.getProp()
		propInt.SetProp( 30 )
		print 'propint test =%d' %propInt.getProp()
		"""

	def testChannelScanBySatellite( self ):
		self.commander.channelscan_BySatellite( 192, ElisEnum.E_BAND_KU )

	def testChannelScanByCarriers( self ):
		prop = ElisPropertyEnum( 'Channel Search Mode', self.commander )
		prop.SetProp( 0 )
		carriers = [[11303,22000,ElisEnum.E_LNB_HORIZONTAL,ElisEnum.E_DVBS2_8PSK_2_3, 0, 0, 0 ] ]
		self.commander.channelscan_ByCarriers( 192, ElisEnum.E_BAND_KU, carriers )

	def testSatelliteconfig_DeleteAll( self ):
		self.commander.satelliteconfig_DeleteAll()

	#ConfiguredSatellite : [TunerIndex, SlotNumber, SatelliteLongitude, BandType, FrequencyLevel, DisEqc11, DisEqcMode, DisEqcRepeat,
	#				   IsConfigUsed, LnbType, MotorizedType, LowLNB, HighLNB, LNBThreshold, MotorizedData,
	#				   IsOneCable, OneCablePin, OneCableMDU, OneCableLoFreq1, OneCableLoFreq2, OneCableUBSlot, OneCableUBFreq]
	def testSatelliteconfigSaveList( self ) :
		configuredList = [[0,1,130,ElisEnum.E_BAND_KU,0,ElisEnum.E_SWITCH_DISABLED,ElisEnum.E_SWITCH_2OF4,0,
						1, ElisEnum.E_LNB_UNIVERSAL,0,9750,10600,11700,0,
						0,0,0,0,0,0,0],
						[1,1,130,ElisEnum.E_BAND_KU,0,ElisEnum.E_SWITCH_DISABLED,ElisEnum.E_SWITCH_2OF4,0,
						1, ElisEnum.E_LNB_UNIVERSAL,0,9750,10600,11700,0,
						0,0,0,0,0,0,0]]
		print 'config=%s' %configuredList
		self.commander.satelliteconfig_SaveList( configuredList )

	def testChannellistByZapping( self ) :
		chlist = self.commander.channel_GetList( ElisEnum.E_TYPE_TV, ElisEnum.E_MODE_ALL, ElisEnum.E_SORT_BY_DEFAULT )
		print 'chlist[%s]'% chlist
	

