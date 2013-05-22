from pvr.gui.WindowImport import *


E_BUTTON_YES	= 301
E_BUTTON_NO		= 302
E_BUTTON_CLOSE	= 303
E_HEADER		= 100
E_BODY_LABEL_1	= 200
E_BODY_LABEL_2	= 201


TIME_OUT		= 10


class DialogVideoRestore( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mIsOk = E_DIALOG_STATE_CANCEL
		self.mEnableLocalThread 	= False


	def onInit( self ) :
		print 'dhkim test start dialog'
		self.mIsOk = E_DIALOG_STATE_CANCEL
		self.getControl( E_HEADER ).setLabel( MR_LANG( 'Save video setting' ) )
		self.getControl( E_BODY_LABEL_1 ).setLabel( MR_LANG( 'Do you want to save video setting?' ) )
		self.getControl( E_BODY_LABEL_2 ).setLabel( MR_LANG( 'Restore video setting %s sec' ) % TIME_OUT )
		self.mEnableLocalThread = True
		self.mThread = self.AsyncRestore( )
		self.IsStandByClose( )
		print 'dhkim test end onInit dialog'


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			thread = threading.Timer( 0.1, self.Close )
			thread.start( )


	def onClick( self, aControlId ) :
		if aControlId == E_BUTTON_YES :
			self.mIsOk = E_DIALOG_STATE_YES
		elif aControlId == E_BUTTON_NO :
			self.mIsOk = E_DIALOG_STATE_NO
		elif aControlId == E_BUTTON_CLOSE :
			self.mIsOk = E_DIALOG_STATE_CANCEL

		thread = threading.Timer( 0.1, self.Close )
		thread.start( )


	def IsOK( self ) :
		return self.mIsOk


	def onFocus( self, aControlId ) :
		pass


	"""
	def SetDialogProperty( self, aTitle = '', aLabel = '', aDefaultClose = False ) :
		self.mTitle = aTitle
		self.mLabel = aLabel
		self.mDefaultIsOk = aDefaultClose
	"""

	@RunThread
	def AsyncRestore( self ) :
		print 'dhkim test start thread'
		for i in range( TIME_OUT ) :
			print 'dhkim test AsyncRestore time = %s' % ( TIME_OUT - i )
			time.sleep( 1 )
			if self.mEnableLocalThread == False :
				return
			self.getControl( E_BODY_LABEL_2 ).setLabel( MR_LANG( 'Restore video setting %s sec' ) % ( TIME_OUT - i ) )

		thread = threading.Timer( 1, self.Close )
		thread.start( )


	def Close( self ) :
		if self.mThread and self.mEnableLocalThread == True :
			self.mEnableLocalThread = False
			self.mThread.join( )

		self.CloseDialog( )


	def IsStandByClose( self ) :
		if self.mDataCache.GetStanbyClosing( ) :
			time.sleep( 0.3 )
			if self.mDefaultIsOk :
				self.mIsOk = E_DIALOG_STATE_YES
			else :
				self.mIsOk = E_DIALOG_STATE_NO
			thread = threading.Timer( 0.1, self.Close )
			thread.start( )

