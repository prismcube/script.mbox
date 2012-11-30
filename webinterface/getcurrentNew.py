from datetime import datetime
from webinterface import Webinterface

class PrismCubeGetCurrent( Webinterface ) :

	"""
	use Channle_GetCurrent to get the current channel 
	use Epgevent_GetCurrent and Epgevent_GetFollowing
	use Datetime_GetLocalTime

	ElisIChannel

	Integer	mNumber	Channel Number
	Integer	mPresentationNumber	Channel presentation number
	String	mName	Channel Name
	Integer	mServiceType	Service Type
	Integer	mLocked	Lock Status : LOCKED or UNLOCKED
	Integer	mIsCA	CAS Status : CA or notCA
	Integer	mIsHD	HD status
	Integer	mNid	Network ID
	Integer	mSid	Service ID
	Integer	mTsid	Transport Stream ID
	Integer	mOnid	Original Network ID
	Integer	mCarrierType	Carrier Type : DVBS, DVBT, DVBC
	Integer	mSkipped	Channel Skip Status : Skip or Not Skip
	Integer	mIsBlank	mIsBlank
	ElisICarrier	mCarrier	Carrier Information

	ElisIEpgEvent

	Integer	mEventId	EPG Event ID 
	String	mEventName	EPG Event NAme
	String	mEventDescription	EPG Event Description
	Integer	mSid	Service ID
	Integer	mTsid	Transport Stream ID
	Integer	mOnid	Original Network ID
	Integer	mStartTime	EPG Event Start Time (ms)
	Integer	mDuration	EPG Event Duration Time (ms) 
	Integer	mContentTag	EPG Event Content Tag
	Integer	mHasHDVideo	HD Video : 1 or 0
	Integer	mHas16_9Video	16:9 video : 1 or 0
	Integer	mHasStereoAudio	Stereo Audio : 1 or 0 
	Integer	mHasMultichannelAudio	Multi Channel Audio : 1 or 0
	Integer	mHasDolbyDigital	Dolby Digital Audio : 1 or 0
	Integer	mHasSubtitles	Subtitle : 1 or 0
	Integer	mHasHardOfHearingAudio	Hard of Hearing Audio : 1 or 0
	Integer	mHasHardOfHearingSub	Hard of Hearing Sub : 1 or 0
	Integer	mHasVisuallyImpairedAudio	Visually Impaire Audio : 1 or 0
	Integer	mIsSeries	Series
	Integer	mHasTimer	Has Timer
	Integer	mTimerId	Timer ID
	Integer	mAgeRating	Age Rateing
		
	"""

	def __init__(self, urlPath) :

		super(PrismCubeGetCurrent, self).__init__(urlPath)

	def xmlResult(self) :

		self.currentTime = self.mCommander.Datetime_GetLocalTime()
		# self.currenttime = datetime.fromtimestamp( self.currentUnixTimestamp )
		
		self.currentChannel = self.mDataCache.Channel_GetCurrent()
		self.currentEpg = self.mDataCache.Epgevent_GetPresent()
		self.followingEpg = self.mCommander.Epgevent_GetFollowing() 

		print 'current time'
		print self.mCommander.Datetime_GetLocalTime()
		
		self.ref = self.makeRef(self.currentChannel.mSid, self.currentChannel.mTsid, self.currentChannel.mOnid) 
		
		json = {}
		info = {}
		now = {}
		next = {}

		info["onid"] = self.currentChannel.mOnid
		info["txtpid"] = "N/A"
		info["pmtpid"] = "N/A"
		info["name"] = self.currentChannel.mName
		info["tsid"] = self.currentChannel.mTsid
		info["pcrpid"] = "N/A"
		info["sid"] = self.currentChannel.mSid
		info["namespace"] = 12582912
		info["height"] = "N/A"
		info["apid"] = "N/A"
		info["width"] = "N/A" 
		info["result"] = True
		info["aspect"] = "N/A"
		info["provider"] = "N/A"
		info["ref"] = self.ref
		info["vpid"] = "N/A"
		info["iswidescreen"] = False

		json["info"] = info

		# now 
		now["sname"] =  self.currentChannel.mName
		now["title"] =  self.currentEpg.mEventName
		now["begin_timestamp"] =  self.currentEpg.mStartTime
		now["now_timestamp"] =  self.currentTime
		now["sref"] =  self.ref
		now["id"] =  None 
		now["duration_sec"] =  self.currentEpg.mDuration
		now["provider"] =  "N/A"

		now["shortdesc"] =  self.currentEpg.mEventDescription.split('\n')[0]
		now["longdesc"] =  self.currentEpg.mEventDescription.split('\n')[0]

		if self.is_number(  self.currentEpg.mStartTime) and  self.is_number(  self.currentEpg.mDuration ) and self.is_number(  self.currentTime ) :
			remain = self.currentEpg.mStartTime + self.currentEpg.mDuration - self.currentTime
		else :
			remain = 0
		now["remaining"] =  remain

		json["now"] = now

		# next 
		next["sname"] =  self.currentChannel.mName
		next["title"] =  self.followingEpg.mEventName
		next["begin_timestamp"] =  self.followingEpg.mStartTime
		next["now_timestamp"] = self.currentTime
		next["sref"] =  self.ref
		next["id"] =  None
		next["duration_sec"] =  self.followingEpg.mDuration
		next["provider"] =  "N/A"
		next["shortdesc"] =  self.followingEpg.mEventDescription.split('\n')[0]
		next["longdesc"] =  self.followingEpg.mEventDescription.split('\n')[0]
		next["remaining"] =  self.followingEpg.mDuration

		json["next"] = next
		
		return str( json ).replace("'", '"').replace("None", "null").replace("True", "true").replace("False", "false")
