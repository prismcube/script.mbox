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
E_IMAGE_DIALOG_BACKGROUND   = 9001
E_GROUP_ID_SHOW_INFO        = 300
E_PROGRESS_NETVOLUME        = 301
E_LABEL_ID_USE_INFO         = 302

E_FROM_NOW					= 0 
E_FROM_EPG					= 1

E_NO_EPG_MAX_TIMESHIFT_COPY	=  60

LIST_COPY_MODE =[ MR_LANG( 'No'), MR_LANG( 'Yes' ) ]


class DialogStartRecord( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		self.mTimer						= None
		self.mOTRInfo					= None
		self.mRecordingProgressThread	= None
		self.mCurrentChannel			= None
		self.mEnableProgress			= False
		self.mStartTime					= 0
		self.mEndTime					= 0
		self.mCopyMode					= E_FROM_NOW
		self.mConflictTimer				= None
		self.mCopyTimeshiftMin			= 0


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mCopyTimeshiftMin = 0		

		self.setProperty( 'DialogDrawFinished', 'False' )
		self.SetHeaderLabel( MR_LANG( 'Start Recording' ) )

		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		self.mFreeHDD  = 0
		self.mTotalHDD = 0
		self.mHDDStatus = False
		self.mSelectIdx = 99
		self.mNetVolume = None
		self.mNetVolumeList = []
		self.mDialogWidth = self.getControl( E_IMAGE_DIALOG_BACKGROUND ).getWidth( )
		self.mNetVolumeList = self.mDataCache.Record_GetNetworkVolume( True )
		if E_SUPPORT_EXTEND_RECORD_PATH and CheckHdd( ) :
			self.mHDDStatus = True
			self.mTotalHDD = self.mCommander.Record_GetPartitionSize( )
			self.mFreeHDD  = self.mCommander.Record_GetFreeMBSize( )

		self.Reload( )
		self.DrawItem( )

		#self.mEventBus.Register( self )
		
		self.mEnableThread = True
		#self.mRecordingProgressThread = self.RecordingProgressThread( )
		self.mDurationChanged = False
		self.mConflictTimer = None		

		self.mIsOk = E_DIALOG_STATE_CANCEL

		self.setProperty( 'DialogDrawFinished', 'True' )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.GetFocusId( )

		self.GlobalSettingAction( self, actionId )
		
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
				
			elif groupId == E_DialogInput04 :
				self.ChangeCopyDuraton( )

			elif groupId == E_DialogInput05 :
				self.ShowNetworkVolume( )

			elif groupId == E_SETTING_DIALOG_BUTTON_OK_ID :	
				self.StartRecord( )

			elif groupId == E_SETTING_DIALOG_BUTTON_CANCEL_ID :
				self.mIsOk = E_DIALOG_STATE_CANCEL
				self.ResetAllControl( )
				self.Close( )

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( self )
	
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( self )

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


	def GetVolumeInfo( self, aNetVolume = None ) :
		lblSelect = MR_LANG( 'None' )
		lblOnline = E_TAG_FALSE
		useFree = self.mFreeHDD
		useTotal= self.mTotalHDD
		useInfo = 0
		if self.mHDDStatus :
			lblSelect = MR_LANG( 'HDD' )
			lblOnline = E_TAG_TRUE

		if aNetVolume :
			lblOnline = E_TAG_FALSE
			lblSelect = os.path.basename( aNetVolume.mMountPath )
			if aNetVolume.mOnline :
				lblOnline = E_TAG_TRUE
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

		isShowVolumeInfo = E_TAG_TRUE
		if not self.mHDDStatus and ( not aNetVolume ) :
			isShowVolumeInfo = E_TAG_FALSE
		self.setProperty( 'NetVolumeInfo', isShowVolumeInfo )

		return lblSelect, useInfo, lblPercent, lblOnline


	def GetVolumeContext( self, aVolumeID = -1 ) :
		trackList = []
		if self.mHDDStatus :
			trackList = [ContextItem( MR_LANG( 'Internal HDD' ), 99 )]

		trackIndex = 0
		if self.mNetVolumeList and len( self.mNetVolumeList ) > 0 :
			for netVolume in self.mNetVolumeList :
				getPath = netVolume.mRemoteFullPath
				urlType = urlparse.urlparse( getPath ).scheme
				#urlHost, urlPort, urlUser, urlPass, urlPath, urlFile, urlSize = GetParseUrl( getPath )
				lblStatus = ''
				lblType = 'local'
				if urlType :
					lblType = '%s'% urlType.upper()
				else :
					if netVolume.mMountPath and bool( re.search( '%s\w\d+'% E_DEFAULT_PATH_USB_POSITION, netVolume.mMountPath, re.IGNORECASE ) ) :
						lblType = 'USB'

				if not netVolume.mOnline :
					lblStatus = '-%s'% MR_LANG( 'Disconnected' )
				if netVolume.mReadOnly :
					lblStatus = '-%s'% MR_LANG( 'Read only' )

				lblPath = '[%s]%s%s'% ( lblType, os.path.basename( netVolume.mMountPath ), lblStatus )
				if lblStatus :
					lblPath = '[COLOR grey3]%s[/COLOR]'% lblPath
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
			LOG_TRACE( '[ManaulTimer] Nothing in the mount list' )
			return

		selectedIdx = 0
		if self.mHDDStatus and self.mSelectIdx != 99 :
			selectedIdx = self.mSelectIdx + 1
		else :
			selectedIdx = self.mSelectIdx

		if selectedIdx < 0 :
			selectedIdx = 0

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( trackList, selectedIdx )
		dialog.doModal( )

		selectAction = dialog.GetSelectedAction( )
		if selectAction < 0 :
			return

		if selectAction == 99 :
			self.mNetVolume = None
		elif selectAction < len( self.mNetVolumeList ) :
			netVolume = self.mNetVolumeList[selectAction]
			if not netVolume.mOnline or netVolume.mReadOnly :
				lblLine = MR_LANG( 'Read only folder' )
				if not netVolume.mOnline :
					lblLine = MR_LANG( 'Inaccessible folder' )

				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), lblLine )
				dialog.doModal( )
				return

			self.mNetVolume = deepcopy( netVolume )

		self.mSelectIdx = selectAction
		lblSelect, useInfo, lblPercent, lblOnline = self.GetVolumeInfo( self.mNetVolume )
		self.SetControlLabel2String( E_DialogInput05, lblSelect )
		self.setProperty( 'NetVolumeConnect', lblOnline )
		self.setProperty( 'NetVolumeUse', lblPercent )
		self.getControl( E_PROGRESS_NETVOLUME ).setPercent( useInfo )
		ResetPositionVolumeInfo( self, lblPercent, self.mDialogWidth, E_GROUP_ID_SHOW_INFO, E_LABEL_ID_USE_INFO )


	def Reload ( self ) :
		netVolumeID = -99
		self.mLocalTime = self.mDataCache.Datetime_GetLocalTime( )
		self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
		self.mTimer = self.mDataCache.GetRunnigTimerByChannel( )
		if self.mTimer :
			self.SetHeaderLabel( MR_LANG( 'Edit Recording' ) )
			netVolumeID = self.mTimer.mVolumeID
		else :
			self.mOTRInfo = self.mDataCache.Timer_GetOTRInfo( )
			#self.mOTRInfo.printdebug( )
			self.CheckValidEPG( )
			#self.mOTRInfo.printdebug( )
			self.mStartTime = self.mLocalTime
			self.mEndTime = self.mOTRInfo.mEventEndTime

		self.GetVolumeContext( netVolumeID )


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
		posx, posy = 300, 310
		try :
			if self.mTimer :
				posy = 270
				self.AddLabelControl( E_LABEL_RECORD_NAME )
				self.SetControlLabelString( E_LABEL_RECORD_NAME, self.mTimer.mName )

				self.SetVisibleControl( E_DialogSpinEx01, False )

				self.AddInputControl( E_DialogInput01, MR_LANG( 'Start Time' ),  TimeToString( self.mTimer.mStartTime, TimeFormatEnum.E_HH_MM ) )
				self.SetEnableControl( E_DialogInput01, False )									
				self.AddInputControl( E_DialogInput02, MR_LANG( 'End Time' ),  TimeToString( self.mTimer.mStartTime + self.mTimer.mDuration , TimeFormatEnum.E_HH_MM ) )
				self.AddInputControl( E_DialogInput03, MR_LANG( 'Duration' ),  '%d %s' % ( int( self.mTimer.mDuration / 60 ), MR_LANG( 'min(s)' ) ), aInputNumberType = TYPE_NUMBER_NORMAL, aMax = 999 )

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
					self.SetVisibleControl( E_DialogSpinEx01, False )
					if self.mOTRInfo.mTimeshiftAvailable :
						self.mCopyTimeshiftMin = int( self.mOTRInfo.mTimeshiftRecordMs/(1000*60) )
						if self.mCopyTimeshiftMin > E_NO_EPG_MAX_TIMESHIFT_COPY :
							self.mCopyTimeshiftMin = E_NO_EPG_MAX_TIMESHIFT_COPY
						self.AddInputControl( E_DialogInput04, MR_LANG( 'Timeshift Copy Duration' ),  '%d %s' % ( self.mCopyTimeshiftMin, MR_LANG( 'min(s)' ) ), aInputNumberType = TYPE_NUMBER_NORMAL, aMax = self.mCopyTimeshiftMin )
					else :
						self.AddInputControl( E_DialogInput04, MR_LANG( 'Timeshift Copy Duration' ),  '0 %s' % ( MR_LANG( 'min(s)' ) ), aInputNumberType = TYPE_NUMBER_NORMAL, aMax = 0 )
						self.SetEnableControl( E_DialogInput04, False )						

				duration = int( self.mEndTime/60 ) - int( self.mStartTime/60 )
				
				LOG_TRACE( 'Name=%s' %self.mOTRInfo.mEventName )
				LOG_TRACE( 'Start Time=%s' %TimeToString( self.mOTRInfo.mEventStartTime, TimeFormatEnum.E_HH_MM ) )
				LOG_TRACE( 'End Time=%s' %TimeToString( self.mOTRInfo.mEventEndTime, TimeFormatEnum.E_HH_MM ) )
				LOG_TRACE( 'Duration=%d' %int( self.mOTRInfo.mExpectedRecordDuration/60 ) )

				self.AddInputControl( E_DialogInput01, MR_LANG( 'Start Time' ),  TimeToString( self.mStartTime, TimeFormatEnum.E_HH_MM ) )
				self.SetEnableControl( E_DialogInput01, False )									
				self.AddInputControl( E_DialogInput02, MR_LANG( 'End Time' ),  TimeToString( self.mEndTime, TimeFormatEnum.E_HH_MM ) )
				self.AddInputControl( E_DialogInput03, MR_LANG( 'Duration' ),  '%d %s' % ( duration, MR_LANG( 'min(s)' ) ), aInputNumberType = TYPE_NUMBER_NORMAL, aMax = 999 )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		if E_SUPPORT_EXTEND_RECORD_PATH :
			lblSelect, useInfo, lblPercent, lblOnline = self.GetVolumeInfo( self.mNetVolume )
			self.AddInputControl( E_DialogInput05, MR_LANG( 'Record Path' ), lblSelect )
			self.AddInputControl( E_DialogInput06, '', '' )
			self.SetEnableControls( [E_DialogInput05, E_DialogInput06], False )
			self.setProperty( 'NetVolumeConnect', lblOnline )
			self.setProperty( 'NetVolumeUse', lblPercent )
			self.getControl( E_PROGRESS_NETVOLUME ).setPercent( useInfo )
			#self.getControl( 300 ).setPosition( posx, posy )
			ResetPositionVolumeInfo( self, lblPercent, self.mDialogWidth, E_GROUP_ID_SHOW_INFO, E_LABEL_ID_USE_INFO )

			#self.setProperty( 'NetVolumeInfo', E_TAG_TRUE )

		self.AddOkCanelButton( )

		if self.mTimer :
			self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_OK_ID, MR_LANG( 'Change Duration' ) )
			#block control by Edit timer
			self.SetEnableControl( E_DialogInput05, False )
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
				self.SetControlLabel2String( E_DialogInput03, '%d %s' %( duration, MR_LANG('min(s)') ) )


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
			
			strEndTime = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_TIME, MR_LANG( 'Enter End Time' ), strEndTime )

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
			self.SetControlLabel2String( E_DialogInput03, '%d %s' %( duration, MR_LANG( 'min(s)' ) ) )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def ChangeDuraton( self ) :
		try :
			if self.mTimer :
				tempDuration = int( self.mTimer.mDuration/60 )
			else :
				tempDuration = int( self.mEndTime/60 ) - int( self.mStartTime/60 )

				
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( '%s(%s)' %( MR_LANG( 'Enter New Duration' ), MR_LANG( 'in mins' ) ), '%d' %tempDuration  , 3 )
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

				self.SetControlLabel2String( E_DialogInput03, '%d %s' % ( duration, MR_LANG( 'min(s)' ) ) )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def ChangeCopyDuraton( self ) :
		try :	
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( '%s(%s)' %( MR_LANG( 'Enter New Duration' ), MR_LANG( 'in mins' ) ), '%d' %self.mCopyTimeshiftMin  , 3 )
 			dialog.doModal( )

 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				duration = int( dialog.GetString( ) )
				LOG_TRACE( 'Duration = %d' % duration )

				copyTimeshiftSec = int( self.mOTRInfo.mTimeshiftRecordMs/(1000*60) )
				if copyTimeshiftSec > E_NO_EPG_MAX_TIMESHIFT_COPY :
					copyTimeshiftSec = E_NO_EPG_MAX_TIMESHIFT_COPY

				if duration >= 0  and duration <=  copyTimeshiftSec :
					self.mCopyTimeshiftMin = duration
				elif duration >  copyTimeshiftSec :
					self.mCopyTimeshiftMin = copyTimeshiftSec
				else :
					self.mCopyTimeshiftMin = 0					
				self.SetControlLabel2String( E_DialogInput04, '%d %s' % ( self.mCopyTimeshiftMin, MR_LANG( 'min(s)' ) ) )

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
					else :
						copyTimeshift = self.mCopyTimeshiftMin *60

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


	def CallballInputNumber( self, aGroupId, aString ) :
		if aGroupId == E_DialogInput03 :
			self.SetControlLabel2String( E_DialogInput03, '%s %s' % ( aString, MR_LANG( 'min(s)' ) ) )
		elif aGroupId == E_DialogInput04 :
			self.SetControlLabel2String( E_DialogInput04, '%s %s' % ( aString, MR_LANG( 'min(s)' ) ) )


	def FocusChangedAction( self, aGroupId ) :
		if aGroupId == E_DialogInput03 :
			duration = int( self.GetControlLabel2String( E_DialogInput03 ).split( )[0] )

			if self.mTimer :
				tempDuration = int( self.mTimer.mDuration / 60 )
			else :
				tempDuration = int( self.mEndTime / 60 ) - int( self.mStartTime / 60 )
			
			if duration > 0 :
				if tempDuration != duration :
					self.mDurationChanged = True

				if self.mTimer :
					self.mTimer.mDuration = duration * 60 
				else :
					self.mEndTime = self.mStartTime + duration * 60

			if self.mTimer :
				self.SetControlLabel2String( E_DialogInput02, TimeToString( self.mTimer.mStartTime + self.mTimer.mDuration, TimeFormatEnum.E_HH_MM ) )
			else :
				self.SetControlLabel2String( E_DialogInput02, TimeToString( self.mEndTime, TimeFormatEnum.E_HH_MM ) )
				
		elif aGroupId == E_DialogInput04 :
			self.mCopyTimeshiftMin = int( self.GetControlLabel2String( E_DialogInput04 ).split( )[0] )
			if self.mCopyTimeshiftMin > E_NO_EPG_MAX_TIMESHIFT_COPY :
				self.mCopyTimeshiftMin = E_NO_EPG_MAX_TIMESHIFT_COPY
			LOG_TRACE( 'change timeshift copy duration =%d' %self.mCopyTimeshiftMin )

