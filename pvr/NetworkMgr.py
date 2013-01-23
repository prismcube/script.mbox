from pvr.gui.GuiConfig import *

gUseDbus = True

try :
	import dbus
except :
	gUseDbus = False


gNetworkMgr = None
CONFIGURATION_TIMEOUT = 20


def GetInstance( ) :
	global gNetworkMgr
	if not gNetworkMgr :
		gNetworkMgr = NetworkMgr( )
	else :
		pass

	return gNetworkMgr


class NetworkMgr( object ) :
	def __init__( self ) :
		self.mEthernetServicePath		= None
		self.mEthernetServiceObejct		= None


	def GetCurrentServiceType( self ) :
		return NETWORK_ETHERNET


	def GetCurrentServiceObject( self ) :
		if self.GetCurrentServiceType( ) == NETWORK_ETHERNET :
			return self.mEthernetServiceObejct
		else :
			return self.mEthernetServiceObejct


	def LoadEthernetService( self ) :
		if gUseDbus == False :
			return False
			
		try :
			self.mEthernetServicePath = None
			self.mEthernetServiceObejct = None
			bus = dbus.SystemBus( )
			manager = dbus.Interface( bus.get_object( 'net.connman', '/' ), 'net.connman.Manager' )
			services = manager.GetServices( )

			for entry in services :
				path = entry[0]
				properties = entry[1]
				for key in properties.keys( ) :
					if properties['Type'] == 'ethernet' :
						self.mEthernetServicePath = path
						break

			if self.mEthernetServicePath :
				self.mEthernetServiceObejct = dbus.Interface( bus.get_object( 'net.connman', self.mEthernetServicePath ),'net.connman.Service' )
				return True
			else :
				return False

		except dbus.DBusException, error :                                  
			LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )
			return False


	def GetEthernetServiceState( self ) :
		if gUseDbus == False :
			return False
	
		try :
			if self.mEthernetServiceObejct :
				property = self.mEthernetServiceObejct.GetProperties( )

				if property['State'] == 'idle' or property['State'] == 'disconnect' :
					return False
				else :
					return True
			else :
				LOG_ERR( 'Ethernet service is empty' )

		except dbus.DBusException, error :                                  
			LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )
			return False


	def SetEthernetServiceConnect( self, aFlag ) :
		if gUseDbus == False :
			return
	
		try :
			if self.mEthernetServiceObejct :
				if aFlag :
					self.mEthernetServiceObejct.Connect( timeout=60000 )
				else :
					self.mEthernetServiceObejct.Disconnect( )
				self.WaitConfigurationService( self.mEthernetServiceObejct )

		except dbus.DBusException, error :                                  
			LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )


	def GetEthernetAddress( self ) :
		address		= 'None'
		netmask		= 'None'
		gateway		= 'None'
		nameserver	= 'None'

		if gUseDbus == False :
			return 'None', 'None', 'None', 'None'

		try :
			property = self.mEthernetServiceObejct.GetProperties( )

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


	def ConnectEthernet( self, aMethod, aAddress=None, aNetmask=None, aGateway=None, aNameServer=None ) :
		if gUseDbus == False :
			return False
	
		try :
			if aMethod == NET_DHCP :
				ipv4_configuration = { 'Method': dbus.String( 'dhcp', variant_level = 1 ) }
			else :
				ipv4_configuration = { 'Method': dbus.String( 'manual', variant_level = 1 ) }
				ipv4_configuration[ 'Address'] = dbus.String( aAddress, variant_level = 1 )
				ipv4_configuration[ 'Netmask'] = dbus.String( aNetmask, variant_level = 1 )
				ipv4_configuration[ 'Gateway'] = dbus.String( aGateway, variant_level = 1 )
				self.mEthernetServiceObejct.SetProperty( 'Nameservers.Configuration', dbus.Array( [ aNameServer ], signature = dbus.Signature( 's' ) ) )

			self.mEthernetServiceObejct.SetProperty( 'IPv4.Configuration', ipv4_configuration )

			if self.GetEthernetServiceState( ) == False :
				self.SetEthernetServiceConnect( True )

			self.WaitConfigurationService( self.mEthernetServiceObejct )
			return True

		except dbus.DBusException, error :                                  
			LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )
			return False


	def GetEthernetMethod( self ) :
		if gUseDbus == False :
			return NET_DHCP
	
		try :
			property = self.mEthernetServiceObejct.GetProperties( )

			for key in property.keys( ) :
				if key == 'IPv4' :
					for val in property[key].keys( ) :
						if val == 'Method' :
							if property[key][val] == 'dhcp' :
								return NET_DHCP
							else :
								return NET_STATIC

			return NET_DHCP

		except dbus.DBusException, error :                                  
			LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )
			return NET_DHCP


	def WaitConfigurationService( self, aService ) :
		if gUseDbus == False :
			return
	
		for i in range( CONFIGURATION_TIMEOUT ) :
			time.sleep( 1 )
			try :
				property = aService.GetProperties( )
				if property['State'] != 'configuration' :
					return
			except dbus.DBusException, error :                                  
				LOG_ERR( '%s : %s' % ( error._dbus_error_name, error.message ) )

		aService.Disconnect( )
		time.sleep( 1 )


	def CheckInternetState( self ) :
		if gUseDbus == False :
			return 'Disconnected'
	
		service = self.GetCurrentServiceObject( )
		if service :
			try :
				property = service.GetProperties( )
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

