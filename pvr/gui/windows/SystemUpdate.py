from pvr.gui.WindowImport import *
from pvr.XBMCInterface import XBMC_CheckNetworkStatus
from fileDownloader import DownloadFile
from version import LooseVersion
from copy import deepcopy
import stat
import shutil
import time
import os
import glob
if E_USE_OLD_NETWORK :
	import pvr.IpParser as NetMgr
else :
	import pvr.NetworkMgr as NetMgr

E_SYSTEM_UPDATE_BASE_ID = WinMgr.WIN_ID_SYSTEM_UPDATE * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID

E_TYPE_PRISMCUBE = 1
E_TYPE_ADDONS = 2

E_DEFAULT_NAND_IMAGE      = 'update.img'
E_DEFAULT_DIR_UNZIP       = 'update_ruby'
E_CURRENT_INFO            = '/etc/release.info'
E_DOWNLOAD_INFO_PVS       = '/mnt/hdd0/program/download/update.xml'
E_DOWNLOAD_PATH_FWURL     = '/mtmp/fwUrl'
E_DOWNLOAD_PATH_UNZIPFILES ='/mtmp/unziplist'
E_DEFAULT_PATH_HDD        = '/mnt/hdd0/program'
E_DEFAULT_PATH_DOWNLOAD   = '%s/download'% E_DEFAULT_PATH_HDD
E_DEFAULT_PATH_USB_UPDATE = '/media/sdb1'
E_DEFAULT_URL_PVS         = 'http://update.prismcube.com/update_new.html?product=ruby'
E_DEFAULT_URL_REQUEST_FW  = 'http://update.prismcube.com/download_new.html?key='
E_DEFAULT_URL_REQUEST_UNZIPFILES  = 'http://update.prismcube.com/download_new.html?unzipfiles='

E_DEFAULT_CHANNEL_LIST		= 'http://update.prismcube.com/channel.html'

E_CONTROL_ID_GROUP_PVS      = 9000 + E_SYSTEM_UPDATE_BASE_ID
E_CONTROL_ID_LABEL_TITLE    = 99 + E_SYSTEM_UPDATE_BASE_ID
E_CONTROL_ID_LABEL_VERSION  = 100 + E_SYSTEM_UPDATE_BASE_ID
E_CONTROL_ID_LABEL_DATE     = 101 + E_SYSTEM_UPDATE_BASE_ID
E_CONTROL_ID_LABEL_SIZE     = 102 + E_SYSTEM_UPDATE_BASE_ID
E_CONTROL_ID_PROGRESS       = 51 + E_SYSTEM_UPDATE_BASE_ID
E_CONTROL_ID_LABEL_PERCENT  = 52 + E_SYSTEM_UPDATE_BASE_ID

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
E_UPDATE_STEP_NAND_WRITE  = 8
E_UPDATE_STEP_FINISH      = 9
E_UPDATE_STEP_UPDATE_NOW  = 10
E_UPDATE_STEP_ERROR_NETWORK = 11

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
E_STRING_CHECK_DOWNLOADING = 15
E_STRING_CHECK_HDD         = 16
E_STRING_CHECK_HDD_SPACE   = 17
E_STRING_CHECK_BLOCK_FLASH = 18
E_STRING_CHECK_BLOCK_SIZE  = 19
E_STRING_CHECK_NAND_WRITE  = 20
E_STRING_CHECK_CENCEL  = 21

UPDATE_TEMP_CHANNEL		= '/mtmp/updatechannel.xml'

class PVSClass( object ) :
	def __init__( self ) :
		self.mKey					= None
		self.mName					= None
		self.mFileName				= None
		self.mDate					= None
		self.mDescription			= ''
		self.mActions				= ''
		self.mMd5					= None
		self.mSize					= 0		#zipSize
		self.mUnpackSize			= 0		#fullSize
		self.mUnzipDir				= 'update_ruby'
		self.mVersion				= 0
		self.mId					= None
		self.mType					= None
		self.mError					= -1

	def printdebug( self ):
		print 'Class  PVSClass'
		print 'mKey= %s'% self.mKey
		print 'mName= %s'%self.mName
		print 'mFileName= %s'%self.mFileName
		print 'mDate= %d'%self.mDate
		print 'mDescription= %s'%self.mDescription
		print 'mActions= %s'%self.mActions
		print 'mMd5= %s'%self.mMd5
		print 'mSize= %s'%self.mSize
		print 'mUnpackSize= %s'%self.mUnpackSize
		print 'mUnzipDir= %s'%self.mUnzipDir
		print 'mVersion= %s'%self.mVersion
		print 'mId= %s'%self.mId
		print 'mType= %s'%self.mType
		print 'mError= %s'%self.mError


class SystemUpdate( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )

		self.mPVSList               = []
		self.mPVSData               = None
		self.mCurrData              = None
		self.mProgress				= None
		self.mChannelUpdateProgress = None
		self.mIsDownload 			= False
		self.mIsCancel 				= False
		self.mLinkStatus 			= False
		self.mGetDownloadThread     = None
		self.mEnableLocalThread 	= False
		self.mCheckEthernetThread 	= None
		self.mStepPage              = E_UPDATE_STEP_HOME

	def onInit( self )  :
		self.SetActivate( True )
		self.SetFrontdisplayMessage( MR_LANG( 'System Update' ) )

		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.SetSingleWindowPosition( E_SYSTEM_UPDATE_BASE_ID )

		self.mCtrlLabelDescTitle      = self.getControl( E_SETTING_DESCRIPTION )
		self.mCtrlLabelTitle          = self.getControl( E_CONTROL_ID_LABEL_TITLE )
		self.mCtrlLabelDate           = self.getControl( E_CONTROL_ID_LABEL_DATE )
		self.mCtrlLabelVersion        = self.getControl( E_CONTROL_ID_LABEL_VERSION )
		self.mCtrlLabelSize           = self.getControl( E_CONTROL_ID_LABEL_SIZE )
		self.mCtrlProgress            = self.getControl( E_CONTROL_ID_PROGRESS )
		self.mCtrlLabelPercent        = self.getControl( E_CONTROL_ID_LABEL_PERCENT )

		#parse settings.xml
		#self.mPVSData = None
		#self.mCurrData = None
		self.mIndexLastVersion = 0
		self.mShowProgressThread = None

		self.SetSettingWindowLabel( MR_LANG( 'Update' ) )
		self.SetHeaderTitle( "%s - %s"%( MR_LANG( 'Installation' ), MR_LANG( 'Update' ) ) )

		self.SetPipScreen( )
		#self.LoadNoSignalState( )

		self.UpdateStepPage( E_UPDATE_STEP_HOME )

		self.mInitialized = True


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.Close( )
				
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
				if self.mGetDownloadThread :
					#self.DialogPopup( E_STRING_ATTENTION, E_STRING_CHECK_DOWNLOADING )
					LOG_ERR( 'Now Downloading' )
					return

				else :
					self.ShowContextMenu( )


	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
		groupId = self.GetGroupId( aControlId )
		if groupId == E_Input01 :
			#LOG_TRACE('-----------pvslist[%s] pvsData[%s] downThread[%s] isDownload[%s]'% (len( self.mPVSList ), self.mPVSData, self.mGetDownloadThread, self.mIsDownload ) )
			self.LoadInit( )

		elif groupId == E_Input02 :
			#LOG_TRACE('-----------------mStepPage[%s]'% self.mStepPage )
			if self.mStepPage == E_UPDATE_STEP_HOME :
				self.UpdateChannelsByInternet( )

			elif self.mStepPage == E_UPDATE_STEP_UPDATE_NOW :
				self.UpdateStepPage( E_UPDATE_STEP_UPDATE_NOW )

			else :
				#LOG_TRACE('------------isDownload[%s] downThread[%s]'% ( self.mIsDownload, self.mGetDownloadThread ) )
				if self.mIsDownload :
					self.UpdateHandler( )
					if self.mStepPage < E_UPDATE_STEP_UPDATE_NOW :
						self.mStepPage = E_UPDATE_STEP_READY
				else :
					if self.mGetDownloadThread :
						self.SetFailProcess( E_STRING_CHECK_CENCEL )

					else :
						self.mGetDownloadThread = self.GetDownloadThread( )

		elif groupId == E_Input03 :
			LOG_TRACE( 'Import Channels from USB' )
			self.ImportChannelsFromUSB( )

		elif groupId == E_Input04 :
			LOG_TRACE( 'Export Channels to USB' )		
			self.ExportChannelsToUSB( )


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
		if self.mInitialized :
			self.ShowDescription( aControlId )


	def LoadInit( self ) :
		global E_UPDATE_FIRMWARE_USE_USB, E_DEFAULT_PATH_DOWNLOAD, E_DEFAULT_PATH_HDD
		E_UPDATE_FIRMWARE_USE_USB = False

		hddPath = self.mDataCache.HDD_GetMountPath( 'program' )
		if hddPath and E_UPDATE_FIRMWARE_USB_ONLY == False :
			LOG_TRACE( 'Check HDD True[%s]'% hddPath )
			E_DEFAULT_PATH_HDD = hddPath
			E_DEFAULT_PATH_DOWNLOAD = '%s/download'% E_DEFAULT_PATH_HDD

		else :
			E_UPDATE_FIRMWARE_USE_USB = True

			usbPath = self.mDataCache.USB_GetMountPath( )
			if not usbPath :
				self.DialogPopup( E_STRING_ATTENTION, E_STRING_CHECK_USB_NOT )
				self.OpenAnimation( )
				self.SetFocusControl( E_CONTROL_ID_GROUP_PVS )
				self.UpdateStepPage( E_UPDATE_STEP_HOME )
				return

			E_DEFAULT_PATH_DOWNLOAD = '%s/stb/download'% usbPath
			#LOG_TRACE('-------------------------usbpath[%s] define[%s]'% ( usbPath, E_DEFAULT_PATH_DOWNLOAD ) )

		if self.mPVSData and self.mPVSData.mError == 0 :
			LOG_TRACE('------------PVSData ver[%s] size[%s] file[%s]'% (self.mPVSData.mVersion, self.mPVSData.mSize, self.mPVSData.mFileName) )
			self.UpdateStepPage( E_UPDATE_STEP_READY )

			if self.mGetDownloadThread :
				self.InitPVSData( )
			else :
				self.UpdateStepPage( E_UPDATE_STEP_PROVISION )

		else :
			if self.mStepPage == E_UPDATE_STEP_HOME :
				self.UpdateStepPage( E_UPDATE_STEP_READY )
			else :
				self.UpdateStepPage( E_UPDATE_STEP_PROVISION )


	def OpenAnimation( self ) :
		self.setFocusId( E_FAKE_BUTTON )
		time.sleep( 0.3 )


	def CheckNoChannel( self ) :
		if self.mDataCache.Channel_GetList( ) :
			return True
		else :
			return False


	def GetStatusFromFirmware( self ) :
		return self.mGetDownloadThread


	def Close( self ) :
		if not self.mGetDownloadThread and \
		   self.mEnableLocalThread and self.mCheckEthernetThread :
			self.mEnableLocalThread = False
			self.mCheckEthernetThread.join( )
			self.mCheckEthernetThread = None

			self.mIsCancel = False
			self.mIsDownload = False

		self.ResetAllControl( )
		self.SetVideoRestore( )
		WinMgr.GetInstance( ).CloseWindow( )


	def CheckEthernetType( self ) :
		if E_USE_OLD_NETWORK :
			import pvr.IpParser as NetMgr
		else :
			import pvr.NetworkMgr as NetMgr

		nType = NetMgr.GetInstance( ).GetCurrentServiceType( )
		return nType


	@RunThread
	def CheckEthernetThread( self ) :
		count = 0
		nType = self.CheckEthernetType( )
		LOG_TRACE( '--------------nType[%s]'% nType )
		while self.mEnableLocalThread :
			if ( count % 20 ) == 0 :
				if self.mStepPage >= E_UPDATE_STEP_PROVISION and self.mStepPage <= E_UPDATE_STEP_DOWNLOAD :
					status = 'down'
					if nType == NETWORK_ETHERNET :
						status = CheckEthernet( 'eth0' )

					else :
						wifiRet = XBMC_CheckNetworkStatus( )
						if wifiRet == 'Connected' or wifiRet == 'Busy' :
							status = 'up'
						LOG_TRACE('------------wifi ret[%s] status[%s]'% ( wifiRet, status ) )

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


	def AsyncCompleteDialog( self ) :
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( MR_LANG( 'Download firmware complete' ), MR_LANG( 'Do you want to install the firmware now?' ) )
		dialog.doModal( )

		answer = dialog.IsOK( )
		if answer == E_DIALOG_STATE_YES :
			curWinID = xbmcgui.getCurrentWindowId( )
			updateWinID = self.mWinId
			if E_SUPPORT_SINGLE_WINDOW_MODE :
				curWinID = WinMgr.GetInstance( ).GetLastWindowID( )
				updateWinID = WinMgr.WIN_ID_SYSTEM_UPDATE

 			if curWinID != updateWinID :
 				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_SYSTEM_UPDATE, WinMgr.WIN_ID_NULLWINDOW )
 				self.LoadInit( )

			elif curWinID == updateWinID and self.mStepPage == E_UPDATE_STEP_HOME :
				self.LoadInit( )


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

		self.setProperty( aPropertyID, aValue )


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
			line = MR_LANG( 'Please insert a USB flash memory and press OK' )
		elif aMsg == E_STRING_CHECK_VERIFY :
			line = MR_LANG( 'File verification failed%s Try downloading it again' )% NEW_LINE
		elif aMsg == E_STRING_CHECK_FINISH :
			line = MR_LANG( 'Ready to update' )
		elif aMsg == E_STRING_CHECK_UNLINK_NETWORK :
			line = MR_LANG( 'Network is disconnected' )
		elif aMsg == E_STRING_CHECK_DISKFULL :
			line = MR_LANG( 'Insufficient disk space' )
		elif aMsg == E_STRING_CHECK_HDD_SPACE :
			line = MR_LANG( 'Not enough space on your HDD' )
		elif aMsg == E_STRING_CHECK_USB_SPACE :
			line = MR_LANG( 'Not enough space on your USB flash memory' )
		elif aMsg == E_STRING_CHECK_CONNECT_ERROR :
			line = MR_LANG( 'Cannot connect to server' )
		elif aMsg == E_STRING_CHECK_CHANNEL_FAIL :
			line = MR_LANG( 'Update process failed' )
		elif aMsg == E_STRING_CHECK_NOT_OLDVERSION :
			line = MR_LANG( 'Cannot find previous versions' )
		elif aMsg == E_STRING_CHECK_FAILED :
			line = MR_LANG( 'Cannot get the latest firmware%s Please try again' )% NEW_LINE
		elif aMsg == E_STRING_CHECK_HAVE_NONE :
			line = MR_LANG( 'No released firmware available' )
		elif aMsg == E_STRING_CHECK_DOWNLOADING :
			line = MR_LANG( 'Downloading...' )
		elif aMsg == E_STRING_CHECK_HDD :
			line = MR_LANG( 'Check your HDD' )
		elif aMsg == E_STRING_CHECK_BLOCK_FLASH :
			line = MR_LANG( 'Check your internal NAND flash' )
		elif aMsg == E_STRING_CHECK_BLOCK_SIZE :
			line = MR_LANG( 'Not enough space on NAND flash' )
		elif aMsg == E_STRING_CHECK_NAND_WRITE :
			line = MR_LANG( 'Failed to write on NAND flash' )

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


	def InitPVSData( self, aForce = False ) :
		isInit = True
		showProgress = E_TAG_FALSE
		buttonFocus  = E_Input01
		button1Enable = True
		button2Enable = False
		button2Label  = MR_LANG( 'Not attempted' )
		button2Desc   = MR_LANG( 'Please check firmware version first' )

		if not self.mPVSData or self.mPVSData.mError != 0 :
			self.SetEnableControl( E_Input02, button2Enable )
			self.SetControlLabel2String( E_Input02, button2Label )
			self.EditDescription( E_Input02, button2Desc )
			self.ShowDescription( E_Input02 )
			#self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_FAILED )
			return False


		if self.mGetDownloadThread :
			showProgress = E_TAG_TRUE
			buttonFocus  = E_Input02
			button1Enable = False
			button2Enable = True
			button2Label  = MR_LANG( 'Cancel' )
			button2Desc   = MR_LANG( 'Press OK to cancel downloading firmware updates' )

		else :
			self.mIsDownload = False
			tempFile = '%s/%s'% ( E_DEFAULT_PATH_DOWNLOAD, self.mPVSData.mFileName )
			#LOG_TRACE( '----------------downpath[%s]'% tempFile )

			if not aForce and self.mCurrData and self.mCurrData.mError == 0 and self.mCurrData.mVersion == self.mPVSData.mVersion :
				isInit = 2
				buttonFocus  = E_Input01
				button2Enable = False
				button2Label  = MR_LANG( 'Your system is up-to-date' )
				button2Desc   = MR_LANG( 'Already updated to the latest version' )

				self.ResetLabel( )

			elif CheckDirectory( tempFile ) and \
			     os.stat( tempFile )[stat.ST_SIZE] == self.mPVSData.mSize :
				self.mIsDownload = True
				buttonFocus  = E_Input02
				button2Enable = True

				button2Label = MR_LANG( 'Copy to HDD' )
				button2Desc  = MR_LANG( 'Download complete. Press OK to copy firmware files to HDD' )
				if E_UPDATE_FIRMWARE_USE_USB :
					button2Label  = MR_LANG( 'Copy to USB' )
					button2Desc   = MR_LANG( 'Download complete. Press OK to copy firmware files to USB' )

			else :
				buttonFocus  = E_Input02
				button2Enable = True
				button2Label  = MR_LANG( 'Download' )
				button2Desc   = MR_LANG( 'Press OK button to download the firmware shown below' )

		self.UpdateLabelPVSInfo( )

		self.UpdatePropertyGUI( 'ShowProgress', showProgress )
		self.SetEnableControl( E_Input01, button1Enable )
		self.SetEnableControl( E_Input02, button2Enable )
		self.SetControlLabel2String( E_Input02, button2Label )
		self.EditDescription( E_Input02, button2Desc )
		self.ShowDescription( E_Input02 )
		self.SetFocusControl( buttonFocus )

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
		LOG_TRACE('----------downThread[%s] isDownload[%s]'% ( self.mGetDownloadThread, self.mIsDownload ) )
		oldPVSData = None
		if self.mPVSData and self.mPVSData.mError == 0 :
			oldPVSData = self.mPVSData

		self.mIsDownload = False
		if self.mGetDownloadThread :
			self.mIsCancel = True
			self.mGetDownloadThread.join( )
			self.mGetDownloadThread = None

		isDownload = False
		self.mPVSData = None
		self.mPVSList = []
		self.ResetLabel( )

		self.OpenBusyDialog( )
		try :
			CreateDirectory( E_DEFAULT_PATH_DOWNLOAD )
			CreateDirectory( '%s'% os.path.dirname( E_DOWNLOAD_INFO_PVS ) )
			isDownload = GetURLpage( E_DEFAULT_URL_PVS, E_DOWNLOAD_INFO_PVS )
			#LOG_TRACE( '[pvs]%s'% isDownload )

			if isDownload :
				mPVSList = []
				tagNames = ['key', 'filename', 'date', 'version', 'zipsize', 'size', 'md5', 'description', 'action']
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
						if pvsData[8] :
							actions = ''
							for item in pvsData[8] :
								actions += '%s\n'% item
							iPVS.mActions = actions
						#if pvsData[9] :
						#	iPVS.mUnzipDir = pvsData[9]

						iPVS.mName = MR_LANG( 'Downloading firmware' )
						iPVS.mType = E_TYPE_ADDONS
						iPVS.mError = 0
						mPVSList.append( iPVS )

					#Check Lastest version
					if mPVSList and len( mPVSList ) > 0 :
						#self.mPVSList = sorted( mPVSList, key=lambda pvslist: pvslist.mVersion, reverse=True )
						self.mPVSList = sorted( mPVSList, key=lambda pvslist: LooseVersion(pvslist.mVersion), reverse=True )

						if oldPVSData and oldPVSData.mError == 0 :
							self.mPVSData = oldPVSData
						else :
							self.mPVSData = deepcopy( self.mPVSList[0] )
							self.mPVSData.mType = E_TYPE_PRISMCUBE

						#self.mPVSList.pop( 0 )

				else :
					self.mPVSData = deepcopy( self.mCurrData )

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )
			self.mPVSData = None
			self.mPVSList = []
			isDownload = False

		self.CloseBusyDialog( )

		if not isDownload :
			self.SetEnableControl( E_Input02, False )
			self.SetControlLabel2String( E_Input02, MR_LANG( 'Not attempted') )
			self.EditDescription( E_Input02, MR_LANG( 'Please check firmware version first' ) )
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_ADDRESS )
			return

		LOG_TRACE('----------pvsData[%s]'% self.mPVSData )

		if self.mPVSList and len( self.mPVSList ) > 0 :
			if self.mCurrData and self.mCurrData.mError == 0 and \
			   self.mPVSData and self.mPVSData.mError == 0 and \
			   self.mCurrData.mVersion == self.mPVSData.mVersion :
				self.DialogPopup( MR_LANG( 'Firmware Version' ), E_STRING_CHECK_UPDATED )

		else :
			self.DialogPopup( MR_LANG( 'Firmware Update' ), E_STRING_CHECK_HAVE_NONE )

		#self.ControlDown( )


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
			"""
			if self.mPVSData and self.mPVSData.mError == 0 :
				global E_DEFAULT_DIR_UNZIP
				tempFile = '%s/%s'% ( E_DEFAULT_PATH_DOWNLOAD, self.mPVSData.mFileName )
				unzipDir = GetUnpackDirectory( tempFile ) :
				if unzipDir and unzipDir != E_DEFAULT_DIR_UNZIP :
					E_DEFAULT_DIR_UNZIP = '%s'% unzipDir
					LOG_TRACE( '--------catched unzip directory[%s]'% E_DEFAULT_DIR_UNZIP )
			"""

			try :
				RemoveDirectory( E_DEFAULT_BACKUP_PATH )
				RemoveDirectory( E_DEFAULT_PATH_DOWNLOAD )
				unpackPath = E_DEFAULT_PATH_DOWNLOAD
				if E_UPDATE_FIRMWARE_USE_USB :
					unpackPath = self.mDataCache.USB_GetMountPath( )
				else :
					InitFlash( )

				if unpackPath :
					#RemoveDirectory( '%s/%s'% ( unpackPath, E_DEFAULT_DIR_UNZIP ) )
					if self.mPVSList and len( self.mPVSList ) > 0 :
						for iPVS in self.mPVSList :
							#RemoveDirectory( '%s/%s'% ( unpackPath, iPVS.mUnzipDir ) )
							request = '%s%s'% ( E_DEFAULT_URL_REQUEST_UNZIPFILES, iPVS.mKey )
							if GetURLpage( request, E_DOWNLOAD_PATH_UNZIPFILES ) :
								RemoveUnzipFiles( unpackPath, False, E_DOWNLOAD_PATH_UNZIPFILES )

			except Exception, e :
				LOG_ERR( 'except[%s]'% e )

			self.mIsDownload = False
			if self.mGetDownloadThread :
				self.mIsCancel = True
				self.mGetDownloadThread.join( )
				self.mGetDownloadThread = None

			self.mPVSData = None
			self.mPVSList = []
			self.ResetLabel( False )
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

			self.mIsDownload = False
			if self.mGetDownloadThread :
				self.mIsCancel = True
				self.mGetDownloadThread.join( )
				self.mGetDownloadThread = None

			self.mPVSData = None
			self.mPVSData = deepcopy( self.mPVSList[select] )
			if select == 0 : #lastest version
				self.mPVSData.mType = E_TYPE_PRISMCUBE

			#global E_DEFAULT_DIR_UNZIP
			#if E_DEFAULT_DIR_UNZIP != self.mPVSData.mUnzipDir :
			#	E_DEFAULT_DIR_UNZIP = '%s'% self.mPVSData.mUnzipDir

			ret = self.InitPVSData( True )
			self.mStepPage = E_UPDATE_STEP_READY

			unpackPath = E_DEFAULT_PATH_DOWNLOAD
			if E_UPDATE_FIRMWARE_USE_USB :
				unpackPath = self.mDataCache.USB_GetMountPath( )

			if not ret :
				self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_FAILED )
				return

			#if ret == 2 :
			#	self.DialogPopup( MR_LANG( 'Firmware Version' ), E_STRING_CHECK_UPDATED )
			#	return

			if unpackPath :
				#RemoveDirectory( '%s/%s'% ( unpackPath, E_DEFAULT_DIR_UNZIP ) )
				#RemoveDirectory( '%s/%s'% ( unpackPath, self.mPVSData.mUnzipDir ) )
				request = '%s%s'% ( E_DEFAULT_URL_REQUEST_UNZIPFILES, self.mPVSData.mKey )
				if GetURLpage( request, E_DOWNLOAD_PATH_UNZIPFILES ) :
					RemoveDirectory( E_DEFAULT_BACKUP_PATH )
					RemoveUnzipFiles( unpackPath, False, E_DOWNLOAD_PATH_UNZIPFILES )
					if not E_UPDATE_FIRMWARE_USE_USB :
						InitFlash( )

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
			self.AddInputControl( E_Input02, MR_LANG( 'Update Channels via Internet' ), '',  MR_LANG( 'Download a pre-configured channel list over the internet' ) )

			self.AddInputControl( E_Input03, MR_LANG( 'Import Channels from USB' ), '', MR_LANG( 'Import a pre-configured channel list via USB' ) )
			self.AddInputControl( E_Input04, MR_LANG( 'Export Channels to USB' ), '',  MR_LANG( 'Export your channel list via USB' ) )

			self.SetEnableControl( E_Input01, True )
			self.SetEnableControl( E_Input02, True )

			self.SetEnableControl( E_Input03, True )
			self.SetEnableControl( E_Input04, True )
			self.SetVisibleControl( E_Input03, True )
			self.SetVisibleControl( E_Input04, True )

			self.InitControl( )
			self.SetFocusControl( E_Input01 )

			#self.mPVSData = None
			self.ResetLabel( False )
			self.UpdatePropertyGUI( 'CurrentDescription', '' )
			self.UpdatePropertyGUI( 'ShowInfoLabel', E_TAG_FALSE )
			self.UpdatePropertyGUI( 'ShowProgress', E_TAG_FALSE )

		elif aStep == E_UPDATE_STEP_READY :
			#showProgress  = E_TAG_FALSE
			buttonFocus   = E_Input01
			button2Enable = False
			button2Label  = MR_LANG( 'Not attempted' )
			button2Desc   = MR_LANG( 'Please check firmware version first' )
			if self.mPVSData and len( self.mPVSList ) > 0 and self.mIsDownload :
				#showProgress  = E_TAG_FALSE
				buttonFocus   = E_Input02
				button2Enable = True
				button2Label = MR_LANG( 'Install')
				button2Desc  = MR_LANG( 'Complete download, Press OK is install' )

			self.SetSettingWindowLabel( MR_LANG( 'Update Firmware' ) )
			self.ResetAllControl( )
			self.AddInputControl( E_Input01, MR_LANG( 'Check Firmware Version' ), '', MR_LANG( 'Check the latest firmware released on the update server' ) ) 
			self.AddInputControl( E_Input02, '', button2Label, button2Desc )
			self.SetEnableControl( E_Input02, button2Enable )

			self.SetEnableControl( E_Input03, False )
			self.SetEnableControl( E_Input04, False )
			self.SetVisibleControl( E_Input03, False )
			self.SetVisibleControl( E_Input04, False )

			self.InitControl( )
			self.SetFocusControl( buttonFocus )
			self.UpdatePropertyGUI( 'ShowInfoLabel', E_TAG_TRUE )
			self.UpdatePropertyGUI( 'ShowProgress', E_TAG_FALSE )

			self.CheckCurrentVersion( )

		elif aStep == E_UPDATE_STEP_PROVISION :
			self.Provisioning( )
			if not self.InitPVSData( ) :
				self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_FAILED )

		elif aStep == E_UPDATE_STEP_DOWNLOAD :
			LOG_TRACE('-----------downThread[%s] isDownload[%s]'% ( self.mGetDownloadThread, self.mIsDownload ) )

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

			tempFile = '%s/%s'% ( E_DEFAULT_PATH_DOWNLOAD, self.mPVSData.mFileName )
			if not CheckDirectory( tempFile ) or os.stat( tempFile )[stat.ST_SIZE] != self.mPVSData.mSize :
				return False

			threadDialog = self.ShowProgressDialog( 30, MR_LANG( 'Checking files checksum...' ), None, strStepNo )
			self.OpenBusyDialog( )
			ret = CheckMD5Sum( tempFile, self.mPVSData.mMd5 )
			self.CloseBusyDialog( )
			if self.mShowProgressThread :
				self.mShowProgressThread.SetResult( True )
				self.mShowProgressThread = None
			if threadDialog :
				threadDialog.join( )
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

			unpackPath = E_DEFAULT_PATH_DOWNLOAD
			stepMsg = MR_LANG( 'Copying files to HDD...' )
			if E_UPDATE_FIRMWARE_USE_USB :
				unpackPath = self.mDataCache.USB_GetMountPath( )
				stepMsg = MR_LANG( 'Copying files to USB drive...' )

			if unpackPath :
				time.sleep( 0.3 )
				threadDialog = self.ShowProgressDialog( 60, stepMsg, None, strStepNo )
				self.OpenBusyDialog( )
				stepResult = UnpackToUSB( tempFile, unpackPath, self.mPVSData.mUnpackSize, E_DOWNLOAD_PATH_UNZIPFILES )
				self.CloseBusyDialog( )
				if self.mShowProgressThread :
					self.mShowProgressThread.SetResult( True )
					self.mShowProgressThread = None
				if threadDialog :
					threadDialog.join( )
				time.sleep( 1 )

			else :
				stepResult = False

			if stepResult != True :
				msgErr1 = E_STRING_CHECK_HDD_SPACE
				msgErr2 = E_STRING_CHECK_HDD
				if E_UPDATE_FIRMWARE_USE_USB :
					msgErr1 = E_STRING_CHECK_USB_SPACE
					msgErr2 = E_STRING_CHECK_USB

				if stepResult == -1 :
					self.DialogPopup( E_STRING_ERROR, msgErr1 )
				else :
					self.DialogPopup( E_STRING_ERROR, msgErr2 )

				stepResult = False

		elif aStep == E_UPDATE_STEP_VERIFY :
			tempFile = '%s/%s'% ( E_DEFAULT_PATH_DOWNLOAD, self.mPVSData.mFileName )
			if not self.VerifiedUnPack( tempFile ) :
				self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_VERIFY )
				stepResult = False

		elif aStep == E_UPDATE_STEP_NAND_WRITE :
			writeFile = GetImgPath( E_DOWNLOAD_PATH_UNZIPFILES, E_DEFAULT_NAND_IMAGE )
			if not writeFile :
				self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_CORRUPT )
				return False

			imgFile = '%s/%s'% ( E_DEFAULT_PATH_DOWNLOAD, writeFile )
			threadDialog = self.ShowProgressDialog( 20, MR_LANG( 'Copying files to internal storage...' ), None, strStepNo )

			self.OpenBusyDialog( )
			ret = SetWriteToFlash( imgFile )
			self.CloseBusyDialog( )

			if self.mShowProgressThread :
				self.mShowProgressThread.SetResult( True )
				self.mShowProgressThread = None
			if threadDialog :
				threadDialog.join( )
			time.sleep( 1 )

			if ret != True :
				if ret == -1 :
					self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_CORRUPT )
				elif ret == -2 :
					self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_BLOCK_FLASH )
				elif ret == -3 :
					self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_BLOCK_SIZE )
				elif ret == -4 :
					self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_NAND_WRITE )

				stepResult = False


		elif aStep == E_UPDATE_STEP_FINISH :
			time.sleep( 0.3 )
			#self.DialogPopup( E_STRING_ATTENTION, E_STRING_CHECK_FINISH )

		elif aStep == E_UPDATE_STEP_UPDATE_NOW :
			time.sleep( 0.3 )
			self.SetControlLabel2String( E_Input02, MR_LANG( 'Update now' ) )
			self.EditDescription( E_Input02, MR_LANG( 'Follow the instructions on front panel display during the firmware installation process' ) )
			self.ShowDescription( E_Input02 )

			self.CheckItems( )

			line1 = MR_LANG( 'DO NOT POWER OFF%s DURING THE UPGRADING' )% NEW_LINE
			if E_UPDATE_FIRMWARE_USE_USB :
				line1 = MR_LANG( 'DO NOT REMOVE YOUR USB%s DURING THE UPGRADING' )% NEW_LINE
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'WARNING' ), '%s'% line1 )
			dialog.doModal( )
			ret = dialog.IsOK( )

			#ret = E_DIALOG_STATE_YES
			if ret == E_DIALOG_STATE_YES :
				if E_UPDATE_FIRMWARE_USE_USB :
					RemoveDirectory( E_DEFAULT_PATH_DOWNLOAD )
					RemoveDirectory( os.path.dirname( E_DOWNLOAD_INFO_PVS ) )

				"""
				msg1 = MR_LANG( 'Your system must be restarted%s in order to complete the update' )% NEW_LINE
				self.mDialogShowInit = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				self.mDialogShowInit.SetDialogProperty( MR_LANG( 'Restart required' ), msg1 )
				self.mDialogShowInit.SetButtonVisible( False )
				self.mDialogShowInit.SetAutoCloseTime( 5 )
				self.mDialogShowInit.doModal( )
				"""

				self.OpenBusyDialog( )
				self.mDataCache.System_Reboot( )


		elif aStep == E_UPDATE_STEP_ERROR_NETWORK :
			thread = threading.Timer( 0.5, self.SetFailProcess, [E_STRING_CHECK_UNLINK_NETWORK] )
			thread.start( )
			#self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_UNLINK_NETWORK )
			if self.mEnableLocalThread and self.mCheckEthernetThread :
				self.mEnableLocalThread = False
				self.mCheckEthernetThread = None
			self.mEnableLocalThread = False

			self.SetFailProcess( E_STRING_CHECK_CENCEL )

		return stepResult


	def UpdateHandler( self ) :
		#LOG_TRACE('----------------pvs[%s]'% self.mPVSData )
		if self.mPVSData == None or self.mPVSData.mError != 0 :
			return

		#LOG_TRACE('----------------download File[%s]'% self.mPVSData.mFileName )
		#if not self.UpdateStepPage( E_UPDATE_STEP_DOWNLOAD ) :
		#	return

		if not self.UpdateStepPage( E_UPDATE_STEP_CHECKFILE ) :
			return

		#LOG_TRACE('----------------path down[%s] usb[%s]'% ( E_DEFAULT_PATH_DOWNLOAD, E_DEFAULT_PATH_USB_UPDATE ) )
		if E_UPDATE_FIRMWARE_USE_USB :
			if not self.UpdateStepPage( E_UPDATE_STEP_CHECKUSB ) :
				return

		#tempFile = '%s/%s'% ( E_DEFAULT_PATH_DOWNLOAD, self.mPVSData.mFileName )
		#if not self.VerifiedUnPack( tempFile, False ) :

		#remove old_Version
		unpackPath = E_DEFAULT_PATH_DOWNLOAD
		if E_UPDATE_FIRMWARE_USE_USB :
			unpackPath = self.mDataCache.USB_GetMountPath( )

		if unpackPath :
			request = '%s%s'% ( E_DEFAULT_URL_REQUEST_UNZIPFILES, self.mPVSData.mKey )
			if GetURLpage( request, E_DOWNLOAD_PATH_UNZIPFILES ) :
				RemoveUnzipFiles( unpackPath, False, E_DOWNLOAD_PATH_UNZIPFILES )

		if not self.UpdateStepPage( E_UPDATE_STEP_UNPACKING ) :
			return

		if not self.UpdateStepPage( E_UPDATE_STEP_VERIFY ) :
			return

		#flash write from HDD
		if not E_UPDATE_FIRMWARE_USE_USB :
			if not self.UpdateStepPage( E_UPDATE_STEP_NAND_WRITE ) :
				return

		#self.UpdateStepPage( E_UPDATE_STEP_FINISH )
		self.UpdateStepPage( E_UPDATE_STEP_UPDATE_NOW )


	@RunThread
	def GetDownloadThread( self ) :
		LOG_TRACE('-----------pvsData[%s]'% self.mPVSData )
		if self.mPVSData == None or self.mPVSData.mError != 0 :
			return

		LOG_TRACE('----------------download File[%s]'% self.mPVSData.mFileName )
		self.UpdatePropertyGUI( 'ShowProgress', E_TAG_TRUE )
		self.SetEnableControl( E_Input01, False )
		self.UpdateStepPage( E_UPDATE_STEP_DOWNLOAD )
		self.UpdatePropertyGUI( 'ShowProgress', E_TAG_FALSE )
		self.SetEnableControl( E_Input01, True )

		button2Label  = MR_LANG( 'Download' )
		button2Desc   = MR_LANG( 'Press OK button to download the firmware shown below' )

		if self.mIsDownload :
			#global E_DEFAULT_DIR_UNZIP
			#if E_DEFAULT_DIR_UNZIP != self.mPVSData.mUnzipDir :
			#	E_DEFAULT_DIR_UNZIP = '%s'% self.mPVSData.mUnzipDir

			button2Label = MR_LANG( 'Copy to HDD' )
			button2Desc  = MR_LANG( 'Download complete. Press OK to copy firmware files to HDD' )
			if E_UPDATE_FIRMWARE_USE_USB :
				button2Label = MR_LANG( 'Copy to USB' )
				button2Desc  = MR_LANG( 'Download complete. Press OK to copy firmware files to USB' )

			if self.mWinId == xbmcgui.getCurrentWindowId( ) and \
			   self.mStepPage > E_UPDATE_STEP_READY and self.mStepPage < E_UPDATE_STEP_UPDATE_NOW :
				self.SetControlLabel2String( E_Input02, button2Label )
				self.EditDescription( E_Input02, button2Desc )
				self.ShowDescription( E_Input02 )

				self.UpdateHandler( )

			else :
				thread = threading.Timer( 0.5, self.AsyncCompleteDialog )
				thread.start( )
				LOG_TRACE( '-------- async Alarm dialog(download complete)' )


		self.mGetDownloadThread = None


	def CheckInitDevice( self ) :
		sizeCheck = True

		global E_UPDATE_FIRMWARE_USE_USB, E_DEFAULT_PATH_DOWNLOAD, E_DEFAULT_PATH_HDD
		E_UPDATE_FIRMWARE_USE_USB = False

		hddPath = self.mDataCache.HDD_GetMountPath( 'program' )
		if hddPath and E_UPDATE_FIRMWARE_USB_ONLY == False :
			LOG_TRACE( 'Check HDD True[%s]'% hddPath )
			E_DEFAULT_PATH_HDD = hddPath
			E_DEFAULT_PATH_DOWNLOAD = '%s/download'% E_DEFAULT_PATH_HDD

			if GetDeviceSize( E_DEFAULT_PATH_HDD ) < self.mPVSData.mSize :
				self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_DISKFULL )
				sizeCheck = False

			return sizeCheck

		else :
			LOG_TRACE( 'Not Exist HDD' )
			#self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_HDD )
			E_UPDATE_FIRMWARE_USE_USB = True

			usbPath = self.mDataCache.USB_GetMountPath( )
			if not usbPath :
				LOG_TRACE( 'Not Exist USB' )
				self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_USB_NOT )
				return False

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
		isExist = GetURLpage( request, E_DOWNLOAD_PATH_FWURL )
		#LOG_TRACE('-------------req fwUrl[%s] ret[%s]'% ( request, isExist ) )

		if isExist == False :
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_HAVE_NONE )
			return False

		request = '%s%s'% ( E_DEFAULT_URL_REQUEST_UNZIPFILES, aPVS.mKey )
		isExist = GetURLpage( request, E_DOWNLOAD_PATH_UNZIPFILES )
		#LOG_TRACE('-------------req unzipfiles[%s] ret[%s]'% ( request, isExist ) )

		reqFile = ''
		tagNames = ['url']
		retList = ParseStringInXML( E_DOWNLOAD_PATH_FWURL, tagNames, 'urlinfo' )
		#LOG_TRACE('------------ret urlinfo[%s]'% retList )
		if retList and len( retList ) > 0 :
			reqFile = retList[0][0]

		else :
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_HAVE_NONE )
			return False

		self.mWorkingItem = deepcopy( aPVS )
		self.mWorkingDownloader = None

		#check device, size free, change path for hdd or usb 
		if not self.CheckInitDevice( ) :
			return False

		LOG_TRACE( 'download path[%s]'% E_DEFAULT_PATH_DOWNLOAD )
		CreateDirectory( E_DEFAULT_PATH_DOWNLOAD )

		isResume = False
		self.mIsDownload = False
		tempFile = '%s/%s'% ( E_DEFAULT_PATH_DOWNLOAD, aPVS.mFileName )
		if CheckDirectory( tempFile ) :
			if os.stat( tempFile )[stat.ST_SIZE] == aPVS.mSize :
				self.mIsDownload = True
				return True

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Resume downloading files' ), MR_LANG( 'Continue interrupted downloads?' ) )
			dialog.doModal( )

			ret = dialog.IsOK( )
			if ret == E_DIALOG_STATE_CANCEL :
				return False

			elif ret == E_DIALOG_STATE_YES :
				isResume = True

		LOG_TRACE( '--------------reqFile[%s]'% reqFile )
		#self.ProgressDialog( isResume, reqFile, tempFile )
		self.ProgressNoDialog( isResume, reqFile, tempFile )

		self.mWorkingItem = None
		self.mWorkingDownloader = None
		time.sleep( 0.3 )

		return self.mIsDownload


	def ProgressDialog( self, aIsResume, aRemoteFile, aDestFile ) :
		self.mDialogProgress = xbmcgui.DialogProgress( )
		self.mDialogProgress.create( self.mWorkingItem.mName, MR_LANG( 'Waiting...' ) )

		LOG_TRACE( '--------------reqFile[%s]'% aRemoteFile )

		try :
			self.mWorkingDownloader = DownloadFile( aRemoteFile, aDestFile )
			if aIsResume :
				self.mWorkingDownloader.resume( self.ShowProgress )
			else :
				self.mWorkingDownloader.download( self.ShowProgress )

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )
			self.mIsCancel = False
			self.mIsDownload = False
			self.mStepPage = E_UPDATE_STEP_READY

		self.mDialogProgress.close( )
		self.mDialogProgress = None


	def ProgressNoDialog( self, aIsResume, aRemoteFile, aDestFile ) :
		#LOG_TRACE( '--------------reqFile[%s]'% aRemoteFile )
		self.mCancel_temp = False

		self.SetControlLabel2String( E_Input02, MR_LANG( 'Cancel' ) )
		self.EditDescription( E_Input02, MR_LANG( 'Press OK to cancel downloading firmware updates' ) )
		self.ShowDescription( E_Input02 )

		try :
			self.mWorkingDownloader = DownloadFile( aRemoteFile, aDestFile )
			if aIsResume :
				self.mWorkingDownloader.resume( self.ShowProgress2 )
			else :
				self.mWorkingDownloader.download( self.ShowProgress2 )

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )
			self.mIsCancel = False
			self.mIsDownload = False
			self.mStepPage = E_UPDATE_STEP_READY
			if self.mWorkingDownloader :
				self.mWorkingDownloader.abort( True )

			LOG_TRACE( '------download stop' )
			return


		if CheckDirectory( aDestFile ) and self.mWorkingItem and \
		   os.stat( aDestFile )[stat.ST_SIZE] == self.mWorkingItem.mSize :
			self.mIsDownload = True
			LOG_TRACE('-------------------------Isdownload[%s] size[%s] down[%s]'% ( self.mIsDownload, os.stat( aDestFile )[stat.ST_SIZE], self.mWorkingItem.mSize ) )

		"""
		else :
			LOG_TRACE( '------------------download fail, link[%s] cencel[%s]'% ( self.mLinkStatus, self.mCancel_temp ) )
			if self.mLinkStatus != True :
				thread = threading.Timer( 0.3, self.SetFailProcess, [E_STRING_CHECK_UNLINK_NETWORK] )
				thread.start( )
		"""

	def SetFailProcess( self, aFailNo ) :
		if aFailNo == E_STRING_CHECK_UNLINK_NETWORK :
			self.mIsCancel = False
			self.mIsDownload = False
			self.mStepPage = E_UPDATE_STEP_READY
			if self.mWorkingDownloader :
				self.mWorkingDownloader.abort( True )
			self.mWorkingDownloader = None

			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_UNLINK_NETWORK )

			msgLine = MR_LANG( 'Checking network status' )
			threadDialog = self.ShowProgressDialog( 30, msgLine, None, '' )
			self.OpenBusyDialog( )
			time.sleep( 30 )
			self.CloseBusyDialog( )
			if self.mShowProgressThread :
				self.mShowProgressThread.SetResult( True )
				self.mShowProgressThread = None

			if threadDialog :
				threadDialog.join( )


		elif aFailNo == E_STRING_CHECK_CENCEL :
			self.mIsCancel = True
			if self.mGetDownloadThread :
				self.mGetDownloadThread.join( )
			self.mGetDownloadThread = None
			self.SetControlLabel2String( E_Input02, MR_LANG( 'Download') )
			self.EditDescription( E_Input02, MR_LANG( 'Press OK button to download the firmware shown below' ) )
			self.ShowDescription( E_Input02 )
			LOG_TRACE( '------------cancel(download)' )


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
				self.mStepPage = E_UPDATE_STEP_READY
				LOG_TRACE( '--------------abort' )


	def ShowProgress2( self, cursize = 0 ) :
		if self.mWorkingItem.mSize :
			#per = 1.0 * cursize / self.mWorkingItem.mSize * 100
			percent = 1.0 * cursize / self.mWorkingItem.mSize * 100
			#self.mCtrlProgress.setPercent( percent )
			#self.mCtrlLabelPercent.setLabel( '{0:.2f}%(download)'.format( round( percent, 2 ) ) )
			self.SetLabelThread( percent )
			#LOG_TRACE('--------------down size[%s] per[%s] tot[%s]'% ( cursize, percent, self.mWorkingItem.mSize ) )

			if self.mWorkingDownloader and self.mIsCancel or \
			   self.mWorkingDownloader and self.mLinkStatus != True :
				self.mWorkingDownloader.abort( True )
				self.mCancel_temp = self.mIsCancel
				self.mIsCancel = False
				self.mIsDownload = False
				self.mStepPage = E_UPDATE_STEP_READY
				LOG_TRACE( '--------------abort(download)' )


	@RunThread
	def SetLabelThread( self, aPercent ) :
		if aPercent > 100 :
			aPercent = 100
		self.mCtrlProgress.setPercent( aPercent )
		self.mCtrlLabelPercent.setLabel( '%s%% %s'% ( '{0:.2f}'.format( round( aPercent, 2 ) ), MR_LANG( 'downloaded' ) ) )


	def VerifiedUnPack( self, aZipFile, aShowProgress = True ) :
		fileList = GetUnpackFiles( aZipFile )
		if not fileList or len( fileList ) < 1 :
			return False

		unpackPath = E_DEFAULT_PATH_DOWNLOAD
		if E_UPDATE_FIRMWARE_USE_USB :
			unpackPath = self.mDataCache.USB_GetMountPath( )

		if not unpackPath :
			return False

		#self.OpenBusyDialog( )
		if aShowProgress :
			dialogProgress = xbmcgui.DialogProgress( )
			dialogProgress.create( self.mPVSData.mName, MR_LANG( 'Verifying...' ) )

		isVerify = True
		totalFiles = len( fileList )
		idx = 0
		for item in fileList :
			idx += 1
			if aShowProgress :
				dialogProgress.update( int( 1.0 * idx / totalFiles * 100 ) )
			unpackFile = '%s/%s'% ( unpackPath, item[1] )
			iFileMD5 = GetUnpackByMD5( unpackFile )
			iRealMD5 = CheckMD5Sum( unpackFile )
			LOG_TRACE( '--------------verify check file[%s] get[%s] md5[%s]'% ( unpackFile, iFileMD5, iRealMD5 ) )
			if not iFileMD5 or not iRealMD5 or iFileMD5 != iRealMD5 :
				LOG_TRACE( '--------------verify err file[%s] get[%s] md5[%s]'% ( unpackFile, iFileMD5, iRealMD5 ) )
				isVerify = False
				break

			if aShowProgress and dialogProgress.iscanceled( ) :
				LOG_TRACE( '--------------abort(verified)' )
				isVerify = False
				break

			time.sleep( 0.2 )

		if aShowProgress :
			dialogProgress.close( )

		#self.CloseBusyDialog( )
		time.sleep( 0.3 )

		return isVerify


	#--deprecated, old check
	def VerifiedUnPack_Old( self, aZipFile, aShowProgress = True ) :
		fileList = GetUnpackFiles( aZipFile )
		if not fileList :
			return False

		unpackPath = E_DEFAULT_PATH_DOWNLOAD
		if E_UPDATE_FIRMWARE_USE_USB :
			unpackPath = self.mDataCache.USB_GetMountPath( )

		if not unpackPath :
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
				dialogProgress.update( int( 1.0 * idx / totalFiles * 100 ) )
			unpackFile = '%s/%s'% ( unpackPath, item[1] )
			unpackSize = GetFileSize( unpackFile )
			if item[0] != unpackSize :
				LOG_TRACE( '--------------verify err pack[%s] unPack[%s] file[%s]'% ( item[0], unpackSize, unpackFile ) )
				isVerify = False
				break

			if aShowProgress and dialogProgress.iscanceled( ) :
				LOG_TRACE( '--------------abort(verified)' )
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

			if self.mPlatform.GetXBMCVersion( ) < self.mPlatform.GetFrodoVersion( ) :
				#from pvr.IpParser import *

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
		#LOG_TRACE( 'mboxDir[%s]'% mboxDir )
		backupFileList = [  '%s/resources/settings.xml'% mboxDir,
							'%s/.xbmc/userdata/guisettings.xml'% E_DEFAULT_PATH_HDD 
						 ]
		try :
			CopyToFile( backupFileList[0], '%s/%s'% ( E_DEFAULT_BACKUP_PATH, os.path.basename( backupFileList[0] ) ) )
			if not CheckHdd( ) :
				CopyToFile( backupFileList[1], '%s/%s'% ( E_DEFAULT_BACKUP_PATH, os.path.basename( backupFileList[1] ) ) )

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )


		LOG_TRACE('4. preprocess.sh ------' )
		preprocessFile = '%s/preprocess.sh'% E_DEFAULT_BACKUP_PATH
		try :
			fd = open( preprocessFile, 'w' )

			if fd :
				if self.mPVSData and self.mPVSData.mActions :
					fd.writelines( '#!/bin/sh\n' )
					fd.writelines( '%s\n'% self.mPVSData.mActions )

				fd.close( )
				os.chmod( preprocessFile, 0755 )

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )


		LOG_TRACE('5. make run script ------' )
		try :
			scriptFile = '%s.sh'% E_DEFAULT_BACKUP_PATH
			fd = open( scriptFile, 'w' )
			if fd :
				fd.writelines( '#!/bin/sh\n' )
				fd.writelines( 'modprobe usb_storage\n' )
				fd.writelines( 'sleep 3\n' )
				fd.writelines( 'cp -f %s/%s %s\n'% ( E_DEFAULT_BACKUP_PATH, os.path.basename( backupFileList[0] ), backupFileList[0] ) )
				if not CheckHdd( ) :
					fd.writelines( 'cp -f %s/%s %s\n'% ( E_DEFAULT_BACKUP_PATH, os.path.basename( backupFileList[1] ), backupFileList[1] ) )

				if CheckDirectory( preprocessFile ) :
					fd.writelines( '%s\n'% preprocessFile )

				fd.close( )
				os.chmod( scriptFile, 0755 )

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )

		return


	def CheckCurrentVersion( self ) :
		lbldesc = ''
		try :
			iPVS = PVSClass( )
			ret = GetCurrentVersion( )
			if not ret[0] :
				ret[0] = MR_LANG( 'Unknown' )
			if not ret[1] :
				ret[1] = MR_LANG( 'Unknown' )
			
			iPVS.mVersion = ret[0]
			iPVS.mDate = ret[1]
			iPVS.mError = 0

			lbldesc += '%s : %s\n'% ( MR_LANG( 'Current Version' ), iPVS.mVersion )
			lbldesc += '%s : %s\n'% ( MR_LANG( 'Date' ), iPVS.mDate )
			#lbldesc += '%s\n%s\n'% ( MR_LANG( 'DESCRIPTION' ), iPVS.mDescription )

			self.mCurrData = iPVS

		except Exception, e :
			LOG_ERR( 'except[%s]'% e )
			lbldesc = MR_LANG( 'Unknown' )

		if self.mCurrData and not self.mCurrData.mVersion :
			lbldesc = MR_LANG( 'Unknown' )

		self.UpdatePropertyGUI( 'CurrentDescription', lbldesc )


	def UpdateChannelsByInternet( self ) :
		self.mChannelUpdateProgress = self.ChannelUpdateProgress( MR_LANG( 'Downloading server information' ), 20 )
		if self.DownloadInfoFile( ) == False :
			self.CloseProgress( )
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_CONNECT_ERROR )
			return

		makelist = self.ParseList( )

		if makelist == None :
			self.CloseProgress( )
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_CHANNEL_FAIL )
			return

		self.CloseProgress( )
		showtext = []
		for text in makelist :
			showtext.append( text[1] + '( ' + text[2] + ' )' )

		dialog = xbmcgui.Dialog( )
		ret = dialog.select( MR_LANG( 'Select a channel package' ), showtext )
		if ret >= 0 :
			result = self.GetChannelUpdate( makelist[ret][0] )
			if result :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG('Update complete'), MR_LANG('Your channel list has been updated successfully') )
				dialog.doModal( )
			else :
				self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_CHANNEL_FAIL )


	def ImportChannelsFromUSB( self ) :
		LOG_TRACE( '' )
		#check usb mount
		usbPath = self.mDataCache.USB_GetMountPath( )
		if not usbPath :
			LOG_TRACE( 'USB not found' )
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_USB_NOT )
			return

		xmlFullPathList = glob.glob( os.path.join( usbPath, 'updatechannel', '*.xml')  )

		LOG_TRACE( 'XML file countd=%d' %len(xmlFullPathList ) )

		if len( xmlFullPathList ) <= 0 :
 			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No channel file in %s directory' ) %('updatechannel' ) )
 			dialog.doModal( )
 			return

		xmlFileList = []
		for i in range( len( xmlFullPathList )  ):
			xmlFileList.append( os.path.basename( xmlFullPathList[i] ) )

		dialog = xbmcgui.Dialog( )
		select = dialog.select( MR_LANG( 'Select a channel list file' ), xmlFileList, False )

		if select >= 0 :
			#check usb file
			strFilename = xmlFileList[select]
			LOG_TRACE( 'select file name=%s' %strFilename )
			filePath = os.path.join( usbPath, 'updatechannel', strFilename )
			LOG_TRACE( 'UPDATE FILE PATH=%s' %filePath )
			if not os.path.exists( filePath ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG('Error'), '%s %s' %( MR_LANG( 'File not found' ), strFilename ) )
				dialog.doModal( )
				return

			self.mChannelUpdateProgress = self.ChannelUpdateProgress( MR_LANG( 'Now updating your channel list' ), 30 )
			shutil.copyfile( filePath, UPDATE_TEMP_CHANNEL )
			os.system( 'sync' )
		
			msgHead = MR_LANG( 'Update channels' )
			msgLine = ''
			ret = self.mCommander.System_SetManualChannelList( UPDATE_TEMP_CHANNEL )
			if ret == ElisEnum.E_UPDATE_SUCCESS :
				msgHead = MR_LANG( 'Update channels' )
				#msgLine = MR_LANG( 'Your channel list has been updated successfully' )
				msgLine = MR_LANG( 'Your system must be restarted%s in order to complete the update' )% NEW_LINE
				"""
				self.mDataCache.LoadAllSatellite( )
				self.mDataCache.LoadAllTransponder( )
				self.mTunerMgr.SyncChannelBySatellite( )
				self.mDataCache.Channel_ReLoad( )
				self.mDataCache.Player_AVBlank( False )
				os.remove( UPDATE_TEMP_CHANNEL )
				os.system( 'sync' )		
				"""

			else :
				if aEvent.mResult == ElisEnum.E_UPDATE_FAILED_BY_RECORD :
					msgLine = MR_LANG( 'Please try again after stopping the recordings' )
				elif aEvent.mResult == ElisEnum.E_UPDATE_FAILED_BY_TIMER :
					msgLine = MR_LANG( 'Please try again after deleting your timers first' )

			self.CloseProgress( )

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( msgHead, msgLine )
			dialog.doModal( )

			if ret == ElisEnum.E_UPDATE_SUCCESS :
				self.mDataCache.System_Reboot( )

	
	def ExportChannelsToUSB( self ) :
		LOG_TRACE( '' )
		#check usb mount
		usbPath = self.mDataCache.USB_GetMountPath( )
		if not usbPath :
			LOG_TRACE( 'Not Exist USB' )
			self.DialogPopup( E_STRING_ERROR, E_STRING_CHECK_USB_NOT )
			return

		#check usb file
		self.mChannelUpdateProgress = self.ChannelUpdateProgress( MR_LANG( 'Now updating your channel list' ), 30 )
		filePath = os.path.join( usbPath, 'updatechannel' )
		LOG_TRACE( 'UPDATE FILE PATH=%s' %filePath )
		if not os.path.exists( filePath ) :
			os.mkdir( filePath, 0777 )

		self.mCommander.System_ExportChannelList( UPDATE_TEMP_CHANNEL )
		os.system( 'sync' )

		localTime = self.mDataCache.Datetime_GetLocalTime( )
		strLocalTime = time.strftime('%d.%m.%Y_%H-%M', time.gmtime( localTime ) )
		strFilename = 'settings_%s.xml' %strLocalTime
	

		LOG_TRACE( 'settings filename=%s' %strFilename )

		filePath = os.path.join( usbPath, 'updatechannel', strFilename )
		if os.path.exists( filePath ) :
			LOG_TRACE( 'already exist file=%s' %filePath )		
			for i in range( 10 ) :
				strLocalTime = time.strftime('%d%m%Y_%H-%M', time.gmtime( localTime ) )
				strFilename = 'settings_%s_%d.xml' %(strLocalTime, i + 1 )
				filePath = os.path.join( usbPath, 'updatechannel', strFilename )				
				if os.path.exists( filePath ) == False :
					break
				else :
					LOG_TRACE( 'already exist file=%s' %filePath )						

		LOG_TRACE( 'update file=%s' %filePath )

		shutil.copyfile( UPDATE_TEMP_CHANNEL, filePath )
		os.system( 'sync' )

		os.remove( UPDATE_TEMP_CHANNEL )
		os.system( 'sync' )		
		
		self.CloseProgress( )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( MR_LANG('Export complete'), MR_LANG('Your channel list has been exported successfully') )
		dialog.doModal( )


	def ParseList( self ) :
		try :
			try :
				import xml.etree.cElementTree as ElementTree
			except Exception, e :
				from elementtree import ElementTree

			tree = ElementTree.parse( '/mtmp/channel.xml' )
			root = tree.getroot( )

			makelist = []
			templist = []

			for channellist in root.findall( 'channellist' ) :
				templist = []
				name = channellist.find( 'name' ).text
				date = channellist.find( 'date' ).text
				key = channellist.find( 'key' ).text
				templist.append( key )
				templist.append( name )
				templist.append( date )

				makelist.append( templist )

			if len( makelist ) != 0 :
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
			self.mCommander.System_SetManualChannelList( '/mtmp/defaultchannel.xml' )
			self.mDataCache.LoadAllSatellite( )
			self.mDataCache.LoadAllTransponder( )
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
			output = open( '/mtmp/defaultchannel.xml', 'wb' )
			output.write( updatefile.read( ) )
			output.close( )
			return True
		except Exception, e :
			LOG_TRACE( 'Error exception[%s]' % e )
			return False


	def DownloadInfoFile( self ) :
		try :
			import urllib2
			updatefile = urllib2.urlopen( E_DEFAULT_CHANNEL_LIST, None, 20 )
			output = open( '/mtmp/channel.xml', 'wb' )
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

