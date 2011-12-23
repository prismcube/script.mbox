import xbmc
import xbmcgui
import sys
import time
import os
import shutil

from gui.basewindow import BaseWindow
from inspect import currentframe
from elementtree import ElementTree


WIN_ID_NULLWINDOW 					= 1
WIN_ID_MAINMENU 					= 2
WIN_ID_CHANNEL_LIST_WINDOW			= 3
WIN_ID_CHANNEL_BANNER				= 4
WIN_ID_CONFIGURE					= 5
WIN_ID_ANTENNA_SETUP				= 6
WIN_ID_TUNER_CONFIGURATION			= 7
WIN_ID_SATELLITE_CONFIGURATION		= 8
WIN_ID_CHANNEL_SEARCH				= 9
WIN_ID_AUTOMATIC_SCAN				= 10
WIN_ID_MANUAL_SCAN					= 11
WIN_ID_TIMESHIFT_BANNER				= 12

WIN_ID_LANGUAGE_SETTING				= 100	#for test
WIN_ID_CHANNEL_LIST2_WINDOW			= 103	#for test



__windowmgr = None

def getInstance():
	global __windowmgr
	if not __windowmgr:
		print 'lael98 check create instance'
		__windowmgr = WindowMgr()
	else:
		pass
		#print 'lael98 check already windowmgr is created'

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
		self.skinFontPath = []
		self.scriptFontPath =[]
		self.skinDir = []
		self.listDir = []
		

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

		self.addDefaultFont( )

		from pvr.gui.windows.nullwindow import NullWindow		
		from pvr.gui.windows.mainmenu import MainMenu
		from pvr.gui.windows.channellistwindow import ChannelListWindow
		from pvr.gui.windows.channelbanner import ChannelBanner
		from pvr.gui.windows.timeshiftbanner import TimeShiftBanner
		from pvr.gui.windows.configure import Configure
		from pvr.gui.windows.antennasetup import AntennaSetup
		from pvr.gui.windows.tunerconfiguration import TunerConfiguration
		from pvr.gui.windows.satelliteconfiguration import SatelliteConfiguration
		from pvr.gui.windows.channelsearch import ChannelSearch
		from pvr.gui.windows.automaticscan import AutomaticScan
		from pvr.gui.windows.manualscan import ManualScan
		from pvr.gui.windows.languagesetting import LanguageSetting		#for test
		from pvr.gui.windows.channellistwindow_b import ChannelListWindow_b #for test


		self.windows[ WIN_ID_NULLWINDOW ]				= NullWindow('nullwindow.xml', self.scriptDir )
		self.windows[ WIN_ID_MAINMENU ]					= MainMenu('mainmenu.xml', self.scriptDir)
		self.windows[ WIN_ID_CHANNEL_LIST_WINDOW ]		= ChannelListWindow('channellistwindow.xml', self.scriptDir )
		self.windows[ WIN_ID_CHANNEL_BANNER	]			= ChannelBanner('channelbanner.xml', self.scriptDir )
		self.windows[ WIN_ID_TIMESHIFT_BANNER ]			= TimeShiftBanner('timeshiftbanner.xml', self.scriptDir )
		self.windows[ WIN_ID_CONFIGURE ]				= Configure('configure.xml', self.scriptDir)
		self.windows[ WIN_ID_ANTENNA_SETUP ]			= AntennaSetup('antennasetup.xml', self.scriptDir)
		self.windows[ WIN_ID_TUNER_CONFIGURATION ]		= TunerConfiguration('tunerconfiguration.xml', self.scriptDir)
		self.windows[ WIN_ID_SATELLITE_CONFIGURATION ]	= SatelliteConfiguration('satelliteconfiguration.xml', self.scriptDir)
		self.windows[ WIN_ID_CHANNEL_SEARCH ]			= ChannelSearch('channelsearch.xml', self.scriptDir)
		self.windows[ WIN_ID_AUTOMATIC_SCAN ]			= AutomaticScan('automaticscan.xml', self.scriptDir)
		self.windows[ WIN_ID_MANUAL_SCAN ]				= ManualScan('manualscan.xml', self.scriptDir)
		self.windows[ WIN_ID_LANGUAGE_SETTING ]			= LanguageSetting('languagesetting.xml', self.scriptDir)		#for test
		self.windows[ WIN_ID_CHANNEL_LIST2_WINDOW ]		= ChannelListWindow_b('channellistwindow_b.xml', self.scriptDir )	#for test
		

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


	def addDefaultFont( self ) :
		self.skinFontPath = xbmc.translatePath("special://skin/fonts/")
		self.scriptFontPath = os.path.join(os.getcwd() , "resources" , "fonts")
		self.skinDir = xbmc.translatePath("special://skin/")
		self.listDir = os.listdir( self.skinDir )

		self.addFont( "font35_title", "DejaVuSans-Bold.ttf", "35" )
		self.addFont( "font12_title", "DejaVuSans-Bold.ttf", "16" )


	def getFontsXML( self ):

		fontPaths = []

		try:
			for subDir in self.listDir:
				subDir = os.path.join( self.skinDir, subDir )
				
				if os.path.isdir( subDir ):
					fontXml = os.path.join( subDir, "Font.xml" )
					
					if os.path.exists( fontXml ):
						fontPaths.append( fontXml )

		except:
			print 'Err : getFontsXML Error'
			return []

		return fontPaths


	def hasFontInstalled( self, fontXMLPath, fontName ):
		name = "<name>%s</name>" % fontName

		if not name in file( fontXMLPath, "r" ).read():
			print '%s font is not installed!' %fontName
			return False
			
		else:
			print '%s font already installed!' %fontName

		return True


	def addFont( self, fontName, fileName, size, style="", aspect="" ):

		try:
			needReloadSkin = False
			fontPaths = self.getFontsXML( )

			if fontPaths:
				for fontXMLPath in fontPaths:
					if not self.hasFontInstalled( fontXMLPath, fontName ):
						tree = ElementTree.parse( fontXMLPath )
						root = tree.getroot( )

						for sets in root.getchildren( ):
							sets.findall( "font" )[ -1 ].tail = "\n\t\t"
							new = ElementTree.SubElement( sets, "font" )
							new.text, new.tail = "\n\t\t\t", "\n\t"

							subNew1=ElementTree.SubElement( new, "name" )
							subNew1.text = fontName
							subNew1.tail = "\n\t\t\t"
							subNew2=ElementTree.SubElement( new, "filename" )
							subNew2.text = ( fileName, "Arial.ttf" )[ sets.attrib.get( "id" ) == "Arial" ]
							subNew2.tail = "\n\t\t\t"
							subNew3=ElementTree.SubElement( new, "size" )
							subNew3.text = size
							subNew3.tail = "\n\t\t\t"
							lastElement = subNew3

							if style in [ "normal", "bold", "italics", "bolditalics" ]:
								subNew4=ElementTree.SubElement(new ,"style")
								subNew4.text = style
								subNew4.tail = "\n\t\t\t"
								lastElement = subNew4
							if aspect:    
								subNew5=ElementTree.SubElement(new ,"aspect")
								subNew5.text = aspect
								subNew5.tail = "\n\t\t\t"
								lastElement = subNew5
							needReloadSkin = True

							lastElement.tail = "\n\t\t"
						tree.write(fontXMLPath)
						needReloadSkin = True
		except:
			print 'Error addFontErr'

		if needReloadSkin:
 			if not os.path.exists( os.path.join( self.skinFontPath, fileName ) ) and os.path.exists( os.path.join( self.scriptFontPath, fileName ) ):
				shutil.copyfile( os.path.join( self.scriptFontPath, fileName ), os.path.join( self.skinFontPath, fileName ) )

			xbmc.executebuiltin( "XBMC.ReloadSkin()" )
			return True

		return False

