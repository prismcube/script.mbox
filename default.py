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
	import pvr.Platform 
	platform = pvr.Platform.GetPlatform( )
	platform.AddLibsToSysPath( )
	cacheDir = platform.GetCacheDir( )

	from pvr.Util import MakeDir
	MakeDir( cacheDir )

	import Launcher
	Launcher.GetInstance( ).Run( )

