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

"""
E_DIALOG_HEADER			= 100

E_LONGITUDE_NEXT		= 201
E_LONGITUDE_PREV		= 202
E_LONGITUDE_LIST		= 203

E_EDIT_LONGITUDE_BUTTON = 300
E_EDIT_LONGITUDE_LABEL1 = 301
E_EDIT_LONGITUDE_LABEL2 = 302

E_BAND_NEXT				= 401
E_BAND_PREV				= 402
E_BAND_LIST				= 403

E_BUTTON_OK_ID			= 501
E_BUTTON_CANCEL_ID		= 601
"""

class DialogAddNewSatellite( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		self.mIsOk = False
		self.satelliteName = None
		self.mLongitude = 0
		self.mIsWest = 0
		self.mIsCBand = 0
		self.bandList = []

		property = ElisPropertyEnum( 'Band', self.mCommander )
		self.bandList.append( property.GetPropStringByIndex( 0 ) )
		self.bandList.append( property.GetPropStringByIndex( 1 ) )
		
	def onInit( self ) :
		self.mLongitude = 0
		self.SetHeaderLabel( 'Add New Satellite' )
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

		if groupId == E_DialogSpinEx01 :
			self.mIsWest = self.GetSelectedIndex( E_DialogSpinEx01 )

		elif groupId == E_DialogInput02 :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_SATELLITE_NUMERIC )
 			dialog.SetProperty( 'Set Longitude', self.mLongitude )
 			dialog.doModal( )

 			if dialog.IsOK() == True :
	 			self.mLongitude  = dialog.GetNumber( )
	 			self.DrawItem( )

		elif groupId == E_DialogSpinEx02 :
			self.mIsCBand = self.GetSelectedIndex( E_DialogSpinEx02 )

		elif groupId == E_DialogInput01 :
			kb = xbmc.Keyboard( self.satelliteName, 'Input Satellite Name', False )
			kb.doModal( )
			if( kb.isConfirmed( ) ) :
				value =  kb.getText( )
				if value == None or value == '' :
					return
				self.satelliteName = value
				self.DrawItem( )

		elif groupId == E_SettingDialogOk :
			self.mIsOk = True
			self.ResetAllControl( )
			self.CloseDialog( )

		elif groupId == E_SettingDialogCancel :
			self.mIsOk = False
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
		return self.mLongitude, self.mBand, self.satelliteName


	def DrawItem( self ) :
		self.ResetAllControl( )
	
		if self.satelliteName == None :
			self.satelliteName = 'No Name'
		self.AddInputControl( E_DialogInput01, 'Satellite Name', self.satelliteName, 4, 15 )
		self.AddUserEnumControl( E_DialogSpinEx01, 'Longitude Direction', E_LIST_MY_LONGITUDE, self.mIsWest )

		tmplongitude = '%03d.%d' % ( ( self.mLongitude / 10 ), self.mLongitude % 10 )
		self.AddInputControl( E_DialogInput02, 'Longitude Angle',  tmplongitude, 6 )
		self.AddUserEnumControl( E_DialogSpinEx02, 'Band Type', self.bandList, self.mIsCBand )
		self.AddOkCanelButton( )

		self.InitControl( )
