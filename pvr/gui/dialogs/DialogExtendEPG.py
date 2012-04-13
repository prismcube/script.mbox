import xbmc
import xbmcgui
import time
import sys

from pvr.gui.BaseDialog import BaseDialog
from pvr.gui.BaseWindow import Action
from pvr.gui.GuiConfig import *
from pvr.Util import RunThread, GetImageByEPGComponent, GuiLock, GuiLock2, LOG_TRACE, LOG_WARN, LOG_ERR, GetSetting, SetSetting, TimeToString, TimeFormatEnum
from ElisEnum import ElisEnum


TEXTBOX_ID_TITLE					= 100
TEXTBOX_ID_DESCRIPTION				= 101
LABEL_ID_DATE						= 300


class DialogExtendEPG( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )	
		self.mEPG = None
		

	def onInit( self ) :
		LOG_TRACE('')
		self.mWinId = xbmcgui.getCurrentWindowDialogId()
		self.mWin = xbmcgui.WindowDialog( self.mWinId )


		self.mWin.setProperty( 'EPGTitle', self.mEPG.mEventName )
		self.mWin.setProperty( 'EPGDescription', self.mEPG.mEventDescription )

		if self.mEPG.mHasHDVideo :
			self.mWin.setProperty( 'HasHD', 'true' )
		else :
			self.mWin.setProperty( 'HasHD', 'false' )			
		
		if self.mEPG.mHasDolbyDigital :
			self.mWin.setProperty( 'HasDolby', 'true' )
		else :
			self.mWin.setProperty( 'HasDolby', 'false' )

		if self.mEPG.mHasSubtitles :
			self.mWin.setProperty( 'HasSubtitle', 'true' )
		else :
			self.mWin.setProperty( 'HasSubtitle', 'false' )

		
		self.mCtrlTitle = self.getControl( TEXTBOX_ID_TITLE )
		self.mCtrlDescription = self.getControl( TEXTBOX_ID_DESCRIPTION )
		self.mCtrlDate = self.getControl( TEXTBOX_ID_DESCRIPTION )		
	

	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.CloseDialog( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
			
		elif actionId == Action.ACTION_PARENT_DIR :
			self.CloseDialog( )
			

	def onClick( self, aControlId ) :
		LOG_TRACE('')	
		pass


	def onFocus( self, aControlId ) :
		pass
		

	def SetEPG( self, aEPG ) :
		LOG_TRACE('')	
		self.mEPG = aEPG
		
		
