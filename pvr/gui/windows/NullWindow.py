import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DlgMgr
import pvr.TunerConfigMgr as ConfigMgr
from pvr.gui.BaseWindow import BaseWindow, Action
from inspect import currentframe
import pvr.ElisMgr
from pvr.Util import GuiLock2, LOG_TRACE, LOG_ERR, LOG_WARN, RunThread
from pvr.gui.GuiConfig import *


class NullWindow( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mAsyncShowTimer = None


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		if self.mInitialized == False :
			self.mInitialized = True
			ConfigMgr.GetInstance( ).SetNeedLoad( True )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_DUMMY_WINDOW )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )


	def onAction(self, aAction) :		
		actionId = aAction.getId( )
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU:
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
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CHANNEL_LIST_WINDOW )
#			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )
			print 'lael98 check ation select'

		elif actionId == Action.ACTION_MOVE_LEFT:
			print 'youn check ation left'
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )

		elif actionId == Action.ACTION_SHOW_INFO:
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EPG_WINDOW )

		elif actionId == Action.ACTION_CONTEXT_MENU:

			window = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE )
			window.SetAutomaticHide( False )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )


		elif actionId == Action.ACTION_PAGE_DOWN:
			LOG_TRACE('TRACE')
			LOG_WARN('WARN')
			LOG_ERR('ERR')
			prevChannel = None
			prevChannel = self.mDataCache.Channel_GetPrev( self.mDataCache.Channel_GetCurrent( ) ) #self.mCommander.Channel_GetPrev( )
			if prevChannel :
				self.mDataCache.Channel_SetCurrent( prevChannel.mNumber, prevChannel.mServiceType )			
				#self.mCommander.Channel_SetCurrent( prevChannel.mNumber, prevChannel.mServiceType )
			
				window = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE )
				window.SetAutomaticHide( True )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )


		elif actionId == Action.ACTION_PAGE_UP:
			nextChannel = None
			nextChannel = self.mDataCache.Channel_GetNext( self.mDataCache.Channel_GetCurrent( ) )
			if nextChannel :
				self.mDataCache.Channel_SetCurrent( nextChannel.mNumber, nextChannel.mServiceType )
				#self.mCommander.Channel_SetCurrent( nextChannel.mNumber, nextChannel.mServiceType )

				window = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE )
				window.SetAutomaticHide( True )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )
			

		#test code
		elif actionId == Action.REMOTE_0 :
			LOG_ERR('')
			try :
				from ElisEPGDB import ElisEPGDB
			except Exception, ex:
				LOG_ERR( "Exception %s" %ex)
				
			LOG_ERR('')
			try :			
				channelDB = ElisEPGDB()
			except Exception, ex:
				LOG_ERR( "Exception %s" %ex)
				
			LOG_ERR('')
			#channel = self.mDataCache.Channel_GetCurrent()
			#gmtTime = self.mDataCache.Datetime_GetGMTTime()
			#epgDB.Epgevent_GetList( channel.mSid,  channel.mTsid,  channel.mOnid, gmtTime, gmtTime+3600, 100) :	
			
			
		elif actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 or \
			actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :

			aKey = actionId - (Action.ACTION_JUMP_SMS2 - 2)
			if actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9:
				aKey = actionId - Action.REMOTE_0

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

				jumpChannel = self.mDataCache.Channel_GetCurr( int(inputNumber) )
				if jumpChannel :
					self.mDataCache.Channel_SetCurrent( jumpChannel.mNumber, jumpChannel.mServiceType )

		else:
			print 'lael98 check ation unknown id=%d' %actionId

		"""
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
		
