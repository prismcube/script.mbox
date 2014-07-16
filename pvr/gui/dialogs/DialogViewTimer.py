from pvr.gui.WindowImport import *


# Control IDs
E_LABEL_RECORD_NAME			= 101
E_LABEL_EPG_START_TIME		= 102
E_LABEL_EPG_END_TIME		= 103
E_BUTTON_ADD				= 200
E_BUTTON_CANCEL				= 201

E_ONCE						= 0
E_WEEKLY					= 1
E_DAILY						= 2


#LIST_RECORDING_MODE	= [ MR_LANG( 'Once' ), MR_LANG( 'Weekly' ), '%s(7 %s)' %(MR_LANG( 'Weekly' ), MR_LANG( 'Days' ))  ]
LIST_WEEKLY = [ MR_LANG( 'Sun' ), MR_LANG( 'Mon'), MR_LANG( 'Tue' ), MR_LANG( 'Wed' ), MR_LANG( 'Thu' ), MR_LANG( 'Fri' ), MR_LANG( 'Sat' ) ]


class DialogViewTimer( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		self.mChannel = None
		self.mTimer = None
		self.mEPG = None
		self.mRecordName = MR_LANG( 'None' )
		self.mErrorMessage = MR_LANG( 'Unknown Error' )
		self.mWeeklyStart = 0
		self.mConflictTimer = None
		self.mIsRunningTimer = False
		self.mIsOk = E_DIALOG_STATE_CANCEL


	def onInit( self ) :
		#global LIST_RECORDING_MODE
		global LIST_WEEKLY
		#LIST_RECORDING_MODE	= [ MR_LANG( 'Once' ), MR_LANG( 'Daily' ), MR_LANG( 'Weekly' ) ]
		LIST_RECORDING_MODE	= [ MR_LANG( 'Once' ), MR_LANG( 'Weekly' ), '%s(7 %s)' %(MR_LANG( 'Weekly' ), MR_LANG( 'Days' ))  ]
		LIST_WEEKLY = [ MR_LANG( 'Sun' ), MR_LANG( 'Mon'), MR_LANG( 'Tue' ), MR_LANG( 'Wed' ), MR_LANG( 'Thu' ), MR_LANG( 'Fri' ), MR_LANG( 'Sat' ) ]

		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.setProperty( 'DialogDrawFinished', 'False' )

		mTitle = MR_LANG( 'Add View Timer' )
		if self.mTimer :
			mTitle = MR_LANG( 'Edit View Timer' )
			self.mRecordName = self.mTimer.mName
		elif self.mChannel :
			self.mRecordName = self.mChannel.mName

		self.SetHeaderLabel( mTitle )

		self.DrawItem( )
		self.Reload( )

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
				self.ShowRecordName( )

			elif groupId == E_DialogSpinEx01 :
				selectIndex = self.GetSelectedIndex( E_DialogSpinEx01 )
				if focusId == E_DialogSpinEx01 + 1 :
					self.ChangeStartDay( True )
				else :
					self.ChangeStartDay( False )

			elif groupId == E_DialogInput02 :
				self.ShowStartTime( )

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


	def SetChannel( self, aChannel ) :
		self.mChannel = aChannel


	def SetTimer( self, aTimer = None ) :
		self.mTimer = aTimer


	def SetEPG( self, aEPG = None ) :
		self.mEPG = aEPG


	def IsOK( self ) :
		return self.mIsOk


	def GetConflictTimer( self ) :
		return self.mConflictTimer


	def DrawItem( self ) :
		LOG_TRACE( 'self.mTimer[%s]'% self.mTimer )
		#global LIST_RECORDING_MODE
		#global LIST_WEEKLY

		try :
			self.ResetAllControl( )
			self.AddInputControl( E_DialogInput01, MR_LANG( 'Name' ),  MR_LANG( 'Record Name' ) )
			self.AddUserEnumControl( E_DialogSpinEx01, MR_LANG( 'Start Date' ), [ MR_LANG( 'Date' ) ], 0 )			
			self.AddInputControl( E_DialogInput02, MR_LANG( 'Start Time' ),  '00:00' )
			self.AddOkCanelButton( )

			self.SetAutoHeight( True )
			self.InitControl( )

			#self.ChangeRecordMode( )
			self.UpdateLocation( )

		except Exception, ex :
			LOG_ERR( 'Exception %s'% ex )


	def ChangeStartDay( self, aIsNext ) :
		days = int( self.mDataCache.Datetime_GetLocalTime( ) / ONE_DAY_SECONDS )
		currentWeeekyStart = days * ONE_DAY_SECONDS

		if aIsNext == True :
			newWeekyStart = self.mWeeklyStart + ONE_DAY_SECONDS
		else :
			newWeekyStart = self.mWeeklyStart - ONE_DAY_SECONDS		

		if newWeekyStart < currentWeeekyStart :
			self.mWeeklyStart = currentWeeekyStart
		else :
			self.mWeeklyStart = newWeekyStart

		LOG_TRACE( 'New StartTime =%s'% TimeToString( self.mWeeklyStart, TimeFormatEnum.E_AW_DD_MM_YYYY ) )
		self.SetListControlItemLabel( E_DialogSpinEx01, TimeToString( self.mWeeklyStart, TimeFormatEnum.E_AW_DD_MM_YYYY ) )


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
			LOG_ERR( 'Exception %s'% ex )	


	def DoAddTimer( self ) :
		retTimer = False
		try :
			LOG_TRACE( 'Edit Mode' )

			strStartTime = self.GetControlLabel2String( E_DialogInput02 )

			tempList = strStartTime.split( ':', 1 )
			startHour = int( tempList[0] )
			startMin = int( tempList[1] )
			startTime = startHour * 3600 + startMin * 60 + self.mWeeklyStart

			LOG_TRACE( 'startTime=%s' %TimeToString( startTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
			LOG_TRACE( 'strStartTime[%s] startTime[%s]'% ( strStartTime, startTime ) )

			ret = None
			if self.mTimer :
				ret = self.mDataCache.Timer_EditViewTimer( self.mTimer.mTimerId, startTime )
			else :
				ret = self.mDataCache.Timer_AddViewTimer( self.mChannel.mNumber, self.mChannel.mServiceType, startTime, self.mRecordName )

			retTimer = True
			if not ret :
				self.mConflictTimer = None
			else :
				if ret[0].mParam == -1 or ret[0].mError == -1 :
					self.mConflictTimer = ret
					self.mErrorMessage = MR_LANG( 'Error' )
					retTimer = False

		except Exception, ex :
			LOG_ERR( 'Exception %s' %ex )
			retTimer = False

		return retTimer

			
	def ShowStartTime( self ) :
		try :
			focusId = self.GetFocusId( )
			strStartTime = self.GetControlLabel2String( E_DialogInput02 )

			#if self.mTimer :
			#	strStartTime = TimeToString( self.mTimer.mStartTime, TimeFormatEnum.E_HH_MM )

			#localTime = self.mDataCache.Datetime_GetLocalTime( )
			#strStartTime = TimeToString( localTime, TimeFormatEnum.E_HH_MM )

			strStartTime = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_TIME, MR_LANG( 'Enter Start Time' ), strStartTime )

			tempList = strStartTime.split( ':', 1 )
			startHour = int( tempList[0] )
			startMin = int( tempList[1] )

			"""
			if self.mTimer :
				startTime = startHour * 3600 + startMin * 60
				days = int( self.mTimer.mStartTime / ONE_DAY_SECONDS )
				self.mTimer.mStartTime	= days * ONE_DAY_SECONDS + startTime

				strStartTime = TimeToString( self.mTimer.mStartTime, TimeFormatEnum.E_HH_MM )
			"""

			self.SetControlLabel2String( E_DialogInput02, strStartTime )

		except Exception, ex :
			LOG_ERR( 'Exception %s'% ex )


	def Reload( self ) :
		self.SetControlLabel2String( E_DialogInput01, self.mRecordName )

		localTime = self.mDataCache.Datetime_GetLocalTime( )
		if self.mEPG and self.mEPG.mStartTime + self.mDataCache.Datetime_GetLocalOffset( ) > localTime :
			localTime = self.mEPG.mStartTime + self.mDataCache.Datetime_GetLocalOffset( )

		if self.mTimer :
			localTime = self.mTimer.mStartTime
		strStartTime = TimeToString( localTime, TimeFormatEnum.E_HH_MM )
		self.SetControlLabel2String( E_DialogInput02, strStartTime )

		days = int( localTime / ONE_DAY_SECONDS )
		self.mWeeklyStart = days * ONE_DAY_SECONDS
		LOG_TRACE( 'New StartTime =%s'% TimeToString( self.mWeeklyStart, TimeFormatEnum.E_AW_DD_MM_YYYY ) )
		self.SetListControlItemLabel( E_DialogSpinEx01, TimeToString( self.mWeeklyStart, TimeFormatEnum.E_AW_DD_MM_YYYY ) )



