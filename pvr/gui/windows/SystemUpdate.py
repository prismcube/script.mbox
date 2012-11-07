from pvr.gui.WindowImport import *
from fileDownloader import DownloadFile
import stat

E_TYPE_PRISMCUBE = 1
E_TYPE_ADDONS = 2

E_CURRENT_INFO            = '/config/update.xml'
E_DOWNLOAD_INFO_PVS       = '/mnt/hdd0/program/download/update.xml'
E_DEFAULT_PATH_HDD        = '/mnt/hdd0/program'
E_DEFAULT_PATH_DOWNLOAD   = '%s/download'% E_DEFAULT_PATH_HDD
E_DEFAULT_PATH_USB_UPDATE = '/media/sdb1'
E_DEFAULT_URL_PVS         = 'http://update.prismcube.com/update/ruby/update.xml'

E_CONTROL_ID_GROUP_PVS      = 9000
E_CONTROL_ID_LABEL_VERSION  = 100
E_CONTROL_ID_LABEL_DATE     = 101
E_CONTROL_ID_LABEL_SIZE     = 102

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

UPDATE_STEP					= E_UPDATE_STEP_FINISH - E_UPDATE_STEP_PROVISION


E_STRING_ATTENTION     = 0
E_STRING_ERROR         = 1
E_STRING_CHECK_USB       = 0
E_STRING_CHECK_USB_SPACE = 1
E_STRING_CHECK_USB_NOT   = 2
E_STRING_CHECK_ADDRESS   = 3
E_STRING_CHECK_UPDATED   = 4
E_STRING_CHECK_CORRUPT   = 5
E_STRING_CHECK_VERIFY    = 6
E_STRING_CHECK_DISKFULL  = 7
E_STRING_CHECK_FINISH    = 8
E_STRING_CHECK_CONNECT_ERROR  = 9
E_STRING_CHECK_UNLINK_NETWORK = 10
E_STRING_CHECK_CHANNEL_FAIL   = 11

class PVSClass( object ) :
	def __init__( self ) :
		self.mName					= None
		self.mFileName				= None
		self.mDate					= None
		self.mDescription			= []
		self.mMd5					= None
		self.mSize					= 0
		self.mVersion				= None
		self.mId					= None
		self.mType					= None
		self.mError					= -1
		self.mProgress				= None
		self.mChannelUpdateProgress = None


class SystemUpdate( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )

		self.mPVSData = None
		self.mCurrData = None

	def onInit( self )  :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mCtrlLabelDescTitle      = self.getControl( E_SETTING_DESCRIPTION )
		self.mCtrlLabelDate           = self.getControl( E_CONTROL_ID_LABEL_DATE )
		self.mCtrlLabelVersion        = self.getControl( E_CONTROL_ID_LABEL_VERSION )
		self.mCtrlLabelSize           = self.getControl( E_CONTROL_ID_LABEL_SIZE )

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
		self.mShowProgressThread = None
		self.testButton = []

		self.SetSettingWindowLabel( MR_LANG( 'Update' ) )

		self.SetPipScreen( )
		self.LoadNoSignalState( )

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
				self.SetFocusControl( E_CONTROL_ID_GROUP_PVS )
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
			if self.mStepPage != E_UPDATE_STEP_HOME :
				self.ShowContextMenu( )


	def onClick( self, aControlId ) :
		groupId = self.GetGroupId( aControlId )
		if groupId == E_Input01 :
			if self.mStepPage == E_UPDATE_STEP_HOME :
				self.UpdateStepPage( E_UPDATE_STEP_READY )
			else :
				self.UpdateStepPage( E_UPDATE_STEP_PROVISION )

		elif groupId == E_Input02 :
			#LOG_TRACE('-----------------mStepPage[%s]'% self.mStepPage )
			if self.mStepPage == E_UPDATE_STEP_HOME :
				self.UpdateChannel( )

			elif self.mStepPage == E_UPDATE_STEP_UPDATE_NOW :
				self.UpdateStepPage( E_UPDATE_STEP_UPDATE_NOW )

			else :
				self.UpdateHandler( )
				if self.mStepPage < E_UPDATE_STEP_UPDATE_NOW :
					self.mStepPage = E_UPDATE_STEP_READY



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
				if status != 'down' :
					self.mLinkStatus = True
				else :
					self.mLinkStatus = False
					self.UpdateStepPage( E_UPDATE_STEP_ERROR_NETWORK )

			time.sleep(1)


	@RunThread
	def ShowProgressDialog( self, aLimitTime, aTitle, aEventName = None, aStep = None ) :
		self.mShowProgressThread = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_FORCE_PROGRESS )
		self.mShowProgressThread.SetDialogProperty( aLimitTime, aTitle, aEventName, aStep )
		self.mShowProgressThread.doModal( )


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


	def UpdatePropertyGUI( self, aPropertyID = None, aValue = None ) :
		#LOG_TRACE( 'Enter property[%s] value[%s]'% (aPropertyID, aValue) )
		if aPropertyID == None :
			return

		self.mWin.setProperty( aPropertyID, aValue )


	def ResetLabel( self, aControls = True ) :
		if aControls :
			self.SetEnableControl( E_Input02, False )

		self.UpdateControlGUI( E_CONTROL_ID_LABEL_DATE, '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_VERSION, '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_SIZE, '' )
		self.UpdatePropertyGUI( 'DescriptionTitle', '' )
		self.UpdatePropertyGUI( 'UpdateDescription', '' )


	def DialogPopup( self, aTitle, aMsg ) :
		title = ''
		line = ''

		if aTitle == E_STRING_ERROR :
			title = MR_LANG( 'Error' )
		elif aTitle == E_STRING_ATTENTION :
			title = MR_LANG( 'Attention' )
		else :
			title = aTitle

		if aMsg == E_STRING_CHECK_USB :
			line = MR_LANG( 'Check USB' )
		elif aMsg == E_STRING_CHECK_ADDRESS :
			line = MR_LANG( 'Can not connect address, Check Network or URL' )
		elif aMsg == E_STRING_CHECK_UPDATED :
			line = MR_LANG( 'Aready Updated' )
		elif aMsg == E_STRING_CHECK_CORRUPT :
			line = MR_LANG( 'File is corrupt, Try again download' )
		elif aMsg == E_STRING_CHECK_USB_NOT :
			line = MR_LANG( 'USB is not detected, Please insert USB' )
		elif aMsg == E_STRING_CHECK_VERIFY :
			line = MR_LANG( 'Verify Failed, try to download again' )
		elif aMsg == E_STRING_CHECK_FINISH :
			line = MR_LANG( 'Update Ready' )
		elif aMsg == E_STRING_CHECK_UNLINK_NETWORK :
			line = MR_LANG( 'Disconnected Network' )
		elif aMsg == E_STRING_CHECK_DISKFULL :
			line = MR_LANG( 'Disk is Full, Please remove Addons' )
		elif aMsg == E_STRING_CHECK_USB_SPACE :
			line = MR_LANG( 'Not enough space, Check USB' )
		elif aMsg == E_STRING_CHECK_CONNECT_ERROR :
			line = MR_LANG( 'Connect server error' )
		elif aMsg == E_STRING_CHECK_CHANNEL_FAIL :
			line = MR_LANG( 'Update process failed' )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( title, line )
		dialog.doModal( )


	def UpdateLabelPVSInfo( self ) :
		if self.mPVSData == None or self.mPVSData.mError != 0 :
			return

		self.ResetLabel( )

		iPVS = self.mPVSData
		if iPVS.mName :
			self.SetEnableControl( E_Input02, True )

			self.UpdateControlGUI( E_CONTROL_ID_LABEL_DATE,    '%s : %s'% ( MR_LANG( 'DATE' ), iPVS.mDate ) )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_VERSION, '%s : %s'% ( MR_LANG( 'VERSION' ), iPVS.mVersion ) )
			lblSize = ''
			if iPVS.mSize < 10000000 :
				lblSize = '%s Kb'% ( iPVS.mSize / 1000 )
			else :
				lblSize = '%s Mb'% ( iPVS.mSize / 1000000 )

			self.UpdateControlGUI( E_CONTROL_ID_LABEL_SIZE, '%s : %s'% ( MR_LANG( 'SIZE' ), lblSize ) )
			self.UpdatePropertyGUI( 'DescriptionTitle', MR_LANG( 'DESCRIPTION' ) )
			self.UpdatePropertyGUI( 'UpdateDescription', iPVS.mDescription )

			lblDescTitle = ''
			if iPVS.mType == E_TYPE_PRISMCUBE :
				lblDescTitle = MR_LANG( 'System, OS, MBox Update' )
			elif iPVS.mType == E_TYPE_ADDONS :
				lblDescTitle = MR_LANG( 'Addon Application Update' )

			self.UpdateControlGUI( E_SETTING_DESCRIPTION, lblDescTitle )
				

	def InitPVSData( self ) :
		if self.mPVSData == None or self.mPVSData.mError != 0 :
			#label = MR_LANG( 'No one' )			
			#self.UpdateControlGUI( E_CONTROL_ID_LABEL_DATE, label )
			self.SetEnableControl( E_Input02, False )
			self.SetControlLabel2String( E_Input02, MR_LANG( 'Not Checked') )
			self.EditDescription( E_Input02, MR_LANG( 'Click to download' ) )
			return 

		self.SetEnableControl( E_Input02, True )

		label2    = MR_LANG( 'Download' )
		descLabel = MR_LANG( 'Click to download' )
		if self.mCurrData and self.mCurrData.mError == 0 and self.mCurrData.mVersion == self.mPVSData.mVersion :
			label2    = MR_LANG( 'Updated' )
			descLabel = MR_LANG( 'Updated lastest' )
			self.mPVSData.mError = -1
			self.SetEnableControl( E_Input02, False )

		self.SetControlLabel2String( E_Input02, '%s'% label2 )
		self.EditDescription( E_Input02, descLabel )
		self.UpdateLabelPVSInfo( )


	def Provisioning( self ) :
		appURL = None
		self.mPVSData = None
		self.ResetLabel( )

		if not self.mUrlPVS :
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_ADDRESS )
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

		self.CloseBusyDialog( )
		self.InitPVSData( )

		if not download :
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_ADDRESS )

		elif self.mCurrData and self.mCurrData.mError == 0 and self.mCurrData.mVersion == self.mPVSData.mVersion :
			self.DialogPopup( MR_LANG( 'Latest version' ), E_STRING_CHECK_UPDATED )


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
			self.mPVSData = None
			self.ResetLabel( False )
			RemoveDirectory( E_DEFAULT_PATH_DOWNLOAD )
			self.UpdateStepPage( E_UPDATE_STEP_READY )

		elif aContextAction == CONTEXT_ACTION_CHANGE_ADDRESS :
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

		strStepNo = '%s/%s'% ( int( aStep ) - 1, UPDATE_STEP )
		if aStep == E_UPDATE_STEP_READY :
			self.OpenAnimation( )
			self.SetFocusControl( E_CONTROL_ID_GROUP_PVS )
			LOG_TRACE('------------------updateStep[%s]'% strStepNo )

		elif aStep > E_UPDATE_STEP_READY :
			self.SetFocusControl( E_CONTROL_ID_GROUP_PVS )
			LOG_TRACE('------------------updateStep[%s]'% strStepNo )


		if aStep == E_UPDATE_STEP_HOME :
			self.ResetAllControl( )
			self.AddInputControl( E_Input01, MR_LANG( 'Firmware Update' ), '', MR_LANG( 'Download STB firmware, check network live' ) )
			self.AddInputControl( E_Input02, MR_LANG( 'Channel Update' ), '', MR_LANG( 'ChannelList update' ) )

			self.SetEnableControl( E_Input01, True )
			self.SetEnableControl( E_Input02, True )

			self.InitControl( )
			self.SetFocusControl( E_Input01 )

			if self.mEnableLocalThread and self.mCheckEthernetThread :
				self.mEnableLocalThread = False
				self.mCheckEthernetThread.join( )
				self.mCheckEthernetThread = None
			self.mEnableLocalThread = False

			self.mPVSData = None
			self.ResetLabel( False )
			self.UpdatePropertyGUI( 'CurrentDescription', '' )
			self.UpdatePropertyGUI( 'UpdateStep', 'False' )

		elif aStep == E_UPDATE_STEP_READY :
			self.ResetAllControl( )
			self.AddInputControl( E_Input01, MR_LANG( 'Update Check' ), '', MR_LANG( 'Check provisionning firmware from PrismCube Server, check network live' ) )
			self.AddInputControl( E_Input02, MR_LANG( 'Firmware' ), MR_LANG( 'Not Checked' ), MR_LANG( 'Click to download' ) )
			self.SetEnableControl( E_Input02, False )

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

			self.ShowProgressDialog( 30, MR_LANG( 'File Checking...' ), None, strStepNo )
			self.OpenBusyDialog( )
			ret = CheckMD5Sum( tempFile, self.mPVSData.mMd5 )
			self.CloseBusyDialog( )
			if self.mShowProgressThread :
				self.mShowProgressThread.SetResult( True )
				self.mShowProgressThread = None
			time.sleep( 1 )

			if not ret :
				self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_CORRUPT )
				stepResult = False


		elif aStep == E_UPDATE_STEP_CHECKUSB :
			#if not CheckDirectory( E_DEFAULT_PATH_USB_UPDATE ) :
			if not self.mDataCache.USB_GetMountPath( ) :
				self.DialogPopup( E_STRING_ATTENTION, E_STRING_CHECK_USB_NOT )
				stepResult = False

		elif aStep == E_UPDATE_STEP_UNPACKING :
			if self.mPVSData == None or self.mPVSData.mError != 0 :
				return False

			tempFile = E_DEFAULT_PATH_DOWNLOAD + '/%s'% os.path.basename( self.mPVSData.mFileName )
			if os.stat( tempFile )[stat.ST_SIZE] != self.mPVSData.mSize :
				return False

			usbPath = self.mDataCache.USB_GetMountPath( )
			if usbPath :
				time.sleep( 0.3 )
				self.ShowProgressDialog( 60, MR_LANG( 'Unpacking...' ), None, strStepNo )
				self.OpenBusyDialog( )
				stepResult = UnpackToUSB( tempFile, usbPath )
				self.CloseBusyDialog( )
				if self.mShowProgressThread :
					self.mShowProgressThread.SetResult( True )
					self.mShowProgressThread = None
				time.sleep( 1 )

			else :
				stepResult = False

			if not stepResult :
				self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_USB )


		elif aStep == E_UPDATE_STEP_VERIFY :
			tempFile = E_DEFAULT_PATH_DOWNLOAD + '/%s'% os.path.basename( self.mPVSData.mFileName )
			if not self.VerifiedUnPack( tempFile ) :
				self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_VERIFY )
				stepResult = False

		elif aStep == E_UPDATE_STEP_FINISH :
			time.sleep( 0.3 )
			#self.DialogPopup( E_STRING_ATTENTION, E_STRING_CHECK_FINISH )

		elif aStep == E_UPDATE_STEP_UPDATE_NOW :
			time.sleep( 0.3 )
			self.SetControlLabel2String( E_Input02, MR_LANG( 'Update Now') )
			self.EditDescription( E_Input02, MR_LANG( 'Reboot and Update, No eject USB' ) )

			line1 = MR_LANG( 'Now reboot and follow from VFD' )
			line2 = MR_LANG( 'Are you sure ?' )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Attention' ), '%s\n%s'% ( line1, line2 ) )
			dialog.doModal( )
			ret = dialog.IsOK( )
			if ret == E_DIALOG_STATE_YES :
				CopyToFile( E_DOWNLOAD_INFO_PVS, E_CURRENT_INFO )
				RemoveDirectory( E_DEFAULT_PATH_DOWNLOAD )
				RemoveDirectory( os.path.dirname( E_DOWNLOAD_INFO_PVS ) )
				self.OpenBusyDialog( )
				self.mDataCache.System_Reboot( )


		elif aStep == E_UPDATE_STEP_ERROR_NETWORK :
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_UNLINK_NETWORK )
			if self.mEnableLocalThread and self.mCheckEthernetThread :
				self.mEnableLocalThread = False
				self.mCheckEthernetThread.join( )
				self.mCheckEthernetThread = None
			self.mEnableLocalThread = False

		return stepResult

		
	def UpdateHandler( self ) :
		#LOG_TRACE('----------------pvs[%s]'% self.mPVSData )
		if self.mPVSData == None or self.mPVSData.mError != 0 :
			return

		#LOG_TRACE('----------------download File[%s]'% self.mPVSData.mFileName )
		if not self.UpdateStepPage( E_UPDATE_STEP_DOWNLOAD ) :
			return

		if not self.UpdateStepPage( E_UPDATE_STEP_CHECKFILE ) :
			return

		#LOG_TRACE('----------------path down[%s] usb[%s]'% ( E_DEFAULT_PATH_DOWNLOAD, E_DEFAULT_PATH_USB_UPDATE ) )
		if not self.UpdateStepPage( E_UPDATE_STEP_CHECKUSB ) :
			return

		tempFile = E_DEFAULT_PATH_DOWNLOAD + '/%s'% os.path.basename( self.mPVSData.mFileName )
		if not self.VerifiedUnPack( tempFile, False ) :
			if not self.UpdateStepPage( E_UPDATE_STEP_UNPACKING ) :
				return

		if not self.UpdateStepPage( E_UPDATE_STEP_VERIFY ) :
			return


		#self.UpdateStepPage( E_UPDATE_STEP_FINISH )
		self.UpdateStepPage( E_UPDATE_STEP_UPDATE_NOW )


	def CheckInitDevice( self ) :
		sizeCheck = True

		if CheckHdd( ) :
			LOG_TRACE( 'Check HDD True' )
			if GetDeviceSize( E_DEFAULT_PATH_HDD ) < self.mPVSData.mSize :
				self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_DISKFULL )
				sizeCheck = False

			return sizeCheck

		LOG_TRACE( 'Not Exist HDD' )
		usbPath = self.mDataCache.USB_GetMountPath( )
		if not usbPath :
			LOG_TRACE( 'Not Exist USB' )
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_USB_NOT )
			return False


		global E_DEFAULT_PATH_DOWNLOAD
		E_DEFAULT_PATH_DOWNLOAD = '%s/stb/download'% usbPath

		usbSize = GetDeviceSize( usbPath )
		if usbSize <= self.mPVSData.mSize :
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_USB_SPACE )
			sizeCheck = False

		LOG_TRACE( 'usbSize[%s] downSize[%s] usbPath[%s]'% ( usbSize, self.mPVSData.mSize, usbPath ) )
		return sizeCheck



	#make tempDir, write local file
	def GetDownload( self, aPVS ) :
		isExist = GetURLpage( aPVS.mFileName, False )

		if not isExist :
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_ADDRESS )
			return False

		self.mWorkingItem = aPVS
		self.mWorkingDownloader = None


		#check device, size free, change path for hdd or usb 
		if not self.CheckInitDevice( ) :
			return False

		LOG_TRACE( 'download path[%s]'% E_DEFAULT_PATH_DOWNLOAD )
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
		time.sleep( 0.3 )

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


	def VerifiedUnPack( self, aZipFile, aShowProgress = True ) :
		fileList = GetUnpackFiles( aZipFile )
		if not fileList :
			return False

		usbPath = self.mDataCache.USB_GetMountPath( )
		if not usbPath :
			return False

		self.OpenBusyDialog( )
		if aShowProgress :
			dialogProgress = xbmcgui.DialogProgress( )
			dialogProgress.create( self.mPVSData.mName, MR_LANG( 'Verifying...' ) )

		isVerify = True
		totalFiles = len( fileList )
		idx = 0
		for item in fileList :
			idx += 1
			if aShowProgress :
				dialogProgress.update( 1.0 * idx / totalFiles * 100 )
			unpackFile = '%s/%s'% ( usbPath, item[1] )
			unpackSize = GetFileSize( unpackFile )
			if item[0] != unpackSize :
				LOG_TRACE( '--------------verify err pack[%s] unPack[%s] file[%s]'% ( item[0], unpackSize, unpackFile ) )
				isVerify = False
				break

			if aShowProgress and dialogProgress.iscanceled( ) :
				LOG_TRACE( '--------------abort' )
				isVerify = False
				break

			time.sleep( 0.2 )

		if aShowProgress :
			dialogProgress.close( )

		self.CloseBusyDialog( )
		time.sleep( 0.3 )

		return isVerify


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

			lbldesc += '%s : %s\n'% ( MR_LANG( 'VERSION' ), iPVS.mVersion )
			lbldesc += '%s : %s\n'% ( MR_LANG( 'DATE' ), iPVS.mDate )
			#lbldesc += '%s\n%s\n'% ( MR_LANG( 'DESCRIPTION' ), iPVS.mDescription )

			self.mCurrData = iPVS

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )
			lbldesc = MR_LANG( 'Unknown version' )

		self.UpdatePropertyGUI( 'CurrentDescription', lbldesc )


	def UpdateChannel( self ) :
		kb = xbmc.Keyboard( PRISMCUBE_SERVER, MR_LANG( 'Enter server address' ), False )			
		kb.setHiddenInput( False )
		kb.doModal( )
		if kb.isConfirmed( ) :
			updatelist = self.GetServerInfo( kb.getText( ) )
			LOG_TRACE( 'updatelist = %s' % updatelist )
			showtext = []
			if updatelist :
				for text in updatelist :
					showtext.append( text[0] )
				LOG_TRACE( 'showtext = %s' % showtext )

				dialog = xbmcgui.Dialog( )
				ret = dialog.select( MR_LANG( 'Select Package' ), showtext )
				if ret >= 0 :
					result = self.GetChannelUpdate( kb.getText( ), updatelist[ret][1] )
					if result == False :
						self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_CHANNEL_FAIL )

			else :
				self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_CONNECT_ERROR )


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
		self.mChannelUpdateProgress = self.ChannelUpdateProgress( MR_LANG( 'Now updating...' ), 20 )
		ret = self.DownloadxmlFile( aAddress, aPath )
		if ret :
			self.mCommander.System_SetManualChannelList( '/tmp/defaultchannel.xml' )
			self.mCommander.System_SetDefaultChannelList( )
			self.mDataCache.LoadAllSatellite( )
			self.mTunerMgr.SyncChannelBySatellite( )
			self.mDataCache.Channel_ReLoad( )
			self.mDataCache.Player_AVBlank( False )
			self.CloseProgress( )
			return True
		else :
			self.CloseProgress( )
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
	def ChannelUpdateProgress( self, aString, aTime ) :
		self.mProgress = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_FORCE_PROGRESS )
		self.mProgress.SetDialogProperty( aTime, aString )
		self.mProgress.doModal( )


	def CloseProgress( self ) :
		self.mProgress.SetResult( True )
		self.mChannelUpdateProgress.join( )

