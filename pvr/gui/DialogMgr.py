import xbmc
import xbmcgui
import sys
import time

from gui.BaseDialog import BaseDialog
from pvr.Util import LOG_TRACE, LOG_ERR, LOG_WARN

DIALOG_ID_LNB_FREQUENCY				= 1
DIALOG_ID_CHANNEL_SEARCH			= 2
DIALOG_ID_START_RECORD				= 3
DIALOG_ID_STOP_RECORD				= 4
DIALOG_ID_SATELLITE_NUMERIC			= 5
DIALOG_ID_MOVE_ANTENNA				= 6
DIALOG_ID_ADD_NEW_SATELLITE			= 7
DIALOG_ID_SET_LIVE_PLATE			= 8
DIALOG_ID_SET_TRANSPONDER			= 9
DIALOG_ID_YES_NO_CANCEL				= 10
DIALOG_ID_NUMERIC_KEYBOARD			= 11
DIALOG_ID_POPUP_OK					= 12
DIALOG_ID_CONTEXT					= 13
DIALOG_ID_CHANNEL_JUMP				= 14
DIALOG_ID_FORCE_PROGRESS			= 15
DIALOG_ID_EXTEND_EPG				= 16
DIALOG_ID_ADD_TIMER					= 17


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
				LOG_TRACE( '---------------- create start record' )
				from pvr.gui.dialogs.DialogStartRecord import DialogStartRecord
				return DialogStartRecord('DialogStartRecord.xml', self.scriptDir)	

			elif aDialogId == DIALOG_ID_STOP_RECORD :
				LOG_TRACE( '---------------- create stop record')
				from pvr.gui.dialogs.DialogStopRecord import DialogStopRecord
				return DialogStopRecord('DialogStopRecord.xml', self.scriptDir)	

			elif aDialogId == DIALOG_ID_SATELLITE_NUMERIC :
				from pvr.gui.dialogs.DialogSatelliteNumeric import DialogSatelliteNumeric
				return DialogSatelliteNumeric('DialogSatelliteNumeric.xml', self.scriptDir)

			elif aDialogId == DIALOG_ID_MOVE_ANTENNA :
				from pvr.gui.dialogs.DialogMoveAntenna import DialogMoveAntenna
				return DialogMoveAntenna('DialogMoveAntenna.xml', self.scriptDir)

			elif aDialogId == DIALOG_ID_ADD_NEW_SATELLITE :
				from pvr.gui.dialogs.DialogAddNewSatellite import DialogAddNewSatellite
				return DialogAddNewSatellite('DialogAddNewSatellite.xml', self.scriptDir)

			elif aDialogId == DIALOG_ID_SET_TRANSPONDER :
				from pvr.gui.dialogs.DialogSetTransponder import DialogSetTransponder
				return DialogSetTransponder('DialogSetTransponder.xml', self.scriptDir)

			elif aDialogId == DIALOG_ID_YES_NO_CANCEL :
				from pvr.gui.dialogs.DialogYesNoCancel import DialogYesNoCancel
				return DialogYesNoCancel('DialogYesNoCancel.xml', self.scriptDir)

			elif aDialogId == DIALOG_ID_NUMERIC_KEYBOARD :
				from pvr.gui.dialogs.DialogNormalNumeric import DialogNormalNumeric
				return DialogNormalNumeric('DialogNormalNumeric.xml', self.scriptDir)

			elif aDialogId == DIALOG_ID_POPUP_OK :
				from pvr.gui.dialogs.DialogPopupOK import DialogPopupOK
				return DialogPopupOK('DialogPopupOK.xml', self.scriptDir)

			elif aDialogId == DIALOG_ID_CONTEXT :
				from pvr.gui.dialogs.DialogContext import DialogContext
				return DialogContext('DialogContext.xml', self.scriptDir)

			elif aDialogId == DIALOG_ID_CHANNEL_JUMP :
				from pvr.gui.dialogs.DialogChannelJump import DialogChannelJump
				return DialogChannelJump('DialogChannelJump.xml', self.scriptDir)

			elif aDialogId == DIALOG_ID_FORCE_PROGRESS :
				from pvr.gui.dialogs.DialogForceProgress import DialogForceProgress
				return DialogForceProgress('DialogForceProgress.xml', self.scriptDir)

			elif aDialogId == DIALOG_ID_EXTEND_EPG :
				from pvr.gui.dialogs.DialogExtendEPG import DialogExtendEPG
				return DialogExtendEPG('DialogExtendEPG.xml', self.scriptDir)

			elif aDialogId == DIALOG_ID_ADD_TIMER :
				from pvr.gui.dialogs.DialogAddTimer import DialogAddTimer
				return DialogAddTimer('DialogAddTimer.xml', self.scriptDir)

			elif aDialogId == DIALOG_ID_SET_LIVE_PLATE :
				from pvr.gui.dialogs.DialogSetLivePlate import DialogSetLivePlate
				return DialogSetLivePlate('DialogSetLivePlate.xml', self.scriptDir)

				
			else :
				LOG_ERR( 'can not find dialog' )

		except Exception, ex :
			LOG_ERR( '-----------------------> except[%s]' %ex )


