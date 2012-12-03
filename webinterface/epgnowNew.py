from datetime import datetime
from webinterface import Webinterface
import dbopen

"""
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

class PrismCubeEpgNow( Webinterface ) :

	def __init__(self, urlPath) :

		super(PrismCubeEpgNow, self).__init__(urlPath)
		self.currenttime = self.mCommander.Datetime_GetLocalTime()
		
	def xmlResult(self) :

		json = {}
		self.events = []
		
		if 'bRef' in self.params: 
			
			ref = self.unMakeRef( self.params['bRef'] ); 
			
			if ref :

				self.connFav = dbopen.DbOpen('channel.db').getConnection()	
				connEpg = dbopen.DbOpen('epg.db').getConnection()
				
				# get services in the bouquet 
				condition = ref['comment'].split('_')

				# query to favorite channel table in channel DB
				sql = "select GroupName, sid, tsid, nid, onid, name from " + condition[0] + " where  " + condition[1] + " = '" + condition[2] + "'"
				
				self.cFav = self.connFav.cursor()
				self.cFav.execute(sql)
				stations = self.cFav.fetchall()
				
				for station in stations :
				
					c = connEpg.cursor()
					
					sql = "select eventid, starttime, duration, eventName, eventDescription from tblEpg where sid=" + str( station[1] ) + " and tsid=" + str( station[2] ) + " and onid=" + str( station[4] )
					sql += " and starttime <= " + str( self.currenttime ) + " and starttime + duration >" + str( self.currenttime )

					c.execute(sql)		
					epg = c.fetchone()

					if epg :
						event = {}
						

						self.services.append(event)
					else :
						event = {}
						event["sname"] = station[5]
						event["title"] = "null"
						event["begin_timestamp"] = "null"
						event["now_timestamp"] = self.currenttime 
						event["sref"] = self.makeRef( station[1], station[2], station[4] )
						event["id"] = "null"
						event["duration_sec"] = "null"
						event["shortdesc"] = "null"
						event["longdesc"] = "null"
						
					self.events.append( event )
					c.close()
					
		json["events"] = self.events
		json["result"] = True

		return str( json ).replace("'", '"').replace('u"', '"').replace('"null"', 'null').replace("True", "true")
