import xbmc
import xbmcgui
import sys
import time

from gui.basewindow import BaseWindow
from inspect import currentframe

WIN_ID_NULLWINDOW 					= 1
WIN_ID_MAINMENU 					= 2
WIN_ID_CHANNEL_LIST_WINDOW			= 3
WIN_ID_CHANNEL_BANNER				= 4
WIN_ID_CONFIGURE					= 5
WIN_ID_ANTENNA_SETUP				= 6
WIN_ID_TUNER_CONFIGURATION			= 7
WIN_ID_SATELLITE_CONFIGURATION		= 8
WIN_ID_TIMESHIFT_BANNER				= 9

WIN_ID_LANGUAGE_SETTING				= 100	#for test

__windowmgr = None

def getInstance():
	global __windowmgr
	if not __windowmgr:
		print 'lael98 check create instance'
		__windowmgr = WindowMgr()
	else:
		print 'lael98 check already windowmgr is created'

	return __windowmgr


class WindowMgr(object):
	def __init__(self):
		print 'lael98 check %d %s' %(currentframe().f_lineno, currentframe().f_code.co_filename)

		import pvr.platform 
		self.scriptDir = pvr.platform.getPlatform().getScriptDir()
		print 'lael98 test scriptDir= %s' %self.scriptDir

		currentSkinName = xbmc.executehttpapi("GetGUISetting(3, lookandfeel.skin)")
		self.skinName = currentSkinName[4:]

		self.windows = {}

		self.copyIncludeFile( )
		self.createAllWindows( )


	def showWindow( self, windowId ):
		print'lael98 check %d %s winid=%d' %(currentframe().f_lineno, currentframe().f_code.co_filename, windowId)    
		try:
			self.windows[windowId].doModal()
 			self.lastId = windowId

		except:
			print "can not find window"


	def createAllWindows( self ):
		import pvr.platform 
		self.scriptDir = pvr.platform.getPlatform().getScriptDir()
		print 'lael98 test scriptDir= %s' %self.scriptDir

		from pvr.gui.windows.nullwindow import NullWindow		
		from pvr.gui.windows.mainmenu import MainMenu
		from pvr.gui.windows.channellistwindow import ChannelListWindow
		from pvr.gui.windows.channelbanner import ChannelBanner
		from pvr.gui.windows.timeshiftbanner import TimeShiftBanner
		from pvr.gui.windows.configure import Configure
		from pvr.gui.windows.antennasetup import AntennaSetup
		from pvr.gui.windows.tunerconfiguration import TunerConfiguration
		from pvr.gui.windows.satelliteconfiguration import SatelliteConfiguration			
		from pvr.gui.windows.languagesetting import LanguageSetting		#for test


		self.windows[ WIN_ID_NULLWINDOW ]             = NullWindow('nullwindow.xml', self.scriptDir )
		self.windows[ WIN_ID_MAINMENU ]	               = MainMenu('mainmenu.xml', self.scriptDir)
		self.windows[ WIN_ID_CHANNEL_LIST_WINDOW ]     = ChannelListWindow('channellistwindow.xml', self.scriptDir )
		self.windows[ WIN_ID_CHANNEL_BANNER	]          = ChannelBanner('channelbanner.xml', self.scriptDir )
		self.windows[ WIN_ID_TIMESHIFT_BANNER ]        = TimeShiftBanner('timeshiftbanner.xml', self.scriptDir )
		self.windows[ WIN_ID_CONFIGURE ]               = Configure('configure.xml', self.scriptDir)
		self.windows[ WIN_ID_ANTENNA_SETUP ]           = AntennaSetup('antennasetup.xml', self.scriptDir)
		self.windows[ WIN_ID_TUNER_CONFIGURATION ]     = TunerConfiguration('tunerconfiguration.xml', self.scriptDir)
		self.windows[ WIN_ID_SATELLITE_CONFIGURATION ] = SatelliteConfiguration('satelliteconfiguration.xml', self.scriptDir)
		self.windows[ WIN_ID_LANGUAGE_SETTING ]        = LanguageSetting('languagesetting.xml', self.scriptDir)		#for test
		

	def resetAllWindows( self ):
		self.windows[ WIN_ID_MAINMENU ].close( )
		self.copyIncludeFile( )		
		self.windows.clear( )
		self.createAllWindows( )
		self.showWindow( WIN_ID_MAINMENU )


	def checkSkinChange( self ):

		currentSkinName = xbmc.executehttpapi("GetGUISetting(3, lookandfeel.skin)")

		print 'skin name=%s : %s' %( self.skinName, currentSkinName[4:] )

		if self.skinName != currentSkinName[4:] :
			print 'change skin name'
			self.skinName = currentSkinName[4:]			
			self.resetAllWindows( )


	def copyIncludeFile( self ):
		import os, shutil
		import pvr.platform 

		skinName = self.skinName

		print 'skinName=%s' %skinName

		import pvr.platform 
		self.scriptDir = pvr.platform.getPlatform().getScriptDir()

		
		if skinName.lower() == 'default' or skinName.lower() == 'skin.confluence' :
			mboxIncludePath = os.path.join( pvr.platform.getPlatform().getScriptDir(), 'resources', 'skins', 'default', '720p', 'mbox_includes.xml')

		else : 
			mboxIncludePath = os.path.join( pvr.platform.getPlatform().getScriptDir(), 'resources', 'skins', skinName, '720p', 'mbox_includes.xml')

			if not os.path.isfile(mboxIncludePath) :
				mboxIncludePath = os.path.join( pvr.platform.getPlatform().getScriptDir(), 'resources', 'skins', 'default', '720p', 'mbox_includes.xml')			
			
		print 'mboxIncludePath=%s' %mboxIncludePath	

		skinIncludePath = os.path.join( pvr.platform.getPlatform().getSkinDir(), '720p', 'mbox_includes.xml')
		print 'skinIncludePath=%s' %skinIncludePath	
		shutil.copyfile( mboxIncludePath, skinIncludePath )


	def getWindow( self, windowId ) :
		return self.windows[ windowId ]
