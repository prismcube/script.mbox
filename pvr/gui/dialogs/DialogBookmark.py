from pvr.gui.WindowImport import *
import time

E_CONTROL_ID_LIST = 3850

DIALOG_BUTTON_CLOSE_ID = 3800
DIALOG_HEADER_LABEL_ID = 3801
DIALOG_HEADER_LABEL2_ID = 3805
DIALOG_BUTTON_OK_ID = 3802
DIALOG_LABEL_POS_ID = 3803


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
		self.mMarkMode = False
		self.mCtrlList = self.getControl( E_CONTROL_ID_LIST )
		self.mCtrlPos =  self.getControl( DIALOG_LABEL_POS_ID )

		self.InitList( )
		self.mEventBus.Register( self )

		"""
		thumbnaillist = []
		thumbnaillist = glob.glob( os.path.join( '/mnt/hdd0/pvr/bookmark', 'record_thumbnail_%d_*.jpg' % 7692 ) )
		icon=[]
		icon.append('IconNotAvailable.png')
		icon.append('RecIconSample.png')
		icon.append(thumbnaillist[0])

		self.mListItems = []
		for i in range(10) :
			listItem = xbmcgui.ListItem( '%s %d'%( 'Offset', i ) )
			listItem.setProperty( 'RecIcon',     icon[i%3] )
			listItem.setProperty( 'RecTotal',    '%s'% (TimeToString( (i+1)*20, TimeFormatEnum.E_AH_MM_SS )) )
			listItem.setProperty( 'RecDate',     '%s'% (TimeToString( time.time(), TimeFormatEnum.E_AW_DD_MM_YYYY )) )
			listItem.setProperty( 'RecDuration', '%sm'% i )
			listItem.setProperty( 'percent', '%s'% ( ((i%3)+1) * 20) )
			listItem.setProperty( 'iPos', 'True' )
			self.mListItems.append( listItem )

			self.mBookmarkList.append( icon[ i % 3 ] )
		self.mCtrlList.addItems( self.mListItems )

		idx = self.mCtrlList.getSelectedPosition( )
		self.mCtrlPos.setLabel( '%s'% ( idx + 1 ) )
		"""

	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.mIsOk = actionId
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.mMarkList = None
			self.Close( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
			
		elif actionId == Action.ACTION_PARENT_DIR :
			if self.mMarkList and len( self.mMarkList ) > 0 :
				self.DoClearMark( )
				self.mMarkList = None
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
			self.Close( )

		elif aControlId == E_CONTROL_ID_LIST :
			if	self.mMarkMode == True :
				self.DoMarkToggle( )
			else :
				self.StartBookmarkPlayback( )
				self.Close( )

		elif aControlId == DIALOG_BUTTON_OK_ID :
			self.Close( )		


	def onFocus( self, aControlId ) :
		pass


	@GuiLock
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


	def BookmarkItems( self ) :
		self.mTitle = 'P%04d.%s'% ( self.mRecordInfo.mChannelNo, self.mRecordInfo.mChannelName )
		startTime = self.mRecordInfo.mStartTime
		duration = self.mRecordInfo.mDuration

		lblStart = TimeToString( startTime, TimeFormatEnum.E_HH_MM )
		lblEnd = TimeToString( startTime + duration, TimeFormatEnum.E_HH_MM )
		self.mSubTitle = '%s (%s ~ %s)'% ( self.mRecordInfo.mRecordName, lblStart, lblEnd )

		self.mBookmarkList = self.mDataCache.Player_GetBookmarkList( self.mRecordInfo.mRecordKey )
		if self.mBookmarkList == None or len( self.mBookmarkList ) < 1 :
			return 

		thumbnaillist = []
		thumbnaillist = glob.glob( os.path.join( '/mnt/hdd0/pvr/bookmark', 'record_thumbnail_%d_*.jpg' % self.mRecordInfo.mRecordKey ) )

		for idx in range( len( self.mBookmarkList ) ) :
			
			listItem = xbmcgui.ListItem( '%s'% TimeToString( self.mBookmarkList[idx].mTimeMs / 1000, TimeFormatEnum.E_AH_MM_SS ) )

			listItem.setProperty( 'RecIcon',     thumbnaillist[idx] )
			listItem.setProperty( 'RecTotal',    '%s'% TimeToString( duration, TimeFormatEnum.E_AH_MM_SS ) )
			listItem.setProperty( 'RecDate',     TimeToString( self.mRecordInfo.mStartTime ) )
			listItem.setProperty( 'RecDuration', '%dm' % ( duration / 60 ) )

			percent = self.mBookmarkList[idx].mTimeMs / ( self.mBookmarkList[idx].mTimeMs + duration * 1000 )
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
				context.append( ContextItem( MR_LANG( 'Delete All' ), CONTEXT_ACTION_DELETE_ALL ) )
				context.append( ContextItem( MR_LANG( 'Remove Selections' ), CONTEXT_ACTION_CLEAR_MARK ) )	

			else :
				context.append( ContextItem( MR_LANG( 'Resume from %s'% ( TimeToString( int( playOffset / 1000 ), TimeFormatEnum.E_AH_MM_SS ) )), CONTEXT_ACTION_RESUME_FROM ) )
				context.append( ContextItem( MR_LANG( 'Delete' ), CONTEXT_ACTION_DELETE ) )
				context.append( ContextItem( MR_LANG( 'Multi-Select' ), CONTEXT_ACTION_START_MARK ) )

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context )
			dialog.doModal( )
			
			contextAction = dialog.GetSelectedAction( )
			self.DoContextAction( contextAction ) 

		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


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
		playOffset = self.mBookmarkList[selectedPos].mTimeMs

		if not self.mMarkList :
			self.mMarkList.append( selectedPos )

		for idx in self.mMarkList :
			playOffset = self.mBookmarkList[idx].mTimeMs
			ret = self.mDataCache.Player_DeleteBookmark( self.mRecordInfo.mRecordKey, playOffset )
			LOG_TRACE( 'bookmark delete[%s]'% ret )

		self.InitList( )


	def ShowDeleteAllConfirm( self ) :
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( MR_LANG( 'Delete Bookmark' ), MR_LANG( 'Do you want to delete the selected file(s)?' ) )
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

		if self.mListItems == None :
			return
 
		for listItem in self.mListItems :
			listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_FALSE )

		self.mMarkList = []


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


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.CloseDialog( )
		
