from pvr.gui.GuiConfig import *
from subprocess import *
from pvr.Util import RunThread


FILE_NAME_INTERFACES	 		=	'/etc/network/interfaces'
FILE_NAME_TEMP_INTERFACES		= 	'/mtmp/interface'
FILE_NAME_RESOLV_CONF			=	'/etc/resolv.conf'
FILE_TEMP						=	'/mtmp/ip_temp'
FILE_WPA_SUPPLICANT				=	'/etc/wpa_supplicant/wpa_supplicant.conf'
SYSTEM_COMMAND_GET_GATEWAY		=	"route -n | awk '/^0.0.0.0/ {print $2}'"

COMMAND_COPY_INTERFACES			=	"cp " + FILE_NAME_TEMP_INTERFACES + " " + FILE_NAME_INTERFACES
COMMAND_COPY_CONFIG_INTERFACES	=	"cp " + FILE_NAME_TEMP_INTERFACES + " " + '/config/interfaces'
COMMAND_COPY_CONFIG_WPA_SUPPLICANT	= "cp " + FILE_WPA_SUPPLICANT + " " + '/config/wpa_supplicant.conf'
COMMAND_COPY_CONFIG_RESOLVE_CONF	= "cp " + FILE_NAME_RESOLV_CONF + " " + '/config/resolv.conf'

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
		self.mEthernetDevName	= 'eth0'
		self.mIsConfigureWindow	= False
		if E_USE_AUTO_CONNECT :
			self.CheckNetworkThread( )


	def IfUpDown( self, aDev ) :
		os.system( 'wpa_cli terminate' )
		os.system( 'touch /mtmp/iftest_%s' % aDev )
		time.sleep( 1 )
		for i in range( 20 ) :
			if os.path.exists( '/mtmp/iftest_%s' % aDev ) :
				time.sleep( 1 )
			else :
				break


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


	def GetNetworkAddress( self, aType ) :
		if aType == NETWORK_ETHERNET :
			dev = self.mEthernetDevName
		else :
			dev = self.GetWifidevice( )
		addressIp = 'None'
		addressMask = 'None'
		addressGateway = 'None'
		addressNameServer = 'None'
		try :
			inputFile = None
			osCommand = [ "ifconfig %s | awk '/inet / {print $2}' | awk -F: '{print $2}'" % dev + ' > ' + FILE_TEMP, "ifconfig %s | awk '/inet / {print $4}' | awk -F: '{print $2}'" % dev + ' >> ' + FILE_TEMP, SYSTEM_COMMAND_GET_GATEWAY + ' >> ' + FILE_TEMP ]

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


	def SetNetworkProperty( self, aAddress, aNetmask, aGateway, aNameserver ) :
		from elisinterface.ElisProperty import ElisPropertyInt
		import pvr.ElisMgr
		command = pvr.ElisMgr.GetInstance( ).GetCommander( )

		if self.CheckIsIptype( aAddress ) == True :
			ElisPropertyInt( 'IpAddress' , command ).SetProp( MakeStringToHex( aAddress ) )
			make = ElisPropertyInt( 'IpAddress' , command ).GetProp( )
			make_1, make_2, make_3, make_4 = MakeHexToIpAddr( make )

		if self.CheckIsIptype( aNetmask ) == True :
			ElisPropertyInt( 'SubNet' , command ).SetProp( MakeStringToHex( aNetmask ) )
			make = ElisPropertyInt( 'SubNet' , command ).GetProp( )
			make_1, make_2, make_3, make_4 = MakeHexToIpAddr( make )

		if self.CheckIsIptype( aGateway ) == True :
			ElisPropertyInt( 'Gateway' , command ).SetProp( MakeStringToHex( aGateway ) )
			make = ElisPropertyInt( 'Gateway' , command ).GetProp( )
			make_1, make_2, make_3, make_4 = MakeHexToIpAddr( make )

		if self.CheckIsIptype( aNameserver ) == True :
			ElisPropertyInt( 'DNS' , command ).SetProp( MakeStringToHex( aNameserver ) )
			make = ElisPropertyInt( 'DNS' , command ).GetProp( )
			make_1, make_2, make_3, make_4 = MakeHexToIpAddr( make )


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

	
	def ConnectEthernet( self, aType, aIpAddress=None, aMaskAddress=None, aGatewayAddress=None, aNameAddress=None ) :
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
						outputFile.writelines( 'address %s\n' % aIpAddress.strip( ) )
						outputFile.writelines( 'netmask %s\n' % aMaskAddress.strip( ) )
						outputFile.writelines( 'gateway %s\n' % aGatewayAddress.strip( ) )
				elif line.startswith( 'address' ) or line.startswith( 'netmask' ) or line.startswith( 'gateway' ) :
					continue
				else :
					outputFile.writelines( line )

			inputFile.close( )
			outputFile.close( )

			self.SetEthernetNameServer( aType, aNameAddress )
			os.system( COMMAND_COPY_INTERFACES )
			os.system( COMMAND_COPY_CONFIG_INTERFACES )
			self.IfUpDown( self.mEthernetDevName )
			status = True
			inputFile.close( )
			outputFile.close( )
			os.system( 'sync' )
			return status

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			status = False
			if inputFile.closed == False :
				inputFile.close( )
			if outputFile.closed == False :
				outputFile.close( )
			return status


	def DisConnectWifi( self ) :
		return


	def DeleteConfigFile( self ) :
		return


	def WriteEthernetConfig( self, aMethod, aAddress=None, aNetmask=None, aGateway=None, aNameServer=None ) :
		return


	def GetCurrentWifiService( self ) :
		return None


	def SetServiceConnect( self, aService, aFlag ) :
		return True


	def SetAutoConnect( self, aService, aFlag ) :
		return True


	def DisConnectEthernet( self ) :
		return


	def VerifiedState( self, aService ) :
		return True


	def LoadSetWifiTechnology( self ) :
		if self.GetWifidevice( ) :
			return True
		else :
			return False


	def LoadEthernetService( self ) :
		return


	def ResetNetwork( self ) :
		if self.GetCurrentServiceType( ) == NETWORK_WIRELESS or self.GetEthernetMethod( ) == NET_STATIC :
			self.ConnectEthernet( NET_DHCP )


	def LoadWifiService( self ) :
		return


	def SetEthernetNameServer( self, aType, aNameAddress ) :
		try :
			if aType == NET_DHCP :
				os.system( 'rm -rf /config/resolv.conf' )
			else :
				os.system( 'echo nameserver %s' % aNameAddress.strip( ) + '> ' + FILE_NAME_RESOLV_CONF )
				os.system( COMMAND_COPY_CONFIG_RESOLVE_CONF )
			return True
			
		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return False


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


	def GetWifiEncryptType( self ) :
		enc = self.GetEncryptType( )
		if enc == 'NONE' :
			if self.GetConfiguredPassword( ) == None :
				return ENCRYPT_OPEN
			else :
				return ENCRYPT_TYPE_WEP
		elif enc == "WPA-PSK" :
			return ENCRYPT_TYPE_WPA
		else :
			LOG_ERR( 'GetEncryptType failed!!' )
			return ENCRYPT_TYPE_WPA
	
	
	def GetEncryptType( self ) :
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


	def GetSearchedWifiApList( self ) :
		dev = self.GetWifidevice( )
		from pythonwifi.iwlibs import Wireless
		import pythonwifi.flags
		try :
			scanResult = []
			if self.GetCurrentServiceType( ) != NETWORK_WIRELESS :
				self.IfUpDown( dev + '_up' )
				time.sleep( 3 )

			os.system( 'iwlist %s scan > %s' % ( dev, FILE_TEMP ) )
			from IwlistParser import Get_ApList
			scanResult = Get_ApList( )
			
			if len( scanResult ) > 0 :
				apList = []
				for ap in scanResult :
					apInfoList = []
					if len( ap[0] ) > 0 :
						apInfoList.append( ap[0] )
						apInfoList.append( ap[1] )
						apInfoList.append( ap[2] )
						apList.append( apInfoList )
				if apList :
					scanResult = apList 
				else :
					scanResult = []

			if self.GetCurrentServiceType( ) != NETWORK_WIRELESS :
				self.IfUpDown( dev + '_down' )
			return scanResult

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			if self.GetCurrentServiceType( ) != NETWORK_WIRELESS :
				self.IfUpDown( dev + '_down' )
			return []


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
				words += "\tauth_alg=LEAP\n"
			elif aEncryptType == ENCRYPT_TYPE_WPA :
				words += "\tkey_mgmt=WPA-PSK\n"
				words += "\tpsk=\"" + aPassWord + "\"\n"
			else:
				words += "\tkey_mgmt=NONE\n"
			words += "}\n"
			openFile.write( words )
			openFile.close( )
			os.system( COMMAND_COPY_CONFIG_WPA_SUPPLICANT )
			self.WriteInterfaces( )
			os.system( 'sync' )
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
			os.system( COMMAND_COPY_CONFIG_INTERFACES )
			os.system( 'sync' )

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			if inputFile.closed == False :
				inputFile.close( )
			if outputFile.closed == False :
				outputFile.close( )


	def ConnectWifi( self ) :
		dev = self.GetWifidevice( )
		try :
			self.IfUpDown( dev )
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
			LOG_ERR( 'Could not find wifi device' )


	def GetWifiUseHiddenSsid( self ) :
		try :
			if os.path.exists( FILE_WPA_SUPPLICANT ) :
				openFile = open( FILE_WPA_SUPPLICANT, 'r' )
				inputline = openFile.readlines( )
				for line in inputline :
					if line.startswith( '\tscan_ssid=1' ) :
						openFile.close( )
						return USE_HIDDEN_SSID

				openFile.close( )
				return NOT_USE_HIDDEN_SSID

			else :
				LOG_ERR( '%s path is not exist' % FILE_WPA_SUPPLICANT )
				return NOT_USE_HIDDEN_SSID

		except Exception, e :
			if openFile.closed == False :
				openFile.close( )
			LOG_ERR( 'Error exception[%s]' % e )
			return NOT_USE_HIDDEN_SSID


	def WriteWifiInterfaces( self, aIsStatic, aIpAddress = None, aMaskAddress = None, aGatewayAddress = None, aNameAddress = None ) :
		try :
			dev = self.GetWifidevice( )
			inputFile = open( FILE_NAME_INTERFACES, 'r' )
			outputFile = open( FILE_NAME_TEMP_INTERFACES, 'w+' )
			inputline = inputFile.readlines( )
			for line in inputline :
				if line.startswith( 'iface ' + dev + ' inet' ) :
					if aIsStatic :
						outputFile.writelines( 'iface ' + dev + ' inet' + ' ' + 'static\n' )
						outputFile.writelines( '\taddress %s\n' % aIpAddress.strip( ) )
						outputFile.writelines( '\tnetmask %s\n' % aMaskAddress.strip( ) )
						outputFile.writelines( '\tgateway %s\n' % aGatewayAddress.strip( ) )
					else :
						outputFile.writelines( 'iface ' + dev + ' inet' + ' ' + 'dhcp\n' )

				elif line.startswith( '\taddress' ) or line.startswith( '\tnetmask' ) or line.startswith( '\tgateway' ) :
					continue
				else :
					outputFile.writelines( line )

			inputFile.close( )
			outputFile.close( )

			self.SetEthernetNameServer( aIsStatic, aNameAddress )
			os.system( COMMAND_COPY_INTERFACES )
			os.system( COMMAND_COPY_CONFIG_INTERFACES )
			status = True
			inputFile.close( )
			outputFile.close( )
			os.system( 'sync' )
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


	####### Network Check and Auto Connect Thread Area ######


	def SetIsConfigureWindow( self, aFlag ) :
		self.mIsConfigureWindow = aFlag


	def GetIsConfigureWindow( self ) :
		return self.mIsConfigureWindow


	@RunThread
	def CheckNetworkThread( self ) :
		print 'dhkim test start thread'
		print 'dhkim test start thread'
		print 'dhkim test start thread'		
		time.sleep( 20 )
		sleeptime = 3
		testcount = 0
		checkcount = 0
		while True :
			print 'dhkim test in thread'
			if self.GetIsConfigureWindow( ) == False :
				networkType = self.GetCurrentServiceType( )
				print 'dhkim test networkType = %s' % networkType
				devicestate = self.CheckDeviceState( networkType )
				print 'dhkim test devicestate = %s' % devicestate
				if devicestate :
					print 'dhkim test CheckDefaultGatewayConnection........' 
					if self.CheckDefaultGatewayConnection( ) :
						print 'dhkim test check connect ok...so pass reconnect process...'
						pass
					else :
						print 'dhkim test reconnect start'
						self.ReConnectNetwork( networkType )
						testcount += 1
						print 'dhkim test reconnect end'

			print 'dhkim test sleep 3 sec.....'
			time.sleep( sleeptime )
			checkcount += 1
			print 'dhkim test result checkcount count = #######%s' % checkcount
			print 'dhkim test result reconnect count = #######%s' % testcount


	def CheckDeviceState( self, aType ) :
		if aType == NETWORK_WIRELESS :
			devicestate = self.CheckWifidevice( )
		else :
			devicestate = self.CheckEthernetdevice( )

		return devicestate
		

	def CheckWifidevice( self ) :
		for dev in self.GetInstalledAdapters( ) :
			if dev.startswith( 'eth' ) or dev == 'lo':
				continue
			if self.GetAdapterState( dev ) == True :
				return True
		return False


	def CheckEthernetdevice( self ) :
		cmd = 'cat /sys/class/net/eth0/operstate'

		try :
			if sys.version_info < ( 2, 7 ) :
				p = Popen( cmd, shell=True, stdout=PIPE )
				state = p.stdout.read( ).strip( )
				p.stdout.close( )
			else :
				p = Popen( cmd, shell=True, stdout=PIPE, close_fds=True )
				( state, err ) = p.communicate( )
				state = state.strip( )
		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return False

		if state == 'down' :
			return False
		else :
			return True


	def CheckDefaultGatewayConnection( self ) :
		defultGatewayAddress = None
		cmd  = "route -n | awk '/^0.0.0.0/ {print $2}'"

		try :
			if sys.version_info < ( 2, 7 ) :
				p = Popen( cmd, shell=True, stdout=PIPE )
				defultGatewayAddress = p.stdout.read( ).strip( )
				p.stdout.close( )
			else :
				p = Popen( cmd, shell=True, stdout=PIPE, close_fds=True )
				( defultGatewayAddress, err ) = p.communicate( )
				defultGatewayAddress = defultGatewayAddress.strip( )
		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return True

		cmd = 'ping -c 3 %s' % defultGatewayAddress
		os.system( '%s > %s' % ( cmd, FILE_TEMP ) )

		try :
			inputFile = open( FILE_TEMP, 'r' )
			inputline = inputFile.readlines( )
			result = False

			for line in inputline :
				if line.startswith( '3 packets' ) :
					words = line.split( ',' )
					result = words[1].strip( )
					break
			inputFile.close( )

			if result == '3 packets received' :
				return True
			else :
				return False

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			if inputFile.closed == False :
				inputFile.close( )
			return False


	def ReConnectNetwork( self, aType ) :
		if aType == NETWORK_WIRELESS :
			self.ConnectWifi( )
		else :
			self.IfUpDown( self.mEthernetDevName )
