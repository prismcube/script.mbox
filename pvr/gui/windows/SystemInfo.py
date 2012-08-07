from pvr.gui.WindowImport import *
from subprocess import *


LABEL_ID_RECORD_FREE_SIZE	=	301
LABEL_ID_HDD_TEMEPERATURE	=	302


class SystemInfo( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
 
#		leftGroupItems			= [ 'STB Infomation' ]
		leftGroupItems			= [ 'Version' ]
	
		self.mCtrlLeftGroup 			= None
		self.mCtrlRecordFreeSize		= None
		self.mCtrlHDDTemperature		= None
		self.mGroupItems 				= []
		self.mInitialized 				= False
		self.mCheckEndThread			= True
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
		self.mCtrlHDDTemperature = self.getControl( LABEL_ID_HDD_TEMEPERATURE )

#		self.getControl( E_SETTING_MINI_TITLE ).setLabel( 'System Information' )
		self.getControl( E_SETTING_MINI_TITLE ).setLabel( 'STB Information' )

		position = self.mCtrlLeftGroup.getSelectedPosition( )
		self.mCtrlLeftGroup.selectItem( position )
		self.ShowRecordFreeSize( )
		self.ShowHDDTemperature( )
		self.SetListControl( )
		self.mInitialized = True
		self.mCheckEndThread = True


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
			self.mCheckEndThread = False
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
				self.mCheckEndThread = False
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
		size = None
		percent = None
		if self.mCommander.Record_GetPartitionSize( ) != -1 and self.mCommander.Record_GetFreeMBSize( ) != -1 :
			size	= self.mCommander.Record_GetFreeMBSize( )
			percent = int( size / float( self.mCommander.Record_GetPartitionSize( ) ) * 100 )
		else :
			LOG_ERR( 'Get Record_GetPartitionSize or Record_GetFreeMBSize Fail!!!' )
		self.mCtrlRecordFreeSize.setLabel( 'Record Free Size : %s MB ( %s%% )' % ( size, percent ) )


	@RunThread
	def ShowHDDTemperature( self ) :
		tem = ''
		cmd = 'hddtemp /dev/sda -n -q'
		while( self.mCheckEndThread ) :
			tem = Popen( cmd, shell=True, stdout=PIPE )
			tem = tem.stdout.read( ).strip( )			
			if self.IsNumber( tem ) == False :
				tem = 'Unknown'
			LOG_TRACE( 'HDD Temperature = %s' % tem )
			self.mCtrlHDDTemperature.setLabel( 'HDD Temperature : %s' % tem )
			time.sleep( 10 )


	def IsNumber( self, aString ) :
		try :
			float( aString )
			return True
		except ValueError :
			return False
