import xbmc
import xbmcgui
import sys
import time
import thread

from pvr.gui.GuiConfig import *
from util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR
import pvr.Platform
from ElisEnum import ElisEnum

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
		print 'Already ChannelLogMgr is created'

	return gChannelLogoMgr



class ChannelLogoMgr( object ) :
	def __init__( self ) :
		self.mLogoHash = {}
		self.mLogoPath = None
		self.mDefaultLogo = None
		self.mDefaultLogoRadio = None
		self.Load( )


	def Load( self ) :
		if E_USE_CHANNEL_LOGO == False :
			return
		scriptDir = pvr.Platform.GetPlatform().GetScriptDir( )
		self.mLogoPath = os.path.join( pvr.Platform.GetPlatform().GetScriptDir( ), 'resources', 'channellogo')

		LOG_TRACE( 'Log Path=%s' %self.mLogoPath )
		self.mDefaultLogo = os.path.join( self.mLogoPath, 'DefaultLogo.png')
		self.mDefaultLogoRadio = os.path.join( self.mLogoPath, 'DefaultLogo_radio.png')		
		LOG_TRACE( 'Default Log Path=%s' %self.mDefaultLogo )

		parseTree = ElementTree.parse( os.path.join(self.mLogoPath, 'ChannelLogo.xml') )
		treeRoot = parseTree.getroot( )

		for node in treeRoot.findall( 'logo' ) :
			#LOG_TRACE( 'id=%s text=%s' %( node.get( 'id' ), node.text ) )		
			self.mLogoHash[ node.get( 'id' ) ] =  os.path.join( self.mLogoPath, node.text)


	def GetLogo( self, aId, aServiceType=ElisEnum.E_SERVICE_TYPE_TV  ) :
		if E_USE_CHANNEL_LOGO == False :
			return None

		logo = self.mLogoHash.get( aId, None )
		if logo == None :
			if aServiceType == ElisEnum.E_SERVICE_TYPE_TV:
				return self.mDefaultLogo
			else :
				return self.mDefaultLogoRadio						

		return logo


	def GetDefaultLogo( self, aServiceType=ElisEnum.E_SERVICE_TYPE_TV  ) :
		if E_USE_CHANNEL_LOGO == False :
			return None
	
		if aServiceType == ElisEnum.E_SERVICE_TYPE_TV:
			return self.mDefaultLogo
		else :
			return self.mDefaultLogoRadio						


