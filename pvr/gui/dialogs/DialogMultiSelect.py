from pvr.gui.WindowImport import *
import time

E_MODE_DEFAULT_LIST = 0
E_MODE_CHANNEL_LIST = 1

E_SELECT_ONLY  = 0
E_SELECT_MULTI = 1

E_CONTROL_ID_LIST = E_BASE_WINDOW_ID + 3950

DIALOG_BUTTON_CLOSE_ID = 3901
DIALOG_HEADER_LABEL_ID = 3902
DIALOG_LABEL_POS_ID = 3903
DIALOG_BUTTON_OK_ID = 3904


class DialogMultiSelect( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )	
		self.mIsOk = None
		self.mCtrlList = None
		self.mListItems = None
		self.mDefaultList = []
		self.mTitle = ''
		self.mMode = E_MODE_DEFAULT_LIST
		self.mIsMulti = E_SELECT_MULTI
		self.mPreviousBlocking = False
		self.mAsyncTimer = None

	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.setProperty( 'DialogDrawFinished', 'False' )

		self.mMarkList = []
		self.mLastSelected = -1
		self.mCtrlList = self.getControl( E_CONTROL_ID_LIST )
		self.mCtrlPos =  self.getControl( DIALOG_LABEL_POS_ID )

		self.InitList( )
		self.mEventBus.Register( self )
		self.SetFocusList( E_CONTROL_ID_LIST )

		self.setProperty( 'DialogDrawFinished', 'True' )
		self.RestartAsyncBlockTimer( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.mIsOk = actionId
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.mLastSelected = -1
			if self.mPreviousBlocking and actionId == Action.ACTION_PARENT_DIR :
				return

			self.Close( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN or \
			 actionId == Action.ACTION_PAGE_UP or actionId == Action.ACTION_PAGE_DOWN :
			idx = self.mCtrlList.getSelectedPosition( )
			self.mCtrlPos.setLabel( '%s'% ( idx + 1 ) )

		elif actionId == Action.ACTION_STOP :
			self.mLastSelected = -1
			self.mMarkList = []
			self.Close( )

		elif actionId == Action.ACTION_PLAYER_PLAY or actionId == Action.ACTION_PAUSE :
			self.mLastSelected = -1
			self.mMarkList = []
			self.Close( )

		self.mPreviousBlocking = False


	def onClick( self, aControlId ) :
		if aControlId == DIALOG_BUTTON_CLOSE_ID :
			self.mLastSelected = -1
			self.mMarkList = []
			self.Close( )

		elif aControlId == E_CONTROL_ID_LIST :
			self.SetMarkupGUI( )
			if self.mIsMulti == E_SELECT_ONLY :
				self.Close( )

		elif aControlId == DIALOG_BUTTON_OK_ID :
			if not self.mMarkList or len( self.mMarkList ) < 1 :
				self.SetMarkupGUI( )
			self.Close( )


	def onFocus( self, aControlId ) :
		pass


	def SetFocusList( self, aControlId ) :
		self.setFocusId( aControlId )


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowDialogId( ) :
			if aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or \
			   aEvent.getName( ) == ElisEventRecordingStopped.getName( ) or \
			   aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
				xbmc.executebuiltin('xbmc.Action(stop)')


	def InitList( self ) :
		self.mCtrlList.reset( )
		self.mListItems = []

		self.getControl( DIALOG_HEADER_LABEL_ID ).setLabel( self.mTitle )

		if not self.mDefaultList or len( self.mDefaultList ) < 1 :
			return

		if self.mMode == E_MODE_CHANNEL_LIST :
			self.ChannelItems( )
		else :
			self.ListItems( )

		self.mCtrlList.addItems( self.mListItems )
		idx = self.mCtrlList.getSelectedPosition( )
		self.mCtrlPos.setLabel( '%s'% ( idx + 1 ) )


	def ListItems( self ) :
		for item in self.mDefaultList :
			listItem = xbmcgui.ListItem( '', '%s'% item )
			self.mListItems.append( listItem )


	def ChannelItems( self ) :
		for iChannel in self.mDefaultList :
			#isAvailable check, if channelList then all view
			if WinMgr.GetInstance( ).GetLastWindowID( ) != WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
				if self.mDataCache.Channel_GetCurr( iChannel.mNumber ) == None :
					continue

			hdLabel = ''
			if iChannel.mIsHD :
				hdLabel = E_TAG_COLOR_HD_LABEL
			listItem = xbmcgui.ListItem( '%04d'% iChannel.mNumber, '%s %s'% ( iChannel.mName, hdLabel ) )
			if len( iChannel.mName ) > 30 :
				listItem.setLabel2( '%s'% iChannel.mName )
				listItem.setProperty( 'iHDLabel', E_TAG_COLOR_HD_LABEL )

			if iChannel.mLocked : 
				listItem.setProperty( E_XML_PROPERTY_LOCK, E_TAG_TRUE )
			if iChannel.mIsCA : 
				listItem.setProperty( E_XML_PROPERTY_CAS,  E_TAG_TRUE )
			if iChannel.mSkipped : 
				listItem.setProperty( E_XML_PROPERTY_SKIP, E_TAG_TRUE )
			if iChannel.mIsHD and E_V1_1_HD_ICON_USE :
				listItem.setProperty( E_XML_PROPERTY_IHD, E_TAG_TRUE )

			self.mListItems.append( listItem )


	def SetMarkupGUI( self ) :
		idx = 0
		isExist = False

		if self.mDefaultList == None or len( self.mDefaultList ) < 1 or \
		   self.mCtrlList == None or self.mListItems == None or len( self.mListItems ) < 1 :
			return

		aPos = self.mCtrlList.getSelectedPosition( )
		self.mLastSelected = aPos

		#aready mark is mark delete
		for i in self.mMarkList :
			if i == aPos :
				self.mMarkList.pop( idx )
				isExist = True
			idx += 1

		#do not exist is append mark
		if isExist == False : 
			self.mMarkList.append( aPos )

		listItem = self.mCtrlList.getListItem( aPos )

		#mark toggle: disable/enable
		if listItem.getProperty( E_XML_PROPERTY_MARK ) == E_TAG_TRUE : 
			listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_FALSE )
		else :
			listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_TRUE )

		self.mCtrlList.selectItem( aPos + 1 )
		time.sleep( 0.05 )

		aPos = self.mCtrlList.getSelectedPosition( )
		self.mCtrlPos.setLabel( '%s'% ( aPos + 1 ) )


	def SetPreviousBlocking( self, aPreviousBlocking = False ) :
		self.mPreviousBlocking = aPreviousBlocking


	def SetDefaultProperty( self, aTitle = 'SELECT', aList = None, aMode = E_MODE_DEFAULT_LIST, aIsMulti = E_SELECT_MULTI ) :
		self.mTitle = aTitle
		self.mDefaultList = aList
		self.mMode = aMode
		self.mIsMulti = aIsMulti


	def GetSelectedList( self ) :
		if self.mIsMulti == E_SELECT_ONLY :
			return self.mLastSelected

		return self.mMarkList


	def GetCloseStatus( self ) :
		return self.mIsOk


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.StopAsyncBlockTimer( )
		self.CloseDialog( )


	def RestartAsyncBlockTimer( self ) :
		self.StopAsyncBlockTimer( )
		self.StartAsyncBlockTimer( )


	def StartAsyncBlockTimer( self ) :
		self.mAsyncTimer = threading.Timer( 2, self.InitPreviousBlocking )
		self.mAsyncTimer.start( )


	def StopAsyncBlockTimer( self ) :
		if self.mAsyncTimer	and self.mAsyncTimer.isAlive( ) :
			self.mAsyncTimer.cancel( )
			del self.mAsyncTimer

		self.mAsyncTimer  = None


	def InitPreviousBlocking( self ) :
		self.mPreviousBlocking = False

