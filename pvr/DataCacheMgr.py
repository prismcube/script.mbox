import thread, sys, copy
from decorator import decorator
from ElisEventClass import *
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
import pvr.ElisMgr
import pvr.Platform
import pvr.BackupSettings
from pvr.XBMCInterface import XBMC_GetVolume, XBMC_SetVolumeByBuiltin, XBMC_GetMute

from pvr.gui.GuiConfig import *
from pvr.GuiHelper import AgeLimit, SetDefaultSettingInXML, GetSelectedLongitudeString
if pvr.Platform.GetPlatform( ).IsPrismCube( ) :
	gFlagUseDB = True
	#from pvr.IpParser import *

else :
	gFlagUseDB = False


import sys
import os
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

print 'mBox----------------use db[%s] platform[%s]' %( gFlagUseDB, pvr.Platform.GetPlatform( ).GetName( ) )

SUPPORT_EPG_DATABASE     = gFlagUseDB
SUPPORT_CHANNEL_DATABASE = gFlagUseDB
SUPPORT_TIMER_DATABASE   = gFlagUseDB
SUPPORT_RECORD_DATABASE  = gFlagUseDB

if SUPPORT_EPG_DATABASE == True :
	from ElisEPGDB import ElisEPGDB

if SUPPORT_CHANNEL_DATABASE == True :
	from ElisChannelDB import ElisChannelDB

if SUPPORT_TIMER_DATABASE == True :
	from ElisTimerDB import ElisTimerDB

if SUPPORT_RECORD_DATABASE == True :
	from ElisRecordDB import ElisRecordDB

gDataCacheMgr = None
gDataLock = thread.allocate_lock( )


@decorator
def DataLock( func, *args, **kw ) :
	gDataLock.acquire( )
	try :
		result =  func( *args, **kw )
		return result

	finally:
		gDataLock.release( )


def GetInstance( ) :
	global gDataCacheMgr
	if not gDataCacheMgr :
		gDataCacheMgr = DataCacheMgr( )
	else :
		pass
		#print 'lael98 check already windowmgr is created'

	return gDataCacheMgr


class CacheChannel( object ) :
	def __init__( self, aChannel, aPrevKey, aNextKey ) :
		self.mChannel = aChannel
		self.mPrevKey = aPrevKey
		self.mNextKey = aNextKey


class DataCacheMgr( object ) :
	def __init__( self ) :
		self.mShutdowning = False
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )

		self.mZappingMode						= None
		self.mLastZappingMode					= ElisIZappingMode( )
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
		self.mTPListByChannelHash				= {}
		self.mAllSatelliteListHash				= {}
		self.mTransponderListHash				= {}
		self.mEPGListHash						= {}
		self.mEPGList 							= None
		self.mEPGData							= None

		self.mChannelListDBTable				= E_TABLE_ALLCHANNEL
		self.mEpgDB 							= None
		self.mChannelDB 						= None
		self.mTimerDB 							= None
		self.mRecordDB 							= None

		self.mPMTEvent							= None

		self.mParentLock						= True
		self.mParentLockPass					= False
		self.mIsPincodeDialog					= False
		self.mLockStatus 						= self.mCommander.Channel_GetStatus( )
		self.mAVBlankStatus 					= self.mCommander.Channel_GetInitialBlank( )
		self.mRecoverBlank 						= False
		self.mSkip 								= False
		self.mIsRunningHiddentest 				= False
		self.mStartMediaCenter					= False
		self.mDefaultHideWatched				= False
		self.mPlayingChannel					= False

		if SUPPORT_CHANNEL_DATABASE	 == True :
			self.mChannelDB = ElisChannelDB( )

		if SUPPORT_TIMER_DATABASE == True :
			self.mTimerDB = ElisTimerDB( )
			#TEST CODE
			"""
			count = self.mTimerDB.Timer_GetTimerCount( )
			LOG_TRACE('TIMER DB TEST count=%d' %count )
			for i in range( count ) :
				timer = self.mTimerDB.Timer_GetByIndex( i )
				timer.printdebug( )
			timerList = self.mTimerDB.Timer_GetTimerList( )
			LOG_TRACE('TIMER DB TEST2')
			if timerList :
				for timer in timerList :
					timer.printdebug( )
			"""

		if SUPPORT_RECORD_DATABASE == True :
			self.mRecordDB = ElisRecordDB( )
			#TEST CODE
			"""
			count = self.mRecordDB.Record_GetCount( ElisEnum.E_SERVICE_TYPE_TV )
			LOG_TRACE('RECORD DB TEST count=%d' %count )
			for i in range( count ) :
				record = self.mRecordDB.Record_GetRecordInfo( i, ElisEnum.E_SERVICE_TYPE_TV )
				record.printdebug( )
			recordList = self.mRecordDB.Record_GetList( ElisEnum.E_SERVICE_TYPE_TV )
			LOG_TRACE('RECORD DB TEST2')
			if recordList :
				for record in recordList :
					record.printdebug( )
			"""

		self.mPropertyAge = ElisPropertyEnum( 'Age Limit', self.mCommander ).GetProp( )
		self.mPropertyPincode = ElisPropertyEnum( 'PinCode', self.mCommander ).GetProp( )
		self.mPropertyChannelBannerTime = ElisPropertyEnum( 'Channel Banner Duration', self.mCommander ).GetProp( )
		self.mPropertyPlaybackBannerTime = ElisPropertyEnum( 'Playback Banner Duration', self.mCommander ).GetProp( )

		self.mRecordingCount = 0

		pvr.BackupSettings.BackupSettings( )
		self.Load( )


	@classmethod
	def GetName(cls) :
		return cls.__name__


	def Test( self ) :
		before = time.clock( )
		LOG_ERR('before=%s' %before )
		for i in range( 10 ) :
			self.mChannelList = self.mCommander.Channel_GetList( self.mZappingMode.mServiceType, self.mZappingMode.mMode, self.mZappingMode.mSortingMode )	

		after = time.clock( )
		LOG_ERR('after=%s' %after )		
		LOG_ERR('--------------> diff=%s' %( after - before ) )


	def Load( self ) :

		self.LoadVolumeToSetGUI( )
		#self.Frontdisplay_ResolutionByIdentified( )

		#Zapping Mode
		self.LoadZappingmode( )
		self.LoadZappingList( )
		#self.mLastZappingMode = copy.deepcopy( self.mZappingMode )

		#SatelliteList
		self.LoadAllSatellite( )
		self.LoadConfiguredSatellite( )
		self.LoadConfiguredTransponder( )

		# Channel
		#self.LoadChannelList( )
		self.ReLoadChannelListByRecording( )
		if self.mChannelList :
			LOG_TRACE('recCount[%s] ChannelCount[%s]'% ( self.mRecordingCount, len( self.mChannelList ) ) )
		else :
			LOG_TRACE('recCount[%s] ChannelCount[None]'% self.mRecordingCount )

		self.mRecordingCount = self.Record_GetRunningRecorderCount( )		

		# DATE
		self.LoadTime( )

		# SetPropertyNetworkAddress
		self.InitNetwork( )


	def InitNetwork( self ) :
		if pvr.Platform.GetPlatform( ).IsPrismCube( ) :
			import pvr.NetworkMgr as NetMgr
			ethernet = None
			if NetMgr.GetInstance( ).LoadEthernetService( ) :
				ethernet = NetMgr.GetInstance( ).GetCurrentEthernetService( )
			else :
				LOG_ERR( 'Ethernet device not configured' )
				
			if NetMgr.GetInstance( ).GetCurrentServiceType( ) == NETWORK_ETHERNET :
				if ethernet :
					addressIp, addressMask, addressGateway, addressNameServer = NetMgr.GetInstance( ).GetServiceAddress( ethernet )
					LOG_TRACE( 'Network address = %s, %s, %s, %s' % ( addressIp, addressMask, addressGateway, addressNameServer ) )
					NetMgr.GetInstance( ).SetNetworkProperty( addressIp, addressMask, addressGateway, addressNameServer )
				else :
					LOG_ERR( 'Ethernet device not configured' )
			else :
				if NetMgr.GetInstance( ).LoadSetWifiTechnology( ) :
					if NetMgr.GetInstance( ).LoadWifiService( ) :
						wifi = NetMgr.GetInstance( ).GetCurrentWifiService( )
						if wifi :
							addressIp, addressMask, addressGateway, addressNameServer = NetMgr.GetInstance( ).GetServiceAddress( wifi )
							LOG_TRACE( 'Network address = %s, %s, %s, %s' % ( addressIp, addressMask, addressGateway, addressNameServer ) )
							NetMgr.GetInstance( ).SetNetworkProperty( addressIp, addressMask, addressGateway, addressNameServer )
					else :
						LOG_ERR( 'Wifi service not configured' )
				else :
					LOG_ERR( 'Wifi device not configured' )


	def LoadVolumeToSetGUI( self ) :
		lastVolume = self.mCommander.Player_GetVolume( )
		lastMute = self.mCommander.Player_GetMute( )
		LOG_TRACE( 'last volume[%s] mute[%s]'% ( lastVolume, lastMute ) )

		if lastMute :
			self.mCommander.Player_SetMute( False )
			LOG_TRACE( 'mute off' )

		revisionVolume = abs( lastVolume - XBMC_GetVolume( ) )
		if revisionVolume >= VOLUME_STEP :
			#XBMC_SetVolume( lastVolume, lastMute )
			XBMC_SetVolumeByBuiltin( lastVolume, False )


	def LoadVolumeBySetGUI( self ) :
		mute = XBMC_GetMute( )
		volume = XBMC_GetVolume( )
		LOG_TRACE( 'GUI mute[%s] volume[%s]'% ( mute, volume ) )
		self.mCommander.Player_SetMute( mute )
		self.mCommander.Player_SetVolume( volume )


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

			for i in range( count ) :
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
			gmtFrom  = self.Datetime_GetLocalTime( )
			#gmtFrom  = self.mTimeshift_curTime
			gmtUntil = gmtFrom + ( 3600 * 24 * 7 )
			maxCount = 100
			#LOG_TRACE('ch.mNumber[%s] sid[%s] tsid[%s] onid[%s]'% ( self.mCurrentChannel.mNumber, self.mCurrentChannel.mSid, self.mCurrentChannel.mTsid, self.mCurrentChannel.mOnid ) )
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

		if satellite != None :
			dir = 'E'

			tmpLongitude  = aLongitude
			if tmpLongitude > 1800 :
				dir = 'W'
				tmpLongitude = 3600 - aLongitude

			formattedName = '%d.%d %s %s' % ( int( tmpLongitude / 10 ), tmpLongitude % 10, dir, satellite.mName )
			return formattedName

		return MR_LANG( 'Unknown' )


	def GetSatelliteName( self, aLongitude, aBand ) :
		hashKey = '%d:%d' % ( aLongitude, aBand )
		satellite = self.mAllSatelliteListHash.get( hashKey, None )

		if satellite :
			return satellite.mName

		return MR_LANG( 'Unknown' )


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
	 			if tmptransponderList[i].mPolarization == ElisEnum.E_LNB_HORIZONTAL :
	 				polarization = MR_LANG( 'Horizontal' )
	 			else :
	 				polarization = MR_LANG( 'Vertical' )
	 				
				transponderList.append( '%d %d MHz %d KS/s %s' % ( ( i + 1 ), tmptransponderList[i].mFrequency, tmptransponderList[i].mSymbolRate, polarization ) )

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


	def GetTunerIndexBySatellite( self, aLongitude, aBand ) :
		tunerEx = 0
		if self.mConfiguredSatelliteListTuner1 :
			for satellite in self.mConfiguredSatelliteListTuner1 :
				if satellite.mSatelliteLongitude == aLongitude and satellite.mBandType == aBand :
					tunerEx = tunerEx + E_CONFIGURED_TUNER_1

		if self.mConfiguredSatelliteListTuner2 :
			for satellite in self.mConfiguredSatelliteListTuner2 :
				if satellite.mSatelliteLongitude == aLongitude and satellite.mBandType == aBand :
					tunerEx = tunerEx + E_CONFIGURED_TUNER_2

		return tunerEx


	def GetTunerIndexByChannel( self, aNumber ) :
		return self.mTPListByChannelHash.get( aNumber, -1 )


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
		self.SetChannelReloadStatus( True )
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
			self.SetChannelReloadStatus( True )


		prevChannel = None
		nextChannel = None
		self.mChannelListHash = {}

		if newCount < 1 :
			LOG_TRACE('count=%d'% newCount)
			self.SetChannelReloadStatus( True )
			#if not self.Get_Player_AVBlank( ) :
			#	self.Player_AVBlank( True )
			self.Channel_InvalidateCurrent( )
			#self.Frontdisplay_SetMessage('NoChannel')
			LOG_TRACE('-------------------------------------------')

		#if self.mChannelList and tmpChannelList :
		#	LOG_TRACE('oldcount[%d] newcount[%s]'% (len(self.mChannelList), len(tmpChannelList)) )

		self.mChannelList = tmpChannelList
		if self.mChannelList and self.mChannelList[0].mError == 0 :
			count = len( self.mChannelList )
			LOG_TRACE( 'count=%d' %count )

			prevChannel = self.mChannelList[count-1]

			for i in range( count ) :
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

					#cacheChannel.mChannel.printdebug( )
					#LOG_TRACE('prevKey=%d nextKey=%d' %( cacheChannel.mPrevKey, cacheChannel.mNextKey ) )

				except Exception, ex:
					LOG_ERR( "Exception %s" %ex)
				
				prevChannel = channel


				if channel and channel.mError == 0 :
					self.mTPListByChannelHash[channel.mNumber] = self.GetTunerIndexBySatellite( channel.mCarrier.mDVBS.mSatelliteLongitude, channel.mCarrier.mDVBS.mSatelliteBand )



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
				channelDB = ElisChannelDB( )
				self.mZappingMode = channelDB.Zappingmode_GetCurrent( )
				channelDB.Close( )
			else :
				self.mZappingMode = self.mCommander.Zappingmode_GetCurrent( )

		return self.mZappingMode


	def GetModeInfoByZappingMode( self, aChannel = None ) :
		mName = ''
		if aChannel == None :
			aChannel = self.Channel_GetCurrent( )
		zappingMode = self.Zappingmode_GetCurrent( )

		if not zappingMode or zappingMode.mError != 0 :
			return mName

		if zappingMode.mMode == ElisEnum.E_MODE_FAVORITE :
			mName = zappingMode.mFavoriteGroup.mGroupName

		elif self.mZappingMode.mMode == ElisEnum.E_MODE_SATELLITE :
			mName = zappingMode.mSatelliteInfo.mName

		elif self.mZappingMode.mMode == ElisEnum.E_MODE_CAS :
			mName = zappingMode.mCasInfo.mName

		else :
			if aChannel and aChannel.mError == 0 :
				satellite = self.Satellite_GetByChannelNumber( aChannel.mNumber )
				if satellite :
					mName = GetSelectedLongitudeString( satellite.mLongitude, satellite.mName )

		LOG_TRACE( '--------------mname[%s]'% mName )
		return mName



	def Fta_cas_GetList( self, aServiceType = ElisEnum.E_SERVICE_TYPE_INVALID ) :
		if aServiceType :
			return self.mCommander.Fta_cas_GetList( aServiceType )
		else :
			return self.mListCasList


	def Favorite_GetList( self, aTemporaryReload = 0, aServiceType = ElisEnum.E_SERVICE_TYPE_INVALID ) :
		if aTemporaryReload :
			if SUPPORT_CHANNEL_DATABASE	== True :
				channelDB = ElisChannelDB( )
				favList = channelDB.Favorite_GetList( aServiceType )
				channelDB.Close( )
				return favList
			else :
				return self.mCommander.Favorite_GetList( aServiceType )
		else :
			return self.mListFavorite


	def Channel_GetList( self, aTemporaryReload = 0, aType = 0, aMode = 0, aSort = 0 ) :
		"""
		#Extention Extension TEST
		import elis
		import time

		aTemporaryReload = 1
		
		commander = elis.Commander( '127.0.0.1', 12345 )
		req = []
		req.append( 'SetElisReady' )
		req.append( '127.0.0.1' )
		commander.Command( req )

		req = []
		req.append( 'Channel_GetList' )
		req.append('0')
		req.append('0')
		req.append('0')


		start = time.time( )
		commander.Command( req )
		end = time.time( )
		print ' #1 getchannel time =%s' %( end  - start )
		"""
		
		if aTemporaryReload :
			if SUPPORT_CHANNEL_DATABASE	== True :
				channelDB = ElisChannelDB( )
				chList = channelDB.Channel_GetList( aType, aMode, aSort, -1, -1, -1, '', self.mSkip, self.mChannelListDBTable )
				channelDB.Close( )
				return chList
			else :
				return self.mCommander.Channel_GetList( aType, aMode, aSort )

		else :
			return self.mChannelList



	def Channel_GetCount( self, aType = ElisEnum.E_SERVICE_TYPE_TV ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			channelDB = ElisChannelDB( )
			chCount = channelDB.Channel_GetCount( aType, self.mChannelListDBTable )
			channelDB.Close( )
			return chCount

		else :
			chCount = 0
			try :
				chCount = len( self.mChannelList )

			except Exception, e:
				LOG_TRACE( 'Error except[%s]'% e )
				chCount = 0

			return chCount


	#ToDO : Call this function when channels are added or deleted. ( aServiceType = CurrentServieType, aUseCache=False )
	def Channel_GetAllChannels( self, aServiceType, aUseCache = True ) :
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

			channelDB = ElisChannelDB( )
			self.mAllChannelList = channelDB.Channel_GetList( aServiceType, ElisEnum.E_MODE_ALL, ElisEnum.E_SORT_BY_NUMBER )
			channelDB.Close( )
			return self.mAllChannelList

		else :
			return self.mCommander.Channel_GetList( aServiceType, ElisEnum.E_MODE_ALL, ElisEnum.E_SORT_BY_NUMBER )

		LOG_TRACE( 'Reload AllChannels')
		return None


	def Channel_GetCurrent( self, aTemporaryReload = 0 ) :
		if aTemporaryReload :
			return self.mCommander.Channel_GetCurrent( )

		return self.mCurrentChannel


	def Channel_GetOldChannel( self ) :
		return self.mOldChannel


	def Channel_GetCurrentByPlaying( self ) :
		return self.mPlayingChannel


	def Channel_SetCurrent( self, aChannelNumber, aServiceType, aTemporaryHash = None, aFrontMessage = False ) :
		#self.mPMTEvent = None #reset cached PMT Event
		if self.mPMTEvent and self.mPMTEvent.mChannelNumber != aChannelNumber or \
		   self.mPMTEvent and self.mPMTEvent.mServiceType != aServiceType :
			self.mPMTEvent = None

		ret = False
		self.mCurrentEvent = None
		self.mOldChannel = self.Channel_GetCurrent( )
		if self.mCommander.Channel_SetCurrent( aChannelNumber, aServiceType ) == True :
			if aTemporaryHash :
				iChannel = aTemporaryHash.get( aChannelNumber, None ) 
				if iChannel :
					self.mCurrentChannel = iChannel
					ret = True

			else :
				cacheChannel = self.mChannelListHash.get( aChannelNumber, None )
				if cacheChannel :
					self.mCurrentChannel = cacheChannel.mChannel
					ret = True

		channel = self.Channel_GetCurrent( not ret )
		self.Frontdisplay_SetIcon( ElisEnum.E_ICON_HD, channel.mIsHD )
		self.mPlayingChannel = None

		LOG_TRACE( 'LAEL98 TEST FRONTDISPLAY ' )
		if aFrontMessage == True :		
			LOG_TRACE( 'LAEL98 TEST FRONTDISPLAY ' )		
			self.Frontdisplay_SetMessage( channel.mName )
		return ret


	def Channel_SetCurrentSync( self, aChannelNumber, aServiceType, aFrontMessage = False ) :
		#self.mPMTEvent = None #reset cached PMT Event
		if self.mPMTEvent and self.mPMTEvent.mChannelNumber != aChannelNumber or \
		   self.mPMTEvent and self.mPMTEvent.mServiceType != aServiceType :
			self.mPMTEvent = None

		ret = False
		self.mCurrentEvent = None
		self.mOldChannel = self.Channel_GetCurrent( )
		if self.mCommander.Channel_SetCurrentAsync( aChannelNumber, aServiceType, 0 ) == True :
			cacheChannel = self.mChannelListHash.get( aChannelNumber, None )
			if cacheChannel :		
				self.mCurrentChannel = cacheChannel.mChannel
				ret = True

		channel = self.Channel_GetCurrent( )
		self.Frontdisplay_SetIcon( ElisEnum.E_ICON_HD, channel.mIsHD )
		LOG_TRACE( 'LAEL98 TEST FRONTDISPLAY ' )		
		if aFrontMessage == True :
			LOG_TRACE( 'LAEL98 TEST FRONTDISPLAY ' )		
			self.Frontdisplay_SetMessage( channel.mName )
		return ret


	def Channel_GetPrev( self, aChannel ) :
		if aChannel	== None or aChannel.mError != 0 :
			return None

		cacheChannel = self.mChannelListHash.get( aChannel.mNumber, None )
		if cacheChannel == None :
			# retry find first channel
			if self.mChannelList and len( self.mChannelList ) > 0 :
				last = len( self.mChannelList ) - 1
				return self.Channel_GetNext( self.mChannelList[last] )

			return None

		prevKey = cacheChannel.mPrevKey
		channel = self.mChannelListHash.get( prevKey, None )
		if channel == None :
			return None
		#LOG_TRACE('------------ Prev Channel-------------------')
		#channel.printdebug( )
		return channel.mChannel


	def Channel_GetNext( self, aChannel ) :
		if aChannel	== None or aChannel.mError != 0 :
			return None

		cacheChannel = self.mChannelListHash.get(aChannel.mNumber, None)
		if cacheChannel == None :
			# retry find end channel
			if self.mChannelList and len( self.mChannelList ) > 0 :
				cacheChannel = self.mChannelListHash.get( self.mChannelList[0].mNumber, None )
				if cacheChannel == None :
					return None
				prevKey = cacheChannel.mPrevKey
				channel = self.mChannelListHash.get( prevKey, None )
				if channel == None :
					return None
				return channel.mChannel

			return None

		nextKey = cacheChannel.mNextKey
		channel = self.mChannelListHash.get( nextKey, None )
		if channel == None :
			return None
		#LOG_TRACE('------------ Next Channel-------------------')
		#channel.printdebug( )
		return channel.mChannel


	@DataLock
	def Channel_GetCurr( self, aJumpNumber ) :
		if aJumpNumber == None :
			return None

		cacheChannel = self.mChannelListHash.get( aJumpNumber, None )
		if cacheChannel == None :
			return None

		channel =  cacheChannel.mChannel
		#LOG_TRACE('------------ get Channel-------------------[%s %s]'% ( channel.mNumber, channel.mName ) )
		#channel.printdebug( )
		return channel


	@DataLock
	def Channel_GetByNumber( self, aNumber ) :

		cacheChannel = self.mChannelListHash.get( aNumber, None )
		if cacheChannel == None :
			return None

		channel = cacheChannel.mChannel
		return channel


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
				channelDB = ElisChannelDB( )
				satelliteList = channelDB.Satellite_GetByChannelNumber( aNumber, aRequestType, self.mChannelListDBTable )
				channelDB.Close( )
				return satelliteList
				
			else :
				return self.mCommander.Satellite_GetByChannelNumber( aNumber, aRequestType )

		return None


	def Epgevent_GetListByChannel( self, aSid, aTsid, aOnid, aGmtFrom, aGmtUntil, aMaxCount ) :
		return self.mCommander.Epgevent_GetList( aSid, aTsid, aOnid, aGmtFrom, aGmtUntil, aMaxCount )


	def Epgevent_GetCurrent( self, aSid, aTsid, aOnid ) :
		eventList = self.mCommander.Epgevent_GetList( aSid, aTsid, aOnid, 0, 0, 1 )
		if eventList :
			eventList = eventList[0]

		return eventList


	def Epgevent_GetCurrentByChannelFromEpgCF( self, aSid, aTsid, aOnid ) :
		eventList = None
		if SUPPORT_EPG_DATABASE	== True :
			ret = self.mCommander.Epgevent_GetChannelDB( aSid, aTsid, aOnid )
			if ret :
				self.mEpgDB = ElisEPGDB( E_EPG_DB_CF )
				eventList = self.mEpgDB.Epgevent_GetCurrentByChannelFromEpgCF( E_EPG_DB_CF_GET_BY_CHANNEL )
				self.mEpgDB.Close( )

		return eventList


	def Epgevent_GetListByChannelFromEpgCF( self, aSid, aTsid, aOnid ) :
		eventList = None
		if SUPPORT_EPG_DATABASE	== True :
			ret = self.mCommander.Epgevent_GetChannelDB( aSid, aTsid, aOnid )
			if ret :
				self.mEpgDB = ElisEPGDB( E_EPG_DB_CF )
				eventList = self.mEpgDB.Epgevent_GetListFromEpgCF( E_EPG_DB_CF_GET_BY_CHANNEL )
				self.mEpgDB.Close( )

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
				self.mEpgDB.Close( )

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
				self.mEpgDB.Close( )

		return eventList


	def Epgevent_GetPresent( self ) :
		iEPG = None
		iconHd = True
		iEPG = self.mCommander.Epgevent_GetPresent( )
		if iEPG == None or iEPG.mError != 0 :
			iEPG = None

		self.mEPGData = iEPG
		return iEPG


	def GetEpgeventCurrent( self ) :
		return self.mEPGData


	def Channel_GetListBySatellite( self, aType, aMode, aSort, aLongitude, aBand ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			channelDB = ElisChannelDB( )
			channelList = channelDB.Channel_GetList( aType, aMode, aSort, aLongitude, aBand, -1, '', self.mSkip, self.mChannelListDBTable )
			channelDB.Close( )
			return channelList
		else :
			return self.mCommander.Channel_GetListBySatellite( aType, aMode, aSort, aLongitude, aBand )


	def Channel_GetListByFTACas( self, aType, aMode, aSort, aCAid ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			channelDB = ElisChannelDB( )
			channelList = channelDB.Channel_GetList( aType, aMode, aSort, None, None, aCAid, '', self.mSkip, self.mChannelListDBTable )
			channelDB.Close( )
			return channelList
		else :
			return self.mCommander.Channel_GetListByFTACas( aType, aMode, aSort, aCAid )


	def Channel_GetListByFavorite( self, aType, aMode, aSort, aFavName ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			tunerTP = None
			if self.mChannelListDBTable == E_TABLE_ZAPPING :
				loopthrough = ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander ).GetProp( )
				recCount = self.Record_GetRunningRecorderCount( )
				if tunerTP == 1 and loopthrough :
					tunerTP = 1
				else :
					tunerTP = 2
			channelDB = ElisChannelDB( )
			channelList = channelDB.Channel_GetList( aType, aMode, aSort, tunerTP, None, None, aFavName, self.mSkip, self.mChannelListDBTable )
			channelDB.Close( )
			return channelList
		else :
			return self.mCommander.Channel_GetListByFavorite( aType, aMode, aSort, aFavName )


	def Channel_GetByOne( self, aSid ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			channelDB = ElisChannelDB( )
			iChannel = channelDB.Channel_GetByOne( aSid )
			channelDB.Close( )
			return iChannel


	def Channel_Lock( self, aLock, aIChannel ) :
		return self.mCommander.Channel_Lock( aLock, aIChannel )


	def Channel_LockByNumber( self, aLock, aType, aNumList ) :
		return self.mCommander.Channel_LockByNumber( aLock, aType, aNumList )


	def Channel_Skip( self, aSet, aIChannel ) :
		return self.mCommander.Channel_Skip( aSet, aIChannel )


	def Channel_SkipByNumber( self, aSet, aType, aNumList ) :
		return self.mCommander.Channel_SkipByNumber( aSet, aType, aNumList )


	def Channel_GetViewingTuner( self ) :
		return self.mCommander.Channel_GetViewingTuner( )
	

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


	def Channel_Delete( self, aUseDB, aIChannel ) :
		return self.mCommander.Channel_Delete( aUseDB, aIChannel )


	def Channel_DeleteByNumber( self, aType, aUseDB, aNumList ) :
		#ToDo delete timer ID
		return self.mCommander.Channel_DeleteByNumber( aType, aUseDB, aNumList )


	def Channel_DeleteAll( self ) :
		#delete timer
		mTimerList = []
		mTimerList = self.Timer_GetTimerList( )

		if mTimerList :
			for timer in mTimerList:
				self.Timer_DeleteTimer( timer.mTimerId )

		return self.mCommander.Channel_DeleteAll( )


	def Channel_DeleteBySatellite( self, aLongitude, aBand ) :
		aTypeAll = []
		aTypeAll.append( ElisEnum.E_SERVICE_TYPE_TV )
		aTypeAll.append( ElisEnum.E_SERVICE_TYPE_RADIO )
		mMode = ElisEnum.E_MODE_SATELLITE
		mSort = ElisEnum.E_SORT_BY_NUMBER

		ret = 0
		try :
			self.SetSkipChannelView( True )
			for mType in aTypeAll :
				tmpChannelList = self.Channel_GetListBySatellite( mType, mMode, mSort, aLongitude, aBand )

				if tmpChannelList == None or len( tmpChannelList ) < 1 :
					LOG_TRACE( 'type[%s] channel None'% mType )
					continue

				numList = []
				for idx in range( len ( tmpChannelList ) ) :
					chNum = ElisEInteger( )
					chNum.mParam = tmpChannelList[idx].mNumber
					numList.append( chNum )

				ret |= self.mCommander.Channel_DeleteByNumber( mType, 0, numList )
				#from pvr.GuiHelper import ClassToList
				#LOG_TRACE('delete type[%s] len[%s] channel[%s]'% ( mType, len(tmpChannelList), ClassToList('convert', numList) ) )

			self.SetSkipChannelView( False )
			if ret :
				self.mCommander.Channel_Save( )
				self.SetChannelReloadStatus( True )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )
			self.SetSkipChannelView( False )

		return ret


	def Satellite_GetListByChannel( self ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			channelDB = ElisChannelDB( )
			satelliteList = channelDB.Satellite_GetListByChannel( )
			channelDB.Close( )
			return satelliteList


	def Channel_SetInitialBlank( self, aBlank ) :
		return self.mCommander.Channel_SetInitialBlank( aBlank )


	def Channel_GetZappingList( self, aSync = 0 ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			recCount = self.Record_GetRunningRecorderCount( )
			LOG_TRACE( '%d : %d' %( self.mRecordingCount, recCount ) )
			if self.mRecordingCount != recCount :
				self.mRecordingCount = recCount
			else :
				LOG_TRACE( 'skip getzapping list' )
				return
 
			self.Frontdisplay_SetIcon( ElisEnum.E_ICON_REC, recCount )
			return self.mCommander.Channel_GetZappingList( aSync )


	def GetChannelReloadStatus( self ) :
		return self.mCacheReload


	def SetChannelReloadStatus( self, aReload = False ) :
		self.mCacheReload = aReload


	def Channel_ReLoad( self ) :
		mCurrentChannel = self.Channel_GetCurrent( )

		self.LoadZappingmode( )
		self.LoadZappingList( )
		self.LoadChannelList( )
		self.Channel_GetAllChannels( self.mZappingMode.mServiceType, False )
		self.SetChannelReloadStatus( True )

		#self.Channel_TuneDefault( mCurrentChannel )
		self.Channel_TuneDefault( False, mCurrentChannel )


	def Channel_TuneDefault( self, aDefault = True, aCurrentChannel = None ) :
		if aDefault :
			aCurrentChannel = self.Channel_GetCurrent( )

		isCurrentChannelDelete = True
		if aCurrentChannel and aCurrentChannel.mError == 0 :
			iChannelList = self.Channel_GetList( )
			if self.Channel_GetCount( ) and iChannelList and len( iChannelList ) > 0 :
				for iChannel in iChannelList :
					if aCurrentChannel.mSid == iChannel.mSid and \
					   aCurrentChannel.mTsid == iChannel.mTsid and \
					   aCurrentChannel.mOnid == iChannel.mOnid :
						isCurrentChannelDelete = False
						aCurrentChannel = iChannel
						break

		#LOG_TRACE( '-----found ch[%s]'% isCurrentChannelDelete )
		if not isCurrentChannelDelete :
			if aCurrentChannel and aCurrentChannel.mError == 0 :
				self.Channel_SetCurrent( aCurrentChannel.mNumber, aCurrentChannel.mServiceType )
				#LOG_TRACE( '-------------1 tune[%s %s]'% ( aCurrentChannel.mNumber, aCurrentChannel.mName ) )
				return

			else :
				isCurrentChannelDelete = True

		if aCurrentChannel == None or isCurrentChannelDelete :
			channelList = self.Channel_GetList( )
			if channelList and len( channelList ) > 0 :
				self.Channel_SetCurrent( channelList[0].mNumber, channelList[0].mServiceType )
				#LOG_TRACE( '-------------2 tune[%s %s]'% ( channelList[0].mNumber, channelList[0].mName ) )


	def Channel_ReTune( self ) :
		channel = self.Channel_GetCurrent( )
		if channel == None or channel.mError != 0 :
			LOG_ERR( 'Load Channel_GetCurrent None' )
		else :
			self.Channel_InvalidateCurrent( )
			self.Channel_SetCurrent( channel.mNumber, channel.mServiceType )


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


	def Player_VideoBlank( self, aBlank, aForce = False ) :
		return self.mCommander.Player_VideoBlank( aBlank, aForce )


	def Player_AVBlank( self, aBlank, aForce = False ) :
		self.mAVBlankStatus = aBlank
		return self.mCommander.Player_AVBlank( aBlank, aForce )


	def Channel_GetInitialBlank( self ) :
		self.mAVBlankStatus = self.mCommander.Channel_GetInitialBlank( )
		return self.mAVBlankStatus


	def Get_Player_AVBlank( self ) :
		return self.mAVBlankStatus


	def SetAVBlankByArchive( self, aBlank ) :
		if aBlank :
			if self.Get_Player_AVBlank( ) :
				self.mRecoverBlank = True
				self.Player_AVBlank( False )
		else :
			if self.mRecoverBlank :
				self.mRecoverBlank = False
				if not self.Get_Player_AVBlank( ) :
					self.Player_AVBlank( True )
					LOG_TRACE('---------------------last blank')


	def SetAVBlankByChannel( self, aChannel = None ) :
		iChannel = None
		if not aChannel :
			iChannel = self.Channel_GetCurrent( )
		else :
			iChannel = aChannel

		if iChannel and iChannel.mLocked :
			if not self.Get_Player_AVBlank( ) :
				self.Player_AVBlank( True )

		else :
			if self.Get_Player_AVBlank( ) :
				self.Player_AVBlank( False )


	def Player_SetMute( self, aMute ) :
		return self.mCommander.Player_SetMute( aMute )


	def Player_GetStatus( self ) :
		return self.mCommander.Player_GetStatus( )


	def Player_Resume( self ) :
		ret = self.mCommander.Player_Resume( )
		self.Frontdisplay_PlayPause( )
		return ret


	def Player_Pause( self ) :
		ret = self.mCommander.Player_Pause( )
		self.Frontdisplay_PlayPause( )
		return ret


	def Player_Stop( self ) :
		self.mPlayingChannel = self.Channel_GetCurrent( )
		self.SetAVBlankByArchive( False )
		ret = self.mCommander.Player_Stop( )
		self.Frontdisplay_PlayPause( False )
		"""
		channel = self.Channel_GetCurrent( )
		if channel and channel.mError == 0 :
			self.Frontdisplay_SetMessage( channel.mName )
		"""
		
		return ret


	def Player_SetSpeed( self, aSpeed ) :
		ret = self.mCommander.Player_SetSpeed( aSpeed )
		self.Frontdisplay_PlayPause( )
		return ret


	def Player_JumpToIFrame( self, aMiliSec ) :
		return self.mCommander.Player_JumpToIFrame( aMiliSec )


	def Player_StartTimeshiftPlayback( self, aPlayBackMode, aData ) :
		ret = self.mCommander.Player_StartTimeshiftPlayback( aPlayBackMode, aData )
		self.Frontdisplay_PlayPause( )
		return ret


	def Player_StartInternalRecordPlayback( self, aRecordKey, aServiceType, aOffsetMS, aSpeed ) :
		ret = self.mCommander.Player_StartInternalRecordPlayback( aRecordKey, aServiceType, aOffsetMS, aSpeed )
		self.SetAVBlankByArchive( True )
		self.Frontdisplay_PlayPause( )
		"""
		recInfo = self.Record_GetRecordInfoByKey( aRecordKey )
		if recInfo and recInfo.mError == 0 :
			self.Frontdisplay_SetMessage( recInfo.mChannelName )
		"""

		return ret


	def Player_CreateBookmark( self ) :
		return self.mCommander.Player_CreateBookmark( )


	def Player_DeleteBookmark( self, aRecordKey, aOffset ) :
		return self.mCommander.Player_DeleteBookmark( aRecordKey, aOffset )


	def Player_GetBookmarkList( self, aRecordKey ) :
		return self.mCommander.Player_GetBookmarkList( aRecordKey )


	def RecordItem_GetEventInfo( self, aKey ) :
		return self.mCommander.RecordItem_GetEventInfo( aKey )


	def RecordItem_GetCurrentPosByKey( self, aRecordKey ) :
		return self.mCommander.RecordItem_GetCurrentPosByKey( aRecordKey )


	def RecordItem_GetCurrentPosByIndex( self, aRecordIndex ) :
		return self.mCommander.RecordItem_GetCurrentPosByIndex( aRecordIndex )
		

	def Record_GetRunningRecorderCount( self ) :
		return self.mCommander.Record_GetRunningRecorderCount( )


	def Record_GetRunningRecordInfo( self, aIndex ) :
		return self.mCommander.Record_GetRunningRecordInfo( aIndex )


	def Record_GetCount( self, aServiceType ) :
		if SUPPORT_RECORD_DATABASE == True :
			recordDB = ElisRecordDB( )
			recordCount = recordDB.Record_GetCount( aServiceType )
			recordDB.Close( )
			return recordCount

		else :
			return self.mCommander.Record_GetCount( aServiceType )


	def Record_GetList( self, aServiceType, aHideWatched = False ) :
		if SUPPORT_RECORD_DATABASE == True :	
			recordDB = ElisRecordDB( )
			recordList = recordDB.Record_GetList( aServiceType, aHideWatched )
			recordDB.Close( )
			return recordList

		else :
			recordList = []
			count = self.Record_GetCount( aServiceType )
			for i in range( count ) :
				recInfo = self.Record_GetRecordInfo( i, aServiceType )
				recordList.append( recInfo )
			return recordList


	def Record_GetRecordInfo( self, aIndex, aServiceType ) :
		if SUPPORT_RECORD_DATABASE == True :	
			recordDB = ElisRecordDB( )
			recInfo = recordDB.Record_GetRecordInfo( aIndex, aServiceType )
			recordDB.Close( )
			return recInfo

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
			timerDB = ElisTimerDB( )
			timerCount = timerDB.Timer_GetTimerCount( )
			timerDB.Close( )
			return timerCount

		else :
			return self.mCommander.Timer_GetTimerCount( )


	def Timer_EditRunningTimer( self, aTimerId, aNewEndTime) :
		return self.mCommander.Timer_EditRunningTimer( aTimerId, aNewEndTime )
	

	def Timer_GetById( self, aTimderId ) :
		if SUPPORT_TIMER_DATABASE == True :
			timerDB = ElisTimerDB( )
			timerId = timerDB.Timer_GetById( aTimderId )
			timerDB.Close( )
			return timerId

		else :
			return self.mCommander.Timer_GetById( aTimderId )


	def Timer_GetByIndex( self, aIndex ) :
		if SUPPORT_TIMER_DATABASE == True :
			timerDB = ElisTimerDB( )
			timerIdx = timerDB.Timer_GetByIndex( aIndex )
			timerDB.Close( )
			return timerIdx

		else :
			return self.mCommander.Timer_GetByIndex( aIndex )


	def Timer_GetOTRInfo( self ) :
		return self.mCommander.Timer_GetOTRInfo( )


	def Timer_AddOTRTimer( self, aFromEPG, aFixedDuration, aCopyTimeshift, aTimerName, aForceDecrypt, aEventId, aSid, aTsid, aOnid ) : 
		return self.mCommander.Timer_AddOTRTimer( aFromEPG, aFixedDuration, aCopyTimeshift, aTimerName, aForceDecrypt, aEventId, aSid, aTsid, aOnid )


	def Timer_AddEPGTimer( self, aForceDecrypt, aForceThisEvent, aEPG  ) : 
		#ToDO : Change as AddEPGTimer
		epgList = []
		epgList.append( aEPG )
		return self.mCommander.Timer_AddEPGTimer( aForceDecrypt, aForceThisEvent, epgList )


	def Timer_AddManualTimer( self, aChannelNo, aServiceType, aStartTime, aDuration, aTimerName, aForceDecrypt ) :
		return self.mCommander.Timer_AddManualTimer( aChannelNo, aServiceType, aStartTime, aDuration, aTimerName, aForceDecrypt )


	def Timer_AddWeeklyTimer( self, aChannelNo, aServiceType, aStartTime, aExpiryTime, aTimerName, aForceDecrypt, aWeeklyTimerCount, aWeeklyTimer ) :
		return self.mCommander.Timer_AddWeeklyTimer( aChannelNo, aServiceType, aStartTime, aExpiryTime, aTimerName, aForceDecrypt, aWeeklyTimerCount, aWeeklyTimer )


	def Timer_AddSeriesTimer( self, aEPGEvent ) :
		return self.mCommander.Timer_AddSeriesTimer( aEPGEvent )


	def Timer_AddKeywordTimer( self, aChannelNo, aServiceType, aKeyword, aTitleOnly, aForceDecrypt ) :
		return self.mCommander.Timer_AddKeywordTimer( aChannelNo, aServiceType, aKeyword, aTitleOnly, aForceDecrypt )


	def Timer_DeleteTimer( self, aTimerId ) :
		return self.mCommander.Timer_DeleteTimer( aTimerId )


	def Timer_GetRunningTimers( self ) :
		return self.mCommander.Timer_GetRunningTimers( )


	def Timer_EditOneWeeklyTimer( self, aTimerId, aDate, aStartTime, aDuration, aNewStartTime, aNewDuration ) :
		return self.mCommander.Timer_EditWeeklyTimer( aTimerId, aDate, aStartTime, aDuration, aNewStartTime, aNewDuration )


	def Timer_AddOneWeeklyTimer( self, aTimerId, aDate, aStartTime, aDuration ) :	
		return self.mCommander.Timer_AddWeeklyTimerItem( aTimerId, aDate, aStartTime, aDuration )

		
	def Timer_DeleteOneWeeklyTimer( self, aTimerId, aDate, aStartTime, aDuration ) :
		return self.mCommander.Timer_EditWeeklyTimer( aTimerId, aDate, aStartTime, aDuration, aStartTime, 0 ) 


	def Teletext_Show( self ) :
		return self.mCommander.Teletext_Show( )


	def Teletext_NotifyHide( self ) :
		return self.mCommander.Teletext_NotifyHide( )


	def Teletext_IsShowing( self ) :
		return self.mCommander.Teletext_IsShowing( )


	def Frontdisplay_SetMessage( self, aName ) :
		self.mCommander.Frontdisplay_SetMessage( aName )


	def Frontdisplay_SetCurrentMessage( self ) :
		LOG_TRACE( 'LAEL98 TEST FRONTDISPLAY ' )
		if self.mChannelList and len( self.mChannelList ) > 0 :
			if self.mCurrentChannel :
				self.Frontdisplay_SetMessage( self.mCurrentChannel.mName )
			else :
				self.Frontdisplay_SetMessage('NoChannel')
		else :
			self.Frontdisplay_SetMessage('NoChannel')		


	def Frontdisplay_SetIcon( self, aIconIndex, aOnOff ) :
		self.mCommander.Frontdisplay_SetIcon( aIconIndex, aOnOff )


	def Frontdisplay_Resolution( self, aResolution = None ) :
		self.Frontdisplay_SetIcon( ElisEnum.E_ICON_1080i, False )
		self.Frontdisplay_SetIcon( ElisEnum.E_ICON_1080p, False )
		self.Frontdisplay_SetIcon( ElisEnum.E_ICON_720p, False )

		mIsHD = False
		if aResolution == ElisEnum.E_ICON_1080i or aResolution == ElisEnum.E_ICON_720p :
			mIsHD = True
			self.Frontdisplay_SetIcon( aResolution, True )

		#LOG_TRACE('---------Front aResolution[%s] mIsHD[%s]'% ( aResolution, mIsHD ) )
		self.Frontdisplay_SetIcon( ElisEnum.E_ICON_HD, mIsHD )


	def Frontdisplay_ResolutionByIdentified( self, aEvent = None ) :
		hdmiFormat = ElisPropertyEnum( 'HDMI Format', self.mCommander ).GetPropString( )
		iconIndex = ElisEnum.E_ICON_1080i
		if not aEvent :
			if hdmiFormat == '576p' :
				iconIndex = -1
			elif hdmiFormat == '720p' :
				iconIndex = ElisEnum.E_ICON_720p

			self.Frontdisplay_Resolution( iconIndex )
		else :
			if hdmiFormat == 'Automatic' :
				if aEvent.mVideoHeight <= 576 :
					iconIndex = -1
				elif aEvent.mVideoHeight <= 720 :
					iconIndex = ElisEnum.E_ICON_720p

				self.Frontdisplay_Resolution( iconIndex )


	def Frontdisplay_PlayPause( self, aIcon = True ) :
		play = 1	#on
		pause= 0	#off
		if aIcon :
			status = self.Player_GetStatus( )
			if status.mSpeed == 0 :
				play = 0
				pause= 1
		else :
			play = 0
			pause= 0

		self.Frontdisplay_SetIcon( ElisEnum.E_ICON_PLAY, play )
		self.Frontdisplay_SetIcon( ElisEnum.E_ICON_PAUSE, pause )


	def GetRunnigTimerByChannel( self, aChannel = None ) :
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


	def USB_GetMountPath( self ) :
		usbPath = ''
		retList = self.mCommander.USB_GetMountPath( )
		if retList and len( retList ) > 0 and retList[0].mError == 0 :
			usbPath = retList[0].mParam

		return usbPath


	def System_Reboot( self ) :
		return self.mCommander.System_Reboot( )


	def ToggleTVRadio( self ) :
		ret = True
		restoreZappingMode = None
		try :
			zappingMode = self.Zappingmode_GetCurrent( )
			restoreZappingMode = copy.deepcopy( zappingMode )
			#zappingMode.printdebug( )

			modeStr = ''
			newZappingMode = copy.deepcopy( self.mLastZappingMode )
			if zappingMode.mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
				modeStr = 'TV'
				newZappingMode.mServiceType = ElisEnum.E_SERVICE_TYPE_RADIO
			else :
				modeStr = 'Radio'
				newZappingMode.mServiceType = ElisEnum.E_SERVICE_TYPE_TV

			checkCount = self.Channel_GetCount( newZappingMode.mServiceType )
			#LOG_TRACE( '-------------check type[%s] count[%s]'% ( newZappingMode.mServiceType, checkCount ) )
			if checkCount < 1 :
				LOG_TRACE('Cannot change. currType[%s] failType[%s] 1:TV, 2:Radio, channel is None'% ( zappingMode.mServiceType, newZappingMode.mServiceType ) )
				return False

			#LOG_TRACE('------changed settings')
			#newZappingMode.printdebug( )
			isSetMod = self.Zappingmode_SetCurrent( newZappingMode )
			self.LoadZappingmode( )
			self.LoadZappingList( )
			self.LoadChannelList( )

			self.mLastZappingMode = copy.deepcopy( zappingMode )
			zappingMode = self.Zappingmode_GetCurrent( )
			self.Channel_InvalidateCurrent( )

			lastChannelProperty = 'Last TV Number'
			if zappingMode.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
				lastChannelProperty = 'Last Radio Number'

			iChannel = None
			#1.default channel, First Channel
			if self.mChannelList and len( self.mChannelList ) > 0 :
				iChannel = self.mChannelList[0]
				#LOG_TRACE( 'default Channel ch[%s %s] type[%s]'% ( iChannel.mNumber, iChannel.mName, iChannel.mServiceType ) )

			#2.find channel, Exist last Channel
			lastChannelNumber = ElisPropertyInt( lastChannelProperty, self.mCommander ).GetProp( )
			cacheChannel = self.mChannelListHash.get( lastChannelNumber, None )
			if cacheChannel :
				iChannel = cacheChannel.mChannel
				#LOG_TRACE( 'find last Channel ch[%s %s] type[%s]'% ( iChannel.mNumber, iChannel.mName, iChannel.mServiceType ) )

			if iChannel :
				self.Channel_SetCurrent( iChannel.mNumber, iChannel.mServiceType )
				#LOG_TRACE( 'tune Channel ch[%s %s] type[%s]'% ( iChannel.mNumber, iChannel.mName, iChannel.mServiceType ) )


		except Exception, e :
			LOG_ERR( 'Exception [%s]'% e )
			ret = False

			#restore
			if restoreZappingMode and restoreZappingMode.mError == 0 :
				LOG_ERR( 'Restore previos zapping mode back' )
				restoreZappingMode.printdebug( )
				self.Zappingmode_SetCurrent( restoreZappingMode )
				self.LoadZappingmode( )
				self.LoadZappingList( )
				self.LoadChannelList( )

		return ret


	def SetCurrentPMTEvent( self, aPMTEvent ) :
		self.mPMTEvent = aPMTEvent


	def GetCurrentPMTEvent( self ) :
		return self.mPMTEvent


	def SetLockedState( self, aIsLock ) :
		self.mLockStatus = aIsLock


	def GetLockedState( self ) :
		return self.mLockStatus


	def SetRunningHiddenTest( self, aFlag ) :
		self.mIsRunningHiddentest = aFlag


	def GetRunningHiddenTest( self ) :
		return self.mIsRunningHiddentest

	
	def SetMediaCenter( self, aValue = False ) :
		if aValue == True :
			self.Frontdisplay_SetMessage( 'Media Center' )
		self.mStartMediaCenter = aValue


	def GetMediaCenter( self ) :
		return self.mStartMediaCenter


	def SetPropertyAge( self, aAge ) :
		self.mPropertyAge = aAge


	def GetPropertyAge( self ) :
		return self.mPropertyAge


	def SetPropertyChannelBannerTime( self, aTime ) :
		self.mPropertyChannelBannerTime = aTime


	def GetPropertyChannelBannerTime( self ) :
		return self.mPropertyChannelBannerTime


	def SetPropertyPlaybackBannerTime( self, aTime ) :
		self.mPropertyPlaybackBannerTime = aTime


	def GetPropertyPlaybackBannerTime( self ) :
		self.mPropertyPlaybackBannerTime = aTime


	def SetParentLockPass( self, aPass = False ) :
		self.mParentLockPass = aPass


	def GetParentLockPass( self ) :
		return self.mParentLockPass


	def SetParentLock( self, aLock = True ) :
		self.mParentLock = aLock


	def GetParentLock( self, aCheckEPG = None ) :
		isLimit = False

		iEPG  = self.mEPGData
		iMode = self.Player_GetStatus( ).mMode
		iLock = self.mParentLock
		if aCheckEPG :
			iEPG  = aCheckEPG
			iMode = ElisEnum.E_MODE_LIVE
			iLock = True

		LOG_TRACE( 'parentlock[%s]'% self.mParentLock )
		if iMode == ElisEnum.E_MODE_LIVE and \
		   iLock and ( iEPG and iEPG.mError == 0 ) :
			isLimit = AgeLimit( self.mPropertyAge, iEPG.mAgeRating )
			LOG_TRACE( 'isLimit[%s]'% isLimit )

		return isLimit


	def SetPincodeDialog( self, aOnShow = False ) :
		self.mIsPincodeDialog = aOnShow


	def GetPincodeDialog( self ) :
		return self.mIsPincodeDialog


	def SetDefaultHideWatched( self, aHideWatched = False ) :
		self.mDefaultHideWatched = aHideWatched


	def GetDefaultHideWatched( self ) :
		return self.mDefaultHideWatched


	def SetDefaultByFactoryReset( self ) :
		LOG_TRACE('-------factory reset')
		#1. pincode : m/w (super pin)
		#2. video : 1080i, normal, RGB
		LOG_TRACE( '>>>>>>>> Default init : Video <<<<<<<<' )
		ElisPropertyEnum( 'HDMI Format', self.mCommander ).SetPropString( '1080i' )
		ElisPropertyEnum( 'Show 4:3', self.mCommander ).SetPropString( 'Normal (Pillarbox)' )
		ElisPropertyEnum( 'HDMI Color Space', self.mCommander ).SetPropString( 'RGB' )
		self.Frontdisplay_Resolution( ElisEnum.E_ICON_1080i )

		#3. network : dhcp
		LOG_TRACE( '>>>>>>>> Default init : Network <<<<<<<<' )
		import pvr.NetworkMgr as NetMgr
		NetMgr.GetInstance( ).ResetNetwork( )
		
		#4. time setting : m/w (Time and Date, Local time offset, Summer Time)

		#5. epg, archive
		self.SetDefaultHideWatched( True )
		ret = SetDefaultSettingInXML( )
		LOG_TRACE( '>>>>>>>> Default init : epg,archive ret[%s] <<<<<<<<'% ret )

		#6. volume : 75db
		LOG_TRACE( '>>>>>>>> Default init : Volume <<<<<<<<' )
		if self.mCommander.Player_GetMute( ) :
			self.mCommander.Player_SetMute( False )
			if XBMC_GetMute( ) == True :
				xbmc.executebuiltin( 'mute( )' )

		self.mCommander.Player_SetVolume( DEFAULT_VOLUME )
		#XBMC_SetVolume( DEFAULT_VOLUME )
		XBMC_SetVolumeByBuiltin( DEFAULT_VOLUME, False )

		#7. ageRating
		LOG_TRACE( '>>>>>>>> Default init : AgeLimit <<<<<<<<' )
		ElisPropertyEnum( 'Age Limit', self.mCommander ).SetPropString( 'No Limit' )
		self.SetPropertyAge( 0 )

		#8. channelList, LivePlate
		LOG_TRACE( '>>>>>>>> Default init : Channel <<<<<<<<' )
		zappingmode = self.Zappingmode_GetCurrent( )
		zappingmode.mMode = ElisEnum.E_MODE_ALL
		zappingmode.mServiceType = ElisEnum.E_SERVICE_TYPE_TV
		zappingmode.mSortingMode = ElisEnum.E_SORT_BY_NUMBER
		self.Zappingmode_SetCurrent( zappingmode )
		#self.Channel_Save( )
		self.Channel_ReLoad( )

		#pvr.gui.WindowMgr.GetInstance( ).GetWindow( pvr.gui.WindowMgr.WIN_ID_LIVE_PLATE ).SetPincodeRequest( True )
		#xbmc.executebuiltin( 'xbmc.Action(contextmenu)' )


