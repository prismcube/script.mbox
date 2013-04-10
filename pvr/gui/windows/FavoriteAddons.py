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
CONTEXT_RUN_FAVORITE		= 2

import sys
import os
if sys.version_info < (2, 7) :
    import simplejson
else:
    import json as simplejson
    
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
		self.SetActivate( True )
		self.SetFrontdisplayMessage( 'Favorite' )		
		print 'BUTTON_ID_FAVORITE_ADDONS :onInit 01'
		self.mWinId = xbmcgui.getCurrentWindowId( )
		print 'BUTTON_ID_FAVORITE_ADDONS :onInit 02'

		#self.getControl( E_SETTING_MINI_TITLE ).setLabel( MR_LANG( 'Favorite Add-ons' ) )
		print 'BUTTON_ID_FAVORITE_ADDONS :onInit 03'

		if pvr.Platform.GetPlatform( ).IsPrismCube( ) == False :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No support %s' ) % self.mPlatform.GetName( ) )
			dialog.doModal( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MAINMENU )
		print 'BUTTON_ID_FAVORITE_ADDONS :onInit 1'

		self.mCtrlCommonList 	= self.getControl( LIST_ID_COMMOM_LIST )
		self.mCtrlThumbnailList	= self.getControl( LIST_ID_COMMOM_THUMBNAIL )

		self.mViewMode = int( GetSetting( 'ADDON_VIEW_MODE' ) )
		self.mCtrlViewMode = self.getControl( BUTTON_ID_VIEW_MODE )

		self.mAscending = int( GetSetting( 'Addons_Sort' ) )
		print 'BUTTON_ID_FAVORITE_ADDONS :onInit 2'

		self.CheckMediaCenter( )
		print 'BUTTON_ID_FAVORITE_ADDONS :onInit 3'
		self.UpdateViewMode( )
		print 'BUTTON_ID_FAVORITE_ADDONS :onInit 4'
		self.UpdateAscending( )
		print 'BUTTON_ID_FAVORITE_ADDONS :onInit 5'
		self.UpdateListItem( )
		self.SetFocusList( self.mViewMode )

		print 'BUTTON_ID_FAVORITE_ADDONS :onInit 6'


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MAINMENU )

		elif actionId == Action.ACTION_CONTEXT_MENU :
			self.mSelectedIndex = self.GetSelectedPosition( )
			if self.mSelectedIndex != -2 :
				self.ShowContextMenu( )


	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
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

		elif aControlId == LIST_ID_COMMOM_LIST or aControlId == LIST_ID_COMMOM_THUMBNAIL :
			self.mSelectedIndex = self.GetSelectedPosition( )
			if self.mSelectedIndex != -1 :
				self.SetMediaCenter( )
				xbmc.executebuiltin( "runaddon(%s)" % self.mFavoriteAddonsIdList[ self.mSelectedIndex ].getProperty( 'AddonId' ) )


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return


	def UpdateListItem( self ) :
		self.mFavoriteAddonsIdList = []

		favoriteList = XBMC_GetFavAddons( )
		self.mCtrlCommonList.reset( )
		self.mCtrlThumbnailList.reset( )

		if len( favoriteList ) > 0 :
			for i in range( len( favoriteList ) ) :
				addonName			= xbmcaddon.Addon( favoriteList[i] ).getAddonInfo( 'name' )
				addonVersion		= xbmcaddon.Addon( favoriteList[i] ).getAddonInfo( 'version' )
				addonIcon			= xbmcaddon.Addon( favoriteList[i] ).getAddonInfo( 'icon' )
				addonDescription	= xbmcaddon.Addon( favoriteList[i] ).getAddonInfo( 'description' )
				item = xbmcgui.ListItem(  addonName, addonVersion, addonIcon )
				item.setProperty( 'AddonId', favoriteList[i] )
				item.setProperty( 'Description', addonDescription )
				self.mFavoriteAddonsIdList.append( item )

			self.mFavoriteAddonsIdList.sort( self.ByName )
			if self.mAscending == False :
				self.mFavoriteAddonsIdList.reverse( )

			self.mCtrlCommonList.addItems( self.mFavoriteAddonsIdList )
			self.mCtrlThumbnailList.addItems( self.mFavoriteAddonsIdList )



	def UpdateViewMode( self ) :
		if self.mViewMode == E_VIEW_MODE_LIST :
			self.mCtrlViewMode.setLabel( '%s : %s' %( MR_LANG( 'View' ), MR_LANG( 'List' ) ) )
			self.setProperty( 'Addons_ViewMode', 'list' )
		elif self.mViewMode == E_VIEW_MODE_THUMBNAIL :
			self.mCtrlViewMode.setLabel( '%s : %s' %( MR_LANG( 'View' ), MR_LANG( 'Thumbnail' ) ) )
			self.setProperty( 'Addons_ViewMode', 'thumbnail' )
		else :
			self.mCtrlViewMode.setLabel( '%s : %s' %( MR_LANG( 'View' ), MR_LANG( 'List' ) ) )
			self.setProperty( 'Addons_ViewMode', 'list' )
			LOG_WARN( 'Unknown view mode' )


	def UpdateAscending( self ) :
		if self.mAscending == True :
			self.setProperty( 'Ascending', 'true' )
			self.setProperty( 'Addons_Sort', 'true' )
		else :
			self.setProperty( 'Ascending', 'false' )
			self.setProperty( 'Addons_Sort', 'false' )


	def ByName( self, aArg1, aArg2 ) :
		return cmp( aArg1.getLabel( ), aArg2.getLabel( ) )


	def ShowContextMenu( self ) :
		context = []
		context.append( ContextItem( MR_LANG( 'Add to favorite add-on' ), CONTEXT_ADD_FAVORITE ) )
		if self.mFavoriteAddonsIdList and len( self.mFavoriteAddonsIdList ) > 0 and self.mSelectedIndex != -1 :
			context.append( ContextItem( MR_LANG( 'Remove' ), CONTEXT_DELETE_FAVORITE ) )
			context.append( ContextItem( MR_LANG( 'Run' ), CONTEXT_RUN_FAVORITE ) )
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
		dialog.doModal( )
			
		contextAction = dialog.GetSelectedAction( )
		self.DoContextAction( contextAction )


	def DoContextAction( self, aContextAction ) :
		if aContextAction == CONTEXT_ADD_FAVORITE :
			addonList = XBMC_GetAddons( )
			if len( addonList ) <= 0  :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No add-ons installed' ) )
	 			dialog.doModal( )
			else :
				dialog = xbmcgui.Dialog( )
				ret = dialog.select( MR_LANG( 'Select Add-on' ), addonList )
				if ret >= 0 :
					XBMC_AddFavAddon( addonList[ret] )
					self.UpdateListItem( )

		elif aContextAction == CONTEXT_DELETE_FAVORITE :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty(  MR_LANG( 'Delete favorite add-on' ),  MR_LANG( 'Do you want to remove %s?' ) % self.mFavoriteAddonsIdList[ self.mSelectedIndex ].getProperty( 'AddonId' ) )
				dialog.doModal( )
				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					XBMC_RemoveFavAddon( self.mFavoriteAddonsIdList[ self.mSelectedIndex ].getProperty( 'AddonId' ) )
					self.UpdateListItem( )

		elif aContextAction == CONTEXT_RUN_FAVORITE :
			self.SetMediaCenter( )
			XBMC_RunAddon( self.mFavoriteAddonsIdList[ self.mSelectedIndex ].getProperty( 'AddonId' ) )			
			
		else :
			LOG_ERR( 'Unknown Context Action' )


	def GetSelectedPosition( self ) :
		position  = -1

		if self.GetFocusId( ) == LIST_ID_COMMOM_LIST or self.GetFocusId( ) == LIST_ID_COMMOM_THUMBNAIL :
			if self.mViewMode == E_VIEW_MODE_LIST :
				position = self.mCtrlCommonList.getSelectedPosition( )
			elif self.mViewMode == E_VIEW_MODE_THUMBNAIL :
				position = self.mCtrlThumbnailList.getSelectedPosition( )
			else :
				position = -1
		else :
			position = -2

		return position


	def SetFocusList( self, aMode ) :
		if aMode == E_VIEW_MODE_LIST :
			self.setFocusId( LIST_ID_COMMOM_LIST )
		elif aMode == E_VIEW_MODE_THUMBNAIL :
			self.setFocusId( LIST_ID_COMMOM_THUMBNAIL )
		else :
			LOG_ERR( 'SetFocusList fail' )
		
