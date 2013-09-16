from pvr.gui.WindowImport import *
import traceback

E_PIP_WINDOW_BASE_ID		=  WinMgr.WIN_ID_PIP_WINDOW * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID
CTRL_ID_BUTTON_SETTING_PIP	= E_PIP_WINDOW_BASE_ID + 0001

CTRL_ID_GROUP_PIP			= E_PIP_WINDOW_BASE_ID + 1000
CTRL_ID_IMAGE_NFOCUSED		= E_PIP_WINDOW_BASE_ID + 1001
CTRL_ID_IMAGE_FOCUSED		= E_PIP_WINDOW_BASE_ID + 1002
#CTRL_ID_IMAGE_BLANK			= E_PIP_WINDOW_BASE_ID + 1003
CTRL_ID_LABEL_CHANNEL		= E_PIP_WINDOW_BASE_ID + 1004

CTRL_ID_GROUP_OSD_STATUS	= E_PIP_WINDOW_BASE_ID + 2001
CTRL_ID_IMAGE_OSD_STATUS	= E_PIP_WINDOW_BASE_ID + 2002

CTRL_ID_IMAGE_ARROW_LEFT	= E_PIP_WINDOW_BASE_ID + 3001
CTRL_ID_IMAGE_ARROW_RIGHT	= E_PIP_WINDOW_BASE_ID + 3002
CTRL_ID_IMAGE_ARROW_TOP		= E_PIP_WINDOW_BASE_ID + 3003
CTRL_ID_IMAGE_ARROW_BOTTOM	= E_PIP_WINDOW_BASE_ID + 3004

CTRL_ID_GROUP_LIST_PIP		= E_PIP_WINDOW_BASE_ID + 8000
CTRL_ID_BUTTON_NEXT_PIP		= E_PIP_WINDOW_BASE_ID + 8001
CTRL_ID_BUTTON_PREV_PIP		= E_PIP_WINDOW_BASE_ID + 8002
CTRL_ID_BUTTON_MUTE_PIP		= E_PIP_WINDOW_BASE_ID + 8003
CTRL_ID_BUTTON_ACTIVE_PIP	= E_PIP_WINDOW_BASE_ID + 8004
CTRL_ID_BUTTON_MOVE_PIP		= E_PIP_WINDOW_BASE_ID + 8005
CTRL_ID_BUTTON_SIZE_PIP		= E_PIP_WINDOW_BASE_ID + 8006
CTRL_ID_BUTTON_DEFAULT_PIP	= E_PIP_WINDOW_BASE_ID + 8007
CTRL_ID_BUTTON_EXIT_PIP		= E_PIP_WINDOW_BASE_ID + 8008
CTRL_ID_BUTTON_STOP_PIP		= E_PIP_WINDOW_BASE_ID + 8009

E_DEFAULT_POSITION_PIP		= [827,125,352,188]#[857,170,352,198] 
CONTEXT_ACTION_DONE_PIP		= 0
CONTEXT_ACTION_MOVE_PIP		= 1
CONTEXT_ACTION_SIZE_PIP		= 2
CONTEXT_ACTION_ACTIVE_PIP	= 3
CONTEXT_ACTION_DEFAULT_PIP 	= 4
CONTEXT_ACTION_STOP_PIP	= 5

E_POSX_ABILITY   = 10
E_POSY_ABILITY   = 5
E_WIDTH_ABILITY  = 20
E_HEIGHT_ABILITY = 10


CURR_CHANNEL_PIP = 0
PREV_CHANNEL_PIP = 1
NEXT_CHANNEL_PIP = 2
SWITCH_CHANNEL_PIP = 3

'''
class PIPWindow( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mLock = thread.allocate_lock( )
		self.mPIPStart = False
	

	def onInit( self ) :
		self.SetActivate( True )
		self.SetFrontdisplayMessage( MR_LANG('PIP Channel') )
		self.mWinId = xbmcgui.getCurrentWindowId( )

		#self.SetSingleWindowPosition( E_PIP_WINDOW_BASE_ID )
		#self.SetPipScreen( )

		self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( )
		self.mCurrentChannel = self.mDataCache.Channel_GetCurrent( )
		self.mServiceType	 = self.mCurrentMode.mServiceType

		LOG_TRACE( 'ZeppingMode(%d,%d,%d)' %( self.mCurrentMode.mServiceType, self.mCurrentMode.mMode, self.mCurrentMode.mSortingMode ) )
		self.mChannelList = self.mDataCache.Channel_GetList( )
		self.mChannelListHash = {}

		#LOG_TRACE( "ChannelList=%d" %len( self.mChannelList ) )
		
		if self.mChannelList :
			for channel in self.mChannelList :
				self.mChannelListHash[ '%d:%d:%d' %( channel.mSid, channel.mTsid, channel.mOnid) ] = channel
	
		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		self.mInitialized = True
		
		self.Load( )

		#self.mEventBus.Register( self )
		self.setFocusId( CTRL_ID_BUTTON_NEXT_PIP )


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		self.GetFocusId( )
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		#LOG_TRACE('onAction=%d' %actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.Close( )

		elif actionId == Action.ACTION_MOVE_RIGHT:
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_SIMPLE_CHANNEL_LIST )

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_PAGE_UP or actionId == Action.ACTION_PAGE_DOWN :
			#WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_SIMPLE_CHANNEL_LIST )
			return

		elif actionId == Action.ACTION_MBOX_TVRADIO :
			LOG_TRACE( 'Not supported Radio' )
			return

			"""
			self.mEventBus.Deregister( self )

			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.ToggleTVRadio( )
				if ret :
					self.SetRadioScreen( self.mServiceType )

				else :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No channels available for the selected mode' ) )
					dialog.doModal( )

			self.mEventBus.Register( self )			
			"""

		elif actionId == Action.ACTION_SELECT_ITEM :
			return
			#if self.mFocusId  == CTRL_ID_BUTTON_NEXT_PIP :
			#	self.Tune( )


		else :
			self.NotAvailAction( )
			LOG_TRACE( 'unknown key[%s]'% actionId )


	def onClick( self, aControlId ) :
		LOG_TRACE( 'onClick' )
		#if aControlId  == LIST_ID_BIG_CHANNEL :
		#	self.Tune( )


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			LOG_TRACE( '--------------------PIP onEvent[%s]'% aEvent.getName( ) )
			if aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
				#if self.mIsUpdateEnable == True	:
				LOG_TRACE( 'record start/stop event' )
				#ToDO

			elif aEvent.getName( ) == ElisEventCurrentEITReceived.getName( ) :
				if self.mFirstTune == True :
					self.mFirstTune = False
					LOG_TRACE( '--------------- First Tune -----------------' )
					#ToDO


	def Close( self ) :
		LOG_TRACE( 'PIP Window close')
		#self.mEventBus.Deregister( self )
		ret = self.mDataCache.PIP_Stop( )
		if ret :
			self.mPIPStart = False
		LOG_TRACE( '---------pip stop ret[%s]'% ret )

		WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
		#self.CloseDialog( )


	def GetPIPStatus( self ) :
		return self.mPIPStart


	def UpdatePropertyGUI( self, aPropertyID = None, aValue = None ) :
		#LOG_TRACE( 'Enter property[%s] value[%s]'% (aPropertyID, aValue) )
		if aPropertyID == None :
			return False

		self.setProperty( aPropertyID, aValue )


	def Load( self ) :
		if self.mPIPStart :
			LOG_TRACE( '--------Already started PIP' )
			return

		pChNumber = self.Channel_GetCurrentByPIP( )
		if not pChNumber :
			self.Close( )
			LOG_TRACE( '------------except------not pChNumber[%s]'% pChNumber )
			return

		self.mDataCache.PIP_SetDimension( 857, 170, 352, 198 )
		ret = self.mDataCache.PIP_Start( pChNumber )
		LOG_TRACE( '---------pip start ret[%s] ch[%s]'% ( ret, pChNumber ) )
		if ret :
			self.mPIPStart = True
			self.UpdatePropertyGUI( 'ShowPIPChannelNumber', '%s'% pChNumber ) 


	def Channel_GetCurrentByPIP( self ) :
		LOG_TRACE( 'mPIPStart[%s]'% self.mPIPStart )
		pChNumber = self.mDataCache.PIP_GetCurrent( )
		#pChNumber = self.mDataCache.Channel_GetCurrent( ).mNumber
		LOG_TRACE( 'PIP_GetCurrent[%s]'% pChNumber )
		if not pChNumber or ( not self.mDataCache.Channel_GetCurr( pChNumber ) ) :
			iChannel = self.mDataCache.Channel_GetCurrent( )
			if iChannel :
				pChNumber = iChannel.mNumber

			else :
				channelList = self.mDataCache.Channel_GetList( )
				if channelList and len( channelList ) > 0 :
					pChNumber = channelList[0].mNumber

		if not pChNumber :			
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			lblTitle = MR_LANG( 'Attention' )
			lblMsg = MR_LANG( 'Can not show PIP, Channel is empty' )
			dialog.SetDialogProperty( lblTitle, lblMsg )
			dialog.doModal( )

		return pChNumber



#-------------------------------------------------------------------------------------------------
class DialogTestCode( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
'''
class PIPWindow( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mLock = thread.allocate_lock( )
		self.mPIPStart = False
	

	def onInit( self ) :
		self.SetActivate( True )
		self.SetFrontdisplayMessage( MR_LANG('PIP Channel') )
		self.mWinId = xbmcgui.getCurrentWindowId( )

		self.SetSingleWindowPosition( E_PIP_WINDOW_BASE_ID )
		#self.SetPipScreen( )

		self.mCtrlGroupPIP     = self.getControl( CTRL_ID_GROUP_PIP )
		#self.mCtrlImageBlank   = self.getControl( CTRL_ID_IMAGE_BLANK )
		self.mCtrlLabelChannel = self.getControl( CTRL_ID_LABEL_CHANNEL )
		self.mCtrlImageFocusNF = self.getControl( CTRL_ID_IMAGE_NFOCUSED )
		self.mCtrlImageFocusFO = self.getControl( CTRL_ID_IMAGE_FOCUSED )
		self.mCtrlImageArrowLeft   = self.getControl( CTRL_ID_IMAGE_ARROW_LEFT )
		self.mCtrlImageArrowRight  = self.getControl( CTRL_ID_IMAGE_ARROW_RIGHT )
		self.mCtrlImageArrowTop    = self.getControl( CTRL_ID_IMAGE_ARROW_TOP )
		self.mCtrlImageArrowBottom = self.getControl( CTRL_ID_IMAGE_ARROW_BOTTOM )
		self.mCtrlGroupOsdStatus   = self.getControl( CTRL_ID_GROUP_OSD_STATUS )
		self.mCtrlImageOsdStatus   = self.getControl( CTRL_ID_IMAGE_OSD_STATUS )

		self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( )
		self.mCurrentChannel = self.mDataCache.PIP_GetCurrent( )
		#self.mServiceType	 = self.mCurrentMode.mServiceType
		#LOG_TRACE( 'ZeppingMode(%d,%d,%d)' %( self.mCurrentMode.mServiceType, self.mCurrentMode.mMode, self.mCurrentMode.mSortingMode ) )

		self.mChannelList = self.mDataCache.Channel_GetList( )
		self.mChannelListHash = {}
		self.mViewMode = CONTEXT_ACTION_DONE_PIP
		self.mPosCurrent = deepcopy( E_DEFAULT_POSITION_PIP )
		self.mCurrentChannel = None
		self.mPIP_EnableAudio = False

		#LOG_TRACE( "ChannelList=%d" %len( self.mChannelList ) )
		
		if self.mChannelList :
			for channel in self.mChannelList :
				self.mChannelListHash[ '%d:%d:%d' %( channel.mSid, channel.mTsid, channel.mOnid) ] = channel
	
		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		self.mInitialized = True
		
		self.Load( )

		labelMode = MR_LANG( 'PIP Window' )
		thread = threading.Timer( 0.1, AsyncShowStatus, [labelMode] )
		thread.start( )

		#self.mEventBus.Register( self )
		self.setFocusId( CTRL_ID_BUTTON_NEXT_PIP )


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		self.GetFocusId( )
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		LOG_TRACE('onAction[%d] viewMode[%s] focus[%s]'% ( actionId, self.mViewMode, self.mFocusId ) )

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			if self.mViewMode > CONTEXT_ACTION_DONE_PIP :
				self.mViewMode = CONTEXT_ACTION_DONE_PIP
				self.ResetLabel( ) 
				return

			self.Close( False )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.DoSettingToPIP( actionId )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			ret = self.DoSettingToPIP( actionId )
#			if not ret :
#				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_SIMPLE_CHANNEL_LIST )

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN :
			ret = self.DoSettingToPIP( actionId )
#			if not ret :
#				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_PAGE_UP :
			self.ChannelTuneToPIP( NEXT_CHANNEL_PIP )

		elif actionId == Action.ACTION_PAGE_DOWN :
			self.ChannelTuneToPIP( PREV_CHANNEL_PIP )

		elif actionId == Action.ACTION_MBOX_TVRADIO :
			LOG_TRACE( 'Not supported Radio' )
			return

			"""
			self.mEventBus.Deregister( self )

			status = self.mDataCache.Player_GetStatus( )
			if status.mMode == ElisEnum.E_MODE_LIVE :
				ret = self.ToggleTVRadio( )
				if ret :
					self.SetRadioScreen( self.mServiceType )

				else :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No channels available for the selected mode' ) )
					dialog.doModal( )

			self.mEventBus.Register( self )			
			"""

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

#		elif actionId == Action.ACTION_CONTEXT_MENU :
#			if self.mViewMode == CONTEXT_ACTION_DONE_PIP :
#				self.ShowContextMenu( )

		else :
			#self.NotAvailAction( )
			LOG_TRACE( 'unknown key[%s]'% actionId )


	def onClick( self, aControlId ) :
		LOG_TRACE( 'onClick[%s]'% aControlId )

		if aControlId  == CTRL_ID_BUTTON_PREV_PIP :
			self.ChannelTuneToPIP( PREV_CHANNEL_PIP )

		elif aControlId  == CTRL_ID_BUTTON_NEXT_PIP :
			self.ChannelTuneToPIP( NEXT_CHANNEL_PIP )

		elif aControlId  == CTRL_ID_BUTTON_MUTE_PIP :
			self.SetAudioPIP( )

		elif aControlId  == CTRL_ID_BUTTON_ACTIVE_PIP :
			self.ChannelTuneToPIP( SWITCH_CHANNEL_PIP )

		elif aControlId  == CTRL_ID_BUTTON_MOVE_PIP :
			if self.mViewMode == CONTEXT_ACTION_DONE_PIP :
				self.DoContextAction( CONTEXT_ACTION_MOVE_PIP )
			else :
				self.mViewMode = CONTEXT_ACTION_DONE_PIP
				self.ResetLabel( )

		elif aControlId  == CTRL_ID_BUTTON_SIZE_PIP :
			if self.mViewMode == CONTEXT_ACTION_DONE_PIP :
				self.DoContextAction( CONTEXT_ACTION_SIZE_PIP )
			else :
				self.mViewMode = CONTEXT_ACTION_DONE_PIP
				self.ResetLabel( )

		elif aControlId  == CTRL_ID_BUTTON_DEFAULT_PIP :
			self.DoContextAction( CONTEXT_ACTION_DEFAULT_PIP )

		elif aControlId  == CTRL_ID_BUTTON_EXIT_PIP :
			self.Close( False )

		elif aControlId  == CTRL_ID_BUTTON_STOP_PIP :
			self.DoContextAction( CONTEXT_ACTION_STOP_PIP )


	def onFocus( self, aControlId ) :
		pass
#		if self.IsActivate( ) == False  :
#			return


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			LOG_TRACE( '--------------------PIP onEvent[%s]'% aEvent.getName( ) )
			if aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
				#if self.mIsUpdateEnable == True	:
				LOG_TRACE( 'record start/stop event' )
				#ToDO

			elif aEvent.getName( ) == ElisEventCurrentEITReceived.getName( ) :
				if self.mFirstTune == True :
					self.mFirstTune = False
					LOG_TRACE( '--------------- First Tune -----------------' )
					#ToDO


	def Close( self, aStopPIP = True ) :
		LOG_TRACE( 'PIP Window close')
		#self.mEventBus.Deregister( self )

		self.UpdatePropertyGUI( 'ShowFocusPIP', E_TAG_FALSE )

		if self.mPIP_EnableAudio :
			self.mDataCache.PIP_EnableAudio( False )

		if aStopPIP :
			ret = self.mDataCache.PIP_Stop( )
			if ret :
				self.mPIPStart = False
			LOG_TRACE( '---------pip stop ret[%s]'% ret )
			self.UpdatePropertyGUI( 'OpenPIP', E_TAG_FALSE )

		status = self.mDataCache.Player_GetStatus( )
		labelMode = GetStatusModeLabel( status.mMode )
		thread = threading.Timer( 0.1, AsyncShowStatus, [labelMode] )
		thread.start( )

		WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )
#		self.CloseDialog( )


	def GetPIPStatus( self ) :
		return self.mPIPStart


	def Load( self ) :
		self.ResetLabel( )

		ret = self.ChannelTuneToPIP( CURR_CHANNEL_PIP )
		if ret :
			self.LoadPositionPIP( )
			self.UpdatePropertyGUI( 'OpenPIP', E_TAG_TRUE )


	def LoadPositionPIP( self ) :
		posNotify = E_DEFAULT_POSITION_PIP
		try :
			posGet = GetSetting( 'PIP_POSITION' )
			LOG_TRACE( '----------------GetSetting posNotify[%s]'% posGet )

			posNotify = re.split( '\|', posGet )
			if not posNotify or len( posNotify ) != 4 :
				posNotify = E_DEFAULT_POSITION_PIP

			for i in range( len( posNotify ) ) :
				posNotify[i] = int( posNotify[i] )

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )
			posNotify = E_DEFAULT_POSITION_PIP

		self.SetPositionPIP( posNotify[0], posNotify[1], posNotify[2], posNotify[3] )


	def SetPositionPIP( self, aPosX = 827, aPosY = 125, aWidth = 352, aHeight = 188 ) :
		"""
		from pvr.GuiHelper import GetInstanceSkinPosition
		skinPos = GetInstanceSkinPosition( )
		skinPos.mZoom = 0
		x, y, w, h = skinPos.GetPipPosition2( aPosX, aPosY, aWidth, aHeight )
		"""
		x = aPosX
		y = aPosY
		w = aWidth
		h = aHeight

		self.mPosCurrent[0] = x
		self.mPosCurrent[1] = y
		self.mPosCurrent[2] = w
		self.mPosCurrent[3] = h

		self.mDataCache.PIP_SetDimension( self.mPosCurrent[0], self.mPosCurrent[1], self.mPosCurrent[2], self.mPosCurrent[3] )

		posNotify = '%s|%s|%s|%s'% ( self.mPosCurrent[0], self.mPosCurrent[1], self.mPosCurrent[2], self.mPosCurrent[3] )
		SetSetting( 'PIP_POSITION', posNotify )

		self.SetGUIToPIP( )


	def Channel_GetCurrentByPIP( self ) :
		LOG_TRACE( 'is PIPStarted[%s]'% self.mPIPStart )

		#1. tunable : last channel by pip
		pChNumber = self.mDataCache.PIP_GetCurrent( )
		LOG_TRACE( '1. tunable : last channel by pip, [%s]'% pChNumber )
		if not pChNumber or ( not self.mDataCache.PIP_IsPIPAvailable( pChNumber ) ) :
			pChNumber = None

			#3. tunable : current channel by main(tv only)
			if not pChNumber :
				iChannel = self.mDataCache.Channel_GetCurrent( )
				if iChannel :
					pChNumber = iChannel.mNumber
					if iChannel.mServiceType != ElisEnum.E_SERVICE_TYPE_TV :
						pChNumber = ElisPropertyInt( 'Last TV Number', self.mCommander ).GetProp( )

					if not self.mDataCache.PIP_IsPIPAvailable( pChNumber ) :
						pChNumber = None

					else :
						LOG_TRACE( '3. tunable : current channel by main(tv only), [%s]'% pChNumber )

			#2. tunable : find channel by tunableList of pip
			if not pChNumber :
				channelList = self.mDataCache.PIP_GetTunableList( )
				if channelList and len( channelList ) > 0 :
					for chNumber in channelList :
						if self.mDataCache.PIP_IsPIPAvailable( chNumber ) :
							pChNumber = chNumber
							LOG_TRACE( '2. tunable : find channel by tunableList of pip, [%s]'% pChNumber )
							break

			#4. tunable : find channel by channelList of main(tv only)
			if not pChNumber :
				channelList = self.mDataCache.Channel_GetList( )
				if self.mCurrentMode and self.mCurrentMode.mServiceType != ElisEnum.E_SERVICE_TYPE_TV :
					channelList = self.mDataCache.Channel_GetList( True, ElisEnum.E_SERVICE_TYPE_TV, ElisEnum.E_MODE_ALL, ElisEnum.E_SORT_BY_NUMBER )

				if channelList and len( channelList ) > 0 :
					for iChannel in channelList :
						if iChannel.mServiceType == ElisEnum.E_SERVICE_TYPE_TV and \
						   self.mDataCache.PIP_IsPIPAvailable( iChannel.mNumber ) :
							pChNumber = iChannel.mNumber
							LOG_TRACE( '4. tunable : find channel by channelList of main(tv only), [%s]'% pChNumber )
							break

		if not pChNumber :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			lblTitle = MR_LANG( 'Attention' )
			lblMsg = MR_LANG( 'Can not show PIP, Channel is empty' )
			dialog.SetDialogProperty( lblTitle, lblMsg )
			dialog.doModal( )

		return pChNumber


	def ChannelTuneToPIP( self, aDir ) :
		isBlank = E_TAG_TRUE
		fakeChannel = self.mCurrentChannel
		if not fakeChannel :
			fakeChannel = self.Channel_GetCurrentByPIP( )
			LOG_TRACE( '---------Channel_GetCurrentByPIP[%s]'% fakeChannel )

		if aDir == PREV_CHANNEL_PIP :
			if fakeChannel :
				fakeChannel = self.mDataCache.PIP_GetPrevAvailable( 1 )

		elif aDir == NEXT_CHANNEL_PIP :
			if fakeChannel :
				fakeChannel = self.mDataCache.PIP_GetNextAvailable( 1 )

		elif aDir == SWITCH_CHANNEL_PIP :
			if self.mCurrentMode and self.mCurrentMode.mServiceType != ElisEnum.E_SERVICE_TYPE_TV :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				lblTitle = MR_LANG( 'Attention' )
				lblMsg = MR_LANG( 'Can not switch PIP, Current mode Radio' )
				dialog.SetDialogProperty( lblTitle, lblMsg )
				dialog.doModal( )
				return
			
			iChannel = self.mDataCache.Channel_GetCurrent( )
			if fakeChannel and iChannel :
				ret = self.mDataCache.Channel_SetCurrentSync( fakeChannel, ElisEnum.E_SERVICE_TYPE_TV )
				if not ret :
					LOG_TRACE( 'Fail to switch' )
					return
				fakeChannel = iChannel.mNumber


		elif aDir == CURR_CHANNEL_PIP :
			if self.mPIPStart :
				LOG_TRACE( '--------Already started PIP' )
				self.UpdatePropertyGUI( 'BlankPIP', E_TAG_FALSE )
				return False

			if not fakeChannel :
				self.Close( )
				return False


		LOG_TRACE( '---------up/down[%s] fakeChannel[%s] current[%s]'% ( aDir, fakeChannel, self.mCurrentChannel ) )
		if fakeChannel :
			#find iChannel in channelList(tv only)
			iChannel = self.mDataCache.Channel_GetByNumber( fakeChannel )
			if self.mCurrentMode and self.mCurrentMode.mServiceType != ElisEnum.E_SERVICE_TYPE_TV :
				iChannel = self.mDataCache.Channel_GetByNumber( fakeChannel, True )

			pChNumber = fakeChannel
			if iChannel :
				ret = self.mDataCache.PIP_Start( fakeChannel )
				LOG_TRACE( '---------pip start ret[%s] ch[%s]'% ( ret, fakeChannel ) )
				if ret :
					isBlank = E_TAG_FALSE
					self.mPIPStart = True
					self.mCurrentChannel = fakeChannel

				pChNumber = iChannel.mNumber
				if E_V1_2_APPLY_PRESENTATION_NUMBER :
					pChNumber = self.mDataCache.CheckPresentationNumber( iChannel )

				label = '%s - %s'% ( EnumToString( 'type', ElisEnum.E_SERVICE_TYPE_TV ).upper(), iChannel.mName )
				#label = '%s - %s'% ( pChNumber, iChannel.mName )
				self.mCtrlLabelChannel.setLabel( label )

			self.UpdatePropertyGUI( 'ShowPIPChannelNumber', '%s'% pChNumber ) 

		self.UpdatePropertyGUI( 'BlankPIP', isBlank )
		return True


	def ResetLabel( self ) :
		self.UpdatePropertyGUI( 'SetContextAction', '' )
		self.UpdatePropertyGUI( 'SettingPIP', E_TAG_FALSE )
		time.sleep( 0.2 )
		self.setFocusId( CTRL_ID_GROUP_LIST_PIP )


	def UpdatePropertyGUI( self, aPropertyID = None, aValue = None ) :
		#LOG_TRACE( 'Enter property[%s] value[%s]'% (aPropertyID, aValue) )
		if aPropertyID == None :
			return False

		self.setProperty( aPropertyID, aValue )
		if aPropertyID == 'SettingPIP' and aValue == E_TAG_TRUE :
			lbltxt = ''
			if self.mViewMode == CONTEXT_ACTION_MOVE_PIP :
				lbltxt = MR_LANG( 'Set move to PIP' )
			elif self.mViewMode == CONTEXT_ACTION_SIZE_PIP :
				lbltxt = MR_LANG( 'Set size to PIP' )

			self.setProperty( 'SetContextAction', lbltxt )
			self.SetGUIArrow( True )


	def ShowContextMenu( self ) :
		context = []
		context.append( ContextItem( MR_LANG( 'Set move to PIP' ), CONTEXT_ACTION_MOVE_PIP ) )
		context.append( ContextItem( MR_LANG( 'Set size to PIP' ), CONTEXT_ACTION_SIZE_PIP ) )
		context.append( ContextItem( MR_LANG( 'Active screen to PIP' ), CONTEXT_ACTION_ACTIVE_PIP ) )
		context.append( ContextItem( MR_LANG( 'Load to Default' ), CONTEXT_ACTION_DEFAULT_PIP ) )
		context.append( ContextItem( MR_LANG( 'Stop PIP' ), CONTEXT_ACTION_STOP_PIP ) )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
 		dialog.doModal( )

		selectedAction = dialog.GetSelectedAction( )
		if selectedAction == -1 :
			#LOG_TRACE( 'CANCEL by context dialog' )
			return

		self.DoContextAction( selectedAction )


	def DoContextAction( self, aAction ) :
		self.mViewMode = aAction
		if aAction == CONTEXT_ACTION_MOVE_PIP :
			self.UpdatePropertyGUI( 'SettingPIP', E_TAG_TRUE ) 

		elif aAction == CONTEXT_ACTION_SIZE_PIP :
			self.UpdatePropertyGUI( 'SettingPIP', E_TAG_TRUE ) 

		elif aAction == CONTEXT_ACTION_ACTIVE_PIP :
			pass

		elif aAction == CONTEXT_ACTION_DEFAULT_PIP :
			self.mViewMode = CONTEXT_ACTION_DONE_PIP
			self.SetPositionPIP( )
			self.setFocusId( CTRL_ID_GROUP_LIST_PIP )

		elif aAction == CONTEXT_ACTION_STOP_PIP :
			self.mViewMode = CONTEXT_ACTION_DONE_PIP
			self.Close( )


	def DoSettingToPIP( self, aAction ) :
		ret = False
		if self.mViewMode == CONTEXT_ACTION_DONE_PIP :
			return ret

		elif self.mViewMode == CONTEXT_ACTION_ACTIVE_PIP :
			#ToDO
			return ret

		ret = True
		pipX, pipY, pipW, pipH = ( 0, 0, 0, 0 )
		if aAction == Action.ACTION_MOVE_LEFT :
			if self.mViewMode == CONTEXT_ACTION_MOVE_PIP : 
				pipX -= E_POSX_ABILITY
			elif self.mViewMode == CONTEXT_ACTION_SIZE_PIP : 
				pipW -= E_WIDTH_ABILITY

		elif aAction == Action.ACTION_MOVE_RIGHT :
			if self.mViewMode == CONTEXT_ACTION_MOVE_PIP : 
				pipX += E_POSX_ABILITY
			elif self.mViewMode == CONTEXT_ACTION_SIZE_PIP : 
				pipW += E_WIDTH_ABILITY

		elif aAction == Action.ACTION_MOVE_UP :
			if self.mViewMode == CONTEXT_ACTION_MOVE_PIP : 
				pipY -= E_POSY_ABILITY
			elif self.mViewMode == CONTEXT_ACTION_SIZE_PIP : 
				pipH -= E_HEIGHT_ABILITY

		elif aAction == Action.ACTION_MOVE_DOWN :
			if self.mViewMode == CONTEXT_ACTION_MOVE_PIP : 
				pipY += E_POSY_ABILITY
			elif self.mViewMode == CONTEXT_ACTION_SIZE_PIP : 
				pipH += E_HEIGHT_ABILITY

		posx  = self.mPosCurrent[0] + pipX
		posy  = self.mPosCurrent[1] + pipY
		width = self.mPosCurrent[2] + pipW
		height= self.mPosCurrent[3] + pipH
		LOG_TRACE( 'set posX[%s] posY[%s] width[%s] height[%s]'% ( posx, posy, width, height ) )

		#limit
		if posx < 0 or ( posx + width ) > 1280 or \
		   posy < 0 or ( posy + height) > 600 or \
		   width < ( E_DEFAULT_POSITION_PIP[2] / 2 ) or width > 1280 or \
		   height < ( E_DEFAULT_POSITION_PIP[3] / 2 ) or height > 600 :
			LOG_TRACE( '----------limit False' )
			return ret

		self.SetPositionPIP( posx, posy, width, height )
		return ret


	def SetGUIToPIP( self ) :
		x = self.mPosCurrent[0] - 16
		y = self.mPosCurrent[1] - 35
		w = self.mPosCurrent[2] + 60
		h = self.mPosCurrent[3] + 55

		#ch name
		self.mCtrlLabelChannel.setWidth( w )

		#pip panel
		self.mCtrlGroupPIP.setPosition( x, y )

		self.mCtrlGroupPIP.setWidth( w )
		self.mCtrlGroupPIP.setHeight( h )

		#self.mCtrlImageBlank.setWidth( w )
		#self.mCtrlImageBlank.setHeight( h )

		self.mCtrlImageFocusNF.setWidth( w - 42 )
		self.mCtrlImageFocusNF.setHeight( h - 20 )

		self.mCtrlImageFocusFO.setWidth( w )
		self.mCtrlImageFocusFO.setHeight( h )

		#osd panel
		self.mCtrlGroupOsdStatus.setPosition( 20, h - 20 )
		if w > 330 :
			self.mCtrlImageOsdStatus.setWidth( w - 42 )

		self.SetGUIArrow( )


	def SetGUIArrow( self, aInit = False ) :
		#arrow at move, size

		x = self.mPosCurrent[0]
		y = self.mPosCurrent[1]
		w = self.mPosCurrent[2]
		h = self.mPosCurrent[3]
		#LOG_TRACE( '------------x[%s] y[%s] w[%s] h[%s] w/2[%s] h/2[%s]'% ( x,y, w, h, w/2, h/2 ) )

		if not aInit and self.mViewMode != CONTEXT_ACTION_SIZE_PIP : 
			return

		self.mCtrlImageArrowLeft.setPosition  ( 0,      int( h / 2 ) )
		self.mCtrlImageArrowRight.setPosition ( 40 + w, int( h / 2 ) )

		self.mCtrlImageArrowTop.setPosition   ( 20 + int( w / 2 ), -20 )
		self.mCtrlImageArrowBottom.setPosition( 20 + int( w / 2 ), 20 + h )


	def SetAudioPIP( self ) :
		isMainAudioBlock = False
		#1. check audio in main
		mute, volume = self.GetAudioStatus( )

		if mute or volume < 1 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			lblTitle = MR_LANG( 'Attention' )
			lblMsg = MR_LANG( 'Can not enable audio, Check main audio' )
			dialog.SetDialogProperty( lblTitle, lblMsg )
			dialog.doModal( )
			return

		isEnable = not self.mPIP_EnableAudio
		ret = self.mDataCache.PIP_EnableAudio( isEnable )
		if ret :
			self.mPIP_EnableAudio = isEnable


