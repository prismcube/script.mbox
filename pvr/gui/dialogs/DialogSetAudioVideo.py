from pvr.gui.WindowImport import *


MAIN_GROUP_ID = 8000


class DialogSetAudioVideo( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		LOG_TRACE( 'args[0]=[%s]' % args[0] )
		LOG_TRACE( 'args[1]=[%s]' % args[1] )

		self.mIsOk = False
		self.mSelectIdx = 0
		self.mSelectName = ''
		self.mDialogTitle = ''
		self.mAudioTrack = []
		self.mMode = CONTEXT_ACTION_VIDEO_SETTING


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.InitProperty( )
		self.SetHeaderLabel( self.mDialogTitle )
		self.DrawItem( )
		self.mIsOk = False
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
			self.Close( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )
			
		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )

		elif actionId == Action.ACTION_STOP :
			self.Close( )

		elif actionId == Action.ACTION_PLAYER_PLAY or actionId == Action.ACTION_PAUSE :
			self.Close( )


	def onFocus( self, aControlId ) :
		pass


	def onClick( self, aControlId ) :
		if aControlId == E_SETTING_DIALOG_BUTTON_CLOSE :
			xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )
		else :
			self.ControlSelect( )
			hdmiFormat = ElisPropertyEnum( 'HDMI Format', self.mCommander ).GetPropString( )
			if hdmiFormat == 'Automatic' :
				return

			iconIndex = ElisEnum.E_ICON_1080i
			if hdmiFormat == '720p' :
				iconIndex = ElisEnum.E_ICON_720p
			elif hdmiFormat == '576p' :
				iconIndex = -1

			self.mDataCache.Frontdisplay_Resolution( iconIndex )


	def onClick( self, aControlId ) :
		if aControlId == E_SETTING_DIALOG_BUTTON_CLOSE :
			xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )
		else :
			self.ControlSelect( )


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


	def DrawItem( self ) :
		self.getControl( MAIN_GROUP_ID ).setVisible( False )
		self.ResetAllControl( )

		if self.mMode == CONTEXT_ACTION_VIDEO_SETTING :
			self.AddEnumControl( E_DialogSpinEx01, 'HDMI Format' )
			self.AddEnumControl( E_DialogSpinEx02, 'Show 4:3', MR_LANG( 'TV Screen Format' ) )
			self.AddEnumControl( E_DialogSpinEx03, 'HDMI Color Space' )
			self.AddEnumControl( E_DialogSpinEx04, 'TV System' )
			
			visibleControlIds = [ E_DialogSpinEx01, E_DialogSpinEx02, E_DialogSpinEx03, E_DialogSpinEx04 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

		elif self.mMode == CONTEXT_ACTION_AUDIO_SETTING :
			self.AddUserEnumControl( E_DialogSpinEx01, MR_LANG( 'Audio HDMI' ), self.mAudioTrack, 0 )

			visibleControlIds = [ E_DialogSpinEx01 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_DialogSpinEx02, E_DialogSpinEx03, E_DialogSpinEx04 ]
			self.SetVisibleControls( hideControlIds, False )

		self.SetAutoHeight( True )
		self.InitControl( )
		self.UpdateLocation( )
		self.getControl( MAIN_GROUP_ID ).setVisible( True )


	def GetCloseStatus( self ) :
		return self.mIsOk


	def GetValue( self, aFlag ) :
		return self.mSelectIdx, self.mSelectName, self.mIsOk


	def SetValue( self, aMode ) :
		self.mMode = aMode


	def SetProperty( self ) : 
		if self.mMode == CONTEXT_ACTION_VIDEO_SETTING :
			self.ControlSelect( )
			#if self.mSelectIdx == E_DialogSpinEx01 :
			#	self.mDataCache.Frontdisplay_Resolution( )

		elif self.mMode == CONTEXT_ACTION_AUDIO_SETTING :
			idx = self.GetSelectedIndex( E_DialogSpinEx01 )
			#LOG_TRACE('idx[%s] track[%s]'% ( idx, self.mAudioTrack) )
			self.mSelectName = self.mAudioTrack[idx]
			self.mDataCache.Audiotrack_select( idx )


	def InitProperty( self ) :
		if self.mMode == CONTEXT_ACTION_VIDEO_SETTING :
			self.mDialogTitle = MR_LANG( 'Video Format' )

		elif self.mMode == CONTEXT_ACTION_AUDIO_SETTING :
			self.mDialogTitle = MR_LANG( 'Audio Setting' )

			getCount = self.mDataCache.Audiotrack_GetCount( )
			selectIdx= self.mDataCache.Audiotrack_GetSelectedIndex( )
			#LOG_TRACE('AudioTrack count[%s] select[%s]'% (getCount, selectIdx) )

			self.mAudioTrack = []
			for i in range( getCount ) :
				iTrack = self.mDataCache.Audiotrack_Get( i )
				#LOG_TRACE('getTrack: name[%s] lang[%s]'% (iTrack.mName, iTrack.mLang) )
				if iTrack :
					label = '%s-%s'% (iTrack.mName, iTrack.mLang)
					self.mAudioTrack.append( label )


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.ResetAllControl( )
		self.CloseDialog( )

