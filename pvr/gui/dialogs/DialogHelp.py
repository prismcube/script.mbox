from pvr.gui.WindowImport import *
from elementtree import ElementTree

E_SETTING_HEADER_TITLE			=	1002
E_SETTING_DESCRIPTION			=	1003

FIRST_PAGE						=	1
LAST_PAGE 						=	40
MAXIMUM_TEXTBOX_NUM			=	3

E_CONTROL_ID_LABEL_PAGENUM		= 	1004
E_CONTROL_ID_IMAGE				=	100
E_CONTROL_ID_TEXTBOX			= 	200
E_CONTROL_ID_BUTTON_PREV		=	7000
E_CONTROL_ID_BUTTON_NEXT		=	7001
E_CONTROL_ID_LABEL_PREV			=	7005
E_CONTROL_ID_LABEL_NEXT			=	7006
E_CONTROL_ID_GROUP_CONTENT		= 	8500
E_CONTROL_ID_GROUP_PAGE		=	9000


#HELP_STRING = '/usr/share/xbmc/addons/script.mbox/resources/skins/Default/720p/Help_String.xml'


class DialogHelp( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		self.mFirstPage				=	FIRST_PAGE
		self.mLastPage				=	LAST_PAGE
		self.mStepNum				= 	self.mFirstPage
		self.mPrevStepNum			= 	self.mFirstPage
		self.mRoot 				=	None
		self.mListContent			=	[]

		#if not self.mPlatform.IsPrismCube( ) :
		#	global HELP_STRING
		#	HELP_STRING = 'special://home/addons/script.mbox/resources/skins/Default/720p/Help_String.xml'

		#self.mHelpString			=  	HELP_STRING
		self.mHelpString			=  	None


	def onInit( self ) :
		self.SetFrontdisplayMessage( 'Help' )
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.getControl( E_CONTROL_ID_GROUP_PAGE ).setVisible( False )

		if self.mInitialized == False :
			helpString = self.getProperty( 'HelpString' )
			if helpString :
				self.mHelpString =  os.path.join( WinMgr.GetInstance( ).GetSkinXMLPath(), helpString )

			self.MakeContentList( )
			self.mInitialized = True
			LOG_TRACE( 'HELP STRING = %s' %self.mHelpString )

		self.SetListControl( self.mStepNum )
		self.getControl( E_CONTROL_ID_GROUP_PAGE ).setVisible( True )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.Close( )


	def onClick( self, aControlId ) :
		if aControlId == E_CONTROL_ID_BUTTON_NEXT :
			if self.mStepNum == self.mLastPage :
				self.Close( )
			else :
				self.OpenAnimation( )
				self.SetListControl( self.mStepNum +1 )
				self.setFocusId( aControlId )

		if aControlId == E_CONTROL_ID_BUTTON_PREV :
			self.OpenAnimation( )
			if self.mPrevStepNum == self.mFirstPage :
				self.setFocusId ( E_CONTROL_ID_BUTTON_NEXT )
			else :
				self.setFocusId( aControlId )

			if self.mPrevStepNum > 0 :
				self.SetListControl( self.mPrevStepNum )


	def onFocus( self, aControlId ) :
		pass

	def Close( self ) :
		self.mStepNum = FIRST_PAGE
		self.SetFrontdisplayMessage( 'Main Menu' )
		self.CloseDialog( )


	def OpenAnimation( self ) :
		self.setFocusId( E_FAKE_BUTTON )
		time.sleep( 0.3 )


	def SetTextboxInvisible( self, aTextboxNum ) :
		for i in range( aTextboxNum ) :
			self.getControl( E_CONTROL_ID_TEXTBOX + i ).setVisible( False )


	def SetListControl( self, aStep ) :
		self.ResetAllControl( )
		self.mStepNum = aStep
		self.mPrevStepNum = self.mStepNum -1
		self.DrawContents( self.mListContent, self.mStepNum )
		self.getControl( E_CONTROL_ID_GROUP_CONTENT ).setVisible( True )
		self.AddPrevNextButton( )
		self.SetPrevNextButtonLabel( )


	def MakeContentList ( self ) :
		tree = ElementTree.parse( self.mHelpString )
		self.mRoot = tree.getroot( )

		for page in self.mRoot.findall( 'page' ) :
			for content in page.findall( 'content' ) :
				self.mListContent.append( PageContent ( page.get( 'number' ), page.get( 'title' ), page.get( 'location' ), content.find( 'type' ).text, content.get( 'name' ), int( content.find( 'posx' ).text ), int( content.find( 'posy' ).text ), int( content.find( 'width' ).text ), int( content.find( 'height' ).text ) ) )


	def DrawContents ( self, aList, aStep ) :
		contentCount = 0
		self.SetTextboxInvisible( MAXIMUM_TEXTBOX_NUM )

		for content in aList :
			if int( content.mPageNum ) == aStep :
				self.getControl( E_SETTING_HEADER_TITLE ).setLabel( content.mTitle )
				self.getControl( E_SETTING_DESCRIPTION ).setLabel( content.mLocation )
				self.getControl( E_CONTROL_ID_LABEL_PAGENUM ).setLabel( '%s / %s' % ( content.mPageNum, self.mLastPage ) )

				if content.mType == "image" :
					self.getControl( E_CONTROL_ID_IMAGE ).setPosition( content.mPositionX , content.mPositionY )
					self.getControl( E_CONTROL_ID_IMAGE ).setWidth( content.mWidth )
					self.getControl( E_CONTROL_ID_IMAGE ).setHeight( content.mHeight )
					self.setProperty('imagepath', content.mDescription )

				elif content.mType == "textbox" :
					self.getControl( E_CONTROL_ID_TEXTBOX + contentCount ).setPosition( content.mPositionX , content.mPositionY )
					self.getControl( E_CONTROL_ID_TEXTBOX + contentCount ).setWidth( content.mWidth )
					self.getControl( E_CONTROL_ID_TEXTBOX + contentCount ).setHeight( content.mHeight )

					if contentCount == 0:
						self.setProperty( 'label', content.mDescription )
					elif contentCount == 1:
						self.setProperty( 'label1', content.mDescription )
					elif contentCount == 2:
						self.setProperty( 'label2', content.mDescription )

					self.getControl( E_CONTROL_ID_TEXTBOX + contentCount ).setVisible( True )
					contentCount += 1


	def SetPrevNextButtonLabel( self ) :
		if self.mStepNum == self.mFirstPage :
			self.SetVisibleControl( E_CONTROL_ID_BUTTON_PREV, False )
			self.getControl( E_CONTROL_ID_LABEL_NEXT ).setLabel( MR_LANG( 'Next' ) )

		elif self.mStepNum == self.mLastPage :
			self.getControl( E_CONTROL_ID_LABEL_PREV ).setLabel( MR_LANG( 'Previous' ) )
			self.getControl( E_CONTROL_ID_LABEL_NEXT ).setLabel( MR_LANG( 'Finish' ) )

		else :
			self.SetVisibleControl( E_CONTROL_ID_BUTTON_PREV, True )
			self.getControl( E_CONTROL_ID_LABEL_PREV ).setLabel( MR_LANG( 'Previous' ) )
			self.getControl( E_CONTROL_ID_LABEL_NEXT ).setLabel( MR_LANG( 'Next' ) )


	def AddPrevNextButton( self ) :
		if self.mStepNum == self.mFirstPage :
			self.getControl( E_CONTROL_ID_BUTTON_PREV ).setVisible( False )
			self.getControl( E_CONTROL_ID_BUTTON_NEXT ).setVisible( True )

		else :
			self.getControl( E_CONTROL_ID_BUTTON_PREV ).setVisible( True )
			self.getControl( E_CONTROL_ID_BUTTON_NEXT ).setVisible( True )


class PageContent :
	def __init__( self, aPageNum, aTitle, aLocation, aType, aDescription, aPositionX, aPositionY, aWidth, aHeight ) :
		self.mPageNum = aPageNum
		self.mTitle = aTitle
		self.mLocation = aLocation
		self.mType = aType
		self.mDescription = aDescription
		self.mPositionX = aPositionX
		self.mPositionY = aPositionY
		self.mWidth = aWidth
		self.mHeight = aHeight

