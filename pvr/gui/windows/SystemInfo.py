from pvr.gui.WindowImport import *
from pvr.STBVersion import *
from subprocess import *
import re


E_VERSION					=	0
E_HDD						=	1

GROUP_ID_MAIN				=	3000

LABEL_ID_PRODUCT_NAME		=	2500
LABEL_ID_PRODUCT_NUMBER		=	2501
LABEL_ID_HARDWARE_VERSION	=	2502
LABEL_ID_SOFTWARE_VERSION	=	2503
LABEL_ID_BOOTLOADER_VERSION	=	2504

LABEL_ID_HDD_NAME			=	2600
LABEL_ID_HDD_SIZE_MEDIA		=	2602
LABEL_ID_HDD_SIZE_PROGRAM	=	2603
LABEL_ID_HDD_SIZE_RECORD	=	2604
LABEL_ID_HDD_TEMEPERATURE	=	2605

PROGRESS_ID_HDD_SIZE_MEDIA		=	2702
PROGRESS_ID_HDD_SIZE_PROGRAM	=	2703
PROGRESS_ID_HDD_SIZE_RECORD		=	2704


class SystemInfo( SettingWindow ) :
	def __init__( self, *args, **kwargs ) :
		SettingWindow.__init__( self, *args, **kwargs )
		leftGroupItems			= [ MR_LANG( 'Version' ), MR_LANG( 'HDD' ) ]
	
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
		self.mCheckEndThread			= False
		self.mLastFocused 				= E_SUBMENU_LIST_ID
		self.mPrevListItemID 			= 0

		self.mCheckHiddenPattern1	= False
		self.mCheckHiddenPattern2	= False
		self.mCheckHiddenPattern3	= False

		for i in range( len( leftGroupItems ) ) :
			self.mGroupItems.append( xbmcgui.ListItem( leftGroupItems[i] ) )


	def onInit( self )  :
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )

		self.getControl( E_SETTING_MINI_TITLE ).setLabel( MR_LANG( 'STB Information' ) )

		self.mCtrlLeftGroup = self.getControl( E_SUBMENU_LIST_ID )
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
		
		self.mCheckEndThread = True
		self.ShowHDDTemperature( )
		
		self.SetListControl( )
		self.mInitialized = True
		self.mPrevListItemID = -1


	def onAction( self, aAction ) :
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
		self.GlobalAction( actionId )
		self.CheckHiddenAction( actionId )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass

		elif actionId == Action.ACTION_SELECT_ITEM :
			pass

		elif actionId == Action.ACTION_PARENT_DIR :
			self.mInitialized = False
			self.mCheckEndThread = False
			WinMgr.GetInstance( ).CloseWindow( )

		elif actionId == Action.ACTION_MOVE_UP :
			if focusId == E_SUBMENU_LIST_ID and self.mCtrlLeftGroup.getSelectedPosition( ) != self.mPrevListItemID :
				self.mPrevListItemID = self.mCtrlLeftGroup.getSelectedPosition( )
				self.SetListControl( )

		elif actionId == Action.ACTION_MOVE_DOWN :
			if focusId == E_SUBMENU_LIST_ID and self.mCtrlLeftGroup.getSelectedPosition( ) != self.mPrevListItemID :
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
				self.mCheckEndThread = False
				WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_HIDDEN_TEST, WinMgr.WIN_ID_NULLWINDOW )
				return
			self.mCheckHiddenPattern3 = True
		else :
			self.mCheckHiddenPattern1	= False
			self.mCheckHiddenPattern2	= False
			self.mCheckHiddenPattern3	= False


	def onClick( self, aControlId ) :
		pass


	def onFocus( self, aControlId ) :
		if self.mInitialized == False :
			return
		if ( self.mLastFocused != aControlId ) or ( self.mCtrlLeftGroup.getSelectedPosition( ) != self.mPrevListItemID ) :
			if aControlId == E_SUBMENU_LIST_ID :
				self.SetListControl( )
				if self.mLastFocused != aControlId :
					self.mLastFocused = aControlId
				if self.mCtrlLeftGroup.getSelectedPosition( ) != self.mPrevListItemID :
					self.mPrevListItemID = self.mCtrlLeftGroup.getSelectedPosition( )


	def SetListControl( self ) :
		self.ResetAllControl( )
		selectedId = self.mCtrlLeftGroup.getSelectedPosition( )
		self.getControl( GROUP_ID_MAIN ).setVisible( False )

		if selectedId == E_VERSION :
			visibleControlIds	= [ LABEL_ID_PRODUCT_NAME, LABEL_ID_PRODUCT_NUMBER, LABEL_ID_HARDWARE_VERSION, LABEL_ID_SOFTWARE_VERSION, LABEL_ID_BOOTLOADER_VERSION ]
			hideControlIds		= [ LABEL_ID_HDD_NAME, LABEL_ID_HDD_SIZE_MEDIA, LABEL_ID_HDD_SIZE_PROGRAM, LABEL_ID_HDD_SIZE_RECORD, LABEL_ID_HDD_TEMEPERATURE ]
			for i in range( len( hideControlIds ) ) :
				self.SetVisibleControl( hideControlIds[i], False )
			for i in range( len( visibleControlIds ) ) :
				self.SetVisibleControl( visibleControlIds[i], True )			

			self.mCtrlVersionProductName.setLabel(		MR_LANG( 'Product Name : %s' ) % PRODUCT_NAME )
			self.mCtrlVersionProductNumber.setLabel(	MR_LANG( 'Product Number : %s' ) % PRODUCT_NUMBER )
			self.mCtrlVersionHardware.setLabel( 		MR_LANG( 'Hardware Version : %s' ) % HARDWARE_VERSION )
			self.mCtrlVersionSoftware.setLabel(			MR_LANG( 'Software Version : %s' ) % SOFTWARE_VERSION )
			self.mCtrlVersionBootloader.setLabel(		MR_LANG( 'Bootloader Version : %s' ) % BOOTLOADER_VERSION )

		elif selectedId == E_HDD :
			self.OpenBusyDialog( )

			visibleControlIds	= [ LABEL_ID_HDD_NAME, LABEL_ID_HDD_SIZE_MEDIA, LABEL_ID_HDD_SIZE_PROGRAM, LABEL_ID_HDD_SIZE_RECORD, LABEL_ID_HDD_TEMEPERATURE ]
			hideControlIds		= [ LABEL_ID_PRODUCT_NAME, LABEL_ID_PRODUCT_NUMBER, LABEL_ID_HARDWARE_VERSION, LABEL_ID_SOFTWARE_VERSION, LABEL_ID_BOOTLOADER_VERSION ]
			for i in range( len( hideControlIds ) ) :
				self.SetVisibleControl( hideControlIds[i], False )
			for i in range( len( visibleControlIds ) ) :
				self.SetVisibleControl( visibleControlIds[i], True )

			if self.CheckExistsDisk( ) :
				self.mCtrlHDDName.setLabel(	MR_LANG( 'Disk name : %s ( %s )' ) % ( self.GetHDDName( ), self.GetTotalSize( ) ) )

				total_size, used_size, percent = self.GetPartitionSize( 'sda5' )
				self.mCtrlProgressMedia.setPercent( percent )
				self.mCtrlHDDSizeMedia.setLabel( MR_LANG( 'Media usage : %s%% ( %s / %s )' ) % ( percent, used_size, total_size ) )

				total_size, used_size, percent = self.GetPartitionSize( 'sda3' )
				self.mCtrlProgressProgram.setPercent( percent )
				self.mCtrlHDDSizeProgram.setLabel( MR_LANG( 'Program usage : %s%% ( %s / %s )' ) % ( percent, used_size, total_size ) )

				total_size, used_size, percent = self.GetRecordFreeSize( )
				self.mCtrlProgressRecord.setPercent( percent )
				self.mCtrlHDDSizeRecord.setLabel( MR_LANG( 'Recording usage : %s%% ( %s / %s )' ) % ( percent, used_size, total_size ) )
			else :
				self.mCtrlHDDName.setLabel( MR_LANG( 'Disk name : Unknown' ) )
				self.mCtrlHDDSizeMedia.setLabel( MR_LANG( 'Media usage : Unknown' ) )
				self.mCtrlHDDSizeProgram.setLabel( MR_LANG( 'Program usage : Unknown' ) )
				self.mCtrlHDDSizeRecord.setLabel( MR_LANG( 'Recording usage : Unknown' ) )
				self.mCtrlProgressMedia.setPercent( 0 )
				self.mCtrlProgressProgram.setPercent( 0 )
				self.mCtrlProgressRecord.setPercent( 0 )
				
			self.CloseBusyDialog( )

		self.getControl( GROUP_ID_MAIN ).setVisible( True )


	def GetPartitionSize( self, aName ) :
		total_size = MR_LANG( 'Unknown' )
		used_size = MR_LANG( 'Unknown' )
		percent = MR_LANG( 'Unknown' )
		cmd = "df -h | awk '/%s/ {print $2}'" % aName
		total_size = Popen( cmd, shell=True, stdout=PIPE )
		total_size = total_size.stdout.read( ).strip( )
		cmd = "df -h | awk '/%s/ {print $3}'" % aName
		used_size = Popen( cmd, shell=True, stdout=PIPE )
		used_size = used_size.stdout.read( ).strip( )
		cmd = "df -h | awk '/%s/ {print $5}'" % aName
		percent = Popen( cmd, shell=True, stdout=PIPE )
		percent = percent.stdout.read( ).strip( )
		percent = int( re.sub( '%', '', percent ) )

		return total_size, used_size, percent


	def GetRecordFreeSize( self ) :
		total_size = MR_LANG( 'Unknown' )
		used_size = MR_LANG( 'Unknown' )
		percent = MR_LANG( 'Unknown' )
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


	def GetHDDName( self ) :
		name = MR_LANG( 'Unknown' )
		device = '/dev/sda'
		cmd = "hddtemp %s -D | awk '/Model:/ {print $2}'" % device
		name = Popen( cmd, shell=True, stdout=PIPE )
		name = name.stdout.read( ).strip( )
		return name


	def GetTotalSize( self ) :
		size = MR_LANG( 'Unknown' )
		unit = ''
		device = '/dev/sda'
		cmd = "fdisk -ul %s | awk '/Disk/ {print $3}'" % device
		size = Popen( cmd, shell=True, stdout=PIPE )
		size = size.stdout.read( ).strip( )
		cmd = "fdisk -ul %s | awk '/Disk/ {print $4}'" % device
		unit = Popen( cmd, shell=True, stdout=PIPE )
		unit = unit.stdout.read( ).strip( )
		unit = re.sub( ',', '', unit )
		return '%s %s' % ( size, unit )


	@RunThread
	def ShowHDDTemperature( self ) :
		temperature = MR_LANG( 'Unknown' )
		device = '/dev/sda'
		cmd = 'hddtemp %s -n -q' % device
		while( self.mCheckEndThread ) :
			if self.mCtrlLeftGroup.getSelectedPosition( ) == E_HDD :
				if self.CheckExistsDisk( ) :
					temperature = Popen( cmd, shell=True, stdout=PIPE )
					temperature = temperature.stdout.read( ).strip( )
					if IsNumber( temperature ) == False :
						temperature = MR_LANG( 'Unknown' )
					LOG_TRACE( 'HDD Temperature = %s' % temperature )
				else :
					temperature = MR_LANG( 'Unknown' )
				self.mCtrlHDDTemperature.setLabel( MR_LANG( 'Temperature : %s' ) % temperature )
			time.sleep( 1 )


	def CheckExistsDisk( self ) :
		cmd = 'df'
		parsing = Popen( cmd, shell=True, stdout=PIPE )
		parsing = parsing.stdout.read( ).strip( )
		if parsing.count( '/dev/sda' ) >= 3 :
			return True
		else :
			return False
