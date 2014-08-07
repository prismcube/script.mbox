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


E_CONTEXT_MENU_FORMAT = 1
E_CONTEXT_MENU_STORAGE = 2

E_SELECT_STORAGE_NONE = 0
E_SELECT_STORAGE_MMC = 1
E_SELECT_STORAGE_USB = 2
E_SELECT_STORAGE_HDD = 3

E_FORMAT_BY_REBOOT = 0
E_FORMAT_BY_NOT_REBOOT = 1


class ExclusiveSettings( object ) :
	def __init__( self ) :
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.mDataCache = pvr.DataCacheMgr.GetInstance( )
		self.mSelectAction = -1
		self.mFormatToSelectHDD = False


	def OpenBusyDialog( self ) :
		xbmc.executebuiltin( 'ActivateWindow(busydialog)' )


	def CloseBusyDialog( self ) :
		xbmc.executebuiltin( 'Dialog.Close(busydialog)' )


	def Configure( self, aMenu = E_CONTEXT_MENU_STORAGE ) :
		self.ShowContextMenu( aMenu )


	def GetContextSelected( self ) :
		return self.mSelectAction


	def ResultDialog( self, aErrorNo ) :
		LOG_TRACE( '--------------------error[%s]'% aErrorNo )
		mTitle = MR_LANG( 'Error' )
		mLines = ''
		if aErrorNo == E_STORAGE_DONE :
			mTitle = MR_LANG( 'Success' )
			mLines = MR_LANG( 'Complete' )
		elif aErrorNo == E_STORAGE_FORMAT_DONE :
			mTitle = MR_LANG( 'Success' )
			mLines = MR_LANG( 'Complete formated' )
		elif aErrorNo == E_STORAGE_ERROR_FORMAT_CANCEL :
			mTitle = MR_LANG( 'Attention' )
			mLines = MR_LANG( 'Format is canceled' )
		elif aErrorNo == E_STORAGE_ERROR_CANCEL :
			mTitle = MR_LANG( 'Attention' )
			mLines = MR_LANG( 'storage appointment is canceled' )
		elif aErrorNo == E_STORAGE_ERROR_SPACE :
			mLines = MR_LANG( 'Not enough space on USB flash memory' )
		elif aErrorNo == E_STORAGE_ERROR_USB_INSERT :
			mLines = MR_LANG( 'Please insert a USB flash memory' )
		elif aErrorNo == E_STORAGE_ERROR_NOT_USB_AVAIL :
			mLines = MR_LANG( 'Check your USB device' )
		elif aErrorNo == E_STORAGE_ERROR_NOT_USB :
			mLines = MR_LANG( 'Check your USB memory' )
		elif aErrorNo == E_STORAGE_ERROR_NOT_MMC :
			mLines = MR_LANG( 'Check your Micro SD card' )
		elif aErrorNo == E_STORAGE_ERROR_NOT_HDD :
			mLines = MR_LANG( 'Check your USB HDD' )
		elif aErrorNo == E_STORAGE_ERROR_MOUNT_TYPE :
			mLines = MR_LANG( 'Unknown filesystem or not formated' )
		elif aErrorNo == E_STORAGE_ERROR_STORAGE :
			mLines = MR_LANG( 'Can not appoint storage' )
		elif aErrorNo == E_STORAGE_ERROR_FORMAT :
			mLines = MR_LANG( 'Fail to format drive' )
		elif aErrorNo == E_STORAGE_ERROR_COPY_FAIL :
			mLines = MR_LANG( 'Fail to copy addons' )
		elif aErrorNo == E_STORAGE_ERROR_RESTORE_FAIL :
			mLines = MR_LANG( 'Fail to restore addons or user data' )
		elif aErrorNo == E_STORAGE_ERROR_NOT_SUPPORT_STORAGE :
			mLines = MR_LANG( 'Not support USB memory' )
		elif aErrorNo == E_STORAGE_ERROR_USED_MMC :
			mLines = MR_LANG( 'Already using Micro SD card' )
		elif aErrorNo == E_STORAGE_ERROR_USED_HDD :
			mLines = MR_LANG( 'Already using USB HDD' )
		elif aErrorNo == E_STORAGE_ERROR_FORMAT_NOT_FOUND :
			mLines = MR_LANG( 'Not found device, Please insert device again' )


		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( mTitle, mLines )
		dialog.doModal( )


	def GetContextMenu( self, aMenu ) :
		context = []
		mntinfo = []

		if aMenu == E_CONTEXT_MENU_FORMAT :
			mntinfo = GetMountExclusiveDevice( )
			#SDExist = self.mCommander.MMC_MountCheck( )
			#if SDExist :
			#	mLines = '%s(%s)'% ( MR_LANG( 'Micro SD Card' ), mmcsize )
			#	context.append( ContextItem( mLines, E_SELECT_STORAGE_MMC ) )

			LOG_TRACE( '-------------mntinfo[%s]'% mntinfo )
			mntidx = 0
			for ele in mntinfo :
				mLines = '%s-%s(%s)'% ( MR_LANG( 'USB' ), ele[0], ele[1] )
				if ele[2] == '/dev/mmc' :
					mLines = '%s(%s)'% ( ele[0], ele[1] )
				context.append( ContextItem( mLines, mntidx ) )
				mntidx += 1

		else :
			defSelect = ElisPropertyEnum( 'Xbmc Save Storage', self.mCommander ).GetProp( )
			deviceList = ElisPropertyEnum( 'Xbmc Save Storage', self.mCommander ).mProperty
			LOG_TRACE( '-------------------def ElisPropertyEnum[%s]'% deviceList[defSelect][1] )

			context.append( ContextItem( MR_LANG('Internal Storage'), E_SELECT_STORAGE_NONE ) )
			context.append( ContextItem( MR_LANG('Micro SD Card'), E_SELECT_STORAGE_MMC ) )
			context.append( ContextItem( MR_LANG('USB Memory'), E_SELECT_STORAGE_USB ) )
			context.append( ContextItem( MR_LANG('USB HDD'), E_SELECT_STORAGE_HDD ) )
			"""
			for i in range( len( deviceList ) ) :
				deviceName = deviceList[i][1]
				#if i == defSelect :
				#	selectItem = i + 1
				#	deviceName = '[COLOR ff2E2E2E]%s[/COLOR]'% deviceName
				context.append( ContextItem( deviceName, i ) )
			"""

		return context, mntinfo


	def ShowContextMenu( self, aMenu = E_CONTEXT_MENU_STORAGE ) :
		contextList, mntinfo = self.GetContextMenu( aMenu )

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

		#LOG_TRACE( '--------------------select[%s]'% contextList[selectAction].mDescription )

		if aMenu == E_CONTEXT_MENU_FORMAT :
			mntPath = GetMountPathByDevice( -1, mntinfo[selectAction][2] )
			self.FormatStorage( mntPath )

		elif aMenu == E_CONTEXT_MENU_STORAGE :
			self.SelectStorage( selectAction )


	def FormatStorage( self, aSelect ) :
		isFail = E_STORAGE_FORMAT_DONE
		mTitle = MR_LANG( 'Error' )
		mLines = MR_LANG( 'Could not find a Micro SD card' )
		mntPath = aSelect
		LOG_TRACE( '--------------------select mntpath[%s]'% mntPath )

		if mntPath :
			ret = self.DoFormatStorage( mntPath )
			self.ResultDialog( ret )

		#unknown or not formated ?
		return E_STORAGE_ERROR_FORMAT_NOT_FOUND


	def DoFormatStorage( self, aMntPath ) :
		isbackup = False
		isformat = False
		doResult = E_STORAGE_ERROR_FORMAT

		usbPath  = ''
		#mntPath  = GetMountPathByDevice( aMntPath )
		xbmcPath = '%s/program/.xbmc'% aMntPath

		mTitle = MR_LANG( 'Format your drive?' )
		mLine1 = MR_LANG( 'Everything on your drive will be erased' )
		mLine2 = MR_LANG( 'This will take a while' )

		if aMntPath == E_SELECT_STORAGE_MMC or aMntPath == E_PATH_MMC :
			mTitle = MR_LANG( 'Format your SD memory card?' )
			mLine1 = MR_LANG( 'Everything on your SD card will be erased' )
			mLine2 = ''

		#1. check .xbmc ?
		#if CheckMountType( aMntPath ).lower( ) == 'ext4' :
		if CheckDirectory( xbmcPath ) :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Backup data?' ), MR_LANG( 'To backup your user data and XBMC add-ons,%s insert a USB flash memory' ) % NEW_LINE )
			dialog.doModal( )
			ret = dialog.IsOK( )
			if ret == E_DIALOG_STATE_YES :
				isbackup = True

			elif ret == E_DIALOG_STATE_CANCEL :
				return E_STORAGE_ERROR_FORMAT_CANCEL

		#ToDO : force dedicated format reboot ? <-- factory empty ?

		#2. backup xbmc data
		if isbackup :
			isformat = True
			usbPath = self.mDataCache.USB_GetMountPath( )
			if usbPath :
				if CheckDirectory( usbPath + '/RubyBackup/' ) :
					RemoveDirectory( usbPath + '/RubyBackup/' )
				CreateDirectory( usbPath + '/RubyBackup/' )

				sourceList = [ '%s/userdata'% xbmcPath, '%s/addons'% xbmcPath ]
				targetPath = '%s/RubyBackup'% usbPath
				doResult = self.CopyXBMCData( sourceList, targetPath, '', MR_LANG( 'Now backing up your user data' ), usbPath )
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

		#3. format
		if isformat :
			doResult = self.MakeDedicateForJET( aMntPath )
			if doResult == E_STORAGE_DONE :
				#4. resotre backup
				if isbackup :
					sourceList = [ '%s/RubyBackup/userdata'% usbPath, '%s/addons'% xbmcPath ]
					targetPath = xbmcPath
					doResult = self.CopyXBMCData( sourceList, targetPath, '', MR_LANG( 'Now restoring up your user data' ), aMntPath )
					if doResult == E_STORAGE_ERROR_COPY_FAIL :
						doResult = E_STORAGE_ERROR_RESTORE_FAIL

		return doResult


	def SelectStorage( self, aSelect ) :
		ret = False
		if aSelect == E_SELECT_STORAGE_NONE :
			ret = E_STORAGE_DONE
		else :
			ret = self.ChangeStorage( aSelect )

		if ret == E_STORAGE_DONE :
			ElisPropertyEnum( 'Xbmc Save Storage', self.mCommander ).SetPropIndex( aSelect )
			LOG_TRACE( '--------------------Save ElisPropertyEnum[%s]'% aSelect )
			msg1 = '%s%s'% ( MR_LANG( 'Your system will reboot in %s seconds' )% 5, ING )
			self.mDialogShowInit = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			self.mDialogShowInit.SetDialogProperty( MR_LANG( 'Restart Required' ), msg1 )
			self.mDialogShowInit.SetButtonVisible( False )
			self.mDialogShowInit.SetDialogType( 'update' )
			self.mDialogShowInit.SetAutoCloseTime( 5 )
			self.mDialogShowInit.doModal( )
			#self.mDataCache.System_Reboot( )

		else :
			self.ResultDialog( ret )


	def ChangeStorage( self, aSelect ) :
		mediaPath = ''
		exceptList = [ '%s/download'% E_PATH_FLASH_PROGRAM ]
		sourceList = [ E_PATH_FLASH_PVR, E_PATH_FLASH_PROGRAM ]
		targetPath = ''
		hddpath = self.mDataCache.HDD_GetMountPath( )
		#LOG_TRACE( '-------------------------HDD_GetMountPath len[%s]'% len( hddpath ) )
		if aSelect == E_SELECT_STORAGE_MMC :
			mediaPath = E_PATH_MMC
			SDExist = self.mCommander.MMC_MountCheck( )
			if not SDExist :
				return E_STORAGE_ERROR_NOT_MMC

			mntPath = GetMountPathByDevice( -1, os.path.basename( E_PATH_MMC ) )
			if mntPath == E_PATH_FLASH_BASE or hddpath and len( hddpath ) < 2 :
				return E_STORAGE_ERROR_USED_MMC

		elif aSelect == E_SELECT_STORAGE_USB :
			return E_STORAGE_ERROR_NOT_SUPPORT_STORAGE

		elif aSelect == E_SELECT_STORAGE_HDD :
			mediaPath = E_PATH_HDD
			mntPath = GetMountPathByDevice( -1, os.path.basename( E_PATH_FLASH_BASE ) )
			if mntPath == E_PATH_FLASH_BASE and hddpath and len( hddpath ) > 2 :
				return E_STORAGE_ERROR_USED_HDD


		targetPath = mediaPath

		mTitle = MR_LANG( 'Error' )
		mLines = MR_LANG( 'Changed Fail to Storage' )
		doResult = E_STORAGE_DONE

		try :
			mType = CheckMountType( mediaPath ).lower( )
			if mType :
				if mType == 'ext4' :
					xbmcPath = '%s/program/.xbmc'% mediaPath
					if CheckDirectory( xbmcPath ) :
						mTitle = MR_LANG( 'Attention' )
						mLines = MR_LANG( 'Can you remove old addons in Micro SD Card?' )
						if aSelect == E_SELECT_STORAGE_HDD :
							mLines = MR_LANG( 'Can you remove old addons in USB HDD?' )
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
					#vfat, ntfs, ... etc
					if aSelect == E_SELECT_STORAGE_HDD :
						self.mFormatToSelectHDD = True

					doResult = self.DoFormatStorage( mediaPath )
					if doResult == E_STORAGE_ERROR_FORMAT_CANCEL :
						doResult = E_STORAGE_ERROR_CANCEL

				if doResult == E_STORAGE_DONE :
					#copy to data
					doResult = self.CopyXBMCData( sourceList, targetPath, exceptList )

			else :
				#check except
				doResult = E_STORAGE_ERROR_MOUNT_TYPE

		except Exception, e :
			LOG_ERR( '[Storage]except[%s]'% e )
			doResult = E_STORAGE_ERROR_STORAGE

		return doResult


	def CopyXBMCData( self, aSourceList, aTargetPath, aExceptList = [], aTitle = '', aTargetDevice = None ) :
		ret = E_STORAGE_DONE
		if not aSourceList or len( aSourceList ) < 1 :
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
		mTitle = MR_LANG( 'XBMC Data Copy' )
		if aTitle :
			mTitle = aTitle
		self.OpenBusyDialog( )
		pathlist = GetDirectoryAllFilePathList( aSourceList, aExceptList )
		self.CloseBusyDialog( )
		progressDialog = None
		try :
			strInit = MR_LANG( 'Initializing process' ) + '...'
			strReady = MR_LANG( 'Ready to start' ) + '...'
			percent = 0
			progressDialog = xbmcgui.DialogProgress( )
			progressDialog.create( mTitle, strInit )
			progressDialog.update( percent, strReady )

			count = 1
			totlen = len( pathlist )
			for fData in pathlist :
				percent = int( 1.0 * count / totlen * 100 )

				if progressDialog.iscanceled( ) :
					strCancel = MR_LANG( 'Canceling' ) + '...'
					progressDialog.update( percent, strCancel )
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
			progressDialog.update( 100, mTitle, MR_LANG( 'Complete' ) )
			time.sleep( 1 )
			progressDialog.update( 0, '', '' )
			progressDialog.close( )

		except Exception, e :
			LOG_ERR( '[Storage]except[%s]' % e )
			for sPath in aSourceList :
				RemoveDirectory( '%s/%s'% ( aTargetPath, sPath[len(E_PATH_FLASH_BASE)+1:] ) )
				#LOG_TRACE( '----------------------removePath[%s/%s]'% ( aTargetPath, sPath[len(E_PATH_FLASH_BASE)+1:] ) )

			if progressDialog :
				progressDialog.close( )
			self.CloseBusyDialog( )
			ret = E_STORAGE_ERROR_COPY_FAIL

		return ret


	def AsyncProgressing( self, aMntPath = E_PATH_MMC, aWaitTime = 10 ) :
		mTitle = MR_LANG( 'Format USB HDD' )
		if aMntPath == E_SELECT_STORAGE_MMC or aMntPath == E_PATH_MMC :
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
			percent = int( waitCount / totalTime )
			if percent > 99 :
				percent = 99
			progressDialog.update( percent, mTitle, strInit, ' ' )

			waitCount += 1
			time.sleep( 1 )

		progressDialog.update( 100, mTitle, MR_LANG( 'Complete' ) )
		time.sleep( 1 )
		progressDialog.update( 0, '', '' )
		progressDialog.close( )


	def MakeDedicateForJET( self, aMntPath ) :
		#for /mnt/hdd0 on usb
		doResult = E_STORAGE_ERROR_FORMAT
		mmcReboot = E_FORMAT_BY_NOT_REBOOT
		if aMntPath == E_PATH_HDD or aMntPath == E_PATH_FLASH_BASE :
			hddpath = self.mDataCache.HDD_GetMountPath( )
			#hddsize = self.GetMaxMediaSize( )
			mntinfo = GetMountExclusiveDevice( )
			hddsize = 0
			LOG_TRACE( '----------------------------formatMnt[%s] mminfo[%s]'% ( aMntPath, mntinfo ) )
			for ele in mntinfo :
				if GetMountPathByDevice( -1, ele[2] ) == aMntPath :
					#hddsize = ele[1]
					hddsize = GetMountExclusiveDevice( ele[2] )

					#mmc format /mnt/hdd0: reboot, /media/hdd0: non-reboot
					if os.path.basename( ele[2] ) == os.path.basename( E_PATH_MMC ) :
						aMntPath = E_PATH_MMC
						mmcReboot = E_FORMAT_BY_REBOOT
					break

			if aMntPath != E_PATH_MMC :
				#LOG_TRACE( '-----------------------size[%s]'% hddsize )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Maximum Partition Size' ), MR_LANG( 'Maximum media partition size' ) + ' : %0.1f GB'% ( float( hddsize ) / ( 1000000 * 1000 ) ) )
				dialog.doModal( )

				mediadefault = 100
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
				dialog.SetDialogProperty( MR_LANG( 'Enter Media Partition Size in GB' ), '%s' % mediadefault , 4 )
				dialog.doModal( )
				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					mediadefault = dialog.GetString( )

				#LOG_TRACE( '-----------------------size[%s] input[%s]'% ( hddsize, int( mediadefault ) * ( 1000000 * 1024 ) ) )
				if int( hddsize ) < int( mediadefault ) * ( 1000000 * 1024 ) :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Partition size not valid' ) )
					dialog.doModal( )
					return E_STORAGE_ERROR_FORMAT_CANCEL

				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( MR_LANG( 'Your Media Partition is %s GB' ) % mediadefault, MR_LANG( 'Start formatting HDD?' ) )
				dialog.doModal( )
				dialog.IsOK( )
				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					ElisPropertyInt( 'MediaRepartitionSize', self.mCommander ).SetProp( int( mediadefault ) * 1024 )
					ElisPropertyEnum( 'HDDRepartition', self.mCommander ).SetProp( 1 )

				else :
					return E_STORAGE_ERROR_FORMAT_CANCEL

		self.OpenBusyDialog( )
		self.mProcessing = True
		tShowProcess = threading.Timer( 0, self.AsyncProgressing, [aMntPath] )
		tShowProcess.start( )

		ret = False
		LOG_TRACE( '---------------------------------format aMntPath[%s]'% aMntPath )
		if aMntPath == E_PATH_MMC :
			ret = self.mCommander.Format_Micro_Card( mmcReboot )
			#LOG_TRACE( '-------------active-----micro format[%s] reboot[%s]'% ( aMntPath, mmcReboot ) )

		elif aMntPath == E_PATH_HDD or aMntPath == E_PATH_FLASH_BASE :
			self.mDataCache.Player_AVBlank( True )
			self.MakeBackupScript( )
			CreateDirectory( E_DEFAULT_BACKUP_PATH )
			os.system( 'touch %s/isUsbBackup' % E_DEFAULT_BACKUP_PATH )

			if self.mFormatToSelectHDD :
				ElisPropertyEnum( 'Xbmc Save Storage', self.mCommander ).SetPropIndex( E_SELECT_STORAGE_HDD )
				LOG_TRACE( '--------------------Save ElisPropertyEnum HDD[%s]'% self.mFormatToSelectHDD )

			#ret = self.mCommander.Make_Dedicated_HDD( ) # reboot and format
			#LOG_TRACE( '-------------active-----dedicate format[%s]'% aMntPath )

		else :
			#usb memory
			ret = self.mCommander.Make_Exclusive_HDD( aMntPath )
			#LOG_TRACE( '-------------active-----exclusive format[%s]'% aMntPath )

		self.mProcessing = False
		if tShowProcess :
			tShowProcess.join( )
		self.CloseBusyDialog( )

		if ret :
			doResult = E_STORAGE_FORMAT_DONE
		else :
			doResult = E_STORAGE_ERROR_FORMAT

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
			LOG_ERR( 'except[%s]'% e )

