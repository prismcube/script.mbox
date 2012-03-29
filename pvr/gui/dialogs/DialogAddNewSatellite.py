import xbmc
import xbmcgui
import sys

import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.BaseDialog import SettingDialog
from pvr.gui.BaseWindow import Action
from ElisEnum import ElisEnum
from ElisProperty import ElisPropertyEnum
from pvr.gui.GuiConfig import *
from pvr.Util import LOG_TRACE


class DialogAddNewSatellite( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		self.mIsOk = E_DIALOG_STATE_NO
		self.mSatelliteName = None
		self.mLongitude = 0
		self.mIsWest = 0
		self.mIsCBand = 0
		self.mListBand = []

		property = ElisPropertyEnum( 'Band', self.mCommander )
		self.mListBand.append( property.GetPropStringByIndex( 0 ) )
		self.mListBand.append( property.GetPropStringByIndex( 1 ) )
		
	def onInit( self ) :
		self.mLongitude = 0
		self.SetHeaderLabel( 'Add New Satellite' )
		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_OK_ID, 'Confirm' )
		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_CANCEL_ID, 'Cancel' )
		self.DrawItem( )
		self.mIsOk = E_DIALOG_STATE_NO

		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )		

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

		if groupId == E_DialogSpinEx01 :
			self.mIsWest = self.GetSelectedIndex( E_DialogSpinEx01 )

		elif groupId == E_DialogInput02 :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_SATELLITE_NUMERIC )
 			dialog.SetDialogProperty( 'Set Longitude', self.mLongitude )
 			dialog.doModal( )

 			if dialog.IsOK() == E_DIALOG_STATE_YES :
	 			self.mLongitude  = dialog.GetNumber( )
	 			self.DrawItem( )

		elif groupId == E_DialogSpinEx02 :
			self.mIsCBand = self.GetSelectedIndex( E_DialogSpinEx02 )

		elif groupId == E_DialogInput01 :
			self.mSatelliteName = InputKeyboard( E_INPUT_KEYBOARD_TYPE_NO_HIDE, 'Satellite Name', self.mSatelliteName, 15 )
			self.DrawItem( )

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
		if self.mIsWest == 1 :
			self.mLongitude = self.mLongitude + 1800

		if self.mIsCBand == 0 :
			self.mBand = ElisEnum.E_BAND_KU
		else :
			self.mBand = ElisEnum.E_BAND_C

		LOG_TRACE('Add New Satellite Longitude = %d Band = %d' % ( self.mLongitude, self.mBand ) )
		return self.mLongitude, self.mBand, self.mSatelliteName


	def DrawItem( self ) :
		self.ResetAllControl( )
	
		if self.mSatelliteName == None :
			self.mSatelliteName = ''
		self.AddInputControl( E_DialogInput01, 'Satellite Name', self.mSatelliteName )
		self.AddUserEnumControl( E_DialogSpinEx01, 'Longitude Direction', E_LIST_MY_LONGITUDE, self.mIsWest )

		tmplongitude = '%03d.%d' % ( ( self.mLongitude / 10 ), self.mLongitude % 10 )
		self.AddInputControl( E_DialogInput02, 'Longitude Angle',  tmplongitude )
		self.AddUserEnumControl( E_DialogSpinEx02, 'Band Type', self.mListBand, self.mIsCBand )
		self.AddOkCanelButton( )
		self.SetAutoHeight( True )

		self.InitControl( )
		