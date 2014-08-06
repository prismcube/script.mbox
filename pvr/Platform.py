import logging
import os
import socket
import sys
import xbmc
import xbmcaddon
import xbmcgui
import urllib
import stat
from subprocess import *
from Product import *


gPlatform = None
try :
	cmd = "awk '/Hardware/ {print $3,$4}' /proc/cpuinfo"
	if sys.version_info < ( 2, 7 ) :
		getPlatformName = Popen( cmd, shell=True, stdout=PIPE )
		gPlatformName = getPlatformName.stdout.read( ).strip( )
		getPlatformName.stdout.close( )
	else :
		p = Popen( cmd, shell=True, stdout=PIPE, close_fds=True )
		( gPlatformName, err ) = p.communicate( )
		gPlatformName = gPlatformName.strip( )
	
except Exception, e :
	print 'except[%s]' % e
	gPlatformName = sys.platform

print '------------------------------platform[%s]'% gPlatformName

def GetPlatform( ) :
	global gPlatform
	if not gPlatform :
		if 'win32' == gPlatformName :
			gPlatform = WindowsPlatform( )
		elif 'linux' == gPlatformName or 'linux2' == gPlatformName :
			gPlatform = LinuxPlatform( )
		elif 'NXP BL-STB' == gPlatformName :
			gPlatform = PrismCubePlatform( PRODUCT_RUBY )
		elif 'Entropic STB' == gPlatformName :
			gPlatform = PrismCubePlatform( PRODUCT_OSCAR )
		elif 'darwin' == gPlatformName :
		# gotta be a better way to detect ipad/iphone/atv2
			if 'USER' in os.environ and os.environ[ 'USER'] in ( 'mobile', 'frontrow', ) :
				gPlatform = IOSPlatform( )
			else: 
				gPlatform = MacPlatform( )
		else :
			gPlatform = LinuxPlatform( )

	return gPlatform


def MakeDir( dir ) :
	""" Create dir with missing path segments and return for chaining """
	if not os.path.exists( dir ) :
		os.makedirs( dir )
	return dir


class Platform( object ) :

	def __init__( self, *args, **kwargs ) :
		self.addon = xbmcaddon.Addon( 'script.mbox' )
		MakeDir( self.GetScriptDataDir( ) )
		MakeDir( self.GetCacheDir( ) )

		self.mXBMCVersion = 0.0
		vs = xbmc.getInfoLabel( 'System.BuildVersion' )
		
		print 'xbmc version=%s' %vs

		try : 
			# sample input: '10.1 Git:Unknown'
			self.mXBMCVersion = float( vs.split( )[0] )
		except ValueError :
			try :
				# sample input: 'PRE-11.0 Git:Unknown'
				self.mXBMCVersion = float( vs.split( )[0].split( '-' )[1] )
			except ValueError :
				try :
					# sample input : 12.0-BETA3 Git:20121206-ae60d24
					self.mXBMCVersion = float( vs.split( )[0].split( '-' )[0] )
				except ValueError :
					print 'Could not determine version of XBMC from build version: %s. Returning %s' % ( vs, self.mXBMCVersion )

		print 'xbmc version=%s' %self.mXBMCVersion


	def GetXBMCVersion( self ) :
		return self.mXBMCVersion


	def GetFrodoVersion( self ) :
		return 12.0


	def GetEdenVersion( self ) :
		return 11.0


	def GetDahamaVersion( self ) :
		return 10.0


	def AddLibsToSysPath( self ) :
		libs = [
			'decorator', 
			'odict',
			'bidict', 
			'elementtree', 
			'tvdb_api', 
			'tvrage',
			'themoviedb', 
			'IMDbPY', 
			'simplejson', 
			'mysql-connector-python',
			'python-twitter',
			'twisted',
			'zope.interface',
			'mockito',
			'unittest2',
			'unittest',
			'distutils',
			'filedownloader']

		for lib in libs :
			sys.path.append( os.path.join( self.GetScriptDir( ), 'libs', lib ) )

		for i, path in enumerate( sys.path ) :    
			print 'check syspath[%d] = %s' % ( i, path )


	def GetName( self ) :
		return "N/A"

    
	def GetScriptDir( self ) :
		"""
		@return: directory that this xbmc script resides in.

		linux  : ~/.xbmc/addons/script.mbox
		windows: c:\Documents and Settings\[user]\Application Data\XBMC\addons\script.mhbox
		mac    : ~/Library/Application Support/XBMC/addons/script.mbox
		"""
		return self.addon.getAddonInfo( 'path' )


	def GetScriptDataDir( self ) :
		"""
		@return: directory for storing user settings for this xbmc script.

		linux  : ~/.xbmc/userdata/addon_data/script.mbox
		windows: c:\Documents and Settings\[user]\Application Data\XBMC\UserData\addon_data\script.mbox
		mac    : ~/Library/Application Support/XBMC/UserData/addon_data/script.mbox
		"""
		return xbmc.translatePath( self.addon.getAddonInfo( 'profile' ) )


	def GetSkinDir( self ) :
		return xbmc.translatePath( 'special://skin' )


	def GetCacheDir( self ) :
		return os.path.join( self.GetScriptDataDir( ), 'cache' )


	def GetUserDataDir( self ) :
		return xbmc.translatePath( 'special://userdata' )


	def GetHostname( self ) :
		try:
			return socket.GetHostname( )
		except:
			return xbmc.getIPAddress( )


	def IsLinux( self ) :
		return False


	def IsPrismCube( self ) :
		return False


	def GetProduct( self ) :
		return PRODUCT_RUBY


	def SetTunerType( self, aType ) :
		pass


	def GetTunerType( self ) :
		return TUNER_TYPE_DVBS_DUAL


	def GetMediaPath( self, aMediaFile ) :
		# TODO: Fix when we support multiple skins
		return os.path.join( self.GetScriptDir( ), 'resources', 'skins', 'Default', 'media', aMediaFile )


class LinuxPlatform( Platform ) :

	def __init__( self, *args, **kwargs ) :
		Platform.__init__( self, *args, **kwargs )


	def GetName( self ) :
		return "linux"


	def IsLinux( self ) :
		return True


class PrismCubePlatform( Platform ) :

	def __init__( self, *args, **kwargs ) :
		Platform.__init__( self, *args, **kwargs )
		self.mProduct = args[0]

		self.mTunerType = TUNER_TYPE_DVBS_SINGLE
		if self.mProduct == PRODUCT_RUBY :
			self.mTunerType = TUNER_TYPE_DVBS_DUAL
		elif self.mProduct == PRODUCT_OSCAR :
			self.mTunerType = TUNER_TYPE_DVBS_SINGLE
		else :
			self.mTunerType = TUNER_TYPE_DVBS_DUAL


	def GetName( self ) :
		return "PrismCube"


	def IsLinux( self ) :
		return True


	def IsPrismCube( self ) :
		return True


	def GetProduct( self ) :
		return self.mProduct


	def SetTunerType( self ) :
		if self.mProduct == PRODUCT_RUBY :
			self.mTunerType = TUNER_TYPE_DVBS_DUAL

		elif self.mProduct == PRODUCT_OSCAR :
			import pvr.ElisMgr
			from elisinterface.ElisEnum import ElisEnum
			tunerType = pvr.ElisMgr.GetInstance( ).GetCommander( ).System_GetFrontEndType( )
			if tunerType == ElisEnum.E_FRONTEND_SINGLE_DVBS :
				self.mTunerType = TUNER_TYPE_DVBS_SINGLE
			elif tunerType == ElisEnum.E_FRONTEND_DUAL_DVBS :
				self.mTunerType = TUNER_TYPE_DVBS_DUAL
			elif tunerType == ElisEnum.E_FRONTEND_SINGLE_DVBT or tunerType == ElisEnum.E_FRONTEND_SINGLE_DVBC :
				self.mTunerType = TUNER_TYPE_DVBT
			else :
				self.mTunerType = TUNER_TYPE_DVBS_SINGLE

		else :
			self.mTunerType = TUNER_TYPE_DVBS_DUAL


	def GetTunerType( self ) :
		return self.mTunerType


	def IsRootfUbiFs( self ) :
		try :
			if os.path.exists( '/etc/mtab' ) :
				inputFile = open( '/etc/mtab', 'r' )
				inputline = inputFile.readlines( )
				for line in inputline :
					if line.startswith( 'ubi0:rootfs' ) :
						return True
				return False
			else :
				return False

		except Exception, e :
			return False


class WindowsPlatform( Platform ) :
	def __init__( self, *args, **kwargs ) :
		Platform.__init__( self, *args, **kwargs )


	def GetName( self ) :
		return "windows"


class MacPlatform( Platform ) :
	def __init__( self, *args, **kwargs ) :
		Platform.__init__( self, *args, **kwargs )


	def GetName( self ) :
		return 'mac'


class IOSPlatform( Platform ) :
	def __init__( self, *args, **kwargs ) :
		Platform.__init__( self, *args, **kwargs )


	def GetName( self ) :
		return 'ios'

