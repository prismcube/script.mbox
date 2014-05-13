from pvr.gui.WindowImport import *
import pvr.DataCacheMgr
import pvr.ElisMgr
import pvr.Platform


AUTOPOWERDOWN_EXCEPTWINDOW = [ WinMgr.WIN_ID_SYSTEM_UPDATE, WinMgr.WIN_ID_FIRST_INSTALLATION ]
PARENTLOCK_CHECKWINDOW = [ 
	WinMgr.WIN_ID_NULLWINDOW,
	WinMgr.WIN_ID_MAINMENU,
	WinMgr.WIN_ID_CHANNEL_LIST_WINDOW,
	WinMgr.WIN_ID_LIVE_PLATE,
	#WinMgr.WIN_ID_CONFIGURE,
	WinMgr.WIN_ID_ARCHIVE_WINDOW,
	WinMgr.WIN_ID_TIMER_WINDOW,
	#WinMgr.WIN_ID_SYSTEM_INFO,
	#WinMgr.WIN_ID_MEDIACENTER,
	WinMgr.WIN_ID_EPG_WINDOW,
	WinMgr.WIN_ID_TIMESHIFT_PLATE,
	WinMgr.WIN_ID_SIMPLE_CHANNEL_LIST,
	WinMgr.WIN_ID_INFO_PLATE
	#WinMgr.WIN_ID_FAVORITE_ADDONS,
	#WinMgr.WIN_ID_SYSTEM_UPDATE,
	#WinMgr.WIN_ID_HELP
	]


gGlobalEvent = None

def GetInstance( ) :
	global gGlobalEvent
	if not gGlobalEvent :
		print 'Create instance'
		gGlobalEvent = GlobalEvent( )
	else :
		pass

	return gGlobalEvent


class GlobalEvent( object ) :
	def __init__( self ) :
		self.mDataCache = pvr.DataCacheMgr.GetInstance( )
		self.mIsDialogOpend	= False
		self.mIsShowPIPDialog = False
		self.mIsHddFullDialogOpened = False
		self.mEventId = None
		self.IsStartChannelLoad		= False
		#self.mIsChannelUpdateEvent = False
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.mTunerMgr	= pvr.TunerConfigMgr.GetInstance( )
		self.SendLocalOffsetToXBMC( )

		self.mDialogShowParental = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
		self.mDialogShowEvent = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CAS_EVENT )


	@classmethod
	def GetName( cls ) :
		return cls.__name__


	def onEvent( self, aEvent ) :
		if not WinMgr.gWindowMgr :
			return

		if aEvent.getName( ) == ElisEventPIPKeyHook.getName( ) :
			if pvr.Platform.GetPlatform( ).GetProduct( ) == PRODUCT_OSCAR :
				return
			#LOG_TRACE( '[GlobalEvent] eventName[%s] keycode[%s]'% ( aEvent.getName( ), aEvent.mKeyCode ) )
			if E_SUPPORT_XBMC_PIP_FULLSCREEN_ONLY :
				if xbmcgui.getCurrentWindowId() == 12005 or xbmcgui.getCurrentWindowId() == 12006 :
					pass
				else :
					xbmc.executebuiltin( 'Notification(%s, %s, 5000, DefaultIconInfo.png)' % ( MR_LANG( 'Watching PIP' ), MR_LANG( 'only available when Video plays in fullscreen' ) ) )
					#LOG_TRACE( '[GlobalEvent] CurrentWindowID[%s]'% xbmcgui.getCurrentWindowId() )
					return

			if aEvent.mKeyCode == 9 and ( not self.mIsShowPIPDialog ) :
				thread = threading.Timer( 0, self.ShowPIPDialog )
				thread.start( )
			return

		if aEvent.getName( ) == ElisEventCAMInsertRemove.getName( ) :
			self.CamInsertRemove( aEvent.mInserted )

		elif aEvent.getName( ) == ElisEventCIMMIShowMenu.getName( ) :
			thread = threading.Timer( 0.3, self.ShowEventDialog, [ aEvent ] )
			thread.start( )

		elif aEvent.getName( ) == ElisEventCIMMIShowEnq.getName( ) :
			thread = threading.Timer( 0.3, self.ShowParentalDialog, [ aEvent ] )
			thread.start( )

		elif aEvent.getName( ) == ElisEventCurrentEITReceived.getName( ) :
			LOG_TRACE( '----------received ElisEventCurrentEITReceived' )
			channel = self.mDataCache.Channel_GetCurrent( )
			if not channel or channel.mError != 0 :
				return -1
			if channel.mSid != aEvent.mSid or channel.mTsid != aEvent.mTsid or channel.mOnid != aEvent.mOnid :
				#LOG_TRACE('ignore event, same event')
				return -1
			self.CheckParentLock( E_PARENTLOCK_EIT, aEvent )
			self.CheckLinkageService()


		elif aEvent.getName( ) == ElisPMTReceivedEvent.getName( ) :
			LOG_TRACE( '----------received ElisPMTReceivedEvent' )
			#LOG_TRACE( '----------ch[%s] type[%s] ttx[%s] sub[%s] aud[%s,%s]'% ( aEvent.mChannelNumber, aEvent.mServiceType, aEvent.mTTXCount, aEvent.mSubCount, aEvent.mAudioCount, aEvent.mAudioStream[aEvent.mAudioSelectedIndex] ) )

			if aEvent :
				#aEvent.printdebug( )
				self.mDataCache.SetCurrentPMTEvent( aEvent )

		elif aEvent.getName( ) == ElisEventTimeReceived.getName( ) :
			self.SendLocalOffsetToXBMC( )

		elif aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or \
			 aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
			self.mDataCache.ReLoadChannelListByRecording( )
			if aEvent.getName( ) == ElisEventRecordingStopped.getName( ) and aEvent.mHDDFull :
				#LOG_TRACE('hddFull, dialogOpen[%s]'% self.mIsHddFullDialogOpened )
				if self.mIsHddFullDialogOpened == False :
					thread = threading.Timer( 0.3, self.AsyncHddFull )
					thread.start( )
				else :
					LOG_TRACE( 'Already opened, hddfull' )

			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_SIMPLE_CHANNEL_LIST ).ResetControls( )
			if WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_EPG_WINDOW :
				if self.mDataCache.Channel_GetZappingListStatus( ) :
					self.mDataCache.Channel_SetZappingListStatus( )
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_EPG_WINDOW ).UpdateByAvailableListChanged( )

		elif aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
			if aEvent.mType == ElisEnum.E_EOF_START :
				if WinMgr.GetInstance( ).GetLastWindowID( ) != WinMgr.WIN_ID_TIMESHIFT_PLATE :
					ret = self.mDataCache.Player_Resume( )
					LOG_TRACE( 'EventRecv EOF_START play_resume( ) ret[%s]'% ret )

			elif aEvent.mType == ElisEnum.E_EOF_END :
				if WinMgr.GetInstance( ).GetLastWindowID( ) != WinMgr.WIN_ID_NULLWINDOW and \
				   WinMgr.GetInstance( ).GetLastWindowID( ) != WinMgr.WIN_ID_TIMESHIFT_PLATE and \
				   WinMgr.GetInstance( ).GetLastWindowID( ) != WinMgr.WIN_ID_ARCHIVE_WINDOW :
					LOG_TRACE( 'CHECK onEVENT[%s] stop key[%s]'% ( aEvent.getName( ), aEvent.mKey ) )
					mPlayingRecord = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW ).GetPlayingRecord( )
					if mPlayingRecord :
						#isArchive and recordKey == EOF Key
						if mPlayingRecord.mRecordKey == aEvent.mKey :
							LOG_TRACE('global stop ------ Player_Stop' )
							self.mDataCache.Player_Stop( )
					else :
						#isTimeshift
						LOG_TRACE('global stop ------ Player_Stop' )
						self.mDataCache.Player_Stop( )

		elif aEvent.getName( ) == ElisEventChannelChangeStatus( ).getName( ) :
			#LOG_TRACE( '----------------ElisEventChannelChangeStatus mStatus[%s]'% aEvent.mStatus )
			restorePIP = False
			if aEvent.mStatus == ElisEnum.E_CC_FAILED_SCRAMBLED_CHANNEL :
				WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).GetLastWindowID( ) ).setProperty( 'Signal', 'Scramble' )
				self.mDataCache.SetLockedState( ElisEnum.E_CC_FAILED_SCRAMBLED_CHANNEL )

			elif aEvent.mStatus == ElisEnum.E_CC_FAILED_NO_SIGNAL :
				WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).GetLastWindowID( ) ).setProperty( 'Signal', 'False' )
				self.mDataCache.SetLockedState( ElisEnum.E_CC_FAILED_NO_SIGNAL )

			elif aEvent.mStatus == ElisEnum.E_CC_SUCCESS :
				WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).GetLastWindowID( ) ).setProperty( 'Signal', 'True' )
				self.mDataCache.SetLockedState( ElisEnum.E_CC_SUCCESS )

			elif aEvent.mStatus == ElisEnum.E_CC_FAILED_PROGRAM_NOT_FOUND :
				WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).GetLastWindowID( ) ).setProperty( 'Signal', 'NoService' )
				self.mDataCache.SetLockedState( ElisEnum.E_CC_FAILED_PROGRAM_NOT_FOUND )

			elif aEvent.mStatus == ElisEnum.E_CC_PIP_FAILED_SCRAMBLED_CHANNEL :#6
				restorePIP = True
				xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', 'True' )
				xbmcgui.Window( 10000 ).setProperty( 'PIPSignal', 'Scramble' )

			elif aEvent.mStatus == ElisEnum.E_CC_PIP_FAILED_PROGRAM_NOT_FOUND :#7
				restorePIP = True
				xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', 'True' )
				xbmcgui.Window( 10000 ).setProperty( 'PIPSignal', 'NoService' )

			elif aEvent.mStatus == ElisEnum.E_CC_PIP_FAILED_NO_SIGNAL :#5
				restorePIP = True
				xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', 'True' )
				xbmcgui.Window( 10000 ).setProperty( 'PIPSignal', 'False' )

			elif aEvent.mStatus == ElisEnum.E_CC_PIP_FAILED_TUNE_NOT_AVAILABLE :
				self.CheckTunablePIP( ElisEnum.E_CC_PIP_FAILED_TUNE_NOT_AVAILABLE )

			elif aEvent.mStatus == ElisEnum.E_CC_PIP_SUCCESS :#4
				blank = 'False'
				pChannel = self.mDataCache.PIP_GetCurrentChannel( )
				if pChannel and pChannel.mLocked :
					blank = 'True'
				#self.mDataCache.PIP_AVBlank( False )
				xbmcgui.Window( 10000 ).setProperty( 'BlankPIP', blank )
				xbmcgui.Window( 10000 ).setProperty( 'PIPSignal', 'True' )
				DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).PIP_Check( E_PIP_CHECK_FORCE )

			if restorePIP and self.mDataCache.PIP_GetSwapStatus( ) :
				DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).SwapExchangeToPIP( None, True, False )

			if WinMgr.GetInstance( ).GetLastWindowID( ) != WinMgr.WIN_ID_NULLWINDOW :
				return

			if aEvent.mStatus != ElisEnum.E_CC_SUCCESS :
				return

			selectedSubtitle = self.mDataCache.Subtitle_GetSelected( )
			if self.mDataCache.GetLockedState( ) == ElisEnum.E_CC_SUCCESS :
				if selectedSubtitle and selectedSubtitle.mError == 0 and selectedSubtitle.mPid :
					self.mDataCache.Subtitle_Show( )
					#WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).mSubTitleIsShow = True
			else :
				if selectedSubtitle and selectedSubtitle.mError == 0 or self.mDataCache.Subtitle_IsShowing( ) :
					self.mDataCache.Subtitle_Hide( )
					#WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).mSubTitleIsShow = False


		elif aEvent.getName( ) == ElisEventChannelChangeResult( ).getName( ) :
			self.CheckParentLock( E_PARENTLOCK_INIT )
			self.CheckTunablePIP( )

		elif aEvent.getName( ) == ElisEventVideoIdentified( ).getName( ) :
			self.mDataCache.Frontdisplay_ResolutionByIdentified( aEvent )

		elif aEvent.getName( ) == ElisEventPowerSave( ).getName( ) :
			if WinMgr.GetInstance( ).GetLastWindowID( ) not in AUTOPOWERDOWN_EXCEPTWINDOW :
				if self.mIsDialogOpend == False :
					thread = threading.Timer( 0.3, self.AsyncPowerSave )
					thread.start( )
			else :
				LOG_TRACE( 'Skip auto power down : %s' % WinMgr.GetInstance( ).GetLastWindowID( ) )

		elif aEvent.getName( ) == ElisEventChannelChangedByRecord.getName( ) :
			self.ChannelChangedByRecord( aEvent )

		elif aEvent.getName( ) == ElisEventShutdown.getName( ) :
			#LOG_TRACE('-----------shutdown[%s] blank[%s]'% ( aEvent.mType, self.mDataCache.Channel_GetInitialBlank( ) ) )
			self.mDataCache.SetStanbyStatus( aEvent.mType )
			if aEvent.mType == ElisEnum.E_STANDBY_POWER_ON :
				thread = threading.Timer( 1, self.AsyncStandbyPowerON )
				thread.start( )

			elif aEvent.mType == ElisEnum.E_NORMAL_STANDBY or aEvent.mType == ElisEnum.E_STANDBY_REC :
				self.mDataCache.SetStanbyClosing( True )
				thread = threading.Timer( 1, self.StanByClose )
				thread.start( )

		elif aEvent.getName( ) == ElisEventTTXClosed.getName( ) :
			if E_SUPPROT_HBBTV :
				LOG_TRACE('----------HBB Tv Ready')
				self.mDataCache.Splash_StartAndStop( 0 )
				self.mHBBTVReady = False

			self.mDataCache.Teletext_NotifyHide( )
			self.mDataCache.LoadVolumeAndSyncMute( True )
			if WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_NULLWINDOW :
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).CheckSubTitle( )
			#self.SetSingleWindowPosition( WinMgr.WIN_ID_NULLWINDOW * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID )
			LOG_TRACE( '----------ElisEventTTXClosed' )

		elif aEvent.getName( ) == ElisEventPVRManagerUpdate.getName( ) :
			#msgLine = MR_LANG( 'New channels have been loaded from PVR manager%s Press OK to continue updating your channel list' )% NEW_LINE
			if aEvent.mResult == ElisEnum.E_UPDATE_START :
				msgHead = MR_LANG( 'Update Channels' )
				msgLine = MR_LANG( 'Loading new channels...' )
				xbmc.executebuiltin( 'Notification(%s, %s, 5000, DefaultIconInfo.png)' % ( msgHead, msgLine ) )
				xbmc.executebuiltin( "ActivateWindow(busydialog)" )
				self.IsStartChannelLoad = True
				thread = threading.Timer( 180, self.StopLoading )
				thread.start( )

			elif aEvent.mResult == ElisEnum.E_UPDATE_SUCCESS :
				self.IsStartChannelLoad = False
				xbmc.executebuiltin( "Dialog.Close(busydialog)" )
				#dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				#dialog.SetDialogProperty( MR_LANG( 'Update Channels' ), MR_LANG( 'Your system must be restarted%s in order to complete the update' )% NEW_LINE )
				#dialog.SetAutoCloseTime( 10 )
				#dialog.doModal( )
				mHead = MR_LANG( 'Please wait' )
				mLine = MR_LANG( 'System is restarting' ) + '...'
				xbmc.executebuiltin( 'Notification( %s, %s, 3000, DefaultIconInfo.png )'% ( mHead, mLine ) )
				time.sleep( 2 )
				self.mDataCache.System_Reboot( )

			else :
				self.IsStartChannelLoad = False
				xbmc.executebuiltin( "Dialog.Close(busydialog)" )
				if aEvent.mResult == ElisEnum.E_UPDATE_FAILED_BY_RECORD :
					msgLine = MR_LANG( 'Please try again after stopping the recordings' )
				elif aEvent.mResult == ElisEnum.E_UPDATE_FAILED_BY_TIMER :
					msgLine = MR_LANG( 'Please try again after deleting your timers first' )

				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( msgHead, msgLine )
				dialog.doModal( )

		elif aEvent.getName( ) == ElisEventUSBNotifyDetach.getName( ) :
			self.mDataCache.SetUSBAttached( False )
			thread = threading.Timer( 0.1, self.ShowAttatchDialog, [False] )
			thread.start( )

			if E_SUPPORT_EXTEND_RECORD_PATH :
				if WinMgr.GetInstance( ).GetLastWindowID( ) != WinMgr.WIN_ID_ARCHIVE_WINDOW and \
				   WinMgr.GetInstance( ).GetLastWindowID( ) != WinMgr.WIN_ID_CONFIGURE :
					self.mDataCache.Record_GetNetworkVolume( )

		elif aEvent.getName( ) == ElisEventUSBNotifyAttach.getName( ) :
			self.mDataCache.SetUSBAttached( True )
			thread = threading.Timer( 0.1, self.ShowAttatchDialog, [True] )
			thread.start( )

			if E_SUPPORT_EXTEND_RECORD_PATH :
				if WinMgr.GetInstance( ).GetLastWindowID( ) != WinMgr.WIN_ID_ARCHIVE_WINDOW and \
				   WinMgr.GetInstance( ).GetLastWindowID( ) != WinMgr.WIN_ID_CONFIGURE :
					self.mDataCache.Record_GetNetworkVolume( )

		elif aEvent.getName( ) == ElisEventViewTimerStatus.getName( ) :
			LOG_TRACE( '-----------------------event name[%s]'% aEvent.getName( ) )
			thread = threading.Timer( 0.1, self.ChannelChangedByRecord, [aEvent] )
			thread.start( )

		elif aEvent.getName( ) == ElisEventChannelDBUpdate.getName( ) :
			if aEvent.mUpdateType == 0 :
				#ToDO : All updated db, reload channelList
				pass

			elif aEvent.mUpdateType == 1 :
				self.mDataCache.UpdateChannelByDBUpdate( aEvent.mChannelNo, aEvent.mServiceType )

		#for HBBTV
		elif E_SUPPROT_HBBTV == True :
			LOG_TRACE("HBBTEST 11111111111111111 %s" % aEvent.getName( ) )
			if aEvent.getName( ) == ElisEventExternalMediaPlayerStart.getName( ) :
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).HbbTV_MediaPlayerStart( aEvent.mUrl )

			elif aEvent.getName( ) == ElisEventExternalMediaPlayerSetSpeed.getName( ) :
				#ToDO
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).HbbTV_MediaPlayerSetSpeed( 0 )				
		
			elif aEvent.getName( ) == ElisEventExternalMediaPlayerSeekStream.getName( ) :
				#ToDO
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).HbbTV_MediaPlayerSeek( aEvent.mSeekPosition )
		
			elif aEvent.getName( ) == ElisEventExternalMediaPlayerStopPlay.getName( ) :
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).HbbTV_MediaPlayerStop(  )
				
			elif aEvent.getName() == ElisEventHBBTVReady.getName() :
				LOG_TRACE( 'HbbTV TEST' )
				#HBBTV			
				#This event must be received from global event.
				if aEvent.mReady == 1 :
					LOG_TRACE("Now new AIT is ready, HBBTV Browser ready")
					self.mDataCache.SetHbbTVEnable( True )
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).HbbTV_ShowRedButton( )

				else :
					LOG_TRACE( 'HbbTV Disable Event' )
					self.mDataCache.SetHbbTVEnable( False )
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).HbbTV_HideRedButton( )	


	def StopLoading( self ) :
		if self.IsStartChannelLoad :
			xbmc.executebuiltin( "Dialog.Close(busydialog)" )
			self.IsStartChannelLoad = False


	def AsyncHddFull( self ) :
		keyblock = 0
		currentWinid = self.GetCurrentWindowIdForStanByClose( )
		if currentWinid == WinMgr.WIN_ID_LIVE_PLATE or currentWinid == WinMgr.WIN_ID_TIMESHIFT_PLATE :
			keyblock = 1
		self.mIsHddFullDialogOpened = True
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Recording stopped due to insufficient disk space' ) )
		dialog.SetStayCount( keyblock )
		dialog.doModal( )

		self.mIsHddFullDialogOpened = False


	def AsyncStandbyPowerON( self ) :
		#default mute off
		if not self.mDataCache.Channel_GetInitialBlank( ) :
			self.mDataCache.Player_AVBlank( False )

		mute = self.mCommander.Player_GetMute( )
		if not self.mDataCache.Get_Player_AVBlank( ) and mute :
			xbmc.executebuiltin( 'xbmc.Action(mute)' )

		self.mDataCache.InitBookmarkButton( )
		WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetPincodeRequest( True )
		self.CheckParentLock( E_PARENTLOCK_INIT, None, True )
		if ElisPropertyEnum( 'First Installation', self.mCommander ).GetProp( ) == 0x2b :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_FIRST_INSTALLATION, WinMgr.WIN_ID_MAINMENU )
		else :
			xbmc.executebuiltin( 'xbmc.Action(contextmenu)' )


	def AsyncPowerSave( self ) :
		self.mIsDialogOpend = True
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_AUTO_POWER_DOWN )

		if self.mCommander.Teletext_IsShowing( ) :
			self.mCommander.Teletext_Hide( )
			dialog.doModal( )
			self.mCommander.Teletext_Show( )

		elif self.mDataCache.Subtitle_IsShowing( ) :
			self.mDataCache.Subtitle_Hide( )
			dialog.doModal( )
			self.mDataCache.Subtitle_Show( )

		else :
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).HbbTV_HideBrowser( )
			dialog.doModal( )

		self.mIsDialogOpend = False


	def GetRecordingInfo( self ) :
		labelInfo = '%s%s'% ( MR_LANG( 'Reloading channel list' ), ING )
		try:
			isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )
			#LOG_TRACE('isRunRecCount[%s]'% isRunRec)

			if isRunRec == 1 :
				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 0 )
				labelInfo = '%s %s'% ( recInfo.mChannelNo, recInfo.mChannelName )

			elif isRunRec == 2 :
				recInfo1 = self.mDataCache.Record_GetRunningRecordInfo( 0 )
				recInfo2 = self.mDataCache.Record_GetRunningRecordInfo( 1 )
				if recInfo1.mStartTime > recInfo2.mStartTime :
					labelInfo = '%s %s'% ( recInfo1.mChannelNo, recInfo1.mChannelName )
				else :
					labelInfo = '%s %s'% ( recInfo2.mChannelNo, recInfo2.mChannelName )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		return labelInfo


	def SendLocalOffsetToXBMC( self ) :
		LOG_TRACE( '--------------' )
		self.mDataCache.LoadTime( )
		localOffset = self.mDataCache.Datetime_GetLocalOffset( )		
		XBMC_SetLocalOffset( localOffset )


	def CheckParentLock( self, aCmd = E_PARENTLOCK_EIT, aEvent = None, aForce = False ) :
		if WinMgr.GetInstance( ).GetLastWindowID( ) not in PARENTLOCK_CHECKWINDOW :
			LOG_TRACE( '--------parentLock check pass winid[%s]'% WinMgr.GetInstance( ).GetLastWindowID( ) )
			return

		if not aForce :
			channelList = self.mDataCache.Channel_GetList( )
			if not channelList or len( channelList ) < 1 :
				LOG_TRACE( '--------parentLock check pass ChannelList None' )
				return


		if aCmd == E_PARENTLOCK_INIT :
			#default blank
			self.mDataCache.Epgevent_GetPresent( )
			iEPG = self.mDataCache.GetEpgeventCurrent( )
			iChannel = self.mDataCache.Channel_GetCurrent( )
			pChannel = self.mDataCache.Channel_GetCurrentByPlaying( )
			if pChannel :
				LOG_TRACE('---------------------parentLock ch[%s %s] mLocked[%s] parentLock[%s] epg[%s] pch[%s %s]'% ( iChannel.mNumber, iChannel.mName, iChannel.mLocked, self.mDataCache.GetParentLock( ), iEPG, pChannel.mNumber, pChannel.mName )  )
			else :
				LOG_TRACE('---------------------parentLock ch[%s %s] mLocked[%s] parentLock[%s] epg[%s] pch[None]'% ( iChannel.mNumber, iChannel.mName, iChannel.mLocked, self.mDataCache.GetParentLock( ), iEPG )  )

			#if not pChannel or not iChannel or \
			#   pChannel.mSid != iChannel.mSid or pChannel.mTsid != iChannel.mTsid or pChannel.mOnid != iChannel.mOnid :
				self.mDataCache.SetParentLock( True )
				self.mDataCache.SetParentLockByEPG( )
				self.mDataCache.SetAgeGurantee( )
				if iChannel and iChannel.mLocked or self.mDataCache.GetParentLock( ) :
					if not self.mDataCache.Get_Player_AVBlank( ) :

						if self.mDataCache.GetParentLockPass( ) :
							self.mDataCache.SetParentLock( False )
							self.mDataCache.SetParentLockPass( False )
							LOG_TRACE( '--------parentLock check pass mediaCenter out' )
							return
						else :
							self.mDataCache.Player_AVBlank( True )

					if ( not self.mDataCache.GetPincodeDialog( ) ) :
						if ( iChannel and ( not iChannel.mLocked ) ) :
							aCmd = E_PARENTLOCK_EIT
						self.mDataCache.SetPincodeDialog( True )
						thread = threading.Timer( 0.1, self.ShowPincodeDialog, [aCmd] )
						thread.start( )

				else :
					if self.mDataCache.Get_Player_AVBlank( ) or aForce == True:
						LOG_TRACE('----------------11')
						self.mDataCache.Player_AVBlank( False )
						self.mDataCache.LoadVolumeBySetGUI( )

			#else :
			#	if self.mDataCache.Get_Player_AVBlank( ) or aForce == True:
			#		LOG_TRACE('----------------22')
			#		self.mDataCache.Player_AVBlank( False )
			#		self.mDataCache.LoadVolumeBySetGUI( )

		elif aCmd == E_PARENTLOCK_EIT :
			iEPG = self.mDataCache.GetEpgeventCurrent( )
			if iEPG and iEPG.mError == 0 :
				LOG_TRACE('EIT-id[%s] oldId[%s] currentEpg[%s] age[%s] limit[%s] gurantee[%s]'% ( aEvent.mEventId, self.mEventId, iEPG.mEventName, iEPG.mAgeRating, self.mDataCache.GetPropertyAge( ), self.mDataCache.GetAgeGurantee( ) ) )
			else :
				LOG_TRACE('EIT-id[%s] oldId[%s] currentEpg[%s]'% ( aEvent.mEventId, self.mEventId, iEPG ) )

			self.mDataCache.CheckExpireByParentLock( )
			if not iEPG or self.mEventId != aEvent.mEventId :
				self.mEventId = aEvent.mEventId
				self.mDataCache.Epgevent_GetPresent( )

				#is Age? agerating check
				if self.mDataCache.GetParentLock( ) :
					if not self.mDataCache.GetPincodeDialog( ) :
						LOG_TRACE('---------------------parentLock')
						self.mDataCache.SetPincodeDialog( True )
						thread = threading.Timer( 0.1, self.ShowPincodeDialog, [aCmd] )
						thread.start( )

				else :
					iChannel = self.mDataCache.Channel_GetCurrent( )
					if iChannel and ( not iChannel.mLocked ) and self.mDataCache.Get_Player_AVBlank( ) :
						LOG_TRACE( '--------------- Release parentLock' )
						self.mDataCache.Player_AVBlank( False )
						self.mDataCache.LoadVolumeBySetGUI( )


	def ShowPincodeDialog( self, aCmd ) :
		if self.mDataCache.GetMediaCenter( ) == True :
			self.mDataCache.SetPincodeDialog( False )
			LOG_TRACE( 'No popup in MediaCenter' )
			return

		LOG_TRACE('--------blank m/w[%s] mbox[%s] lockDialog[%s]'% ( self.mDataCache.Channel_GetInitialBlank( ), self.mDataCache.Get_Player_AVBlank(), self.mDataCache.GetPincodeDialog( ) ) )
		if not self.mDataCache.Get_Player_AVBlank( ) :
			self.mDataCache.Player_AVBlank( True )

		if WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_MAINMENU :
			self.mDataCache.SetPincodeDialog( False )
			LOG_TRACE( 'No popup in MainMenu' )
			return

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_INPUT_PINCODE )
		dialog.SetTitleLabel( MR_LANG( 'Enter PIN Code' ) )
		dialog.SetCheckStatus( E_CHECK_PARENTLOCK )
		dialog.doModal( )

		if WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_NULLWINDOW or \
		   WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_LIVE_PLATE or \
		   WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_TIMESHIFT_PLATE or \
		   WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :

			if dialog.GetNextAction( ) == dialog.E_TUNE_NEXT_CHANNEL :
				xbmc.executebuiltin( 'xbmc.Action(PageUp)' )
				self.mDataCache.LoadVolumeBySetGUI( )

			elif dialog.GetNextAction( ) == dialog.E_TUNE_PREV_CHANNEL :
				xbmc.executebuiltin( 'xbmc.Action(PageDown)' )
				self.mDataCache.LoadVolumeBySetGUI( )

			elif dialog.GetNextAction( ) == dialog.E_SHOW_EPG_WINDOW :
				xbmc.executebuiltin( 'xbmc.Action(info)' )

			elif dialog.GetNextAction( ) == dialog.E_SHOW_ARCHIVE_WINDOW :
				#from pvr.HiddenTestMgr import SendCommand
				#SendCommand( 'VKEY_ARCHIVE' )
				xbmc.executebuiltin( 'xbmc.Action(DVBArchive)' )

			elif dialog.GetNextAction( ) == dialog.E_TUNE_TVRADIO_TOGGLE :
				xbmc.executebuiltin( 'xbmc.Action(DVBTVRadio)' )

		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			if aCmd == E_PARENTLOCK_EIT :
				self.mDataCache.SetParentLockByEPG( )
				iEPG = self.mDataCache.GetEpgeventCurrent( )
				if iEPG and iEPG.mError == 0 and self.mDataCache.GetAgeGurantee( ) < iEPG.mAgeRating :
					self.mDataCache.SetAgeGurantee( iEPG.mAgeRating )

			self.mDataCache.SetParentLock( False )
			if self.mDataCache.Get_Player_AVBlank( ) :
				self.mDataCache.Player_AVBlank( False )
				self.mDataCache.LoadVolumeBySetGUI( )

		self.mDataCache.SetPincodeDialog( False )


	def CamInsertRemove( self, aInserted ) :
		if aInserted :
			xbmc.executebuiltin( 'Notification(%s, %s, 3000, DefaultIconInfo.png)' % ( MR_LANG( 'Attention' ), MR_LANG( 'CAM initialized' ) ) )
			self.mCommander.Cicam_EnterMMI( CAS_SLOT_NUM_1 )
		else :
			xbmc.executebuiltin( 'Notification(%s, %s, 3000, DefaultIconInfo.png)' % ( MR_LANG( 'Attention' ), MR_LANG( 'CAM removed' ) ) )
			try :
				self.mDialogShowParental.close( )
				self.mDialogShowEvent.close( )
			except Exception, ex :
				LOG_TRACE( 'except close dialog' )


	def ShowAttatchDialog( self, aAttatch = False ) :
		#if xbmcgui.getCurrentWindowDialogId( ) != 9999 :
		#	LOG_TRACE( 'Another dialog aready popuped!!' )
		#	return

		msg = MR_LANG( 'Connected' )
		if not aAttatch :
			msg = MR_LANG( 'Removed' )

		xbmc.executebuiltin( 'Notification(%s, %s, 3000, USB.png)' % ( MR_LANG( 'USB Device' ), msg ) )


	def ShowEventDialog( self, aEvent ) :
		self.mDialogShowEvent.SetProperty( aEvent )
		self.mDialogShowEvent.doModal( )
		ret = self.mDialogShowEvent.GetSelectedIndex( )
		if ret >= 0 :
			self.mCommander.Cicam_SendMenuAnswer( aEvent.mSlotNo, ret + 1 )
		else :
			self.mCommander.Cicam_SendMenuAnswer( aEvent.mSlotNo, 0 )


	def ShowParentalDialog( self, aEvent ) :
		self.mDialogShowParental.SetDialogProperty( '%s' % aEvent.mEnqData.mText, '', aEvent.mEnqData.mAnswerTextLen, aEvent.mEnqData.mBlindAnswer )
		self.mDialogShowParental.doModal( )

		if self.mDialogShowParental.IsOK( ) == E_DIALOG_STATE_YES :
			self.mCommander.Cicam_SendEnqAnswer( aEvent.mSlotNo, 1, self.mDialogShowParental.GetString( ), len( self.mDialogShowParental.GetString( ) ) )
		else :
			self.mCommander.Cicam_SendEnqAnswer( aEvent.mSlotNo, 0, 'None', 4 )


	def ShowPIPDialog( self ) :
		self.mIsShowPIPDialog = True
		DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).PIP_SetPositionSync( )
		DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).doModal( )
		self.mIsShowPIPDialog = False


	def ChannelChangedByRecord( self, aEvent ) :
		if not aEvent :
			LOG_TRACE('no event data')
			return

		status = self.mDataCache.Player_GetStatus( )
		if aEvent.getName( ) == ElisEventViewTimerStatus.getName( ) :
			ret = self.CheckViewTimer( aEvent )
			if ret :
				LOG_TRACE( 'success, change channel by view timer' )
				if status.mMode != ElisEnum.E_MODE_LIVE :
					self.mDataCache.Player_Stop( )
				self.mDataCache.Channel_SetCurrentByUpdateSync( aEvent.mChannelNo, aEvent.mServiceType )
				self.CheckTunablePIP( -1, True )
			else :
				LOG_TRACE( 'Alarm view timer' )
				return

		if status.mMode != ElisEnum.E_MODE_TIMESHIFT :
			self.mDataCache.Player_Stop( )

		zappingMode = self.mDataCache.Zappingmode_GetCurrent( )
		if zappingMode and zappingMode.mServiceType != aEvent.mServiceType :
			zappingMode.mServiceType = aEvent.mServiceType
			self.mDataCache.SetChannelReloadStatus( True )
			self.mDataCache.Channel_ResetOldChannelList( )
			self.mDataCache.Zappingmode_SetCurrent( zappingMode )
			self.mDataCache.LoadZappingmode( )
			self.mDataCache.LoadZappingList( )
			self.mDataCache.LoadChannelList( )
			self.mDataCache.Channel_GetAllChannels( zappingMode.mServiceType.mServiceType, False )
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW ).SetRadioScreen( )

		self.mDataCache.Channel_SetCurrentByUpdateSync( aEvent.mChannelNo, aEvent.mServiceType )
		if self.mDataCache.GetStanbyStatus( ) == ElisEnum.E_STANDBY_POWER_ON :
			self.mDataCache.Player_AVBlank( True )
			self.CheckParentLock( E_PARENTLOCK_INIT, None, True )
			#if WinMgr.GetInstance( ).GetLastWindowID( ) in PARENTLOCK_CHECKWINDOW :
			#	self.mDataCache.Channel_SetCurrentByUpdateSync( aEvent.mChannelNo, aEvent.mServiceType )
			if WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_NULLWINDOW :
				xbmc.executebuiltin( 'xbmc.Action(contextmenu)' )
			#self.mDataCache.Channel_SetCurrent( aEvent.mChannelNo, aEvent.mServiceType )

		LOG_TRACE('event[%s] tune[%s] type[%s]'% ( aEvent.getName( ), aEvent.mChannelNo, aEvent.mServiceType ) )


	def CheckViewTimer( self, aEvent ) :
		viewResult = False
		if aEvent.mResult == ElisEnum.E_VIEWTIMER_SUCCESS :
			viewResult = True
			if self.mDataCache.GetMediaCenter( ) == True :
				self.mDataCache.SetAlarmByViewTimer( True )

		elif aEvent.mResult == ElisEnum.E_VIEWTIMER_WAIT :
			if self.mDataCache.GetMediaCenter( ) == True :
				LOG_TRACE( 'No popup in MediaCenter' )
				return

			timer = self.mDataCache.Timer_GetById( aEvent.mTimerID )
			if timer and timer.mTimerType == ElisEnum.E_ITIMER_VIEW :
				tempDate = '%s'% ( TimeToString( timer.mStartTime, TimeFormatEnum.E_AW_DD_MM_YYYY ) )						
				tempDuration = '%s'% TimeToString( timer.mStartTime, TimeFormatEnum.E_HH_MM )
				mDate = '[%s %s]'% ( tempDate, tempDuration )

				channel = self.mDataCache.GetChannelByIDs( timer.mSid, timer.mTsid, timer.mOnid )
				iChNumber = timer.mChannelNo
				if channel :
					iChNumber = channel.mNumber
					if E_V1_2_APPLY_PRESENTATION_NUMBER :
						iChNumber = self.mDataCache.CheckPresentationNumber( channel )

				mName = '%04d %s'% ( iChNumber, timer.mName )
				if timer.mName and len( timer.mName ) > 20 :
					mName = '%04d %s%s'% ( iChNumber, timer.mName[:20], ING )

				line1 = '[COLOR orange]%s %s[/COLOR]'% ( mName, mDate )
				line2 = '%s'% ( MR_LANG( 'Do you want to change the channel %s minutes later?' ) % '5' )

				mHead = MR_LANG( 'Timer Notification' )
				mLine = '%s%s%s'% ( line1, NEW_LINE, line2 )

				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( mHead, mLine, True )
				dialog.SetAutoCloseProperty( True, 20, True )
				dialog.doModal( )

				ret = dialog.IsOK( )
				if ret == E_DIALOG_STATE_NO :
					self.mDataCache.Timer_DeleteTimer( timer.mTimerId )
					LOG_TRACE( 'delete timer[%s]'% timer.mTimerId )

		elif aEvent.mResult == ElisEnum.E_VIEWTIMER_SOON :
			if self.mDataCache.GetMediaCenter( ) == True :
				LOG_TRACE( 'No alarm in MediaCenter' )
				return

			mHead = MR_LANG( 'Timer Notification' )
			mLine = MR_LANG( 'The channel will be changed %s min later' )% 1
			xbmc.executebuiltin( 'Notification(%s, %s, 3000, DefaultIconInfo.png)'% ( mHead, mLine ) )

		else :
			# E_VIEWTIMER_FAILED_BY_RECORD
			LOG_TRACE( 'View timer failed to change the channel' )

		return viewResult


	def StanByClose( self ) :
		if xbmc.Player( ).isPlaying( ) :
			xbmc.Player( ).stop( )

		curreuntWindowId = self.GetCurrentWindowIdForStanByClose( )
		previousWindowId = 1234

		while curreuntWindowId != WinMgr.WIN_ID_NULLWINDOW or xbmcgui.getCurrentWindowDialogId( ) != 9999 :
			if curreuntWindowId != previousWindowId :
				xbmc.executebuiltin( 'xbmc.Action(PreviousMenu)' )
				if xbmcgui.getCurrentWindowDialogId( ) == 9999 :
					previousWindowId = curreuntWindowId

			curreuntWindowId = self.GetCurrentWindowIdForStanByClose( )
			time.sleep( 0.3 )

		self.mDataCache.SetStanbyClosing( False )
		DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).PIP_Stop( True )


	def GetCurrentWindowIdForStanByClose( self ) :
		if self.mDataCache.GetRootWindowId( ) == xbmcgui.getCurrentWindowId( ) :
			return WinMgr.GetInstance( ).GetLastWindowID( )
		else :
			return xbmcgui.getCurrentWindowId( )	


	def CheckLinkageService( self ) :
		epg = self.mDataCache.GetEpgeventCurrent( )
		if epg :
			#epg.printdebug()		
			#hasLinkageService = self.mDataCache.GetLinkageService(  )

			#if hasLinkageService !=  epg.mHasLinkageService : #if linkage service changed
			if epg.mHasLinkageService : #if linkage service changed
				self.mDataCache.SetLinkageService( epg.mHasLinkageService )
				LOG_TRACE('LAEL98 TEST')

				if WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_NULLWINDOW or  \
					WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_LIVE_PLATE :
					LOG_TRACE('LAEL98 TEST')				
					WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).GetLastWindowID( )  ).UpdateLinkageService( )


	def CheckTunablePIP( self, aEvent = None, aForce = False ) :
		# 1. isStart PIP ?
		if not self.mDataCache.PIP_GetStatus( ) :
			return

		if aEvent == ElisEnum.E_CC_PIP_FAILED_TUNE_NOT_AVAILABLE :
			iChannel = self.mDataCache.Channel_GetCurrent( )
			DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).TuneChannelByExternal( iChannel )
			return

		# 2. isRecording ?
		if not aForce and self.mDataCache.GetChangeDBTableChannel( ) != E_TABLE_ZAPPING :
			return

		oldCh = self.mDataCache.Channel_GetOldChannel( )
		curCh = self.mDataCache.Channel_GetCurrent( )

		if not oldCh or ( not curCh ) :
			return

		#LOG_TRACE( 'zappingResult--old[%s %s] cur[%s %s]'% ( oldCh.mNumber, oldCh.mName, curCh.mNumber, curCh.mName ) )

		# 3. different tp zapping ?
		if oldCh.mCarrier.mDVBS.mSatelliteLongitude != curCh.mCarrier.mDVBS.mSatelliteLongitude or \
		   oldCh.mCarrier.mDVBS.mSatelliteBand != curCh.mCarrier.mDVBS.mSatelliteBand or \
		   oldCh.mCarrier.mDVBS.mFrequency != curCh.mCarrier.mDVBS.mFrequency or \
		   oldCh.mCarrier.mDVBS.mSymbolRate != curCh.mCarrier.mDVBS.mSymbolRate or \
		   oldCh.mCarrier.mDVBS.mPolarization != curCh.mCarrier.mDVBS.mPolarization :
			self.mDataCache.PIP_SetTunableList( )
			LOG_TRACE( 'different TP zapping, refresh TunableList' )


	def DoXBMCEvent( self, aEvent  ) :
		#aEvent.printdebug()
		if aEvent.mName == "OnPlay" :
			LOG_TRACE( 'XBMCEvent OnPlay' )
			liveWindow = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_NULLWINDOW )			
			if aEvent.mValue == "True" :
				if liveWindow.mHbbTVShowing != True :
					WinMgr.GetInstance( ).GetCurrentWindow( ).SetVideoRestore( )
					status = self.mDataCache.Player_GetStatus( )
					if status.mMode != ElisEnum.E_MODE_LIVE :
						self.mDataCache.Player_Stop( )

				if liveWindow.mHbbTVShowing != True :
					liveWindow.SetMediaCenter( True )
					if liveWindow.mWinId == xbmcgui.getCurrentWindowId( ) :
						xbmc.executebuiltin( 'ActivateWindow(Home)' )

				xbmc.executebuiltin( 'PlayerControl(enplay)', True )

			elif aEvent.mValue == "False" :
				if liveWindow.mHbbTVShowing == True :
					pass
				else :
					xbmc.executebuiltin( 'ActivateWindow(busydialog)' )
					liveWindow.CheckMediaCenter()
					DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).PIP_Check( E_PIP_STOP )
					if self.mDataCache.PIP_GetSwapStatus( ) :
						self.mDataCache.PIP_SwapWindow( False )
					xbmc.executebuiltin( 'Dialog.Close(busydialog)' )

		elif aEvent.mName == "OnVolumeChanged" :
			volumelist  = aEvent.mValue.split(':')
			mute = int( volumelist[0] )
			volume = int( volumelist[1] )
			mw_mute = self.mCommander.Player_GetMute( )
			mw_volume = self.mCommander.Player_GetVolume( )

			LOG_TRACE( "Mute=%d:%d Volume=%d:%d" % ( mute, mw_mute, volume, mw_volume ) )

			if mute != mw_mute :
				self.mCommander.Player_SetMute( mute )
			elif volume != mw_volume :
				self.mCommander.Player_SetVolume( volume )

