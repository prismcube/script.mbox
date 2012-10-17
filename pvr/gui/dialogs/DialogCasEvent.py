from pvr.gui.WindowImport import *


DIALOG_MAIN_GROUP_ID 	= 9000
BUTTON_ID_CLOSE			= 300
LABEL_ID_TITLE			= 301
LABEL_ID_SUB_TITLE		= 302
LABEL_ID_BOTTOM			= 303


class DialogCasEvent( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mTitle = ''
		self.mSubTitle = ''
		self.mBottomTitle = ''
		self.mItems = []
		self.mSelectedIndex = -1

		self.mCtrlTitleLabel = None
		self.mCtrlSubTitleLabel = None
		self.mCtrlBottomLabel = None
		self.mCtrlList = None


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mCtrlTitleLabel = self.getControl( LABEL_ID_TITLE )
		self.mCtrlSubTitleLabel = self.getControl( LABEL_ID_SUB_TITLE )
		self.mCtrlBottomLabel = self.getControl( LABEL_ID_BOTTOM )
		self.mCtrlList = self.getControl( DIALOG_MAIN_GROUP_ID )

		self.mCtrlList.reset( )
		self.DrawItem( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.mIsOk = actionId

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.mSelectedIndex = -1
			self.Close( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_PARENT_DIR :
			self.mSelectedIndex = -1
			self.Close( )


	def onClick( self, aControlId ) :
		if aControlId == BUTTON_ID_CLOSE :
			self.mSelectedIndex = -1
			self.Close( )
			return

		self.mSelectedIndex = self.mCtrlList.getSelectedPosition( )
		self.Close( )	


	def onFocus( self, aControlId ) :
		pass


	def SetProperty( self, aEvent ) :
		self.mTitle			= aEvent.mMenuData.mTitle
		self.mSubTitle		= aEvent.mMenuData.mSubtitle
		self.mBottomTitle	= aEvent.mMenuData.mBottom
		self.mItems = []
		for i in range( aEvent.mMenuData.mItemCount ) :
			self.mItems.append( xbmcgui.ListItem( aEvent.mMenuData.mItems[i].mText ) )


	def DrawItem( self ) :
		self.mCtrlList.addItems( self.mItems )
		self.mCtrlTitleLabel.setLabel( self.mTitle )
		self.mCtrlSubTitleLabel.setLabel( self.mSubTitle )
		self.mCtrlBottomLabel.setLabel( self.mBottomTitle )


	def Close( self ) :
		self.CloseDialog( )


	def GetSelectedIndex( self ) :
		return self.mSelectedIndex