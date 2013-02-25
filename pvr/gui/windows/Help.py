from pvr.gui.WindowImport import *
from elementtree import ElementTree

E_STEP_FEATURES					=	1
HELP_STEPS 						=	40

E_SETTING_PAGENUM				= 	1004

E_HELP_IMAGE					=	100

E_HELP_TEXTBOX					= 	200
E_MAXIMUM_TEXTBOX_NUM			=	3

# Help Button & Label Ids
E_HELP_PREV						=	7000
E_HELP_NEXT						=	7001	
E_HELP_PREV_LABEL				=	7005
E_HELP_NEXT_LABEL				=	7006

E_HELP_CONTETNT				= 	8500

E_GROUP_LIST_CONTROL			=	9000

#HELP_STRING = '/usr/share/xbmc/addons/script.mbox/resources/skins/Default/720p/Help_String.xml'


class Help( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mStepNum				= 	E_STEP_FEATURES
		self.mPrevStepNum			= 	E_STEP_FEATURES
		self.mRoot 					=	None
		self.mListContent 			=	[]

		#if not self.mPlatform.IsPrismCube( ) :
		#	global HELP_STRING
		#	HELP_STRING = 'special://home/addons/script.mbox/resources/skins/Default/720p/Help_String.xml'

		#self.mHelpString				=  	HELP_STRING	
		self.mHelpString				=  	None	


	def onInit( self ) :
		self.SetActivate( True )
		self.SetFrontdisplayMessage( 'Help' )
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.getControl( E_GROUP_LIST_CONTROL ).setVisible( False )
		
		if self.mInitialized == False :
			helpString = self.getProperty( 'HelpString' )		
			if helpString :
				self.mHelpString =  os.path.join( WinMgr.GetInstance( ).GetSkinXMLPath(),  helpString )

			self.MakeContentList( )
			self.mInitialized = True
			LOG_TRACE( 'HELP STRING = %s' %self.mHelpString )

		self.SetListControl( self.mStepNum )
		self.getControl( E_GROUP_LIST_CONTROL ).setVisible( True )

		
	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.Close( )


	def onClick( self, aControlId ) :		
		if self.IsActivate( ) == False  :
			return
	
		if aControlId == E_HELP_NEXT :
			if self.mStepNum == HELP_STEPS :
				self.Close( )
			else :
				self.OpenAnimation( )
				self.SetListControl( self.mStepNum +1 )
				self.setFocusId( aControlId )	

		if aControlId == E_HELP_PREV :
			self.OpenAnimation( )
			if self.mPrevStepNum == 1 :
				self.setFocusId ( E_HELP_NEXT )
			else :
				self.setFocusId( aControlId )
			
			if self.mPrevStepNum > 0 :
				self.SetListControl( self.mPrevStepNum )


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
		if self.mInitialized == False :
			return


	def Close( self ) :
		self.mStepNum = E_STEP_FEATURES
		WinMgr.GetInstance( ).CloseWindow( )


	def OpenAnimation( self ) :
		self.setFocusId( E_FAKE_BUTTON )
		time.sleep( 0.3 )

							
	def SetTextboxInvisible( self, aTextboxNum ) :
		for i in range( aTextboxNum ) :
			self.getControl( E_HELP_TEXTBOX + i ).setVisible( False )


	def SetListControl( self, aStep ) :
		self.ResetAllControl( )
		self.mStepNum = aStep
		self.mPrevStepNum = self.mStepNum -1
		self.DrawContents( self.mListContent, self.mStepNum )
		self.getControl( E_HELP_CONTETNT ).setVisible( True )
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
		self.SetTextboxInvisible( E_MAXIMUM_TEXTBOX_NUM )
		
		for content in aList :
			if int( content.mPageNum ) == aStep :
				self.getControl( E_SETTING_HEADER_TITLE ).setLabel( content.mTitle )
				self.getControl( E_SETTING_DESCRIPTION ).setLabel( content.mLocation )
				self.getControl( E_SETTING_PAGENUM ).setLabel( '%s / %s' % ( content.mPageNum, HELP_STEPS ) )
				
				if content.mType == "image" :
					self.getControl( E_HELP_IMAGE ).setPosition( content.mPositionX , content.mPositionY )
					self.getControl( E_HELP_IMAGE ).setWidth( content.mWidth )
					self.getControl( E_HELP_IMAGE ).setHeight( content.mHeight )
					self.setProperty('imagepath', content.mDescription )
					
				elif content.mType == "textbox" :
					self.getControl( E_HELP_TEXTBOX + contentCount ).setPosition( content.mPositionX , content.mPositionY )
					self.getControl( E_HELP_TEXTBOX + contentCount ).setWidth( content.mWidth )
					self.getControl( E_HELP_TEXTBOX + contentCount ).setHeight( content.mHeight )
					
					if contentCount == 0:
						self.setProperty( 'label', content.mDescription )
					elif contentCount == 1:
						self.setProperty( 'label1', content.mDescription )
					elif contentCount == 2:
						self.setProperty( 'label2', content.mDescription )

					self.getControl( E_HELP_TEXTBOX + contentCount ).setVisible( True )
					contentCount += 1


	def SetPrevNextButtonLabel( self ) :
		if self.mStepNum == E_STEP_FEATURES :
			self.SetVisibleControl( E_HELP_PREV, False )
			self.getControl( E_HELP_NEXT_LABEL ).setLabel( MR_LANG( 'Next' ) )

		elif self.mStepNum == HELP_STEPS :
			self.getControl( E_HELP_PREV_LABEL ).setLabel( MR_LANG( 'Previous' ) )
			self.getControl( E_HELP_NEXT_LABEL ).setLabel( MR_LANG( 'Finish' ) )

		else :
			self.SetVisibleControl( E_HELP_PREV, True )
			self.getControl( E_HELP_PREV_LABEL ).setLabel( MR_LANG( 'Previous' ) )
			self.getControl( E_HELP_NEXT_LABEL ).setLabel( MR_LANG( 'Next' ) )

	
	def AddPrevNextButton( self ) :
		if self.mStepNum == E_STEP_FEATURES :
			self.getControl( E_HELP_PREV ).setVisible( False )
			self.getControl( E_HELP_NEXT ).setVisible( True )
			
		else :
			self.getControl( E_HELP_PREV ).setVisible( True )
			self.getControl( E_HELP_NEXT ).setVisible( True )
				

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

