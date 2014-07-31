from pvr.gui.WindowImport import *


DIALOG_MAIN_GROUP_ID		= 9000
DIALOG_WIDTH				= 370

DIALOG_MIDDLE_IMAGE_ID		= 100
DIALOG_BOTTOM_IMAGE_ID		= 101

DIALOG_LIST_ID				= 102

MAX_ITEM					= 12


class DialogHotkeys( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mItemList = []
		self.mCtrlList = None
		self.mItemCount = 0
		self.mIsOk = None


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mEventBus.Register( self )

		self.setProperty( 'DialogDrawFinished', 'False' )

		itemHeight = int( self.getProperty( 'ItemHeight' ) )
		self.mCtrlList = self.getControl( DIALOG_LIST_ID )

		listItems = []
		for i in range( self.mItemCount ) :
			( icon1, icon2, menu ) = self.mItemList[i]
			listItem = xbmcgui.ListItem( '%s' % menu )
			listItem.setProperty( 'KeyIcon1', '%s' % icon1 )
			if icon2 :
				listItem.setProperty( 'KeyIcon2', '%s' % icon2 )
			listItems.append( listItem )

		self.mCtrlList.addItems( listItems )

		# Set Dialog Size
		realcnt = self.mItemCount
		if realcnt > MAX_ITEM :
			realcnt = MAX_ITEM
		height = ( realcnt * itemHeight )
		self.getControl( DIALOG_MIDDLE_IMAGE_ID ).setHeight( height )

		# Set Dialog Bottom Image
		middle_y, empty = self.getControl( DIALOG_MIDDLE_IMAGE_ID ).getPosition( )
		middley_height = self.getControl( DIALOG_MIDDLE_IMAGE_ID ).getHeight( )
		self.getControl( DIALOG_BOTTOM_IMAGE_ID ).setPosition( 0, middle_y + middley_height )

		# Set Center Align
		start_x = E_WINDOW_WIDTH / 2 - DIALOG_WIDTH / 2
		start_y = E_WINDOW_HEIGHT / 2 - middley_height / 2
		self.getControl( DIALOG_MAIN_GROUP_ID ).setPosition( start_x, start_y )

		self.setProperty( 'DialogDrawFinished', 'True' )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.mIsOk = actionId
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.Close( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
			

	def onClick( self, aControlId ) :
		pass

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


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.CloseDialog( )
