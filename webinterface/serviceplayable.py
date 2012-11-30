from webinterface import Webinterface
import urllib

class ElmoServicePlayable( Webinterface ) :

	def __init__(self, urlPath) :
		super( ElmoServicePlayable, self ).__init__( urlPath )

	def xmlResult(self) :
		xmlStr = '<?xml version="1.0" encoding="UTF-8"?>'
            
 		#å{e2:convert type=web:ListFiller}
		xmlStr += '<e2serviceplayable>'
		xmlStr += '<e2servicereference>' + urllib.unquote( self.params['sRef'] ) + '</e2servicereference>'
		#xmlStr += '<e2servicereference>1:0:19:1324:3ef:1:C00000:0:0:0:</e2servicereference>'
		xmlStr += '<e2isplayable>True</e2isplayable>'
		xmlStr += '</e2serviceplayable>'
		#{/e2:convert}
	
		return xmlStr
