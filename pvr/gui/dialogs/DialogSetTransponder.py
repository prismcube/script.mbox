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

from pvr.Util import LOG_WARN, LOG_TRACE, LOG_ERR


class DialogSetTransponder( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		self.mMode			= E_MODE_ADD_NEW_TRANSPODER
		self.mIsOk			= False
		self.mFrequency		= 0
		self.mDvbType		= 0
		self.mFec			= 0
		self.mPolarization	= 0
		self.mSimbolicRate	= 0

		self.mListDvbType		= []
		self.mListFec			= []
		self.mListPolarization	= []

		property = ElisPropertyEnum( 'DVB Type', self.mCommander )
		self.mListDvbType.append( property.GetPropStringByIndex( 0 ) )
		self.mListDvbType.append( property.GetPropStringByIndex( 1 ) )

		property = ElisPropertyEnum( 'FEC', self.mCommander )
		for i in range( property.GetIndexCount() ) :
				self.mListFec.append( property.GetPropStringByIndex( i ) )

		property = ElisPropertyEnum( 'Polarisation', self.mCommander )
		self.mListPolarization.append( property.GetPropStringByIndex( 0 ) )
		self.mListPolarization.append( property.GetPropStringByIndex( 1 ) )
		
		
	def onInit( self ) :
		if self.GetMode( ) == E_MODE_ADD_NEW_TRANSPODER :
			self.SetHeaderLabel( 'Add New Transponder' )
		elif self.GetMode( ) == E_MODE_EDIT_TRANSPODER :
			self.SetHeaderLabel( 'Edit Transponder' )
		self.SetButtonLabel( E_SETTING_DIALOG_OK, 'Confirm' )
		self.SetButtonLabel( E_SETTING_DIALOG_CANCEL, 'Cancel' )
		self.DrawItem( )
		self.mIsOk = False

		
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
		groupId = self.GetGroupId( aControlId )

		# Frequency
		if groupId == E_DialogInput01 :
			tempval = self.NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_NUMBER, 'Input Frequency', '%d' % self.mFrequency, 5 )
			if int( tempval ) > 13000 :
				self.mFrequency = 13000
			elif int( tempval ) < 3000 :
				self.mFrequency = 3000
			else :
				self.mFrequency = int( tempval )
			
			self.DrawItem( )

		# DVB Type
		elif groupId == E_DialogSpinEx01 :
			if self.GetSelectedIndex( E_DialogSpinEx01 ) == 0 :
				self.mDvbType = 0
				self.mFec = 0
				

			else :
				self.mDvbType = 1
				self.mFec = ElisEnum.E_DVBS2_QPSK_1_2
				self.getControl( E_DialogSpinEx02 + 3 ).getListItem( 0 ).setLabel2( 'QPSK 1/2' )
			self.DisableControl( )

		# FEC
		elif groupId == E_DialogSpinEx02 :
			property = ElisPropertyEnum( 'FEC', self.mCommander )
			self.mFec = property.GetPropStringByIndex( self.mListFec[ self.GetSelectedIndex( E_DialogSpinEx01 ) ] )
			
		# Polarization
		elif groupId == E_DialogSpinEx03 :
			self.mPolarization = self.GetSelectedIndex( E_DialogSpinEx03 )

		# Symbol Rate
		elif groupId == E_DialogInput02 :
			tempval = self.NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_NUMBER, 'Input Symbol Rate', '%d' % self.mSimbolicRate, 5 )
			if int( tempval ) > 60000 :
				self.mSimbolicRate = 60000
			else :
				self.mSimbolicRate = int( tempval )
			
			self.DrawItem( )

		elif groupId == E_SETTING_DIALOG_OK :			
			self.mIsOk = True
			self.ResetAllControl( )
			self.CloseDialog( )

		elif groupId == E_SETTING_DIALOG_CANCEL :
			self.mIsOk = False
			self.ResetAllControl( )
			self.CloseDialog( )

 				
	def IsOK( self ) :
		return self.mIsOk
		

	def onFocus( self, aControlId ):
		pass


	def GetValue( self ) :
		return self.mFrequency, self.mDvbType, self.mFec, self.mPolarization, self.mSimbolicRate


	def SetDefaultValue( self, aFrequency, aDvbType, aFec, aPolarization, aSimbolicRate ) :
		self.mFrequency		= aFrequency
		self.mDvbType		= aDvbType
		self.mFec			= aFec
		self.mPolarization	= aPolarization
		self.mSimbolicRate	= aSimbolicRate
		

	def DrawItem( self ) :
		self.ResetAllControl( )
		
		self.AddInputControl( E_DialogInput01, 'Frequency', '%d MHz' % self.mFrequency )
		self.AddUserEnumControl( E_DialogSpinEx01, 'DVB Type', self.mListDvbType, self.mDvbType )
		self.AddUserEnumControl( E_DialogSpinEx02, 'FEC', self.mListFec, self.mFec )
		self.AddUserEnumControl( E_DialogSpinEx03, 'Polarization', self.mListPolarization, self.mPolarization )
		self.AddInputControl( E_DialogInput02, 'Symbol Rate', '%d KS/s' % self.mSimbolicRate )
		self.AddOkCanelButton( )

		self.InitControl( )
		self.DisableControl( )


	def DisableControl( self ) :
		if self.GetSelectedIndex( E_DialogSpinEx01 ) == 0 :
			self.SetEnableControl( E_DialogSpinEx02, False )
			self.getControl( E_DialogSpinEx02 + 3 ).getListItem( 0 ).setLabel2( 'Automatic' )
		else :
			self.SetEnableControl( E_DialogSpinEx02, True )


	def GetMode( self ) :
		return self.mMode

		
	def SetMode( self, aMode ) :
		self.mMode = aMode