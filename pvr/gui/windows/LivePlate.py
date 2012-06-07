from pvr.gui.WindowImport import *

FLAG_MASK_ADD  = 0x01
FLAG_MASK_NONE = 0x00
FLAG_CLOCKMODE_ADMYHM  = 1
FLAG_CLOCKMODE_AHM     = 2
FLAG_CLOCKMODE_HMS     = 3
FLAG_CLOCKMODE_HHMM    = 4
FLAG_CLOCKMODE_INTTIME = 5

FLAG_ZAPPING_LOAD   = 0
FLAG_ZAPPING_CHANGE = 1

E_TAG_COLOR_WHITE = '[COLOR white]'
E_TAG_COLOR_GREY  = '[COLOR grey]'
E_TAG_COLOR_GREY3 = '[COLOR grey3]'
E_TAG_COLOR_END   = '[/COLOR]'

NEXT_EPG		= 0
PREV_EPG 		= 1

NEXT_CHANNEL	= 0
PREV_CHANNEL	= 1
CURR_CHANNEL	= 2

CONTEXT_ACTION_VIDEO_SETTING = 1 
CONTEXT_ACTION_AUDIO_SETTING = 2

class LivePlate( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )

		self.mGMTTime = 0
		self.mEventID = 0
		self.mPincodeEnter = FLAG_MASK_NONE
		self.mCurrentChannel = None
		self.mLastChannel = None
		self.mFakeChannel = None
		self.mZappingMode = None
		self.mFlag_OnEvent = True
		self.mPropertyAge = 0
		self.mPropertyPincode = -1
		self.mCertification = False

		self.mAutomaticHideTimer = None	
		self.mAsyncEPGTimer = None
		self.mAsyncTuneTimer = None	
		self.mAutomaticHide = False


	"""
	def __del__(self):
		LOG_TRACE( 'destroyed LivePlate' )

		# end thread CurrentTimeThread()
		self.mEnableThread = False

	def onInit ( self ) :
		currentStack = inspect.stack()
		print '+++++getrecursionlimit[%s] currentStack[%s]'% (sys.getrecursionlimit(), len(currentStack))
		print '+++++currentStackInfo[%s]'% (currentStack) 
	

	def onAction(self, aAction):
		id = aAction.getId()
		
		if id == Action.ACTION_PREVIOUS_MENU or id == Action.ACTION_PARENT_DIR:
			#WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
			#WinMgr.GetInstance().CloseWindow( WinMgr.WIN_ID_LIVE_PLATE )
			#self.close()

			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )


		elif id == Action.REMOTE_0 : 
			xbmc.executebuiltin('XBMC.ReloadSkin()')

		elif id == 104 : #scroll up
			xbmc.executebuiltin('XBMC.ReloadSkin()')

	def onFocus(self, aControlId):
		pass

	def SetAutomaticHide( self, aHide=True ) :
		self.mAutomaticHide = aHide

	def GetAutomaticHide( self ) :
		return self.mAutomaticHide
	"""

	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		LOG_TRACE( 'winID[%d]'% self.mWinId)

		self.mCtrlLblChannelNumber     = self.getControl( 601 )
		self.mCtrlLblChannelName       = self.getControl( 602 )
		self.mCtrlImgServiceTypeTV     = self.getControl( 603 )
		self.mCtrlImgServiceTypeRadio  = self.getControl( 604 )

		self.mCtrlGroupComponentData   = self.getControl( 605 )
		self.mCtrlGroupComponentDolby  = self.getControl( 606 )
		self.mCtrlGroupComponentHD     = self.getControl( 607 )
		self.mCtrlLblEventClock        = self.getControl( 610 )
		self.mCtrlLblLongitudeInfo     = self.getControl( 701 )
		self.mCtrlLblEventName         = self.getControl( 703 )
		self.mCtrlLblEventStartTime    = self.getControl( 704 )
		self.mCtrlLblEventEndTime      = self.getControl( 705 )
		self.mCtrlProgress             = self.getControl( 707 )
		#self.mCtrlProgress = xbmcgui.ControlProgress(100, 250, 125, 75)
		#self.mCtrlProgress(self.Progress)

		#button icon
		self.mCtrlImgRec1              = self.getControl(  10 )
		self.mCtrlLblRec1              = self.getControl(  11 )
		self.mCtrlImgRec2              = self.getControl(  15 )
		self.mCtrlLblRec2              = self.getControl(  16 )
		self.mCtrlBtnExInfo            = self.getControl( 621 )
		self.mCtrlBtnTeletext          = self.getControl( 622 )
		self.mCtrlBtnSubtitle          = self.getControl( 623 )
		self.mCtrlBtnStartRec          = self.getControl( 624 )
		self.mCtrlBtnStopRec           = self.getControl( 625 )
		self.mCtrlBtnMute              = self.getControl( 626 )
		self.mCtrlBtnSettingFormat     = self.getControl( 627 )
		self.mCtrlImgLocked            = self.getControl( 651 )
		self.mCtrlImgICas              = self.getControl( 652 )
		#self.mCtrlBtnTSbanner          = self.getControl( 630 )

		self.mCtrlBtnPrevEpg           = self.getControl( 702 )
		self.mCtrlBtnNextEpg           = self.getControl( 706 )

		self.mFlag_OnEvent = True
		self.mFlag_ChannelChanged = True
		self.mCurrentEvent = None
		self.mEPGList = None
		self.mEPGListIdx = 0
		self.mJumpNumber = 0
		self.mZappingMode = None

		self.mAsyncEPGTimer = None
		self.mAsyncTuneTimer = None
		self.mAutomaticHideTimer = None

		self.UpdateLabelGUI( self.mCtrlLblEventClock.getId(), '' )

		self.mPropertyAge = ElisPropertyEnum( 'Age Limit', self.mCommander ).GetProp( )
		self.mPropertyPincode = ElisPropertyInt( 'PinCode', self.mCommander ).GetProp( )
		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )

		self.mZappingMode = self.mDataCache.Zappingmode_GetCurrent( )
		if not self.mZappingMode :
			self.mZappingMode = ElisIZappingMode( )

		self.ShowRecording( )

		#get channel
		self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
		self.mFakeChannel =	self.mCurrentChannel
		self.mLastChannel =	self.mCurrentChannel

		self.InitLabelInfo()
		self.GetEPGList()

		try :
			iEPG = None
			iEPG = self.mDataCache.Epgevent_GetPresent()
			if iEPG and iEPG.mEventName != 'No Name':
				self.mCurrentEvent = iEPG
				self.UpdateONEvent( iEPG )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		#if not self.mCertification :
		if self.mCurrentChannel.mLocked :
			WinMgr.GetInstance().GetWindow( WinMgr.WIN_ID_NULLWINDOW ).PincodeDialogLimit( self.mDataCache.mPropertyPincode )

		"""
		else :
			if self.mZappingMode.mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
				self.mDataCache.Player_AVBlank( False, False )
				LOG_TRACE('------------- type[%s] avBlank False'% self.mZappingMode.mServiceType)
			else :
				self.mDataCache.Player_AVBlank( True, False )
				LOG_TRACE('------------- type[%s] avBlank True'% self.mZappingMode.mServiceType)
		"""

		#get epg event right now, as this windows open
		self.mEventBus.Register( self )

		#run thread
		self.mEnableThread = True
		self.CurrentTimeThread()

		if self.mAutomaticHide == True :
			self.StartAutomaticHide()


	def onAction( self, aAction ) :
		id = aAction.getId( )
		self.GlobalAction( id )
		if id >= Action.REMOTE_0 and id <= Action.REMOTE_9 :
			self.KeySearch( id-Action.REMOTE_0 )

		elif id >= Action.ACTION_JUMP_SMS2 and id <= Action.ACTION_JUMP_SMS9 :
			rKey = id - (Action.ACTION_JUMP_SMS2 - 2)
			self.KeySearch( rKey )

		elif id == Action.ACTION_PREVIOUS_MENU or id == Action.ACTION_PARENT_DIR:
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )

			self.Close()
			status = self.mDataCache.Player_GetStatus()
			if status.mMode == ElisEnum.E_MODE_TIMESHIFT :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE, WinMgr.WIN_ID_NULLWINDOW )
			else :
				WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_NULLWINDOW, WinMgr.WIN_ID_ROOTWINDOW )


		elif id == Action.ACTION_SELECT_ITEM:
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )

	
		elif id == Action.ACTION_CONTEXT_MENU :
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
			self.onClick( self.mCtrlBtnExInfo.getId() )


		elif id == Action.ACTION_MOVE_LEFT:
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
		
			self.GetFocusId()
			if self.mFocusId == self.mCtrlBtnPrevEpg.getId( ) :			
				self.EPGNavigation( PREV_EPG )

		elif id == Action.ACTION_MOVE_RIGHT :
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
		
			self.GetFocusId()
			if self.mFocusId == self.mCtrlBtnNextEpg.getId():
				self.EPGNavigation( NEXT_EPG )

		elif id == Action.ACTION_PAGE_UP:
			if self.mDataCache.mStatusIsArchive :
				#LOG_TRACE('Archive playing now')
				return -1

			self.ChannelTune( NEXT_CHANNEL )

		elif id == Action.ACTION_PAGE_DOWN :
			if self.mDataCache.mStatusIsArchive :
				#LOG_TRACE('Archive playing now')
				return -1

			self.ChannelTune( PREV_CHANNEL )

		elif id == Action.ACTION_PAUSE:
			winmgr.GetInstance().ShowWindow( winmgr.WIN_ID_TIMESHIFT_PLATE )

		elif id == Action.ACTION_STOP :
			status = None
			status = self.mDataCache.Player_GetStatus()
			if status.mMode :
				ret = self.mDataCache.Player_Stop()
			else :
				self.ShowDialog( self.mCtrlBtnStopRec.getId() )

		#test
		elif id == 13: #'x'
			LOG_TRACE( 'cwd[%s]'% xbmc.getLanguage() )


	def onClick(self, aControlId):
		if aControlId == self.mCtrlBtnMute.getId():
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
		
			self.GlobalAction( Action.ACTION_MUTE  )

		elif aControlId == self.mCtrlBtnExInfo.getId() :
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
			self.ShowDialog( aControlId )

		elif aControlId == self.mCtrlBtnTeletext.getId() :
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
			self.ShowDialog( aControlId )

		elif aControlId == self.mCtrlBtnSubtitle.getId() :
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
			self.ShowDialog( aControlId )

		elif aControlId == self.mCtrlBtnStartRec.getId() :
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
			self.ShowDialog( aControlId )

		elif aControlId == self.mCtrlBtnStopRec.getId() :
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
			self.ShowDialog( aControlId )

		elif aControlId == self.mCtrlBtnSettingFormat.getId() :
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
			self.ShowDialog( aControlId )

		elif aControlId == self.mCtrlBtnPrevEpg.getId() :
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
			self.EPGNavigation( PREV_EPG )

		elif aControlId == self.mCtrlBtnNextEpg.getId() :
			self.StopAutomaticHide()
			self.SetAutomaticHide( False )
			self.EPGNavigation( NEXT_EPG )



	def onFocus(self, aControlId):
		#LOG_TRACE( 'control %d' % controlId )
		pass


	@GuiLock
	def onEvent(self, aEvent):
		if self.mWinId == xbmcgui.getCurrentWindowId():
			ch = self.mCurrentChannel
			if aEvent.getName() == ElisEventCurrentEITReceived.getName() :

				if ch == None :
					#LOG_TRACE('ignore event, currentChannel None, [%s]'% ch)
					return -1
				
				if ch.mSid != aEvent.mSid or ch.mTsid != aEvent.mTsid or ch.mOnid != aEvent.mOnid :
					#LOG_TRACE('ignore event, same event')
					return -1

				if ch.mNumber != self.mFakeChannel.mNumber :
					#LOG_TRACE('ignore event, Channel: current[%s] fake[%s]'% (ch.mNumber, self.mFakeChannel.mNumber) )
					return -1

				if self.mFlag_OnEvent != True :
					#LOG_TRACE('ignore event, mFlag_OnEvent[%s]'% self.mFlag_OnEvent)
					return -1

				#LOG_TRACE( 'eventid:new[%d] old[%d]' %(aEvent.mEventId, self.mEventID ) )

				if aEvent.mEventId != self.mEventID :
					iEPG = None
					iEPG = self.mDataCache.Epgevent_GetCurrent( ch.mSid, ch.mTsid, ch.mOnid )
					if iEPG and iEPG.mEventName != 'No Name':
						if not self.mCurrentEvent or \
						iEPG.mEventId != self.mCurrentEvent.mEventId or \
						iEPG.mSid != self.mCurrentEvent.mSid or \
						iEPG.mTsid != self.mCurrentEvent.mTsid or \
						iEPG.mOnid != self.mCurrentEvent.mOnid :
							#LOG_TRACE('epg DIFFER, id[%s]'% iEPG.mEventId)
							self.mEventID = aEvent.mEventId
							self.mCurrentEvent = iEPG
							#update label
							self.UpdateONEvent( iEPG )

							#check : new event?
							if self.mEPGList :
								#1. aready exist? search in EPGList
								idx = 0
								self.mEPGListIdx = -1
								for item in self.mEPGList :
									#LOG_TRACE('idx[%s] item[%s]'% (idx, item) )
									if item and \
									 	item.mEventId == self.mCurrentEvent.mEventId and \
										item.mSid == self.mCurrentEvent.mSid and \
										item.mTsid == self.mCurrentEvent.mTsid and \
										item.mOnid == self.mCurrentEvent.mOnid :

										self.mEPGListIdx = idx
										#LOG_TRACE('Received ONEvent : EPGList idx moved(current idx)')

										#iEPGList=[]
										#iEPGList.append(item)
										#LOG_TRACE('1.Aready Exist: NOW EPG idx[%s] [%s]'% (idx, ClassToList('convert', iEPGList)) )
										break

									idx += 1

								#2. new epg, append to EPGList
								if self.mEPGListIdx == -1 :
									#LOG_TRACE('new EPG received, not exist in EPGList')
									oldLen = len(self.mEPGList)
									idx = 0
									for idx in range(len(self.mEPGList)) :
										if self.mCurrentEvent.mStartTime < self.mEPGList[idx].mStartTime :
											break

									self.mEPGListIdx = idx
									self.mEPGList = self.mEPGList[:idx]+[self.mCurrentEvent]+self.mEPGList[idx:]
									#LOG_TRACE('append new idx[%s], epgTotal:oldlen[%s] newlen[%s]'% (idx, oldLen, len(self.mEPGList)) )

			elif aEvent.getName() == ElisEventRecordingStarted.getName() or \
				 aEvent.getName() == ElisEventRecordingStopped.getName() :
				time.sleep(1.5)
				self.ShowRecording()
				self.mDataCache.mCacheReload = True

			elif aEvent.getName() == ElisEventChannelChangeResult.getName() :
				pass
				#ToDO : do not db open in thread
				"""
				isLimit = False
				if self.mCurrentEvent :
					isLimit = AgeLimit( self.mPropertyAge, self.mCurrentEvent.mAgeRating )

				if ch.mLocked or isLimit :
					WinMgr.GetInstance().GetWindow( WinMgr.WIN_ID_NULLWINDOW ).PincodeDialogLimit( self.mDataCache.mPropertyPincode )
				"""

		else:
			LOG_TRACE( 'LivePlate winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId()) )


	def ChannelTune(self, aDir):

		if aDir == PREV_CHANNEL:
		
			prevChannel = self.mDataCache.Channel_GetPrev( self.mFakeChannel )

			if prevChannel == None or prevChannel.mError != 0 :
				return

			self.mFakeChannel = prevChannel
			#self.InitLabelInfo()
			self.UpdateLabelGUI( self.mCtrlLblChannelNumber.getId(), ('%s'% self.mFakeChannel.mNumber) )
			self.UpdateLabelGUI( self.mCtrlLblChannelName.getId(), self.mFakeChannel.mName )
			self.RestartAsyncTune()

		elif aDir == NEXT_CHANNEL:
			nextChannel = self.mDataCache.Channel_GetNext( self.mFakeChannel )

			if nextChannel == None or nextChannel.mError != 0 :
				return

			self.mFakeChannel = nextChannel
			#self.InitLabelInfo()
			self.UpdateLabelGUI( self.mCtrlLblChannelNumber.getId(), ('%s'% self.mFakeChannel.mNumber) )
			self.UpdateLabelGUI( self.mCtrlLblChannelName.getId(), self.mFakeChannel.mName )
			self.RestartAsyncTune()

		elif aDir == CURR_CHANNEL:
			jumpChannel = self.mDataCache.Channel_GetCurr( self.mJumpNumber )

			if jumpChannel == None or jumpChannel.mError != 0 :
				return

			self.mFakeChannel = jumpChannel
			self.InitLabelInfo()
			self.RestartAsyncTune()

		if self.mAutomaticHide == True :
			self.RestartAutomaticHide()


	def EPGListMove( self ) :
		try :
			iEPG = self.mEPGList[self.mEPGListIdx]

			if iEPG :
				self.InitLabelInfo()
				GuiLock2(True)
				self.mCurrentEvent = iEPG
				self.mFlag_OnEvent = False
				GuiLock2(False)

				self.UpdateONEvent( iEPG )

				#retList = []
				#retList.append( iEPG )
				#LOG_TRACE( 'idx[%s] epg[%s]'% (self.mEPGListIdx, ClassToList( 'convert', retList )) )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def EPGNavigation(self, aDir ):
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


	def GetEPGList( self ) :
		#stop onEvent
		self.mFlag_OnEvent = False

		try :
			ch = self.mCurrentChannel

			if self.mCurrentEvent == None :
				if not ch :
					#LOG_TRACE('No Channels')
					return

				iEPG = None
				iEPG = self.mDataCache.Epgevent_GetCurrent( ch.mSid, ch.mTsid, ch.mOnid )
				if iEPG and iEPG.mEventName != 'No Name':
					self.mCurrentEvent = iEPG

				else :
					#receive onEvent
					self.mFlag_OnEvent = True
					return -1

			if ch :
				self.mEPGList = None

				#Live EPG
				#gmtime = self.mDataCache.Datetime_GetGMTTime()
				#gmtFrom  = self.mCurrentEvent.mStartTime
				gmtFrom  = self.mDataCache.Datetime_GetGMTTime()
				gmtUntil = gmtFrom + ( 3600 * 24 * 7 )
				maxCount = 100
				iEPGList = None
				iEPGList = self.mDataCache.Epgevent_GetListByChannel( ch.mSid, ch.mTsid, ch.mOnid, gmtFrom, gmtUntil, maxCount )
				time.sleep(0.05)
				#LOG_TRACE('iEPGList[%s] ch[%d] sid[%d] tid[%d] oid[%d] from[%s] until[%s]'% (iEPGList, ch.mNumber, ch.mSid, ch.mTsid, ch.mOnid, time.asctime(time.localtime(gmtFrom)), time.asctime(time.localtime(gmtUntil))) )
				if iEPGList :
					self.mEPGList = iEPGList
					self.mFlag_ChannelChanged = False

				else :
					#receive onEvent
					self.mFlag_OnEvent = True
					#LOG_TRACE('EPGList is None\nLeave')
					return -1

				idx = 0
				self.mEPGListIdx = -1
				for item in self.mEPGList :
					#LOG_TRACE('idx[%s] item[%s]'% (idx, item) )
					if item and \
					 	item.mEventId == self.mCurrentEvent.mEventId and \
						item.mSid == self.mCurrentEvent.mSid and \
						item.mTsid == self.mCurrentEvent.mTsid and \
						item.mOnid == self.mCurrentEvent.mOnid :

						self.mEPGListIdx = idx

						#retList=[]
						#retList.append(item)
						#LOG_TRACE('SAME NOW EPG idx[%s] [%s]'% (idx, ClassToList('convert', retList)) )

						break

					idx += 1

				#search not current epg
				if self.mEPGListIdx == -1 : 
					self.mEPGListIdx = 0
					#LOG_TRACE('SEARCH NOT CURRENT EPG, idx=0')

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		#receive onEvent
		self.mFlag_OnEvent = True


	def UpdateONEvent(self, aEvent = None):
		ch = self.mCurrentChannel
		if ch :
			try :
				#satellite
				label = ''
				satellite = self.mDataCache.Satellite_GetByChannelNumber( ch.mNumber, -1, True )
				if satellite :
					label = GetSelectedLongitudeString( satellite.mLongitude, satellite.mName )
				self.UpdateLabelGUI( self.mCtrlLblLongitudeInfo.getId(), label )

				#lock,cas
				if ch.mLocked :
					self.UpdateLabelGUI( self.mCtrlImgLocked.getId(), 'True' )
					#if self.mFlag_OnEvent == True :
					#	self.mPincodeEnter |= FLAG_MASK_ADD

				if ch.mIsCA :
					self.UpdateLabelGUI( self.mCtrlImgICas.getId(), 'True' )

				#type
				setPropertyTV    = 'False'
				setPropertyRadio = 'False'
				if ch.mServiceType == ElisEnum.E_SERVICE_TYPE_TV:
					setPropertyTV    = 'True'
					setPropertyRadio = 'False'
				elif ch.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO:
					setPropertyTV    = 'False'
					setPropertyRadio = 'True'
				elif ch.mServiceType == ElisEnum.E_SERVICE_TYPE_DATA:
					pass
				else:
					pass
					#LOG_TRACE( 'unknown ElisEnum tvType[%s]'% ch.mServiceType )
				self.UpdateLabelGUI( self.mCtrlImgServiceTypeTV.getId(),    setPropertyTV )
				self.UpdateLabelGUI( self.mCtrlImgServiceTypeRadio.getId(), setPropertyRadio )

			except Exception, e :
				LOG_TRACE( 'Error exception[%s]'% e )


		if aEvent :
			try :
				#epg name
				self.UpdateLabelGUI( self.mCtrlLblEventName.getId(), deepcopy(aEvent.mEventName) )

				#start,end
				label = TimeToString( aEvent.mStartTime + self.mLocalOffset, TimeFormatEnum.E_HH_MM )
				self.UpdateLabelGUI( self.mCtrlLblEventStartTime.getId(), label )
				label = TimeToString( aEvent.mStartTime + aEvent.mDuration + self.mLocalOffset, TimeFormatEnum.E_HH_MM )
				self.UpdateLabelGUI( self.mCtrlLblEventEndTime.getId(),   label )

				#component
				setPropertyList = []
				setPropertyList = GetPropertyByEPGComponent( aEvent )
				self.UpdateLabelGUI( self.mCtrlGroupComponentData.getId(),  setPropertyList[0] )
				self.UpdateLabelGUI( self.mCtrlGroupComponentDolby.getId(), setPropertyList[1] )
				self.UpdateLabelGUI( self.mCtrlGroupComponentHD.getId(),    setPropertyList[2] )

				"""
				#is Age? agerating check
				if self.mFlag_OnEvent == True :
					isLimit = AgeLimit( self.mPropertyAge, aEvent.mAgeRating )
					if isLimit == True :
						self.mPincodeEnter |= FLAG_MASK_ADD
						LOG_TRACE( 'AgeLimit[%s]'% isLimit )
				"""

			except Exception, e:
				LOG_TRACE( 'Error exception[%s]'% e )


	@RunThread
	def CurrentTimeThread(self):
		while self.mEnableThread:
			#LOG_TRACE( 'repeat <<<<' )
			self.mGMTTime = self.mDataCache.Datetime_GetGMTTime()
			lbl_localTime = TimeToString( self.mGMTTime, TimeFormatEnum.E_HH_MM )
			self.UpdateLabelGUI( self.mCtrlLblEventClock.getId(), lbl_localTime )

			if  ( self.mGMTTime % 10 ) == 0 :
				if self.mFlag_ChannelChanged :
					self.GetEPGList( )
				self.UpdateLocalTime( )

			time.sleep(1)


	def UpdateLocalTime( self ) :
		try:
			if self.mCurrentEvent :
				startTime = self.mCurrentEvent.mStartTime + self.mLocalOffset
				endTime   = startTime + self.mCurrentEvent.mDuration
				pastDuration = endTime - self.mGMTTime
				#LOG_TRACE('past[%s] time[%s] start[%s] duration[%s] offset[%s]'% (pastDuration,self.mGMTTime, self.mCurrentEvent.mStartTime, self.mCurrentEvent.mDuration,self.mLocalOffset ) )

				if self.mGMTTime > endTime: #Already past
					self.UpdateLabelGUI( self.mCtrlProgress.getId(), 100 )
					return

				elif self.mGMTTime < startTime :
					self.UpdateLabelGUI( self.mCtrlProgress.getId(), 0 )
					return

				if pastDuration < 0 : #Already past
					pastDuration = 0

				if self.mCurrentEvent.mDuration > 0 :
					percent = 100 - (pastDuration * 100.0/self.mCurrentEvent.mDuration)
				else :
					percent = 0

				self.UpdateLabelGUI( self.mCtrlProgress.getId(), percent )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def InitLabelInfo(self):
		if self.mFakeChannel :
			self.mCurrentEvent = None
			self.UpdateLabelGUI( self.mCtrlProgress.getId(),                  0 )
			self.UpdateLabelGUI( self.mCtrlLblChannelNumber.getId(), ('%s'% self.mFakeChannel.mNumber) )
			self.UpdateLabelGUI( self.mCtrlLblChannelName.getId(), self.mFakeChannel.mName )
			self.UpdateLabelGUI( self.mCtrlLblLongitudeInfo.getId(),         '' )
			self.UpdateLabelGUI( self.mCtrlLblEventName.getId(),             '' )
			self.UpdateLabelGUI( self.mCtrlLblEventStartTime.getId(),        '' )
			self.UpdateLabelGUI( self.mCtrlLblEventEndTime.getId(),          '' )
			self.UpdateLabelGUI( self.mCtrlImgServiceTypeTV.getId(),     'True' )
			self.UpdateLabelGUI( self.mCtrlImgServiceTypeRadio.getId(), 'False' )
			self.UpdateLabelGUI( self.mCtrlImgLocked.getId(),           'False' )
			self.UpdateLabelGUI( self.mCtrlImgICas.getId(),             'False' )

			self.UpdateLabelGUI( self.mCtrlGroupComponentData.getId(),  'False' )
			self.UpdateLabelGUI( self.mCtrlGroupComponentDolby.getId(), 'False' )
			self.UpdateLabelGUI( self.mCtrlGroupComponentHD.getId(),    'False' )
			self.UpdateLabelGUI( self.mCtrlLblLongitudeInfo.getId(),         '' )

		else:
			pass
			#LOG_TRACE( 'has no channel' )
		
			# todo 
			# show message box : has no channnel


	@GuiLock
	def UpdateLabelGUI( self, aCtrlID = None, aValue = None, aExtra = None ) :
		#LOG_TRACE( 'Enter control[%s] value[%s]'% (aCtrlID, aValue) )

		if aCtrlID == self.mCtrlLblChannelNumber.getId( ) :
			self.mCtrlLblChannelNumber.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblChannelName.getId( ) :
			self.mCtrlLblChannelName.setLabel( aValue )

		elif aCtrlID == self.mCtrlImgServiceTypeTV.getId( ) :
			self.mWin.setProperty( 'ServiceTypeTV', aValue )

		elif aCtrlID == self.mCtrlImgServiceTypeRadio.getId( ) :
			self.mWin.setProperty( 'ServiceTypeRadio', aValue )

		elif aCtrlID == self.mCtrlGroupComponentData.getId( ) :
			self.mWin.setProperty( 'HasSubtitle', aValue )

		elif aCtrlID == self.mCtrlGroupComponentDolby.getId( ) :
			self.mWin.setProperty( 'HasDolby', aValue )

		elif aCtrlID == self.mCtrlGroupComponentHD.getId( ) :
			self.mWin.setProperty( 'HasHD', aValue )

		elif aCtrlID == self.mCtrlLblEventClock.getId( ) :
			self.mCtrlLblEventClock.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblLongitudeInfo.getId( ) :
			self.mCtrlLblLongitudeInfo.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblEventName.getId( ) :
			self.mCtrlLblEventName.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblEventStartTime.getId( ) :
			self.mCtrlLblEventStartTime.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblEventEndTime.getId( ) :
			self.mCtrlLblEventEndTime.setLabel( aValue )

		elif aCtrlID == self.mCtrlProgress.getId( ) :
			self.mCtrlProgress.setPercent( aValue )

		elif aCtrlID == self.mCtrlImgLocked.getId( ) :
			self.mWin.setProperty( 'iLock', aValue )

		elif aCtrlID == self.mCtrlImgICas.getId( ) :
			self.mWin.setProperty( 'iCas', aValue )

		elif aCtrlID == self.mCtrlImgRec1.getId( ) :
			self.mWin.setProperty( 'ViewRecord1', aValue )

		elif aCtrlID == self.mCtrlImgRec2.getId( ) :
			self.mWin.setProperty( 'ViewRecord2', aValue )

		elif aCtrlID == self.mCtrlLblRec1.getId( ) :
			self.mCtrlLblRec1.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblRec2.getId( ) :
			self.mCtrlLblRec2.setLabel( aValue )

		elif aCtrlID == self.mCtrlBtnStartRec.getId( ) :
			self.mCtrlBtnStartRec.setEnabled( aValue )


	def ShowDialog( self, aFocusId, aVisible = False ):
		msg1 = ''
		msg2 = ''

		if aFocusId == self.mCtrlBtnMute.getId():
			msg1 = 'Mute'
			msg2 = 'test'

		elif aFocusId == self.mCtrlBtnTeletext.getId() :
			msg1 = 'Teletext'
			msg2 = 'test'
			#xbmc.executebuiltin('Custom.SetLanguage(French)')

			startTime = time.time()
			for i in range(50000):
				dummy = ElisPropertyEnum( 'Age Limit', self.mCommander ).GetProp( )

			endTime = time.time()
			LOG_TRACE('--------------DBtestCount[%s] time[%s]'% (i, endTime-startTime ) )

			

		elif aFocusId == self.mCtrlBtnSubtitle.getId() :
			msg1 = 'Subtitle'
			msg2 = 'test'
			#xbmc.executebuiltin('Custom.SetLanguage(English)')


		elif aFocusId == self.mCtrlBtnExInfo.getId() :
			if self.mCurrentEvent :
				GuiLock2( True )
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_EXTEND_EPG )
				dialog.SetEPG( self.mCurrentEvent )
				dialog.doModal( )
				GuiLock2( False )


		elif aFocusId == self.mCtrlBtnStartRec.getId() :
			runningCount = self.ShowRecording()
			#LOG_TRACE( 'runningCount[%s]' %runningCount)

			isOK = False
			GuiLock2(True)
			if runningCount < 2 :
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
				dialog.doModal()

				isOK = dialog.IsOK()
				if isOK == E_DIALOG_STATE_YES :
					isOK = True

			else:
				msg = 'Already [%s] recording(s) running' %runningCount
				xbmcgui.Dialog().ok('Infomation', msg )
			GuiLock2(False)

			if isOK :
				time.sleep(1.5)
				self.ShowRecording()
				self.mDataCache.mCacheReload = True

		elif aFocusId == self.mCtrlBtnStopRec.getId() :
			runningCount = self.ShowRecording()
			#LOG_TRACE( 'runningCount[%s]' %runningCount )

			isOK = False
			if runningCount > 0 :
				GuiLock2( True )
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_STOP_RECORD )
				dialog.doModal( )

				isOK = dialog.IsOK()
				if isOK == E_DIALOG_STATE_YES :
					isOK = True
				GuiLock2( False )

			if isOK :
				time.sleep(1.5)
				self.ShowRecording( )
				self.mDataCache.mCacheReload = True

		elif aFocusId == self.mCtrlBtnSettingFormat.getId() :
			context = []
			context.append( ContextItem( 'Video Format', CONTEXT_ACTION_VIDEO_SETTING ) )
			context.append( ContextItem( 'Audio Track',  CONTEXT_ACTION_AUDIO_SETTING ) )

			GuiLock2( True )
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context )
			dialog.doModal( )
			GuiLock2( False )

			selectAction = dialog.GetSelectedAction( )
			if selectAction == -1 :
				return

			if selectAction == CONTEXT_ACTION_VIDEO_SETTING :
				GuiLock2( True )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SET_LIVE_PLATE )
				dialog.SetValue( selectAction )
	 			dialog.doModal( )
	 			GuiLock2( False )

	 		else :
				getCount = self.mDataCache.Audiotrack_GetCount( )
				selectIdx= self.mDataCache.Audiotrack_GetSelectedIndex( )

				context = []
				iSelectAction = 0
				for idx in range(getCount) :
					idxTrack = self.mDataCache.Audiotrack_Get( idx )
					#LOG_TRACE('getTrack name[%s] lang[%s]'% (idxTrack.mName, idxTrack.mLang) )
					if selectIdx == idx :
						label = '%s%s-%s%s' % (E_TAG_COLOR_WHITE,idxTrack.mName,idxTrack.mLang,E_TAG_COLOR_END)
					else :
						label = '%s%s-%s%s' % (E_TAG_COLOR_GREY,idxTrack.mName,idxTrack.mLang,E_TAG_COLOR_END)

					context.append( ContextItem( label, iSelectAction ) )
					iSelectAction += 1

				GuiLock2( True )
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
				dialog.SetProperty( context )
				dialog.doModal( )
				GuiLock2( False )

				selectIdx2 = dialog.GetSelectedAction( )
				self.mDataCache.Audiotrack_select( selectIdx2 )

				#LOG_TRACE('Select[%s --> %s]'% (selectAction, selectIdx2) )


	def ShowRecording( self ) :
		try:
			isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )
			#LOG_TRACE('isRunRecCount[%s]'% isRunRec)

			strLabelRecord1 = ''
			strLabelRecord2 = ''
			setPropertyRecord1 = 'False'
			setPropertyRecord2 = 'False'
			if isRunRec == 1 :
				setPropertyRecord1 = 'True'
				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 0 )
				strLabelRecord1 = '%04d %s'% ( int(recInfo.mChannelNo), recInfo.mChannelName )

			elif isRunRec == 2 :
				setPropertyRecord1 = 'True'
				setPropertyRecord2 = 'True'
				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 0 )
				strLabelRecord1 = '%04d %s'% ( int(recInfo.mChannelNo), recInfo.mChannelName )
				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 1 )
				strLabelRecord2 = '%04d %s'% ( int(recInfo.mChannelNo), recInfo.mChannelName )


			if self.mDataCache.GetChangeDBTableChannel( ) != -1 :
				if isRunRec > 0 :
					#use zapping table, in recording
					self.mDataCache.mChannelListDBTable = E_TABLE_ZAPPING
					self.mDataCache.Channel_GetZappingList( )
					#### data cache re-load ####
					self.mDataCache.LoadChannelList( FLAG_ZAPPING_CHANGE, self.mZappingMode.mServiceType, self.mZappingMode.mMode, self.mZappingMode.mSortingMode, E_REOPEN_TRUE  )

				else :
					self.mDataCache.mChannelListDBTable = E_TABLE_ALLCHANNEL
					if self.mDataCache.mCacheReload :
						self.mDataCache.mCacheReload = False
						#### data cache re-load ####
						self.mDataCache.LoadChannelList( FLAG_ZAPPING_CHANGE, self.mZappingMode.mServiceType, self.mZappingMode.mMode, self.mZappingMode.mSortingMode, E_REOPEN_TRUE  )


				self.mFakeChannel = self.mCurrentChannel
				self.mLastChannel = self.mCurrentChannel
				#LOG_TRACE('table[%s]'% ret)


			btnValue = False
			if isRunRec >= 2 :
				btnValue = False
			else :
				btnValue = True

			self.UpdateLabelGUI( self.mCtrlLblRec1.getId(), strLabelRecord1 )
			self.UpdateLabelGUI( self.mCtrlLblRec2.getId(), strLabelRecord2 )
			self.UpdateLabelGUI( self.mCtrlImgRec1.getId(), setPropertyRecord1 )
			self.UpdateLabelGUI( self.mCtrlImgRec2.getId(), setPropertyRecord2 )
			self.UpdateLabelGUI( self.mCtrlBtnStartRec.getId(), btnValue )

			return isRunRec

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def Close( self ):
		self.mEventBus.Deregister( self )

		self.mEnableThread = False
		#self.CurrentTimeThread().join()
		
		self.StopAsyncTune()
		self.StopAutomaticHide()
		#WinMgr.GetInstance().CloseWindow( )


	def SetLastChannelCertificationPinCode( self, aCertification ) :
		self.mCertification = aCertification


	def SetAutomaticHide( self, aHide=True ) :
		self.mAutomaticHide = aHide


	def GetAutomaticHide( self ) :
		return self.mAutomaticHide

	
	def AsyncAutomaticHide( self ) :
		xbmc.executebuiltin('xbmc.Action(previousmenu)')		
		#self.Close()


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
		self.mAsyncTuneTimer = threading.Timer( 0.5, self.AsyncTuneChannel ) 				
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

			else :
				LOG_ERR('Tune Fail')
			
		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def KeySearch( self, aKey ) :
		if self.mDataCache.mStatusIsArchive :
			#LOG_TRACE('Archive playing now')
			return -1

		if aKey == 0 :
			return -1

		self.mFlag_OnEvent = False

		GuiLock2(True)
		dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CHANNEL_JUMP )
		if self.mCurrentEvent:
			dialog.SetDialogProperty( str(aKey), E_INPUT_MAX, None, self.mCurrentEvent.mStartTime)
		else :
			dialog.SetDialogProperty( str(aKey), E_INPUT_MAX, None)
		dialog.doModal()
		GuiLock2(False)

		self.mFlag_OnEvent = True

		isOK = dialog.IsOK()
		if isOK == E_DIALOG_STATE_YES :

			inputNumber = dialog.GetChannelLast()
			#LOG_TRACE('=========== Jump chNum[%s] currentCh[%s]'% (inputNumber,self.mCurrentChannel.mNumber) )

			if self.mCurrentChannel.mNumber != int(inputNumber) :
				self.mJumpNumber = int(inputNumber)
				self.ChannelTune(CURR_CHANNEL)


