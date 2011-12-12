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
		self.listItems = []
		self.currentSatellite = []
		'''
		self.inputLabel = ''
		self.ctrlEditLabel = 0
		#self.cursorPosition = 0
		'''
		
	def onInit( self ) :
		self.getControl( E__DIALOG_HEADER ).setLabel( 'LNB Frequency' )

		self.currentSatellite = configmgr.getInstance( ).getCurrentConfiguredSatellite( )
		
		listItem = xbmcgui.ListItem( 'Low Frequency', self.currentSatellite[ E_CONFIGURE_SATELLITE_LOW_LNB ], "-", "-", "-" )
		self.listItems.append( listItem )
		listItem = xbmcgui.ListItem( 'High Frequency', self.currentSatellite[ E_CONFIGURE_SATELLITE_HIGH_LNB ], "-", "-", "-" )
		self.listItems.append( listItem )
		listItem = xbmcgui.ListItem( 'Switch Frequency', self.currentSatellite[ E_CONFIGURE_SATELLITE_LNB_THRESHOLD ], "-", "-", "-" )
		self.listItems.append( listItem )

		self.getControl( E_MAIN_LIST_ID ).addItems( self.listItems )
		
		'''
		self.getControl( E_DIALOG_HEADER ).setLabel( diamgr.getInstance().getTitleLabel( ) )
		#self.inputLabel = diamgr.getInstance().getDefaultText( )
		self.inputLabel = '1234'
		self.ctrlEditLabel = self.getControl( E_INPUT_LABEL )
		self.ctrlEditLabel.setLabel( self.inputLabel )
		self.drawKeyboard( )
		'''
		
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

		if( focusId == E_MAIN_LIST_ID ) :
			if self.getControl( E_MAIN_LIST_ID ).getSelectedPosition( ) == 0 :
				diamgr.getInstance().setTitleLabel( 'Low Frequency' )
				diamgr.getInstance().setDefaultText( self.currentSatellite[ E_CONFIGURE_SATELLITE_LOW_LNB ] )
				
			elif self.getControl( E_MAIN_LIST_ID ).getSelectedPosition( ) == 1 :
				diamgr.getInstance().setTitleLabel( 'High Frequency' )
				diamgr.getInstance().setDefaultText( self.currentSatellite[ E_CONFIGURE_SATELLITE_HIGH_LNB ] )
				
			elif self.getControl( E_MAIN_LIST_ID ).getSelectedPosition( ) == 2 :
				diamgr.getInstance().setTitleLabel( 'Switch Frequency' )
				diamgr.getInstance().setDefaultText( self.currentSatellite[ E_CONFIGURE_SATELLITE_LNB_THRESHOLD ] )
				
			diamgr.getInstance().showDialog( diamgr.DIALOG_ID_NUMERIC )
		
		'''
		if( focusId >= E_START_ID_NUMBER and focusId <= 19 ) :
			self.inputLabel += self.getControl( focusId ).getLabel( )

		elif( focusId == E_BUTTON_BACK_SPACE ) :
			self.inputLabel = self.inputLabel[ : len( self.inputLabel ) - 1 ]
		
		elif( focusId == E_BUTTON_PREV ) :
			pass

		elif( focusId == E_BUTTON_NEXT ) :
			pass

		elif( focusId == E_BUTTON_DONE ) :
			diamgr.getInstance().setResultText( self.ctrlEditLabel.getLabel( ) )
			self.close( )
		self.ctrlEditLabel.setLabel( self.inputLabel )
		'''
	def onFocus( self, controlId ):
		pass

