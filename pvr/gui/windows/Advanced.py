from pvr.gui.WindowImport import *

E_ADVANCED_BASE_ID				=  WinMgr.WIN_ID_ADVANCED * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 
E_ADVANCED_SUBMENU_LIST_ID		=  E_ADVANCED_BASE_ID + 9000
E_ADVANCED_SETTING_DESCRIPTION	=  E_ADVANCED_BASE_ID + 1003


E_ADVANCED_DEFAULT_FOCUS_ID	=  E_ADVANCED_SUBMENU_LIST_ID


E_APPEARANCE			= 0
E_LIVESTREAM			= 1
E_HBBTV					= 2



class Advanced( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mGroupItems 		= []
		self.mDescriptionList	= []
		self.mCtrlLeftGroup		= None
		self.mPrevListItemID	= -1

		#self.mMainRss			= self.GetSettingToNumber( GetSetting( 'RSS_FEED_MAIN_MENU' ) )
		#self.mClockLiveScreen	= self.GetSettingToNumber( GetSetting( 'DISPLAY_CLOCK_NULLWINDOW' ) )
		#self.mClockFront		= self.GetSettingToNumber( GetSetting( 'DISPLAY_CLOCK_VFD' ) )
		#self.mEpgNotify			= self.GetSettingToNumber( GetSetting( 'DISPLAY_EVENT_LIVE' ) )

		#self.mLiveStream		= self.GetSettingToNumber( GetSetting( 'LIVE_STREAM' ) )

	def onInit( self ) :
		self.getControl( E_SETTING_CONTROL_GROUPID ).setVisible( False )

		leftGroupItems			= [
		MR_LANG( 'Appearance' ),
		#MR_LANG( 'HBB TV' ),
		MR_LANG( 'Experimental' ) ]

		self.mGroupItems = []
		for i in range( len( leftGroupItems ) ) :
			self.mGroupItems.append( xbmcgui.ListItem( leftGroupItems[i] ) )
		
		self.mDescriptionList	= [
		MR_LANG( 'You can customise the appearance of PRISMCUBE RUBY' ),
		#MR_LANG( 'HBB TV Settings' ),
		MR_LANG( 'WARNING : Problems may arise from using experimental features and there is no guarantee that your system will stay usable' ) ]
	
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
		self.mInitialized = False
		self.ResetAllControl( )
		WinMgr.GetInstance( ).CloseWindow( )


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

		elif selectedId == E_LIVESTREAM :
			if groupId == E_SpinEx01 :
				self.ControlSelect( )
			elif groupId == E_SpinEx02 :
				self.SetSettingFromNumber( 'WEB_INTERFACE', self.GetSelectedIndex( E_SpinEx02 ) )

		elif selectedId == E_HBBTV :
			pass


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

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			self.InitControl( )
			
		elif selectedId == E_LIVESTREAM :
			self.getControl( E_ADVANCED_SETTING_DESCRIPTION ).setLabel( self.mDescriptionList[ selectedId ] )
			self.AddEnumControl( E_SpinEx01, 'UPnP', MR_LANG( 'Live Streaming (restart required)' ), MR_LANG( 'Watch live stream of TV channels from PC or mobile devices' ) )
			self.AddUserEnumControl( E_SpinEx02, MR_LANG( 'Web Interface (restart required)' ), USER_ENUM_LIST_YES_NO, self.GetSettingToNumber( GetSetting( 'WEB_INTERFACE' ) ), MR_LANG( 'Open web interface' ) )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx03, E_SpinEx04 ]
			self.SetVisibleControls( hideControlIds, False )

			self.InitControl( )

		elif selectedId == E_HBBTV :
			pass
		
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


	def WaitInitialize( self ) :
		if self.mInitialized :
			time.sleep( 0.02 )
		else :
			time.sleep( 0.2 )

