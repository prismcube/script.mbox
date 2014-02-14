from datetime import datetime
from webinterface import Webinterface
import dbopen

class ElmoEpgService( Webinterface ) :

	def __init__(self, urlPath) :
		super(ElmoEpgService, self).__init__(urlPath)
		
		#print self.params['sRef']
		#print self.params['time']
		#print self.params['endTime']

		ref = self.unMakeRef( self.params['sRef'] )
		self.currenttime = self.mCommander.Datetime_GetLocalTime()

		self.conn = dbopen.DbOpen('epg.db').getConnection()		

		sql = 'select eventId, startTime, duration, eventName, eventDescription, sid, tsid, onid '
		sql += ' from tblEPG where sid=' + str( ref['sid'] ) + ' and tsid=' + str( ref['tsid'] ) + ' and onid=' + str( ref['onid'] ) + ' and startTime=' + self.params['time'] + ' and startTime + duration=' + self.params['endTime']
		
		print sql

		self.c = self.conn.cursor()
		self.c.execute(sql)

	def xmlResult(self) :

		xmlStr = ''
		xmlStr += '<?xml version="1.0" encoding="UTF-8"?>\n'
		xmlStr += '<e2eventlist>\n'

		for row in self.c :

			conn = dbopen.DbOpen('channel.db').getConnection()
			c = conn.cursor()

			sql = 'select name from tblChannel where sid=' + str( row[5] ) + ' and tsid=' + str( row[6] ) + ' and onid=' + str( row[7] )
			c.execute(sql)

			result = c.fetchone()

			xmlStr += '<e2event>\n'
			xmlStr += '<e2eventid>\n'
			xmlStr += 	str( row[0] )
			xmlStr += '</e2eventid>\n'
			xmlStr += '<e2eventstart>\n'
			xmlStr += 	str( row[1] )
			xmlStr += '</e2eventstart>\n'
			xmlStr += '<e2eventduration>\n'
			xmlStr += 	str( row[2] )
			xmlStr += '</e2eventduration>\n'
			xmlStr += '<e2eventcurrenttime>\n'
			xmlStr += 	str( self.currenttime )
			xmlStr += '</e2eventcurrenttime>\n'
			xmlStr += '<e2eventtitle>\n'
			xmlStr += 	row[3]
			xmlStr += '</e2eventtitle>\n'
			xmlStr += '<e2eventdescription>\n'
			# xmlStr += 	row[4].encode('ascii', 'ignore')
			xmlStr += 	row[4]
			xmlStr += '</e2eventdescription>\n'
			xmlStr += '<e2eventdescriptionextended>\n'
			xmlStr += 	'' 
			xmlStr += '</e2eventdescriptionextended>\n'
			xmlStr += '<e2eventservicereference>\n'
			xmlStr += 	self.makeRef( row[5], row[6], row[7] )  	# def makeRef(self, sid, tsid, onid) :
			xmlStr += '</e2eventservicereference>\n'
			xmlStr += '<e2eventservicename>\n'
			xmlStr += 	result[0]
			xmlStr += '</e2eventservicename>\n'
			xmlStr += '</e2event>\n'

			conn.close()

		xmlStr += '</e2eventlist>\n'

		return xmlStr
		
