from pvr.gui.WindowImport import *


E_GROUP_LIST_CONTROL		= 8000


class DialogManualWifi( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		self.mIsOk			= E_DIALOG_STATE_NO
		self.mUseStatic		= 0
		self.mIpAddr		= MR_LANG( 'None' )
		self.mSubNet		= MR_LANG( 'None' )
		self.mGateway		= MR_LANG( 'None' )
		self.mDns			= MR_LANG( 'None' )
		self.mUseHidden		= 0
		self.mHiddenSSID	= MR_LANG( 'None' )
		self.mEncryptType	= ENCRYPT_TYPE_WEP
		self.mCurrentSsid	= 'None'


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.getControl( E_GROUP_LIST_CONTROL ).setVisible( False )
		self.SetHeaderLabel( MR_LANG( 'Manual Wifi Setup' ) )
		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_OK_ID, MR_LANG( 'Connect' ) )
		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_CANCEL_ID, MR_LANG( 'Cancel' ) )
		self.DrawItem( )
		self.mIsOk = E_DIALOG_STATE_NO
		self.getControl( E_GROUP_LIST_CONTROL ).setVisible( True )


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

		if groupId == E_DialogSpinEx01 :
			self.mUseStatic = self.GetSelectedIndex( E_DialogSpinEx01 )
			self.DisableControl( )

		elif groupId == E_DialogSpinEx02 :
			self.mUseHidden = self.GetSelectedIndex( E_DialogSpinEx02 )
			self.DisableControl( )

		elif groupId == E_DialogSpinEx03 :
			self.mEncryptType = self.GetSelectedIndex( E_DialogSpinEx03 )

		elif groupId == E_DialogInput01 :
			self.mIpAddr = self.ShowIpInputDialog( self.mIpAddr )
			self.SetControlLabel2String( E_DialogInput01, self.mIpAddr )

		elif groupId == E_DialogInput02 :
			self.mSubNet = self.ShowIpInputDialog( self.mSubNet )
			self.SetControlLabel2String( E_DialogInput02, self.mSubNet )

		elif groupId == E_DialogInput03 :
			self.mGateway = self.ShowIpInputDialog( self.mGateway )
			self.SetControlLabel2String( E_DialogInput03, self.mGateway )

		elif groupId == E_DialogInput04 :
			self.mDns = self.ShowIpInputDialog( self.mDns )
			self.SetControlLabel2String( E_DialogInput04, self.mDns )

		elif groupId == E_DialogInput05 :
			self.mHiddenSSID = InputKeyboard( E_INPUT_KEYBOARD_TYPE_NO_HIDE, MR_LANG( 'Enter your SSID' ), self.mHiddenSSID, 30 )
			self.SetControlLabel2String( E_DialogInput05, self.mHiddenSSID )

		elif groupId == E_SETTING_DIALOG_BUTTON_OK_ID :
			self.mIsOk = E_DIALOG_STATE_YES
			self.ResetAllControl( )
			self.CloseDialog( )

		elif groupId == E_SETTING_DIALOG_BUTTON_CANCEL_ID :
			self.mIsOk = E_DIALOG_STATE_NO
			self.ResetAllControl( )
			self.CloseDialog( )

		else :
			self.ResetAllControl( )
			self.CloseDialog( )


	def IsOK( self ) :
		return self.mIsOk


	def onFocus( self, aControlId ) :
		pass


	def GetValue( self ) :
		return self.mUseStatic, self.mIpAddr, self.mSubNet, self.mGateway, self.mDns, self.mUseHidden, self.mHiddenSSID, self.mEncryptType


	def SetDefaultValue( self, aCurrentSsid, aUseStatic, aIpAddr, aSubNet, aGateway, aDns, aUseHidden, aHiddenSSID, aEncryptType ) :
		self.mCurrentSsid	= aCurrentSsid
		self.mUseStatic		= aUseStatic
		self.mIpAddr		= aIpAddr
		self.mSubNet		= aSubNet
		self.mGateway		= aGateway
		self.mDns			= aDns
		self.mUseHidden		= aUseHidden
		self.mHiddenSSID	= aHiddenSSID
		self.mEncryptType	= aEncryptType


	def DrawItem( self ) :
		self.ResetAllControl( )

		self.AddUserEnumControl( E_DialogSpinEx01, MR_LANG( 'IP Settings' ), USER_ENUM_LIST_ON_OFF, self.mUseStatic, MR_LANG( 'Assign a static IP address for wireless network' ) )
		self.AddInputControl( E_DialogInput01, MR_LANG( ' - IP Address' ), self.mIpAddr, MR_LANG( 'Enter your IP address' ) )
		self.AddInputControl( E_DialogInput02, MR_LANG( ' - Subnet Mask' ), self.mSubNet, MR_LANG( 'Enter your subnet mask' ) )
		self.AddInputControl( E_DialogInput03, MR_LANG( ' - Gateway' ), self.mGateway, MR_LANG( 'Enter your gateway' ) )
		self.AddInputControl( E_DialogInput04, MR_LANG( ' - DNS' ), self.mDns, MR_LANG( 'Enter the DNS server address' ) )
		self.AddUserEnumControl( E_DialogSpinEx02, MR_LANG( 'Hidden SSID' ), USER_ENUM_LIST_ON_OFF, self.mUseHidden, MR_LANG( 'Connect to a hidden wireless network' ) )
		self.AddInputControl( E_DialogInput05, MR_LANG( ' - SSID' ), self.mHiddenSSID, MR_LANG( 'Enter network name for the wireless network you wish to connect to' ) )
		self.AddUserEnumControl( E_DialogSpinEx03, MR_LANG( ' - Security' ), USER_ENUM_LIST_ENCRYPT_TYPE, self.mEncryptType, MR_LANG( 'Select security type for the hidden wireless network' ) )
		
		self.AddOkCanelButton( )
		self.SetAutoHeight( True )
		self.InitControl( )
		self.UpdateLocation( )
		self.DisableControl( )


	def DisableControl( self ) :
		visibleControlIds = [ E_DialogInput01, E_DialogInput02, E_DialogInput03, E_DialogInput04 ]
		if self.mUseStatic :
			self.SetEnableControls( visibleControlIds, True )
		else :
			self.SetEnableControls( visibleControlIds, False )

		if self.mUseHidden :
			self.SetEnableControl( E_DialogInput05, True )
			self.SetEnableControl( E_DialogSpinEx03, True )
		else :
			self.SetEnableControl( E_DialogInput05, False )
			self.SetEnableControl( E_DialogSpinEx03, False )


	def ShowIpInputDialog( self, aIpAddr ) :
		if aIpAddr == 'None' :
			aIpAddr = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_IP, MR_LANG( 'Enter an IP address' ), '0.0.0.0' )			
		else :
			aIpAddr = NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_IP, MR_LANG( 'Enter an IP address' ), aIpAddr )
		return aIpAddr

