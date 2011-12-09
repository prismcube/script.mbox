
#Channel :  [Number, PresentationNumber, Name, ServiceType, Locked, IsCA, IsHD, Nid, Sid, Tsid, Onid, CarrierType ]
#EPG : [ EventId, EventName, Sid, Tsid, Onid, StartTime, Duration, ContentTag, Components, IsSeries, HasTimer, TimerId, AgeRating ]
#EPG_Description : [EventId, Description ]
#Satellite  : [Longitude, Band, Name]
#Satellite Carrier : [Frequency, Symbolrate, Polarization, FECMode, Tsid, Onid, Nid]
#ConfiguredSatellite : [TunerIndex, SlotNumber, SatelliteLongitude, BandType, FrequencyLevel, DisEqc11, DisEqcMode, DisEqcRepeat,
#				   IsConfigUsed, LnbType, MotorizedType, LowLNB, HighLNB, LNBThreshold, MotorizedData,
#				   IsOneCable, OneCablePin, OneCableMDU, OneCableLoFreq1, OneCableLoFreq2, OneCableUBSlot, OneCableUBFreq]
#PlayerStatus [ Mode, Key, ServiceType, StartTimeInMs, PlayTimeInMs, EndTimeInMs, Speed, IsTimeshiftPending ]
#RecordInfo [ RecordKey, FolderNumber, StartTime, Duration, PlayedOffset(longlong), ChannelNo, ServiceType, ChannelName, RecordName, Sid, Vpid, Apid, Locked ]



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
		return

		for i in range( len( event ) ):
			print 'publish event[%d] ---> %s' %(i,event[i])
		
		for listener in self.listeners[:]:
			try:
				listener.onEvent(event)
			except:
				print 'Error publishing event %s to %s' % (event, listener)


