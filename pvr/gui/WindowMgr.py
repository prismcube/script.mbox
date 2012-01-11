import xbmc
import xbmcgui
import sys
import time
import os
import shutil

from gui.BaseWindow import BaseWindow
from inspect import currentframe
from elementtree import ElementTree


WIN_ID_NULLWINDOW 					= 1
WIN_ID_MAINMENU 					= 2
WIN_ID_CHANNEL_LIST_WINDOW			= 3
WIN_ID_LIVE_PLATE					= 4
WIN_ID_CONFIGURE					= 5
WIN_ID_ANTENNA_SETUP				= 6
WIN_ID_TUNER_CONFIGURATION			= 7
WIN_ID_CONFIG_SIMPLE				= 8
WIN_ID_CONFIG_MOTORIZED_12			= 9
WIN_ID_CONFIG_MOTORIZED_USALS		= 10
WIN_ID_CONFIG_MOTORIZED_USALS2		= 11
WIN_ID_CONFIG_ONECABLE				= 12
WIN_ID_CONFIG_ONECABLE_2			= 13
WIN_ID_CONFIG_DISEQC_10				= 14
WIN_ID_CONFIG_DISEQC_11				= 15
WIN_ID_CHANNEL_SEARCH				= 16
WIN_ID_AUTOMATIC_SCAN				= 17
WIN_ID_MANUAL_SCAN					= 18
WIN_ID_TIMESHIFT_PLATE				= 19
WIN_ID_CHANNEL_EDIT_WINDOW			= 20
WIN_ID_EDIT_SATELLITE				= 21
WIN_ID_EDIT_TRANSPONDER				= 22
WIN_ID_ARCHIVE_WINDOW				= 23


gWindowMgr = None

def GetInstance():
	global gWindowMgr
	if not gWindowMgr:
		print 'lael98 check create instance'
		gWindowMgr = WindowMgr()
	else:
		pass
		#print 'lael98 check already windowmgr is created'

	return gWindowMgr


class WindowMgr(object):
	def __init__(self):
		print 'lael98 check %d %s' %(currentframe().f_lineno, currentframe().f_code.co_filename)

		import pvr.Platform 
		self.mScriptDir = pvr.Platform.GetPlatform().GetScriptDir()
		print 'lael98 test scriptDir= %s' %self.mScriptDir

		currentSkinName = xbmc.executehttpapi("GetGUISetting(3, lookandfeel.skin)")
		self.mSkinName = currentSkinName[4:]

		self.mSkinFontPath = []
		self.mScriptFontPath =[]
		self.mSkinDir = []
		self.mListDir = []

		self.AddDefaultFont( )		
		self.CopyIncludeFile( )


	def ShowWindow( self, aWindowId ):
		print'lael98 check %d %s winid=%d WIN_ID_NULLWINDOW=%d' %(currentframe().f_lineno, currentframe().f_code.co_filename, aWindowId, WIN_ID_NULLWINDOW)    
		try:
			if aWindowId ==  WIN_ID_NULLWINDOW:
				from pvr.gui.windows.NullWindow import NullWindow
				print 'self.mScriptDir=%s' %self.mScriptDir
				NullWindow('NullWindow.xml', self.mScriptDir ).doModal()

			elif aWindowId ==  WIN_ID_MAINMENU:
				from pvr.gui.windows.MainMenu import MainMenu
				MainMenu('MainMenu.xml', self.mScriptDir).doModal()

			elif aWindowId ==  WIN_ID_CHANNEL_LIST_WINDOW:
				from pvr.gui.windows.ChannelListWindow import ChannelListWindow
				ChannelListWindow('ChannelListWindow.xml', self.mScriptDir ).doModal()
				#ChannelListWindow('ChannelListWindow_b.xml', self.mScriptDir ).doModal()

			elif aWindowId ==  WIN_ID_LIVE_PLATE:
				from pvr.gui.windows.LivePlate import LivePlate
				LivePlate('LivePlate.xml', self.mScriptDir ).doModal()

			elif aWindowId == WIN_ID_TIMESHIFT_PLATE:
				from pvr.gui.windows.TimeshiftPlate import TimeShiftPlate
				TimeShiftPlate('TimeshiftPlate.xml', self.mScriptDir ).doModal()

			elif aWindowId ==  WIN_ID_CONFIGURE:
				from pvr.gui.windows.Configure import Configure	
				Configure('Configure.xml', self.mScriptDir).doModal()

			elif aWindowId ==  WIN_ID_ANTENNA_SETUP:
				from pvr.gui.windows.AntennaSetup import AntennaSetup
				AntennaSetup('AntennaSetup.xml', self.mScriptDir).doModal()

			elif aWindowId ==  WIN_ID_TUNER_CONFIGURATION:
				from pvr.gui.windows.TunerConfiguration import TunerConfiguration
				TunerConfiguration('TunerConfiguration.xml', self.mScriptDir).doModal()
				
			elif aWindowId ==  WIN_ID_CONFIG_SIMPLE:
				from pvr.gui.windows.SatelliteConfigSimple import SatelliteConfigSimple
				SatelliteConfigSimple('SatelliteConfiguration.xml', self.mScriptDir).doModal()

			elif aWindowId ==  WIN_ID_CONFIG_MOTORIZED_USALS:
				from pvr.gui.windows.SatelliteConfigMotorizedUsals import SatelliteConfigMotorizedUsals
				SatelliteConfigMotorizedUsals('SatelliteConfigMotorizedUsals.xml', self.mScriptDir).doModal()

			elif aWindowId ==  WIN_ID_CONFIG_MOTORIZED_USALS2:
				from pvr.gui.windows.SatelliteConfigMotorizedUsals2 import SatelliteConfigMotorizedUsals2
				SatelliteConfigMotorizedUsals2('SatelliteConfiguration.xml', self.mScriptDir).doModal()

			elif aWindowId ==  WIN_ID_CONFIG_MOTORIZED_12:
				from pvr.gui.windows.SatelliteConfigMotorized12 import SatelliteConfigMotorized12
				SatelliteConfigMotorized12('SatelliteConfiguration.xml', self.mScriptDir).doModal()

			elif aWindowId ==  WIN_ID_CONFIG_ONECABLE:
				from pvr.gui.windows.SatelliteConfigOnecable import SatelliteConfigOnecable
				SatelliteConfigOnecable('SatelliteConfigOnecable.xml', self.mScriptDir).doModal()

			elif aWindowId ==  WIN_ID_CONFIG_ONECABLE_2:
				from pvr.gui.windows.SatelliteConfigOnecable2 import SatelliteConfigOnecable2
				SatelliteConfigOnecable2('SatelliteConfigOnecable2.xml', self.mScriptDir).doModal()

			elif aWindowId ==  WIN_ID_CONFIG_DISEQC_10:
				from pvr.gui.windows.SatelliteConfigDisEqc10 import SatelliteConfigDisEqC10
				SatelliteConfigDisEqC10('SatelliteConfiguration.xml', self.mScriptDir).doModal()

			elif aWindowId ==  WIN_ID_CONFIG_DISEQC_11:
				from pvr.gui.windows.SatelliteConfigDisEqc11 import SatelliteConfigDisEqC11
				SatelliteConfigDisEqC11('SatelliteConfiguration.xml', self.mScriptDir).doModal()

			elif aWindowId ==  WIN_ID_CHANNEL_SEARCH:
				from pvr.gui.windows.ChannelSearch import ChannelSearch
				ChannelSearch('ChannelSearch.xml', self.mScriptDir).doModal()

			elif aWindowId ==  WIN_ID_AUTOMATIC_SCAN:
				from pvr.gui.windows.AutomaticScan import AutomaticScan	
				AutomaticScan('AutomaticScan.xml', self.mScriptDir).doModal()

			elif aWindowId ==  WIN_ID_MANUAL_SCAN:
				from pvr.gui.windows.ManualScan import ManualScan
				ManualScan('ManualScan.xml', self.mScriptDir).doModal()

			elif aWindowId ==  WIN_ID_EDIT_SATELLITE:
				from pvr.gui.windows.EditSatellite import EditSatellite
				EditSatellite('EditSatellite.xml', self.mScriptDir).doModal()

			elif aWindowId ==  WIN_ID_EDIT_TRANSPONDER:
				from pvr.gui.windows.EditTransponder import EditTransponder
				EditTransponder('EditTransponder.xml', self.mScriptDir).doModal()

			elif aWindowId ==  WIN_ID_CHANNEL_EDIT_WINDOW:
				#from pvr.gui.windows.channeleditwindow import ChannelEditWindow
				#ChannelEditWindow('channeleditwindow.xml', self.mScriptDir )
				pass
			

			elif aWindowId ==  WIN_ID_ARCHIVE_WINDOW:
				from pvr.gui.windows.ArchiveWindow import ArchiveWindow
				ArchiveWindow('ArchiveWindow.xml', self.mScriptDir ).doModal()

			else :
				print 'Unknown widnowId=%d' %aWindowId

			self.mLastId = aWindowId

		except Exception, ex:
			print "Exception %s" %ex
			



	def Reset( self ):
		import pvr.Platform 
		self.mScriptDir = pvr.Platform.GetPlatform().GetScriptDir()
	
		self.CopyIncludeFile( )
		self.showWindow( WIN_ID_MAINMENU )


	def CheckSkinChange( self ):

		currentSkinName = xbmc.executehttpapi("GetGUISetting(3, lookandfeel.skin)")

		print 'skin name=%s : %s' %( self.mSkinName, currentSkinName[4:] )

		if self.mSkinName != currentSkinName[4:] :
			print 'change skin name'
			self.mSkinName = currentSkinName[4:]
			self.Reset( )


	def CopyIncludeFile( self ):
		import os, shutil
		import pvr.Platform 

		skinName = self.mSkinName

		print 'skinName=%s' %skinName

		import pvr.Platform 
		self.mScriptDir = pvr.Platform.GetPlatform().GetScriptDir()

		
		if skinName.lower() == 'default' or skinName.lower() == 'skin.confluence' :
			mboxIncludePath = os.path.join( pvr.Platform.GetPlatform().GetScriptDir(), 'resources', 'skins', 'default', '720p', 'mbox_includes.xml')

		else : 
			mboxIncludePath = os.path.join( pvr.Platform.GetPlatform().GetScriptDir(), 'resources', 'skins', skinName, '720p', 'mbox_includes.xml')

			if not os.path.isfile(mboxIncludePath) :
				mboxIncludePath = os.path.join( pvr.Platform.GetPlatform().GetScriptDir(), 'resources', 'skins', 'default', '720p', 'mbox_includes.xml')			
			
		print 'mboxIncludePath=%s' %mboxIncludePath	

		skinIncludePath = os.path.join( pvr.Platform.GetPlatform().GetSkinDir(), '720p', 'mbox_includes.xml')
		print 'skinIncludePath=%s' %skinIncludePath	
		shutil.copyfile( mboxIncludePath, skinIncludePath )


	def GetWindow( self, aWindowId ) :
		pass



	def AddDefaultFont( self ) :
		self.mSkinFontPath = xbmc.translatePath("special://skin/fonts/")
		self.mScriptFontPath = os.path.join(os.getcwd() , "resources" , "fonts")
		self.mSkinDir = xbmc.translatePath("special://skin/")
		self.mListDir = os.listdir( self.mSkinDir )

		self.AddFont( "font35_title", "DejaVuSans-Bold.ttf", "35" )
		self.AddFont( "font12_title", "DejaVuSans-Bold.ttf", "16" )


	def GetFontsXML( self ):

		fontPaths = []

		try:
			for subDir in self.mListDir:
				subDir = os.path.join( self.mSkinDir, subDir )
				
				if os.path.isdir( subDir ):
					fontXml = os.path.join( subDir, "Font.xml" )
					
					if os.path.exists( fontXml ):
						fontPaths.append( fontXml )

		except:
			print 'Err : GetFontsXML Error'
			return []

		return fontPaths


	def HasFontInstalled( self, aFontXMLPath, aFontName ):
		name = "<name>%s</name>" % aFontName

		if not name in file( aFontXMLPath, "r" ).read():
			print '%s font is not installed!' %aFontName
			return False
			
		else:
			print '%s font already installed!' %aFontName

		return True


	def AddFont( self, aFontName, aFileName, aSize, aStyle="", aAspect="" ):

		try:
			needReloadSkin = False
			fontPaths = self.GetFontsXML( )

			if fontPaths:
				for fontXMLPath in fontPaths:
					if not self.HasFontInstalled( fontXMLPath, aFontName ):
						tree = ElementTree.parse( fontXMLPath )
						root = tree.getroot( )

						for sets in root.getchildren( ):
							sets.findall( "font" )[ -1 ].tail = "\n\t\t"
							new = ElementTree.SubElement( sets, "font" )
							new.text, new.tail = "\n\t\t\t", "\n\t"

							subNew1=ElementTree.SubElement( new, "name" )
							subNew1.text = aFontName
							subNew1.tail = "\n\t\t\t"
							subNew2=ElementTree.SubElement( new, "aFileName" )
							subNew2.text = ( aFileName, "Arial.ttf" )[ sets.attrib.get( "id" ) == "Arial" ]
							subNew2.tail = "\n\t\t\t"
							subNew3=ElementTree.SubElement( new, "size" )
							subNew3.text = aSize
							subNew3.tail = "\n\t\t\t"
							lastElement = subNew3

							if aStyle in [ "normal", "bold", "italics", "bolditalics" ]:
								subNew4=ElementTree.SubElement(new ,"style")
								subNew4.text = aStyle
								subNew4.tail = "\n\t\t\t"
								lastElement = subNew4
							if aAspect:    
								subNew5=ElementTree.SubElement(new ,"aspect")
								subNew5.text = aAspect
								subNew5.tail = "\n\t\t\t"
								lastElement = subNew5
							needReloadSkin = True

							lastElement.tail = "\n\t\t"
						tree.write(fontXMLPath)
						needReloadSkin = True
		except:
			print 'Error AddFontErr'

		if needReloadSkin:
 			if not os.path.exists( os.path.join( self.mSkinFontPath, aFileName ) ) and os.path.exists( os.path.join( self.mScriptFontPath, aFileName ) ):
				shutil.copyfile( os.path.join( self.mScriptFontPath, aFileName ), os.path.join( self.mSkinFontPath, aFileName ) )

			xbmc.executebuiltin( "XBMC.ReloadSkin()" )
			return True

		return False

