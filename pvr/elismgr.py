
import datetime
import socket
import time
from pvr.util import run_async
from eliscommander import ElisCommander
from net.net import EventServer, EventHandler, EventRequest
from elisevent import ElisEventBus
from elisaction import ElisAction
from elisenum import ElisEnum
import pvr.netconfig as netconfig
import threading
import select


__elismgr = None
__commander = None


def getInstance():
	global __elismgr
	if not __elismgr:
		print 'lael98 check create instance'
		__elismgr = ElisMgr()
	else:
		pass
		#print 'lael98 check already windowmgr is created'

	return __elismgr


class ElisEventHandler( EventHandler ):
	def handle( self ):
		print 'lael98 check handle ElisEventHandler'
		cur_thread = threading.currentThread()
		print "lael98 check threadname %s" % cur_thread.getName()

		request = EventRequest( self.request )
		self.bus = getInstance().getEventBus()
		
		while 1:
			print 'handle --->!!!!!!!!!!!!!!!!!'

			fd_sets = select.select([self.request], [], [], 0.5 )
			if not fd_sets[0]:
				if getInstance().shutdowning:
					break
				else :
					continue

			event = request.readMsg()
			self.addEvent( event )
			print 'handle end --->!!!!!!!!!!!!!!!!!'
	

	def addEvent( self, event ):
		self.bus.addEvent( event )


class ElisEventRecevier( EventServer ): pass


class ElisMgr( object ):
	def __init__( self ):
		print 'lael98 check ElisMgr init'
		self.shutdowning = False
		self.eventBus = ElisEventBus()
		print 'check test'
		print 'check test netconfig.receiverPort=%d' %netconfig.receiverPort		
		self.receiver = ElisEventRecevier(('', netconfig.receiverPort), ElisEventHandler )
		print 'check test netconfig.targetIp=%s netconfig.commanderPort=%d' %(netconfig.targetIp, netconfig.commanderPort)
		self.commander = ElisCommander( (netconfig.targetIp, netconfig.commanderPort) )		
		print 'check test'

	def getCommander( self ):
		return self.commander

	def getEventBus( self ):
		return self.eventBus
	

	@run_async
	def run( self ):
		print 'lael98 check ElisMgr run...'
		self.receiver.serve_forever()
		print 'lael98 check ElisMgr run2...'

	def shutdown( self ):
		print 'lael98 check ElisMgr shutdown...'
		self.shutdowning = True
		self.receiver.shutdown()


