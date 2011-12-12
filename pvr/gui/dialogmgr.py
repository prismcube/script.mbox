import xbmc
import xbmcgui
import sys
import time

from gui.basedialog import BaseDialog

DIALOG_ID_KEYBOARD 					= 0
DIALOG_ID_NUMERIC					= 1
DIALOG_ID_LNB_FREQUENCY				= 2


gDialogmgr = None

def getInstance():
	global gDialogmgr
	if not gDialogmgr:
		gDialogmgr = DialogMgr()
	else:
		print 'lael98 check already dialogmgr is created'

	return gDialogmgr


class DialogMgr(object):
	def __init__(self):
		self.dialogs = {}

		self.createAllDialogs( )
		self.titleLabel = None
		self.defaultText = None
		self.resultText = None


	def showDialog( self, dialogId ):
		try:
			self.dialogs[dialogId].doModal()
 			self.lastId = dialogId

		except:
			print "can not find dialog"


	def createAllDialogs( self ):
		import pvr.platform 
		self.scriptDir = pvr.platform.getPlatform().getScriptDir()

		from pvr.gui.dialogs.dialogkeyboard import DialogKeyboard
		from pvr.gui.dialogs.dialognumeric import DialogNumeric
		from pvr.gui.dialogs.dialoglnbfrequency import DialogLnbFrequency

		
		self.dialogs[ DIALOG_ID_KEYBOARD ]	               = DialogKeyboard('dialogkeyboard.xml', self.scriptDir)	
		self.dialogs[ DIALOG_ID_NUMERIC ]	               = DialogNumeric('dialognumeric.xml', self.scriptDir)	
		self.dialogs[ DIALOG_ID_LNB_FREQUENCY ]	           = DialogLnbFrequency('dialoglnbfrequency.xml', self.scriptDir)	


	def setDefaultText( self, text ):
		self.defaultText = text


	def getDefaultText( self ):
		return self.defaultText


	def setTitleLabel( self, text ):
		self.titleLabel = text


	def getTitleLabel( self ):
		return self.titleLabel


	def setResultText( self, text ):
		self.resultText = text


	def getResultText( self ):
		return self.resultText
