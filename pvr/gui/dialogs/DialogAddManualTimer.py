from pvr.gui.WindowImport import *


# Control IDs
E_LABEL_RECORD_NAME			= 101
E_LABEL_EPG_START_TIME		= 102
E_LABEL_EPG_END_TIME		= 103
E_BUTTON_ADD				= 200
E_BUTTON_CANCEL				= 201

E_ONCE						= 0
E_DAILY						= 1
E_WEEKLY					= 2


WEEKLY_DEFALUT_EXPIRE_DAYS	= 7

LIST_RECORDING_MODE	= [ MR_LANG( 'Once' ), MR_LANG( 'Daily' ), MR_LANG( 'Weekly' ) ]
LIST_WEEKLY = [ MR_LANG( 'Sun' ), MR_LANG( 'Mon'), MR_LANG( 'Tue' ), MR_LANG( 'Wed' ), MR_LANG( 'Thu' ), MR_LANG( 'Fri' ), MR_LANG( 'Sat' ) ]

MININUM_KEYWORD_SIZE  		= 3
ONE_DAY_SECONDS				= 3600*24


class UsedWeeklyTimer( ElisIWeeklyTimer ) :
	def __init__( self ) :
		ElisIWeeklyTimer.__init__( self )
		self.mUsed = False


class DialogAddManualTimer( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		self.mEPG = None
		self.mRecordingMode = E_ONCE
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


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		if self.mTimer :
			self.SetHeaderLabel( MR_LANG( 'Edit Timer' ) )
		else :
			self.SetHeaderLabel( MR_LANG( 'Add Manual Timer' ) )

		if self.mTimer :
			self.mRecordName = self.mTimer.mName
		elif self.mEPG  :
			self.mRecordName = self.mEPG.mEventName
		else :
			self.mRecordName = self.mChannel.mName

		self.Reload( )

		self.mIsOk = E_DIALOG_STATE_CANCEL

		self.DrawItem( )

		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_OK_ID, MR_LANG( 'Confirm' ) )
		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_CANCEL_ID, MR_LANG( 'Cancel' ) )
		

	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.GetFocusId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.ResetAllControl( )
			self.Close( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			groupId = self.GetGroupId( focusId )

			if groupId == E_DialogInput01 :
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


	def onClick( self, aControlId ) :

		groupId = self.GetGroupId( aControlId )

		if groupId == E_SETTING_DIALOG_BUTTON_OK_ID :			
			if self.DoAddTimer() == False :
				self.mIsOk = E_DIALOG_STATE_ERROR
			
			self.ResetAllControl( )
			self.Close( )

		elif groupId == E_SETTING_DIALOG_BUTTON_CANCEL_ID :
			self.mIsOk = E_DIALOG_STATE_NO
			self.ResetAllControl( )
			self.Close( )


	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		pass
		"""
		if xbmcgui.getCurrentWindowDialogId( ) == self.winId :
			print 'Do Event'
			pass
		"""


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


	def Close( self ) :
		#self.mEventBus.Deregister( self )
		self.CloseDialog( )


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
						weeklyTimer.printdebug( )
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

				if self.mEPG :
					startTime = self.mEPG.mStartTime + self.mDataCache.Datetime_GetLocalOffset( )
					duraton = self.mEPG.mDuration
					self.mRecordName = self.mEPG.mEventName					
				else :
					self.mRecordName = self.mChannel.mName

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

		try :

			self.ResetAllControl( )
			self.AddUserEnumControl( E_DialogSpinEx01, MR_LANG( 'Recording' ), LIST_RECORDING_MODE, self.mRecordingMode )
			self.AddInputControl( E_DialogInput01, MR_LANG( 'Name' ),  MR_LANG( 'Record Name' ) )
			self.AddUserEnumControl( E_DialogSpinEx02, MR_LANG( 'Start Date' ), [ MR_LANG( 'Date' ) ], 0 )			
			#self.AddInputControl(  E_DialogSpinEx02, 'Date', 'Date' )
			self.AddListControl( E_DialogSpinDay, LIST_WEEKLY, self.mSelectedWeekOfDay )
			self.SetListControlTitle( E_DialogSpinDay, MR_LANG( 'Daily' ) )			
			self.AddInputControl( E_DialogInput02, MR_LANG( 'Start Time' ),  '00:00' )
			self.AddInputControl( E_DialogInput03, MR_LANG( 'End Time' ),  '00:00' )			
			self.AddOkCanelButton( )

			self.SetAutoHeight( True )
			self.InitControl( )
			
			self.ChangeRecordMode( )
			self.UpdateLocation( )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )
		

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
					#self.SetVisibleControl( E_DialogSpinEx02, True )
					self.SetListControlItemLabel( E_DialogSpinEx02, TimeToString( startTime, TimeFormatEnum.E_AW_DD_MM_YYYY ) )
					self.SetEnableControl( E_DialogSpinEx02, False )
					
					self.SetControlLabel2String( E_DialogInput02, TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
					self.SetControlLabel2String( E_DialogInput03, TimeToString( endTime, TimeFormatEnum.E_HH_MM) )

					if self.mIsRunningTimer == True :
						self.SetEnableControl( E_DialogInput02, False )
						self.SetFocus( E_DialogInput03 )
					else :
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
				self.mUsedWeeklyList[ self.mSelectedWeekOfDay ].printdebug( )
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
					LOG_TRACE( 'startTime=%s' %TimeToString( startTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
					LOG_TRACE( 'endTime=%s' %TimeToString( endTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )						
					ret = self.mDataCache.Timer_EditRunningTimer( self.mTimer.mTimerId, endTime )
					LOG_TRACE( 'RET=%s' %ret )
					if ret == False :
						self.mErrorMessage = MR_LANG( 'Unable to edit the timer' )
						self.mConflictTimer = None
					return ret
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
						self.mDataCache.Timer_DeleteTimer( self.mTimer.mTimerId )

						startTime = self.mTimer.mStartTime
						endTime = startTime + self.mTimer.mDuration
						LOG_TRACE( 'startTime=%s' %TimeToString( startTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
						LOG_TRACE( 'endTime=%s' %TimeToString( endTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )						
						
						ret = self.mDataCache.Timer_AddManualTimer( self.mTimer.mChannelNo, self.mTimer.mServiceType, self.mTimer.mStartTime, self.mTimer.mDuration, self.mTimer.mName, True )

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

				ret = self.mDataCache.Timer_AddManualTimer( self.mChannel.mNumber, self.mChannel.mServiceType, startTime,	self.mUsedWeeklyList[0].mDuration, self.mRecordName, True )

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

				ret = self.mDataCache.Timer_AddWeeklyTimer( self.mChannel.mNumber, self.mChannel.mServiceType, self.mWeeklyStart, self.mWeeklyEnd, self.mRecordName, len( weeklyTimerList ), weeklyTimerList )
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

			strStartTime = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_TIME, MR_LANG( 'Enter the start time' ), strStartTime )			

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

			strEndTime = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_TIME, 'Enter the end time', strEndTime )	

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

