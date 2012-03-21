import os
import re
import sys
import shutil
import string
import time
from pvr.gui.GuiConfig import *
from pvr.Util import LOG_ERR


FILE_NAME_INTERFACES	 		=	'/etc/network/interfaces'
FILE_NAME_TEMP_INTERFACES		= 	'/tmp/interface'
FILE_NAME_RESOLV_CONF			=	'/etc/resolv.conf'
FILE_NAME_AUTO_RESOLV_CONF		=	'/etc/init.d/update-resolv.sh'
FILE_TEMP						=	'/tmp/ip_temp'

KEYWORD_ETH0					=	'iface eth0 inet'
KEYWORD_NAMESERVER				=	'nameserver'

SYSTEM_COMMAND_GET_IP			=	"ifconfig eth0 | awk '/inet / {print $2}' | awk -F: '{print $2}'"
SYSTEM_COMMAND_GET_MASK			=	"ifconfig eth0 | awk '/inet / {print $4}' | awk -F: '{print $2}'"
SYSTEM_COMMAND_GET_GATEWAY		=	"route -n | awk '/^0.0.0.0/ {print $2}'"

COMMAND_NETWORK_RESTART			=	"/etc/init.d/networking restart"
COMMAND_COPY_INTERFACES			=	"cp " + FILE_NAME_TEMP_INTERFACES + " " + FILE_NAME_INTERFACES


class IpParser :

	def __init__( self ) :
		self.mEth0Type			= None
		self.mAddressIp			= '255.255.255.255'
		self.mAddressMask		= '255.255.255.255'
		self.mAddressGateway	= '255.255.255.255'
		self.mAddressNameServer	= '255.255.255.255'


	def LoadNetworkType( self ) :
		try :
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
			LOG_ERR( 'LoadNetworkType Load Fail!!!' )
			return False

		except Exception, e :
			inputFile.close( )
			LOG_ERR( 'Error exception[%s]' % e )
			return False


	def LoadNetworkAddress( self ) :
		try :
			osCommand = [ SYSTEM_COMMAND_GET_IP + ' > ' + FILE_TEMP, SYSTEM_COMMAND_GET_MASK + ' >> ' + FILE_TEMP, SYSTEM_COMMAND_GET_GATEWAY + ' >> ' + FILE_TEMP ]
			
			for command in osCommand :
				time.sleep( 0.01 )
				os.system( command )
			
			time.sleep( 0.02 )
			inputFile = open( FILE_TEMP, 'r' )
			self.mAddressIp = inputFile.readline( ).strip( )
			self.mAddressMask = inputFile.readline( ).strip( )
			self.mAddressGateway = inputFile.readline( ).strip( )
			self.LoadNameServer( )

			if self.CheckIsIptype( self.mAddressIp ) == False :
				self.mAddressIp = None

			if self.CheckIsIptype( self.mAddressMask ) == False :
				self.mAddressMask = None

			if self.CheckIsIptype( self.mAddressGateway ) == False :
				self.mAddressGateway = None

			if self.CheckIsIptype( self.mAddressNameServer ) == False :
				self.mAddressNameServer = None

			inputFile.close( )
			if self.mAddressIp == None or self.mAddressIp == None or self.mAddressIp == None or self.mAddressIp == None :
				LOG_ERR( 'Load Ip fail !!' )
				return False
			else :
				return True

		except Exception, e :
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
			inputFile.close( )
			self.mAddressNameServer = None
			LOG_ERR( 'Error exception[%s]' % e )


	def GetNetworkType( self ) :
		return self.mEth0Type


	def GetNetworkAddress( self ) :
		return self.mAddressIp, self.mAddressMask, self.mAddressGateway, self.mAddressNameServer


	def CheckIsIptype( self, aAddress ) :
		try :
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


	def SetNetwork( self, aType, aIpAddress=None, aMaskAddress=None, aGatewayAddress=None, aNameAddress=None ) :
		try :
			inputFile = open( FILE_NAME_INTERFACES, 'r' )
			outputFile = open( FILE_NAME_TEMP_INTERFACES, 'w+' )
			inputline = inputFile.readlines( )
			for line in inputline :
				if line.startswith( KEYWORD_ETH0 ) :
					if aType == NET_DHCP :
						outputFile.writelines( KEYWORD_ETH0 + ' ' + 'dhcp\n' )
					else :
						outputFile.writelines( KEYWORD_ETH0 + ' ' + 'static\n' )
						outputFile.writelines( 'address %s\n' % aIpAddress )
						outputFile.writelines( 'netmask %s\n' % aMaskAddress )
						outputFile.writelines( 'gateway %s\n' % aGatewayAddress )
				elif line.startswith( 'address' ) or line.startswith( 'netmask' ) or line.startswith( 'gateway' ) :
					continue
				else :
					outputFile.writelines( line )

			self.SetNameServer( aType, aNameAddress )
			inputFile.close( )
			outputFile.close( )

			os.system( COMMAND_COPY_INTERFACES )
			os.system( COMMAND_NETWORK_RESTART )
			return True

		except Exception, e :
			inputFile.close( )
			outputFile.close( )
			LOG_ERR( 'Error exception[%s]' % e )
			return False


	def SetNameServer( self, aType, aNameAddress ) :
		try :
			if aType == NET_DHCP :
				os.system( 'rm -rf ' + FILE_NAME_AUTO_RESOLV_CONF )
			else :
				os.system( 'echo ' + KEYWORD_NAMESERVER + ' %s ' % aNameAddress + '> ' + FILE_NAME_RESOLV_CONF )
				os.system( 'echo ' + KEYWORD_NAMESERVER + ' %s ' % aNameAddress + '> ' + FILE_NAME_AUTO_RESOLV_CONF )
				os.system( 'chmod 755 %s' % FILE_NAME_AUTO_RESOLV_CONF )
			return True
			
		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return False		