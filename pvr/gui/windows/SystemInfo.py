from pvr.gui.WindowImport import *


LABEL_ID_RECORD_FREE_SIZE	=	301


class SystemInfo( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
 
		leftGroupItems			= [ 'STB Infomation' ]
	
		self.mCtrlLeftGroup 			= None
		self.mCtrlRecordFreeSize		= None
		self.mGroupItems 				= []
		self.mInitialized 				= False
		self.mLastFocused 				= E_SUBMENU_LIST_ID
		self.mPrevListItemID 			= 0

		self.mCheckHiddenPattern1	= False
		self.mCheckHiddenPattern2	= False
		self.mCheckHiddenPattern3	= False

		for i in range( len( leftGroupItems ) ) :
			self.mGroupItems.append( xbmcgui.ListItem( leftGroupItems[i] ) )

		
			
	def onInit( self )  :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mCtrlLeftGroup = self.getControl( E_SUBMENU_LIST_ID )
		self.mCtrlLeftGroup.addItems( self.mGroupItems )
		self.mCtrlRecordFreeSize = self.getControl( LABEL_ID_RECORD_FREE_SIZE )

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( 'System Information' )

		position = self.mCtrlLeftGroup.getSelectedPosition( )
		self.mCtrlLeftGroup.selectItem( position )
		self.ShowRecordFreeSize( )
		self.SetListControl( )
		self.mInitialized = True


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		self.GlobalAction( actionId )
		self.CheckHiddenAction( actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mInitialized = False
			WinMgr.GetInstance().CloseWindow( )

		elif actionId == Action.ACTION_MOVE_UP :
			if focusId == E_SUBMENU_LIST_ID and self.mCtrlLeftGroup.getSelectedPosition() != self.mPrevListItemID :
				self.mPrevListItemID = self.mCtrlLeftGroup.getSelectedPosition( )
				self.SetListControl( )
	
		elif actionId == Action.ACTION_MOVE_DOWN :
			if focusId == E_SUBMENU_LIST_ID and self.mCtrlLeftGroup.getSelectedPosition() != self.mPrevListItemID :
				self.mPrevListItemID = self.mCtrlLeftGroup.getSelectedPosition( )
				self.SetListControl( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			if focusId != E_SUBMENU_LIST_ID and ( ( focusId % 10 ) == 1 ) :
				self.setFocusId( E_SUBMENU_LIST_ID )
				
		elif actionId == Action.ACTION_MOVE_RIGHT :
			if focusId == E_SUBMENU_LIST_ID :
				self.setFocusId( E_SETUPMENU_GROUP_ID )


	def CheckHiddenAction( self, aAction ) :
		if aAction == Action.ACTION_MOVE_LEFT :
			if self.mCheckHiddenPattern1 == True :
				self.mCheckHiddenPattern2 = True
			self.mCheckHiddenPattern1 = True
		elif aAction == Action.ACTION_MOVE_RIGHT and self.mCheckHiddenPattern2 :
			if self.mCheckHiddenPattern3 == True :
				self.mCheckHiddenPattern1	= False
				self.mCheckHiddenPattern2	= False
				self.mCheckHiddenPattern3	= False
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_HIDDEN_TEST, WinMgr.WIN_ID_NULLWINDOW )
				return
			self.mCheckHiddenPattern3 = True
		else :
			self.mCheckHiddenPattern1	= False
			self.mCheckHiddenPattern2	= False
			self.mCheckHiddenPattern3	= False


	def onClick( self, aControlId ) :
		pass


	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return
		if ( self.mLastFocused != aControlId ) or ( self.mCtrlLeftGroup.getSelectedPosition( ) != self.mPrevListItemID ) :
			if aControlId == E_SUBMENU_LIST_ID :
				self.SetListControl( )
				if self.mLastFocused != aControlId :
					self.mLastFocused = aControlId
				if self.mCtrlLeftGroup.getSelectedPosition( ) != self.mPrevListItemID :
					self.mPrevListItemID = self.mCtrlLeftGroup.getSelectedPosition( )
		

	def SetListControl( self ) :
		#self.ResetAllControl( )
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		
		if selectedId == 0 :
			pass


	def ShowRecordFreeSize( self ) :
		size = ''
		if self.mCommander.Record_GetFreeMBSize( ) != -1 :
			size = '%s' % self.mCommander.Record_GetFreeMBSize( )
		self.mCtrlRecordFreeSize.setLabel( 'Record Free Size : %s MB' % size )
