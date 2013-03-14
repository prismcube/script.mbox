from pvr.gui.WindowImport import *
from pvr.HiddenTestMgr import *
import xbmc, xbmcaddon


FILE_NAME_TEST = xbmcaddon.Addon( 'script.mbox' ).getAddonInfo( 'path' ) + '/elmo_test.xml'


class HiddenTest( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mRoot = None


	def onInit( self ) :
		self.SetActivate( True )
		self.SetFrontdisplayMessage( 'Hidden Test' )
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.CheckTestFile( )


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		actionId = aAction.getId( )
		if actionId == Action.ACTION_PREVIOUS_MENU :
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_PARENT_DIR :
			WinMgr.GetInstance( ).CloseWindow( )


	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return


	def CheckTestFile( self ) :
		if os.path.exists( FILE_NAME_TEST ) == True :
			self.ShowContextMenu( )
		else :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'File not found : %s' ) % FILE_NAME_TEST )			
			dialog.doModal( )
			WinMgr.GetInstance( ).CloseWindow( )


	def ShowContextMenu( self ) :
		from elementtree import ElementTree
		tree = ElementTree.parse( FILE_NAME_TEST )
		self.mRoot = tree.getroot( )
		
		context = []
		context.append( ContextItem( 'PROPRTY CHECK', 9999 ) )
		context.append( ContextItem( 'ALL Navigation', 8888 ) )
		menuCount = 0

		for scenario in self.mRoot.findall( 'scenario' ) :
			for name in scenario.findall( 'name' ) :
				context.append( ContextItem( name.text.encode( 'utf-8' ), menuCount ) )
			menuCount = menuCount + 1

		if menuCount == 0 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Test scenario not available : %s' ) % FILE_NAME_TEST )			
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
		elif aContextAction == 9999 :
			self.CheckProperty( )
			WinMgr.GetInstance( ).CloseWindow( )
		elif aContextAction == 8888 :
			#WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE, WinMgr.WIN_ID_NULLWINDOW )
			if ConnectSocket( ) :
				self.mDataCache.SetRunningHiddenTest( True )
				scenario = AllNavigation( )
				pvr.HiddenTestMgr.StartTest2( scenario )
			else :
				LOG_TRACE( 'Socket connect error' )

			#WinMgr.GetInstance( ).CloseWindow( )

		else :
			scenario = TestScenario( 'scenario', 'scenario' )
			item = self.mRoot.getchildren( )[ aContextAction ]
			for node in item :
				LOG_TRACE( 'TEST MGR root node  = %s' % node )
				scenario.AddChild( self.MakeChild( node ) )
			if ConnectSocket( ) :
				self.mDataCache.SetRunningHiddenTest( True )
				pvr.HiddenTestMgr.StartTest( scenario )
			else :
				LOG_TRACE( 'Socket connect error' )


	def MakeChild( self, aNode ) :
		if aNode.tag.lower( ) == 'loop' :
			return self.MakeChildLoop( aNode )
		elif aNode.tag.lower( ) == 'sendkey' :
			return SendKeySuite( aNode.tag, aNode.text )
		elif aNode.tag.lower( ) == 'sleep' :
			return SleepSuite( aNode.tag, aNode.text )
		elif aNode.tag.lower( ) == 'waitevent' :
			return WaitEventSuite( aNode.tag, aNode.text )
		elif aNode.tag.lower( ) == 'sendevent' :
			return SendEventSuite( aNode.tag, aNode.text )


	def MakeChildLoop( self, aNode ) :
		count = 1
		if aNode.get( 'repeat' ) != None :
			count = aNode.get( 'repeat' )
		LOG_TRACE( 'TEST MGR test repeat = %s' % count )
		loop = LoopSuite( 'loop', count )
		for node in aNode :
			loop.AddChild( self.MakeChild( node ) )
		return loop


	def CheckProperty( self ) :
		self.OpenBusyDialog( )
		from ElisProperty import GetPropertyTable
		table = GetPropertyTable( )
		errcnt = 0
		for prop in table :
			target = self.mCommander.Property_GetValue( prop[0] )
			if len( target ) != ( len( prop ) - 1 ) :
				self.CloseBusyDialog( )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), 'Property length is different', 'Name = %s' % prop[0], 'prop = %s, target = %s' % ( len( target ), ( len( prop ) - 1 ) ) )
				dialog.doModal( )
				return

			for i in range( len( target ) ) :
				print 'mValue = %s' % target[i].mValue
				print 'mString = %s' % target[i].mString
				print 'val = %s' % prop[i+1][0]
				print 'string = %s' % prop[i+1][1]
				print 'mValue = %s' % target[i].mValue
				print 'mString = %s' % target[i].mString

				if prop[i+1][0] != target[i].mValue :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), 'Property value is different', 'Name = %s' % prop[0], 'prop = %s, target = %s' % ( prop[i+1][0], target[i].mValue ) )
					dialog.doModal( )
					errcnt = errcnt + 1
					
				if prop[i+1][1] != target[i].mString :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), 'Property string is different', 'Name = %s' % prop[0], 'prop = %s, target = %s' % ( prop[i+1][1], target[i].mString ) )	
					dialog.doModal( )
					errcnt = errcnt + 1

		self.CloseBusyDialog( )
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( 'Complete', 'Property check finished', 'error cnt = %s' % errcnt )
		dialog.doModal( )
