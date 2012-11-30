from datetime import datetime
from webinterface import Webinterface
import dbopen

class PrismCubeGetServices( Webinterface ) :

	def __init__(self, urlPath) :
	
		super(PrismCubeGetServices, self).__init__(urlPath)

		self.conn = dbopen.DbOpen('channel.db').getConnection()		
		self.c = self.conn.cursor()
		
	def xmlResult(self) :

		if 'sRef' in self.params :

			try :
				pass
				
			except :
				pass
					
		else :

			sql = "select name from tblFavoriteGroup where serviceType=1"
			self.c.execute(sql)
			result = self.c.fetchall()
			
			json = {}

			services = []
			for row in result:
				service = {}
				
				service["servicereference"] = '1:7:1:0:0:0:0:0:0:0:' + 'tblFavoriteChannel_GroupName_' + row[0]
				service["servicename"] = row[0]

				services.append( service )

			json["services"] = services
						
		return str( json ).replace("'", '"').replace('u"', '"')
		
