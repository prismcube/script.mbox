from pvr.util import run_async
from pvr.net.net import EventCommander
from pvr.elisevent import ElisAction, ElisEnum
import pvr.net.netconfig as netconfig


class ElisCommander( EventCommander ): 
	"""
	request ['Command', 'ipAddress']
	retuns ['TRUE'] or ['FALSE']
	"""
	def setElisReady( self ) :
		req = []
		req.append( ElisAction.ElisReady )
		req.append( netconfig.myIp )
		reply = self.command( req )
		return reply

	"""
	request ['Command', 'ChannelNumber', 'ServiceType']
	retuns ['TRUE'] or ['FALSE']
	"""
	def setCurrentChannel( self, number ):
		req = []
		req.append( ElisAction.SetCurrentChannel )
		req.append( '%d' %number )
		req.append( '%d' %ElisEnum.E_TYPE_TV )
		reply = self.command( req )
		return reply

	"""
	request ['Command']
	retuns [channel] or ['NULL']
	"""
	def getCurrentChannel( self ):
		req = []
		req.append( ElisAction.GetCurrentChannel )
		reply = self.command( req )	
		return reply

	"""
	request ['Command']
	retuns [channel] or ['NULL']
	"""
	def GetPrevChannel( self ):
		req = []
		req.append( ElisAction.GetPrevChannel )
		reply = self.command( req )	
		return reply

	"""
	request ['Command']
	retuns [channel] or ['NULL']
	"""
	def GetNextChannel( self ):
		req = []
		req.append( ElisAction.GetNextChannel )
		reply = self.command( req )	
		return reply

	"""
	request ['Command', 'ServiceType', 'ZappingMode', 'SortingMode']
	retuns [ChannelList] or ['NULL']
	channel[Number, PresentationNumber, Name, ServiceType, Locked, IsCA, IsHD ]
	"""
	def getChannelList( self, serviceType, zappimgMode, sortingMode, channelList ):
		req = []
		req.append( ElisAction.GetChannelList )
		req.append( '%d' %serviceType )
		req.append( '%d' %zappimgMode )
		req.append( '%d' %sortingMode )
		self.send( req )
		while 1:
			reply=self.read()
			if reply[0].upper() == 'NULL':
				return reply
			channelList.append( reply )

	"""
	request ['Command']
	retuns [EPG] or ['NULL']
	"""
	def getPresentEvent( self ):
		req = []
		req.append( ElisAction.GetPresentEvent )
		reply = self.command( req )	
		return reply

	"""
	request ['Command']
	retuns [EPG] or ['NULL']
	"""
	def getFollowingEvent( self ):
		req = []
		req.append( ElisAction.GetFollowingEvent )
		reply = self.command( req )	
		return reply

	"""
	request ['Command', 'eventId', 'sid', 'tsid', 'onid', 'startTime]
	retuns [EPG] or ['NULL']
	"""
	def getGetEvent( self, eventId, sid, tsid, onid, startTime):
		req = []
		req.append( ElisAction.GetEvent )
		req.append( '%d' %eventId )
		req.append( '%d' %sid )
		req.append( '%d' %tsid )
		req.append( '%d' %onid )
		req.append( '%d' %startTime )
		reply = self.command( req )	
		return reply

	"""
	request ['Command']
	retuns [EPG] or ['NULL']
	"""
	def getGetEventList( self, sid, tsid, onid, gmtForm, gmtUntil, maxCount, epgList):
		req = []
		req.append( ElisAction.GetEventList )
		req.append( '%d' %sid )
		req.append( '%d' %tsid )
		req.append( '%d' %onid )
		req.append( '%d' %gmtFrom )
		req.append( '%d' %gmtUntil )
		req.append( '%d' %maxCount )
		self.send( req )
		while 1:
			reply=self.read()
			if reply[0].upper() == 'NULL':
				return reply
			epgList.append( reply )
		
		return reply

		

