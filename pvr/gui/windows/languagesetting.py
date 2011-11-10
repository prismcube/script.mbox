
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

		# Description List
		self.DescriptionList					= ['Set menu and popup language', 'Set primary audio language', 'Set primary subtitle language', 'Set secondary subtitle language', 'Enable hearing impaired support']

		# OSD Language
		self.osdlangugelist 					= []
		self.osdLanguageProperty				= ElisPropertyEnum( 'Language' )
		
		for i in range( self.osdLanguageProperty.getIndexCount() ):
			listItem = xbmcgui.ListItem(self.osdLanguageProperty.getName(), self.osdLanguageProperty.getPropStringByIndex( i ),"-", "-", "-")
			self.osdlangugelist.append(listItem)

		# Primary Audio Language
		self.primaryAudioLanguagelist 			= []
		self.primaryAudioLanguageProperty		= ElisPropertyEnum( 'Audio Language' )

		for i in range( self.primaryAudioLanguageProperty.getIndexCount() ):
			listItem = xbmcgui.ListItem(self.primaryAudioLanguageProperty.getName(), self.primaryAudioLanguageProperty.getPropStringByIndex( i ),"-", "-", "-")
			self.primaryAudioLanguagelist.append(listItem)

		# Primary Subtitle Language
		self.primarySubtitleLanguagelist 		= []
		self.primarySubtitleLanguageProperty	= ElisPropertyEnum( 'Subtitle Language' )
		
		for i in range( self.primarySubtitleLanguageProperty.getIndexCount() ):
			listItem = xbmcgui.ListItem(self.primarySubtitleLanguageProperty.getName(), self.primarySubtitleLanguageProperty.getPropStringByIndex( i ),"-", "-", "-")
			self.primarySubtitleLanguagelist.append(listItem)

		# Secondary Subtitle Language
		self.secondarySubtitleLanguagelist 		= []
		self.secondarySubtitleLanguageProperty	= ElisPropertyEnum( 'Secondary Subtitle Language' )
		
		for i in range( self.secondarySubtitleLanguageProperty.getIndexCount() ):
			listItem = xbmcgui.ListItem(self.secondarySubtitleLanguageProperty.getName(), self.secondarySubtitleLanguageProperty.getPropStringByIndex( i ),"-", "-", "-")
			self.secondarySubtitleLanguagelist.append(listItem)

		# For The Hearing Impaired
		self.forTheHearingImpairedlist		 	= []
		self.forTheHearingImpairedProperty		= ElisPropertyEnum( 'Hearing Impaired' )
		
		for i in range( self.forTheHearingImpairedProperty.getIndexCount() ):
			listItem = xbmcgui.ListItem(self.forTheHearingImpairedProperty.getName(), self.forTheHearingImpairedProperty.getPropStringByIndex( i ),"-", "-", "-")
			self.forTheHearingImpairedlist.append(listItem)


	def onInit(self):
		if not self.win:
			self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())

		# OSD Language
		self.ctrlOSDLanguage				= self.getControl( 9100 )
		self.ctrlOSDLanguage.addItems( self.osdlangugelist )
		self.ctrlOSDLanguage.selectItem( self.osdLanguageProperty.getProp() )

		# Primary Audio Language
		self.ctrlPrimaryAudioLanguage		= self.getControl( 9101 )
		self.ctrlPrimaryAudioLanguage.addItems( self.primaryAudioLanguagelist )
		self.ctrlPrimaryAudioLanguage.selectItem( self.primaryAudioLanguageProperty.getProp() )

		# Primary Audio Language
		self.ctrlPrimarySubtitleLanguage	= self.getControl( 9102 )
		self.ctrlPrimarySubtitleLanguage.addItems( self.primarySubtitleLanguagelist )
		self.ctrlPrimarySubtitleLanguage.selectItem( self.primarySubtitleLanguageProperty.getProp() )

		# Secondary Subtitle Language
		self.ctrlSecondarySubtitleLanguage	= self.getControl( 9103 )
		self.ctrlSecondarySubtitleLanguage.addItems( self.secondarySubtitleLanguagelist )
		self.ctrlSecondarySubtitleLanguage.selectItem( self.secondarySubtitleLanguageProperty.getProp() )

		# For The Hearing Impaired
		self.ctrlForTheHearingImpaired		= self.getControl( 9104 )
		self.ctrlForTheHearingImpaired.addItems( self.forTheHearingImpairedlist )
		self.ctrlForTheHearingImpaired.selectItem( self.forTheHearingImpairedProperty.getProp() )

		# Description Label
		self.ctrlDescriptionLabel			= self.getControl( 100 )
		self.ctrlDescriptionLabel.setLabel( self.DescriptionList[int((self.getFocusid() / 100) - 3)] )
		
		
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
		if controlId == 304 or controlId == 305:
			self.osdLanguageProperty.setPropString( self, self.ctrlOSDLanguagelist.getSelectedItem().getLabel() )
		# other setProperty setting here...

	def onFocus(self, controlId):
		# change description
		self.ctrlDescriptionLabel.setLabel( self.DescriptionList[int(controlId / 100 - 3)] )
