from pvr.gui.WindowImport import *
import sys, inspect, time

class NullWindow( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mAsyncShowTimer = None


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		self.mGotoWinID = None
		self.mOnEventing= False

		if self.mInitialized == False :
			self.mInitialized = True

		self.mEventBus.Register( self )

		if E_SUPPROT_HBBTV == True :
			self.mCommander.AppHBBTV_Ready( 1 )

		currentStack = inspect.stack()
		LOG_TRACE( '+++++getrecursionlimit[%s] currentStack[%s]'% (sys.getrecursionlimit(), len(currentStack)) )
		LOG_TRACE( '+++++currentStackInfo[%s]'% (currentStack) )

		lastTime = time.time() + 7200
		lblStart = time.strftime('%H:%M:%S', time.localtime(WinMgr.GetInstance( ).mXbmcStartTime) )
		lblLast  = time.strftime('%H:%M:%S', time.localtime(lastTime) )
		lblTest  = time.strftime('%H:%M:%S', time.gmtime(lastTime - WinMgr.GetInstance( ).mXbmcStartTime) )
		LOG_TRACE( 'startTime[%s] lastTime[%s] TestTime[%s]'% (lblStart, lblLast, lblTest) )

		
	def onAction(self, aAction) :		
		actionId = aAction.getId( )
		self.GlobalAction( actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU:
			if self.mGotoWinID :
				if self.mGotoWinID == WinMgr.WIN_ID_ARCHIVE_WINDOW :
					self.mGotoWinID = None
					self.Close( )
					WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_ARCHIVE_WINDOW )
				return
				
			if ElisPropertyEnum( 'Lock Mainmenu', self.mCommander ).GetProp( ) == 0 :
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
				dialog.SetDialogProperty( 'PIN Code 4 digit', '', 4, True )
	 			dialog.doModal( )
	 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
	 				tempval = dialog.GetString( )
	 				if tempval == '' :
	 					return
					if int( tempval ) == ElisPropertyInt( 'PinCode', self.mCommander ).GetProp( ) :
						self.Close( )
						WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MAINMENU )
					else :
						dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
						dialog.SetDialogProperty( 'ERROR', 'ERROR PIN Code' )
			 			dialog.doModal( )
			 	return

			self.Close( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MAINMENU )
			
		elif actionId == Action.ACTION_PARENT_DIR:
			pass
			"""
			LOG_TRACE('previous channel')
			try :
				ch = self.mDataCache.mOldChannel
				self.mDataCache.Channel_SetCurrent( ch.mNumber, ch.mServiceType )

			except Exception, ex:
				print 'ERR prev channel'
			"""

		elif actionId == Action.ACTION_SELECT_ITEM:
			"""
			LOG_TRACE('key ok')
			if self.mDataCache.mStatusIsArchive :
				LOG_TRACE('Archive playing now')
				return -1
			"""
			self.Close( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_CHANNEL_LIST_WINDOW )

		elif actionId == Action.ACTION_MOVE_LEFT:
			print 'youn check ation left'
			window = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )
			window.SetAutomaticHide( True )
			self.Close( )			
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )

		elif actionId == Action.ACTION_SHOW_INFO:
			self.Close( )		
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_EPG_WINDOW )

		elif actionId == Action.ACTION_CONTEXT_MENU:
			status = None
			status = self.mDataCache.Player_GetStatus()
			gotoWinId = WinMgr.WIN_ID_LIVE_PLATE
			if status.mMode != ElisEnum.E_MODE_LIVE :
				gotoWinId = WinMgr.WIN_ID_TIMESHIFT_PLATE

			window = WinMgr.GetInstance( ).GetWindow( gotoWinId )
			window.SetAutomaticHide( False )
			self.Close( )
			WinMgr.GetInstance( ).ShowWindow( gotoWinId )

		elif actionId == Action.ACTION_PAGE_DOWN:
			if self.mDataCache.mStatusIsArchive :
				#LOG_TRACE('Archive playing now')
				return -1

			prevChannel = None
			prevChannel = self.mDataCache.Channel_GetPrev( self.mDataCache.Channel_GetCurrent( ) ) #self.mCommander.Channel_GetPrev( )
			if prevChannel :
				self.mDataCache.Channel_SetCurrent( prevChannel.mNumber, prevChannel.mServiceType )			
			
				window = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE )
				self.Close( )
				window.SetAutomaticHide( True )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )


		elif actionId == Action.ACTION_PAGE_UP:
			if self.mDataCache.mStatusIsArchive :
				#LOG_TRACE('Archive playing now')
				return -1

			nextChannel = None
			nextChannel = self.mDataCache.Channel_GetNext( self.mDataCache.Channel_GetCurrent( ) )
			if nextChannel :
				self.mDataCache.Channel_SetCurrent( nextChannel.mNumber, nextChannel.mServiceType )

				window = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE )
				self.Close( )
				window.SetAutomaticHide( True )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )
			
	
		elif actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9 or \
			actionId >= Action.ACTION_JUMP_SMS2 and actionId <= Action.ACTION_JUMP_SMS9 :

			aKey = actionId - (Action.ACTION_JUMP_SMS2 - 2)
			if actionId >= Action.REMOTE_0 and actionId <= Action.REMOTE_9:
				aKey = actionId - Action.REMOTE_0

			if self.mDataCache.mStatusIsArchive :
				#LOG_TRACE('Archive playing now')
				return -1

			if aKey == 0 :
				return -1

			GuiLock2(True)
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CHANNEL_JUMP )
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
				#LOG_TRACE('----------mode[%s] stop[%s] up/down[%s]'% (status.mMode, ret, self.mDataCache.mStatusIsArchive) )
				if ret :
					if status.mMode == ElisEnum.E_MODE_PVR :
						if self.mDataCache.mStatusIsArchive :
							self.mGotoWinID = WinMgr.WIN_ID_ARCHIVE_WINDOW
							self.mDataCache.mStatusIsArchive = False
							#LOG_TRACE('archive play, stop to go Archive')
						else :
							self.mGotoWinID = None
							self.mDataCache.mStatusIsArchive = False
							#LOG_TRACE('recording play, stop only(NullWindow)')

						#LOG_TRACE('up/down key released, goto win[%s]'% self.mGotoWinID)
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
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_START_RECORD )
				dialog.doModal( )
			else:
				msg = 'Already %d recording(s) running' %runningCount
				xbmcgui.Dialog( ).ok('Infomation', msg )
				
		
		elif actionId == Action.REMOTE_4:  #TEST : stop Record
			print 'open record dialog'
			runningCount = self.mCommander.Record_GetRunningRecorderCount( )
			LOG_TRACE( 'runningCount=%d' %runningCount )

			if  runningCount > 0 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_STOP_RECORD )
				dialog.doModal( )

		elif actionId == Action.REMOTE_1:  #TEST : bg test
		"""


	def onClick(self, aControlId) :
		pass
		#print "onclick( ): control %s" % aControlId


	def onFocus(self, aControlId) :
		pass
		#print "onFocus( ): control %s" % aControlId
		#self.mLastFocusId = aControlId


	@GuiLock
	def onEvent(self, aEvent):
		if self.mWinId == xbmcgui.getCurrentWindowId():
			#LOG_TRACE( 'NullWindow winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId()) )
			if aEvent.getName() == ElisEventPlaybackEOF.getName() :
				if self.mOnEventing :
					#LOG_TRACE('ignore event, mFlag_OnEvent[%s]'% self.mOnEventing)
					return -1

				self.mOnEventing = True

				if aEvent.mType == ElisEnum.E_EOF_END :
					#LOG_TRACE( 'EventRecv EOF_STOP' )
					xbmc.executebuiltin('xbmc.Action(stop)')

				self.mOnEventing = False

			elif aEvent.getName() == ElisEventChannelChangeResult.getName() :
				ch = self.mDataCache.Channel_GetCurrent( )
				if ch.mLocked :
					self.PincodeDialogLimit( self.mDataCache.mPropertyPincode )

		else:
			pass
			#LOG_TRACE( 'NullWindow winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId()) )


	def PincodeDialogLimit( self, aPincode ) :
		isUnlock = False
		try :
			self.mDataCache.Player_AVBlank( True, False )
			msg = MR_LANG('Input PIN Code')
			inputPin = ''

			GuiLock2(True)
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( msg, '', 4, True )
			dialog.doModal()
			GuiLock2(False)

			reply = dialog.IsOK()
			if reply == E_DIALOG_STATE_YES :
				inputPin = dialog.GetString()

			elif reply == E_DIALOG_STATE_CANCEL :
				return isUnlock

			if inputPin == None or inputPin == '' :
				inputPin = ''

			if inputPin == str('%s'% aPincode ) :
				isUnlock = True
				self.mDataCache.Player_AVBlank( False, False )

			else:
				msg1 = MR_LANG('Error')
				msg2 = MR_LANG('Wrong PIN Code')
				GuiLock2(True)
				xbmcgui.Dialog().ok( msg1, msg2 )
				GuiLock2(False)


		except Exception, e:
			LOG_TRACE( 'Error exception[%s]'% e )

		return isUnlock


	def RecordingStop( self ) :
		isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )

		if isRunRec > 0 :
			GuiLock2( True )
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_STOP_RECORD )
			dialog.doModal( )
			GuiLock2( False )

			isOK = dialog.IsOK()
			if isOK == E_DIALOG_STATE_YES :
				if self.mDataCache.GetChangeDBTableChannel( ) != -1 :
					time.sleep(1.5)
					isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )
					if isRunRec > 0 :
						#use zapping table, in recording
						self.mDataCache.mChannelListDBTable = E_TABLE_ZAPPING
						self.mDataCache.Channel_GetZappingList( )
						self.mDataCache.LoadChannelList( )
					else :
						self.mDataCache.mChannelListDBTable = E_TABLE_ALLCHANNEL
						self.mDataCache.LoadChannelList( )
						self.mDataCache.mCacheReload = True


	def Close( self ) :
		self.mEventBus.Deregister( self )

		if E_SUPPROT_HBBTV == True :
			self.mCommander.AppHBBTV_Ready( 0 )


	def GetKeyDisabled( self ) :
		return False
		

