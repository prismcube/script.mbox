from pvr.gui.GuiConfig import *


FILE_NAME_INTERFACES	 		=	'/etc/network/interfaces'
FILE_NAME_INTERFACES_BAK 		=	'/etc/network/interfaces.bak'
FILE_NAME_TEMP_INTERFACES		= 	'/tmp/interface'
FILE_NAME_RESOLV_CONF			=	'/etc/resolv.conf'
FILE_NAME_AUTO_RESOLV_CONF		=	'/etc/init.d/update-resolv.sh'
FILE_NAME_AUTO_RESOLV_LINK		=	'/etc/rc5.d/S90resolve.conf'
FILE_TEMP						=	'/tmp/ip_temp'
FILE_WPA_SUPPLICANT				=	'/etc/wpa_supplicant/wpa_supplicant.conf'

SYSTEM_COMMAND_GET_GATEWAY		=	"route -n | awk '/^0.0.0.0/ {print $2}'"

COMMAND_COPY_INTERFACES_RESTORE	=	"cp " + FILE_NAME_INTERFACES_BAK + " " + FILE_NAME_INTERFACES
COMMAND_COPY_INTERFACES			=	"cp " + FILE_NAME_TEMP_INTERFACES + " " + FILE_NAME_INTERFACES

gWifiDevName		= 'wlan0'
gEthernetDevName	= 'eth0'
gNetworkType		= NETWORK_ETHERNET

def SetCurrentNetworkType( aType ) :
	global gNetworkType
	gNetworkType = aType


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
		string = aAddress.split( '.', 3 )
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


class IpParser :

	def __init__( self ) :
		self.mEthType			= None
		self.mAddressIp			= '255.255.255.255'
		self.mAddressMask		= '255.255.255.255'
		self.mAddressGateway	= '255.255.255.255'
		self.mAddressNameServer	= '255.255.255.255'


	def GetEthdevice( self ) :
		for dev in GetInstalledAdapters( ) :
			if dev.startswith( 'eth' ) :
				if GetAdapterState( dev ) == True :
					return dev
		return None	


	def LoadNetworkType( self ) :
		global gEthernetDevName
		status = False
		try :
			gEthernetDevName = self.GetEthdevice( )
			if gEthernetDevName != None :
				if os.path.isfile( FILE_NAME_INTERFACES ) == False :
					os.system( COMMAND_COPY_INTERFACES_RESTORE )
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
				if status == False :
					os.system( COMMAND_COPY_INTERFACES_RESTORE )

			else :
				LOG_ERR( 'LoadNetworkType Load Fail!!!' )

			inputFile.close( )
			return status

		except Exception, e :
			if inputFile.closed == False :
				inputFile.close( )
			LOG_ERR( 'Error exception[%s]' % e )
			status = False
			return status


	def LoadNetworkAddress( self ) :
		global gEthernetDevName
		try :
			osCommand = [ "ifconfig %s | awk '/inet / {print $2}' | awk -F: '{print $2}'" % gEthernetDevName + ' > ' + FILE_TEMP, "ifconfig %s | awk '/inet / {print $4}' | awk -F: '{print $2}'" % gEthernetDevName + ' >> ' + FILE_TEMP, SYSTEM_COMMAND_GET_GATEWAY + ' >> ' + FILE_TEMP ]
			
			for command in osCommand :
				time.sleep( 0.01 )
				os.system( command )
			
			time.sleep( 0.02 )
			inputFile = open( FILE_TEMP, 'r' )
			self.mAddressIp = inputFile.readline( ).strip( )
			self.mAddressMask = inputFile.readline( ).strip( )
			self.mAddressGateway = inputFile.readline( ).strip( )
			self.LoadNameServer( )

			if CheckIsIptype( self.mAddressIp ) == False :
				self.mAddressIp = 'None'

			if CheckIsIptype( self.mAddressMask ) == False :
				self.mAddressMask = 'None'

			if CheckIsIptype( self.mAddressGateway ) == False :
				self.mAddressGateway = 'None'

			if CheckIsIptype( self.mAddressNameServer ) == False :
				self.mAddressNameServer = 'None'

			inputFile.close( )
			return True

		except Exception, e :
			if inputFile.closed == False :
				inputFile.close( )
			LOG_ERR( 'Error exception[%s]' % e )
			return False


	def LoadNameServer( self ) :
		try :
			inputFile = open( FILE_NAME_RESOLV_CONF, 'r' )
			inputline = inputFile.readline( )
			words = string.split( inputline )
			self.mAddressNameServer = words[1]
			inputFile.close( )

		except Exception, e :
			if inputFile.closed == False :
				inputFile.close( )
			self.mAddressNameServer = 'None'
			LOG_ERR( 'Error exception[%s]' % e )


	def GetNetworkType( self ) :
		return self.mEthType


	def GetNetworkAddress( self ) :
		return self.mAddressIp, self.mAddressMask, self.mAddressGateway, self.mAddressNameServer


	def SetNetwork( self, aType, aIpAddress=None, aMaskAddress=None, aGatewayAddress=None, aNameAddress=None ) :
		global gEthernetDevName
		global gWifiDevName
		status = False
		try :
			inputFile = open( FILE_NAME_INTERFACES, 'r' )
			outputFile = open( FILE_NAME_TEMP_INTERFACES, 'w+' )
			inputline = inputFile.readlines( )
			for line in inputline :
				if line.startswith( 'iface ' + gEthernetDevName + ' inet' ) :
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

			self.SetNameServer( aType, aNameAddress )
			os.system( COMMAND_COPY_INTERFACES )
			os.system( 'ifdown %s' % gWifiDevName )
			os.system( 'ifdown %s' % gEthernetDevName )
			
			time.sleep( 1 )
			os.system( 'ifup %s'% gEthernetDevName )	
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


	def SetNameServer( self, aType, aNameAddress ) :
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
		self.mPasswordType	= PASSWORD_TYPE_ASCII
		self.mPassWord		= None
		self.key_mgmt		= None
		self.proto			= None
		self.mEncriptType	= ENCRIPT_TYPE_WEP


	def ResetInfo( self ) :
		self.mCurrentSsid	= None
		self.mPasswordType	= PASSWORD_TYPE_ASCII
		self.mPassWord		= None
		self.key_mgmt		= None
		self.proto			= None
		self.mEncriptType	= ENCRIPT_TYPE_WEP
	

	def getWlandevice( self ) :
		global gWifiDevName	
		for dev in GetInstalledAdapters( ) :
			if dev.startswith( 'eth' ) or dev == 'lo':
				continue
			if GetAdapterState( dev ) == True :
				gWifiDevName = dev
				return dev
		return None	


	def ScanAp( self, aDev ) :
		from pythonwifi.iwlibs import Wireless
		import pythonwifi.flags
		status = None
		try :
			scanResult = None
			if GetCurrentNetworkType( ) != NETWORK_WIRELESS :
				os.system( 'ifup %s' % aDev )
			wifi = Wireless( aDev )

			scanResult  = wifi.scan( )
			if scanResult != None :
				apList = []
				for ap in scanResult :
					if len( ap.essid ) > 0 :
						apInfoList = []
						apInfoList.append( ap.essid )
						apInfoList.append( ap.quality.getSignallevel( ) )
						if ap.encode.flags & pythonwifi.flags.IW_ENCODE_DISABLED :
							apInfoList.append( 'No' )
						else :
							apInfoList.append( 'Yes' )
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
					self.mPasswordType = PASSWORD_TYPE_ASCII
					self.mPassWord = line[ 10 : -2 ]
				elif line.startswith( 'wep_key0=' ) and len( line ) > 9 :
					self.mPasswordType = PASSWORD_TYPE_HEX
					self.mPassWord = line[ 9 : -1 ]
				elif line.startswith( 'psk="' ) and len( line ) > 6 :
					self.mPasswordType = PASSWORD_TYPE_ASCII
					self.mPassWord = line[ 5 : -2 ]
				elif line.startswith( '#psk="' ) and len( line ) > 6 :
					self.mPasswordType = PASSWORD_TYPE_HEX
					self.mPassWord = line[ 6 : -2 ]
				elif not self.mPassWord and line.startswith( 'psk=' ) and len( line ) > 4:
					self.mPasswordType = PASSWORD_TYPE_HEX
					self.mPassWord = line[ 4 : -1 ]
				elif line.startswith( 'key_mgmt=' ) and len( line ) > 9 :
					self.key_mgmt = line[ 9 : -1 ]
				elif line.startswith( 'proto=' ) and len( line ) > 6 :
					self.proto = line[ 6 : -1 ]

			openFile.close( )
			return True

		except Exception, e :
			if openFile.closed == False :
				openFile.close( )
			LOG_ERR( 'Error exception[%s]' % e )
			return False


	def WriteWpaSupplicant( self, aUseHiddenId, aHiddenSsid, aCurrentSsid, aUseEncrypt, aEncriptType, aPasswordType, aPassWord ) :
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
			if aUseEncrypt == USE_PASSWORD_ENCRYPT :
				if aEncriptType == ENCRIPT_TYPE_WEP :
					words += "\tkey_mgmt=NONE\n"
					words += "\twep_key0="
					if aPasswordType == PASSWORD_TYPE_ASCII :
						words += "\"" + aPassWord + "\"\n"
					else:
						words += aPassWord + "\n"
				elif aEncriptType == ENCRIPT_TYPE_WPA :
					words += "\tkey_mgmt=WPA-PSK\n"
					words += "\tproto=WPA\n"
					words += "\tpairwise=CCMP TKIP\n"
					words += "\tgroup=CCMP TKIP\n"
					words += "\tpsk=\"" + aPassWord + "\"\n"
				elif aEncriptType == ENCRIPT_TYPE_WPA2 :
					words += "\tkey_mgmt=WPA-PSK\n"
					words += "\tproto=RSN\n"
					words += "\tpairwise=CCMP TKIP\n"
					words += "\tgroup=CCMP TKIP\n"
					words += "\tpsk=\"" + aPassWord + "\"\n"
				else:
					words += "\tkey_mgmt=WPA-PSK\n"
					words += "\tproto=WPA RSN\n"
					words += "\tpairwise=CCMP TKIP\n"
					words += "\tgroup=CCMP TKIP\n"
					words += "\tpsk=\"" + aPassWord + "\"\n"
			else:
				words += "\tkey_mgmt=NONE\n"
			words += "}\n"
			openFile.write( words )
			openFile.close( )
			return True

		except Exception, e :
			if openFile.closed == False :
				openFile.close( )				
			LOG_ERR( 'Error exception[%s]' % e )
			return False


	def ConnectWifi( self, aDev ) :
		global gEthernetDevName	
		try :
			os.system( 'ifdown %s' % aDev )
			time.sleep( 0.5 )
			os.system( 'ifdown %s' % gEthernetDevName )
			time.sleep( 0.5 )
			os.system( 'ifup %s' % aDev )			
		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return False


	def GetCurrentSsid( self ) :
		if self.mCurrentSsid == None :
			return 'None'
		return self.mCurrentSsid


	def GetPasswordType( self ) :
		return self.mPasswordType


	def GetPassword( self ) :
		if self.mPassWord == None :
			return ''
		return self.mPassWord


	def GetUseEncrypt( self ) :
		if self.mPassWord == None :
			return NOT_USE_PASSWORD_ENCRYPT
		else :
			return USE_PASSWORD_ENCRYPT


	def GetEncryptType( self ) :
		if self.key_mgmt == 'NONE' :
			self.mEncriptType = ENCRIPT_TYPE_WEP
		elif self.key_mgmt == "WPA-PSK" :
			if self.proto == "WPA" :
				self.mEncriptType = ENCRIPT_TYPE_WPA
			elif self.proto == "RSN" :
				self.mEncriptType = ENCRIPT_TYPE_WPA2
			elif self.proto in ( "WPA RSN", "WPA WPA2" ) :
				self.mEncriptType = ENCRIPT_TYPE_WPA_WPA2
			else :
				self.mEncriptType = ENCRIPT_TYPE_WPA
		else :
			self.mEncriptType = ENCRIPT_TYPE_WEP
			
		return self.mEncriptType
