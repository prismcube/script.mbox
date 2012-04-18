import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DlgMgr
import pvr.TunerConfigMgr as ConfigMgr
from pvr.gui.BaseWindow import BaseWindow, Action
from inspect import currentframe
import pvr.ElisMgr
from ElisEnum import ElisEnum
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
from pvr.Util import RunThread, GuiLock, GuiLock2
from util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR
from pvr.gui.GuiConfig import *
from ElisEventClass import *

E_TABLE_ALLCHANNEL = 0
E_TABLE_ZAPPING = 1


class NullWindow( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mAsyncShowTimer = None
		self.mStatusIsArchive = False
		self.mRecInfo = None


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		self.mGotoWinID = None
		self.mOnEventing= False

		#self.mEventBus.Register( self )

		if self.mInitialized == False :
			self.mInitialized = True
			ConfigMgr.GetInstance( ).SetNeedLoad( True )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_DUMMY_WINDOW )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )


	def onAction(self, aAction) :		
		actionId = aAction.getId( )
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU:
			if self.mGotoWinID :
				if self.mGotoWinID == WinMgr.WIN_ID_ARCHIVE_WINDOW :
					self.mGotoWinID = None
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW )
				return
				
			if ElisPropertyEnum( 'Lock Mainmenu', self.mCommander ).GetProp( ) == 0 :
				dialog = DlgMgr.GetInstance().GetDialog( DlgMgr.DIALOG_ID_NUMERIC_KEYBOARD )
				dialog.SetDialogProperty( 'PIN Code 4 digit', '', 4, True )
	 			dialog.doModal( )
	 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
	 				tempval = dialog.GetString( )
	 				if tempval == '' :
	 					return
					if int( tempval ) == ElisPropertyInt( 'PinCode', self.mCommander ).GetProp( ) :
						WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MAINMENU )
					else :
						dialog = DlgMgr.GetInstance().GetDialog( DlgMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( 'ERROR', 'ERROR PIN Code' )
			 			dialog.doModal( )
			 	return
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MAINMENU )
			
				
		elif actionId == Action.ACTION_PARENT_DIR:
			try :
				currentChannel = self.mCommander.Channel_GetCurrent( )
				#lastChannel = WinMgr.GetInstance( ).getWindow(WinMgr.WIN_ID_LIVE_PLATE).getLastChannel( )
				#if lastChannel > 0 and lastchannel != currentChannel :
				#	self.mCommander.channel_SetCurrent( lastChannel )
				#	WinMgr.GetInstance( ).getWindow(WinMgr.WIN_ID_LIVE_PLATE).setLastChannel( currentChannel )
				#	WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )

			except Exception, ex:
				print 'ERR prev channel'

		elif actionId == Action.ACTION_SELECT_ITEM:
			LOG_TRACE('key ok')
			if self.mStatusIsArchive :
				LOG_TRACE('Archive playing now')
				return -1
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CHANNEL_LIST_WINDOW )

		elif actionId == Action.ACTION_MOVE_LEFT:
			print 'youn check ation left'
			window = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )
			window.SetAutomaticHide( True )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )

		elif actionId == Action.ACTION_SHOW_INFO:
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EPG_WINDOW )

		elif actionId == Action.ACTION_CONTEXT_MENU:
			status = None
			status = self.mDataCache.Player_GetStatus()
			gotoWinId = WinMgr.WIN_ID_LIVE_PLATE
			if status.mMode != ElisEnum.E_MODE_LIVE :
				gotoWinId = WinMgr.WIN_ID_TIMESHIFT_PLATE

			window = WinMgr.GetInstance( ).GetWindow( gotoWinId )
			window.SetAutomaticHide( False )
			WinMgr.GetInstance( ).ShowWindow( gotoWinId )

		elif actionId == Action.ACTION_PAGE_DOWN:
			LOG_TRACE('key down')
			if self.mStatusIsArchive :
				LOG_TRACE('Archive playing now')
				return -1

			prevChannel = None
			prevChannel = self.mDataCache.Channel_GetPrev( self.mDataCache.Channel_GetCurrent( ) ) #self.mCommander.Channel_GetPrev( )
			if prevChannel :
				self.mDataCache.Channel_SetCurrent( prevChannel.mNumber, prevChannel.mServiceType )			
				#self.mCommander.Channel_SetCurrent( prevChannel.mNumber, prevChannel.mServiceType )
			
				window = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE )
				window.SetAutomaticHide( True )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )


		elif actionId == Action.ACTION_PAGE_UP:
			LOG_TRACE('key up')
			if self.mStatusIsArchive :
				LOG_TRACE('Archive playing now')
				return -1

			nextChannel = None
			nextChannel = self.mDataCache.Channel_GetNext( self.mDataCache.Channel_GetCurrent( ) )
			if nextChannel :
				self.mDataCache.Channel_SetCurrent( nextChannel.mNumber, nextChannel.mServiceType )
				#self.mCommander.Channel_SetCurrent( nextChannel.mNumber, nextChannel.mServiceType )

				window = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE )
				window.SetAutomaticHide( True )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )
			
	
		elif actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 or \
			actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :

			aKey = actionId - (Action.ACTION_JUMP_SMS2 - 2)
			if actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9:
				aKey = actionId - Action.REMOTE_0

			if self.mStatusIsArchive :
				LOG_TRACE('Archive playing now')
				return -1

			if aKey == 0 :
				return -1

			GuiLock2(True)
			dialog = DlgMgr.GetInstance().GetDialog( DlgMgr.DIALOG_ID_CHANNEL_JUMP )
			event = self.mDataCache.Epgevent_GetPresent()
			if event:
				dialog.SetDialogProperty( str(aKey), E_INPUT_MAX, None, event.mStartTime)
			else :
				dialog.SetDialogProperty( str(aKey), E_INPUT_MAX, None)
			dialog.doModal()
			GuiLock2(False)

			isOK = dialog.IsOK()
			if isOK == E_DIALOG_STATE_YES :
				inputNumber = dialog.GetChannelLast()
				LOG_TRACE('=========== Jump chNum[%s]'% inputNumber)

				iCurrentCh = self.mDataCache.Channel_GetCurrent( )
				if iCurrentCh.mNumber != int(inputNumber) :
					jumpChannel = self.mDataCache.Channel_GetCurr( int(inputNumber) )
					if jumpChannel :
						self.mDataCache.Channel_SetCurrent( jumpChannel.mNumber, jumpChannel.mServiceType )

		elif actionId == Action.ACTION_STOP :
			status = None
			status = self.mDataCache.Player_GetStatus()
			if status.mMode :
				ret = self.mDataCache.Player_Stop()
				LOG_TRACE('----------mode[%s] stop[%s] up/down[%s]'% (status.mMode, ret, self.mStatusIsArchive) )
				if ret :
					if status.mMode == ElisEnum.E_MODE_PVR :
						if self.mStatusIsArchive :
							self.mGotoWinID = WinMgr.WIN_ID_ARCHIVE_WINDOW
							self.mStatusIsArchive = False
							LOG_TRACE('archive play, stop to go Archive')
						else :
							self.mGotoWinID = None
							self.mStatusIsArchive = False
							LOG_TRACE('recording play, stop only(NullWindow)')

						LOG_TRACE('up/down key released, goto win[%s]'% self.mGotoWinID)
						if self.mGotoWinID :
							xbmc.executebuiltin('xbmc.Action(previousmenu)')

			else :
				self.RecordingStop()

		else:
			print 'lael98 check ation unknown id=%d' %actionId


		"""
		#test
		elif actionId == Action.ACTION_MOVE_RIGHT :
			print 'youn check ation right'
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_INFO_PLATE1 )

		elif actionId == Action.ACTION_MOVE_UP :
			print 'youn check ation up'
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_INFO_PLATE )

		elif actionId == Action.ACTION_MOVE_DOWN :
			print 'youn check ation up'
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_INFO_PLATE2 )

		elif actionId == Action.REMOTE_3:  #TEST : start Record
			print 'open record dialog'
			
			runningCount = self.mCommander.Record_GetRunningRecorderCount( )
			LOG_TRACE( 'runningCount=%d' %runningCount)
			if  runningCount < E_MAX_RECORD_COUNT :
				dialog = DlgMgr.GetInstance( ).GetDialog( DlgMgr.DIALOG_ID_START_RECORD )
				dialog.doModal( )
			else:
				msg = 'Already %d recording(s) running' %runningCount
				xbmcgui.Dialog( ).ok('Infomation', msg )
				
		
		elif actionId == Action.REMOTE_4:  #TEST : stop Record
			print 'open record dialog'
			runningCount = self.mCommander.Record_GetRunningRecorderCount( )
			LOG_TRACE( 'runningCount=%d' %runningCount )

			if  runningCount > 0 :
				dialog = DlgMgr.GetInstance( ).GetDialog( DlgMgr.DIALOG_ID_STOP_RECORD )
				dialog.doModal( )

		elif actionId == Action.REMOTE_1:  #TEST : bg test
		"""


	def onClick(self, aControlId) :
		print "onclick( ): control %s" % aControlId


	def onFocus(self, aControlId) :
		print "onFocus( ): control %s" % aControlId
		self.mLastFocusId = aControlId


	@GuiLock
	def onEvent(self, aEvent):
		LOG_TRACE( 'Enter' )

		if self.mWinId == xbmcgui.getCurrentWindowId():
			LOG_TRACE( 'NullWindow winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId()) )
			if aEvent.getName() == ElisEventPlaybackEOF.getName() :
				#aEvent.printdebug()
				LOG_TRACE( 'mType[%d]' %(aEvent.mType ) )

				if self.mOnEventing :
					LOG_TRACE('ignore event, mFlag_OnEvent[%s]'% self.mOnEventing)
					return -1

				self.mOnEventing = True

				if aEvent.mType == ElisEnum.E_EOF_END :
					LOG_TRACE( 'EventRecv EOF_STOP' )
					xbmc.executebuiltin('xbmc.Action(stop)')

				self.mOnEventing = False


		else:
			LOG_TRACE( 'NullWindow winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId()) )


		LOG_TRACE( 'Leave' )


	def RecordingStop( self ) :
		LOG_TRACE('Enter')

		isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )
		LOG_TRACE( 'runningCount[%s]'% isRunRec )

		if isRunRec > 0 :
			GuiLock2( True )
			dialog = DlgMgr.GetInstance().GetDialog( DlgMgr.DIALOG_ID_STOP_RECORD )
			dialog.doModal( )
			GuiLock2( False )

			isOK = dialog.IsOK()
			if isOK == E_DIALOG_STATE_YES :
				if self.mDataCache.GetChangeDBTableChannel( ) != -1 :
					time.sleep(1.5)
					isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )
					if isRunRec > 0 :
						#use zapping table, in recording
						self.mDataCache.SetChangeDBTableChannel( E_TABLE_ZAPPING )
						self.mDataCache.Channel_GetZappingList( )
						self.mDataCache.LoadChannelList( )
					else :
						self.mDataCache.SetChangeDBTableChannel( E_TABLE_ALLCHANNEL )
						self.mDataCache.LoadChannelList( )
						self.mDataCache.mCacheReload = True

		LOG_TRACE('Leave')

	def SetKeyDisabled( self, aDisable = False, aRecInfo = None ) :
		self.mStatusIsArchive = aDisable
		self.mRecInfo = aRecInfo

	def GetKeyDisabled( self ) :
		return self.mStatusIsArchive

	def Close( self ) :
		#self.mOnEventing = aDisable
		self.mEventBus.Deregister( self )

