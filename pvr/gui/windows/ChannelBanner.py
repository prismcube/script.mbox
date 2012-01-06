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

#from threading import Thread
from ElisEventClass import *
from pvr.Util import RunThread, GuiLock, MLOG, LOG_WARN
from pvr.PublicReference import GetSelectedLongitudeString, EpgInfoTime, EpgInfoClock, EpgInfoComponentImage, EnumToString, ClassToList, AgeLimit

import threading, time, os

#debug log
import logging
from inspect import currentframe

log = logging.getLogger('mythbox.ui')
mlog = logging.getLogger('mythbox.method')


FLAG_MASK_ADD  = 0x01
FLAG_MASK_NONE = 0x00

class ChannelBanner(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		print 'args[0]=[%s]' % args[0]
		print 'args[1]=[%s]' % args[1]

		#summary
		self.__file__ = os.path.basename( currentframe().f_code.co_filename )

		self.mCommander = pvr.ElisMgr.GetInstance().GetCommander()
		self.mLastFocusId = None
		self.mCurrentChannel=None
		self.mLocalTime = 0
		self.mEventID = 0
		self.mPincodeEnter = FLAG_MASK_NONE
		#self.mLastChannel = 	self.mCommander.Channel_GetCurrent()	
		#self.mCurrentChannel =  self.mLastChannel
		self.mEventBus = pvr.ElisMgr.GetInstance().GetEventBus()
		#self.mEventBus.register( self )


	def __del__(self):
		print '[%s:%s] destroyed ChannelBanner'% (self.__file__, currentframe().f_lineno)

		# end thread CurrentTimeThread()
		self.mUntilThread = False

	def onInit(self):
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId )
		print '[%s:%s]winID[%d]'% (self.__file__, currentframe().f_lineno, self.mWinId)

		#get event
		#request = EventRequest(self)
		self.mCtrlChannelNumber  = self.getControl( 601 )
		self.mCtrlChannelName    = self.getControl( 602 )
		self.mCtrlImgServiceType    = self.getControl( 603 )
		self.mCtrlImgServiceTypeImg1= self.getControl( 604 )
		self.mCtrlImgServiceTypeImg2= self.getControl( 605 )
		self.mCtrlImgServiceTypeImg3= self.getControl( 606 )
		self.mCtrlEventClock     = self.getControl( 610 )
		self.mCtrlLongitudeInfo  = self.getControl( 701 )
		self.mCtrlEventName      = self.getControl( 703 )
		self.mCtrlEventStartTime = self.getControl( 704 )
		self.mCtrlEventEndTime   = self.getControl( 705 )
		self.mCtrlProgress       = self.getControl( 707 )
		self.mCtrlEventDescGroup = self.getControl( 800 )
		self.mCtrlEventDescText1 = self.getControl( 801 )
		self.mCtrlEventDescText2 = self.getControl( 802 )
		#self.mCtrlProgress = xbmcgui.ControlProgress(100, 250, 125, 75)
		#self.mCtrlProgress(self.Progress)

		#button icon
		self.mCtrlBtnExInfo      = self.getControl( 621 )
		self.mCtrlBtnTeletext    = self.getControl( 622 )
		self.mCtrlBtnSubtitle    = self.getControl( 623 )
		self.mCtrlBtnStartRec    = self.getControl( 624 )
		self.mCtrlBtnStopRec     = self.getControl( 625 )
		self.mCtrlBtnMute        = self.getControl( 626 )
		self.mCtrlBtnMuteToggled = self.getControl( 627 )
		self.mCtrlBtnTSbanner    = self.getControl( 630 )
		
		self.mCtrlBtnPrevEpg     = self.getControl( 702 )
		self.mCtrlBtnNextEpg     = self.getControl( 706 )
		

		self.mImgTV    = 'confluence/tv.png'
		self.mCtrlEventClock.setLabel('')

		self.mToggleFlag=False
		self.mEpgStartTime = 0
		self.mEpgDuration = 0
		self.mLocalOffset = self.mCommander.Datetime_GetLocalOffset()

		#get channel
		self.mCurrentChannel = self.mCommander.Channel_GetCurrent()
		self.mCurrentChannel.printdebug()

		self.InitLabelInfo()
		self.UpdateVolume(Action.ACTION_MUTE)
	
		self.UpdateServiceType( self.mCurrentChannel.mServiceType )


		"""
		#get last zapping mode
		ret = []
		ret = self.mCommander.Zappingmode_GetCurrent()
		ret.printdebug()
		try:
			print 'zappingMode[%s] sortMode[%s] serviceType[%s]'% \
				(enumToString('mode', ret.mMode ), \
				 enumToString('sort', ret.mSortingMode ), \
				 enumToString('type', ret.mServiceType ))

		except Exception, e :
			print '[%s:%s] Error exception[%s]'% (	\
				self.__file__,						\
				currentframe().f_lineno,			\
				e )
		"""


		#get epg event right now, as this windows open
		ret = None
		ret=self.mCommander.Epgevent_GetPresent()
		if ret :
			self.mEventCopy = ret
			self.UpdateONEvent(self.mEventCopy)
		print 'epgevent_GetPresent[%s]'% ClassToList( 'convert', self.mEventCopy )


		#run thread
		self.mUntilThread = True
		self.CurrentTimeThread()


	def onAction(self, aAction):
		id = aAction.getId()
		focusid = self.getFocusId()
		
		if id == Action.ACTION_PREVIOUS_MENU:
			print 'youn check action menu'
			self.DescboxToggle('close')
			self.mUntilThread = False
			self.CurrentTimeThread().join()
			winmgr.GetInstance().ShowWindow( winmgr.WIN_ID_MAINMENU )

		elif id == Action.ACTION_SELECT_ITEM:
			print '===== test youn: ID[%s]' % id
			log.debug('youn:%s' % id)
	
		elif id == Action.ACTION_PARENT_DIR:
			print 'youn check ation back'

			self.DescboxToggle('close')
			self.mUntilThread = False
			self.CurrentTimeThread().join()
			self.close( )
			#winmgr.GetInstance().ShowWindow( winmgr.WIN_ID_NULLWINDOW )


			"""
			if focusid >= self.mCtrlBtnExInfo.getId() and focusid <= self.mCtrlBtnMute.getId():
				self.ShowEPGDescription(focusid, self.mEventCopy)

			else:
				# end thread CurrentTimeThread()
				self.mUntilThread = False
				self.CurrentTimeThread().join()

				self.close( )
#				winmgr.GetInstance().ShowWindow( winmgr.WIN_ID_CHANNEL_LIST_WINDOW )
#				winmgr.GetInstance().ShowWindow( winmgr.WIN_ID_NULLWINDOW )
#				winmgr.Shutdown()
			"""

		elif id == Action.ACTION_SHOW_INFO	:
			self.ShowEPGDescription( self.mCtrlBtnExInfo.getId(), self.mEventCopy)

		elif id == Action.ACTION_MOVE_LEFT:
			if focusid == self.mCtrlBtnPrevEpg.getId():			
				self.ChannelTune(id)

		elif id == Action.ACTION_MOVE_RIGHT:
			if focusid == self.mCtrlBtnNextEpg.getId():
				self.ChannelTune(id)

		elif id == Action.ACTION_PAGE_UP:
			self.ChannelTune(id)

		elif id == Action.ACTION_PAGE_DOWN:
			self.ChannelTune(id)

		elif id == Action.ACTION_MUTE:
			self.UpdateVolume(id)

		elif id == Action.ACTION_PAUSE:
			self.DescboxToggle('close')
			self.mUntilThread = False
			self.CurrentTimeThread().join()
			winmgr.GetInstance().ShowWindow( winmgr.WIN_ID_TIMESHIFT_BANNER )

		else:
			#print 'youn check action unknown id=%d' % id
			#self.ChannelTune(id)
			pass


		"""
		elif id == Action.ACTION_VOLUME_UP:
		
			vol = int ( self.mCommander.player_GetVolume( )[0] )
			vol = vol + pvr.gui.GuiConfig.VOLUME_STEP
			
			if vol > pvr.gui.GuiConfig.MAX_VOLUME :
				vol = pvr.gui.GuiConfig.MAX_VOLUME

			self.mCommander.player_SetVolume( vol )

		elif id == Action.ACTION_VOLUME_DOWN:
		
			vol = int ( self.mCommander.player_GetVolume( )[0] )
			vol = vol - pvr.gui.GuiConfig.VOLUME_STEP
			
			if vol < 0 :
				vol = 0
				
			self.mCommander.player_SetVolume( vol )
		"""




	def onClick(self, aControlId):
		print "onclick(): control %d" % aControlId
		if aControlId == self.mCtrlBtnMute.getId():
			self.UpdateVolume( Action.ACTION_MUTE )

		elif aControlId == self.mCtrlBtnMuteToggled.getId():
			self.UpdateVolume( Action.ACTION_MUTE )

		elif aControlId == self.mCtrlBtnExInfo.getId() :
			print 'click expantion info'
			self.ShowEPGDescription(aControlId, self.mEventCopy)

		elif aControlId == self.mCtrlBtnTeletext.getId() :
			print 'click teletext'
			self.ShowDialog( aControlId )

		elif aControlId == self.mCtrlBtnSubtitle.getId() :
			print 'click subtitle'
			self.ShowDialog( aControlId )

		elif aControlId == self.mCtrlBtnStartRec.getId() :
			print 'click start recording'
			self.ShowDialog( aControlId )

		elif aControlId == self.mCtrlBtnStopRec.getId() :
			print 'click stop recording'
			self.ShowDialog( aControlId )

		elif aControlId == self.mCtrlBtnTSbanner.getId() :
			print 'click Time Shift banner'
			self.mUntilThread = False
			self.CurrentTimeThread().join()

			winmgr.GetInstance().ShowWindow( winmgr.WIN_ID_TIMESHIFT_BANNER )


		elif aControlId == self.mCtrlBtnPrevEpg.getId() :
			self.ChannelTune(Action.ACTION_MOVE_LEFT)

		elif aControlId == self.mCtrlBtnNextEpg.getId() :
			self.ChannelTune(Action.ACTION_MOVE_RIGHT)



	def onFocus(self, aControlId):
		#print "onFocus(): control %d" % controlId
		pass


	def onEvent(self, aEvent):
		print '[%s]%s():%s'% (os.path.basename(currentframe().f_code.co_filename), currentframe().f_code.co_name, currentframe().f_lineno)
		#print 'aEvent len[%s]'% len(aEvent)
		#ClassToList( 'print', aEvent )

		if self.mWinId == xbmcgui.getCurrentWindowId():
			if aEvent.getName() == ElisEventCurrentEITReceived.getName() :			
				if aEvent.mEventId != self.mEventID :
					ret = None
					ret = self.mCommander.Epgevent_GetPresent()
					if ret :
						self.mEventCopy = ret
						self.mEventID = aEvent.mEventId
						self.UpdateONEvent( ret )

					#ret = self.mCommander.Epgevent_Get(self.mEventID, aEvent.mSid, aEvent.mTsid, aEvent.mOnid, self.mLocalTime )
			else :
				print 'event unknown[%s]'% aEvent.getName()
		else:
			print 'channelbanner winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId())



	def ChannelTune(self, aActionID):
		print '[%s:%s]'% (self.__file__, currentframe().f_lineno)
		print 'tuneActionID[%s]'% aActionID

		if aActionID == Action.ACTION_PAGE_UP:
			print 'onAction():ACTION_PREVIOUS_ITEM control %d' % aActionID
			priv_ch = None
			priv_ch = self.mCommander.Channel_GetPrev()
			print 'priv_ch[%s]' % ClassToList( 'convert', priv_ch )

			if priv_ch :
				try:
					self.mLastChannel = self.mCurrentChannel
					ret = self.mCommander.Channel_SetCurrent( priv_ch.mNumber , priv_ch.mServiceType )

					if ret[0].upper() == 'TRUE' :
						self.mCurrentChannel = self.mCommander.Channel_GetCurrent()
						self.InitLabelInfo()
						self.UpdateServiceType( priv_ch.mServiceType )

				except Exception, e :
					print '[%s:%s] Error exception[%s]'% (	\
						self.__file__,						\
						currentframe().f_lineno,			\
						e )

		elif aActionID == Action.ACTION_PAGE_DOWN:
			print 'onAction():ACTION_NEXT_ITEM control %d' % aActionID
			next_ch = None
			next_ch = self.mCommander.Channel_GetNext()
			print 'next_ch[%s]' % ClassToList( 'convert', next_ch )

			try:
				self.mLastChannel = self.mCurrentChannel
				ret = self.mCommander.channel_SetCurrent( next_ch.mNumber, next_ch.mServiceType )

				if ret[0].upper() == 'TRUE' :
					self.mCurrentChannel = self.mCommander.Channel_GetCurrent()
					self.InitLabelInfo()
					self.UpdateServiceType( next_ch.mServiceType )

			except Exception, e :
				print '[%s:%s] Error exception[%s]'% (	\
					self.__file__,						\
					currentframe().f_lineno,			\
					e )

		elif aActionID == Action.ACTION_MOVE_LEFT:
			#epg priv
			ret = None
			ret = self.mCommander.Epgevent_GetPresent()
			print 'epgevent_GetPresent() ret[%s]'% ClassToList( 'convert', ret )
			if ret :
				self.mEventCopy = ret
				self.UpdateONEvent( ret )

		elif aActionID == Action.ACTION_MOVE_RIGHT:
			#epg next
			ret = None
			ret = self.mCommander.Epgevent_GetFollowing()
			print 'epgevent_GetFollowing() ret[%s]'% ClassToList( 'convert', ret )
			if ret :
				self.mEventCopy = ret
				self.UpdateONEvent( ret )

		else:
			pass

	def UpdateONEvent(self, aEvent):
		print '[%s:%s]'% (self.__file__, currentframe().f_lineno)
		#print 'component [%s]'% EpgInfoComponentImage ( aEvent )

		if aEvent :
			try :
				#epg name
				self.mCtrlEventName.setLabel(aEvent.mEventName)

				#epg time
				self.mProgress_max = int(aEvent[6])

				ret = None
				ret = EpgInfoTime( self.mLocalOffset, aEvent.mStartTime, aEvent.mDuration)
				if ret :
					self.mCtrlEventStartTime.setLabel( ret[0] )
					self.mCtrlEventEndTime.setLabel( ret[1] )

				print 'aEvent6[%s] aEvent7[%s]'% (aEvent.mStartTime, aEvent.mDuration)


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
					print 'AgeLimit[%s]'% isLimit

			except Exception, e:
				print '[%s:%s] Error exception[%s]'% (	\
					self.__file__,						\
					currentframe().f_lineno,			\
					e )


		else:
			print 'aEvent null'


	@RunThread
	def CurrentTimeThread(self):
		print '[%s():%s]begin_start thread'% (self.__file__, currentframe().f_lineno)

		loop = 0
		#rLock = threading.RLock()
		while self.mEnableThread:
			#print '[%s:%s]repeat <<<<'% (self.__file__, currentframe().f_lineno)

			#progress

			if  ( loop % 10 ) == 0 :
				print 'loop=%d' %loop
				self.UpdateLocalTime( )


			#local clock
			ret = EpgInfoClock(1, self.mLocalTime, loop)
			self.mCtrlHeader3.setLabel(ret[0])
			self.mCtrlHeader4.setLabel(ret[1])

			time.sleep(1)
			loop += 1

		print '[%s:%s]leave_end thread'% (self.__file__, currentframe().f_lineno)


	@GuiLock
	def UpdateLocalTime( self ) :
		
		try:
			self.mLocalTime = self.mCommander.Datetime_GetLocalTime( )

		except Exception, e :
			print '[%s:%s] Error exception[%s]'% (	\
				self.__file__,						\
				currentframe().f_lineno,			\
				e )

			self.mLocalTime = 0


		endTime = self.mEpgStartTime + self.mEpgDuration
		pastDuration = endTime - self.mLocalTime
		if pastDuration < 0 :
			pastDuration = 0

		if self.mEpgDuration > 0 :
			percent = pastDuration * 100/self.mEpgDuration
		else :
			percent = 0

		#print 'percent=%d' %percent
		self.mCtrlProgress.setPercent( percent )


	def InitLabelInfo(self):
		print '[%s:%s]'% (self.__file__, currentframe().f_lineno)
		
		if self.mCurrentChannel :

			self.mCtrlProgress.setPercent(0)
			self.mProgress_idx = 0.0
			self.mProgress_max = 0.0
			self.mEventCopy = []

			self.mCtrlChannelNumber.setLabel( str(self.mCurrentChannel.mNumber) )
			self.mCtrlChannelName.setLabel( self.mCurrentChannel.mName )
			self.mCtrlLongitudeInfo.setLabel('')
			self.mCtrlEventName.setLabel('')
			self.mCtrlEventStartTime.setLabel('')
			self.mCtrlEventEndTime.setLabel('')

			self.mCtrlImgServiceType.setImage('')
			self.mCtrlImgServiceTypeImg1.setImage('')
			self.mCtrlImgServiceTypeImg2.setImage('')
			self.mCtrlImgServiceTypeImg3.setImage('')
			self.mCtrlEventDescGroup.setVisible( False )
			self.mCtrlEventDescText1.reset()
			self.mCtrlEventDescText2.reset()


			self.mLocalTime = self.mCommander.Datetime_GetLocalTime()
			longitude = None
			longitude = self.mCommander.Satellite_GetByChannelNumber( self.mCurrentChannel.mNumber, self.mCurrentChannel.mServiceType )
			if longitude :
				ret = GetSelectedLongitudeString( longitude.mLongitude, self.mCurrentChannel.mName )
				self.mCtrlLongitudeInfo.setLabel( ret )
			else:
				self.mCtrlLongitudeInfo.setLabel( '' )

		else:
			print 'has no channel'
		
			# todo 
			# show message box : has no channnel


	def UpdateServiceType(self, aTvType):
		print '[%s:%s]'% (self.__file__, currentframe().f_lineno)
		print 'serviceType[%s]' % aTvType

		if aTvType == ElisEnum.E_TYPE_TV:
			self.mCtrlImgServiceType.setImage(self.mImgTV)
		elif aTvType == ElisEnum.E_TYPE_RADIO:
			pass
		elif aTvType == ElisEnum.E_TYPE_DATA:
			pass
		else:
			self.mCtrlImgServiceType.setImage('')
			print 'unknown ElisEnum tvType[%s]'% aTvType


	def UpdateVolume(self, aCmd):
		print '[%s:%s]'% (self.__file__, currentframe().f_lineno)

		if aCmd == Action.ACTION_MUTE:
			mute = self.mCommander.Player_GetMute()
			print 'mute:current[%s]'% mute
			if mute == False:
				ret = self.mCommander.Player_SetMute( True )
				self.mCtrlBtnMute.setVisible(True)
				self.mCtrlBtnMuteToggled.setVisible( False )

			else:
				ret = self.mCommander.Player_SetMute( False )
				self.mCtrlBtnMute.setVisible(False)
				self.mCtrlBtnMuteToggled.setVisible( True )

		elif aCmd == Action.ACTION_VOLUME_UP:
			pass
		elif aCmd == Action.ACTION_VOLUME_UP:
			pass


	def ShowEPGDescription(self, aFocusid, aEvent):
		print '[%s:%s]'% (self.__file__, currentframe().f_lineno)

		if aFocusid == self.mCtrlBtnExInfo.getId():
			if aEvent :
				print 'epgDescription[%s]' % (aEvent.mEventDescription)
				self.mCtrlEventDescText1.setText( aEvent.mEventName )
				self.mCtrlEventDescText2.setText( aEvent.mEventDescription )

			else:
				print 'event is None'
				self.mCtrlEventDescText1.setText('')
				self.mCtrlEventDescText2.setText('')

		self.DescboxToggle('toggle')

		#self.mCtrlEventDescription.setVisibleCondition('[Control.IsVisible(100)]',True)
		#self.mCtrlEventDescription.setEnabled(True)

	def ShowDialog( self, aFocusid ):
		print '[%s:%s]'% (self.__file__, currentframe().f_lineno)

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
			print 'runningCount=%d' %runningCount

			if  runningCount < 2 :
				dialog = diamgr.GetInstance().GetDialog( diamgr.DIALOG_ID_START_RECORD )
				dialog.doModal( )
			else:
				msg = 'Already %d recording(s) running' %runningCount
				xbmcgui.Dialog().ok('Infomation', msg )

		elif aFocusid == self.mCtrlBtnStopRec.getId() :
			runningCount = self.mCommander.Record_GetRunningRecorderCount()
			print 'runningCount=%d' %runningCount

			if  runningCount > 0 :
				dialog = diamgr.GetInstance().GetDialog( diamgr.DIALOG_ID_STOP_RECORD )
				dialog.doModal( )
			

		#ret = xbmcgui.Dialog().ok(msg1, msg2)
		#print 'dialog ret[%s]' % ret


	def DescboxToggle( self, aCmd ):
		print '[%s:%s]'% (self.__file__, currentframe().f_lineno)

		if aCmd == 'toggle':
			if self.mToggleFlag == True:
				self.mCtrlEventDescText1.reset()
				self.mCtrlEventDescText2.reset()
				self.mCtrlEventDescGroup.setVisible( False )
				self.mToggleFlag = False
			else:
				self.mCtrlEventDescGroup.setVisible( True )
				self.mToggleFlag = True

		elif aCmd == 'close':
			if self.mToggleFlag == True:
				self.mCtrlEventDescText1.reset()
				self.mCtrlEventDescText2.reset()
				self.mCtrlEventDescGroup.setVisible( False )
				self.mToggleFlag = False


	def GetLastChannel( self ):
		return self.mLastChannel
		
	def SetLastChannel( self, lastChannel ):
		self.mLastChannel = lastChannel

