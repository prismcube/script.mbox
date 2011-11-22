#
#  MythBox for XBMC
#
#  Copyright (C) 2011 analogue@yahoo.com 
#  http://mythbox.googlecode.com
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
##

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

