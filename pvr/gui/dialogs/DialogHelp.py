from pvr.gui.WindowImport import *
import pvr.Platform

try :
	import xml.etree.cElementTree as ElementTree
except Exception, e :
	from elementtree import ElementTree

MENU_PAGE					= 	0
FIRST_CONTENT_PAGE			=	1
LAST_PAGE_DEFAULT			=	22
LAST_PAGE_RUBY				=	22
LAST_PAGE_OSCAR				=	27

JET_PAGE					=	1
SET_PAGE					=	4
WATCH_PAGE					=	10
XBMC_PAGE					=	21

MAXIMUM_LABEL_NUM			=	12
MAXIMUM_TEXTBOX_NUM			=	2

GROUP_ID_CONTENT_PAGE		=	9000
GROUP_ID_CONTENT			= 	9010

LABEL_TITLE					=	1100
LABEL_CATEGORY				=	1101
LABEL_PAGENUM				= 	1102

IMAGE_ID_CONTENT			=	1200
LABEL_ID_STRING				= 	1210
TEXTBOX_BIGFONT_ID_STRING	= 	1230
TEXTBOX_SMALLFONT_ID_STRING	= 	1240
TEXTBOX_ID_STRING			= 	1250

BUTTON_ID_PREV				=	2000
BUTTON_ID_NEXT				=	2001

BUTTON_ID_JET				=	2002
BUTTON_ID_SET				=	2003
BUTTON_ID_GO				=	2004
BUTTON_ID_TIPS				=	2005


class DialogHelp( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		if pvr.Platform.GetPlatform( ).GetProduct( ) == PRODUCT_OSCAR :
			self.mFirstPage			=	MENU_PAGE
			self.mLastPage			=	LAST_PAGE_OSCAR
		elif pvr.Platform.GetPlatform( ).GetProduct( ) == PRODUCT_RUBY :
			self.mFirstPage			=	FIRST_CONTENT_PAGE
			self.mLastPage			=	LAST_PAGE_RUBY
		else :
			self.mFirstPage			=	FIRST_CONTENT_PAGE
			self.mLastPage			=	LAST_PAGE_DEFAULT
		self.mCurrentPageNum		= 	self.mFirstPage
		self.mPrevPageNum			= 	self.mFirstPage
		self.mHelpString			=  	None
		self.mRoot 					=	None
		self.mListContent			=	[]
		self.mImagePath				=	os.path.join( pvr.Platform.GetPlatform( ).GetScriptDir( ), 'resources', 'help/' )


	def onInit( self ) :
		self.SetFrontdisplayMessage( MR_LANG( 'Help' ) )
		language = XBMC_GetCurrentLanguage( )
		self.getControl( GROUP_ID_CONTENT_PAGE ).setVisible( False )

		if self.mInitialized == False :
			helpString = self.getProperty( 'HelpString' )
			if helpString :
				if pvr.Platform.GetPlatform( ).GetProduct( ) == PRODUCT_OSCAR :
					if pvr.Platform.GetPlatform( ).GetTunerType( ) == TUNER_TYPE_DVBS_DUAL :
						HelpStringPath = os.path.join( pvr.Platform.GetPlatform().GetScriptDir( ), 'resources', 'language', ('%s')%language, 'help_strings', 'oscar', 'DVB_S2_DUAL', helpString )
					elif pvr.Platform.GetPlatform( ).GetTunerType( ) == TUNER_TYPE_DVBS_SINGLE :
						HelpStringPath = os.path.join( pvr.Platform.GetPlatform().GetScriptDir( ), 'resources', 'language', ('%s')%language, 'help_strings', 'oscar', 'DVB_S2_SINGLE', helpString )
					elif pvr.Platform.GetPlatform( ).GetTunerType( ) == TUNER_TYPE_DVBTC :
						HelpStringPath = os.path.join( pvr.Platform.GetPlatform().GetScriptDir( ), 'resources', 'language', ('%s')%language, 'help_strings', 'oscar', 'DVB_TC', helpString )
					else :
						HelpStringPath = os.path.join( pvr.Platform.GetPlatform().GetScriptDir( ), 'resources', 'language', ('%s')%language, 'help_strings', 'oscar', 'DVB_S2_SINGLE', helpString )
					self.setFocusId( BUTTON_ID_JET )
					self.setProperty( 'HelpMenu', 'true' )

				elif pvr.Platform.GetPlatform( ).GetProduct( ) == PRODUCT_RUBY :
					HelpStringPath = os.path.join( pvr.Platform.GetPlatform().GetScriptDir( ), 'resources', 'language', ('%s')%language, 'help_strings', 'ruby', helpString )
					self.setProperty( 'HelpMenu', 'false' )

				else :
					HelpStringPath = os.path.join( pvr.Platform.GetPlatform().GetScriptDir( ), 'resources', 'language', ('%s')%language, 'help_strings', 'default', helpString )
					self.setProperty( 'HelpMenu', 'false' )

				if CheckDirectory( HelpStringPath ) :
					self.mHelpString = HelpStringPath
				else : # If no translated help_strings provided in the selected language
					self.mHelpString = os.path.join( pvr.Platform.GetPlatform().GetScriptDir( ), 'resources', 'language', 'English', 'help_strings', 'default', helpString )

			self.MakeContentList( )
			self.mInitialized = True
			LOG_TRACE( 'HELP STRING = %s' %self.mHelpString )

		if self.mInitialized == True and pvr.Platform.GetPlatform( ).GetProduct( ) == PRODUCT_RUBY :
			self.ShowHelpPage( self.mCurrentPageNum )
			self.getControl( GROUP_ID_CONTENT_PAGE ).setVisible( True )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_MOVE_RIGHT :
			if self.mCurrentPageNum == MENU_PAGE :
				return
			else :
				if self.mCurrentPageNum == self.mLastPage :
					self.Close( )
				else :
					self.ShowHelpPage( self.mCurrentPageNum +1 )
					self.setFocusId( BUTTON_ID_NEXT )

		if actionId == Action.ACTION_MOVE_LEFT :
			if self.mCurrentPageNum == MENU_PAGE :
				return
			else :
				if self.mPrevPageNum > 0 :
					self.ShowHelpPage( self.mPrevPageNum )
					self.setFocusId( BUTTON_ID_PREV )
				if self.mPrevPageNum == self.mFirstPage -1 :
					self.setFocusId ( BUTTON_ID_NEXT )
		
		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.Close( )


	def onClick( self, aControlId ) :
		if aControlId == BUTTON_ID_JET :
			self.ShowHelpPage( JET_PAGE )
			self.setProperty( 'HelpMenu', 'false' )
			self.getControl( GROUP_ID_CONTENT_PAGE ).setVisible( True )
			self.setFocusId( BUTTON_ID_NEXT )

		elif aControlId == BUTTON_ID_SET :
			self.ShowHelpPage( SET_PAGE )
			self.setProperty( 'HelpMenu', 'false' )
			self.getControl( GROUP_ID_CONTENT_PAGE ).setVisible( True )
			self.setFocusId( BUTTON_ID_NEXT )

		elif aControlId == BUTTON_ID_GO :
			self.ShowHelpPage( WATCH_PAGE )
			self.setProperty( 'HelpMenu', 'false' )
			self.getControl( GROUP_ID_CONTENT_PAGE ).setVisible( True )
			self.setFocusId( BUTTON_ID_NEXT )

		elif aControlId == BUTTON_ID_TIPS :
			self.ShowHelpPage( XBMC_PAGE )
			self.setProperty( 'HelpMenu', 'false' )
			self.getControl( GROUP_ID_CONTENT_PAGE ).setVisible( True )
			self.setFocusId( BUTTON_ID_NEXT )


	def onFocus( self, aControlId ) :
		pass


	def Close( self ) :
		self.mCurrentPageNum = FIRST_CONTENT_PAGE
		self.SetFrontdisplayMessage( MR_LANG( 'Main Menu' ) )
		self.CloseDialog( )


	def MakeContentList( self ) :
		tree = ElementTree.parse( self.mHelpString )
		self.mRoot = tree.getroot( )

		try :
			for page in self.mRoot.findall( 'page' ) :
				for content in page.findall( 'content' ) :
					self.mListContent.append( PageContent ( page.get( 'number' ), page.get( 'title' ), page.get( 'location' ), content.find( 'type' ).text, content.get( 'name' ), int( content.find( 'posx' ).text ), int( content.find( 'posy' ).text ), int( content.find( 'width' ).text ), int( content.find( 'height' ).text ) ) )

		except Exception, ex :
			LOG_ERR( "Exception %s" % ex )


	def ResetControls( self, aLabelNum, aTextboxNum ) :
		self.getControl( IMAGE_ID_CONTENT ).setVisible( False )
		self.getControl( TEXTBOX_BIGFONT_ID_STRING ).setVisible( False )

		for i in range( aLabelNum ) :
			self.getControl( LABEL_ID_STRING + i ).setVisible( False )

		for i in range( aTextboxNum ) :
			self.getControl( TEXTBOX_ID_STRING + i ).setVisible( False )
			self.getControl( TEXTBOX_SMALLFONT_ID_STRING + i ).setVisible( False )


	def ShowHelpPage( self, aStep ) :
		self.mCurrentPageNum = aStep
		self.mPrevPageNum = self.mCurrentPageNum -1
		self.getControl( GROUP_ID_CONTENT ).setVisible( False )
		self.DrawContents( self.mListContent, self.mCurrentPageNum )
		self.getControl( GROUP_ID_CONTENT ).setVisible( True )
		self.AddPrevNextButton( )


	def DrawContents( self, aList, aStep ) :
		labelCount = 0
		textboxCount = 0

		self.ResetControls( MAXIMUM_LABEL_NUM, MAXIMUM_TEXTBOX_NUM )

		for content in aList :
			if int( content.mPageNum ) == aStep :
				self.getControl( LABEL_TITLE ).setLabel( content.mTitle )
				self.getControl( LABEL_CATEGORY ).setLabel( content.mLocation )
				self.getControl( LABEL_PAGENUM ).setLabel( '( %s / %s )' % ( content.mPageNum, self.mLastPage ) )

				if content.mType == "image" :
					self.getControl( IMAGE_ID_CONTENT ).setPosition( content.mPositionX, content.mPositionY )
					self.getControl( IMAGE_ID_CONTENT ).setWidth( content.mWidth )
					self.getControl( IMAGE_ID_CONTENT ).setHeight( content.mHeight )
					self.setProperty('imagepath', self.mImagePath + content.mDescription )
					self.getControl( IMAGE_ID_CONTENT ).setVisible( True )

				elif content.mType == "label" :
					self.getControl( LABEL_ID_STRING + labelCount ).setPosition( content.mPositionX, content.mPositionY )
					self.getControl( LABEL_ID_STRING + labelCount ).setWidth( content.mWidth )
					self.getControl( LABEL_ID_STRING + labelCount ).setHeight( content.mHeight )
					self.setProperty( 'label_' + str( labelCount ), content.mDescription )
					self.getControl( LABEL_ID_STRING + labelCount ).setVisible( True )
					labelCount += 1

				elif content.mType == "textbox" :
					self.getControl( TEXTBOX_ID_STRING + textboxCount ).setPosition( content.mPositionX, content.mPositionY )
					self.getControl( TEXTBOX_ID_STRING + textboxCount ).setWidth( content.mWidth )
					self.getControl( TEXTBOX_ID_STRING + textboxCount ).setHeight( content.mHeight )
					self.setProperty( 'textbox_' + str( textboxCount ), content.mDescription )
					self.getControl( TEXTBOX_ID_STRING + textboxCount ).setVisible( True )
					textboxCount += 1

				elif content.mType == "textbox_smallfont" :
					self.getControl( TEXTBOX_SMALLFONT_ID_STRING + textboxCount ).setPosition( content.mPositionX, content.mPositionY )
					self.getControl( TEXTBOX_SMALLFONT_ID_STRING + textboxCount ).setWidth( content.mWidth )
					self.getControl( TEXTBOX_SMALLFONT_ID_STRING + textboxCount ).setHeight( content.mHeight )
					self.setProperty( 'textbox_smallfont_' + str( textboxCount ), content.mDescription )
					self.getControl( TEXTBOX_SMALLFONT_ID_STRING + textboxCount ).setVisible( True )
					textboxCount += 1

				elif content.mType == "textbox_bigfont" :
					self.getControl( TEXTBOX_BIGFONT_ID_STRING ).setPosition( content.mPositionX, content.mPositionY )
					self.getControl( TEXTBOX_BIGFONT_ID_STRING ).setWidth( content.mWidth )
					self.getControl( TEXTBOX_BIGFONT_ID_STRING ).setHeight( content.mHeight )
					self.setProperty( 'textbox_bigfont_0', content.mDescription )
					self.getControl( TEXTBOX_BIGFONT_ID_STRING ).setVisible( True )


	def AddPrevNextButton( self ) :
		if self.mCurrentPageNum == FIRST_CONTENT_PAGE :
			self.getControl( BUTTON_ID_PREV ).setVisible( False )
			self.getControl( BUTTON_ID_NEXT ).setVisible( True )
		else :
			self.getControl( BUTTON_ID_PREV ).setVisible( True )
			self.getControl( BUTTON_ID_NEXT ).setVisible( True )


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
