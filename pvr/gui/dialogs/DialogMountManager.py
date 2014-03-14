from pvr.gui.WindowImport import *
import urlparse

E_RECORDPATH_SETUPMENU_GROUP_ID	 = 9010
E_RECORDPATH_SUBMENU_LIST_ID     = 9000
E_RECORDPATH_SETTING_DESCRIPTION = 1003

E_LABEL_ID_DEFAULT_PATH   = 201
E_PROGRESS_ID_DEFAULT_USE = 202
E_LABEL_ID_DEFAULT_USE    = 203
E_PROGRESS_ID_USE         = 300
E_LABEL_ID_USE            = 301
E_IMAGE_ID_ONLINE         = 302

E_NETWORK_VOLUME_ADD = 0
E_NETWORK_VOLUME_EDIT = 1
E_NETWORK_VOLUME_DELETE = 2

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

		self.mCtrlLabelDefaultPath   = self.getControl( E_LABEL_ID_DEFAULT_PATH )
		self.mCtrlProgressDefaultUse = self.getControl( E_PROGRESS_ID_DEFAULT_USE )
		self.mCtrlLabelDefaultUse    = self.getControl( E_LABEL_ID_DEFAULT_USE )
		self.mCtrlProgressUse        = self.getControl( E_PROGRESS_ID_USE )
		self.mCtrlLabelUse           = self.getControl( E_LABEL_ID_USE )
		#self.setProperty( 'DialogDrawFinished', 'False' )
		lblTitle = MR_LANG( 'Record Path' )
		self.SetHeaderLabel( lblTitle )

		self.mDefaultPathVolume = None
		self.mFreeHDD  = 0
		self.mTotalHDD = 0
		if CheckHdd( ) :
			self.mTotalHDD = self.mCommander.Record_GetPartitionSize( )
			self.mFreeHDD  = self.mCommander.Record_GetFreeMBSize( )

		self.mMode = E_NETWORK_VOLUME_ADD
		self.mSelectIdx = -1
		self.mNetVolume = ElisENetworkVolume( )
		self.mNetVolume.mRemotePath = ''
		self.mNetVolume.mMountPath = ''
		self.mNetVolumeList = self.mDataCache.Record_GetNetworkVolume( )
		if self.mNetVolumeList and len( self.mNetVolumeList ) > 0 :
			self.mSelectIdx = 0
			#check default
			for netVolume in self.mNetVolumeList :
				if netVolume.mIsDefaultSet :
					self.mDefaultPathVolume = netVolume
					break

		self.DrawItem( )

		self.setProperty( 'DialogDrawFinished', 'True' )
		#self.mInitialized = True


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		self.mIsOk = actionId

		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
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

		if groupId == E_DialogInput04 : #reset
			self.mSelectIdx = -1
			self.SetMountByVolumeList( )
			self.DrawItem( )

		else :
			#if groupId == E_DialogSpinEx01 or groupId == E_DialogSpinEx02 : #isDefault
			#	self.ControlSelect( )

			self.SetNetworkVolume( groupId )


	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		pass


	def Close( self ) :
		self.ResetAllControl( )
		self.CloseDialog( )


	def SetNetworkVolume( self, aInput, aBrowseTitle = '' ) :

		# select path
		if aInput == E_DialogInput05 or aInput == E_DialogInput06 :
			browseTitle = MR_LANG( 'Select' )
			if aInput == E_DialogInput05 :
				browseTitle = '%s %s'% ( browseTitle, MR_LANG( 'Record Path' ) )
			elif aInput == E_DialogInput06 :
				browseTitle = '%s %s'% ( browseTitle, MR_LANG( 'Mount Path' ) )

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
					lblLine = '%s\n%s'% ( MR_LANG( 'Incorrect path' ), MR_LANG( 'select your local directory' ) )
				else :
					isFail = False

			else :
				if urlType :
					if urlType == 'smb' :
						isFail = False
						LOG_TRACE( '-----------------------smb getPath[%s]'% getPath )

					elif urlType == 'nfs' :
						pass

					else :
						# upnp, zeroconf, daap, ...
						lblLine = MR_LANG( 'No %s support' )% urlType
				else :
					lblLine = '%s\n%s'% ( MR_LANG( 'Incorrect path' ), MR_LANG( 'select your remote directory' ) )


			if isFail :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( lblTitle, lblLine )
				dialog.doModal( )
				return

			#init value
			if aInput == E_DialogInput05 :
				urlHost, urlPort, urlUser, urlPass, urlPath, urlFile, urlSize = GetParseUrl( getPath )
				lblPath = '%s%s'% ( urlHost, os.path.dirname( urlPath ) )
				self.mNetVolume.mRemotePath = '//' + lblPath
				self.mNetVolume.mRemoteFullPath = getPath
				self.SetControlLabel2String( E_DialogInput05, lblPath )
				LOG_TRACE( 'lblPath[%s] remote[%s] fullpath[%s]'% ( lblPath, self.mNetVolume.mRemotePath, self.mNetVolume.mRemoteFullPath ) )

			elif aInput == E_DialogInput06 :
				urlHost, urlPort, urlUser, urlPass, urlPath, urlFile, urlSize = GetParseUrl( getPath )
				lblPath = os.path.join( urlHost, urlPath )
				mntPath = os.path.dirname( urlPath )
				self.mNetVolume.mMountPath = mntPath
				self.SetControlLabel2String( E_DialogInput06, lblPath )
				LOG_TRACE( 'lblPath[%s] mount[%s]'% ( lblPath, mntPath ) )

		elif aInput == E_DialogSpinEx01 :
			if not self.mNetVolume.mRemotePath or ( not self.mNetVolume.mMountPath ) :
				self.SelectPosition( E_DialogSpinEx01, self.mNetVolume.mIsDefaultSet )
				lblLine = MR_LANG( 'Enter the input record path first' )
				if not self.mNetVolume.mMountPath :
					lblLine = MR_LANG( 'Enter the input mount path first' )

				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), lblLine )
				dialog.doModal( )
				return

			mIsDefaultSet_backup = self.mNetVolume.mIsDefaultSet
			self.mNetVolume.mIsDefaultSet = self.GetSelectedIndex( E_DialogSpinEx01 )
			if not self.DoCheckDefaultPath( self.mNetVolume ) :
				self.mNetVolume.mIsDefaultSet = mIsDefaultSet_backup
				self.SelectPosition( E_DialogSpinEx01, mIsDefaultSet_backup )
			LOG_TRACE( '======================mIsDefaultSet_backup[%s] mIsDefaultSet[%s] GetSelectedIndex[%s]'% ( mIsDefaultSet_backup, self.mNetVolume.mIsDefaultSet, self.GetSelectedIndex( E_DialogSpinEx01 ) ) )

		elif aInput == E_DialogSpinEx02 :
			self.mNetVolume.mSupport4G = self.GetSelectedIndex( E_DialogSpinEx02 )


	def DoCheckDefaultPath( self, aNetVolume = None, aAsk = True ) :
		if not aNetVolume :
			LOG_TRACE( '[MountManager] pass, volume is None' )
			return False

		isReset = False
		isChange = False

		if self.mDefaultPathVolume :
			if self.mDefaultPathVolume.mMountPath == aNetVolume.mMountPath :
				if self.mDefaultPathVolume.mIsDefaultSet != aNetVolume.mIsDefaultSet :
					#current : no -> yes, yes -> no
					isChange = True
					if self.mDefaultPathVolume.mIsDefaultSet and ( not aNetVolume.mIsDefaultSet ) :
						isReset = True

			else :
				#change : another -> this volume
				isChange = True

		else :
			#new default
			isChange = True
			if not aNetVolume.mIsDefaultSet :
				isReset = True
				if not aAsk :
					isChange = False

		if isChange :
			if aAsk :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				lblLine = MR_LANG( 'Are you sure default path this volume?' )
				if isReset :
					lblLine = '%s\n%s'% ( MR_LANG( 'Reset default path' ), MR_LANG( 'Are you sure default path internal HDD?' ) )
				dialog.SetDialogProperty( MR_LANG( 'Default path' ), lblLine )
				dialog.doModal( )
				isChange = False
				if dialog.IsOK( ) == E_DIALOG_STATE_YES :
					isChange = True

			#if isChange :
			#	isChange = self.mDataCache.Record_SetDefaultVolume( aNetVolume )

		return isChange


	def DoDeleteVolume( self, aNetVolume = None, aIsUMount = True ) :
		if not aNetVolume :
			LOG_TRACE( '[MountManager] Fail, netVolume is None' )
			return False

		ret = self.mDataCache.Record_DeleteNetworkVolume( aNetVolume )
		LOG_TRACE( '[MountManager] Record_DeleteNetworkVolume[%s]'% ret )
		if ret :
			if aIsUMount :
				os.system( '/bin/umount -f %s'% aNetVolume.mMountPath )
				os.system( 'sync' )

			listCount = len( self.mNetVolumeList )
			if not self.mNetVolumeList or ( listCount - 1 ) < 1 :
				self.mSelectIdx = -1
				#self.mNetVolume = ElisENetworkVolume( )
				#self.mNetVolume.mRemotePath = ''
				#self.mNetVolume.mMountPath = ''

			else :
				if self.mSelectIdx >= listCount - 1 :
					self.mSelectIdx = listCount - 2

				else :
					self.mSelectIdx -= 1

		return ret


	def DoNetworkVolume( self, aInput = None ) :

		if aInput :
			isFail = True
			lblLine = ''
			lblTitle= MR_LANG( 'Error' )
			if aInput == E_DialogInput07 :
				mountPath = ''
				lblLine = MR_LANG( 'Can not apply' )
				if self.mNetVolume.mRemotePath and self.mNetVolume.mMountPath :

					urlHost, urlPort, urlUser, urlPass, urlPath, urlFile, urlSize = GetParseUrl( self.mNetVolume.mRemoteFullPath )
					self.mNetVolume.mMountCmd = 'mount -t cifs -o username=%s,password=%s %s %s'% ( urlUser, urlPass, self.mNetVolume.mRemotePath, self.mNetVolume.mMountPath )
					mountPath = MountToSMB( self.mNetVolume.mRemoteFullPath, self.mNetVolume.mMountPath, False )
					LOG_TRACE( '----------------------------------mountPath[%s]'% mountPath )
					#self.mNetVolume.printdebug( )

					lblLine = MR_LANG( 'Can not mount this volume' )
					if mountPath != '' :
						isAdd = True
						#is edit? delete old volume
						if self.mNetVolumeList and len( self.mNetVolumeList ) > 0 :
							for netVolume in self.mNetVolumeList :
								netVolume.printdebug()
								if netVolume.mMountPath == self.mNetVolume.mMountPath :
									if not self.DoDeleteVolume( netVolume, False ) :
										isAdd = False
										lblLine = '%s\'%s\' on \'%s\''% ( MR_LANG( 'Arleady mounted' ), netVolume.mRemotePath, self.mNetVolume.mMountPath )

									LOG_TRACE( '[MountManager] detected same path mnt[%s] new[%s]'% ( netVolume.mMountPath, self.mNetVolume.mMountPath ) )
									#netVolume.printdebug( )
									break

						if isAdd :
							lblLine = MR_LANG( 'Can not add this volume' )
							ret = self.mDataCache.Record_AddNetworkVolume( self.mNetVolume )
							LOG_TRACE( '----------------------------------ret[%s]'% ret )
							if ret :
								isFail = False
								lblLine = '%s\n%s%s to %s'% ( MR_LANG( 'Add volume' ), urlHost, os.path.dirname(urlPath), mountPath )
								if self.DoCheckDefaultPath( self.mNetVolume, False ) :
									ret = self.mDataCache.Record_SetDefaultVolume( self.mNetVolume )

							else :
								# Add fail then restore umount
								os.system( '/bin/umount -f %s'% mountPath )
								os.system( 'sync' )

			elif aInput == E_DialogInput02 :
				delTitle= MR_LANG( 'Delete' )
				delLine = MR_LANG( 'Are you delete this volume?' )
				delLine = '%s\n%s'% ( self.mNetVolume.mMountPath, delLine )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( delTitle, delLine )
				dialog.doModal( )
				if dialog.IsOK( ) != E_DIALOG_STATE_YES :
					LOG_TRACE( '[MountManager] Cancel delete' )
					return

				ret = self.DoDeleteVolume( self.mNetVolume )
				if ret :
					isFail = False
					urlHost, urlPort, urlUser, urlPass, urlPath, urlFile, urlSize = GetParseUrl( self.mNetVolume.mRemoteFullPath )
					lblLine = '%s\n%s%s'% ( MR_LANG( 'Delete volume' ), urlHost, os.path.dirname( urlPath ) )


			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			if isFail :
				lblLine = '%s\n%s'% ( MR_LANG( 'Fail' ), lblLine )
				dialog.SetDialogProperty( lblTitle, lblLine )
				dialog.doModal( )
				return

			lblTitle= MR_LANG( 'Success' )
			dialog.SetDialogProperty( lblTitle, lblLine )
			dialog.doModal( )


		selectIdx = -1
		self.mDefaultPathVolume = None
		defaultPath = E_DEFAULT_PATH_INTERNAL_HDD
		self.mNetVolumeList = self.mDataCache.Record_GetNetworkVolume( )
		if self.mNetVolumeList and len( self.mNetVolumeList ) > 0 :
			for netVolume in self.mNetVolumeList :
				selectIdx += 1
				if netVolume.mMountPath == self.mNetVolume.mMountPath :
					self.mSelectIdx = selectIdx

				if netVolume.mIsDefaultSet :
					self.mDefaultPathVolume = netVolume

			#if selectIdx > -1 :
			#	self.mNetVolume = self.mNetVolumeList[self.mSelectIdx]
			#	self.mNetVolume.printdebug()

		ElisPropertyEnum( 'Record Default Path Change', self.mCommander ).SetProp( defaultPath )

		self.DrawItem( )
		LOG_TRACE( '[MountManager] Done' )


	def DrawItem( self ) :
		xbmc.executebuiltin( 'ActivateWindow(busydialog)' )
		self.ResetAllControl( )
		time.sleep( 0.2 )
		defaultFocus = E_DialogInput05

		lblSelect = MR_LANG( 'None' )
		lblRemote = lblSelect
		lblMount  = lblSelect
		isDefault = 0
		is4Gb     = 0
		usePercent= 0
		lblOnline = E_TAG_FALSE
		self.mNetVolume = ElisENetworkVolume( )
		self.mNetVolume.mRemotePath = ''
		self.mNetVolume.mMountPath = ''

		if self.mNetVolumeList and self.mSelectIdx > -1 and self.mSelectIdx < len( self.mNetVolumeList ) :
			#self.mSelectIdx = 0
			defaultFocus = E_DialogInput03
			self.mNetVolume = deepcopy( self.mNetVolumeList[self.mSelectIdx] )
			getPath   = self.mNetVolume.mRemoteFullPath
			urlHost, urlPort, urlUser, urlPass, urlPath, urlFile, urlSize = GetParseUrl( getPath )
			urlType   = urlparse.urlparse( getPath ).scheme
			lblMount  = self.mNetVolume.mMountPath
			lblSelect = '[%s] %s'% ( urlType, lblMount )
			lblRemote = '%s%s'% ( urlHost, os.path.dirname( urlPath ) )
			isDefault = self.mNetVolume.mIsDefaultSet
			is4Gb     = self.mNetVolume.mSupport4G
			if self.mNetVolume.mOnline :
				lblOnline = E_TAG_TRUE
			if self.mNetVolume.mTotalMB > 0 :
				usePercent = int( ( ( 1.0 * ( self.mNetVolume.mTotalMB - self.mNetVolume.mFreeMB ) ) / self.mNetVolume.mTotalMB ) * 100 )

		#self.AddInputControl( E_DialogInput01, MR_LANG( 'Add' ), '' )
		self.AddInputControl( E_DialogInput03, MR_LANG( 'Select' ), lblSelect )
		self.AddInputControl( E_DialogInput02, '', MR_LANG( 'Delete' ) )

		self.AddInputControl( E_DialogInput04, 'Reset', '' )
		self.AddInputControl( E_DialogInput05, 'Record Path', lblRemote )
		self.AddInputControl( E_DialogInput06, 'Access Location', lblMount )
		self.AddUserEnumControl( E_DialogSpinEx01, 'Use default path', USER_ENUM_LIST_YES_NO, isDefault )
		self.AddUserEnumControl( E_DialogSpinEx02, 'Use record per 4GB', USER_ENUM_LIST_YES_NO, is4Gb )
		self.AddInputControl( E_DialogInput07, 'Apply', '' )

		visibleControlIds = [E_DialogInput02, E_DialogInput03, E_DialogInput04, E_DialogInput05, E_DialogInput06, E_DialogSpinEx01, E_DialogSpinEx02, E_DialogInput07 ]

		self.SetVisibleControls( visibleControlIds, True )
		self.SetEnableControls( visibleControlIds, True )
		if self.mSelectIdx < 0 :
			self.SetEnableControl( E_DialogInput02, False )
			#ToDO : usb? then enable false

		self.InitControl( )
		time.sleep( 0.2 )
		#if not self.mInitialized :
		#	self.mInitialize = True
		self.SetAutoHeight( False )
		self.UpdateLocation( )
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

		default_byte = '%sMb'% self.mFreeHDD
		if self.mFreeHDD > 1024 :
			default_byte = '%sGb'% ( self.mFreeHDD / 1024 )
		elif self.mFreeHDD < 0 :
			default_byte = '%sKb'% ( self.mFreeHDD * 1024 )

		default_lblPercent = '%s%%, %s Free'% ( default_usePercent, default_byte )

		#select size
		lblbyte = '%sMb'% self.mNetVolume.mFreeMB
		if self.mNetVolume.mFreeMB > 1024 :
			lblbyte = '%sGb'% ( self.mNetVolume.mFreeMB / 1024 )
		elif self.mNetVolume.mFreeMB < 0 :
			lblbyte = '%sKb'% ( self.mNetVolume.mFreeMB * 1024 )

		if self.mDefaultPathVolume :
			default_Path = self.mDefaultPathVolume.mMountPath
			if self.mDefaultPathVolume.mTotalMB > 0 :
				default_usePercent = int( ( ( 1.0 * ( self.mDefaultPathVolume.mTotalMB - self.mDefaultPathVolume.mFreeMB ) ) / self.mDefaultPathVolume.mTotalMB ) * 100 )
			default_lblPercent = '%s%%, %s Free'% ( default_usePercent, lblbyte )

			default_lblOnline = E_TAG_FALSE
			if self.mDefaultPathVolume.mOnline :
				default_lblOnline = E_TAG_TRUE

		#lblDefault = '%s : %s'% ( MR_LANG( 'Default path' ), mntDefault )
		lblPercent = '%s%%, %s %s'% ( usePercent, lblbyte, MR_LANG( 'Free' ) )

		#default info
		self.mCtrlLabelDefaultPath.setLabel( default_Path )
		self.mCtrlLabelDefaultUse.setLabel( default_lblPercent )
		self.mCtrlProgressDefaultUse.setPercent( default_usePercent )
		#select info
		self.mCtrlProgressUse.setPercent( usePercent )
		self.mCtrlLabelUse.setLabel( lblPercent )
		self.setProperty( 'SelectVolumeConnect', lblOnline )
		self.setProperty( 'DefaultVolumeConnect', default_lblOnline )

		xbmc.executebuiltin( 'Dialog.Close(busydialog)' )
		LOG_TRACE( '----------------------------------DrawItem property[%s]'% ElisPropertyEnum( 'Record Default Path Change', self.mCommander ).GetPropString( ) )


	def GetMountList( self ) :
		#self.mNetVolumeList = self.mDataCache.Record_GetNetworkVolume( )

		trackList = []
		trackIndex = 0
		if self.mNetVolumeList and len( self.mNetVolumeList ) > 0 :
			for netVolume in self.mNetVolumeList :
				getPath = netVolume.mRemoteFullPath
				urlType = urlparse.urlparse( getPath ).scheme
				urlHost, urlPort, urlUser, urlPass, urlPath, urlFile, urlSize = GetParseUrl( getPath )
				lblType = 'local'
				if urlType :
					lblType = '%s'% urlType.upper()

				#lblPath = '[%s]%s%s'% ( lblType, urlHost, os.path.dirname( urlPath ) )
				lblPath = '[%s]%s'% ( lblType, netVolume.mMountPath )
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
		dialog.SetProperty( trackList, self.mSelectIdx )
		dialog.doModal( )

		selectAction = dialog.GetSelectedAction( )
		if selectAction < 0 :
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

		RemoveDirectory( '/config/smbReserved.info' )
		volumeCount = len( volumeList )
		count = 0
		os.system( 'echo \"#!/bin/sh\" >> /config/smbReserved.info' )
		for netVolume in volumeList :
			count += 1
			cmd = netVolume.mMountCmd
			lblLabel = '[%s/%s]%s'% ( count, volumeCount, netVolume.mMountPath )
			self.mCtrlLabelDefaultPath.setLabel( lblLabel )
			self.SetControlLabel2String( E_DialogInput04, lblLabel )
			os.system( 'umount -f %s '% netVolume.mMountPath )
			time.sleep( 1 )
			os.system( '%s'% cmd )
			os.system( 'echo \"%s\" >> /config/smbReserved.info'% cmd )
			os.system( 'sync' )

		os.system( 'chmod 755 /config/smbReserved.info' )
		os.system( 'sync' )
		xbmc.executebuiltin( 'Dialog.Close(busydialog)' )
		self.DrawItem( )

