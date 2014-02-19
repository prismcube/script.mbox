from datetime import datetime
from webinterface import Webinterface
import dbopen
import time

class ElmoZap( Webinterface ) :

	def __init__(self, urlPath) :
	
		super(ElmoZap, self).__init__(urlPath)
		if 'sRef' in self.params :
			ref = self.unMakeRef( self.params['sRef'] )

			if ref:
				self.conn = dbopen.DbOpen('channel.db').getConnection()	
				sql = "select number from tblChannel where sid=" + str( ref['sid'] ) + " and tsid=" + str( ref['tsid'] ) + " and onid=" + str( ref['onid'] )
				self.c = self.conn.cursor()
				self.c.execute(sql)

				print sql

				self.result = self.c.fetchone()
				if self.result == None :
					self.result = False
			else : 
				self.result = False
				
		
	def xmlResult(self) :

		xmlStr = '<?xml version="1.0" encoding="UTF-8"?>'
		xmlStr += '<e2simplexmlresult>'
		
		if self.result : 
			#def Channel_SetCurrentSync( self, aChannelNumber, aServiceType, aFrontMessage = False ) :
			#if self.mDataCache.Channel_SetCurrent( self.result[0], 1 ) :
			
			if self.mDataCache.Channel_SetCurrentSync( self.result[0], 1, True ) :
				print 'channel zap to ' + str( self.result[0] )
				
				xmlStr += '<e2state>True</e2state>'
				# xmlStr += '<e2statetext>Active service switched to ' + self.params['sRef'] + '</e2statetext>'
				xmlStr += "<e2statetext>Active service is now 'the service'</e2statetext>"
			else :
				xmlStr += '<e2state>False</e2state>'
				xmlStr += '<e2statetext>Not switched to ' + self.params['sRef'] + '</e2statetext>'
		else :
			xmlStr += '<e2state>False</e2state>'
			xmlStr += '<e2statetext>Unable to switched to ' + self.params['sRef'] + '</e2statetext>'
				
		xmlStr += '</e2simplexmlresult>'

						
		return xmlStr
		
