from pvr.gui.WindowImport import *

E_EPG_WINDOW_BASE_ID			=  WinMgr.WIN_ID_EPG_WINDOW * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID

BUTTON_ID_EPG_MODE				= E_EPG_WINDOW_BASE_ID + 100
RADIIOBUTTON_ID_EXTRA			= E_EPG_WINDOW_BASE_ID + 101
LIST_ID_COMMON_EPG				= E_BASE_WINDOW_ID + 3500
LIST_ID_BIG_EPG					= E_BASE_WINDOW_ID + 3510
LIST_ID_GRID_CHANNEL				= E_EPG_WINDOW_BASE_ID + 2000


SCROLL_ID_COMMON_EPG			= E_BASE_WINDOW_ID + 3501
SCROLL_ID_BIG_EPG				= E_BASE_WINDOW_ID + 3511

BUTTON_ID_SEARCH				= E_EPG_WINDOW_BASE_ID + 202
LABEL_ID_TIME					= E_EPG_WINDOW_BASE_ID + 300
LABEL_ID_DATE					= E_EPG_WINDOW_BASE_ID + 301
LABEL_ID_DURATION				= E_EPG_WINDOW_BASE_ID + 302
LABEL_ID_EVENT_NAME				= E_EPG_WINDOW_BASE_ID + 303
LABEL_ID_EPG_CHANNEL_NAME		= E_EPG_WINDOW_BASE_ID + 400
LABEL_ID_CURRNET_CHANNEL_NAME	= E_EPG_WINDOW_BASE_ID + 401


E_EPG_WINDOW_DEFAULT_FOCUS_ID	=  E_EPG_WINDOW_BASE_ID + 9003


E_VIEW_GRID						= 0
E_VIEW_CHANNEL					= 1
E_VIEW_CURRENT					= 2
E_VIEW_FOLLOWING				= 3
E_VIEW_END						= 4

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
E_SEVEN_DAYS_EPG_TIME 			= 24 * 3600 * 7

E_GRID_HALF_HOUR				= 30 * 60
E_GRID_MAX_TIMELINE_COUNT		= 8
E_GRID_MAX_ROW_COUNT			= 8
E_GRID_MAX_COL_COUNT			= 20
E_GRID_MAX_BUTTON_COUNT			= 100
E_GRID_SCHEDULED_BUTTON_COUNT	= 20
E_GRID_DEFAULT_DELTA_TIME		= 60 * 30
E_GRID_DEFAULT_HEIGHT			= 60
E_GRID_DEFAULT_GAP				= 5

E_DIR_CURRENT					= 0
E_DIR_LINE_UP					= 1
E_DIR_LINE_DOWN					= 2
E_DIR_PAGE_UP					= 3
E_DIR_PAGE_DOWN					= 4


BUTTON_ID_BASE_TIME_LINE		= E_EPG_WINDOW_BASE_ID + 1001
BUTTON_ID_BASE_CHANNEL			= E_EPG_WINDOW_BASE_ID + 2001
BUTTON_ID_BASE_LOGS				= E_EPG_WINDOW_BASE_ID + 2101
BUTTON_ID_BASE_GRID				= E_EPG_WINDOW_BASE_ID + 3001
BUTTON_ID_SHOWING_DATE			= E_EPG_WINDOW_BASE_ID + 1010
IMAGE_ID_TIME_SEPERATOR			= E_EPG_WINDOW_BASE_ID + 3500
BUTTON_ID_FOCUS_BUTTON			= E_EPG_WINDOW_BASE_ID + 3501
IMAGE_ID_GRID_CAS				= E_EPG_WINDOW_BASE_ID + 3502
LABEL_ID_GRID_EPG				= E_EPG_WINDOW_BASE_ID + 3503
GROUP_ID_LEFT_SLIDE				= E_EPG_WINDOW_BASE_ID + 9000

BUTTON_ID_BASE_RUNNNING_REC		= E_EPG_WINDOW_BASE_ID + 3601
BUTTON_ID_BASE_SCHEDULED		= E_EPG_WINDOW_BASE_ID + 3701



class GridMeta( object ) :
	def __init__( self, aControlId = 0, aRow = 0, aCol = 0, aEPG = None, aChannelIndex = 0 ) :
		self.mId = aControlId
		self.mRow = aRow
		self.mCol = aCol
		self.mEPG = aEPG
		self.mChannelIndex = aChannelIndex

	
class EPGWindow( BaseWindow ) :

	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mServiceType = ElisEnum.E_SERVICE_TYPE_TV
		self.mLock = thread.allocate_lock( )
		self.mEnableAysncTimer = False
		self.mFirstTune = False

		self.mEPGList = []
		self.mEPGHashTable = {}
		self.mEPGCount = 0
		self.mListItems = []
		self.mTimerList = []
		self.mUpdateEPGInfomationTimer = None
		

		#GRID MODE
		self.mCtrlTimelineButtons = []
		self.mCtrlChannelButtons = []
		self.mCtrlChannelLogos = []		
		self.mCtrlGridEPGButtonList = []
		self.mCtrlRecButtonList = []
		self.mCtrlScheduledButtonList = []
		self.mCtrlFocusButton = None
		#self.mCtrlGridNavigationButtons	= []	
		
		self.mShowingGMTTime = 0
		self.mShowingOffset = 0		
		self.mDeltaTime = E_GRID_HALF_HOUR
		self.mGridEPGList = None
		self.mVisibleFocusRow = 0
		self.mVisibleFocusCol = 0		
		self.mGridCanvasWidth = 880
		self.mGridItemHeight = E_GRID_DEFAULT_HEIGHT
		self.mGridItemGap = E_GRID_DEFAULT_GAP
		self.mGridLastFoucusId = 0
		self.mGridItemGap = 5

	def onInit( self ) :
	
		self.setFocusId( E_EPG_WINDOW_DEFAULT_FOCUS_ID )		

		self.mEnableAysncTimer = True
		self.mFirstTune = False

		self.SetActivate( True )
		self.SetFrontdisplayMessage( 'EPG' )		
		self.mWinId = xbmcgui.getCurrentWindowId( )

		self.mSelectedIndex = 0
		#self.mListItems = []
		self.Flush( )

		#GRID MODE
		self.mVisibleTopIndex = 0
		self.mShowingOffset = 0
		self.mGridEPGList = [None] * E_GRID_MAX_ROW_COUNT
		self.mGridLastFoucusId = BUTTON_ID_BASE_GRID
		self.mCtrlGridTimeSeperator = self.getControl( IMAGE_ID_TIME_SEPERATOR )
		self.mCtrlGridCas	= self.getControl( IMAGE_ID_GRID_CAS )
		self.mCtrlGridEPGInfo = self.getControl( LABEL_ID_GRID_EPG )
		self.mGridItemGap = int( self.getProperty( 'GridItemGap' ) )
		self.mFocusButton = self.getControl( BUTTON_ID_FOCUS_BUTTON )
		self.mFocusButton.setVisible( False )

		self.mPreRecTime	= ElisPropertyEnum( 'Pre-Rec Time', self.mCommander ).GetProp( )
		self.mPostRecTime = ElisPropertyEnum( 'Post-Rec Time', self.mCommander ).GetProp( )		

		self.mEPGMode = int( GetSetting( 'EPG_MODE' ) )
		self.mCtrlEPGMode = self.getControl( BUTTON_ID_EPG_MODE )
		self.mCtrlList = self.getControl( LIST_ID_COMMON_EPG )
		self.mCtrlBigList = self.getControl( LIST_ID_BIG_EPG )
		self.mCtrlGridChannelList = self.getControl( LIST_ID_GRID_CHANNEL )

		self.mCtrlTimeLabel = self.getControl( LABEL_ID_TIME )
		self.mCtrlDateLabel = self.getControl( LABEL_ID_DATE )
		self.mCtrlDurationLabel = self.getControl( LABEL_ID_DURATION )
		self.mCtrlEPGDescription = self.getControl( LABEL_ID_EVENT_NAME )
		self.mCtrlEPGChannelLabel = self.getControl( LABEL_ID_EPG_CHANNEL_NAME )
		self.mCtrlCurrentChannelLabel = self.getControl( LABEL_ID_CURRNET_CHANNEL_NAME )

		self.UpdateViewMode( )
		self.SetSingleWindowPosition( E_EPG_WINDOW_BASE_ID )

		self.SetPipScreen( )

		self.ResetEPGInfomation( )
		self.InitControl( )
		self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( )
		self.mServiceType = self.mCurrentMode.mServiceType
		self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )

		LOG_TRACE( 'ZeppingMode(%d,%d,%d)' %( self.mCurrentMode.mServiceType, self.mCurrentMode.mMode, self.mCurrentMode.mSortingMode ) )
		#self.mChannelList = self.mDataCache.Channel_GetList( )
		self.mChannelList = self.mDataCache.Channel_GetAllChannels( self.mServiceType )
		self.UpdateFootor( )

		if self.mChannelList == None :
			LOG_WARN( 'No Channel List' )
		else:
			LOG_TRACE( 'ChannelList=%d' %len( self.mChannelList ) )

		self.mSelectChannel = self.mCurrentChannel
		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )

		LOG_TRACE( 'CHANNEL current=%s select=%s' %( self.mCurrentChannel, self.mSelectChannel ) )


		if self.mEPGMode == E_VIEW_GRID :
			self.SetVideoRestore( )

		self.UpdateCurrentChannel( )
		self.UpdateAllEPGList( )

		self.mEventBus.Register( self )

		self.StartEPGUpdateTimer( )

		self.SetFocusList( self.mEPGMode )
		self.mInitialized = True


	def LoadEPGControls( self ) :
		self.InitTimelineButtons( )
		self.InitGridEPGButtons( )

	

	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return

		self.GetFocusId()
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR or actionId == Action.ACTION_SHOW_INFO:
			focusId = self.getFocusId( )
			if focusId == BUTTON_ID_EPG_MODE or focusId == RADIIOBUTTON_ID_EXTRA or focusId == BUTTON_ID_SEARCH:
				self.SetFocusList( self.mEPGMode )				
			else :
				self.Close( )
	
		elif actionId == Action.ACTION_MOVE_RIGHT :
			if self.mEPGMode == E_VIEW_GRID	:
				focusId = self.getFocusId( )
				if focusId == LIST_ID_GRID_CHANNEL  :
					self.GridControlRight( )
				else :
					self.setFocusId( LIST_ID_GRID_CHANNEL )
					

		elif actionId == Action.ACTION_MOVE_LEFT :
			if self.mEPGMode == E_VIEW_GRID	:
				focusId = self.getFocusId( )	
				LOG_TRACE('lael98 test focusid=%d' %focusId )
				if focusId == LIST_ID_GRID_CHANNEL  :
					LOG_TRACE('lael98 test focusid=%d' %focusId )				
					self.GridControlLeft( )
				else :
					self.setFocusId( LIST_ID_GRID_CHANNEL )


		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN :
			if self.mEPGMode == E_VIEW_GRID	:
				focusId = self.getFocusId( )
				if focusId == LIST_ID_GRID_CHANNEL  :
					if actionId == Action.ACTION_MOVE_UP :
						self.GridControlUp( )
					else :
						self.GridControlDown( )
		
			elif self.mFocusId == LIST_ID_COMMON_EPG or self.mFocusId == LIST_ID_BIG_EPG or self.mFocusId == SCROLL_ID_COMMON_EPG or self.mFocusId == SCROLL_ID_BIG_EPG:
				self.UpdateEPGInfomation( )

		elif actionId == Action.ACTION_PAGE_UP  or actionId == Action.ACTION_PAGE_DOWN :
			if self.mEPGMode == E_VIEW_GRID	:
				focusId = self.getFocusId( )
				if focusId == LIST_ID_GRID_CHANNEL  :
					if actionId == Action.ACTION_PAGE_UP :
						self.GridControlPageUp( )
					else :
						self.GridControlPageDown( )

			elif self.mFocusId == LIST_ID_COMMON_EPG or self.mFocusId == LIST_ID_BIG_EPG or self.mFocusId == SCROLL_ID_COMMON_EPG or self.mFocusId == SCROLL_ID_BIG_EPG:
				self.UpdateEPGInfomation( )

		elif actionId == Action.ACTION_CONTEXT_MENU:
			if self.mChannelList == None or len( self.mChannelList ) <= 0 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No channels available' ) )			
	 			dialog.doModal( )
				return
		
			self.mEventBus.Deregister( self )
			self.StopEPGUpdateTimer( )

			contextAction = self.ShowContextMenu( )

			if contextAction == CONTEXT_SHOW_ALL_TIMERS or contextAction == CONTEXT_SEARCH :
				self.DoContextAction( contextAction ) 
			else :
				self.DoContextAction( contextAction ) 
				self.StartEPGUpdateTimer( )
				self.mEventBus.Register( self )

		elif actionId == Action.ACTION_MBOX_ARCHIVE :
			if HasAvailableRecordingHDD( ) == False :
				return

			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )

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

		elif actionId == Action.ACTION_MBOX_TEXT :
			self.ShowSearchDialog( )

		elif actionId == Action.ACTION_PAUSE or actionId == Action.ACTION_PLAYER_PLAY :
			if self.mEPGMode == E_VIEW_GRID :
				if self.mDeltaTime	== E_GRID_HALF_HOUR :
					self.mDeltaTime	= E_GRID_HALF_HOUR/2
				else :
					self.mDeltaTime	= E_GRID_HALF_HOUR

				self.mVisibleFocusCol = 0
				self.UpdateAllEPGList( )
				self.GridSetFocus( )
			else :
				return


	def onClick( self, aControlId ) :
		LOG_TRACE( 'aControlId=%d' %aControlId )
		if self.IsActivate( ) == False  :
			return


		if aControlId  == LIST_ID_GRID_CHANNEL :
			self.Tune( )
			"""
			if self.mChannelList == None or len( self.mChannelList ) == 0 :
				self.setFocusId( BUTTON_ID_FOCUS_BUTTON  )
				return
		
			self.GridSetFocus( )
			"""
				
		elif  aControlId == LIST_ID_COMMON_EPG or aControlId == LIST_ID_BIG_EPG :
			self.Tune( )
			
		elif aControlId >= BUTTON_ID_BASE_GRID and aControlId < BUTTON_ID_BASE_GRID + E_GRID_MAX_BUTTON_COUNT :
			self.Tune( )
		
		elif aControlId == BUTTON_ID_EPG_MODE :
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

			#GRID MODE
			self.SetSingleWindowPosition( E_EPG_WINDOW_BASE_ID )
			if self.mEPGMode == E_VIEW_GRID :
				self.SetVideoRestore( )
			else :
				self.SetPipScreen()
				
			self.UpdateAllEPGList( )
			
			#self.mLock.release( )

			self.mEventBus.Register( self )
			self.StartEPGUpdateTimer( )
		
		elif aControlId == RADIIOBUTTON_ID_EXTRA :
			pass

		elif aControlId == BUTTON_ID_SEARCH :
			self.SetFocusList( self.mEPGMode )
			self.DoContextAction( CONTEXT_SEARCH )


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return

		LOG_TRACE('TEST focusId=%d' %self.getFocusId() )


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			if aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
				#if self.mIsUpdateEnable == True	:
				LOG_TRACE( 'record start/stop event' )
				self.StopEPGUpdateTimer( )
				self.UpdateListUpdateOnly( )
				self.StartEPGUpdateTimer( E_SHORT_UPDATE_TIME )

			elif aEvent.getName( ) == ElisPMTReceivedEvent.getName( ) :
				#LOG_TRACE( "--------- received ElisPMTReceivedEvent-----------" )
				self.UpdatePropertyByCacheData( E_XML_PROPERTY_TELETEXT )
				self.UpdatePropertyByCacheData( E_XML_PROPERTY_SUBTITLE )
				self.UpdatePropertyByCacheData( E_XML_PROPERTY_DOLBYPLUS )

			elif aEvent.getName( ) == ElisEventCurrentEITReceived.getName( ) :
				if self.mFirstTune == True :
					self.mFirstTune = False
					LOG_TRACE( '--------------- First Tune -----------------' )
					self.StartEPGUpdateTimer( E_SHORT_UPDATE_TIME )			
				#self.DoCurrentEITReceived( aEvent )


	def Close( self ) :
		self.mEnableAysncTimer = False
		self.mFirstTune = False
		self.mEventBus.Deregister( self )	

		self.StopEPGUpdateTimer( )
		self.SetVideoRestore( )
		#self.mCtrlList.reset( )
		#self.mCtrlBigList.reset( )
		WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )


	def InitControl( self ) :

		if self.mEPGMode == E_VIEW_GRID :
			self.mCtrlEPGMode.setLabel( '%s: %s' %( MR_LANG( 'View' ), MR_LANG( 'Grid' ) ) )
		elif self.mEPGMode == E_VIEW_CHANNEL :
			self.mCtrlEPGMode.setLabel( '%s: %s' %( MR_LANG( 'View' ), MR_LANG( 'Channel' ) ) )
		elif self.mEPGMode == E_VIEW_CURRENT :			
			self.mCtrlEPGMode.setLabel( '%s: %s' %( MR_LANG( 'View' ), MR_LANG( 'Current' ) ) )
		elif self.mEPGMode == E_VIEW_FOLLOWING :			
			self.mCtrlEPGMode.setLabel( '%s: %s' %( MR_LANG( 'View' ),  MR_LANG( 'Following' ) ) )
		else :
			LOG_WARN( 'Unknown epg mode' )
			

	def UpdateViewMode( self ) :
		if self.mEPGMode == E_VIEW_GRID :
			self.setProperty( 'EPGMode', 'grid' )
		elif self.mEPGMode == E_VIEW_CHANNEL :
			self.setProperty( 'EPGMode', 'channel' )
			self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'EPG' ), MR_LANG( 'Channel' ) ) )
		elif self.mEPGMode == E_VIEW_CURRENT :			
			self.setProperty( 'EPGMode', 'current' )
			self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'EPG' ), MR_LANG( 'Current' ) ) )
		elif self.mEPGMode == E_VIEW_FOLLOWING :			
			self.setProperty( 'EPGMode', 'following' )
			self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'EPG' ), MR_LANG( 'Following' ) ) )
		else :
			self.mEPGMode = E_VIEW_GRID 		
			self.setProperty( 'EPGMode', 'grid' )

		LOG_TRACE( '---------------------self.mEPGMode=%d' %self.mEPGMode )


	def Flush( self ) :
		self.mEPGList = []
		self.mEPGHashTable = {}
		self.mEPGCount = 0
		self.mTimerList = []


	def Load( self ) :

		LOG_TRACE( '----------------------------------->Start' )
		self.mDebugStart = time.time( )

		self.mLock.acquire( )
		
		if self.mEPGMode == E_VIEW_GRID :
			self.LoadByGrid( )		
		elif self.mEPGMode == E_VIEW_CHANNEL :
			self.LoadByChannel( )
		elif self.mEPGMode == E_VIEW_CURRENT :			
			self.LoadByCurrent( )
		elif self.mEPGMode == E_VIEW_FOLLOWING :			
			self.LoadByFollowing( )
		else :
			self.mEPGMode = E_VIEW_GRID 		
			self.LoadByGrid( )

		self.mLock.release( )
		LOG_TRACE( '----------------------------------->End' )			
		self.mDebugEnd = time.time( )
		print ' epg loading test time =%s' %( self.mDebugEnd  - self.mDebugStart )


	def LoadByGrid( self ) :

		start = time.time( )
		gmtFrom = self.mShowingGMTTime + self.mShowingOffset
		gmtUntil = gmtFrom + E_GRID_MAX_TIMELINE_COUNT * self.mDeltaTime

		LOG_ERR( 'From : %s' % TimeToString( gmtFrom+self.mDataCache.Datetime_GetLocalOffset( ), TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )		
		LOG_ERR( 'Until : %s' % TimeToString( gmtUntil+self.mDataCache.Datetime_GetLocalOffset( ), TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )				

		strNoEvent = MR_LANG( 'No event' )
		epgTotalCount = 0
		epgCount = 0
		channelCount = 0

		if self.mChannelList  :
			channelCount = len( self.mChannelList )
		else :
			LOG_WARN( 'no channel')

		for i in range( E_GRID_MAX_ROW_COUNT ) :
			#DrawChannel
			epgList = []

			
			if self.mVisibleTopIndex < 0 or self.mVisibleTopIndex + i >= channelCount :
				LOG_ERR( 'GRID error offsetPosition=%d i=%d channelCount=%d' %( self.mVisibleTopIndex , i,channelCount ) )
				break

			channel = self.mChannelList[ self.mVisibleTopIndex + i]
			if channel :
				epgList = self.mDataCache.Epgevent_GetListByChannel( channel.mSid,  channel.mTsid,  channel.mOnid, gmtFrom, gmtUntil, 20 )
			
				if epgList == None or len ( epgList ) <= 0 or len ( epgList ) == 20 or epgList[0].mError != 0 :
					epgList = []
					epgEvent = ElisIEPGEvent( )
					epgEvent.mSid = channel.mSid
					epgEvent.mTsid = channel.mTsid
					epgEvent.mOnid = channel.mOnid
					epgEvent.mStartTime = gmtFrom 
					epgEvent.mDuration = E_GRID_MAX_TIMELINE_COUNT * self.mDeltaTime
					epgEvent.mEventName = strNoEvent
					epgList.append( epgEvent )

				epgCount = len( epgList )
				if epgCount > 0 :
					lastEPG = epgList[epgCount-1]
					if ( lastEPG.mStartTime + lastEPG.mDuration ) < gmtUntil:
						epgEvent = ElisIEPGEvent( )
						epgEvent.mSid = channel.mSid
						epgEvent.mTsid = channel.mTsid
						epgEvent.mOnid = channel.mOnid
						epgEvent.mStartTime = lastEPG.mStartTime + lastEPG.mDuration
						epgEvent.mDuration = gmtUntil - epgEvent.mStartTime
						#LOG_ERR( 'Start : %s' % (TimeToString( epgEvent.mStartTime + self.mDataCache.Datetime_GetLocalOffset( ), TimeFormatEnum.E_HH_MM_SS ) ) )
						#LOG_ERR( 'End :  %s' % (TimeToString( epgEvent.mStartTime+epgEvent.mDuration+self.mDataCache.Datetime_GetLocalOffset( ), TimeFormatEnum.E_HH_MM_SS ) ) )
						
						epgEvent.mEventName = strNoEvent
						epgList.append( epgEvent )
						epgCount += 1
				
				self.mGridEPGList[i]=epgList

				epgTotalCount += epgCount
				
			else :
				LOG_ERR( 'Cannot find channel' )
				break

		end = time.time( )

		LOG_ERR( 'GRID epgTotalCount=%d' %epgTotalCount )				
		print 'epg grid load =%s' %( end  - start )


	def LoadByChannel( self ) :
	
		gmtFrom = self.mDataCache.Datetime_GetGMTTime( )
		gmtUntil = gmtFrom + E_SEVEN_DAYS_EPG_TIME

		LOG_TRACE( 'Select Channel Number=%d' %self.mSelectChannel.mNumber )
		LOG_ERR( 'START : localoffset=%d' %self.mLocalOffset )
		LOG_ERR( 'START : %s' % TimeToString( gmtFrom+self.mLocalOffset, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
		LOG_ERR( 'START : %d : %d %d' % ( self.mSelectChannel.mSid,  self.mSelectChannel.mTsid,  self.mSelectChannel.mOnid) )
		
		try :
			self.mEPGList = self.mDataCache.Epgevent_GetListByChannel( self.mSelectChannel.mSid,  self.mSelectChannel.mTsid,  self.mSelectChannel.mOnid, gmtFrom, gmtUntil, 256 )		
			#self.mEPGList = self.mDataCache.Epgevent_GetListByChannelFromEpgCF(  self.mSelectChannel.mSid,  self.mSelectChannel.mTsid,  self.mSelectChannel.mOnid )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		if self.mEPGList == None or self.mEPGList[0].mError != 0 :
			LOG_TRACE( 'NO EPG' )
			self.mEPGList = None
			return

		if self.mEPGList == None or len ( self.mEPGList ) <= 0 :
			LOG_TRACE( 'NO EPG' )
			return

		LOG_ERR( 'self.mEPGList COUNT=%d' %len(self.mEPGList ) )

		for epg in self.mEPGList :
			self.mEPGHashTable[ '%d:%d:%d' %( epg.mSid, epg.mTsid, epg.mOnid) ] = epg


	def LoadByCurrent( self ) :
	
		try :
			self.mEPGList = self.mDataCache.Epgevent_GetCurrentListByEpgCF( self.mServiceType )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		if self.mEPGList == None or len ( self.mEPGList ) <= 0 :
			return

		LOG_TRACE( 'self.mEPGList COUNT=%d' %len( self.mEPGList ) )
		
		for epg in self.mEPGList :
			self.mEPGHashTable[ '%d:%d:%d' %( epg.mSid, epg.mTsid, epg.mOnid) ] = epg


	def LoadByFollowing( self ) :		
		try :
			self.mEPGList = self.mDataCache.Epgevent_GetFollowingListByEpgCF( self.mServiceType )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		if self.mEPGList == None or len ( self.mEPGList ) <= 0 :
			return

		LOG_TRACE( 'self.mEPGList COUNT=%d' %len(self.mEPGList ) )
		
		for epg in self.mEPGList :
			self.mEPGHashTable[ '%d:%d:%d' %( epg.mSid, epg.mTsid, epg.mOnid) ] = epg


	def UpdateSelcetedPosition( self ) :
	
		if self.mChannelList == None :
			self.setProperty( 'SelectedPosition', '0' )
			return

		selectedPos = 0

		if self.mEPGMode == E_VIEW_GRID :
			selectedPos = self.mCtrlGridChannelList.getSelectedPosition( )		
		elif self.mEPGMode == E_VIEW_CHANNEL :
			selectedPos = self.mCtrlList.getSelectedPosition( )		
		else :
			selectedPos = self.mCtrlBigList.getSelectedPosition( )

		self.setProperty( 'SelectedPosition', '%d' %( selectedPos+1 ) )


	def FocusCurrentChannel( self ) :
		if self.mChannelList == None :
			return

		if self.mEPGMode == E_VIEW_CHANNEL :
			self.mCtrlList.selectItem( 0 )
		else :
			fucusIndex = 0
			if self.mCurrentChannel and self.mCurrentChannel.mError == 0 :
				for channel in self.mChannelList:
					if channel.mNumber == self.mCurrentChannel.mNumber :
						break
					fucusIndex += 1

			if self.mEPGMode == E_VIEW_GRID :
				self.mCtrlGridChannelList.selectItem( fucusIndex )		
			else :
				self.mCtrlBigList.selectItem( fucusIndex )


	def UpdateSelectedChannel( self ) :
		if self.mEPGMode == E_VIEW_GRID :
			return
	
		if self.mChannelList == None or len( self.mChannelList ) <= 0 :
			self.mCtrlEPGChannelLabel.setLabel( MR_LANG( 'No Channel' ) )		
		elif self.mSelectChannel :
			self.mCtrlEPGChannelLabel.setLabel( '%04d %s' %( self.mSelectChannel.mNumber, self.mSelectChannel.mName ) )
		else:
			self.mCtrlEPGChannelLabel.setLabel( MR_LANG( 'No Channel' ) )


	def UpdateCurrentChannel( self ) :
		if self.mEPGMode == E_VIEW_GRID :
			return
	
		if self.mCurrentChannel :
			self.mCtrlCurrentChannelLabel.setLabel( self.mCurrentChannel.mName )
		else :
			self.mCtrlCurrentChannelLabel.setLabel( '' )


	def UpdateEPGInfomation( self ) :
	
		self.UpdateSelcetedPosition( )

		if self.mEPGMode == E_VIEW_GRID :
			return
		
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

			else :
				self.ResetEPGInfomation( )

			#component
			self.UpdatePropertyByCacheData( E_XML_PROPERTY_TELETEXT )
			isSubtitle = self.UpdatePropertyByCacheData( E_XML_PROPERTY_SUBTITLE )
			if not isSubtitle :
				self.setProperty( E_XML_PROPERTY_SUBTITLE, HasEPGComponent( epg, ElisEnum.E_HasSubtitles ) )
			if not self.UpdatePropertyByCacheData( E_XML_PROPERTY_DOLBYPLUS ) :
				self.setProperty( E_XML_PROPERTY_DOLBY,HasEPGComponent( epg, ElisEnum.E_HasDolbyDigital ) )
			self.setProperty( E_XML_PROPERTY_HD,       HasEPGComponent( epg, ElisEnum.E_HasHDVideo ) )

			#age info
			UpdatePropertyByAgeRating( self, epg )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def	ResetEPGInfomation( self ) :
		self.mCtrlTimeLabel.setLabel( '' )
		self.mCtrlDateLabel.setLabel( '' )
		self.mCtrlDurationLabel.setLabel( '' )
		self.mCtrlEPGDescription.setText( '' )

		self.setProperty( 'EPGAgeRating', '' )
		self.setProperty( 'HasAgeRating', 'None' )
		self.setProperty( E_XML_PROPERTY_TELETEXT, E_TAG_FALSE )
		self.setProperty( E_XML_PROPERTY_SUBTITLE, E_TAG_FALSE )
		self.setProperty( E_XML_PROPERTY_DOLBY,    E_TAG_FALSE )
		self.setProperty( E_XML_PROPERTY_DOLBYPLUS,E_TAG_FALSE )
		self.setProperty( E_XML_PROPERTY_HD,       E_TAG_FALSE )


	def UpdatePropertyByCacheData( self, aPropertyID = None ) :

		channel = None

		if self.mEPGMode == E_VIEW_GRID :
			return False
		
		elif self.mEPGMode == E_VIEW_CHANNEL :
			channel = self.mSelectChannel
		else :
			selectedPos = self.mCtrlBigList.getSelectedPosition( )
			if selectedPos >= 0 and self.mChannelList and selectedPos < len( self.mChannelList ) :
				channel = self.mChannelList[ selectedPos ]

		if channel :	
			pmtEvent = self.mDataCache.GetCurrentPMTEvent( channel )
			if pmtEvent :
				return UpdatePropertyByCacheData( self, pmtEvent, aPropertyID )

		return False


	def UpdateListUpdateOnly( self ) :
		if self.mEPGMode == E_VIEW_GRID :	
			self.UpdateList( )
		else :
			self.UpdateList( True )


	def UpdateList( self, aUpdateOnly=False ) :
		LOG_TRACE( '------------------------> Start Update----------' )
		#self.mLock.acquire( )	
		#if aUpdateOnly == False :
		#	self.mLock.acquire( )	
		#	self.mListItems = []
		#	self.mLock.release( )

		self.LoadTimerList( )

		if  self.mChannelList  == None :
			 self.mChannelList = []

		if self.mListItems == None :
			self.mListItems = []

		if self.mEPGMode == E_VIEW_GRID :
			self.UpdateGridView( aUpdateOnly )
		
		elif self.mEPGMode == E_VIEW_CHANNEL :
			self.UpdateChannelView( aUpdateOnly )

		elif self.mEPGMode == E_VIEW_CURRENT :
			self.UpdateCurrentView( aUpdateOnly )

		elif self.mEPGMode == E_VIEW_FOLLOWING :
			self.UpdateFollowingView( aUpdateOnly )

		self.UpdateTimeSeperator( )


	def UpdateGridChannelList( self, aUpdateOnly=False ) :

		self.mDebugStart = time.time( )
		try :
			if self.mChannelList == None :
				self.mCtrlGridChannelList.reset( )
				self.mListItems = []			
				return

			aUpdateOnly = True
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

			strNoEvent = MR_LANG( 'No event' )

			if aUpdateOnly == False :
				for i in range( len( self.mChannelList ) ) :
					listItem = xbmcgui.ListItem( '', '' )
					self.mListItems.append( listItem )				
				self.mCtrlGridChannelList.addItems( self.mListItems )
			
			for i in range( len( self.mChannelList ) ) :
				channel = self.mChannelList[i]
				tempChannelName = '%04d %s' %( channel.mNumber, channel.mName )

				listItem = self.mListItems[i]
				listItem.setLabel( tempChannelName )

				#add channel logo
				if E_USE_CHANNEL_LOGO == True :
					logo = '%s_%s' %(channel.mCarrier.mDVBS.mSatelliteLongitude, channel.mSid )
					#LOG_TRACE( 'logo=%s' %logo )
					#LOG_TRACE( 'logo path=%s' %self.mChannelLogo.GetLogo( logo ) )
					listItem.setProperty( 'ChannelLogo', self.mChannelLogo.GetLogo( logo, self.mServiceType ) )

				if  i== E_GRID_MAX_ROW_COUNT:
					xbmc.executebuiltin( 'container.refresh' )
					print 'LAEL98 UPDATE CONTAINER'
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		xbmc.executebuiltin( 'container.refresh' )

		self.mDebugEnd = time.time( )
		print 'epg loading test =%s' %( self.mDebugEnd  - self.mDebugStart )


	def UpdateGridView( self, aUpdateOnly=False) :
		#remove all buttons

		#LOG_TRACE( 'GRID len(mCtrlChannelButtons) = %d' %len(self.mCtrlChannelButtons) )

		start = time.time( )
		enableCount = 0
		
		offsetX = 0
		offsetY = 0
		drawWidth = 100
		row = 0
		col = 0
		drawableTime =  self.mDeltaTime * E_GRID_MAX_TIMELINE_COUNT
		
		for i in range( E_GRID_MAX_ROW_COUNT ) :
			epgList = self.mGridEPGList[i]
			offsetX = 0
			offsetX2 = 0
			if epgList :
				#LOG_TRACE( 'GRID i=%d len(epgList)=%d' %( i, len( epgList ) ) )
				epgCount = len( epgList )

				col = 0
				for j in range( epgCount ) :
					
					if epgList[j].mStartTime + epgList[j].mDuration < self.mShowingGMTTime + self.mShowingOffset:
						LOG_ERR( 'Invalid EPG : i=%d j=%d' %(i,j) )

					if epgList[j].mStartTime >= ( self.mShowingGMTTime + self.mShowingOffset + E_GRID_MAX_TIMELINE_COUNT * self.mDeltaTime ) :
						LOG_ERR( 'Invalid EPG : i=%d j=%d statTime=%s' %(i,j, TimeToString( epgList[j].mStartTime + self.mShowingOffset + self.mDataCache.Datetime_GetLocalOffset( ), TimeFormatEnum.E_HH_MM_SS ) ) )
					

					offsetX = self.mGridCanvasWidth*(  epgList[j].mStartTime - self.mShowingOffset -self.mShowingGMTTime )/(E_GRID_MAX_TIMELINE_COUNT * self.mDeltaTime )

					if offsetX < 0 :
						offsetX = 0

					if offsetX < offsetX2 :
						offsetX = offsetX2


					#LOG_ERR( 'Start : (%d,%d) %s' % (i,j,TimeToString( epgList[j].mStartTime+self.mDataCache.Datetime_GetLocalOffset( ), TimeFormatEnum.E_HH_MM_SS ) ) )
					#LOG_ERR( 'End : (%d,%d) %s' % (i,j,TimeToString( epgList[j].mStartTime+epgList[j].mDuration+self.mDataCache.Datetime_GetLocalOffset( ), TimeFormatEnum.E_HH_MM_SS ) ) )
					duraton = epgList[j].mDuration
					if epgList[j].mStartTime < self.mShowingGMTTime + self.mShowingOffset:
						duraton = epgList[j].mStartTime + epgList[j].mDuration - self.mShowingGMTTime - self.mShowingOffset


					drawWidth = int( duraton* self.mGridCanvasWidth / drawableTime ) 
					#LOG_ERR( 'End : %d' %(drawWidth ) )

					if offsetX + drawWidth > self.mGridCanvasWidth :
						drawWidth = self.mGridCanvasWidth - offsetX

					if drawWidth <= 0 :
						LOG_ERR( 'Invalid width %d : i=%d j=%d' %(drawWidth,i,j) )

					ctrlButton = self.mCtrlGridEPGButtonList[enableCount + col]
					if drawWidth < 20 :
						ctrlButton.setLabel( '.' )
					else :
						ctrlButton.setLabel( epgList[j].mEventName )
					ctrlButton.setPosition( offsetX, offsetY )
					ctrlButton.setVisible( True )							

					ctrlButton.setWidth( drawWidth  )
					offsetX2 = offsetX + drawWidth
					
					gridMeta = GridMeta( ctrlButton.getId(), row, col, epgList[j], self.mVisibleTopIndex  + i )
					self.mEPGHashTable[ '%d:%d' %( self.mVisibleTopIndex + row, col ) ] = gridMeta
					#LOG_ERR( 'controlID : %d' %( gridMeta.mId ) )							
					
					col +=  1

					if epgList[j].mEventId == 0 : #dummy epg
						break

					if offsetX + 5 >= self.mGridCanvasWidth:
						break

				enableCount += col

				offsetY += self.mGridItemHeight + self.mGridItemGap

				row += 1

			else :
				LOG_ERR( 'Cannot find epgList' )
				continue
					

		for i in range(E_GRID_MAX_BUTTON_COUNT - enableCount ) :
			self.mCtrlGridEPGButtonList[enableCount + i].setVisible( False )	

		self.GridUpdateTimer( )
		
		xbmc.executebuiltin( 'container.refresh' )
			
		end = time.time( )

		LOG_TRACE( 'GRID update grid time=%s' %( end - start ) )



	def UpdateChannelView( self, aUpdateOnly ) :

		if self.mEPGList == None :
			self.mCtrlList.reset( )
			self.mListItems = []
			return

		try :
			aUpdateOnly = True
	
			if self.mListItems == None  :
				aUpdateOnly = False
				self.mLock.acquire( )
				self.mListItems = []
				self.mLock.release( )			

			else :
				if len( self.mEPGList ) != len( self.mListItems ) :
					LOG_TRACE( 'UpdateOnly------------>Create' )
					aUpdateOnly = False 
					self.mLock.acquire( )	
					self.mListItems = []
					self.mLock.release( )

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
			#else :
			xbmc.executebuiltin( 'container.refresh' )
			#self.SetFocusList( self.mEPGMode )
			#xbmc.executebuiltin('xbmc.Container.SetViewMode(%d)' %E_VIEW_CHANNEL)
			
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def UpdateCurrentView( self, aUpdateOnly ) :
		self.mDebugStart = time.time( )		
		if self.mChannelList == None :
			self.mCtrlBigList.reset( )
			self.mListItems = []			
			return

		aUpdateOnly = True
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

		strNoEvent = MR_LANG( 'No event' )

		if aUpdateOnly == False :
			for i in range( len( self.mChannelList ) ) :
				listItem = xbmcgui.ListItem( '', '' )
				self.mListItems.append( listItem )				
			self.mCtrlBigList.addItems( self.mListItems )				
		
		for i in range( len( self.mChannelList ) ) :
			channel = self.mChannelList[i]
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
					listItem = self.mListItems[i]
					listItem.setLabel( tempChannelName )
					listItem.setLabel2( strNoEvent )

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

				#add channel logo
				if E_USE_CHANNEL_LOGO == True :
					logo = '%s_%s' %(channel.mCarrier.mDVBS.mSatelliteLongitude, channel.mSid )
					#LOG_TRACE( 'logo=%s' %logo )
					#LOG_TRACE( 'logo path=%s' %self.mChannelLogo.GetLogo( logo ) )
					listItem.setProperty( 'ChannelLogo', self.mChannelLogo.GetLogo( logo, self.mServiceType ) )
				

			except Exception, ex :
				LOG_ERR( "Exception %s" %ex )

			if aUpdateOnly == True and  i==8 :
				xbmc.executebuiltin( 'container.refresh' )
				print 'LAEL98 UPDATE CONTAINER'

			#self.setFocusId( LIST_ID_BIG_EPG )
		#else :
		xbmc.executebuiltin( 'container.refresh' )
		#self.SetFocusList( self.mEPGMode )
		#xbmc.executebuiltin('xbmc.Container.SetViewMode(%d)' %E_VIEW_CURRENT)

		self.mDebugEnd = time.time( )
		print 'epg loading test =%s' %( self.mDebugEnd  - self.mDebugStart )


	def  UpdateFollowingView( self, aUpdateOnly ) :
		if self.mChannelList == None :
			self.mCtrlBigList.reset( )
			self.mListItems = []			
			return

		aUpdateOnly = True
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

		strNoEvent = MR_LANG( 'No event' )

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
						listItem = xbmcgui.ListItem( tempChannelName, strNoEvent )
					else :
						listItem = self.mListItems[i]
						listItem.setLabel( tempChannelName )
						listItem.setLabel2( strNoEvent )
					
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

				#add channel logo
				if E_USE_CHANNEL_LOGO == True :
					logo = '%s_%s' %(channel.mCarrier.mDVBS.mSatelliteLongitude, channel.mSid )
					#LOG_TRACE( 'logo=%s' %logo )
					#LOG_TRACE( 'logo path=%s' %self.mChannelLogo.GetLogo( logo ) )
					listItem.setProperty( 'ChannelLogo', self.mChannelLogo.GetLogo( logo, self.mServiceType ) )

				#ListItem.PercentPlayed
				if aUpdateOnly == False :					
					self.mListItems.append( listItem )

			except Exception, ex :
				LOG_ERR( "Exception %s" %ex )

		if aUpdateOnly == False :
			self.mCtrlBigList.addItems( self.mListItems )
			#self.setFocusId( LIST_ID_BIG_EPG )

		xbmc.executebuiltin( 'container.refresh' )
		#self.SetFocusList( self.mEPGMode )
		#xbmc.executebuiltin('xbmc.Container.SetViewMode(%d)' %E_VIEW_FOLLOWING)	
	

	def GetEPGByIds( self, aSid, aTsid, aOnid ) :
		return self.mEPGHashTable.get( '%d:%d:%d' %( aSid, aTsid, aOnid ), None )
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
			context.append( ContextItem( MR_LANG( 'Extend information' ), CONTEXT_EXTEND_INFOMATION ) )
			context.append( ContextItem( MR_LANG( 'Hotkeys' ), CONTEXT_ACTION_HOTKEYS ) )


		else :
			timer = None

			if self.mEPGMode == E_VIEW_GRID :
				timer = self.GetTimerByFocus( )

			elif self.mEPGMode == E_VIEW_CURRENT or self.mEPGMode == E_VIEW_FOLLOWING :				
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
			context.append( ContextItem( MR_LANG( 'Hotkeys' ), CONTEXT_ACTION_HOTKEYS ) )

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

		elif aContextAction == CONTEXT_ACTION_HOTKEYS :
			self.ShowHotkeys( )


	def ShowHotkeys( self ) :
		if self.mEPGMode == E_VIEW_GRID :
			#context = [ ( 'OSDLeft.png', '', MR_LANG( 'Slide Menu' ) ), ( 'OSDOK.png', '', MR_LANG( 'Tune' ) ), ( 'OSDPlayNF.png', '', MR_LANG( 'Zoom' ) ), ( 'OSDRewindNF.png', '', MR_LANG( 'Return to current time' ) ), ( 'OSDRecordNF.png', '',  MR_LANG( 'Start Recording' ) ), ( 'OSDStopNF.png', '', MR_LANG( 'Stop Recording' ) ), ( 'OSDTeletextNF.png', '', MR_LANG( 'Search' ) ), ( 'OSDTVRadio.png', '', MR_LANG( 'TV/Radio' ) ), ( 'OSDBack.png', 'OSDMenu.png', MR_LANG( 'Go Back' ) ) ]
			context = [ ( 'OSDLeft.png', '', MR_LANG( 'Slide Menu' ) ), ( 'OSDOK.png', '', MR_LANG( 'Tune' ) ), ( 'OSDPlayNF.png', '', MR_LANG( 'Zoom' ) ), ( 'OSDRecordNF.png', '',  MR_LANG( 'Start Recording' ) ), ( 'OSDStopNF.png', '', MR_LANG( 'Stop Recording' ) ), ( 'OSDTeletextNF.png', '', MR_LANG( 'Search' ) ), ( 'OSDTVRadio.png', '', MR_LANG( 'TV/Radio' ) ), ( 'OSDBack.png', 'OSDMenu.png', MR_LANG( 'Go Back' ) ) ]

		elif  self.mEPGMode == E_VIEW_CHANNEL :
			context = [ ( 'OSDLeft.png', '', MR_LANG( 'Slide Menu' ) ), ( 'OSDRewindNF.png', '', MR_LANG( 'Previous Channel' ) ), ( 'OSDForwardNF.png', '', MR_LANG( 'Next Channel' ) ), ( 'OSDRecordNF.png', '',  MR_LANG( 'Start Recording' ) ), ( 'OSDStopNF.png', '', MR_LANG( 'Stop Recording' ) ), ( 'OSDTeletextNF.png', '', MR_LANG( 'Search' ) ), ( 'OSDTVRadio.png', '', MR_LANG( 'TV/Radio' ) ), ( 'OSDBack.png', 'OSDMenu.png', MR_LANG( 'Go Back' ) ) ]

		else :
			context = [ ( 'OSDLeft.png', '', MR_LANG( 'Slide Menu' ) ), ( 'OSDOK.png', '', MR_LANG( 'Tune' ) ), ( 'OSDRecordNF.png', '',  MR_LANG( 'Start Recording' ) ), ( 'OSDStopNF.png', '', 'Stop Recording' ), ( 'OSDTeletextNF.png', '', MR_LANG( 'Search' ) ), ( 'OSDTVRadio.png', '', MR_LANG( 'TV/Radio' ) ), ( 'OSDBack.png', 'OSDMenu.png', MR_LANG( 'Go Back' ) ) ]

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_HOTKEYS )
		dialog.SetProperty( context )
		dialog.doModal( )


	def ShowEPGTimer( self, aEPG ) :
		LOG_TRACE( 'ShowEPGTimer' )

		if HasAvailableRecordingHDD( ) == False :
			return

		try :	
			if aEPG :
				localOffset = self.mDataCache.Datetime_GetLocalOffset( )
				expire  = aEPG.mStartTime + aEPG.mDuration + localOffset
				if expire <=  self.mDataCache.Datetime_GetLocalTime( ) :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG('Error'), MR_LANG("That programme has already finished"))
					dialog.doModal( )
					return
				
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_ADD_TIMER )
			dialog.SetEPG( aEPG )
			dialog.doModal( )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		try :
			if dialog.IsOK() == E_DIALOG_STATE_YES :
				ret = self.mDataCache.Timer_AddEPGTimer( True, 0, aEPG )
				LOG_ERR( 'Conflict ret=%s' %ret )
				if ret and (ret[0].mParam == -1 or ret[0].mError == -1) :
					RecordConflict( ret )
					return

			else :
				LOG_TRACE( '' )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		self.UpdateListUpdateOnly( )
		

	def ShowEditTimer( self ) :
		if HasAvailableRecordingHDD( ) == False :
			return
			
		selectedEPG = self.GetSelectedEPG( )

		timer = None

		if selectedEPG :
			timer = self.GetTimerByEPG( selectedEPG )
			if timer and timer.mTimerId > 0 :	# Edit Mode
				self.ShowManualTimer( selectedEPG, timer )

		else :
			if self.mEPGMode == E_VIEW_GRID :
				timer = self.GetTimerByFocus( )			
		
			elif self.mEPGMode == E_VIEW_CURRENT or self.mEPGMode == E_VIEW_FOLLOWING :
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

		if HasAvailableRecordingHDD( ) == False :
			return

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_ADD_MANUAL_TIMER )


		if aTimer :
			dialog.SetTimer( aTimer, self.IsRunningTimer( aTimer ) )

		"""
		if aEPG :
			dialog.SetEPG( aEPG )
		"""
		if aEPG :
			dialog.SetEPG( aEPG  )
		else :
			dialog.SetEPG( None  )
			
		channel = None

		if self.mEPGMode == E_VIEW_GRID  :
			selectedPos = self.mCtrlGridChannelList.getSelectedPosition( )
			if selectedPos >= 0 and self.mChannelList and selectedPos < len( self.mChannelList ) :
				channel = self.mChannelList[ selectedPos ]
			else :
				LOG_ERR( 'Cannot find the channel' )
				return
		
		elif self.mEPGMode == E_VIEW_CHANNEL  :
			#channel = self.mDataCache.Channel_GetCurrent( )
			channel = self.mSelectChannel
		else :
			selectedPos = self.mCtrlBigList.getSelectedPosition( )
			if selectedPos >= 0 and self.mChannelList and selectedPos < len( self.mChannelList ) :
				channel = self.mChannelList[ selectedPos ]
			else :
				LOG_ERR( 'Cannot find the channel' )
				return
	
		dialog.SetChannel( channel )			

		dialog.doModal( )

		if dialog.IsOK( ) == E_DIALOG_STATE_ERROR :
			if dialog.GetConflictTimer( ) == None :
				infoDialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				infoDialog.SetDialogProperty( MR_LANG( 'Error' ), dialog.GetErrorMessage( ) )
				infoDialog.doModal( )
			else :
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

			if self.mEPGMode == E_VIEW_GRID  :
				timer = self.GetTimerByFocus( )
			
			elif self.mEPGMode == E_VIEW_CURRENT or self.mEPGMode == E_VIEW_FOLLOWING :				
				selectedPos = self.mCtrlBigList.getSelectedPosition( )
				if selectedPos >= 0 and self.mChannelList and selectedPos < len( self.mChannelList ) :
					channel = self.mChannelList[ selectedPos ]
					timer = self.GetTimerByChannel( channel )					

			elif self.mEPGMode == E_VIEW_CHANNEL :
				timer = self.GetTimerByChannel( self.mCurrentChannel )

		if timer :		
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Delete timer' ), MR_LANG( 'Are you sure you want to remove this timer?' ) )
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
		dialog.SetDialogProperty( MR_LANG( 'Delete all timers' ), MR_LANG( 'Are you sure you want to remove all your timers?' ) )
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
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'A keyword must be at least %d characters long' ) % MININUM_KEYWORD_SIZE )
					dialog.doModal( )
					return

				self.mEventBus.Deregister( self )	
				self.StopEPGUpdateTimer( )

				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_EPG_SEARCH ).SetText( keyword )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EPG_SEARCH )


				
				"""
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
					dialog.SetDialogProperty( MR_LANG( 'Search result' ), MR_LANG( 'No matched result found' ) )
					dialog.doModal( )
		 			return
		 		else :
					dialog = xbmcgui.Dialog( )
		 			select = dialog.select( MR_LANG( 'Select Event' ), searchList )

					if select >= 0 and select < len( searchList ) :
						LOG_TRACE( 'selectIndex=%d' %indexList[ select ] )
						LOG_TRACE( 'selectName=%s' %searchList[ select ] )
						if self.mEPGMode == E_VIEW_CHANNEL :
							self.mCtrlList.selectItem( indexList[ select ] )
						else:
							self.mCtrlBigList.selectItem( indexList[ select ] )
				"""

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
		
		if self.mEPGMode == E_VIEW_GRID :		

			gridMeta = self.mEPGHashTable.get( '%d:%d' %( self.mVisibleTopIndex + self.mVisibleFocusRow, self.mVisibleFocusCol ), None )
			if gridMeta and gridMeta.mEPG and gridMeta.mEPG.mEventId  != 0 :
				selectedEPG = gridMeta.mEPG
			
		
		elif self.mEPGMode == E_VIEW_CHANNEL :
			selectedPos = self.mCtrlList.getSelectedPosition( )
			if self.mEPGList == None:
				LOG_WARN( 'Has no EPG list' )
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
						elif self.HasOverlapped( startTime, endTime, timer.mStartTime + RECORD_ENDTIME_TRICK_MARGIN, timer.mStartTime + timer.mDuration - RECORD_ENDTIME_TRICK_MARGIN ) == True :
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
					if timer.mFromEPG and timer.mEventId > 0 :
						if  ( aEPG.mEventId == timer.mEventId ) and ( aEPG.mSid == timer.mSid ) and ( aEPG.mTsid  == timer.mTsid ) and ( aEPG.mOnid == timer.mOnid ) :
							LOG_TRACE( '------------------- found by event id -------------------------' )
							return timer

					else :
						if aEPG.mSid == timer.mSid and aEPG.mTsid == timer.mTsid and aEPG.mOnid == timer.mOnid :
							if self.HasOverlapped( startTime, endTime, timer.mStartTime + RECORD_ENDTIME_TRICK_MARGIN, timer.mStartTime + timer.mDuration - RECORD_ENDTIME_TRICK_MARGIN ) == True :
								LOG_TRACE( '------------------- found by manual timer-------------------------' )
								return timer
						
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		return None


	def HasOverlapped( self, aStartTime, aEndTime, aStartTime2, aEndTime2 ) :
		if ( aStartTime >= aStartTime2 and aStartTime <= aEndTime2 ) or \
			( aEndTime >= aStartTime2 and aEndTime <= aEndTime2 )  or \
			( aStartTime >= aStartTime2 and aEndTime <= aEndTime2 ) or \
			( aStartTime2 >= aStartTime and aEndTime2 <= aEndTime ) :
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

			if self.HasOverlapped( aStartTime, aEndTime, weeklyStartTime + RECORD_ENDTIME_TRICK_MARGIN, weeklyStartTime + weeklyTimer.mDuration - RECORD_ENDTIME_TRICK_MARGIN ) == True :
				LOG_TRACE( '------------------- found by weekly timer -------------------------' )
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
		if self.mEPGMode == E_VIEW_GRID :

			selectedPos = self.mCtrlGridChannelList.getSelectedPosition( )
			if selectedPos >= 0 and self.mChannelList and selectedPos < len( self.mChannelList ) :
				LOG_TRACE( '' )
				channel = self.mChannelList[ selectedPos ]

				self.StopEPGUpdateTimer( )
				if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
					self.mDataCache.Player_Stop( )
				self.mDataCache.Channel_SetCurrent( channel.mNumber, channel.mServiceType )
				self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
				self.mFirstTune = True				
				self.StartEPGUpdateTimer( )

			"""		
			channel = self.GetChannelByFocus( )
			currentChannel = self.mDataCache.Channel_GetCurrent( ) 
			if channel and currentChannel :
				if currentChannel.mNumber != channel.mNumber :
					self.StopEPGUpdateTimer( )				
					if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
						self.mDataCache.Player_Stop( )
					self.mDataCache.Channel_SetCurrent( channel.mNumber, channel.mServiceType )
					self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
					self.UpdateCurrentChannel( )
					self.mFirstTune = True
					self.RestartEPGUpdateTimer( )
			"""
		
		elif self.mEPGMode == E_VIEW_CHANNEL :
			#LOG_TRACE( '##################################### channel %d:%d' %(self.mSelectChannel.mNumber, self.mCurrentChannel.mNumber) )	
			if self.mSelectChannel == None or self.mCurrentChannel == None :
				LOG_ERR( 'Invalid channel' )
				return

			self.StopEPGUpdateTimer( )
			if self.mSelectChannel.mNumber != self.mCurrentChannel.mNumber :
				if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
					self.mDataCache.Player_Stop( )
				self.mDataCache.Channel_SetCurrent( self.mSelectChannel.mNumber, self.mSelectChannel.mServiceType )
				self.mCurrentChannel = self.mSelectChannel
				self.UpdateCurrentChannel( )				

			channel = self.mDataCache.Channel_GetCurrent( )
			self.mDataCache.Channel_SetCurrent( channel.mNumber, channel.mServiceType ) 
			self.mFirstTune = True
			self.RestartEPGUpdateTimer( )

		else : #self.mEPGMode == E_VIEW_CURRENT  or self.mEPGMode == E_VIEW_FOLLOWING
			selectedPos = self.mCtrlBigList.getSelectedPosition( )
			if selectedPos >= 0 and self.mChannelList and selectedPos < len( self.mChannelList ) :
				LOG_TRACE( '' )
				channel = self.mChannelList[ selectedPos ]
				"""
				if channel.mLocked == True :				
					if self.ShowPincodeDialog( ) == False :
						return

				else :
					if self.mDataCache.Get_Player_AVBlank( ) :
						self.mDataCache.Player_AVBlank( False )
				"""

				self.StopEPGUpdateTimer( )
				if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
					self.mDataCache.Player_Stop( )
				self.mDataCache.Channel_SetCurrent( channel.mNumber, channel.mServiceType )
				self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
				self.UpdateCurrentChannel( )
				self.mFirstTune = True				
				self.StartEPGUpdateTimer( )


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
		if self.mEPGMode == E_VIEW_GRID :	
			self.GridSetFocus( )
		else :
			self.UpdateEPGInfomation( )

		self.RestartEPGUpdateTimer( )


	def ToggleTVRadio( self ) :
		if not self.mDataCache.ToggleTVRadio( ) :
			return False

		self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( )
		self.mServiceType = self.mCurrentMode.mServiceType
		self.mChannelList = self.mDataCache.Channel_GetAllChannels( self.mServiceType )

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
		#self.mCurrentChannel.printdebug()
		self.mSelectChannel = self.mCurrentChannel			

		self.UpdateCurrentChannel( )
		self.UpdateAllEPGList( )

		return True


	def RecordByHotKey( self ) :
		selectedEPG = self.GetSelectedEPG( )

		timer = None

		if selectedEPG :
			timer = self.GetTimerByEPG( selectedEPG )
			if timer and timer.mTimerId > 0 :	# Edit Mode
				self.ShowManualTimer( selectedEPG, timer )
			else: # Add EPG Timer
				self.ShowEPGTimer( selectedEPG )

		else :
			if self.mEPGMode == E_VIEW_GRID :
				timer = self.GetTimerByFocus( )
		
			elif self.mEPGMode == E_VIEW_CURRENT or self.mEPGMode == E_VIEW_FOLLOWING :
				selectedPos = self.mCtrlBigList.getSelectedPosition( )
				if selectedPos >= 0 and self.mChannelList and selectedPos < len( self.mChannelList ) :
					channel = self.mChannelList[ selectedPos ]
					timer = self.GetTimerByChannel( channel )					

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

		self.mDataCache.SetPincodeDialog( True )
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_INPUT_PINCODE )
		dialog.SetTitleLabel( MR_LANG( 'Enter your PIN code' ) )
		dialog.doModal( )

		ret = False
		
		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			self.mDataCache.SetParentLock( False )
			if self.mDataCache.Get_Player_AVBlank( ) :
				self.mDataCache.Player_AVBlank( False )
				self.mDataCache.LoadVolumeBySetGUI( )

			ret = True

		self.mEventBus.Register( self )
		self.mDataCache.SetPincodeDialog( False )

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

		nextChannel = None

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
			LOG_ERR( 'Cannot find next channel' )

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
			index = count - 1 

		LOG_TRACE( 'Select Channel index=%d' %index )
		
		self.mEventBus.Deregister( self )
		self.StopEPGUpdateTimer( )

		prevChannel = None

		try :			
			prevChannel = self.mChannelList[ index ]
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )
			prevChannel = self.mChannelList[ 0 ]
			
		if prevChannel :
			self.mSelectChannel = prevChannel
			LOG_TRACE( 'Select Channel Number=%d' %self.mSelectChannel.mNumber )
			self.UpdateAllEPGList( )
		else: 
			LOG_ERR( 'Cannot find next channel' )

		self.mEventBus.Register( self )
		self.StartEPGUpdateTimer( 3 )


	def UpdateAllEPGList( self ) :
		self.mLock.acquire( )
		self.Flush( )
		self.mLock.release( )
	
		if self.mEPGMode == E_VIEW_GRID :
			self.UpdateGridChannelList( )
			normalize = int( self.mDataCache.Datetime_GetGMTTime( ) / E_GRID_HALF_HOUR )
			self.mShowingGMTTime = normalize * E_GRID_HALF_HOUR
			self.SetTimeline( )
			self.FocusCurrentChannel( )
			
			if self.mUpdateEPGInfomationTimer and self.mUpdateEPGInfomationTimer.isAlive( ) :
				self.mUpdateEPGInfomationTimer.cancel( )
			
			self.mUpdateEPGInfomationTimer = threading.Timer( 0.5, self.AsyncUpdateEPGInfomation )
			self.mUpdateEPGInfomationTimer.start( )
			return
			
		self.Load( )
		self.UpdateList( )
		self.UpdateSelectedChannel( )
		self.FocusCurrentChannel( )
		
		#time.sleep( 0.2 )
		self.ResetEPGInfomation( )

		if self.mUpdateEPGInfomationTimer and self.mUpdateEPGInfomationTimer.isAlive( ) :
			self.mUpdateEPGInfomationTimer.cancel( )
		
		self.mUpdateEPGInfomationTimer = threading.Timer( 0.5, self.AsyncUpdateEPGInfomation )
		self.mUpdateEPGInfomationTimer.start( )


	def AsyncUpdateEPGInfomation( self ) :
		if self.mEPGMode == E_VIEW_GRID :
			self.mLock.acquire( )
			self.mVisibleTopIndex = self.mCtrlGridChannelList.getOffsetPosition( )
			LOG_TRACE('LAEL98 TEST offsetPositon=%d' %self.mVisibleTopIndex )
			self.mVisibleFocusRow = self.mCtrlGridChannelList.getSelectedPosition( ) - self.mVisibleTopIndex					
			self.mVisibleFocusCol = 0
			self.mLock.release( )
			self.Flush( )
			self.Load( )
			self.UpdateList( )
			self.GridSetFocus( )

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

		#LOG_TRACE( 'Percent=%d' %percent )
		return percent


	def SetFocusList( self, aMode ) :
		if aMode == E_VIEW_GRID :	
			self.setFocusId( LIST_ID_GRID_CHANNEL )
			self.mLock.acquire( )			
			self.mVisibleTopIndex = self.mCtrlGridChannelList.getOffsetPosition( )			
			self.mVisibleFocusRow = self.mCtrlGridChannelList.getSelectedPosition( ) - self.mVisibleTopIndex		
			self.mVisibleFocusCol = 0
			self.mLock.release( )
			self.GridSetFocus( )			
		elif aMode == E_VIEW_CHANNEL :
			self.setFocusId( LIST_ID_COMMON_EPG )
		elif aMode == E_VIEW_CURRENT or aMode == E_VIEW_FOLLOWING :
			self.setFocusId( LIST_ID_BIG_EPG )
		else :
			LOG_ERR( 'SetFocusList fail' )


	def InitTimelineButtons( self ) :	
		for i in range( E_GRID_MAX_TIMELINE_COUNT ):
			self.mCtrlTimelineButtons.append( self.getControl(BUTTON_ID_BASE_TIME_LINE + i) )


	def InitGridEPGButtons( self ) :
		for i in range( E_GRID_MAX_BUTTON_COUNT ):
			ctrlButton = self.getControl(BUTTON_ID_BASE_GRID + i)
			ctrlButton.setVisible( False )
			self.mCtrlGridEPGButtonList.append( ctrlButton )

		for i in range( E_MAX_RECORD_COUNT ):
			ctrlButton = self.getControl(BUTTON_ID_BASE_RUNNNING_REC + i)
			ctrlButton.setVisible( False )
			self.mCtrlRecButtonList.append( ctrlButton )

		for i in range( E_GRID_SCHEDULED_BUTTON_COUNT ):
			ctrlButton = self.getControl(BUTTON_ID_BASE_SCHEDULED + i)
			ctrlButton.setVisible( False )
			self.mCtrlScheduledButtonList.append( ctrlButton )


	def SetTimeline( self ) :
		showingTime = self.mShowingGMTTime + self.mShowingOffset + self.mDataCache.Datetime_GetLocalOffset( )
		self.getControl( BUTTON_ID_SHOWING_DATE ).setLabel( TimeToString( showingTime, TimeFormatEnum.E_AW_DD_MM_YYYY ) )		

		for i in range( len( self.mCtrlTimelineButtons ) ):
			self.mCtrlTimelineButtons[i].setLabel( TimeToString( showingTime, TimeFormatEnum.E_HH_MM ) )
			showingTime = showingTime + self.mDeltaTime


	def UpdateTimeSeperator( self ) :
		if self.mEPGMode == E_VIEW_GRID :
			drawX = -1
			if self.mShowingOffset >= 0 and self.mShowingOffset <= self.mDeltaTime * E_GRID_MAX_TIMELINE_COUNT :
				showingTime = self.mShowingGMTTime + self.mShowingOffset + self.mDataCache.Datetime_GetLocalOffset( )
				currentTime = self.mDataCache.Datetime_GetLocalTime( )
				drawX = int( ( currentTime - showingTime )*self.mGridCanvasWidth /( self.mDeltaTime * E_GRID_MAX_TIMELINE_COUNT ) ) 

			LOG_TRACE('drawX=%d' %drawX )
			LOG_TRACE('EPGMode=%s' %self.getProperty( 'EPGMode' ) )
						
			if drawX >= 0 :
				#self.mCtrlGridTimeSeperator.setVisible( True )
				self.setProperty( 'EPGTimeSeperator', 'True' )
				self.mCtrlGridTimeSeperator.setPosition( drawX, 0 )
			else :
				self.setProperty( 'EPGTimeSeperator', 'False' )
				#self.mCtrlGridTimeSeperator.setVisible( False )			

		else :
			self.setProperty( 'EPGTimeSeperator', 'False' )		
			#self.mCtrlGridTimeSeperator.setVisible( False )


	def GridControlLeft( self ) :
		LOG_TRACE('TEST focusId=%d' %self.getFocusId() )				
		LOG_TRACE('self.mVisibleFocusRow=%d self.mVisibleFocusCol=%d' %( self.mVisibleFocusRow, self.mVisibleFocusCol ) )			
		gridMeta = self.mEPGHashTable.get( '%d:%d' %( self.mVisibleTopIndex + self.mVisibleFocusRow, self.mVisibleFocusCol - 1 ), None )
		if gridMeta :
			LOG_TRACE('gridMeta.mId=%d' %gridMeta.mId )		
			self.mLock.acquire( )
			self.mVisibleFocusCol -= 1
			self.mLock.release( )
			self.GridSetFocus( )
		else :
			if self.mShowingOffset > 0 :
				self.mLock.acquire( )
				self.mVisibleFocusCol = 0
				self.mShowingOffset -= self.mDeltaTime * E_GRID_MAX_TIMELINE_COUNT
				self.mLock.release( )				
				self.SetTimeline( )
				self.Flush( )
				self.Load( )
				self.UpdateList( )
				self.GridSetFocus( )
			else :
				self.setFocusId( GROUP_ID_LEFT_SLIDE )


	def GridControlRight( self ) :
		LOG_TRACE('TEST focusId=%d' %self.getFocusId() )					
		LOG_TRACE('self.mVisibleFocusRow=%d self.mVisibleFocusCol=%d' %( self.mVisibleFocusRow, self.mVisibleFocusCol ) )			
		gridMeta = self.mEPGHashTable.get( '%d:%d' %( self.mVisibleTopIndex + self.mVisibleFocusRow, self.mVisibleFocusCol + 1 ), None )
		if gridMeta :
			LOG_TRACE('gridMeta.mId=%d' %gridMeta.mId )
			self.mLock.acquire( )			
			self.mVisibleFocusCol += 1
			self.mLock.release( )			
			self.GridSetFocus( )
		else :
			if ( self.mShowingOffset + self.mDeltaTime * E_GRID_MAX_TIMELINE_COUNT ) < E_SEVEN_DAYS_EPG_TIME :
				self.mLock.acquire( )
				self.mVisibleFocusCol = 0
				self.mShowingOffset += self.mDeltaTime * E_GRID_MAX_TIMELINE_COUNT
				self.mLock.release( )
				LOG_TRACE( 'self.mShowingOffset=%d' %self.mShowingOffset )
				self.SetTimeline( )
				self.Flush( )				
				self.Load( )
				self.UpdateList( )
				self.GridSetFocus( )


	def GridControlUp( self ) :
		LOG_TRACE('self.mVisibleTopIndex=%d self.mVisibleFocusRow=%d self.mVisibleFocusCol=%d' %( self.mVisibleTopIndex, self.mVisibleFocusRow, self.mVisibleFocusCol ) )
		self.mLock.acquire( )
		self.mVisibleTopIndex = self.mCtrlGridChannelList.getOffsetPosition( )		
		self.mVisibleFocusRow = self.mCtrlGridChannelList.getSelectedPosition( ) - self.mVisibleTopIndex
		self.mVisibleFocusCol = 0
		self.mLock.release( )
		gridMeta = self.mEPGHashTable.get( '%d:%d' %( self.mVisibleTopIndex + self.mVisibleFocusRow , 0 ), None )
		if gridMeta :
			LOG_TRACE('gridMeta.mId=%d' %gridMeta.mId )
			self.GridSetFocus( )
		else :
			self.Flush( )
			self.Load( )
			self.UpdateList( )
			self.GridSetFocus( )


	def GridControlDown( self ) :
		LOG_TRACE('self.mVisibleTopIndex=%d self.mVisibleFocusRow=%d self.mVisibleFocusCol=%d' %( self.mVisibleTopIndex, self.mVisibleFocusRow, self.mVisibleFocusCol ) )
		self.mLock.acquire( )
		self.mVisibleTopIndex = self.mCtrlGridChannelList.getOffsetPosition( )		
		self.mVisibleFocusRow = self.mCtrlGridChannelList.getSelectedPosition( ) - self.mVisibleTopIndex
		self.mVisibleFocusCol = 0
		self.mLock.release( )

		gridMeta = self.mEPGHashTable.get( '%d:%d' %( self.mVisibleTopIndex + self.mVisibleFocusRow, 0 ), None )
		if gridMeta :
			LOG_TRACE('gridMeta.mId=%d' %gridMeta.mId )
			self.GridSetFocus( )
		else :
			self.Flush( )
			self.Load( )
			self.UpdateList( )
			self.GridSetFocus( )


	def GridControlPageUp( self ) :
		self.mLock.acquire( )
		self.mVisibleTopIndex = self.mCtrlGridChannelList.getOffsetPosition( )
		LOG_TRACE('LAEL98 TEST offsetPositon=%d' %self.mVisibleTopIndex )
		self.mVisibleFocusRow = self.mCtrlGridChannelList.getSelectedPosition( ) - self.mVisibleTopIndex		
		self.mVisibleFocusCol = 0
		self.mLock.release( )
		self.Flush( )
		self.Load( )
		self.UpdateList( )
		self.GridSetFocus( )


	def GridControlPageDown( self ) :
		self.mLock.acquire( )
		self.mVisibleTopIndex = self.mCtrlGridChannelList.getOffsetPosition( )
		LOG_TRACE('LAEL98 TEST offsetPositon=%d' %self.mVisibleTopIndex )
		self.mVisibleFocusRow = self.mCtrlGridChannelList.getSelectedPosition( ) - self.mVisibleTopIndex		
		self.mVisibleFocusCol = 0
		self.mLock.release( )
		self.Flush( )		
		self.Load( )
		self.UpdateList( )
		self.GridSetFocus( )


	def GridSetFocus( self ) :
		gridMeta = self.mEPGHashTable.get( '%d:%d' %(self.mVisibleTopIndex +  self.mVisibleFocusRow, self.mVisibleFocusCol ), None )
		#LOG_TRACE( 'LAEL98 TEST Row=%d Col=%d' %( self.mVisibleFocusRow, self.mVisibleFocusCol ) )

		if gridMeta :
			button = self.getControl( gridMeta.mId )
			if button :
				( x, y ) = button.getPosition( )
				w = button.getWidth( )
				h = button.getHeight( )
				#LOG_TRACE( 'LAEL98 TEST [%d,%d,%d,%d]' %(x,y,w,h) )
				self.mFocusButton.setPosition( x, y )
				self.mFocusButton.setWidth( w )
				self.mFocusButton.setHeight( h )
				self.mFocusButton.setVisible( True )				
			else :
				self.mFocusButton.setVisible( False )				
		else :
			self.mFocusButton.setVisible( False )
				
		if self.mChannelList == None or len( self.mChannelList ) <= 0 :
			self.mCtrlGridEPGInfo.setLabel(' ')
			self.setProperty( 'GridSetPocusIndex', '0' )
			return
		else :
			self.setProperty( 'GridSetPocusIndex', '%d'	%(self.mVisibleTopIndex +  self.mVisibleFocusRow ) )
		
		gridMeta = self.mEPGHashTable.get( '%d:%d' %( self.mVisibleTopIndex + self.mVisibleFocusRow, self.mVisibleFocusCol ), None )
		channel = None
		if self.mVisibleTopIndex + self.mVisibleFocusRow >= 0 and self.mVisibleTopIndex + self.mVisibleFocusRow < len( self.mChannelList ) :
			channel = self.mChannelList[self.mVisibleTopIndex + self.mVisibleFocusRow]
		else :
			self.mCtrlGridEPGInfo.setLabel(' ')

		if gridMeta :
			LOG_TRACE('gridMeta.mId=%d' %gridMeta.mId )
			if gridMeta.mEPG and gridMeta.mEPG.mEventId >  0  :
				localOffset = self.mDataCache.Datetime_GetLocalOffset( )
				start  = gridMeta.mEPG.mStartTime + localOffset
				self.mCtrlGridEPGInfo.setLabel('%04d %s (%s~%s) %s' %( channel.mNumber, channel.mName, TimeToString( start , TimeFormatEnum.E_AW_HH_MM ), TimeToString( start + gridMeta.mEPG.mDuration, TimeFormatEnum.E_HH_MM ), gridMeta.mEPG.mEventName  ) )
			else :
				self.mCtrlGridEPGInfo.setLabel(' %04d %s' %( channel.mNumber, channel.mName) )			
		else :
			LOG_ERR( 'cannot find control (%d,%d)' %(self.mVisibleFocusRow,self.mVisibleFocusCol) )
			gridMeta = self.mEPGHashTable.get( '%d:%d' %( self.mVisibleTopIndex + self.mVisibleFocusRow, 0 ), None )
			if gridMeta :
				LOG_TRACE('gridMeta.mId=%d' %gridMeta.mId )
				if gridMeta.mEPG and gridMeta.mEPG.mEventId >  0  :
					localOffset = self.mDataCache.Datetime_GetLocalOffset( )
					start  = gridMeta.mEPG.mStartTime + localOffset
					self.mCtrlGridEPGInfo.setLabel('%04d %s (%s~%s) %s' %( channel.mNumber, channel.mName, TimeToString( start , TimeFormatEnum.E_AW_HH_MM ), TimeToString( start + gridMeta.mEPG.mDuration, TimeFormatEnum.E_HH_MM ), gridMeta.mEPG.mEventName  ) )
				else :
					self.mCtrlGridEPGInfo.setLabel(' %04d %s' %( channel.mNumber, channel.mName) )			
				self.mVisibleFocusCol = 0					

			else :
				self.mVisibleFocusRow = 0
				self.mVisibleFocusCol = 0
				self.mCtrlGridEPGInfo.setLabel(' ' )

		#cas image
		if channel.mIsCA :
			self.mCtrlGridCas.setImage('IconCas.png')
		else :
			self.mCtrlGridCas.setImage('')

		self.UpdateSelcetedPosition( )
		
		"""
		#index
		selectPosition = self.mVisibleTopIndex + self.mVisibleFocusRow + 1
		self.setProperty( 'GridSelectedPosition', '%d' %selectPosition )
		self.setProperty( 'GridNumItems', '%d' %(totalCount) )

		totalPage = int( totalCount/E_GRID_MAX_ROW_COUNT )
		if ( totalCount%E_GRID_MAX_ROW_COUNT )  != 0 :
			totalPage = totalPage +1
		self.setProperty( 'GridNumPages', '%d' %totalPage )
		
		currentPage = int(self.mVisibleTopIndex/E_GRID_MAX_ROW_COUNT) + 1
		if self.mVisibleTopIndex == totalCount - E_GRID_MAX_ROW_COUNT :
			if selectPosition > currentPage*E_GRID_MAX_ROW_COUNT :
				currentPage = currentPage + 1
		self.setProperty( 'GridCurrentPage', '%d' %currentPage )
		#self.setProperty( 'GridSetPocusIndex', '%d' %( self.mVisibleFocusRow + self.mVisibleFocusCol ) )
		"""


	def GridUpdateTimer( self ) :

		localOffset = self.mDataCache.Datetime_GetLocalOffset( )
		drawableTime =  self.mDeltaTime * E_GRID_MAX_TIMELINE_COUNT		
		recCount = 0
		timerCount = 0
		#not runningTimer
		if self.mTimerList and len( self.mTimerList ) > 0  :
			try :	
				for i in range( len( self.mTimerList ) ) :
					timer =  self.mTimerList[i]
					start = timer.mStartTime - localOffset
					end = start + timer.mDuration
					
					for j in range( E_GRID_MAX_ROW_COUNT ) :
						gridMeta = self.mEPGHashTable.get( '%d:%d' %(self.mVisibleTopIndex + j,0 ), None )
						if gridMeta == None :
							break

						if j >=  len(  self.mChannelList ) :
							break

						channel = self.mChannelList[gridMeta.mChannelIndex]
						if channel and channel.mSid == timer.mSid and channel.mTsid == timer.mTsid and channel.mOnid == timer.mOnid :
							#find
							isRunning = self.IsRunningTimer( timer )
							if isRunning :
								if timer.mFromEPG :
									start = start  -self.mPreRecTime
									end = end + self.mPostRecTime

							if start < self.mShowingGMTTime + self.mShowingOffset :
								start  = self.mShowingGMTTime + self.mShowingOffset

							if end > self.mShowingGMTTime + self.mShowingOffset + self.mDeltaTime * E_GRID_MAX_TIMELINE_COUNT :
								end = self.mShowingGMTTime + self.mShowingOffset + self.mDeltaTime * E_GRID_MAX_TIMELINE_COUNT
								
							offsetX = int( ( start - self.mShowingGMTTime - self.mShowingOffset )*self.mGridCanvasWidth/drawableTime )
							offsetY = gridMeta.mRow * ( self.mGridItemHeight + self.mGridItemGap )


							LOG_TRACE( 'start=%s' %TimeToString( start + localOffset, TimeFormatEnum.E_HH_MM )	)
							LOG_TRACE( 'end=%s' %TimeToString( end + localOffset, TimeFormatEnum.E_HH_MM )	)					
							
							drawWidth = int( ( end-start ) * self.mGridCanvasWidth/drawableTime ) 

							LOG_TRACE( 'offsetX=%d offsetY=%d width=%d' %( offsetX, offsetY, drawWidth ) )

							if drawWidth <= 0 :
								LOG_ERR( 'drawWidth is too small' )
								break

							ctrlButton = None
							if isRunning and recCount < len( self.mCtrlRecButtonList ) :
								ctrlButton = self.mCtrlRecButtonList[recCount]
								recCount += 1
							
							elif recCount < len( self.mCtrlScheduledButtonList ) :
								ctrlButton = self.mCtrlScheduledButtonList[timerCount]
								timerCount += 1

							if ctrlButton :
								ctrlButton.setPosition( offsetX, offsetY )
								ctrlButton.setWidth( drawWidth  )					
								ctrlButton.setVisible( True )

			except Exception, ex :
				LOG_ERR( "Exception %s" %ex )

		for i in range( len( self.mCtrlRecButtonList ) - recCount ) :
			self.mCtrlRecButtonList[recCount + i].setVisible( False )

		for i in range( len( self.mCtrlScheduledButtonList ) - timerCount ) :
			self.mCtrlScheduledButtonList[timerCount + i].setVisible( False )		


	def GetTimerByFocus( self ) :
		focusId = self.getFocusId( )

		if focusId < BUTTON_ID_BASE_GRID or focusId >= BUTTON_ID_BASE_GRID + E_GRID_MAX_BUTTON_COUNT :
			return None
		
		for i in range( E_GRID_MAX_ROW_COUNT ) :
			for j in range( E_GRID_MAX_COL_COUNT ) :
				gridMeta = self.mEPGHashTable.get( '%d:%d' %(self.mVisibleTopIndex + i, j ), None )
				if gridMeta == None :
					break

				if gridMeta.mId == focusId :
					return self.GetTimerByEPG( gridMeta.mEPG )

		return None


	def UpdateFootor( self ) :
		if self.mChannelList == None :
			self.setProperty( 'EPGFootor', 'False' )
		else:
			self.setProperty( 'EPGFootor', 'True' )
		
