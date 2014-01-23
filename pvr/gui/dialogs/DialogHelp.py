from pvr.gui.WindowImport import *

try :
	import xml.etree.cElementTree as ElementTree
except Exception, e :
	from elementtree import ElementTree


E_SETTING_HEADER_TITLE			=	1002
E_SETTING_DESCRIPTION			=	1003

FIRST_PAGE						=	1
LAST_PAGE 						=	22
MAXIMUM_TEXTBOX_NUM			=	2

E_CONTROL_ID_LABEL_PAGENUM		= 	1004
E_CONTROL_ID_IMAGE				=	100
E_CONTROL_ID_TEXTBOX			= 	200
E_CONTROL_ID_BUTTON_PREV		=	7000
E_CONTROL_ID_BUTTON_NEXT		=	7001
E_CONTROL_ID_GROUP_CONTENT		= 	8500
E_CONTROL_ID_GROUP_PAGE		=	9000


class DialogHelp( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		self.mFirstPage				=	FIRST_PAGE
		self.mLastPage				=	LAST_PAGE
		self.mStepNum				= 	self.mFirstPage
		self.mPrevStepNum			= 	self.mFirstPage
		self.mRoot 				=	None
		self.mListContent			=	[]
		self.mHelpString			=  	None


	def onInit( self ) :
		self.SetFrontdisplayMessage( MR_LANG('Help') )
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.getControl( E_CONTROL_ID_GROUP_PAGE ).setVisible( False )
		language = XBMC_GetCurrentLanguage( )

		if self.mInitialized == False :
			helpString = self.getProperty( 'HelpString' )
			if helpString :
				HelpStringPath = os.path.join( pvr.Platform.GetPlatform().GetScriptDir( ), 'resources', 'language', ('%s')%language, helpString )
				if CheckDirectory( HelpStringPath ) :
					self.mHelpString = HelpStringPath
				else :
					self.mHelpString = os.path.join( pvr.Platform.GetPlatform().GetScriptDir( ), 'resources', 'language', 'English', helpString )

			self.MakeContentList( )
			self.mInitialized = True
			LOG_TRACE( 'HELP STRING = %s' %self.mHelpString )

		self.SetListControl( self.mStepNum )
		self.getControl( E_CONTROL_ID_GROUP_PAGE ).setVisible( True )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_MOVE_RIGHT :
			if self.mStepNum == self.mLastPage :
				self.Close( )
			else :
				self.SetListControl( self.mStepNum +1 )
				self.setFocusId( E_CONTROL_ID_BUTTON_NEXT )

		if actionId == Action.ACTION_MOVE_LEFT :		
			if self.mPrevStepNum > 0 :
				self.SetListControl( self.mPrevStepNum )
				self.setFocusId( E_CONTROL_ID_BUTTON_PREV )
			if self.mPrevStepNum == self.mFirstPage -1 :
				self.setFocusId ( E_CONTROL_ID_BUTTON_NEXT )
		
		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.Close( )


	def onClick( self, aControlId ) :
		pass


	def onFocus( self, aControlId ) :
		pass


	def Close( self ) :
		self.mStepNum = FIRST_PAGE
		self.SetFrontdisplayMessage( MR_LANG('Main Menu') )
		self.CloseDialog( )


	def SetTextboxInvisible( self, aTextboxNum ) :
		for i in range( aTextboxNum ) :
			self.getControl( E_CONTROL_ID_TEXTBOX + i ).setVisible( False )


	def SetListControl( self, aStep ) :
		self.mStepNum = aStep
		self.mPrevStepNum = self.mStepNum -1
		self.getControl( E_CONTROL_ID_GROUP_CONTENT ).setVisible( False )
		self.ShowContents( self.mListContent, self.mStepNum )
		self.getControl( E_CONTROL_ID_GROUP_CONTENT ).setVisible( True )
		self.AddPrevNextButton( )


	def MakeContentList ( self ) :
		tree = ElementTree.parse( self.mHelpString )
		self.mRoot = tree.getroot( )

		for page in self.mRoot.findall( 'page' ) :
			for content in page.findall( 'content' ) :
				self.mListContent.append( PageContent ( page.get( 'number' ), page.get( 'title' ), page.get( 'location' ), content.find( 'type' ).text, content.get( 'name' ), int( content.find( 'posx' ).text ), int( content.find( 'posy' ).text ), int( content.find( 'width' ).text ), int( content.find( 'height' ).text ) ) )


	def ShowContents ( self, aList, aStep ) :
		contentCount = 0
		self.SetTextboxInvisible( MAXIMUM_TEXTBOX_NUM )

		for content in aList :
			if int( content.mPageNum ) == aStep :
				self.getControl( E_SETTING_HEADER_TITLE ).setLabel( content.mTitle )
				self.getControl( E_SETTING_DESCRIPTION ).setLabel( content.mLocation )
				self.getControl( E_CONTROL_ID_LABEL_PAGENUM ).setLabel( '( %s / %s )' % ( content.mPageNum, self.mLastPage ) )

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
						self.setProperty( 'label1', content.mDescription )
					elif contentCount == 1:
						self.setProperty( 'label2', content.mDescription )

					self.getControl( E_CONTROL_ID_TEXTBOX + contentCount ).setVisible( True )
					contentCount += 1


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
