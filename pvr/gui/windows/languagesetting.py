
import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import SettingWindow, setWindowBusy
from pvr.gui.basewindow import Action
import pvr.elismgr
from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.guiconfig import FooterMask


E_OSDLanguage					= 1100
E_PrimaryAudioLanguage			= 1200
E_PrimarySubtitleLanguage		= 1300
E_SecondarySubtitleLanguage		= 1400
E_ForTheHearingImpaired			= 1500


class LanguageSetting(SettingWindow):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance().getCommander( )

		# Description List
		self.navigationIds 						= [E_OSDLanguage,E_PrimaryAudioLanguage,E_PrimarySubtitleLanguage,E_SecondarySubtitleLanguage,E_ForTheHearingImpaired]
		self.descriptionList					= ['Set menu and popup language', 'Set primary audio language', 'Set primary subtitle language', 'Set secondary subtitle language', 'Enable hearing impaired support']
		
		self.addEnumControl( E_OSDLanguage, 'Language' )
		self.addEnumControl( E_PrimaryAudioLanguage, 'Audio Language' )
		self.addEnumControl( E_PrimarySubtitleLanguage, 'Subtitle Language' )
		self.addEnumControl( E_SecondarySubtitleLanguage, 'Secondary Subtitle Language' )
		self.addEnumControl( E_ForTheHearingImpaired, 'Hearing Impaired' )		
		

	def onInit(self):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.setHeaderLabel( 'Language Preference' )
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK | FooterMask.G_FOOTER_ICON_SEARCH_MASK | FooterMask.G_FOOTER_ICON_OK_MASK | FooterMask.G_FOOTER_ICON_RECORD_MASK )
		
		self.initControl()
		selectedIndex = self.getSelectedIndex( E_PrimarySubtitleLanguage )
		print 'primarySubtitleLanguage selectedIndex=%d' % selectedIndex

		if selectedIndex == 0 :
			print 'primarySubtitleLanguage is disabled'		
			self.setEnableControl( E_SecondarySubtitleLanguage, False )
			self.setEnableControl( E_ForTheHearingImpaired, False )
		else:
			self.setEnableControl( E_SecondarySubtitleLanguage, True )
			self.setEnableControl( E_ForTheHearingImpaired, True )

	def onAction( self, action ):

		actionId = action.getId( )
		focusId = self.getFocusId( )

		if actionId == Action.ACTION_PREVIOUS_MENU:
			print 'LanguageSetting check action previous'
		elif actionId == Action.ACTION_SELECT_ITEM:

			self.controlSelect( )
			groupId = self.getGroupId( focusId )

			if groupId == E_PrimarySubtitleLanguage :

				selectedIndex = self.getSelectedIndex( E_PrimarySubtitleLanguage )

				if selectedIndex == 0 :
					self.setEnableControl( E_SecondarySubtitleLanguage, False )
					self.setEnableControl( E_ForTheHearingImpaired, False )

				else :
					self.setEnableControl( E_SecondarySubtitleLanguage, True )
					self.setEnableControl( E_ForTheHearingImpaired, True )
				
		elif actionId == Action.ACTION_PARENT_DIR:
			self.close( )

		elif actionId == Action.ACTION_MOVE_UP:
			self.controlUp( )

		elif actionId == Action.ACTION_MOVE_DOWN:
			self.controlDown( )


	def onClick( self, controlId ):

		self.controlSelect( )

		focusId = self.getFocusId( )		
		groupId = self.getGroupId( focusId )
		
		if groupId == E_PrimarySubtitleLanguage :
		
			selectedIndex = self.getSelectedIndex( E_PrimarySubtitleLanguage )
			
			if selectedIndex == 0 :
				self.setEnableControl( E_SecondarySubtitleLanguage, False )
				self.setEnableControl( E_ForTheHearingImpaired, False )

			else :
				self.setEnableControl( E_SecondarySubtitleLanguage, True )
				self.setEnableControl( E_ForTheHearingImpaired, True )

		
	def onFocus( self, controlId ):
		#self.controlDescription( self.win, controlId )
		print 'LanguageSetting test in Focus event id=%d' %controlId

