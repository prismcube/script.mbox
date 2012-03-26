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


CONTEXT_ADD_TIMER				= 0
CONTEXT_EDIT_TIMER				= 1
CONTEXT_DELETE_TIMER			= 2
CONTEXT_EXTEND_INFOMATION		= 3
CONTEXT_SEARCH					= 4

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
			if self.mFocusId == LIST_ID_BIG_EPG :
				self.Tune( )
	
		elif actionId == Action.ACTION_PARENT_DIR :
			self.Close( )
			
		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT :
			pass

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN :
			if self.mFocusId == LIST_ID_COMMON_EPG or self.mFocusId == LIST_ID_BIG_EPG :
				LOG_TRACE('')
				self.UpdateEPGInfomation( )

		elif actionId == Action.ACTION_PAGE_UP  or actionId == Action.ACTION_PAGE_DOWN :
			if self.mFocusId == LIST_ID_COMMON_EPG or self.mFocusId == LIST_ID_BIG_EPG :
				LOG_TRACE('')
				self.UpdateEPGInfomation( )
		
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
		epg = self.GetSelectedEPG()

		try :
			if epg :
				self.mCtrlTimeLabel.setLabel('%s~%s' %( TimeToString( epg.mStartTime, TimeFormatEnum.E_HH_MM ), TimeToString( epg.mStartTime + epg.mDuration, TimeFormatEnum.E_HH_MM ) ) )
				self.mCtrlDateLabel.setLabel('%s' %TimeToString( epg.mStartTime, TimeFormatEnum.E_AW_DD_MM_YYYY_HH_MM ) )
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

		if self.mEPGMode == E_VIEW_CHANNEL :
			if self.mEPGList == None :
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
					self.setFocusId( LIST_ID_COMMON_EPG )
				else :
					xbmc.executebuiltin('container.update')
					#xbmc.executebuiltin('xbmc.Container.SetViewMode(%d)' %E_VIEW_CHANNEL)
					
				
			except Exception, ex :
				LOG_ERR( "Exception %s" %ex)

		elif self.mEPGMode == E_VIEW_CURRENT :
			if self.mChannelList == None :
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
				self.setFocusId( LIST_ID_BIG_EPG )
			else :
				xbmc.executebuiltin('container.update')			
				#xbmc.executebuiltin('xbmc.Container.SetViewMode(%d)' %E_VIEW_CURRENT)			

		elif self.mEPGMode == E_VIEW_FOLLOWING :
			if self.mChannelList == None :
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
				self.setFocusId( LIST_ID_BIG_EPG )
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
				context.append( ContextItem( 'Search', CONTEXT_SEARCH ) )				
			else :
				LOG_TRACE('')
				timerId = self.GetTimerByEPG( selectedEPG )
				if timerId > 0 :
					context.append( ContextItem( 'Edit Timer', CONTEXT_EDIT_TIMER ) )
					context.append( ContextItem( 'Delete Timer', CONTEXT_DELETE_TIMER ) )
					context.append( ContextItem( 'Search', CONTEXT_SEARCH ) )					
				else:
					context.append( ContextItem( 'Add Timer', CONTEXT_ADD_TIMER ) )
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
				context.append( ContextItem( 'Search', CONTEXT_SEARCH ) )				
			else :
				LOG_TRACE('')			
				context.append( ContextItem( 'Add Timer', CONTEXT_ADD_TIMER ) )
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

		if aContextAction == CONTEXT_ADD_TIMER :
			epg = self.GetSelectedEPG( )
			if epg :
				self.ShowAddTimer( epg )
			else :
				self.ShowManualTimer( None )			

		elif aContextAction == CONTEXT_EDIT_TIMER :
			self.ShowEditTimer( )

		elif aContextAction == CONTEXT_DELETE_TIMER :
			self.ShowDeleteConfirm( )

		elif aContextAction == CONTEXT_EXTEND_INFOMATION :
			self.ShowDetailInfomation( )

		elif aContextAction == CONTEXT_SEARCH :
			self.ShowKeybordDialog( )


	def ShowAddTimer( self, aEPG ) :
		LOG_TRACE('ShowAddTimer')
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


	def ShowManualTimer( self, aEPG ) :
		LOG_TRACE('ShowManualTimer')
		"""
		GuiLock2( True )
		dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_ADD_TIMER )
		dialog.SetEPG( aEPG )
		dialog.doModal( )
		GuiLock2( False )
		"""


	def ShowDeleteConfirm( self ) :
		LOG_TRACE('ShowDeleteConfirm')

		epg = self.GetSelectedEPG( )
		timerId = 0
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


	def ShowEditTimer( self ) :
		LOG_TRACE('ShowEditTimer')
		pass


	def ShowKeybordDialog( self ) :
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
				endTime = aEPG.mStartTime + aEPG.mDuration

				LOG_TRACE('id=%d:%d %d:%d %d:%d' %(aEPG.mSid, timer.mSid, aEPG.mTsid, timer.mTsid, aEPG.mOnid, timer.mOnid) )
				LOG_TRACE('EPG Start Time = %s' % TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
				LOG_TRACE('Timer Start Time = %s' % TimeToString( timer.mStartTime , TimeFormatEnum.E_HH_MM ) )			
				LOG_TRACE('Start Time = %x:%x' % (startTime, timer.mStartTime )	)

				LOG_TRACE('EPG End Time = %s' % TimeToString( endTime, TimeFormatEnum.E_HH_MM ) )
				LOG_TRACE('Timer End Time = %s' % TimeToString( timer.mStartTime + timer.mDuration , TimeFormatEnum.E_HH_MM ) )
				LOG_TRACE('End Time = %x:%x' % (endTime, timer.mStartTime + timer.mDuration )	)

				LOG_TRACE(' timer.mFromEPG = %d  aEPG.mEventId=%d timer.mTimerId=%d' % (timer.mFromEPG, aEPG.mEventId, timer.mEventId ) )
				
				if timer.mFromEPG :
					if  timer.mEventId > 0  and aEPG.mEventId == timer.mEventId and aEPG.mSid == timer.mSid and aEPG.mTsid == timer.mTsid and aEPG.mOnid == timer.mOnid :
						LOG_TRACE('------------------- find by id -------------------------')					
						return aEPG.mTimerId

				else :
					if ( aEPG.mSid == timer.mSid and aEPG.mTsid == timer.mTsid and aEPG.mOnid == timer.mOnid ) and \
						(( startTime >= timer.mStartTime and startTime < (timer.mStartTime + timer.mDuration) ) or \
						( endTime > timer.mStartTime and endTime < (timer.mStartTime + timer.mDuration) ) ) :
						LOG_TRACE('------------------- find -------------------------')
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


