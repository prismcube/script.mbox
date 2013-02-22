from pvr.gui.WindowImport import *


TEXTBOX_ID_TITLE					= 100
TEXTBOX_ID_DESCRIPTION				= 101
LABEL_ID_DATE						= 102


class DialogExtendEPG( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )	
		self.mEPG = None
		self.mIsOk = None
		

	def onInit( self ) :
		LOG_TRACE( '' )
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.setProperty( 'EPGTitle', self.mEPG.mEventName )
		self.setProperty( 'EPGDescription', self.mEPG.mEventDescription )

		pmtEvent = self.mDataCache.GetCurrentPMTEvent( )
		UpdatePropertyByCacheData( self, pmtEvent, E_XML_PROPERTY_TELETEXT )

		setPropertyList = []
		setPropertyList = GetPropertyByEPGComponent( self.mEPG )
		LOG_TRACE('--------component[%s]'% setPropertyList )

		self.setProperty( E_XML_PROPERTY_SUBTITLE, setPropertyList[0] )
		self.setProperty( E_XML_PROPERTY_DOLBY,    setPropertyList[1] )
		self.setProperty( E_XML_PROPERTY_HD,       setPropertyList[2] )

		"""
		if self.mEPG.mHasSubtitles :
			self.setProperty( 'HasSubtitle', 'True' )
		else :
			self.setProperty( 'HasSubtitle', 'False' )

		if self.mEPG.mHasHDVideo :
			self.setProperty( 'HasHD', 'True' )
		else :
			self.setProperty( 'HasHD', 'False' )
		
		if self.mEPG.mHasDolbyDigital :
			self.setProperty( 'HasDolby', 'True' )
		else :
			self.setProperty( 'HasDolby', 'False' )
		"""
		
		self.mCtrlTitle = self.getControl( TEXTBOX_ID_TITLE )
		self.mCtrlDescription = self.getControl( TEXTBOX_ID_DESCRIPTION )
		self.mCtrlDate = self.getControl( LABEL_ID_DATE )

		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		sTime = TimeToString( self.mEPG.mStartTime + self.mLocalOffset, TimeFormatEnum.E_HH_MM )
		eTime = TimeToString( self.mEPG.mStartTime + self.mEPG.mDuration + self.mLocalOffset, TimeFormatEnum.E_HH_MM )
		self.setProperty( 'EPGTime', '%s - %s'% (sTime, eTime) )

		self.mEventBus.Register( self )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.mIsOk = actionId
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU :	
			#self.mEPG = None
			self.Close( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
			
		elif actionId == Action.ACTION_PARENT_DIR :
			self.Close( )
			
		elif actionId == Action.ACTION_CONTEXT_MENU :
			self.Close( )
			#xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )

		elif actionId == Action.ACTION_STOP :
			self.Close( )

		elif actionId == Action.ACTION_PLAYER_PLAY or actionId == Action.ACTION_PAUSE :
			self.Close( )


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


	def GetCloseStatus( self ) :
		return self.mIsOk


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.CloseDialog( )


