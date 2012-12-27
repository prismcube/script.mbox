from pvr.gui.WindowImport import *
from fileDownloader import DownloadFile
from version import LooseVersion
from copy import deepcopy
import stat

E_TYPE_PRISMCUBE = 1
E_TYPE_ADDONS = 2

E_CURRENT_INFO            = '/etc/release.info'
E_DOWNLOAD_INFO_PVS       = '/mnt/hdd0/program/download/update.xml'
E_DEFAULT_PATH_HDD        = '/mnt/hdd0/program'
E_DEFAULT_PATH_DOWNLOAD   = '%s/download'% E_DEFAULT_PATH_HDD
E_DEFAULT_PATH_USB_UPDATE = '/media/sdb1'
E_DEFAULT_URL_PVS         = 'http://update.prismcube.com/update.html?product=ruby'
E_DEFAULT_URL_REQUEST_FW  = 'http://update.prismcube.com/download.html?key='

E_DEFAULT_CHANNEL_LIST		= 'http://update.prismcube.com/channel.html'

E_CONTROL_ID_GROUP_PVS      = 9000
E_CONTROL_ID_LABEL_TITLE    = 99
E_CONTROL_ID_LABEL_VERSION  = 100
E_CONTROL_ID_LABEL_DATE     = 101
E_CONTROL_ID_LABEL_SIZE     = 102

CONTEXT_ACTION_REFRESH_CONNECT      = 1
CONTEXT_ACTION_LOAD_OLD_VERSION     = 2

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
E_STRING_CHECK_NOT_OLDVERSION = 12
E_STRING_CHECK_FAILED    = 13
E_STRING_CHECK_HAVE_NONE = 14

class PVSClass( object ) :
	def __init__( self ) :
		self.mKey					= None
		self.mName					= None
		self.mFileName				= None
		self.mDate					= None
		self.mDescription			= []
		self.mMd5					= None
		self.mSize					= 0		#zipSize
		self.mUnpackSize			= 0		#fullSize
		self.mVersion				= 0
		self.mId					= None
		self.mType					= None
		self.mError					= -1


class SystemUpdate( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )

		self.mPVSData               = None
		self.mCurrData              = None
		self.mProgress				= None
		self.mChannelUpdateProgress = None

	def onInit( self )  :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.mCtrlLabelDescTitle      = self.getControl( E_SETTING_DESCRIPTION )
		self.mCtrlLabelTitle          = self.getControl( E_CONTROL_ID_LABEL_TITLE )
		self.mCtrlLabelDate           = self.getControl( E_CONTROL_ID_LABEL_DATE )
		self.mCtrlLabelVersion        = self.getControl( E_CONTROL_ID_LABEL_VERSION )
		self.mCtrlLabelSize           = self.getControl( E_CONTROL_ID_LABEL_SIZE )

		#parse settings.xml
		self.mPVSData = None
		self.mCurrData = None
		self.mPVSList = []
		self.mIndexLastVersion = 0
		self.mEnableLocalThread = False
		self.mLinkStatus = False
		self.mIsDownload = True
		self.mStepPage = E_UPDATE_STEP_HOME
		self.mCheckEthernetThread = None
		self.mShowProgressThread = None

		self.SetSettingWindowLabel( MR_LANG( 'Update' ) )

		self.SetPipScreen( )
		self.LoadNoSignalState( )

		self.UpdateStepPage( E_UPDATE_STEP_HOME )
		self.mInitialized = True


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

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
		self.SetVideoRestore( )
		WinMgr.GetInstance( ).CloseWindow( )


	@RunThread
	def CheckEthernetThread( self ) :
		count = 0
		while self.mEnableLocalThread :
			if ( count % 20 ) == 0 :
				if self.mStepPage >= E_UPDATE_STEP_PROVISION and self.mStepPage <= E_UPDATE_STEP_DOWNLOAD :
					status = CheckEthernet( 'eth0' )
					if status != 'down' :
						self.mLinkStatus = True
					else :
						self.mLinkStatus = False
						self.UpdateStepPage( E_UPDATE_STEP_ERROR_NETWORK )

			time.sleep( 0.05 )
			count = count + 1


	@RunThread
	def ShowProgressDialog( self, aLimitTime, aTitle, aEventName = None, aStep = None ) :
		self.mShowProgressThread = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_FORCE_PROGRESS )
		self.mShowProgressThread.SetDialogProperty( aLimitTime, aTitle, aEventName, aStep )
		self.mShowProgressThread.doModal( )


	def UpdateControlGUI( self, aCtrlID = None, aValue = None, aExtra = None ) :
		#LOG_TRACE( 'Enter control[%s] value[%s]'% (aCtrlID, aValue) )

		if aCtrlID == E_CONTROL_ID_LABEL_TITLE :
			self.mCtrlLabelTitle.setLabel( aValue )

		elif aCtrlID == E_CONTROL_ID_LABEL_DATE :
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

		self.UpdateControlGUI( E_CONTROL_ID_LABEL_TITLE, '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_DATE, '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_VERSION, '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_SIZE, '' )
		self.UpdatePropertyGUI( 'DescriptionTitle', '' )
		self.UpdatePropertyGUI( 'UpdateDescription', '' )
		self.UpdatePropertyGUI( 'VersionInfo', E_TAG_FALSE )


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
			line = MR_LANG( 'Check your USB device' )
		elif aMsg == E_STRING_CHECK_ADDRESS :
			line = MR_LANG( 'Cannot connect to server' )
		elif aMsg == E_STRING_CHECK_UPDATED :
			line = MR_LANG( 'Already updated to the latest version' )
		elif aMsg == E_STRING_CHECK_CORRUPT :
			line = MR_LANG( 'File is corrupted, try downloading it again' )
		elif aMsg == E_STRING_CHECK_USB_NOT :
			line = MR_LANG( 'Please insert a USB flash drive and press OK' )
		elif aMsg == E_STRING_CHECK_VERIFY :
			line = MR_LANG( 'File verification failed, try downloading it again' )
		elif aMsg == E_STRING_CHECK_FINISH :
			line = MR_LANG( 'Ready to update' )
		elif aMsg == E_STRING_CHECK_UNLINK_NETWORK :
			line = MR_LANG( 'Network is disconnected' )
		elif aMsg == E_STRING_CHECK_DISKFULL :
			line = MR_LANG( 'Insufficient disk space' )
		elif aMsg == E_STRING_CHECK_USB_SPACE :
			line = MR_LANG( 'Not enough space on USB flash drive' )
		elif aMsg == E_STRING_CHECK_CONNECT_ERROR :
			line = MR_LANG( 'Cannot connect to server' )
		elif aMsg == E_STRING_CHECK_CHANNEL_FAIL :
			line = MR_LANG( 'Update process failed' )
		elif aMsg == E_STRING_CHECK_NOT_OLDVERSION :
			line = MR_LANG( 'Cannot find previous versions' )
		elif aMsg == E_STRING_CHECK_FAILED :
			line = MR_LANG( 'Cannot get the latest firmware, please try again' )
		elif aMsg == E_STRING_CHECK_HAVE_NONE :
			line = MR_LANG( 'No released firmware available' )

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

			self.UpdateControlGUI( E_CONTROL_ID_LABEL_TITLE,   MR_LANG( 'Firmware Information' ) )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_DATE,    '%s : %s'% ( MR_LANG( 'Date' ), iPVS.mDate ) )
			self.UpdateControlGUI( E_CONTROL_ID_LABEL_VERSION, '%s : %s'% ( MR_LANG( 'Version' ), iPVS.mVersion ) )
			lblSize = ''
			if iPVS.mSize < 10000000 :
				lblSize = '%s KB'% ( iPVS.mSize / 1000 )
			else :
				lblSize = '%s MB'% ( iPVS.mSize / 1000000 )

			self.UpdateControlGUI( E_CONTROL_ID_LABEL_SIZE, '%s : %s'% ( MR_LANG( 'Size' ), lblSize ) )
			self.UpdatePropertyGUI( 'DescriptionTitle', MR_LANG( 'Description' ) )
			self.UpdatePropertyGUI( 'UpdateDescription', iPVS.mDescription )
			self.UpdatePropertyGUI( 'VersionInfo', E_TAG_TRUE )

			"""
			lblDescTitle = ''
			if iPVS.mType == E_TYPE_PRISMCUBE :
				lblDescTitle = MR_LANG( 'Checking Last Update' )
			elif iPVS.mType == E_TYPE_ADDONS :
				lblDescTitle = MR_LANG( 'Addon Application Update' )

			self.UpdateControlGUI( E_SETTING_DESCRIPTION, lblDescTitle )
			"""


	def InitPVSData( self ) :
		isInit = True
		if not self.mPVSData or self.mPVSData.mError != 0 :
			self.SetEnableControl( E_Input02, False )
			self.SetControlLabel2String( E_Input02, MR_LANG( 'Not attempted') )
			self.EditDescription( E_Input02, MR_LANG( 'Please check firmware version first' ) )
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_FAILED )
			return False

		self.SetEnableControl( E_Input02, True )

		label2    = MR_LANG( 'Download' )
		descLabel = MR_LANG( 'Press OK button to download the firmware shown below' )
		if self.mCurrData and self.mCurrData.mError == 0 and self.mCurrData.mVersion == self.mPVSData.mVersion :
			label2    = MR_LANG( 'Your system is up-to-date' )
			descLabel = MR_LANG( 'Already updated to the latest version' )
			self.mPVSData.mError = -1
			self.SetEnableControl( E_Input02, False )
			self.SetFocusControl( E_Input01 )
			self.ResetLabel( )
			isInit = False

		self.SetControlLabel2String( E_Input02, '%s'% label2 )
		self.EditDescription( E_Input02, descLabel )
		self.UpdateLabelPVSInfo( )

		return isInit


	def GetParseVersion( self, aVersion = None ) :
		versions = ''
		count = 0
		for num in aVersion.split('.') :
			if count == 3 :
				versions += '.'
			versions += num
			count += 1

		return versions


	def Provisioning( self ) :
		appURL = None
		isDownload = False
		self.mPVSData = None
		self.mPVSList = []
		self.ResetLabel( )

		self.OpenBusyDialog( )
		#try :
		CreateDirectory( E_DEFAULT_PATH_DOWNLOAD )
		isDownload = GetURLpage( E_DEFAULT_URL_PVS, E_DOWNLOAD_INFO_PVS )
		#LOG_TRACE( '[pvs]%s'% isDownload )

		if isDownload :
			mPVSList = []
			tagNames = ['key', 'filename', 'date', 'version', 'zipsize', 'size', 'md5', 'description']
			retList = ParseStringInXML( E_DOWNLOAD_INFO_PVS, tagNames )
			if retList and len( retList ) > 0 :
				for pvsData in retList :
					iPVS = PVSClass( )
					if pvsData[0] :
						iPVS.mKey      = pvsData[0]
					if pvsData[1] :
						iPVS.mFileName = pvsData[1]
					if pvsData[2] :
						iPVS.mDate     = pvsData[2]
					if pvsData[3] :
						iPVS.mVersion  = pvsData[3]
						#iPVS.mVersion  = self.GetParseVersion( pvsData[3] )
					if pvsData[4] :
						iPVS.mSize     = int( pvsData[4] )
					if pvsData[5] :
						iPVS.mUnpackSize = int( pvsData[5] )
					if pvsData[6] :
						iPVS.mMd5      = pvsData[6]
					if pvsData[7] :
						description = ''
						for item in pvsData[7] :
							description += '%s\n'% item
						iPVS.mDescription = description

					iPVS.mName = MR_LANG( 'Downloading firmware' )
					iPVS.mType = E_TYPE_ADDONS
					iPVS.mError = 0
					mPVSList.append( iPVS )

				#Check Lastest version
				if mPVSList and len( mPVSList ) > 0 :
					#self.mPVSList = sorted( mPVSList, key=lambda pvslist: pvslist.mVersion, reverse=True )
					self.mPVSList = sorted( mPVSList, key=lambda pvslist: LooseVersion(pvslist.mVersion), reverse=True )

					self.mPVSData = deepcopy( self.mPVSList[0] )
					self.mPVSData.mType = E_TYPE_PRISMCUBE

					#self.mPVSList.pop( 0 )

			else :
				self.mPVSData = deepcopy( self.mCurrData )

		"""
		except Exception, e :
			LOG_ERR( 'except[%s]'% e )
			self.mPVSData = None
			self.mPVSList = []
			isDownload = False
		"""

		self.CloseBusyDialog( )

		if not isDownload :
			self.SetEnableControl( E_Input02, False )
			self.SetControlLabel2String( E_Input02, MR_LANG( 'Not attempted') )
			self.EditDescription( E_Input02, MR_LANG( 'Please check firmware version first' ) )
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_ADDRESS )
			return


		self.InitPVSData( )

		if self.mPVSList and len( self.mPVSList ) > 0 :
			if self.mCurrData and self.mCurrData.mError == 0 and \
			   self.mPVSData and self.mPVSData.mError == 0 and \
			   self.mCurrData.mVersion == self.mPVSData.mVersion :
				self.DialogPopup( MR_LANG( 'Firmware Version' ), E_STRING_CHECK_UPDATED )

		else :
			self.DialogPopup( MR_LANG( 'Firmware Update' ), E_STRING_CHECK_HAVE_NONE )

		self.ControlDown( )


	def ShowContextMenu( self ) :
		context = []
		context.append( ContextItem( MR_LANG( 'Refresh firmware update' ), CONTEXT_ACTION_REFRESH_CONNECT ) )
		if os.path.isfile( E_DOWNLOAD_INFO_PVS ) :
			context.append( ContextItem( MR_LANG( 'Get previous versions' ), CONTEXT_ACTION_LOAD_OLD_VERSION ) )

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
			try :
				RemoveDirectory( E_DEFAULT_PATH_DOWNLOAD )
				usbPath = self.mDataCache.USB_GetMountPath( )
				if usbPath :
					RemoveDirectory( '%s/update'% usbPath )
			except Exception, e :
				LOG_ERR( 'except[%s]'% e )

			self.UpdateStepPage( E_UPDATE_STEP_READY )

		elif aContextAction == CONTEXT_ACTION_LOAD_OLD_VERSION :
			self.ShowOldVersion( )


	def ShowOldVersion( self ) :
		if self.mPVSList and len( self.mPVSList ) > 0 :

			verList = []
			idx = -1
			self.mIndexLastVersion = 0
			for item in self.mPVSList :
				idx  += 1
				label = 'V%s  %s'% ( item.mVersion, item.mDate )

				if self.mCurrData and self.mCurrData.mError == 0 and \
				   self.mCurrData.mVersion == self.mPVSList[idx].mVersion :
					self.mIndexLastVersion = idx
					label = '[COLOR grey3]V%s  %s[/COLOR]'% ( item.mVersion, item.mDate )

				verList.append( label )

			dialog = xbmcgui.Dialog( )
			select =  dialog.select( MR_LANG( 'Previous firmware versions' ), verList, False, self.mIndexLastVersion )

			if select < 0 :
				return

			self.mPVSData = None
			self.mPVSData = deepcopy( self.mPVSList[select] )
			if select == 0 : #lastest version
				self.mPVSData.mType = E_TYPE_PRISMCUBE

			ret = self.InitPVSData( )
			self.mStepPage = E_UPDATE_STEP_READY
			usbPath = self.mDataCache.USB_GetMountPath( )
			if ret and usbPath :
				RemoveDirectory( '%s/update'% usbPath )
				self.SetFocusControl( E_Input02 )

		else :
			self.DialogPopup( E_STRING_ATTENTION, E_STRING_CHECK_NOT_OLDVERSION )


	def UpdateStepPage( self, aStep ) :
		self.mStepPage = aStep
		stepResult = True

		strStepNo = '%s/%s'% ( int( aStep ) - 1, UPDATE_STEP )
		if aStep == E_UPDATE_STEP_READY :
			self.OpenAnimation( )
			self.SetFocusControl( E_CONTROL_ID_GROUP_PVS )
			#LOG_TRACE('------------------updateStep[%s]'% strStepNo )

		elif aStep > E_UPDATE_STEP_READY :
			self.SetFocusControl( E_CONTROL_ID_GROUP_PVS )
			#LOG_TRACE('------------------updateStep[%s]'% strStepNo )


		if aStep == E_UPDATE_STEP_HOME :
			self.SetSettingWindowLabel( MR_LANG( 'Update' ) )
			self.ResetAllControl( )
			self.AddInputControl( E_Input01, MR_LANG( 'Update Firmware' ), '', MR_LANG( 'Download the latest firmware for your PRISMCUBE RUBY' ) )
			self.AddInputControl( E_Input02, MR_LANG( 'Update Channel List' ), '',  MR_LANG( 'Download a pre-configured channel list over the internet' ) )

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
			self.UpdatePropertyGUI( 'ShowInfoLabel', E_TAG_FALSE )

		elif aStep == E_UPDATE_STEP_READY :
			self.SetSettingWindowLabel( MR_LANG( 'Update Firmware' ) )
			self.ResetAllControl( )
			self.AddInputControl( E_Input01, MR_LANG( 'Check Firmware Version' ), '', MR_LANG( 'Check the latest firmware released on the update server' ) ) 
			self.AddInputControl( E_Input02, '', MR_LANG( 'Not attempted' ), MR_LANG( 'Please check firmware version first' ) )
			self.SetEnableControl( E_Input02, False )

			self.InitControl( )
			self.SetFocusControl( E_Input01 )
			self.UpdatePropertyGUI( 'ShowInfoLabel', E_TAG_TRUE )

			self.CheckCurrentVersion( )

		elif aStep == E_UPDATE_STEP_PROVISION :
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
				#self.mCheckEthernetThread.join( )
				self.mCheckEthernetThread = None
			self.mEnableLocalThread = False

		elif aStep == E_UPDATE_STEP_CHECKFILE :
			if self.mPVSData == None or self.mPVSData.mError != 0 :
				return False

			tempFile = '%s/%s'% ( E_DEFAULT_PATH_DOWNLOAD, self.mPVSData.mFileName )
			if os.stat( tempFile )[stat.ST_SIZE] != self.mPVSData.mSize :
				return False

			self.ShowProgressDialog( 30, MR_LANG( 'Checking files checksum...' ), None, strStepNo )
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

			tempFile = '%s/%s'% ( E_DEFAULT_PATH_DOWNLOAD, self.mPVSData.mFileName )
			if os.stat( tempFile )[stat.ST_SIZE] != self.mPVSData.mSize :
				return False

			usbPath = self.mDataCache.USB_GetMountPath( )
			if usbPath :
				time.sleep( 0.3 )
				self.ShowProgressDialog( 60, MR_LANG( 'Copying files to USB drive...' ), None, strStepNo )
				self.OpenBusyDialog( )
				stepResult = UnpackToUSB( tempFile, usbPath, self.mPVSData.mUnpackSize )
				self.CloseBusyDialog( )
				if self.mShowProgressThread :
					self.mShowProgressThread.SetResult( True )
					self.mShowProgressThread = None
				time.sleep( 1 )

			else :
				stepResult = False

			if stepResult != True :
				if stepResult == -1 :
					self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_USB_SPACE )
				else :
					self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_USB )

				stepResult = False


		elif aStep == E_UPDATE_STEP_VERIFY :
			tempFile = '%s/%s'% ( E_DEFAULT_PATH_DOWNLOAD, self.mPVSData.mFileName )
			if not self.VerifiedUnPack( tempFile ) :
				self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_VERIFY )
				stepResult = False

		elif aStep == E_UPDATE_STEP_FINISH :
			time.sleep( 0.3 )
			#self.DialogPopup( E_STRING_ATTENTION, E_STRING_CHECK_FINISH )

		elif aStep == E_UPDATE_STEP_UPDATE_NOW :
			time.sleep( 0.3 )
			self.SetControlLabel2String( E_Input02, MR_LANG( 'Update' ) )
			self.EditDescription( E_Input02, MR_LANG( 'Follow the instructions on front panel display during the updating process' ) )

			line1 = MR_LANG( 'DO NOT REMOVE YOUR USB DURING THE UPGRADING' )
			line2 = MR_LANG( 'PRESS YES TO REBOOT SYSTEM NOW' )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'WARNING' ), '%s\n%s'% ( line1, line2 ) )
			dialog.doModal( )
			ret = dialog.IsOK( )
			if ret == E_DIALOG_STATE_YES :
				self.CheckItems( )
				RemoveDirectory( E_DEFAULT_PATH_DOWNLOAD )
				RemoveDirectory( os.path.dirname( E_DOWNLOAD_INFO_PVS ) )
				self.OpenBusyDialog( )
				self.mDataCache.System_Reboot( )


		elif aStep == E_UPDATE_STEP_ERROR_NETWORK :
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_UNLINK_NETWORK )
			if self.mEnableLocalThread and self.mCheckEthernetThread :
				self.mEnableLocalThread = False
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

		tempFile = '%s/%s'% ( E_DEFAULT_PATH_DOWNLOAD, self.mPVSData.mFileName )
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
		if usbSize <= ( self.mPVSData.mSize + self.mPVSData.mUnpackSize ) :
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_USB_SPACE )
			sizeCheck = False

		LOG_TRACE( 'usbSize[%s] downSize[%s] unzip[%s] usbPath[%s]'% ( usbSize, self.mPVSData.mSize, self.mPVSData.mUnpackSize, usbPath ) )
		return sizeCheck


	#make tempDir, write local file
	def GetDownload( self, aPVS ) :
		request = '%s%s'% ( E_DEFAULT_URL_REQUEST_FW, aPVS.mKey )
		isExist = GetURLpage( request, '/tmp/fwUrl' )
		#LOG_TRACE('-------------request[%s] ret[%s]'% ( request, isExist ) )

		if isExist == False :
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_HAVE_NONE )
			return False

		tagNames = ['url']
		retList = ParseStringInXML( '/tmp/fwUrl', tagNames, 'urlinfo' )
		#LOG_TRACE('------------ret urlinfo[%s]'% retList )
		if retList and len( retList ) > 0 :
			reqFile = retList[0][0]

		else :
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_HAVE_NONE )
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
		tempFile = '%s/%s'% ( E_DEFAULT_PATH_DOWNLOAD, aPVS.mFileName )
		if os.path.exists( tempFile ) :
			if os.stat( tempFile )[stat.ST_SIZE] == aPVS.mSize :
				return True

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Resume downloads' ), MR_LANG( 'Continue broken or interrupted downloads?' ) )
			dialog.doModal( )

			ret = dialog.IsOK( )
			if ret == E_DIALOG_STATE_CANCEL :
				return False

			elif ret == E_DIALOG_STATE_YES :
				isResume = True

		self.mDialogProgress = xbmcgui.DialogProgress( )
		self.mDialogProgress.create( aPVS.mName, MR_LANG( 'Waiting...' ) )

		LOG_TRACE( '--------------reqFile[%s]'% reqFile )

		self.mWorkingDownloader = DownloadFile( reqFile, tempFile )
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


	def CheckItems( self ) :
		#check recording
		runningTimerList = self.mDataCache.Timer_GetRunningTimers( )
		#LOG_TRACE( 'runningTimerList[%s]'% runningTimerList )
		if runningTimerList :
			for timer in runningTimerList :
				self.mDataCache.Timer_DeleteTimer( timer.mTimerId )


		from pvr.IpParser import *
		"""
		LOG_TRACE('1. update version ------' )
		try :

			fd = open( E_CURRENT_INFO, 'w' )

			if fd :
				updateVersion = ''
				updateDate = ''
				if self.mPVSData :
					updateVersion = self.mPVSData.mVersion
					updateDate = self.mPVSData.mDate

				fd.writelines( 'Version=%s\n'% updateVersion )
				fd.writelines( 'Date=%s\n'% updateDate )

				fd.close( )

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )
		"""


		LOG_TRACE('2. network settings ------' )
		try :
			RemoveDirectory( E_DEFAULT_BACKUP_PATH )
			CreateDirectory( E_DEFAULT_BACKUP_PATH )

			fd = open( '%s/network.conf'% E_DEFAULT_BACKUP_PATH, 'w' )
			if fd :
				nType = GetCurrentNetworkType( )
				fd.writelines( 'NetworkType=%s\n'% nType )
				command = pvr.ElisMgr.GetInstance( ).GetCommander( )
				if nType == NETWORK_ETHERNET :
					ipInfo = IpParser( )
					ipInfo.LoadEthernetType( )
					ethType = 'dhcp'
					if ipInfo.GetEthernetType( ) :
						ethType = 'static'
					fd.writelines( 'ethtype=%s\n'% ethType )
					fd.writelines( 'ipaddr=%s.%s.%s.%s\n'% ( MakeHexToIpAddr( ElisPropertyInt( 'IpAddress' , command ).GetProp( ) ) ) )
					fd.writelines( 'subnet=%s.%s.%s.%s\n'% ( MakeHexToIpAddr( ElisPropertyInt( 'SubNet' , command ).GetProp( ) ) ) )
					fd.writelines( 'gateway=%s.%s.%s.%s\n'% ( MakeHexToIpAddr( ElisPropertyInt( 'Gateway' , command ).GetProp( ) ) ) )
					fd.writelines( 'dns=%s.%s.%s.%s\n'% ( MakeHexToIpAddr( ElisPropertyInt( 'DNS' , command ).GetProp( ) ) ) )
				else :
					wifiInfo = WirelessParser( )
					wifiInfo.LoadWpaSupplicant( )
					fd.writelines( 'devname=%s\n'% wifiInfo.GetWifidevice( ) )
					rd = open( FILE_WPA_SUPPLICANT, 'r' )
					wifiData = rd.readlines( )
					rd.close( )
					if wifiData :
						for line in wifiData :
							value = ParseStringInPattern( '=', line )
							#LOG_TRACE('-----------split[%s]'% value )
							if not value or len( value ) < 2 :
								continue

							if not value[0] :
								continue

							if value[0][0] == '#' or ( value[1] and value[1][0] ) == '{' : 
								continue

							fd.writelines( '%s=%s\n'% ( value[0], value[1] ) )

				fd.close( )

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )

		LOG_TRACE('3. user settings ------' )
		mboxDir = xbmcaddon.Addon( 'script.mbox' ).getAddonInfo( 'path' )
		backupFileList = [  '%s/resources/settings.xml'% mboxDir,
							'%s/.xbmc/userdata/guisettings.xml'% E_DEFAULT_PATH_HDD 
						 ]
		#LOG_TRACE( 'mboxDir[%s]'% mboxDir )
		try :
			CopyToFile( backupFileList[0], '%s/%s'% ( E_DEFAULT_BACKUP_PATH, os.path.basename( backupFileList[0] ) ) )
			if not CheckHdd( ) :
				CopyToFile( backupFileList[1], '%s/%s'% ( E_DEFAULT_BACKUP_PATH, os.path.basename( backupFileList[1] ) ) )

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )

		LOG_TRACE('4. make run script ------' )
		try :
			scriptFile = '%s.sh'% E_DEFAULT_BACKUP_PATH
			fd = open( scriptFile, 'w' )
			if fd :
				fd.writelines( '#!/bin/sh\n' )
				fd.writelines( 'cp -f %s/%s %s\n'% ( E_DEFAULT_BACKUP_PATH, os.path.basename( backupFileList[0] ), backupFileList[0] ) )
				if not CheckHdd( ) :
					fd.writelines( 'cp -f %s/%s %s\n'% ( E_DEFAULT_BACKUP_PATH, os.path.basename( backupFileList[1] ), backupFileList[1] ) )
				fd.close( )

				os.chmod( scriptFile, 0755 )

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )

		return


	def CheckCurrentVersion( self ) :
		lbldesc = ''
		try :
			f = open( E_CURRENT_INFO, 'r' )
			currInfo = f.readlines( )
			f.close( )


			iPVS = PVSClass( )
			for line in currInfo :
				value = ParseStringInPattern( '=', line )
				#LOG_TRACE('-----------split[%s]'% value )
				if not value or len( value ) < 2 :
					continue

				if value[0].lower() == 'version' :
					if value[1].isdigit( ) :
						#iPVS.mVersion = self.GetParseVersion( value[1] )
						iPVS.mVersion = value[1]
					else :
						iPVS.mVersion = value[1]

				elif value[0].lower() == 'date' :
					iPVS.mDate = value[1]

			iPVS.mError = 0

			lbldesc += '%s : %s\n'% ( MR_LANG( 'CURRENT VER.' ), iPVS.mVersion )
			lbldesc += '%s : %s\n'% ( MR_LANG( 'DATE' ), iPVS.mDate )
			#lbldesc += '%s\n%s\n'% ( MR_LANG( 'DESCRIPTION' ), iPVS.mDescription )

			self.mCurrData = iPVS


		except Exception, e :
			LOG_ERR( 'except[%s]'% e )
			lbldesc = MR_LANG( 'Unknown version' )

		if self.mCurrData and not self.mCurrData.mVersion :
			lbldesc = MR_LANG( 'Unknown version' )

		self.UpdatePropertyGUI( 'CurrentDescription', lbldesc )



	def UpdateChannel( self ) :
		self.mChannelUpdateProgress = self.ChannelUpdateProgress( MR_LANG( 'Downloading server information' ), 20 )
		parselist =  self.GetServerInfo( )
		if parselist == None :
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_CONNECT_ERROR )
			self.CloseProgress( )
			return

		LOG_TRACE( 'server info = %s' % parselist )

		makelist = self.ParseList( parselist )

		if makelist == None :
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_CHANNEL_FAIL )
			self.CloseProgress( )
			return

		self.CloseProgress( )
		showtext = []
		for text in makelist :
			showtext.append( text[1] + '( ' + text[2] + ' )' )

		dialog = xbmcgui.Dialog( )
		ret = dialog.select( MR_LANG( 'Select Channel Package' ), showtext )
		if ret >= 0 :
			result = self.GetChannelUpdate( makelist[ret][0] )
			if result :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG('Update finished'), MR_LANG('Updating channel list is finished successfully') )
				dialog.doModal( )
			else :
				self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_CHANNEL_FAIL )


	def GetServerInfo( self ) :
		parselist = None
		try :
			import urllib2
			f = urllib2.urlopen( E_DEFAULT_CHANNEL_LIST, None, 20 )
			if f :
				parselist = f.read( )
			f.close( )
			return parselist

		except URLError, e:
			if f.closed == False :
				f.close( )
			LOG_ERR( 'Error exception[%s]' % e.reason )
			return None


	def ParseList( self, aParseInfo ) :
		try :
			updatelist = string.split( aParseInfo )
			templist = []
			makelist = []
			if len( updatelist ) % 3 == 0 :
				for i in range( len( updatelist ) ) :
					templist.append( updatelist[i] )
					if ( i + 1 ) % 3 == 0 :
						makelist.append( templist )
						templist = []
				LOG_TRACE( 'makelist = %s' % makelist )
				return makelist
			else :
				return None

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]' % e )
			return None


	def GetChannelUpdate( self, aKey ) :
		self.mChannelUpdateProgress = self.ChannelUpdateProgress( MR_LANG( 'Now updating your channel list' ), 30 )
		ret = self.DownloadxmlFile( aKey )
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
		


	def DownloadxmlFile( self, aKey ) :
		try :
			import urllib2
			updatefile = urllib2.urlopen( E_DEFAULT_CHANNEL_LIST + '?key=%s' % aKey , None, 20 )
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

