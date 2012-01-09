
import xbmc
import xbmcgui
import time
import sys


from pvr.gui.BaseWindow import Action
from pvr.gui.BaseDialog import BaseDialog
from  pvr.TunerConfigMgr import *
import pvr.gui.DialogMgr as DlgMgr
from ElisEnum import ElisEnum

import pvr.ElisMgr

from pvr.Util import RunThread, GuiLock, LOG_TRACE, LOG_WARN, LOG_ERR
from pvr.PublicReference import EpgInfoClock



# Control IDs
LIST_ID_RECORD				= 201




class DialogStopRecord( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.mEventBus = pvr.ElisMgr.GetInstance().GetEventBus()

	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId  )
		self.mRunningRecordCount = self.mCommander.Record_GetRunningRecorderCount()
		self.mCtrlRecordList = self.getControl( LIST_ID_RECORD )
		self.mRecordListItems = []
		self.mRunnigRecordInfoList = []

		LOG_TRACE( 'recordcount=%d' %self.mRunningRecordCount )

		for i in range( self.mRunningRecordCount ) :
			recordInfo = self.mCommander.Record_GetRunningRecordInfo( i )
			if recordInfo :
				recordInfo.printdebug()
				listItem = xbmcgui.ListItem( recordInfo.RecordName, "_" , "-", "-", "-" )
				self.mRecordListItems.append( listItem )
				self.mRunnigRecordInfoList.append( recordInfo )
				
		self.mCtrlRecordList.addItems( self.mRecordListItems )		


	@GuiLock
	def onAction( self, aAction ):
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		LOG_TRACE('action=%d' %actionId )
	
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
			LOG_WARN( 'Unknown Action' )


	def onClick( self, aControlId ):
		focusId = self.getFocusId( )

		LOG_TRACE('DialogRecord focusId=%d' %focusId )
		if focusId == LIST_ID_RECORD :
			self.StopRecord( )

	def onFocus( self, aControlId ):
		pass


	@GuiLock	
	def onEvent( self, aEvent ):
		if xbmcgui.getCurrentWindowId() == self.mWinId :
			LOG_TRACE('')
			pass

	def Close( self ):
		self.close( )


	def StopRecord( self ):
		position = self.mCtrlRecordList.getSelectedPosition( )
		if position >=0 and position < len( self.mRunnigRecordInfoList ) :
			LOG_TRACE('position=%d' %position )
			recInfo = self.mRunnigRecordInfoList[position]
			self.mCommander.Record_StopRecord( recInfo.ChannelNo, recInfo.ServiceType, recInfo.RecordKey  )
			LOG_TRACE('recInfo.ChannelNo=%d, recInfo.ServiceType=%d, recInfo.RecordKey=%d' %(recInfo.ChannelNo, recInfo.ServiceType, recInfo.RecordKey) )
			self.Close( )


	@RunThread
	def CurrentTimeThread(self):
		loop = 0

		while self.mEnableThread:
			if  ( loop % 10 ) == 0 :
				LOG_TRACE(  'loop=%d' %loop )
				self.mLocalTime = self.mCommander.Datetime_GetLocalTime( )
				
			self.UpdateEPGTime( )

			time.sleep(1)
			self.mLocalTime += 1			
			loop += 1


	@GuiLock	
	def UpdateEPGTime( self ):
		self.UpdateProgress( )


	def UpdateProgress( self ):
		pass

		startTime = self.mEPGStartTime+ self.mLocalOffset
		endTime =  startTime  + self.mEPGDuration

		passDuration = self.mLocalTime - startTime

		startTimeString = EpgInfoClock( 1, startTime, 0 )
		endTimeString = EpgInfoClock( 1, endTime, 0 )		

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

		LOG_TRACE( 'percent=%d' %percent )
		
		self.mCtrlProgress.setPercent( percent )

