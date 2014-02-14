from datetime import datetime
from webinterface import Webinterface
import dbopen

class ElmoEpgServiceNext( Webinterface ) :

	def __init__(self, urlPath) :
		super(ElmoEpgServiceNext, self).__init__(urlPath)
		
		#print self.params['sRef']
		#print self.params['time']
		#print self.params['endTime']

		print 'sRef is'
		print self.params['sRef']

		ref = self.unMakeRef( self.params['sRef'] )
		self.currenttime = self.mCommander.Datetime_GetLocalTime()
		self.currenttime = 1335344600

		self.conn = dbopen.DbOpen('epg.db').getConnection()		

		sql = 'select eventId, startTime, duration, eventName, eventDescription, sid, tsid, onid '
		sql += ' from tblEPG where sid=' + str( ref['sid'] ) + ' and tsid=' + str( ref['tsid'] ) + ' and onid=' + str( ref['onid'] ) + ' and startTime  >' + str( self.currenttime )
		sql += ' order by startTime limit 1 '

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
			xmlStr += 	row[3]
			xmlStr += '</e2eventdescription>\n'
			xmlStr += '<e2eventdescriptionextended>\n'
			xmlStr += 	row[4]
			xmlStr += '</e2eventdescriptionextended>\n'
			xmlStr += '<e2eventservicereference>\n'
			xmlStr += 	self.makeRef( row[5], row[6], row[7] )  	# def makeRef(self, sid, tsid, onid) :
			xmlStr += '</e2eventservicereference>\n'
			xmlStr += '<e2eventservicename>\n'
			# xmlStr += 	result[0]
			xmlStr += 'na'
			xmlStr += '</e2eventservicename>\n'
			xmlStr += '</e2event>\n'
			
			conn.close()
		
		xmlStr += '</e2eventlist>\n'
		
		"""
		xmlStr = '<?xml version="1.0" encoding="UTF-8"?>'
		xmlStr += '<e2eventlist>'
		xmlStr += '<e2event>'
		xmlStr += '<e2eventid>24039</e2eventid>'
		xmlStr += '<e2eventstart>1258495800</e2eventstart>'
		xmlStr += '<e2eventduration>1200</e2eventduration>'
		xmlStr += '<e2eventcurrenttime>1258494377</e2eventcurrenttime>'
		xmlStr += '<e2eventtitle>ANIXE HD News</e2eventtitle>'
		xmlStr += '<e2eventdescription>ANIXE HD News</e2eventdescription>'
		xmlStr += '<e2eventdescriptionextended>(Deutschland 2009)  Inhalt: T?glich pr?sentiert Moderatorin Vio Kosanic die neuesten Nachrichten aus Wirtschaft, Politik und Sport im ?berblick.</e2eventdescriptionextended>'
		xmlStr += '<e2eventservicereference>1:0:1:1324:3ef:1:C00000:0:0:0:</e2eventservicereference>'
		xmlStr += '<e2eventservicename>&lt;n/a&gt;</e2eventservicename>'
		xmlStr += '</e2event>'
		xmlStr += '</e2eventlist>'
		"""
		
		return xmlStr
		

