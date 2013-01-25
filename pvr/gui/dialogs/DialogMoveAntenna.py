from pvr.gui.WindowImport import *
import pvr.TunerConfigMgr as ConfigMgr

E_MOVE_WEST					= 0
E_STEP_WEST					= 1
E_STOP						= 2
E_STEP_EAST					= 3
E_MOVE_EAST					= 4
E_CLOSE						= 5

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

		self.mTunerIndex = ConfigMgr.GetInstance( ).GetCurrentTunerNumber( )

		context = [ MR_LANG( 'Rotate to West' ), MR_LANG( 'One step to West' ), MR_LANG( 'Stop' ), MR_LANG( 'One step to East' ), MR_LANG( 'Rotate to East' ), MR_LANG( 'Close' ) ]

		itemHeight = int( self.getProperty( 'ItemHeight' ) )
		self.mCtrlList = self.getControl( DIALOG_LIST_ID )

		for i in range( len( context ) ) :
			self.mCtrlList.addItem( context[i] )

		# Set Dialog Size
		height = 6 * itemHeight
		self.getControl( DIALOG_MIDDLE_IMAGE_ID ).setHeight( height )

		# Set Dialog Bottom Image
		middle_y, empty = self.getControl( DIALOG_MIDDLE_IMAGE_ID ).getPosition( )
		middley_height = self.getControl( DIALOG_MIDDLE_IMAGE_ID ).getHeight( )
		self.getControl( DIALOG_BOTTOM_IMAGE_ID ).setPosition( 0, middle_y + middley_height )

		# Set Center Align
		start_x = E_WINDOW_WIDTH / 2 - DIALOG_WIDTH / 2
		start_y = E_WINDOW_HEIGHT / 2 - middley_height / 2
		self.getControl( DIALOG_MAIN_GROUP_ID ).setPosition( start_x, start_y )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.CloseDialog( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass


	def onFocus( self, aControlId ) :
		pass


	def onClick( self, aControlId ) :
		if aControlId == DIALOG_BUTTON_CLOSE_ID :
			xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )
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

			else :
				xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )

