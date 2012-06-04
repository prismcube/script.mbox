from pvr.gui.WindowImport import *
import pvr.HiddenTestMgr as TestMgr
import struct, socket, fcntl
SIOCGIFNETMASK = 0x891b


TEST_ZAPPING_NULL = 0
TEST_ZAPPING_EPG = 1
TEST_WINDOWS = 2

PORT = 56892
#HOST = '192.168.101.169'

class KeyCode( object ):
	KEY_FROM_NONE = 0
	KEY_FROM_RCU = 1
	KEY_FROM_TACT = 2
	KEY_FROM_FRONTWHEEL = 3

	FLAG_NONE = 0
	FLAG_REPEATED = 1
	
	VKEY_NO_KEY = 0
	VKEY_OK = 1
	VKEY_UP = 2
	VKEY_DOWN = 3
	VKEY_LEFT = 4
	VKEY_RIGHT = 5
	VKEY_RED = 6
	VKEY_GREEN = 7
	VKEY_YELLOW = 8
	VKEY_BLUE = 9
	VKEY_0 = 10		# 10

	VKEY_1 = 11
	VKEY_2 = 12
	VKEY_3 = 13
	VKEY_4 = 14
	VKEY_5 = 15
	VKEY_6 = 16
	VKEY_7 = 17
	VKEY_8 = 18
	VKEY_9 = 19
	VKEY_FF = 20	# 20

	VKEY_REV = 21
	VKEY_PLAY = 22
	VKEY_REC = 23
	VKEY_PAUSE = 24
	VKEY_STOP = 25
	VKEY_SLOW = 26
	VKEY_MENU = 27
	VKEY_EPG = 28
	VKEY_TEXT = 29
	VKEY_INFO = 30	# 30

	VKEY_BACK = 31
	VKEY_EXIT = 32
	VKEY_POWER = 33
	VKEY_MUTE = 34
	VKEY_PROG_UP = 35
	VKEY_PROG_DOWN = 36
	VKEY_VOL_UP = 37
	VKEY_VOL_DOWN = 38
	VKEY_HELP = 39
	VKEY_MEDIA = 40	# 40

	VKEY_ARCHIVE = 41
	VKEY_PREVCH = 42
	VKEY_FAVORITE = 43
	VKEY_OPT = 44
	VKEY_PIP = 45
	VKEY_SLEEP = 46
	VKEY_HISTORY = 47
	VKEY_ADDBOOKMARK = 48
	VKEY_BMKWINDOW = 49
	VKEY_JUMP_FORWARD = 50	# 50

	VKEY_JUMP_BACKWARD = 51
	VKEY_TV_RADIO = 52
	# added by lael98 20090331
	VKEY_SUBTITLE = 53
	VKEY_STAR = 54
	VKEY_CHECK = 55		# 55
	VKEY_SEARCH = 56
	VKEY_EDIT = 57
	VKEY_DELETE = 58
	VKEY_FUNC_A = 59
	VKEY_FUNC_B = 60	# 60

	VKEY_VOD_TIMESHIFT = 61
	VKEY_ADULT = 62
	VKEY_VOD = 63
	VKEY_SOURCE = 64 
	VKEY_VFORMAT = 65
	VKEY_AFORMAT = 66
	VKEY_WIDE = 67
	VKEY_LIST = 68


	VKEY_FRONT_MENU = 0x80 #0x80 
	VKEY_FRONT_EXIT = 0x81
	VKEY_FRONT_AUX = 0x82
	VKEY_FRONT_TV_R = 0x83
	VKEY_FRONT_OK = 0x84
	VKEY_FRONT_CCW = 0x85
	VKEY_FRONT_CW = 0x86

	VKEY_CHANGE_ADDR1 = 0x74,
	VKEY_CHANGE_ADDR2 = 0x75,
	VKEY_CHANGE_ADDR3 = 0x76,
	VKEY_CHANGE_ADDR4 = 0x77



class HiddenTest( BaseWindow ) :
	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )
		self.mStopflag = True
		self.mZappingTime = 5
		self.mCtrlLabel = None

	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mCtrlLabel = self.getControl( 100 )
		self.TestFunction( )
		self.mStopflag = True

	def onAction( self, aAction ) :
		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.mStopflag = False
			self.ZappingTestNull( ).join( )
			WinMgr.GetInstance( ).CloseWindow( )
	
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mStopflag = False
			self.ZappingTestNull( ).join( )
			WinMgr.GetInstance( ).CloseWindow( )


	def onClick( self, aControlId ):
		LOG_TRACE('')
		pass
		
 
	def onFocus( self, aControlId ):
		LOG_TRACE('')
		pass


	def TestFunction( self ) :
		context = []
		context.append( ContextItem( 'Zapping Test : TestWindow', TEST_ZAPPING_NULL ) )
		context.append( ContextItem( 'Zapping Test : EPGWindow', TEST_ZAPPING_EPG ) )
		context.append( ContextItem( 'Window Moving Test', TEST_WINDOWS ) )				
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
		dialog.doModal( )
		contextAction = dialog.GetSelectedAction( )
		if contextAction < 0 :
			return

		if contextAction == TEST_ZAPPING_NULL or contextAction == TEST_ZAPPING_EPG :
			self.ZappingTest( contextAction )

		elif contextAction == TEST_WINDOWS :
			self.mStopflag = True
			nRet = WindowMovingTest()
			if nRet == -1 :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( 'Error', 'LIRC open error' )
				dialog.doModal( )
				



	def ZappingTest( self , aType ) :
		if self.mDataCache.Channel_GetList( ) :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( 'Zapping Time', '%d' % self.mZappingTime, 2 )
 			dialog.doModal( )
 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.mZappingTime = int( dialog.GetString( ) )
			if aType == TEST_ZAPPING_EPG :
				TestMgr.GetInstance( ).SetZappingTime( self.mZappingTime )
				TestMgr.GetInstance( ).ZappingTestEPG( )
			else :
				
				self.ZappingTestNull( )
				
		else :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( 'Error', 'Channel List is Empty' )
			dialog.doModal( )
			return


	@RunThread
	def ZappingTestNull( self ) :
		current = self.mDataCache.Channel_GetCurrent( )
		while self.mStopflag :
			nextChannel = self.mDataCache.Channel_GetNext( current )
			self.mDataCache.Channel_SetCurrent( nextChannel.mNumber, nextChannel.mServiceType )
			self.mCtrlLabel.setLabel( 'Now Zapping %d : %s ... ' % ( nextChannel.mNumber, nextChannel.mName ) )
			current = nextChannel
			time.sleep( self.mZappingTime )



class WindowMovingTest( BaseWindow ) :
	def __init__( self ) :
		self.mKeySource = 0x1
		self.mKeyCode = 0x0	#keyCode
		self.mFlag = 0x0


	@RunThread
	def send(self, aMsg = None) :
		HOST = self.get_ip_address('eth0')
		try:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		except socket.error, msg:
			sys.stderr.write("[ERROR1] %s\n" % msg[1])
			return -1
		 
		try:
			sock.connect((HOST, PORT + 10))
		except socket.error, msg:
			sys.stderr.write("[ERROR2] %s\n" % msg[1])
			return -1
		
		VKey = KeyCode()
		testScene = [VKey.VKEY_MENU, VKey.VKEY_BACK]

		loop = 0
		while self.mStopflag :
			for key in testList :
				self.mCtrlLabel.setLabel( 'Moving %d : %s ... ' % ( loop, key ) )

				msg = struct.pack("3i",*[1, key, 0])
				LOG_TRACE( 'send[%s] size[%s] '% (key, len(msg) ) )

				sock.send( msg )
				time.sleep(4)

			loop += 1

	def get_ip_address( self, ifname ) : 
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
		return socket.inet_ntoa(fcntl.ioctl( \
			s.fileno(), \
			0x8915, # SIOCGIFADDR \
			struct.pack('256s', ifname[:15]) )[20:24])

	def Close( self ) :
		self.mStopflag = False
		self.send.join( )

