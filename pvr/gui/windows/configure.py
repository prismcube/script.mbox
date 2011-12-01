import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import SettingWindow, setWindowBusy
from pvr.gui.basewindow import Action
import pvr.elismgr
from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.guiconfig import FooterMask

E_SpinEx01			= 1100
E_SpinEx02			= 1200
E_SpinEx03			= 1300
E_SpinEx04			= 1400
E_SpinEx05			= 1500

E_LANGUAGE			= 0
E_PARENTAL			= 1
E_RECORDING_OPTION	= 2
E_AUDIO_SETTING		= 3
E_SCART_SETTING		= 4
E_HDMI_SETTING		= 5
E_IP_SETTING		= 6
E_FORMAT_HDD		= 7
E_FACTORY_RESET		= 8
E_ETC				= 9

class Configure(SettingWindow):
	def __init__( self, *args, **kwargs ):
		SettingWindow.__init__( self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance().getCommander( )
 
		self.LeftGroupItems						= ['Language', 'Parental', 'Recording Option', 'Audio Setting', 'SCART Setting','HDMI Setting', 'IP Setting', 'Format HDD', 'Factory Reset', 'Etc' ]
		self.descriptionList					= ['DESC Language', 'DESC Parental', 'DESC Recording Option', 'DESC Audio Setting', 'DESC SCART Setting', 'DESC HDMI Setting', 'DESC IP Setting', 'DESC Format HDD', 'DESC Factory Reset', 'DESC Etc' ]
	
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

		self.initLang()

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

		
		if selectedId == E_LANGUAGE :

			self.addEnumControl( E_SpinEx01, 'Language' )
			self.addEnumControl( E_SpinEx02, 'Audio Language' )
			self.addEnumControl( E_SpinEx03, 'Subtitle Language' )
			self.addEnumControl( E_SpinEx04, 'Secondary Subtitle Language' )
			self.addEnumControl( E_SpinEx05, 'Hearing Impaired' )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05 ]
			self.setVisibleControls( visibleControlIds, True )


			selectedIndex = self.getSelectedIndex( E_SpinEx03 )
			if ( selectedIndex == 0 ) and ( self.ctrlLeftGroup.getSelectedPosition( ) == 0 ):
				disableControlIds = [E_SpinEx04, E_SpinEx05]
				self.setEnableControls( disableControlIds, False )
			else:
				self.setEnableControls( visibleControlIds, True )			

			self.initControl( )

		elif selectedId == E_PARENTAL :	
			self.addEnumControl( E_SpinEx01, 'Lock Mainmenu' )
			self.addEnumControl( E_SpinEx02, 'Age Restricted' )	#PINCODE CONTROL
			self.addEnumControl( E_SpinEx03, 'Age Restricted' )	#PINCODE CONTROL			
			self.addEnumControl( E_SpinEx04, 'Age Restricted' )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]

			self.setEnableControls( visibleControlIds, True )
			self.initControl( )

		elif selectedId == E_RECORDING_OPTION :

			self.addEnumControl( E_SpinEx01, 'Automatic Timeshift' )
			self.addEnumControl( E_SpinEx02, 'Default Rec Duration' )
			self.addEnumControl( E_SpinEx03, 'Pre-Rec Time' )
			self.addEnumControl( E_SpinEx04, 'Post-Rec Time' )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
			self.setVisibleControls( visibleControlIds, True )

			hideControlIds = [ E_SpinEx05 ]
			self.setVisibleControls( hideControlIds, False )

			self.setEnableControls( visibleControlIds, True )
			self.initControl( )
			
		elif selectedId == E_AUDIO_SETTING :
			self.addEnumControl( E_SpinEx01, 'Audio Dolby' )
			self.addEnumControl( E_SpinEx02, 'Audio HDMI' )
			self.addEnumControl( E_SpinEx03, 'Audio Delay' )

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03 ]
			self.setVisibleControls( visibleControlIds, True )

			self.setEnableControls( visibleControlIds, True )
			self.initControl( )

	
		elif selectedId == E_SCART_SETTING :
			self.addEnumControl( E_SpinEx01, 'TV Aspect' )
			self.addEnumControl( E_SpinEx02, 'Picture 16:9' )
			self.addEnumControl( E_SpinEx03, 'Scart TV' )
			self.addEnumControl( E_SpinEx04, 'TV System' )	

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
			self.setVisibleControls( visibleControlIds, True )

			self.setEnableControls( visibleControlIds, True )
			self.initControl( )
			

		elif selectedId == E_HDMI_SETTING :
			self.addEnumControl( E_SpinEx01, 'CurrentVoutResolution' )
			self.addEnumControl( E_SpinEx02, 'Show 4:3' )
			self.addEnumControl( E_SpinEx03, 'HDMI Color Space' )
			self.addEnumControl( E_SpinEx04, 'TV System' )	
			
			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
			self.setVisibleControls( visibleControlIds, True )

			self.setEnableControls( visibleControlIds, True )
			self.initControl( )

		
		elif selectedId == E_IP_SETTING :	
			self.addEnumControl( E_SpinEx01, 'DHCP' )
			self.addEnumControl( E_SpinEx02, 'CurrentVoutResolution' ) 	#INPUT_CONTROL
			self.addEnumControl( E_SpinEx03, 'CurrentVoutResolution' ) 	#INPUT_CONTROL	
			self.addEnumControl( E_SpinEx04, 'CurrentVoutResolution' ) 	#INPUT_CONTROL
			self.addEnumControl( E_SpinEx05, 'CurrentVoutResolution' )	#INPUT_CONTROL

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04, E_SpinEx05 ]
			self.setVisibleControls( visibleControlIds, True )

			self.setEnableControls( visibleControlIds, True )
			self.initControl( )

		elif selectedId == E_FORMAT_HDD :	
			self.addEnumControl( E_SpinEx01, 'CurrentVoutResolution' ) # BUTTON
			
			visibleControlIds = [ E_SpinEx01 ]
			self.setVisibleControls( visibleControlIds, True )

			self.setEnableControls( visibleControlIds, True )
			self.initControl( )

		elif selectedId == E_FACTORY_RESET :	
			self.addEnumControl( E_SpinEx01, 'CurrentVoutResolution' )	#	Erase channel list yes/no
			self.addEnumControl( E_SpinEx02, 'CurrentVoutResolution' )	#	Erase custom menu yes/no
			self.addEnumControl( E_SpinEx03, 'CurrentVoutResolution' )	#	Erase property yes/no
			self.addEnumControl( E_SpinEx04, 'CurrentVoutResolution' )	#    BUTTON		

			visibleControlIds = [ E_SpinEx01, E_SpinEx02, E_SpinEx03, E_SpinEx04 ]
			self.setVisibleControls( visibleControlIds, True )

			self.setEnableControls( visibleControlIds, True )
			self.initControl( )

		elif selectedId == E_ETC :	
			self.addEnumControl( E_SpinEx01, 'Channel Banner Duration' )	#	Erase channel list yes/no
			self.addEnumControl( E_SpinEx02, 'Playback Banner Duration' )	#	Erase custom menu yes/no

			visibleControlIds = [ E_SpinEx01, E_SpinEx02 ]
			self.setVisibleControls( visibleControlIds, True )

			self.setEnableControls( visibleControlIds, True )
			self.initControl( )

		else :
			print 'ERROR : Can not find selected ID'

	def initLang():
		import pvr.msg as m
		self.ctrlLbl = getControl( 9001 )
		self.ctrlBtn = getControl( 9002 )

		self.ctrlLbl.setLabel( m.strings(m.LANGUAGE) )

		ret = xbmc.getLanguage()
		self.ctrlBtn.setLabel(ret)
		print 'TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT'