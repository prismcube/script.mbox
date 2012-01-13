import xbmc
import xbmcgui
import time
import sys

from pvr.gui.BaseDialog import SettingDialog
from pvr.gui.BaseWindow import Action
from pvr.gui.GuiConfig import *


class DialogLnbFrequency( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )

		self.mLowFreq = 0
		self.mHighFreq = 0
		self.mThreshFreq = 0
		self.mIsOk = False

		
	def onInit( self ) :
		self.SetHeaderLabel( 'LNB Frequency' )
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

		if groupId == E_SettingDialogOk :
			self.mIsOk = True
			self.ResetAllControl( )
			self.CloseDialog( )
			
		elif groupId == E_SettingDialogCancel :
			self.mIsOk = False
			self.ResetAllControl( )
			self.CloseDialog( )
			
		elif groupId == E_DialogInput01 :
			tempval = self.NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_NUMBER, 'Input Low Frequncy', self.mLowFreq, 5 )
			self.mLowFreq = '%d' % int( tempval )
			self.DrawItem( )

		elif groupId == E_DialogInput02 :
			tempval = self.NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_NUMBER, 'Input High Frequncy', self.mHighFreq, 5 )
			self.mHighFreq = '%d' % int( tempval )
			self.DrawItem( )

		elif groupId == E_DialogInput03 :
			tempval = self.NumericKeyboard( E_NUMERIC_KEYBOARD_TYPE_NUMBER, 'Input Switch Frequncy', self.mThreshFreq, 5 )
			self.mThreshFreq = '%d' % int( tempval )
			self.DrawItem( )

 				
	def IsOK( self ) :
		return self.mIsOk

		
	def onFocus( self, aControlId ):
		pass


	def SetFrequency( self, aLowFreq, aHighFreq, aThreshFreq ) :
		self.mLowFreq = '%d' % aLowFreq
		self.mHighFreq = '%d' % aHighFreq
		self.mThreshFreq = '%d' % aThreshFreq


	def GetFrequency( self ) :
		return self.mLowFreq, self.mHighFreq, self.mThreshFreq


	def DrawItem( self ) :
		self.ResetAllControl( )
	
		self.AddInputControl( E_DialogInput01, 'Low Frequency' , self.mLowFreq )
		self.AddInputControl( E_DialogInput02, 'High Frequency' , self.mHighFreq )
		self.AddInputControl( E_DialogInput03, 'Switch Frequency' , self.mThreshFreq )
		self.AddOkCanelButton( )
		
		self.InitControl( )
