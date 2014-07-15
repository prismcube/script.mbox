import xbmcaddon
from decorator import decorator
from elisinterface.ElisEventClass import *
from elisinterface.ElisProperty import ElisPropertyEnum, ElisPropertyInt
import pvr.ElisMgr
import pvr.Platform
import pvr.BackupSettings
from pvr.XBMCInterface import XBMC_GetVolume, XBMC_SetVolumeByBuiltin, XBMC_GetMute, XBMC_GetCurrentLanguage
from pvr.gui.GuiConfig import *
from pvr.Util import TimeToString, TimeFormatEnum
from pvr.Product import *

if E_USE_OLD_NETWORK :
	import pvr.IpParser as NetMgr
else :
	import pvr.NetworkMgr as NetMgr

from pvr.GuiHelper import AgeLimit, SetDefaultSettingInXML, MR_LANG, AsyncShowStatus, SetSetting, GetXBMCLanguageToPropLanguage, GetXBMCLanguageToPropAudioLanguage, CheckDirectory, ParseStringInPattern, RemoveDirectory

if pvr.Platform.GetPlatform( ).IsPrismCube( ) :
	gFlagUseDB = True
else :
	gFlagUseDB = False


import sys
import os
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

print 'mBox----------------use db[%s] platform[%s]' %( gFlagUseDB, pvr.Platform.GetPlatform( ).GetName( ) )

E_ENUM_OBJECT_REUSE_ZAPPING = 0
E_ENUM_OBJECT_REUSE_ALLCHANNEL = 1
E_ENUM_OBJECT_INSTANCE = 3

SUPPORT_EPG_DATABASE     = gFlagUseDB
SUPPORT_CHANNEL_DATABASE = gFlagUseDB
SUPPORT_TIMER_DATABASE   = gFlagUseDB
SUPPORT_RECORD_DATABASE  = gFlagUseDB

if SUPPORT_EPG_DATABASE == True :
	from elisinterface.ElisEPGDB import ElisEPGDB

if SUPPORT_CHANNEL_DATABASE == True :
	from elisinterface.ElisChannelDB import ElisChannelDB

if SUPPORT_TIMER_DATABASE == True :
	from elisinterface.ElisTimerDB import ElisTimerDB

if SUPPORT_RECORD_DATABASE == True :
	from elisinterface.ElisRecordDB import ElisRecordDB

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


class CacheChannelPIP( object ) :
	def __init__( self, aChannel, aPrevKey, aNextKey ) :
		self.mChannel = aChannel
		self.mPrevKey = aPrevKey
		self.mNextKey = aNextKey


class CacheChannel( object ) :
	def __init__( self, aChannel, aPrevKey, aNextKey ) :
		self.mChannel = aChannel
		self.mPrevKey = aPrevKey
		self.mNextKey = aNextKey


class DataCacheMgr( object ) :
	def __init__( self ) :
		self.mShutdowning = False
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.mChannelLogo = pvr.ChannelLogoMgr.GetInstance( )
		
		self.mZappingMode						= None
		self.mLastZappingMode					= ElisIZappingMode( )
		self.mChannelList						= None
		self.mListItems						= []
		self.mListItemsPool 					= []		
		self.mAllChannelList					= None
		self.mCurrentChannel					= None
		self.mOldChannel						= self.Channel_GetCurrent( True )
		self.mOldChannelList					= []
		self.mBackupOldChannel					= None
		self.mBackupOldChannelList				= []

		self.mLocalOffset						= 0
		self.mLocalTime							= 0
		self.mAllSatelliteList					= None
		self.mConfiguredSatelliteList			= None
		self.mConfiguredSatelliteListTuner1		= None
		self.mConfiguredSatelliteListTuner2		= None
		self.mConfiguredTuner1Hash				= {}
		self.mConfiguredTuner2Hash				= {}
		self.mTransponderLists					= None
		self.mEPGList							= None
		self.mCurrentEvent						= None
		self.mListCasList						= None
		self.mListFavorite						= None
		self.mListProvider						= []
		self.mPropertyAge						= 0
		self.mPropertyPincode					= -1
		self.mCacheReload						= False
		self.mIsEmptySatelliteInfo				= False

		self.mChannelListHash					= {}
		self.mChannelListHashForTimer			= {}
		self.mAllChannelListHash				= {}
		self.mAllSatelliteListHash				= {}
		self.mTransponderListHash				= {}
		self.mEPGListHash						= {}
		self.mEPGList 							= None
		self.mEPGData							= None
		self.mMaxChannelNum 					= E_INPUT_MAX

		self.mChannelListDBTable				= E_TABLE_ALLCHANNEL
		self.mEpgDB 							= None
		self.mChannelDB 						= None
		self.mTimerDB 							= None
		self.mRecordDB 							= None

		self.mPMTinstance						= None
		self.mPMTListHash						= {}
		self.mBookmarkButton                    = []
		self.mBookmarkHash						= {}

		self.mParentLock						= True
		self.mParentLockPass					= False
		self.mParentLockEPG						= None
		self.mIsPincodeDialog					= False
		self.mLockStatus 						= self.mCommander.Channel_GetStatus( )
		self.mAVBlankStatus 					= self.mCommander.Channel_GetInitialBlank( )
		self.mRecoverBlank 						= False
		self.mSkip 								= False
		self.mIsRunningHiddentest 				= False
		self.mStartMediaCenter					= False
		self.mDefaultHideWatched				= False
		self.mPlayingChannel					= False

		self.mStandByClose						= False
		self.mStandByStatus						= ElisEnum.E_STANDBY_POWER_ON
		self.mSearchNewChannel					= False
		self.mUSBAttatched						= False
		self.mChangedByViewTimer				= False
		self.mDelaySettingWindow				= True
		self.mTimerList							= self.Timer_GetTimerList( )
		self.mChannelListPIP					= []
		self.mChannelListHashPIP				= {}
		self.mPresentNumberHashPIP				= {}
		self.mZappingListChange					= False

		self.mRootWindowId						= 0
		self.mRootWindow						= None
		self.mHasLinkageService					= False

		self.mPIPStart							= self.PIP_IsStarted( )
		self.mPIPSwapStatus						= False
		self.mCurrentChannelPIP					= None
		self.mOldHdmiFormatIndex				= ElisEnum.E_ICON_720p

		self.mVideoOutput						= E_VIDEO_HDMI
		self.mSavedResolution					= self.GetResolution( True )
		self.mIsMediaCenterUi					= False
		self.mChannelWindows					= {}

		self.mHbbTVEnable						= False
		self.mHbbtvStatus						= False
		self.mNetVolumeList						= []

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

		self.mAgeGurantee = self.mPropertyAge
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

	def SetRootWindow( self, aRootWindow ) :
		self.mRootWindow	= aRootWindow

	def Load( self ) :

		self.LoadVolumeAndSyncMute( True ) #False : LoadVolume Only
		#self.SyncLanguagePropFromXBMC( XBMC_GetCurrentLanguage( ) )
		#self.Frontdisplay_ResolutionByIdentified( )

		#Zapping Mode
		self.LoadZappingmode( )
		self.LoadZappingList( )
		#self.mLastZappingMode = copy.deepcopy( self.mZappingMode )

		#SatelliteList
		self.LoadAllSatellite( )
		self.LoadConfiguredSatellite( )
		self.LoadAllTransponder( )

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
		self.SetHbbtvStatus( )

		#init record path
		if E_SUPPORT_EXTEND_RECORD_PATH :
			self.InitNetworkVolume( )

	
	def InitNetwork( self ) :
		NetMgr.GetInstance( ).LoadEthernetService( )
		NetMgr.GetInstance( ).LoadSetWifiTechnology( )
		NetMgr.GetInstance( ).LoadWifiService( )
		"""
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
		"""


	def LoadVolumeAndSyncMute( self, isSyncMuteOn ) :
		lastVolume = self.mCommander.Player_GetVolume( )
		lastMute = self.mCommander.Player_GetMute( )
		lastXBMCMute = XBMC_GetMute( )
		LOG_TRACE( 'last volume[%s] mute[%s]'% ( lastVolume, lastMute ) )
		LOG_TRACE( 'xbmc mute[%s]'% ( lastXBMCMute ) )
		if lastMute :
			if isSyncMuteOn :
				if lastXBMCMute :
					LOG_TRACE( 'mute on' )
				else :
					xbmc.executebuiltin( 'Mute( )' )
					LOG_TRACE( 'mute on' )
			else :
				self.mCommander.Player_SetMute( False )
				lastMute = False
				LOG_TRACE( 'mute off' )

		if lastXBMCMute and lastMute == False :
			xbmc.executebuiltin( 'Mute( )' )
			LOG_TRACE( 'mute icon removed' )

		revisionVolume = abs( lastVolume - XBMC_GetVolume( ) )
		if revisionVolume >= VOLUME_STEP :
			#XBMC_SetVolume( lastVolume, lastMute )
			XBMC_SetVolumeByBuiltin( lastVolume, False )


	def LoadVolumeBySetGUI( self ) :
		if self.Get_Player_AVBlank( ) :
			LOG_TRACE( '-------------pass by volumeSync, status [avBlank]' )
			return

		mute = XBMC_GetMute( )
		volume = XBMC_GetVolume( )
		LOG_TRACE( 'GUI mute[%s] volume[%s]'% ( mute, volume ) )
		self.mCommander.Player_SetMute( mute )
		self.mCommander.Player_SetVolume( volume )


	def LoadTime( self ) :
		self.mLocalOffset = self.mCommander.Datetime_GetLocalOffset( )
		self.mLocalTime = self.mCommander.Datetime_GetLocalTime( )


	def LoadTimerList( self ) :
		self.mTimerList = self.Timer_GetTimerList( )


	def GetTimerList( self ) :
		return self.mTimerList


	def LoadAllSatellite( self ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			channelDB = ElisChannelDB( )
			self.mAllSatelliteList = channelDB.Satellite_GetList( ElisEnum.E_SORTING_FAVORITE )
			channelDB.Close( )
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
			channelDB = ElisChannelDB( )
			self.mConfiguredSatelliteList = channelDB.Satellite_GetConfiguredList( ElisEnum.E_SORT_NAME )
			channelDB.Close( )
		else :
			self.mConfiguredSatelliteList = self.mCommander.Satellite_GetConfiguredList( ElisEnum.E_SORT_NAME )

		if self.mConfiguredSatelliteList and self.mConfiguredSatelliteList[0].mError == 0 :
			pass
		else :
			LOG_WARN('Has no Configured Satellite')


		self.mConfiguredTuner1Hash = {}
		self.mConfiguredSatelliteListTuner1 = []
		if SUPPORT_CHANNEL_DATABASE	== True :
			channelDB = ElisChannelDB( )
			self.mConfiguredSatelliteListTuner1 = channelDB.Satelliteconfig_GetList( E_TUNER_1 )
			channelDB.Close( )
		else :
			self.mConfiguredSatelliteListTuner1 = self.mCommander.Satelliteconfig_GetList( E_TUNER_1 )

		if self.mConfiguredSatelliteListTuner1 and self.mConfiguredSatelliteListTuner1[0].mError == 0 :
			for satellite in self.mConfiguredSatelliteListTuner1 :
				satelliteKey = '%d:%d'% ( satellite.mSatelliteLongitude, satellite.mBandType )
				self.mConfiguredTuner1Hash[satelliteKey] = E_CONFIGURED_TUNER_1
		else :
			LOG_WARN('Has no Configured Satellite Tuner 1')


		self.mConfiguredTuner2Hash = {}
		self.mConfiguredSatelliteListTuner2 = []
		if SUPPORT_CHANNEL_DATABASE	== True :
			channelDB = ElisChannelDB( )
			self.mConfiguredSatelliteListTuner2 = channelDB.Satelliteconfig_GetList( E_TUNER_2 )
			channelDB.Close( )
		else :
			self.mConfiguredSatelliteListTuner2 = self.mCommander.Satelliteconfig_GetList( E_TUNER_2 )

		if self.mConfiguredSatelliteListTuner2 and self.mConfiguredSatelliteListTuner2[0].mError == 0 :
			for satellite in self.mConfiguredSatelliteListTuner2 :
				satelliteKey = '%d:%d'% ( satellite.mSatelliteLongitude, satellite.mBandType )
				self.mConfiguredTuner2Hash[satelliteKey] = E_CONFIGURED_TUNER_2
		else :
			LOG_WARN('Has no Configured Satellite Tuner 2')


	def LoadAllTransponder( self ) :
		self.mTransponderLists = []
		self.mTransponderListHash = {}

		if self.GetEmptySatelliteInfo( ) == False :
			for satellite in self.mAllSatelliteList :
				if SUPPORT_CHANNEL_DATABASE	== True :
					channelDB = ElisChannelDB( )
					transponderList = channelDB.Transponder_GetList( satellite.mLongitude, satellite.mBand )
					channelDB.Close( )
				else :
					transponderList = self.mCommander.Transponder_GetList( satellite.mLongitude, satellite.mBand )
				self.mTransponderLists.append( transponderList )
				hashKey = '%d:%d' % ( satellite.mLongitude, satellite.mBand )
				self.mTransponderListHash[hashKey] = transponderList
		else :
			LOG_WARN('Has no All Satellite')


	def LoadGetListEpgByChannel( self ) :
		if SUPPORT_EPG_DATABASE	== True :
			#Live EPG
			gmtFrom  = self.Datetime_GetLocalTime( )
			#gmtFrom  = self.mTimeshift_curTime
			gmtUntil = gmtFrom + E_MAX_EPG_DAYS
			maxCount = 1000
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
				channelDB = ElisChannelDB( )
				return channelDB.Satellite_GetConfiguredList( ElisEnum.E_SORT_NAME )
				channelDB.Close( )
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

				transponderList.append( '%dMHz   %dKS/s   %s' % ( tmptransponderList[i].mFrequency, tmptransponderList[i].mSymbolRate, polarization ) )

		return transponderList


	def GetTransponderListByIndex( self, aLongitude, aBand, aIndex ) :
		transponder = []
		hashKey = '%d:%d' % ( aLongitude, aBand )
		transponder = self.mTransponderListHash.get( hashKey, None )

		if transponder and len( transponder ) > aIndex :
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


	def GetSimpleTPInformation( self, aLongitude, aBand, aIndex ) :
		transponder = self.GetTransponderListByIndex( aLongitude, aBand, aIndex )
		if transponder :
			pol = 'H'
			if transponder.mPolarization :
				pol = 'V'

			return '%s / %s / %s' % ( transponder.mFrequency, transponder.mSymbolRate, pol )

		return 'None'


	def GetTunerIndexBySatellite( self, aLongitude, aBand ) :
		tunerEx = 0
		tunerEx += self.mConfiguredTuner1Hash.get( '%d:%d'% ( aLongitude, aBand ), 0 )
		tunerEx += self.mConfiguredTuner2Hash.get( '%d:%d'% ( aLongitude, aBand ), 0 )

		"""
		if self.mConfiguredSatelliteListTuner1 :
			for satellite in self.mConfiguredSatelliteListTuner1 :
				if satellite.mSatelliteLongitude == aLongitude and satellite.mBandType == aBand :
					tunerEx = tunerEx + E_CONFIGURED_TUNER_1
					break

		if self.mConfiguredSatelliteListTuner2 :
			for satellite in self.mConfiguredSatelliteListTuner2 :
				if satellite.mSatelliteLongitude == aLongitude and satellite.mBandType == aBand :
					tunerEx = tunerEx + E_CONFIGURED_TUNER_2
					break
		"""

		return tunerEx


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
		self.Channel_GetCurrentSync( )


	def RefreshCacheByChannelList( self, aChannelList ) :
		prevChannel = None
		nextChannel = None
		self.mChannelListHash = {}
		self.mChannelListHashForTimer = {}
		self.mChannelList = aChannelList
		self.mMaxChannelNum = E_INPUT_MAX

		if not self.mChannelList or len( self.mChannelList ) < 1 :
			LOG_TRACE( 'ChannelList None' )
			return

		count = len( self.mChannelList )
		LOG_TRACE( '-------2-------------count[%d]'% count )

		prevChannel = self.mChannelList[count-1]
		self.mListItems = []
		poolCount = len( self.mListItemsPool )

		for i in range( count ) :
			channel = self.mChannelList[i]
			if i+1 < count :
				nextChannel = self.mChannelList[i+1]
			else:
				nextChannel = self.mChannelList[0]

			#LOG_TRACE("---------------------- CacheChannel -----------------")
			try :
				cacheChannel = CacheChannel( channel, prevChannel.mNumber, nextChannel.mNumber )
				self.mChannelListHash[channel.mNumber] = cacheChannel
				#cacheChannel.mChannel.printdebug( )
				#LOG_TRACE('prevKey=%d nextKey=%d' %( cacheChannel.mPrevKey, cacheChannel.mNextKey ) )

			except Exception, ex:
				LOG_ERR( "Exception %s" %ex)

			prevChannel = channel

			if channel and channel.mError == 0 :
				channelKey = '%d:%d:%d'% ( channel.mSid, channel.mTsid, channel.mOnid )
				self.mChannelListHashForTimer[channelKey] = channel

				chNumber = channel.mNumber
				if E_V1_2_APPLY_PRESENTATION_NUMBER :
					chNumber = self.CheckPresentationNumber( channel )

				if chNumber > self.mMaxChannelNum :
					self.mMaxChannelNum = chNumber

				#create listitems
				if i >= poolCount :
					listItem = xbmcgui.ListItem( "%04d" %chNumber, channel.mName )
					self.mListItemsPool.append( listItem )
				else :
					listItem = self.mListItemsPool[i]
					listItem.setLabel( "%04d" %chNumber )
					listItem.setLabel2( channel.mName )

				if E_USE_CHANNEL_LOGO == True :
					logo = '%s_%s' %(channel.mCarrier.mDVBS.mSatelliteLongitude, channel.mSid )
					listItem.setProperty( E_XML_PROPERTY_CHANNEL_LOG, self.mChannelLogo.GetLogo( logo, channel.mServiceType ) )

				self.mListItems.append( listItem )				

		"""
		if self.mMaxChannelNum > 9999 :
			self.mRootWindow.setProperty( E_XML_PROPERTY_CHANNEL_ALIGN, E_TAG_TRUE )
		else :
			self.mRootWindow.setProperty( E_XML_PROPERTY_CHANNEL_ALIGN, E_TAG_FALSE )
		"""
		self.SharedChannel_SetUpdated( 0, True )		
		
		if E_V1_2_APPLY_PIP :
			self.PIP_SetTunableList( )


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
				LOG_TRACE( '---------get db skip[%s] tbl[%s] Sync[%s] type[%s] mode[%s] sort[%s]'% ( self.mSkip, self.mChannelListDBTable, aSync, aType, aMode, aSort ) )
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

			elif mMode == ElisEnum.E_MODE_PROVIDER :
				mProvider = self.mZappingMode.mProviderInfo.mProviderName
				LOG_TRACE( '-----------------------------------1' )
				tmpChannelList = self.Channel_GetListByProvider( mType, mMode, mSort, mProvider )
				LOG_TRACE( '-----------------------------------2' )

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

		LOG_TRACE( '-------------------count old[%s] new[%s]'% ( oldCount, newCount ) )


		prevChannel = None
		nextChannel = None
		self.mChannelListHash = {}
		self.mChannelListHashForTimer = {}
		self.mMaxChannelNum = E_INPUT_MAX

		if newCount < 1 :
			LOG_TRACE('---------newCount-------------count[%d]'% newCount)
			self.SetChannelReloadStatus( True )
			#if not self.Get_Player_AVBlank( ) :
			#	self.Player_AVBlank( True )
			self.Channel_InvalidateCurrent( )
			#self.Frontdisplay_SetMessage('NoChannel')
			LOG_TRACE('-------------------------------------------')

		#if self.mChannelList and tmpChannelList :
		#	LOG_TRACE('oldcount[%d] newcount[%s]'% (len(self.mChannelList), len(tmpChannelList)) )

		self.mChannelList = tmpChannelList
		start = time.time()
		if self.mChannelList and self.mChannelList[0].mError == 0 :
			count = len( self.mChannelList )
			LOG_TRACE( '-------1---------------count[%d]'% count )

			prevChannel = self.mChannelList[count-1]

			self.mListItems = []
			poolCount = len( self.mListItemsPool )

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
					channelKey = '%d:%d:%d'% ( channel.mSid, channel.mTsid, channel.mOnid )
					self.mChannelListHashForTimer[channelKey] = channel

					chNumber = channel.mNumber
					if E_V1_2_APPLY_PRESENTATION_NUMBER :
						chNumber = self.CheckPresentationNumber( channel )

					if chNumber > self.mMaxChannelNum :
						self.mMaxChannelNum = chNumber

					#create listitems
					if i >= poolCount :
						listItem = xbmcgui.ListItem( "%04d" %chNumber, channel.mName )
						self.mListItemsPool.append( listItem )
					else :
						listItem = self.mListItemsPool[i]
						listItem.setLabel( "%04d" %chNumber )
						listItem.setLabel2( channel.mName )

					if E_USE_CHANNEL_LOGO == True :
						logo = '%s_%s' %(channel.mCarrier.mDVBS.mSatelliteLongitude, channel.mSid )
						listItem.setProperty( E_XML_PROPERTY_CHANNEL_LOG, self.mChannelLogo.GetLogo( logo, channel.mServiceType ) )

					self.mListItems.append( listItem )				

		self.SharedChannel_SetUpdated( 0, True )
		"""
		if self.mMaxChannelNum > 9999 :
			self.mRootWindow.setProperty( E_XML_PROPERTY_CHANNEL_ALIGN, E_TAG_TRUE )
		else :
			self.mRootWindow.setProperty( E_XML_PROPERTY_CHANNEL_ALIGN, E_TAG_FALSE )
		"""

		#reload tunableList for PIP
		#if aSync == 0 and mType == ElisEnum.E_SERVICE_TYPE_TV :
		if E_V1_2_APPLY_PIP :
			self.PIP_SetTunableList( )


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
			self.mListCasList  = self.mCommander.Fta_cas_GetList( serviceType )
			self.mListFavorite = self.Favorite_GetList( True, serviceType )
			self.mListProvider = self.Provider_GetList( True, serviceType )
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

		elif zappingMode.mMode == ElisEnum.E_MODE_SATELLITE :
			#mName = zappingMode.mSatelliteInfo.mName
			mName = self.GetSatelliteName( zappingMode.mSatelliteInfo.mLongitude, zappingMode.mSatelliteInfo.mBand )

		elif zappingMode.mMode == ElisEnum.E_MODE_CAS :
			mName = zappingMode.mCasInfo.mName

		elif zappingMode.mMode == ElisEnum.E_MODE_PROVIDER :
			mName = zappingMode.mProviderInfo.mProviderName

		else :
			if aChannel and aChannel.mError == 0 :
				satellite = self.Satellite_GetByChannelNumber( aChannel.mNumber )
				if satellite :
					mName = self.GetFormattedSatelliteName( satellite.mLongitude, satellite.mBand )

		#LOG_TRACE( '--------------mname[%s]'% mName )
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


	def Favorite_GetLCN( self, aFavGroup = '' ) :
		if not aFavGroup :
			return None

		useLCN = False
		if SUPPORT_CHANNEL_DATABASE	== True :
			channelDB = ElisChannelDB( )
			isLCN = channelDB.Favorite_GetLCN( aFavGroup )
			channelDB.Close( )

			if isLCN and isLCN[0] == 1 :
				useLCN = True

		return useLCN


	def Provider_GetList( self, aTemporaryReload = 0, aServiceType = ElisEnum.E_SERVICE_TYPE_INVALID ) :
		if aTemporaryReload :
			if SUPPORT_CHANNEL_DATABASE	== True :
				channelDB = ElisChannelDB( )
				proList = channelDB.Provider_GetList( aServiceType )
				channelDB.Close( )
				return proList

		return self.mListProvider


	def Channel_GetList( self, aTemporaryReload = 0, aType = 0, aMode = 0, aSort = 0, aKeyword = '', aInstanceLoad = False ) :
		if aTemporaryReload :
			if SUPPORT_CHANNEL_DATABASE	== True :
				channelDB = ElisChannelDB( )
				if aKeyword or aInstanceLoad :
					channelDB.SetListUse( E_ENUM_OBJECT_INSTANCE )
				chList = channelDB.Channel_GetList( aType, aMode, aSort, -1, -1, -1, '', '', self.mSkip, self.mChannelListDBTable, aKeyword )
				channelDB.SetListUse( E_ENUM_OBJECT_REUSE_ZAPPING )
				channelDB.Close( )
				return chList
			else :
				return self.mCommander.Channel_GetList( aType, aMode, aSort )

		else :
			return self.mChannelList


	def Channel_GetCount( self, aType = ElisEnum.E_SERVICE_TYPE_TV, aDBTableAll = False ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			dbTable = self.mChannelListDBTable
			if aDBTableAll :
				dbTable = E_TABLE_ALLCHANNEL
			channelDB = ElisChannelDB( )
			chCount = channelDB.Channel_GetCount( aType, dbTable )
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

			LOG_TRACE( 'Reload AllChannels' )

			channelDB = ElisChannelDB( )
			channelDB.SetListUse( E_ENUM_OBJECT_REUSE_ALLCHANNEL )
			self.mAllChannelList = channelDB.Channel_GetList( aServiceType, ElisEnum.E_MODE_ALL, ElisEnum.E_SORT_BY_NUMBER )
			channelDB.SetListUse( E_ENUM_OBJECT_REUSE_ZAPPING )
			channelDB.Close( )
			#return self.mAllChannelList

		else :
			self.mAllChannelList = self.mCommander.Channel_GetList( aServiceType, ElisEnum.E_MODE_ALL, ElisEnum.E_SORT_BY_NUMBER )

		self.mAllChannelListHash = {}
		if self.mAllChannelList and len( self.mAllChannelList ) > 0 :
			for iChannel in self.mAllChannelList :
				channelKey = '%d:%d:%d'% ( iChannel.mSid, iChannel.mTsid, iChannel.mOnid )
				self.mAllChannelListHash[channelKey] = iChannel
				#LOG_TRACE( '---------hash key[%s] no[%s] name[%s]'% ( channelKey, iChannel.mNumber, iChannel.mName ) )

		self.UpdateTimerChannelByChangeNumber( )
		#LOG_TRACE( 'Reload AllChannels len[%s] hashLen[%s]'% ( len( self.mAllChannelList ), len( self.mAllChannelListHash ) ) )
		return self.mAllChannelList


	def Channel_GetCurrent( self, aTemporaryReload = 0 ) :
		if aTemporaryReload :
			return self.mCommander.Channel_GetCurrent( )

		return self.mCurrentChannel


	def Channel_GetCurrentSync( self ) :
		self.mCurrentChannel = self.mCommander.Channel_GetCurrent( )


	def Channel_SetOldChannel( self, aChannelNumber, aServiceType ) :
		newChannel = None
		cacheChannel = self.mChannelListHash.get( aChannelNumber, None )
		if cacheChannel :
			newChannel = cacheChannel.mChannel

		if not newChannel or newChannel.mError != 0 :
			#LOG_TRACE('newChannel None[%s]'% newChannel )
			return

		currentChannel = self.Channel_GetCurrent( )
		if currentChannel and currentChannel.mError == 0 :
			#LOG_TRACE('newChannel[%s %s]'% ( newChannel.mNumber, newChannel.mName ) )
			if currentChannel.mServiceType != aServiceType or \
			   currentChannel.mSid != newChannel.mSid or \
			   currentChannel.mTsid != newChannel.mTsid or \
			   currentChannel.mOnid != newChannel.mOnid or \
			   currentChannel.mNumber != newChannel.mNumber :
				self.mOldChannel = currentChannel
				#LOG_TRACE('init oldCh[%s %s]'% ( self.mOldChannel.mNumber, self.mOldChannel.mName ) )

		else :
			self.mOldChannel = newChannel
			#LOG_TRACE('init oldCh[%s %s]'% ( self.mOldChannel.mNumber, self.mOldChannel.mName ) )


	def Channel_SetOldChannelList( self, aServiceType ) :
		if not self.mOldChannel or self.mOldChannel.mError != 0 :
			return

		if not self.mOldChannelList or len( self.mOldChannelList ) < 1 :
			self.mOldChannelList = []

		for ch in self.mOldChannelList :
			if ch.mSid == self.mOldChannel.mSid and \
			   ch.mTsid == self.mOldChannel.mTsid and \
			   ch.mOnid == self.mOldChannel.mOnid and \
			   ch.mNumber == self.mOldChannel.mNumber :
				self.mOldChannelList.remove( ch )
				break

		#LOG_TRACE('add oldCh[%s %s]'% ( self.mOldChannel.mNumber, self.mOldChannel.mName ) )
		if aServiceType != self.mOldChannel.mServiceType :
			return

		self.mOldChannelList.insert( 0, self.mOldChannel )
		if len( self.mOldChannelList ) > 10 :
			self.mOldChannelList = self.mOldChannelList[:9]
			#from pvr.GuiHelper import ClassToList
			#LOG_TRACE('-------delete 10 over oldList[%s][%s]'% ( len(self.mOldChannelList), ClassToList('convert', self.mOldChannelList ) ) )


	def Channel_GetOldChannel( self ) :
		return self.mOldChannel


	def Channel_GetOldChannelList( self ) :
		return self.mOldChannelList


	def Channel_ResetOldChannelList( self ) :
		self.mOldChannel = None
		self.mOldChannelList = []


	def Channel_BackupOldChannelList( self ) :
		self.mBackupOldChannel = self.mOldChannel
		self.mBackupOldChannelList = copy.deepcopy( self.mOldChannelList )


	def Channel_RestoreOldChannelList( self ) :
		self.mOldChannel = self.mBackupOldChannel
		self.mOldChannelList = copy.deepcopy( self.mBackupOldChannel )


	def Channel_GetCurrentByPlaying( self ) :
		return self.mPlayingChannel


	def Channel_SetCurrent( self, aChannelNumber, aServiceType, aTemporaryHash = None, aFrontMessage = False ) :
		ret = False
		self.mCurrentEvent = None

		self.Channel_SetOldChannel( aChannelNumber, aServiceType )
		self.Channel_SetOldChannelList( aServiceType )

		if self.mRootWindow :
			self.mRootWindow.setProperty( 'Signal', 'True' )

		if self.mCurrentChannel and aChannelNumber != self.mCurrentChannel.mNumber :
			self.SetHbbTVEnable( False )

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

		if ret == True : #Reset LinkageService
			self.SetLinkageService( False )

		channel = self.Channel_GetCurrent( not ret )
		self.Frontdisplay_SetIcon( ElisEnum.E_ICON_HD, channel.mIsHD )
		self.mPlayingChannel = None

		LOG_TRACE( 'LAEL98 TEST FRONTDISPLAY ' )
		if aFrontMessage == True :
			LOG_TRACE( 'LAEL98 TEST FRONTDISPLAY ' )		
			self.Frontdisplay_SetMessage( channel.mName )
		return ret


	def Channel_SetCurrentSync( self, aChannelNumber, aServiceType, aFrontMessage = False ) :
		ret = False
		self.mCurrentEvent = None

		if self.GetStanbyStatus( ) != ElisEnum.E_STANDBY_POWER_ON :
			ret = self.Channel_SetCurrentByUpdateSync( aChannelNumber, aServiceType )
			return ret

		self.Channel_SetOldChannel( aChannelNumber, aServiceType )
		self.Channel_SetOldChannelList( aServiceType )

		if self.mCommander.Channel_SetCurrentAsync( aChannelNumber, aServiceType, 0 ) == True :
			cacheChannel = self.mChannelListHash.get( aChannelNumber, None )
			if cacheChannel :		
				self.mCurrentChannel = cacheChannel.mChannel
				ret = True

		if ret == True : #Reset LinkageService
			self.SetLinkageService( False )

		channel = self.Channel_GetCurrent( )
		self.Frontdisplay_SetIcon( ElisEnum.E_ICON_HD, channel.mIsHD )
		LOG_TRACE( 'LAEL98 TEST FRONTDISPLAY ' )		
		if aFrontMessage == True :
			LOG_TRACE( 'LAEL98 TEST FRONTDISPLAY ' )		
			self.Frontdisplay_SetMessage( channel.mName )
		return ret


	def Channel_SetCurrentByOld( self, aOldChannel ) :
		if aOldChannel and aOldChannel.mError == 0 :
			jumpChannel = self.Channel_GetCurr( aOldChannel.mNumber )
			if jumpChannel and jumpChannel.mError == 0 :
				self.SetAVBlankByChannel( jumpChannel )
				self.Channel_SetCurrent( jumpChannel.mNumber, jumpChannel.mServiceType, None, True )


	def Channel_SetCurrentByUpdateSync( self, aChannelNumber, aServiceType, aTemporaryHash = None, aFrontMessage = False ) :
		ret = False
		self.mCurrentEvent = None

		self.Channel_SetOldChannel( aChannelNumber, aServiceType )
		self.Channel_SetOldChannelList( aServiceType )

		if self.mRootWindow :
			self.mRootWindow.setProperty( 'Signal', 'True' )

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

		if ret == True : #Reset LinkageService
			self.SetLinkageService( False )

		channel = self.Channel_GetCurrent( not ret )
		self.Frontdisplay_SetIcon( ElisEnum.E_ICON_HD, channel.mIsHD )
		self.mPlayingChannel = None

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
				return self.Channel_GetNext( self.mChannelList[last], True )

			return None

		prevKey = cacheChannel.mPrevKey
		channel = self.mChannelListHash.get( prevKey, None )
		if channel == None :
			return None
		#LOG_TRACE('------------ Prev Channel-------------------')
		#channel.printdebug( )
		return channel.mChannel


	def Channel_GetNext( self, aChannel, aLast = False ) :
		if aChannel	== None or aChannel.mError != 0 :
			return None

		cacheChannel = self.mChannelListHash.get(aChannel.mNumber, None)
		if cacheChannel == None :
			# retry find end channel
			if self.mChannelList and len( self.mChannelList ) > 0 :
				cacheChannel = self.mChannelListHash.get( self.mChannelList[0].mNumber, None )
				if cacheChannel == None :
					return None

				channel = cacheChannel
				if aLast :
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
	def Channel_GetByNumber( self, aNumber, aUseDB = False, aTable = E_TABLE_ZAPPING, aType = ElisEnum.E_SERVICE_TYPE_TV ) :
		if aUseDB :
			if SUPPORT_CHANNEL_DATABASE	== True :
				channelDB = ElisChannelDB( )
				channelDB.SetListUse( E_ENUM_OBJECT_INSTANCE )
				channel = channelDB.Channel_GetNumber( aNumber, '', '', aType )
				channelDB.SetListUse( E_ENUM_OBJECT_REUSE_ZAPPING )
				channelDB.Close( )
				return channel

		else :
			cacheChannel = self.mChannelListHash.get( aNumber, None )
			if cacheChannel == None :
				return None

			channel = cacheChannel.mChannel
			return channel


	@DataLock
	def Channel_GetByAvailTransponder( self, aServiceType, aNumber, aTsid, aOnid, aSid, aSubTsid, aSubOnid ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			channelDB = ElisChannelDB( )
			channelDB.SetListUse( E_ENUM_OBJECT_INSTANCE )
			channel = channelDB.Channel_GetByAvailTransponder( aServiceType, aNumber, aTsid, aOnid, aSid, aSubTsid, aSubOnid )
			channelDB.SetListUse( E_ENUM_OBJECT_REUSE_ZAPPING )
			channelDB.Close( )
			return channel

		return None


	@DataLock
	def Channel_GetListByIDs( self, aServiceType, aTsid, aOnid, aSid, aLongitude = -1, aBand = -1, aSymbolRate = -1, aPolarization = -1 ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			channelDB = ElisChannelDB( )
			channelDB.SetListUse( E_ENUM_OBJECT_INSTANCE )
			channel = channelDB.Channel_GetListByIDs( aServiceType, aTsid, aOnid, aSid, self.mChannelListDBTable, aLongitude, aBand, aSymbolRate, aPolarization )
			channelDB.SetListUse( E_ENUM_OBJECT_REUSE_ZAPPING )
			channelDB.Close( )
			return channel

		return None


	def Channel_GetMaxNumber( self ) :
		return self.mMaxChannelNum


	def Channel_GetChannelByTimer( self, aTimer ) :
		channelKey = '%d:%d:%d'% ( aTimer.mSid, aTimer.mTsid, aTimer.mOnid )
		channel = self.mAllChannelListHash.get( channelKey, None )
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
		if eventList and len( eventList ) > 0 :
			eventList = eventList[0]

		return eventList


	def Epgevent_GetShortList( self, aType, aNumList ) :
		return self.mCommander.Epgevent_GetShortList( aType, aNumList )


	def Epgevent_GetShortListAll( self, aZappingMode = None ) :
		if not aZappingMode :
			aZappingMode = self.Zappingmode_GetCurrent( )

		zappingModes = [aZappingMode]
		return self.mCommander.Epgevent_GetShortListAll( zappingModes )


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


	def Channel_GetListBySatellite( self, aType, aMode, aSort, aLongitude, aBand, aKeyword = '', aInstanceLoad = False ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			channelDB = ElisChannelDB( )
			if aKeyword or aInstanceLoad :
				channelDB.SetListUse( E_ENUM_OBJECT_INSTANCE )
			channelList = channelDB.Channel_GetList( aType, aMode, aSort, aLongitude, aBand, -1, '', '', self.mSkip, self.mChannelListDBTable, aKeyword )
			channelDB.SetListUse( E_ENUM_OBJECT_REUSE_ZAPPING )
			channelDB.Close( )
			return channelList
		else :
			return self.mCommander.Channel_GetListBySatellite( aType, aMode, aSort, aLongitude, aBand )


	def Channel_GetListByFTACas( self, aType, aMode, aSort, aCAid, aKeyword = '', aInstanceLoad = False ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			channelDB = ElisChannelDB( )
			if aKeyword or aInstanceLoad :
				channelDB.SetListUse( E_ENUM_OBJECT_INSTANCE )
			channelList = channelDB.Channel_GetList( aType, aMode, aSort, None, None, aCAid, '', '', self.mSkip, self.mChannelListDBTable, aKeyword )
			channelDB.SetListUse( E_ENUM_OBJECT_REUSE_ZAPPING )
			channelDB.Close( )
			return channelList
		else :
			return self.mCommander.Channel_GetListByFTACas( aType, aMode, aSort, aCAid )


	def Channel_GetListByFavorite( self, aType, aMode, aSort, aFavName, aKeyword = '', aInstanceLoad = False ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			tunerTP = None
			recCount = self.Record_GetRunningRecorderCount( )

			if self.mChannelListDBTable == E_TABLE_ZAPPING :
				loopthrough = ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander ).GetProp( )
				if tunerTP == 1 and loopthrough :
					tunerTP = 1
				else :
					tunerTP = 2
			channelDB = ElisChannelDB( )
			if aKeyword or aInstanceLoad :
				channelDB.SetListUse( E_ENUM_OBJECT_INSTANCE )
			channelList = channelDB.Channel_GetList( aType, aMode, aSort, tunerTP, None, None, aFavName, '', self.mSkip, self.mChannelListDBTable, aKeyword )
			channelDB.SetListUse( E_ENUM_OBJECT_REUSE_ZAPPING )
			channelDB.Close( )
			"""
			if recCount > 0 :
				channelDB2 = ElisChannelDB( )				
				channelDB.SetListUse( E_ENUM_OBJECT_INSTANCE )
				favoriteList = channelDB2.Channel_GetList( aType, aMode, aSort, None, None, None, aFavName, self.mSkip, E_TABLE_ALLCHANNEL )
				channelDB.SetListUse( E_ENUM_OBJECT_REUSE_ZAPPING )
				channelDB2.Close( )

				favoriteHash =  {}
				for  channel in favoriteList :
					favoriteHash['%s' %channel.mNumber]= channel

				for channel in channelList :
					refChannel = favoriteHash.get( '%d' %(channel.mNumber ), None )
					if refChannel :
						channel.mPresentationNumber = refChannel.mPresentationNumber
			"""

			return channelList

		else :
			return self.mCommander.Channel_GetListByFavorite( aType, aMode, aSort, aFavName )


	def Channel_GetListByProvider( self, aType, aMode, aSort, aProvider, aKeyword = '', aInstanceLoad = False ) :
		channelList = []
		if SUPPORT_CHANNEL_DATABASE	== True :
			channelDB = ElisChannelDB( )
			if aKeyword or aInstanceLoad :
				channelDB.SetListUse( E_ENUM_OBJECT_INSTANCE )
			channelList = channelDB.Channel_GetList( aType, aMode, aSort, None, None, None, '', aProvider, self.mSkip, self.mChannelListDBTable, aKeyword )
			channelDB.SetListUse( E_ENUM_OBJECT_REUSE_ZAPPING )
			channelDB.Close( )

		return channelList


	def Channel_GetByOneForRecording( self, aSid ) :
		if SUPPORT_CHANNEL_DATABASE	== True :
			channelDB = ElisChannelDB( )
			channelDB.SetListUse( E_ENUM_OBJECT_INSTANCE )
			iChannel = channelDB.Channel_GetByOneForRecording( aSid )
			channelDB.SetListUse( E_ENUM_OBJECT_REUSE_ZAPPING )
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
		self.Channel_BackupOldChannelList( )
		return self.mCommander.Channel_Backup( )


	def Channel_Restore( self, aRestore ) :
		self.Channel_RestoreOldChannelList( )
		return self.mCommander.Channel_Restore( aRestore )


	def Channel_Delete( self, aUseDB, aIChannel ) :
		return self.mCommander.Channel_Delete( aUseDB, aIChannel )


	def Channel_DeleteByNumber( self, aType, aUseDB, aNumList ) :
		#ToDo delete timer ID
		return self.mCommander.Channel_DeleteByNumber( aType, aUseDB, aNumList )


	def Channel_DeleteAll( self, aDeleteTimer = True ) :
		#delete timer
		if aDeleteTimer :
			mTimerList = []
			mTimerList = self.Timer_GetTimerList( )

			if mTimerList :
				for timer in mTimerList:
					self.Timer_DeleteTimer( timer.mTimerId )

		return self.mCommander.Channel_DeleteAll( )


	def Channel_DeleteBySatellite( self, aLongitude, aBand, aChannelSave = True ) :
		ret = self.mCommander.Channel_DeleteBySatellite( aLongitude, aBand )
		if ret and aChannelSave :
			self.Channel_Save( )

		return ret


	def Channel_DeleteBySatellite_( self, aLongitude, aBand ) :
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
				self.Channel_Save( )
				self.SetChannelReloadStatus( True )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )
			self.SetSkipChannelView( False )

		return ret


	def UpdateTimerChannelByChangeNumber( self ) :
		mEditTimerList = []
		newNumber = []
		oldNumber = []
		zappingMode = self.Zappingmode_GetCurrent( )
		timerList = self.GetTimerList( )
		#LOG_TRACE( '------------mAllChannelListHash len[%s]'% len( self.mAllChannelListHash ) )
		if timerList and len( timerList ) > 0 :
			for timer in timerList :
				timerKey = '%d:%d:%d'% ( timer.mSid, timer.mTsid, timer.mOnid )
				iChannel = self.mAllChannelListHash.get( timerKey, None )
				#LOG_TRACE( '---------timerId[%s] timerKey[%s] iChannel[%s]'% ( timer.mTimerId, timerKey, iChannel ) )
				if iChannel :
					#LOG_TRACE( '---------find iChannel, timerId[%s] Tch[%s] type[%s],  ich[%s] type[%s]'% ( timer.mTimerId, timer.mChannelNo, timer.mServiceType, iChannel.mNumber, iChannel.mServiceType ) )
					if timer.mServiceType == iChannel.mServiceType and timer.mChannelNo != iChannel.mNumber :
						chTimer = ElisETimerChannel( )
						chTimer.mTimerID = timer.mTimerId
						chTimer.mNewChannel = iChannel.mNumber
						mEditTimerList.append( chTimer )

						newNumber.append( iChannel.mNumber )
						oldNumber.append( timer.mChannelNo )
						#LOG_TRACE( '---------change timer(change number) timerId[%s] name[%s] oldNo[%s] newNo[%s]'% ( timer.mTimerId, timer.mName, timer.mChannelNo, iChannel.mNumber ) )

				else :
					#LOG_TRACE( '---------channel not found, zappingmode[%s] timer serviceType[%s]'% ( zappingMode, timer.mServiceType ) )
					if zappingMode and zappingMode.mServiceType == timer.mServiceType :
						ret = self.Timer_DeleteTimer( timer.mTimerId )
						#LOG_TRACE( '---------delete timer(channel not found) ret[%s] timerId[%s] no[%s] name[%s]'% ( ret, timer.mTimerId, timer.mChannelNo, timer.mName ) )

		if mEditTimerList and len( mEditTimerList ) > 0 :
			ret = self.Timer_ChangeChannel( mEditTimerList )
			#LOG_TRACE( '------------UpdateTimerChannelByChangeNumber ret[%s] len[%s] newNumber[%s], timerHashLen[%s] oldNumber[%s]'% ( ret, len( newNumber ), newNumber, len( timerList ), oldNumber ) )


	def UpdateChannelByDBUpdate( self, aNumber, aType ) :
		#updated info by current channel
		ret = False
		if self.mChannelList == None or len( self.mChannelList ) < 1 :
			LOG_TRACE( 'Can not update channel info, channellist is None' )
			return ret

		iChannel = self.Channel_GetByNumber( aNumber, True, E_TABLE_ALLCHANNEL, aType )
		if not iChannel or iChannel.mError != 0 :
			LOG_TRACE( 'can not query none, Channel_GetByNumber chNo[%s] type[%s]'% ( aNumber, aType ) )
			return ret


		#find array index
		try :
			#update iChannel
			cacheChannel = None
			iChannelIdx = 0
			for channel in self.mChannelList :
				if channel.mNumber == iChannel.mNumber :			
					#channel.mPresentationNumber= iChannel.mPresentationNumber
					channel.mName= iChannel.mName
					channel.mServiceType= iChannel.mServiceType
					channel.mLocked= iChannel.mLocked
					channel.mIsCA= iChannel.mIsCA
					channel.mIsHD= iChannel.mIsHD
					channel.mNid= iChannel.mNid
					channel.mSid= iChannel.mSid
					channel.mTsid= iChannel.mTsid
					channel.mOnid= iChannel.mOnid
					channel.mCarrierType= iChannel.mCarrierType
					channel.mSkipped= iChannel.mSkipped
					channel.mIsBlank= iChannel.mIsBlank
					break

		except Exception, e :
			LOG_ERR( 'except[%s]update fail, ElisEventChannelDBUpdate'% e )

		"""
		#find array index
		try :
			#update iChannel
			cacheChannel = None
			iChannelIdx = 0
			for channel in self.mChannelList :
				if channel.mNumber == iChannel.mNumber :
					cacheChannel = self.mChannelListHash.get( iChannel.mNumber, -1 )
					if cacheChannel == -1 :
						LOG_TRACE( 'can not find channelList ch[%s %s]'% ( iChannel.mNumber, iChannel.mName ) )
						return ret
					fChannel = cacheChannel.mChannel
					break

				iChannelIdx += 1

			self.mChannelList[iChannelIdx] = iChannel
			updateCacheChannel = CacheChannel( iChannel, cacheChannel.mPrevKey, cacheChannel.mNextKey )
			self.mChannelListHash[fChannel.mNumber] = updateCacheChannel

			if self.mCurrentChannel and self.mCurrentChannel.mNumber == iChannel.mNumber :
				self.mCurrentChannel = iChannel
				LOG_TRACE( 'update mCurrentChannel by ElisEventChannelDBUpdate' )

			#LOG_TRACE( '-----updated channelList: idx[%s] new[%s %s]ca[%s]  old[%s %s]ca[%s]'% ( iChannelIdx, iChannel.mNumber, iChannel.mName, iChannel.mIsCA, fChannel.mNumber, fChannel.mName, fChannel.mIsCA ) )
			self.SetChannelReloadStatus( True )

			ret = True
			LOG_TRACE( 'success channelList update by ElisEventChannelDBUpdate ch[%s %s]'% ( iChannel.mNumber, iChannel.mName ) )

		except Exception, e :
			LOG_ERR( 'except[%s]update fail, ElisEventChannelDBUpdate'% e )
		"""
		return ret


	def Channel_ChangeChannelName( self, aChannelNumber, aServiceType, aNewName ) :
		return self.mCommander.Channel_ChangeChannelName( aChannelNumber, aServiceType, aNewName )


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

			self.Channel_SetZappingListStatus( True )
			self.Frontdisplay_SetIcon( ElisEnum.E_ICON_REC, recCount )
			return self.mCommander.Channel_GetZappingList( aSync )


	def Channel_GetZappingListStatus( self ) :
		return self.mZappingListChange


	def Channel_SetZappingListStatus( self, aChange = False ) :
		self.mZappingListChange = aChange


	def GetChannelByIDs( self, aSid, aTsid, aOnid, aAllChannel = False ) :
		findHash = self.mChannelListHashForTimer
		if aAllChannel :
			findHash = self.mAllChannelListHash

		if findHash == None or len( findHash ) <= 0 :
			return None

		return findHash.get( '%d:%d:%d' %( aSid, aTsid, aOnid ), None )


	def GetChannelReloadStatus( self ) :
		return self.mCacheReload


	def SetChannelReloadStatus( self, aReload = False ) :
		self.mCacheReload = aReload


	def Channel_ReLoad( self, aDefaultTune = True ) :
		mCurrentChannel = self.Channel_GetCurrent( )

		self.LoadZappingmode( )
		self.LoadZappingList( )
		self.LoadChannelList( )
		self.Channel_GetAllChannels( self.mZappingMode.mServiceType, False )
		self.SetChannelReloadStatus( True )
		import pvr.gui.WindowMgr as WinMgr
		WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_SIMPLE_CHANNEL_LIST ).ResetControls( )

		if aDefaultTune :
			#self.Channel_TuneDefault( mCurrentChannel )
			self.Channel_TuneDefault( False, mCurrentChannel )
			if E_V1_2_APPLY_PIP :
				self.PIP_SetTunableList( )


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
				self.Channel_SetCurrentSync( aCurrentChannel.mNumber, aCurrentChannel.mServiceType )
				#LOG_TRACE( '-------------1 tune[%s %s]'% ( aCurrentChannel.mNumber, aCurrentChannel.mName ) )
				return

			else :
				isCurrentChannelDelete = True

		if aCurrentChannel == None or isCurrentChannelDelete :
			channelList = self.Channel_GetList( )
			if channelList and len( channelList ) > 0 :
				self.Channel_SetCurrentSync( channelList[0].mNumber, channelList[0].mServiceType )
				#LOG_TRACE( '-------------2 tune[%s %s]'% ( channelList[0].mNumber, channelList[0].mName ) )


	def Channel_ReTune( self ) :
		iChannel = self.Channel_GetCurrent( )
		channelList = self.Channel_GetList( )
		if iChannel and channelList and len( channelList ) > 0 :
			self.Channel_InvalidateCurrent( )
			self.Channel_SetCurrentSync( iChannel.mNumber, iChannel.mServiceType )

		else :
			LOG_ERR( 'Load Channel_GetCurrent None' )

			if E_V1_2_APPLY_PIP :
				self.PIP_SetTunableList( )

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


	def Audiotrack_GetForRecord( self, aKey, aIndex ) :
		return self.mCommander.Audiotrack_GetForRecord( aKey, aIndex )


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
				self.LoadVolumeBySetGUI( )


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
		import pvr.gui.DialogMgr as DiaMgr
		DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).SwapExchangeToPIP( None, True, False )

		if xbmcgui.Window( 10000 ).getProperty( 'RadioPlayback' ) == E_TAG_TRUE :
			xbmcgui.Window( 10000 ).setProperty( 'RadioPlayback', E_TAG_FALSE )

		self.SetAVBlankByArchive( False )
		ret = self.mCommander.Player_Stop( )
		self.Frontdisplay_PlayPause( False )
		self.mPMTinstance = None
		self.mPlayingChannel = None
		if not self.Get_Player_AVBlank( ) :
			self.mPlayingChannel = self.Channel_GetCurrent( )

		lblMode = MR_LANG( 'LIVE' )
		thread = threading.Timer( 0.1, AsyncShowStatus, [lblMode] )
		thread.start( )

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


	def Player_JumpTo( self, aMiliSec ) :
		return self.mCommander.Player_JumpTo( aMiliSec )


	def Player_JumpToIFrame( self, aMiliSec ) :
		return self.mCommander.Player_JumpToIFrame( aMiliSec )


	def Player_StartTimeshiftPlayback( self, aPlayBackMode, aData ) :
		ret = self.mCommander.Player_StartTimeshiftPlayback( aPlayBackMode, aData )
		self.Frontdisplay_PlayPause( )
		return ret


	def Player_StartInternalRecordPlayback( self, aRecordKey, aServiceType, aOffsetMS, aSpeed ) :
		ret = self.mCommander.Player_StartInternalRecordPlayback( aRecordKey, aServiceType, aOffsetMS, aSpeed )
		#self.InitBookmarkButton( )
		self.SetAVBlankByArchive( True )
		self.Frontdisplay_PlayPause( )
		"""
		recInfo = self.Record_GetRecordInfoByKey( aRecordKey )
		if recInfo and recInfo.mError == 0 :
			self.Frontdisplay_SetMessage( recInfo.mChannelName )
		"""

		if aServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
			xbmcgui.Window( 10000 ).setProperty( 'RadioPlayback', E_TAG_TRUE )

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


	def RecordItem_HasRecordablePartition( self ) :
		return self.mCommander.RecordItem_HasRecordablePartition( )


	def Record_GetRunningRecorderCount( self ) :
		return self.mCommander.Record_GetRunningRecorderCount( )


	def Record_GetRunningRecordInfo( self, aIndex ) :
		return self.mCommander.Record_GetRunningRecordInfo( aIndex )


	def Record_GetAgeRating( self, aRecordKey ) :
		if SUPPORT_RECORD_DATABASE == True :
			recordDB = ElisRecordDB( )
			recordAgeRating = recordDB.Record_GetAgeRating( aRecordKey )
			recordDB.Close( )
			return recordAgeRating

		else :
			return 0


	def Record_GetCount( self, aServiceType ) :
		if SUPPORT_RECORD_DATABASE == True :
			recordDB = ElisRecordDB( )
			recordCount = recordDB.Record_GetCount( aServiceType )
			recordDB.Close( )
			return recordCount

		else :
			return self.mCommander.Record_GetCount( aServiceType )


	def Record_GetList( self, aServiceType, aHideWatched = False, aMountInfo = '' ) :
		if SUPPORT_RECORD_DATABASE == True :	
			recordDB = ElisRecordDB( )
			recordList = recordDB.Record_GetList( aServiceType, aHideWatched, aMountInfo )
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


	def Record_DeleteByKeyList( self, aServiceType, aKeyList ) :
		return self.mCommander.Record_DeleteByKeyList( aServiceType, aKeyList )


	def Record_DeleteAllRecord( self, aServiceType ) :
		return self.mCommander.Record_DeleteAllRecord( aServiceType )


	def Record_SetLock(self, aKey, aServiceType, aLock ) :
		return self.mCommander.Record_SetLock( aKey, aServiceType, aLock )


	def Record_Rename(self, aKey, aServiceType, aNewName ) :
		return self.mCommander.Record_Rename( aKey, aServiceType, aNewName )


	def Record_GetMountInfo( self, aKey ) :
		if SUPPORT_RECORD_DATABASE == True :
			recordDB = ElisRecordDB( )
			recInfo = recordDB.Record_GetMountInfo( aKey )
			recordDB.Close( )
			return recInfo


	def Record_GetNetworkVolume( self, aCache = False ) :
		if aCache :
			return self.mNetVolumeList

		self.mNetVolumeList = self.mCommander.Record_GetNetworkVolume( )
		return self.mNetVolumeList


	def Record_AddNetworkVolume( self, aENetworkVolume ) :
		return self.mCommander.Record_AddNetworkVolume( [aENetworkVolume] )


	def Record_DeleteNetworkVolume( self, aENetworkVolume ) :
		return self.mCommander.Record_DeleteNetworkVolume( [aENetworkVolume] )


	def Record_SetDefaultVolume( self, aENetworkVolume ) :
		return self.mCommander.Record_SetDefaultVolume( [aENetworkVolume] )


	def Record_RefreshNetworkVolume( self ) :
		return self.mCommander.Record_RefreshNetworkVolume( )


	def InitNetworkVolume( self ) :
		from pvr.GuiHelper import CheckNetworkStatus, RefreshMountToSMB
		#return value, 1'st value :
		#  inteager < 0 : error No.
		#  inteager > 0 : fail count
		#  inteager = 0 : success

		#return value, 2'nd value :
		#  lblText : status label

		retVal = 0
		isFail = False
		lblLine = MR_LANG( 'Network volume failure' )
		try :
			if not CheckNetworkStatus( ) :
				retVal = -1
				lblLine = MR_LANG( 'Try again after connecting network' )
				raise Exception, 'pass, network fail'

			status = self.Player_GetStatus( )
			if status == ElisEnum.E_MODE_PVR :
				retVal = -2
				lblLine = MR_LANG( 'Try again after stopping playback' )
				raise Exception, 'pass, pvr playing'

			if self.Record_GetRunningRecorderCount( ) :
				retVal = -3
				lblLine = MR_LANG( 'Try again after stopping record' )
				raise Exception, 'pass, run recording'

			volumeList = self.Record_GetNetworkVolume( )
			if not volumeList or len( volumeList ) < 1 :
				retVal = -4
				lblLine = MR_LANG( 'Record path is empty' )
				raise Exception, 'pass, volume list None'

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )
			isFail = True

		if isFail :
			return retVal, lblLine

		lblLine = MR_LANG( 'Success' )
		volumeCount = len( volumeList )
		count = 0
		failCount = 0
		failItem = ''
		defVolume = None
		for netVolume in volumeList :
			count += 1
			cmd = netVolume.mMountCmd
			lblLabel = '[%s/%s]%s'% ( count, volumeCount, os.path.basename( netVolume.mMountPath ) )
			LOG_TRACE( '[DataCache]checkVolume %s'% lblLabel )

			failCount_, failItem_ = RefreshMountToSMB( netVolume )
			failCount += failCount_
			if failItem_ :
				failItem += ',%s'% failItem_
			time.sleep( 0.5 )

		self.Record_RefreshNetworkVolume( )
		self.Record_GetNetworkVolume( )
		if failCount > 0 :
			lblLine = '%s\n%s'% ( MR_LANG( 'Record path failure' ), failItem[1:] )
			LOG_TRACE( '[DataCache]%s'% lblLine )

		#1. reload defVolume
		volumeList = self.Record_GetNetworkVolume( True )
		if volumeList and len( volumeList ) > 0 :
			for netVolume in volumeList :
				if netVolume.mIsDefaultSet :
					defVolume = netVolume
					break

		#2. nas only one? must default
		if not self.HDD_GetMountPath( ) and self.mNetVolumeList and len( self.mNetVolumeList ) == 1 :
			defVolume = self.mNetVolumeList[0]
			defVolume.mIsDefaultSet = 1

		#3. use not able? change default hdd
		if defVolume and defVolume.mIsDefaultSet :
			defProperty = 1
			if not defVolume.mOnline or defVolume.mReadOnly :
				defProperty = 0
				defVolume.mIsDefaultSet = 0
				LOG_TRACE( '[DataCache]changed reset path : HDD' )

			self.Record_SetDefaultVolume( defVolume )
			ElisPropertyEnum( 'Record Default Path Change', self.mCommander ).SetProp( defProperty )
			self.Record_GetNetworkVolume( )

		return failCount, lblLine


	def Timer_StopRecordingByRecordKey( self, aKey ) :
		return self.mCommander.Timer_StopRecordingByRecordKey( aKey )


	def Timer_GetTimerList( self ) :
		timerList = []	
		if SUPPORT_TIMER_DATABASE == True :
			timerDB = ElisTimerDB( )
			timerList = timerDB.Timer_GetTimerList( )
			timerDB.Close( )
		else :
			timerCount = self.Timer_GetTimerCount( )
			for i in range( timerCount ) :
				timer = self.Timer_GetByIndex( i )
				timerList.append( timer )

		if not timerList :
			timerList = []

		"""
		runningTimers = self.Timer_GetRunningTimers()

		try :
			if runningTimers and len(runningTimers) > 0 :
				for i in range( len(runningTimers) ) :
					hasMatch = False
					timerCount = len( timerList )
					for j in range( timerCount ) :
						if runningTimers[ i ].mTimerId == timerList[ j ].mTimerId :
							hasMatch = True
							break

					if hasMatch == False :
						timerList.append( runningTimers[i] )

		except Exception, e :
			timerList = []
			LOG_ERR( 'Exception [%s]'% e )
		"""
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


	def Timer_EditManualTimer(self , aTimerId, aNewStartTime, aNewDuration ) :
		return self.mCommander.Timer_EditManualTimer( aTimerId, aNewStartTime, aNewDuration )	


	def Timer_ChangeChannel( self, aETimerChannel ) :
		return self.mCommander.Timer_ChangeChannel( aETimerChannel )


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


	def Timer_AddManualTimer( self, aChannelNo, aServiceType, aStartTime, aDuration, aTimerName, aForceDecrypt, aVolumeId = 0 ) :
		ret = False
		if E_SUPPORT_EXTEND_RECORD_PATH :
			ret = self.mCommander.Timer_AddManualTimer( aChannelNo, aServiceType, aStartTime, aDuration, aTimerName, aForceDecrypt, aVolumeId )
		else :
			ret = self.mCommander.Timer_AddManualTimer( aChannelNo, aServiceType, aStartTime, aDuration, aTimerName, aForceDecrypt )
		return ret


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


	def Timer_AddViewTimer( self, aChannelNo, aServiceType, aStartTime, aTimerName ) :
		return self.mCommander.Timer_AddViewTimer( aChannelNo, aServiceType, aStartTime, aTimerName )


	def Timer_EditViewTimer( self, aTimerId,  aNewStartTime ) :
		return self.mCommander.Timer_EditViewTimer( aTimerId, aNewStartTime )


	def Timer_AddViewWeeklyTimer( self, aChannelNo, aServiceType, aStartTime, aExpiryTime, aTimerName, aForceDecrypt, aWeeklyTimerCount, aWeeklyTimer ) :
		return self.mCommander.Timer_AddViewWeeklyTimer( aChannelNo, aServiceType, aStartTime, aExpiryTime, aTimerName, aForceDecrypt, aWeeklyTimerCount, aWeeklyTimer )


	def Timer_AddOneViewWeeklyTimer( self, aTimerId, aDate, aStartTime, aDuration = 10 ) :
		return self.mCommander.Timer_AddViewWeeklyTimerItem( aTimerId, aDate, aStartTime, aDuration )


	def Timer_EditViewWeeklyTimer( self, aTimerId, aDate, aStartTime, aNewStartTime, aDuration = 10, aNewDuration = 10 ) :
		return self.mCommander.Timer_EditViewWeeklyTimer( aTimerId, aDate, aStartTime, aDuration, aNewStartTime, aNewDuration )


	def Timer_EditOneViewWeeklyTimer( self, aTimerId, aStartTime, aDuration, aNewStartTime, aNewDuration ) :
		return self.mCommander.Timer_EditOneViewWeeklyTimer( aTimerId, aStartTime, aDuration, aNewStartTime, aNewDuration )


	def Timer_DeleteOneViewWeeklyTimer( self, aTimerId, aDate, aStartTime, aDuration = 10 ) :
		return self.mCommander.Timer_EditViewWeeklyTimer( aTimerId, aDate, aStartTime, aDuration, aStartTime, 0 ) 


	def Teletext_Show( self ) :
		return self.mCommander.Teletext_Show( )


	def Teletext_NotifyHide( self ) :
		return self.mCommander.Teletext_NotifyHide( )


	def Teletext_IsShowing( self ) :
		return self.mCommander.Teletext_IsShowing( )


	def Subtitle_IsShowing( self ) :
		return self.mCommander.Subtitle_IsShowing( )


	def Subtitle_Show( self ) :
		return self.mCommander.Subtitle_Show( )


	def Subtitle_Hide( self ) :
		return self.mCommander.Subtitle_Hide( )


	def Subtitle_GetSelected( self ) :
		return self.mCommander.Subtitle_GetSelected( )


	def Subtitle_Get( self, aIndex ) :
		return self.mCommander.Subtitle_Get( aIndex )


	def Subtitle_GetCount( self ) :
		return self.mCommander.Subtitle_GetCount( )


	def Subtitle_Select( self, aPid, aPageId, aSubId ) :
		return self.mCommander.Subtitle_Select( aPid, aPageId, aSubId )


	def Subtitle_SetBySpeed( self, aSpeed = 100 ) :
		selectedSubtitle = self.Subtitle_GetSelected( )
		if ( not selectedSubtitle ) or selectedSubtitle.mError != 0 or selectedSubtitle.mPid <= 0 :
			#LOG_TRACE( 'Subtitle : Not Selected' )
			return

		showSubtitle = False
		if aSpeed == 100 or \
		   aSpeed >= 200 and aSpeed <= 800 :
			showSubtitle = True

		ret = 0
		if showSubtitle :
			ret = self.Subtitle_Show( )
		else :
			ret = self.Subtitle_Hide( )

		#LOG_TRACE( 'set Subtitle[%s] ret[%s] speed[%s]'% ( showSubtitle, ret, aSpeed ) )


	def Frontdisplay_SetMessage( self, aName ) :
		newName = aName.encode('utf-8')
		self.mCommander.Frontdisplay_SetMessage( newName )


	def Frontdisplay_SetCurrentMessage( self ) :
		LOG_TRACE( 'LAEL98 TEST FRONTDISPLAY ' )
		if self.mChannelList and len( self.mChannelList ) > 0 :
			if self.mCurrentChannel :
				self.Frontdisplay_SetMessage( self.mCurrentChannel.mName )
			else :
				self.Frontdisplay_SetMessage( MR_LANG( 'NoChannel' ) )
		else :
			self.Frontdisplay_SetMessage( MR_LANG( 'NoChannel' ) )


	def Frontdisplay_SetIcon( self, aIconIndex, aOnOff ) :
		self.mCommander.Frontdisplay_SetIcon( aIconIndex, aOnOff )


	def Frontdisplay_Resolution( self, aResolution = None ) :
		self.Frontdisplay_SetIcon( ElisEnum.E_ICON_1080i, False )
		self.Frontdisplay_SetIcon( ElisEnum.E_ICON_1080p, False )
		self.Frontdisplay_SetIcon( ElisEnum.E_ICON_720p, False )

		mIsHD = False
		if aResolution >= ElisEnum.E_ICON_1080i and aResolution <= ElisEnum.E_ICON_720p :
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
			elif hdmiFormat == '1080p' :
				iconIndex = ElisEnum.E_ICON_1080p

			self.Frontdisplay_Resolution( iconIndex )
		else :
			self.SaveResolution( aEvent )
			if hdmiFormat == 'Automatic' :
				if aEvent.mVideoHeight <= 576 :
					iconIndex = -1
				elif aEvent.mVideoHeight <= 720 :
					iconIndex = ElisEnum.E_ICON_720p

				else :
					if aEvent.mVideoInterlaced == 0 :
						iconIndex = ElisEnum.E_ICON_1080p

				self.Frontdisplay_Resolution( iconIndex )

				if self.mOldHdmiFormatIndex != iconIndex and self.PIP_GetStatus( ) :
					import pvr.gui.DialogMgr as DiaMgr
					DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).PIP_SetPositionSync( True )

				self.mOldHdmiFormatIndex = iconIndex


	def Frontdisplay_PlayPause( self, aIcon = True ) :
		play = 1	#on
		pause= 0	#off
		if aIcon :
			status = self.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_LIVE :
				play = 0
				pause= 0
			else :
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


	def HDD_GetMountPath( self, aFind = '', aCheckForce = False ) :
		hddPath = ''
		if not aCheckForce :
			if pvr.Platform.GetPlatform( ).GetProduct( ) == PRODUCT_OSCAR :
				return hddPath

		retList = self.mCommander.HDD_GetMountPath( )
		if retList and len( retList ) > 0 and retList[0].mError == 0 :
			hddPath = retList[0].mParam
			if aFind :
				hddPath = ''
				for idx in range( len( retList ) ) :
					if os.path.basename( retList[idx].mParam ) == aFind :
						hddPath = retList[idx].mParam
						break

		return hddPath


	def System_Reboot( self ) :
		xbmc.executebuiltin( 'Settings.Save' )
		time.sleep( 1 )
		if not self.mCommander.System_Reboot( ) :
			LOG_ERR( 'System_Reboot Fail' )


	def System_Shutdown( self ) :
		xbmc.executebuiltin( 'Settings.Save' )
		time.sleep( 1 )
		if not self.mCommander.System_Shutdown( ) :
			LOG_ERR( 'System_Shutdown Fail' )


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
				LOG_TRACE('Could not change. currType[%s] failType[%s] 1:TV, 2:Radio, channel is None'% ( zappingMode.mServiceType, newZappingMode.mServiceType ) )
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
			LOG_TRACE( '-----------------ElisPropertyInt lastChannelNumber[%s]'% lastChannelNumber )
			cacheChannel = self.mChannelListHash.get( lastChannelNumber, None )
			if cacheChannel :
				iChannel = cacheChannel.mChannel
				LOG_TRACE( 'find last Channel ch[%s %s] type[%s]'% ( iChannel.mNumber, iChannel.mName, iChannel.mServiceType ) )

			if iChannel :
				self.Channel_SetCurrent( iChannel.mNumber, iChannel.mServiceType )
				#LOG_TRACE( 'tune Channel ch[%s %s] type[%s]'% ( iChannel.mNumber, iChannel.mName, iChannel.mServiceType ) )

			self.Channel_ResetOldChannelList( )


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
		if aPMTEvent and aPMTEvent.mPMTSource == ElisEnum.E_MODE_PVR :
			self.mPMTinstance = aPMTEvent
			return

		channel = self.Channel_GetCurrent( )
		if channel and channel.mError == 0 :
			hashkey = '%d:%d:%d'% ( channel.mSid, channel.mTsid, channel.mOnid )
			self.mPMTListHash[hashkey] = aPMTEvent


	def GetCurrentPMTEventByPVR( self ) :
		return self.mPMTinstance


	def GetCurrentPMTEvent( self, aFindChannel = None ) :
		pmt = None
		channel = self.Channel_GetCurrent( )
		if aFindChannel :
			channel = aFindChannel

		if channel and channel.mError == 0 :
			hashkey = '%d:%d:%d'% ( channel.mSid, channel.mTsid, channel.mOnid )
			pmt = self.mPMTListHash.get( hashkey, None )

		return pmt

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
			self.Frontdisplay_SetMessage( MR_LANG( 'Media Center' ) )
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
		return self.mPropertyPlaybackBannerTime


	def SetParentLockPass( self, aPass = False ) :
		self.mParentLockPass = aPass


	def GetParentLockPass( self ) :
		return self.mParentLockPass


	def SetParentLock( self, aLock = True ) :
		self.mParentLock = aLock


	def SetAgeGurantee( self, aGurantee = -1 ) :
		self.mAgeGurantee = aGurantee
		if aGurantee == -1 :
			self.mAgeGurantee = self.mPropertyAge


	def GetAgeGurantee( self ) :
		return self.mAgeGurantee


	def GetStatusByParentLock( self ) :
		return self.mParentLock


	def GetParentLock( self, aCheckEPG = None ) :
		isLimit = False

		iEPG  = self.mEPGData
		iMode = self.Player_GetStatus( ).mMode
		iLock = self.mParentLock
		if aCheckEPG :
			iEPG  = aCheckEPG
			iMode = ElisEnum.E_MODE_LIVE
			iLock = True

		LOG_TRACE( 'parentlock checking[%s]'% self.mParentLock )
		if iMode == ElisEnum.E_MODE_LIVE and \
		   iLock and ( iEPG and iEPG.mError == 0 ) :
			isLimit = AgeLimit( self.mPropertyAge, iEPG.mAgeRating, self.mAgeGurantee )
			LOG_TRACE( 'isLimit[%s]'% isLimit )

		return isLimit


	def SetParentLockByEPG( self ) :
		self.mParentLockEPG = self.mEPGData


	def CheckExpireByParentLock( self ) :
		if self.mParentLockEPG and self.mParentLockEPG.mError == 0 :
			LOG_TRACE( '----------mParentLockEPG eventId[%s] name[%s] isSeries[%s] age[%s] time[%s %s]'% ( self.mParentLockEPG.mEventId, self.mParentLockEPG.mEventName, self.mParentLockEPG.mIsSeries, self.mParentLockEPG.mAgeRating, self.mParentLockEPG.mStartTime, self.mParentLockEPG.mDuration ) )
			startTime = self.mParentLockEPG.mStartTime + self.Datetime_GetLocalOffset( )
			endTime   = startTime + self.mParentLockEPG.mDuration
			LOG_TRACE( 'localTime[%s] duration[%s] startTime[%s] endTime[%s]'% ( TimeToString( self.Datetime_GetLocalTime( ), TimeFormatEnum.E_HH_MM ), TimeToString( self.mParentLockEPG.mDuration, TimeFormatEnum.E_HH_MM ), TimeToString( startTime, TimeFormatEnum.E_HH_MM ), TimeToString( endTime, TimeFormatEnum.E_HH_MM ) ) )
			if ( not self.GetParentLock( ) ) and self.Datetime_GetLocalTime( ) > endTime :
				self.SetParentLock( True )
				LOG_TRACE( '--------parentLock expired, check again by new epg age rating' )

		else :
			self.mParentLockEPG = self.GetEpgeventCurrent( )


	def SetPincodeDialog( self, aOnShow = False ) :
		self.mIsPincodeDialog = aOnShow


	def GetPincodeDialog( self ) :
		return self.mIsPincodeDialog


	def SetDefaultHideWatched( self, aHideWatched = False ) :
		self.mDefaultHideWatched = aHideWatched


	def GetDefaultHideWatched( self ) :
		return self.mDefaultHideWatched


	def SetStanbyClosing( self, aFlag ) :
		self.mStandByClose = aFlag


	def GetStanbyClosing( self ) :
		return self.mStandByClose


	def SetStanbyStatus( self, aFlag ) :
		self.mStandByStatus = aFlag


	def GetStanbyStatus( self ) :
		return self.mStandByStatus


	def SetDefaultByFactoryReset( self ) :
		LOG_TRACE('-------factory reset')
		self.mPMTListHash = {}
		self.Channel_ResetOldChannelList( )
		self.InitBookmarkButton( )
		#1. pincode : m/w (super pin)
		#2. video : 1080i, normal, RGB
		LOG_TRACE( '>>>>>>>> Default init : Video <<<<<<<<' )
		ElisPropertyEnum( 'HDMI Format', self.mCommander ).SetPropString( '1080i' )
		ElisPropertyEnum( 'Show 4:3', self.mCommander ).SetPropString( 'Normal (Pillarbox)' )
		ElisPropertyEnum( 'HDMI Color Space', self.mCommander ).SetPropString( 'RGB' )
		self.Frontdisplay_Resolution( ElisEnum.E_ICON_1080i )

		#3. network : dhcp
		LOG_TRACE( '>>>>>>>> Default init : Network <<<<<<<<' )
		NetMgr.GetInstance( ).ResetNetwork( )
		
		#4. time setting : m/w (Time and Date, Local time offset, Summer Time)

		#5. epg, archive
		self.SetDefaultHideWatched( True )

		#delete setting file
		settingsDir = xbmc.translatePath( "special://profile/addon_data/script.mbox/settings.xml" )
		os.system( 'rm %s' % settingsDir )
		#ret = SetDefaultSettingInXML( )
		#LOG_TRACE( '>>>>>>>> Default init : epg,archive ret[%s] <<<<<<<<'% ret )

		#6. ageRating
		LOG_TRACE( '>>>>>>>> Default init : AgeLimit <<<<<<<<' )
		ElisPropertyEnum( 'Age Limit', self.mCommander ).SetPropString( 'No Limit' )
		self.SetPropertyAge( 0 )

		#7. channelList, LivePlate
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


	def SyncMute( self ) :
		xbmcMute = XBMC_GetMute( )
		playerMute = self.mCommander.Player_GetMute( )

		if xbmcMute != playerMute :
			playerMute = True
		if not xbmcMute :
			playerMute = False
		self.mCommander.Player_SetMute( playerMute )


	def InitBookmarkButton( self ) :
		for button in self.mBookmarkButton :
			button.setVisible( False )


	def SetBookmarkButton( self, aButtonList ) :
		self.mBookmarkButton = aButtonList


	def GetBookmarkButton( self ) :
		return self.mBookmarkButton


	def InitBookmarkHash( self ) :
		self.mBookmarkHash = {}


	def GetBookmarkHash( self, aBookmark ) :
		return self.mBookmarkHash.get( aBookmark, -1 )


	def SetBookmarkHash( self, aControlId, aBookmark ) :
		self.mBookmarkHash[aBookmark] = aControlId


	def DeleteBookmarkHash( self, aBookmark ) :
		if self.GetBookmarkHash( aBookmark ) != -1 :
			del self.mBookmarkHash[aBookmark]


	def SetSearchNewChannel( self, aFlag ) :
		self.mSearchNewChannel = aFlag


	def GetSearchNewChannel( self ) :
		return self.mSearchNewChannel


	def GetUSBAttached( self ) :
		return self.mUSBAttatched


	@DataLock
	def SetUSBAttached( self, aAttached = False ) :
		self.mUSBAttatched = aAttached


	def SetRootWindowId( self, aId ) :
		self.mRootWindowId = aId


	def GetRootWindowId( self ) :
		return self.mRootWindowId


	def CheckPresentationNumber( self, aChannel, aMode = None ) :
		zappingMode = aMode
		if aMode == None :
			zappingMode = self.mZappingMode

		iChNumber = aChannel.mNumber
		if zappingMode and zappingMode.mMode == ElisEnum.E_MODE_FAVORITE :
			iChNumber = aChannel.mPresentationNumber

		return iChNumber


	def SetAlarmByViewTimer( self, aViewTimer = False ) :
		self.mChangedByViewTimer = aViewTimer


	def GetAlarmByViewTimer( self ) :
		return self.mChangedByViewTimer


	def SetDelaySettingWindow( self, aValue ) :
		self.mDelaySettingWindow = aValue


	def GetDelaySettingWindow( self ) :
		return self.mDelaySettingWindow


	def SetLinkageService( self, aBool ) :
		self.mHasLinkageService = aBool


	def GetLinkageService( self ) :
		return self.mHasLinkageService


	def SetVideoOutput( self, aVideoOutput = E_VIDEO_HDMI ) :
		self.mVideoOutput = aVideoOutput


	def GetVideoOutput( self ) :
		return self.mVideoOutput


	def PIP_Start( self, aNumber ) :
		return self.mCommander.PIP_Start( aNumber )


	def PIP_Stop( self, aResetSwap = True ) :
		if aResetSwap and self.PIP_GetSwapStatus( ) :
			import pvr.gui.DialogMgr as DiaMgr
			DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).SwapExchangeToPIP( None, True, False )

		return self.mCommander.PIP_Stop( )


	def PIP_GetStatus( self ) :
		return self.mPIPStart


	def PIP_SetStatus( self, isStart = False ) :
		self.mPIPStart = isStart


	def PIP_SetDimension( self, aPosX, aPosY, aWidth, aHeight ) :
		return self.mCommander.PIP_SetDimension( aPosX, aPosY, aWidth, aHeight )


	def PIP_GetCurrent( self ) :
		return self.mCommander.PIP_GetCurrent( )


	def PIP_GetTunableList( self, aTemporaryReload = 0 ) :
		if aTemporaryReload :
			tunableList = self.PIP_InitChannel( )

			"""
			retList = self.mCommander.PIP_GetTunableList( )
			if retList and len( retList ) > 0 :
				for item in retList :
					tunableList.append( item.mParam )
					iChannel = channelListHash.get( item.mParam, None )
					if iChannel :
						tunableList.append( iChannel )
			"""

			return tunableList

		else :
			return self.mChannelListPIP


	def PIP_InitChannel( self ) :
		channelListPIP = []

		#2.find pip channel in 1
		aTunableList = self.mCommander.PIP_GetTunableList( )

		if aTunableList and len( aTunableList ) > 0 :
			#1.current channel in TV
			currentMode = self.Zappingmode_GetCurrent( )
			channelList = self.Channel_GetList( )
			if currentMode and currentMode.mServiceType != ElisEnum.E_SERVICE_TYPE_TV :
				channelList = self.Channel_GetAllChannels( ElisEnum.E_SERVICE_TYPE_TV, False )

			channelListHash = {}
			if channelList and len( channelList ) > 0 :
				for channel in channelList :
					channelListHash[channel.mNumber] = channel

				for item in aTunableList :
					iChannel = channelListHash.get( item.mParam, None )
					if iChannel :
						channelListPIP.append( iChannel )

		return channelListPIP


	def PIP_SetTunableList( self ) :
		self.PIP_StopByDeleteChannel( )
		self.mChannelListPIP = self.PIP_InitChannel( )
		self.mChannelListHashPIP = {}

		count = len( self.mChannelListPIP )
		LOG_TRACE( '-------2-------------count[%d]'% count )
		if count < 1 :
			return False

		#3.init prev,next
		prevChannel = self.mChannelListPIP[count-1]
		for i in range( count ) :
			channel = self.mChannelListPIP[i]
			if i+1 < count :
				nextChannel = self.mChannelListPIP[i+1]
			else:
				nextChannel = self.mChannelListPIP[0]

			try :
				cacheChannel = CacheChannelPIP( channel, prevChannel.mNumber, nextChannel.mNumber )
				self.mChannelListHashPIP[channel.mNumber] = cacheChannel
				self.mPresentNumberHashPIP[channel.mPresentationNumber] = cacheChannel

				#cacheChannel.mChannel.printdebug( )
				#LOG_TRACE('prevKey=%d nextKey=%d' %( cacheChannel.mPrevKey, cacheChannel.mNextKey ) )

			except Exception, ex:
				LOG_ERR( "Exception %s" %ex)

			prevChannel = channel

		return self.mChannelListPIP


	def PIP_IsPIPAvailable( self, aNumber ) :
		return self.mCommander.PIP_IsPIPAvailable( aNumber )


	def PIP_GetPrevAvailable( self, aNumber ) :
		return self.mCommander.PIP_GetPrevAvailable( aNumber )


	def PIP_GetNextAvailable( self, aNumber ) :
		return self.mCommander.PIP_GetNextAvailable( aNumber )


	def PIP_EnableAudio( self, aEnable = True ) :
		return self.mCommander.PIP_EnableAudio( aEnable )


	def PIP_IsStarted( self ) :
		return self.mCommander.PIP_IsStarted( )


	def PIP_StopIfStarted( self ) :
		return self.mCommander.PIP_StopIfStarted( )


	def PIP_AVBlank( self, aBlank ) :
		return self.mCommander.PIP_AVBlank( aBlank )


	def PIP_GetAVBlank( self ) :
		return self.mCommander.PIP_GetAVBlank( )


	def PIP_SwapWindow( self, aSwap = None, aRegular = True ) :
		if aSwap == None :
			aSwap = not self.mPIPSwapStatus

		ret = self.mCommander.PIP_SwapWindow( aSwap )
		if ret and aRegular :
			self.mPIPSwapStatus = aSwap

		if ret and ( not self.GetMediaCenter( ) ) :
			self.PIP_EnableAudio( aSwap )

		return ret


	def PIP_GetSwapStatus( self ) :
		return self.mPIPSwapStatus


	def PIP_IsSwapped( self ) :
		return self.mCommander.PIP_IsSwapped( )


	def PIP_GetPrev( self, aChannel ) :
		if aChannel	== None or aChannel.mError != 0 :
			return None

		cacheChannel = self.mChannelListHashPIP.get( aChannel.mNumber, None )
		if cacheChannel == None :
			# retry find first channel
			if self.mChannelListPIP and len( self.mChannelListPIP ) > 0 :
				last = len( self.mChannelListPIP ) - 1
				return self.PIP_GetNext( self.mChannelListPIP[last], True )

			return None

		prevKey = cacheChannel.mPrevKey
		channel = self.mChannelListHashPIP.get( prevKey, None )
		if channel == None :
			return None
		#LOG_TRACE('------------ Prev Channel-------------------')
		#channel.printdebug( )
		return channel.mChannel


	def PIP_GetNext( self, aChannel, aLast = False ) :
		if aChannel	== None or aChannel.mError != 0 :
			return None

		cacheChannel = self.mChannelListHashPIP.get( aChannel.mNumber, None )
		if cacheChannel == None :
			# retry find end channel
			if self.mChannelListPIP and len( self.mChannelListPIP ) > 0 :
				cacheChannel = self.mChannelListHashPIP.get( self.mChannelListPIP[0].mNumber, None )
				if cacheChannel == None :
					return None

				channel = cacheChannel
				if aLast :
					prevKey = cacheChannel.mPrevKey
					channel = self.mChannelListHashPIP.get( prevKey, None )
					if channel == None :
						return None
				return channel.mChannel

			return None

		nextKey = cacheChannel.mNextKey
		channel = self.mChannelListHashPIP.get( nextKey, None )
		if channel == None :
			return None
		#LOG_TRACE('------------ Next Channel-------------------')
		#channel.printdebug( )
		return channel.mChannel


	def PIP_GetByNumber( self, aNumber, aUseDB = False, aAllChannel = False ) :
		favGroup = ''
		provider = ''
		currentMode = self.Zappingmode_GetCurrent( )
		if not aAllChannel :
			if currentMode.mMode == ElisEnum.E_MODE_FAVORITE :
				favGroup = currentMode.mFavoriteGroup.mGroupName
			#elif currentMode.mMode == ElisEnum.E_MODE_PROVIDER :
			#	provider = currentMode.mProviderInfo.mProviderName
			#	LOG_TRACE( '------------------------------provider pip[%s %s]'% ( provider, aNumber ) )

		if aUseDB :
			if SUPPORT_CHANNEL_DATABASE	== True :
				channelDB = ElisChannelDB( )
				channelDB.SetListUse( E_ENUM_OBJECT_INSTANCE )
				channel = channelDB.Channel_GetNumber( aNumber, favGroup, provider )
				channelDB.SetListUse( E_ENUM_OBJECT_REUSE_ZAPPING )
				channelDB.Close( )
				return channel

		else :
			cacheChannel = self.mChannelListHashPIP.get( aNumber, None )
			if cacheChannel == None :
				return None

			channel = cacheChannel.mChannel
			return channel


	def PIP_GetTunableListHash( self ) :
		hashPIP = self.mChannelListHashPIP
		currentMode = self.Zappingmode_GetCurrent( )
		if currentMode.mMode == ElisEnum.E_MODE_FAVORITE :
			hashPIP = self.mPresentNumberHashPIP

		return hashPIP


	def LoadPIPStatus( self ) :
		if CheckDirectory( E_VOLITILE_PIP_STATUS_PATH ) :
			try :
				fd = open( E_VOLITILE_PIP_STATUS_PATH, 'r' )
				lines = fd.readlines( )
				fd.close( )
				RemoveDirectory( E_VOLITILE_PIP_STATUS_PATH )
				#LOG_TRACE( '---------------pipStatus\n%s'% lines )

				isStart   = 'False'
				pipLock   = 'False'
				pipBlank  = 'False'
				pipSignal = 'True'

				for line in lines :
					value = ParseStringInPattern( '=', line )

					if not value or len( value ) < 2 :
						continue

					if not value[0] :
						continue

					LOG_TRACE( '%s=%s\n'% ( value[0], value[1] ) )
					if value[0] == 'PIPStart' :
						isStart = value[1]
					elif value[0] == 'PIPSignal' :
						pipSignal = value[1]
					elif value[0] == 'BlankPIP' :
						pipBlank = value[1]
					elif value[0] == 'PIPLock' :
						pipLock = value[1]

				#LOG_TRACE( '---------------pipStatus start[%s] blank[%s] signal[%s]'% ( isStart, pipBlank, pipSignal ) )
				if isStart == 'True' :
					import pvr.gui.DialogMgr as DiaMgr
					self.PIP_SetStatus( True )
					DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).PIP_SetPositionSync( )
					xbmcgui.Window( 10000 ).setProperty( 'iLockPIP', pipLock )
					xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', pipBlank )
					xbmcgui.Window( 10000 ).setProperty( 'PIPSignal', pipSignal )
					#LOG_TRACE( '-----------------------------setProperty blank[%s] signal[%s]'% ( pipBlank, pipSignal ) )

			except Exception, e :
				LOG_ERR( 'except[%s]'% e )


	def SavePIPStatus( self ) :
		isSave = True
		if self.PIP_GetStatus( ) :
			try :
				fd = open( E_VOLITILE_PIP_STATUS_PATH, 'w', 0644 )
				fd.writelines( 'PIPStart=True\n' )
				fd.writelines( 'BlankPIP=%s\n'% xbmcgui.Window( 10000 ).getProperty( 'BlankPIP' ) )
				fd.writelines( 'PIPSignal=%s\n'% xbmcgui.Window( 10000 ).getProperty( 'PIPSignal' ) )
				fd.writelines( 'PIPLock=%s\n'% xbmcgui.Window( 10000 ).getProperty( 'iLockPIP' ) )

				fd.close( )
			except Exception, e :
				LOG_ERR( 'except[%s]'% e )
				isSave = False

		return isSave


	def PIP_GetCurrentChannel( self ) :
		return self.mCurrentChannelPIP


	def PIP_SetCurrentChannel( self, aChannel = None ) :
		if aChannel :
			self.mCurrentChannelPIP = deepcopy( aChannel )


	def PIP_StopByDeleteChannel( self ) :
		#LOG_TRACE( 'PIP_StopByDeleteChannel status[%s]'% self.PIP_GetStatus( ) )

		#1. check pip start?
		if not self.PIP_GetStatus( ) :
			return

		#2. exist current pip?
		pChannel = self.PIP_GetCurrentChannel( )
		if not pChannel :
			return
		#LOG_TRACE( 'PIP_StopByDeleteChannel status[%s] pChannel[%s %s] lock[%s]'% ( self.PIP_GetStatus( ),pChannel.mNumber,pChannel.mName,pChannel.mLocked ) )

		#3. edited pipCurrent?(move,skipped,delete), find change channel
		#   buyer issue 62 : show stay last channel on pip if tunable check, when changed mode
		fChannel = None
		reTunePIP = False
		channelList = self.Channel_GetListByIDs( ElisEnum.E_SERVICE_TYPE_TV, pChannel.mTsid, pChannel.mOnid, pChannel.mSid )
		if channelList and len( channelList ) > 0 :
			for iChannel in channelList :
				#iChannel.printdebug( )
				#LOG_TRACE( '--------------------Channel_GetListByIDs[%s %s]'% ( iChannel.mNumber, iChannel.mName ) )
				if iChannel.mCarrier.mDVBS.mSatelliteLongitude == pChannel.mCarrier.mDVBS.mSatelliteLongitude and \
				   iChannel.mCarrier.mDVBS.mFrequency == pChannel.mCarrier.mDVBS.mFrequency and \
				   iChannel.mCarrier.mDVBS.mSymbolRate == pChannel.mCarrier.mDVBS.mSymbolRate and \
				   iChannel.mCarrier.mDVBS.mSatelliteBand == pChannel.mCarrier.mDVBS.mSatelliteBand and \
				   iChannel.mCarrier.mDVBS.mPolarization == pChannel.mCarrier.mDVBS.mPolarization :
					LOG_TRACE( '[PIP] changed Number : pChannel[%s %s] --> iChannel[%s %s]'% ( pChannel.mNumber, pChannel.mName, iChannel.mNumber, iChannel.mName ) )
					fChannel = iChannel
					break

		if not fChannel or fChannel.mSkipped :
			reTunePIP = True
			fChannel = self.Channel_GetCurrent( )
			#DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).PIP_Check( E_PIP_STOP )
			LOG_TRACE( 'deleted channel, reTune current pip' )

		else :
			if not fChannel.mLocked :
				reTunePIP = True
				LOG_TRACE( 'edit channel, reTune pip' )

		if reTunePIP :
			import pvr.gui.DialogMgr as DiaMgr
			DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).TuneChannelByExternal( fChannel )


	def Splash_StartAndStop( self, aStartStop ) :
		return self.mCommander.Splash_StartAndStop( aStartStop )


	def SyncLanguagePropFromXBMC( self, aLangauge ) :
		currentLanguageProp = ElisPropertyEnum( 'Language', self.mCommander ).GetProp( )
		if GetXBMCLanguageToPropLanguage( aLangauge ) != currentLanguageProp or GetXBMCLanguageToPropLanguage( aLangauge ) == ElisEnum.E_ENGLISH :
			import pvr.gui.WindowMgr as WinMgr
			self.SetChannelReloadStatus( True )
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_SIMPLE_CHANNEL_LIST ).ResetControls( )
			prop = GetXBMCLanguageToPropLanguage( aLangauge )
			ElisPropertyEnum( 'Language', self.mCommander ).SetProp( prop )
			prop = GetXBMCLanguageToPropAudioLanguage( aLangauge )
			ElisPropertyEnum( 'Audio Language', self.mCommander ).SetProp( prop )
			xbmcgui.Window( 10000 ).setProperty( 'PIPLoadFinished', E_TAG_FALSE )


	def SaveResolution( self, aEvent ) :
		res = ''
		if aEvent.mVideoHeight <= 576 :
			res = '576'
		elif aEvent.mVideoHeight <= 720 :
			res = '720'
		else :
			res = '1080'

		if aEvent.mVideoInterlaced == 0 :
			res += 'p'
		else :
			res += 'i'

		self.mSavedResolution = res


	def GetResolution( self, aInit = False ) :
		if aInit :
			res = self.mCommander.VideoIdentified_GetStatus( )
			if res :
				return res.mParam
			else :
				return ''
		else :
			return self.mSavedResolution


	def SharedChannel_GetListItems( self ) :
		return self.mListItems


	def SharedChannel_AddWindow( self, aWindowId ) :
			self.mChannelWindows[aWindowId] = True

			
	def SharedChannel_SetUpdated( self, aWindowId, aEnable ) :
		LOG_TRACE( 'aWindowId=%s aEnable=%s' %(aWindowId, aEnable )  )
		if aWindowId ==  0 :
			for key in self.mChannelWindows :
				LOG_TRACE( 'key=%s aEnable=%s' %(key, aEnable )  )			
				self.mChannelWindows[key] = aEnable
		else :
			if self.mChannelWindows.get( aWindowId, -1 ) >= 0 :
				self.mChannelWindows[aWindowId] = aEnable
			else :
				LOG_ERR( 'Can not find WindowId=%s'  %aWindowId )


	def SharedChannel_GetUpdated( self, aWindowId ) :
		ret = self.mChannelWindows.get( aWindowId, 0 )
		LOG_TRACE( 'RET=%s' %ret )
		return ret


	def SetHbbTVEnable( self, aEnable ) :
		LOG_TRACE( 'SetHbbTVEnable=%s' %aEnable )
		self.mHbbTVEnable = aEnable


	def GetHbbTVEnable( self ) :
		LOG_TRACE( 'GetHbbTVEnable=%s' %self.mHbbTVEnable )
		return self.mHbbTVEnable


	def SetHbbtvStatus( self ) :
		if xbmcaddon.Addon( 'script.mbox' ).getSetting( 'HBB_TV' ) == 'true' :
			self.mHbbtvStatus = True
		else :
			self.mHbbtvStatus = False


	def GetHbbtvStatus( self ) :
		return self.mHbbtvStatus

