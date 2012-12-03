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

class ElmoEpgNext( Webinterface ) :

	def __init__(self, urlPath) :

		super(ElmoEpgNext, self).__init__(urlPath)
		self.currenttime = self.mCommander.Datetime_GetLocalTime()
		self.services = []

		if 'bRef' in self.params: 
			
			ref = self.unMakeRef( self.params['bRef'] ); 
			if ref :

				self.connFav = dbopen.DbOpen('channel.db').getConnection()	
				
				# get services in the bouquet 
				condition = ref['comment'].split('_')
				sql = "select GroupName, sid, tsid, nid, onid from " + condition[0] + " where  " + condition[1] + " = '" + condition[2] + "'"
				
				self.cFav = self.connFav.cursor()
				self.cFav.execute(sql)
				stations = self.cFav.fetchall()
				
				for station in stations :
				
					connEpg = dbopen.DbOpen('epg.db').getConnection()
					c = connEpg.cursor()
					
					sql = "select eventid, starttime, duration, eventName, eventDescription from tblEpg where sid=" + str( station[1] ) + " and tsid=" + str( station[2] ) + " and onid=" + str( station[4] )
					sql += " and starttime > " + str( self.currenttime ) + " order by starttime limit 1 "

					print sql
			
					c.execute(sql)		
					epg = c.fetchone()

					if epg :
						temp = {}
						temp['eventid'] = epg[0]
						temp['starttime'] = epg[1]
						temp['duration'] = epg[2]
						temp['eventName'] = epg[3]
						temp['eventDescription'] = epg[4]

						temp['sid'] = station[1]
						temp['tsid'] = station[2]
						temp['onid'] = station[4]

						self.services.append(temp)
						
		
				print self.services
				print len(self.services)


	def xmlResult(self) :

		xmlStr = ''
		xmlStr += '<?xml version="1.0" encoding="UTF-8"?> '
		xmlStr += '<e2eventlist> '

		for row in self.services :

			conn = dbopen.DbOpen('channel.db').getConnection()
			c = conn.cursor()

			sql = "select name from tblChannel where sid=" + str( row['sid'] )  + " and tsid=" + str( row['tsid'] ) + " and onid=" + str( row['onid'] )
			c.execute(sql)

			print sql

			result = c.fetchone()
			if result == None :
				serviceName = 'Unknown'
			else :
				serviceName = result[0]
				
			xmlStr += '<e2event> '
			xmlStr += '<e2eventid> '
			xmlStr += 	str( row['eventid'] )
			xmlStr += '</e2eventid> '
			xmlStr += '<e2eventstart> '
			xmlStr += 	str( row['starttime'] )
			xmlStr += '</e2eventstart> '
			xmlStr += '<e2eventduration> '
			xmlStr += 	str( row['duration'] )
			xmlStr += '</e2eventduration> '
			xmlStr += '<e2eventcurrenttime> '
			xmlStr += 	str( self.currenttime )
			xmlStr += '</e2eventcurrenttime> '
			xmlStr += '<e2eventtitle> '
			xmlStr += 	row['eventName']
			xmlStr += '</e2eventtitle> '
			xmlStr += '<e2eventdescription> '
			xmlStr += 	row['eventDescription']
			# xmlStr += 	row[4]
			xmlStr += '</e2eventdescription> '
			xmlStr += '<e2eventdescriptionextended> '
			xmlStr += 	'' 
			xmlStr += '</e2eventdescriptionextended> '
			xmlStr += '<e2eventservicereference> '
			xmlStr += 	 self.makeRef( row['sid'], row['tsid'], row['onid'] )  	# def makeRef(self, sid, tsid, onid) :
			xmlStr += '</e2eventservicereference> '
			xmlStr += '<e2eventservicename> '
			xmlStr += 	serviceName
			xmlStr += '</e2eventservicename> '
			xmlStr += '</e2event> '
			
			conn.close()
	
		xmlStr += '</e2eventlist> '
		return xmlStr
		
