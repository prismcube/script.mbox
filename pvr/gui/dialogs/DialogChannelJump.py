from pvr.gui.WindowImport import *


E_CHANNEL_NUM_ID	= 210
E_CHANNEL_NAME_ID	= 211
E_EPG_NAME_ID		= 212
E_PROGRESS_ID		= 213
E_DEFAULT_CLOSE_TIME = 1.2


class DialogChannelJump( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mChannelNumber		= ''
		self.mCtrlChannelNum	= None
		self.mCtrlChannelName	= None
		self.mCtrlEPGName		= None
		self.mCtrlProgress		= None

		self.mFlagFind          = False
		self.mChannelListHash   = {}
		self.mAsyncTuneTimer    = None
		self.mFakeChannel       = None
		self.mFakeEPG           = None

		self.mMaxChannelNum		= E_INPUT_MAX
		self.mIsOk              = E_DIALOG_STATE_CANCEL
		self.mIsChannelListWindow = False
		self.mBackKeyCheck = False


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.mCtrlChannelNum	= self.getControl( E_CHANNEL_NUM_ID )
		self.mCtrlChannelName	= self.getControl( E_CHANNEL_NAME_ID )
		self.mCtrlEPGName		= self.getControl( E_EPG_NAME_ID )
		self.mCtrlProgress		= self.getControl( E_PROGRESS_ID )

		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		self.mFindChannel = None
		self.mAsynViewTime = E_DEFAULT_CLOSE_TIME
		self.mPreviousCount = 0

		self.SetLabelChannelNumber( )
		self.SetLabelChannelName( )
		self.SearchChannel( )
		self.mIsOk = E_DIALOG_STATE_CANCEL
		#self.mOnInitTime = time.time( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			if actionId == Action.ACTION_PARENT_DIR and self.mBackKeyCheck :
				self.mPreviousCount += 1
				#if self.mPreviousCount > 2 :
				#	self.StopAsyncTune( )
				#	self.CloseDialog( )

				return

			self.CloseDialog( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 :
			if self.mBackKeyCheck :
				LOG_TRACE( 'Back key mode, no receive input' )
				return

			inputString = '%d' % ( int( actionId ) - Action.REMOTE_0 )
			self.mChannelNumber += inputString
			self.mChannelNumber = '%d' % int( self.mChannelNumber )
			if int( self.mChannelNumber ) > self.mMaxChannelNum :
				self.mChannelNumber = inputString
			self.SetLabelChannelNumber( )

			self.SetLabelChannelName( )
			self.SetLabelEPGName( )
			self.SetPogress( )
			self.SearchChannel( )

		elif actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :
			inputNum = actionId - ( Action.ACTION_JUMP_SMS2 - 2 )
			if self.mBackKeyCheck :
				LOG_TRACE( 'Back key mode, no receive input' )
				return

			if inputNum >= 2 and inputNum <= 9 :
				inputString = '%d' % inputNum
				self.mChannelNumber += inputString
				self.mChannelNumber = '%d' % int( self.mChannelNumber )
				if int( self.mChannelNumber ) > self.mMaxChannelNum :
					self.mChannelNumber = inputString
				self.SetLabelChannelNumber( )

				self.SetLabelChannelName( )
				self.SetLabelEPGName( )
				self.SetPogress( )
				self.SearchChannel( )


	def onClick( self, aControlId ) :
		pass


	def onFocus( self, aControlId ) :
		pass


	def SetDialogProperty( self, aChannelFirstNum, aChannelListHash = None, aIsChannelListWindow = False, aMaxChannelNum = E_INPUT_MAX ) :
		self.mChannelNumber	= aChannelFirstNum
		self.mMaxChannelNum = aMaxChannelNum
		self.mChannelListHash = aChannelListHash
		self.mIsChannelListWindow = aIsChannelListWindow


	def SetLabelChannelNumber( self ) :
		self.mFlagFind = False
		self.mCtrlChannelNum.setLabel( self.mChannelNumber )


	def SetLabelChannelName( self, aChannelName = MR_LANG( 'No Channel' ) ) :
		self.mCtrlChannelName.setLabel( aChannelName )


	def SetLabelEPGName( self, aEPGName = '' ) :
		self.mCtrlEPGName.setLabel( aEPGName )


	def SetPogress( self, aPercent = 0 ) :
		self.mCtrlProgress.setPercent( aPercent )


	def Channel_GetByNumberFromChannelListWindow( self, aNumber ) :
		LOG_TRACE('hash len[%s] get[%s]'% ( len( self.mChannelListHash ), aNumber ) )
		if not self.mChannelListHash :
			return None

		iChannel = self.mChannelListHash.get( aNumber, None )
		if iChannel == None :
			return None

		LOG_TRACE('found[%s]'% iChannel.mNumber )
		return iChannel


	def SearchChannel( self ) :
		if self.mIsChannelListWindow :
			fChannel = self.Channel_GetByNumberFromChannelListWindow( int( self.mChannelNumber ) )
		else:
			fChannel = self.mDataCache.Channel_GetByNumber( int( self.mChannelNumber ) )

		if fChannel == None or fChannel.mError != 0 :
			LOG_TRACE( 'No search channel[%s]'% self.mChannelNumber )
			self.mFlagFind = True
			self.mFindChannel = self.mDataCache.Channel_GetCurrent( )
			self.mAsynViewTime = 5
			self.RestartAsyncTune( )
			return

		#retList = []
		#retList.append( fChannel )
		#LOG_TRACE( '======= Search Channel[%s]'% ClassToList('convert', retList) )
		self.mFindChannel = fChannel

		self.SetLabelChannelName( fChannel.mName )
		self.GetEPGInfo( fChannel )

		self.mFlagFind = True
		self.mAsynViewTime = E_DEFAULT_CLOSE_TIME
		self.RestartAsyncTune( )


	def GetEPGInfo( self, aChannel ) :
		sid  = aChannel.mSid
		tsid = aChannel.mTsid
		onid = aChannel.mOnid
		#gmtime = self.mDataCache.Datetime_GetGMTTime( )
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
			self.GetEPGProgress( )


	def GetEPGProgress( self ) :
		try:
			mLocalTime = self.mDataCache.Datetime_GetGMTTime( )

			if self.mFakeEPG :
				startTime = self.mFakeEPG.mStartTime + self.mLocalOffset
				endTime   = startTime + self.mFakeEPG.mDuration
				pastDuration = endTime - mLocalTime

				if mLocalTime > endTime: #Already passed
					self.SetPogress( 100 )
					return

				elif mLocalTime < startTime :
					self.SetPogress( 0 )
					return

				if pastDuration < 0 :
					pastDuration = 0

				if self.mFakeEPG.mDuration > 0 :
					percent = 100 - ( pastDuration * 100.0 / self.mFakeEPG.mDuration )
				else :
					percent = 0

				#LOG_TRACE( 'percent=%d'% percent )
				self.SetPogress( percent )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def SetBackKeyCheck( self, aBackKeyCheck = False ) :
		self.mBackKeyCheck = aBackKeyCheck


	def GetPreviousKey( self ) :
		return self.mPreviousCount


	def GetChannelLast( self ) :
		return self.mChannelNumber


	def IsOK( self ) :
		return self.mIsOk


	def RestartAsyncTune( self ) :
		self.StopAsyncTune( )
		self.StartAsyncTune( )


	def StartAsyncTune( self ) :
		self.mAsyncTuneTimer = threading.Timer( self.mAsynViewTime, self.AsyncTuneChannel )
		self.mAsyncTuneTimer.start( )


	def StopAsyncTune( self ) :
		if self.mAsyncTuneTimer	and self.mAsyncTuneTimer.isAlive( ) :
			self.mAsyncTuneTimer.cancel( )
			del self.mAsyncTuneTimer

		self.mAsyncTuneTimer  = None


	def AsyncTuneChannel( self ) :
		if self.mFlagFind :
			self.mIsOk = E_DIALOG_STATE_YES
			self.CloseDialog( )


