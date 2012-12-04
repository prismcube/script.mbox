from pvr.gui.WindowImport import *

BUTTON_ID_GO_PARENT				= 100
LIST_ID_BIG_EPG					= 3510

LABEL_ID_TIME					= 300
LABEL_ID_DATE					= 301
LABEL_ID_DURATION				= 302

IMAMGE_ID_HD					= 310
IMAMGE_ID_DOLBY					= 311
IMAMGE_ID_SUBTITLE				= 312


CONTEXT_GO_PARENT				= 1
CONTEXT_EDIT_TIMER				= 2
CONTEXT_DELETE_TIMER			= 3
CONTEXT_DELETE_ALL_TIMERS		= 4



class TimerWindow( BaseWindow ) :

	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )

	
	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( MR_LANG( 'Timer' ) )
		self.mSelectedWeeklyTimer = 0

		self.mListItems = []
		self.mTimerList = []

		self.mCtrlBigList = self.getControl( LIST_ID_BIG_EPG )

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

		self.SetPipScreen( )
		
		self.UpdateTimerMode( )

		self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( )
		self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
		LOG_TRACE( 'ZeppingMode(%d,%d,%d)' %( self.mCurrentMode.mServiceType, self.mCurrentMode.mMode, self.mCurrentMode.mSortingMode ) )
		self.mChannelList = self.mDataCache.Channel_GetList( )

		if self.mChannelList :
			LOG_TRACE( "ChannelList=%d" %len( self.mChannelList ) )
		
		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		self.mGMTTime = 0
		
		self.Load( )
		self.UpdateList( )

		self.mEventBus.Register( self )	
		self.mInitialized = True


	def onAction( self, aAction ) :
		self.GetFocusId( )
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		#LOG_TRACE('onAction=%d' %actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.GoParentTimer( )

		elif  actionId == Action.ACTION_SELECT_ITEM :
			if self.mSelectedWeeklyTimer == 0 :
				self.GoChildTimer( )
			else :
				selectedPos = self.mCtrlBigList.getSelectedPosition( )
				if self.mSelectedWeeklyTimer > 0 and selectedPos == 0 :
					self.GoParentTimer( )
				return
	
		elif actionId == Action.ACTION_PARENT_DIR :
			self.GoParentTimer( )
			
		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT :
			pass

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN :
			if self.mFocusId == LIST_ID_BIG_EPG :
				pass

		elif actionId == Action.ACTION_PAGE_UP  or actionId == Action.ACTION_PAGE_DOWN :
			if self.mFocusId == LIST_ID_BIG_EPG :
				pass
		
		elif actionId == Action.ACTION_CONTEXT_MENU:
			self.ShowContextMenu( )


	def onClick( self, aControlId ) :
		LOG_TRACE( 'aControlId=%d' %aControlId )
		if aControlId == BUTTON_ID_GO_PARENT :
			self.GoParentTimer( )


	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			if aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
				LOG_TRACE( 'Record status chanaged' )
				self.UpdateList( )


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.SetVideoRestore( )
		WinMgr.GetInstance( ).CloseWindow( )


	def UpdateTimerMode( self ) :
		self.mWin.setProperty( 'TimerMode', 'true' )


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

					channel = self.mDataCache.Channel_GetByNumber( timer.mChannelNo )
					#channel.printdebug()
					tempChannelName = '%04d %s' %( channel.mNumber, channel.mName )

					listItem = xbmcgui.ListItem( tempChannelName, timer.mName )							

					tempName = '%s' %(TimeToString( weeklyStarTime, TimeFormatEnum.E_AW_DD_MM_YYYY ) )						
					listItem.setProperty( 'StartTime', tempName )

					tempDuration = '%s~%s' %(TimeToString( weeklyStarTime, TimeFormatEnum.E_HH_MM ), TimeToString( weeklyStarTime + weeklyTimer.mDuration, TimeFormatEnum.E_HH_MM ) ) 
					listItem.setProperty( 'Duration', tempDuration )

					if self.IsRunningTimer( timer.mTimerId ) == True and \
						weeklyStarTime < self.mDataCache.Datetime_GetLocalTime( ) and self.mDataCache.Datetime_GetLocalTime( ) < weeklyStarTime + weeklyTimer.mDuration :
						listItem.setProperty( 'TimerType', 'Running' )
					else :
						listItem.setProperty( 'TimerType', 'None' )

					listItem.setProperty( 'HasEvent', 'false' )

					self.mListItems.append( listItem )

				self.mCtrlBigList.addItems( self.mListItems )						

			else :
				for i in range( len( self.mTimerList ) ) :
					timer = self.mTimerList[i]
					channel = self.mDataCache.Channel_GetByNumber( timer.mChannelNo )
					#channel.printdebug()
					tempChannelName = '%04d %s' %( channel.mNumber, channel.mName )

					listItem = xbmcgui.ListItem( tempChannelName, timer.mName )	

					if timer.mTimerType == ElisEnum.E_ITIMER_WEEKLY :
						tempName = MR_LANG( 'Weekly' )
						listItem.setProperty( 'Duration', '' )
						tempDuration = ''
					else :
						tempName = '%s' %(TimeToString( timer.mStartTime, TimeFormatEnum.E_AW_DD_MM_YYYY ) )						
						tempDuration = '%s~%s' %(TimeToString( timer.mStartTime, TimeFormatEnum.E_HH_MM ), TimeToString( timer.mStartTime + timer.mDuration, TimeFormatEnum.E_HH_MM ) )

					listItem.setProperty( 'StartTime', tempName )
					listItem.setProperty( 'Duration', tempDuration )

					if self.IsRunningTimer( timer.mTimerId ) == True :
						listItem.setProperty( 'TimerType', 'Running' )
					else :
						listItem.setProperty( 'TimerType', 'None' )

					listItem.setProperty( 'HasEvent', 'false' )

					self.mListItems.append( listItem )

					LOG_TRACE( '---------- self.mListItems COUNT=%d' %len( self.mListItems ) )
					
				self.mCtrlBigList.addItems( self.mListItems )

				xbmc.executebuiltin( 'container.update' )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	@RunThread
	def CurrentTimeThread( self ) :
		pass


	def UpdateLocalTime( self ) :
		pass


	def ShowContextMenu( self ) :
		context = []

		context.append( ContextItem( MR_LANG( 'Back to Previous Page' ), CONTEXT_GO_PARENT ) )
		
		if self.mListItems and len( self.mListItems ) > 0 :
			context.append( ContextItem( MR_LANG( 'Edit Timer' ), CONTEXT_EDIT_TIMER ) )
			context.append( ContextItem( MR_LANG( 'Delete Timer' ), CONTEXT_DELETE_TIMER ) )
			context.append( ContextItem( MR_LANG( 'Delete All Timers' ), CONTEXT_DELETE_ALL_TIMERS ) )			

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
					LOG_WARN( 'Can not find weeklytimer' )
					return

				if selectedPos > 0 and selectedPos <= timer.mWeeklyTimerCount :
					LOG_TRACE( '' )
					timer.printdebug( )
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_ADD_MANUAL_TIMER )
					LOG_TRACE( '' )
					dialog.SetTimer( timer, self.IsRunningTimer( timer.mTimerId ) )
					LOG_TRACE( '' )					
					dialog.doModal( )
					LOG_TRACE( '' )					

					if dialog.IsOK( ) == E_DIALOG_STATE_ERROR :
						if dialog.GetConflictTimer( ) == None :
							infoDialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
							infoDialog.SetDialogProperty( MR_LANG( 'Error' ), dialog.GetErrorMessage( ) )
							infoDialog.doModal( )
						else :
							from pvr.GuiHelper import RecordConflict
							RecordConflict( dialog.GetConflictTimer( ) )

			else :
				if selectedPos >= 0 and selectedPos < len( self.mTimerList ) :
					timer = self.mTimerList[selectedPos]

					if timer == None :
						LOG_WARN( 'Can not find weeklytimer' )
						return
		
					dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_ADD_MANUAL_TIMER )
					dialog.SetTimer( timer, self.IsRunningTimer( timer.mTimerId ) )
					dialog.doModal( )

					if dialog.IsOK( ) == E_DIALOG_STATE_ERROR :
						if dialog.GetConflictTimer( ) == None :
							infoDialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
							infoDialog.SetDialogProperty( MR_LANG( 'Error' ), dialog.GetErrorMessage( ) )
							infoDialog.doModal( )
						else :
							from pvr.GuiHelper import RecordConflict
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
				LOG_WARN( 'Can not find weeklytimer' )
				return

			if selectedPos > 0 and selectedPos <= timer.mWeeklyTimerCount :

				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( MR_LANG( 'Delete Timer' ), MR_LANG( 'Do you want to delete the timer?' ) )
				dialog.doModal( )

				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					weeklyTimer = timer.mWeeklyTimer[ selectedPos-1 ]
					self.mDataCache.Timer_DeleteOneWeeklyTimer( self.mSelectedWeeklyTimer, weeklyTimer.mDate, weeklyTimer.mStartTime, weeklyTimer.mDuration ) 
					self.UpdateList( )

		else :
			if selectedPos >= 0 and selectedPos < len( self.mTimerList ) :
				timer = self.mTimerList[ selectedPos ]
				timerId = timer.mTimerId
	
			if timerId > 0 :		
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( MR_LANG( 'Delete Timer' ), MR_LANG( 'Do you want to delete the timer?'  ) )
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
		dialog.SetDialogProperty( MR_LANG( 'WARNING' ), MR_LANG( 'DO YOU WANT TO REMOVE ALL YOUR TIMERS?' ) )
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

			if timer.mTimerType == ElisEnum.E_ITIMER_WEEKLY and timer.mWeeklyTimerCount > 0 :
				self.mSelectedWeeklyTimer = timer.mTimerId
				self.UpdateList( )


	def GoParentTimer( self ) :
		if self.mSelectedWeeklyTimer > 0 :
			self.mSelectedWeeklyTimer = 0
			self.UpdateList( )

		else :
			self.Close( )


