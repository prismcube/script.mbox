from pvr.gui.WindowImport import *
import urlparse

E_RECORDPATH_SETUPMENU_GROUP_ID	 = 9010
E_RECORDPATH_SUBMENU_LIST_ID     = 9000
E_RECORDPATH_SETTING_DESCRIPTION = 1003

E_LABEL_ID_DEFAULT_PATH = 201
E_PROGRESS_ID_USE       = 300
E_LABEL_ID_USE          = 301
E_LABEL_ID_ONLINE       = 302

E_NETWORK_VOLUME_ADD = 0
E_NETWORK_VOLUME_EDIT = 1
E_NETWORK_VOLUME_DELETE = 2

E_ID_NO  = 0
E_ID_YES = 1


class DialogMountManager( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		self.mIsOk					= False


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.mCtrlLabelDefaultPath = self.getControl( E_LABEL_ID_DEFAULT_PATH )
		self.mCtrlProgressUse      = self.getControl( E_PROGRESS_ID_USE )
		self.mCtrlLabelUse         = self.getControl( E_LABEL_ID_USE )
		self.mCtrlLabelOnline      = self.getControl( E_LABEL_ID_ONLINE )
		#self.setProperty( 'DialogDrawFinished', 'False' )
		lblTitle = MR_LANG( 'RECORD PATH' )
		self.SetHeaderLabel( lblTitle )

		self.mMode = E_NETWORK_VOLUME_ADD
		self.mSelectIdx = -1
		self.mNetVolume = ElisENetworkVolume( )
		self.mNetVolume.mRemotePath = ''
		self.mNetVolume.mMountPath = ''
		self.mNetVolumeList = self.mDataCache.Record_GetNetworkVolume( )
		if self.mNetVolumeList and len( self.mNetVolumeList ) > 0 :
			self.mSelectIdx = 0

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


	def onClick( self, aControlId ) :
		if aControlId == E_SETTING_DIALOG_BUTTON_CLOSE :
			self.Close( )

		groupId = self.GetGroupId( aControlId )
		if groupId == E_DialogInput07 or groupId == E_DialogInput02 : #apply, delete
			self.DoNetworkVolume( groupId )

		if groupId == E_DialogInput03 : #select
			if self.ShowMountList( ) :
				self.DrawItem( )

		if groupId == E_DialogInput04 : #reset
			self.mSelectIdx = -1
			self.DrawItem( )

		else :
			if groupId == E_DialogSpinEx01 or groupId == E_DialogSpinEx02 : #isDefault
				self.ControlSelect( )

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
				ret = self.SetControlLabel2String( E_DialogInput05, lblPath )
				LOG_TRACE( 'ret[%s] lblPath[%s] remote[%s] fullpath[%s]'% ( ret, lblPath, self.mNetVolume.mRemotePath, self.mNetVolume.mRemoteFullPath ) )

			elif aInput == E_DialogInput06 :
				urlHost, urlPort, urlUser, urlPass, urlPath, urlFile, urlSize = GetParseUrl( getPath )
				lblPath = os.path.join( urlHost, urlPath )
				mntPath = os.path.dirname( urlPath )
				self.mNetVolume.mMountPath = mntPath
				self.SetControlLabel2String( E_DialogInput06, lblPath )
				LOG_TRACE( 'lblPath[%s] mount[%s]'% ( lblPath, mntPath ) )

		elif aInput == E_DialogSpinEx01 :
			self.ControlSelect( )
			self.mNetVolume.mIsDefaultSet = self.GetSelectedIndex( E_DialogSpinEx01 )

		elif aInput == E_DialogSpinEx02 :
			self.ControlSelect( )
			self.mNetVolume.mSupport4G = self.GetSelectedIndex( E_DialogSpinEx02 )


	def DoDeleteVolume( self, aNetVolume = None ) :
		if not aNetVolume :
			LOG_TRACE( '[MountManager] Fail, netVolume is None' )
			return False

		ret = self.mDataCache.Record_DeleteNetworkVolume( aNetVolume )
		LOG_TRACE( '[MountManager] Record_DeleteNetworkVolume[%s]'% ret )
		if ret :
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
					isAdd = True
					#is edit? delete old volume
					if self.mNetVolumeList and len( self.mNetVolumeList ) > 0 :
						for netVolume in self.mNetVolumeList :
							if netVolume.mMountPath == self.mNetVolume.mMountPath :
								if not self.DoDeleteVolume( netVolume ) :
									isAdd = False
									lblLine = '%s\'%s\''% ( MR_LANG( 'Arleady mounted' ), netVolume.mRemotePath )

								LOG_TRACE( '[MountManager] detected same path' )
								netVolume.printdebug( )
								break

					if isAdd :
						urlHost, urlPort, urlUser, urlPass, urlPath, urlFile, urlSize = GetParseUrl( self.mNetVolume.mRemoteFullPath )
						self.mNetVolume.mMountCmd = 'mount -t cifs -o username=%s,password=%s %s %s'% ( urlUser, urlPass, self.mNetVolume.mRemotePath, self.mNetVolume.mMountPath )
						mountPath = MountToSMB( self.mNetVolume.mRemoteFullPath, self.mNetVolume.mMountPath, False )
						LOG_TRACE( '----------------------------------mountPath[%s]'% mountPath )
						self.mNetVolume.printdebug( )

						lblLine = MR_LANG( 'Can not mount this volume' )
						if mountPath != '' :
							lblLine = MR_LANG( 'Can not add this volume' )
							ret = self.mDataCache.Record_AddNetworkVolume( self.mNetVolume )
							if ret :
								isFail = False
								lblLine = '%s\n%s%s to %s'% ( MR_LANG( 'Add volume' ), urlHost, os.path.dirname(urlPath), mountPath )

							LOG_TRACE( '----------------------------------ret[%s]'% ret )


			elif aInput == E_DialogInput02 :
				delLine = MR_LANG( 'Are you delete this volume?' )
				delLine = '%s\n%s'% ( self.mNetVolume.mMountPath, delLine )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( lblTitle, lblLine )
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
		netList = self.mDataCache.Record_GetNetworkVolume( )
		if netList and len( netList ) > 0 :
			self.mNetVolumeList = netList
			for netVolume in netList :
				selectIdx += 1
				if self.mNetVolume.mMountPath == netVolume.mMountPath :
					self.mSelectIdx = selectIdx
					break
			if selectIdx > -1 :
				self.mNetVolume = netList[self.mSelectIdx]
				self.mNetVolume.printdebug()

		self.DrawItem( )
		LOG_TRACE( '[MountManager] Done' )


	def DrawItem( self ) :
		xbmc.executebuiltin( "ActivateWindow(busydialog)" )
		self.ResetAllControl( )
		time.sleep( 0.2 )
		#defaultFocus = E_DialogInput01
		#if self.mInitialized :
		#	defaultFocus = E_DialogSpinEx01

		lblSelect = MR_LANG( 'None' )
		lblPath   = lblSelect
		lblMount  = lblSelect
		isDefault = 0
		is4Gb     = 0
		usePercent= 0
		lblOnline = MR_LANG( 'Off-line' )
		self.mNetVolume = ElisENetworkVolume( )
		self.mNetVolume.mRemotePath = ''
		self.mNetVolume.mMountPath = ''

		if self.mNetVolumeList and self.mSelectIdx > -1 and self.mSelectIdx < len( self.mNetVolumeList ) :
			#self.mSelectIdx = 0
			self.mNetVolume = self.mNetVolumeList[self.mSelectIdx]
			urlHost, urlPort, urlUser, urlPass, urlPath, urlFile, urlSize = GetParseUrl( self.mNetVolume.mRemoteFullPath )
			lblSelect = '%s%s'% ( urlHost, os.path.dirname( urlPath ) )
			lblMount  = self.mNetVolume.mMountPath
			isDefault = self.mNetVolume.mIsDefaultSet
			is4Gb     = self.mNetVolume.mSupport4G
			if self.mNetVolume.mOnline :
				lblOnline = '%s%s%s'% ( E_TAG_COLOR_GREEN, MR_LANG( 'On-line' ), E_TAG_COLOR_END )
			if self.mNetVolume.mTotalMB > 0 :
				usePercent = ( self.mNetVolume.mFreeMB / self.mNetVolume.mTotalMB ) * 100

		#self.AddInputControl( E_DialogInput01, MR_LANG( 'Add' ), '' )
		self.AddInputControl( E_DialogInput03, MR_LANG( 'Select' ), lblSelect )
		self.AddInputControl( E_DialogInput02, '', MR_LANG( 'Delete' ) )

		self.AddInputControl( E_DialogInput04, 'Reset', '' )
		self.AddInputControl( E_DialogInput05, 'Record Path', lblSelect )
		self.AddInputControl( E_DialogInput06, 'Access Location', lblMount )
		self.AddUserEnumControl( E_DialogSpinEx01, 'Use default path', USER_ENUM_LIST_YES_NO, 0 )
		self.AddUserEnumControl( E_DialogSpinEx02, 'Use record per 4GB', USER_ENUM_LIST_YES_NO, is4Gb )
		self.AddInputControl( E_DialogInput07, 'Apply', '' )

		visibleControlIds = [E_DialogInput02, E_DialogInput03, E_DialogInput04, E_DialogInput05, E_DialogInput06, E_DialogSpinEx01, E_DialogSpinEx02, E_DialogInput07 ]
		if self.mSelectIdx < 0 :
			visibleControlIds = [E_DialogInput02, E_DialogInput03, E_DialogInput04, E_DialogInput05, E_DialogInput06, E_DialogSpinEx01, E_DialogSpinEx02, E_DialogInput07 ]
			self.SetEnableControl( E_DialogInput03, False )

		self.SetVisibleControls( visibleControlIds, True )
		self.SetEnableControls( visibleControlIds, True )

		self.InitControl( )
		time.sleep( 0.2 )
		#if not self.mInitialized :
		#	self.mInitialize = True
		self.SetAutoHeight( True )
		self.UpdateLocation( )
		#self.SetFocus( defaultFocus )

		lblDefault = '%s : %s'% ( MR_LANG( 'Default path' ), USER_ENUM_LIST_YES_NO[isDefault] )
		lblPercent = '%s%%, %sMb %s'% ( usePercent, self.mNetVolume.mFreeMB, MR_LANG( 'Free' ) )

		self.mCtrlLabelDefaultPath.setLabel( lblDefault )
		self.mCtrlProgressUse.setPercent( usePercent )
		self.mCtrlLabelUse.setLabel( lblPercent )
		self.mCtrlLabelOnline.setLabel( lblOnline )

		xbmc.executebuiltin( "Dialog.Close(busydialog)" )
		LOG_TRACE( '----------------------------------DrawItem' )


	def GetMountList( self ) :
		self.mNetVolumeList = self.mDataCache.Record_GetNetworkVolume( )

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

				lblPath = '[%s]%s%s'% ( lblType, urlHost, os.path.dirname( urlPath ) )
				#LOG_TRACE('mountPath urlType[%s] mRemotePath[%s] mMountPath[%s] isDefault[%s]'% ( urlType, netVolume.mRemotePath, netVolume.mMountPath, netVolume.mIsDefaultSet ) )

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

