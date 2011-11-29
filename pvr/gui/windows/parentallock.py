
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
		self.commander = pvr.elismgr.getInstance().getCommander( )
 
		self.LeftGroupItems						= ['Language', 'Parental']
		self.descriptionList					= ['Set menu and popup language', 'Set primary audio language', 'Set primary subtitle language', 'Set secondary subtitle language', 'Enable hearing impaired support']
	
		self.ctrlLeftGroup = 0
		self.groupItems = []
		self.initialized = False
		self.lastFocused = -1
		self.prevListItemID = -1

		for i in range( len( self.LeftGroupItems ) ) :
			self.groupItems.append( xbmcgui.ListItem( self.LeftGroupItems[i], '%s' % i, '-', '-', '-' ) )
			
	def onInit(self):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.ctrlLeftGroup = self.getControl( 9000 )
		self.ctrlLeftGroup.addItems( self.groupItems )

		self.setHeaderLabel( self.win, 'Language Preference' )
		self.setFooter( self.win, ( FooterMask.G_FOOTER_ICON_BACK_MASK | FooterMask.G_FOOTER_ICON_SEARCH_MASK | FooterMask.G_FOOTER_ICON_OK_MASK | FooterMask.G_FOOTER_ICON_RECORD_MASK ) )
		self.initialized = True
		self.ctrlLeftGroup.selectItem( 0 )
		self.setListControl( )


	def onAction( self, action ):

		actionId = action.getId( )
		focusId = self.getFocusId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			print 'LanguageSetting check action previous'
		elif actionId == Action.ACTION_SELECT_ITEM :
			print 'dhkim test Action select item event'
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.close( )
			winmgr.getInstance().showWindow( winmgr.WIN_ID_MAINMENU )

		elif actionId == Action.ACTION_MOVE_UP :
			if focusId == 9000 :
				self.setListControl( )
			else :
				self.controlUp( )
	
		elif actionId == Action.ACTION_MOVE_DOWN :
			if focusId == 9000 :
				self.setListControl( )
			else :
				self.controlDown( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			if ( focusId != 9000 ) and ( ( focusId % 10 ) == 1 ) :
				self.setFocusId( 9000 )
			else :
				self.controlLeft( )
				
		elif actionId == Action.ACTION_MOVE_RIGHT :
			if focusId == 9000 :
				self.setFocusId( 9010 )
			elif ( focusId != 9000 ) and ( ( focusId % 10 ) == 2 ) :
				self.setFocusId( 9000 )
			else :
				self.controlRight( )

	def onClick( self, controlId ):
		self.controlSelect( )

		
	def onFocus( self, controlId ):
		if self.initialized == False :
			return

		if not( self.lastFocused == controlId ) or not(self.ctrlLeftGroup.getSelectedPosition() == self.prevListItemID):
			if controlId == 9000 :
				self.setListControl( )
			self.lastFocused = controlId
			self.prevListItemID = self.ctrlLeftGroup.getSelectedPosition()
		'''
		selectedIndex = self.getSelectedIndex( E_PrimarySubtitleLanguage )
		if ( selectedIndex == 0 ) and ( self.ctrlLeftGroup.getSelectedPosition( ) == 0 ):
			self.setEnableControl( E_SecondarySubtitleLanguage, False )
			self.setEnableControl( E_ForTheHearingImpaired, False )
		else:
			self.setEnableControl( E_SecondarySubtitleLanguage, True )
			self.setEnableControl( E_ForTheHearingImpaired, True )
		'''

	def setListControl( self ):
		self.removeAllControl( )
		ctrlLeftGroup = self.getControl( 9000 )
		selectedId = ctrlLeftGroup.getSelectedPosition()
		print 'dhkim test getSelectedPosition( ) #2 = %s' % selectedId
		
		if selectedId == 0 :
			self.addEnumControl( E_OSDLanguage, 'Language' )
			self.addEnumControl( E_PrimaryAudioLanguage, 'Audio Language' )
			self.addEnumControl( E_PrimarySubtitleLanguage, 'Subtitle Language' )
			self.addEnumControl( E_SecondarySubtitleLanguage, 'Secondary Subtitle Language' )
			self.addEnumControl( E_ForTheHearingImpaired, 'Hearing Impaired' )
			self.initControl( )
		elif selectedId == 1 :		
			self.addEnumControl( E_AutomaticTimeshift, 'Automatic Timeshift' )
			self.addEnumControl( E_DefaultRecordDuration, 'Default Rec Duration' )
			self.addEnumControl( E_PreRecordingTime, 'Pre-Rec Time' )
			self.addEnumControl( E_PostRecordingTime, 'Post-Rec Time' )
			self.initControl( )
		
