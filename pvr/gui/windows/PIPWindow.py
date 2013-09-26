from pvr.gui.WindowImport import *
import traceback

E_PIP_WINDOW_BASE_ID		=  WinMgr.WIN_ID_PIP_WINDOW * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID
CTRL_ID_BUTTON_SETTING_PIP	= E_PIP_WINDOW_BASE_ID + 0001

CTRL_ID_GROUP_PIP			= E_PIP_WINDOW_BASE_ID + 1000
#CTRL_ID_IMAGE_NFOCUSED		= E_PIP_WINDOW_BASE_ID + 1001
CTRL_ID_IMAGE_FOCUSED		= E_PIP_WINDOW_BASE_ID + 1002
#CTRL_ID_LABEL_LOCK			= E_PIP_WINDOW_BASE_ID + 1004

CTRL_ID_GROUP_OSD_STATUS	= E_PIP_WINDOW_BASE_ID + 2000
CTRL_ID_IMAGE_OSD_STATUS	= E_PIP_WINDOW_BASE_ID + 2002
CTRL_ID_LABEL_CHANNEL		= E_PIP_WINDOW_BASE_ID + 2001

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

CTRL_ID_GROUP_BASE_PIP		= E_BASE_WINDOW_ID + 8899
CTRL_ID_IMAGE_BASE_PIP		= E_BASE_WINDOW_ID + 2001
CTRL_ID_IMAGE_NFOCUSED		= E_BASE_WINDOW_ID + 2002
CTRL_ID_LABEL_LOCK			= E_BASE_WINDOW_ID + 2004
CTRL_ID_LABEL_SCRAMBLE		= E_BASE_WINDOW_ID + 2005
CTRL_ID_LABEL_NOSIGNAL		= E_BASE_WINDOW_ID + 2006

E_DEFAULT_POSITION_PIP		= [827,125,352,188]#[857,170,352,198] 
CONTEXT_ACTION_DONE_PIP		= 0
CONTEXT_ACTION_MOVE_PIP		= 1
CONTEXT_ACTION_SIZE_PIP		= 2
CONTEXT_ACTION_SWITCH_PIP	= 3
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

PIP_CHECKWINDOW = [
	WinMgr.WIN_ID_NULLWINDOW,
	WinMgr.WIN_ID_MAINMENU,
	WinMgr.WIN_ID_TIMESHIFT_PLATE,
	WinMgr.WIN_ID_LIVE_PLATE
]


class PIPWindow( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mPIPStart = False
		self.mCurrentChannel = ElisIChannel( )
		self.mCurrentChannel.mNumber = self.mDataCache.PIP_GetCurrent( )
		self.mCurrentChannel.mError = -1


	def onInit( self ) :
		self.SetActivate( True )
		self.SetFrontdisplayMessage( MR_LANG('PIP Channel') )
		self.mWinId = xbmcgui.getCurrentWindowId( )

		#self.SetSingleWindowPosition( E_PIP_WINDOW_BASE_ID )
		#self.SetRadioScreen( )

		self.mCtrlGroupPIP         = self.getControl( CTRL_ID_GROUP_PIP )
		self.mCtrlLabelChannel     = self.getControl( CTRL_ID_LABEL_CHANNEL )
		self.mCtrlImageFocusNF     = self.getControl( CTRL_ID_IMAGE_NFOCUSED )
		self.mCtrlImageFocusFO     = self.getControl( CTRL_ID_IMAGE_FOCUSED )
		self.mCtrlImageArrowLeft   = self.getControl( CTRL_ID_IMAGE_ARROW_LEFT )
		self.mCtrlImageArrowRight  = self.getControl( CTRL_ID_IMAGE_ARROW_RIGHT )
		self.mCtrlImageArrowTop    = self.getControl( CTRL_ID_IMAGE_ARROW_TOP )
		self.mCtrlImageArrowBottom = self.getControl( CTRL_ID_IMAGE_ARROW_BOTTOM )
		self.mCtrlGroupOsdStatus   = self.getControl( CTRL_ID_GROUP_OSD_STATUS )
		self.mCtrlImageOsdStatus   = self.getControl( CTRL_ID_IMAGE_OSD_STATUS )
		self.mCtrlGroupBasePIP     = self.getControl( CTRL_ID_GROUP_BASE_PIP )
		self.mCtrlImageBasePIP     = self.getControl( CTRL_ID_IMAGE_BASE_PIP )
		self.mCtrlLabelLock        = self.getControl( CTRL_ID_LABEL_LOCK )
		self.mCtrlLabelScramble    = self.getControl( CTRL_ID_LABEL_SCRAMBLE )
		self.mCtrlLabelNoSignal    = self.getControl( CTRL_ID_LABEL_NOSIGNAL )

		self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( )

		self.mChannelList = []
		self.mChannelListHash = {}
		self.mTunableList = []
		self.mViewMode = CONTEXT_ACTION_DONE_PIP
		self.mPosCurrent = deepcopy( E_DEFAULT_POSITION_PIP )
		self.mPIP_EnableAudio = False
		self.mAsyncTuneTimer = None
		self.mIndexAvail = 0
		self.mFakeChannel = self.mCurrentChannel
	
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
	
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		#self.GetFocusId( )
		#LOG_TRACE('onAction[%d] viewMode[%s] focus[%s]'% ( actionId, self.mViewMode, self.mFocusId ) )

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			if self.mViewMode > CONTEXT_ACTION_DONE_PIP :
				self.mViewMode = CONTEXT_ACTION_DONE_PIP
				self.ResetLabel( ) 
				return

			self.Close( False )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.DoSettingToPIP( actionId )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.DoSettingToPIP( actionId )

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN :
			self.DoSettingToPIP( actionId )

		elif actionId == Action.ACTION_PAGE_UP :
			self.ChannelTuneToPIP( NEXT_CHANNEL_PIP )

		elif actionId == Action.ACTION_PAGE_DOWN :
			self.ChannelTuneToPIP( PREV_CHANNEL_PIP )

		elif actionId == Action.ACTION_MBOX_TVRADIO :
			LOG_TRACE( 'Not supported Radio' )
			return

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		else :
			self.NotAvailAction( )
			LOG_TRACE( 'unknown key[%s]'% actionId )

#		elif actionId == Action.ACTION_CONTEXT_MENU :
#			if self.mViewMode == CONTEXT_ACTION_DONE_PIP :
#				self.ShowContextMenu( )


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
		if self.IsActivate( ) == False  :
			return


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			LOG_TRACE( '--------------------PIP onEvent[%s]'% aEvent.getName( ) )
			if aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
				#if self.mIsUpdateEnable == True	:
				LOG_TRACE( 'record start/stop event' )
				#ToDO


	def Close( self, aStopPIP = True ) :
		LOG_TRACE( 'PIP Window close')
		#self.mEventBus.Deregister( self )

		self.setFocusId( CTRL_ID_BUTTON_NEXT_PIP )
		self.UpdatePropertyGUI( 'ShowFocusPIP', E_TAG_FALSE )

		if self.mPIP_EnableAudio :
			self.mDataCache.PIP_EnableAudio( False )

		if aStopPIP :
			self.PIP_Stop( )

		if self.mAsyncTuneTimer	and self.mAsyncTuneTimer.isAlive( ) :
			self.mAsyncTuneTimer.join( )

		status = self.mDataCache.Player_GetStatus( )
		labelMode = GetStatusModeLabel( status.mMode )
		thread = threading.Timer( 0.1, AsyncShowStatus, [labelMode] )
		thread.start( )

		WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )


	def PIP_Stop( self ) :
		ret = self.mDataCache.PIP_Stop( )
		LOG_TRACE( '---------PIP_Stop ret[%s]'% ret )
		if ret :
			self.mPIPStart = False
			self.UpdatePropertyGUI( 'OpenPIP', E_TAG_FALSE )
			self.UpdatePropertyGUI( 'iLockPIP', E_TAG_FALSE )
			self.UpdatePropertyGUI( 'BlankPIP', E_TAG_FALSE )


	def PIP_Check( self, aStop = False ) :
		if not E_V1_2_APPLY_PIP :
			return

		if aStop or self.mDataCache.GetMediaCenter( ) :
			self.PIP_Stop( )
			return

		if self.GetPIPStatus( ) :
			isShow = False
			if WinMgr.GetInstance( ).GetLastWindowID( ) in PIP_CHECKWINDOW :
				isShow = True

			ret = self.mDataCache.PIP_AVBlank( not isShow )
			self.UpdatePropertyGUI( 'OpenPIP', '%s'% isShow )
			self.UpdatePropertyGUI( 'ShowNamePIP', '%s'% ( not isShow ) )
			LOG_TRACE( 'GetLastWindowID[%s] PIPShow[%s]'% ( WinMgr.GetInstance( ).GetLastWindowID( ), isShow ) )

		LOG_TRACE( 'mPIPStart[%s] OpenPIP[%s]'% ( self.mPIPStart, self.getProperty( 'OpenPIP' ) ) )


	def GetPIPStatus( self ) :
		return self.mPIPStart


	def Load( self ) :
		self.ResetLabel( )

		"""
		self.mIndexLimit = 1
		numList = self.mDataCache.PIP_GetTunableList( )
		if numList and len( numList ) > 0 :
			self.mIndexLimit = len( numList )
		"""

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
		self.mPosCurrent[0] = aPosX
		self.mPosCurrent[1] = aPosY
		self.mPosCurrent[2] = aWidth
		self.mPosCurrent[3] = aHeight

		from pvr.GuiHelper import GetInstanceSkinPosition
		skinPos = GetInstanceSkinPosition( )
		x, y, w, h = skinPos.GetPipPosition2( aPosX, aPosY, aWidth, aHeight )

		self.mDataCache.PIP_SetDimension( x, y, w, h )

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
		fakeChannel = self.mCurrentChannel
		self.UpdatePropertyGUI( 'BlankPIP', E_TAG_TRUE )

		if not fakeChannel or fakeChannel.mError != 0 or fakeChannel.mNumber == 0 :
			chNumber = self.Channel_GetCurrentByPIP( )
			fakeChannel = self.mDataCache.PIP_GetByNumber( chNumber )
			if fakeChannel :
				LOG_TRACE( '---load------Channel_GetCurrentByPIP[%s %s]'% ( fakeChannel.mNumber, fakeChannel.mName ) )

		if aDir == PREV_CHANNEL_PIP :
			fakeChannel = self.mDataCache.PIP_GetPrev( self.mFakeChannel )
			#self.mIndexAvail += 1
			#fakeChannel = self.mDataCache.PIP_GetPrevAvailable( ( self.mIndexAvail % self.mIndexLimit ) )

		elif aDir == NEXT_CHANNEL_PIP :
			fakeChannel = self.mDataCache.PIP_GetNext( self.mFakeChannel )
			#self.mIndexAvail += 1
			#fakeChannel = self.mDataCache.PIP_GetNextAvailable( ( self.mIndexAvail % self.mIndexLimit ) )

		elif aDir == SWITCH_CHANNEL_PIP :
			if self.mCurrentMode and self.mCurrentMode.mServiceType != ElisEnum.E_SERVICE_TYPE_TV :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				lblTitle = MR_LANG( 'Attention' )
				lblMsg = MR_LANG( 'Can not switch PIP, Current mode Radio' )
				dialog.SetDialogProperty( lblTitle, lblMsg )
				dialog.doModal( )
				if self.mCurrentChannel and ( not self.mCurrentChannel.mLocked ) :
					self.UpdatePropertyGUI( 'BlankPIP', E_TAG_FALSE )
				return

			iChannel = self.mDataCache.Channel_GetCurrent( )
			if fakeChannel and iChannel :
				ret = self.mDataCache.Channel_SetCurrentSync( fakeChannel.mNumber, ElisEnum.E_SERVICE_TYPE_TV )
				if not ret :
					LOG_TRACE( 'Fail to switch' )
					if self.mCurrentChannel and ( not self.mCurrentChannel.mLocked ) and \
					   self.getProperty( 'PIPSignal' ) == E_TAG_TRUE :
						self.UpdatePropertyGUI( 'BlankPIP', E_TAG_FALSE )
					return

				fakeChannel = iChannel

		elif aDir == CURR_CHANNEL_PIP :
			if self.mPIPStart :
				LOG_TRACE( '--------Already started PIP' )
				self.mDataCache.PIP_AVBlank( False )

				if self.mCurrentChannel and ( not self.mCurrentChannel.mLocked ) and \
				   self.getProperty( 'PIPSignal' ) == E_TAG_TRUE :
					self.UpdatePropertyGUI( 'BlankPIP', E_TAG_FALSE )

				return True

			if not fakeChannel :
				self.Close( )
				lblTitle = MR_LANG( 'Attention' )
				lblMsg = MR_LANG( 'Can not open PIP, Tunable not found' )
				dialog.SetDialogProperty( lblTitle, lblMsg )
				dialog.doModal( )
				return False

		LOG_TRACE( '---------up/down[%s] fakeChannel[%s] current[%s %s]'% ( aDir, fakeChannel, self.mCurrentChannel.mNumber, self.mCurrentChannel.mName ) )
		if fakeChannel :
			LOG_TRACE('----------fakeChannel[%s %s]'% ( fakeChannel.mNumber, fakeChannel.mName ) )
			label = 'PIP - %s'% fakeChannel.mName
			self.mCtrlLabelChannel.setLabel( label )

			pChNumber = fakeChannel.mNumber
			if E_V1_2_APPLY_PRESENTATION_NUMBER :
				pChNumber = self.mDataCache.CheckPresentationNumber( fakeChannel )

			self.UpdatePropertyGUI( 'ShowPIPChannelNumber', '%s'% pChNumber ) 

			self.mFakeChannel = fakeChannel
			self.RestartAsyncTune( )

		return True


	def ResetLabel( self ) :
		self.UpdatePropertyGUI( 'SetContextAction', '' )
		self.UpdatePropertyGUI( 'SettingPIP', E_TAG_FALSE )
		self.UpdatePropertyGUI( 'ShowOSDStatus', E_TAG_TRUE )
		self.UpdatePropertyGUI( 'ShowNamePIP', E_TAG_TRUE )

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

			self.setProperty( 'ShowOSDStatus', E_TAG_FALSE )
			self.setProperty( 'SetContextAction', lbltxt )
			self.SetGUIArrow( True )


	def ShowContextMenu( self ) :
		context = []
		context.append( ContextItem( MR_LANG( 'Set move to PIP' ), CONTEXT_ACTION_MOVE_PIP ) )
		context.append( ContextItem( MR_LANG( 'Set size to PIP' ), CONTEXT_ACTION_SIZE_PIP ) )
		context.append( ContextItem( MR_LANG( 'Active screen to PIP' ), CONTEXT_ACTION_SWITCH_PIP ) )
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

		elif aAction == CONTEXT_ACTION_SWITCH_PIP :
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

		elif self.mViewMode == CONTEXT_ACTION_SWITCH_PIP :
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
		x = self.mPosCurrent[0]
		y = self.mPosCurrent[1]
		w = self.mPosCurrent[2]# + 10
		h = self.mPosCurrent[3]# + 10

		#ch name
		self.mCtrlLabelChannel.setWidth( w )

		#pip panel
		self.mCtrlGroupPIP.setPosition( x, y )

		self.mCtrlGroupPIP.setWidth( w )
		self.mCtrlGroupPIP.setHeight( h )

		self.mCtrlImageFocusFO.setWidth( w )
		self.mCtrlImageFocusFO.setHeight( h )

		#base overlay for radio mode
		bh = h - 10
		bw = w - 10
		self.mCtrlGroupBasePIP.setPosition( x, y )
		self.mCtrlImageBasePIP.setWidth( bw )
		self.mCtrlImageBasePIP.setHeight( bh )
		self.mCtrlLabelLock.setWidth( bw )
		self.mCtrlLabelLock.setPosition( 0, int( ( bh - 10 ) / 2 ) )
		self.mCtrlLabelScramble.setWidth( bw )
		self.mCtrlLabelScramble.setPosition( 0, int( ( bh - 10 ) / 2 ) )
		self.mCtrlLabelNoSignal.setWidth( bw )
		self.mCtrlLabelNoSignal.setPosition( 0, int( ( bh - 10 ) / 2 ) )

		self.mCtrlLabelChannel.setPosition( 5, bh - 25 )

		self.mCtrlImageFocusNF.setWidth( bw )
		self.mCtrlImageFocusNF.setHeight( bh )


		#osd panel
		self.mCtrlGroupOsdStatus.setPosition( 0, h )
		if w > 330 :
			self.mCtrlImageOsdStatus.setWidth( w )

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

		self.mCtrlImageArrowLeft.setPosition  ( 0, int( h / 2 ) )
		self.mCtrlImageArrowRight.setPosition ( w, int( h / 2 ) )

		self.mCtrlImageArrowTop.setPosition   ( int( w / 2 ), 0 )
		self.mCtrlImageArrowBottom.setPosition( int( w / 2 ), h )


	def SetAudioPIP( self, aForce = False, aEnable = False ) :
		if aForce :
			ret = self.mDataCache.PIP_EnableAudio( aEnable )
			if ret :
				self.mPIP_EnableAudio = aEnable

			return

		lblMsg = ''
		isAudioBlock = False

		if self.mCurrentChannel and self.mCurrentChannel.mLocked :
			isAudioBlock = True
			lblMsg = MR_LANG( 'Can not enable audio, Channel is locked' )

		#1. check audio in main
		mute, volume = self.GetAudioStatus( )

		if mute or volume < 1 :
			isAudioBlock = True
			lblMsg = MR_LANG( 'Can not enable audio, Check main audio' )

		if isAudioBlock :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			lblTitle = MR_LANG( 'Attention' )
			dialog.SetDialogProperty( lblTitle, lblMsg )
			dialog.doModal( )
			return

		isEnable = not self.mPIP_EnableAudio
		ret = self.mDataCache.PIP_EnableAudio( isEnable )
		if ret :
			self.mPIP_EnableAudio = isEnable


	def RestartAsyncTune( self ) :
		self.StopAsyncTune( )
		self.StartAsyncTune( )


	def StartAsyncTune( self ) :
		self.mAsyncTuneTimer = threading.Timer( 0.5, self.TuneChannel )
		self.mAsyncTuneTimer.start( )


	def StopAsyncTune( self ) :
		if self.mAsyncTuneTimer	and self.mAsyncTuneTimer.isAlive( ) :
			self.mAsyncTuneTimer.cancel( )
			del self.mAsyncTuneTimer

		self.mAsyncTuneTimer = None


	def TuneChannel( self ) :
		try :
			self.mIndexAvail = 0
			self.mCurrentChannel = self.mFakeChannel
			ret = self.mDataCache.PIP_Start( self.mFakeChannel.mNumber )
			LOG_TRACE( '---------pip start ret[%s] ch[%s]'% ( ret, self.mFakeChannel ) )
			if ret :
				self.mPIPStart = True
				if self.mFakeChannel.mLocked :
					self.SetAudioPIP( True, False )
					self.UpdatePropertyGUI( 'iLockPIP', E_TAG_TRUE )
				else :
					self.UpdatePropertyGUI( 'iLockPIP', E_TAG_FALSE )
					self.UpdatePropertyGUI( 'BlankPIP', E_TAG_FALSE )
					self.UpdatePropertyGUI( 'PIPSignal', E_TAG_TRUE )

			else :
				LOG_ERR('Tune failed')
				self.UpdatePropertyGUI( 'iLockPIP', E_TAG_FALSE )
				self.UpdatePropertyGUI( 'PIPSignal', E_TAG_FALSE )
			
		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

