import xbmc
import xbmcgui
import sys
import time
import thread

from pvr.gui.GuiConfig import *
from gui.BaseDialog import BaseDialog
from util.Logger import LOG_TRACE, LOG_WARN, LOG_ERR
import pvr.Platform
import pvr.ElisMgr
import pvr.DataCacheMgr
from pvr.XBMCInterface import XBMC_GetVolume, XBMC_GetMute


XBMC_WINDOW_DIALOG_KEYBOARD			= 10103
XBMC_WINDOW_DIALOG_NUMERIC			= 10109
XBMC_WINDOW_DIALOG_SELECT			= 12000
XBMC_WINDOW_DIALOG_PROGRESS			= 10101
XBMC_WINDOW_DIALOG_BUSY				= 10138
XBMC_WINDOW_DIALOG_YES_NO			= 10100
XBMC_WINDOW_DIALOG_OK				= 12002

XBMC_WINDOW_DIALOGS = [
	XBMC_WINDOW_DIALOG_KEYBOARD,
	XBMC_WINDOW_DIALOG_NUMERIC,
	XBMC_WINDOW_DIALOG_SELECT,
	XBMC_WINDOW_DIALOG_PROGRESS,
	XBMC_WINDOW_DIALOG_BUSY ]

DIALOG_ID_LNB_FREQUENCY				= 1
DIALOG_ID_CHANNEL_SEARCH			= 2
DIALOG_ID_START_RECORD				= 3
DIALOG_ID_STOP_RECORD				= 4
DIALOG_ID_SATELLITE_NUMERIC			= 5
DIALOG_ID_MOVE_ANTENNA				= 6
DIALOG_ID_ADD_NEW_SATELLITE			= 7
DIALOG_ID_SET_AUDIOVIDEO			= 8
DIALOG_ID_SET_TRANSPONDER			= 9
DIALOG_ID_YES_NO_CANCEL				= 10
DIALOG_ID_NUMERIC_KEYBOARD			= 11
DIALOG_ID_POPUP_OK					= 12
DIALOG_ID_CONTEXT					= 13
DIALOG_ID_CHANNEL_JUMP				= 14
DIALOG_ID_FORCE_PROGRESS			= 15
DIALOG_ID_EXTEND_EPG				= 16
DIALOG_ID_ADD_TIMER					= 17
DIALOG_ID_ADD_MANUAL_TIMER			= 18
DIALOG_ID_TIMESHIFT_JUMP			= 19
DIALOG_ID_INPUT_PINCODE				= 20
DIALOG_ID_SELECT					= 21
DIALOG_ID_BOOKMARK					= 22
DIALOG_ID_CAS_EVENT					= 23
DIALOG_ID_AUTO_POWER_DOWN			= 24
DIALOG_ID_HELP						= 25


DIALOG_ID_TEST_WORK			= 99


gDialogMgr = None

def GetInstance( ) :
	global gDialogMgr
	if not gDialogMgr :
		gDialogMgr = DialogMgr( )
	else:
		print 'Already DialogMgr is created'

	return gDialogMgr


class DialogMgr( object ) :
	def __init__( self ) :
		self.mDialogs = {}
		self.mShowingCount = 0
		self.mVolume = 0

		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.mDataCache = pvr.DataCacheMgr.GetInstance( )
		self.mPlatform =  pvr.Platform.GetPlatform( )

		self.mLock = thread.allocate_lock()
		thread.start_new_thread( self.AsyncCheckVolume,() )
		

	def GetDialog( self, aDialogId ) :
		import pvr.Platform 

		self.scriptDir = pvr.Platform.GetPlatform().GetScriptDir( )

		try :	#
			if aDialogId == DIALOG_ID_LNB_FREQUENCY :
				from pvr.gui.dialogs.DialogLnbFrequency import DialogLnbFrequency		
				return DialogLnbFrequency( 'DialogLnbFrequency.xml', self.scriptDir )	

			elif aDialogId == DIALOG_ID_CHANNEL_SEARCH :
				from pvr.gui.dialogs.DialogChannelSearch import DialogChannelSearch
				return DialogChannelSearch( 'DialogChannelSearch.xml', self.scriptDir )	

			elif aDialogId == DIALOG_ID_START_RECORD :
				LOG_TRACE( '---------------- create start record' )
				from pvr.gui.dialogs.DialogStartRecord import DialogStartRecord
				return DialogStartRecord( 'DialogStartRecord.xml', self.scriptDir )	

			elif aDialogId == DIALOG_ID_STOP_RECORD :
				LOG_TRACE( '---------------- create stop record')
				from pvr.gui.dialogs.DialogStopRecord import DialogStopRecord
				return DialogStopRecord( 'DialogStopRecord.xml', self.scriptDir )	

			elif aDialogId == DIALOG_ID_SATELLITE_NUMERIC :
				from pvr.gui.dialogs.DialogSatelliteNumeric import DialogSatelliteNumeric
				return DialogSatelliteNumeric( 'DialogSatelliteNumeric.xml', self.scriptDir )

			elif aDialogId == DIALOG_ID_MOVE_ANTENNA :
				from pvr.gui.dialogs.DialogMoveAntenna import DialogMoveAntenna
				return DialogMoveAntenna( 'DialogMoveAntenna.xml', self.scriptDir )

			elif aDialogId == DIALOG_ID_ADD_NEW_SATELLITE :
				from pvr.gui.dialogs.DialogAddNewSatellite import DialogAddNewSatellite
				return DialogAddNewSatellite( 'DialogAddNewSatellite.xml', self.scriptDir )

			elif aDialogId == DIALOG_ID_SET_TRANSPONDER :
				from pvr.gui.dialogs.DialogSetTransponder import DialogSetTransponder
				return DialogSetTransponder( 'DialogSetTransponder.xml', self.scriptDir )

			elif aDialogId == DIALOG_ID_YES_NO_CANCEL :
				from pvr.gui.dialogs.DialogYesNoCancel import DialogYesNoCancel
				return DialogYesNoCancel( 'DialogYesNoCancel.xml', self.scriptDir )

			elif aDialogId == DIALOG_ID_NUMERIC_KEYBOARD :
				from pvr.gui.dialogs.DialogNormalNumeric import DialogNormalNumeric
				return DialogNormalNumeric( 'DialogNormalNumeric.xml', self.scriptDir )

			elif aDialogId == DIALOG_ID_POPUP_OK :
				from pvr.gui.dialogs.DialogPopupOK import DialogPopupOK
				return DialogPopupOK( 'DialogPopupOK.xml', self.scriptDir )

			elif aDialogId == DIALOG_ID_CONTEXT :
				from pvr.gui.dialogs.DialogContext import DialogContext
				return DialogContext( 'DialogContext.xml', self.scriptDir )

			elif aDialogId == DIALOG_ID_CHANNEL_JUMP :
				from pvr.gui.dialogs.DialogChannelJump import DialogChannelJump
				return DialogChannelJump( 'DialogChannelJump.xml', self.scriptDir )

			elif aDialogId == DIALOG_ID_FORCE_PROGRESS :
				from pvr.gui.dialogs.DialogForceProgress import DialogForceProgress
				return DialogForceProgress( 'DialogForceProgress.xml', self.scriptDir )

			elif aDialogId == DIALOG_ID_EXTEND_EPG :
				from pvr.gui.dialogs.DialogExtendEPG import DialogExtendEPG
				return DialogExtendEPG( 'DialogExtendEPG.xml', self.scriptDir )

			elif aDialogId == DIALOG_ID_ADD_TIMER :
				from pvr.gui.dialogs.DialogAddTimer import DialogAddTimer
				return DialogAddTimer( 'DialogAddTimer.xml', self.scriptDir )

			elif aDialogId == DIALOG_ID_ADD_MANUAL_TIMER :
				from pvr.gui.dialogs.DialogAddManualTimer import DialogAddManualTimer
				return DialogAddManualTimer( 'DialogAddManualTimer.xml', self.scriptDir )

			elif aDialogId == DIALOG_ID_SET_AUDIOVIDEO :
				from pvr.gui.dialogs.DialogSetAudioVideo import DialogSetAudioVideo
				return DialogSetAudioVideo ( 'DialogSetAudioVideo.xml', self.scriptDir )

			elif aDialogId == DIALOG_ID_TIMESHIFT_JUMP :
				from pvr.gui.dialogs.DialogTimeshiftJump import DialogTimeshiftJump
				return DialogTimeshiftJump( 'DialogChannelJump.xml', self.scriptDir )

			elif aDialogId == DIALOG_ID_INPUT_PINCODE :
				from pvr.gui.dialogs.DialogInputPincode import DialogInputPincode
				return DialogInputPincode( 'DialogInputPincode.xml', self.scriptDir )

			elif aDialogId == DIALOG_ID_SELECT :
				from pvr.gui.dialogs.DialogMultiSelect import DialogMultiSelect
				return DialogMultiSelect( 'DialogMultiSelect.xml', self.scriptDir )

			elif aDialogId == DIALOG_ID_BOOKMARK :
				from pvr.gui.dialogs.DialogBookmark import DialogBookmark
				return DialogBookmark( 'DialogBookmark.xml', self.scriptDir )

			elif aDialogId == DIALOG_ID_CAS_EVENT :
				from pvr.gui.dialogs.DialogCasEvent import DialogCasEvent
				return DialogCasEvent( 'DialogCasEvent.xml', self.scriptDir )

			elif aDialogId == DIALOG_ID_AUTO_POWER_DOWN :
				from pvr.gui.dialogs.DialogAutoPowerDown import DialogAutoPowerDown
				return DialogAutoPowerDown( 'DialogAutoPowerDown.xml', self.scriptDir )

			elif aDialogId == DIALOG_ID_HELP :
				from pvr.gui.dialogs.DialogHelp import DialogHelp
				return DialogHelp( 'DialogHelp.xml', self.scriptDir )

			else :
				LOG_ERR( 'Cannot find dialog' )

		except Exception, ex :
			LOG_ERR( '-----------------------> except[%s]' %ex )


	def AsyncCheckVolume( self ) :
		currentID = -1
		while( 1 ) :
			currentID = xbmcgui.getCurrentWindowDialogId( )
			if currentID in XBMC_WINDOW_DIALOGS :
				LOG_TRACE( 'Volume check TEST : currentID=%d' %currentID )
				if self.mDataCache.GetMediaCenter( ) == False :
					LOG_TRACE( 'Volume check TEST : Update Volume ' )
					self.UpdateVolume( )
			time.sleep(0.5)


	def UpdateVolume( self, aVolumeStep = -1 ) :
		volume = 0
		if self.mPlatform.IsPrismCube( ) :
			if XBMC_GetMute() == False :
				volume =  XBMC_GetVolume( )

		else :
			volume = self.mCommander.Player_GetVolume( )
			if aVolumeStep != -1 :
				if aVolumeStep == 0 :
					if self.mCommander.Player_GetMute( ) :
						self.mCommander.Player_SetMute( False )
						return
					else :
						volume = aVolumeStep

				else :
					volume += aVolumeStep / 2

		LOG_TRACE( 'GET VOLUME=%d' %volume )
		if volume > MAX_VOLUME :
			volume = MAX_VOLUME

		if volume <= 0 :
			volume = 0
			self.mCommander.Player_SetMute( True )
		else :
			if self.mCommander.Player_GetMute( ) :
				self.mCommander.Player_SetMute( False )
			self.mCommander.Player_SetVolume( volume )

