from pvr.util import run_async
from pvr.net.net import EventCommander
from pvr.elisevent import ElisAction, ElisEnum
import pvr.net.netconfig as netconfig


class ElisCommander( EventCommander ): 
	"""
	request ['Command', 'ipAddress']
	returns ['TRUE'] or ['FALSE']
	"""
	def setElisReady( self ) :
		req = []
		req.append( ElisAction.ElisReady )
		req.append( netconfig.myIp )
		reply = self.command( req )
		return reply

	"""
	####################################################
						CHANNEL
	####################################################	
	"""
	"""
	request ['Command', 'ChannelNumber', 'ServiceType']
	returns ['TRUE'] or ['FALSE']
	"""
	def channel_SetCurrent( self, number ):
		req = []
		req.append( ElisAction.Channel_SetCurrent )
		req.append( '%d' %number )
		req.append( '%d' %ElisEnum.E_TYPE_TV )
		reply = self.command( req )
		return reply

	"""
	request ['Command']
	returns [Channel] or ['NULL']
	"""
	def channel_GetCurrent( self ):
		req = []
		req.append( ElisAction.Channel_GetCurrent )
		reply = self.command( req )	
		return reply

	"""
	request ['Command']
	returns [Channel] or ['NULL']
	"""
	def channel_GetPrev( self ):
		req = []
		req.append( ElisAction.Channel_GetPrev )
		reply = self.command( req )	
		return reply

	"""
	request ['Command']
	returns [Channel] or ['NULL']
	"""
	def channel_GetNext( self ):
		req = []
		req.append( ElisAction.Channel_GetNext )
		reply = self.command( req )	
		return reply

	"""
	request ['Command', 'ServiceType', 'ZappingMode', 'SortingMode']
	returns [ChannelList] or ['NULL']
	channel[Number, PresentationNumber, Name, ServiceType, Locked, IsCA, IsHD ]
	"""
	def channel_GetList( self, serviceType, zappimgMode, sortingMode, channelList ):
		req = []
		req.append( ElisAction.Channel_GetList )
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
	####################################################
						EPG EVENT
	####################################################	
	"""

	"""
	request ['Command']
	returns [EPG] or ['NULL']
	"""
	def epgevent_GetPresent( self ):
		req = []
		req.append( ElisAction.EPGEvent_GetPresent )
		reply = self.command( req )	
		return reply

	"""
	request ['Command']
	returns [EPG] or ['NULL']
	"""
	def epgevent_GetFollowing( self ):
		req = []
		req.append( ElisAction.EPGEvent_GetFollowing )
		reply = self.command( req )	
		return reply

	"""
	request ['Command', 'eventId', 'sid', 'tsid', 'onid', 'startTime]
	returns [EPG] or ['NULL']
	"""
	def epgevent_Get( self, eventId, sid, tsid, onid, startTime):
		req = []
		req.append( ElisAction.EPGEvent_Get )
		req.append( '%d' %eventId )
		req.append( '%d' %sid )
		req.append( '%d' %tsid )
		req.append( '%d' %onid )
		req.append( '%d' %startTime )
		reply = self.command( req )	
		return reply

	"""
	request ['Command']
	returns [EPG] or ['NULL']
	"""
	def epgevent_GetList( self, sid, tsid, onid, gmtForm, gmtUntil, maxCount, epgList):
		req = []
		req.append( ElisAction.EPGEvent_GetList )
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


	"""
	request ['Command', 'eventId', 'sid', 'tsid', 'onid', 'startTime]
	returns [EPG_Description] or ['NULL']
	"""
	def epgevent_GetDescription( self, eventId, sid, tsid, onid, startTime):
		req = []
		req.append( ElisAction.EPGEvent_GetDescription )
		req.append( '%d' %eventId )
		req.append( '%d' %sid )
		req.append( '%d' %tsid )
		req.append( '%d' %onid )
		req.append( '%d' %startTime )
		reply = self.command( req )	
		return reply


	"""
	####################################################
						DATE TIME
	####################################################	
	"""

	"""
	request ['Command']
	returns [INTEGER] or ['NULL']
	"""
	def datetime_GetGMTTime( self ):
		req = []
		req.append( ElisAction.DateTime_GetGMTTime )
		reply = self.command( req )	
		return reply


	"""
	request ['Command']
	returns [INTEGER] or ['NULL']
	"""
	def datetime_GetLocalOffset( self ):
		req = []
		req.append( ElisAction.DateTime_GetLocalOffset )
		reply = self.command( req )	
		return reply


	"""
	request ['Command']
	returns [INTEGER] or ['NULL']
	"""
	def datetime_GetLocalTime( self ):
		req = []
		req.append( ElisAction.DateTime_GetLocalTime )
		reply = self.command( req )	
		return reply


	"""
	####################################################
					SATELLITE & TRANSPONDER
	####################################################	
	"""

	"""
	request ['Command', 'ChanenlNumber', 'ServiceType']
	returns [Satellite] or ['NULL']
	"""
	def satellite_GetByChannelNumber( self, channelNumber, seriveType ):
		req = []
		req.append( ElisAction.Satellite_GetByChannelNumber )
		req.append( '%d' %channelNumber )
		req.append( '%d' %seriveType )		
		reply = self.command( req )	
		return reply


	"""
	request ['Command', 'Longitude', 'Band']
	returns [Satellite] or ['NULL']
	"""
	def satellite_Get( self, longitude, band ):
		req = []
		req.append( ElisAction.Satellite_Get )
		req.append( '%d' %longitude )
		req.append( '%d' %band )		
		reply = self.command( req )	
		return reply


	"""
	request ['Command', 'SortOrder']
	returns [Satellite] or ['NULL']
	"""
	def satellite_GetList( self, sortOrder, satelliteList ):
		req = []
		req.append( ElisAction.Satellite_GetList )
		req.append( '%d' %sortOrder )
		reply = self.send( req )	

		while 1:
			reply=self.read()
			if reply[0].upper() == 'NULL':
				return reply
			satelliteList.append( reply )
		
		return reply

	"""
	request ['Command', 'Longitude', 'Band', 'Name']
	returns ['TRUE'] or ['FALSE']
	"""
	def satellite_Add( self, longitude, band, name ):
		req = []
		req.append( ElisAction.Satellite_Add )
		req.append( '%d' %longitude )
		req.append( '%d' %band )
		req.append( name )		
		reply = self.command( req )	
		return reply


	"""
	request ['Command', 'Longitude', 'Band', 'Name']
	returns ['TRUE'] or ['FALSE']
	"""
	def satellite_ChangeName( self, longitude, band, name ):
		req = []
		req.append( ElisAction.Satellite_ChangeName )
		req.append( '%d' %longitude )
		req.append( '%d' %band )
		req.append( name )
		reply = self.command( req )	
		return reply

	"""
	request ['Command', 'Longitude', 'Band']
	returns ['TRUE'] or ['FALSE']
	"""
	def satellite_Delete( self, longitude, band ):
		req = []
		req.append( ElisAction.Satellite_Delete )
		req.append( '%d' %longitude )
		req.append( '%d' %band )
		reply = self.command( req )	
		return reply


	"""
	####################################################
					CONFIGURED SATELLITE
	####################################################	
	"""

	"""
	request ['Command', 'SortOrder']
	returns [Satellite] or ['NULL']
	"""
	def satellite_GetConfiguredList( self, sortOrder, satelliteList ):
		req = []
		req.append( ElisAction.Satellite_GetConfiguredList )
		req.append( '%d' %sortOrder )
		reply = self.send( req )

		while 1:
			reply=self.read()
			if reply[0].upper() == 'NULL':
				return reply
			satelliteList.append( reply )
		
		return reply

	"""
	request ['Command', 'Longitude', 'Band']
	returns [Transponder] or ['NULL']
	"""
	def transponder_GetList( self, longitude, band, transponderList ):
		req = []
		req.append( ElisAction.Transponder_GetList )
		req.append( '%d' %longitude )
		req.append( '%d' %band )		
		reply = self.send( req )

		while 1:
			reply=self.read()
			if reply[0].upper() == 'NULL':
				return reply
			transponderList.append( reply )
		
		return reply

	"""
	request ['Command','Logitue', 'Band', 'Transponder']
	returns ['TRUE'] or ['FALSE']
	"""
	def transponder_HasCompatible( self, longitude, band, transponder ):
		req = []
		req.append( ElisAction.Transponder_HasCompatible )
		req.append( '%d' %longitude )
		req.append( '%d' %band )		
		for ele in transponder:
			req.append( '%d' %ele )

		reply = self.command( req )	
		return reply

	"""
	request ['Command','Logitue', 'Band', 'Transponder']
	returns ['TRUE'] or ['FALSE']
	"""
	def transponder_Add( self, longitude, band, transponder ):
		req = []
		req.append( ElisAction.Transponder_Add )
		req.append( '%d' %longitude )
		req.append( '%d' %band )		
		for ele in transponder:
			req.append( '%d' %ele )

		reply = self.command( req )	
		return reply


	"""
	request ['Command','Logitue', 'Band', 'Transponder']
	returns ['TRUE'] or ['FALSE']
	"""
	def transponder_Delete( self, longitude, band, transponder ):
		req = []
		req.append( ElisAction.Transponder_Delete )
		req.append( '%d' %longitude )
		req.append( '%d' %band )		
		for ele in transponder:
			req.append( '%d' %ele )

		reply = self.command( req )	
		return reply


	"""
	request ['Command']
	returns ['TRUE'] or ['FALSE']
	"""
	def satelliteconfig_DeleteAll( self ):
		req = []
		req.append( ElisAction.SatelliteConfig_DeleteAll )
		reply = self.command( req )	
		return reply


	"""
	request ['Command', 'tunerNo']
	returns ['ConfiguredSatellite'] or ['NULL']
	"""
	def satelliteconfig_GetList( self, tunerNo, configuredList ):
		req = []
		req.append( ElisAction.SatelliteConfig_GetList )
		req.append( '%d' %tunerNo )
		reply = self.send( req )

		while 1:
			reply=self.read()
			if reply[0].upper() == 'NULL':
				return reply
			configuredList.append( reply )
		
		return reply

	"""
	request ['Command', 'TunerNo', 'SlotNo']
	returns ['TRUE'] or ['FALSE']
	"""
	def satelliteconfig_GetFirstAvailablePos( self, tunerNo, slotNo ):
		req = []
		req.append( ElisAction.SatelliteConfig_GetFirstAvailablePos )
		req.append( '%d' %tunerNo )
		req.append( '%d' %slotNo )		
		reply = self.command( req )
		return reply


	"""
	request ['Command', 'ConfiguredSatelliteList']
	returns ['TRUE'] or ['FALSE']
	"""
	def satelliteconfig_SaveList( self, configuredList ):
		req = []
		req.append( ElisAction.SatelliteConfig_SaveList )

		for config in configuredList:
			for ele in config:
				req.append( '%d' %ele )
				
		reply = self.send( req )

		return reply

	"""
	####################################################
					MOTORIZED
	####################################################	
	"""

	"""
	request ['Command', 'TunerNo']
	returns ['TRUE'] or ['FALSE']
	"""
	def motorized_Stop( self, tunerNo ):
		req = []
		req.append( ElisAction.Motorized_Stop )
		req.append( '%d' %tunerNo )		
		reply = self.command( req )	
		return reply


	"""
	request ['Command', 'TunerNo']
	returns ['TRUE'] or ['FALSE']
	"""
	def motorized_GoWest( self, tunerNo ):
		req = []
		req.append( ElisAction.Motorized_GoWest )
		req.append( '%d' %tunerNo )		
		reply = self.command( req )	
		return reply

	"""
	request ['Command', 'TunerNo']
	returns ['TRUE'] or ['FALSE']
	"""
	def motorized_GoEast( self, tunerNo ):
		req = []
		req.append( ElisAction.Motorized_GoEast )
		req.append( '%d' %tunerNo )		
		reply = self.command( req )	
		return reply

	"""
	request ['Command', 'TunerNo']
	returns ['TRUE'] or ['FALSE']
	"""
	def motorized_StepWest( self, tunerNo ):
		req = []
		req.append( ElisAction.Motorized_StepWest )
		req.append( '%d' %tunerNo )		
		reply = self.command( req )	
		return reply

	"""
	request ['Command', 'TunerNo']
	returns ['TRUE'] or ['FALSE']
	"""
	def motorized_StepEast( self, tunerNo ):
		req = []
		req.append( ElisAction.Motorized_StepEast )
		req.append( '%d' %tunerNo )		
		reply = self.command( req )	
		return reply

	"""
	request ['Command', 'TunerNo']
	returns ['TRUE'] or ['FALSE']
	"""
	def motorized_SetEastLimit( self, tunerNo ):
		req = []
		req.append( ElisAction.Motorized_SetEastLimit )
		req.append( '%d' %tunerNo )
		reply = self.command( req )
		return reply

	"""
	request ['Command', 'TunerNo']
	returns ['TRUE'] or ['FALSE']
	"""
	def motorized_SetWestLimit( self, tunerNo ):
		req = []
		req.append( ElisAction.Motorized_SetWestLimit )
		req.append( '%d' %tunerNo )
		reply = self.command( req )
		return reply

	"""
	request ['Command', 'TunerNo']
	returns ['TRUE'] or ['FALSE']
	"""
	def motorized_ResetLimit( self, tunerNo ):
		req = []
		req.append( ElisAction.MotorizedResetLimit )
		req.append( '%d' %tunerNo )
		reply = self.command( req )
		return reply

	"""
	request ['Command', 'TunerNo']
	returns ['TRUE'] or ['FALSE']
	"""
	def motorized_GotoNull( self, tunerNo ):
		req = []
		req.append( ElisAction.MotorizedGotoNull )
		req.append( '%d' %tunerNo )
		reply = self.command( req )
		return reply

	"""
	request ['Command', 'TunerNo', 'PosNo']
	returns ['TRUE'] or ['FALSE']
	"""
	def motorized_SavePosition( self, tunerNo, posNo ):
		req = []
		req.append( ElisAction.Motorized_SavePosition )
		req.append( '%d' %tunerNo )
		req.append( '%d' %posNo )		
		reply = self.command( req )
		return reply


