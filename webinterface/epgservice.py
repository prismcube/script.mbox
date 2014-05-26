from datetime import datetime
from webinterface import Webinterface
from xml.sax.saxutils import escape

class ElmoEpgService( Webinterface ) :

	def __init__(self, urlPath) :
		super(ElmoEpgService, self).__init__(urlPath)
		
		#print self.params['sRef']
		#print self.params['time']
		#print self.params['endTime']

		ref = self.unMakeRef( self.params['sRef'] )
		self.gmtFrom = self.mDataCache.Datetime_GetLocalTime()
		self.gmtUntil = self.gmtFrom + ( 3600 * 24 * 1 )
		self.maxCount = 100

		self.epgList = self.mCommander.Epgevent_GetList( ref['sid'], ref['tsid'], ref['onid'], self.gmtFrom, self.gmtUntil, self.maxCount );
	
	def xmlResult(self) :

		xmlStr = ''
		xmlStr += '<?xml version="1.0" encoding="UTF-8"?>\n'
		xmlStr += '<e2eventlist>\n'

		if self.epgList :
			for row in self.epgList :
	
				xmlStr += '<e2event>\n'
				xmlStr += '<e2eventid>' + str( row.mEventId ) + '</e2eventid>\n'
				xmlStr += '<e2eventstart>' + str( row.mStartTime ) + '</e2eventstart>\n'
				xmlStr += '<e2eventduration>' + str( row.mDuration ) + '</e2eventduration>\n'
				xmlStr += '<e2eventcurrenttime>' + str( self.gmtFrom ) + '</e2eventcurrenttime>\n'
				xmlStr += '<e2eventtitle>' + escape( row.mEventName ) + '</e2eventtitle>\n'
				xmlStr += '<e2eventdescription>' + escape( row.mEventDescription ) +'</e2eventdescription>\n'
				xmlStr += '<e2eventdescriptionextended></e2eventdescriptionextended>\n'
				xmlStr += '<e2eventservicereference>' + self.params['sRef'] + '</e2eventservicereference>\n'
				xmlStr += '<e2eventservicename>' + escape(row.mEventName) +'</e2eventservicename>\n'
				xmlStr += '</e2event>\n'

				# print xmlStr

		xmlStr += '</e2eventlist>\n'

		return xmlStr
		
