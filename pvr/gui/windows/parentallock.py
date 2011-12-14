
import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import SettingWindow, setWindowBusy
from pvr.gui.basewindow import Action
import pvr.elismgr
from elisproperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.guiconfig import FooterMask

E_SpinEx01			= 1100
E_SpinEx02			= 1200
E_SpinEx03			= 1300
E_SpinEx04			= 1400
E_SpinEx05			= 1500


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
			self.groupItems.append( xbmcgui.ListItem( self.LeftGroupItems[i], self.descriptionList[i], '-', '-', '-' ) )
			
	def onInit(self):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.ctrlLeftGroup = self.getControl( 9000 )
		self.ctrlLeftGroup.addItems( self.groupItems )

		self.initialized = True
		position = self.ctrlLeftGroup.getSelectedPosition()
		self.ctrlLeftGroup.selectItem( position )
		self.setListControl( )


	def onAction( self, action ):

		actionId = action.getId( )
		focusId = self.getFocusId( )

		if actionId == Action.ACTION_PREVIOUS_MENU :
			print 'LanguageSetting check action previous'
		elif actionId == Action.ACTION_SELECT_ITEM :
			print 'dhkim test Action select item event'
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.initialized = False
			self.close( )

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
			elif ( focusId != 9000 ) and ( ( focusId % 10 ) == 1 ) :
				self.controlRight( )


	def onClick( self, controlId ):
		self.controlSelect( )

		
	def onFocus( self, controlId ):
		if self.initialized == False :
			return

		if ( self.lastFocused != controlId ) or (self.ctrlLeftGroup.getSelectedPosition() != self.prevListItemID):
			if controlId == 9000 :
				self.setListControl( )
			self.lastFocused = controlId
			self.prevListItemID = self.ctrlLeftGroup.getSelectedPosition()
		

	def setListControl( self ):
		self.resetAllControl( )
		ctrlLeftGroup = self.getControl( 9000 )
		selectedId = ctrlLeftGroup.getSelectedPosition()
		
		if selectedId == 0 :

			self.addEnumControl( E_SpinEx01, 'Language', None )
			self.addEnumControl( E_SpinEx02, 'Audio Language', None )
			self.addEnumControl( E_SpinEx03, 'Subtitle Language', None )
			self.addEnumControl( E_SpinEx04, 'Secondary Subtitle Language', None )
			self.addEnumControl( E_SpinEx05, 'Hearing Impaired', None )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05 ]
			self.setVisibleControls( visibleControlIds, True )


			selectedIndex = self.getSelectedIndex( E_SpinEx03 )
			if ( selectedIndex == 0 ) and ( self.ctrlLeftGroup.getSelectedPosition( ) == 0 ):
				disableControlIds = [E_SpinEx04, E_SpinEx05]
				self.setEnableControls( disableControlIds, False )
			else:
				self.setEnableControls( visibleControlIds, True )			

			self.initControl( )

		elif selectedId == 1 :		

			self.addEnumControl( E_SpinEx01, 'Automatic Timeshift', None )
			self.addEnumControl( E_SpinEx02, 'Default Rec Duration', None )
			self.addEnumControl( E_SpinEx03, 'Pre-Rec Time', None )
			self.addEnumControl( E_SpinEx04, 'Post-Rec Time', None )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
			self.setVisibleControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx05 ]
			self.setVisibleControls( hideControlIds, False )

			self.setEnableControls( visibleControlIds, True )
			self.initControl( )
		
