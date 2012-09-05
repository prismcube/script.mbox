from pvr.gui.WindowImport import *

E_CONTROL_ID_LIST = 3850

DIALOG_BUTTON_CLOSE_ID = 100
DIALOG_HEADER_LABEL_ID = 101
DIALOG_BUTTON_OK_ID = 102

class DialogMultiSelect( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )	
		self.mIsOk = None
		self.mCtrlList = None
		self.mListItems = None
		self.DefaultList = []
		self.mTitle = ''
		self.mMethod = None
		

	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.WindowDialog( self.mWinId )

		self.mMarkList = []
		self.mCtrlList = self.getControl( E_CONTROL_ID_LIST )

		self.InitList( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.mIsOk = actionId
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.mMarkList = None
			self.Close( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
			
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mMarkList = None
			self.Close( )
			

	def onClick( self, aControlId ) :
		if aControlId == DIALOG_BUTTON_CLOSE_ID :
			self.mMarkList = None
			self.Close( )

		elif aControlId == E_CONTROL_ID_LIST :
			idx = self.mCtrlList.getSelectedPosition( )
			self.SetMarkupGUI( idx )
			self.mCtrlList.selectItem( idx + 1 )

		elif aControlId == DIALOG_BUTTON_OK_ID :
			self.Close( )		


	def onFocus( self, aControlId ) :
		pass


	@GuiLock
	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowDialogId( ) :
			pass


	def InitList( self ) :
		if self.DefaultList == None or len( self.DefaultList ) < 1 :
			return

		self.mCtrlList.reset( )
		self.mListItems = []

		if self.mMethod :
			self.mMethod( )
		else :
			self.mEventBus.Register( self )
			self.ChannelItems( )

		self.getControl( DIALOG_HEADER_LABEL_ID ).setLabel( self.mTitle )
		self.mCtrlList.addItems( self.mListItems )


	def ChannelItems( self ) :

		for iChannel in self.DefaultList :
			listItem = xbmcgui.ListItem( '%04d %s'%( iChannel.mNumber, iChannel.mName ) )

			if iChannel.mLocked : 
				listItem.setProperty( E_XML_PROPERTY_LOCK, E_TAG_TRUE )
			if iChannel.mIsCA : 
				listItem.setProperty( E_XML_PROPERTY_CAS,  E_TAG_TRUE )
			if iChannel.mSkipped : 
				listItem.setProperty( E_XML_PROPERTY_SKIP, E_TAG_TRUE )

			self.mListItems.append( listItem )


	def SetMarkupGUI( self, aPos ) :
		idx = 0
		isExist = False

		#aready mark is mark delete
		for i in self.mMarkList :
			if i == aPos :
				self.mMarkList.pop(idx)
				isExist = True
			idx += 1

		#do not exist is append mark
		if isExist == False : 
			self.mMarkList.append( aPos )

		listItem = self.mCtrlList.getListItem(aPos)

		#mark toggle: disable/enable
		if listItem.getProperty( E_XML_PROPERTY_MARK ) == E_TAG_TRUE : 
			listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_FALSE )
		else :
			listItem.setProperty( E_XML_PROPERTY_MARK, E_TAG_TRUE )


	def SetDefaultProperty( self, aTitle = 'SELECT', aList = None ) :
		self.mTitle = aTitle
		self.DefaultList = aList


	def GetSelectedList( self ) :
		return self.mMarkList


	def GetCloseStatus( self ) :
		return self.mIsOk


	def Close( self ) :
		if self.mMethod == None :
			self.mEventBus.Deregister( self )
		self.CloseDialog( )
		
