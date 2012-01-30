import xbmc
import xbmcgui
import time
import sys

import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.BaseDialog import SettingDialog
from pvr.gui.BaseWindow import Action
from ElisEnum import ElisEnum
from ElisProperty import ElisPropertyEnum
from pvr.gui.GuiConfig import *


class DialogSetTransponder( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		self.mIsOk			= E_DIALOG_STATE_NO
		self.mFrequency		= 0
		self.mFec			= 0
		self.mPolarization	= 0
		self.mSimbolicRate	= 0
		
		
	def onInit( self ) :
		self.SetHeaderLabel( 'Set Transponder' )
		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_OK_ID, 'Confirm' )
		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_CANCEL_ID, 'Cancel' )
		self.DrawItem( )
		self.mIsOk = E_DIALOG_STATE_NO

		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.ResetAllControl( )
			self.CloseDialog( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl( )
			self.CloseDialog( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )
			
		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )


	def onClick( self, aControlId ) :
		pass
		groupId = self.GetGroupId( aControlId )

		# Frequency
		if groupId == E_DialogInput01 :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( 'Frequency', '%d' % self.mFrequency, 5 )
 			dialog.doModal( )
 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
 				tempval = dialog.GetString( )
				if int( tempval ) > 13000 :
					self.mFrequency = 13000
				elif int( tempval ) < 3000 :
					self.mFrequency = 3000
				else :
					self.mFrequency = int( tempval )
				
				self.SetControlLabel2String( E_DialogInput01, '%d MHz' % self.mFrequency )

		# DVB Type
		elif groupId == E_DialogSpinEx01 :
			if self.GetSelectedIndex( E_DialogSpinEx01 ) == 0 :
				self.mFec = ElisEnum.E_FEC_UNDEFINED		
			else :
				self.mFec = ElisEnum.E_DVBS2_QPSK_1_2
	
			self.DisableControl( )

		# FEC
		elif groupId == E_DialogSpinEx02 :
			self.ControlSelect( )
			property = ElisPropertyEnum( 'FEC', self.mCommander )
			self.mFec = property.GetProp( )
			
		# Polarization
		elif groupId == E_DialogSpinEx03 :
			self.mPolarization = self.GetSelectedIndex( E_DialogSpinEx03 )

		# Symbol Rate
		elif groupId == E_DialogInput02 :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( 'Symbol Rate', '%d' % self.mSimbolicRate, 5 )
 			dialog.doModal( )
 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
 				tempval = dialog.GetString( )
				if int( tempval ) > 60000 :
					self.mSimbolicRate = 60000
				elif int( tempval ) < 1000 :
					self.mSimbolicRate = 1000
				else :
					self.mSimbolicRate = int( tempval )
				
				self.SetControlLabel2String( E_DialogInput02, '%d KS/s' % self.mSimbolicRate )

		elif groupId == E_SETTING_DIALOG_BUTTON_OK_ID :			
			self.mIsOk = E_DIALOG_STATE_YES
			self.ResetAllControl( )
			self.CloseDialog( )

		elif groupId == E_SETTING_DIALOG_BUTTON_CANCEL_ID :
			self.mIsOk = E_DIALOG_STATE_NO
			self.ResetAllControl( )
			self.CloseDialog( )

 				
	def IsOK( self ) :
		return self.mIsOk
		

	def onFocus( self, aControlId ):
		pass


	def GetValue( self ) :
		return self.mFrequency, self.mFec, self.mPolarization, self.mSimbolicRate


	def SetDefaultValue( self, aFrequency, aFec, aPolarization, aSimbolicRate ) :
		self.mFrequency		= aFrequency
		self.mFec			= aFec
		self.mPolarization	= aPolarization
		self.mSimbolicRate	= aSimbolicRate
		

	def DrawItem( self ) :
		self.ResetAllControl( )
		
		self.AddInputControl( E_DialogInput01, 'Frequency', '%d MHz' % self.mFrequency )
		
		self.AddEnumControl( E_DialogSpinEx01, 'DVB Type' )
		if self.mFec == ElisEnum.E_FEC_UNDEFINED :
			self.SetProp( E_DialogSpinEx01,  0 )
		else :
			self.SetProp( E_DialogSpinEx01,  1 )
		
		self.AddEnumControl( E_DialogSpinEx02, 'FEC' )
		self.SetProp( E_DialogSpinEx02, self.mFec )
		
		self.AddEnumControl( E_DialogSpinEx03, 'Polarisation' )
		self.SetProp( E_DialogSpinEx03, self.mPolarization )

		
		self.AddInputControl( E_DialogInput02, 'Symbol Rate', '%d KS/s' % self.mSimbolicRate )
		self.AddOkCanelButton( )
		self.SetAutoHeight( True )

		self.InitControl( )
		self.DisableControl( )


	def DisableControl( self ) :
		if self.mFec == ElisEnum.E_FEC_UNDEFINED :
			self.getControl( E_DialogSpinEx02 + 3 ).getListItem( 0 ).setLabel2( 'Automatic' )
			self.getControl( E_DialogSpinEx02 + 3 ).selectItem( 0 )
			self.SetEnableControl( E_DialogSpinEx02, False )
		else :
			self.getControl( E_DialogSpinEx02 + 3 ).getListItem( 0 ).setLabel2( 'QPSK 1/2' )
			self.SetEnableControl( E_DialogSpinEx02, True )
