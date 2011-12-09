import xbmc
import xbmcgui
import sys
import time

from gui.basedialog import BaseDialog

DIALOG_ID_KEYBOARD 					= 0

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

	def showDialog( self, dialogId ):
		try:
			self.dialogs[dialogId].doModal()
 			self.lastId = dialogId

		except:
			print "can not find dialog"

	def createAllDialogs( self ):
		import pvr.platform 
		self.scriptDir = pvr.platform.getPlatform().getScriptDir()

		from pvr.gui.dialogs.keyboarddialog import KeyboardDialog

		self.dialogs[ DIALOG_ID_KEYBOARD ]	               = KeyboardDialog('keyboarddialog.xml', self.scriptDir)	

