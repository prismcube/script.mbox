import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
from pvr.gui.BaseWindow import BaseWindow, Action
from ElisEnum import ElisEnum
from ElisEventBus import ElisEventBus
from ElisEventClass import *
from pvr.Util import RunThread, GuiLock, LOG_TRACE, LOG_WARN, LOG_ERR, GetSetting, SetSetting, TimeToString, TimeFormatEnum
from pvr.PublicReference import GetSelectedLongitudeString, EpgInfoTime, EpgInfoClock, EpgInfoComponentImage, EnumToString, ClassToList, AgeLimit
import pvr.ElisMgr
from ElisProperty import ElisPropertyEnum, ElisPropertyInt

from pvr.gui.GuiConfig import FooterMask
import threading, time, os


BUTTON_ID_EPG_MODE				= 100
RADIIOBUTTON_ID_EXTRA			= 101
LIST_ID_EPG						= 3500

E_VIEW_CHANNEL					= 0
E_VIEW_CURRENT					= 1
E_VIEW_FOLLOWING				= 2
E_VIEW_END						= 3


E_MAX_EPG_COUNT					= 512
E_MAX_SCHEDULE_DAYS				= 8


class EPGWindow(BaseWindow):

	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		self.mCommander = pvr.ElisMgr.GetInstance().GetCommander()		
		self.mEventBus = pvr.ElisMgr.GetInstance().GetEventBus()
		self.mInitialized = False
	
	def onInit(self):
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId )

		LOG_TRACE('')
		self.mEPGCount = 0
		self.mSelectedIndex = 0
		self.mEPGList = [] 
		self.mListItems = []

		LOG_TRACE('')
		self.mEPGMode = int( GetSetting( 'EPG_MODE' ) )
		self.mCtrlEPGMode = self.getControl( BUTTON_ID_EPG_MODE )

		self.mCtrlList = self.getControl( LIST_ID_EPG )
		self.UpdateViewMode( )
		
		LOG_TRACE('')
		self.InitControl()
		LOG_TRACE('')

		self.mCurrentMode = self.mCommander.Zappingmode_GetCurrent( )
		self.mCurrentChannel = self.mCommander.Channel_GetCurrent( )
		LOG_TRACE('ZeppingMode(%d,%d,%d)' %( self.mCurrentMode.mServiceType, self.mCurrentMode.mMode, self.mCurrentMode.mSortingMode ) )
		self.mChannelList = self.mCommander.Channel_GetList( self.mCurrentMode.mServiceType, self.mCurrentMode.mMode, self.mCurrentMode.mSortingMode )

		LOG_TRACE("ChannelList=%d" %len(self.mChannelList) )
		
		self.mSelectChannel = self.mCurrentChannel
		self.mLocalOffset = self.mCommander.Datetime_GetLocalOffset( )
		self.mGMTTime = 0
		LOG_TRACE('CHANNEL current=%s select=%s' %( self.mCurrentChannel, self.mSelectChannel ))

		self.Load( )
		LOG_TRACE('')
		self.UpdateList( )
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
		self.mGMTTime = self.mCommander.Datetime_GetGMTTime( )
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
			self.mEPGList = self.mCommander.Epgevent_GetList(  self.mSelectChannel.mSid,  self.mSelectChannel.mTsid,  self.mSelectChannel.mOnid,  gmtFrom,  gmtUntil,  E_MAX_EPG_COUNT)

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)

		if self.mEPGList == None or self.mEPGList[0].mError != 0 :
			self.mEPGList = []

		LOG_TRACE('self.mEPGList COUNT=%d' %len(self.mEPGList ))
		


	def LoadByCurrent( self ):
		LOG_TRACE('')

		gmtFrom =  0
		gmtUntil = 0

		LOG_TRACE('ChannelList len=%d' %(len(self.mChannelList) ) )

		for i in range( len(self.mChannelList) ) :
			channel = self.mChannelList[ i ]
			#LOG_TRACE('channel[%d].mNumber=%d name=%s' %(i, channel.mNumber, channel.mName) )
			epgList = []
			epgList = self.mCommander.Epgevent_GetList( channel.mSid, channel.mTsid, channel.mOnid, gmtFrom, gmtUntil, 1 )

		
			if epgList == None :
				#LOG_WARN('Has no')
				continue

			elif epgList[0].mError != 0 :
				LOG_ERR('epg Err=%d' %epgList[0].mError )
				continue
			else :
				self.mEPGList.append( epgList[0] )


		LOG_TRACE('self.mEPGList COUNT=%d' %len(self.mEPGList ))



	def LoadByFollowing( self ):
		LOG_TRACE('')

		gmtFrom =  1
		gmtUntil = 1

		LOG_TRACE('ChannelList len=%d' %(len(self.mChannelList) ) )

		for i in range( len(self.mChannelList) ) :
			channel = self.mChannelList[ i ]
			#LOG_TRACE('channel[%d].mNumber=%d name=%s' %(i, channel.mNumber, channel.mName) )
			epgList = []
			epgList = self.mCommander.Epgevent_GetList( channel.mSid, channel.mTsid, channel.mOnid, gmtFrom, gmtUntil, 1 )

		
			if epgList == None :
				#LOG_WARN('Has no')
				continue

			elif epgList[0].mError != 0 :
				LOG_ERR('epg Err=%d' %epgList[0].mError )
				continue
			else :
				self.mEPGList.append( epgList[0] )


		LOG_TRACE('self.mEPGList COUNT=%d' %len(self.mEPGList ))



	def UpdateList( self ) :
		LOG_TRACE('')
		self.mListItems = []
		if self.mEPGMode == E_VIEW_CHANNEL :		
			for i in range( len( self.mEPGList ) ) :
				LOG_TRACE('---------->i=%d' %i)		
				epgEvent = self.mEPGList[i]
				epgEvent.printdebug()
				listItem = xbmcgui.ListItem( TimeToString( epgEvent.mStartTime + self.mLocalOffset, TimeFormatEnum.E_HH_MM ), epgEvent.mEventName )			
				self.mListItems.append( listItem )


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
					else :
						listItem = xbmcgui.ListItem( tempChannelName, 'No Event' )
						listItem.setProperty( 'Duration', '' )
						listItem.setProperty( 'HasEvent', 'false' )

					#ListItem.PercentPlayed
					self.mListItems.append( listItem )

				except Exception, ex :
					LOG_ERR( "Exception %s" %ex)

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
					else :
						listItem = xbmcgui.ListItem( tempChannelName, 'No Event' )
						listItem.setProperty( 'Duration', '' )
						listItem.setProperty( 'HasEvent', 'false' )

					#ListItem.PercentPlayed
					self.mListItems.append( listItem )

				except Exception, ex :
					LOG_ERR( "Exception %s" %ex)

		LOG_TRACE('')
		self.mCtrlList.addItems( self.mListItems )


	def GetEPGByIds( self, aSid, aTsid, aOnid ) :
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

