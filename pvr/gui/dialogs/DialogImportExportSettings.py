from pvr.gui.WindowImport import *


E_CONTROL_ID_RADIO_CHANNELS		= 1007463
E_CONTROL_ID_RADIO_NETWORK		= 1007464


class DialogImportExportSettings( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		self.mCtrlRadioChannels	= None
		self.mCtrlRadioNetwork	= None

		self.mIsSetChannelList	= False
		self.mIsSetNetwork		= False

	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.setProperty( 'DialogDrawFinished', 'False' )

		self.mCtrlRadioChannels	= self.getControl( E_CONTROL_ID_RADIO_CHANNELS )
		self.mCtrlRadioNetwork	= self.getControl( E_CONTROL_ID_RADIO_NETWORK )
		self.mCtrlRadioChannels.setSelected( self.mIsSetChannelList )
		self.mCtrlRadioNetwork.setSelected( self.mIsSetNetwork )
		
		self.SetHeaderLabel( MR_LANG( 'Select Configuration Data' ) )
		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_OK_ID, MR_LANG( 'Confirm' ) )
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


	def SetSelect( self, aChannels = False, aNetwork = False ) :
		self.mIsSetChannelList	= aChannels
		self.mIsSetNetwork		= aNetwork


	def GetSelectChannels( self ) :
		return self.mCtrlRadioChannels.isSelected( )


	def GetSelectNetwork( self ) :
		return self.mCtrlRadioNetwork.isSelected( )

