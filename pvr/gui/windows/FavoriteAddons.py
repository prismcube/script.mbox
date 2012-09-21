from pvr.gui.WindowImport import *


LIST_ID_COMMOM_LIST			= 3400
LIST_ID_COMMOM_THUMBNAIL	= 3500

BUTTON_ID_VIEW_MODE			= 100
BUTTON_ID_SORT_MODE			= 101
TOGGLEBUTTON_ID_ASC			= 102
RADIIOBUTTON_ID_EXTRA		= 104

E_SORT_NAME					= 0
E_SORT_DATE					= 1

E_VIEW_MODE_LIST			= 1
E_VIEW_MODE_THUMBNAIL		= 2

CONTEXT_DELETE_FAVORITE		= 0
CONTEXT_ADDON_SETTING		= 1


class FavoriteAddons( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mViewMode				= E_VIEW_MODE_LIST
		self.mSortMode				= E_SORT_DATE

		self.mCtrlViewMode			= None
		self.mCtrlSortMode			= None

		self.mCtrlCommonList		= None
		self.mCtrlThumbnailList		= None

		self.mAscending				= []
		self.mFavoriteAddonsList	= []
		self.mSelectedIndex			= -1


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( MR_LANG( 'Favorite Add-ons' ) )

		self.mCtrlCommonList 	= self.getControl( LIST_ID_COMMOM_LIST )
		self.mCtrlThumbnailList	= self.getControl( LIST_ID_COMMOM_THUMBNAIL )

		self.mViewMode = int( GetSetting( 'ADDON_VIEW_MODE' ) )
		self.mCtrlViewMode = self.getControl( BUTTON_ID_VIEW_MODE )

		self.mSortMode = int( GetSetting( 'ADDON_SORT_MODE' ) )		
		self.mCtrlSortMode = self.getControl( BUTTON_ID_SORT_MODE )

		self.mAscending = []
		self.mAscending = [ False, False ]

		self.mAscending[ E_SORT_NAME ] = True
		self.mAscending[ E_SORT_DATE ] = False

		self.UpdateViewMode( )
		self.UpdateSortMode( )
		self.UpdateAscending( )
		self.UpdateListItem( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MAINMENU )

		elif actionId == Action.ACTION_CONTEXT_MENU :
			self.mSelectedIndex = self.GetSelectedPosition( )
			if self.mSelectedIndex == len( self.mFavoriteAddonsList ) - 1 :
				return
			else :
				if self.mSelectedIndex != -1 :
					self.mFavoriteAddonsList[ self.mSelectedIndex ].select( True )
					self.ShowContextMenu( )
					self.mFavoriteAddonsList[ self.mSelectedIndex ].select( False )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass


	def onClick( self, aControlId ) :
		if aControlId == BUTTON_ID_VIEW_MODE :	
			if self.mViewMode == E_VIEW_MODE_LIST :
				self.mViewMode = E_VIEW_MODE_THUMBNAIL
			else :
				self.mViewMode = E_VIEW_MODE_LIST

			SetSetting( 'ADDON_VIEW_MODE', '%d' % self.mViewMode )
			self.UpdateViewMode( )
			self.UpdateListItem( )

		elif aControlId == BUTTON_ID_SORT_MODE :
			if self.mSortMode == E_SORT_NAME :
				self.mSortMode = E_SORT_DATE
			else :
				self.mSortMode = E_SORT_NAME
				
			SetSetting( 'ADDON_SORT_MODE', '%d' % self.mSortMode ) 								
			self.UpdateSortMode( )			
			self.UpdateAscending( )
			self.UpdateListItem( )
		
		elif aControlId == TOGGLEBUTTON_ID_ASC :
			if self.mAscending[self.mSortMode] == True :
				self.mAscending[self.mSortMode] = False
			else :
				self.mAscending[self.mSortMode] = True

			self.UpdateAscending( )
			self.UpdateListItem( )				

		elif aControlId == RADIIOBUTTON_ID_EXTRA :
			pass


	def onFocus( self, aControlId ) :
		pass


	def UpdateListItem( self ) :
		self.mFavoriteAddonsList = []
		item = xbmcgui.ListItem( 'YouTube', '0.0.1', 'DefaultAddon.png' )
		self.mFavoriteAddonsList.append( item )

		if self.mFavoriteAddonsList == None or len( self.mFavoriteAddonsList ) == 0 :
			self.mFavoriteAddonsList = []

		if self.mSortMode == E_SORT_NAME :
			self.mFavoriteAddonsList.sort( self.ByName )
		elif self.mSortMode == E_SORT_DATE :
			self.mFavoriteAddonsList.sort( self.ByDate )
		else :
			LOG_WARN( 'Unknown sort mode' )		
			self.mSortMode = E_SORT_NAME
			self.mFavoriteAddonsList.sort( self.ByName )

		if self.mAscending[self.mSortMode] == False :
			self.mFavoriteAddonsList.reverse( )

		item = xbmcgui.ListItem( 'Add Favorite Addons', '', 'DefaultAddon.png' )
		self.mFavoriteAddonsList.append( item )

		self.mCtrlCommonList.reset( )
		self.mCtrlThumbnailList.reset( )

		self.mCtrlCommonList.addItems( self.mFavoriteAddonsList )
		self.mCtrlThumbnailList.addItems( self.mFavoriteAddonsList )


	def UpdateViewMode( self ) :
		if self.mViewMode == E_VIEW_MODE_LIST :
			self.mCtrlViewMode.setLabel( '%s: %s' %( MR_LANG( 'VIEW' ), MR_LANG( 'LIST' ) ) )
		elif self.mViewMode == E_VIEW_MODE_THUMBNAIL :
			self.mCtrlViewMode.setLabel( '%s: %s' %( MR_LANG( 'VIEW' ), MR_LANG( 'THUMBNAIL' ) ) )
		else :
			self.mCtrlViewMode.setLabel( '%s: %s' %( MR_LANG( 'VIEW' ), MR_LANG( 'LIST' ) ) )
			LOG_WARN( 'Unknown view mode' )
		if self.mViewMode == E_VIEW_MODE_LIST :
			self.mWin.setProperty( 'Addons_ViewMode', 'list' )
		elif self.mViewMode == E_VIEW_MODE_THUMBNAIL :
			self.mWin.setProperty( 'Addons_ViewMode', 'thumbnail' )
		else :
			self.mViewMode = E_VIEW_MODE_LIST
			self.mWin.setProperty( 'Addons_ViewMode', 'list' )


	def UpdateSortMode( self ) :
		if self.mSortMode == E_SORT_NAME :
			self.mCtrlSortMode.setLabel( '%s: %s' %( MR_LANG( 'SORT BY' ), MR_LANG( 'NAME' ) ) )
		elif self.mSortMode == E_SORT_DATE :
			self.mCtrlSortMode.setLabel( '%s: %s' %( MR_LANG( 'SORT BY' ), MR_LANG( 'DATE' ) ) )
		else :
			LOG_WARN( 'Unknown view mode' )


	def UpdateAscending( self ) :
		if self.mAscending[self.mSortMode] == True :
			self.mWin.setProperty( 'Ascending', 'true' )
		else :
			self.mWin.setProperty( 'Ascending', 'false' )


	def ByName( self, aArg1, aArg2 ) :
		return cmp( aArg1.getLabel( ), aArg2.getLabel( ) )


	def ByDate( self, aArg1, aArg2 ) :
		return cmp( aArg1.getLabel( ), aArg2.getLabel( ) )


	def ShowContextMenu( self ) :
		if self.mFavoriteAddonsList and len( self.mFavoriteAddonsList ) > 0 :
			context = []
			context.append( ContextItem( MR_LANG( 'Delete favorite addon' ), CONTEXT_DELETE_FAVORITE ) )
			context.append( ContextItem( MR_LANG( 'Add-on settings' ), CONTEXT_ADDON_SETTING ) )
		else :
			# Todo
			#if self.mSelectedIndex
			return
			
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
		dialog.doModal( )
		
		contextAction = dialog.GetSelectedAction( )
		self.DoContextAction( contextAction )


	def DoContextAction( self, aContextAction ) :
		if aContextAction == CONTEXT_DELETE_FAVORITE :
			pass
			#self.UpdateListItem( )
		elif aContextAction == CONTEXT_ADDON_SETTING :
			pass
		else :
			LOG_ERR( 'Unknown Context Action' )


	def GetSelectedPosition( self ) :
		position  = -1 

		if self.mViewMode == E_VIEW_MODE_LIST :
			position = self.mCtrlCommonList.getSelectedPosition( )		
		elif self.mViewMode == E_VIEW_MODE_THUMBNAIL :
			position = self.mCtrlThumbnailList.getSelectedPosition( )				
		else :
			position = -1

		return position