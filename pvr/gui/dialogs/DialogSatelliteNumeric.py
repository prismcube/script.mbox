import xbmc
import xbmcgui
import sys

from pvr.gui.BaseDialog import BaseDialog
from pvr.gui.BaseWindow import Action
from pvr.gui.GuiConfig import *

E_INPUT_LABEL			= 4
E_DIALOG_HEADER			= 1
E_BUTTON_DONE			= 201
E_BUTTON_BACK_SPACE		= 200
E_BUTTON_PREV			= 202
E_BUTTON_NEXT			= 203

E_START_ID_NUMBER		= 100

class DialogSatelliteNumeric( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		
		self.mTitleLabel = ''
		self.mCursor = 0
		self.mCtrlEditLabel = 0
		self.mIsOk = E_DIALOG_STATE_NO
		self.mInput1 = 0
		self.mInput2 = 0
		self.mInput3 = 0
		self.mInput4 = 0


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		
		self.mIsOk = E_DIALOG_STATE_NO
		self.mCursor = 0
		self.getControl( E_DIALOG_HEADER ).setLabel( self.GetTitleLabel( ) )
		self.mCtrlEditLabel = self.getControl( E_INPUT_LABEL )
		self.SetInputLabel( )
		self.DrawKeyboard( )
		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.CloseDialog( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 :		# number
			self.InputControl( actionId, 1 )
			self.SetInputLabel( )

		elif actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :
			self.InputControl( actionId, 2 )
			self.SetInputLabel( )
			
		elif actionId == Action.ACTION_PARENT_DIR : 							# back space
			self.DeleteValue( )
			self.SetInputLabel( )

	def onClick( self, aControlId ) :
		if aControlId >= E_START_ID_NUMBER and aControlId <= 109 :
			self.InputControl( aControlId, 0 )

		elif aControlId == E_BUTTON_BACK_SPACE :
			self.DeleteValue( )
			self.SetInputLabel( )
		
		elif aControlId == E_BUTTON_PREV :
			self.PrevCursor( )
			
		elif aControlId == E_BUTTON_NEXT :
			self.NextCursor( )
			
		elif aControlId == E_BUTTON_DONE :
			self.mIsOk = E_DIALOG_STATE_YES
			self.CloseDialog( )

		self.SetInputLabel( )


	def IsOK( self ) :
		return self.mIsOk

	def onFocus( self, aControlId ):
		pass


	def DrawKeyboard( self ):
		for i in range( 10 ) :
			self.getControl( E_START_ID_NUMBER + i ).setLabel( '%s' % i )

	def GetNumber( self ) :
		value = self.mInput1 * 1000 + self.mInput2 * 100 + self.mInput3 * 10 + self.mInput4
		return value

	def GetTitleLabel( self ) :
		return self.mTitleLabel
		
	def SetDialogProperty( self, aTitle, aValue ) :
		self.mTitleLabel = aTitle
		
		self.mInput4 = aValue % 10
		aValue = aValue / 10
		self.mInput3 = aValue % 10
		aValue = aValue / 10
		self.mInput2 = aValue % 10
		aValue = aValue / 10
		self.mInput1 = aValue


	def SetInputLabel( self ) :
		if self.mCursor == 0 :
			tmp = '[COLOR selected]%d[/COLOR]%d%d.%d' % ( self.mInput1, self.mInput2, self.mInput3, self.mInput4 ) 

		elif self.mCursor == 1 :
			tmp = '%d[COLOR selected]%d[/COLOR]%d.%d' % ( self.mInput1, self.mInput2, self.mInput3, self.mInput4 ) 

		elif self.mCursor == 2 :
			tmp = '%d%d[COLOR selected]%d[/COLOR].%d' % ( self.mInput1, self.mInput2, self.mInput3, self.mInput4 ) 

		elif self.mCursor == 3 :
			tmp = '%d%d%d.[COLOR selected]%d[/COLOR]' % ( self.mInput1, self.mInput2, self.mInput3, self.mInput4 )

		else :
			return
				
		self.mCtrlEditLabel.setLabel( tmp )


	def InputControl( self, aControlId, aInputtype ) :
		if aInputtype == 0 :
			value = int( self.getControl( aControlId ).getLabel( ) )
			
		elif aInputtype == 1 :
			tmp = chr( aControlId - 10 )
			value = int( tmp )

		elif aInputtype == 2 :
			tmp = chr( aControlId - 92 )
			value = int( tmp )

		else :
			return
			
		if self.mCursor == 0 and value < 2 :
			self.mInput1 = value
			self.NextCursor( )

		elif self.mCursor == 1 and value < 8 :
			self.mInput2 = value
			self.NextCursor( )

		elif self.mCursor == 2 :
			self.mInput3 = value
			self.NextCursor( )
 
		elif self.mCursor == 3 :
			self.mInput4 = value
			self.NextCursor( )
 
		else :
			return


	def DeleteValue( self ) :
		if self.mCursor == 0 :
			self.mInput1 = 0
			self.PrevCursor( )

		elif self.mCursor == 1 :
			self.mInput2 = 0
			self.PrevCursor( )

		elif self.mCursor == 2 :
			self.mInput3 = 0
			self.PrevCursor( )
 
		elif self.mCursor == 3 :
			self.mInput4 = 0
			self.PrevCursor( )
 
		else :
			return



	def NextCursor( self ) :
		if self.mCursor == 3 :
				self.mCursor = 0
		else :
			self.mCursor = self.mCursor + 1


	def PrevCursor( self ) :
		if self.mCursor == 0 :
				self.mCursor = 3
		else :
			self.mCursor = self.mCursor - 1

		
