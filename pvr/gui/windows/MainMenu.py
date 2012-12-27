from pvr.gui.WindowImport import *

from pvr.gui.GuiConfig import *

MAIN_GROUP_ID					= 9100
LIST_ID_FAV_ADDON				= 9050

BUTTON_ID_INSTALLATION			= 90100
BUTTON_ID_ARCHIVE				= 90200
BUTTON_ID_EPG					= 90300
BUTTON_ID_CHANNEL_LIST			= 90400
BUTTON_ID_FAVORITE_ADDONS		= 90500
BUTTON_ID_MEDIA_CENTER			= 90600
BUTTON_ID_SYSTEM_INFO			= 90700
BUTTON_ID_HELP					= 90800

BUTTON_ID_MEDIA_WEATHER	        = 90601
BUTTON_ID_MEDIA_PICTURES        = 90602
BUTTON_ID_MEDIA_MUSICS	        = 90603
BUTTON_ID_MEDIA_VIDEOS	        = 90604
BUTTON_ID_MEDIA_PROGRAMS        = 90605
BUTTON_ID_MEDIA_SETTINGS        = 90606
BUTTON_ID_MEDIA_FILE_MGR        = 90607
BUTTON_ID_MEDIA_PROFILES        = 90608
BUTTON_ID_MEDIA_SYS_INFO        = 90609

BUTTON_ID_FIRSTINSTALLATION		= 90101
BUTTON_ID_ANTENNA_SETUP			= 90102
BUTTON_ID_CHANNEL_SEARCH		= 90103
BUTTON_ID_EDIT_SATELLITE		= 90104
BUTTON_ID_EDIT_TRANSPONDER		= 90105
BUTTON_ID_CONFIGURE				= 90106
BUTTON_ID_CAS					= 90107
BUTTON_ID_UPDATE				= 90108


import sys
import os
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

class MainMenu( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mCtrlFavAddonList = None


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.CheckMediaCenter( )
		self.GetFavAddons( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_PARENT_DIR :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )

		elif actionId == Action.ACTION_MBOX_XBMC :
			self.onClick( BUTTON_ID_MEDIA_CENTER )

		elif actionId == Action.ACTION_MBOX_ARCHIVE :
			if HasAvailableRecordingHDD( ) == False :
				return	
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW )

		elif actionId == Action.ACTION_SHOW_INFO :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EPG_WINDOW )


	def onClick( self, aControlId ) :
		LOG_TRACE("MainMenu onclick(): control %d" % aControlId )
		if aControlId >= BUTTON_ID_INSTALLATION and aControlId <= BUTTON_ID_UPDATE :
			if self.mDataCache.Player_GetStatus( ).mMode != ElisEnum.E_MODE_LIVE or self.mDataCache.Record_GetRunningRecorderCount( ) > 0 :
				self.getControl( MAIN_GROUP_ID ).setVisible( False )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Try again after stopping playback, recordings\nand timeshift' ) )
				dialog.doModal( )
				self.getControl( MAIN_GROUP_ID ).setVisible( True )
			else :
				if aControlId == BUTTON_ID_INSTALLATION :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_INSTALLATION )
				elif aControlId == BUTTON_ID_FIRSTINSTALLATION :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_FIRST_INSTALLATION )
				elif aControlId == BUTTON_ID_ANTENNA_SETUP :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ANTENNA_SETUP )
				elif aControlId == BUTTON_ID_CHANNEL_SEARCH :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CHANNEL_SEARCH )
				elif aControlId == BUTTON_ID_EDIT_SATELLITE :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EDIT_SATELLITE )
				elif aControlId == BUTTON_ID_EDIT_TRANSPONDER :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EDIT_TRANSPONDER )
				elif aControlId == BUTTON_ID_CONFIGURE :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONFIGURE )
				elif aControlId == BUTTON_ID_CAS :
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CONDITIONAL_ACCESS )
				elif aControlId == BUTTON_ID_UPDATE :
					if self.mPlatform.IsPrismCube( ) :
						WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_SYSTEM_UPDATE )
					else :
						self.getControl( MAIN_GROUP_ID ).setVisible( False )
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Not support Win32' ) )
						dialog.doModal( )
						self.getControl( MAIN_GROUP_ID ).setVisible( True )
					

		elif aControlId == BUTTON_ID_ARCHIVE :
			if HasAvailableRecordingHDD( ) == False :
				return
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW )

		elif aControlId == BUTTON_ID_EPG :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EPG_WINDOW )

		elif aControlId == BUTTON_ID_CHANNEL_LIST : #Channel List
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CHANNEL_LIST_WINDOW )

		elif aControlId == BUTTON_ID_FAVORITE_ADDONS :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_FAVORITE_ADDONS )

		elif aControlId >= BUTTON_ID_MEDIA_CENTER and aControlId <= BUTTON_ID_MEDIA_SYS_INFO :
			self.SetMediaCenter( )
			if self.mDataCache.Player_GetStatus( ).mMode != ElisEnum.E_MODE_LIVE :
				self.mDataCache.Player_Stop( )

			if aControlId == BUTTON_ID_MEDIA_CENTER :
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MEDIACENTER )

		elif aControlId == BUTTON_ID_SYSTEM_INFO :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_SYSTEM_INFO )

		elif aControlId == LIST_ID_FAV_ADDON :
			position = -1
			position = self.mCtrlFavAddonList.getSelectedPosition( )
			if position != -1 :
				self.SetMediaCenter( )
				xbmc.executebuiltin( "runaddon(%s)" % self.mFavAddonsList[ position ].getProperty( 'AddonId' ) )

		elif aControlId == BUTTON_ID_HELP :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_HELP )

		elif aControlId == 20 :
			pass
			"""
			import pvr.Launcher
			pvr.Launcher.GetInstance( ).PowerOff()
			"""


	def onFocus( self, aControlId ) :
		if aControlId == E_FAKE_BUTTON :
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_NULLWINDOW )


	def GetFavAddons( self ) :
		if pvr.Platform.GetPlatform( ).IsPrismCube( ) :
			if E_ADD_XBMC_HTTP_FUNCTION == True :
				currentSkinName = xbmc.executehttpapi( "GetGUISetting(3, lookandfeel.skin)" )
				currentSkinName = currentSkinName[4:]
				if currentSkinName == 'skin.confluence' or currentSkinName == 'Default' :
					tmpList = xbmc.executehttpapi( "getfavourites()" )
					self.mCtrlFavAddonList = self.getControl( LIST_ID_FAV_ADDON )
					self.mCtrlFavAddonList.reset( )
					if tmpList != '<li>' :
						tmpList = tmpList[4:].split( ':' )
						tmpList = self.SyncAddonsList( tmpList )
						if tmpList :
							self.mFavAddonsList = []
							for i in range( len( tmpList ) ) :
								item = xbmcgui.ListItem(  xbmcaddon.Addon( tmpList[i] ).getAddonInfo( 'name' ) )
								item.setProperty( 'AddonId', tmpList[i] )
								self.mFavAddonsList.append( item )
							self.mCtrlFavAddonList.addItems( self.mFavAddonsList )
			elif E_ADD_XBMC_JSONRPC_FUNCTION == True :
				print 'E_ADD_XBMC_JSONRPC_FUNCTION : lookandfeel.skin '
				json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "GUI.GetProperties", "params": {"properties": ["skin"]}, "id": 1}')
				json_response = unicode(json_query, 'utf-8', errors='ignore')
				jsonobject = simplejson.loads(json_response)
				currentSkinName = None
				if jsonobject.has_key('result') and jsonobject['result'] != None and jsonobject['result'].has_key('skin'):
					print 'result has key with skin = %s' % jsonobject['result']['skin']
					total = str( len( jsonobject['result']['skin'] ) )
					print 'total skin result = %s' % total
					item = jsonobject['result']['skin']
					if item.has_key('id' ):
						currentSkinName = item['id']
						print 'skinId = %s' % currentSkinName
					if item.has_key('name') :
						skinName = item['name']
						print 'skinName = %s' % skinName
				if currentSkinName == 'skin.confluence' or currentSkinName == 'Default' :
					json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.GetAddonFavourites", "params": {"properties": ["name", "author", "summary", "version", "fanart", "thumbnail","description"]}, "id": 1}')
					json_response = unicode(json_query, 'utf-8', errors='ignore')
					jsonobject = simplejson.loads(json_response)
					count = 0
					if jsonobject.has_key('result') and jsonobject['result'] != None and jsonobject['result'].has_key('addons'):
						total = str( len( jsonobject['result']['addons'] ) )
						# find plugins and scripts
						addonlist = []
						for item in jsonobject['result']['addons']:
							if item['type'] == 'xbmc.python.script' or item['type'] == 'xbmc.python.pluginsource':
								addonlist.append(item)
								count += 1
					
					self.mCtrlFavAddonList = self.getControl( LIST_ID_FAV_ADDON )
					self.mCtrlFavAddonList.reset( )
					
					if count > 0 :
						self.mFavAddonsList = []
						for item in addonlist :
							listitem = xbmcgui.ListItem( item['name'] )
							listitem.setProperty( 'AddonId', item['addonid'] )
							self.mFavAddonsList.append( listitem )
						self.mCtrlFavAddonList.addItems( self.mFavAddonsList )
						

	def SyncAddonsList( self, aAddonList ) :
		#tmpList = xbmc.executehttpapi( "getaddons()" )
		result = deepcopy( aAddonList )
		return result
		if tmpList == '<li>' :
			return None
		else :
			tmpList = tmpList[4:].split( ':' )
			for i in range( len( aAddonList ) ) :
				findaddon = False
				for addon in tmpList :
					if aAddonList[i] == addon :
						findaddon = True
				if findaddon == False :
					del result[i]

		return result
