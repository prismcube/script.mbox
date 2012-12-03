from datetime import datetime
from webinterface import Webinterface
import dbopen

class ElmoGetServices( Webinterface ) :

	def __init__(self, urlPath) :
	
		super(ElmoGetServices, self).__init__(urlPath)

		self.conn = dbopen.DbOpen('channel.db').getConnection()		
		self.c = self.conn.cursor()
		
	def xmlResult(self) :

		if 'sRef' in self.params :

			try :

				print 'sRef is '
				print self.params['sRef']
				
				sRefParams = self.unMakeRef(self.params['sRef'])
				conditions = sRefParams['comment'].split('_')
				
				sql = "select name, sid, tsid, onid  from " + conditions[0] + " where " + conditions[1] + " = '" + conditions[2] + "'"
				self.c.execute(sql)

				self.result = self.c.fetchall()

				"""
							
				self.xmlStr = '<?xml version="1.0" encoding="UTF-8"?>'
				self.xmlStr += '<e2servicelist>'

				self.xmlStr += '<e2service>'
				self.xmlStr += '<e2servicereference>1:0:1:1325:3EF:1:C00000:0:0:0:</e2servicereference>'
				self.xmlStr += '<e2servicename>Why Oh Why</e2servicename>'
				self.xmlStr += '</e2service>'			
				
				self.xmlStr += '<e2service>'
				self.xmlStr += '<e2servicereference>1:0:1:1325:3EF:1:C00000:0:0:0:</e2servicereference>'
				self.xmlStr += '<e2servicename>HowSo?</e2servicename>'
				self.xmlStr += '</e2service>'

				self.xmlStr += '<e2service>'
				self.xmlStr += '<e2servicereference>1:0:1:1325:3EF:1:C00000:0:0:0:</e2servicereference>'
				self.xmlStr += '<e2servicename>Testing</e2servicename>'
				self.xmlStr += '</e2service>'

				self.xmlStr += '<e2service>'
				self.xmlStr += '<e2servicereference>1:0:1:1325:3EF:1:C00000:0:0:0:</e2servicereference>'
				self.xmlStr += '<e2servicename>Servus TV</e2servicename>'
				self.xmlStr += '</e2service>'
		
				self.xmlStr += '</e2servicelist>'

				"""
				
				self.xmlStr = '<?xml version="1.0" encoding="UTF-8"?> '
				self.xmlStr += '<e2servicelist>'
				

				for row in self.result :
				# def makeRef( self, sid, tsid, onid ) :

					self.xmlStr += '<e2service>'
					self.xmlStr += '	<e2servicereference>' + self.makeRef(row[1], row[2], row[3]) + '</e2servicereference>'
					self.xmlStr += '	<e2servicename>' + row[0] + '</e2servicename>'
					self.xmlStr += '</e2service>'	

				self.xmlStr += '</e2servicelist>'

			except :

				self.xmlStr = '<?xml version="1.0" encoding="UTF-8"?>'
				self.xmlStr += '<e2servicelist>'

				self.xmlStr += '<e2service>'
				self.xmlStr += '</e2service>'
	
				self.xmlStr +='</e2servicelist>'
					
		else :

			sql = "select name from tblFavoriteGroup where serviceType=1"
			self.c.execute(sql)
			result = self.c.fetchall()
			
			self.xmlStr = '<?xml version="1.0" encoding="UTF-8"?>'
			self.xmlStr += '<e2servicelist>'

			for row in result :
				self.xmlStr += '<e2service>'
				self.xmlStr += '<e2servicereference>1:7:1:0:0:0:0:0:0:0:' + 'tblFavoriteChannel_GroupName_' + row[0] + '</e2servicereference>'
				self.xmlStr += '<e2servicename>' + row[0] + '</e2servicename>'
				self.xmlStr += '</e2service>'
	
			self.xmlStr +='</e2servicelist>'
						
		return self.xmlStr
		
