import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.BaseWindow import BaseWindow, Action
from pvr.gui.GuiConfig import *
from ElisEnum import ElisEnum
from ElisEventBus import ElisEventBus
from ElisEventClass import *
from pvr.Util import RunThread, GuiLock, GuiLock2, LOG_TRACE, LOG_WARN, LOG_ERR, GetSetting, SetSetting, TimeToString
from pvr.PublicReference import GetSelectedLongitudeString, EpgInfoComponentImage, EnumToString, ClassToList, AgeLimit
import pvr.ElisMgr
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
import threading, time, os


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
CONTEXT_LOCK					= 3
CONTEXT_UNLOCK					= 4
CONTEXT_RENAME					= 5
CONTEXT_START_MARK				= 6
CONTEXT_CLEAR_MARK				= 7



MININUM_KEYWORD_SIZE			= 3


class ArchiveWindow( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )

	
	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( 'Archive' )

		LOG_TRACE('')
		self.mRecordCount = 0
		self.mSelectedIndex = 0
		self.mRecordList = [] 
		self.mSortList = [] 		
		self.mRecordListItems = []

		LOG_TRACE('')
		self.mServiceType =  self.mCurrentMode = self.mDataCache.Zappingmode_GetCurrent( ).mServiceType
		LOG_TRACE('serviceType=%d' %self.mServiceType)		
		
		LOG_TRACE('')
		self.mViewMode = int( GetSetting( 'VIEW_MODE' ) )
		self.mCtrlViewMode = self.getControl( BUTTON_ID_VIEW_MODE )

		LOG_TRACE('')
		self.mSortMode = int( GetSetting( 'SORT_MODE' ) )		
		self.mCtrlSortMode = self.getControl( BUTTON_ID_SORT_MODE )

		self.mAscending = []
		self.mAscending = [False,False,False,False,False]
		LOG_TRACE('self.mAscending=%s' %self.mAscending )		
		self.mAscending[E_SORT_DATE] = False
		self.mAscending[E_SORT_CHANNEL] = True
		self.mAscending[E_SORT_TITLE] = True
		self.mAscending[E_SORT_DURATION] = False

		LOG_TRACE('self.mAscending2=%s' %self.mAscending )				

		self.mCtrlCommonList = self.getControl( LIST_ID_COMMON_RECORD )
		self.mCtrlThumbnailList = self.getControl( LIST_ID_THUMBNAIL_RECORD )
		self.mCtrlPosterwrapList = self.getControl( LIST_ID_POSTERWRAP_RECORD )
		self.mCtrlFanartList = self.getControl( LIST_ID_FANART_RECORD )

		self.UpdateAscending()
		self.UpdateViewMode( )
		
		LOG_TRACE('')
		self.InitControl()
		LOG_TRACE('')

		self.Load( )
		LOG_TRACE('')
		self.UpdateList( )
		LOG_TRACE('')

		
		self.mInitialized = True


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )		

		#LOG_TRACE('onAction=%d' %actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			LOG_ERR('ERROR TEST')		
			self.SetVideoRestore( )
			LOG_ERR('ERROR TEST')			
			self.close( )
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_MAINMENU )

		elif actionId == Action.ACTION_SELECT_ITEM :
			LOG_ERR('ERROR TEST')
			focusId = self.GetFocusId()
			LOG_ERR('ERROR TEST focusId=%d' %focusId)			
			if focusId == LIST_ID_COMMON_RECORD or focusId == LIST_ID_THUMBNAIL_RECORD or focusId == LIST_ID_POSTERWRAP_RECORD or focusId == LIST_ID_FANART_RECORD:
				if	self.mMarkMode == True	:
					self.DoMarkToggle()
				else :
					self.StartRecordPlayback()
				#self.close()
			LOG_ERR('ERROR TEST')


		elif actionId == Action.ACTION_PARENT_DIR :
			LOG_ERR('ERROR TEST')
			self.SetVideoRestore( )
			self.close( )				
			WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_MAINMENU )
			LOG_ERR('ERROR TEST')			


		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT :
			pass

		elif actionId == Action.ACTION_MOVE_UP or id == Action.ACTION_MOVE_DOWN :
			pass

		elif actionId == Action.ACTION_CONTEXT_MENU:
			LOG_TRACE('')
			self.ShowContextMenu( )

		#testcode remove all archive
		elif actionId == Action.REMOTE_0 :
			LOG_TRACE('----------- Remove All Archive --------------')
			recordCount = self.mDataCache.Record_GetCount( self.mServiceType )
			
			self.OpenBusyDialog( )

			for i in range( recordCount ) :
				LOG_TRACE('i=%d' %i)		
				recInfo = self.mDataCache.Record_GetRecordInfo( 0, self.mServiceType )
				self.mDataCache.Record_DeleteRecord( recInfo.mRecordKey, self.mServiceType )


			self.CloseBusyDialog( )

			self.Flush( )
			self.Load( )
			self.UpdateList( )

			
		#testcode remove all timer
		elif actionId == Action.REMOTE_1 :
			LOG_TRACE('----------- Remove All Timer --------------')
			
		
	def onClick( self, aControlId ) :
		LOG_TRACE( 'aControlId=%d' % aControlId )

		if aControlId == BUTTON_ID_VIEW_MODE :
			self.mViewMode += 1
			if self.mViewMode >= E_VIEW_END :
				self.mViewMode = 0 

			SetSetting( 'VIEW_MODE','%d' %self.mViewMode )
			self.UpdateViewMode( )
			self.InitControl()			
			self.UpdateList( )
		
		elif aControlId == BUTTON_ID_SORT_MODE :
			self.mSortMode += 1
			if self.mSortMode >= E_SORT_END :
				self.mSortMode = 0 
				
			SetSetting( 'SORT_MODE','%d' %self.mSortMode ) 								
			self.UpdateSortMode( )
			self.InitControl()			
			self.UpdateAscending( )
			self.UpdateList( )

		elif aControlId == TOGGLEBUTTON_ID_ASC :
			LOG_TRACE('Mode=%d' % self.mSortMode )
			LOG_TRACE('mAscending=%d' %self.mAscending[self.mSortMode] )
			if self.mAscending[self.mSortMode] == True :
				self.mAscending[self.mSortMode] = False
			else :
				self.mAscending[self.mSortMode] = True

			self.UpdateAscending( )
			self.UpdateList( )

		elif aControlId == RADIIOBUTTON_ID_EXTRA :
			pass
		


	def onFocus(self, controlId):

		if self.mInitialized == False :
			return


	@GuiLock
	def onEvent(self, aEvent):
		pass


	def InitControl( self ) :

		if self.mViewMode == E_VIEW_LIST :
			self.mCtrlViewMode.setLabel('VIEW: LIST')
		elif self.mViewMode == E_VIEW_THUMBNAIL :			
			self.mCtrlViewMode.setLabel('VIEW: THUMBNAIL')		
		elif self.mViewMode == E_VIEW_POSTER_WRAP :			
			self.mCtrlViewMode.setLabel('VIEW: POSTER_WRAP')		
		elif self.mViewMode == E_VIEW_FANART :			
			self.mCtrlViewMode.setLabel('VIEW: FANART')		
		else :
			LOG_WARN('Unknown view mode')
			
		if self.mSortMode == E_SORT_DATE :
			self.mCtrlSortMode.setLabel('SORT: DATE')
		elif self.mSortMode == E_SORT_CHANNEL :			
			self.mCtrlSortMode.setLabel('SORT: CHANNEL')		
		elif self.mSortMode == E_SORT_TITLE :			
			self.mCtrlSortMode.setLabel('SORT: TITLE')		
		elif self.mSortMode == E_SORT_DURATION :			
			self.mCtrlSortMode.setLabel('SORT: DURATION')		
		else :
			LOG_WARN('Unknown sort mode')


	def UpdateViewMode( self ) :
		LOG_TRACE('---------------------')
		if self.mViewMode == E_VIEW_LIST :
			self.mWin.setProperty( 'ViewMode', 'common' )
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


		"""
		try :
			self.mRecordCount = self.mDataCache.Record_GetCount( self.mServiceType )
		except Exception, ex:
			LOG_ERR( "Exception %s" %ex)
		
		LOG_TRACE('')
		LOG_TRACE('RecordCount=%d' %self.mRecordCount )
		
		for i in range( self.mRecordCount ) :
			LOG_TRACE('i=%d' %i)		
			recInfo = self.mDataCache.Record_GetRecordInfo( i, self.mServiceType )
			recInfo.printdebug()
			self.mRecordList.append( recInfo )
		"""
		

	def UpdateList( self ) :
		LOG_TRACE('UpdateList Start')
		try :
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

			LOG_TRACE('')			
			if self.mAscending[self.mSortMode] == False :
				self.mRecordList.reverse()

			LOG_TRACE('')

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
		#(self ,  recordKey,  serviceType,  offsetms,  speed) :
		selectedPos = self.GetSelectedPosition()
		LOG_TRACE('selectedPos=%d' %selectedPos)
		
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

		self.close()
		WinMgr.GetInstance().GetWindow( WinMgr.WIN_ID_NULLWINDOW ).SetKeyDisabled( True, recInfo )

		self.SetVideoRestore();
		WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_TIMESHIFT_PLATE )				


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
			return markedList

		count = len( self.mRecordListItems )

		for i in range( count ) :
			listItem = self.mRecordListItems[i]
			if listItem.getProperty('Marked') == 'True' :
				markedList.append( i )

		return markedList


	def ShowContextMenu( self ) :
		LOG_TRACE('')
		try :
			selectedPos = self.GetSelectedPosition()
			context = []

			markedList = self.GetMarkedList()
			
			if markedList and len( markedList ) > 0 :
				context.append( ContextItem( 'Delete', CONTEXT_DELETE ) )
				context.append( ContextItem( 'Lock', CONTEXT_LOCK ) )
				context.append( ContextItem( 'Unlock', CONTEXT_UNLOCK ) )	
				context.append( ContextItem( 'Clear Marked Items', CONTEXT_CLEAR_MARK ) )	
				
			elif selectedPos >= 0 and selectedPos < len( self.mRecordList ) :
				recordInfo = self.mRecordList[ selectedPos ]		
				context.append( ContextItem( 'Play', CONTEXT_PLAY ) )
				context.append( ContextItem( 'Play from beginning', CONTEXT_PLAY_FROM_BEGINNIG ) )
				context.append( ContextItem( 'Delete', CONTEXT_DELETE ) )
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
			LOG_TRACE('')
			self.StartRecordPlayback( True )

		elif aContextAction == CONTEXT_PLAY_FROM_BEGINNIG :
			self.StartRecordPlayback( False )

		elif aContextAction == CONTEXT_DELETE :
			LOG_TRACE('')
			self.ShowDeleteConfirm()

		elif aContextAction == CONTEXT_LOCK :
			LOG_TRACE('')
			self.DoLockUnlock( True )

		elif aContextAction == CONTEXT_UNLOCK :
			LOG_TRACE('')
			self.DoLockUnlock( False )

		elif aContextAction == CONTEXT_RENAME :
			LOG_TRACE('')
			self.ShowRenameDialog( )

		elif aContextAction == CONTEXT_START_MARK :
			LOG_TRACE('')
			self.DoStartMark( )

		elif aContextAction == CONTEXT_CLEAR_MARK :
			LOG_TRACE('')		
			self.DoClearMark( )
		else :
			LOG_ERR('Unknown Context Action')


	def ShowDeleteConfirm( self ) :
		LOG_TRACE('ShowDeleteConfirm')

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
				LOG_TRACE('i=%d' %i)
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
		LOG_TRACE('')
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
		
