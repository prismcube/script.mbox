from pvr.gui.WindowImport import *

NEXT_EPG		= 0
PREV_EPG 		= 1

NEXT_CHANNEL	= 0
PREV_CHANNEL	= 1
CURR_CHANNEL	= 2

CONTEXT_ACTION_VIDEO_SETTING = 1 
CONTEXT_ACTION_AUDIO_SETTING = 2


class Test2( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )

		self.mLocalTime = 0
		self.mEventID = 0
		self.mCurrentChannel = None
		self.mLastChannel = None
		self.mFakeChannel = None
		self.mZappingMode = None

		self.mAutomaticHideTimer = None	
		self.mAsyncEPGTimer = None
		self.mAsyncTuneTimer = None	
		self.mAutomaticHide = True


	"""
	def __del__(self):
		LOG_TRACE( 'destroyed LivePlate' )

		# end thread CurrentTimeThread()
		self.mEnableThread = False
	"""


	def onInit ( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		LOG_TRACE( 'winID[%d]'% self.mWinId)

		self.mCtrlLblChannelNumber     = self.getControl( 601 )
		self.mCtrlLblChannelName       = self.getControl( 602 )
		self.mCtrlLblChannelNumber2    = self.getControl( 701 )
		self.mCtrlLblChannelName2      = self.getControl( 702 )


		#get channel
		self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
		self.mFakeChannel =	self.mCurrentChannel
		self.mLastChannel =	self.mCurrentChannel
		self.mFakeChannel2 =	self.mCurrentChannel
		self.mLastChannel2 =	self.mCurrentChannel

		self.InitLabelInfo()

		#run thread
		#self.mEnableThread = True
		#self.mEnableThread2 = True
		#self.ZappingThread1()
		#self.ZappingThread2()

	def onAction(self, aAction):
		id = aAction.getId()
		
		if id == Action.ACTION_PREVIOUS_MENU or id == Action.ACTION_PARENT_DIR:
			#WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
			self.Close()

		elif id == Action.REMOTE_0 : 
			xbmc.executebuiltin('XBMC.ReloadSkin()')

		elif id == 104 : #scroll up
			xbmc.executebuiltin('XBMC.ReloadSkin()')

		elif id == Action.ACTION_PAGE_UP:

			self.ChannelTune( NEXT_CHANNEL )
			self.ChannelTune2( NEXT_CHANNEL )

		elif id == Action.ACTION_PAGE_DOWN:

			self.ChannelTune( PREV_CHANNEL )
			self.ChannelTune2( PREV_CHANNEL )


	def onFocus(self, aControlId):
		pass


	@RunThread
	def ChannelTune(self, aDir):

		if self.mDataCache.mStatusIsArchive :
			LOG_TRACE('Archive playing now')
			return -1

		if aDir == PREV_CHANNEL:
		
			prevChannel = self.mDataCache.Channel_GetPrev( self.mFakeChannel )

			if prevChannel == None or prevChannel.mError != 0 :
				return

			self.mFakeChannel = prevChannel
			#self.InitLabelInfo()
			self.UpdateLabelGUI( self.mCtrlLblChannelNumber.getId(), ('%s'% self.mFakeChannel.mNumber) )
			self.UpdateLabelGUI( self.mCtrlLblChannelName.getId(), self.mFakeChannel.mName )
			self.RestartAsyncTune()

		elif aDir == NEXT_CHANNEL:
			nextChannel = self.mDataCache.Channel_GetNext( self.mFakeChannel )

			if nextChannel == None or nextChannel.mError != 0 :
				return

			self.mFakeChannel = nextChannel
			#self.InitLabelInfo()
			self.UpdateLabelGUI( self.mCtrlLblChannelNumber.getId(), ('%s'% self.mFakeChannel.mNumber) )
			self.UpdateLabelGUI( self.mCtrlLblChannelName.getId(), self.mFakeChannel.mName )
			self.RestartAsyncTune()
			#LOG_TRACE( 'ch[%s] name[%s]'% (self.mFakeChannel.mNumber, self.mFakeChannel.mName) )


	@RunThread
	def ChannelTune2(self, aDir):

		if WinMgr.GetInstance().GetWindow( WinMgr.WIN_ID_NULLWINDOW ).GetKeyDisabled() :
			LOG_TRACE('Archive playing now')
			return -1

		if aDir == PREV_CHANNEL:
		
			prevChannel = self.mDataCache.Channel_GetPrev( self.mFakeChannel2 )

			if prevChannel == None or prevChannel.mError != 0 :
				return

			self.mFakeChannel2 = prevChannel
			#self.InitLabelInfo()
			self.UpdateLabelGUI( self.mCtrlLblChannelNumber2.getId(), ('%s'% self.mFakeChannel2.mNumber) )
			self.UpdateLabelGUI( self.mCtrlLblChannelName2.getId(), self.mFakeChannel2.mName )
			self.RestartAsyncTune()

		elif aDir == NEXT_CHANNEL:
			nextChannel = self.mDataCache.Channel_GetNext( self.mFakeChannel2 )

			if nextChannel == None or nextChannel.mError != 0 :
				return

			self.mFakeChannel2 = nextChannel
			#self.InitLabelInfo()
			self.UpdateLabelGUI( self.mCtrlLblChannelNumber2.getId(), ('%s'% self.mFakeChannel2.mNumber) )
			self.UpdateLabelGUI( self.mCtrlLblChannelName2.getId(), self.mFakeChannel2.mName )
			self.RestartAsyncTune()


	def InitLabelInfo(self):
		LOG_TRACE( 'Enter' )
		
		if self.mFakeChannel :
			self.UpdateLabelGUI( self.mCtrlLblChannelNumber.getId(), ('%s'% self.mFakeChannel.mNumber) )
			self.UpdateLabelGUI( self.mCtrlLblChannelName.getId(), self.mFakeChannel.mName )

			self.UpdateLabelGUI( self.mCtrlLblChannelNumber2.getId(), ('%s'% self.mFakeChannel2.mNumber) )
			self.UpdateLabelGUI( self.mCtrlLblChannelName2.getId(), self.mFakeChannel2.mName )

		else:
			LOG_TRACE( 'has no channel' )
		
			# todo 
			# show message box : has no channnel

		LOG_TRACE( 'Leave' )


	@GuiLock
	def UpdateLabelGUI( self, aCtrlID = None, aValue = None, aExtra = None ) :
		LOG_TRACE( 'Enter control[%s] value[%s]'% (aCtrlID, aValue) )

		if aCtrlID == self.mCtrlLblChannelNumber.getId( ) :
			self.mCtrlLblChannelNumber.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblChannelName.getId( ) :
			self.mCtrlLblChannelName.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblChannelNumber2.getId( ) :
			self.mCtrlLblChannelNumber2.setLabel( aValue )

		elif aCtrlID == self.mCtrlLblChannelName2.getId( ) :
			self.mCtrlLblChannelName2.setLabel( aValue )


		LOG_TRACE( 'Leave' )

	"""
	@RunThread
	def ZappingThread1( self ) :
		LOG_TRACE( 'begin_start thread' )

		while self.mEnableThread:

			if self.mDataCache.mStatusIsArchive :
				LOG_TRACE('Archive playing now')
				continue

			self.ChannelTune( NEXT_CHANNEL )
			time.sleep(0.4)

		LOG_TRACE( 'leave_end thread' )


	@RunThread
	def ZappingThread2( self ) :
		LOG_TRACE( 'begin_start thread' )

		while self.mEnableThread2:

			isArchive = WinMgr.GetInstance().GetWindow( WinMgr.WIN_ID_NULLWINDOW ).GetKeyDisabled( )
			if isArchive :
				LOG_TRACE('Archive playing now')
				continue

			self.ChannelTune2( CURR_CHANNEL )
			time.sleep(0.4)

		LOG_TRACE( 'leave_end thread' )
	"""

	def Close( self ):
		#self.mEnableThread = False
		#self.mEnableThread2 = False
		#self.ZappingThread1().join()
		#self.ZappingThread2().join()
		
		self.StopAsyncTune()
		self.StopAutomaticHide()

		self.close()


	def SetAutomaticHide( self, aHide=True ) :
		self.mAutomaticHide = aHide


	def GetAutomaticHide( self ) :
		return self.mAutomaticHide


	def AsyncAutomaticHide( self ) :
		self.Close()


	def RestartAutomaticHide( self ) :
		self.StopAutomaticHide()
		self.StartAutomaticHide()


	def StartAutomaticHide( self ) :
		prop = ElisPropertyEnum( 'Channel Banner Duration', self.mCommander )
		bannerTimeout = prop.GetProp()
		self.mAutomaticHideTimer = threading.Timer( bannerTimeout, self.AsyncAutomaticHide )
		self.mAutomaticHideTimer.start()


	def StopAutomaticHide( self ) :
		if self.mAutomaticHideTimer and self.mAutomaticHideTimer.isAlive() :
			self.mAutomaticHideTimer.cancel()
			del self.mAutomaticHideTimer
			
		self.mAutomaticHideTimer = None


	def RestartAsyncTune( self ) :
		self.mFlag_ChannelChanged = True
		self.StopAsyncTune( )
		self.StartAsyncTune( )


	def StartAsyncTune( self ) :
		self.mAsyncTuneTimer = threading.Timer( 0.5, self.AsyncTuneChannel ) 				
		self.mAsyncTuneTimer.start()


	def StopAsyncTune( self ) :
		if self.mAsyncTuneTimer	and self.mAsyncTuneTimer.isAlive() :
			self.mAsyncTuneTimer.cancel()
			del self.mAsyncTuneTimer

		self.mAsyncTuneTimer  = None


	def AsyncTuneChannel( self ) :

		try :
			ret = self.mDataCache.Channel_SetCurrent( self.mFakeChannel.mNumber, self.mFakeChannel.mServiceType )
			#self.mFakeChannel.printdebug()
			if ret == True :
				self.mCurrentChannel = self.mDataCache.Channel_GetCurrent()
				self.mFakeChannel = self.mCurrentChannel
				self.mLastChannel = self.mCurrentChannel
				self.InitLabelInfo()

			else :
				LOG_ERR('Tune Fail')
			
		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

