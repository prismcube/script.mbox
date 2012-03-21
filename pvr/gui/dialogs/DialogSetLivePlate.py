import xbmc
import xbmcgui
import time
import sys

import pvr.gui.DialogMgr as DiaMgr
import pvr.DataCacheMgr as CacheMgr
from pvr.gui.BaseDialog import SettingDialog
from pvr.gui.BaseWindow import Action
from ElisEnum import ElisEnum
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.GuiConfig import *

from pvr.Util import LOG_WARN, LOG_TRACE, LOG_ERR
import pvr.Msg as Msg
import pvr.gui.windows.Define_string as MsgId
import threading

CONTEXT_ACTION_VIDEO_SETTING = 1
CONTEXT_ACTION_AUDIO_SETTING = 2

class DialogSetLivePlate( SettingDialog ) :
	def __init__( self, *args, **kwargs ) :
		SettingDialog.__init__( self, *args, **kwargs )
		LOG_TRACE( 'args[0]=[%s]' % args[0] )
		LOG_TRACE( 'args[1]=[%s]' % args[1] )

		self.mIsOk = False
		self.mSelectIdx = 0
		self.mSelectName = ''
		self.mDialogTitle = ''
		self.mAudioTrack = []
		self.mMode = CONTEXT_ACTION_VIDEO_SETTING
		self.mAsyncSetTimer = None

	def onInit( self ) :

		#self.mCtrlImgBox = self.getControl( 9001 )

		self.InitProperty( )
		self.SetHeaderLabel( self.mDialogTitle )
		self.DrawItem( )
		self.mIsOk = False

	def onAction( self, aAction ) :
		actionId = aAction.getId()
		self.GlobalAction( actionId )		

		if actionId == Action.ACTION_PREVIOUS_MENU :
			self.ResetAllControl()
			self.CloseDialog()
			
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.ResetAllControl()
			self.CloseDialog()

		elif actionId == Action.ACTION_MOVE_LEFT :
			self.ControlLeft()

		elif actionId == Action.ACTION_MOVE_RIGHT :
			self.ControlRight()
			
		elif actionId == Action.ACTION_MOVE_UP :
			self.ControlUp()
			
		elif actionId == Action.ACTION_MOVE_DOWN :
			self.ControlDown()


	def onClick( self, aControlId ) :
		self.mSelectIdx = id = self.GetGroupId( aControlId )
		LOG_TRACE( 'control[%s] getGroup[%s]'% (aControlId, id) )

		#if id >= E_DialogSpinEx01 and id <= E_DialogSpinEx04 :
			#self.RestartAsyncSet( )

		self.RestartAsyncSet( )

	def onFocus( self, aControlId ):
		pass


	def DrawItem( self ) :
		self.ResetAllControl( )

		#------------------ section1 : unused control -------------------
		for idx in range(9) :
			self.SetVisibleControl( idx*10 + E_DialogInput01, False )

		#------------------ section2 : using control -------------------
		if self.mMode == CONTEXT_ACTION_VIDEO_SETTING :

			self.AddEnumControl( E_DialogSpinEx01, 'HDMI Format' )
			self.AddEnumControl( E_DialogSpinEx02, 'Show 4:3', 'TV Screen Format' )
			self.AddEnumControl( E_DialogSpinEx03, 'HDMI Color Space' )
			self.AddEnumControl( E_DialogSpinEx04, 'TV System' )
			
			visibleControlIds = [ E_DialogSpinEx01, E_DialogSpinEx02, E_DialogSpinEx03, E_DialogSpinEx04 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			#self.getControl( E_SUBMENU_LIST_ID ).setVisible( True )

		elif self.mMode == CONTEXT_ACTION_AUDIO_SETTING :
			LOG_TRACE('list audio[%s]'% self.mAudioTrack)
			self.AddUserEnumControl( E_DialogSpinEx01, Msg.Strings( MsgId.LANG_AUDIO_HDMI ), self.mAudioTrack, 0)

			visibleControlIds = [ E_DialogSpinEx01 ]
			self.SetVisibleControls( visibleControlIds, True )
			self.SetEnableControls( visibleControlIds, True )

			#unused visible false
			hideControlIds = [ E_DialogSpinEx02, E_DialogSpinEx03, E_DialogSpinEx04 ]
			self.SetVisibleControls( hideControlIds, False )

		#self.AddOkCanelButton( )
		self.SetAutoHeight( True )
		self.InitControl( )


	def IsOK( self ) :
		return self.mIsOk

	def GetValue( self, aFlag ) :
		#LOG_TRACE('SelectIdx[%s] SelectName[%s] isOk[%s]' % ( self.mSelectIdx, self.mSelectName, self.mIsOk ) )
		return self.mSelectIdx, self.mSelectName, self.mIsOk

	def SetValue( self, aMode ) :
		self.mMode = aMode

	def SetProperty( self ) : 
		if self.mMode == CONTEXT_ACTION_VIDEO_SETTING :
			self.ControlSelect( )

		elif self.mMode == CONTEXT_ACTION_AUDIO_SETTING :
			idx = self.GetSelectedIndex( E_DialogSpinEx01 )
			LOG_TRACE('idx[%s] track[%s]'% (idx, self.mAudioTrack))
			self.mSelectName = self.mAudioTrack[idx]

			self.mDataCache.Audiotrack_select( idx )

	def InitProperty( self ) :
		if self.mMode == CONTEXT_ACTION_VIDEO_SETTING :
			self.mDialogTitle = 'VIDEO SETTING'

		elif self.mMode == CONTEXT_ACTION_AUDIO_SETTING :
			self.mDialogTitle = 'AUDIO SETTING'

			getCount = self.mDataCache.Audiotrack_GetCount( )
			selectIdx= self.mDataCache.Audiotrack_GetSelectedIndex( )
			#LOG_TRACE('AudioTrack count[%s] select[%s]'% (getCount, selectIdx) )

			self.mAudioTrack = []
			for i in range(getCount) :
				iTrack = self.mDataCache.Audiotrack_Get( i )
				#LOG_TRACE('getTrack: name[%s] lang[%s]'% (iTrack.mName, iTrack.mLang) )
				if iTrack :
					label = '%s-%s'% (iTrack.mName, iTrack.mLang)
					self.mAudioTrack.append( label )


	def RestartAsyncSet( self ) :
		self.StopAsyncSet( )
		self.StartAsyncSet( )


	def StartAsyncSet( self ) :
		self.mAsyncSetTimer = threading.Timer( 3, self.AsyncSetProperty ) 				
		self.mAsyncSetTimer.start()


	def StopAsyncSet( self ) :
		if self.mAsyncSetTimer and self.mAsyncSetTimer.isAlive() :
			self.mAsyncSetTimer.cancel()
			del self.mAsyncSetTimer

		self.mAsyncSetTimer  = None


	def AsyncSetProperty( self ) :
		self.SetProperty( )


