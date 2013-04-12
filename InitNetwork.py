import os
import string
import dbus
import time

TYPE_ETHERNET		= 0
TYPE_WIFI			= 1

NETWORK_CONFIG_PATH			= '/config/network.config'
WIFI_CONFIGURED_PATH		= '/var/lib/connman/wifi.config'

CONFIGURATION_TIMEOUT		= 30


class InitNetwork( ) :
	def __init__( self ) :
		self.mNettype				= TYPE_ETHERNET
		self.mMethod				= 'dhcp'
		self.mAddress				= None
		self.mNetmask				= None
		self.mGateway				= None
		self.mNameserver			= None
		self.mSSID					= None
		self.mPassphrase			= None
		self.mIsHidden				= 'False'
		self.mEthernet				= None
		self.mWifiTechnologyObject	= None
		self.mWifi					= None


	def Print( self ) :
		print 'networktype = %s' % self.mNettype
		print 'method = %s' % self.mMethod
		print 'address = %s' % self.mAddress
		print 'netmask = %s' % self.mNetmask
		print 'gateway = %s' % self.mGateway
		print 'nameserver = %s' % self.mNameserver
		print 'ssid = %s' % self.mSSID
		print 'passphrase = %s' % self.mPassphrase
		print 'hidden = %s' % self.mIsHidden
		time.sleep( 1 )


	def LoadNetworkConfig( self ) :
		print 'LoadNetworkConfig'
		if os.path.exists( NETWORK_CONFIG_PATH ) :
			try :
				print 'parse /config/network.config'
				inputFile = open( NETWORK_CONFIG_PATH, 'r' )
				inputline = inputFile.readlines( )
				for line in inputline :
					if line.startswith( 'networktype' ) :
						word = string.split( line )[2]
						if word != 'ethernet' :
							self.mNettype = TYPE_WIFI

					elif line.startswith( 'method' ) :
						word = string.split( line )[2]
						if word != 'dhcp' :
							self.mMethod = 'static'

					elif line.startswith( 'address' ) :
						self.mAddress = string.split( line )[2]

					elif line.startswith( 'netmask' ) :
						self.mNetmask = string.split( line )[2]

					elif line.startswith( 'gateway' ) :
						self.mGateway = string.split( line )[2]

					elif line.startswith( 'nameserver' ) :
						self.mNameserver = string.split( line )[2]

					elif line.startswith( 'ssid' ) :
						self.mSSID = string.split( line )[2]

					elif line.startswith( 'passphrase' ) :
						self.mPassphrase = string.split( line )[2]

					elif line.startswith( 'hidden' ) :
						self.mIsHidden = string.split( line )[2]

				inputFile.close( )
				return True

			except Exception, e :
				print 'Error exception[%s]' % e
				return False

		else :
			return False
			print '/config/network.config is not exist'


	def InitEthernet( self ) :
		print 'InitEthernet'
		try :
			self.LoadEthernetService( )
			
			if self.mEthernet :
				if self.mMethod == 'dhcp' :
					ipv4_configuration = { 'Method': dbus.String( 'dhcp', variant_level = 1 ) }
				else :
					ipv4_configuration = { 'Method': dbus.String( 'manual', variant_level = 1 ) }
					ipv4_configuration[ 'Address'] = dbus.String( self.mAddress, variant_level = 1 )
					ipv4_configuration[ 'Netmask'] = dbus.String( self.mNetmask, variant_level = 1 )
					ipv4_configuration[ 'Gateway'] = dbus.String( self.mGateway, variant_level = 1 )
					self.mEthernet.SetProperty( 'Nameservers.Configuration', dbus.Array( [ self.mNameserver ], signature = dbus.Signature( 's' ) ) )
					time.sleep( 0.5 )

				self.mEthernet.SetProperty( 'IPv4.Configuration', ipv4_configuration )
				time.sleep( 1 )

				if self.GetServiceState( self.mEthernet ) == False :
					self.SetServiceConnect( self.mEthernet, True )
				return True
			else :
				print 'Ethernet device not configured'

			print 'InitEthernet load wifi object = %s' % self.mWifi
			

		except dbus.DBusException, error :                                  
			print '%s : %s' % ( error._dbus_error_name, error.message )
			return False


	def InitWifi( self ) :
		print 'InitWifi'
		try :
			self.LoadEthernetService( )

			if self.mWifiTechnologyObject :
				if self.mIsHidden == 'False' :
					self.WriteWifiConfig( self.mSSID, self.mPassphrase, False )
				else :
					self.WriteWifiConfig( self.mSSID, self.mPassphrase, True )

				self.LoadWifiService( )
				if self.mWifi :
					self.SetServiceConnect( self.mWifi, True )
					self.SetAutoConnect( self.mWifi, False )
					time.sleep( 1 )
				else :
					print 'cannot find current set wifi config info'
			else :
				print 'Wifi device not configured'

			if self.mEthernet :
				self.SetServiceConnect( self.mEthernet, False )

		except dbus.DBusException, error :                                  
			print '%s : %s' % ( error._dbus_error_name, error.message )


	def WriteWifiConfig( self, aSSID, aPassword, aIsHidden ) :
		try :
			openFile = open( WIFI_CONFIGURED_PATH, 'w' )
			words = '[service_home]\n'
			words += 'Type = wifi\n'
			words += 'Name = ' + aSSID + '\n'
			if aPassword != '' :
				words += 'Passphrase = ' + aPassword + '\n'
			if aIsHidden :
				words += 'Hidden = True\n'

			openFile.write( words )
			openFile.close( )
			time.sleep( 1 )
			return True

		except Exception, e :				
			print 'WriteWifiConfigFile Error exception[%s]' % e
			return False


	def SetAutoConnect( self, aService, aFlag ) :
		print 'SetAutoConnect'
		try :
			if aService :
				aService.SetProperty( 'AutoConnect', aFlag )
				time.sleep( 0.5 )

		except dbus.DBusException, error :                                  
			print '%s : %s' % ( error._dbus_error_name, error.message )


	def LoadWifiService( self ) :
		print 'LoadWifiService'
		try :
			self.mWifi = None
			if self.mSSID :
				path = self.GetConfiguredWifiServicePath( self.mSSID )
				print 'LoadWifiService path = %s' % path
				if path :
					bus = dbus.SystemBus( )
					self.mWifi = dbus.Interface( bus.get_object( 'net.connman', path ), 'net.connman.Service' )

		except dbus.DBusException, error :                                  
			print '%s : %s' % ( error._dbus_error_name, error.message )


	def GetConfiguredWifiServicePath( self, aSSID ) :
		print 'GetConfiguredWifiServicePath'
		aplist = self.GetSearchedWifiApList( )

		if len( aplist ) > 0 :
			for ap in aplist :
				if str( ap[0] ) == aSSID :
					print 'Find matched SSID = %s' % ap[0]
					return ap[1]

		print 'GetConfiguredWifiServicePath is None'
		return None


	def GetSearchedWifiApList( self ) :
		print 'GetSearchedWifiApList'
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
						for i in properties[ 'Security' ]:
							Security += ' ' + str( i )
						Security += ' ]'
					servicelist.append( [ name, path, str( int ( properties[ 'Strength' ] ) ), Security ] )

			print 'GetSearchedWifiApList = %s' % servicelist
			return servicelist

		except dbus.DBusException, error :                                  
			print '%s : %s' % ( error._dbus_error_name, error.message )
			return []


	def LoadSetWifiTechnology( self ) :
		print 'LoadSetWifiTechnology'
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
				print 'wifi tech = %s' % self.mWifiTechnologyObject
				if self.GetWifiTechnologyPower( ) == False :
					self.SetWifiTechnologyPower( True )
				return True
			else :
				return False

		except dbus.DBusException, error :
			self.mWifiTechnologyObject = None
			wifiTechnologyPath = None
			print '%s : %s' % ( error._dbus_error_name, error.message )
			return False


	def GetWifiTechnologyPower( self ) :
		print 'GetWifiTechnologyPower'
		try :
			if self.mWifiTechnologyObject :
				property = self.mWifiTechnologyObject.GetProperties( )
				if property['Powered'] == 1 :
					return True
				else :
					return False
			else :
				print 'mWifiTechnologyObject is None'
				return True

		except dbus.DBusException, error :                                  
			print '%s : %s' % ( error._dbus_error_name, error.message )
			return True


	def SetWifiTechnologyPower( self, aFlag ) :
		print 'SetWifiTechnologyPower'
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
				print 'wifiTechnologyObject is None'

		except dbus.DBusException, error :                                  
			print '%s : %s' % ( error._dbus_error_name, error.message )
						
	
	def LoadEthernetService( self ) :
		print 'LoadEthernetService'
		try :
			ethernetServicePath = None
			self.mEthernet = None
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
				self.mEthernet = dbus.Interface( bus.get_object( 'net.connman', ethernetServicePath ), 'net.connman.Service' )
				print 'ethernet = %s' % self.mEthernet

		except dbus.DBusException, error :
			print '%s : %s' % ( error._dbus_error_name, error.message )


	def GetServiceState( self, aService ) :
		print 'GetServiceState'
		try :
			if aService :
				property = aService.GetProperties( )
				if property['State'] == 'idle' or property['State'] == 'disconnect' :
					return False
				elif property['State'] == 'ready' or property['State'] == 'online' :
					return True
			else :
				print 'service is empty'
				return None

		except dbus.DBusException, error :                                  
			print '%s : %s' % ( error._dbus_error_name, error.message )
			return False


	def SetServiceConnect( self, aService, aFlag ) :
		print 'SetServiceConnect'
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

				#aService = None
				#time.sleep( 0.5 )
				return True
			else :
				return False

		except dbus.DBusException, error :                                  
			print '%s : %s' % ( error._dbus_error_name, error.message )
			return False


	def WaitConfigurationService( self, aService ) :
		print 'WaitConfigurationService'
		if aService :
			try :
				for i in range( CONFIGURATION_TIMEOUT ) :
					time.sleep( 1 )
					try :
						property = aService.GetProperties( )
						if property['State'] != 'configuration' and property['State'] != 'association' :
							return

					except dbus.DBusException, error :
						print '%s : %s' % ( error._dbus_error_name, error.message )

				time.sleep( 1 )

			except dbus.DBusException, error :                                  
				print '%s : %s' % ( error._dbus_error_name, error.message )


print 'Start init network'

initNetwork = InitNetwork( )
if initNetwork.LoadNetworkConfig( ) :
	initNetwork.Print( )

	initNetwork.LoadSetWifiTechnology( )

	if initNetwork.mNettype == TYPE_ETHERNET :
		initNetwork.InitEthernet( )
	else :
		initNetwork.InitWifi( )

del initNetwork

print 'Init network done'

	
