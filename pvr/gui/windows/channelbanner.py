import xbmc
import xbmcgui
import sys
import time

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import BaseWindow
from pvr.gui.basewindow import Action
from pvr.gui.guiconfig import *


import pvr.elismgr
from elisaction import ElisAction
from elisenum import ElisEnum

#from threading import Thread
from pvr.util import run_async, is_digit, Mutex, epgInfoTime, epgInfoClock, epgInfoComponentImage, GetSelectedLongitudeString, enumToString #, synchronized, sync_instance
import thread

#debug log
import logging
from inspect import currentframe

log = logging.getLogger('mythbox.ui')
mlog = logging.getLogger('mythbox.method')


class ChannelBanner(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		print 'f_coname[%s] f_lineno[%d] co_filename[%s]' %(currentframe().f_code.co_name, currentframe().f_lineno, currentframe().f_code.co_filename)    
		print 'args[0]=[%s]' % args[0]
		print 'args[1]=[%s]' % args[1]

		self.commander = pvr.elismgr.getInstance().getCommander()
		self.lastFocusId = None
		self.lastChannel = 	self.commander.channel_GetCurrent()	
		self.currentChannel =  self.lastChannel
		self.eventBus = pvr.elismgr.getInstance().getEventBus()
		#self.eventBus.register( self )


		self.currentChannel=[]
		self.nowTime = 0
		self.eventID = 0

		#push push test test

		#time track
		#from threading import Thread
		#self.timeTrack = threading.Thread(target = self.updateLocalTime)

	def __del__(self):
		print '[%s():%s] destroyed ChannelBanner'% (currentframe().f_code.co_name, currentframe().f_lineno)

		# end thread updateLocalTime()
		self.untilThread = False

	def onInit(self):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		if not self.win:
			self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())

			#get event
			#request = EventRequest(self)
			self.ctrlChannelNumber  = self.getControl( 601 )
			self.ctrlChannelName    = self.getControl( 602 )
			self.ctrlServiceType    = self.getControl( 603 )
			self.ctrlServiceTypeImg1= self.getControl( 604 )
			self.ctrlServiceTypeImg2= self.getControl( 605 )
			self.ctrlServiceTypeImg3= self.getControl( 606 )
			self.ctrlEventClock     = self.getControl( 610 )
			self.ctrlLongitudeInfo  = self.getControl( 701 )
			self.ctrlEventName      = self.getControl( 703 )
			self.ctrlEventStartTime = self.getControl( 704 )
			self.ctrlEventEndTime   = self.getControl( 705 )
			self.ctrlProgress       = self.getControl( 707 )
			self.ctrlEventDescGroup = self.getControl( 800 )
			self.ctrlEventDescText1 = self.getControl( 801 )
			self.ctrlEventDescText2 = self.getControl( 802 )
			#self.ctrlProgress = xbmcgui.ControlProgress(100, 250, 125, 75)
			#self.ctrlProgress(self.Progress)

			#button icon
			self.ctrlBtnExInfo      = self.getControl( 621 )
			self.ctrlBtnTeletext    = self.getControl( 622 )
			self.ctrlBtnSubtitle    = self.getControl( 623 )
			self.ctrlBtnStartRec    = self.getControl( 624 )
			self.ctrlBtnStopRec     = self.getControl( 625 )
			self.ctrlBtnMute        = self.getControl( 626 )
			self.ctrlBtnMuteToggled = self.getControl( 627 )
			self.ctrlBtnTSbanner    = self.getControl( 630 )
			
			self.ctrlBtnPrevEpg     = self.getControl( 702 )
			self.ctrlBtnNextEpg     = self.getControl( 706 )
			

			self.imgTV    = 'confluence/tv.png'
			self.ctrlEventClock.setLabel('')

		self.toggleFlag=False
		self.epgStartTime = 0
		self.epgDuration = 0
		self.localOffset = int( self.commander.datetime_GetLocalOffset()[0] )

		#get channel
		self.currentChannel = self.commander.channel_GetCurrent()

		self.initLabelInfo()
		self.updateVolume(Action.ACTION_MUTE)
	
		if is_digit(self.currentChannel[3]):
			self.updateServiceType(int(self.currentChannel[3]))


		"""
		#get last zapping mode
		ret = []
		ret = self.commander.zappingmode_GetCurrent()
		print 'zappingmode_GetCurrent[%s]'% ret
		try:
			print 'zappingMode[%s] sortMode[%s] serviceType[%s]'% \
				(enumToString('mode', int(ret[0]) ), \
				 enumToString('sort', int(ret[1]) ), \
				 enumToString('type', int(ret[2]) ))

		except Exception, e:
			print 'zappingmode_GetCurrent Error[%s]'% e
		"""

		
		#get epg event right now, as this windows open
		ret = []
		ret=self.commander.epgevent_GetPresent()
		if ret != []:
			self.updateONEvent(self.eventCopy)
		print 'epgevent_GetPresent[%s]'% self.eventCopy


		#run thread
		self.untilThread = True
		self.updateLocalTime()


	def onAction(self, action):
		id = action.getId()
		focusid = self.getFocusId()
		
		if id == Action.ACTION_PREVIOUS_MENU:
			print 'youn check action menu'
			self.descboxToggle('close')
			self.untilThread = False
			self.updateLocalTime().join()
			winmgr.getInstance().showWindow( winmgr.WIN_ID_MAINMENU )

		elif id == Action.ACTION_SELECT_ITEM:
			print '===== test youn: ID[%s]' % id
			log.debug('youn:%s' % id)
	
		elif id == Action.ACTION_PARENT_DIR:
			print 'youn check ation back'

			self.descboxToggle('close')
			self.untilThread = False
			self.updateLocalTime().join()
			self.close( )
			#winmgr.getInstance().showWindow( winmgr.WIN_ID_NULLWINDOW )


			"""
			if focusid >= self.ctrlBtnExInfo.getId() and focusid <= self.ctrlBtnMute.getId():
				self.showEPGDescription(focusid, self.eventCopy)

			else:
				# end thread updateLocalTime()
				self.untilThread = False
				self.updateLocalTime().join()

				self.close( )
#				winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_LIST_WINDOW )
#				winmgr.getInstance().showWindow( winmgr.WIN_ID_NULLWINDOW )
#				winmgr.shutdown()
			"""

		elif id == Action.ACTION_SHOW_INFO	:
			self.showEPGDescription( self.ctrlBtnExInfo.getId(), self.eventCopy)

		elif id == Action.ACTION_MOVE_LEFT:
			if focusid == self.ctrlBtnPrevEpg.getId():			
				self.channelTune(id)

		elif id == Action.ACTION_MOVE_RIGHT:
			if focusid == self.ctrlBtnNextEpg.getId():
				self.channelTune(id)

		elif id == Action.ACTION_PAGE_UP:
			self.channelTune(id)

		elif id == Action.ACTION_PAGE_DOWN:
			self.channelTune(id)

		elif id == Action.ACTION_MUTE:
			self.updateVolume(id)

		elif id == Action.ACTION_PAUSE:
			self.descboxToggle('close')
			self.untilThread = False
			self.updateLocalTime().join()
			winmgr.getInstance().showWindow( winmgr.WIN_ID_TIMESHIFT_BANNER )

		else:
			#print 'youn check action unknown id=%d' % id
			#self.channelTune(id)
			pass


		"""
		elif id == Action.ACTION_VOLUME_UP:
		
			vol = int ( self.commander.player_GetVolume( )[0] )
			vol = vol + pvr.gui.guiconfig.VOLUME_STEP
			
			if vol > pvr.gui.guiconfig.MAX_VOLUME :
				vol = pvr.gui.guiconfig.MAX_VOLUME

			self.commander.player_SetVolume( vol )

		elif id == Action.ACTION_VOLUME_DOWN:
		
			vol = int ( self.commander.player_GetVolume( )[0] )
			vol = vol - pvr.gui.guiconfig.VOLUME_STEP
			
			if vol < 0 :
				vol = 0
				
			self.commander.player_SetVolume( vol )
		"""




	def onClick(self, controlId):
		print "onclick(): control %d" % controlId
		if controlId == self.ctrlBtnMute.getId():
			self.updateVolume( Action.ACTION_MUTE )

		elif controlId == self.ctrlBtnMuteToggled.getId():
			self.updateVolume( Action.ACTION_MUTE )

		elif controlId == self.ctrlBtnExInfo.getId() :
			print 'click expantion info'
			self.showEPGDescription(controlId, self.eventCopy)

		elif controlId == self.ctrlBtnTeletext.getId() :
			print 'click teletext'
			self.showDialog( controlId )

		elif controlId == self.ctrlBtnSubtitle.getId() :
			print 'click subtitle'
			self.showDialog( controlId )

		elif controlId == self.ctrlBtnStartRec.getId() :
			print 'click start recording'
			self.showDialog( controlId )

		elif controlId == self.ctrlBtnStopRec.getId() :
			print 'click stop recording'
			self.showDialog( controlId )

		elif controlId == self.ctrlBtnTSbanner.getId() :
			print 'click Time Shift banner'
			self.untilThread = False
			self.updateLocalTime().join()

			winmgr.getInstance().showWindow( winmgr.WIN_ID_TIMESHIFT_BANNER )


		elif controlId == self.ctrlBtnPrevEpg.getId() :
			self.channelTune(Action.ACTION_MOVE_LEFT)

		elif controlId == self.ctrlBtnNextEpg.getId() :
			self.channelTune(Action.ACTION_MOVE_RIGHT)



	def onFocus(self, controlId):
		#print "onFocus(): control %d" % controlId
		pass


	def onEvent(self, event):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'event[%s]'% event

		if self.win :
			msg = event[0]
			
			if msg == 'Elis-CurrentEITReceived' :

				if int(event[4]) != self.eventID :			
					ret = self.commander.epgevent_GetPresent( )
					if len( ret ) > 0 :
						self.eventCopy = event
						self.eventID = int( event[4] )
						self.updateONEvent( ret )

					#ret = self.commander.epgevent_Get(self.eventID, int(event[1]), int(event[2]), int(event[3]), int(self.epgClock[0]) )
			else :
				print 'event unknown[%s]'% event
		else:
			print 'show screen is another windows page[%s]'% xbmcgui.getCurrentWindowId()



	def channelTune(self, actionID):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)		
		print 'tuneActionID[%s]'% actionID

		if actionID == Action.ACTION_PAGE_UP:
			print 'onAction():ACTION_PREVIOUS_ITEM control %d' % actionID
			priv_ch = self.commander.channel_GetPrev()
			print 'priv_ch[%s]' % priv_ch

			try:
				channelNumber = priv_ch[0]
				channelType = priv_ch[3]
				if is_digit(channelNumber):
					ret = self.commander.channel_SetCurrent( int(channelNumber) , int(channelType))
					self.lastChannel = self.currentChannel

					if ret[0].upper() == 'TRUE' :
						self.currentChannel = self.commander.channel_GetCurrent()
						self.initLabelInfo()

				else:
					print 'No Channel priv_ch[%s]'% priv_ch

				if is_digit(priv_ch[3]):
					self.updateServiceType(int(priv_ch[3]))

			except Exception, e:
				print 'channel_GetPrev Error[%s]'% e

		elif actionID == Action.ACTION_PAGE_DOWN:
			print 'onAction():ACTION_NEXT_ITEM control %d' % actionID
			next_ch = self.commander.channel_GetNext()
			print 'next_ch[%s]' % next_ch

			try:
				channelNumber = next_ch[0]
				channelType = next_ch[3]
				if is_digit(channelNumber):
					ret = self.commander.channel_SetCurrent( int(channelNumber), int(channelType) )
					self.lastChannel = self.currentChannel

					if ret[0].upper() == 'TRUE' :
						self.currentChannel = self.commander.channel_GetCurrent()
						self.initLabelInfo()

				else:
					print 'No Channel next_ch[%s]'% next_ch

				if is_digit(next_ch[3]):
					self.updateServiceType(int(next_ch[3]))

			except Exception, e:
				print 'channel_GetNext Error[%s]'% e

		elif actionID == Action.ACTION_MOVE_LEFT:
			#epg priv
			ret = []
			ret = self.commander.epgevent_GetPresent()
			print 'epgevent_GetPresent() ret[%s]'% ret
			if ret != []:
				self.eventCopy = ret
				self.updateONEvent(self.eventCopy)

		elif actionID == Action.ACTION_MOVE_RIGHT:
			#epg next
			ret = []
			ret = self.commander.epgevent_GetFollowing()
			print 'epgevent_GetFollowing() ret[%s]'% ret
			if ret != []:
				self.eventCopy = ret
				self.updateONEvent(self.eventCopy)

		else:
			pass

	def updateONEvent(self, event):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'event[%s]'% event
		print 'component [%s]'% event[8:17]

		if len(event) == 21:
			#epg name
			if event[1] != '':
				print '[%s():%s]%s'% (currentframe().f_code.co_name, currentframe().f_lineno,event[2])
				try:
					self.ctrlEventName.setLabel(event[1])
				except Exception, ex:
					print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
					print 'CATCHALL_UI: Caught  exception %s' % str(ex)
			else:
				self.ctrlEventName.setLabel('')

			#epg time
			if is_digit(event[6]):
				self.progress_max = int(event[6])

				if is_digit(event[5]):
					self.epgStartTime = int( event[5] )
					self.epgDuration = int( event[6] )
					ret = epgInfoTime( self.localOffset, int(event[5]), int(event[6]))
					if ret != []:
						print 'ret[%s]'% ret
						self.ctrlEventStartTime.setLabel(ret[0])
						self.ctrlEventEndTime.setLabel(ret[1])
				
					print 'event6[%s] event7[%s]'% (event[5], event[6])
				else:
					print 'value error EPGTime start[%s]' % event[5]
			else:
				print 'value error EPGTime duration[%s]' % event[6]

			#component
			component = []
			component = event[8:17]	#component ~ isSeries
#			ret = epgInfoComponentImage(int(event[9]))
			ret = epgInfoComponentImage(component)			
			if len(ret) == 1:
				self.ctrlServiceTypeImg1.setImage(ret[0])
			elif len(ret) == 2:
				self.ctrlServiceTypeImg1.setImage(ret[0])
				self.ctrlServiceTypeImg2.setImage(ret[1])
			elif len(ret) == 3:
				self.ctrlServiceTypeImg1.setImage(ret[0])
				self.ctrlServiceTypeImg2.setImage(ret[1])
				self.ctrlServiceTypeImg3.setImage(ret[2])
			else:
				self.ctrlServiceTypeImg1.setImage('')
				self.ctrlServiceTypeImg2.setImage('')
				self.ctrlServiceTypeImg3.setImage('')

		else:
			print 'event null'

	@run_async
	def updateLocalTime(self):
		print '[%s():%s]begin_start thread'% (currentframe().f_code.co_name, currentframe().f_lineno)
		#print 'untilThread[%s] self.progress_max[%s]' % (self.untilThread, self.progress_max)

		loop = 0
		rLock.acquire()
		while self.untilThread:
			#print '[%s():%s]repeat <<<<'% (currentframe().f_code.co_name, currentframe().f_lineno)

			#progress
			rLock.acquire()
			if  ( loop % 10 ) == 0 :
				try:
					ret = self.commander.datetime_GetLocalTime( )
					localTime = int( ret[0] )

				except Exception, e:
					print 'Error e[%s] datetime_GetLocalTime()'% e
					rLock.release()
					continue

					endTime = self.epgStartTime + self.epgDuration
					#print 'localoffset=%d localToime=%d epgStartTime=%d duration=%d' %(self.localOffset, localTime, self.epgStartTime, self.epgDuration )
					#print 'endtime=%d' %endTime

					pastDuration = endTime - localTime
					if pastDuration < 0 :
						pastDuration = 0

					if self.epgDuration > 0 :
						percent = pastDuration * 100/self.epgDuration
					else :
						percent = 0

					#print 'percent=%d' %percent
					self.ctrlProgress.setPercent( percent )


			#local clock
			ret = epgInfoClock(2, localTime, loop)
			self.ctrlEventClock.setLabel(ret[0])
			rLock.release()

			#self.nowTime += 1
			time.sleep(1)
			loop += 1

		print '[%s():%s]leave_end thread'% (currentframe().f_code.co_name, currentframe().f_lineno)

	def initLabelInfo(self):
		print '[%s():%s]Initialize Label'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'currentChannel[%s]' % self.currentChannel
		
		if( self.currentChannel != [] ) :

			self.ctrlProgress.setPercent(0)
			self.progress_idx = 0.0
			self.progress_max = 0.0
			self.eventCopy = []

			self.ctrlChannelNumber.setLabel( self.currentChannel[1] )
			self.ctrlChannelName.setLabel( self.currentChannel[2] )
			self.ctrlLongitudeInfo.setLabel('')
			self.ctrlEventName.setLabel('')
			self.ctrlEventStartTime.setLabel('')
			self.ctrlEventEndTime.setLabel('')

			self.ctrlServiceType.setImage('')
			self.ctrlServiceTypeImg1.setImage('')
			self.ctrlServiceTypeImg2.setImage('')
			self.ctrlServiceTypeImg3.setImage('')
			self.ctrlEventDescGroup.setVisible(False)
			self.ctrlEventDescText1.reset()
			self.ctrlEventDescText2.reset()


			self.epgClock = self.commander.datetime_GetLocalTime()
			
			longitude = self.commander.satellite_GetByChannelNumber(int(self.currentChannel[0]), int(self.currentChannel[3]))
			ret = GetSelectedLongitudeString(longitude)
			self.ctrlLongitudeInfo.setLabel(ret)


		else:
			print 'has no channel'
		
			# todo 
			# show message box : has no channnel


	def updateServiceType(self, tvType):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'serviceType[%s]' % tvType


		if tvType == ElisEnum.E_TYPE_TV:
			self.ctrlServiceType.setImage(self.imgTV)
		elif tvType == ElisEnum.E_TYPE_RADIO:pass
		elif tvType == ElisEnum.E_TYPE_DATA:pass
		else:
			self.ctrlServiceType.setImage('')
			print 'unknown ElisEnum tvType[%s]'% tvType


	def updateVolume(self, cmd):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		if cmd == Action.ACTION_MUTE:
			mute = int(self.commander.player_GetMute()[0])
			print 'mute:current[%s]'% mute
			if mute == False:
				ret = self.commander.player_SetMute(True)
				self.ctrlBtnMute.setVisible(True)
				self.ctrlBtnMuteToggled.setVisible(False)

			else:
				ret = self.commander.player_SetMute(False)
				self.ctrlBtnMute.setVisible(False)
				self.ctrlBtnMuteToggled.setVisible(True)

		elif cmd == Action.ACTION_VOLUME_UP:
			pass
		elif cmd == Action.ACTION_VOLUME_UP:
			pass


	def showEPGDescription(self, focusid, event):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		if focusid == self.ctrlBtnExInfo.getId():
			if event != [] and event[1] != 'NULL' and len(event) > 2:
				print '[%s][%s][%s][%s][%s]' % (event[1], event[3], event[4], event[5], event[6])
				msgDescription = self.commander.epgevent_GetDescription(
								int(event[1]), #eventId
								int(event[3]), #sid
								int(event[4]), #tsid
								int(event[5]), #onid
								int(event[6])) #startTime

				print 'msgDescription[%s]' % msgDescription

				if msgDescription[0] != 'NULL':
					msg = msgDescription[1]
				else:
					print 'No value Description  \'NULL\''
					msg = ''

				self.ctrlEventDescText1.setText(event[2])
				self.ctrlEventDescText2.setText(msg)

			else:
				print 'event is None'
				self.ctrlEventDescText1.setText('')
				self.ctrlEventDescText2.setText('')

		self.descboxToggle('toggle')

		#self.ctrlEventDescription.setVisibleCondition('[Control.IsVisible(100)]',True)
		#self.ctrlEventDescription.setEnabled(True)

	def showDialog( self, focusid ):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		msg1 = ''
		msg2 = ''

		if focusid == self.ctrlBtnMute.getId():
			msg1 = 'Mute'
			msg2 = 'test'

		elif focusid == self.ctrlBtnTeletext.getId() :
			msg1 = 'Teletext'
			msg2 = 'test'


		elif focusid == self.ctrlBtnSubtitle.getId() :
			msg1 = 'Subtitle'
			msg2 = 'test'

		elif focusid == self.ctrlBtnStartRec.getId() :
			msg1 = 'Start Recording'
			msg2 = 'test'

		elif focusid == self.ctrlBtnStopRec.getId() :
			msg1 = 'Stop Recording'
			msg2 = 'test'

		ret = xbmcgui.Dialog().ok(msg1, msg2)
		print 'dialog ret[%s]' % ret


	def descboxToggle( self, cmd ):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		if cmd == 'toggle':
			if self.toggleFlag == True:
				self.ctrlEventDescText1.reset()
				self.ctrlEventDescText2.reset()
				self.ctrlEventDescGroup.setVisible(False)
				self.toggleFlag = False
			else:
				self.ctrlEventDescGroup.setVisible(True)
				self.toggleFlag = True

		elif cmd == 'close':
			if self.toggleFlag == True:
				self.ctrlEventDescText1.reset()
				self.ctrlEventDescText2.reset()
				self.ctrlEventDescGroup.setVisible(False)
				self.toggleFlag = False
			

	def getLastChannel( self ):
		return self.lastChannel
		
	def setLastChannel( self, lastChannel ):
		self.lastChannel = lastChannel

