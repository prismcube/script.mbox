import time
import pvr.DataCacheMgr
import pvr.gui.WindowMgr as WinMgr
from pvr.Util import RunThread


gHiddenTestMgr = None


def GetInstance( ) :
	global gHiddenTestMgr
	if not gHiddenTestMgr:
		gHiddenTestMgr = HiddenTestMgr( )
	else:
		pass

	return gHiddenTestMgr


class HiddenTestMgr( object ) :
	def __init__( self ) :
		self.mDataCache = pvr.DataCacheMgr.GetInstance( )
		self.mStopflag = False
		self.mZappingTime = 5


	def ZappingTestEPG( self ) :
		self.mStopflag = True
		self.StartZapping( )
		WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EPG_WINDOW, WinMgr.WIN_ID_MAINMENU )
		

	def SetZappingTime( self, aTime ) :
		self.mZappingTime = aTime


	@RunThread
	def StartZapping( self ) :
		current = self.mDataCache.Channel_GetCurrent( )
		while self.mStopflag :
			nextChannel = self.mDataCache.Channel_GetNext( current )
			self.mDataCache.Channel_SetCurrent( nextChannel.mNumber, nextChannel.mServiceType )
			self.mDataCache.Epgevent_GetPresent( )
			current = nextChannel
			time.sleep( self.mZappingTime )


	def CheckAndStopTest( self ) :
		if self.mStopflag :
			self.mStopflag = False
			self.StartZapping( ).join( )
			