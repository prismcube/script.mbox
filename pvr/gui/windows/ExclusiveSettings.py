from pvr.gui.WindowImport import *
import pvr.DataCacheMgr
import shutil


E_STORAGE_DONE = 0
E_STORAGE_FORMAT_DONE = 1

E_STORAGE_ERROR_NOT_MEDIA = -1
E_STORAGE_ERROR_MOUNT_TYPE = -2
E_STORAGE_ERROR_CANCEL = -3
E_STORAGE_ERROR_STORAGE = -4
E_STORAGE_ERROR_SPACE = -5
E_STORAGE_ERROR_COPY_FAIL = -6
E_STORAGE_ERROR_NOT_SUPPORT_STORAGE = -7
E_STORAGE_ERROR_NOT_USB = -8
E_STORAGE_ERROR_NOT_MMC = -9
E_STORAGE_ERROR_NOT_HDD = -10
E_STORAGE_ERROR_USED_MMC = -11
E_STORAGE_ERROR_USED_HDD = -12
E_STORAGE_ERROR_NOT_USB_AVAIL = -13
E_STORAGE_ERROR_USB_INSERT = -14
E_STORAGE_ERROR_RESTORE_FAIL = -15
E_STORAGE_ERROR_FORMAT = -16
E_STORAGE_ERROR_FORMAT_CANCEL = -17
E_STORAGE_ERROR_FORMAT_NOT_FOUND = -18
E_STORAGE_ERROR_USED_INTERNAL = -19
E_STORAGE_ERROR_TRY_AGAIN = -20


E_CONTEXT_MENU_FORMAT = 1
E_CONTEXT_MENU_STORAGE = 2

E_SELECT_STORAGE_NONE = 0
E_SELECT_STORAGE_MMC = 1
E_SELECT_STORAGE_USB = 2
E_SELECT_STORAGE_HDD = 3

E_FORMAT_MED_USB = 0
E_FORMAT_MED_MMC = 1
E_FORMAT_MNT_MMC = 2
E_FORMAT_MED_HDD = 3
E_FORMAT_MNT_HDD = 4

E_FORMAT_BY_REBOOT = 0
E_FORMAT_BY_NOT_REBOOT = 1


class ExclusiveSettings( object ) :
	def __init__( self ) :
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.mDataCache = pvr.DataCacheMgr.GetInstance( )
		self.mSelectAction = -1
		self.mFormatToSelectHDD = False
		self.mSelectDeviceList = []


	def OpenBusyDialog( self ) :
		xbmc.executebuiltin( 'ActivateWindow(busydialog)' )


	def CloseBusyDialog( self ) :
		xbmc.executebuiltin( 'Dialog.Close(busydialog)' )


	def Configure( self, aMenu = E_CONTEXT_MENU_STORAGE ) :
		self.ShowContextMenu( aMenu )


	def GetContextSelected( self ) :
		return self.mSelectAction


	def ResultDialog( self, aErrorNo ) :
		LOG_TRACE( '--------------------Error[%s]'% aErrorNo )
		mTitle = MR_LANG( 'Error' )
		mLines = ''
		if aErrorNo == E_STORAGE_DONE :
			mTitle = MR_LANG( 'Format Device' )
			mLines = MR_LANG( 'Done' )
		elif aErrorNo == E_STORAGE_FORMAT_DONE :
			mTitle = MR_LANG( 'Format Device' )
			mLines = MR_LANG( 'Complete' )
		elif aErrorNo == E_STORAGE_ERROR_FORMAT_CANCEL :
			mTitle = MR_LANG( 'Format Device' )
			mLines = MR_LANG( 'Cancelled' )
		elif aErrorNo == E_STORAGE_ERROR_CANCEL :
			mTitle = MR_LANG( 'Change Storage' )
			mLines = MR_LANG( 'Cancelled' )
		elif aErrorNo == E_STORAGE_ERROR_SPACE :
			mLines = MR_LANG( 'Not enough space on USB stick' )
		elif aErrorNo == E_STORAGE_ERROR_USB_INSERT :
			mLines = MR_LANG( 'Please insert an USB stick' )
		elif aErrorNo == E_STORAGE_ERROR_NOT_USB_AVAIL :
			mLines = MR_LANG( 'Check your USB device' )
		elif aErrorNo == E_STORAGE_ERROR_NOT_USB :
			mLines = MR_LANG( 'No USB stick found' )
		elif aErrorNo == E_STORAGE_ERROR_NOT_MMC :
			mLines = MR_LANG( 'No Micro SD found' )
		elif aErrorNo == E_STORAGE_ERROR_NOT_HDD :
			mLines = MR_LANG( 'No USB HDD found' )
		elif aErrorNo == E_STORAGE_ERROR_MOUNT_TYPE :
			mLines = MR_LANG( 'Unknown filesystem or Not formatted device' )
		elif aErrorNo == E_STORAGE_ERROR_STORAGE :
			mLines = MR_LANG( 'Storage device not changed' )
		elif aErrorNo == E_STORAGE_ERROR_FORMAT :
			mLines = MR_LANG( 'Failed to format device' )
		elif aErrorNo == E_STORAGE_ERROR_COPY_FAIL :
			mLines = MR_LANG( 'Failed to copy XBMC addons' )
		elif aErrorNo == E_STORAGE_ERROR_RESTORE_FAIL :
			mLines = MR_LANG( 'Failed to restore data' )
		elif aErrorNo == E_STORAGE_ERROR_NOT_SUPPORT_STORAGE :
			mLines = MR_LANG( 'Not supported device' )
		elif aErrorNo == E_STORAGE_ERROR_USED_MMC :
			mLines = MR_LANG( 'The device is already selected' )
		elif aErrorNo == E_STORAGE_ERROR_USED_HDD :
			mLines = MR_LANG( 'The device is already selected' )
		elif aErrorNo == E_STORAGE_ERROR_FORMAT_NOT_FOUND :
			mLines = MR_LANG( 'No device found' )
		elif aErrorNo == E_STORAGE_ERROR_USED_INTERNAL :
			mLines = MR_LANG( 'The device is already selected' )
		elif aErrorNo == E_STORAGE_ERROR_TRY_AGAIN :
			mLines = MR_LANG( 'Try again select a few second' )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( mTitle, mLines )
		dialog.doModal( )


	def InitDeviceList( self ) :
		devinfo = GetMountExclusiveDevice( )
		self.mDeviceList = deepcopy( devinfo )
		#LOG_TRACE( '-------------devinfo[%s]'% devinfo )
		devidx = 0
		context = []
		for ele in devinfo :
			mLines = '%s-%s(%s)'% ( MR_LANG( 'USB' ), ele[0], ele[1] )
			if ele[2] == '/dev/mmc' :
				mLines = '%s(%s)'% ( ele[0], ele[1] )

			mntPath = GetMountPathByDevice( -1, ele[2] )
			cmdFormat = -1
			if not mntPath :
				if bool( re.search( '/dev/mmc', ele[2], re.IGNORECASE ) ) :
					cmdFormat = E_FORMAT_MED_MMC
				elif bool( re.search( '/dev/sd', ele[2], re.IGNORECASE ) ) :
					cmdFormat = E_FORMAT_MED_HDD
					hddsize = GetMountExclusiveDevice( ele[2] )
					if int( hddsize ) < 100 * ( 1000000 * 1000 ) :
						cmdFormat = E_FORMAT_MED_USB
					#LOG_TRACE( '----------------------hddsize[%s] cmdFormat[%s]'% (hddsize,cmdFormat) )
			else :
				if mntPath == E_PATH_MMC :
					cmdFormat = E_FORMAT_MED_MMC
				elif mntPath == E_PATH_HDD :
					cmdFormat = E_FORMAT_MED_HDD
				elif mntPath == E_PATH_FLASH_BASE :
					if bool( re.search( '/dev/mmc', ele[2], re.IGNORECASE ) ) :
						cmdFormat = E_FORMAT_MNT_MMC
					elif bool( re.search( '/dev/sd', ele[2], re.IGNORECASE ) ) :
						cmdFormat = E_FORMAT_MNT_HDD
						hddsize = GetMountExclusiveDevice( ele[2] )
						if int( hddsize ) < 100 * ( 1000000 * 1000 ) :
							cmdFormat = E_FORMAT_MED_USB
						#LOG_TRACE( '----------------------hddsize[%s] cmdFormat[%s]'% (hddsize,cmdFormat) )

				else :
					if bool( re.search( '/dev/sd', ele[2], re.IGNORECASE ) ) :
						cmdFormat = E_FORMAT_MED_HDD
						hddsize = GetMountExclusiveDevice( ele[2] )
						if int( hddsize ) < 100 * ( 1000000 * 1000 ) :
							cmdFormat = E_FORMAT_MED_USB
						#LOG_TRACE( '----------------------hddsize[%s] cmdFormat[%s]'% (hddsize,cmdFormat) )

			self.mDeviceList[devidx].append( mntPath )
			self.mDeviceList[devidx].append( cmdFormat )
			context.append( ContextItem( mLines, devidx ) )
			devidx += 1

		return context


	def GetContextMenu( self, aMenu ) :
		context = []
		self.mDeviceList = []
		self.mDeviceListSelect = []

		if aMenu == E_CONTEXT_MENU_FORMAT :
			context = self.InitDeviceList( )

		else :
			defSelect = ElisPropertyEnum( 'Xbmc Save Storage', self.mCommander ).GetPropIndex( )

			context.append( ContextItem( MR_LANG('Internal Flash'), E_SELECT_STORAGE_NONE ) )
			context.append( ContextItem( MR_LANG('Micro SD'), E_SELECT_STORAGE_MMC ) )
			context.append( ContextItem( MR_LANG('USB Stick'), E_SELECT_STORAGE_USB ) )
			context.append( ContextItem( MR_LANG('USB HDD'), E_SELECT_STORAGE_HDD ) )

		return context


	def ShowContextMenu( self, aMenu = E_CONTEXT_MENU_STORAGE ) :
		contextList = self.GetContextMenu( aMenu )

		selectAction = -1
		if contextList and len( contextList ) > 0 :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( contextList )
	 		dialog.doModal( )

			selectAction = dialog.GetSelectedAction( )

		else :
			if aMenu == E_CONTEXT_MENU_FORMAT :
				self.ResultDialog( E_STORAGE_ERROR_FORMAT_NOT_FOUND )
				return

		self.mSelectAction = selectAction
		if selectAction < 0 :
			LOG_TRACE( '[Exclusive] Cancelled. Back to the previous window' )
			return

		#if selectAction == defSelect :
		#	return

		#LOG_TRACE( '--------------------select[%s]'% contextList[selectAction].mDescription )
		self.mSelectAction = selectAction
		if aMenu == E_CONTEXT_MENU_FORMAT :
			#mntPath = GetMountPathByDevice( -1, self.mDeviceList[selectAction][2] )
			self.mDeviceListSelect = self.mDeviceList[selectAction]
			self.FormatStorage( )

		elif aMenu == E_CONTEXT_MENU_STORAGE :
			self.SelectStorage( selectAction )


	def FormatStorage( self ) :
		isFail = E_STORAGE_FORMAT_DONE
		mTitle = MR_LANG( 'Error' )
		mLines = MR_LANG( 'Micro SD not found' )
		#LOG_TRACE( '-------------devlist[%s] selectList[%s]'% ( self.mDeviceList, self.mDeviceListSelect ) )

		if self.mDeviceListSelect :
			ret = self.DoFormatStorage( )
			self.ResultDialog( ret )

		#Unknown or not formatted
		return E_STORAGE_ERROR_FORMAT_NOT_FOUND


	def DoFormatStorage( self ) :
		isbackup = False
		isformat = False
		doResult = E_STORAGE_ERROR_FORMAT
		if not self.mDeviceListSelect :
			return doResult

		usbPath  = ''
		mntCmd = self.mDeviceListSelect[4]
		mntPath  = self.mDeviceListSelect[3]
		xbmcPath = '%s/program/.xbmc'% mntPath

		if mntCmd == E_FORMAT_MED_HDD :
			hddsize = GetMountExclusiveDevice( self.mDeviceListSelect[2] )
			if int( hddsize ) < 100 * ( 1000000 * 1000 ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( MR_LANG( 'Attention' ), MR_LANG( 'Detected into HDD, Are you sure?' ) )
				dialog.doModal( )
				if dialog.IsOK( ) != E_DIALOG_STATE_YES :
					return E_STORAGE_ERROR_TRY_AGAIN


		mTitle = MR_LANG( 'Format Device' )
		mLine1 = MR_LANG( 'Formatting will erase ALL data on this device' )
		mLine2 = MR_LANG( 'This will take a while' )

		if mntCmd == E_FORMAT_MED_MMC or mntPath == E_FORMAT_MNT_MMC :
			mLine2 = ''

		#1. Check .xbmc
		#if CheckMountType( aMntPath ).lower( ) == 'ext4' :
		"""
		if CheckDirectory( xbmcPath ) :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Backup data?' ), MR_LANG( 'To backup your user data and XBMC add-ons,%s insert a USB flash memory' ) % NEW_LINE )
			dialog.doModal( )
			ret = dialog.IsOK( )
			if ret == E_DIALOG_STATE_YES :
				isbackup = True

			elif ret == E_DIALOG_STATE_CANCEL :
				return E_STORAGE_ERROR_FORMAT_CANCEL
		"""

		#2. Backup XBMC data
		if isbackup :
			isformat = True
			usbPath = self.mDataCache.USB_GetMountPath( )
			if usbPath :
				if CheckDirectory( usbPath + '/RubyBackup/' ) :
					RemoveDirectory( usbPath + '/RubyBackup/' )
				CreateDirectory( usbPath + '/RubyBackup/' )

				sourceList = [ '%s/userdata'% xbmcPath, '%s/addons'% xbmcPath ]
				targetPath = '%s/RubyBackup'% usbPath
				doResult = self.CopyXBMCData( sourceList, targetPath, '', MR_LANG( 'Backup XBMC data' ), usbPath )
				if doResult != E_STORAGE_DONE :
					isformat = False

			else :
				isformat = False
				doResult = E_STORAGE_ERROR_USB_INSERT

		else :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( mTitle, mLine1, mLine2 )
			dialog.doModal( )
			ret = dialog.IsOK( ) == E_DIALOG_STATE_YES
			if ret == E_DIALOG_STATE_YES :
				isformat = True
			elif ret == E_DIALOG_STATE_NO :
				doResult = E_STORAGE_ERROR_FORMAT_CANCEL
			else :
				doResult = E_STORAGE_ERROR_FORMAT_CANCEL

		#3. Format
		if isformat :
			doResult = self.MakeDedicateForJET( )
			if doResult == E_STORAGE_DONE :
				#4. Restore backup data
				if isbackup :
					sourceList = [ '%s/RubyBackup/userdata'% usbPath, '%s/addons'% xbmcPath ]
					targetPath = xbmcPath
					doResult = self.CopyXBMCData( sourceList, targetPath, '', MR_LANG( 'Restore XBMC data' ), mntPath )
					if doResult == E_STORAGE_ERROR_COPY_FAIL :
						doResult = E_STORAGE_ERROR_RESTORE_FAIL

		return doResult


	def SelectStorage( self, aSelect ) :
		ret = self.ChangeStorage( aSelect )
		if ret == E_STORAGE_DONE :
			ElisPropertyEnum( 'Xbmc Save Storage', self.mCommander ).SetPropIndex( aSelect )
			#LOG_TRACE( '--------------------Save ElisPropertyEnum[%s]'% aSelect )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Restart Required' ), MR_LANG( 'Your system will reboot in %s seconds' )% 10, True )
			dialog.SetAutoCloseProperty( True, 10, True )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				"""
				msg1 = '%s%s'% ( MR_LANG( 'Your system will reboot in %s seconds' )% 5, ING )
				self.mDialogShowInit = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				self.mDialogShowInit.SetDialogProperty( MR_LANG( 'Restart Required' ), msg1 )
				self.mDialogShowInit.SetButtonVisible( False )
				self.mDialogShowInit.SetDialogType( 'update' )
				self.mDialogShowInit.SetAutoCloseTime( 5 )
				self.mDialogShowInit.doModal( )
				"""
				self.mDataCache.System_Reboot( )

		else :
			self.ResultDialog( ret )


	def ChangeStorage( self, aSelect ) :
		exceptList = [ '%s/download'% E_PATH_FLASH_PROGRAM ]
		sourceList = [ E_PATH_FLASH_PVR, E_PATH_FLASH_PROGRAM ]

		deviceHash = {}
		self.mDeviceList = []
		self.mDeviceListSelect = []
		self.InitDeviceList( )
		#LOG_TRACE( '------------------devList[%s]'% self.mDeviceList )
		for ele in self.mDeviceList :
			deviceHash[ele[4]] = ele

		hddpath = self.mDataCache.HDD_GetMountPath( )
		#LOG_TRACE( '-------------------------HDD_GetMountPath len[%s]'% len( hddpath ) )
		if aSelect == E_SELECT_STORAGE_MMC :
			mediaPath = E_PATH_MMC
			SDExist = self.mCommander.MMC_MountCheck( )
			if not SDExist :
				return E_STORAGE_ERROR_NOT_MMC

			if deviceHash.get( E_FORMAT_MED_MMC, -1 ) != -1 :
				self.mDeviceListSelect = deviceHash.get( E_FORMAT_MED_MMC, -1 )
			elif deviceHash.get( E_FORMAT_MNT_MMC, -1 ) != -1 :
				return E_STORAGE_ERROR_USED_MMC
			else :
				return E_STORAGE_ERROR_NOT_MMC

		elif aSelect == E_SELECT_STORAGE_USB :
			return E_STORAGE_ERROR_NOT_USB

		elif aSelect == E_SELECT_STORAGE_HDD :
			mediaPath = E_PATH_HDD
			mntPath = GetMountPathByDevice( -1, os.path.basename( E_PATH_FLASH_BASE ) )
			if mntPath == E_PATH_FLASH_BASE and hddpath and len( hddpath ) > 2 :
				return E_STORAGE_ERROR_USED_HDD

			if deviceHash.get( E_FORMAT_MED_HDD, -1 ) != -1 :
				self.mDeviceListSelect = deviceHash.get( E_FORMAT_MED_HDD, -1 )
			elif deviceHash.get( E_FORMAT_MNT_HDD, -1 ) != -1 :
				return E_STORAGE_ERROR_USED_HDD

			else :
				return E_STORAGE_ERROR_NOT_HDD

		else :
			defSelect = ElisPropertyEnum( 'Xbmc Save Storage', self.mCommander ).GetPropIndex( )
			LOG_TRACE( '-------------getProperty[%s] select[%s]'% (defSelect,aSelect ) )
			if aSelect == defSelect :
				return E_STORAGE_ERROR_USED_INTERNAL

			return E_STORAGE_DONE


		LOG_TRACE( '------------------devList[%s] selectList[%s]'% ( self.mDeviceList, self.mDeviceListSelect ) )

		mTitle = MR_LANG( 'Error' )
		mLines = MR_LANG( 'Failed to change storage device' )
		doResult = E_STORAGE_DONE

		if not self.mDeviceListSelect :
			return E_STORAGE_ERROR_STORAGE

		targetPath = ''
		devName = self.mDeviceListSelect[2]
		mediaPath = self.mDeviceListSelect[3]
		targetPath = mediaPath

		try :
			mType = CheckMountType( mediaPath ).lower( )
			#LOG_TRACE( '-------------------mountType[%s]'% mType )
			if mType :
				ret = mType.split( '\n' )
				if len( ret ) > 1 :
					mType = ret[0].strip( )
				if mType == 'ext4' or mType == 'vfat' :
					doResult = E_STORAGE_FORMAT_DONE
					xbmcPath = '%s/program/.xbmc'% mediaPath
					if CheckDirectory( xbmcPath ) :
						mTitle = MR_LANG( 'Installed XBMC addons' )
						mLines = MR_LANG( 'Do you want to copy your addons to Micro SD?' )
						if aSelect == E_SELECT_STORAGE_HDD :
							mLines = MR_LANG( 'Do you want to copy your addons to USB HDD?' )
						dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
						dialog.SetDialogProperty( mTitle, mLines )
						dialog.doModal( )

						ret = dialog.IsOK( )
						if ret == E_DIALOG_STATE_CANCEL :
							doResult = E_STORAGE_ERROR_CANCEL

						elif ret == E_DIALOG_STATE_YES :
							RemoveDirectory( xbmcPath )

						elif ret == E_DIALOG_STATE_NO :
							exceptList.append( '%s/.xbmc'% E_PATH_FLASH_PROGRAM )

				else :
					#vfat, ntfs, etc ...
					doResult = self.DoFormatStorage( )
					if doResult == E_STORAGE_ERROR_FORMAT_CANCEL :
						doResult = E_STORAGE_ERROR_CANCEL

				if doResult == E_STORAGE_DONE or doResult == E_STORAGE_FORMAT_DONE :
					#Copy XBMC data
					targetPath = GetMountPathByDevice( -1, devName )
					doResult = self.CopyXBMCData( sourceList, targetPath, exceptList )

			else :
				#Check exception
				doResult = E_STORAGE_ERROR_MOUNT_TYPE

		except Exception, e :
			LOG_ERR( '[Storage] Exception[%s]'% e )
			doResult = E_STORAGE_ERROR_STORAGE

		return doResult


	def CopyXBMCData( self, aSourceList, aTargetPath, aExceptList = [], aTitle = '', aTargetDevice = None ) :
		ret = E_STORAGE_DONE
		if not aSourceList or len( aSourceList ) < 1 :
			LOG_TRACE( '-------------------Nothing to copy[%s]'% aSourceList )
			return ret

		sourceSize = 0
		exceptSize = 0
		for sPath in aSourceList :
			sourceSize += GetDirectorySize( sPath )
		for ePath in aExceptList :
			exceptSize += GetDirectorySize( ePath )
		sourceSize -= exceptSize
		targetSize = GetDeviceSize( aTargetPath )
		if aTargetDevice :
			targetSize = GetDeviceSize( aTargetDevice )
		#LOG_TRACE( '---------------size target[%s][%s][%s] source[%s][%s] exceptList[%s:%s]'% ( targetSize, aTargetDevice, aTargetPath, sourceSize, aSourceList, exceptSize, aExceptList ) )
		if targetSize < sourceSize :
			return E_STORAGE_ERROR_SPACE

		copyList = []
		mTitle = MR_LANG( 'Copy XBMC Data' )
		if aTitle :
			mTitle = aTitle
		self.OpenBusyDialog( )
		pathlist = GetDirectoryAllFilePathList( aSourceList, aExceptList )
		self.CloseBusyDialog( )
		progressDialog = None
		try :
			strInit = MR_LANG( 'Initializing' ) + '...'
			strReady = MR_LANG( 'Ready' )
			percent = 0
			progressDialog = xbmcgui.DialogProgress( )
			progressDialog.create( mTitle, strInit )
			progressDialog.update( percent, strReady )

			count = 1
			totlen = len( pathlist )
			for fData in pathlist :
				percent = int( 1.0 * count / totlen * 100 )

				if progressDialog.iscanceled( ) :
					strCancel = MR_LANG( 'Cancelling' ) + '...'
					#progressDialog.update( percent, strCancel )
					self.OpenBusyDialog( )
					for sPath in aSourceList :
						RemoveDirectory( '%s/%s'% ( aTargetPath, sPath[len(E_PATH_FLASH_BASE)+1:] ) )
						#LOG_TRACE( '----------------------removePath[%s/%s]'% ( aTargetPath, sPath[len(E_PATH_FLASH_BASE)+1:] ) )

					#RemoveDirectory( '%s/%s'% ( aMediaPath, os.path.dirname( E_PATH_FLASH_PVR ) ) )
					#RemoveDirectory( '%s/%s'% ( aMediaPath, os.path.dirname( E_PATH_FLASH_PROGRAM ) ) )
					self.CloseBusyDialog( )
					progressDialog.update( 0, '', '' )
					progressDialog.close( )
					return E_STORAGE_ERROR_CANCEL

				strData = MR_LANG( 'Copying data' ) + '...'
				progressDialog.update( percent, strData, '%s'% fData[len(E_PATH_FLASH_BASE)+1:], ' ' )

				destPathCopy = '%s%s'% ( aTargetPath, fData[len(E_PATH_FLASH_BASE):] )
				copyList.append( destPathCopy )
				if CheckDirectory( fData, True ) :
					CreateDirectory( destPathCopy, fData )

				else :
					shutil.copy( fData, destPathCopy )
					#os.system( 'cp -af %s %s'% ( aSourceList, destPathCopy ) )
				if not CheckDirectory( destPathCopy ) :
					os.system( 'sync' )
				count = count + 1

			os.system( 'sync' )
			progressDialog.update( 100, MR_LANG( 'Done' ) )
			time.sleep( 1 )
			progressDialog.update( 0, '', '' )
			progressDialog.close( )

		except Exception, e :
			LOG_ERR( '[Storage] Exception[%s]' % e )
			for sPath in aSourceList :
				RemoveDirectory( '%s/%s'% ( aTargetPath, sPath[len(E_PATH_FLASH_BASE)+1:] ) )
				#LOG_TRACE( '----------------------removePath[%s/%s]'% ( aTargetPath, sPath[len(E_PATH_FLASH_BASE)+1:] ) )

			if progressDialog :
				progressDialog.close( )
			self.CloseBusyDialog( )
			ret = E_STORAGE_ERROR_COPY_FAIL

		return ret


	def AsyncProgressing( self, aWaitMin = 5 ) :
		mntCmd = self.mDeviceListSelect[4]
		mTitle = MR_LANG( 'Format Device' )
		strReady = MR_LANG( 'Ready' )
		strInit = ''
		strInit2= ''
		percent = 0
		progressDialog = xbmcgui.DialogProgress( )
		progressDialog.create( mTitle, strInit )
		progressDialog.update( percent, strReady )

		totalTime = 60 * aWaitMin
		waitCount = 1
		while self.mProcessing :
			percent = int( 1.0 * waitCount / totalTime * 100 )
			if percent > 99 :
				percent = 99
			progressDialog.update( percent, strInit, strInit2 )
			#LOG_TRACE( '-----------percent[%s] len[%s]'% ( percent,len(strInit)) )
			if len( strInit ) <= 100 :
				strInit = '%s.'% strInit
			elif len( strInit ) >= 100 :
				strInit2 = '%s.'% strInit2
			if len( strInit2 ) >= 100 :
				strInit = ''
				strInit2 = ''
				progressDialog.update( percent, ' ', ' ' )

			waitCount += 1
			time.sleep( 1 )

		progressDialog.update( 100, MR_LANG( 'Done' ) )
		time.sleep( 1 )
		progressDialog.update( 0, '', '' )
		progressDialog.close( )


	def MakeDedicateForJET( self ) :
		#USB to /mnt/hdd0
		doResult = E_STORAGE_ERROR_FORMAT
		devName = self.mDeviceListSelect[2]
		mntCmd  = self.mDeviceListSelect[4]
		if mntCmd == E_FORMAT_MED_HDD or mntCmd == E_FORMAT_MNT_HDD :
			hddsize = GetMountExclusiveDevice( devName )

			#LOG_TRACE( '-----------------------size[%s]'% hddsize )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Partition Info' ), MR_LANG( 'Maximum media partition size' ) + ' : %0.1f GB'% ( float( hddsize ) / ( 1000000 * 1000 ) ) )
			dialog.doModal( )

			mediaDefault = 100
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
			dialog.SetDialogProperty( MR_LANG( 'Set media partition in GB' ), '%s' % mediaDefault , 4 )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				mediaDefault = dialog.GetString( )

			#LOG_TRACE( '-----------------------size[%s] input[%s]'% ( hddsize, int( mediaDefault ) * ( 1000000 * 1024 ) ) )
			if int( hddsize ) < int( mediaDefault ) * ( 1000000 * 1024 ) :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Incorrect partition size' ) )
				dialog.doModal( )
				return E_STORAGE_ERROR_FORMAT_CANCEL

			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Format Device' ), MR_LANG( 'Are you sure you want to continue?' ) )
			dialog.doModal( )
			dialog.IsOK( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				ElisPropertyInt( 'MediaRepartitionSize', self.mCommander ).SetProp( int( mediaDefault ) * 1024 )
				ElisPropertyEnum( 'HDDRepartition', self.mCommander ).SetProp( 1 )

			else :
				return E_STORAGE_ERROR_FORMAT_CANCEL

		ElisPropertyInt( 'Update Flag', self.mCommander ).SetProp( 1 )	#block power key 1:on, 0:off
		self.OpenBusyDialog( )
		self.mProcessing = True
		tShowProcess = threading.Timer( 0, self.AsyncProgressing )
		tShowProcess.start( )

		ret = False
		#LOG_TRACE( '---------------------------------devName[%s]'% devName )
		if mntCmd == E_FORMAT_MED_MMC or mntCmd == E_FORMAT_MNT_MMC :
			mmcReboot = E_FORMAT_BY_NOT_REBOOT
			if mntCmd == E_FORMAT_MNT_HDD :
				mmcReboot = E_FORMAT_BY_REBOOT
				ElisPropertyInt( 'Update Flag', self.mCommander ).SetProp( 0 )

			ret = self.mCommander.Format_Micro_Card( mmcReboot )
			LOG_TRACE( '-------------Active-----Micro SD Format devName[%s] reboot[%s]'% ( devName, mmcReboot ) )

		elif mntCmd == E_FORMAT_MNT_HDD :
			ElisPropertyInt( 'Update Flag', self.mCommander ).SetProp( 0 )
			self.mDataCache.Player_AVBlank( True )
			self.MakeBackupScript( )
			CreateDirectory( E_DEFAULT_BACKUP_PATH )
			os.system( 'touch %s/isUsbBackup' % E_DEFAULT_BACKUP_PATH )

			ElisPropertyEnum( 'Xbmc Save Storage', self.mCommander ).SetPropIndex( E_SELECT_STORAGE_HDD )
			LOG_TRACE( '--------------------Save ElisPropertyEnum HDD[%s]'% self.mFormatToSelectHDD )

			ret = self.mCommander.Make_Dedicated_HDD( ) # reboot and format
			LOG_TRACE( '-------------Active-----Dedicated HDD[%s]'% devName )

		elif mntCmd == E_FORMAT_MED_HDD :
			ret = self.mCommander.Make_Exclusive_HDD( devName )
			LOG_TRACE( '-------------Active-----Exclusive HDD[%s] vendor[%s]'% ( devName, self.mDeviceListSelect[0] ) )

		elif mntCmd == E_FORMAT_MED_USB :
			ret = self.mCommander.Format_USB_Storage( devName )
			LOG_TRACE( '-------------Active-----Exclusive HDD[%s] vendor[%s]'% ( devName, self.mDeviceListSelect[0] ) )

		self.mProcessing = False
		if tShowProcess :
			tShowProcess.join( )
		self.CloseBusyDialog( )

		if ret :
			doResult = E_STORAGE_FORMAT_DONE
		else :
			doResult = E_STORAGE_ERROR_FORMAT

		ElisPropertyInt( 'Update Flag', self.mCommander ).SetProp( 0 )
		return doResult


	def MakeBackupScript( self ) :
		try :
			scriptFile = '%s.sh' % E_DEFAULT_BACKUP_PATH
			fd = open( scriptFile, 'w' )
			if fd :
				fd.writelines( '#!/bin/sh\n' )
				#fd.writelines( 'modprobe usb_storage\n' )
				#fd.writelines( 'sleep 3\n' )
				#fd.writelines( 'mount /dev/sdb1 /media/usb/sdb1\n' )
				usbpath = self.mDataCache.USB_GetMountPath( )
				fd.writelines( 'mkdir -p /mnt/hdd0/program/.xbmc/userdata\n' )
				fd.writelines( 'mkdir -p /mnt/hdd0/program/.xbmc/addons\n' )
				fd.writelines( 'cp -rf %s/RubyBackup/userdata/* /mnt/hdd0/program/.xbmc/userdata/\n' % usbpath )
				fd.writelines( 'cp -rf %s/RubyBackup/addons/* /mnt/hdd0/program/.xbmc/addons/\n' % usbpath )
				fd.close( )
				os.chmod( scriptFile, 0755 )

		except Exception, e :
			LOG_ERR( 'Exception[%s]'% e )

