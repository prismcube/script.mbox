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
E_STORAGE_ERROR_UNKNOWN_SIZE = -21


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
E_FORMAT_MNT_USB = 5

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
			mLines = MR_LANG( 'Not enough space left on the device' )
		elif aErrorNo == E_STORAGE_ERROR_USB_INSERT :
			mLines = MR_LANG( 'Please insert an USB stick' )
		elif aErrorNo == E_STORAGE_ERROR_NOT_USB_AVAIL :
			mLines = MR_LANG( 'Check your USB device' )
		elif aErrorNo == E_STORAGE_ERROR_NOT_USB :
			mLines = MR_LANG( 'Device not found' )
		elif aErrorNo == E_STORAGE_ERROR_NOT_MMC :
			mLines = MR_LANG( 'Device not found' )
		elif aErrorNo == E_STORAGE_ERROR_NOT_HDD :
			mLines = MR_LANG( 'Device not found' )
		elif aErrorNo == E_STORAGE_ERROR_MOUNT_TYPE :
			mLines = MR_LANG( 'Unknown filesystem or not formatted' )
		elif aErrorNo == E_STORAGE_ERROR_STORAGE :
			mLines = MR_LANG( 'Storage device not changed' )
		elif aErrorNo == E_STORAGE_ERROR_FORMAT :
			mLines = MR_LANG( 'Failed to format device' )
		elif aErrorNo == E_STORAGE_ERROR_COPY_FAIL :
			mLines = MR_LANG( 'Failed to copy XBMC add-ons' )
		elif aErrorNo == E_STORAGE_ERROR_RESTORE_FAIL :
			mLines = MR_LANG( 'Failed to restore data' )
		elif aErrorNo == E_STORAGE_ERROR_NOT_SUPPORT_STORAGE :
			mLines = MR_LANG( 'Setting USB stick as storage device is not yet supported' )
		elif aErrorNo == E_STORAGE_ERROR_USED_MMC :
			mLines = MR_LANG( 'The device is already selected' )
		elif aErrorNo == E_STORAGE_ERROR_USED_HDD :
			mLines = MR_LANG( 'The device is already selected' )
		elif aErrorNo == E_STORAGE_ERROR_FORMAT_NOT_FOUND :
			mLines = MR_LANG( 'No device found' )
		elif aErrorNo == E_STORAGE_ERROR_USED_INTERNAL :
			mLines = MR_LANG( 'The device is already selected' )
		elif aErrorNo == E_STORAGE_ERROR_TRY_AGAIN :
			mLines = MR_LANG( 'Try again after few seconds' )
		elif aErrorNo == E_STORAGE_ERROR_UNKNOWN_SIZE :
			mLines = MR_LANG( 'Invalid storage size' )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( mTitle, mLines )
		dialog.doModal( )


	def GetContextMenu( self, aMenu ) :
		context = []
		#self.mDeviceListSelect = []

		self.mDeviceList = deepcopy( GetDeviceList() )

		if aMenu == E_CONTEXT_MENU_STORAGE :
			device = ['/dev/internalflash', 0, 'Internal Flash']
			self.mDeviceList.insert( 0, device )

		device_index = 0		
		for device in self.mDeviceList :
			if device[0] == '/dev/internalflash' :
				display_name = '%s' %( device[2] )
			else :
				display_name = '%s(%s)' %( device[2], SizeToString( device[1] ) )
			context.append( ContextItem(display_name, device_index ) )
			device_index += 1

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
			#self.mDeviceListSelect = self.mDeviceList[selectAction]
			self.FormatStorage( selectAction )

		elif aMenu == E_CONTEXT_MENU_STORAGE :
			self.SelectStorage( selectAction )


	def FormatStorage( self, aIndex ) :
		ret = self.DoFormatStorage( aIndex )
		self.ResultDialog( ret )


	def DoFormatStorage( self, aIndex ) :
		isformat = True	
		doResult = E_STORAGE_ERROR_FORMAT
		mTitle = MR_LANG( 'Format Device' )
		mLine1 = MR_LANG( 'Formatting will erase ALL data on this device' )
		mLine2 = MR_LANG( 'This will take a while' )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( mTitle, mLine1, mLine2 )
		dialog.doModal( )
		ret = dialog.IsOK( ) == E_DIALOG_STATE_YES
		if ret == E_DIALOG_STATE_YES :
			isformat = True
		elif ret == E_DIALOG_STATE_NO :
			return E_STORAGE_ERROR_FORMAT_CANCEL
		else :
			return E_STORAGE_ERROR_FORMAT_CANCEL

		if isformat :
			device = self.mDeviceList[aIndex]
			waitMin = 5
			dev_name = device[0]
			dev_size =device[1]
			waitMin += int( dev_size / ( 30 * 1024 *  1024 * 1024 ) ) #30GB/MIN
			
			LOG_TRACE( 'dev_name=%s dev_size=%s waitMin=%s' %(dev_name, dev_size, waitMin ) )			

			mountList = GetMountDevice( )

			mntCmd = E_FORMAT_MED_USB			

			#MMC FORMAT
			if dev_name.startswith( '/dev/mmcblk' ) == True :
				mntCmd = E_FORMAT_MED_MMC
				for mount in mountList :
					if mount[0].startswith( dev_name ) == True and mount[1] == '/mmt/hdd0' :
						mntCmd = E_FORMAT_MNT_MMC
						break

			#USB/HDD FORMAT
			elif dev_name.startswith('/dev/sd' ) == True :
				if dev_size < (100 *  1024 * 1024 * 1024 ) : #100GB
					mntCmd = E_FORMAT_MED_USB
					for mount in mountList :
						if mount[0].startswith( dev_name ) == True and mount[1] == '/mmt/hdd0/program' :
							mntCmd = E_FORMAT_MNT_USB
							break
					
				else :
					mntCmd = E_FORMAT_MED_HDD
					for mount in mountList :
						if mount[0].startswith( dev_name ) == True and mount[1] == '/mmt/hdd0/program' :
							mntCmd = E_FORMAT_MNT_HDD
							break

					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Partition Info' ), MR_LANG( 'Maximum media partition size' ) + ' : %0.1f GB'% ( 1.0 * dev_size / ( 1024 * 1024 * 1024) ) )
					dialog.doModal( )

					mediaDefault = 100
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
					dialog.SetDialogProperty( MR_LANG( 'Set media partition in GB' ), '%s' % mediaDefault , 4 )
					dialog.doModal( )
					if dialog.IsOK( ) == E_DIALOG_STATE_YES :
						mediaDefault = dialog.GetString( )

					#LOG_TRACE( '-----------------------size[%s] input[%s]'% ( dev_size, int( mediaDefault ) * ( 1000000 * 1024 ) ) )
					if dev_size < int( mediaDefault ) * ( 1024 * 1024 * 1024 ) :
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
			tShowProcess = threading.Timer( 0, self.AsyncProgressing, [waitMin] )
			tShowProcess.start( )

			ret = False

			mmcReboot = E_FORMAT_BY_NOT_REBOOT
			if mntCmd == E_FORMAT_MED_MMC or mntCmd == E_FORMAT_MNT_MMC :
				if mntCmd == E_FORMAT_MNT_HDD :
					mmcReboot = E_FORMAT_BY_REBOOT
				ret = self.mCommander.Format_Micro_Card( mmcReboot )

			elif mntCmd == E_FORMAT_MED_HDD or mntCmd == E_FORMAT_MNT_HDD:
				if mntCmd == E_FORMAT_MNT_HDD :
					mmcReboot = E_FORMAT_BY_REBOOT
				ret = self.mCommander.Make_Exclusive_HDD( dev_name )

			elif mntCmd == E_FORMAT_MED_USB or mntCmd == E_FORMAT_MNT_USB :
				if mntCmd == E_FORMAT_MNT_USB :
					mmcReboot = E_FORMAT_BY_REBOOT
				ret = self.mCommander.Format_USB_Storage( dev_name )

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

	def SelectStorage( self, aSelect ) :
		ret = self.ChangeStorage( aSelect )
		if ret == E_STORAGE_DONE :
			mHead = MR_LANG( 'Please wait' )
			mLine = MR_LANG( 'System is restarting' ) + '...'
			xbmc.executebuiltin( 'Notification( %s, %s, 3000, DefaultIconInfo.png )'% ( mHead, mLine ) )
			time.sleep( 2 )
			self.mDataCache.System_Reboot( )

		else :
			self.ResultDialog( ret )


	def ChangeStorage( self, aSelect ) :
		#aDevice 1: mmc, 2: usb memory, 3: hdd	
		exceptList = [ '%s/download'% E_PATH_FLASH_PROGRAM, '%s/.xbmc/temp'% E_PATH_FLASH_PROGRAM ]
		sourceList = [ E_PATH_FLASH_PVR, E_PATH_FLASH_PROGRAM ]

		device  = self.mDeviceList[aSelect]

		dev_name = device[0]
		dev_size = device[1]
		vender_name = device[2]
	
		mountList = GetMountDevice( )

		cur_index = ElisPropertyEnum( 'Xbmc Save Storage', self.mCommander ).GetPropIndex( )
		new_index = cur_index

		LOG_TRACE( 'dev_name=%s current=%s' %(dev_name, cur_index ) )

		isfomated = False

		targetPath = ''
		#INTERNAL SELECT
		if dev_name.startswith( '/dev/internalflash' ) == True :
			new_index = 0
			isfomated = True
		
		#MMC SELECT
		elif dev_name.startswith( '/dev/mmcblk' ) == True :
			new_index = 1
			targetPath = '/media/mmc'
			for mount in mountList :
				if mount[0].startswith( dev_name ) == True and mount[1] == '/media/mmc' and ( mount[2] == 'ext3' or mount[2] == 'ext4' ):
					isfomated = True
					break

		#USB/HDD SELECT
		elif dev_name.startswith('/dev/sd' ) == True :
			if dev_size < (100 *  1024 * 1024 * 1024 ) : #100GB
				new_index = 2
			else :
				new_index = 3

			targetPath = '/media/hdd0'

			for mount in mountList :
				if mount[0].startswith( dev_name ) == True and mount[1] == '/media/hdd0/program' and ( mount[2] == 'ext3' or mount[2] == 'ext4'  ):
					isfomated = True
					break

		#CHECK already used
		if new_index == cur_index :
			if new_index == 0 :
				return E_STORAGE_ERROR_USED_INTERNAL
			elif new_index == 1 :
				return E_STORAGE_ERROR_USED_MMC
			else :
				return E_STORAGE_ERROR_USED_HDD

		if new_index == 2 : #USB Stick is not support until now
			return E_STORAGE_ERROR_NOT_SUPPORT_STORAGE

		#FORMAT
		if isfomated == False and new_index !=0 :
			ret = self.DoFormatStorage( aSelect )
			if ret != E_STORAGE_FORMAT_DONE :
				return E_STORAGE_ERROR_CANCEL

		mTitle = MR_LANG( 'Error' )
		mLines = MR_LANG( 'Failed to change storage device' )

		doResult = E_STORAGE_DONE

		if  new_index !=0 :
			mTitle = MR_LANG( 'Installed XBMC add-ons' )
			mLines = MR_LANG( 'Do you want to copy your add-ons to Micro SD?' )
			if new_index == 1 :
				removePath = '/media/mmc/program/.xbmc'
			if new_index == 2 or new_index == 3  :
				removePath = '/media/hdd0/program/.xbmc'			
				mLines = MR_LANG( 'Do you want to copy your add-ons to USB HDD?' )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( mTitle, mLines )
			dialog.doModal( )

			ret = dialog.IsOK( )
			if ret == E_DIALOG_STATE_CANCEL :
				doResult = E_STORAGE_ERROR_CANCEL

			elif ret == E_DIALOG_STATE_YES :
				self.OpenBusyDialog( )			
				RemoveDirectory( removePath )
				self.CloseBusyDialog()

			elif ret == E_DIALOG_STATE_NO :
				self.OpenBusyDialog( )			
				RemoveDirectory( removePath )			
				exceptList.append( '%s/.xbmc'% E_PATH_FLASH_PROGRAM )
				self.CloseBusyDialog()				

			if doResult == E_STORAGE_DONE or doResult == E_STORAGE_FORMAT_DONE :
				#Copy XBMC data
				doResult = self.CopyXBMCData( sourceList, targetPath, exceptList )

		if doResult == E_STORAGE_DONE :
			ElisPropertyEnum( 'Xbmc Save Storage', self.mCommander ).SetPropIndex( new_index )

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

		if targetSize == 0 :
			return E_STORAGE_ERROR_NOT_HDD

		if targetSize < sourceSize and targetSize > 0 :
			print 'daniel ------------- targetSize = %s'%targetSize
			print 'daniel ------------- sourceSize = %s'%sourceSize
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
					#shutil.copy( fData, destPathCopy )
					os.system( 'cp -af %s %s'% ( fData, destPathCopy ) )
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
		#mntCmd = self.mDeviceListSelect[4]
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

