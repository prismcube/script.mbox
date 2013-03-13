from pvr.gui.WindowImport import *
import time


E_INPUT_LABEL			= 4
E_DIALOG_HEADER			= 1

E_START_ID_NUMBER		= 100
MAX_PINCODE_LENGTH		= 4


class DialogInputPincode( BaseDialog ) :
	E_TUNE_NEXT_CHANNEL     = 1
	E_TUNE_PREV_CHANNEL		= 2
	E_SHOW_EPG_WINDOW       = 3
	E_SHOW_ARCHIVE_WINDOW   = 4
	E_TUNE_TVRADIO_TOGGLE   = 5

	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
	
		self.mTitleLabel = ''
		self.mCtrlInputLabel = None
		self.mInputNumber = ''
		self.mNextAction = 0
		self.mCheckStatus = None


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.mIsOk = E_DIALOG_STATE_CANCEL
		self.mNextAction = 0
		self.mIsValidateThread = None

		self.DrawKeyboard( )
		
		self.getControl( E_DIALOG_HEADER ).setLabel( self.GetTitleLabel( ) )
		self.mCtrlInputLabel = self.getControl( E_INPUT_LABEL )
		self.mInputNumber = ''		
		self.mCtrlInputLabel.setLabel( self.mInputNumber )

		if self.mCheckStatus == E_CHECK_PARENTLOCK :
			self.mIsValidateThread = self.CheckValidate( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return
		
		if actionId == Action.ACTION_PREVIOUS_MENU :
			if WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_LIVE_PLATE :
				WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).StartAutomaticHide( )
			self.Close( )
			self.CloseDialog( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 :		# number
			self.InputNumber( int( actionId ) - Action.REMOTE_0 )

		elif actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :
			self.InputNumber( actionId + 2 - Action.ACTION_JUMP_SMS2 )
			
		elif actionId == Action.ACTION_PARENT_DIR : 							# back space
			self.DeleteValue( )

		elif actionId == Action.ACTION_PAGE_UP:
			try :
				if WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_LIVE_PLATE or \
				   WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_NULLWINDOW :
					self.mNextAction = self.E_TUNE_NEXT_CHANNEL
					self.Close( )
					self.CloseDialog( )
					
			except Exception, e :
				LOG_TRACE( 'Exception %s' %e )
			
		elif actionId == Action.ACTION_PAGE_DOWN :
			try :
				if WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_LIVE_PLATE or \
				   WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_NULLWINDOW :
					self.mNextAction = self.E_TUNE_PREV_CHANNEL
					self.Close( )
					self.CloseDialog( )

			except Exception, e :
				LOG_TRACE( 'Exception %s' %e )

		elif actionId == Action.ACTION_SHOW_INFO :
			if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
				LOG_TRACE( 'Try again after stopping all your recordings first' )
			else :
				if WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_LIVE_PLATE or \
				   WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_NULLWINDOW :
					self.mNextAction = self.E_SHOW_EPG_WINDOW
					self.Close( )
					self.CloseDialog( )

		elif actionId == Action.ACTION_MBOX_ARCHIVE :
			if HasAvailableRecordingHDD( ) == False :
				return

			if WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_LIVE_PLATE or \
			   WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_NULLWINDOW :
				self.mNextAction = self.E_SHOW_ARCHIVE_WINDOW
				self.Close( )
				self.CloseDialog( )

		elif actionId == Action.ACTION_MBOX_TVRADIO :
			if self.mDataCache.Player_GetStatus( ).mMode == ElisEnum.E_MODE_PVR :
				LOG_TRACE( 'Try again after stopping all your recordings first' )
			else :
				if WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_LIVE_PLATE or \
				   WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_NULLWINDOW :
					self.mNextAction = self.E_TUNE_TVRADIO_TOGGLE
					self.Close( )
					self.CloseDialog( )


	def onClick( self, aControlId ) :
		if aControlId >= E_START_ID_NUMBER and aControlId <= E_START_ID_NUMBER + 9 :
			self.InputNumber( aControlId - E_START_ID_NUMBER )


	def onFocus( self, aControlId ):
		pass


	def Close( self ) :
		if self.mIsValidateThread :
			self.mCheckStatus = False
			self.mIsValidateThread.join( )


	def IsOK( self ) :
		return self.mIsOk


	def GetNextAction( self ) :
		return self.mNextAction


	def DrawKeyboard( self ):
		for i in range( 10 ) :
			self.getControl( E_START_ID_NUMBER + i ).setLabel( '%s' % i )


	def GetNumber( self ) :
		return int( self.mInputNumber )


	def GetTitleLabel( self ) :
		return self.mTitleLabel


	def SetTitleLabel( self, aTitleLabel ) :
		self.mTitleLabel = aTitleLabel


	def SetCheckStatus( self, aCheck = None ) :
		self.mCheckStatus = aCheck


	def InputNumber( self, aNumber ) :
		newString ='%s' %aNumber
		
		self.mInputNumber = self.mInputNumber + newString

		length = len( self.mInputNumber )

		try :
			if length >= MAX_PINCODE_LENGTH :
				#CheckPineCode
				savedPincode = ElisPropertyInt( 'PinCode', self.mCommander ).GetProp( )
				LOG_TRACE( 'pinValue = %d : %d' %( savedPincode, int( self.mInputNumber ) ) )
				if savedPincode == int( self.mInputNumber ) :
					self.mIsOk = E_DIALOG_STATE_YES
					self.Close( )
					xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )
				else : #Wrong PinCode
					self.mInputNumber = ''
					self.mCtrlInputLabel.setLabel( self.mInputNumber )					
					self.getControl( E_DIALOG_HEADER ).setLabel( MR_LANG( 'Please try again' ) )
			else :
				temp = '*'
				self.mCtrlInputLabel.setLabel( temp*length )

		except Exception, e :
			LOG_TRACE( 'Exception %s' %e )

		LOG_TRACE( 'InputNumber =%s' %self.mInputNumber )


	def DeleteValue( self ) :
		LOG_TRACE( 'InputNumber del=%s' %self.mInputNumber )
		length = len( self.mInputNumber )
		if length > 0 :
			self.mInputNumber = self.mInputNumber[:-1]
		LOG_TRACE( 'InputNumber del=%s' %self.mInputNumber )

		length = len( self.mInputNumber )
		if length > 0 :
			temp = '*'
			self.mCtrlInputLabel.setLabel( temp*length )

		else :
			self.mCtrlInputLabel.setLabel( '' )


	@RunThread
	def CheckValidate( self ) :
		isClose = False
		while self.mCheckStatus == E_CHECK_PARENTLOCK :
			iChannel = self.mDataCache.Channel_GetCurrent( )
			if ( iChannel and iChannel.mLocked ) or self.mDataCache.GetParentLock( ) :
				LOG_TRACE( 'Checked self : pincode parentLock True' )
				#pass
			else :
				isClose = True
				break

			time.sleep( 1 )


		if isClose :
			LOG_TRACE( '---------------------Checked self : parentLock False, Close dialog' )
			self.mCheckStatus = False
			self.mIsValidateThread = None
			xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )


