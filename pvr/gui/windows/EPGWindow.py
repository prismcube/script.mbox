from pvr.gui.WindowImport import *
import pvr.HiddenTestMgr as TestMgr


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

LABEL_ID_TEST					= 450

E_VIEW_CHANNEL					= 0
E_VIEW_CURRENT					= 1
E_VIEW_FOLLOWING				= 2
E_VIEW_END						= 3

E_NOMAL_UPDATE_TIME				= 30
E_SHORT_UPDATE_TIME				= 10

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


class EPGWindow( BaseWindow ) :

	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mLock = thread.allocate_lock()		

	
	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.SetPipScreen( )

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( 'EPG' )

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

		#test
		self.mCtrlTestLabel = self.getControl( LABEL_ID_TEST )

		self.ResetEPGInfomation( )
		self.UpdateViewMode( )
		self.InitControl()
		self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( )
		self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
		LOG_TRACE('ZeppingMode(%d,%d,%d)' %( self.mCurrentMode.mServiceType, self.mCurrentMode.mMode, self.mCurrentMode.mSortingMode ) )
		self.mChannelList = self.mDataCache.Channel_GetList( )

		if self.mChannelList == None :
			LOG_WARN('No Channel List')
		else:
			LOG_TRACE("ChannelList=%d" %len(self.mChannelList) )
		
		self.mSelectChannel = self.mCurrentChannel
		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		self.mGMTTime = 0
		LOG_TRACE('CHANNEL current=%s select=%s' %( self.mCurrentChannel, self.mSelectChannel ))

		self.Load( )
		self.UpdateList( )
		self.UpdateCurrentChannel( )
		self.UpdateSelectedChannel( )
		self.FocusCurrentChannel( )		
		self.UpdateEPGInfomation( )


		self.mUpdateLocked = False
		self.mIsUpdateEnable = True

		self.mEventBus.Register( self )

		self.StartEPGUpdateTimer( )
		
		self.mInitialized = True


	def onAction( self, aAction ) :
		self.GetFocusId()
		actionId = aAction.getId( )
		self.GlobalAction( actionId )

		
		#LOG_TRACE('onAction=%d' %actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.Close( )

		elif  actionId == Action.ACTION_SELECT_ITEM :
			if self.mFocusId == LIST_ID_COMMON_EPG or self.mFocusId == LIST_ID_BIG_EPG :
				self.Tune( )
	
		elif actionId == Action.ACTION_PARENT_DIR :
			self.Close( )
			
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
			self.ShowContextMenu( )


	def onClick( self, aControlId ) :
		LOG_TRACE( 'aControlId=%d' %aControlId )

		if aControlId == BUTTON_ID_EPG_MODE :
			self.mLock.acquire( )
			self.mUpdateLocked = True
			self.mLock.release( )

			self.mEPGMode += 1
			if self.mEPGMode >= E_VIEW_END :
				self.mEPGMode = 0 

			self.mSelectChannel = self.mCurrentChannel

			SetSetting( 'EPG_MODE','%d' %self.mEPGMode )

			self.mEventBus.Deregister( self )
			self.StopEPGUpdateTimer( )

			self.UpdateViewMode( )
			self.InitControl( )
			self.Load( )
			
			self.UpdateListWithGUILock( )
			self.UpdateList( )	
			self.UpdateSelectedChannel( )
			self.FocusCurrentChannel( )			
			self.UpdateEPGInfomation()

			self.mLock.acquire( )
			self.mUpdateLocked = False
			self.mLock.release( )

			self.mEventBus.Register( self )
			self.StartEPGUpdateTimer( )
			
		
		elif aControlId == RADIIOBUTTON_ID_EXTRA :
			pass

		elif aControlId == LIST_ID_COMMON_EPG :
			pass


	def onFocus( self, aControlId ) :
		pass
		"""
		if self.mInitialized == False :
			return
		"""

	@GuiLock
	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			if aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
				if self.mIsUpdateEnable == True	:
					self.StopEPGUpdateTimer( )
					self.UpdateListWithGUILock( )
					self.StartEPGUpdateTimer( E_SHORT_UPDATE_TIME )

			"""
			elif aEvent.getName( ) == ElisEventCurrentEITReceived.getName( ) :
				self.DoCurrentEITReceived( aEvent )
			"""


	def Close( self ) :
		TestMgr.GetInstance( ).CheckAndStopTest( )
		self.mEventBus.Deregister( self )	

		self.StopEPGUpdateTimer( )
		self.SetVideoRestore( )
		WinMgr.GetInstance().CloseWindow( )


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
		self.mEPGListHash = {}


	def Load( self ) :

		LOG_TRACE('----------------------------------->')
		self.mDebugStart = time.time( )
		
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
			
		self.mDebugEnd = time.time( )
		print 'epg loading test time =%s' %( self.mDebugEnd  - self.mDebugStart )


	def LoadByChannel( self ) :
		gmtFrom =  self.mGMTTime 
		gmtUntil = self.mGMTTime + E_MAX_SCHEDULE_DAYS*3600*24

		LOG_ERR('START : localoffset=%d' %self.mLocalOffset )
		LOG_ERR('START : %s' % TimeToString( gmtFrom+self.mLocalOffset, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
		LOG_ERR('START : %d : %d %d' % ( self.mSelectChannel.mSid,  self.mSelectChannel.mTsid,  self.mSelectChannel.mOnid) )

		
		try :
			#self.mEPGList = self.mDataCache.Epgevent_GetListByChannel(  self.mSelectChannel.mSid,  self.mSelectChannel.mTsid,  self.mSelectChannel.mOnid,  gmtFrom,  gmtUntil,  E_MAX_EPG_COUNT)
			self.mEPGList = self.mDataCache.Epgevent_GetListByChannelFromEpgCF(  self.mSelectChannel.mSid,  self.mSelectChannel.mTsid,  self.mSelectChannel.mOnid )

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)

		if self.mEPGList == None or self.mEPGList[0].mError != 0 :
			self.mEPGList = None
			return

		if self.mEPGList == None or len ( self.mEPGList ) <= 0 :
			return

		LOG_ERR('self.mEPGList COUNT=%d' %len(self.mEPGList ))

		for epg in self.mEPGList :
			self.mEPGListHash[ '%d:%d:%d' %( epg.mSid, epg.mTsid, epg.mOnid) ] = epg


	def LoadByCurrent( self ) :
	
		try :
			#self.mEPGList=self.mDataCache.Epgevent_GetCurrentList()
			self.mEPGList = self.mDataCache.Epgevent_GetCurrentListByEpgCF( )

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)

		if self.mEPGList == None or len ( self.mEPGList ) <= 0 :
			return

		LOG_TRACE('self.mEPGList COUNT=%d' %len(self.mEPGList ))
		
		for epg in self.mEPGList :
			self.mEPGListHash[ '%d:%d:%d' %( epg.mSid, epg.mTsid, epg.mOnid) ] = epg


	def LoadByFollowing( self ) :		
		try :
			#self.mEPGList=self.mDataCache.Epgevent_GetFollowingList()
			self.mEPGList = self.mDataCache.Epgevent_GetFollowingListByEpgCF( )

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)

		if self.mEPGList == None or len ( self.mEPGList ) <= 0 :
			return

		LOG_TRACE('self.mEPGList COUNT=%d' %len(self.mEPGList ))
		
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
	
		if self.mSelectChannel :
			self.mCtrlEPGChannelLabel.setLabel( '%04d %s' %( self.mSelectChannel.mNumber, self.mSelectChannel.mName ) )
		else:
			self.mCtrlEPGChannelLabel.setLabel( 'No Channel' )


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
				self.mCtrlDurationLabel.setLabel( '%dMin' % ( epg.mDuration / 60 ) )

				#self.mCtrlTestLabel.setLabel('eid[%s] sid[%s] tsid[%s] onid[%s]'% (epg.mEventId, epg.mSid, epg.mTsid, epg.mOnid) )

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
			LOG_ERR( "Exception %s" %ex)


	def	ResetEPGInfomation( self ) :
		self.mCtrlTimeLabel.setLabel('')
		self.mCtrlDateLabel.setLabel('')
		self.mCtrlDurationLabel.setLabel('')
		self.mCtrlEPGDescription.setText( '' )
		
		self.mWin.setProperty( 'HasSubtitle', 'False' )
		self.mWin.setProperty( 'HasDolby', 'False' )
		self.mWin.setProperty( 'HasHD', 'False' )


	def UpdateListWithGUILock( self ) :
		if self.mUpdateLocked == True :
			return

		self.mIsUpdateEnable = False
		self.UpdateList( True )
		self.mIsUpdateEnable = True

	def UpdateList( self, aUpdateOnly=False ) :
		if aUpdateOnly == False :
			self.mListItems = []
		self.LoadTimerList( )

		if self.mEPGMode == E_VIEW_CHANNEL :
			if self.mEPGList == None :
				self.mCtrlList.reset()
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
					#self.setFocusId( LIST_ID_COMMON_EPG )
				else :
					xbmc.executebuiltin('container.update')
					#xbmc.executebuiltin('xbmc.Container.SetViewMode(%d)' %E_VIEW_CHANNEL)
				
			except Exception, ex :
				LOG_ERR( "Exception %s" %ex)

		elif self.mEPGMode == E_VIEW_CURRENT :
			self.mDebugStart = time.time( )		
			if self.mChannelList == None :
				self.mCtrlBigList.reset()			
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

						listItem.setProperty( 'StartTime', '' )
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
				#self.setFocusId( LIST_ID_BIG_EPG )
			else :
				xbmc.executebuiltin('container.update')			
				#xbmc.executebuiltin('xbmc.Container.SetViewMode(%d)' %E_VIEW_CURRENT)

			self.mDebugEnd = time.time( )
			print 'epg loading test =%s' %( self.mDebugEnd  - self.mDebugStart )
				

		elif self.mEPGMode == E_VIEW_FOLLOWING :
			if self.mChannelList == None :
				self.mCtrlBigList.reset()
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
						listItem.setProperty( 'StartTime', '' )
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
				#self.setFocusId( LIST_ID_BIG_EPG )
			else :
				xbmc.executebuiltin('container.update')			
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
	def CurrentTimeThread(self):
		pass


	@GuiLock
	def UpdateLocalTime( self ) :
		pass


	def ShowContextMenu( self ) :
		GuiLock2( True )
		context = []
		
		selectedEPG = self.GetSelectedEPG( )

		if self.mEPGMode == E_VIEW_CHANNEL :
			context.append( ContextItem( 'Select Channel', CONTEXT_SELECT_CHANNEL ) )

		if selectedEPG :
			if selectedEPG.mHasTimer :
				context.append( ContextItem( 'Edit Timer', CONTEXT_EDIT_TIMER ) )
				context.append( ContextItem( 'Delete Timer', CONTEXT_DELETE_TIMER ) )
			else :
				timerId = self.GetTimerByEPG( selectedEPG )
				if timerId > 0 :
					context.append( ContextItem( 'Edit Timer', CONTEXT_EDIT_TIMER ) )
					context.append( ContextItem( 'Delete Timer', CONTEXT_DELETE_TIMER ) )
				else:
					context.append( ContextItem( 'Add Timer', CONTEXT_ADD_EPG_TIMER ) )
					context.append( ContextItem( 'Add Manual Timer', CONTEXT_ADD_MANUAL_TIMER ) )

			if 	self.mTimerList and len( self.mTimerList ) > 0 :
				context.append( ContextItem( 'Delete All Timers', CONTEXT_DELETE_ALL_TIMERS ) )
				context.append( ContextItem( 'Show All Timers', CONTEXT_SHOW_ALL_TIMERS ) )
				

			context.append( ContextItem( 'Search', CONTEXT_SEARCH ) )					
			context.append( ContextItem( 'Extend Infomation', CONTEXT_EXTEND_INFOMATION ) )		
			

		else :
			timerId = 0

			if self.mEPGMode == E_VIEW_CURRENT or self.mEPGMode == E_VIEW_FOLLOWING :				
				selectedPos = self.mCtrlBigList.getSelectedPosition()
				if selectedPos >= 0 and selectedPos < len( self.mChannelList ) :
					channel = self.mChannelList[ selectedPos ]
					timerId = self.GetTimerByChannel( channel )					

			if timerId > 0 :
				context.append( ContextItem( 'Edit Timer', CONTEXT_EDIT_TIMER ) )
				context.append( ContextItem( 'Delete Timer', CONTEXT_DELETE_TIMER ) )
			else :
				context.append( ContextItem( 'Add Manual Timer', CONTEXT_ADD_MANUAL_TIMER ) )

			if 	self.mTimerList and len( self.mTimerList ) > 0 :
				context.append( ContextItem( 'Delete All Timers', CONTEXT_DELETE_ALL_TIMERS ) )	
				context.append( ContextItem( 'Show All Timers', CONTEXT_SHOW_ALL_TIMERS ) )				

			context.append( ContextItem( 'Search', CONTEXT_SEARCH ) )

		dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
		dialog.doModal( )

		contextAction = dialog.GetSelectedAction()
		self.DoContextAction( contextAction ) 
		GuiLock2( False )


	def DoContextAction( self, aContextAction ) :
		LOG_TRACE('aContextAction=%d' %aContextAction )

		if aContextAction == CONTEXT_ADD_EPG_TIMER :
			epg = self.GetSelectedEPG( )
			if epg :
				self.ShowEPGTimer( epg )

		elif aContextAction == CONTEXT_ADD_MANUAL_TIMER :
			epg = self.GetSelectedEPG( )
			self.ShowManualTimer( epg )

		elif aContextAction == CONTEXT_EDIT_TIMER :
			pass
			"""
			#ToDO
			epg = self.GetSelectedEPG( )		
			self.ShowManualTimer( epg, True )		
			"""

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
		LOG_TRACE('ShowEPGTimer')
		dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_ADD_TIMER )
		dialog.SetEPG( aEPG )
		dialog.doModal( )

		try :
			if dialog.IsOK() == E_DIALOG_STATE_YES :
				LOG_TRACE('')
				ret = self.mDataCache.Timer_AddEPGTimer( 0, 0, aEPG )

				if ret[0].mParam == -1 or ret[0].mError == -1 :
					self.RecordConflict( ret )
				else :
					self.StopEPGUpdateTimer( )
					self.UpdateListWithGUILock( )
					self.StartEPGUpdateTimer( E_SHORT_UPDATE_TIME )

			else :
				LOG_TRACE('')

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)


	def ShowManualTimer( self, aEPG, aIsEdit=False ) :
		if aEPG :
			LOG_TRACE('ShowManualTimer EPG=%d IsEdit=%d' %( aEPG.mEventId, aIsEdit) )
		else :
			LOG_TRACE('ShowManualTimer EPG=None IsEdit=%d' %aIsEdit )

		dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_ADD_MANUAL_TIMER )

		if aIsEdit :
			dialog.SetEditMode( True )		
			timerId = self.GetTimerByEPG( aEPG )		
			dialolg.SetTimer( timerId )
			
			if timerId < 0 :
				LOG_ERR('Can not find Timer')
				return

		else :
			dialog.SetEditMode( False )

			if aEPG :
				dialog.SetEPG( aEPG )

			channel = None
			if self.mEPGMode == E_VIEW_CHANNEL  :
				channel = self.mDataCache.Channel_GetCurrent( )
			else :
				selectedPos = self.mCtrlBigList.getSelectedPosition()
				if selectedPos >= 0 and selectedPos < len( self.mChannelList ) :
					channel = self.mChannelList[ selectedPos ]
				else :
					LOG_ERR('Can not find channel')
					return
		
			dialog.SetChannel( channel )			

		dialog.doModal( )

		if dialog.IsOK( ) == E_DIALOG_STATE_ERROR :
			if dialog.GetConflictTimer( ) == None :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'Error', dialog.GetErrorMessage( ) )
				dialog.doModal( )
			else :
				self.RecordConflict( dialog.GetConflictTimer( ) )
			return

		self.StopEPGUpdateTimer( )
		self.UpdateListWithGUILock( )
		self.StartEPGUpdateTimer( E_SHORT_UPDATE_TIME )



	def ShowDeleteConfirm( self ) :
		LOG_TRACE('ShowDeleteConfirm')

		timerId = 0
		
		epg = self.GetSelectedEPG( )

		if epg :
			timerId = self.GetTimerByEPG( epg )

		else :
			if self.mEPGMode == E_VIEW_CURRENT or self.mEPGMode == E_VIEW_FOLLOWING :				
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
				self.StopEPGUpdateTimer( )
				self.UpdateListWithGUILock( )
				self.StartEPGUpdateTimer( E_SHORT_UPDATE_TIME )



	def ShowDeleteAllConfirm( self ) :
		LOG_TRACE('ShowDeleteConfirm')
		if self.mTimerList == None or len(self.mTimerList) <= 0 :
			LOG_WARN('Has no Timer')
			return

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( 'Confirm', 'Do you want to delete all timers?' )
		dialog.doModal( )

		self.OpenBusyDialog( )
		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			for timer in self.mTimerList:
				#timer.printdebug()
				self.mDataCache.Timer_DeleteTimer( timer.mTimerId )

			self.StopEPGUpdateTimer( )
			self.UpdateListWithGUILock( )
			self.StartEPGUpdateTimer( E_SHORT_UPDATE_TIME )

		self.CloseBusyDialog( )


	def ShowAllTimers( self ) :
		LOG_TRACE('ShowAllTimers')
		WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMER_WINDOW )
	

	def ShowSearchDialog( self ) :
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

					label1 = listItem.getLabel( )
					label2 = listItem.getLabel2( )
					
					if label2.lower().find( keyword.lower() ) >= 0 or label1.lower().find( keyword.lower() ) >= 0:
						searchList.append( '%s : %s' %(label1,label2) )
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
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_EXTEND_EPG )
			dialog.SetEPG( epg )
			dialog.doModal( )


	def ShowSelectChannel( self ) :
		if self.mChannelList == None or len( self.mChannelList ) <= 0 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( 'Error', 'Has no channel' )
 			dialog.doModal( )
			return
	
		dialog = xbmcgui.Dialog( )
		channelNameList = []
		for channel in self.mChannelList :
			channelNameList.append( '%04d %s' %( channel.mNumber, channel.mName ) )

		ret = dialog.select( 'Select Channel', channelNameList )

		if ret >= 0 :
			self.mSelectChannel = self.mChannelList[ ret ]

			self.mEventBus.Deregister( self )
			self.StopEPGUpdateTimer( )
			
			self.Load( )
			self.UpdateList( )			
			self.UpdateListWithGUILock( )
			self.UpdateSelectedChannel( )
			self.FocusCurrentChannel( )			
			self.UpdateEPGInfomation()

			self.mEventBus.Register( self )
			self.StartEPGUpdateTimer( )


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


					struct_time = time.gmtime( timer.mStartTime )
					# tm_wday is different between Python and C++
					LOG_TRACE('time.struct_time[6]=%d' %struct_time[6] )
					if struct_time[6] == 6 : #tm_wday
						weekday = 0
					elif struct_time[6] == 0 :
						weekday = 6
					else  :
						weekday = struct_time[6] + 1

						
					# hour*3600 + min*60 + sec
					secondsNow = struct_time[3]*3600 + struct_time[4]*60 + struct_time[5]

					LOG_TRACE('weekday=%d'  %weekday )

					for weeklyTimer in timer.mWeeklyTimer :
						dateLeft = weeklyTimer.mDate - weekday
						if dateLeft < 0 :
							dateLeft += 7
						elif dateLeft == 0 :
							if weeklyTimer.mStartTime < secondsNow :
								dateLeft += 7

						weeklyStarTime = dateLeft*24*3600 + timer.mStartTime + weeklyTimer.mStartTime - secondsNow

						#LOG_TRACE('weeklyTimer date==%d time=%s duration=%d' %(weeklyTimer.mDate, TimeToString( weeklyStarTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ), weeklyTimer.mDuration ) )
						if ( aEPG.mSid == timer.mSid and aEPG.mTsid == timer.mTsid and aEPG.mOnid == timer.mOnid ) and \
							(( startTime >= weeklyStarTime and startTime < (weeklyStarTime + weeklyTimer.mDuration) ) or \
							( endTime > weeklyStarTime and endTime < (weeklyStarTime + weeklyTimer.mDuration) ) ) :
							LOG_TRACE('------------------- find by weekly timer -------------------------')
							return timer.mTimerId
								
				else :
					if timer.mFromEPG :
						if  timer.mEventId > 0  and aEPG.mEventId == timer.mEventId and aEPG.mSid == timer.mSid and aEPG.mTsid == timer.mTsid and aEPG.mOnid == timer.mOnid :
							LOG_TRACE('------------------- find by event id -------------------------')					
							return timer.mTimerId

					else :
						if ( aEPG.mSid == timer.mSid and aEPG.mTsid == timer.mTsid and aEPG.mOnid == timer.mOnid ) and \
							(( startTime >= timer.mStartTime and startTime < (timer.mStartTime + timer.mDuration) ) or \
							( endTime > timer.mStartTime and endTime < (timer.mStartTime + timer.mDuration) ) ) :
							LOG_TRACE('------------------- find by manual timer-------------------------')
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
		if self.mEPGMode == E_VIEW_CHANNEL :
			channel = self.mDataCache.Channel_GetCurrent( )
			self.mDataCache.Channel_SetCurrent( channel.mNumber, channel.mServiceType ) 
			self.RestartEPGUpdateTimer( 5 )			

		else : #self.mEPGMode == E_VIEW_CURRENT  or self.mEPGMode == E_VIEW_FOLLOWING
			selectedPos = self.mCtrlBigList.getSelectedPosition()		
			if selectedPos >= 0 and selectedPos < len( self.mChannelList ) :
				channel = self.mChannelList[ selectedPos ]
				LOG_TRACE('--------------- number=%d ----------------' %channel.mNumber )
				self.mDataCache.Channel_SetCurrent( channel.mNumber, channel.mServiceType )
				self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
				self.UpdateCurrentChannel( )
				self.RestartEPGUpdateTimer( 5 )


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
			LOG_WARN( 'EPG Update timer expired' )
			return


		if self.mUpdateLocked == False :	
			if self.mEPGMode == E_VIEW_FOLLOWING : # Following is not support until now.
				LOG_TRACE("ToDO : DocurrentEITReceived is not support until now.")
				self.RestartEPGUpdateTimer( )
			else :
				self.mLock.acquire( )
				self.Load( )
				self.mLock.release( )
				self.UpdateListWithGUILock( )
				self.UpdateEPGInfomation( )

				self.RestartEPGUpdateTimer( )


	def RecordConflict( self, aInfo ) :
		label = [ '', '', '' ]
		if aInfo[0].mError == -1 :
			label[0] = 'Error EPG'
			label[1] = 'Can not found EPG Information'
		else :
			conflictNum = len( aInfo ) - 1
			if conflictNum > 3 :
				conflictNum = 3
			for i in range( conflictNum ) :
				timer = self.mDataCache.Timer_GetById( aInfo[ i + 1 ].mParam )
				time = '%s~%s' % ( TimeToString( timer.mStartTime, TimeFormatEnum.E_HH_MM ), TimeToString( timer.mStartTime + timer.mDuration, TimeFormatEnum.E_HH_MM ) )
				channelNum = '%04d' % timer.mChannelNo
				epgNAme = timer.mName
				label[i] = time + ' ' + channelNum + ' ' + epgNAme
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( 'Conflict', label[0], label[1], label[2] )
		dialog.doModal( )

