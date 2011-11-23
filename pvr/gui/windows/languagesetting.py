
import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import SettingWindow, setWindowBusy
from pvr.gui.basewindow import Action
import pvr.elismgr
from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt


E_OSDLanguage					= 1100
E_PrimaryAudioLanguage			= 1200
E_PrimarySubtitleLanguage		= 1300
E_SecondarySubtitleLanguage		= 1400
E_ForTheHearingImpaired			= 1500

E_LEFTBUTTON_OFFSET				= 1
E_RIGHTBUTTON_OFFSET			= 2
E_SPINCONTROL_OFFSET			= 3

class LanguageSetting(SettingWindow):
	def __init__(self, *args, **kwargs):
		SettingWindow.__init__(self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance().getCommander()

		# Description List
		self.navigationIds 						= [E_OSDLanguage,E_PrimaryAudioLanguage,E_PrimarySubtitleLanguage,E_SecondarySubtitleLanguage,E_ForTheHearingImpaired]
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

		#TEST
		self.setProperty('WindowType', 'ChannalList')

	def onInit(self):
		#if not self.win:
		self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())

		# Header Title
		self.ctrlHeaderTitle				= self.getControl( 3001 )
		self.ctrlHeaderTitle.setLabel('Language Preference')

		# OSD Language
		self.ctrlOSDLanguage				= self.getControl( E_OSDLanguage + E_SPINCONTROL_OFFSET )
		self.ctrlOSDLanguage.addItems( self.osdlangugelist )
		self.ctrlOSDLanguage.selectItem( self.osdLanguageProperty.getPropIndex() )

		# Primary Audio Language
		self.ctrlPrimaryAudioLanguage		= self.getControl( E_PrimaryAudioLanguage + E_SPINCONTROL_OFFSET )
		self.ctrlPrimaryAudioLanguage.addItems( self.primaryAudioLanguagelist )
		self.ctrlPrimaryAudioLanguage.selectItem( self.primaryAudioLanguageProperty.getPropIndex() )

		# Primary Subtitle Language
		self.ctrlPrimarySubtitleLanguage	= self.getControl( E_PrimarySubtitleLanguage + E_SPINCONTROL_OFFSET )
		self.ctrlPrimarySubtitleLanguage.addItems( self.primarySubtitleLanguagelist )
		self.ctrlPrimarySubtitleLanguage.selectItem( self.primarySubtitleLanguageProperty.getPropIndex() )

		# Secondary Subtitle Language
		self.ctrlSecondarySubtitleLanguage	= self.getControl( E_SecondarySubtitleLanguage + E_SPINCONTROL_OFFSET )
		self.ctrlSecondarySubtitleLanguage.addItems( self.secondarySubtitleLanguagelist )
		self.ctrlSecondarySubtitleLanguage.selectItem( self.secondarySubtitleLanguageProperty.getPropIndex() )

		# For The Hearing Impaired
		self.ctrlForTheHearingImpaired		= self.getControl( E_ForTheHearingImpaired + E_SPINCONTROL_OFFSET )
		self.ctrlForTheHearingImpaired.addItems( self.forTheHearingImpairedlist )
		self.ctrlForTheHearingImpaired.selectItem( self.forTheHearingImpairedProperty.getPropIndex() )


	def onAction(self, action):
 		
		id = action.getId()
		focusId = self.win.getFocusId( )		
		print 'LanguagSetting OnAction controlId=%d' %id
		
		if id == Action.ACTION_PREVIOUS_MENU:
			print 'dhkim LanguageSetting check action previous'
		elif id == Action.ACTION_SELECT_ITEM:
			if focusId == E_OSDLanguage + E_LEFTBUTTON_OFFSET or focusId == E_OSDLanguage + E_RIGHTBUTTON_OFFSET :
				self.setPropertyEnum( self.osdLanguageProperty, self.ctrlOSDLanguage.getSelectedPosition() )
			elif focusId == E_PrimaryAudioLanguage + E_LEFTBUTTON_OFFSET or focusId == E_PrimaryAudioLanguage + E_RIGHTBUTTON_OFFSET :
				self.setPropertyEnum( self.primaryAudioLanguageProperty, self.ctrlPrimaryAudioLanguage.getSelectedPosition() )
			elif focusId == E_PrimarySubtitleLanguage + E_LEFTBUTTON_OFFSET or focusId == E_PrimarySubtitleLanguage + E_RIGHTBUTTON_OFFSET :
				self.setPropertyEnum( self.primarySubtitleLanguageProperty, self.ctrlPrimarySubtitleLanguage.getSelectedPosition() )
			elif focusId == E_SecondarySubtitleLanguage + E_LEFTBUTTON_OFFSET or focusId == E_SecondarySubtitleLanguage + E_RIGHTBUTTON_OFFSET :
				self.setPropertyEnum( self.secondarySubtitleLanguageProperty, self.ctrlSecondarySubtitleLanguage.getSelectedPosition() )
			elif focusId == E_ForTheHearingImpaired + E_LEFTBUTTON_OFFSET or focusId == E_ForTheHearingImpaired + E_RIGHTBUTTON_OFFSET :
				self.setPropertyEnum( self.forTheHearingImpairedProperty, self.ctrlForTheHearingImpaired.getSelectedPosition() )


		elif id == Action.ACTION_PARENT_DIR:
			winmgr.getInstance().showWindow( winmgr.WIN_ID_MAINMENU )
			print 'dhkim LanguageSetting check action parent'

		elif id == Action.ACTION_MOVE_UP:
			print 'LanguagSetting ACTION_MOVE_UP OnAction getFocusId()=%d' %focusId
			navId = int(focusId/100)*100
			self.controlUp( self.navigationIds, navId )


		elif id == Action.ACTION_MOVE_DOWN:
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

