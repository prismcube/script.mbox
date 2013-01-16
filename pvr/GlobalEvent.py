from pvr.gui.WindowImport import *
import pvr.DataCacheMgr
import pvr.ElisMgr


AUTOPOWERDOWN_EXCEPTWINDOW = [ WinMgr.WIN_ID_SYSTEM_UPDATE, WinMgr.WIN_ID_FIRST_INSTALLATION ]
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
		self.mIsHddFullDialogOpened = False
		self.mEventId = None
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.SendLocalOffsetToXBMC( )		


	@classmethod
	def GetName( cls ) :
		return cls.__name__


	def onEvent( self, aEvent ) :
		if not WinMgr.gWindowMgr :
			return

		if aEvent.getName( ) == ElisEventCurrentEITReceived.getName( ) :
			channel = self.mDataCache.Channel_GetCurrent( )
			if not channel or channel.mError != 0 :
				return -1

			if channel.mSid != aEvent.mSid or channel.mTsid != aEvent.mTsid or channel.mOnid != aEvent.mOnid :
				#LOG_TRACE('ignore event, same event')
				return -1

			iEPG = self.mDataCache.GetEpgeventCurrent( )
			if iEPG and iEPG.mError == 0 :
				LOG_TRACE('EIT-id[%s] oldId[%s] currentEpg[%s] age[%s] limit[%s]'% ( aEvent.mEventId, self.mEventId, iEPG.mEventName, iEPG.mAgeRating, self.mDataCache.GetPropertyAge( ) ) )
			else :
				LOG_TRACE('EIT-id[%s] oldId[%s] currentEpg[%s]'% ( aEvent.mEventId, self.mEventId, iEPG ) )

			if not iEPG or self.mEventId != aEvent.mEventId :
				self.mEventId = aEvent.mEventId
				self.mDataCache.Epgevent_GetPresent( )
				#is Age? agerating check
				if ( not self.mDataCache.GetPincodeDialog( ) ) and self.mDataCache.GetParentLock( ) :
					LOG_TRACE('---------------------parentLock')
					self.mDataCache.SetPincodeDialog( True )
					thread = threading.Timer( 0.1, self.ShowPincodeDialog )
					thread.start( )


		if aEvent.getName( ) == ElisEventTimeReceived.getName( ) :
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

		elif aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
			if aEvent.mType == ElisEnum.E_EOF_END :
				if WinMgr.GetInstance( ).GetLastWindowID( ) != WinMgr.WIN_ID_NULLWINDOW and \
				   WinMgr.GetInstance( ).GetLastWindowID( ) != WinMgr.WIN_ID_TIMESHIFT_PLATE :
					LOG_TRACE( 'CHECK onEVENT[%s] stop'% aEvent.getName( ) )
					self.mDataCache.Player_Stop( )

		elif aEvent.getName( ) == ElisEventChannelChangeStatus( ).getName( ) :
			if aEvent.mStatus == ElisEnum.E_CC_FAILED_SCRAMBLED_CHANNEL :
				WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).GetLastWindowID( ) ).setProperty( 'Signal', 'Scramble' )
				self.mDataCache.Frontdisplay_Resolution( )
				self.mDataCache.SetLockedState( ElisEnum.E_CC_FAILED_SCRAMBLED_CHANNEL )
			elif aEvent.mStatus == ElisEnum.E_CC_FAILED_NO_SIGNAL :
				WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).GetLastWindowID( ) ).setProperty( 'Signal', 'False' )
				self.mDataCache.Frontdisplay_Resolution( )
				self.mDataCache.SetLockedState( ElisEnum.E_CC_FAILED_NO_SIGNAL )
			else :
				WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).GetLastWindowID( ) ).setProperty( 'Signal', 'True' )
				self.mDataCache.SetLockedState( ElisEnum.E_CC_SUCCESS )
				self.mDataCache.SetParentLock( True )
				self.mDataCache.Epgevent_GetPresent( )


		elif aEvent.getName( ) == ElisEventVideoIdentified( ).getName( ) :
			hdmiFormat = ElisPropertyEnum( 'HDMI Format', self.mCommander ).GetPropString( )
			if hdmiFormat == 'Automatic' :
				iconIndex = ElisEnum.E_ICON_1080i
				if aEvent.mVideoHeight <= 576 :
					iconIndex = -1
				elif aEvent.mVideoHeight <= 720 :
					iconIndex = ElisEnum.E_ICON_720p

				self.mDataCache.Frontdisplay_Resolution( iconIndex )

		elif aEvent.getName( ) == ElisEventPowerSave( ).getName( ) :
			if WinMgr.GetInstance( ).GetLastWindowID( ) not in AUTOPOWERDOWN_EXCEPTWINDOW :
				if self.mIsDialogOpend == False :
					thread = threading.Timer( 0.3, self.AsyncPowerSave )
					thread.start( )
			else :
				LOG_TRACE( 'Skip auto power down : %s' ) % WinMgr.GetInstance( ).GetLastWindowID( )

		elif aEvent.getName( ) == ElisEventChannelChangedByRecord.getName( ) :
			if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_TIMESHIFT :
				self.mDataCache.Player_Stop( )
			self.mDataCache.Player_AVBlank( False )
			#self.mDataCache.Channel_SetCurrent( aEvent.mChannelNo, aEvent.mServiceType )
			LOG_TRACE('event[%s] tune[%s] type[%s]'% ( aEvent.getName( ), aEvent.mChannelNo, aEvent.mServiceType ) )

		elif aEvent.getName( ) == ElisEventShutdown.getName( ) :
			#LOG_TRACE('-----------shutdown[%s] blank[%s]'% ( aEvent.mType, self.mDataCache.Channel_GetInitialBlank( ) ) )
			if aEvent.mType == ElisEnum.E_STANDBY_POWER_ON :
				thread = threading.Timer( 0.3, self.AsyncStandbyPowerON )
				thread.start( )
				return


	def AsyncHddFull( self ) :
		self.mIsHddFullDialogOpened = True
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Recording stopped due to insufficient disk space' ) )
		dialog.SetStayCount( 1 )
		dialog.doModal( )

		self.mIsHddFullDialogOpened = False


	def AsyncStandbyPowerON( self ) :
		while WinMgr.GetInstance( ).GetLastWindowID( ) > WinMgr.WIN_ID_NULLWINDOW :
			xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )
			time.sleep( 1 )

		time.sleep( 1 )
		WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetPincodeRequest( True )
		xbmc.executebuiltin( 'xbmc.Action(contextmenu)' )


	def AsyncPowerSave( self ) :
		self.mIsDialogOpend = True
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_AUTO_POWER_DOWN )

		if self.mCommander.Teletext_IsShowing( ) :
			self.mCommander.Teletext_Hide( )
			dialog.doModal( )
			self.mCommander.Teletext_Show( )
		#elif self.mCommander.Subtitle_IsShowing( ) :
		#TODO
		else :
			if WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_NULLWINDOW :
				self.mCommander.AppHBBTV_Ready( 0 )
			dialog.doModal( )
			if WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_NULLWINDOW :
				self.mCommander.AppHBBTV_Ready( 1 )
			
		self.mIsDialogOpend = False


	def GetRecordingInfo( self ) :
		labelInfo = MR_LANG( 'Reloading channel list...' )
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


	def ShowPincodeDialog( self ) :
		LOG_TRACE('--------blank m/w[%s] mbox[%s]'% ( self.mDataCache.Channel_GetInitialBlank( ), self.mDataCache.Get_Player_AVBlank() ) )
		if not self.mDataCache.Get_Player_AVBlank( ) :
			self.mDataCache.Player_AVBlank( True )
		LOG_TRACE('--------blank m/w[%s] mbox[%s]'% ( self.mDataCache.Channel_GetInitialBlank( ), self.mDataCache.Get_Player_AVBlank() ) )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_INPUT_PINCODE )
		dialog.SetTitleLabel( MR_LANG( 'Enter your PIN code' ) )
		dialog.doModal( )

		if WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_NULLWINDOW or \
		   WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_LIVE_PLATE or \
		   WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_TIMESHIFT_PLATE or \
		   WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :

			if dialog.GetNextAction( ) == dialog.E_TUNE_NEXT_CHANNEL :
				xbmc.executebuiltin( 'xbmc.Action(PageUp)' )

			elif dialog.GetNextAction( ) == dialog.E_TUNE_PREV_CHANNEL :
				xbmc.executebuiltin( 'xbmc.Action(PageDown)' )

			elif dialog.GetNextAction( ) == dialog.E_SHOW_EPG_WINDOW :
				xbmc.executebuiltin( 'xbmc.Action(info)' )

			elif dialog.GetNextAction( ) == dialog.E_SHOW_ARCHIVE_WINDOW :
				from pvr.HiddenTestMgr import SendCommand
				SendCommand( 'VKEY_ARCHIVE' )

		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			self.mDataCache.SetParentLock( False )
			if self.mDataCache.Get_Player_AVBlank( ) :
				self.mDataCache.Player_AVBlank( False )

		self.mDataCache.SetPincodeDialog( False )

