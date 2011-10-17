
import datetime
import socket
import time
from pvr.util import run_async
from pvr.net.net import EventServer, EventHandler, EventCommander, EventRequest
import pvr.elisevent as elisevent


__elismgr = None

def getInstance():
	global __elismgr
	if not __elismgr:
		print 'lael98 check create instance'
		__elismgr = ElisMgr()
	else:
		print 'lael98 check already windowmgr is created'

	return __elismgr



class ElisCommander( EventCommander ): pass

class ElisEventHandler( EventHandler ):
	def handle( self ):
		print 'lael98 check handle ElisEventHandler'
		request = EventRequest( self.request )
		while 1:
			print 'handle --->!!!!!!!!!!!!!!!!!'
			event = request.readMsg()
			self.doEvent( event )
			request.sendMsg(['OK'])

	def doEvent( self, event ):
		for i in range( len( event ) ):
			print 'received reply[%d] ---> %s' %(i,event[i])

		elisevent.publish( event )


class ElisEventRecevier( EventServer ): pass


class ElisMgr( object ):
	def __init__( self ):
		print 'lael98 check ElisMgr init'
		self.receiver = ElisEventRecevier(('', 12345), ElisEventHandler )

	@run_async
	def run( self ):
		print 'lael98 check ElisMgr run...'
		self.receiver.serve_forever()
		print 'lael98 check ElisMgr run2...'

	def shutdown( self ):
		print 'lael98 check ElisMgr shutdown...'
		self.receiver.shutdown()


