import xbmc
import xbmcgui
import time
import sys

from pvr.gui.BaseDialog import BaseDialog
from pvr.gui.BaseWindow import Action


class DialogMoveAntenna( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		
		
	def onInit( self ) :
		#self.DrawItem( )
		self.mIsOk = False		

		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.CloseDialog( )


	def onClick( self, aControlId ) :
		"""
		if aControlId == E_MAIN_LIST_ID :
			if self.getControl( E_MAIN_LIST_ID ).getSelectedPosition( ) == 0 :
				self.mLowFreq = self.NumericKeyboard( 0, 'Low Frequency', self.mLowFreq, 5 )
				self.DrawItem( )

			elif self.getControl( E_MAIN_LIST_ID ).getSelectedPosition( ) == 1 :
				self.mHighFreq = self.NumericKeyboard( 0, 'High Frequency', self.mHighFreq, 5 )
				self.DrawItem( )
			
			elif self.getControl( E_MAIN_LIST_ID ).getSelectedPosition( ) == 2 :
				self.mThreshFreq = self.NumericKeyboard( 0, 'Switch Frequency', self.mThreshFreq, 5 )
				self.DrawItem( )
			
		elif aControlId ==  E_BUTTON_OK_ID :
			self.mIsOk = True
			self.CloseDialog( )
		
		elif aControlId == E_BUTTON_CANCEL_ID :
			self.mIsOk = False
			self.CloseDialog( )		
 		"""
 		pass
 		
	def IsOK( self ) :
		return self.mIsOk

		
	def onFocus( self, aControlId ):
		pass

	"""
	def DrawItem( self ) :
		listItems = []
		listItem = xbmcgui.ListItem( 'Low Frequency', self.mLowFreq, "-", "-", "-" )
		listItems.append( listItem )
		
		listItem = xbmcgui.ListItem( 'High Frequency', self.mHighFreq, "-", "-", "-" )
		listItems.append( listItem )
		
		listItem = xbmcgui.ListItem( 'Switch Frequency', self.mThreshFreq, "-", "-", "-" )
		listItems.append( listItem )

		self.getControl( E_MAIN_LIST_ID ).addItems( listItems )
	"""

