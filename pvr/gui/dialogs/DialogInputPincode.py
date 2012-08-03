from pvr.gui.WindowImport import *


E_INPUT_LABEL			= 4
E_DIALOG_HEADER			= 1

E_START_ID_NUMBER		= 100
MAX_PINCODE_LENGTH		= 4


class DialogInputPincode( BaseDialog ) :
	E_TUNE_NEXT_CHANNEL     = 1
	E_TUNE_PREV_CHANNEL		= 2

	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
	
		self.mTitleLabel = ''
		self.mCtrlInputLabel = None
		self.mInputNumber = ''
		self.mNextAction = 0


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		LOG_TRACE('+++++++++++++++++++++++++++++++++++++++++++++')			
		LOG_TRACE( '---------------- lael98 -----------------' )

		self.mIsOk = E_DIALOG_STATE_CANCEL
		self.mNextAction = 0		

		self.DrawKeyboard( )
		
		self.getControl( E_DIALOG_HEADER ).setLabel( self.GetTitleLabel( ) )
		self.mCtrlInputLabel = self.getControl( E_INPUT_LABEL )
		self.mInputNumber = ''		
		self.mCtrlInputLabel.setLabel( self.mInputNumber )
		LOG_TRACE('+++++++++++++++++++++++++++++++++++++++++++++')	


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )		

		LOG_TRACE( '---------------- lael98 actionId=%d -----------------' %actionId )
		LOG_TRACE( '---------------- lael98 Action.ACTION_JUMP_SMS2=%d -----------------' %Action.ACTION_JUMP_SMS2 )
		LOG_TRACE( '---------------- lael98 Action.REMOTE_0=%d -----------------' %Action.REMOTE_0 )		
		
		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			LOG_TRACE( '---------------- CloseDialog -----------------' )			
			self.CloseDialog( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 :		# number
			LOG_TRACE( '---------------- lael98 actionId=%d -----------------' %actionId )		
			self.InputNumber( actionId - Action.REMOTE_0 )

		elif actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :
			LOG_TRACE( '---------------- lael98 actionId=%d -----------------' %actionId )		
			self.InputNumber( actionId + 2 - Action.ACTION_JUMP_SMS2 )
			
		elif actionId == Action.ACTION_PARENT_DIR : 							# back space
			self.DeleteValue( )

		elif actionId == Action.ACTION_PAGE_UP:
			LOG_TRACE('+++++++++++++++++++++++++++++++++++++++++++++')	
			LOG_TRACE( '---------------- lael98 LastID=%d-----------------' %WinMgr.GetInstance( ).GetLastWindowID( )  )					
			try :
				if WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_LIVE_PLATE :
					LOG_TRACE('+++++++++++++++++++++++++++++++++++++++++++++')	
					self.mNextAction =  self.E_TUNE_NEXT_CHANNEL					
					self.CloseDialog( )
					
			except Exception, e :
				LOG_TRACE( 'Exception %s' %e )
			
		elif actionId == Action.ACTION_PAGE_DOWN :
			LOG_TRACE('+++++++++++++++++++++++++++++++++++++++++++++')	
			LOG_TRACE( '---------------- lael98 LastID=%d-----------------' %WinMgr.GetInstance( ).GetLastWindowID( )  )					
			try :
				if WinMgr.GetInstance( ).GetLastWindowID( ) == WinMgr.WIN_ID_LIVE_PLATE :
					LOG_TRACE('+++++++++++++++++++++++++++++++++++++++++++++')	
					self.mNextAction =  self.E_TUNE_PREV_CHANNEL										
					self.CloseDialog( )

			except Exception, e :
				LOG_TRACE( 'Exception %s' %e )


	def onClick( self, aControlId ) :
		if aControlId >= E_START_ID_NUMBER and aControlId <= E_START_ID_NUMBER + 9 :
			self.InputNumber( aControlId - E_START_ID_NUMBER )


	def IsOK( self ) :
		return self.mIsOk


	def GetNextAction( self ) :
		return self.mNextAction


	def onFocus( self, aControlId ):
		pass


	def DrawKeyboard( self ):
		for i in range( 10 ) :
			self.getControl( E_START_ID_NUMBER + i ).setLabel( '%s' % i )


	def GetNumber( self ) :
		return int( self.mInputNumber )


	def GetTitleLabel( self ) :
		return self.mTitleLabel


	def SetTitleLabel( self, aTitleLabel ) :
		self.mTitleLabel = aTitleLabel


	def InputNumber( self, aNumber ) :
		LOG_TRACE( '---------------- lael98 -----------------' )	
		LOG_TRACE( 'InputNumber=%s' %aNumber )

		newString ='%s' %aNumber
		
		LOG_TRACE( 'InputNumber #1=%s' %self.mInputNumber )
		self.mInputNumber = self.mInputNumber + newString

		length = len( self.mInputNumber )
		LOG_TRACE( 'LEN=%d' %length )				
		
		LOG_TRACE( 'InputNumber #2=%s' %self.mInputNumber )		

		try :
			if length >= MAX_PINCODE_LENGTH :
				LOG_TRACE( '' )
				#CheckPineCode
				savedPincode = ElisPropertyInt( 'PinCode', self.mCommander ).GetProp( )
				LOG_TRACE( 'pinValue = %d : %d' %( savedPincode, int( self.mInputNumber ) ) )
				if savedPincode == int( self.mInputNumber ) :
					LOG_TRACE( '' )				
					self.mIsOk = E_DIALOG_STATE_YES
					LOG_TRACE( '---------------- CloseDialog -----------------' )								
					self.CloseDialog( )
				else : #Wrong PinCode
					LOG_TRACE( '' )
					self.mInputNumber = ''
					self.mCtrlInputLabel.setLabel( self.mInputNumber )					
					self.getControl( E_DIALOG_HEADER ).setLabel( 'Wrong Pincode' )								
			else :
				LOG_TRACE( '' )
				temp = '*'
				self.mCtrlInputLabel.setLabel( temp*length )

		except Exception, e :
			LOG_TRACE( 'Exception %s' %e )

		LOG_TRACE( 'InputNumber #3=%s' %self.mInputNumber )


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


