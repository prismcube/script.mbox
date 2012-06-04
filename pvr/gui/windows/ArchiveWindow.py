from pvr.gui.WindowImport import *
 

BUTTON_ID_VIEW_MODE				= 100
BUTTON_ID_SORT_MODE				= 101
TOGGLEBUTTON_ID_ASC				= 102
RADIIOBUTTON_ID_EXTRA			= 103
LIST_ID_COMMON_RECORD			= 3400
LIST_ID_THUMBNAIL_RECORD		= 3410
LIST_ID_POSTERWRAP_RECORD		= 3420
LIST_ID_FANART_RECORD			= 3430


E_VIEW_LIST						= 0
E_VIEW_THUMBNAIL				= 1
E_VIEW_POSTER_WRAP				= 2
E_VIEW_FANART					= 3
E_VIEW_END						= 4

E_SORT_DATE						= 0
E_SORT_CHANNEL					= 1
E_SORT_TITLE					= 2
E_SORT_DURATION					= 3
E_SORT_END						= 4


CONTEXT_PLAY					= 0
CONTEXT_PLAY_FROM_BEGINNIG		= 1
CONTEXT_DELETE					= 2
CONTEXT_DELETE_ALL				= 3
CONTEXT_LOCK					= 4
CONTEXT_UNLOCK					= 5
CONTEXT_RENAME					= 6
CONTEXT_START_MARK				= 7
CONTEXT_CLEAR_MARK				= 8



MININUM_KEYWORD_SIZE			= 3


class ArchiveWindow( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mSelectRecordKey = -1
		self.mExitByPlay = False

	
	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( 'Archive' )

		self.mRecordCount = 0
		self.mSelectedIndex = 0
		self.mRecordList = [] 
		self.mSortList = [] 		
		self.mRecordListItems = []
		self.mLastFocusItem = -1

		self.mServiceType =  self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( ).mServiceType

		try :		
			self.mViewMode = int( GetSetting( 'VIEW_MODE' ) )
			self.mCtrlViewMode = self.getControl( BUTTON_ID_VIEW_MODE )

			LOG_TRACE('LAEL98 self.mCtrlViewMode =%s' %self.mCtrlViewMode )			

			self.mSortMode = int( GetSetting( 'SORT_MODE' ) )		
			self.mCtrlSortMode = self.getControl( BUTTON_ID_SORT_MODE )

			self.mAscending = []
			self.mAscending = [False,False,False,False,False]

			self.mAscending[E_SORT_DATE] = False
			self.mAscending[E_SORT_CHANNEL] = True
			self.mAscending[E_SORT_TITLE] = True
			self.mAscending[E_SORT_DURATION] = False


			self.mCtrlCommonList = self.getControl( LIST_ID_COMMON_RECORD )
			self.mCtrlThumbnailList = self.getControl( LIST_ID_THUMBNAIL_RECORD )
			self.mCtrlPosterwrapList = self.getControl( LIST_ID_POSTERWRAP_RECORD )
			self.mCtrlFanartList = self.getControl( LIST_ID_FANART_RECORD )
		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)


		self.Load( )
		if self.mRecordCount == 0 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( 'Error', 'Play list is Empty' )
			dialog.doModal( )
			self.SetVideoRestore( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MAINMENU )

		self.UpdateAscending()
		self.UpdateViewMode( )
		
		self.InitControl( )

		self.UpdateList( )
		self.SelectLastRecordKey( )		

		self.mInitialized = True
		

	def onAction( self, aAction ) :
		if self.mRecordCount == 0 :
			return
		focusId = self.GetFocusId( )
		actionId = aAction.getId( )
		self.GlobalAction( actionId )		


		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.SetVideoRestore( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_MAINMENU )

		elif actionId == Action.ACTION_SELECT_ITEM :
			if focusId  == LIST_ID_COMMON_RECORD or focusId  == LIST_ID_THUMBNAIL_RECORD or focusId  == LIST_ID_POSTERWRAP_RECORD or focusId  == LIST_ID_FANART_RECORD:
				if	self.mMarkMode == True	:
					self.DoMarkToggle( )
				else :			
					self.StartRecordPlayback( )

		elif actionId == Action.ACTION_MOVE_RIGHT or actionId == Action.ACTION_MOVE_LEFT :
			if focusId == LIST_ID_POSTERWRAP_RECORD or focusId  == LIST_ID_FANART_RECORD or focusId  == LIST_ID_THUMBNAIL_RECORD:
				self.UpdateSelectedPosition( )

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN :
			if focusId  == LIST_ID_COMMON_RECORD or focusId  == LIST_ID_THUMBNAIL_RECORD :
				self.UpdateSelectedPosition( )
				if focusId  == LIST_ID_COMMON_RECORD :
					self.UpdateArchiveInfomation( )

		elif actionId == Action.ACTION_CONTEXT_MENU:
			self.ShowContextMenu( )

	
	def onClick( self, aControlId ) :
		if self.mRecordCount == 0 :
			return
		LOG_TRACE( 'aControlId=%d' % aControlId )

		if aControlId == BUTTON_ID_VIEW_MODE :
			self.RestoreLastRecordKey( )		
			self.mViewMode += 1
			if self.mViewMode >= E_VIEW_END :
				self.mViewMode = 0 

			SetSetting( 'VIEW_MODE','%d' %self.mViewMode )
			self.UpdateViewMode( )
			self.InitControl( )
			self.UpdateList( )
			self.SelectLastRecordKey( )						
		
		elif aControlId == BUTTON_ID_SORT_MODE :
			self.RestoreLastRecordKey( )		
			self.mSortMode += 1
			if self.mSortMode >= E_SORT_END :
				self.mSortMode = 0 
				
			SetSetting( 'SORT_MODE','%d' %self.mSortMode ) 								
			self.UpdateSortMode( )
			self.InitControl( )			
			self.UpdateAscending( )
			self.UpdateList( )
			self.SelectLastRecordKey( )			
			
		elif aControlId == TOGGLEBUTTON_ID_ASC :
			self.RestoreLastRecordKey( )
			LOG_TRACE('Mode=%d' % self.mSortMode )
			LOG_TRACE('mAscending=%d' %self.mAscending[self.mSortMode] )
			if self.mAscending[self.mSortMode] == True :
				self.mAscending[self.mSortMode] = False
			else :
				self.mAscending[self.mSortMode] = True

			self.UpdateAscending( )
			self.UpdateList( )
			self.SelectLastRecordKey( )						

		elif aControlId == RADIIOBUTTON_ID_EXTRA :
			pass
		


	def onFocus(self, controlId):

		if self.mInitialized == False :
			return


	@GuiLock
	def onEvent(self, aEvent):
		pass


	def InitControl( self ) :

		LOG_TRACE('LAEL98')		
		if self.mViewMode == E_VIEW_LIST :
			self.mCtrlViewMode.setLabel('VIEW: LIST')
			LOG_TRACE('LAEL98')		
		elif self.mViewMode == E_VIEW_THUMBNAIL :			
			self.mCtrlViewMode.setLabel('VIEW: THUMBNAIL')		
		elif self.mViewMode == E_VIEW_POSTER_WRAP :			
			self.mCtrlViewMode.setLabel('VIEW: POSTER_WRAP')		
		elif self.mViewMode == E_VIEW_FANART :			
			self.mCtrlViewMode.setLabel('VIEW: FANART')		
		else :
			LOG_WARN('Unknown view mode')

		LOG_TRACE('LAEL98')					
		if self.mSortMode == E_SORT_DATE :
			LOG_TRACE('LAEL98')				
			self.mCtrlSortMode.setLabel('SORT: DATE')
		elif self.mSortMode == E_SORT_CHANNEL :			
			self.mCtrlSortMode.setLabel('SORT: CHANNEL')		
		elif self.mSortMode == E_SORT_TITLE :			
			self.mCtrlSortMode.setLabel('SORT: TITLE')		
		elif self.mSortMode == E_SORT_DURATION :			
			self.mCtrlSortMode.setLabel('SORT: DURATION')		
		else :
			LOG_WARN('Unknown sort mode')

		LOG_TRACE('LAEL98')					


	def UpdateViewMode( self ) :
		LOG_TRACE('--------------------- self.mViewMode=%d' %self.mViewMode)
		if self.mViewMode == E_VIEW_LIST :
			LOG_TRACE('LAEL98')
			self.mWin.setProperty( 'ViewMode', 'common' )
			LOG_TRACE('LAEL98')
		elif self.mViewMode == E_VIEW_THUMBNAIL :			
			self.mWin.setProperty( 'ViewMode', 'thumbnail' )
		elif self.mViewMode == E_VIEW_POSTER_WRAP :			
			self.mWin.setProperty( 'ViewMode', 'posterwrap' )
		elif self.mViewMode == E_VIEW_FANART :			
			self.mWin.setProperty( 'ViewMode', 'panart' )
		else :
			self.mViewMode = E_VIEW_LIST 		
			self.mWin.setProperty( 'ViewMode', 'common' )
		

	def UpdateSortMode( self ) :
		LOG_TRACE('---------------------')


	def UpdateAscending( self ) :
		LOG_TRACE('--------------------- %d ' %self.mAscending[self.mSortMode])	
		if self.mAscending[self.mSortMode] == True :
			self.mWin.setProperty( 'Ascending', 'true' )
		else :
			self.mWin.setProperty( 'Ascending', 'false' )
	

	def Flush( self ) :
		self.mRecordCount = 0
		self.mRecordList = []
		self.mSortList = []		


	def Load( self ) :

		self.mMarkMode = False

		LOG_TRACE('----------------------------------->')
		try :
			self.mRecordList = self.mDataCache.Record_GetList( self.mServiceType )
			if self.mRecordList == None :
				self.mRecordCount = 0
			else :
				self.mRecordCount = len( self.mRecordList  )

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)



	def UpdateList( self ) :
		LOG_TRACE('UpdateList Start')
		try :
			if not self.mRecordList or self.mRecordList == None :
				self.mRecordList = []

			if self.mSortMode == E_SORT_DATE :
				self.mRecordList.sort( self.ByDate )
			elif self.mSortMode == E_SORT_CHANNEL :
				self.mRecordList.sort( self.ByChannel )

			elif self.mSortMode == E_SORT_TITLE :
				self.mRecordList.sort( self.ByTitle )

			elif self.mSortMode == E_SORT_DURATION :
				self.mRecordList.sort( self.ByDuration )
			else :
				LOG_WARN('Unknown sort mode')		
				self.mSortMode = 0
				self.mRecordList.sort( self.ByDate )

			if self.mAscending[self.mSortMode] == False :
				self.mRecordList.reverse()

			self.mCtrlCommonList.reset( )
			self.mCtrlThumbnailList.reset( )
			self.mCtrlPosterwrapList.reset( )
			self.mCtrlFanartList.reset( )

			self.mRecordListItems = []
			for i in range( len( self.mRecordList ) ) :
				recInfo = self.mRecordList[i]
				#recInfo.printdebug()
				channelName = 'P%04d.%s' %(recInfo.mChannelNo, recInfo.mChannelName,)
				#recItem = xbmcgui.ListItem( '1234567890abcdefghijklmnopqrstuvwxyz123456789abcdefghijklmnopqrstuvwxyz', '1234567890abcdefghijklmnopqrstuvwxyz123456789abcdefghijklmnopqrstuvwxyz' )
				recItem = xbmcgui.ListItem( channelName, recInfo.mRecordName )
				#if i == 0 :
				#	recItem.setProperty('RecIcon', 'test.png')
				#else :
				recItem.setProperty('RecDate', TimeToString( recInfo.mStartTime ))
				recItem.setProperty('RecDuration', '%dm' %( recInfo.mDuration/60 ) )
				
				if recInfo.mLocked :
					recItem.setProperty('Locked', 'True')
					recItem.setProperty('RecIcon', 'IconNotAvailable.png')
				else :
					recItem.setProperty('Locked', 'False')
					recItem.setProperty('RecIcon', 'RecIconSample.jpg')					

				recItem.setProperty('Marked', 'False')
					
				self.mRecordListItems.append( recItem )

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)

		if self.mViewMode == E_VIEW_LIST :
			self.SetPipScreen( )		
			self.mCtrlCommonList.addItems( self.mRecordListItems )		
			#self.setFocusId( LIST_ID_COMMON_RECORD )
		elif self.mViewMode == E_VIEW_THUMBNAIL :
			self.SetVideoRestore( )		
			self.mCtrlThumbnailList.addItems( self.mRecordListItems )		
			#self.setFocusId( LIST_ID_THUMBNAIL_RECORD )
		elif self.mViewMode == E_VIEW_POSTER_WRAP :
			self.SetVideoRestore( )		
			self.mCtrlPosterwrapList.addItems( self.mRecordListItems )		
			#self.setFocusId( LIST_ID_POSTERWRAP_RECORD )
		elif self.mViewMode == E_VIEW_FANART :
			self.SetVideoRestore( )		
			self.mCtrlFanartList.addItems( self.mRecordListItems )		
			#self.setFocusId( LIST_ID_FANART_RECORD )
		else :
			LOG_WARN('Unknown view mode')

		LOG_TRACE('UpdateList END')


	def ByDate( self, aRec1, aRec2 ) :
		return cmp( aRec1.mStartTime, aRec2.mStartTime )
		

	def ByChannel( self, aRec1, aRec2 ) :
		return cmp( aRec1.mChannelNo, aRec2.mChannelNo )


	def ByTitle( self, aRec1, aRec2 ) :
		return cmp( aRec1.mRecordName, aRec2.mRecordName )


	def ByDuration( self, aRec1, aRec2 ) :
		return cmp( aRec1.mDuration, aRec2.mDuration )


	@RunThread
	def CurrentTimeThread(self):
		pass


	@GuiLock
	def UpdateLocalTime( self ) :
		pass


		"""
		try:
			self.mLocalTime = self.mCommander.Datetime_GetLocalTime( )


			if self.mNavEpg :
				endTime = self.mNavEpg.mStartTime + self.mNavEpg.mDuration
		
				pastDuration = endTime - self.mLocalTime
				if pastDuration < 0 :
					pastDuration = 0

				if self.mNavEpg.mDuration > 0 :
					percent = pastDuration * 100/self.mNavEpg.mDuration
				else :
					percent = 0

				#print 'percent=%d' %percent
				self.mCtrlProgress.setPercent( percent )

		except Exception, e :
			print '[%s:%s] Error exception[%s]'% (	\
				self.__file__,						\
				currentframe().f_lineno,			\
				e )

			self.mLocalTime = 0
		"""


	def StartRecordPlayback( self, aResume=True ) :
		selectedPos = self.GetSelectedPosition( )
		if self.mLastFocusItem == selectedPos :
			self.SetVideoRestore( )
			WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )
		else :		
			if selectedPos >= 0 and selectedPos < len( self.mRecordList ):
				recInfo = self.mRecordList[selectedPos]
				if recInfo.mLocked == True :
					if self.CheckPincode() == False :
						return False
				
				if aResume == True :
					#ToDO
					self.mDataCache.Player_StartInternalRecordPlayback( recInfo.mRecordKey, self.mServiceType, 0, 100 )
				else :
					self.mDataCache.Player_StartInternalRecordPlayback( recInfo.mRecordKey, self.mServiceType, 0, 100 )			

			self.mDataCache.SetKeyDisabled( True, recInfo )
			self.RestoreLastRecordKey( )
			self.mLastFocusItem = selectedPos


	def GetSelectedPosition( self ) :
		position  = -1 

		if self.mViewMode == E_VIEW_LIST :
			position = self.mCtrlCommonList.getSelectedPosition( )		
		elif self.mViewMode == E_VIEW_THUMBNAIL :
			position = self.mCtrlThumbnailList.getSelectedPosition( )		
		elif self.mViewMode == E_VIEW_POSTER_WRAP :
			position = self.mCtrlPosterwrapList.getSelectedPosition( )		
		elif self.mViewMode == E_VIEW_FANART :
			position = self.mCtrlFanartList.getSelectedPosition( )		
		else :
			position = -1

		return position


	def GetMarkedList( self ) :
		markedList = []

		if self.mRecordListItems == None :
			self.UpdateList( )
			return markedList

		count = len( self.mRecordListItems )

		for i in range( count ) :
			listItem = self.mRecordListItems[i]
			if listItem.getProperty('Marked') == 'True' :
				markedList.append( i )

		return markedList


	def ShowContextMenu( self ) :
		try :
			selectedPos = self.GetSelectedPosition()
			context = []

			markedList = self.GetMarkedList()
			
			if markedList and len( markedList ) > 0 :
				context.append( ContextItem( 'Delete', CONTEXT_DELETE ) )
				context.append( ContextItem( 'Delete All', CONTEXT_DELETE_ALL ) )
				context.append( ContextItem( 'Lock', CONTEXT_LOCK ) )
				context.append( ContextItem( 'Unlock', CONTEXT_UNLOCK ) )	
				context.append( ContextItem( 'Clear Marked Items', CONTEXT_CLEAR_MARK ) )	
				
			elif selectedPos >= 0 and selectedPos < len( self.mRecordList ) :
				recordInfo = self.mRecordList[ selectedPos ]		
				context.append( ContextItem( 'Play', CONTEXT_PLAY ) )
				context.append( ContextItem( 'Play from beginning', CONTEXT_PLAY_FROM_BEGINNIG ) )
				context.append( ContextItem( 'Delete', CONTEXT_DELETE ) )
				context.append( ContextItem( 'Delete All', CONTEXT_DELETE_ALL ) )				
				if recordInfo.mLocked:
					context.append( ContextItem( 'Unlock', CONTEXT_UNLOCK ) )
				else :
					context.append( ContextItem( 'Lock', CONTEXT_LOCK ) )

				context.append( ContextItem( 'Rename', CONTEXT_RENAME ) )
				context.append( ContextItem( 'Start Mark', CONTEXT_START_MARK ) )

			else :
				return
				
			GuiLock2( True )
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context )
			dialog.doModal( )
			GuiLock2( False )
			
			contextAction = dialog.GetSelectedAction()
			self.DoContextAction( contextAction ) 

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)


	def DoContextAction( self, aContextAction ) :
		LOG_TRACE('aContextAction=%d' %aContextAction )

		if aContextAction == CONTEXT_PLAY :
			self.StartRecordPlayback( True )

		elif aContextAction == CONTEXT_PLAY_FROM_BEGINNIG :
			self.StartRecordPlayback( False )

		elif aContextAction == CONTEXT_DELETE :
			self.ShowDeleteConfirm()

		elif aContextAction == CONTEXT_DELETE_ALL :
			self.ShowDeleteAllConfirm()

		elif aContextAction == CONTEXT_LOCK :
			self.DoLockUnlock( True )

		elif aContextAction == CONTEXT_UNLOCK :
			self.DoLockUnlock( False )

		elif aContextAction == CONTEXT_RENAME :
			self.ShowRenameDialog( )

		elif aContextAction == CONTEXT_START_MARK :
			self.DoStartMark( )

		elif aContextAction == CONTEXT_CLEAR_MARK :
			self.DoClearMark( )
		else :
			LOG_ERR('Unknown Context Action')


	def ShowDeleteConfirm( self ) :
		markedList = self.GetMarkedList()
		selectedPos = self.GetSelectedPosition( )

		if markedList == None or len( markedList ) <= 0 :
			markedList = []
			if selectedPos >= 0 and selectedPos < len( self.mRecordList ) :
				markedList.append( selectedPos )

		if len( markedList ) > 0 :
			hasLocked = False

			# Check Locked Item
			for i in range( len( markedList ) ) :
				position = markedList[i]
				recInfo = self.mRecordList[ position ]
				if recInfo.mLocked == True :
					hasLocked = True
					break

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( 'Confirm', 'Do you want to delete record(s)?' )
			dialog.doModal( )

			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				if hasLocked == True :
					if self.CheckPincode() == False :
						return False

				self.DoDelete( markedList )


	def ShowDeleteAllConfirm( self ) :
		if self.mRecordList == None or len( self.mRecordList  ) <= 0 :
			return

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( 'Confirm', 'Do you want to delete all records?' )
		dialog.doModal( )

		if dialog.IsOK( ) == E_DIALOG_STATE_YES :

			hasLocked = False

			# Check Locked Item
			for recInfo in self.mRecordList :
				if recInfo.mLocked == True :
					hasLocked = True
					break
		
			if hasLocked == True :
				if self.CheckPincode() == False :
					return False

			self.OpenBusyDialog( )

			for recInfo in self.mRecordList :
				self.mDataCache.Record_DeleteRecord( recInfo.mRecordKey, self.mServiceType )


			self.CloseBusyDialog( )

			self.Flush( )
			self.Load( )
			self.UpdateList( )


	def ShowRenameDialog( self ) :
		selectedPos = self.GetSelectedPosition( )	
		try :
			kb = xbmc.Keyboard( '', 'Rename', False )
			kb.doModal( )
			if kb.isConfirmed( ) :
				newName = kb.getText( )
				LOG_TRACE('newName len=%d' %len( newName ) )
				if len( newName ) < MININUM_KEYWORD_SIZE :
					xbmcgui.Dialog( ).ok('Infomation', 'Input more than %d characters' %MININUM_KEYWORD_SIZE )
					return
				else :
					if self.mRecordList[ selectedPos ].mLocked == True :
						if self.CheckPincode() == False :
							return False

					LOG_TRACE('Key=%d ServiceType=%d Name=%s %s' %(self.mRecordList[ selectedPos ].mRecordKey,  self.mServiceType, self.mRecordList[ selectedPos ].mRecordName, newName ) )
					self.mDataCache.Record_Rename( self.mRecordList[ selectedPos ].mRecordKey, self.mServiceType, newName )
					self.mRecordListItems[selectedPos].setLabel2( newName )	
					self.mRecordList[ selectedPos ].mRecordName = newName
					xbmc.executebuiltin('container.update')

					

		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)


	def DoDelete( self, aDeleteList ) :

		if len( aDeleteList ) > 0 :
			self.OpenBusyDialog( )

			count = len( aDeleteList )
			for i in range( count ) :
				position = aDeleteList[i]
				LOG_TRACE('i=%d serviceType=%d key=%d' %(position, self.mServiceType, self.mRecordList[position].mRecordKey ) )
				self.mDataCache.Record_DeleteRecord( self.mRecordList[position].mRecordKey, self.mServiceType )

			self.CloseBusyDialog( )
			self.Flush( )
			self.Load( )
			self.UpdateList( )


	def DoLockUnlock( self, aLock=False ) :
		markedList = self.GetMarkedList()
		selectedPos = self.GetSelectedPosition( )

		if markedList == None or len( markedList ) <= 0 :
			markedList = []
			if selectedPos >= 0 and selectedPos < len( self.mRecordList ) :
				markedList.append( selectedPos )
				
		if len( markedList ) > 0 :
			if self.CheckPincode() == False :
				return False

			count = len( markedList )
			for i in range( count ) :
				position =  markedList[i]
				listItem = self.mRecordListItems[position]
				if aLock == True :
					self.mRecordList[ position ].mLocked = True
					self.mDataCache.Record_SetLock( self.mRecordList[position].mRecordKey, self.mServiceType, True )
					listItem.setProperty('Locked', 'True')
					listItem.setProperty('RecIcon', 'IconNotAvailable.png')
				else :
					self.mRecordList[ position ].mLocked = False
					self.mDataCache.Record_SetLock( self.mRecordList[position].mRecordKey, self.mServiceType, False )				
					listItem.setProperty('Locked', 'False')
					listItem.setProperty('RecIcon', 'RecIconSample.jpg')

			self.DoClearMark()
			xbmc.executebuiltin('container.update')


	def DoStartMark( self ) :
		self.mMarkMode = True


	def DoClearMark( self ) :
		self.mMarkMode = False

		if self.mRecordListItems == None :
			return
 
		for listItem in self.mRecordListItems:
			listItem.setProperty('Marked', 'False')


	def DoMarkToggle( self ) :
		if self.mRecordListItems == None :
			return
			
		selectedPos = self.GetSelectedPosition( )

		if selectedPos >= 0 and selectedPos < len( self.mRecordListItems ) :
			listItem = self.mRecordListItems[selectedPos]
			if listItem.getProperty('Marked') == 'True' :
				listItem.setProperty('Marked', 'False')
			else :
				listItem.setProperty('Marked', 'True')			


		selectedPos = selectedPos + 1	
		if selectedPos >= len( self.mRecordListItems ) :
			selectedPos = 0
			
		if selectedPos >= 0 and selectedPos < len( self.mRecordListItems ) :
			if self.mViewMode == E_VIEW_LIST :
				self.mCtrlCommonList.selectItem( selectedPos )		
			elif self.mViewMode == E_VIEW_THUMBNAIL :
				self.mCtrlThumbnailList.selectItem( selectedPos )		
			elif self.mViewMode == E_VIEW_POSTER_WRAP :
				self.mCtrlPosterwrapList.addselectItemItems( selectedPos )		
			elif self.mViewMode == E_VIEW_FANART :
				self.mCtrlFanartList.selectItem( selectedPos )		
			else :
				LOG_WARN('Unknown view mode')
			
		#xbmc.executebuiltin('container.update')


	def CheckPincode( self ) :
		savedPincode = ElisPropertyInt( 'PinCode', self.mCommander ).GetProp( )
		GuiLock2( True )
		pincodeDialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
		pincodeDialog.SetDialogProperty( 'Input Pincode', '', 4, True )
		pincodeDialog.doModal( )
		GuiLock2( False )
		
		if pincodeDialog.IsOK( ) == E_DIALOG_STATE_YES :
			inputPincode = int( pincodeDialog.GetString( ) )
			LOG_TRACE('Input pincode=%d savedPincode=%d' %( savedPincode, inputPincode) )
			if inputPincode == savedPincode :
				return True
			else :
				infoDialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				infoDialog.SetDialogProperty( 'ERROR', 'New PIN codes do not match' )
	 			infoDialog.doModal( )

		return False


	def Close( self ) :
		pass


	def UpdateSelectedPosition( self ) :
		selectedPos = self.GetSelectedPosition( )
		if selectedPos < 0 :
			self.mWin.setProperty( 'SelectedPosition', '0' )
		else :
			self.mWin.setProperty( 'SelectedPosition', '%d' %(selectedPos+1) )		
				

	def UpdateArchiveInfomation( self ) :
		selectedPos = self.GetSelectedPosition()
		
		if selectedPos >= 0 and selectedPos < len( self.mRecordList ) :
			recInfo = self.mRecordList[selectedPos]
			"""
			LOG_TRACE( 'Archive Info --> ChannelName=%s' %recInfo.mChannelName )
			LOG_TRACE( 'Archive Info --> RecDate=%s' %TimeToString( recInfo.mStartTime ) )
			LOG_TRACE( 'Archive Info --> RecDuration=%d' %( recInfo.mDuration/60 ) )
			LOG_TRACE( 'Archive Info --> RecName=%s' %recInfo.mRecordName )
			"""
			
			if recInfo :
				self.mWin.setProperty( 'ChannelName', recInfo.mChannelName )
				self.mWin.setProperty( 'RecDate',  TimeToString( recInfo.mStartTime ) )
				self.mWin.setProperty( 'RecDuration',  '%dm' %( recInfo.mDuration/60 ) )
				self.mWin.setProperty( 'RecName', recInfo.mRecordName )
			else :
				self.ResetArchiveInfomation( )
		else :
			self.ResetArchiveInfomation( )


	def ResetArchiveInfomation( self ) :
		self.mWin.setProperty( 'ChannelName', '' )
		self.mWin.setProperty( 'RecDate', '' )
		self.mWin.setProperty( 'RecDuration',  '' )
		self.mWin.setProperty( 'RecName', '' )				


	def RestoreLastRecordKey( self ):
		selectedPos = self.GetSelectedPosition( )

		if selectedPos >= 0 and selectedPos < len( self.mRecordList ) :
			recInfo = self.mRecordList[selectedPos]
			self.mSelectRecordKey = recInfo.mRecordKey
		else :
			self.mSelectRecordKey = -1


	def SelectLastRecordKey( self ) :
		selectedPos = 0
		for i in range( len( self.mRecordList ) ) :
			recInfo = self.mRecordList[i]
			if recInfo.mRecordKey == self.mSelectRecordKey  :
				break;
			selectedPos += 1

		LOG_TRACE('SelectPos=%d' %selectedPos )

		if self.mViewMode == E_VIEW_LIST :
			self.mCtrlCommonList.selectItem( selectedPos )
		elif self.mViewMode == E_VIEW_THUMBNAIL :
			self.mCtrlThumbnailList.selectItem( selectedPos )
		elif self.mViewMode == E_VIEW_POSTER_WRAP :
			self.mCtrlPosterwrapList.selectItem( selectedPos )
		elif self.mViewMode == E_VIEW_FANART :
			self.mCtrlFanartList.selectItem( selectedPos )
		else :
			LOG_WARN( 'Unknown View Mode' )

		self.UpdateSelectedPosition( )
		self.UpdateArchiveInfomation( )
	
