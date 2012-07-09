import xbmc, xbmcgui, time
import pvr.DataCacheMgr
from pvr.Util import TimeToString, TimeFormatEnum, RunThread
from util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR
import pvr.ElisMgr
from ElisEventClass import *


@RunThread
def StartTest( aScenario ) :
	time.sleep(0.5)
	xbmc.executebuiltin('xbmc.Action(previousmenu)')
	aScenario.DoCommand( )


class TestSuite( object ) :
	def __init__( self, aName, aValue ) :
		self.mDataCache = pvr.DataCacheMgr.GetInstance( )
		self.mName = aName
		self.mValue = aValue
		self.mChildList = []


	def AddChild( self, aChild ) :
		self.mChildList.append( aChild )


	def PrintStartTime( self ) :
		LOG_TRACE( 'Command Name=%s, value = %s, SendTime = %s' % ( self.mName, self.mValue, TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_HH_MM ) ) )


class TestScenario( TestSuite ) :
	def __init__( self, aName, aValue ) :
		TestSuite.__init__( self, aName, aValue )


	def DoCommand( self ) :
		for child in self.mChildList :
			if child :
				child.DoCommand( )


class LoopSuite( TestSuite ) :
	def __init__( self, aName, aValue ) :
		TestSuite.__init__( self, aName, aValue )


	def DoCommand( self ) :
		for i in range( int( self.mValue ) ) :
			for child in self.mChildList :
				if child :
					LOG_TRACE( 'Loop Count = %s' % i )
					child.DoCommand( )

		
class SendKeySuite( TestSuite ) :	
	def __init__( self, aName, aValue ) :
		TestSuite.__init__( self, aName, aValue )


	def DoCommand( self ) :
		self.PrintStartTime( )
		xbmc.executebuiltin( 'xbmc.Action(%s)' % self.mValue )


class SleepSuite( TestSuite ) :
	def __init__( self, aName, aValue ) :
		TestSuite.__init__( self, aName, aValue )


	def DoCommand( self ) :
		self.PrintStartTime( )
		time.sleep( float( self.mValue ) )


class WaitEventSuite( TestSuite ) :
	def __init__( self, aName, aValue ) :
		TestSuite.__init__( self, aName, aValue )
		self.mEndEvent = False
		self.mEventBus = pvr.ElisMgr.GetInstance( ).GetEventBus( )
		self.mEventName = self.MappingEventName( aValue )


	def DoCommand( self ) :
		self.PrintStartTime( )
		LOG_TRACE( '' )
		otrinfo = self.mDataCache.Timer_GetOTRInfo( )
		LOG_TRACE('====================================')
		LOG_TRACE('====================================')
		otrinfo.printdebug( )
		LOG_TRACE('====================================')
		LOG_TRACE('====================================')
		self.mEventBus.Register( self )
		LOG_TRACE( 'Start Wait Event !!!! ' )
		while self.mEndEvent == False :
			print 'dhkim test wait event.....'
			time.sleep(1)
		self.mEventBus.Deregister( self )
		LOG_TRACE( 'End Wait Event !!!! ' )
		otrinfo.printdebug( )


	@classmethod
	def GetName( cls ) :
		return cls.__name__


	def onEvent( self, aEvent ) :
		if aEvent.getName( ) == self.mEventName :
			self.mEndEvent = True


	def MappingEventName( self, aValue ) :
		if aValue == 'stoprecord' :
			print 'dhkim test event name mapping record'
			return ElisEventRecordingStopped.getName( )

			
