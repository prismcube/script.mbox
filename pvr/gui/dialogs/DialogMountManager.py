from pvr.gui.WindowImport import *
import urlparse

E_RECORDPATH_SETUPMENU_GROUP_ID	 = 9010
E_RECORDPATH_SUBMENU_LIST_ID     = 9000
E_RECORDPATH_SETTING_DESCRIPTION = 1003

E_IMAGE_DIALOG_BACKGROUND = 9001
E_GROUP_ID_SHOW_INFO      = 300
E_PROGRESS_NETVOLUME      = 301
E_LABEL_ID_USE_INFO       = 302

E_NETWORK_VOLUME_ADD = 0
E_NETWORK_VOLUME_EDIT = 1
E_NETWORK_VOLUME_SELECT = 2

E_DEFAULT_PATH_INTERNAL_HDD = 0
E_DEFAULT_PATH_NETWORK_VOLUME = 1

E_ID_NO  = 0
E_ID_YES = 1


class DialogMountManager( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		self.mIsOk					= False


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.mCtrlGroupShowInfo = self.getControl( E_GROUP_ID_SHOW_INFO )
		self.mCtrlLabelUseInfo = self.getControl( E_LABEL_ID_USE_INFO )
		self.mCtrlProgressUse = self.getControl( E_PROGRESS_NETVOLUME )
		#self.setProperty( 'DialogDrawFinished', 'False' )

		self.mDialogWidth = self.getControl( E_IMAGE_DIALOG_BACKGROUND ).getWidth( )
		lblTitle = MR_LANG( 'Add/Remove Record Path' )
		self.SetHeaderLabel( lblTitle )

		self.mDefaultPathVolume = None
		self.mFreeHDD  = 0
		self.mTotalHDD = 0
		self.mHDDStatus = False
		if CheckHdd( ) :
			self.mHDDStatus = True
			self.mTotalHDD = self.mCommander.Record_GetPartitionSize( )
			self.mFreeHDD  = self.mCommander.Record_GetFreeMBSize( )

		self.mNetVolumeListHash = {}
		self.mMode = E_NETWORK_VOLUME_ADD
		self.mSelectIdx = -1
		self.mInputMountPath = E_DEFAULT_PATH_SMB_POSITION
		self.mNetVolume = ElisENetworkVolume( )
		self.mNetVolume.mRemotePath = ''
		self.mNetVolume.mMountPath = ''
		self.mNetVolumeList = self.mDataCache.Record_GetNetworkVolume( )
		if self.mNetVolumeList and len( self.mNetVolumeList ) > 0 :
			self.mSelectIdx = 0
			self.mMode = E_NETWORK_VOLUME_SELECT
			#check default
			for netVolume in self.mNetVolumeList :
				hashkey = '%s:%s'% ( netVolume.mRemoteFullPath, netVolume.mMountPath )
				self.mNetVolumeListHash[hashkey] = netVolume

				if netVolume.mIsDefaultSet :
					self.mDefaultPathVolume = netVolume

		self.InitItem( )

		self.mEventBus.Register( self )
		self.setProperty( 'DialogDrawFinished', 'True' )
		#self.mInitialized = True


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.mIsOk = actionId

		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			if self.mMode != E_NETWORK_VOLUME_SELECT and self.mNetVolumeList and len( self.mNetVolumeList ) > 0 :
				self.mMode = E_NETWORK_VOLUME_SELECT
				self.DrawItem( )
				LOG_TRACE( '[MountManager] cancel done, restore[%s]'% self.mSelectIdx )
				return

			self.Close( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )
			
		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )

		elif Action.ACTION_PLAYER_PLAY or actionId == Action.ACTION_PAUSE :
			self.SetMountByVolumeList( )


	def onClick( self, aControlId ) :
		if aControlId == E_SETTING_DIALOG_BUTTON_CLOSE :
			self.Close( )

		groupId = self.GetGroupId( aControlId )
		if groupId == E_DialogInput07 or groupId == E_DialogInput02 : #apply, delete
			xbmc.executebuiltin( 'ActivateWindow(busydialog)' )
			self.DoNetworkVolume( groupId )
			xbmc.executebuiltin( 'Dialog.Close(busydialog)' )

		if groupId == E_DialogInput03 : #select
			if self.ShowMountList( ) :
				self.DrawItem( )

		else :
			#if groupId == E_DialogSpinEx01 or groupId == E_DialogSpinEx02 : #isDefault
			#	self.ControlSelect( )

			self.SetNetworkVolume( groupId )


	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		if self.mWinId == xbmcgui.getCurrentWindowDialogId( ) :

			if aEvent.getName( ) == ElisEventUSBRecordVolumeAttach.getName( ) or \
			   aEvent.getName( ) == ElisEventUSBRecordVolumeDetach.getName( ) :
				self.mNetVolumeList = self.mDataCache.Record_GetNetworkVolume( )
				#for netvolume in self.mNetVolumeList :
				#	netvolume.printdebug()


	def Close( self ) :
		#self.SetMountByVolumeList( )
		self.mEventBus.Deregister( self )
		self.CloseDialog( )


	def GetNetworkVolumes( self ) :
		return self.mNetVolumeList


	def GetDefaultVolume( self ) :
		return self.mDefaultPathVolume


	def GetVolumeIDs( self, aReqVolume = None ) :
		getVolume = None
		if aReqVolume :
			hashKey = '%s:%s'% ( aReqVolume.mRemoteFullPath, aReqVolume.mMountPath )
			getVolume = self.mNetVolumeListHash.get( hashKey, None )

		return getVolume


	def GetVolumeInfo( self, aNetVolume = None ) :
		lblSelect = MR_LANG( 'HDD' )
		lblOnline = E_TAG_TRUE
		useFree   = self.mFreeHDD
		useTotal  = self.mTotalHDD
		useInfo   = 0
		if aNetVolume :
			lblSelect = os.path.basename( aNetVolume.mMountPath )
			if not aNetVolume.mOnline :
				lblOnline = E_TAG_FALSE
			useFree = aNetVolume.mFreeMB
			if aNetVolume.mTotalMB > 0 :
				useTotal = aNetVolume.mTotalMB

		else :
			#hdd not
			if useTotal < 1 :
				lblOnline = E_TAG_FALSE

		if useTotal > 0 :
			useInfo = int( ( ( 1.0 * ( useTotal - useFree ) ) / useTotal ) * 100 )

		lblByte = '%sMB'% useFree
		if useFree > 1024 :
			lblByte = '%sGB'% ( useFree / 1024 )
		elif useFree < 0 :
			lblByte = '%sKB'% ( useFree * 1024 )
		lblPercent = '%s%%, %s %s'% ( useInfo, lblByte, MR_LANG( 'Free' ) )

		return lblSelect, useInfo, lblPercent, lblOnline


	def SetEditEnableVolume( self, aCheckControl = None ) :
		deleteVisible = False
		deleteName = MR_LANG( 'Delete' )
		selectName = MR_LANG( 'Add' )
		netVolume = self.GetVolumeIDs( self.mNetVolume )
		if netVolume :
			if aCheckControl == E_DialogSpinEx02 :
				if netVolume.mSupport4G == self.mNetVolume.mSupport4G :
					self.DrawItem( E_DialogSpinEx02 )
					return

			self.mMode = E_NETWORK_VOLUME_EDIT
			selectName = MR_LANG( 'Edit' )
			deleteName = MR_LANG( 'Cancel' )
			deleteVisible = True

			lblSelect, useInfo, lblPercent, lblOnline = self.GetVolumeInfo( netVolume )
			self.setProperty( 'NetVolumeConnect', lblOnline )
			self.setProperty( 'NetVolumeUse', lblPercent )
			self.mCtrlProgressUse.setPercent( useInfo )
			ResetPositionVolumeInfo( self, lblPercent, self.mDialogWidth, E_GROUP_ID_SHOW_INFO, E_LABEL_ID_USE_INFO )

		else :
			#new
			self.mNetVolume.mSupport4G = 0
			self.mNetVolume.mIsDefaultSet = 0
			self.SelectPosition( E_DialogSpinEx02, 0 )
			#self.SetControlLabel2String( E_DialogInput04, USER_ENUM_LIST_YES_NO[0] )

			if self.mNetVolumeList and len( self.mNetVolumeList ) > 0 :
				self.mMode = E_NETWORK_VOLUME_ADD
				deleteName = MR_LANG( 'Cancel' )
				deleteVisible = True

		self.SetControlLabelString( E_DialogInput03, selectName )
		self.SetControlLabel2String( E_DialogInput03, '' )
		self.SetEnableControl( E_DialogInput03, False )

		self.SetControlLabel2String( E_DialogInput02, deleteName )
		self.SetVisibleControl( E_DialogInput02, deleteVisible )
		self.SetEnableControl( E_DialogInput02, True )


	def SetNetworkVolume( self, aInput, aBrowseTitle = '' ) :

		# remote path
		if aInput == E_DialogInput05 :
			browseTitle = MR_LANG( 'Select' )
			if aInput == E_DialogInput05 :
				browseTitle = '%s %s'% ( browseTitle, MR_LANG( 'Record Path' ) )
			#elif aInput == E_DialogInput06 :
			#	browseTitle = '%s %s'% ( browseTitle, MR_LANG( 'Mount Path' ) )

			getPath = xbmcgui.Dialog( ).browsedirectory( browseTitle )
			LOG_TRACE( '----------getPath[%s]'% getPath )
			if not getPath or getPath == 'None' :
				LOG_TRACE( 'not selected path' )
				return

			isFail = True
			lblLine = ''
			lblTitle= MR_LANG( 'Error' )
			urlType = urlparse.urlparse( getPath ).scheme
			LOG_TRACE( '------------------------urlType[%s]'% urlType )
			if aInput == E_DialogInput06 :
				if urlType :
					lblLine = MR_LANG( 'Invalid record path chosen' )
				else :
					isFail = False

			else :
				if urlType :
					self.mInputMountPath = E_DEFAULT_PATH_SMB_POSITION
					if urlType == 'smb' :
						isFail = False
						self.mInputMountPath = E_DEFAULT_PATH_SMB_POSITION
						LOG_TRACE( '-----------------------smb getPath[%s]'% getPath )

					elif urlType == 'nfs' :
						isFail = False
						self.mInputMountPath = E_DEFAULT_PATH_NFS_POSITION

					elif urlType == 'ftp' :
						isFail = False
						self.mInputMountPath = E_DEFAULT_PATH_FTP_POSITION

					else :
						# upnp, zeroconf, daap, ...
						lblLine = MR_LANG( 'No %s support' ) % urlType
				else :
					lblLine = MR_LANG( 'Invalid record path chosen' )

			if isFail :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( lblTitle, lblLine )
				dialog.doModal( )
				return

			#init value
			urlHost, urlPort, urlUser, urlPass, urlPath, urlFile, urlSize = GetParseUrl( getPath )
			lblPath  = '%s%s'% ( urlHost, os.path.dirname( urlPath ) )
			self.mNetVolume.mRemotePath = '//' + lblPath
			self.mNetVolume.mRemoteFullPath = getPath
			lblMount = os.path.basename( lblPath )
			self.mNetVolume.mMountPath = ''
			if lblMount : # select root? then mount name is None
				self.mNetVolume.mMountPath = os.path.join( self.mInputMountPath, lblMount )
			self.SetControlLabel2String( E_DialogInput05, lblPath )
			self.SetControlLabel2String( E_DialogInput06, lblMount )
			LOG_TRACE( 'lblPath[%s] remote[%s] fullpath[%s] mountPath[%s]'% ( lblPath, self.mNetVolume.mRemotePath, self.mNetVolume.mRemoteFullPath, self.mNetVolume.mMountPath ) )
			self.SetEditEnableVolume( )

		elif aInput == E_DialogInput06 :
			if not self.mNetVolume.mRemotePath :
				lblLine = MR_LANG( 'Enter record path first' )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), lblLine )
				dialog.doModal( )
				return

			mntName = os.path.basename( self.mNetVolume.mMountPath )
			label = MR_LANG( 'Enter New Path Name' )
			kb = xbmc.Keyboard( mntName, label, False )
			kb.doModal( )

			isConfirmed = kb.isConfirmed( )
			mntName = kb.getText( )
			if not isConfirmed or mntName == None or mntName == '' :
				LOG_TRACE('[Edit] No name or cencel')
				return

			symbolPattern = '\'|\"|\%|\^|\&|\*|\`'
			if bool( re.search( symbolPattern, mntName, re.IGNORECASE ) ) :
				LOG_TRACE( '[Edit] invalid characters' )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'That name contains invalid characters' ) )
				dialog.doModal( )
				return

			self.mNetVolume.mMountPath = os.path.join( self.mInputMountPath, mntName )
			self.SetControlLabel2String( E_DialogInput06, mntName )
			LOG_TRACE( 'lblPath[%s] mount[%s]'% ( mntName, self.mNetVolume.mMountPath ) )
			self.SetEditEnableVolume( )


		elif aInput == E_DialogSpinEx02 :
			self.mNetVolume.mSupport4G = self.GetSelectedIndex( E_DialogSpinEx02 )
			self.SetEditEnableVolume( E_DialogSpinEx02 )


	def DoDeleteVolume( self, aNetVolume = None, aIsUMount = True ) :
		if not aNetVolume :
			LOG_TRACE( '[MountManager] Fail, netVolume is None' )
			return False

		ret = self.mDataCache.Record_DeleteNetworkVolume( aNetVolume )
		LOG_TRACE( '[MountManager] Record_DeleteNetworkVolume[%s]'% ret )
		if ret :
			if aIsUMount :
				os.system( '/bin/umount -fl %s'% aNetVolume.mMountPath )
				os.system( 'sync' )
				mntHistory = ExecuteShell( 'mount' )
				if mntHistory and ( not bool( re.search( '%s'% aNetVolume.mMountPath, mntHistory, re.IGNORECASE ) ) ) :
					RemoveDirectory( aNetVolume.mMountPath )

			listCount = len( self.mNetVolumeList )
			if not self.mNetVolumeList or listCount < 1 :
				self.mSelectIdx = -1

			else :
				if self.mSelectIdx < listCount - 1 :
					pass

				else :
					if listCount - 1 > 0 :
						self.mSelectIdx = listCount - 2
					else :
						self.mSelectIdx = -1

		return ret


	def DoNetworkVolume( self, aInput = None ) :

		if aInput :
			isFail = True
			lblLine = ''
			lblTitle= MR_LANG( 'Error' )
			if aInput == E_DialogInput07 :
				mountPath = ''
				lblLine = MR_LANG( 'Could not apply' )
				if self.mNetVolume.mRemotePath and self.mNetVolume.mMountPath :
					netVolume = self.GetVolumeIDs( self.mNetVolume )
					if netVolume and \
					   netVolume.mRemoteFullPath == self.mNetVolume.mRemoteFullPath and \
					   netVolume.mMountPath == self.mNetVolume.mMountPath and \
					   netVolume.mSupport4G == self.mNetVolume.mSupport4G :
						isAdd = False
						#lblLine = '%s\'%s\' on \'%s\''% ( MR_LANG( 'The path is already mounted' ), netVolume.mRemotePath, os.path.basename( self.mNetVolume.mMountPath ) )
						lblLine = '%s \'%s\''% ( MR_LANG( 'The path is already mounted' ), os.path.basename( self.mNetVolume.mMountPath ) )
						LOG_TRACE( '[MountManager] detected same path mnt[%s] new[%s]'% ( netVolume.mMountPath, self.mNetVolume.mMountPath ) )

					else :
						#add new, edit
						urlHost, urlPort, urlUser, urlPass, urlPath, urlFile, urlSize = GetParseUrl( self.mNetVolume.mRemoteFullPath )
						if not IsIPv4( urlHost ) :
							hostip = ExecuteShell( 'net lookup %s'% urlHost )
							if hostip and IsIPv4( hostip ) :
								urlHost = hostip

						remotePath = '//%s%s'% ( urlHost, os.path.dirname( urlPath ) )
						mountCmd   = 'mount -t cifs -o username=%s,password=%s %s %s'% ( urlUser, urlPass, remotePath, self.mNetVolume.mMountPath )
						urlType = urlparse.urlparse( self.mNetVolume.mRemoteFullPath ).scheme
						if urlType == 'smb' :
							remotePath = '//%s%s'% ( urlHost, os.path.dirname( urlPath ) )
							mountCmd = 'mount -t cifs -o username=%s,password=%s %s %s'% ( urlUser, urlPass, remotePath, self.mNetVolume.mMountPath )
						elif urlType == 'nfs' :
							remotePath = '%s:%s'% ( urlHost, os.path.dirname( urlPath ) )
							mountCmd = 'mount -t nfs %s %s -o nolock,mountvers=4'% ( remotePath, self.mNetVolume.mMountPath )
						elif urlType == 'ftp' :
							remotePath = '%s:%s'% ( urlHost, os.path.dirname( urlPath ) )
							mountCmd = 'modprobe fuse && curlftpfs %s %s -o user=%s:%s,allow_other'% ( remotePath, self.mNetVolume.mMountPath, urlUser, urlPass  )

						self.mNetVolume.mMountCmd = mountCmd
						mountPath = MountToSMB( self.mNetVolume.mRemoteFullPath, self.mNetVolume.mMountPath, False )
						#LOG_TRACE( '----------------------------------mountPath[%s]'% mountPath )
						#self.mNetVolume.printdebug( )

						lblLine = MR_LANG( 'Unable to mount location' )
						if mountPath != '' :
							isAdd = True
							#is edit? delete old volume
							netVolume = self.GetVolumeIDs( self.mNetVolume )
							LOG_TRACE( '--------------------------find volume GetVolumeIDs[%s]'% netVolume )
							if netVolume :
								if not self.DoDeleteVolume( netVolume, False ) :
									isAdd = False
									#lblLine = '%s\'%s\' on \'%s\''% ( MR_LANG( 'The path is already mounted' ), netVolume.mRemotePath, os.path.basename( self.mNetVolume.mMountPath ) )
									lblLine = '%s \'%s\''% ( MR_LANG( 'The path is already mounted' ), os.path.basename( self.mNetVolume.mMountPath ) )

								LOG_TRACE( '[MountManager] detected same path mnt[%s] new[%s]'% ( netVolume.mMountPath, self.mNetVolume.mMountPath ) )

							if isAdd :
								lblLine = MR_LANG( 'Could not add this record path' )
								ret = self.mDataCache.Record_AddNetworkVolume( self.mNetVolume )
								LOG_TRACE( '----------------------------------ret[%s]'% ret )
								if ret :
									isFail = False
									lblLine = '\'%s\' %s'% ( os.path.basename( self.mNetVolume.mMountPath ), MR_LANG( 'is mounted' ) )

								else :
									# Add fail then restore umount
									os.system( '/bin/umount -fl %s'% mountPath )
									os.system( 'sync' )

						else :
							lblTitle = MR_LANG( 'Unable to mount location' )
							lblLine = MR_LANG( 'Make sure you have permission to access that folder' )

				else :
					lblLine = MR_LANG( 'Please enter path name' )

			elif aInput == E_DialogInput02 :
				if self.mMode != E_NETWORK_VOLUME_SELECT :
					self.mMode = E_NETWORK_VOLUME_SELECT
					self.DrawItem( )
					LOG_TRACE( '[MountManager] cancel done, restore[%s]'% self.mSelectIdx )
					return

				delTitle= MR_LANG( 'Delete' )
				delLine = MR_LANG( 'Do you want to delete this record path?' )
				delLine = '%s\n%s'% ( os.path.basename( self.mNetVolume.mMountPath ), delLine )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( delTitle, delLine )
				dialog.doModal( )
				if dialog.IsOK( ) != E_DIALOG_STATE_YES :
					LOG_TRACE( '[MountManager] Cancel delete' )
					return

				ret = self.DoDeleteVolume( self.mNetVolume )
				if ret :
					isFail = False
					#urlHost, urlPort, urlUser, urlPass, urlPath, urlFile, urlSize = GetParseUrl( self.mNetVolume.mRemoteFullPath )
					lblLine = '\'%s\' %s'% ( os.path.basename( self.mNetVolume.mMountPath ), MR_LANG( 'is removed' ) )


			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			if isFail :
				lblLine = '%s'% lblLine
				dialog.SetDialogProperty( lblTitle, lblLine )
				dialog.doModal( )
				return

			lblTitle= MR_LANG( 'Success' )
			dialog.SetDialogProperty( lblTitle, lblLine )
			dialog.doModal( )


		selectIdx = -1
		self.mNetVolumeListHash = {}
		self.mDefaultPathVolume = None
		defaultPath = E_DEFAULT_PATH_INTERNAL_HDD
		self.mNetVolumeList = self.mDataCache.Record_GetNetworkVolume( )
		if self.mNetVolumeList and len( self.mNetVolumeList ) > 0 :
			for netVolume in self.mNetVolumeList :
				selectIdx += 1
				hashkey = '%s:%s'% ( netVolume.mRemoteFullPath, netVolume.mMountPath )
				self.mNetVolumeListHash[hashkey] = netVolume
				if netVolume.mMountPath == self.mNetVolume.mMountPath :
					self.mSelectIdx = selectIdx

				if netVolume.mIsDefaultSet :
					self.mDefaultPathVolume = netVolume

			if not self.mHDDStatus and ( not self.mDefaultPathVolume ) :
				defaultPath = E_DEFAULT_PATH_NETWORK_VOLUME
				self.mDefaultPathVolume = self.mNetVolumeList[0]
				self.mDefaultPathVolume.mIsDefaultSet = 1
				self.mDataCache.Record_SetDefaultVolume( self.mDefaultPathVolume )

		self.mMode = E_NETWORK_VOLUME_SELECT
		#ElisPropertyEnum( 'Record Default Path Change', self.mCommander ).SetProp( defaultPath )

		self.DrawItem( )
		self.UpdateShell( )
		LOG_TRACE( '[MountManager] Done' )


	def InitItem( self ) :
		lblValue = MR_LANG( 'None' )
		self.ResetAllControl( )
		self.AddInputControl( E_DialogInput03, MR_LANG( 'Select' ), lblValue )
		self.AddInputControl( E_DialogInput02, '', MR_LANG( 'Delete' ) )

		self.AddInputControl( E_DialogInput05, MR_LANG( 'Record Path' ), lblValue )
		self.AddInputControl( E_DialogInput06, MR_LANG( 'Path Name' ), lblValue )
		self.AddUserEnumControl( E_DialogSpinEx02, MR_LANG( 'Split into 4GB files' ), USER_ENUM_LIST_YES_NO, 0 )
		#self.AddInputControl( E_DialogInput04, MR_LANG( 'Default Volume' ), USER_ENUM_LIST_YES_NO[0] )
		self.AddInputControl( E_DialogInput07, MR_LANG( 'Apply' ), '' )

		#visibleControlIds = [E_DialogInput02, E_DialogInput03, E_DialogInput05, E_DialogInput06, E_DialogSpinEx02, E_DialogInput07 ]
		#self.SetEnableControl( E_DialogInput04, False )

		self.InitControl( )
		self.SetAutoHeight( False )
		self.UpdateLocation( )

		self.DrawItem( )


	def DrawItem( self, aDefaultFocus = None ) :
		xbmc.executebuiltin( 'ActivateWindow(busydialog)' )
		defaultFocus = E_DialogInput05

		selectControlVisible = False
		disableConrols = []
		enableConrols = [E_DialogInput03, E_DialogInput02, E_DialogInput05, E_DialogInput06, E_DialogSpinEx02, E_DialogInput07]
		selectControl = MR_LANG( 'Add' )
		lblSelect = ''
		lblRemote = MR_LANG( 'None' )
		lblMount  = lblRemote
		isDefault = 0
		is4Gb     = 0
		usePercent= 0
		lblOnline = E_TAG_FALSE
		self.mNetVolume = ElisENetworkVolume( )
		self.mNetVolume.mRemotePath = ''
		self.mNetVolume.mMountPath = ''

		if self.mMode == E_NETWORK_VOLUME_ADD :
			disableConrols = [E_DialogInput03,E_DialogInput02]
			enableConrols = [E_DialogInput05, E_DialogInput06, E_DialogSpinEx02, E_DialogInput07]

		if self.mMode == E_NETWORK_VOLUME_SELECT and self.mSelectIdx > -1 :
			if self.mNetVolumeList and self.mSelectIdx < len( self.mNetVolumeList ) :
				#self.mSelectIdx = 0
				self.mMode = E_NETWORK_VOLUME_SELECT
				selectControlVisible = True
				selectControl = MR_LANG( 'Select' )
				defaultFocus = E_DialogInput03
				self.mNetVolume = deepcopy( self.mNetVolumeList[self.mSelectIdx] )
				getPath   = self.mNetVolume.mRemoteFullPath
				urlHost, urlPort, urlUser, urlPass, urlPath, urlFile, urlSize = GetParseUrl( getPath )
				urlType   = urlparse.urlparse( getPath ).scheme
				lblMount  = os.path.basename( self.mNetVolume.mMountPath )
				lblSelect = '[%s] %s'% ( urlType.upper(), lblMount )
				lblRemote = '%s%s'% ( urlHost, os.path.dirname( urlPath ) )
				isDefault = self.mNetVolume.mIsDefaultSet
				is4Gb     = self.mNetVolume.mSupport4G
				if self.mNetVolume.mOnline :
					lblOnline = E_TAG_TRUE
				if self.mNetVolume.mTotalMB > 0 :
					usePercent = int( ( ( 1.0 * ( self.mNetVolume.mTotalMB - self.mNetVolume.mFreeMB ) ) / self.mNetVolume.mTotalMB ) * 100 )

				if self.mNetVolume.mMountPath and bool( re.search( '%s\w\d+'% E_DEFAULT_PATH_USB_POSITION, self.mNetVolume.mMountPath, re.IGNORECASE ) ) :
					# usb? then enable false
					lblSelect = '[USB] %s'% lblMount
					enableConrols = [E_DialogInput03]
					disableConrols = [E_DialogInput02, E_DialogInput05, E_DialogInput06, E_DialogInput07, E_DialogSpinEx02]

		self.SetControlLabelString( E_DialogInput03, selectControl )
		self.SetControlLabel2String( E_DialogInput03, lblSelect )
		self.SetControlLabel2String( E_DialogInput02, MR_LANG( 'Delete' ) )

		self.SetControlLabel2String( E_DialogInput05, lblRemote )
		self.SetControlLabel2String( E_DialogInput06, lblMount )
		self.SelectPosition( E_DialogSpinEx02, is4Gb )
		#self.SetControlLabel2String( E_DialogInput04, USER_ENUM_LIST_YES_NO[isDefault] )

		self.SetEnableControls( enableConrols, True )
		self.SetEnableControls( disableConrols, False )
		self.SetVisibleControl( E_DialogInput02, selectControlVisible )

		if aDefaultFocus :
			defaultFocus = aDefaultFocus
		self.SetFocus( defaultFocus )

		#hdd size
		default_Path = MR_LANG( 'HDD' )
		default_lblOnline = E_TAG_TRUE
		default_usePercent = 0
		if self.mTotalHDD > 0 :
			default_usePercent = int( ( ( 1.0 * ( self.mTotalHDD - self.mFreeHDD ) ) / self.mTotalHDD ) * 100 )
			#LOG_TRACE( '--------------hdd use[%s] free[%s] total[%s]'% ( (self.mTotalHDD - self.mFreeHDD), self.mFreeHDD, self.mTotalHDD ) )
		else :
			#hdd is none
			default_lblOnline = E_TAG_FALSE

		default_byte = '%sMB'% self.mFreeHDD
		if self.mFreeHDD > 1024 :
			default_byte = '%sGB'% ( self.mFreeHDD / 1024 )
		elif self.mFreeHDD < 0 :
			default_byte = '%sKB'% ( self.mFreeHDD * 1024 )

		default_lblPercent = '%s%%, %s %s'% ( default_usePercent, default_byte, MR_LANG( 'Free' ) )

		#select size
		lblbyte = '%sMB'% self.mNetVolume.mFreeMB
		if self.mNetVolume.mFreeMB > 1024 :
			lblbyte = '%sGB'% ( self.mNetVolume.mFreeMB / 1024 )
		elif self.mNetVolume.mFreeMB < 0 :
			lblbyte = '%sKB'% ( self.mNetVolume.mFreeMB * 1024 )

		if self.mDefaultPathVolume :
			default_Path = self.mDefaultPathVolume.mMountPath
			if self.mDefaultPathVolume.mTotalMB > 0 :
				default_usePercent = int( ( ( 1.0 * ( self.mDefaultPathVolume.mTotalMB - self.mDefaultPathVolume.mFreeMB ) ) / self.mDefaultPathVolume.mTotalMB ) * 100 )
			default_lblPercent = '%s%%, %s %s'% ( default_usePercent, lblbyte, MR_LANG( 'Free' ) )

			default_lblOnline = E_TAG_FALSE
			if self.mDefaultPathVolume.mOnline :
				default_lblOnline = E_TAG_TRUE

		lblPercent = '%s%%, %s %s'% ( usePercent, lblbyte, MR_LANG( 'Free' ) )

		#default info
		#self.mCtrlLabelDefaultPath.setLabel( default_Path )
		#self.mCtrlLabelDefaultUse.setLabel( default_lblPercent )
		#self.mCtrlProgressDefaultUse.setPercent( default_usePercent )

		#select info
		self.mCtrlProgressUse.setPercent( usePercent )
		self.setProperty( 'NetVolumeUse', lblPercent )
		self.setProperty( 'NetVolumeConnect', lblOnline )
		ResetPositionVolumeInfo( self, lblPercent, self.mDialogWidth, E_GROUP_ID_SHOW_INFO, E_LABEL_ID_USE_INFO )

		xbmc.executebuiltin( 'Dialog.Close(busydialog)' )
		LOG_TRACE( '----------------------------------DrawItem property[%s]'% ElisPropertyEnum( 'Record Default Path Change', self.mCommander ).GetPropString( ) )


	def GetMountList( self ) :
		#self.mNetVolumeList = self.mDataCache.Record_GetNetworkVolume( )

		trackList = [ContextItem( MR_LANG( 'Add' ), 99 )]
		trackIndex = 0
		if self.mNetVolumeList and len( self.mNetVolumeList ) > 0 :
			for netVolume in self.mNetVolumeList :
				getPath = netVolume.mRemoteFullPath
				urlType = urlparse.urlparse( getPath ).scheme
				#urlHost, urlPort, urlUser, urlPass, urlPath, urlFile, urlSize = GetParseUrl( getPath )
				lblType = 'local'
				if urlType :
					lblType = '%s'% urlType.upper()
				else :
					if netVolume.mMountPath and bool( re.search( '%s\w\d+'% E_DEFAULT_PATH_USB_POSITION, netVolume.mMountPath, re.IGNORECASE ) ) :
						lblType = 'USB'

				#lblPath = '[%s]%s%s'% ( lblType, urlHost, os.path.dirname( urlPath ) )
				lblPath = '[%s]%s'% ( lblType, os.path.basename( netVolume.mMountPath ) )
				LOG_TRACE('mountPath idx[%s] urlType[%s] mRemotePath[%s] mMountPath[%s] isDefault[%s]'% ( trackIndex, urlType, netVolume.mRemotePath, netVolume.mMountPath, netVolume.mIsDefaultSet ) )

				trackList.append( ContextItem( lblPath, trackIndex ) )
				trackIndex += 1

		else :
			self.mNetVolumeList = []
			self.mSelectIdx = -1
			LOG_TRACE( 'Record_GetNetworkVolume none' )

		return trackList


	def ShowMountList( self ) :
		trackList = self.GetMountList( )
		LOG_TRACE( '[MountManager] Record_GetNetworkVolume len[%s]'% len( self.mNetVolumeList ) )

		if not trackList or len( trackList ) < 1 :
			LOG_TRACE( '[MountManager] show fail, mount list is None' )
			return

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( trackList, self.mSelectIdx + 1 )
		dialog.doModal( )

		selectAction = dialog.GetSelectedAction( )
		if selectAction < 0 :
			return

		if selectAction == 99 :
			self.mMode = E_NETWORK_VOLUME_ADD
			self.DrawItem( E_DialogInput05 )
			return

		LOG_TRACE('Select[%s --> %s]'% ( self.mSelectIdx, selectAction ) )

		if selectAction < len( trackList ) :
			self.mSelectIdx = selectAction
			#self.SetControlLabel2String( E_DialogInput03, '%s(%s/%s)'% ( trackList[selectAction].mDescription, self.mSelectIdx + 1, len( self.mNetVolumeList ) ) )

		return True


	def SetMountByVolumeList( self ) :
		volumeList = self.mDataCache.Record_GetNetworkVolume( )
		if not volumeList or len( volumeList ) < 1 :
			LOG_TRACE( '[MountManager] passed, volume list None' )
			return

		xbmc.executebuiltin( 'ActivateWindow(busydialog)' )

		RemoveDirectory( E_DEFAULT_NETWORK_VOLUME_SHELL )
		volumeCount = len( volumeList )
		defVolume = None
		count = 0
		failCount = 0
		failItem = ''
		os.system( 'echo \"#!/bin/sh\" >> %s'% E_DEFAULT_NETWORK_VOLUME_SHELL )
		for netVolume in volumeList :
			count += 1
			lblRet = MR_LANG( 'OK' )
			lblLabel = '[%s/%s]%s'% ( count, volumeCount, os.path.basename( netVolume.mMountPath ) )
			if netVolume.mIsDefaultSet :
				defVolume = netVolume
			self.SetControlLabel2String( E_DialogInput03, lblLabel )

			mntHistory = ExecuteShell( 'mount' )
			if not mntHistory or ( not bool( re.search( '%s'% netVolume.mMountPath, mntHistory, re.IGNORECASE ) ) ) :
				mntPath = MountToSMB( netVolume.mRemoteFullPath, netVolume.mMountPath, False )
				if not mntPath :
					mntHistory = ExecuteShell( 'mount' )
					if not mntHistory or ( not bool( re.search( '%s'% netVolume.mMountPath, mntHistory, re.IGNORECASE ) ) ) :
						lblRet = MR_LANG( 'Fail' )
						failCount += 1
						failItem += '\n%s'% os.path.basename( netVolume.mMountPath )

			lblLabel = '%s%s'% ( lblRet, lblLabel )
			self.SetControlLabel2String( E_DialogInput03, lblLabel )

			os.system( 'echo \"mkdir -p %s\" >> %s'% ( netVolume.mMountPath, E_DEFAULT_NETWORK_VOLUME_SHELL ) )
			os.system( 'echo \"%s\" >> %s'% ( netVolume.mMountCmd, E_DEFAULT_NETWORK_VOLUME_SHELL ) )
			os.system( 'sync' )
			time.sleep( 1 )

		os.system( 'chmod 755 %s'% E_DEFAULT_NETWORK_VOLUME_SHELL )
		os.system( 'sync' )
		xbmc.executebuiltin( 'Dialog.Close(busydialog)' )

		lblSelect, useInfo, lblPercent, lblOnline = self.GetVolumeInfo( defVolume )
		self.SetControlLabel2String( E_DialogInput03, lblSelect )
		self.setProperty( 'NetVolumeConnect', lblOnline )
		self.setProperty( 'NetVolumeUse', lblPercent )
		self.mCtrlProgressUse.setPercent( useInfo )
		ResetPositionVolumeInfo( self, lblPercent, self.mDialogWidth, E_GROUP_ID_SHOW_INFO, E_LABEL_ID_USE_INFO )

		if failCount :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), failItem[1:] )
			dialog.doModal( )

		#self.DrawItem( )


	def UpdateShell( self ) :
		RemoveDirectory( E_DEFAULT_NETWORK_VOLUME_SHELL )
		if not self.mNetVolumeList or len( self.mNetVolumeList ) < 1 :
			return

		os.system( 'echo \"#!/bin/sh\" >> %s'% E_DEFAULT_NETWORK_VOLUME_SHELL )
		for netVolume in self.mNetVolumeList :
			os.system( 'echo \"/bin/umount -fl %s\" >> %s'% ( netVolume.mMountPath, E_DEFAULT_NETWORK_VOLUME_SHELL ) )
		os.system( 'echo \"rm -rf %s; mkdir -p %s\" >> %s'% ( E_DEFAULT_PATH_SMB_POSITION, E_DEFAULT_PATH_SMB_POSITION, E_DEFAULT_NETWORK_VOLUME_SHELL ) )
		os.system( 'echo \"rm -rf %s; mkdir -p %s\" >> %s'% ( E_DEFAULT_PATH_NFS_POSITION, E_DEFAULT_PATH_NFS_POSITION, E_DEFAULT_NETWORK_VOLUME_SHELL ) )
		os.system( 'echo \"rm -rf %s; mkdir -p %s\" >> %s'% ( E_DEFAULT_PATH_FTP_POSITION, E_DEFAULT_PATH_FTP_POSITION, E_DEFAULT_NETWORK_VOLUME_SHELL ) )
		for netVolume in self.mNetVolumeList :
			os.system( 'echo \"mkdir -p %s\" >> %s'% ( netVolume.mMountPath, E_DEFAULT_NETWORK_VOLUME_SHELL ) )
			os.system( 'echo \"%s\" >> %s'% ( netVolume.mMountCmd, E_DEFAULT_NETWORK_VOLUME_SHELL ) )


		os.system( 'chmod 755 %s'% E_DEFAULT_NETWORK_VOLUME_SHELL )
		os.system( 'sync' )
		time.sleep( 1 )


