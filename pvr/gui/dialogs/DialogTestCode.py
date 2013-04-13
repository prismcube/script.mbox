from pvr.gui.WindowImport import *
import time, math


E_CONTROL_ID_LIST_SHOW_BOOKMARK		= 500
E_CONTROL_ID_LIST_SHOW_PROGRESS2	= 200

class DialogTestCode( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mMode = ElisEnum.E_MODE_LIVE


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.mCtrlBookMarkList      = self.getControl( E_CONTROL_ID_LIST_SHOW_BOOKMARK )
		self.mCtrlProgress2      = self.getControl( E_CONTROL_ID_LIST_SHOW_PROGRESS2 )

		self.mThumbnailList = []
		self.mBookmarkList = []
		self.mBookmarkButton = []
		self.mPlayingRecordInfo = None

		status = self.mDataCache.Player_GetStatus( )
		self.mMode = status.mMode

		self.LoadToBookmark( )
		self.mMoveP = 0


	def onAction( self, aAction ) :
		if aAction == Action.ACTION_PREVIOUS_MENU or aAction == Action.ACTION_PARENT_DIR :
			self.CloseDialog( )

		elif aAction == Action.ACTION_SELECT_ITEM :
			pass

		elif aAction == Action.ACTION_STOP :
			self.CloseDialog( )

		elif aAction == Action.ACTION_PLAYER_PLAY or aAction == Action.ACTION_PAUSE :
			self.CloseDialog( )

		elif aAction == Action.ACTION_MOVE_LEFT :
			self.MoveTest( -10 )

		elif aAction == Action.ACTION_MOVE_RIGHT :
			self.MoveTest( 10 )


	def onClick( self, aControlId ):
		pass


	def onFocus( self, aControlId ):
		pass


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowDialogId( ) :
			#LOG_TRACE( '---------CHECK onEVENT winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId( )) )
			if aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
				LOG_TRACE( 'ElisEventPlaybackEOF mType[%d]'% ( aEvent.mType ) )

				if self.mFlag_OnEvent != True :
					return -1

				elif aEvent.mType == ElisEnum.E_EOF_END :
					LOG_TRACE( 'EventRecv EOF_END' )
					xbmc.executebuiltin('xbmc.Action(stop)')
					#self.TimeshiftAction( E_CONTROL_ID_BUTTON_STOP )

			elif aEvent.getName( ) == ElisEventChannelChangedByRecord.getName( ) :
				xbmc.executebuiltin('xbmc.Action(previousmenu)')

		else:
			LOG_TRACE( 'TimeshiftPlate winID[%d] this winID[%d]'% ( self.mWinId, xbmcgui.getCurrentWindowId( ) ) )


	def MoveTest( self, aDirection ) :
		self.mMoveP += aDirection
		if self.mMoveP < 0 : 
			self.mMoveP = 0
		elif self.mMoveP > 100 :
			self.mMoveP = 100

		self.mCtrlProgress2.setPercent( self.mMoveP )


	def LoadToBookmark( self ) :
		self.mThumbnailList = []
		self.mBookmarkList = []
		self.Flush( )

		if self.mMode != ElisEnum.E_MODE_PVR :
			self.setProperty( 'BookMarkShow', 'False' )
			return

		playingRecord = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW ).GetPlayingRecord( )
		#LOG_TRACE('--------record[%s]'% playingRecord.mRecordKey )
		if playingRecord == None or playingRecord.mError != 0 :
			self.setProperty( 'BookMarkShow', 'False' )
			return

		self.mPlayingRecordInfo = playingRecord
		self.mBookmarkList = self.mDataCache.Player_GetBookmarkList( playingRecord.mRecordKey )
		#LOG_TRACE('--------len[%s] [%s]'% ( len( mBookmarkList ), mBookmarkList[0].mError ) )
		if self.mBookmarkList == None or len( self.mBookmarkList ) < 1 or self.mBookmarkList[0].mError != 0 :
			self.setProperty( 'BookMarkShow', 'False' )
			return 

		#for item in mBookmarkList :
		#	LOG_TRACE('timeMs[%s]'% item.mTimeMs )

		self.mThumbnailList = []
		thumbnaillist = []
		thumbnaillist = glob.glob( os.path.join( '/mnt/hdd0/pvr/bookmark/%d'% playingRecord.mRecordKey, 'record_bookmark_%d_*.jpg' % playingRecord.mRecordKey ) )

		#LOG_TRACE('len[%s] list[%s]'% ( len(thumbnaillist), thumbnaillist ) )
		thumbnailHash = {}
		if thumbnaillist and len( thumbnaillist ) > 0 :
			for mfile in thumbnaillist :
				try :
					#thumbnailHash[int( os.path.basename( mfile ).split('_')[3] )] = mfile
					self.mThumbnailList.append( mfile )

				except Exception, e :
					LOG_ERR( 'Error exception[%s]'% e )
					continue

		#LOG_TRACE('len[%s] hash[%s]'% ( len(thumbnailHash), thumbnailHash ) )
		#LOG_TRACE(' len[%s] bookmarkFile[%s]'% ( len(self.mThumbnailList), self.mThumbnailList ) )
		self.ShowBookmark( )


	def ShowBookmark( self ) :
		#self.StopAutomaticHide( )

		#1.show thumbnail on plate
		self.Flush( )
		if len( self.mBookmarkList ) < 1 :
			self.setProperty( 'BookMarkShow', 'False' )
			LOG_TRACE( 'bookmark None, show False' )
			return

		listItems = []
		idx = 0
		for i in range( len( self.mBookmarkList ) ) :
			idx += 1
			lblOffset = TimeToString( self.mBookmarkList[i].mTimeMs / 1000, TimeFormatEnum.E_AH_MM_SS )
			listItem = xbmcgui.ListItem( '%s'% lblOffset, '%s'% idx )
			listItem.setProperty( 'BookMarkThumb', self.mThumbnailList[i] )
			#LOG_TRACE('show listIdx[%s] file[%s]'% ( i, self.mThumbnailList[i] ) )

			listItems.append( listItem )
		self.mCtrlBookMarkList.addItems( listItems )

		self.setProperty( 'BookMarkShow', 'True' )


	def Flush( self ) :
		self.mCtrlBookMarkList.reset( )
		if self.mBookmarkButton and len( self.mBookmarkButton ) > 0 :
			for i in range( len( self.mBookmarkButton ) ) :
				try :
					mWin = self
					if E_SUPPORT_SINGLE_WINDOW_MODE :
						mWin = self.mRootWindow
					#self.removeControl( self.mBookmarkButton[i] )
					mWin.removeControl( self.mBookmarkButton[i] )
				except Exception, e :
					LOG_TRACE( 'except[%s]'% e )
			self.mBookmarkButton = []
			LOG_TRACE('erased Init. bookmarkButton[%s]'% self.mBookmarkButton )




