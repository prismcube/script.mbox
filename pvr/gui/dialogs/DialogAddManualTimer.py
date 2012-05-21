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
LIST_WEEKLY = ['Sun','Mon','Tue', 'Wed', 'The', 'Fri', 'Sat' ]

MININUM_KEYWORD_SIZE  		= 3

class UsedWeeklyTimer( ElisIWeeklyTimer ):
	def __init__( self ):
		self.mUsed=False


class DialogAddManualTimer( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		self.mEPG = None
		self.mIsEdit = False
		self.mRecordingMode = E_ONCE
		self.mChanne = None
		self.mTimer = -1
		self.mUsedWeeklyList = None
		self.mSelectedWeekOfDay = 0
		self.mRecordName = 'None'
		self.mErrorMessage = 'Unknown Error'		
		self.mWeeklyStart = 0
		self.mWekklyEnd = 0
		


	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		if self.mIsEdit == True :
			self.SetHeaderLabel( 'Edit Recording' )		
		else :
			self.SetHeaderLabel( 'Add Manual Recording' )

		if self.mEPG  :
			self.mRecordName = self.mEPG.mEventName
		else :
			self.mRecordName = self.mChannel.mName

		self.Reload( )
		#self.mEventBus.Register( self )

		self.mIsOk = E_DIALOG_STATE_CANCEL


		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_OK_ID, 'Confirm' )
		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_CANCEL_ID, 'Cancel' )
		self.DrawItem( )

		

	def onAction( self, aAction ):
		actionId = aAction.getId( )
		focusId = self.GetFocusId( )
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.ResetAllControl( )
			self.Close()		

		elif actionId == Action.ACTION_SELECT_ITEM :
			groupId = self.GetGroupId( focusId )

			if groupId == E_DialogInput01 :
				self.ShowRecordName()
				self.DrawItem()
			
			elif groupId == E_DialogSpinEx01 :
				self.mRecordingMode = self.GetSelectedIndex( E_DialogSpinEx01 )
				self.Reload()
				self.DrawItem()

			elif groupId == E_DialogSpinDay :
				self.SelectWeeklyDay()
				self.DrawItem()

			elif groupId == E_DialogInput03 :
				self.ShowStartTime( )
				self.DrawItem()

			elif groupId == E_DialogInput04 :
				self.ShowEndTime( )
				self.DrawItem()

				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.ResetAllControl( )
			self.Close()		

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
	
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			if self.GetGroupId( focusId ) == E_DialogSpinDay :
				self.ChangeWeeklyDay( )
				self.DrawItem()
			else :
				self.ControlLeft( )
				
		elif actionId == Action.ACTION_MOVE_RIGHT :
			if self.GetGroupId( focusId ) == E_DialogSpinDay :
				self.ChangeWeeklyDay( )
				self.DrawItem()
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


	def SetEditMode( self, aIsEdit ):
		self.mIsEdit = aIsEdit


	def SetEPG( self, aEPG ):
		self.mEPG = aEPG


	def SetChannel( self, aChannel ) :
		self.mChannel = aChannel


	def SetTimer( self, aTimer ):
		self.mTimer = aTimer


	def IsOK( self ) :
		return self.mIsOk


	def Close( self ):
		#self.mEventBus.Deregister( self )
		self.CloseDialog( )


	def Reload ( self ) :
		LOG_TRACE('')
		try :
			self.mSelectedWeekOfDay	= 0 
			self.mUsedWeeklyList = []

			if self.mIsEdit  == True :
				LOG_TRACE('')
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
				if struct_time[6] == 6 : #tm_wday
					weekday = 0
				elif struct_time[6] == 0 :
					weekday = 6
				else  :
					weekday = struct_time[6] + 1

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

			if self.mIsEdit  == True :
				self.AddUserEnumControl( E_DialogSpinEx01, 'Recording', LIST_RECORDING_MODE, self.mRecordingMode )
				#SetEnableControl

			else :
				self.AddUserEnumControl( E_DialogSpinEx01, 'Recording', LIST_RECORDING_MODE, self.mRecordingMode )
				self.SetEnableControl(E_DialogSpinEx01,  True )
				self.AddInputControl( E_DialogInput01, 'Name :',  self.mRecordName )
				self.SetEnableControl(E_DialogInput01,  True )

				if self.mRecordingMode == E_ONCE :
					startTime = self.mWeeklyStart + self.mUsedWeeklyList[0].mStartTime
					endTime = startTime + self.mUsedWeeklyList[0].mDuration
						
					self.SetVisibleControl( E_DialogSpinDay, False )
					self.SetVisibleControl( E_DialogInput02, True )
					self.AddInputControl( E_DialogInput02, 'Date :', TimeToString( startTime, TimeFormatEnum.E_AW_DD_MM_YYYY ) )
					self.SetEnableControl( E_DialogInput02, False )
					
					self.AddInputControl( E_DialogInput03, 'Start Time :',  TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
					self.AddInputControl( E_DialogInput04, 'End Time :',  TimeToString( endTime, TimeFormatEnum.E_HH_MM) )
					
				else :

					LOG_TRACE('self.mSelectedWeekOfDay =%d' %self.mSelectedWeekOfDay )
					self.AddListControl( E_DialogSpinDay, LIST_WEEKLY, self.mSelectedWeekOfDay )
					listItems = self.GetListItems( E_DialogSpinDay )

					for i in range( len(listItems) ) :
						if self.mUsedWeeklyList[i].mUsed == True :
							listItems[i].setProperty( 'Used', 'True')
						else :
							listItems[i].setProperty( 'Used', 'False')
					
					
					self.SetListControlTitle( E_DialogSpinDay, 'Daily' )
					self.SetVisibleControl( E_DialogSpinDay, True )

					self.SetVisibleControl( E_DialogInput02, False )					

					if self.mRecordingMode == E_WEEKLY :
						self.SetEnableControl( E_DialogSpinDay, True )
					else :
						self.SetEnableControl( E_DialogSpinDay, False )
						
					startTime = self.mUsedWeeklyList[self.mSelectedWeekOfDay ].mStartTime
					endTime = startTime + self.mUsedWeeklyList[self.mSelectedWeekOfDay ].mDuration

					self.AddInputControl( E_DialogInput03, 'Start Time :',  TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
					self.AddInputControl( E_DialogInput04, 'End Time :',  TimeToString( endTime, TimeFormatEnum.E_HH_MM) )

					if self.mRecordingMode == E_WEEKLY and self.mUsedWeeklyList[self.mSelectedWeekOfDay].mUsed == False:
						self.SetEnableControl( E_DialogInput03, False )
						self.SetEnableControl( E_DialogInput04, False )
					else :
						self.SetEnableControl( E_DialogInput03, True )
						self.SetEnableControl( E_DialogInput04, True )
					
				self.AddOkCanelButton( )
				self.SetAutoHeight( True )

			self.InitControl( )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex)
		

	def ChangeWeeklyDay( self ) :
		selectIndex = self.GetSelectedIndex( E_DialogSpinDay )
		LOG_TRACE('selectIndex = %d' %selectIndex )
		if selectIndex >= 0 and selectIndex < len(self.mUsedWeeklyList) :
			self.mSelectedWeekOfDay	= selectIndex
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

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)	
		E_DialogInput01	

	

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

			tmpItems = self.GetListItems( E_DialogSpinDay )
	

	def DoAddTimer( self ) :
		try :
			if self.mIsEdit  == True :
				LOG_TRACE('Edit Mode')
		
			else :
				for i in range( len(self.mUsedWeeklyList) ) :
					#debug
					LOG_TRACE('index=%d' %i )
					LOG_TRACE('used=%d' %self.mUsedWeeklyList[i].mUsed )
					LOG_TRACE('date=%d' %self.mUsedWeeklyList[i].mDate )
					LOG_TRACE('startTime=%s' %TimeToString(self.mWeeklyStart, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
					LOG_TRACE('weeklyTime=%s' %TimeToString(self.mUsedWeeklyList[i].mStartTime, TimeFormatEnum.E_HH_MM ) )

				if self.mRecordingMode == E_ONCE :
					startTime = self.mWeeklyStart + self.mUsedWeeklyList[0].mStartTime
					if  startTime + self.mUsedWeeklyList[0].mDuration < self.mDataCache.Datetime_GetLocalTime() :
						self.mErrorMessage = 'Already Passed'
						return False
					self.mCommander.Timer_AddManualTimer( self.mChannel.mNumber, self.mChannel.mServiceType, startTime,	self.mUsedWeeklyList[0].mDuration, self.mRecordName, 0 )
					return True
				else :
					count = len( self.mUsedWeeklyList )
					weeklyTimerList = []
					for i in range( count ) :
						if self.mUsedWeeklyList[i].mUsed == True and self.mDataCache.Datetime_GetLocalTime() < self.mWeeklyEnd:
							timer = ElisIWeeklyTimer()
							timer.mDate = i
							timer.mStartTime = self.mUsedWeeklyList[i].mStartTime
							timer.mDuration = self.mUsedWeeklyList[i].mDuration
							weeklyTimerList.append( timer )

					if len( weeklyTimerList ) <= 0 :
						self.mErrorMessage = 'Has no valid Timer'
						return False

					self.mCommander.Timer_AddWeeklyTimer( self.mChannel.mNumber, self.mChannel.mServiceType, 0, 0, self.mRecordName, len( weeklyTimerList ), weeklyTimerList )

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
				self.mUsedWeeklyList[selectIndex].mStartTime = startHour*3600 + startMin*60
			else :
				for i in range( len(self.mUsedWeeklyList) ) :
					self.mUsedWeeklyList[i].mStartTime = startHour*3600 + startMin*60

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

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex)

	
