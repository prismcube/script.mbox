import dbopen
from webinterface import Webinterface

class ElmoMovieList( Webinterface ) :

	def __init__(self, urlPath) :
		super(ElmoMovieList, self).__init__(urlPath)
		self.conn = dbopen.DbOpen('recordinfo.db').getConnection()

		sql = "select ChannelName, RecordName, StartTime, duration  from tblRecordInfo"
		self.c = self.conn.cursor()
		self.c.execute(sql)

		self.results = self.c.fetchall()
		print self.results
		
	def xmlResult(self) :
	
		xmlstr = '<?xml version="1.0" encoding="UTF-8"?>'
		xmlstr += '<e2movielist>'

		for row in self.results :
			xmlstr += '  <e2movie>'
			xmlstr += '      <e2servicereference>1:0:0:0</e2servicereference>'
			xmlstr += '      <e2title>'+row[1]+'</e2title>'

			xmlstr += '      <e2description/>'
			xmlstr += '      <e2descriptionextended/>'
			# xmlstr += '      <e2servicename>'+row[0]+'</e2servicename>'
			xmlstr += '      <e2servicename>ElmoStation</e2servicename>'
			xmlstr += '      <e2time>'+str( row[2] )+'</e2time>'
			xmlstr += '      <e2length>'+self.DurationInHMS( row[3] )+'</e2length>'
			xmlstr += '      <e2tags></e2tags>'
			xmlstr += '      <e2filename>FileFormat.ts</e2filename>'
			xmlstr += '      <e2filesize>1000</e2filesize>'
			xmlstr += '   </e2movie>'
		
		xmlstr += '</e2movielist>'

		return xmlstr

	def DurationInHMS(self, duration) :
	
		theHour = int( duration / 3600 )
		duration = duration % 3600
		theMin = int( duration / 60 )
		theSec = duration % 60

		return str( theHour ) + ':' + str( theMin ) + ':' + str( theSec )
		