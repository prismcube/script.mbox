from pvr.gui.WindowImport import *


BUTTON_ID_VIEW_MODE				= 100
BUTTON_ID_SORT_MODE				= 101
TOGGLEBUTTON_ID_ASC				= 102
RADIIOBUTTON_ID_EXTRA			= 103

LABEL_ID_PLAY_NAME				= 401
PROGRESS_ID_PLAY_PROGRESS		= 402

LABEL_ID_PLAY_START				= 403
LABEL_ID_PLAY_END				= 404

LIST_ID_COMMON_RECORD			= 3400
LIST_ID_THUMBNAIL_RECORD		= 3410
LIST_ID_POSTERWRAP_RECORD		= 3420
LIST_ID_FANART_RECORD			= 3430

E_VIEW_LIST						= 0
E_VIEW_THUMBNAIL				= 1
E_VIEW_POSTER_WRAP				= 2
E_VIEW_FANART					= 3
E_VIEW_END						= 4

E_SORT_DATE						= 0
E_SORT_CHANNEL					= 1
E_SORT_TITLE					= 2
E_SORT_DURATION					= 3
E_SORT_END						= 4

CONTEXT_RESUME_FROM				= 0
CONTEXT_PLAY_FROM_BEGINNIG		= 1
CONTEXT_DELETE					= 2
CONTEXT_DELETE_ALL				= 3
CONTEXT_LOCK					= 4
CONTEXT_UNLOCK					= 5
CONTEXT_RENAME					= 6
CONTEXT_START_MARK				= 7
CONTEXT_CLEAR_MARK				= 8

MININUM_KEYWORD_SIZE			= 3


class ArchiveWindow( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mSelectRecordKey = -1
		self.mExitByPlay = False
		self.mPlayingRecord = None
		self.mPlayProgressThread = None
		self.mEnableThread = False
		self.mViewMode = E_VIEW_LIST

	
	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		status = self.mDataCache.Player_GetStatus( )
		
		if status.mMode == ElisEnum.E_MODE_PVR :
			self.mWin.setProperty( 'PvrPlay', 'True' )
		else :
			self.mWin.setProperty( 'PvrPlay', 'False' )
		
		if self.mPlayingRecord :
			self.mEventBus.Register( self )
			self.mSelectRecordKey = self.mPlayingRecord.mRecordKey
			self.UpdatePlayStopThumbnail( self.mPlayingRecord )			
			self.SelectLastRecordKey( )
			self.UpdatePlayStatus( )

			if self.mViewMode == E_VIEW_LIST :
				self.SetPipScreen( )
				self.LoadNoSignalState( )
			return

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( MR_LANG( 'Archive' ) )

		self.mRecordCount = 0
		self.mSelectedIndex = 0
		self.mRecordList = [] 
		self.mSortList = [] 		
		self.mRecordListItems = []
		self.mLastFocusItem = -1	

		self.mServiceType =  self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( ).mServiceType

		try :		
			self.mViewMode = int( GetSetting( 'VIEW_MODE' ) )
			self.mCtrlViewMode = self.getControl( BUTTON_ID_VIEW_MODE )

			LOG_TRACE( 'self.mCtrlViewMode =%s' % self.mCtrlViewMode )			

			self.mSortMode = int( GetSetting( 'SORT_MODE' ) )		
			self.mCtrlSortMode = self.getControl( BUTTON_ID_SORT_MODE )

			self.mAscending = []
			self.mAscending = [False,False,False,False,False]

			self.mAscending[E_SORT_DATE] = False
			self.mAscending[E_SORT_CHANNEL] = True
			self.mAscending[E_SORT_TITLE] = True
			self.mAscending[E_SORT_DURATION] = False

			self.mCtrlCommonList = self.getControl( LIST_ID_COMMON_RECORD )
			self.mCtrlThumbnailList = self.getControl( LIST_ID_THUMBNAIL_RECORD )
			self.mCtrlPosterwrapList = self.getControl( LIST_ID_POSTERWRAP_RECORD )
			self.mCtrlFanartList = self.getControl( LIST_ID_FANART_RECORD )

			self.mCtrlPlayName = self.getControl( LABEL_ID_PLAY_NAME )
			self.mCtrlPlayProgress = self.getControl( PROGRESS_ID_PLAY_PROGRESS )
			self.mCtrlPlayStart = self.getControl( LABEL_ID_PLAY_START )
			self.mCtrlPlayEnd = self.getControl( LABEL_ID_PLAY_END )

			self.mPlayPerent = 0
			self.mCtrlPlayProgress.setPercent( self.mPlayPerent ) 			

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		self.mEventBus.Register( self )

		self.Load( )

		self.UpdateAscending( )
		self.UpdateViewMode( )
		
		self.InitControl( )

		self.UpdateList( )
		self.SelectLastRecordKey( )		
		self.UpdatePlayStatus( )

		self.mInitialized = True


	def onAction( self, aAction ) :
		focusId = self.GetFocusId( )
		actionId = aAction.getId( )
		self.GlobalAction( actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR or actionId == Action.ACTION_MBOX_ARCHIVE  :
			self.mDataCache.Player_Stop( )
			self.mPlayingRecord	= None
			self.mWin.setProperty( 'PvrPlay', 'False' )
			self.Close( )
			self.SetVideoRestore( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_SELECT_ITEM or actionId == Action.ACTION_PAUSE or actionId == Action.ACTION_PLAYER_PLAY :
			if focusId == LIST_ID_COMMON_RECORD or focusId == LIST_ID_THUMBNAIL_RECORD or focusId == LIST_ID_POSTERWRAP_RECORD or focusId == LIST_ID_FANART_RECORD :
				if	self.mMarkMode == True :
					self.DoMarkToggle( )
				else :
					if actionId == Action.ACTION_PAUSE or actionId == Action.ACTION_PLAYER_PLAY :
						self.StartRecordPlayback( False )
					else :
						self.StartRecordPlayback( True )
						
		elif actionId == Action.ACTION_MOVE_RIGHT or actionId == Action.ACTION_MOVE_LEFT :
			if focusId == LIST_ID_POSTERWRAP_RECORD or focusId == LIST_ID_FANART_RECORD or focusId == LIST_ID_THUMBNAIL_RECORD :
				self.UpdateSelectedPosition( )

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN :
			if focusId == LIST_ID_COMMON_RECORD or focusId == LIST_ID_POSTERWRAP_RECORD or focusId == LIST_ID_FANART_RECORD or focusId == LIST_ID_THUMBNAIL_RECORD :
				self.UpdateSelectedPosition( )
				if focusId  == LIST_ID_COMMON_RECORD :
					self.UpdateArchiveInfomation( )

		elif actionId == Action.ACTION_PAGE_UP or actionId == Action.ACTION_PAGE_DOWN :
			if focusId == LIST_ID_POSTERWRAP_RECORD or focusId == LIST_ID_FANART_RECORD or focusId == LIST_ID_THUMBNAIL_RECORD :
				self.UpdateSelectedPosition( )

		elif actionId == Action.ACTION_CONTEXT_MENU :
			self.ShowContextMenu( )

		elif actionId == Action.ACTION_STOP :
			self.StopRecordPlayback( )

		elif actionId == Action.ACTION_MBOX_TVRADIO :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_LIVE :
				if self.mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
					self.mServiceType = ElisEnum.E_SERVICE_TYPE_RADIO
				else :
					self.mServiceType = ElisEnum.E_SERVICE_TYPE_TV
				self.Flush( )
				self.Load( )
				self.UpdateList( )
				self.SetRadioScreen( self.mServiceType )
					
			else :
				xbmcgui.Dialog( ).ok( MR_LANG( 'Attention' ), MR_LANG( 'Try again after stopping the PVR clip' ) )

	
	def onClick( self, aControlId ) :
		LOG_TRACE( 'aControlId=%d' % aControlId )

		if aControlId == BUTTON_ID_VIEW_MODE :
			self.RestoreLastRecordKey( )		
			self.mViewMode += 1
			if self.mViewMode >= E_VIEW_END :
				self.mViewMode = 0 

			SetSetting( 'VIEW_MODE','%d' %self.mViewMode )
			self.UpdateViewMode( )
			self.InitControl( )
			self.UpdateList( )
			self.SelectLastRecordKey( )						
		
		elif aControlId == BUTTON_ID_SORT_MODE :
			self.RestoreLastRecordKey( )		
			self.mSortMode += 1
			if self.mSortMode >= E_SORT_END :
				self.mSortMode = 0 
				
			SetSetting( 'SORT_MODE','%d' %self.mSortMode ) 								
			self.UpdateSortMode( )
			self.InitControl( )			
			self.UpdateAscending( )
			self.UpdateList( )
			self.SelectLastRecordKey( )			
			
		elif aControlId == TOGGLEBUTTON_ID_ASC :
			self.RestoreLastRecordKey( )
			LOG_TRACE( 'Mode=%d' % self.mSortMode )
			LOG_TRACE( 'mAscending=%d' %self.mAscending[self.mSortMode] )
			if self.mAscending[self.mSortMode] == True :
				self.mAscending[self.mSortMode] = False
			else :
				self.mAscending[self.mSortMode] = True

			self.UpdateAscending( )
			self.UpdateList( )
			self.SelectLastRecordKey( )						

		elif aControlId == RADIIOBUTTON_ID_EXTRA :
			pass


	def onFocus( self, controlId ) :
		if self.mInitialized == False :
			return


	@GuiLock
	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			if aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
				if aEvent.mType == ElisEnum.E_EOF_END :
					xbmc.executebuiltin( 'xbmc.Action(stop)' )
			elif aEvent.getName( ) == ElisEventPlaybackStopped.getName( ) :
				if self.mPlayingRecord :
					self.UpdatePlayStopThumbnail( self.mPlayingRecord )


	def InitControl( self ) :

		if self.mViewMode == E_VIEW_LIST :
			self.mCtrlViewMode.setLabel( '%s: %s' %( MR_LANG( 'VIEW' ), MR_LANG( 'LIST' ) ) )
		elif self.mViewMode == E_VIEW_THUMBNAIL :			
			self.mCtrlViewMode.setLabel( '%s: %s' %( MR_LANG( 'VIEW' ), MR_LANG( 'THUMBNAIL' ) ) )		
		elif self.mViewMode == E_VIEW_POSTER_WRAP :			
			self.mCtrlViewMode.setLabel( '%s: %s' %( MR_LANG( 'VIEW' ), MR_LANG( 'POSTER_WRAP' ) ) )		
		elif self.mViewMode == E_VIEW_FANART :
			self.mCtrlViewMode.setLabel( '%s: %s' %( MR_LANG( 'VIEW' ), MR_LANG( 'FANART' ) ) )		
		else :
			LOG_WARN( 'Unknown view mode' )

		if self.mSortMode == E_SORT_DATE :
			self.mCtrlSortMode.setLabel( '%s: %s' %( MR_LANG( 'SORT' ), MR_LANG( 'DATE' ) ) )
		elif self.mSortMode == E_SORT_CHANNEL :
			self.mCtrlSortMode.setLabel( '%s: %s' %( MR_LANG( 'SORT' ), MR_LANG( 'CHANNEL' ) ) )		
		elif self.mSortMode == E_SORT_TITLE :
			self.mCtrlSortMode.setLabel( '%s: %s' %( MR_LANG( 'SORT' ), MR_LANG( 'TITLE' ) ) )		
		elif self.mSortMode == E_SORT_DURATION :
			self.mCtrlSortMode.setLabel( '%s: %s' %( MR_LANG( 'SORT' ), MR_LANG( 'DURATION') ) )
		else :
			LOG_WARN( 'Unknown sort mode' )


	def UpdateViewMode( self ) :
		LOG_TRACE( '--------------------- self.mViewMode=%d' %self.mViewMode)
		if self.mViewMode == E_VIEW_LIST :
			self.mWin.setProperty( 'ViewMode', 'common' )
		elif self.mViewMode == E_VIEW_THUMBNAIL :			
			self.mWin.setProperty( 'ViewMode', 'thumbnail' )
		elif self.mViewMode == E_VIEW_POSTER_WRAP :			
			self.mWin.setProperty( 'ViewMode', 'posterwrap' )
		elif self.mViewMode == E_VIEW_FANART :			
			self.mWin.setProperty( 'ViewMode', 'panart' )
		else :
			self.mViewMode = E_VIEW_LIST 		
			self.mWin.setProperty( 'ViewMode', 'common' )
		

	def UpdateSortMode( self ) :
		LOG_TRACE( '---------------------' )


	def UpdateAscending( self ) :
		LOG_TRACE( '--------------------- %d' %self.mAscending[self.mSortMode] )	
		if self.mAscending[self.mSortMode] == True :
			self.mWin.setProperty( 'Ascending', 'true' )
		else :
			self.mWin.setProperty( 'Ascending', 'false' )
	

	def Flush( self ) :
		self.mRecordCount = 0
		self.mRecordList = []
		self.mSortList = []		


	def Load( self ) :

		self.mMarkMode = False

		LOG_TRACE( '----------------------------------->' )
		try :
			self.mRecordList = self.mDataCache.Record_GetList( self.mServiceType )
			if self.mRecordList == None :
				self.mRecordCount = 0
			else :
				self.mRecordCount = len( self.mRecordList  )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def UpdateList( self ) :
		LOG_TRACE( 'UpdateList Start' )
		try :
			if not self.mRecordList or self.mRecordList == None :
				self.mRecordList = []

			if self.mSortMode == E_SORT_DATE :
				self.mRecordList.sort( self.ByDate )
			elif self.mSortMode == E_SORT_CHANNEL :
				self.mRecordList.sort( self.ByChannel )

			elif self.mSortMode == E_SORT_TITLE :
				self.mRecordList.sort( self.ByTitle )

			elif self.mSortMode == E_SORT_DURATION :
				self.mRecordList.sort( self.ByDuration )
			else :
				LOG_WARN( 'Unknown sort mode' )		
				self.mSortMode = 0
				self.mRecordList.sort( self.ByDate )

			if self.mAscending[self.mSortMode] == False :
				self.mRecordList.reverse( )

			self.mCtrlCommonList.reset( )
			self.mCtrlThumbnailList.reset( )
			self.mCtrlPosterwrapList.reset( )
			self.mCtrlFanartList.reset( )

			self.mRecordListItems = []
			for i in range( len( self.mRecordList ) ) :
				self.UpdateListItem( self.mRecordList[i] )

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )

		self.CheckVideoSize( )
		LOG_TRACE( 'UpdateList END' )


	def UpdateListItem( self, aRecordInfo ) :
		channelName = 'P%04d.%s' % ( aRecordInfo.mChannelNo, aRecordInfo.mChannelName )
		recItem = xbmcgui.ListItem( channelName, aRecordInfo.mRecordName )
		recItem.setProperty( 'RecDate', TimeToString( aRecordInfo.mStartTime ) )
		recItem.setProperty( 'RecDuration', '%dm' % ( aRecordInfo.mDuration / 60 ) )
		if aRecordInfo.mLocked :
			recItem.setProperty( 'RecIcon', 'IconNotAvailable.png' )
		else :
			thumbnaillist = []
			thumbnaillist = glob.glob( os.path.join( '/mnt/hdd0/pvr/thumbnail', 'record_thumbnail_%d_*.jpg' % aRecordInfo.mRecordKey ) )
			if len( thumbnaillist ) > 0 :
				recItem.setProperty( 'RecIcon', thumbnaillist[0] )
			else :
				recItem.setProperty( 'RecIcon', 'RecIconSample.png' )

		recItem.setProperty( 'Marked', 'False' )
		self.mRecordListItems.append( recItem )


	def UpdatePlayStopThumbnail( self, aRecordInfo, aPrevRecordInfo=None ) :

		listindex = 0

		if aPrevRecordInfo :
			for recInfo in self.mRecordList :
				if recInfo.mRecordKey == aPrevRecordInfo.mRecordKey :
					break
				listindex = listindex + 1

			recItem = self.mRecordListItems[ listindex ]				

			if recInfo.mLocked :
				recItem.setProperty( 'RecIcon', 'IconNotAvailable.png' )
			else :
				thumbnaillist = []
				thumbnaillist = glob.glob( os.path.join( '/mnt/hdd0/pvr/thumbnail', 'record_thumbnail_%d_*.jpg' % aPrevRecordInfo.mRecordKey ) )
				if len( thumbnaillist ) > 0 :
					recItem.setProperty( 'RecIcon', thumbnaillist[0] )
				else :
					recItem.setProperty( 'RecIcon', 'RecIconSample.png' )

			recItem.setProperty( 'Playing', 'False' )

		if aRecordInfo == None :
			LOG_ERR( 'Has no playing record')
			return

		listindex = 0

		for recInfo in self.mRecordList :
			if recInfo.mRecordKey == aRecordInfo.mRecordKey :
				break
			listindex = listindex + 1

		recItem = self.mRecordListItems[ listindex ]

		status = self.mDataCache.Player_GetStatus( )
			
		if recInfo.mLocked == True and status.mMode != ElisEnum.E_MODE_PVR:
			recItem.setProperty( 'RecIcon', 'IconNotAvailable.png' )
		else :
			thumbnaillist = []
			thumbnaillist = glob.glob( os.path.join( '/mnt/hdd0/pvr/thumbnail', 'record_thumbnail_%d_*.jpg' % aRecordInfo.mRecordKey ) )
			if len( thumbnaillist ) > 0 :
				recItem.setProperty( 'RecIcon', thumbnaillist[0] )
			else :
				recItem.setProperty( 'RecIcon', 'RecIconSample.png' )

		if status.mMode == ElisEnum.E_MODE_PVR :
			recItem.setProperty( 'Playing', 'True' )
		else :
			recItem.setProperty( 'Playing', 'False' )


		xbmc.executebuiltin( 'container.update' )


	def CheckVideoSize( self ) :
		if self.mViewMode == E_VIEW_LIST :
			self.SetPipScreen( )
			self.LoadNoSignalState( )
			self.mCtrlCommonList.addItems( self.mRecordListItems )		
			#self.setFocusId( LIST_ID_COMMON_RECORD )
		elif self.mViewMode == E_VIEW_THUMBNAIL :
			self.mDataCache.Player_SetVIdeoSize( 1230, 0, 50, 50 )
			#self.SetVideoRestore( )		
			self.mCtrlThumbnailList.addItems( self.mRecordListItems )		
			#self.setFocusId( LIST_ID_THUMBNAIL_RECORD )
		elif self.mViewMode == E_VIEW_POSTER_WRAP :
			self.mDataCache.Player_SetVIdeoSize( 1230, 0, 50, 50 )
			#self.SetVideoRestore( )		
			self.mCtrlPosterwrapList.addItems( self.mRecordListItems )		
			#self.setFocusId( LIST_ID_POSTERWRAP_RECORD )
		elif self.mViewMode == E_VIEW_FANART :
			self.mDataCache.Player_SetVIdeoSize( 1230, 0, 50, 50 )
			#self.SetVideoRestore( )		
			self.mCtrlFanartList.addItems( self.mRecordListItems )		
			#self.setFocusId( LIST_ID_FANART_RECORD )
		else :
			LOG_WARN( 'Unknown view mode' )


	def ByDate( self, aRec1, aRec2 ) :
		return cmp( aRec1.mStartTime, aRec2.mStartTime )
		

	def ByChannel( self, aRec1, aRec2 ) :
		return cmp( aRec1.mChannelNo, aRec2.mChannelNo )


	def ByTitle( self, aRec1, aRec2 ) :
		return cmp( aRec1.mRecordName, aRec2.mRecordName )


	def ByDuration( self, aRec1, aRec2 ) :
		return cmp( aRec1.mDuration, aRec2.mDuration )


	@RunThread
	def CurrentTimeThread(self) :
		pass


	@GuiLock
	def UpdateLocalTime( self ) :
		pass

		"""
		try:
			self.mLocalTime = self.mCommander.Datetime_GetLocalTime( )


			if self.mNavEpg :
				endTime = self.mNavEpg.mStartTime + self.mNavEpg.mDuration
		
				pastDuration = endTime - self.mLocalTime
				if pastDuration < 0 :
					pastDuration = 0

				if self.mNavEpg.mDuration > 0 :
					percent = pastDuration * 100/self.mNavEpg.mDuration
				else :
					percent = 0

				#print 'percent=%d' %percent
				self.mCtrlProgress.setPercent( percent )

		except Exception, e :
			print '[%s:%s] Error exception[%s]'% (	\
				self.__file__,						\
				currentframe().f_lineno,			\
				e )

			self.mLocalTime = 0
		"""


	def StopRecordPlayback( self ) :
		if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
			ret = self.mDataCache.Player_Stop( )
			self.mLastFocusItem = -1
			self.UpdatePlayStatus( )
			

	def StartRecordPlayback( self, aResume=True ) :
		selectedPos = self.GetSelectedPosition( )
		if self.mLastFocusItem == selectedPos and self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
			self.Close( )
			self.SetVideoRestore( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE, WinMgr.WIN_ID_NULLWINDOW )
		else :
			currentPlayingRecord = self.mPlayingRecord		
			if selectedPos >= 0 and selectedPos < len( self.mRecordList ) :
				recInfo = self.mRecordList[selectedPos]
				if recInfo.mLocked == True :
					if self.CheckPincode() == False :
						return False

				if aResume == True :
					playOffset = self.mDataCache.RecordItem_GetCurrentPosByKey( recInfo.mRecordKey )
					LOG_TRACE( 'RecKey=%d PlayOffset=%s' %( recInfo.mRecordKey, playOffset ) )
					if playOffset < 0 :
						playOffset = 0
					self.mDataCache.Player_StartInternalRecordPlayback( recInfo.mRecordKey, self.mServiceType, playOffset, 100 )
				else :
					self.mDataCache.Player_StartInternalRecordPlayback( recInfo.mRecordKey, self.mServiceType, 0, 100 )

				self.mPlayingRecord = recInfo
				self.mWin.setProperty( 'PvrPlay', 'True' )
				self.UpdatePlayStatus( )

			self.RestoreLastRecordKey( )
			self.UpdatePlayStopThumbnail( self.mPlayingRecord, currentPlayingRecord )
			self.mLastFocusItem = selectedPos
			if self.mViewMode != E_VIEW_LIST :
				self.Close( )
				self.SetVideoRestore( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE, WinMgr.WIN_ID_NULLWINDOW )


	def GetSelectedPosition( self ) :
		position  = -1 

		if self.mViewMode == E_VIEW_LIST :
			position = self.mCtrlCommonList.getSelectedPosition( )		
		elif self.mViewMode == E_VIEW_THUMBNAIL :
			position = self.mCtrlThumbnailList.getSelectedPosition( )		
		elif self.mViewMode == E_VIEW_POSTER_WRAP :
			position = self.mCtrlPosterwrapList.getSelectedPosition( )		
		elif self.mViewMode == E_VIEW_FANART :
			position = self.mCtrlFanartList.getSelectedPosition( )		
		else :
			position = -1

		return position


	def GetMarkedList( self ) :
		markedList = []

		if self.mRecordListItems == None :
			self.UpdateList( )
			return markedList

		count = len( self.mRecordListItems )

		for i in range( count ) :
			listItem = self.mRecordListItems[i]
			if listItem.getProperty( 'Marked' ) == 'True' :
				markedList.append( i )

		return markedList


	def ShowContextMenu( self ) :

		status = self.mDataCache.Player_GetStatus( )
		if status.mMode == ElisEnum.E_MODE_PVR :
			xbmcgui.Dialog( ).ok( MR_LANG( 'Attention' ), MR_LANG( 'Try again after stopping the PVR clip' ) )
			return
	
		try :
			selectedPos = self.GetSelectedPosition( )
			context = []

			markedList = self.GetMarkedList( )
			
			if markedList and len( markedList ) > 0 :
				context.append( ContextItem( MR_LANG( 'Delete' ), CONTEXT_DELETE ) )
				context.append( ContextItem( MR_LANG( 'Delete All' ), CONTEXT_DELETE_ALL ) )
				context.append( ContextItem( MR_LANG( 'Lock' ), CONTEXT_LOCK ) )
				context.append( ContextItem( MR_LANG( 'Unlock' ), CONTEXT_UNLOCK ) )	
				context.append( ContextItem( MR_LANG( 'Remove Selections' ), CONTEXT_CLEAR_MARK ) )	
				
			elif selectedPos >= 0 and selectedPos < len( self.mRecordList ) :
				recordInfo = self.mRecordList[ selectedPos ]
				playOffset = self.mDataCache.RecordItem_GetCurrentPosByKey( recordInfo.mRecordKey )
				LOG_TRACE('Offset Test =%s' %playOffset )
				if playOffset < 0 :
					playOffset = 0
				context.append( ContextItem( MR_LANG( 'Resume from %s' %(TimeToString( int( playOffset / 1000 ), TimeFormatEnum.E_HH_MM_SS ) )), CONTEXT_RESUME_FROM ) )
				context.append( ContextItem( MR_LANG( 'Play from beginning' ), CONTEXT_PLAY_FROM_BEGINNIG ) )
				context.append( ContextItem( MR_LANG( 'Delete' ), CONTEXT_DELETE ) )
				context.append( ContextItem( MR_LANG( 'Delete All' ), CONTEXT_DELETE_ALL ) )				
				if recordInfo.mLocked:
					context.append( ContextItem( MR_LANG( 'Unlock' ), CONTEXT_UNLOCK ) )
				else :
					context.append( ContextItem( MR_LANG( 'Lock' ), CONTEXT_LOCK ) )

				context.append( ContextItem( MR_LANG( 'Rename' ), CONTEXT_RENAME ) )
				context.append( ContextItem( MR_LANG( 'Multi-Select' ), CONTEXT_START_MARK ) )

			else :
				return
				
			GuiLock2( True )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context )
			dialog.doModal( )
			GuiLock2( False )
			
			contextAction = dialog.GetSelectedAction( )
			self.DoContextAction( contextAction ) 

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def DoContextAction( self, aContextAction ) :
		LOG_TRACE( 'aContextAction=%d' %aContextAction )

		if aContextAction == CONTEXT_RESUME_FROM :
			self.StartRecordPlayback( True )

		elif aContextAction == CONTEXT_PLAY_FROM_BEGINNIG :
			self.StartRecordPlayback( False )

		elif aContextAction == CONTEXT_DELETE :
			self.ShowDeleteConfirm()

		elif aContextAction == CONTEXT_DELETE_ALL :
			self.ShowDeleteAllConfirm()

		elif aContextAction == CONTEXT_LOCK :
			self.DoLockUnlock( True )

		elif aContextAction == CONTEXT_UNLOCK :
			self.DoLockUnlock( False )

		elif aContextAction == CONTEXT_RENAME :
			self.ShowRenameDialog( )

		elif aContextAction == CONTEXT_START_MARK :
			self.DoStartMark( )

		elif aContextAction == CONTEXT_CLEAR_MARK :
			self.DoClearMark( )
		else :
			LOG_ERR( 'Unknown Context Action' )


	def ShowDeleteConfirm( self ) :
		markedList = self.GetMarkedList( )
		selectedPos = self.GetSelectedPosition( )
		afterPos = -1

		if markedList == None or len( markedList ) <= 0 :
			markedList = []
			if selectedPos >= 0 and selectedPos < len( self.mRecordList ) :
				markedList.append( selectedPos )

		if len( markedList ) > 0 :
			hasLocked = False
			afterPos = markedList[0]

			# Check Locked Item
			for i in range( len( markedList ) ) :
				position = markedList[i]
				recInfo = self.mRecordList[ position ]
				if recInfo.mLocked == True :
					hasLocked = True
					break

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Delete Record' ), MR_LANG( 'Do you want to delete the selected file(s)?' ) )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				if hasLocked == True :
					if self.CheckPincode( ) == False :
						return False

				self.DoDelete( markedList )


				if afterPos < 0 or afterPos >= len( self.mRecordList ) :
					afterPos = 0
				
				if self.mViewMode == E_VIEW_LIST :
					self.mCtrlCommonList.selectItem( afterPos )
				elif self.mViewMode == E_VIEW_THUMBNAIL :
					self.mCtrlThumbnailList.selectItem( afterPos )
				elif self.mViewMode == E_VIEW_POSTER_WRAP :
					self.mCtrlPosterwrapList.selectItem( afterPos )
				elif self.mViewMode == E_VIEW_FANART :
					self.mCtrlFanartList.selectItem( afterPos )
				else :
					LOG_WARN( 'Unknown View Mode' )

				self.UpdateSelectedPosition( )
				self.UpdateArchiveInfomation( )


	def ShowDeleteAllConfirm( self ) :
		if self.mRecordList == None or len( self.mRecordList  ) <= 0 :
			return

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( MR_LANG( 'WARNING' ), MR_LANG( 'DO YOU REALLY WANT TO DELETE ALL YOUR FILES?' ) )
		dialog.doModal( )

		if dialog.IsOK( ) == E_DIALOG_STATE_YES :

			hasLocked = False

			# Check Locked Item
			for recInfo in self.mRecordList :
				if recInfo.mLocked == True :
					hasLocked = True
					break
		
			if hasLocked == True :
				if self.CheckPincode( ) == False :
					return False

			self.OpenBusyDialog( )

			for recInfo in self.mRecordList :
				self.mDataCache.Record_DeleteRecord( recInfo.mRecordKey, self.mServiceType )

			self.CloseBusyDialog( )

			self.Flush( )
			self.Load( )
			self.UpdateList( )
			self.UpdateSelectedPosition( )
			self.UpdateArchiveInfomation( )


	def ShowRenameDialog( self ) :
		selectedPos = self.GetSelectedPosition( )	
		if self.mRecordList[ selectedPos ].mLocked == True :
			if self.CheckPincode() == False :
				return False
		
		try :
			kb = xbmc.Keyboard( self.mRecordList[ selectedPos ].mRecordName, MR_LANG( 'Please enter new filename' ), False )			
			kb.doModal( )
			if kb.isConfirmed( ) :
				newName = kb.getText( )
				LOG_TRACE( 'newName len=%d' %len( newName ) )
				if len( newName ) < MININUM_KEYWORD_SIZE :
					xbmcgui.Dialog( ).ok( MR_LANG( 'Attention' ), MR_LANG( 'A filename must be at least %d characters long' ) %MININUM_KEYWORD_SIZE )
					return
				else :

					LOG_TRACE( 'Key=%d ServiceType=%d Name=%s %s' %(self.mRecordList[ selectedPos ].mRecordKey,  self.mServiceType, self.mRecordList[ selectedPos ].mRecordName, newName ) )
					self.mDataCache.Record_Rename( self.mRecordList[ selectedPos ].mRecordKey, self.mServiceType, newName )
					self.mRecordListItems[ selectedPos ].setLabel2( newName )	
					self.mRecordList[ selectedPos ].mRecordName = newName
					xbmc.executebuiltin( 'container.update' )
					self.UpdateArchiveInfomation( )
					

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def DoDelete( self, aDeleteList ) :

		if len( aDeleteList ) > 0 :
			self.OpenBusyDialog( )

			count = len( aDeleteList )
			for i in range( count ) :
				position = aDeleteList[i]
				LOG_TRACE( 'i=%d serviceType=%d key=%d' %( position, self.mServiceType, self.mRecordList[position].mRecordKey ) )
				self.mDataCache.Record_DeleteRecord( self.mRecordList[position].mRecordKey, self.mServiceType )

			self.Flush( )
			self.Load( )
			self.UpdateList( )
			self.CloseBusyDialog( )
			

	def DoLockUnlock( self, aLock=False ) :
		markedList = self.GetMarkedList( )
		selectedPos = self.GetSelectedPosition( )

		if markedList == None or len( markedList ) <= 0 :
			markedList = []
			if selectedPos >= 0 and selectedPos < len( self.mRecordList ) :
				markedList.append( selectedPos )
				
		if len( markedList ) > 0 :
			if self.CheckPincode( ) == False :
				return False

			count = len( markedList )
			for i in range( count ) :
				position = markedList[i]
				recItem = self.mRecordListItems[ position ]
				if aLock == True :
					self.mRecordList[ position ].mLocked = True
					self.mDataCache.Record_SetLock( self.mRecordList[ position ].mRecordKey, self.mServiceType, True )
					recItem.setProperty( 'RecIcon', 'IconNotAvailable.png' )
				else :
					self.mRecordList[ position ].mLocked = False
					self.mDataCache.Record_SetLock( self.mRecordList[ position ].mRecordKey, self.mServiceType, False )
					thumbnaillist = []
					thumbnaillist = glob.glob( os.path.join( '/mnt/hdd0/pvr/thumbnail', 'record_thumbnail_%d_*.jpg' % self.mRecordList[ position ].mRecordKey ) )
					if len( thumbnaillist ) > 0 :
						recItem.setProperty( 'RecIcon', thumbnaillist[0] )
					else :
						recItem.setProperty( 'RecIcon', 'RecIconSample.png' )

			self.DoClearMark( )
			xbmc.executebuiltin( 'container.update' )


	def DoStartMark( self ) :
		self.mMarkMode = True


	def DoClearMark( self ) :
		self.mMarkMode = False

		if self.mRecordListItems == None :
			return
 
		for listItem in self.mRecordListItems :
			listItem.setProperty( 'Marked', 'False' )


	def DoMarkToggle( self ) :
		if self.mRecordListItems == None :
			return
			
		selectedPos = self.GetSelectedPosition( )

		if selectedPos >= 0 and selectedPos < len( self.mRecordListItems ) :
			listItem = self.mRecordListItems[ selectedPos ]
			if listItem.getProperty( 'Marked' ) == 'True' :
				listItem.setProperty( 'Marked', 'False' )
			else :
				listItem.setProperty( 'Marked', 'True' )			

		selectedPos = selectedPos + 1	
		if selectedPos >= len( self.mRecordListItems ) :
			selectedPos = 0
			
		if selectedPos >= 0 and selectedPos < len( self.mRecordListItems ) :
			if self.mViewMode == E_VIEW_LIST :
				self.mCtrlCommonList.selectItem( selectedPos )
			#elif self.mViewMode == E_VIEW_THUMBNAIL :
				#self.mCtrlThumbnailList.selectItem( selectedPos )
			#elif self.mViewMode == E_VIEW_POSTER_WRAP :
				#self.mCtrlPosterwrapList.selectItem( selectedPos )
			#elif self.mViewMode == E_VIEW_FANART :
				#self.mCtrlFanartList.selectItem( selectedPos )
			else :
				LOG_WARN( 'Unknown view mode' )
			
		#xbmc.executebuiltin('container.update')


	def CheckPincode( self ) :
		savedPincode = ElisPropertyInt( 'PinCode', self.mCommander ).GetProp( )
		GuiLock2( True )
		pincodeDialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
#		pincodeDialog.SetDialogProperty( 'Input Pincode', '', 4, True )
		pincodeDialog.SetDialogProperty( MR_LANG( 'Enter your PIN code' ), '', 4, True )
		pincodeDialog.doModal( )
		GuiLock2( False )
		
		if pincodeDialog.IsOK( ) == E_DIALOG_STATE_YES :
			inputPincode = int( pincodeDialog.GetString( ) )
			LOG_TRACE( 'Input pincode=%d savedPincode=%d' %( savedPincode, inputPincode) )
			if inputPincode == savedPincode :
				return True
			else :
				infoDialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				infoDialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Sorry, that PIN code does not match' ) )
	 			infoDialog.doModal( )

		return False


	def Close( self ) :
		self.mEventBus.Deregister( self )	
		self.mEnableThread = False
		if self.mPlayProgressThread :
			self.mPlayProgressThread.join( )


	def UpdateSelectedPosition( self ) :
		selectedPos = self.GetSelectedPosition( )
		if selectedPos < 0 :
			self.mWin.setProperty( 'SelectedPosition', '0' )
		else :
			self.mWin.setProperty( 'SelectedPosition', '%d' % ( selectedPos + 1 ) )


	def UpdateArchiveInfomation( self ) :
		selectedPos = self.GetSelectedPosition( )
		
		if selectedPos >= 0 and selectedPos < len( self.mRecordList ) :
			recInfo = self.mRecordList[ selectedPos ]
			"""
			LOG_TRACE( 'Archive Info --> ChannelName=%s' %recInfo.mChannelName )
			LOG_TRACE( 'Archive Info --> RecDate=%s' %TimeToString( recInfo.mStartTime ) )
			LOG_TRACE( 'Archive Info --> RecDuration=%d' %( recInfo.mDuration/60 ) )
			LOG_TRACE( 'Archive Info --> RecName=%s' %recInfo.mRecordName )
			"""
			
			if recInfo :
				self.mWin.setProperty( 'ChannelName', recInfo.mChannelName )
				self.mWin.setProperty( 'RecDate',  TimeToString( recInfo.mStartTime ) )
				self.mWin.setProperty( 'RecDuration',  '%dMin' %( recInfo.mDuration/60 ) )
				self.mWin.setProperty( 'RecName', recInfo.mRecordName )
			else :
				self.ResetArchiveInfomation( )
		else :
			self.ResetArchiveInfomation( )


	def ResetArchiveInfomation( self ) :
		self.mWin.setProperty( 'ChannelName', '' )
		self.mWin.setProperty( 'RecDate', '' )
		self.mWin.setProperty( 'RecDuration',  '' )
		self.mWin.setProperty( 'RecName', '' )				


	def RestoreLastRecordKey( self ) :
		selectedPos = self.GetSelectedPosition( )

		if selectedPos >= 0 and selectedPos < len( self.mRecordList ) :
			recInfo = self.mRecordList[ selectedPos ]
			self.mSelectRecordKey = recInfo.mRecordKey
		else :
			self.mSelectRecordKey = -1


	def SelectLastRecordKey( self ) :
		selectedPos = 0
		for i in range( len( self.mRecordList ) ) :
			recInfo = self.mRecordList[i]
			if recInfo.mRecordKey == self.mSelectRecordKey  :
				break;
			selectedPos += 1

		LOG_TRACE( 'SelectPos=%d' %selectedPos )

		if self.mViewMode == E_VIEW_LIST :
			self.mCtrlCommonList.selectItem( selectedPos )
		elif self.mViewMode == E_VIEW_THUMBNAIL :
			self.mCtrlThumbnailList.selectItem( selectedPos )
		elif self.mViewMode == E_VIEW_POSTER_WRAP :
			self.mCtrlPosterwrapList.selectItem( selectedPos )
		elif self.mViewMode == E_VIEW_FANART :
			self.mCtrlFanartList.selectItem( selectedPos )
		else :
			LOG_WARN( 'Unknown View Mode' )

		self.UpdateSelectedPosition( )
		self.UpdateArchiveInfomation( )


	def UpdatePlayStatus( self ) :
		status = self.mDataCache.Player_GetStatus( )

		#Playing Name
		if status.mMode == ElisEnum.E_MODE_PVR :
			if self.mPlayingRecord :
				self.mCtrlPlayName.setLabel( self.mPlayingRecord.mRecordName )
				
				if self.mEnableThread == True and self.mPlayProgressThread :
					self.mEnableThread = False				
					self.mPlayProgressThread.join( )
				
				self.mEnableThread = True
				self.mPlayProgressThread = self.PlayProgressThread( )
				
			else :
				if self.mEnableThread == True and self.mPlayProgressThread :
					self.mEnableThread = False
					self.mPlayProgressThread.join( )

				self.mCtrlPlayProgress.setPercent( 0 ) 
				self.mCtrlPlayName.setLabel( '' )
				
		else :
			self.mPlayingRecord = None
			self.mWin.setProperty( 'PvrPlay', 'False' )
			if self.mEnableThread == True and self.mPlayProgressThread :
				self.mEnableThread = False			
				self.mPlayProgressThread.join( )

			self.mCtrlPlayProgress.setPercent( 0 )			
			channel = self.mDataCache.Channel_GetCurrent( )
			if channel :
				self.mCtrlPlayName.setLabel( channel.mName )
			else :
				self.mCtrlPlayName.setLabel( '' )

		self.mCtrlPlayStart.setLabel( '' )
		self.mCtrlPlayEnd.setLabel( '' )


	@RunThread
	def PlayProgressThread( self ) :
		self.mCtrlPlayProgress.setPercent( 0 ) 	
		while self.mEnableThread :
			time.sleep(1)
			self.UpdatePlayProgress( )


	@GuiLock
	def UpdatePlayProgress( self ) :
		status = self.mDataCache.Player_GetStatus( )
		if status == None or status.mError != 0 :
			LOG_ERR( 'Player_GetStatus fail' )
			return

		self.mPlayPerent = 0
		if status.mMode == ElisEnum.E_MODE_PVR and status.mEndTimeInMs > 0 :
			self.mPlayPerent = int ( ( status.mPlayTimeInMs - status.mStartTimeInMs ) * 100 / status.mEndTimeInMs )
			if self.mPlayPerent < 1 :
				self.mPlayPerent = 1

		LOG_TRACE( 'Update PlayProgress = %d [%d,%d,%d]' %( self.mPlayPerent, status.mPlayTimeInMs, status.mStartTimeInMs, status.mEndTimeInMs ) )
		
		self.mCtrlPlayProgress.setPercent( self.mPlayPerent )
		self.mCtrlPlayStart.setLabel( '%s' %(TimeToString( int( status.mPlayTimeInMs / 1000 ), TimeFormatEnum.E_HH_MM_SS ) ) )
		self.mCtrlPlayEnd.setLabel( '%s' %(TimeToString( int( status.mEndTimeInMs / 1000 ), TimeFormatEnum.E_HH_MM_SS ) ) )
		

	def GetPlayingRecord( self ) :
		return self.mPlayingRecord
