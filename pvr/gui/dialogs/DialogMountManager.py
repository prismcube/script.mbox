from pvr.gui.WindowImport import *
import urlparse

E_RECORDPATH_SETUPMENU_GROUP_ID	= 9010
E_RECORDPATH_SUBMENU_LIST_ID    = 9000
E_RECORDPATH_SETTING_DESCRIPTION = 1003

E_ID_NO  = 0
E_ID_YES = 1


class DialogMountManager( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		self.mIsOk					= False


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.setProperty( 'DialogDrawFinished', 'False' )
		lblTitle = MR_LANG( 'RECORD PATH' )
		self.SetHeaderLabel( lblTitle )
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
		if groupId == E_DialogInput01 : #add
			pass

		elif groupId == E_DialogInput02 : #select
			pass

		elif groupId == E_DialogInput03 : #delete
			pass

		elif groupId == E_DialogSpinEx01 :
			self.ControlSelect( )
			enableControlIds = [ E_DialogSpinEx02, E_DialogInput03, E_DialogInput04 ]
			enable = False
			if self.GetSelectedIndex( E_DialogSpinEx01 ) == E_ID_YES :
				enable = True
			self.SetEnableControls( enableControlIds, enable )

		else :
			self.ControlSelect( )


	def onFocus( self, aControlId ) :
		pass


	def onEvent( self, aEvent ) :
		pass


	def Close( self ) :
		self.ResetAllControl( )
		self.CloseDialog( )


	def DrawItem( self ) :
		self.ResetAllControl( )
		#defaultFocus = E_DialogInput01
		#if self.mInitialized :
		#	defaultFocus = E_DialogSpinEx01

		trackList = self.GetMountList( )
		lblSelect = MR_LANG( 'None' )
		lblType =
		lblRemote = 
		lblMount =

		self.mSelectIdx = -1
		if trackList and len( trackList ) > 0 :
			self.mSelectIdx = 0
			netVolume = trackList[self.mSelectIdx].mDescription
			lblSelect = netVolume.mDescription
			lblType = MR_LANG( 'local' )
			urlType = urlparse.urlparse( netVolume.mRemotePath ).scheme
			if urlType :
				lblType = urlType.upper( )


		self.AddInputControl( E_DialogInput01, MR_LANG( 'Add' ), '' )
		self.AddInputControl( E_DialogInput02, MR_LANG( 'Select' ), lblSelect )
		self.AddInputControl( E_DialogInput03, '', MR_LANG( 'Delete' ) )

		visibleControlIds = [E_DialogInput01, E_DialogInput02 ]
		hideControlIds = [E_DialogInput04, E_DialogInput05, E_DialogInput06, E_DialogSpinEx01, E_DialogInput07 ]
		disableControlIds = [E_DialogInput03]

		lblDefault = USER_ENUM_LIST_YES_NO[0]
		self.AddInputControl( E_DialogInput04, 'Record Path', lblSelect )
		self.AddInputControl( E_DialogInput05, '', lblSelect )

		self.AddInputControl( E_DialogInput06, 'Access Location', lblSelect )
		self.AddInputControl( E_DialogSpinEx01, 'Use default path', USER_ENUM_LIST_YES_NO[0] )
		self.AddInputControl( E_DialogInput07, 'Apply', '' )

		if selectIdx > -1 :
			visibleControlIds = [E_DialogInput01, E_DialogInput02, E_DialogInput03, E_DialogInput04, E_DialogInput05, E_DialogInput06, E_DialogSpinEx01, E_DialogInput07 ]
			disableControlIds = [E_DialogInput03, E_DialogInput05]
			hideControlIds = []

		self.SetVisibleControls( visibleControlIds, True )
		self.SetEnableControls( visibleControlIds, True )
		self.SetEnableControls( disableControlIds, False )

		if hideControlIds :
			self.SetVisibleControls( hideControlIds, False )


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


