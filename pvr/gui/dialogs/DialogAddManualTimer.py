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

LIST_RECORDING_MODE	= [ 'Once', 'Daily', 'Weekly' ]
LIST_WEEKLY = ['Sun', 'Mon','Tue', 'Wed', 'The', 'Fri', 'Sat' ]

MININUM_KEYWORD_SIZE  		= 3

class UsedWeeklyTimer( ElisIWeeklyTimer ) :
	def __init__( self ) :
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
		self.mRecordName = 'None'
		self.mErrorMessage = 'Unknown Error'		
		self.mWeeklyStart = 0
		self.mWekklyEnd = 0
		self.mConflictTimer = None


	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		if self.mTimer :
			self.SetHeaderLabel( 'Edit Recording' )		
		else :
			self.SetHeaderLabel( 'Add Manual Recording' )

		if self.mEPG  :
			self.mRecordName = self.mEPG.mEventName
		else :
			self.mRecordName = self.mChannel.mName

		self.Reload( )

		self.mIsOk = E_DIALOG_STATE_CANCEL

		self.DrawItem( )

		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_OK_ID, 'Confirm' )
		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_CANCEL_ID, 'Cancel' )

		

	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.GetFocusId( )
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU :
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

			elif groupId == E_DialogSpinDay :
				self.SelectWeeklyDay( )
				#self.DrawItem( )

			elif groupId == E_DialogInput03 :
				self.ShowStartTime( )

			elif groupId == E_DialogInput04 :
				self.ShowEndTime( )
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.ResetAllControl( )
			self.Close( )

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
				self.ControlLeft( )


		else :
			LOG_WARN( 'Unknown Action' )


	def onClick( self, aControlId ):

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


	def onFocus( self, aControlId ):
		pass


	@GuiLock	
	def onEvent( self, aEvent ):
		pass
		"""
		if xbmcgui.getCurrentWindowDialogId() == self.winId :
			print 'Do Event'
			pass
		"""


	def GetErrorMessage( self ) :
		return self.mErrorMessage


	def SetEPG( self, aEPG ):
		self.mEPG = aEPG


	def SetChannel( self, aChannel ) :
		self.mChannel = aChannel


	def SetTimer( self, aTimer ):
		self.mTimer = aTimer


	def IsOK( self ) :
		return self.mIsOk


	def GetConflictTimer( self ) :
		return self.mConflictTimer


	def Close( self ) :
		#self.mEventBus.Deregister( self )
		self.CloseDialog( )


	def Reload ( self ) :
		LOG_TRACE('')
		try :
			self.mSelectedWeekOfDay	= 0 
			self.mUsedWeeklyList = []

			if self.mTimer :
				LOG_TRACE('')
				if self.mTimer.mTimerType == ElisEnum.E_ITIMER_WEEKLY :
					self.mRecordingMode = E_WEEKLY
					self.mWeeklyStart = mTimer.mStartTime
					self.mWeeklyEnd = self.mWeeklyStart + WEEKLY_DEFALUT_EXPIRE_DAYS*24*3600 - 1											
					for i in range( 7 ) :
						usedTimer =  UsedWeeklyTimer()
						usedTimer.mDate = i
						self.mUsedWeeklyList.append( usedTimer )

					for i in range( self.mTimer.mWeeklyTimerCount ) :
						weeklyTimer = self.mTimer.mWeeklyTimer= [i]
						weeklyTimer.printdebug( )
						usedTimer = self.mUsedWeeklyList[weeklyTimer.mDate]
						usedTimer.mUsed =True
						usedTimer.mStartTime = weeklyTimer.mStartTime
						usedTimer.mDuration = weeklyTimer.mDuration
						if i == 0 :
							self.mSelectedWeekOfDay	= weeklyTimer.mDate
				else :
					self.mRecordingMode == E_ONCE 
					
			else :
				startTime = self.mDataCache.Datetime_GetLocalTime()
				prop = ElisPropertyEnum( 'Default Rec Duration', self.mCommander )
				duration = prop.GetProp( )

				if self.mEPG :
					startTime = self.mEPG.mStartTime + self.mDataCache.Datetime_GetLocalOffset()
					duraton = self.mEPG.mDuration
					self.mRecordName = self.mEPG.mEventName					
				else :
					self.mRecordName = self.mChannel.mName


				days = int( startTime/(24*3600) )
				self.mWeeklyStart = days*24*3600
				self.mWeeklyEnd = days*24*3600 + WEEKLY_DEFALUT_EXPIRE_DAYS*24*3600 - 1

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
						
					else :
						usedTimer.mUsed = True
						if i == weekday :
							self.mSelectedWeekOfDay	= weekday

					usedTimer.mDate = i
					usedTimer.mStartTime = startTime %( 24*3600 )
					usedTimer.mDuration = duration
					self.mUsedWeeklyList.append( usedTimer )
			
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex)

		return


	def DrawItem( self ) :
		LOG_TRACE('self.mRecordingMode=%d' %self.mRecordingMode )

		try :

			self.ResetAllControl( )
			self.AddUserEnumControl( E_DialogSpinEx01, 'Recording', LIST_RECORDING_MODE, self.mRecordingMode )
			self.AddInputControl( E_DialogInput01, 'Name',  'Record Name' )
			self.AddInputControl( E_DialogInput02, 'Date', 'Date' )
			self.AddListControl( E_DialogSpinDay, LIST_WEEKLY, self.mSelectedWeekOfDay )
			self.SetListControlTitle( E_DialogSpinDay, 'Daily' )			
			self.AddInputControl( E_DialogInput03, 'Start Time',  '00:00' )
			self.AddInputControl( E_DialogInput04, 'End Time',  '00:00' )			
			self.AddOkCanelButton( )

			self.SetAutoHeight( True )
			self.InitControl( )
			
			self.ChangeRecordMode( )
			self.UpdateLocation( )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex)
		

	def ChangeRecordMode( self ) :
		try :

			if self.mTimer :
				self.SelectPosition( E_DialogSpinEx01, self.mRecordingMode )
				self.SetEnableControl(E_DialogSpinEx01,  False )
				self.SetControlLabel2String( E_DialogInput01,  self.mTimer.mName )
				self.SetEnableControl(E_DialogInput01,  False )


				if self.mRecordingMode == E_ONCE :
					startTime = self.mTimer.mStartTime
					endTime = startTime + self.mTimer.mDuration
						
					self.SetVisibleControl( E_DialogSpinDay, False )
					self.SetVisibleControl( E_DialogInput02, True )
					self.SetControlLabel2String( E_DialogInput02, TimeToString( startTime, TimeFormatEnum.E_AW_DD_MM_YYYY ) )
					self.SetEnableControl( E_DialogInput02, False )
					
					self.SetControlLabel2String( E_DialogInput03, TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
					self.SetControlLabel2String( E_DialogInput04, TimeToString( endTime, TimeFormatEnum.E_HH_MM) )

				else :

					self.SelectPosition( E_DialogSpinEx01, self.mRecordingMode )
					listItems = self.GetListItems( E_DialogSpinDay )

					for i in range( len(listItems) ) :
						if self.mUsedWeeklyList[i].mUsed == True :
							listItems[i].setProperty( 'Used', 'True')
						else :
							listItems[i].setProperty( 'Used', 'False')
					
					self.SetVisibleControl( E_DialogSpinDay, True )

					self.SetVisibleControl( E_DialogInput02, False )					

					self.SetEnableControl( E_DialogSpinDay, True )
						
					startTime = self.mUsedWeeklyList[self.mSelectedWeekOfDay ].mStartTime
					endTime = startTime + self.mUsedWeeklyList[self.mSelectedWeekOfDay ].mDuration

					self.SetControlLabel2String( E_DialogInput03, TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
					self.SetControlLabel2String( E_DialogInput04, TimeToString( endTime, TimeFormatEnum.E_HH_MM) )

					if self.mRecordingMode == E_WEEKLY and self.mUsedWeeklyList[self.mSelectedWeekOfDay].mUsed == False:
						self.SetEnableControl( E_DialogInput03, False )
						self.SetEnableControl( E_DialogInput04, False )
					else :
						self.SetEnableControl( E_DialogInput03, True )
						self.SetEnableControl( E_DialogInput04, True )

					self.SetFocus( E_DialogInput03 )

			else :
				self.SetEnableControl(E_DialogSpinEx01, True )
				self.SelectPosition( E_DialogSpinEx01, self.mRecordingMode )

				self.SetEnableControl(E_DialogInput01,  True )
				self.SetControlLabel2String( E_DialogInput01, self.mRecordName )


				if self.mRecordingMode == E_ONCE :
					startTime = self.mWeeklyStart + self.mUsedWeeklyList[0].mStartTime
					endTime = startTime + self.mUsedWeeklyList[0].mDuration

					self.SetEnableControl( E_DialogSpinDay, False )						
					self.SetVisibleControl( E_DialogSpinDay, False )

					self.SetControlLabel2String( E_DialogInput02, TimeToString( startTime, TimeFormatEnum.E_AW_DD_MM_YYYY ) )

					self.SetEnableControl( E_DialogInput02, False )
					self.SetVisibleControl( E_DialogInput02, True )					

					self.SetControlLabel2String( E_DialogInput03, TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
					self.SetControlLabel2String( E_DialogInput04, TimeToString( endTime, TimeFormatEnum.E_HH_MM) )

				else :

					self.SelectPosition( E_DialogSpinEx01, self.mRecordingMode )
					listItems = self.GetListItems( E_DialogSpinDay )

					for i in range( len(listItems) ) :
						if self.mUsedWeeklyList[i].mUsed == True :
							listItems[i].setProperty( 'Used', 'True')
						else :
							listItems[i].setProperty( 'Used', 'False')
					
					self.SetVisibleControl( E_DialogSpinDay, True )

					self.SetVisibleControl( E_DialogInput02, False )					

					if self.mRecordingMode == E_WEEKLY :
						self.SetEnableControl( E_DialogSpinDay, True )
					else :
						self.SetEnableControl( E_DialogSpinDay, False )
						
					startTime = self.mUsedWeeklyList[self.mSelectedWeekOfDay ].mStartTime
					endTime = startTime + self.mUsedWeeklyList[self.mSelectedWeekOfDay ].mDuration

					self.SetControlLabel2String( E_DialogInput03, TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
					self.SetControlLabel2String( E_DialogInput04, TimeToString( endTime, TimeFormatEnum.E_HH_MM) )

					if self.mRecordingMode == E_WEEKLY and self.mUsedWeeklyList[self.mSelectedWeekOfDay].mUsed == False:
						self.SetEnableControl( E_DialogInput03, False )
						self.SetEnableControl( E_DialogInput04, False )
					else :
						self.SetEnableControl( E_DialogInput03, True )
						self.SetEnableControl( E_DialogInput04, True )
						
				self.SetFocus( E_DialogSpinEx01 )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex)		


	def ChangeWeeklyDay( self ) :
		selectIndex = self.GetSelectedIndex( E_DialogSpinDay )
		LOG_TRACE('selectIndex = %d' %selectIndex )
		if selectIndex >= 0 and selectIndex < len(self.mUsedWeeklyList) :
			self.mSelectedWeekOfDay	= selectIndex
			
			strStartTime = TimeToString( self.mUsedWeeklyList[self.mSelectedWeekOfDay ].mStartTime, TimeFormatEnum.E_HH_MM )
			strEndTime = TimeToString( self.mUsedWeeklyList[self.mSelectedWeekOfDay ].mStartTime + self.mUsedWeeklyList[self.mSelectedWeekOfDay ].mDuration, TimeFormatEnum.E_HH_MM )
			
			self.SetControlLabel2String( E_DialogInput03, strStartTime )
			self.SetControlLabel2String( E_DialogInput04, strEndTime )			
			
			return


	def ShowRecordName( self ) :
		try :
			kb = xbmc.Keyboard( self.mRecordName, 'Change Record Name', False )
			kb.doModal( )
			if kb.isConfirmed( ) :
				keyword = kb.getText( )
				LOG_TRACE('keyword len=%d' %len( keyword ) )
				if len( keyword ) < MININUM_KEYWORD_SIZE :
					xbmcgui.Dialog( ).ok('Infomation', 'Input more than %d characters' %MININUM_KEYWORD_SIZE )
					return

				self.mRecordName = keyword
				self.SetControlLabel2String( E_DialogInput01, self.mRecordName )
				
		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)	


	def SelectWeeklyDay( self ) :
		selectIndex = self.GetSelectedIndex( E_DialogSpinDay )
		LOG_TRACE('selectIndex = %d' %selectIndex )
		if selectIndex >= 0 and selectIndex < len(self.mUsedWeeklyList) :
			listItems = self.GetListItems( E_DialogSpinDay )

			if self.mUsedWeeklyList[selectIndex].mUsed == True :
				self.mUsedWeeklyList[selectIndex].mUsed = False
				listItems[selectIndex].setProperty( 'Used', 'False')
			else:
				self.mUsedWeeklyList[selectIndex].mUsed = True
				listItems[selectIndex].setProperty( 'Used', 'True')				
	

	def DoAddTimer( self ) :
		try :
			if self.mTimer :
				LOG_TRACE('Edit Mode')
				if self.mRecordingMode == E_ONCE :
					self.mDataCache.Timer_DeleteTimer( self.mTimer.mTimerId )
					ret = self.mDataCache.Timer_AddManualTimer( self.mTimer.mChannelNo, self.mTimer.mServiceType, startTime, duration, self.mTimer.mName, True )
					if ret and ( ret[0].mParam == -1 or ret[0].mError == -1 ):
						self.mConflictTimer = ret
						self.mErrorMessage = 'Conflict'
						return False
					else :
						self.mConflictTimer = None
						return True
				else:
					self.mDataCache.Timer_DeleteTimer( self.mTimer.mTimerId )
		

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
				if  startTime + self.mUsedWeeklyList[0].mDuration < self.mDataCache.Datetime_GetLocalTime() :
					self.mErrorMessage = 'Already Passed'
					return False
				ret = self.mDataCache.Timer_AddManualTimer( self.mChannel.mNumber, self.mChannel.mServiceType, startTime,	self.mUsedWeeklyList[0].mDuration, self.mRecordName, True )

				if ret[0].mParam == -1 or ret[0].mError == -1 :
					self.mConflictTimer = ret
					self.mErrorMessage = 'Conflict'
					return False
				else :
					self.mConflictTimer = None
					return True
			else :
				count = len( self.mUsedWeeklyList )
				weeklyTimerList = []

				localTime = self.mDataCache.Datetime_GetLocalTime()
				struct_time = time.gmtime( localTime  )


				for i in range( count ) :
					if self.mUsedWeeklyList[i].mUsed == True and self.mDataCache.Datetime_GetLocalTime() < self.mWeeklyEnd:
						timer = ElisIWeeklyTimer()
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
					self.mErrorMessage = 'Has no valid Timer'
					return False

				"""
				LOG_TRACE( 'Channel Number=%d' %self.mChannel.mNumber )
				LOG_TRACE( 'Service Type=%d' %self.mChannel.mServiceType )
				LOG_TRACE( 'Record Name=%s' %self.mRecordName )
				LOG_TRACE( 'weeklyTimerCount=%d'  %len( weeklyTimerList ) )
				LOG_TRACE( 'weeklyTimer=%s' %weeklyTimerList )
				"""

				ret = self.mDataCache.Timer_AddWeeklyTimer( self.mChannel.mNumber, self.mChannel.mServiceType, 0, 0, self.mRecordName, len( weeklyTimerList ), weeklyTimerList )
				LOG_TRACE( 'ret=%s' %ret )				

				if ret and ( ret[0].mParam == -1 or ret[0].mError == -1 ) :
					LOG_TRACE( '' )				
					self.mConflictTimer = ret
					self.mErrorMessage = 'Conflict'
					return False
				else :
					LOG_TRACE( '' )				
					self.mConflictTimer = None
					return True

				return True

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)	

		return False

			
	def ShowStartTime( self ) :

		try :
		
			focusId = self.GetFocusId( )

			strStartTime = self.GetControlLabel2String( E_DialogInput03 )
			dialog = xbmcgui.Dialog( )

			selectIndex = self.GetSelectedIndex( E_DialogSpinDay )

			if self.mRecordingMode == E_DAILY or self.mRecordingMode == E_WEEKLY :
				strStartTime = TimeToString( self.mUsedWeeklyList[selectIndex].mStartTime, TimeFormatEnum.E_HH_MM )
			else :
				strStartTime = TimeToString( self.mUsedWeeklyList[0].mStartTime, TimeFormatEnum.E_HH_MM )			

			strStartTime = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_TIME, 'Input Time', strStartTime )		

			tempList = strStartTime.split( ':', 1 )

			startHour = int( tempList[0] )
		
			startMin = int( tempList[1] )

			if self.mRecordingMode == E_WEEKLY  :
				LOG_TRACE( 'selectIndex=%d' %selectIndex )
				self.mUsedWeeklyList[selectIndex].mStartTime = startHour*3600 + startMin*60
				strStartTime = TimeToString( self.mUsedWeeklyList[selectIndex].mStartTime, TimeFormatEnum.E_HH_MM )
				strEndTime = TimeToString( self.mUsedWeeklyList[selectIndex].mStartTime + self.mUsedWeeklyList[selectIndex].mDuration, TimeFormatEnum.E_HH_MM )
			else :
				for i in range( len(self.mUsedWeeklyList) ) :
					self.mUsedWeeklyList[i].mStartTime = startHour*3600 + startMin*60

				strStartTime = TimeToString( self.mUsedWeeklyList[0].mStartTime, TimeFormatEnum.E_HH_MM )
				strEndTime = TimeToString( self.mUsedWeeklyList[0].mStartTime + self.mUsedWeeklyList[0].mDuration, TimeFormatEnum.E_HH_MM )

			self.SetControlLabel2String( E_DialogInput03, strStartTime )
			self.SetControlLabel2String( E_DialogInput04, strEndTime )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex)


	def ShowEndTime( self ) :	
		try :

			focusId = self.GetFocusId( )
			
			strEndTime = self.GetControlLabel2String( E_DialogInput04 )
			dialog = xbmcgui.Dialog( )

			selectIndex = self.GetSelectedIndex( E_DialogSpinDay )


			if self.mRecordingMode == E_DAILY or self.mRecordingMode == E_WEEKLY :
				strEndTime = TimeToString( self.mUsedWeeklyList[selectIndex].mStartTime + self.mUsedWeeklyList[selectIndex].mDuration, TimeFormatEnum.E_HH_MM )
			else :
				strEndTime = TimeToString( self.mUsedWeeklyList[0].mStartTime + self.mUsedWeeklyList[0].mDuration, TimeFormatEnum.E_HH_MM )			

			strEndTime = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_TIME, 'Input Time', strEndTime )		

			tempList = strEndTime.split( ':', 1 )

			endHour = int( tempList[0] )
			
			endMin = int( tempList[1] )

			if self.mRecordingMode == E_WEEKLY :
				endTime = endHour*3600 + endMin*60
				duration = endTime - self.mUsedWeeklyList[selectIndex].mStartTime

				if duration <= 0 :
					duration = duration + 24*3600

				if duration <= 0 :
					prop = ElisPropertyEnum( 'Default Rec Duration', self.mCommander )
					duration = prop.GetProp( )

				self.mUsedWeeklyList[selectIndex].mDuration = duration

			else :
				endTime = endHour*3600 + endMin*60
				duration = endTime - self.mUsedWeeklyList[0].mStartTime

				if duration <= 0 :
					duration = duration + 24*3600

				if duration <= 0 :
					prop = ElisPropertyEnum( 'Default Rec Duration', self.mCommander )
					duration = prop.GetProp( )

				for i in range( len(self.mUsedWeeklyList) ) :
					self.mUsedWeeklyList[i].mDuration = duration

			self.SetControlLabel2String( E_DialogInput04, strEndTime )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex)


