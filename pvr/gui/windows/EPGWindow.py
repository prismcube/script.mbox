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
from pvr.Util import GetImageByEPGComponent,RunThread, GuiLock, GuiLock2, LOG_TRACE, LOG_WARN, LOG_ERR, GetSetting, SetSetting, TimeToString, TimeFormatEnum
from pvr.PublicReference import GetSelectedLongitudeString, EpgInfoTime, EpgInfoClock, EpgInfoComponentImage, EnumToString, ClassToList, AgeLimit
import pvr.ElisMgr
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
import threading, time, os


BUTTON_ID_EPG_MODE				= 100
RADIIOBUTTON_ID_EXTRA			= 101
LIST_ID_COMMON_EPG				= 3500
LIST_ID_BIG_EPG					= 3510

LABEL_ID_TIME					= 300
LABEL_ID_DATE					= 301
LABEL_ID_DURATION				= 302

IMAMGE_ID_HD					= 310
IMAMGE_ID_DOLBY					= 311
IMAMGE_ID_SUBTITLE				= 312

E_VIEW_CHANNEL					= 0
E_VIEW_CURRENT					= 1
E_VIEW_FOLLOWING				= 2
E_VIEW_END						= 3


E_MAX_EPG_COUNT					= 512
E_MAX_SCHEDULE_DAYS				= 8


CONTEXT_ADD_EPG_TIMER			= 0
CONTEXT_ADD_MANUAL_TIMER		= 1
CONTEXT_EDIT_TIMER				= 2
CONTEXT_DELETE_TIMER			= 3
CONTEXT_DELETE_ALL_TIMERS		= 4
CONTEXT_SHOW_ALL_TIMERS			= 5
CONTEXT_EXTEND_INFOMATION		= 6
CONTEXT_SEARCH					= 7

MININUM_KEYWORD_SIZE			= 3


class EPGWindow(BaseWindow):

	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)

	
	def onInit(self):
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId )

		self.SetPipScreen( )
		self.getControl( E_SETTING_MINI_TITLE ).setLabel( 'EPG' )

		LOG_TRACE('')
		self.mIsTimerMode = False
		self.mSelectedWeeklyTimer = 0

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

		self.mCtrlTimeLabel = self.getControl( LABEL_ID_TIME )
		self.mCtrlDateLabel = self.getControl( LABEL_ID_DATE )
		self.mCtrlDurationLabel = self.getControl( LABEL_ID_DURATION )		

		self.mCtrlHDImage = self.getControl( IMAMGE_ID_HD )
		self.mCtrlDolbyImage = self.getControl( IMAMGE_ID_DOLBY )
		self.mCtrlSubtitleImage = self.getControl( IMAMGE_ID_SUBTITLE )		

		self.mCtrlTimeLabel.setLabel('')
		self.mCtrlDateLabel.setLabel('')
		self.mCtrlDurationLabel.setLabel('')

		self.mCtrlHDImage.setImage('')
		self.mCtrlDolbyImage.setImage('')
		self.mCtrlSubtitleImage.setImage('')
		

		self.UpdateViewMode( )
		
		LOG_TRACE('')
		self.InitControl()
		LOG_TRACE('')

		self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( )
		self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
		LOG_TRACE('ZeppingMode(%d,%d,%d)' %( self.mCurrentMode.mServiceType, self.mCurrentMode.mMode, self.mCurrentMode.mSortingMode ) )
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
		self.UpdateEPGInfomation( )

		self.mEventBus.Register( self )	
		
		self.mInitialized = True

	def onAction( self, aAction ) :
		self.GetFocusId()
		actionId = aAction.getId( )
		self.GlobalAction( actionId )

		
		#LOG_TRACE('onAction=%d' %actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.Close( )
		elif  actionId == Action.ACTION_SELECT_ITEM :
			if self.mIsTimerMode == True :
				if self.mSelectedWeeklyTimer == 0 :
					self.GoChildTimer()
				else :
					selectedPos = self.mCtrlBigList.getSelectedPosition()		
					if self.mSelectedWeeklyTimer > 0 and selectedPos == 0 :
						self.GoParentTimer( )
					return
					
		
			elif self.mFocusId == LIST_ID_BIG_EPG:
				self.Tune( )
	
		elif actionId == Action.ACTION_PARENT_DIR :
			if self.mIsTimerMode == True :
				self.GoParentTimer( )
			else :
				self.Close( )
			
		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT :
			pass

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN :
			if self.mFocusId == LIST_ID_COMMON_EPG or self.mFocusId == LIST_ID_BIG_EPG :
				LOG_TRACE('')
				if self.mIsTimerMode == False :
					self.UpdateEPGInfomation( )

		elif actionId == Action.ACTION_PAGE_UP  or actionId == Action.ACTION_PAGE_DOWN :
			if self.mFocusId == LIST_ID_COMMON_EPG or self.mFocusId == LIST_ID_BIG_EPG :
				LOG_TRACE('')
				if self.mIsTimerMode == False :
					self.UpdateEPGInfomation( )
		
		elif actionId == Action.ACTION_CONTEXT_MENU:
			LOG_TRACE('')
			self.ShowContextMenu( )


	def onClick(self, aControlId):
		LOG_TRACE( 'aControlId=%d' %aControlId )
		if self.mIsTimerMode == True :
			return

		if aControlId == BUTTON_ID_EPG_MODE :
			self.mEPGMode += 1
			if self.mEPGMode >= E_VIEW_END :
				self.mEPGMode = 0 

			SetSetting( 'EPG_MODE','%d' %self.mEPGMode )
			self.UpdateViewMode( )
			self.InitControl( )
			self.Load( )
			self.UpdateList( )
			self.UpdateEPGInfomation()
		
		elif aControlId == RADIIOBUTTON_ID_EXTRA :
			pass

		elif aControlId == LIST_ID_COMMON_EPG :
			pass


	def onFocus(self, aControlId):
		if self.mInitialized == False :
			return


	@GuiLock
	def onEvent(self, aEvent):
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			if aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
				LOG_TRACE('Record Status chanaged')
				self.UpdateList( True )


	def Close( self ) :
		self.mEventBus.Deregister( self )	
		self.SetVideoRestore( )
		self.close( )


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
		if self.mEPGMode == E_VIEW_CHANNEL :
			self.mWin.setProperty( 'EPGMode', 'channel' )
		elif self.mEPGMode == E_VIEW_CURRENT :			
			self.mWin.setProperty( 'EPGMode', 'current' )
		elif self.mEPGMode == E_VIEW_FOLLOWING :			
			self.mWin.setProperty( 'EPGMode', 'following' )
		else :
			self.mEPGMode = E_VIEW_LIST 		
			self.mWin.setProperty( 'EPGMode', 'channel' )
			
		LOG_TRACE('---------------------self.mEPGMode=%d' %self.mEPGMode)
		

	def Flush( self ) :
		self.mEPGCount = 0
		self.mEPGList = []


	def Load( self ) :

		LOG_TRACE('----------------------------------->')
		self.mGMTTime = self.mDataCache.Datetime_GetGMTTime( )

		self.mEPGList = None
		
		if self.mIsTimerMode == True :
			pass

		else:
		
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
			self.mEPGList = None
			return

		LOG_TRACE('self.mEPGList COUNT=%d' %len(self.mEPGList ))
		

	def LoadByCurrent( self ):
		LOG_TRACE('')	
		
		try :
			self.mEPGList=self.mDataCache.Epgevent_GetCurrentList()

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)
	

	def LoadByFollowing( self ):
		LOG_TRACE('')
		
		try :
			self.mEPGList=self.mDataCache.Epgevent_GetFollowingList()

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)

		LOG_TRACE('self.mEPGList COUNT=%d' %len(self.mEPGList ))


	def UpdateEPGInfomation( self ) :

		if self.mIsTimerMode == True :
			epg = None
		else :
			epg = self.GetSelectedEPG()

		try :
			if epg :
				self.mCtrlTimeLabel.setLabel('%s~%s' %( TimeToString( epg.mStartTime, TimeFormatEnum.E_HH_MM ), TimeToString( epg.mStartTime + epg.mDuration, TimeFormatEnum.E_HH_MM ) ) )
				self.mCtrlDateLabel.setLabel('%s' %TimeToString( epg.mStartTime, TimeFormatEnum.E_AW_DD_MM_YYYY ) )
				self.mCtrlDurationLabel.setLabel('%dMin' %(epg.mDuration/60) )

				self.mCtrlHDImage.setImage( GetImageByEPGComponent( epg, ElisEnum.E_HasHDVideo ) )
				self.mCtrlDolbyImage.setImage( GetImageByEPGComponent( epg, ElisEnum.E_HasDolbyDigital ) )
				self.mCtrlSubtitleImage.setImage( GetImageByEPGComponent( epg, ElisEnum.E_HasSubtitles ) )
			else :
				self.mCtrlTimeLabel.setLabel('')
				self.mCtrlDateLabel.setLabel('')
				self.mCtrlDurationLabel.setLabel('')

				self.mCtrlHDImage.setImage('')
				self.mCtrlDolbyImage.setImage('')
				self.mCtrlSubtitleImage.setImage('')
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex)


	def UpdateList( self, aUpdateOnly=False ) :
		LOG_TRACE('')
		if aUpdateOnly == False :
			self.mListItems = []
		self.LoadTimerList( )

		LOG_TRACE('')
		if self.mIsTimerMode == True :
			LOG_TRACE('')

			self.mCtrlBigList.reset()
			self.mListItems = []
			
			if self.mTimerList== None or len( self.mTimerList ) <= 0 :
				return
				
			try :

				if self.mSelectedWeeklyTimer > 0 :
					timer = None
					for i in range( len( self.mTimerList ) ) :
						if self.mTimerList[i].mTimerId == self.mSelectedWeeklyTimer :
							timer = self.mTimerList[i]
							break

					if timer == None :
						return

					struct_time = time.gmtime( timer.mStartTime )
					# tm_wday is different between Python and C++
					LOG_TRACE('time.struct_time[6]=%d' %struct_time[6] )
					if struct_time[6] == 6 : #tm_wday
						weekday = 0
					elif struct_time[6] == 0 :
						weekday = 6
					else  :
						weekday = struct_time[6] + 1

						
					# hour*3600 + min*60 + sec
					secondsNow = struct_time[3]*3600 + struct_time[4]*60 + struct_time[5]

					LOG_TRACE('weekday=%d'  %weekday )

					listItem = xbmcgui.ListItem( '..' )
					listItem.setProperty( 'Duration', '' )
					listItem.setProperty( 'TimerType', 'None' )
					listItem.setProperty( 'HasEvent', 'false' )

					self.mListItems.append( listItem )					
					LOG_TRACE('')					

					for weeklyTimer in timer.mWeeklyTimer :
						dateLeft = weeklyTimer.mDate - weekday
						if dateLeft < 0 :
							dateLeft += 7
						elif dateLeft == 0 :
							if weeklyTimer.mStartTime < secondsNow :
								dateLeft += 7

						weeklyStarTime = dateLeft*24*3600 + timer.mStartTime + weeklyTimer.mStartTime - secondsNow

						channel = self.mDataCache.Channel_GetByNumber( timer.mChannelNo )
						LOG_TRACE('----------')
						channel.printdebug()
						tempChannelName = '%04d %s' %( channel.mNumber, channel.mName )

						listItem = xbmcgui.ListItem( tempChannelName, timer.mName )							

						#tempName = '%s(%s~%s)' %(TimeToString( weeklyStarTime, TimeFormatEnum.E_AW_DD_MM_YYYY ), TimeToString( weeklyStarTime, TimeFormatEnum.E_HH_MM ), TimeToString( weeklyStarTime + weeklyTimer.mDuration, TimeFormatEnum.E_HH_MM ) )
						tempName = '%s(%d)' %(TimeToString( weeklyStarTime, TimeFormatEnum.E_AW_DD_MM_YYYY ), weeklyTimer.mDuration )						
							
						listItem.setProperty( 'Duration', tempName )

						if self.IsRunningTimer( timer.mTimerId ) == True and \
							weeklyStarTime < self.mDataCache.Datetime_GetLocalTime() and self.mDataCache.Datetime_GetLocalTime() < weeklyStarTime + weeklyTimer.mDuration :
							listItem.setProperty( 'TimerType', 'Running' )
						else :
							listItem.setProperty( 'TimerType', 'None' )

						listItem.setProperty( 'HasEvent', 'false' )

						self.mListItems.append( listItem )

					self.mCtrlBigList.addItems( self.mListItems )						

				else :
					for i in range( len( self.mTimerList ) ) :
						timer = self.mTimerList[i]
						channel = self.mDataCache.Channel_GetByNumber( timer.mChannelNo )
						LOG_TRACE('----------')
						channel.printdebug()
						tempChannelName = '%04d %s' %( channel.mNumber, channel.mName )

						LOG_TRACE('----------')
						
						if aUpdateOnly == False :
							LOG_TRACE('----------')						
							listItem = xbmcgui.ListItem( tempChannelName, timer.mName )	
						else :
							LOG_TRACE('----------')						
							listItem = self.mListItems[i]

						if timer.mTimerType == ElisEnum.E_ITIMER_WEEKLY :
							tempName = 'Weekly'
						else :
							tempName = '%s~%s' %(TimeToString( timer.mStartTime, TimeFormatEnum.E_HH_MM ), TimeToString( timer.mStartTime + timer.mDuration, TimeFormatEnum.E_HH_MM ) )

						LOG_TRACE('----------')
						
						listItem.setProperty( 'Duration', tempName )

						if self.IsRunningTimer( timer.mTimerId ) == True :
							listItem.setProperty( 'TimerType', 'Running' )
						else :
							listItem.setProperty( 'TimerType', 'None' )

						listItem.setProperty( 'HasEvent', 'false' )

						LOG_TRACE('----------')
						
						if aUpdateOnly == False :
							self.mListItems.append( listItem )

						LOG_TRACE('---------- self.mListItems COUNT=%d' %len(self.mListItems))
						
					if aUpdateOnly == False :
						LOG_TRACE('----------')					
						self.mCtrlBigList.addItems( self.mListItems )

					xbmc.executebuiltin('container.update')

			except Exception, ex :
				LOG_ERR( "Exception %s" %ex)
			

		elif self.mEPGMode == E_VIEW_CHANNEL :
			if self.mEPGList == None :
				self.mCtrlList.reset()
				return

			try :		
				for i in range( len( self.mEPGList ) ) :
					epgEvent = self.mEPGList[i]
					#epgEvent.printdebug()
					if aUpdateOnly == False :
						listItem = xbmcgui.ListItem( TimeToString( epgEvent.mStartTime + self.mLocalOffset, TimeFormatEnum.E_HH_MM ), epgEvent.mEventName )					
					else :
						listItem = self.mListItems[i]					

					timerId = self.GetTimerByEPG( epgEvent )
					if timerId > 0 :
						if self.IsRunningTimer( timerId ) == True :
							listItem.setProperty( 'TimerType', 'Running' )
						else :
							listItem.setProperty( 'TimerType', 'Schedule' )						
					else :
						listItem.setProperty( 'TimerType', 'None' )

					if aUpdateOnly == False :
						self.mListItems.append( listItem )

				if aUpdateOnly == False :
					self.mCtrlList.addItems( self.mListItems )
					#self.setFocusId( LIST_ID_COMMON_EPG )
				else :
					xbmc.executebuiltin('container.update')
					#xbmc.executebuiltin('xbmc.Container.SetViewMode(%d)' %E_VIEW_CHANNEL)
					
				
			except Exception, ex :
				LOG_ERR( "Exception %s" %ex)

		elif self.mEPGMode == E_VIEW_CURRENT :
			if self.mChannelList == None :
				self.mCtrlBigList.reset()			
				return

			for i in range( len( self.mChannelList ) ) :
				channel = self.mChannelList[i]
				tempChannelName = '%04d %s' %( channel.mNumber, channel.mName )
				hasEpg = False

				try :
					epgEvent = self.GetEPGByIds( channel.mSid, channel.mTsid, channel.mOnid )

					if epgEvent :
						hasEpg = True
						if aUpdateOnly == False :
							listItem = xbmcgui.ListItem( tempChannelName, epgEvent.mEventName )
						else:
							listItem = self.mListItems[i]

						epgStart = epgEvent.mStartTime + self.mLocalOffset
						tempName = '%s~%s' %(TimeToString( epgStart, TimeFormatEnum.E_HH_MM ), TimeToString( epgStart + epgEvent.mDuration, TimeFormatEnum.E_HH_MM ) )
						listItem.setProperty( 'Duration', tempName )
						listItem.setProperty( 'HasEvent', 'true' )
 
						timerId = self.GetTimerByEPG( epgEvent )
						if timerId > 0 :
							if self.IsRunningTimer( timerId ) == True :
								listItem.setProperty( 'TimerType', 'Running' )
							else :
								listItem.setProperty( 'TimerType', 'Schedule' )						
						else :
							listItem.setProperty( 'TimerType', 'None' )
						
					else :
						if aUpdateOnly == False :					
							listItem = xbmcgui.ListItem( tempChannelName, 'No Event' )
						else:
							listItem = self.mListItems[i]

						listItem.setProperty( 'Duration', '' )
						listItem.setProperty( 'HasEvent', 'false' )
						timerId = self.GetTimerByChannel( channel )
 
						if timerId > 0 :
							if self.IsRunningTimer( timerId ) == True :
								listItem.setProperty( 'TimerType', 'Running' )
							else :
								listItem.setProperty( 'TimerType', 'Schedule' )						
						else :
							listItem.setProperty( 'TimerType', 'None' )

					#ListItem.PercentPlayed
					if aUpdateOnly == False :
						self.mListItems.append( listItem )

				except Exception, ex :
					LOG_ERR( "Exception %s" %ex)

			if aUpdateOnly == False :
				self.mCtrlBigList.addItems( self.mListItems )
				#self.setFocusId( LIST_ID_BIG_EPG )
			else :
				xbmc.executebuiltin('container.update')			
				#xbmc.executebuiltin('xbmc.Container.SetViewMode(%d)' %E_VIEW_CURRENT)			

		elif self.mEPGMode == E_VIEW_FOLLOWING :
			if self.mChannelList == None :
				self.mCtrlBigList.reset()
				return
		
			for i in range( len( self.mChannelList ) ) :
				channel = self.mChannelList[i]
				tempChannelName = '%04d %s' %( channel.mNumber, channel.mName )
				hasEpg = False

				try :
					epgEvent = self.GetEPGByIds( channel.mSid, channel.mTsid, channel.mOnid )

					if epgEvent :
						hasEpg = True
						if aUpdateOnly == False :						
							listItem = xbmcgui.ListItem( tempChannelName, epgEvent.mEventName )
						else :
							listItem = self.mListItems[i]

						epgStart = epgEvent.mStartTime + self.mLocalOffset
						tempName = '%s~%s' %(TimeToString( epgStart, TimeFormatEnum.E_HH_MM ), TimeToString( epgStart + epgEvent.mDuration, TimeFormatEnum.E_HH_MM ) )
						listItem.setProperty( 'Duration', tempName )
						listItem.setProperty( 'HasEvent', 'true' )
 
						timerId = self.GetTimerByEPG( epgEvent )
						if timerId > 0 :
							if self.IsRunningTimer( timerId ) == True :
								listItem.setProperty( 'TimerType', 'Running' )
							else :
								listItem.setProperty( 'TimerType', 'Schedule' )						
						else :
							listItem.setProperty( 'TimerType', 'None' )
						
					else :
						listItem = xbmcgui.ListItem( tempChannelName, 'No Event' )
						listItem.setProperty( 'Duration', '' )
						listItem.setProperty( 'HasEvent', 'false' )
 						timerId = self.GetTimerByChannel( channel )

						if timerId > 0 :
							if self.IsRunningTimer( timerId ) == True :
								listItem.setProperty( 'TimerType', 'Running' )
							else :
								listItem.setProperty( 'TimerType', 'Schedule' )						
						else :
							listItem.setProperty( 'TimerType', 'None' )

					#ListItem.PercentPlayed
					if aUpdateOnly == False :					
						self.mListItems.append( listItem )

				except Exception, ex :
					LOG_ERR( "Exception %s" %ex)

			if aUpdateOnly == False :
				self.mCtrlBigList.addItems( self.mListItems )
				#self.setFocusId( LIST_ID_BIG_EPG )
			else :
				xbmc.executebuiltin('container.update')			
				#xbmc.executebuiltin('xbmc.Container.SetViewMode(%d)' %E_VIEW_FOLLOWING)				

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


	def ShowContextMenu( self ) :
		LOG_TRACE('')
		context = []
		
		if self.mIsTimerMode == True :
			context.append( ContextItem( 'Edit Timer', CONTEXT_EDIT_TIMER ) )
			context.append( ContextItem( 'Delete Timer', CONTEXT_DELETE_TIMER ) )
			if self.mSelectedWeeklyTimer == 0 :			
				context.append( ContextItem( 'Delete All Timers', CONTEXT_DELETE_ALL_TIMERS ) )			

		else :

			selectedEPG = self.GetSelectedEPG()

			LOG_TRACE('')
			if selectedEPG :
				LOG_TRACE('')		
				if selectedEPG.mHasTimer :
					LOG_TRACE('')			
					context.append( ContextItem( 'Edit Timer', CONTEXT_EDIT_TIMER ) )
					context.append( ContextItem( 'Delete Timer', CONTEXT_DELETE_TIMER ) )
				else :
					LOG_TRACE('')
					timerId = self.GetTimerByEPG( selectedEPG )
					if timerId > 0 :
						context.append( ContextItem( 'Edit Timer', CONTEXT_EDIT_TIMER ) )
						context.append( ContextItem( 'Delete Timer', CONTEXT_DELETE_TIMER ) )
					else:
						context.append( ContextItem( 'Add Timer', CONTEXT_ADD_EPG_TIMER ) )
						context.append( ContextItem( 'Add Manual Timer', CONTEXT_ADD_MANUAL_TIMER ) )

				if 	self.mTimerList and len( self.mTimerList ) > 0 :
					context.append( ContextItem( 'Delete All Timers', CONTEXT_DELETE_ALL_TIMERS ) )
					context.append( ContextItem( 'Show All Timers', CONTEXT_SHOW_ALL_TIMERS ) )
					

				context.append( ContextItem( 'Search', CONTEXT_SEARCH ) )					
				context.append( ContextItem( 'Extend Infomation', CONTEXT_EXTEND_INFOMATION ) )		
				

			else :
				LOG_TRACE('')		
				timerId = 0

				if self.mEPGMode == E_VIEW_CURRENT or self.mEPGMode == E_VIEW_FOLLOWING :				
					LOG_TRACE('')			
					selectedPos = self.mCtrlBigList.getSelectedPosition()
					if selectedPos >= 0 and selectedPos < len( self.mChannelList ) :
						channel = self.mChannelList[ selectedPos ]
						timerId = self.GetTimerByChannel( channel )					

				if timerId > 0 :
					LOG_TRACE('')			
					context.append( ContextItem( 'Edit Timer', CONTEXT_EDIT_TIMER ) )
					context.append( ContextItem( 'Delete Timer', CONTEXT_DELETE_TIMER ) )
				else :
					LOG_TRACE('')			
					context.append( ContextItem( 'Add Manual Timer', CONTEXT_ADD_MANUAL_TIMER ) )

				if 	self.mTimerList and len( self.mTimerList ) > 0 :
					context.append( ContextItem( 'Delete All Timers', CONTEXT_DELETE_ALL_TIMERS ) )	
					context.append( ContextItem( 'Show All Timers', CONTEXT_SHOW_ALL_TIMERS ) )				

				context.append( ContextItem( 'Search', CONTEXT_SEARCH ) )

		GuiLock2( True )
		dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
		dialog.doModal( )
		GuiLock2( False )
		
		contextAction = dialog.GetSelectedAction()
		self.DoContextAction( contextAction ) 


	def DoContextAction( self, aContextAction ) :
		LOG_TRACE('aContextAction=%d' %aContextAction )

		if aContextAction == CONTEXT_ADD_EPG_TIMER :
			epg = self.GetSelectedEPG( )
			if epg :
				self.ShowEPGTimer( epg )

		elif aContextAction == CONTEXT_ADD_MANUAL_TIMER :
			epg = self.GetSelectedEPG( )
			self.ShowManualTimer( epg )

		elif aContextAction == CONTEXT_EDIT_TIMER :
			pass
			"""
			#ToDO
			epg = self.GetSelectedEPG( )		
			self.ShowManualTimer( epg, True )		
			"""

		elif aContextAction == CONTEXT_DELETE_TIMER :
			self.ShowDeleteConfirm( )

		elif aContextAction == CONTEXT_EXTEND_INFOMATION :
			self.ShowDetailInfomation( )

		elif aContextAction == CONTEXT_SEARCH :
			self.ShowSearchDialog( )

		elif aContextAction == CONTEXT_DELETE_ALL_TIMERS :
			self.ShowDeleteAllConfirm( )

		elif aContextAction == CONTEXT_SHOW_ALL_TIMERS :
			self.ShowAllTimers( )


	def ShowEPGTimer( self, aEPG ) :
		LOG_TRACE('ShowEPGTimer')
		GuiLock2( True )
		dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_ADD_TIMER )
		dialog.SetEPG( aEPG )
		dialog.doModal( )
		GuiLock2( False )

		try :
			if dialog.IsOK() == E_DIALOG_STATE_YES :
				LOG_TRACE('')
				self.mDataCache.Timer_AddEPGTimer( 0, 0, aEPG )
				self.UpdateList( True )
			else :
				LOG_TRACE('')

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)


	def ShowManualTimer( self, aEPG, aIsEdit=False ) :
		if aEPG :
			LOG_TRACE('ShowManualTimer EPG=%d IsEdit=%d' %( aEPG.mEventId, aIsEdit) )
		else :
			LOG_TRACE('ShowManualTimer EPG=None IsEdit=%d' %aIsEdit )

		GuiLock2( True )
		dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_ADD_MANUAL_TIMER )

		if aIsEdit :
			dialog.SetEditMode( True )		
			timerId = self.GetTimerByEPG( aEPG )		
			dialolg.SetTimer( timerId )
			
			if timerId < 0 :
				LOG_ERR('Can not find Timer')
				GuiLock2( False )				
				return

		else :
			dialog.SetEditMode( False )

			if aEPG :
				dialog.SetEPG( aEPG )

			channel = None
			if self.mEPGMode == E_VIEW_CHANNEL  :
				channel = self.mDataCache.Channel_GetCurrent( )
			else :
				selectedPos = self.mCtrlBigList.getSelectedPosition()
				if selectedPos >= 0 and selectedPos < len( self.mChannelList ) :
					channel = self.mChannelList[ selectedPos ]
				else :
					LOG_ERR('Can not find channel')
					GuiLock2( False )
					return
		
			dialog.SetChannel( channel )			

		dialog.doModal( )
		GuiLock2( False )

		if dialog.IsOK( ) == E_DIALOG_STATE_ERROR :
			xbmcgui.Dialog( ).ok('Error', dialog.GetErrorMessage() )
			return

		self.UpdateList( True )


	def ShowDeleteConfirm( self ) :
		LOG_TRACE('ShowDeleteConfirm')

		timerId = 0
		
		if self.mIsTimerMode == True :
			pass
		else :
			epg = self.GetSelectedEPG( )

			if epg :
				timerId = self.GetTimerByEPG( epg )

			else :
				if self.mEPGMode == E_VIEW_CURRENT or self.mEPGMode == E_VIEW_FOLLOWING :				
					LOG_TRACE('')			
					selectedPos = self.mCtrlBigList.getSelectedPosition()
					if selectedPos >= 0 and selectedPos < len( self.mChannelList ) :
						channel = self.mChannelList[ selectedPos ]
						timerId = self.GetTimerByChannel( channel )					
		
		if timerId > 0 :		
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( 'Confirm', 'Do you want to delete timer?' )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.mDataCache.Timer_DeleteTimer( timerId )
				self.UpdateList( True )


	def ShowDeleteAllConfirm( self ) :
		LOG_TRACE('ShowDeleteConfirm')
		if self.mTimerList == None or len(self.mTimerList) <= 0 :
			LOG_WARN('Has no Timer')
			return

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( 'Confirm', 'Do you want to delete all timers?' )
		dialog.doModal( )

		self.OpenBusyDialog( )
		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			for timer in self.mTimerList:
				timer.printdebug()
				self.mDataCache.Timer_DeleteTimer( timer.mTimerId )

			if self.mIsTimerMode == True :
				self.UpdateList( )
			else :
				self.UpdateList( True )
	
		self.CloseBusyDialog( )


	def ShowAllTimers( self ) :
		LOG_TRACE('ShowAllTimers')

		self.mIsTimerMode = True
		self.mSelectedWeeklyTimer = 0
		self.Load()
		self.UpdateList()
		self.UpdateEPGInfomation()
		

		"""
		if self.mTimerList == None or len(self.mTimerList) <= 0 :
			LOG_WARN('Has no Timer')
			return

		
		try:
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_TIMER_LIST )
			dialog.SetTimerList( self.mTimerList )
			dialog.doModal( )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex)
		"""

		

	def ShowSearchDialog( self ) :
		try :
			kb = xbmc.Keyboard( '', 'Search', False )
			kb.doModal( )
			if kb.isConfirmed( ) :
				keyword = kb.getText( )
				LOG_TRACE('keyword len=%d' %len( keyword ) )
				if len( keyword ) < MININUM_KEYWORD_SIZE :
					xbmcgui.Dialog( ).ok('Infomation', 'Input more than %d characters' %MININUM_KEYWORD_SIZE )
					return
					
				searchList = []
				indexList = []
				count = len( self.mListItems )
				
				for i in range( count ) :
					listItem = self.mListItems[ i ]

					label2 = listItem.getLabel2( )
					if label2.lower().find( keyword.lower() ) >= 0 :
						searchList.append( label2 )
						indexList.append( i )						

				LOG_TRACE('Result =%d' %len( searchList ) )

				if len( searchList ) <= 0 :
					xbmcgui.Dialog( ).ok('Infomation', 'Can not find matched result')			
		 			return
		 		else :
					dialog = xbmcgui.Dialog( )
		 			select = dialog.select( 'Select Event', searchList )

					if select >= 0 and select < len( searchList ) :
						LOG_TRACE('selectIndex=%d' %indexList[select] )
						LOG_TRACE('selectName=%s' %searchList[select] )
						if self.mEPGMode == E_VIEW_CHANNEL :
							self.mCtrlList.selectItem( indexList[select] )
						else:
							self.mCtrlBigList.selectItem( indexList[select] )

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)


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
		LOG_TRACE('')

		try :
			self.mTimerList = self.mDataCache.Timer_GetTimerList( )
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex)

		if self.mTimerList :
			LOG_TRACE('self.mTimerList len=%d' %len( self.mTimerList ) )

		"""
		self.mTimerList = []
		timerCount = self.mDataCache.Timer_GetTimerCount( )

		for i in range( timerCount ) :
			timer = self.mDataCache.Timer_GetByIndex( i )
			self.mTimerList.append( timer )
		"""


	def GetTimerByChannel( self, aChannel ) :
		if self.mTimerList == None :
			return 0
 
		for i in range( len( self.mTimerList ) ) :
			timer =  self.mTimerList[i]
			#if timer.mTimerType == 1 and aChannel.mSid == timer.mSid and aChannel.mTsid == timer.mTsid and aChannel.mOnid == timer.mOnid :						
			#if timer.mTimerType == ElisEnum.E_ITIMER_MANUAL and aChannel.mSid == timer.mSid and aChannel.mTsid == timer.mTsid and aChannel.mOnid == timer.mOnid :
			if aChannel.mSid == timer.mSid and aChannel.mTsid == timer.mTsid and aChannel.mOnid == timer.mOnid :			
				return timer.mTimerId

		return 0


	def GetTimerByEPG( self, aEPG ) :
		if self.mTimerList == None :
			return 0

		try :	
			for i in range( len( self.mTimerList ) ) :
				timer =  self.mTimerList[i]
				startTime = aEPG.mStartTime +  self.mLocalOffset 
				endTime = startTime + aEPG.mDuration

				LOG_TRACE('timerType=%d' %timer.mTimerType )
				LOG_TRACE('id=%d:%d %d:%d %d:%d' %(aEPG.mSid, timer.mSid, aEPG.mTsid, timer.mTsid, aEPG.mOnid, timer.mOnid) )
				LOG_TRACE('EPG Start Time = %s' % TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
				LOG_TRACE('Timer Start Time = %s' % TimeToString( timer.mStartTime , TimeFormatEnum.E_HH_MM ) )			
				LOG_TRACE('Start Time = %x:%x' % (startTime, timer.mStartTime )	)

				LOG_TRACE('EPG End Time = %s' % TimeToString( endTime, TimeFormatEnum.E_HH_MM ) )
				LOG_TRACE('Timer End Time = %s' % TimeToString( timer.mStartTime + timer.mDuration , TimeFormatEnum.E_HH_MM ) )
				LOG_TRACE('End Time = %x:%x' % (endTime, timer.mStartTime + timer.mDuration )	)

				LOG_TRACE(' timer.mFromEPG = %d  aEPG.mEventId=%d timer.mEventId=%d timer.mTimerId=%d' % (timer.mFromEPG, aEPG.mEventId, timer.mEventId, timer.mTimerId ) )

				if timer.mTimerType == ElisEnum.E_ITIMER_WEEKLY and timer.mWeeklyTimer and timer.mWeeklyTimerCount > 0 :


					struct_time = time.gmtime( timer.mStartTime )
					# tm_wday is different between Python and C++
					LOG_TRACE('time.struct_time[6]=%d' %struct_time[6] )
					if struct_time[6] == 6 : #tm_wday
						weekday = 0
					elif struct_time[6] == 0 :
						weekday = 6
					else  :
						weekday = struct_time[6] + 1

						
					# hour*3600 + min*60 + sec
					secondsNow = struct_time[3]*3600 + struct_time[4]*60 + struct_time[5]

					LOG_TRACE('weekday=%d'  %weekday )

					for weeklyTimer in timer.mWeeklyTimer :
						dateLeft = weeklyTimer.mDate - weekday
						if dateLeft < 0 :
							dateLeft += 7
						elif dateLeft == 0 :
							if weeklyTimer.mStartTime < secondsNow :
								dateLeft += 7

						weeklyStarTime = dateLeft*24*3600 + timer.mStartTime + weeklyTimer.mStartTime - secondsNow

						LOG_TRACE('weeklyTimer date==%d time=%s duration=%d' %(weeklyTimer.mDate, TimeToString( weeklyStarTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ), weeklyTimer.mDuration ) )
						if ( aEPG.mSid == timer.mSid and aEPG.mTsid == timer.mTsid and aEPG.mOnid == timer.mOnid ) and \
							(( startTime >= weeklyStarTime and startTime < (weeklyStarTime + weeklyTimer.mDuration) ) or \
							( endTime > weeklyStarTime and endTime < (weeklyStarTime + weeklyTimer.mDuration) ) ) :
							LOG_TRACE('------------------- find by weekly timer -------------------------')
							return timer.mTimerId
								
				else :
					if timer.mFromEPG :
						if  timer.mEventId > 0  and aEPG.mEventId == timer.mEventId and aEPG.mSid == timer.mSid and aEPG.mTsid == timer.mTsid and aEPG.mOnid == timer.mOnid :
							LOG_TRACE('------------------- find by event id -------------------------')					
							return timer.mTimerId

					else :
						if ( aEPG.mSid == timer.mSid and aEPG.mTsid == timer.mTsid and aEPG.mOnid == timer.mOnid ) and \
							(( startTime >= timer.mStartTime and startTime < (timer.mStartTime + timer.mDuration) ) or \
							( endTime > timer.mStartTime and endTime < (timer.mStartTime + timer.mDuration) ) ) :
							LOG_TRACE('------------------- find by manual timer-------------------------')
							return timer.mTimerId

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex)

		return 0


	def IsRunningTimer( self, aTimerId ) :
		runningTimers = self.mDataCache.Timer_GetRunningTimers( )
		if runningTimers == None :
			return False
			
		for timer in runningTimers :
			if timer.mTimerId == aTimerId :
				return True

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


	def GoChildTimer( self ) :
		if self.mIsTimerMode == False or self.mSelectedWeeklyTimer > 0 :
			return

		selectedPos = self.mCtrlBigList.getSelectedPosition()
		
		if selectedPos >= 0 and selectedPos < len( self.mTimerList ) :
			timer = self.mTimerList[selectedPos]

			if timer.mTimerType == ElisEnum.E_ITIMER_WEEKLY and timer.mWeeklyTimerCount > 0 :
				self.mSelectedWeeklyTimer = timer.mTimerId
				self.UpdateList()
		

	def GoParentTimer( self ) :
		if self.mIsTimerMode == False :
			return

		if self.mSelectedWeeklyTimer > 0 :
			self.mSelectedWeeklyTimer = 0
			self.UpdateList()

		else :
			self.mIsTimerMode = False
			self.Load()
			self.UpdateList()
			self.UpdateEPGInfomation()



