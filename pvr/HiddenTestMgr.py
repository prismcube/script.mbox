import xbmc, xbmcgui, time
import pvr.DataCacheMgr
from pvr.Util import TimeToString, TimeFormatEnum, RunThread
from util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR


gHiddenTestMgr = None


def GetInstance( ) :
	global gHiddenTestMgr
	if not gHiddenTestMgr :
		gHiddenTestMgr = HiddenTestMgr( )
	else:
		pass

	return gHiddenTestMgr


class HiddenTestMgr( object ) :
	def __init__( self ) :
		self.mDataCache = pvr.DataCacheMgr.GetInstance( )


	@RunThread
	def StartTest( self, aScenario ) :
		xbmc.executebuiltin('xbmc.Action(previousmenu)')
		time.sleep(3)
		for i in range( len( aScenario ) ) :
			if isinstance( aScenario[i], list ) :
				temp, node_count = aScenario[i][0]
				for j in range( int( node_count ) ) :
					for k in range( len( aScenario[i] ) - 1 ) :
						self.DoAction( aScenario[i][k+1] )
						LOG_TRACE( 'Loop Result : Count = %s, Time = %s' % ( j, TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_HH_MM ) ) )
			else :
				self.DoAction( aScenario[i] )
				LOG_TRACE( 'Single Result : Time = %s' % TimeToString( self.mDataCache.Datetime_GetLocalTime( ), TimeFormatEnum.E_HH_MM ) )


	def DoAction( self, aKey ) :
		actionType, actionValue = aKey
		if actionType.lower( ) == 'sendkey' :
			xbmc.executebuiltin( 'xbmc.Action(%s)' % actionValue )
		elif actionType.lower( ) == 'sleep' :
			time.sleep( float( actionValue ) )
		else :
			LOG_ERR( 'Unknown Test Action' )
		time.sleep( 0.5 )

