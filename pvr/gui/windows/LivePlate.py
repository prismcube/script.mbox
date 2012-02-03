import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as winmgr
import pvr.gui.DialogMgr as diamgr
from pvr.gui.BaseWindow import BaseWindow, Action
from pvr.gui.GuiConfig import *

import pvr.ElisMgr
from ElisAction import ElisAction
from ElisEnum import ElisEnum
from ElisEventBus import ElisEventBus
from ElisEventClass import *

from pvr.Util import RunThread, GuiLock, GuiLock2, MLOG, LOG_WARN, LOG_TRACE, LOG_ERR
from pvr.PublicReference import GetSelectedLongitudeString, EpgInfoTime, EpgInfoClock, EpgInfoComponentImage, EnumToString, ClassToList, AgeLimit

import threading, time, os

#debug log
import logging
from inspect import currentframe

#log = logging.getLogger('mythbox.ui')
#mlog = logging.getLogger('mythbox.method')


FLAG_MASK_ADD  = 0x01
FLAG_MASK_NONE = 0x00
FLAG_CLOCKMODE_ADMYHM = 1
FLAG_CLOCKMODE_AHM    = 2
FLAG_CLOCKMODE_HMS    = 3
FLAG_CLOCKMODE_HHMM   = 4
FLAG_CLOCKMODE_INTTIME= 5



class LivePlate(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		LOG_TRACE( 'args[0]=[%s]' % args[0] )
		LOG_TRACE( 'args[1]=[%s]' % args[1] )

		self.mCommander = pvr.ElisMgr.GetInstance().GetCommander()
		self.mEventBus = pvr.ElisMgr.GetInstance().GetEventBus()

		self.mLastFocusId = None
		self.mCurrentChannel=None
		self.mLocalTime = 0
		self.mEventID = 0
		self.mPincodeEnter = FLAG_MASK_NONE
		self.mLastChannel = 	self.mCommander.Channel_GetCurrent()	
		self.mCurrentChannel =  self.mLastChannel


	def __del__(self):
		LOG_TRACE( 'destroyed LivePlate' )

		# end thread CurrentTimeThread()
		self.mEnableThread = False

	def onInit(self):
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId )
		LOG_TRACE( 'winID[%d]'% self.mWinId)

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
		#self.mCtrlBtnTSbanner          = self.getControl( 630 )

		self.mCtrlBtnPrevEpg           = self.getControl( 702 )
		self.mCtrlBtnNextEpg           = self.getControl( 706 )


		self.mImgTV    = 'confluence/tv.png'
		self.mCtrlLblEventClock.setLabel('')

		self.mToggleFlag=False
		self.mLocalOffset = self.mCommander.Datetime_GetLocalOffset()

		#get channel
		self.mCurrentChannel = self.mCommander.Channel_GetCurrent()
		#self.mCurrentChannel.printdebug()

		self.mEventCopy = None

		self.UpdateServiceType( self.mCurrentChannel.mServiceType )
		self.InitLabelInfo()
		self.UpdateVolume(Action.ACTION_MUTE)

		try :
			ret = None
			ret = self.mCommander.Epgevent_GetPresent()
			if ret :
				self.mEventCopy = ret
				self.UpdateONEvent(self.mEventCopy)

				retList = []
				retList.append( self.mEventCopy )
				LOG_TRACE( 'epgevent_GetPresent[%s]'% ClassToList( 'convert', retList ) )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )



		"""
		#get last zapping mode
		ret = []
		ret = self.mCommander.Zappingmode_GetCurrent()
		ret.printdebug()
		try:
			LOG_TRACE( 'zappingMode[%s] sortMode[%s] serviceType[%s]'% \
				(EnumToString('mode', ret.mMode ), \
				 EnumToString('sort', ret.mSortingMode ), \
				 EnumToString('type', ret.mServiceType )) )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )
		"""


		#get epg event right now, as this windows open
		self.mEventBus.Register( self )

		#run thread
		self.mEnableThread = True
		self.CurrentTimeThread()

		LOG_TRACE( 'Leave' )


	def onAction(self, aAction):
		#LOG_TRACE( 'Enter' )
		id = aAction.getId()

		if id == Action.ACTION_PREVIOUS_MENU or id == Action.ACTION_PARENT_DIR:
			LOG_TRACE( 'esc close' )
			self.DescboxToggle('close')
			self.mEnableThread = False
			self.CurrentTimeThread().join()
			#winmgr.GetInstance().ShowWindow( winmgr.WIN_ID_MAINMENU )
			self.close()

			"""
			self.GetFocusId()
			if self.mFocusId >= self.mCtrlBtnExInfo.getId() and self.mFocusId <= self.mCtrlBtnMute.getId():
				self.ShowEPGDescription(self.mFocusId, self.mEventCopy)

			else:
				# end thread CurrentTimeThread()
				self.mEnableThread = False
				self.CurrentTimeThread().join()

				self.close( )
#				winmgr.GetInstance().ShowWindow( winmgr.WIN_ID_CHANNEL_LIST_WINDOW )
#				winmgr.GetInstance().ShowWindow( winmgr.WIN_ID_NULLWINDOW )
#				winmgr.Shutdown()
			"""

		elif id == Action.ACTION_SELECT_ITEM:
			LOG_TRACE( 'youn:%s' % id )
	
		elif id == Action.ACTION_SHOW_INFO	:
			self.ShowEPGDescription( self.mCtrlBtnExInfo.getId(), self.mEventCopy)

		elif id == Action.ACTION_MOVE_LEFT:
			self.GetFocusId()
			if self.mFocusId == self.mCtrlBtnPrevEpg.getId():			
				self.ChannelTune(id)

		elif id == Action.ACTION_MOVE_RIGHT:
			self.GetFocusId()
			if self.mFocusId == self.mCtrlBtnNextEpg.getId():
				self.ChannelTune(id)

		elif id == Action.ACTION_PAGE_UP:
			self.ChannelTune(id)

		elif id == Action.ACTION_PAGE_DOWN:
			self.ChannelTune(id)

		elif id == Action.ACTION_MUTE:
			self.UpdateVolume(id)

		elif id == Action.ACTION_PAUSE:
			self.DescboxToggle('close')
			self.mEnableThread = False
			self.CurrentTimeThread().join()
			winmgr.GetInstance().ShowWindow( winmgr.WIN_ID_TIMESHIFT_PLATE )

		elif id == 13: #'x'
			#this is test
			LOG_TRACE( 'cwd[%s]'% xbmc.getLanguage() )

		"""
		elif id == Action.ACTION_VOLUME_UP:
		
			vol = self.mCommander.Player_GetVolume()
			vol = vol + pvr.gui.GuiConfig.VOLUME_STEP
			
			if vol > pvr.gui.GuiConfig.MAX_VOLUME :
				vol = pvr.gui.GuiConfig.MAX_VOLUME

			self.mCommander.Player_SetVolume( vol )

		elif id == Action.ACTION_VOLUME_DOWN:
		
			vol = self.mCommander.player_GetVolume()
			vol = vol - pvr.gui.GuiConfig.VOLUME_STEP
			
			if vol < 0 :
				vol = 0
				
			self.mCommander.Player_SetVolume( vol )
		"""

		#LOG_TRACE( 'Leave' )



	def onClick(self, aControlId):
		LOG_TRACE( 'control %d' % aControlId )

		if aControlId == self.mCtrlBtnMute.getId():
			self.UpdateVolume( Action.ACTION_MUTE )

		elif aControlId == self.mCtrlBtnExInfo.getId() :
			LOG_TRACE( 'click expantion info' )
			self.ShowEPGDescription(aControlId, self.mEventCopy)

		elif aControlId == self.mCtrlBtnTeletext.getId() :
			LOG_TRACE( 'click teletext' )
			self.ShowDialog( aControlId )

		elif aControlId == self.mCtrlBtnSubtitle.getId() :
			LOG_TRACE( 'click subtitle' )
			self.ShowDialog( aControlId )

		elif aControlId == self.mCtrlBtnStartRec.getId() :
			LOG_TRACE( 'click start recording' )
			self.ShowDialog( aControlId )

		elif aControlId == self.mCtrlBtnStopRec.getId() :
			LOG_TRACE( 'click stop recording' )
			self.ShowDialog( aControlId )

		elif aControlId == self.mCtrlBtnPrevEpg.getId() :
			self.ChannelTune(Action.ACTION_MOVE_LEFT)

		elif aControlId == self.mCtrlBtnNextEpg.getId() :
			self.ChannelTune(Action.ACTION_MOVE_RIGHT)


		"""
		elif aControlId == self.mCtrlBtnTSbanner.getId() :
			LOG_TRACE( 'click Time Shift banner' )
			self.mEnableThread = False
			self.CurrentTimeThread().join()
			self.close()

			winmgr.GetInstance().ShowWindow( winmgr.WIN_ID_TIMESHIFT_PLATE )
		"""

		LOG_TRACE( 'Leave' )


	def onFocus(self, aControlId):
		#LOG_TRACE( 'control %d' % controlId )
		pass


	def onEvent(self, aEvent):
		LOG_TRACE( 'Enter' )
		#LOG_TRACE( 'aEvent len[%s]'% len(aEvent) )
		#ClassToList( 'print', aEvent )

		if self.mWinId == xbmcgui.getCurrentWindowId():
			if aEvent.getName() == ElisEventCurrentEITReceived.getName() :

				if int(aEvent.mEventId) != int(self.mEventID) :
					ret = None
					ret = self.mCommander.Epgevent_GetPresent()
					if ret :
						self.mEventID = aEvent.mEventId
						if not self.mEventCopy or \
						   ret.mEventId != self.mEventCopy.mEventId or \
						   ret.mSid != self.mEventCopy.mSid or \
						   ret.mTsid != self.mEventCopy.mTsid or \
						   ret.mOnid != self.mEventCopy.mOnid :
							LOG_TRACE('epg DIFFER')
							self.mEventCopy = ret

							#update label
							self.UpdateONEvent( ret )
						else:
							LOG_TRACE('epg SAME')


			else :
				LOG_TRACE( 'event unknown[%s]'% aEvent.getName() )
		else:
			LOG_TRACE( 'LivePlate winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId()) )


		LOG_TRACE( 'Leave' )


	def ChannelTune(self, aActionID):
		LOG_TRACE( 'Enter' )
		LOG_TRACE( 'tuneActionID[%s]'% aActionID )

		if aActionID == Action.ACTION_PAGE_DOWN:
			LOG_TRACE( 'ACTION_PREVIOUS_CH control %d' % aActionID )
			priv_ch = None
			priv_ch = self.mCommander.Channel_GetPrev()

			if priv_ch :
				retList = []
				retList.append( priv_ch )
				LOG_TRACE( 'priv_ch[%s]' % ClassToList( 'convert', retList ) )

			try:
				self.mLastChannel = self.mCurrentChannel
				ret = self.mCommander.Channel_SetCurrent( priv_ch.mNumber, priv_ch.mServiceType )

				if ret :
					self.mCurrentChannel = self.mCommander.Channel_GetCurrent()
					if self.mCurrentChannel :
						self.UpdateServiceType( priv_ch.mServiceType )
						self.InitLabelInfo()

			except Exception, e :
				LOG_TRACE( 'Error exception[%s]'% e )

		elif aActionID == Action.ACTION_PAGE_UP:
			LOG_TRACE( 'ACTION_NEXT_CH control %d' % aActionID )
			next_ch = None
			next_ch = self.mCommander.Channel_GetNext()

			if next_ch :
				retList = []
				retList.append( next_ch )
				LOG_TRACE( 'next_ch[%s]' % ClassToList( 'convert', retList ) )

			try:
				self.mLastChannel = self.mCurrentChannel
				ret = self.mCommander.Channel_SetCurrent( next_ch.mNumber, next_ch.mServiceType )

				if ret :
					self.mCurrentChannel = self.mCommander.Channel_GetCurrent()
					if self.mCurrentChannel :
						self.UpdateServiceType( next_ch.mServiceType )
						self.InitLabelInfo()

			except Exception, e :
				LOG_TRACE( 'Error exception[%s]'% e )

		elif aActionID == Action.ACTION_MOVE_LEFT:
			#epg priv
			ret = None
			ret = self.mCommander.Epgevent_GetPresent()

			if ret :
				retList = []
				retList.append( ret )
				LOG_TRACE( 'epgevent_GetPresent() ret[%s]'% ClassToList( 'convert', retList ) )
				self.mEventCopy = ret
				self.UpdateONEvent( ret )

		elif aActionID == Action.ACTION_MOVE_RIGHT:
			#epg next
			ret = None
			ret = self.mCommander.Epgevent_GetFollowing()

			if ret :
				retList = []
				retList.append( ret )
				LOG_TRACE( 'epgevent_GetFollowing() ret[%s]'% ClassToList( 'convert', retList ) )
				self.mEventCopy = ret
				self.UpdateONEvent( ret )



		LOG_TRACE( 'Leave' )


	@GuiLock
	def UpdateONEvent(self, aEvent):
		LOG_TRACE( 'Enter' )
		#LOG_TRACE( 'component [%s]'% EpgInfoComponentImage ( aEvent ))

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
				isLimit = AgeLimit( self.mCommander, aEvent.mAgeRating )
				if isLimit == True :
					self.mPincodeEnter |= FLAG_MASK_ADD
					LOG_TRACE( 'AgeLimit[%s]'% isLimit )

			except Exception, e:
				LOG_TRACE( 'Error exception[%s]'% e )

		else:
			LOG_TRACE( 'aEvent null' )


		#popup pin-code dialog
		if self.mPincodeEnter > FLAG_MASK_NONE :
			msg1 = Msg.Strings(MsgId.LANG_INPUT_PIN_CODE)
			msg2 = Msg.Strings(MsgId.LANG_CURRENT_PIN_CODE)
			kb = xbmc.Keyboard( msg1, '1111', False )
			kb.doModal()
			if( kb.isConfirmed() ) :
				inputPass = kb.getText()
				#self.mPincodeEnter = FLAG_MASK_NONE
				LOG_TRACE( 'password[%s]'% inputPass )

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

			#local clock
			ret = EpgInfoClock( FLAG_CLOCKMODE_AHM, self.mLocalTime, loop )
			self.mCtrlLblEventClock.setLabel( ret[0] )

			xbmc.sleep(1000)
			#self.mLocalTime += 1
			loop += 1

		LOG_TRACE( 'leave_end thread' )


	@GuiLock
	def UpdateLocalTime( self ) :
		
		try:
			self.mLocalTime = self.mCommander.Datetime_GetLocalTime()

			if self.mEventCopy :
				startTime = self.mEventCopy.mStartTime + self.mLocalOffset
				endTime   = startTime + self.mEventCopy.mDuration
				pastDuration = endTime - self.mLocalTime
				#LOG_TRACE('past[%s] time[%s] start[%s] duration[%s] offset[%s]'% (pastDuration,self.mLocalTime, self.mEventCopy.mStartTime, self.mEventCopy.mDuration,self.mLocalOffset ) )

				if self.mLocalTime > endTime: #Already past
					pastDuration = 100
				elif self.mLocalTime < startTime :
					pastDuration = 0

				if pastDuration < 0 : #Already past
					pastDuration = 100

				if self.mEventCopy.mDuration > 0 :
					percent = 100 - (pastDuration * 100.0/self.mEventCopy.mDuration )
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
		
		if self.mCurrentChannel :

			self.mCtrlProgress.setPercent(0)
			self.mEventCopy = []

			self.mCtrlLblChannelNumber.setLabel( str('%s'% self.mCurrentChannel.mNumber) )
			self.mCtrlLblChannelName.setLabel( self.mCurrentChannel.mName )
			self.mCtrlLblLongitudeInfo.setLabel('')
			self.mCtrlLblEventName.setLabel('')
			self.mCtrlLblEventStartTime.setLabel('')
			self.mCtrlLblEventEndTime.setLabel('')

			#self.mCtrlImgServiceType.setImage('')
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
			#self.mCtrlImgServiceType.setImage('')
			self.mImgTV = ''
			LOG_TRACE( 'unknown ElisEnum tvType[%s]'% aTvType )

		LOG_TRACE( 'Leave' )


	def UpdateVolume(self, aCmd):
		LOG_TRACE( 'Enter' )

		if aCmd == Action.ACTION_MUTE:
			mute = self.mCommander.Player_GetMute()
			LOG_TRACE( 'mute:current[%s]'% mute )
			if mute == False:
				ret = self.mCommander.Player_SetMute( True )

			else:
				ret = self.mCommander.Player_SetMute( False )


		elif aCmd == Action.ACTION_VOLUME_UP:
			pass
		elif aCmd == Action.ACTION_VOLUME_UP:
			pass

		LOG_TRACE( 'Leave' )


	def ShowEPGDescription(self, aFocusid, aEvent):
		LOG_TRACE( 'Enter' )

		if aFocusid == self.mCtrlBtnExInfo.getId():
			if aEvent :
				LOG_TRACE( 'epgDescription[%s]' % aEvent.mEventDescription )
				self.mCtrlTxtBoxEventDescText1.setText( aEvent.mEventName )
				self.mCtrlTxtBoxEventDescText2.setText( aEvent.mEventDescription )

			else:
				LOG_TRACE( 'event is None' )
				self.mCtrlTxtBoxEventDescText1.setText('')
				self.mCtrlTxtBoxEventDescText2.setText('')

		self.DescboxToggle('toggle')

		#self.mCtrlEventDescription.setVisibleCondition('[Control.IsVisible(100)]',True)
		#self.mCtrlEventDescription.setEnabled(True)
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
			

		#ret = xbmcgui.Dialog().ok(msg1, msg2)
		#LOG_TRACE( 'dialog ret[%s]' % ret )

		LOG_TRACE( 'Leave' )


	def DescboxToggle( self, aCmd ):
		LOG_TRACE( 'Enter' )

		if aCmd == 'toggle':
			if self.mToggleFlag == True:
				self.mCtrlTxtBoxEventDescText1.reset()
				self.mCtrlTxtBoxEventDescText2.reset()
				self.mCtrlGropEventDescGroup.setVisible( False )
				self.mToggleFlag = False
			else:
				self.mCtrlGropEventDescGroup.setVisible( True )
				self.mToggleFlag = True

		elif aCmd == 'close':
			if self.mToggleFlag == True:
				self.mCtrlTxtBoxEventDescText1.reset()
				self.mCtrlTxtBoxEventDescText2.reset()
				self.mCtrlGropEventDescGroup.setVisible( False )
				self.mToggleFlag = False

		LOG_TRACE( 'Leave' )
	"""
	def GetLastChannel( self ):
		return self.mLastChannel
		
	def SetLastChannel( self, lastChannel ):
		self.mLastChannel = lastChannel
	"""

