from pvr.gui.WindowImport import *


# Control IDs
E_LABEL_RECORD_NAME			= 101
E_LABEL_EPG_START_TIME		= 102
E_LABEL_EPG_END_TIME		= 103
E_BUTTON_ADD				= 200
E_BUTTON_CANCEL				= 201

E_IMAGE_DIALOG_BACKGROUND   = 9001
E_GROUP_ID_SHOW_INFO        = 300
E_PROGRESS_NETVOLUME        = 301
E_LABEL_ID_USE_INFO         = 302

E_ONCE						= 0
E_WEEKLY					= 1
E_DAILY						= 2

E_RECORD_MODE				= 0
E_VIEW_MODE				= 1


WEEKLY_DEFALUT_EXPIRE_DAYS	= 7

#LIST_RECORDING_MODE	= [ MR_LANG( 'Once' ), MR_LANG( 'Daily' ), MR_LANG( 'Weekly' ) ]
LIST_RECORDING_MODE	= [ MR_LANG( 'Once' ), MR_LANG( 'Weekly' ), '%s(7 %s)' %(MR_LANG( 'Weekly' ), MR_LANG( 'Days' ))  ]
LIST_WEEKLY = [ MR_LANG( 'Sun' ), MR_LANG( 'Mon'), MR_LANG( 'Tue' ), MR_LANG( 'Wed' ), MR_LANG( 'Thu' ), MR_LANG( 'Fri' ), MR_LANG( 'Sat' ) ]


ONE_DAY_SECONDS				= 3600*24


class UsedWeeklyTimer( ElisIWeeklyTimer ) :
	def __init__( self ) :
		ElisIWeeklyTimer.__init__( self )
		self.mUsed = False
		self.mEnableSelectChannel = False


class DialogAddManualTimer( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		self.mEPG = None
		self.mRecordingMode = E_ONCE
		self.mTimerMode = E_RECORD_MODE
		self.mChanne = None
		self.mTimer = None
		self.mUsedWeeklyList = None
		self.mSelectedWeekOfDay = 0
		self.mRecordName = MR_LANG( 'None' )
		self.mErrorMessage = MR_LANG( 'Unknown Error' )
		self.mWeeklyStart = 0
		self.mWekklyEnd = 0
		self.mConflictTimer = None
		self.mIsRunningTimer = False
		self.mEnableSelectChannel = False		
		self.mIsOk = E_DIALOG_STATE_CANCEL


	def onInit( self ) :
		global LIST_RECORDING_MODE
		global LIST_WEEKLY
		#LIST_RECORDING_MODE	= [ MR_LANG( 'Once' ), MR_LANG( 'Daily' ), MR_LANG( 'Weekly' ) ]
		LIST_RECORDING_MODE	= [ MR_LANG( 'Once' ), MR_LANG( 'Weekly' ), '%s(7 %s)' %(MR_LANG( 'Weekly' ), MR_LANG( 'Days' ))  ]
		LIST_WEEKLY = [ MR_LANG( 'Sun' ), MR_LANG( 'Mon'), MR_LANG( 'Tue' ), MR_LANG( 'Wed' ), MR_LANG( 'Thu' ), MR_LANG( 'Fri' ), MR_LANG( 'Sat' ) ]

		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.setProperty( 'DialogDrawFinished', 'False' )

		netVolumeID = -99
		self.mFreeHDD  = 0
		self.mTotalHDD = 0
		self.mSelectIdx = 99
		self.mNetVolume = None
		self.mNetVolumeList = []
		self.mDialogWidth = self.getControl( E_IMAGE_DIALOG_BACKGROUND ).getWidth( )

		if E_SUPPORT_EXTEND_RECORD_PATH and CheckHdd( ) :
			self.mNetVolumeList = self.mDataCache.Record_GetNetworkVolume( )
			self.mTotalHDD = self.mCommander.Record_GetPartitionSize( )
			self.mFreeHDD  = self.mCommander.Record_GetFreeMBSize( )


		defaultFocus = E_DialogSpinEx03
		if self.mTimer :
			self.SetHeaderLabel( MR_LANG( 'Edit Timer' ) )
			netVolumeID = self.mTimer.mVolumeID
			defaultFocus = E_DialogInput03
		else :
			self.SetHeaderLabel( MR_LANG( 'Add Manual Timer' ) )

		if self.mTimer :
			self.mRecordName = self.mTimer.mName
		elif self.mEPG  :
			self.mRecordName = self.mEPG.mEventName
		else :
			self.mRecordName = self.mChannel.mName

		self.GetVolumeContext( netVolumeID )

		self.Reload( )
		self.DrawItem( )

		self.SetFocus( defaultFocus )

		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_OK_ID, MR_LANG( 'Confirm' ) )
		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_CANCEL_ID, MR_LANG( 'Cancel' ) )
		self.mIsOk = E_DIALOG_STATE_CANCEL

		self.setProperty( 'DialogDrawFinished', 'True' )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.GetFocusId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			self.CloseDialog( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			groupId = self.GetGroupId( focusId )

			if groupId == E_DialogInput01 :
				if self.mEnableSelectChannel :
					self.ShowSelectChannel( )
				else :
					self.ShowRecordName( )
			
			elif groupId == E_DialogSpinEx01 :
				self.mRecordingMode = self.GetSelectedIndex( E_DialogSpinEx01 )
				self.Reload( )
				self.ChangeRecordMode( )
				self.UpdateLocation( )

			elif groupId == E_DialogSpinEx02 :
				selectIndex = self.GetSelectedIndex( E_DialogSpinEx02 )
				if focusId == E_DialogSpinEx02 + 1 : 
					self.ChangeStartDay( True )
				else :
					self.ChangeStartDay( False )

			elif groupId == E_DialogSpinEx03 :
				self.mTimerMode = self.GetSelectedIndex( E_DialogSpinEx03 )			
				self.mRecordingMode = self.GetSelectedIndex( E_DialogSpinEx01 )
				if self.mRecordingMode != E_ONCE :
					self.mRecordingMode = E_ONCE
					self.Reload( )
					self.ChangeRecordMode( )
					self.UpdateLocation( )
			
				self.ChangeTimerMode()

			elif groupId == E_DialogSpinDay :
				if self.mRecordingMode == E_WEEKLY  and self.mIsRunningTimer == True:
					pass
				else :
					self.SelectWeeklyDay( )
				#self.DrawItem( )

			elif groupId == E_DialogInput02 :
				self.ShowStartTime( )

			elif groupId == E_DialogInput03 :
				self.ShowEndTime( )

			elif groupId == E_DialogInput04 :
				self.ShowNetworkVolume( )

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
	
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			if self.GetGroupId( focusId ) == E_DialogSpinDay :
				self.ChangeWeeklyDay( )
			else :
				self.ControlLeft( )
				
		elif actionId == Action.ACTION_MOVE_RIGHT :
			if self.GetGroupId( focusId ) == E_DialogSpinDay :
				self.ChangeWeeklyDay( )
			else :
				self.ControlRight( )

		else :
			LOG_WARN( 'Unknown Action' )


	def onFocus( self, aControlId ) :
		pass


	def onClick( self, aControlId ) :
		groupId = self.GetGroupId( aControlId )
		if groupId == E_SETTING_DIALOG_BUTTON_OK_ID :			
			if self.DoAddTimer( ) == False :
				self.mIsOk = E_DIALOG_STATE_ERROR
			self.ResetAllControl( )
			self.CloseDialog( )

		elif groupId == E_SETTING_DIALOG_BUTTON_CANCEL_ID :
			self.mIsOk = E_DIALOG_STATE_NO
			self.ResetAllControl( )
			self.CloseDialog( )

		elif groupId == E_SETTING_DIALOG_BUTTON_CLOSE :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.ResetAllControl( )
			self.CloseDialog( )


	def GetErrorMessage( self ) :
		return self.mErrorMessage


	def SetEPG( self, aEPG ) :
		self.mEPG = aEPG


	def SetChannel( self, aChannel ) :
		self.mChannel = aChannel


	def SetTimer( self, aTimer, aIsRunningTimer=False ) :
		self.mTimer = aTimer
		self.mIsRunningTimer = aIsRunningTimer		


	def IsOK( self ) :
		return self.mIsOk


	def GetConflictTimer( self ) :
		return self.mConflictTimer


	def GetVolumeInfo( self, aNetVolume = None ) :
		lblSelect = MR_LANG( 'HDD' )
		lblOnline = E_TAG_TRUE
		useFree = self.mFreeHDD
		useTotal= self.mTotalHDD
		useInfo = 0
		if aNetVolume :
			lblSelect = os.path.basename( aNetVolume.mMountPath )
			if not aNetVolume.mOnline :
				lblOnline = E_TAG_FALSE
			useFree = aNetVolume.mFreeMB
			if aNetVolume.mTotalMB > 0 :
				useTotal = aNetVolume.mTotalMB

		else :
			#hdd not
			if useTotal < 1 :
				lblOnline = E_TAG_FALSE

		if useTotal > 0 :
			useInfo = int( ( ( 1.0 * ( useTotal - useFree ) ) / useTotal ) * 100 )

		lblByte = '%sMB'% useFree
		if useFree > 1024 :
			lblByte = '%sGB'% ( useFree / 1024 )
		elif useFree < 0 :
			lblByte = '%sKB'% ( useFree * 1024 )
		lblPercent = '%s%%, %s %s'% ( useInfo, lblByte, MR_LANG( 'Free' ) )

		return lblSelect, useInfo, lblPercent, lblOnline


	def GetVolumeContext( self, aVolumeID = -1 ) :
		trackList = [ContextItem( MR_LANG( 'Internal HDD' ), 99 )]
		trackIndex = 0
		if self.mNetVolumeList and len( self.mNetVolumeList ) > 0 :
			for netVolume in self.mNetVolumeList :
				getPath = netVolume.mRemoteFullPath
				urlType = urlparse.urlparse( getPath ).scheme
				#urlHost, urlPort, urlUser, urlPass, urlPath, urlFile, urlSize = GetParseUrl( getPath )
				lblType = 'local'
				if urlType :
					lblType = '%s'% urlType.upper()

				lblPath = '[%s]%s'% ( lblType, os.path.basename( netVolume.mMountPath ) )
				#LOG_TRACE('mountPath idx[%s] urlType[%s] mRemotePath[%s] mMountPath[%s] isDefault[%s]'% ( trackIndex, urlType, netVolume.mRemotePath, netVolume.mMountPath, netVolume.mIsDefaultSet ) )

				if aVolumeID > -1 :
					if netVolume.mIndexID == aVolumeID :
						self.mNetVolume = netVolume
						self.mSelectIdx = trackIndex
						LOG_TRACE( '[ManaulTimer] Edit Timer, get volumeID[%s]'% aVolumeID )
				else :
					if netVolume.mIsDefaultSet :
						self.mNetVolume = netVolume
						if aVolumeID == -99 :
							self.mSelectIdx = trackIndex
						LOG_TRACE( '[ManaulTimer] find Default volume, mnt[%s]'% netVolume.mMountPath )

				trackList.append( ContextItem( lblPath, trackIndex ) )
				trackIndex += 1

		else :
			self.mNetVolumeList = []
			LOG_TRACE( 'Record_GetNetworkVolume none' )

		return trackList


	def ShowNetworkVolume( self ) :
		trackList = self.GetVolumeContext( )
		if not trackList or len( trackList ) < 1 :
			LOG_TRACE( '[ManaulTimer] show fail, mount list is None' )
			return

		selectedIdx = 0
		if self.mSelectIdx != 99 :
			selectedIdx = self.mSelectIdx + 1
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( trackList, selectedIdx )
		dialog.doModal( )

		selectAction = dialog.GetSelectedAction( )
		if selectAction < 0 :
			return

		self.mSelectIdx = selectAction
		if selectAction == 99 :
			self.mNetVolume = None
		elif selectAction < len( self.mNetVolumeList ) :
			self.mNetVolume = deepcopy( self.mNetVolumeList[selectAction] )

		lblSelect, useInfo, lblPercent, lblOnline = self.GetVolumeInfo( self.mNetVolume )
		self.SetControlLabel2String( E_DialogInput04, lblSelect )
		self.setProperty( 'NetVolumeConnect', lblOnline )
		self.setProperty( 'NetVolumeUse', lblPercent )
		self.getControl( E_PROGRESS_NETVOLUME ).setPercent( useInfo )
		ResetPositionVolumeInfo( self, lblPercent, self.mDialogWidth, E_GROUP_ID_SHOW_INFO, E_LABEL_ID_USE_INFO )


	def Reload ( self ) :
		LOG_TRACE( '' )
		try :
			self.mSelectedWeekOfDay	= 0 
			self.mUsedWeeklyList = []

			if self.mTimer :
				if self.mTimer.mTimerType == ElisEnum.E_ITIMER_WEEKLY :
					self.mRecordingMode = E_WEEKLY
					self.mWeeklyStart = self.mTimer.mStartTime
					self.mWeeklyEnd = self.mWeeklyStart + WEEKLY_DEFALUT_EXPIRE_DAYS*ONE_DAY_SECONDS - 1

					for i in range( 7 ) :
						usedTimer =  UsedWeeklyTimer( )
						usedTimer.mDate = i
						self.mUsedWeeklyList.append( usedTimer )

					compareStartTime = 0
					compareDuration = 0
					isDailyMode = True

					for i in range( self.mTimer.mWeeklyTimerCount ) :
						weeklyTimer = self.mTimer.mWeeklyTimer[i]
						#weeklyTimer.printdebug( )
						usedTimer = self.mUsedWeeklyList[weeklyTimer.mDate]
						usedTimer.mUsed =True
						usedTimer.mStartTime = weeklyTimer.mStartTime
						usedTimer.mDuration = weeklyTimer.mDuration

						if i == 0 :
							self.mSelectedWeekOfDay	= weeklyTimer.mDate
							compareStartTime = usedTimer.mStartTime
							compareDuration = usedTimer.mDuration
						elif isDailyMode == True :
							if usedTimer.mStartTime != compareStartTime or usedTimer.mDuration != compareDuration :
								isDailyMode = False

					if isDailyMode == True and self.mTimer.mWeeklyTimerCount == 7 : #expect all weekly time are same  --- > E_DAILY
						self.mRecordingMode = E_DAILY					

					#fill unused date
					for i in range( 7 ) :
						if self.mUsedWeeklyList[i].mUsed == False :
							self.mUsedWeeklyList[i].mStartTime = compareStartTime
							self.mUsedWeeklyList[i].mDuration = compareDuration
					
				else :
					self.mRecordingMode == E_ONCE 
					
			else :
				startTime = self.mDataCache.Datetime_GetLocalTime( )
				prop = ElisPropertyEnum( 'Default Rec Duration', self.mCommander )
				duration = prop.GetProp( )
				self.mRecordName = self.mChannel.mName				

				if self.mEPG and  self.mEPG.mStartTime + self.mEPG.mDuration + self.mDataCache.Datetime_GetLocalOffset( ) > self.mDataCache.Datetime_GetLocalTime( ) :
					if self.mEPG.mStartTime + self.mDataCache.Datetime_GetLocalOffset( ) < self.mDataCache.Datetime_GetLocalTime( ) :
						startTime = self.mDataCache.Datetime_GetLocalTime( )
						duration =  self.mEPG.mStartTime + self.mEPG.mDuration +  self.mDataCache.Datetime_GetLocalOffset( )  - self.mDataCache.Datetime_GetLocalTime( )
						if duration <=  0 :
							duration = prop.GetProp( )
						
					else :
						startTime = self.mEPG.mStartTime + self.mDataCache.Datetime_GetLocalOffset( )
						duration = self.mEPG.mDuration

				days = int( startTime/ONE_DAY_SECONDS )
				self.mWeeklyStart = days*ONE_DAY_SECONDS
				self.mWeeklyEnd = days*ONE_DAY_SECONDS + WEEKLY_DEFALUT_EXPIRE_DAYS*ONE_DAY_SECONDS - 1

				struct_time = time.gmtime( startTime )
				# tm_wday is different between Python and C++
				weekday = struct_time[6] + 1
				if weekday > 6 :
					weekday = 0

				LOG_TRACE( 'weekday=%d' %weekday )

				for i in range( 7 ) :

					usedTimer =  UsedWeeklyTimer()

					if self.mRecordingMode == E_ONCE :
						if i == 0 :
							usedTimer.mUsed = True
						else :
							usedTimer.mUsed = False

					elif self.mRecordingMode == E_WEEKLY :
						if i == weekday :
							usedTimer.mUsed = True
							self.mSelectedWeekOfDay	= weekday							
						else :
							usedTimer.mUsed = False
						
					else : #E_DAILY
						usedTimer.mUsed = True
						if i == weekday :
							self.mSelectedWeekOfDay	= weekday

					usedTimer.mDate = i
					usedTimer.mStartTime = startTime %( ONE_DAY_SECONDS )
					usedTimer.mDuration = duration
					self.mUsedWeeklyList.append( usedTimer )

			
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex)

		return


	def DrawItem( self ) :
		LOG_TRACE( 'self.mRecordingMode=%d' %self.mRecordingMode )
		global LIST_RECORDING_MODE
		global LIST_WEEKLY

		try :
			self.ResetAllControl( )
			self.AddUserEnumControl( E_DialogSpinEx03, MR_LANG( 'Timer Mode' ), [ MR_LANG( 'Record' ),  MR_LANG( 'View' ) ], 0 )
			if self.mTimer :
				self.SetEnableControl( E_DialogSpinEx03, False )					
				
			self.AddUserEnumControl( E_DialogSpinEx01, MR_LANG( 'Recording' ), LIST_RECORDING_MODE, self.mRecordingMode )
			if self.mEnableSelectChannel == True :
				self.AddInputControl( E_DialogInput01, MR_LANG( 'Select Channel' ),  MR_LANG( 'Record Name' ) )
			else :
				self.AddInputControl( E_DialogInput01, MR_LANG( 'Name' ),  MR_LANG( 'Record Name' ) )

			self.AddUserEnumControl( E_DialogSpinEx02, MR_LANG( 'Start Date' ), [ MR_LANG( 'Date' ) ], 0 )			
			#self.AddInputControl(  E_DialogSpinEx02, 'Date', 'Date' )
			self.AddListControl( E_DialogSpinDay, LIST_WEEKLY, self.mSelectedWeekOfDay )
			#self.SetListControlTitle( E_DialogSpinDay, MR_LANG( 'Daily' ) )
			self.SetListControlTitle( E_DialogSpinDay, MR_LANG( 'Day of Week' ) )

			self.AddInputControl( E_DialogInput02, MR_LANG( 'Start Time' ),  '00:00' )
			self.AddInputControl( E_DialogInput03, MR_LANG( 'End Time' ),  '00:00' )

			if E_SUPPORT_EXTEND_RECORD_PATH :
				lblSelect, useInfo, lblPercent, lblOnline = self.GetVolumeInfo( self.mNetVolume )
				self.AddInputControl( E_DialogInput04, MR_LANG( 'Record Path' ), lblSelect )
				self.setProperty( 'NetVolumeConnect', lblOnline )
				self.setProperty( 'NetVolumeUse', lblPercent )
				self.getControl( E_PROGRESS_NETVOLUME ).setPercent( useInfo )
				ResetPositionVolumeInfo( self, lblPercent, self.mDialogWidth, E_GROUP_ID_SHOW_INFO, E_LABEL_ID_USE_INFO )
				if self.mTimer :
					#block control by Edit timer
					self.SetEnableControl( E_DialogInput04, False )

				self.setProperty( 'NetVolumeInfo', E_TAG_TRUE )

			self.AddOkCanelButton( )

			self.SetAutoHeight( False )
			self.InitControl( )
			
			self.ChangeRecordMode( )
			self.UpdateLocation( )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def ChangeTimerMode( self ) :
		if self.mTimerMode == E_RECORD_MODE: 
			self.SetEnableControl( E_DialogSpinEx01, True )
			self.SetEnableControl( E_DialogInput03, True )
			self.SetEnableControl( E_DialogInput04, True )
		else :
			self.SetEnableControl( E_DialogSpinEx01, False )
			self.SetEnableControl( E_DialogInput03, False )
			self.SetEnableControl( E_DialogInput04, False )

		self.SetFocus( E_DialogSpinEx03 )


	def ChangeRecordMode( self ) :
		try :

			if self.mTimer :
				self.SelectPosition( E_DialogSpinEx01, self.mRecordingMode )
				self.SetEnableControl( E_DialogSpinEx01,  False )
				self.SetControlLabel2String( E_DialogInput01,  self.mTimer.mName )
				self.SetEnableControl( E_DialogInput01,  False )

				if self.mRecordingMode == E_ONCE :
					startTime = self.mTimer.mStartTime
					endTime = startTime + self.mTimer.mDuration

					self.SelectPosition( E_DialogSpinEx02, 0 )						
					self.SetVisibleControl( E_DialogSpinDay, False )
					self.SetEnableControl( E_DialogSpinDay, False )
					#self.SetVisibleControl( E_DialogSpinEx02, True )
					self.SetListControlItemLabel( E_DialogSpinEx02, TimeToString( startTime, TimeFormatEnum.E_AW_DD_MM_YYYY ) )
					
					self.SetControlLabel2String( E_DialogInput02, TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
					self.SetControlLabel2String( E_DialogInput03, TimeToString( endTime, TimeFormatEnum.E_HH_MM) )

					if self.mIsRunningTimer == True :
						self.SetEnableControl( E_DialogSpinEx02, False )					
						self.SetEnableControl( E_DialogInput02, False )
						self.SetFocus( E_DialogInput03 )
					else :
						self.SetEnableControl( E_DialogSpinEx02, True )					
						self.SetFocus( E_DialogInput02 )

				else :

					self.SelectPosition( E_DialogSpinEx01, self.mRecordingMode )
					self.SelectPosition( E_DialogSpinEx02, 0 )
					listItems = self.GetListItems( E_DialogSpinDay )

					for i in range( len(listItems) ) :
						if self.mUsedWeeklyList[i].mUsed == True :
							listItems[i].setProperty( 'Used', 'True')
						else :
							listItems[i].setProperty( 'Used', 'False')

					self.SelectPosition( E_DialogSpinDay, self.mSelectedWeekOfDay )
					self.SetVisibleControl( E_DialogSpinDay, True )
					self.SetEnableControl( E_DialogSpinDay, True )

					self.SelectPosition( E_DialogSpinEx02, 0 )
					self.SetEnableControl( E_DialogSpinEx02, False )
					#self.SetVisibleControl( E_DialogSpinEx02, True )

					startTime = self.mUsedWeeklyList[ self.mSelectedWeekOfDay ].mStartTime
					endTime = startTime + self.mUsedWeeklyList[ self.mSelectedWeekOfDay ].mDuration

					self.SetControlLabel2String( E_DialogInput02, TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
					self.SetControlLabel2String( E_DialogInput03, TimeToString( endTime, TimeFormatEnum.E_HH_MM) )

					if self.mRecordingMode == E_WEEKLY :
						self.SetEnableControl( E_DialogSpinDay, True )
						self.SetFocus( E_DialogSpinDay )
						if self.mUsedWeeklyList[ self.mSelectedWeekOfDay ].mUsed == False :
							self.SetEnableControl( E_DialogInput02, False )
							self.SetEnableControl( E_DialogInput03, False )
						else :
							if self.mIsRunningTimer == True :
								self.SetEnableControl( E_DialogInput02, False )
								self.SetEnableControl( E_DialogInput03, True )							
							else :
								self.SetEnableControl( E_DialogInput02, True )
								self.SetEnableControl( E_DialogInput03, True )
					else : #E_DAILY
						self.SetEnableControl( E_DialogSpinDay, False )
						if self.mIsRunningTimer == True :
							self.SetEnableControl( E_DialogInput02, False )
							self.SetEnableControl( E_DialogInput03, True )							
							self.SetFocus( E_DialogInput03 )								
						else :
							self.SetEnableControl( E_DialogInput02, True )
							self.SetEnableControl( E_DialogInput03, True )
							self.SetFocus( E_DialogInput02 )							

			else :
				self.SetEnableControl(E_DialogSpinEx01, True )
				self.SelectPosition( E_DialogSpinEx01, self.mRecordingMode )

				self.SetEnableControl( E_DialogInput01,  True )
				self.SetControlLabel2String( E_DialogInput01, self.mRecordName )

				if self.mRecordingMode == E_ONCE :
					startTime = self.mWeeklyStart + self.mUsedWeeklyList[0].mStartTime
					endTime = startTime + self.mUsedWeeklyList[0].mDuration

					self.SelectPosition( E_DialogSpinDay, self.mSelectedWeekOfDay )	
					self.SetEnableControl( E_DialogSpinDay, False )						
					self.SetVisibleControl( E_DialogSpinDay, False )

					self.SelectPosition( E_DialogSpinEx02, 0 )
					self.SetListControlItemLabel( E_DialogSpinEx02, TimeToString( startTime, TimeFormatEnum.E_AW_DD_MM_YYYY ) )

					#self.SetEnableControl( E_DialogSpinEx02, False )
					#self.SetVisibleControl( E_DialogSpinEx02, True )					

					self.SetControlLabel2String( E_DialogInput02, TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
					self.SetControlLabel2String( E_DialogInput03, TimeToString( endTime, TimeFormatEnum.E_HH_MM) )

				else :

					self.SelectPosition( E_DialogSpinEx01, self.mRecordingMode )
					self.SelectPosition( E_DialogSpinEx02, 0 )

					listItems = self.GetListItems( E_DialogSpinDay )

					for i in range( len(listItems) ) :
						if self.mUsedWeeklyList[i].mUsed == True :
							listItems[i].setProperty( 'Used', 'True')
						else :
							listItems[i].setProperty( 'Used', 'False')

					self.SelectPosition( E_DialogSpinDay, self.mSelectedWeekOfDay )					
					self.SetVisibleControl( E_DialogSpinDay, True )

					#self.SetVisibleControl( E_DialogSpinEx02, False )					

					if self.mRecordingMode == E_WEEKLY :
						self.SetEnableControl( E_DialogSpinDay, True )
					else :
						self.SetEnableControl( E_DialogSpinDay, False )
						
					startTime = self.mUsedWeeklyList[ self.mSelectedWeekOfDay ].mStartTime
					endTime = startTime + self.mUsedWeeklyList[ self.mSelectedWeekOfDay ].mDuration

					self.SetControlLabel2String( E_DialogInput02, TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
					self.SetControlLabel2String( E_DialogInput03, TimeToString( endTime, TimeFormatEnum.E_HH_MM) )

					if self.mRecordingMode == E_WEEKLY and self.mUsedWeeklyList[ self.mSelectedWeekOfDay ].mUsed == False :
						self.SetEnableControl( E_DialogInput02, False )
						self.SetEnableControl( E_DialogInput03, False )
					else :
						self.SetEnableControl( E_DialogInput02, True )
						self.SetEnableControl( E_DialogInput03, True )

				if self.mTimerMode == E_VIEW_MODE :
					self.SetFocus( E_DialogSpinEx03 )
				else :
					self.SetFocus( E_DialogSpinEx01 )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )		


	def ChangeWeeklyDay( self ) :
		selectIndex = self.GetSelectedIndex( E_DialogSpinDay )
		LOG_TRACE( 'selectIndex = %d' %selectIndex )
		if selectIndex >= 0 and selectIndex < len( self.mUsedWeeklyList ) :
			self.mSelectedWeekOfDay	= selectIndex

			try :
				usedWeekly = self.mUsedWeeklyList[ self.mSelectedWeekOfDay ]
				usedWeekly = self.mUsedWeeklyList[ self.mSelectedWeekOfDay ]
				#self.mUsedWeeklyList[ self.mSelectedWeekOfDay ].printdebug( )
				strStartTime = TimeToString( self.mUsedWeeklyList[ self.mSelectedWeekOfDay ].mStartTime, TimeFormatEnum.E_HH_MM )
				strEndTime = TimeToString( self.mUsedWeeklyList[ self.mSelectedWeekOfDay ].mStartTime + self.mUsedWeeklyList[ self.mSelectedWeekOfDay ].mDuration, TimeFormatEnum.E_HH_MM )
			except Exception, ex :
				LOG_ERR( "Exception %s" %ex )		
			
			self.SetControlLabel2String( E_DialogInput02, strStartTime )
			self.SetControlLabel2String( E_DialogInput03, strEndTime )			

			if self.mUsedWeeklyList[ selectIndex ].mUsed == False :
				self.SetEnableControl( E_DialogInput02, False )
				self.SetEnableControl( E_DialogInput03, False )
			else :
				if self.mIsRunningTimer == True :
					self.SetEnableControl( E_DialogInput02, False )
					self.SetEnableControl( E_DialogInput03, True )							
				else :
					self.SetEnableControl( E_DialogInput02, True )
					self.SetEnableControl( E_DialogInput03, True )
			
			return


	def ChangeStartDay( self, aIsNext ) :

		if self.mTimer and self.mRecordingMode == E_ONCE :

			if aIsNext == True :
				newStart = self.mTimer.mStartTime + ONE_DAY_SECONDS
			else :
				newStart = self.mTimer.mStartTime - ONE_DAY_SECONDS		

			if newStart < self.mDataCache.Datetime_GetLocalTime( ) :
				newStart = self.mTimer.mStartTime

			self.mTimer.mStartTime = newStart

			LOG_TRACE( 'New StartTime =%s' %TimeToString( self.mTimer.mStartTime, TimeFormatEnum.E_AW_DD_MM_YYYY ) )
			self.SetListControlItemLabel( E_DialogSpinEx02, TimeToString( self.mTimer.mStartTime, TimeFormatEnum.E_AW_DD_MM_YYYY ) )

		else :
			days = int( self.mDataCache.Datetime_GetLocalTime( )/ONE_DAY_SECONDS )
			currentWeeekyStart = days * ONE_DAY_SECONDS

			if aIsNext == True :
				newWeekyStart = self.mWeeklyStart + ONE_DAY_SECONDS
			else :
				newWeekyStart = self.mWeeklyStart - ONE_DAY_SECONDS		

			if newWeekyStart < currentWeeekyStart :
				self.mWeeklyStart = currentWeeekyStart
			else :
				self.mWeeklyStart = newWeekyStart

			LOG_TRACE( 'New StartTime =%s' %TimeToString( self.mWeeklyStart, TimeFormatEnum.E_AW_DD_MM_YYYY ) )
			self.SetListControlItemLabel( E_DialogSpinEx02, TimeToString( self.mWeeklyStart, TimeFormatEnum.E_AW_DD_MM_YYYY ) )


	def ShowRecordName( self ) :
		try :
			kb = xbmc.Keyboard( self.mRecordName, MR_LANG( 'Rename timer' ), False )			
			kb.doModal( )
			if kb.isConfirmed( ) :
				keyword = kb.getText( )
				LOG_TRACE( 'keyword len=%d' %len( keyword ) )
				if len( keyword ) < MININUM_KEYWORD_SIZE :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'A timer name must be at least %d characters long' ) % MININUM_KEYWORD_SIZE )
					dialog.doModal( )
					return

				self.mRecordName = keyword
				self.SetControlLabel2String( E_DialogInput01, self.mRecordName )
				
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )	


	def SelectWeeklyDay( self ) :
		selectIndex = self.GetSelectedIndex( E_DialogSpinDay )
		LOG_TRACE( 'selectIndex = %d' %selectIndex )
		if selectIndex >= 0 and selectIndex < len(self.mUsedWeeklyList ) :
			listItems = self.GetListItems( E_DialogSpinDay )

			if self.mUsedWeeklyList[ selectIndex ].mUsed == True :
				self.mUsedWeeklyList[ selectIndex ].mUsed = False
				listItems[ selectIndex ].setProperty( 'Used', 'False')
			else:
				self.mUsedWeeklyList[ selectIndex ].mUsed = True
				listItems[ selectIndex ].setProperty( 'Used', 'True')				

			if self.mUsedWeeklyList[ selectIndex ].mUsed == False :
				self.SetEnableControl( E_DialogInput02, False )
				self.SetEnableControl( E_DialogInput03, False )
			else :
				self.SetEnableControl( E_DialogInput02, True )
				self.SetEnableControl( E_DialogInput03, True )
			

	def DoAddTimer( self ) :
		try :
			if self.mTimer :
				LOG_TRACE( 'Edit Mode' )
				if self.mIsRunningTimer and self.mRecordingMode == E_ONCE :
					#if self.mRecordingMode == E_ONCE :
					startTime = self.mTimer.mStartTime
					endTime = startTime + self.mTimer.mDuration
					#Normalize EndTime
					tmpEndTime = int( endTime/60 )
					endTime = tmpEndTime * 60

					LOG_TRACE( 'startTime=%s' %TimeToString( startTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
					LOG_TRACE( 'endTime=%s' %TimeToString( endTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )						
					ret = self.mDataCache.Timer_EditRunningTimer( self.mTimer.mTimerId, endTime )
					LOG_TRACE( 'RET=%s' %ret )
					if ret[0].mParam == -1 or ret[0].mError == -1 :					
						self.mConflictTimer = ret
						self.mErrorMessage = MR_LANG( 'Unable to edit the timer' )
						return False
					"""
					else: #E_DAILY or E_WEEKLY
						count = len( self.mUsedWeeklyList )
						for i in range( count ) :
							weeklyTimer = self.FindWeeklyTimerByDate( self.mUsedWeeklyList[i].mDate )
							LOG_TRACE( 'EditWeekly i=%d' %i )
							if weeklyTimer == None :
								if self.mUsedWeeklyList[i].mUsed == True : #Add New WeeklyTimer
									LOG_TRACE( 'EditWeekly Add New' )
									ret = self.mDataCache.Timer_AddOneWeeklyTimer( self.mTimer.mTimerId, self.mUsedWeeklyList[i].mDate, self.mUsedWeeklyList[i].mStartTime, self.mUsedWeeklyList[i].mDuration )
									LOG_TRACE( 'ret=%s' %ret )									
							else :
								if self.mUsedWeeklyList[i].mUsed == False : #Delete WeeklyTimer
									LOG_TRACE( 'EditWeekly Delete' )								
									ret = self.mDataCache.Timer_DeleteOneWeeklyTimer( self.mTimer.mTimerId, weeklyTimer.mDate, \
									weeklyTimer.mStartTime, weeklyTimer.mDuration )
									LOG_TRACE( 'ret=%s' %ret )
								else : #Change Timer
									LOG_TRACE( 'EditWeekly Change' )								
									ret = self.mDataCache.Timer_EditOneWeeklyTimer( self.mTimer.mTimerId, weeklyTimer.mDate, \
									weeklyTimer.mStartTime, weeklyTimer.mDuration, self.mUsedWeeklyList[i].mStartTime, self.mUsedWeeklyList[i].mDuration )
									LOG_TRACE( 'ret=%s' %ret )
					"""
					return True

				else : 
					if self.mRecordingMode == E_ONCE :
						#self.mDataCache.Timer_DeleteTimer( self.mTimer.mTimerId )

						startTime = self.mTimer.mStartTime
						endTime = startTime + self.mTimer.mDuration
						LOG_TRACE( 'startTime=%s' %TimeToString( startTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
						LOG_TRACE( 'endTime=%s' %TimeToString( endTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )						

						#Normalize EndTime
						tmpEndTime = int( endTime/60 )
						endTime = tmpEndTime * 60
						self.mTimer.mDuration = endTime - startTime
						#aTimerId, aNewStartTime, aNewDuration
						ret = self.mDataCache.Timer_EditManualTimer( self.mTimer.mTimerId, self.mTimer.mStartTime, self.mTimer.mDuration )

						if ret[0].mParam == -1 or ret[0].mError == -1 :
							self.mConflictTimer = ret
							self.mErrorMessage = MR_LANG( 'Error' )
							return False
						else :
							self.mConflictTimer = None
							return True
					else :
						count = len( self.mUsedWeeklyList )
						for i in range( count ) :
							weeklyTimer = self.FindWeeklyTimerByDate( self.mUsedWeeklyList[i].mDate )
							LOG_TRACE( 'Edit Weekly i=%d' %i )
							if weeklyTimer == None :
								if self.mUsedWeeklyList[i].mUsed == True : #Add New WeeklyTimer
									LOG_TRACE( 'Edit Weekly Add New' )
									#Normalize EndTime
									tmpEndTime = int( ( self.mUsedWeeklyList[i].mStartTime + self.mUsedWeeklyList[i].mDuration )/60 )
									endTime = tmpEndTime * 60
									self.mUsedWeeklyList[i].mDuration = endTime - self.mUsedWeeklyList[i].mStartTime

									ret = self.mDataCache.Timer_AddOneWeeklyTimer( self.mTimer.mTimerId, self.mUsedWeeklyList[i].mDate, self.mUsedWeeklyList[i].mStartTime, self.mUsedWeeklyList[i].mDuration )
									LOG_TRACE( 'ret=%s' %ret )									
							else :
								if self.mUsedWeeklyList[i].mUsed == False : #Delete WeeklyTimer
									LOG_TRACE( 'Edit Weekly Delete' )
									ret = self.mDataCache.Timer_DeleteOneWeeklyTimer( self.mTimer.mTimerId, weeklyTimer.mDate, \
									weeklyTimer.mStartTime, weeklyTimer.mDuration )
									LOG_TRACE( 'ret=%s' %ret )
								else : #Change Timer
									LOG_TRACE( 'Edit Weekly Change' )
									#Normalize EndTime
									tmpEndTime = int( ( self.mUsedWeeklyList[i].mStartTime + self.mUsedWeeklyList[i].mDuration )/60 )
									endTime = tmpEndTime * 60
									self.mUsedWeeklyList[i].mDuration = endTime - self.mUsedWeeklyList[i].mStartTime

									ret = self.mDataCache.Timer_EditOneWeeklyTimer( self.mTimer.mTimerId, weeklyTimer.mDate, \
									weeklyTimer.mStartTime, weeklyTimer.mDuration, self.mUsedWeeklyList[i].mStartTime, self.mUsedWeeklyList[i].mDuration )
									LOG_TRACE( 'ret=%s' %ret )
						
				return True
				
			#debug
			"""
			for i in range( len(self.mUsedWeeklyList) ) :
				LOG_TRACE('index=%d' %i )
				LOG_TRACE('used=%d' %self.mUsedWeeklyList[i].mUsed )
				LOG_TRACE('date=%d' %self.mUsedWeeklyList[i].mDate )
				LOG_TRACE('startTime=%s' %TimeToString(self.mWeeklyStart, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
				LOG_TRACE('weeklyTime=%s' %TimeToString(self.mUsedWeeklyList[i].mStartTime, TimeFormatEnum.E_HH_MM ) )
			"""

			if self.mRecordingMode == E_ONCE :
				startTime = self.mWeeklyStart + self.mUsedWeeklyList[0].mStartTime
				if  startTime + self.mUsedWeeklyList[0].mDuration < self.mDataCache.Datetime_GetLocalTime( ) :
					self.mErrorMessage = MR_LANG( 'The time you entered has already passed' )					
					return False

				if self.mTimerMode == E_VIEW_MODE :
					if  startTime  < self.mDataCache.Datetime_GetLocalTime( ) :
						self.mErrorMessage = MR_LANG( 'The time you entered has already passed' )					
						return False
					ret = self.mDataCache.Timer_AddViewTimer( self.mChannel.mNumber, self.mChannel.mServiceType, startTime, self.mRecordName )
				else :
					volumeId = 0
					if self.mNetVolume :
						volumeId = self.mNetVolume.mIndexID
					ret = self.mDataCache.Timer_AddManualTimer( self.mChannel.mNumber, self.mChannel.mServiceType, startTime, self.mUsedWeeklyList[0].mDuration, self.mRecordName, True, volumeId )

				if ret[0].mParam == -1 or ret[0].mError == -1 :
					self.mConflictTimer = ret
					self.mErrorMessage = MR_LANG( 'Error' )
					return False
				else :
					self.mConflictTimer = None
					return True

			else :
				count = len( self.mUsedWeeklyList )
				weeklyTimerList = []

				localTime = self.mDataCache.Datetime_GetLocalTime( )
				struct_time = time.gmtime( localTime  )


				for i in range( count ) :
					if self.mUsedWeeklyList[i].mUsed == True and self.mDataCache.Datetime_GetLocalTime() < self.mWeeklyEnd :
						timer = ElisIWeeklyTimer( )
						timer.mDate = i

						"""
						if weekday == timer.mDate and \
						(( self.mWeeklyStart + self.mUsedWeeklyList[i].mStartTime ) <=  localTime ) and \
						(( self.mWeeklyStart + self.mUsedWeeklyList[i].mStartTime + self.mUsedWeeklyList[i].mDuration ) > localTime ) :
								timer.mStartTime = 	localTime/(24*3600) + 5
								timer.mDuration = self.mWeeklyStart + self.mUsedWeeklyList[i].mStartTime + self.mUsedWeeklyList[i].mDuration - localTime
						else :
							timer.mStartTime = self.mUsedWeeklyList[i].mStartTime
							timer.mDuration = self.mUsedWeeklyList[i].mDuration
						"""

						timer.mStartTime = self.mUsedWeeklyList[i].mStartTime
						timer.mDuration = self.mUsedWeeklyList[i].mDuration

						#Normalize EndTime
						tmpEndTime = int( ( timer.mStartTime + timer.mDuration )/60 )
						endTime = tmpEndTime * 60
						timer.mDuration = endTime - timer.mStartTime
						
						weeklyTimerList.append( timer )

				if len( weeklyTimerList ) <= 0 :
					self.mErrorMessage = MR_LANG( 'There is no valid timer' )
					return False

				"""
				LOG_TRACE( 'Channel Number=%d' %self.mChannel.mNumber )
				LOG_TRACE( 'Service Type=%d' %self.mChannel.mServiceType )
				LOG_TRACE( 'Record Name=%s' %self.mRecordName )
				LOG_TRACE( 'weeklyTimerCount=%d'  %len( weeklyTimerList ) )
				LOG_TRACE( 'weeklyTimer=%s' %weeklyTimerList )
				"""

				ret = self.mDataCache.Timer_AddWeeklyTimer( self.mChannel.mNumber, self.mChannel.mServiceType, self.mWeeklyStart, self.mWeeklyEnd, self.mRecordName, True, len( weeklyTimerList ), weeklyTimerList )
				LOG_TRACE( 'ret=%s' %ret )				

				if ret and ( ret[0].mParam == -1 or ret[0].mError == -1 ) :
					self.mConflictTimer = ret
					self.mErrorMessage = MR_LANG( 'Error' )
					return False
				else :
					self.mConflictTimer = None
					return True

				return True

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		return False

			
	def ShowStartTime( self ) :

		try :
		
			focusId = self.GetFocusId( )

			strStartTime = self.GetControlLabel2String( E_DialogInput02 )

			selectIndex = self.GetSelectedIndex( E_DialogSpinDay )

			if self.mTimer and self.mRecordingMode == E_ONCE :
				strStartTime = TimeToString( self.mTimer.mStartTime, TimeFormatEnum.E_HH_MM )
			else :
				if self.mRecordingMode == E_DAILY or self.mRecordingMode == E_WEEKLY :
					strStartTime = TimeToString( self.mUsedWeeklyList[selectIndex].mStartTime, TimeFormatEnum.E_HH_MM )
				else :
					strStartTime = TimeToString( self.mUsedWeeklyList[0].mStartTime, TimeFormatEnum.E_HH_MM )			

			strStartTime = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_TIME, MR_LANG( 'Enter Start Time' ), strStartTime )

			tempList = strStartTime.split( ':', 1 )

			startHour = int( tempList[0] )
		
			startMin = int( tempList[1] )

			if self.mTimer and self.mRecordingMode == E_ONCE :
				startTime = startHour*3600 + startMin*60

				days = int( self.mTimer.mStartTime/ONE_DAY_SECONDS )

				self.mTimer.mStartTime	= days*ONE_DAY_SECONDS + startTime

				strStartTime = TimeToString( self.mTimer.mStartTime, TimeFormatEnum.E_HH_MM )
				strEndTime = TimeToString( self.mTimer.mStartTime + self.mTimer.mDuration, TimeFormatEnum.E_HH_MM )

			elif self.mRecordingMode == E_WEEKLY  :
				LOG_TRACE( 'selectIndex=%d' %selectIndex )
				self.mUsedWeeklyList[ selectIndex ].mStartTime = startHour*3600 + startMin*60
				strStartTime = TimeToString( self.mUsedWeeklyList[ selectIndex ].mStartTime, TimeFormatEnum.E_HH_MM )
				strEndTime = TimeToString( self.mUsedWeeklyList[ selectIndex ].mStartTime + self.mUsedWeeklyList[ selectIndex ].mDuration, TimeFormatEnum.E_HH_MM )
			else :
				for i in range( len( self.mUsedWeeklyList) ) :
					self.mUsedWeeklyList[i].mStartTime = startHour*3600 + startMin*60

				strStartTime = TimeToString( self.mUsedWeeklyList[0].mStartTime, TimeFormatEnum.E_HH_MM )
				strEndTime = TimeToString( self.mUsedWeeklyList[0].mStartTime + self.mUsedWeeklyList[0].mDuration, TimeFormatEnum.E_HH_MM )

			self.SetControlLabel2String( E_DialogInput02, strStartTime )
			self.SetControlLabel2String( E_DialogInput03, strEndTime )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def ShowEndTime( self ) :	
		try :

			LOG_TRACE( '' )
			focusId = self.GetFocusId( )
			
			strEndTime = self.GetControlLabel2String( E_DialogInput03 )

			selectIndex = self.GetSelectedIndex( E_DialogSpinDay )

			if self.mTimer and self.mRecordingMode == E_ONCE :
				strEndTime = TimeToString( self.mTimer.mStartTime + self.mTimer.mDuration, TimeFormatEnum.E_HH_MM )
			else :
				if self.mRecordingMode == E_DAILY or self.mRecordingMode == E_WEEKLY :
					strEndTime = TimeToString( self.mUsedWeeklyList[ selectIndex ].mStartTime + self.mUsedWeeklyList[ selectIndex ].mDuration, TimeFormatEnum.E_HH_MM )
				else :
					strEndTime = TimeToString( self.mUsedWeeklyList[0].mStartTime + self.mUsedWeeklyList[0].mDuration, TimeFormatEnum.E_HH_MM )			

			strEndTime = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_TIME, MR_LANG( 'Enter End Time' ), strEndTime )

			tempList = strEndTime.split( ':', 1 )

			endHour = int( tempList[0] )
			
			endMin = int( tempList[1] )

			if self.mTimer and self.mRecordingMode == E_ONCE :
				endTime = endHour*3600 + endMin*60

				strStartTime = TimeToString( self.mTimer.mStartTime, TimeFormatEnum.E_HH_MM )

				tempList = strStartTime.split( ':', 1 )

				startHour = int( tempList[0] )
				
				startMin = int( tempList[1] )
				
				startTime = startHour*3600 + startMin*60

				duration = endTime - startTime

				if duration <= 0 :
					duration = duration + ONE_DAY_SECONDS

				if duration <= 0 :
					prop = ElisPropertyEnum( 'Default Rec Duration', self.mCommander )
					duration = prop.GetProp( )

				self.mTimer.mDuration = duration
				strEndTime = TimeToString( self.mTimer.mStartTime + self.mTimer.mDuration, TimeFormatEnum.E_HH_MM )
			
			elif self.mRecordingMode == E_WEEKLY :
				endTime = endHour*3600 + endMin*60
				duration = endTime - self.mUsedWeeklyList[selectIndex].mStartTime

				if duration <= 0 :
					duration = duration + ONE_DAY_SECONDS

				if duration <= 0 :
					prop = ElisPropertyEnum( 'Default Rec Duration', self.mCommander )
					duration = prop.GetProp( )

				self.mUsedWeeklyList[selectIndex].mDuration = duration
				strEndTime = TimeToString( self.mUsedWeeklyList[selectIndex].mStartTime + self.mUsedWeeklyList[selectIndex].mDuration, TimeFormatEnum.E_HH_MM )				

			else :
				endTime = endHour*3600 + endMin*60
				duration = endTime - self.mUsedWeeklyList[0].mStartTime

				if duration <= 0 :
					duration = duration + ONE_DAY_SECONDS

				if duration <= 0 :
					prop = ElisPropertyEnum( 'Default Rec Duration', self.mCommander )
					duration = prop.GetProp( )

				for i in range( len(self.mUsedWeeklyList) ) :
					self.mUsedWeeklyList[i].mDuration = duration

				strEndTime = TimeToString( self.mUsedWeeklyList[0].mStartTime + self.mUsedWeeklyList[0].mDuration, TimeFormatEnum.E_HH_MM )

			self.SetControlLabel2String( E_DialogInput03, strEndTime )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def FindWeeklyTimerByDate( self, aDate ) :
		if self.mTimer == None :
			return None
			
		for i in range( self.mTimer.mWeeklyTimerCount ) :
			weeklyTimer = self.mTimer.mWeeklyTimer[i]
			if self.mTimer.mWeeklyTimer[i].mDate == aDate :
				return weeklyTimer

		return None


	def EnableSelectChannel( self, aEnable ) :
		self.mEnableSelectChannel = aEnable


	def ShowSelectChannel( self ) :
		dialog = xbmcgui.Dialog( )
		channelNameList = []
		channelList = self.mDataCache.Channel_GetList( )
		channelIndex = 0
		count = 0
		for channel in channelList :
			iChNumber = channel.mNumber
			if iChNumber == self.mChannel.mNumber :
				channelIndex = count
			if E_V1_2_APPLY_PRESENTATION_NUMBER :
				iChNumber = self.mDataCache.CheckPresentationNumber( channel )
			channelNameList.append( '%04d %s' %( iChNumber, channel.mName ) )
			count += 1

		iChNumber = self.mChannel.mNumber
		if E_V1_2_APPLY_PRESENTATION_NUMBER :
			iChNumber = self.mDataCache.CheckPresentationNumber( self.mChannel )

		ret = dialog.select( MR_LANG( 'Select Channel' ), channelNameList, False, channelIndex )

		if ret >= 0 :
			self.mChannel = channelList[ ret ]
			self.mRecordName = self.mChannel.mName
			self.SetControlLabel2String( E_DialogInput01, self.mRecordName )			

	
