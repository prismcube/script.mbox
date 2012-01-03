
import datetime
import socket
import time
from pvr.Util import RunThread
from ElisCommander import ElisCommander
from net.Net import EventServer, EventHandler, EventRequest
from ElisEvent import ElisEventBus
from ElisAction import ElisAction
from ElisEnum import ElisEnum
import pvr.NetConfig as NetConfig
import threading
import select


gElisMgr = None


def GetInstance():
	global gElisMgr
	if not gElisMgr:
		print 'lael98 check create instance'
		gElisMgr = ElisMgr()
	else:
		pass
		#print 'lael98 check already windowmgr is created'

	return gElisMgr


class ElisEventHandler( EventHandler ):
	def handle( self ):
		print 'lael98 check handle ElisEventHandler'
		cur_thread = threading.currentThread()
		print "lael98 check threadname %s" % cur_thread.getName()

		request = EventRequest( self.request )
		self.mEventBus = GetInstance().GetEventBus()
		
		while 1:
			print 'handle --->!!!!!!!!!!!!!!!!!'

			fd_sets = select.select([self.request], [], [], 0.5 )
			if not fd_sets[0]:
				if GetInstance().mShutdowning:
					break
				else :
					continue

			event = request.readMsg()
			self.AddEvent( event )
			print 'handle end --->!!!!!!!!!!!!!!!!!'
	

	def AddEvent( self, aEvent ):
		self.mEventBus.AddEvent( aEvent )


class ElisEventRecevier( EventServer ): pass


class ElisMgr( object ):
	def __init__( self ):
		print 'lael98 check ElisMgr init'
		self.mShutdowning = False
		self.mEventBus = ElisEventBus()
		print 'check test'
		print 'check test netconfig.receiverPort=%d' %NetConfig.receiverPort		
		self.mReceiver = ElisEventRecevier(('', NetConfig.receiverPort), ElisEventHandler )
		print 'check test netconfig.targetIp=%s netconfig.commanderPort=%d' %(NetConfig.targetIp, NetConfig.commanderPort)
		self.mCommander = ElisCommander( (NetConfig.targetIp, NetConfig.commanderPort) )		
		print 'check test'

	def GetCommander( self ):
		return self.mCommander

	def GetEventBus( self ):
		return self.mEventBus
	

	@RunThread
	def Run( self ):
		print 'lael98 check ElisMgr run...'
		self.mReceiver.serve_forever()
		print 'lael98 check ElisMgr run2...'

	def Shutdown( self ):
		print 'lael98 check ElisMgr shutdown...'
		self.mShutdowning = True
		self.mReceiver.shutdown()


