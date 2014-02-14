import dbopen
from webinterface import Webinterface

class ElmoGetLocations( Webinterface ) :

	def __init__( self, urlPath ) :
	
		super( ElmoGetLocations, self ).__init__( urlPath )
		
	def xmlResult( self ) :
	
		xmlstr = '<?xml version="1.0" encoding="UTF-8"?>\n'
		xmlstr += '<e2locations>\n'
   		xmlstr += '	<e2location>Archive</e2location>\n'
		xmlstr += '</e2locations>\n'

		return xmlstr
