from datetime import datetime
from webinterface import Webinterface

class ElmoCurrentTime( Webinterface ) :

	def __init__(self, urlPath) :
		super(ElmoCurrentTime, self).__init__(urlPath)
		self.currenttime = datetime.fromtimestamp( self.mDataCache.Datetime_GetLocalTime() )

	def xmlResult(self) :
		
		xmlstr = '<?xml version="1.0" encoding="UTF-8"?>\n'
		xmlstr += '<e2currenttime>\n'
		xmlstr += 	str(self.currenttime.hour) + ':' + str(self.currenttime.minute) + ':' + str(self.currenttime.second)
		xmlstr += '</e2currenttime>\n'

		print self.currenttime
		print self.mDataCache.Datetime_GetLocalTime()
	
		return xmlstr
