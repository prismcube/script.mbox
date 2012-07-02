from pvr.gui.WindowImport import *
import pvr.HiddenTestMgr as TestMgr


FILE_NAME_TEST	=	'/home/root/elmo_test.xml'


class HiddenTest( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mSoup = None


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		self.CheckTestFile( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if actionId == Action.ACTION_PREVIOUS_MENU :
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_PARENT_DIR :
			WinMgr.GetInstance( ).CloseWindow( )


	def onClick( self, aControlId ) :
		pass
		
 
	def onFocus( self, aControlId ) :
		pass


	def CheckTestFile( self ) :
		if os.path.exists( FILE_NAME_TEST ) == True :
			self.ShowContextMenu( )
		else :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( 'Error', 'No file : %s' % FILE_NAME_TEST )
			dialog.doModal( )
			WinMgr.GetInstance( ).CloseWindow( )


	def ShowContextMenu( self ) :
		from BeautifulSoup import BeautifulSoup
		fp = open( FILE_NAME_TEST )
		xml = fp.read( )
		fp.close( )
		self.mSoup = BeautifulSoup( xml )

		context = []
		menuCount = 0

		for node in self.mSoup.findAll( 'name' ) :
			context.append( ContextItem( node.string.encode( 'utf-8' ), menuCount ) )
			menuCount = menuCount + 1

		if menuCount == 0 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( 'Error', 'No test scenario in file : %s' % FILE_NAME_TEST )
			dialog.doModal( )
			WinMgr.GetInstance( ).CloseWindow( )
		else :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context )
			dialog.doModal( )
			contextAction = dialog.GetSelectedAction( )
			self.DoContextAction( contextAction )


	def DoContextAction( self, aContextAction ) : 
		if aContextAction == -1 :
			WinMgr.GetInstance( ).CloseWindow( )
		else :
			scenario = []
			soup = self.mSoup.findAll( 'scenario' )[ aContextAction ]
			node = soup.findNext( ).findNext( )
			while node != None :
				scenario.append( self.MakeAction( node ) )
				node = node.findNextSibling( )
			LOG_TRACE( scenario )
			TestMgr.GetInstance( ).StartTest( scenario )


	def MakeAction( self, aNode ) :
		if aNode.name.lower( ) == 'loop' :
			return self.MakeActionLoop( aNode )
		else :
			return ( aNode.name, aNode.string )


	def MakeActionLoop( self, aNode ) :
		loop 		= []
		count		= 1
		if aNode.get( 'repeat' ) != None :
			count = aNode.get( 'repeat' )
		loop.append( ( 'loop', count ) )
		if aNode.find( ) != None :
			firstchild	= aNode.find( )
			childaction	= firstchild.name
			childvalue	= firstchild.string
			loop.append( ( childaction, childvalue ) )
			while firstchild.findNextSibling( ) != None :
				firstchild = firstchild.findNextSibling( )
				childaction	= firstchild.name
				childvalue	= firstchild.string
				loop.append( ( childaction, childvalue ) )
		return loop
