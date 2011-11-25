
import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import BaseWindow, setWindowBusy
from pvr.gui.basewindow import Action
import pvr.elismgr
from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt


class ParentalLock(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance().getCommander()

	def onInit(self):
		if not self.win:
			self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
		"""
		print 'lael98 test parentlock 0'
		self.ctrlOSDLanguage 				= self.getId( 101 )
		print 'lael98 test parentlock 1'
		self.ctrlPrimaryAudioLanguage    	= self.getControl( 102 )
		print 'lael98 test parentlock 1'		
		self.ctrlPrimarySubtitleLanguage    = self.getControl( 103 )
		self.ctrlSecondarySubtitleLanguage  = self.getControl( 104 )
		self.ctrlHearingImpaired 			= self.getControl( 105 )
		print 'lael98 test parentlock 2'		

		print 'lael98 test parentlock 3'
		self.ctrlOSDLanguage.SetText("test")
		print 'lael98 test parentlock 4'		
		"""
		# OSDLanguage

		"""
		osdLangProp = ElisPropertyEnum( 'Language' )
		value = osdLangProp.getProp()
		
		count = osdLangProp.getIndexCount()
		for i range( count )
			strName = osdLangProp.getName() + osdLangProp.getPropString( i )
			osdLangProp.addLabel( strName, osdLangProp.getPropByIndex( i ) )
			if osdLangProp.getPropByIndex( i ) == value
				osdLangProp.setValue( value )
		"""	

	def onAction(self, action):
 		
		id = action.getId()
		
		if id == Action.ACTION_PREVIOUS_MENU:
			print 'dhkim MenuReceiverSetupNetwork check action previous'
		elif id == Action.ACTION_SELECT_ITEM:
			print 'dhkim MenuReceiverSetupNetwork check action select'
		elif id == Action.ACTION_PARENT_DIR:
			self.close( )
			winmgr.getInstance().showWindow( winmgr.WIN_ID_MAINMENU )
			print 'dhkim MenuReceiverSetupNetwork check action parent'

	def onClick(self, controlId):
		print "MenuReceiverSetupNetwork onclick(): control %d" % controlId	

	def onFocus(self, controlId):
		print "onFocus(): control %d" % controlId


