from pvr.gui.GuiConfig import *
from pvr.GuiHelper import *
import pvr.ElisMgr


class BackupSettings( object ) :
	def __init__( self ) :
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )

		LOG_TRACE( '------------------------------check backup' )
		if CheckDirectory( E_DEFAULT_BACKUP_PATH ) :
			self.CheckBackup( )
			RemoveDirectory( E_DEFAULT_BACKUP_PATH )


	def CheckBackup( self ) :
		LOG_TRACE( 'backup checked' )
		pass

		if CheckDirectory( '%s/%s'% ( E_DEFAULT_BACKUP_PATH, 'network.conf' ) ) :
			self.SetNetwork( )


	def SetNetwork( self ) :
		pass
		#ToDO : network backup, /config/backup/network
		#ToDO : network restart



