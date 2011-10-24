
import datetime
import socket
import time
from pvr.util import run_async
from pvr.net.net import EventServer, EventHandler, EventCommander, EventRequest
from pvr.elisevent import ElisEventBus, ElisAction, ElisEnum
import threading
import select


__elismgr = None
__commander = None

targetIp	= '192.168.101.67'
myIp		= '192.168.101.69'

def getInstance():
	global __elismgr
	if not __elismgr:
		print 'lael98 check create instance'
		__elismgr = ElisMgr()
	else:
		print 'lael98 check already windowmgr is created'

	return __elismgr


def getCommander():
	global __commander
	if not __commander:
		print 'lael98 check create instance'
		__commander = ElisCommander( (targetIp, 12345) )
	else:
		print 'lael98 check already windowmgr is created'

	return __commander


class ElisCommander( EventCommander ): 
	"""
	args ['Command', 'ipAddress']
	retuns ['OK'] or ['KO']
	"""
	def setElisReady( self ) :
		req = []
		req.append( ElisAction.ElisReady )
		req.append( myIp )
		reply = self.command( req )
		print reply

	"""
	args ['Command', 'ChannelNumber', 'ServiceType']
	retuns ['OK'] or ['KO']
	"""
	def setCurrentChannel( self, number ):
		req = []
		req.append( ElisAction.SetCurrentChannel )
		req.append( '%d' %number )
		req.append( '%d' %ElisEnum.E_TYPE_TV )
		print req
		reply = self.command( req )
		print reply

class ElisEventHandler( EventHandler ):
	def handle( self ):
		print 'lael98 check handle ElisEventHandler'
		cur_thread = threading.currentThread()
		print "lael98 check threadname %s" % cur_thread.getName()

		request = EventRequest( self.request )
		self.bus = ElisEventBus()
		
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
#			request.sendMsg(['OK'])
	

	def doEvent( self, event ):
		for i in range( len( event ) ):
			print 'received reply[%d] ---> %s' %(i,event[i])

		self.bus.publish( event )


class ElisEventRecevier( EventServer ): pass


class ElisMgr( object ):
	def __init__( self ):
		print 'lael98 check ElisMgr init'
		self.shutdowning = False
		self.receiver = ElisEventRecevier(('', 54321), ElisEventHandler )

	@run_async
	def run( self ):
		print 'lael98 check ElisMgr run...'
		self.receiver.serve_forever()
		print 'lael98 check ElisMgr run2...'

	def shutdown( self ):
		print 'lael98 check ElisMgr shutdown...'
		self.shutdowning = True
		self.receiver.shutdown()


