from pvr.gui.WindowImport import *

E_CHANNEL_NUM_ID	= 210
E_CHANNEL_NAME_ID	= 211
E_EPG_NAME_ID		= 212
E_PROGRESS_ID		= 213

class DialogChannelJump( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )	
		self.mChannelNumber		= ''
		#self.mChannelName		= 'No channel'
		#self.mEPGName			= ''
		self.mCtrlChannelNum	= None
		self.mCtrlChannelName	= None
		self.mCtrlEPGName		= None
		self.mCtrlProgress		= None

		self.mFlagFind          = False
		self.mChannelList       = None
		self.mAsyncTuneTimer    = None
		self.mFakeChannel       = None
		self.mFakeEPG           = None
		self.mTestTime          = 0

		self.mMaxChannelNum		= E_INPUT_MAX
		self.mIsOk              = E_DIALOG_STATE_CANCEL


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mCtrlChannelNum	= self.getControl( E_CHANNEL_NUM_ID )
		self.mCtrlChannelName	= self.getControl( E_CHANNEL_NAME_ID )
		self.mCtrlEPGName		= self.getControl( E_EPG_NAME_ID )
		self.mCtrlProgress		= self.getControl( E_PROGRESS_ID )

		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset()

		self.SetLabelChannelNumber( )
		self.SetLabelChannelName( )
		self.SearchChannel()
				
	def onAction( self, aAction ) :
		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.CloseDialog( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
			
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.CloseDialog( )

		elif actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 :
			inputString = '%d' % ( actionId - Action.REMOTE_0 )
			self.mChannelNumber += inputString
			self.mChannelNumber = '%d' % int( self.mChannelNumber )
			if int( self.mChannelNumber ) > self.mMaxChannelNum :
				self.mChannelNumber = inputString
			self.SetLabelChannelNumber( )

			self.SetLabelChannelName()
			self.SetLabelEPGName()
			self.SetPogress()
			self.SearchChannel()

		elif actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :
			inputNum = actionId - (Action.ACTION_JUMP_SMS2 - 2)
			if inputNum >= 2 and inputNum <= 9 :
				inputString = '%d' % inputNum
				self.mChannelNumber += inputString
				self.mChannelNumber = '%d' % int( self.mChannelNumber )
				if int( self.mChannelNumber ) > self.mMaxChannelNum :
					self.mChannelNumber = inputString
				self.SetLabelChannelNumber( )

				self.SetLabelChannelName()
				self.SetLabelEPGName()
				self.SetPogress()
				self.SearchChannel()


	def onClick( self, aControlId ) :
		if aControlId == E_BUTTON_OK :
			self.CloseDialog( )


	def onFocus( self, aControlId ) :
		pass

		
	def SetDialogProperty( self, aChannelFirstNum, aMaxChannelNum, aChannelList, testTime = None ) :
		self.mChannelNumber	= aChannelFirstNum
		self.mMaxChannelNum = aMaxChannelNum
		self.mChannelList = aChannelList

		if testTime:
			self.mTestTime = testTime


	def SetLabelChannelNumber( self ) :
		self.mFlagFind = False
		self.mCtrlChannelNum.setLabel( self.mChannelNumber )

	def SetLabelChannelName( self, aChannelName='No Channel' ) :
		self.mCtrlChannelName.setLabel( aChannelName )

	def SetLabelEPGName( self, aEPGName='' ) :
		self.mCtrlEPGName.setLabel( aEPGName )

	def SetPogress( self, aPercent=0 ) :
		self.mCtrlProgress.setPercent( aPercent )

	def ChannelList_GetSearch( self, aNumber ):
		iChannel = None
		idx = 0
		for ch in self.mChannelList:
			if ch.mNumber == aNumber :
				iChannel = self.mChannelList[idx]
				LOG_TRACE('------- Success to searched[%s]'% iChannel.mNumber)
				break
			idx += 1

		return iChannel

	def SearchChannel( self ) :
		if self.mChannelList:
			fChannel = self.ChannelList_GetSearch( int(self.mChannelNumber) )
		else:
			fChannel = self.mDataCache.Channel_GetSearch( int(self.mChannelNumber) )

		if fChannel == None or fChannel.mError != 0 :
			LOG_TRACE('No search Channel[%s]'% self.mChannelNumber)
			return

		#retList = []
		#retList.append(fChannel)
		#LOG_TRACE('======= Search Channel[%s]'% ClassToList('convert', retList) )

		self.SetLabelChannelName( fChannel.mName )
		self.GetEPGInfo( fChannel )

		self.mFlagFind = True
		self.RestartAsyncTune()

	def GetEPGInfo( self, aChannel ):
		sid  = aChannel.mSid
		tsid = aChannel.mTsid
		onid = aChannel.mOnid
		#gmtime = self.mDataCache.Datetime_GetGMTTime()
		#gmtFrom = gmtime
		#gmtUntil= gmtime
		#maxCount= 1

		try:
			iEPGList = None
			iEPGList = self.mDataCache.Epgevent_GetCurrent( sid, tsid, onid )
			#iEPGList = self.mDataCache.Epgevent_GetListByChannel( sid, tsid, onid, gmtFrom, gmtUntil, maxCount )
		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )
			return -1


		if iEPGList :
			self.mFakeEPG = iEPGList
			self.SetLabelEPGName( self.mFakeEPG.mEventName )
			self.GetEPGProgress()

	def GetEPGProgress( self ):
		try:
			mLocalTime = self.mDataCache.Datetime_GetGMTTime()

			if self.mFakeEPG :
				startTime = self.mFakeEPG.mStartTime + self.mLocalOffset
				endTime   = startTime + self.mFakeEPG.mDuration
				pastDuration = endTime - mLocalTime

				if mLocalTime > endTime: #Already past
					self.SetPogress( 100 )
					return

				elif mLocalTime < startTime :
					self.SetPogress( 0 )
					return

				if pastDuration < 0 :
					pastDuration = 0

				if self.mFakeEPG.mDuration > 0 :
					#percent = pastDuration * 100/self.mFakeEPG.mDuration
					percent = 100 - (pastDuration * 100.0/self.mFakeEPG.mDuration )
				else :
					percent = 0

				#LOG_TRACE( 'percent=%d'% percent )
				self.SetPogress( percent )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def GetChannelLast( self ):
		return self.mChannelNumber

	def IsOK( self ) :
		return self.mIsOk

	def RestartAsyncTune( self ) :
		self.StopAsyncTune( )
		self.StartAsyncTune( )


	def StartAsyncTune( self ) :
		self.mAsyncTuneTimer = threading.Timer( 1, self.AsyncTuneChannel ) 				
		self.mAsyncTuneTimer.start()


	def StopAsyncTune( self ) :
		if self.mAsyncTuneTimer	and self.mAsyncTuneTimer.isAlive() :
			self.mAsyncTuneTimer.cancel()
			del self.mAsyncTuneTimer

		self.mAsyncTuneTimer  = None


	def AsyncTuneChannel( self ) :
		if self.mFlagFind :
			self.mIsOk = E_DIALOG_STATE_YES
			self.CloseDialog( )

