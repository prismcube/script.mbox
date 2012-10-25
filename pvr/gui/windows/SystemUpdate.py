from pvr.gui.WindowImport import *
from fileDownloader import DownloadFile

E_TYPE_PRISMCUBE = 1
E_TYPE_ADDONS = 2

E_DEFAULT_URL_PVS = 'http://192.168.100.142/RSS/update.xml'
E_DEFAULT_DIRECTORY_DOWNLOAD = '/mnt/hdd0/program/download'

E_CONTROL_ID_GROUP_PVS         = 49
E_CONTROL_ID_LIST_PVS          = 50
E_CONTROL_ID_LABEL_DATE        = 100
E_CONTROL_ID_LABEL_VERSION     = 101
E_CONTROL_ID_LABEL_SIZE        = 102
E_CONTROL_ID_LABEL_DESCRIPTION = 103

E_STRING_DATE        = MR_LANG( 'DATE' )
E_STRING_VERSION     = MR_LANG( 'VERSION' )
E_STRING_SIZE        = MR_LANG( 'SIZE' )
E_STRING_DESCRIPTION = MR_LANG( 'DESCRIPTION' )

CONTEXT_ACTION_REFRESH_CONNECT      = 1
CONTEXT_ACTION_CHANGE_ADDRESS       = 2
CONTEXT_ACTION_LOAD_DEFAULT_ADDRESS = 3

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

		self.mUrlPVS = E_DEFAULT_URL_PVS
		self.mListItems = None
		self.mPVSList = []
		self.SetSettingWindowLabel( MR_LANG( 'Update' ) )

		self.SetPipScreen( )
		self.LoadNoSignalState( )

		self.mUrlPVS = GetSetting( 'UpdateServer' )
		IsState = self.Provisioning( )

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


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.mIsCloseing = False
			self.Close( )
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mIsCloseing = False
			self.Close( )

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_MOVE_DOWN :
			self.UpdatePVSInfo( )

		elif actionId == Action.ACTION_CONTEXT_MENU :
			self.ShowContextMenu( )


	def onClick( self, aControlId ) :
		if aControlId == E_CONTROL_ID_LIST_PVS :
			self.DownloadHandler( )


	def onFocus( self, aControlId ) :
		pass


	def CheckNoChannel( self ) :
		if self.mDataCache.Channel_GetList( ) :
			return True
		else :
			return False


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
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_DATE, '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_VERSION, '' )
		self.UpdateControlGUI( E_CONTROL_ID_LABEL_SIZE, '' )
		self.UpdatePropertyGUI( 'DescriptionTitle', '' )
		self.UpdatePropertyGUI( 'UpdateDescription', '' )


	def UpdatePVSInfo( self ) :
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

		for iPVS in self.mPVSList :
			listItem = xbmcgui.ListItem( '%s'% iPVS.mName, '%s'% iPVS.mDate )
			self.mListItems.append( listItem )

		self.UpdateControlGUI( E_CONTROL_ID_LIST_PVS, self.mListItems, E_TAG_ADD_ITEM )
		self.UpdatePVSInfo( )


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
			appURL        = ParseStringInXML( download, 'application' )

			description = ''
			descList = ParseStringInXML( download, 'description' )
			LOG_TRACE( 'desc[%s]'% descList )

			if descList and len( descList ) > 0 :
				for item in descList :
					description += '%s\n'% item
			iPVS.mDescription = description

			self.mPVSList.append( iPVS )

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
			self.Provisioning( )

		elif aContextAction == CONTEXT_ACTION_CHANGE_ADDRESS :
			self.SetChangeServerURL( )

		elif aContextAction == CONTEXT_ACTION_LOAD_DEFAULT_ADDRESS :
			self.mUrlPVS = E_DEFAULT_URL_PVS
			SetSetting( 'UpdateServer', '%s'% E_DEFAULT_URL_PVS )
			self.Provisioning( )


	def SetChangeServerURL( self ) :
		label = MR_LANG( 'Repair Server Address' )
		kb = xbmc.Keyboard( self.mUrlPVS, label, False )
		kb.doModal( )

		repairUrl = ''
		repairUrl = kb.getText( )
		if not repairUrl :
			return

		self.mUrlPVS = repairUrl
		self.Provisioning( )


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


	def DownloadHandler( self ) :
		LOG_TRACE('----------------list[%s]'% self.mPVSList )
		if self.mPVSList == None or len( self.mPVSList ) < 1 :
			return

		idx = self.mCtrlListPVS.getSelectedPosition( )
		iPVS = self.mPVSList[idx]
		LOG_TRACE('----------------download[%s]'% iPVS.mFileName )

		#ToDo : usb detected
		self.GetDownload( iPVS )

		if iPVS.mType == E_TYPE_PRISMCUBE :
			pass
			#toDo


	def GetDownload( self, aPVS ) :
		isStable = GetURLpage( aPVS.mFileName, False )

		if not isStable :
			return


		#self.mDialogProgress = None
		self.mDialogProgress = xbmcgui.DialogProgress( )
		self.mDialogProgress.create( aPVS.mName, MR_LANG( 'Downloading...' ) )

		LOG_TRACE('-----------hold check-----------------------TTTTTTTTTTTTTTTTTTT')
		self.mWorkingItem = aPVS
		self.mWorkingDownloader = None


		#make tempDir, write local file
		CreateDirectory( E_DEFAULT_DIRECTORY_DOWNLOAD )
		LOG_TRACE('-----------hold check-----------------------TTTTTTTTTTTTTTTTTTT')
		tempFile = E_DEFAULT_DIRECTORY_DOWNLOAD + '/%s' + os.path.basename( aPVS.mFileName )
		LOG_TRACE('-----------hold check-----------------------TTTTTTTTTTTTTTTTTTT')
		self.mWorkingDownloader = DownloadFile( aPVS.mFileName, tempFile )
		LOG_TRACE('-----------hold check-----------------------TTTTTTTTTTTTTTTTTTT')
		if os.path.exists( tempFile ) :
			self.mWorkingDownloader.resume( self.ShowProgress )
		else :
			self.mWorkingDownloader.download( self.ShowProgress )


		LOG_TRACE('-----------hold check-----------------------TTTTTTTTTTTTTTTTTTT')
		self.mDialogProgress.close( )
		#RemoveDirectory( E_DEFAULT_DIRECTORY_DOWNLOAD )
		self.mDialogProgress = None
		self.mWorkingItem = None
		self.mWorkingDownloader = None


	def ShowProgress( self, cursize = 0 ) :
		if cursize :
			LOG_TRACE('--------------down size[%s]'% cursize )

		if self.mDialogProgress and self.mWorkingItem.mSize :
			per = ( cursize / self.mWorkingItem.mSize ) * 100
			LOG_TRACE('--------------down size[%s] per[%s] tot[%s]'% ( cursize, per, self.mWorkingItem.mSize ) )

			self.mDialogProgress.update( ( cursize / self.mWorkingItem.mSize ) * 100 )

			if self.mDialogProgress.iscanceled( ) and self.mWorkingDownloader :
				self.mWorkingDownloader.abort( True )
				LOG_TRACE('--------------abort')


	def Close( self ) :
		self.SaveAsServerAddress( )
		self.SetVideoRestore( )
		WinMgr.GetInstance( ).CloseWindow( )



