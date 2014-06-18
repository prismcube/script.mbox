from pvr.gui.WindowImport import *
from subprocess import *
import re
from uuid import getnode as get_mac


#for test
import sys
import os
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson 

E_SYSTEM						=	0
E_VERSION						=	1
E_HDD							=	2

E_SYSTEM_INFO_BASE_ID			=  WinMgr.WIN_ID_SYSTEM_INFO * E_BASE_WINDOW_UNIT + E_BASE_WINDOW_ID 

GROUP_ID_MAIN					=	E_SYSTEM_INFO_BASE_ID + 3000

LABEL_ID_PRODUCT_NAME			=	E_SYSTEM_INFO_BASE_ID + 2500
LABEL_ID_SERIAL_NUMBER			=	E_SYSTEM_INFO_BASE_ID + 2501
LABEL_ID_MAC_ADDRESS			=	E_SYSTEM_INFO_BASE_ID + 2801

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

		self.mCtrlSystemProductName		= None
		self.mCtrlSystemSerialNumber	= None
		self.mCtrlSystemMacAddress		= None

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
		self.SetFrontdisplayMessage( MR_LANG('System Info') )		
		self.mWinId = xbmcgui.getCurrentWindowId( )

		self.SetSingleWindowPosition( E_SYSTEM_INFO_BASE_ID )

		self.mGroupItems = []

		self.mGroupItems.append( xbmcgui.ListItem( MR_LANG( 'System' ) ) )
		self.mGroupItems.append( xbmcgui.ListItem( MR_LANG( 'Version' ) ) )
		if self.mPlatform.GetProduct( ) != PRODUCT_OSCAR :
			self.mGroupItems.append( xbmcgui.ListItem( MR_LANG( 'HDD' ) ) )

		self.SetHeaderTitle( MR_LANG( 'STB Information' ) )

		self.mCtrlLeftGroup = self.getControl( E_SYSTEM_INFO_SUBMENU_LIST_ID )
		self.mCtrlLeftGroup.addItems( self.mGroupItems )

		self.mCtrlSystemProductName		= self.getControl( LABEL_ID_PRODUCT_NAME )
		self.mCtrlSystemSerialNumber	= self.getControl( LABEL_ID_SERIAL_NUMBER )
		self.mCtrlSystemMacAddress		= self.getControl( LABEL_ID_MAC_ADDRESS )

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

		elif actionId == Action.ACTION_MOVE_UP or actionId == Action.ACTION_PAGE_UP :
			if focusId == E_SYSTEM_INFO_SUBMENU_LIST_ID and self.mCtrlLeftGroup.getSelectedPosition( ) != self.mPrevListItemID :
				self.mPrevListItemID = self.mCtrlLeftGroup.getSelectedPosition( )
				self.SetListControl( )

		elif actionId == Action.ACTION_MOVE_DOWN or actionId == Action.ACTION_PAGE_DOWN :
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


	def SetListControl( self ) :
		self.ResetAllControl( )
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		self.getControl( GROUP_ID_MAIN ).setVisible( False )

		if selectedId == E_SYSTEM :
			self.OpenBusyDialog( )
			self.StopCheckHddTempTimer( )

			visibleControlIds	= [ LABEL_ID_PRODUCT_NAME, LABEL_ID_SERIAL_NUMBER, LABEL_ID_MAC_ADDRESS ]
			hideControlIds		= [ LABEL_ID_HARDWARE_VERSION, LABEL_ID_SOFTWARE_VERSION, LABEL_ID_BOOTLOADER_VERSION, LABEL_ID_HDD_NAME, LABEL_ID_HDD_SIZE_MEDIA, LABEL_ID_HDD_SIZE_PROGRAM, LABEL_ID_HDD_SIZE_RECORD, LABEL_ID_HDD_TEMEPERATURE ]
			for i in range( len( hideControlIds ) ) :
				self.SetVisibleControl( hideControlIds[i], False )
			for i in range( len( visibleControlIds ) ) :
				self.SetVisibleControl( visibleControlIds[i], True )

			self.mCtrlSystemProductName.setLabel(   '%s : %s'% ( MR_LANG( 'Product Name' ), self.GetProductName( ) ) )
			self.mCtrlSystemSerialNumber.setLabel( '%s : %s'% ( MR_LANG( 'Serial Number' ) , self.GetSerialNymber( ) ) )
			self.mCtrlSystemMacAddress.setLabel( '%s : %s'% ( MR_LANG( 'Ethernet MAC Address' ) , self.GetMacAddress( ) ) )

			self.CloseBusyDialog( )

		elif selectedId == E_VERSION :
			self.OpenBusyDialog( )
			self.StopCheckHddTempTimer( )

			versionHardware   = MR_LANG( 'Unknown' )
			versionBootloader = MR_LANG( 'Unknown' )

			version_info = self.mCommander.System_GetVersion( )
			if version_info :
				versionHardware   = '1.0.%s' % version_info.mHwVersion
				tmp = '%02d' % version_info.mLoadVersion
				versionBootloader = '1.%s.%s' % ( tmp[0], tmp[1] )

			visibleControlIds	= [ LABEL_ID_HARDWARE_VERSION, LABEL_ID_SOFTWARE_VERSION, LABEL_ID_BOOTLOADER_VERSION ]
			hideControlIds		= [ LABEL_ID_PRODUCT_NAME, LABEL_ID_SERIAL_NUMBER, LABEL_ID_MAC_ADDRESS, LABEL_ID_HDD_NAME, LABEL_ID_HDD_SIZE_MEDIA, LABEL_ID_HDD_SIZE_PROGRAM, LABEL_ID_HDD_SIZE_RECORD, LABEL_ID_HDD_TEMEPERATURE ]
			for i in range( len( hideControlIds ) ) :
				self.SetVisibleControl( hideControlIds[i], False )
			for i in range( len( visibleControlIds ) ) :
				self.SetVisibleControl( visibleControlIds[i], True )
			 
			self.mCtrlVersionHardware.setLabel(      '%s : %s'% ( MR_LANG( 'Hardware Version' ) , versionHardware ) )
			self.mCtrlVersionSoftware.setLabel(      '%s : %s'% ( MR_LANG( 'Release Version' ) , self.GetReleaseVersion( ) ) )
			self.mCtrlVersionBootloader.setLabel(    '%s : %s'% ( MR_LANG( 'Bootloader Version' ) , versionBootloader ) )

			self.CloseBusyDialog( )

		elif selectedId == E_HDD :
			self.OpenBusyDialog( )
			visibleControlIds	= [ LABEL_ID_HDD_NAME, LABEL_ID_HDD_SIZE_MEDIA, LABEL_ID_HDD_SIZE_PROGRAM, LABEL_ID_HDD_SIZE_RECORD, LABEL_ID_HDD_TEMEPERATURE ]
			hideControlIds		= [ LABEL_ID_PRODUCT_NAME, LABEL_ID_SERIAL_NUMBER, LABEL_ID_MAC_ADDRESS, LABEL_ID_HARDWARE_VERSION, LABEL_ID_SOFTWARE_VERSION, LABEL_ID_BOOTLOADER_VERSION ]
			for i in range( len( hideControlIds ) ) :
				self.SetVisibleControl( hideControlIds[i], False )
			for i in range( len( visibleControlIds ) ) :
				self.SetVisibleControl( visibleControlIds[i], True )

			if CheckHdd( ) :
				self.StartCheckHddTempTimer( )
				self.mCtrlHDDName.setLabel(	'%s : %s ( %s )'% ( MR_LANG( 'Model' ), self.GetHDDName( ), self.GetTotalSize( ) ) )
				self.mCtrlHDDTemperature.setLabel( MR_LANG( 'Temperature : Busy' ) )
				total_size, used_size, percent = self.GetPartitionSize( 'sda5' )
				self.mCtrlProgressMedia.setPercent( percent )
				self.mCtrlHDDSizeMedia.setLabel( '%s : %s%% ( %s / %s )'% ( MR_LANG( 'Media Partition Usage' ), percent, used_size, total_size ) )
				total_size, used_size, percent = self.GetPartitionSize( 'sda3' )
				self.mCtrlProgressProgram.setPercent( percent )
				self.mCtrlHDDSizeProgram.setLabel( '%s : %s%% ( %s / %s )'% ( MR_LANG( 'Program Partition Usage' ), percent, used_size, total_size ) )
				total_size, used_size, percent = self.GetRecordFreeSize( )
				self.mCtrlProgressRecord.setPercent( percent )
				self.mCtrlHDDSizeRecord.setLabel( '%s : %s%% ( %s / %s )'% ( MR_LANG( 'Recording Partition Usage' ), percent, used_size, total_size ) )
			else :
				self.mCtrlHDDName.setLabel( '%s : %s'% ( MR_LANG( 'Model'), MR_LANG( 'Unknown' ) ) )
				self.mCtrlHDDTemperature.setLabel( '%s : %s'% ( MR_LANG( 'Temperature'), MR_LANG( 'Unknown' ) ) )
				self.mCtrlHDDSizeMedia.setLabel( '%s : %s'% ( MR_LANG( 'Media Partition Usage'), MR_LANG( 'Unknown' ) ) )
				self.mCtrlHDDSizeProgram.setLabel( '%s : %s'% ( MR_LANG( 'Program Partition Usage'), MR_LANG( 'Unknown' ) ) )
				self.mCtrlHDDSizeRecord.setLabel( '%s : %s'% ( MR_LANG( 'Recording Partition Usage'), MR_LANG( 'Unknown' ) ) )
				self.mCtrlProgressMedia.setPercent( 0 )
				self.mCtrlProgressProgram.setPercent( 0 )
				self.mCtrlProgressRecord.setPercent( 0 )
				
			self.CloseBusyDialog( )

		self.getControl( GROUP_ID_MAIN ).setVisible( True )


	def GetProductName( self ) :
		if self.mPlatform.GetProduct( ) == PRODUCT_OSCAR :
			return 'PRISMCUBE JET'
		else :
			return 'PRISMCUBE RUBY'


	def GetSerialNymber( self ) :
		try :
			if ( os.path.exists( '/config/serial' ) ) :
				f = open( '/config/serial', 'r' )
				lines = f.readline( ).strip( )
				f.close( )
				return lines
			else :
				LOG_ERR( 'not exists /config/serial' )
				return MR_LANG( 'Unknown' )
			
		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return MR_LANG( 'Unknown' )


	def GetReleaseVersion( self ) :
		ret = GetCurrentVersion( )
		if not ret[0] :
			ret[0] = MR_LANG( 'Unknown' )
			return ret[0]
		if not ret[1] :
			ret[1] = MR_LANG( 'Unknown' )

		retInfo = ret[0] + ' ( %s )' % ret[1]
		return retInfo


	def GetMacAddress( self ) :
		try :
			if ( os.path.exists( '/sys/class/net/eth0/address' ) ) :
				f = open( '/sys/class/net/eth0/address', 'rb' )
				data = f.readlines( )
				f.close( )
				if data :
					data = str( data[0] )
					data = data.strip( )
					return data

				return MR_LANG( 'Unknown' )
			else :
				LOG_ERR( 'not exists /sys/class/net/eth0/address' )
				return MR_LANG( 'Unknown' )

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return MR_LANG( 'Unknown' )


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
		defaultSize = MR_LANG( 'Unknown' )
		total_size = defaultSize
		used_size = defaultSize
		percent = defaultSize
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
			return defaultSize, defaultSize, defaultSize


	def GetRecordFreeSize( self ) :
		defaultSize = MR_LANG( 'Unknown' )
		total_size = defaultSize
		used_size = defaultSize
		percent = defaultSize
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
				LOG_ERR( 'Get Record_GetPartitionSize or Record_GetFreeMBSize Failed!!!' )

			return total_size, used_size, percent

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return defaultSize, defaultSize, defaultSize


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
		defaultLang = MR_LANG( 'Unknown' )
		temperature = defaultLang
		device = '/dev/sda'
		cmd = 'hddtemp %s -n -q' % device

		if self.mCtrlLeftGroup.getSelectedPosition( ) == E_HDD :
			if CheckHdd( ) :
				if sys.version_info < ( 2, 7 ) :
					p = Popen( cmd, shell=True, stdout=PIPE )
					temperature = p.stdout.read( ).strip( )
					p.stdout.close( )
				else :
					p = Popen( cmd, shell=True, stdout=PIPE, close_fds=True )
					( temperature, err ) = p.communicate( )
					temperature = temperature.strip( )

				if IsNumber( temperature ) == False :
					temperature = defaultLang
				LOG_TRACE( 'HDD Temperature = %s' % temperature )
			else :
				temperature = defaultLang

			self.mCtrlHDDTemperature.setLabel( '%s : %s %s'% ( MR_LANG( 'Temperature' ), temperature, MR_LANG( 'Degree Celsius' ) ) )


	def StartCheckHddTempTimer( self ) :
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Start' )	
		self.mEnableLocalThread = True
		self.mCheckHddTempTimer = self.AsyncCheckHddTempTimer( )
	

	def StopCheckHddTempTimer( self ) :
		LOG_TRACE( '++++++++++++++++++++++++++++++++++++ Stop' )
		self.mEnableLocalThread = False
		if self.mEnableLocalThread :
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

