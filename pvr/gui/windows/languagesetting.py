
import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import SettingWindow, setWindowBusy
from pvr.gui.basewindow import Action
import pvr.elismgr
from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt


class LanguageSetting(SettingWindow):
	def __init__(self, *args, **kwargs):
		SettingWindow.__init__(self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance().getCommander()

		# Description List
		self.navigationIds 						= [1100,1200,1300,1400,1500]
		self.descriptionList					= ['Set menu and popup language', 'Set primary audio language', 'Set primary subtitle language', 'Set secondary subtitle language', 'Enable hearing impaired support']

		# OSD Language
		self.osdlangugelist 					= []
		self.osdLanguageProperty				= ElisPropertyEnum( 'Language' )
		self.creatPropertyEnum( self.osdlangugelist, self.osdLanguageProperty )

		# Primary Audio Language
		self.primaryAudioLanguagelist 			= []
		self.primaryAudioLanguageProperty		= ElisPropertyEnum( 'Audio Language' )
		self.creatPropertyEnum( self.primaryAudioLanguagelist, self.primaryAudioLanguageProperty )		

		# Primary Subtitle Language
		self.primarySubtitleLanguagelist 		= []
		self.primarySubtitleLanguageProperty	= ElisPropertyEnum( 'Subtitle Language' )
		self.creatPropertyEnum( self.primarySubtitleLanguagelist, self.primarySubtitleLanguageProperty )				

		# Secondary Subtitle Language
		self.secondarySubtitleLanguagelist 		= []
		self.secondarySubtitleLanguageProperty	= ElisPropertyEnum( 'Secondary Subtitle Language' )
		self.creatPropertyEnum( self.secondarySubtitleLanguagelist, self.secondarySubtitleLanguageProperty )						

		# For The Hearing Impaired
		self.forTheHearingImpairedlist		 	= []
		self.forTheHearingImpairedProperty		= ElisPropertyEnum( 'Hearing Impaired' )
		self.creatPropertyEnum( self.forTheHearingImpairedlist, self.forTheHearingImpairedProperty )
		

	def onInit(self):
		#if not self.win:
		self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())

		# OSD Language
		self.ctrlOSDLanguage				= self.getControl( 1103 )
		self.ctrlOSDLanguage.addItems( self.osdlangugelist )
		self.ctrlOSDLanguage.selectItem( self.osdLanguageProperty.getProp() )

		# Primary Audio Language
		self.ctrlPrimaryAudioLanguage		= self.getControl( 1203 )
		self.ctrlPrimaryAudioLanguage.addItems( self.primaryAudioLanguagelist )
		self.ctrlPrimaryAudioLanguage.selectItem( self.primaryAudioLanguageProperty.getProp() )

		self.ctrlPrimaryAudioLanguage.setEnabled( False )

		# Primary Subtitle Language
		self.ctrlPrimarySubtitleLanguage	= self.getControl( 1303 )
		self.ctrlPrimarySubtitleLanguage.addItems( self.primarySubtitleLanguagelist )
		self.ctrlPrimarySubtitleLanguage.selectItem( self.primarySubtitleLanguageProperty.getProp() )

		# Secondary Subtitle Language
		self.ctrlSecondarySubtitleLanguage	= self.getControl( 1403 )
		self.ctrlSecondarySubtitleLanguage.addItems( self.secondarySubtitleLanguagelist )
		self.ctrlSecondarySubtitleLanguage.selectItem( self.secondarySubtitleLanguageProperty.getProp() )

		# For The Hearing Impaired
		self.ctrlForTheHearingImpaired		= self.getControl( 1503 )
		self.ctrlForTheHearingImpaired.addItems( self.forTheHearingImpairedlist )
		self.ctrlForTheHearingImpaired.selectItem( self.forTheHearingImpairedProperty.getProp() )


	def onAction(self, action):
 		
		id = action.getId()
		print 'LanguagSetting OnAction controlId=%d' %id
		
		if id == Action.ACTION_PREVIOUS_MENU:
			print 'dhkim LanguageSetting check action previous'
		elif id == Action.ACTION_SELECT_ITEM:
			print 'dhkim LanguageSetting check action select'
		elif id == Action.ACTION_PARENT_DIR:
			winmgr.getInstance().showWindow( winmgr.WIN_ID_MAINMENU )
			print 'dhkim LanguageSetting check action parent'

		elif id == Action.ACTION_MOVE_UP:
			focusId = self.win.getFocusId( )
			print 'LanguagSetting ACTION_MOVE_UP OnAction getFocusId()=%d' %focusId
			navId = int(focusId/100)*100
			self.controlUp( self.navigationIds, navId )


		elif id == Action.ACTION_MOVE_DOWN:
			focusId = self.win.getFocusId( )
			print 'LanguagSetting ACTION_MOVE_DOWN OnAction getFocusId()=%d' %focusId

			navId = int(focusId/100)*100

			self.controlDown( self.navigationIds, navId )


	def onClick(self, controlId):
		print 'dhkim test in onClick event controlId=%d' %controlId
		"""
		if (controlId == 504) or (controlId == 505):
			if self.primarySubtitleLanguageProperty.getProp() == 0:
				self.ctrlGroupSecondarySubtitleLanguage.setEnabled(False)
				self.ctrlGroupForTheHearingImpaired.setEnabled(False)
			else:
				self.ctrlGroupSecondarySubtitleLanguage.setEnabled(True)
				self.ctrlGroupForTheHearingImpaired.setEnabled(True)
		"""				

		"""	
		# setProperty setting here...
		if controlId == 1101 or controlId == 1102:
			self.osdLanguageProperty.setPropString( self, self.ctrlOSDLanguage.getSelectedItem().getLabel() )
		if controlId == 1201 or controlId == 1202:
			self.primaryAudioLanguageProperty.setPropString( self, self.ctrlPrimaryAudioLanguage.getSelectedItem().getLabel() )

		if controlId == 504 or controlId == 505:
			self.primarySubtitleLanguageProperty.setPropString( self, self.ctrlPrimarySubtitleLanguage.getSelectedItem().getLabel() )
		if controlId == 604 or controlId == 605:
			self.secondarySubtitleLanguageProperty.setPropString( self, self.ctrlSecondarySubtitleLanguage.getSelectedItem().getLabel() )
		if controlId == 704 or controlId == 705:
			self.forTheHearingImpairedProperty.setPropString( self, self.ctrlForTheHearingImpaired.getSelectedItem().getLabel() )
		"""
		
	def onFocus(self, controlId):
		print 'dhkim test in Focus event id=%d' %controlId
		# change description
		#self.ctrlDescriptionLabel.setLabel( self.descriptionList[controlId / 100 - 3] )

