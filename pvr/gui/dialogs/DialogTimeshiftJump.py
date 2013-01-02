from pvr.gui.WindowImport import *


E_MOVETOJUMP_NUM_ID  = 210
E_RESERVED_ID        = 211
E_MOVETOJUMP_TIME_ID = 212
E_PROGRESS_ID        = 213

FLAG_CLOCKMODE_ADMYHM  = 1
FLAG_CLOCKMODE_AHM     = 2
FLAG_CLOCKMODE_HMS     = 3
FLAG_CLOCKMODE_HHMM    = 4
FLAG_CLOCKMODE_INTTIME = 5


class DialogTimeshiftJump( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )	
		self.mMoveToNumber		= ''
		self.mAsyncMoveTimer    = None

		self.mMaxMoveNum		= E_INDEX_JUMP_MAX
		self.mIsOk              = E_DIALOG_STATE_CANCEL


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mCtrlLblMoveToNum	= self.getControl( E_MOVETOJUMP_NUM_ID )
		self.mCtrlLblMoveToName	= self.getControl( E_RESERVED_ID )
		self.mCtrlLblMoveToTime	= self.getControl( E_MOVETOJUMP_TIME_ID )
		self.mCtrlProgress      = self.getControl( E_PROGRESS_ID )

		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		self.mJumpIFrame = 0

		self.SetLabelMoveToTime( )
		self.SetLabelMoveToName( )

		self.SetLabelMoveToNumber( )
		self.GetPreviewMove( )
		self.RestartAsyncMove( )
		self.mIsOk = E_DIALOG_STATE_CANCEL


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.CloseDialog( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
			
		elif actionId == Action.ACTION_PARENT_DIR :
			self.CloseDialog( )

		elif actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 :
			inputString = '%d' % ( int( actionId ) - Action.REMOTE_0 )
			self.mMoveToNumber += inputString
			self.mMoveToNumber = '%d' % int( self.mMoveToNumber )
			if int( self.mMoveToNumber ) > self.mMaxMoveNum :
				self.mMoveToNumber = inputString

			self.SetLabelMoveToNumber( )
			self.GetPreviewMove( )
			self.RestartAsyncMove( )

		elif actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :
			inputNum = actionId - ( Action.ACTION_JUMP_SMS2 - 2 )

			if inputNum >= 2 and inputNum <= 9 :
				inputString = '%d' % inputNum
				self.mMoveToNumber += inputString
				self.mMoveToNumber = '%d' % int( self.mMoveToNumber )

				if int( self.mMoveToNumber ) > self.mMaxMoveNum :
					self.mMoveToNumber = inputString

				self.SetLabelMoveToNumber( )
				self.GetPreviewMove( )
				self.RestartAsyncMove( )


	def onClick( self, aControlId ) :
		pass


	def onFocus( self, aControlId ) :
		pass

		
	def SetDialogProperty( self, aMoveToFirstNum, aMoveToMax = E_INDEX_JUMP_MAX ) :
		self.mMoveToNumber	= aMoveToFirstNum
		self.mMaxMoveNum = aMoveToMax


	def SetLabelMoveToNumber( self ) :
		label = '%s%%'% self.mMoveToNumber
		self.mCtrlLblMoveToNum.setLabel( label )


	def SetLabelMoveToName( self, aMoveName = '' ) :
		self.mCtrlLblMoveToName.setLabel( aMoveName )


	def SetLabelMoveToTime( self, aMoveTime = '' ) :
		self.mCtrlLblMoveToTime.setLabel( aMoveTime )


	def SetPogress( self, aPercent = 0 ) :
		self.mCtrlProgress.setPercent( aPercent )


	def GetPreviewMove( self ):
		status = None
		status = self.mDataCache.Player_GetStatus( )

		if not status :
			return -1

		#calculate current position
		moveTime = ( status.mEndTimeInMs - status.mStartTimeInMs ) * ( int( self.mMoveToNumber ) / 100.0 )
		self.mJumpIFrame = status.mStartTimeInMs + moveTime

		if self.mJumpIFrame > status.mEndTimeInMs :
			self.mJumpIFrame = 0

		elif self.mJumpIFrame < status.mStartTimeInMs :
			self.mJumpIFrame = 0


		lbl_timeP = ''
		if self.mJumpIFrame :
			lbl_timeP = TimeToString( ( self.mJumpIFrame / 1000.0 ), TimeFormatEnum.E_HH_MM_SS )
			#LOG_TRACE('move time[%s] iframe[%s] progress[%s]'% (lbl_timeP, self.mJumpIFrame, self.mMoveToNumber) )
		else :
			lbl_timeP = MR_LANG( 'Move failed' )			

		self.SetLabelMoveToTime( lbl_timeP )
		self.SetPogress( int( self.mMoveToNumber ) )


	def GetMoveToJump( self ):
		return self.mJumpIFrame


	def IsOK( self ) :
		return self.mIsOk


	def RestartAsyncMove( self ) :
		self.StopAsyncMove( )
		self.StartAsyncMove( )


	def StartAsyncMove( self ) :
		self.mAsyncMoveTimer = threading.Timer( 3, self.AsyncToMove ) 				
		self.mAsyncMoveTimer.start( )


	def StopAsyncMove( self ) :
		if self.mAsyncMoveTimer	and self.mAsyncMoveTimer.isAlive( ) :
			self.mAsyncMoveTimer.cancel( )
			del self.mAsyncMoveTimer

		self.mAsyncMoveTimer  = None


	def AsyncToMove( self ) :
		self.mIsOk = E_DIALOG_STATE_YES
		xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )

