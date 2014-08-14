from pvr.gui.WindowImport import *
import os, threading, copy, stat, re, types

PROGRESS_SCAN		= 400
BUTTON_CANCEL		= 300
BUTTON_CLOSE		= 301
LABEL_TITLE			= 200
LABEL_STRING		= 201
TEXTBOX				= 202

E_COMMAND_SHELL_STATUS    = '/mtmp/update.status'
E_COMMAND_SHELL_CANCEL    = '/mtmp/force.stop'
E_COMMAND_SHELL_STOP      = '/mtmp/update.stop'
E_COMMAND_SHELL_COMPLETE  = '/mtmp/update.complete'
E_COMMAND_SHELL_LOG       = '/mtmp/update.log'

E_RESULT_UPDATE_DONE     = 0
E_RESULT_ERROR_FAIL      = -1
E_RESULT_ERROR_CANCEL    = -2
E_RESULT_ERROR_CHECKSUME = -3

E_UPDATE_MODE_NETWORK = 0
E_UPDATE_MODE_LOCAL   = 1

E_FILE_SHELL_LOCAL = 'local_updater.sh'


class DialogUpdateProgress( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mTitle             = None
		self.mFinish            = 0
		self.mBaseDirectory     = ''
		self.mPVSData           = None
		self.mRunShell          = True
		self.mRunShellThread    = None
		self.mReturnShell       = E_RESULT_UPDATE_DONE
		self.mStatusCancel      = False
		self.mResultOutputs     = ''
		self.mShowBlink         = False
		self.mCheckFirmware     = False
		self.mUSBAttached 		= False
		self.mUSBmode           = False
		self.mUSBThread         = False
		self.mCheckSumError     = False
		self.mUpdateMode        = E_UPDATE_MODE_NETWORK


	def onInit( self ) :
		self.mWinId = xbmcgui.getCurrentWindowDialogId( )

		#self.mEventBus.Register( self )

		self.mCtrlLabelTitle    = self.getControl( LABEL_TITLE )
		self.mCtrlLabelString   = self.getControl( LABEL_STRING )
		self.mCtrlProgress      = self.getControl( PROGRESS_SCAN )
		self.mCtrlTextbox       = self.getControl( TEXTBOX )

		self.mCtrlLabelTitle.setLabel( self.mTitle )
		self.mCtrlLabelString.setLabel( MR_LANG( 'Ready to update' ) )

		ElisPropertyInt( 'Update Flag', self.mCommander ).SetProp( 1 )
		thread = threading.Timer( 1, self.DoUpdateHandler )
		thread.start( )

		LOG_TRACE( '-----usb mode[%s]'% self.mUSBmode )


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		if self.GlobalAction( actionId ) :
			return

		if self.mStatusCancel :
			LOG_TRACE( '------------blocking key : cancel' )
			if not self.mShowBlink :
				label = '%s%s'% ( MR_LANG( 'Please wait' ), ING )
				self.AsyncShowAlarm( label )
			return

		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.UpdateStepShellCancel( )


	def onClick( self, aControlId ) :
		if self.mStatusCancel :
			LOG_TRACE( '------------blocking key : cancel' )
			if not self.mShowBlink :
				label = '%s%s'% ( MR_LANG( 'Please wait' ), ING )
				self.AsyncShowAlarm( label )
			return

		if aControlId == BUTTON_CLOSE :
			self.UpdateStepShellCancel( )

		elif aControlId == BUTTON_CANCEL :
			self.UpdateStepShellCancel( )


	def onFocus( self, aControlId ) :
		pass


	def SetDialogProperty( self, aTitle, aBaseDir, aPVSData, aUsbmode = False, aUpdateMode = E_UPDATE_MODE_NETWORK ) :
		self.mBaseDirectory = aBaseDir
		self.mTitle         = aTitle
		self.mPVSData       = aPVSData
		self.mFinish        = E_RESULT_UPDATE_DONE
		self.mStatusCancel  = False
		self.mRunShellThread = None
		self.mUSBmode       = aUsbmode
		self.mUSBThread     = None
		self.mCheckSumError = False
		if self.mUSBmode :
			self.mUSBAttached = self.mDataCache.GetUSBAttached( )

		self.mUpdateMode = aUpdateMode


	def TimeoutProgress( self, aLimitTime, aTitle, aOutPuts = '', aDefaultPer = 0 ) :
		if aLimitTime < 1 :
			return

		waitTime = 1.0
		while self.mRunShellThread or self.mCheckFirmware :
			if waitTime > aLimitTime :
				self.DrawProgress( 0, MR_LANG( 'Timed out' ) )
				break

			percent = int( waitTime / aLimitTime * 100 ) + aDefaultPer
			if percent > 100 :
				percent = 100
			self.DrawProgress( percent, aTitle )

			if aOutPuts :
				aOutPuts += '.'
				self.setProperty( 'ShellDescription', aOutPuts )

			waitTime += 1
			time.sleep( 1 )


	def DrawProgress( self, aPercent, aLabel = None ) :
		if aLabel == None :
			aLabel = MR_LANG( 'Waiting' )

		if aPercent > 0 :
			aLabel += ' - %s %%' % aPercent
		self.mCtrlLabelString.setLabel( aLabel )
		self.mCtrlProgress.setPercent( aPercent )


	def Close( self ) :
		#self.mEventBus.Deregister( self )
		ElisPropertyInt( 'Update Flag', self.mCommander ).SetProp( 0 )
		if self.mUSBThread :
			self.mUSBmode = False
			self.mUSBThread.join( )
			LOG_TRACE( '----------USBThread join end' )

		self.mEnd = True
		self.mUpdateMode = E_UPDATE_MODE_NETWORK
		time.sleep( 1 )
		self.CloseDialog( )


	def GetResult( self ) :
		return self.mFinish


	def DoUpdateHandler( self ) :
		if self.mUpdateMode == E_UPDATE_MODE_LOCAL :
			self.DoCommandRunLocal( )
			self.DoCommandRunShell( )

		else :

			if self.mUSBmode :
				self.mUSBThread = self.CheckUSBThread( )

			if self.DoPreviousAction( ) and self.CheckFirmware( ) :
				self.DoCommandRunShell( )

		while not self.mStatusCancel and self.mCheckSumError :
			time.sleep( 0.5 )

		if self.mCheckSumError :
			self.mFinish = E_RESULT_ERROR_CHECKSUME

		self.Close( )


	def DoCommandRunLocal( self ) :
		LOG_TRACE( 'Local update...' )
		#LOG_TRACE( 'checksum[%s] baseDir[%s] localZip[%s] cancel[%s]'% ( self.mCheckSumError, self.mBaseDirectory, self.mPVSData, self.mStatusCancel ) )

		from pvr.gui.windows.SystemUpdate import PVSClass
		iPVS = PVSClass( )
		iPVS.mFileName = self.mPVSData
		iPVS.mShellScript.mScriptFileName = E_FILE_SHELL_LOCAL

		self.mPVSData = iPVS
		#self.mPVSData.printdebug( )
		#LOG_TRACE( '-------------localSh[%s]'% self.mPVSData.mShellScript.mScriptFileName )

		scriptShell = '%s/%s'% ( self.mBaseDirectory, self.mPVSData.mShellScript.mScriptFileName )
		for i in range( 3 ) :
			localsh = os.path.join( self.mPlatform.GetScriptDir( ), 'resources', E_FILE_SHELL_LOCAL )
			CopyToFile( localsh, scriptShell )

			if CheckDirectory( scriptShell ) :
				os.chmod( scriptShell, 0755 )
				break

			time.sleep( 1 )


	@RunThread
	def CheckUSBThread( self ) :
		while self.mUSBmode :
			self.mUSBAttached = self.mDataCache.GetUSBAttached( )
			tempFile = '%s/%s'% ( self.mBaseDirectory, self.mPVSData.mFileName )
			isExist = CheckDirectory( tempFile )
			LOG_TRACE( '--------------mUSBAttached[%s] isExist[%s]'% ( self.mUSBAttached, isExist ) )
			if ( not self.mUSBAttached ) or ( not isExist ) :
				self.mUSBAttached = False
				LOG_TRACE( '-------------------stop usb deteched' )
				self.UpdateStepShellCancel( )
				break

			time.sleep( 0.5 )


	def DoPreviousAction( self ) :
		ret = True
		if not self.mPVSData :
			self.mFinish = E_RESULT_ERROR_FAIL
			return False

		if not self.mPVSData.mActions :
			LOG_TRACE( '--------- No Actions' )
			return True

		desc = '%s'% MR_LANG( 'Prework in progress' )
		outputs = '[*] Prework actions%s'% NEW_LINE

		try :
			actions = re.split( '\n', self.mPVSData.mActions.rstrip( ) )
			LOG_TRACE( 'len[%s] actions[%s]'% ( len( actions ), actions ) )

			if not actions or len( actions ) < 1 :
				LOG_TRACE( '--------- No Actions' )
				return True

			cmdlen = len( actions )
			count = 0
			for cmd in actions :

				LOG_TRACE( '----------action[%s]'% cmd )
				if self.mStatusCancel :
					self.mFinish = E_RESULT_ERROR_CANCEL
					ret = False
					break

				count += 1.0
				outputs += '%s%s'% ( cmd, NEW_LINE )
				percent = int( ( count / cmdlen ) * 100 )

				self.setProperty( 'ShellDescription', outputs )
				self.DrawProgress( percent, desc )

				self.mRunShellThread = True
				thread = threading.Timer( 0.1, self.TimeoutProgress, [ 60, desc, outputs, percent ] )
				thread.start( )
				os.system( cmd )
				LOG_TRACE( '---------per[%s] count[%s]'% ( percent, count ) )

				self.mRunShellThread = False
				if thread :
					thread.join( )

				time.sleep( 1 )

		except Exception, e :
			LOG_ERR( 'Exception[%s]'% e )
			self.mFinish = E_RESULT_ERROR_FAIL
			ret = False

		percent = 100
		statusLabel = desc
		if self.mFinish < E_RESULT_UPDATE_DONE :
			percent = 0
			if self.mFinish == E_RESULT_ERROR_FAIL :
				LOG_TRACE( '--------Previous action failed' )
				statusLabel = MR_LANG( 'Failed' )
			elif self.mFinish == E_RESULT_ERROR_CANCEL :
				LOG_TRACE( '--------Previous action cancelled' )
				statusLabel = MR_LANG( 'Aborted' )
			else :
				LOG_TRACE( '--------Previous action stopped' )
				statusLabel = MR_LANG( 'Failed' )

		self.DrawProgress( percent, statusLabel )
		time.sleep( 1 )

		return ret


	def CheckFirmware( self ) :
		tempFile = '%s/%s'% ( self.mBaseDirectory, self.mPVSData.mFileName )
		isExist = CheckDirectory( tempFile )
		LOG_TRACE( '----------------file[%s]'% tempFile )
		#self.mPVSData.printdebug( )
		#LOG_TRACE( 'exist[%s] pvs[%s] usbfile size[%s] xml size[%s] path[%s]'% ( isExist, self.mPVSData, os.stat( tempFile )[stat.ST_SIZE], self.mPVSData.mSize, tempFile ) )

		if ( not isExist ) or ( not self.mPVSData ) or \
		   os.stat( tempFile )[stat.ST_SIZE] != self.mPVSData.mSize :
			self.mCheckSumError = True
			LOG_TRACE( '---------------check error, firmware' )
			desc = '[*] Error checking files'
			outputs = '%s%s%s'% ( E_TAG_COLOR_RED, desc, E_TAG_COLOR_END )
			self.setProperty( 'ShellDescription', outputs )
			self.DrawProgress( 0, MR_LANG( 'Failed' ) )
			RemoveDirectory( tempFile )
			return False

		self.mCheckFirmware = True
		desc1 = '%s'% MR_LANG( 'Verification in progress' )
		desc2 = '[*] Checking files checksum'
		thread = threading.Timer( 0.1, self.TimeoutProgress, [ 30, desc1 , desc2 ] )
		thread.start( )

		ret = False
		retval = CheckMD5Sum( tempFile, self.mPVSData.mMd5, True )
		self.mCheckFirmware = False

		if thread :
			thread.join ( )

		LOG_TRACE( '---------retval[%s]'% list( retval ) )
		if type( retval ) == types.TupleType :
			ret, readmd5, xmlmd5 = retval
			LOG_TRACE( '--------------ret[%s] read[%s] xml[%s]'% ( ret, readmd5, xmlmd5 ) )
			if not ret :
				outputs = '%s%s%s%sFail%s%s'% ( desc2, NEW_LINE, NEW_LINE, E_TAG_COLOR_RED, E_TAG_COLOR_END, NEW_LINE )
				outputs += 'object file : %s%s%s%s'% ( E_TAG_COLOR_RED, readmd5, E_TAG_COLOR_END, NEW_LINE )
				outputs += 'source file : %s%s'% ( xmlmd5, NEW_LINE )

				self.setProperty( 'ShellDescription', outputs )
				RemoveDirectory( tempFile )

		else :
			ret = retval

		percent = 100
		statusLabel = desc1
		if not ret :
			percent = 0
			statusLabel = MR_LANG( 'Failed' )
			ret = False
			self.mCheckSumError = True
			if self.mStatusCancel :
				self.mFinish = E_RESULT_ERROR_CANCEL

			LOG_TRACE( '---------fail to md5sum' )

		self.DrawProgress( percent, statusLabel )
		time.sleep( 1 )

		LOG_TRACE( '---------md5sum ret[%s]'% ret )
		return ret


	def DoCommandRunShell( self ) :
		LOG_TRACE( '----------------cancel[%s]'% self.mStatusCancel )
		if self.mStatusCancel :
			return

		self.mReturnShell = E_RESULT_UPDATE_DONE
		self.mRunShell = True
		self.mRunShellThread = None

		RemoveDirectory( E_COMMAND_SHELL_LOG )
		RemoveDirectory( E_COMMAND_SHELL_STOP )
		RemoveDirectory( E_COMMAND_SHELL_CANCEL )
		RemoveDirectory( E_COMMAND_SHELL_STATUS )
		RemoveDirectory( E_COMMAND_SHELL_COMPLETE )
		os.system( 'sync' )

		scriptShell = '%s/%s'% ( self.mBaseDirectory, self.mPVSData.mShellScript.mScriptFileName )
		firmware = self.mPVSData.mFileName
		LOG_TRACE( '--------shell[%s] fw[%s]'% ( scriptShell, firmware ) )
		if scriptShell :
			thread = threading.Timer( 0.1, self.UpdateStepRunShell, [ scriptShell, firmware ] )
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
			self.mReturnShell = E_RESULT_ERROR_FAIL
			self.mRunShell = False
			LOG_TRACE( '------------shell script none[%s]'% scriptShell )


		#last usb check
		if self.mUSBmode :
			self.mUSBAttached = self.mDataCache.GetUSBAttached( )
			tempFile = '%s/%s'% ( self.mBaseDirectory, self.mPVSData.mFileName )
			isExist = CheckDirectory( tempFile )
			if ( not self.mUSBAttached ) or ( not isExist ) :
				self.mReturnShell = E_RESULT_ERROR_FAIL
				LOG_TRACE( '---------------update fail, usb deteched[%s] isExist[%s] file[%s]'% ( self.mUSBAttached, isExist, tempFile ) )


		percent = 100
		statusLabel = MR_LANG( 'Completed' )
		if self.mReturnShell < E_RESULT_UPDATE_DONE :
			percent = 0
			if self.mReturnShell == E_RESULT_ERROR_FAIL :
				LOG_TRACE( '--------shell failed' )
				statusLabel = MR_LANG( 'Failed' )
			elif self.mReturnShell == E_RESULT_ERROR_CANCEL :
				LOG_TRACE( '--------shell cancelled' )
				statusLabel = MR_LANG( 'Aborted' )
			else :
				LOG_TRACE( '--------unknown fail' )
				statusLabel = MR_LANG( 'Failed' )

			self.mRunShell = False

		self.DrawProgress( percent, statusLabel )
		self.mFinish = self.mReturnShell
		time.sleep( 1 )


	def UpdateStepRunShell( self, aScript, aFirmware ) :
		cmd = '%s start %s'% ( aScript, aFirmware )
		LOG_TRACE( '---------------run shell[%s]'% cmd )
		os.system( cmd )


	def UpdateStepShellStatus( self ) :
		waitTime = 0
		while waitTime < 5 :
			if CheckDirectory( E_COMMAND_SHELL_LOG ) :
				break

			waitTime += 1
			time.sleep( 1 )

		if not CheckDirectory( E_COMMAND_SHELL_LOG ) :
			self.mRunShell = False
			self.mReturnShell = E_RESULT_ERROR_FAIL
			LOG_TRACE( '---------------file not found [%s]'% E_COMMAND_SHELL_LOG )
			time.sleep( 1 )
			return

		fp = None
		try :
			fp = open( E_COMMAND_SHELL_LOG )
		except Exception, e :
			LOG_ERR( 'Exception[%s]'% e )
			fp = None

		if fp == None :
			self.mRunShell = False
			self.mReturnShell = E_RESULT_ERROR_FAIL
			return

		LINEMAX = ( self.mCtrlTextbox.getHeight( ) - 20 ) / 20
		outputs = ''
		testline = []
		self.mResultOutputs = ''

		fp.seek( 0, 2 )            # go to END
		while self.mRunShellThread :
			isAdd = False
			if CheckDirectory( E_COMMAND_SHELL_COMPLETE ) :
				LOG_TRACE( '-------------------done complete' )
				self.mReturnShell = E_RESULT_UPDATE_DONE
				break

			if CheckDirectory( E_COMMAND_SHELL_STOP ) :
				LOG_TRACE( '-------------------stop' )
				self.mReturnShell = E_RESULT_ERROR_FAIL
				break

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
					self.mResultOutputs = copy.deepcopy( outputs )
					self.setProperty( 'ShellDescription', outputs )

			else :
				time.sleep( 0.5 )

		fp.close( )
		self.mRunShell = False


	def UpdateStepShellProgress( self ) :
		title = MR_LANG( 'Installation in progress' )

		curr = 0.0
		while self.mRunShell :
			isAdd = False
			if CheckDirectory( E_COMMAND_SHELL_STOP ) :
				LOG_TRACE( '-------------------stop' )
				self.mReturnShell = E_RESULT_ERROR_FAIL
				break

			if CheckDirectory( E_COMMAND_SHELL_STATUS ) :
				percent = GetFileRead( E_COMMAND_SHELL_STATUS )
				RemoveDirectory( E_COMMAND_SHELL_STATUS )
				if percent and percent.isdigit( ) :
					self.DrawProgress( int( percent ), title )
					curr = float( percent )

			else :
				curr += 0.25
				if curr > 95 :
					curr = 95
				self.DrawProgress( int( curr ), title )
				if curr % 0.5 == 0 :
					isAdd = True
					self.mResultOutputs += '.'
					self.setProperty( 'ShellDescription', self.mResultOutputs )

			time.sleep( 0.5 )

		self.mRunShell = False


	@RunThread
	def UpdateStepShellCancel( self ) :
		LOG_TRACE( '--------------abort(shell)' )
		self.mStatusCancel = True
		CreateFile( E_COMMAND_SHELL_CANCEL )
		self.mFinish        = E_RESULT_ERROR_CANCEL
		self.mReturnShell   = E_RESULT_ERROR_CANCEL
		self.mRunShell      = False

		if self.mCheckFirmware :
			self.mCheckFirmware = False
			time.sleep( 1 )
			self.mCheckFirmware = True

		self.TimeoutProgress( 60, MR_LANG( 'Aborting' ) )
		LOG_TRACE( '--------------abort(shell) runThread[%s]'% self.mRunShellThread )

		self.mRunShellThread = None
		self.mCheckFirmware = False

		#self.Close( )


	@RunThread
	def AsyncShowAlarm( self, aMessage ) :
		self.mShowBlink = True
		self.setProperty( 'ShowStatusLabel', '%s'% aMessage )

		loopCount = 0
		while loopCount <= 2 :
			#if self.mWinId != xbmcgui.getCurrentWindowDialogId( ) :
			#	break

			self.setProperty( 'StatusLabel', 'True' )
			time.sleep( 0.2 )
			self.setProperty( 'StatusLabel', 'False' )
			time.sleep( 0.2 )
			loopCount += 0.4

		self.setProperty( 'StatusLabel', 'False' )
		self.setProperty( 'StatusLabel', '' )

		self.mShowBlink = False



