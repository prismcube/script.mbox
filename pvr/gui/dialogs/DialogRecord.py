
import xbmc
import xbmcgui
import time
import sys


from pvr.gui.BaseWindow import Action
from pvr.gui.BaseDialog import BaseDialog
from  pvr.TunerConfigMgr import *
import pvr.gui.DialogMgr as diamgr
from elisevent import ElisEvent
from ElisEnum import ElisEnum

import pvr.ElisMgr

from pvr.Util import RunThread, GuiLock, epgInfoClock



# Control IDs
E_LABEL_RECORD_NAME			= 101
E_PROGRESS_EPG				= 400
E_LABEL_EPG_START_TIME		= 102
E_LABEL_EPG_END_TIME		= 103
E_BUTTON_DURATION			= 501
E_LABEL_DURATION			= 502
E_BUTTON_START				= 201
E_BUTTON_CANCEL				= 301




class DialogRecord( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mCommander = pvr.ElisMgr.getInstance( ).getCommander( )
		self.mEventBus = pvr.ElisMgr.getInstance().getEventBus()

	def onInit( self ):
		self.winId = xbmcgui.getCurrentWindowId()

		self.mCtrlProgress = self.getControl( E_PROGRESS_EPG )
		
		self.mLocalOffset = int( self.mCommander.datetime_GetLocalOffset()[0] )
		
		localTime = self.mCommander.datetime_GetLocalTime( )
		self.mLocalTime = int( localTime[0] )
		self.mRecordName = 'RecordName'

		epg=self.mCommander.epgevent_GetPresent( )
		
		print 'epg=%s' %epg
		self.mHasEPG = False
		
		if epg != []:
			self.mEPGStartTime = int( epg[5] ) #EPG Start Time		
			self.mEPGDuration = int( epg[6] ) #EPG Duration
			self.mRecordName = epg[1]

			#Check Valid EPG
			startTime =  self.mEPGStartTime + self.mLocalOffset
			endTime = startTime + self.mEPGDuration


			if startTime < self.mLocalTime and self.mLocalTime < endTime :
				self.mHasEPG = True


		if self.mHasEPG == False :
			prop = ElisPropertyEnum( 'Default Rec Duration', self.mCommander )
			self.mEPGDuration = prop.getProp( )
			self.mEPGStartTime = self.mLocalTime - self.mLocalOffset
			channel = self.mCommander.channel_GetCurrent( )
			self.mRecordName = channel[2]
		
		print 'RecordName=%s Duration=%d' %(self.mRecordName, self.mEPGDuration )

		self.getControl( E_LABEL_RECORD_NAME ).setLabel( self.mRecordName )

		self.UpdateEPGTime()

		self.mEventBus.register( self )
		
		self.mEnableThread = True
		self.CurrentTimeThread( )


	@GuiLock
	def onAction( self, action ):
		actionId = action.getId( )
		focusId = self.getFocusId( )
	
		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
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
			print 'Unknown Action'


	@GuiLock	
	def onClick( self, controlId ):
		focusId = self.getFocusId( )

		print 'DialogRecord focusId=%d' %focusId
		if focusId == E_BUTTON_START :
			self.StartRecord( )			

		elif focusId == E_BUTTON_CANCEL :
			self.Close( )


	@GuiLock
	def onFocus( self, controlId ):
		pass


	@GuiLock	
	def onEvent( self, event ):
		if xbmcgui.getCurrentWindowId() == self.winId :
			print 'Do Event'
			pass

	def Close( self ):
		self.mEventBus.deregister( self )
		self.mEnableThread = False
		self.CurrentTimeThread().join()
		self.close( )


	def StartRecord( self ):
		print 'Start Record'
		current = self.mCommander.channel_GetCurrent( )
		ret = self.mCommander.record_StartRecord( int( current[0] ),  int( current[3] ),  self.mEPGDuration,  self.mRecordName )
		print 'Record Result=%s' %ret

		self.Close( )


	@RunThread
	def CurrentTimeThread(self):
		loop = 0

		while self.mEnableThread:
			if  ( loop % 10 ) == 0 :
				print 'loop=%d' %loop
				localTime = self.mCommander.datetime_GetLocalTime( )
				self.mLocalTime = int( localTime[0] )
				
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

		print 'mLocalOffset=%d' % int( self.mLocalOffset/60 )
		print 'start=%s' % epgInfoClock( 1, startTime, 0 )
		print 'current=%s' % epgInfoClock( 1,self.mLocalTime, 0 )
		print 'end=%s' % epgInfoClock( 1, endTime, 0 )		

		print 'UpdateProgress=%d' %passDuration 

		startTimeString = epgInfoClock( 1, startTime, 0 )
		endTimeString = epgInfoClock( 1, endTime, 0 )		

		self.getControl( E_LABEL_EPG_START_TIME ).setLabel( startTimeString[1] )
		self.getControl( E_LABEL_EPG_END_TIME ).setLabel( endTimeString[1] )

		if self.mHasEPG == True :
			recordDuration = endTime - self.mLocalTime
			if recordDuration < 0 :
				recordDuration = 0
			self.getControl( E_LABEL_DURATION ).setLabel( '%d' %int( recordDuration/(60) )  )
		else :
			self.getControl( E_LABEL_DURATION ).setLabel( '%d' % int( self.mEPGDuration/(60) ) )			


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

		print 'percent=%d' %percent
		
		self.mCtrlProgress.setPercent( percent )


