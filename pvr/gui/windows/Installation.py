from pvr.gui.WindowImport import *


MENU_ID_FIRSTINSTALLATION		= 0
MENU_ID_ANTENNA_SETUP			= 1
MENU_ID_CHANNEL_SEARCH			= 2
MENU_ID_EDIT_SATELLITE			= 3
MENU_ID_EDIT_TRANSPONDER		= 4
MENU_ID_CONFIGURE				= 5
MENU_ID_CAS						= 6

class Installation( BaseWindow ):
	def __init__( self, *args, **kwargs ):
		BaseWindow.__init__( self, *args, **kwargs )

#		self.leftGroupItems = [ 'First Installation', 'Antenna Setup', 'Channel Search', 'Edit Satellite', 'Edit Transponder', 'Configure', 'CAS' ]
		self.leftGroupItems = [ 'First Installation', 'Antenna Setup', 'Channel Search', 'Edit Satellite', 'Edit Transponder', 'Configuration', 'CAS' ]
#		self.descriptionList	 = [ 'Desc First Installation', 'Desc Antenna Setup', 'Desc Channel Search', 'Desc Edit Satellite', 'Desc Edit Transponder', 'Desc Configure', 'Desc CAS' ]
		self.descriptionList	 = [ 'You can setup Language, Video, Audio, Antenna, Satellite, Channel, Time and Date in the First Installation', \
		'Antenna Setup enables you to configure Tuner 1 and Tuner 2', \
		'Channel Search menu allows you to scan channels automatically or manually', \
		'You can add or delete a satellite here', \
		'Here you can add or delete a transponder', \
		'Most of STB settings can be configured via the GUI under Configuration', \
		'The Conditional Access System allows you to setup subscription configurations including Smartcard' ]
		#self.icon = [ 'special://skin/backgrounds/appearance.jpg', 'special://skin/backgrounds/videos.jpg', 'special://skin/backgrounds/music.jpg', 'special://skin/backgrounds/pictures.jpg', 'special://skin/backgrounds/weather.jpg', 'special://skin/backgrounds/addons.jpg', 'special://skin/backgrounds/network.jpg' ]

		self.mCtrlLeftGroup = 0
		
		
	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( 'Installation' )
		self.SetPipScreen( ) 

		groupItems = []
		
		for i in range( len( self.leftGroupItems ) ) :
			#groupItems.append( xbmcgui.ListItem( self.leftGroupItems[i], self.descriptionList[i], self.icon[i] ) )
			groupItems.append( xbmcgui.ListItem( self.leftGroupItems[i], self.descriptionList[i] ) )
		
		self.mCtrlLeftGroup = self.getControl( 9000 )
		self.mCtrlLeftGroup.addItems( groupItems )


	
	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.SetVideoRestore( )
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_MAINMENU )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.SetVideoRestore( )
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_MAINMENU )


	def onClick( self, aControlId ) :
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		
		if selectedId == MENU_ID_FIRSTINSTALLATION : # First Installation
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_FIRST_INSTALLATION )

		elif selectedId == MENU_ID_ANTENNA_SETUP : # Antenna Setup
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_ANTENNA_SETUP )

		elif selectedId == MENU_ID_CHANNEL_SEARCH : # Channel Search
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CHANNEL_SEARCH )

		elif selectedId == MENU_ID_EDIT_SATELLITE : # Edit Satellite
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_EDIT_SATELLITE )
			
		elif selectedId == MENU_ID_EDIT_TRANSPONDER : # Edit TransPonder
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_EDIT_TRANSPONDER )

		elif selectedId == MENU_ID_CONFIGURE : # Config
			self.SetVideoRestore( )
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CONFIGURE )

		elif selectedId == MENU_ID_CAS : # CAS
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CONDITIONAL_ACCESS )

 
	def onFocus( self, aControlId ):
		pass
