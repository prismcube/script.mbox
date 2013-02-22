from pvr.gui.WindowImport import *
import pvr.DataCacheMgr
import pvr.ElisMgr


AUTOPOWERDOWN_EXCEPTWINDOW = [ WinMgr.WIN_ID_SYSTEM_UPDATE, WinMgr.WIN_ID_FIRST_INSTALLATION ]
PARENTLOCK_CHECKWINDOW = [ 
	WinMgr.WIN_ID_NULLWINDOW,
	WinMgr.WIN_ID_MAINMENU,
	WinMgr.WIN_ID_CHANNEL_LIST_WINDOW,
	WinMgr.WIN_ID_LIVE_PLATE,
	WinMgr.WIN_ID_CONFIGURE,
	WinMgr.WIN_ID_ARCHIVE_WINDOW,
	#WinMgr.WIN_ID_SYSTEM_INFO,
	#WinMgr.WIN_ID_MEDIACENTER,
	WinMgr.WIN_ID_EPG_WINDOW,
	WinMgr.WIN_ID_TIMESHIFT_PLATE,
	WinMgr.WIN_ID_INFO_PLATE
	#WinMgr.WIN_ID_FAVORITE_ADDONS,
	#WinMgr.WIN_ID_SYSTEM_UPDATE,
	#WinMgr.WIN_ID_HELP
	]

gGlobalEvent = None

E_PARENTLOCK_INIT = 0
E_PARENTLOCK_EIT  = 1

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
			self.CheckParentLock( E_PARENTLOCK_EIT, aEvent )

		elif aEvent.getName( ) == ElisPMTReceivedEvent.getName( ) :
			LOG_TRACE( '--------- received ElisPMTReceivedEvent-----------' )
			if aEvent :
				aEvent.printdebug( )
				self.mDataCache.SetCurrentPMTEvent( aEvent )

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
				#self.mDataCache.Frontdisplay_Resolution( )
				self.mDataCache.SetLockedState( ElisEnum.E_CC_FAILED_SCRAMBLED_CHANNEL )
			elif aEvent.mStatus == ElisEnum.E_CC_FAILED_NO_SIGNAL :
				WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).GetLastWindowID( ) ).setProperty( 'Signal', 'False' )
				#self.mDataCache.Frontdisplay_Resolution( )
				self.mDataCache.SetLockedState( ElisEnum.E_CC_FAILED_NO_SIGNAL )
			else :
				WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).GetLastWindowID( ) ).setProperty( 'Signal', 'True' )
				self.mDataCache.SetLockedState( ElisEnum.E_CC_SUCCESS )

		elif aEvent.getName( ) == ElisEventChannelChangeResult( ).getName( ) :
			self.CheckParentLock( E_PARENTLOCK_INIT )

		elif aEvent.getName( ) == ElisEventVideoIdentified( ).getName( ) :
			self.mDataCache.Frontdisplay_ResolutionByIdentified( aEvent )

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
			self.mDataCache.Channel_GetInitialBlank( )
			self.CheckParentLock( E_PARENTLOCK_INIT )
			if WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_NULLWINDOW :
				self.mDataCache.Channel_SetCurrent( aEvent.mChannelNo, aEvent.mServiceType, None, True )
				xbmc.executebuiltin( 'xbmc.Action(contextmenu)' )
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
		#WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetPincodeRequest( True )
		self.CheckParentLock( E_PARENTLOCK_INIT )
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


	def CheckParentLock( self, aCmd = E_PARENTLOCK_EIT, aEvent = None ) :
		if WinMgr.GetInstance( ).GetLastWindowID( ) not in PARENTLOCK_CHECKWINDOW :
			LOG_TRACE( '--------parentLock check pass winid[%s]'% WinMgr.GetInstance( ).GetLastWindowID( ) )
			return

		if aCmd == E_PARENTLOCK_INIT :
			#default blank
			self.mDataCache.SetParentLock( True )
			self.mDataCache.Epgevent_GetPresent( )
			iEPG = self.mDataCache.GetEpgeventCurrent( )
			iChannel = self.mDataCache.Channel_GetCurrent( )
			LOG_TRACE('---------------------parentLock ch[%s %s] mLocked[%s] parentLock[%s] epg[%s]'% ( iChannel.mNumber, iChannel.mName, iChannel.mLocked, self.mDataCache.GetParentLock( ), iEPG )  )

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
					self.mDataCache.SetPincodeDialog( True )
					#self.ShowPincodeDialog( )
					thread = threading.Timer( 0.1, self.ShowPincodeDialog )
					thread.start( )
			else :
				if self.mDataCache.Get_Player_AVBlank( ) :
					self.mDataCache.Player_AVBlank( False )

		elif aCmd == E_PARENTLOCK_EIT :
			iEPG = self.mDataCache.GetEpgeventCurrent( )
			if iEPG and iEPG.mError == 0 :
				LOG_TRACE('EIT-id[%s] oldId[%s] currentEpg[%s] age[%s] limit[%s]'% ( aEvent.mEventId, self.mEventId, iEPG.mEventName, iEPG.mAgeRating, self.mDataCache.GetPropertyAge( ) ) )
			else :
				LOG_TRACE('EIT-id[%s] oldId[%s] currentEpg[%s]'% ( aEvent.mEventId, self.mEventId, iEPG ) )

			if not iEPG or self.mEventId != aEvent.mEventId :
				self.mEventId = aEvent.mEventId
				self.mDataCache.Epgevent_GetPresent( )
				#is Age? agerating check
				if self.mDataCache.GetParentLock( ) :
					if ( not self.mDataCache.GetPincodeDialog( ) ) :
						LOG_TRACE('---------------------parentLock')
						self.mDataCache.SetPincodeDialog( True )
						#self.ShowPincodeDialog( )
						thread = threading.Timer( 0.1, self.ShowPincodeDialog )
						thread.start( )

				else :
					iChannel = self.mDataCache.Channel_GetCurrent( )
					if iChannel and ( not iChannel.mLocked ) and self.mDataCache.Get_Player_AVBlank( ) :
						LOG_TRACE( '--------------- Release parentLock' )
						self.mDataCache.Player_AVBlank( False )


	def ShowPincodeDialog( self ) :
		LOG_TRACE('--------blank m/w[%s] mbox[%s] lockDialog[%s]'% ( self.mDataCache.Channel_GetInitialBlank( ), self.mDataCache.Get_Player_AVBlank(), self.mDataCache.GetPincodeDialog( ) ) )
		if not self.mDataCache.Get_Player_AVBlank( ) :
			self.mDataCache.Player_AVBlank( True )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_INPUT_PINCODE )
		dialog.SetTitleLabel( MR_LANG( 'Enter your PIN code' ) )
		dialog.SetCheckStatus( E_CHECK_PARENTLOCK )
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
				#from pvr.HiddenTestMgr import SendCommand
				#SendCommand( 'VKEY_ARCHIVE' )
				xbmc.executebuiltin( 'xbmc.Action(DVBArchive)' )

		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			self.mDataCache.SetParentLock( False )
			if self.mDataCache.Get_Player_AVBlank( ) :
				self.mDataCache.Player_AVBlank( False )

		self.mDataCache.SetPincodeDialog( False )

