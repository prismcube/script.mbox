
import xbmc
import xbmcgui
import time
import sys


from pvr.gui.BaseDialog import SettingDialog
from pvr.gui.BaseWindow import Action
from  pvr.TunerConfigMgr import *
from ElisEnum import ElisEnum
import pvr.gui.DialogMgr as DiaMgr
from ElisProperty import ElisPropertyEnum


import pvr.ElisMgr

from pvr.Util import RunThread, GuiLock, LOG_TRACE, LOG_WARN, LOG_ERR, TimeToString, TimeFormatEnum
from pvr.gui.GuiConfig import *


# Control IDs
E_LABEL_RECORD_NAME			= 101
E_LABEL_EPG_START_TIME		= 102
E_LABEL_EPG_END_TIME		= 103
E_BUTTON_ADD				= 200
E_BUTTON_CANCEL				= 201

E_ONCE						= 0
E_DAILY						= 1
E_WEEKLY					= 2

LIST_RECORDING_MODE	= [ 'Once', 'Daily', 'Weekly' ]
LIST_WEEKLY = ['Sun','Mon','Tue', 'Wed', 'The', 'Fri', 'Sat' ]


class DialogAddManualTimer( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		self.mEPG = None
		self.mIsEdit = False
		self.mRecordingMode = E_ONCE
		self.mChanne = None
		self.mTimer = -1;


	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId  )

		if self.mIsEdit == True :
			self.SetHeaderLabel( 'Edit Recording' )		
		else :
			self.SetHeaderLabel( 'Add Manual Recording' )


		self.Reload( )
		#self.mEventBus.Register( self )

		self.mIsOk = E_DIALOG_STATE_CANCEL

		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_OK_ID, 'Confirm' )
		self.SetButtonLabel( E_SETTING_DIALOG_BUTTON_CANCEL_ID, 'Cancel' )
		self.DrawItem( )

		

	def onAction( self, aAction ):
		actionId = aAction.getId( )
		focusId = self.GetFocusId( )
		self.GlobalAction( actionId )		

		LOG_TRACE( 'actionId=%d' %actionId )
			
		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.ResetAllControl( )
			self.Close()		

		elif actionId == Action.ACTION_SELECT_ITEM :
			LOG_TRACE('FOCUS=%d' %focusId )
			LOG_TRACE('FOCUS2=%d' %E_DialogSpinEx01 )			
			if self.GetGroupId( focusId ) == E_DialogSpinEx01 :
				self.mRecordingMode = self.GetSelectedIndex( E_DialogSpinEx01 )
				self.DrawItem()
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.ResetAllControl( )
			self.Close()		

		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp( )
	
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown( )

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft( )
				
		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight( )

		else :
			LOG_WARN( 'Unknown Action' )


	def onClick( self, aControlId ):

		groupId = self.GetGroupId( aControlId )

		if groupId == E_SETTING_DIALOG_BUTTON_OK_ID :			
			self.mIsOk = E_DIALOG_STATE_YES
			self.DoAddTimer()
			self.ResetAllControl( )
			self.Close( )

		elif groupId == E_SETTING_DIALOG_BUTTON_CANCEL_ID :
			self.mIsOk = E_DIALOG_STATE_NO
			self.ResetAllControl( )
			self.Close( )


		"""
		if groupId == E_DialogSpinEx01 :
			self.mIsWest = self.GetSelectedIndex( E_DialogSpinEx01 )

		elif groupId == E_DialogInput02 :
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_SATELLITE_NUMERIC )
 			dialog.SetDialogProperty( 'Set Longitude', self.mLongitude )
 			dialog.doModal( )

 			if dialog.IsOK() == E_DIALOG_STATE_YES :
	 			self.mLongitude  = dialog.GetNumber( )
	 			self.DrawItem( )

		elif groupId == E_DialogSpinEx02 :
			self.mIsCBand = self.GetSelectedIndex( E_DialogSpinEx02 )

		elif groupId == E_DialogInput01 :
			self.mSatelliteName = InputKeyboard( E_INPUT_KEYBOARD_TYPE_NO_HIDE, 'Satellite Name', self.mSatelliteName, 15 )
			self.DrawItem( )

		elif groupId == E_SETTING_DIALOG_BUTTON_OK_ID :
			self.mIsOk = E_DIALOG_STATE_YES
			self.ResetAllControl( )
			self.CloseDialog( )

		elif groupId == E_SETTING_DIALOG_BUTTON_CANCEL_ID :
			self.mIsOk = E_DIALOG_STATE_NO
			self.ResetAllControl( )
			self.CloseDialog( )

	
		if focusId == E_BUTTON_ADD :
			self.mIsOk = E_DIALOG_STATE_YES
			self.Close( )

		elif focusId == E_BUTTON_CANCEL :
			self.mIsOk = E_DIALOG_STATE_CANCEL
			self.Close( )
		"""
		

	def onFocus( self, aControlId ):
		pass


	@GuiLock	
	def onEvent( self, aEvent ):
		pass
		"""
		if xbmcgui.getCurrentWindowId() == self.winId :
			print 'Do Event'
			pass
		"""


	def SetEditMode( self, aIsEdit ):
		self.mIsEdit = aIsEdit


	def SetEPG( self, aEPG ):
		self.mEPG = aEPG


	def SetChannel( self, aChannel ) :
		self.mChannel = aChannel


	def SetTimer( self, aTimer ):
		self.mTimer = aTimer


	def IsOK( self ) :
		return self.mIsOk


	def Close( self ):
		#self.mEventBus.Deregister( self )
		self.CloseDialog( )


	def Reload ( self ) :
		LOG_TRACE('')
		return


		try :
			if self.mEPG != None and self.mEPG.mError == 0:
				self.mEPG.printdebug( )		

				localOffset = self.mDataCache.Datetime_GetLocalOffset()
				localTime = self.mDataCache.Datetime_GetLocalTime( )

				startTime = self.mEPG.mStartTime + localOffset
				endTime =  startTime  + self.mEPG.mDuration
			

				LOG_TRACE('START : %s' %TimeToString( startTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )
				LOG_TRACE('CUR : %s' %TimeToString( localTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )			
				LOG_TRACE('END : %s' %TimeToString( endTime, TimeFormatEnum.E_DD_MM_YYYY_HH_MM ) )			
				self.getControl( E_LABEL_RECORD_NAME ).setLabel( '%s' %self.mEPG.mEventName )

				self.getControl( E_LABEL_EPG_START_TIME ).setLabel( 'Start : %s' %TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
				self.getControl( E_LABEL_EPG_END_TIME ).setLabel( 'End : %s' %TimeToString( endTime, TimeFormatEnum.E_HH_MM ) )
			
		except Exception, ex :
			LOG_ERR( "Exception %s" %ex)


	def DrawItem( self ) :
		LOG_TRACE('self.mRecordingMode=%d' %self.mRecordingMode )
		if self.mEPG :
			LOG_TRACE('Has EPG')
			self.mEPG.printdebug()
		else  :
			LOG_TRACE('Has no EPG')
			self.mChannel.printdebug()

		self.ResetAllControl( )

		if self.mIsEdit  == True :
			self.AddUserEnumControl( E_DialogSpinEx01, 'Recording', LIST_RECORDING_MODE, self.mRecordingMode )
			#SetEnableControl

		else :
			self.AddUserEnumControl( E_DialogSpinEx01, 'Recording', LIST_RECORDING_MODE, self.mRecordingMode )
			self.SetEnableControl(E_DialogSpinEx01,  True )
			if self.mEPG  :
				self.AddInputControl( E_DialogInput01, 'Name', self.mEPG.mEventName )
			else :
				self.AddInputControl( E_DialogInput01, 'Name', self.mChannel.mName )
				
			self.SetEnableControl(E_DialogInput01,  True )
			
			if self.mRecordingMode == E_ONCE :
				startTime = self.mDataCache.Datetime_GetLocalTime()
				prop = ElisPropertyEnum( 'Default Rec Duration', self.mCommander )
				duration = prop.GetProp( )
				
				if self.mEPG :
					startTime = self.mEPG.mStartTime + self.mDataCache.Datetime_GetLocalOffset()
					duraton = self.mEPG.mDuration
					endTime = startTime + duraton
					
				self.AddInputControl( E_DialogInput02, 'Date :', TimeToString( startTime, TimeFormatEnum.E_AW_DD_MM_YYYY ) )
				self.SetVisibleControl( E_DialogInput02, True )
				self.SetVisibleControl( E_DialogSpinDay, False )
				
				self.AddInputControl( E_DialogInput03, 'Start Time :',  TimeToString( startTime, TimeFormatEnum.E_HH_MM ) )
				self.AddInputControl( E_DialogInput04, 'End Time :',  TimeToString( endTime, TimeFormatEnum.E_HH_MM) )
				
			else :
				self.AddListControl( E_DialogSpinDay, LIST_WEEKLY, 0 )
				self.SetListControlTitle( E_DialogSpinDay, 'Daily' )
				self.SetVisibleControl( E_DialogInput02, False )
				self.SetVisibleControl( E_DialogSpinDay, True )

				self.AddInputControl( E_DialogInput03, 'Start Time :',  '00:00' )
				self.AddInputControl( E_DialogInput04, 'End Time :',  '12:00' )

			self.AddOkCanelButton( )
			self.SetAutoHeight( True )

		self.InitControl( )


	def DoAddTimer( self ) :
		LOG_TRACE('')
		if self.mIsEdit  == True :
			LOG_TRACE('Edit Mode')
	
		else :
			LOG_TRACE('Add Mode')		
			if self.mRecordingMode == E_ONCE :
				if self.mEPG  :
					LOG_TRACE('EPG and Once')
				else:
					LOG_TRACE('no EPG and Once')				
			else :
				if self.mEPG  :
					LOG_TRACE('EPG and Daily or Weekly')
				else:
					LOG_TRACE('no EPG and Daily or Weekly')				
			

