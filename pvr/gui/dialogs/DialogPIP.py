from pvr.gui.WindowImport import *

E_PIP_WINDOW_BASE_ID		=  WinMgr.WIN_ID_PIP_WINDOW * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID
CTRL_ID_BUTTON_SETTING_PIP	= E_PIP_WINDOW_BASE_ID + 0001

CTRL_ID_GROUP_PIP			= E_PIP_WINDOW_BASE_ID + 1000
CTRL_ID_IMAGE_FOCUSED		= E_PIP_WINDOW_BASE_ID + 1002
CTRL_ID_GROUP_INPUT			= E_PIP_WINDOW_BASE_ID + 1100
CTRL_ID_IMAGE_INPUTBG		= E_PIP_WINDOW_BASE_ID + 1101
CTRL_ID_LABEL_INPUTCH		= E_PIP_WINDOW_BASE_ID + 1102
CTRL_ID_LABEL_INPUTNAME		= E_PIP_WINDOW_BASE_ID + 1103

CTRL_ID_GROUP_OSD_STATUS	= E_PIP_WINDOW_BASE_ID + 2000
CTRL_ID_IMAGE_OSD_STATUS	= E_PIP_WINDOW_BASE_ID + 2002
CTRL_ID_LABEL_CHANNEL		= E_PIP_WINDOW_BASE_ID + 2001

CTRL_ID_IMAGE_ARROW_LEFT	= E_PIP_WINDOW_BASE_ID + 3001
CTRL_ID_IMAGE_ARROW_RIGHT	= E_PIP_WINDOW_BASE_ID + 3002
CTRL_ID_IMAGE_ARROW_TOP		= E_PIP_WINDOW_BASE_ID + 3003
CTRL_ID_IMAGE_ARROW_BOTTOM	= E_PIP_WINDOW_BASE_ID + 3004

CTRL_ID_LIST_CHANNEL_PIP    = E_PIP_WINDOW_BASE_ID + 3850

CTRL_ID_GROUP_LIST_PIP		= E_PIP_WINDOW_BASE_ID + 8000
CTRL_ID_BUTTON_NEXT_PIP		= E_PIP_WINDOW_BASE_ID + 8001
CTRL_ID_BUTTON_PREV_PIP		= E_PIP_WINDOW_BASE_ID + 8002
CTRL_ID_BUTTON_MUTE_PIP		= E_PIP_WINDOW_BASE_ID + 8003
CTRL_ID_BUTTON_ACTIVE_PIP	= E_PIP_WINDOW_BASE_ID + 8004
CTRL_ID_BUTTON_MOVE_PIP		= E_PIP_WINDOW_BASE_ID + 8005
CTRL_ID_BUTTON_SIZE_PIP		= E_PIP_WINDOW_BASE_ID + 8006
CTRL_ID_BUTTON_DEFAULT_PIP	= E_PIP_WINDOW_BASE_ID + 8007
CTRL_ID_BUTTON_EXIT_PIP		= E_PIP_WINDOW_BASE_ID + 8008
CTRL_ID_BUTTON_STOP_PIP		= E_PIP_WINDOW_BASE_ID + 8009
CTRL_ID_BUTTON_LIST_PIP		= E_PIP_WINDOW_BASE_ID + 8010

CTRL_ID_GROUP_LIST_2ND_PIP	= E_PIP_WINDOW_BASE_ID + 8100
CTRL_ID_BUTTON_MOVE_2ND_PIP	= E_PIP_WINDOW_BASE_ID + 8110
CTRL_ID_BUTTON_SIZE_2ND_PIP	= E_PIP_WINDOW_BASE_ID + 8111

CTRL_ID_IMAGE_BLANK			= E_PIP_WINDOW_BASE_ID + 1003
CTRL_ID_IMAGE_LOCK			= E_PIP_WINDOW_BASE_ID + 1004
CTRL_ID_LABEL_LOCK			= E_PIP_WINDOW_BASE_ID + 1005
CTRL_ID_LABEL_SCRAMBLE		= E_PIP_WINDOW_BASE_ID + 1006
CTRL_ID_LABEL_NOSIGNAL		= E_PIP_WINDOW_BASE_ID + 1007
CTRL_ID_LABEL_NOSERVICE		= E_PIP_WINDOW_BASE_ID + 1008

CTRL_ID_BASE_GROUP_PIP		 = E_BASE_WINDOW_ID + 8899
CTRL_ID_BASE_IMAGE_OVERLAY	 = E_BASE_WINDOW_ID + 2001
CTRL_ID_BASE_IMAGE_BLANK	 = E_BASE_WINDOW_ID + 2002
CTRL_ID_BASE_LABEL_LOCK		 = E_BASE_WINDOW_ID + 2004
CTRL_ID_BASE_LABEL_SCRAMBLE	 = E_BASE_WINDOW_ID + 2005
CTRL_ID_BASE_LABEL_NOSIGNAL	 = E_BASE_WINDOW_ID + 2006
CTRL_ID_BASE_LABEL_NOSERVICE = E_BASE_WINDOW_ID + 2007

E_DEFAULT_POSITION_PIP     = [827,125,352,188]#[857,170,352,198] 
E_SHOWLIST_POSITION_PIP    = [932,62,345,190]#[930,65,350,200]
CONTEXT_ACTION_DONE_PIP    = 0
CONTEXT_ACTION_MOVE_PIP    = 1
CONTEXT_ACTION_SIZE_PIP    = 2
CONTEXT_ACTION_SWITCH_PIP  = 3
CONTEXT_ACTION_DEFAULT_PIP = 4
CONTEXT_ACTION_STOP_PIP    = 5
CONTEXT_ACTION_LIST_PIP    = 6

E_POSX_ABILITY   = 20
E_POSY_ABILITY   = 10
E_WIDTH_ABILITY  = 20
E_HEIGHT_ABILITY = 10

CURR_CHANNEL_PIP = 0
PREV_CHANNEL_PIP = 1
NEXT_CHANNEL_PIP = 2
SWITCH_CHANNEL_PIP = 3
INPUT_CHANNEL_PIP  = 4
LIST_CHANNEL_PIP = 5

E_USE_CHANNEL_LOGO = True

PIP_CHECKWINDOW = [
	WinMgr.WIN_ID_NULLWINDOW,
	WinMgr.WIN_ID_SIMPLE_CHANNEL_LIST,
	WinMgr.WIN_ID_MAINMENU,
	WinMgr.WIN_ID_TIMESHIFT_PLATE,
	WinMgr.WIN_ID_INFO_PLATE,
	WinMgr.WIN_ID_LIVE_PLATE
]

WINDOW_ID_FULLSCREEN_VIDEO = 12005
WINDOW_ID_FULLSCREEN_AUDIO = 12006

XBMC_WINDOW_DIALOG_BUSY    = 10138

XBMC_CHECKWINDOW = [
	WINDOW_ID_FULLSCREEN_VIDEO,
	WINDOW_ID_FULLSCREEN_AUDIO
]


class DialogPIP( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mCurrentChannel = ElisIChannel( )
		self.mCurrentChannel.mNumber = self.mDataCache.Channel_GetCurrent( )
		self.mIsOk = None
		if E_V1_2_APPLY_PIP :
			self.mCurrentChannel.mNumber = self.mDataCache.PIP_GetCurrent( )
		self.mCurrentChannel.mError = -1
		self.mChannelLogo = pvr.ChannelLogoMgr.GetInstance( )


	def onInit( self ) :
		#self.SetFrontdisplayMessage( MR_LANG('PIP Channel') )
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		if not self.PIP_LoadToBaseControlIDs( ) :
			self.CloseDialog( )
			return

		#self.mCtrlImageBlank       = self.getControl( CTRL_ID_IMAGE_BLANK )
		#self.mCtrlLabelLock        = self.getControl( CTRL_ID_LABEL_LOCK )
		#self.mCtrlLabelScramble    = self.getControl( CTRL_ID_LABEL_SCRAMBLE )
		#self.mCtrlLabelNoSignal    = self.getControl( CTRL_ID_LABEL_NOSIGNAL )
		#self.mCtrlLabelNoService   = self.getControl( CTRL_ID_LABEL_NOSERVICE )

		self.mCtrlGroupPIP         = self.getControl( CTRL_ID_GROUP_PIP )
		self.mCtrlLabelChannel     = self.getControl( CTRL_ID_LABEL_CHANNEL )
		self.mCtrlImageFocusFO     = self.getControl( CTRL_ID_IMAGE_FOCUSED )
		self.mCtrlImageArrowLeft   = self.getControl( CTRL_ID_IMAGE_ARROW_LEFT )
		self.mCtrlImageArrowRight  = self.getControl( CTRL_ID_IMAGE_ARROW_RIGHT )
		self.mCtrlImageArrowTop    = self.getControl( CTRL_ID_IMAGE_ARROW_TOP )
		self.mCtrlImageArrowBottom = self.getControl( CTRL_ID_IMAGE_ARROW_BOTTOM )
		self.mCtrlGroupOsdStatus   = self.getControl( CTRL_ID_GROUP_OSD_STATUS )
		self.mCtrlImageOsdStatus   = self.getControl( CTRL_ID_IMAGE_OSD_STATUS )
		self.mCtrlGroupInput       = self.getControl( CTRL_ID_GROUP_INPUT )
		self.mCtrlImageInputBG     = self.getControl( CTRL_ID_IMAGE_INPUTBG )
		self.mCtrlLabelInputCH     = self.getControl( CTRL_ID_LABEL_INPUTCH )
		self.mCtrlLabelInputName   = self.getControl( CTRL_ID_LABEL_INPUTNAME )
		self.mCtrlGroupList2ndPIP  = self.getControl( CTRL_ID_GROUP_LIST_2ND_PIP )
		self.mCtrlListChannelPIP   = self.getControl( CTRL_ID_LIST_CHANNEL_PIP )

		#init tunable list : loop though or record full
		if self.mDataCache.Record_GetRunningRecorderCount( ) > 1 or \
		   ElisPropertyEnum( 'Tuner2 Connect Type', self.mCommander ).GetProp( ) == E_TUNER_LOOPTHROUGH :
			self.mDataCache.PIP_SetTunableList( )
			LOG_TRACE( '[PIP] init tunable list. loopthough or rec full' )

		self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( )
		self.mCurrentChannel = self.Channel_GetCurrentByStartOnFirst( )

		self.mChannelList     = []
		self.mChannelListHash = {}
		self.mTunableList     = []
		self.mListItems       = []
		self.mViewMode        = CONTEXT_ACTION_DONE_PIP
		self.mPosCurrent      = deepcopy( E_DEFAULT_POSITION_PIP )
		self.mPosBackup       = deepcopy( E_DEFAULT_POSITION_PIP )
		self.mPIP_EnableAudio = False
		self.mAsyncTuneTimer  = None
		self.mAsyncInputTimer = None
		self.mIndexAvail      = 0
		self.mFakeChannel     = self.mCurrentChannel
		self.mInputString     = ''
		self.mInitialized     = True
		self.mCheckMediaPlay  = False
		self.mCheckMediaPlayThread = None
		self.mLastNumber      = self.mDataCache.PIP_GetCurrent( )

		self.mHotKeyAvailableGreen = True
		self.mHotKeyAvailableYellow= True

		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		self.mEventBus.Register( self )

		self.Load( )
		self.setFocusId( CTRL_ID_BUTTON_LIST_PIP )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.mIsOk = actionId
		#LOG_TRACE('onAction[%d] pipStatus[%s]'% ( actionId, self.mViewMode ) )

		if self.mDataCache.GetMediaCenter( ) and ( xbmcgui.getCurrentWindowId( ) in XBMC_CHECKWINDOW ) :
			mExecute = False
			if actionId == Action.ACTION_MUTE :
				#self.UpdateVolume( 0 )
				self.mDataCache.LoadVolumeBySetGUI( )
				mExecute = True

			elif actionId == Action.ACTION_VOLUME_UP :
				#self.UpdateVolume( VOLUME_STEP )
				self.mDataCache.LoadVolumeBySetGUI( )
				mExecute = True

			elif actionId == Action.ACTION_VOLUME_DOWN :
				#self.UpdateVolume( -VOLUME_STEP )
				self.mDataCache.LoadVolumeBySetGUI( )
				mExecute = True

			if mExecute :
				return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			if self.mViewMode > CONTEXT_ACTION_DONE_PIP :
				self.mViewMode = CONTEXT_ACTION_DONE_PIP
				self.ResetLabel( )
				self.SavePipPosition( )
				return

			self.Close( False )

		elif actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 :

			inputString = '%d' % ( int( actionId ) - Action.REMOTE_0 )
			#LOG_TRACE( '[PIP] inputTot[%s] input[%s]'% ( self.mInputString, inputString ) )
			self.mInputString += inputString
			self.mInputString = '%d' % int( self.mInputString )
			if int( self.mInputString ) > E_INPUT_MAX :
				self.mInputString = inputString
			#LOG_TRACE( '[PIP] inputNum[%s]'% ( self.mInputString ) )

			self.ChannelTuneToPIP( INPUT_CHANNEL_PIP )

		elif actionId == Action.ACTION_MOVE_LEFT or actionId == Action.ACTION_MOVE_RIGHT :
			if self.mViewMode == CONTEXT_ACTION_LIST_PIP :
				self.mViewMode = CONTEXT_ACTION_DONE_PIP
				self.ResetLabel( ) 
				return

			self.DoSettingToPIP( actionId )

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN or \
		     actionId == Action.ACTION_PAGE_UP or actionId == Action.ACTION_PAGE_DOWN :

			if self.mViewMode == CONTEXT_ACTION_LIST_PIP :
				self.UpdateCurrentPositon( )

			else :
				if actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN :
					self.DoSettingToPIP( actionId )
				else :
					updown = NEXT_CHANNEL_PIP
					if actionId == Action.ACTION_PAGE_DOWN :
						updown = PREV_CHANNEL_PIP

					self.ChannelTuneToPIP( updown )

		elif actionId == Action.ACTION_MBOX_TVRADIO :
			LOG_TRACE( '[PIP] No Radio support' )
			return

		elif actionId == Action.ACTION_STOP :
			if self.mDataCache.GetMediaCenter( ) and ( xbmcgui.getCurrentWindowId( ) in XBMC_CHECKWINDOW ) :
				self.Close( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_COLOR_RED :
			self.Close( False )

		elif actionId == Action.ACTION_COLOR_GREEN :
			if self.mHotKeyAvailableGreen :
				self.ChannelTuneToPIP( SWITCH_CHANNEL_PIP )

		elif actionId == Action.ACTION_COLOR_YELLOW :
			if self.mHotKeyAvailableYellow :
				self.SetAudioPIP( )

		elif actionId == Action.ACTION_COLOR_BLUE :
			if self.mViewMode > CONTEXT_ACTION_DONE_PIP :
				if self.mViewMode != CONTEXT_ACTION_LIST_PIP :
					self.SavePipPosition( )

				self.mViewMode = CONTEXT_ACTION_DONE_PIP
				self.ResetLabel( )
				return

			self.Close( True )

		else :
			LOG_TRACE( '[PIP] Unknown key[%s]'% actionId )

#		elif actionId == Action.ACTION_CONTEXT_MENU :
#			if self.mViewMode == CONTEXT_ACTION_DONE_PIP :
#				self.ShowContextMenu( )

#		elif actionId == Action.ACTION_CONTEXT_MENU :
#			if self.mViewMode == CONTEXT_ACTION_MOVE_PIP :
#				self.DoContextAction( CONTEXT_ACTION_SIZE_PIP )
#			elif self.mViewMode == CONTEXT_ACTION_SIZE_PIP :
#				self.DoContextAction( CONTEXT_ACTION_MOVE_PIP )


	def onClick( self, aControlId ) :
		LOG_TRACE( '[PIP] onClick[%s]'% aControlId )

		if aControlId  == CTRL_ID_BUTTON_PREV_PIP :
			self.ChannelTuneToPIP( PREV_CHANNEL_PIP )

		elif aControlId  == CTRL_ID_BUTTON_NEXT_PIP :
			self.ChannelTuneToPIP( NEXT_CHANNEL_PIP )

		elif aControlId  == CTRL_ID_LIST_CHANNEL_PIP :
			self.ChannelTuneToPIP( LIST_CHANNEL_PIP )

		elif aControlId  == CTRL_ID_BUTTON_ACTIVE_PIP :
			self.ChannelTuneToPIP( SWITCH_CHANNEL_PIP )

		elif aControlId  == CTRL_ID_BUTTON_MUTE_PIP :
			self.SetAudioPIP( )

		elif aControlId  == CTRL_ID_BUTTON_MOVE_PIP or aControlId  == CTRL_ID_BUTTON_MOVE_2ND_PIP :
			if self.mViewMode == CONTEXT_ACTION_DONE_PIP :
				self.DoContextAction( CONTEXT_ACTION_MOVE_PIP )
			else :
				self.mViewMode = CONTEXT_ACTION_DONE_PIP
				self.ResetLabel( )
				self.SavePipPosition( )

		elif aControlId  == CTRL_ID_BUTTON_SIZE_PIP or aControlId  == CTRL_ID_BUTTON_SIZE_2ND_PIP :
			if self.mViewMode == CONTEXT_ACTION_DONE_PIP :
				self.DoContextAction( CONTEXT_ACTION_SIZE_PIP )
			else :
				self.mViewMode = CONTEXT_ACTION_DONE_PIP
				self.ResetLabel( )
				self.SavePipPosition( )

		elif aControlId  == CTRL_ID_BUTTON_DEFAULT_PIP :
			self.DoContextAction( CONTEXT_ACTION_DEFAULT_PIP )
			self.SavePipPosition( )

		elif aControlId  == CTRL_ID_BUTTON_EXIT_PIP :
			self.Close( False )

		elif aControlId  == CTRL_ID_BUTTON_STOP_PIP :
			self.DoContextAction( CONTEXT_ACTION_STOP_PIP )

		elif aControlId  == CTRL_ID_BUTTON_LIST_PIP :
			self.DoContextAction( CONTEXT_ACTION_LIST_PIP )


	def onFocus( self, aControlId ) :
		pass


	def GetCloseStatus( self ) :
		return self.mIsOk


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowDialogId( ) :
			LOG_TRACE( '[PIP] onEvent[%s]'% aEvent.getName( ) )

			if aEvent.getName( ) == ElisEventPIPKeyHook.getName( ) :
				LOG_TRACE( '[PIP] eventName[%s] keycode[%s]'% ( aEvent.getName( ), aEvent.mKeyCode ) )
				if aEvent.mKeyCode == 9 :
					thread = threading.Timer( 0, self.Close, [True] )
					thread.start( )

			elif aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or \
			   aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
				#if self.mIsUpdateEnable == True	:
				status = self.mDataCache.Player_GetStatus( )
				if status and status.mMode != ElisEnum.E_MODE_LIVE :
					#self.mDataCache.Player_Stop( )
					self.mIsOk = Action.ACTION_STOP
					self.Close( )

				LOG_TRACE( '[PIP] record start/stop event' )
				#ToDO

			elif aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
				LOG_TRACE( '[PIP] ElisEventPlaybackEOF mType[%d]'% ( aEvent.mType ) )
				if aEvent.mType == ElisEnum.E_EOF_END :
					LOG_TRACE( '[PIP] EventRecv EOF_END' )
					#self.mDataCache.Player_Stop( )
					self.mIsOk = Action.ACTION_STOP
					thread = threading.Timer( 0, self.Close, [False] )
					thread.start( )

			elif aEvent.getName( ) == ElisEventPlaybackStopped.getName( ) :
				thread = threading.Timer( 1, self.SetButtonExtended )
				thread.start( )

			"""
			elif aEvent.getName( ) == ElisEventChannelChangeStatus( ).getName( ) :
				LOG_TRACE( '[PIP] ElisEventChannelChangeStatus mStatus[%s]'% aEvent.mStatus )

				if aEvent.mStatus == ElisEnum.E_CC_PIP_FAILED_SCRAMBLED_CHANNEL :
					xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', 'True' )
					xbmcgui.Window( 10000 ).setProperty( 'PIPSignal', 'Scramble' )

				elif aEvent.mStatus == ElisEnum.E_CC_PIP_FAILED_PROGRAM_NOT_FOUND :
					xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', 'True' )
					xbmcgui.Window( 10000 ).setProperty( 'PIPSignal', 'NoService' )

				elif aEvent.mStatus == ElisEnum.E_CC_PIP_FAILED_NO_SIGNAL :
					xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', 'True' )
					xbmcgui.Window( 10000 ).setProperty( 'PIPSignal', 'False' )

				elif aEvent.mStatus == ElisEnum.E_CC_PIP_SUCCESS :
					xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', 'False' )
					xbmcgui.Window( 10000 ).setProperty( 'PIPSignal', 'True' )
			"""


	def Close( self, aStopPIP = True ) :
		LOG_TRACE( '[PIP] Window close')
		self.mEventBus.Deregister( self )

		self.setFocusId( CTRL_ID_BUTTON_LIST_PIP )
		self.UpdatePropertyGUI( 'ShowNamePIP', E_TAG_FALSE )

		winId = xbmcgui.getCurrentWindowId( )

		if self.mPIP_EnableAudio :
			self.mDataCache.PIP_EnableAudio( False )

		if aStopPIP or ( self.mDataCache.GetMediaCenter( ) and winId not in XBMC_CHECKWINDOW ) :
			ret = self.PIP_Stop( )

		if self.mDataCache.GetMediaCenter( ) and winId in XBMC_CHECKWINDOW :
			if self.mPIP_EnableAudio and winId in XBMC_CHECKWINDOW :
				self.SetAudioXBMC( True )

				# back? stay pip
				if not aStopPIP :
					self.mDataCache.PIP_Start( self.mFakeChannel.mNumber )

		self.StopAsyncHideInput( )
		if self.mAsyncTuneTimer	and self.mAsyncTuneTimer.isAlive( ) :
			self.mAsyncTuneTimer.join( )

		self.mCheckMediaPlay = False
		if self.mCheckMediaPlayThread and self.mCheckMediaPlayThread.isAlive( ) :
			self.mCheckMediaPlay = False
			self.mCheckMediaPlayThread.cancel( )
			del self.mCheckMediaPlayThread
		self.mCheckMediaPlayThread = None

		#self.PIP_PositionBackup( self.mPosCurrent )
		self.CloseDialog( )


	def CloseByMediaPlayStop( self ) :
		isClose = False
		while self.mCheckMediaPlay :
			time.sleep( 1 )
			if xbmcgui.getCurrentWindowId() not in XBMC_CHECKWINDOW :
				isClose = True
				break

		if isClose :
			self.Close( True )


	def PIP_Stop( self, aForce = False ) :
		winId = xbmcgui.getCurrentWindowId( )

		if self.mDataCache.GetMediaCenter( ) and winId in XBMC_CHECKWINDOW :
			self.mDataCache.PIP_EnableAudio( False )

		ret = self.mDataCache.PIP_Stop( )
		LOG_TRACE( '[PIP] PIP_Stop ret[%s]'% ret )
		if ret or aForce :
			self.mDataCache.PIP_SetStatus( False )
			xbmcgui.Window( 10000 ).setProperty( 'iLockPIP', E_TAG_FALSE )
			xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', E_TAG_FALSE )
			xbmcgui.Window( 10000 ).setProperty( 'OpenPIP', E_TAG_FALSE )

		return ret


	def PIP_Check( self, aStop = False ) :
		if not E_V1_2_APPLY_PIP :
			return

		if aStop == E_PIP_STOP or ( aStop != E_PIP_CHECK_FORCE and self.mDataCache.GetMediaCenter( ) ) :
			aStop = True
			if xbmcgui.getCurrentWindowId( ) in XBMC_CHECKWINDOW :
				aStop = False
				if self.mDataCache.PIP_IsStarted( ) :
					self.mDataCache.PIP_AVBlank( False )
					xbmcgui.Window( 10000 ).setProperty( 'OpenPIP', E_TAG_TRUE )

			if aStop :
				self.PIP_Stop( )

			return

		isShow = False
		if self.mDataCache.PIP_GetStatus( ) :
			#0. force stop by empty db
			chList = self.mDataCache.Channel_GetList( )
			if not chList or ( chList and len( chList ) < 1 ) :
				if self.mDataCache.Channel_GetCount( ElisEnum.E_SERVICE_TYPE_TV, True ) < 1 :
					#xbmc.executebuiltin( 'Notification(%s, %s, 5000, DefaultIconInfo.png)'% ( MR_LANG( 'Close PIP' ), MR_LANG( 'Close by delete all' ) ) )
					self.PIP_Stop( )
					return

			#1. show/hide auto
			if WinMgr.GetInstance( ).GetLastWindowID( ) in PIP_CHECKWINDOW :
				isShow = True

			ret = self.mDataCache.PIP_AVBlank( not isShow )
			xbmcgui.Window( 10000 ).setProperty( 'OpenPIP', '%s'% isShow )
			LOG_TRACE( '[PIP] GetLastWindowID[%s] isPIPShow[%s]'% ( WinMgr.GetInstance( ).GetLastWindowID( ), isShow ) )

		LOG_TRACE( '[PIP] mPIPStart[%s] OpenPIP[%s]'% ( self.mDataCache.PIP_GetStatus( ), xbmcgui.Window( 10000 ).getProperty( 'OpenPIP' ) ) )
		return isShow


	def PIP_Available( self ) :
		isAvailable = False
		if WinMgr.GetInstance( ).GetLastWindowID( ) in PIP_CHECKWINDOW :
			isAvailable = True

		return isAvailable


	def PIP_PositionBackup( self, aPos = None ) :
		try :
			posNotify = aPos
			if not posNotify :
				posNotify = self.LoadPositionPIP( )
			posStr = '%s|%s|%s|%s'% ( posNotify[0], posNotify[1], posNotify[2], posNotify[3] )
			df = open( '/mtmp/pipPos', 'w', 0644 )
			df.writelines( posStr )

		except Exception, e :
			LOG_ERR( '[PIP] except[%s]'% e )


	def PIP_SetPositionSync( self, aSetPosition = False ) :
		if not self.PIP_LoadToBaseControlIDs( ) :
			return

		try :
			posNotify = self.LoadPositionPIP( )

			x = posNotify[0]
			y = posNotify[1]
			w = posNotify[2]# + 10
			h = posNotify[3]# + 10

			#base overlay for radio mode
			bh = h - 10
			bw = w - 10
			self.mCtrlBasePIPGroup.setPosition( x, y )
			self.mCtrlBasePIPImageOverlay.setWidth( bw )
			self.mCtrlBasePIPImageOverlay.setHeight( bh )
			self.mCtrlBasePIPLabelLock.setWidth( bw )
			self.mCtrlBasePIPLabelLock.setPosition( 0, int( ( bh - 10 ) / 2 ) )
			self.mCtrlBasePIPLabelScramble.setWidth( bw )
			self.mCtrlBasePIPLabelScramble.setPosition( 0, int( ( bh - 10 ) / 2 ) )
			self.mCtrlBasePIPLabelNoSignal.setWidth( bw )
			self.mCtrlBasePIPLabelNoSignal.setPosition( 0, int( ( bh - 10 ) / 2 ) )
			self.mCtrlBasePIPLabelNoService.setWidth( bw )
			self.mCtrlBasePIPLabelNoService.setPosition( 0, int( ( bh - 10 ) / 2 ) )
			#self.mCtrlLabelChannel.setPosition( 5, bh - 25 )

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )
			return

		LOG_TRACE( '[PIP] PIP controls position sync' )

		if aSetPosition and self.mDataCache.PIP_GetStatus( ) :
			from pvr.GuiHelper import GetInstanceSkinPosition
			skinPos = GetInstanceSkinPosition( )
			x, y, w, h = skinPos.GetPipPosition2( x, y, w, h )

			self.mDataCache.PIP_SetDimension( x, y, w, h )


	def PIP_LoadToBaseControlIDs( self ) :
		ret = True
		try :
			self.mLastWindow = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW )
			if self.mDataCache.GetMediaCenter( ) :
				self.mLastWindow = xbmcgui.Window(xbmcgui.getCurrentWindowId())
				LOG_TRACE( '[PIP] Check current window[%s]'% xbmcgui.getCurrentWindowId() )
			self.mCtrlBasePIPGroup          = self.mLastWindow.getControl( CTRL_ID_BASE_GROUP_PIP )
			self.mCtrlBasePIPImageBlank     = self.mLastWindow.getControl( CTRL_ID_BASE_IMAGE_BLANK )
			self.mCtrlBasePIPImageOverlay   = self.mLastWindow.getControl( CTRL_ID_BASE_IMAGE_OVERLAY )
			self.mCtrlBasePIPLabelLock      = self.mLastWindow.getControl( CTRL_ID_BASE_LABEL_LOCK )
			self.mCtrlBasePIPLabelScramble  = self.mLastWindow.getControl( CTRL_ID_BASE_LABEL_SCRAMBLE )
			self.mCtrlBasePIPLabelNoSignal  = self.mLastWindow.getControl( CTRL_ID_BASE_LABEL_NOSIGNAL )
			self.mCtrlBasePIPLabelNoService = self.mLastWindow.getControl( CTRL_ID_BASE_LABEL_NOSERVICE )
		except Exception, e :
			LOG_ERR( '[PIP] except[%s]'% e )
			xbmc.executebuiltin( 'Notification(%s, %s, 5000, DefaultIconInfo.png)'% ( MR_LANG( 'Watching PIP' ), MR_LANG( 'only available when Video plays in fullscreen' ) ) )
			ret = False

		return ret


	def SetButtonExtended( self ) :
		mute = True
		full = True
		move = True
		size = True

		if self.mDataCache.GetMediaCenter( ) :
			mute = False
			full = False
			if E_SUPPORT_MEDIA_PLAY_AV_SWITCH :
				mute = True

		else :
			enable = True
			status = self.mDataCache.Player_GetStatus( )
			if status and status.mMode != ElisEnum.E_MODE_LIVE :
				mute = False
				full = False
				enable = False
				if E_SUPPORT_MEDIA_PLAY_AV_SWITCH :
					mute = True

			#self.getControl( CTRL_ID_BUTTON_ACTIVE_PIP ).setEnabled( enable )
			#self.getControl( CTRL_ID_BUTTON_MUTE_PIP ).setEnabled( enable )

		self.mHotKeyAvailableGreen = full
		self.mHotKeyAvailableYellow= mute
		self.getControl( CTRL_ID_BUTTON_MUTE_PIP ).setVisible( mute )
		self.getControl( CTRL_ID_BUTTON_ACTIVE_PIP ).setVisible( full )
		self.getControl( CTRL_ID_BUTTON_MOVE_PIP ).setVisible( move )
		self.getControl( CTRL_ID_BUTTON_SIZE_PIP ).setVisible( size )


	def DialogPopup( self, aTitle = '', aMsg = '' ) :
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( aTitle, aMsg )
		dialog.doModal( )


	def Load( self ) :
		if self.mDataCache.Channel_GetCount( ElisEnum.E_SERVICE_TYPE_TV, True ) < 1 :
			self.PIP_Stop( True )
			self.Close( )
			lblTitle = MR_LANG( 'Error' )
			lblMsg = MR_LANG( 'Your channel list is empty' )
			thread = threading.Timer( 0, self.DialogPopup, [lblTitle, lblMsg] )
			thread.start( )
			return

		self.SetButtonExtended( )
		thread = threading.Timer( 0, self.InitChannelList )
		thread.start( )

		if self.mDataCache.GetMediaCenter( ) :
			if self.mDataCache.PIP_GetStatus( ) :
				ret = self.mDataCache.PIP_Stop( )
				if ret :
					self.mDataCache.PIP_SetStatus( False )

			self.mCheckMediaPlay = True
			self.mCheckMediaPlayThread = threading.Timer( 0, self.CloseByMediaPlayStop )
			self.mCheckMediaPlayThread.start( )

		self.ResetLabel( )
		ret = self.ChannelTuneToPIP( CURR_CHANNEL_PIP )
		if ret :
			posNotify = self.LoadPositionPIP( )

			self.SetPositionPIP( posNotify[0], posNotify[1], posNotify[2], posNotify[3] )
			xbmcgui.Window( 10000 ).setProperty( 'OpenPIP', E_TAG_TRUE )

		self.setProperty( 'OpenPIP', E_TAG_TRUE )


	def LoadPositionPIP( self ) :
		try :
			posGet = GetSetting( 'PIP_POSITION' )
			LOG_TRACE( '[PIP] GetSetting posNotify[%s]'% posGet )

			posNotify = re.split( '\|', posGet )
			if not posNotify or len( posNotify ) != 4 :
				posNotify = E_DEFAULT_POSITION_PIP

			for i in range( len( posNotify ) ) :
				posNotify[i] = int( posNotify[i] )

		except Exception, e :
			LOG_ERR( '[PIP] except[%s]'% e )
			posNotify = E_DEFAULT_POSITION_PIP

		return posNotify


	def SavePipPosition( self ) :
		posNotify = '%s|%s|%s|%s'% ( self.mPosCurrent[0], self.mPosCurrent[1], self.mPosCurrent[2], self.mPosCurrent[3] )
		SetSetting( 'PIP_POSITION', posNotify )


	def SetPositionPIP( self, aPosX = 827, aPosY = 125, aWidth = 352, aHeight = 188 ) :
		self.mPosCurrent[0] = aPosX
		self.mPosCurrent[1] = aPosY
		self.mPosCurrent[2] = aWidth
		self.mPosCurrent[3] = aHeight

		from pvr.GuiHelper import GetInstanceSkinPosition
		skinPos = GetInstanceSkinPosition( )
		x, y, w, h = skinPos.GetPipPosition2( aPosX, aPosY, aWidth, aHeight )

		self.mDataCache.PIP_SetDimension( x - 1, y - 1, w + 4, h + 3 )

		#posNotify = '%s|%s|%s|%s'% ( self.mPosCurrent[0], self.mPosCurrent[1], self.mPosCurrent[2], self.mPosCurrent[3] )
		#SetSetting( 'PIP_POSITION', posNotify )

		self.SetGUIToPIP( )


	def InitChannelList( self ) :
		listItems = []
		self.mCtrlListChannelPIP.reset( )
		self.mChannelList = self.mDataCache.PIP_GetTunableList( )
		currentPos = 0
		channelCount = 0
		for iChannel in self.mChannelList :

			if self.mCurrentChannel and self.mCurrentChannel.mNumber == iChannel.mNumber :
				currentPos = channelCount

			iChNumber = iChannel.mNumber
			if E_V1_2_APPLY_PRESENTATION_NUMBER :
				iChNumber = self.mDataCache.CheckPresentationNumber( iChannel )

			listItem = xbmcgui.ListItem( '%04d'% iChNumber, '%s'% iChannel.mName )

			if E_USE_CHANNEL_LOGO :
				logo = '%s_%s' %( iChannel.mCarrier.mDVBS.mSatelliteLongitude, iChannel.mSid )
				chImage = self.mChannelLogo.GetLogo( logo )
				listItem.setProperty( 'ChannelLogo', '%s'% chImage )

			if iChannel.mLocked : 
				listItem.setProperty( E_XML_PROPERTY_LOCK, E_TAG_TRUE )
			if iChannel.mIsCA : 
				listItem.setProperty( E_XML_PROPERTY_CAS,  E_TAG_TRUE )
			if iChannel.mIsHD :
				listItem.setProperty( E_XML_PROPERTY_IHD, E_TAG_TRUE )

			channelCount += 1
			listItems.append( listItem )

		self.setProperty( 'ReadyToListPIP', E_TAG_TRUE )
		self.mCtrlListChannelPIP.addItems( listItems )

		#self.mCtrlListChannelPIP.selectItem( currentPos )
		self.UpdateControlListSelectItem( self.mCtrlListChannelPIP, currentPos )
		self.setProperty( 'SelectedPosition', '%s'% ( currentPos + 1 ) )


	def Channel_GetCurrentByStartOnFirst( self ) :
		if self.mDataCache.PIP_GetStatus( ) :
			return None

		#1. fixed No.50 : after start PIP, actual channel should be in small window
		iChannel = self.mDataCache.Channel_GetCurrent( )
		if iChannel and iChannel.mServiceType != ElisEnum.E_SERVICE_TYPE_TV :
			pChNumber = ElisPropertyInt( 'Last TV Number', self.mCommander ).GetProp( )
			iChannel = self.mDataCache.Channel_GetByNumber( pChNumber, True )

			if iChannel and ( not self.mDataCache.PIP_IsPIPAvailable( iChannel.mNumber ) ) :
				LOG_TRACE( '[PIP] failed : could not tune current channel, [%s] not available'% pChNumber )
				iChannel = None

		if not iChannel :
			channelList = self.mDataCache.PIP_GetTunableList( )
			LOG_TRACE('[PIP] PIP_GetTunableList len[%s]'% len( channelList ) )
			if channelList and len( channelList ) > 0 :
				for chNumber in channelList :
					if self.mDataCache.PIP_IsPIPAvailable( chNumber.mNumber ) :
						LOG_TRACE( '[PIP] 3. tunable : find channel by tunableList of PIP, [%s %s]'% ( chNumber.mNumber, chNumber.mName ) )
						break

		if iChannel :
			LOG_TRACE( '[PIP] Start on channel[%s %s]'% ( iChannel.mNumber, iChannel.mName ) )
		else :
			LOG_TRACE( '[PIP] Start on channel failed[%s]'% iChannel )

		return iChannel


	def Channel_GetCurrentByPIP( self ) :
		LOG_TRACE( '[PIP] is PIPStarted[%s]'% self.mDataCache.PIP_GetStatus( ) )

		#1. tunable : last channel by pip
		pChNumber = self.mDataCache.PIP_GetCurrent( )
		LOG_TRACE( '[PIP] 1. tunable : last PIP channel. [%s]'% pChNumber )
		if not pChNumber or ( not self.mDataCache.PIP_IsPIPAvailable( pChNumber ) ) :
			pChNumber = None

			#2. tunable : current channel by main(tv only)
			if not pChNumber :
				iChannel = self.mDataCache.Channel_GetCurrent( )
				if iChannel :
					pChNumber = iChannel.mNumber
					if iChannel.mServiceType != ElisEnum.E_SERVICE_TYPE_TV :
						pChNumber = ElisPropertyInt( 'Last TV Number', self.mCommander ).GetProp( )

					if not self.mDataCache.PIP_IsPIPAvailable( pChNumber ) :
						LOG_TRACE( '[PIP] failed : could not tune current channel. [%s] not available'% pChNumber )
						pChNumber = None

					else :
						#exist check
						if self.mDataCache.PIP_GetByNumber( pChNumber ) :
							LOG_TRACE( '[PIP] 2. tunable : current main sceen channel(tv only). [%s]'% pChNumber )
						else :
							LOG_TRACE( '[PIP] failed : current channel is not tunable list. [%s]'% pChNumber )
							pChNumber = None

			#3. tunable : find channel by tunableList of pip
			if not pChNumber :
				channelList = self.mDataCache.PIP_GetTunableList( )
				LOG_TRACE('[PIP] PIP_GetTunableList len[%s]'% len( channelList ) )
				if channelList and len( channelList ) > 0 :
					for chNumber in channelList :
						if self.mDataCache.PIP_IsPIPAvailable( chNumber.mNumber ) :
							pChNumber = chNumber.mNumber
							LOG_TRACE( '[PIP] 3. tunable : find channel by tunableList of PIP. [%s]'% pChNumber )
							break

			#4. tunable : find channel by channelList of main(tv only)
			if not pChNumber :
				channelList = self.mDataCache.Channel_GetList( )
				if self.mCurrentMode and self.mCurrentMode.mServiceType != ElisEnum.E_SERVICE_TYPE_TV :
					channelList = self.mDataCache.Channel_GetList( True, ElisEnum.E_SERVICE_TYPE_TV, ElisEnum.E_MODE_ALL, ElisEnum.E_SORT_BY_NUMBER )

				if channelList and len( channelList ) > 0 :
					for iChannel in channelList :
						if iChannel.mServiceType == ElisEnum.E_SERVICE_TYPE_TV and \
						   self.mDataCache.PIP_IsPIPAvailable( iChannel.mNumber ) :
							pChNumber = iChannel.mNumber
							LOG_TRACE( '[PIP] 4. tunable : find channel by channelList of main(tv only). [%s]'% pChNumber )
							break

		"""
		if not pChNumber :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			lblTitle = MR_LANG( 'Error' )
			lblMsg = MR_LANG( 'Your channel list is empty' )
			dialog.SetDialogProperty( lblTitle, lblMsg )
			dialog.doModal( )
		"""
		return pChNumber


	def ChannelTuneToPIP( self, aDir ) :
		fakeChannel = self.mCurrentChannel
		if aDir != INPUT_CHANNEL_PIP and aDir != CURR_CHANNEL_PIP and aDir != LIST_CHANNEL_PIP :
			xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', E_TAG_TRUE )

		if not fakeChannel or fakeChannel.mError != 0 or fakeChannel.mNumber == 0 :
			chNumber = self.Channel_GetCurrentByPIP( )
			fakeChannel = self.mDataCache.PIP_GetByNumber( chNumber )
			if not fakeChannel :
				fakeChannel = self.mDataCache.Channel_GetCurrent( )
				#LOG_TRACE( '---load to default------Channel_GetCurrentByPIP[%s(%s) %s]'% ( fakeChannel.mNumber, fakeChannel.mPresentationNumber, fakeChannel.mName ) )

		if aDir == PREV_CHANNEL_PIP :
			fakeChannel = self.mDataCache.PIP_GetPrev( fakeChannel )

		elif aDir == NEXT_CHANNEL_PIP :
			fakeChannel = self.mDataCache.PIP_GetNext( fakeChannel )

		elif aDir == LIST_CHANNEL_PIP :
			if not self.mChannelList or len( self.mChannelList ) < 1 :
				LOG_TRACE( '[PIP] tune fail, channel list None' )
				return

			idx = self.mCtrlListChannelPIP.getSelectedPosition( )
			if idx < len( self.mChannelList ) :
				fakeChannel = self.mChannelList[idx]
			else :
				LOG_TRACE( '[PIP] incorrect index, not exist position[%s]'% idx )
				return

			if self.mCurrentChannel and self.mCurrentChannel.mNumber == fakeChannel.mNumber :
				LOG_TRACE( '[PIP] passed, same channel' )
				return

			xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', E_TAG_TRUE )

		elif aDir == INPUT_CHANNEL_PIP :
			self.StopAsyncTune( )
			self.StopAsyncHideInput( )
			self.SetLabelInputNumber( )
			pChNumber = int( self.mInputString )
			hashPIP = self.mDataCache.PIP_GetTunableListHash( )
			cacheChannel = hashPIP.get( int( self.mInputString ), None )
			if cacheChannel :
				pChNumber = cacheChannel.mChannel.mNumber
			fakeChannel = self.mDataCache.PIP_GetByNumber( pChNumber )
			if fakeChannel :
				self.SetLabelInputName( fakeChannel.mName )
				self.RestartAsyncTune( fakeChannel )
			else :
				self.SetLabelInputName( )
				self.RestartAsyncHideInput( )

			return

		elif aDir == SWITCH_CHANNEL_PIP :
			isFail = False
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode != ElisEnum.E_MODE_LIVE :
				isFail = True
				LOG_TRACE( '[PIP] Cannot switch PIP. No Live program' )

			if ( not isFail ) and self.mCurrentMode and \
			   self.mCurrentMode.mServiceType != ElisEnum.E_SERVICE_TYPE_TV :
				isFail = True
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				lblTitle = MR_LANG( 'Error' )
				lblMsg = MR_LANG( 'To watch PIP, please switch from radio mode to TV mode' )
				dialog.SetDialogProperty( lblTitle, lblMsg )
				dialog.doModal( )

			iChannel = self.mDataCache.Channel_GetCurrent( )
			if ( not isFail ) and fakeChannel and iChannel :
				LOG_TRACE( '----------------main ch[%s %s] pip[%s %s]'% ( iChannel.mNumber, iChannel.mName, fakeChannel.mNumber, fakeChannel.mName ) )
				#check 1 - load tunable pip
				if iChannel.mSid == fakeChannel.mSid and iChannel.mTsid == fakeChannel.mTsid and iChannel.mOnid == fakeChannel.mOnid :
					isFail = True
					LOG_TRACE( '[PIP] Cannot switch PIP. Same channel' )

					# check 2 - last pip, issue 2661
					pipCurrent = self.mDataCache.PIP_GetCurrent( )
					pipCurrent = self.mDataCache.Channel_GetByNumber( pipCurrent, True )
					if pipCurrent :
						if iChannel.mSid != pipCurrent.mSid or iChannel.mTsid != pipCurrent.mTsid or iChannel.mOnid != pipCurrent.mOnid :
							isFail = False
							fakeChannel = pipCurrent
							LOG_TRACE( '[PIP] pipCurrent[%s %s]'% ( pipCurrent.mNumber, pipCurrent.mName ) )
							LOG_TRACE( '[PIP] Available switch PIP. different channel, check more pipCurrent' )

				# check 3 - find channel current mode
				if not isFail :
					if not self.mDataCache.GetChannelByIDs( fakeChannel.mSid, fakeChannel.mTsid, fakeChannel.mOnid ) :
						isFail = True
						curMode = EnumToString( 'mode', self.mCurrentMode.mMode )
						lblTitle = MR_LANG( 'Error' )
						lblMsg = MR_LANG( 'No service channel this mode' )
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( lblTitle, lblMsg )
						dialog.doModal( )

				if not isFail :
					if self.mDataCache.PIP_IsStarted( ) :

						if self.mDataCache.GetMediaCenter( ) and xbmcgui.getCurrentWindowId( ) in XBMC_CHECKWINDOW :
							if self.mPIP_EnableAudio :
								self.mDataCache.PIP_EnableAudio( False )

						self.mPIP_EnableAudio = False
						self.mDataCache.PIP_Stop( )
						self.setProperty( 'EnableAudioPIP', '%s'% self.mPIP_EnableAudio )

					ret = self.mDataCache.Channel_SetCurrentSync( fakeChannel.mNumber, ElisEnum.E_SERVICE_TYPE_TV, True )
					if ret :
						fakeChannel = iChannel

					else :
						isFail = True
						LOG_TRACE( '[PIP] Failed to switch, Full screen' )

			if isFail :
				if fakeChannel and ( not fakeChannel.mLocked ) and \
				   xbmcgui.Window( 10000 ).getProperty( 'PIPSignal' ) == E_TAG_TRUE :
					xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', E_TAG_FALSE )

				return

		elif aDir == CURR_CHANNEL_PIP :
			if self.mDataCache.PIP_GetStatus( ) :
				LOG_TRACE( '[PIP] already started' )
				#self.mDataCache.PIP_AVBlank( False )

				if fakeChannel :
					if fakeChannel.mLocked :
						xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', E_TAG_TRUE )
						xbmcgui.Window( 10000 ).setProperty( 'iLockPIP', E_TAG_TRUE )
						xbmcgui.Window( 10000 ).setProperty( 'PIPSignal', E_TAG_TRUE )

					else:
						xbmcgui.Window( 10000 ).setProperty( 'iLockPIP', E_TAG_FALSE )
						if xbmcgui.Window( 10000 ).getProperty( 'PIPSignal' ) == E_TAG_TRUE :
							xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', E_TAG_FALSE )
						else :
							#ToDO: one more, check PIP_IsStarted( )? or PIP_GetAVBlank( ) ?
							xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', E_TAG_TRUE )

					#check sync info, showChannel and PIPcurrent, reasen by TuneChannelByExternal() ?
					pipCurrent = self.mDataCache.Channel_GetByNumber( self.mLastNumber, True )
					LOG_TRACE( '[PIP] fakeChannel[%s %s]'% ( fakeChannel.mNumber, fakeChannel.mName ) )
					if pipCurrent :
						LOG_TRACE( '[PIP] pipCurrent[%s %s]'% ( pipCurrent.mNumber, pipCurrent.mName ) )
						if pipCurrent.mSid != fakeChannel.mSid or \
						   pipCurrent.mTsid != fakeChannel.mTsid or \
						   pipCurrent.mOnid != fakeChannel.mOnid :
							fakeChannel = pipCurrent
							#self.mCurrentChannel = pipCurrent

					self.SetLabelChannel( fakeChannel )

				return True

			xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', E_TAG_TRUE )
			if not fakeChannel :
				self.Close( )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				lblTitle = MR_LANG( 'Error' )
				lblMsg = MR_LANG( 'Unable to tune the channel on PIP' )
				dialog.SetDialogProperty( lblTitle, lblMsg )
				dialog.doModal( )
				return False

		if not fakeChannel :
			#have not tune
			fakeChannel = self.mDataCache.Channel_GetCurrent( )
			LOG_TRACE( '[PIP] have no channel. Restore default current channel' )

		if fakeChannel :
			self.SetLabelChannel( fakeChannel )
			self.mFakeChannel = fakeChannel
			self.RestartAsyncTune( )
			LOG_TRACE( '[PIP] up/down[%s] fakeChannel[%s %s]'% ( aDir, fakeChannel.mNumber, fakeChannel.mName ) )

		if self.mCurrentChannel :
			LOG_TRACE( '[PIP] up/down[%s] current[%s %s]'% ( aDir, self.mCurrentChannel.mNumber, self.mCurrentChannel.mName ) )

		return True


	def SetLabelInputNumber( self ) :
		imagePng = 'black-back_noAlpha.png'
		if xbmcgui.Window( 10000 ).getProperty( 'PIPSignal' ) != E_TAG_TRUE :
			imagePng = 'button-focus2.png'

		self.mCtrlImageInputBG.setImage( imagePng )
		xbmcgui.Window( 10000 ).setProperty( 'InputNumber', E_TAG_TRUE )
		self.mCtrlLabelInputCH.setLabel( self.mInputString )

	def SetLabelInputName( self, aChannelName = MR_LANG( 'No Channel' ) ) :
		self.mCtrlLabelInputName.setLabel( aChannelName )


	def SetLabelChannel( self, aChannel = None ) :
		if not aChannel :
			LOG_TRACE( 'No channel label' )
			return

		pChNumber = aChannel.mNumber
		if E_V1_2_APPLY_PRESENTATION_NUMBER :
			pChNumber = self.mDataCache.CheckPresentationNumber( aChannel )

		label = '%s - %s'% ( pChNumber, aChannel.mName )
		self.mCtrlLabelChannel.setLabel( label )
		#self.UpdatePropertyGUI( 'ShowPIPChannelNumber', '%s'% pChNumber ) 


	def ResetLabel( self ) :
		self.getFocusId( )
		if self.getFocusId( ) == CTRL_ID_LIST_CHANNEL_PIP :
			self.mPosCurrent = deepcopy( self.mPosBackup )
			self.SetPositionPIP( self.mPosCurrent[0], self.mPosCurrent[1], self.mPosCurrent[2], self.mPosCurrent[3] )

		self.UpdatePropertyGUI( 'SetContextAction', '' )
		self.UpdatePropertyGUI( 'ShowListPIP', E_TAG_FALSE )
		self.UpdatePropertyGUI( 'SettingPIP', E_TAG_FALSE )
		self.UpdatePropertyGUI( 'ShowOSDStatus', E_TAG_TRUE )
		self.UpdatePropertyGUI( 'ShowNamePIP', E_TAG_TRUE )
		xbmcgui.Window( 10000 ).setProperty( 'InputNumber', E_TAG_FALSE )

		time.sleep( 0.2 )
		currentFocus = CTRL_ID_GROUP_LIST_PIP
		if self.mViewMode == CONTEXT_ACTION_LIST_PIP :
			currentFocus = CTRL_ID_LIST_CHANNEL_PIP
		self.setFocusId( currentFocus )


	def UpdatePropertyGUI( self, aPropertyID = None, aValue = None ) :
		#LOG_TRACE( 'Enter property[%s] value[%s]'% (aPropertyID, aValue) )
		if aPropertyID == None :
			return False

		self.setProperty( aPropertyID, aValue )
		if aPropertyID == 'SettingPIP' and aValue == E_TAG_TRUE :
			lbltxt = ''
			if self.mViewMode == CONTEXT_ACTION_MOVE_PIP :
				lbltxt = MR_LANG( 'Move PIP window' )
			elif self.mViewMode == CONTEXT_ACTION_SIZE_PIP :
				lbltxt = MR_LANG( 'Resize PIP window' )

			self.setProperty( 'ShowOSDStatus', E_TAG_FALSE )
			self.setProperty( 'SetContextAction', lbltxt )
			self.SetGUIArrow( True )


	def UpdateCurrentPositon( self, aInput = False, aChannel = None ) :
		if self.mViewMode != CONTEXT_ACTION_LIST_PIP :
			LOG_TRACE( '[PIP] can not position, not list mode' )
			return

		if aInput :
			if not self.mChannelList :
				LOG_TRACE( '[PIP] ChannelList None' )
				return

			curNumber = 0
			if aChannel :
				curNumber = aChannel.mNumber

			else :
				if self.mCurrentChannel :
					curNumber = self.mCurrentChannel.mNumber
				else :
					curNumber = self.mDataCache.PIP_GetCurrent( )

			if not curNumber :
				LOG_TRACE( '[PIP] Current channel None' )
				return

			channelPos = 0
			currentPos = 0
			for iChannel in self.mChannelList :
				if iChannel.mNumber == curNumber :
					currentPos = channelPos
					break
				channelPos += 1

			#self.mCtrlListChannelPIP.selectItem( currentPos )
			self.UpdateControlListSelectItem( self.mCtrlListChannelPIP, currentPos )
			self.setProperty( 'SelectedPosition', '%s'% ( currentPos + 1 ) )

			LOG_TRACE( '[PIP] update position item' )

		else :
			idx = self.mCtrlListChannelPIP.getSelectedPosition( ) + 1
			self.setProperty( 'SelectedPosition', '%s'% idx )


	def ShowContextMenu( self ) :
		context = []
		context.append( ContextItem( MR_LANG( 'Position' ), CONTEXT_ACTION_MOVE_PIP ) )
		context.append( ContextItem( MR_LANG( 'Size' ), CONTEXT_ACTION_SIZE_PIP ) )
		context.append( ContextItem( MR_LANG( 'Swap Screen' ), CONTEXT_ACTION_SWITCH_PIP ) )
		context.append( ContextItem( MR_LANG( 'Reset' ), CONTEXT_ACTION_DEFAULT_PIP ) )
		context.append( ContextItem( MR_LANG( 'Close' ), CONTEXT_ACTION_STOP_PIP ) )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
 		dialog.doModal( )

		selectedAction = dialog.GetSelectedAction( )
		if selectedAction == -1 :
			#LOG_TRACE( 'CANCEL by context dialog' )
			return

		self.DoContextAction( selectedAction )


	def DoContextAction( self, aAction ) :
		self.mViewMode = aAction
		if aAction == CONTEXT_ACTION_MOVE_PIP :
			self.UpdatePropertyGUI( 'SettingPIP', E_TAG_TRUE ) 
			self.setFocusId( CTRL_ID_BUTTON_MOVE_PIP )
			self.setFocusId( CTRL_ID_BUTTON_MOVE_2ND_PIP )

		elif aAction == CONTEXT_ACTION_SIZE_PIP :
			self.UpdatePropertyGUI( 'SettingPIP', E_TAG_TRUE ) 
			self.setFocusId( CTRL_ID_BUTTON_SIZE_PIP )
			self.setFocusId( CTRL_ID_BUTTON_SIZE_2ND_PIP )

		elif aAction == CONTEXT_ACTION_SWITCH_PIP :
			pass

		elif aAction == CONTEXT_ACTION_DEFAULT_PIP :
			self.mViewMode = CONTEXT_ACTION_DONE_PIP
			self.SetPositionPIP( )
			self.setFocusId( CTRL_ID_GROUP_LIST_PIP )

		elif aAction == CONTEXT_ACTION_STOP_PIP :
			self.mViewMode = CONTEXT_ACTION_DONE_PIP
			self.Close( )

		elif aAction == CONTEXT_ACTION_LIST_PIP :
			self.UpdatePropertyGUI( 'ShowListPIP', E_TAG_TRUE ) 
			self.setFocusId( CTRL_ID_LIST_CHANNEL_PIP )
			self.mViewMode = CONTEXT_ACTION_LIST_PIP

			self.UpdateCurrentPositon( True )
			self.mPosBackup = deepcopy( self.mPosCurrent )
			x,y,w,h = E_SHOWLIST_POSITION_PIP
			self.SetPositionPIP( x, y, w, h )


	def DoSettingToPIP( self, aAction ) :
		ret = False
		if self.mViewMode == CONTEXT_ACTION_DONE_PIP :
			return ret

		elif self.mViewMode == CONTEXT_ACTION_SWITCH_PIP :
			#ToDO
			return ret

		elif self.mViewMode == CONTEXT_ACTION_LIST_PIP :
			return ret

		#self.setFocusId( CTRL_ID_GROUP_LIST_2ND_PIP )

		ret = True
		pipX, pipY, pipW, pipH = ( 0, 0, 0, 0 )
		if aAction == Action.ACTION_MOVE_LEFT :
			if self.mViewMode == CONTEXT_ACTION_MOVE_PIP : 
				pipX -= E_POSX_ABILITY
			elif self.mViewMode == CONTEXT_ACTION_SIZE_PIP : 
				pipW -= E_WIDTH_ABILITY
				pipH -= E_HEIGHT_ABILITY

		elif aAction == Action.ACTION_MOVE_RIGHT :
			if self.mViewMode == CONTEXT_ACTION_MOVE_PIP : 
				pipX += E_POSX_ABILITY
			elif self.mViewMode == CONTEXT_ACTION_SIZE_PIP : 
				pipW += E_WIDTH_ABILITY
				pipH += E_HEIGHT_ABILITY

		elif aAction == Action.ACTION_MOVE_UP :
			if self.mViewMode == CONTEXT_ACTION_MOVE_PIP : 
				pipY -= E_POSY_ABILITY
			elif self.mViewMode == CONTEXT_ACTION_SIZE_PIP : 
				pipW -= E_WIDTH_ABILITY
				pipH -= E_HEIGHT_ABILITY

		elif aAction == Action.ACTION_MOVE_DOWN :
			if self.mViewMode == CONTEXT_ACTION_MOVE_PIP : 
				pipY += E_POSY_ABILITY
			elif self.mViewMode == CONTEXT_ACTION_SIZE_PIP : 
				pipW += E_WIDTH_ABILITY
				pipH += E_HEIGHT_ABILITY

		posx  = self.mPosCurrent[0] + pipX
		posy  = self.mPosCurrent[1] + pipY
		width = self.mPosCurrent[2] + pipW
		height= self.mPosCurrent[3] + pipH
		LOG_TRACE( '[PIP] set posX[%s] posY[%s] width[%s] height[%s]'% ( posx, posy, width, height ) )

		#limit
		if posx < 0 or ( posx + width ) > 1280 or \
		   posy < 0 or ( posy + height) > 670 or \
		   width < ( E_DEFAULT_POSITION_PIP[2] / 2 ) or width > 1280 or \
		   height < ( E_DEFAULT_POSITION_PIP[3] / 2 ) or height > 600 :
			LOG_TRACE( '[PIP] limit False' )
			return ret

		self.SetPositionPIP( posx, posy, width, height )
		return ret


	def SetGUIToPIP( self ) :
		x = self.mPosCurrent[0]
		y = self.mPosCurrent[1]
		w = self.mPosCurrent[2]# + 10
		h = self.mPosCurrent[3]# + 10

		#ch name
		self.mCtrlLabelChannel.setWidth( w )

		#pip panel
		self.mCtrlGroupPIP.setPosition( x, y )

		self.mCtrlGroupPIP.setWidth( w )
		self.mCtrlGroupPIP.setHeight( h )

		self.mCtrlImageFocusFO.setWidth( w )
		self.mCtrlImageFocusFO.setHeight( h )

		#base overlay for radio mode
		bh = h - 10
		bw = w - 10
		self.mCtrlBasePIPGroup.setPosition( x, y )
		self.mCtrlBasePIPImageOverlay.setWidth( bw )
		self.mCtrlBasePIPImageOverlay.setHeight( bh )
		self.mCtrlBasePIPLabelLock.setWidth( bw )
		self.mCtrlBasePIPLabelLock.setPosition( 0, int( ( bh - 10 ) / 2 ) )
		self.mCtrlBasePIPLabelScramble.setWidth( bw )
		self.mCtrlBasePIPLabelScramble.setPosition( 0, int( ( bh - 10 ) / 2 ) )
		self.mCtrlBasePIPLabelNoSignal.setWidth( bw )
		self.mCtrlBasePIPLabelNoSignal.setPosition( 0, int( ( bh - 10 ) / 2 ) )
		self.mCtrlBasePIPLabelNoService.setWidth( bw )
		self.mCtrlBasePIPLabelNoService.setPosition( 0, int( ( bh - 10 ) / 2 ) )
		#self.mCtrlLabelChannel.setPosition( 5, bh - 25 )

		self.mCtrlBasePIPImageBlank.setWidth( bw )
		self.mCtrlBasePIPImageBlank.setHeight( bh )

		"""
		if self.mDataCache.GetMediaCenter( ) :
			#dialog control
			self.mCtrlImageBlank.setWidth( bw )
			self.mCtrlImageBlank.setHeight( bh )
			self.mCtrlLabelLock.setWidth( bw )
			self.mCtrlLabelLock.setPosition( 0, int( ( bh - 10 ) / 2 ) )
			self.mCtrlLabelScramble.setWidth( bw )
			self.mCtrlLabelScramble.setPosition( 0, int( ( bh - 10 ) / 2 ) )
			self.mCtrlLabelNoSignal.setWidth( bw )
			self.mCtrlLabelNoSignal.setPosition( 0, int( ( bh - 10 ) / 2 ) )
			self.mCtrlLabelNoService.setWidth( bw )
			self.mCtrlLabelNoService.setPosition( 0, int( ( bh - 10 ) / 2 ) )
		"""

		#input ch
		self.mCtrlGroupInput.setPosition( 5, int( ( bh - 10 ) / 2 ) )
		self.mCtrlImageInputBG.setWidth( bw )
		self.mCtrlLabelInputCH.setWidth( bw )
		#self.mCtrlLabelInputCH.setPosition( 0, int( ( bh - 10 ) / 2 ) )
		self.mCtrlLabelInputName.setWidth( bw )
		self.mCtrlLabelInputName.setPosition( 0, 20 )

		#osd panel
		self.mCtrlGroupOsdStatus.setPosition( 0, h )
		if w > 350 :
			self.mCtrlImageOsdStatus.setWidth( w )
			self.mCtrlGroupList2ndPIP.setPosition( w, 0 )

		self.SetGUIArrow( )


	def SetGUIArrow( self, aInit = False ) :
		#arrow at move, size
		x = self.mPosCurrent[0]
		y = self.mPosCurrent[1]
		w = self.mPosCurrent[2]
		h = self.mPosCurrent[3]
		#LOG_TRACE( '[PIP] guiArrow x[%s] y[%s] w[%s] h[%s] w/2[%s] h/2[%s]'% ( x,y, w, h, w/2, h/2 ) )

		if not aInit and self.mViewMode != CONTEXT_ACTION_SIZE_PIP : 
			return

		self.mCtrlImageArrowLeft.setPosition  ( 0, int( h / 2 ) )
		self.mCtrlImageArrowRight.setPosition ( w, int( h / 2 ) )

		self.mCtrlImageArrowTop.setPosition   ( int( w / 2 ), 0 )
		self.mCtrlImageArrowBottom.setPosition( int( w / 2 ), h )


	def SetAudioXBMC( self, aEnable = False ) :
		xbmc.executebuiltin( 'Audio.Enable(%s)'% aEnable, True )
		return

		loopTime = 0
		limitTime = 5
		while loopTime < limitTime :
			if xbmcgui.getCurrentWindowDialogId( ) != XBMC_WINDOW_DIALOG_BUSY :
				break

			time.sleep( 0.2 )
			loopTime += 0.2


	def SetAudioPIP( self, aForce = False, aEnable = False ) :
		if aForce :
			ret = self.mDataCache.PIP_EnableAudio( aEnable )
			if ret :
				self.mPIP_EnableAudio = aEnable

			self.setProperty( 'EnableAudioPIP', '%s'% self.mPIP_EnableAudio )
			return

		lblMsg = ''
		isAudioBlock = False

		if self.mCurrentChannel and self.mCurrentChannel.mLocked :
			isAudioBlock = True
			lblMsg = MR_LANG( 'The channel is locked' )

		"""
		if not self.mDataCache.GetMediaCenter( ) :
			#check dvb only
			#1. check audio in main
			mute, volume = self.GetAudioStatus( )

			if mute or volume < 1 :
				isAudioBlock = True
				lblMsg = MR_LANG( 'Audio is muted' )
		"""
		if isAudioBlock :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			lblTitle = MR_LANG( 'No Audio' )
			dialog.SetDialogProperty( lblTitle, lblMsg )
			dialog.doModal( )
			return


		isEnable = not self.mPIP_EnableAudio
		if self.mDataCache.GetMediaCenter( ) and E_SUPPORT_MEDIA_PLAY_AV_SWITCH :
			if self.mPIP_EnableAudio :
				self.mDataCache.PIP_EnableAudio( False )

			ret = self.mDataCache.PIP_Stop( )
			if ret :
				self.mDataCache.PIP_SetStatus( False )
				self.SetAudioXBMC( not isEnable )
				ret = self.mDataCache.PIP_Start( self.mFakeChannel.mNumber )
				#LOG_TRACE( '[PIP] PIP_Start ret[%s] ch[%s %s]'% ( ret, self.mFakeChannel.mNumber, self.mFakeChannel.mName ) )
				if ret :
					self.mDataCache.PIP_SetStatus( True )
					ret = self.mDataCache.PIP_EnableAudio( isEnable )
					self.mPIP_EnableAudio = isEnable
					self.mDataCache.LoadVolumeBySetGUI( ) #mute,volume sync

			LOG_TRACE( '[PIP] DVB audioSwitch ret[%s] pipAudio[%s] mediaAudio[%s]'% ( ret, isEnable, not isEnable ) )


		else :
			ret = self.mDataCache.PIP_EnableAudio( isEnable )
			if ret :
				self.mPIP_EnableAudio = isEnable
			LOG_TRACE( '[PIP] DVB audioSwitch ret[%s] pipAudio[%s] mediaAudio[%s]'% ( ret, isEnable, not isEnable ) )

		self.setProperty( 'EnableAudioPIP', '%s'% self.mPIP_EnableAudio )


	def RestartAsyncTune( self, aChannel = None ) :
		self.StopAsyncTune( )
		self.StartAsyncTune( aChannel )


	def StartAsyncTune( self, aChannel = None ) :
		tuneTime = 0.5
		if aChannel :
			tuneTime = 3

		if self.mFakeChannel :
			self.mCurrentChannel = self.mFakeChannel

		self.mAsyncTuneTimer = threading.Timer( tuneTime, self.TuneChannel, [aChannel] )
		self.mAsyncTuneTimer.start( )


	def StopAsyncTune( self ) :
		if self.mAsyncTuneTimer and self.mAsyncTuneTimer.isAlive( ) :
			self.mAsyncTuneTimer.cancel( )
			del self.mAsyncTuneTimer

		self.mAsyncTuneTimer = None


	def TuneChannel( self, aChannel = None ) :
		try :
			if aChannel :
				self.StopAsyncHideInput( )
				self.ResetHideInput( )
				self.mCurrentChannel = aChannel
				self.ChannelTuneToPIP( -1 )

			#update channelList position
			thread = threading.Timer( 0, self.UpdateCurrentPositon, [True, self.mFakeChannel] )
			thread.start( )

			self.mDataCache.PIP_SetStatus( True )
			self.mDataCache.PIP_SetCurrentChannel( self.mFakeChannel )
			self.mIndexAvail = 0
			self.mCurrentChannel = self.mFakeChannel
			ret = self.mDataCache.PIP_Start( self.mFakeChannel.mNumber )
			LOG_TRACE( '[PIP] PIP_Start ret[%s] ch[%s %s]'% ( ret, self.mFakeChannel.mNumber, self.mFakeChannel.mName ) )
			if ret :
				if self.mFakeChannel.mLocked :
					self.SetAudioPIP( True, False )
					xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', E_TAG_TRUE )
					xbmcgui.Window( 10000 ).setProperty( 'iLockPIP', E_TAG_TRUE )

				else :
					xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', E_TAG_FALSE )
					xbmcgui.Window( 10000 ).setProperty( 'iLockPIP', E_TAG_FALSE )
					xbmcgui.Window( 10000 ).setProperty( 'PIPSignal', E_TAG_TRUE )

			else :
				LOG_ERR('Tune failed')
				xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', E_TAG_TRUE )
				xbmcgui.Window( 10000 ).setProperty( 'iLockPIP', E_TAG_FALSE )
				xbmcgui.Window( 10000 ).setProperty( 'PIPSignal', E_TAG_FALSE )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def TuneChannelByExternal( self, aChannel = None, aRetune = False ) :
		if aRetune :
			if self.mDataCache.PIP_GetStatus( ) :
				self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( )
				chNumber = self.Channel_GetCurrentByPIP( )
				aChannel = self.mDataCache.PIP_GetByNumber( chNumber )
				if not aChannel :
					aChannel = self.mDataCache.Channel_GetCurrent( )

			else :
				LOG_TRACE( '[PIP] reject retune, not started PIP_GetStatus false' )
				return

		if not aChannel :
			LOG_TRACE( '[PIP] could not tune by external. None channel' )
			return

		self.mDataCache.PIP_SetStatus( True )
		self.mDataCache.PIP_SetCurrentChannel( aChannel )
		ret = self.mDataCache.PIP_Start( aChannel.mNumber )
		LOG_TRACE( '[PIP] PIP_Start ret[%s] ch[%s %s]'% ( ret, aChannel.mNumber, aChannel.mName ) )
		if ret :
			if aChannel.mLocked :
				xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', E_TAG_TRUE )
				xbmcgui.Window( 10000 ).setProperty( 'iLockPIP', E_TAG_TRUE )

			else :
				xbmcgui.Window( 10000 ).setProperty( 'iLockPIP', E_TAG_FALSE )
				xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', E_TAG_FALSE )
				xbmcgui.Window( 10000 ).setProperty( 'PIPSignal', E_TAG_TRUE )

		else :
			LOG_ERR('Tune failed')
			xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', E_TAG_TRUE )
			xbmcgui.Window( 10000 ).setProperty( 'iLockPIP', E_TAG_FALSE )
			xbmcgui.Window( 10000 ).setProperty( 'PIPSignal', E_TAG_FALSE )


	def RestartAsyncHideInput( self ) :
		self.StopAsyncHideInput( )
		self.StartAsyncHideInput( )


	def StartAsyncHideInput( self ) :
		self.mAsyncInputTimer = threading.Timer( 5, self.ResetHideInput )
		self.mAsyncInputTimer.start( )


	def StopAsyncHideInput( self ) :
		if self.mAsyncInputTimer and self.mAsyncInputTimer.isAlive( ) :
			self.mAsyncInputTimer.cancel( )
			del self.mAsyncInputTimer

		self.mAsyncInputTimer = None


	def ResetHideInput( self ) :
		self.mInputString = ''
		xbmcgui.Window( 10000 ).setProperty( 'InputNumber', E_TAG_FALSE )


