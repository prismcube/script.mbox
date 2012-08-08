import datetime
import socket
import time
from pvr.Util import RunThread
from util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR
from ElisCommander import ElisCommander
from net.Net import EventServer, EventHandler, EventRequest
from ElisEventClass import *
from ElisEventBus import ElisEventBus
from ElisAction import ElisAction
from ElisEnum import ElisEnum
import pvr.NetConfig as NetConfig
import threading
import select


gElisMgr = None


def GetInstance( ) :
	global gElisMgr
	if not gElisMgr :
		gElisMgr = ElisMgr( )
	else :
		pass
	return gElisMgr


class ElisEventHandler( EventHandler ) :
	def handle( self ) :
		cur_thread = threading.currentThread( )
		LOG_TRACE( 'check threadname %s' % cur_thread.getName( ) )

		request = EventRequest( self.request )
		self.mEventBus = GetInstance( ).GetEventBus( )
		
		while 1 :
			fd_sets = select.select( [ self.request ], [], [], 0.5 )
			if not fd_sets[0] :
				if GetInstance( ).mShutdowning :
					break
				else :
					continue

			read = request.ReadMsg( )
			event = ElisEvent.ParseElisEvent( read )
			self.AddEvent( event )
	

	def AddEvent( self, aEvent ) :
		self.mEventBus.AddEvent( aEvent )


class ElisEventRecevier( EventServer ) :
	pass


class ElisMgr( object ) :
	def __init__( self ) :
		self.mShutdowning = False
		self.mEventBus = ElisEventBus( )
		LOG_TRACE( 'check test netconfig.receiverPort = %d' % NetConfig.receiverPort )		
		self.mReceiver = ElisEventRecevier( ( '', NetConfig.receiverPort ), ElisEventHandler )
		LOG_TRACE( 'check test netconfig.targetIp = %s netconfig.commanderPort = %d' % ( NetConfig.targetIp, NetConfig.commanderPort ) )
		self.mCommander = ElisCommander( ( NetConfig.targetIp, NetConfig.commanderPort ) )
		

	def GetCommander( self ) :
		return self.mCommander


	def GetEventBus( self ) :
		return self.mEventBus
	

	@RunThread
	def Run( self ) :
		LOG_TRACE( 'lael98 check ElisMgr run1...' )
		self.mReceiver.serve_forever()
		LOG_TRACE( 'lael98 check ElisMgr run2...' )


	def Shutdown( self ) :
		LOG_TRACE( 'lael98 check ElisMgr shutdown...' )
		self.mShutdowning = True
		self.mReceiver.shutdown( )

