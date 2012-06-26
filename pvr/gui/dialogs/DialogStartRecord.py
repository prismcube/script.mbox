from pvr.gui.WindowImport import *


# Control IDs
E_LABEL_RECORD_NAME			= 101
E_LABEL_EPG_START_TIME		= 102
E_LABEL_EPG_END_TIME		= 103
E_BUTTON_START				= 200
E_BUTTON_CANCEL				= 201
E_PROGRESS_EPG				= 400
E_BUTTON_DURATION			= 501
E_LABEL_DURATION			= 502



class DialogStartRecord( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mTimer = None
		self.mOTRInfo = None


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		self.SetHeaderLabel( 'Record' )

		self.mCtrlProgress = self.getControl( E_PROGRESS_EPG )
		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		
		self.mLocalTime = self.mDataCache.Datetime_GetLocalTime( )
		self.mRecordName = 'RecordName'

		self.mHasEPG = False
		self.mEPG = None

		self.Reload( )

		self.UpdateProgress( )

		self.mEventBus.Register( self )
		
		self.mEnableThread = True
		self.RecordingProgressThread( )
		self.mDurationChanged = False


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		self.GlobalAction( actionId )		

		LOG_TRACE( 'actionId=%d' %actionId )
			
		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.Close()		

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.Close()

		elif actionId == Action.ACTION_MOVE_UP :
			pass
	
		elif actionId == Action.ACTION_MOVE_DOWN :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT :
			pass
				
		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass
		else :
			LOG_WARN( 'Unknown Action actionId=%d' %actionId )


	def onClick( self, aControlId ) :
		focusId = self.getFocusId( )

		if focusId == E_BUTTON_START :
			self.StartRecord( )			

		elif focusId == E_BUTTON_CANCEL :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.Close( )

		elif focusId == E_BUTTON_DURATION :
			self.ChangeDuraton( )


	def onFocus( self, aControlId ) :
		pass


	@GuiLock	
	def onEvent( self, aEvent ) :
		pass


	def IsOK( self ) :
		return self.mIsOk


	def SetTimer( self, aTimer=None ) :
		self.mTimer = aTimer
		if self.mTimer :
			self.mTimer.printdebug( )



	def Close( self ):
		self.mEventBus.Deregister( self )
		self.mEnableThread = False
		self.CloseDialog( )


	def Reload ( self ) :
		try :
			if self.mTimer :
				self.getControl( E_LABEL_RECORD_NAME ).setLabel( self.mTimer.mName )
				self.getControl( E_BUTTON_START ).setLabel( 'Change Duration' )

			else :
				self.mOTRInfo = self.mDataCache.Timer_GetOTRInfo( )
				LOG_TRACE( '------------- LAEL98 TEST ----------------')
				self.mOTRInfo.printdebug( )
				LOG_TRACE( '------------- LAEL98 TEST ----------------')			

				self.getControl( E_BUTTON_START ).setLabel( 'Start Record' )		
				self.mEPG = self.mDataCache.Epgevent_GetPresent( )
				self.mRecordStartTime = self.mLocalTime - self.mLocalOffset
				
				if self.mEPG != None and self.mEPG.mError == 0 :
					startTime =  self.mEPG.mStartTime + self.mLocalOffset
					endTime = startTime + self.mEPG.mDuration

					self.mRecordDuration = endTime - self.mLocalTime
					self.mRecordName = self.mEPG.mEventName

					"""
					LOG_TRACE('START : %s' %TimeToString( startTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
					LOG_TRACE('CUR : %s' %TimeToString( self.mLocalTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
					LOG_TRACE('END : %s' %TimeToString( endTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
					"""

					#Check Valid EPG
					if startTime < self.mLocalTime and self.mLocalTime < endTime :
						self.mHasEPG = True
						self.getControl( E_LABEL_RECORD_NAME ).setLabel( '(%s~%s) %s' % ( TimeToString( startTime, TimeFormatEnum.E_HH_MM ), TimeToString( endTime, TimeFormatEnum.E_HH_MM ) , self.mRecordName) )

				if self.mHasEPG == False :
					prop = ElisPropertyEnum( 'Default Rec Duration', self.mCommander )
					self.mRecordDuration = prop.GetProp( )
					channel = self.mDataCache.Channel_GetCurrent( )
					self.mRecordName = channel.mName
					self.getControl( E_LABEL_RECORD_NAME ).setLabel( self.mRecordName )

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)


	def ChangeDuraton( self ) :
		try :
			if self.mTimer :
				tempDuration = int( self.mTimer.mDuration / 60 )
			else :
				tempDuration = int( self.mRecordDuration / 60 )

				
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( 'Duration(Min)', '%d' %tempDuration  , 3 )
 			dialog.doModal( )

 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				duration = int( dialog.GetString( ) )
				LOG_TRACE('Duration = %d' % duration )

				if duration > 0 :
					if tempDuration != duration :
						self.mDurationChanged = True

					if self.mTimer :
						self.mTimer.mDuration = duration * 60 
					else :
						self.mRecordDuration = duration * 60
					self.UpdateProgress( )

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)

	
	def StartRecord( self ) :
		try :
			if self.mTimer :
				self.mIsOk = E_DIALOG_STATE_CANCEL
				if self.mDurationChanged == True :
					if len(self.mTimer.self.mWeeklyTimer) > 0 :
						LOG_TRACE( 'ToDO : weely timer is running' )
						endTime = self.mTimer.mStartTime + self.mTimer.mDuration						
					else :
						endTime = self.mTimer.mStartTime + self.mTimer.mDuration
						
					LOG_TRACE('NEW END TIME : %s' %TimeToString( endTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )				
					if self.mDataCache.Timer_EditRunningTimer( self.mTimer.mTimerId, endTime ) == True :
						self.mIsOk = E_DIALOG_STATE_YES
					else :
						msg = 'Can not Change Duration'
						xbmcgui.Dialog( ).ok('ERROR', msg )

			else :
				current = self.mDataCache.Channel_GetCurrent( )
				ret = self.mDataCache.Timer_AddOTRTimer( False, self.mRecordDuration, 0,  self.mRecordName,  0,  0,  0,  0,  0 )
				"""
				if self.mDurationChanged == True :
					ret = self.mDataCache.Timer_AddOTRTimer( False, self.mRecordDuration, 0,  self.mRecordName,  0,  0,  0,  0,  0 )
				else :	
					ret = self.mDataCache.Timer_AddOTRTimer( self.mHasEPG, self.mRecordDuration, 0,  self.mRecordName,  0,  0,  0,  0,  0 )
				"""	
				if ret[0].mParam == -1 or ret[0].mError == -1 :
					self.RecordConflict( ret )
					self.mIsOk = E_DIALOG_STATE_CANCEL
				else :
					self.mIsOk = E_DIALOG_STATE_YES
		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)

		self.Close( )


	@RunThread
	def RecordingProgressThread( self ) :
		loop = 0

		while self.mEnableThread :
			if ( loop % 10 ) == 0 :
				LOG_ERR( 'loop=%d' % loop )
				self.mLocalTime = self.mDataCache.Datetime_GetLocalTime( )

			self.UpdateProgress( )

			time.sleep( 1 )
			self.mLocalTime += 1
			loop += 1


	@GuiLock	
	def UpdateProgress( self ) :
		if self.mTimer :
			if len(self.mTimer.self.mWeeklyTimer) > 0 :
				LOG_TRACE( 'ToDO : weely timer is running' )
				startTime = self.mTimer.mStartTime
				endTime = startTime + self.mTimer.mDuration
			else :
				startTime = self.mTimer.mStartTime
				endTime = startTime + self.mTimer.mDuration

			duration = self.mTimer.mDuration

		else :
			startTime = self.mRecordStartTime + self.mLocalOffset
			endTime =  startTime + self.mRecordDuration
			duration = self.mRecordDuration

		passDuration = self.mLocalTime - startTime

		#LOG_TRACE( 'UpdateProgress=%d' % passDuration )

		self.getControl( E_LABEL_EPG_START_TIME ).setLabel( TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
		self.getControl( E_LABEL_EPG_END_TIME ).setLabel( TimeToString( endTime, TimeFormatEnum.E_HH_MM ) )
		self.mWin.setProperty( 'Duration', '%d(Min)' % int( duration / ( 60 ) ) )		
		#self.getControl( E_LABEL_DURATION ).setLabel( '%d(Min)' % int( self.mRecordDuration / ( 60 ) ) )			

		if endTime < self.mLocalTime : #Already past
			self.mCtrlProgress.setPercent( 100 )
			return
		elif self.mLocalTime < startTime :
			passDuration = 0

		if passDuration < 0 :
			passDuration = 0

		if duration > 0 :
			percent = passDuration * 100 / duration
		else :
			percent = 0

		LOG_TRACE( 'percent=%d' %percent )
		
		self.mCtrlProgress.setPercent( percent )


	def RecordConflict( self, aInfo ) :
		label = [ '', '', '' ]
		if aInfo[0].mError == -1 :
			label[0] = 'Error EPG'
			label[1] = 'Can not found EPG Information'
		else :
			conflictNum = len( aInfo ) - 1
			if conflictNum > 3 :
				conflictNum = 3
			for i in range( conflictNum ) :
				timer = self.mDataCache.Timer_GetById( aInfo[ i + 1 ].mParam )
				time = '%s~%s' % ( TimeToString( timer.mStartTime, TimeFormatEnum.E_HH_MM ), TimeToString( timer.mStartTime + timer.mDuration, TimeFormatEnum.E_HH_MM ) )
				channelNum = '%04d' % timer.mChannelNo
				epgNAme = timer.mName
				label[i] = time + ' ' + channelNum + ' ' + epgNAme
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( 'Conflict', label[0], label[1], label[2] )
		dialog.doModal( )

