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
WIN_ID_LANGUAGE_SETTING				= 5
WIN_ID_PARENTAL_LOCK				= 6
WIN_ID_CONFIGURE					= 7


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

		from pvr.gui.windows.nullwindow import NullWindow		
		self.nullWindow =  NullWindow('nullwindow.xml', self.scriptDir )

		self.createAllWindows( )


	def showWindow( self, windowId ):
		print'lael98 check %d %s winid=%d' %(currentframe().f_lineno, currentframe().f_code.co_filename, windowId)    
		try:
			if windowId == WIN_ID_NULLWINDOW :
				self.nullWindow.doModal()
			else:
				self.windows[windowId].doModal()
 			self.lastId = windowId

		except:
			print "can not find window"


	def createAllWindows( self ):
		import pvr.platform 
		self.scriptDir = pvr.platform.getPlatform().getScriptDir()
		print 'lael98 test scriptDir= %s' %self.scriptDir

		from pvr.gui.windows.mainmenu import MainMenu
		from pvr.gui.windows.channellistwindow import ChannelListWindow
		from pvr.gui.windows.channelbanner import ChannelBanner
		from pvr.gui.windows.languagesetting import LanguageSetting
		from pvr.gui.windows.parentallock import ParentalLock
		from pvr.gui.windows.configure import Configure


		self.windows[ WIN_ID_MAINMENU ]	= MainMenu('mainmenu.xml', self.scriptDir)
		self.windows[ WIN_ID_CHANNEL_LIST_WINDOW ] = ChannelListWindow('channellistwindow.xml', self.scriptDir )
		self.windows[ WIN_ID_CHANNEL_BANNER	] = ChannelBanner('channelbanner.xml', self.scriptDir )
		self.windows[ WIN_ID_LANGUAGE_SETTING ]= LanguageSetting('languagesetting.xml', self.scriptDir)
		self.windows[ WIN_ID_PARENTAL_LOCK ] = ParentalLock('parentallock.xml', self.scriptDir )
		self.windows[ WIN_ID_CONFIGURE ] = Configure('configure.xml', self.scriptDir)


	def resetAllWindows( self ):
		self.windows[ WIN_ID_MAINMENU ].close( )
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

		
	
