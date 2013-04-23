from pvr.gui.WindowImport import *


DIALOG_HEADER_LABEL				= 3005
DIALOG_BUTTON_CLOSE	= 6995


# Control IDs
E_LABEL_RECORD_NAME			= 102
E_LABEL_CHANNEL_NAME		= 101
E_BUTTON_ADD				= 200
E_BUTTON_CANCEL				= 202


class DialogAddTimer( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mEPG = None
		self.mIsOk = E_DIALOG_STATE_CANCEL


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.setProperty( 'DialogDrawFinished', 'False' )


		currentMode = self.mDataCache.Zappingmode_GetCurrent( )
		self.mChannelList = self.mDataCache.Channel_GetAllChannels( currentMode.mServiceType )

		#self.SetHeaderLabel( MR_LANG( 'Add Timer' ) )
		self.getControl( DIALOG_HEADER_LABEL ).setLabel( MR_LANG( 'Add Timer' ) )

		self.Reload( )
		self.mEventBus.Register( self )
		self.mIsOk = E_DIALOG_STATE_CANCEL

		self.setProperty( 'DialogDrawFinished', 'True' )
		

	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.GetFocusId( )
		if self.GlobalAction( actionId ) :
			return

		LOG_TRACE( 'actionId=%d' %actionId )
			
		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.Close( )

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN :
			if focusId == DIALOG_BUTTON_CLOSE :
				self.setFocusId( E_BUTTON_ADD )
			elif focusId == E_BUTTON_ADD or focusId == E_BUTTON_CANCEL :
				self.setFocusId( DIALOG_BUTTON_CLOSE )
			
		#elif actionId == Action.ACTION_MOVE_DOWN :
		#	if focusId == DIALOG_BUTTON_CLOSE :
		#		self.setFocusId( E_BUTTON_ADD )


	def onClick( self, aControlId ) :
		focusId = self.getFocusId( )

		if focusId == E_BUTTON_ADD :
			self.mIsOk = E_DIALOG_STATE_YES
			self.Close( )

		elif focusId == E_BUTTON_CANCEL or focusId == DIALOG_BUTTON_CLOSE :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.Close( )


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

				channel = None
				if self.mChannelList  and len( self.mChannelList ) > 0 :
					for channel in self.mChannelList :
						if channel.mSid == self.mEPG.mSid and  channel.mTsid == self.mEPG.mTsid and channel.mOnid == self.mEPG.mOnid :
							break;

				if channel :
					self.getControl( E_LABEL_CHANNEL_NAME ).setLabel( '%04d %s' %( channel.mNumber, channel.mName ) )
				else :
					self.getControl( E_LABEL_CHANNEL_NAME ).setLabel(  MR_LANG('Unknown')  )

				self.getControl( E_LABEL_RECORD_NAME ).setLabel( '(%s~%s) %s' %( TimeToString( startTime, TimeFormatEnum.E_HH_MM ), TimeToString( endTime, TimeFormatEnum.E_HH_MM ), self.mEPG.mEventName ) )

				#self.getControl( E_LABEL_EPG_START_TIME ).setLabel( MR_LANG( 'Start Time' ) + ': %s' %TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
				#self.getControl( E_LABEL_EPG_END_TIME ).setLabel( MR_LANG( 'End Time' ) + ': %s' %TimeToString( endTime, TimeFormatEnum.E_HH_MM ) )
			
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
	
