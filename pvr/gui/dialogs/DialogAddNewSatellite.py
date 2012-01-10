import xbmc
import xbmcgui
import time
import sys

import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.BaseDialog import BaseDialog
from pvr.gui.BaseWindow import Action
from ElisEnum import ElisEnum
from pvr.gui.GuiConfig import *

from pvr.Util import LOG_WARN, LOG_TRACE, LOG_ERR


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

class DialogAddNewSatellite( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )

		self.mLongitude = None
		self.mBand = None
		self.mIsOk = False
		self.mCtrlLongitudeList = None
		self.mCtrlBandList = None
		self.mLongitude = 0
		self.mBand = 0
		self.mIsWest = 0
		self.mIsCBand = 0

		
	def onInit( self ) :
		
		self.getControl( E_DIALOG_HEADER ).setLabel( 'New Satellite' )
		
		self.mCtrlLongitudeList = self.getControl( E_LONGITUDE_LIST )
		self.mCtrlBandList		= self.getControl( E_BAND_LIST )

		self.mLongitude = 0
		self.DrawItem( )
		self.mIsOk = False

		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.CloseDialog( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.CloseDialog( )


	def onClick( self, aControlId ) :
		if aControlId ==  E_BUTTON_OK_ID :
			self.mIsOk = True
			self.CloseDialog( )
		
		elif aControlId == E_BUTTON_CANCEL_ID :
			self.mIsOk = False
			self.CloseDialog( )

		elif aControlId == E_BAND_NEXT or aControlId == E_BAND_PREV :
			if self.mIsCBand == 0 :
				self.mIsCBand = 1
			else :
				self.mIsCBand = 0

		elif aControlId == E_LONGITUDE_NEXT or aControlId == E_LONGITUDE_PREV :
			if self.mIsWest == 0 :
				self.mIsWest = 1
			else :
				self.mIsWest = 0
				
		elif aControlId == E_EDIT_LONGITUDE_BUTTON :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_SATELLITE_NUMERIC )
 			dialog.SetProperty( 'Set Longitude', self.mLongitude )
 			dialog.doModal( )

 			if dialog.IsOK() == True :
	 			self.mLongitude  = dialog.GetNumber( )
	 			self.DrawItem( )

 				
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
		return self.mLongitude, self.mBand


	def DrawItem( self ) :

		tmpList = []
		tmplongitude1 = '%d.%d %s' % ( self.mLongitude / 10, self.mLongitude % 10, E_LIST_MY_LONGITUDE[ 0 ] )
		tmplongitude2 = '%d.%d %s' % ( self.mLongitude / 10, self.mLongitude % 10, E_LIST_MY_LONGITUDE[ 1 ] )
		tmpList.append( xbmcgui.ListItem( 'Longitude', tmplongitude1, "-", "-", "-" ) )
		tmpList.append( xbmcgui.ListItem( 'Longitude', tmplongitude2, "-", "-", "-" ) )
		self.mCtrlLongitudeList.addItems( tmpList )
		self.mCtrlLongitudeList.selectItem( self.mIsWest )

		tmpList = []
		tmpList.append( xbmcgui.ListItem( 'Band Type', 'KU Band', "-", "-", "-" ) )
		tmpList.append( xbmcgui.ListItem( 'Band Type', 'C Band', "-", "-", "-" ) )
		self.mCtrlBandList.addItems( tmpList )
		self.mCtrlBandList.selectItem( self.mIsCBand )