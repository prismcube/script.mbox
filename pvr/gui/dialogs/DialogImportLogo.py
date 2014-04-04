from pvr.gui.WindowImport import *
import xbmc, xbmcgui
import urllib2
from subprocess import *

try :
	import xml.etree.cElementTree as ElementTree
except Exception, e :
	from elementtree import ElementTree


E_DEFAULT_LOGO_DIRECTORY	= 'http://update.prismcube.com/channellogo.html'
E_DEFAULT_LOGO_PATH			= 'http://update.prismcube.com/updatefile/channellogo'
TEMP_LOGO_PATH = xbmc.translatePath( "special://profile/channellogo_tmp" )


CONTROL_ID_RADIO_ENABLE		= 110
CONTROL_ID_BUTTON_USB		= 111
CONTROL_ID_BUTTON_INTERNET	= 114
CONTROL_ID_BUTTON_CLEAR		= 115
CONTROL_ID_BUTTON_OK		= 118
CONTROL_ID_BUTTON_CANCEL	= 119
CONTROL_ID_LABEL_LOADED		= 117


class DialogImportLogo( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mCtrlEnable			= None
		self.mCtrlImportUSB			= None
		self.mCtrlImportInternet	= None
		self.mCtrlClear				= None
		self.mCtrlOK				= None
		self.mCtrlCancel			= None
		self.mCtrlLoaded			= None
		self.mCheckedItem			= 0
		self.mIconHash				= {}


	def onInit( self ) :
		self.getControl( 102 ).setLabel( MR_LANG( 'Import Channel Logos' ) )
		self.getControl( 103 ).setLabel( MR_LANG( 'Enable/Disable customized version of channel logos' ) )
		self.getControl( 104 ).setLabel( MR_LANG( 'Select a way of importing customized channel logos' ) )
	
		self.mCtrlEnable	= self.getControl( CONTROL_ID_RADIO_ENABLE )
		self.mCtrlEnable.setLabel( MR_LANG( 'Customized Channel Logos' ) )
		if GetSetting( 'CUSTOM_ICON' ) == 'true' :
			self.mCtrlEnable.setSelected( True )
		else :
			self.mCtrlEnable.setSelected( False )
		self.mCtrlImportUSB			= self.getControl( CONTROL_ID_BUTTON_USB )
		self.mCtrlImportInternet	= self.getControl( CONTROL_ID_BUTTON_INTERNET )
		self.mCtrlClear				= self.getControl( CONTROL_ID_BUTTON_CLEAR )
		self.mCtrlOK				= self.getControl( CONTROL_ID_BUTTON_OK )
		self.mCtrlCancel			= self.getControl( CONTROL_ID_BUTTON_CANCEL )
		self.mCtrlLoaded			= self.getControl( CONTROL_ID_LABEL_LOADED )

		self.mCtrlImportUSB.setLabel( MR_LANG( 'Load Icons from USB' ) )
		self.mCtrlImportInternet.setLabel( MR_LANG( 'Load Icons via Internet' ) )
		self.mCtrlClear.setLabel( MR_LANG( 'Remove All Customized Logos' ) )
		self.mCtrlLoaded.setLabel( MR_LANG( '0 Icon Loaded' ) )
		self.DisableControl( )


	def onClick( self, aControlId ) :
		if aControlId == CONTROL_ID_RADIO_ENABLE :
			if self.mCtrlEnable.isSelected( ) :
				SetSetting( 'CUSTOM_ICON', 'true' )
				pvr.ChannelLogoMgr.GetInstance( ).mUseCustomPath = 'true'
			else :
				SetSetting( 'CUSTOM_ICON', 'false' )
				pvr.ChannelLogoMgr.GetInstance( ).mUseCustomPath = 'false'

			self.DisableControl( )

		elif aControlId == CONTROL_ID_BUTTON_USB :
			usbPath = self.mDataCache.USB_GetMountPath( )
			if not usbPath :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Please insert a USB flash memory' ) )
				dialog.doModal( )
				return

			ziplist = self.GetZipFileFromUSB( usbPath )
			if ziplist :
				dialog = xbmcgui.Dialog( )
				ret = dialog.select( MR_LANG( 'Select Zip File for Channel Icons' ), ziplist, False, 0 )
				if ret >= 0 :
					retlist = self.CheckZipFileUsb( usbPath, ziplist[ ret ] )
					if retlist :
						self.LoadChannelLogo( TEMP_LOGO_PATH, retlist )
						self.DisableControl( )

		elif aControlId == CONTROL_ID_BUTTON_INTERNET :
			res = self.SelectInternetLogo( )
			if res :
				if self.DownloadLogo( res ) :
					retlist = self.CheckZipFileInternet( )
					if retlist :
						self.LoadChannelLogo( TEMP_LOGO_PATH, retlist )
						self.DisableControl( )
				else :
					dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
					dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Downlaod process failed' ) )
					dialog.doModal( )

		elif aControlId == CONTROL_ID_BUTTON_CLEAR :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( MR_LANG( 'Delete all customized channel logos?' ), MR_LANG( 'All customized channel logos will be erased' ) )
			dialog.doModal( )
			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
				xbmc.executebuiltin( "ActivateWindow(busydialog)" )
				os.system( 'rm -rf %s' % TEMP_LOGO_PATH )
				os.system( 'rm -rf %s' % CUSTOM_LOGO_PATH )
				os.system( 'sync' )
				pvr.ChannelLogoMgr.GetInstance( ).LoadCustom( )
				SetSetting( 'CUSTOM_ICON', 'false' )
				pvr.ChannelLogoMgr.GetInstance( ).mUseCustomPath = 'false'
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Restart Required' ), MR_LANG( 'System restart is needed in order to apply changes' ) )
				dialog.doModal( )
				xbmc.executebuiltin( "Dialog.Close(busydialog)" )
				self.close( )
				time.sleep( 0.2 )


		elif aControlId == CONTROL_ID_BUTTON_OK :
			self.DoOK( )

		elif aControlId == CONTROL_ID_BUTTON_CANCEL :
			self.CloseDialog( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.CloseDialog( )


	def onFocus( self, aControlId ) :
		pass


	def CloseDialog( self ) :
		self.DeleteTempLogo( )
		self.close( )
		time.sleep( 0.2 )
		

	def DoOK( self ) :
		xmlpath = CUSTOM_LOGO_PATH + '/ChannelLogo.xml'
		progressDialog = None
		onceCanceld = True
		try :
			xbmc.executebuiltin( "ActivateWindow(busydialog)" )

			if not os.path.exists( CUSTOM_LOGO_PATH ) :
				os.system( 'mkdir %s' % CUSTOM_LOGO_PATH )
			if not os.path.exists( xmlpath ) :
				oldhash = None
			else :
				parseTree = ElementTree.parse( xmlpath )
				treeRoot = parseTree.getroot( )
				oldhash = {}
				for node in treeRoot.findall( 'logo' ) :
					oldhash[ node.get( 'id' ) ] =  node.text

			xbmc.executebuiltin( "Dialog.Close(busydialog)" )

			if oldhash :
				mergehash = dict( oldhash, **self.mIconHash )
				outputFile = open( xmlpath + '.tmp', 'w' )
				outputFile.writelines( '<?xml version="1.0" encoding="utf-8"?>\n' )
				outputFile.writelines( '<Logolist>\n' )

				filecount = len( mergehash )
				strInit = MR_LANG( 'Initializing process' ) + '...'
				strReady = MR_LANG( 'Ready to start' ) + '...'
				percent = 0
				count = 0
				progressDialog = xbmcgui.DialogProgress( )
				progressDialog.create( MR_LANG( 'Copy Files' ), strInit )
				progressDialog.update( percent, strReady )

				for hash in mergehash :
					if self.mIconHash.get( hash, None ) and oldhash.get( hash, None ) :
						rmfilename = '%s/%s' % ( CUSTOM_LOGO_PATH, oldhash.get( hash, None ) )
						os.system( 'rm %s' % rmfilename )
						copyfile = self.mIconHash.get( hash, None )
						os.system( 'cp %s %s/' % ( copyfile, CUSTOM_LOGO_PATH ) )

					elif self.mIconHash.get( hash, None ) and not oldhash.get( hash, None ) :
						copyfile = self.mIconHash.get( hash, None )
						os.system( 'cp %s %s/' % ( copyfile, CUSTOM_LOGO_PATH ) )

					filename = mergehash.get( hash, None )
					filename = filename.split( '/' )
					filename = filename[ len( filename ) -1 ]
					outputFile.writelines( '\t<logo id= "%s">%s</logo>\n' % ( hash, filename ) )

					count = count + 1
					if progressDialog.iscanceled( ) and onceCanceld :
						xbmc.executebuiltin( 'Notification(%s, %s, 3000, DefaultIconInfo.png)' % ( MR_LANG( 'Please Wait' ), MR_LANG( 'Cancellation in progrss...' ) ) )
						onceCanceld = False

					percent = int( 1.0 * count / filecount * 100 )
					if percent > 99 :
						percent = 99
					strCopy = MR_LANG( 'Copying files' ) + '...'
					progressDialog.update( percent, strCopy, '%s' % mergehash.get( hash, None ).strip( ) )

				outputFile.writelines( '</Logolist>\n' )
				outputFile.close( )
				os.system( 'cp %s %s' % ( xmlpath + '.tmp', xmlpath ) )
				os.system( 'sync' )

				progressDialog.update( 100, MR_LANG( 'Copying logo files' ), MR_LANG( 'Complete' ) )
				time.sleep( 1 )
				progressDialog.close( )
			else :
				outputFile = open( xmlpath + '.tmp', 'w' )
				outputFile.writelines( '<?xml version="1.0" encoding="utf-8"?>\n' )
				outputFile.writelines( '<Logolist>\n' )

				filecount = len( self.mIconHash )
				strInit = MR_LANG( 'Initializing process' ) + '...'
				strReady = MR_LANG( 'Ready to start' ) + '...'
				percent = 0
				count = 0
				progressDialog = xbmcgui.DialogProgress( )
				progressDialog.create( MR_LANG( 'Copy Files' ), strInit )
				progressDialog.update( percent, strReady )

				for hash in self.mIconHash :
					filename = self.mIconHash.get( hash, None )
					try :
						os.system( 'cp %s %s/' % ( filename, CUSTOM_LOGO_PATH ) )
					except Exception, e :
						continue

					filename = filename.split( '/' )
					filename = filename[ len( filename ) -1 ]
					outputFile.writelines( '\t<logo id= "%s">%s</logo>\n' % ( hash, filename ) )

					count = count + 1
					if progressDialog.iscanceled( ) and onceCanceld :
						xbmc.executebuiltin( 'Notification(%s, %s, 3000, DefaultIconInfo.png)' % ( MR_LANG( 'Please Wait' ), MR_LANG( 'Cancellation in progrss...' ) ) )
						onceCanceld = False

					percent = int( 1.0 * count / filecount * 100 )
					if percent > 99 :
						percent = 99
					strCopy = MR_LANG( 'Copying files' ) + '...'
					progressDialog.update( percent, strCopy, '%s' % self.mIconHash.get( hash, None ).strip( ) )

				outputFile.writelines( '</Logolist>\n' )
				outputFile.close( )
				os.system( 'cp %s %s' % ( xmlpath + '.tmp', xmlpath ) )
				os.system( 'sync' )

				progressDialog.update( 100, MR_LANG( 'Copying logo files' ), MR_LANG( 'Complete' ) )
				time.sleep( 1 )
				progressDialog.close( )

			pvr.ChannelLogoMgr.GetInstance( ).LoadCustom( )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Restart Required' ), MR_LANG( 'System restart is needed in order to apply changes' ) )
			dialog.doModal( )
			self.CloseDialog( )

		except Exception, e :
			LOG_TRACE( 'import ok process except = %s' % e )
			xbmc.executebuiltin( "Dialog.Close(busydialog)" )
			if progressDialog :
				progressDialog.close( )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Importing channel logos failed to complete' ), MR_LANG( 'All customized logo data will be erased' ) )
			dialog.doModal( )
			os.system( 'rm -rf %s' % CUSTOM_LOGO_PATH )
			self.CloseDialog( )


	def CheckPathXmlBase( self, aPath, aFilelist, aXmlfile ) :
		try :
			count = 0
			self.mIconHash = {}
			xmlpath = '%s/%s' % ( aPath, aXmlfile )
			verifypath = xmlpath[ : xmlpath.rindex( '/' )]
			parseTree = ElementTree.parse( xmlpath )
			treeRoot = parseTree.getroot( )
			for node in treeRoot.findall( 'logo' ) :
				filename = '%s/%s' % ( verifypath, node.text.encode('utf-8') )
				if os.path.exists( filename ) :
					self.mIconHash[ node.get( 'id' ) ] =  filename
					count = count + 1

			return count
		except Exception, e :
			LOG_TRACE( 'Exception CheckPathXmlBase = %s' % e )
			return 0


	def CheckPath( self, aPath, aFilelist ) :
		try :
			if os.path.exists( aPath ) :
				count = 0
				self.mIconHash = {}
				for file in aFilelist :
					if file.endswith( '.xml' ) :
						count = self.CheckPathXmlBase( aPath, aFilelist, file )
						return count
					elif file.endswith( '.png' ) :
						filename = '%s/%s' % ( aPath, file )
						imagename = filename.split( '/' )
						imagename = imagename[ len( imagename ) -1 ]
						if len( imagename.split( '_' ) ) == 10 and len( imagename.split( '.' ) ) == 2 :
							count = count + 1
							sid = int( imagename.split( '_' )[3], 16 )
							longitude = int( imagename.split( '_' )[6][0:len( imagename.split( '_' )[6])-4], 16 )
							self.mIconHash[ '%s_%s' % ( longitude, sid ) ] = filename

				return count
			else :
				return 0

		except Exception, e :
			LOG_TRACE( 'Exception CheckPath = %s' % e )
			return 0


	def LoadChannelLogo( self, aPath, aFilelist ) :
		xbmc.executebuiltin( "ActivateWindow(busydialog)" )
		checkedItems = self.CheckPath( aPath, aFilelist )
		xbmc.executebuiltin( "Dialog.Close(busydialog)" )
		self.mCheckedItem = checkedItems
		self.mCtrlLoaded.setLabel( '%s %s' % ( checkedItems, MR_LANG( 'Icons Loaded' ) ) )
		if checkedItems :
			self.mCheckedItem	= checkedItems
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Complete' ), MR_LANG( '%s %s\n%s' ) % ( checkedItems, MR_LANG( 'Icons loaded' ), MR_LANG( 'Select OK Button to apply icons' ) ) )
			dialog.doModal( )
		else :
			self.mCheckedItem = 0
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Invalid path' ) )
			dialog.doModal( )


	def GetZipFileFromUSB( self, aPath ) :
		zipfiles = []
		for filename in os.listdir( aPath ) :
			if filename.endswith( '.zip' ) :
				zipfiles.append( filename )

		if len( zipfiles ) > 0 :
			return zipfiles
		else :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'No zip file found in USB' ) )
			dialog.doModal( )
			return None


	def CheckZipFileUsb( self, aUsbPath, aFilename ) :
		filename = '%s/%s' % ( aUsbPath, aFilename )

		xbmc.executebuiltin( "ActivateWindow(busydialog)" )
		filelistzip = GetUnpackFilenames( filename )
		xbmc.executebuiltin( "Dialog.Close(busydialog)" )

		if filelistzip and len( filelistzip ) > 0 :
			self.DeleteTempLogo( )
			os.system( 'mkdir %s' % TEMP_LOGO_PATH )
			retlist = self.ExtractZipFile( filename, filelistzip )
			if retlist :
				return retlist

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
		dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Extracting zip file failed to complete' ) )
		dialog.doModal( )
		return False


	def CheckZipFileInternet( self ) :
		try :
			zipfile = None
			md5file = None
			for filename in os.listdir( TEMP_LOGO_PATH ) :
				if filename.endswith( '.zip' ) :
					zipfile = '%s/%s' % ( TEMP_LOGO_PATH, filename )
				elif filename.endswith( '.md5sum' ) :
					md5file = '%s/%s' % ( TEMP_LOGO_PATH, filename )

			if zipfile and md5file :
				file = open( md5file, 'r' )
				md5sum = file.read( ).strip( )
				if CheckMD5Sum( zipfile, md5sum ) :
					xbmc.executebuiltin( "ActivateWindow(busydialog)" )
					filelistzip = GetUnpackFilenames( zipfile )
					xbmc.executebuiltin( "Dialog.Close(busydialog)" )
					if filelistzip and len( filelistzip ) > 0 :
						retlist = self.ExtractZipFile( zipfile, filelistzip )
						if retlist :
							return retlist

				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'The zip file is invalid or corrupted' ) )
				dialog.doModal( )
				return False
			else :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Downloading zip file failed to complete' ) )
				dialog.doModal( )
				return False

		except Exception, e :
			LOG_TRACE( 'CheckZipFileInternet except %s' % e )
			self.DeleteTempLogo( )
			return False


	def ExtractZipFile( self, aFilename, aFilelist ) :
		progressDialog = None
		try :
			filecount = len( aFilelist )
			strInit = MR_LANG( 'Initializing process' ) + '...'
			strReady = MR_LANG( 'Ready to start' ) + '...'
			percent = 0
			progressDialog = xbmcgui.DialogProgress( )
			progressDialog.create( MR_LANG( 'Extract Zip File' ), strInit )
			progressDialog.update( percent, strReady )

			os.system( 'echo unzip %s -d %s > /tmp/channellogo.sh' % ( aFilename, TEMP_LOGO_PATH ) )
			os.system( 'chmod 777 /tmp/channellogo.sh' )
			pipe = Popen( '/tmp/channellogo.sh', shell=True, stdout=PIPE )
			count = 1

			while pipe.poll( ) == None :
				if progressDialog.iscanceled( ) :
					strCancel = MR_LANG( 'Cancelling' ) + '...'
					progressDialog.update( percent, strCancel )
					self.DeleteTempLogo( )
					pipe.kill( )
					progressDialog.update( 0, '' )
					progressDialog.close( )
					return None

				line = pipe.stdout.readline( )
				if line != '' :
					percent = int( 1.0 * count / filecount * 100 )
					if percent > 99 :
						percent = 99
					strCopy = MR_LANG( 'Extracting data' ) + '...'
					progressDialog.update( percent, strCopy, '%s' % line.strip( ) )
					count = count + 1

			progressDialog.update( 100, MR_LANG( 'Extracting Zip File' ), MR_LANG( 'Complete' ) )
			time.sleep( 1 )
			progressDialog.update( 0, '' )
			progressDialog.close( )
			return aFilelist

		except Exception, e :
			LOG_TRACE( 'ExtractZipFile except = %s' % e )
			self.DeleteTempLogo( )
			if progressDialog :
				progressDialog.close( )
			return None


	def SelectInternetLogo( self ) :
		try :
			xbmc.executebuiltin( "ActivateWindow(busydialog)" )
			logofile = urllib2.urlopen( E_DEFAULT_LOGO_DIRECTORY , None, 20 )
			xbmc.executebuiltin( "Dialog.Close(busydialog)" )
			logofiledata = logofile.readlines( )
			if logofiledata != '' and logofiledata != 'Error' :
				logolist = []
				for logo in logofiledata :
					logo = logo.strip( )
					if logo.endswith( '.zip' ) :
						logo = logo.split( '.' )
						logo = logo[0]
						logolist.append( logo.strip( ) )

				dialog = xbmcgui.Dialog( )
				ret = dialog.select( MR_LANG( 'Select Channel Icon Package' ), logolist, False, 0 )
				if ret >= 0 :
					return logolist[ ret ] + '.zip'

				return None
		except Exception, e :
			xbmc.executebuiltin( "Dialog.Close(busydialog)" )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Downloading zip file failed to complete' ) )
			dialog.doModal( )
			LOG_TRACE( 'SelectInternetLogo except = %s' % e )
			return None


	def DownloadLogo( self, aZipfile ) :
		try :
			xbmc.executebuiltin( "ActivateWindow(busydialog)" )
			self.DeleteTempLogo( )
			os.system( 'mkdir %s' % TEMP_LOGO_PATH )
			downpath = '%s/%s' % ( E_DEFAULT_LOGO_PATH, aZipfile )
			data = urllib2.urlopen( downpath, None, 20 )
			output = open( '%s/%s' % ( TEMP_LOGO_PATH, aZipfile ) , 'wb' )
			output.write( data.read( ) )
			output.close( )

			downpath = '%s/%s.md5sum' % ( E_DEFAULT_LOGO_PATH, aZipfile )
			data = urllib2.urlopen( downpath, None, 20 )
			output = open( '%s/%s.md5sum' % ( TEMP_LOGO_PATH, aZipfile ) , 'wb' )
			output.write( data.read( ) )
			output.close( )
			xbmc.executebuiltin( "Dialog.Close(busydialog)" )
			return True

		except Exception, e :
			LOG_TRACE( 'DownloadLogo except = %s' % e )
			xbmc.executebuiltin( "Dialog.Close(busydialog)" )
			self.DeleteTempLogo( )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Downloading zip file failed to complete' ) )
			dialog.doModal( )
			return False


	def DeleteTempLogo( self ) :
		xbmc.executebuiltin( "ActivateWindow(busydialog)" )
		os.system( 'rm -rf %s' % TEMP_LOGO_PATH )
		os.system( 'sync' )
		xbmc.executebuiltin( "Dialog.Close(busydialog)" )


	def DisableControl( self ) :
		if self.mCtrlEnable.isSelected( ) :
			self.mCtrlImportUSB.setEnabled( True )
			self.mCtrlImportInternet.setEnabled( True )
		else :
			self.mCtrlImportUSB.setEnabled( False )
			self.mCtrlImportInternet.setEnabled( False )

		if self.mCheckedItem and self.mCtrlEnable.isSelected( ) :
			self.mCtrlOK.setEnabled( True )
		else :
			self.mCtrlOK.setEnabled( False )

