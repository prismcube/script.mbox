
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

		LOG_TRACE('')
		self.Load()
		LOG_TRACE('')

		#self.mEventBus.Register( self )


	@classmethod
	def GetName(cls):
		return cls.__name__


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

		self.LoadPropertyLimit( )

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
		self.LoadChannelList( )


		# DATE
		self.mLocalOffset = self.mCommander.Datetime_GetLocalOffset( )
		self.mLocalTime = self.mCommander.Datetime_GetLocalTime( )


	def LoadAllSatellite( self ) :
		self.mAllSatelliteList = self.mCommander.Satellite_GetList( ElisEnum.E_SORT_INSERTED )

		if self.mAllSatelliteList and self.mAllSatelliteList[0].mError == 0 :
		
			count =  len( self.mAllSatelliteList )
			LOG_TRACE('satellite count=%d' %count )
			from pvr.PublicReference import ClassToList
			LOG_TRACE('satellite[%s]'% ClassToList('convert', self.mAllSatelliteList) )

			for i in range( count ):
				satellite = self.mAllSatelliteList[i]
				hashKey = '%d:%d' % ( satellite.mLongitude, satellite.mBand )
				self.mAllSatelliteListHash[hashKey] = satellite
		else :
			LOG_ERR('Has no Satellite')
 

	def LoadConfiguredSatellite( self ) :
		self.mConfiguredSatelliteList = []
		self.mConfiguredSatelliteList = self.mCommander.Satellite_GetConfiguredList( ElisEnum.E_SORT_NAME )

		if self.mConfiguredSatelliteList and self.mConfiguredSatelliteList[0].mError == 0 :
			pass
		else :
			LOG_WARN('Has no Configured Satellite')

		self.mConfiguredSatelliteListTuner1 = []
		self.mConfiguredSatelliteListTuner1 = self.mCommander.Satelliteconfig_GetList( E_TUNER_1 )

		if self.mConfiguredSatelliteListTuner1 and self.mConfiguredSatelliteListTuner1[0].mError == 0 :
			pass
		else :
			LOG_WARN('Has no Configured Satellite Tuner 1')

		self.mConfiguredSatelliteListTuner2 = []
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
				transponder = self.mCommander.Transponder_GetList( satellite.mLongitude, satellite.mBand )
				self.mTransponderList.append( transponder )
				hashKey = '%d:%d' % ( satellite.mLongitude, satellite.mBand )
				self.mTransponderListHash[hashKey] = transponder
		else :
			LOG_WARN('Has no Configured Satellite')
		
	@DataLock
	def Satellite_GetAllSatelliteList( self ) :
		return self.mAllSatelliteList


	@DataLock
	def Satellite_ConfiguredTunerSatellite( self, aTunerNumber ) :
		if aTunerNumber == E_TUNER_1 :
			if self.mConfiguredSatelliteListTuner1 :
				return self.mConfiguredSatelliteListTuner1
			else :
				return self.mCommander.Satelliteconfig_GetList( E_TUNER_1 )
				
		elif aTunerNumber == E_TUNER_2 :
			if self.mConfiguredSatelliteListTuner2 :
				return self.mConfiguredSatelliteListTuner2
			else :
				return self.mCommander.Satelliteconfig_GetList( E_TUNER_2 )

		else :
			LOG_ERR( 'Unknown Tuner Number %s' % aTunerNumber )


	@DataLock
	def Satellite_GetConfiguredList( self ) :
		if self.mConfiguredSatelliteList :
			return self.mConfiguredSatelliteList
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


	def LoadChannelList( self ) :
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
		
	

	def LoadZappingmode( self ) :
		self.mZappingMode = self.mCommander.Zappingmode_GetCurrent( )
		self.mCurrentChannel = self.mCommander.Channel_GetCurrent( )

	def LoadZappingList( self ) :
		serviceType = ElisEnum.E_SERVICE_TYPE_TV
		if self.mZappingMode :
			serviceType = self.mZappingMode.mServiceType
		self.mListCasList   = self.mCommander.Fta_cas_GetList( serviceType )
		self.mListFavorite  = self.mCommander.Favorite_GetList( serviceType )

	def LoadPropertyLimit( self ) :
		self.mPropertyPincode = ElisPropertyInt( 'PinCode', self.mCommander ).GetProp( )
		self.mPropertyAge = ElisPropertyEnum( 'Age Limit', self.mCommander ).GetProp( )

	def Zappingmode_SetCurrent( self , aZappingMode ) :
		if self.mCommander.Zappingmode_SetCurrent( aZappingMode ) == True :
			self.mZappingMode = aZappingMode

	@DataLock
	def Zappingmode_GetCurrent( self ) :
		return self.mZappingMode

	@DataLock
	def Fta_cas_GetList( self ) :
		return self.mListCasList

	@DataLock
	def Favorite_GetList( self ) :
		return self.mListFavorite

	@DataLock
	def Channel_GetList( self ) :
		return self.mChannelList

	@DataLock
	def Channel_GetCurrent( self ) :
		return self.mCurrentChannel


	def Channel_SetCurrent( self, aChannelNumber, aServiceType ) :
		self.mCurrentEvent = None
		if self.mCommander.Channel_SetCurrent( aChannelNumber, aServiceType ) == True :
			cacheChannel = self.mChannelListHash.get( aChannelNumber, None )
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
				satellite = self.mAllSatelliteListHash.get( hashKey, None )
				return satellite

			else :
				LOG_ERR('Not Supported Carrier type =%d' %carrier.mCarrierType )

		return None

	def Epgevent_GetList( self, aChannel, aTestTime=0 ) :
		try :
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

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		return None

	@DataLock
	def Epgevent_GetEvent( self, aEvent ) :
		hashKey = '%d:%d:%d:%d' %( aEvent.mEventId, aEvent.mSid, aEvent.mTsid, aEvent.mOnid )
		event = self.mEPGListHash.get( hashKey, None )

		if event :
			return event

		return None


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

	def Channel_GetList_Elis( self, aType, aMode, aSort ) :
		return self.mCommander.Channel_GetList( aType, aMode, aSort )

	def Channel_GetCurrent_Elis( self ) :
		return self.mCommander.Channel_GetCurrent( )

	def Channel_SetCurrent_Elis( self, aChannelNumber, aServiceType ) :
		return self.mCommander.Channel_SetCurrent( aChannelNumber, aServiceType )

	def Zappingmode_GetCurrent_Elis( self ) :
		return self.mCommander.Zappingmode_GetCurrent( )

	def Satellite_GetConfiguredList_Elis( self, aSortMode ) :
		return self.mCommander.Satellite_GetConfiguredList( aSortMode )

	def Fta_cas_GetList_Elis( self, aServiceType ) :
		return self.mCommander.Fta_cas_GetList( aServiceType )

	def Favorite_GetList_Elis( self, aServieType ) :
		return self.mCommander.Favorite_GetList( aServieType )

	def Satellite_GetByChannelNumber_Elis( self, aNumber, aType ) :
		return self.mCommander.Satellite_GetByChannelNumber( aNumber, aType )

	#New declared : request direct command 

	def Channel_GetListBySatellite( self, aType, aMode, aSort, aLongitude, aBand ) :
		return self.mCommander.Channel_GetListBySatellite( aType, aMode, aSort, aLongitude, aBand )

	def Channel_GetListByFTACas( self, aType, aMode, aSort, aCAid ) :
		return self.mCommander.Channel_GetListByFTACas( aType, aMode, aSort, aCAid )

	def Channel_GetListByFavorite( self, aType, aMode, aSort, aFavName ) :
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

	def Channel_Delete( self, aIChannel ) :
		return self.mCommander.Channel_Delete( aIChannel )

	def Favoritegroup_Create( self, aGroupName, aServieType ) :
		return self.mCommander.Favoritegroup_Create( aGroupName, aServieType )

	def Favoritegroup_ChangeName( self, aGroupName, aServieType, aGroupNewName ) :
		return self.mCommander.Favoritegroup_ChangeName( aGroupName, aServieType, aGroupNewName )

	def Favoritegroup_Remove( self, aGroupName, aServieType ) :
		return self.mCommander.Favoritegroup_Remove( aGroupName, aServieType )

	def Channel_Move( self, aServieType, aNumber, aIChannel ) :
		return self.mCommander.Channel_Move( aServieType, aNumber, aIChannel )

	def Player_SetVIdeoSize( self, aX, aY, aW, aH ) :
		return self.mCommander.Player_SetVIdeoSize( aX, aY, aW, aH ) 

	def Channel_Save( self ) :
		return self.mCommander.Channel_Save( )

	def Channel_Backup( self ) :
		return self.mCommander.Channel_Backup( )

	def Channel_Restore( self, aRestore ) :
		return self.mCommander.Channel_Restore( aRestore )

	def Channel_DeleteAll( self ) :
		return self.mCommander.Channel_DeleteAll( )

	def Player_VideoBlank( self, aBlank, aForce ) :
		return self.mCommander.Player_VideoBlank( aBlank, aForce )

	def Player_AVBlank( self, aBlank, aForce ) :
		return self.mCommander.Player_AVBlank( aBlank, aForce )

	def Channel_SetInitialBlank( self, aBlank ) :
		return self.mCommander.Channel_SetInitialBlank( aBlank )


