from pvr.gui.WindowImport import *


E_BUTTON_OK		= 301
E_HEADER		= 100
E_BODY_LABEL_1	= 200


class DialogPopupOK( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )	
		self.mTitle = ''
		self.mLabel = ''
		

	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		
		self.getControl( E_HEADER ).setLabel( self.mTitle )
		self.getControl( E_BODY_LABEL_1 ).setLabel( self.mLabel )		
		
	def onAction( self, aAction ) :
		actionId = aAction.getId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.CloseDialog( )
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
			
		elif actionId == Action.ACTION_PARENT_DIR :
			self.CloseDialog( )
			

	def onClick( self, aControlId ) :
		if aControlId == E_BUTTON_OK :
			self.CloseDialog( )


	def onFocus( self, aControlId ) :
		pass
		

	def SetDialogProperty( self, aTitle='', aLabel='' ) :
		self.mTitle = aTitle
		self.mLabel = aLabel
