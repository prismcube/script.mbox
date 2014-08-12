from pvr.gui.WindowImport import *
from subprocess import *


CONTROL_ID_HEADER				= 200
CONTROL_ID_PROGRESS_SCAN		= 400
CONTROL_ID_BUTTON_CANCEL		= 300
CONTROL_ID_BUTTON_CLOSE			= 301
CONTROL_ID_LABEL_STRING			= 201
CONTROL_ID_TEXTBOX				= 202


class DialogRootfsBackup( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mHeaderLabel				= 'None'
		self.mScriptFileName			= None
		self.mLogFileName				= None
		self.mDirectoryName				= None

		self.mCtrlProgress				= None
		self.mCtrlTextbox				= None
		self.mCtrlLabelString			= None
		self.mCtrlButtonCancel			= None

		self.mRunScriptThread			= None
		self.mCheckStatusFileThread		= None
		self.mCheckStatusSecond			= None
		self.mCheckStatusRunning		= False

		self.mProcessId					= 0
		self.mPipe						= None
		self.mReturnShell 				= False

		self.Isbusy						= False


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.mCtrlProgress		= self.getControl( CONTROL_ID_PROGRESS_SCAN )
		self.mCtrlTextbox		= self.getControl( CONTROL_ID_TEXTBOX )
		self.mCtrlLabelString	= self.getControl( CONTROL_ID_LABEL_STRING )
		self.mCtrlButtonCancel	= self.getControl( CONTROL_ID_BUTTON_CANCEL )

		self.getControl( CONTROL_ID_HEADER ).setLabel( self.mHeaderLabel )
		self.mCtrlLabelString.setLabel( MR_LANG( 'Ready' ) )
		self.mCtrlButtonCancel.setLabel( MR_LANG( 'Cancel' ) )

		try :
			self.mPipe = Popen( '%s %s' % ( self.mScriptFileName, self.mDirectoryName ), shell=True )
			self.mProcessId = self.mPipe.pid

			self.mCheckStatusFileThread = threading.Timer( 0.5, self.CheckRunScriptStatus )
			self.mCheckStatusSecond		= threading.Timer( 6, self.RunSecond )
			self.mCheckStatusRunning = True
			self.mCheckStatusFileThread.start( )
			self.mCheckStatusSecond.start( )
		except Exception, e :
			LOG_ERR( 'Exception[%s]'% e )


	def SetDialogProperty( self, aLabel, aRunScript, aLogScript, aArg1=None ) :
		self.mHeaderLabel = aLabel
		self.mScriptFileName = aRunScript
		self.mLogFileName = aLogScript
		self.mDirectoryName = aArg1


	def RunSecond( self ) :
		for i in range( 100 ) : # 13.3 min
			time.sleep( 8 )
			if self.mCheckStatusRunning == False :
				break

			strProcess = MR_LANG( 'Processing' ) + ' - %s%%'
			self.mCtrlLabelString.setLabel( strProcess % i )
			self.mCtrlProgress.setPercent( i )

		self.mCheckStatusSecond = None


	def CheckRunScriptStatus( self ) :
		waitTime = 0
		while waitTime < 5 :
			if CheckDirectory( self.mLogFileName ) :
				break

			waitTime += 1
			time.sleep( 1 )

		if not CheckDirectory( self.mLogFileName ) :
			self.setProperty( 'ShellDescription', MR_LANG( 'Run script error' ) )
			time.sleep( 1 )
			return

		fp = None
		try :
			fp = open( self.mLogFileName )
		except Exception, e :
			LOG_ERR( 'Exception[%s]'% e )
			fp = None

		if fp == None :
			return

		LINEMAX = 6
		outputs = ''
		testline = []
		while self.mCheckStatusRunning :
			lines = fp.readlines( )
			if lines :
				for v in lines :
					#print v,
					testline.append( v )
					outputs += v
					if len( testline ) > LINEMAX :
						testline.pop( 0 )
						outputs = ''
						for t in testline :
							outputs += t

					self.setProperty( 'ShellDescription', outputs )
					if v.rstrip( ) == 'Done' :
						self.mCtrlLabelString.setLabel( MR_LANG( 'Completed' ) )
						self.mCtrlButtonCancel.setLabel( MR_LANG( 'Close' ) )
						self.mCtrlProgress.setPercent( 100 )
						self.mCheckStatusRunning = False
						self.mReturnShell = True
						break

			if self.mPipe.poll( ) != None :
				self.mCtrlButtonCancel.setLabel( MR_LANG( 'Close' ) )
				self.mCtrlProgress.setPercent( 100 )
				time.sleep( 1 )
				self.mCheckStatusRunning = False
				break

			else :
				time.sleep( 0.5 )

		fp.close( )
		self.mCheckStatusFileThread = None


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if self.Isbusy :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.Close( )


	def onClick( self, aControlId ) :
		if self.Isbusy :
			return
		
		if aControlId == CONTROL_ID_BUTTON_CLOSE :
			self.Close( )

		elif aControlId == CONTROL_ID_BUTTON_CANCEL :
			self.Close( )


	def onFocus( self, aControlId ) :
		pass


	def Close( self ) :
		self.Isbusy = True
		xbmc.executebuiltin( "ActivateWindow(busydialog)" )
		if self.mReturnShell == False :
			strProcess = MR_LANG( 'Processing' )
			strCancel = MR_LANG( 'Canceling' )
			strClose = strProcess + ' - ' + strCancel + '...'
			self.mCtrlLabelString.setLabel( strClose )
			try :
				self.mPipe.kill( )
			except Exception, e :
				LOG_ERR( 'Error exception[%s]' % e )
			KillScript( self.mProcessId )
		if self.mCheckStatusFileThread :
			self.mCheckStatusRunning = False
			self.mCheckStatusFileThread.join( )
		if self.mCheckStatusSecond :
			self.mCheckStatusRunning = False
			self.mCheckStatusSecond.join( )

		xbmc.executebuiltin( "Dialog.Close(busydialog)" )
		self.CloseDialog( )


	def GetResultStatus( self ) :
		return self.mReturnShell

