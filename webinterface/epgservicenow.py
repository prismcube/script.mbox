from datetime import datetime
from webinterface import Webinterface
import dbopen

class ElmoEpgServiceNow( Webinterface ) :

	def __init__(self, urlPath) :
		super(ElmoEpgServiceNow, self).__init__(urlPath)
		
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
		sql += ' from tblEPG where sid=' + str( ref['sid'] ) + ' and tsid=' + str( ref['tsid'] ) + ' and onid=' + str( ref['onid'] ) + ' and startTime<=' + str( self.currenttime ) + ' and startTime + duration >' + str( self.currenttime )

		print sql

		self.c = self.conn.cursor()
		self.c.execute(sql)

	def xmlResult(self) :
		
		xmlStr = ''
		xmlStr += '<?xml version="1.0" encoding="UTF-8"?> '
		xmlStr += '<e2eventlist> '

		for row in self.c :

			conn = dbopen.DbOpen('channel.db').getConnection()
			c = conn.cursor()

			sql = 'select name from tblChannel where sid=' + str( row[5] ) + ' and tsid=' + str( row[6] ) + ' and onid=' + str( row[7] )
			c.execute(sql)

			result = c.fetchone()
			
			xmlStr += '<e2event>'
			xmlStr += '<e2eventid>'
			xmlStr += 	str( row[0] )
			xmlStr += '</e2eventid>'
			xmlStr += '<e2eventstart>'
			xmlStr += 	str( row[1] )
			xmlStr += '</e2eventstart>'
			xmlStr += '<e2eventduration>'
			xmlStr += 	str( row[2] )
			xmlStr += '</e2eventduration>'
			xmlStr += '<e2eventcurrenttime>'
			xmlStr += 	str( self.currenttime )
			xmlStr += '</e2eventcurrenttime>'
			xmlStr += '<e2eventtitle>'
			xmlStr += 	row[3]
			xmlStr += '</e2eventtitle>'
			xmlStr += '<e2eventdescription>'
			# xmlStr += 	row[4].encode('ascii', 'ignore')
			xmlStr += 	row[3]
			xmlStr += '</e2eventdescription>'
			xmlStr += '<e2eventdescriptionextended>'
			xmlStr += 	row[4]
			xmlStr += '</e2eventdescriptionextended>'
			xmlStr += '<e2eventservicereference>'
			xmlStr += 	self.makeRef( row[5], row[6], row[7] )  	# def makeRef(self, sid, tsid, onid) :
			xmlStr += '</e2eventservicereference>'
			xmlStr += '<e2eventservicename>'
			# xmlStr += 	result[0]
			xmlStr += 'na'
			xmlStr += '</e2eventservicename>'
			xmlStr += '</e2event>'
			
			conn.close()
		
		xmlStr += '</e2eventlist>'
		
		"""

		xmlStr = '<?xml version="1.0" encoding="UTF-8"?><e2eventlist>	<e2event> '
		xmlStr += '<e2eventid>24036</e2eventid> '
		xmlStr += '<e2eventstart>1258485300</e2eventstart> '
		xmlStr += '<e2eventduration>6600</e2eventduration>'
		xmlStr += '<e2eventcurrenttime>1258490131</e2eventcurrenttime>'
		xmlStr += '<e2eventtitle>Herzsprung</e2eventtitle>'
		xmlStr += '<e2eventdescription>Herzsprung</e2eventdescription>'
		xmlStr += '<e2eventdescriptionextended>Regiseur:Helke Misselwitz(Deutschland 1992)  Inhalt: Die arbeitslose K?chin Johanna kehrt mit ihren beiden Kindern in ihr Heimatdorf Herzsprung zur?ck. Als ihr Mann sich nach seinem Bankrott selbst t?tet, scheint es f?r Johanna keine Chance mehr zu geben. Doch ihr lebenslustiger Vater und eine Freundin helfen ihr wieder auf die Beine.  Besetzung: Ben Becker, Tatjana Besson, G?nter Lamprecht</e2eventdescriptionextended>'
		xmlStr += '<e2eventservicereference>1:0:1:1324:3ef:1:C00000:0:0:0:</e2eventservicereference>'
		xmlStr += '<e2eventservicename>&lt;n/a&gt;</e2eventservicename>'
		xmlStr += '</e2event>'
	
		xmlStr += '</e2eventlist>' 
		"""
		
		return xmlStr
		
