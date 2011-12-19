import xbmc
import xbmcgui
import time
import sys

from pvr.gui.basedialog import BaseDialog
from pvr.gui.basewindow import Action
import pvr.gui.dialogmgr as diamgr
import pvr.tunerconfigmgr as configmgr
from pvr.tunerconfigmgr import *


E__DIALOG_HEADER		= 100
E_MAIN_LIST_ID			= 101

E_BUTTON_OK_ID			= 201
E_BUTTON_CANCEL_ID		= 301

'''
E_BUTTON_DONE			= 21
E_BUTTON_BACK_SPACE		= 23
E_BUTTON_PREV			= 20
E_BUTTON_NEXT			= 22

E_START_ID_NUMBER		= 10
'''
class DialogLnbFrequency( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )

		self.lowFreq = None
		self.highFreq = None
		self.threshFreq = None
		self.isOk = False

		
	def onInit( self ) :
		self.getControl( E__DIALOG_HEADER ).setLabel( 'LNB Frequency' )
		self.drawItem( )
		self.isOk = False		

		
	def onAction( self, action ) :
		actionId = action.getId( )
		focusId = self.getFocusId( )


		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.listItems = []
			self.close( )


	def onClick( self, controlId ):
		focusId = self.getFocusId( )

		print 'dialoglnb frequency focus id=%d' %focusId

		if( focusId == E_MAIN_LIST_ID ) :
			if self.getControl( E_MAIN_LIST_ID ).getSelectedPosition( ) == 0 :
				dialog = diamgr.getInstance().getDialog( diamgr.DIALOG_ID_NUMERIC )
				dialog.setTiteLabel( 'Low Frequency' )
				dialog.setNumber( self.lowFreq )
 				dialog.doModal( )

				if dialog.isOK() == True :
	 				self.lowFreq = dialog.getNumber( )
	 				self.drawItem( )
 
			elif self.getControl( E_MAIN_LIST_ID ).getSelectedPosition( ) == 1 :
				dialog = diamgr.getInstance().getDialog( diamgr.DIALOG_ID_NUMERIC )
				dialog.setTiteLabel( 'High Frequency' )
				dialog.setNumber( self.highFreq )
 				dialog.doModal( )

				if dialog.isOK() == True :
					self.highFreq = dialog.getNumber( )
	 				self.drawItem( )
				
			elif self.getControl( E_MAIN_LIST_ID ).getSelectedPosition( ) == 2 :
				dialog = diamgr.getInstance().getDialog( diamgr.DIALOG_ID_NUMERIC )
				dialog.setTiteLabel( 'Switch Frequency' )
				dialog.setNumber( self.threshFreq )
 				dialog.doModal( )

				if dialog.isOK() == True :
	 				self.threshFreq = dialog.getNumber( )
	 				self.drawItem( )
 				
		elif focusId ==  E_BUTTON_OK_ID :
			self.isOk = True
			self.close( )
		
		elif focusId == E_BUTTON_CANCEL_ID :
			self.isOk = False
			self.close( )				
 				
	def isOK( self ) :
		return self.isOk
		
	def onFocus( self, controlId ):
		pass

	def setFrequency( self, lowFreq, highFreq, threshFreq ) :
		self.lowFreq = lowFreq
		self.highFreq = highFreq
		self.threshFreq = threshFreq


	def getFrequency( self ) :
		return self.lowFreq, self.highFreq, self.threshFreq

	def drawItem( self ) :
		listItems = []
		listItem = xbmcgui.ListItem( 'Low Frequency', self.lowFreq, "-", "-", "-" )
		listItems.append( listItem )
		
		listItem = xbmcgui.ListItem( 'High Frequency', self.highFreq, "-", "-", "-" )
		listItems.append( listItem )
		
		listItem = xbmcgui.ListItem( 'Switch Frequency', self.threshFreq, "-", "-", "-" )
		listItems.append( listItem )

		self.getControl( E_MAIN_LIST_ID ).addItems( listItems )
