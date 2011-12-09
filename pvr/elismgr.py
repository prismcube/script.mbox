
import datetime
import socket
import time
from pvr.util import run_async
from pvr.eliscommander import ElisCommander
from pvr.net.net import EventServer, EventHandler, EventRequest
from pvr.elisevent import ElisEventBus
'''
, ElisAction, ElisEnum //by shinjh
'''
from pvr.elisaction import ElisAction
from pvr.elisenum import ElisEnum
import pvr.net.netconfig as netconfig
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
		print 'lael98 check already windowmgr is created'

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
			self.doEvent( event )
			print 'handle end --->!!!!!!!!!!!!!!!!!'
	

	def doEvent( self, event ):
		for i in range( len( event ) ):
			print 'received reply[%d] ---> %s' %(i,event[i])

		self.bus.publish( event )


class ElisEventRecevier( EventServer ): pass


class ElisMgr( object ):
	def __init__( self ):
		print 'lael98 check ElisMgr init'
		self.shutdowning = False
		self.eventBus = ElisEventBus()
		self.receiver = ElisEventRecevier(('', netconfig.receiverPort), ElisEventHandler )
		self.commander = ElisCommander( (netconfig.targetIp, netconfig.commanderPort) )		

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


