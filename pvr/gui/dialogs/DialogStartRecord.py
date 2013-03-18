from pvr.gui.WindowImport import *

# Control IDs
"""
E_LABEL_RECORD_NAME			= 101
E_LABEL_EPG_START_TIME		= 102
E_LABEL_EPG_END_TIME		= 103
E_BUTTON_START				= 200
E_BUTTON_CANCEL				= 201
E_PROGRESS_EPG				= 400
E_BUTTON_DURATION			= 501
E_LABEL_DURATION			= 502
"""

# Control IDs
E_LABEL_RECORD_NAME			= 101
E_GROUP_LIST_CONTROL		= 8000


E_FROM_NOW					= 0 
E_FROM_EPG					= 1


LIST_COPY_MODE =[ MR_LANG( 'No'), MR_LANG( 'Yes' ) ]


class DialogStartRecord( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		self.mTimer = None
		self.mOTRInfo = None
		self.mRecordingProgressThread = None
		self.mCurrentChannel = None
		self.mEnableProgress = False
		self.mStartTime = 0
		self.mEndTime = 0
		self.mCopyMode = E_FROM_NOW
		self.mConflictTimer = None		

	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		
		self.getControl( E_GROUP_LIST_CONTROL ).setVisible( False )
		self.SetHeaderLabel( MR_LANG( 'Start Recording' ) )

		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		
		self.Reload( )
		self.DrawItem( )

		#self.mEventBus.Register( self )
		
		self.mEnableThread = True
		#self.mRecordingProgressThread = self.RecordingProgressThread( )
		self.mDurationChanged = False
		self.mConflictTimer = None		

		self.getControl( E_GROUP_LIST_CONTROL ).setVisible( True )
		self.mIsOk = E_DIALOG_STATE_CANCEL


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.GetFocusId( )
		print ' actionID= %d, focusId = %d ' % (actionId,focusId )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			self.Close( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			groupId = self.GetGroupId( focusId )

			if groupId == E_DialogSpinEx01 :
				self.ChangeCopyMode( )

			elif groupId == E_DialogInput01 :
				pass

			elif groupId == E_DialogInput02 :
				self.ChangeEndTime( )

			elif groupId == E_DialogInput03 :
				self.ChangeDuraton( )

			elif groupId == E_SETTING_DIALOG_BUTTON_OK_ID :	
				self.StartRecord( )

			elif groupId == E_SETTING_DIALOG_BUTTON_CANCEL_ID :
				self.mIsOk = E_DIALOG_STATE_CANCEL
				self.ResetAllControl( )
				self.Close( )

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
	
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )
				
		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )

		else :
			LOG_WARN( 'Unknown Action' )


	def onClick( self, aControlId ) :
		focusId = self.GetFocusId( )
		if focusId == E_SETTING_DIALOG_BUTTON_CLOSE :
			self.ResetAllControl( )
			self.Close( )


	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		pass


	def IsOK( self ) :
		return self.mIsOk


	def GetConflictTimer( self ) :
		return self.mConflictTimer


	def Close( self ) :
		#self.mEventBus.Deregister( self )
		self.mEnableThread = False
		if self.mRecordingProgressThread :
			self.mRecordingProgressThread.join( )
		self.CloseDialog( )


	def Reload ( self ) :

		self.mLocalTime = self.mDataCache.Datetime_GetLocalTime( )	
		self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
		self.mTimer = self.mDataCache.GetRunnigTimerByChannel( )

		if self.mTimer :
			self.SetHeaderLabel( MR_LANG( 'Edit Recording' ) )
		else :
			self.mOTRInfo = self.mDataCache.Timer_GetOTRInfo( )
			self.mOTRInfo.printdebug( )
			self.CheckValidEPG( )
			self.mOTRInfo.printdebug( )
			self.mStartTime = self.mLocalTime
			self.mEndTime = self.mOTRInfo.mEventEndTime


	def CheckValidEPG( self ) :
		if self.mOTRInfo.mHasEPG :
			if self.mLocalTime >= self.mOTRInfo.mEventStartTime  and self.mLocalTime < self.mOTRInfo.mEventEndTime :
				return True

		self.mOTRInfo.mHasEPG = False
		prop = ElisPropertyEnum( 'Default Rec Duration', self.mCommander )
		self.mOTRInfo.mExpectedRecordDuration = prop.GetProp( )
		self.mOTRInfo.mEventStartTime = self.mLocalTime
		self.mOTRInfo.mEventEndTime = self.mLocalTime +	self.mOTRInfo.mExpectedRecordDuration
		self.mOTRInfo.mEventName = self.mCurrentChannel.mName
		return False


	def DrawItem( self ) :
		try :
			if self.mTimer :

				self.AddLabelControl( E_LABEL_RECORD_NAME )
				self.SetControlLabelString( E_LABEL_RECORD_NAME, self.mTimer.mName )

				self.SetVisibleControl( E_DialogSpinEx01, False )

				self.AddInputControl( E_DialogInput01, MR_LANG( 'Start Time' ),  TimeToString( self.mTimer.mStartTime, TimeFormatEnum.E_HH_MM ) )
				self.SetEnableControl( E_DialogInput01, False )									
				self.AddInputControl( E_DialogInput02, MR_LANG( 'End Time' ),  TimeToString( self.mTimer.mStartTime + self.mTimer.mDuration , TimeFormatEnum.E_HH_MM ) )
				self.AddInputControl( E_DialogInput03, MR_LANG( 'Duration' ),  '%d(%s)' %( int( self.mTimer.mDuration/60 ), MR_LANG('mins') ) )

			else :
				LOG_TRACE( 'self.mOTRInfo.mHasEPG=%d' %self.mOTRInfo.mHasEPG )

				#status = self.mDataCache.Player_GetStatus()				

				if self.mOTRInfo.mHasEPG == True :
					self.AddLabelControl( E_LABEL_RECORD_NAME )
					self.SetControlLabelString( E_LABEL_RECORD_NAME, '(%s~%s) %s' %(TimeToString( self.mOTRInfo.mEventStartTime, TimeFormatEnum.E_HH_MM ),
						TimeToString( self.mOTRInfo.mEventEndTime, TimeFormatEnum.E_HH_MM ), self.mOTRInfo.mEventName ) )
					
					if self.mOTRInfo.mTimeshiftAvailable :
						timeshiftRecordSec = int( self.mOTRInfo.mTimeshiftRecordMs/1000 )					
						copyTimeshift  = self.mLocalTime - self.mOTRInfo.mEventStartTime
						if copyTimeshift > timeshiftRecordSec :
							copyTimeshift = timeshiftRecordSec
	
						self.mStartTime = self.mLocalTime - copyTimeshift
						self.AddUserEnumControl( E_DialogSpinEx01, MR_LANG( 'From EPG' ), LIST_COPY_MODE, E_FROM_EPG)
						self.SetEnableControl( E_DialogSpinEx01, True )						
					else :
						self.AddUserEnumControl( E_DialogSpinEx01, MR_LANG( 'From EPG' ), LIST_COPY_MODE, E_FROM_NOW )
						self.SetEnableControl( E_DialogSpinEx01, False )

				else :
					self.AddLabelControl( E_LABEL_RECORD_NAME )
					self.SetControlLabelString(E_LABEL_RECORD_NAME, self.mOTRInfo.mEventName )

					self.AddUserEnumControl( E_DialogSpinEx01, MR_LANG( 'From EPG' ), LIST_COPY_MODE, E_FROM_NOW )
					self.SetEnableControl( E_DialogSpinEx01, False )

				duration = int( self.mEndTime/60 ) - int( self.mStartTime/60 )
				
				LOG_TRACE( 'Name=%s' %self.mOTRInfo.mEventName )
				LOG_TRACE( 'Start Time=%s' %TimeToString( self.mOTRInfo.mEventStartTime, TimeFormatEnum.E_HH_MM ) )
				LOG_TRACE( 'End Time=%s' %TimeToString( self.mOTRInfo.mEventEndTime, TimeFormatEnum.E_HH_MM ) )
				LOG_TRACE( 'Duration=%d' %int( self.mOTRInfo.mExpectedRecordDuration/60 ) )

				self.AddInputControl( E_DialogInput01, MR_LANG( 'Start Time' ),  TimeToString( self.mStartTime, TimeFormatEnum.E_HH_MM ) )
				self.SetEnableControl( E_DialogInput01, False )									
				self.AddInputControl( E_DialogInput02, MR_LANG( 'End Time' ),  TimeToString( self.mEndTime, TimeFormatEnum.E_HH_MM ) )
				self.AddInputControl( E_DialogInput03, MR_LANG( 'Duration' ),  '%d(%s)' %(duration, MR_LANG('mins') ) )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		self.AddOkCanelButton( )

		if self.mTimer :
			self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_OK_ID, MR_LANG( 'Change Duration' ) )
		else:
			self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_OK_ID, MR_LANG( 'Start' ) )			

		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_CANCEL_ID, MR_LANG( 'Cancel' ) )
		
		self.SetAutoHeight( True )

		self.InitControl( )
		self.UpdateLocation( )
		self.setFocusId( E_DialogInput03 )


	def ChangeCopyMode( self ) :
		if self.mTimer == None :
			if self.GetEnableControl( E_DialogSpinEx01 ) == True :
				copyMode = self.GetSelectedIndex( E_DialogSpinEx01 )			
				if copyMode == E_FROM_EPG :
					timeshiftRecordSec = int( self.mOTRInfo.mTimeshiftRecordMs/1000 )					
					copyTimeshift  = self.mLocalTime - self.mOTRInfo.mEventStartTime
					if copyTimeshift > timeshiftRecordSec :
						copyTimeshift = timeshiftRecordSec

					self.mStartTime = self.mLocalTime - copyTimeshift
					self.mEndTime = self.mOTRInfo.mEventEndTime
				else :
					self.mStartTime = self.mLocalTime
					self.mEndTime = self.mOTRInfo.mEventEndTime

				if self.mEndTime <= self.mStartTime :
					prop = ElisPropertyEnum( 'Default Rec Duration', self.mCommander )
					self.mEndTime = self.mStartTime + prop.GetProp( )

				duration = int( self.mEndTime/60 ) - int( self.mStartTime/60 )					
				self.SetControlLabel2String( E_DialogInput01, TimeToString( self.mStartTime, TimeFormatEnum.E_HH_MM ) )
				self.SetControlLabel2String( E_DialogInput02, TimeToString( self.mEndTime, TimeFormatEnum.E_HH_MM ) )
				self.SetControlLabel2String( E_DialogInput03, '%d(%s)' %( duration, MR_LANG('mins') ) )


	def ChangeEndTime( self ) :
		try :
			"""
			if self.mTimer :
				return;
			"""

			strEndTime = self.GetControlLabel2String( E_DialogInput02 )
			tempList = strEndTime.split( ':', 1 )
			orgEndHour = int( tempList[0] )
			orgEndMin = int( tempList[1] )
			
			strEndTime = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_TIME, MR_LANG( 'Enter the end time' ), strEndTime )		

			tempList = strEndTime.split( ':', 1 )

			endHour = int( tempList[0] )
			endMin = int( tempList[1] )

			LOG_TRACE( 'Hour=%d:%d Min=%d:%d' %( orgEndHour, endHour, orgEndMin, endMin ) )
			
			if orgEndHour == endHour and orgEndMin == endMin :
				return

			self.mDurationChanged = True

			if self.mTimer :
				tmpStartTime = self.mTimer.mStartTime			
				tmpEndTime = self.mTimer.mStartTime + self.mTimer.mDuration
			else :
				tmpStartTime = self.mStartTime
				tmpEndTime = self.mEndTime				
						
			LOG_TRACE( 'Before End Time=%s' %TimeToString( tmpEndTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )			
			days = int( tmpEndTime / ( 24*3600 ) )
			LOG_TRACE( 'days %d' %days )						
			tmpEndTime = days *( 24*3600 ) + endHour*3600 + endMin*60

			LOG_TRACE( 'After endTime=%d' %tmpEndTime )

			if tmpEndTime < tmpStartTime :
				tmpEndTime = tmpEndTime + 24*3600

			LOG_TRACE( 'End Hour=%d End Min=%d' %( endHour, endMin ) )
			LOG_TRACE( 'Changed End Time=%s' %TimeToString( tmpEndTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )

			if self.mTimer :
				duration = int( tmpEndTime/60 ) - int( self.mTimer.mStartTime/60 )
				self.mTimer.mDuration = duration * 60
			else :
				self.mEndTime = tmpEndTime			
				duration = int( tmpEndTime/60 ) - int( self.mStartTime/60 )
				
			self.SetControlLabel2String( E_DialogInput02, TimeToString( tmpEndTime, TimeFormatEnum.E_HH_MM ) )
			self.SetControlLabel2String( E_DialogInput03, '%d(%s)' %( duration, MR_LANG('mins') ) )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def ChangeDuraton( self ) :
		try :
			if self.mTimer :
				tempDuration = int( self.mTimer.mDuration/60 )
			else :
				tempDuration = int( self.mEndTime/60 ) - int( self.mStartTime/60 )

				
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( '%s(%s)' %( MR_LANG( 'Enter new duration' ), MR_LANG( 'in mins' ) ), '%d' %tempDuration  , 3 )
 			dialog.doModal( )

 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				duration = int( dialog.GetString( ) )
				LOG_TRACE( 'Duration = %d' % duration )

				if duration > 0 :
					if tempDuration != duration :
						self.mDurationChanged = True

					if self.mTimer :
						self.mTimer.mDuration = duration * 60 
					else :
						self.mEndTime = self.mStartTime + duration * 60

				if self.mTimer :
					self.SetControlLabel2String( E_DialogInput02, TimeToString( self.mTimer.mStartTime + self.mTimer.mDuration , TimeFormatEnum.E_HH_MM ) )
				else :
					self.SetControlLabel2String( E_DialogInput02, TimeToString( self.mEndTime, TimeFormatEnum.E_HH_MM ) )

				self.SetControlLabel2String( E_DialogInput03, '%d(%s)' %( duration, MR_LANG( 'mins' ) ) )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def StartRecord( self ) :
		try :
			if self.mTimer :
				self.mIsOk = E_DIALOG_STATE_CANCEL
				if self.mDurationChanged == True :
					if self.mTimer.mTimerType == ElisEnum.E_ITIMER_WEEKLY :
						LOG_TRACE( 'ToDO : Weekly timer is running' )
						endTime = self.mTimer.mStartTime + self.mTimer.mDuration						
					else :
						endTime = self.mTimer.mStartTime + self.mTimer.mDuration

					#Normalize EndTime
					tmpEndTime = int( endTime/60 )
					endTime = tmpEndTime * 60

					LOG_TRACE( 'NEW END TIME : %s' %TimeToString( endTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )				
					ret =  self.mDataCache.Timer_EditRunningTimer( self.mTimer.mTimerId, endTime )
					if ret[0].mParam == -1 or ret[0].mError == -1 :
						self.mConflictTimer = ret
						self.mIsOk = E_DIALOG_STATE_ERROR
					else :
						self.mIsOk = E_DIALOG_STATE_YES					

			else :
				copyTimeshift = 0
				otrInfo = self.mDataCache.Timer_GetOTRInfo( )
				self.mOTRInfo.mTimeshiftRecordMs = otrInfo.mTimeshiftRecordMs
				self.mLocalTime = self.mDataCache.Datetime_GetLocalTime( )				
				
				if self.mOTRInfo.mTimeshiftAvailable :
					"""
					if status.mMode == ElisEnum.E_MODE_TIMESHIFT : 	# Now Timeshifting
						copyTimeshift = int( (status.mEndTimeInMs - status.mPlayTimeInMs)/1000 )
						LOG_TRACE( 'copyTimeshift #1=%d' %copyTimeshift )
						if copyTimeshift > timeshiftRecordSec :
							copyTimeshift = timeshiftRecordSec
							LOG_TRACE( 'copyTimeshift #2=%d' %copyTimeshift )

					else :
					"""
					if self.GetEnableControl( E_DialogSpinEx01 ) == True and self.GetSelectedIndex( E_DialogSpinEx01 ) == E_FROM_EPG:
						status = self.mDataCache.Player_GetStatus( )
						timeshiftRecordSec = int( self.mOTRInfo.mTimeshiftRecordMs/1000 )
						LOG_ERR( "self.mDataCache.Player_GetStatus() = %d" %status.mMode)
						LOG_TRACE( 'mTimeshiftRecordMs=%dMs : %dSec' %(self.mOTRInfo.mTimeshiftRecordMs, timeshiftRecordSec ) )
					
						copyTimeshift  = self.mLocalTime - self.mOTRInfo.mEventStartTime
						LOG_TRACE( 'copyTimeshift #3=%d' %copyTimeshift )
						if copyTimeshift > timeshiftRecordSec :
							copyTimeshift = timeshiftRecordSec
						LOG_TRACE( 'copyTimeshift #4=%d' %copyTimeshift )


				LOG_TRACE( 'copyTimeshift=%d' %copyTimeshift )

				if copyTimeshift <  0 or copyTimeshift > 12*3600 : #12hour * 60min * 60sec
					copyTimeshift = 0

				#expectedDuration =  self.mEndTime - self.mStartTime - copyTimeshift
				#Normalize EndTime
				tmpEndTime = int( self.mEndTime/60 )
				self.mEndTime = tmpEndTime * 60
				expectedDuration =  self.mEndTime - self.mStartTime

				LOG_TRACE( 'expectedDuration=%d' %expectedDuration )

				if expectedDuration < 0:
					LOG_ERR( 'Error : Already Passed' )
					expectedDuration = 0

				ret = self.mDataCache.Timer_AddOTRTimer( False, expectedDuration, copyTimeshift, self.mOTRInfo.mEventName, True, 0, 0,  0, 0 )

				#if ret[0].mParam == -1 or ret[0].mError == -1 :
				LOG_ERR( 'StartDialog ret=%s ' %ret )
				if ret and ( ret[0].mParam == -1 or ret[0].mError == -1 ) :	
					LOG_ERR( 'StartDialog ' )
					self.mConflictTimer = ret
					self.mIsOk = E_DIALOG_STATE_ERROR
				else :
					self.mIsOk = E_DIALOG_STATE_YES
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		self.ResetAllControl( )
		self.Close( )

