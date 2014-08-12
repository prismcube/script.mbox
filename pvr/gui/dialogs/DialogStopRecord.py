from pvr.gui.WindowImport import *


# Control IDs
IMAGE_ID_BACKGROUND 		= 100
LIST_ID_RECORD				= 9000

GROUP_ID_RECORD_1			= 500
GROUP_ID_RECORD_2			= 510
GROUP_ID_CANCEL				= 520

BUTTON_ID_RECORD_1			= 501
BUTTON_ID_RECORD_2			= 511
BUTTON_ID_CANCEL			= 521

LABEL_ID_CHANNELNAME_1		= 502
LABEL_ID_CHANNELNAME_2		= 512

LABEL_ID_RECORDNAME_1		= 503
LABEL_ID_RECORDNAME_2		= 513

LABEL_ID_DURATION_1			= 504
LABEL_ID_DURATION_2			= 514

PROGRESS_ID_DURATION_1		= 505
PROGRESS_ID_DURATION_2		= 515


class DialogStopRecord( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mBackgroundHeight = -1
		self.mEnableThread = False
		self.mRecordingProgressThread = None
		self.mLock = thread.allocate_lock( )


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.setProperty( 'DialogDrawFinished', 'False' )

		self.mCtrlRecordGroup = {}
		self.mCtrlChannelName = {}
		self.mCtrlRecordName = {}
		self.mCtrlDuration = {}
		self.mCtrlProgress = {}		
		self.mIsOk = E_DIALOG_STATE_CANCEL

		try :		
			self.mCtrlRecordGroup[0] = self.getControl( GROUP_ID_RECORD_1 )
			self.mCtrlRecordGroup[1] = self.getControl( GROUP_ID_RECORD_2 )
			self.mCtrlRecordGroup[2] = self.getControl( GROUP_ID_CANCEL )			

			self.mCtrlChannelName[0] = self.getControl( LABEL_ID_CHANNELNAME_1 )
			self.mCtrlChannelName[1] = self.getControl( LABEL_ID_CHANNELNAME_2 )

			self.mCtrlRecordName[0] = self.getControl( LABEL_ID_RECORDNAME_1 )
			self.mCtrlRecordName[1] = self.getControl( LABEL_ID_RECORDNAME_2 )

			self.mCtrlDuration[0] = self.getControl( LABEL_ID_DURATION_1 )
			self.mCtrlDuration[1] = self.getControl( LABEL_ID_DURATION_2 )

			self.mCtrlProgress[0] = self.getControl( PROGRESS_ID_DURATION_1 )
			self.mCtrlProgress[1] = self.getControl( PROGRESS_ID_DURATION_2 )
		
			self.mCtrlCancelGroup = self.getControl( GROUP_ID_CANCEL )					
			self.mCtrlBackgroundImage = self.getControl( IMAGE_ID_BACKGROUND )


			if self.mBackgroundHeight <  0 :
				self.mBackgroundHeight = self.mCtrlBackgroundImage.getHeight( )

			self.SetHeaderLabel( MR_LANG( 'Stop Recording' ) )

			self.mLocalTime = self.mDataCache.Datetime_GetLocalTime( )
			
			self.Update( )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )
			
		self.mEnableThread = True
		self.mRecordingProgressThread = self.RecordingProgressThread( )
		self.mEventBus.Register( self )
		self.setProperty( 'DialogDrawFinished', 'True' )

		self.setFocusId( BUTTON_ID_RECORD_1 )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		if self.GlobalAction( actionId ) :
			return
		
		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.Close( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
		
		elif actionId == Action.ACTION_MOVE_UP :
			if focusId == BUTTON_ID_RECORD_1 :
				self.setFocusId( E_SETTING_DIALOG_BUTTON_CLOSE )
			elif focusId == BUTTON_ID_RECORD_2 :
				self.setFocusId( BUTTON_ID_RECORD_1 )
			elif focusId == BUTTON_ID_CANCEL :
				if self.mRunningRecordCount < 2 :
					self.setFocusId( BUTTON_ID_RECORD_1 )
				else :
					self.setFocusId( BUTTON_ID_RECORD_2 )
			elif focusId == E_SETTING_DIALOG_BUTTON_CLOSE :
				self.setFocusId( BUTTON_ID_CANCEL )
			else :
				self.setFocusId( BUTTON_ID_CANCEL )

		elif actionId == Action.ACTION_MOVE_DOWN :
			if focusId == BUTTON_ID_RECORD_1 :
				if self.mRunningRecordCount < 2 :
					self.setFocusId( BUTTON_ID_CANCEL )								
				else :
					self.setFocusId( BUTTON_ID_RECORD_2 )
			elif focusId == BUTTON_ID_RECORD_2 :
				self.setFocusId( BUTTON_ID_CANCEL )
			elif focusId == BUTTON_ID_CANCEL :
				self.setFocusId( E_SETTING_DIALOG_BUTTON_CLOSE )
			elif focusId == E_SETTING_DIALOG_BUTTON_CLOSE :
				self.setFocusId( BUTTON_ID_RECORD_1 )
			else :
				self.setFocusId( BUTTON_ID_CANCEL )			


		elif actionId == Action.ACTION_MOVE_LEFT :
			pass
				
		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass
		else :
			LOG_WARN( 'Unknown Action' )


	def onClick( self, aControlId ) :
		LOG_TRACE( 'DialogRecord aControlId=%d' %aControlId )
		if aControlId == BUTTON_ID_RECORD_1 or aControlId == BUTTON_ID_RECORD_2 or aControlId == BUTTON_ID_CANCEL :
			self.StopRecord( aControlId )
		elif aControlId == E_SETTING_DIALOG_BUTTON_CLOSE :
			self.Close( )


	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		if xbmcgui.getCurrentWindowDialogId() == self.mWinId :
			if aEvent.getName() == ElisEventRecordingStarted.getName( ) or \
				aEvent.getName() == ElisEventRecordingStopped.getName( ) :
				self.Update( )


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.mEnableThread = False

		if self.mRecordingProgressThread :
			self.mRecordingProgressThread.join( )

		self.CloseDialog( )


	def StopRecord( self, aControlId ) :
		try :
			LOG_TRACE( 'aControlId=%d'% aControlId )
			if aControlId == BUTTON_ID_RECORD_1 :
				timer = self.mRunningTimerList[0]
				self.mDataCache.Timer_DeleteTimer( timer.mTimerId )
				self.mIsOk = E_DIALOG_STATE_YES
				self.Close( )
			elif aControlId == BUTTON_ID_RECORD_2 :
				timer = self.mRunningTimerList[1]
				self.mDataCache.Timer_DeleteTimer( timer.mTimerId )			
				self.mIsOk = E_DIALOG_STATE_YES
				self.Close( )
			elif aControlId == BUTTON_ID_CANCEL :
				self.mIsOk = E_DIALOG_STATE_CANCEL
				self.Close( )
			else :
				LOG_ERR( 'Could not find any control' )

		except Exception, e :
			LOG_ERR( 'Exception[%s]'% e )
			self.Close( )


	@RunThread
	def RecordingProgressThread( self ) :
		loop = 0
		while self.mEnableThread :
			if ( loop % 200 ) == 0 :
				self.mLocalTime = self.mDataCache.Datetime_GetLocalTime( )

			if ( loop % 20 ) == 0 :
				self.UpdateProgress( )
				self.mLocalTime += 1

			time.sleep( 0.05 )
			loop += 1


	def UpdateProgress( self ) :
		self.mLock.acquire( )

		for i in range( self.mRunningRecordCount ) :
			timer = self.mRunningTimerList[i]

			#timer.printdebug( )
			#LOG_TRACE( 'START REC: %s' %TimeToString( timer.mRecordStartedTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )			
			#LOG_TRACE( 'START : %s' %TimeToString( timer.mStartTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
			#LOG_TRACE( 'CUR : %s' %TimeToString( self.mLocalTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
			#LOG_TRACE( 'END : %s' %TimeToString( timer.mStartTime + timer.mDuration, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )

			recInfo = self.mDataCache.Record_GetRecordInfoByKey( timer.mRecordKey )
			duration = timer.mDuration

			if recInfo :
				LOG_TRACE( 'START REC: %s' %TimeToString( recInfo.mStartTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )	
				expectedRecording = self.mLocalTime - recInfo.mStartTime
				duration = timer.mRecordStartedTime + timer.mDuration -  recInfo.mStartTime
			else :
				expectedRecording = self.mLocalTime - timer.mRecordStartedTime

			if expectedRecording < 0 :
				expectedRecording = 0

			if duration <= 0 : #to avoid exception
				duration = 1

			#self.mCtrlDuration[i].setLabel( '%d/%d Min' %(int(expectedRecording/60) , int(timer.mDuration/60) ) )
			self.mCtrlDuration[i].setLabel( '%s' %(TimeToString( expectedRecording, TimeFormatEnum.E_HH_MM_SS ) ) )			
			self.mCtrlProgress[i].setPercent( int( expectedRecording*100/duration ) )

		self.mLock.release( )


	def DrawItem( self ) :
		if self.mRunningRecordCount < 2 :
			newHeight = self.mBackgroundHeight - self.mCtrlRecordGroup[0].getHeight( )
			self.mCtrlBackgroundImage.setHeight( newHeight )
			self.mCtrlRecordGroup[1].setVisible( False )
			
		else :
			self.mCtrlBackgroundImage.setHeight( self.mBackgroundHeight )		
			self.mCtrlRecordGroup[1].setVisible( True )

		for i in range( self.mRunningRecordCount ) :
			timer = self.mRunningTimerList[i]
			#LOG_TRACE( '---------timer ch[%s] name[%s]'% ( timer.mChannelNo, timer.mName ) )
			#channel = self.mDataCache.Channel_GetByNumber( timer.mChannelNo )

			iChNumber = timer.mChannelNo
			channel = self.mDataCache.GetChannelByIDs( timer.mSid, timer.mTsid, timer.mOnid )
			recInfo = self.mDataCache.Record_GetRunningRecordInfo( i )
			if recInfo :
				iChNumber = recInfo.mChannelNo
				if channel :
					iChNumber = channel.mNumber
					if E_V1_2_APPLY_PRESENTATION_NUMBER :
						iChNumber = self.mDataCache.CheckPresentationNumber( channel )

				self.mCtrlChannelName[i].setLabel( 'P%04d %s' %( iChNumber, recInfo.mChannelName ) )			
			else :
				self.mCtrlChannelName[i].setLabel( 'P%04d' %( timer.mChannelNo ) )
			self.mCtrlRecordName[i].setLabel( '%s' %timer.mName )


	def IsOK( self ) :
		return self.mIsOk


	def Update( self ) :
		self.mLock.acquire( ) 

		self.mRunningRecordCount = 0
		
		self.mRunningTimerList = self.mDataCache.Timer_GetRunningTimers( )

		if self.mRunningTimerList :
			self.mRunningRecordCount = len( self.mRunningTimerList )
			
		LOG_TRACE( "self.mRunningRecordCount=%d" %self.mRunningRecordCount )

		if self.mRunningRecordCount <= 0 :
			self.mLock.release( )
			xbmc.executebuiltin('xbmc.Action(previousmenu)')			
			#self.Close( )
			return

		else :
			self.DrawItem( )

		self.mLock.release( )


