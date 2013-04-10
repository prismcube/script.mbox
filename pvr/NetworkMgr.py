from pvr.gui.GuiConfig import *


gUseNetwork = True

try :
	import dbus
except :
	gUseNetwork = False


gNetworkMgr					= None
CONFIGURATION_TIMEOUT		= 10

NETWORK_CONFIG_PATH			= '/config/network.config'
WIFI_CONFIGURED_PATH		= '/var/lib/connman/wifi.config'


def GetInstance( ) :
	global gNetworkMgr
	if not gNetworkMgr :
		gNetworkMgr = NetworkMgr( )
		import pvr
		global gUseNetwork
		if not pvr.Platform.GetPlatform( ).IsRootfUbiFs( ) :
			gUseNetwork = False

	else :
		pass

	return gNetworkMgr


class NetworkMgr( object ) :
	def __init__( self ) :
		self.mEthernetServiceObejct		= None
		self.mWifiTechnologyObject		= None
		self.mWifiServiceObejct			= None
		self.mBusyConfigFile			= False


	def ResetNetwork( self ) :
		self.WriteEthernetConfig( NET_DHCP )
		self.ConnectEthernet( NET_DHCP )
		time.sleep( 1 )
		self.DisConnectWifi( )
		self.DeleteConfigFile( )
		time.sleep( 1 )


	def GetCurrentServiceType( self ) :
		if gUseNetwork == False :
			return NETWORK_ETHERNET

		try :
			nettype = NETWORK_ETHERNET
			if os.path.exists( NETWORK_CONFIG_PATH ) :
				self.mBusyConfigFile = True
				inputFile = open( NETWORK_CONFIG_PATH, 'r' )
				inputline = inputFile.readlines( )
				for line in inputline :
					if line.startswith( 'networktype' ) :
						word = string.split( line )[2]
						if word != 'ethernet' :
							nettype = NETWORK_WIRELESS

				inputFile.close( )
				self.mBusyConfigFile = False
				return nettype
			else :
				LOG_ERR( '%s path is not exist' % WIFI_CONFIGURED_PATH )
				return NETWORK_ETHERNET

		except Exception, e :
			if inputFile.closed == False :
				inputFile.close( )
			self.mBusyConfigFile = False
			LOG_ERR( 'Error exception[%s]' % e )
			return NETWORK_ETHERNET


	def WriteEthernetConfig( self, aMethod, aAddress=None, aNetmask=None, aGateway=None, aNameServer=None ) :
		if gUseNetwork == False :
			return False

		try :
			self.mBusyConfigFile = True
			openFile = open( NETWORK_CONFIG_PATH, 'w' )
			words = 'networktype = ethernet\n'
			if aMethod == NET_DHCP :
				words += 'method = dhcp\n'
			else :
				words += 'method = static\n'
				words += 'address = %s\n' % aAddress
				words += 'netmask = %s\n' % aNetmask
				words += 'gateway = %s\n' % aGateway
				words += 'nameserver = %s\n' % aNameServer

			openFile.write( words )
			openFile.close( )
			self.mBusyConfigFile = False
			time.sleep( 0.5 )
			return True

		except Exception, e :
			self.mBusyConfigFile = False
			LOG_ERR( 'WriteEthernetConfig Error exception[%s]' % e )
			return False


	def WriteWifiConfig( self, aSSID, aPassword, aIsHidden ) :
		if gUseNetwork == False :
			return False

		try :
			self.mBusyConfigFile = True
			openFile = open( NETWORK_CONFIG_PATH, 'w' )
			words = 'networktype = wifi\n'
			words += 'ssid = ' + aSSID + '\n'
			if aPassword != '' :
				words += 'passphrase = ' + aPassword + '\n'
			if aIsHidden == USE_HIDDEN_SSID :
				words += 'hidden = True\n'
			else :
				words += 'hidden = False\n'

			openFile.write( words )
			openFile.close( )
			self.mBusyConfigFile = False
			time.sleep( 0.5 )
			return True

		except Exception, e :
			self.mBusyConfigFile = False
			LOG_ERR( 'WriteWifiConfig Error exception[%s]' % e )
			return False


	def GetCurrentServiceObject( self ) :
		if self.GetCurrentServiceType( ) == NETWORK_ETHERNET :
			return self.mEthernetServiceObejct
		else :
			return self.mWifiServiceObejct


	def GetCurrentEthernetService( self ) :
		return self.mEthernetServiceObejct


	def GetCurrentWifiService( self ) :
		return self.mWifiServiceObejct


	def LoadEthernetService( self ) :
		if gUseNetwork == False :
			return False
			
		try :
			ethernetServicePath = None
			self.mEthernetServiceObejct = None
			bus = dbus.SystemBus( )
			manager = dbus.Interface( bus.get_object( 'net.connman', '/' ), 'net.connman.Manager' )
			services = manager.GetServices( )

			for entry in services :
				properties = entry[1]
				for key in properties.keys( ) :
					if properties['Type'] == 'ethernet' :
						ethernetServicePath = entry[0]
						break

			if ethernetServicePath :
				self.mEthernetServiceObejct = dbus.Interface( bus.get_object( 'net.connman', ethernetServicePath ), 'net.connman.Service' )
				return True
			else :
				return False

		except dbus.DBusException, error :
			ethernetServicePath = None
			self.mEthernetServiceObejct = None
			LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )
			return False


	def LoadWifiService( self ) :
		if gUseNetwork == False :
			return False

		try :
			self.mWifiServiceObejct = None
			SSID = self.GetConfiguredSSID( )
			LOG_TRACE( 'LoadWifiService ssid = %s' % SSID )
			if SSID :
				path = self.GetConfiguredWifiServicePath( SSID )
				LOG_TRACE( 'LoadWifiService path = %s' % path )
				if path :
					bus = dbus.SystemBus( )
					self.mWifiServiceObejct = dbus.Interface( bus.get_object( 'net.connman', path ), 'net.connman.Service' )
					return True
				else :
					return False

		except dbus.DBusException, error :                                  
			LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )
			return False


	def LoadSetWifiTechnology( self ) :
		if gUseNetwork == False :
			return False

		self.mWifiTechnologyObject = None
		wifiTechnologyPath = None
		try :
			bus = dbus.SystemBus( )
			manager = dbus.Interface( bus.get_object( 'net.connman', '/' ), 'net.connman.Manager' )

			technologies = manager.GetTechnologies( )
			for entry in technologies :
				properties = entry[1]
				for key in properties.keys( ) :
					if properties['Type'] == 'wifi' :
						wifiTechnologyPath = entry[0]
						break

			if wifiTechnologyPath :
				self.mWifiTechnologyObject = dbus.Interface( bus.get_object( 'net.connman', wifiTechnologyPath ), 'net.connman.Technology' )
				if self.GetWifiTechnologyPower( ) == False :
					self.SetWifiTechnologyPower( True )
				return True
			else :
				return False

		except dbus.DBusException, error :
			self.mWifiTechnologyObject = None
			wifiTechnologyPath = None
			LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )
			return False


	def GetWifiTechnologyPower( self ) :
		if gUseNetwork == False :
			return True

		try :
			if self.mWifiTechnologyObject :
				property = self.mWifiTechnologyObject.GetProperties( )
				if property['Powered'] == 1 :
					return True
				else :
					return False
			else :
				LOG_ERR( 'mWifiTechnologyObject is None' )
				return True

		except dbus.DBusException, error :                                  
			LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )
			return True


	def SetWifiTechnologyPower( self, aFlag ) :
		if gUseNetwork == False :
			return

		try :
			if self.mWifiTechnologyObject :
				self.mWifiTechnologyObject.SetProperty( 'Powered', aFlag )
				for i in range( CONFIGURATION_TIMEOUT ) :
					time.sleep( 1 )
					property = self.mWifiTechnologyObject.GetProperties( )
					if property['Powered'] == True :
						time.sleep( 5 )
						return
			else :
				LOG_ERR( 'wifiTechnologyObject is None' )

		except dbus.DBusException, error :                                  
			LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )
		

	def GetConfiguredSSID( self ) :
		if gUseNetwork == False :
			return None

		try :
			if os.path.exists( NETWORK_CONFIG_PATH ) :
				inputFile = open( NETWORK_CONFIG_PATH, 'r' )
				inputline = inputFile.readlines( )
				for line in inputline :
					if line.startswith( 'ssid' ) :
						words = string.split( line )
						inputFile.close( )
						return words[2]

				inputFile.close( )
				return None

			else :
				LOG_ERR( '%s path is not exist' % NETWORK_CONFIG_PATH )
				return None

		except Exception, e :
			if inputFile.closed == False :
				inputFile.close( )
			LOG_ERR( 'Error exception[%s]' % e )
			return None


	def GetConfiguredPassword( self ) :
		if gUseNetwork == False :
			return None

		try :
			if os.path.exists( NETWORK_CONFIG_PATH ) :
				inputFile = open( NETWORK_CONFIG_PATH, 'r' )
				inputline = inputFile.readlines( )
				for line in inputline :
					if line.startswith( 'passphrase' ) :
						words = string.split( line )
						inputFile.close( )
						return words[2]

				inputFile.close( )
				return None
			else :
				LOG_ERR( '%s path is not exist' % NETWORK_CONFIG_PATH )
				return None

		except Exception, e :
			if inputFile.closed == False :
				inputFile.close( )
			LOG_ERR( 'Error exception[%s]' % e )
			return None


	def GetIsConfiguredHiddenSSID( self ) :
		if gUseNetwork == False :
			return None

		try :
			if os.path.exists( NETWORK_CONFIG_PATH ) :
				inputFile = open( NETWORK_CONFIG_PATH, 'r' )
				inputline = inputFile.readlines( )
				for line in inputline :
					if line.startswith( 'hidden' ) :
						return True
				inputFile.close( )
				return False
			else :
				LOG_ERR( '%s path is not exist' % NETWORK_CONFIG_PATH )
				return False

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return False


	def GetWifiEncryptType( self ) :
		print 'dhkim test todo!'
		return ENCRYPT_TYPE_WPA


	def GetWifiUseStatic( self ) :
		print 'dhkim test todo!'
		return NET_DHCP


	def WriteWifiConfigFile( self, aSSID, aPassword, aIsHidden ) :
		if gUseNetwork == False :
			return False

		try :
			openFile = open( WIFI_CONFIGURED_PATH, 'w' )
			words = '[service_home]\n'
			words += 'Type = wifi\n'
			words += 'Name = ' + aSSID + '\n'
			if aPassword != '' :
				words += 'Passphrase = ' + aPassword + '\n'
			if aIsHidden == USE_HIDDEN_SSID :
				words += 'Hidden = True\n'

			openFile.write( words )
			openFile.close( )
			time.sleep( 1 )
			return True

		except Exception, e :				
			LOG_ERR( 'WriteWifiConfigFile Error exception[%s]' % e )
			return False


	def GetConfiguredWifiServicePath( self, aSSID ) :
		if gUseNetwork == False :
			return None

		aplist = self.GetSearchedWifiApList( )

		if len( aplist ) > 0 :
			for ap in aplist :
				if str( ap[0] ) == aSSID :
					LOG_TRACE( 'Find matched SSID = %s' % ap[0] )
					return ap[1]

		LOG_ERR( 'GetConfiguredWifiServicePath is None' )
		return None


	def GetSearchedWifiApList( self ) :
		if gUseNetwork == False :
			return []

		try :
			bus = dbus.SystemBus( )
			manager = dbus.Interface( bus.get_object( 'net.connman', '/' ), 'net.connman.Manager' )

			servicelist = []
			for path, properties in manager.GetServices( ) :
				if properties[ 'Type' ] == 'wifi' :
					
					if 'Name' in properties.keys( ) :
						name = properties[ 'Name' ]
					else:
						name = '{Hidden}'

					Security = None
					if 'Security' in properties.keys( ) :
						Security = '['
						for i in properties[ 'Security' ] :
							Security += ' ' + str( i )
						Security += ' ]'
					servicelist.append( [ name, str( int ( properties[ 'Strength' ] ) ), Security, path ] )

			LOG_TRACE( 'GetSearchedWifiApList = %s' % servicelist )
			return servicelist

		except dbus.DBusException, error :                                  
			LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )
			return []


	def SetAutoConnect( self, aService, aFlag ) :
		if gUseNetwork == False :
			return False

		try :
			if aService :
				aService.SetProperty( 'AutoConnect', aFlag )
				time.sleep( 0.5 )

		except dbus.DBusException, error :                                  
			LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )
			return False


	def DeleteConfigFile( self ) :
		try :
			os.system( 'rm -rf /var/lib/connman/wifi*' )

		except Exception, e :				
			print 'WriteWifiConfigFile Error exception[%s]' % e


	def GetServiceState( self, aService ) :
		if gUseNetwork == False :
			return False

		try :
			if aService :
				property = aService.GetProperties( )
				if property['State'] == 'idle' or property['State'] == 'disconnect' :
					return False
				elif property['State'] == 'ready' or property['State'] == 'online' :
					return True
			else :
				LOG_ERR( 'service is empty' )
				return None

		except dbus.DBusException, error :                                  
			LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )
			return False


	def SetServiceConnect( self, aService, aFlag ) :
		if gUseNetwork == False :
			return False
	
		try :
			if aService :
				if aFlag :
					aService.Connect( timeout=60000 )
					time.sleep( 1 )
					self.WaitConfigurationService( aService )
				else :
					aService.Disconnect( )
					time.sleep( 1 )
					self.WaitConfigurationService( aService )

				return True
			else :
				return False

		except dbus.DBusException, error :                                  
			LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )
			return False


	def DisConnectEthernet( self ) :
		try :
			self.LoadEthernetService( )
			if self.mEthernetServiceObejct :
				self.SetServiceConnect( self.mEthernetServiceObejct, False )
				self.mEthernetServiceObejc = None

		except dbus.DBusException, error :                                  
			LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )


	def DisConnectWifi( self ) :
		try :
			if self.LoadSetWifiTechnology( ) :
				if self.LoadWifiService( ) :
					if self.mWifiServiceObejct :
						self.SetServiceConnect( self.mWifiServiceObejct, False )
						self.mWifiServiceObejct = None

		except dbus.DBusException, error :                                  
			LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )


	def ApInfoToEncrypt( self, aType ) :
		print 'dhkim test Todo'
		print 'dhkim test type = %s' % aType
		if aType == 'No' :
			return ENCRYPT_OPEN
		elif aType == 'WPA' :
			return ENCRYPT_TYPE_WPA
		elif aType == 'WEP' :
			return ENCRYPT_TYPE_WEP
		else :
			LOG_ERR( 'ApInfoToEncrypt Fail!!' )
			return ENCRYPT_TYPE_WPA


	def GetWifiUseHiddenSsid( self ) :
		print 'dhkim test todo'
		return NOT_USE_HIDDEN_SSID


	"""
	def GetServiceAddress( self, aService ) :
		address		= 'None'
		netmask		= 'None'
		gateway		= 'None'
		nameserver	= 'None'

		if gUseNetwork == False :
			return 'None', 'None', 'None', 'None'

		if aService :
			try :
				self.WaitConfigurationService( aService )

				property = aService.GetProperties( )
				for key in property.keys( ) :
					if key == 'Nameservers' :
						if len( property[key] ) != 0 :
							nameserver = property[key][0]
						else :
							LOG_ERR( 'Name server empty!!' )
					elif key == 'IPv4' :
						for val in property[key].keys( ) :
							if val == 'Address' :
								address = property[key][val]
							elif val == 'Netmask' :
								netmask = property[key][val]
							elif val == 'Gateway' :
								gateway = property[key][val]

				return self.CheckChangeIpType( address, netmask, gateway, nameserver )

			except dbus.DBusException, error :                                  
				LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )
				return 'None', 'None', 'None', 'None'

		else :
			return 'None', 'None', 'None', 'None'
	"""
	def GetNetworkAddress( self, aType ) :
		address		= 'None'
		netmask		= 'None'
		gateway		= 'None'
		nameserver	= 'None'

		if gUseNetwork == False :
			return 'None', 'None', 'None', 'None'

		if aType == NETWORK_ETHERNET :
			service = self.GetCurrentEthernetService( )
		else :
			service = self.GetCurrentWifiService( )

		if service :
			try :
				self.WaitConfigurationService( service )

				property = aService.GetProperties( )
				for key in property.keys( ) :
					if key == 'Nameservers' :
						if len( property[key] ) != 0 :
							nameserver = property[key][0]
						else :
							LOG_ERR( 'Name server empty!!' )
					elif key == 'IPv4' :
						for val in property[key].keys( ) :
							if val == 'Address' :
								address = property[key][val]
							elif val == 'Netmask' :
								netmask = property[key][val]
							elif val == 'Gateway' :
								gateway = property[key][val]

				return self.CheckChangeIpType( address, netmask, gateway, nameserver )

			except dbus.DBusException, error :                                  
				LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )
				return 'None', 'None', 'None', 'None'

		else :
			return 'None', 'None', 'None', 'None'


	def ConnectEthernet( self, aMethod, aAddress=None, aNetmask=None, aGateway=None, aNameServer=None ) :
		if gUseNetwork == False :
			return False
	
		try :
			if self.LoadEthernetService( ) :
				if self.mEthernetServiceObejct :
					if aMethod == NET_DHCP :
						ipv4_configuration = { 'Method': dbus.String( 'dhcp', variant_level = 1 ) }
					else :
						ipv4_configuration = { 'Method': dbus.String( 'manual', variant_level = 1 ) }
						ipv4_configuration[ 'Address'] = dbus.String( aAddress, variant_level = 1 )
						ipv4_configuration[ 'Netmask'] = dbus.String( aNetmask, variant_level = 1 )
						ipv4_configuration[ 'Gateway'] = dbus.String( aGateway, variant_level = 1 )
						self.mEthernetServiceObejct.SetProperty( 'Nameservers.Configuration', dbus.Array( [ aNameServer ], signature = dbus.Signature( 's' ) ) )
						time.sleep( 0.5 )

					self.mEthernetServiceObejct.SetProperty( 'IPv4.Configuration', ipv4_configuration )
					time.sleep( 1 )

					if self.GetServiceState( self.mEthernetServiceObejct ) == False :
						if self.SetServiceConnect( self.mEthernetServiceObejct, True ) == False :
							return False
					return True
				else :
					return False
			else :
				return False

		except dbus.DBusException, error :                                  
			LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )
			return False


	def GetEthernetMethod( self ) :
		if gUseNetwork == False :
			return NET_DHCP

		try :
			nettype = NET_DHCP
			if os.path.exists( NETWORK_CONFIG_PATH ) :
				self.mBusyConfigFile = True
				inputFile = open( NETWORK_CONFIG_PATH, 'r' )
				inputline = inputFile.readlines( )
				for line in inputline :
					if line.startswith( 'method' ) :
						word = string.split( line )[2]
						if word != 'dhcp' :
							nettype =  NET_STATIC

				inputFile.close( )
				self.mBusyConfigFile = False
				return nettype
			else :
				LOG_ERR( '%s path is not exist' % WIFI_CONFIGURED_PATH )
				return nettype

		except Exception, e :
			if inputFile.closed == False :
				inputFile.close( )
			self.mBusyConfigFile = False
			LOG_ERR( 'Error exception[%s]' % e )
			return NET_DHCP


	def WaitConfigurationService( self, aService ) :
		if aService :
			try :
				for i in range( CONFIGURATION_TIMEOUT ) :
					time.sleep( 1 )
					try :
						property = aService.GetProperties( )
						if property['State'] != 'configuration' and property['State'] != 'association' :
							return

					except dbus.DBusException, error :                                  
						LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )

				time.sleep( 1 )

			except dbus.DBusException, error :                                  
				LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )


	def CheckInternetState( self ) :
		if gUseNetwork == False :
			return 'Disconnected'

		if self.mBusyConfigFile :
			return 'Busy CF'

		service = self.GetCurrentServiceObject( )
		if service :
			try :
				property = service.GetProperties( )
				if property['State'] == 'failure' :
					LOG_ERR( 'Internet State error = %s' % property['Error'] )
				
				if property['State'] != 'configuration' :
					if property['State'] == 'online' :
						return 'Connected'
					else :
						return 'Disconnected'
				else :
					return 'Busy'
			except dbus.DBusException, error :    
				return 'Disconnected'
				LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )

		else :
			return 'Disconnected'


	def SetNetworkProperty( self, aAddress, aNetmask, aGateway, aNameserver ) :
		from ElisProperty import ElisPropertyInt
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


	def CheckChangeIpType( self, aAddress, aNetmask, aGateway, aNameserver ) :
		if self.CheckIsIptype( aAddress ) == False :
			aAddress = 'None'

		if self.CheckIsIptype( aNetmask ) == False :
			aNetmask = 'None'

		if self.CheckIsIptype( aGateway ) == False :
			aGateway = 'None'

		if self.CheckIsIptype( aNameserver ) == False :
			aNameserver = 'None'

		return aAddress, aNetmask, aGateway, aNameserver


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

