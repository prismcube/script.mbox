from pvr.gui.WindowImport import *
import time

E_CONTROL_ID_LIST = E_BASE_WINDOW_ID + 3950
E_CONTROL_ID_LIST2 = E_BASE_WINDOW_ID + 3960

DIALOG_BUTTON_CLOSE_ID = 3901
DIALOG_HEADER_LABEL_ID = 3902
DIALOG_LABEL_POS_ID = 3903
DIALOG_BUTTON_OK_ID = 3904


class DialogChannelGroup( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )	
		self.mIsOk = None
		self.mCtrlList = None
		self.mListItems = []
		self.mDefaultList = []
		self.mTitle = ''
		self.mDefaultFocus = 0

	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.setProperty( 'DialogDrawFinished', 'False' )

		self.mLastSelected = -1
		self.mCtrlList = self.getControl( self.E_CONTROL_ID_LIST2 )
		self.mCtrlPos =  self.getControl( DIALOG_LABEL_POS_ID )

		self.InitList( )
		self.mEventBus.Register( self )

		self.setProperty( 'DialogDrawFinished', 'True' )
		self.SetFocusList( E_CONTROL_ID_LIST2 )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.mIsOk = actionId
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.mLastSelected = -1
			self.Close( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT or actionId == Action.ACTION_MOVE_RIGHT :
			pass

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN or \
			 actionId == Action.ACTION_PAGE_UP or actionId == Action.ACTION_PAGE_DOWN :

			idx = self.mCtrlList.getSelectedPosition( )
			self.mCtrlPos.setLabel( '%s'% ( idx + 1 ) )

		elif actionId == Action.ACTION_STOP :
			self.mLastSelected = -1
			self.Close( )

		elif actionId == Action.ACTION_PLAYER_PLAY or actionId == Action.ACTION_PAUSE :
			self.mLastSelected = -1
			self.Close( )


	def onClick( self, aControlId ) :
		if aControlId == DIALOG_BUTTON_CLOSE_ID :
			self.mLastSelected = -1
			self.Close( )

		elif aControlId == E_CONTROL_ID_LIST2 :
			self.SelectItem( )
			self.Close( )

		elif aControlId == DIALOG_BUTTON_OK_ID :
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

		self.GroupItems( )

		self.mCtrlList.addItems( self.mListItems )
		self.mCtrlList.selectItem( self.mDefaultFocus )
		idx = self.mCtrlList.getSelectedPosition( )
		self.mCtrlPos.setLabel( '%s'% ( idx + 1 ) )


	def GroupItems( self ) :
		for item in self.mDefaultList :
			listItem = xbmcgui.ListItem( '%s'% item.mGroupName )
			if item.mServiceType > ElisEnum.E_SERVICE_TYPE_RADIO :
				listItem.setProperty( E_XML_PROPERTY_FASTSCAN, E_TAG_TRUE )

			self.mListItems.append( listItem )


	def SelectItem( self ) :
		idx = 0
		isExist = False

		if not self.mDefaultList or len( self.mDefaultList ) < 1 or \
		   not self.mListItems or len( self.mListItems ) < 1 :
			return

		aPos = self.mCtrlList.getSelectedPosition( )
		self.mLastSelected = aPos


	def SetDefaultProperty( self, aTitle = 'SELECT', aList = None, aDefaultFocus = 0 ) :
		self.mTitle = aTitle
		self.mDefaultList = aList
		self.mDefaultFocus = aDefaultFocus


	def GetSelectedList( self ) :
		return self.mLastSelected


	def GetCloseStatus( self ) :
		return self.mIsOk


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.CloseDialog( )


	def LoadByGroup( self, aMode = E_MODE_FAVORITE_GROUP ) :
		zappingmode = self.mDataCache.Zappingmode_GetCurrent( )

		#check AllChannels
		allChannels = self.mDataCache.Channel_GetAllChannels( zappingmode.mServiceType, True )
		if not allChannels or len( allChannels ) < 1 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No channels available' ) )
			dialog.doModal( )
			return

		#check fav groups
		favoriteGroup = self.mDataCache.Favorite_GetList( FLAG_ZAPPING_CHANGE, zappingmode.mServiceType )
		if not favoriteGroup or len( favoriteGroup ) < 1 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No favorite group available' ) )
			dialog.doModal( )
			return

		#favoriteList = [MR_LANG( 'All Channels' )]
		iFavGroup = ElisIFavoriteGroup( )
		iFavGroup.mGroupName = MR_LANG( 'All Channels' )
		iFavGroup.mServiceType = zappingmode.mServiceType
		favoriteList = [ iFavGroup ]
		for item in favoriteGroup :
			#favoriteList.append( item.mGroupName )
			favoriteList.append( item )

		#find current focus
		currentIdx = 0
		if zappingmode.mMode == ElisEnum.E_MODE_FAVORITE :
			favName = zappingmode.mFavoriteGroup.mGroupName
			for idx in range( 1, len( favoriteList ) ) :
				if favName == favoriteList[idx].mGroupName :
					currentIdx = idx
					break



