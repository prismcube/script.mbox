from pvr.gui.WindowImport import *
import shutil


class ExclusiveSettings( object ) :
	def __init__( self ) :
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )


	def OpenBusyDialog( self ) :
		xbmc.executebuiltin( 'ActivateWindow(busydialog)' )


	def CloseBusyDialog( self ) :
		xbmc.executebuiltin( 'Dialog.Close(busydialog)' )


	def Configure( self ) :
		self.CopyXBMCData( )
		#self.ShowContextMenu( )


	def ShowContextMenu( self ) :
		context = []
		defSelect = ElisPropertyEnum( 'Xbmc Save Storage', self.mCommander ).GetProp( )
		#deviceList = [MR_LANG( 'None' ), MR_LANG( 'Micro SD Card' ), MR_LANG( 'USB Storage' ), MR_LANG( 'Exclusive HDD' )]
		deviceList = ElisPropertyEnum( 'Xbmc Save Storage', self.mCommander ).mProperty

		selectItem = -1
		itemCount = -1
		for i in range( len( deviceList ) ) :
			if i == 1 or i == 3 :
				itemCount += 1
				deviceName = deviceList[i][1]
				if i == defSelect :
					selectItem = itemCount
					deviceName = '[COLOR ff2E2E2E]%s[/COLOR]'% deviceName
				context.append( ContextItem( deviceName, i ) )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context, selectItem )
 		dialog.doModal( )


		selectAction = dialog.GetSelectedAction( )
		if selectAction < 0 :
			LOG_TRACE( '[Exclusive] cancel, previous back' )
			return

		if selectAction == defSelect :
			LOG_TRACE( '[Exclusive] pass, select same' )
			return

		ElisPropertyEnum( 'Xbmc Save Storage', self.mCommander ).SetPropIndex( selectAction )
		LOG_TRACE( '--------------------select[%s]'% deviceList[selectAction][1] )


	def CopyXBMCData( self ) :
		xbmcPath = '/mnt/hdd0/program/.xbmc'
		self.OpenBusyDialog( )
		usbpath = pvr.DataCacheMgr.GetInstance( ).USB_GetMountPath( )
		if not usbpath :
			return False

		if GetDeviceSize( usbpath ) < GetDirectorySize( xbmcPath ) :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Not enough space on USB flash memory' ) )
			dialog.doModal( )
			self.CloseBusyDialog( )
			return False

		destPath = usbpath + '/xbmc_backup_data'
		if os.path.exists( destPath ) :
			RemoveDirectory( destPath )

		pathlist = GetDirectoryAllFilePathList( [ xbmcPath ] )
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
			for path in pathlist :
				percent = int( 1.0 * count / len( pathlist ) * 100 )

				if progressDialog.iscanceled( ) :
					strCancel = MR_LANG( 'Canceling' ) + '...'
					progressDialog.update( percent, strCancel )
					self.OpenBusyDialog( )
					RemoveDirectory( destPath )
					self.CloseBusyDialog( )
					progressDialog.update( 0, '', '' )
					progressDialog.close( )
					return False

				strData = MR_LANG( 'Copying data' ) + '...'
				progressDialog.update( percent, strData, '%s' % path, ' ' )

				destPathCopy = destPath + path[ len( xbmcPath ) : ]
				if not os.path.exists( os.path.dirname( destPathCopy ) ) :
					os.makedirs( os.path.dirname( destPathCopy ) )

				shutil.copy( path, destPathCopy )
				count = count + 1

			progressDialog.update( 100, MR_LANG( 'XBMC Data Copy' ), MR_LANG( 'Complete' ) )
			time.sleep( 1 )
			progressDialog.update( 0, '', '' )
			progressDialog.close( )
			return True

		except Exception, e :
			LOG_ERR( 'except BackupXBMC [%s]' % e )
			RemoveDirectory( destPath )
			if progressDialog :
				progressDialog.close( )
			self.CloseBusyDialog( )
			return False
