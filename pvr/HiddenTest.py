from pvr.gui.WindowImport import *
from pvr.HiddenTestMgr import *
import xbmc, xbmcaddon

E_TBR_BASIC	= 0
E_TBR_FM	= 1


FILE_NAME_TEST = xbmcaddon.Addon( 'script.mbox' ).getAddonInfo( 'path' ) + '/elmo_test.xml'


class HiddenTest( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mRoot = None
		self.mStartTime = 0


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
		context.append( ContextItem( 'TBR BASIC TEST', 9995 ) )
		context.append( ContextItem( 'TBR FM TEST', 9996 ) )
		context.append( ContextItem( 'PROPRTY CHECK', 9999 ) )
		if E_SUPPORT_SINGLE_WINDOW_MODE :
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
		elif aContextAction == 9995 :
			self.AutomaticAddTBR( E_TBR_BASIC )
		elif aContextAction == 9996 :
			self.AutomaticAddTBR( E_TBR_FM )
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
		WinMgr.GetInstance( ).CloseWindow( )


	def AutomaticAddTBR( self, aMode ) :
		self.OpenBusyDialog( )

		gmtFrom = self.mDataCache.Datetime_GetLocalTime( )
		
		if aMode == E_TBR_BASIC :
			channel1, channel2 = self.GetScenarioChannel( aMode )
		
			if channel1 and channel2 :
				ret = self.AddScenarioTimer( aMode, channel1, channel2 )
				if ret :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( 'Complete', 'Timer add complete' )
					dialog.doModal( )
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'Error', 'Channel match fail...' )
				dialog.doModal( )

		elif aMode == E_TBR_FM :
			for i in range( 14 ) :
				channel1, channel2 = self.GetScenarioChannel( aMode, i )
			
				if channel1 and channel2 :
					ret = self.AddScenarioTimer( aMode, channel1, channel2, i )
					if ret == False :
						break
				else :
					ret = False
					break

			if ret :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'Complete', 'Timer add complete' )
				dialog.doModal( )
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'Error', 'add E_TBR_FM timer  fail...' )
				dialog.doModal( )
				
		self.CloseBusyDialog( )
		WinMgr.GetInstance( ).CloseWindow( )


	def GetScenarioChannel( self, aMode, aStep=0 ) :
		channelList =  self.mDataCache.Channel_GetAllChannels( ElisEnum.E_SERVICE_TYPE_TV )
		if channelList  :
			channelCount = len( channelList )
		else :
			LOG_WARN( 'no channel')
			return None, None 
		
		channel1 = None
		channel2 = None
		matched = False

		if aMode == E_TBR_BASIC :
			for i in  range( channelCount ) :
				if channelList[i].mIsCA :
					continue
				if channel1 :
					channel2 = channelList[i]
					if channel1.mCarrier.mDVBS.mFrequency == channel2.mCarrier.mDVBS.mFrequency and channel1.mCarrier.mDVBS.mSymbolRate == channel2.mCarrier.mDVBS.mSymbolRate :
						matched = True
						break
					else :
						channel1 = None
						channel2 = None
				else :
					channel1 = channelList[i]

			if matched :
				return channel1, channel2
			else :
				return None, None

		elif ( aMode == E_TBR_FM and aStep == 0 ) or ( aMode == E_TBR_FM and aStep == 2 ) or ( aMode == E_TBR_FM and aStep == 4 ) or ( aMode == E_TBR_FM and aStep == 6 ) or ( aMode == E_TBR_FM and aStep == 8 ) or ( aMode == E_TBR_FM and aStep == 10 ) or ( aMode == E_TBR_FM and aStep == 12 ) : 
			for i in  range( channelCount ) :
				if channelList[i].mIsCA :
					continue
				if channel1 :
					channel2 = channelList[i]
					if channel1.mCarrier.mDVBS.mFrequency == channel2.mCarrier.mDVBS.mFrequency and channel1.mCarrier.mDVBS.mSymbolRate == channel2.mCarrier.mDVBS.mSymbolRate :
						matched = True
						break
					else :
						channel1 = None
						channel2 = None
				else :
					channel1 = channelList[i]

			if matched :
				return channel1, channel2
			else :
				return None, None

		elif ( aMode == E_TBR_FM and aStep == 1 ) or ( aMode == E_TBR_FM and aStep == 3 ) or ( aMode == E_TBR_FM and aStep == 5 ) or ( aMode == E_TBR_FM and aStep == 7 ) or ( aMode == E_TBR_FM and aStep == 9 ) or ( aMode == E_TBR_FM and aStep == 11 ) or ( aMode == E_TBR_FM and aStep == 13 ) :
			for i in  range( channelCount ) :
				if channelList[i].mIsCA :
					continue
				if channel1 :
					channel2 = channelList[i]
					if channel1.mCarrier.mDVBS.mFrequency == channel2.mCarrier.mDVBS.mFrequency and channel1.mCarrier.mDVBS.mSymbolRate == channel2.mCarrier.mDVBS.mSymbolRate :
						continue
					else :
						if channel1.mCarrier.mDVBS.mPolarization == channel2.mCarrier.mDVBS.mPolarization :
							matched = True
							break
						else :
							continue
				else :
					channel1 = channelList[i]

			if matched :
				return channel1, channel2
			else :
				return None, None
			

	def AddScenarioTimer( self, aMode, aChannel1, aChannel2, aStep=0 ) :
		if aMode == E_TBR_BASIC :
			self.mStartTime = self.mDataCache.Datetime_GetLocalTime( ) + 5 * 60
			for i in range( 10 ) :
				ret = True
				ret1 = self.mDataCache.Timer_AddManualTimer( aChannel1.mNumber, aChannel1.mServiceType, self.mStartTime, 5 * 60, aChannel1.mName, True )
				ret2 = self.mDataCache.Timer_AddManualTimer( aChannel2.mNumber, aChannel2.mServiceType, self.mStartTime, 5 * 60, aChannel2.mName, True )
				if ret1[0].mParam == -1 or ret1[0].mError == -1 :
					print ' test timer 1 add fail'
					ret = False
				if ret2[0].mParam == -1 or ret2[0].mError == -1 :
					print ' test timer 2 add fail'
					ret = False
				if ret :
					self.mStartTime = self.mStartTime + 10 * 60
				else :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( 'Error', 'Add timer fail...' )
					dialog.doModal( )
					return False

			return True

		elif ( aMode == E_TBR_FM and aStep == 0 ) or  ( aMode == E_TBR_FM and aStep == 1 ) : 
			if aStep == 0 :
				self.mStartTime = self.mDataCache.Datetime_GetLocalTime( ) + 5 * 60
			else :
				self.mStartTime = self.mStartTime + 10 * 60
			
			ret = True
			ret1 = self.mDataCache.Timer_AddManualTimer( aChannel1.mNumber, aChannel1.mServiceType, self.mStartTime, 5 * 60, aChannel1.mName, True )
			ret2 = self.mDataCache.Timer_AddManualTimer( aChannel2.mNumber, aChannel2.mServiceType, self.mStartTime, 5 * 60, aChannel2.mName, True )
			if ret1[0].mParam == -1 or ret1[0].mError == -1 :
				print ' test timer 1 add fail step = %s' % aStep
				ret = False
			if ret2[0].mParam == -1 or ret2[0].mError == -1 :
				print ' test timer 2 add fail step = %s' % aStep
				ret = False
			if ret :
				return True
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'Error', 'Add timer fail...step %s' % aStep )
				dialog.doModal( )
				return False

		elif ( aMode == E_TBR_FM and aStep == 2 ) or ( aMode == E_TBR_FM and aStep == 3 ) :
			self.mStartTime = self.mStartTime + 10 * 60
			
			ret = True
			ret1 = self.mDataCache.Timer_AddManualTimer( aChannel1.mNumber, aChannel1.mServiceType, self.mStartTime, 5 * 60, aChannel1.mName, True )
			ret2 = self.mDataCache.Timer_AddManualTimer( aChannel2.mNumber, aChannel2.mServiceType, self.mStartTime + 3*60, 5 * 60, aChannel2.mName, True )
			if ret1[0].mParam == -1 or ret1[0].mError == -1 :
				print ' test timer 1 add fail step = %s' % aStep
				ret = False
			if ret2[0].mParam == -1 or ret2[0].mError == -1 :
				print ' test timer 2 add fail step = %s' % aStep
				ret = False
			if ret :
				return True
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'Error', 'Add timer fail...step %s' % aStep )
				dialog.doModal( )
				return False

		elif ( aMode == E_TBR_FM and aStep == 4 ) or ( aMode == E_TBR_FM and aStep == 5 ) :
			self.mStartTime = self.mStartTime + 10 * 60
			
			ret = True
			ret1 = self.mDataCache.Timer_AddManualTimer( aChannel1.mNumber, aChannel1.mServiceType, self.mStartTime, 5 * 60, aChannel1.mName, True )
			ret2 = self.mDataCache.Timer_AddManualTimer( aChannel1.mNumber, aChannel1.mServiceType, self.mStartTime+5*60, 5 * 60, aChannel1.mName, True )
			ret3 = self.mDataCache.Timer_AddManualTimer( aChannel2.mNumber, aChannel2.mServiceType, self.mStartTime, 5 * 60, aChannel2.mName, True )
			ret4 = self.mDataCache.Timer_AddManualTimer( aChannel2.mNumber, aChannel2.mServiceType, self.mStartTime+5*60, 5 * 60, aChannel2.mName, True )
			if ret1[0].mParam == -1 or ret1[0].mError == -1 :
				print ' test timer 1 add fail step = %s' % aStep
				ret = False
			if ret2[0].mParam == -1 or ret2[0].mError == -1 :
				print ' test timer 2 add fail step = %s' % aStep
				ret = False
			if ret3[0].mParam == -1 or ret3[0].mError == -1 :
				print ' test timer 3 add fail step = %s' % aStep
				ret = False
			if ret4[0].mParam == -1 or ret4[0].mError == -1 :
				print ' test timer 4 add fail step = %s' % aStep
				ret = False
			if ret :
				self.mStartTime = self.mStartTime + 5 * 60
				return True
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'Error', 'Add timer fail...step %s' % aStep )
				dialog.doModal( )
				return False

		elif ( aMode == E_TBR_FM and aStep == 6 ) or ( aMode == E_TBR_FM and aStep == 7 ) :
			self.mStartTime = self.mStartTime + 10 * 60
			
			ret = True
			ret1 = self.mDataCache.Timer_AddManualTimer( aChannel1.mNumber, aChannel1.mServiceType, self.mStartTime, 5 * 60, aChannel1.mName, True )
			ret2 = self.mDataCache.Timer_AddManualTimer( aChannel1.mNumber, aChannel1.mServiceType, self.mStartTime+5*60, 5 * 60, aChannel1.mName, True )
			ret3 = self.mDataCache.Timer_AddManualTimer( aChannel2.mNumber, aChannel2.mServiceType, self.mStartTime+3*60, 5 * 60, aChannel2.mName, True )
			ret4 = self.mDataCache.Timer_AddManualTimer( aChannel2.mNumber, aChannel2.mServiceType, self.mStartTime+8*60, 5 * 60, aChannel2.mName, True )
			if ret1[0].mParam == -1 or ret1[0].mError == -1 :
				print ' test timer 1 add fail step = %s' % aStep
				ret = False
			if ret2[0].mParam == -1 or ret2[0].mError == -1 :
				print ' test timer 2 add fail step = %s' % aStep
				ret = False
			if ret3[0].mParam == -1 or ret3[0].mError == -1 :
				print ' test timer 3 add fail step = %s' % aStep
				ret = False
			if ret4[0].mParam == -1 or ret4[0].mError == -1 :
				print ' test timer 4 add fail step = %s' % aStep
				ret = False
			if ret :
				self.mStartTime = self.mStartTime + 5 * 60
				return True
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'Error', 'Add timer fail...step %s' % aStep )
				dialog.doModal( )
				return False

		elif ( aMode == E_TBR_FM and aStep == 8 ) or ( aMode == E_TBR_FM and aStep == 9 ) :
			self.mStartTime = self.mStartTime + 10 * 60
			
			ret = True
			ret1 = self.mDataCache.Timer_AddManualTimer( aChannel1.mNumber, aChannel1.mServiceType, self.mStartTime, 8 * 60, aChannel1.mName, True )
			ret2 = self.mDataCache.Timer_AddManualTimer( aChannel1.mNumber, aChannel1.mServiceType, self.mStartTime+10*60, 5 * 60, aChannel1.mName, True )
			ret3 = self.mDataCache.Timer_AddManualTimer( aChannel2.mNumber, aChannel2.mServiceType, self.mStartTime, 5 * 60, aChannel2.mName, True )
			ret4 = self.mDataCache.Timer_AddManualTimer( aChannel2.mNumber, aChannel2.mServiceType, self.mStartTime+10*60, 5 * 60, aChannel2.mName, True )
			if ret1[0].mParam == -1 or ret1[0].mError == -1 :
				print ' test timer 1 add fail step = %s' % aStep
				ret = False
			if ret2[0].mParam == -1 or ret2[0].mError == -1 :
				print ' test timer 2 add fail step = %s' % aStep
				ret = False
			if ret3[0].mParam == -1 or ret3[0].mError == -1 :
				print ' test timer 3 add fail step = %s' % aStep
				ret = False
			if ret4[0].mParam == -1 or ret4[0].mError == -1 :
				print ' test timer 4 add fail step = %s' % aStep
				ret = False
			if ret :
				self.mStartTime = self.mStartTime + 5 * 60
				return True
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'Error', 'Add timer fail...step %s' % aStep )
				dialog.doModal( )
				return False

		elif ( aMode == E_TBR_FM and aStep == 10 ) or ( aMode == E_TBR_FM and aStep == 11 ) :
			self.mStartTime = self.mStartTime + 10 * 60
			
			ret = True
			ret1 = self.mDataCache.Timer_AddManualTimer( aChannel1.mNumber, aChannel1.mServiceType, self.mStartTime, 10 * 60, aChannel1.mName, True )
			ret3 = self.mDataCache.Timer_AddManualTimer( aChannel2.mNumber, aChannel2.mServiceType, self.mStartTime+7 * 60, 10 * 60, aChannel2.mName, True )
			ret2 = self.mDataCache.Timer_AddManualTimer( aChannel1.mNumber, aChannel1.mServiceType, self.mStartTime+15*60, 10 * 60, aChannel1.mName, True )
			ret4 = self.mDataCache.Timer_AddManualTimer( aChannel2.mNumber, aChannel2.mServiceType, self.mStartTime+22*60, 10 * 60, aChannel2.mName, True )
			if ret1[0].mParam == -1 or ret1[0].mError == -1 :
				print ' test timer 1 add fail step = %s' % aStep
				ret = False
			if ret2[0].mParam == -1 or ret2[0].mError == -1 :
				print ' test timer 2 add fail step = %s' % aStep
				ret = False
			if ret3[0].mParam == -1 or ret3[0].mError == -1 :
				print ' test timer 3 add fail step = %s' % aStep
				ret = False
			if ret4[0].mParam == -1 or ret4[0].mError == -1 :
				print ' test timer 4 add fail step = %s' % aStep
				ret = False
			if ret :
				self.mStartTime = self.mStartTime + 30 * 60
				return True
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'Error', 'Add timer fail...step %s' % aStep )
				dialog.doModal( )
				return False

		elif ( aMode == E_TBR_FM and aStep == 12 ) or ( aMode == E_TBR_FM and aStep == 13 ) :
			self.mStartTime = self.mStartTime + 10 * 60
			
			ret = True
			ret1 = self.mDataCache.Timer_AddManualTimer( aChannel1.mNumber, aChannel1.mServiceType, self.mStartTime, 5 * 60, aChannel1.mName, True )
			ret2 = self.mDataCache.Timer_AddManualTimer( aChannel1.mNumber, aChannel1.mServiceType, self.mStartTime+7*60, 5 * 60, aChannel1.mName, True )
			ret3 = self.mDataCache.Timer_AddManualTimer( aChannel2.mNumber, aChannel2.mServiceType, self.mStartTime+2 * 60, 5 * 60, aChannel2.mName, True )
			ret4 = self.mDataCache.Timer_AddManualTimer( aChannel2.mNumber, aChannel2.mServiceType, self.mStartTime+9*60, 5 * 60, aChannel2.mName, True )
			if ret1[0].mParam == -1 or ret1[0].mError == -1 :
				print ' test timer 1 add fail step = %s' % aStep
				ret = False
			if ret2[0].mParam == -1 or ret2[0].mError == -1 :
				print ' test timer 2 add fail step = %s' % aStep
				ret = False
			if ret3[0].mParam == -1 or ret3[0].mError == -1 :
				print ' test timer 3 add fail step = %s' % aStep
				ret = False
			if ret4[0].mParam == -1 or ret4[0].mError == -1 :
				print ' test timer 4 add fail step = %s' % aStep
				ret = False
			if ret :
				self.mStartTime = self.mStartTime + 30 * 60
				return True
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'Error', 'Add timer fail...step %s' % aStep )
				dialog.doModal( )
				return False

			
			