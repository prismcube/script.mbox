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
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.SendLocalOffsetToXBMC( )		


	@classmethod
	def GetName( cls ) :
		return cls.__name__


	def onEvent( self, aEvent ) :
		if not WinMgr.gWindowMgr :
			return

		if aEvent.getName( ) == ElisEventTimeReceived.getName( ) :
			self.SendLocalOffsetToXBMC( )

		elif aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or \
			 aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
			self.mDataCache.ReLoadChannelListByRecording( )
			if aEvent.getName( ) == ElisEventRecordingStopped.getName( ) and aEvent.mHDDFull :
				if self.mIsHddFullDialogOpened == False :
					thread = threading.Timer( 0.3, self.AsyncHddFull )
					thread.start( )
				else :
					LOG_TRACE( 'Already opened, hddfull' )

		elif aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
			if aEvent.mType == ElisEnum.E_EOF_END :
				if WinMgr.GetInstance( ).mLastId != WinMgr.WIN_ID_NULLWINDOW and \
				   WinMgr.GetInstance( ).mLastId != WinMgr.WIN_ID_TIMESHIFT_PLATE :
					LOG_TRACE( 'CHECK onEVENT[%s] stop'% aEvent.getName( ) )
					self.mDataCache.Player_Stop( )

		elif aEvent.getName( ) == ElisEventChannelChangeStatus( ).getName( ) :
			if aEvent.mStatus == ElisEnum.E_CC_FAILED_SCRAMBLED_CHANNEL :
				WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).mLastId ).setProperty( 'Signal', 'Scramble' )
				self.mDataCache.Frontdisplay_Resolution( )
				self.mDataCache.SetLockedState( ElisEnum.E_CC_FAILED_SCRAMBLED_CHANNEL )
			elif aEvent.mStatus == ElisEnum.E_CC_FAILED_NO_SIGNAL :
				WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).mLastId ).setProperty( 'Signal', 'False' )
				self.mDataCache.Frontdisplay_Resolution( )
				self.mDataCache.SetLockedState( ElisEnum.E_CC_FAILED_NO_SIGNAL )
			else :
				WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).mLastId ).setProperty( 'Signal', 'True' )
				self.mDataCache.SetLockedState( ElisEnum.E_CC_SUCCESS )

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
			if WinMgr.GetInstance( ).mLastId not in AUTOPOWERDOWN_EXCEPTWINDOW :
				if self.mIsDialogOpend == False :
					thread = threading.Timer( 0.3, self.AsyncPowerSave )
					thread.start( )
			else :
				LOG_TRACE( 'Skip auto power down : %s' ) % WinMgr.GetInstance( ).mLastId

		elif aEvent.getName( ) == ElisEventChannelChangedByRecord.getName( ) :
			if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_TIMESHIFT :
				self.mDataCache.Player_Stop( )
			self.mDataCache.Player_AVBlank( False )
			self.mDataCache.Channel_SetCurrent( aEvent.mChannelNo, aEvent.mServiceType )
			LOG_TRACE('event[%s] tune[%s] type[%s]'% ( aEvent.getName( ), aEvent.mChannelNo, aEvent.mServiceType ) )


	def AsyncHddFull( self ):
		self.mIsHddFullDialogOpened = True
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Recording stopped due to insufficient disk space' ) )
		dialog.doModal( )

		self.mIsHddFullDialogOpened = False


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
			if WinMgr.GetInstance( ).mLastId == WinMgr.WIN_ID_NULLWINDOW :
				self.mCommander.AppHBBTV_Ready( 0 )
			dialog.doModal( )
			if WinMgr.GetInstance( ).mLastId == WinMgr.WIN_ID_NULLWINDOW :
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
		
		if E_ADD_XBMC_HTTP_FUNCTION == True :
			localOffset = self.mDataCache.Datetime_GetLocalOffset( )
			xbmc.executehttpapi( 'setlocaloffset(%d)' %localOffset )
		elif E_ADD_XBMC_ADDON_API == True :			
			localOffset = self.mDataCache.Datetime_GetLocalOffset( )
			print 'E_ADD_XBMC_ADDON_API : setlocal offset = %s ' % localOffset
			xbmc.setLocalOffset( localOffset )
		LOG_TRACE( '--------------' )

