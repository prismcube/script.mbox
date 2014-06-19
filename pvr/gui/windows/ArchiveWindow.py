from pvr.gui.WindowImport import *

E_ARCHIVE_WINDOW_BASE_ID			=  WinMgr.WIN_ID_ARCHIVE_WINDOW * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 

BUTTON_ID_VIEW_MODE					= E_ARCHIVE_WINDOW_BASE_ID + 100
BUTTON_ID_SORT_MODE					= E_ARCHIVE_WINDOW_BASE_ID + 101
TOGGLEBUTTON_ID_ASC					= E_ARCHIVE_WINDOW_BASE_ID + 102
RADIOBUTTON_ID_EXTRA				= E_ARCHIVE_WINDOW_BASE_ID + 104
BUTTON_ID_NAS_ARCHIVE				= E_ARCHIVE_WINDOW_BASE_ID + 105
BUTTON_ID_ALL_ARCHIVE				= E_ARCHIVE_WINDOW_BASE_ID + 106
RADIOBUTTON_ID_WATCHED				= E_ARCHIVE_WINDOW_BASE_ID + 200

LABEL_ID_PLAY_NAME					= E_ARCHIVE_WINDOW_BASE_ID + 401
PROGRESS_ID_PLAY_PROGRESS			= E_ARCHIVE_WINDOW_BASE_ID + 402

LABEL_ID_PLAY_START					= E_ARCHIVE_WINDOW_BASE_ID + 403
LABEL_ID_PLAY_END					= E_ARCHIVE_WINDOW_BASE_ID + 404

LIST_ID_COMMON_RECORD				= E_BASE_WINDOW_ID + 3400
LIST_ID_THUMBNAIL_RECORD			= E_BASE_WINDOW_ID + 3410
LIST_ID_POSTERWRAP_RECORD			= E_BASE_WINDOW_ID + 3420
LIST_ID_FANART_RECORD				= E_BASE_WINDOW_ID + 3430
LIST_ID_NETVOLUME					= E_ARCHIVE_WINDOW_BASE_ID + 9050

SCROLL_ID_COMMON_VIEW				= E_BASE_WINDOW_ID + 3401
SCROLL_ID_THUMBNAIL_VIEW			= E_BASE_WINDOW_ID + 3411
SCROLL_ID_POSTERWRAP_VIEW			= E_BASE_WINDOW_ID + 3421
SCROLL_ID_FANART_VIEW				= E_BASE_WINDOW_ID + 3431


E_ARCHIVE_WINDOW_DEFAULT_FOCUS_ID	= E_ARCHIVE_WINDOW_BASE_ID + 9003


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
CONTEXT_REFRESH_NET_VOLUME		= 9


class ArchiveWindow( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mSelectRecordKey		= -1
		self.mExitByPlay			= False
		self.mPlayingRecord			= None
		self.mPlayProgressThread	= None
		self.mEnableThread			= False
		self.mViewMode				= E_VIEW_LIST
		self.mThumbnailHash		= {}
		self.mUpdateInfomationTimer = None		

		self.mAscending = []
		self.mAscending = [ False, False, False, False, False ]

		self.mAscending[E_SORT_DATE] = False
		self.mAscending[E_SORT_CHANNEL] = True
		self.mAscending[E_SORT_TITLE] = True
		self.mAscending[E_SORT_DURATION] = False


	def onInit( self ) :
		self.setProperty( 'SetBackgroundColor', '1' )
		self.setFocusId( E_ARCHIVE_WINDOW_DEFAULT_FOCUS_ID )
		self.SetFrontdisplayMessage( MR_LANG('Archive') )		
		self.mWinId = xbmcgui.getCurrentWindowId( )

		self.mUpdateInfomationTimer = None
		if E_SUPPORT_EXTEND_RECORD_PATH :
			self.mNetVolumeSelectIndex = -1
			self.mNetVolumeList = self.mDataCache.Record_GetNetworkVolume( True )

		status = self.mDataCache.Player_GetStatus( )
		
		if status.mMode == ElisEnum.E_MODE_PVR :
			self.setProperty( 'PvrPlay', 'True' )
		else :
			self.setProperty( 'PvrPlay', 'False' )

		if self.mPlayingRecord :
			self.SetSingleWindowPosition( E_ARCHIVE_WINDOW_BASE_ID )
			self.mEventBus.Register( self )
			self.mSelectRecordKey = self.mPlayingRecord.mRecordKey
			self.Load( )
			self.UpdateList(  )
			self.UpdatePlayStatus( )
			self.SetFocusList( self.mViewMode )
			self.SelectLastRecordKey( )			
			return

		#self.getControl( E_SETTING_MINI_TITLE ).setLabel( MR_LANG( 'Archive' ) )

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
			self.mCtrlHideWatched = self.getControl( RADIOBUTTON_ID_WATCHED )
			if self.mDataCache.GetDefaultHideWatched( ) :
				self.mDataCache.SetDefaultHideWatched( False )
				self.mCtrlHideWatched.setSelected( False )

			self.mCtrlCommonList = self.getControl( LIST_ID_COMMON_RECORD )
			self.mCtrlThumbnailList = self.getControl( LIST_ID_THUMBNAIL_RECORD )
			self.mCtrlPosterwrapList = self.getControl( LIST_ID_POSTERWRAP_RECORD )
			self.mCtrlFanartList = self.getControl( LIST_ID_FANART_RECORD )
			self.mCtrlNetVolumeList = self.getControl( LIST_ID_NETVOLUME )

			self.mCtrlPlayName = self.getControl( LABEL_ID_PLAY_NAME )
			self.mCtrlPlayProgress = self.getControl( PROGRESS_ID_PLAY_PROGRESS )
			self.mCtrlPlayStart = self.getControl( LABEL_ID_PLAY_START )
			self.mCtrlPlayEnd = self.getControl( LABEL_ID_PLAY_END )

			self.mPlayPerent = 0
			self.mCtrlPlayProgress.setPercent( self.mPlayPerent ) 			

		except Exception, ex :
			LOG_ERR( "Exception %s" % ex )

		self.mEventBus.Register( self )

		self.Load( )

		self.UpdateAscending( )
		self.UpdateViewMode( )
		
		self.InitControl( )

		self.UpdateList( )
		
		self.SetFocusList( self.mViewMode )
		
		self.SelectLastRecordKey( )	
		self.UpdatePlayStatus( )
		
		self.mInitialized = True


	def onAction( self, aAction ) :
		focusId = self.GetFocusId( )
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR or actionId == Action.ACTION_MBOX_ARCHIVE  :
			if self.mMarkMode :
				self.DoClearMark( )
			else :

				if focusId == BUTTON_ID_VIEW_MODE or focusId == BUTTON_ID_SORT_MODE or focusId == TOGGLEBUTTON_ID_ASC or focusId == RADIOBUTTON_ID_EXTRA or focusId == RADIOBUTTON_ID_WATCHED :
					self.SetFocusList( self.mViewMode )				
				else :
					#self.mDataCache.Player_Stop( )
					#self.mPlayingRecord	= None
					#self.setProperty( 'PvrPlay', 'False' )
					self.Close( )
					self.SetVideoRestore( )
					#WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
					WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_PAUSE or actionId == Action.ACTION_PLAYER_PLAY :
			if focusId == LIST_ID_COMMON_RECORD or focusId == LIST_ID_THUMBNAIL_RECORD or focusId == LIST_ID_POSTERWRAP_RECORD or focusId == LIST_ID_FANART_RECORD :
				if self.mMarkMode == True :
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

			elif focusId == BUTTON_ID_NAS_ARCHIVE :
				if E_SUPPORT_EXTEND_RECORD_PATH and self.mNetVolumeList and \
				   self.mNetVolumeSelectIndex > -1 and self.mNetVolumeSelectIndex < len( self.mNetVolumeList ) :
					self.mCtrlNetVolumeList.selectItem( self.mNetVolumeSelectIndex )

		elif actionId == Action.ACTION_PAGE_UP or actionId == Action.ACTION_PAGE_DOWN :
			if focusId  == LIST_ID_COMMON_RECORD or focusId == LIST_ID_POSTERWRAP_RECORD or focusId == LIST_ID_FANART_RECORD or focusId == LIST_ID_THUMBNAIL_RECORD :
				self.UpdateSelectedPosition( )
				if focusId  == LIST_ID_COMMON_RECORD :
					self.UpdateArchiveInfomation( )

		elif actionId == Action.ACTION_CONTEXT_MENU :
			if focusId == SCROLL_ID_COMMON_VIEW or focusId == SCROLL_ID_POSTERWRAP_VIEW or focusId == SCROLL_ID_FANART_VIEW or focusId == SCROLL_ID_THUMBNAIL_VIEW :
				return
			self.ShowContextMenu( )

		elif actionId == Action.ACTION_STOP :
			self.StopRecordPlayback( )

		elif actionId == Action.ACTION_MBOX_TVRADIO :
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.mDataCache.ToggleTVRadio( )
				if ret :
					self.mServiceType =  self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( ).mServiceType
					self.Flush( )
					self.Load( )
					self.UpdateList( )
					self.UpdatePlayStatus( )
					self.SetRadioScreen( )

				else :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No channels available for the selected mode' ) )
					dialog.doModal( )
					
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Try again after stopping playback%s and timeshift' )% NEW_LINE )
				dialog.doModal( )


	def onClick( self, aControlId ) :
		LOG_TRACE( 'aControlId=%d' % aControlId )
		if aControlId == BUTTON_ID_VIEW_MODE :
			self.RestoreLastRecordKey( )		
			self.mViewMode += 1
			if self.mViewMode >= E_VIEW_END :
				self.mViewMode = 0 

			SetSetting( 'VIEW_MODE', '%d' % self.mViewMode )
			self.UpdateViewMode( )
			self.InitControl( )
			self.UpdateList(  )
			self.SelectLastRecordKey( )
			#self.SetFocusList( self.mViewMode )

		elif aControlId == BUTTON_ID_SORT_MODE :
			self.RestoreLastRecordKey( )		
			self.mSortMode += 1
			if self.mSortMode >= E_SORT_END :
				self.mSortMode = 0 

			SetSetting( 'SORT_MODE', '%d' % self.mSortMode )
			self.UpdateSortMode( )
			self.InitControl( )			
			self.UpdateAscending( )
			self.UpdateList(  )
			self.SelectLastRecordKey( )			

		elif aControlId == TOGGLEBUTTON_ID_ASC :
			self.RestoreLastRecordKey( )
			LOG_TRACE( 'Mode=%d' % self.mSortMode )
			LOG_TRACE( 'mAscending=%d' % self.mAscending[self.mSortMode] )
			if self.mAscending[self.mSortMode] == True :
				self.mAscending[self.mSortMode] = False
			else :
				self.mAscending[self.mSortMode] = True

			self.UpdateAscending( )
			self.UpdateList(  )
			self.SelectLastRecordKey( )

		elif aControlId == RADIOBUTTON_ID_EXTRA :
			pass

		elif aControlId == RADIOBUTTON_ID_WATCHED :
			self.Load( )
			self.UpdateList( )
			self.UpdateViewMode( )
			#self.SetFocusList( self.mViewMode )

		elif aControlId == LIST_ID_COMMON_RECORD or aControlId == LIST_ID_THUMBNAIL_RECORD or aControlId == LIST_ID_POSTERWRAP_RECORD or aControlId == LIST_ID_FANART_RECORD :
			if	self.mMarkMode == True :
				self.DoMarkToggle( )
			else :
				self.StartRecordPlayback( True )

		elif aControlId == LIST_ID_NETVOLUME :
			selectPos = self.mCtrlNetVolumeList.getSelectedPosition( )
			if selectPos == self.mNetVolumeSelectIndex :
				LOG_TRACE( '[Archive] pass, select same' )
				return
			self.mNetVolumeSelectIndex = selectPos
			if self.mMarkMode :
				self.DoClearMark( )
			self.SetFocusList( self.mViewMode )
			self.Load( )
			self.UpdateList( )
			self.UpdateViewMode( )
			self.SelectLastRecordKey( )

		elif aControlId == BUTTON_ID_ALL_ARCHIVE :
			if self.mNetVolumeSelectIndex == -1 :
				LOG_TRACE( '[Archive] pass, select same' )
				return
			self.mNetVolumeSelectIndex = -1
			if self.mMarkMode :
				self.DoClearMark( )
			self.SetFocusList( self.mViewMode )
			self.Load( )
			self.UpdateList( )
			self.UpdateViewMode( )
			self.SelectLastRecordKey( )


	def onFocus( self, controlId ) :
		if self.mInitialized == False :
			return


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			if aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
				#LOG_TRACE( '-------------------Event[%s] key[%s]'% ( aEvent.getName( ), aEvent.mKey ) )
				if aEvent.mType == ElisEnum.E_EOF_END :
					if self.mPlayingRecord and self.mPlayingRecord.mRecordKey == aEvent.mKey :
						#LOG_TRACE( '=================================correct stop' )
						#xbmc.executebuiltin( 'xbmc.Action(stop)' )
						self.StopRecordPlayback( )

			elif aEvent.getName( ) == ElisEventPlaybackStarted.getName( ) :
				self.UpdatePlayStopThumbnail( aEvent.mKey, True )

			elif aEvent.getName( ) == ElisEventPlaybackStopped.getName( ) :
				#LOG_TRACE( '-------------------Event[%s] key[%s]'% ( aEvent.getName( ), aEvent.mKey ) )
				if self.mPlayingRecord and self.mPlayingRecord.mRecordKey == aEvent.mKey :
					self.UpdatePlayStopThumbnail( aEvent.mKey, False )
					self.UpdatePlayStatus( )

			elif aEvent.getName( ) == ElisEventJpegEncoded.getName( ) :
				#LOG_TRACE( '-------------------Event[%s] key[%s]'% ( aEvent.getName( ), aEvent.mRecordKey ) )
				if self.mCtrlHideWatched.isSelected( ) :
					self.Load( )
					self.UpdateList( )
					#self.SetFocusList( self.mViewMode )
					return

				#refresh preload
				#LOG_TRACE( '------------------------------------Event[%s]'% aEvent.getName( ) )
				if self.mViewMode == E_VIEW_POSTER_WRAP :
					thread = threading.Timer( 0.1, self.RefreshListItemByPosterWrap, [aEvent] )
					thread.start( )
					return

				#isPlay = False
				#if self.mPlayingRecord :
				#	isPlay = True
				#self.UpdatePlayStopThumbnail( aEvent.mRecordKey, isPlay )
				self.UpdatePlayStopThumbnail( aEvent.mRecordKey, False )
				#LOG_TRACE('-----------------------%s[%s]'% ( aEvent.getName( ), aEvent.mRecordKey ) )

			elif aEvent.getName( ) == ElisEventUSBRecordVolumeAttach.getName( ) or \
			     aEvent.getName( ) == ElisEventUSBRecordVolumeDetach.getName( ) :
				if E_SUPPORT_EXTEND_RECORD_PATH :
					self.mNetVolumeList = self.mDataCache.Record_GetNetworkVolume( )
					self.Flush( )
					self.Load( )
					self.UpdateList( )


	def InitControl( self ) :

		if self.mViewMode == E_VIEW_LIST :
			self.mCtrlViewMode.setLabel( '%s : %s' %( MR_LANG( 'View' ), MR_LANG( 'List' ) ) )
		elif self.mViewMode == E_VIEW_THUMBNAIL :			
			self.mCtrlViewMode.setLabel( '%s : %s' %( MR_LANG( 'View' ), MR_LANG( 'Thumbnail' ) ) )
		elif self.mViewMode == E_VIEW_POSTER_WRAP :			
			self.mCtrlViewMode.setLabel( '%s : %s' %( MR_LANG( 'View' ), MR_LANG( 'Poster_wrap' ) ) )
		elif self.mViewMode == E_VIEW_FANART :
			self.mCtrlViewMode.setLabel( '%s : %s' %( MR_LANG( 'View' ), MR_LANG( 'Fanart' ) ) )
		else :
			LOG_WARN( 'Unknown view mode' )

		if self.mSortMode == E_SORT_DATE :
			self.mCtrlSortMode.setLabel( '%s : %s' %( MR_LANG( 'Sort' ), MR_LANG( 'Date' ) ) )
		elif self.mSortMode == E_SORT_CHANNEL :
			self.mCtrlSortMode.setLabel( '%s : %s' %( MR_LANG( 'Sort' ), MR_LANG( 'Channel' ) ) )
		elif self.mSortMode == E_SORT_TITLE :
			self.mCtrlSortMode.setLabel( '%s : %s' %( MR_LANG( 'Sort' ), MR_LANG( 'Title' ) ) )
		elif self.mSortMode == E_SORT_DURATION :
			self.mCtrlSortMode.setLabel( '%s : %s' %( MR_LANG( 'Sort' ), MR_LANG( 'Duration') ) )
		else :
			LOG_WARN( 'Unknown sort mode' )


	def UpdateViewMode( self ) :
		LOG_TRACE( '--------------------- self.mViewMode=%d' % self.mViewMode)
		hideWatched = ''
		if self.mCtrlHideWatched.isSelected( ) :
			hideWatched = '(%s)'% MR_LANG( 'Hide Watched' )

		if self.mViewMode == E_VIEW_LIST :
			self.setProperty( 'ViewMode', 'common' )
			self.SetHeaderTitle( "%s - %s %s"%( MR_LANG( 'Archive' ), MR_LANG( 'List' ), hideWatched ), 0 )
		elif self.mViewMode == E_VIEW_THUMBNAIL :			
			self.setProperty( 'ViewMode', 'thumbnail' )
			self.SetHeaderTitle( "%s - %s %s"%( MR_LANG( 'Archive' ), MR_LANG( 'Thumbnail' ), hideWatched ), 0 )
		elif self.mViewMode == E_VIEW_POSTER_WRAP :			
			self.setProperty( 'ViewMode', 'posterwrap' )
			self.SetHeaderTitle( "%s - %s %s"%( MR_LANG( 'Archive' ), MR_LANG( 'Poster_wrap' ), hideWatched ), 0 )
		elif self.mViewMode == E_VIEW_FANART :			
			self.setProperty( 'ViewMode', 'fanart' )
			self.SetHeaderTitle( "%s - %s %s"%( MR_LANG( 'Archive' ), MR_LANG( 'Fanart' ), hideWatched ), 0 )
		else :
			self.mViewMode = E_VIEW_LIST 		
			self.setProperty( 'ViewMode', 'common' )
			self.SetHeaderTitle( "%s - %s %s"%( MR_LANG( 'Archive' ), MR_LANG( 'List' ), hideWatched ), 0 )

		self.SetSingleWindowPosition( E_ARCHIVE_WINDOW_BASE_ID )
		

	def UpdateSortMode( self ) :
		LOG_TRACE( '---------------------' )


	def UpdateAscending( self ) :
		LOG_TRACE( '--------------------- %d' % self.mAscending[self.mSortMode] )	
		if self.mAscending[self.mSortMode] == True :
			self.setProperty( 'Ascending', 'true' )
		else :
			self.setProperty( 'Ascending', 'false' )
	

	def Flush( self ) :
		self.mRecordCount = 0
		self.mRecordList = []
		self.mSortList = []		


	def Load( self ) :
		self.mMarkMode = False
		self.mThumbnailHash =  {}		
		self.ResetArchiveInfomation( )
		LOG_TRACE( '----------------------------------->' )
		try :
			isHideWatched = False
			if self.mCtrlHideWatched.isSelected( ) :
				isHideWatched = True

			mountInfo = ''
			if E_SUPPORT_EXTEND_RECORD_PATH and self.mNetVolumeList :
				if self.mNetVolumeSelectIndex > -1 and self.mNetVolumeSelectIndex < len( self.mNetVolumeList ) :
					mountInfo = self.mNetVolumeList[self.mNetVolumeSelectIndex].mMountPath

			self.mRecordList = self.mDataCache.Record_GetList( self.mServiceType, isHideWatched, mountInfo )
			if self.mRecordList == None :
				self.mRecordCount = 0
			else :
				self.mRecordCount = len( self.mRecordList  )
			self.UpdateFootor( )

		except Exception, ex :
			LOG_ERR( "Exception %s" % ex )


	def UpdateList( self ) :
		LOG_TRACE( 'UpdateList Start' )
		if self.mViewMode == E_VIEW_LIST :
			self.SetPipScreen( )
			#self.LoadNoSignalState( )
		else :
			self.mDataCache.Player_SetVIdeoSize( 0, 0, 1280, 720 )
		#self.OpenBusyDialog( )

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

			if self.mRecordListItems == None :
				self.mRecordListItems = []

			if self.mRecordList  == None :
				self.mRecordList =[]

			#LOG_TRACE('')
			self.mCtrlCommonList.reset( )
			self.mCtrlThumbnailList.reset( )
			self.mCtrlPosterwrapList.reset( )
			self.mCtrlFanartList.reset( )
			if E_SUPPORT_EXTEND_RECORD_PATH :
				self.mCtrlNetVolumeList.reset( )
				if self.mNetVolumeList :
					listItems = []
					for netVolume in self.mNetVolumeList :
						volumeName = os.path.basename( netVolume.mMountPath )
						listItem = xbmcgui.ListItem( '%s'% volumeName )
						listItems.append( listItem )
					self.mCtrlNetVolumeList.addItems( listItems )

			#LOG_TRACE('')
			updateOnly = False
			if len( self.mRecordListItems ) == len( self.mRecordList ) :
				updateOnly = True
			else :
				self.mRecordListItems = []

			thumbnaillist = glob.glob( os.path.join( '/mnt/hdd0/pvr/thumbnail', 'record_thumbnail*.jpg')  )
			
			for i in range(  len( thumbnaillist )  ) :
				recKey = thumbnaillist[i].split('_')
				#print 'recKey=%s' %recKey[2]
				if recKey and recKey[2] :
					self.mThumbnailHash[ recKey[2] ] = thumbnaillist[i]

			#LOG_TRACE('')
			for i in range( len( self.mRecordList ) ) :
				if updateOnly == True :
					#LOG_TRACE('')				
					self.UpdateListItem( self.mRecordList[i], self.mRecordListItems[i] )				
				else :
					#LOG_TRACE('')				
					self.UpdateListItem( self.mRecordList[i] )

			#LOG_TRACE('')
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_PVR :
				self.UpdatePlayStopThumbnail( self.mPlayingRecord.mRecordKey, True )

		except Exception, ex :
			LOG_ERR( "Exception %s" % ex )

		self.AddListItems( )
		#self.CloseBusyDialog( )
		LOG_TRACE( 'UpdateList END' )


	def UpdateListItem( self, aRecordInfo, aRecItem=None ) :
		thumbIcon = E_DEFAULT_THUMBNAIL_ICON
		if self.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
			thumbIcon = 'DefaultAudioNF.png'
			playOffset = self.mDataCache.RecordItem_GetCurrentPosByKey( aRecordInfo.mRecordKey )
			if playOffset > 0 :
				thumbIcon = 'DefaultAudioFO.png'

		channelName = 'P%04d.%s' % ( aRecordInfo.mChannelNo, aRecordInfo.mChannelName )

		if aRecItem :
			recItem = aRecItem
			recItem.setLabel(channelName )
			recItem.setLabel2( aRecordInfo.mRecordName )
		else :
			recItem = xbmcgui.ListItem( channelName, aRecordInfo.mRecordName )

		recItem.setProperty( 'RecDate', TimeToString( aRecordInfo.mStartTime ) )
		recDuration =  int( aRecordInfo.mDuration / 60 )
		if ( aRecordInfo.mDuration % 60 ) != 0 :
			recDuration += 1
		recItem.setProperty( 'RecDuration', '%dm' %recDuration )

		if aRecordInfo.mLocked or \
		   self.mDataCache.GetPropertyAge( ) != 0 and aRecordInfo.mAgeRating >= self.mDataCache.GetPropertyAge( ) :
			recItem.setProperty( 'RecIcon', 'IconNotAvailable.png' )
		else :
			recItem.setProperty( 'RecIcon', thumbIcon )

			thumbIcon =  self.mThumbnailHash.get('%d' %aRecordInfo.mRecordKey, None ) 

			if thumbIcon :
				recItem.setProperty( 'RecIcon', thumbIcon )
			else :
				recItem.setProperty( 'RecIcon', E_DEFAULT_THUMBNAIL_ICON )			

			"""
			thumbnaillist = []
			thumbnaillist = glob.glob( os.path.join( '/mnt/hdd0/pvr/thumbnail', 'record_thumbnail_%d_*.jpg' % aRecordInfo.mRecordKey ) )
			if len( thumbnaillist ) > 0 :
				recItem.setProperty( 'RecIcon', thumbnaillist[0] )
			else :
				#recItem.setProperty( 'RecIcon', E_DEFAULT_THUMBNAIL_ICON )
				recItem.setProperty( 'RecIcon', thumbIcon )
			"""

		recItem.setProperty( 'Marked', 'False' )
		recItem.setProperty( 'Playing', 'False' )

		if E_SUPPORT_EXTEND_RECORD_PATH :
			netVolume = E_TAG_FALSE
			if aRecordInfo.mMountInfo :
				mntType = 'HDD'
				netVolume = E_TAG_TRUE
				netVolumeUSB = E_TAG_FALSE
				retPath = os.path.dirname( aRecordInfo.mMountInfo )
				if retPath == E_DEFAULT_PATH_SMB_POSITION or \
				   retPath == E_DEFAULT_PATH_NFS_POSITION or \
				   retPath == E_DEFAULT_PATH_FTP_POSITION :
					mntType = 'NAS'
				elif bool( re.search( '%s\w\d+'% E_DEFAULT_PATH_USB_POSITION, aRecordInfo.mMountInfo, re.IGNORECASE ) ) :
					mntType = 'USB'
					netVolumeUSB = E_TAG_TRUE
				else :
					#internal
					netVolume = E_TAG_FALSE
					netVolumeUSB = E_TAG_FALSE

				recItem.setProperty( 'iNetVolumeType', mntType )
				recItem.setProperty( 'iNetVolumeUSB', netVolumeUSB )
				recItem.setProperty( 'iNetVolumeName', os.path.basename( aRecordInfo.mMountInfo ) )
			recItem.setProperty( 'RecNetVolume', netVolume )

		if aRecItem == None :		
			self.mRecordListItems.append( recItem )


	@SetLock
	def UpdatePlayStopThumbnail( self, aRecordKey, aIsStartEvent ) :
		if not self.mRecordList or len( self.mRecordList ) < 1 :
			LOG_TRACE( 'RecordList item is empty' )
			return

		thumbIcon = E_DEFAULT_THUMBNAIL_ICON
		if self.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
			thumbIcon = 'DefaultAudioNF.png'
			playOffset = self.mDataCache.RecordItem_GetCurrentPosByKey( aRecordKey )
			if playOffset > 0 :
				thumbIcon = 'DefaultAudioFO.png'

		listindex = 0
		for recInfo in self.mRecordList :
			if recInfo.mRecordKey == aRecordKey :
				break
			listindex = listindex + 1

		#isNoMatch
		if listindex >= len( self.mRecordList ) :
			xbmc.executebuiltin( 'container.refresh' )
			LOG_TRACE( 'except refresh thumbnail, Not matched recordkey[%s]'% aRecordkey )
			return

		recItem = self.mRecordListItems[ listindex ]

		status = self.mDataCache.Player_GetStatus( )
		if ( recInfo.mLocked and status.mMode != ElisEnum.E_MODE_PVR ) or \
		   ( self.mDataCache.GetPropertyAge( ) != 0 and recInfo.mAgeRating >= self.mDataCache.GetPropertyAge( ) and status.mMode != ElisEnum.E_MODE_PVR ) :
			recItem.setProperty( 'RecIcon', 'IconNotAvailable.png' )
		else :
			thumbnaillist = []
			thumbnaillist = glob.glob( os.path.join( '/mnt/hdd0/pvr/thumbnail', 'record_thumbnail_%d_*.jpg' % aRecordKey ) )
			if len( thumbnaillist ) > 0 :
				recItem.setProperty( 'RecIcon', thumbnaillist[0] )
			else :
				#recItem.setProperty( 'RecIcon', E_DEFAULT_THUMBNAIL_ICON )
				recItem.setProperty( 'RecIcon', thumbIcon )

		if aIsStartEvent :
			recItem.setProperty( 'Playing', 'True' )
		else :
			recItem.setProperty( 'Playing', 'False' )
		LOG_TRACE( '----------------playing[%s] recKey[%s] idx[%s]'% ( aIsStartEvent, recInfo.mRecordKey, listindex ) )

		xbmc.executebuiltin( 'container.refresh' )
		#self.SetFocusList( self.mViewMode )


	def RefreshListItemByPosterWrap( self, aEvent = None ) :
		if not self.mRecordList and len( self.mRecordList ) < 1 :
			LOG_TRACE( 'Recorditem None' )
			return

		lastFocus = self.mCtrlPosterwrapList.getSelectedPosition( )
		if aEvent :
			#LOG_TRACE( '-------------------UpdatePlayStopThumbnail' )
			self.UpdatePlayStopThumbnail( aEvent.mRecordKey, False )
			time.sleep( 0.02 )

		#LOG_TRACE( '-----1------------- refresh thumbnail[%s] key[%s]'% ( self.mThumbnailHash.get( '%s'% aEvent.mRecordKey, -1 ), aEvent.mRecordKey ) )

		self.mThumbnailHash = {}
		self.mRecordListItems = []
		try :
			thumbnaillist = glob.glob( os.path.join( '/mnt/hdd0/pvr/thumbnail', 'record_thumbnail*.jpg') )
			for i in range( len( thumbnaillist ) ) :
				recKey = thumbnaillist[i].split('_')
				#LOG_TRACE( '--------------recKey[%s]'% recKey )
				if recKey and recKey[2] :
					self.mThumbnailHash[ recKey[2] ] = thumbnaillist[i]

			for i in range( len( self.mRecordList ) ) :
				self.UpdateListItem( self.mRecordList[i] )

		except Exception, ex :
			LOG_ERR( "Exception %s" % ex )
			self.UpdateList( )
			self.mCtrlPosterwrapList.selectItem( lastFocus )
			LOG_TRACE( '-------Retry update list' )
			return

		self.AddListItems( )

		self.mCtrlPosterwrapList.selectItem( lastFocus )
		#LOG_TRACE( '-----2------------- refresh thumbnail[%s] key[%s]'% ( self.mThumbnailHash.get( '%s'% aEvent.mRecordKey, -1 ), aEvent.mRecordKey ) )


	def AddListItems( self ) :
		if self.mViewMode == E_VIEW_LIST :
			self.mCtrlCommonList.addItems( self.mRecordListItems )
		elif self.mViewMode == E_VIEW_THUMBNAIL :
			self.mCtrlThumbnailList.addItems( self.mRecordListItems )
		elif self.mViewMode == E_VIEW_POSTER_WRAP :
			self.mCtrlPosterwrapList.addItems( self.mRecordListItems )
		elif self.mViewMode == E_VIEW_FANART :
			self.mCtrlFanartList.addItems( self.mRecordListItems )
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
			LOG_TRACE( '-----------------------------1----' )
			ret = self.mDataCache.Player_Stop( )
			LOG_TRACE( '-----------------------------2----' )
			self.mLastFocusItem = -1


	def StartRecordPlayback( self, aResume=True ) :
		selectedPos = self.GetSelectedPosition( )
		if self.mLastFocusItem == selectedPos and self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
			self.Close( )
			self.SetVideoRestore( )
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).SetAutomaticHide( True )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE, WinMgr.WIN_ID_NULLWINDOW )
		else :
			currentPlayingRecord = self.mPlayingRecord		
			if selectedPos >= 0 and selectedPos < len( self.mRecordList ) :
				recInfo = self.mRecordList[selectedPos]
				iEPG = self.mDataCache.RecordItem_GetEventInfo( recInfo.mRecordKey )
				#iEPG.printdebug()
				if recInfo.mLocked or \
				   self.mDataCache.GetPropertyAge( ) != 0 and recInfo.mAgeRating >= self.mDataCache.GetPropertyAge( ) :
					if self.CheckPincode( ) == False :
						return False

				isPlay = False
				if aResume == True :
					playOffset = self.mDataCache.RecordItem_GetCurrentPosByKey( recInfo.mRecordKey )
					LOG_TRACE( 'RecKey=%d PlayOffset=%s' %( recInfo.mRecordKey, playOffset ) )
					if playOffset < 0 :
						playOffset = 0
					isPlay = self.mDataCache.Player_StartInternalRecordPlayback( recInfo.mRecordKey, self.mServiceType, playOffset, 100 )
				else :
					isPlay = self.mDataCache.Player_StartInternalRecordPlayback( recInfo.mRecordKey, self.mServiceType, 0, 100 )

				if not isPlay :
					lblLine = MR_LANG( 'Could not playback' )
					if E_SUPPORT_EXTEND_RECORD_PATH and recInfo.mMountInfo :
						mntType = 'HDD'
						retPath = os.path.dirname( recInfo.mMountInfo )
						if retPath == E_DEFAULT_PATH_SMB_POSITION or \
						   retPath == E_DEFAULT_PATH_NFS_POSITION or \
						   retPath == E_DEFAULT_PATH_FTP_POSITION :
							mntType = 'NAS'
						elif bool( re.search( '%s\w\d+'% E_DEFAULT_PATH_USB_POSITION, recInfo.mMountInfo, re.IGNORECASE ) ) :
							mntType = 'USB'

						if mntType != 'HDD' :
							lblLine = '%s \'%s\'\n %s'% ( lblLine, mntType, MR_LANG( 'Please check network connection' ) )

					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), lblLine )
					dialog.doModal( )
					return False

				SetLock2( True )
				self.mPlayingRecord = recInfo
				SetLock2( False )
				LOG_TRACE( '-----------start recKey[%s]'% recInfo.mRecordKey )

				self.setProperty( 'PvrPlay', 'True' )
				self.UpdatePlayStatus( )

			self.RestoreLastRecordKey( )
			self.mLastFocusItem = selectedPos


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
			#self.UpdateList( )
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
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Try again after stopping playback' ) )
			dialog.doModal( )
			return
	
		try :
			selectedPos = self.GetSelectedPosition( )
			context = []

			markedList = self.GetMarkedList( )
			
			if markedList and len( markedList ) > 0 :
				context.append( ContextItem( MR_LANG( 'Delete' ), CONTEXT_DELETE ) )
				context.append( ContextItem( MR_LANG( 'Delete all' ), CONTEXT_DELETE_ALL ) )
				context.append( ContextItem( MR_LANG( 'Lock' ), CONTEXT_LOCK ) )
				context.append( ContextItem( MR_LANG( 'Unlock' ), CONTEXT_UNLOCK ) )	
				context.append( ContextItem( MR_LANG( 'Remove selections' ), CONTEXT_CLEAR_MARK ) )
				if E_SUPPORT_EXTEND_RECORD_PATH :
					context.append( ContextItem( MR_LANG( 'Refresh record path' ), CONTEXT_REFRESH_NET_VOLUME ) )
				context.append( ContextItem( MR_LANG( 'Hotkeys' ), CONTEXT_ACTION_HOTKEYS ) )
				
			elif selectedPos >= 0 and selectedPos < len( self.mRecordList ) :
				recordInfo = self.mRecordList[ selectedPos ]
				playOffset = self.mDataCache.RecordItem_GetCurrentPosByKey( recordInfo.mRecordKey )
				LOG_TRACE('Offset Test =%s' %playOffset )
				if playOffset < 0 :
					playOffset = 0
				context.append( ContextItem( '%s %s' %(MR_LANG( 'Resume from'), TimeToString( int( playOffset / 1000 ), TimeFormatEnum.E_HH_MM_SS ) ), CONTEXT_RESUME_FROM ) )
				context.append( ContextItem( MR_LANG( 'Play from beginning' ), CONTEXT_PLAY_FROM_BEGINNIG ) )
				context.append( ContextItem( MR_LANG( 'Delete' ), CONTEXT_DELETE ) )
				context.append( ContextItem( MR_LANG( 'Delete all' ), CONTEXT_DELETE_ALL ) )				
				if recordInfo.mLocked:
					context.append( ContextItem( MR_LANG( 'Unlock' ), CONTEXT_UNLOCK ) )
				else :
					context.append( ContextItem( MR_LANG( 'Lock' ), CONTEXT_LOCK ) )

				context.append( ContextItem( MR_LANG( 'Rename' ), CONTEXT_RENAME ) )
				context.append( ContextItem( MR_LANG( 'Multi-select' ), CONTEXT_START_MARK ) )
				if E_SUPPORT_EXTEND_RECORD_PATH :
					context.append( ContextItem( MR_LANG( 'Refresh record path' ), CONTEXT_REFRESH_NET_VOLUME ) )
				context.append( ContextItem( MR_LANG( 'Hotkeys' ), CONTEXT_ACTION_HOTKEYS ) )

			else :
				if E_SUPPORT_EXTEND_RECORD_PATH :
					context.append( ContextItem( MR_LANG( 'Refresh record path' ), CONTEXT_REFRESH_NET_VOLUME ) )
				return
				
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context )
			dialog.doModal( )
			
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
			self.ShowDeleteConfirm( )

		elif aContextAction == CONTEXT_DELETE_ALL :
			self.ShowDeleteAllConfirm( )

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

		elif aContextAction == CONTEXT_REFRESH_NET_VOLUME :
			self.DoRefreshNetVolume( )

		elif aContextAction == CONTEXT_ACTION_HOTKEYS :
			self.ShowHotkeys( )
		else :
			LOG_ERR( 'Unknown Context Action' )


	def DoRefreshNetVolume( self, aExtenal = False ) :
		self.OpenBusyDialog( )
		defPath_old = ElisPropertyEnum( 'Record Default Path Change', self.mCommander ).GetPropString( )
		retVal, lblLine = self.mDataCache.InitNetworkVolume( )
		self.CloseBusyDialog( )

		defPath_cur = ElisPropertyEnum( 'Record Default Path Change', self.mCommander ).GetPropString( )
		if defPath_old != defPath_cur :
			lblLine = MR_LANG( 'Recordings will be temporarily stored on your hard drive' )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Inaccessible folder' ), lblLine )
			dialog.doModal( )

		lblTitle = MR_LANG( 'Fail' )
		if retVal == 0 :
			if aExtenal :
				LOG_TRACE( 'refresh volume Done' )
				return

			self.Flush( )
			self.Load( )
			self.UpdateList( )
			return

		elif retVal < 0 :
			lblTitle = MR_LANG( 'Error' )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( lblTitle, lblLine )
		dialog.doModal( )


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
			dialog.SetDialogProperty( MR_LANG( 'Delete File' ), MR_LANG( 'Are you sure you want to delete this file?' ) )
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
		dialog.SetDialogProperty( MR_LANG( 'Delete All Files' ), MR_LANG( 'Are you sure you want to delete%s all your recorded files?' )% NEW_LINE )
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

			#deprecated
			#for recInfo in self.mRecordList :
			#	self.mDataCache.Record_DeleteRecord( recInfo.mRecordKey, self.mServiceType )
			self.mDataCache.Record_DeleteAllRecord( self.mServiceType )

			self.CloseBusyDialog( )

			self.Flush( )
			self.Load( )
			self.UpdateList( )
			self.UpdateSelectedPosition( )
			self.UpdateArchiveInfomation( )


	def ShowRenameDialog( self ) :
		selectedPos = self.GetSelectedPosition( )	
		if self.mRecordList[ selectedPos ].mLocked == True :
			if self.CheckPincode( ) == False :
				return False
		
		try :
			kb = xbmc.Keyboard( self.mRecordList[ selectedPos ].mRecordName, MR_LANG( 'Enter New Name' ), False )
			kb.doModal( )
			if kb.isConfirmed( ) :
				newName = kb.getText( )
				LOG_TRACE( 'newName len=%d' %len( newName ) )
				if len( newName ) < MININUM_KEYWORD_SIZE :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'A filename must be at least %d characters long' ) % MININUM_KEYWORD_SIZE )
					dialog.doModal( )
					return
				else :

					LOG_TRACE( 'Key=%d ServiceType=%d Name=%s %s' %(self.mRecordList[ selectedPos ].mRecordKey,  self.mServiceType, self.mRecordList[ selectedPos ].mRecordName, newName ) )
					self.mDataCache.Record_Rename( self.mRecordList[ selectedPos ].mRecordKey, self.mServiceType, newName )
					self.mRecordListItems[ selectedPos ].setLabel2( newName )	
					self.mRecordList[ selectedPos ].mRecordName = newName
					xbmc.executebuiltin( 'container.refresh' )
					self.UpdateArchiveInfomation( )
					

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	def DoDelete( self, aDeleteList ) :
		if len( aDeleteList ) > 0 :
			self.OpenBusyDialog( )

			"""
			#deprecated
			count = len( aDeleteList )
			for i in range( count ) :
				position = aDeleteList[i]
				LOG_TRACE( 'i=%d serviceType=%d key=%d' %( position, self.mServiceType, self.mRecordList[position].mRecordKey ) )
				self.mDataCache.Record_DeleteRecord( self.mRecordList[position].mRecordKey, self.mServiceType )
			"""

			keyList = []
			testList = []
			for i in range( len( aDeleteList ) ) :
				position = aDeleteList[i]
				#LOG_TRACE( 'i=%d serviceType=%d key=%d' %( position, self.mServiceType, self.mRecordList[position].mRecordKey ) )
				recKey = ElisEInteger( )
				recKey.mParam = self.mRecordList[position].mRecordKey
				keyList.append( recKey )
				testList.append( self.mRecordList[position].mRecordKey )
			self.mDataCache.Record_DeleteByKeyList( self.mServiceType, keyList )
			LOG_TRACE( '---------------deleteList[%s]'% testList )

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

					if self.mPlatform.IsPrismCube( ) :
						thumbnaillist = []
						thumbnaillist = glob.glob( os.path.join( '/mnt/hdd0/pvr/thumbnail', 'record_thumbnail_%d_*.jpg' % self.mRecordList[ position ].mRecordKey ) )
						if len( thumbnaillist ) > 0 :
							recItem.setProperty( 'RecIcon', thumbnaillist[0] )
						else :
							recItem.setProperty( 'RecIcon', E_DEFAULT_THUMBNAIL_ICON )

					else :
						recItem.setProperty( 'RecIcon', E_DEFAULT_THUMBNAIL_ICON )
						

			self.DoClearMark( )
			xbmc.executebuiltin( 'container.refresh' )
			#self.SetFocusList( self.mViewMode )


	def DoStartMark( self ) :
		self.mMarkMode = True


	def DoClearMark( self ) :
		self.mMarkMode = False

		if self.mRecordListItems == None or ( self.mRecordListItems and len( self.mRecordListItems ) < 1 ) :
			return
 
		for listItem in self.mRecordListItems :
			listItem.setProperty( 'Marked', 'False' )


	def ShowHotkeys( self ) :
		lblPlaybackPause = '%s/%s'% ( MR_LANG( 'Playback' ),  MR_LANG( 'Pause' ) )
		context = [ ( 'OSDPlayNF_Rotated.png', '', MR_LANG( 'Extra Options' ) ), ( 'OSDPlayPauseNF.png', '', lblPlaybackPause ), ( 'OSDOK.png', '', MR_LANG( 'Playback' ) ) , ( 'OSDStopNF.png', '', MR_LANG( 'Stop' ) ) , ( 'OSDTVRadioNF.png', '', MR_LANG( 'TV/Radio' ) ) , ( 'OSDBackNF.png', 'OSDMenuNF.png', MR_LANG( 'Go Back' ) ) ]

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_HOTKEYS )
		dialog.SetProperty( context )
		dialog.doModal( )


	def DoMarkToggle( self ) :
		if self.mRecordListItems == None or ( self.mRecordListItems and len( self.mRecordListItems ) < 1 ) :
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
			
		#xbmc.executebuiltin('container.refresh')


	def CheckPincode( self ) :
		savedPincode = ElisPropertyInt( 'PinCode', self.mCommander ).GetProp( )
		pincodeDialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
#		pincodeDialog.SetDialogProperty( 'Input Pincode', '', 4, True )
		pincodeDialog.SetDialogProperty( MR_LANG( 'Enter PIN Code' ), '', 4, True )
		pincodeDialog.doModal( )
		
		if pincodeDialog.IsOK( ) == E_DIALOG_STATE_YES :
			inputPincode = int( pincodeDialog.GetString( ) )
			if len( pincodeDialog.GetString( ) ) != 4 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'The PIN code must be 4-digit long' ) )
	 			dialog.doModal( )
	 			return False
			LOG_TRACE( 'Input pincode=%d savedPincode=%d' %( savedPincode, inputPincode) )
			if inputPincode == savedPincode :
				return True
			else :
				infoDialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				infoDialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Sorry, that PIN code does not match' ) )
	 			infoDialog.doModal( )

		return False


	def Close( self ) :
		self.setProperty( 'SetBackgroundColor', '16777215' )
		self.mEventBus.Deregister( self )
		SetLock2( True )
		self.mEnableThread = False
		SetLock2( False )
		if self.mPlayProgressThread :
			self.mPlayProgressThread.join( )

		if self.mUpdateInfomationTimer and self.mUpdateInfomationTimer.isAlive() :
			self.mUpdateInfomationTimer.cancel( )		


	def UpdateSelectedPosition( self ) :
		selectedPos = self.GetSelectedPosition( )
		if selectedPos < 0 :
			self.setProperty( 'SelectedPosition', '0' )
		else :
			self.setProperty( 'SelectedPosition', '%d' % ( selectedPos + 1 ) )


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
				self.setProperty( 'ChannelName', recInfo.mChannelName )
				self.setProperty( 'RecDate',  TimeToString( recInfo.mStartTime, TimeFormatEnum.E_AW_DD_MM_YYYY_HH_MM ) )
				recDuration =  int( recInfo.mDuration / 60 )
				if ( recInfo.mDuration % 60 ) != 0 :
					recDuration += 1
				self.setProperty( 'RecDuration',  '%d%s' %( recDuration, MR_LANG( 'min(s)' ) ) )
				self.setProperty( 'RecName', recInfo.mRecordName )

				#has lock
				isLock = E_TAG_FALSE
				if recInfo.mLocked == 1 :
					isLock = E_TAG_TRUE
				self.setProperty( 'HasLock', isLock )

				#age info
				iEPG = self.mDataCache.RecordItem_GetEventInfo( recInfo.mRecordKey )
				UpdatePropertyByAgeRating( self, iEPG )

				#component
				#UpdatePropertyByCacheData( self, pmtEvent, E_XML_PROPERTY_TELETEXT )
				self.setProperty( E_XML_PROPERTY_SUBTITLE, HasEPGComponent( iEPG, ElisEnum.E_HasSubtitles ) )
				self.setProperty( E_XML_PROPERTY_DOLBY,    HasEPGComponent( iEPG, ElisEnum.E_HasDolbyDigital ) )
				self.setProperty( E_XML_PROPERTY_HD,       HasEPGComponent( iEPG, ElisEnum.E_HasHDVideo ) )

				if E_SUPPORT_EXTEND_RECORD_PATH :
					netVolume = E_TAG_FALSE
					#mountInfo = self.mDataCache.Record_GetMountInfo( recInfo.mRecordKey )
					mountInfo = recInfo.mMountInfo
					if mountInfo :
						mntType = 'HDD'
						netVolume = E_TAG_TRUE
						netVolumeUSB = E_TAG_FALSE
						retPath = os.path.dirname( mountInfo )
						if retPath == E_DEFAULT_PATH_SMB_POSITION or \
						   retPath == E_DEFAULT_PATH_NFS_POSITION or \
						   retPath == E_DEFAULT_PATH_FTP_POSITION :
							mntType = 'NAS'
						elif bool( re.search( '%s\w\d+'% E_DEFAULT_PATH_USB_POSITION, mountInfo, re.IGNORECASE ) ) :
							mntType = 'USB'
							netVolumeUSB = E_TAG_TRUE
						else :
							#internal
							netVolume = E_TAG_FALSE
							netVolumeUSB = E_TAG_FALSE

						self.setProperty( 'iNetVolumeType', mntType )
						self.setProperty( 'iNetVolumeUSB', netVolumeUSB )
						self.setProperty( 'iNetVolumeName', os.path.basename( mountInfo ) )
					self.setProperty( 'RecNetVolume', netVolume )

			else :
				self.ResetArchiveInfomation( )
		else :
			self.ResetArchiveInfomation( )


	def ResetArchiveInfomation( self ) :
		self.setProperty( 'ChannelName', '' )
		self.setProperty( 'RecDate', '' )
		self.setProperty( 'RecDuration',  '' )
		self.setProperty( 'RecName', '' )				
		self.setProperty( 'RecNetVolume', E_TAG_FALSE )
		self.setProperty( 'iNetVolumeUSB', E_TAG_FALSE )
		self.setProperty( 'iNetVolumeType', '' )
		self.setProperty( 'iNetVolumeName', '' )
		self.setProperty( 'EPGAgeRating', '' )
		self.setProperty( 'HasAgeRating', 'None' )
		self.setProperty( 'HasLock', E_TAG_FALSE )
		self.setProperty( E_XML_PROPERTY_TELETEXT, E_TAG_FALSE )
		self.setProperty( E_XML_PROPERTY_SUBTITLE, E_TAG_FALSE )
		self.setProperty( E_XML_PROPERTY_DOLBYPLUS, E_TAG_FALSE )
		self.setProperty( E_XML_PROPERTY_DOLBY, E_TAG_FALSE )
		self.setProperty( E_XML_PROPERTY_HD,       E_TAG_FALSE )


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

		if self.mViewMode == E_VIEW_LIST :
			#self.UpdateControlListSelectItem( self.mCtrlCommonList, selectedPos )
			self.mCtrlCommonList.selectItem( selectedPos )
		elif self.mViewMode == E_VIEW_THUMBNAIL :
			#self.UpdateControlListSelectItem( self.mCtrlThumbnailList, selectedPos )
			self.mCtrlThumbnailList.selectItem( selectedPos )
		elif self.mViewMode == E_VIEW_POSTER_WRAP :
			#self.UpdateControlListSelectItem( self.mCtrlPosterwrapList, selectedPos )
			self.mCtrlPosterwrapList.selectItem( selectedPos )
		elif self.mViewMode == E_VIEW_FANART :
			#self.UpdateControlListSelectItem( self.mCtrlFanartList, selectedPos )
			self.mCtrlFanartList.selectItem( selectedPos )
		else :
			LOG_WARN( 'Unknown View Mode' )

		if self.mUpdateInfomationTimer and self.mUpdateInfomationTimer.isAlive() :
			self.mUpdateInfomationTimer.cancel( )		
		
		self.mUpdateInfomationTimer = threading.Timer( 0.5, self.AsyncUpdateInfomation )
		self.mUpdateInfomationTimer.start( )

	def AsyncUpdateInfomation( self ) :
		self.UpdateSelectedPosition( )
		self.UpdateArchiveInfomation( )


	@SetLock
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
			self.setProperty( 'PvrPlay', 'False' )
			if self.mEnableThread == True and self.mPlayProgressThread :
				self.mEnableThread = False
				self.mPlayProgressThread.join( )

			chName = MR_LANG( 'No Channel' )
			self.mCtrlPlayProgress.setPercent( 0 )			
			iChannelList = self.mDataCache.Channel_GetList( )
			if iChannelList and len( iChannelList ) > 0 :
				channel = self.mDataCache.Channel_GetCurrent( )
				if channel :
					chName = '%s'% channel.mName
				else :
					chName = ''

			self.mCtrlPlayName.setLabel( chName )

		self.mCtrlPlayStart.setLabel( '' )
		self.mCtrlPlayEnd.setLabel( '' )


	@RunThread
	def PlayProgressThread( self ) :
		self.mCtrlPlayProgress.setPercent( 0 ) 
		cnt = 0
		while self.mEnableThread :
			time.sleep( 0.01 )
			if ( cnt % 50 ) == 0 :
				self.UpdatePlayProgress( )
			cnt = cnt + 1


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

		#LOG_TRACE( 'Update PlayProgress = %d [%d,%d,%d]' %( self.mPlayPerent, status.mPlayTimeInMs, status.mStartTimeInMs, status.mEndTimeInMs ) )
		
		self.mCtrlPlayProgress.setPercent( self.mPlayPerent )
		self.mCtrlPlayStart.setLabel( '%s' %(TimeToString( int( status.mPlayTimeInMs / 1000 ), TimeFormatEnum.E_HH_MM_SS ) ) )
		#self.mCtrlPlayEnd.setLabel( '%s' %(TimeToString( int( status.mEndTimeInMs / 1000 ), TimeFormatEnum.E_AH_MM_SS ) ) )
		if self.mPlayingRecord :
			self.mCtrlPlayEnd.setLabel( '%s' %(TimeToString( self.mPlayingRecord.mDuration, TimeFormatEnum.E_AH_MM_SS ) ) )


	def GetPlayingRecord( self ) :
		status = self.mDataCache.Player_GetStatus( )
		if status.mMode == ElisEnum.E_MODE_PVR :
			return self.mPlayingRecord
		else :
			return None


	def SetFocusList( self, aMode ) :
		if aMode == E_VIEW_LIST :
			self.setFocusId( LIST_ID_COMMON_RECORD )
		elif aMode == E_VIEW_THUMBNAIL :
			self.setFocusId( LIST_ID_THUMBNAIL_RECORD )
		elif aMode == E_VIEW_POSTER_WRAP :
			self.setFocusId( LIST_ID_POSTERWRAP_RECORD )
		elif aMode == E_VIEW_FANART :
			self.setFocusId( LIST_ID_FANART_RECORD )
		else :
			LOG_ERR( 'SetFocusList fail' )


	def UpdateFootor( self ) :
		if self.mRecordList == None :
			self.setProperty( 'ArchiveFootor', 'False' )
		else :
			self.setProperty( 'ArchiveFootor', 'True' )

