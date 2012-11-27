from pvr.gui.WindowImport import *
import time

E_MODE_DEFAULT_LIST = 0
E_MODE_CHANNEL_LIST = 1

E_CONTROL_ID_LIST = 3850

DIALOG_BUTTON_CLOSE_ID = 3800
DIALOG_HEADER_LABEL_ID = 3801
DIALOG_BUTTON_OK_ID = 3802
DIALOG_LABEL_POS_ID = 3803

class DialogMultiSelect( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )	
		self.mIsOk = None
		self.mCtrlList = None
		self.mListItems = None
		self.mDefaultList = []
		self.mTitle = ''
		self.mMode = E_MODE_DEFAULT_LIST
		

	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.WindowDialog( self.mWinId )

		self.mMarkList = []
		self.mCtrlList = self.getControl( E_CONTROL_ID_LIST )
		self.mCtrlPos =  self.getControl( DIALOG_LABEL_POS_ID )

		self.InitList( )
		self.mEventBus.Register( self )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.mIsOk = actionId
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.mMarkList = None
			self.Close( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN or \
			 actionId == Action.ACTION_PAGE_UP or actionId == Action.ACTION_PAGE_DOWN :
			idx = self.mCtrlList.getSelectedPosition( )
			self.mCtrlPos.setLabel( '%s'% ( idx + 1 ) )

		elif actionId == Action.ACTION_STOP :
			self.Close( )

		elif actionId == Action.ACTION_PLAYER_PLAY or actionId == Action.ACTION_PAUSE :
			self.Close( )


	def onClick( self, aControlId ) :
		if aControlId == DIALOG_BUTTON_CLOSE_ID :
			self.mMarkList = None
			self.Close( )

		elif aControlId == E_CONTROL_ID_LIST :
			self.SetMarkupGUI( )

		elif aControlId == DIALOG_BUTTON_OK_ID :
			self.Close( )		


	def onFocus( self, aControlId ) :
		pass



	@GuiLock
	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowDialogId( ) :
			if aEvent.getName( ) == ElisEventRecordingStarted.getName( ) or \
			   aEvent.getName( ) == ElisEventRecordingStopped.getName( ) or \
			   aEvent.getName( ) == ElisEventPlaybackEOF.getName( ) :
				xbmc.executebuiltin('xbmc.Action(stop)')


	def InitList( self ) :
		if self.mDefaultList == None or len( self.mDefaultList ) < 1 :
			return

		self.mCtrlList.reset( )
		self.mListItems = []

		if self.mMode == E_MODE_CHANNEL_LIST :
			self.ChannelItems( )
		else :
			self.ListItems( )

		self.getControl( DIALOG_HEADER_LABEL_ID ).setLabel( self.mTitle )
		self.mCtrlList.addItems( self.mListItems )

		idx = self.mCtrlList.getSelectedPosition( )
		self.mCtrlPos.setLabel( '%s'% ( idx + 1 ) )


	def ListItems( self ) :
		for item in self.mDefaultList :
			listItem = xbmcgui.ListItem( '%s'% item )
			self.mListItems.append( listItem )


	def ChannelItems( self ) :

		for iChannel in self.mDefaultList :
			listItem = xbmcgui.ListItem( '%04d %s'%( iChannel.mNumber, iChannel.mName ) )

			if iChannel.mLocked : 
				listItem.setProperty( E_XML_PROPERTY_LOCK, E_TAG_TRUE )
			if iChannel.mIsCA : 
				listItem.setProperty( E_XML_PROPERTY_CAS,  E_TAG_TRUE )
			if iChannel.mSkipped : 
				listItem.setProperty( E_XML_PROPERTY_SKIP, E_TAG_TRUE )

			self.mListItems.append( listItem )


	def SetMarkupGUI( self ) :
		idx = 0
		isExist = False

		if self.mDefaultList == None or len( self.mDefaultList ) < 1 or \
		   self.mCtrlList == None or self.mListItems == None or len( self.mListItems ) < 1 :
			return

		aPos = self.mCtrlList.getSelectedPosition( )

		#aready mark is mark delete
		for i in self.mMarkList :
			if i == aPos :
				self.mMarkList.pop( idx )
				isExist = True
			idx += 1

		#do not exist is append mark
		if isExist == False : 
			self.mMarkList.append( aPos )

		listItem = self.mCtrlList.getListItem( aPos )

		#mark toggle: disable/enable
		if listItem.getProperty( E_XML_PROPERTY_MARK ) == E_TAG_TRUE : 
			listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_FALSE )
		else :
			listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_TRUE )

		self.mCtrlList.selectItem( aPos + 1 )
		time.sleep( 0.05 )

		aPos = self.mCtrlList.getSelectedPosition( )
		self.mCtrlPos.setLabel( '%s'% ( aPos + 1 ) )


	def SetDefaultProperty( self, aTitle = 'SELECT', aList = None, aMode = E_MODE_DEFAULT_LIST ) :
		self.mTitle = aTitle
		self.mDefaultList = aList
		self.mMode = aMode


	def GetSelectedList( self ) :
		return self.mMarkList


	def GetCloseStatus( self ) :
		return self.mIsOk


	def Close( self ) :
		self.mEventBus.Deregister( self )
		self.CloseDialog( )
		
