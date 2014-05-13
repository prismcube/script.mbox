from datetime import datetime
from webinterface import Webinterface
from xml.sax.saxutils import escape

class ElmoGetCurrent( Webinterface ) :

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

		super(ElmoGetCurrent, self).__init__(urlPath)
		
		self.currentUnixTimestamp = self.mCommander.Datetime_GetLocalTime()
		# self.currenttime = datetime.fromtimestamp( self.currentUnixTimestamp )
		self.currentChannel = self.mDataCache.Channel_GetCurrent()
		
		# self.currentEpg = self.mDataCache.Epgevent_GetPresent()
		self.currentEpg = self.mCommander.Epgevent_GetPresent()
		self.followingEpg = self.mCommander.Epgevent_GetFollowing() 

		"""
		if self.currentEpg == None :
			self.currentEpg =  ElisIEPGEvent()
		if self.followingEpg == None :
			self.followingEpg =  ElisIEPGEvent()		
		"""
		
		# print 'current time'
		# print self.mCommander.Datetime_GetLocalTime()
		
		# self.ref = self.makeRef(self.currentChannel.mSid, self.currentChannel.mTsid, self.currentChannel.mOnid, self.currentChannel.mNumber) 
		self.ref = self.makeRef(self.currentChannel.mSid, self.currentChannel.mTsid, self.currentChannel.mOnid, self.currentChannel.mNumber) 
		
	def xmlResult(self) :
	
		xmlstr = '<?xml version="1.0" encoding="UTF-8"?>\n'
		
		xmlstr += '<e2currentserviceinformation>\n'
		xmlstr += '   <e2service>\n'
		xmlstr += '      <e2servicereference>'+self.ref.strip()+'</e2servicereference>\n'
		xmlstr += '      <e2servicename>' + self.currentChannel.mName + '</e2servicename>\n'
		xmlstr += '      <e2providername>' + self.currentChannel.mName + '</e2providername>\n'
		xmlstr += '      <e2videowidth>{e2:convert type=ServiceInfo}VideoWidth{/e2:convert}</e2videowidth>\n'
		xmlstr += '      <e2videoheight>{e2:convert type=ServiceInfo}VideoHeight{/e2:convert}</e2videoheight>\n'
		xmlstr += '      <e2servicevideosize>{e2:convert type=ServiceInfo}VideoWidth{/e2:convert} x{e2:convert type=ServiceInfo}VideoHeight{/e2:convert}</e2servicevideosize>\n'
		xmlstr += '      <e2iswidescreen>{e2:convert type=ServiceInfo}IsWidescreen{/e2:convert}</e2iswidescreen>\n'
		xmlstr += '      <e2apid>{e2:convert type=ServiceInfo}AudioPid{/e2:convert}</e2apid>\n'
		xmlstr += '      <e2vpid>{e2:convert type=ServiceInfo}VideoPid{/e2:convert}</e2vpid>\n'
		xmlstr += '      <e2pcrpid>{e2:convert type=ServiceInfo}PcrPid{/e2:convert}</e2pcrpid>\n'
		xmlstr += '      <e2pmtpid>{e2:convert type=ServiceInfo}PmtPid{/e2:convert}</e2pmtpid>\n'
		xmlstr += '      <e2txtpid>{e2:convert type=ServiceInfo}TxtPid{/e2:convert}</e2txtpid>\n'
		xmlstr += '      <e2tsid>' + str(self.currentChannel.mSid) + '</e2tsid>\n'
		xmlstr += '      <e2onid>' + str(self.currentChannel.mOnid) + '</e2onid>\n'
		xmlstr += '      <e2sid>' + str(self.currentChannel.mSid) + '</e2sid>\n'
		xmlstr += '   </e2service>\n'

		xmlstr += '   <e2eventlist>\n'

		if self.currentEpg == None :
			pass
		else :
			xmlstr += '      <e2event>\n'
			xmlstr += '         <e2eventservicereference>' + self.ref + '</e2eventservicereference>\n'
			xmlstr += '         <e2eventservicename>' + self.currentEpg.mEventName + '</e2eventservicename>\n'
			xmlstr += '         <e2eventprovidername>' + self.currentChannel.mName + '</e2eventprovidername>\n'
			xmlstr += '         <e2eventid>' + str(self.currentEpg.mEventId) + '</e2eventid>\n'
			xmlstr += '         <e2eventname>' + self.currentEpg.mEventName + '</e2eventname>\n'
			xmlstr += '         <e2eventtitle>' + self.currentEpg.mEventName + '</e2eventtitle>\n'
			xmlstr += '         <e2eventdescription>' + escape( self.currentEpg.mEventDescription ) + '</e2eventdescription>\n'
			xmlstr += '         <e2eventstart>' + str( self.currentEpg.mStartTime ) + '</e2eventstart>\n'
			xmlstr += '         <e2eventduration>' + str( self.currentEpg.mDuration ) + '</e2eventduration>\n'
			
			endTime = self.currentEpg.mStartTime + self.currentEpg.mDuration
			remainTime = endTime - self.currentUnixTimestamp
			
			xmlstr += '         <e2eventremaining>' + str( remainTime ) + '</e2eventremaining>\n'
			xmlstr += '         <e2eventcurrenttime>' + str( self.currentUnixTimestamp ) + '</e2eventcurrenttime>\n'
			xmlstr += '         <e2eventdescriptionextended></e2eventdescriptionextended>\n'
			xmlstr += '      </e2event>\n'

		if self.followingEpg == None :
			pass
		else :
			xmlstr += '      <e2event>\n'
			xmlstr += '         <e2eventservicereference>' + self.ref + '</e2eventservicereference>\n'
			xmlstr += '         <e2eventservicename>' + self.followingEpg.mEventName + '</e2eventservicename>\n'
			xmlstr += '         <e2eventprovidername>' + self.currentChannel.mName + '</e2eventprovidername>\n'
			xmlstr += '         <e2eventid>' + str( self.followingEpg.mEventName ) + '</e2eventid>\n'
			xmlstr += '         <e2eventname>' + str( self.followingEpg.mEventName ) + '</e2eventname>\n'
			xmlstr += '         <e2eventtitle>' + str( self.followingEpg.mEventName ) + '</e2eventtitle>\n'
			xmlstr += '         <e2eventdescription>' + escape( str( self.followingEpg.mEventDescription ) ) + '</e2eventdescription>\n'
			xmlstr += '         <e2eventstart>' + str( self.followingEpg.mStartTime ) + '</e2eventstart>\n'
			xmlstr += '         <e2eventduration>' + str( self.followingEpg.mDuration ) + '</e2eventduration>\n'
			xmlstr += '         <e2eventremaining>' + str( self.followingEpg.mDuration ) + '</e2eventremaining>\n'
			xmlstr += '         <e2eventcurrenttime>' + str( self.currentUnixTimestamp ) + '</e2eventcurrenttime>\n'
			xmlstr += '         <e2eventdescriptionextended></e2eventdescriptionextended>\n'
			xmlstr += '      </e2event>\n'
			
		xmlstr += '   </e2eventlist>\n'
		xmlstr += '</e2currentserviceinformation>\n'

		return xmlstr
