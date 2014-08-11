import dbopen
from webinterface import Webinterface
from xml.sax.saxutils import escape

class ElmoTimerList( Webinterface ) :

	def __init__(self, urlPath) :
	
		super(ElmoTimerList, self).__init__(urlPath)
		self.timerList = self.mDataCache.Timer_GetTimerList()

	def xmlResult(self) :

		xmlstr = '<?xml version="1.0" encoding="UTF-8" ?>'
		xmlstr += '<e2timerlist>\n'
		
		for info in self.timerList :

			xmlstr += '<e2timer>\n'

			sRef = self.makeRef( info.mSid, info.mTsid, info.mOnid )
			
			xmlstr +=		'<e2servicereference>%s</e2servicereference>\n' % sRef
			xmlstr +=		'<e2servicename>%s</e2servicename>\n' % info.mName
			xmlstr +=		'<e2eit>%s</e2eit>\n' % str(info.mRecordKey)
			xmlstr +=		'<e2name>%s</e2name>\n' % escape(info.mName)
			xmlstr +=		'<e2description></e2description>\n'
			xmlstr +=		'<e2descriptionextended></e2descriptionextended>\n'
			xmlstr +=		'<e2disabled>0</e2disabled>\n'
			xmlstr +=		'<e2timebegin>%s</e2timebegin>\n' % str(info.mStartTime)
			xmlstr +=		'<e2timeend>%s</e2timeend>\n' % str(info.mStartTime + info.mDuration) 
			xmlstr +=		'<e2duration>%s</e2duration>\n' % str(info.mDuration)
			xmlstr +=		'<e2startprepare>%s</e2startprepare>\n' % str(info.mStartTime - 20)
			xmlstr += 		'<recordkey>%s</recordkey>\n' % str(info.mTimerId)

			if info.mTimerType == 7 :
				xmlstr +=	'<e2justplay>1</e2justplay>\n' 
			else :
				xmlstr +=	'<e2justplay>0</e2justplay>\n' 
				
			xmlstr +=		'<e2afterevent>0</e2afterevent>\n'
			xmlstr +=		'<e2location>None</e2location>\n'
			xmlstr +=		'<e2tags></e2tags>\n'
			xmlstr +=		'<e2logentries>[PrismCube Timer List]</e2logentries>\n'
			xmlstr +=		'<e2filename></e2filename>\n'
			xmlstr +=		'<e2backoff>0</e2backoff>\n'
			xmlstr +=		'<e2nextactivation></e2nextactivation>\n'
			xmlstr +=		'<e2firsttryprepare>True</e2firsttryprepare>\n'
			xmlstr +=		'<e2state>0</e2state>'

			if info.mTimerType == 2 :
				xmlstr +=	'<e2repeated>1</e2repeated>\n'
			else :
				xmlstr +=	'<e2repeated>0</e2repeated>\n'
				
			xmlstr +=		'<e2dontsave>0</e2dontsave>\n'
			xmlstr +=		'<e2cancled>Flase</e2cancled>\n'
			xmlstr +=		'<e2toggledisabled>1</e2toggledisabled>\n'
			xmlstr +=		'<e2toggledisabledimg>off</e2toggledisabledimg>\n'
			
			xmlstr +=	'</e2timer>\n'

		xmlstr += '</e2timerlist>\n'
		return xmlstr
