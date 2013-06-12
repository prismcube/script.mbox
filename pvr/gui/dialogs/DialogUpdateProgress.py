from pvr.gui.WindowImport import *
import os, threading

PROGRESS_SCAN		= 400
BUTTON_CANCEL		= 300
BUTTON_CLOSE		= 301
LABEL_TITLE			= 200
LABEL_STRING		= 201

E_COMMAND_SHELL_STATUS    = '/mtmp/update.status'
E_COMMAND_SHELL_CANCEL    = '/mtmp/force.stop'
E_COMMAND_SHELL_STOP      = '/mtmp/update.stop'
E_COMMAND_SHELL_COMPLETE  = '/mtmp/update.complete'
E_COMMAND_SHELL_LOG       = '/mtmp/update.log'


class DialogUpdateProgress( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mLimitTime 		= 10
		self.mTitle				= None
		self.mFinish			= False
		self.mScriptFile 		= ''
		self.mFirmware 			= ''
		self.mRunShell          = True
		self.mRunShellThread    = None
		self.mReturnShell       = 0
		self.mStatusCancel      = False


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		#self.mEventBus.Register( self )

		self.mCtrlLabelTitle	= self.getControl( LABEL_TITLE )
		self.mCtrlLabelString	= self.getControl( LABEL_STRING )
		self.mCtrlProgress		= self.getControl( PROGRESS_SCAN )

		self.mCtrlLabelTitle.setLabel( self.mTitle )
		self.mCtrlLabelString.setLabel( MR_LANG( 'Waiting' ) + ' - 0 %' )

		#self.DrawProgress( )
		#self.setProperty( 'ShellDescription', mLine )
		thread = threading.Timer( 0.5, self.DoCommandRunShell )
		thread.start( )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if self.mStatusCancel :
			LOG_TRACE( 'blocking key : canceling' )
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.UpdateStepShellCancel( )
			self.Close( )


	def onClick( self, aControlId ) :
		if self.mStatusCancel :
			LOG_TRACE( 'blocking key : canceling' )
			return

		if aControlId == BUTTON_CLOSE :
			self.UpdateStepShellCancel( )
			self.Close( )

		elif aControlId == BUTTON_CANCEL :
			self.UpdateStepShellCancel( )
			self.Close( )


	def onFocus( self, aControlId ) :
		pass


	def SetDialogProperty( self, aTitle, aScriptFile, aFirmware ) :
		self.mLimitTime  = aLimitTime
		self.mTitle      = aTitle
		self.mScriptFile = aScriptFile
		self.mFirmware   = aFirmware
		self.mFinish     = False
		self.mStatusCancel = False


	def TimeoutProgress( self, aLimitTime, aTitle ) :
		if aLimitTime < 1 :
			break

		waitTime = 1
		while self.mRunShellThread :
			if waitTime > aLimitTime :
				self.DrawProgress( 0, MR_LANG( 'timed out' ) )
				break

			percent = int( waitTime / aLimitTime * 100 )
			if percent > 100 :
				percent = 100
			self.DrawProgress( percent, aTitle )
			
			waitTime += 1
			time.sleep( 1 )


	def DrawProgress( self, aPercent, aLabel = None ) :
		if aLabel == None :
			aLabel = MR_LANG( 'Waiting' )

		mLabel = aLabel + ' - %d %%' % percent
		self.mCtrlLabelString.setLabel( mLabel )
		self.mCtrlProgress.setPercent( percent )


	def Close( self ) :
		#self.mEventBus.Deregister( self )
		time.sleep( 1 )
		self.CloseDialog( )


	def GetResult( self ) :
		return self.mFinish


	def DoCommandRunShell( self ) :
		ret = True
		self.mReturnShell = 0
		self.mRunShell = True
		self.mRunShellThread = None

		RemoveDirectory( E_COMMAND_SHELL_LOG )
		RemoveDirectory( E_COMMAND_SHELL_STOP )
		RemoveDirectory( E_COMMAND_SHELL_CANCEL )
		RemoveDirectory( E_COMMAND_SHELL_STATUS )
		RemoveDirectory( E_COMMAND_SHELL_COMPLETE )
		os.system( 'sync' )

		if self.mScriptFile :
			thread = threading.Timer( 0.1, self.UpdateStepRunShell )
			thread.start( )

			self.mRunShellThread = threading.Timer( 0.5, self.UpdateStepShellStatus )
			self.mRunShellThread.start( )

			thread2 = threading.Timer( 0.5, self.UpdateStepShellProgress )
			thread2.start( )

			if self.mRunShellThread :
				LOG_TRACE( '---------------wait shell[%s]'% self.mRunShell )
				self.mRunShellThread.join( )

			LOG_TRACE( '---------------wait progress[%s]'% self.mRunShell )
			thread2.join( )

		else :
			self.mReturnShell = -1
			self.mRunShell = False

		#while self.mRunShell :
		#	time.sleep( 1 )
		#	LOG_TRACE( '---------------wait shell[%s]'% self.mRunShell )


		percent = 100
		statusLabel = MR_LANG( 'Complete' )
		if self.mReturnShell < 0 :
			percent = 0
			if self.mReturnShell == -1 :
				LOG_TRACE( '--------shell fail' )
				statusLabel = MR_LANG( 'Fail' )
			elif self.mReturnShell < -1 :
				LOG_TRACE( '--------shell cancel' )
				statusLabel = MR_LANG( 'Cancel' )

			self.mRunShell = False
			ret = False

		self.DrawProgress( percent, statusLabel )
		self.mFinish = ret
		self.Close( )


	def UpdateStepRunShell( self ) :
		cmd = '%s start %s'% ( self.mScriptFile, self.mFirmware )
		LOG_TRACE( '---------------run shell[%s]'% cmd )
		os.system( cmd )


	def UpdateStepShellStatus( self ) :
		if not CheckDirectory( E_COMMAND_SHELL_LOG ) :
			self.mRunShell = False
			self.mReturnShell = -1
			LOG_TRACE( '---------------file not found [%s]'% E_COMMAND_SHELL_LOG )
			time.sleep( 1 )
			return

		f = open( E_COMMAND_SHELL_LOG )
		f.seek( 0, 2 )            # go to END
		outputs = ''
		while self.mRunShellThread :
			if CheckDirectory( E_COMMAND_SHELL_COMPLETE ) :
				LOG_TRACE( '-------------------done complete' )
				self.mReturnShell = 0
				break

			if CheckDirectory( E_COMMAND_SHELL_STOP ) :
				LOG_TRACE( '-------------------stop' )
				self.mReturnShell = -1
				break

			lines = f.readlines( )
			if lines :
				for v in lines :
					#print v,
					outputs += v
					self.setProperty( 'ShellDescription', outputs )
			else:
				time.sleep( 0.5 )

		f.close( )
		self.mRunShell = False


	def UpdateStepShellProgress( self ) :
		title = MR_LANG( 'Waiting' )

		while self.mRunShell :
			if CheckDirectory( E_COMMAND_SHELL_STOP ) :
				LOG_TRACE( '-------------------stop' )
				self.mReturnShell = -1
				break

			if CheckDirectory( E_COMMAND_SHELL_STATUS ) :
				percent = GetFileRead( E_COMMAND_SHELL_STATUS )
				RemoveDirectory( E_COMMAND_SHELL_STATUS )
				if percent and percent.isdigit( ) :
					self.DrawProgress( percent, title )

			time.sleep( 0.5 )

		self.mRunShell = False


	def UpdateStepShellCancel( self ) :
		LOG_TRACE( '--------------abort(shell)' )
		self.mStatusCancel = True
		CreateFile( E_COMMAND_SHELL_CANCEL )
		self.mReturnShell = -2
		self.mRunShell = False

		thread = self.TimeoutProgress( 60, MR_LANG( 'Canceling' ) )
		LOG_TRACE( '--------------abort(shell) runThread[%s]'% self.mRunShellThread )

		self.mRunShellThread = None


