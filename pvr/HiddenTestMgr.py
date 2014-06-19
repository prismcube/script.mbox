import xbmc, xbmcgui, time, socket, struct, random, sys, inspect
import pvr.DataCacheMgr
from pvr.Util import TimeToString, TimeFormatEnum, RunThread
from elisinterface.util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR
import pvr.ElisMgr
from elisinterface.ElisEventClass import *


KeyCode = {
	'KEY_FROM_NONE' : 0,
	'KEY_FROM_RCU' : 1,
	'KEY_FROM_TACT' : 2,
	'KEY_FROM_FRONTWHEEL' : 3,

	'FLAG_NONE' : 0,
	'FLAG_REPEATED' : 1,
	
	'VKEY_NO_KEY' : 0,
	'VKEY_OK' : 1,
	'VKEY_UP' : 2,
	'VKEY_DOWN' : 3,
	'VKEY_LEFT' : 4,
	'VKEY_RIGHT' : 5,
	'VKEY_RED' : 6,
	'VKEY_GREEN' : 7,
	'VKEY_YELLOW' : 8,
	'VKEY_BLUE' : 9,
	'VKEY_0' : 10,

	'VKEY_1' : 11,
	'VKEY_2' : 12,
	'VKEY_3' : 13,
	'VKEY_4' : 14,
	'VKEY_5' : 15,
	'VKEY_6' : 16,
	'VKEY_7' : 17,
	'VKEY_8' : 18,
	'VKEY_9' : 19,
	'VKEY_FF' : 20,

	'VKEY_REV' : 21,
	'VKEY_PLAY' : 22,
	'VKEY_REC' : 23,
	'VKEY_PAUSE' : 24,
	'VKEY_STOP' : 25,
	'VKEY_SLOW' : 26,
	'VKEY_MENU' : 27,
	'VKEY_EPG' : 28,
	'VKEY_TEXT' : 29,
	'VKEY_INFO' : 30,

	'VKEY_BACK' : 31,
	'VKEY_EXIT' : 32,
	'VKEY_POWER' : 33,
	'VKEY_MUTE' : 34,
	'VKEY_PROG_UP' : 35,
	'VKEY_PROG_DOWN' : 36,
	'VKEY_VOL_UP' : 37,
	'VKEY_VOL_DOWN' : 38,
	'VKEY_HELP' : 39,
	'VKEY_MEDIA' : 40,

	'VKEY_ARCHIVE' : 41,
	'VKEY_PREVCH' : 42,
	'VKEY_FAVORITE' : 43,
	'VKEY_OPT' : 44,
	'VKEY_PIP' : 45,
	'VKEY_SLEEP' : 46,
	'VKEY_HISTORY' : 47,
	'VKEY_ADDBOOKMARK' : 48,
	'VKEY_BMKWINDOW' : 49,
	'VKEY_JUMP_FORWARD' : 50,

	'VKEY_JUMP_BACKWARD' : 51,
	'VKEY_TV_RADIO' : 52,

	'VKEY_SUBTITLE' : 53,
	'VKEY_STAR' : 54,
	'VKEY_CHECK' : 55,
	'VKEY_SEARCH' : 56,
	'VKEY_EDIT' : 57,
	'VKEY_DELETE' : 58,
	'VKEY_FUNC_A' : 59,
	'VKEY_FUNC_B' : 60,

	'VKEY_VOD_TIMESHIFT' : 61,
	'VKEY_ADULT' : 62,
	'VKEY_VOD' : 63,
	'VKEY_SOURCE' : 64, 
	'VKEY_VFORMAT' : 65,
	'VKEY_AFORMAT' : 66,
	'VKEY_WIDE' : 67,
	'VKEY_LIST' : 68,


	'VKEY_FRONT_MENU' : 0x80,
	'VKEY_FRONT_EXIT' : 0x81,
	'VKEY_FRONT_AUX' : 0x82,
	'VKEY_FRONT_TV_R' : 0x83,
	'VKEY_FRONT_OK' : 0x84,
	'VKEY_FRONT_CCW' : 0x85,
	'VKEY_FRONT_CW' : 0x86
}


PORT = 56892
sock = None


def ConnectSocket( ) :
	global sock
	try :
		sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	except socket.error, msg :
		print 'create socket error %s' % msg[1]
		return False
	 
	try :
		sock.connect( ( '127.0.0.1', PORT + 10 ) )
	except socket.error, msg :
		print 'connect socket error %s' % msg[1]
		return False
	return True


def CloseSocket( ) :
	sock.close( )


def SendCommand( aCmd ) :
	if ConnectSocket( ) :
		msg = struct.pack( '3i', *[ 1, KeyCode[ aCmd ], 0 ] )
		sock.send( msg )
		CloseSocket( )


@RunThread
def StartTest( aScenario ) :
	time.sleep( 0.5 )
	xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )
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


	def CloseTestProgram( self ) :
		sock.close( )
		self.mChildList = []


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
		if self.mDataCache.GetRunningHiddenTest( ) == False :
			self.CloseTestProgram( )
		self.PrintStartTime( )
		msg = struct.pack( '3i', *[ 1, KeyCode[ self.mValue ], 0 ] )
		sock.send( msg )
		#xbmc.executebuiltin( 'xbmc.Action(%s)' % self.mValue )


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
		otrinfo = self.mDataCache.Timer_GetOTRInfo( )
		otrinfo.printdebug( )
		self.mEventBus.Register( self )
		LOG_TRACE( 'Start Wait Event !!!! ' )
		while self.mEndEvent == False :
			LOG_TRACE( 'TEST MGR wait event...')
			time.sleep( 1 )
		self.mEventBus.Deregister( self )
		LOG_TRACE( 'End Wait Event !!!!' )
		otrinfo.printdebug( )


	@classmethod
	def GetName( cls ) :
		return cls.__name__


	def onEvent( self, aEvent ) :
		if aEvent.getName( ) == self.mEventName :
			self.mEndEvent = True


	def MappingEventName( self, aValue ) :
		if aValue == 'stoprecord' :
			return ElisEventRecordingStopped.getName( )


class SendEventSuite( TestSuite ) :
	def __init__( self, aName, aValue ) :
		TestSuite.__init__( self, aName, aValue )
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.mEventName = aValue


	def DoCommand( self ) :
		if self.mEventName == 'settestmode' :
			self.mCommander.Stress_Test_Mode( 1 )


@RunThread
def StartTest2( aScenario ) :
	time.sleep( 0.5 )
	xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )
	aScenario.StartTestAll( )

import pvr.gui.WindowMgr as WinMgr
gDenyWinid = [ 
	WinMgr.WIN_ID_ROOTWINDOW, 
	WinMgr.WIN_ID_NULLWINDOW, 
	WinMgr.WIN_ID_ANTENNA_SETUP,
	WinMgr.WIN_ID_TUNER_CONFIGURATION,
	WinMgr.WIN_ID_CONFIG_SIMPLE,
	WinMgr.WIN_ID_CONFIG_MOTORIZED_12,
	WinMgr.WIN_ID_CONFIG_MOTORIZED_USALS,
	WinMgr.WIN_ID_CONFIG_ONECABLE,
	WinMgr.WIN_ID_CONFIG_ONECABLE_2,
	WinMgr.WIN_ID_CONFIG_DISEQC_10,
	WinMgr.WIN_ID_CONFIG_DISEQC_11,
	11,
	WinMgr.WIN_ID_CONFIG_ONECABLE_2, 
	WinMgr.WIN_ID_CHANNEL_SEARCH, 
	WinMgr.WIN_ID_AUTOMATIC_SCAN,
	WinMgr.WIN_ID_MANUAL_SCAN,
	WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW, 
	WinMgr.WIN_ID_FIRST_INSTALLATION, 
	WinMgr.WIN_ID_HIDDEN_TEST
	]


gTestWinid = [ 
	WinMgr.WIN_ID_MAINMENU,
	WinMgr.WIN_ID_CHANNEL_LIST_WINDOW,
	WinMgr.WIN_ID_LIVE_PLATE,
	WinMgr.WIN_ID_CONFIGURE,
	WinMgr.WIN_ID_ARCHIVE_WINDOW,
	WinMgr.WIN_ID_SYSTEM_INFO,
	WinMgr.WIN_ID_EPG_WINDOW,
	#WinMgr.WIN_ID_TIMESHIFT_PLATE,
	#WinMgr.WIN_ID_INFO_PLATE,
	#WinMgr.WIN_ID_FAVORITE_ADDONS,
	#WinMgr.WIN_ID_SYSTEM_UPDATE,
	#WinMgr.WIN_ID_HELP
	]


class AllNavigation( object ) :
	def __init__( self, *args, **kwargs ) :
		self.mDataCache = pvr.DataCacheMgr.GetInstance( )
		self.mTestCount = 0
		self.mStartTime = time.time()


	def StartTestAll( self ) :
		testCount = 0
		testTime = 0
		testSleep = 5
		time.sleep( testSleep )
		while self.mDataCache.GetRunningHiddenTest( ) :
			for winid in gTestWinid :
				if not self.mDataCache.GetRunningHiddenTest( ) :
					break

				if self.CheckWindow( testSleep ) :
					continue

				code = None
				if winid == WinMgr.WIN_ID_MAINMENU :
					code = KeyCode[ 'VKEY_MENU' ]
				elif winid == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
					code = KeyCode[ 'VKEY_OK' ]
				elif winid == WinMgr.WIN_ID_LIVE_PLATE :
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( False )
					code = KeyCode[ 'VKEY_INFO' ]
				elif winid == WinMgr.WIN_ID_ARCHIVE_WINDOW :
					code = KeyCode[ 'VKEY_ARCHIVE' ]
				elif winid == WinMgr.WIN_ID_EPG_WINDOW :
					code = KeyCode[ 'VKEY_EPG' ]

				LOG_TRACE('------sock[%s] key[%s]'% ( sock, code ) )
				WinMgr.GetInstance( ).ShowWindow( winid )
				#if code :
				#	msg = struct.pack( '3i', *[ 1, code, 0 ] )
				#	sock.send( msg )

				time.sleep( testSleep )

				testTime += testSleep
				testCount += 1
				self.PrintLog( testCount, testTime )
				xbmc.executebuiltin( 'xbmc.Action(PreviousMenu)' )
				time.sleep(1)

				if WinMgr.GetInstance( ).GetLastWindowID( ) > WinMgr.WIN_ID_NULLWINDOW :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
					#msg = struct.pack( '3i', *[ 1, KeyCode[ 'VKEY_BACK' ], 0 ] )
					#sock.send( msg )
					time.sleep( testSleep )


			if not self.mDataCache.GetRunningHiddenTest( ) :
				break

			msg = struct.pack( '3i', *[ 1, KeyCode[ 'VKEY_PLAY' ], 0 ] )
			xbmc.executebuiltin( 'xbmc.Action(play)' )
			#sock.send( msg )
			time.sleep( 2 )
			testTime += 2
			testCount += 1
			self.PrintLog( testCount, testTime )

			msg = struct.pack( '3i', *[ 1, KeyCode[ 'VKEY_INFO' ], 0 ] )
			xbmc.executebuiltin( 'xbmc.Action(contextmenu)' )
			#sock.send( msg )
			time.sleep( testSleep )
			testTime += testSleep
			testCount += 1
			self.PrintLog( testCount, testTime )

			msg = struct.pack( '3i', *[ 1, KeyCode[ 'VKEY_STOP' ], 0 ] )
			xbmc.executebuiltin( 'xbmc.Action(stop)' )
			#sock.send( msg )
			time.sleep( testSleep )
			testTime += testSleep
			testCount += 1
			self.PrintLog( testCount, testTime )

		self.CloseTestProgram( )


	def PrintLog( self, testCount, testTime ) :
		testTime = '%02d:%s'% ( testTime / 3600, time.strftime('%M:%S', time.gmtime(testTime) ) )
		currT = time.strftime('%H:%M', time.gmtime(time.time()) )
		currS = time.strftime('%H:%M', time.gmtime(self.mStartTime) )
		LOG_TRACE( '--------- Loop Count[%s] TestTime[%s] curr[%s] start[%s] testwin[%s]'% ( testCount, testTime, currT, currS, WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).GetLastWindowID( ) ).GetName( ) ) )
		currentStack = inspect.stack( )
		LOG_TRACE( '+++++getrecursionlimit[%s] currentStack[%s] StackCount[%s] StackType[%s]'% (sys.getrecursionlimit( ), len(currentStack), currentStack.count, type(currentStack) ) )


	def CheckWindow( self, aSleep ) :
		ret = False
		#LOG_TRACE('-----------activate win[%s]'% xbmcgui.getCurrentWindowId( ) )
		if WinMgr.GetInstance( ).GetLastWindowID( ) > WinMgr.WIN_ID_NULLWINDOW :
			LOG_TRACE('---Reset NullWindow (lastid[%s])'% WinMgr.GetInstance( ).GetLastWindowID( ) )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
			time.sleep( aSleep )
			ret = True

		return ret


	def CloseTestProgram( self ) :
		sock.close( )


