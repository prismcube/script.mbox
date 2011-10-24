
class ElisEvent(object):
	ElisPMTReceived						= 'ElisPMTReceived'
	ElisCurrentEITReceived				= 'ElisCurrentEITReceived'
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
	GetLocked							= 'GetLocked'
	SetTVRadio							= 'SetTVRadio'
	GetTVRadio							= 'GetTVRadio'	
	SetZappingMode						= 'SetZappingMode'
	GetZappingMode						= 'GetZappingMode'
	SetAVBlank							= 'SetAVBlank'
	GetAVBlank							= 'GetAVBlank'
	SetChannelStatus					= 'SetChannelStatus'	
	GetChannelStatus					= 'GetChannelStatus'


class ElisEnum(object):
	E_TYPE_INVALID 				= 0
	E_TYPE_TV 					= 1
	E_TYPE_RADIO				= 2
	E_TYPE_DATA					= 3



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


