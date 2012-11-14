from pvr.gui.WindowImport import *
import pvr.ElisMgr

"""
def GetInstance( ) :
	global gGlobalEvent
	if not gGlobalEvent :
		print 'Create instance'
		gGlobalEvent = GlobalEvent( )
	else :
		pass

	return gGlobalEvent
"""

class BackupSettings( object ) :
	def __init__( self ) :
		#self.mDataCache = pvr.DataCacheMgr.GetInstance( )
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )

		#ToDO : network backup, /config/backup/network
		#ToDO : delete directory backup, /config/backup

		self.CheckBackup( )


	def CheckBackup( self ) :
		pass



