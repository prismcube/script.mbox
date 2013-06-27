from pvr.gui.WindowImport import *
import traceback

E_SIMPLE_CHANNEL_LIST_BASE_ID		=  WinMgr.WIN_ID_SIMPLE_CHANNEL_LIST * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID
LIST_ID_BIG_CHANNEL					= E_SIMPLE_CHANNEL_LIST_BASE_ID + 1000


E_NOMAL_UPDATE_TIME				= 30
E_SHORT_UPDATE_TIME				= 1


class SimpleChannelList( BaseWindow ) :

	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mLock = thread.allocate_lock( )		
		self.mEPGHashTable = {}
		self.mEPGList	= []	
		self.mListItems = []		
		self.mFirstTune = False
		self.mEPGUpdateTimer = None
		self.mEnableAysncTimer = False		
	
	def onInit( self ) :
		self.SetActivate( True )
		self.SetFrontdisplayMessage( MR_LANG('Channel List') )
		self.mWinId = xbmcgui.getCurrentWindowId( )

		self.mEnableAysncTimer = True		
		self.mFirstTune = False
		self.mEPGUpdateTimer = None		

		self.mCtrlBigList = self.getControl( LIST_ID_BIG_CHANNEL )
		#self.SetSingleWindowPosition( E_SIMPLE_CHANNEL_LIST_BASE_ID )
		#self.SetPipScreen( )

		self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( )
		self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
		self.mServiceType	 = self.mCurrentMode.mServiceType

		LOG_TRACE( 'ZeppingMode(%d,%d,%d)' %( self.mCurrentMode.mServiceType, self.mCurrentMode.mMode, self.mCurrentMode.mSortingMode ) )
		self.mChannelList = self.mDataCache.Channel_GetList( )
		self.mChannelListHash = {}

		#LOG_TRACE( "ChannelList=%d" %len( self.mChannelList ) )
		
		if self.mChannelList :
			for channel in self.mChannelList :
				self.mChannelListHash[ '%d:%d:%d' %( channel.mSid, channel.mTsid, channel.mOnid) ] = channel
	
		
		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		
		self.UpdateAllEPGList( )
		self.FocusCurrentChannel()

		self.mEventBus.Register( self )	

		self.StartEPGUpdateTimer( )

		self.mInitialized = True
		self.setFocusId( LIST_ID_BIG_CHANNEL )


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		self.GetFocusId( )
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		#LOG_TRACE('onAction=%d' %actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR:
			self.Close( )

		elif actionId == Action.ACTION_MOVE_LEFT or actionId == Action.ACTION_MOVE_RIGHT:
			self.Close( )

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN or actionId == Action.ACTION_PAGE_UP  or actionId == Action.ACTION_PAGE_DOWN:
			self.UpdateSelectedPosition( )

		elif actionId == Action.ACTION_MBOX_TVRADIO :
			self.mEventBus.Deregister( self )
			self.StopEPGUpdateTimer( )

			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.ToggleTVRadio( )
				if ret :
					self.SetRadioScreen( self.mServiceType )

				else :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No channels available for the selected mode' ) )
					dialog.doModal( )

			self.StartEPGUpdateTimer( )
			self.mEventBus.Register( self )			


	def onClick( self, aControlId ) :
		if aControlId  == LIST_ID_BIG_CHANNEL :
			self.Tune( )


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			if aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
				#if self.mIsUpdateEnable == True	:
				LOG_TRACE( 'record start/stop event' )
				self.StopEPGUpdateTimer( )
				self.UpdateListUpdateOnly( )
				self.StartEPGUpdateTimer( E_SHORT_UPDATE_TIME )

			elif aEvent.getName( ) == ElisEventCurrentEITReceived.getName( ) :
				if self.mFirstTune == True :
					self.mFirstTune = False
					LOG_TRACE( '--------------- First Tune -----------------' )
					self.StartEPGUpdateTimer( E_SHORT_UPDATE_TIME )			


	def Close( self ) :
		LOG_TRACE( 'LAEL98 TEST CLOSE')
		self.mEnableAysncTimer = False
		self.mFirstTune = False
		self.mEventBus.Deregister( self )

		self.StopEPGUpdateTimer( )
		WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )


	def Flush( self ) :
		self.mEPGList = []
		self.mEPGHashTable = {}


	def UpdateAllEPGList( self ) :
		self.Flush( )
		self.Load( )
		self.UpdateList( )
		threading.Timer( 0.5, self.UpdateSelectedPosition ).start( )		


	def Load( self ) :
		LOG_TRACE( '----------------------------------->' )
		self.mLock.acquire( )
		try :
			self.mEPGList = self.mDataCache.Epgevent_GetCurrentListByEpgCF( self.mServiceType )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		self.mLock.release( )

		if self.mEPGList == None or len ( self.mEPGList ) <= 0 :
			return

		LOG_TRACE( 'self.mEPGList COUNT=%d' %len( self.mEPGList ) )
		
		for epg in self.mEPGList :
			self.mEPGHashTable[ '%d:%d:%d' %( epg.mSid, epg.mTsid, epg.mOnid) ] = epg


	def UpdateListUpdateOnly( self ) :
		self.UpdateList( True )


	def UpdateList( self, aUpdateOnly=False ) :
		if self.mChannelList == None or len( self.mChannelList ) <= 0 :
			self.mCtrlBigList.reset( )
			self.mListItems = []
			xbmc.executebuiltin( 'container.refresh' )			
			return

		#aUpdateOnly = True
		if self.mListItems == None  :
			aUpdateOnly = False
			self.mLock.acquire( )
			self.mListItems = []
			self.mLock.release( )			
		else :
			if len( self.mChannelList ) != len( self.mListItems ) :
				LOG_TRACE( 'UpdateOnly------------>Create' )
				aUpdateOnly = False 
				self.mLock.acquire( )
				self.mListItems = []
				self.mLock.release( )

		print 'LAEL98 UPDATE CONTAINER aUpdateOnly=%d' %aUpdateOnly
				
		currentTime = self.mDataCache.Datetime_GetLocalTime( )
		runningTimers = self.mDataCache.Timer_GetRunningTimers( )		

		strNoEvent = MR_LANG( 'No event' )

		if aUpdateOnly == False :
			self.mListItems = []
			for i in range( len( self.mChannelList ) ) :
				listItem = xbmcgui.ListItem( '', '' )
				self.mListItems.append( listItem )				
			self.mCtrlBigList.addItems( self.mListItems )
		
		for i in range( len( self.mChannelList ) ) :
			channel = self.mChannelList[i]
			if self.IsRunningTimer( runningTimers, channel ) :
				tempChannelName = '[COLOR=red]%04d %s[/COLOR]' %( channel.mNumber, channel.mName )
			else :
				tempChannelName = '%04d %s' %( channel.mNumber, channel.mName )

			hasEpg = False

			try :
				epgEvent = self.GetEPGByIds( channel.mSid, channel.mTsid, channel.mOnid )

				if epgEvent :
					hasEpg = True
					listItem = self.mListItems[i]
					listItem.setLabel( tempChannelName )
					listItem.setLabel2( epgEvent.mEventName )

					epgStart = epgEvent.mStartTime + self.mLocalOffset
					listItem.setProperty( 'HasEvent', 'true' )					
					listItem.setProperty( 'Percent', '%s' %self.CalculateProgress( currentTime, epgStart, epgEvent.mDuration  ) )

				else :
					listItem = self.mListItems[i]
					listItem.setLabel( tempChannelName )
					listItem.setLabel2( strNoEvent )
					listItem.setProperty( 'HasEvent', 'false' )					


				#add channel logo
				if E_USE_CHANNEL_LOGO == True :
					logo = '%s_%s' %(channel.mCarrier.mDVBS.mSatelliteLongitude, channel.mSid )
					listItem.setProperty( 'ChannelLogo', self.mChannelLogo.GetLogo( logo, self.mServiceType ) )
				

			except Exception, ex :
				LOG_ERR( "Exception %s" %traceback.format_exc() )

			if aUpdateOnly == True and  i==8 :
				xbmc.executebuiltin( 'container.refresh' )
				print 'LAEL98 UPDATE CONTAINER'

		xbmc.executebuiltin( 'container.refresh' )


	def UpdateSelectedPosition( self ) :
		selectedPos = self.mCtrlBigList.getSelectedPosition( )

		if selectedPos < 0 :
			self.setProperty( 'SelectedPosition', '0' )
		else :
			self.setProperty( 'SelectedPosition', '%d' % ( selectedPos + 1 ) )


	def FocusCurrentChannel( self ) :
		if self.mChannelList == None :
			return

		fucusIndex = 0
		if self.mCurrentChannel and self.mCurrentChannel.mError == 0 :
			for channel in self.mChannelList:
				if channel.mNumber == self.mCurrentChannel.mNumber :
					break
				fucusIndex += 1

			self.mCtrlBigList.selectItem( fucusIndex )


	def GetEPGByIds( self, aSid, aTsid, aOnid ) :
		return self.mEPGHashTable.get( '%d:%d:%d' %( aSid, aTsid, aOnid ), None )


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

		#LOG_TRACE( 'Percent=%d' %percent )
		return percent


	def IsRunningTimer( self, aRunningTimers, aChannel ) :
		if aRunningTimers == None :
			return False

		for timer in aRunningTimers :
			if timer.mSid == aChannel.mSid  and timer.mTsid == aChannel.mTsid and timer.mOnid == aChannel.mOnid :
				return True

		return False


	def Tune( self ) :
		self.StopEPGUpdateTimer( )	
		selectedPos = self.mCtrlBigList.getSelectedPosition( )
		if selectedPos >= 0 and self.mChannelList and selectedPos < len( self.mChannelList ) :
			channel = self.mChannelList[ selectedPos ]
			if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
				self.mDataCache.Player_Stop( )
			else :
				if self.mCurrentChannel.mNumber == channel.mNumber :
					self.Close( )
					return

			if not self.mDataCache.Get_Player_AVBlank( ) :
				self.mDataCache.Player_AVBlank( True )

			self.mDataCache.Channel_SetCurrent( channel.mNumber, channel.mServiceType )
			self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
			self.mFirstTune = True
		self.RestartEPGUpdateTimer( )


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

		if self.mEnableAysncTimer == False :
			LOG_WARN( 'EnableAysncTimer is False' )		
			return

		self.Load( )

		self.UpdateListUpdateOnly( )
		self.RestartEPGUpdateTimer( )


	def ToggleTVRadio( self ) :
		if not self.mDataCache.ToggleTVRadio( ) :
			return False

		self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( )
		self.mServiceType = self.mCurrentMode.mServiceType
		#self.mChannelList = self.mDataCache.Channel_GetAllChannels( self.mServiceType )
		self.mChannelList = self.mDataCache.Channel_GetList( )

		lastChannelNumber = 1
		if self.mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
			lastChannelNumber = ElisPropertyInt( 'Last TV Number', self.mCommander ).GetProp( )
		else :
			lastChannelNumber = ElisPropertyInt( 'Last Radio Number', self.mCommander ).GetProp( )

		self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
		if lastChannelNumber < len( self.mChannelList ) :
			channelIndex = lastChannelNumber - 1
			if channelIndex >= 0:
				self.mCurrentChannel = self.mChannelList[ channelIndex ]

		LOG_ERR( 'TOGGLE TVRADIO' )

		self.UpdateAllEPGList( )

		return True

