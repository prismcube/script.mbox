from pvr.gui.WindowImport import *


BUTTON_ID_EPG_MODE				= 100
RADIIOBUTTON_ID_EXTRA			= 101
LIST_ID_COMMON_EPG				= 3500
LIST_ID_BIG_EPG					= 3510

SCROLL_ID_COMMON_EPG			= 3501
SCROLL_ID_BIG_EPG				= 3511


LABEL_ID_TIME					= 300
LABEL_ID_DATE					= 301
LABEL_ID_DURATION				= 302
LABEL_ID_EVENT_NAME				= 303
LABEL_ID_EPG_CHANNEL_NAME		= 400
LABEL_ID_CURRNET_CHANNEL_NAME	= 401

E_VIEW_CHANNEL					= 0
E_VIEW_CURRENT					= 1
E_VIEW_FOLLOWING				= 2
E_VIEW_END						= 3

E_NOMAL_UPDATE_TIME				= 30
E_SHORT_UPDATE_TIME				= 1

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
CONTEXT_SELECT_CHANNEL			= 8


MININUM_KEYWORD_SIZE			= 3

E_USE_FIXED_INTERVAL			= False

class EPGWindow( BaseWindow ) :

	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mServiceType = ElisEnum.E_SERVICE_TYPE_TV
		self.mLock = thread.allocate_lock( )		

	
	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( MR_LANG( 'EPG' ) )
		self.SetPipScreen( )
		self.LoadNoSignalState( )

		self.mEPGCount = 0
		self.mSelectedIndex = 0
		self.mEPGList = []
		self.mEPGListHash = {}
		self.mListItems = []
		self.mTimerList = []

		self.mEPGMode = int( GetSetting( 'EPG_MODE' ) )
		self.mCtrlEPGMode = self.getControl( BUTTON_ID_EPG_MODE )
		self.mCtrlList = self.getControl( LIST_ID_COMMON_EPG )
		self.mCtrlBigList = self.getControl( LIST_ID_BIG_EPG )

		self.mCtrlTimeLabel = self.getControl( LABEL_ID_TIME )
		self.mCtrlDateLabel = self.getControl( LABEL_ID_DATE )
		self.mCtrlDurationLabel = self.getControl( LABEL_ID_DURATION )
		self.mCtrlEPGDescription = self.getControl( LABEL_ID_EVENT_NAME )
		self.mCtrlEPGChannelLabel = self.getControl( LABEL_ID_EPG_CHANNEL_NAME )
		self.mCtrlCurrentChannelLabel = self.getControl( LABEL_ID_CURRNET_CHANNEL_NAME )

		self.ResetEPGInfomation( )
		self.UpdateViewMode( )
		self.InitControl( )
		self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( )
		self.mServiceType = self.mCurrentMode.mServiceType
		self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
		LOG_TRACE( 'ZeppingMode(%d,%d,%d)' %( self.mCurrentMode.mServiceType, self.mCurrentMode.mMode, self.mCurrentMode.mSortingMode ) )
		#self.mChannelList = self.mDataCache.Channel_GetList( )
		self.mChannelList = self.mDataCache.Channel_GetAllChannels( self.mServiceType )

		if self.mChannelList == None :
			LOG_WARN( 'No Channel List' )
		else:
			LOG_TRACE( "ChannelList=%d" %len( self.mChannelList ) )
		
		self.mSelectChannel = self.mCurrentChannel
		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		self.mGMTTime = 0
		LOG_TRACE( 'CHANNEL current=%s select=%s' %( self.mCurrentChannel, self.mSelectChannel ) )

		self.UpdateCurrentChannel( )
		self.UpdateAllEPGList( )

		self.mEventBus.Register( self )

		self.StartEPGUpdateTimer( )
		
		self.mInitialized = True


	def onAction( self, aAction ) :
		self.GetFocusId()
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return


		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR or actionId == Action.ACTION_SHOW_INFO:
			self.Close( )

		elif  actionId == Action.ACTION_SELECT_ITEM :
			#if self.mFocusId == LIST_ID_COMMON_EPG or self.mFocusId == LIST_ID_BIG_EPG :
			self.Tune( )
	
		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT :
			pass

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN :
			if self.mFocusId == LIST_ID_COMMON_EPG or self.mFocusId == LIST_ID_BIG_EPG or self.mFocusId == SCROLL_ID_COMMON_EPG or self.mFocusId == SCROLL_ID_BIG_EPG:
				self.UpdateEPGInfomation( )

		elif actionId == Action.ACTION_PAGE_UP  or actionId == Action.ACTION_PAGE_DOWN :
			if self.mFocusId == LIST_ID_COMMON_EPG or self.mFocusId == LIST_ID_BIG_EPG or self.mFocusId == SCROLL_ID_COMMON_EPG or self.mFocusId == SCROLL_ID_BIG_EPG:
				self.UpdateEPGInfomation( )

		elif actionId == Action.ACTION_CONTEXT_MENU:
			if self.mChannelList == None or len( self.mChannelList ) <= 0 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No channel is available' ) )			
	 			dialog.doModal( )
				return
		
			self.mEventBus.Deregister( self )
			self.StopEPGUpdateTimer( )

			contextAction = self.ShowContextMenu( )

			if contextAction == CONTEXT_SHOW_ALL_TIMERS :
				self.DoContextAction( contextAction ) 
			else :
				self.DoContextAction( contextAction ) 
				self.StartEPGUpdateTimer( )
				self.mEventBus.Register( self )			

		elif actionId == Action.ACTION_MBOX_TVRADIO :
			self.mEventBus.Deregister( self )
			self.StopEPGUpdateTimer( )
			ret = self.ToggleTVRadio( )

			if ret :
				self.SetRadioScreen( self.mServiceType )
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No TV/Radio channel is available' ) )
				dialog.doModal( )

			self.StartEPGUpdateTimer( )
			self.mEventBus.Register( self )			
			
		elif actionId == Action.ACTION_MBOX_RECORD :
			self.mEventBus.Deregister( self )
			self.StopEPGUpdateTimer( )
			self.RecordByHotKey( )

			self.StartEPGUpdateTimer( )
			self.mEventBus.Register( self )			

		elif actionId == Action.ACTION_STOP :
			self.mEventBus.Deregister( self )
			self.StopEPGUpdateTimer( )
			self.StopByHotKey( )
			
			self.StartEPGUpdateTimer( )
			self.mEventBus.Register( self )			

		elif actionId == Action.ACTION_MBOX_REWIND :
			self.SelectPrevChannel( )

		elif actionId == Action.ACTION_MBOX_FF : #no service
			self.SelectNextChannel( )			


	def onClick( self, aControlId ) :
		LOG_TRACE( 'aControlId=%d' %aControlId )

		if aControlId == BUTTON_ID_EPG_MODE :
			self.mEventBus.Deregister( self )
			self.StopEPGUpdateTimer( )
	
			#self.mLock.acquire( )

			self.mEPGMode += 1
			if self.mEPGMode >= E_VIEW_END :
				self.mEPGMode = 0 

			self.mSelectChannel = self.mCurrentChannel

			SetSetting( 'EPG_MODE','%d' %self.mEPGMode )

			self.UpdateViewMode( )
			self.InitControl( )
			self.UpdateAllEPGList( )
			#self.mLock.release( )

			self.mEventBus.Register( self )
			self.StartEPGUpdateTimer( )
		
		elif aControlId == RADIIOBUTTON_ID_EXTRA :
			pass

		elif aControlId == LIST_ID_COMMON_EPG :
			pass


	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			if aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
				#if self.mIsUpdateEnable == True	:
				LOG_TRACE( 'record start/stop event' )
				self.StopEPGUpdateTimer( )
				self.UpdateListUpdateOnly( )
				self.StartEPGUpdateTimer( E_SHORT_UPDATE_TIME )

			"""
			elif aEvent.getName( ) == ElisEventCurrentEITReceived.getName( ) :
				self.DoCurrentEITReceived( aEvent )
			"""


	def Close( self ) :
		self.mEventBus.Deregister( self )	

		self.StopEPGUpdateTimer( )
		self.SetVideoRestore( )
		WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )


	def InitControl( self ) :

		if self.mEPGMode == E_VIEW_CHANNEL :
			self.mCtrlEPGMode.setLabel( '%s: %s' %( MR_LANG( 'VIEW' ), MR_LANG( 'CHANNEL' ) ) )
		elif self.mEPGMode == E_VIEW_CURRENT :			
			self.mCtrlEPGMode.setLabel( '%s: %s' %( MR_LANG( 'VIEW' ), MR_LANG( 'CURRENT' ) ) )		
		elif self.mEPGMode == E_VIEW_FOLLOWING :			
			self.mCtrlEPGMode.setLabel( '%s: %s' %( MR_LANG( 'VIEW' ),  MR_LANG( 'FOLLOWING' ) ) )		
		else :
			LOG_WARN( 'Unknown epg mode' )
			

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
			
		LOG_TRACE( '---------------------self.mEPGMode=%d' %self.mEPGMode )


	def Flush( self ) :
		self.mEPGCount = 0
		self.mEPGList = []
		self.mEPGListHash = {}


	def Load( self ) :

		LOG_TRACE( '----------------------------------->Start' )
		self.mDebugStart = time.time( )

		self.mLock.acquire( )
		
		self.mGMTTime = self.mDataCache.Datetime_GetGMTTime( )

		self.mEPGList = None
		
		if self.mEPGMode == E_VIEW_CHANNEL :
			self.LoadByChannel( )
		elif self.mEPGMode == E_VIEW_CURRENT :			
			self.LoadByCurrent( )
		elif self.mEPGMode == E_VIEW_FOLLOWING :			
			self.LoadByFollowing( )
		else :
			self.mEPGMode = E_VIEW_CHANNEL 		
			self.LoadByChannel( )

		self.mLock.release( )
		LOG_TRACE( '----------------------------------->End' )			
		self.mDebugEnd = time.time( )
		print ' epg loading test time =%s' %( self.mDebugEnd  - self.mDebugStart )


	def LoadByChannel( self ) :
		gmtFrom = self.mGMTTime 
		gmtUntil = self.mGMTTime + E_MAX_SCHEDULE_DAYS*3600*24

		LOG_ERR( 'START : localoffset=%d' %self.mLocalOffset )
		LOG_ERR( 'START : %s' % TimeToString( gmtFrom+self.mLocalOffset, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
		LOG_ERR( 'START : %d : %d %d' % ( self.mSelectChannel.mSid,  self.mSelectChannel.mTsid,  self.mSelectChannel.mOnid) )
		
		try :
			self.mEPGList = self.mDataCache.Epgevent_GetListByChannelFromEpgCF(  self.mSelectChannel.mSid,  self.mSelectChannel.mTsid,  self.mSelectChannel.mOnid )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		if self.mEPGList == None or self.mEPGList[0].mError != 0 :
			self.mEPGList = None
			return

		if self.mEPGList == None or len ( self.mEPGList ) <= 0 :
			return

		LOG_ERR( 'self.mEPGList COUNT=%d' %len(self.mEPGList ) )

		for epg in self.mEPGList :
			self.mEPGListHash[ '%d:%d:%d' %( epg.mSid, epg.mTsid, epg.mOnid) ] = epg


	def LoadByCurrent( self ) :
	
		try :
			self.mEPGList = self.mDataCache.Epgevent_GetCurrentListByEpgCF( self.mServiceType )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		if self.mEPGList == None or len ( self.mEPGList ) <= 0 :
			return

		LOG_TRACE( 'self.mEPGList COUNT=%d' %len( self.mEPGList ) )
		
		for epg in self.mEPGList :
			self.mEPGListHash[ '%d:%d:%d' %( epg.mSid, epg.mTsid, epg.mOnid) ] = epg


	def LoadByFollowing( self ) :		
		try :
			self.mEPGList = self.mDataCache.Epgevent_GetFollowingListByEpgCF( self.mServiceType )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		if self.mEPGList == None or len ( self.mEPGList ) <= 0 :
			return

		LOG_TRACE( 'self.mEPGList COUNT=%d' %len(self.mEPGList ) )
		
		for epg in self.mEPGList :
			self.mEPGListHash[ '%d:%d:%d' %( epg.mSid, epg.mTsid, epg.mOnid) ] = epg


	def UpdateSelcetedPosition( self ) :
		if self.mChannelList == None :
			self.mWin.setProperty( 'SelectedPosition', '0' )
			return

		selectedPos = 0
		
		if self.mEPGMode == E_VIEW_CHANNEL :
			selectedPos = self.mCtrlList.getSelectedPosition( )		
		else :
			selectedPos = self.mCtrlBigList.getSelectedPosition( )

		self.mWin.setProperty( 'SelectedPosition', '%d' %( selectedPos+1 ) )


	def FocusCurrentChannel( self ) :
		if self.mChannelList == None :
			return

		if self.mEPGMode == E_VIEW_CHANNEL :
			self.mCtrlList.selectItem( 0 )
		else :
			fucusIndex = 0
			for channel in self.mChannelList:
				if channel.mNumber == self.mCurrentChannel.mNumber :
					break
				fucusIndex += 1

			self.mCtrlBigList.selectItem( fucusIndex )


	def UpdateSelectedChannel( self ) :
		if self.mChannelList == None or len( self.mChannelList ) <= 0 :
			self.mCtrlEPGChannelLabel.setLabel( MR_LANG( 'No Channels' ) )		
		elif self.mSelectChannel :
			self.mCtrlEPGChannelLabel.setLabel( '%04d %s' %( self.mSelectChannel.mNumber, self.mSelectChannel.mName ) )
		else:
			self.mCtrlEPGChannelLabel.setLabel( MR_LANG( 'No Channels' ) )


	def UpdateCurrentChannel( self ) :
		if self.mCurrentChannel :
			self.mCtrlCurrentChannelLabel.setLabel( self.mCurrentChannel.mName )
		else :
			self.mCtrlCurrentChannelLabel.setLabel( '' )


	def UpdateEPGInfomation( self ) :
		self.UpdateSelcetedPosition( )
		
		epg = self.GetSelectedEPG( )

		try :
			if epg :
				self.mCtrlTimeLabel.setLabel( '%s~%s' % ( TimeToString( epg.mStartTime + self.mLocalOffset, TimeFormatEnum.E_HH_MM ), TimeToString( epg.mStartTime + self.mLocalOffset+ epg.mDuration, TimeFormatEnum.E_HH_MM ) ) )
				self.mCtrlDateLabel.setLabel( '%s' % TimeToString( epg.mStartTime + self.mLocalOffset, TimeFormatEnum.E_AW_DD_MM_YYYY ) )
				self.mCtrlDurationLabel.setLabel( '%d%s' %( ( epg.mDuration / 60 ), MR_LANG( 'mins' ) ) )				

				if epg.mEventDescription and epg.mEventDescription.upper() != '(NULL)' :
					self.mCtrlEPGDescription.setText( epg.mEventDescription )
				elif epg.mEventName :
					self.mCtrlEPGDescription.setText( epg.mEventName )
				else :
					self.mCtrlEPGDescription.setText( '' )

				self.mWin.setProperty( 'HasHD', HasEPGComponent( epg, ElisEnum.E_HasHDVideo ) )
				self.mWin.setProperty( 'HasDolby', HasEPGComponent( epg, ElisEnum.E_HasDolbyDigital ) )
				self.mWin.setProperty( 'HasSubtitle', HasEPGComponent( epg, ElisEnum.E_HasSubtitles ) )
			else :
				self.ResetEPGInfomation( )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def	ResetEPGInfomation( self ) :
		self.mCtrlTimeLabel.setLabel( '' )
		self.mCtrlDateLabel.setLabel( '' )
		self.mCtrlDurationLabel.setLabel( '' )
		self.mCtrlEPGDescription.setText( '' )
		
		self.mWin.setProperty( 'HasSubtitle', 'False' )
		self.mWin.setProperty( 'HasDolby', 'False' )
		self.mWin.setProperty( 'HasHD', 'False' )


	def UpdateListUpdateOnly( self ) :
		self.UpdateList( True )


	def UpdateList( self, aUpdateOnly=False ) :
		LOG_TRACE( '------------------------> Start Update----------' )
		#self.mLock.acquire( )	
		if aUpdateOnly == False :
			self.mLock.acquire( )	
			self.mListItems = []
			self.mLock.release( )

		self.LoadTimerList( )

		if self.mEPGMode == E_VIEW_CHANNEL :
			if self.mEPGList == None :
				self.mCtrlList.reset( )
				return

			try :		
				for i in range( len( self.mEPGList ) ) :
					epgEvent = self.mEPGList[i]
					#epgEvent.printdebug()
					if aUpdateOnly == False :
						listItem = xbmcgui.ListItem( TimeToString( epgEvent.mStartTime + self.mLocalOffset, TimeFormatEnum.E_HH_MM ), epgEvent.mEventName )
					else :
						listItem = self.mListItems[i]
						listItem.setLabel( TimeToString( epgEvent.mStartTime + self.mLocalOffset, TimeFormatEnum.E_HH_MM ) )
						listItem.setLabel2( epgEvent.mEventName )

					listItem.setProperty( 'EPGDate', TimeToString( epgEvent.mStartTime + self.mLocalOffset, TimeFormatEnum.E_AW_DD_MON ) )

					timer = self.GetTimerByEPG( epgEvent )
					if timer :
						if self.IsRunningTimer( timer ) == True :
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
					xbmc.executebuiltin( 'container.update' )
					#xbmc.executebuiltin('xbmc.Container.SetViewMode(%d)' %E_VIEW_CHANNEL)
				
			except Exception, ex :
				LOG_ERR( "Exception %s" %ex )

		elif self.mEPGMode == E_VIEW_CURRENT :
			self.mDebugStart = time.time( )		
			if self.mChannelList == None :
				self.mCtrlBigList.reset( )
				return

			currentTime = self.mDataCache.Datetime_GetLocalTime( )
			
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
							listItem.setLabel( tempChannelName )
							listItem.setLabel2( epgEvent.mEventName )

						epgStart = epgEvent.mStartTime + self.mLocalOffset
						tempName = '%s~%s' % ( TimeToString( epgStart, TimeFormatEnum.E_HH_MM ), TimeToString( epgStart + epgEvent.mDuration, TimeFormatEnum.E_HH_MM ) )
						listItem.setProperty( 'StartTime', tempName )
						listItem.setProperty( 'Duration', '' )
						listItem.setProperty( 'HasEvent', 'true' )
						listItem.setProperty( 'Percent', '%s' %self.CalculateProgress( currentTime, epgStart, epgEvent.mDuration  ) )
						timer= self.GetTimerByEPG( epgEvent )

						if timer :
							if self.IsRunningTimer( timer ) == True :
								listItem.setProperty( 'TimerType', 'Running' )
							else :
								listItem.setProperty( 'TimerType', 'Schedule' )						
						else :
							listItem.setProperty( 'TimerType', 'None' )

					else :
						if aUpdateOnly == False :					
							listItem = xbmcgui.ListItem( tempChannelName, MR_LANG( 'No event' ) )
						else:
							listItem = self.mListItems[i]
							listItem.setLabel( tempChannelName )
							listItem.setLabel2( MR_LANG( 'No event' ) )

						listItem.setProperty( 'StartTime', '' )
						listItem.setProperty( 'Duration', '' )						
						listItem.setProperty( 'HasEvent', 'false' )

						timer = self.GetTimerByChannel( channel )

						if timer :
							if self.IsRunningTimer( timer ) == True :
								listItem.setProperty( 'TimerType', 'Running' )
							else :
								listItem.setProperty( 'TimerType', 'Schedule' )						
						else :
							listItem.setProperty( 'TimerType', 'None' )

					#ListItem.PercentPlayed
					if aUpdateOnly == False :
						self.mListItems.append( listItem )

				except Exception, ex :
					LOG_ERR( "Exception %s" %ex )

			if aUpdateOnly == False :
				self.mCtrlBigList.addItems( self.mListItems )
				#self.setFocusId( LIST_ID_BIG_EPG )
			else :
				xbmc.executebuiltin( 'container.update' )			
				#xbmc.executebuiltin('xbmc.Container.SetViewMode(%d)' %E_VIEW_CURRENT)

			self.mDebugEnd = time.time( )
			print 'epg loading test =%s' %( self.mDebugEnd  - self.mDebugStart )
				

		elif self.mEPGMode == E_VIEW_FOLLOWING :
			if self.mChannelList == None :
				self.mCtrlBigList.reset( )
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
							listItem.setLabel( tempChannelName )
							listItem.setLabel2( epgEvent.mEventName )

						epgStart = epgEvent.mStartTime + self.mLocalOffset
						tempName = '%s~%s' % ( TimeToString( epgStart, TimeFormatEnum.E_HH_MM ), TimeToString( epgStart + epgEvent.mDuration, TimeFormatEnum.E_HH_MM ) )
						listItem.setProperty( 'StartTime', tempName )
						listItem.setProperty( 'Duration', '' )						
						listItem.setProperty( 'HasEvent', 'true' )
 
						timer = self.GetTimerByEPG( epgEvent )
						if timer :
							if self.IsRunningTimer( timer ) == True :
								listItem.setProperty( 'TimerType', 'Running' )
							else :
								listItem.setProperty( 'TimerType', 'Schedule' )						
						else :
							listItem.setProperty( 'TimerType', 'None' )
						
					else :
						if aUpdateOnly == False :
							listItem = xbmcgui.ListItem( tempChannelName, MR_LANG( 'No event' ) )
						else :
							listItem = self.mListItems[i]
							listItem.setLabel( tempChannelName )
							listItem.setLabel2( MR_LANG( 'No event' ) )
						
						listItem.setProperty( 'StartTime', '' )
						listItem.setProperty( 'Duration', '' )						
						listItem.setProperty( 'HasEvent', 'false' )

 						timer = self.GetTimerByChannel( channel )

						if timer :
							if self.IsRunningTimer( timer ) == True :
								listItem.setProperty( 'TimerType', 'Running' )
							else :
								listItem.setProperty( 'TimerType', 'Schedule' )						
						else :
							listItem.setProperty( 'TimerType', 'None' )

					#ListItem.PercentPlayed
					if aUpdateOnly == False :					
						self.mListItems.append( listItem )

				except Exception, ex :
					LOG_ERR( "Exception %s" %ex )

			if aUpdateOnly == False :
				self.mCtrlBigList.addItems( self.mListItems )
				#self.setFocusId( LIST_ID_BIG_EPG )
			else :
				xbmc.executebuiltin( 'container.update' )			
				#xbmc.executebuiltin('xbmc.Container.SetViewMode(%d)' %E_VIEW_FOLLOWING)


	def GetEPGByIds( self, aSid, aTsid, aOnid ) :
		return self.mEPGListHash.get( '%d:%d:%d' %( aSid, aTsid, aOnid ), None )
		"""
		if self.mEPGList == None :
			return None

		for i in range( len( self.mEPGList ) ) :
			epgEvent = self.mEPGList[i]
			if epgEvent.mSid == aSid and epgEvent.mTsid == aTsid and epgEvent.mOnid == aOnid :
				return epgEvent

		return None
		"""


	@RunThread
	def CurrentTimeThread( self ) :
		pass


	@SetLock
	def UpdateLocalTime( self ) :
		pass


	def ShowContextMenu( self ) :
		context = []
		
		selectedEPG = self.GetSelectedEPG( )

		if self.mEPGMode == E_VIEW_CHANNEL :
			context.append( ContextItem( MR_LANG( 'Select channel' ), CONTEXT_SELECT_CHANNEL ) )

		if selectedEPG :
			"""
			if selectedEPG.mHasTimer :
				context.append( ContextItem( 'Edit Timer', CONTEXT_EDIT_TIMER ) )
				context.append( ContextItem( 'Delete Timer', CONTEXT_DELETE_TIMER ) )
			else :
			"""
			timer = self.GetTimerByEPG( selectedEPG )
			if timer :
				context.append( ContextItem( MR_LANG( 'Edit timer' ), CONTEXT_EDIT_TIMER ) )
				context.append( ContextItem( MR_LANG( 'Delete timer' ), CONTEXT_DELETE_TIMER ) )
			else:
				context.append( ContextItem( MR_LANG( 'Add timer' ), CONTEXT_ADD_EPG_TIMER ) )
				context.append( ContextItem( MR_LANG( 'Add manual timer' ), CONTEXT_ADD_MANUAL_TIMER ) )

			if 	self.mTimerList and len( self.mTimerList ) > 0 :
				context.append( ContextItem( MR_LANG( 'Delete all timers' ), CONTEXT_DELETE_ALL_TIMERS ) )
				context.append( ContextItem( MR_LANG( 'Show all timers' ), CONTEXT_SHOW_ALL_TIMERS ) )

			context.append( ContextItem( MR_LANG( 'Search' ), CONTEXT_SEARCH ) )					
			context.append( ContextItem( MR_LANG( 'Extend infomation' ), CONTEXT_EXTEND_INFOMATION ) )		

		else :
			timer = None

			if self.mEPGMode == E_VIEW_CURRENT or self.mEPGMode == E_VIEW_FOLLOWING :				
				selectedPos = self.mCtrlBigList.getSelectedPosition( )
				if selectedPos >= 0 and self.mChannelList and selectedPos < len( self.mChannelList ) :
					channel = self.mChannelList[ selectedPos ]
					timer = self.GetTimerByChannel( channel )

			if timer :
				context.append( ContextItem( MR_LANG( 'Edit timer' ), CONTEXT_EDIT_TIMER ) )
				context.append( ContextItem( MR_LANG( 'Delete timer' ), CONTEXT_DELETE_TIMER ) )
			else :
				context.append( ContextItem( MR_LANG( 'Add manual timer' ), CONTEXT_ADD_MANUAL_TIMER ) )

			if 	self.mTimerList and len( self.mTimerList ) > 0 :
				context.append( ContextItem( MR_LANG( 'Delete all timers' ), CONTEXT_DELETE_ALL_TIMERS ) )	
				context.append( ContextItem( MR_LANG( 'Show all timers' ), CONTEXT_SHOW_ALL_TIMERS ) )				

			context.append( ContextItem( MR_LANG( 'Search' ), CONTEXT_SEARCH ) )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
		dialog.doModal( )

		contextAction = dialog.GetSelectedAction( )

		return contextAction


	def DoContextAction( self, aContextAction ) :
		LOG_TRACE( 'aContextAction=%d' %aContextAction )

		if aContextAction == CONTEXT_ADD_EPG_TIMER :
			epg = self.GetSelectedEPG( )
			if epg :
				self.ShowEPGTimer( epg )

		elif aContextAction == CONTEXT_ADD_MANUAL_TIMER :
			epg = self.GetSelectedEPG( )
			self.ShowManualTimer( epg )

		elif aContextAction == CONTEXT_EDIT_TIMER :
			self.ShowEditTimer( )

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
			
		elif aContextAction == CONTEXT_SELECT_CHANNEL :
			self.ShowSelectChannel( )


	def ShowEPGTimer( self, aEPG ) :
		LOG_TRACE( 'ShowEPGTimer' )

		from pvr.GuiHelper import HasAvailableRecordingHDD
		if HasAvailableRecordingHDD( ) == False :
			return
			
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_ADD_TIMER )
		dialog.SetEPG( aEPG )
		dialog.doModal( )

		try :
			if dialog.IsOK() == E_DIALOG_STATE_YES :
				ret = self.mDataCache.Timer_AddEPGTimer( True, 0, aEPG )
				LOG_ERR( 'Conflict ret=%s' %ret )
				if ret[0].mParam == -1 or ret[0].mError == -1 :
					from pvr.GuiHelper import RecordConflict
					RecordConflict( ret )
					return

			else :
				LOG_TRACE( '' )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		self.UpdateListUpdateOnly( )
		

	def ShowEditTimer( self ) :

		from pvr.GuiHelper import HasAvailableRecordingHDD
		if HasAvailableRecordingHDD( ) == False :
			return
			
		selectedEPG = self.GetSelectedEPG( )

		timer = None

		if selectedEPG :
			timer = self.GetTimerByEPG( selectedEPG )
			if timer and timer.mTimerId > 0 :	# Edit Mode
				self.ShowManualTimer( selectedEPG, timer )

		else :
			if self.mEPGMode == E_VIEW_CURRENT or self.mEPGMode == E_VIEW_FOLLOWING :
				selectedPos = self.mCtrlBigList.getSelectedPosition( )
				if selectedPos >= 0 and self.mChannelList and selectedPos < len( self.mChannelList ) :
					channel = self.mChannelList[ selectedPos ]
					timer = self.GetTimerByChannel( channel )					
		
			if timer and timer.mTimerId > 0 :	# Edit Mode
				self.ShowManualTimer( None, timer )				
	

	def ShowManualTimer( self, aEPG=None, aTimer=None ) :

		"""
		if aTimer :
			if self.IsRunningTimer( aTimer ) == True :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'WARN', 'Recording is running' )
	 			dialog.doModal( )
				return
		"""

		from pvr.GuiHelper import HasAvailableRecordingHDD
		if HasAvailableRecordingHDD( ) == False :
			return

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_ADD_MANUAL_TIMER )


		if aTimer :
			dialog.SetTimer( aTimer, self.IsRunningTimer( aTimer ) )

		if aEPG :
			dialog.SetEPG( aEPG )

		channel = None
		if self.mEPGMode == E_VIEW_CHANNEL  :
			channel = self.mDataCache.Channel_GetCurrent( )
		else :
			selectedPos = self.mCtrlBigList.getSelectedPosition( )
			if selectedPos >= 0 and self.mChannelList and selectedPos < len( self.mChannelList ) :
				channel = self.mChannelList[ selectedPos ]
			else :
				LOG_ERR( 'Can not find channel' )
				return
	
		dialog.SetChannel( channel )			

		dialog.doModal( )

		if dialog.IsOK( ) == E_DIALOG_STATE_ERROR :
			if dialog.GetConflictTimer( ) == None :
				infoDialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				infoDialog.SetDialogProperty( MR_LANG( 'Error' ), dialog.GetErrorMessage( ) )
				infoDialog.doModal( )
			else :
				from pvr.GuiHelper import RecordConflict
				RecordConflict( dialog.GetConflictTimer( ) )
			return

		#self.StopEPGUpdateTimer( )
		self.UpdateListUpdateOnly( )
		#self.StartEPGUpdateTimer( E_SHORT_UPDATE_TIME )


	def ShowDeleteConfirm( self ) :
		LOG_TRACE( 'ShowDeleteConfirm' )

		timer = None
		
		epg = self.GetSelectedEPG( )

		if epg :
			timer = self.GetTimerByEPG( epg )

		else :
			if self.mEPGMode == E_VIEW_CURRENT or self.mEPGMode == E_VIEW_FOLLOWING :				
				selectedPos = self.mCtrlBigList.getSelectedPosition( )
				if selectedPos >= 0 and self.mChannelList and selectedPos < len( self.mChannelList ) :
					channel = self.mChannelList[ selectedPos ]
					timer = self.GetTimerByChannel( channel )					

			elif self.mEPGMode == E_VIEW_CHANNEL :
				timer = self.GetTimerByChannel( self.mCurrentChannel )

		if timer :		
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Delete Timer' ), MR_LANG( 'Do you want to remove the timer?' ) )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.mDataCache.Timer_DeleteTimer( timer.mTimerId )
				#self.StopEPGUpdateTimer( )
				self.UpdateListUpdateOnly( )
				#self.StartEPGUpdateTimer( E_SHORT_UPDATE_TIME )


	def ShowDeleteAllConfirm( self ) :
		LOG_TRACE( 'ShowDeleteConfirm' )
		if self.mTimerList == None or len(self.mTimerList) <= 0 :
			LOG_WARN( 'Has no Timer' )
			return

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( MR_LANG( 'WARNING' ), MR_LANG( 'DO YOU WANT TO REMOVE ALL YOUR TIMERS?' ) )
		dialog.doModal( )

		self.OpenBusyDialog( )
		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			for timer in self.mTimerList:
				#timer.printdebug()
				self.mDataCache.Timer_DeleteTimer( timer.mTimerId )

			#self.StopEPGUpdateTimer( )
			self.UpdateListUpdateOnly( )
			#self.StartEPGUpdateTimer( E_SHORT_UPDATE_TIME )

		self.CloseBusyDialog( )


	def ShowAllTimers( self ) :
		LOG_TRACE( 'ShowAllTimers' )
		self.mEventBus.Deregister( self )	
		self.StopEPGUpdateTimer( )
		WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMER_WINDOW )
	

	def ShowSearchDialog( self ) :
		try :
			kb = xbmc.Keyboard( '', MR_LANG( 'Enter search keywords here' ), False )			
			kb.doModal( )
			if kb.isConfirmed( ) :
				keyword = kb.getText( )
				LOG_TRACE( 'keyword len=%d' %len( keyword ) )
				if len( keyword ) < MININUM_KEYWORD_SIZE :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'A search keyword must be at least %d characters long' ) % MININUM_KEYWORD_SIZE )
					dialog.doModal( )
					return
					
				searchList = []
				indexList = []
				count = len( self.mListItems )
				
				for i in range( count ) :
					listItem = self.mListItems[ i ]

					label1 = listItem.getLabel( )
					label2 = listItem.getLabel2( )
					
					if label2.lower( ).find( keyword.lower( ) ) >= 0 or label1.lower( ).find( keyword.lower( ) ) >= 0 :
						searchList.append( '%s : %s' %( label1, label2 ) )
						indexList.append( i )

				LOG_TRACE( 'Result =%d' %len( searchList ) )

				if len( searchList ) <= 0 :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Search Result' ), MR_LANG( 'No matched result found' ) )
					dialog.doModal( )
		 			return
		 		else :
					dialog = xbmcgui.Dialog( )
		 			select = dialog.select( 'Select Event', searchList )

					if select >= 0 and select < len( searchList ) :
						LOG_TRACE( 'selectIndex=%d' %indexList[ select ] )
						LOG_TRACE( 'selectName=%s' %searchList[ select ] )
						if self.mEPGMode == E_VIEW_CHANNEL :
							self.mCtrlList.selectItem( indexList[ select ] )
						else:
							self.mCtrlBigList.selectItem( indexList[ select ] )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def ShowDetailInfomation( self ) :
		LOG_TRACE( 'ShowDetailInfomation' )

		epg = self.GetSelectedEPG( )

		if epg :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_EXTEND_EPG )
			dialog.SetEPG( epg )
			dialog.doModal( )


	def ShowSelectChannel( self ) :
	
		dialog = xbmcgui.Dialog( )
		channelNameList = []
		for channel in self.mChannelList :
			channelNameList.append( '%04d %s' %( channel.mNumber, channel.mName ) )

		ret = dialog.select( MR_LANG( 'Select Channel' ), channelNameList, False, StringToListIndex( channelNameList, '%04d %s' % ( self.mSelectChannel.mNumber, self.mSelectChannel.mName ) ) )

		if ret >= 0 :
			self.mSelectChannel = self.mChannelList[ ret ]

			"""
			self.mEventBus.Deregister( self )
			self.StopEPGUpdateTimer( )
			"""
			self.UpdateAllEPGList( )

			"""
			self.mEventBus.Register( self )
			self.StartEPGUpdateTimer( )
			"""


	def	GetSelectedEPG( self ) :
		selectedEPG = None
		selectedPos = -1

		self.mLock.acquire( )
		if self.mEPGMode == E_VIEW_CHANNEL :
			selectedPos = self.mCtrlList.getSelectedPosition( )
			if self.mEPGList == None:
				LOG_WARN( 'Has no epglist' )
			if self.mEPGList and selectedPos >= 0 and self.mEPGList  and selectedPos < len( self.mEPGList ) :
				selectedEPG = self.mEPGList[ selectedPos ]

		else :
			selectedPos = self.mCtrlBigList.getSelectedPosition( )
			if selectedPos >= 0 and self.mChannelList and selectedPos < len( self.mChannelList ) :
				channel = self.mChannelList[ selectedPos ]
				selectedEPG = self.GetEPGByIds( channel.mSid, channel.mTsid, channel.mOnid )

		self.mLock.release( )
		
		return selectedEPG


	def LoadTimerList( self ) :
		self.mTimerList = []
		LOG_TRACE( '' )

		try :
			self.mTimerList = self.mDataCache.Timer_GetTimerList( )
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		if self.mTimerList :
			LOG_TRACE( 'self.mTimerList len=%d' %len( self.mTimerList ) )


	def GetTimerByChannel( self, aChannel ) :

		if self.mTimerList == None :
			return None

		try :		
			if E_USE_FIXED_INTERVAL == True :
				startTime = self.mDataCache.Datetime_GetLocalTime( )
				endTime = self.mDataCache.Datetime_GetLocalTime( ) + 3600*24

				for i in range( len( self.mTimerList ) ) :
					timer =  self.mTimerList[i]
					if aChannel.mSid == timer.mSid and aChannel.mTsid == timer.mTsid and aChannel.mOnid == timer.mOnid :
						if timer.mTimerType == ElisEnum.E_ITIMER_WEEKLY	:
							if self.HasMachedWeeklyTimer( timer, startTime, endTime ) == True :
								return timer
						elif self.HasOverlapped( startTime, endTime, timer.mStartTime, timer.mStartTime + timer.mDuration ) == True :
							return timer
			else :
				for i in range( len( self.mTimerList ) ) :
					timer =  self.mTimerList[i]
					if aChannel.mSid == timer.mSid and aChannel.mTsid == timer.mTsid and aChannel.mOnid == timer.mOnid :
						return timer

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		return None


	def GetTimerByEPG( self, aEPG ) :
		if self.mTimerList == None :
			return None

		try :	
			for i in range( len( self.mTimerList ) ) :
				timer =  self.mTimerList[i]
				startTime = aEPG.mStartTime +  self.mLocalOffset 
				endTime = startTime + aEPG.mDuration

				""" Debug 
				LOG_TRACE('timerType=%d' %timer.mTimerType )
				LOG_TRACE('id=%d:%d %d:%d %d:%d' %(aEPG.mSid, timer.mSid, aEPG.mTsid, timer.mTsid, aEPG.mOnid, timer.mOnid) )
				LOG_TRACE('EPG Start Time = %s' % TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
				LOG_TRACE('Timer Start Time = %s' % TimeToString( timer.mStartTime , TimeFormatEnum.E_HH_MM ) )			
				LOG_TRACE('Start Time = %x:%x' % (startTime, timer.mStartTime )	)

				LOG_TRACE('EPG End Time = %s' % TimeToString( endTime, TimeFormatEnum.E_HH_MM ) )
				LOG_TRACE('Timer End Time = %s' % TimeToString( timer.mStartTime + timer.mDuration , TimeFormatEnum.E_HH_MM ) )
				LOG_TRACE('End Time = %x:%x' % (endTime, timer.mStartTime + timer.mDuration )	)

				LOG_TRACE(' timer.mFromEPG = %d  aEPG.mEventId=%d timer.mEventId=%d timer.mTimerId=%d' % (timer.mFromEPG, aEPG.mEventId, timer.mEventId, timer.mTimerId ) )
				"""				

				if timer.mTimerType == ElisEnum.E_ITIMER_WEEKLY and timer.mWeeklyTimer and timer.mWeeklyTimerCount > 0 :
					if aEPG.mSid == timer.mSid and aEPG.mTsid == timer.mTsid and aEPG.mOnid == timer.mOnid :
						if self.HasMachedWeeklyTimer( timer, startTime, endTime ) == True :
							return timer
						
				else :
					if timer.mFromEPG :
						if  timer.mEventId > 0  and ( aEPG.mEventId == timer.mEventId ) and ( aEPG.mSid == timer.mSid ) and ( aEPG.mTsid  == timer.mTsid ) and ( aEPG.mOnid == timer.mOnid ) :
							LOG_TRACE( '------------------- find by event id -------------------------' )
							return timer

					else :
						if aEPG.mSid == timer.mSid and aEPG.mTsid == timer.mTsid and aEPG.mOnid == timer.mOnid :
							if self.HasOverlapped( startTime, endTime, timer.mStartTime, timer.mStartTime + timer.mDuration ) == True :
								LOG_TRACE( '------------------- find by manual timer-------------------------' )
								return timer
						
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		return None


	def HasOverlapped( self, aStartTime, aEndTime, aStartTime2, aEndTime2 ) :
		if ( aStartTime >= aStartTime2 and aStartTime < aEndTime2 ) or \
			( aEndTime >= aStartTime2 and aEndTime < aEndTime2 )  or \
			( aStartTime >= aStartTime2 and aEndTime < aEndTime2 ) or \
			( aStartTime2 >= aStartTime and aEndTime2 < aEndTime ) :
			return True

		return False


	def HasMachedWeeklyTimer( self, aTimer, aStartTime, aEndTime ) :
		struct_time = time.gmtime( aTimer.mStartTime )
		# tm_wday is different between Python and C++
		weekday = struct_time[6] + 1
		if weekday > 6 :
			weekday = 0
			
		# hour*3600 + min*60 + sec
		secondsNow = struct_time[3]*3600 + struct_time[4]*60 + struct_time[5]

		#LOG_TRACE('weekday=%d'  %weekday )

		for weeklyTimer in aTimer.mWeeklyTimer :
			dateLeft = weeklyTimer.mDate - weekday
			if dateLeft < 0 :
				dateLeft += 7
			elif dateLeft == 0 :
				if weeklyTimer.mStartTime < secondsNow :
					dateLeft += 7

			weeklyStartTime = dateLeft*24*3600 + aTimer.mStartTime + weeklyTimer.mStartTime - secondsNow

			if self.HasOverlapped( aStartTime, aEndTime, weeklyStartTime, weeklyStartTime + weeklyTimer.mDuration ) == True :
				LOG_TRACE( '------------------- find by weekly timer -------------------------' )
				return True

		return False
	

	def IsRunningTimer( self, aTimer ) :
		if aTimer == None :
			return False

		runningTimers = self.mDataCache.Timer_GetRunningTimers( )
		if runningTimers == None :
			return False
			
		for timer in runningTimers :
			if timer.mTimerId == aTimer.mTimerId :
				return True

		return False
			

	def Tune( self ) :
		if self.mEPGMode == E_VIEW_CHANNEL :
			#LOG_TRACE( '##################################### channel %d:%d' %(self.mSelectChannel.mNumber, self.mCurrentChannel.mNumber) )	
			if self.mSelectChannel == None or self.mCurrentChannel == None :
				LOG_ERR( 'Invalid channel' )
				return

			if self.mSelectChannel.mNumber != self.mCurrentChannel.mNumber :
				if self.mSelectChannel.mLocked == True :
					if self.ShowPincodeDialog( ) == False :
						return

				else :
					if self.mDataCache.Get_Player_AVBlank( ) :
						self.mDataCache.Player_AVBlank( False )

				self.mDataCache.Channel_SetCurrent( self.mSelectChannel.mNumber, self.mSelectChannel.mServiceType )
				self.mCurrentChannel = self.mSelectChannel
				self.UpdateCurrentChannel( )				

			"""
			channel = self.mDataCache.Channel_GetCurrent( )
			if channel.mLocked == True :
				if self.ShowPincodeDialog( ) == False :
					return
			self.mDataCache.Channel_SetCurrent( channel.mNumber, channel.mServiceType ) 
			self.RestartEPGUpdateTimer( 5 )
			"""

		else : #self.mEPGMode == E_VIEW_CURRENT  or self.mEPGMode == E_VIEW_FOLLOWING
			selectedPos = self.mCtrlBigList.getSelectedPosition( )
			if selectedPos >= 0 and self.mChannelList and selectedPos < len( self.mChannelList ) :
				LOG_TRACE( '' )
				channel = self.mChannelList[ selectedPos ]
				if channel.mLocked == True :				
					if self.ShowPincodeDialog( ) == False :
						return

				else :
					if self.mDataCache.Get_Player_AVBlank( ) :
						self.mDataCache.Player_AVBlank( False )


				self.StopEPGUpdateTimer( )					
				self.mDataCache.Channel_SetCurrent( channel.mNumber, channel.mServiceType )
				self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
				self.UpdateCurrentChannel( )
				#self.StartEPGUpdateTimer( E_SHORT_UPDATE_TIME )


	def RestartEPGUpdateTimer( self, aTimeout=E_NOMAL_UPDATE_TIME ) :
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Restart' )
		self.StopEPGUpdateTimer( )
		self.StartEPGUpdateTimer( aTimeout )


	def StartEPGUpdateTimer( self, aTimeout=E_NOMAL_UPDATE_TIME ) :
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Start' )	
		self.mEPGUpdateTimer = threading.Timer( aTimeout, self.AsyncEPGUpdateTimer )
		self.mEPGUpdateTimer.start( )
	

	def StopEPGUpdateTimer( self ) :
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Stop' )	
		if self.mEPGUpdateTimer and self.mEPGUpdateTimer.isAlive( ) :
			self.mEPGUpdateTimer.cancel( )
			del self.mEPGUpdateTimer
			
		self.mEPGUpdateTimer = None


	def AsyncEPGUpdateTimer( self ) :	
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Async' )	
		if self.mEPGUpdateTimer == None :
			LOG_WARN( 'EPG update timer expired' )
			return

		self.Load( )

		self.UpdateListUpdateOnly( )
		self.UpdateEPGInfomation( )

		self.RestartEPGUpdateTimer( )


	def ToggleTVRadio( self ) :
		if self.mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
			self.mServiceType = ElisEnum.E_SERVICE_TYPE_RADIO
		else :
			self.mServiceType = ElisEnum.E_SERVICE_TYPE_TV

		self.mChannelList = self.mDataCache.Channel_GetAllChannels( self.mServiceType )

		if self.mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
			lastChannelNumber = ElisPropertyInt( 'Last TV Number', self.mCommander ).GetProp( )
		else :
			lastChannelNumber = ElisPropertyInt( 'Last Radio Number', self.mCommander ).GetProp( )

		self.mCurrentChannel = None
		if lastChannelNumber < len( self.mChannelList ) :
			channelIndex = lastChannelNumber - 1
			if channelIndex >= 0:
				self.mCurrentChannel = self.mChannelList[ channelIndex ]

		LOG_ERR( 'TOGGLE TVRADIO' )
		self.mCurrentChannel.printdebug()
		self.mSelectChannel = self.mCurrentChannel			

		self.UpdateAllEPGList( )


	def RecordByHotKey( self ) :
		selectedEPG = self.GetSelectedEPG( )

		timer = None

		if selectedEPG :
			timer = self.GetTimerByEPG( selectedEPG )
			if timer :
				timer.printdebug( )
			if timer and timer.mTimerId > 0 :	# Edit Mode
				self.ShowManualTimer( selectedEPG, timer )
			else: # Add EPG Timer
				self.ShowEPGTimer( selectedEPG )

		else :
			if self.mEPGMode == E_VIEW_CURRENT or self.mEPGMode == E_VIEW_FOLLOWING :
				selectedPos = self.mCtrlBigList.getSelectedPosition( )
				if selectedPos >= 0 and self.mChannelList and selectedPos < len( self.mChannelList ) :
					channel = self.mChannelList[ selectedPos ]
					timer = self.GetTimerByChannel( channel )					

			if timer :
				timer.printdebug( )
			
			if timer and timer.mTimerId > 0 :	# Edit Mode
				self.ShowManualTimer( None, timer )				
			else :	# Add Manual Timer
				self.ShowManualTimer( None )


	def	StopByHotKey( self ) :
		self.ShowDeleteConfirm( )	


	def ShowPincodeDialog( self ) :
		self.mEventBus.Deregister( self )

		if not self.mDataCache.Get_Player_AVBlank( ) :
			self.mDataCache.Player_AVBlank( True )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_INPUT_PINCODE )
		dialog.SetTitleLabel( MR_LANG( 'Enter your PIN code' ) )
		dialog.doModal( )

		ret = False
		
		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			if self.mDataCache.Get_Player_AVBlank( ) :
				self.mDataCache.Player_AVBlank( False )

			ret = True

		self.mEventBus.Register( self )
		
		return ret


	def SelectNextChannel( self ) :
		if self.mEPGMode != E_VIEW_CHANNEL :
			return

		LOG_TRACE( 'Select Channel Number=%d' %self.mSelectChannel.mNumber )

		if self.mChannelList == None :
			return

		count = len( self.mChannelList )

		if count <= 0 :
			return

		index = self.mSelectChannel.mNumber

		LOG_TRACE( 'Select Channel count=%d' %count )
		
		if index < 0 or index >= count : 
			index = 0

		LOG_TRACE( 'Select Channel index=%d' %index )
		
		self.mEventBus.Deregister( self )
		self.StopEPGUpdateTimer( )

		try :			
			nextChannel = self.mChannelList[ index ]
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )
			nextChannel = self.mChannelList[ 0 ]
			
		if nextChannel :
			self.mSelectChannel = nextChannel
			LOG_TRACE( 'Select Channel Number=%d' %self.mSelectChannel.mNumber )
			self.UpdateAllEPGList( )
		else: 
			LOG_ERR( 'can not find next channel' )

		self.mEventBus.Register( self )
		self.StartEPGUpdateTimer( 3 )


	def SelectPrevChannel( self ) :
		if self.mEPGMode != E_VIEW_CHANNEL :
			return

		LOG_TRACE( 'Select Channel Number=%d' %self.mSelectChannel.mNumber )

		if self.mChannelList == None :
			return

		count = len( self.mChannelList )

		if count <= 0 :
			return

		index = self.mSelectChannel.mNumber - 2

		LOG_TRACE( 'Select Channel count=%d' %count )
		
		if index < 0 or index >= count : 
			index = 0

		LOG_TRACE( 'Select Channel index=%d' %index )
		
		self.mEventBus.Deregister( self )
		self.StopEPGUpdateTimer( )

		try :			
			nextChannel = self.mChannelList[ index ]
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )
			nextChannel = self.mChannelList[ 0 ]
			
		if nextChannel :
			self.mSelectChannel = nextChannel
			LOG_TRACE( 'Select Channel Number=%d' %self.mSelectChannel.mNumber )
			self.UpdateAllEPGList( )
		else: 
			LOG_ERR( 'can not find next channel' )

		self.mEventBus.Register( self )
		self.StartEPGUpdateTimer( 3 )


	def UpdateAllEPGList( self ) :
		self.Load( )
		self.UpdateList( )
		self.UpdateSelectedChannel( )			
		self.FocusCurrentChannel( )
		time.sleep( 0.2 )
		self.UpdateEPGInfomation( )


	def CalculateProgress( self, aCurrentTime, aEpgStart, aDuration  ) :
		startTime = aEpgStart
		endTime = aEpgStart + aDuration
		
		pastDuration = endTime - aCurrentTime

		if aCurrentTime > endTime : #past
			return 100

		elif aCurrentTime < startTime : #future
			return 0

		if pastDuration < 0 : #past
			pastDuration = 0

		if aDuration > 0 :
			percent = 100 - ( pastDuration * 100.0 / aDuration )
		else :
			percent = 0

		LOG_TRACE( 'Percent=%d' %percent )
		return percent

	
