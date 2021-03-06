import logging
import os
import socket
import sys
import xbmc
import xbmcaddon
import xbmcgui
import urllib
import stat


gPlatform = None


def GetPlatform():
    global gPlatform
    if not gPlatform:
        if 'win32' in sys.platform:
            gPlatform = WindowsPlatform()
        elif 'linux' in sys.platform:
            gPlatform = LinuxPlatform()
        elif 'darwin' in sys.platform:
            # gotta be a better way to detect ipad/iphone/atv2
            if 'USER' in os.environ and os.environ['USER'] in ('mobile','frontrow',):
                gPlatform = IOSPlatform()
            else: 
                gPlatform = MacPlatform()
        else:
            gPlatform = LinuxPlatform()
    return gPlatform


def MakeDir(dir):
    '''Create dir with missing path segments and return for chaining'''
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir


class Platform(object):

    def __init__(self, *args, **kwargs):
        self.addon = xbmcaddon.Addon('script.mbox')
        MakeDir(self.GetScriptDataDir())
        MakeDir(self.GetCacheDir())

    def GetMediaPath(self):
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
    
    def AddLibsToSysPath(self):
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
            'unittest',
            'beautifulsoup']
        
        for lib in libs:
            sys.path.append(os.path.join(self.GetScriptDir(), 'libs', lib))
        
        for i, path in enumerate(sys.path):    
            print 'lael98 check syspath[%d] = %s' % (i, path)
    
    def GetName(self):
        return "N/A"
    
    def GetScriptDir(self):
        '''
        @return: directory that this xbmc script resides in.
        
        linux  : ~/.xbmc/addons/script.mbox
        windows: c:\Documents and Settings\[user]\Application Data\XBMC\addons\script.mhbox
        mac    : ~/Library/Application Support/XBMC/addons/script.mbox
        '''
        return self.addon.getAddonInfo('path')
    
    def GetScriptDataDir(self):
        '''
        @return: directory for storing user settings for this xbmc script.
        
        linux  : ~/.xbmc/userdata/addon_data/script.mbox
        windows: c:\Documents and Settings\[user]\Application Data\XBMC\UserData\addon_data\script.mbox
        mac    : ~/Library/Application Support/XBMC/UserData/addon_data/script.mbox
        '''
        return xbmc.translatePath(self.addon.getAddonInfo('profile'))

    def GetSkinDir(self):
        return xbmc.translatePath('special://skin')

    def GetCacheDir(self):
        return os.path.join(self.GetScriptDataDir(), 'cache')
    
    def GetUserDataDir(self):
        return xbmc.translatePath('special://userdata')
    
    def GetHostname(self):
        try:
            return socket.GetHostname()
        except:
            return xbmc.getIPAddress()
     
    def IsLinux(self):
        return False

    def GetMediaPath(self, aMediaFile):
        # TODO: Fix when we support multiple skins
        return os.path.join(self.GetScriptDir(), 'resources', 'skins', 'Default', 'media', aMediaFile)
        

class LinuxPlatform(Platform):

    def __init__(self, *args, **kwargs):
        Platform.__init__(self, *args, **kwargs)
        
    def GetName(self):
        return "linux"
    
    def IsLinux(self):
        return True


class WindowsPlatform(Platform):

    def __init__(self, *args, **kwargs):
        Platform.__init__(self, *args, **kwargs)
    
    def GetName(self):
        return "windows"

        
class MacPlatform(Platform):

    def __init__(self, *args, **kwargs):
        Platform.__init__(self, *args, **kwargs)
        
    def GetName(self):
        return 'mac'

    
class IOSPlatform(Platform):
    
    def __init__(self, *args, **kwargs):
        Platform.__init__(self, *args, **kwargs)
        
    def GetName(self):
        return 'ios'

