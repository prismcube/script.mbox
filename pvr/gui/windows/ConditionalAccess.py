from pvr.gui.WindowImport import *

E_CONDITIONAL_ACCESS_BASE_ID = WinMgr.WIN_ID_CONDITIONAL_ACCESS * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 

CAS_SLOT_NUM_1 = 0
CAS_SLOT_NUM_2 = 1


class ConditionalAccess( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )

			
	def onInit( self ) :
		self.SetActivate( True )
		self.SetFrontdisplayMessage( 'Conditional Access' )		
		self.mWinId = xbmcgui.getCurrentWindowId( )

		self.mEventBus.Register( self )

		self.SetSettingWindowLabel( MR_LANG( 'Conditional Access' ) )
		self.SetPipScreen( )
		self.LoadNoSignalState( )

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
		self.SetPipLabel( )
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
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT or actionId == Action.ACTION_MOVE_RIGHT :
			pass

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

		elif groupId == E_Input03 :
			pass

		elif groupId == E_Input04 :
			pass

		elif groupId == E_Input05 :
			pass
				

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
			if aEvent.getName( ) == ElisEventCIMMIShowMenu.getName( ) :
				self.ShowEventDialog( aEvent )
			elif aEvent.getName( ) == ElisEventCIMMIShowEnq.getName( ) :
				self.ShowParentalDialog( aEvent )


	def ShowEventDialog( self, aEvent ) :
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CAS_EVENT )
		dialog.SetProperty( aEvent )
		dialog.doModal( )
		ret = dialog.GetSelectedIndex( )
		if ret >= 0 :
			self.mCommander.Cicam_SendMenuAnswer( aEvent.mSlotNo, ret + 1 )
		else :
			self.mCommander.Cicam_SendMenuAnswer( aEvent.mSlotNo, 0 )


	def ShowParentalDialog( self, aEvent ) :
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
		dialog.SetDialogProperty( '%s' % aEvent.mEnqData.mText, '', aEvent.mEnqData.mAnswerTextLen, aEvent.mEnqData.mBlindAnswer )
		dialog.doModal( )

		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			self.mCommander.Cicam_SendEnqAnswer( aEvent.mSlotNo, 1, dialog.GetString( ), len( dialog.GetString( ) ) )
		else :
			self.mCommander.Cicam_SendEnqAnswer( aEvent.mSlotNo, 0, 'None', 4 )
