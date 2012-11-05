from pvr.gui.WindowImport import *
from fileDownloader import DownloadFile
import stat

E_TYPE_PRISMCUBE = 1
E_TYPE_ADDONS = 2

E_CURRENT_INFO          = '/usr/share/xbmc/addons/script.mbox/resources/update.xml'
E_DOWNLOAD_INFO_PVS     = '/mnt/hdd0/program/download/update.xml'
E_DEFAULT_URL_PVS = 'http://192.168.100.142/RSS/update.xml'
E_DEFAULT_PATH_DOWNLOAD = '/mnt/hdd0/program/download'
E_DEFAULT_PATH_USB_UPDATE = '/media/sdb1'

E_CONTROL_ID_GROUP_PVS      = 9000
E_CONTROL_ID_LABEL_VERSION  = 100
E_CONTROL_ID_LABEL_DATE     = 101
E_CONTROL_ID_LABEL_SIZE     = 102
E_CONTROL_ID_LABEL_PERCENT  = 110

E_STRING_DATE        = MR_LANG( 'DATE' )
E_STRING_VERSION     = MR_LANG( 'VERSION' )
E_STRING_SIZE        = MR_LANG( 'SIZE' )
E_STRING_DESCRIPTION = MR_LANG( 'DESCRIPTION' )

CONTEXT_ACTION_REFRESH_CONNECT      = 1
CONTEXT_ACTION_CHANGE_ADDRESS       = 2
CONTEXT_ACTION_LOAD_DEFAULT_ADDRESS = 3

E_UPDATE_STEP_HOME        = 0
E_UPDATE_STEP_READY       = 1
E_UPDATE_STEP_PROVISION   = 2
E_UPDATE_STEP_DOWNLOAD    = 3
E_UPDATE_STEP_CHECKFILE   = 4
E_UPDATE_STEP_CHECKUSB    = 5
E_UPDATE_STEP_UNPACKING   = 6
E_UPDATE_STEP_VERIFY      = 7
E_UPDATE_STEP_FINISH      = 8
E_UPDATE_STEP_UPDATE_NOW  = 9
E_UPDATE_STEP_ERROR_NETWORK = 10

UPDATE_STEP						=	8
E_UPDATE_IMAGE					=	100
E_UPDATE_TEXTBOX				= 	200

E_UPDATE_PREV					=	7000
E_UPDATE_NEXT					=	7001	
E_UPDATE_PREV_LABEL				=	7005
E_UPDATE_NEXT_LABEL				=	7006

E_UPDATE_STEP_IMAGE				= 	7100
E_UPDATE_STEP_IMAGE_BACK		= 	7200


class PVSClass( object ) :
	def __init__( self ) :
		self.mName			= None
		self.mFileName		= None
		self.mDate			= None
		self.mDescription	= []
		self.mMd5			= None
		self.mSize			= 0
		self.mVersion		= None
		self.mId			= None
		self.mType			= None
		self.mError			= -1
		self.mProgress		= None


class SystemUpdate( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mIsCloseing = False
		self.mNoChannel = False


	def onInit( self )  :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mCtrlLabelDescTitle      = self.getControl( E_SETTING_DESCRIPTION )
		self.mCtrlLabelDate           = self.getControl( E_CONTROL_ID_LABEL_DATE )
		self.mCtrlLabelVersion        = self.getControl( E_CONTROL_ID_LABEL_VERSION )
		self.mCtrlLabelSize           = self.getControl( E_CONTROL_ID_LABEL_SIZE )
		self.mCtrlLabelPercent        = self.getControl( E_CONTROL_ID_LABEL_PERCENT )

		#parse settings.xml
		self.mUrlPVS = GetSetting( 'UpdateServer' )
		if not self.mUrlPVS :
			self.mUrlPVS = E_DEFAULT_URL_PVS
		self.mPVSData = None
		self.mCurrData = None
		self.mEnableLocalThread = False
		self.mLinkStatus = False
		self.mIsDownload = True
		self.mStepPage = E_UPDATE_STEP_HOME
		self.mCheckEthernetThread = None

		self.SetSettingWindowLabel( MR_LANG( 'Update' ) )

		self.SetPipScreen( )
		self.LoadNoSignalState( )

		if self.mIsCloseing == False :
			if self.CheckNoChannel( ) :
				self.mNoChannel = True
			else :
				self.mNoChannel = False
		else :
			if self.mNoChannel == False :
				if self.CheckNoChannel( ) :
					self.mDataCache.Channel_TuneDefault( )
					self.mDataCache.Player_AVBlank( False )
					self.mNoChannel = False
				else :
					self.mDataCache.Player_AVBlank( True )

		self.mInitialized = True

		self.UpdateStepPage( E_UPDATE_STEP_HOME )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.Close( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			if self.mStepPage == E_UPDATE_STEP_HOME :
				self.Close( )
			else :
				self.OpenAnimation( )
				self.DrawUpdateStep( self.mStepPage )
				self.UpdateStepPage( E_UPDATE_STEP_HOME )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )				

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )

		elif actionId == Action.ACTION_CONTEXT_MENU :
			if self.mStepPage == E_UPDATE_STEP_READY :
				self.ShowContextMenu( )


	def onClick( self, aControlId ) :
		groupId = self.GetGroupId( aControlId )
		if groupId == E_Input01 :
			if self.mStepPage == E_UPDATE_STEP_HOME :
				self.UpdateStepPage( E_UPDATE_STEP_READY )
			else :
				self.UpdateStepPage( E_UPDATE_STEP_PROVISION )

		elif groupId == E_Input02 :
			if self.mStepPage == E_UPDATE_STEP_HOME :
				self.UpdateChannel( )
			else :
				self.UpdateHandler( )
				self.mStepPage = E_UPDATE_STEP_READY
				self.UpdateControlGUI( E_CONTROL_ID_LABEL_PERCENT, '' )

		elif groupId == E_Input03 :
			self.UpdateStepPage( E_UPDATE_STEP_UPDATE_NOW )


	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return

		if self.mLastFocused != aControlId :
			self.ShowDescription( aControlId )
			self.mLastFocused = aControlId


	def OpenAnimation( self ) :
		self.setFocusId( E_FAKE_BUTTON )
		time.sleep( 0.3 )


	def CheckNoChannel( self ) :
		if self.mDataCache.Channel_GetList( ) :
			return True
		else :
			return False


	def Close( self ) :
		self.mIsCloseing = False

		if self.mEnableLocalThread and self.mCheckEthernetThread :
			self.mEnableLocalThread = False
			self.mCheckEthernetThread.join( )

		self.ResetAllControl( )
		self.SaveAsServerAddress( )
		self.SetVideoRestore( )
		WinMgr.GetInstance( ).CloseWindow( )


	@RunThread
	def CheckEthernetThread( self ) :
		while self.mEnableLocalThread :
			if self.mStepPage >= E_UPDATE_STEP_PROVISION and self.mStepPage <= E_UPDATE_STEP_DOWNLOAD :
				status = CheckEthernet( 'eth0' )
				if status == 'up' :
					self.mLinkStatus = True
				else :
					self.mLinkStatus = False
					self.UpdateStepPage( E_UPDATE_STEP_ERROR_NETWORK )

			time.sleep(1)


	@GuiLock
	def UpdateControlGUI( self, aCtrlID = None, aValue = None, aExtra = None ) :
		#LOG_TRACE( 'Enter control[%s] value[%s]'% (aCtrlID, aValue) )

		if aCtrlID == E_CONTROL_ID_LABEL_DATE :
			self.mCtrlLabelDate.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_VERSION :
			self.mCtrlLabelVersion.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_SIZE :
			self.mCtrlLabelSize.setLabel( aValue )

		elif aCtrlID == E_SETTING_DESCRIPTION :
			self.mCtrlLabelDescTitle.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_PERCENT :
			self.mCtrlLabelPercent.setLabel( aValue )


	def UpdatePropertyGUI( self, aPropertyID = None, aValue = None ) :
		#LOG_TRACE( 'Enter property[%s] value[%s]'% (aPropertyID, aValue) )
		if aPropertyID == None :
			return

		self.mWin.setProperty( aPropertyID, aValue )


	def ResetLabel( self ) :
		self.SetEnableControl( E_Input02, False )
		self.SetEnableControl( E_Input03, False )

		self.UpdateControlGUI( E_CONTROL_ID_LABEL_PERCENT, '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_DATE, '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_VERSION, '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_SIZE, '' )
		self.UpdatePropertyGUI( 'DescriptionTitle', '' )
		self.UpdatePropertyGUI( 'UpdateDescription', '' )


	def DrawUpdateStep( self, aStep = None ) :
		if aStep == None :
			for i in range( UPDATE_STEP ) :
				self.getControl( E_UPDATE_STEP_IMAGE_BACK + i ).setVisible( False )
				self.getControl( E_UPDATE_STEP_IMAGE + i ).setVisible( False )
		else :
			if aStep > E_UPDATE_STEP_READY and aStep < E_UPDATE_STEP_ERROR_NETWORK :
				aStep = aStep - 2
			else :
				aStep = -1

			for i in range( UPDATE_STEP ) :
				if i == aStep :
					self.getControl( E_UPDATE_STEP_IMAGE + i ).setVisible( True )
				else :
					self.getControl( E_UPDATE_STEP_IMAGE + i ).setVisible( False )
				self.getControl( E_UPDATE_STEP_IMAGE_BACK + i ).setVisible( True )

			self.SetFocusControl( E_CONTROL_ID_GROUP_PVS )
			LOG_TRACE('------------------drawStep[%s]'% aStep )


	def UpdateLabelPVSInfo( self ) :
		if self.mPVSData == None or self.mPVSData.mError != 0 :
			return

		self.ResetLabel( )

		iPVS = self.mPVSData
		if iPVS.mName :
			self.SetEnableControl( E_Input02, True )

			self.UpdateControlGUI( E_CONTROL_ID_LABEL_DATE, '%s : %s'% ( E_STRING_DATE, iPVS.mDate ) )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_VERSION, '%s : %s'% ( E_STRING_VERSION, iPVS.mVersion ) )
			lblSize = ''
			if iPVS.mSize < 10000000 :
				lblSize = '%s Kb'% ( iPVS.mSize / 1000 )
			else :
				lblSize = '%s Mb'% ( iPVS.mSize / 1000000 )

			self.UpdateControlGUI( E_CONTROL_ID_LABEL_SIZE, '%s : %s'% ( E_STRING_SIZE, lblSize ) )
			self.UpdatePropertyGUI( 'DescriptionTitle', E_STRING_DESCRIPTION )
			self.UpdatePropertyGUI( 'UpdateDescription', iPVS.mDescription )

			lblDescTitle = ''
			if iPVS.mType == E_TYPE_PRISMCUBE :
				lblDescTitle = MR_LANG( 'System, OS, MBox Update' )
			elif iPVS.mType == E_TYPE_ADDONS :
				lblDescTitle = MR_LANG( 'Addon Application Update' )

			self.UpdateControlGUI( E_SETTING_DESCRIPTION, lblDescTitle )
				

	def InitPVSData( self ) :
		if self.mPVSData == None or self.mPVSData.mError != 0 :
			label = MR_LANG( 'No one' )			
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_DATE, label )
			self.SetEnableControl( E_Input02, False )
			return 

		self.SetEnableControl( E_Input02, True )

		label2 = self.mPVSData.mVersion
		if self.mCurrData and self.mCurrData.mError == 0 and self.mCurrData.mVersion == self.mPVSData.mVersion :
			label2 = 'Updated'
			self.mPVSData.mError = -1
			self.SetEnableControl( E_Input02, False )

		self.SetControlLabel2String( E_Input02, '%s'% label2 )
		self.UpdateLabelPVSInfo( )


	def Provisioning( self ) :
		appURL = None
		self.mPVSData = None
		self.ResetLabel( )

		if not self.mUrlPVS :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Update server address is wrong, retry to input URL' ) )
 			dialog.doModal( )
 			return

		self.OpenBusyDialog( )

		try :
			download = GetURLpage( self.mUrlPVS )
			#LOG_TRACE( '[pvs]%s'% download )

			if download :
				iPVS = PVSClass( )
				iPVS.mName = MR_LANG( 'Firmware Update' )
				iPVS.mType = E_TYPE_PRISMCUBE

				iPVS.mFileName = ParseStringInXML( download, 'filename' )
				"""
				try :
					iPVS.mFileName = os.path.basename( iPVS.mFileName )
				except Exception, e :
					LOG_ERR( 'except[%s] files[%s]'% ( e, iPVS.mFileName ) )

				LOG_TRACE('filename[%s]'% iPVS.mFileName )
				"""

				iPVS.mDate    = ParseStringInXML( download, 'date' )
				iPVS.mVersion = ParseStringInXML( download, 'version' )
				iPVS.mSize    = int( ParseStringInXML( download, 'size' ) )
				iPVS.mMd5     = ParseStringInXML( download, 'md5' )
				appURL        = ParseStringInXML( download, 'application' )

				description = ''
				descList = ParseStringInXML( download, 'description' )
				LOG_TRACE( 'desc[%s]'% descList )

				if descList and len( descList ) > 0 :
					for item in descList :
						description += '%s\n'% item
				iPVS.mDescription = description
				iPVS.mError = 0

				self.mPVSData = iPVS

				CreateDirectory( E_DEFAULT_PATH_DOWNLOAD )
				f = open( E_DOWNLOAD_INFO_PVS, 'w' )
				f.write( download )
				f.close( )

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )

		self.InitPVSData( )

		self.CloseBusyDialog( )

		if not download :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Can not connect address, retry to input URL' ) )
 			dialog.doModal( )

		elif self.mCurrData and self.mCurrData.mError == 0 and self.mCurrData.mVersion == self.mPVSData.mVersion :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Latest version' ), MR_LANG( 'Aready Updated' ) )
 			dialog.doModal( )


	def ShowContextMenu( self ) :
		context = []
		context.append( ContextItem( MR_LANG( 'Refresh' ),              CONTEXT_ACTION_REFRESH_CONNECT ) )
		context.append( ContextItem( MR_LANG( 'Change Address' ),       CONTEXT_ACTION_CHANGE_ADDRESS ) )
		context.append( ContextItem( MR_LANG( 'Load Default Address' ), CONTEXT_ACTION_LOAD_DEFAULT_ADDRESS ) )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
		dialog.doModal( )

		contextAction = dialog.GetSelectedAction( )
		if contextAction == -1 :
			return

		self.DoContextAction( contextAction ) 


	def DoContextAction( self, aContextAction ) :
		#LOG_TRACE( 'aContextAction=%d' %aContextAction )
		if aContextAction == CONTEXT_ACTION_REFRESH_CONNECT :
			RemoveDirectory( E_DEFAULT_PATH_DOWNLOAD )
			self.UpdateStepPage( E_UPDATE_STEP_PROVISION )

		elif aContextAction == CONTEXT_ACTION_CHANGE_ADDRESS :
			self.SetChangeServerURL( )
			label = MR_LANG( 'Change Server Address' )
			kb = xbmc.Keyboard( self.mUrlPVS, label, False )
			kb.doModal( )

			chageUrl = ''
			chageUrl = kb.getText( )
			if not chageUrl :
				return

			self.mUrlPVS = chageUrl
			#self.UpdateStepPage( E_UPDATE_STEP_PROVISION )

		elif aContextAction == CONTEXT_ACTION_LOAD_DEFAULT_ADDRESS :
			self.mUrlPVS = E_DEFAULT_URL_PVS
			SetSetting( 'UpdateServer', '%s'% E_DEFAULT_URL_PVS )
			self.UpdateStepPage( E_UPDATE_STEP_PROVISION )


	def SaveAsServerAddress( self ) :
		if E_DEFAULT_URL_PVS == self.mUrlPVS :
			return

		loadURL = GetSetting( 'UpdateServer' )
		if loadURL == self.mUrlPVS :
			return

		title = MR_LANG( 'Save update server URL' )
		line1 = MR_LANG( 'Do you want to save ?' )
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( title, '%s\n%s'% ( line1, self.mUrlPVS ) )
		dialog.doModal( )

		answer = dialog.IsOK( )

		#answer is yes
		if answer != E_DIALOG_STATE_YES :
			return

		SetSetting( 'UpdateServer', '%s'% self.mUrlPVS )


	def UpdateStepPage( self, aStep ) :
		self.mStepPage = aStep
		stepResult = True

		if aStep == E_UPDATE_STEP_READY :
			self.OpenAnimation( )
			self.DrawUpdateStep( aStep )
		elif aStep > E_UPDATE_STEP_READY :
			self.DrawUpdateStep( aStep )


		if aStep == E_UPDATE_STEP_HOME :
			self.ResetAllControl( )
			self.AddInputControl( E_Input01, MR_LANG( 'Firmware Update' ), '', MR_LANG( 'Download STB firmware, check network live' ) )
			self.AddInputControl( E_Input02, MR_LANG( 'Channel Update' ), '', MR_LANG( 'ChannelList update' ) )

			self.SetEnableControl( E_Input01, True )
			self.SetEnableControl( E_Input02, True )
			self.SetVisibleControl( E_Input03, False )

			self.InitControl( )
			self.SetFocusControl( E_Input01 )

			if self.mEnableLocalThread and self.mCheckEthernetThread :
				self.mEnableLocalThread = False
				self.mCheckEthernetThread.join( )
				self.mCheckEthernetThread = None
			self.mEnableLocalThread = False
			self.UpdatePropertyGUI( 'CurrentDescription', '' )
			self.UpdatePropertyGUI( 'UpdateStep', 'False' )

		elif aStep == E_UPDATE_STEP_READY :
			self.ResetAllControl( )
			self.AddInputControl( E_Input01, MR_LANG( 'Update Check' ), '', MR_LANG( 'Check provisionning firmware from PrismCube Server, check network live' ) )
			self.AddInputControl( E_Input02, MR_LANG( 'Firmware Update' ), 'Not Checked', MR_LANG( 'Click to download' ) )
			self.AddInputControl( E_Input03, MR_LANG( '- Apply' ),      '', MR_LANG( 'Update now, Reboot and get update stb' ) )
			self.SetEnableControl( E_Input02, False )
			self.SetEnableControl( E_Input03, False )
			self.SetVisibleControl( E_Input03, True )

			self.InitControl( )
			self.SetFocusControl( E_Input01 )

			self.CheckCurrentVersion( )

		elif aStep == E_UPDATE_STEP_PROVISION :
			self.UpdatePropertyGUI( 'UpdateStep', 'True' )
			self.Provisioning( )

		elif aStep == E_UPDATE_STEP_DOWNLOAD :
			self.mEnableLocalThread = True
			self.mCheckEthernetThread = self.CheckEthernetThread( )

			if self.mPVSData == None or self.mPVSData.mError != 0 :
				stepResult = False
			else :
				stepResult = self.GetDownload( self.mPVSData )

			if self.mEnableLocalThread and self.mCheckEthernetThread :
				self.mEnableLocalThread = False
				self.mCheckEthernetThread.join( )
				self.mCheckEthernetThread = None
			self.mEnableLocalThread = False

		elif aStep == E_UPDATE_STEP_CHECKFILE :
			if self.mPVSData == None or self.mPVSData.mError != 0 :
				return False

			tempFile = E_DEFAULT_PATH_DOWNLOAD + '/%s'% os.path.basename( self.mPVSData.mFileName )
			if os.stat( tempFile )[stat.ST_SIZE] != self.mPVSData.mSize :
				return False

			self.OpenBusyDialog( )
			ret = CheckMD5Sum( tempFile, self.mPVSData.mMd5 )
			self.CloseBusyDialog( )
			if not ret :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'File is corrupt, Try again download' ) )
				dialog.doModal( )
				stepResult = False


		elif aStep == E_UPDATE_STEP_CHECKUSB :
			if not CheckDirectory( E_DEFAULT_PATH_USB_UPDATE ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'USB is not detected, Please insert USB' ) )
				dialog.doModal( )
				stepResult = False

		elif aStep == E_UPDATE_STEP_UNPACKING :
			if self.mPVSData == None or self.mPVSData.mError != 0 :
				return False

			tempFile = E_DEFAULT_PATH_DOWNLOAD + '/%s'% os.path.basename( self.mPVSData.mFileName )
			if os.stat( tempFile )[stat.ST_SIZE] != self.mPVSData.mSize :
				return False

			usbPath = self.mDataCache.USB_GetMountPath( )
			if not usbPath :
				usbPath = E_DEFAULT_PATH_USB_UPDATE

			time.sleep( 0.3 )
			self.OpenBusyDialog( )
			stepResult = CopyToUSB( tempFile, usbPath )
			self.CloseBusyDialog( )

			if not stepResult :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Check USB' ) )
				dialog.doModal( )


		elif aStep == E_UPDATE_STEP_VERIFY :
			pass

		elif aStep == E_UPDATE_STEP_FINISH :
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_PERCENT, MR_LANG( 'Update Ready' ) )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Update Ready' ) )
			dialog.doModal( )
			self.SetEnableControl( E_Input03, True )


		elif aStep == E_UPDATE_STEP_UPDATE_NOW :
			line1 = MR_LANG( 'Now reboot and follow from VFD' )
			line2 = MR_LANG( 'Are you sure ?' )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Attention' ), '%s\n%s'% ( line1, line2 ) )
			dialog.doModal( )
			ret = dialog.IsOK( )
			if ret == E_DIALOG_STATE_YES :
				CopyToFile( E_DOWNLOAD_INFO_PVS, E_CURRENT_INFO )
				RemoveDirectory( E_DEFAULT_PATH_DOWNLOAD )
				self.mDataCache.System_Reboot( )


		elif aStep == E_UPDATE_STEP_ERROR_NETWORK :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Disconnected Network' ) )
			dialog.doModal( )
			if self.mEnableLocalThread and self.mCheckEthernetThread :
				self.mEnableLocalThread = False
				self.mCheckEthernetThread.join( )
				self.mCheckEthernetThread = None
			self.mEnableLocalThread = False

		return stepResult

		
	def UpdateHandler( self ) :
		LOG_TRACE('----------------pvs[%s]'% self.mPVSData )
		if self.mPVSData == None or self.mPVSData.mError != 0 :
			return

		LOG_TRACE('----------------download File[%s]'% self.mPVSData.mFileName )

		self.UpdateControlGUI( E_CONTROL_ID_LABEL_PERCENT, MR_LANG( 'Downloading...' ) )
		if not self.UpdateStepPage( E_UPDATE_STEP_DOWNLOAD ) :
			return

		self.UpdateControlGUI( E_CONTROL_ID_LABEL_PERCENT, MR_LANG( 'File Checking...' ) )
		if not self.UpdateStepPage( E_UPDATE_STEP_CHECKFILE ) :
			return

		LOG_TRACE('----------------path down[%s] usb[%s]'% ( E_DEFAULT_PATH_DOWNLOAD, E_DEFAULT_PATH_USB_UPDATE ) )
		if not self.UpdateStepPage( E_UPDATE_STEP_CHECKUSB ) :
			return

		self.UpdateControlGUI( E_CONTROL_ID_LABEL_PERCENT, MR_LANG( 'Image Unpacking...' ) )
		if not self.UpdateStepPage( E_UPDATE_STEP_UNPACKING ) :
			return

		self.UpdateControlGUI( E_CONTROL_ID_LABEL_PERCENT, MR_LANG( 'Verify Checking...' ) )
		if not self.UpdateStepPage( E_UPDATE_STEP_VERIFY ) :
			return

		self.UpdateStepPage( E_UPDATE_STEP_FINISH )


	def GetDownload( self, aPVS ) :
		isExist = GetURLpage( aPVS.mFileName, False )

		if not isExist :
			return False

		self.mWorkingItem = aPVS
		self.mWorkingDownloader = None

		#make tempDir, write local file
		CreateDirectory( E_DEFAULT_PATH_DOWNLOAD )

		isResume = False
		self.mIsDownload = True
		tempFile = E_DEFAULT_PATH_DOWNLOAD + '/%s'% os.path.basename( aPVS.mFileName )
		if os.path.exists( tempFile ) :
			if os.stat( tempFile )[stat.ST_SIZE] == aPVS.mSize :
				return True

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Already exist download file' ), MR_LANG( 'Do you want to continue ?' ) )
			dialog.doModal( )

			ret = dialog.IsOK( )
			if ret == E_DIALOG_STATE_CANCEL :
				return False

			elif ret == E_DIALOG_STATE_YES :
				isResume = True

		self.mDialogProgress = xbmcgui.DialogProgress( )
		self.mDialogProgress.create( aPVS.mName, MR_LANG( 'Downloading...' ) )

		self.mWorkingDownloader = DownloadFile( aPVS.mFileName, tempFile )
		if isResume :
			self.mWorkingDownloader.resume( self.ShowProgress )
		else :
			self.mWorkingDownloader.download( self.ShowProgress )

		self.mDialogProgress.close( )

		self.mDialogProgress = None
		self.mWorkingItem = None
		self.mWorkingDownloader = None

		return self.mIsDownload


	#this function is callback
	def ShowProgress( self, cursize = 0 ) :
		#if cursize :
		#	LOG_TRACE('--------------down size[%s] tot[%s]'% ( cursize, self.mWorkingItem.mSize ) )

		if self.mDialogProgress and self.mWorkingItem.mSize :
			#per = 1.0 * cursize / self.mWorkingItem.mSize * 100
			#LOG_TRACE('--------------down size[%s] per[%s] tot[%s]'% ( cursize, per, self.mWorkingItem.mSize ) )
			self.mDialogProgress.update( 1.0 * cursize / self.mWorkingItem.mSize * 100 )

			if self.mWorkingDownloader and self.mDialogProgress.iscanceled( ) or \
			   self.mWorkingDownloader and self.mLinkStatus != True :
				self.mWorkingDownloader.abort( True )
				self.mIsDownload = False

				LOG_TRACE( '--------------abort' )


	def CheckCurrentVersion( self ) :
		lbldesc = ''
		try :
			f = open( E_CURRENT_INFO, 'r' )
			currInfo = f.read( )
			f.close( )

			iPVS = PVSClass( )
			iPVS.mVersion = ParseStringInXML( currInfo, 'version' )
			iPVS.mDate    = ParseStringInXML( currInfo, 'date' )

			description = ''
			descList = ParseStringInXML( currInfo, 'description' )
			LOG_TRACE( 'desc[%s]'% descList )

			if descList and len( descList ) > 0 :
				for item in descList :
					description += '  %s\n'% item

			iPVS.mDescription = description
			iPVS.mError = 0

			lbldesc += '%s : %s\n'% ( E_STRING_VERSION, iPVS.mVersion )
			lbldesc += '%s : %s\n'% ( E_STRING_DATE, iPVS.mDate )
			lbldesc += '%s\n%s\n'% ( E_STRING_DESCRIPTION, iPVS.mDescription )

			self.mCurrData = iPVS

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )

		self.UpdatePropertyGUI( 'CurrentDescription', lbldesc )


	def UpdateChannel( self ) :
		kb = xbmc.Keyboard( PRISMCUBE_SERVER, MR_LANG( 'Enter server address' ), False )			
		kb.setHiddenInput( False )
		kb.doModal( )
		if kb.isConfirmed( ) :
			updatelist = self.GetServerInfo( kb.getText( ) )
			LOG_TRACE( 'updatelist = %s' % updatelist )
			showtext = []
			for text in updatelist :
				showtext.append( text[0] )
			LOG_TRACE( 'showtext = %s' % showtext )
			if updatelist :
				dialog = xbmcgui.Dialog( )
				ret = dialog.select( MR_LANG( 'Select Package' ), showtext )
				if ret >= 0 :
					self.GetChannelUpdate( kb.getText( ), updatelist[ret][1] )
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Connect server error' ) )
				dialog.doModal( )


	def GetServerInfo( self, aAddress ) :
		try :
			import urllib2
			updatefile = urllib2.urlopen( aAddress + '/channel/package.xml' )
			inputline = updatefile.readlines( )
			updatefile.close( )
			updatelist = []
			for line in inputline :
				updatelist.append( string.split( line ) )

			return updatelist
			
		except Exception, e :
			LOG_TRACE( 'Error exception[%s]' % e )
			return None


	def GetChannelUpdate( self, aAddress, aPath ) :
		self.ShowProgress( MR_LANG( 'Now updating...' ), 20 )
		ret = self.DownloadxmlFile( aAddress, aPath )
		if ret :
			self.mCommander.System_SetManualChannelList( '/tmp/defaultchannel.xml' )
			self.mCommander.System_SetDefaultChannelList( )
			self.mDataCache.LoadAllSatellite( )
			self.mTunerMgr.SyncChannelBySatellite( )
			self.mDataCache.Channel_ReLoad( )
			self.mDataCache.Player_AVBlank( False )
			self.mProgress.SetResult( True )
			return True
		else :
			self.mProgress.SetResult( True )
			return False


	def DownloadxmlFile( self, aAddress, aPath ) :
		try :
			import urllib2
			updatefile = urllib2.urlopen( aAddress + aPath )
			output = open( '/tmp/defaultchannel.xml', 'wb' )
			output.write( updatefile.read( ) )
			output.close( )
			return True
		except Exception, e :
			LOG_TRACE( 'Error exception[%s]' % e )
			return False


	@RunThread
	def ShowProgress( self, aString, aTime ) :
		self.mProgress = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_FORCE_PROGRESS )
		self.mProgress.SetDialogProperty( aTime, aString )
		self.mProgress.doModal( )