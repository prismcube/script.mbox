
#Channel :  [Number, PresentationNumber, Name, ServiceType, Locked, IsCA, IsHD]
#EPG : [ElisName, EventId, EventName, Sid, Tsid, Onid, StartTime, Duration, ContentTag, Components, IsSeries, HasTimer, TimerId, AgeRating ]

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
	SetCurrentChannel					= 'SetCurrentChannel'	
	GetCurrentChannel					= 'GetCurrentChannel'
	GetPrevChannel						= 'GetPrevChannel'
	GetNextChannel						= 'GetNextChannel'
	GetLocked							= 'GetLocked'
	SetTVRadio							= 'SetTVRadio'
	GetTVRadio							= 'GetTVRadio'	
	SetZappingMode						= 'SetZappingMode'
	GetZappingMode						= 'GetZappingMode'
	SetAVBlank							= 'SetAVBlank'
	GetAVBlank							= 'GetAVBlank'
	SetChannelStatus					= 'SetChannelStatus'	
	GetChannelStatus					= 'GetChannelStatus'
	GetChannelList						= 'GetChannelList'
	GetPresentEvent						= 'GetPresentEvent'
	GetFollowingEvent					= 'GetFollowingEvent'
	GetEvent							= 'GetEvent'
	GetEventList						= 'GetEventList'	


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

	# SortingMode
	E_SORT_BY_DEFAULT				= 0
	E_SORT_BY_ALPHABET				= 1
	E_SORT_BY_CARRIER				= 2
	E_SORT_BY_NUMBER				= 3
	E_SORT_BY_HD					= 4

	E_HasHDVideo 					= 1 << 0
	E_Has16_9Video					= 1 << 1
	E_HasStereoAudio				= 1 << 2
	E_mHasMultichannelAudio			= 1 << 3	
	E_mHasDolbyDigital				= 1 << 4
	E_mHasSubtitles					= 1 << 5
	E_mHasHardOfHearingAudio		= 1 << 6
	E_mHasHardOfHearingSub			= 1 << 7
	E_mHasVisuallyImpairedAudio		= 1 << 8
	
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


