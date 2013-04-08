from pvr.gui.WindowImport import *
import sys, inspect, time, threading
import gc


E_NULL_WINDOW_BASE_ID = WinMgr.WIN_ID_NULLWINDOW * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID
E_BUTTON_ID_FAKE      = E_NULL_WINDOW_BASE_ID + 9000

E_NOMAL_BLINKING_TIME = 0.2


class NullWindow( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mAsyncTuneTimer = None
		self.mAsyncShowTimer = None
		self.mRecordBlinkingTimer = None	
		if E_SUPPROT_HBBTV == True :
			self.mHBBTVReady = False
			self.mMediaPlayerStarted = False
			self.mForceSetCurrent = True
			self.mStartTimeForTest = time.time( ) + 7200
			LOG_ERR('self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s' %( self.mHBBTVReady, self.mMediaPlayerStarted ) )
			#self.mSubTitleIsShow = False
			self.mIsShowDialog = False
			self.mEnableBlickingTimer = False			


	def onInit( self ) :
		self.mLoopCount = 0
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

		self.CheckMediaCenter( )
		status = self.mDataCache.Player_GetStatus( )
		if status.mMode == ElisEnum.E_MODE_LIVE :
			self.setProperty( 'PvrPlay', 'False' )
		else :
			self.setProperty( 'PvrPlay', 'True' )

		if self.mInitialized == False :
			self.mInitialized = True
			if ElisPropertyEnum( 'First Installation', self.mCommander ).GetProp( ) != 0 :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_FIRST_INSTALLATION, WinMgr.WIN_ID_MAINMENU )
				return
			else :
				self.mCommander.AppHBBTV_Ready( 1 )
				self.mHBBTVReady = True
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetPincodeRequest( True )
				xbmc.executebuiltin( 'xbmc.Action(contextmenu)' )
				labelMode = GetStatusModeLabel( status.mMode )
				thread = threading.Timer( 0.1, self.mDataCache.AsyncShowStatus, [labelMode] )
				thread.start( )
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
				self.RestartAsyncTune( )

			elif status.mMode == ElisEnum.E_MODE_PVR :
				self.Close( )			
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )

			else :
				labelMode = GetStatusModeLabel( status.mMode )
				thread = threading.Timer( 0.1, self.mDataCache.AsyncShowStatus, [labelMode] )
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
				return -1

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
				return -1

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

			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_LIVE :
				self.CloseSubTitle( )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_JUMP )
				dialog.SetDialogProperty( str( aKey ) )
				dialog.doModal( )
				self.CheckSubTitle( )				

				isOK = dialog.IsOK( )
				if isOK == E_DIALOG_STATE_YES :
					inputNumber = dialog.GetChannelLast( )
					iCurrentCh = self.mDataCache.Channel_GetCurrent( )
					if iCurrentCh.mNumber != int(inputNumber) :
						jumpChannel = self.mDataCache.Channel_GetCurr( int(inputNumber) )
						if jumpChannel != None and jumpChannel.mError == 0 :
							self.mDataCache.SetAVBlankByChannel( jumpChannel )
							self.mDataCache.Channel_SetCurrent( jumpChannel.mNumber, jumpChannel.mServiceType, None, True )

			else :
				self.CloseSubTitle( )			
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_TIMESHIFT_JUMP )
				dialog.SetDialogProperty( str( aKey ) )
				dialog.doModal( )
				self.CheckSubTitle( )

				isOK = dialog.IsOK( )
				if isOK == E_DIALOG_STATE_YES :
					move = dialog.GetMoveToJump( )
					if move :
						ret = self.mDataCache.Player_JumpToIFrame( int( move ) )

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

				elif status.mMode == ElisEnum.E_MODE_TIMESHIFT :
					self.Close( )
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE, WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_MBOX_XBMC :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode != ElisEnum.E_MODE_LIVE :
				if status.mMode == ElisEnum.E_MODE_PVR :
					self.DialogPopupOK( actionId )
					return

				self.mDataCache.Player_Stop( )

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
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_PVR :
				self.mDataCache.Player_CreateBookmark( )

		elif actionId == Action.ACTION_COLOR_YELLOW :
			self.DialogPopupOK( actionId )

		elif actionId == Action.ACTION_COLOR_BLUE :
			self.DialogPopupOK( actionId )

		else :
			self.NotAvailAction( )
			LOG_TRACE( 'unknown key[%s]'% actionId )



		"""
		#test
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
					self.StopBlickingIconTimer( )
					self.SetBlinkingProperty( 'None' )

				self.mDataCache.SetChannelReloadStatus( True )
				xbmc.executebuiltin( 'xbmc.Action(contextmenu)' )

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
			msg = MR_LANG( 'You have reached the maximum number of\nrecordings allowed' )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), msg )
			dialog.doModal( )

		if isOK :
			self.SetBlinkingProperty( 'True' )
			self.mEnableBlickingTimer = True
			self.StartBlickingIconTimer( )
			
			self.mDataCache.SetChannelReloadStatus( True )


	def RestartBlickingIconTimer( self, aTimeout=E_NOMAL_BLINKING_TIME ) :
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Restart' )
		self.StopBlickingIconTimer( )
		self.StartBlickingIconTimer( aTimeout )


	def StartBlickingIconTimer( self, aTimeout=E_NOMAL_BLINKING_TIME ) :
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Start' )	
		self.mRecordBlinkingTimer  = threading.Timer( aTimeout, self.AsyncBlinkingIcon )
		self.mRecordBlinkingTimer.start( )
	

	def StopBlickingIconTimer( self ) :
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

		if self.GetBlinkingProperty( ) == 'True' :
			self.SetBlinkingProperty( 'False' )
		else :
			self.SetBlinkingProperty( 'True' )

		self.RestartBlickingIconTimer( )


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
			msg = MR_LANG( 'You have reached the maximum number of\nrecordings allowed' )
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

		self.CloseSubTitle( )

		self.StopBlickingIconTimer( )
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
			

	def GetKeyDisabled( self ) :
		return False
	

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
			#self.mSubTitleIsShow = True
			self.mDataCache.Subtitle_Hide( )
		#else :
		#	self.mSubTitleIsShow = False


	def CheckSubTitle( self ) :
		#if self.mSubTitleIsShow :
		#	self.mDataCache.Subtitle_Show( )

		if self.mDataCache.GetLockedState( ) != ElisEnum.E_CC_SUCCESS :
			return

		selectedSubtitle = self.mDataCache.Subtitle_GetSelected( )
		if selectedSubtitle and selectedSubtitle.mError == 0 and selectedSubtitle.mPid :
			self.mDataCache.Subtitle_Show( )


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


	def RestartAsyncTune( self ) :
		self.mLoopCount += 1
		self.StopAsyncTune( )
		self.StartAsyncTune( )


	def StartAsyncTune( self ) :
		self.mAsyncTuneTimer = threading.Timer( 0.5, self.AsyncTuneChannel ) 				
		self.mAsyncTuneTimer.start( )


	def StopAsyncTune( self ) :
		if self.mAsyncTuneTimer	and self.mAsyncTuneTimer.isAlive( ) :
			self.mAsyncTuneTimer.cancel( )
			del self.mAsyncTuneTimer

		self.mAsyncTuneTimer  = None


	def AsyncTuneChannel( self ) :
		oldChannel = self.mDataCache.Channel_GetOldChannel( )

		if self.mLoopCount > 10 :
			channelList = self.mDataCache.Channel_GetOldChannelList( )
			listNumber = []
			for ch in channelList :
				listNumber.append( '%04d %s'% ( ch.mNumber, ch.mName ) )

			self.CloseSubTitle( )
			isSelect = xbmcgui.Dialog().select( MR_LANG( 'Recent channels' ), listNumber )
			#LOG_TRACE( '-------previous idx[%s] list[%s]'% ( isSelect, listNumber ) )
			self.CheckSubTitle( )

			if isSelect != -1 :
				oldChannel = channelList[isSelect]


		self.mDataCache.Channel_SetCurrentByOld( oldChannel )
		self.mLoopCount = 0
	

