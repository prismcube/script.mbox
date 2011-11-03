
#Channel :  [Number, PresentationNumber, Name, ServiceType, Locked, IsCA, IsHD, Nid, Sid, Tsid, Onid, CarrierType ]
#EPG : [ EventId, EventName, Sid, Tsid, Onid, StartTime, Duration, ContentTag, Components, IsSeries, HasTimer, TimerId, AgeRating ]
#EPG_Description : [EventId, Description ]
#Satellite  : [Longitude, Band, Name]
#Transponder : [Frequency, Symbolrate, Polarization, FECMode, Tsid, Onid, Nid]
#ConfiguredSatellite : [TunerIndex, SlotNumber, SatelliteLongitude, BandType, FrequencyLevel, DisEqc11, DisEqcMode, DisEqcRepeat,
#				   IsConfigUsed, LnbType, MotorizedType, LowLNB, HighLNB, LNBThreshold, MotorizedData,
#				   IsOneCable, OneCablePin, OneCableMDU, OneCableLoFreq1, OneCableLoFreq2, OneCableUBSlot, OneCableUBFreq]



class ElisEvent(object):
	ElisPMTReceived						= 'ElisPMTReceived'					
	ElisCurrentEITReceived				= 'ElisCurrentEITReceived'		#EPG
	ElisVideoIentified					= 'ElisVideoIentified'
	ElisChannelChanged					= 'ElisChannelChanged'
	ElisRecordingStarted				= 'ElisRecordingStarted'
	ElisRecordingStopped				= 'ElisRecordingStopped'
	ElisChannelChangedByRecord			= 'ElisChannelChangedByRecord'
	ElisPlaybackStopped					= 'ElisPlaybackStopped'
	ElisTimeshiftEITReceived			= 'ElisTimeshiftEITReceived'


class ElisAction(object):
	Tune								= 'Tune'
	ElisReady							= 'ElisReady'
	Channel_SetCurrent					= 'Channel_SetCurrent'	
	Channel_GetCurrent					= 'Channel_GetCurrent'
	Channel_GetPrev						= 'Channel_GetPrev'
	Channel_GetNext						= 'Channel_GetNext'
	Channel_GetList						= 'Channel_GetList'

	EPGEvent_GetPresent					= 'EPGEvent_GetPresent'
	EPGEvent_GetFollowing				= 'EPGEvent_GetFollowing'
	EPGEvent_Get						= 'EPGEvent_Get'
	EPGEvent_GetList					= 'EPGEvent_GetList'
	EPGEvent_GetDescription				= 'EPGEvent_GetDescription'

	DateTime_GetGMTTime					= 'DateTime_GetGMTTime'
	DateTime_GetLocalOffset				= 'DateTime_GetLocalOffset'
	DateTime_GetLocalTime				= 'DateTime_GetLocalTime'

	Satellite_GetByChannelNumber		= 'Satellite_GetByChannelNumber'
	Satellite_Get						= 'Satellite_Get'
	Satellite_GetList					= 'Satellite_GetList'
	Satellite_Add						= 'Satellite_Add'
	Satellite_ChangeName				= 'Satellite_ChangeName'
	Satellite_Delete					= 'Satellite_Delete'
	Satellite_GetConfiguredList			= 'Satellite_GetConfiguredList'

	Transponder_GetList					= 'Transponder_GetList'
	Transponder_HasCompatible			= 'Transponder_HasCompatible'
	Transponder_Add						= 'Transponder_Add'
	Transponder_Delete					= 'Transponder_Delete'

	SatelliteConfig_DeleteAll			= 'SatelliteConfig_DeleteAll'
	SatelliteConfig_GetList				= 'SatelliteConfig_GetList'
	SatelliteConfig_GetFirstAvailablePos	= 'SatelliteConfig_GetFirstAvailablePos'
	SatelliteConfig_SaveList			= 'SatelliteConfig_SaveList'
	
	Motorized_Stop						= 'Motorized_Stop'
	Motorized_GoWest					= 'Motorized_GoWest'
	Motorized_GoEast					= 'Motorized_GoEast'
	Motorized_StepWest					= 'Motorized_StepWest'
	Motorized_StepEast					= 'Motorized_StepEast'
	Motorized_SetEastLimit				= 'Motorized_SetEastLimit'
	Motorized_SetWestLimit				= 'Motorized_SetWestLimit'
	Motorized_ResetLimit				= 'Motorized_ResetLimit'
	Motorized_GotoNull					= 'Motorized_GotoNull'
	Motorized_SavePosition				= 'Motorized_SavePosition'



class ElisEnum(object):
	# ServiceType
	E_TYPE_INVALID 				= 0
	E_TYPE_TV 					= 1
	E_TYPE_RADIO				= 2
	E_TYPE_DATA					= 3

	# ZappingMode
	E_MODE_ALL					= 0 
	E_MODE_FAVORITE				= 1
	E_MODE_NETWORK				= 2
	E_MODE_SATELLITE			= 3
	E_MODE_CAS					= 4

	# Channel SortingMode
	E_SORT_BY_DEFAULT				= 0
	E_SORT_BY_ALPHABET				= 1
	E_SORT_BY_CARRIER				= 2
	E_SORT_BY_NUMBER				= 3
	E_SORT_BY_HD					= 4

	#Channel Componets
	E_HasHDVideo 					= 1 << 0
	E_Has16_9Video					= 1 << 1
	E_HasStereoAudio				= 1 << 2
	E_mHasMultichannelAudio			= 1 << 3
	E_mHasDolbyDigital				= 1 << 4
	E_mHasSubtitles					= 1 << 5
	E_mHasHardOfHearingAudio		= 1 << 6
	E_mHasHardOfHearingSub			= 1 << 7
	E_mHasVisuallyImpairedAudio		= 1 << 8

	#Transponder  Polarization
	E_LNB_HORIZONTAL				= 0
	E_LNB_VERTICAL					= 1
	E_LNB_LEFT						= 2
	E_LNB_RIGHT						= 3

	#Transponder  FECMode
	E_FEC_UNDEFINED					= 0
	E_DVBS_1_2						= 1
	E_DVBS_2_3						= 2
	E_DVBS_3_4						= 3
	E_DVBS_5_6						= 4
	E_DVBS_7_8						= 5
	E_DVBS2_QPSK_1_2				= 6
	E_DVBS2_QPSK_3_5				= 7
	E_DVBS2_QPSK_2_3				= 8
	E_DVBS2_QPSK_3_4				= 9
	E_DVBS2_QPSK_4_5				= 10
	E_DVBS2_QPSK_5_6				= 11
	E_DVBS2_QPSK_8_9				= 12
	E_DVBS2_QPSK_9_10				= 13
	E_DVBS2_8PSK_3_5				= 14
	E_DVBS2_8PSK_2_3				= 15
	E_DVBS2_8PSK_3_4				= 16
	E_DVBS2_8PSK_5_6				= 17
	E_DVBS2_8PSK_8_9				= 18
	E_DVBS2_8PSK_9_10				= 19

	#Satellite Config
	E_SAT_22KHZ_OFF 				= 0
	E_SAT_22KHZ_ON 					= 1

	E_SWITCH_DISABLED 				= 0
	E_SWITCH_1OF4					= 1
	E_SWITCH_2OF4					= 2
	E_SWITCH_3OF4					= 3
	E_SWITCH_4OF4					= 4
	E_SWITCH_MINI_A					= 5
	E_SWITCH_MINI_B					= 6

	E_LNB_UNIVERSAL					= 0
	E_LNB_SINGLE					= 1
	E_LNB_DUAL						= 2

	E_MOTORIZED_OFF					= 0
	E_MOTORIZED_ON					= 1
	E_MOTORIZED_USALS				= 2

	E_SORT_LONGITUDE				= 0
	E_SORT_NAME						= 1
	E_SORT_INSERTED					= 2
	
	# EPG
	E_MAX_EPG_REQUEST_COUNT			= 128




class ElisEventBus(object):
	def __init__(self):
		self.listeners = []

	def register(self, listener, addfirst=False):
		if addfirst:
			self.listeners.insert(0, listener)
		else:
			self.listeners.append(listener)

	def deregister(self, listener):
		try:
			self.listeners.remove(listener)
		except ValueError, ve:
			print 'ValueError=%s' %ve

	def publish(self, event):
		print 'Publishing event %s to %d listeners' % (event, len(self.listeners))

		for i in range( len( event ) ):
			print 'publish event[%d] ---> %s' %(i,event[i])
		
		for listener in self.listeners[:]:
			try:
				listener.onEvent(event)
			except:
				print 'Error publishing event %s to %s' % (event, listener)


