
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
E_BUTTON_START				= 200
E_BUTTON_CANCEL				= 201
E_PROGRESS_EPG				= 400
E_BUTTON_DURATION			= 501
E_LABEL_DURATION			= 502



class DialogStartRecord( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )

	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		self.SetHeaderLabel( 'Record' )

		self.mCtrlProgress = self.getControl( E_PROGRESS_EPG )
		self.mLocalOffset = self.mCommander.Datetime_GetLocalOffset()
		
		self.mLocalTime = self.mCommander.Datetime_GetLocalTime( )
		self.mRecordName = 'RecordName'

		self.mHasEPG = False
		self.mEPG = None

		self.Reload( )

		self.UpdateEPGTime( )

		self.mEventBus.Register( self )
		
		self.mEnableThread = True
		self.CurrentTimeThread( )


	def onAction( self, aAction ):
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		self.GlobalAction( actionId )		

		LOG_TRACE( 'actionId=%d' %actionId )
			
		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.Close()		

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
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
		if focusId == E_BUTTON_START :
			self.StartRecord( )			

		elif focusId == E_BUTTON_CANCEL :
			self.Close( )
		elif focusId == E_BUTTON_DURATION :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( 'Duration(Min)', '%d' %int(self.mRecordDuration/60) , 3 )
 			dialog.doModal( )
 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				duration = int( dialog.GetString( ) )
				LOG_TRACE('Duration=%d' %duration )

				if duration > 0 :
					self.mRecordDuration = duration*60
					self.UpdateEPGTime()

			


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

	def Close( self ):
		self.mEventBus.Deregister( self )
		self.mEnableThread = False
		self.CurrentTimeThread().join()
		self.CloseDialog( )


	def Reload ( self ) :

		self.mEPG=self.mCommander.Epgevent_GetPresent( )

		self.mRecordStartTime = self.mLocalTime - self.mLocalOffset
		
		if self.mEPG != None and self.mEPG.mError == 0:
			self.mEPG.printdebug( )		

			startTime =  self.mEPG.mStartTime + self.mLocalOffset
			endTime = startTime + self.mEPG.mDuration

			self.mRecordDuration = endTime - self.mLocalTime
			self.mRecordName = self.mEPG.mEventName

			LOG_TRACE('START : %s' %TimeToString( startTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
			LOG_TRACE('CUR : %s' %TimeToString( self.mLocalTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )			
			LOG_TRACE('END : %s' %TimeToString( endTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )			

			#Check Valid EPG
			if startTime < self.mLocalTime and self.mLocalTime < endTime :
				self.mHasEPG = True
				self.getControl( E_LABEL_RECORD_NAME ).setLabel( '(%s~%s)%s' %(TimeToString( startTime, TimeFormatEnum.E_HH_MM ), TimeToString( endTime, TimeFormatEnum.E_HH_MM ) , self.mRecordName) )
				



		if self.mHasEPG == False :
			prop = ElisPropertyEnum( 'Default Rec Duration', self.mCommander )
			self.mRecordDuration = prop.GetProp( )
			channel = self.mCommander.Channel_GetCurrent( )
			self.mRecordName = channel.mName
			self.getControl( E_LABEL_RECORD_NAME ).setLabel( self.mRecordName )
		
	
	def StartRecord( self ):
		LOG_TRACE('')

		current = self.mCommander.Channel_GetCurrent( )
		ret = self.mCommander.Timer_AddOTRTimer( self.mHasEPG, self.mRecordDuration, 0,  self.mRecordName,  0,  0,  0,  0,  0)
					
		self.Close( )

		if ret == False :
			xbmcgui.Dialog().ok('Failure', 'Start Record Fail' )



	@RunThread
	def CurrentTimeThread(self):
		loop = 0

		while self.mEnableThread:
			if  ( loop % 10 ) == 0 :
				LOG_TRACE( 'loop=%d' %loop )
				self.mLocalTime = self.mCommander.Datetime_GetLocalTime( )

				
			self.UpdateEPGTime( )

			time.sleep(1)
			self.mLocalTime += 1			
			loop += 1


	@GuiLock	
	def UpdateEPGTime( self ):
		self.UpdateProgress( )


	def UpdateProgress( self ):

		startTime = self.mRecordStartTime+ self.mLocalOffset
		endTime =  startTime  + self.mRecordDuration

		passDuration = self.mLocalTime - startTime

		LOG_TRACE( 'UpdateProgress=%d' %passDuration )

		self.getControl( E_LABEL_EPG_START_TIME ).setLabel( TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
		self.getControl( E_LABEL_EPG_END_TIME ).setLabel( TimeToString( endTime, TimeFormatEnum.E_HH_MM ) )
		self.getControl( E_LABEL_DURATION ).setLabel( '%d(Min)' % int( self.mRecordDuration/(60) ) )			


		if endTime < self.mLocalTime : #Already past
			self.mCtrlProgress.setPercent( 100 )
			return
		elif self.mLocalTime < startTime :
			passDuration = 0

		if passDuration < 0 :
			passDuration = 0

		if self.mRecordDuration > 0 :
			percent = passDuration * 100/self.mRecordDuration
		else :
			percent = 0

		LOG_TRACE( 'percent=%d' %percent )
		
		self.mCtrlProgress.setPercent( percent )


