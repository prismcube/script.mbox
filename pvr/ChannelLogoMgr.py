import xbmc
import xbmcgui
import sys
import time
import thread

from pvr.gui.GuiConfig import *
from pvr.GuiHelper import *
from elisinterface.util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR
import pvr.Platform
from elisinterface.ElisEnum import ElisEnum

try :
	import xml.etree.cElementTree as ElementTree
except Exception, e :
	from elementtree import ElementTree


gChannelLogoMgr = None

def GetInstance( ) :
	global gChannelLogoMgr
	if not gChannelLogoMgr :
		gChannelLogoMgr = ChannelLogoMgr( )
	else:
		print 'ChannelLogoMgr is already created'

	return gChannelLogoMgr



class ChannelLogoMgr( object ) :
	def __init__( self ) :
		self.mMboxLogoHash = {}
		self.mCustomLogoHash = {}
		self.mUseCustomPath = GetSetting( 'CUSTOM_ICON' )
		self.Load( )


	def Load( self ) :
		if E_USE_CHANNEL_LOGO == False :
			return

		self.LoadDefaultLogo( )
		self.LoadCustomLogo( )


	def LoadDefaultLogo( self ) :
		self.mMboxLogoHash = {}
		try :
			mbox_logo_path = os.path.join( pvr.Platform.GetPlatform( ).GetScriptDir( ), 'resources', 'channellogo' )
			LOG_TRACE( 'Log Path=%s' % mbox_logo_path )

			parseTree = ElementTree.parse( os.path.join( mbox_logo_path, 'ChannelLogo.xml') )
			treeRoot = parseTree.getroot( )

			for node in treeRoot.findall( 'logo' ) :
				self.mMboxLogoHash[ node.get( 'id' ) ] =  os.path.join( mbox_logo_path, node.text )
		except :
			LOG_ERR( 'Loading defult logo path failed' )


	def LoadCustomLogo( self ) :
		self.mCustomLogoHash = {}
		try :
			parseTree = ElementTree.parse( os.path.join( CUSTOM_LOGO_PATH, 'ChannelLogo.xml' ) )
			treeRoot = parseTree.getroot( )
			for node in treeRoot.findall( 'logo' ) :
				self.mCustomLogoHash[ node.get( 'id' ) ] = os.path.join( CUSTOM_LOGO_PATH, node.text)
		except :
			LOG_ERR( 'Loading custom logo path failed' )


	def GetLogo( self, aId, aServiceType=ElisEnum.E_SERVICE_TYPE_TV  ) :
		if E_USE_CHANNEL_LOGO == False :
			return None
		if self.mUseCustomPath == 'true' :
			return self.GetCustomLogo( aId, aServiceType )
		else :
			return self.GetMboxLogo( aId, aServiceType )


	def GetMboxLogo( self, aId, aServiceType ) :
		logo = self.mMboxLogoHash.get( aId, None )
		if logo == None :
			if aServiceType == ElisEnum.E_SERVICE_TYPE_TV :
				return 'DefaultLogo.png'
			else :
				return 'DefaultLogo_radio.png'

		return logo


	def GetCustomLogo( self, aId, aServiceType ) :
		logo = self.mCustomLogoHash.get( aId, None )
		if logo == None :
			logo = self.GetMboxLogo( aId, aServiceType )
			if logo == None :
				if aServiceType == ElisEnum.E_SERVICE_TYPE_TV :
					return 'DefaultLogo.png'
				else :
					return 'DefaultLogo_radio.png'

		return logo
		

	def GetDefaultLogo( self, aServiceType=ElisEnum.E_SERVICE_TYPE_TV  ) :
		if E_USE_CHANNEL_LOGO == False :
			return None
	
		if aServiceType == ElisEnum.E_SERVICE_TYPE_TV:
			return 'DefaultLogo.png'
		else :
			return 'DefaultLogo_radio.png'

