import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DlgMgr
import pvr.TunerConfigMgr as ConfigMgr
from pvr.gui.BaseWindow import BaseWindow, Action
from inspect import currentframe
import pvr.ElisMgr
from pvr.Util import LOG_TRACE, LOG_ERR, LOG_WARN
from pvr.gui.GuiConfig import *


class NullWindow(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		print 'lael98 check %d %s' %(currentframe().f_lineno, currentframe().f_code.co_filename)    
		print 'args=%s' % args[0]
		self.mCommander = pvr.ElisMgr.GetInstance().GetCommander()				
		self.mLastFocusId = None

	def onInit(self):
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId )

	def onAction(self, aAction):
		id = aAction.getId()

		if id == Action.ACTION_PREVIOUS_MENU:
			print 'lael98 check ation menu'
			ConfigMgr.GetInstance( ).SetNeedLoad( True )
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_MAINMENU )

		elif id == Action.ACTION_PARENT_DIR:
			try :
				currentChannel = self.mCommander.Channel_GetCurrent()
				#lastChannel = WinMgr.GetInstance().getWindow(WinMgr.WIN_ID_LIVE_PLATE).getLastChannel( )
				#if lastChannel > 0 and lastchannel != currentChannel :
				#	self.mCommander.channel_SetCurrent( lastChannel )
				#	WinMgr.GetInstance().getWindow(WinMgr.WIN_ID_LIVE_PLATE).setLastChannel( currentChannel )
				#	WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )

			except Exception, ex:
				print 'ERR prev channel'

		elif id == Action.ACTION_SELECT_ITEM:
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CHANNEL_LIST_WINDOW )
#			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )
			print 'lael98 check ation select'

		elif id == Action.ACTION_MOVE_LEFT:
			print 'youn check ation left'
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )

		elif id == Action.ACTION_SHOW_INFO	:
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )
			
		elif id == Action.ACTION_PAGE_UP:
			LOG_TRACE('TRACE')
			LOG_WARN('WARN')
			LOG_ERR('ERR')
			prevChannel = None
			prevChannel = self.mCommander.Channel_GetPrev()
			if prevChannel :
				self.mCommander.Channel_SetCurrent( prevChannel.mNumber, prevChannel.mServiceType )
			
				#WinMgr.GetInstance().getWindow(WinMgr.WIN_ID_LIVE_PLATE).setLastChannel( currentChannel )
				WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )		


		elif id == Action.ACTION_PAGE_DOWN:
			nextChannel = None
			nextChannel = self.mCommander.Channel_GetNext()
			if nextChannel :
				self.mCommander.Channel_SetCurrent( nextChannel.mNumber, nextChannel.mServiceType )
			
				#WinMgr.GetInstance().getWindow(WinMgr.WIN_ID_LIVE_PLATE).setLastChannel( currentChannel )
				WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )		

		elif id == Action.REMOTE_3:  #TEST : start Record
			print 'open record dialog'
			
			runningCount = self.mCommander.Record_GetRunningRecorderCount()
			LOG_TRACE( 'runningCount=%d' %runningCount)
			if  runningCount < E_MAX_RECORD_COUNT :
				dialog = DlgMgr.GetInstance().GetDialog( DlgMgr.DIALOG_ID_START_RECORD )
				dialog.doModal( )
			else:
				msg = 'Already %d recording(s) running' %runningCount
				xbmcgui.Dialog().ok('Infomation', msg )
				
		
		elif id == Action.REMOTE_4:  #TEST : stop Record
			print 'open record dialog'
			runningCount = self.mCommander.Record_GetRunningRecorderCount()
			LOG_TRACE( 'runningCount=%d' %runningCount )

			if  runningCount > 0 :
				dialog = DlgMgr.GetInstance().GetDialog( DlgMgr.DIALOG_ID_STOP_RECORD )
				dialog.doModal( )

		elif id == Action.REMOTE_1:  #TEST : bg test
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_TEST1 )


		elif id == Action.ACTION_PAGE_UP:
			pass

		elif id == Action.ACTION_PAGE_DOWN:
			pass

		else:
			print 'lael98 check ation unknown id=%d' %id


	def onClick(self, aControlId):
		print "onclick(): control %s" % aControlId


	def onFocus(self, aControlId):
		print "onFocus(): control %s" % aControlId
		self.mLastFocusId = aControlId


