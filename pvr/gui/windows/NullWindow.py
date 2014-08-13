from pvr.gui.WindowImport import *
import sys, inspect, time, threading
import xbmc, xbmcgui
from pvr.XBMCInterface import XBMC_GetWebserver, XBMC_GetUpnpRenderer, XBMC_GetEsallinterfaces
import time


E_NULL_WINDOW_BASE_ID = WinMgr.WIN_ID_NULLWINDOW * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID
E_BUTTON_ID_FAKE      = E_NULL_WINDOW_BASE_ID + 9000
E_LABEL_ID_GUI_RESTART      = E_NULL_WINDOW_BASE_ID + 100
E_NOMAL_BLINKING_TIME = 0.2
E_MAX_BLINKING_COUNT  =  10

E_LINKAGE_ICON_TIMEOUT	= 5

E_NO_TUNE  = False
E_SET_TUNE = True



class NullWindow( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mAsyncTuneTimer		= None
		self.mAsyncShowTimer		= None
		self.mRecordBlinkingTimer	= None
		self.mLinkageServiceTimer	= None
		self.mOnTimeDelay			= 0
		self.mPreviousBlockTime		= 1.0
		self.mRecordBlinkingCount	= E_MAX_BLINKING_COUNT
		self.mOnBlockTimer_GreenKey	= 0
		self.mIsShowDialog			= False
		self.mEventId				= 0
		self.mHbbTVTimer			= None
		self.mHbbTVShowing			= False
		self.mYoutubeTVStarted		= False
		self.mStartedWebserver		= False
		self.mStartedUpnp			= False
		self.mStartedEsall			= False

		if E_SUPPROT_HBBTV == True :
			self.mHBBTVReady = False
			self.mMediaPlayerStarted = False
			self.mForceSetCurrent = True
			self.mStartTimeForTest = time.time( ) + 7200
			LOG_ERR('self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s' %( self.mHBBTVReady, self.mMediaPlayerStarted ) )
			#self.mSubTitleIsShow = False

		self.mEnableBlickingTimer = False


	def onInit( self ) :
		self.mLoopCount = 0
		self.mPreviousBlockTime = 1.0
		self.mEnableBlickingTimer = False
		self.mNewEPGAlarm = time.time()
		self.mNewEPGAlarmEnabled = False
		if GetSetting( 'DISPLAY_EVENT_LIVE' ).lower( ) == 'true'.lower( ) :
			self.mNewEPGAlarmEnabled = True
		self.setProperty( 'ShowClock', GetSetting( 'DISPLAY_CLOCK_NULLWINDOW' ) )
		self.setProperty( 'LiveStream', GetSetting( 'LIVE_STREAM' ) )
		self.setFocusId( E_BUTTON_ID_FAKE )
		self.SetSingleWindowPosition( E_NULL_WINDOW_BASE_ID )
		playingRecord = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW ).GetPlayingRecord( )
		#LOG_TRACE('---------------playingrecord[%s]'% playingRecord )
		try :
			if playingRecord :
				self.SetFrontdisplayMessage( playingRecord.mRecordName )
			else :
				self.mDataCache.Frontdisplay_SetCurrentMessage( )
		except Exception, e :
			LOG_TRACE('Exception[%s]'% e )

		self.mWinId = xbmcgui.getCurrentWindowId( )

		self.SetBlinkingProperty( 'None' )
		self.mRecordBlinkingCount	 = 0 
		self.mIsShowDialog = False

		self.CheckMediaCenter( )
		status = self.mDataCache.Player_GetStatus( )
		if status.mMode == ElisEnum.E_MODE_LIVE :
			self.setProperty( 'PvrPlay', 'False' )

			if self.mDataCache.Get_Player_AVBlank( ) :
				iChannel = self.mDataCache.Channel_GetCurrent( )
				channelList = self.mDataCache.Channel_GetList( )
				iEPG = self.mDataCache.Epgevent_GetPresent( )

				if self.mDataCache.GetStatusByParentLock( ) and ( not self.mDataCache.GetPincodeDialog( ) ) and \
				   channelList and len( channelList ) > 0 and iChannel and iChannel.mLocked or self.mDataCache.GetParentLock( iEPG ) :
					pvr.GlobalEvent.GetInstance( ).CheckParentLock( E_PARENTLOCK_INIT )
					#LOG_TRACE('---------------------------------------parentLock recheck repeat')
		else :
			self.setProperty( 'PvrPlay', 'True' )

		if self.mInitialized == False :
			self.getControl( E_LABEL_ID_GUI_RESTART ).setLabel( '[I]' +  MR_LANG( 'Restarting GUI' )  +  '[/I]' )
			self.mInitialized = True
			self.MboxFirstProcess( )
			self.mDataCache.LoadPIPStatus( )
			return

		iEPG = self.mDataCache.Epgevent_GetPresent( )
		if iEPG and iEPG.mError == 0 :
			self.mEventId = iEPG.mEventId


		LOG_TRACE("HBBTEST------" )
		self.mEventBus.Register( self )
		self.CheckNochannel( )
		#self.LoadNoSignalState( )
		self.CheckSubTitle( )

		self.HbbTV_ShowRedButton()


		"""
		if E_SUPPROT_HBBTV == True :
			LOG_ERR('self.mDataCache.Player_GetStatus( ) = %d'% status.mMode )
			if status.mMode == ElisEnum.E_MODE_LIVE :
				if self.mDataCache.GetLockedState( ) != ElisEnum.E_CC_SUCCESS :
					self.mCommander.AppHBBTV_Ready( 0 )
					self.mHBBTVReady = False
				elif self.mHBBTVReady == False :
					LOG_TRACE('----------HBB Tv Ready')
					self.mCommander.AppHBBTV_Ready( 1 )
					self.mHBBTVReady = True
					LOG_ERR('self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s'%( self.mHBBTVReady, self.mMediaPlayerStarted ) )
				elif self.mForceSetCurrent == True :
					self.mCommander.AppMediaPlayer_Control( 0 )
					self.mCommander.AppHBBTV_Ready( 1 )
					LOG_ERR('self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s'%( self.mHBBTVReady, self.mMediaPlayerStarted ) )
					self.mMediaPlayerStarted = False
					self.ForceSetCurrent( )
				elif self.mForceSetCurrent == False :
					#if self.mMediaPlayerStarted == True :
					LOG_ERR('self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s'%( self.mHBBTVReady, self.mMediaPlayerStarted ) )
					self.mForceSetCurrent = True
		"""
		
		self.DoRelayAction( )
		self.mOnTimeDelay = time.time( )
		self.mOnBlockTimer_GreenKey = time.time( )

		self.UpdateLinkageService( )

		"""
		currentStack = inspect.stack( )
		LOG_TRACE( '+++++getrecursionlimit[%s] currentStack[%s] count[%s] type[%s]'% (sys.getrecursionlimit( ), len(currentStack), currentStack.count, type(currentStack) ) )
		LOG_TRACE( '+++++currentStackInfo[%s]'% (currentStack) )
		for i in range(len(currentStack)) :
			LOG_TRACE( 'currentStack[%s][%s]'% (i,currentStack[i]) )

		startTime= self.mStartTimeForTest
		lastTime = time.time( ) + 7200
		lblStart = time.strftime('%H:%M:%S', time.localtime(startTime) )
		lblLast  = time.strftime('%H:%M:%S', time.localtime(lastTime) )
		lblTest  = '%02d:%s'% ( (lastTime - startTime)/3600, time.strftime('%M:%S', time.gmtime(lastTime - startTime) ) )
		LOG_TRACE( 'startTime[%s] lastTime[%s] TestTime[%s]'% (lblStart, lblLast, lblTest) )
		"""

	def MboxFirstProcess( self ) :
		if GetSetting( 'NEED_SYNC_CHANNEL' ) == 'true' :
			self.OpenBusyDialog( )
			self.mTunerMgr.SyncChannelBySatellite( )
			SetSetting( 'NEED_SYNC_CHANNEL', 'false' )
			self.CloseBusyDialog( )

		thread = threading.Timer( 6, self.XBMCFirstProcess )
		thread.start( )

		unpackPath = self.mDataCache.USB_GetMountPath( )
		if unpackPath :
			self.mDataCache.SetUSBAttached( True )

		if E_V1_1_UPDATE_NOTIFY :
			thread = threading.Timer( 5, self.FirmwareNotify )
			thread.start( )

		if ElisPropertyEnum( 'First Installation', self.mCommander ).GetProp( ) != 0 :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_FIRST_INSTALLATION, WinMgr.WIN_ID_MAINMENU )
			
		else :
			"""
			self.mCommander.AppHBBTV_Ready( 1 )
			self.mHBBTVReady = True
			"""
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetPincodeRequest( True )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )


	def XBMCFirstProcess( self ) :
		if os.path.exists( '/mtmp/XbmcDbBroken' ) :
			databaseName = None
			try :
				inputFile = open( '/mtmp/XbmcDbBroken', 'r' )
				inputline = inputFile.readlines( )
				inputFile.close( )
				if inputline :
					for line in inputline :
						databaseName = line.strip( )
						break
			except Exception, e :
				LOG_ERR( 'Error exception[%s]' % e )
				return

			if databaseName :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( MR_LANG( 'Corrupted Database' ), MR_LANG( 'Do you want to repair database? (%s)' ) % databaseName )
				dialog.doModal( )
				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					userDatabasePath = self.mPlatform.GetUserDataDir( )
					userDatabasePath = userDatabasePath + 'Database/'
					databaseName = userDatabasePath + databaseName + '.db'
					os.system( 'rm %s' % databaseName )
					os.system( 'rm %s' % '/mtmp/XbmcDbBroken' )
					pvr.ElisMgr.GetInstance( ).Shutdown( )
					xbmc.executebuiltin( 'Settings.Save' )
					os.system( 'killall -9 xbmc.bin' )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) and actionId != Action.ACTION_MBOX_RESERVED22   :
			return

		#only for test
		#if actionId == Action.REMOTE_9:
		#	LOG_TRACE("Show Google TV")
		#	#self.mCommander.AppHBBTV_Ready( 1 )
		#	self.mCommander.System_ShowWebPage("http://www.youtube.com/tv", 0 )
		#	return
			
		#if actionId == Action.REMOTE_8:
		#	LOG_TRACE("Close Google TV")
		#	self.mCommander.System_CloseWebPage( )
		#	self.mCommander.AppHBBTV_Ready( 0 )
		#	return	
			
		LOG_ERR( 'ACTION_TEST actionID=%d'% actionId )
		if actionId == Action.ACTION_PREVIOUS_MENU :
			#if self.mHbbTVShowing == True :		
			#	self.HbbTV_HideBrowser()
			#	return
				
			if ElisPropertyEnum( 'Lock Mainmenu', self.mCommander ).GetProp( ) == 0 :
				self.CloseSubTitle( )			
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
				dialog.SetDialogProperty( MR_LANG( 'Enter PIN Code' ), '', 4, True )
	 			dialog.doModal( )
	 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
	 				tempval = dialog.GetString( )
	 				if len( tempval ) != 4 :
	 					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'The PIN code must be 4-digit long' ) )
			 			dialog.doModal( )
			 			self.CheckSubTitle( )
			 			return
					if int( tempval ) == ElisPropertyInt( 'PinCode', self.mCommander ).GetProp( ) :
						self.Close( )
						WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MAINMENU )
					else :
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Sorry, that PIN code does not match' ) )
			 			dialog.doModal( )
			 			self.CheckSubTitle( )			 			
			else :
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MAINMENU )
			
		elif actionId == Action.ACTION_PARENT_DIR :
			#if self.mHbbTVShowing == True :		
			#	self.HbbTV_HideBrowser()
			#	return
		
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_LIVE :

				if self.mDataCache.GetLinkageService(  ) : #hide linkage service icon
					self.StopLinkageServiceTimer()
					#return

				if ( time.time( ) - self.mOnTimeDelay ) < 1.5 :
					LOG_TRACE( '------Block back key time' )
					return

				self.RestartAsyncTimerByBackKey( )

			elif status.mMode == ElisEnum.E_MODE_PVR :
				self.Close( )			
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )

			else :
				labelMode = GetStatusModeLabel( status.mMode )
				thread = threading.Timer( 0.1, AsyncShowStatus, [labelMode] )
				thread.start( )

		elif actionId == Action.ACTION_SHOW_INFO :
			if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
				self.DialogPopupOK( actionId )

			else :
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EPG_WINDOW )

		elif actionId == Action.ACTION_CONTEXT_MENU :
			status = self.mDataCache.Player_GetStatus( )
			self.Close( )
			if status.mMode == ElisEnum.E_MODE_LIVE :
				#WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( False )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )

			else :
				#WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).SetAutomaticHide( False )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE, WinMgr.WIN_ID_NULLWINDOW )			

		elif actionId == Action.ACTION_PAGE_DOWN :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_PVR :
				self.Close( )
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = actionId
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).SetAutomaticHide( True )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )
				return

			prevChannel = None
			prevChannel = self.mDataCache.Channel_GetPrev( self.mDataCache.Channel_GetCurrent( ) ) #self.mCommander.Channel_GetPrev( )
			if prevChannel :
				self.mDataCache.Channel_SetCurrent( prevChannel.mNumber, prevChannel.mServiceType, None, True )			
				self.mDataCache.SetAVBlankByChannel( prevChannel )
				self.Close( )
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
				#WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetPincodeRequest( True )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )

		elif actionId == Action.ACTION_PAGE_UP :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_PVR :
				self.Close( )
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = actionId
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).SetAutomaticHide( True )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )
				return

			nextChannel = None
			nextChannel = self.mDataCache.Channel_GetNext( self.mDataCache.Channel_GetCurrent( ) )
			if nextChannel :
				self.mDataCache.Channel_SetCurrent( nextChannel.mNumber, nextChannel.mServiceType, None, True )
				self.mDataCache.SetAVBlankByChannel( nextChannel )
				self.Close( )
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
				#WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetPincodeRequest( True )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )

		#HBBTV
		elif actionId == Action.ACTION_COLOR_RED :
			LOG_TRACE( 'RED KEY' )
			if os.path.exists( '/mtmp/crossepg_running' ) :
				mHead = MR_LANG( 'While downloading EPG data' )
				mLine = MR_LANG( 'Not allowed operation' )
				xbmc.executebuiltin( 'Notification(%s, %s, 5000, DefaultIconInfo.png)' % ( mHead, mLine ) )
				return
			self.HbbTV_ShowBrowser( )


		elif actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 or \
			actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :
			
			aKey = actionId - (Action.ACTION_JUMP_SMS2 - 2)
			if actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 :
				aKey = int( actionId ) - Action.REMOTE_0

			if aKey == 0 :
				return -1

			if self.mIsShowDialog == False :
				status = self.mDataCache.Player_GetStatus( )
				if status.mMode == ElisEnum.E_MODE_LIVE :
					thread = threading.Timer( 0.1, self.AsyncTuneChannelByInput, ( aKey, False ) )
					thread.start( )

				else :
					if status.mSpeed != 100 :
						self.mDataCache.Player_Resume( )

					thread = threading.Timer( 0.1, self.AsyncTimeshiftJumpByInput, [ aKey ] )
					thread.start( )

		elif actionId == Action.ACTION_STOP :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_LIVE:
				self.CloseSubTitle( )			
				self.ShowRecordingStopDialog( )
				self.CheckSubTitle( )

			else :
				self.mDataCache.Player_Stop( )
				if self.mDataCache.Teletext_IsShowing( ) :
					LOG_TRACE( '----------Teletext_IsShowing - No window change' )
					return

				if status.mMode == ElisEnum.E_MODE_PVR :
					self.Close( )
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )

				#buyer issue, hide
				elif status.mMode == ElisEnum.E_MODE_TIMESHIFT :
					self.mDataCache.Frontdisplay_PlayPause( False )
					labelMode = MR_LANG( 'LIVE' )
					thread = threading.Timer( 0.1, AsyncShowStatus, [labelMode] )
					thread.start( )
				#	self.Close( )
				#	WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
				#	WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE, WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_MBOX_XBMC or actionId == Action.ACTION_MBOX_RESERVED22 :
			if actionId == Action.ACTION_MBOX_XBMC :
				if self.GetBlinkingProperty( ) != 'None' :
					LOG_TRACE( '---------------- Try recording' )
					return

				isDownload = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_SYSTEM_UPDATE ).GetStatusFromFirmware( )
				if isDownload :
					self.DialogPopupOK( actionId + 1000 )
					return

			status = self.mDataCache.Player_GetStatus( )
			if status.mMode != ElisEnum.E_MODE_LIVE :
				if actionId == Action.ACTION_MBOX_XBMC :			
					if status.mMode == ElisEnum.E_MODE_PVR :
						self.DialogPopupOK( actionId )
						return

				self.mDataCache.Player_Stop( )

			if actionId == Action.ACTION_MBOX_XBMC :
				if not CheckHdd( True ) :
					self.CloseSubTitle( )
					msg = MR_LANG( 'Installing and executing XBMC add-ons%s may not work properly without an internal HDD' )% NEW_LINE
					if self.mPlatform.GetProduct( ) == PRODUCT_OSCAR :
						msg = MR_LANG( 'Installing and executing XBMC add-ons%s may not work properly without an external storage' )% NEW_LINE
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Attention' ), msg )
					dialog.doModal( )
					self.CheckSubTitle( )

			if actionId == Action.ACTION_MBOX_XBMC :
				self.Close( )
				self.SetMediaCenter( )
			else :
				self.SetMediaCenter( True )
			LOG_ERR('self.mWinId = %s xbmcgui.getCurrentWindowId( ) = %s, self.mMediaPlayerStarted = %s' % (self.mWinId, xbmcgui.getCurrentWindowId( ),self.mMediaPlayerStarted ) )
			if self.mWinId == xbmcgui.getCurrentWindowId( ) and self.mMediaPlayerStarted == False:
				xbmc.executebuiltin( 'ActivateWindow(Home)' )


		elif actionId == Action.ACTION_MBOX_TVRADIO :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.mDataCache.ToggleTVRadio( )
				if ret :
					self.Close( )
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )
				else :
					self.DialogPopupOK( actionId )

		elif actionId == Action.ACTION_MBOX_RECORD :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_PVR :
				self.DialogPopupOK( actionId )

			else :
				if self.mDataCache.GetLockedState( ) != ElisEnum.E_CC_SUCCESS :
				#	ToDO : not support m/w, will be 1.2
				#	self.DialogPopupOK( ElisEnum.E_CC_FAILED_NO_SIGNAL )
					return

				if status.mMode == ElisEnum.E_MODE_TIMESHIFT :
					self.mDataCache.Player_Stop( )

				self.CloseSubTitle( )
				isAvail, isConfiguration = self.HasDefaultRecordPath( )
				self.CheckSubTitle( )
				if isAvail != E_DEFAULT_RECORD_PATH_RESERVED :
					if isConfiguration :
						self.Close( )
						self.SetMoveConfigureToAddVolume( )
					return

				if RECORD_WIDTHOUT_ASKING == True :
					if self.GetBlinkingProperty( ) != 'None' :
						self.CheckSubTitle( )
						return
					self.StartRecordingWithoutAsking( )				
				else :
					self.ShowRecordingStartDialog( )
				self.CheckSubTitle( )

		elif actionId == Action.ACTION_PAUSE or actionId == Action.ACTION_PLAYER_PLAY or \
			actionId == Action.ACTION_MOVE_LEFT or actionId == Action.ACTION_MOVE_RIGHT :
			if actionId == Action.ACTION_MOVE_RIGHT :
				status = self.mDataCache.Player_GetStatus( )
				if status.mMode == ElisEnum.E_MODE_LIVE :
					self.Close( )
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_SIMPLE_CHANNEL_LIST )
					return

			self.CloseSubTitle( )
			playingRecord = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW ).GetPlayingRecord( )
			if not playingRecord and ( not HasAvailableRecordingHDD( False ) ) :
				self.CheckSubTitle( )
				return
			self.CheckSubTitle( )

			status = self.mDataCache.Player_GetStatus( )
			if status.mMode != ElisEnum.E_MODE_PVR :
				if self.mDataCache.GetLockedState( ) == ElisEnum.E_CC_FAILED_NO_SIGNAL or \
			       self.mDataCache.GetLockedState( ) == ElisEnum.E_CC_FAILED_PROGRAM_NOT_FOUND :
					return -1

			if actionId == Action.ACTION_MOVE_RIGHT and status.mMode == ElisEnum.E_MODE_LIVE :
				return -1

			if ( actionId == Action.ACTION_PLAYER_PLAY or actionId == Action.ACTION_PAUSE ) and \
			   self.mDataCache.Get_Player_AVBlank( ) and status.mMode == ElisEnum.E_MODE_LIVE :
				return -1

			if not self.CheckDMXInfo( ) and status.mMode == ElisEnum.E_MODE_LIVE :
				return -1

			self.Close( )
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = actionId
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).SetAutomaticHide( True )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )

		elif actionId == Action.ACTION_MBOX_REWIND :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_TIMESHIFT or status.mMode == ElisEnum.E_MODE_PVR :
				self.Close( )
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = actionId
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).SetAutomaticHide( True )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )

		elif actionId == Action.ACTION_MBOX_FF :
			status = self.mDataCache.Player_GetStatus( )		
			if status.mMode == ElisEnum.E_MODE_TIMESHIFT or status.mMode == ElisEnum.E_MODE_PVR :
				self.Close( )			
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = actionId
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).SetAutomaticHide( True )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )

		elif actionId == Action.ACTION_MBOX_ARCHIVE :
			self.CloseSubTitle( )
			if not HasAvailableRecordingHDD( ) :
				self.CheckSubTitle( )
				return
			self.CheckSubTitle( )

			self.Close( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_MBOX_TEXT :
			if self.mDataCache.GetLockedState( ) != ElisEnum.E_CC_SUCCESS :
				LOG_TRACE( '---------Status Signal[%s]'% self.mDataCache.GetLockedState( ) )
				return

			if not self.mDataCache.Teletext_Show( ) :
				self.DialogPopupOK( actionId )

		elif actionId == Action.ACTION_MBOX_SUBTITLE :
			if self.mDataCache.GetLockedState( ) != ElisEnum.E_CC_SUCCESS :
				LOG_TRACE( '---------Status Signal[%s]'% self.mDataCache.GetLockedState( ) )
				return

			if ShowSubtitle( ) == -2 :
				self.DialogPopupOK( actionId )

		elif actionId == Action.ACTION_MBOX_NUMLOCK :
			LOG_TRACE( 'Numlock is not supported' )
			pass

		elif actionId == Action.ACTION_COLOR_GREEN :
			if abs( time.time( ) - self.mOnBlockTimer_GreenKey ) <= 1 :
				LOG_TRACE( 'Green key block time diff=%s' %(time.time( ) - self.mOnBlockTimer_GreenKey) )
				return

			self.mOnBlockTimer_GreenKey = time.time( )
			self.DialogPopupOK( actionId )

		elif actionId == Action.ACTION_COLOR_YELLOW :
			self.DialogPopupOK( actionId )

		elif actionId == Action.ACTION_COLOR_BLUE :
			self.DialogPopupOK( actionId )

		elif actionId == Action.ACTION_MOVE_UP :
			pass

		elif actionId == Action.ACTION_MOVE_DOWN :
			pass

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		else :
			if actionId == Action.ACTION_MUTE or actionId == Action.ACTION_VOLUME_UP or actionId == Action.ACTION_VOLUME_DOWN :
				pass
			else :
				self.NotAvailAction( )
				LOG_TRACE( 'Unknown key[%s]'% actionId )


	def onClick( self, aControlId ) :
		self.Close( )
		status = self.mDataCache.Player_GetStatus( )
		if status.mMode == ElisEnum.E_MODE_PVR :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )
		else :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CHANNEL_LIST_WINDOW, WinMgr.WIN_ID_NULLWINDOW )


	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			#LOG_TRACE( '---------CHECK onEVENT winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId( )) )
			if aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
				if aEvent.mType == ElisEnum.E_EOF_END :
					LOG_TRACE( '---------CHECK onEVENT[%s] stop'% aEvent.getName( ) )
					xbmc.executebuiltin('xbmc.Action(stop)')

			elif aEvent.getName( ) == ElisEventChannelChangeResult.getName( ) :
				pass
				"""
				ch = self.mDataCache.Channel_GetCurrent( )
				if ch.mLocked :
					LOG_TRACE( 'LAEL98 CHECK PINCODE' )				
					CheckPincode( )
				"""

			if aEvent.getName( ) == ElisEventCurrentEITReceived.getName( ) :
				if self.mNewEPGAlarmEnabled == True :
					iEPG = self.mDataCache.Epgevent_GetPresent( )
					if iEPG == None or iEPG.mError != 0 :
						return -1
					if iEPG.mEventId != self.mEventId :
						status = self.mDataCache.Player_GetStatus( )
						if status.mMode == ElisEnum.E_MODE_LIVE :
								
							iChannel = self.mDataCache.Channel_GetCurrent( )
							if iChannel.mSid == iEPG.mSid and iChannel.mTsid == iEPG.mTsid  and iChannel.mOnid == iEPG.mOnid  :
								self.mEventId = iEPG.mEventId 
								if time.time() - self.mNewEPGAlarm  < 5:#5sec
									LOG_ERR( 'Ignore event change' )
								else :
									xbmc.executebuiltin( 'xbmc.Action(contextmenu)' )
								self.mNewEPGAlarm  = time.time()

			elif aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or \
				 aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :

				if aEvent.getName( ) == ElisEventRecordingStarted.getName( ) :
					self.mRecordBlinkingCount = 0
					self.StopBlinkingIconTimer( )
					self.SetBlinkingProperty( 'None' )

				self.mDataCache.SetChannelReloadStatus( True )

				#buyer issue, hide info
				#xbmc.executebuiltin( 'xbmc.Action(contextmenu)' )

			#elif aEvent.getName( ) == ElisEventChannelChangedByRecord.getName( ) :
			#	xbmc.executebuiltin( 'xbmc.Action(contextmenu)' )

			"""
			elif E_SUPPROT_HBBTV == True :
				LOG_TRACE("HBBTEST 11111111111111111 %s" % aEvent.getName( ) )
				if aEvent.getName( ) == ElisEventExternalMediaPlayerStart.getName( ) :
					self.HbbTV_MediaPlayerStart( aEvent.mUrl )

				elif aEvent.getName( ) == ElisEventExternalMediaPlayerSetSpeed.getName( ) :
					#ToDO
					self.HbbTV_MediaPlayerSetSpeed( 0 )				
			
				elif aEvent.getName( ) == ElisEventExternalMediaPlayerSeekStream.getName( ) :
					#ToDO
					self.HbbTV_MediaPlayerSeek( 0 )
			
				elif aEvent.getName( ) == ElisEventExternalMediaPlayerStopPlay.getName( ) :
					self.HbbTV_MediaPlayerStop(  )
					
				elif aEvent.getName() == ElisEventHBBTVReady.getName() :
					LOG_TRACE( 'HbbTV TEST' )
					#HBBTV			
					#This event must be received from global event.
					if aEvent.mReady == 1 :
						LOG_TRACE("Now new AIT is ready, HBBTV Browser ready")
						self.mDataCache.SetHbbTVEnable( True )
						self.HbbTV_ShowRedButton( )

					else :
						LOG_TRACE( 'HbbTV Disable Event' )
						self.mDataCache.SetHbbTVEnable( False )
						self.HbbTV_HideRedButton( )	
			"""

		else :
			pass
			"""
			LOG_TRACE("HBBTEST 2222222222222222 %s" % aEvent.getName( ) )
			if E_SUPPROT_HBBTV == True :
				if aEvent.getName( ) == ElisEventExternalMediaPlayerStart.getName( ) :
						self.HbbTV_MediaPlayerStart( aEvent.mUrl )

				elif aEvent.getName( ) == ElisEventExternalMediaPlayerSetSpeed.getName( ) :
					#ToDO
					self.HbbTV_MediaPlayerSetSpeed( 0 )				
			
				elif aEvent.getName( ) == ElisEventExternalMediaPlayerSeekStream.getName( ) :
					#ToDO
					self.HbbTV_MediaPlayerSeek( 0 )
			
				elif aEvent.getName( ) == ElisEventExternalMediaPlayerStopPlay.getName( ) :
					self.HbbTV_MediaPlayerStop(  )
				elif aEvent.getName() == ElisEventHBBTVReady.getName() :
					LOG_TRACE( 'HbbTV TEST' )
					#HBBTV			
					#This event must be received from global event.
					if aEvent.mReady == 1 :
						LOG_TRACE("Now new AIT is ready, HBBTV Browser ready")
						self.mDataCache.SetHbbTVEnable( True )
						self.HbbTV_ShowRedButton( )

					else :
						LOG_TRACE( 'HbbTV Disable Event' )
						self.mDataCache.SetHbbTVEnable( False )
						self.HbbTV_HideRedButton( )		
				else:
					pass 
					#LOG_TRACE( 'NullWindow winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId( )) )
			"""

	def StartRecordingWithoutAsking( self ) :
		runningCount = self.mDataCache.Record_GetRunningRecorderCount( )
		#LOG_TRACE( 'runningCount[%s]' %runningCount)

		if not HasAvailableRecordingHDD( ) :
			return

		if not self.CheckDMXInfo( ) :
			return -1

		mTimer = self.mDataCache.GetRunnigTimerByChannel( )
		isOK = False

		if mTimer :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_ERROR and dialog.GetConflictTimer( ) :
				RecordConflict( dialog.GetConflictTimer( ) )

			return

		elif runningCount < E_MAX_RECORD_COUNT :
			copyTimeshift = 0
			otrInfo = self.mDataCache.Timer_GetOTRInfo( )
			localTime = self.mDataCache.Datetime_GetLocalTime( )				

			#check ValidEPG
			hasValidEPG = False
			if otrInfo.mHasEPG :
				if localTime >= otrInfo.mEventStartTime  and localTime < otrInfo.mEventEndTime :
					hasValidEPG = True

			if hasValidEPG == False :
				otrInfo.mHasEPG = False
				prop = ElisPropertyEnum( 'Default Rec Duration', self.mCommander )
				otrInfo.mExpectedRecordDuration = prop.GetProp( )
				otrInfo.mEventStartTime = localTime
				otrInfo.mEventEndTime = localTime +	otrInfo.mExpectedRecordDuration
				otrInfo.mEventName = self.mDataCache.Channel_GetCurrent( ).mName

			
			if otrInfo.mTimeshiftAvailable :
				timeshiftRecordSec = int( otrInfo.mTimeshiftRecordMs/1000 )
				LOG_TRACE( 'mTimeshiftRecordMs=%dMs : %dSec' %(otrInfo.mTimeshiftRecordMs, timeshiftRecordSec ) )
			
				if otrInfo.mHasEPG == True :			
				
					copyTimeshift  = localTime - otrInfo.mEventStartTime
					LOG_TRACE( 'copyTimeshift #3=%d' %copyTimeshift )
					if copyTimeshift > timeshiftRecordSec :
						copyTimeshift = timeshiftRecordSec
					LOG_TRACE( 'copyTimeshift #4=%d' %copyTimeshift )
				else :
					self.ShowRecordingStartDialog( )
					return

			LOG_TRACE( 'copyTimeshift=%d' %copyTimeshift )

			if copyTimeshift <  0 or copyTimeshift > 12*3600 : #12hour * 60min * 60sec
				copyTimeshift = 0

			#expectedDuration =  self.mEndTime - self.mStartTime - copyTimeshift
			expectedDuration = otrInfo.mEventEndTime - localTime - 5 # 5sec margin

			LOG_TRACE( 'expectedDuration=%d' %expectedDuration )

			if expectedDuration < 0:
				LOG_ERR( 'Error : Already Passed' )
				expectedDuration = 0

			ret = self.mDataCache.Timer_AddOTRTimer( False, expectedDuration, copyTimeshift, otrInfo.mEventName, True, 0, 0,  0, 0 )

			#if ret[0].mParam == -1 or ret[0].mError == -1 :
			LOG_ERR( 'StartDialog ret=%s ' %ret )
			if ret and ( ret[0].mParam == -1 or ret[0].mError == -1 ) :	
				LOG_ERR( 'StartDialog ' )
				#RecordConflict( ret )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
				dialog.doModal( )

				if dialog.IsOK( ) == E_DIALOG_STATE_ERROR and dialog.GetConflictTimer( ) :
					RecordConflict( dialog.GetConflictTimer( ) )

			else :
				isOK = True



		else:
			msg = MR_LANG( 'Maximum number of recordings reached' )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), msg )
			dialog.doModal( )

		if isOK :
			self.SetBlinkingProperty( 'True' )
			self.mEnableBlickingTimer = True
			self.mRecordBlinkingCount = E_MAX_BLINKING_COUNT			
			self.StartBlinkingIconTimer( )
			
			self.mDataCache.SetChannelReloadStatus( True )


	def RestartBlinkingIconTimer( self, aTimeout=E_NOMAL_BLINKING_TIME ) :
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Restart' )
		self.StopBlinkingIconTimer( )
		self.StartBlinkingIconTimer( aTimeout )


	def StartBlinkingIconTimer( self, aTimeout=E_NOMAL_BLINKING_TIME ) :
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Start' )	
		self.mRecordBlinkingTimer  = threading.Timer( aTimeout, self.AsyncBlinkingIcon )
		self.mRecordBlinkingTimer.start( )
	

	def StopBlinkingIconTimer( self ) :
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Stop' )	
		if self.mRecordBlinkingTimer and self.mRecordBlinkingTimer.isAlive( ) :
			self.mRecordBlinkingTimer.cancel( )
			del self.mRecordBlinkingTimer
			
		self.mRecordBlinkingTimer = None


	def AsyncBlinkingIcon( self ) :	
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Async' )	
		if self.mRecordBlinkingTimer == None or self.mEnableBlickingTimer == False:
			self.SetBlinkingProperty( 'None' )		
			LOG_WARN( 'Blinking Icon update timer expired' )
			return

		if self.mRecordBlinkingCount  <=  0 :
			LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Blinking count is zero' )
			self.SetBlinkingProperty( 'None' )			
			return

		if self.GetBlinkingProperty( ) == 'True' :
			self.SetBlinkingProperty( 'False' )
		else :
			self.SetBlinkingProperty( 'True' )

		self.mRecordBlinkingCount = self.mRecordBlinkingCount  -1

		self.RestartBlinkingIconTimer( )


	def ShowRecordingStartDialog( self ) :
		runningCount = self.mDataCache.Record_GetRunningRecorderCount( )
		#LOG_TRACE( 'runningCount[%s]' %runningCount)
		if not HasAvailableRecordingHDD( ) :
			return

		if not self.CheckDMXInfo( ) :
			return -1

		mTimer = self.mDataCache.GetRunnigTimerByChannel( )

		isOK = False
		if runningCount < E_MAX_RECORD_COUNT or mTimer :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
			dialog.doModal( )

			isOK = dialog.IsOK( )
			if isOK == E_DIALOG_STATE_YES :
				isOK = True

			if dialog.IsOK( ) == E_DIALOG_STATE_ERROR and dialog.GetConflictTimer( ) :
				RecordConflict( dialog.GetConflictTimer( ) )

		else:
			msg = MR_LANG( 'Maximum number of recordings reached' )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), msg )
			dialog.doModal( )

		if isOK :
			self.mDataCache.SetChannelReloadStatus( True )


	def ShowRecordingStopDialog( self ) :
		runningCount = self.mDataCache.Record_GetRunningRecorderCount( )

		isOK = False
		if runningCount > 0 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_STOP_RECORD )
			dialog.doModal( )

			isOK = dialog.IsOK( )
			if isOK == E_DIALOG_STATE_YES :
				isOK = True

		if isOK :
			self.mDataCache.SetChannelReloadStatus( True )


	def Close( self ) :
		self.mEnableBlickingTimer = False	
		self.mEventBus.Deregister( self )
		self.StopAsyncTimerByBackKey( )
		self.StopAsyncTuneByHistory( )
		self.CloseSubTitle( )

		self.HbbTV_HideRedButton( )

		self.StopBlinkingIconTimer( )
		self.SetBlinkingProperty( 'None' )

		self.StopLinkageServiceTimer( )

		"""
		if E_SUPPROT_HBBTV == True :
			LOG_ERR('self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s'% ( self.mHBBTVReady, self.mMediaPlayerStarted ) )
			if self.mHBBTVReady == True :
				if self.mMediaPlayerStarted == True :
					xbmc.executebuiltin( 'XBMC.PlayerControl(Stop)', True )
					self.mCommander.AppMediaPlayer_Control( 0 )
					self.mMediaPlayerStarted = False;
					self.ForceSetCurrent( )
				LOG_TRACE( '----------HBB Tv Not Ready' )
				self.mCommander.AppHBBTV_Ready( 0 )
				self.mHBBTVReady = False 
				LOG_ERR( 'self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s'% ( self.mHBBTVReady, self.mMediaPlayerStarted ) )
		"""

	def ForceSetCurrent( self ) :
		pass
		#current channel re-zapping
		#iChannel = self.mDataCache.Channel_GetCurrent( )
		#if iChannel :
			#self.mDataCache.Channel_InvalidateCurrent( )
			#self.mDataCache.Channel_SetCurrentSync( iChannel.mNumber, iChannel.mServiceType )
			#print 're-zapping ch[%s] type[%s]'% (iChannel.mNumber, iChannel.mServiceType )


	def CheckNochannel( self ) :
		channel = self.mDataCache.Channel_GetList( )
		if not channel or len( channel ) < 1 :
			self.mDataCache.SetLockedState( ElisEnum.E_CC_FAILED_NO_SIGNAL )


	def CloseSubTitle( self ) :
		if self.mDataCache.Subtitle_IsShowing( ) :
			self.mDataCache.Subtitle_Hide( )


	def CheckSubTitle( self ) :
		if self.mDataCache.GetLockedState( ) != ElisEnum.E_CC_SUCCESS :
			return

		status = self.mDataCache.Player_GetStatus( )
		if status :
			if status.mMode == ElisEnum.E_MODE_LIVE :
				self.mDataCache.Subtitle_SetBySpeed( )
			else :
				self.mDataCache.Subtitle_SetBySpeed( status.mSpeed )


	def DialogPopupOK( self, aAction ) :
		if self.mIsShowDialog == False :
			thread = threading.Timer( 0.1, self.ShowDialog, [aAction] )
			thread.start( )
		else :
			LOG_TRACE( 'Already a dialog opened' )


	def ShowDialog( self, aAction ) :
		self.mIsShowDialog = True

		head= MR_LANG( 'Attention' )
		msg = ''
		dialogId = DiaMgr.DIALOG_ID_POPUP_OK
		extendData = None
		if aAction == Action.ACTION_SHOW_INFO :
			msg = MR_LANG( 'Try again after stopping playback' )

			iPlayingRecord = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW ).GetPlayingRecord( )
			if iPlayingRecord :
				iCurrentEPG = self.mDataCache.RecordItem_GetEventInfo( iPlayingRecord.mRecordKey )
				if iCurrentEPG == None or iCurrentEPG.mError != 0 :
					iCurrentEPG = ElisIEPGEvent()
					iCurrentEPG.mEventName = iPlayingRecord.mRecordName
					iCurrentEPG.mEventDescription = ''
					iCurrentEPG.mStartTime = iPlayingRecord.mStartTime - self.mDataCache.Datetime_GetLocalOffset( )
					iCurrentEPG.mDuration = iPlayingRecord.mDuration

				dialogId = DiaMgr.DIALOG_ID_EXTEND_EPG
				extendData = iCurrentEPG

			else :
				head = MR_LANG( 'Error' )
				msg = MR_LANG( 'No EPG' )

		elif aAction == Action.ACTION_MBOX_TEXT :
			head = MR_LANG( 'No teletext' )
			msg = MR_LANG( 'No teletext available' )

		elif aAction == Action.ACTION_MBOX_SUBTITLE :
			head = MR_LANG( 'No subtitle' )
			msg = MR_LANG( 'No subtitle available' )

		elif aAction == Action.ACTION_MBOX_XBMC :
			msg = MR_LANG( 'Try again after stopping playback' )

		elif aAction == ( Action.ACTION_MBOX_XBMC + 1000 ) :
			msg = MR_LANG( 'Try again after completing firmware update' )

		elif aAction == Action.ACTION_MBOX_RECORD :
			msg = MR_LANG( 'Try again after stopping playback' )

		elif aAction == ElisEnum.E_CC_FAILED_NO_SIGNAL :
			status = self.mDataCache.GetLockedState( )
			if status != ElisEnum.E_CC_SUCCESS :
				msg = MR_LANG( 'No Signal' )
				if status == ElisEnum.E_CC_FAILED_SCRAMBLED_CHANNEL :
					msg = MR_LANG( 'Scrambled' )
				elif status == ElisEnum.E_CC_FAILED_PROGRAM_NOT_FOUND :
					msg = MR_LANG( 'No Service' )
				

		elif aAction == Action.ACTION_MBOX_TVRADIO :
			head = MR_LANG( 'Error' )
			msg = MR_LANG( 'No channels available for the selected mode' )

		elif aAction == Action.ACTION_COLOR_YELLOW :
			self.CloseSubTitle( )
			DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SET_AUDIOVIDEO ).doModal( )
			self.CheckSubTitle( )
			self.mIsShowDialog = False
			return

		elif aAction == Action.ACTION_COLOR_BLUE :
			self.mIsShowDialog = False
			self.CloseSubTitle( )
			pipDialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP )
			pipDialog.doModal( )
			self.EventReceivedDialog( pipDialog )
			self.CheckSubTitle( )
			return

		elif aAction == Action.ACTION_COLOR_GREEN :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_PVR :
				playingRecord = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW ).GetPlayingRecord( )
				if playingRecord == None or playingRecord.mError != 0 :
					self.mIsShowDialog = False
					return

				bookmarkList = self.mDataCache.Player_GetBookmarkList( playingRecord.mRecordKey )
				if bookmarkList and len( bookmarkList ) >= E_DEFAULT_BOOKMARK_LIMIT :
					head = MR_LANG( 'Error' )
					msg = MR_LANG( 'Maximum number of bookmarks reached' )
				else :

					status = self.mDataCache.Player_GetStatus( )
					if status.mSpeed != 100 :
						self.mDataCache.Player_Resume( )

					self.mDataCache.Player_CreateBookmark( )
					self.mIsShowDialog = False
					return
			else : #Show Linkage Service
				if self.mDataCache.GetLinkageService( ) :
					self.CloseSubTitle( )				
					self.ShowLinkageChannels( )
					self.CheckSubTitle( )
					self.mIsShowDialog = False
				else :
					self.mIsShowDialog = False
				return

		elif aAction == Action.ACTION_MOVE_UP or aAction == Action.ACTION_MOVE_DOWN :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode != ElisEnum.E_MODE_PVR :
				self.CloseSubTitle( )
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_MAINMENU ).ShowGroupByZappingMode( )
				self.CheckSubTitle( )

			self.mIsShowDialog = False
			return


		self.CloseSubTitle( )
		dialog = DiaMgr.GetInstance( ).GetDialog( dialogId )
		if dialogId == DiaMgr.DIALOG_ID_EXTEND_EPG and extendData :
			dialog.SetEPG( extendData )
		else :
			dialog.SetDialogProperty( head, msg )
		dialog.doModal( )
		self.CheckSubTitle( )

		self.EventReceivedDialog( dialog )

		self.mIsShowDialog = False


	def SetBlinkingProperty( self, aValue ) :
		rootWinow = xbmcgui.Window( 10000 )
		rootWinow.setProperty( 'RecordBlinkingIcon', aValue )


	def GetBlinkingProperty( self ) :
		rootWinow = xbmcgui.Window( 10000 )
		return rootWinow.getProperty( 'RecordBlinkingIcon' )


	def RestartAsyncTimerByBackKey( self ) :
		"""
		self.mLoopCount += 1
		if self.mLoopCount > 2 :
			self.RestartAsyncTuneByHistory( )
		else :
			self.StopAsyncTimerByBackKey( )
			self.StartAsyncTimerByBackKey( )
		"""

		if self.mLoopCount < 1 :
			self.StopAsyncTimerByBackKey( )
			self.StartAsyncTimerByBackKey( )

		self.mLoopCount += 1


	def StopAsyncTimerByBackKey( self ) :
		if self.mAsyncTuneTimer	and self.mAsyncTuneTimer.isAlive( ) :
			self.mAsyncTuneTimer.cancel( )
			del self.mAsyncTuneTimer

		self.mAsyncTuneTimer  = None


	def StartAsyncTimerByBackKey( self ) :
		if self.mIsShowDialog :
			self.mLoopCount = 0
			#LOG_TRACE(' ---------- already back key showing -----Unvisible previous-------------' )
			return

		self.mAsyncTuneTimer = threading.Timer( 0.05, self.AsyncTuneByPrevious )
		self.mAsyncTuneTimer.start( )


	def AsyncTuneByPrevious( self ) :
		oldChannel = self.mDataCache.Channel_GetOldChannel( )
		if not oldChannel or oldChannel.mError != 0 :
			oldChannel = self.mDataCache.Channel_GetCurrent( )

		channelList = self.mDataCache.Channel_GetList( )
		if not channelList or len( channelList ) < 1 or ( not oldChannel ) or \
		   ( oldChannel and self.mDataCache.Channel_GetCurr( oldChannel.mNumber ) == None ) :
			self.mLoopCount = 0
			self.NotAvailAction( )
			LOG_TRACE( '----------------- Cannot setCurrent if there is no previous channel' )
			return

		iChNumber = oldChannel.mNumber
		if E_V1_2_APPLY_PRESENTATION_NUMBER :
			iChNumber = self.mDataCache.CheckPresentationNumber( oldChannel )
		self.AsyncTuneChannelByInput( iChNumber, True )


	def RestartAsyncTuneByHistory( self ) :
		self.StopAsyncTuneByHistory( )
		self.StartAsyncTuneByHistory( )


	def StartAsyncTuneByHistory( self ) :
		if self.mIsShowDialog :
			self.mLoopCount = 0
			#LOG_TRACE(' ---------- already back key showing --Unvisible History----------------' )
			return

		self.mAsyncTuneTimer = threading.Timer( 0.05, self.AsyncTuneChannelByHistory )
		self.mAsyncTuneTimer.start( )


	def StopAsyncTuneByHistory( self ) :
		if self.mAsyncTuneTimer	and self.mAsyncTuneTimer.isAlive( ) :
			self.mAsyncTuneTimer.cancel( )
			del self.mAsyncTuneTimer

		self.mAsyncTuneTimer  = None


	def AsyncTuneChannelByHistory( self ) :
		#LOG_TRACE('--------------Loop Count backKey[%s]'% self.mLoopCount )
		channelList = self.mDataCache.Channel_GetOldChannelList( )
		#if not channelList or len( channelList ) < 1 :
		#	channelList = []
		#	self.mLoopCount = 0
		#	return

		self.mIsShowDialog = True
		self.CloseSubTitle( )
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SELECT )
		dialog.SetPreviousBlocking( True )
		dialog.SetDefaultProperty( MR_LANG( 'Recent channels' ), channelList, E_MODE_CHANNEL_LIST, E_SELECT_ONLY  )
		dialog.doModal( )
		isSelect = dialog.GetSelectedList( )
		self.CheckSubTitle( )

		self.mLoopCount = 0
		self.mIsShowDialog = False
		#self.mPreviousBlockTime = 0.2
		#self.mOnTimeDelay = time.time( )
		#listNumber = []
		#for ch in channelList :
		#	listNumber.append( '%04d %s'% ( ch.mNumber, ch.mName ) )
		#LOG_TRACE( '-------previous idx[%s] list[%s]'% ( isSelect, listNumber ) )

		if isSelect < 0 :
			return

		oldChannel = channelList[isSelect]
		self.mDataCache.Channel_SetCurrentByOld( oldChannel )


	def AsyncTuneChannelByInput( self, aNumber, aBackKeyCheck ) :
		self.mIsShowDialog = True

		self.CloseSubTitle( )
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_JUMP )
		dialog.SetBackKeyCheck( aBackKeyCheck )
		dialog.SetDialogProperty( str( aNumber ) )
		dialog.doModal( )
		self.CheckSubTitle( )

		self.mIsShowDialog = False

		isOK = dialog.IsOK( )
		backKeyInput = dialog.GetPreviousKey( )
		if backKeyInput > 2 :
			self.AsyncTuneChannelByHistory( )

		else :
			if isOK == E_DIALOG_STATE_YES :
				inputNumber = dialog.GetChannelLast( )
				iCurrentCh = self.mDataCache.Channel_GetCurrent( )
				if iCurrentCh.mNumber != int(inputNumber) :
					jumpChannel = self.mDataCache.Channel_GetCurr( int(inputNumber) )
					if jumpChannel != None and jumpChannel.mError == 0 :
						self.mDataCache.SetAVBlankByChannel( jumpChannel )
						self.mDataCache.Channel_SetCurrent( jumpChannel.mNumber, jumpChannel.mServiceType, None, True )

		self.mLoopCount = 0
		#self.mPreviousBlockTime = 0.2
		#self.mOnTimeDelay = time.time( )


	def AsyncTimeshiftJumpByInput( self, aKey ) :
		self.CloseSubTitle( )			
		self.mIsShowDialog = True
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_TIMESHIFT_JUMP )
		dialog.SetDialogProperty( str( aKey ) )
		dialog.doModal( )
		self.mIsShowDialog = False
		self.CheckSubTitle( )

		isOK = dialog.IsOK( )
		if isOK == E_DIALOG_STATE_YES :
			move = dialog.GetMoveToJump( )
			if move :
				ret = self.mDataCache.Player_JumpToIFrame( int( move ) )


	def FirmwareNotify( self ) :
		isNotify = False
		try :
			fwNotify = int( GetSetting( 'UPDATE_NOTIFY' ) )
			LOG_TRACE( '----fwNotify[%s]'% fwNotify )
			if fwNotify == 0 :
				LOG_TRACE( '----fwNotify None' )
			elif fwNotify == 1 :
				fwNotifyCount = int( GetSetting( 'UPDATE_NOTIFY_COUNT' ) )
				LOG_TRACE( '----fwNotifyCount[%s]'% fwNotifyCount )
				if fwNotifyCount < 5 :
					isNotify = True
					fwNotifyCount += 1
					SetSetting( 'UPDATE_NOTIFY_COUNT', '%d'% fwNotifyCount )
			elif fwNotify == 2 :
				isNotify = True

		except Exception, e :
			LOG_ERR( 'Exception[%s]'% e )
			SetSetting( 'UPDATE_NOTIFY', '0' )
			SetSetting( 'UPDATE_NOTIFY_COUNT', '0' )
			LOG_TRACE( '------------- Add cached UPDATE_NOTIFY=0 UPDATE_NOTIFY_COUNT=0' )

		if isNotify :
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_SYSTEM_UPDATE ).CheckBootOnVersion( )


	def UpdateLinkageService( self, aForceHide=False ) :
		if aForceHide == True :
			LOG_TRACE( 'Force hide linkage service' )
			self.setProperty( 'HasLinkageService', 'False' )
			return

		chList = self.mDataCache.Channel_GetList( )
		if not chList or len( chList ) < 1 :
			LOG_TRACE( 'Delete all or not channel' )
			return

		status = self.mDataCache.Player_GetStatus( )

		if status.mMode == ElisEnum.E_MODE_PVR :
			self.setProperty( 'HasLinkageService', 'False' )
		else :
			hasLinkageService = self.mDataCache.GetLinkageService( )
			if hasLinkageService :
				self.setProperty( 'HasLinkageService', 'True' )
				self.StartLinkageServiceTimer()
				
			else :
				self.setProperty( 'HasLinkageService', 'False' )


	def ShowLinkageChannels( self ) :
		dialog = xbmcgui.Dialog( )
		linkageChannelList = []
		channelNameList = []

		linkageChannelList = self.mCommander.EPGEvent_GetLinkageChannel( )
		#self.mSid, self.mTsid, self.mOnid, self.mEventId, self.mChannelName

		if linkageChannelList == None or len( linkageChannelList ) <= 0 :
			LOG_WARN( "Has no linkage channel")
			return

		#runningTimer tp
		runningTimerList = self.mDataCache.Timer_GetRunningTimers( )

		LOG_TRACE('--------------- Linkage Channel List ----------------------')
		for linkageChannel in linkageChannelList :
			#linkageChannel.printdebug( )
			isAvailable = True
			if runningTimerList :
				isAvailable = False
				for timer in runningTimerList :
					iChannel = self.mDataCache.Channel_GetByAvailTransponder( timer.mServiceType, timer.mChannelNo, timer.mTsid, timer.mOnid, timer.mSid, linkageChannel.mTsid, linkageChannel.mOnid )
					if iChannel :
						isAvailable = True
						break

			if isAvailable :
				channelNameList.append( linkageChannel.mChannelName )

		isSelect = dialog.select( MR_LANG( 'Select Channel' ), channelNameList )

		if isSelect >= 0 :
			linkageChannel = linkageChannelList[ isSelect ]
			if linkageChannel :
				currentChannel = self.mDataCache.Channel_GetCurrent( )
				ret = self.mCommander.Channel_SetCurrentLinkageChannel( currentChannel.mNumber, currentChannel.mServiceType, linkageChannel.mTsid, linkageChannel.mOnid, linkageChannel.mSid, True )
				LOG_TRACE( 'TUNE LinkageService ret[%s] %s, %s, %s, %s, %s, %s' %( ret, currentChannel.mNumber, currentChannel.mServiceType, linkageChannel.mTsid, linkageChannel.mOnid, linkageChannel.mSid, True ) )



	def AsyncLinkageTimeout( self ) :
		self.setProperty( 'HasLinkageService', 'False' )


	def StartLinkageServiceTimer( self ) :
		self.mLinkageServiceTimer  = threading.Timer( E_LINKAGE_ICON_TIMEOUT, self.AsyncLinkageTimeout )
		self.mLinkageServiceTimer.start( )
	

	def StopLinkageServiceTimer( self ) :
		self.setProperty( 'HasLinkageService', 'False' )	
		if self.mLinkageServiceTimer and self.mLinkageServiceTimer.isAlive( ) :
			self.mLinkageServiceTimer.cancel( )
			del self.mLinkageServiceTimer
			
		self.mLinkageServiceTimer = None


	def HbbTV_ShowRedButton( self ) :
		LOG_TRACE( 'Show HbbTV' )
		if not self.mDataCache.GetHbbtvStatus( ) or self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
			return
		if self.mDataCache.GetHbbTVEnable( ) :
			self.setProperty ( 'EnableHbbTV', 'True' )
			self.mHbbTVTimer = threading.Timer( 10 , self.HbbTV_HideRedButton )
			self.mHbbTVTimer.start( )
		

	def HbbTV_HideRedButton( self ) :
		LOG_TRACE( 'Hide HbbTV' )	
		if self.mHbbTVTimer and self.mHbbTVTimer.isAlive( ) :
			self.mHbbTVTimer.cancel( )
			self.mHbbTVTimer = None

		self.setProperty ( 'EnableHbbTV', 'False' )


	def HbbTV_ShowBrowser( self ) :
		LOG_TRACE( 'Show HbbTV Command' )
		if not self.mDataCache.GetHbbtvStatus( ) or self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
			return
		if self.mDataCache.GetHbbTVEnable( ) :
			self.CheckStartedService( )
			self.mHbbTVShowing = True
			self.mCommander.AppHBBTV_Ready( 1 )
		else :
			LOG_TRACE("HbbTV not ready - Do nothing")


	def HbbTV_HideBrowser( self ) :
		if self.mMediaPlayerStarted == True :
			self.HbbTV_MediaPlayerStop() 
		LOG_TRACE( 'HideHbbTV Command' )
		if self.mHbbTVShowing == True :
			self.RestartService( )
			self.mHbbTVShowing = False		
			self.mCommander.AppHBBTV_Ready( 0 )
		else :
			LOG_TRACE("HbbTV not ready - Do nothing")


	def HbbTV_MediaPlayerStart( self, aURL) :
		LOG_ERR( 'HBBTEST URL=%s' %aURL )
		if self.mMediaPlayerStarted == True :
			self.mForceSetCurrent = False
			self.mMediaPlayerStarted = True 
			#xbmc.executebuiltin( 'XBMC.PlayerControl(Stop)' , True)
			xbmc.executebuiltin( 'XBMC.PlayMedia(%s, noresume, hbbtv )'% aURL )		
			self.mCommander.ExternalMediaPlayer_Started( 1 )
			LOG_ERR( 'self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s'% ( self.mHBBTVReady, self.mMediaPlayerStarted ) )
		else:
			self.mForceSetCurrent = True
			self.mCommander.AppMediaPlayer_Control( 1 )
			xbmc.executebuiltin( 'XBMC.PlayMedia(%s, noresume, hbbtv )'% aURL )
			self.mMediaPlayerStarted = True 
			self.mCommander.ExternalMediaPlayer_Started( 1 )
			LOG_ERR( 'self.mHBBTVReady[%s], self.mMediaPlayerStarted[%s]'% ( self.mHBBTVReady, self.mMediaPlayerStarted ) )
	

	def HbbTV_MediaPlayerStop( self ) :
		LOG_ERR( 'self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s'% ( self.mHBBTVReady, self.mMediaPlayerStarted ) )
		LOG_ERR( 'HBBTEST ElisEventExternalMediaPlayerStopPlay.getName' )
		if self.mMediaPlayerStarted == True :
			self.mMediaPlayerStarted = False
			self.mForceSetCurrent = False
			xbmc.executebuiltin( 'XBMC.PlayerControl(Stop)', True )
			self.mCommander.AppMediaPlayer_Control( 0 )
			#LOG_TRACE("MediaPlayerStop Sleep Start")
			#time.sleep(3)
			#LOG_TRACE("MediaPlayerStop Sleep End")
			self.UpdateMediaCenterVolume( )
			self.mDataCache.SyncMute( )
			self.mCommander.ExternalMediaPlayer_StopPlay( 1 )
			LOG_ERR( 'self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s'% ( self.mHBBTVReady, self.mMediaPlayerStarted ) )


	def HbbTV_MediaPlayerSetSpeed( self, aSpeed ) :
		LOG_ERR( 'self.mHBBTVReady[%s], self.ElisEventExternalMediaPlayerSetSpeed[%s]'% ( self.mHBBTVReady, aSpeed ) )
		if self.mMediaPlayerStarted == True :
			if aSpeed == 0 :
				xbmc.executebuiltin( 'XBMC.PlayerControl(pause)', False )
			elif aSpeed == 100 :
				xbmc.executebuiltin( 'XBMC.PlayerControl(resume)', False )
			else :
				LOG_ERR( 'HbbTV_MediaPlayerSetSpeed unknown speed = %s' %  aSpeed )


	def HbbTV_MediaPlayerSeek( self, aSeek ) :
		LOG_ERR( 'self.mHBBTVReady[%s], self.HbbTV_MediaPlayerSeek[%s]'% ( self.mHBBTVReady, aSeek ) )
		if self.mMediaPlayerStarted == True :
			xbmc.executebuiltin( 'XBMC.PlayerControl(seekpercentage(%s))'% aSeek )


	def StartYoutubeTV( self ) :
		print 'doliyu test start youtube'
		self.CheckStartedService( )
		self.mYoutubeTVStarted = True
		self.mCommander.System_ShowWebPage("http://www.youtube.com/tv", 0 )


	def StopYoutubeTV( self ) :
		print 'doliyu test stop youtube'
		self.mCommander.System_CloseWebPage( )
		self.mCommander.AppHBBTV_Ready( 0 )
		self.mYoutubeTVStarted = False
		print 'doliyu test stop youtube : end'

		iChannel = self.mDataCache.Channel_GetCurrent( )
		channelList = self.mDataCache.Channel_GetList( )
		if iChannel and channelList and len( channelList ) > 0 :
			iEPG = self.mDataCache.Epgevent_GetPresent( )
			if self.mDataCache.GetStatusByParentLock( ) and ( not self.mDataCache.GetPincodeDialog( ) ) and \
			   channelList and len( channelList ) > 0 and iChannel and iChannel.mLocked or self.mDataCache.GetParentLock( iEPG ) :
				#pvr.GlobalEvent.GetInstance( ).CheckParentLock( E_PARENTLOCK_INIT )
				self.mDataCache.Player_AVBlank( True )
				self.mDataCache.Channel_InvalidateCurrent( )
				self.mDataCache.Channel_SetCurrentSync( iChannel.mNumber, iChannel.mServiceType )
				self.mDataCache.Player_AVBlank( True )
				LOG_TRACE( '----------------------------------------------ch lock' )

			else :
				self.mDataCache.Channel_InvalidateCurrent( )
				self.mDataCache.Channel_SetCurrentSync( iChannel.mNumber, iChannel.mServiceType )
				self.mDataCache.SetParentLockPass( True )

		self.UpdateMediaCenterVolume( )
		self.mDataCache.SyncMute( )
		self.RestartService( )


	def CheckStartedService( self ) :
		if XBMC_GetWebserver( ) :
			self.mStartedWebserver = True
			xbmc.executebuiltin( 'WebServer(false)' )
		if XBMC_GetUpnpRenderer( ) :
			self.mStartedUpnp = True
			xbmc.executebuiltin( 'UpnpRenderer(false)' )
		if XBMC_GetEsallinterfaces( ) :
			self.mStartedEsall = True
			xbmc.executebuiltin( 'Esallinterfaces(false)' )


	def RestartService( self ) :
		if self.mStartedWebserver :
			self.mStartedWebserver = False
			xbmc.executebuiltin( 'WebServer(true)' )
		if self.mStartedUpnp :
			self.mStartedUpnp = False
			xbmc.executebuiltin( 'UpnpRenderer(true)' )
		if self.mStartedEsall :
			self.mStartedEsall = False
			xbmc.executebuiltin( 'Esallinterfaces(true)' )


	def CheckDMXInfo( self ) :
		dmxAvail = True

		mTitle = MR_LANG( 'Maximum number of demux reached' )
		mLine1 = MR_LANG( 'Try again after stopping%s any one of recording, timeshift or PIP' )% NEW_LINE
		dmxCount = self.mDataCache.Get_FreeTssCount( )
		LOG_TRACE( '----------------------------------------DMX count[%s]'% dmxCount )
		if dmxCount < 1 :
			dmxAvail = False

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( mTitle, mLine1 )
			dialog.doModal( )

		return dmxAvail

	def SetMoveConfigureToAddVolume( self ) :
		configure = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_CONFIGURE )
		configure.mPrevListItemID = 7
		configure.SetFocusAddVolume( True )
		WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIGURE, WinMgr.WIN_ID_MAINMENU )

