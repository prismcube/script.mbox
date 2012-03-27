
import xbmc
import xbmcgui
import time
import sys


from pvr.gui.BaseDialog import BaseDialog
from pvr.gui.BaseWindow import Action
from  pvr.TunerConfigMgr import *
from ElisEnum import ElisEnum
import pvr.gui.DialogMgr as DiaMgr

import pvr.ElisMgr

from pvr.Util import RunThread, GuiLock, LOG_TRACE, LOG_WARN, LOG_ERR, TimeToString, TimeFormatEnum
from pvr.gui.GuiConfig import *


# Control IDs
E_LABEL_RECORD_NAME			= 101
E_LABEL_EPG_START_TIME		= 102
E_LABEL_EPG_END_TIME		= 103
E_BUTTON_ADD				= 200
E_BUTTON_CANCEL				= 201



class DialogAddTimer( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mEPG = None

	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		self.SetHeaderLabel( 'Add Recording' )
		self.mIsOk = E_DIALOG_STATE_CANCEL		

		self.Reload( )
		self.mEventBus.Register( self )
		

	def onAction( self, aAction ):
		actionId = aAction.getId( )
		focusId = self.GetFocusId( )
		self.GlobalAction( actionId )		

		LOG_TRACE( 'actionId=%d' %actionId )
			
		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.Close()		

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.Close()

		elif actionId == Action.ACTION_MOVE_UP :
			pass
	
		elif actionId == Action.ACTION_MOVE_DOWN :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT :
			pass
				
		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass
		else :
			LOG_WARN( 'Unknown Action' )


	def onClick( self, aControlId ):
		focusId = self.getFocusId( )

		LOG_TRACE( 'DialogRecord focusId=%d' %focusId )
		if focusId == E_BUTTON_ADD :
			self.mIsOk = E_DIALOG_STATE_YES
			self.Close( )

		elif focusId == E_BUTTON_CANCEL :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.Close( )


	def onFocus( self, aControlId ):
		pass


	@GuiLock	
	def onEvent( self, aEvent ):
		pass
		"""
		if xbmcgui.getCurrentWindowId() == self.winId :
			print 'Do Event'
			pass
		"""


	def SetEPG( self, aEPG ):
		self.mEPG = aEPG


	def IsOK( self ) :
		return self.mIsOk


	def Close( self ):
		self.mEventBus.Deregister( self )
		self.CloseDialog( )


	def Reload ( self ) :
		LOG_TRACE('')


		try :
			if self.mEPG != None and self.mEPG.mError == 0:
				self.mEPG.printdebug( )		

				localOffset = self.mDataCache.Datetime_GetLocalOffset()
				localTime = self.mDataCache.Datetime_GetLocalTime( )

				startTime = self.mEPG.mStartTime + localOffset
				endTime =  startTime  + self.mEPG.mDuration
			

				LOG_TRACE('START : %s' %TimeToString( startTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
				LOG_TRACE('CUR : %s' %TimeToString( localTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )			
				LOG_TRACE('END : %s' %TimeToString( endTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )			
				self.getControl( E_LABEL_RECORD_NAME ).setLabel( '%s' %self.mEPG.mEventName )

				self.getControl( E_LABEL_EPG_START_TIME ).setLabel( 'Start : %s' %TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
				self.getControl( E_LABEL_EPG_END_TIME ).setLabel( 'End : %s' %TimeToString( endTime, TimeFormatEnum.E_HH_MM ) )
			
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex)


	"""
	def AddRecord( self ):
		LOG_TRACE('')

		ret = self.mDataCache.Timer_AddEPGTimer( self.mEPG )
		self.Close( )

		if ret == False :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			xbmcgui.Dialog().ok('Failure', 'Start Record Fail' )

	"""
	