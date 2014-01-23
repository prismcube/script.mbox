
from datetime import datetime
from webinterface import Webinterface
# from ElisClass import *

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
		
		print 'current time'
		print self.mCommander.Datetime_GetLocalTime()
		
		# self.ref = self.makeRef(self.currentChannel.mSid, self.currentChannel.mTsid, self.currentChannel.mOnid, self.currentChannel.mNumber) 
		self.ref = self.makeRef(self.currentChannel.mSid, self.currentChannel.mTsid, self.currentChannel.mOnid, self.currentChannel.mNumber) 
		
	def xmlResult(self) :
	
		xmlstr = '<?xml version="1.0" encoding="UTF-8"?>'
		
		xmlstr += '<e2currentserviceinformation>'
		xmlstr += '   <e2service>'
		xmlstr += '      <e2servicereference>'
		xmlstr += 			self.ref
		xmlstr += '      </e2servicereference>'
		xmlstr += '      <e2servicename>'
		xmlstr +=			self.currentChannel.mName
		xmlstr += '      </e2servicename>'
		xmlstr += '      <e2providername>'
		xmlstr += 			self.currentChannel.mName
		xmlstr += '      </e2providername>'
		xmlstr += '      <e2videowidth>'
		xmlstr += '         {e2:convert type=ServiceInfo}VideoWidth{/e2:convert} '
		xmlstr += '      </e2videowidth>'
		xmlstr += '      <e2videoheight>'
		xmlstr += '         {e2:convert type=ServiceInfo}VideoHeight{/e2:convert} '
		xmlstr += '      </e2videoheight>'
		xmlstr += '      <e2servicevideosize>'
		xmlstr += '         {e2:convert type=ServiceInfo}VideoWidth{/e2:convert} x{e2:convert type=ServiceInfo}VideoHeight{/e2:convert} '
		xmlstr += '      </e2servicevideosize>'
		xmlstr += '      <e2iswidescreen>'
		xmlstr += '         {e2:convert type=ServiceInfo}IsWidescreen{/e2:convert} '
		xmlstr += '      </e2iswidescreen>'
		xmlstr += '      <e2apid>'
		xmlstr += '         {e2:convert type=ServiceInfo}AudioPid{/e2:convert} '
		xmlstr += '      </e2apid>'
		xmlstr += '      <e2vpid>'
		xmlstr += '         {e2:convert type=ServiceInfo}VideoPid{/e2:convert} '
		xmlstr += '      </e2vpid>'
		xmlstr += '      <e2pcrpid>'
		xmlstr += '         {e2:convert type=ServiceInfo}PcrPid{/e2:convert} '
		xmlstr += '      </e2pcrpid>'
		xmlstr += '      <e2pmtpid>'
		xmlstr += '         {e2:convert type=ServiceInfo}PmtPid{/e2:convert} '
		xmlstr += '      </e2pmtpid>'
		xmlstr += '      <e2txtpid>'
		xmlstr += '         {e2:convert type=ServiceInfo}TxtPid{/e2:convert} '
		xmlstr += '      </e2txtpid>'
		xmlstr += '      <e2tsid>'
		xmlstr +=			str(self.currentChannel.mSid)
		xmlstr += '      </e2tsid>'
		xmlstr += '      <e2onid>'
		xmlstr +=			str(self.currentChannel.mOnid)
		xmlstr += '      </e2onid>'
		xmlstr += '      <e2sid>'
		xmlstr += 			str(self.currentChannel.mSid)
		xmlstr += '      </e2sid>'
		xmlstr += '   </e2service>'

		xmlstr += '   <e2eventlist>'

		if self.currentEpg == None :
			pass
		else :
			xmlstr += '      <e2event>'
			xmlstr += '         <e2eventservicereference>'
			xmlstr += 			self.ref
			xmlstr += '         </e2eventservicereference>'
			xmlstr += '         <e2eventservicename>'
			xmlstr += 				self.currentEpg.mEventName
			xmlstr += '         </e2eventservicename>'
			xmlstr += '         <e2eventprovidername>'
			xmlstr +=           			self.currentChannel.mName
			xmlstr += '         </e2eventprovidername>'
			xmlstr += '         <e2eventid>'
			xmlstr += 				str(self.currentEpg.mEventId)
			xmlstr += '         </e2eventid>'
			xmlstr += '         <e2eventname>'
			xmlstr += 				self.currentEpg.mEventName
			xmlstr += '         </e2eventname>'
			xmlstr += '         <e2eventtitle>'
			xmlstr += 				self.currentEpg.mEventName
			xmlstr += '         </e2eventtitle>'
			xmlstr += '         <e2eventdescription>'
			xmlstr += 				self.currentEpg.mEventDescription
			xmlstr += '         </e2eventdescription>'
			xmlstr += '         <e2eventstart>'
			xmlstr += 				str( self.currentEpg.mStartTime )
			xmlstr += '         </e2eventstart>'
			xmlstr += '         <e2eventduration>'
			xmlstr += 				str( self.currentEpg.mDuration )
			xmlstr += '         </e2eventduration>'
			xmlstr += '         <e2eventremaining>'

			endTime = self.currentEpg.mStartTime + self.currentEpg.mDuration
			remainTime = endTime - self.currentUnixTimestamp
			
			xmlstr += 		str( remainTime )
			xmlstr += '         </e2eventremaining>'
			xmlstr += '         <e2eventcurrenttime>'
			xmlstr +=				str( self.currentUnixTimestamp )
			xmlstr += '         </e2eventcurrenttime>'
			xmlstr += '         <e2eventdescriptionextended>'
			xmlstr += '         </e2eventdescriptionextended>'
			xmlstr += '      </e2event>'

		if self.followingEpg == None :
			pass
		else :
			xmlstr += '      <e2event>'
			xmlstr += '         <e2eventservicereference>'
			xmlstr += 			self.ref
			xmlstr += '         </e2eventservicereference>'
			xmlstr += '         <e2eventservicename>'
			xmlstr += 				self.followingEpg.mEventName 
			xmlstr += '         </e2eventservicename>'
			xmlstr += '         <e2eventprovidername>'
			xmlstr += 				self.currentChannel.mName
			xmlstr += '         </e2eventprovidername>'
			xmlstr += '         <e2eventid>'
			xmlstr += 				str( self.followingEpg.mEventName )
			xmlstr += '         </e2eventid>'
			xmlstr += '         <e2eventname>'
			xmlstr += 				str( self.followingEpg.mEventName )
			xmlstr += '         </e2eventname>'
			xmlstr += '         <e2eventtitle>'
			xmlstr += 				str( self.followingEpg.mEventName )
			xmlstr += '         </e2eventtitle>'
			xmlstr += '         <e2eventdescription>'
			xmlstr += 				str( self.followingEpg.mEventDescription )
			xmlstr += '         </e2eventdescription>'
			xmlstr += '         <e2eventstart>'
			xmlstr += 				str( self.followingEpg.mStartTime )
			xmlstr += '         </e2eventstart>'
			xmlstr += '         <e2eventduration>'
			xmlstr += 				str( self.followingEpg.mDuration )
			xmlstr += '         </e2eventduration>'
			xmlstr += '         <e2eventremaining>'
			xmlstr +=			str( self.followingEpg.mDuration )
			xmlstr += '         </e2eventremaining>'
			xmlstr += '         <e2eventcurrenttime>'
			xmlstr +=				str( self.currentUnixTimestamp )
			xmlstr += '         </e2eventcurrenttime>'
			xmlstr += '         <e2eventdescriptionextended>'
			xmlstr += '         </e2eventdescriptionextended>'
			xmlstr += '      </e2event>'
			
		xmlstr += '   </e2eventlist>'
				
		"""	
		xmlstr += '   <e2volume>'
		xmlstr += '      <e2result>'
		xmlstr += '         {e2:convert type=VolumeInfo}Result{/e2:convert} '
		xmlstr += '      </e2result>'
		xmlstr += '      <e2resulttext>'
		xmlstr += '         {e2:convert type=VolumeInfo}ResultText{/e2:convert} '
		xmlstr += '      </e2resulttext>'
		xmlstr += '      <e2current>'
		xmlstr += '         {e2:convert type=VolumeInfo}Volume{/e2:convert} '
		xmlstr += '      </e2current>'
		xmlstr += '      <e2ismuted>'
		xmlstr += '         {e2:convert type=VolumeInfo}IsMuted{/e2:convert} '
		xmlstr += '      </e2ismuted>'
		xmlstr += '   </e2volume>'
		"""
		
		xmlstr += '</e2currentserviceinformation>'
		return xmlstr
