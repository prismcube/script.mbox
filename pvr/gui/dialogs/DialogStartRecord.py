
import xbmc
import xbmcgui
import time
import sys


from pvr.gui.BaseDialog import BaseDialog
from pvr.gui.BaseWindow import Action
from  pvr.TunerConfigMgr import *
from ElisEnum import ElisEnum
from pvr.PublicReference import EpgInfoClock

import pvr.ElisMgr

from pvr.Util import RunThread, GuiLock, LOG_TRACE, LOG_WARN, LOG_ERR



# Control IDs
E_LABEL_RECORD_NAME			= 101
E_PROGRESS_EPG				= 400
E_LABEL_EPG_START_TIME		= 102
E_LABEL_EPG_END_TIME		= 103
E_BUTTON_DURATION			= 501
E_LABEL_DURATION			= 502
E_BUTTON_START				= 201
E_BUTTON_CANCEL				= 301




class DialogStartRecord( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.mEventBus = pvr.ElisMgr.GetInstance().GetEventBus()

	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		self.mCtrlProgress = self.getControl( E_PROGRESS_EPG )
		self.mLocalOffset = self.mCommander.Datetime_GetLocalOffset()
		
		self.mLocalTime = self.mCommander.Datetime_GetLocalTime( )
		self.mRecordName = 'RecordName'

		epg=self.mCommander.Epgevent_GetPresent( )
		self.mHasEPG = False

		if epg:
			self.mEPGStartTime = epg.mStartTime #EPG Start Time		
			self.mEPGDuration = epg.mDuration #EPG Duration
			self.mRecordName = epg.mEventName

			#Check Valid EPG
			startTime =  self.mEPGStartTime + self.mLocalOffset
			endTime = startTime + self.mEPGDuration


			if startTime < self.mLocalTime and self.mLocalTime < endTime :
				self.mHasEPG = True


		if self.mHasEPG == False :
			prop = ElisPropertyEnum( 'Default Rec Duration', self.mCommander )
			self.mEPGDuration = prop.GetProp( )
			self.mEPGStartTime = self.mLocalTime - self.mLocalOffset
			channel = self.mCommander.Channel_GetCurrent( )
			self.mRecordName = channel.mName
		
		LOG_TRACE( 'RecordName=%s Duration=%d' %(self.mRecordName, self.mEPGDuration ) )

		self.getControl( E_LABEL_RECORD_NAME ).setLabel( self.mRecordName )

		self.UpdateEPGTime()

		self.mEventBus.Register( self )
		
		self.mEnableThread = True
		self.CurrentTimeThread( )


	def onAction( self, aAction ):
		actionId = aAction.getId( )
		focusId = self.getFocusId( )

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
		self.close( )


	def StartRecord( self ):
		LOG_TRACE('')
		current = self.mCommander.Channel_GetCurrent( )
		"""
		ret = self.mCommander.record_StartRecord( int( current[0] ),  int( current[3] ),  self.mEPGDuration,  self.mRecordName )
		print 'Record Result=%s' %ret
		"""

		self.Close( )


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
		startTime = self.mEPGStartTime+ self.mLocalOffset
		endTime =  startTime  + self.mEPGDuration

		passDuration = self.mLocalTime - startTime

		LOG_TRACE( 'mLocalOffset=%d' % int( self.mLocalOffset/60 ) )
		LOG_TRACE( 'start=%s' % EpgInfoClock( 1, startTime, 0 ) )
		LOG_TRACE( 'current=%s' % EpgInfoClock( 1,self.mLocalTime, 0 ) )
		LOG_TRACE( 'end=%s' % EpgInfoClock( 1, endTime, 0 ) )

		LOG_TRACE( 'UpdateProgress=%d' %passDuration )

		startTimeString = EpgInfoClock( 1, startTime, 0 )
		endTimeString = EpgInfoClock( 1, endTime, 0 )		

		self.getControl( E_LABEL_EPG_START_TIME ).setLabel( startTimeString[1] )
		self.getControl( E_LABEL_EPG_END_TIME ).setLabel( endTimeString[1] )

		if self.mHasEPG == True :
			recordDuration = endTime - self.mLocalTime
			if recordDuration < 0 :
				recordDuration = 0
			self.getControl( E_LABEL_DURATION ).setLabel( '%d Min' %int( recordDuration/(60) )  )
		else :
			self.getControl( E_LABEL_DURATION ).setLabel( '%d Min' % int( self.mEPGDuration/(60) ) )			


		if endTime < self.mLocalTime : #Already past
			passDuration = 100
		elif self.mLocalTime < startTime :
			passDuration = 0

		if passDuration < 0 :
			passDuration = 0

		if self.mEPGDuration > 0 :
			percent = passDuration * 100/self.mEPGDuration
		else :
			percent = 0

		LOG_TRACE( 'percent=%d' %percent )
		
		self.mCtrlProgress.setPercent( percent )


