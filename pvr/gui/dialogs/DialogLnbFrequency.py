from pvr.gui.WindowImport import *


class DialogLnbFrequency( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		self.mLowFreq = 0
		self.mHighFreq = 0
		self.mThreshFreq = 0
		self.mIsOk = E_DIALOG_STATE_NO


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		
		self.SetHeaderLabel( MR_LANG( 'LNB Frequency' ) )
		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_OK_ID, MR_LANG( 'Confirm' ) )
		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_CANCEL_ID, MR_LANG( 'Cancel' ) )
		self.DrawItem( )
		self.mIsOk = E_DIALOG_STATE_NO


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			self.CloseDialog( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )

		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )


	def onClick( self, aControlId ) :
		groupId = self.GetGroupId( aControlId )

		if groupId == E_SETTING_DIALOG_BUTTON_OK_ID :
			self.mIsOk = E_DIALOG_STATE_YES
			self.ResetAllControl( )
			self.CloseDialog( )

		elif groupId == E_SETTING_DIALOG_BUTTON_CANCEL_ID :
			self.mIsOk = E_DIALOG_STATE_NO
			self.ResetAllControl( )
			self.CloseDialog( )

		elif groupId == E_DialogInput01 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( MR_LANG( 'Low frequency' ), self.mLowFreq, 5 )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.mLowFreq = dialog.GetString( )
				self.DrawItem( )

		elif groupId == E_DialogInput02 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( MR_LANG( 'High frequency' ), self.mHighFreq, 5 )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.mHighFreq = dialog.GetString( )
				self.DrawItem( )

		elif groupId == E_DialogInput03 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( MR_LANG( 'Switch frequency' ), self.mThreshFreq, 5 )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.mThreshFreq = dialog.GetString( )
				self.DrawItem( )

		else :
			xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )


	def IsOK( self ) :
		return self.mIsOk


	def onFocus( self, aControlId ) :
		pass


	def SetFrequency( self, aLowFreq, aHighFreq, aThreshFreq ) :
		self.mLowFreq = '%d' % aLowFreq
		self.mHighFreq = '%d' % aHighFreq
		self.mThreshFreq = '%d' % aThreshFreq


	def GetFrequency( self ) :
		return self.mLowFreq, self.mHighFreq, self.mThreshFreq


	def DrawItem( self ) :
		self.ResetAllControl( )

		self.AddInputControl( E_DialogInput01, MR_LANG( 'Low Frequency' ), '%d' % int( self.mLowFreq ) )
		self.AddInputControl( E_DialogInput02, MR_LANG( 'High Frequency' ), '%d' % int( self.mHighFreq ) )
		self.AddInputControl( E_DialogInput03, MR_LANG( 'Switch Frequency' ), '%d' % int( self.mThreshFreq ) )
		self.AddOkCanelButton( )
		self.SetAutoHeight( True )

		self.InitControl( )
		self.UpdateLocation( )

