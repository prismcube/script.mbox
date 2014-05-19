import os, sys, time, threading
import xbmc
import xbmcgui
import xbmcaddon

from decorator import decorator
from odict import odict
from elisinterface.ElisEnum import ElisEnum
import pvr.Platform
from elisinterface.util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR
from pvr.gui.GuiConfig import InitTranslateByEnumList

if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

try :
	import xml.etree.cElementTree as ElementTree
except Exception, e :
	from elementtree import ElementTree


def XBMC_GetCurrentSkinName( ) :

	LOG_TRACE( '' )
	currentSkinName = 'Default'

	if pvr.Platform.GetPlatform( ).GetXBMCVersion( ) < pvr.Platform.GetPlatform( ).GetFrodoVersion( ) :	# for Frodo	
		currentSkinName = xbmc.executehttpapi( "GetGUISetting(3, lookandfeel.skin)" )
		currentSkinName = currentSkinName[4:]

	else :
		json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "GUI.GetProperties", "params": {"properties": ["skin"]}, "id": 1}')
		json_response = unicode(json_query, 'utf-8', errors='ignore')
		jsonobject = simplejson.loads(json_response)
		if jsonobject.has_key('result') and jsonobject['result'] != None and jsonobject['result'].has_key('skin'):
			print 'result has key with skin = %s' % jsonobject['result']['skin']
			total = str( len( jsonobject['result']['skin'] ) )
			print 'total skin result = %s' % total
			item = jsonobject['result']['skin']
			if item.has_key('id' ):
				currentSkinName = item['id']
				print 'skinId = %s' % currentSkinName
			if item.has_key('name') :
				skinName = item['name']
				print 'skinName = %s' % skinName

	LOG_TRACE( 'currentSkinName=%s' %currentSkinName )

	return currentSkinName



def XBMC_GetFavAddons( ) :
	LOG_TRACE( '' )
	favoriteList = []
	
	if pvr.Platform.GetPlatform( ).GetXBMCVersion( ) < pvr.Platform.GetPlatform( ).GetFrodoVersion( ) :
		tmpList = xbmc.executehttpapi( "getfavourites()" )
		if tmpList != '<li>' :
			favoriteList = tmpList[4:].split( ':' )

			addonList = XBMC_GetAddons( )
			LOG_TRACE( 'lael98 addonList=%s' %addonList )		
			total = len( aAddonList )
			for i in range( total ) :
				findaddon = False
				reversIndex = total - i - 1
				LOG_TRACE( 'reversindex=%d' %reversIndex )
				for addon in addonList :
					if addonList[reversIndex] == addon :
						findaddon = True
				if findaddon == False :
					del addonList[reversIndex]

	else :
		json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.GetAddonFavourites", "params": {"properties": ["name", "author", "summary", "version", "fanart", "thumbnail","description"]}, "id": 1}')
		json_response = unicode(json_query, 'utf-8', errors='ignore')
		jsonobject = simplejson.loads(json_response)

		if jsonobject.has_key('result') and jsonobject['result'] != None and jsonobject['result'].has_key('addons'):
			total = str( len( jsonobject['result']['addons'] ) )
			for item in jsonobject['result']['addons']:
				if item['type'] == 'xbmc.python.script' or item['type'] == 'xbmc.python.pluginsource':
					favoriteList.append(item['addonid'])

	LOG_TRACE( 'favoriteList=%s' %favoriteList )

	
	return favoriteList


def XBMC_GetAddons( ) :
	LOG_TRACE( '' )
	addonList = []
	if pvr.Platform.GetPlatform( ).GetXBMCVersion( ) < pvr.Platform.GetPlatform( ).GetFrodoVersion( ) :
		tmpList = xbmc.executehttpapi( "getaddons()" )
		if tmpList == '<li>' :
			addonList = []		
		else :
			addonList = tmpList[4:].split( ':' )

	else :
		json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.GetAddons", "params": {"properties": ["name", "author", "summary", "version", "fanart", "thumbnail","description"]}, "id": 1}')
		json_response = unicode(json_query, 'utf-8', errors='ignore')
		jsonobject = simplejson.loads(json_response)

		if jsonobject.has_key('result') and jsonobject['result'] != None and jsonobject['result'].has_key('addons'):
			total = str( len( jsonobject['result']['addons'] ) )
			# find plugins and scripts
			for item in jsonobject['result']['addons']:
				if item['type'] == 'xbmc.python.script' or item['type'] == 'xbmc.python.pluginsource':
					print "Addon Id = %s" % item['addonid']
					addonList.append(item['addonid'])

	return addonList


def XBMC_AddFavAddon( aAddonId ) :
	LOG_TRACE( '' )
	if pvr.Platform.GetPlatform( ).GetXBMCVersion( ) < pvr.Platform.GetPlatform( ).GetFrodoVersion( ) :
		xbmc.executehttpapi( "addfavourite(%s)" % aAddonId )
	else :
		LOG_ERR( 'ToDO ' )


def XBMC_RemoveFavAddon( aAddonId ) :
	LOG_TRACE( '' )
	if pvr.Platform.GetPlatform( ).GetXBMCVersion( ) < pvr.Platform.GetPlatform( ).GetFrodoVersion( ) :
		xbmc.executehttpapi( "removefavourite(%s)" %aAddonId )
	else :
		removeAddonFavString = '{"jsonrpc": "2.0", "method": "Addons.RemoveAddonFavourite", "params": {"addonid":"'+aAddonId+'"}, "id": 1}'
		json_query = xbmc.executeJSONRPC( removeAddonFavString)
		json_response = unicode(json_query, 'utf-8', errors='ignore')
		jsonobject = simplejson.loads(json_response)


def XBMC_RunAddon( aAddonId ) :
	LOG_TRACE( '' )
	if pvr.Platform.GetPlatform( ).GetXBMCVersion( ) < pvr.Platform.GetPlatform( ).GetFrodoVersion( ) :
		xbmc.executebuiltin( "runaddon(%s)" %aAddonId )
	else :
		runAddonFavString = '{"jsonrpc": "2.0", "method": "Addons.ExecuteAddon", "params": {"addonid":"'+aAddonId+'"}, "id": 1}'
		json_query = xbmc.executeJSONRPC( runAddonFavString )
		json_response = unicode(json_query, 'utf-8', errors='ignore')
		jsonobject = simplejson.loads(json_response)



def XBMC_GetVolume( ) :	
	LOG_TRACE( '' )
	volume = 0
	if pvr.Platform.GetPlatform( ).GetXBMCVersion( ) < pvr.Platform.GetPlatform( ).GetFrodoVersion( ) :
		retVolume = xbmc.executehttpapi( 'getvolume' )
		volume = int( retVolume[4:] )
	else :
		#LOG_TRACE( '' )
		#if XBMC_GetMute() == True :
		#	LOG_TRACE( '' )
		#	return 0
		LOG_TRACE( '' )			
		print 'E_ADD_XBMC_JSONRPC_FUNCTION : getVolume'
		json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["volume"]}, "id": 1}')
		json_response = unicode(json_query, 'utf-8', errors='ignore')
		jsonobject = simplejson.loads(json_response)

		if jsonobject.has_key('result') and jsonobject['result'] != None and jsonobject['result'].has_key('volume'):
			volume = int( jsonobject['result']['volume'] )
			
	LOG_TRACE( 'currentvolume = %d' %volume )
	return volume


def XBMC_GetMute( ) :	

	volume = 0
	if pvr.Platform.GetPlatform( ).GetXBMCVersion( ) < pvr.Platform.GetPlatform( ).GetFrodoVersion( ) :
		retVolume = xbmc.executehttpapi( 'getvolume' )
		volume = int( retVolume[4:] )
		if volume == 0 :
			return True
	else :
		print 'E_ADD_XBMC_JSONRPC_FUNCTION : getMute'
		json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Application.GetProperties", "params": {"properties": ["muted"]}, "id": 1}')
		json_response = unicode(json_query, 'utf-8', errors='ignore')
		jsonobject = simplejson.loads(json_response)

		if jsonobject.has_key('result') and jsonobject['result'] != None and jsonobject['result'].has_key('muted'):
			muted = jsonobject['result']['muted']
			LOG_TRACE('---------------xbmc muted = %s' %muted)
			return muted
			
	return False


def XBMC_SetVolume( aVolume, aIsMute=0 ) :	
	LOG_TRACE( '' )
	if pvr.Platform.GetPlatform( ).GetXBMCVersion( ) < pvr.Platform.GetPlatform( ).GetFrodoVersion( ) :
		volumeString = 'setvolume(%s)'% aVolume
		if aIsMute or aVolume <= 0 :
			volumeString = 'Mute'
		xbmc.executehttpapi( volumeString )

	else :
		print 'E_ADD_XBMC_JSONRPC_FUNCTION: SetVolume %d ' % aVolume
		setvolume_query = '{"jsonrpc": "2.0", "method": "Application.SetVolume", "params": {"volume": %d}, "id": 1}' % aVolume
		#if not aVolume :
		#	setvolume_query = '{"jsonrpc": "2.0", "method": "Application.SetMute", "params": {"mute": "toggle"}, "id": 1}'
		#setvolume_query = '{"jsonrpc": 2.0", "method": "Application.SetVolume", "params": { "value": "13"}, "id": 1}'
		xbmc.executeJSONRPC ( setvolume_query )


def XBMC_SetVolumeByBuiltin( aVolume, aIsVisible ) :
	LOG_TRACE( '' )
	print 'XMBC_BUILTIN_FUNCTION: SetVolume %d' % aVolume
	xbmc.executebuiltin( 'SetVolume( %s, %s )' % ( aVolume, aIsVisible ) )


def XBMC_GetResolution( ) :
	LOG_TRACE( '' )
	left =0
	top = 0
	right = 1280
	bottom = 720

	if pvr.Platform.GetPlatform( ).GetXBMCVersion( ) < pvr.Platform.GetPlatform( ).GetFrodoVersion( ) :
		strResolution = xbmc.executehttpapi( "getresolution( )" )
		resInfo =  strResolution[4:].split( ':' )
		LOG_TRACE( 'resInfo = %s' % resInfo )
		width = int( resInfo[0] )
		height = int( resInfo[1] )
		fixelRate=  float( resInfo[2] )
		left = int( resInfo[3] )
		top = int( resInfo[4] )
		right = int( resInfo[5] )
		bottom = int( resInfo[6] )

	else :
		print 'E_ADD_XBMC_JSONRPC_FUNCTION : getresolution '
		json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "GUI.GetProperties", "params": {"properties": ["resolution"]}, "id": 1}')
		json_response = unicode(json_query, 'utf-8', errors='ignore')
		jsonobject = simplejson.loads(json_response)
		if jsonobject.has_key('result') and jsonobject['result'] != None and jsonobject['result'].has_key('resolution'):
			print 'result has key with skin resolution = %s' % jsonobject['result']['resolution']
			total = str( len( jsonobject['result']['resolution'] ) )
			print 'total skin result = %s' % total
			item = jsonobject['result']['resolution']
			if item.has_key('left' ):
				left = item['left']
				print 'left = %s' % left
			if item.has_key('top') :
				top = item['top']
				print 'top = %s' % top
			if item.has_key('right') :
				right = item['right']
				print 'right = %s' % right
			if item.has_key('bottom') :
				bottom = item['bottom']
				print 'bottom = %s' % bottom

	
		else :
			try :
				from pvr.GuiHelper import GetInstanceSkinPosition
				userDatePath	= pvr.Platform.GetPlatform( ).GetUserDataDir( ) + 'guisettings.xml'

				resolutionInfo	= ElementTree.parse( userDatePath )
				root 			= resolutionInfo.getroot( )
				resolution		= root.find( 'resolutions' )
				
				left			= int( resolution.getchildren( )[1].find( 'overscan' ).find( 'left' ).text )
				top				= int( resolution.getchildren( )[1].find( 'overscan' ).find( 'top' ).text )
				right			= int( resolution.getchildren( )[1].find( 'overscan' ).find( 'right' ).text )
				bottom			= int( resolution.getchildren( )[1].find( 'overscan' ).find( 'bottom' ).text )

			except Exception, e :
				LOG_ERR( 'Error exception[%s]' % e )

	return [left,top,right,bottom]


def XBMC_GetSkinZoom( ) :
	LOG_TRACE( '' )
	skinzoom = 0
	if pvr.Platform.GetPlatform( ).GetXBMCVersion( ) < pvr.Platform.GetPlatform( ).GetFrodoVersion( ) :
		strZoom = xbmc.executehttpapi( "GetGUISetting(0, lookandfeel.skinzoom)" )
		skinzoom = int( strZoom[4:] )
	else :
		json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "GUI.GetProperties", "params": {"properties": ["skinzoom"]}, "id": 1}')
		json_response = unicode(json_query, 'utf-8', errors='ignore')
		jsonobject = simplejson.loads(json_response)
		if jsonobject.has_key('result') and jsonobject['result'] != None and jsonobject['result'].has_key('skinzoom'):
			print 'result has key with skin skinzoom = %s' % jsonobject['result']['skinzoom']
			total = str( len( jsonobject['result']['skinzoom'] ) )
			print 'total skin result = %s' % total
			item = jsonobject['result']['skinzoom']
			if item.has_key('zoom' ):
				zoom = int( item['zoom'] )
				print 'zoom = %s' % zoom
			
			skinzoom = zoom

		else :
			from pvr.GuiHelper import GetInstanceSkinPosition
			userDatePath	= pvr.Platform.GetPlatform( ).GetUserDataDir( ) + 'guisettings.xml'

			resolutionInfo	= ElementTree.parse( userDatePath )
			root 			= resolutionInfo.getroot( )
			skinzoom		= int( root.find( 'lookandfeel' ).find( 'skinzoom' ).text )

	LOG_TRACE( 'zoom=%d' %skinzoom )
	return skinzoom


def XBMC_GetWebserver( ) :
	if pvr.Platform.GetPlatform( ).GetXBMCVersion( ) < pvr.Platform.GetPlatform( ).GetFrodoVersion( ) :
		return None
	else :
		try :
			print 'dhkim test XBMC_GetWebserver'
			json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "GUI.GetProperties", "params": {"properties": ["webserver"]}, "id": 1}')
			json_response = unicode(json_query, 'utf-8', errors='ignore')
			jsonobject = simplejson.loads(json_response)

			if jsonobject.has_key('result') and jsonobject['result'] != None and jsonobject['result'].has_key('webserver') :
				result = jsonobject['result']['webserver']
				webserver = result["webserver"]
				return webserver
			else :
				return None

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return None


def XBMC_GetUpnpRenderer( ) :
	if pvr.Platform.GetPlatform( ).GetXBMCVersion( ) < pvr.Platform.GetPlatform( ).GetFrodoVersion( ) :
		return None
	else :
		try :
			print 'dhkim test XBMC_GetUpnpRenderer'
			json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "GUI.GetProperties", "params": {"properties": ["upnprenderer"]}, "id": 1}')
			json_response = unicode(json_query, 'utf-8', errors='ignore')
			jsonobject = simplejson.loads(json_response)

			if jsonobject.has_key('result') and jsonobject['result'] != None and jsonobject['result'].has_key('upnprenderer') :
				result = jsonobject['result']['upnprenderer']
				upnprenderer = result["upnprenderer"]
				return upnprenderer
			else :
				return None

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return None


def XBMC_GetEsallinterfaces( ) :
	if pvr.Platform.GetPlatform( ).GetXBMCVersion( ) < pvr.Platform.GetPlatform( ).GetFrodoVersion( ) :
		return None
	else :
		try :
			print 'dhkim test XBMC_GetUpnpRenderer'
			json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "GUI.GetProperties", "params": {"properties": ["esallinterfaces"]}, "id": 1}')
			json_response = unicode(json_query, 'utf-8', errors='ignore')
			jsonobject = simplejson.loads(json_response)

			if jsonobject.has_key('result') and jsonobject['result'] != None and jsonobject['result'].has_key('esallinterfaces') :
				result = jsonobject['result']['esallinterfaces']
				esallinterfaces = result["esallinterfaces"]
				return esallinterfaces
			else :
				return None

		except Exception, e :
			LOG_ERR( 'Error exception[%s]' % e )
			return None


def XBMC_SetSkinZoom( aZoom ) :	
	LOG_TRACE( '' )
	xbmc.executebuiltin( 'lookandfeel.skinzoom( %d )' % aZoom )


def XBMC_GetCurrentLanguage( ) :
	LOG_TRACE( '' )
	if pvr.Platform.GetPlatform( ).GetXBMCVersion( ) < pvr.Platform.GetPlatform( ).GetFrodoVersion( ) :
		currentLanguage = xbmc.executehttpapi( "GetGUISetting(3, locale.language)" )
		LOG_TRACE( "Get currentLanguage = %s" % currentLanguage[4:] )
		capitalizedString  = currentLanguage[4:].capitalize( )
		return capitalizedString
	else :
		currentLanguage = xbmc.getLanguage()
		print 'Current Language = %s ' % currentLanguage
		capitalizedString  = currentLanguage.capitalize( )
		return capitalizedString
		

def XBMC_SetCurrentLanguage( aLanguage ) :
	from elisinterface.ElisProperty import ResetHash
	ResetHash( )

	LOG_TRACE( 'aLanguage=%s' %aLanguage )
	oldLanguage = xbmc.getLanguage()
	newLanguage = aLanguage
	if pvr.Platform.GetPlatform( ).GetXBMCVersion( ) < pvr.Platform.GetPlatform( ).GetFrodoVersion( ) :
		LOG_TRACE( '' )
		xbmc.executebuiltin( "Custom.SetLanguage(%s)" % aLanguage )
	else :
		LOG_TRACE( '' )	
		xbmc.executebuiltin( "Custom.SetLanguage(%s)" % aLanguage )		
		#xbmc.setLanguage( aLanguage )

	xbmcgui.Window( 10000 ).setProperty( 'PIPLoadFinished', 'False' )
	checkLanguage = threading.Timer( 0.5, XBMC_CheckChangeLanguage, [newLanguage] )
	checkLanguage.start( )


def XBMC_CheckChangeLanguage( aNewLanguage ) :
	#from pvr.gui.GuiConfig import *
	maxTime = 15
	loopTime = 0
	inteval = 1

	while loopTime < maxTime :
		time.sleep( inteval )
		loopTime += inteval
		#LOG_TRACE('----------checking language....[%s]'% loopTime )
		if XBMC_GetCurrentLanguage( ) == aNewLanguage :
			break

	InitTranslateByEnumList( )


def XBMC_SetLocalOffset( aLocalOffset ) :
	LOG_TRACE( '' )
	LOG_TRACE( 'SetLocalOffset=%d' %aLocalOffset )

	if pvr.Platform.GetPlatform( ).GetXBMCVersion( ) < pvr.Platform.GetPlatform( ).GetFrodoVersion( ) :
		xbmc.executehttpapi( 'setlocaloffset(%d)' %aLocalOffset )
	else :
		xbmc.setLocalOffset( aLocalOffset )


def XBMC_CheckNetworkStatus( ) :
	return xbmc.getInfoLabel( 'System.internetstate' )

