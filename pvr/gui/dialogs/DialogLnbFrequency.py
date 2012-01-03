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
				self.lowFreq = self.numericKeyboard( 0, 'Low Frequency', self.lowFreq, 5 )
				self.drawItem( )

			elif self.getControl( E_MAIN_LIST_ID ).getSelectedPosition( ) == 1 :
				self.highFreq = self.numericKeyboard( 0, 'High Frequency', self.highFreq, 5 )
				self.drawItem( )
			
			elif self.getControl( E_MAIN_LIST_ID ).getSelectedPosition( ) == 2 :
				self.threshFreq = self.numericKeyboard( 0, 'Switch Frequency', self.threshFreq, 5 )
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
