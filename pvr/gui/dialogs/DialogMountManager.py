from pvr.gui.WindowImport import *
import urlparse

E_RECORDPATH_SETUPMENU_GROUP_ID	= 9010
E_RECORDPATH_SUBMENU_LIST_ID    = 9000
E_RECORDPATH_SETTING_DESCRIPTION = 1003

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

		#self.setProperty( 'DialogDrawFinished', 'False' )
		lblTitle = MR_LANG( 'RECORD PATH' )
		self.SetHeaderLabel( lblTitle )

		self.mMode = E_NETWORK_VOLUME_ADD
		self.mSelectIdx = -1
		self.mNetVolume = ElisENetworkVolume( )
		self.mNetVolume.mRemotePath = ''
		self.mNetVolume.mMountPath = ''
		self.mNetVolumeList = self.mDataCache.Record_GetNetworkVolume( )

		self.DrawItem( )

		self.setProperty( 'DialogDrawFinished', 'True' )
		self.mInitialized = True


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
		if groupId >= E_DialogInput01 and groupId <= E_DialogInput06 : #add
			self.SetNetworkVolume( groupId )

			# E_DialogInput02 : #select
			# E_DialogInput03 : #delete
			# E_DialogInput04 : #remote
			# E_DialogInput05 : #
			# E_DialogInput06 : #access

		elif groupId == E_DialogInput06 : #apply
			self.DoNetworkVolume( groupId )

		elif groupId == E_DialogSpinEx01 : #isDefault
			self.ControlSelect( )
			#enableControlIds = [ E_DialogSpinEx02, E_DialogInput03, E_DialogInput04 ]
			#enable = False
			#if self.GetSelectedIndex( E_DialogSpinEx01 ) == E_ID_YES :
			#	enable = True
			#self.SetEnableControls( enableControlIds, enable )

		else :
			self.ControlSelect( )


	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		pass


	def Close( self ) :
		self.ResetAllControl( )
		self.CloseDialog( )


	def SetNetworkVolume( self, aInput ) :

		# select path
		if aInput == E_DialogInput01 or aInput == E_DialogInput04 or aInput == E_DialogInput05 :

			zipFile = xbmcgui.Dialog( ).browsepath( MR_LANG( 'ADD RECORD PATH' ), '*.zip' )
			LOG_TRACE( '----------zip[%s]'% zipFile )
			if not zipFile or zipFile == 'None' :
				LOG_TRACE( 'not selected zip' )
				return

			isFail = True
			lblLine = ''
			lblTitle= MR_LANG( 'Error' )
			urlType = urlparse.urlparse( zipFile ).scheme
			LOG_TRACE( '------------------------urlType[%s]'% urlType )
			if aInput == E_DialogInput05 :
				if urlType :
					lblLine = '%s\n%s'% ( MR_LANG( 'Incorrect path' ), MR_LANG( 'select your local directory' ) )
				else :
					isFail = False

			else :
				if urlType :
					if urlType == 'smb' :
						isFail = False
						#zipFile = MountToSMB( zipFile, E_DEFAULT_PATH_SAMBA )
						LOG_TRACE( '-----------------------smb zipFile[%s]'% zipFile )

					elif urlType == 'nfs' :
						pass

					else :
						# upnp, zeroconf, daap, ...
						lblLine = MR_LANG( 'No %s support' )% urlType


			if isFail :
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( lblTitle, lblLine )
				dialog.doModal( )
				return

		#init value
		if aInput == E_DialogInput01 or aInput == E_DialogInput04 :
			self.mNetVolume.mRemotePath = zipFile
			self.SetControlLabel2String( E_DialogInput04, zipFile )
			#self.SetControlLabel2String( E_DialogInput05, urlType )

		elif aInput == E_DialogInput05 :
			self.mNetVolume.mMountPath = zipFile
			self.SetControlLabel2String( E_DialogInput05, zipFile )

		elif aInput == E_DialogSpinEx01 :
			self.ControlSelect( )
			self.mNetVolume.mIsDefaultSet = self.GetSelectedIndex( E_DialogSpinEx01 )

		elif aInput == E_DialogSpinEx02 :
			self.ControlSelect( )
			self.mNetVolume.mSupport4G = self.GetSelectedIndex( E_DialogSpinEx02 )


	def DoNetworkVolume( self, aInput = None ) :

		if aInput == E_DialogInput06 :
			isFail = True
			lblLine = ''
			mountPath = ''
			if self.mNetVolume.mRemotePath and self.mNetVolume.mMountPath :
				mountPath = MountToSMB( self.mNetVolume.mRemotePath, self.mNetVolume.mMountPath )

			if not CheckDirectory( mountPath ) :
				LOG_TRACE( 'not found mountPath[%s]'% mountPath )
				lblLine = MR_LANG( 'Fail to Mount' )

			else :
				isFail = self.mDataCache.Record_AddNetworkVolume( self.mNetVolume )

			if isFail :
				lblLine = '%s\n%s'% ( MR_LANG( 'Fail' ), lblLine )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				dialog.SetDialogProperty( MR_LANG( 'Error' ), lblLine )
				dialog.doModal( )
				return

		selectIdx = -1
		netList = self.mDataCache.Record_GetNetworkVolume( )
		if netList and len( netList ) > 0 :
			self.mNetVolumeList = netList
			for netVolume in netList :
				selectIdx += 1
				if self.mNetVolume.mRemotePath == netVolume.mRemotePath :
					self.mSelectIdx = selectIdx
					break

		self.DrawItem( selectIdx )


	def DrawItem( self ) :
		self.ResetAllControl( )
		#defaultFocus = E_DialogInput01
		#if self.mInitialized :
		#	defaultFocus = E_DialogSpinEx01

		lblSelect = MR_LANG( 'None' )
		lblPath = lblSelect
		lblMount = lblSelect
		useDefault = 0
		use4Gb = 0

		if self.mNetVolumeList and len( self.mNetVolumeList ) > 0 :
			self.mSelectIdx = 0
			netVolume = self.mNetVolumeList[self.mSelectIdx]
			lblSelect = netVolume.mRemotePath
			lblPath = netVolume.mMountPath
			isDefault = netVolume.mIsDefaultSet
			use4Gb = netVolume.mSupport4G


		self.AddInputControl( E_DialogInput01, MR_LANG( 'Add' ), '' )
		self.AddInputControl( E_DialogInput02, MR_LANG( 'Select' ), lblSelect )
		self.AddInputControl( E_DialogInput03, '', MR_LANG( 'Delete' ) )

		visibleControlIds = [E_DialogInput01, E_DialogInput02 ]
		#hideControlIds = [E_DialogInput04, E_DialogInput05, E_DialogInput06, E_DialogSpinEx01, E_DialogInput06 ]
		disableControlIds = [E_DialogInput03]

		lblDefault = USER_ENUM_LIST_YES_NO[0]
		self.AddInputControl( E_DialogInput04, 'Record Path', lblSelect )

		self.AddInputControl( E_DialogInput05, 'Access Location', lblPath )
		self.AddUserEnumControl( E_DialogSpinEx01, 'Use default path', USER_ENUM_LIST_YES_NO, useDefault )
		self.AddUserEnumControl( E_DialogSpinEx02, 'Use record per 4GB', USER_ENUM_LIST_YES_NO, use4Gb )
		self.AddInputControl( E_DialogInput06, 'Apply', '' )

		#if self.mSelectIdx > -1 :
		visibleControlIds = [E_DialogInput01, E_DialogInput02, E_DialogInput03, E_DialogInput04, E_DialogInput05, E_DialogInput06, E_DialogSpinEx01, E_DialogSpinEx02 ]
		#	hideControlIds = []

		self.SetVisibleControls( visibleControlIds, True )
		self.SetEnableControls( visibleControlIds, True )
		self.SetEnableControls( disableControlIds, False )

		#if hideControlIds :
		#	self.SetVisibleControls( hideControlIds, False )


		self.SetAutoHeight( True )
		self.InitControl( )
		self.UpdateLocation( )
		#self.SetFocus( defaultFocus )


	def GetMountList( self ) :
		netVolumeList = self.mDataCache.Record_GetNetworkVolume( )

		trackList = []
		trackIndex = 0
		if netVolumeList and len( netVolumeList ) > 0 :
			for netVolume in netVolumeList :
				urlType = urlparse.urlparse( netVolume.mRemotePath ).scheme
				LOG_TRACE('mountPath urlType[%s] mRemotePath[%s] mMountPath[%s] isDefault[%s]'% ( urlType, netVolume.mRemotePath, netVolume.mMountPath, netVolume.mIsDefaultSet ) )
				label = '[%s]%s'% ( urlType.upper(), netVolume.mRemotePath )
				if not urlType :
					label = '[local]%s'% netVolume.mRemotePath

				trackList.append( ContextItem( label, trackIndex ) )
				trackIndex += 1

		else :
			LOG_TRACE( 'Record_GetNetworkVolume none' )

		return trackList


	def ShowMountList( self ) :
		trackList = self.GetMountList( )

		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( trackList, self.mSelectIdx )
		dialog.doModal( )

		selectAction = dialog.GetSelectedAction( )
		if selectAction < 0 :
			return

		LOG_TRACE('Select[%s --> %s]'% ( self.mSelectIdx, selectAction) )

		if selectAction < len( trackList ) :
			self.mSelectIdx = selectAction
			self.SetControlLabel2String( E_DialogInput02, trackList[selectAction].mDescription )


