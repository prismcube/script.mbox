import xbmc
import xbmcgui
import threading, time
import sys

from pvr.gui.BaseDialog import BaseDialog
from pvr.gui.BaseWindow import Action
from pvr.gui.GuiConfig import *

from ElisEnum import ElisEnum
import pvr.DataCacheMgr as CacheMgr
from pvr.PublicReference import ClassToList, EpgInfoClock
from pvr.Util import RunThread, GuiLock, GuiLock2, MLOG, LOG_WARN, LOG_TRACE, LOG_ERR

E_MOVETOJUMP_NUM_ID  = 210
E_RESERVED_ID        = 211
E_MOVETOJUMP_TIME_ID = 212
E_PROGRESS_ID        = 213

E_INDEX_JUMP_MAX = 100

FLAG_CLOCKMODE_ADMYHM  = 1
FLAG_CLOCKMODE_AHM     = 2
FLAG_CLOCKMODE_HMS     = 3
FLAG_CLOCKMODE_HHMM    = 4
FLAG_CLOCKMODE_INTTIME = 5

class DialogTimeshiftJump( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )	
		self.mMoveToNumber		= ''
		#self.mChannelName		= 'No channel'
		#self.mEPGName			= ''

		self.mAsyncMoveTimer    = None
		self.mTestTime          = 0

		self.mMaxChannelNum		= E_INDEX_JUMP_MAX
		self.mIsOk              = E_DIALOG_STATE_CANCEL


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mCtrlLblMoveToNum	= self.getControl( E_MOVETOJUMP_NUM_ID )
		self.mCtrlLblMoveToName	= self.getControl( E_RESERVED_ID )
		self.mCtrlLblMoveToTime	= self.getControl( E_MOVETOJUMP_TIME_ID )
		self.mCtrlProgress      = self.getControl( E_PROGRESS_ID )

		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset()
		self.mJumpIFrame = 0

		self.SetLabelMoveToTime( )
		self.SetLabelMoveToName( )

		self.SetLabelMoveToNumber( )
		self.GetPreviewMove( )
		self.RestartAsyncMove( )

	def onAction( self, aAction ) :
		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.CloseDialog( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
			
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.CloseDialog( )

		elif actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 :
			inputString = '%d' % ( actionId - Action.REMOTE_0 )
			self.mMoveToNumber += inputString
			self.mMoveToNumber = '%d' % int( self.mMoveToNumber )
			if int( self.mMoveToNumber ) > self.mMaxChannelNum :
				self.mMoveToNumber = inputString
			self.SetLabelMoveToNumber( )
			self.GetPreviewMove( )
			self.RestartAsyncMove( )


		elif actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :
			inputNum = actionId - (Action.ACTION_JUMP_SMS2 - 2)
			if inputNum >= 2 and inputNum <= 9 :
				inputString = '%d' % inputNum
				self.mMoveToNumber += inputString
				self.mMoveToNumber = '%d' % int( self.mMoveToNumber )
				if int( self.mMoveToNumber ) > self.mMaxChannelNum :
					self.mMoveToNumber = inputString
				self.SetLabelMoveToNumber( )
				self.GetPreviewMove( )
				self.RestartAsyncMove( )

	def onClick( self, aControlId ) :
		if aControlId == E_BUTTON_OK :
			self.CloseDialog( )


	def onFocus( self, aControlId ) :
		pass

		
	def SetDialogProperty( self, aMoveToFirstNum, aMoveToMax, aTestTime = None ) :
		self.mMoveToNumber	= aMoveToFirstNum
		self.mMaxChannelNum = aMoveToMax

		if aTestTime:
			self.mTestTime = aTestTime


	def SetLabelMoveToNumber( self ) :
		label = '%s%%'% self.mMoveToNumber
		self.mCtrlLblMoveToNum.setLabel( label )

	def SetLabelMoveToName( self, aMoveName='' ) :
		self.mCtrlLblMoveToName.setLabel( aMoveName )

	def SetLabelMoveToTime( self, aMoveTime='' ) :
		self.mCtrlLblMoveToTime.setLabel( aMoveTime )

	def SetPogress( self, aPercent=0 ) :
		self.mCtrlProgress.setPercent( aPercent )

	def GetPreviewMove( self ):
		status = None
		status = self.mDataCache.Player_GetStatus()

		if not status :
			return -1

		#calculate current position
		moveTime = (status.mEndTimeInMs - status.mStartTimeInMs) * (int(self.mMoveToNumber) / 100.0)
		self.mJumpIFrame = status.mStartTimeInMs + moveTime

		if self.mJumpIFrame > status.mEndTimeInMs:
			#self.mJumpIFrame = status.mEndTimeInMs
			self.mJumpIFrame = 0
		elif self.mJumpIFrame < status.mStartTimeInMs :
			#self.mJumpIFrame = status.mStartTimeInMs
			self.mJumpIFrame = 0


		lbl_timeP = ''
		if self.mJumpIFrame :
			if status.mMode == ElisEnum.E_MODE_TIMESHIFT :
				ret = EpgInfoClock(FLAG_CLOCKMODE_HMS, (self.mJumpIFrame/1000.0), 0)
				lbl_timeP = ret[0]
			else :
				lbl_timeP = EpgInfoClock(FLAG_CLOCKMODE_HHMM, (self.mJumpIFrame/1000.0), 0)

			LOG_TRACE('move time[%s] iframe[%s] progress[%s]'% (lbl_timeP, self.mJumpIFrame, self.mMoveToNumber) )
		else :
			lbl_timeP = 'Move Fail'

		self.SetLabelMoveToTime( lbl_timeP )
		self.SetPogress( int(self.mMoveToNumber) )

	def GetMoveToJump( self ):
		return self.mJumpIFrame

	def IsOK( self ) :
		return self.mIsOk

	def RestartAsyncMove( self ) :
		self.StopAsyncMove( )
		self.StartAsyncMove( )


	def StartAsyncMove( self ) :
		self.mAsyncMoveTimer = threading.Timer( 3, self.AsyncToMove ) 				
		self.mAsyncMoveTimer.start()


	def StopAsyncMove( self ) :
		if self.mAsyncMoveTimer	and self.mAsyncMoveTimer.isAlive() :
			self.mAsyncMoveTimer.cancel()
			del self.mAsyncMoveTimer

		self.mAsyncMoveTimer  = None


	def AsyncToMove( self ) :
		self.mIsOk = E_DIALOG_STATE_YES
		self.CloseDialog( )

