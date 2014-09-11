from datetime import datetime
from webinterface import Webinterface
import dbopen
import urllib
from xml.sax.saxutils import escape, unescape

class ElmoGetServices( Webinterface ) :

	def __init__(self, urlPath) :
	
		# super(ElmoGetServices, self).__init__(urlPath)
		super(ElmoGetServices, self).__init__()

		# getservices has only sRef parameter, so let's just take care of it here
		if len( urlPath.split("?") ) == 2 :
			param = urlPath.split("?")[1]
			self.params['sRef'] = urllib.unquote( param[5:] )

		print self.params

		self.conn = dbopen.DbOpen('channel.db').getConnection()		
		self.c = self.conn.cursor()

		# defilne custom characters
		self.space = "]][["
		
	def xmlResult(self) :

		if 'sRef' in self.params :

			try :
				print 'sRef is '
				print urllib.unquote( self.params['sRef'] )
				print self.params
				
				sRefParams = self.unMakeRef(self.params['sRef'])
				conditions = sRefParams['comment'].split('_')

				if len(conditions) == 3 : 
					sql = "select name, sid, tsid, onid, number as key  from " + conditions[0] + " where " + conditions[1] + " = '" + self.escapeMinus( conditions[2] ) + "'"
					self.makeChannelListXML( sql )
					
				elif "bouquets.radio" in self.params['sRef'] : 
					# Radio channels in Favorite folder
					sql = "select name from tblFavoriteGroup where serviceType=2 or serviceType=4"
					self.makeFavoriteFolderXML( sql )
					
				elif "(type+==+2)" in self.params['sRef'] :
					# all Radio channels
					sql = "select name, sid, tsid, onid, number as key from tblChannel where serviceType=2 or serviceType=4 order by name"
					self.makeChannelListXML( sql )
					
				else :
					# if conditions are not met, assume user asks for all channels. 
					sql = "select name, sid, tsid, onid, number as key from tblChannel where serviceType=1 or serviceType=3 order by name"
					self.makeChannelListXML( sql )

			except Exception, e:
				print str(e)
				self.noResult()
					
		else :
			
			sql = "select name from tblFavoriteGroup where serviceType=1 or serviceType=3"
			self.makeFavoriteFolderXML( sql )
						
		return self.xmlStr

	def makeFavoriteFolderXML(self, sql) :

		print '[getservices - folder]' + sql
		
		self.c.execute(sql)
		result = self.c.fetchall()
			
		self.xmlStr = '<?xml version="1.0" encoding="UTF-8"?>\n'
		self.xmlStr += '<e2servicelist>\n'

		for row in result :
		
			self.xmlStr += '<e2service>\n'
			# self.xmlStr += '<e2servicereference>1:7:1:0:0:0:0:0:0:0:' + 'tblFavoriteChannel_GroupName_' + urllib.quote( row[0] ) + '</e2servicereference>\n'
			self.xmlStr += '<e2servicereference>1:7:1:0:0:0:0:0:0:0:' + 'tblFavoriteChannel_GroupName_' + self.escapePlus( row[0] ) + '</e2servicereference>\n'
			self.xmlStr += '<e2servicename>' + escape(row[0]) + '</e2servicename>\n'
			self.xmlStr += '</e2service>\n'
	
		self.xmlStr +='</e2servicelist>\n'

	def makeChannelListXML(self, sql) :

		print '[getservices - list]' + sql
		
		self.c.execute(sql)
		result = self.c.fetchall()

		print result
			
		self.xmlStr = '<?xml version="1.0" encoding="UTF-8"?>\n'
		self.xmlStr += '<e2servicelist>\n'

		for row in result :
		
			self.xmlStr += '<e2service>\n'
			self.xmlStr += '	<e2servicereference>' + self.makeRef( row[1], row[2],  row[3] ) + '</e2servicereference>\n'
			self.xmlStr += '	<e2servicename>' + escape(row[0]) + '</e2servicename>\n'
			self.xmlStr += '	<key>' + str(row[4]) + '</key>\n'
			self.xmlStr += '</e2service>\n'	
	
		self.xmlStr +='</e2servicelist>\n'

	def noResult(self) :

		self.xmlStr = '<?xml version="1.0" encoding="UTF-8"?>\n'
		self.xmlStr += '<e2servicelist>\n'

		self.xmlStr += '<e2service></e2service>\n'
	
		self.xmlStr +='</e2servicelist>\n'

	def escapePlus(self, name) :

		tempName = escape(name)
		return tempName.replace(" ", self.space)

	def escapeMinus(self, name) : #aka unEscapePlus()

		tempName = name.replace(self.space, " ")
		return unescape(tempName)
		
