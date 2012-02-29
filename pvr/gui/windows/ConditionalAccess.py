import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.GuiConfig import *
from pvr.gui.BaseWindow import SettingWindow, Action


class ConditionalAccess( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )

			
	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		self.SetPipScreen( )
		self.SetSettingWindowLabel( 'Conditional Access' )

		smartCard = self.mCommander.Conax_GetInformation( CAS_SLOT_NUM_1 )
		smartCardName = 'Not inserted'
		if smartCard and smartCard.mError == 0 :
			smartCardName = 'CONAX - %s' % smartCard.card_number
		else :
			smartCardName = 'Not inserted'			
		self.AddInputControl( E_Input01, 'Smartcard Information', '%s' % smartCardName, 'View smartcard information' )

		camName = 'Not inserted'
		if self.mCommander.Cicam_IsInserted( CAS_SLOT_NUM_1 ) == True :
			cardinfo = self.mCommander.Cicam_GetInfo( CAS_SLOT_NUM_1 )
			camName = cardinfo.mName
		self.AddInputControl( E_Input02, 'CAM Information', '%s' % camName, 'View CAM information' )
		
		self.AddInputControl( E_Input03, 'PIN Code Modification', '', 'Change pin code' )
		self.AddInputControl( E_Input04, 'Maturity Rating', '', 'Access maturity rating' )
		self.AddInputControl( E_Input05, 'Rights Consultation', '', 'View rights consultation' )
		self.AddInputControl( E_Input06, 'Purchase List Consultation', '', 'View purchase list consultation' )
		self.AddInputControl( E_Input07, 'Operator Message', '', 'View operator message' )
		
		self.InitControl( )
		self.ShowDescription( )
		self.mInitialized = True

		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GetFocusId( )
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.ResetAllControl( )
			self.SetVideoRestore( )
			self.close( )
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			self.SetVideoRestore( )
			self.close( )

		elif actionId == Action.ACTION_MOVE_LEFT or actionId == Action.ACTION_MOVE_RIGHT :
			pass

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			self.ShowDescription( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )
			self.ShowDescription( )
			

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

		elif groupId == E_Input06 :
			pass

		elif groupId == E_Input06 :
			pass
				

	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return

		if self.mLastFocused != aControlId :
			self.ShowDescription( )
			self.mLastFocused = aControlId
