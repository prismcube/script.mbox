import xbmc
import xbmcgui
import time
import sys

from pvr.gui.BaseDialog import BaseDialog
from pvr.gui.BaseWindow import Action
from pvr.gui.GuiConfig import *

DIALOG_MAIN_GROUP_ID		= 9000
DIALOG_WIDTH				= 370

DIALOG_MIDDLE_IMAGE_ID		= 100
DIALOG_BOTTOM_IMAGE_ID		= 101

DIALOG_LIST_ID				= 102
DIALOG_BUTTON_CLOSE_ID		= 103


class DialogContext( BaseDialog ) :

	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )	
		self.mItemList = []
		self.mSelectedIndex = -1
		self.mCtrlList = None


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mCtrlList = self.getControl( DIALOG_LIST_ID )
		for i in range( len( self.mItemList ) ) :
			self.mCtrlList.addItem( self.mItemList[i].mDescription )

		# Set Dialog Size
		height = len ( self.mItemList ) * 38
		self.getControl( DIALOG_MIDDLE_IMAGE_ID ).setHeight( height )

		# Set Dialog Bottom Image
		middle_y, empty = self.getControl( DIALOG_MIDDLE_IMAGE_ID ).getPosition( )
		middley_height = self.getControl( DIALOG_MIDDLE_IMAGE_ID ).getHeight()
		self.getControl( DIALOG_BOTTOM_IMAGE_ID ).setPosition( 0, middle_y + middley_height )

		# Set Center Align
		start_x = E_WINDOW_WIDTH / 2 - DIALOG_WIDTH / 2
		start_y = E_WINDOW_HEIGHT / 2 - middley_height / 2
		self.getControl( DIALOG_MAIN_GROUP_ID ).setPosition( start_x, start_y )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.CloseDialog( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
			
		elif actionId == Action.ACTION_PARENT_DIR :
			self.CloseDialog( )
			

	def onClick( self, aControlId ) :
		if aControlId == DIALOG_BUTTON_CLOSE_ID :
			self.CloseDialog( )
			self.mSelectedIndex = -1

		self.mSelectedIndex = self.mCtrlList.getSelectedPosition( )
		self.CloseDialog( )		


	def onFocus( self, aControlId ) :
		pass


	def SetProperty( self, aItemList ) :
		self.mItemList = aItemList
			
		if len( self.mItemList ) == 0 :
			self.mItemList.append( ContextItem( 'None' ) )


	def GetSelectedAction( self ) :
		if self.mSelectedIndex <  0 :
			return -1
			
		if self.mItemList == None or len( self.mItemList ) <= 0 :
			return -1
		
		return self.mItemList[self.mSelectedIndex].mContextAction
		
	