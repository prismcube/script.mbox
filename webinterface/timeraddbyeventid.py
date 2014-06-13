import dbopen
from webinterface import Webinterface
from pvr.gui.WindowImport import *

class ElmoTimerAddByEventId( Webinterface ) :

	def __init__(self, urlPath) :
		super(ElmoTimerAddByEventId, self).__init__(urlPath)
		print self.params['sRef']

	def xmlResult(self) :

		xmlstr = '<?xml version="1.0" encoding="UTF-8"?>\n'
		xmlstr += '<e2implexmlresult>\n'

		self.conn = dbopen.DbOpen('timer.db').getConnection()
		sql = "select key from tblTimer where EventId = " + self.params['eventid']
		self.c = self.conn.cursor()
		self.c.execute(sql)

		self.result = self.c.fetchall()
		if self.result :
			xmlstr += '<e2state>\n'
			xmlstr += '	false	\n'
			xmlstr += '</e2state>\n'
			xmlstr += '<e2statetext>\n'
			xmlstr += '	Already in Timer List\n'
			xmlstr += '</e2statetext>\n'
			xmlstr += '</e2implexmlresult>\n'

			return xmlstr
		
		if not HasAvailableRecordingHDD( ) :

			xmlstr += '<e2state>\n'
			xmlstr += '	false	\n'
			xmlstr += '</e2state>\n'
			xmlstr += '<e2statetext>\n'
			xmlstr += '	No HDD Available\n'
			xmlstr += '</e2statetext>\n'
			xmlstr += '</e2implexmlresult>\n'
			
			return xmlstr

		sRef = self.unMakeRef( self.params['sRef'] )
		# aEPG = self.mDataCache.Epgevent_GetCurrent( sRef['sid'], sRef['tsid'], sRef['onid'] )
		gmtFrom = self.mDataCache.Datetime_GetLocalTime() - 3600 * 2
		gmtUntil = gmtFrom + (3600*24*7)
		maxCount = 100
		
		epgList = self.mCommander.Epgevent_GetList( sRef['sid'], sRef['tsid'], sRef['onid'], gmtFrom, gmtUntil, maxCount )
	
		aEPG = None 
		
		for epg in epgList :
			if epg.mEventId == int(self.params['eventid']) :
				aEPG = epg
				break
			
		try :	
			if aEPG :
				localOffset = self.mDataCache.Datetime_GetLocalOffset( )
				expire  = aEPG.mStartTime + aEPG.mDuration + localOffset
				
				if expire <=  self.mDataCache.Datetime_GetLocalTime( ) :
					"""
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG('Error'), MR_LANG("That programme has already finished"))
					dialog.doModal( )
					"""
					xmlstr += '<e2state>\n'
					xmlstr += '	false	\n'
					xmlstr += '</e2state>\n'
					xmlstr += '<e2statetext>\n'
					xmlstr += '	That program has already finished\n'
					xmlstr += '</e2statetext>\n'
					xmlstr += '</e2implexmlresult>\n'

					return xmlstr

			else :
				xmlstr += '<e2state>\n'
				xmlstr += '	false	\n'
				xmlstr += '</e2state>\n'
				xmlstr += '<e2statetext>\n'
				xmlstr += '	EPG Fetch Error No Such EPG\n'
				xmlstr += '</e2statetext>\n'
				xmlstr += '</e2implexmlresult>\n'

				return xmlstr 
				

		except Exception, ex :
		
			LOG_ERR( "Exception %s" %ex )

			xmlstr += '<e2state>\n'
			xmlstr += '	false	\n'
			xmlstr += '</e2state>\n'
			xmlstr += '<e2statetext>\n'
			xmlstr += '	EPG Fetch Error %s\n' %ex
			xmlstr += '</e2statetext>\n'
			xmlstr += '</e2implexmlresult>\n'

			return xmlstr

		try :
			ret = self.mDataCache.Timer_AddEPGTimer( True, 0, aEPG )
			LOG_ERR( 'Conflict ret=%s' %ret )
			if ret and (ret[0].mParam == -1 or ret[0].mError == -1) :

				xmlstr += '<e2state>\n'
				xmlstr += '	false	\n'
				xmlstr += '</e2state>\n'
				xmlstr += '<e2statetext>\n'
				xmlstr += '	Record Conflict\n'
				xmlstr += '</e2statetext>\m'
				xmlstr += '</e2implexmlresult>\n'

			else :
			
				xmlstr += '<e2state>\n'
				xmlstr += '	true	\n'
				xmlstr += '</e2state>\n'
				xmlstr += '<e2statetext>\n'
				xmlstr += '	Record Good\n'
				xmlstr += '</e2statetext>\n'
				xmlstr += '</e2implexmlresult>\n'

		except Exception, ex :
		
			LOG_ERR( "Exception %s" %ex )
			xmlstr += '<e2state>\n'
			xmlstr += '	false	\n'
			xmlstr += '</e2state>\n'
			xmlstr += '<e2statetext>\n'
			xmlstr += '	Timer Error %s\n' %ex
			xmlstr += '</e2statetext>\n'
			xmlstr += '</e2implexmlresult>\n'

		return xmlstr 
