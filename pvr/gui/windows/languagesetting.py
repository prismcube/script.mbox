
import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import BaseWindow, setWindowBusy
from pvr.gui.basewindow import Action
import pvr.elismgr
from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt


class LanguageSetting(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance().getCommander()
		print 'dhkim __init__ test'

		self.OsdLanguageList = [1, 2, 3, 4, 5]

	def onInit(self):
		if not self.win:
			self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())

		self.ctrlOSDLanguagelist					= self.getControl( 9100 )
		self.ctrlOSDLanguagelist.addItems(self.OsdLanguageList)
		'''
		print 'dhkim test for'
		osdLangProp = ElisPropertyEnum( 'Language' )
		value = osdLangProp.getProp()

		count = osdLangProp.getIndexCount()
		for i in range( count ):
			self.ctrlOSDLanguagelist.append(osdLangProp.getName() + osdLangProp.getPropString( i ))
		
			#strName = osdLangProp.getName() + osdLangProp.getPropString( i )
			#osdLangProp.addLabel( strName, osdLangProp.getPropByIndex( i ) )
			#if osdLangProp.getPropByIndex( i ) == value
			#	osdLangProp.setValue( value )

		
		self.ctrlOSDLanguagelist.addItems(self.OsdLanguageList)
		'''
		'''
		self.ctrlRootGroup.addItems(testlist)
		# OSDLanguage
		print 'dhkim OnInit test'
		osdLangProp = ElisPropertyEnum( 'Language' )
		value = osdLangProp.getProp()
		
		#count = osdLangProp.getIndexCount()
		#for i in range( count ):
		#strName = osdLangProp.getName()
			# + osdLangProp.getPropString( value )
		print 'dhkim property test = %s' % strName
		self.ctrlOSDLanguage.addItem( strName )
			#if osdLangProp.getPropByIndex( i ) == value
			#	osdLangProp.setValue( value )
		'''
		
		'''
		self.ctrlOSDLanguage    			= self.getControl( 101 )
		self.ctrlPrimaryAudioLanguage    	= self.getControl( 102 )
		self.ctrlPrimarySubtitleLanguage    = self.getControl( 103 )
		self.ctrlSecondarySubtitleLanguage  = self.getControl( 104 )
		self.ctrlHearingImpaired 			= self.getControl( 105 )
		
		osdLangProp = ElisPropertyEnum( 'Language' )
		value = osdLangProp.getProp()
		
		count = osdLangProp.getIndexCount()
		for i range( count )
			strName = osdLangProp.getName() + osdLangProp.getPropString( i )
			osdLangProp.addLabel( strName, osdLangProp.getPropByIndex( i ) )
			if osdLangProp.getPropByIndex( i ) == value
				osdLangProp.setValue( value )
		'''

	def onAction(self, action):
 		
		id = action.getId()
		
		if id == Action.ACTION_PREVIOUS_MENU:
			print 'dhkim LanguageSetting check action previous'
		elif id == Action.ACTION_SELECT_ITEM:
			print 'dhkim LanguageSetting check action select'
		elif id == Action.ACTION_PARENT_DIR:
			winmgr.getInstance().showWindow( winmgr.WIN_ID_MAINMENU )
			print 'dhkim LanguageSetting check action parent'

	def onClick(self, controlId):
		print "MenuReceiverSetupNetwork onclick(): control %d" % controlId	

	def onFocus(self, controlId):
		print "onFocus(): control %d" % controlId


