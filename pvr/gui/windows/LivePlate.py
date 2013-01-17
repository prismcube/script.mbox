from pvr.gui.WindowImport import *

E_CONTROL_ID_IMAGE_RECORDING1 			= 10
E_CONTROL_ID_LABEL_RECORDING1 			= 11
E_CONTROL_ID_IMAGE_RECORDING2 			= 15
E_CONTROL_ID_LABEL_RECORDING2 			= 16
E_CONTROL_ID_BUTTON_PREV_EPG 			= 702
E_CONTROL_ID_BUTTON_NEXT_EPG 			= 706
E_CONTROL_ID_LABEL_CHANNEL_NUMBER		= 601
E_CONTROL_ID_LABEL_CHANNEL_NAME			= 602
E_CONTROL_ID_IMAGE_SERVICETYPE_TV		= 603
E_CONTROL_ID_IMAGE_SERVICETYPE_RADIO	= 604
E_CONTROL_ID_GROUP_COMPONENT_DATA		= 605
E_CONTROL_ID_GROUP_COMPONENT_DOLBY 		= 606
E_CONTROL_ID_GROUP_COMPONENT_HD			= 607
E_CONTROL_ID_IMAGE_LOCKED 				= 651
E_CONTROL_ID_IMAGE_ICAS 				= 652
E_CONTROL_ID_LABEL_LONGITUDE_INFO		= 701
E_CONTROL_ID_LABEL_EPG_NAME				= 703
E_CONTROL_ID_LABEL_EPG_STARTTIME		= 704
E_CONTROL_ID_LABEL_EPG_ENDTIME			= 705
E_CONTROL_ID_PROGRESS_EPG 				= 707

E_CONTROL_DEFAULT_HIDE = [ 

	E_CONTROL_ID_BUTTON_BOOKMARK
]

FLAG_MASK_ADD  = 0x01
FLAG_MASK_NONE = 0x00
FLAG_CLOCKMODE_ADMYHM  = 1
FLAG_CLOCKMODE_AHM     = 2
FLAG_CLOCKMODE_HMS     = 3
FLAG_CLOCKMODE_HHMM    = 4
FLAG_CLOCKMODE_INTTIME = 5

NEXT_EPG		= 0
PREV_EPG 		= 1

CURR_CHANNEL	= 0
NEXT_CHANNEL	= 1
PREV_CHANNEL	= 2
INIT_CHANNEL	= 3


class LivePlate( LivePlateWindow ) :
	def __init__( self, *args, **kwargs ) :
		LivePlateWindow.__init__( self, *args, **kwargs )

		self.mLocalTime = 0
		self.mCurrentChannel = None
		self.mLastChannel = None
		self.mFakeChannel = None
		self.mZappingMode = None
		self.mFlag_OnEvent = True
		self.mPropertyAge = 0
		self.mPropertyPincode = -1
		self.mPincodeConfirmed = False

		self.mAutomaticHideTimer = None	
		self.mAsyncEPGTimer = None
		self.mAsyncTuneTimer = None	
		self.mAutomaticHide = False
		self.mEnableLocalThread = False

		self.test_count = 0
		self.test_load = []


	def onInit( self ) :
		self.SetActivate( True )
		
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		LOG_TRACE( 'winID[%d]'% self.mWinId)

		self.mCtrlLblRec1              = self.getControl( E_CONTROL_ID_LABEL_RECORDING1 )
		self.mCtrlLblRec2              = self.getControl( E_CONTROL_ID_LABEL_RECORDING2 )

		#channel, epg info
		self.mCtrlLblChannelNumber     = self.getControl( E_CONTROL_ID_LABEL_CHANNEL_NUMBER )
		self.mCtrlLblChannelName       = self.getControl( E_CONTROL_ID_LABEL_CHANNEL_NAME )
		self.mCtrlLblLongitudeInfo     = self.getControl( E_CONTROL_ID_LABEL_LONGITUDE_INFO )
		self.mCtrlLblEventName         = self.getControl( E_CONTROL_ID_LABEL_EPG_NAME )
		self.mCtrlLblEventStartTime    = self.getControl( E_CONTROL_ID_LABEL_EPG_STARTTIME )
		self.mCtrlLblEventEndTime      = self.getControl( E_CONTROL_ID_LABEL_EPG_ENDTIME )
		self.mCtrlProgress             = self.getControl( E_CONTROL_ID_PROGRESS_EPG )

		#button icon
		self.mCtrlBtnPrevEpg           = self.getControl( E_CONTROL_ID_BUTTON_PREV_EPG )
		self.mCtrlBtnNextEpg           = self.getControl( E_CONTROL_ID_BUTTON_NEXT_EPG )

		self.CheckMediaCenter( )
		self.LoadNoSignalState( )

		self.InitControl( )
		self.SetVisibleControls( E_CONTROL_DEFAULT_HIDE, False )

		self.mFlag_OnEvent = True
		self.mFlag_ChannelChanged = False
		self.mCurrentEPG = None
		self.mEPGList = None
		self.mEPGListIdx = 0
		self.mJumpNumber = 0
		self.mZappingMode = None
		self.mEventId = 0

		self.mAsyncEPGTimer = None
		self.mAsyncTuneTimer = None
		self.mAutomaticHideTimer = None
		self.mLoopCount = 0
		self.mShowOpenWindow = None

		self.mPropertyAge = ElisPropertyEnum( 'Age Limit', self.mCommander ).GetProp( )
		self.mPropertyPincode = ElisPropertyInt( 'PinCode', self.mCommander ).GetProp( )
		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )

		self.mZappingMode = self.mDataCache.Zappingmode_GetCurrent( )
		if not self.mZappingMode :
			self.mZappingMode = ElisIZappingMode( )

		#get channel
		self.ChannelTune( INIT_CHANNEL )
		self.LoadInit( )

		#run thread
		self.mEventBus.Register( self )
		self.mEnableLocalThread = True
		self.EPGProgressThread( )

		if self.mAutomaticHide :
			self.StartAutomaticHide( )
		else :
			self.StopAutomaticHide( )

		if self.mPincodeConfirmed and ( not self.mDataCache.GetPincodeDialog( ) ) :
			thread = threading.Timer( 0.3, self.ShowPincodeDialog )
			thread.start( )
			self.mPincodeConfirmed = False


	def onAction( self, aAction ) :
		LOG_TRACE( 'action=%d' %aAction.getId( ) )	
		if self.IsActivate( ) == False  :
			LOG_TRACE( 'SKIP' )		
			return
	
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 :
			self.SetTuneByNumber( int( actionId ) - Action.REMOTE_0 )

		elif actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :
			rKey = actionId - ( Action.ACTION_JUMP_SMS2 - 2 )
			self.SetTuneByNumber( rKey )

		elif actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.Close( )
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_TIMESHIFT :
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).SetAutomaticHide( True )			
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE, WinMgr.WIN_ID_NULLWINDOW )
			else :
				if self.mShowOpenWindow == WinMgr.WIN_ID_ARCHIVE_WINDOW :
					if HasAvailableRecordingHDD( ) == False :
						return
						
					self.Close( )
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW )

				else :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_SELECT_ITEM :
			self.StopAutomaticHide( )
			self.SetAutomaticHide( False )

		elif actionId == Action.ACTION_CONTEXT_MENU :
			self.StopAutomaticHide( )
			self.SetAutomaticHide( False )
			self.onClick( E_CONTROL_ID_BUTTON_DESCRIPTION_INFO )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.StopAutomaticHide( )
			self.SetAutomaticHide( False )
		
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_BUTTON_PREV_EPG :			
				self.EPGNavigation( PREV_EPG )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.StopAutomaticHide( )
			self.SetAutomaticHide( False )
		
			self.GetFocusId( )
			if self.mFocusId == E_CONTROL_ID_BUTTON_NEXT_EPG:
				self.EPGNavigation( NEXT_EPG )

		elif actionId == Action.ACTION_PAGE_UP :
			self.ChannelTune( NEXT_CHANNEL )

		elif actionId == Action.ACTION_PAGE_DOWN :
			self.ChannelTune( PREV_CHANNEL )

		elif actionId == Action.ACTION_MBOX_XBMC :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode != ElisEnum.E_MODE_LIVE :
				self.mDataCache.Player_Stop( )
				
			self.SetMediaCenter( )
			self.Close( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MEDIACENTER, WinMgr.WIN_ID_LIVE_PLATE )

		elif actionId == Action.ACTION_MBOX_ARCHIVE :
			if HasAvailableRecordingHDD( ) == False :
				return
				
			self.Close( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW )

		elif actionId == Action.ACTION_SHOW_INFO :
			self.Close( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EPG_WINDOW )

		elif actionId == Action.ACTION_MBOX_RECORD :
			self.onClick( E_CONTROL_ID_BUTTON_START_RECORDING )

		elif actionId == Action.ACTION_STOP :
			status = None
			status = self.mDataCache.Player_GetStatus( )
			if status and status.mError == 0 and status.mMode :
				ret = self.mDataCache.Player_Stop( )
			else :
				self.onClick( E_CONTROL_ID_BUTTON_STOP_RECORDING )

		elif actionId == Action.ACTION_PAUSE or actionId == Action.ACTION_PLAYER_PLAY :
			if self.mDataCache.GetLockedState( ) == ElisEnum.E_CC_FAILED_NO_SIGNAL :
				return -1

			if HasAvailableRecordingHDD( ) == False :
				return

			self.Close( )
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = actionId
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )

		elif actionId == Action.ACTION_MBOX_REWIND :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_TIMESHIFT :
				self.Close( )
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = actionId
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )

		elif actionId == Action.ACTION_MBOX_FF :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_TIMESHIFT :
				self.Close( )
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = actionId
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )

		elif actionId == Action.ACTION_MBOX_TVRADIO :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.mDataCache.ToggleTVRadio( )
				if ret :
					self.SetRadioScreen( )
					self.mZappingMode = self.mDataCache.Zappingmode_GetCurrent( )
					self.ChannelTune( INIT_CHANNEL )
				else :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No TV and radio channels available' ) )
					dialog.doModal( )

		elif actionId == Action.ACTION_MBOX_TEXT :
			self.ShowDialog( E_CONTROL_ID_BUTTON_TELETEXT )


	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
		if aControlId == E_CONTROL_ID_BUTTON_MUTE :
			self.StopAutomaticHide( )
			self.SetAutomaticHide( False )
			self.GlobalAction( Action.ACTION_MUTE  )

		elif aControlId == E_CONTROL_ID_BUTTON_DESCRIPTION_INFO :
			self.StopAutomaticHide( )
			self.SetAutomaticHide( False )
			self.ShowDialog( aControlId )

		elif aControlId == E_CONTROL_ID_BUTTON_TELETEXT :
			self.StopAutomaticHide( )
			self.SetAutomaticHide( False )
			self.ShowDialog( aControlId )

		elif aControlId == E_CONTROL_ID_BUTTON_SUBTITLE :
			self.StopAutomaticHide( )
			self.SetAutomaticHide( False )
			self.ShowDialog( aControlId )

		elif aControlId == E_CONTROL_ID_BUTTON_START_RECORDING :
			self.StopAutomaticHide( )
			self.SetAutomaticHide( False )
			self.ShowDialog( aControlId )

		elif aControlId == E_CONTROL_ID_BUTTON_STOP_RECORDING :
			self.StopAutomaticHide( )
			self.SetAutomaticHide( False )
			self.ShowDialog( aControlId )

		elif aControlId == E_CONTROL_ID_BUTTON_SETTING_FORMAT :
			self.StopAutomaticHide( )
			self.SetAutomaticHide( False )
			self.ShowDialog( aControlId )

		elif aControlId == E_CONTROL_ID_BUTTON_PREV_EPG :
			self.StopAutomaticHide( )
			self.SetAutomaticHide( False )
			self.EPGNavigation( PREV_EPG )

		elif aControlId == E_CONTROL_ID_BUTTON_NEXT_EPG :
			self.StopAutomaticHide( )
			self.SetAutomaticHide( False )
			self.EPGNavigation( NEXT_EPG )


	def onFocus(self, aControlId):
		if self.IsActivate( ) == False  :
			return


	def LoadInit( self ):
		self.ShowRecordingInfo( )
		self.InitControlGUI( )
		#self.GetEPGListByChannel( )

		try :
			if self.mCurrentChannel :
				iEPG = None
				#iEPG = self.mDataCache.Epgevent_GetPresent( )
				iEPG = self.mDataCache.GetEpgeventCurrent( )
				if iEPG and iEPG.mError == 0 :
					self.mCurrentEPG = iEPG
					self.mDataCache.Frontdisplay_SetIcon( ElisEnum.E_ICON_HD, iEPG.mHasHDVideo )

				self.UpdateChannelAndEPG( self.mCurrentEPG )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def onEvent(self, aEvent):
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			#LOG_TRACE( '---------CHECK onEVENT winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId( )) )
			channel = self.mCurrentChannel
			if self.mFlag_OnEvent != True :
				#LOG_TRACE('ignore event, mFlag_OnEvent[%s]'% self.mFlag_OnEvent)
				return -1

			if channel == None :
				#LOG_TRACE('ignore event, currentChannel None, [%s]'% channel)
				return -1

			if aEvent.getName( ) == ElisEventCurrentEITReceived.getName( ) :
				if channel.mNumber != self.mFakeChannel.mNumber :
					#LOG_TRACE('ignore event, Channel: current[%s] fake[%s]'% (channel.mNumber, self.mFakeChannel.mNumber) )
					return -1

				if channel.mSid != aEvent.mSid or channel.mTsid != aEvent.mTsid or channel.mOnid != aEvent.mOnid :
					#LOG_TRACE('ignore event, same event')
					return -1

				if self.mCurrentEPG == None or aEvent.mEventId != self.mEventId :
					#LOG_TRACE('id[%s] old[%s] currentEpg[%s]'% ( aEvent.mEventId, self.mEventId, self.mCurrentEPG) )
					self.mEventId = aEvent.mEventId
					self.Epgevent_GetCurrent( channel.mSid, channel.mTsid, channel.mOnid )

			#elif aEvent.getName( ) == ElisEventChannelChangeResult.getName( ) :
			#	self.Epgevent_GetCurrent( channel.mSid, channel.mTsid, channel.mOnid )
			#	LOG_TRACE('----------------------------receive epg')

			elif aEvent.getName( ) == ElisEventChannelChangeResult.getName( ) :
				pass

			elif aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
				if aEvent.mType == ElisEnum.E_EOF_END :
					LOG_TRACE( '---------CHECK onEVENT[%s] stop'% aEvent.getName( ) )
					xbmc.executebuiltin('xbmc.Action(stop)')

			elif aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or \
				 aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
 				self.ShowRecordingInfo( )

			elif aEvent.getName( ) == ElisEventChannelChangedByRecord.getName( ) :
				self.mJumpNumber = aEvent.mChannelNo
				self.ChannelTune( CURR_CHANNEL )
				LOG_TRACE('event[%s] tune[%s] type[%s]'% ( aEvent.getName( ), aEvent.mChannelNo, aEvent.mServiceType ) )

			#elif aEvent.getName( ) == ElisEventTuningStatus.getName( ) :
			#	LOG_TRACE('TunerNo[%s] locked[%s] quality[%s] strength[%s] frequency[%s]'% ( \
			#			aEvent.mTunerNo, aEvent.mIsLocked, aEvent.mSignalQuality, aEvent.mSignalStrength, aEvent.mFrequency ) )
				#ToDo
				#xbmcgui.Dialog( ).ok( MR_LANG('Infomation'), MR_LANG('No Signal') )

		else:
			LOG_TRACE( 'LivePlate winID[%d] this winID[%d]'% ( self.mWinId, xbmcgui.getCurrentWindowId( ) ) )


	def ChannelTune( self, aDir, aInitChannel = 0 ):
		if aDir == PREV_CHANNEL :
			prevChannel = self.mDataCache.Channel_GetPrev( self.mFakeChannel )
			if prevChannel == None or prevChannel.mError != 0 :
				return -1

			SetLock2(True)
			self.mFakeChannel = prevChannel
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NUMBER, ( '%s'% self.mFakeChannel.mNumber ) )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, self.mFakeChannel.mName )
			SetLock2(False)
			
			self.RestartAsyncTune( )

		elif aDir == NEXT_CHANNEL :
			nextChannel = self.mDataCache.Channel_GetNext( self.mFakeChannel )
			if nextChannel == None or nextChannel.mError != 0 :
				return -1

			SetLock2(True)
			self.mFakeChannel = nextChannel
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NUMBER, ( '%s'% self.mFakeChannel.mNumber ) )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, self.mFakeChannel.mName )
			SetLock2(False)

			self.RestartAsyncTune( )

		elif aDir == CURR_CHANNEL :
			jumpChannel = self.mDataCache.Channel_GetCurr( self.mJumpNumber )
			if jumpChannel == None or jumpChannel.mError != 0 :
				return -1
				
			SetLock2(True)
			self.mFakeChannel = jumpChannel
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NUMBER, ( '%s'% self.mFakeChannel.mNumber ) )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, self.mFakeChannel.mName )
			SetLock2(False)
			
			self.RestartAsyncTune( )

		elif aDir == INIT_CHANNEL :
			currNumber = ''
			currName = MR_LANG( 'No Channel' )
			iChannel = self.mDataCache.Channel_GetCurrent( )
			if iChannel == None or iChannel.mError != 0 :
				SetLock2(True)
				self.mCurrentChannel = None
				self.mFakeChannel =	None
				self.mLastChannel =	None
				self.mCurrentEPG = None
				SetLock2(False)				

			else :
				SetLock2(True)			
				self.mCurrentChannel = iChannel
				self.mFakeChannel    = iChannel
				self.mLastChannel    = iChannel
				currNumber = '%s'% self.mFakeChannel.mNumber
				currName = self.mFakeChannel.mName
				SetLock2(False)

			self.InitControlGUI( )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NUMBER, currNumber )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, currName )
			return

		if self.mAutomaticHide == True :
			self.RestartAutomaticHide( )


	def EPGListMoveToIndex( self ) :
		try :
			iEPG = self.mEPGList[self.mEPGListIdx]
			if iEPG :
				self.InitControlGUI( )
				SetLock2(True)
				self.mCurrentEPG = iEPG
				self.mFlag_OnEvent = False
				SetLock2(False)

				self.UpdateChannelAndEPG( iEPG )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def EPGNavigation( self, aDir ):
		if self.mEPGList :
			lastIdx = len( self.mEPGList ) - 1
			if aDir == NEXT_EPG :
				if self.mEPGListIdx + 1 > lastIdx :
					self.mEPGListIdx = lastIdx
				else :
					self.mEPGListIdx += 1

			elif aDir == PREV_EPG:
				if self.mEPGListIdx - 1 < 0 :
					self.mEPGListIdx = 0
				else :
					self.mEPGListIdx -= 1

			self.EPGListMoveToIndex( )


	@SetLock
	def Epgevent_GetCurrent( self, aSid, aTsid, aOnid ) :
		iEPG = None
		#iEPG = self.mDataCache.Epgevent_GetPresent( )
		iEPG = self.mDataCache.GetEpgeventCurrent( )
		if iEPG == None or iEPG.mError != 0 :
			return -1

		self.UpdateChannelAndEPG( iEPG )

		if not self.mCurrentEPG or \
		   iEPG.mEventId != self.mCurrentEPG.mEventId or \
		   iEPG.mSid != self.mCurrentEPG.mSid or \
		   iEPG.mTsid != self.mCurrentEPG.mTsid or \
		   iEPG.mOnid != self.mCurrentEPG.mOnid or \
		   iEPG.mAgeRating != self.mCurrentEPG.mAgeRating or \
		   iEPG.mStartTime != self.mCurrentEPG.mStartTime or \
		   iEPG.mDuration != self.mCurrentEPG.mDuration :
			#update label
			self.mCurrentEPG = iEPG
			self.mDataCache.Frontdisplay_SetIcon( ElisEnum.E_ICON_HD, iEPG.mHasHDVideo )
			#LOG_TRACE('epg DIFFER, event id[%s] current id[%s]'% (iEPG.mEventId, self.mCurrentEPG.mEventId) )
			#LOG_TRACE('-----------------------update epg[%s]'% iEPG.mEventName)

			#check : new event?
			if self.mEPGList :
				#1. aready exist? search in EPGList
				idx = 0
				self.mEPGListIdx = -1
				for item in self.mEPGList :
					#LOG_TRACE('idx[%s] item[%s]'% (idx, item) )
					if item and \
					 	item.mEventId == self.mCurrentEPG.mEventId and \
						item.mSid == self.mCurrentEPG.mSid and \
						item.mTsid == self.mCurrentEPG.mTsid and \
						item.mOnid == self.mCurrentEPG.mOnid :

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
					oldLen = len( self.mEPGList )
					idx = 0
					for idx in range( len( self.mEPGList ) ) :
						if self.mCurrentEPG.mStartTime < self.mEPGList[idx].mStartTime :
							break

					self.mEPGListIdx = idx
					self.mEPGList = self.mEPGList[:idx]+[self.mCurrentEPG]+self.mEPGList[idx:]
					#LOG_TRACE('append new idx[%s], epgTotal:oldlen[%s] newlen[%s]'% (idx, oldLen, len(self.mEPGList)) )


	def GetEPGListByChannel( self ) :
		#do not receive onEvent
		self.mFlag_OnEvent = False
		try :
			channel = self.mCurrentChannel

			if self.mCurrentEPG == None or self.mCurrentEPG.mError != 0 :
				if not channel :
					#LOG_TRACE( 'No Channel' )
					return

				iEPG = None
				#iEPG = self.mDataCache.Epgevent_GetCurrent( channel.mSid, channel.mTsid, channel.mOnid )
				#iEPG = self.mDataCache.Epgevent_GetPresent( )
				iEPG = self.mDataCache.GetEpgeventCurrent( )
				if iEPG == None or iEPG.mError != 0 :
					#receive onEvent
					self.mFlag_OnEvent = True
					return -1
				else :
					self.mCurrentEPG = iEPG

			if channel :
				self.mEPGList = None
				iEPGList = None

				#self.mEPGList = self.mDataCache.Epgevent_GetListByChannelFromEpgCF(  channel.mSid,  channel.mTsid,  channel.mOnid )
				gmtFrom  = self.mDataCache.Datetime_GetLocalTime( )
				gmtUntil = gmtFrom + ( 3600 * 24 * 7 )
				maxCount = 100
				#self.mEPGList = self.mDataCache.Epgevent_GetListByChannel( channel.mSid, channel.mTsid, channel.mOnid, gmtFrom, gmtUntil, maxCount )
				self.mEPGList = self.mCommander.Epgevent_GetList( channel.mSid, channel.mTsid, channel.mOnid, gmtFrom, gmtUntil, maxCount )
				#LOG_TRACE('mSid[%s] mTsid[%s] mOnid[%s] gmtFrom[%s] gmtUntil[%s]'% ( channel.mSid, channel.mTsid, channel.mOnid, gmtFrom, gmtUntil ) )
				if self.mEPGList == None or self.mEPGList[0].mError != 0 :
					self.mFlag_OnEvent = True
					LOG_TRACE( 'EPGList is None\nLeave [%s]'% self.mEPGList )
					return -1

				#LOG_TRACE('-------------------------------------epgList len[%s]'% len( self.mEPGList ) )

				self.mFlag_ChannelChanged = False

				idx = 0
				self.mEPGListIdx = -1
				for item in self.mEPGList :
					#LOG_TRACE( 'idx[%s] item[%s] event[%s]'% ( idx, item, self.mCurrentEPG ) )
					if item != None and item.mError == 0 and \
					   self.mCurrentEPG != None and self.mCurrentEPG.mError == 0 :
						if item.mEventId == self.mCurrentEPG.mEventId and \
							item.mSid == self.mCurrentEPG.mSid and \
							item.mTsid == self.mCurrentEPG.mTsid and \
							item.mOnid == self.mCurrentEPG.mOnid :

							self.mEPGListIdx = idx
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


	def UpdateChannelAndEPG( self, aEpg = None ):
		ch = self.mCurrentChannel
		if ch :
			try :
				#satellite
				label = ''
				if self.mZappingMode.mMode == ElisEnum.E_MODE_FAVORITE :
					#self.UpdatePropertyGUI( E_XML_PROPERTY_FAV, 'True' )
					label = self.mDataCache.Favoritegroup_GetCurrent( )

				else :
					satellite = self.mDataCache.Satellite_GetByChannelNumber( ch.mNumber, -1 )
					if satellite :
						label = GetSelectedLongitudeString( satellite.mLongitude, satellite.mName )

				self.UpdateControlGUI( E_CONTROL_ID_LABEL_LONGITUDE_INFO, label )

				#lock,cas
				if ch.mLocked :
					self.UpdatePropertyGUI( E_XML_PROPERTY_LOCK, 'True' )

				if ch.mIsCA :
					self.UpdatePropertyGUI( E_XML_PROPERTY_CAS, 'True' )

	
			except Exception, e :
				LOG_TRACE( 'Error exception[%s]'% e )


		if aEpg :
			try :
				#epg name
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_NAME, deepcopy( aEpg.mEventName ) )

				#start,end
				label = TimeToString( aEpg.mStartTime + self.mLocalOffset, TimeFormatEnum.E_HH_MM )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_STARTTIME, label )
				label = TimeToString( aEpg.mStartTime + aEpg.mDuration + self.mLocalOffset, TimeFormatEnum.E_HH_MM )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_ENDTIME,   label )

				#component
				setPropertyList = []
				setPropertyList = GetPropertyByEPGComponent( aEpg )
				self.UpdatePropertyGUI( E_XML_PROPERTY_SUBTITLE,  setPropertyList[0] )
				self.UpdatePropertyGUI( E_XML_PROPERTY_DOLBY, setPropertyList[1] )
				self.UpdatePropertyGUI( E_XML_PROPERTY_HD,    setPropertyList[2] )

				#is Age? agerating check
				if ( not self.mDataCache.GetPincodeDialog( ) ) and self.mDataCache.GetParentLock( ) :
					thread = threading.Timer( 0.3, self.ShowPincodeDialog )
					thread.start( )

			except Exception, e:
				LOG_TRACE( 'Error exception[%s]'% e )


	@RunThread
	def EPGProgressThread( self ):
		while self.mEnableLocalThread :
			#LOG_TRACE( 'repeat <<<<' )
			self.mLocalTime = self.mDataCache.Datetime_GetLocalTime( )

			if ( self.mLocalTime % 10 ) == 0 or self.mLoopCount == 3 :
				if self.mFlag_ChannelChanged or self.mEPGList == None :
					self.GetEPGListByChannel( )
				self.UpdateProgress( )

			time.sleep(1)
			self.mLoopCount += 1


	def UpdateProgress( self ) :
		try:
			if self.mCurrentEPG :
				startTime = self.mCurrentEPG.mStartTime + self.mLocalOffset
				endTime   = startTime + self.mCurrentEPG.mDuration
				pastDuration = endTime - self.mLocalTime

				if self.mLocalTime > endTime : #past
					self.mCtrlProgress.setPercent( 100 )
					return

				elif self.mLocalTime < startTime : #future
					self.mCtrlProgress.setPercent( 0 )
					return

				if pastDuration < 0 : #past
					pastDuration = 0

				if self.mCurrentEPG.mDuration > 0 :
					percent = 100 - ( pastDuration * 100.0 / self.mCurrentEPG.mDuration )
				else :
					percent = 0

				self.mCtrlProgress.setPercent( percent )
				#LOG_TRACE('progress percent[%s]'% percent)

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def InitControlGUI( self ) :
		self.UpdateControlGUI( E_CONTROL_ID_PROGRESS_EPG,          0 )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_LONGITUDE_INFO, '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_NAME,       '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_STARTTIME,  '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_ENDTIME,    '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_LONGITUDE_INFO, '' )

		tvValue = 'True'
		raValue = 'False'
		if self.mCurrentChannel :
			if self.mCurrentChannel.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
				tvValue = 'False'
				raValue = 'True'
		else :
			tvValue = 'False'
			raValue = 'False'

		self.UpdatePropertyGUI( E_XML_PROPERTY_TV,      tvValue )
		self.UpdatePropertyGUI( E_XML_PROPERTY_RADIO,   raValue )
		self.UpdatePropertyGUI( E_XML_PROPERTY_LOCK,    'False' )
		self.UpdatePropertyGUI( E_XML_PROPERTY_CAS,     'False' )
		self.UpdatePropertyGUI( E_XML_PROPERTY_FAV,     'False' )
		self.UpdatePropertyGUI( E_XML_PROPERTY_SUBTITLE,'False' )
		self.UpdatePropertyGUI( E_XML_PROPERTY_DOLBY,   'False' )
		self.UpdatePropertyGUI( E_XML_PROPERTY_HD,      'False' )


	def UpdateControlGUI( self, aCtrlID = None, aValue = None, aExtra = None ) :
		#LOG_TRACE( 'Enter control[%s] value[%s]'% (aCtrlID, aValue) )
		if aCtrlID == E_CONTROL_ID_LABEL_CHANNEL_NUMBER :
			self.mCtrlLblChannelNumber.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_CHANNEL_NAME :
			self.mCtrlLblChannelName.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_LONGITUDE_INFO :
			self.mCtrlLblLongitudeInfo.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_EPG_NAME :
			self.mCtrlLblEventName.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_EPG_STARTTIME :
			self.mCtrlLblEventStartTime.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_EPG_ENDTIME :
			self.mCtrlLblEventEndTime.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_PROGRESS_EPG :
			self.mCtrlProgress.setPercent( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_RECORDING1 :
			self.mCtrlLblRec1.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_RECORDING2 :
			self.mCtrlLblRec2.setLabel( aValue )

		#elif aCtrlID == E_CONTROL_ID_BUTTON_START_RECORDING :
		#	self.mCtrlBtnStartRec.setEnabled( aValue )


	def UpdatePropertyGUI( self, aPropertyID = None, aValue = None ) :
		#LOG_TRACE( 'Enter property[%s] value[%s]'% (aPropertyID, aValue) )
		if aPropertyID == None :
			return

		self.mWin.setProperty( aPropertyID, aValue )


	def ShowDialog( self, aFocusId, aVisible = False ) :
		if aFocusId == E_CONTROL_ID_BUTTON_TELETEXT :
			if not self.mPlatform.IsPrismCube( ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No support %s' ) % self.mPlatform.GetName( ) )
				dialog.doModal( )
				return

			if not self.mDataCache.Teletext_Show( ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No teletext available' ) )
				dialog.doModal( )
			else :
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
				return

		elif aFocusId == E_CONTROL_ID_BUTTON_SUBTITLE :
			if not self.mPlatform.IsPrismCube( ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No support %s' ) % self.mPlatform.GetName( ) )
				dialog.doModal( )

		elif aFocusId == E_CONTROL_ID_BUTTON_DESCRIPTION_INFO :
			if self.mCurrentEPG and self.mCurrentEPG.mError == 0 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_EXTEND_EPG )
				dialog.SetEPG( self.mCurrentEPG )
				dialog.doModal( )

		elif aFocusId == E_CONTROL_ID_BUTTON_START_RECORDING :
			self.ShowRecordingStartDialog( )

		elif aFocusId == E_CONTROL_ID_BUTTON_STOP_RECORDING :
			self.ShowRecordingStopDialog( )

		elif aFocusId == E_CONTROL_ID_BUTTON_SETTING_FORMAT :
			self.SetAudioVideoContext( )

		self.RestartAutomaticHide( )


	def ShowRecordingStartDialog( self ) :
		runningCount = self.mDataCache.Record_GetRunningRecorderCount( )
		#LOG_TRACE( 'runningCount[%s]' %runningCount)

		if HasAvailableRecordingHDD( ) == False :
			return

		isOK = False
		if runningCount < 2 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
			dialog.doModal( )

			isOK = dialog.IsOK( )
			if isOK == E_DIALOG_STATE_YES :
				isOK = True

			if dialog.IsOK( ) == E_DIALOG_STATE_ERROR and dialog.GetConflictTimer( ) :
				RecordConflict( dialog.GetConflictTimer( ) )

		else :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'You have reached the maximum number of\nrecordings allowed' ) )
			dialog.doModal( )

		if isOK :
			self.mDataCache.mCacheReload = True


	def ShowRecordingStopDialog( self ) :
		runningCount = self.mDataCache.Record_GetRunningRecorderCount( )
		#LOG_TRACE( 'runningCount[%s]' %runningCount )

		isOK = False
		if runningCount > 0 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_STOP_RECORD )
			dialog.doModal( )

			isOK = dialog.IsOK( )
			if isOK == E_DIALOG_STATE_YES :
				isOK = True

		if isOK :
			self.mDataCache.mCacheReload = True


	def SetAudioVideoContext( self ) :
		context = []
		context.append( ContextItem( 'Video format', CONTEXT_ACTION_VIDEO_SETTING ) )
		context.append( ContextItem( 'Audio track',  CONTEXT_ACTION_AUDIO_SETTING ) )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
		dialog.doModal( )

		selectAction = dialog.GetSelectedAction( )
		if selectAction == -1 :
			return

		if selectAction == CONTEXT_ACTION_VIDEO_SETTING :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SET_AUDIOVIDEO )
			dialog.SetValue( selectAction )
 			dialog.doModal( )

 		else :
			getCount = self.mDataCache.Audiotrack_GetCount( )
			selectIdx= self.mDataCache.Audiotrack_GetSelectedIndex( )

			context = []
			iSelectAction = 0
			for idx in range(getCount) :
				idxTrack = self.mDataCache.Audiotrack_Get( idx )
				#LOG_TRACE('getTrack name[%s] lang[%s]'% (idxTrack.mName, idxTrack.mLang) )
				label = '%s-%s'% ( idxTrack.mName, idxTrack.mLang )

				context.append( ContextItem( label, iSelectAction ) )
				iSelectAction += 1

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context, selectIdx )
			dialog.doModal( )

			selectIdx2 = dialog.GetSelectedAction( )
			self.mDataCache.Audiotrack_select( selectIdx2 )
			#LOG_TRACE('Select[%s --> %s]'% (selectAction, selectIdx2) )


 	def ShowRecordingInfo( self ) :
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

			btnValue = True
			if isRunRec >= 2 :
				btnValue = False

			self.UpdateControlGUI( E_CONTROL_ID_LABEL_RECORDING1, strLabelRecord1 )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_RECORDING2, strLabelRecord2 )
			self.UpdatePropertyGUI( E_XML_PROPERTY_RECORDING1, setPropertyRecord1 )
			self.UpdatePropertyGUI( E_XML_PROPERTY_RECORDING2, setPropertyRecord2 )
			#self.UpdateControlGUI( E_CONTROL_ID_BUTTON_START_RECORDING, btnValue )
			self.SetEnableControl( E_CONTROL_ID_BUTTON_START_RECORDING, btnValue )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def Close( self ) :
		self.mEPGList = []
		self.mEventBus.Deregister( self )
		self.mEnableLocalThread = False

		self.StopAsyncTune( )
		self.StopAutomaticHide( )
		#WinMgr.GetInstance( ).CloseWindow( )


	def SetPincodeRequest( self, aConfirm ) :
		self.mPincodeConfirmed = aConfirm


	def SetAutomaticHide( self, aHide=True ) :
		self.mAutomaticHide = aHide


	def GetAutomaticHide( self ) :
		return self.mAutomaticHide

	
	def AsyncAutomaticHide( self ) :
		#LOG_TRACE('DO WinId=%s'% xbmcgui.getCurrentWindowId( ) )
		#LOG_TRACE('DO DlgWinId=%s'% xbmcgui.getCurrentWindowDialogId( ) )
		xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )
		#self.Close( )


	def RestartAutomaticHide( self ) :
		self.StopAutomaticHide( )
		self.StartAutomaticHide( )

	
	def StartAutomaticHide( self ) :
		#LOG_TRACE('-----hide START')		
		prop = ElisPropertyEnum( 'Channel Banner Duration', self.mCommander )
		bannerTimeout = prop.GetProp( )
		self.mAutomaticHideTimer = threading.Timer( bannerTimeout, self.AsyncAutomaticHide )
		self.mAutomaticHideTimer.start( )


	def StopAutomaticHide( self ) :
		#LOG_TRACE('-----hide STOP')		
		if self.mAutomaticHideTimer and self.mAutomaticHideTimer.isAlive( ) :
			self.mAutomaticHideTimer.cancel( )
			del self.mAutomaticHideTimer
			
		self.mAutomaticHideTimer = None


	def RestartAsyncTune( self ) :
		self.mFlag_ChannelChanged = True
		self.mLoopCount = 0
		self.StopAsyncTune( )
		self.StartAsyncTune( )


	def StartAsyncTune( self ) :
		self.mAsyncTuneTimer = threading.Timer( 0.5, self.AsyncTuneChannel ) 				
		self.mAsyncTuneTimer.start( )


	def StopAsyncTune( self ) :
		if self.mAsyncTuneTimer	and self.mAsyncTuneTimer.isAlive( ) :
			self.mAsyncTuneTimer.cancel( )
			del self.mAsyncTuneTimer

		self.mAsyncTuneTimer  = None


	@SetLock
	def AsyncTuneChannel( self ) :
		try :
			ret = self.mDataCache.Channel_SetCurrent( self.mFakeChannel.mNumber, self.mFakeChannel.mServiceType )
			#self.mFakeChannel.printdebug( )
			if ret == True :
				self.mDataCache.SetParentLock( True )
				self.mCurrentEPG = None
				self.InitControlGUI( )
				self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
				self.mFakeChannel = self.mCurrentChannel
				self.mLastChannel = self.mCurrentChannel
				self.UpdateChannelAndEPG( )
				self.ShowPincodeDialog( )

			else :
				LOG_ERR('Tune failed')
			
		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def SetTuneByNumber( self, aKey ) :
		if aKey == 0 :
			return -1

		self.StopAutomaticHide( )
		self.mFlag_OnEvent = False

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_JUMP )
		dialog.SetDialogProperty( str( aKey ) )
		dialog.doModal( )

		self.mFlag_OnEvent = True

		isOK = dialog.IsOK( )
		if isOK == E_DIALOG_STATE_YES :
			inputNumber = dialog.GetChannelLast( )
			#LOG_TRACE('=========== Jump chNum[%s] currentCh[%s]'% (inputNumber,self.mCurrentChannel.mNumber) )

			if self.mCurrentChannel.mNumber != int( inputNumber ) :
				self.mJumpNumber = int( inputNumber )
				self.ChannelTune( CURR_CHANNEL )

		self.RestartAutomaticHide( )


	def ShowPincodeDialog( self ) :
		if self.mDataCache.GetPincodeDialog( ) :
			LOG_TRACE( 'Aleady pincode dialog' )
			return

		self.mDataCache.SetPincodeDialog( True )
		self.mEventBus.Deregister( self )

		if self.mCurrentChannel and self.mCurrentChannel.mLocked or \
		   self.mDataCache.GetParentLock( ) :
			if self.mAutomaticHide == True :
				self.StopAutomaticHide( )

			if not self.mDataCache.Get_Player_AVBlank( ) :
				self.mDataCache.Player_AVBlank( True )

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_INPUT_PINCODE )
			dialog.SetTitleLabel( MR_LANG( 'Enter your PIN code' ) )
			dialog.doModal( )

			if dialog.GetNextAction( ) == dialog.E_TUNE_NEXT_CHANNEL :
				self.ChannelTune( NEXT_CHANNEL )

			elif dialog.GetNextAction( ) == dialog.E_TUNE_PREV_CHANNEL :
				self.ChannelTune( PREV_CHANNEL )

			elif dialog.GetNextAction( ) == dialog.E_SHOW_EPG_WINDOW :
				xbmc.executebuiltin( 'xbmc.Action(info)' )

			elif dialog.GetNextAction( ) == dialog.E_SHOW_ARCHIVE_WINDOW :
				from pvr.HiddenTestMgr import SendCommand
				SendCommand( 'VKEY_ARCHIVE' )

			else :
				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					self.mDataCache.SetParentLock( False )
					if self.mDataCache.Get_Player_AVBlank( ) :
						self.mDataCache.Player_AVBlank( False )

				LOG_TRACE( 'Has no next action' )
				if self.mAutomaticHide == True :
					self.RestartAutomaticHide( )
		else :
			if self.mDataCache.Get_Player_AVBlank( ) :
				self.mDataCache.Player_AVBlank( False )

		if WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_LIVE_PLATE : # Still showing 
			self.mEventBus.Register( self )

		self.mDataCache.SetPincodeDialog( False )


