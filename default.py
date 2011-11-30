
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

	mboxIncludePath = os.path.join( platform.getScriptDir(), 'resources', 'skins', 'Default', '720p', 'mbox_includes.xml')
	print 'mboxIncludePath=%s' %mboxIncludePath	

	skinIncludePath = os.path.join( platform.getSkinDir(), '720p', 'mbox_includes.xml')
	print 'skinIncludePath=%s' %skinIncludePath	
	shutil.copyfile( mboxIncludePath, skinIncludePath )

	import launcher
	launcher.getInstance().run()

