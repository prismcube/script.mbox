from datetime import datetime
from webinterface import Webinterface
import dbopen

class PrismCubeZap( Webinterface ) :

	def __init__(self, urlPath) :
	
		super(PrismCubeZap, self).__init__(urlPath)
		if 'sRef' in self.params :
			ref = self.unMakeRef( self.params['sRef'] )

			if ref:
				self.conn = dbopen.DbOpen('channel.db').getConnection()	
				sql = "select number from tblChannel where sid=" + str( ref['sid'] ) + " and tsid=" + str( ref['tsid'] ) + " and onid=" + str( ref['onid'] )
				self.c = self.conn.cursor()
				self.c.execute(sql)

				self.result = self.c.fetchone()
				if self.result == None :
					self.result = False
			else : 
				self.result = False
				
		
	def xmlResult(self) :

		json = {}
		
		if self.result : 
			if self.mDataCache.Channel_SetCurrent( self.result[0], 1 ) :
				print 'channel zap to ' + str( self.result[0] )
				
				json["message"] = 'Active service switched to ' + self.params['sRef'] 
				json["result"] = True
				
			else :
				json["message"] = 'Active service not switched to ' + self.params['sRef'] 
				json["result"] = False
		else :
			json["message"] = 'Active service not switched to ' + self.params['sRef'] 
			json["result"] = False
								
		return str( json ).replace("'", '"').replace('T', 't').replace('F', 'f')
		
