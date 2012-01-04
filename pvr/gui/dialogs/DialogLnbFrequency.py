import xbmc
import xbmcgui
import time
import sys

from pvr.gui.BaseDialog import BaseDialog
from pvr.gui.BaseWindow import Action
import pvr.gui.DialogMgr as DiaMgr
import pvr.TunerConfigMgr as ConfigMgr
from pvr.TunerConfigMgr import *

E_DIALOG_HEADER		= 100
E_MAIN_LIST_ID			= 101

E_BUTTON_OK_ID			= 201
E_BUTTON_CANCEL_ID		= 301

class DialogLnbFrequency( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )

		self.mLowFreq = None
		self.mHighFreq = None
		self.mThreshFreq = None
		self.mIsOk = False

		
	def onInit( self ) :
		self.getControl( E_DIALOG_HEADER ).setLabel( 'LNB Frequency' )
		self.DrawItem( )
		self.mIsOk = False		

		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )


		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.close( )


	def onClick( self, aControlId ):
		focusId = self.getFocusId( )

		if focusId == E_MAIN_LIST_ID :
			if self.getControl( E_MAIN_LIST_ID ).getSelectedPosition( ) == 0 :
				self.mLowFreq = self.NumericKeyboard( 0, 'Low Frequency', self.mLowFreq, 5 )
				self.DrawItem( )

			elif self.getControl( E_MAIN_LIST_ID ).getSelectedPosition( ) == 1 :
				self.mHighFreq = self.NumericKeyboard( 0, 'High Frequency', self.mHighFreq, 5 )
				self.DrawItem( )
			
			elif self.getControl( E_MAIN_LIST_ID ).getSelectedPosition( ) == 2 :
				self.mThreshFreq = self.NumericKeyboard( 0, 'Switch Frequency', self.mThreshFreq, 5 )
				self.DrawItem( )
			
		elif focusId ==  E_BUTTON_OK_ID :
			self.mIsOk = True
			self.close( )
		
		elif focusId == E_BUTTON_CANCEL_ID :
			self.mIsOk = False
			self.close( )				
 				
	def IsOK( self ) :
		return self.mIsOk
		
	def onFocus( self, aControlId ):
		pass

	def SetFrequency( self, aLowFreq, aHighFreq, aThreshFreq ) :
		self.mLowFreq = aLowFreq
		self.mHighFreq = aHighFreq
		self.mThreshFreq = aThreshFreq


	def GetFrequency( self ) :
		return self.mLowFreq, self.mHighFreq, self.mThreshFreq

	def DrawItem( self ) :
		listItems = []
		listItem = xbmcgui.ListItem( 'Low Frequency', self.mLowFreq, "-", "-", "-" )
		listItems.append( listItem )
		
		listItem = xbmcgui.ListItem( 'High Frequency', self.mHighFreq, "-", "-", "-" )
		listItems.append( listItem )
		
		listItem = xbmcgui.ListItem( 'Switch Frequency', self.mThreshFreq, "-", "-", "-" )
		listItems.append( listItem )

		self.getControl( E_MAIN_LIST_ID ).addItems( listItems )
