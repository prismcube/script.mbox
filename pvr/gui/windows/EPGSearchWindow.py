from pvr.gui.WindowImport import *
from elisinterface.ElisClass import *

E_EPG_SEARC_BASE_ID				=  WinMgr.WIN_ID_EPG_SEARCH * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID
E_EPG_WINDOW_BASE_ID			=  WinMgr.WIN_ID_EPG_WINDOW * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID

BUTTON_ID_EPG_MODE				= E_EPG_WINDOW_BASE_ID + 100
LIST_ID_BIG_EPG					= E_BASE_WINDOW_ID + 3510

LABEL_ID_TIME					= E_EPG_WINDOW_BASE_ID + 300
LABEL_ID_DATE					= E_EPG_WINDOW_BASE_ID + 301
LABEL_ID_DURATION				= E_EPG_WINDOW_BASE_ID + 302
LABEL_ID_EVENT_NAME				= E_EPG_WINDOW_BASE_ID + 303


CONTEXT_GO_PARENT				= 1
CONTEXT_ADD_TIMER				= 2
CONTEXT_EDIT_TIMER				= 3
CONTEXT_DELETE_TIMER			= 4
CONTEXT_SEARCH					= 5
CONTEXT_EXTEND_INFOMATION		= 6


class EPGSearchWindow( BaseWindow ) :

	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mText	= None	
		self.mLock = thread.allocate_lock( )
	
	def onInit( self ) :
		self.SetFrontdisplayMessage( MR_LANG( 'EPG Search' ) )
		self.mWinId = xbmcgui.getCurrentWindowId( )

		#self.getControl( E_SETTING_MINI_TITLE ).setLabel( MR_LANG( 'Timer' ) )
		self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'EPG' ), MR_LANG( 'Search' ) ) )
		self.mListItems = []
		self.mTimerList = []
		self.mEPGList = []		

		self.mCtrlEPGMode = self.getControl( BUTTON_ID_EPG_MODE )
		self.mCtrlBigList = self.getControl( LIST_ID_BIG_EPG )
		self.mCtrlBigList.reset()		

		self.mCtrlTimeLabel = self.getControl( LABEL_ID_TIME )
		self.mCtrlDateLabel = self.getControl( LABEL_ID_DATE )
		self.mCtrlDurationLabel = self.getControl( LABEL_ID_DURATION )
		self.mCtrlEPGDescription = self.getControl( LABEL_ID_EVENT_NAME )				


		self.mCtrlTimeLabel.setLabel( '' )
		self.mCtrlDateLabel.setLabel( '' )
		self.mCtrlDurationLabel.setLabel( '' )
		self.ResetEPGInfomation( )

		self.UpdateViewMode( )
		self.SetSingleWindowPosition( E_EPG_SEARC_BASE_ID )
		self.SetPipScreen( )

		self.mCtrlEPGMode.setLabel( '%s' %MR_LANG( 'Go Back' ) )
		
		self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( )
		self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
		LOG_TRACE( 'ZeppingMode(%d,%d,%d)' %( self.mCurrentMode.mServiceType, self.mCurrentMode.mMode, self.mCurrentMode.mSortingMode ) )
		#self.mChannelList = self.mDataCache.Channel_GetList( )
		self.mChannelList = self.mDataCache.Channel_GetAllChannels( self.mCurrentMode.mServiceType )
		self.mChannelListHash = {}

		LOG_TRACE( "ChannelList=%d" %len( self.mChannelList ) )

		if self.mChannelList :
			for channel in self.mChannelList :
				self.mChannelListHash[ '%d:%d:%d' %( channel.mSid, channel.mTsid, channel.mOnid) ] = channel
	
		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		self.mGMTTime = 0

		self.Load( )
		self.UpdateList( )

		self.mEventBus.Register( self )	
		self.mInitialized = True
		self.setFocusId( LIST_ID_BIG_EPG )

		self.UpdateEPGInfomation( )		


	def onAction( self, aAction ) :
		self.GetFocusId( )
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		#LOG_TRACE('onAction=%d' %actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR:
			focusId = self.getFocusId( )		
			if focusId  == BUTTON_ID_EPG_MODE	: 
				self.setFocusId( LIST_ID_BIG_EPG )			
			else:
				self.Close( )
	
		elif actionId == Action.ACTION_CONTEXT_MENU:
			self.ShowContextMenu( )

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN :
			if self.mFocusId == LIST_ID_BIG_EPG :
				self.UpdateEPGInfomation( )

		elif actionId == Action.ACTION_PAGE_UP  or actionId == Action.ACTION_PAGE_DOWN :
			if self.mFocusId == LIST_ID_BIG_EPG:
				self.UpdateEPGInfomation( )

		elif actionId == Action.ACTION_MBOX_RECORD :
			isAvail, isConfiguration = self.HasDefaultRecordPath( )
			if isAvail != E_DEFAULT_RECORD_PATH_RESERVED :
				if isConfiguration :
					self.Close( )
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).SetMoveConfigureToAddVolume( )
				return

			selectedEPG = self.GetSelectedEPG( )
			if selectedEPG  :
				timer = self.GetTimerByEPG( selectedEPG )
				if timer :
					self.DoContextAction( CONTEXT_EDIT_TIMER ) 				
				else :
					self.DoContextAction( CONTEXT_ADD_TIMER ) 

		elif actionId == Action.ACTION_STOP :
			self.DoContextAction( CONTEXT_DELETE_TIMER ) 

		elif actionId == Action.ACTION_MBOX_TEXT :
			self.DoContextAction( CONTEXT_SEARCH ) 		
		

	def onClick( self, aControlId ) :
		LOG_TRACE( 'aControlId=%d' %aControlId )
		if aControlId == BUTTON_ID_EPG_MODE :
			self.Close( )


	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			if aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
				LOG_TRACE( 'Record status chanaged' )
				self.UpdateList( True )

			elif aEvent.getName( ) == ElisPMTReceivedEvent.getName( ) :
				#LOG_TRACE( "--------- received ElisPMTReceivedEvent-----------" )
				self.UpdatePropertyByCacheData( E_XML_PROPERTY_TELETEXT )
				self.UpdatePropertyByCacheData( E_XML_PROPERTY_SUBTITLE )
				self.UpdatePropertyByCacheData( E_XML_PROPERTY_DOLBYPLUS )

			elif aEvent.getName( ) == ElisEventChannelDBUpdate.getName( ) :
				pass
				#self.UpdateChannelByDBUpdateEvent( aEvent )


	def SetText( self, aText=None ) :
		self.mText = aText
		LOG_TRACE( 'TEXT=%s' %self.mText )


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.SetVideoRestore( )

		self.mChannelList = []
		self.mChannelListHash = {}
		self.mEPGList = []
		
		WinMgr.GetInstance( ).CloseWindow( )


	def UpdateChannelByDBUpdateEvent( self, aEvent = None ) :
		if not aEvent :
			LOG_TRACE( 'aEvent is none' )
			return

		if aEvent.mUpdateType == 0 :
			#ToDO : All updated db, reload channelList
			pass
			return

		try :
			if self.mEPGList == None or len ( self.mEPGList ) <= 0 :
				return
			if self.mChannelList == None or len ( self.mChannelList ) <= 0 :
				return

			channel = None
			selectedPos = self.mCtrlBigList.getSelectedPosition( )
			if selectedPos >= 0 and selectedPos < len( self.mChannelList ) :
				channel = self.mChannelList[selectedPos]

			self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
			if channel and self.mCurrentChannel and channel.mNumber == self.mCurrentChannel.mNumber :
				UpdateCASInfo( self, self.mCurrentChannel )
				hashkey = '%s:%s:%s'% ( self.mCurrentChannel.mSid, self.mCurrentChannel.mTsid, self.mCurrentChannel.mOnid )
				self.mChannelList[selectedPos] = self.mCurrentChannel
				self.mChannelListHash[hashkey] = self.mCurrentChannel

		except Exception, e :
			LOG_ERR( 'Exception[%s] Failed to update - ElisEventChannelDBUpdate'% e )


	def UpdateViewMode( self ) :
		self.setProperty( 'EPGMode', 'search' )


	def Flush( self ) :
		self.mEPGList = []	


	def Load( self ) :

		LOG_TRACE( '----------------------------------->' )

		if len( self.mText ) < MININUM_KEYWORD_SIZE : 
			self.mEPGList = None
			return

		self.mEPGList = []

		try :

			epgFilterList = []

			epgFilter = ElisIEPGFilter( )
			epgFilter.mFilterType = ElisEnum.E_TYPE_TEXT_SEARCH
			epgFilter.mTextSearchType = ElisEnum.E_TEXT_SEARCH_ALL
			epgFilter.mText = self.mText
			epgFilterList.append( epgFilter )

			LOG_TRACE( 'epgFilter.mText=%s' %epgFilter.mText )

			tempList = self.mCommander.EPGEvent_GetFilteredEvent( epgFilterList )

			if tempList :
				for i in range( len( tempList ) ) :
					epgEvent = tempList[i]
					channel = self.GetChannelByIDs( epgEvent.mSid, epgEvent.mTsid, epgEvent.mOnid )
					if channel :
						self.mEPGList.append( epgEvent )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		if self.mEPGList == None or len ( self.mEPGList ) <= 0 :
			self.mEPGList = None
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'No results found' ), MR_LANG( 'Could not find any results for that search') )
			dialog.doModal( )
			return
		"""
		else :
			for i in range( len( self.mEPGList ) ) :
				epgEvent = self.mEPGList[i]
				LOG_ERR( 'id=%d name=%s' %(epgEvent.mEventId, epgEvent.mEventName ) )
				LOG_ERR( 'Start : %s' % (TimeToString( epgEvent.mStartTime + self.mDataCache.Datetime_GetLocalOffset( ), TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) ) )
				LOG_ERR( 'End :  %s' % (TimeToString( epgEvent.mStartTime+epgEvent.mDuration+self.mDataCache.Datetime_GetLocalOffset( ), TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) ) )
		"""		
		

		LOG_TRACE( 'self.mEPGList COUNT=%d' %len( self.mEPGList ) )
		

	@SetLock
	def UpdateList( self, aUpdateOnly=False ) :

		if self.mEPGList == None :
			self.mCtrlBigList.reset( )
			return

		if aUpdateOnly == False or self.mListItems == None:
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
			
	
		self.LoadTimerList( )

		try :
			self.mDebugStart = time.time( )		

			currentTime = self.mDataCache.Datetime_GetLocalTime( )

			strNoEvent = MR_LANG( 'No event' )

			LOG_TRACE( 'len( self.mEPGLis=%d' %len( self.mEPGList ) )		
			
			for i in range( len( self.mEPGList ) ) :
				epgEvent = self.mEPGList[i]
				channel = self.GetChannelByIDs( epgEvent.mSid, epgEvent.mTsid, epgEvent.mOnid )

				if channel == None :
					tempChannelNumber = '%04d' %0
					tempChannelName = '%s' %epgEvent.mEventName
				else :
					tempChannelNumber = '%04d' %channel.mNumber
					tempChannelName = '%s' %channel.mName

				if aUpdateOnly == False :
					listItem = xbmcgui.ListItem( tempChannelNumber, tempChannelName )
				else :
					listItem = self.mListItems[i]
					listItem.setLabel( tempChannelNumber )
					listItem.setLabel2( tempChannelName )

				epgStart = epgEvent.mStartTime + self.mLocalOffset
				tempName = '%s~%s' % ( TimeToString( epgStart, TimeFormatEnum.E_HH_MM ), TimeToString( epgStart + epgEvent.mDuration, TimeFormatEnum.E_HH_MM ) )
				listItem.setProperty( 'EPGName', epgEvent.mEventName )				
				listItem.setProperty( 'StartTime', tempName )
				listItem.setProperty( 'Duration', '' )
				listItem.setProperty( 'HasEvent', 'true' )
				listItem.setProperty( 'ViewTimer', 'None' )
				#listItem.setProperty( 'Percent', '%s' %self.CalculateProgress( currentTime, epgStart, epgEvent.mDuration  ) )
				timer = self.GetTimerByEPG( epgEvent )

				if timer :
					if self.IsRunningTimer( timer.mTimerId ) == True :
						listItem.setProperty( 'TimerType', 'Running' )

					else :
						listItem.setProperty( 'TimerType', 'Schedule' )

				else :
					listItem.setProperty( 'TimerType', 'None' )

				if E_V1_2_APPLY_VIEW_TIMER :
					hasTimer = '%s'% self.GetViewTimerByEPG( epgEvent, None )
					listItem.setProperty( 'ViewTimer', hasTimer )

				if E_USE_CHANNEL_LOGO == True :
					if channel :
						logo = '%s_%s' %(channel.mCarrier.mDVBS.mSatelliteLongitude, channel.mSid )
						listItem.setProperty( 'ChannelLogo', self.mChannelLogo.GetLogo( logo, self.mCurrentMode.mServiceType ) )
					else :
						listItem.setProperty( 'ChannelLogo', self.mChannelLogo.GetDefaultLogo(  self.mCurrentMode.mServiceType )  )					

				#ListItem.PercentPlayed
				if aUpdateOnly == False :
					self.mListItems.append( listItem )

			if aUpdateOnly == False :
				self.mCtrlBigList.addItems( self.mListItems )

			self.mDebugEnd = time.time( )
			print 'epg loading test =%s' %( self.mDebugEnd  - self.mDebugStart )

			xbmc.executebuiltin( 'container.refresh' )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def UpdateSelcetedPosition( self ) :
		if self.mEPGList == None :
			self.setProperty( 'SelectedPosition', '0' )
			return

		selectedPos = self.mCtrlBigList.getSelectedPosition( )

		self.setProperty( 'SelectedPosition', '%d' %( selectedPos+1 ) )

		channel = None
		if selectedPos >= 0 and selectedPos < len( self.mChannelList ) :
			channel = self.mChannelList[selectedPos]

		if channel :
			UpdateCASInfo( self, channel )


	def UpdateEPGInfomation( self ) :
		self.UpdateSelcetedPosition( )
		
		epg = self.GetSelectedEPG( )
		try :
			if epg :
				self.mCtrlTimeLabel.setLabel( '%s~%s' % ( TimeToString( epg.mStartTime + self.mLocalOffset, TimeFormatEnum.E_HH_MM ), TimeToString( epg.mStartTime + self.mLocalOffset+ epg.mDuration, TimeFormatEnum.E_HH_MM ) ) )
				self.mCtrlDateLabel.setLabel( '%s' % TimeToString( epg.mStartTime + self.mLocalOffset, TimeFormatEnum.E_AW_DD_MM_YYYY ) )
				self.mCtrlDurationLabel.setLabel( '%d%s' %( ( epg.mDuration / 60 ), MR_LANG( 'min(s)' ) ) )

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

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def	ResetEPGInfomation( self ) :
		self.mCtrlTimeLabel.setLabel( '' )
		self.mCtrlDateLabel.setLabel( '' )
		self.mCtrlDurationLabel.setLabel( '' )
		self.mCtrlEPGDescription.setText( '' )

		self.setProperty( E_XML_PROPERTY_TELETEXT, E_TAG_FALSE )
		self.setProperty( E_XML_PROPERTY_SUBTITLE, E_TAG_FALSE )
		self.setProperty( E_XML_PROPERTY_DOLBY,    E_TAG_FALSE )
		self.setProperty( E_XML_PROPERTY_DOLBYPLUS,E_TAG_FALSE )
		self.setProperty( E_XML_PROPERTY_HD,       E_TAG_FALSE )



	def UpdatePropertyByCacheData( self, aPropertyID = None, aValue = False ) :

		epgEvent = self.GetSelectedEPG( )		
		if epgEvent :
			channel = self.GetChannelByIDs( epgEvent.mSid, epgEvent.mTsid, epgEvent.mOnid )
			if channel :	
				pmtEvent = self.mDataCache.GetCurrentPMTEvent( channel )
				if pmtEvent :
					return UpdatePropertyByCacheData( self, pmtEvent, aPropertyID )

		return False


	@RunThread
	def CurrentTimeThread( self ) :
		pass


	def UpdateLocalTime( self ) :
		pass


	def ShowContextMenu( self ) :
		context = []

		context.append( ContextItem( MR_LANG( 'Back to previous page' ), CONTEXT_GO_PARENT ) )

		selectedEPG = self.GetSelectedEPG( )		

		if selectedEPG  :
			timer = self.GetTimerByEPG( selectedEPG )
			if timer :
				context.append( ContextItem( MR_LANG( 'Edit timer' ), CONTEXT_EDIT_TIMER ) )
				context.append( ContextItem( MR_LANG( 'Delete timer' ), CONTEXT_DELETE_TIMER ) )				
			else :
				context.append( ContextItem( MR_LANG( 'Add timer' ), CONTEXT_ADD_TIMER ) )		

		context.append( ContextItem( MR_LANG( 'Search' ), CONTEXT_SEARCH ) )

		if selectedEPG  :		
			context.append( ContextItem( MR_LANG( 'Extend information' ), CONTEXT_EXTEND_INFOMATION ) )
		context.append( ContextItem( MR_LANG( 'Hotkeys' ), CONTEXT_ACTION_HOTKEYS ) )

		dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
		dialog.doModal( )
		
		contextAction = dialog.GetSelectedAction( )
		self.DoContextAction( contextAction ) 


	def DoContextAction( self, aContextAction ) :
		LOG_TRACE( 'aContextAction=%d' %aContextAction )

		if aContextAction == CONTEXT_GO_PARENT :
			self.Close( )

		elif aContextAction == CONTEXT_ADD_TIMER :
			self.ShowEPGTimer( )

		elif aContextAction == CONTEXT_EDIT_TIMER :
			self.ShowEditTimer( )

		elif aContextAction == CONTEXT_DELETE_TIMER :
			self.ShowDeleteConfirm( )

		elif aContextAction == CONTEXT_SEARCH :
			self.ShowSearchDialog( )

		elif aContextAction == CONTEXT_EXTEND_INFOMATION :
			self.ShowDetailInfomation( )

		elif aContextAction == CONTEXT_ACTION_HOTKEYS :
			self.ShowHotkeys( )


	def ShowEPGTimer( self ) :
		LOG_TRACE( 'ShowEPGTimer' )

		if not HasAvailableRecordingHDD( ) :
			return

		if not WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).CheckDMXInfo( ) :
			return -1

		selectedEPG = self.GetSelectedEPG( )

		if selectedEPG == None :
			return
			
		try :		
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_ADD_TIMER )
			dialog.SetEPG( selectedEPG )
			dialog.doModal( )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		try :
			if dialog.IsOK() == E_DIALOG_STATE_YES :
				ret = self.mDataCache.Timer_AddEPGTimer( True, 0, selectedEPG )
				LOG_ERR( 'Conflict ret=%s' %ret )
				if ret and (ret[0].mParam == -1 or ret[0].mError == -1) :
					RecordConflict( ret )
					return

			else :
				LOG_TRACE( '' )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		self.UpdateList( True )


	def ShowEditTimer( self ) :

		selectedEPG = self.GetSelectedEPG( )

		if selectedEPG == None :
			return

		timer = self.GetTimerByEPG( selectedEPG )

		if timer == None :
			return

		try :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_ADD_MANUAL_TIMER )
			dialog.SetTimer( timer, self.IsRunningTimer( timer.mTimerId ) )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_ERROR :
				if dialog.GetConflictTimer( ) == None :
					infoDialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					infoDialog.SetDialogProperty( MR_LANG( 'Error' ), dialog.GetErrorMessage( ) )
					infoDialog.doModal( )
				else :
					RecordConflict( dialog.GetConflictTimer( ) )

			self.UpdateList( True )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def ShowDeleteConfirm( self ) :
		LOG_TRACE( 'ShowDeleteConfirm' )

		selectedEPG = self.GetSelectedEPG( )

		if selectedEPG == None :
			return

		timer = self.GetTimerByEPG( selectedEPG )

		if timer == None :
			return

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( MR_LANG( 'Delete Timer' ), MR_LANG( 'Are you sure you want to delete this timer?'  ) )
		dialog.doModal( )

		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			self.mDataCache.Timer_DeleteTimer( timer.mTimerId )
			self.UpdateList( True )


	def ShowSearchDialog( self ) :
		try :
			kb = xbmc.Keyboard( '', MR_LANG( 'Enter Search Keywords' ), False )
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
				self.SetText( keyword )
				self.OpenBusyDialog( )
				self.Load( )
				self.UpdateList( )
				self.CloseBusyDialog( )				
				self.UpdateEPGInfomation( )						
				self.mEventBus.Register( self )				

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def ShowDetailInfomation( self ) :
		LOG_TRACE( 'ShowDetailInfomation' )

		self.mEventBus.Deregister( self )
		epg = self.GetSelectedEPG( )

		if epg :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_EXTEND_EPG )
			dialog.SetEPG( epg )
			dialog.doModal( )
		self.mEventBus.Register( self )


	def ShowHotkeys( self ) :
		context = [ ( 'OSDPlayNF_Rotated.png', '', MR_LANG( 'Extra Options' ) ), ( 'OSDRecordNF.png', '',  MR_LANG( 'Start Recording' ) ), ( 'OSDStopNF.png', '', MR_LANG( 'Stop Recording' ) ), ( 'OSDTeletextNF.png', '', MR_LANG( 'Search' ) ), ( 'OSDBackNF.png', 'OSDMenuNF.png', MR_LANG( 'Go Back' ) ) ]

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_HOTKEYS )
		dialog.SetProperty( context )
		dialog.doModal( )


	def LoadTimerList( self ) :
		self.mTimerList = []
		LOG_TRACE( '' )

		try :
			self.mTimerList = self.mDataCache.Timer_GetTimerList( )
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		if self.mTimerList :
			LOG_TRACE('self.mTimerList len=%d' %len( self.mTimerList ) )


	def	GetSelectedEPG( self ) :
		selectedEPG = None
		selectedPos = -1

		self.mLock.acquire( )
		selectedPos = self.mCtrlBigList.getSelectedPosition( )
		if selectedPos >= 0 and selectedPos < len( self.mEPGList ) :
			selectedEPG = self.mEPGList[selectedPos]

		self.mLock.release( )
		
		return selectedEPG


	def GetTimerByChannel( self, aChannel ) :
		if self.mTimerList == None :
			return 0
 
		for i in range( len( self.mTimerList ) ) :
			timer =  self.mTimerList[i]
			if aChannel.mSid == timer.mSid and aChannel.mTsid == timer.mTsid and aChannel.mOnid == timer.mOnid :			
				return timer.mTimerId

		return 0


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

				if timer.mTimerType == ElisEnum.E_ITIMER_VIEW or \
				   E_V1_9_APPLY_WEEKLY_VIEW_TIMER and timer.mTimerType == ElisEnum.E_ITIMER_VIEWWEEKLY :
					continue

				if timer.mTimerType == ElisEnum.E_ITIMER_WEEKLY and timer.mWeeklyTimer and timer.mWeeklyTimerCount > 0 :
					if aEPG.mSid == timer.mSid and aEPG.mTsid == timer.mTsid and aEPG.mOnid == timer.mOnid :
						if self.HasMachedWeeklyTimer( timer, startTime, endTime ) == True :
							return timer
						
				else :
					if timer.mFromEPG :
						if  timer.mEventId > 0  and ( aEPG.mEventId == timer.mEventId ) and ( aEPG.mSid == timer.mSid ) and ( aEPG.mTsid  == timer.mTsid ) and ( aEPG.mOnid == timer.mOnid ) :
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


	def GetViewTimerByEPG( self, aEPG = None, aChannel = None, aIsRequestList = False ) :
		if self.mTimerList == None :
			return None

		try :
			reqTimerList = []
			startTime = self.mLocalOffset
			endTime = startTime
			if aEPG :
				startTime = aEPG.mStartTime + self.mLocalOffset
				endTime = startTime + aEPG.mDuration
				#LOG_TRACE( 'epg : start[%s] end[%s] offset[%s]'% ( startTime, endTime, self.mLocalOffset ) )
				#LOG_TRACE( 'epg ch[%s] sid[%s] tsid[%s] onid[%s]'% ( aEPG.mEventName, aEPG.mSid, aEPG.mTsid, aEPG.mOnid ) )

			for i in range( len( self.mTimerList ) ) :
				timer = self.mTimerList[i]

				if timer.mTimerType == ElisEnum.E_ITIMER_VIEW or \
				   E_V1_9_APPLY_WEEKLY_VIEW_TIMER and timer.mTimerType == ElisEnum.E_ITIMER_VIEWWEEKLY :
					#LOG_TRACE( 'timer ch[%s] sid[%s] tsid[%s] onid[%s]'% ( timer.mChannelNo, timer.mSid, timer.mTsid, timer.mOnid ) )
					if aEPG and aEPG.mSid == timer.mSid and aEPG.mTsid == timer.mTsid and aEPG.mOnid == timer.mOnid and \
					   timer.mStartTime >= startTime and timer.mStartTime < endTime :
						if aIsRequestList :
							reqTimerList.append( timer )
							continue
						#LOG_TRACE( 'start[%s] end[%s] timer[%s] ch[%s]'% ( startTime, endTime, timer.mStartTime, timer.mChannelNo ) )
						#LOG_TRACE( '------------------- found by event id -------------------------' )
						return True

					elif aChannel and aChannel.mSid == timer.mSid and aChannel.mTsid == timer.mTsid and aChannel.mOnid == timer.mOnid :
						if aIsRequestList :
							reqTimerList.append( timer )
							continue
						#LOG_TRACE( '------------------- found by noEpg timer-------------------------' )
						return True

			if aIsRequestList :
				return reqTimerList

		except Exception, ex :
			LOG_ERR( 'Exception %s'% ex )

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
	

	def IsRunningTimer( self, aTimerId ) :
		runningTimers = self.mDataCache.Timer_GetRunningTimers( )
		if runningTimers == None :
			return False
			
		for timer in runningTimers :
			if timer.mTimerId == aTimerId :
				return True

		return False
			

	def GetChannelByIDs( self, aSid, aTsid, aOnid ) :
		if self.mChannelListHash == None or len( self.mChannelListHash ) <= 0 :
			return None
		return self.mChannelListHash.get( '%d:%d:%d' %( aSid, aTsid, aOnid ), None )


