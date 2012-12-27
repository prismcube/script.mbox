from pvr.gui.WindowImport import *
import sys, inspect, time
import gc


class NullWindow( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mAsyncShowTimer = None
		if E_SUPPROT_HBBTV == True :
			self.mHBBTVReady = False
			self.mMediaPlayerStarted = False
			self.mForceSetCurrent = True
			self.mStartTimeForTest = time.time( ) + 7200
			LOG_ERR('self.mHBBTVReady = %s, self.mMediaPlayerStarted =%s' %( self.mHBBTVReady, self.mMediaPlayerStarted ) )


	def onInit( self ) :
		collected = gc.collect()
		#print "Garbage collection thresholds: %d\n" % gc.get_threshold()
		print "Garbage collector: collected %d objects." % (collected)
		
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.CheckMediaCenter( )
		status = self.mDataCache.Player_GetStatus( )
		if status.mMode == ElisEnum.E_MODE_LIVE :
			self.mWin.setProperty( 'PvrPlay', 'False' )
		else :
			self.mWin.setProperty( 'PvrPlay', 'True' )

		if self.mInitialized == False :
			self.mInitialized = True
			if self.mDataCache.GetFristInstallation( ) :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_FIRST_INSTALLATION, WinMgr.WIN_ID_MAINMENU )
				return
			else :
				self.mCommander.AppHBBTV_Ready( 1 )
				self.mHBBTVReady = True
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetPincodeRequest( True )
				xbmc.executebuiltin( 'xbmc.Action(contextmenu)' )
				return

		self.mEventBus.Register( self )
		self.LoadNoSignalState( )

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

		"""
		currentStack = inspect.stack( )
		LOG_TRACE( '+++++getrecursionlimit[%s] currentStack[%s]'% (sys.getrecursionlimit( ), len(currentStack)) )
		LOG_TRACE( '+++++currentStackInfo[%s]'% (currentStack) )

		startTime= self.mStartTimeForTest
		lastTime = time.time( ) + 7200
		lblStart = time.strftime('%H:%M:%S', time.localtime(startTime) )
		lblLast  = time.strftime('%H:%M:%S', time.localtime(lastTime) )
		lblTest  = '%02d:%s'% ( (lastTime - startTime)/3600, time.strftime('%M:%S', time.gmtime(lastTime - startTime) ) )
		LOG_TRACE( 'startTime[%s] lastTime[%s] TestTime[%s]'% (lblStart, lblLast, lblTest) )
		"""


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return


		LOG_ERR( 'ACTION_TEST actionID=%d'% actionId )
		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_MOVE_LEFT :
			if ElisPropertyEnum( 'Lock Mainmenu', self.mCommander ).GetProp( ) == 0 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
				dialog.SetDialogProperty( MR_LANG( 'Enter your PIN code' ), '', 4, True )
	 			dialog.doModal( )
	 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
	 				tempval = dialog.GetString( )
	 				if len( tempval ) != 4 :
	 					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'The PIN code must be 4-digit long' ) )
			 			dialog.doModal( )
			 			return
					if int( tempval ) == ElisPropertyInt( 'PinCode', self.mCommander ).GetProp( ) :
						self.Close( )
						WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MAINMENU )
					else :
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Sorry, that PIN code does not match' ) )
			 			dialog.doModal( )
			else :
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MAINMENU )
			
		elif actionId == Action.ACTION_PARENT_DIR :
			status = self.mDataCache.Player_GetStatus( )		
			if status.mMode == ElisEnum.E_MODE_PVR :
				self.Close( )			
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW )			
		
		elif actionId == Action.ACTION_SELECT_ITEM :
			self.Close( )
			status = self.mDataCache.Player_GetStatus( )		
			if status.mMode == ElisEnum.E_MODE_PVR :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )
			else :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CHANNEL_LIST_WINDOW, WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_SHOW_INFO :
			if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
				msg = MR_LANG( 'Try again after stopping all your recordings first' )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), msg )
				dialog.doModal( )
			else :
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EPG_WINDOW )

		elif actionId == Action.ACTION_CONTEXT_MENU :
			status = self.mDataCache.Player_GetStatus( )
			self.Close( )
			if status.mMode == ElisEnum.E_MODE_LIVE :
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )

			else :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE, WinMgr.WIN_ID_NULLWINDOW )			

		elif actionId == Action.ACTION_PAGE_DOWN :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_PVR :
				return -1

			prevChannel = None
			prevChannel = self.mDataCache.Channel_GetPrev( self.mDataCache.Channel_GetCurrent( ) ) #self.mCommander.Channel_GetPrev( )
			if prevChannel :
				self.mDataCache.Channel_SetCurrent( prevChannel.mNumber, prevChannel.mServiceType )			
				self.Close( )
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetPincodeRequest( True )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )

		elif actionId == Action.ACTION_PAGE_UP :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_PVR :
				return -1

			nextChannel = None
			nextChannel = self.mDataCache.Channel_GetNext( self.mDataCache.Channel_GetCurrent( ) )
			if nextChannel :
				self.mDataCache.Channel_SetCurrent( nextChannel.mNumber, nextChannel.mServiceType )
				self.Close( )
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetPincodeRequest( True )
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

				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_JUMP )
				dialog.SetDialogProperty( str( aKey ) )
				dialog.doModal( )

				isOK = dialog.IsOK( )
				if isOK == E_DIALOG_STATE_YES :
					inputNumber = dialog.GetChannelLast( )
					iCurrentCh = self.mDataCache.Channel_GetCurrent( )
					if iCurrentCh.mNumber != int(inputNumber) :
						jumpChannel = self.mDataCache.Channel_GetCurr( int(inputNumber) )
						if jumpChannel != None and jumpChannel.mError == 0 :
							if jumpChannel.mLocked :
								if not self.mDataCache.Get_Player_AVBlank( ) :
									self.mDataCache.Player_AVBlank( True )
								dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_INPUT_PINCODE )
								dialog.SetTitleLabel( MR_LANG( 'Enter your PIN code' ) )
								dialog.doModal( )

								if dialog.GetNextAction( ) == dialog.E_TUNE_NEXT_CHANNEL :
									xbmc.executebuiltin( 'xbmc.Action(PageUp)' )

								elif dialog.GetNextAction( ) == dialog.E_TUNE_PREV_CHANNEL :
									xbmc.executebuiltin( 'xbmc.Action(PageDown)' )

								if dialog.IsOK( ) == E_DIALOG_STATE_YES :
									if self.mDataCache.Get_Player_AVBlank( ) :
										self.mDataCache.Player_AVBlank( False )
							else :
								if self.mDataCache.Get_Player_AVBlank( ) :
									self.mDataCache.Player_AVBlank( False )

							self.mDataCache.Channel_SetCurrent( jumpChannel.mNumber, jumpChannel.mServiceType )


			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_TIMESHIFT_JUMP )
				dialog.SetDialogProperty( str( aKey ) )
				dialog.doModal( )

				isOK = dialog.IsOK( )
				if isOK == E_DIALOG_STATE_YES :

					move = dialog.GetMoveToJump( )
					if move :
						ret = self.mDataCache.Player_JumpToIFrame( int( move ) )

		elif actionId == Action.ACTION_STOP :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_LIVE:
				self.ShowRecordingStopDialog( )			

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
				self.mDataCache.Player_Stop( )

			self.Close( )
			self.SetMediaCenter( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MEDIACENTER, WinMgr.WIN_ID_LIVE_PLATE )

		elif actionId == Action.ACTION_MBOX_TVRADIO :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.mDataCache.ToggleTVRadio( )
				if ret :
					self.Close( )
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )
				else :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No TV and radio channel available' ) )
					dialog.doModal( )

		elif actionId == Action.ACTION_MBOX_RECORD :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_PVR :
				msg = MR_LANG( 'Try again after stopping playback first' )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), msg )
				dialog.doModal( )
			else :
				self.ShowRecordingStartDialog( )
		
		elif actionId == Action.ACTION_PAUSE or actionId == Action.ACTION_PLAYER_PLAY :
			if HasAvailableRecordingHDD( ) == False :
				return
				
			if self.mDataCache.GetLockedState( ) == ElisEnum.E_CC_FAILED_NO_SIGNAL :
				return -1

			self.Close( )
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = actionId
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )

		elif actionId == Action.ACTION_MBOX_REWIND :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_TIMESHIFT or status.mMode == ElisEnum.E_MODE_PVR :
				self.Close( )
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = actionId
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )

		elif actionId == Action.ACTION_MBOX_FF :
			status = self.mDataCache.Player_GetStatus( )		
			if status.mMode == ElisEnum.E_MODE_TIMESHIFT or status.mMode == ElisEnum.E_MODE_PVR :
				self.Close( )			
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = actionId
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )

		elif actionId == Action.ACTION_MBOX_ARCHIVE :
			if HasAvailableRecordingHDD( ) == False :
				return
				
			self.Close( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_MBOX_TEXT :
			if not self.mDataCache.Teletext_Show( ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No teletext available' ) )
				dialog.doModal( )

		elif actionId == Action.ACTION_MBOX_SUBTITLE :
			pass

		elif actionId == Action.ACTION_MBOX_NUMLOCK :
			LOG_TRACE( 'Numlock is not support until now' )
			pass

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
				xbmcgui.Dialog( ).ok('Infomation', msg )
				
		
		elif actionId == Action.REMOTE_4:  #TEST : stop Record
			print 'open record dialog'
			runningCount = self.mCommander.Record_GetRunningRecorderCount( )
			LOG_TRACE( 'runningCount=%d' %runningCount )

			if  runningCount > 0 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_STOP_RECORD )
				dialog.doModal( )

		elif actionId == Action.REMOTE_1:  #TEST : bg test
		"""


	def onClick(self, aControlId) :
		pass
		#print "onclick( ): control %s" % aControlId


	def onFocus(self, aControlId) :
		pass
		#print "onFocus( ): control %s" % aControlId
		#self.mLastFocusId = aControlId


	def onEvent(self, aEvent):
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
				self.mDataCache.mCacheReload = True
				xbmc.executebuiltin( 'xbmc.Action(contextmenu)' )

			elif aEvent.getName( ) == ElisEventChannelChangedByRecord.getName( ) :
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetPincodeRequest( True )
				xbmc.executebuiltin( 'xbmc.Action(contextmenu)' )

			elif aEvent.getName( ) == ElisEventTTXClosed.getName( ) :
				if E_SUPPROT_HBBTV :
					LOG_TRACE('----------HBB Tv Ready')
					self.mCommander.AppHBBTV_Ready( 0 )
					self.mHBBTVReady = False

				self.mDataCache.Teletext_NotifyHide( )
				self.mDataCache.LoadVolumeToSetGUI( )
				LOG_TRACE( '----------ElisEventTTXClosed' )

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



	def ShowRecordingStartDialog( self ) :
		runningCount = self.mDataCache.Record_GetRunningRecorderCount( )
		#LOG_TRACE( 'runningCount[%s]' %runningCount)
		
		if HasAvailableRecordingHDD( ) == False :
			return

		isOK = False
		if runningCount < 2 :
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
			self.mDataCache.mCacheReload = True


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
			self.mDataCache.mCacheReload = True


	def Close( self ) :
		self.mEventBus.Deregister( self )

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
