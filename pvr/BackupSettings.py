from pvr.gui.GuiConfig import *
from pvr.GuiHelper import *
import pvr.Platform
import pvr.ElisMgr


class NetworkInfo( object ) :
	def __init__( self ) :
		self.mType					= NETWORK_ETHERNET
		self.mEthType				= NET_DHCP
		self.mIpaddr				= '127.0.0.1'
		self.mSubnet				= '255.255.255.0'
		self.mGwaddr				= '127.0.0.1'
		self.mDns					= '168.126.63.1'

		self.mWinfo_mDevName		= 'ra0'
		self.mWinfo_ctrl_interface	= '/var/run/wpa_supplicant'
		self.mWinfo_meapol_version	= 1
		self.mWinfo_fast_reauth		= 1
		self.mWinfo_ap_scan			= 1
		#Network
		self.mWinfo_ssid			= '\"PrismCubeAP\"'
		self.mWinfo_scan_ssid		= 0
		self.mWinfo_key_mgmt		= 'WPA-PSK'
		self.mWinfo_proto			= 'RSN'
		self.mWinfo_pairwise		= 'CCMP TKIP'
		self.mWinfo_group			= 'CCMP TKIP'
		self.mWinfo_psk				= '\"curlyonion757\"'

		self.mError 				= -1


class BackupSettings( object ) :
	def __init__( self ) :
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )

		LOG_TRACE( '------------------------------Check backup' )
		if CheckDirectory( E_DEFAULT_BACKUP_PATH ) :
			#self.CheckBackup( )
			RemoveDirectory( E_DEFAULT_BACKUP_PATH )

		if CheckDirectory( '%s.sh'% E_DEFAULT_BACKUP_PATH ) :
			RemoveDirectory( '%s.sh'% E_DEFAULT_BACKUP_PATH )


	def CheckBackup( self ) :
		LOG_TRACE( 'Backup checked' )
		return

		if CheckDirectory( '%s/%s'% ( E_DEFAULT_BACKUP_PATH, 'network.conf' ) ) :
			self.SetNetwork( )

		LOG_TRACE( 'Backup done' )


	def SetNetwork( self ) :
		if not self.mPlatform.IsPrismCube( ) :
			LOG_TRACE( 'Not supported platform' )
			return

		if pvr.Platform.GetPlatform( ).GetXBMCVersion( ) >= pvr.Platform.GetPlatform( ).GetFrodoVersion( ) :
			LOG_TRACE( 'Network setting in Frodo' )
			return
	
		fd = open( '%s/network.conf'% E_DEFAULT_BACKUP_PATH, 'r' )
		networkData = fd.readlines( )
		fd.close( )

		iNet = NetworkInfo( )

		if networkData :
			try :
				for line in networkData :
					value = ParseStringInPattern( '=', line )
					#LOG_TRACE('-----------split[%s]'% value )
					if not value or len( value ) < 2 :
						continue

					if not value[0] :
						continue

					if value[0][0] == '#' or ( value[1] and value[1][0] ) == '{' : 
						continue

					LOG_TRACE( '%s=%s\n'% ( value[0], value[1] ) )

					if value[0] == 'NetworkType' :
						if value[1].isdigit( ) :
							iNet.mType = int( value[1] )
						else :
							iNet.mType = value[1]
					elif value[0] == 'ethtype' :
						ethType = NET_DHCP
						if value[1] == 'static' :
							ethType = NET_STATIC
						iNet.mEthType = ethType
					elif value[0] == 'ipaddr' :
						iNet.mIpaddr = value[1]
					elif value[0] == 'subnet' :
						iNet.mSubnet = value[1]
					elif value[0] == 'gateway' :
						iNet.mGwaddr = value[1]
					elif value[0] == 'dns' :
						iNet.mDns = value[1]

					elif value[0] == 'devname' :
						iNet.mWinfo_mDevName = value[1]
					elif value[0] == 'ctrl_interface' :
						iNet.mWinfo_ctrl_interface = value[1]
					elif value[0] == 'eapol_version' :
						iNet.mWinfo_meapol_version = value[1]
					elif value[0] == 'fast_reauth' :
						iNet.mWinfo_fast_reauth = value[1]
					elif value[0] == 'ap_scan' :
						iNet.mWinfo_ap_scan = value[1]
					elif value[0] == 'ssid' :
						#check \" \"
						iNet.mWinfo_ssid = value[1]
					elif value[0] == 'scan_ssid' :
						iNet.mWinfo_scan_ssid = value[1]
					elif value[0] == 'key_mgmt' :
						iNet.mWinfo_key_mgmt = value[1]
					elif value[0] == 'proto' :
						iNet.mWinfo_proto = value[1]
					elif value[0] == 'pairwise' :
						iNet.mWinfo_pairwise = value[1]
					elif value[0] == 'group' :
						iNet.mWinfo_group = value[1]
					elif value[0] == 'psk' :
						#check \" \"
						iNet.mWinfo_psk = value[1]

				iNet.mError = 0

			except Exception, e :
				iNet.mError = -1
				LOG_TRACE( 'Exception[%s]'% e )


		if iNet.mError != 0 :
			return

		"""
		SetCurrentNetworkType( iNet.mType )
		if iNet.mType == NETWORK_ETHERNET or iNet.mType == '0' :
			SetIpAddressProperty( iNet.mIpaddr, iNet.mSubnet, iNet.mGwaddr, iNet.mDns )
			ipInfo = IpParser( )
			ret = ipInfo.SetEthernet( iNet.mEthType, iNet.mIpaddr, iNet.mSubnet, iNet.mGwaddr, iNet.mDns )
			LOG_TRACE( 'setting done[%s]'% ret )

		else :
			pass
			#ToDO : wifi set

		#ToDO : wifi, network restart
		"""


