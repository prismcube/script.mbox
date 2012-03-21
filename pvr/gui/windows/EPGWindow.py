import xbmc
import xbmcgui
import sys
import time

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.BaseWindow import BaseWindow, Action
from pvr.gui.GuiConfig import *
from ElisEnum import ElisEnum
from ElisEventBus import ElisEventBus
from ElisEventClass import *
from pvr.Util import RunThread, GuiLock, GuiLock2, LOG_TRACE, LOG_WARN, LOG_ERR, GetSetting, SetSetting, TimeToString, TimeFormatEnum
from pvr.PublicReference import GetSelectedLongitudeString, EpgInfoTime, EpgInfoClock, EpgInfoComponentImage, EnumToString, ClassToList, AgeLimit
import pvr.ElisMgr
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
import threading, time, os


BUTTON_ID_EPG_MODE				= 100
RADIIOBUTTON_ID_EXTRA			= 101
LIST_ID_COMMON_EPG				= 3500
LIST_ID_BIG_EPG					= 3510

E_VIEW_CHANNEL					= 0
E_VIEW_CURRENT					= 1
E_VIEW_FOLLOWING				= 2
E_VIEW_END						= 3


E_MAX_EPG_COUNT					= 512
E_MAX_SCHEDULE_DAYS				= 8


CONTEXT_ADD_TIMER				= 0
CONTEXT_EDIT_TIMER				= 1
CONTEXT_DELETE_TIMER			= 2
CONTEXT_EXTEND_INFOMATION		= 3
CONTEXT_SEARCH					= 4



class EPGWindow(BaseWindow):

	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)

	
	def onInit(self):
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId )

		self.SetPipScreen( )
		self.getControl( E_SETTING_MINI_TITLE ).setLabel( 'EPG' )

		LOG_TRACE('')
		self.mEPGCount = 0
		self.mSelectedIndex = 0
		self.mEPGList = [] 
		self.mListItems = []
		self.mTimerList = []

		LOG_TRACE('')
		self.mEPGMode = int( GetSetting( 'EPG_MODE' ) )
		self.mCtrlEPGMode = self.getControl( BUTTON_ID_EPG_MODE )

		self.mCtrlList = self.getControl( LIST_ID_COMMON_EPG )
		self.mCtrlBigList = self.getControl( LIST_ID_BIG_EPG )
		self.UpdateViewMode( )
		
		LOG_TRACE('')
		self.InitControl()
		LOG_TRACE('')

		self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( )
		self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
		LOG_TRACE('ZeppingMode(%d,%d,%d)' %( self.mCurrentMode.mServiceType, self.mCurrentMode.mMode, self.mCurrentMode.mSortingMode ) )
		#self.mChannelList = self.mDataCache.Channel_GetList( self.mCurrentMode.mServiceType, self.mCurrentMode.mMode, self.mCurrentMode.mSortingMode )
		self.mChannelList = self.mDataCache.Channel_GetList( )

		LOG_TRACE("ChannelList=%d" %len(self.mChannelList) )
		
		self.mSelectChannel = self.mCurrentChannel
		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		self.mGMTTime = 0
		LOG_TRACE('CHANNEL current=%s select=%s' %( self.mCurrentChannel, self.mSelectChannel ))

		self.Load( )
		LOG_TRACE('')
		self.UpdateList( )
		LOG_TRACE('')

		
		self.mInitialized = True

	def onAction( self, aAction ) :
		self.GetFocusId()
		actionId = aAction.getId( )
		self.GlobalAction( actionId )

		
		#LOG_TRACE('onAction=%d' %actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.SetVideoRestore( )
			self.close( )

		elif  actionId == Action.ACTION_SELECT_ITEM :
			if self.mFocusId == LIST_ID_BIG_EPG :
				self.Tune( )
	
		elif actionId == Action.ACTION_PARENT_DIR :
			self.SetVideoRestore( )
			self.close( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT :
			pass

		elif actionId == Action.ACTION_MOVE_UP or id == Action.ACTION_MOVE_DOWN :
			pass

		elif actionId == Action.ACTION_CONTEXT_MENU:
			LOG_TRACE('')
			self.ShowContextMenu( )


	def onClick(self, aControlId):
		LOG_TRACE( 'aControlId=%d' %aControlId )

		if aControlId == BUTTON_ID_EPG_MODE :
			self.mEPGMode += 1
			if self.mEPGMode >= E_VIEW_END :
				self.mEPGMode = 0 

			SetSetting( 'EPG_MODE','%d' %self.mEPGMode )
			self.UpdateViewMode( )
			self.InitControl( )
			self.Load( )
			self.UpdateList( )
		
		elif aControlId == RADIIOBUTTON_ID_EXTRA :
			pass

		elif aControlId == LIST_ID_COMMON_EPG :
			pass


	def onFocus(self, controlId):

		if self.mInitialized == False :
			return


	@GuiLock
	def onEvent(self, aEvent):
		pass


	def InitControl( self ) :

		if self.mEPGMode == E_VIEW_CHANNEL :
			self.mCtrlEPGMode.setLabel('VIEW: CHANNEL')
		elif self.mEPGMode == E_VIEW_CURRENT :			
			self.mCtrlEPGMode.setLabel('VIEW: CURRENT')		
		elif self.mEPGMode == E_VIEW_FOLLOWING :			
			self.mCtrlEPGMode.setLabel('VIEW: FOLLOWING')		
		else :
			LOG_WARN('Unknown epg mode')
			

	def UpdateViewMode( self ) :
		LOG_TRACE('---------------------')
		if self.mEPGMode == E_VIEW_CHANNEL :
			self.mWin.setProperty( 'EPGMode', 'channel' )
		elif self.mEPGMode == E_VIEW_CURRENT :			
			self.mWin.setProperty( 'EPGMode', 'current' )
		elif self.mEPGMode == E_VIEW_FOLLOWING :			
			self.mWin.setProperty( 'EPGMode', 'following' )
		else :
			self.mEPGMode = E_VIEW_LIST 		
			self.mWin.setProperty( 'EPGMode', 'channel' )
		

	def Flush( self ) :
		self.mEPGCount = 0
		self.mEPGList = []


	def Load( self ) :

		LOG_TRACE('----------------------------------->')
		self.mGMTTime = self.mDataCache.Datetime_GetGMTTime( )
		self.mEPGList = []
		
		if self.mEPGMode == E_VIEW_CHANNEL :
			self.LoadByChannel( )
		elif self.mEPGMode == E_VIEW_CURRENT :			
			self.LoadByCurrent( )
		elif self.mEPGMode == E_VIEW_FOLLOWING :			
			self.LoadByFollowing( )
		else :
			self.mEPGMode = E_VIEW_CHANNEL 		
			self.LoadByChannel( )


	def LoadByChannel( self ):
		LOG_TRACE('')

		gmtFrom =  self.mGMTTime 
		gmtUntil = self.mGMTTime + E_MAX_SCHEDULE_DAYS*3600*24

		try :
			self.mEPGList = self.mDataCache.Epgevent_GetListByChannel(  self.mSelectChannel.mSid,  self.mSelectChannel.mTsid,  self.mSelectChannel.mOnid,  gmtFrom,  gmtUntil,  E_MAX_EPG_COUNT)

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)

		if self.mEPGList == None or self.mEPGList[0].mError != 0 :
			self.mEPGList = []
			return

		LOG_TRACE('self.mEPGList COUNT=%d' %len(self.mEPGList ))
		


	def LoadByCurrent( self ):
		try :
			self.mEPGList=self.mDataCache.Epgevent_GetCurrentList()

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)
	

	def LoadByFollowing( self ):

		try :
			self.mEPGList=self.mDataCache.Epgevent_GetFollowingList()

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)

		LOG_TRACE('self.mEPGList COUNT=%d' %len(self.mEPGList ))


	def UpdateList( self ) :
		LOG_TRACE('')
		self.mListItems = []
		self.LoadTimerList( )


		if self.mEPGMode == E_VIEW_CHANNEL :
			try :		
				for i in range( len( self.mEPGList ) ) :
					epgEvent = self.mEPGList[i]
					#epgEvent.printdebug()
					listItem = xbmcgui.ListItem( TimeToString( epgEvent.mStartTime + self.mLocalOffset, TimeFormatEnum.E_HH_MM ), epgEvent.mEventName )
					if epgEvent.mHasTimer : 
						listItem.setProperty( 'HasTimer', 'true' )
					else :
						if self.HasIntersectionRecording( epgEvent ) == True :
							listItem.setProperty( 'HasTimer', 'true' )							
						else :
							listItem.setProperty( 'HasTimer', 'false' )
	 
					self.mListItems.append( listItem )

				self.mCtrlList.addItems( self.mListItems )
				self.setFocusId( LIST_ID_COMMON_EPG )
			except Exception, ex :
				LOG_ERR( "Exception %s" %ex)


		elif self.mEPGMode == E_VIEW_CURRENT :
			for i in range( len( self.mChannelList ) ) :
				channel = self.mChannelList[i]
				tempChannelName = '%04d %s' %( channel.mNumber, channel.mName )
				hasEpg = False

				try :
					epgEvent = self.GetEPGByIds( channel.mSid, channel.mTsid, channel.mOnid )

					if epgEvent :
						hasEpg = True
						listItem = xbmcgui.ListItem( tempChannelName, epgEvent.mEventName )
						epgStart = epgEvent.mStartTime + self.mLocalOffset
						tempName = '%s~%s' %(TimeToString( epgStart, TimeFormatEnum.E_HH_MM ), TimeToString( epgStart + epgEvent.mDuration, TimeFormatEnum.E_HH_MM ) )
						listItem.setProperty( 'Duration', tempName )
						listItem.setProperty( 'HasEvent', 'true' )
 
						if epgEvent.mHasTimer : 
							listItem.setProperty( 'HasTimer', 'true' )
						else :
							if self.HasIntersectionRecording( epgEvent ) == True :
								listItem.setProperty( 'HasTimer', 'true' )							
							else :
								listItem.setProperty( 'HasTimer', 'false' )
						
					else :
						listItem = xbmcgui.ListItem( tempChannelName, 'No Event' )
						listItem.setProperty( 'Duration', '' )
						listItem.setProperty( 'HasEvent', 'false' )
						
						if self.HasManualRecording( channel ) == True : 
							listItem.setProperty( 'HasTimer', 'true' )
						else :
							listItem.setProperty( 'HasTimer', 'false' )


					#ListItem.PercentPlayed
					self.mListItems.append( listItem )

				except Exception, ex :
					LOG_ERR( "Exception %s" %ex)

			self.mCtrlBigList.addItems( self.mListItems )
			self.setFocusId( LIST_ID_BIG_EPG )

		elif self.mEPGMode == E_VIEW_FOLLOWING :
			for i in range( len( self.mChannelList ) ) :
				channel = self.mChannelList[i]
				tempChannelName = '%04d %s' %( channel.mNumber, channel.mName )
				hasEpg = False

				try :
					epgEvent = self.GetEPGByIds( channel.mSid, channel.mTsid, channel.mOnid )

					if epgEvent :
						hasEpg = True
						listItem = xbmcgui.ListItem( tempChannelName, epgEvent.mEventName )
						epgStart = epgEvent.mStartTime + self.mLocalOffset
						tempName = '%s~%s' %(TimeToString( epgStart, TimeFormatEnum.E_HH_MM ), TimeToString( epgStart + epgEvent.mDuration, TimeFormatEnum.E_HH_MM ) )
						listItem.setProperty( 'Duration', tempName )
						listItem.setProperty( 'HasEvent', 'true' )
 
						if epgEvent.mHasTimer : 
							listItem.setProperty( 'HasTimer', 'true' )
						else :
							if self.HasIntersectionRecording( epgEvent ) == True :
								listItem.setProperty( 'HasTimer', 'true' )							
							else :
								listItem.setProperty( 'HasTimer', 'false' )

						
					else :
						listItem = xbmcgui.ListItem( tempChannelName, 'No Event' )
						listItem.setProperty( 'Duration', '' )
						listItem.setProperty( 'HasEvent', 'false' )
 
						if self.HasManualRecording( channel ) == True :
							listItem.setProperty( 'HasTimer', 'true' )
						else :
							listItem.setProperty( 'HasTimer', 'false' )

					#ListItem.PercentPlayed
					self.mListItems.append( listItem )

				except Exception, ex :
					LOG_ERR( "Exception %s" %ex)

			self.mCtrlBigList.addItems( self.mListItems )
			self.setFocusId( LIST_ID_BIG_EPG )


		LOG_TRACE('')



	def GetEPGByIds( self, aSid, aTsid, aOnid ) :
		if self.mEPGList == None :
			return None

		for i in range( len( self.mEPGList ) ) :
			epgEvent = self.mEPGList[i]
			if epgEvent.mSid == aSid and epgEvent.mTsid == aTsid and epgEvent.mOnid == aOnid :
				return epgEvent

		return None


	@RunThread
	def CurrentTimeThread(self):
		pass


	@GuiLock
	def UpdateLocalTime( self ) :
		pass


		"""
		try:
			self.mLocalTime = self.mDataCache.Datetime_GetLocalTime( )


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


	def ShowContextMenu( self ) :
		LOG_TRACE('')
		selectedEPG = self.GetSelectedEPG()
		context = []

		LOG_TRACE('')
		if selectedEPG :
			LOG_TRACE('')		
			if selectedEPG.mHasTimer :
				LOG_TRACE('')			
				context.append( ContextItem( 'Edit Timer', CONTEXT_EDIT_TIMER ) )
				context.append( ContextItem( 'Delete Timer', CONTEXT_DELETE_TIMER ) )
			else :
				LOG_TRACE('')
				if self.HasIntersectionRecording( selectedEPG ) == True :
					context.append( ContextItem( 'Edit Timer', CONTEXT_EDIT_TIMER ) )
					context.append( ContextItem( 'Delete Timer', CONTEXT_DELETE_TIMER ) )
				else:
					context.append( ContextItem( 'Add Timer', CONTEXT_ADD_TIMER ) )

			context.append( ContextItem( 'Extend Infomation', CONTEXT_EXTEND_INFOMATION ) )		
			

		else :
			LOG_TRACE('')		
			hasManualRecording = False

			if self.mEPGMode == E_VIEW_CURRENT or self.mEPGMode == E_VIEW_FOLLOWING :				
				LOG_TRACE('')			
				selectedPos = self.mCtrlBigList.getSelectedPosition()
				if selectedPos >= 0 and selectedPos < len( self.mChannelList ) :
					channel = self.mChannelList[ selectedPos ]
					hasManualRecording = self.HasManualRecording( channel )					

			if hasManualRecording == True :
				LOG_TRACE('')			
				context.append( ContextItem( 'Edit Timer', CONTEXT_EDIT_TIMER ) )
				context.append( ContextItem( 'Delete Timer', CONTEXT_DELETE_TIMER ) )
			else :
				LOG_TRACE('')			
				context.append( ContextItem( 'Add Timer', CONTEXT_ADD_TIMER ) )
				

		GuiLock2( True )
		dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
		dialog.doModal( )
		GuiLock2( False )
		
		contextAction = dialog.GetSelectedAction()
		self.DoContextAction( contextAction ) 


	def DoContextAction( self, aContextAction ) :
		LOG_TRACE('aContextAction=%d' %aContextAction )

		if aContextAction == CONTEXT_ADD_TIMER :
			self.ShowAddTimer( )

		elif aContextAction == CONTEXT_EDIT_TIMER :
			self.ShowEditTimer( )

		elif aContextAction == CONTEXT_DELETE_TIMER :
			self.ShowDeleteConfirm( )

		elif aContextAction == CONTEXT_EXTEND_INFOMATION :
			self.ShowDetailInfomation( )


	def ShowAddTimer( self ) :
		LOG_TRACE('ShowAddTimer')
		epg = self.GetSelectedEPG( )
		try :
			GuiLock2( True )
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_ADD_TIMER )
			dialog.SetEPG( epg )
			dialog.doModal( )
			GuiLock2( False )
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex)


	def ShowDeleteConfirm( self ) :
		LOG_TRACE('ShowDeleteConfirm')
		pass


	def ShowEditTimer( self ) :
		LOG_TRACE('ShowEditTimer')
		pass


	def ShowDetailInfomation( self ) :
		LOG_TRACE('ShowDetailInfomation')

		epg = self.GetSelectedEPG( )

		if epg :
			GuiLock2( True )
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_EXTEND_EPG )
			dialog.SetEPG( epg )
			dialog.doModal( )
			GuiLock2( False )


	def	GetSelectedEPG( self ) :
		selectedEPG = None
		selectedPos = -1

		if self.mEPGMode == E_VIEW_CHANNEL :
			selectedPos = self.mCtrlList.getSelectedPosition()
			LOG_TRACE('selectedPos=%d' %selectedPos )
			if selectedPos >= 0 and selectedPos < len( self.mEPGList ) :
				selectedEPG = self.mEPGList[selectedPos]

		else :
			selectedPos = self.mCtrlBigList.getSelectedPosition()
			if selectedPos >= 0 and selectedPos < len( self.mChannelList ) :
				channel = self.mChannelList[ selectedPos ]
				selectedEPG = self.GetEPGByIds( channel.mSid, channel.mTsid, channel.mOnid )
			
		return selectedEPG


	def LoadTimerList( self ) :
		self.mTimerList = []
		timerCount = self.mDataCache.Timer_GetTimerCount( )

		for i in range( timerCount ) :
			timer = self.mDataCache.Timer_GetByIndex( i )
			self.mTimerList.append( timer )


	def HasManualRecording( self, aChannel ) :
		for i in range( len( self.mTimerList ) ) :
			timer =  self.mTimerList[i]
			#if timer.mTimerType == ElisEnum.E_ITIMER_MANUAL and aChannel.mSid == timer.mSid and aChannel.mTsid == timer.mTsid and aChannel.mOnid == timer.mOnid :
			if timer.mTimerType == 1 and aChannel.mSid == timer.mSid and aChannel.mTsid == timer.mTsid and aChannel.mOnid == timer.mOnid :			
				return True

		return False


	def HasIntersectionRecording( self, aEPG ) :

		try :	
			for i in range( len( self.mTimerList ) ) :
				timer =  self.mTimerList[i]
				startTime = aEPG.mStartTime 
				endTime = aEPG.mStartTime + aEPG.mDuration

				LOG_TRACE('id=%d:%d %d:%d %d:%d' %(aEPG.mSid, timer.mSid, aEPG.mTsid, timer.mTsid, aEPG.mOnid, timer.mOnid) )
				LOG_TRACE('EPG Start Time = %s' % TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
				LOG_TRACE('Timer Start Time = %s' % TimeToString( timer.mStartTime , TimeFormatEnum.E_HH_MM ) )			

				LOG_TRACE('EPG End Time = %s' % TimeToString( endTime, TimeFormatEnum.E_HH_MM ) )
				LOG_TRACE('Timer End Time = %s' % TimeToString( timer.mStartTime + timer.mDuration , TimeFormatEnum.E_HH_MM ) )
				
				
				if ( aEPG.mSid == timer.mSid and aEPG.mTsid == timer.mTsid and aEPG.mOnid == timer.mOnid ) and \
					(( startTime >= timer.mStartTime and startTime < (timer.mStartTime + timer.mDuration) ) or \
					( endTime > timer.mStartTime and endTime < (timer.mStartTime + timer.mDuration) ) ) :
					return True

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex)

		return False


	def Tune( self ) :

		LOG_TRACE('###########################')

		if self.mEPGMode == E_VIEW_CHANNEL :
			channel = self.mDataCache.Channel_GetCurrent( )
			self.mDataCache.Channel_SetCurrent( channel.mNumber, channel.mServiceType ) 

		else : #self.mEPGMode == E_VIEW_CURRENT  or self.mEPGMode == E_VIEW_FOLLOWING
			selectedPos = self.mCtrlBigList.getSelectedPosition()		
			if selectedPos >= 0 and selectedPos < len( self.mChannelList ) :
				channel = self.mChannelList[ selectedPos ]
				LOG_TRACE('--------------- number=%d ----------------' %channel.mNumber )
				self.mDataCache.Channel_SetCurrent( channel.mNumber, channel.mServiceType )


