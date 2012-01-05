import xbmc
import xbmcgui
import sys
import time

from gui.BaseDialog import BaseDialog

DIALOG_ID_LNB_FREQUENCY				= 1
DIALOG_ID_CHANNEL_SEARCH			= 2
DIALOG_ID_START_RECORD				= 3
DIALOG_ID_STOP_RECORD				= 4

gDialogMgr = None

def GetInstance():
	global gDialogMgr
	if not gDialogMgr:
		gDialogMgr = DialogMgr()
	else:
		print 'lael98 check already DialogMgr is created'

	return gDialogMgr


class DialogMgr(object):
	def __init__(self):
		self.mDialogs = {}


	def GetDialog( self, aDialogId ) :
		import pvr.Platform 

		self.scriptDir = pvr.Platform.GetPlatform().GetScriptDir()

		try :	#
			if aDialogId == DIALOG_ID_LNB_FREQUENCY :
				from pvr.gui.dialogs.DialogLnbFrequency import DialogLnbFrequency		
				return DialogLnbFrequency('DialogLnbFrequency.xml', self.scriptDir)	

			elif aDialogId == DIALOG_ID_CHANNEL_SEARCH :
				from pvr.gui.dialogs.DialogChannelSearch import DialogChannelSearch
				return DialogChannelSearch('DialogChannelSearch.xml', self.scriptDir)	

			elif aDialogId == DIALOG_ID_START_RECORD :
				print '---------------- create start record'
				from pvr.gui.dialogs.DialogStartRecord import DialogStartRecord
				return DialogStartRecord('DialogStartRecord.xml', self.scriptDir)	

			elif aDialogId == DIALOG_ID_STOP_RECORD :
				print '---------------- create start record'
				from pvr.gui.dialogs.DialogStopRecord import DialogStopRecord
				return DialogStopRecord('DialogStopRecord.xml', self.scriptDir)	
				
			else :
				print "ERROR : can not find dialog"

		except Exception, e :
			print '-----------------------> except[%s]'% e

