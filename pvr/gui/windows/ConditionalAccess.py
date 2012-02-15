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

		self.AddInputControl( E_Input01, 'Smartcard Information', '', 'View smartcard information' )
		self.AddInputControl( E_Input02, 'PIN Code Modification', '', 'Change pin code' )
		self.AddInputControl( E_Input03, 'Maturity Rating', '', 'Access maturity rating' )
		self.AddInputControl( E_Input04, 'Rights Consultation', '', 'View rights consultation' )
		self.AddInputControl( E_Input05, 'Purchase List Consultation', '', 'View purchase list consultation' )
		self.AddInputControl( E_Input06, 'Operator Message', '', 'View operator message' )
		
		self.InitControl( )
		self.ShowDescription( self.getFocusId( ) )
		self.mInitialized = True

		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
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
			self.ShowDescription( focusId )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )
			self.ShowDescription( focusId )
			

	def onClick( self, aControlId ) :
		groupId = self.GetGroupId( aControlId )
		if groupId == E_Input01 :
			cardinfo = self.mCommander.Cicam_GetInfo( CAS_SLOT_NUM_1 )
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( 'SMART Card Inserted', 'SMART card Name = %s' % cardinfo.mName)
 			dialog.doModal( )
			
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
				

	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return

		if self.mLastFocused != aControlId :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId
