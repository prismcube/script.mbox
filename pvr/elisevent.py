
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
	SetChnnelByNumber					= 'SetChnnelByNumber'
	CheckLock							= 'CheckLock'
	ChangeTVRadio						= 'ChangeTVRadio'
	ChangeZappingMode					= 'ChangeZappingMode'
	AVBank								= 'AVBank'
	IsAVBank							= 'IsAVBank'
	GetChannelStatus					= 'GetChannelStatus'
	SetChannelStatus					= 'SetChannelStatus'



class ElisEventBus(object):
	def __init__(self):
		self.listeners = []
        
	def register(self, listener, isfirst=False):
		if isfirst:
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


