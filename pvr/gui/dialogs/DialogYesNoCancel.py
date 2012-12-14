from pvr.gui.WindowImport import *


E_BUTTON_YES	= 301
E_BUTTON_NO		= 302
E_BUTTON_CLOSE	= 303
E_HEADER		= 100
E_BODY_LABEL_1	= 200


class DialogYesNoCancel( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mIsOk = E_DIALOG_STATE_NO
		self.mTitle = ''
		self.mLabel = ''


	def onInit( self ) :
		self.mIsOk = E_DIALOG_STATE_NO
		self.getControl( E_HEADER ).setLabel( self.mTitle )
		self.getControl( E_BODY_LABEL_1 ).setLabel( self.mLabel )
		self.mIsOk = E_DIALOG_STATE_CANCEL


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.CloseDialog( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass


	def onClick( self, aControlId ) :
		if aControlId == E_BUTTON_YES :
			self.mIsOk = E_DIALOG_STATE_YES
			xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )
			#self.CloseDialog( )

		elif aControlId == E_BUTTON_NO :
			self.mIsOk = E_DIALOG_STATE_NO
			xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )			
			#self.CloseDialog( )

		elif aControlId == E_BUTTON_CLOSE :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			xbmc.executebuiltin( 'xbmc.Action(previousmenu)' )			
			#self.CloseDialog( )

	def IsOK( self ) :
		return self.mIsOk


	def onFocus( self, aControlId ) :
		pass


	def SetDialogProperty( self, aTitle='', aLabel='' ) :
		self.mTitle = aTitle
		self.mLabel = aLabel

