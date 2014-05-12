from pvr.gui.WindowImport import *

E_ADVANCED_BASE_ID				=  WinMgr.WIN_ID_ADVANCED * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 
E_ADVANCED_SUBMENU_LIST_ID		=  E_ADVANCED_BASE_ID + 9000
E_ADVANCED_SETTING_DESCRIPTION	=  E_ADVANCED_BASE_ID + 1003


E_ADVANCED_DEFAULT_FOCUS_ID	=  E_ADVANCED_SUBMENU_LIST_ID


E_APPEARANCE			= 0
E_LIVESTREAM			= 1
E_CEC					= 2


class Advanced( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mGroupItems 		= []
		self.mDescriptionList	= []
		self.mCtrlLeftGroup		= None
		self.mPrevListItemID	= -1
		self.mPrevLiveStream	= ElisPropertyEnum( 'UPnP', self.mCommander ).GetPropIndex( )
		self.mPrevWebinterface	= self.GetSettingToNumber( GetSetting( 'WEB_INTERFACE' ) )


	def onInit( self ) :
		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( False )

		leftGroupItems			= [
		MR_LANG( 'Appearance' ),
		MR_LANG( 'Experimental' ),
		MR_LANG( 'HDMI-CEC' ) ]

		self.mGroupItems = []
		for i in range( len( leftGroupItems ) ) :
			self.mGroupItems.append( xbmcgui.ListItem( leftGroupItems[i] ) )
		
		self.mDescriptionList	= [
		MR_LANG( 'You can customize the appearance of PRISMCUBE RUBY' ),
		MR_LANG( 'WARNING : Problems may arise from using experimental features and there is no guarantee that your system will stay usable' ),
		MR_LANG( 'Control PRISMCUBE using your existing TV remote when connected via HDMI' ) ]
	
		self.setFocusId( E_ADVANCED_DEFAULT_FOCUS_ID )
		self.SetActivate( True )
		self.SetSingleWindowPosition( E_ADVANCED_BASE_ID )
		self.SetFrontdisplayMessage( MR_LANG('Advanced') )
		self.SetHeaderTitle( "%s - %s" % ( MR_LANG( 'Installation' ), MR_LANG( 'Advanced' ) ) )

		self.mCtrlLeftGroup = self.getControl( E_ADVANCED_SUBMENU_LIST_ID )
		self.mCtrlLeftGroup.addItems( self.mGroupItems )
		
		if self.mPrevListItemID != -1 :
			self.mCtrlLeftGroup.selectItem( self.mPrevListItemID )

		self.SetListControl( )
		self.mInitialized = True


	def Close( self ) :
		self.RestartSystem( )
		self.mInitialized = False
		self.ResetAllControl( )
		WinMgr.GetInstance( ).CloseWindow( )


	def RestartSystem( self ) :
		if self.mPrevLiveStream != ElisPropertyEnum( 'UPnP', self.mCommander ).GetPropIndex( ) or \
			self.mPrevWebinterface != self.GetSettingToNumber( GetSetting( 'WEB_INTERFACE' ) ) :

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Restart Required' ), MR_LANG( 'You must reboot your system for the changes to take effect.' ), MR_LANG( 'Do you want to restart the system now?' ) )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.mDataCache.System_Reboot( )


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return

		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.Close( )

		elif actionId == Action.ACTION_MOVE_UP :
			if focusId == E_ADVANCED_SUBMENU_LIST_ID and selectedId != self.mPrevListItemID :
				self.mPrevListItemID = selectedId
				self.SetListControl( )
			if focusId != E_ADVANCED_SUBMENU_LIST_ID :
				self.ControlUp( )

		elif actionId == Action.ACTION_MOVE_DOWN :
			if focusId == E_ADVANCED_SUBMENU_LIST_ID and selectedId != self.mPrevListItemID :
				self.mPrevListItemID = selectedId
				self.SetListControl( )
			if focusId != E_ADVANCED_SUBMENU_LIST_ID :
				self.ControlDown( )

		elif actionId == Action.ACTION_PAGE_UP or actionId == Action.ACTION_PAGE_DOWN :
			if focusId == E_ADVANCED_SUBMENU_LIST_ID and selectedId != self.mPrevListItemID :
				self.mPrevListItemID = selectedId
				self.SetListControl( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			if focusId != E_ADVANCED_SUBMENU_LIST_ID and ( ( focusId % 10 ) == 1 ) :
				self.setFocusId( E_ADVANCED_SUBMENU_LIST_ID )
			else :
				self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			if focusId == E_ADVANCED_SUBMENU_LIST_ID :
				self.SetDefaultControl( )
			elif focusId != E_ADVANCED_SUBMENU_LIST_ID and ( focusId % 10 ) == 1 :
				self.ControlRight( )


	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return

		groupId = self.GetGroupId( aControlId )
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )

		if selectedId == E_APPEARANCE :
			if groupId == E_SpinEx01 :
				self.SetSettingFromNumber( 'RSS_FEED_MAIN_MENU', self.GetSelectedIndex( E_SpinEx01 ) )
			elif groupId == E_SpinEx02 :
				self.SetSettingFromNumber( 'DISPLAY_CLOCK_NULLWINDOW', self.GetSelectedIndex( E_SpinEx02 ) )
				self.setProperty( 'ShowClock', GetSetting( 'DISPLAY_CLOCK_NULLWINDOW' ) )
			elif groupId == E_SpinEx03 :
				self.SetSettingFromNumber( 'DISPLAY_CLOCK_VFD', self.GetSelectedIndex( E_SpinEx03 ) )
				if self.GetSelectedIndex( E_SpinEx03 ) == 1 :
					ElisPropertyEnum( 'FrontDisplay Function', self.mCommander ).SetProp( 1 )
				else :
					ElisPropertyEnum( 'FrontDisplay Function', self.mCommander ).SetProp( 0 )
					self.SetFrontdisplayMessage( MR_LANG('Advanced') )
			elif groupId == E_SpinEx04 :
				self.SetSettingFromNumber( 'DISPLAY_EVENT_LIVE', self.GetSelectedIndex( E_SpinEx04 ) )
			elif groupId == E_SpinEx05 :
				self.SetSettingFromNumber( 'CUSTOM_ICON', self.GetSelectedIndex( E_SpinEx05 ) )
				if self.GetSelectedIndex( E_SpinEx05 ) == 1 :
					pvr.ChannelLogoMgr.GetInstance( ).mUseCustomPath = 'true'
				else :
					pvr.ChannelLogoMgr.GetInstance( ).mUseCustomPath = 'false'

		elif selectedId == E_LIVESTREAM :
			if groupId == E_SpinEx01 :
				self.ControlSelect( )

			elif groupId == E_SpinEx02 :
				self.SetSettingFromNumber( 'WEB_INTERFACE', self.GetSelectedIndex( E_SpinEx02 ) )

			elif groupId == E_SpinEx03 :
				if self.GetSelectedIndex( E_SpinEx03 ) == 1 :
					self.mCommander.Player_SetResolution24( 1 )
					time.sleep( 1 )
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_VIDEO_RESTORE )
					dialog.doModal( )

					if dialog.IsOK( ) == E_DIALOG_STATE_YES :
						self.SetSettingFromNumber( 'SURFACE_24', self.GetSelectedIndex( E_SpinEx03 ) )
					else :
						control = self.getControl( E_SpinEx03 + 3 )
						control.selectItem( 0 )
					self.mCommander.Player_SetResolution24( 0 )
				else :
					self.SetSettingFromNumber( 'SURFACE_24', self.GetSelectedIndex( E_SpinEx03 ) )

			elif groupId == E_SpinEx04 :
				if self.GetSelectedIndex( E_SpinEx04 ) :
					self.SetHbbTv( True )
				else :
					self.SetHbbTv( False )

		elif selectedId == E_CEC :
			self.ControlSelect( )


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
		if self.mInitialized == False :
			return

		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		if aControlId == E_ADVANCED_SUBMENU_LIST_ID :
			self.getControl( E_ADVANCED_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			if self.mPrevListItemID != selectedId :
				self.mPrevListItemID = selectedId
				self.SetListControl( )

		else :
			self.ShowDescription( aControlId, E_ADVANCED_SETTING_DESCRIPTION )


	def SetListControl( self ) :
		self.ResetAllControl( )
		self.WaitInitialize( )
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( False )

		if selectedId == E_APPEARANCE :
			self.getControl( E_ADVANCED_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddUserEnumControl( E_SpinEx01, MR_LANG( 'Show RSS on Main Menu' ), USER_ENUM_LIST_ON_OFF, self.GetSettingToNumber( GetSetting( 'RSS_FEED_MAIN_MENU' ) ), MR_LANG( 'Receive information from the RSS server as soon as it is updated' ) )
			self.AddUserEnumControl( E_SpinEx02, MR_LANG( 'Show Clock on Live Screen' ), USER_ENUM_LIST_ON_OFF, self.GetSettingToNumber( GetSetting( 'DISPLAY_CLOCK_NULLWINDOW' ) ), MR_LANG( 'Allows you to display clock on the top middle of live screen' ) )
			self.AddUserEnumControl( E_SpinEx03, MR_LANG( 'Show Clock on Front Panel Display' ), USER_ENUM_LIST_ON_OFF, self.GetSettingToNumber( GetSetting( 'DISPLAY_CLOCK_VFD' ) ), MR_LANG( 'Allows you to display clock on front panel display instead of channel name and menu' ) )
			self.AddUserEnumControl( E_SpinEx04, MR_LANG( 'Show Next EPG Notification' ), USER_ENUM_LIST_ON_OFF, self.GetSettingToNumber( GetSetting( 'DISPLAY_EVENT_LIVE' ) ), MR_LANG( 'Allows you to display next EPG notification on live screen' ) )
			self.AddUserEnumControl( E_SpinEx05, MR_LANG( 'Show Customized Channel Logos' ), USER_ENUM_LIST_ON_OFF, self.GetSettingToNumber( GetSetting( 'CUSTOM_ICON' ) ), MR_LANG( 'Allows you to display customized channel logos' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			self.InitControl( )
			
		elif selectedId == E_LIVESTREAM :
			self.getControl( E_ADVANCED_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddEnumControl( E_SpinEx01, 'UPnP', '%s ( %s )' % ( MR_LANG( 'Live Streaming' ),  MR_LANG( 'restart required' ) ), MR_LANG( 'Watch live stream of TV channels from PC or mobile devices' ) )
			self.AddUserEnumControl( E_SpinEx02, '%s ( %s )' % ( MR_LANG( 'Web Interface' ),  MR_LANG( 'restart required' ) ), USER_ENUM_LIST_YES_NO, self.GetSettingToNumber( GetSetting( 'WEB_INTERFACE' ) ), MR_LANG( 'Open web interface' ) )
			self.AddUserEnumControl( E_SpinEx03, MR_LANG( 'Automatic 1080 24p' ), USER_ENUM_LIST_YES_NO, self.GetSettingToNumber( GetSetting( 'SURFACE_24' ) ), MR_LANG( 'Allows you to playback 1080 24p video without having to switch the video output manually' ) )
			self.AddUserEnumControl( E_SpinEx04, '%s ( %s )' % ( MR_LANG( 'HbbTV' ), MR_LANG( 'restart required' ) ), USER_ENUM_LIST_YES_NO, self.GetHbbTv( ), MR_LANG( 'Watch HbbTV on your PRISMCUBE' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx05 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )

		elif selectedId == E_CEC :
			self.getControl( E_ADVANCED_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddEnumControl( E_SpinEx01, 'CEC Enable', MR_LANG( 'HDMI-CEC Setting' ), MR_LANG( 'Enable/Disable HDMI-CEC option' ) )
			self.AddEnumControl( E_SpinEx02, 'CEC TV On', MR_LANG( 'HDMI-CEC TV On' ), MR_LANG( 'Set an action for STB when turning TV on via HDMI-CEC' ) )
			self.AddEnumControl( E_SpinEx03, 'CEC TV Off', MR_LANG( 'HDMI-CEC TV Off' ), MR_LANG( 'Set an action for STB when turning TV off via HDMI-CEC' ) )
			self.AddEnumControl( E_SpinEx04, 'CEC STB On', MR_LANG( 'HDMI-CEC STB On' ), MR_LANG( 'Set an action for TV when turning STB on via HDMI-CEC' ) )
			self.AddEnumControl( E_SpinEx05, 'CEC STB Off', MR_LANG( 'HDMI-CEC STB Off' ), MR_LANG( 'Set an action for TV when turning STB off via HDMI-CEC' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			self.InitControl( )

		else :
			LOG_ERR( 'Could not find the selected ID' )

		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( True )


	def GetSettingToNumber( self, aString ) :
		if aString == 'true' :
			return 1
		else :
			return 0


	def SetSettingFromNumber( self, aId, aValue ) :
		if aValue == 1 :
			SetSetting( aId, 'true' )
		else :
			SetSetting( aId, 'false' )


	def GetHbbTv( self ) :
		if os.path.exists( FILE_NAME_HBB_TV ) :
			return 1
		else :
			return 0


	def SetHbbTv( self, aFlag ) :
		if aFlag :
			os.system( 'touch %s' % FILE_NAME_HBB_TV )
		else :
			os.system( 'rm %s' % FILE_NAME_HBB_TV )


	def WaitInitialize( self ) :
		if self.mInitialized :
			time.sleep( 0.02 )
		else :
			time.sleep( 0.2 )

