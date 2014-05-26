from datetime import datetime
from webinterface import Webinterface
import dbopen
from urllib import unquote, quote

class ElmoGetAllServices( Webinterface ) :

	def __init__(self, urlPath) :
	
		super(ElmoGetAllServices, self).__init__(urlPath)
		# self.currenttime = self.mCommander.Datetime_GetLocalTime()

		self.conn = dbopen.DbOpen('channel.db').getConnection()		
		sql = "select Max(name) as name, sid, tsid, onid, Max(Presentation) as chno from tblChannel group by sid, tsid, onid order by chno"
		
		self.c = self.conn.cursor()
		self.c.execute(sql)
		self.result = self.c.fetchall()

		#self.c.execute(sql)
		#self.resultSub = self.c.fetchall()
		
	def xmlResult(self) :

		"""
		serviceList = '<e2servicelist>\n'
		for row in self.resultSub :
			serviceList += '<e2service>\n'
			serviceList += '<e2servicereference>' + self.makeRef(row[1], row[2], row[3]) +'</e2servicereference>\n'
			serviceList += '<e2servicename>' + row[0] + '</e2servicename>\n'
			serviceList += '</e2service>\n'
		serviceList += '</e2servicelist>\n' 
		"""
		
		xmlStr = ''
		xmlStr += '<?xml version="1.0" encoding="UTF-8"?>\n'
		xmlStr += '<e2servicelistrecursive>\n'

		for row in self.result :
		# def makeRef( self, sid, tsid, onid ) :

			#xmlStr += '<e2bouquet>\n'
			xmlStr += '	<e2service>\n'
			xmlStr += '		<e2servicereference>' + self.makeRef(row[1], row[2], row[3]) + '</e2servicereference>\n'
			xmlStr += '		<e2servicename>' + quote( row[0] ) + '</e2servicename>\n'
			xmlStr += '	</e2service>\n'
			# xmlStr += serviceList
			# xmlStr += '</e2bouquet>\n'	

		xmlStr += '</e2servicelistrecursive>\n'
		
		return xmlStr
		
