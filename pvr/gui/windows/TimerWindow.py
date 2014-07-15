from pvr.gui.WindowImport import *

E_TIMER_WINDOW_BASE_ID			=  WinMgr.WIN_ID_TIMER_WINDOW * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID

BUTTON_ID_GO_PARENT				= E_TIMER_WINDOW_BASE_ID + 100
LIST_ID_BIG_TIMER				= E_BASE_WINDOW_ID + 3610
SCROLL_ID_BIG_TIMER			= E_BASE_WINDOW_ID + 3611

LABEL_ID_TIME					= E_TIMER_WINDOW_BASE_ID + 300
LABEL_ID_DATE					= E_TIMER_WINDOW_BASE_ID + 301
LABEL_ID_DURATION				= E_TIMER_WINDOW_BASE_ID + 302

IMAMGE_ID_HD					= E_TIMER_WINDOW_BASE_ID + 310
IMAMGE_ID_DOLBY					= E_TIMER_WINDOW_BASE_ID + 311
IMAMGE_ID_SUBTITLE				= E_TIMER_WINDOW_BASE_ID + 312

CONTEXT_GO_PARENT				= 1
CONTEXT_EDIT_TIMER				= 2
CONTEXT_DELETE_TIMER			= 3
CONTEXT_DELETE_ALL_TIMERS		= 4



class TimerWindow( BaseWindow ) :

	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )

	
	def onInit( self ) :
		self.SetFrontdisplayMessage( MR_LANG( 'Timer List' ) )
		self.mWinId = xbmcgui.getCurrentWindowId( )

		#self.getControl( E_SETTING_MINI_TITLE ).setLabel( MR_LANG( 'Timer' ) )
		self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'EPG' ), MR_LANG( 'Timer List' ) ) )
		self.mSelectedWeeklyTimer = 0

		self.mListItems = []
		self.mTimerList = []

		self.mCtrlBigList = self.getControl( LIST_ID_BIG_TIMER )

		self.mCtrlTimeLabel = self.getControl( LABEL_ID_TIME )
		self.mCtrlDateLabel = self.getControl( LABEL_ID_DATE )
		self.mCtrlDurationLabel = self.getControl( LABEL_ID_DURATION )

		self.mCtrlHDImage = self.getControl( IMAMGE_ID_HD )
		self.mCtrlDolbyImage = self.getControl( IMAMGE_ID_DOLBY )
		self.mCtrlSubtitleImage = self.getControl( IMAMGE_ID_SUBTITLE )		

		self.mCtrlTimeLabel.setLabel( '' )
		self.mCtrlDateLabel.setLabel( '' )
		self.mCtrlDurationLabel.setLabel( '' )

		self.mCtrlHDImage.setImage( '' )
		self.mCtrlDolbyImage.setImage( '' )
		self.mCtrlSubtitleImage.setImage( '' )

		#toDO self.ResetEPGInfomation( )		
		self.UpdateTimerMode( )
		self.SetSingleWindowPosition( E_TIMER_WINDOW_BASE_ID )
		self.SetPipScreen( )

		self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( )
		self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
		LOG_TRACE( 'ZeppingMode(%d,%d,%d)' %( self.mCurrentMode.mServiceType, self.mCurrentMode.mMode, self.mCurrentMode.mSortingMode ) )
		#self.mChannelList = self.mDataCache.Channel_GetList( )
		self.mChannelList = self.mDataCache.Channel_GetAllChannels( self.mCurrentMode.mServiceType )
		self.mChannelListHash = {}

		#LOG_TRACE( "ChannelList=%d" %len( self.mChannelList ) )
		
		if self.mChannelList :
			for channel in self.mChannelList :
				self.mChannelListHash[ '%d:%d:%d' %( channel.mSid, channel.mTsid, channel.mOnid) ] = channel
	
		
		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		self.mGMTTime = 0
		
		self.Load( )
		self.UpdateList( )

		self.mEventBus.Register( self )	
		self.mInitialized = True
		self.setFocusId( LIST_ID_BIG_TIMER )


	def onAction( self, aAction ) :
		self.GetFocusId( )
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		#LOG_TRACE('onAction=%d' %actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR:
			focusId = self.getFocusId( )		
			if focusId  == BUTTON_ID_GO_PARENT	: 
				self.setFocusId( LIST_ID_BIG_TIMER )			
			else:
				self.GoParentTimer( )
		
		elif actionId == Action.ACTION_CONTEXT_MENU :
			focusId = self.GetFocusId( )
			if focusId == SCROLL_ID_BIG_TIMER :
				return
			self.ShowContextMenu( )

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN :
			self.UpdateSelectedPosition( )


	def onClick( self, aControlId ) :
		if aControlId == LIST_ID_BIG_TIMER :
			if self.mSelectedWeeklyTimer == 0 :
				self.GoChildTimer( )
			else :
				selectedPos = self.mCtrlBigList.getSelectedPosition( )
				if self.mSelectedWeeklyTimer > 0 and selectedPos == 0 :
					self.GoParentTimer( )
				return
		
		elif aControlId == BUTTON_ID_GO_PARENT :
			self.GoParentTimer( )


	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			if aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
				LOG_TRACE( 'Record status chanaged' )
				self.UpdateList( )

			if aEvent.getName( ) == ElisEventViewTimerStatus.getName( ) :
				if aEvent.mResult == ElisEnum.E_VIEWTIMER_SUCCESS :
					LOG_TRACE( 'view timer expired' )
					self.UpdateList( )


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.SetVideoRestore( )

		self.mChannelList = []
		self.mChannelListHash = {}
		
		WinMgr.GetInstance( ).CloseWindow( )


	def UpdateTimerMode( self ) :
		self.setProperty( 'TimerMode', 'true' )


	def Flush( self ) :
		pass


	def Load( self ) :
		LOG_TRACE( '----------------------------------->' )
		self.mGMTTime = self.mDataCache.Datetime_GetGMTTime( )

		self.mTimerList = []
		try :
			self.mTimerList = self.mDataCache.Timer_GetTimerList( )
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		if self.mTimerList :
			LOG_TRACE( 'self.mTimerList len=%d' %len( self.mTimerList ) )


	@SetLock
	def UpdateList( self, aUpdateOnly=False ) :
		self.mListItems = []
		self.LoadTimerList( )

		self.mCtrlBigList.reset( )
		self.mListItems = []
		if self.mTimerList== None or len( self.mTimerList ) <= 0 :
			self.mCtrlBigList.addItems( self.mListItems )
			self.UpdateSelectedPosition( )
			return
			
		try :
			if self.mSelectedWeeklyTimer > 0 :
				LOG_TRACE( '' )			
				timer = None
				for i in range( len( self.mTimerList ) ) :
					if self.mTimerList[i].mTimerId == self.mSelectedWeeklyTimer :
						timer = self.mTimerList[i]
						break

				if timer == None :
					return

				struct_time = time.gmtime( timer.mStartTime )
				# tm_wday is different between Python and C++
				LOG_TRACE( 'time.struct_time[6]=%d' %struct_time[6] )
				weekday = struct_time[6] + 1
				if weekday > 6 :
					weekday = 0
				
				# hour*3600 + min*60 + sec
				secondsNow = struct_time[3]*3600 + struct_time[4]*60 + struct_time[5]

				LOG_TRACE( 'weekday=%d'  %weekday )

				listItem = xbmcgui.ListItem( '..' )
				listItem.setProperty( 'StartTime', '' )
				listItem.setProperty( 'Duration', '' )
				listItem.setProperty( 'TimerType', 'None' )
				listItem.setProperty( 'ViewTimer', 'None' )
				listItem.setProperty( 'HasEvent', 'false' )

				self.mListItems.append( listItem )					

				for weeklyTimer in timer.mWeeklyTimer :
					dateLeft = weeklyTimer.mDate - weekday
					if dateLeft < 0 :
						dateLeft += 7
					elif dateLeft == 0 :
						if weeklyTimer.mStartTime < secondsNow :
							dateLeft += 7

					weeklyStarTime = dateLeft*24*3600 + timer.mStartTime + weeklyTimer.mStartTime - secondsNow

					#channel = self.GetChannelByIDs( timer.mSid, timer.mTsid, timer.mOnid )
					channel = self.mDataCache.GetChannelByIDs( timer.mSid, timer.mTsid, timer.mOnid )
					#channel.printdebug()

					iChName   = timer.mName
					iChNumber = timer.mChannelNo
					if channel :
						iChName   = channel.mName
						iChNumber = channel.mNumber
						if E_V1_2_APPLY_PRESENTATION_NUMBER :
							iChNumber = self.mDataCache.CheckPresentationNumber( channel )

					tempChannelName = '%04d %s' %( iChNumber, iChName )

					timerName = '%s'% timer.mName
					#if timer.mTimerType == ElisEnum.E_ITIMER_VIEW or timer.mTimerType == ElisEnum.E_ITIMER_VIEWWEEKLY :
					#	timerName = '[%s]%s'% ( MR_LANG( 'Viewtime' ), timer.mName )

					listItem = xbmcgui.ListItem( tempChannelName, timerName )							

					tempName = '%s' %(TimeToString( weeklyStarTime, TimeFormatEnum.E_AW_DD_MM_YYYY ) )						
					listItem.setProperty( 'StartTime', tempName )

					tempDuration = '%s~%s' %(TimeToString( weeklyStarTime, TimeFormatEnum.E_HH_MM ), TimeToString( weeklyStarTime + weeklyTimer.mDuration, TimeFormatEnum.E_HH_MM ) ) 
					listItem.setProperty( 'Duration', tempDuration )

					if self.IsRunningTimer( timer.mTimerId ) == True and \
						weeklyStarTime < self.mDataCache.Datetime_GetLocalTime( ) and self.mDataCache.Datetime_GetLocalTime( ) < weeklyStarTime + weeklyTimer.mDuration :
						listItem.setProperty( 'TimerType', 'Running' )
					else :
						listItem.setProperty( 'TimerType', 'None' )

					hasView = 'None'
					if timer.mTimerType == ElisEnum.E_ITIMER_VIEW or timer.mTimerType == ElisEnum.E_ITIMER_VIEWWEEKLY :
						hasView = 'True'
					listItem.setProperty( 'ViewTimer', hasView )
					listItem.setProperty( 'HasEvent', 'false' )

					self.mListItems.append( listItem )

				self.mCtrlBigList.addItems( self.mListItems )						

			else :
				for i in range( len( self.mTimerList ) ) :
					timer = self.mTimerList[i]

					#channel = self.GetChannelByIDs( timer.mSid, timer.mTsid, timer.mOnid )
					channel = self.mDataCache.GetChannelByIDs( timer.mSid, timer.mTsid, timer.mOnid )
					#channel.printdebug()

					iChName   = timer.mName
					iChNumber = timer.mChannelNo
					if channel :
						iChName   = channel.mName
						iChNumber = channel.mNumber
						if E_V1_2_APPLY_PRESENTATION_NUMBER :
							iChNumber = self.mDataCache.CheckPresentationNumber( channel )

					tempChannelName = '%04d %s' %( iChNumber, iChName )					

					timerName = '%s'% timer.mName
					#if timer.mTimerType == ElisEnum.E_ITIMER_VIEW or timer.mTimerType == ElisEnum.E_ITIMER_VIEWWEEKLY :
					#	timerName = '[%s]%s'% ( MR_LANG( 'Viewtime' ), timer.mName )

					listItem = xbmcgui.ListItem( tempChannelName, timerName )	

					if timer.mTimerType == ElisEnum.E_ITIMER_WEEKLY or timer.mTimerType == ElisEnum.E_ITIMER_VIEWWEEKLY :
						tempName = MR_LANG( 'Weekly' )
						listItem.setProperty( 'Duration', '' )
						tempDuration = ''
					else :
						tempName = '%s'% ( TimeToString( timer.mStartTime, TimeFormatEnum.E_AW_DD_MM_YYYY ) )						
						tempDuration = '%s~%s'% ( TimeToString( timer.mStartTime, TimeFormatEnum.E_HH_MM ), TimeToString( timer.mStartTime + timer.mDuration, TimeFormatEnum.E_HH_MM ) )

					listItem.setProperty( 'StartTime', tempName )
					listItem.setProperty( 'Duration', tempDuration )

					if self.IsRunningTimer( timer.mTimerId ) == True :
						listItem.setProperty( 'TimerType', 'Running' )
					else :
						listItem.setProperty( 'TimerType', 'None' )

					hasView = 'None'
					if timer.mTimerType == ElisEnum.E_ITIMER_VIEW or timer.mTimerType == ElisEnum.E_ITIMER_VIEWWEEKLY :
						hasView = 'True'
					listItem.setProperty( 'ViewTimer', hasView )

					listItem.setProperty( 'HasEvent', 'false' )

					self.mListItems.append( listItem )

					LOG_TRACE( '---------- self.mListItems COUNT=%d' %len( self.mListItems ) )
					
				self.mCtrlBigList.addItems( self.mListItems )

			xbmc.executebuiltin( 'container.refresh' )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		self.UpdateSelectedPosition( )


	@RunThread
	def CurrentTimeThread( self ) :
		pass


	def UpdateLocalTime( self ) :
		pass


	def ShowContextMenu( self ) :
		context = []

		context.append( ContextItem( MR_LANG( 'Back to previous page' ), CONTEXT_GO_PARENT ) )

		if self.mListItems and len( self.mListItems ) > 0 :
			context.append( ContextItem( MR_LANG( 'Edit' ), CONTEXT_EDIT_TIMER ) )
			context.append( ContextItem( MR_LANG( 'Delete' ), CONTEXT_DELETE_TIMER ) )
			context.append( ContextItem( MR_LANG( 'Delete all' ), CONTEXT_DELETE_ALL_TIMERS ) )

		dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
		dialog.doModal( )
		
		contextAction = dialog.GetSelectedAction( )
		self.DoContextAction( contextAction )


	def DoContextAction( self, aContextAction ) :
		LOG_TRACE( 'aContextAction=%d' %aContextAction )

		if aContextAction == CONTEXT_GO_PARENT :
			self.GoParentTimer( )

		elif aContextAction == CONTEXT_EDIT_TIMER :
			self.ShowEditTimer( )

		elif aContextAction == CONTEXT_DELETE_TIMER :
			self.ShowDeleteConfirm( )

		elif aContextAction == CONTEXT_DELETE_ALL_TIMERS :
			self.ShowDeleteAllConfirm( )


	def ShowEditTimer( self ) :
		try :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_ADD_MANUAL_TIMER )

			timerId = 0
			timerMode = E_TIMER_MODE_RECORD
			selectedPos = self.mCtrlBigList.getSelectedPosition( )

			LOG_TRACE( 'selectedPos=%d' %selectedPos )

			LOG_TRACE( 'self.mSelectedWeeklyTimer=%d' %self.mSelectedWeeklyTimer )
			if self.mSelectedWeeklyTimer > 0 :
				timer = None
				for i in range( len( self.mTimerList ) ) :
					if self.mTimerList[i].mTimerId == self.mSelectedWeeklyTimer :
						timer = self.mTimerList[i]
						break

				if timer == None or timer.mWeeklyTimerCount <= 0 :
					LOG_WARN( 'Could not find weekly timers' )
					return

				if selectedPos > 0 and selectedPos <= timer.mWeeklyTimerCount :
					LOG_TRACE( '' )
					#timer.printdebug( )
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_ADD_MANUAL_TIMER )
					dialog.SetTimer( timer, self.IsRunningTimer( timer.mTimerId ) )
					if timer.mTimerType == ElisEnum.E_ITIMER_VIEW or timer.mTimerType == ElisEnum.E_ITIMER_VIEWWEEKLY :
						#dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_VIEW_TIMER )
						#dialog.SetTimer( timer )
						timerMode = E_TIMER_MODE_VIEW

					dialog.SetTimerMode( timerMode )
					dialog.doModal( )

					if dialog.IsOK( ) == E_DIALOG_STATE_ERROR :
						if dialog.GetConflictTimer( ) == None :
							infoDialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
							infoDialog.SetDialogProperty( MR_LANG( 'Error' ), dialog.GetErrorMessage( ) )
							infoDialog.doModal( )
						else :
							RecordConflict( dialog.GetConflictTimer( ) )

			else :
				if selectedPos >= 0 and selectedPos < len( self.mTimerList ) :
					timer = self.mTimerList[selectedPos]

					if timer == None :
						LOG_WARN( 'Could not find weekly timers' )
						return
		
					dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_ADD_MANUAL_TIMER )
					dialog.SetTimer( timer, self.IsRunningTimer( timer.mTimerId ) )
					if timer.mTimerType == ElisEnum.E_ITIMER_VIEW or timer.mTimerType == ElisEnum.E_ITIMER_VIEWWEEKLY :
						#dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_VIEW_TIMER )
						#dialog.SetTimer( timer )
						timerMode = E_TIMER_MODE_VIEW

					dialog.SetTimerMode( timerMode )
					dialog.doModal( )

					if dialog.IsOK( ) == E_DIALOG_STATE_ERROR :
						if dialog.GetConflictTimer( ) == None :
							infoDialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
							infoDialog.SetDialogProperty( MR_LANG( 'Error' ), dialog.GetErrorMessage( ) )
							infoDialog.doModal( )
						else :
							RecordConflict( dialog.GetConflictTimer( ) )

			self.UpdateList( )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		
	def ShowDeleteConfirm( self ) :
		LOG_TRACE( 'ShowDeleteConfirm' )

		timerId = 0

		selectedPos = self.mCtrlBigList.getSelectedPosition( )
		
		LOG_TRACE( 'EPG Delete debug selectedPos=%d' %selectedPos )

		if self.mSelectedWeeklyTimer > 0 :
			LOG_TRACE( 'EPG Delete debug : selected weekly timer' )
			timer = None
			for i in range( len( self.mTimerList ) ) :
				if self.mTimerList[i].mTimerId == self.mSelectedWeeklyTimer :
					timer = self.mTimerList[i]
					break

			if timer == None or timer.mWeeklyTimerCount <= 0 :
				LOG_WARN( 'Could not find weekly timers' )
				return

			if selectedPos > 0 and selectedPos <= timer.mWeeklyTimerCount :

				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( MR_LANG( 'Delete Timer' ), MR_LANG( 'Are you sure you want to delete this timer?' ) )
				dialog.doModal( )

				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					weeklyTimer = timer.mWeeklyTimer[ selectedPos-1 ]
					if timer.mTimerType == ElisEnum.E_ITIMER_VIEWWEEKLY :
						self.mDataCache.Timer_DeleteOneViewWeeklyTimer( self.mSelectedWeeklyTimer, weeklyTimer.mDate, weeklyTimer.mStartTime ) 
					else :
						self.mDataCache.Timer_DeleteOneWeeklyTimer( self.mSelectedWeeklyTimer, weeklyTimer.mDate, weeklyTimer.mStartTime, weeklyTimer.mDuration ) 
					self.UpdateList( )

		else :
			if selectedPos >= 0 and selectedPos < len( self.mTimerList ) :
				timer = self.mTimerList[ selectedPos ]
				timerId = timer.mTimerId
	
			if timerId > 0 :		
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( MR_LANG( 'Delete Timer' ), MR_LANG( 'Are you sure you want to delete this timer?'  ) )
				dialog.doModal( )

				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					self.mDataCache.Timer_DeleteTimer( timerId )
					self.UpdateList( )


	def ShowDeleteAllConfirm( self ) :
		LOG_TRACE( 'ShowDeleteAllConfirm' )
		if self.mTimerList == None or len(self.mTimerList) <= 0 :
			LOG_WARN( 'Has no timer' )
			return

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( MR_LANG( 'Delete All Timers' ), MR_LANG( 'Are you sure you want to remove all your timers?' ) )
		dialog.doModal( )

		self.OpenBusyDialog( )
		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			if self.mSelectedWeeklyTimer > 0 :
				self.mDataCache.Timer_DeleteTimer( self.mSelectedWeeklyTimer )
			else :
				for timer in self.mTimerList:
					#timer.printdebug()
					self.mDataCache.Timer_DeleteTimer( timer.mTimerId )

			self.UpdateList( )
	
		self.CloseBusyDialog( )


	def LoadTimerList( self ) :
		self.mTimerList = []
		LOG_TRACE( '' )

		try :
			self.mTimerList = self.mDataCache.Timer_GetTimerList( )
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		if self.mTimerList :
			LOG_TRACE('self.mTimerList len=%d' %len( self.mTimerList ) )


	def GetTimerByChannel( self, aChannel ) :
		if self.mTimerList == None :
			return 0
 
		for i in range( len( self.mTimerList ) ) :
			timer =  self.mTimerList[i]
			if aChannel.mSid == timer.mSid and aChannel.mTsid == timer.mTsid and aChannel.mOnid == timer.mOnid :			
				return timer.mTimerId

		return 0


	def IsRunningTimer( self, aTimerId ) :
		runningTimers = self.mDataCache.Timer_GetRunningTimers( )
		if runningTimers == None :
			return False
			
		for timer in runningTimers :
			if timer.mTimerId == aTimerId :
				return True

		return False
			

	def GoChildTimer( self ) :
		if self.mSelectedWeeklyTimer > 0 :
			return

		selectedPos = self.mCtrlBigList.getSelectedPosition( )
		
		if selectedPos >= 0 and selectedPos < len( self.mTimerList ) :
			timer = self.mTimerList[ selectedPos ]

			if timer.mTimerType == ElisEnum.E_ITIMER_WEEKLY and timer.mWeeklyTimerCount > 0 or \
			   timer.mTimerType == ElisEnum.E_ITIMER_VIEWWEEKLY and timer.mWeeklyTimerCount > 0 :
				self.mSelectedWeeklyTimer = timer.mTimerId
				self.UpdateList( )


	def GoParentTimer( self ) :
		if self.mSelectedWeeklyTimer > 0 :
			self.mSelectedWeeklyTimer = 0
			self.UpdateList( )

		else :
			self.Close( )


	def GetChannelByIDs( self, aSid, aTsid, aOnid ) :
		if self.mChannelListHash == None or len( self.mChannelListHash ) <= 0 :
			return None
		return self.mChannelListHash.get( '%d:%d:%d' %( aSid, aTsid, aOnid ), None )


	def UpdateSelectedPosition( self ) :
		selectedPos = self.mCtrlBigList.getSelectedPosition( )
		if self.mTimerList == None or len(self.mTimerList) <= 0 :
			self.setProperty( 'SelectedPosition', '0' )
			return
		if selectedPos < 0 :
			self.setProperty( 'SelectedPosition', '0' )
		else :
			self.setProperty( 'SelectedPosition', '%d' % ( selectedPos + 1 ) )


