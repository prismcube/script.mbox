from pvr.gui.WindowImport import *


CAS_SLOT_NUM_1					= 0
CAS_SLOT_NUM_2					= 1


class ConditionalAccess( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )

			
	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.SetSettingWindowLabel( MR_LANG( 'Conditional Access' ) )
		self.SetPipScreen( )
		self.LoadNoSignalState( )

		smartCard = self.mCommander.Conax_GetInformation( CAS_SLOT_NUM_1 )
		smartCardName = MR_LANG( 'Not inserted' )
		if smartCard and smartCard.mError == 0 :
			smartCardName = 'CONAX - %s' % smartCard.card_number
		else :
			smartCardName = MR_LANG( 'Not inserted' )
		self.AddInputControl( E_Input01, MR_LANG( 'Smartcard Information' ), '%s' % smartCardName, MR_LANG( 'View smartcard information' ) )

		camName = MR_LANG( 'Not inserted' )
		if self.mCommander.Cicam_IsInserted( CAS_SLOT_NUM_1 ) == True :
			cardinfo = self.mCommander.Cicam_GetInfo( CAS_SLOT_NUM_1 )
			camName = cardinfo.mName
		self.AddInputControl( E_Input02, MR_LANG( 'CAM Information' ), '%s' % camName, MR_LANG( 'View CAM information' ) )
		
		self.AddInputControl( E_Input03, MR_LANG( 'PIN Code Modification' ), '', MR_LANG( 'Change pin code' ) )
		self.AddInputControl( E_Input04, MR_LANG( 'Maturity Rating' ), '', MR_LANG( 'Access maturity rating' ) )
		self.AddInputControl( E_Input05, MR_LANG( 'Operator Message' ), '', MR_LANG( 'View operator message' ) )
		
		self.InitControl( )
		self.mInitialized = True
		self.SetFocusControl( E_Input01 )

		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GetFocusId( )
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.ResetAllControl( )
			self.SetVideoRestore( )
			WinMgr.GetInstance( ).CloseWindow( )
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			self.SetVideoRestore( )
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_MOVE_LEFT or actionId == Action.ACTION_MOVE_RIGHT :
			pass

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )
			

	def onClick( self, aControlId ) :
		groupId = self.GetGroupId( aControlId )
		if groupId == E_Input01 :
			pass
			
		elif groupId == E_Input02 :
			pass

		elif groupId == E_Input03 :
			pass

		elif groupId == E_Input04 :
			pass

		elif groupId == E_Input05 :
			pass
				

	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return

		if self.mLastFocused != aControlId :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId

