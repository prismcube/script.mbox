
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

from pvr.Util import RunThread, GuiLock, LOG_TRACE, LOG_WARN, LOG_ERR, TimeToString, TimeFormatEnum


# Control IDs
IMAGE_ID_BACKGROUND 		= 100
LIST_ID_RECORD				= 9000

GROUP_ID_RECORD_1			= 500
GROUP_ID_RECORD_2			= 510
GROUP_ID_CANCEL				= 520

BUTTON_ID_RECORD_1			= 501
BUTTON_ID_RECORD_2			= 511
BUTTON_ID_CANCEL			= 521

LABEL_ID_CHANNELNAME_1		= 502
LABEL_ID_CHANNELNAME_2		= 512

LABEL_ID_RECORDNAME_1		= 503
LABEL_ID_RECORDNAME_2		= 513

LABEL_ID_DURATION_1			= 504
LABEL_ID_DURATION_2			= 514

PROGRESS_ID_DURATION_1		= 505
PROGRESS_ID_DURATION_2		= 515


class DialogStopRecord( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mBackgroundHeight = -1;

	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		self.mCtrlRecordGroup = {}
		self.mCtrlChannelName = {}
		self.mCtrlRecordName = {}
		self.mCtrlDuration = {}
		self.mCtrlProgress = {}		
		self.mIsOk = E_DIALOG_STATE_CANCEL

		try :		
			self.mCtrlRecordGroup[0] = self.getControl( GROUP_ID_RECORD_1 )
			self.mCtrlRecordGroup[1] = self.getControl( GROUP_ID_RECORD_2 )
			self.mCtrlRecordGroup[2] = self.getControl( GROUP_ID_CANCEL )			

			self.mCtrlChannelName[0] = self.getControl( LABEL_ID_CHANNELNAME_1 )
			self.mCtrlChannelName[1] = self.getControl( LABEL_ID_CHANNELNAME_2 )

			self.mCtrlRecordName[0] = self.getControl( LABEL_ID_RECORDNAME_1 )
			self.mCtrlRecordName[1] = self.getControl( LABEL_ID_RECORDNAME_2 )

			self.mCtrlDuration[0] = self.getControl( LABEL_ID_DURATION_1 )
			self.mCtrlDuration[1] = self.getControl( LABEL_ID_DURATION_2 )

			self.mCtrlProgress[0] = self.getControl( PROGRESS_ID_DURATION_1 )
			self.mCtrlProgress[1] = self.getControl( PROGRESS_ID_DURATION_2 )
		
			self.mCtrlCancelGroup = self.getControl( GROUP_ID_CANCEL )					
			self.mCtrlBackgroundImage = self.getControl( IMAGE_ID_BACKGROUND )

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)

		if self.mBackgroundHeight <  0 :
			self.mBackgroundHeight = self.mCtrlBackgroundImage.getHeight()

		self.SetHeaderLabel( 'Stop Record' )

		self.mLocalTime = self.mCommander.Datetime_GetLocalTime( )		
		self.mRunningRecordCount = self.mCommander.Record_GetRunningRecorderCount()

		LOG_ERR("self.mRunningRecordCount=%d" %self.mRunningRecordCount )

		self.mRunnigRecordInfoList = []
		LOG_TRACE( 'recordcount=%d' %self.mRunningRecordCount )

		for i in range( self.mRunningRecordCount ) :
			recordInfo = self.mCommander.Record_GetRunningRecordInfo( i )
			if recordInfo :
				recordInfo.printdebug()
				self.mRunnigRecordInfoList.append( recordInfo )
		
		self.DrawItem( )
		#self.setFocusId( self.mCtrlGropCHList.getId( ) )
		
	def onAction( self, aAction ):
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		LOG_TRACE('action=%d' %actionId )
		LOG_TRACE('focusId=%d' %focusId )
		
		self.GlobalAction( actionId )
		
		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.Close()
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
					
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.Close()
		
		elif actionId == Action.ACTION_MOVE_UP :
			if focusId == BUTTON_ID_RECORD_1 :
				self.setFocusId( BUTTON_ID_CANCEL )
			elif focusId == BUTTON_ID_RECORD_2 :
				self.setFocusId( BUTTON_ID_RECORD_1 )
			elif focusId == BUTTON_ID_CANCEL :
				if self.mRunningRecordCount < 2 :
					self.setFocusId( BUTTON_ID_RECORD_1 )								
				else :
					self.setFocusId( BUTTON_ID_RECORD_2 )
			else :
				self.setFocusId( BUTTON_ID_CANCEL )			

		elif actionId == Action.ACTION_MOVE_DOWN :
			if focusId == BUTTON_ID_RECORD_1 :
				if self.mRunningRecordCount < 2 :
					self.setFocusId( BUTTON_ID_CANCEL )								
				else :
					self.setFocusId( BUTTON_ID_RECORD_2 )
			elif focusId == BUTTON_ID_RECORD_2 :
				self.setFocusId( BUTTON_ID_CANCEL )
			elif focusId == BUTTON_ID_CANCEL :
				self.setFocusId( BUTTON_ID_RECORD_1 )
			else :
				self.setFocusId( BUTTON_ID_CANCEL )			


		elif actionId == Action.ACTION_MOVE_LEFT :
			pass
				
		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass
		else :
			LOG_WARN( 'Unknown Action' )


	def onClick( self, aControlId ):

		LOG_TRACE('DialogRecord aControlId=%d' %aControlId )
		if aControlId == BUTTON_ID_RECORD_1 or aControlId == BUTTON_ID_RECORD_2 or aControlId == BUTTON_ID_CANCEL :
			self.StopRecord( aControlId )


	def onFocus( self, aControlId ):
		pass


	@GuiLock	
	def onEvent( self, aEvent ):
		if xbmcgui.getCurrentWindowId() == self.mWinId :
			LOG_TRACE('')
			pass

	def Close( self ):
		self.close( )


	def StopRecord( self, aControlId ):

		LOG_TRACE('aControlId=%d' %aControlId)
		if aControlId == BUTTON_ID_RECORD_1 :
			LOG_TRACE('---------------------------------------->')		
			recInfo = self.mRunnigRecordInfoList[0]
			recInfo.printdebug()
			self.mCommander.Timer_StopRecordingByRecordKey( recInfo.mRecordKey )
			#self.mCommander.Record_StopRecord( recInfo.mChannelNo, recInfo.mServiceType, recInfo.mRecordKey  )
			self.mIsOk = E_DIALOG_STATE_YES
			self.Close( )			

		elif aControlId == BUTTON_ID_RECORD_2 :
			LOG_TRACE('---------------------------------------->')
			recInfo = self.mRunnigRecordInfoList[1]
			self.mCommander.Timer_StopRecordingByRecordKey( recInfo.mRecordKey )			
			#self.mCommander.Record_StopRecord( recInfo.mChannelNo, recInfo.mServiceType, recInfo.mRecordKey  )
			self.mIsOk = E_DIALOG_STATE_YES
			self.Close( )

		elif aControlId == BUTTON_ID_CANCEL :
			LOG_TRACE('')		
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.Close( )
		else :
			LOG_ERR('Can not find control')


	@RunThread
	def CurrentTimeThread(self):
		loop = 0

		while self.mEnableThread:
			if  ( loop % 10 ) == 0 :
				LOG_TRACE(  'loop=%d' %loop )
				self.mLocalTime = self.mCommander.Datetime_GetLocalTime( )

			self.UpdateProgress( )

			time.sleep(1)
			self.mLocalTime += 1			
			loop += 1


	def UpdateProgress( self ):
		pass

		"""
		for i in range( self.mRunningRecordCount ) :
			recordInfo = self.mRunnigRecordInfoList[i]
			startTime = recordInfo.mStartTime + self.mLocalOffset
			endTime =  startTime  + recordInfo.mDuration

			LOG_TRACE('START : %s' %TimeToString( startTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
			LOG_TRACE('CUR : %s' %TimeToString( self.mLocalTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )			
			LOG_TRACE('END : %s' %TimeToString( endTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )			
		"""

		"""
		self.mCommander.Record_StopRecord( recInfo.mChannelNo, recInfo.mServiceType, recInfo.mRecordKey  )


		startTime = self.mEPGStartTime+ self.mLocalOffset
		endTime =  startTime  + self.mEPGDuration

		passDuration = self.mLocalTime - startTime

		#self.getControl( E_LABEL_EPG_START_TIME ).setLabel(  TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
		#self.getControl( E_LABEL_EPG_END_TIME ).setLabel(  TimeToString( endTime, TimeFormatEnum.E_HH_MM ) )

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
		"""		

	def DrawItem( self ) :
		LOG_TRACE('')
		if self.mRunningRecordCount < 2 :
			newHeight = self.mBackgroundHeight - self.mCtrlRecordGroup[0].getHeight()
			self.mCtrlBackgroundImage.setHeight( newHeight )
			self.mCtrlRecordGroup[1].setVisible( False )
			
		else :
			self.mCtrlBackgroundImage.setHeight( self.mBackgroundHeight )		
			self.mCtrlRecordGroup[1].setVisible( True )


		for i in range( self.mRunningRecordCount ) :
			recordInfo = self.mRunnigRecordInfoList[i]
			LOG_TRACE('i=%d recordInfo.mChannelNo=%d, recordInfo.mChannelName=%s' %( i, recordInfo.mChannelNo, recordInfo.mChannelName ) )
			"""
			self.mCtrlChannelName[i].setLabel( '1234567890123456789012345678901234567890' )
			self.mCtrlRecordName[i].setLabel( '1234567890123456789012345678901234567890' )
			self.mCtrlDuration[i].setLabel( '999 Min' )
			self.mCtrlProgress[i].setPercent( 0 )
			"""

			self.mCtrlChannelName[i].setLabel( 'P%04d %s' %(recordInfo.mChannelNo, recordInfo.mChannelName) )
			self.mCtrlRecordName[i].setLabel( '%s' %recordInfo.mRecordName )
			self.mCtrlDuration[i].setLabel( '%d Min' %int(recordInfo.mDuration/60) )
			self.mCtrlProgress[i].setPercent( 0 )

	def IsOK( self ) :
		return self.mIsOk

	
