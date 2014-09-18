from pvr.gui.WindowImport import *


MAIN_GROUP_ID = 8000
E_SET_INTERVAL = 3


class DialogSetAudioVideo( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		LOG_TRACE( 'args[0]=[%s]' % args[0] )
		LOG_TRACE( 'args[1]=[%s]' % args[1] )

		self.mIsOk					= False
		self.mSelectIdx				= 0
		self.mSelectName			= ''
		self.mAudioTrack			= []
		self.mMode					= CONTEXT_ACTION_VIDEO_SETTING

		self.mVideoOutput			= self.mDataCache.GetVideoOutput( )
		self.mAnalogAscpect			= E_16_9
		self.mAsyncVideoSetThread 	= None
		self.mBusyVideoSetting		= False
		self.mAsyncBlinkThread		= None


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.setProperty( 'DialogDrawFinished', 'False' )
		self.mAnalogAscpect = ElisPropertyEnum( 'TV Aspect', self.mCommander ).GetProp( )

		lblTitle = '%s & %s'% ( MR_LANG( 'Audio' ), MR_LANG( 'Video' ) )
		self.SetHeaderLabel( lblTitle )
		self.DrawItem( )
		self.mIsOk = False
		self.mEventBus.Register( self )

		self.setProperty( 'DialogDrawFinished', 'True' )
		self.mInitialized = True


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

		elif actionId == Action.ACTION_COLOR_YELLOW :
			self.Close( )


	def onFocus( self, aControlId ) :
		pass


	def onClick( self, aControlId ) :
		if aControlId == E_SETTING_DIALOG_BUTTON_CLOSE :
			self.Close( )

		if self.mMode == CONTEXT_ACTION_VIDEO_SETTING :
			groupId = self.GetGroupId( aControlId )
			if groupId == E_DialogSpinEx01 :
				self.mVideoOutput = self.GetSelectedIndex( E_DialogSpinEx01 )
				self.mDataCache.SetVideoOutput( self.mVideoOutput )
				time.sleep( 0.02 )
				self.DrawItem( )
				return

			elif self.mVideoOutput == E_VIDEO_ANALOG and groupId == E_DialogSpinEx02 :
				self.ControlSelect( )
				self.mAnalogAscpect = self.GetSelectedIndex( E_DialogSpinEx02 )
				time.sleep( 0.02 )
				self.DrawItem( )

			elif self.mVideoOutput == E_VIDEO_HDMI and groupId == E_DialogInput02 :
				self.ShowHDMIFormat( )

			elif groupId == E_DialogInput01 :
				self.ShowAudioTrack( )

			else :
				self.ControlSelect( )

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
		self.ResetAllControl( )
		defaultFocus = E_DialogInput01
		if self.mInitialized :
			defaultFocus = E_DialogSpinEx01

		if self.mMode == CONTEXT_ACTION_VIDEO_SETTING :
			trackList, selectIdx = self.GetAudioTrack( )
			lblSelect = MR_LANG( 'None' )
			if selectIdx != -1 and selectIdx < len( trackList ) :
				lblSelect = trackList[selectIdx].mDescription

			self.AddInputControl( E_DialogInput01, MR_LANG( 'Audio Track' ), lblSelect )
			if len( trackList ) < 1 :
				self.SetEnableControl( E_DialogInput01, False )
				defaultFocus = E_DialogSpinEx01

			self.AddUserEnumControl( E_DialogSpinEx01, MR_LANG( 'Video Output' ), USER_ENUM_LIST_VIDEO_OUTPUT, self.mVideoOutput, MR_LANG( 'Select HDMI or Analog for your video output' ) )
			if self.mVideoOutput == E_VIDEO_HDMI :
				lblSelect = ElisPropertyEnum( 'HDMI Format', self.mCommander ).GetPropString( )
				self.AddInputControl( E_DialogInput02, MR_LANG( 'HDMI Format' ), lblSelect )
				self.AddEnumControl( E_DialogSpinEx03, 'Show 4:3', MR_LANG( ' - TV Screen Format' ) )
				self.AddEnumControl( E_DialogSpinEx04, 'HDMI Color Space', MR_LANG( ' - HDMI Color Space' ) )

				visibleControlIds = [ E_DialogSpinEx01, E_DialogInput02, E_DialogSpinEx03, E_DialogSpinEx04 ]
				self.SetVisibleControl( E_DialogSpinEx02, False )
				self.SetVisibleControls( visibleControlIds, True )
				self.SetEnableControls( visibleControlIds, True )

			else :
				self.AddEnumControl( E_DialogSpinEx02, 'TV Aspect', MR_LANG( ' - TV Aspect Ratio' ) )
				if self.mAnalogAscpect == E_16_9 :
					self.AddEnumControl( E_DialogSpinEx03, 'Picture 16:9', MR_LANG( ' - Picture Format' ) )
				else :
					self.AddEnumControl( E_DialogSpinEx03, 'Picture 4:3', MR_LANG( ' - Picture Format' ) )

				visibleControlIds = [ E_DialogSpinEx01, E_DialogSpinEx02, E_DialogSpinEx03 ]
				self.SetVisibleControls( visibleControlIds, True )
				self.SetEnableControls( visibleControlIds, True )

				hideControlIds = [ E_DialogSpinEx04, E_DialogInput02 ]
				self.SetVisibleControls( hideControlIds, False )

		#deprecated
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
		self.SetFocus( defaultFocus )


	def ShowHDMIFormat( self ) :
		hdmiList = []
		selectIdx = ElisPropertyEnum( 'HDMI Format', self.mCommander ).GetPropIndex( )
		propCount = ElisPropertyEnum( 'HDMI Format', self.mCommander ).GetIndexCount( )
		for i in range( propCount ) :
			propName = ElisPropertyEnum( 'HDMI Format', self.mCommander ).GetPropStringByIndex( i )
			hdmiList.append( ContextItem( propName, i ) )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( hdmiList, selectIdx )
		dialog.doModal( )

		selectAction = dialog.GetSelectedAction( )
		#LOG_TRACE( '------HDMI[%s]'% selectAction )

		if selectAction > -1 :
			ElisPropertyEnum( 'HDMI Format', self.mCommander ).SetPropIndex( selectAction )
			self.SetControlLabel2String( E_DialogInput02, hdmiList[selectAction].mDescription )
			DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).PIP_SetPositionSync( True )

			time.sleep(1)
			self.VideoRestore( selectIdx, hdmiList[selectIdx].mDescription )


	def VideoRestore( self, aRestoreIdx, aRestoreValue ) :
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_VIDEO_RESTORE )
		dialog.doModal( )

		if dialog.IsOK( ) != E_DIALOG_STATE_YES :
			ElisPropertyEnum( 'HDMI Format', self.mCommander ).SetPropIndex( aRestoreIdx )
			self.SetControlLabel2String( E_DialogInput02, aRestoreValue )
			DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP ).PIP_SetPositionSync( True )

		self.mDataCache.Frontdisplay_ResolutionByIdentified( )


	def GetAudioTrack( self ) :
		getCount = self.mDataCache.Audiotrack_GetCount( )
		selectIdx= self.mDataCache.Audiotrack_GetSelectedIndex( )

		trackList = []
		trackIndex = 0
		for idx in range(getCount) :
			idxTrack = None
			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_PVR :
				mPlayingRecord = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW ).GetPlayingRecord( )
				if mPlayingRecord :
					idxTrack = self.mDataCache.Audiotrack_GetForRecord( mPlayingRecord.mRecordKey, idx )

			else :
				idxTrack = self.mDataCache.Audiotrack_Get( idx )

			if idxTrack == None :
				#dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
				#dialog.SetProperty( trackList )
				#dialog.doModal( )
				selectIdx = -1
				break

			#idxTrack = self.mDataCache.Audiotrack_Get( idx )
			LOG_TRACE('getTrack name[%s] lang[%s]'% ( idxTrack.mName, idxTrack.mLang ) )
			label = '%s-%s'% ( idxTrack.mName, idxTrack.mLang )
			if idxTrack.mName == '' :
				label = 'Stereo-%s' % idxTrack.mLang
			elif idxTrack.mLang == '' :
				label = '%s' % idxTrack.mName
			elif idxTrack.mName == '' and idxTrack.mLang == '' :
				label = MR_LANG( 'Unknown' )

			trackList.append( ContextItem( label, trackIndex ) )
			trackIndex += 1

		return trackList, selectIdx


	def ShowAudioTrack( self ) :
		trackList, selectIdx = self.GetAudioTrack( )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( trackList, selectIdx )
		dialog.doModal( )

		selectAction = dialog.GetSelectedAction( )
		if selectAction < 0 :
			return

		if self.mCommander.Player_GetMute( ) :
			self.mCommander.Player_SetMute( False )
			xbmc.executebuiltin( 'Mute( )' )

		self.mDataCache.Audiotrack_select( selectAction )
		#LOG_TRACE('Select[%s --> %s]'% (aSelectAction, selectAction) )

		if selectAction < len( trackList ) :
			self.SetControlLabel2String( E_DialogInput01, trackList[selectAction].mDescription )


	def GetCloseStatus( self ) :
		return self.mIsOk


	def GetValue( self, aFlag ) :
		return self.mSelectIdx, self.mSelectName, self.mIsOk


	def SetValue( self, aMode ) :
		return
		self.mMode = aMode


	def SetProperty( self ) : 
		return
		self.ControlSelect( )


	def Close( self ) :
		if self.mAsyncVideoSetThread :
			self.mAsyncVideoSetThread.cancel( )
		if self.mAsyncBlinkThread :
			self.mAsyncBlinkThread.cancel( )

		self.mEventBus.Deregister( self )
		self.ResetAllControl( )
		self.CloseDialog( )

