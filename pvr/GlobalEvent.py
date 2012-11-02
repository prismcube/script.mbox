import xbmc
import xbmcgui
import sys
import time
import os
import shutil
import weakref

from pvr.gui.WindowImport import *
from ElisEventBus import ElisEventBus
from util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR
import pvr.Platform
import pvr.DataCacheMgr
from ElisEnum import ElisEnum
import pvr.ElisMgr

gGlobalEvent = None


def GetInstance( ) :
	global gGlobalEvent
	if not gGlobalEvent :
		print 'Create instance'
		gGlobalEvent = GlobalEvent( )
	else :
		pass

	return gGlobalEvent


class GlobalEvent( object ) :
	def __init__( self ) :
		self.mDataCache = pvr.DataCacheMgr.GetInstance( )
		self.mIsDialogOpend	= False
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.SendLocalOffsetToXBMC( )		


	@classmethod
	def GetName( cls ) :
		return cls.__name__


	def onEvent(self, aEvent) :
		if not WinMgr.gWindowMgr :
			return

		if aEvent.getName( ) == ElisEventTimeReceived.getName( ) :
			self.SendLocalOffsetToXBMC( )

		elif aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or \
			 aEvent.getName( ) == ElisEventRecordingStopped.getName( ) :
			self.mDataCache.ReLoadChannelListByRecording( )

		elif aEvent.getName( ) == ElisEventChannelChangeStatus( ).getName( ) :
			if aEvent.mStatus == ElisEnum.E_CC_FAILED_SCRAMBLED_CHANNEL :
				WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).mLastId ).setProperty( 'Signal', 'Scramble' )
				self.mDataCache.Frontdisplay_Resolution( )
				self.mDataCache.SetLockedState( ElisEnum.E_CC_FAILED_SCRAMBLED_CHANNEL )
			elif aEvent.mStatus == ElisEnum.E_CC_FAILED_NO_SIGNAL :
				WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).mLastId ).setProperty( 'Signal', 'False' )
				self.mDataCache.Frontdisplay_Resolution( )
				self.mDataCache.SetLockedState( ElisEnum.E_CC_FAILED_NO_SIGNAL )
			else :
				WinMgr.GetInstance( ).GetWindow( WinMgr.GetInstance( ).mLastId ).setProperty( 'Signal', 'True' )
				self.mDataCache.SetLockedState( ElisEnum.E_CC_SUCCESS )


		elif aEvent.getName( ) == ElisEventVideoIdentified( ).getName( ) :
			hdmiFormat = ElisPropertyEnum( 'HDMI Format', self.mCommander ).GetPropString( )

			iconIndex = ElisEnum.E_ICON_1080i
			if aEvent.mVideoHeight <= 576 :
				iconIndex = -1
			elif aEvent.mVideoHeight <= 720 :
				iconIndex = ElisEnum.E_ICON_720p

			self.mDataCache.Frontdisplay_Resolution( iconIndex )

		elif aEvent.getName( ) == ElisEventPowerSave( ).getName( ) :
			if self.mIsDialogOpend == False :
				thread = threading.Timer( 1, self.AsyncPowerSave )
				thread.start( )
				

	def AsyncPowerSave( self ) :
		self.mIsDialogOpend = True
		LOG_TRACE( 'Open Auto power down dialog' )
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_AUTO_POWER_DOWN )
		dialog.doModal( )
		self.mIsDialogOpend = False


	def GetRecordingInfo( self ) :
		labelInfo = MR_LANG( 'Reloading channel list...' )
		try:
			isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )
			#LOG_TRACE('isRunRecCount[%s]'% isRunRec)

			if isRunRec == 1 :
				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 0 )
				labelInfo = '%s %s'% ( recInfo.mChannelNo, recInfo.mChannelName )

			elif isRunRec == 2 :
				recInfo1 = self.mDataCache.Record_GetRunningRecordInfo( 0 )
				recInfo2 = self.mDataCache.Record_GetRunningRecordInfo( 1 )
				if recInfo1.mStartTime > recInfo2.mStartTime :
					labelInfo = '%s %s'% ( recInfo1.mChannelNo, recInfo1.mChannelName )
				else :
					labelInfo = '%s %s'% ( recInfo2.mChannelNo, recInfo2.mChannelName )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		return labelInfo


	def SendLocalOffsetToXBMC( self ) :
		LOG_TRACE( '--------------' )
		if WinMgr.E_ADD_XBMC_HTTP_FUNCTION == True :
			localOffset = self.mDataCache.Datetime_GetLocalOffset( )
			xbmc.executehttpapi( 'setlocaloffset(%d)' %localOffset )

		LOG_TRACE( '--------------' )

