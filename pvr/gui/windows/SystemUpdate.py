from pvr.gui.WindowImport import *
from fileDownloader import DownloadFile
import stat

E_TYPE_PRISMCUBE = 1
E_TYPE_ADDONS = 2

E_DEFAULT_URL_PVS = 'http://192.168.100.142/RSS/update.xml'
E_DEFAULT_PATH_DOWNLOAD = '/mnt/hdd0/program/download'
#E_DEFAULT_PATH_USB_UPDATE = '/media/usb'
E_DEFAULT_PATH_USB_UPDATE = '/media/sdb1'

E_CONTROL_ID_GROUP_PVS         = 49
E_CONTROL_ID_LIST_PVS          = 50
E_CONTROL_ID_LABEL_DATE        = 100
E_CONTROL_ID_LABEL_VERSION     = 101
E_CONTROL_ID_LABEL_SIZE        = 102
E_CONTROL_ID_LABEL_DESCRIPTION = 103
E_CONTROL_ID_LABEL_PERCENT     = 110

E_STRING_DATE        = MR_LANG( 'DATE' )
E_STRING_VERSION     = MR_LANG( 'VERSION' )
E_STRING_SIZE        = MR_LANG( 'SIZE' )
E_STRING_DESCRIPTION = MR_LANG( 'DESCRIPTION' )

CONTEXT_ACTION_REFRESH_CONNECT      = 1
CONTEXT_ACTION_CHANGE_ADDRESS       = 2
CONTEXT_ACTION_LOAD_DEFAULT_ADDRESS = 3

E_UPDATE_STEP_HOME        = 0
E_UPDATE_STEP_PROVISION   = 1
E_UPDATE_STEP_DOWNLOAD    = 2
E_UPDATE_STEP_CHECKFILE   = 3
E_UPDATE_STEP_CHECKUSB    = 4
E_UPDATE_STEP_UNPACKING   = 5
E_UPDATE_STEP_VERIFY      = 6
E_UPDATE_STEP_FINISH      = 7
E_UPDATE_STEP_UPDATE_NOW  = 8
E_UPDATE_STEP_CHECK_NETWORK = 10

UPDATE_STEP						=	10
E_UPDATE_IMAGE					=	100
E_UPDATE_TEXTBOX				= 	200

E_UPDATE_PREV					=	7000
E_UPDATE_NEXT					=	7001	
E_UPDATE_PREV_LABEL				=	7005
E_UPDATE_NEXT_LABEL				=	7006

E_UPDATE_STEP_IMAGE				= 	7100
E_UPDATE_STEP_IMAGE_BACK		= 	7200


class PVSList( object ) :
	def __init__( self ) :
		self.mName = None
		self.mFileName = None
		self.mDate = None
		self.mDescription = []
		self.mMd5 = None
		self.mSize = 0
		self.mVersion = None
		self.mId = None
		self.mType = None
		self.mError = 0


class SystemUpdate( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mIsCloseing = False
		self.mNoChannel = False


	def onInit( self )  :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mCtrlLabelDescTitle      = self.getControl( E_SETTING_DESCRIPTION )
		self.mCtrlGroupPVS            = self.getControl( E_CONTROL_ID_GROUP_PVS )
		self.mCtrlListPVS             = self.getControl( E_CONTROL_ID_LIST_PVS )
		self.mCtrlLabelDate           = self.getControl( E_CONTROL_ID_LABEL_DATE )
		self.mCtrlLabelVersion        = self.getControl( E_CONTROL_ID_LABEL_VERSION )
		self.mCtrlLabelSize           = self.getControl( E_CONTROL_ID_LABEL_SIZE )
		self.mCtrlLabelDescription    = self.getControl( E_CONTROL_ID_LABEL_DESCRIPTION )
		self.mCtrlLabelPercent        = self.getControl( E_CONTROL_ID_LABEL_PERCENT )

		#win test only
		if not self.mPlatform.IsPrismCube( ) :
			global E_DEFAULT_PATH_DOWNLOAD, E_DEFAULT_PATH_USB_UPDATE
			E_DEFAULT_PATH_DOWNLOAD   = 'd:\\temp\\test'
			E_DEFAULT_PATH_USB_UPDATE = 'd:\\temp\\test\\usb'

		#parse settings.xml
		self.mUrlPVS = GetSetting( 'UpdateServer' )
		if not self.mUrlPVS :
			self.mUrlPVS = E_DEFAULT_URL_PVS
		self.mListItems = None
		self.mPVSList = []
		self.mEnableLocalThread = False
		self.mLinkStatus = False

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
			if self.mStepPage == E_UPDATE_STEP_HOME :
				self.Close( )
			else :
				self.UpdateStepPage( E_UPDATE_STEP_HOME )
				
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.Close( )

		#elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN :
		#	self.UpdateLabelPVSInfo( )
		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )				

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )

		elif actionId == Action.ACTION_CONTEXT_MENU :
			if self.mStepPage == E_UPDATE_STEP_PROVISION :
				self.ShowContextMenu( )


	def onClick( self, aControlId ) :
		if aControlId == E_CONTROL_ID_LIST_PVS :
			self.UpdateHandler( )

		else :
			groupId = self.GetGroupId( aControlId )
			if groupId == E_Input01 :
				self.UpdateStepPage( E_UPDATE_STEP_PROVISION )

			elif groupId == E_Input02 :
				if self.mStepPage == E_UPDATE_STEP_HOME :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'No supported' ) )
					dialog.doModal( )

				else :
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
					self.UpdateStepPage( E_UPDATE_STEP_CHECK_NETWORK )

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

		elif aCtrlID == E_CONTROL_ID_LABEL_DESCRIPTION :
			self.mCtrlLabelDescription.setLabel( aValue )

		elif aCtrlID == E_SETTING_DESCRIPTION :
			self.mCtrlLabelDescTitle.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_PERCENT :
			self.mCtrlLabelPercent.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LIST_PVS :
			if aExtra == E_TAG_SET_SELECT_POSITION :
				self.mCtrlListPVS.selectItem( aValue )
			elif aExtra == E_TAG_ENABLE :
				self.mCtrlListPVS.setEnabled( aValue )
			elif aExtra == E_TAG_ADD_ITEM :
				self.mCtrlListPVS.addItems( aValue )


	def UpdatePropertyGUI( self, aPropertyID = None, aValue = None ) :
		#LOG_TRACE( 'Enter property[%s] value[%s]'% (aPropertyID, aValue) )
		if aPropertyID == None :
			return

		self.mWin.setProperty( aPropertyID, aValue )


	def ResetLabel( self ) :
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
			for i in range( UPDATE_STEP ) :
				if i == aStep :
					self.getControl( E_UPDATE_STEP_IMAGE + i ).setVisible( True )
				else :
					self.getControl( E_UPDATE_STEP_IMAGE + i ).setVisible( False )
				self.getControl( E_UPDATE_STEP_IMAGE_BACK + i ).setVisible( True )

			self.SetFocusControl( E_UPDATE_NEXT )



	def UpdateLabelPVSInfo( self ) :
		if self.mPVSList == None or len(self.mPVSList) < 1 :
			return

		self.ResetLabel( )

		idx = self.mCtrlListPVS.getSelectedPosition( )
		iPVS = self.mPVSList[idx]

		if iPVS.mName :
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_DATE, '%s : %s'% ( E_STRING_DATE, iPVS.mDate ) )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_VERSION, '%s : %s'% ( E_STRING_VERSION, iPVS.mVersion ) )
			lblSize = ''
			if iPVS.mSize < 10000000 :
				lblSize = '%s Kb'% ( iPVS.mSize / 1000 )
			else :
				lblSize = '%s Mb'% ( iPVS.mSize / 1000000 )

			self.UpdateControlGUI( E_CONTROL_ID_LABEL_VERSION, '%s : %s'% ( E_STRING_SIZE, lblSize ) )
			self.UpdatePropertyGUI( 'DescriptionTitle', E_STRING_DESCRIPTION )
			self.UpdatePropertyGUI( 'UpdateDescription', iPVS.mDescription )

			lblDescTitle = ''
			if iPVS.mType == E_TYPE_PRISMCUBE :
				lblDescTitle = MR_LANG( 'System, OS, MBox Update' )
			elif iPVS.mType == E_TYPE_ADDONS :
				lblDescTitle = MR_LANG( 'Addon Application Update' )

			self.UpdateControlGUI( E_SETTING_DESCRIPTION, lblDescTitle )
				

	def InitPVSList( self ) :
		if self.mPVSList == None or len( self.mPVSList ) < 1 :
			self.mListItems = None
			self.mCtrlListPVS.reset( )
			label = MR_LANG( 'No one' )			
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_DATE, label )
			return 

		self.mListItems = []
		self.mCtrlListPVS.reset( )

		for idx in range( len( self.mPVSList ) ) :
			iPVS = self.mPVSList[idx]
			label2 = iPVS.mVersion
			if iPVS.mVersion == GetSTBVersion( ) :
				label2 = 'Updated'
				self.mPVSList[idx].mError = -1

			listItem = xbmcgui.ListItem( '%s'% iPVS.mName, '%s'% label2 )
			self.mListItems.append( listItem )

		self.UpdateControlGUI( E_CONTROL_ID_LIST_PVS, self.mListItems, E_TAG_ADD_ITEM )
		self.UpdateLabelPVSInfo( )


	def Provisioning( self ) :
		appURL = None
		self.mPVSList = []
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
				iPVS = PVSList( )
				iPVS.mName = MR_LANG( 'System Update' )
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

				self.mPVSList.append( iPVS )

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )

		self.GetAPPList( appURL )
		self.InitPVSList( )

		self.CloseBusyDialog( )

		if not download :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Can not connect address, retry to input URL' ) )
 			dialog.doModal( )


	def GetAPPList( self, aURL ) :
		pass
		#ToDO


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
			self.UpdateStepPage( E_UPDATE_STEP_PROVISION )

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


	def UpdateStepPage( self, aStep, aPVS = None ) :
		self.mStepPage = aStep
		stepResult = True

		self.OpenAnimation( )
		if aStep != E_UPDATE_STEP_HOME and self.mWin.getProperty( 'PVSShow' ) :
			#self.SetFocusControl( E_CONTROL_ID_LIST_PVS )
			self.DrawUpdateStep( aStep )


		if aStep == E_UPDATE_STEP_HOME :
			self.UpdatePropertyGUI( 'PVSShow', 'False' )
			self.ResetAllControl( )
			self.AddInputControl( E_Input01, MR_LANG( 'Firmware Update' ), '', MR_LANG( 'Download STB firmware, check network live' ) )
			self.AddInputControl( E_Input02, MR_LANG( 'Software Update' ), '', MR_LANG( 'Download Software or etc, check network live' ) )

			self.InitControl( )
			self.SetFocusControl( E_Input01 )

			if self.mEnableLocalThread and self.mCheckEthernetThread :
				self.mEnableLocalThread = False
				self.mCheckEthernetThread.join( )
			self.mEnableLocalThread = False

		elif aStep == E_UPDATE_STEP_PROVISION :
			self.ResetAllControl( )
			self.AddInputControl( E_Input01, MR_LANG( 'Update Check' ), '', MR_LANG( 'Check provisionning firmware from PrismCube Server, check network live' ) )
			self.AddInputControl( E_Input02, MR_LANG( '- Apply' ),      '', MR_LANG( 'Update now, Reboot and get update stb' ) )

			self.InitControl( )
			self.SetFocusControl( E_Input01 )
			self.SetEnableControl( E_Input02, False )

			
			self.mStepPage = E_UPDATE_STEP_PROVISION
			self.UpdatePropertyGUI( 'PVSShow', 'True' )
			self.SetFocusControl( E_CONTROL_ID_LIST_PVS )

			self.mEnableLocalThread = True
			self.mCheckEthernetThread = self.CheckEthernetThread( )

			self.Provisioning( )

		elif aStep == E_UPDATE_STEP_DOWNLOAD :
			if aPVS :
				stepResult = self.GetDownload( aPVS )
			else :
				stepResult = False

			if self.mEnableLocalThread and self.mCheckEthernetThread :
				self.mEnableLocalThread = False
				self.mCheckEthernetThread.join( )
			self.mEnableLocalThread = False

		elif aStep == E_UPDATE_STEP_CHECKFILE :
			if not aPVS :
				return False

			tempFile = E_DEFAULT_PATH_DOWNLOAD + '/%s'% os.path.basename( aPVS.mFileName )
			if os.stat( tempFile )[stat.ST_SIZE] != aPVS.mSize :
				return False

			self.OpenBusyDialog( )
			ret = CheckMD5Sum( tempFile, aPVS.mMd5 )
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
			if not aPVS :
				return False

			tempFile = E_DEFAULT_PATH_DOWNLOAD + '/%s'% os.path.basename( aPVS.mFileName )
			if os.stat( tempFile )[stat.ST_SIZE] != aPVS.mSize :
				return False

			self.OpenBusyDialog( )
			stepResult = CopyToUSB( tempFile, E_DEFAULT_PATH_USB_UPDATE )
			#ToDO : extract file verify ??? file list check-up
			self.CloseBusyDialog( )

			if not stepResult :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Check USB' ) )
				dialog.doModal( )


		elif aStep == E_UPDATE_STEP_VERIFY :
			pass

		elif aStep == E_UPDATE_STEP_FINISH :
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_PERCENT, MR_LANG( 'Update Ready!!' ) )
			RemoveDirectory( E_DEFAULT_PATH_DOWNLOAD )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Update Ready' ) )
			dialog.doModal( )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_PERCENT, '' )
			self.SetEnableControl( E_Input02, False )


		elif aStep == E_UPDATE_STEP_UPDATE_NOW :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Now reboot and follow from VFD' ) )
			dialog.doModal( )
			#ToDo : reboot

		elif aStep == E_UPDATE_STEP_CHECK_NETWORK :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Disconnected Network' ) )
			dialog.doModal( )
			if self.mEnableLocalThread and self.mCheckEthernetThread :
				self.mEnableLocalThread = False
				self.mCheckEthernetThread.join( )
			self.mEnableLocalThread = False


		return stepResult

		

	def UpdateHandler( self ) :
		LOG_TRACE('----------------list[%s]'% self.mPVSList )
		if self.mPVSList == None or len( self.mPVSList ) < 1 :
			return

		idx = self.mCtrlListPVS.getSelectedPosition( )
		iPVS = self.mPVSList[idx]
		LOG_TRACE('----------------download File[%s]'% iPVS.mFileName )

		if iPVS.mError != 0 :
			return

		self.UpdateControlGUI( E_CONTROL_ID_LABEL_PERCENT, MR_LANG( 'Downloading...' ) )
		if not self.UpdateStepPage( E_UPDATE_STEP_DOWNLOAD, iPVS ) :
			return

		self.UpdateControlGUI( E_CONTROL_ID_LABEL_PERCENT, MR_LANG( 'File Checking...' ) )
		if not self.UpdateStepPage( E_UPDATE_STEP_CHECKFILE, iPVS ) :
			return

		LOG_TRACE('----------------path down[%s] usb[%s]'% ( E_DEFAULT_PATH_DOWNLOAD, E_DEFAULT_PATH_USB_UPDATE ) )
		if not self.UpdateStepPage( E_UPDATE_STEP_CHECKUSB ) :
			return

		self.UpdateControlGUI( E_CONTROL_ID_LABEL_PERCENT, MR_LANG( 'Image Unpacking...' ) )
		if not self.UpdateStepPage( E_UPDATE_STEP_UNPACKING, iPVS ) :
			return

		#self.UpdateControlGUI( E_CONTROL_ID_LABEL_PERCENT, MR_LANG( 'Verify Checking...' ) )
		#if not self.UpdateStepPage( E_UPDATE_STEP_VERIFY, iPVS ) :
		#	return

		self.UpdateStepPage( E_UPDATE_STEP_FINISH )



	def GetDownload( self, aPVS ) :
		isStable = GetURLpage( aPVS.mFileName, False )

		if not isStable :
			return

		self.mWorkingItem = aPVS
		self.mWorkingDownloader = None

		#make tempDir, write local file
		CreateDirectory( E_DEFAULT_PATH_DOWNLOAD )

		isResume = False
		tempFile = E_DEFAULT_PATH_DOWNLOAD + '/%s'% os.path.basename( aPVS.mFileName )
		if os.path.exists( tempFile ) :
			if os.stat( tempFile )[stat.ST_SIZE] == aPVS.mSize :
				self.SetUpdate( tempFile, aPVS.mMd5 )
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
				LOG_TRACE('--------------abort')



