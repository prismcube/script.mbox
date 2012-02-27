import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DiaMgr
import pvr.DataCacheMgr as CacheMgr

from pvr.gui.BaseWindow import BaseWindow, Action
from pvr.gui.GuiConfig import *

import pvr.ElisMgr
from ElisAction import ElisAction
from ElisEnum import ElisEnum
from ElisEventBus import ElisEventBus
from ElisEventClass import *

from pvr.Util import RunThread, GuiLock, GuiLock2, MLOG, LOG_WARN, LOG_TRACE, LOG_ERR, TimeToString, TimeFormatEnum
from pvr.PublicReference import GetSelectedLongitudeString, EpgInfoTime, EpgInfoClock, EpgInfoComponentImage, EnumToString, ClassToList, AgeLimit
from ElisProperty import ElisPropertyEnum

import pvr.Msg as Msg
import pvr.gui.windows.Define_string as MsgId

import threading, time, os

#debug log
import logging
from inspect import currentframe

#log = logging.getLogger('mythbox.ui')
#mlog = logging.getLogger('mythbox.method')


FLAG_MASK_ADD  = 0x01
FLAG_MASK_NONE = 0x00
FLAG_CLOCKMODE_ADMYHM  = 1
FLAG_CLOCKMODE_AHM     = 2
FLAG_CLOCKMODE_HMS     = 3
FLAG_CLOCKMODE_HHMM    = 4
FLAG_CLOCKMODE_INTTIME = 5

E_IMG_SCREEN_HIDE = 'confluence/black-back.png'
E_IMG_ICON_LOCK   = 'IconLockFocus.png'
E_IMG_ICON_ICAS   = 'IconCas.png'
E_IMG_ICON_TV     = 'confluence/tv.png'
E_IMG_ICON_RADIO  = 'icon_radio.png'

NEXT_EPG		= 0
PREV_EPG 		= 1

NEXT_CHANNEL	= 0
PREV_CHANNEL	= 1
CURR_CHANNEL	= 2

class LivePlate(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)

		self.mLocalTime = 0
		self.mEventID = 0
		self.mPincodeEnter = FLAG_MASK_NONE
		self.mCurrentChannel = None
		self.mLastChannel = None
		self.mFakeChannel = None
		self.mFlag_OnEvent = True
		self.mShowExtendInfo = False
		self.mPropertyAge = 0
		self.mPropertyPincode = -1

		self.mAutomaticHideTimer = None	
		self.mAsyncEPGTimer = None
		self.mAsyncTuneTimer = None	
		self.mAutomaticHide = True


	def __del__(self):
		LOG_TRACE( 'destroyed LivePlate' )

		# end thread CurrentTimeThread()
		self.mEnableThread = False

	def onInit(self):
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId )
		LOG_TRACE( 'winID[%d]'% self.mWinId)

		self.mShowExtendInfo = False

		self.mCtrlLblChannelNumber     = self.getControl( 601 )
		self.mCtrlLblChannelName       = self.getControl( 602 )
		self.mCtrlImgServiceType       = self.getControl( 603 )
		self.mCtrlImgServiceTypeImg1   = self.getControl( 604 )
		self.mCtrlImgServiceTypeImg2   = self.getControl( 605 )
		self.mCtrlImgServiceTypeImg3   = self.getControl( 606 )
		self.mCtrlLblEventClock        = self.getControl( 610 )
		self.mCtrlLblLongitudeInfo     = self.getControl( 701 )
		self.mCtrlLblEventName         = self.getControl( 703 )
		self.mCtrlLblEventStartTime    = self.getControl( 704 )
		self.mCtrlLblEventEndTime      = self.getControl( 705 )
		self.mCtrlProgress             = self.getControl( 707 )
		self.mCtrlGropEventDescGroup   = self.getControl( 800 )
		self.mCtrlTxtBoxEventDescText1 = self.getControl( 801 )
		self.mCtrlTxtBoxEventDescText2 = self.getControl( 802 )
		#self.mCtrlProgress = xbmcgui.ControlProgress(100, 250, 125, 75)
		#self.mCtrlProgress(self.Progress)

		#button icon
		self.mCtrlBtnExInfo            = self.getControl( 621 )
		self.mCtrlBtnTeletext          = self.getControl( 622 )
		self.mCtrlBtnSubtitle          = self.getControl( 623 )
		self.mCtrlBtnStartRec          = self.getControl( 624 )
		self.mCtrlBtnStopRec           = self.getControl( 625 )
		self.mCtrlBtnMute              = self.getControl( 626 )
		self.mCtrlImgLocked            = self.getControl( 651 )
		self.mCtrlImgICas              = self.getControl( 652 )
		#self.mCtrlBtnTSbanner          = self.getControl( 630 )

		self.mCtrlBtnPrevEpg           = self.getControl( 702 )
		self.mCtrlBtnNextEpg           = self.getControl( 706 )


		self.mImgTV    = E_IMG_ICON_TV
		self.mCtrlLblEventClock.setLabel('')

		self.mPropertyAge = self.mDataCache.mPropertyAge
		self.mPropertyPincode = self.mDataCache.mPropertyPincode
		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset()

		#get channel
		self.mCurrentChannel = self.mDataCache.Channel_GetCurrent()
		self.mFakeChannel =	self.mCurrentChannel
		self.mLastChannel =	self.mCurrentChannel

		self.mFlag_OnEvent = True
		self.mFlag_ChannelChanged = True
		self.mEventCopy = None
		self.mEPGList = None
		self.mEPGListIdx = 0
		self.mJumpNumber = 0

		self.GetEPGList()
		self.UpdateServiceType( self.mCurrentChannel.mServiceType )
		self.InitLabelInfo()

		#get epg event right now, as this windows open
		self.mEventBus.Register( self )

		#run thread
		self.mEnableThread = True
		self.CurrentTimeThread()

		try :
			ret = None
			ret = self.mDataCache.Epgevent_GetPresent()
			if ret and ret.mEventName != 'No Name':
				self.mEventCopy = ret
				self.UpdateONEvent(self.mEventCopy)

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		self.PincodeDialogLimit()
		self.mAsyncEPGTimer = None
		self.mAsyncTuneTimer = None
		self.mAutomaticHideTimer = None

		if self.mAutomaticHide == True :
			self.StartAutomaticHide()


	def onAction(self, aAction):
		#LOG_TRACE( 'Enter' )

		id = aAction.getId()
		self.GlobalAction( id )
		if id >= Action.REMOTE_0 and id <= Action.REMOTE_9 :
			self.KeySearch( id-Action.REMOTE_0 )

		elif id >= Action.ACTION_JUMP_SMS2 and id <= Action.ACTION_JUMP_SMS9 :
			rKey = id - (Action.ACTION_JUMP_SMS2 - 2)
			self.KeySearch( rKey )

		elif id == Action.ACTION_PREVIOUS_MENU or id == Action.ACTION_PARENT_DIR:
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )

			if self.mShowExtendInfo ==  True :
				self.ShowEPGDescription( False )
				return
 
			self.Close()

		elif id == Action.ACTION_SELECT_ITEM:
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )

	
		elif id == Action.ACTION_CONTEXT_MENU :
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
		
			if self.mShowExtendInfo ==  True :
				self.ShowEPGDescription( False )
			self.Close( )

		elif id == Action.ACTION_MOVE_LEFT:
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
		
			self.GetFocusId()
			if self.mFocusId == self.mCtrlBtnPrevEpg.getId():			
				self.EPGNavigation( PREV_EPG )

		elif id == Action.ACTION_MOVE_RIGHT:
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
		
			self.GetFocusId()
			if self.mFocusId == self.mCtrlBtnNextEpg.getId():
				self.EPGNavigation( NEXT_EPG )

		elif id == Action.ACTION_PAGE_UP:
			self.ChannelTune( NEXT_CHANNEL )

		elif id == Action.ACTION_PAGE_DOWN:
			self.ChannelTune( PREV_CHANNEL )

		elif id == Action.ACTION_PAUSE:
			if self.mShowExtendInfo ==  False :
				self.Close()
				winmgr.GetInstance().ShowWindow( winmgr.WIN_ID_TIMESHIFT_PLATE )
 		
		elif id == 13: #'x'
			#this is test
			LOG_TRACE( 'cwd[%s]'% xbmc.getLanguage() )


		#LOG_TRACE( 'Leave' )



	def onClick(self, aControlId):
		LOG_TRACE( 'control %d' % aControlId )

		if aControlId == self.mCtrlBtnMute.getId():
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
		
			self.GlobalAction( Action.ACTION_MUTE  )

		elif aControlId == self.mCtrlBtnExInfo.getId() :
			LOG_TRACE( 'click expantion info' )		
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
			self.ShowEPGDescription( not self.mShowExtendInfo )

		elif aControlId == self.mCtrlBtnTeletext.getId() :
			LOG_TRACE( 'click teletext' )
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
			self.ShowDialog( aControlId )

		elif aControlId == self.mCtrlBtnSubtitle.getId() :
			LOG_TRACE( 'click subtitle' )
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
			self.ShowDialog( aControlId )

		elif aControlId == self.mCtrlBtnStartRec.getId() :
			LOG_TRACE( 'click start recording' )
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
			self.ShowDialog( aControlId )

		elif aControlId == self.mCtrlBtnStopRec.getId() :
			LOG_TRACE( 'click stop recording' )
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
			self.ShowDialog( aControlId )

		elif aControlId == self.mCtrlBtnPrevEpg.getId() :
			LOG_TRACE( 'click prev epg' )
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
			self.EPGNavigation( PREV_EPG )

		elif aControlId == self.mCtrlBtnNextEpg.getId() :
			LOG_TRACE( 'click next epg' )
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
			self.EPGNavigation( NEXT_EPG )




	def onFocus(self, aControlId):
		#LOG_TRACE( 'control %d' % controlId )
		pass


	def onEvent(self, aEvent):
		#LOG_TRACE( 'Enter' )

		if self.mWinId == xbmcgui.getCurrentWindowId():
			currentChannel = self.mCurrentChannel	
			if aEvent.getName() == ElisEventCurrentEITReceived.getName() :

				if currentChannel == None :
					LOG_TRACE('ignore event, currentChannel None, [%s]'% currentChannel)
					return -1
				
				if currentChannel.mSid != aEvent.mSid or currentChannel.mTsid != aEvent.mTsid or currentChannel.mOnid != aEvent.mOnid :
					#LOG_TRACE('ignore event, same event')
					return -1

				if currentChannel.mNumber != self.mFakeChannel.mNumber :
					LOG_TRACE('ignore event, Channel: current[%s] fake[%s]'% (currentChannel.mNumber, self.mFakeChannel.mNumber) )
					return -1

				if self.mFlag_OnEvent != True :
					LOG_TRACE('ignore event, mFlag_OnEvent[%s]'% self.mFlag_OnEvent)
					return -1

				LOG_TRACE( 'eventid:new[%d] old[%d]' %(aEvent.mEventId, self.mEventID ) )
				#aEvent.printdebug()

				if aEvent.mEventId != self.mEventID :
					ret = None
					ret = self.mDataCache.Epgevent_GetPresent( )
					if ret and ret.mEventName != 'No Name':
						LOG_TRACE('-----------------------')
						#ret.printdebug()

						if not self.mEventCopy or \
						ret.mEventId != self.mEventCopy.mEventId or \
						ret.mSid != self.mEventCopy.mSid or \
						ret.mTsid != self.mEventCopy.mTsid or \
						ret.mOnid != self.mEventCopy.mOnid :
							LOG_TRACE('epg DIFFER, id[%s]'% ret.mEventId)
							self.mEventID = aEvent.mEventId
							self.mEventCopy = ret
							#update label
							self.UpdateONEvent( ret )

							#check : new event?
							if self.mEPGList :
								#1. aready exist? search in EPGList
								idx = 0
								self.mEPGListIdx = -1
								for item in self.mEPGList :
									if 	item.mEventId == self.mEventCopy.mEventId and \
										item.mSid == self.mEventCopy.mSid and \
										item.mTsid == self.mEventCopy.mTsid and \
										item.mOnid == self.mEventCopy.mOnid :

										self.mEPGListIdx = idx
										LOG_TRACE('Received ONEvent : EPGList idx moved(current idx)')

										retList=[]
										retList.append(item)
										LOG_TRACE('1.Aready Exist: NOW EPG idx[%s] [%s]'% (idx, ClassToList('convert', retList)) )
										break

									idx += 1

								#2. new epg, append to EPGList
								if self.mEPGListIdx == -1 :
									LOG_TRACE('new EPG received, not exist in EPGList')
									oldLen = len(self.mEPGList)
									idx = 0
									for idx in range(len(self.mEPGList)) :
										if self.mEventCopy.mStartTime < self.mEPGList[idx].mStartTime :
											break

									self.mEPGListIdx = idx
									self.mEPGList = self.mEPGList[:idx]+[self.mEventCopy]+self.mEPGList[idx:]
									LOG_TRACE('append new idx[%s], epgTotal:oldlen[%s] newlen[%s]'% (idx, oldLen, len(self.mEPGList)) )
									LOG_TRACE('list[%s]'% ClassToList('convert',self.mEPGList) )


		else:
			LOG_TRACE( 'LivePlate winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId()) )


		#LOG_TRACE( 'Leave' )


	def ChannelTune(self, aDir):

		if aDir == PREV_CHANNEL:
		
			prevChannel = self.mDataCache.Channel_GetPrev( self.mFakeChannel )

			if prevChannel == None or prevChannel.mError != 0 :
				return

			self.mFakeChannel = prevChannel
			self.UpdateServiceType( self.mFakeChannel.mServiceType )
			self.InitLabelInfo()
			self.RestartAsyncTune()

		elif aDir == NEXT_CHANNEL:
			nextChannel = self.mDataCache.Channel_GetNext( self.mFakeChannel )

			if nextChannel == None or nextChannel.mError != 0 :
				return

			self.mFakeChannel = nextChannel
			self.UpdateServiceType( self.mFakeChannel.mServiceType )
			self.InitLabelInfo()			
			self.RestartAsyncTune()

		elif aDir == CURR_CHANNEL:
			jumpChannel = self.mDataCache.Channel_GetCurr( self.mJumpNumber )

			if jumpChannel == None or jumpChannel.mError != 0 :
				return

			self.mFakeChannel = jumpChannel
			self.UpdateServiceType( self.mFakeChannel.mServiceType )
			self.InitLabelInfo()			
			self.RestartAsyncTune()

		if self.mAutomaticHide == True :
			self.RestartAutomaticHide()


	def EPGListMove( self ) :
		LOG_TRACE( 'Enter' )

		try :

			LOG_TRACE('ch[%s] len[%s] idx[%s]'% (self.mCurrentChannel.mNumber, len(self.mEPGList),self.mEPGListIdx) )
			ret = self.mEPGList[self.mEPGListIdx]

			if ret :
				self.InitLabelInfo()
				GuiLock2(True)
				self.mEventCopy = ret
				self.mFlag_OnEvent = False
				GuiLock2(False)

				self.UpdateServiceType( self.mCurrentChannel.mServiceType )
				self.UpdateONEvent( self.mEventCopy )

				retList = []
				retList.append( self.mEventCopy )
				LOG_TRACE( 'idx[%s] epg[%s]'% (self.mEPGListIdx, ClassToList( 'convert', retList )) )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		LOG_TRACE( 'Leave' )

	def EPGNavigation(self, aDir ):
		LOG_TRACE('Enter')

		#if self.mFlag_OnEvent :
		#	self.GetEPGList()

		if self.mEPGList :
			lastIdx = len(self.mEPGList) - 1
			if aDir == NEXT_EPG:
				if self.mEPGListIdx+1 > lastIdx :
					self.mEPGListIdx = lastIdx
				else :
					self.mEPGListIdx += 1


			elif aDir == PREV_EPG:
				if self.mEPGListIdx-1 < 0 :
					self.mEPGListIdx = 0
				else :
					self.mEPGListIdx -= 1

			self.EPGListMove()
			#self.PincodeDialogLimit()


		LOG_TRACE('Leave')

	def GetEPGList( self ) :
		LOG_TRACE( 'Enter' )

		ret = None

		try :
			#stop onEvent
			self.mFlag_OnEvent = False
			if self.mEventCopy == None :
				ret = self.mCommander.Epgevent_GetPresent()
				if ret and ret.mEventName != 'No Name':
					self.mEventCopy = ret

				else :
					#receive onEvent
					self.mFlag_OnEvent = True
					return -1

			if self.mCurrentChannel :
				self.mEPGList = None
				ichannel = self.mCurrentChannel

				#Live EPG
				#gmtime = self.mDataCache.Datetime_GetGMTTime()
				#test Stream
				gmtFrom  = self.mEventCopy.mStartTime

				gmtUntil = gmtFrom + ( 3600 * 24 * 7 )
				maxCount = 100
				ret = None
				ret = self.mCommander.Epgevent_GetList( ichannel.mSid, ichannel.mTsid, ichannel.mOnid, gmtFrom, gmtUntil, maxCount )
				time.sleep(0.05)
				LOG_TRACE('==================')
				LOG_TRACE('ret[%s] ch[%d] sid[%d] tid[%d] oid[%d] from[%s] until[%s]'% (ret,ichannel.mNumber,ichannel.mSid, ichannel.mTsid, ichannel.mOnid, time.asctime(time.localtime(gmtFrom)), time.asctime(time.localtime(gmtUntil))) )
				#LOG_TRACE('=============epg len[%s] list[%s]'% (len(ret),ClassToList('convert', ret )) )
				if ret :
					self.mEPGList = ret
					self.mFlag_ChannelChanged = False
				else :
					LOG_TRACE('EPGList is None\nLeave')
					#receive onEvent
					self.mFlag_OnEvent = True
					return -1

				LOG_TRACE('event[%s]'% self.mEventCopy )
				retList=[]
				retList.append(self.mEventCopy)
				LOG_TRACE('==========[%s]'% ClassToList('convert', retList) )
				LOG_TRACE('EPGList len[%s] [%s]'% (len(self.mEPGList), ClassToList('convert', self.mEPGList)) )
				LOG_TRACE('onEvent[%s] list[%s]'% (self.mEventCopy, self.mEPGList))
				idx = 0
				self.mEPGListIdx = -1
				for item in self.mEPGList :
					#LOG_TRACE('idx[%s] item[%s]'% (idx, item) )
					if 	item.mEventId == self.mEventCopy.mEventId and \
						item.mSid == self.mEventCopy.mSid and \
						item.mTsid == self.mEventCopy.mTsid and \
						item.mOnid == self.mEventCopy.mOnid :

						self.mEPGListIdx = idx

						retList=[]
						retList.append(item)
						LOG_TRACE('SAME NOW EPG idx[%s] [%s]'% (idx, ClassToList('convert', retList)) )

						break

					idx += 1

				#search not current epg
				if self.mEPGListIdx == -1 : 
					self.mEPGListIdx = 0
					LOG_TRACE('SEARCH NOT CURRENT EPG, idx=0')


				#receive onEvent
				self.mFlag_OnEvent = True

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		LOG_TRACE( 'Leave' )


	@GuiLock
	def UpdateONEvent(self, aEvent = None):
		LOG_TRACE( 'Enter' )
		#LOG_TRACE( 'component [%s]'% EpgInfoComponentImage ( aEvent ))


		if self.mCurrentChannel :
			ch = self.mCurrentChannel

			if ch.mLocked :
				self.mCtrlImgLocked.setImage( E_IMG_ICON_LOCK )
				if self.mFlag_OnEvent == True :
					self.mPincodeEnter |= FLAG_MASK_ADD

			if ch.mIsCA :
				self.mCtrlImgICas.setImage( E_IMG_ICON_ICAS )


		if aEvent :
			try :
				#epg name
				self.mCtrlLblEventName.setLabel(aEvent.mEventName)

				ret = None
				ret = EpgInfoTime( self.mLocalOffset, aEvent.mStartTime, aEvent.mDuration )
				if ret :
					self.mCtrlLblEventStartTime.setLabel( ret[0] )
					self.mCtrlLblEventEndTime.setLabel( ret[1] )

				LOG_TRACE( 'mStartTime[%s] mDuration[%s]'% (aEvent.mStartTime, aEvent.mDuration) )


				#component
				imglist = EpgInfoComponentImage( aEvent )
				if len(imglist) == 1:
					self.mCtrlImgServiceTypeImg1.setImage( imglist[0] )
				elif len(imglist) == 2:
					self.mCtrlImgServiceTypeImg1.setImage( imglist[0] )
					self.mCtrlImgServiceTypeImg2.setImage( imglist[1] )
				elif len(imglist) == 3:
					self.mCtrlImgServiceTypeImg1.setImage( imglist[0] )
					self.mCtrlImgServiceTypeImg2.setImage( imglist[1] )
					self.mCtrlImgServiceTypeImg3.setImage( imglist[2] )
				else:
					self.mCtrlImgServiceTypeImg1.setImage('')
					self.mCtrlImgServiceTypeImg2.setImage('')
					self.mCtrlImgServiceTypeImg3.setImage('')

				#is Age? agerating check
				if self.mFlag_OnEvent == True :
					isLimit = AgeLimit( self.mPropertyAge, aEvent.mAgeRating )
					if isLimit == True :
						self.mPincodeEnter |= FLAG_MASK_ADD
						LOG_TRACE( 'AgeLimit[%s]'% isLimit )

			except Exception, e:
				LOG_TRACE( 'Error exception[%s]'% e )

		else:
			LOG_TRACE( 'aEvent null' )


		"""
		# Todo
		if self.mFlag_OnEvent :
			self.GetEPGList()
		"""


		LOG_TRACE( 'Leave' )


	def PincodeDialogLimit( self ) :

		#popup pin-code dialog
		#if self.mPincodeEnter > FLAG_MASK_NONE :

		while self.mPincodeEnter > FLAG_MASK_NONE :

			try :
				msg = Msg.Strings(MsgId.LANG_INPUT_PIN_CODE)
				inputPin = ''

				#ret = self.mCommander.Channel_SetInitialBlank( True )
				ret = self.mCommander.Player_AVBlank( True, True )

				GuiLock2( True )
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
				dialog.SetDialogProperty( msg, '', 4, True )
	 			dialog.doModal()
				GuiLock2( False )

				reply = dialog.IsOK()
	 			if reply == E_DIALOG_STATE_YES :
	 				inputPin = dialog.GetString()

	 			elif reply == E_DIALOG_STATE_CANCEL :
	 				self.mPincodeEnter = FLAG_MASK_NONE
					self.mCommander.Player_AVBlank( False, True )

	 				inputKey = dialog.GetInputKey()
	 				self.onAction( inputKey )
	 				break


				if inputPin == None or inputPin == '' :
					inputPin = ''

				#LOG_TRACE( 'mask[%s] inputPin[%s] stbPin[%s]'% (self.mPincodeEnter, inputPin, self.mPropertyPincode) )

				if inputPin == str('%s'% self.mPropertyPincode) :
					self.mPincodeEnter = FLAG_MASK_NONE
					#ret = self.mCommander.Channel_SetInitialBlank( False )
					#self.mCommander.Player_AVBlank( False, True )
					mNumber = self.mCurrentChannel.mNumber
					mType = self.mCurrentChannel.mServiceType
					ret = self.mDataCache.Channel_SetCurrent( mNumber, mType)

					LOG_TRACE( 'Pincode success' ) 
					break
				else:
					msg1 = Msg.Strings(MsgId.LANG_ERROR)
					msg2 = Msg.Strings(MsgId.LANG_WRONG_PIN_CODE)
					GuiLock2( True )
					xbmcgui.Dialog().ok( msg1, msg2 )
					GuiLock2( False )

			except Exception, e:
				LOG_TRACE( 'Error exception[%s]'% e )

			time.sleep(0.1)
			LOG_TRACE('=======loop==============')

		LOG_TRACE( 'Leave' )


	@RunThread
	def CurrentTimeThread(self):
		LOG_TRACE( 'begin_start thread' )

		loop = 0
		#rLock = threading.RLock()
		while self.mEnableThread:
			#LOG_TRACE( 'repeat <<<<' )

			#progress

			if  ( loop % 10 ) == 0 :
				#LOG_TRACE( 'loop=%d' %loop )
				if self.mFlag_ChannelChanged :
					self.GetEPGList()
				self.UpdateLocalTime( )


			#bmc.sleep(1000)
			time.sleep(1)
			self.mLocalTime += 1
			loop += 1

		LOG_TRACE( 'leave_end thread' )


	@GuiLock
	def UpdateLocalTime( self ) :
		
		try:
			self.mLocalTime = self.mDataCache.Datetime_GetLocalTime()
			self.mCtrlLblEventClock.setLabel( TimeToString( self.mLocalTime, TimeFormatEnum.E_HH_MM ) )			

			if self.mEventCopy :
				startTime = self.mEventCopy.mStartTime + self.mLocalOffset
				endTime   = startTime + self.mEventCopy.mDuration
				pastDuration = endTime - self.mLocalTime
				#LOG_TRACE('past[%s] time[%s] start[%s] duration[%s] offset[%s]'% (pastDuration,self.mLocalTime, self.mEventCopy.mStartTime, self.mEventCopy.mDuration,self.mLocalOffset ) )

				if self.mLocalTime > endTime: #Already past
					self.mCtrlProgress.setPercent( 100 )
					return

				elif self.mLocalTime < startTime :
					self.mCtrlProgress.setPercent( 0 )
					return

				if pastDuration < 0 : #Already past
					pastDuration = 0

				if self.mEventCopy.mDuration > 0 :
					percent = 100 - (pastDuration * 100.0/self.mEventCopy.mDuration)
				else :
					percent = 0

				LOG_TRACE( 'percent=%d' %percent )
				self.mCtrlProgress.setPercent( percent )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		LOG_TRACE( 'Leave' )


	@GuiLock
	def InitLabelInfo(self):
		
		if self.mFakeChannel :

			self.mCtrlProgress.setPercent(0)
			self.mEventCopy = None
			self.mCtrlLblChannelNumber.setLabel( '%s'% self.mFakeChannel.mNumber )
			self.mCtrlLblChannelName.setLabel( self.mFakeChannel.mName )
			self.mCtrlLblLongitudeInfo.setLabel('')
			self.mCtrlLblEventName.setLabel('')
			self.mCtrlLblEventStartTime.setLabel('')
			self.mCtrlLblEventEndTime.setLabel('')

			self.mCtrlImgLocked.setImage('')
			self.mCtrlImgICas.setImage('')
			self.mCtrlImgServiceType.setImage(self.mImgTV)
			self.mCtrlImgServiceTypeImg1.setImage('')
			self.mCtrlImgServiceTypeImg2.setImage('')
			self.mCtrlImgServiceTypeImg3.setImage('')
			self.mCtrlGropEventDescGroup.setVisible( False )
			self.mCtrlTxtBoxEventDescText1.reset()
			self.mCtrlTxtBoxEventDescText2.reset()
			ret = self.InitLongitudeInfo()
			self.mCtrlLblLongitudeInfo.setLabel( ret )


		else:
			LOG_TRACE( 'has no channel' )
		
			# todo 
			# show message box : has no channnel

		LOG_TRACE( 'Leave' )


	def InitLongitudeInfo( self ) :

		ret = ''

		try :
			self.mLocalTime = self.mDataCache.Datetime_GetLocalTime()
			LOG_TRACE('')
			satellite = self.mDataCache.Satellite_GetByChannelNumber( self.mCurrentChannel.mNumber )
			if satellite :
				ret = GetSelectedLongitudeString( satellite.mLongitude, satellite.mName )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		return ret


	def UpdateServiceType(self, aTvType):

		if aTvType == ElisEnum.E_SERVICE_TYPE_TV:
			#self.mCtrlImgServiceType.setImage(self.mImgTV)
			self.mImgTV = E_IMG_ICON_TV
		elif aTvType == ElisEnum.E_SERVICE_TYPE_RADIO:
			self.mImgTV = E_IMG_ICON_RADIO
		elif aTvType == ElisEnum.E_SERVICE_TYPE_DATA:
			pass
		else:
			self.mImgTV = ''
			LOG_TRACE( 'unknown ElisEnum tvType[%s]'% aTvType )



	def ShowEPGDescription(self, aVisible):
		LOG_TRACE( 'Enter' )

		if aVisible == True :
			LOG_TRACE('')
			if self.mEventCopy :
				LOG_TRACE('')
				
				self.mCtrlTxtBoxEventDescText1.setText( self.mEventCopy.mEventName )
				self.mCtrlTxtBoxEventDescText2.setText( self.mEventCopy.mEventDescription )
				self.mCtrlGropEventDescGroup.setVisible( True )

			else:
				LOG_TRACE( 'event is None' )
				self.mCtrlTxtBoxEventDescText1.setText('')
				self.mCtrlTxtBoxEventDescText2.setText('')
				self.mCtrlGropEventDescGroup.setVisible( True )				

		else :
			LOG_TRACE('')		
			self.mCtrlTxtBoxEventDescText1.reset()
			self.mCtrlTxtBoxEventDescText2.reset()
			self.mCtrlGropEventDescGroup.setVisible( False )
				

		self.mShowExtendInfo = aVisible
		
		LOG_TRACE( 'Leave' )

	def ShowDialog( self, aFocusid ):
		LOG_TRACE( 'Enter' )

		msg1 = ''
		msg2 = ''

		if aFocusid == self.mCtrlBtnMute.getId():
			msg1 = 'Mute'
			msg2 = 'test'

		elif aFocusid == self.mCtrlBtnTeletext.getId() :
			msg1 = 'Teletext'
			msg2 = 'test'


		elif aFocusid == self.mCtrlBtnSubtitle.getId() :
			msg1 = 'Subtitle'
			msg2 = 'test'

		elif aFocusid == self.mCtrlBtnStartRec.getId() :
			runningCount = self.mCommander.Record_GetRunningRecorderCount()
			LOG_TRACE( 'runningCount=%d' %runningCount)

			GuiLock2(True)
			if  runningCount < 2 :
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
				dialog.doModal()
			else:
				msg = 'Already %d recording(s) running' %runningCount
				xbmcgui.Dialog().ok('Infomation', msg )
			GuiLock2(False)

		elif aFocusid == self.mCtrlBtnStopRec.getId() :
			runningCount = self.mCommander.Record_GetRunningRecorderCount()
			LOG_TRACE( 'runningCount=%d' %runningCount )

			if  runningCount > 0 :
				GuiLock2(True)
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_STOP_RECORD )
				dialog.doModal()
				GuiLock2(False)
			

		LOG_TRACE( 'Leave' )


	def Close( self ):
		self.mEventBus.Deregister( self )

		self.mEnableThread = False
		self.CurrentTimeThread().join()
		
		#self.StopAsyncEPG()
		self.StopAsyncTune()
		self.StopAutomaticHide()

		self.close()

	def SetAutomaticHide( self, aHide=True ) :
		self.mAutomaticHide = aHide


	def GetAutomaticHide( self ) :
		return self.mAutomaticHide

	
	def AsyncAutomaticHide( self ) :
		if self.mShowExtendInfo ==  True :
			self.ShowEPGDescription( False )
	
		self.Close()


	def RestartAutomaticHide( self ) :
		self.StopAutomaticHide()
		self.StartAutomaticHide()

	
	def StartAutomaticHide( self ) :
		prop = ElisPropertyEnum( 'Channel Banner Duration', self.mCommander )
		bannerTimeout = prop.GetProp()
		self.mAutomaticHideTimer = threading.Timer( bannerTimeout, self.AsyncAutomaticHide )
		self.mAutomaticHideTimer.start()
		

	def StopAutomaticHide( self ) :
		if self.mAutomaticHideTimer and self.mAutomaticHideTimer.isAlive() :
			self.mAutomaticHideTimer.cancel()
			del self.mAutomaticHideTimer
			
		self.mAutomaticHideTimer = None


	def RestartAsyncTune( self ) :
		self.mFlag_ChannelChanged = True
		self.StopAsyncTune( )
		self.StartAsyncTune( )


	def StartAsyncTune( self ) :
		self.mAsyncTuneTimer = threading.Timer( 0.2, self.AsyncTuneChannel ) 				
		self.mAsyncTuneTimer.start()


	def StopAsyncTune( self ) :
		if self.mAsyncTuneTimer	and self.mAsyncTuneTimer.isAlive() :
			self.mAsyncTuneTimer.cancel()
			del self.mAsyncTuneTimer

		self.mAsyncTuneTimer  = None


	def AsyncTuneChannel( self ) :

		try :
			ret = self.mDataCache.Channel_SetCurrent( self.mFakeChannel.mNumber, self.mFakeChannel.mServiceType )
			#self.mFakeChannel.printdebug()
			if ret == True :
				self.mCurrentChannel = self.mDataCache.Channel_GetCurrent()
				self.mFakeChannel = self.mCurrentChannel
				self.mLastChannel = self.mCurrentChannel
				self.InitLabelInfo()
				self.UpdateONEvent()
				self.PincodeDialogLimit()

			else :
				LOG_ERR('Tune Fail')
			
		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def KeySearch( self, aKey ) :
		LOG_TRACE( 'Enter' )

		self.mFlag_OnEvent = False

		GuiLock2(True)
		dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CHANNEL_JUMP )
		if self.mEventCopy:
			dialog.SetDialogProperty( str(aKey), E_INPUT_MAX, None, self.mEventCopy.mStartTime)
		else :
			dialog.SetDialogProperty( str(aKey), E_INPUT_MAX, None)
		dialog.doModal()
		GuiLock2(False)

		self.mFlag_OnEvent = True

		isOK = dialog.IsOK()
		if isOK == E_DIALOG_STATE_YES :

			inputNumber = dialog.GetChannelLast()
			LOG_TRACE('=========== Jump chNum[%s]'% inputNumber)

			self.mJumpNumber = int(inputNumber)
			self.ChannelTune(CURR_CHANNEL)


		LOG_TRACE( 'Leave' )
	

