import dbopen
from webinterface import Webinterface
from xml.sax.saxutils import escape, unescape

class ElmoMovieList( Webinterface ) :

	def __init__(self, urlPath) :
		super(ElmoMovieList, self).__init__(urlPath)
		self.conn = dbopen.DbOpen('recordinfo.db').getConnection()

		sql = "select ChannelName, RecordName, StartTime, duration, RecordKey  from tblRecordInfo where serviceType=1 or serviceType=3"
		self.c = self.conn.cursor()
		self.c.execute(sql)

		self.results = self.c.fetchall()
		print self.results
		
	def xmlResult(self) :
	
		xmlstr = '<?xml version="1.0" encoding="UTF-8"?>\n'
		xmlstr += '<e2movielist>\n'

		for row in self.results :
			xmlstr += '  <e2movie>\n'
			xmlstr += '      <e2servicereference>1:0:0:0:0:0:0:0:0:0:/Archive/' + str(row[4]) +'</e2servicereference>\n'
			xmlstr += '      <e2title>'+escape(row[1])+'</e2title>\n'

			xmlstr += '      <e2description/>\n'
			xmlstr += '      <e2descriptionextended/>\n'
			xmlstr += '      <e2servicename>'+escape(row[0])+'</e2servicename>\n'
			# xmlstr += '      <e2servicename>ElmoStation</e2servicename>'
			xmlstr += '      <e2time>'+str( row[2] )+'</e2time>\n'
			xmlstr += '      <e2length>'+self.DurationInHMS( row[3] )+'</e2length>\n'
			xmlstr += '      <e2tags></e2tags>\n'
			xmlstr += '      <e2filename>' + str(row[4]) + '</e2filename>\n'
			xmlstr += '      <e2filesize>0</e2filesize>\n'
			xmlstr += '   </e2movie>\n'
		
		xmlstr += '</e2movielist>\n'

		return xmlstr

	def DurationInHMS(self, duration) :
	
		theHour = int( duration / 3600 )
		duration = duration % 3600
		theMin = int( duration / 60 )
		theSec = duration % 60

		return str( theHour ) + ':' + str( theMin ) + ':' + str( theSec )
		