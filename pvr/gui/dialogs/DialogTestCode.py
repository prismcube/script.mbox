from pvr.gui.WindowImport import *
import time, math


E_CONTROL_ID_LIST_SHOW_BOOKMARK		= 500
E_CONTROL_ID_LIST_SHOW_PROGRESS2	= 200

E_CONTROL_ID_HOTKEY_RED_IMAGE 		= 511
E_CONTROL_ID_HOTKEY_RED_LABEL 		= 512
E_CONTROL_ID_HOTKEY_GREEN_IMAGE 	= 521
E_CONTROL_ID_HOTKEY_GREEN_LABEL 	= 522
E_CONTROL_ID_HOTKEY_YELLOW_IMAGE 	= 531
E_CONTROL_ID_HOTKEY_YELLOW_LABEL 	= 532
E_CONTROL_ID_HOTKEY_BLUE_IMAGE 		= 541
E_CONTROL_ID_HOTKEY_BLUE_LABEL 		= 542

class DialogTestCode( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mMode = ElisEnum.E_MODE_LIVE

	"""
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
	"""

	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mLimit = False
		#self.TestList( )

		self.TestLogo( )
		self.TestChannelList( )


	def onAction( self, aAction ) :
		if aAction == Action.ACTION_PREVIOUS_MENU or aAction == Action.ACTION_PARENT_DIR :
			self.mCommander.Player_SetVIdeoSize( 0, 0, 1280, 720 )
			self.CloseDialog( )

		elif aAction == Action.ACTION_SELECT_ITEM :
			if self.mLimit :
				self.mLimit = False
			else :
				self.mLimit = True
			self.TestList( )


		elif aAction == Action.ACTION_STOP :
			self.CloseDialog( )

		elif aAction == Action.ACTION_MBOX_REWIND :
			self.setProperty( 'ShowExtendInfo', E_TAG_FALSE )

		elif aAction == Action.ACTION_MBOX_FF :
			self.setProperty( 'ShowExtendInfo', E_TAG_TRUE )


		elif aAction == Action.ACTION_MOVE_UP :
			imgctrl = self.getControl( 998 )
			pos = imgctrl.getPosition( )
			imgctrl.setPosition( pos[0], pos[1] - 10 )

		elif aAction == Action.ACTION_MOVE_DOWN :
			imgctrl = self.getControl( 998 )
			pos = imgctrl.getPosition( )
			imgctrl.setPosition( pos[0], pos[1] + 10 )

		"""
		elif aAction == Action.ACTION_PLAYER_PLAY or aAction == Action.ACTION_PAUSE :
			self.TestScreen( )

		elif aAction == Action.ACTION_MOVE_DOWN :
			self.setProperty( 'iHotkeys', E_TAG_FALSE )
			self.setProperty( 'InfoPlateName', E_TAG_FALSE )
			self.setProperty( E_XML_PROPERTY_HOTKEY_RED,    E_TAG_FALSE )
			self.setProperty( E_XML_PROPERTY_HOTKEY_GREEN,  E_TAG_TRUE )
			self.setProperty( E_XML_PROPERTY_HOTKEY_YELLOW, E_TAG_TRUE )
			self.setProperty( E_XML_PROPERTY_HOTKEY_BLUE,   E_TAG_TRUE )
			self.setProperty( 'iHotkeys', E_TAG_TRUE )

		elif aAction == Action.ACTION_MOVE_UP :
			self.setProperty( 'iHotkeys', E_TAG_FALSE )
			if E_V1_2_APPLY_TEXTWIDTH_LABEL :
				ResizeImageWidthByTextSize( self.getControl( E_CONTROL_ID_HOTKEY_GREEN_LABEL ), self.getControl( E_CONTROL_ID_HOTKEY_GREEN_IMAGE ), MR_LANG( 'Number' ), self.getControl( ( E_CONTROL_ID_HOTKEY_GREEN_IMAGE - 1 ) ) )
				ResizeImageWidthByTextSize( self.getControl( E_CONTROL_ID_HOTKEY_YELLOW_LABEL ), self.getControl( E_CONTROL_ID_HOTKEY_YELLOW_IMAGE ), MR_LANG( 'Fast' ), self.getControl( ( E_CONTROL_ID_HOTKEY_YELLOW_IMAGE - 1 ) ) )
				ResizeImageWidthByTextSize( self.getControl( E_CONTROL_ID_HOTKEY_BLUE_LABEL ), self.getControl( E_CONTROL_ID_HOTKEY_BLUE_IMAGE ), MR_LANG( 'Vertical' ), self.getControl( ( E_CONTROL_ID_HOTKEY_BLUE_IMAGE - 1 ) ) )

			self.setProperty( 'InfoPlateName', E_TAG_FALSE )
			self.setProperty( E_XML_PROPERTY_HOTKEY_RED,    E_TAG_FALSE )
			self.setProperty( E_XML_PROPERTY_HOTKEY_GREEN,  E_TAG_TRUE )
			self.setProperty( E_XML_PROPERTY_HOTKEY_YELLOW, E_TAG_TRUE )
			self.setProperty( E_XML_PROPERTY_HOTKEY_BLUE,   E_TAG_TRUE )
			self.setProperty( 'iHotkeys', E_TAG_TRUE )


		elif aAction == Action.ACTION_PLAYER_PLAY or aAction == Action.ACTION_PAUSE :
			#self.CloseDialog( )
			#self.setProperty( 'iPlayerRewind', E_TAG_FALSE )
			self.setProperty( 'iPlayerXpeed', E_TAG_FALSE )
			self.setProperty( 'iPlayerResume', E_TAG_TRUE )

		elif aAction == Action.ACTION_MBOX_REWIND :
			self.setProperty( 'iPlayerResume', E_TAG_FALSE )
			#self.setProperty( 'iPlayerRewind', E_TAG_TRUE )
			self.setProperty( 'iPlayerXpeed', E_TAG_TRUE )
			self.setProperty( 'iFileXpeed', 'OSD2x.png' )
			self.setProperty( 'iXpeedArrow', 'Rewind' )

		elif aAction == Action.ACTION_MOVE_UP :
			iRussian = E_TAG_FALSE
			if XBMC_GetCurrentLanguage( ) == 'Russian' :
				iRussian = E_TAG_TRUE
			self.setProperty( 'iHotkeyGreenRussian', '%s'% iRussian )
			self.setProperty( 'InfoPlateName', E_TAG_FALSE )
			self.setProperty( E_XML_PROPERTY_HOTKEY_RED,    E_TAG_FALSE )
			self.setProperty( E_XML_PROPERTY_HOTKEY_GREEN,  E_TAG_FALSE )
			self.setProperty( E_XML_PROPERTY_HOTKEY_YELLOW, E_TAG_TRUE )
			self.setProperty( E_XML_PROPERTY_HOTKEY_BLUE,   E_TAG_TRUE )

		elif aAction == Action.ACTION_MOVE_DOWN :
			iRussian = E_TAG_FALSE
			if XBMC_GetCurrentLanguage( ) == 'Russian' :
				iRussian = E_TAG_TRUE
			self.setProperty( 'iHotkeyGreenRussian', '%s'% iRussian )
			self.setProperty( 'InfoPlateName', E_TAG_FALSE )
			self.setProperty( E_XML_PROPERTY_HOTKEY_RED,    E_TAG_FALSE )
			self.setProperty( E_XML_PROPERTY_HOTKEY_GREEN,  E_TAG_TRUE )
			self.setProperty( E_XML_PROPERTY_HOTKEY_YELLOW, E_TAG_TRUE )
			self.setProperty( E_XML_PROPERTY_HOTKEY_BLUE,   E_TAG_TRUE )
		"""
		#elif aAction == Action.ACTION_MOVE_LEFT :
		#	self.MoveTest( -10 )

		#elif aAction == Action.ACTION_MOVE_RIGHT :
		#	self.MoveTest( 10 )





	def onClick( self, aControlId ):
		pass


	def onFocus( self, aControlId ):
		pass


	def TestChannelList( self ) :
		self.getControl( E_DEFAULT_HEADER_TITLE ).setLabel( 'Channel List' )
		from pvr.GuiHelper import GetInstanceSkinPosition
		ctrlImgVideoPos = self.getControl( E_SETTING_PIP_SCREEN_IMAGE )

		h = ctrlImgVideoPos.getHeight( )
		w = ctrlImgVideoPos.getWidth( )
		x, y = list( ctrlImgVideoPos.getPosition( ) )
		
		x, y, w, h = pvr.GuiHelper.GetInstanceSkinPosition( ).GetPipPosition( x, y, w, h )

		self.mDataCache.Player_SetVIdeoSize( x, y + 1, w, h - 2 )

		self.setProperty( 'iCas', E_TAG_TRUE )
		self.setProperty( 'iCasV', 'V' )


	def TestLogo( self ) :
		chLogoB = E_TAG_FALSE
		chImage = ''
		iChannel = self.mDataCache.Channel_GetCurrent( )
		if iChannel :
			chLogoB = E_TAG_TRUE
			mChannelLogo = pvr.ChannelLogoMgr.GetInstance( )
			logo = '%s_%s'% ( iChannel.mCarrier.mDVBS.mSatelliteLongitude, iChannel.mSid )
			LOG_TRACE( 'logo=%s'% logo )
			LOG_TRACE( 'logo path=%s'% mChannelLogo.GetLogo( logo ) )
			chImage = mChannelLogo.GetLogo( logo, iChannel.mServiceType )

		self.setProperty( 'iChannelLogo', '%s'% chImage )
		self.setProperty( 'iChannelLogoBack', chLogoB )


	def TestScreen( self ) :
		self.getControl( 3050 ).reset( )
		for i in range( 1, 4 ) :
			imgFile = '%s.png'% i
			self.setProperty( 'RadioSCR', imgFile )
			time.sleep( 5 )

		self.setProperty( 'RadioSCR', '' )


	def TestList( self ) :
		mCtrlList = self.getControl( 3050 )
		mCtrlList.reset()
		mChannelList = self.mDataCache.Channel_GetList( )
		mListItems = []
		if self.mLimit :
			mChannelList = mChannelList[:12]

		color = ['brown', 'yellow', 'orange', 'blue', 'red', 'purple', 'green', 'pink', 'violet', 'silver', 'golden' ]
		idx = 0
		for iChannel in mChannelList :

			if idx >= len( color ) :
				idx = 0
			#listItem = xbmcgui.ListItem( '%04d %s'%( iChannel.mNumber, iChannel.mName ), '', 'IconHD.png', 'icon-rss.png' )
			itemLabel = '%04d %s [COLOR %s][B]%s[/B][/COLOR]'% ( iChannel.mNumber, iChannel.mName, color[idx], '[HD]' )
			idx += 1

			listItem = None
			if self.mLimit :
				listItem = xbmcgui.ListItem( '[COLOR white]%04d %s[/COLOR]'% ( iChannel.mNumber, iChannel.mName ) )
			else :
				listItem = xbmcgui.ListItem( itemLabel )

			if iChannel.mSkipped : listItem.setProperty( E_XML_PROPERTY_SKIP, E_TAG_TRUE )
			if iChannel.mLocked  : listItem.setProperty( E_XML_PROPERTY_LOCK, E_TAG_TRUE )
			if iChannel.mIsCA    : listItem.setProperty( E_XML_PROPERTY_CAS,  E_TAG_TRUE )
			if iChannel.mIsHD : 
				posx = '%s'% ( 130 + len( iChannel.mName ) )
				listItem.setProperty( 'iHDPosx', posx )
				listItem.setProperty( E_XML_PROPERTY_IHD,  E_TAG_TRUE )
				listItem.setIconImage( 'IconHD.png' )
				LOG_TRACE( '---------------- posx[%s] len[%s]'% ( posx, len( iChannel.mName ) ) )

			mTPnum = self.mDataCache.GetTunerIndexBySatellite( iChannel.mCarrier.mDVBS.mSatelliteLongitude, iChannel.mCarrier.mDVBS.mSatelliteBand )
			if mTPnum == E_CONFIGURED_TUNER_1 :
				listItem.setProperty( E_XML_PROPERTY_TUNER1, E_TAG_TRUE )
			elif mTPnum == E_CONFIGURED_TUNER_2 :
				listItem.setProperty( E_XML_PROPERTY_TUNER2, E_TAG_TRUE )
			elif mTPnum == E_CONFIGURED_TUNER_1_2 :
				listItem.setProperty( E_XML_PROPERTY_TUNER1_2, E_TAG_TRUE )

			mListItems.append( listItem )

		mCtrlList.addItems( mListItems )

'''
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
					mWin = self.mRootWindow
					#self.removeControl( self.mBookmarkButton[i] )
					mWin.removeControl( self.mBookmarkButton[i] )
				except Exception, e :
					LOG_TRACE( 'except[%s]'% e )
			self.mBookmarkButton = []
			LOG_TRACE('erased Init. bookmarkButton[%s]'% self.mBookmarkButton )

'''


