
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
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.GuiConfig import *


SUPPORT_EPG_DATABASE = True
SUPPORT_CHANNEL_DATABASE = True
SUPPORT_TIMER_DATABASE = False
SUPPORT_RECORD_DATABASE = True


if SUPPORT_EPG_DATABASE == True :
	from ElisEPGDB import ElisEPGDB

if SUPPORT_CHANNEL_DATABASE == True :
	from ElisChannelDB import ElisChannelDB

if SUPPORT_TIMER_DATABASE == True :
	from ElisTimerDB import ElisTimerDB

if SUPPORT_RECORD_DATABASE == True :
	from ElisRecordDB import ElisRecordDB


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

		self.mZappingMode						= None
		self.mChannelList						= None
		self.mCurrentChannel					= None
		self.mLocalOffset						= 0
		self.mLocalTime							= 0
		self.mAllSatelliteList					= None
		self.mConfiguredSatelliteList			= None
		self.mConfiguredSatelliteListTuner1		= None
		self.mConfiguredSatelliteListTuner2		= None
		self.mTransponderList					= None
		self.mEPGList							= None
		self.mCurrentEvent						= None
		self.mListCasList						= None
		self.mListFavorite						= None
		self.mPropertyAge						= 0
		self.mPropertyPincode					= -1
		self.mCacheReload						= False

		self.mChannelListHash					= {}
		self.mAllSatelliteListHash				= {}
		self.mTransponderListHash				= {}
		self.mEPGListHash						= {}

		self.mEpgDB = None
		self.mChannelDB = None
		self.mTimerDB = None
		self.mRecordDB = None		

		if SUPPORT_EPG_DATABASE	 == True :
			self.mEpgDB = ElisEPGDB( )

		if SUPPORT_CHANNEL_DATABASE	 == True :
			self.mChannelDB = ElisChannelDB( )

		if SUPPORT_TIMER_DATABASE == True :
			self.mTimerDB = ElisTimerDB( )
			#TEST CODE
			"""
			count = self.mTimerDB.Timer_GetTimerCount()
			LOG_TRACE('TIMER DB TEST count=%d' %count )
			for i in range( count ) :
				timer = self.mTimerDB.Timer_GetByIndex( i )
				timer.printdebug()
			timerList = self.mTimerDB.Timer_GetTimerList()
			LOG_TRACE('TIMER DB TEST2')
			if timerList :
				for timer in timerList :
					timer.printdebug()
			"""

		if SUPPORT_RECORD_DATABASE == True :
			self.mRecordDB = ElisRecordDB( )
			#TEST CODE
			"""
			count = self.mRecordDB.Record_GetCount( ElisEnum.E_SERVICE_TYPE_TV )
			LOG_TRACE('RECORD DB TEST count=%d' %count )
			for i in range( count ) :
				record = self.mRecordDB.Record_GetRecordInfo( i, ElisEnum.E_SERVICE_TYPE_TV )
				record.printdebug()
			recordList = self.mRecordDB.Record_GetList( ElisEnum.E_SERVICE_TYPE_TV )
			LOG_TRACE('RECORD DB TEST2')
			if recordList :
				for record in recordList :
					record.printdebug()
			"""

		LOG_TRACE('')
		self.Load( )
		LOG_TRACE('')
		#self.mEventBus.Register( self )


	@classmethod
	def GetName(cls):
		return cls.__name__


	def BeginEPGTransaction( self ) :
		if SUPPORT_EPG_DATABASE	== True :
			self.mEpgDB.Execute('begin')


	def EndEPGTransaction( self ):
		if SUPPORT_EPG_DATABASE	== True :
			self.mEpgDB.Execute('commit')


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

	def Test( self ):
		before = time.clock()
		LOG_ERR('before=%s' %before )
		for i in range( 10 ) :
			self.mChannelList = self.mCommander.Channel_GetList( self.mZappingMode.mServiceType, self.mZappingMode.mMode, self.mZappingMode.mSortingMode )	

		after = time.clock()
		LOG_ERR('after=%s' %after )		
		LOG_ERR('--------------> diff=%s' %(after-before) )


	def Load( self ) :

		self.LoadVolumeToSetGUI( )

		#Zapping Mode
		LOG_TRACE('')
		self.LoadZappingmode( )
		self.LoadZappingList( )
		LOG_TRACE('')


		#SatelliteList
		self.LoadAllSatellite( )
		self.LoadConfiguredSatellite( )
		self.LoadConfiguredTransponder( )

		# Channel
		self.Channel_GetZappingList( )
		self.LoadChannelList( )

		# DATE
		self.LoadTime( )


	def LoadVolumeToSetGUI( self ) :
		volume = self.mCommander.Player_GetVolume( )
		LOG_TRACE( 'playerVolume[%s]'% volume)

		apiSet = 'setvolume(%s)'% volume
		xbmc.executehttpapi(apiSet)


	def LoadTime( self ) :
		self.mLocalOffset = self.mCommander.Datetime_GetLocalOffset( )
		self.mLocalTime = self.mCommander.Datetime_GetLocalTime( )


	def LoadAllSatellite( self ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			self.mAllSatelliteList = self.mChannelDB.Satellite_GetList( ElisEnum.E_SORTING_FAVORITE )
		else:
			self.mAllSatelliteList = self.mCommander.Satellite_GetList( ElisEnum.E_SORTING_FAVORITE )

		if self.mAllSatelliteList and self.mAllSatelliteList[0].mError == 0 :
		
			count =  len( self.mAllSatelliteList )
			LOG_TRACE( 'satellite count = %d' % count )
			from pvr.PublicReference import ClassToList
			LOG_TRACE( 'satellite[%s]' % ClassToList( 'convert', self.mAllSatelliteList ) )

			for i in range( count ):
				satellite = self.mAllSatelliteList[i]
				hashKey = '%d:%d' % ( satellite.mLongitude, satellite.mBand )
				self.mAllSatelliteListHash[hashKey] = satellite
		else :
			LOG_ERR('Has no Satellite')


	def LoadConfiguredSatellite( self ) :
		self.mConfiguredSatelliteList = []
		if SUPPORT_CHANNEL_DATABASE	== True :
			self.mConfiguredSatelliteList = self.mChannelDB.Satellite_GetConfiguredList( ElisEnum.E_SORT_NAME )
		else :
			self.mConfiguredSatelliteList = self.mCommander.Satellite_GetConfiguredList( ElisEnum.E_SORT_NAME )

		if self.mConfiguredSatelliteList and self.mConfiguredSatelliteList[0].mError == 0 :
			pass
		else :
			LOG_WARN('Has no Configured Satellite')


		self.mConfiguredSatelliteListTuner1 = []
		if SUPPORT_CHANNEL_DATABASE	== True :
			self.mConfiguredSatelliteListTuner1 = self.mChannelDB.Satelliteconfig_GetList( E_TUNER_1 )
		else :
			self.mConfiguredSatelliteListTuner1 = self.mCommander.Satelliteconfig_GetList( E_TUNER_1 )

		if self.mConfiguredSatelliteListTuner1 and self.mConfiguredSatelliteListTuner1[0].mError == 0 :
			pass
		else :
			LOG_WARN('Has no Configured Satellite Tuner 1')


		self.mConfiguredSatelliteListTuner2 = []
		if SUPPORT_CHANNEL_DATABASE	== True :
			self.mConfiguredSatelliteListTuner2 = self.mChannelDB.Satelliteconfig_GetList( E_TUNER_2 )
		else :
			self.mConfiguredSatelliteListTuner2 = self.mCommander.Satelliteconfig_GetList( E_TUNER_2 )

		if self.mConfiguredSatelliteListTuner2 and self.mConfiguredSatelliteListTuner2[0].mError == 0 :
			pass
		else :
			LOG_WARN('Has no Configured Satellite Tuner 2')


	def LoadConfiguredTransponder( self ) :
		self.mTransponderList = []
		self.mTransponderListHash = {}

	 	if self.mConfiguredSatelliteList and self.mConfiguredSatelliteList[0].mError == 0 :
			for satellite in self.mConfiguredSatelliteList :
				if SUPPORT_CHANNEL_DATABASE	== True :
					transponder = self.mChannelDB.Transponder_GetList( satellite.mLongitude, satellite.mBand )
				else :
					transponder = self.mCommander.Transponder_GetList( satellite.mLongitude, satellite.mBand )
				self.mTransponderList.append( transponder )
				hashKey = '%d:%d' % ( satellite.mLongitude, satellite.mBand )
				self.mTransponderListHash[hashKey] = transponder
		else :
			LOG_WARN('Has no Configured Satellite')
		
	@DataLock
	def Satellite_GetAllSatelliteList( self ) :
		return self.mAllSatelliteList


	def Satellite_ConfiguredTunerSatellite( self, aTunerNumber ) :
		if aTunerNumber == E_TUNER_1 :
			if self.mConfiguredSatelliteListTuner1 :
				return self.mConfiguredSatelliteListTuner1
			else :
				if SUPPORT_CHANNEL_DATABASE	== True :
					return self.mChannelDB.Satelliteconfig_GetList( E_TUNER_1 )
				else :
					return self.mCommander.Satelliteconfig_GetList( E_TUNER_1 )

				
		elif aTunerNumber == E_TUNER_2 :
			if self.mConfiguredSatelliteListTuner2 :
				return self.mConfiguredSatelliteListTuner2
			else :
				if SUPPORT_CHANNEL_DATABASE	== True :
					return self.mChannelDB.Satelliteconfig_GetList( E_TUNER_2 )
				else :
					return self.mCommander.Satelliteconfig_GetList( E_TUNER_2 )

		else :
			LOG_ERR( 'Unknown Tuner Number %s' % aTunerNumber )


	def Satellite_GetConfiguredList( self ) :
		if self.mConfiguredSatelliteList :
			return self.mConfiguredSatelliteList
		else :
			if SUPPORT_CHANNEL_DATABASE	== True :
				return self.mChannelDB.Satellite_GetConfiguredList( ElisEnum.E_SORT_NAME )
			else :
				return self.mCommander.Satellite_GetConfiguredList( ElisEnum.E_SORT_NAME )
			

	@DataLock
	def Satellite_GetFormattedNameList( self ) :
		formattedlist = []	
		for satellite in self.mAllSatelliteList :
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
		return self.mAllSatelliteList[ aIndex ]


	def Satellite_GetFormattedName( self, aLongitude, aBand ) :
		hashKey = '%d:%d' % ( aLongitude, aBand )
		satellite = self.mAllSatelliteListHash.get( hashKey, None )
		if satellite != None:
			dir = 'E'

			tmpLongitude  = aLongitude
			if tmpLongitude > 1800 :
				dir = 'W'
				tmpLongitude = 3600 - aLongitude

			formattedName = '%d.%d %s %s' % ( int( tmpLongitude / 10 ), tmpLongitude % 10, dir, satellite.mName )
			return formattedName

		return 'UnKnown'


	def Satellite_GetTransponderList( self, aLongitude, aBand ) :
		transponder = []
		hashKey = '%d:%d' % ( aLongitude, aBand )
		transponder = self.mTransponderListHash.get( hashKey, None )
		if transponder :
			return transponder
		else :
			if SUPPORT_CHANNEL_DATABASE	== True :
				return self.mChannelDB.Transponder_GetList( aLongitude, aBand )
			else :
				return self.mCommander.Transponder_GetList( aLongitude, aBand )


	def Satellite_GetFormattedTransponderList( self, aLongitude, aBand ) :
		tmptransponderList = []
		transponderList = None
		
		tmptransponderList = self.Satellite_GetTransponderList( aLongitude, aBand )
		
		if tmptransponderList and tmptransponderList[0].mError == 0 :
			transponderList = []
	 		for i in range( len( tmptransponderList ) ) :
				transponderList.append( '%d %d MHz %d KS/s' % ( ( i + 1 ), tmptransponderList[i].mFrequency, tmptransponderList[i].mSymbolRate ) )

		return transponderList


	def Satellite_GetTransponderListByIndex( self, aLongitude, aBand, aIndex ) :
		transponder = []
		hashKey = '%d:%d' % ( aLongitude, aBand )
		transponder = self.mTransponderListHash.get( hashKey, None )
		if transponder :
			return transponder[ aIndex ]
		else :
			if SUPPORT_CHANNEL_DATABASE	== True :
				channelDB = ElisChannelDB( )
				transponder = channelDB.Transponder_GetList( aLongitude, aBand )
				channelDB.Close( )
				if transponder :
					return transponder[ aIndex ]
			else :
				transponder = self.mCommander.Transponder_GetList( aLongitude, aBand )
				if transponder :
					return transponder[ aIndex ]
		return None


	def SetChangeDBTableChannel( self, aChannelTable ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			self.mChannelDB.mDBChTable = aChannelTable


	def GetChangeDBTableChannel( self ) :
		ret = -1
		if SUPPORT_CHANNEL_DATABASE	== True :
			ret = self.mChannelDB.mDBChTable

		return ret


	def LoadChannelList( self, aSync = 0, aType = ElisEnum.E_SERVICE_TYPE_TV, aMode = ElisEnum.E_MODE_ALL, aSort = ElisEnum.E_SORT_BY_NUMBER, aReopen = False ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			mType = aType
			mMode = aMode
			mSort = aSort
		
			if aSync == 0 and self.mZappingMode :
				mType = self.mZappingMode.mServiceType
				mMode = self.mZappingMode.mMode
				mSort = self.mZappingMode.mSortingMode

			if mMode == ElisEnum.E_MODE_ALL :
				tmpChannelList = self.Channel_GetList( True, mType, mMode, mSort, aReopen )

			elif mMode == ElisEnum.E_MODE_SATELLITE :
				mLongitude = self.mZappingMode.mSatelliteInfo.mLongitude
				mBand = self.mZappingMode.mSatelliteInfo.mBand
				tmpChannelList = self.Channel_GetListBySatellite( mType, mMode, mSort, mLongitude, mBand, aReopen )

			elif mMode == ElisEnum.E_MODE_CAS :
				mCaid = self.mZappingMode.mCasInfo.mCAId
				tmpChannelList = self.Channel_GetListByFTACas( mType, mMode, mSort, mCaid, aReopen )
				
			elif mMode == ElisEnum.E_MODE_FAVORITE :
				mFavName = self.mZappingMode.mFavoriteGroup.mGroupName
				tmpChannelList = self.Channel_GetListByFavorite( mType, mMode, mSort, mFavName, aReopen )

			elif mMode == ElisEnum.E_MODE_NETWORK :
				return None

		else:
			tmpChannelList = self.mCommander.Channel_GetList( self.mZappingMode.mServiceType, self.mZappingMode.mMode, self.mZappingMode.mSortingMode )

		mCount = 0
		tCount = 0
		if self.mChannelList :
			mCount = len(self.mChannelList)
		if tmpChannelList :
			tCount = len(tmpChannelList)
		if mCount != tCount :
			self.mCacheReload = True

		prevChannel = None
		nextChannel = None

		self.mChannelList = tmpChannelList
		if self.mChannelList and self.mChannelList[0].mError == 0 :
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
		
	
	def LoadZappingmode( self, aReopen = False ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			self.mZappingMode = self.Zappingmode_GetCurrent( True, aReopen )
			self.mCurrentChannel = self.mCommander.Channel_GetCurrent( )
		else :
			self.mZappingMode = self.mCommander.Zappingmode_GetCurrent( )
			self.mCurrentChannel = self.mCommander.Channel_GetCurrent( )


	def LoadZappingList( self, aReopen = False ) :
		serviceType = ElisEnum.E_SERVICE_TYPE_TV
		if self.mZappingMode :
			serviceType = self.mZappingMode.mServiceType

		if SUPPORT_CHANNEL_DATABASE	== True :
			self.mListCasList   = self.mCommander.Fta_cas_GetList( serviceType )
			self.mListFavorite = self.Favorite_GetList( True, serviceType, aReopen )
		else :
			self.mListCasList   = self.mCommander.Fta_cas_GetList( serviceType )
			self.mListFavorite  = self.mCommander.Favorite_GetList( serviceType )

	def Zappingmode_SetCurrent( self , aZappingMode, aSync = 0 ) :
		ret = False
		ret = self.mCommander.Zappingmode_SetCurrent( aZappingMode )
		if ret == True :
			self.mZappingMode = aZappingMode[0]

		return ret


	def Zappingmode_GetCurrent( self, aRequestChanged = 0, aReopen = False ) :
		if aRequestChanged :
			if SUPPORT_CHANNEL_DATABASE	== True :
				if aReopen :
					channelDB = ElisChannelDB()
					self.mZappingMode = channelDB.Zappingmode_GetCurrent( )
					channelDB.Close()
				else :
					self.mZappingMode = self.mChannelDB.Zappingmode_GetCurrent( )
			else :
				self.mZappingMode = self.mCommander.Zappingmode_GetCurrent( )

		return self.mZappingMode


	def Fta_cas_GetList( self, aServiceType = ElisEnum.E_SERVICE_TYPE_INVALID ) :
		if aServiceType :
			return self.mCommander.Fta_cas_GetList( aServiceType )
		else :
			return self.mListCasList


	def Favorite_GetList( self, aRequestChanged = 0, aServiceType = ElisEnum.E_SERVICE_TYPE_INVALID, aReopen = False ) :
		if aRequestChanged :
			if SUPPORT_CHANNEL_DATABASE	== True :
				if aReopen :
					channelDB = ElisChannelDB()
					return channelDB.Favorite_GetList( aServiceType )
					channelDB.Close()
				else :
					return self.mChannelDB.Favorite_GetList( aServiceType )
			else :
				return self.mCommander.Favorite_GetList( aServiceType )
		else :
			return self.mListFavorite

	def Channel_GetList( self, aRequestChanged = 0, aType = 0, aMode = 0, aSort = 0, aReopen = False ) :
		if aRequestChanged :
			if SUPPORT_CHANNEL_DATABASE	== True :
				if aReopen :
					channelDB = ElisChannelDB()
					return channelDB.Channel_GetList( aType, aMode, aSort )
					channelDB.Close()
				else :
					return self.mChannelDB.Channel_GetList( aType, aMode, aSort )
			else :
				return self.mCommander.Channel_GetList( aType, aMode, aSort )

		else :
			return self.mChannelList


	def Channel_GetCurrent( self, aRequestChanged = 0 ) :
		if aRequestChanged :
			return self.mCommander.Channel_GetCurrent( )

		return self.mCurrentChannel

	def Channel_SetCurrent( self, aChannelNumber, aServiceType ) :
		ret = False
		self.mCurrentEvent = None
		if self.mCommander.Channel_SetCurrent( aChannelNumber, aServiceType ) == True :
			cacheChannel = self.mChannelListHash.get( aChannelNumber, None )
			if cacheChannel :
				self.mCurrentChannel = cacheChannel.mChannel
				ret = True

		return ret


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
		localTime = time.localtime( )
		self.mLocalTime = time.mktime( localTime ) + self.mLocalOffset
		return self.mLocalTime


	@DataLock
	def Datetime_GetGMTTime( self ) :
		localTime = time.localtime( )
		return  time.mktime( localTime )


#	@DataLock
	def Satellite_GetByChannelNumber( self, aNumber, aRequestType = -1, aReopen = False ) :
		if aRequestType == -1 :
			cacheChannel = self.mChannelListHash.get(aNumber, None)
			if cacheChannel :
				carrier = cacheChannel.mChannel.mCarrier
				if carrier.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBS :
					hashKey = '%d:%d' %( carrier.mDVBS.mSatelliteLongitude, carrier.mDVBS.mSatelliteBand )
					satellite = self.mAllSatelliteListHash.get( hashKey, None )
					return satellite

				else :
					LOG_ERR('Not Supported Carrier type =%d' %carrier.mCarrierType )

		else :
			if SUPPORT_CHANNEL_DATABASE	== True :
				if aReopen :
					channelDB = ElisChannelDB()
					return channelDB.Satellite_GetByChannelNumber( aNumber, aRequestType )
					channelDB.Close()
				else :
					return self.mChannelDB.Satellite_GetByChannelNumber( aNumber, aRequestType )
				
			else :
				return self.mCommander.Satellite_GetByChannelNumber( aNumber, aRequestType )

		return None


#	@DataLock
	def Epgevent_GetListByChannel( self, aSid, aTsid, aOnid, aGmtFrom, aGmtUntil, aMaxCount, aReopen = False ) :

		eventList = None
		
		if SUPPORT_EPG_DATABASE	== True :
			if aReopen == True :
				epgDB = ElisEPGDB()
				eventList = epgDB.Epgevent_GetList( aSid, aTsid, aOnid, aGmtFrom, aGmtUntil, aMaxCount )
				epgDB.Close()
			else :
				eventList = self.mEpgDB.Epgevent_GetList( aSid, aTsid, aOnid, aGmtFrom, aGmtUntil, aMaxCount )
				
		else:
			eventList = self.mCommander.Epgevent_GetList( aSid, aTsid, aOnid, aGmtFrom, aGmtUntil, aMaxCount )

		return eventList


#	@DataLock
	def Epgevent_GetEvent( self, aEvent ) :
		hashKey = '%d:%d:%d:%d' %( aEvent.mEventId, aEvent.mSid, aEvent.mTsid, aEvent.mOnid )
		event = self.mEPGListHash.get( hashKey, None )

		if event :
			return event

		return None


#	@DataLock
	def Epgevent_GetCurrent( self, aSid, aTsid, aOnid, aReopen = False ) :

		eventList = None
		
		if SUPPORT_EPG_DATABASE	== True :
			if aReopen == True :
				epgDB = ElisEPGDB()
				eventList = epgDB.Epgevent_GetCurrent( aSid, aTsid, aOnid, self.Datetime_GetGMTTime() )
				epgDB.Close()
			else :
				eventList = self.mEpgDB.Epgevent_GetCurrent( aSid, aTsid, aOnid, self.Datetime_GetGMTTime() )

		else:
			eventList = self.mCommander.Epgevent_GetList( aSid, aTsid, aOnid, 0, 0, 1 )
			if eventList :
				eventList = eventList[0]

		return eventList


	def Epgevent_GetCurrentList( self  ) :

		eventList = None

		if SUPPORT_EPG_DATABASE	== True :
			eventList = self.mEpgDB.Epgevent_GetCurrentList( self.Datetime_GetGMTTime() )
		else:
			return None

		return eventList


#	@DataLock
	def Epgevent_GetFollowing( self, aSid, aTsid, aOnid ) :

		eventList = None

		if SUPPORT_EPG_DATABASE	== True :
			eventList = self.mEpgDB.Epgevent_GetFollowing( aSid, aTsid, aOnid, self.Datetime_GetGMTTime() )
			
		else:
			eventList = self.mCommander.Epgevent_GetList( aSid, aTsid, aOnid, 1, 1, 1 )

		return eventList


#	@DataLock
	def Epgevent_GetFollowingList( self  ) :

		eventList = None

		if SUPPORT_EPG_DATABASE	== True :
			eventList = self.mEpgDB.Epgevent_GetFollowingList( self.Datetime_GetGMTTime() )
		else:
			return None

		return eventList



	#@DataLock
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


	#Aready declared : _Elis, request direct command 


	#New declared : request direct command 
	def Channel_GetListBySatellite( self, aType, aMode, aSort, aLongitude, aBand, aReopen = False ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			if aReopen :
				channelDB = ElisChannelDB()
				return channelDB.Channel_GetList( aType, aMode, aSort, aLongitude, aBand )
				channelDB.Close()
			else :
				return self.mChannelDB.Channel_GetList( aType, aMode, aSort, aLongitude, aBand )
		else :
			return self.mCommander.Channel_GetListBySatellite( aType, aMode, aSort, aLongitude, aBand )

	def Channel_GetListByFTACas( self, aType, aMode, aSort, aCAid, aReopen = False ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			if aReopen :
				channelDB = ElisChannelDB()
				return channelDB.Channel_GetList( aType, aMode, aSort, None, None, aCAid )
				channelDB.Close()
			else :
				return self.mChannelDB.Channel_GetList( aType, aMode, aSort, None, None, aCAid )
		else :
			return self.mCommander.Channel_GetListByFTACas( aType, aMode, aSort, aCAid )

	def Channel_GetListByFavorite( self, aType, aMode, aSort, aFavName, aReopen = False ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			if aReopen :
				channelDB = ElisChannelDB()
				return channelDB.Channel_GetList( aType, aMode, aSort, None, None, None, aFavName )
				channelDB.Close()
			else :
				return self.mChannelDB.Channel_GetList( aType, aMode, aSort, None, None, None, aFavName )
		else :
			return self.mCommander.Channel_GetListByFavorite( aType, aMode, aSort, aFavName )

	def Channel_Lock( self, aLock, aIChannel ) :
		return self.mCommander.Channel_Lock( aLock, aIChannel )

	def Channel_Skip( self, aSet, aIChannel ) :
		return self.mCommander.Channel_Skip( aSet, aIChannel )

	def Favoritegroup_AddChannel( self, aGroupName, aNumber, aServieType ) :
		return self.mCommander.Favoritegroup_AddChannel( aGroupName, aNumber, aServieType )

	def Favoritegroup_RemoveChannel( self, aGroupName, aNumber, aServieType ) :
		return self.mCommander.Favoritegroup_RemoveChannel( aGroupName, aNumber, aServieType )

	def FavoriteGroup_MoveChannels( self, aGroupName, aInsertPosition, aServieType, aIChannel ) :
		return self.mCommander.FavoriteGroup_MoveChannels( aGroupName, aInsertPosition, aServieType, aIChannel )

	def Favoritegroup_Create( self, aGroupName, aServieType ) :
		return self.mCommander.Favoritegroup_Create( aGroupName, aServieType )

	def Favoritegroup_ChangeName( self, aGroupName, aServieType, aGroupNewName ) :
		return self.mCommander.Favoritegroup_ChangeName( aGroupName, aServieType, aGroupNewName )

	def Favoritegroup_Remove( self, aGroupName, aServieType ) :
		return self.mCommander.Favoritegroup_Remove( aGroupName, aServieType )

	def Channel_Move( self, aServieType, aNumber, aIChannel ) :
		return self.mCommander.Channel_Move( aServieType, aNumber, aIChannel )

	def Channel_Save( self ) :
		return self.mCommander.Channel_Save( )

	def Channel_Backup( self ) :
		return self.mCommander.Channel_Backup( )

	def Channel_Restore( self, aRestore ) :
		return self.mCommander.Channel_Restore( aRestore )

	def Channel_Delete( self, aIChannel ) :
		return self.mCommander.Channel_Delete( aIChannel )

	def Channel_DeleteByNumber( self, aType, aNumList ) :
		return self.mCommander.Channel_DeleteByNumber( aType, aNumList )

	def Channel_DeleteAll( self ) :
		return self.mCommander.Channel_DeleteAll( )

	def Channel_SetInitialBlank( self, aBlank ) :
		return self.mCommander.Channel_SetInitialBlank( aBlank )

	def Channel_GetZappingList( self, aSync = 0 ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			return self.mCommander.Channel_GetZappingList( aSync )


	def Audiotrack_GetCount( self ) :
		return self.mCommander.Audiotrack_GetCount( )

	def Audiotrack_GetSelectedIndex( self ) :
		return self.mCommander.Audiotrack_GetSelectedIndex( )

	def Audiotrack_select( self, aIndex ) :
		return self.mCommander.Audiotrack_select( aIndex )

	def Audiotrack_Get( self, aIndex ) :
		return self.mCommander.Audiotrack_Get( aIndex )

	def Player_SetVIdeoSize( self, aX, aY, aW, aH ) :
		return self.mCommander.Player_SetVIdeoSize( aX, aY, aW, aH ) 

	def Player_VideoBlank( self, aBlank, aForce ) :
		return self.mCommander.Player_VideoBlank( aBlank, aForce )

	def Player_AVBlank( self, aBlank, aForce ) :
		return self.mCommander.Player_AVBlank( aBlank, aForce )

	def Player_GetStatus( self ) :
		return self.mCommander.Player_GetStatus( )

	def Player_Resume( self ) :
		return self.mCommander.Player_Resume( )

	def Player_Pause( self ) :
		return self.mCommander.Player_Pause( )

	def Player_Stop( self ) :
		return self.mCommander.Player_Stop( )

	def Player_SetSpeed( self, aSpeed ) :
		return self.mCommander.Player_SetSpeed( aSpeed )

	def Player_JumpToIFrame( self, aMiliSec ) :
		return self.mCommander.Player_JumpToIFrame( aMiliSec )


	def Player_StartTimeshiftPlayback( self, aPlayBackMode, aData ) :
		return self.mCommander.Player_StartTimeshiftPlayback( aPlayBackMode, aData )


	def Player_StartInternalRecordPlayback( self, aRecordKey, aServiceType, aOffsetMS, aSpeed ) :
		return self.mCommander.Player_StartInternalRecordPlayback( aRecordKey, aServiceType, aOffsetMS, aSpeed )


	def Record_GetRunningRecorderCount( self ) :
		return self.mCommander.Record_GetRunningRecorderCount( )

	def Record_GetRunningRecordInfo( self, aIndex ) :
		return self.mCommander.Record_GetRunningRecordInfo( aIndex )


	def Record_GetCount( self, aServiceType ) :
		if SUPPORT_RECORD_DATABASE == True :	
			return self.mRecordDB.Record_GetCount( aServiceType )
		else :
			return self.mCommander.Record_GetCount( aServiceType )


	def Record_GetList( self, aServiceType ) :
		if SUPPORT_RECORD_DATABASE == True :	
			return self.mRecordDB.Record_GetList( aServiceType )		
		else :
			recordList = []
			count = self.Record_GetCount( aServiceType )
			for i in range( count ) :
				recInfo = self.Record_GetRecordInfo( i, aServiceType )
				recordList.append( recInfo )
			return recordList

	def Record_GetRecordInfo( self, aIndex, aServiceType ) :
		if SUPPORT_RECORD_DATABASE == True :	
			return self.mRecordDB.Record_GetRecordInfo( aServiceType )
		else :
			return self.mCommander.Record_GetRecordInfo( aIndex, aServiceType )


	def Record_DeleteRecord( self, aKey, aServiceType ) :
		return self.mCommander.Record_DeleteRecord( aKey, aServiceType )


	def Record_SetLock(self, aKey, aServiceType, aLock ) :
		return self.mCommander.Record_SetLock( aKey, aServiceType, aLock )


	def Record_Rename(self, aKey, aServiceType, aNewName ) :
		return self.mCommander.Record_Rename( aKey, aServiceType, aNewName )

	def Timer_StopRecordingByRecordKey( self, aKey ) :
		return self.mCommander.Timer_StopRecordingByRecordKey( aKey )

	def Timer_GetTimerList( self ) :
		if SUPPORT_TIMER_DATABASE == True :
			return self.mTimerDB.Timer_GetTimerList()
		else :
			timerList = []
			timerCount = self.Timer_GetTimerCount( )

			for i in range( timerCount ) :
				timer = self.Timer_GetByIndex( i )
				timerList.append( timer )

			return timerList


	def Timer_GetTimerCount( self ) :
		if SUPPORT_TIMER_DATABASE == True :
			return self.mTimerDB.Timer_GetTimerCount()
		else :
			return self.mCommander.Timer_GetTimerCount()


	def Timer_GetById( self, aTimderId ) :
		if SUPPORT_TIMER_DATABASE == True :
			return self.mTimerDB.Timer_GetById( aTimderId )
		else :	
			return self.mCommander.Timer_GetById( aTimderId )


	def Timer_GetByIndex( self, aIndex ) :
		if SUPPORT_TIMER_DATABASE == True :
			return self.mTimerDB.Timer_GetByIndex( aIndex )
		else :	
			return self.mCommander.Timer_GetByIndex( aIndex )


	def Timer_AddOTRTimer( self, aFromEPG, aFixedDuration, aCopyTimeshift, aTimerName, aForceDecrypt, aEventId, aSid, aTsid, aOnid) : 
		return self.mCommander.Timer_AddOTRTimer( aFromEPG, aFixedDuration, aCopyTimeshift, aTimerName, aForceDecrypt, aEventId, aSid, aTsid, aOnid )


	def Timer_AddEPGTimer( self, aForceDecrypt, aForceThisEvent, aEPG  ) : 
		#ToDO : Change as AddEPGTimer
		LOG_TRACE('')
		aEPG.printdebug()
		LOG_TRACE('')
		epgList = []
		epgList.append( aEPG )
		return self.mCommander.Timer_AddEPGTimer( aForceDecrypt, aForceThisEvent, epgList )


	def Timer_DeleteTimer( self, aTimerId ) :
		return self.mCommander.Timer_DeleteTimer( aTimerId )


	def Timer_GetRunningTimers( self ) :
		return self.mCommander.Timer_GetRunningTimers( )

