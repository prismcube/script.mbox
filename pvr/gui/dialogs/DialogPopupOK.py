from pvr.gui.WindowImport import *


E_BUTTON_OK		= 301
E_HEADER		= 100
E_BODY_LABEL_1	= 200
E_BODY_LABEL_2	= 300
E_BODY_LABEL_3	= 400


class DialogPopupOK( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )	
		self.mTitle = ''
		self.mLabel1 = ''
		self.mLabel2 = ''
		self.mLabel3 = ''
		

	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		
		self.getControl( E_HEADER ).setLabel( self.mTitle )
		self.getControl( E_BODY_LABEL_1 ).setLabel( self.mLabel1 )
		self.getControl( E_BODY_LABEL_2 ).setLabel( self.mLabel2 )
		self.getControl( E_BODY_LABEL_3 ).setLabel( self.mLabel3 )

		
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
		

	def SetDialogProperty( self, aTitle='', aLabel1='', aLabel2='', aLabel3='' ) :
		self.mTitle = aTitle
		self.mLabel1 = aLabel1
		self.mLabel2 = aLabel2
		self.mLabel3 = aLabel3
		if self.mLabel2 == '' and self.mLabel3 == '' :
			self.mLabel2 = self.mLabel1
			self.mLabel1 = ''