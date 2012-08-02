from pvr.gui.WindowImport import *


class RootWindow( BaseWindow ):
	def __init__( self, *args, **kwargs ):
		BaseWindow.__init__( self, *args, **kwargs )

		self.mInitialized = False

	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		if self.mInitialized == False :
			if E_SUPPROT_HBBTV == True :
				self.mCommander.AppHBBTV_Ready( 0 )
			self.UpdateVolume( )
			self.SendLocalOffsetToXBMC( )
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetAutomaticHide( True )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )
			WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).mLastId ).doModal()
			self.mInitialized = True
			self.mEventBus.Register( self )			
		else :
			WinMgr.GetInstance( ).GetWindow(WinMgr.GetInstance( ).mLastId).doModal( )

		
	def onAction( self, aAction ) :
		LOG_TRACE( '' )
		"""
		actionId = aAction.getId( )
		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR:
			LOG_ERR( '------------- Root Window -------------' )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
		"""
			
				
	def onClick( self, aControlId ):
		LOG_TRACE( '' )	
		
 
	def onFocus( self, aControlId ):
		LOG_TRACE('')


	@GuiLock
	def onEvent(self, aEvent) :
		if aEvent.getName() == ElisEventTimeReceived.getName( ) :
			self.SendLocalOffsetToXBMC( )

		elif aEvent.getName() == ElisEventRecordingStarted.getName() or \
			 aEvent.getName() == ElisEventRecordingStopped.getName() :

			#LOG_TRACE('<<<<<<<<<<<<<<<<<<<<< RootWindow <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
			self.mDataCache.ReLoadChannelListByRecording( )
			"""
			if aEvent.getName() == ElisEventRecordingStarted.getName() :
				msg1 = MR_LANG('Recording Started')
			else :
				msg1 = MR_LANG('Recording Ended')
			msg2 = self.GetRecordingInfo( )

			self.AlarmDialog(msg1, msg2)
			"""
		"""
		elif aEvent.getName() == ElisEventTuningStatus.getName() :
			LOG_TRACE('No Signal TEST TunerNo[%s] locked[%s]' % ( aEvent.mTunerNo, aEvent.mIsLocked ) )
			if aEvent.mIsLocked :
				WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).mLastId ).setProperty('Signal', 'False')
			else :
				WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).mLastId ).setProperty('Signal', 'True')

			import inspect
			currentStack = inspect.stack()
			LOG_TRACE( '+++++getrecursionlimit[%s] currentStack[%s]'% (sys.getrecursionlimit(), len(currentStack)) )
			LOG_TRACE( '+++++currentStackInfo[%s]'% (currentStack) )
		"""


	def GetRecordingInfo( self ) :
		labelInfo = MR_LANG('Reload Channel List...')
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
		if WinMgr.E_ADD_XBMC_HTTP_FUNCTION == True :
			localOffset = self.mDataCache.Datetime_GetLocalOffset( )
			xbmc.executehttpapi( 'setlocaloffset(%d)' %localOffset )

		LOG_TRACE( '--------------' )

