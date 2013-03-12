from pvr.gui.WindowImport import *
from subprocess import *
import re


#for test
import sys
import os
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson 

E_VERSION						=	0
E_HDD							=	1

E_SYSTEM_INFO_BASE_ID			=  WinMgr.WIN_ID_SYSTEM_INFO * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 

GROUP_ID_MAIN					=	E_SYSTEM_INFO_BASE_ID + 3000

LABEL_ID_PRODUCT_NAME			=	E_SYSTEM_INFO_BASE_ID + 2500
LABEL_ID_PRODUCT_NUMBER			=	E_SYSTEM_INFO_BASE_ID + 2501
LABEL_ID_HARDWARE_VERSION		=	E_SYSTEM_INFO_BASE_ID + 2502
LABEL_ID_SOFTWARE_VERSION		=	E_SYSTEM_INFO_BASE_ID + 2503
LABEL_ID_BOOTLOADER_VERSION		=	E_SYSTEM_INFO_BASE_ID + 2504

LABEL_ID_HDD_NAME				=	E_SYSTEM_INFO_BASE_ID + 2600
LABEL_ID_HDD_SIZE_MEDIA			=	E_SYSTEM_INFO_BASE_ID + 2602
LABEL_ID_HDD_SIZE_PROGRAM		=	E_SYSTEM_INFO_BASE_ID + 2603
LABEL_ID_HDD_SIZE_RECORD		=	E_SYSTEM_INFO_BASE_ID + 2604
LABEL_ID_HDD_TEMEPERATURE		=	E_SYSTEM_INFO_BASE_ID + 2605

PROGRESS_ID_HDD_SIZE_MEDIA		=	E_SYSTEM_INFO_BASE_ID + 2702
PROGRESS_ID_HDD_SIZE_PROGRAM	=	E_SYSTEM_INFO_BASE_ID + 2703
PROGRESS_ID_HDD_SIZE_RECORD		=	E_SYSTEM_INFO_BASE_ID + 2704


E_SYSTEM_INFO_SUBMENU_LIST_ID	=   E_SYSTEM_INFO_BASE_ID + 9000
E_SYSTEM_INFO_DEFAULT_FOCUS_ID	=   E_SYSTEM_INFO_SUBMENU_LIST_ID



TIME_SEC_CHECK_HDD_TEMP			=	0.05





class SystemInfo( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		self.mCtrlLeftGroup 			= None

		self.mCtrlVersionProductName	= None
		self.mCtrlVersionProductNumber	= None
		self.mCtrlVersionHardware		= None
		self.mCtrlVersionSoftware		= None
		self.mCtrlVersionBootloader		= None

		self.mCtrlHDDName				= None
		self.mCtrlHDDSizeMedia			= None
		self.mCtrlHDDSizeProgram		= None
		self.mCtrlHDDSizeRecord			= None
		self.mCtrlHDDTemperature		= None

		self.mCtrlProgressMedia			= None
		self.mCtrlProgressProgram		= None
		self.mCtrlProgressRecord		= None
		
		self.mGroupItems 				= []
		self.mCheckHddTempTimer			= None
		self.mLastFocused 				= E_SYSTEM_INFO_SUBMENU_LIST_ID
		self.mPrevListItemID 			= 0
		self.mEnableLocalThread 		= True

		self.mCheckHiddenPattern1		= False
		self.mCheckHiddenPattern2		= False
		self.mCheckHiddenPattern3		= False

		self.mLastDateFile 				= None


	def onInit( self )  :
		self.setFocusId( E_SYSTEM_INFO_DEFAULT_FOCUS_ID )		
		self.SetActivate( True )
		self.SetFrontdisplayMessage( 'System Info' )		
		self.mWinId = xbmcgui.getCurrentWindowId( )

		self.SetSingleWindowPosition( E_SYSTEM_INFO_BASE_ID )

		self.mGroupItems = []

		self.mGroupItems.append( xbmcgui.ListItem( MR_LANG( 'Version' ) ) )
		self.mGroupItems.append( xbmcgui.ListItem( MR_LANG( 'HDD' ) ) )

		#self.getControl( E_SETTING_MINI_TITLE ).setLabel( MR_LANG( 'STB Information' ) )

		self.mCtrlLeftGroup = self.getControl( E_SYSTEM_INFO_SUBMENU_LIST_ID )
		self.mCtrlLeftGroup.addItems( self.mGroupItems )

		self.mCtrlVersionProductName	= self.getControl( LABEL_ID_PRODUCT_NAME )
		self.mCtrlVersionProductNumber	= self.getControl( LABEL_ID_PRODUCT_NUMBER )
		self.mCtrlVersionHardware		= self.getControl( LABEL_ID_HARDWARE_VERSION )
		self.mCtrlVersionSoftware		= self.getControl( LABEL_ID_SOFTWARE_VERSION )
		self.mCtrlVersionBootloader		= self.getControl( LABEL_ID_BOOTLOADER_VERSION )

		self.mCtrlHDDName				= self.getControl( LABEL_ID_HDD_NAME )
		self.mCtrlHDDSizeMedia			= self.getControl( LABEL_ID_HDD_SIZE_MEDIA )
		self.mCtrlHDDSizeProgram		= self.getControl( LABEL_ID_HDD_SIZE_PROGRAM )
		self.mCtrlHDDSizeRecord			= self.getControl( LABEL_ID_HDD_SIZE_RECORD )
		self.mCtrlHDDTemperature		= self.getControl( LABEL_ID_HDD_TEMEPERATURE )

		self.mCtrlProgressMedia			= self.getControl( PROGRESS_ID_HDD_SIZE_MEDIA )
		self.mCtrlProgressProgram		= self.getControl( PROGRESS_ID_HDD_SIZE_PROGRAM )
		self.mCtrlProgressRecord		= self.getControl( PROGRESS_ID_HDD_SIZE_RECORD )

		position = self.mCtrlLeftGroup.getSelectedPosition( )
		self.mCtrlLeftGroup.selectItem( position )
		
		self.StartCheckHddTempTimer( )
		self.SetListControl( )
		self.mPrevListItemID = -1
		self.mInitialized = True


	def onAction( self, aAction ) :
		if self.IsActivate( ) == False  :
			return
	
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		if self.GlobalAction( actionId ) :
			return

		self.CheckHiddenAction( actionId )
		if actionId == Action.ACTION_PREVIOUS_MENU or actionId == Action.ACTION_PARENT_DIR :
			self.OpenBusyDialog( )
			self.mInitialized = False
			self.StopCheckHddTempTimer( )
			self.CloseBusyDialog( )
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_MOVE_UP :
			if focusId == E_SYSTEM_INFO_SUBMENU_LIST_ID and self.mCtrlLeftGroup.getSelectedPosition( ) != self.mPrevListItemID :
				self.mPrevListItemID = self.mCtrlLeftGroup.getSelectedPosition( )
				self.SetListControl( )

		elif actionId == Action.ACTION_MOVE_DOWN :
			if focusId == E_SYSTEM_INFO_SUBMENU_LIST_ID and self.mCtrlLeftGroup.getSelectedPosition( ) != self.mPrevListItemID :
				self.mPrevListItemID = self.mCtrlLeftGroup.getSelectedPosition( )
				self.SetListControl( )


	def CheckHiddenAction( self, aAction ) :
		if aAction == Action.ACTION_MOVE_LEFT :
			if self.mCheckHiddenPattern1 == True :
				self.mCheckHiddenPattern2 = True
			self.mCheckHiddenPattern1 = True
		elif aAction == Action.ACTION_MOVE_RIGHT and self.mCheckHiddenPattern2 :
			if self.mCheckHiddenPattern3 == True :
				self.mCheckHiddenPattern1	= False
				self.mCheckHiddenPattern2	= False
				self.mCheckHiddenPattern3	= False
				self.StopCheckHddTempTimer( )
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_HIDDEN_TEST, WinMgr.WIN_ID_NULLWINDOW )
				return
			self.mCheckHiddenPattern3 = True
		else :
			self.mCheckHiddenPattern1	= False
			self.mCheckHiddenPattern2	= False
			self.mCheckHiddenPattern3	= False


	def onClick( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return


	def onFocus( self, aControlId ) :
		if self.IsActivate( ) == False  :
			return
	
		if self.mInitialized == False :
			return

		"""
		if ( self.mLastFocused != aControlId ) or ( self.mCtrlLeftGroup.getSelectedPosition( ) != self.mPrevListItemID ) :
			if aControlId == E_SYSTEM_INFO_SUBMENU_LIST_ID :
				self.SetListControl( )
				if self.mLastFocused != aControlId :
					self.mLastFocused = aControlId
				if self.mCtrlLeftGroup.getSelectedPosition( ) != self.mPrevListItemID :
					self.mPrevListItemID = self.mCtrlLeftGroup.getSelectedPosition( )
		"""


	def SetListControl( self ) :
		self.ResetAllControl( )
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		self.getControl( GROUP_ID_MAIN ).setVisible( False )

		if selectedId == E_VERSION :
			self.OpenBusyDialog( )

			versionHardware		= MR_LANG( 'Unknown' )
			versionBootloader		= MR_LANG( 'Unknown' )

			version_info = self.mCommander.System_GetVersion( )
			if version_info :
				versionHardware			= version_info.mHwVersion
				versionBootloader		= version_info.mLoadVersion

			visibleControlIds	= [ LABEL_ID_PRODUCT_NAME, LABEL_ID_PRODUCT_NUMBER, LABEL_ID_HARDWARE_VERSION, LABEL_ID_SOFTWARE_VERSION, LABEL_ID_BOOTLOADER_VERSION ]
			hideControlIds		= [ LABEL_ID_HDD_NAME, LABEL_ID_HDD_SIZE_MEDIA, LABEL_ID_HDD_SIZE_PROGRAM, LABEL_ID_HDD_SIZE_RECORD, LABEL_ID_HDD_TEMEPERATURE ]
			for i in range( len( hideControlIds ) ) :
				self.SetVisibleControl( hideControlIds[i], False )
			for i in range( len( visibleControlIds ) ) :
				self.SetVisibleControl( visibleControlIds[i], True )

			self.mCtrlVersionProductName.setLabel(		MR_LANG( 'Product Name : %s' ) % self.GetProductName( ) )
			self.mCtrlVersionProductNumber.setLabel(	MR_LANG( 'Product Number : %s' ) % self.GetProductNymber( ) )
			self.mCtrlVersionHardware.setLabel( 		MR_LANG( 'Hardware Version : %s' ) % versionHardware )
			self.mCtrlVersionSoftware.setLabel(			MR_LANG( 'Release Version : %s' ) % self.GetReleaseVersion( ) )
			self.mCtrlVersionBootloader.setLabel(		MR_LANG( 'Bootloader Version : %s' ) % versionBootloader )

			self.CloseBusyDialog( )

		elif selectedId == E_HDD :
			self.OpenBusyDialog( )

			visibleControlIds	= [ LABEL_ID_HDD_NAME, LABEL_ID_HDD_SIZE_MEDIA, LABEL_ID_HDD_SIZE_PROGRAM, LABEL_ID_HDD_SIZE_RECORD, LABEL_ID_HDD_TEMEPERATURE ]
			hideControlIds		= [ LABEL_ID_PRODUCT_NAME, LABEL_ID_PRODUCT_NUMBER, LABEL_ID_HARDWARE_VERSION, LABEL_ID_SOFTWARE_VERSION, LABEL_ID_BOOTLOADER_VERSION ]
			for i in range( len( hideControlIds ) ) :
				self.SetVisibleControl( hideControlIds[i], False )
			for i in range( len( visibleControlIds ) ) :
				self.SetVisibleControl( visibleControlIds[i], True )

			if self.CheckExistsDisk( ) :
				self.mCtrlHDDName.setLabel(	MR_LANG( 'Name and Total Size : %s ( %s )' ) % ( self.GetHDDName( ), self.GetTotalSize( ) ) )
				self.mCtrlHDDTemperature.setLabel( MR_LANG( 'Temperature : Busy' ) )

				total_size, used_size, percent = self.GetPartitionSize( 'sda5' )
				self.mCtrlProgressMedia.setPercent( percent )
				self.mCtrlHDDSizeMedia.setLabel( MR_LANG( 'Media Partition Usage : %s%% ( %s / %s )' ) % ( percent, used_size, total_size ) )

				total_size, used_size, percent = self.GetPartitionSize( 'sda3' )
				self.mCtrlProgressProgram.setPercent( percent )
				self.mCtrlHDDSizeProgram.setLabel( MR_LANG( 'Program Partition Usage : %s%% ( %s / %s )' ) % ( percent, used_size, total_size ) )
				
				total_size, used_size, percent = self.GetRecordFreeSize( )
				self.mCtrlProgressRecord.setPercent( percent )
				self.mCtrlHDDSizeRecord.setLabel( MR_LANG( 'Recording Partition Usage : %s%% ( %s / %s )' ) % ( percent, used_size, total_size ) )
			else :
				self.mCtrlHDDName.setLabel( MR_LANG( 'Name and Total Size : Unknown' ) )
				self.mCtrlHDDSizeMedia.setLabel( MR_LANG( 'Media Partition Usage : Unknown' ) )
				self.mCtrlHDDSizeProgram.setLabel( MR_LANG( 'Program Partition Usage : Unknown' ) )
				self.mCtrlHDDSizeRecord.setLabel( MR_LANG( 'Recording Partition Usage : Unknown' ) )
				self.mCtrlProgressMedia.setPercent( 0 )
				self.mCtrlProgressProgram.setPercent( 0 )
				self.mCtrlProgressRecord.setPercent( 0 )
				
			self.CloseBusyDialog( )

		self.getControl( GROUP_ID_MAIN ).setVisible( True )


	def GetProductName( self ) :
		return 'PRISMCUBE RUBY'


	def GetProductNymber( self ) :
		return '00ASV3824ASDMARUSYS322'


	def GetHardwareVersion( self ) :
		return '1.00'


	def GetBootloaderVersion( self ) :
		return '1.00'


	def GetReleaseVersion( self ) :
		ret = GetCurrentVersion( )
		if not ret[0] :
			ret[0] = MR_LANG( 'Unknown' )
			return ret[0]
		if not ret[1] :
			ret[1] = MR_LANG( 'Unknown' )

		retInfo = ret[0] + ' ( %s )' % ret[1]
		return retInfo


	def RunningGetLastDate( self, aDirname ) :
		flist = os.listdir( aDirname )
		for f in flist:
			next = os.path.join( aDirname, f )
			if os.path.isdir( next ) :
				self.RunningGetLastDate( next )
			else :
				ext = os.path.splitext( next )[-1]
				lastdate = 0
				if ext == '.py' or ext == '.xml' :
					self.SetLastDate( next )


	def SetLastDate( self, aFile ) :
		if self.mLastDateFile == None :
			self.mLastDateFile = aFile
		last = int( time.strftime( '%y%m%d', time.localtime( os.stat( self.mLastDateFile ).st_mtime ) ) )
		current = int( time.strftime( '%y%m%d', time.localtime( os.stat( aFile ).st_mtime ) ) )
		
		if last < current :
			self.mLastDateFile = aFile


	def GetLastDate( self ) :
		if os.path.exists( xbmcaddon.Addon( 'script.mbox' ).getAddonInfo( 'path' ) ) == False :
			return ' '
		else :
			self.RunningGetLastDate( xbmcaddon.Addon( 'script.mbox' ).getAddonInfo( 'path' ) )
			return ' ( Last modified ' + time.strftime( '%y.%m.%d', time.localtime( os.stat( self.mLastDateFile ).st_mtime ) ) + ' )'


	def GetPartitionSize( self, aName ) :
		total_size = MR_LANG( 'Unknown' )
		used_size = MR_LANG( 'Unknown' )
		percent = MR_LANG( 'Unknown' )
		try :
			cmd = "df -h | awk '/%s/ {print $2}'" % aName
			if sys.version_info < ( 2, 7 ) :
				p = Popen( cmd, shell=True, stdout=PIPE )
				total_size = p.stdout.read( ).strip( )
				p.stdout.close( )
			else :
				p = Popen( cmd, shell=True, stdout=PIPE, close_fds=True )
				( total_size, err ) = p.communicate( )
				total_size = total_size.strip( )
			total_size = total_size.split( '\n' )
			total_size = total_size[0]

			cmd = "df -h | awk '/%s/ {print $3}'" % aName
			if sys.version_info < ( 2, 7 ) :
				p = Popen( cmd, shell=True, stdout=PIPE )
				used_size = p.stdout.read( ).strip( )
				p.stdout.close( )
			else :
				p = Popen( cmd, shell=True, stdout=PIPE, close_fds=True )
				( used_size, err ) = p.communicate( )
				used_size = used_size.strip( )
			used_size = used_size.split( '\n' )
			used_size = used_size[0]
			
			cmd = "df -h | awk '/%s/ {print $5}'" % aName
			if sys.version_info < ( 2, 7 ) :
				p = Popen( cmd, shell=True, stdout=PIPE )
				percent = p.stdout.read( ).strip( )
				p.stdout.close( )
			else :
				p = Popen( cmd, shell=True, stdout=PIPE, close_fds=True )
				( percent, err ) = p.communicate( )
				percent = percent.strip( )
			percent = percent.split( '\n' )
			percent = percent[0]
			percent = int( re.sub( '%', '', percent ) )

			return total_size, used_size, percent

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return MR_LANG( 'Unknown' ), MR_LANG( 'Unknown' ), MR_LANG( 'Unknown' )


	def GetRecordFreeSize( self ) :
		total_size = MR_LANG( 'Unknown' )
		used_size = MR_LANG( 'Unknown' )
		percent = MR_LANG( 'Unknown' )
		try :
			if self.mCommander.Record_GetPartitionSize( ) != -1 and self.mCommander.Record_GetFreeMBSize( ) != -1 :
				total_size	= self.mCommander.Record_GetPartitionSize( )
				used_size	= total_size - self.mCommander.Record_GetFreeMBSize( )
				percent		= int( used_size / float( total_size ) * 100 )
				if used_size >= 1024 :
					used_size	= '%sG' % int( used_size / float( 1024 ) )
				else :
					used_size	= '%sM' % used_size
				if total_size >= 1024 :
					total_size = '%sG' % int( total_size / float( 1024 ) )
				else :
					total_size	= '%sM' % total_size
			else :
				LOG_ERR( 'Get Record_GetPartitionSize or Record_GetFreeMBSize Fail!!!' )

			return total_size, used_size, percent

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return MR_LANG( 'Unknown' ), MR_LANG( 'Unknown' ), MR_LANG( 'Unknown' )


	def GetHDDName( self ) :
		model = MR_LANG( 'Unknown' )
		try :
			if os.path.exists( '/sys/block/sda/device/model' ) :
				openFile = open( '/sys/block/sda/device/model', 'r' )
				inputline = openFile.readlines( )
				model = inputline[0]
				model = model.strip( )
			else :
				device = '/dev/sda'
				cmd = "hddtemp %s -D | awk '/Model:/ {print $2}'" % device
				if sys.version_info < ( 2, 7 ) :
					p = Popen( cmd, shell=True, stdout=PIPE )
					model = p.stdout.read( ).strip( )
					p.stdout.close( )
				else :
					p = Popen( cmd, shell=True, stdout=PIPE, close_fds=True )
					( model, err ) = p.communicate( )
					model = model.strip( )

			return model

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return model


	def GetTotalSize( self ) :
		size = MR_LANG( 'Unknown' )
		unit = ''
		device = '/dev/sda'
		cmd = "fdisk -ul %s | awk '/Disk/ {print $3,$4}'" % device
		if sys.version_info < ( 2, 7 ) :
			p = Popen( cmd, shell=True, stdout=PIPE )
			size = p.stdout.read( ).strip( )
			p.stdout.close( )
		else :
			p = Popen( cmd, shell=True, stdout=PIPE, close_fds=True )
			( size, err ) = p.communicate( )
			size = size.strip( )

		size = re.sub( ',', '', size )
		return size


	def ShowHDDTemperature( self ) :
		temperature = MR_LANG( 'Unknown' )
		device = '/dev/sda'
		cmd = 'hddtemp %s -n -q' % device

		if self.mCtrlLeftGroup.getSelectedPosition( ) == E_HDD :
			if self.CheckExistsDisk( ) :
				if sys.version_info < ( 2, 7 ) :
					p = Popen( cmd, shell=True, stdout=PIPE )
					temperature = p.stdout.read( ).strip( )
					p.stdout.close( )
				else :
					p = Popen( cmd, shell=True, stdout=PIPE, close_fds=True )
					( temperature, err ) = p.communicate( )
					temperature = temperature.strip( )

				if IsNumber( temperature ) == False :
					temperature = MR_LANG( 'Unknown' )
				LOG_TRACE( 'HDD Temperature = %s' % temperature )
			else :
				temperature = MR_LANG( 'Unknown' )
			self.mCtrlHDDTemperature.setLabel( MR_LANG( 'Temperature : %s degree celsius' ) % temperature )


	def CheckExistsDisk( self ) :
		if not self.mPlatform.IsPrismCube( ) :
			return False

		cmd = 'df'
		if sys.version_info < ( 2, 7 ) :
			p = Popen( cmd, shell=True, stdout=PIPE )
			parsing = p.stdout.read( ).strip( )
			p.stdout.close( )
		else :
			p = Popen( cmd, shell=True, stdout=PIPE, close_fds=True )
			( parsing, err ) = p.communicate( )
			parsing = parsing.strip( )

		if parsing.count( '/dev/sda' ) >= 3 :
			return True
		else :
			return False


	def StartCheckHddTempTimer( self ) :
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Start' )	
		self.mEnableLocalThread = True
		self.mCheckHddTempTimer = self.AsyncCheckHddTempTimer( )
	

	def StopCheckHddTempTimer( self ) :
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Stop' )
		self.mEnableLocalThread = False				
		self.mCheckHddTempTimer.join( )


	@RunThread
	def AsyncCheckHddTempTimer( self ) :
		count = 0
		while self.mEnableLocalThread :
			if self.mCtrlLeftGroup.getSelectedPosition( ) == E_HDD :
				if ( count % 60 ) == 0 :	# 3 secs
					self.ShowHDDTemperature( )
			count = count + 1
			time.sleep( TIME_SEC_CHECK_HDD_TEMP )

