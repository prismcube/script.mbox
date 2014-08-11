from pvr.gui.WindowImport import *
from subprocess import *


FILE_NAME_MAKE_SCRIPT			= '/mtmp/customscript.sh'
FILE_NAME_SCRIPT_LOG			= '/mtmp/customscript.log'


CONTROL_ID_PROGRESS_SCAN		= 400
CONTROL_ID_BUTTON_CANCEL		= 300
CONTROL_ID_BUTTON_CLOSE			= 301
CONTROL_ID_LABEL_STRING			= 201
CONTROL_ID_TEXTBOX				= 202


class DialogCustomScriptProgress( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mScriptFileName			= None

		self.mCtrlProgress				= None
		self.mCtrlTextbox				= None
		self.mCtrlLabelString			= None
		self.mCtrlButtonCancel			= None

		self.mRunScriptThread			= None
		self.mCheckStatusFileThread		= None
		self.mCheckStatusRunning		= False

		self.mProcessId					= 0
		self.mTotalStep					= 0


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		self.mCtrlProgress		= self.getControl( CONTROL_ID_PROGRESS_SCAN )
		self.mCtrlTextbox		= self.getControl( CONTROL_ID_TEXTBOX )
		self.mCtrlLabelString	= self.getControl( CONTROL_ID_LABEL_STRING )
		self.mCtrlButtonCancel	= self.getControl( CONTROL_ID_BUTTON_CANCEL )

		self.mCtrlLabelString.setLabel( MR_LANG( 'Ready' ) )
		self.mCtrlButtonCancel.setLabel( MR_LANG( 'Cancel' ) )

		os.system( 'rm -rf %s' % FILE_NAME_MAKE_SCRIPT )

		if self.MakeCustomScript( ) :
			p = Popen( FILE_NAME_MAKE_SCRIPT, shell=True )
			self.mProcessId = p.pid

			self.mCheckStatusFileThread = threading.Timer( 0.5, self.CheckRunScriptStatus )
			self.mCheckStatusRunning = True
			self.mCheckStatusFileThread.start( )

		else :
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_POPUP_OK )
			dialog.SetDialogProperty( MR_LANG( 'Error' ), MR_LANG( 'Could not read script from file' ) )
 			dialog.doModal( )
 			self.CloseDialog( )


	def SetDialogProperty( self, aFile ) :
		self.mScriptFileName = aFile


	def MakeCustomScript( self ) :
		try :
			inputFile = open( self.mScriptFileName, 'r' )
			outputFile = open( FILE_NAME_MAKE_SCRIPT, 'w' )
			inputline = inputFile.readlines( )
			startCmd = False
			step = 0
			for line in inputline :
				if line == None or line == '' or line == '\n' :
					continue

				if line.rstrip( ).lower( ) == 'start' :
					outputFile.writelines( 'echo start!!! > %s\n' % FILE_NAME_SCRIPT_LOG )
				elif line.rstrip( ).lower( ) == 'end' :
					outputFile.writelines( 'echo ok!!! >> %s\n' % FILE_NAME_SCRIPT_LOG )
					outputFile.writelines( 'echo finish!!! >> %s\n' % FILE_NAME_SCRIPT_LOG )
				elif line.startswith( 'step' ) :
					words = string.split( line )
					self.mTotalStep = int( words[1] )
					outputFile.writelines( 'echo ok!!! >> %s\n' % FILE_NAME_SCRIPT_LOG )
					outputFile.writelines( 'echo step %s >> %s\n' % ( step, FILE_NAME_SCRIPT_LOG ) )
					step += 1
					startCmd = True
				else :
					if startCmd :
						tmpline = line
						if len( tmpline.rstrip( ) ) > 50 :
							tmpline = tmpline.rstrip( )[ : 50 ]
						outputFile.writelines( 'echo %s... >> %s\n' % ( tmpline.rstrip( ), FILE_NAME_SCRIPT_LOG ) )
						outputFile.writelines( line )
						startCmd = False
					else :
						outputFile.writelines( line )
			
			inputFile.close( )
			outputFile.close( )
			os.system( 'chmod 777 %s' % FILE_NAME_MAKE_SCRIPT )
			os.system( 'sync' )
			return True

		except Exception, e :
			LOG_ERR( 'MakeCustomScript Error' )
			if inputFile.closed == False :
				inputFile.close( )
			if outputFile.closed == False :
				outputFile.close( )

			return False


	def CheckRunScriptStatus( self ) :
		waitTime = 0
		while waitTime < 5 :
			if CheckDirectory( FILE_NAME_SCRIPT_LOG ) :
				break

			waitTime += 1
			time.sleep( 1 )

		if not CheckDirectory( FILE_NAME_SCRIPT_LOG ) :
			self.setProperty( 'ShellDescription', 'Run script error' )
			time.sleep( 1 )
			return

		fp = None
		try :
			fp = open( FILE_NAME_SCRIPT_LOG )
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
					if not v.startswith( 'step' ) :
						testline.append( v )
						outputs += v

					if len( testline ) > LINEMAX :
						testline.pop( 0 )
						outputs = ''
						for t in testline :
							outputs += t

					self.setProperty( 'ShellDescription', outputs )

					if v.rstrip( ) == 'finish!!!' :
						self.mCtrlLabelString.setLabel( MR_LANG( 'Completed' ) )
						self.mCtrlButtonCancel.setLabel( MR_LANG( 'Close' ) )
						self.mCtrlProgress.setPercent( 100 )
						time.sleep( 1 )
						self.mCheckStatusRunning = False

					elif v.rstrip( ) == 'start!!!' :
						time.sleep( 1 )
						self.mCtrlLabelString.setLabel( MR_LANG( 'Processing' ) )

					elif v.startswith( 'step' ) :
						words = string.split( v )
						step = int( words[1] )
						percent = int ( step * 100 / self.mTotalStep )
						self.mCtrlProgress.setPercent( percent )

			else :
				time.sleep( 1 )

		fp.close( )
		self.mCheckStatusFileThread = None


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.Close( )


	def onClick( self, aControlId ) :
		if aControlId == CONTROL_ID_BUTTON_CLOSE :
			self.Close( )

		elif aControlId == CONTROL_ID_BUTTON_CANCEL :
			self.Close( )


	def onFocus( self, aControlId ) :
		pass


	def Close( self ) :
		if self.mCheckStatusFileThread :
			self.mCheckStatusRunning = False
			self.mCheckStatusFileThread.join( )
		KillScript( self.mProcessId )
		self.CloseDialog( )

