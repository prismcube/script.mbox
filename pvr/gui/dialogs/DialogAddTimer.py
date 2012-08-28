from pvr.gui.WindowImport import *


# Control IDs
E_LABEL_RECORD_NAME			= 101
E_LABEL_EPG_START_TIME		= 102
E_LABEL_EPG_END_TIME		= 103
E_BUTTON_ADD				= 200
E_BUTTON_CANCEL				= 201



class DialogAddTimer( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mEPG = None

	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		self.SetHeaderLabel( MR_LANG( 'Add Timer' ) )		
		self.mIsOk = E_DIALOG_STATE_CANCEL		

		self.Reload( )
		self.mEventBus.Register( self )
		

	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.GetFocusId( )
		self.GlobalAction( actionId )		

		LOG_TRACE( 'actionId=%d' %actionId )
			
		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.Close( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.Close( )

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

		LOG_TRACE( 'DialogRecord focusId=%d' %focusId )
		if focusId == E_BUTTON_ADD :
			self.mIsOk = E_DIALOG_STATE_YES
			self.Close( )

		elif focusId == E_BUTTON_CANCEL :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.Close( )


	def onFocus( self, aControlId ) :
		pass


	@GuiLock	
	def onEvent( self, aEvent ) :
		pass
		"""
		if xbmcgui.getCurrentWindowDialogId( ) == self.winId :
			print 'Do Event'
			pass
		"""


	def SetEPG( self, aEPG ) :
		self.mEPG = aEPG


	def IsOK( self ) :
		return self.mIsOk


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.CloseDialog( )


	def Reload( self ) :

		try :
			if self.mEPG != None and self.mEPG.mError == 0 :
				#self.mEPG.printdebug( )		

				localOffset = self.mDataCache.Datetime_GetLocalOffset( )
				localTime = self.mDataCache.Datetime_GetLocalTime( )

				startTime = self.mEPG.mStartTime + localOffset
				endTime =  startTime  + self.mEPG.mDuration
			

				LOG_TRACE( 'START : %s' %TimeToString( startTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
				LOG_TRACE( 'CUR : %s' %TimeToString( localTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )			
				LOG_TRACE( 'END : %s' %TimeToString( endTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )			
				self.getControl( E_LABEL_RECORD_NAME ).setLabel( '%s' %self.mEPG.mEventName )

				self.getControl( E_LABEL_EPG_START_TIME ).setLabel( MR_LANG( 'Start Time' ) + ': %s' %TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
				self.getControl( E_LABEL_EPG_END_TIME ).setLabel( MR_LANG( 'End Time' ) + ': %s' %TimeToString( endTime, TimeFormatEnum.E_HH_MM ) )
			
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex )


	"""
	def AddRecord( self ):
		LOG_TRACE('')

		ret = self.mDataCache.Timer_AddEPGTimer( self.mEPG )
		self.Close( )

		if ret == False :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			xbmcgui.Dialog().ok('Failure', 'Start Record Fail' )

	"""
	
