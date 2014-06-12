class PrismCubeVersion( object ) :

	def __init__(self, path) :
		pass
	
	def xmlResult(self) :
		xmlStr = ''
		xmlStr += '<?xml version="1.0" encoding="UTF-8"?>\n'
		xmlStr += '<version>0.1.0</version>'

		return xmlStr

