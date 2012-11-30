from datetime import datetime
from webinterface import Webinterface
import dbopen

class ElmoGetAllServices( Webinterface ) :

	def __init__(self, urlPath) :
	
		super(ElmoGetAllServices, self).__init__(urlPath)
		# self.currenttime = self.mCommander.Datetime_GetLocalTime()

		self.conn = dbopen.DbOpen('channel.db').getConnection()		
		sql = "select Max(name) as name, sid, tsid, onid from tblChannel group by sid, tsid, onid"
		
		self.c = self.conn.cursor()
		self.c.execute(sql)
		self.result = self.c.fetchall()

		self.c.execute(sql)
		self.resultSub = self.c.fetchall()
		
	def xmlResult(self) :

		serviceList = '<e2servicelist>'
		for row in self.resultSub :
			serviceList += '<e2service>'
			serviceList += '<e2servicereference>' + self.makeRef(row[1], row[2], row[3]) +'</e2servicereference>'
			serviceList += '<e2servicename>' + row[0] + '</e2servicename>'
			serviceList += '</e2service>'
		serviceList += '</e2servicelist>' 

		xmlStr = ''
		xmlStr += '<?xml version="1.0" encoding="UTF-8"?> '
		xmlStr += '<e2servicelistrecursive>'

		for row in self.result :
		# def makeRef( self, sid, tsid, onid ) :

			xmlStr += '<e2bouquet>'
			xmlStr += '	<e2servicereference>' + self.makeRef(row[1], row[2], row[3]) + '</e2servicereference>'
			xmlStr += '	<e2servicename>' + row[0] + '</e2servicename>'
			xmlStr += serviceList
			xmlStr += '</e2bouquet>'	

		xmlStr += '</e2servicelistrecursive>'
		
		return xmlStr
		
