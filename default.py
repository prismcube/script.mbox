from elementtree import ElementTree

if __name__ == '__main__':
	import os, sys, xbmcaddon, shutil
	scriptDir = xbmcaddon.Addon('script.mbox').getAddonInfo('path')
	sys.path.append(os.path.join(scriptDir, 'pvr'))
	sys.path.append(os.path.join(scriptDir, 'resources'))	

	elisDir =  xbmcaddon.Addon('script.module.elisinterface').getAddonInfo('path')
	print 'elisDir=%s' %elisDir
	print 'elisDir=%s' %os.path.join(elisDir, 'lib', 'elisinterface')
	sys.path.append(os.path.join(elisDir, 'lib', 'elisinterface'))		

#	import xbmcgui
#	import xbmc
#	loading = xbmcgui.WindowXML('loading.xml', scriptDir)
#	loading.show()
	print 'sys.prefix=%s' %sys.prefix
	print 'sys.exec_prefix=%s' %sys.exec_prefix
	print 'sys.path=%s' %sys.path

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
	cacheDir = platform.GetCacheDir( )

	from pvr.Util import MakeDir
	MakeDir( cacheDir )

	import Launcher
	Launcher.GetInstance( ).Run( )

