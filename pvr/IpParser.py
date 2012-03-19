import os
import re
import shutil
import sgmllib
import string
from pvr.gui.GuiConfig import *
from subprocess import *
from pvr.Util import LOG_ERR


FILE_NAME_INTERFACES	 		=	'/etc/network/interfaces'
FILE_NAME_TEMP_INTERFACES		= 	'/tmp/output'
FILE_NAME_RESOLV_CONF			=	'/etc/resolv.conf'
FILE_NAME_AUTO_RESOLV_CONF		=	'/etc/init.d/update-resolv.sh'

KEYWORD_ETH0					=	'iface eth0 inet'
KEYWORD_NAMESERVER				=	'nameserver'

SYSTEM_COMMAND_GET_IP			=	"ifconfig eth0 | awk '/inet / {print $2}' | awk -F: '{print $2}'"
SYSTEM_COMMAND_GET_MASK			=	"ifconfig eth0 | awk '/inet / {print $4}' | awk -F: '{print $2}'"
SYSTEM_COMMAND_GET_GATEWAY		=	"route -n | awk '/^0.0.0.0/ {print $2}'"


class IpParser :

	def __init__( self ) :
		self.mEth0Type			= NET_DHCP
		self.mAddressIp			= '255.255.255.255'
		self.mAddressMask		= '255.255.255.255'
		self.mAddressGateway	= '255.255.255.255'
		self.mAddressNameServer	= '255.255.255.255'


	def LoadNetworkType( self ) :
		inputFile = open( FILE_NAME_INTERFACES, 'r' )
		inputline = inputFile.readlines( )
		
		for line in inputline :
			if line.startswith( KEYWORD_ETH0 ) :
				words = string.split( line )
				if words[3] == 'static' :
					self.mEth0Type = NET_STATIC
				else :
					self.mEth0Type = NET_DHCP
				inputFile.close( )
				return True

		inputFile.close( )
		LOG_ERR( 'LoadNetworkType Fail!!!' )


	def LoadNetworkAddress( self ) :
		pipe = Popen( SYSTEM_COMMAND_GET_IP, shell=True, stdout=PIPE)
		self.mAddressIp = pipe.stdout.read( ).strip( )
		
		pipe = Popen( SYSTEM_COMMAND_GET_MASK, shell=True, stdout=PIPE)
		self.mAddressMask = pipe.stdout.read( ).strip( )
		
		pipe = Popen( SYSTEM_COMMAND_GET_GATEWAY, shell=True, stdout=PIPE)
		self.mAddressGateway = pipe.stdout.read( ).strip( )
		
		self.LoadNameServer( )
	

	def LoadNameServer( self ) :
		inputFile = open( FILE_NAME_RESOLV_CONF, 'r' )
		inputline = inputFile.readlines( )

		for line in inputline :
			if line.startswith( KEYWORD_NAMESERVER ) :
				words = string.split( line )
				self.mAddressNameServer = words[1]
				inputFile.close( )
				return	True
				
		inputFile.close( )				
		LOG_ERR( 'LoadNameServer Fail!!!' )


	def GetNetworkType( self ) :
		return self.mEth0Type


	def GetNetworkAddress( self ) :
		return self.mAddressIp, self.mAddressMask, self.mAddressGateway, self.mAddressNameServer

		"""

		#outputFile = open(FILE_NAME_TEMP_INTERFACES, 'w')
		
		for line in inputline :
		if line.startswith( 'iface eth0 inet' ) :
			var = re.sub('static', 'dhcp', line) # ('target', 'change', 'line' )
			outputFile.writelines( var )
			outputFile.writelines( 'address 192.168.101.168\n')
			outputFile.writelines( 'metmask 192.168.101.168\n')
			outputFile.writelines( 'gateway 192.168.101.168\n')
			nameIn.writelines('255.255.255.000\n')
		else :
			outputFile.writelines( line )
		"""



