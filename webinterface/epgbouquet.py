from datetime import datetime
from webinterface import Webinterface
import dbopen

class ElmoEpgBouquet( Webinterface ) :

	def __init__(self, urlPath) :
	
		super(ElmoEpgBouquet, self).__init__(urlPath)
		self.currenttime = self.mCommander.Datetime_GetLocalTime()

		"""
		self.conn = dbopen.DbOpen('epg.db').getConnection()		
		sql = 'select eventId, startTime, duration, eventName, eventDescription, sid, tsid, onid '
		sql += ' from tblEpg where startTime <= ' + self.params['time'] + ' and startTime + duration >= ' + self.params['time']

		print sql

		self.c = self.conn.cursor()
		self.c.execute(sql)
		"""

	def xmlResult(self) :

		xmlStr = ''
		xmlStr += '<?xml version="1.0" encoding="UTF-8"?> '
		xmlStr += '<e2eventlist> '

		"""
		for row in self.c :

			conn = dbopen.DbOpen('channel.db').getConnection()
			c = conn.cursor()

			sql = 'select name from tblChannel where sid=' + str( row[5] ) + ' and tsid=' + str( row[6] ) + ' and onid=' + str( row[7] )
			c.execute(sql)

			result = c.fetchone()
			
			xmlStr += '<e2event> '
			xmlStr += '<e2eventid> '
			xmlStr += 	str( row[0] )
			xmlStr += '</e2eventid> '
			xmlStr += '<e2eventstart> '
			xmlStr += 	str( row[1] )
			xmlStr += '</e2eventstart> '
			xmlStr += '<e2eventduration> '
			xmlStr += 	str( row[2] )
			xmlStr += '</e2eventduration> '
			xmlStr += '<e2eventcurrenttime> '
			xmlStr += 	str( self.currenttime )
			xmlStr += '</e2eventcurrenttime> '
			xmlStr += '<e2eventtitle> '
			xmlStr += 	row[3]
			xmlStr += '</e2eventtitle> '
			xmlStr += '<e2eventdescription> '
			xmlStr += 	row[4]
			xmlStr += '</e2eventdescription> '
			xmlStr += '<e2eventdescriptionextended> '
			xmlStr += 	'' 
			xmlStr += '</e2eventdescriptionextended> '
			xmlStr += '<e2eventservicereference> '
			xmlStr += 	self.makeRef( row[5], row[6], row[7] )  	# def makeRef(self, sid, tsid, onid) :
			xmlStr += '</e2eventservicereference> '
			xmlStr += '<e2eventservicename> '
			xmlStr += 	result[0]
			xmlStr += '</e2eventservicename> '
			xmlStr += '</e2event> '

			conn.close()
		"""
		
		xmlStr += '</e2eventlist> '
		return xmlStr
		
