import thread

import pvr.ElisMgr
from decorator import decorator
from ElisEventClass import *
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.GuiConfig import *

import sys
if sys.platform == 'win32' :
	gFlagUseDB = False
else :
	gFlagUseDB = True
print 'mBox----------------use db[%s]'% gFlagUseDB

SUPPORT_EPG_DATABASE = gFlagUseDB
SUPPORT_CHANNEL_DATABASE = gFlagUseDB
SUPPORT_TIMER_DATABASE = gFlagUseDB
SUPPORT_RECORD_DATABASE = gFlagUseDB


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
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )

		self.mZappingMode						= None
		self.mChannelList						= None
		self.mAllChannelList					= None
		self.mCurrentChannel					= None
		self.mOldChannel						= None
		self.mLocalOffset						= 0
		self.mLocalTime							= 0
		self.mAllSatelliteList					= None
		self.mConfiguredSatelliteList			= None
		self.mConfiguredSatelliteListTuner1		= None
		self.mConfiguredSatelliteListTuner2		= None
		self.mTransponderLists					= None
		self.mEPGList							= None
		self.mCurrentEvent						= None
		self.mListCasList						= None
		self.mListFavorite						= None
		self.mPropertyAge						= 0
		self.mPropertyPincode					= -1
		self.mCacheReload						= False
		self.mIsEmptySatelliteInfo				= False

		self.mChannelListHash					= {}
		self.mAllSatelliteListHash				= {}
		self.mTransponderListHash				= {}
		self.mEPGListHash						= {}
		self.mEPGList 							= None

		self.mChannelListDBTable				= E_TABLE_ALLCHANNEL
		self.mEpgDB = None
		self.mChannelDB = None
		self.mTimerDB = None
		self.mRecordDB = None		

		self.mSkip = False

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

		self.mPropertyPincode = ElisPropertyEnum( 'PinCode', self.mCommander ).GetProp( )
		self.mPropertyAge = ElisPropertyEnum( 'Age Limit', self.mCommander ).GetProp( )

		self.mRecordingCount = 0
		
		self.Load( )


	@classmethod
	def GetName(cls):
		return cls.__name__


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
		self.LoadZappingmode( )
		self.LoadZappingList( )


		#SatelliteList
		self.LoadAllSatellite( )
		self.LoadConfiguredSatellite( )
		self.LoadConfiguredTransponder( )

		# Channel
		#self.LoadChannelList( )
		self.ReLoadChannelListByRecording( )
		if self.mChannelList :
			LOG_TRACE('recCount[%s] ChannelCount[%s]'% (self.mRecordingCount, len(self.mChannelList) ) )
		else :
			LOG_TRACE('recCount[%s] ChannelCount[None]'% self.mRecordingCount )

		self.mRecordingCount = self.Record_GetRunningRecorderCount()		

		# DATE
		self.LoadTime( )


	def LoadVolumeToSetGUI( self ) :
		volume = self.mCommander.Player_GetVolume( )
		LOG_TRACE( 'playerVolume[%s]'% volume)

		volumeString = 'setvolume(%s)'% volume
		xbmc.executehttpapi(volumeString)


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
			if count == 0 :
				self.SetEmptySatelliteInfo( True )
			else :
				self.SetEmptySatelliteInfo( False )

			for i in range( count ):
				satellite = self.mAllSatelliteList[i]
				hashKey = '%d:%d' % ( satellite.mLongitude, satellite.mBand )
				self.mAllSatelliteListHash[hashKey] = satellite
		else :
			self.SetEmptySatelliteInfo( True )
			LOG_ERR('Has no Satellite')


	def SetEmptySatelliteInfo( self, aFlag ) :
		self.mIsEmptySatelliteInfo = aFlag


	def GetEmptySatelliteInfo( self ) :
		return self.mIsEmptySatelliteInfo


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
		self.mTransponderLists = []
		self.mTransponderListHash = {}

	 	if self.mConfiguredSatelliteList and self.mConfiguredSatelliteList[0].mError == 0 :
			for satellite in self.mConfiguredSatelliteList :
				if SUPPORT_CHANNEL_DATABASE	== True :
					transponderList = self.mChannelDB.Transponder_GetList( satellite.mLongitude, satellite.mBand )
				else :
					transponderList = self.mCommander.Transponder_GetList( satellite.mLongitude, satellite.mBand )
				self.mTransponderLists.append( transponderList )
				hashKey = '%d:%d' % ( satellite.mLongitude, satellite.mBand )
				self.mTransponderListHash[hashKey] = transponderList
		else :
			LOG_WARN('Has no Configured Satellite')


	def LoadGetListEpgByChannel( self ) :
		if SUPPORT_EPG_DATABASE	== True :
			#Live EPG
			gmtFrom  = self.Datetime_GetLocalTime()
			#gmtFrom  = self.mTimeshift_curTime
			gmtUntil = gmtFrom + ( 3600 * 24 * 7 )
			maxCount = 100
			LOG_TRACE('-------------------------------------------')
			LOG_TRACE('ch.mNumber[%s] sid[%s] tsid[%s] onid[%s]'% ( self.mCurrentChannel.mNumber, self.mCurrentChannel.mSid, self.mCurrentChannel.mTsid, self.mCurrentChannel.mOnid ) )
			if self.mCurrentChannel == None or self.mCurrentChannel.mError != 0 :
				return None

			self.mEPGList = self.Epgevent_GetListByChannel( self.mCurrentChannel.mSid, self.mCurrentChannel.mTsid, self.mCurrentChannel.mOnid, gmtFrom, gmtUntil, maxCount )

			"""
			from pvr.GuiHelper import ClassToList 
			if self.mEPGList != None and len(self.mEPGList) > 0 :
				LOG_TRACE('epgList len[%s] [%s]'% (len(self.mEPGList), ClassToList('convert', self.mEPGList) ) )
			else :
				LOG_TRACE('epgList None')
			"""


	@DataLock
	def GetAllSatelliteList( self ) :
		return self.mAllSatelliteList


	def GetConfiguredSatelliteListByTunerIndex( self, aTunerNumber ) :
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
	def GetFormattedSatelliteNameList( self ) :
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
	def GetSatelliteByIndex( self, aIndex ) :
		return self.mAllSatelliteList[ aIndex ]


	def GetFormattedSatelliteName( self, aLongitude, aBand ) :
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


	def GetTransponderListBySatellite( self, aLongitude, aBand ) :
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


	def GetFormattedTransponderList( self, aLongitude, aBand ) :
		tmptransponderList = []
		transponderList = None
		
		tmptransponderList = self.GetTransponderListBySatellite( aLongitude, aBand )
		
		if tmptransponderList and tmptransponderList[0].mError == 0 :
			transponderList = []
	 		for i in range( len( tmptransponderList ) ) :
				transponderList.append( '%d %d MHz %d KS/s' % ( ( i + 1 ), tmptransponderList[i].mFrequency, tmptransponderList[i].mSymbolRate ) )

		return transponderList


	def GetTransponderListByIndex( self, aLongitude, aBand, aIndex ) :
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


	def GetChangeDBTableChannel( self ) :
		ret = -1
		if SUPPORT_CHANNEL_DATABASE	== True :
			ret = self.mChannelListDBTable

		return ret


	def SetChangeDBTableChannel( self, aTable ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			self.mChannelListDBTable = aTable


	def SetSkipChannelView( self, aSkip ) :
		if SUPPORT_CHANNEL_DATABASE :
			self.mSkip = aSkip


	def ReLoadChannelListByRecording( self ) :
		self.mCacheReload = True
		isRunRec = self.Record_GetRunningRecorderCount( )
		if isRunRec > 0 :
			#use zapping table 
			self.SetChangeDBTableChannel( E_TABLE_ZAPPING )
 
		else :
			self.SetChangeDBTableChannel( E_TABLE_ALLCHANNEL )

		self.Channel_GetZappingList( )
		self.LoadChannelList( FLAG_ZAPPING_LOAD )


	def LoadChannelList( self, aSync = 0, aType = ElisEnum.E_SERVICE_TYPE_TV, aMode = ElisEnum.E_MODE_ALL, aSort = ElisEnum.E_SORT_BY_NUMBER ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			#self.Channel_GetZappingList( )
			mType = aType
			mMode = aMode
			mSort = aSort
		
			if aSync == 0 and self.mZappingMode :
				mType = self.mZappingMode.mServiceType
				mMode = self.mZappingMode.mMode
				mSort = self.mZappingMode.mSortingMode

			if mMode == ElisEnum.E_MODE_ALL :
				tmpChannelList = self.Channel_GetList( True, mType, mMode, mSort )

			elif mMode == ElisEnum.E_MODE_SATELLITE :
				mLongitude = self.mZappingMode.mSatelliteInfo.mLongitude
				mBand = self.mZappingMode.mSatelliteInfo.mBand
				tmpChannelList = self.Channel_GetListBySatellite( mType, mMode, mSort, mLongitude, mBand )

			elif mMode == ElisEnum.E_MODE_CAS :
				mCaid = self.mZappingMode.mCasInfo.mCAId
				tmpChannelList = self.Channel_GetListByFTACas( mType, mMode, mSort, mCaid )
				
			elif mMode == ElisEnum.E_MODE_FAVORITE :
				mFavName = self.mZappingMode.mFavoriteGroup.mGroupName
				tmpChannelList = self.Channel_GetListByFavorite( mType, mMode, mSort, mFavName )

			elif mMode == ElisEnum.E_MODE_NETWORK :
				return None

		else:
			tmpChannelList = self.mCommander.Channel_GetList( self.mZappingMode.mServiceType, self.mZappingMode.mMode, self.mZappingMode.mSortingMode )


		oldCount = 0
		newCount = 0
		if self.mChannelList :
			oldCount = len( self.mChannelList )
		if tmpChannelList :
			newCount = len( tmpChannelList )
		if oldCount != newCount :
			self.mCacheReload = True


		prevChannel = None
		nextChannel = None
		self.mChannelListHash = {}

		if newCount < 1 :
			LOG_TRACE('count=%d'% newCount)
			self.mCacheReload = True
			self.Player_AVBlank( True, False )
			#self.Channel_InvalidateCurrent( )
			self.Frontdisplay_SetMessage('NoChannel')
			LOG_TRACE('-------------------------------------------')

		#if self.mChannelList and tmpChannelList :
		#	LOG_TRACE('oldcount[%d] newcount[%s]'% (len(self.mChannelList), len(tmpChannelList)) )

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
		if SUPPORT_CHANNEL_DATABASE	== True :
			self.mZappingMode = self.Zappingmode_GetCurrent( True )
			self.mCurrentChannel = self.mCommander.Channel_GetCurrent( )
		else :
			self.mZappingMode = self.mCommander.Zappingmode_GetCurrent( )
			self.mCurrentChannel = self.mCommander.Channel_GetCurrent( )


	def LoadZappingList( self ) :
		serviceType = ElisEnum.E_SERVICE_TYPE_TV
		if self.mZappingMode :
			serviceType = self.mZappingMode.mServiceType

		if SUPPORT_CHANNEL_DATABASE	== True :
			self.mListCasList   = self.mCommander.Fta_cas_GetList( serviceType )
			self.mListFavorite = self.Favorite_GetList( True, serviceType )
		else :
			self.mListCasList   = self.mCommander.Fta_cas_GetList( serviceType )
			self.mListFavorite  = self.mCommander.Favorite_GetList( serviceType )

	def Zappingmode_SetCurrent( self, aZappingMode ) :
		ret = False
		zappingList = []
		zappingList.append( aZappingMode )
		ret = self.mCommander.Zappingmode_SetCurrent( zappingList )
		if ret == True :
			self.mZappingMode = aZappingMode

		return ret


	def Zappingmode_GetCurrent( self, aReload = 0 ) :
		if aReload :
			if SUPPORT_CHANNEL_DATABASE	== True :
				channelDB = ElisChannelDB()
				self.mZappingMode = channelDB.Zappingmode_GetCurrent( )
				channelDB.Close()
			else :
				self.mZappingMode = self.mCommander.Zappingmode_GetCurrent( )

		return self.mZappingMode


	def Fta_cas_GetList( self, aServiceType = ElisEnum.E_SERVICE_TYPE_INVALID ) :
		if aServiceType :
			return self.mCommander.Fta_cas_GetList( aServiceType )
		else :
			return self.mListCasList


	def Favorite_GetList( self, aTemporaryReload = 0, aServiceType = ElisEnum.E_SERVICE_TYPE_INVALID ) :
		if aTemporaryReload :
			if SUPPORT_CHANNEL_DATABASE	== True :
				channelDB = ElisChannelDB()
				favList = channelDB.Favorite_GetList( aServiceType )
				channelDB.Close()
				return favList
			else :
				return self.mCommander.Favorite_GetList( aServiceType )
		else :
			return self.mListFavorite


	def Channel_GetList( self, aTemporaryReload = 0, aType = 0, aMode = 0, aSort = 0 ) :
		if aTemporaryReload :
			if SUPPORT_CHANNEL_DATABASE	== True :
				channelDB = ElisChannelDB()
				chList = channelDB.Channel_GetList( aType, aMode, aSort, -1, -1, -1, '', self.mSkip, self.mChannelListDBTable )
				channelDB.Close()
				return chList
			else :
				return self.mCommander.Channel_GetList( aType, aMode, aSort )

		else :
			return self.mChannelList

	def Channel_GetCount( self, aType = ElisEnum.E_SERVICE_TYPE_TV ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			channelDB = ElisChannelDB()
			chCount = channelDB.Channel_GetCount( aType, self.mChannelListDBTable )
			channelDB.Close()
			return chCount


	#ToDO : Call this function when channels are added or deleted. ( aServiceType = CurrentServieType, aUseCache=False )
	def Channel_GetAllChannels( self, aServiceType, aUseCache=True ) :
		LOG_TRACE( 'Reload AllChannels')
		if SUPPORT_CHANNEL_DATABASE	== True :
			LOG_TRACE( 'Reload AllChannels')		
			if aUseCache :
				LOG_TRACE( 'Reload AllChannels')			
				if self.mAllChannelList and len( self.mAllChannelList ) > 0 :
					LOG_TRACE( 'Reload AllChannels')				
					channel =  self.mAllChannelList[0]
					if channel.mServiceType == aServiceType :
						LOG_TRACE( 'Reload AllChannels')					
						return self.mAllChannelList

			LOG_TRACE( 'Reload AllChannels')

			channelDB = ElisChannelDB()
			self.mAllChannelList = channelDB.Channel_GetList( aServiceType, ElisEnum.E_MODE_ALL, ElisEnum.E_SORT_BY_NUMBER )
			channelDB.Close()
			return self.mAllChannelList

		else :
			return self.mCommander.Channel_GetList( aType, aMode, aSort )

		LOG_TRACE( 'Reload AllChannels')
		return None


	def Channel_GetCurrent( self, aTemporaryReload = 0 ) :
		if aTemporaryReload :
			return self.mCommander.Channel_GetCurrent( )

		return self.mCurrentChannel

	def Channel_GetOldChannel( self ) :
		return self.mOldChannel

	def Channel_SetCurrent( self, aChannelNumber, aServiceType ) :
		ret = False
		self.mCurrentEvent = None
		self.mOldChannel = self.Channel_GetCurrent( )
		if self.mCommander.Channel_SetCurrent( aChannelNumber, aServiceType ) == True :
			cacheChannel = self.mChannelListHash.get( aChannelNumber, None )
			if cacheChannel :		
				self.mCurrentChannel = cacheChannel.mChannel
				ret = True

		channel = self.Channel_GetCurrent( )
		self.Frontdisplay_SetMessage( channel.mName )
		return ret

	def Channel_SetCurrentSync( self, aChannelNumber, aServiceType ) :
		ret = False
		self.mCurrentEvent = None
		self.mOldChannel = self.Channel_GetCurrent( )
		if self.mCommander.Channel_SetCurrentAsync( aChannelNumber, aServiceType, 0 ) == True :
			cacheChannel = self.mChannelListHash.get( aChannelNumber, None )
			if cacheChannel :		
				self.mCurrentChannel = cacheChannel.mChannel
				ret = True

		channel = self.Channel_GetCurrent( )
		self.Frontdisplay_SetMessage( channel.mName )
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
	def Channel_GetByNumber( self, aNumber ) :

		cacheChannel = self.mChannelListHash.get(aNumber, None).mChannel
		if cacheChannel == None :
			return None

		channel =  cacheChannel
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
	def Satellite_GetByChannelNumber( self, aNumber, aRequestType = -1 ) :
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
				channelDB = ElisChannelDB()
				satelliteList = channelDB.Satellite_GetByChannelNumber( aNumber, aRequestType, self.mChannelListDBTable )
				channelDB.Close()
				return satelliteList
				
			else :
				return self.mCommander.Satellite_GetByChannelNumber( aNumber, aRequestType )

		return None


#	@DataLock
	def Epgevent_GetListByChannel( self, aSid, aTsid, aOnid, aGmtFrom, aGmtUntil, aMaxCount ) :

		eventList = None
		
		if SUPPORT_EPG_DATABASE	== True :
 			self.mEpgDB = ElisEPGDB()
 			eventList = self.mEpgDB.Epgevent_GetList( aSid, aTsid, aOnid, aGmtFrom, aGmtUntil, aMaxCount )
 			self.mEpgDB.Close()

			"""
			from pvr.GuiHelper import ClassToList
			#test
			for iEPG in eventList :
				ret=[]
				ret.append(iEPG)
				LOG_TRACE('iEPG_DB[%s]'% ClassToList('convert', ret) )

			#test
			ElisListCMD = self.mCommander.Epgevent_GetList( aSid, aTsid, aOnid, aGmtFrom, aGmtUntil, aMaxCount )
			if ElisListCMD :
				for iEPG in ElisListCMD :
					ret=[]
					ret.append(iEPG)
					LOG_TRACE('iEPG_CMD[%s]'% ClassToList('convert', ret) )
			"""

		else:
			eventList = self.mCommander.Epgevent_GetList( aSid, aTsid, aOnid, aGmtFrom, aGmtUntil, aMaxCount )

		return eventList


#	@DataLock
	def Epgevent_GetCurrent( self, aSid, aTsid, aOnid ) :

		eventList = None
		
		if SUPPORT_EPG_DATABASE	== True :
			self.mEpgDB = ElisEPGDB()
			eventList = self.mEpgDB.Epgevent_GetCurrent( aSid, aTsid, aOnid, self.Datetime_GetGMTTime() )
			self.mEpgDB.Close()
		else:
			eventList = self.mCommander.Epgevent_GetList( aSid, aTsid, aOnid, 0, 0, 1 )
			if eventList :
				eventList = eventList[0]

		return eventList


	def Epgevent_GetCurrentList( self  ) :

		eventList = None

		if SUPPORT_EPG_DATABASE	== True :
			self.mEpgDB = ElisEPGDB()
			eventList = self.mEpgDB.Epgevent_GetCurrentList( self.Datetime_GetGMTTime() )
			self.mEpgDB.Close()

		else:
			return None

		return eventList



#	@DataLock
	def Epgevent_GetFollowing( self, aSid, aTsid, aOnid ) :

		eventList = None

		if SUPPORT_EPG_DATABASE	== True :
			self.mEpgDB = ElisEPGDB()
			eventList = self.mEpgDB.Epgevent_GetFollowing( aSid, aTsid, aOnid, self.Datetime_GetGMTTime() )
			self.mEpgDB.Close()
		else:
			eventList = self.mCommander.Epgevent_GetList( aSid, aTsid, aOnid, 1, 1, 1 )

		return eventList


#	@DataLock
	def Epgevent_GetFollowingList( self ) :

		eventList = None

		if SUPPORT_EPG_DATABASE	== True :
			self.mEpgDB = ElisEPGDB()
			eventList = self.mEpgDB.Epgevent_GetFollowingList( self.Datetime_GetGMTTime() )
			self.mEpgDB.Close()
		else:
			return None

		return eventList


	def Epgevent_GetCurrentByChannelFromEpgCF( self, aSid, aTsid, aOnid ) :
		eventList = None

		if SUPPORT_EPG_DATABASE	== True :
			ret = self.mCommander.Epgevent_GetChannelDB( aSid, aTsid, aOnid )
			if ret :
				self.mEpgDB = ElisEPGDB( E_EPG_DB_CF )
				eventList = self.mEpgDB.Epgevent_GetCurrentByChannelFromEpgCF( E_EPG_DB_CF_GET_BY_CHANNEL )
				self.mEpgDB.Close()

		return eventList


	def Epgevent_GetListByChannelFromEpgCF( self, aSid, aTsid, aOnid ) :
		eventList = None

		if SUPPORT_EPG_DATABASE	== True :
			ret = self.mCommander.Epgevent_GetChannelDB( aSid, aTsid, aOnid )
			if ret :
				self.mEpgDB = ElisEPGDB( E_EPG_DB_CF )
				eventList = self.mEpgDB.Epgevent_GetListFromEpgCF( E_EPG_DB_CF_GET_BY_CHANNEL )
				self.mEpgDB.Close()

		return eventList


	def Epgevent_GetCurrentListByEpgCF( self, aSerciveType ) :
		eventList = None

		if SUPPORT_EPG_DATABASE	== True :
			epgStart = 0 #end - start = 0 : all channel following
			epgEnd = 0

			ret = self.mCommander.Epgevnt_GetCurrentDB( aSerciveType, epgStart, epgEnd )
			if ret :
				self.mEpgDB = ElisEPGDB( E_EPG_DB_CF )
				eventList = self.mEpgDB.Epgevent_GetListFromEpgCF( E_EPG_DB_CF_GET_BY_CURRENT )
				self.mEpgDB.Close()

		return eventList


	def Epgevent_GetFollowingListByEpgCF( self, aSerciveType ) :
		eventList = None

		if SUPPORT_EPG_DATABASE	== True :
			epgStart = 0 #end - start = 0 : all channel following
			epgEnd = 0

			ret = self.mCommander.Epgevent_GetFollowingDB( aSerciveType, epgStart, epgEnd )
			if ret :
				self.mEpgDB = ElisEPGDB( E_EPG_DB_CF )
				eventList = self.mEpgDB.Epgevent_GetListFromEpgCF( E_EPG_DB_CF_GET_BY_FOLLOWING )
				self.mEpgDB.Close()

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
	def Channel_GetListBySatellite( self, aType, aMode, aSort, aLongitude, aBand ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			channelDB = ElisChannelDB()
			chList = channelDB.Channel_GetList( aType, aMode, aSort, aLongitude, aBand, -1, '', self.mSkip, self.mChannelListDBTable )
			channelDB.Close()
			return chList
		else :
			return self.mCommander.Channel_GetListBySatellite( aType, aMode, aSort, aLongitude, aBand )

	def Channel_GetListByFTACas( self, aType, aMode, aSort, aCAid ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			channelDB = ElisChannelDB()
			chList = channelDB.Channel_GetList( aType, aMode, aSort, None, None, aCAid, '', self.mSkip, self.mChannelListDBTable )
			channelDB.Close()
			return chList
		else :
			return self.mCommander.Channel_GetListByFTACas( aType, aMode, aSort, aCAid )

	def Channel_GetListByFavorite( self, aType, aMode, aSort, aFavName ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			channelDB = ElisChannelDB()
			chList = channelDB.Channel_GetList( aType, aMode, aSort, None, None, None, aFavName, self.mSkip, self.mChannelListDBTable )
			channelDB.Close()
			return chList
		else :
			return self.mCommander.Channel_GetListByFavorite( aType, aMode, aSort, aFavName )

	def Channel_Lock( self, aLock, aIChannel ) :
		return self.mCommander.Channel_Lock( aLock, aIChannel )

	def Channel_LockByNumber( self, aLock, aType, aNumList ) :
		return self.mCommander.Channel_LockByNumber( aLock, aType, aNumList )

	def Channel_Skip( self, aSet, aIChannel ) :
		return self.mCommander.Channel_Skip( aSet, aIChannel )

	def Channel_SkipByNumber( self, aSet, aType, aNumList ) :
		return self.mCommander.Channel_SkipByNumber( aSet, aType, aNumList )

	def Favoritegroup_AddChannel( self, aGroupName, aNumber, aServieType ) :
		return self.mCommander.Favoritegroup_AddChannel( aGroupName, aNumber, aServieType )

	def Favoritegroup_AddChannelByNumber( self, aGroupName, aServieType, aNumList ) :
		return self.mCommander.Favoritegroup_AddChannelByNumber( aGroupName, aServieType, aNumList )

	def Favoritegroup_RemoveChannel( self, aGroupName, aNumber, aServieType ) :
		return self.mCommander.Favoritegroup_RemoveChannel( aGroupName, aNumber, aServieType )

	def Favoritegroup_RemoveChannelByNumber( self, aGroupName, aServieType, aNumList ) :
		return self.mCommander.Favoritegroup_RemoveChannelByNumber( aGroupName, aServieType, aNumList )

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
			recCount = self.Record_GetRunningRecorderCount( )
			LOG_TRACE('%d : %d' %(self.mRecordingCount, recCount))
			if self.mRecordingCount != recCount :
				self.mRecordingCount = recCount
			else :
				LOG_TRACE('skip getzapping list')
				return
 
			return self.mCommander.Channel_GetZappingList( aSync )

	def Channel_InvalidateCurrent( self ) :
		return self.mCommander.Channel_InvalidateCurrent( )

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

	def Player_SetMute( self, aMute ) :
		return self.mCommander.Player_SetMute( aMute )

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

	def RecordItem_GetEventInfo( self, aKey ) :
		return self.mCommander.RecordItem_GetEventInfo( aKey )

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
			return self.mRecordDB.Record_GetRecordInfo( aIndex, aServiceType )
		else :
			return self.mCommander.Record_GetRecordInfo( aIndex, aServiceType )


	def Record_GetRecordInfoByKey( self, aKey ) :
		return self.mCommander.Record_GetRecordInfoByKey( aKey )	


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
			timerDB = ElisTimerDB( )
			timerList = timerDB.Timer_GetTimerList( )
			timerDB.Close( )
			return timerList
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


	def Timer_EditRunningTimer(self , aTimerId, aNewEndTime) :
			return self.mCommander.Timer_EditRunningTimer( aTimerId, aNewEndTime )
	

	def Timer_GetById( self, aTimderId ) :
		if SUPPORT_TIMER_DATABASE == True :
			timerDB = ElisTimerDB( )
			timer = timerDB.Timer_GetById( aTimderId )
			timerDB.Close( )
			return timer
		else :	
			return self.mCommander.Timer_GetById( aTimderId )


	def Timer_GetByIndex( self, aIndex ) :
		if SUPPORT_TIMER_DATABASE == True :
			return self.mTimerDB.Timer_GetByIndex( aIndex )
		else :	
			return self.mCommander.Timer_GetByIndex( aIndex )


	def Timer_GetOTRInfo( self ) :
		return self.mCommander.Timer_GetOTRInfo( )


	def Timer_AddOTRTimer( self, aFromEPG, aFixedDuration, aCopyTimeshift, aTimerName, aForceDecrypt, aEventId, aSid, aTsid, aOnid) : 
		return self.mCommander.Timer_AddOTRTimer( aFromEPG, aFixedDuration, aCopyTimeshift, aTimerName, aForceDecrypt, aEventId, aSid, aTsid, aOnid )


	def Timer_AddEPGTimer( self, aForceDecrypt, aForceThisEvent, aEPG  ) : 
		#ToDO : Change as AddEPGTimer
		epgList = []
		epgList.append( aEPG )
		return self.mCommander.Timer_AddEPGTimer( aForceDecrypt, aForceThisEvent, epgList )


	def Timer_AddManualTimer( self ,  aChannelNo,  aServiceType,  aStartTime,  aDuration,  aTimerName,  aForceDecrypt ) :
		return self.mCommander.Timer_AddManualTimer( aChannelNo,  aServiceType,  aStartTime,  aDuration,  aTimerName,  aForceDecrypt )


	def Timer_AddWeeklyTimer( self ,  aChannelNo,  aServiceType,  aStartTime,  aExpiryTime,  aTimerName,  aWeeklyTimerCount,  aWeeklyTimer ) :
		return self.mCommander.Timer_AddWeeklyTimer( aChannelNo,  aServiceType,  aStartTime,  aExpiryTime,  aTimerName,  aWeeklyTimerCount,  aWeeklyTimer )


	def Timer_AddSeriesTimer( self ,  aEPGEvent ) :
		return self.mCommander.Timer_AddSeriesTimer( aEPGEvent )


	def Timer_AddKeywordTimer( self ,  aChannelNo,  aServiceType,  aKeyword,  aTitleOnly,  aForceDecrypt ) :
		return self.mCommander.Timer_AddKeywordTimer( aChannelNo,  aServiceType,  aKeyword,  aTitleOnly,  aForceDecrypt )


	def Timer_DeleteTimer( self, aTimerId ) :
		return self.mCommander.Timer_DeleteTimer( aTimerId )


	def Timer_GetRunningTimers( self ) :
		return self.mCommander.Timer_GetRunningTimers( )


	def Timer_EditOneWeeklyTimer( self, aTimerId, aDate, aStartTime, aDuration, aNewStartTime, aNewDuration) :
		return self.mCommander.Timer_EditWeeklyTimer( aTimerId, aDate, aStartTime, aDuration, aNewStartTime, aNewDuration )


	def Timer_AddOneWeeklyTimer( self, aTimerId, aDate, aStartTime, aDuration) :	
		return self.mCommander.Timer_AddWeeklyTimerItem( aTimerId, aDate, aStartTime, aDuration )

		
	def Timer_DeleteOneWeeklyTimer( self, aTimerId, aDate, aStartTime, aDuration ) :
		return self.mCommander.Timer_EditWeeklyTimer( aTimerId, aDate, aStartTime, aDuration, aStartTime, 0 ) 


	def Frontdisplay_SetMessage( self, aName ) :
		self.mCommander.Frontdisplay_SetMessage( aName )


	def GetRunnigTimerByChannel( self, aChannel=None ) :
		if aChannel == None :
			aChannel = self.Channel_GetCurrent( )

		runningTimers = self.Timer_GetRunningTimers( )

		findTimer = None

		if runningTimers :
			for timer in runningTimers :
				if aChannel.mSid == timer.mSid and aChannel.mTsid == timer.mTsid and aChannel.mOnid == timer.mOnid :
					findTimer = timer
					break

		return findTimer


	def ToggleTVRadio( self ) :

		try :
			LOG_TRACE( 'LAEL98 - TVRADIO' )

			zappingMode= self.Zappingmode_GetCurrent( )
			LOG_TRACE( 'LAEL98 Current ZappingMode' )
			zappingMode.printdebug( )

			LOG_TRACE( 'LAEL98' )
			newZappingMode = ElisIZappingMode( )
			LOG_TRACE( 'LAEL98 create ZappingMode' )
			newZappingMode.printdebug( )

			if zappingMode.mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
				newZappingMode.mServiceType = ElisEnum.E_SERVICE_TYPE_RADIO 
			else :
				newZappingMode.mServiceType = ElisEnum.E_SERVICE_TYPE_TV

			LOG_TRACE( 'LAEL98 new ZappingMode' )
			newZappingMode.printdebug( )

			self.Zappingmode_SetCurrent( newZappingMode )

			self.LoadZappingmode( )
			self.LoadZappingList( )
			self.LoadChannelList( )

			zappingMode= self.Zappingmode_GetCurrent( )
			zappingMode.printdebug( )
			self.Channel_InvalidateCurrent( )

			if zappingMode.mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
				lastChannelNumber = ElisPropertyInt( 'Last TV Number', self.mCommander ).GetProp( )
				self.Channel_SetCurrent( lastChannelNumber, ElisEnum.E_SERVICE_TYPE_TV )				
			else :
				lastChannelNumber = ElisPropertyInt( 'Last Radio Number', self.mCommander ).GetProp( )
				self.Channel_SetCurrent( lastChannelNumber, ElisEnum.E_SERVICE_TYPE_RADIO )				


			channel = self.Channel_GetCurrent( )
			LOG_TRACE( 'LAEL98 get Current Channel after zappingMode channge' )
			if channel :
				channel.printdebug( )
			elif self.mChannelList and len( self.mChannelList ) > 0 :
				self.Channel_SetCurrent( 1, zappingMode.mServiceType )							

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)


