from pvr.gui.WindowImport import *


DIALOG_MAIN_GROUP_ID		= 9000
DIALOG_WIDTH				= 370

DIALOG_MIDDLE_IMAGE_ID		= 100
DIALOG_BOTTOM_IMAGE_ID		= 101

DIALOG_LIST_ID				= 102
DIALOG_BUTTON_CLOSE_ID		= 103


MAX_ITEM					= 12


class DialogContext( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mItemList = []
		self.mSelectedIndex = -1
		self.mCtrlList = None
		self.mItemCount = 0
		self.mIsOk = None


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		self.mEventBus.Register( self )

		itemHeight = int( self.getProperty( 'ItemHeight' ) )
		self.mCtrlList = self.getControl( DIALOG_LIST_ID )

		listItems = []
		for i in range( self.mItemCount ) :
			listItem = xbmcgui.ListItem( '%s' % self.mItemList[i].mDescription )
			if i == self.mSelectedIndex :
				listItem.setProperty( 'mark', 'True' )
			listItems.append( listItem )

		self.mCtrlList.addItems( listItems )

		# Set Dialog Size
		realcnt = self.mItemCount
		if realcnt > MAX_ITEM :
			realcnt = MAX_ITEM
		height = realcnt * itemHeight
		self.getControl( DIALOG_MIDDLE_IMAGE_ID ).setHeight( height )

		# Set Dialog Bottom Image
		middle_y, empty = self.getControl( DIALOG_MIDDLE_IMAGE_ID ).getPosition( )
		middley_height = self.getControl( DIALOG_MIDDLE_IMAGE_ID ).getHeight( )
		self.getControl( DIALOG_BOTTOM_IMAGE_ID ).setPosition( 0, middle_y + middley_height )

		# Set Center Align
		start_x = E_WINDOW_WIDTH / 2 - DIALOG_WIDTH / 2
		start_y = E_WINDOW_HEIGHT / 2 - middley_height / 2
		self.getControl( DIALOG_MAIN_GROUP_ID ).setPosition( start_x, start_y )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.mIsOk = actionId
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.mSelectedIndex = -1
			self.Close( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_STOP :
			self.Close( )

		elif actionId == Action.ACTION_PLAYER_PLAY or actionId == Action.ACTION_PAUSE :
			self.Close( )


	def onClick( self, aControlId ) :
		if aControlId == DIALOG_BUTTON_CLOSE_ID :
			self.Close( )
			self.mSelectedIndex = -1
			return

		self.mSelectedIndex = self.mCtrlList.getSelectedPosition( )
		self.Close( )		


	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowDialogId( ) :

			if aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
				LOG_TRACE( 'ElisEventPlaybackEOF mType[%d]'% ( aEvent.mType ) )

				if aEvent.mType == ElisEnum.E_EOF_START :
					self.mIsOk = Action.ACTION_PLAYER_PLAY
					xbmc.executebuiltin('xbmc.Action(play)')

				elif aEvent.mType == ElisEnum.E_EOF_END :
					LOG_TRACE( 'EventRecv EOF_END' )
					xbmc.executebuiltin('xbmc.Action(stop)')


	def SetProperty( self, aItemList, aSelectedIndex = -1 ) :
		self.mItemList = aItemList
		if len( self.mItemList ) == 0 :
			self.mItemList.append( ContextItem( MR_LANG( 'None' ) ) )
		self.mItemCount = len( self.mItemList )

		self.mSelectedIndex = aSelectedIndex


	def GetSelectedAction( self ) :
		if self.mSelectedIndex < 0 :
			return -1

		if self.mItemList == None or self.mItemCount <= 0 :
			return -1

		return self.mItemList[ self.mSelectedIndex ].mContextAction


	def GetCloseStatus( self ) :
		return self.mIsOk


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.CloseDialog( )

