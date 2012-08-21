from pvr.gui.WindowImport import *


# Control IDs
E_LABEL_RECORD_NAME			= 101
E_LABEL_EPG_START_TIME		= 102
E_LABEL_EPG_END_TIME		= 103
E_PROGRESS_EPG				= 400
#E_DialogInput01



class DialogRecord( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )

	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowDialogId()
		self.mWin = xbmcgui.Window( self.mWinId  )

		self.SetHeaderLabel( 'Start Recording' )
		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_OK_ID, 'Start' )
		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_CANCEL_ID, 'Cancel' )

		self.mCtrlProgress = self.getControl( E_PROGRESS_EPG )
		
		self.mLocalOffset = self.mCommander.Datetime_GetLocalOffset()
		self.mLocalTime = self.mCommander.datetime_GetLocalTime( )
		
		self.mRecordName = 'RecordName'

		epg=self.mCommander.Epgevent_GetPresent( )
		#epg.printdebug( )

		self.mHasEPG = False
		
		if epg != None and epg.mError == 0:
			self.mEPGStartTime = epg.mStartTime
			self.mEPGDuration = epg.mDuration
			self.mRecordName = epg.mEventName

			#Check Valid EPG
			startTime =  self.mEPGStartTime + self.mLocalOffset
			endTime = startTime + self.mEPGDuration


			if startTime < self.mLocalTime and self.mLocalTime < endTime :
				self.mHasEPG = True


		if self.mHasEPG == False :
			prop = ElisPropertyEnum( 'Default Rec Duration', self.mCommander )
			self.mEPGDuration = prop.GetProp( )
			self.mEPGStartTime = self.mLocalTime - self.mLocalOffset
			channel = self.mCommander.Channel_GetCurrent( )
			self.mRecordName = channel.mName
		
		LOG_TRACE('RecordName=%s Duration=%d' %(self.mRecordName, self.mEPGDuration ) )

		self.getControl( E_LABEL_RECORD_NAME ).setLabel( self.mRecordName )

		self.UpdateEPGTime()

		self.mEventBus.Register( self )
		
		self.mEnableThread = True
		self.CurrentTimeThread( )


	@GuiLock
	def onAction( self, action ):
		actionId = action.getId( )
		focusId = self.getFocusId( )

		self.GlobalAction( actionId )
			
		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
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
			print 'Unknown Action'


	@GuiLock	
	def onClick( self, controlId ):
		focusId = self.getFocusId( )

		print 'DialogRecord focusId=%d' %focusId
		if focusId == E_SETTING_DIALOG_BUTTON_OK_ID :
			self.StartRecord( )			

		elif focusId == E_SETTING_DIALOG_BUTTON_CANCEL_ID :
			self.Close( )


	@GuiLock
	def onFocus( self, controlId ):
		pass


	@GuiLock	
	def onEvent( self, event ):
		if xbmcgui.getCurrentWindowDialogId() == self.winId :
			print 'Do Event'
			pass

	def Close( self ):
		self.mEventBus.Deregister( self )
		self.mEnableThread = False
		self.CurrentTimeThread().join()
		self.CloseDialog( )


	def StartRecord( self ):
		print 'Start Record'
		current = self.mCommander.Channel_GetCurrent( )
		"""
		ret = self.mCommander.Record_StartRecord( int( current[0] ),  int( current[3] ),  self.mEPGDuration,  self.mRecordName )
		"""
		print 'Record Result=%s' %ret

		self.Close( )


	@RunThread
	def CurrentTimeThread(self):
		loop = 0

		while self.mEnableThread:
			if  ( loop % 10 ) == 0 :
				print 'loop=%d' %loop
				self.mLocalTime = self.mCommander.Datetime_GetLocalTime( )
				
			self.UpdateEPGTime( )

			time.sleep(1)
			self.mLocalTime += 1			
			loop += 1


	@GuiLock	
	def UpdateEPGTime( self ):
		self.UpdateProgress( )


	def UpdateProgress( self ):
		startTime = self.mEPGStartTime+ self.mLocalOffset
		endTime =  startTime  + self.mEPGDuration

		passDuration = self.mLocalTime - startTime

		print 'mLocalOffset=%d' % int( self.mLocalOffset/60 )
		print 'start=%s'%   TimeToString( startTime, TimeFormatEnum.E_HH_MM)
		print 'current=%s'% TimeToString( (endTime-startTime), TimeFormatEnum.E_HH_MM)
		print 'end=%s'%     TimeToString( endTime, TimeFormatEnum.E_HH_MM)

		print 'UpdateProgress=%d' %passDuration 

		startTimeString = TimeToString( startTime, TimeFormatEnum.E_HH_MM)
		endTimeString   = TimeToString( endTime, TimeFormatEnum.E_HH_MM)

		self.getControl( E_LABEL_EPG_START_TIME ).setLabel( startTimeString[1] )
		self.getControl( E_LABEL_EPG_END_TIME ).setLabel( endTimeString[1] )

		self.SetControlLabelString(E_DialogInput01, 'Duration' )
		if self.mHasEPG == True :
			recordDuration = endTime - self.mLocalTime
			if recordDuration < 0 :
				recordDuration = 0
			self.SetControlLabel2String(E_DialogInput01, '%d' %int( recordDuration/(60) ) ) 
			#self.getControl( E_LABEL_DURATION ).setLabel( '%d' %int( recordDuration/(60) )  )
		else :
			self.SetControlLabel2String(E_DialogInput01, '%d' %int( self.mEPGDuration/(60) ) )
			#self.getControl( E_LABEL_DURATION ).setLabel( '%d' % int( self.mEPGDuration/(60) ) )


		if endTime < self.mLocalTime : #Already past
			passDuration = 100
		elif self.mLocalTime < startTime :
			passDuration = 0

		if passDuration < 0 :
			passDuration = 0

		if self.mEPGDuration > 0 :
			percent = passDuration * 100/self.mEPGDuration
		else :
			percent = 0

		print 'percent=%d' %percent
		
		self.mCtrlProgress.setPercent( percent )


	def DrawItem( self ) :
		self.ResetAllControl( )
		self.AddInputControl( E_DialogInput01, 'Start' , 'Duration' )
		self.AddOkCanelButton( )
		self.InitControl( )


