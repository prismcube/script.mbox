from pvr.gui.GuiConfig import *


FILE_NAME_INTERFACES	 		=	'/etc/network/interfaces'
FILE_NAME_TEMP_INTERFACES		= 	'/tmp/interface'
FILE_NAME_RESOLV_CONF			=	'/etc/resolv.conf'
FILE_NAME_AUTO_RESOLV_CONF		=	'/etc/init.d/update-resolv.sh'
FILE_NAME_AUTO_RESOLV_LINK		=	'/etc/rc5.d/S90resolve.conf'
FILE_TEMP						=	'/tmp/ip_temp'
FILE_WPA_SUPPLICANT				=	'/etc/wpa_supplicant/wpa_supplicant.conf'

SYSTEM_COMMAND_GET_GATEWAY		=	"route -n | awk '/^0.0.0.0/ {print $2}'"

COMMAND_COPY_INTERFACES			=	"cp " + FILE_NAME_TEMP_INTERFACES + " " + FILE_NAME_INTERFACES

gEthernetDevName	= 'eth0'
gNetworkType		= NETWORK_ETHERNET


def SetCurrentNetworkType( aType ) :
	global gNetworkType
	gNetworkType = aType
	from ElisProperty import ElisPropertyEnum
	import pvr.ElisMgr
	command = pvr.ElisMgr.GetInstance( ).GetCommander( )
	if gNetworkType == NETWORK_WIRELESS :
		ElisPropertyEnum( 'Network Type' , command ).SetProp( 1 )
	else :
		ElisPropertyEnum( 'Network Type' , command ).SetProp( 0 )


def GetCurrentNetworkType( ) :
	global gNetworkType
	return gNetworkType


def GetAdapterState( aDevice ) :
	classdir = "/sys/class/net/" + aDevice + "/device/"
	if os.path.exists( classdir ) :
		files = os.listdir( classdir )
		if 'driver' in files :
			return True
		else:
			return False
	else:
		return False


def GetInstalledAdapters( ) :
	return [ dev for dev in os.listdir( '/sys/class/net' ) ]


def GetDefaultGateway( ) :
	addr = None
	try :
		os.system( SYSTEM_COMMAND_GET_GATEWAY + ' > ' + FILE_TEMP )
		inputFile = open( FILE_TEMP, 'r' )
		addr = inputFile.readline( ).strip( )
		if CheckIsIptype( addr ) == False :
			addr = None
		inputFile.close( )
		return addr

	except Exception, e :
		if inputFile.closed == False :
			inputFile.close( )
		LOG_ERR( 'Error exception[%s]' % e )
		addr = None
		return addr

		
def PingTestInternal( ) :
	status = False
	try :
		defalutRoute = GetDefaultGateway( )
		if defalutRoute != None and defalutRoute != '' :
			os.system( 'ping -c 1 -W 6 %s > %s' % ( defalutRoute, FILE_TEMP ) )
			inputFile = open( FILE_TEMP, 'r' )
			inputline = inputFile.readlines( )
			for line in inputline :
				if line.startswith( '1 packets') :
					if line.split(' packets received')[0].split(', ')[-1] == '1' :
						status = True
						break

		inputFile.close( )
		return status

	except Exception, e :
		if inputFile.closed == False :
			inputFile.close( )
		LOG_ERR( 'Error exception[%s]' % e )
		status = False
		return status


def PingTestExternal( aAddr ) :
	status = False
	try :
		os.system( 'ping -c 1 -W 6 %s > %s' % ( aAddr, FILE_TEMP ) )
		inputFile = open( FILE_TEMP, 'r' )
		inputline = inputFile.readlines( )
		if len( inputline ) == 0 :
			inputFile.close( )
			return status
		for line in inputline :
			if line.startswith( '1 packets') :
				if line.split(' packets received')[0].split(', ')[-1] == '1' :
					status = True
					break

		inputFile.close( )
		return status

	except Exception, e :
		if inputFile.closed == False :
			inputFile.close( )
		LOG_ERR( 'Error exception[%s]' % e )
		status = False


def CheckIsIptype( aAddress ) :
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


def LoadNetworkType( ) :
	try :
		inputFile = open( FILE_NAME_INTERFACES, 'r' )
		inputline = inputFile.readlines( )
		inputFile.close( )
		for line in inputline :
			if line.startswith( 'auto ra0' ) or line.startswith( 'auto wlan0' ) :
				SetCurrentNetworkType( NETWORK_WIRELESS )
				break
			elif line.startswith( 'auto eth0' ) :
				SetCurrentNetworkType( NETWORK_ETHERNET )
				break
	except Exception, e :
			if inputFile.closed == False :
				inputFile.close( )
			LOG_ERR( 'Error exception[%s]' % e )
			SetCurrentNetworkType( NETWORK_ETHERNET )


def GetNetworkAddress( aDeviceName ) :
	addressIp = 'None'
	addressMask = 'None'
	addressGateway = 'None'
	addressNameServer = 'None'
	try :
		osCommand = [ "ifconfig %s | awk '/inet / {print $2}' | awk -F: '{print $2}'" % aDeviceName + ' > ' + FILE_TEMP, "ifconfig %s | awk '/inet / {print $4}' | awk -F: '{print $2}'" % aDeviceName + ' >> ' + FILE_TEMP, SYSTEM_COMMAND_GET_GATEWAY + ' >> ' + FILE_TEMP ]
		
		for command in osCommand :
			time.sleep( 0.01 )
			os.system( command )
		
		time.sleep( 0.02 )
		inputFile = open( FILE_TEMP, 'r' )
		addressIp = inputFile.readline( )
		addressMask = inputFile.readline( )
		addressGateway = inputFile.readline( )
		addressNameServer = GetNameServer( )

		if CheckIsIptype( addressIp ) == False :
			addressIp = 'None'

		if CheckIsIptype( addressMask ) == False :
			addressMask = 'None'

		if CheckIsIptype( addressGateway ) == False :
			addressGateway = 'None'

		if CheckIsIptype( addressNameServer ) == False :
			addressNameServer = 'None'

		inputFile.close( )
		return addressIp, addressMask, addressGateway, addressNameServer

	except Exception, e :
		if inputFile.closed == False :
			inputFile.close( )
		LOG_ERR( 'Error exception[%s]' % e )
		return 'None', 'None', 'None', 'None'


def GetNameServer( ) :
	addressNameServer = 'None'
	try :
		inputFile = open( FILE_NAME_RESOLV_CONF, 'r' )
		inputline = inputFile.readline( )
		words = string.split( inputline )
		addressNameServer = words[1]
		inputFile.close( )
		return addressNameServer

	except Exception, e :
		if inputFile.closed == False :
			inputFile.close( )
		addressNameServer = 'None'
		LOG_ERR( 'Error exception[%s]' % e )
		return addressNameServer


def SetIpAddressProperty( aAddressIp, aAddressMask, aAddressGateway, aAddressNameServer ) :
	from ElisProperty import ElisPropertyInt
	import pvr.ElisMgr
	command = pvr.ElisMgr.GetInstance( ).GetCommander( )
	if CheckIsIptype( aAddressIp ) == True :
		ElisPropertyInt( 'IpAddress' , command ).SetProp( MakeStringToHex( aAddressIp ) )
		make = ElisPropertyInt( 'IpAddress' , command ).GetProp( )
		make_1, make_2, make_3, make_4 = MakeHexToIpAddr( make )
		LOG_TRACE( 'make_1 = %d' % make_1 )
		LOG_TRACE( 'make_2 = %d' % make_2 )
		LOG_TRACE( 'make_3 = %d' % make_3 )
		LOG_TRACE( 'make_4 = %d' % make_4 )
	if CheckIsIptype( aAddressMask ) == True :
		ElisPropertyInt( 'SubNet' , command ).SetProp( MakeStringToHex( aAddressMask ) )
		make = ElisPropertyInt( 'SubNet' , command ).GetProp( )
		make_1, make_2, make_3, make_4 = MakeHexToIpAddr( make )
		LOG_TRACE( 'make_1 = %d' % make_1 )
		LOG_TRACE( 'make_2 = %d' % make_2 )
		LOG_TRACE( 'make_3 = %d' % make_3 )
		LOG_TRACE( 'make_4 = %d' % make_4 )
	if CheckIsIptype( aAddressGateway ) == True :
		ElisPropertyInt( 'Gateway' , command ).SetProp( MakeStringToHex( aAddressGateway ) )
		make = ElisPropertyInt( 'Gateway' , command ).GetProp( )
		make_1, make_2, make_3, make_4 = MakeHexToIpAddr( make )
		LOG_TRACE( 'make_1 = %d' % make_1 )
		LOG_TRACE( 'make_2 = %d' % make_2 )
		LOG_TRACE( 'make_3 = %d' % make_3 )
		LOG_TRACE( 'make_4 = %d' % make_4 )
	if CheckIsIptype( aAddressNameServer ) == True :
		ElisPropertyInt( 'DNS' , command ).SetProp( MakeStringToHex( aAddressNameServer ) )
		make = ElisPropertyInt( 'DNS' , command ).GetProp( )
		make_1, make_2, make_3, make_4 = MakeHexToIpAddr( make )
		LOG_TRACE( 'make_1 = %d' % make_1 )
		LOG_TRACE( 'make_2 = %d' % make_2 )
		LOG_TRACE( 'make_3 = %d' % make_3 )
		LOG_TRACE( 'make_4 = %d' % make_4 )


class IpParser :
	def __init__( self ) :
		self.mEthType			= None
		self.mAddressIp			= '255.255.255.255'
		self.mAddressMask		= '255.255.255.255'
		self.mAddressGateway	= '255.255.255.255'
		self.mAddressNameServer	= '255.255.255.255'


	"""	
	def GetEthdevice( self ) :
		for dev in GetInstalledAdapters( ) :
			if dev.startswith( 'eth' ) :
				if GetAdapterState( dev ) == True :
					return dev
		return None
	"""


	def LoadEthernetType( self ) :
		global gEthernetDevName
		status = False
		try :
			if gEthernetDevName != None :
				inputFile = open( FILE_NAME_INTERFACES, 'r' )
				inputline = inputFile.readlines( )
				for line in inputline :
					if line.startswith( 'iface ' + gEthernetDevName + ' inet' ) :
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


	def LoadEthernetAddress( self ) :
		global gEthernetDevName
		self.mAddressIp, self.mAddressMask, self.mAddressGateway, self.mAddressNameServer = GetNetworkAddress( gEthernetDevName )


	def GetEthernetType( self ) :
		return self.mEthType


	def GetEthernetAddress( self ) :
		return self.mAddressIp, self.mAddressMask, self.mAddressGateway, self.mAddressNameServer


	def SetEthernet( self, aType, aIpAddress=None, aMaskAddress=None, aGatewayAddress=None, aNameAddress=None ) :
		global gEthernetDevName
		status = False
		try :
			inputFile = open( FILE_NAME_INTERFACES, 'r' )
			outputFile = open( FILE_NAME_TEMP_INTERFACES, 'w+' )
			inputline = inputFile.readlines( )
			for line in inputline :
				if line.startswith( 'auto ra0' ) or line.startswith( 'auto wlan0' ) or line.startswith( 'auto eth0' ) :
					outputFile.writelines( 'auto ' + gEthernetDevName + '\n' )
				elif line.startswith( 'iface ' + gEthernetDevName + ' inet' ) :
					if aType == NET_DHCP :
						outputFile.writelines( 'iface ' + gEthernetDevName + ' inet' + ' ' + 'dhcp\n' )
					else :
						outputFile.writelines( 'iface ' + gEthernetDevName + ' inet' + ' ' + 'static\n' )
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
			wifi = WirelessParser( )
			os.system( 'ifdown %s' %  wifi.GetWifidevice( ) )
			os.system( 'ifdown %s' % gEthernetDevName )
			
			time.sleep( 1 )
			os.system( 'ifup %s' % gEthernetDevName )	
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


class WirelessParser :
	def __init__( self ) :
		self.mCurrentSsid	= None
		self.mPassWord		= None
		self.key_mgmt		= None
		self.mEncryptType	= ENCRYPT_TYPE_WPA


	def ResetInfo( self ) :
		self.mCurrentSsid	= None
		self.mPassWord		= None
		self.key_mgmt		= None
		self.mEncryptType	= ENCRYPT_TYPE_WPA


	def LoadWpaSupplicant( self ) :
		self.ResetInfo( )
		if os.path.exists( FILE_WPA_SUPPLICANT ) == False :
			return False
		try :
			openFile = open( FILE_WPA_SUPPLICANT, 'r' )
			inputline = openFile.readlines( )
			for line in inputline :
				line = line.lstrip( )
				if line.startswith( 'ssid=' ) and len( line ) > 6 :
					self.mCurrentSsid = line[ 6 : -2 ]
				elif line.startswith( 'wep_key0="' ) and len( line ) > 11 :
					self.mPassWord = line[ 10 : -2 ]
				elif line.startswith( 'wep_key0=' ) and len( line ) > 9 :
					self.mPassWord = line[ 9 : -1 ]
				elif line.startswith( 'psk="' ) and len( line ) > 6 :
					self.mPassWord = line[ 5 : -2 ]
				elif line.startswith( '#psk="' ) and len( line ) > 6 :
					self.mPassWord = line[ 6 : -2 ]
				elif not self.mPassWord and line.startswith( 'psk=' ) and len( line ) > 4 :
					self.mPassWord = line[ 4 : -1 ]
				elif line.startswith( 'key_mgmt=' ) and len( line ) > 9 :
					self.key_mgmt = line[ 9 : -1 ]
			openFile.close( )
			return True

		except Exception, e :
			if openFile.closed == False :
				openFile.close( )
			LOG_ERR( 'Error exception[%s]' % e )
			return False


	def GetCurrentSsid( self ) :
		if self.mCurrentSsid == None :
			return 'None'
		return self.mCurrentSsid


	def GetPassword( self ) :
		if self.mPassWord == None :
			return ''
		return self.mPassWord


	def GetEncryptType( self ) :
		if self.key_mgmt == 'NONE' :
			if self.mPassWord == None :
				self.mEncryptType = ENCRYPT_OPEN
			else :
				self.mEncryptType = ENCRYPT_TYPE_WEP
		elif self.key_mgmt == "WPA-PSK" :
			self.mEncryptType = ENCRYPT_TYPE_WPA
		else :
			LOG_ERR( 'GetEncryptType Fail!!' )

		return self.mEncryptType


	def GetWifidevice( self ) :
		for dev in GetInstalledAdapters( ) :
			if dev.startswith( 'eth' ) or dev == 'lo':
				continue
			if GetAdapterState( dev ) == True :
				return dev
		return None	


	def ScanWifiAP( self, aDev ) :
		from pythonwifi.iwlibs import Wireless
		import pythonwifi.flags
		status = None
		try :
			scanResult = None
			if GetCurrentNetworkType( ) != NETWORK_WIRELESS :
				os.system( 'ifup %s' % aDev )

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

			if GetCurrentNetworkType( ) != NETWORK_WIRELESS :
				os.system( 'ifdown %s' % aDev )
			return status

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			if GetCurrentNetworkType( ) != NETWORK_WIRELESS :
				os.system( 'ifdown %s' % aDev )
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
				words += "auth_alg=SHARED\n"
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
		global gEthernetDevName	
		try :
			os.system( 'rm -rf ' + FILE_NAME_AUTO_RESOLV_CONF )
			os.system( 'ifdown %s' % aDev )
			time.sleep( 1 )
			os.system( 'ifdown %s' % gEthernetDevName )
			time.sleep( 1 )
			os.system( 'ifup %s' % aDev )			
		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return False

