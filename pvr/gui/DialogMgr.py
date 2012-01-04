import xbmc
import xbmcgui
import sys
import time

from gui.BaseDialog import BaseDialog

DIALOG_ID_LNB_FREQUENCY				= 1
DIALOG_ID_CHANNEL_SEARCH			= 2
DIALOG_ID_RECORD					= 3


gDialogMgr = None

def getInstance():
	global gDialogMgr
	if not gDialogMgr:
		gDialogMgr = DialogMgr()
	else:
		print 'lael98 check already DialogMgr is created'

	return gDialogMgr


class DialogMgr(object):
	def __init__(self):
		self.dialogs = {}


	def getDialog( self, dialogId ) :
		import pvr.Platform 
		"""
		self.scriptDir = pvr.Platform.getPlatform().GetScriptDir()

		try :	
			if dialogId == DIALOG_ID_LNB_FREQUENCY :
				from pvr.gui.dialogs.dialoglnbfrequency import DialogLnbFrequency		
				return DialogLnbFrequency('dialoglnbfrequency.xml', self.scriptDir)	

			elif dialogId == DIALOG_ID_CHANNEL_SEARCH :
				from pvr.gui.dialogs.dialogchannelsearch import DialogChannelSearch
				return DialogChannelSearch('dialogchannelsearch.xml', self.scriptDir)	

			elif dialogId == DIALOG_ID_RECORD :
				from pvr.gui.dialogs.DialogRecord import DialogRecord
				return DialogRecord('DialogRecord.xml', self.scriptDir)	
				
			else :
				print "ERROR : can not find dialog"

		except Exception, e :
			print '-----------------------> except[%s]'% e
		"""
