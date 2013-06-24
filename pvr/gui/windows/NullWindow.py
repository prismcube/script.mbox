from pvr.gui.WindowImport import *
import sys, inspect, time, threading
import xbmc, xbmcgui, gc


E_NULL_WINDOW_BASE_ID = WinMgr.WIN_ID_NULLWINDOW * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID
E_BUTTON_ID_FAKE      = E_NULL_WINDOW_BASE_ID + 9000

E_NOMAL_BLINKING_TIME = 0.2
E_MAX_BLINKING_COUNT  =  10

E_NO_TUNE  = False
E_SET_TUNE = True


class NullWindow( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mAsyncTuneTimer = None
		self.mAsyncShowTimer = None
		self.mRecordBlinkingTimer = None	
		self.mOnTimeDelay = 0
		self.mPreviousBlockTime = 1.0
		self.mRecordBlinkingCount = E_MAX_BLINKING_COUNT
		self.mOnBlockTimer_GreenKey = 0
		self.mIsShowDialog = False
		
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
		self.SetActivate( True )
		self.setFocusId( E_BUTTON_ID_FAKE )
		self.SetSingleWindowPosition( E_NULL_WINDOW_BASE_ID )
		collected = gc.collect( )
		#print "Garbage collection thresholds: %d\n" % gc.get_threshold()
		playingRecord = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW ).GetPlayingRecord( )
		#LOG_TRACE('---------------playingrecord[%s]'% playingRecord )
		try :
			if playingRecord :
				self.SetFrontdisplayMessage( playingRecord.mRecordName )
			else :
				self.mDataCache.Frontdisplay_SetCurrentMessage( )
		except Exception, e :
			LOG_TRACE('except[%s]'% e )

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
			self.mInitialized = True
			unpackPath = self.mDataCache.USB_GetMountPath( )
			if unpackPath :
				self.mDataCache.SetUSBAttached( True )
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_SYSTEM_UPDATE ).CheckBootOnVersion( )

			if ElisPropertyEnum( 'First Installation', self.mCommander ).GetProp( ) != 0 :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_FIRST_INSTALLATION, WinMgr.WIN_ID_MAINMENU )
				return
			else :
				self.mCommander.AppHBBTV_Ready( 1 )
				self.mHBBTVReady = True
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetPincodeRequest( True )
				xbmc.executebuiltin( 'xbmc.Action(contextmenu)' )
				#labelMode = GetStatusModeLabel( status.mMode )
				#thread = threading.Timer( 0.1, AsyncShowStatus, [labelMode] )
				#thread.start( )
				return

		self.mEventBus.Register( self )
		self.CheckNochannel( )
		#self.LoadNoSignalState( )
		self.CheckSubTitle( )

		if E_SUPPROT_HBBTV == True :
			LOG_ERR('self.mDataCache.Player_GetStatus( ) = %d'% status.mMode )
			if status.mMode == ElisEnum.E_MODE_LIVE :
				if self.mDataCache.GetLockedState( ) == ElisEnum.E_CC_FAILED_SCRAMBLED_CHANNEL or \
				self.mDataCache.GetLockedState( ) == ElisEnum.E_CC_FAILED_NO_SIGNAL :
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

		self.DoRelayAction( )
		self.mOnTimeDelay = time.time( )
		self.mOnBlockTimer_GreenKey = time.time( )

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


	def onAction( self, aAction ) :
		LOG_TRACE( 'action=%d' % aAction.getId( ) )
		if self.IsActivate( ) == False  :
			LOG_TRACE( 'SKIP' )
			return
	
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		LOG_ERR( 'ACTION_TEST actionID=%d'% actionId )
		if actionId == Action.ACTION_PREVIOUS_MENU :
			if ElisPropertyEnum( 'Lock Mainmenu', self.mCommander ).GetProp( ) == 0 :
				self.CloseSubTitle( )			
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
				dialog.SetDialogProperty( MR_LANG( 'Enter your PIN code' ), '', 4, True )
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
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_LIVE :
				if ( time.time( ) - self.mOnTimeDelay ) < 1.5 :
					LOG_TRACE( '------blocking Time back key' )
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
					LOG_TRACE( '----------Teletext_IsShowing...No Changed window' )
					return

				if status.mMode == ElisEnum.E_MODE_PVR :
					self.Close( )
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )

				#buyer issue, hide
				elif status.mMode == ElisEnum.E_MODE_TIMESHIFT :
					labelMode = MR_LANG( 'LIVE' )
					thread = threading.Timer( 0.1, AsyncShowStatus, [labelMode] )
					thread.start( )
				#	self.Close( )
				#	WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
				#	WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE, WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_MBOX_XBMC :
			if self.GetBlinkingProperty( ) != 'None' :
				LOG_TRACE( '----------------try recording' )
				return

			isDownload = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_SYSTEM_UPDATE ).GetStatusFromFirmware( )
			if isDownload :
				self.DialogPopupOK( actionId + 1000 )
				return

			status = self.mDataCache.Player_GetStatus( )
			if status.mMode != ElisEnum.E_MODE_LIVE :
				if status.mMode == ElisEnum.E_MODE_PVR :
					self.DialogPopupOK( actionId )
					return

				self.mDataCache.Player_Stop( )

			if not CheckHdd( ) :
				self.CloseSubTitle( )
				msg = MR_LANG( 'Installing and executing XBMC add-ons%s may not work properly without an internal HDD' )% NEW_LINE
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), msg )
				dialog.doModal( )
				self.CheckSubTitle( )

			self.Close( )
			self.SetMediaCenter( )
			#WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MEDIACENTER, WinMgr.WIN_ID_LIVE_PLATE )
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
					self.DialogPopupOK( ElisEnum.E_CC_FAILED_NO_SIGNAL )
					return

				if status.mMode == ElisEnum.E_MODE_TIMESHIFT :
					self.mDataCache.Player_Stop( )

				self.CloseSubTitle( )
				if RECORD_WIDTHOUT_ASKING == True :
					if self.GetBlinkingProperty( ) != 'None' :
						return
					self.StartRecordingWithoutAsking( )				
				else :
					self.ShowRecordingStartDialog( )
				self.CheckSubTitle( )
		
		elif actionId == Action.ACTION_PAUSE or actionId == Action.ACTION_PLAYER_PLAY or \
		     actionId == Action.ACTION_MOVE_LEFT or actionId == Action.ACTION_MOVE_RIGHT :
			if HasAvailableRecordingHDD( ) == False :
				return

			status = self.mDataCache.Player_GetStatus( )
			if status.mMode != ElisEnum.E_MODE_PVR and \
			   self.mDataCache.GetLockedState( ) == ElisEnum.E_CC_FAILED_NO_SIGNAL :
				return -1

			if actionId == Action.ACTION_MOVE_RIGHT and status.mMode == ElisEnum.E_MODE_LIVE :
				return -1

			if ( actionId == Action.ACTION_PLAYER_PLAY or actionId == Action.ACTION_PAUSE ) and \
			   self.mDataCache.Get_Player_AVBlank( ) and status.mMode == ElisEnum.E_MODE_LIVE :
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
			if HasAvailableRecordingHDD( ) == False :
				return
				
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
			LOG_TRACE( 'Numlock is not support until now' )
			pass

		elif actionId == Action.ACTION_COLOR_GREEN :
			if ( time.time( ) - self.mOnBlockTimer_GreenKey ) <= 1 :
				LOG_TRACE( 'blocking time Green key' )
				return

			self.mOnBlockTimer_GreenKey = time.time( )
			self.DialogPopupOK( actionId )

		elif actionId == Action.ACTION_COLOR_YELLOW :
			self.DialogPopupOK( actionId )

		elif actionId == Action.ACTION_COLOR_BLUE :
			self.DialogPopupOK( actionId )

		else :
			self.NotAvailAction( )
			LOG_TRACE( 'unknown key[%s]'% actionId )



		"""
		#test
		elif actionId == Action.ACTION_MOVE_DOWN :
			from pvr.gui.windows.SystemUpdate import SCRIPTClass, PVSClass
			iPVSData = PVSClass( )
			iPVSData.mFileName = 'update_ruby_1.0.0.rc2_Update_Test.zip'
			iPVSData.mMd5 = 'a62064abd41c2a59c4703cd174a463de'
			iPVSData.mSize = 189322973
			iPVSData.mShellScript.mScriptFileName = 'updater7.sh'
			iPVSData.mActions = 'sleep 1\necho Test1\necho Test2\nsleep 2\necho Action end'
			basedir = '/mnt/hdd0/program/download'

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_UPDATE_PROGRESS )
			dialog.SetDialogProperty( MR_LANG( 'System Update' ), basedir, iPVSData )
			dialog.doModal( )

			shell = dialog.GetResult( )
			if shell == 0 :
				InitFlash( )
			LOG_TRACE( '--------------result[%s]'% shell )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			print 'youn check ation right'
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_INFO_PLATE1 )
			#DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_TEST_DIALOG ).doModal( )

		elif actionId == Action.ACTION_MOVE_UP :
			print 'youn check ation up'
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_INFO_PLATE )

		elif actionId == Action.ACTION_MOVE_DOWN :
			print 'youn check ation up'
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_INFO_PLATE2 )

		elif actionId == Action.REMOTE_3:  #TEST : start Record
			print 'open record dialog'
			
			runningCount = self.mCommander.Record_GetRunningRecorderCount( )
			LOG_TRACE( 'runningCount=%d' %runningCount)
			if  runningCount < E_MAX_RECORD_COUNT :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
				dialog.doModal( )
			else:
				msg = 'Already %d recording(s) running' %runningCount
				xbmcgui.Dialog( ).ok('Information', msg )
				
		
		elif actionId == Action.REMOTE_4:  #TEST : stop Record
			print 'open record dialog'
			runningCount = self.mCommander.Record_GetRunningRecorderCount( )
			LOG_TRACE( 'runningCount=%d' %runningCount )

			if  runningCount > 0 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_STOP_RECORD )
				dialog.doModal( )

		elif actionId == Action.REMOTE_1:  #TEST : bg test
			pass
		"""


	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return

		self.Close( )
		status = self.mDataCache.Player_GetStatus( )
		if status.mMode == ElisEnum.E_MODE_PVR :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )
		else :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CHANNEL_LIST_WINDOW, WinMgr.WIN_ID_NULLWINDOW )


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
		#print "onFocus( ): control %s" % aControlId
		#self.mLastFocusId = aControlId


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


			elif E_SUPPROT_HBBTV == True :
				if aEvent.getName( ) == ElisEventExternalMediaPlayerStart.getName( ) :
					LOG_ERR( 'HBBTEST URL=%s' %aEvent.mUrl )
					if self.mMediaPlayerStarted == True :
						self.mForceSetCurrent = False
						self.mMediaPlayerStarted = True 
						xbmc.executebuiltin( 'XBMC.PlayerControl(Stop)' )
						xbmc.executebuiltin( 'XBMC.PlayMedia(%s, noresume )'% aEvent.mUrl )		
						self.mCommander.ExternalMediaPlayer_Started( 1 )
						LOG_ERR( 'self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s'% ( self.mHBBTVReady, self.mMediaPlayerStarted ) )
					else:
						self.mForceSetCurrent = True
						self.mCommander.AppMediaPlayer_Control( 1 )
						xbmc.executebuiltin( 'XBMC.PlayMedia(%s, noresume )'% aEvent.mUrl )
						self.mMediaPlayerStarted = True 
						self.mCommander.ExternalMediaPlayer_Started( 1 )
						LOG_ERR( 'self.mHBBTVReady[%s], self.mMediaPlayerStarted[%s]'% ( self.mHBBTVReady, self.mMediaPlayerStarted ) )

				elif aEvent.getName( ) == ElisEventExternalMediaPlayerSetSpeed.getName( ) :
					pass
			
				elif aEvent.getName( ) == ElisEventExternalMediaPlayerSeekStream.getName( ) :
					pass
			
				elif aEvent.getName( ) == ElisEventExternalMediaPlayerStopPlay.getName( ) :
					LOG_ERR( 'self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s'% ( self.mHBBTVReady, self.mMediaPlayerStarted ) )
					LOG_ERR( 'HBBTEST ElisEventExternalMediaPlayerStopPlay.getName' )
					if self.mMediaPlayerStarted == True :
						self.mMediaPlayerStarted = False
						self.mForceSetCurrent = False
						xbmc.executebuiltin( 'XBMC.PlayerControl(Stop)' )
						self.mCommander.ExternalMediaPlayer_StopPlay( 1 )
						self.mCommander.AppMediaPlayer_Control( 0 )
						self.ForceSetCurrent( )
						LOG_ERR( 'self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s'% ( self.mHBBTVReady, self.mMediaPlayerStarted ) )

		else :
			if aEvent.getName( ) == ElisEventExternalMediaPlayerStopPlay.getName( ) :
				LOG_TRACE( 'HBBTEST ElisEventExternalMediaPlayerStopPlay.getName' )
				LOG_ERR( 'self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s' %( self.mHBBTVReady, self.mMediaPlayerStarted ) )
				if self.mMediaPlayerStarted == True :
					self.mForceSetCurrent = False
					self.mMediaPlayerStarted = False
					xbmc.executebuiltin( 'XBMC.PlayerControl(Stop)' )
					self.mCommander.ExternalMediaPlayer_StopPlay( 1 )
					self.mCommander.AppMediaPlayer_Control( 0 )					
					self.ForceSetCurrent( )
					LOG_ERR( 'self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s'% ( self.mHBBTVReady, self.mMediaPlayerStarted ) )

			elif aEvent.getName( ) == ElisEventExternalMediaPlayerStart.getName( ) :
				LOG_TRACE( 'HBBTEST URL=%s' %aEvent.mUrl )
				LOG_ERR( 'self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s'% ( self.mHBBTVReady, self.mMediaPlayerStarted) )
				if self.mMediaPlayerStarted == True :
					self.mMediaPlayerStarted = False
					self.mForceSetCurrent = False
					xbmc.executebuiltin( 'XBMC.PlayerControl(Stop)' )
					xbmc.executebuiltin( 'XBMC.PlayMedia(%s, noresume )'% aEvent.mUrl )
					self.mMediaPlayerStarted = True 
					self.mCommander.ExternalMediaPlayer_Started( 1 )
					LOG_ERR( 'self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s'% ( self.mHBBTVReady, self.mMediaPlayerStarted ) )
				else:
					self.mForceSetCurrent = True
					self.mCommander.AppMediaPlayer_Control( 1 )
					xbmc.executebuiltin( 'XBMC.PlayMedia(%s, noresume )'% aEvent.mUrl )
					self.mMediaPlayerStarted = True 
					self.mCommander.ExternalMediaPlayer_Started( 1 )
					LOG_ERR( 'self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s'%( self.mHBBTVReady, self.mMediaPlayerStarted ) )

			else:
				pass 
				#LOG_TRACE( 'NullWindow winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId( )) )


	def StartRecordingWithoutAsking( self ) :
		runningCount = self.mDataCache.Record_GetRunningRecorderCount( )
		#LOG_TRACE( 'runningCount[%s]' %runningCount)
		if HasAvailableRecordingHDD( ) == False :
			return

		mTimer = self.mDataCache.GetRunnigTimerByChannel( )
		isOK = False

		if mTimer :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_ERROR and dialog.GetConflictTimer( ) :
				RecordConflict( dialog.GetConflictTimer( ) )

			return

		elif runningCount < 2 :
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
				if otrInfo.mHasEPG == True :			
					timeshiftRecordSec = int( otrInfo.mTimeshiftRecordMs/1000 )
					LOG_TRACE( 'mTimeshiftRecordMs=%dMs : %dSec' %(otrInfo.mTimeshiftRecordMs, timeshiftRecordSec ) )
				
					copyTimeshift  = localTime - otrInfo.mEventStartTime
					LOG_TRACE( 'copyTimeshift #3=%d' %copyTimeshift )
					if copyTimeshift > timeshiftRecordSec :
						copyTimeshift = timeshiftRecordSec
					LOG_TRACE( 'copyTimeshift #4=%d' %copyTimeshift )

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
			msg = MR_LANG( 'You have reached the maximum number of%s recordings allowed' )% NEW_LINE
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
			LOG_TRACE( '++++++++++++++++++++++++++++++++++++ blinking count  is zero' )
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
		if HasAvailableRecordingHDD( ) == False :
			return

		mTimer = self.mDataCache.GetRunnigTimerByChannel( )

		isOK = False
		if runningCount < 2 or mTimer :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
			dialog.doModal( )

			isOK = dialog.IsOK( )
			if isOK == E_DIALOG_STATE_YES :
				isOK = True

			if dialog.IsOK( ) == E_DIALOG_STATE_ERROR and dialog.GetConflictTimer( ) :
				RecordConflict( dialog.GetConflictTimer( ) )

		else:
			msg = MR_LANG( 'You have reached the maximum number of%s recordings allowed' )% NEW_LINE
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

		self.StopBlinkingIconTimer( )
		self.SetBlinkingProperty( 'None' )		

		if E_SUPPROT_HBBTV == True :
			LOG_ERR('self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s'% ( self.mHBBTVReady, self.mMediaPlayerStarted ) )
			if self.mHBBTVReady == True :
				if self.mMediaPlayerStarted == True :
					xbmc.executebuiltin( 'XBMC.PlayerControl(Stop)' )
					self.mCommander.AppMediaPlayer_Control( 0 )
					self.mMediaPlayerStarted = False;
					self.ForceSetCurrent( )
				LOG_TRACE( '----------HBB Tv Not Ready' )
				self.mCommander.AppHBBTV_Ready( 0 )
				self.mHBBTVReady = False 
				LOG_ERR( 'self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s'% ( self.mHBBTVReady, self.mMediaPlayerStarted ) )
			

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
			LOG_TRACE( 'Already opened, Dialog' )


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
				msg = MR_LANG( 'EPG None' )

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

		elif aAction == Action.ACTION_MBOX_TVRADIO :
			head = MR_LANG( 'Error' )
			msg = MR_LANG( 'No channels available for the selected mode' )

		elif aAction == Action.ACTION_COLOR_YELLOW :
			self.CloseSubTitle( )
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).DoContextAction( CONTEXT_ACTION_AUDIO_SETTING )
			self.CheckSubTitle( )
			self.mIsShowDialog = False
			return

		elif aAction == Action.ACTION_COLOR_BLUE :
			self.CloseSubTitle( )
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).DoContextAction( CONTEXT_ACTION_VIDEO_SETTING )
			self.CheckSubTitle( )
			self.mIsShowDialog = False
			return

		elif aAction == Action.ACTION_COLOR_GREEN :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode != ElisEnum.E_MODE_PVR :
				self.mIsShowDialog = False
				return
			
			playingRecord = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW ).GetPlayingRecord( )
			if playingRecord == None or playingRecord.mError != 0 :
				self.mIsShowDialog = False
				return

			bookmarkList = self.mDataCache.Player_GetBookmarkList( playingRecord.mRecordKey )
			if bookmarkList and len( bookmarkList ) >= E_DEFAULT_BOOKMARK_LIMIT :
				head = MR_LANG( 'Error' )
				msg = MR_LANG( 'You have reached the maximum number of%s bookmarks allowed' )% NEW_LINE
			else :

				status = self.mDataCache.Player_GetStatus( )
				if status.mSpeed != 100 :
					self.mDataCache.Player_Resume( )

				self.mDataCache.Player_CreateBookmark( )
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
			LOG_TRACE( '----------------- Can not setCurrent by No Channel previous' )
			return

		self.AsyncTuneChannelByInput( oldChannel.mNumber, True )


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
		dialog.SetDefaultProperty( MR_LANG( 'Recent channels' ), channelList, True, False  )
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

