import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import SettingWindow, setWindowBusy
from pvr.gui.basewindow import Action
import pvr.elismgr
from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.guiconfig import *

class Configure( SettingWindow ):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs )
		self.commander = pvr.elismgr.getInstance( ).getCommander( )
 
		self.LeftGroupItems						= [ 'Language', 'Parental', 'Recording Option', 'Audio Setting', 'SCART Setting','HDMI Setting', 'IP Setting', 'Format HDD', 'Factory Reset', 'Etc' ]
		self.descriptionList					= [ 'DESC Language', 'DESC Parental', 'DESC Recording Option', 'DESC Audio Setting', 'DESC SCART Setting', 'DESC HDMI Setting', 'DESC IP Setting', 'DESC Format HDD', 'DESC Factory Reset', 'DESC Etc' ]
	
		self.ctrlLeftGroup = None
		self.groupItems = []
		self.initialized = False
		self.lastFocused = E_SUBMENU_LIST_ID
		self.prevListItemID = 0

		for i in range( len( self.LeftGroupItems ) ) :
			self.groupItems.append( xbmcgui.ListItem( self.LeftGroupItems[i], self.descriptionList[i], '-', '-', '-' ) )
			
	def onInit( self ):
		self.win = xbmcgui.Window( xbmcgui.getCurrentWindowId( ) )

		self.ctrlLeftGroup = self.getControl( E_SUBMENU_LIST_ID )
		self.ctrlLeftGroup.addItems( self.groupItems )

		self.initialized = True
		position = self.ctrlLeftGroup.getSelectedPosition( )
		self.ctrlLeftGroup.selectItem( position )
		self.setListControl( )

		#self.setHeaderLabel( 'Language Preference' )
		#self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK | FooterMask.G_FOOTER_ICON_SEARCH_MASK | FooterMask.G_FOOTER_ICON_OK_MASK | FooterMask.G_FOOTER_ICON_RECORD_MASK )


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
			if focusId == E_SUBMENU_LIST_ID and self.ctrlLeftGroup.getSelectedPosition() != self.prevListItemID :
				self.prevListItemID = self.ctrlLeftGroup.getSelectedPosition( )
				self.setListControl( )
			elif focusId != E_SUBMENU_LIST_ID:
				self.controlUp( )
	
		elif actionId == Action.ACTION_MOVE_DOWN :
			if focusId == E_SUBMENU_LIST_ID and self.ctrlLeftGroup.getSelectedPosition() != self.prevListItemID :
				self.prevListItemID = self.ctrlLeftGroup.getSelectedPosition( )
				self.setListControl( )
			elif focusId != E_SUBMENU_LIST_ID:
				self.controlDown( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			if focusId != E_SUBMENU_LIST_ID and ( ( focusId % 10 ) == 1 ) :
				self.setFocusId( E_SUBMENU_LIST_ID )
			else :
				self.controlLeft( )
				
		elif actionId == Action.ACTION_MOVE_RIGHT :
			if focusId == E_SUBMENU_LIST_ID :
				self.setFocusId( E_SETUPMENU_GROUP_ID )
			elif ( focusId != E_SUBMENU_LIST_ID ) and ( ( focusId % 10 ) == 2 ) :
				self.setFocusId( E_SUBMENU_LIST_ID )
			elif ( focusId != E_SUBMENU_LIST_ID ) and ( ( focusId % 10 ) == 1 ) :
				self.controlRight( )
			

	def onClick( self, controlId ):
		if( self.ctrlLeftGroup.getSelectedPosition() == E_LANGUAGE or self.ctrlLeftGroup.getSelectedPosition() == E_IP_SETTING ) :
			self.disableControl( self.ctrlLeftGroup.getSelectedPosition() )
		self.controlSelect( )

		
	def onFocus( self, controlId ):
		if self.initialized == False :
			return
		if ( self.lastFocused != controlId ) or ( self.ctrlLeftGroup.getSelectedPosition() != self.prevListItemID ):
			if controlId == E_SUBMENU_LIST_ID :
				self.setListControl( )
				if self.lastFocused != controlId :
					self.lastFocused = controlId
				if self.ctrlLeftGroup.getSelectedPosition() != self.prevListItemID:
					self.prevListItemID = self.ctrlLeftGroup.getSelectedPosition()
		

	def setListControl( self ):
		self.resetAllControl( )
		selectedId = self.ctrlLeftGroup.getSelectedPosition()
		self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( False )
		
		if selectedId == E_LANGUAGE :

			self.addEnumControl( E_SpinEx01, 'Language' )
			self.addEnumControl( E_SpinEx02, 'Audio Language' )
			self.addEnumControl( E_SpinEx03, 'Subtitle Language' )
			self.addEnumControl( E_SpinEx04, 'Secondary Subtitle Language' )
			self.addEnumControl( E_SpinEx05, 'Hearing Impaired' )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05 ]
			self.setVisibleControls( visibleControlIds, True )
			self.setEnableControls( visibleControlIds, True )

			hideControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04 ]
			self.setVisibleControls( hideControlIds, False )
			
			self.initControl( )
			self.disableControl( E_LANGUAGE )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return
			
			
		elif selectedId == E_PARENTAL :	
			self.addEnumControl( E_SpinEx01, 'Lock Mainmenu' )
			self.addInputControl( E_Input01, 'New PIN code', '****', 5)
			self.addInputControl( E_Input02, 'Confirmation PIN code', '****' , 5)
			self.addEnumControl( E_SpinEx02, 'Age Restricted' )
			

			visibleControlIds = [ E_SpinEx01, E_Input01, E_Input02, E_SpinEx02 ]
			self.setVisibleControls( visibleControlIds, True )
			self.setEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input03, E_Input04 ]
			self.setVisibleControls( hideControlIds, False )
			
			self.initControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return


		elif selectedId == E_RECORDING_OPTION :

			self.addEnumControl( E_SpinEx01, 'Automatic Timeshift' )
			self.addEnumControl( E_SpinEx02, 'Default Rec Duration' )
			self.addEnumControl( E_SpinEx03, 'Pre-Rec Time' )
			self.addEnumControl( E_SpinEx04, 'Post-Rec Time' )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
			self.setVisibleControls( visibleControlIds, True )
			self.setEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04 ]
			self.setVisibleControls( hideControlIds, False )
			
			self.initControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return

			
		elif selectedId == E_AUDIO_SETTING :
			self.addEnumControl( E_SpinEx01, 'Audio Dolby' )
			self.addEnumControl( E_SpinEx02, 'Audio HDMI' )
			self.addEnumControl( E_SpinEx03, 'Audio Delay' )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03 ]
			self.setEnableControls( visibleControlIds, True )
			self.setVisibleControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx04, E_SpinEx05,  E_Input01, E_Input02, E_Input03, E_Input04 ]
			self.setVisibleControls( hideControlIds, False )

			self.initControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return

	
		elif selectedId == E_SCART_SETTING :
			self.addEnumControl( E_SpinEx01, 'TV Aspect' )
			self.addEnumControl( E_SpinEx02, 'Picture 16:9' )
			self.addEnumControl( E_SpinEx03, 'Scart TV' )
			self.addEnumControl( E_SpinEx04, 'TV System' )	

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
			self.setVisibleControls( visibleControlIds, True )
			self.setEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx05,  E_Input01, E_Input02, E_Input03, E_Input04 ]
			self.setVisibleControls( hideControlIds, False )

			self.initControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return
			

		elif selectedId == E_HDMI_SETTING :
			self.addEnumControl( E_SpinEx01, 'CurrentVoutResolution' )
			self.addEnumControl( E_SpinEx02, 'Show 4:3' )
			self.addEnumControl( E_SpinEx03, 'HDMI Color Space' )
			self.addEnumControl( E_SpinEx04, 'TV System' )	
			
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
			self.setVisibleControls( visibleControlIds, True )
			self.setEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04 ]
			self.setVisibleControls( hideControlIds, False )

			self.initControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return

		
		elif selectedId == E_IP_SETTING :	
			self.addEnumControl( E_SpinEx01, 'DHCP' )
			self.addInputControl( E_Input01, 'IP Address', '192.168.101.160' , 3 )
			self.addInputControl( E_Input02, 'Subnet Mask', '255.255.252.0', 3 )
			self.addInputControl( E_Input03, 'Gateway', '192.168.100.1', 3 )
			self.addInputControl( E_Input04, 'DNS', '192.168.100.1', 3 )

			visibleControlIds = [ E_SpinEx01, E_Input01, E_Input02, E_Input03, E_Input04 ]
			self.setVisibleControls( visibleControlIds, True )
			self.setEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05 ]
			self.setVisibleControls( hideControlIds, False )
			
			self.initControl( )
			self.disableControl( E_IP_SETTING )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return
			

		elif selectedId == E_FORMAT_HDD :	
			self.addUserEnumControl( E_SpinEx01, 'Format Type', USER_ENUM_CONTROL_FORMAT_TYPE )
			self.addUserButtonControl( E_Input01, 'Start HDD Format' )
			
			visibleControlIds = [ E_SpinEx01, E_Input01 ]
			self.setVisibleControls( visibleControlIds, True )
			self.setEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input02, E_Input03, E_Input04 ]
			self.setVisibleControls( hideControlIds, False )
			
			self.initControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return
			

		elif selectedId == E_FACTORY_RESET :	
			self.addUserEnumControl( E_SpinEx01, 'Reset Channel List', USER_ENUM_CONTROL_YES_NO )
			self.addUserEnumControl( E_SpinEx02, 'Reset Favorite Add-ons', USER_ENUM_CONTROL_YES_NO )
			self.addUserEnumControl( E_SpinEx03, 'Reset Configure Setting', USER_ENUM_CONTROL_YES_NO )
			self.addUserButtonControl( E_Input01, 'Start Reset' )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_Input01 ]
			self.setVisibleControls( visibleControlIds, True )
			self.setEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx04 , E_SpinEx05, E_Input02, E_Input03, E_Input04 ]
			self.setVisibleControls( hideControlIds, False )

			self.initControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return
			

		elif selectedId == E_ETC :	
			self.addEnumControl( E_SpinEx01, 'Channel Banner Duration' )	#	Erase channel list yes/no
			self.addEnumControl( E_SpinEx02, 'Playback Banner Duration' )	#	Erase custom menu yes/no

			visibleControlIds = [ E_SpinEx01, E_SpinEx02 ]
			self.setVisibleControls( visibleControlIds, True )
			self.setEnableControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx03, E_SpinEx04, E_SpinEx05, E_Input01, E_Input02, E_Input03, E_Input04 ]
			self.setVisibleControls( hideControlIds, False )
			
			self.initControl( )
			self.getControl( E_SETUPMENU_GROUP_ID ).setVisible( True )
			return
			

		else :
			print 'ERROR : Can not find selected ID'

	def disableControl( self, selectedItem ):
		if( selectedItem == E_LANGUAGE ) :
			selectedIndex = self.getSelectedIndex( E_SpinEx03 )
			visibleControlIds = [ E_SpinEx04, E_SpinEx05 ]
			if ( selectedIndex == 0 ) :
				self.setEnableControls( visibleControlIds, False )
			else :
				self.setEnableControls( visibleControlIds, True )
		elif( selectedItem == E_IP_SETTING ) :
			selectedIndex = self.getSelectedIndex( E_SpinEx01 )
			visibleControlIds = [ E_Input01, E_Input02, E_Input03, E_Input04 ]
			if ( selectedIndex == 1 ) :
				self.setEnableControls( visibleControlIds, False )
			else :
				self.setEnableControls( visibleControlIds, True )
