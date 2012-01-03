
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
	import pvr.platform 
	platform = pvr.platform.getPlatform()
	platform.addLibsToSysPath()
	cacheDir = platform.getCacheDir()

	from pvr.util import MakeDir
	MakeDir( cacheDir )

	import launcher
	launcher.getInstance().run()

