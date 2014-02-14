from pvr.gui.WindowImport import *
from webinterface import Webinterface

class ElmoPowerStatus( Webinterface ) :

	def __init__(self, urlPath) :
	
		super(ElmoPowerStatus, self).__init__(urlPath)
		self.result = "True"

		print '[Power Control] '
		print self.params

		if 'newstate' in self.params :
			# Gui Restart
			if self.params['newstate'] == '3' : 
				self.mDataCache.Splash_StartAndStop( 1 )
				pvr.ElisMgr.GetInstance().Shutdown( )
				xbmc.executebuiltin( 'Settings.Save' )
				os.system( 'killall -9 xbmc.bin' )
			#Active Standby
			if self.params['newstate'] == '0' :
				self.mCommander.System_StandbyMode( 1 )
			#Deep Standby
			if self.params['newstate'] == '1' :
				self.mCommander.System_StandbyMode( 0 )
			#Reboot
			if self.params['newstate'] == '2' :
				isDownload = WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_SYSTEM_UPDATE ).GetStatusFromFirmware( )
				if isDownload :
					self.result = "False"
				else :
					self.mDataCache.System_Reboot( )
	
	def xmlResult(self) :

		xmlStr = '<?xml version="1.0" encoding="UTF-8"?>\n'
		xmlStr += '<e2instandby>' + self.result + '</e2instandby>\n'
		xmlStr += '</e2instandby>\n'
						
		return xmlStr
		
