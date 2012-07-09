from pvr.gui.WindowImport import *
from pvr.HiddenTestMgr import *


FILE_NAME_TEST	=	'/home/root/elmo_test.xml'


class HiddenTest( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mRoot = None


	def onInit( self ) :
		print 'dhkim test #1'
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
		print 'dhkim test check test file'
		if os.path.exists( FILE_NAME_TEST ) == True :
			self.ShowContextMenu( )
		else :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( 'Error', 'No file : %s' % FILE_NAME_TEST )
			dialog.doModal( )
			WinMgr.GetInstance( ).CloseWindow( )


	def ShowContextMenu( self ) :
		print 'dhkim test show context'
		from elementtree import ElementTree
		tree = ElementTree.parse( FILE_NAME_TEST )
		self.mRoot = tree.getroot( )
		
		context = []
		menuCount = 0

		for scenario in self.mRoot.findall( 'scenario' ) :
			for name in scenario.findall( 'name' ) :
				context.append( ContextItem( name.text.encode( 'utf-8' ), menuCount ) )
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
			#scenario = []
			print 'dhkim test #1'
			scenario = TestScenario( 'scenario', 'scenario' )
			print 'dhkim test #2'
			item = self.mRoot.getchildren( )[ aContextAction ]
			for node in item :
				print 'root node  = %s' % node
				scenario.AddChild( self.MakeChild( node ) )
			pvr.HiddenTestMgr.StartTest( scenario )


	def MakeChild( self, aNode ) :
		if aNode.tag.lower( ) == 'loop' :
			print 'dhkim test make loop!'
			return self.MakeChildLoop( aNode )
		elif aNode.tag.lower( ) == 'sendkey' :
			print 'dhkim test make sendkey!'
			return SendKeySuite( aNode.tag, aNode.text )
		elif aNode.tag.lower( ) == 'sleep' :
			print 'dhkim test make sleep!'
			return SleepSuite( aNode.tag, aNode.text )
		elif aNode.tag.lower( ) == 'waitevent' :
			return WaitEventSuite( aNode.tag, aNode.text )


	def MakeChildLoop( self, aNode ) :
		print 'dhkim test Make loop!!!!!!!!!!!!!'
		count = 1
		if aNode.get( 'repeat' ) != None :
			count = aNode.get( 'repeat' )
		print 'dhkim test repeat = %s' % count
		loop = LoopSuite( 'loop', count )
		for node in aNode :
			loop.AddChild( self.MakeChild( node ) )
		return loop

