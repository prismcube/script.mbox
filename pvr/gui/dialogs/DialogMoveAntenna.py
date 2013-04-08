from pvr.gui.WindowImport import *
import pvr.TunerConfigMgr as ConfigMgr

E_MOVE_WEST					= 0
E_STEP_WEST					= 1
E_STOP						= 2
E_STEP_EAST					= 3
E_MOVE_EAST					= 4
E_LIMIT_RESET				= 5
E_WEST_LIMIT				= 6
E_EAST_LIMIT				= 7
E_SAVE_POSITION				= 8
#E_CLOSE						= 9


DIALOG_MAIN_GROUP_ID		= 9000
DIALOG_WIDTH				= 370

DIALOG_MIDDLE_IMAGE_ID		= 100
DIALOG_BOTTOM_IMAGE_ID		= 101

DIALOG_LIST_ID				= 102
DIALOG_BUTTON_CLOSE_ID		= 103


class DialogMoveAntenna( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mTunerIndex = E_TUNER_1


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.setProperty( 'DialogDrawFinished', 'False' )

		self.mTunerIndex = ConfigMgr.GetInstance( ).GetCurrentTunerNumber( )

		context = [ MR_LANG( 'Rotate to West' ), MR_LANG( 'One step to West' ), MR_LANG( 'Stop' ), MR_LANG( 'One step to East' ), MR_LANG( 'Rotate to East' ), MR_LANG( 'Reset Limits' ), MR_LANG( 'West Limit' ), MR_LANG( 'East Limit' ),  MR_LANG( 'Store Position' ) ]
		icon = [ 'OSDRewindNF.png', 'OSDLeft.png', 'OSDPauseNF.png', 'OSDRight.png', 'OSDForwardNF.png' ]

		itemHeight = int( self.getProperty( 'ItemHeight' ) )

		self.mListItems = []

		# Set Menu and Icons
		for i in range( len( context ) ) :
			motorizedItem = xbmcgui.ListItem( context[i] )
			if i < len( icon ) :
				motorizedItem.setProperty( 'HotKey', icon[i] )
			self.mListItems.append( motorizedItem )

		self.mCtrlList = self.getControl( DIALOG_LIST_ID )
		self.mCtrlList.addItems( self.mListItems )

		# Set Dialog Size
		height = 9 * itemHeight
		self.getControl( DIALOG_MIDDLE_IMAGE_ID ).setHeight( height )

		# Set Dialog Bottom Image
		middle_y, empty = self.getControl( DIALOG_MIDDLE_IMAGE_ID ).getPosition( )
		middley_height = self.getControl( DIALOG_MIDDLE_IMAGE_ID ).getHeight( )
		self.getControl( DIALOG_BOTTOM_IMAGE_ID ).setPosition( 0, middle_y + middley_height )

		# Set Center Align
		start_x = E_WINDOW_WIDTH / 2 - DIALOG_WIDTH / 2
		start_y = E_WINDOW_HEIGHT / 2 - middley_height / 2
		self.getControl( DIALOG_MAIN_GROUP_ID ).setPosition( start_x, start_y )

		self.setFocusId( DIALOG_LIST_ID )

		self.setProperty( 'DialogDrawFinished', 'True' )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.CloseDialog( )

		elif actionId == Action.ACTION_MBOX_REWIND :
			self.mCtrlList.selectItem( E_MOVE_WEST )
			self.mCommander.Motorized_GoWest( self.mTunerIndex )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.mCtrlList.selectItem( E_STEP_WEST )
			self.mCommander.Motorized_StepWest( self.mTunerIndex )

		elif actionId == Action.ACTION_PAUSE or actionId == Action.ACTION_PLAYER_PLAY :
			self.mCtrlList.selectItem( E_STOP )
			self.mCommander.Motorized_Stop( self.mTunerIndex )

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.mCtrlList.selectItem( E_STEP_EAST )
			self.mCommander.Motorized_StepEast( self.mTunerIndex )

		elif actionId == Action.ACTION_MBOX_FF :
			self.mCtrlList.selectItem( E_MOVE_EAST )
			self.mCommander.Motorized_GoEast( self.mTunerIndex )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass


	def onFocus( self, aControlId ) :
		pass


	def onClick( self, aControlId ) :
		if aControlId == DIALOG_BUTTON_CLOSE_ID :
			self.CloseDialog( )
		else :
			selectedIndex = self.mCtrlList.getSelectedPosition( )
			if selectedIndex == E_MOVE_WEST :
				self.mCommander.Motorized_GoWest( self.mTunerIndex )

			elif selectedIndex == E_STEP_WEST :
				self.mCommander.Motorized_StepWest( self.mTunerIndex )

			elif selectedIndex == E_STOP :
				self.mCommander.Motorized_Stop( self.mTunerIndex )

			elif selectedIndex == E_STEP_EAST :
				self.mCommander.Motorized_StepEast( self.mTunerIndex )

			elif selectedIndex == E_MOVE_EAST :
				self.mCommander.Motorized_GoEast( self.mTunerIndex )

			elif selectedIndex == E_LIMIT_RESET :
				ret = self.mCommander.Motorized_ResetLimit( self.mTunerIndex )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				if ret :
					dialog.SetDialogProperty(  MR_LANG( 'Reset complete' ),  MR_LANG( 'Reset limit complete' ) )
				else :
					dialog.SetDialogProperty(  MR_LANG( 'Error' ),  MR_LANG( 'Reset limit failed to complete' ) )
		 		dialog.doModal( )
			
			elif selectedIndex == E_WEST_LIMIT :
				ret = self.mCommander.Motorized_SetWestLimit( self.mTunerIndex )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				if ret :
					dialog.SetDialogProperty(  MR_LANG( 'Set complete' ),  MR_LANG( 'Set limit complete' ) )
				else :
					dialog.SetDialogProperty(  MR_LANG( 'Error' ),  MR_LANG( 'Set limit failed to complete' ) )
		 		dialog.doModal( )

			elif selectedIndex == E_EAST_LIMIT :
				ret = self.mCommander.Motorized_SetEastLimit( self.mTunerIndex )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				if ret :
					dialog.SetDialogProperty(  MR_LANG( 'Set complete' ),  MR_LANG( 'Set limit complete' ) )
				else :
					dialog.SetDialogProperty(  MR_LANG( 'Error' ),  MR_LANG( 'Set limit failed to complete' ) )
		 		dialog.doModal( )

			elif selectedIndex == E_SAVE_POSITION :	
				ret = self.mCommander.Motorized_SavePosition( self.mTunerIndex, ConfigMgr.GetInstance( ).GetCurrentConfigIndex( ) + 1 )			
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
				if ret :
					dialog.SetDialogProperty(  MR_LANG( 'Save complete' ),  MR_LANG( 'Save position complete' ) )
				else :
					dialog.SetDialogProperty(  MR_LANG( 'Error' ),  MR_LANG( 'Save position failed to complete' ) )
		 		dialog.doModal( )
			else :
				self.CloseDialog( )


