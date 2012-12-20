from pvr.gui.WindowImport import *
import time

E_CONTROL_ID_LIST = 3850

DIALOG_BUTTON_CLOSE_ID = 3800
DIALOG_HEADER_LABEL_ID = 3801
DIALOG_HEADER_LABEL2_ID = 3805
DIALOG_BUTTON_OK_ID = 3802
DIALOG_LABEL_POS_ID = 3803

CONTEXT_RESUME_FROM	= 0
CONTEXT_DELETE		= 1
CONTEXT_DELETE_ALL	= 2
CONTEXT_START_MARK	= 3
CONTEXT_CLEAR_MARK	= 4

class DialogBookmark( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )	
		self.mBookmarkList = []
		self.mIsOk = None
		self.mCtrlList = None
		self.mListItems = None
		self.mRecordInfo = None
		self.mTitle = ''
		self.mSubTitle = ''


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.WindowDialog( self.mWinId )

		self.mMarkList = []
		self.mThumbnailHash = {}
		self.mMarkMode = False
		self.mCtrlList = self.getControl( E_CONTROL_ID_LIST )
		self.mCtrlPos  = self.getControl( DIALOG_LABEL_POS_ID )
		self.mIsDelete = False

		self.InitList( )
		self.mEventBus.Register( self )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.mIsOk = actionId
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.Close( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
			
		elif actionId == Action.ACTION_PARENT_DIR :
			if self.mMarkList and len( self.mMarkList ) > 0 :
				self.DoClearMark( )
				self.mMarkList = []
			else :
				self.Close( )

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN or \
			 actionId == Action.ACTION_PAGE_UP or actionId == Action.ACTION_PAGE_DOWN :
			idx = self.mCtrlList.getSelectedPosition( )
			self.mCtrlPos.setLabel( '%s'% ( idx + 1 ) )

		elif actionId == Action.ACTION_STOP :
			self.Close( )

		elif actionId == Action.ACTION_PLAYER_PLAY or actionId == Action.ACTION_PAUSE :
			self.StartBookmarkPlayback( )
			self.Close( )

		elif actionId == Action.ACTION_CONTEXT_MENU :
			self.ShowContextMenu( )


	def onClick( self, aControlId ) :
		if aControlId == DIALOG_BUTTON_CLOSE_ID :
			self.mMarkList = None
			xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )

		elif aControlId == E_CONTROL_ID_LIST :
			if self.mMarkMode == True :
				self.DoMarkToggle( )
			else :
				self.StartBookmarkPlayback( )
				xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )

		elif aControlId == DIALOG_BUTTON_OK_ID :
			self.StartBookmarkPlayback( )
			xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )	


	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowDialogId( ) :
			if aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or \
			   aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
				xbmc.executebuiltin('xbmc.Action(stop)')

			elif aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
				xbmc.executebuiltin('xbmc.Action(stop)')


	def InitList( self ) :
		self.mCtrlList.reset( )
		self.mListItems = []
		self.mMarkList = []

		if self.mRecordInfo == None or self.mRecordInfo.mError != 0 :
			return

		self.BookmarkItems( )
		self.getControl( DIALOG_HEADER_LABEL_ID ).setLabel( self.mTitle )
		self.getControl( DIALOG_HEADER_LABEL2_ID ).setLabel( self.mSubTitle )
		self.mCtrlList.addItems( self.mListItems )

		idx = self.mCtrlList.getSelectedPosition( )
		self.mCtrlPos.setLabel( '%s'% ( idx + 1 ) )


	def InitThumbnail( self ) :
		self.mThumbnailHash = {}

		thumbnaillist = []
		thumbnaillist = glob.glob( os.path.join( '/mnt/hdd0/pvr/bookmark/%d'% self.mRecordInfo.mRecordKey, 'record_bookmark_%d_*.jpg' % self.mRecordInfo.mRecordKey ) )

		LOG_TRACE('hash[%s] list[%s]'% (self.mThumbnailHash, thumbnaillist) )
		if thumbnaillist == None or len( thumbnaillist ) < 1 :
			return 

		for mfile in thumbnaillist :
			try :
				self.mThumbnailHash[int( os.path.basename(mfile).split('_')[3] )] = mfile
			except Exception, ex :
				LOG_ERR( 'Exception %s'% ex )
				continue


	def BookmarkItems( self ) :
		self.mTitle = 'P%04d.%s'% ( self.mRecordInfo.mChannelNo, self.mRecordInfo.mChannelName )
		startTime = self.mRecordInfo.mStartTime
		duration = self.mRecordInfo.mDuration

		lblStart = TimeToString( startTime, TimeFormatEnum.E_HH_MM )
		lblEnd = TimeToString( startTime + duration, TimeFormatEnum.E_HH_MM )
		self.mSubTitle = '%s (%s ~ %s)'% ( self.mRecordInfo.mRecordName, lblStart, lblEnd )

		self.mBookmarkList = self.mDataCache.Player_GetBookmarkList( self.mRecordInfo.mRecordKey )
		if self.mBookmarkList == None or len( self.mBookmarkList ) < 1 or self.mBookmarkList[0].mError != 0 :
			return 

		self.InitThumbnail( )

		LOG_TRACE('bookmark[%s]'% ClassToList('convert', self.mBookmarkList) )
		LOG_TRACE('thumnail[%s]'% self.mThumbnailHash )

		for idx in range( len( self.mBookmarkList ) ) :
			
			listItem = xbmcgui.ListItem( '%s'% TimeToString( self.mBookmarkList[idx].mTimeMs / 1000, TimeFormatEnum.E_AH_MM_SS ) )

			listItem.setProperty( 'RecIcon',     '%s'% self.mThumbnailHash.get( self.mBookmarkList[idx].mTimeMs, None ) )
			listItem.setProperty( 'RecTotal',    '%s'% TimeToString( duration, TimeFormatEnum.E_AH_MM_SS ) )
			listItem.setProperty( 'RecDate',     TimeToString( self.mRecordInfo.mStartTime ) )

			percent = ( self.mBookmarkList[idx].mTimeMs / ( duration * 1000.0 ) ) * 100
			LOG_TRACE('progress[%s] (%s / %s * 1000) * 100'% (percent, self.mBookmarkList[idx].mTimeMs, duration))
			listItem.setProperty( 'percent', '%s'% percent )
			listItem.setProperty( 'iPos', E_TAG_TRUE )

			self.mListItems.append( listItem )


	def ShowContextMenu( self ) :
		if self.mBookmarkList == None or len( self.mBookmarkList ) < 1 or \
		   self.mCtrlList == None or self.mListItems == None or len( self.mListItems ) < 1 :
			return

		try :
			selectedPos = self.mCtrlList.getSelectedPosition( )
			playOffset = self.mBookmarkList[selectedPos].mTimeMs

			context = []
			markedList = self.GetSelectedList( )

			if markedList and len( markedList ) > 1 :
				context.append( ContextItem( MR_LANG( 'Delete' ), CONTEXT_ACTION_DELETE ) )
				context.append( ContextItem( MR_LANG( 'Remove selections' ), CONTEXT_ACTION_CLEAR_MARK ) )	
			else :
				context.append( ContextItem( MR_LANG( 'Resume from %s'% ( TimeToString( int( playOffset / 1000 ), TimeFormatEnum.E_AH_MM_SS ) )), CONTEXT_ACTION_RESUME_FROM ) )
				context.append( ContextItem( MR_LANG( 'Delete' ), CONTEXT_ACTION_DELETE ) )
				context.append( ContextItem( MR_LANG( 'Delete all' ), CONTEXT_ACTION_DELETE_ALL ) )
				context.append( ContextItem( MR_LANG( 'Multi-select' ), CONTEXT_ACTION_START_MARK ) )

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context )
			dialog.doModal( )
			
			contextAction = dialog.GetSelectedAction( )
			self.DoContextAction( contextAction ) 

		except Exception, ex :
			LOG_ERR( 'Exception %s'% ex )


	def DoContextAction( self, aContextAction ) :
		LOG_TRACE( 'aContextAction=%d' %aContextAction )

		if aContextAction == CONTEXT_ACTION_RESUME_FROM :
			self.StartBookmarkPlayback( )

		elif aContextAction == CONTEXT_ACTION_DELETE :
			self.DoDeleteConfirm()

		elif aContextAction == CONTEXT_ACTION_DELETE_ALL :
			self.ShowDeleteAllConfirm()

		elif aContextAction == CONTEXT_ACTION_START_MARK :
			self.DoStartMark( )

		elif aContextAction == CONTEXT_ACTION_CLEAR_MARK :
			self.DoClearMark( )
		else :
			LOG_ERR( 'Unknown Context Action' )


	def StartBookmarkPlayback( self ) :
		if self.mBookmarkList == None or len( self.mBookmarkList ) < 1 or \
		   self.mCtrlList == None or self.mListItems == None or len( self.mListItems ) < 1 :
			return

		selectedPos = self.mCtrlList.getSelectedPosition( )
		playOffset = self.mBookmarkList[selectedPos].mTimeMs
		LOG_TRACE('bookmark idx[%s] key[%s] pos[%s]'% ( selectedPos, self.mRecordInfo.mRecordKey, TimeToString( playOffset / 1000, TimeFormatEnum.E_AH_MM_SS ) ) )

		#self.mDataCache.Player_StartInternalRecordPlayback( self.mRecordInfo.mRecordKey, self.mRecordInfo.mServiceType, playOffset, 100 )
		self.mDataCache.Player_JumpToIFrame( playOffset )


	def DoDeleteConfirm( self ) :
		selectedPos = self.mCtrlList.getSelectedPosition( )
		playOffset = self.mBookmarkList[selectedPos].mOffset

		if not self.mMarkList :
			self.mMarkList.append( selectedPos )

		for idx in self.mMarkList :
			self.mIsDelete = True
			playOffset = self.mBookmarkList[idx].mOffset
			ret = self.mDataCache.Player_DeleteBookmark( self.mRecordInfo.mRecordKey, playOffset )
			LOG_TRACE( 'bookmark delete[%s %s %s %s] ret[%s]'% (self.mRecordInfo.mRecordKey, idx, playOffset,self.mBookmarkList[selectedPos].mTimeMs,ret ) )

		self.InitList( )


	def ShowDeleteAllConfirm( self ) :
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( MR_LANG( 'Delete all bookmarks' ), MR_LANG( 'Are you sure you want to remove\nall your bookmarks?' ) )
		dialog.doModal( )

		if dialog.IsOK( ) != E_DIALOG_STATE_YES :
			return

		self.mMarkList = []
		for idx in range( len( self.mBookmarkList ) ) :
			self.mMarkList.append( idx )

		self.DoDeleteConfirm( )


	def DoStartMark( self ) :
		self.mMarkMode = True


	def DoClearMark( self ) :
		self.mMarkMode = False
		self.mMarkList = []

		if self.mListItems == None :
			return
 
		for listItem in self.mListItems :
			listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_FALSE )


	def DoMarkToggle( self ) :
		idx = 0
		isExist = False

		if self.mBookmarkList == None or len( self.mBookmarkList ) < 1 or \
		   self.mCtrlList == None or self.mListItems == None or len( self.mListItems ) < 1 :
			return

		aPos = self.mCtrlList.getSelectedPosition( )

		#aready mark is mark delete
		for i in self.mMarkList :
			if i == aPos :
				self.mMarkList.pop( idx )
				isExist = True
			idx += 1

		#do not exist is append mark
		if isExist == False : 
			self.mMarkList.append( aPos )

		listItem = self.mCtrlList.getListItem( aPos )

		#mark toggle: disable/enable
		if listItem.getProperty( E_XML_PROPERTY_MARK ) == E_TAG_TRUE : 
			listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_FALSE )
		else :
			listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_TRUE )

		self.mCtrlList.selectItem( aPos + 1 )
		time.sleep( 0.05 )

		nPos = -1
		while nPos < 0 :
			nPos = self.mCtrlList.getSelectedPosition( )
			if nPos != len( self.mBookmarkList ) - 1 and nPos == aPos :
				time.sleep( 0.02 )
				nPos = -1

		self.mCtrlPos.setLabel( '%s'% ( nPos + 1 ) )


	def SetDefaultProperty( self, aRecord = None ) :
		self.mRecordInfo = aRecord


	def GetSelectedList( self ) :
		return self.mMarkList


	def GetCloseStatus( self ) :
		return self.mIsOk


	def IsDeleteBookmark( self ) :
		return self.mIsDelete


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.CloseDialog( )
		
