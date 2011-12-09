
if __name__ == '__main__':
	import os, sys, xbmcaddon, shutil
	scriptDir = xbmcaddon.Addon('script.mbox').getAddonInfo('path')
	sys.path.append(os.path.join(scriptDir, 'pvr'))
	sys.path.append(os.path.join(scriptDir, 'resources'))	

#	import xbmcgui
#	import xbmc
#	loading = xbmcgui.WindowXML('loading.xml', scriptDir)
#	loading.show()
	import pvr.platform 
	platform = pvr.platform.getPlatform()
	platform.addLibsToSysPath()
	cacheDir = platform.getCacheDir()

	from pvr.util import requireDir
	requireDir( cacheDir )

	import launcher
	launcher.getInstance().run()

