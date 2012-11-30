from datetime import datetime
from webinterface import Webinterface
import dbopen

class PrismCubeServicesm3u( Webinterface ) :

	def __init__(self, urlPath) :
	
		super(PrismCubeServicesm3u, self).__init__(urlPath)
		
		self.conn = dbopen.DbOpen('channel.db').getConnection()	
		"""
		sql = "select number from tblChannel where sid=" + str( ref['sid'] ) + " and tsid=" + str( ref['tsid'] ) + " and onid=" + str( ref['onid'] )
		self.c = self.conn.cursor()
		self.c.execute(sql)

		self.result = self.c.fetchone()
		if self.result == None :
			self.result = False
		else : 
			self.result = False
		"""		
		
	def xmlResult(self) :

		json = {}
		
		return '{"services": [{"servicereference": "1:7:1:0:0:0:0:0:0:0:FROM BOUQUET", "servicename": "Favourites (TV)"}], "host": "192.168.100.158:8001"}'
		
