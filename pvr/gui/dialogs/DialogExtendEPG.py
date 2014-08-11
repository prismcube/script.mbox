from pvr.gui.WindowImport import *


#TEXTBOX_ID_TITLE					= 100
#TEXTBOX_ID_DESCRIPTION				= 101
#LABEL_ID_DATE						= 102
SCROLL_ID_SHOW						= 110
GROUP_ID_BASE						= 300
BUTTON_ID_PREV						= 301
BUTTON_ID_NEXT						= 302

EPGLIST_EXCEPTWINDOW = [ WinMgr.WIN_ID_NULLWINDOW, WinMgr.WIN_ID_EPG_WINDOW, WinMgr.WIN_ID_EPG_SEARCH ]

class DialogExtendEPG( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )	
		self.mEPG = None
		self.mIsOk = None
		self.mEPGList = []
		self.mEPGListIdx = 0


	def onInit( self ) :
		LOG_TRACE( '' )
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		isShowList = True

		try :
			descriptGroup = self.getControl( GROUP_ID_BASE )
			basePos = descriptGroup.getPosition( )
			lastWin = WinMgr.GetInstance( ).GetLastWindowID( )
			if lastWin in EPGLIST_EXCEPTWINDOW :
				descriptGroup.setPosition( basePos[0], basePos[1] + 55 )
				isShowList = False

			elif lastWin == WinMgr.WIN_ID_INFO_PLATE :
				isShowList = False

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )


		button1 = E_TAG_FALSE
		button2 = E_TAG_FALSE
		if self.mEPGList and len( self.mEPGList ) > 0 :
			button2 = E_TAG_TRUE
			if self.mEPGListIdx > 0 :
				button1 = E_TAG_TRUE
			self.EPGListMoveToCurrent( )
			self.EPGListMoveToIndex( )

		else :
			if isShowList :
				self.GetEPGListByChannel( )

		self.setProperty( 'EPGPrev', button1 )
		self.setProperty( 'EPGNext', button2 )

		if button2 == E_TAG_TRUE :
			self.UpdateSetFocus( BUTTON_ID_NEXT )

		self.ShowExtendedInfo( )
		self.mEventBus.Register( self )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.mIsOk = actionId
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU :	
			self.Close( )
			
		elif actionId == Action.ACTION_PARENT_DIR :
			self.Close( )
			
		elif actionId == Action.ACTION_CONTEXT_MENU :
			self.Close( )

		elif actionId == Action.ACTION_STOP :
			self.Close( )

		elif actionId == Action.ACTION_PLAYER_PLAY or actionId == Action.ACTION_PAUSE :
			self.Close( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			self.GetFocusId( )
			if self.mFocusId == BUTTON_ID_PREV or self.mFocusId == BUTTON_ID_NEXT :
				self.EPGNavigation( self.mFocusId )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.GetFocusId( )
			if self.mFocusId == BUTTON_ID_PREV or self.mFocusId == BUTTON_ID_NEXT :
				self.EPGNavigation( BUTTON_ID_PREV )
			else :
				self.setFocusId( BUTTON_ID_PREV )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.GetFocusId( )
			if self.mFocusId == BUTTON_ID_PREV or self.mFocusId == BUTTON_ID_NEXT :
				self.EPGNavigation( BUTTON_ID_NEXT )
			else :
				self.setFocusId( BUTTON_ID_NEXT )

		elif actionId == Action.ACTION_MOVE_UP :
			self.setFocusId( SCROLL_ID_SHOW )

		elif actionId == Action.ACTION_MOVE_DOWN :
			self.setFocusId( SCROLL_ID_SHOW )


	def onClick( self, aControlId ) :
		pass


	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowDialogId( ) :

			if aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
				LOG_TRACE( 'ExtendDialog ElisEventPlaybackEOF mType[%d]'% ( aEvent.mType ) )

				if aEvent.mType == ElisEnum.E_EOF_START :
					self.mIsOk = Action.ACTION_PLAYER_PLAY
					xbmc.executebuiltin('xbmc.Action(play)')

				elif aEvent.mType == ElisEnum.E_EOF_END :
					LOG_TRACE( 'EventRecv EOF_END' )
					xbmc.executebuiltin('xbmc.Action(stop)')


	def SetEPG( self, aEPG ) :
		self.mEPG = aEPG


	def SetEPGList( self, aEPGList = [], aIdx = 0 ) :
		self.mEPGList = aEPGList
		self.mEPGListIdx = aIdx


	@RunThread
	def GetEPGListByChannel( self ) :
		channel = self.mDataCache.Channel_GetCurrent( )
		if channel :
			self.mEPGList = []
			self.mEPGListIdx = -1

			#self.mEPGList = self.mDataCache.Epgevent_GetListByChannelFromEpgCF(  channel.mSid,  channel.mTsid,  channel.mOnid )
			gmtFrom  = self.mDataCache.Datetime_GetGMTTime( )
			gmtUntil = gmtFrom + E_MAX_EPG_DAYS
			maxCount = 1000
			self.mEPGList = self.mDataCache.Epgevent_GetListByChannel( channel.mSid, channel.mTsid, channel.mOnid, gmtFrom, gmtUntil, maxCount )
			#LOG_TRACE('mSid[%s] mTsid[%s] mOnid[%s] gmtFrom[%s] gmtUntil[%s]'% ( channel.mSid, channel.mTsid, channel.mOnid, gmtFrom, gmtUntil ) )

			button1 = E_TAG_FALSE
			button2 = E_TAG_FALSE
			if self.mEPGList and len( self.mEPGList ) > 0 :
				button2 = E_TAG_TRUE
				self.mEPGListIdx = 0
				self.EPGListMoveToCurrent( )
				#LOG_TRACE( 'EPGList load[%s] idx[%s]'% ( len( self.mEPGList ), self.mEPGListIdx ) )

			else :
				LOG_TRACE( 'EPGList is None' )

			self.EPGListMoveToIndex( )
			self.setProperty( 'EPGPrev', button1 )
			self.setProperty( 'EPGNext', button2 )
			if button2 == E_TAG_TRUE :
				self.UpdateSetFocus( BUTTON_ID_NEXT )


	def EPGListMoveToCurrent( self ) :
		if self.mEPG and self.mEPG.mError == 0 :
			#LOG_TRACE('new EPG received, not exist in EPGList')
			idx = 0
			for idx in range( len( self.mEPGList ) ) :
				if self.mEPG.mStartTime <= self.mEPGList[idx].mStartTime :
					break

			self.mEPGListIdx = idx
			#self.mEPGList = self.mEPGList[:idx]+[self.mEPG]+self.mEPGList[idx:]


	def EPGListMoveToIndex( self ) :
		try :
			if not self.mEPGList or len( self.mEPGList ) < 1 :
				return

			iEPG = self.mEPGList[self.mEPGListIdx]
			if iEPG :
				self.ResetLabel( )
				SetLock2(True)
				self.mEPG = iEPG
				SetLock2(False)

				self.setProperty( 'EPGIndex', '%s/%s'% ( self.mEPGListIdx + 1, len( self.mEPGList ) ) )
				self.ShowExtendedInfo( )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def EPGNavigation( self, aDir ):
		if self.mEPGList :
			lastIdx = len( self.mEPGList ) - 1
			if aDir == BUTTON_ID_NEXT :
				if self.mEPGListIdx + 1 > lastIdx :
					self.mEPGListIdx = lastIdx
				else :
					self.mEPGListIdx += 1

			elif aDir == BUTTON_ID_PREV:
				if self.mEPGListIdx - 1 < 0 :
					self.mEPGListIdx = 0
				else :
					self.mEPGListIdx -= 1

			button1 = E_TAG_FALSE
			if self.mEPGListIdx > 0 :
				button1 = E_TAG_TRUE

			self.setProperty( 'EPGPrev', button1 )
			self.EPGListMoveToIndex( )


	def GetCloseStatus( self ) :
		return self.mIsOk


	def ShowExtendedInfo( self ) :
		if not self.mEPG or self.mEPG.mError != 0 :
			#LOG_TRACE('epg None' )
			return

		desc = MR_LANG( 'No description' )
		if self.mEPG.mEventDescription and self.mEPG.mEventDescription != '(null)' :
			desc = self.mEPG.mEventDescription
		self.setProperty( 'EPGTitle', self.mEPG.mEventName )
		self.setProperty( 'EPGDescription', desc )

		pmtEvent = self.mDataCache.GetCurrentPMTEvent( self.mEPG )
		pmtinstance = self.mDataCache.GetCurrentPMTEventByPVR( )
		if pmtinstance :
			pmtEvent = pmtinstance

		UpdatePropertyByCacheData( self, pmtEvent, E_XML_PROPERTY_TELETEXT )
		isSubtitle = UpdatePropertyByCacheData( self, pmtEvent, E_XML_PROPERTY_SUBTITLE )
		if not isSubtitle :
			self.setProperty( E_XML_PROPERTY_SUBTITLE, HasEPGComponent( self.mEPG, ElisEnum.E_HasSubtitles ) )
		if not UpdatePropertyByCacheData( self, pmtEvent, E_XML_PROPERTY_DOLBYPLUS ) :
			self.setProperty( E_XML_PROPERTY_DOLBY,HasEPGComponent( self.mEPG, ElisEnum.E_HasDolbyDigital ) )
		self.setProperty( E_XML_PROPERTY_HD,       HasEPGComponent( self.mEPG, ElisEnum.E_HasHDVideo ) )

		#age info
		UpdatePropertyByAgeRating( self, self.mEPG )

		#self.mCtrlTitle = self.getControl( TEXTBOX_ID_TITLE )
		#self.mCtrlDescription = self.getControl( TEXTBOX_ID_DESCRIPTION )
		#self.mCtrlDate = self.getControl( LABEL_ID_DATE )

		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		sTime = TimeToString( self.mEPG.mStartTime + self.mLocalOffset, TimeFormatEnum.E_HH_MM )
		eTime = TimeToString( self.mEPG.mStartTime + self.mEPG.mDuration + self.mLocalOffset, TimeFormatEnum.E_HH_MM )
		eDate = TimeToString( self.mEPG.mStartTime + self.mLocalOffset, TimeFormatEnum.E_AW_DD_MM_YYYY )
		self.setProperty( 'EPGTime', '%s - %s'% ( sTime, eTime ) )
		self.setProperty( 'EPGDate', '%s'% ( eDate ) )
		self.setProperty( 'EPGDuration', '%sm'% ( self.mEPG.mDuration / 60 ) )


	def ResetLabel( self ) :
		self.setProperty( 'EPGTime', '' )
		self.setProperty( 'EPGDate', '' )
		self.setProperty( 'EPGDuration', '' )
		self.setProperty( 'EPGIndex', '' )
		self.setProperty( 'EPGTitle', '' )
		self.setProperty( 'EPGDescription', '' )
		self.setProperty( 'EPGAgeRating', '' )
		self.setProperty( 'HasAgeRating', 'None' )
		self.setProperty( E_XML_PROPERTY_TELETEXT, E_TAG_FALSE )
		self.setProperty( E_XML_PROPERTY_SUBTITLE, E_TAG_FALSE )
		self.setProperty( E_XML_PROPERTY_DOLBYPLUS, E_TAG_FALSE )
		self.setProperty( E_XML_PROPERTY_DOLBY, E_TAG_FALSE )


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.CloseDialog( )


