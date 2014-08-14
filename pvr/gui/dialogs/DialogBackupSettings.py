from pvr.gui.WindowImport import *


E_CONTROL_ID_RADIO_XBMC				= 1007463
E_CONTROL_ID_RADIO_CONFIG			= 1007464


class DialogBackupSettings( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		self.mCtrlRadioXBMC		= None
		self.mCtrlRadioConfig	= None
		self.mCtrlRadioRoot		= None

		self.mIsSetXBMC		= False
		self.mIsSetConfig	= False
		self.mIsSetRoot	 	= False


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.setProperty( 'DialogDrawFinished', 'False' )

		self.mCtrlRadioXBMC		= self.getControl( E_CONTROL_ID_RADIO_XBMC )
		self.mCtrlRadioConfig	= self.getControl( E_CONTROL_ID_RADIO_CONFIG )

		self.mCtrlRadioXBMC.setSelected( False )
		self.mCtrlRadioConfig.setSelected( False )

		self.mCtrlRadioXBMC.setLabel( MR_LANG( 'XBMC add-ons and Userdata' ) )
		self.mCtrlRadioConfig.setLabel( MR_LANG( 'STB Configuration' ) )
		
		self.SetHeaderLabel( MR_LANG( 'Select Data To Be Backup ( Optional )' ) )
		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_OK_ID, MR_LANG( 'Start' ) )
		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_CANCEL_ID, MR_LANG( 'Cancel' ) )
		self.mIsOk = E_DIALOG_STATE_NO

		self.setProperty( 'DialogDrawFinished', 'True' )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )

		self.GlobalSettingAction( self, actionId )
		
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.CloseDialog( )


	def onClick( self, aControlId ) :
		if aControlId == E_SETTING_DIALOG_BUTTON_OK_ID :
			self.mIsOk = E_DIALOG_STATE_YES
			self.CloseDialog( )

		elif aControlId == E_SETTING_DIALOG_BUTTON_CANCEL_ID :
			self.mIsOk = E_DIALOG_STATE_NO
			self.CloseDialog( )


	def IsOK( self ) :
		return self.mIsOk


	def onFocus( self, aControlId ) :
		pass


	def GetSelectXBMC( self ) :
		return self.mCtrlRadioXBMC.isSelected( )


	def GetSelectConfig( self ) :
		return self.mCtrlRadioConfig.isSelected( )

	#def GetSelectRoot( self ) :
		#return self.mCtrlRadioRoot.isSelected( )

