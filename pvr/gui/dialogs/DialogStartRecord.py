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

		self.UpdateEPGTime( )

		self.mEventBus.Register( self )
		
		self.mEnableThread = True
		self.CurrentTimeThread( )
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
			LOG_WARN( 'Unknown Action' )


	def onClick( self, aControlId ) :
		focusId = self.getFocusId( )

		if focusId == E_BUTTON_START :
			self.StartRecord( )			

		elif focusId == E_BUTTON_CANCEL :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.Close( )

		elif focusId == E_BUTTON_DURATION :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			tempDuration = int( self.mRecordDuration / 60 )
			dialog.SetDialogProperty( 'Duration(Min)', '%d' %tempDuration  , 3 )
 			dialog.doModal( )
 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				duration = int( dialog.GetString( ) )
				LOG_TRACE('Duration = %d' % duration )

				if duration > 0 :
					if tempDuration != duration :
						self.mDurationChanged = True
					self.mRecordDuration = duration * 60
					self.UpdateEPGTime( )


	def onFocus( self, aControlId ) :
		pass


	@GuiLock	
	def onEvent( self, aEvent ) :
		pass


	def IsOK( self ) :
		return self.mIsOk


	def Close( self ):
		self.mEventBus.Deregister( self )
		self.mEnableThread = False
		self.CurrentTimeThread( ).join( )
		self.CloseDialog( )


	def Reload ( self ) :
		self.mEPG = self.mDataCache.Epgevent_GetPresent( )
		self.mRecordStartTime = self.mLocalTime - self.mLocalOffset
		
		if self.mEPG != None and self.mEPG.mError == 0 :
			startTime =  self.mEPG.mStartTime + self.mLocalOffset
			endTime = startTime + self.mEPG.mDuration

			self.mRecordDuration = endTime - self.mLocalTime
			self.mRecordName = self.mEPG.mEventName

			LOG_TRACE('START : %s' %TimeToString( startTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
			LOG_TRACE('CUR : %s' %TimeToString( self.mLocalTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )			
			LOG_TRACE('END : %s' %TimeToString( endTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )			

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
		
	
	def StartRecord( self ) :
		current = self.mDataCache.Channel_GetCurrent( )
		if self.mDurationChanged == True :
			ret = self.mDataCache.Timer_AddOTRTimer( False, self.mRecordDuration, 0,  self.mRecordName,  0,  0,  0,  0,  0 )
		else :	
			ret = self.mDataCache.Timer_AddOTRTimer( self.mHasEPG, self.mRecordDuration, 0,  self.mRecordName,  0,  0,  0,  0,  0 )
			
		if ret[0].mParam == -1 or ret[0].mError == -1 :
			self.RecordConflict( ret )
			self.mIsOk = E_DIALOG_STATE_CANCEL
		else :
			self.mIsOk = E_DIALOG_STATE_YES
		self.Close( )


	@RunThread
	def CurrentTimeThread( self ) :
		loop = 0

		while self.mEnableThread :
			if ( loop % 10 ) == 0 :
				LOG_TRACE( 'loop=%d' % loop )
				self.mLocalTime = self.mDataCache.Datetime_GetLocalTime( )

			self.UpdateEPGTime( )

			time.sleep( 1 )
			self.mLocalTime += 1			
			loop += 1


	@GuiLock	
	def UpdateEPGTime( self ) :
		self.UpdateProgress( )


	def UpdateProgress( self ) :
		startTime = self.mRecordStartTime + self.mLocalOffset
		endTime =  startTime + self.mRecordDuration

		passDuration = self.mLocalTime - startTime

		LOG_TRACE( 'UpdateProgress=%d' % passDuration )

		self.getControl( E_LABEL_EPG_START_TIME ).setLabel( TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
		self.getControl( E_LABEL_EPG_END_TIME ).setLabel( TimeToString( endTime, TimeFormatEnum.E_HH_MM ) )
		self.getControl( E_LABEL_DURATION ).setLabel( '%d(Min)' % int( self.mRecordDuration / ( 60 ) ) )			

		if endTime < self.mLocalTime : #Already past
			self.mCtrlProgress.setPercent( 100 )
			return
		elif self.mLocalTime < startTime :
			passDuration = 0

		if passDuration < 0 :
			passDuration = 0

		if self.mRecordDuration > 0 :
			percent = passDuration * 100 / self.mRecordDuration
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