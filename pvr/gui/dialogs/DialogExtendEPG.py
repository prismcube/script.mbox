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
		self.mWin = xbmcgui.WindowDialog( self.mWinId )

		self.mWin.setProperty( 'EPGTitle', self.mEPG.mEventName )
		self.mWin.setProperty( 'EPGDescription', self.mEPG.mEventDescription )

		if self.mEPG.mHasHDVideo :
			self.mWin.setProperty( 'HasHD', 'true' )
		else :
			self.mWin.setProperty( 'HasHD', 'false' )			
		
		if self.mEPG.mHasDolbyDigital :
			self.mWin.setProperty( 'HasDolby', 'true' )
		else :
			self.mWin.setProperty( 'HasDolby', 'false' )

		if self.mEPG.mHasSubtitles :
			self.mWin.setProperty( 'HasSubtitle', 'true' )
		else :
			self.mWin.setProperty( 'HasSubtitle', 'false' )

		
		self.mCtrlTitle = self.getControl( TEXTBOX_ID_TITLE )
		self.mCtrlDescription = self.getControl( TEXTBOX_ID_DESCRIPTION )
		self.mCtrlDate = self.getControl( LABEL_ID_DATE )

		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		sTime = TimeToString( self.mEPG.mStartTime + self.mLocalOffset, TimeFormatEnum.E_HH_MM )
		eTime = TimeToString( self.mEPG.mStartTime + self.mEPG.mDuration + self.mLocalOffset, TimeFormatEnum.E_HH_MM )
		self.mWin.setProperty( 'EPGTime', '%s - %s'% (sTime, eTime) )

		self.mEventBus.Register( self )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.mIsOk = actionId
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.Close( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
			
		elif actionId == Action.ACTION_PARENT_DIR :
			self.Close( )
			
		elif actionId == Action.ACTION_CONTEXT_MENU :
			self.Close( )


	def onClick( self, aControlId ) :
		pass


	def onFocus( self, aControlId ) :
		pass


	@GuiLock
	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowDialogId( ) :

			if aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
				LOG_TRACE( 'ElisEventPlaybackEOF mType[%d]'% ( aEvent.mType ) )

				if aEvent.mType == ElisEnum.E_EOF_START :
					self.mIsOk = Action.ACTION_PLAYER_PLAY
					#xbmc.executebuiltin('xbmc.Action(play)')
					self.Close( )
					LOG_TRACE( 'EventRecv EOF_START' )

				elif aEvent.mType == ElisEnum.E_EOF_END :
					LOG_TRACE( 'EventRecv EOF_END' )
					#xbmc.executebuiltin('xbmc.Action(stop)')
					self.mIsOk = Action.ACTION_STOP
					self.Close( )


	def SetEPG( self, aEPG ) :
		self.mEPG = aEPG


	def GetCloseStatus( self ) :
		return self.mIsOk


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.CloseDialog( )
		
