from pvr.gui.WindowImport import *


LIST_ID_COMMOM_LIST			= 3400
LIST_ID_COMMOM_THUMBNAIL	= 3500

BUTTON_ID_VIEW_MODE			= 100
TOGGLEBUTTON_ID_ASC			= 102
RADIIOBUTTON_ID_EXTRA		= 104

E_VIEW_MODE_LIST			= 1
E_VIEW_MODE_THUMBNAIL		= 2

CONTEXT_ADD_FAVORITE		= 0
CONTEXT_DELETE_FAVORITE		= 1


class FavoriteAddons( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mViewMode				= E_VIEW_MODE_LIST

		self.mCtrlViewMode			= None

		self.mCtrlCommonList		= None
		self.mCtrlThumbnailList		= None

		self.mAscending				= False
		self.mFavoriteAddonsIdList	= []
		self.mSelectedIndex			= -1


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( MR_LANG( 'Favorite Add-ons' ) )

		self.mCtrlCommonList 	= self.getControl( LIST_ID_COMMOM_LIST )
		self.mCtrlThumbnailList	= self.getControl( LIST_ID_COMMOM_THUMBNAIL )

		self.mViewMode = int( GetSetting( 'ADDON_VIEW_MODE' ) )
		self.mCtrlViewMode = self.getControl( BUTTON_ID_VIEW_MODE )

		self.mAscending = int( GetSetting( 'Addons_Sort' ) )

		self.UpdateViewMode( )
		self.UpdateAscending( )
		self.UpdateListItem( )

		fav1 = xbmc.executehttpapi( "getaddons()" )
		print 'dhkim test getaddons = %s' % fav1
		fav2 = xbmc.executehttpapi( "getfavourites()" )
		print 'dhkim test getfavourites = %s' % fav2


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MAINMENU )

		elif actionId == Action.ACTION_CONTEXT_MENU :
			self.mSelectedIndex = self.GetSelectedPosition( )
			if self.mSelectedIndex != -1 :
				self.mFavoriteAddonsIdList[ self.mSelectedIndex ].select( True )
				self.ShowContextMenu( )
				self.mFavoriteAddonsIdList[ self.mSelectedIndex ].select( False )

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
		
		elif aControlId == TOGGLEBUTTON_ID_ASC :
			if self.mAscending == True :
				self.mAscending = False
			else :
				self.mAscending = True

			self.UpdateAscending( )
			self.UpdateListItem( )				

		elif aControlId == RADIIOBUTTON_ID_EXTRA :
			pass


	def onFocus( self, aControlId ) :
		pass


	def UpdateListItem( self ) :
		tmpList = [ 'script.mbox', 'skin.confluence' ]
		self.mFavoriteAddonsIdList = []
		if tmpList and len( tmpList ) > 0 :
			for i in range( len( tmpList ) ) :
				addonName			= xbmcaddon.Addon( tmpList[i] ).getAddonInfo( 'name' )
				addonVersion		= xbmcaddon.Addon( tmpList[i] ).getAddonInfo( 'version' )
				addonIcon			= xbmcaddon.Addon( tmpList[i] ).getAddonInfo( 'icon' )
				addonDescription	= xbmcaddon.Addon( tmpList[i] ).getAddonInfo( 'description' )
				item = xbmcgui.ListItem(  addonName, addonVersion, addonIcon )
				item.setProperty( 'Description', addonDescription )
				self.mFavoriteAddonsIdList.append( item )

			self.mFavoriteAddonsIdList.sort( self.ByName )
			if self.mAscending == False :
				self.mFavoriteAddonsIdList.reverse( )

			self.mCtrlCommonList.reset( )
			self.mCtrlThumbnailList.reset( )

			self.mCtrlCommonList.addItems( self.mFavoriteAddonsIdList )
			self.mCtrlThumbnailList.addItems( self.mFavoriteAddonsIdList )


	def UpdateViewMode( self ) :
		if self.mViewMode == E_VIEW_MODE_LIST :
			self.mCtrlViewMode.setLabel( '%s : %s' %( MR_LANG( 'VIEW' ), MR_LANG( 'LIST' ) ) )
			self.mWin.setProperty( 'Addons_ViewMode', 'list' )
		elif self.mViewMode == E_VIEW_MODE_THUMBNAIL :
			self.mCtrlViewMode.setLabel( '%s : %s' %( MR_LANG( 'VIEW' ), MR_LANG( 'THUMBNAIL' ) ) )
			self.mWin.setProperty( 'Addons_ViewMode', 'thumbnail' )
		else :
			self.mCtrlViewMode.setLabel( '%s : %s' %( MR_LANG( 'VIEW' ), MR_LANG( 'LIST' ) ) )
			self.mWin.setProperty( 'Addons_ViewMode', 'list' )
			LOG_WARN( 'Unknown view mode' )


	def UpdateAscending( self ) :
		if self.mAscending == True :
			self.mWin.setProperty( 'Ascending', 'true' )
			self.mWin.setProperty( 'Addons_Sort', 'true' )
		else :
			self.mWin.setProperty( 'Ascending', 'false' )
			self.mWin.setProperty( 'Addons_Sort', 'false' )


	def ByName( self, aArg1, aArg2 ) :
		return cmp( aArg1.getLabel( ), aArg2.getLabel( ) )


	def ShowContextMenu( self ) :
		if self.mFavoriteAddonsIdList and len( self.mFavoriteAddonsIdList ) > 0 :
			context = []
			context.append( ContextItem( MR_LANG( 'Add favorite addon' ), CONTEXT_ADD_FAVORITE ) )
			context.append( ContextItem( MR_LANG( 'Delete favorite addon' ), CONTEXT_DELETE_FAVORITE ) )

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context )
			dialog.doModal( )
			
			contextAction = dialog.GetSelectedAction( )
			self.DoContextAction( contextAction )


	def DoContextAction( self, aContextAction ) :
		if aContextAction == CONTEXT_ADD_FAVORITE :
			pass
		elif aContextAction == CONTEXT_DELETE_FAVORITE :
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