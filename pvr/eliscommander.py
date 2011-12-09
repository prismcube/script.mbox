
from pvr.util import run_async
from pvr.net.net import EventCommander
from pvr.elisaction import ElisAction
from pvr.elisenum import ElisEnum

import pvr.net.netconfig as netconfig

class ElisCommander( EventCommander ): 
	"""  
	ElisCommand Interface Class
	@package ElisCommander
	This Class describes all functions between m/w and Python UI.
	All functions of this class have it's equavalent functions in M/W on C++
	@author doliyu@marusys.com, jhshin@marusys.com
	@date	02.12.2011
	@file ElisCommander.py
	"""

	def setElisReady(self ,  aPeerAddress) :
		"""
		Socket connect
		@param    aPeerAddress  String  M/W IP addrss
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.setElisReady )
		req.append(aPeerAddress)

		reply= self.command(req)
		return reply

	def zappingmode_GetCurrent(self ) :
		"""
		Get Current ZappingMode
		@return    IZappingMode  Struct  Zapping Mode
			\n[\n
			Integer mMode,		//Zapping Mode : E_MODE_ALL, E_MODE_FAVORITE, E_MODE_NETWORK, E_MODE_SATELLITE, E_MODE_CAS\n
			Integer mSortingMode,		//Sorting Mode :E_SORT_BY_DEFAULT, E_SORT_BY_ALPHABET, E_SORT_BY_CARRIER, E_SORT_BY_NUMBER, E_SORT_BY_HD\n
			Integer mServiceType,		//Service Type :E_SERVICE_TYPE_INVALID, E_SERVICE_TYPE_TV, E_SERVICE_TYPE_RADIO, E_SERVICE_TYPE_DATA\n
			]\n
		
		"""
		req = []
		req.append( ElisAction.zappingmode_GetCurrent )

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def zappingmode_SetCurrent(self ,  mode,  sortingMode,  serviceType) :
		"""
		Set Current ZappingMode
		@param    mode  Integer  Zapping Mode : E_MODE_ALL, E_MODE_FAVORITE, E_MODE_NETWORK, E_MODE_SATELLITE, E_MODE_CAS
		@param    sortingMode  Integer  Sorting Mode :E_SORT_BY_DEFAULT, E_SORT_BY_ALPHABET, E_SORT_BY_CARRIER, E_SORT_BY_NUMBER, E_SORT_BY_HD
		@param    serviceType  Integer  Service Type :E_SERVICE_TYPE_INVALID, E_SERVICE_TYPE_TV, E_SERVICE_TYPE_RADIO, E_SERVICE_TYPE_DATA
		@return      Bool   TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.zappingmode_SetCurrent )
		req.append('%d' %mode)
		req.append('%d' %sortingMode)
		req.append('%d' %serviceType)

		reply= self.command(req)
		return reply

	def channel_Get(self ,  channelNumber,  serviceType) :
		"""
		Get Current by number
		@param    channelNumber  Integer  Channel Number 
		@param    serviceType  Integer  Service Type :E_SERVICE_TYPE_INVALID, E_SERVICE_TYPE_TV, E_SERVICE_TYPE_RADIO, E_SERVICE_TYPE_DATA
		@return    IChannel  Struct  Channel Information
			\n[\n
			Integer mNumber,		//Channel Number\n
			Integer mPresentationNumber,		//Channel presentation number\n
			String mName,		//Channel Name\n
			Integer mServiceType,		//Service Type\n
			Integer mLocked,		//Lock Status : LOCKED or UNLOCKED\n
			Integer mIsCA,		//CAS Status : CA or notCA\n
			Integer mIsHD,		//HD status\n
			Integer mNid,		//Network ID\n
			Integer mSid,		//Service ID\n
			Integer mTsid,		//Transport Stream ID\n
			Integer mOnid,		//Original Network ID\n
			Integer mCarrierType,		//Carrier Type : DVBS, DVBT, DVBC\n
			Integer mSkipped,		//Channel Skip Status : Skip or Not Skip\n
			Integer mIsBlank,		//mIsBlank\n
			]\n
		
		@see   IChannel
		"""
		req = []
		req.append( ElisAction.channel_Get )
		req.append('%d' %channelNumber)
		req.append('%d' %serviceType)

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def channel_GetByTwolDs(self ,  Sid,  Onid) :
		"""
		Get Current by Sid and Onid
		@param    Sid  Integer  Service ID
		@param    Onid  Integer  Original Network ID
		@return    IChannel  Struct  Channel Information
			\n[\n
			Integer mNumber,		//Channel Number\n
			Integer mPresentationNumber,		//Channel presentation number\n
			String mName,		//Channel Name\n
			Integer mServiceType,		//Service Type\n
			Integer mLocked,		//Lock Status : LOCKED or UNLOCKED\n
			Integer mIsCA,		//CAS Status : CA or notCA\n
			Integer mIsHD,		//HD status\n
			Integer mNid,		//Network ID\n
			Integer mSid,		//Service ID\n
			Integer mTsid,		//Transport Stream ID\n
			Integer mOnid,		//Original Network ID\n
			Integer mCarrierType,		//Carrier Type : DVBS, DVBT, DVBC\n
			Integer mSkipped,		//Channel Skip Status : Skip or Not Skip\n
			Integer mIsBlank,		//mIsBlank\n
			]\n
		
		@see   IChannel
		"""
		req = []
		req.append( ElisAction.channel_GetByTwolDs )
		req.append('%d' %Sid)
		req.append('%d' %Onid)

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def channel_GetByFourIDs(self ,  channelNumber,  Sid,  Onid,  TSid) :
		"""
		Get Current by Sid ,Onid, TSid, Channel Number
		@param    channelNumber  Integer  Channel Number
		@param    Sid  Integer  Service ID
		@param    Onid  Integer  Original Network ID
		@param    TSid  Integer  Transport Stream ID
		@return    IChannel  Struct  Channel Information
			\n[\n
			Integer mNumber,		//Channel Number\n
			Integer mPresentationNumber,		//Channel presentation number\n
			String mName,		//Channel Name\n
			Integer mServiceType,		//Service Type\n
			Integer mLocked,		//Lock Status : LOCKED or UNLOCKED\n
			Integer mIsCA,		//CAS Status : CA or notCA\n
			Integer mIsHD,		//HD status\n
			Integer mNid,		//Network ID\n
			Integer mSid,		//Service ID\n
			Integer mTsid,		//Transport Stream ID\n
			Integer mOnid,		//Original Network ID\n
			Integer mCarrierType,		//Carrier Type : DVBS, DVBT, DVBC\n
			Integer mSkipped,		//Channel Skip Status : Skip or Not Skip\n
			Integer mIsBlank,		//mIsBlank\n
			]\n
		
		@see   IChannel
		"""
		req = []
		req.append( ElisAction.channel_GetByFourIDs )
		req.append('%d' %channelNumber)
		req.append('%d' %Sid)
		req.append('%d' %Onid)
		req.append('%d' %TSid)

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def channel_SetCurrent(self ,  channelNumber,  serviceType) :
		"""
		Set Current Channel
		@param    channelNumber  Integer  Channel Number of Current Channel
		@param    serviceType  Integer  Service Type :E_SERVICE_TYPE_INVALID, E_SERVICE_TYPE_TV, E_SERVICE_TYPE_RADIO, E_SERVICE_TYPE_DATA
		@return      Bool  TRUE or FALSE
		@see   IChannel
		"""
		req = []
		req.append( ElisAction.channel_SetCurrent )
		req.append('%d' %channelNumber)
		req.append('%d' %serviceType)

		reply= self.command(req)
		return reply

	def channel_GetCurrent(self ) :
		"""
		Get Current Channel
		@return    IChannel  Struct  Channel Information
			\n[\n
			Integer mNumber,		//Channel Number\n
			Integer mPresentationNumber,		//Channel presentation number\n
			String mName,		//Channel Name\n
			Integer mServiceType,		//Service Type\n
			Integer mLocked,		//Lock Status : LOCKED or UNLOCKED\n
			Integer mIsCA,		//CAS Status : CA or notCA\n
			Integer mIsHD,		//HD status\n
			Integer mNid,		//Network ID\n
			Integer mSid,		//Service ID\n
			Integer mTsid,		//Transport Stream ID\n
			Integer mOnid,		//Original Network ID\n
			Integer mCarrierType,		//Carrier Type : DVBS, DVBT, DVBC\n
			Integer mSkipped,		//Channel Skip Status : Skip or Not Skip\n
			Integer mIsBlank,		//mIsBlank\n
			]\n
		
		@see   IChannel
		"""
		req = []
		req.append( ElisAction.channel_GetCurrent )

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def channel_GetPrev(self ) :
		"""
		Get Prev Channel
		@return    IChannel  Struct  Channel Information
			\n[\n
			Integer mNumber,		//Channel Number\n
			Integer mPresentationNumber,		//Channel presentation number\n
			String mName,		//Channel Name\n
			Integer mServiceType,		//Service Type\n
			Integer mLocked,		//Lock Status : LOCKED or UNLOCKED\n
			Integer mIsCA,		//CAS Status : CA or notCA\n
			Integer mIsHD,		//HD status\n
			Integer mNid,		//Network ID\n
			Integer mSid,		//Service ID\n
			Integer mTsid,		//Transport Stream ID\n
			Integer mOnid,		//Original Network ID\n
			Integer mCarrierType,		//Carrier Type : DVBS, DVBT, DVBC\n
			Integer mSkipped,		//Channel Skip Status : Skip or Not Skip\n
			Integer mIsBlank,		//mIsBlank\n
			]\n
		
		@see   IChannel
		"""
		req = []
		req.append( ElisAction.channel_GetPrev )

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def channel_GetNext(self ) :
		"""
		Get Next Channel
		@return    IChannel  Struct  Channel Information
			\n[\n
			Integer mNumber,		//Channel Number\n
			Integer mPresentationNumber,		//Channel presentation number\n
			String mName,		//Channel Name\n
			Integer mServiceType,		//Service Type\n
			Integer mLocked,		//Lock Status : LOCKED or UNLOCKED\n
			Integer mIsCA,		//CAS Status : CA or notCA\n
			Integer mIsHD,		//HD status\n
			Integer mNid,		//Network ID\n
			Integer mSid,		//Service ID\n
			Integer mTsid,		//Transport Stream ID\n
			Integer mOnid,		//Original Network ID\n
			Integer mCarrierType,		//Carrier Type : DVBS, DVBT, DVBC\n
			Integer mSkipped,		//Channel Skip Status : Skip or Not Skip\n
			Integer mIsBlank,		//mIsBlank\n
			]\n
		
		@see   IChannel
		"""
		req = []
		req.append( ElisAction.channel_GetNext )

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def channel_GetList(self ,  serviceType,  zappingMode,  sortingMode) :
		"""
		Get Channel List for All
		@param    serviceType  Integer  Service Type :E_SERVICE_TYPE_INVALID, E_SERVICE_TYPE_TV, E_SERVICE_TYPE_RADIO, E_SERVICE_TYPE_DATA
		@param    zappingMode  Integer  Zapping Mode : E_MODE_ALL, E_MODE_FAVORITE, E_MODE_NETWORK, E_MODE_SATELLITE, E_MODE_CAS
		@param    sortingMode  Integer  Sorting Mode :E_SORT_BY_DEFAULT, E_SORT_BY_ALPHABET, E_SORT_BY_CARRIER, E_SORT_BY_NUMBER, E_SORT_BY_HD
		@return    IChannel  Struct  Channel Information
			\n[\n[\n
			Integer mNumber,		//Channel Number\n
			Integer mPresentationNumber,		//Channel presentation number\n
			String mName,		//Channel Name\n
			Integer mServiceType,		//Service Type\n
			Integer mLocked,		//Lock Status : LOCKED or UNLOCKED\n
			Integer mIsCA,		//CAS Status : CA or notCA\n
			Integer mIsHD,		//HD status\n
			Integer mNid,		//Network ID\n
			Integer mSid,		//Service ID\n
			Integer mTsid,		//Transport Stream ID\n
			Integer mOnid,		//Original Network ID\n
			Integer mCarrierType,		//Carrier Type : DVBS, DVBT, DVBC\n
			Integer mSkipped,		//Channel Skip Status : Skip or Not Skip\n
			Integer mIsBlank,		//mIsBlank\n
			]\n]\n
		
		@see   IChannel
		"""
		req = []
		req.append( ElisAction.channel_GetList )
		req.append('%d' %serviceType)
		req.append('%d' %zappingMode)
		req.append('%d' %sortingMode)

		self.send( req )
		retValue = []
		while 1:
			reply=self.read()
			if reply[len(reply)-1].upper() == 'LASTMESSAGE':
				reply.remove('LASTMESSAGE')
				retValue.append( reply )
				return retValue
			retValue.append( reply )
		

	def channel_GetListBySatellite(self ,  serviceType,  zappingMode,  sortingMode,  longitude,  band) :
		"""
		Get Channel List by Satellite
		@param    serviceType  Integer  Service Type :E_SERVICE_TYPE_INVALID, E_SERVICE_TYPE_TV, E_SERVICE_TYPE_RADIO, E_SERVICE_TYPE_DATA
		@param    zappingMode  Integer  Zapping Mode : E_MODE_ALL, E_MODE_FAVORITE, E_MODE_NETWORK, E_MODE_SATELLITE, E_MODE_CAS
		@param    sortingMode  Integer  Sorting Mode :E_SORT_BY_DEFAULT, E_SORT_BY_ALPHABET, E_SORT_BY_CARRIER, E_SORT_BY_NUMBER, E_SORT_BY_HD
		@param    longitude  Integer  Satellite Longitude
		@param    band  Integer  Band :Satellite Band E_BAND_UNDEFINED, E_BAND_KU, E_BAND_C
		@return    IChannel  Struct  Channel Information
			\n[\n[\n
			Integer mNumber,		//Channel Number\n
			Integer mPresentationNumber,		//Channel presentation number\n
			String mName,		//Channel Name\n
			Integer mServiceType,		//Service Type\n
			Integer mLocked,		//Lock Status : LOCKED or UNLOCKED\n
			Integer mIsCA,		//CAS Status : CA or notCA\n
			Integer mIsHD,		//HD status\n
			Integer mNid,		//Network ID\n
			Integer mSid,		//Service ID\n
			Integer mTsid,		//Transport Stream ID\n
			Integer mOnid,		//Original Network ID\n
			Integer mCarrierType,		//Carrier Type : DVBS, DVBT, DVBC\n
			Integer mSkipped,		//Channel Skip Status : Skip or Not Skip\n
			Integer mIsBlank,		//mIsBlank\n
			]\n]\n
		
		@see   IChannel
		"""
		req = []
		req.append( ElisAction.channel_GetListBySatellite )
		req.append('%d' %serviceType)
		req.append('%d' %zappingMode)
		req.append('%d' %sortingMode)
		req.append('%d' %longitude)
		req.append('%d' %band)

		
		self.send( req )
		retValue = []
		while 1:
			reply=self.read()
			if reply[len(reply)-1].upper() == 'LASTMESSAGE':
				reply.remove('LASTMESSAGE')
				retValue.append( reply )
				return retValue
			retValue.append( reply )
		

	def channel_GetListByFavorite(self ,  serviceType,  zappingMode,  sortingMode,  favoriteName) :
		"""
		Get Channel List by Favorite
		@param    serviceType  Integer  Service Type :E_SERVICE_TYPE_INVALID, E_SERVICE_TYPE_TV, E_SERVICE_TYPE_RADIO, E_SERVICE_TYPE_DATA
		@param    zappingMode  Integer  Zapping Mode : E_MODE_ALL, E_MODE_FAVORITE, E_MODE_NETWORK, E_MODE_SATELLITE, E_MODE_CAS
		@param    sortingMode  Integer  Sorting Mode :E_SORT_BY_DEFAULT, E_SORT_BY_ALPHABET, E_SORT_BY_CARRIER, E_SORT_BY_NUMBER, E_SORT_BY_HD
		@param    favoriteName  String  Favorite Name
		@return    IChannel  Struct  Channel Information
			\n[\n[\n
			Integer mNumber,		//Channel Number\n
			Integer mPresentationNumber,		//Channel presentation number\n
			String mName,		//Channel Name\n
			Integer mServiceType,		//Service Type\n
			Integer mLocked,		//Lock Status : LOCKED or UNLOCKED\n
			Integer mIsCA,		//CAS Status : CA or notCA\n
			Integer mIsHD,		//HD status\n
			Integer mNid,		//Network ID\n
			Integer mSid,		//Service ID\n
			Integer mTsid,		//Transport Stream ID\n
			Integer mOnid,		//Original Network ID\n
			Integer mCarrierType,		//Carrier Type : DVBS, DVBT, DVBC\n
			Integer mSkipped,		//Channel Skip Status : Skip or Not Skip\n
			Integer mIsBlank,		//mIsBlank\n
			]\n]\n
		
		@see   IChannel
		"""
		req = []
		req.append( ElisAction.channel_GetListByFavorite )
		req.append('%d' %serviceType)
		req.append('%d' %zappingMode)
		req.append('%d' %sortingMode)
		req.append(favoriteName)

		
		self.send( req )
		retValue = []
		while 1:
			reply=self.read()
			if reply[len(reply)-1].upper() == 'LASTMESSAGE':
				reply.remove('LASTMESSAGE')
				retValue.append( reply )
				return retValue
			retValue.append( reply )
		

	def channel_GetListByFTACas(self ,  serviceType,  zappingMode,  sortingMode,  CAId) :
		"""
		Get Channel List by FTA_CA
		@param    serviceType  Integer  Service Type :E_SERVICE_TYPE_INVALID, E_SERVICE_TYPE_TV, E_SERVICE_TYPE_RADIO, E_SERVICE_TYPE_DATA
		@param    zappingMode  Integer  Zapping Mode : E_MODE_ALL, E_MODE_FAVORITE, E_MODE_NETWORK, E_MODE_SATELLITE, E_MODE_CAS
		@param    sortingMode  Integer  Sorting Mode :E_SORT_BY_DEFAULT, E_SORT_BY_ALPHABET, E_SORT_BY_CARRIER, E_SORT_BY_NUMBER, E_SORT_BY_HD
		@param    CAId  Integer  CAId : E_FTA_CHANNEL, E_MEDIAGUARD, E_VIACCESS, E_NAGRA, E_IRDETO, E_CONAX, E_CRYPTOWORKS, E_NDS, E_BETADIGITAL,  E_OTHERS
		@return    IChannel  Struct  Channel Information
			\n[\n[\n
			Integer mNumber,		//Channel Number\n
			Integer mPresentationNumber,		//Channel presentation number\n
			String mName,		//Channel Name\n
			Integer mServiceType,		//Service Type\n
			Integer mLocked,		//Lock Status : LOCKED or UNLOCKED\n
			Integer mIsCA,		//CAS Status : CA or notCA\n
			Integer mIsHD,		//HD status\n
			Integer mNid,		//Network ID\n
			Integer mSid,		//Service ID\n
			Integer mTsid,		//Transport Stream ID\n
			Integer mOnid,		//Original Network ID\n
			Integer mCarrierType,		//Carrier Type : DVBS, DVBT, DVBC\n
			Integer mSkipped,		//Channel Skip Status : Skip or Not Skip\n
			Integer mIsBlank,		//mIsBlank\n
			]\n]\n
		
		@see   IChannel
		"""
		req = []
		req.append( ElisAction.channel_GetListByFTACas )
		req.append('%d' %serviceType)
		req.append('%d' %zappingMode)
		req.append('%d' %sortingMode)
		req.append('%d' %CAId)

		
		self.send( req )
		retValue = []
		while 1:
			reply=self.read()
			if reply[len(reply)-1].upper() == 'LASTMESSAGE':
				reply.remove('LASTMESSAGE')
				retValue.append( reply )
				return retValue
			retValue.append( reply )
		

	def channel_GetFavoriteList(self ,  serviceType) :
		"""
		Get Favorit List
		@param    serviceType  Integer  Service Type :E_SERVICE_TYPE_INVALID, E_SERVICE_TYPE_TV, E_SERVICE_TYPE_RADIO, E_SERVICE_TYPE_DATA
		@return    IFavoriteGroup  Struct  Favoirte Group Information
			\n[\n[\n
			String mGroupName,		//Favorite Group Name\n
			Integer mServiceType,		//Service Type\n
			Integer mFavoriteChannelCount,		//Total Count for Favorite\n
			]\n]\n
		
		@see   IFavoriteGroup
		"""
		req = []
		req.append( ElisAction.channel_GetFavoriteList )
		req.append('%d' %serviceType)

		
		self.send( req )
		retValue = []
		while 1:
			reply=self.read()
			if reply[len(reply)-1].upper() == 'LASTMESSAGE':
				reply.remove('LASTMESSAGE')
				retValue.append( reply )
				return retValue
			retValue.append( reply )
		

	def channel_GetFTACasList(self ,  serviceType) :
		"""
		Get FTA_CAS List
		@param    serviceType  Integer  Service Type :E_SERVICE_TYPE_INVALID, E_SERVICE_TYPE_TV, E_SERVICE_TYPE_RADIO, E_SERVICE_TYPE_DATA
		@return    IChannelCASInfo  Struct  CAS Information
			\n[\n[\n
			String mName,		//CAS Name\n
			Integer mChannelCount,		//\n
			Integer mCAId,		//CAId : E_FTA_CHANNEL, E_MEDIAGUARD, E_VIACCESS, E_NAGRA, E_IRDETO, E_CONAX, E_CRYPTOWORKS, E_NDS, E_BETADIGITAL,  E_OTHERS\n
			]\n]\n
		
		@see   IChannelCASInfo
		"""
		req = []
		req.append( ElisAction.channel_GetFTACasList )
		req.append('%d' %serviceType)

		
		self.send( req )
		retValue = []
		while 1:
			reply=self.read()
			if reply[len(reply)-1].upper() == 'LASTMESSAGE':
				reply.remove('LASTMESSAGE')
				retValue.append( reply )
				return retValue
			retValue.append( reply )
		

	def channel_GetCarrierForDVBS(self ) :
		"""
		Get Carrier of Current Channel  for DVBS
		@return    IDVBSCarrier  Struct  Zapping Mode
			\n[\n
			Integer mSatelliteLongitude,		//Longitude : Satellite Longitude\n
			Integer mSatelliteBand,		//Band:Satellite Band E_BAND_UNDEFINED, E_BAND_KU, E_BAND_C\n
			Integer mFrequency,		//Current Chanenl Frequency [MHz] \n
			Integer mSymbolRate,		//Current Channel SymbolRate [ KHz ]\n
			Integer mFECValue,		//Current Channel FEC Mode : \n
			Integer mPolarization,		//Current Channel Polarization : E_LNB_HORIZONTAL, E_LNB_VERTICAL, E_LNB_LEFT, E_LNB_RIGHT\n
			]\n
		
		@see   IDVBSCarrier
		"""
		req = []
		req.append( ElisAction.channel_GetCarrierForDVBS )

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def channel_GetCarrierForDVBT(self ) :
		"""
		Get Carrier of Current Channel  for DVBT
		@return    IDVBTCarrier  Struct  Zapping Mode
			\n[\n
			Integer mFrequency,		//Current Chanenl Frequency [MHz] \n
			Integer mBand,		//Band:Satellite Band E_BAND_UNDEFINED, E_BAND_KU, E_BAND_C\n
			]\n
		
		@see   IDVBTCarrier
		"""
		req = []
		req.append( ElisAction.channel_GetCarrierForDVBT )

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def channel_GetCarrierForDVBC(self ) :
		"""
		Get Carrier of Current Channel  for DVBC
		@return    IDVBCCarrier  Struct  Zapping Mode
			\n[\n
			Integer mFrequency,		//Current Chanenl Frequency [MHz] \n
			Integer mSymbolRate,		//Current Channel SymbolRate [ KHz ]\n
			Integer mQAM,		//QAM: 64, 128,256\n
			]\n
		
		@see   IDVBCCarrier
		"""
		req = []
		req.append( ElisAction.channel_GetCarrierForDVBC )

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def channel_Skip(self ,  aSet,  IChannel) :
		"""
		Channel Skip Set/Reset
		@param    aSet  Integer  Skip Value : 1 or 0
		@param    IChannel  Struct  Favorite Name
		@return      Bool  TRUE or FALSE
		@see   IChannel
		"""
		req = []
		req.append( ElisAction.channel_Skip )
		req.append('%d' %aSet)
		for ele in IChannel:
			req.append('%d' %mNumber)
			req.append('%d' %mServiceType)

		reply= self.command(req)
		return reply

	def channel_Lock(self ,  aLock,  IChannel) :
		"""
		Channel Lock Set/Reset
		@param    aLock  Integer  Lock Value : 1 or 0
		@param    IChannel  Struct  Favorite Name
		@return      Bool  TRUE or FALSE
		@see   IChannel
		"""
		req = []
		req.append( ElisAction.channel_Lock )
		req.append('%d' %aLock)
		for ele in IChannel:
			req.append('%d' %mNumber)
			req.append('%d' %mServiceType)

		reply= self.command(req)
		return reply

	def channel_Delete(self ,  IChannel) :
		"""
		Channel Delete
		@param    IChannel  Struct  Favorite Name
		@return      Bool  TRUE or FALSE
		@see   IChannel
		"""
		req = []
		req.append( ElisAction.channel_Delete )
		for ele in IChannel:
			req.append('%d' %mNumber)
			req.append('%d' %mServiceType)

		reply= self.command(req)
		return reply

	def channel_Save(self ) :
		"""
		Channel Save
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.channel_Save )

		reply= self.command(req)
		return reply

	def channel_Backup(self ) :
		"""
		Channel Backup
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.channel_Backup )

		reply= self.command(req)
		return reply

	def channel_DeleteAll(self ) :
		"""
		Channel Delete All
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.channel_DeleteAll )

		reply= self.command(req)
		return reply

	def channel_Restore(self ,  aRestore) :
		"""
		Channel Restore
		@param    aRestore  Integer  Restore Value : 1 or 0
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.channel_Restore )
		req.append('%d' %aRestore)

		reply= self.command(req)
		return reply

	def favoritegroup_GetGroupCount(self ,  serviceType) :
		"""
		Get Group Count of FavoriteGroup
		@param    serviceType  Integer  Service Type :E_SERVICE_TYPE_INVALID, E_SERVICE_TYPE_TV, E_SERVICE_TYPE_RADIO, E_SERVICE_TYPE_DATA
		@return      Integer  Total Group Count of FavoriteGroup
		"""
		req = []
		req.append( ElisAction.favoritegroup_GetGroupCount )
		req.append('%d' %serviceType)

		reply= self.command(req)
		return reply

	def favoritegroup_Create(self ,  groupName,  serviceType) :
		"""
		FavoriteGroup Create
		@param    groupName  String  FavoirteGroup Name
		@param    serviceType  Integer  Service Type :E_SERVICE_TYPE_INVALID, E_SERVICE_TYPE_TV, E_SERVICE_TYPE_RADIO, E_SERVICE_TYPE_DATA
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.favoritegroup_Create )
		req.append(groupName)
		req.append('%d' %serviceType)

		reply= self.command(req)
		return reply

	def favoritegroup_GetByIndex(self ,  index,  serviceType) :
		"""
		Get FavoriteGroup by Favorite index 
		@param    index  Integer  FavoriteGroup index
		@param    serviceType  Integer  Service Type :E_SERVICE_TYPE_INVALID, E_SERVICE_TYPE_TV, E_SERVICE_TYPE_RADIO, E_SERVICE_TYPE_DATA
		@return    IFavoriteGroup  Struct  Favoirte Group Information
			\n[\n
			String mGroupName,		//Favorite Group Name\n
			Integer mServiceType,		//Service Type\n
			Integer mFavoriteChannelCount,		//Total Count for Favorite\n
			]\n
		
		@see   IFavoriteGroup
		"""
		req = []
		req.append( ElisAction.favoritegroup_GetByIndex )
		req.append('%d' %index)
		req.append('%d' %serviceType)

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def favoritegroup_GetByGroupName(self ,  groupName,  serviceType) :
		"""
		Get FavoriteGroup by Favorite Name 
		@param    groupName  String  FavoirteGroup Name
		@param    serviceType  Integer  Service Type :E_SERVICE_TYPE_INVALID, E_SERVICE_TYPE_TV, E_SERVICE_TYPE_RADIO, E_SERVICE_TYPE_DATA
		@return    IFavoriteGroup  Struct  Favoirte Group Information
			\n[\n
			String mGroupName,		//Favorite Group Name\n
			Integer mServiceType,		//Service Type\n
			Integer mFavoriteChannelCount,		//Total Count for Favorite\n
			]\n
		
		@see   IFavoriteGroup
		"""
		req = []
		req.append( ElisAction.favoritegroup_GetByGroupName )
		req.append(groupName)
		req.append('%d' %serviceType)

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def favoritegroup_Remove(self ,  groupName,  serviceType) :
		"""
		FavoirteGroup Remove
		@param    groupName  String  FavoirteGroup Name
		@param    serviceType  Integer  Service Type :E_SERVICE_TYPE_INVALID, E_SERVICE_TYPE_TV, E_SERVICE_TYPE_RADIO, E_SERVICE_TYPE_DATA
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.favoritegroup_Remove )
		req.append(groupName)
		req.append('%d' %serviceType)

		reply= self.command(req)
		return reply

	def favoritegroup_ChangeName(self ,  groupName,  serviceType,  groupNewName) :
		"""
		FavoirteGroup Change Name
		@param    groupName  String  FavoirteGroup Name
		@param    serviceType  Integer  Service Type :E_SERVICE_TYPE_INVALID, E_SERVICE_TYPE_TV, E_SERVICE_TYPE_RADIO, E_SERVICE_TYPE_DATA
		@param    groupNewName  String  FavoirteGroup New Name
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.favoritegroup_ChangeName )
		req.append(groupName)
		req.append('%d' %serviceType)
		req.append(groupNewName)

		reply= self.command(req)
		return reply

	def favoritegroup_AddChannel(self ,  groupName,  channelNumber,  serviceType) :
		"""
		Favorite Group Add Channel
		@param    groupName  String  FavoirteGroup Name
		@param    channelNumber  Integer  Channel Number 
		@param    serviceType  Integer  Service Type :E_SERVICE_TYPE_INVALID, E_SERVICE_TYPE_TV, E_SERVICE_TYPE_RADIO, E_SERVICE_TYPE_DATA
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.favoritegroup_AddChannel )
		req.append(groupName)
		req.append('%d' %channelNumber)
		req.append('%d' %serviceType)

		reply= self.command(req)
		return reply

	def favoritegroup_RemoveChannel(self ,  groupName,  channelNumber,  serviceType) :
		"""
		Favorite Group Remove Channel
		@param    groupName  String  FavoirteGroup Name
		@param    channelNumber  Integer  Channel Number 
		@param    serviceType  Integer  Service Type :E_SERVICE_TYPE_INVALID, E_SERVICE_TYPE_TV, E_SERVICE_TYPE_RADIO, E_SERVICE_TYPE_DATA
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.favoritegroup_RemoveChannel )
		req.append(groupName)
		req.append('%d' %channelNumber)
		req.append('%d' %serviceType)

		reply= self.command(req)
		return reply

	def epgevent_GetPresent(self ) :
		"""
		Get EPG of Present
		@return    IEPGEvent  Struct  Elis EPG Event
			\n[\n
			Integer mEventId,		//EPG Event ID \n
			String mEventName,		//EPG Event NAme\n
			Integer mSid,		//Service ID\n
			Integer mTsid,		//Transport Stream ID\n
			Integer mOnid,		//Original Network ID\n
			Integer mStartTime,		//EPG Event Start Time (ms)\n
			Integer mDuration,		//EPG Event Duration Time (ms) \n
			Integer mContentTag,		//EPG Event Content Tag\n
			Integer mHasHDVideo,		//HD Video : 1 or 0\n
			Integer mHas16_9Video,		//16:9 video : 1 or 0\n
			Integer mHasStereoAudio,		//Stereo Audio : 1 or 0 \n
			Integer mHasMultichannelAudio,		//Multi Channel Audio : 1 or 0\n
			Integer mHasDolbyDigital,		//Dolby Digital Audio : 1 or 0\n
			Integer mHasSubtitles,		//Subtitle : 1 or 0\n
			Integer mHasHardOfHearingAudio,		//Hard of Hearing Audio : 1 or 0\n
			Integer mHasHardOfHearingSub,		//Hard of Hearing Sub : 1 or 0\n
			Integer mHasVisuallyImpairedAudio,		//Visually Impaire Audio : 1 or 0\n
			Integer mIsSeries,		//Series\n
			Integer mHasTimer,		//Has Timer\n
			Integer mTimerId,		//Timer ID\n
			Integer mAgeRating,		//Age Rateing\n
			]\n
		
		@see   IEPGEvent
		@todo   mStartTime return Type :  time_t
		"""
		req = []
		req.append( ElisAction.epgevent_GetPresent )

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def epgevent_GetFollowing(self ) :
		"""
		Get EPG of Following
		@return    IEPGEvent  Struct  Elis EPG Event
			\n[\n
			Integer mEventId,		//EPG Event ID \n
			String mEventName,		//EPG Event NAme\n
			Integer mSid,		//Service ID\n
			Integer mTsid,		//Transport Stream ID\n
			Integer mOnid,		//Original Network ID\n
			Integer mStartTime,		//EPG Event Start Time (ms)\n
			Integer mDuration,		//EPG Event Duration Time (ms) \n
			Integer mContentTag,		//EPG Event Content Tag\n
			Integer mHasHDVideo,		//HD Video : 1 or 0\n
			Integer mHas16_9Video,		//16:9 video : 1 or 0\n
			Integer mHasStereoAudio,		//Stereo Audio : 1 or 0 \n
			Integer mHasMultichannelAudio,		//Multi Channel Audio : 1 or 0\n
			Integer mHasDolbyDigital,		//Dolby Digital Audio : 1 or 0\n
			Integer mHasSubtitles,		//Subtitle : 1 or 0\n
			Integer mHasHardOfHearingAudio,		//Hard of Hearing Audio : 1 or 0\n
			Integer mHasHardOfHearingSub,		//Hard of Hearing Sub : 1 or 0\n
			Integer mHasVisuallyImpairedAudio,		//Visually Impaire Audio : 1 or 0\n
			Integer mIsSeries,		//Series\n
			Integer mHasTimer,		//Has Timer\n
			Integer mTimerId,		//Timer ID\n
			Integer mAgeRating,		//Age Rateing\n
			]\n
		
		@see   IEPGEvent
		@todo   mStartTime return Type :  time_t
		"""
		req = []
		req.append( ElisAction.epgevent_GetFollowing )

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def epgevent_Get(self ,  eventId,  sid,  tsid,  onid,  startTime) :
		"""
		Get EPG Event
		@param    eventId  Integer  EPG Event ID 
		@param    sid  Integer  Service ID
		@param    tsid  Integer  Transport Stream ID
		@param    onid  Integer  Original Network ID
		@param    startTime  Integer  EPG Event Start Time (ms)
		@return    IEPGEvent  Struct  Elis EPG Event
			\n[\n
			Integer mEventId,		//EPG Event ID \n
			String mEventName,		//EPG Event Name\n
			Integer mSid,		//Service ID\n
			Integer mTsid,		//Transport Stream ID\n
			Integer mOnid,		//Original Network ID\n
			Integer mStartTime,		//EPG Event Start Time (ms)\n
			Integer mDuration,		//EPG Event Duration Time (ms) \n
			Integer mContentTag,		//EPG Event Content Tag\n
			Integer mHasHDVideo,		//HD Video : 1 or 0\n
			Integer mHas16_9Video,		//16:9 video : 1 or 0\n
			Integer mHasStereoAudio,		//Stereo Audio : 1 or 0 \n
			Integer mHasMultichannelAudio,		//Multi Channel Audio : 1 or 0\n
			Integer mHasDolbyDigital,		//Dolby Digital Audio : 1 or 0\n
			Integer mHasSubtitles,		//Subtitle : 1 or 0\n
			Integer mHasHardOfHearingAudio,		//Hard of Hearing Audio : 1 or 0\n
			Integer mHasHardOfHearingSub,		//Hard of Hearing Sub : 1 or 0\n
			Integer mHasVisuallyImpairedAudio,		//Visually Impaire Audio : 1 or 0\n
			Integer mIsSeries,		//Series\n
			Integer mHasTimer,		//Has Timer\n
			Integer mTimerId,		//Timer ID\n
			Integer mAgeRating,		//Age Rateing\n
			]\n
		
		@see   IEPGEvent
		@todo   mStartTime return Type :  time_t
		"""
		req = []
		req.append( ElisAction.epgevent_Get )
		req.append('%d' %eventId)
		req.append('%d' %sid)
		req.append('%d' %tsid)
		req.append('%d' %onid)
		req.append('%d' %startTime)

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def epgevent_GetList(self ,  sid,  tsid,  onid,  gmtFrom,  gmtUntil,  maxCount) :
		"""
		Get EPG Event List
		@param    sid  Integer  Service ID
		@param    tsid  Integer  Transport Stream ID
		@param    onid  Integer  Original Network ID
		@param    gmtFrom  Integer  EPG Event Start Time (ms)
		@param    gmtUntil  Integer  EPG Event Start Time (ms)
		@param    maxCount  Integer  EPG Event Start Time (ms)
		@return    IEPGEvent  Struct  Elis EPG Event
			\n[\n[\n
			Integer mEventId,		//EPG Event ID \n
			String mEventName,		//EPG Event Name\n
			Integer mSid,		//Service ID\n
			Integer mTsid,		//Transport Stream ID\n
			Integer mOnid,		//Original Network ID\n
			Integer mStartTime,		//EPG Event Start Time (ms)\n
			Integer mDuration,		//EPG Event Duration Time (ms) \n
			Integer mContentTag,		//EPG Event Content Tag\n
			Integer mHasHDVideo,		//HD Video : 1 or 0\n
			Integer mHas16_9Video,		//16:9 video : 1 or 0\n
			Integer mHasStereoAudio,		//Stereo Audio : 1 or 0 \n
			Integer mHasMultichannelAudio,		//Multi Channel Audio : 1 or 0\n
			Integer mHasDolbyDigital,		//Dolby Digital Audio : 1 or 0\n
			Integer mHasSubtitles,		//Subtitle : 1 or 0\n
			Integer mHasHardOfHearingAudio,		//Hard of Hearing Audio : 1 or 0\n
			Integer mHasHardOfHearingSub,		//Hard of Hearing Sub : 1 or 0\n
			Integer mHasVisuallyImpairedAudio,		//Visually Impaire Audio : 1 or 0\n
			Integer mIsSeries,		//Series\n
			Integer mHasTimer,		//Has Timer\n
			Integer mTimerId,		//Timer ID\n
			Integer mAgeRating,		//Age Rateing\n
			]\n]\n
		
		@see   IEPGEvent
		@todo   mStartTime return Type :  time_t
		"""
		req = []
		req.append( ElisAction.epgevent_GetList )
		req.append('%d' %sid)
		req.append('%d' %tsid)
		req.append('%d' %onid)
		req.append('%d' %gmtFrom)
		req.append('%d' %gmtUntil)
		req.append('%d' %maxCount)

		
		self.send( req )
		retValue = []
		while 1:
			reply=self.read()
			if reply[len(reply)-1].upper() == 'LASTMESSAGE':
				reply.remove('LASTMESSAGE')
				retValue.append( reply )
				return retValue
			retValue.append( reply )
		

	def epgevent_GetDescription(self ,  eventId,  sid,  tsid,  onid,  startTime) :
		"""
		Get EPG Event Description
		@param    eventId  Integer  EPG Event ID 
		@param    sid  Integer  Service ID
		@param    tsid  Integer  Transport Stream ID
		@param    onid  Integer  Original Network ID
		@param    startTime  Integer  EPG Event Start Time (ms)
		@return    IEPGEvent  Struct  Elis EPG Event
			\n[\n
			Integer mEventId,		//EPG Event ID \n
			String mEventDescription,		//EPG Event Description\n
			]\n
		
		@see   IEPGEvent
		"""
		req = []
		req.append( ElisAction.epgevent_GetDescription )
		req.append('%d' %eventId)
		req.append('%d' %sid)
		req.append('%d' %tsid)
		req.append('%d' %onid)
		req.append('%d' %startTime)

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def satellite_GetByChannelNumber(self ,  number,  serviceType) :
		"""
		Get Satellite Information By ChannelNumber
		@param    number  Integer  Channel Number
		@param    serviceType  Integer  Service Type :E_SERVICE_TYPE_INVALID, E_SERVICE_TYPE_TV, E_SERVICE_TYPE_RADIO, E_SERVICE_TYPE_DATA
		@return    ISatelliteInfo  Struct  Satellite Information
			\n[\n
			Integer mLongitude,		//Satellite Longitude\n
			Integer mBand,		//Band:Satellite Band E_BAND_UNDEFINED, E_BAND_KU, E_BAND_C\n
			String mName,		//Satellite Name\n
			]\n
		
		@see   ISatelliteInfo
		"""
		req = []
		req.append( ElisAction.satellite_GetByChannelNumber )
		req.append('%d' %number)
		req.append('%d' %serviceType)

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def satellite_Get(self ,  longitude,  band) :
		"""
		Get Satellite Information 
		@param    longitude  Integer  Satellite Longitude
		@param    band  Integer  Band:Satellite Band E_BAND_UNDEFINED, E_BAND_KU, E_BAND_C
		@return    ISatelliteInfo  Struct  Satellite Information
			\n[\n
			Integer mLongitude,		//Satellite Longitude\n
			Integer mBand,		//Band:Satellite Band E_BAND_UNDEFINED, E_BAND_KU, E_BAND_C\n
			String mName,		//Satellite Name\n
			]\n
		
		@see   ISatelliteInfo
		"""
		req = []
		req.append( ElisAction.satellite_Get )
		req.append('%d' %longitude)
		req.append('%d' %band)

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def satellite_GetList(self ,  sortOrder) :
		"""
		Get Satellite List 
		@param    sortOrder  Integer  Sort Order : E_SORTING_ORBITAL, E_SORTING_ALPHBET, E_SORTING_FAVORITE
		@return    ISatelliteInfo  Struct  Satellite Information
			\n[\n[\n
			Integer mLongitude,		//Satellite Longitude\n
			Integer mBand,		//Band:Satellite Band E_BAND_UNDEFINED, E_BAND_KU, E_BAND_C\n
			String mName,		//Satellite Name\n
			]\n]\n
		
		@see   ISatelliteInfo
		"""
		req = []
		req.append( ElisAction.satellite_GetList )
		req.append('%d' %sortOrder)

		
		self.send( req )
		retValue = []
		while 1:
			reply=self.read()
			if reply[len(reply)-1].upper() == 'LASTMESSAGE':
				reply.remove('LASTMESSAGE')
				retValue.append( reply )
				return retValue
			retValue.append( reply )
		

	def satellite_Add(self ,  longitude,  band,  name) :
		"""
		Satellite ADD
		@param    longitude  Integer  Satellite Longitude
		@param    band  Integer  Band:Satellite Band E_BAND_UNDEFINED, E_BAND_KU, E_BAND_C
		@param    name  String  Satellite name
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.satellite_Add )
		req.append('%d' %longitude)
		req.append('%d' %band)
		req.append(name)

		reply= self.command(req)
		return reply

	def satellite_ChangeName(self ,  longitude,  band,  newName) :
		"""
		Satellite Change Name
		@param    longitude  Integer  Satellite Longitude
		@param    band  Integer  Band:Satellite Band E_BAND_UNDEFINED, E_BAND_KU, E_BAND_C
		@param    newName  String  Satellite newName
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.satellite_ChangeName )
		req.append('%d' %longitude)
		req.append('%d' %band)
		req.append(newName)

		reply= self.command(req)
		return reply

	def satellite_Delete(self ,  longitude,  band) :
		"""
		Satellite Delete
		@param    longitude  Integer  Satellite Longitude
		@param    band  Integer  Band:Satellite Band E_BAND_UNDEFINED, E_BAND_KU, E_BAND_C
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.satellite_Delete )
		req.append('%d' %longitude)
		req.append('%d' %band)

		reply= self.command(req)
		return reply

	def satellite_GetConfiguredList(self ,  sortOrder) :
		"""
		Get Satellite List for Configured
		@param    sortOrder  Integer  Sort Order : E_SORTING_ORBITAL, E_SORTING_ALPHBET, E_SORTING_FAVORITE
		@return    ISatelliteInfo  Struct  Satellite Information
			\n[\n[\n
			Integer mLongitude,		//Satellite Longitude\n
			Integer mBand,		//Band:Satellite Band E_BAND_UNDEFINED, E_BAND_KU, E_BAND_C\n
			String mName,		//Satellite Name\n
			]\n]\n
		
		@see   ISatelliteInfo
		"""
		req = []
		req.append( ElisAction.satellite_GetConfiguredList )
		req.append('%d' %sortOrder)

		print ' test init Channel List by shinjh777 '	
		self.send( req )
		retValue = []
		while 1:
			reply=self.read()
			if reply[len(reply)-1].upper() == 'LASTMESSAGE':
				reply.remove('LASTMESSAGE')
				retValue.append( reply )
				return retValue
			retValue.append( reply )
		

	def transponder_GetList(self ,  longitude,  band) :
		"""
		Get Transponder List of Satellite
		@param    longitude  Integer  Satellite Longitude
		@param    band  Integer  Band:Satellite Band E_BAND_UNDEFINED, E_BAND_KU, E_BAND_C
		@return    ITransponderInfo  Struct  Transponder Information
			\n[\n[\n
			Integer mFrequency,		//Frequency [MHz]\n
			Integer mSymbolRate,		//Symbolrate [ KHz ]\n
			Integer mPolarization,		//Polarizationi:\n
			Integer mFECMode,		//Fec Mode : \n
			Integer mTsid,		//Transport Stream ID\n
			Integer mOnid,		//Original Network ID\n
			Integer mNid,		//Network ID\n
			]\n]\n
		
		@see   ITransponderInfo
		"""
		req = []
		req.append( ElisAction.transponder_GetList )
		req.append('%d' %longitude)
		req.append('%d' %band)

		
		self.send( req )
		retValue = []
		while 1:
			reply=self.read()
			if reply[len(reply)-1].upper() == 'LASTMESSAGE':
				reply.remove('LASTMESSAGE')
				retValue.append( reply )
				return retValue
			retValue.append( reply )
		

	def transponder_HasCompatible(self ,  longitude,  band,  ITransponderInfo) :
		"""
		Transponder
		@param    longitude  Integer  Satellite Longitude
		@param    band  Integer  Band:Satellite Band E_BAND_UNDEFINED, E_BAND_KU, E_BAND_C
		@param    ITransponderInfo  Struct  Transponder information
		@return      Bool   TRUE or FALSE
		@see   ITransponderInfo
		"""
		req = []
		req.append( ElisAction.transponder_HasCompatible )
		req.append('%d' %longitude)
		req.append('%d' %band)
		for ele in ITransponderInfo:
			req.append('%d' %mFrequency)
			req.append('%d' %mSymbolRate)
			req.append('%d' %mPolarization)
			req.append('%d' %mFECMode)
			req.append('%d' %mTsid)
			req.append('%d' %mOnid)
			req.append('%d' %mNid)

		reply= self.command(req)
		return reply

	def transponder_Add(self ,  longitude,  band,  ITransponderInfo) :
		"""
		Transponder Add
		@param    longitude  Integer  Satellite Longitude
		@param    band  Integer  Band:Satellite Band E_BAND_UNDEFINED, E_BAND_KU, E_BAND_C
		@param    ITransponderInfo  Struct  Transponder information
		@return      Bool   TRUE or FALSE
		@see   ITransponderInfo
		"""
		req = []
		req.append( ElisAction.transponder_Add )
		req.append('%d' %longitude)
		req.append('%d' %band)
		for ele in ITransponderInfo:
			req.append('%d' %mFrequency)
			req.append('%d' %mSymbolRate)
			req.append('%d' %mPolarization)
			req.append('%d' %mFECMode)
			req.append('%d' %mTsid)
			req.append('%d' %mOnid)
			req.append('%d' %mNid)

		reply= self.command(req)
		return reply

	def transponder_Delete(self ,  longitude,  band,  ITransponderInfo) :
		"""
		Transponder Delete
		@param    longitude  Integer  Satellite Longitude
		@param    band  Integer  Band:Satellite Band E_BAND_UNDEFINED, E_BAND_KU, E_BAND_C
		@param    ITransponderInfo  Struct  Transponder information
		@return      Bool   TRUE or FALSE
		@see   ITransponderInfo
		"""
		req = []
		req.append( ElisAction.transponder_Delete )
		req.append('%d' %longitude)
		req.append('%d' %band)
		for ele in ITransponderInfo:
			req.append('%d' %mFrequency)
			req.append('%d' %mSymbolRate)
			req.append('%d' %mPolarization)
			req.append('%d' %mFECMode)
			req.append('%d' %mTsid)
			req.append('%d' %mOnid)
			req.append('%d' %mNid)

		reply= self.command(req)
		return reply

	def satelliteconfig_GetList(self ,  tunerNo) :
		"""
		Get Satellite Config List 
		@param    tunerNo  Integer  Tuner Number 
		@return    ISatelliteConfig  Struct  Satellite Configure Information
			\n[\n[\n
			Integer mTunerIndex,		//Tuenr Index\n
			Integer mSlotNumber,		//Slot Number\n
			Integer mSatelliteLongitude,		//Satellite Longitude\n
			Integer mBandType,		//Band Type : E_BAND_UNDEFINED, E_BAND_KU, E_BAND_C\n
			Integer mFrequencyLevel,		//Frequency Level : E_SAT_22KHZ_OFF, E_SAT_22KHZ_ON\n
			Integer mDisEqc11,		//Diseqc11 used ?: \n
			Integer mDisEqcMode,		//Diseqc Mode : E_SWITC_DISABLED, E_SWITCH_1OF4, E_SWITCH_2OF4, E_SWITCH_3OF4, E_SWITCH_4OF4, E_SWITCH_MINI_A, E_SWITCH_MINI_B\n
			Integer mDisEqcRepeat,		//Diseqc Repeat : true or false \n
			Integer mIsConfigUsed,		//Configure used : true or false\n
			Integer mLnbType,		//Lnb Type : E_LNB_UNIVERSAL, E_LNB_SINGLE, E_LNB_DUAL\n
			Integer mMotorizedType,		//Diseqc Motorized Type : E_MOTORIZED_OFF, E_MOTORIZED_ON, E_MOTORIZED_USALS\n
			Integer mLowLNB,		//Low LNB Value\n
			Integer mHighLNB,		//High LNB Value\n
			Integer mLNBThreshold,		//LNB Threadhold Value\n
			Integer mMotorizedData,		//Motorized Data \n
			Integer mIsOneCable,		//One Cable : true or false\n
			Integer mOneCablePin,		//One Cable Pin\n
			Integer mOneCableMDU,		//One Cable MDU : true or false\n
			Integer mOneCableLoFreq1,		//One Cable Lo Frequency1[MHz]\n
			Integer mOneCableLoFreq2,		//One Cable Lo Frequency1[MHz]\n
			Integer mOneCableUBSlot,		//One Cable UB Slot \n
			Integer mOneCableUBFreq,		//One Cable UB Frequency[MHz]\n
			]\n]\n
		
		@see   ISatelliteConfig
		"""
		req = []
		req.append( ElisAction.satelliteconfig_GetList )
		req.append('%d' %tunerNo)

		
		self.send( req )
		retValue = []
		while 1:
			reply=self.read()
			if reply[len(reply)-1].upper() == 'LASTMESSAGE':
				reply.remove('LASTMESSAGE')
				retValue.append( reply )
				return retValue
			retValue.append( reply )
		

	def satelliteconfig_GetFirstAvailablePos(self ,  tunerNo,  currentSlotNo) :
		"""
		Get First Available Position
		@param    tunerNo  Integer  Tuner Number
		@param    currentSlotNo  Integer  Current Slot Number
		@return      Integer  First Available Position Number
		"""
		req = []
		req.append( ElisAction.satelliteconfig_GetFirstAvailablePos )
		req.append('%d' %tunerNo)
		req.append('%d' %currentSlotNo)

		reply= self.command(req)
		return reply

	def satelliteconfig_SaveList(self ,  ISatelliteConfig) :
		"""
		Get Satellite Config List 
		@param    ISatelliteConfig  Struct  Satellite Configure Information
		@return      Bool  TRUE or FALSE
		@see   ISatelliteConfig
		"""
		req = []
		req.append( ElisAction.satelliteconfig_SaveList )
		for ele in ISatelliteConfig:
			req.append('%d' %mTunerIndex)
			req.append('%d' %mSlotNumber)
			req.append('%d' %mSatelliteLongitude)
			req.append('%d' %mBandType)
			req.append('%d' %mFrequencyLevel)
			req.append('%d' %mDisEqc11)
			req.append('%d' %mDisEqcMode)
			req.append('%d' %mDisEqcRepeat)
			req.append('%d' %mIsConfigUsed)
			req.append('%d' %mLnbType)
			req.append('%d' %mMotorizedType)
			req.append('%d' %mLowLNB)
			req.append('%d' %mHighLNB)
			req.append('%d' %mLNBThreshold)
			req.append('%d' %mMotorizedData)
			req.append('%d' %mIsOneCable)
			req.append('%d' %mOneCablePin)
			req.append('%d' %mOneCableMDU)
			req.append('%d' %mOneCableLoFreq1)
			req.append('%d' %mOneCableLoFreq2)
			req.append('%d' %mOneCableUBSlot)
			req.append('%d' %mOneCableUBFreq)

		reply= self.command(req)
		return reply

	def satelliteconfig_DeleteAll(self ) :
		"""
		Delete of Satellite Config
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.satelliteconfig_DeleteAll )

		reply= self.command(req)
		return reply

	def datetime_GetGMTTime(self ) :
		"""
		Get GMT Time
		@return      Integer   GMT Time ms
		"""
		req = []
		req.append( ElisAction.datetime_GetGMTTime )

		reply= self.command(req)
		return reply

	def datetime_GetLocalOffset(self ) :
		"""
		Get Offset Time
		@return      Integer  Offset Time sec
		"""
		req = []
		req.append( ElisAction.datetime_GetLocalOffset )

		reply= self.command(req)
		return reply

	def datetime_GetLocalTime(self ) :
		"""
		Get Local Time
		@return      Integer   Local Time ms
		"""
		req = []
		req.append( ElisAction.datetime_GetLocalTime )

		reply= self.command(req)
		return reply

	def motorized_Stop(self ,  tunerNo) :
		"""
		diseqc command for Motorized Stop
		@param    tunerNo  Integer  Tuner Index
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.motorized_Stop )
		req.append('%d' %tunerNo)

		reply= self.command(req)
		return reply

	def motorized_GoWest(self ,  tunerNo) :
		"""
		diseqc command for Go West
		@param    tunerNo  Integer  Tuner Index
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.motorized_GoWest )
		req.append('%d' %tunerNo)

		reply= self.command(req)
		return reply

	def motorized_GoEast(self ,  tunerNo) :
		"""
		diseqc command for Go East
		@param    tunerNo  Integer  Tuner Index
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.motorized_GoEast )
		req.append('%d' %tunerNo)

		reply= self.command(req)
		return reply

	def motorized_StepWest(self ,  tunerNo) :
		"""
		diseqc command for Step West
		@param    tunerNo  Integer  Tuner Index
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.motorized_StepWest )
		req.append('%d' %tunerNo)

		reply= self.command(req)
		return reply

	def motorized_StepEast(self ,  tunerNo) :
		"""
		diseqc command for Step East
		@param    tunerNo  Integer  Tuner Index
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.motorized_StepEast )
		req.append('%d' %tunerNo)

		reply= self.command(req)
		return reply

	def motorized_SetEastLimit(self ,  tunerNo) :
		"""
		diseqc command for Set East Limit
		@param    tunerNo  Integer  Tuner Index
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.motorized_SetEastLimit )
		req.append('%d' %tunerNo)

		reply= self.command(req)
		return reply

	def motorized_SetWestLimit(self ,  tunerNo) :
		"""
		diseqc command for Set West Limit
		@param    tunerNo  Integer  Tuner Index
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.motorized_SetWestLimit )
		req.append('%d' %tunerNo)

		reply= self.command(req)
		return reply

	def motorized_ResetLimit(self ,  tunerNo) :
		"""
		diseqc command for Reset Limit
		@param    tunerNo  Integer  Tuner Index
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.motorized_ResetLimit )
		req.append('%d' %tunerNo)

		reply= self.command(req)
		return reply

	def motorized_GotoNull(self ,  tunerNo) :
		"""
		diseqc command for Go To NULL
		@param    tunerNo  Integer  Tuner Index
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.motorized_GotoNull )
		req.append('%d' %tunerNo)

		reply= self.command(req)
		return reply

	def motorized_SavePosition(self ,  tunerNo,  posNo) :
		"""
		diseqc command for Save Position
		@param    tunerNo  Integer  Tuner Index
		@param    posNo  Integer  Position Index
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.motorized_SavePosition )
		req.append('%d' %tunerNo)
		req.append('%d' %posNo)

		reply= self.command(req)
		return reply

	def player_GetStatus(self ) :
		"""
		Get Status of Player
		@return    IPlayerStatus  Struct  Player Status Information
			\n[\n
			Integer mMode,		//Player Mode : E_MODE_LIVE, E_MODE_TIMESHIFT, E_MODE_PVR, E_MODE_EXTERNAL_PVR, E_MODE_MULTIMEDIA\n
			Integer mKey,		//Live Channel number\n
			Integer mServiceType,		//Service Type\n
			Integer mStartTimeInMs,		//Start Time ms\n
			Integer mPlayTimeInMs,		//Play Time ms\n
			Integer mEndTimeInMs,		//End Time ms\n
			Integer mSpeed,		//Play Speed Value\n
			Integer mIsTimeshiftPending,		//Timeshift Pending Status : true or false\n
			Integer mTotalFileCount,		//Total File Conut\n
			Integer mCurrentIndex,		//Current playing Index\n
			Integer mAbsoluteCurrentIndex,		//Absolute Current Index\n
			]\n
		
		"""
		req = []
		req.append( ElisAction.player_GetStatus )

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def player_StartTimeshiftPlayback(self ,  playbackMode,  data) :
		"""
		Start Timeshift of Playback
		@param    playbackMode  Integer  playbackMode : E_IPLAYER_TIMESHIFT_START_PAUSE, E_IPLAYER_TIMESHIFT_START_REWIND,  E_IPLAYER_TIMESHIFT_START_REPLAY
		@param    data  Integer  Offset time ms
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.player_StartTimeshiftPlayback )
		req.append('%d' %playbackMode)
		req.append('%d' %data)

		reply= self.command(req)
		return reply

	def player_StartInternalRecordPlayback(self ,  recordKey,  serviceType,  offsetms,  speed) :
		"""
		Start Internal Record of Playback
		@param    recordKey  Integer  Record Key
		@param    serviceType  Integer  Service Type
		@param    offsetms  Integer  Offset Time Ms
		@param    speed  Integer  Speed Value
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.player_StartInternalRecordPlayback )
		req.append('%d' %recordKey)
		req.append('%d' %serviceType)
		req.append('%d' %offsetms)
		req.append('%d' %speed)

		reply= self.command(req)
		return reply

	def player_Stop(self ) :
		"""
		Stop of Playback
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.player_Stop )

		reply= self.command(req)
		return reply

	def player_SetSpeed(self ,  speed) :
		"""
		Set Speed of Playback
		@param    speed  Integer  Play Speed
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.player_SetSpeed )
		req.append('%d' %speed)

		reply= self.command(req)
		return reply

	def player_JumpTo(self ,  milisec) :
		"""
		Jump to time Play 
		@param    milisec  Integer  Jump Time ms
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.player_JumpTo )
		req.append('%d' %milisec)

		reply= self.command(req)
		return reply

	def player_JumpToIFrame(self ,  milisec) :
		"""
		Jump to IFrame Play
		@param    milisec  Integer  Jump to IFrame ms
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.player_JumpToIFrame )
		req.append('%d' %milisec)

		reply= self.command(req)
		return reply

	def player_Pause(self ) :
		"""
		Pause of Playback
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.player_Pause )

		reply= self.command(req)
		return reply

	def player_Resume(self ) :
		"""
		Resume of Playback
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.player_Resume )

		reply= self.command(req)
		return reply

	def player_SetVolume(self ,  absVolume) :
		"""
		Set Volume of Playback 
		@param    absVolume  Integer  Volume Value
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.player_SetVolume )
		req.append('%d' %absVolume)

		reply= self.command(req)
		return reply

	def player_GetVolume(self ) :
		"""
		Get Volume of Playback
		@return      Integer   Volume Value
		"""
		req = []
		req.append( ElisAction.player_GetVolume )

		reply= self.command(req)
		return reply

	def player_SetMute(self ,  mute) :
		"""
		Set Mute of Playback 
		@param    mute  Integer  Mute Value : 1(Mute on), 0(Mute off)
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.player_SetMute )
		req.append('%d' %mute)

		reply= self.command(req)
		return reply

	def player_GetMute(self ) :
		"""
		Get Mute Statue of Playback
		@return      Integer   Mute Statue  : 1(Mute on), 0(Mute off)
		"""
		req = []
		req.append( ElisAction.player_GetMute )

		reply= self.command(req)
		return reply

	def player_AVBlank(self ,  blank,  force) :
		"""
		Set Blank/Mute of AV
		@param    blank  Integer  Blank : true or false
		@param    force  Integer  Force : true or false
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.player_AVBlank )
		req.append('%d' %blank)
		req.append('%d' %force)

		reply= self.command(req)
		return reply

	def player_VideoBlank(self ,  blank,  force) :
		"""
		Set Blank/Mute of Video
		@param    blank  Integer  Blank : true or false
		@param    force  Integer  Force : true or false
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.player_VideoBlank )
		req.append('%d' %blank)
		req.append('%d' %force)

		reply= self.command(req)
		return reply

	def player_AVMute(self ,  mute,  force) :
		"""
		Set Mute of AV
		@param    mute  Integer  Blank : true or false
		@param    force  Integer  Force : true or false
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.player_AVMute )
		req.append('%d' %mute)
		req.append('%d' %force)

		reply= self.command(req)
		return reply

	def player_StopLivePlayer(self ) :
		"""
		Stop of LivePlayer
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.player_StopLivePlayer )

		reply= self.command(req)
		return reply

	def player_SetVIdeoSize(self ,  posX,  posY,  width,  height) :
		"""
		Set Video Size of Player
		@param    posX  Integer  Position X
		@param    posY  Integer  Position Y
		@param    width  Integer  Width
		@param    height  Integer  Height
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.player_SetVIdeoSize )
		req.append('%d' %posX)
		req.append('%d' %posY)
		req.append('%d' %width)
		req.append('%d' %height)

		reply= self.command(req)
		return reply

	def player_IsVideoValid(self ) :
		"""
		Video Valid
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.player_IsVideoValid )

		reply= self.command(req)
		return reply

	def record_GetCount(self ,  serviceType) :
		"""
		Get Count of Record
		@param    serviceType  Integer  service Type
		@return      Integer   Record total Count
		"""
		req = []
		req.append( ElisAction.record_GetCount )
		req.append('%d' %serviceType)

		reply= self.command(req)
		return reply

	def record_GetRecordInfo(self ,  index,  serviceType) :
		"""
		Get Record Informationl
		@param    index  Integer  Recode Index
		@param    serviceType  Integer  service Type
		@return    IRecordInfo  Struct  Record Information
			\n[\n
			Integer RecordKey,		//Channel Number\n
			Integer FolderNumber,		//Channel presentation number\n
			Integer StartTime,		//Record Start Time\n
			Integer Duration,		//Record Duration Time\n
			Integer PlayedOffset,		//Played Offset\n
			Integer ChannelNo,		//Record Channel Number\n
			Integer ServiceType,		//Service Type\n
			String ChannelName,		//Record Channel Name\n
			String RecordName,		//Record Name\n
			Integer ServiceId,		//Service Id\n
			Integer Vpid,		//Video Pid\n
			Integer Apid,		//Audio Pid\n
			]\n
		
		@see   IRecordInfo
		"""
		req = []
		req.append( ElisAction.record_GetRecordInfo )
		req.append('%d' %index)
		req.append('%d' %serviceType)

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def record_GetRecordInfoByKey(self ,  key) :
		"""
		Get Record Informationl by Record Key
		@param    key  Integer  Recode Id
		@return    IRecordInfo  Struct  Record Information
			\n[\n
			Integer RecordKey,		//Channel Number\n
			Integer FolderNumber,		//Channel presentation number\n
			Integer StartTime,		//Record Start Time\n
			Integer Duration,		//Record Duration Time\n
			Integer PlayedOffset,		//Played Offset\n
			Integer ChannelNo,		//Record Channel Number\n
			Integer ServiceType,		//Service Type\n
			String ChannelName,		//Record Channel Name\n
			String RecordName,		//Record Name\n
			Integer ServiceId,		//Service Id\n
			Integer Vpid,		//Video Pid\n
			Integer Apid,		//Audio Pid\n
			]\n
		
		@see   IRecordInfo
		"""
		req = []
		req.append( ElisAction.record_GetRecordInfoByKey )
		req.append('%d' %key)

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def record_StartRecord(self ,  channelNo,  serviceType,  duration,  recordName) :
		"""
		Start Record
		@param    channelNo  Integer  Record Channel Number
		@param    serviceType  Integer  Record Service Type
		@param    duration  Integer  Record Duration Time
		@param    recordName  String  Record Name
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.record_StartRecord )
		req.append('%d' %channelNo)
		req.append('%d' %serviceType)
		req.append('%d' %duration)
		req.append(recordName)

		reply= self.command(req)
		return reply

	def record_StopRecord(self ,  channelNo,  serviceType,  key) :
		"""
		Stop Record
		@param    channelNo  Integer  Record Channel Number
		@param    serviceType  Integer  Record Service Type
		@param    key  Integer  Record Id
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.record_StopRecord )
		req.append('%d' %channelNo)
		req.append('%d' %serviceType)
		req.append('%d' %key)

		reply= self.command(req)
		return reply

	def record_GetRunningRecorderCount(self ) :
		"""
		Get Running Record Count
		@return      Integer  Running Record Count
		"""
		req = []
		req.append( ElisAction.record_GetRunningRecorderCount )

		reply= self.command(req)
		return reply

	def record_GetRunningRecordInfo(self ,  index) :
		"""
		Get Running Record Informationl
		@param    index  Integer  Recode Index
		@return    IRecordInfo  Struct  Record Information
			\n[\n
			Integer RecordKey,		//Channel Number\n
			Integer FolderNumber,		//Channel presentation number\n
			Integer StartTime,		//Record Start Time\n
			Integer Duration,		//Record Duration Time\n
			Integer PlayedOffset,		//Played Offset\n
			Integer ChannelNo,		//Record Channel Number\n
			Integer ServiceType,		//Service Type\n
			String ChannelName,		//Record Channel Name\n
			String RecordName,		//Record Name\n
			Integer ServiceId,		//Service Id\n
			Integer Vpid,		//Video Pid\n
			Integer Apid,		//Audio Pid\n
			]\n
		
		@see   IRecordInfo
		"""
		req = []
		req.append( ElisAction.record_GetRunningRecordInfo )
		req.append('%d' %index)

		
		reply= self.command(req)
		reply.remove('LASTMESSAGE')
		return reply
			

	def record_GetPartitionSize(self ) :
		"""
		Get Partition Size
		@return      Integer  Parition Size
		"""
		req = []
		req.append( ElisAction.record_GetPartitionSize )

		reply= self.command(req)
		return reply

	def record_GetFreeMBSize(self ) :
		"""
		Get Free MB Size
		@return      Integer  Free MB Size
		"""
		req = []
		req.append( ElisAction.record_GetFreeMBSize )

		reply= self.command(req)
		return reply

	def record_DeleteRecord(self ,  key,  serviceType) :
		"""
		Delete Record
		@param    key  Integer  Record Id
		@param    serviceType  Integer  Record Service Type
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.record_DeleteRecord )
		req.append('%d' %key)
		req.append('%d' %serviceType)

		reply= self.command(req)
		return reply

	def record_SetLock(self ,  key,  serviceType,  lock) :
		"""
		Set Lock of Record
		@param    key  Integer  Record Id
		@param    serviceType  Integer  Record Service Type
		@param    lock  Integer  Record Lock  Value : true or false
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.record_SetLock )
		req.append('%d' %key)
		req.append('%d' %serviceType)
		req.append('%d' %lock)

		reply= self.command(req)
		return reply

	def record_Rename(self ,  key,  serviceType,  newName) :
		"""
		Record Rename 
		@param    key  Integer  Record Id
		@param    serviceType  Integer  Record Service Type
		@param    newName  String  New Name of Record
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.record_Rename )
		req.append('%d' %key)
		req.append('%d' %serviceType)
		req.append(newName)

		reply= self.command(req)
		return reply

	def record_IsRecording(self ,  key,  serviceType) :
		"""
		Recording Check
		@param    key  Integer  Record Id
		@param    serviceType  Integer  Record Service Type
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.record_IsRecording )
		req.append('%d' %key)
		req.append('%d' %serviceType)

		reply= self.command(req)
		return reply

	def enum_GetProp(self ,  name) :
		"""
		Get Enum Property
		@param    name  String  Property Name
		@return      Integer  Property Value
		"""
		req = []
		req.append( ElisAction.enum_GetProp )
		req.append(name)

		reply= self.command(req)
		return reply

	def int_GetProp(self ,  name) :
		"""
		Get Int Property
		@param    name  String  Property Name
		@return      Integer  Property Value
		"""
		req = []
		req.append( ElisAction.int_GetProp )
		req.append(name)

		reply= self.command(req)
		return reply

	def enum_SetProp(self ,  name,  Property) :
		"""
		Set Enum Property
		@param    name  String  Property Name
		@param    Property  Integer  Property Value
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.enum_SetProp )
		req.append(name)
		req.append('%d' %Property)

		reply= self.command(req)
		return reply

	def int_SetProp(self ,  name,  Property) :
		"""
		Set Int Property
		@param    name  String  Property Name
		@param    Property  Integer  Property Value
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.int_SetProp )
		req.append(name)
		req.append('%d' %Property)

		reply= self.command(req)
		return reply

	def channel_SearchByCarrier(self ,  longitude,  band,  ITransponderInfo) :
		"""
		Channel Search by Carrier
		@param    longitude  Integer  Satellite Longitude
		@param    band  Integer  Carrier Index
		@param    ITransponderInfo  Struct  Transponder information
		@return      Bool   TRUE or FALSE
		@see   ITransponderInfo
		"""
		req = []
		req.append( ElisAction.channel_SearchByCarrier )
		req.append('%d' %longitude)
		req.append('%d' %band)
		for ele in ITransponderInfo:
			req.append('%d' %mFrequency)
			req.append('%d' %mSymbolRate)
			req.append('%d' %mPolarization)
			req.append('%d' %mFECMode)
			req.append('%d' %mTsid)
			req.append('%d' %mOnid)
			req.append('%d' %mNid)

		reply= self.command(req)
		return reply

	def channelscan_BySatellite(self ,  longitude,  band) :
		"""
		Channel Search by Satellite
		@param    longitude  Integer  Satellite Longitude
		@param    band  Integer  Band Type : E_BAND_UNDEFINED, E_BAND_KU, E_BAND_C
		@return      Bool   TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.channelscan_BySatellite )
		req.append('%d' %longitude)
		req.append('%d' %band)

		reply= self.command(req)
		return reply

	def channelscan_Abort(self ) :
		"""
		Channel Scan Abort
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.channelscan_Abort )

		reply= self.command(req)
		return reply

	def subtitle_GetCount(self ) :
		"""
		Get Subtitle Count 
		@return      Integer  Property Value
		"""
		req = []
		req.append( ElisAction.subtitle_GetCount )

		reply= self.command(req)
		return reply

	def subtitle_Select(self ,  pid,  pageId,  subId) :
		"""
		Select Subtitle
		@param    pid  Integer  
		@param    pageId  Integer  
		@param    subId  Integer  
		@return      Integer  Property Value
		"""
		req = []
		req.append( ElisAction.subtitle_Select )
		req.append('%d' %pid)
		req.append('%d' %pageId)
		req.append('%d' %subId)

		reply= self.command(req)
		return reply

	def frontdisplay_GetMaxStringLength(self ) :
		"""
		Get Max String Length
		@return      Integer  Max String Length Value
		"""
		req = []
		req.append( ElisAction.frontdisplay_GetMaxStringLength )

		reply= self.command(req)
		return reply

	def frontdisplay_SetMessage(self ,  message) :
		"""
		Set Message for Front Display
		@param    message  String  Message
		@return      Integer  Max String Length Value
		"""
		req = []
		req.append( ElisAction.frontdisplay_SetMessage )
		req.append(message)

		reply= self.command(req)
		return reply

	def frontdisplay_SetIcon(self ,  iconIndex,  onoff) :
		"""
		Set Icon for Front Display
		@param    iconIndex  Integer  Icon Index
		@param    onoff  Integer  On or Off
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.frontdisplay_SetIcon )
		req.append('%d' %iconIndex)
		req.append('%d' %onoff)

		reply= self.command(req)
		return reply

	def frontdisplay_SetLedOnOff(self ,  ledNumber,  onoff) :
		"""
		Set LED On and Off forFront Display
		@param    ledNumber  Integer  Led Number
		@param    onoff  Integer  On or Off
		@return      Bool  TRUE or FALSE
		"""
		req = []
		req.append( ElisAction.frontdisplay_SetLedOnOff )
		req.append('%d' %ledNumber)
		req.append('%d' %onoff)

		reply= self.command(req)
		return reply
