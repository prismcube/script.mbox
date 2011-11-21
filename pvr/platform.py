#
#  MythBox for XBMC - http://mythbox.googlecode.com
#  Copyright (C) 2011 analogue@yahoo.com
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
import logging
import os
import socket
import sys
import xbmc
import xbmcaddon
import xbmcgui
import urllib
import stat


__platform = None


def getPlatform():
    global __platform
    if not __platform:
        if 'win32' in sys.platform:
            __platform = WindowsPlatform()
        elif 'linux' in sys.platform:
            __platform = LinuxPlatform()
        elif 'darwin' in sys.platform:
            # gotta be a better way to detect ipad/iphone/atv2
            if 'USER' in os.environ and os.environ['USER'] in ('mobile','frontrow',):
                __platform = IOSPlatform()
            else: 
                __platform = MacPlatform()
        else:
            __platform = LinuxPlatform()
    return __platform


def requireDir(dir):
    '''Create dir with missing path segments and return for chaining'''
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir


class Platform(object):

    def __init__(self, *args, **kwargs):
        self.addon = xbmcaddon.Addon('script.mbox')
        requireDir(self.getScriptDataDir())
        requireDir(self.getCacheDir())

    def xbmcVersion(self):
        version = 0.0
        vs = xbmc.getInfoLabel('System.BuildVersion')
        try: 
            # sample input: '10.1 Git:Unknown'
            version = float(vs.split()[0])
        except ValueError:
            try:
                # sample input: 'PRE-11.0 Git:Unknown'
                version = float(vs.split()[0].split('-')[1])
            except ValueError:
                print('Cannot determine version of XBMC from build version: %s. Returning %s' % (vs, version))
        return version
    
    def addLibsToSysPath(self):
        '''Add 3rd party libs in ${scriptdir}/resources/lib to the PYTHONPATH'''
        libs = [
            'decorator', 
            'odict',
            'bidict', 
            'elementtree', 
            'tvdb_api', 
            'tvrage',
            'themoviedb', 
            'IMDbPY', 
            'simplejson', 
            'mysql-connector-python',
            'python-twitter',
            'twisted',
            'zope.interface',
            'mockito',
            'unittest2',
            'unittest']
        
        for lib in libs:
            sys.path.append(os.path.join(self.getScriptDir(), 'libs', lib))
        
        for i, path in enumerate(sys.path):    
            print 'lael98 check syspath[%d] = %s' % (i, path)
    
    def getName(self):
        return "N/A"
    
    def getScriptDir(self):
        '''
        @return: directory that this xbmc script resides in.
        
        linux  : ~/.xbmc/addons/script.mbox
        windows: c:\Documents and Settings\[user]\Application Data\XBMC\addons\script.mhbox
        mac    : ~/Library/Application Support/XBMC/addons/script.mbox
        '''
        return self.addon.getAddonInfo('path')
    
    def getScriptDataDir(self):
        '''
        @return: directory for storing user settings for this xbmc script.
        
        linux  : ~/.xbmc/userdata/addon_data/script.mbox
        windows: c:\Documents and Settings\[user]\Application Data\XBMC\UserData\addon_data\script.mbox
        mac    : ~/Library/Application Support/XBMC/UserData/addon_data/script.mbox
        '''
        return xbmc.translatePath(self.addon.getAddonInfo('profile'))

    def getSkinDir(self):
        return xbmc.translatePath('special://skin')

    def getCacheDir(self):
        return os.path.join(self.getScriptDataDir(), 'cache')
    
    def getUserDataDir(self):
        return xbmc.translatePath('special://userdata')
    
    def getHostname(self):
        try:
            return socket.gethostname()
        except:
            return xbmc.getIPAddress()
     
    def isLinux(self):
        return False
    
    def addonVersion(self):
        return self.addon.getAddonInfo('version')
            
    def __repr__(self):
        bar = "=" * 80
        s = bar + \
"""
hostname        = %s
platform        = %s 
script dir      = %s
script data dir = %s
""" % (self.getHostname(), type(self).__name__, self.getScriptDir(), self.getScriptDataDir())
        s += bar
        return s
    
    def getDefaultRecordingsDir(self):
        return ''

    def getMediaPath(self, mediaFile):
        # TODO: Fix when we support multiple skins
        return os.path.join(self.getScriptDir(), 'resources', 'skins', 'Default', 'media', mediaFile)
        
    def showPopup(self, title, text, millis=10000):
        # filter all commas out of text since they delimit args
        title = title.replace(',', ';')
        text = text.replace(',', ';')
        s = u'XBMC.Notification(%s,%s,%s)' % (title, text, millis)
        xbmc.executebuiltin(s)


class LinuxPlatform(Platform):

    def __init__(self, *args, **kwargs):
        Platform.__init__(self, *args, **kwargs)
        
    def getName(self):
        return "linux"
    
    def isLinux(self):
        return True


class WindowsPlatform(Platform):

    def __init__(self, *args, **kwargs):
        Platform.__init__(self, *args, **kwargs)
    
    def getName(self):
        return "windows"

        
class MacPlatform(Platform):

    def __init__(self, *args, **kwargs):
        Platform.__init__(self, *args, **kwargs)
        
    def getName(self):
        return 'mac'

    
class IOSPlatform(Platform):
    
    def __init__(self, *args, **kwargs):
        Platform.__init__(self, *args, **kwargs)
        
    def getName(self):
        return 'ios'

