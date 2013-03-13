from pvr.gui.WindowImport import *


E_CONDITIONAL_ACCESS_BASE_ID = WinMgr.WIN_ID_CONDITIONAL_ACCESS * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 


class ConditionalAccess( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )

			
	def onInit( self ) :
		self.SetActivate( True )
		self.SetSingleWindowPosition( E_CONDITIONAL_ACCESS_BASE_ID )
		self.SetFrontdisplayMessage( 'Conditional Access' )		
		self.mWinId = xbmcgui.getCurrentWindowId( )

		self.mEventBus.Register( self )

		self.SetSettingWindowLabel( MR_LANG( 'Conditional Access' ) )
		self.SetPipScreen( )

		smartCard = self.mCommander.Conax_GetInformation( CAS_SLOT_NUM_1 )
		smartCardName = MR_LANG( 'Not inserted' )
		if smartCard and smartCard.mError == 0 :
			smartCardName = 'CONAX - %s' % smartCard.card_number
		else :
			smartCardName = MR_LANG( 'Not inserted' )
		self.AddInputControl( E_Input01, MR_LANG( 'Smartcard Information' ), '%s' % smartCardName, MR_LANG( 'View Smartcard information' ) )

		camName = MR_LANG( 'Not inserted' )
		if self.mCommander.Cicam_IsInserted( CAS_SLOT_NUM_1 ) == True :
			cardinfo = self.mCommander.Cicam_GetInfo( CAS_SLOT_NUM_1 )
			camName = cardinfo.mName
		self.AddInputControl( E_Input02, MR_LANG( 'CAM Information' ), '%s' % camName, MR_LANG( 'View CAM information' ) )
		
		self.InitControl( )
		self.SetFocusControl( E_Input01 )
		self.mInitialized = True

		
	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		actionId = aAction.getId( )
		self.GetFocusId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			self.SetVideoRestore( )
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )
			

	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
		groupId = self.GetGroupId( aControlId )
		if groupId == E_Input01 :
			pass
			
		elif groupId == E_Input02 :
			self.mCommander.Cicam_EnterMMI( CAS_SLOT_NUM_1 )
				

	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
		if self.mInitialized == False :
			return

		if self.mLastFocused != aControlId :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId


	def onEvent( self, aEvent ) :
		if xbmcgui.getCurrentWindowId( ) == self.mWinId :
			if aEvent.getName( ) == ElisEventCAMInsertRemove.getName( ) :
				camName = MR_LANG( 'Not inserted' )
				if aEvent.mInserted :
					time.sleep( 1 )
					if self.mCommander.Cicam_IsInserted( CAS_SLOT_NUM_1 ) == True :
						cardinfo = self.mCommander.Cicam_GetInfo( CAS_SLOT_NUM_1 )
						camName = cardinfo.mName
					self.SetControlLabel2String( E_Input02, camName )
				else :
					self.SetControlLabel2String( E_Input02, camName )

