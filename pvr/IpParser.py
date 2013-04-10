from pvr.gui.GuiConfig import *


FILE_NAME_INTERFACES	 		=	'/etc/network/interfaces'
FILE_NAME_TEMP_INTERFACES		= 	'/mtmp/interface'
FILE_NAME_RESOLV_CONF			=	'/etc/resolv.conf'
FILE_NAME_AUTO_RESOLV_CONF		=	'/etc/init.d/update-resolv.sh'
FILE_NAME_AUTO_RESOLV_LINK		=	'/etc/rc5.d/S90resolve.conf'
FILE_TEMP						=	'/mtmp/ip_temp'
FILE_WPA_SUPPLICANT				=	'/etc/wpa_supplicant/wpa_supplicant.conf'

SYSTEM_COMMAND_GET_GATEWAY		=	"route -n | awk '/^0.0.0.0/ {print $2}'"

COMMAND_COPY_INTERFACES			=	"cp " + FILE_NAME_TEMP_INTERFACES + " " + FILE_NAME_INTERFACES

gNetworkMgr					= None

def GetInstance( ) :
	global gNetworkMgr
	if not gNetworkMgr :
		gNetworkMgr = IpParser( )
	else :
		pass

	return gNetworkMgr


class IpParser( object ) :
	def __init__( self ) :
		self.mEthernetDevName			= 'eth0'
		#self.mNetworkType				= NETWORK_ETHERNET
	
		self.mEthType					= None
		self.mEthernetAddressIp			= '255.255.255.255'
		self.mEthernetAddressMask		= '255.255.255.255'
		self.mEthernetAddressGateway	= '255.255.255.255'
		self.mEthernetAddressNameServer	= '255.255.255.255'

		self.mWifiCurrentSsid			= None
		self.mWifiPassWord				= None
		self.mWifikey_mgmt				= None
		self.mWifiEncryptType			= ENCRYPT_TYPE_WPA


	def IfUpDown( self, aDev ) :
		os.system( 'touch /mtmp/iftest_%s' % aDev )
		time.sleep( 1 )
		for i in range( 20 ) :
			if os.path.exists( '/mtmp/iftest_%s' % aDev ) :
				time.sleep( 1 )
			else :
				break


	#def SetCurrentNetworkType( aType ) :
		#self.mNetworkType = aType
		"""
		from ElisProperty import ElisPropertyEnum
		import pvr.ElisMgr
		command = pvr.ElisMgr.GetInstance( ).GetCommander( )
		if self.mNetworkType == NETWORK_WIRELESS :
			ElisPropertyEnum( 'Network Type' , command ).SetProp( 1 )
		else :
			ElisPropertyEnum( 'Network Type' , command ).SetProp( 0 )
		"""


	def GetCurrentServiceType( self ) :
		try :
			inputFile = open( FILE_NAME_INTERFACES, 'r' )
			inputline = inputFile.readlines( )
			inputFile.close( )
			for line in inputline :
				if line.startswith( 'auto ra0' ) or line.startswith( 'auto wlan0' ) :
					return NETWORK_WIRELESS
				elif line.startswith( 'auto eth0' ) :
					return NETWORK_ETHERNET
		except Exception, e :
				if inputFile.closed == False :
					inputFile.close( )
				LOG_ERR( 'Error exception[%s]' % e )
				return NETWORK_ETHERNET


	def GetAdapterState( self, aDevice ) :
		classdir = "/sys/class/net/" + aDevice + "/device/"
		if os.path.exists( classdir ) :
			files = os.listdir( classdir )
			if 'driver' in files :
				return True
			else:
				return False
		else:
			return False


	def GetInstalledAdapters( self ) :
		return [ dev for dev in os.listdir( '/sys/class/net' ) ]


	def GetDefaultGateway( self ) :
		addr = None
		try :
			inputFile = None
			os.system( SYSTEM_COMMAND_GET_GATEWAY + ' > ' + FILE_TEMP )
			inputFile = open( FILE_TEMP, 'r' )
			addr = inputFile.readline( ).strip( )
			if CheckIsIptype( addr ) == False :
				addr = None
			inputFile.close( )
			return addr

		except Exception, e :
			if inputFile and inputFile.closed == False :
				inputFile.close( )
			LOG_ERR( 'Error exception[%s]' % e )
			addr = None
			return addr


	def CheckIsIptype( self, aAddress ) :
		try :
			if aAddress == None or len( aAddress ) < 1 :
				return False

			string = None
			string = aAddress.split( '.', 3 )
			if string == None or len( string ) < 4 :
				return False

			if int( string[0] ) < 0 or int( string[0] ) > 255 :
				return False
			if int( string[1] ) < 0 or int( string[1] ) > 255 :
				return False
			if int( string[2] ) < 0 or int( string[2] ) > 255 :
				return False
			if int( string[3] ) < 0 or int( string[3] ) > 255 :
				return False
			return True

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return False


	def LoadNetworkType( self ) :
		try :
			inputFile = open( FILE_NAME_INTERFACES, 'r' )
			inputline = inputFile.readlines( )
			inputFile.close( )
			for line in inputline :
				if line.startswith( 'auto ra0' ) or line.startswith( 'auto wlan0' ) :
					#self.SetCurrentNetworkType( NETWORK_WIRELESS )
					break
				elif line.startswith( 'auto eth0' ) :
					#self.SetCurrentNetworkType( NETWORK_ETHERNET )
					break
		except Exception, e :
				if inputFile.closed == False :
					inputFile.close( )
				LOG_ERR( 'Error exception[%s]' % e )
				#self.SetCurrentNetworkType( NETWORK_ETHERNET )


	def GetNetworkAddress( self, aType ) :
		print 'dhkim test GetNetworkAddress #1'
		if aType == NETWORK_ETHERNET :
			dev = self.mEthernetDevName
		else :
			dev = self.GetWifidevice( )
		print 'dhkim test dev = %s' % dev
		addressIp = 'None'
		addressMask = 'None'
		addressGateway = 'None'
		addressNameServer = 'None'
		print 'dhkim test GetNetworkAddress #3'
		try :
			inputFile = None
			osCommand = [ "ifconfig %s | awk '/inet / {print $2}' | awk -F: '{print $2}'" % dev + ' > ' + FILE_TEMP, "ifconfig %s | awk '/inet / {print $4}' | awk -F: '{print $2}'" % aDeviceName + ' >> ' + FILE_TEMP, SYSTEM_COMMAND_GET_GATEWAY + ' >> ' + FILE_TEMP ]
			
			for command in osCommand :
				time.sleep( 0.01 )
				os.system( command )
			
			time.sleep( 0.02 )
			inputFile = open( FILE_TEMP, 'r' )
			addressIp = inputFile.readline( )
			addressMask = inputFile.readline( )
			addressGateway = inputFile.readline( )
			addressNameServer = self.GetNameServer( )

			if self.CheckIsIptype( addressIp ) == False :
				addressIp = 'None'

			if self.CheckIsIptype( addressMask ) == False :
				addressMask = 'None'

			if self.CheckIsIptype( addressGateway ) == False :
				addressGateway = 'None'

			if self.CheckIsIptype( addressNameServer ) == False :
				addressNameServer = 'None'

			inputFile.close( )
			print 'dhkim test GetNetworkAddress #2'
			return addressIp, addressMask, addressGateway, addressNameServer

		except Exception, e :
			if inputFile and inputFile.closed == False :
				inputFile.close( )
			LOG_ERR( 'Error exception[%s]' % e )
			return 'None', 'None', 'None', 'None'


	def GetNameServer( self ) :
		addressNameServer = 'None'
		try :
			inputFile = open( FILE_NAME_RESOLV_CONF, 'r' )
			inputline = inputFile.readlines( )

			for line in inputline :
				if line.startswith( 'nameserver' ) :
					words = string.split( line )
					addressNameServer = words[1]
					break
			inputFile.close( )
			return addressNameServer

		except Exception, e :
			if inputFile.closed == False :
				inputFile.close( )
			addressNameServer = 'None'
			LOG_ERR( 'Error exception[%s]' % e )
			return addressNameServer


	def SetIpAddressProperty( self, aAddressIp, aAddressMask, aAddressGateway, aAddressNameServer ) :
		from ElisProperty import ElisPropertyInt
		import pvr.ElisMgr
		command = pvr.ElisMgr.GetInstance( ).GetCommander( )
		if self.CheckIsIptype( aAddressIp ) == True :
			ElisPropertyInt( 'IpAddress' , command ).SetProp( MakeStringToHex( aAddressIp ) )
			make = ElisPropertyInt( 'IpAddress' , command ).GetProp( )
			make_1, make_2, make_3, make_4 = MakeHexToIpAddr( make )
			LOG_TRACE( 'make_1 = %d' % make_1 )
			LOG_TRACE( 'make_2 = %d' % make_2 )
			LOG_TRACE( 'make_3 = %d' % make_3 )
			LOG_TRACE( 'make_4 = %d' % make_4 )
		if self.CheckIsIptype( aAddressMask ) == True :
			ElisPropertyInt( 'SubNet' , command ).SetProp( MakeStringToHex( aAddressMask ) )
			make = ElisPropertyInt( 'SubNet' , command ).GetProp( )
			make_1, make_2, make_3, make_4 = MakeHexToIpAddr( make )
			LOG_TRACE( 'make_1 = %d' % make_1 )
			LOG_TRACE( 'make_2 = %d' % make_2 )
			LOG_TRACE( 'make_3 = %d' % make_3 )
			LOG_TRACE( 'make_4 = %d' % make_4 )
		if self.CheckIsIptype( aAddressGateway ) == True :
			ElisPropertyInt( 'Gateway' , command ).SetProp( MakeStringToHex( aAddressGateway ) )
			make = ElisPropertyInt( 'Gateway' , command ).GetProp( )
			make_1, make_2, make_3, make_4 = MakeHexToIpAddr( make )
			LOG_TRACE( 'make_1 = %d' % make_1 )
			LOG_TRACE( 'make_2 = %d' % make_2 )
			LOG_TRACE( 'make_3 = %d' % make_3 )
			LOG_TRACE( 'make_4 = %d' % make_4 )
		if self.CheckIsIptype( aAddressNameServer ) == True :
			ElisPropertyInt( 'DNS' , command ).SetProp( MakeStringToHex( aAddressNameServer ) )
			make = ElisPropertyInt( 'DNS' , command ).GetProp( )
			make_1, make_2, make_3, make_4 = MakeHexToIpAddr( make )
			LOG_TRACE( 'make_1 = %d' % make_1 )
			LOG_TRACE( 'make_2 = %d' % make_2 )
			LOG_TRACE( 'make_3 = %d' % make_3 )
			LOG_TRACE( 'make_4 = %d' % make_4 )


	"""
	def LoadEthernetType( self ) :
		status = False
		try :
			if self.mEthernetDevName != None :
				inputFile = open( FILE_NAME_INTERFACES, 'r' )
				inputline = inputFile.readlines( )
				for line in inputline :
					if line.startswith( 'iface ' + self.mEthernetDevName + ' inet' ) :
						words = string.split( line )
						if words[3] == 'static' :
							self.mEthType = NET_STATIC
						else :
							self.mEthType = NET_DHCP
						status = True
			else :
				LOG_ERR( 'LoadEthernetType Load Fail!!!' )

			inputFile.close( )
			return status

		except Exception, e :
			if inputFile.closed == False :
				inputFile.close( )
			LOG_ERR( 'Error exception[%s]' % e )
			status = False
			return status
	"""
	def GetEthernetMethod( self ) :
		try :
			nettype = NET_DHCP
			if os.path.exists( FILE_NAME_INTERFACES ) :
				inputFile = open( FILE_NAME_INTERFACES, 'r' )
				inputline = inputFile.readlines( )
				for line in inputline :
					if line.startswith( 'iface ' + self.mEthernetDevName + ' inet' ) :
						words = string.split( line )
						if words[3] == 'static' :
							nettype = NET_STATIC

				inputFile.close( )
				return nettype

			else :
				LOG_ERR( '%s path is not exist' % WIFI_CONFIGURED_PATH )
				return nettype

		except Exception, e :
			if inputFile.closed == False :
				inputFile.close( )
			LOG_ERR( 'Error exception[%s]' % e )
			return NET_DHCP


	def LoadEthernetAddress( self ) :
		self.mEthernetAddressIp, self.mEthernetAddressMask, self.mEthernetAddressGateway, self.mEthernetAddressNameServer = self.GetNetworkAddress( self.mEthernetDevName )


	def GetEthernetType( self ) :
		return self.mEthType


	def GetEthernetAddress( self ) :
		return self.mEthernetAddressIp, self.mEthernetAddressMask, self.mEthernetAddressGateway, self.mEthernetAddressNameServer


	def SetEthernet( self, aType, aIpAddress=None, aMaskAddress=None, aGatewayAddress=None, aNameAddress=None ) :
		status = False
		try :
			inputFile = open( FILE_NAME_INTERFACES, 'r' )
			outputFile = open( FILE_NAME_TEMP_INTERFACES, 'w+' )
			inputline = inputFile.readlines( )
			for line in inputline :
				if line.startswith( 'auto ra0' ) or line.startswith( 'auto wlan0' ) or line.startswith( 'auto eth0' ) :
					outputFile.writelines( 'auto ' + self.mEthernetDevName + '\n' )
				elif line.startswith( 'iface ' + self.mEthernetDevName + ' inet' ) :
					if aType == NET_DHCP :
						outputFile.writelines( 'iface ' + self.mEthernetDevName + ' inet' + ' ' + 'dhcp\n' )
					else :
						outputFile.writelines( 'iface ' + self.mEthernetDevName + ' inet' + ' ' + 'static\n' )
						outputFile.writelines( 'address %s\n' % aIpAddress )
						outputFile.writelines( 'netmask %s\n' % aMaskAddress )
						outputFile.writelines( 'gateway %s\n' % aGatewayAddress )
				elif line.startswith( 'address' ) or line.startswith( 'netmask' ) or line.startswith( 'gateway' ) :
					continue
				else :
					outputFile.writelines( line )

			inputFile.close( )
			outputFile.close( )

			self.SetEthernetNameServer( aType, aNameAddress )
			os.system( COMMAND_COPY_INTERFACES )
			#wifi = WirelessParser( )
			self.IfUpDown( self.mEthernetDevName )
			#os.system( '/app/ifdown_wifi.sh' )
			#os.system( '/app/ifdown_ethernet.sh' )
			
			#time.sleep( 1 )
			#os.system( '/app/ifup_ethernet.sh' )
			status = True
			inputFile.close( )
			outputFile.close( )
			return status

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			status = False
			if inputFile.closed == False :
				inputFile.close( )
			if outputFile.closed == False :
				outputFile.close( )
			return status


	def SetEthernetNameServer( self, aType, aNameAddress ) :
		try :
			if aType == NET_DHCP :
				os.system( 'rm -rf ' + FILE_NAME_AUTO_RESOLV_CONF )
			else :
				os.system( 'echo nameserver %s' % aNameAddress + '> ' + FILE_NAME_RESOLV_CONF )
				os.system( 'echo echo nameserver %s \> %s > %s' % ( aNameAddress, FILE_NAME_RESOLV_CONF, FILE_NAME_AUTO_RESOLV_CONF ) )
				os.system( 'chmod 755 %s' % FILE_NAME_AUTO_RESOLV_CONF )
				if os.path.isfile( FILE_NAME_AUTO_RESOLV_LINK ) == False :
					os.system( 'ln -s %s %s' % ( FILE_NAME_AUTO_RESOLV_CONF, FILE_NAME_AUTO_RESOLV_LINK ) )
			return True
			
		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return False


	def ResetWifiInfo( self ) :
		self.mWifiCurrentSsid	= None
		self.mWifiPassWord		= None
		self.mWifikey_mgmt		= None
		self.mWifiEncryptType	= ENCRYPT_TYPE_WPA


	def LoadWpaSupplicant( self ) :
		self.ResetWifiInfo( )
		if os.path.exists( FILE_WPA_SUPPLICANT ) == False :
			return False
		try :
			openFile = open( FILE_WPA_SUPPLICANT, 'r' )
			inputline = openFile.readlines( )
			for line in inputline :
				line = line.lstrip( )
				if line.startswith( 'ssid=' ) and len( line ) > 6 :
					self.mWifiCurrentSsid = line[ 6 : -2 ]
				elif line.startswith( 'wep_key0="' ) and len( line ) > 11 :
					self.mWifiPassWord = line[ 10 : -2 ]
				elif line.startswith( 'wep_key0=' ) and len( line ) > 9 :
					self.mWifiPassWord = line[ 9 : -1 ]
				elif line.startswith( 'psk="' ) and len( line ) > 6 :
					self.mWifiPassWord = line[ 5 : -2 ]
				elif line.startswith( '#psk="' ) and len( line ) > 6 :
					self.mWifiPassWord = line[ 6 : -2 ]
				elif not self.mWifiPassWord and line.startswith( 'psk=' ) and len( line ) > 4 :
					self.mWifiPassWord = line[ 4 : -1 ]
				elif line.startswith( 'key_mgmt=' ) and len( line ) > 9 :
					self.mWifikey_mgmt = line[ 9 : -1 ]
			openFile.close( )
			return True

		except Exception, e :
			if openFile.closed == False :
				openFile.close( )
			LOG_ERR( 'Error exception[%s]' % e )
			return False


	"""
	def GetCurrentSsid( self ) :
		if self.mWifiCurrentSsid == None :
			return 'None'
		return self.mWifiCurrentSsid
	"""
	def GetConfiguredSSID( self ) :
		try :
			if os.path.exists( FILE_WPA_SUPPLICANT ) :
				openFile = open( FILE_WPA_SUPPLICANT, 'r' )
				inputline = openFile.readlines( )
				for line in inputline :
					line = line.lstrip( )
					if line.startswith( 'ssid=' ) and len( line ) > 6 :
						ssid = line[ 6 : -2 ]
						openFile.close( )
						return ssid

				openFile.close( )
				return None

			else :
				LOG_ERR( '%s path is not exist' % FILE_WPA_SUPPLICANT )
				return None

		except Exception, e :
			if openFile.closed == False :
				openFile.close( )
			LOG_ERR( 'Error exception[%s]' % e )
			return None


	"""
	def GetPassword( self ) :
		if self.mWifiPassWord == None :
			return ''
		return self.mWifiPassWord
	"""
	def GetConfiguredPassword( self ) :
		try :
			if os.path.exists( FILE_WPA_SUPPLICANT ) :
				passwd = None
				openFile = open( FILE_WPA_SUPPLICANT, 'r' )
				inputline = openFile.readlines( )
				for line in inputline :
					line = line.lstrip( )
					if line.startswith( 'wep_key0="' ) and len( line ) > 11 :
						passwd = line[ 10 : -2 ]
					elif line.startswith( 'wep_key0=' ) and len( line ) > 9 :
						passwd = line[ 9 : -1 ]
					elif line.startswith( 'psk="' ) and len( line ) > 6 :
						passwd = line[ 5 : -2 ]
					elif line.startswith( '#psk="' ) and len( line ) > 6 :
						passwd = line[ 6 : -2 ]
					#elif not self.mWifiPassWord and line.startswith( 'psk=' ) and len( line ) > 4 :
					#	self.mWifiPassWord = line[ 4 : -1 ]
					#elif line.startswith( 'key_mgmt=' ) and len( line ) > 9 :
					#	passwd = line[ 9 : -1 ]

					if passwd :
						openFile.close( )
						return passwd

				openFile.close( )
				return None

			else :
				LOG_ERR( '%s path is not exist' % FILE_WPA_SUPPLICANT )
				return None

		except Exception, e :
			if openFile.closed == False :
				openFile.close( )
			LOG_ERR( 'Error exception[%s]' % e )
			return None
		
	"""
	def GetWifiEncryptType( self ) :
		if self.mWifikey_mgmt == 'NONE' :
			if self.mWifiPassWord == None :
				self.mWifiEncryptType = ENCRYPT_OPEN
			else :
				self.mWifiEncryptType = ENCRYPT_TYPE_WEP
		elif self.mWifikey_mgmt == "WPA-PSK" :
			self.mWifiEncryptType = ENCRYPT_TYPE_WPA
		else :
			LOG_ERR( 'GetEncryptType failed!!' )

		return self.mWifiEncryptType

	"""
	def GetWifiEncryptType( self ) :
		enc = self.GetConfiguredPassword( )
		if enc == None :
			if self.GetConfiguredPassword( ) == None :
				return ENCRYPT_OPEN
			else :
				return ENCRYPT_TYPE_WEP
		elif enc == "WPA-PSK" :
			return ENCRYPT_TYPE_WPA
		else :
			LOG_ERR( 'GetEncryptType failed!!' )
			return ENCRYPT_TYPE_WPA
	
	
	def GetConfiguredPassword( self ) :
		try :
			if os.path.exists( FILE_WPA_SUPPLICANT ) :
				openFile = open( FILE_WPA_SUPPLICANT, 'r' )
				inputline = openFile.readlines( )
				for line in inputline :
					line = line.lstrip( )
					if line.startswith( 'key_mgmt=' ) and len( line ) > 9 :
						enc = line[ 9 : -1 ]
						openFile.close( )
						return enc

				openFile.close( )
				return None

			else :
				LOG_ERR( '%s path is not exist' % FILE_WPA_SUPPLICANT )
				return None

		except Exception, e :
			if openFile.closed == False :
				openFile.close( )
			LOG_ERR( 'Error exception[%s]' % e )
			return None


	def GetWifidevice( self ) :
		for dev in self.GetInstalledAdapters( ) :
			if dev.startswith( 'eth' ) or dev == 'lo':
				continue
			if self.GetAdapterState( dev ) == True :
				return dev
		return None	


	def ScanWifiAP( self, aDev ) :
		from pythonwifi.iwlibs import Wireless
		import pythonwifi.flags
		status = None
		try :
			scanResult = None
			if self.GetCurrentNetworkType( ) != NETWORK_WIRELESS :
				#os.system( 'ifup %s' % aDev )
				#os.system( '/app/ifup_wifi.sh' )
				self.IfUpDown( aDev + '_up' )

			os.system( 'iwlist %s scan > %s' % ( aDev, FILE_TEMP ) )
			from IwlistParser import Get_ApList
			scanResult = Get_ApList( )
			
			if scanResult != None :
				apList = []
				for ap in scanResult :
					apInfoList = []
					if len( ap[0] ) > 0 :
						apInfoList.append( ap[0] )
						apInfoList.append( ap[1] )
						apInfoList.append( ap[2] )
						apList.append( apInfoList )
				if apList :
					status = apList 
				else :
					status = None

			if self.GetCurrentNetworkType( ) != NETWORK_WIRELESS :
				#os.system( 'ifdown %s' % aDev )
				#os.system( '/app/ifdown_wifi.sh' )
				self.IfUpDown( aDev + '_down' )
			return status

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			if self.GetCurrentNetworkType( ) != NETWORK_WIRELESS :
				#os.system( 'ifdown %s' % aDev )
				#os.system( '/app/ifdown_wifi.sh' )
				self.IfUpDown( aDev + '_down' )
			status = None
			return status


	def ApInfoToEncrypt( self, aType ) :
		if aType == 'No' :
			return ENCRYPT_OPEN
		elif aType == 'WPA' :
			return ENCRYPT_TYPE_WPA
		elif aType == 'WEP' :
			return ENCRYPT_TYPE_WEP
		else :
			LOG_ERR( 'ApInfoToEncrypt Fail!!' )
			return ENCRYPT_TYPE_WPA


	def WriteWpaSupplicant( self, aUseHiddenId, aHiddenSsid, aCurrentSsid, aEncryptType, aPassWord ) :
		try :
			openFile = open( FILE_WPA_SUPPLICANT, 'w' )
			words = "ctrl_interface=/var/run/wpa_supplicant\n"
			words += "eapol_version=1\n"
			words += "fast_reauth=1\n"
			words += "ap_scan=1\n"
			words += "network={\n"
			if aUseHiddenId == USE_HIDDEN_SSID :
				words += "\tssid=\"" + aHiddenSsid + "\"\n"
				words += "\tscan_ssid=1\n"
			else :
				words += "\tssid=\"" + aCurrentSsid + "\"\n"
				words += "\tscan_ssid=0\n"
			if aEncryptType == ENCRYPT_TYPE_WEP :
				words += "\tkey_mgmt=NONE\n"
				words += "\twep_key0="
				if len( aPassWord ) == 10 or len( aPassWord ) == 26 :
					words += aPassWord + "\n"
				else:
					words += "\"" + aPassWord + "\"\n"
				words += "\tauth_alg=SHARED\n"
			elif aEncryptType == ENCRYPT_TYPE_WPA :
				words += "\tkey_mgmt=WPA-PSK\n"
				words += "\tpsk=\"" + aPassWord + "\"\n"
			else:
				words += "\tkey_mgmt=NONE\n"
			words += "}\n"
			openFile.write( words )
			openFile.close( )
			self.WriteInterfaces( )
			return True

		except Exception, e :
			if openFile.closed == False :
				openFile.close( )				
			LOG_ERR( 'Error exception[%s]' % e )
			return False


	def WriteInterfaces( self ) :
		try :
			inputFile = open( FILE_NAME_INTERFACES, 'r' )
			outputFile = open( FILE_NAME_TEMP_INTERFACES, 'w+' )
			inputline = inputFile.readlines( )
			for line in inputline :
				if line.startswith( 'auto ra0' ) or line.startswith( 'auto wlan0' ) or line.startswith( 'auto eth0' ) :
					outputFile.writelines( 'auto ' + self.GetWifidevice( ) + '\n')
				else :
					outputFile.writelines( line )

			inputFile.close( )
			outputFile.close( )
			os.system( COMMAND_COPY_INTERFACES )

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			if inputFile.closed == False :
				inputFile.close( )
			if outputFile.closed == False :
				outputFile.close( )


	def ConnectWifi( self, aDev ) :
		try :
			os.system( 'rm -rf ' + FILE_NAME_AUTO_RESOLV_CONF )
			#os.system( 'ifdown %s' % aDev )
			#os.system( '/app/ifdown_wifi.sh' )
			#time.sleep( 1 )
			#os.system( 'ifdown %s' % self.mEthernetDevName )
			#os.system( '/app/ifdown_ethernet.sh' )
			#time.sleep( 1 )
			#os.system( 'ifup %s' % aDev )
			#os.system( '/app/ifup_wifi.sh' )
			self.IfUpDown( aDev )
		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return False


	def GetWifiUseStatic( self ) :
		dev = self.GetWifidevice( )
		if dev :
			try :
				status = NET_DHCP
				inputFile = open( FILE_NAME_INTERFACES, 'r' )
				inputline = inputFile.readlines( )
				for line in inputline :
					if line.startswith( 'iface ' + dev + ' inet' ) :
						words = string.split( line )
						if words[3] == 'static' :
							status = NET_STATIC
						else :
							status = NET_DHCP
						break

				inputFile.close( )
				return status

			except Exception, e :
				if inputFile.closed == False :
					inputFile.close( )
				LOG_ERR( 'Error exception[%s]' % e )
				return status

		else :
			LOG_ERR( 'Can not found wifi device' )


	def SetEthernetNameServer( self, aType, aNameAddress ) :
		try :
			if aType :
				os.system( 'echo nameserver %s' % aNameAddress + '> ' + FILE_NAME_RESOLV_CONF )
				os.system( 'echo echo nameserver %s \> %s > %s' % ( aNameAddress, FILE_NAME_RESOLV_CONF, FILE_NAME_AUTO_RESOLV_CONF ) )
				os.system( 'chmod 755 %s' % FILE_NAME_AUTO_RESOLV_CONF )
				if os.path.isfile( FILE_NAME_AUTO_RESOLV_LINK ) == False :
					os.system( 'ln -s %s %s' % ( FILE_NAME_AUTO_RESOLV_CONF, FILE_NAME_AUTO_RESOLV_LINK ) )
			else :
				os.system( 'rm -rf ' + FILE_NAME_AUTO_RESOLV_CONF )
			return True
			
		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return False


	def WriteWifiInterfaces( self, aDev, aIsStatic, aIpAddress = None, aMaskAddress = None, aGatewayAddress = None, aNameAddress = None ) :
		try :
			inputFile = open( FILE_NAME_INTERFACES, 'r' )
			outputFile = open( FILE_NAME_TEMP_INTERFACES, 'w+' )
			inputline = inputFile.readlines( )
			for line in inputline :
				if line.startswith( 'iface ' + aDev + ' inet' ) :
					if aIsStatic :
						outputFile.writelines( 'iface ' + aDev + ' inet' + ' ' + 'static\n' )
						outputFile.writelines( '\taddress %s\n' % aIpAddress.strip( ) )
						outputFile.writelines( '\tnetmask %s\n' % aMaskAddress.strip( ) )
						outputFile.writelines( '\tgateway %s\n' % aGatewayAddress.strip( ) )
					else :
						outputFile.writelines( 'iface ' + aDev + ' inet' + ' ' + 'dhcp\n' )

				elif line.startswith( '\taddress' ) or line.startswith( '\tnetmask' ) or line.startswith( '\tgateway' ) :
					continue
				else :
					outputFile.writelines( line )

			inputFile.close( )
			outputFile.close( )

			self.SetEthernetNameServer( aIsStatic, aNameAddress )
			os.system( COMMAND_COPY_INTERFACES )
			status = True
			inputFile.close( )
			outputFile.close( )
			return status

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			status = False
			if inputFile.closed == False :
				inputFile.close( )
			if outputFile.closed == False :
				outputFile.close( )
			return status


	def CheckInternetState( self ) :
		return xbmc.getInfoLabel( 'System.internetstate' )

