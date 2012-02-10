import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.BaseWindow import BaseWindow, Action
from pvr.gui.GuiConfig import *

import pvr.ElisMgr
from ElisAction import ElisAction
from ElisEnum import ElisEnum
from ElisEventBus import ElisEventBus
from ElisEventClass import *

from pvr.Util import RunThread, GuiLock, GuiLock2, MLOG, LOG_WARN, LOG_TRACE, LOG_ERR, TimeToString, TimeFormatEnum
from pvr.PublicReference import GetSelectedLongitudeString, EpgInfoTime, EpgInfoClock, EpgInfoComponentImage, EnumToString, ClassToList, AgeLimit, PincodeLimit 
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

NEXT_EPG 				= 0
PREV_EPG 				= 1

NEXT_CHANNEL			= 0
PREV_CHANNEL			= 1


class LivePlate(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		LOG_TRACE( 'args[0]=[%s]' % args[0] )
		LOG_TRACE( 'args[1]=[%s]' % args[1] )

		self.mCurrentChannel=None
		self.mLocalTime = 0
		self.mEventID = 0
		self.mPincodeEnter = FLAG_MASK_NONE
		self.mLastChannel = self.mCommander.Channel_GetCurrent()	
		self.mCurrentChannel = self.mLastChannel
		self.mFakeChannel = self.mLastChannel # Used  for zapping speed up
		self.mChannelChanged = True
		self.mShowExtendInfo = False
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

		self.mLocalOffset = self.mCommander.Datetime_GetLocalOffset()

		#get channel
		self.mCurrentChannel = self.mCommander.Channel_GetCurrent()
		self.mFakeChannel =	self.mCurrentChannel 
		#self.mCurrentChannel.printdebug()

		self.mChannelChanged = True
		self.mEventCopy = None
		self.mEPGList = None
		self.mEPGListIdx = 0

		self.UpdateServiceType( self.mCurrentChannel.mServiceType )
		self.InitLabelInfo()

		#get epg event right now, as this windows open
		self.mEventBus.Register( self )

		#run thread
		self.mEnableThread = True
		self.CurrentTimeThread()

		try :
			ret = None
			ret = self.mCommander.Epgevent_GetPresent()
			if ret :
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

		LOG_TRACE( 'Leave' )

	def onAction(self, aAction):
		#LOG_TRACE( 'Enter' )

		id = aAction.getId()
		self.GlobalAction( id )

		if id == Action.ACTION_PREVIOUS_MENU or id == Action.ACTION_PARENT_DIR:
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


		LOG_TRACE( 'Leave' )


	def onFocus(self, aControlId):
		#LOG_TRACE( 'control %d' % controlId )
		pass


	def onEvent(self, aEvent):
		#LOG_TRACE( 'Enter' )

		if self.mWinId == xbmcgui.getCurrentWindowId():
			if aEvent.getName() == ElisEventCurrentEITReceived.getName() :

				if self.mCurrentChannel == None :
					return -1
				
				if self.mCurrentChannel.mSid != aEvent.mSid or self.mCurrentChannel.mTsid != aEvent.mTsid or self.mCurrentChannel.mOnid != aEvent.mOnid :
					return -1

				if self.mCurrentChannel.mNumber != self.mFakeChannel.mNumber :
					return -1

				if self.mChannelChanged != True :
					return -1

				LOG_TRACE( '%d : %d' %(aEvent.mEventId, self.mEventID ) )
				#aEvent.printdebug()

				if aEvent.mEventId != self.mEventID :
					ret = None
					ret = self.mCommander.Epgevent_GetPresent()
					if ret :
						#ret.printdebug()

						if not self.mEventCopy or \
						ret.mEventId != self.mEventCopy.mEventId or \
						ret.mSid != self.mEventCopy.mSid or \
						ret.mTsid != self.mEventCopy.mTsid or \
						ret.mOnid != self.mEventCopy.mOnid :
							LOG_TRACE('epg DIFFER')
							self.mEventID = aEvent.mEventId
							self.mEventCopy = ret

							#update label
							self.UpdateONEvent( ret )

		else:
			LOG_TRACE( 'LivePlate winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId()) )


		#LOG_TRACE( 'Leave' )


	def ChannelTune(self, aDir):
		LOG_TRACE( 'Enter' )

		if aDir == PREV_CHANNEL:
		
			prevChannel = self.mCommander.Channel_GetPrev()

			if prevChannel == None or prevChannel.mError != 0 :
				return

			self.mFakeChannel = prevChannel
			self.UpdateServiceType( self.mFakeChannel.mServiceType )
			self.RestartAsyncTune()

		elif aDir == NEXT_CHANNEL:
			nextChannel = self.mCommander.Channel_GetNext()

			if nextChannel == None or nextChannel.mError != 0 :
				return

			self.mFakeChannel = nextChannel
			self.UpdateServiceType( self.mFakeChannel.mServiceType )
			self.RestartAsyncTune()

		if self.mAutomaticHide == True :
			self.RestartAutomaticHide()

		self.mChannelChanged = True
		LOG_TRACE( 'Leave' )


	def EPGNavigation(self, aDir ):
		LOG_TRACE( 'Enter' )

		if self.mChannelChanged :
			self.GetEPGList()

		lastIdx = len(self.mEPGList) - 1
		if aDir == NEXT_EPG:
			if self.mEPGListIdx+1 > lastIdx :
				self.mEPGListIdx = lastIdx
			else :
				self.mEPGListIdx += 1

			LOG_TRACE('NEXT_EPG')

		elif aDir == PREV_EPG:
			if self.mEPGListIdx-1 < 0 :
				self.mEPGListIdx = 0
			else :
				self.mEPGListIdx -= 1

			LOG_TRACE('PREV_EPG')

		self.RestartAsyncEPG()
		#self.PincodeDialogLimit()

		LOG_TRACE( 'Leave' )

	def GetEPGList( self ) :
		LOG_TRACE( 'Enter' )

		ret = None

		try :
			if self.mCurrentChannel :
				self.mEPGList = None
				self.mEPGList = 0
				ch = self.mCurrentChannel
				gmtime = self.mCommander.Datetime_GetGMTTime()
				gmtFrom = gmtime - ( 3600 * 24 * 7 )
				gmtUntil= gmtime + ( 3600 * 24 * 7 )
				maxCount= 100
				ret = None
				ret = self.mCommander.Epgevent_GetList( ch.mSid, ch.mTsid, ch.mOnid, gmtFrom, gmtUntil, maxCount )
				time.sleep(0.05)
				#LOG_TRACE('=============epg len[%s] list[%s]'% (len(ret),ClassToList('convert', ret )) )
				if ret :
					self.mEPGList = ret

				self.mChannelChanged = False

				#retList=[]
				#retList.append(self.mEventCopy)
				#LOG_TRACE('==========[%s]'% ClassToList('convert', retList) )
				#LOG_TRACE('EPGinfo len[%s] [%s]'% (len(self.mEPGList), ClassToList('convert', self.mEPGList)) )
				idx = 0
				for item in self.mEPGList :
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

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		LOG_TRACE( 'Leave' )


	@GuiLock
	def UpdateONEvent(self, aEvent):
		LOG_TRACE( 'Enter' )
		#LOG_TRACE( 'component [%s]'% EpgInfoComponentImage ( aEvent ))

		if self.mCurrentChannel :
			ch = self.mCurrentChannel

			if ch.mLocked :
				self.mCtrlImgLocked.setImage( E_IMG_ICON_LOCK )
				if self.mChannelChanged == True :
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
				if self.mChannelChanged == True :
					isLimit = AgeLimit( self.mCommander, aEvent.mAgeRating )
					if isLimit == True :
						self.mPincodeEnter |= FLAG_MASK_ADD
						LOG_TRACE( 'AgeLimit[%s]'% isLimit )

			except Exception, e:
				LOG_TRACE( 'Error exception[%s]'% e )

		else:
			LOG_TRACE( 'aEvent null' )


		if self.mChannelChanged :
			self.GetEPGList()

		LOG_TRACE( 'Leave' )


	def PincodeDialogLimit( self ) :
		LOG_TRACE( 'Enter' )

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

				stbPin = PincodeLimit( self.mCommander, inputPin )
				if inputPin == None or inputPin == '' :
					inputPin = ''

				#LOG_TRACE( 'mask[%s] inputPin[%s] stbPin[%s]'% (self.mPincodeEnter, inputPin, stbPin) )

				if inputPin == str('%s'% stbPin) :
					self.mPincodeEnter = FLAG_MASK_NONE
					#ret = self.mCommander.Channel_SetInitialBlank( False )
					self.mCommander.Player_AVBlank( False, True )

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
				self.UpdateLocalTime( )


			#bmc.sleep(1000)
			time.sleep(1)
			self.mLocalTime += 1
			loop += 1

		LOG_TRACE( 'leave_end thread' )


	@GuiLock
	def UpdateLocalTime( self ) :
		
		try:
			self.mLocalTime = self.mCommander.Datetime_GetLocalTime()
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
		LOG_TRACE( 'Enter' )
		
		if self.mFakeChannel :

			self.mCtrlProgress.setPercent(0)
			self.mEventCopy = None
			self.mCtrlLblChannelNumber.setLabel( '%d' %self.mFakeChannel.mNumber )
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
			self.mLocalTime = self.mCommander.Datetime_GetLocalTime()
			longitude = None
			LOG_TRACE('')
			longitude = self.mCommander.Satellite_GetByChannelNumber( self.mCurrentChannel.mNumber, self.mCurrentChannel.mServiceType )
			if longitude :
				ret = GetSelectedLongitudeString( longitude.mLongitude, self.mCurrentChannel.mName )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		LOG_TRACE( 'Leave' )
		return ret


	def UpdateServiceType(self, aTvType):
		LOG_TRACE( 'Enter' )
		LOG_TRACE( 'serviceType[%s]' % aTvType )

		if aTvType == ElisEnum.E_SERVICE_TYPE_TV:
			#self.mCtrlImgServiceType.setImage(self.mImgTV)
			self.mImgTV = 'confluence/tv.png'
		elif aTvType == ElisEnum.E_SERVICE_TYPE_RADIO:
			pass
		elif aTvType == ElisEnum.E_SERVICE_TYPE_DATA:
			pass
		else:
			self.mImgTV = ''
			LOG_TRACE( 'unknown ElisEnum tvType[%s]'% aTvType )

		LOG_TRACE( 'Leave' )


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
				dialog = diamgr.GetInstance().GetDialog( diamgr.DIALOG_ID_START_RECORD )
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
				dialog = diamgr.GetInstance().GetDialog( diamgr.DIALOG_ID_STOP_RECORD )
				dialog.doModal()
				GuiLock2(False)
			

		LOG_TRACE( 'Leave' )


	def Close( self ):
		self.mEventBus.Deregister( self )

		self.mEnableThread = False
		self.CurrentTimeThread().join()
		
		self.StopAsyncEPG()
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
		bannerTimeout = ElisPropertyEnum( 'Channel Banner Duration', self.mCommander ).GetProp( )
		self.mAutomaticHideTimer = threading.Timer( bannerTimeout, self.AsyncAutomaticHide )
		self.mAutomaticHideTimer.start()
		

	def StopAutomaticHide( self ) :
		if self.mAutomaticHideTimer and self.mAutomaticHideTimer.isAlive() :
			self.mAutomaticHideTimer.cancel()
			del self.mAutomaticHideTimer
			
		self.mAutomaticHideTimer = None


	def RestartAsyncTune( self ) :
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
		LOG_TRACE( 'Enter' )

		try :
			ret = self.mCommander.Channel_SetCurrent( self.mFakeChannel.mNumber, self.mFakeChannel.mServiceType )
			#self.mFakeChannel.printdebug()
			if ret == True :
				self.mCurrentChannel = self.mFakeChannel
				self.mLastChannel = self.mCurrentChannel
				self.InitLabelInfo()
				ret = None
				ret = self.mCommander.Epgevent_GetPresent()
				if ret :
					self.mEventCopy = ret
					self.UpdateONEvent(self.mEventCopy)

				self.PincodeDialogLimit()
			else :
				LOG_ERR('Tune Fail')
			
		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		LOG_TRACE( 'Leave' )


	def RestartAsyncEPG( self ) :
		self.StopAsyncEPG( )
		self.StartAsyncEPG( )


	def StartAsyncEPG( self ) :
		self.mAsyncEPGTimer = threading.Timer( 0.2, self.AsyncTuneEPG ) 				
		self.mAsyncEPGTimer.start()


	def StopAsyncEPG( self ) :
		if self.mAsyncEPGTimer	and self.mAsyncEPGTimer.isAlive() :
			self.mAsyncEPGTimer.cancel()
			del self.mAsyncEPGTimer

		self.mAsyncEPGTimer  = None


	def AsyncTuneEPG( self ) :
		LOG_TRACE( 'Enter' )

		try :

			LOG_TRACE('ch[%s] len[%s] idx[%s]'% (self.mCurrentChannel.mNumber, len(self.mEPGList),self.mEPGListIdx) )
			ret = self.mEPGList[self.mEPGListIdx]

			if ret :
				self.InitLabelInfo()
				GuiLock2(True)
				self.mEventCopy = ret
				GuiLock2(False)

				self.UpdateServiceType( self.mCurrentChannel.mServiceType )
				self.UpdateONEvent( self.mEventCopy )

				retList = []
				retList.append( self.mEventCopy )
				LOG_TRACE( 'idx[%s] epg[%s]'% (self.mEPGListIdx, ClassToList( 'convert', retList )) )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		LOG_TRACE( 'Leave' )

