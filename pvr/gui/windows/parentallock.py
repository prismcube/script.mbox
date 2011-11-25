
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

E_AutomaticTimeshift			= 1100
E_DefaultRecordDuration			= 1200
E_PreRecordingTime				= 1300
E_PostRecordingTime				= 1400

class ParentalLock(SettingWindow):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance( ).getCommander( )

		self.LeftGroupItems						= ['Language', 'Parental']
		self.navigationIds 						= [E_OSDLanguage,E_PrimaryAudioLanguage,E_PrimarySubtitleLanguage,E_SecondarySubtitleLanguage,E_ForTheHearingImpaired]
		self.descriptionList					= ['Set menu and popup language', 'Set primary audio language', 'Set primary subtitle language', 'Set secondary subtitle language', 'Enable hearing impaired support']
	
		self.ctrlLeftGroup = 0
		self.groupItems = []		
		
	def onInit(self):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.ctrlLeftGroup = self.getControl( 9000 )

		for i in range( len( self.LeftGroupItems ) ):
			self.groupItems.append( xbmcgui.ListItem( self.LeftGroupItems[i], '-', '-', '-', '-' ) )	
		
		self.ctrlLeftGroup.addItems( self.groupItems )

		self.setHeaderLabel( self.win, 'Language Preference' )
		self.setFooter( self.win, ( FooterMask.G_FOOTER_ICON_BACK_MASK | FooterMask.G_FOOTER_ICON_SEARCH_MASK | FooterMask.G_FOOTER_ICON_OK_MASK | FooterMask.G_FOOTER_ICON_RECORD_MASK ) )

		self.setListControl( )
		
	def onAction( self, action ):

		actionId = action.getId( )
		focusId = self.getFocusId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			print 'LanguageSetting check action previous'
		elif actionId == Action.ACTION_SELECT_ITEM :
			self.controlSelect( )
				
		elif actionId == Action.ACTION_PARENT_DIR :
			winmgr.getInstance().showWindow( winmgr.WIN_ID_MAINMENU )

		elif actionId == Action.ACTION_MOVE_UP :
			if not( self.getFocusId( ) == 9000 ) :
				self.controlUp( )

		elif actionId == Action.ACTION_MOVE_DOWN :
			if not( self.getFocusId( ) == 9000 ) :
				self.controlDown( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.setFocus( self.ctrlLeftGroup )


	def onClick( self, controlId ):
		self.controlSelect( )
		
		
	def onFocus( self, controlId ):
		if self.getFocusId( ) == 9000 :
			self.setListControl( )
		#self.controlDescription( self.win, controlId )
		print 'LanguageSetting test in Focus event id=%d' %controlId

	def setListControl( self ):
		self.removeAllControl( )
		print 'dhkim test contro numm % d' % self.ctrlLeftGroup.getSelectedPosition( )
		
		if self.ctrlLeftGroup.getSelectedPosition( ) == 1 :
			self.addEnumControl( E_OSDLanguage, 'Language' )
			self.addEnumControl( E_PrimaryAudioLanguage, 'Audio Language' )
			self.addEnumControl( E_PrimarySubtitleLanguage, 'Subtitle Language' )
			self.addEnumControl( E_SecondarySubtitleLanguage, 'Secondary Subtitle Language' )
			self.addEnumControl( E_ForTheHearingImpaired, 'Hearing Impaired' )			
		elif self.ctrlLeftGroup.getSelectedPosition( ) == 2 :
			self.addEnumControl( E_AutomaticTimeshift, 'Automatic Timeshift' )
			self.addEnumControl( E_DefaultRecordDuration, 'Default Rec Duration' )
			self.addEnumControl( E_PreRecordingTime, 'Pre-Rec Time' )
			self.addEnumControl( E_PostRecordingTime, 'Post-Rec Time' )

		self.initControl( )

		
