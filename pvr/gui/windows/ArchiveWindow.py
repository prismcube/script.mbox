import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
from pvr.gui.BaseWindow import BaseWindow, Action
from ElisEnum import ElisEnum
from ElisEventBus import ElisEventBus
from ElisEventClass import *
from pvr.Util import RunThread, GuiLock, LOG_TRACE, LOG_WARN, LOG_ERR, GetSetting, SetSetting, TimeToString
from pvr.PublicReference import GetSelectedLongitudeString, EpgInfoTime, EpgInfoClock, EpgInfoComponentImage, EnumToString, ClassToList, AgeLimit
import pvr.ElisMgr
from ElisProperty import ElisPropertyEnum, ElisPropertyInt

from pvr.gui.GuiConfig import FooterMask
import threading, time, os


BUTTON_ID_VIEW_MODE				= 100
BUTTON_ID_SORT_MODE				= 101
TOGGLEBUTTON_ID_ASC				= 102
RADIIOBUTTON_ID_EXTRA			= 103
LIST_ID_RECORD					= 3400

E_VIEW_LIST						= 0
E_VIEW_THUMBNAIL				= 1
E_VIEW_POSTER_WRAP				= 2
E_VIEW_FANART					= 3
E_VIEW_END						= 4

E_SORT_DATE						= 0
E_SORT_CHANNEL					= 1
E_SORT_TITLE					= 2
E_SORT_DURATION					= 3
E_SORT_FOLDER					= 4
E_SORT_END						= 5



class ArchiveWindow(BaseWindow):

	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		self.mCommander = pvr.ElisMgr.GetInstance().GetCommander()		
		self.mEventBus = pvr.ElisMgr.GetInstance().GetEventBus()
		self.mInitialized = False
	
	def onInit(self):
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId )

		LOG_TRACE('')
		self.mRecordCount = 0
		self.mSelectedIndex = 0
		self.mRecordList = [] 
		self.mSortList = [] 		
		self.mRecordListItems = []

		LOG_TRACE('')
		self.mServiceType =  self.mCommander.Channel_GetCurrent().mServiceType
		LOG_TRACE('serviceType=%d' %self.mServiceType)		
		
		LOG_TRACE('')
		self.mViewMode = int( GetSetting( 'VIEW_MODE' ) )
		self.mCtrlViewMode = self.getControl( BUTTON_ID_VIEW_MODE )

		LOG_TRACE('')
		self.mSortMode = int( GetSetting( 'SORT_MODE' ) )		
		self.mCtrlSortMode = self.getControl( BUTTON_ID_SORT_MODE )

		self.mAscending = []
		self.mAscending = [False,False,False,False,False]
		LOG_TRACE('self.mAscending=%s' %self.mAscending )		
		self.mAscending[E_SORT_DATE] = False
		self.mAscending[E_SORT_CHANNEL] = True
		self.mAscending[E_SORT_TITLE] = True
		self.mAscending[E_SORT_DURATION] = False
		self.mAscending[E_SORT_FOLDER] = True
		LOG_TRACE('self.mAscending2=%s' %self.mAscending )				

		self.mCtrlRecordList = self.getControl( LIST_ID_RECORD )
		self.UpdateAscending()

		LOG_TRACE('')
		self.InitControl()
		LOG_TRACE('')

		self.Load( )
		LOG_TRACE('')
		try :
			self.UpdateList( )
		except Exception, ex:
			LOG_ERR( "Exception %s" %ex )
			
		LOG_TRACE('')

		
		self.mInitialized = True

	def onAction(self, aAction):
		actionId = aAction.getId()
		focusId = self.getFocusId()

		#LOG_TRACE('onAction=%d' %actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU:
			self.close( )

		elif actionId == Action.ACTION_SELECT_ITEM:
			pass

		elif actionId == Action.ACTION_PARENT_DIR :
			self.close( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT :
			pass

		elif actionId == Action.ACTION_MOVE_UP or id == Action.ACTION_MOVE_DOWN :
			pass

		
	def onClick(self, aControlId):
		LOG_TRACE( 'aControlId=%d' %aControlId )

		if aControlId == BUTTON_ID_VIEW_MODE :
			self.mViewMode += 1
			if self.mViewMode >= E_VIEW_END :
				self.mViewMode = 0 

			SetSetting( 'VIEW_MODE','%d' %self.mViewMode ) 				
			self.UpdateViewMode( )
			self.UpdateList( )
		
		elif aControlId == BUTTON_ID_SORT_MODE :
			self.mSortMode += 1
			if self.mSortMode >= E_SORT_END :
				self.mSortMode = 0 
				
			SetSetting( 'SORT_MODE','%d' %self.mSortMode ) 								
			self.UpdateSortMode( )
			self.UpdateAscending( )
			self.UpdateList( )

		elif aControlId == TOGGLEBUTTON_ID_ASC :
			LOG_TRACE('Mode=%d' % self.mSortMode )
			LOG_TRACE('mAscending=%d' %self.mAscending[self.mSortMode] )
			if self.mAscending[self.mSortMode] == True :
				self.mAscending[self.mSortMode] = False
			else :
				self.mAscending[self.mSortMode] = True

			self.UpdateAscending( )
			self.UpdateList( )

		elif aControlId == RADIIOBUTTON_ID_EXTRA :
			pass
		


	def onFocus(self, controlId):

		if self.mInitialized == False :
			return


	@GuiLock
	def onEvent(self, aEvent):
		pass


	def InitControl( self ) :

		if self.mViewMode == E_VIEW_LIST :
			self.mCtrlViewMode.setLabel('VIEW: LIST')
		elif self.mViewMode == E_VIEW_THUMBNAIL :			
			self.mCtrlViewMode.setLabel('VIEW: THUMBNAIL')		
		elif self.mViewMode == E_VIEW_POSTER_WRAP :			
			self.mCtrlViewMode.setLabel('VIEW: POSTER_WRAP')		
		elif self.mViewMode == E_VIEW_FANART :			
			self.mCtrlViewMode.setLabel('VIEW: FANART')		
		else :
			LOG_WARN('Unknown view mode')
			
		if self.mSortMode == E_SORT_DATE :
			self.mCtrlSortMode.setLabel('SORT: DATE')
		elif self.mSortMode == E_SORT_CHANNEL :			
			self.mCtrlSortMode.setLabel('SORT: CHANNEL')		
		elif self.mSortMode == E_SORT_TITLE :			
			self.mCtrlSortMode.setLabel('SORT: TITLE')		
		elif self.mSortMode == E_SORT_DURATION :			
			self.mCtrlSortMode.setLabel('SORT: DURATION')		
		elif self.mSortMode == E_SORT_FOLDER :			
			self.mCtrlSortMode.setLabel('SORT: FOLDER')		
		else :
			LOG_WARN('Unknown sort mode')


	def UpdateViewMode( self ) :
		LOG_TRACE('---------------------')
		self.InitControl()


	def UpdateSortMode( self ) :
		LOG_TRACE('---------------------')
		self.InitControl()		

	def UpdateAscending( self ) :
		LOG_TRACE('--------------------- %d ' %self.mAscending[self.mSortMode])	
		if self.mAscending[self.mSortMode] == True :
			self.mWin.setProperty( 'ascending', 'true' )
		else :
			self.mWin.setProperty( 'ascending', 'false' )
	

	def Flush( self ) :
		self.mRecordCount = 0
		self.mRecordList = []
		self.mSortList = []		


	def Load( self ) :

		LOG_TRACE('----------------------------------->')
		self.mRecordCount = self.mCommander.Record_GetCount( self.mServiceType )
		
		LOG_TRACE('')
		LOG_TRACE('RecordCount=%d' %self.mRecordCount )
		
		for i in range( self.mRecordCount ) :
			LOG_TRACE('i=%d' %i)		
			recInfo = self.mCommander.Record_GetRecordInfo( i, self.mServiceType )
			recInfo.printdebug()
			self.mRecordList.append( recInfo )


	def UpdateList( self ) :
		LOG_TRACE('')
		if self.mSortMode == E_SORT_DATE :
			self.mRecordList.sort( self.ByDate )
		elif self.mSortMode == E_SORT_CHANNEL :
			self.mRecordList.sort( self.ByChannel )

		elif self.mSortMode == E_SORT_TITLE :
			self.mRecordList.sort( self.ByTitle )

		elif self.mSortMode == E_SORT_DURATION :
			self.mRecordList.sort( self.ByDuration )

		elif self.mSortMode == E_SORT_FOLDER :
			self.ByFolder( )
		else :
			LOG_WARN('Unknown sort mode')		
			self.mSortMode = 0
			self.mRecordList.sort( self.ByDate )

		LOG_TRACE('')			
		if self.mAscending[self.mSortMode] == False :
			self.mRecordList.reverse()

		LOG_TRACE('')
		
		self.mRecordListItems = []
		for i in range( len( self.mRecordList ) ) :
			LOG_TRACE('---------->i=%d' %i)		
			recInfo = self.mRecordList[i]
			recInfo.printdebug()
			channelName = 'P%04d.%s' %(recInfo.mChannelNo, recInfo.mChannelName)
			#recItem = xbmcgui.ListItem( '1234567890abcdefghijklmnopqrstuvwxyz123456789abcdefghijklmnopqrstuvwxyz', '1234567890abcdefghijklmnopqrstuvwxyz123456789abcdefghijklmnopqrstuvwxyz' )
			recItem = xbmcgui.ListItem( channelName, recInfo.mRecordName )			
			recItem.setProperty('RecIcon', 'RecIconSample.jpg')

			recItem.setProperty('RecDate', TimeToString( recInfo.mStartTime ))
			recItem.setProperty('RecDuration', '%dm' %( recInfo.mDuration/60 ) )
			self.mRecordListItems.append( recItem )

		LOG_TRACE('')
		self.mCtrlRecordList.addItems( self.mRecordListItems )


	def ByDate( self, aRec1, aRec2 ) :
		return cmp( aRec1.StartTime, aRec2.StartTime )
		

	def ByChannel( self, aRec1, aRec2 ) :
		return cmp( aRec1.ChannelNo, aRec2.ChannelNo )


	def ByTitle( self, aRec1, aRec2 ) :
		return cmp( aRec1.RecordName, aRec2.RecordName )


	def ByDuration( self, aRec1, aRec2 ) :
		return cmp( aRec1.Duration, aRec2.Duration )


	def ByFolder( self ): #ToDO : 
		pass


	@RunThread
	def CurrentTimeThread(self):
		pass


	@GuiLock
	def UpdateLocalTime( self ) :
		pass


		"""
		try:
			self.mLocalTime = self.mCommander.Datetime_GetLocalTime( )


			if self.mNavEpg :
				endTime = self.mNavEpg.mStartTime + self.mNavEpg.mDuration
		
				pastDuration = endTime - self.mLocalTime
				if pastDuration < 0 :
					pastDuration = 0

				if self.mNavEpg.mDuration > 0 :
					percent = pastDuration * 100/self.mNavEpg.mDuration
				else :
					percent = 0

				#print 'percent=%d' %percent
				self.mCtrlProgress.setPercent( percent )

		except Exception, e :
			print '[%s:%s] Error exception[%s]'% (	\
				self.__file__,						\
				currentframe().f_lineno,			\
				e )

			self.mLocalTime = 0
		"""

