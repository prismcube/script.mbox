from pvr.gui.WindowImport import *


# Control IDs
E_LABEL_RECORD_NAME			= 101
E_LABEL_EPG_START_TIME		= 102
E_LABEL_EPG_END_TIME		= 103
E_BUTTON_ADD				= 200
E_BUTTON_CANCEL				= 202


class DialogAddTimer( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mEPG = None
		self.mIsOk = E_DIALOG_STATE_CANCEL


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.SetHeaderLabel( MR_LANG( 'Add Timer' ) )

		self.Reload( )
		self.mEventBus.Register( self )
		self.mIsOk = E_DIALOG_STATE_CANCEL
		

	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.GetFocusId( )
		if self.GlobalAction( actionId ) :
			return

		LOG_TRACE( 'actionId=%d' %actionId )
			
		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.Close( )

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN :
			if focusId == E_SETTING_DIALOG_BUTTON_CLOSE :
				self.setFocusId( E_BUTTON_ADD )
			elif focusId == E_BUTTON_ADD or focusId == E_BUTTON_CANCEL :
				self.setFocusId( E_SETTING_DIALOG_BUTTON_CLOSE )
			
		#elif actionId == Action.ACTION_MOVE_DOWN :
		#	if focusId == E_SETTING_DIALOG_BUTTON_CLOSE :
		#		self.setFocusId( E_BUTTON_ADD )


	def onClick( self, aControlId ) :
		focusId = self.getFocusId( )

		if focusId == E_BUTTON_ADD :
			self.mIsOk = E_DIALOG_STATE_YES
			xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )

		elif focusId == E_BUTTON_CANCEL or focusId == E_SETTING_DIALOG_BUTTON_CLOSE :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )


	def onFocus( self, aControlId ) :
		pass


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
	
