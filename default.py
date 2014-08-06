try :
	import xml.etree.cElementTree as ElementTree
except Exception, e :
	from elementtree import ElementTree

import os, sys, xbmcaddon, shutil


if __name__ == '__main__' :
	scriptDir = xbmcaddon.Addon( 'script.mbox' ).getAddonInfo( 'path' )
	#sys.path.append( os.path.join( scriptDir, 'pvr' ) )
	#sys.path.append( os.path.join( scriptDir, 'resources' ) )
	sys.path.append( os.path.join( scriptDir, 'webinterface' ) )		

	#elisDir = xbmcaddon.Addon( 'script.module.elisinterface' ).getAddonInfo( 'path' )
	#sys.path.append( os.path.join( elisDir, 'lib', 'elisinterface' ) )

#	import xbmcgui
#	import xbmc
#	loading = xbmcgui.WindowXML('loading.xml', scriptDir)
#	loading.show()
#	print 'sys.prefix=%s' %sys.prefix
#	print 'sys.exec_prefix=%s' %sys.exec_prefix
#	print 'sys.path=%s' %sys.path

	"""
	sitepath = os.path.join( sys.prefix,"lib",
				"python" + sys.version[:3],
				"site-packages" )

	print 'site path=%s' %sitepath
	"""

	
	#sitepath=''
	#site.addsitedir( sitepath )
	import pvr.Platform 
	platform = pvr.Platform.GetPlatform( )
	platform.AddLibsToSysPath( )
	platform.SetTunerType( )
	cacheDir = platform.GetCacheDir( )

	from pvr.Util import MakeDir
	MakeDir( cacheDir )

	import pvr.Launcher as Launcher
	Launcher.GetInstance( ).Run( )
