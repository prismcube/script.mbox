
import datetime
import time
from pvr.Util import RunThread, LOG_WARN, LOG_TRACE, LOG_ERR
from ElisCommander import ElisCommander
from ElisEventClass import *
from ElisEventBus import ElisEventBus
from ElisAction import ElisAction
from ElisEnum import ElisEnum
import pvr.ElisMgr
import thread
import select
from decorator import decorator
from ElisClass import *
from ElisEventClass import *
from ElisProperty import ElisPropertyEnum
from pvr.gui.GuiConfig import *


gDataCacheMgr = None

gDataLock = thread.allocate_lock()



@decorator
def DataLock(func, *args, **kw):
	gDataLock.acquire()
	try :
		result =  func(*args, **kw)
		return result
		
	finally:
		gDataLock.release( )


def GetInstance():
	global gDataCacheMgr
	if not gDataCacheMgr:
		gDataCacheMgr = DataCacheMgr()
	else:
		pass
		#print 'lael98 check already windowmgr is created'

	return gDataCacheMgr


class CacheChannel( object ) :
	def __init__( self, aChannel, aPrevKey, aNextKey ):
		self.mChannel = aChannel
		self.mPrevKey = aPrevKey
		self.mNextKey = aNextKey


class DataCacheMgr( object ):
	def __init__( self ):
		self.mShutdowning = False
		LOG_TRACE('')		
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		LOG_TRACE('')		
		self.mEventBus = pvr.ElisMgr.GetInstance( ).GetEventBus( )
		LOG_TRACE('')

		self.mZappingMode				= None
		self.mChannelList				= None
		self.mCurrentChannel			= None
		self.mLocalOffset				= 0
		self.mLocalTime					= 0
		self.mSatelliteList				= None
		self.mConfiguredSatelliteList1	= None
		self.mConfiguredSatelliteList2	= None
		self.mTransponderList			= None
		self.mEPGList					= None
		self.mCurrentEvent				= None

		self.mChannelListHash			= {}
		self.mSatelliteListHash			= {}
		self.mTransponderListHash		= {}
		self.mEPGListHash				= {}

		LOG_TRACE('')
		self.Load()
		LOG_TRACE('')

		self.mEventBus.Register( self )		


	def onEvent(self, aEvent):
		if aEvent.getName() == ElisEventCurrentEITReceived.getName() :
			hashKey = '%d:%d:%d:%d' %( aEvent.mEventId, aEvent.mSid, aEvent.mTsid, aEvent.mOnid )
			#LOG_TRACE('hashKey=%s' %hashKey )
			event = self.mEPGListHash.get( hashKey, None )

			if event == None:
				event = self.mCommander.Epgevent_GetPresent()
				if event and event.mError == 0:
					LOG_TRACE('add hashKey=%s' %hashKey )				
					self.mEPGListHash[hashKey] = event

			if event and self.mCurrentChannel.mSid == event.mSid and \
			self.mCurrentChannel.mTsid == event.mTsid and self.mCurrentChannel.mOnid == event.mOnid :
				self.mCurrentEvent = event
				#LOG_TRACE('currentEvent' )



	def Load( self ) :

		#Zapping Mode
		LOG_TRACE('')
		self.mZappingMode = self.mCommander.Zappingmode_GetCurrent( )
		LOG_TRACE('')		
		self.mCurrentChannel = self.mCommander.Channel_GetCurrent( )
		LOG_TRACE('')		


		#SatelliteList
		self.LoadAllSatellite( )
		self.LoadConfiguredSatellite( )
		self.LoadConfiguredTransponder( )


		# Channel
		self.LoadChannelList( )


		# DATE
		self.mLocalOffset = self.mCommander.Datetime_GetLocalOffset( )
		self.mLocalTime = self.mCommander.Datetime_GetLocalTime( )


	def LoadAllSatellite( self ) :
		self.mSatelliteList = self.mCommander.Satellite_GetList( ElisEnum.E_SORT_INSERTED )
		count =  len( self.mSatelliteList )
		LOG_TRACE('satellite count=%d' %count )

		for i in range( count ):
			satellite = self.mSatelliteList[i]
			hashKey = '%d:%d' % ( satellite.mLongitude, satellite.mBand )
			self.mSatelliteListHash[hashKey] = satellite


	def LoadConfiguredSatellite( self ) :
		self.mConfiguredSatelliteList1 = []
		self.mConfiguredSatelliteList1 = self.mCommander.Satelliteconfig_GetList( E_TUNER_1 )

		for configsatellite in self.mConfiguredSatelliteList1 :
			if configsatellite == None :
				self.mConfiguredSatelliteList1 = []
				break
				
			elif configsatellite.mError < 0 :
				self.mConfiguredSatelliteList1 = []
				break

		self.mConfiguredSatelliteList2 = []				
		self.mConfiguredSatelliteList2 = self.mCommander.Satelliteconfig_GetList( E_TUNER_2 )

		for configsatellite in self.mConfiguredSatelliteList2 :
			if configsatellite == None :
				self.mConfiguredSatelliteList2 = []
				break
				
			elif configsatellite.mError < 0 :
				self.mConfiguredSatelliteList2 = []
				break


	def GetConfiguredSatellite( self, aTunerNumber ) :
		if aTunerNumber == E_TUNER_1 :
			return self.mConfiguredSatelliteList1

		elif aTunerNumber == E_TUNER_2 :
			return self.mConfiguredSatelliteList2

		else :
			LOG_ERR( 'Unknown Tuner Number %s' % aTunerNumber )
			return self.mConfiguredSatelliteList1


	def LoadConfiguredTransponder( self ) :
		self.mTransponderList = []
		self.mTransponderListHash = {}
		
		if len( self.mConfiguredSatelliteList1 ) == 0 and len( self.mConfiguredSatelliteList2 ) == 0 :
			LOG_TRACE( 'Configured Satellite List is Empty' )
			return
			
		if len( self.mConfiguredSatelliteList1 ) != 0 :
			for satellite in self.mConfiguredSatelliteList1 :
				transponder = self.mCommander.Transponder_GetList( satellite.mSatelliteLongitude, satellite.mBandType )
				self.mTransponderList.append( transponder )
				hashKey = '%d:%d' % ( satellite.mSatelliteLongitude, satellite.mBandType )
				self.mTransponderListHash[hashKey] = transponder
				
		if len( self.mConfiguredSatelliteList2 ) != 0 :
			for satellite in self.mConfiguredSatelliteList2 :
				transponder = self.mCommander.Transponder_GetList( satellite.mSatelliteLongitude, satellite.mBandType )
				self.mTransponderList.append( transponder )
				hashKey = '%d:%d' % ( satellite.mSatelliteLongitude, satellite.mBandType )
				self.mTransponderListHash[hashKey] = transponder


	def LoadChannelList( self ) :
		self.mChannelList = self.mCommander.Channel_GetList( self.mZappingMode.mServiceType, self.mZappingMode.mMode, self.mZappingMode.mSortingMode )

		prevChannel = None
		nextChannel = None
		
		if self.mChannelList and self.mChannelList[0].mError == 0 :

			LOG_TRACE('')
			count = len( self.mChannelList )
			LOG_TRACE('count=%d' %count)			

			prevChannel = self.mChannelList[count-1]

			for i in range( count ):
				channel = self.mChannelList[i]
				if i+1 < count :
					nextChannel = self.mChannelList[i+1]
				else:
					nextChannel = self.mChannelList[0]

				#LOG_TRACE("---------------------- CacheChannel -----------------")

				try :
					cacheChannel = CacheChannel( channel, prevChannel.mNumber, nextChannel.mNumber )
					#LOG_TRACE('')
					self.mChannelListHash[channel.mNumber] = cacheChannel
					#LOG_TRACE('')				

					#cacheChannel.mChannel.printdebug()
					#LOG_TRACE('prevKey=%d nextKey=%d' %( cacheChannel.mPrevKey, cacheChannel.mNextKey ) )

				except Exception, ex:
					LOG_ERR( "Exception %s" %ex)
				
				
				prevChannel = channel		
	

	@DataLock
	def Zappingmode_GetCurrent( self ) :
		return self.mZappingMode


	@DataLock
	def Zappingmode_SetCurrent( self , aZappingMode ) :
		if self.mCommander.Zappingmode_SetCurrent( aZappingMode ) == True :
			self.mZappingMode = aZappingMode

	@DataLock
	def Channel_GetList( self ) :
		return self.mChannelList
		

	@DataLock
	def Channel_GetCurrent( self ) :
		return self.mCurrentChannel


	@DataLock
	def Channel_SetCurrent( self, aChannelNumber, aServiceType ) :
		self.mCurrentEvent = None
		if self.mCommander.Channel_SetCurrent( aChannelNumber, aServiceType ) == True :
			cacheChannel = self.mChannelListHash.get(aChannelNumber, None )
			self.mCurrentChannel = cacheChannel.mChannel
			return True
		return False


	@DataLock
	def Channel_GetPrev( self, aChannel ) :
		if aChannel	== None or aChannel.mError != 0 :
			return None

		cacheChannel = self.mChannelListHash.get(aChannel.mNumber, None)
		if cacheChannel == None :
			return None

		prevKey = cacheChannel.mPrevKey
		channel =  self.mChannelListHash.get(prevKey, None).mChannel
		#LOG_TRACE('------------ Prev Channel-------------------')
		#channel.printdebug()
		return channel


	@DataLock
	def Channel_GetNext( self, aChannel ) :
		if aChannel	== None or aChannel.mError != 0 :
			return None

		cacheChannel = self.mChannelListHash.get(aChannel.mNumber, None)
		if cacheChannel == None :
			return None

		nextKey = cacheChannel.mNextKey
		channel =  self.mChannelListHash.get(nextKey, None).mChannel
		#LOG_TRACE('------------ Next Channel-------------------')
		#channel.printdebug()
		return channel

	@DataLock
	def Channel_GetCurr( self, aJumpNumber ) :

		cacheChannel = self.mChannelListHash.get(aJumpNumber, None).mChannel
		if cacheChannel == None :
			return None

		channel =  cacheChannel
		#LOG_TRACE('------------ Current Channel-------------------')
		#channel.printdebug()
		return channel

	@DataLock
	def Channel_GetSearch( self, aNumber ) :

		fChannel = None
		if self.mChannelList and self.mChannelList[0].mError == 0 :
			findCh = False
			for iChannel in self.mChannelList :
				#LOG_TRACE('searching[%s] [%s]'% (iChannel.mNumber, aChannel.mNumber) )
				if iChannel.mNumber == aNumber :
					fChannel = iChannel
					findCh = True
					LOG_TRACE('------- Success to searched[%s]'% iChannel.mNumber)
					break
			if findCh == False:
				LOG_TRACE('------- Fail to searched[%s]'% aNumber)
				return None

		return fChannel

	@DataLock
	def Datetime_GetLocalOffset( self ) :
		return self.mLocalOffset


	@DataLock
	def Datetime_GetLocalTime( self ) :
		localTime = time.localtime()
		self.mLocalTime = time.mktime( localTime ) + self.mLocalOffset
		return self.mLocalTime


	@DataLock
	def Datetime_GetGMTTime( self ) :
		gmtTime = self.mLocalTime - self.mLocalOffset
		if gmtTime <= 0 :
			return self.mLocalTime

		return gmtTime


	@DataLock
	def Satellite_GetByChannelNumber( self , aNumber ) :
		cacheChannel = self.mChannelListHash.get(aNumber, None)
		if cacheChannel :
			carrier = cacheChannel.mChannel.mCarrier
			if carrier.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBS :
				hashKey = '%d:%d' %( carrier.mDVBS.mSatelliteLongitude, carrier.mDVBS.mSatelliteBand )
				satellite = self.mSatelliteListHash.get( hashKey, None )
				return satellite

			else :
				LOG_ERR('Not Supported Carrier type =%d' %carrier.mCarrierType )

		return None

	#@DataLock
	def Epgevent_GetList( self, aChannel, aTestTime=0 ) :
		if aTestTime :
			gmtime = aTestTime
		else:
			gmtime = self.Datetime_GetGMTTime()

		gmtFrom = gmtime
		gmtUntil= gmtime
		maxCount= 1

		#LOG_TRACE('ch[%s] sid[%d] tsid[%d] oid[%d]'% (aChannel.mNumber, aChannel.mSid, aChannel.mTsid, aChannel.mOnid) )
		#LOG_TRACE('from[%s] until[%s]'% (time.strftime("%H:%M", time.gmtime(gmtFrom)), time.strftime("%H:%M", time.gmtime(gmtFrom)) ) )
		event = self.mCommander.Epgevent_GetList( aChannel.mSid, aChannel.mTsid, aChannel.mOnid, gmtFrom, gmtUntil, maxCount )
		if event :
			#from pvr.PublicReference import ClassToList
			#LOG_TRACE('=============epg len[%s] list[%s]'% (len(event),ClassToList('convert', event )) )
			return event[0]

		return None

	@DataLock
	def Epgevent_GetEvent( self, aEvent ) :
		hashKey = '%d:%d:%d:%d' %( aEvent.mEventId, aEvent.mSid, aEvent.mTsid, aEvent.mOnid )
		event = self.mEPGListHash.get( hashKey, None )

		if event :
			return event

		return None


	@DataLock
	def Epgevent_GetPresent( self ) :
		#Todo later
		""" 
		if self.mCurrentEvent :
			LOG_TRACE('currentEvent' )
			self.mCurrentEvent.printdebug()
		else :
			 self.mCurrentEvent = self.mCommander.Epgevent_GetPresent()

		return self.mCurrentEvent
		"""

		return	self.mCommander.Epgevent_GetPresent( )


	@DataLock
	def Satellite_GetFormattedNameList( self ) :
		formattedlist = []	
		for satellite in self.mSatelliteList :
			dir = 'E'

			tmpLongitude  = satellite.mLongitude
			if tmpLongitude > 1800 :
				dir = 'W'
				tmpLongitude = 3600 - satellite.mLongitude

			formattedName = '%d.%d %s %s' %( int( tmpLongitude / 10 ), tmpLongitude % 10, dir, satellite.mName )
			formattedlist.append( formattedName )

		return formattedlist


	@DataLock
	def Satellite_GetSatelliteByIndex( self, aIndex ) :
		return self.mSatelliteList[ aIndex ]


	def Satellite_GetFormattedName( self, aLongitude, aBand ) :
		hashKey = '%d:%d' % ( aLongitude, aBand )
		satellite = self.mSatelliteListHash.get( hashKey, None )
		if satellite != None:
			dir = 'E'

			tmpLongitude  = aLongitude
			if tmpLongitude > 1800 :
				dir = 'W'
				tmpLongitude = 3600 - aLongitude

			formattedName = '%d.%d %s %s' % ( int( tmpLongitude / 10 ), tmpLongitude % 10, dir, satellite.mName )
			return formattedName

		return 'UnKnown'


	def Satellite_GetTransponder( self, aLongitude, aBand ) :
		transponder = []
		hashKey = '%d:%d' % ( aLongitude, aBand )
		transponder = self.mTransponderListHash.get( hashKey, None )
		if transponder :
			return transponder
		else :
			transponder = self.mCommander.Transponder_GetList( aLongitude, aBand )
		if transponder < 0 :
			return []
		else :
			return transponder


	def Satellite_GetFormattedTransponderList( self, aLongitude, aBand ) :
		tmptransponderList = []
		transponderList = []
		
		tmptransponderList = self.Satellite_GetTransponder( aLongitude, aBand )
  
 		for i in range( len( tmptransponderList ) ) :
 			if tmptransponderList[i].mError < 0 :
 				transponderList.append( 'Empty' ) 
	 			return transponderList
 			else :
				transponderList.append( '%d %d MHz %d KS/s' % ( ( i + 1 ), tmptransponderList[i].mFrequency, tmptransponderList[i].mSymbolRate ) )

		return transponderList
