from datetime import datetime
from webinterface import Webinterface
import dbopen

"""
IEPGEvent structure

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

class ElmoEpgNow( Webinterface ) :

	def __init__(self, urlPath) :

		super(ElmoEpgNow, self).__init__(urlPath)
		self.currenttime = self.mCommander.Datetime_GetLocalTime()
		self.noResult = False; 
		
		if 'bRef' in self.params: 
			self.ref = self.unMakeRef( self.params['bRef'] ); 

			if self.ref['comment'] != '' :
			
				# get services in the bouquet 
				# datebaseName_columnName_value 
				# condition[0] ==> database name
				# condition[1] ==> column name
				# condition[2] ==> value 
				self.conn = dbopen.DbOpen('channel.db').getConnection()
				self.c = self.conn.cursor()

				condition = self.ref['comment'].split('_')
				sql = "select sid, tsid, nid, onid, name from " + condition[0] + " where " + condition[1] + " = '" + condition[2] + "'"
				print sql
				
				self.c.execute(sql) 
				self.services = self.c.fetchall()

		else :
			self.noResult = True;
					
	def xmlResult(self) :

		xmlStr = ''
		xmlStr += '<?xml version="1.0" encoding="UTF-8"?>\n'
		xmlStr += '<e2eventlist>\n'

		if self.noResult == True :
			xmlStr += '</e2eventlist>\n'
			return xmlStr

		try :

			for service in self.services :

				# def Epgevent_GetCurrent( self, aSid, aTsid, aOnid ) :
				
				sid = 	service[0]
				tsid = 	service[1]
				onid =	service[3]
				name =	service[4]

				print sid, tsid, onid
				
				info = self.mDataCache.Epgevent_GetCurrent( sid, tsid, onid )

				if info == None :  # no EPG infomation 
					xmlStr += '<e2event>\n'
					xmlStr += '<e2eventid>None</e2eventid>\n'
					xmlStr += '<e2eventstart>None</e2eventstart>\n'
					xmlStr += '<e2eventduration>None</e2eventduration>\n'
					xmlStr += '<e2eventcurrenttime>' + str(self.currenttime) + '</e2eventcurrenttime>\n'
					xmlStr += '<e2eventtitle>None</e2eventtitle>\n'
					xmlStr += '<e2eventdescription>None</e2eventdescription>\n'
					xmlStr += '<e2eventdescriptionextended>None</e2eventdescriptionextended>\n'
					xmlStr += '<e2eventservicereference>' + self.makeRef( sid, tsid, onid ) + '</e2eventservicereference>\n'  	# def makeRef(self, sid, tsid, onid) :
					xmlStr += '<e2eventservicename>' + name + '</e2eventservicename>\n'
					xmlStr += '</e2event>\n'
				else : 
					xmlStr += '<e2event>\n'
					xmlStr += '<e2eventid>\n'
					xmlStr += 	info.mEventIdEPG
					xmlStr += '</e2eventid>\n'
					xmlStr += '<e2eventstart>\n'
					xmlStr += 	''
					xmlStr += '</e2eventstart>\n'
					xmlStr += '<e2eventduration>\n'
					xmlStr += 	''
					xmlStr += '</e2eventduration>\n'
					xmlStr += '<e2eventcurrenttime>\n'
					xmlStr += 	''
					xmlStr += '</e2eventcurrenttime>\n'
					xmlStr += '<e2eventtitle>\n'
					xmlStr += 	''
					xmlStr += '</e2eventtitle>\n'
					xmlStr += '<e2eventdescription>\n'
					xmlStr += 	''
					xmlStr += '</e2eventdescription>\n'
					xmlStr += '<e2eventdescriptionextended>\n'
					xmlStr += 	'' 
					xmlStr += '</e2eventdescriptionextended>\n'
					xmlStr += '<e2eventservicereference>\n'
					xmlStr += 	 self.makeRef( sid, tsid, onid )  	# def makeRef(self, sid, tsid, onid) :
					xmlStr += '</e2eventservicereference>\n'
					xmlStr += '<e2eventservicename>' + name + '</e2eventservicename>\n'
					xmlStr += '</e2event>\n'
					
				
			xmlStr += '</e2eventlist>\n'
			return xmlStr
				
		except Exception, e :

			xmlStr += '</e2eventlist>'
			print str(e)
			
			return xmlStr
		
