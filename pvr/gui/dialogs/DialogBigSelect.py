from pvr.gui.WindowImport import *
import time

BIG_LIST							= 9001
DIALOG_BUTTON_OK_ID 				= 100
DIALOG_HEADER_LABEL_ID			= 101
DIALOG_BUTTON_CLOSE_ID 			= 109

E_MODE_TIMER_LIST					= 0

class DialogBigSelect( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )	
		self.mIsOk = False
		self.mCtrlList = None
		self.mListItems = None
		self.mDefaultList = []
		self.mMarkList = []		
		self.mTitle = ''
		self.mIsMulti = True
		self.mDefaultFocus = 0


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.setProperty( 'DialogDrawFinished', 'False' )			
		self.mMode = E_MODE_TIMER_LIST
		self.mMarkList = []
		self.mLastSelected = -1
		self.mCtrlList = self.getControl( BIG_LIST )
		self.Initialize( )
		self.setProperty( 'DialogDrawFinished', 'True' )		


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.mLastSelected = -1
			self.mMarkList = []
			self.Close( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT or actionId == Action.ACTION_MOVE_RIGHT :
			self.GetFocusId( )

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN or \
			 actionId == Action.ACTION_PAGE_UP or actionId == Action.ACTION_PAGE_DOWN :
			self.GetFocusId( )


	def onClick( self, aControlId ) :
		if aControlId == DIALOG_BUTTON_CLOSE_ID :
			self.mLastSelected = -1
			self.mMarkList = []
			self.Close( )

		elif aControlId == BIG_LIST:
			self.SetMark( )

		elif aControlId == DIALOG_BUTTON_OK_ID :
			self.mIsOK = True
			self.Close( )

	def onFocus( self, aControlId ) :
		pass


	def SetFocusList( self, aControlId ) :
		self.setFocusId( aControlId )


	def SetDefaultProperty( self, aTitle = 'SELECT', aList = None, aMode = 0, aIsMulti = True, aDefaultFocus = 0 ) :
		self.mTitle = aTitle
		self.mDefaultList = aList
		self.mMode = aMode
		self.mIsMulti = aIsMulti
		self.mDefaultFocus = aDefaultFocus


	def Initialize( self ) :
		self.mCtrlList.reset( )
		self.mListItems = []

		self.getControl( DIALOG_HEADER_LABEL_ID ).setLabel( self.mTitle )
		self.setProperty( 'SelectedPosition', '0' )		

		if not self.mDefaultList or len( self.mDefaultList ) < 1 :
			LOG_TRACE( 'timerlist none' )
			return
		if self.mMode == E_MODE_TIMER_LIST :
			self.TimerItems()


	def TimerItems( self ) :
		runningTimers = self.mDataCache.Timer_GetRunningTimers( )
		#if runningTimers == None :
		#	return False

		for timer in self.mDefaultList :
			channelNumber = timer.mChannelNo
			channelName = timer.mName
			channel = self.mDataCache.Channel_GetChannelByTimer( timer ) 
			if channel :
				if E_V1_2_APPLY_PRESENTATION_NUMBER :
					channelNumber = self.mDataCache.CheckPresentationNumber( channel )
				channelName = channel.mName

			isRunningTimer = False
			if runningTimers and len( runningTimers ) > 0 :
				for runningTimer in runningTimers :
					if timer.mTimerId == runningTimer.mTimerId :
						isRunningTimer = True
						break

			if isRunningTimer == True :
				item = xbmcgui.ListItem( '[COLOR=red]%04d %s[/COLOR]'%(channelNumber, channelName), '%s'%  timer.mName )
			elif timer.mTimerType == ElisEnum.E_ITIMER_VIEW:
				item = xbmcgui.ListItem( '[COLOR=green]%04d %s[/COLOR]'%(channelNumber, channelName), '%s'%  timer.mName )
			else :
				item = xbmcgui.ListItem( '%04d %s'%(channelNumber, channelName), '%s'%  timer.mName )

			item.setProperty( 'StartTime', TimeToString( timer.mStartTime, TimeFormatEnum.E_AW_DD_MM_YYYY )  )
			item.setProperty( 'Duration', '%s~%s' %( TimeToString( timer.mStartTime, TimeFormatEnum.E_HH_MM ), TimeToString( timer.mStartTime + timer.mDuration, TimeFormatEnum.E_HH_MM ) ) )
			self.mListItems.append( item )

		self.mCtrlList.addItems( self.mListItems )


	def SetMark( self ) :
		idx = 0
		isExist = False

		if self.mDefaultList == None or len( self.mDefaultList ) < 1 or \
		   self.mCtrlList == None or self.mListItems == None or len( self.mListItems ) < 1 :
			return

		aPos = self.mCtrlList.getSelectedPosition( )
		self.mLastSelected = aPos

		for i in self.mMarkList :
			if i == aPos :
				self.mMarkList.pop( idx )
				isExist = True
			idx += 1

		if isExist == False : 
			self.mMarkList.append( aPos )

		listItem = self.mCtrlList.getListItem( aPos )

		if listItem.getProperty( E_XML_PROPERTY_MARK ) == E_TAG_TRUE : 
			listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_FALSE )
		else :
			listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_TRUE )

		self.mCtrlList.selectItem( aPos + 1 )
		time.sleep( 0.05 )

		#aPos = self.mCtrlList.getSelectedPosition( )
		#self.setProperty( 'SelectedPosition',  '%s'% ( aPos + 1 )  )
		self.setProperty( 'SelectedPosition',  '%s'% len( self.mMarkList ) )


	def GetSelectedList( self ) :
		return self.mMarkList


	def IsOK( self ) :
		return self.mIsOk


	def Close( self ) :
		self.CloseDialog( )


