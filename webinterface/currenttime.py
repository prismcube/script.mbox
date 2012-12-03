from datetime import datetime
from webinterface import Webinterface

class ElmoCurrentTime( Webinterface ) :

	def __init__(self, urlPath) :
		super(ElmoCurrentTime, self).__init__(urlPath)
		self.currenttime = datetime.fromtimestamp( self.mDataCache.Datetime_GetLocalTime() )

	def xmlResult(self) :
		xml = ''
		xmlstr = '<?xml version="1.0" encoding="UTF-8"?>';
		xmlstr += '<e2currenttime>';
		xmlstr += 	str(self.currenttime.hour) + ':' + str(self.currenttime.minute) + ':' + str(self.currenttime.second);
		xmlstr += '</e2currenttime>';
	
		return xmlstr
