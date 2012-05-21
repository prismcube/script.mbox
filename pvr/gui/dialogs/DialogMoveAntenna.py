from pvr.gui.WindowImport import *
import pvr.TunerConfigMgr as ConfigMgr


E_MOVE_WEST_BUTTON_ID		= 9101
E_STEP_WEST_BUTTON_ID		= 9201
E_STOP_BUTTON_ID			= 9301
E_STEP_EAST_BUTTON_ID		= 9401
E_MOVE_EAST_BUTTON_ID		= 9501


class DialogMoveAntenna( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		
		
	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.Window( self.mWinId )	

		self.tunerIndex = ConfigMgr.GetInstance( ).GetCurrentTunerIndex( )
		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )

		self.GlobalAction( actionId )
		
		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.CloseDialog( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.CloseDialog( )


	def onClick( self, aControlId ) :
 		if aControlId == E_MOVE_WEST_BUTTON_ID :
 			self.mCommander.Motorized_GoWest( self.tunerIndex )

 		elif aControlId == E_STEP_WEST_BUTTON_ID :
 			self.mCommander.Motorized_StepWest( self.tunerIndex )

 		elif aControlId == E_STOP_BUTTON_ID :
 			self.mCommander.Motorized_Stop( self.tunerIndex )

 		elif aControlId == E_STEP_EAST_BUTTON_ID :
 			self.mCommander.Motorized_StepEast( self.tunerIndex )

 		elif aControlId == E_MOVE_EAST_BUTTON_ID :
			self.mCommander.Motorized_GoEast( self.tunerIndex )
		
	def onFocus( self, aControlId ):
		pass
