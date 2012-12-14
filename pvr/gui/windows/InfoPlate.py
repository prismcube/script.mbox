from pvr.gui.WindowImport import *

E_CONTROL_ID_IMAGE_RECORDING1 			= 10
E_CONTROL_ID_LABEL_RECORDING1 			= 11
E_CONTROL_ID_IMAGE_RECORDING2 			= 15
E_CONTROL_ID_LABEL_RECORDING2 			= 16
E_CONTROL_ID_BUTTON_PREV_EPG 			= 702
E_CONTROL_ID_BUTTON_NEXT_EPG 			= 706
E_CONTROL_ID_LABEL_CHANNEL_NUMBER		= 601
E_CONTROL_ID_LABEL_CHANNEL_NAME			= 602
E_CONTROL_ID_IMAGE_SERVICETYPE_TV		= 603
E_CONTROL_ID_IMAGE_SERVICETYPE_RADIO	= 604
E_CONTROL_ID_GROUP_COMPONENT_DATA		= 605
E_CONTROL_ID_GROUP_COMPONENT_DOLBY 		= 606
E_CONTROL_ID_GROUP_COMPONENT_HD			= 607
E_CONTROL_ID_IMAGE_LOCKED 				= 651
E_CONTROL_ID_IMAGE_ICAS 				= 652
E_CONTROL_ID_LABEL_LONGITUDE_INFO		= 701
E_CONTROL_ID_LABEL_EPG_NAME				= 703
E_CONTROL_ID_LABEL_EPG_STARTTIME		= 704
E_CONTROL_ID_LABEL_EPG_ENDTIME			= 705
E_CONTROL_ID_PROGRESS_EPG 				= 707

E_CONTROL_DEFAULT_HIDE = [ 
	E_CONTROL_ID_BUTTON_START_RECORDING,
	E_CONTROL_ID_BUTTON_STOP_RECORDING
]

FLAG_MASK_ADD  = 0x01
FLAG_MASK_NONE = 0x00
FLAG_CLOCKMODE_ADMYHM  = 1
FLAG_CLOCKMODE_AHM     = 2
FLAG_CLOCKMODE_HMS     = 3
FLAG_CLOCKMODE_HHMM    = 4
FLAG_CLOCKMODE_INTTIME = 5

#NEXT_EPG		= 0
#PREV_EPG 		= 1

#CURR_CHANNEL	= 0
#NEXT_CHANNEL	= 1
#PREV_CHANNEL	= 2
#INIT_CHANNEL	= 3


class InfoPlate( LivePlateWindow ) :
	def __init__( self, *args, **kwargs ) :
		LivePlateWindow.__init__( self, *args, **kwargs )

		self.mAutomaticHideTimer = None	
		self.mAutomaticHide = False
		self.mEnableLocalThread = False


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		LOG_TRACE( 'winID[%d]'% self.mWinId)

		self.mCtrlLblRec1              = self.getControl( E_CONTROL_ID_LABEL_RECORDING1 )
		self.mCtrlLblRec2              = self.getControl( E_CONTROL_ID_LABEL_RECORDING2 )

		#channel, epg info
		self.mCtrlLblChannelNumber     = self.getControl( E_CONTROL_ID_LABEL_CHANNEL_NUMBER )
		self.mCtrlLblChannelName       = self.getControl( E_CONTROL_ID_LABEL_CHANNEL_NAME )
		self.mCtrlLblLongitudeInfo     = self.getControl( E_CONTROL_ID_LABEL_LONGITUDE_INFO )
		self.mCtrlLblEventName         = self.getControl( E_CONTROL_ID_LABEL_EPG_NAME )
		self.mCtrlLblEventStartTime    = self.getControl( E_CONTROL_ID_LABEL_EPG_STARTTIME )
		self.mCtrlLblEventEndTime      = self.getControl( E_CONTROL_ID_LABEL_EPG_ENDTIME )
		self.mCtrlProgress             = self.getControl( E_CONTROL_ID_PROGRESS_EPG )

		#button icon
		self.mCtrlBtnPrevEpg           = self.getControl( E_CONTROL_ID_BUTTON_PREV_EPG )
		self.mCtrlBtnNextEpg           = self.getControl( E_CONTROL_ID_BUTTON_NEXT_EPG )

		self.SetRadioScreen( )
		self.InitControl( )
		self.SetVisibleControls( E_CONTROL_DEFAULT_HIDE, False )

		self.mPlayingRecord = None
		self.mCurrentEPG = None
		self.mAutomaticHideTimer = None

		#get channel
		self.LoadInit( )

		#run thread
		self.mEventBus.Register( self )
		self.mEnableLocalThread = True
		self.EPGProgressThread( )

		if self.mAutomaticHide == True :
			self.StartAutomaticHide( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 :
			self.MoveToSeekFrame( int( actionId ) - Action.REMOTE_0 )

		elif actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :
			rKey = actionId - (Action.ACTION_JUMP_SMS2 - 2)
			self.MoveToSeekFrame( rKey )

		elif actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.Close( )
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			self.StopAutomaticHide( )
			self.SetAutomaticHide( False )

		elif actionId == Action.ACTION_CONTEXT_MENU :
			self.StopAutomaticHide( )
			self.SetAutomaticHide( False )
			self.onClick( E_CONTROL_ID_BUTTON_DESCRIPTION_INFO )

		elif actionId == Action.ACTION_MOVE_LEFT :
			pass

		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass

		elif actionId == Action.ACTION_STOP :
			ret = self.mDataCache.Player_Stop( )
			if ret :
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_MBOX_ARCHIVE :
			self.Close( )
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_SHOW_INFO :
			self.Close( )
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_PAUSE or actionId == Action.ACTION_PLAYER_PLAY :
			from pvr.GuiHelper import HasAvailableRecordingHDD
			if HasAvailableRecordingHDD( ) == False :
				return
				
			self.Close( )
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = actionId
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_MBOX_REWIND :
			from pvr.GuiHelper import HasAvailableRecordingHDD
			if HasAvailableRecordingHDD( ) == False :
				return
				
			self.Close( )
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = actionId
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_MBOX_FF :
			from pvr.GuiHelper import HasAvailableRecordingHDD
			if HasAvailableRecordingHDD( ) == False :
				return
				
			self.Close( )			
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = actionId
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_MBOX_TVRADIO :
			pass
			#ToDo warning msg

		#test
		elif actionId == 13: #'x'
			LOG_TRACE( 'cwd[%s]'% xbmc.getLanguage( ) )


	def onClick( self, aControlId ) :
		if aControlId == E_CONTROL_ID_BUTTON_MUTE :
			self.GlobalAction( Action.ACTION_MUTE )

		elif aControlId >= E_CONTROL_ID_BUTTON_DESCRIPTION_INFO and aControlId <= E_CONTROL_ID_BUTTON_BOOKMARK :
			self.ShowDialog( aControlId )


	def onFocus( self, aControlId ) :
		pass


	def LoadInit( self ):
		self.ShowRecordingInfo( )
		self.mPlayingRecord = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW ).GetPlayingRecord( )
		if self.mPlayingRecord :
			self.mCurrentEPG = self.mDataCache.RecordItem_GetEventInfo( self.mPlayingRecord.mRecordKey )
			if self.mCurrentEPG == None or self.mCurrentEPG.mError != 0 :
				self.mCurrentEPG = ElisIEPGEvent()
				self.mCurrentEPG.mEventName = self.mPlayingRecord.mRecordName
				self.mCurrentEPG.mEventDescription = ''
				self.mCurrentEPG.mStartTime = self.mPlayingRecord.mStartTime - self.mDataCache.Datetime_GetLocalOffset( )
				self.mCurrentEPG.mDuration = self.mPlayingRecord.mDuration

		self.InitControlGUI( )
		self.UpdateChannelAndEPG( )


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :

			if aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
				LOG_TRACE( 'ElisEventPlaybackEOF mType[%d]'% ( aEvent.mType ) )

				if aEvent.mType == ElisEnum.E_EOF_START :
					#ret = self.mDataCache.Player_Resume( )
					xbmc.executebuiltin('xbmc.Action(play)')
					LOG_TRACE( 'EventRecv EOF_START' )

				elif aEvent.mType == ElisEnum.E_EOF_END :
					LOG_TRACE( 'EventRecv EOF_END' )
					xbmc.executebuiltin('xbmc.Action(stop)')

			elif aEvent.getName( ) == ElisEventTuningStatus.getName( ) :
				LOG_TRACE('TunerNo[%s] locked[%s] quality[%s] strength[%s] frequency[%s]'% ( \
						aEvent.mTunerNo, aEvent.mIsLocked, aEvent.mSignalQuality, aEvent.mSignalStrength, aEvent.mFrequency ) )
				#ToDo
				#xbmcgui.Dialog( ).ok( MR_LANG('Infomation'), MR_LANG('No Signal') )

			elif aEvent.getName( ) == ElisEventChannelChangeResult.getName( ) :
				pass

			elif aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or \
				 aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
 				self.ShowRecordingInfo( )

		else:
			LOG_TRACE( 'LivePlate winID[%d] this winID[%d]'% ( self.mWinId, xbmcgui.getCurrentWindowId( ) ) )


	def UpdateChannelAndEPG( self, aEpg = None ):
		rec = self.mPlayingRecord
		if rec :
			try :
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NUMBER, '[COLOR red]PVR[/COLOR]' )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, rec.mChannelName )

				#satellite
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_LONGITUDE_INFO, 'Archive' )

				#lock,cas
				if rec.mLocked :
					self.UpdatePropertyGUI( E_XML_PROPERTY_LOCK, 'True' )

				#if ch.mIsCA :
				#	self.UpdatePropertyGUI( E_XML_PROPERTY_CAS, 'True' )


				#record name
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_NAME, deepcopy( rec.mRecordName ) )

				#start,end
				label = TimeToString( rec.mStartTime, TimeFormatEnum.E_HH_MM )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_STARTTIME, label )
				label = TimeToString( rec.mStartTime + rec.mDuration, TimeFormatEnum.E_HH_MM )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_ENDTIME,   label )

			except Exception, e:
				LOG_TRACE( 'Error exception[%s]'% e )


	@RunThread
	def EPGProgressThread( self ):
		while self.mEnableLocalThread :
			#LOG_TRACE( 'repeat <<<<' )
			self.UpdateProgress( )
			time.sleep(1)


	def UpdateProgress( self ) :
		try :
			status = self.mDataCache.Player_GetStatus( )
			#retList = []
			#retList.append( status )
			#LOG_TRACE( 'player_GetStatus[%s]'% ClassToList( 'convert', retList ) )

			if status and status.mError == 0 :
				totTime = ( status.mEndTimeInMs - status.mStartTimeInMs ) / 1000
				curTime = ( status.mPlayTimeInMs - status.mStartTimeInMs ) / 1000

				if totTime > 0 and curTime >= 0 :
					percent = ( curTime / float( totTime ) ) * 100.0

					#LOG_TRACE( 'curTime[%s] totTime[%s]'% ( curTime,totTime ) )
					#LOG_TRACE( 'curTime[%s] idx[%s] endTime[%s]'% ( curTime, percent, status.mEndTimeInMs ) )

					if percent > 100 :
						percent = 100
					elif percent < 0 :
						percent = 0

					self.mCtrlProgress.setPercent( percent )
					#LOG_TRACE('progress percent[%s]'% percent)

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def InitControlGUI( self ) :
		self.UpdateControlGUI( E_CONTROL_ID_PROGRESS_EPG,          0 )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_LONGITUDE_INFO, '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_NAME,       '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_STARTTIME,  '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_ENDTIME,    '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_LONGITUDE_INFO, '' )
		self.mCtrlBtnPrevEpg.setVisible( False )
		self.mCtrlBtnNextEpg.setVisible( False )

		tvValue = 'True'
		raValue = 'False'
		if self.mPlayingRecord :
			if self.mPlayingRecord.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
				tvValue = 'False'
				raValue = 'True'
		else :
			tvValue = 'False'
			raValue = 'False'

		self.UpdatePropertyGUI( E_XML_PROPERTY_TV,      tvValue )
		self.UpdatePropertyGUI( E_XML_PROPERTY_RADIO,   raValue )
		self.UpdatePropertyGUI( E_XML_PROPERTY_LOCK,    'False' )
		self.UpdatePropertyGUI( E_XML_PROPERTY_CAS,     'False' )
		self.UpdatePropertyGUI( E_XML_PROPERTY_FAV,     'False' )
		self.UpdatePropertyGUI( E_XML_PROPERTY_SUBTITLE,'False' )
		self.UpdatePropertyGUI( E_XML_PROPERTY_DOLBY,   'False' )
		self.UpdatePropertyGUI( E_XML_PROPERTY_HD,      'False' )


	def UpdateControlGUI( self, aCtrlID = None, aValue = None, aExtra = None ) :
		#LOG_TRACE( 'Enter control[%s] value[%s]'% (aCtrlID, aValue) )
		if aCtrlID == E_CONTROL_ID_LABEL_CHANNEL_NUMBER :
			self.mCtrlLblChannelNumber.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_CHANNEL_NAME :
			self.mCtrlLblChannelName.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_LONGITUDE_INFO :
			self.mCtrlLblLongitudeInfo.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_EPG_NAME :
			self.mCtrlLblEventName.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_EPG_STARTTIME :
			self.mCtrlLblEventStartTime.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_EPG_ENDTIME :
			self.mCtrlLblEventEndTime.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_PROGRESS_EPG :
			self.mCtrlProgress.setPercent( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_RECORDING1 :
			self.mCtrlLblRec1.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_RECORDING2 :
			self.mCtrlLblRec2.setLabel( aValue )


	def UpdatePropertyGUI( self, aPropertyID = None, aValue = None ) :
		#LOG_TRACE( 'Enter property[%s] value[%s]'% (aPropertyID, aValue) )
		if aPropertyID == None :
			return

		self.mWin.setProperty( aPropertyID, aValue )


	def ShowDialog( self, aFocusId ) :
		if aFocusId == E_CONTROL_ID_BUTTON_TELETEXT :
			if not self.mPlatform.IsPrismCube( ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No support %s' ) % self.mPlatform.GetName( ) )
				dialog.doModal( )
				return

			if not self.mDataCache.Teletext_Show( ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No teletext available' ) )
				dialog.doModal( )
			else :
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW, WinMgr.WIN_ID_NULLWINDOW )
				return

		elif aFocusId == E_CONTROL_ID_BUTTON_SUBTITLE :
			if not self.mPlatform.IsPrismCube( ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No support %s' ) % self.mPlatform.GetName( ) )
				dialog.doModal( )
				return

		elif aFocusId == E_CONTROL_ID_BUTTON_BOOKMARK :
			if not self.mPlatform.IsPrismCube( ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No support %s' ) % self.mPlatform.GetName( ) )
				dialog.doModal( )
				return

			self.BookMarkContext( )

		elif aFocusId == E_CONTROL_ID_BUTTON_DESCRIPTION_INFO :
			self.ShowEPGDescription( )

		elif aFocusId == E_CONTROL_ID_BUTTON_SETTING_FORMAT :
			self.mEventBus.Deregister( self )
			self.AudioVideoContext( )
			self.mEventBus.Register( self )


	def EventReceivedDialog( self, aDialog ) :
		ret = aDialog.GetCloseStatus( )
		if ret == Action.ACTION_PLAYER_PLAY :
			xbmc.executebuiltin('xbmc.Action(play)')

		elif ret == Action.ACTION_STOP :
			xbmc.executebuiltin('xbmc.Action(stop)')


	def BookMarkContext( self ) :
		context = []
		context.append( ContextItem( 'Create bookmark', CONTEXT_ACTION_ADD_TO_BOOKMARK ) )
		context.append( ContextItem( 'Show all bookmarks',  CONTEXT_ACTION_SHOW_LIST ) )

		self.mEventBus.Deregister( self )
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
		dialog.doModal( )
		self.mEventBus.Register( self )

		self.EventReceivedDialog( dialog )

		selectAction = dialog.GetSelectedAction( )
		if selectAction == -1 :
			return

		if selectAction == CONTEXT_ACTION_ADD_TO_BOOKMARK :
			self.mDataCache.Player_CreateBookmark( )

		elif selectAction == CONTEXT_ACTION_SHOW_LIST :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_BOOKMARK )
			dialog.SetDefaultProperty( self.mPlayingRecord )
			dialog.doModal( )
			#tempList = dialog.GetSelectedList( )
			#LOG_TRACE('------------dialog list[%s]'% tempList )


	def AudioVideoContext( self ) :
		context = []
		context.append( ContextItem( 'Video format', CONTEXT_ACTION_VIDEO_SETTING ) )
		context.append( ContextItem( 'Audio track',  CONTEXT_ACTION_AUDIO_SETTING ) )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
		dialog.doModal( )

		self.EventReceivedDialog( dialog )

		selectAction = dialog.GetSelectedAction( )
		if selectAction == -1 :
			return

		if selectAction == CONTEXT_ACTION_VIDEO_SETTING :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SET_AUDIOVIDEO )
			dialog.SetValue( selectAction )
 			dialog.doModal( )

 			self.EventReceivedDialog( dialog )

 		else :
			getCount = self.mDataCache.Audiotrack_GetCount( )
			selectIdx= self.mDataCache.Audiotrack_GetSelectedIndex( )

			context = []
			iSelectAction = 0
			for idx in range(getCount) :
				idxTrack = self.mDataCache.Audiotrack_Get( idx )
				#LOG_TRACE('getTrack name[%s] lang[%s]'% (idxTrack.mName, idxTrack.mLang) )
				label = '%s-%s'% ( idxTrack.mName, idxTrack.mLang )

				context.append( ContextItem( label, iSelectAction ) )
				iSelectAction += 1

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context, selectIdx )
			dialog.doModal( )

			self.EventReceivedDialog( dialog )

			selectIdx2 = dialog.GetSelectedAction( )
			self.mDataCache.Audiotrack_select( selectIdx2 )
			#LOG_TRACE('Select[%s --> %s]'% (selectAction, selectIdx2) )


	def ShowEPGDescription( self ) :
		if self.mCurrentEPG == None or self.mCurrentEPG.mError != 0 :
			return

		self.mEventBus.Deregister( self )
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_EXTEND_EPG )
		dialog.SetEPG( self.mCurrentEPG )
		dialog.doModal( )
		self.mEventBus.Register( self )

		ret = dialog.GetCloseStatus( )
		if ret == Action.ACTION_CONTEXT_MENU :
			self.Close( )
			WinMgr.GetInstance( ).CloseWindow( )
		else:
			self.EventReceivedDialog( dialog )


 	def ShowRecordingInfo( self ) :
		try:
			isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )
			#LOG_TRACE('isRunRecCount[%s]'% isRunRec)

			strLabelRecord1 = ''
			strLabelRecord2 = ''
			setPropertyRecord1 = 'False'
			setPropertyRecord2 = 'False'
			if isRunRec == 1 :
				setPropertyRecord1 = 'True'
				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 0 )
				strLabelRecord1 = '%04d %s'% ( int(recInfo.mChannelNo), recInfo.mChannelName )

			elif isRunRec == 2 :
				setPropertyRecord1 = 'True'
				setPropertyRecord2 = 'True'
				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 0 )
				strLabelRecord1 = '%04d %s'% ( int(recInfo.mChannelNo), recInfo.mChannelName )
				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 1 )
				strLabelRecord2 = '%04d %s'% ( int(recInfo.mChannelNo), recInfo.mChannelName )

			self.UpdateControlGUI( E_CONTROL_ID_LABEL_RECORDING1, strLabelRecord1 )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_RECORDING2, strLabelRecord2 )
			self.UpdatePropertyGUI( E_XML_PROPERTY_RECORDING1, setPropertyRecord1 )
			self.UpdatePropertyGUI( E_XML_PROPERTY_RECORDING2, setPropertyRecord2 )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.mEnableLocalThread = False

		self.StopAutomaticHide( )
		#WinMgr.GetInstance( ).CloseWindow( )


	def SetAutomaticHide( self, aHide=True ) :
		self.mAutomaticHide = aHide


	def GetAutomaticHide( self ) :
		return self.mAutomaticHide

	
	def AsyncAutomaticHide( self ) :
		#LOG_TRACE('DO WinId=%s'% xbmcgui.getCurrentWindowId( ) )
		#LOG_TRACE('DO DlgWinId=%s'% xbmcgui.getCurrentWindowDialogId( ) )
		xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )
		#self.Close( )


	def RestartAutomaticHide( self ) :
		self.StopAutomaticHide( )
		self.StartAutomaticHide( )

	
	def StartAutomaticHide( self ) :
		#LOG_TRACE('-----hide START')		
		prop = ElisPropertyEnum( 'Channel Banner Duration', self.mCommander )
		bannerTimeout = prop.GetProp( )
		self.mAutomaticHideTimer = threading.Timer( bannerTimeout, self.AsyncAutomaticHide )
		self.mAutomaticHideTimer.start( )


	def StopAutomaticHide( self ) :
		#LOG_TRACE('-----hide STOP')		
		if self.mAutomaticHideTimer and self.mAutomaticHideTimer.isAlive( ) :
			self.mAutomaticHideTimer.cancel( )
			del self.mAutomaticHideTimer
			
		self.mAutomaticHideTimer = None


	def MoveToSeekFrame( self, aKey ) :
		if aKey == 0 :
			return -1

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_TIMESHIFT_JUMP )
		dialog.SetDialogProperty( str( aKey ), E_INDEX_JUMP_MAX, None )
		dialog.doModal( )

		isOK = dialog.IsOK( )
		if isOK == E_DIALOG_STATE_YES :

			move = dialog.GetMoveToJump( )
			if move :
				ret = self.mDataCache.Player_JumpToIFrame( int( move ) )


