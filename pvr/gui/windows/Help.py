from pvr.gui.WindowImport import *
from elementtree import ElementTree
import pvr.TunerConfigMgr as ConfigMgr

E_STEP_FEATURES					=	1
E_STEP_FRONT_PLATE				=	2
E_STEP_REAR_PLATE				=	3
E_STEP_REMOTE1					=	4
E_STEP_REMOTE2					=	5
E_STEP_CONNECTING				=	6
E_STEP_INFO_PLATE				=	7
E_STEP_FIRST_INSTALLATION		=	8
E_STEP_SIMPLE_LNB				=	9
E_STEP_DISEQC_1					=	10
E_STEP_DISEQC_1_1				=	11
E_STEP_DISEQC_1_2				=	12
E_STEP_USALS					=	13
E_STEP_ONECABLE					=	14
E_STEP_AUTO_SCAN				=	15
E_STEP_MANUAL_SCAN				=	16
E_STEP_TIMESHIFT				=	17
E_STEP_RECORDING				=	18
E_STEP_ARCHIVE					=	19
E_STEP_PVR						=	20
E_STEP_BOOKMARK				=	21
E_STEP_EPG						=	22
E_STEP_VIEW_MODE				=	23
E_STEP_EPG_TIMER				=	24
E_STEP_MANUAL_TIMER			=	25
E_STEP_EDIT_TIMER				=	26
E_STEP_EDIT_CHANNEL_LIST		=	27
E_STEP_MOVING_CHANNELS			=	28
E_STEP_LOCKING_CHANNELS		=	29
E_STEP_SKIPPING_CHANNELS		=	30
E_STEP_CREATING_FAV				=	31
E_STEP_ADDING_CHANNELS			=	32
E_STEP_REMOVING_CHANNELS		=	33
E_STEP_RENAMING_FAV			=	34
E_STEP_DELETING_FAV				=	35

TOTAL_STEPS						=	35

E_SETTING_PAGENUM				= 	1004

E_HELP_IMAGE					=	100
E_HELP_TEXTBOX					= 	200

E_HELP_PREV						=	7000
E_HELP_NEXT						=	7001	
E_HELP_PREV_LABEL				=	7005
E_HELP_NEXT_LABEL				=	7006

E_HELP_CONTETNT				= 	8500

E_MAXIMUM_TEXTBOX_NUM			=	3


HELP_STRING = '/usr/share/xbmc/addons/script.mbox/resources/skins/Default/720p/Help_String.xml'


class Help( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mStepNum				= 	E_STEP_FEATURES
		self.mPrevStepNum				= 	E_STEP_FEATURES
		self.mRoot 					=	None
		self.mListContent 				=	[]
		if not self.mPlatform.IsPrismCube( ) :
			global HELP_STRING
			HELP_STRING = 'special://home/addons/script.mbox/resources/skins/Default/720p/Help_String.xml'

		self.MakeContentList( )


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		self.SetListControl( self.mStepNum )
		self.mInitialized = True	


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )

		self.GlobalAction( actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.Close( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_PARENT_DIR :
			self.Close( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )


	def onClick( self, aControlId ) :		
		if aControlId == E_HELP_NEXT :
			if self.mStepNum == E_STEP_DELETING_FAV :
				self.Close( )
			else :
				self.OpenAnimation( )
				self.SetListControl( self.mStepNum +1)
				self.setFocusId( aControlId )	

		if aControlId == E_HELP_PREV :
			self.OpenAnimation( )
			if self.mPrevStepNum == 1 :
				self.setFocusId ( E_HELP_NEXT )
			else :
				self.setFocusId( aControlId )
			
			self.SetListControl( self.mPrevStepNum )


	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return


	def Close( self ) :
		self.mInitialized = False
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
		
		return

	def MakeContentList ( self ) :
		tree = ElementTree.parse( HELP_STRING )
		self.mRoot = tree.getroot( )

		for page in self.mRoot.findall( 'page' ):
			for content in page.findall( 'content' ):
				self.mListContent.append( PageContent ( page.get( 'number' ), page.get( 'title' ), page.get( 'location' ), content.find( 'type' ).text, content.get( 'name' ), int( content.find( 'posx' ).text ), int( content.find( 'posy' ).text ), int( content.find( 'width' ).text ), int( content.find( 'height' ).text ) ) )


	def DrawContents ( self, aList, aStep) :
		contentcount = 0
		self.SetTextboxInvisible( E_MAXIMUM_TEXTBOX_NUM )
		
		for content in aList :
			if int( content.mPageNum ) == aStep :
				self.getControl( E_SETTING_HEADER_TITLE ).setLabel( content.mTitle )
				self.getControl( E_SETTING_DESCRIPTION ).setLabel( content.mLocation )
				self.getControl( E_SETTING_PAGENUM ).setLabel( '%s / %s' % ( content.mPageNum, TOTAL_STEPS ) )
				
				if content.mType == "image" :
					self.getControl( E_HELP_IMAGE ).setPosition( content.mPositionX , content.mPositionY )
					self.getControl( E_HELP_IMAGE ).setWidth( content.mWidth )
					self.getControl( E_HELP_IMAGE ).setHeight( content.mHeight )
					self.mWin.setProperty('imagepath', content.mDescription )
					
				elif content.mType == "textbox" :
					self.getControl( E_HELP_TEXTBOX + contentcount ).setPosition( content.mPositionX , content.mPositionY )
					self.getControl( E_HELP_TEXTBOX + contentcount ).setWidth( content.mWidth )
					self.getControl( E_HELP_TEXTBOX + contentcount ).setHeight( content.mHeight )
					
					if contentcount == 0:
						self.mWin.setProperty( 'label', content.mDescription )
					elif contentcount == 1:
						self.mWin.setProperty( 'label1', content.mDescription )
					elif contentcount == 2:
						self.mWin.setProperty( 'label2', content.mDescription )

					self.getControl( E_HELP_TEXTBOX + contentcount ).setVisible( True )
					contentcount += 1


	def SetPrevNextButtonLabel( self ) :
		if self.mStepNum == E_STEP_FEATURES :
			self.SetVisibleControl( E_HELP_PREV, False )
			self.getControl( E_HELP_NEXT_LABEL ).setLabel( MR_LANG( 'Next' ) )

		elif self.mStepNum == E_STEP_DELETING_FAV :
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

	
