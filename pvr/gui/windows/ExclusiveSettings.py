from pvr.gui.WindowImport import *
import shutil


E_PATH_MMC = '/media/mmc'
E_PATH_HDD = '/media/hdd0'
E_PATH_FLASH_BASE    = '/mnt/hdd0'
E_PATH_FLASH_PVR     = '%s/pvr'% E_PATH_FLASH_BASE
E_PATH_FLASH_PROGRAM = '%s/program'% E_PATH_FLASH_BASE

E_STORAGE_DONE = 0
E_STORAGE_ERROR_NOT_MEDIA = -1
E_STORAGE_ERROR_MOUNT_TYPE = -3
E_STORAGE_ERROR_CANCEL = -4
E_STORAGE_ERROR_STORAGE = -5
E_STORAGE_ERROR_FORMAT = -6
E_STORAGE_ERROR_SPACE = -7
E_STORAGE_ERROR_COPY_FAIL = -8
E_STORAGE_ERROR_NOT_USB = -9

E_CONTEXT_MENU_FORMAT = 1
E_CONTEXT_MENU_STORAGE = 2
E_STORAGE_FORMAT_SD = 1
E_STORAGE_FORMAT_HDD = 3

E_FORMAT_BY_REBOOT = 0
E_FORMAT_BY_NOT_REBOOT = 1


class ExclusiveSettings( object ) :
	def __init__( self ) :
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.mSelectAction = -1


	def OpenBusyDialog( self ) :
		xbmc.executebuiltin( 'ActivateWindow(busydialog)' )


	def CloseBusyDialog( self ) :
		xbmc.executebuiltin( 'Dialog.Close(busydialog)' )


	def Configure( self, aMenu = E_CONTEXT_MENU_STORAGE ) :
		self.ShowContextMenu( aMenu )


	def GetContextSelected( self ) :
		return self.mSelectAction


	def GetContextMenu( self, aMenu ) :
		context = []

		if aMenu == E_CONTEXT_MENU_FORMAT :
			mmcsize, hddsize, hddmodel = GetMountExclusiveDevice( )
			SDExist = self.mCommander.MMC_MountCheck( )
			if SDExist :
				mLines = '%s(%s)'% ( MR_LANG( 'Micro SD Card' ), mmcsize )
				context.append( ContextItem( mLines, E_STORAGE_FORMAT_SD ) )

			if hddsize :
				mLines = '%s-%s(%s)'% ( MR_LANG( 'USB' ), hddmodel, hddsize )
				context.append( ContextItem( mLines, E_STORAGE_FORMAT_HDD ) )

		else :
			defSelect = ElisPropertyEnum( 'Xbmc Save Storage', self.mCommander ).GetProp( )
			deviceList = ElisPropertyEnum( 'Xbmc Save Storage', self.mCommander ).mProperty
			LOG_TRACE( '-------------------def ElisPropertyEnum[%s]'% deviceList[defSelect][1] )

			for i in range( len( deviceList ) ) :
				#if i == 2 :
				#	#'not support USB Stick'
				#	continue

				deviceName = deviceList[i][1]
				#if i == defSelect :
				#	selectItem = i + 1
				#	deviceName = '[COLOR ff2E2E2E]%s[/COLOR]'% deviceName
				context.append( ContextItem( deviceName, i ) )

		return context


	def ShowContextMenu( self, aMenu = E_CONTEXT_MENU_STORAGE ) :
		contextList = self.GetContextMenu( aMenu )

		selectAction = -1
		if contextList and len( contextList ) > 0 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( contextList )
	 		dialog.doModal( )

			selectAction = dialog.GetSelectedAction( )

		self.mSelectAction = selectAction
		if selectAction < 0 :
			LOG_TRACE( '[Exclusive] cancel, previous back' )
			return

		#if selectAction == defSelect :
		#	LOG_TRACE( '[Exclusive] pass, select same' )
		#	return

		LOG_TRACE( '--------------------select[%s]'% contextList[selectAction].mDescription )

		if aMenu == E_CONTEXT_MENU_FORMAT :
			self.FormatStorage( selectAction, False )

		elif aMenu == E_CONTEXT_MENU_STORAGE :
			self.SelectStorage( selectAction )


	def FormatStorage( self, aSelect, aCheckDevice = True ) :
		isFail = False
		mTitle = MR_LANG( 'Error' )
		mLines = MR_LANG( 'Could not find a SD memory card' )

		if aSelect == E_STORAGE_FORMAT_SD :
			SDExist = True
			if aCheckDevice : 
				SDExist = self.mCommander.MMC_MountCheck( )

			if SDExist :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( MR_LANG( 'Format your SD memory card?' ), MR_LANG( 'Everything on your SD card will be erased' ) )
				dialog.doModal( )
				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					configure = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_CONFIGURE )
					configure.DedicatedFormat( E_STORAGE_FORMAT_SD )

			else :
				isFail = True

		elif aSelect == E_STORAGE_FORMAT_HDD :
			driveList = self.mCommander.USB_GetMountPath( )
			if driveList and len( driveList ) > 0 and driveList[0].mError == 0 :
				context = []
				for i in range( len( driveList ) ) :
					context.append( ContextItem( driveList[i].mParam, i ) )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
				dialog.SetProperty( context )
				dialog.doModal( )
				contextAction = dialog.GetSelectedAction( )
				if contextAction >= 0 :
					self.mSelectAction = contextAction
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_CONFIGURE ).StartExclusiveFormat( driveList, contextAction )

			else :
				isFail = True
				mLines = MR_LANG( 'Could not find a exclusive drive' )


		if isFail :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( mTitle, mLines )
			dialog.doModal( )



	def SelectStorage( self, aSelect ) :
		ret = False
		if aSelect == 0 :
			ret = E_STORAGE_DONE
		else :
			ret = self.ChangeStorage( aSelect )

		if ret == E_STORAGE_DONE :
			ElisPropertyEnum( 'Xbmc Save Storage', self.mCommander ).SetPropIndex( aSelect )
			LOG_TRACE( '--------------------Save ElisPropertyEnum[%s]'% aSelect )

		else :
			LOG_TRACE( '--------------------error[%s]'% ret )
			mTitle = MR_LANG( 'Error' )
			mLines = ''
			if ret == E_STORAGE_ERROR_SPACE :
				mLines = MR_LANG( 'Not enough space on USB flash memory' )
			elif ret == E_STORAGE_ERROR_NOT_MEDIA :
				mLines = MR_LANG( 'Check your USB device' )
			elif ret == E_STORAGE_ERROR_MOUNT_TYPE :
				mLines = MR_LANG( 'Unknown filesystem or not formated' )
			elif ret == E_STORAGE_ERROR_STORAGE :
				mLines = MR_LANG( 'Can not appoint storage' )
			elif ret == E_STORAGE_ERROR_FORMAT :
				mLines = MR_LANG( 'Format drive fail to complete' )
			elif ret == E_STORAGE_ERROR_COPY_FAIL :
				mLines = MR_LANG( 'Fail to copy addons' )
			elif ret == E_STORAGE_ERROR_CANCEL :
				mTitle = MR_LANG( 'Attention' )
				mLines = MR_LANG( 'storage appointment is canceled' )
			elif ret == E_STORAGE_ERROR_NOT_USB :
				mLines = MR_LANG( 'Not support USB memory' )

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( mTitle, mLines )
			dialog.doModal( )


	def ChangeStorage( self, aSelect ) :
		mediaPath = E_PATH_MMC
		if aSelect == 3 :
			mediaPath = E_PATH_HDD

		elif aSelect == 2 :
			return E_STORAGE_ERROR_NOT_USB

		if not CheckDirectory( mediaPath ) :
			return E_STORAGE_ERROR_NOT_MEDIA

		mTitle = MR_LANG( 'Error' )
		mLines = MR_LANG( 'Changed Fail to Storage' )
		isChanged = E_STORAGE_DONE

		try :
			mType = CheckMountType( mediaPath ).lower( )
			if mType :
				isFormat = False
				isCopyData = True

				if mType == 'ext4' :
					xbmcPath = '%s/%s/.xbmc'% ( mediaPath, os.path.dirname( E_PATH_FLASH_PROGRAM ) )
					if CheckDirectory( xbmcPath ) :
						mTitle = MR_LANG( 'Attention' )
						mLines = MR_LANG( 'Can you remove old addons in Micro SD Card?' )
						if aSelect == 3 :
							mLines = MR_LANG( 'Can you remove old addons in USB HDD?' )
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
						dialog.SetDialogProperty( mTitle, mLines )
						dialog.doModal( )

						ret = dialog.IsOK( )
						if ret == E_DIALOG_STATE_CANCEL :
							isChanged = E_STORAGE_ERROR_CANCEL

						elif ret == E_DIALOG_STATE_YES :
							RemoveDirectory( xbmcPath )

						else :
							isCopyData = False

				else :
					#vfat, ntfs, ... etc
					isFormat = False

					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
					dialog.SetDialogProperty( MR_LANG( 'Format your drive?' ), MR_LANG( 'Everything on your drive will be erased' ), MR_LANG( 'This will take a while' ) )
					dialog.doModal( )
					if dialog.IsOK( ) == E_DIALOG_STATE_YES :
						isFormat = True
					elif dialog.IsOK( ) == E_DIALOG_STATE_NO :
						isChanged = E_STORAGE_ERROR_STORAGE
					else :
						isChanged = E_STORAGE_ERROR_CANCEL

				if isChanged == E_STORAGE_DONE :
					#copy to data
					isChanged = self.CopyXBMCData( mediaPath, isCopyData, isFormat )

			else :
				#check except
				isChanged = E_STORAGE_ERROR_MOUNT_TYPE

		except Exception, e :
			LOG_ERR( '[Storage]except[%s]'% e )
			isChanged = E_STORAGE_ERROR_STORAGE

		return isChanged


	def CopyXBMCData( self, aMediaPath, isCopyData = True, isFormat = False ) :
		if isFormat :
			self.OpenBusyDialog( )
			self.mProcessing = True
			tShowProcess = threading.Timer( 0, self.AsyncProgressing )
			tShowProcess.start( )

			ret = False
			if mediaPath == E_PATH_MMC :
				ret = self.mCommander.Format_Micro_Card( E_FORMAT_BY_NOT_REBOOT )
			elif mediaPath == E_PATH_HDD :
				ret = self.mCommander.Make_Exclusive_HDD( mediaPath )

			self.mProcessing = False
			if tShowProcess :
				tShowProcess.join( )
			self.CloseBusyDialog( )
			if not ret :
				return E_STORAGE_ERROR_FORMAT

		if not isCopyData :
			return E_STORAGE_DONE

		ret = E_STORAGE_DONE
		sourceSize = GetDirectorySize( E_PATH_FLASH_PVR ) + GetDirectorySize( E_PATH_FLASH_PROGRAM )
		targetSize = GetDeviceSize( aMediaPath )
		LOG_TRACE( '---------------size /media/mmc[%s] /mnt/hdd0[%s]'% ( targetSize, sourceSize ) )
		if targetSize < sourceSize :
			return E_STORAGE_ERROR_SPACE

		self.OpenBusyDialog( )
		pathlist = GetDirectoryAllFilePathList( [ E_PATH_FLASH_BASE ], ['%s/download'% E_PATH_FLASH_PROGRAM] )
		self.CloseBusyDialog( )
		progressDialog = None
		try :
			strInit = MR_LANG( 'Initializing process' ) + '...'
			strReady = MR_LANG( 'Ready to start' ) + '...'
			percent = 0
			progressDialog = xbmcgui.DialogProgress( )
			progressDialog.create( MR_LANG( 'XBMC Data Copy' ), strInit )
			progressDialog.update( percent, strReady )

			count = 1
			totlen = len( pathlist )
			for sourcePath in pathlist :
				percent = int( 1.0 * count / totlen * 100 )

				if progressDialog.iscanceled( ) :
					strCancel = MR_LANG( 'Canceling' ) + '...'
					progressDialog.update( percent, strCancel )
					self.OpenBusyDialog( )
					RemoveDirectory( '%s/%s'% ( aMediaPath, os.path.dirname( E_PATH_FLASH_PVR ) ) )
					RemoveDirectory( '%s/%s'% ( aMediaPath, os.path.dirname( E_PATH_FLASH_PROGRAM ) ) )
					self.CloseBusyDialog( )
					progressDialog.update( 0, '', '' )
					progressDialog.close( )
					return E_STORAGE_ERROR_CANCEL

				strData = MR_LANG( 'Copying data' ) + '...'
				progressDialog.update( percent, strData, '%s'% sourcePath[len(E_PATH_FLASH_BASE)+1:], ' ' )

				destPathCopy = '%s%s'% ( aMediaPath, sourcePath[ len( E_PATH_FLASH_BASE ) : ] )
				if CheckDirectory( sourcePath, True ) :
					CreateDirectory( destPathCopy, sourcePath )

				else :
					shutil.copy( sourcePath, destPathCopy )
					#os.system( 'cp -af %s %s'% ( sourcePath, destPathCopy ) )
				if not CheckDirectory( destPathCopy ) :
					os.system( 'sync' )
				count = count + 1

			os.system( 'sync' )
			progressDialog.update( 100, MR_LANG( 'XBMC Data Copy' ), MR_LANG( 'Complete' ) )
			time.sleep( 1 )
			progressDialog.update( 0, '', '' )
			progressDialog.close( )

		except Exception, e :
			LOG_ERR( '[Storage]except[%s]' % e )
			RemoveDirectory( '%s/%s'% ( aMediaPath, os.path.dirname( E_PATH_FLASH_PVR ) ) )
			RemoveDirectory( '%s/%s'% ( aMediaPath, os.path.dirname( E_PATH_FLASH_PROGRAM ) ) )
			if progressDialog :
				progressDialog.close( )
			self.CloseBusyDialog( )
			ret = E_STORAGE_ERROR_COPY_FAIL

		return ret


	def AsyncProgressing( self, aWaitTime = 10 ) :
		mTitle = MR_LANG( 'Format Micro SD' )
		strReady = MR_LANG( 'Ready to start' ) + '...'
		strInit = ''
		percent = 0
		progressDialog = xbmcgui.DialogProgress( )
		progressDialog.create( mTitle, strInit )
		progressDialog.update( percent, strReady )

		totalTime = 60 * aWaitTime
		waitCount = 0
		while self.mProcessing :
			strInit = '%s.'% strInit
			percent = waitCount / totalTime
			if percent > 99 :
				percent = 99
			progressDialog.update( percent, mTitle, strInit, ' ' )

			waitCount += 1
			time.sleep( 1 )

		progressDialog.update( 100, mTitle, MR_LANG( 'Complete' ) )
		time.sleep( 1 )
		progressDialog.update( 0, '', '' )
		progressDialog.close( )


	def DedicatedFormat( self, aType ) :
		self.mUseUsbBackup = False
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( MR_LANG( 'Backup data?' ), MR_LANG( 'To backup your user data and XBMC add-ons,%s insert a USB flash memory' ) % NEW_LINE )
		dialog.doModal( )
		if dialog.IsOK( ) == E_DIALOG_STATE_YES :
			if CheckDirectory( '/mnt/hdd0/program/.xbmc/userdata' ) and CheckDirectory( '/mnt/hdd0/program/.xbmc/addons' ) :
				self.BackupAndFormat( aType )
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Could not find backup data' ) )
				dialog.doModal( )
		else :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Start formatting without making a backup?' ), MR_LANG( 'Formatting HDD cannot be undone!' ) )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.MakeDedicate( aType )


	def BackupAndFormat( self, aType ) :
		usbpath = self.mDataCache.USB_GetMountPath( )
		if usbpath :
			size_addons = GetDirectorySize( '/mnt/hdd0/program/.xbmc/addons' )
			size_udata = GetDirectorySize( '/mnt/hdd0/program/.xbmc/userdata' )
			usbfreesize = GetDeviceSize( usbpath )
			if ( size_addons + size_udata ) > usbfreesize :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Not enough space on USB flash memory' ) )
				dialog.doModal( )
			else :
				self.CopyBackupData( usbpath, aType )
		else :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Please insert a USB flash memory' ) )
			dialog.doModal( )


	def CopyBackupData( self, aUsbpath, aType ) :
		self.mProgressThread = self.ShowProgress( '%s%s' % ( MR_LANG( 'Now backing up your user data' ), ING ), 30 )
		if CheckDirectory( aUsbpath + '/RubyBackup/' ) :
			RemoveDirectory( aUsbpath + '/RubyBackup/' )

		ret_udata = CopyToDirectory( '/mnt/hdd0/program/.xbmc/userdata', aUsbpath + '/RubyBackup/userdata' )
		ret_addons = CopyToDirectory( '/mnt/hdd0/program/.xbmc/addons', aUsbpath + '/RubyBackup/addons' )
		if ret_udata and ret_addons :
			self.CloseProgress( )
			time.sleep( 0.5 )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Start formatting HDD?' ), MR_LANG( 'Press OK button to format your HDD now' ) )
			dialog.doModal( )
			self.mUseUsbBackup = True
			self.MakeDedicate( aType )
		else :
			self.CloseProgress( )
			time.sleep( 0.5 )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Data backup failed' ) )
			dialog.doModal( )


	def MakeDedicate( self, aType ) :
		if aType == FORMAT_HARD_DISK :
			maxsize = self.GetMaxMediaSize( )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Maximum Partition Size' ), MR_LANG( 'Maximum media partition size' ) + ' : %s GB' % maxsize )
			dialog.doModal( )

			mediadefault = 100
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( MR_LANG( 'Enter Media Partition Size in GB' ), '%s' % mediadefault , 4 )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				mediadefault = dialog.GetString( )

			if maxsize < int( mediadefault ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Partition size not valid' ) )
				dialog.doModal( )
				return

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Your Media Partition is %s GB' ) % mediadefault, MR_LANG( 'Start formatting HDD?' ) )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				self.OpenBusyDialog( )
				ElisPropertyInt( 'MediaRepartitionSize', self.mCommander ).SetProp( int( mediadefault ) * 1024 )
				ElisPropertyEnum( 'HDDRepartition', self.mCommander ).SetProp( 1 )
				self.mDataCache.Player_AVBlank( True )
				if self.mUseUsbBackup :
					self.MakeBackupScript( )
					CreateDirectory( E_DEFAULT_BACKUP_PATH )
					os.system( 'touch %s/isUsbBackup' % E_DEFAULT_BACKUP_PATH )
				self.mCommander.Make_Dedicated_HDD( )
		else :
			self.OpenBusyDialog( )
			self.mDataCache.Player_AVBlank( True )
			if self.mUseUsbBackup :
				self.MakeBackupScript( )
				CreateDirectory( E_DEFAULT_BACKUP_PATH )
				os.system( 'touch %s/isUsbBackup' % E_DEFAULT_BACKUP_PATH )
			self.mCommander.Format_Micro_Card( )

