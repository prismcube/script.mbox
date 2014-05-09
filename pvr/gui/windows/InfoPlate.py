from pvr.gui.WindowImport import *

E_INFO_PLATE_BASE_ID = WinMgr.WIN_ID_LIVE_PLATE * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID

E_CONTROL_ID_IMAGE_RECORDING1 			= 10 + E_INFO_PLATE_BASE_ID
E_CONTROL_ID_LABEL_RECORDING1 			= 11 + E_INFO_PLATE_BASE_ID
E_CONTROL_ID_IMAGE_RECORDING2 			= 15 + E_INFO_PLATE_BASE_ID
E_CONTROL_ID_LABEL_RECORDING2 			= 16 + E_INFO_PLATE_BASE_ID
E_CONTROL_ID_BUTTON_PREV_EPG 			= 702 + E_INFO_PLATE_BASE_ID
E_CONTROL_ID_BUTTON_NEXT_EPG 			= 706 + E_INFO_PLATE_BASE_ID
E_CONTROL_ID_LABEL_CHANNEL_NUMBER		= 601 + E_INFO_PLATE_BASE_ID
E_CONTROL_ID_LABEL_CHANNEL_NAME			= 602 + E_INFO_PLATE_BASE_ID
E_CONTROL_ID_IMAGE_SERVICETYPE_TV		= 603 + E_INFO_PLATE_BASE_ID
E_CONTROL_ID_IMAGE_SERVICETYPE_RADIO	= 604 + E_INFO_PLATE_BASE_ID
E_CONTROL_ID_GROUP_COMPONENT_DATA		= 605 + E_INFO_PLATE_BASE_ID
E_CONTROL_ID_GROUP_COMPONENT_DOLBY 		= 606 + E_INFO_PLATE_BASE_ID
E_CONTROL_ID_GROUP_COMPONENT_HD			= 607 + E_INFO_PLATE_BASE_ID
#E_CONTROL_ID_IMAGE_LOCKED 				= 651 + E_INFO_PLATE_BASE_ID
#E_CONTROL_ID_IMAGE_ICAS 				= 652 + E_INFO_PLATE_BASE_ID
E_CONTROL_ID_LABEL_LONGITUDE_INFO		= 701 + E_INFO_PLATE_BASE_ID
E_CONTROL_ID_LABEL_EPG_NAME				= 703 + E_INFO_PLATE_BASE_ID
E_CONTROL_ID_LABEL_EPG_STARTTIME		= 704 + E_INFO_PLATE_BASE_ID
E_CONTROL_ID_LABEL_EPG_ENDTIME			= 705 + E_INFO_PLATE_BASE_ID
E_CONTROL_ID_PROGRESS_EPG 				= 707 + E_INFO_PLATE_BASE_ID

E_CONTROL_ID_HOTKEY_RED_IMAGE 			= E_INFO_PLATE_BASE_ID + 511
E_CONTROL_ID_HOTKEY_RED_LABEL 			= E_INFO_PLATE_BASE_ID + 512
E_CONTROL_ID_HOTKEY_GREEN_IMAGE 		= E_INFO_PLATE_BASE_ID + 521
E_CONTROL_ID_HOTKEY_GREEN_LABEL 		= E_INFO_PLATE_BASE_ID + 522
E_CONTROL_ID_HOTKEY_YELLOW_IMAGE 		= E_INFO_PLATE_BASE_ID + 531
E_CONTROL_ID_HOTKEY_YELLOW_LABEL 		= E_INFO_PLATE_BASE_ID + 532
E_CONTROL_ID_HOTKEY_BLUE_IMAGE 			= E_INFO_PLATE_BASE_ID + 541
E_CONTROL_ID_HOTKEY_BLUE_LABEL 			= E_INFO_PLATE_BASE_ID + 542

E_CONTROL_DEFAULT_HIDE = [ 
	E_CONTROL_ID_BUTTON_START_RECORDING,
	E_CONTROL_ID_BUTTON_STOP_RECORDING
]

E_INFO_PLATE_DEFAULT_FOCUS_ID			=  E_BASE_WINDOW_ID + 3621

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
		self.mOnBlockTimer_GreenKey = 0
		self.mIsShowDialog = False


	def onInit( self ) :
		self.setFocusId( E_INFO_PLATE_DEFAULT_FOCUS_ID )
		self.SetActivate( True )
		
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.SetSingleWindowPosition( WinMgr.WIN_ID_INFO_PLATE * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID )
		self.UpdatePropertyGUI( 'InfoPlateName', E_TAG_TRUE )

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
		#isSwap? show media surface
		if self.mDataCache.PIP_GetSwapStatus( ) :
			self.mDataCache.PIP_SwapWindow( False, False )

		self.SetRadioScreen( )
		self.InitControl( )
		self.SetVisibleControls( E_CONTROL_DEFAULT_HIDE, False )

		self.mPlayingRecord = None
		self.mCurrentEPG = None
		#self.mEnableCasInfo = False
		self.mIsShowDialog = False
		self.mSpeed = 0
		self.mPMTInfo = self.mDataCache.GetCurrentPMTEventByPVR( )
		self.mBannerTimeout = self.mDataCache.GetPropertyChannelBannerTime( )

		#get channel
		self.LoadInit( )

		if self.mPlayingRecord :
			self.SetFrontdisplayMessage( self.mPlayingRecord.mRecordName )
		else :
			self.mDataCache.Frontdisplay_SetCurrentMessage( )

		#run thread
		self.mEventBus.Register( self )
		self.mEnableLocalThread = True
		self.EPGProgressThread( )

		self.RestartAutomaticHide( )
		self.mOnBlockTimer_GreenKey = time.time( )


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			self.RestartAutomaticHide( )
			return

		if actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 :
			self.StopAutomaticHide( )
			self.MoveToSeekFrame( int( actionId ) - Action.REMOTE_0 )
			self.RestartAutomaticHide( )

		elif actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :
			rKey = actionId - (Action.ACTION_JUMP_SMS2 - 2)
			self.StopAutomaticHide( )
			self.MoveToSeekFrame( rKey )
			self.RestartAutomaticHide( )

		elif actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.Close( )
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			return
			self.StopAutomaticHide( )
			self.SetAutomaticHide( False )

		elif actionId == Action.ACTION_CONTEXT_MENU :
			self.StopAutomaticHide( )
			self.DialogPopup( E_CONTROL_ID_BUTTON_DESCRIPTION_INFO )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.RestartAutomaticHide( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.RestartAutomaticHide( )

		elif actionId == Action.ACTION_STOP :
			ret = self.mDataCache.Player_Stop( )
			if ret :
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_MBOX_ARCHIVE :
			self.Close( )
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_SHOW_INFO :
			pass
			"""
			#deprecate
			self.Close( )
			WinMgr.GetInstance( ).CloseWindow( )
			"""

		elif actionId == Action.ACTION_PAGE_UP or actionId == Action.ACTION_PAGE_DOWN :
			self.Close( )
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = actionId
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_PAUSE or actionId == Action.ACTION_PLAYER_PLAY :
			if not HasAvailableRecordingHDD( ) :
				return

			self.Close( )
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = actionId
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_MBOX_REWIND or actionId == Action.ACTION_MBOX_FF :
			if not HasAvailableRecordingHDD( ) :
				return

			self.Close( )
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = actionId
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_MBOX_TVRADIO :
			pass
			#ToDo warning msg

		elif actionId == Action.ACTION_MBOX_TEXT :
			self.DialogPopup( E_CONTROL_ID_BUTTON_TELETEXT )

		elif actionId == Action.ACTION_MBOX_SUBTITLE :
			self.DialogPopup( E_CONTROL_ID_BUTTON_SUBTITLE )

		elif actionId == Action.ACTION_COLOR_YELLOW :
			self.DialogPopup( E_CONTROL_ID_BUTTON_SETTING_FORMAT )

		elif actionId == Action.ACTION_COLOR_BLUE :
			self.DialogPopup( E_CONTROL_ID_BUTTON_PIP )

		elif actionId == Action.ACTION_COLOR_GREEN :
			if ( time.time( ) - self.mOnBlockTimer_GreenKey ) <= 1 :
				return

			self.mOnBlockTimer_GreenKey = time.time( )
			self.AddToBookmark( )


	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return

		if aControlId == E_CONTROL_ID_BUTTON_MUTE :
			self.GlobalAction( Action.ACTION_MUTE )

		elif aControlId >= E_CONTROL_ID_BUTTON_DESCRIPTION_INFO and aControlId <= E_CONTROL_ID_BUTTON_BOOKMARK :
			self.DialogPopup( aControlId )


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return


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
		self.UpdateChannelAndEPG( self.mCurrentEPG )

		if E_V1_2_APPLY_TEXTWIDTH_LABEL :
			ResizeImageWidthByTextSize( self.getControl( E_CONTROL_ID_HOTKEY_GREEN_LABEL ), self.getControl( E_CONTROL_ID_HOTKEY_GREEN_IMAGE ), MR_LANG( 'Bookmark' ), self.getControl( ( E_CONTROL_ID_HOTKEY_GREEN_IMAGE - 1 ) ) )
			ResizeImageWidthByTextSize( self.getControl( E_CONTROL_ID_HOTKEY_YELLOW_LABEL ), self.getControl( E_CONTROL_ID_HOTKEY_YELLOW_IMAGE ), MR_LANG( 'A / V' ), self.getControl( ( E_CONTROL_ID_HOTKEY_YELLOW_IMAGE - 1 ) ) )
			ResizeImageWidthByTextSize( self.getControl( E_CONTROL_ID_HOTKEY_BLUE_LABEL ), self.getControl( E_CONTROL_ID_HOTKEY_BLUE_IMAGE ), MR_LANG( 'PIP' ), self.getControl( ( E_CONTROL_ID_HOTKEY_BLUE_IMAGE - 1 ) ) )
		else :
			iRussian = E_TAG_FALSE
			if XBMC_GetCurrentLanguage( ) == 'Russian' :
				iRussian = E_TAG_TRUE
			self.UpdatePropertyGUI( 'iHotkeyGreenRussian', '%s'% iRussian )

		self.UpdatePropertyGUI( 'InfoPlateName', E_TAG_TRUE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_HOTKEY_RED,    E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_HOTKEY_GREEN,  E_TAG_TRUE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_HOTKEY_YELLOW, E_TAG_TRUE )
		if E_V1_2_APPLY_PIP :
			self.UpdatePropertyGUI( E_XML_PROPERTY_HOTKEY_BLUE,   E_TAG_TRUE )


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
				#xbmcgui.Dialog( ).ok( MR_LANG('Information'), MR_LANG('No Signal') )

			elif aEvent.getName( ) == ElisEventChannelChangeResult.getName( ) :
				pass

			elif aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or \
				 aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
 				self.ShowRecordingInfo( )

			elif aEvent.getName( ) == ElisPMTReceivedEvent.getName( ) :
				#LOG_TRACE( "--------- received ElisPMTReceivedEvent-----------" )
				self.mPMTInfo = self.mDataCache.GetCurrentPMTEventByPVR( )
				self.UpdatePropertyByCacheData( E_XML_PROPERTY_TELETEXT )
				self.UpdatePropertyByCacheData( E_XML_PROPERTY_SUBTITLE )
				self.UpdatePropertyByCacheData( E_XML_PROPERTY_DOLBYPLUS )

		else:
			LOG_TRACE( 'LivePlate winID[%d] this winID[%d]'% ( self.mWinId, xbmcgui.getCurrentWindowId( ) ) )


	def UpdateChannelAndEPG( self, aEpg = None ):
		rec = self.mPlayingRecord
		if rec :
			try :
				#self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NUMBER, '[COLOR red]PLAYBACK[/COLOR]' )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_CHANNEL_NAME, rec.mChannelName )

				#satellite
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_LONGITUDE_INFO, '%s'% MR_LANG( 'Archive' ) )

				#lock,cas
				if rec.mLocked :
					self.UpdatePropertyGUI( E_XML_PROPERTY_LOCK, 'True' )
				"""
				self.mEnableCasInfo = False
				if rec.mIsCA :
					self.UpdatePropertyGUI( E_XML_PROPERTY_CAS, 'True' )
					casInfo = HasCasInfoByChannel( rec )
					if casInfo and len( casInfo ) > 1 :
						self.mEnableCasInfo = True
						self.ShowCasInfoThread( casInfo )

					elif casInfo and len( casInfo ) == 1 :
						self.UpdatePropertyGUI( 'iCasInfo', casInfo[0] )

					else :
						self.UpdatePropertyGUI( 'iCasInfo', '' )
				"""
				#if rec.mIsCA :
				UpdateCasInfo( self, rec )

				#record name
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_NAME, deepcopy( rec.mRecordName ) )

				#start,end
				label = TimeToString( rec.mStartTime, TimeFormatEnum.E_HH_MM )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_STARTTIME, label )
				label = TimeToString( rec.mStartTime + rec.mDuration, TimeFormatEnum.E_HH_MM )
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_EPG_ENDTIME,   label )

				#component
				self.UpdatePropertyByCacheData( E_XML_PROPERTY_TELETEXT )
				isSubtitle = self.UpdatePropertyByCacheData( E_XML_PROPERTY_SUBTITLE )
				if not isSubtitle :
					self.UpdatePropertyGUI( E_XML_PROPERTY_SUBTITLE, HasEPGComponent( aEpg, ElisEnum.E_HasSubtitles ) )
				if not self.UpdatePropertyByCacheData( E_XML_PROPERTY_DOLBYPLUS ) :
					self.UpdatePropertyGUI( E_XML_PROPERTY_DOLBY,HasEPGComponent( aEpg, ElisEnum.E_HasDolbyDigital ) )
				self.UpdatePropertyGUI( E_XML_PROPERTY_HD,       HasEPGComponent( aEpg, ElisEnum.E_HasHDVideo ) )

				#age info
				UpdatePropertyByAgeRating( self, aEpg )

			except Exception, e:
				LOG_TRACE( 'Error exception[%s]'% e )

	"""
	@RunThread
	def ShowCasInfoThread( self, aCasInfo ) :
		while self.mEnableCasInfo :
			for item in aCasInfo :
				self.UpdatePropertyGUI( 'iCasInfo', item )

				loopCount = 0
				while loopCount < 3 :
					if not self.mEnableCasInfo :
						break
					loopCount += 0.5
					time.sleep( 0.5 )

			time.sleep( 0.5 )
		self.UpdatePropertyGUI( 'iCasInfo', '' )
	"""

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
				self.mSpeed = status.mSpeed
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
		#self.mCtrlBtnPrevEpg.setVisible( False )
		#self.mCtrlBtnNextEpg.setVisible( False )

		tvValue = E_TAG_TRUE
		raValue = E_TAG_FALSE
		if self.mPlayingRecord :
			if self.mPlayingRecord.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
				tvValue = E_TAG_FALSE
				raValue = E_TAG_TRUE
		else :
			tvValue = E_TAG_FALSE
			raValue = E_TAG_FALSE

		self.UpdatePropertyGUI( E_XML_PROPERTY_TV,       tvValue )
		self.UpdatePropertyGUI( E_XML_PROPERTY_RADIO,    raValue )
		self.UpdatePropertyGUI( E_XML_PROPERTY_LOCK,     E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_CAS,      E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_FAV,      E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_TELETEXT, E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_SUBTITLE, E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_DOLBY,    E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_DOLBYPLUS,E_TAG_FALSE )
		self.UpdatePropertyGUI( E_XML_PROPERTY_HD,       E_TAG_FALSE )
		self.UpdatePropertyGUI( 'iCasInfo', '' )
		self.UpdatePropertyGUI( 'EPGAgeRating', '' )
		self.UpdatePropertyGUI( 'HasAgeRating', 'None' )
		#self.mEnableCasInfo = False


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


	def UpdatePropertyByCacheData( self, aPropertyID = None ) :
		ret = UpdatePropertyByCacheData( self, self.mPMTInfo, aPropertyID )
		return ret


	def UpdatePropertyGUI( self, aPropertyID = None, aValue = None ) :
		#LOG_TRACE( 'Enter property[%s] value[%s]'% (aPropertyID, aValue) )
		if aPropertyID == None :
			return False

		self.setProperty( aPropertyID, aValue )


	def DialogPopup( self, aFocusId ) :
		if self.mIsShowDialog == False :
			thread = threading.Timer( 0.1, self.ShowDialog, [aFocusId] )
			thread.start( )
		else :
			LOG_TRACE( 'Already opened, Dialog' )


	def ShowDialog( self, aFocusId ) :
		self.mIsShowDialog = True
		self.StopAutomaticHide( )

		if aFocusId == E_CONTROL_ID_BUTTON_TELETEXT :
			if not self.mPlatform.IsPrismCube( ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No %s support' ) % self.mPlatform.GetName( ) )
				dialog.doModal( )
				self.mIsShowDialog = False
				self.RestartAutomaticHide( )
				return

			if not self.mDataCache.Teletext_Show( ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'No Teletext' ), MR_LANG( 'No teletext available' ) )
				dialog.doModal( )
			else :
				self.mIsShowDialog = False
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW, WinMgr.WIN_ID_NULLWINDOW )
				return

		elif aFocusId == E_CONTROL_ID_BUTTON_SUBTITLE :
			if not self.mPlatform.IsPrismCube( ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No %s support' ) % self.mPlatform.GetName( ) )
				dialog.doModal( )
				self.mIsShowDialog = False
				self.RestartAutomaticHide( )
				return

			ret = ShowSubtitle( )
			if ret > -1 :
				self.mIsShowDialog = False
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
				return
			elif ret == -2 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'No Subtitle' ), MR_LANG( 'No subtitle available' ) )
				dialog.doModal( )

		elif aFocusId == E_CONTROL_ID_BUTTON_BOOKMARK :
			self.mIsShowDialog = False
			self.Close( )
			WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE ).mPrekey = E_DEFAULT_ACTION_CLICK_EVENT + CONTEXT_ACTION_SHOW_BOOKMARK
			WinMgr.GetInstance( ).CloseWindow( )
			return

		elif aFocusId == E_CONTROL_ID_BUTTON_DESCRIPTION_INFO :
			self.ShowEPGDescription( )

		elif aFocusId == E_CONTROL_ID_BUTTON_SETTING_FORMAT :
			#self.mEventBus.Deregister( self )
			DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_SET_AUDIOVIDEO ).doModal( )
 			#self.EventReceivedDialog( dialog )
			#self.mEventBus.Register( self )

		elif aFocusId == E_CONTROL_ID_BUTTON_PIP :
			pipDialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_PIP )
			pipDialog.doModal( )
			if pipDialog.GetCloseStatus( ) == Action.ACTION_STOP :
				self.mIsShowDialog = False
				LOG_TRACE( '[InfoPlate] no automaticHide by pvr/timeshift stop on PIP' )
				self.Close( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW, WinMgr.WIN_ID_NULLWINDOW )
				return

		self.RestartAutomaticHide( )
		self.mIsShowDialog = False


	def AddToBookmark( self, aSelectAction ) :
		if not self.mPlayingRecord :
			return

		bookmarkList = self.mDataCache.Player_GetBookmarkList( self.mPlayingRecord.mRecordKey )
		if bookmarkList and len( bookmarkList ) >= E_DEFAULT_BOOKMARK_LIMIT :
			head = MR_LANG( 'Error' )
			msg = MR_LANG( 'You have reached the maximum number of%s bookmarks allowed' )% NEW_LINE
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( head, msg )
			dialog.doModal( )
			return

		else :
			if self.mSpeed != 100 :
				self.mDataCache.Player_Resume( )

			self.mDataCache.Player_CreateBookmark( )


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
			#WinMgr.GetInstance( ).CloseWindow( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
		else:
			self.EventReceivedDialog( dialog )


 	def ShowRecordingInfo( self ) :
		try:
			isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )
			isRunningTimerList = self.mDataCache.Timer_GetRunningTimers( )
			#LOG_TRACE('isRunRecCount[%s]'% isRunRec)
			runningRecordCount = 0

			if isRunningTimerList :
				runningRecordCount = len( isRunningTimerList )

			#LOG_TRACE( "runningRecordCount=%d" %runningRecordCount )

			strLabelRecord1 = ''
			strLabelRecord2 = ''
			setPropertyRecord1 = 'False'
			setPropertyRecord2 = 'False'
			if isRunRec == 1 and runningRecordCount == 1 :
				setPropertyRecord1 = 'True'
				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 0 )
				timer = isRunningTimerList[0]

				channel = self.mDataCache.GetChannelByIDs( timer.mSid, timer.mTsid, timer.mOnid )
				iChNumber = recInfo.mChannelNo
				if channel :
					iChNumber = channel.mNumber
					if E_V1_2_APPLY_PRESENTATION_NUMBER :
						iChNumber = self.mDataCache.CheckPresentationNumber( channel )
				strLabelRecord1 = '(%s~%s)  %04d %s'% ( TimeToString( timer.mStartTime, TimeFormatEnum.E_HH_MM ), TimeToString( ( timer.mStartTime + timer.mDuration) , TimeFormatEnum.E_HH_MM ), int( iChNumber ), recInfo.mChannelName )

			elif isRunRec == 2 and runningRecordCount == 2 :
				setPropertyRecord1 = 'True'
				setPropertyRecord2 = 'True'
				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 0 )
				timer = isRunningTimerList[0]
				channel = self.mDataCache.GetChannelByIDs( timer.mSid, timer.mTsid, timer.mOnid )
				iChNumber = recInfo.mChannelNo
				if channel :
					iChNumber = channel.mNumber
					if E_V1_2_APPLY_PRESENTATION_NUMBER :
						iChNumber = self.mDataCache.CheckPresentationNumber( channel )
				strLabelRecord1 = '(%s~%s)  %04d %s'% ( TimeToString( timer.mStartTime, TimeFormatEnum.E_HH_MM ), TimeToString( ( timer.mStartTime + timer.mDuration) , TimeFormatEnum.E_HH_MM ), int( iChNumber ), recInfo.mChannelName )

				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 1 )
				timer = isRunningTimerList[1]
				channel = self.mDataCache.GetChannelByIDs( timer.mSid, timer.mTsid, timer.mOnid )
				iChNumber = recInfo.mChannelNo
				if channel :
					iChNumber = channel.mNumber
					if E_V1_2_APPLY_PRESENTATION_NUMBER :
						iChNumber = self.mDataCache.CheckPresentationNumber( channel )
				strLabelRecord2 = '(%s~%s)  %04d %s'% ( TimeToString( timer.mStartTime, TimeFormatEnum.E_HH_MM ), TimeToString( ( timer.mStartTime + timer.mDuration) , TimeFormatEnum.E_HH_MM ), int( iChNumber ), recInfo.mChannelName )

			self.UpdateControlGUI( E_CONTROL_ID_LABEL_RECORDING1, strLabelRecord1 )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_RECORDING2, strLabelRecord2 )
			self.UpdatePropertyGUI( E_XML_PROPERTY_RECORDING1, setPropertyRecord1 )
			self.UpdatePropertyGUI( E_XML_PROPERTY_RECORDING2, setPropertyRecord2 )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.mEnableLocalThread = False
		#self.mEnableCasInfo = False

		self.StopAutomaticHide( )
		#WinMgr.GetInstance( ).CloseWindow( )

		#isSwap? swap surface
		if self.mDataCache.PIP_GetSwapStatus( ) :
			self.mDataCache.PIP_SwapWindow( True, False )


	def SetAutomaticHide( self, aHide=True ) :
		self.mAutomaticHide = aHide


	def GetAutomaticHide( self ) :
		return self.mAutomaticHide

	
	def AsyncAutomaticHide( self ) :
		#LOG_TRACE('DO WinId=%s'% xbmcgui.getCurrentWindowId( ) )
		#LOG_TRACE('DO DlgWinId=%s'% xbmcgui.getCurrentWindowDialogId( ) )
		if self.mAutomaticHide == True :
			xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )
		#self.Close( )


	def RestartAutomaticHide( self ) :
		self.StopAutomaticHide( )
		self.StartAutomaticHide( )

	
	def StartAutomaticHide( self ) :
		#LOG_TRACE('-----hide START')		
		self.mAutomaticHideTimer = threading.Timer( self.mBannerTimeout, self.AsyncAutomaticHide )
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
		dialog.SetDialogProperty( str( aKey ) )
		dialog.doModal( )

		isOK = dialog.IsOK( )
		if isOK == E_DIALOG_STATE_YES :

			move = dialog.GetMoveToJump( )
			if move :
				if self.mSpeed != 100 :
					self.mDataCache.Player_Resume( )

				ret = self.mDataCache.Player_JumpToIFrame( int( move ) )


