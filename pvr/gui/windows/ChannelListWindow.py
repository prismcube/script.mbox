import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DiaMgr
import pvr.DataCacheMgr as CacheMgr

from pvr.gui.BaseWindow import BaseWindow, Action
from pvr.gui.GuiConfig import *

from ElisEnum import ElisEnum
from ElisEventBus import ElisEventBus
from ElisEventClass import *
from ElisClass import *

from pvr.Util import RunThread, GuiLock, GuiLock2, MLOG, LOG_WARN, LOG_TRACE, LOG_ERR
from pvr.PublicReference import GetSelectedLongitudeString, EpgInfoTime, EpgInfoClock, EpgInfoComponentImage, EnumToString, ClassToList, AgeLimit, ParseLabelToCh
import pvr.ElisMgr
from ElisProperty import ElisPropertyEnum, ElisPropertyInt

from copy import deepcopy
from inspect import currentframe
import threading, time, os, re

import pvr.Msg as Msg
import pvr.gui.windows.Define_string as MsgId

FLAG_MASK_ADD    = 0x01
FLAG_MASK_NONE   = 0x00
FLAG_MODE_TV     = ElisEnum.E_SERVICE_TYPE_TV
FLAG_MODE_RADIO  = ElisEnum.E_SERVICE_TYPE_RADIO
FLAG_MODE_DATA   = ElisEnum.E_SERVICE_TYPE_DATA
FLAG_SLIDE_OPEN  = 0
FLAG_SLIDE_INIT  = 1
FLAG_OPT_LIST    = 0
FLAG_OPT_GROUP   = 1
FLAG_OPT_MOVE    = 2
FLAG_OPT_MOVE_OK = 3
FLAG_OPT_MOVE_UPDOWN = 4
FLAG_CLOCKMODE_ADMYHM   = 1
FLAG_CLOCKMODE_AHM      = 2
FLAG_CLOCKMODE_HMS      = 3
FLAG_CLOCKMODE_HHMM     = 4
FLAG_MODE_JUMP      = True
FLAG_ZAPPING_LOAD   = 0
FLAG_ZAPPING_CHANGE = 1

#slide index
E_SLIDE_ACTION_MAIN     = 0
E_SLIDE_ACTION_SUB      = 1
E_SLIDE_ALLCHANNEL      = 0
E_SLIDE_MENU_SATELLITE  = 1
E_SLIDE_MENU_FTACAS     = 2
E_SLIDE_MENU_FAVORITE   = 3
#E_SLIDE_MENU_EDITMODE   = 4
#E_SLIDE_MENU_DELETEALL  = 5
E_SLIDE_MENU_BACK       = 5

#list property
E_IMG_ICON_LOCK   = 'IconLockFocus.png'
E_IMG_ICON_ICAS   = 'IconCas.png'
E_IMG_ICON_MARK   = 'confluence/OverlayWatched.png'
E_IMG_ICON_REC   = 'IconPlateRec.png'
E_IMG_ICON_TITLE1 = 'IconHeaderTitleSmall.png'
E_IMG_ICON_TITLE2 = 'icon_setting_focus.png'
E_IMG_ICON_UPDOWN = 'DI_Cursor_UpDown.png'
E_TAG_COLOR_RED   = '[COLOR red]'
E_TAG_COLOR_GREY  = '[COLOR grey]'
E_TAG_COLOR_GREY3 = '[COLOR grey3]'
E_TAG_COLOR_END   = '[/COLOR]'

#db
E_SYNCHRONIZED  = 0
E_ASYNCHRONIZED = 1
E_TABLE_ALLCHANNEL = 0
E_TABLE_ZAPPING = 1

#dialog menu
CONTEXT_ACTION_LOCK				= 1 
CONTEXT_ACTION_UNLOCK			= 2
CONTEXT_ACTION_SKIP				= 3
CONTEXT_ACTION_UNSKIP			= 4
CONTEXT_ACTION_DELETE			= 5
CONTEXT_ACTION_MOVE				= 6
CONTEXT_ACTION_ADD_TO_FAV		= 7
CONTEXT_ACTION_CREATE_GROUP_FAV	= 10
CONTEXT_ACTION_RENAME_FAV		= 11
CONTEXT_ACTION_DELETE_FAV		= 12


class ChannelListWindow( BaseWindow ) :

	def __init__( self, *args, **kwargs ) :
		BaseWindow.__init__( self, *args, **kwargs )

		#submenu list
		self.mListAllChannel= []
		self.mListSatellite = []
		self.mListCasList   = []
		self.mListFavorite  = []
		self.mElisZappingModeInfo = None
		self.mElisSetZappingModeInfo = None
		self.mLastMainSlidePosition = 0
		self.mLastSubSlidePosition = 0
		self.mSelectMainSlidePosition = 0
		self.mSelectSubSlidePosition = 0
		self.mLastChannel = None
		self.mListItems = None

		self.mEventId = 0
		self.mLocalTime = 0
		self.mAsyncTuneTimer = None

		self.mPropertyAge = 0
		self.mPropertyPincode = -1
		self.mPincodeEnter = FLAG_MASK_NONE
		self.mViewMode = WinMgr.WIN_ID_CHANNEL_LIST_WINDOW
		
	def __del__(self):
		LOG_TRACE( 'destroyed ChannelList' )

		# end thread
		self.mEnableThread = False


	def onInit(self):
		LOG_TRACE( 'Enter' )

		self.mWinId = xbmcgui.getCurrentWindowId( )
		self.mWin = xbmcgui.Window( self.mWinId )
		LOG_TRACE( 'winID[%d]'% self.mWinId)

		#starttime = time.time( )
		#print '==================== TEST TIME[ONINIT] START[%s]'% starttime

		#header
		#self.mCtrlImgRec1            = self.getControl( 10 )
		#self.mCtrlLblRec1            = self.getControl( 11 )
		#self.mCtrlImgRec2            = self.getControl( 15 )
		#self.mCtrlLblRec2            = self.getControl( 16 )
		self.mCtrlLblPath1           = self.getControl( 21 )
		self.mCtrlGropOpt            = self.getControl( 500 )
		self.mCtrlBtnOpt             = self.getControl( 501 )
		self.mCtrlLblOpt1            = self.getControl( 502 )
		self.mCtrlLblOpt2            = self.getControl( 503 )

		#main menu
		self.mCtrlGropMainmenu       = self.getControl( 100 )
		self.mCtrlBtnMenu            = self.getControl( 101 )
		self.mCtrlListMainmenu       = self.getControl( 102 )

		#sub menu list
		self.mCtrlGropSubmenu        = self.getControl( 9001 )
		self.mCtrlListSubmenu        = self.getControl( 112 )

		#sub menu btn
		self.mCtrlRdoTV              = self.getControl( 113 )
		self.mCtrlRdoRadio           = self.getControl( 114 )
		self.mCtrlBtnEdit            = self.getControl( 115 )
		self.mCtrlBtnDelAll          = self.getControl( 116 )

		#ch list
		self.mCtrlGropCHList         = self.getControl( 49 )
		self.mCtrlListCHList         = self.getControl( 50 )

		#info
		self.mCtrlImgVideoPos        = self.getControl( 301 )
		self.mCtrlChannelName        = self.getControl( 303 )
		self.mCtrlEventName          = self.getControl( 304 )
		self.mCtrlEventTime          = self.getControl( 305 )
		self.mCtrlProgress           = self.getControl( 306 )
		self.mCtrlLongitudeInfo      = self.getControl( 307 )
		self.mCtrlCareerInfo         = self.getControl( 308 )
		self.mCtrlLockedInfo         = self.getControl( 309 )
		self.mCtrlServiceTypeImg1    = self.getControl( 310 )
		self.mCtrlServiceTypeImg2    = self.getControl( 311 )
		self.mCtrlServiceTypeImg3    = self.getControl( 312 )
		self.mCtrlSelectItem         = self.getControl( 401 )

		self.mIsSelect = False
		self.mIsMark = True
		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset( )
		self.mChannelListServiceType = ElisEnum.E_SERVICE_TYPE_INVALID
		self.mChannelListSortMode = ElisEnum.E_SORT_BY_DEFAULT
		self.mZappingMode = ElisEnum.E_MODE_ALL
		self.mZappingName = ''
		self.mChannelList = []
		self.mRecCount = 0
		self.mRecChannel1 = []
		self.mRecChannel2 = []
		self.mNavEpg = None
		self.mNavChannel = None
		self.mCurrentChannel = None
		self.mRecoveryChannel = None
		self.mSlideOpenFlag = False
		self.mFlag_EditChanged = False
		self.mFlag_DeleteAll = False

		#edit mode
		self.mIsSave = FLAG_MASK_NONE
		self.mMarkList = []
		self.mEditFavorite = []
		self.mMoveFlag = False
		self.mMoveItem = []

		self.SetVideoSize( )

		#initialize get cache
		zappingmode = None
		zappingmode = self.mDataCache.Zappingmode_GetCurrent( )
		if zappingmode :
			self.mElisSetZappingModeInfo = deepcopy( zappingmode )
		else :
			self.mElisSetZappingModeInfo = ElisIZappingMode()
		self.ShowRecording( )

		self.mPropertyAge = ElisPropertyEnum( 'Age Limit', self.mCommander ).GetProp( )
		self.mPropertyPincode = ElisPropertyInt( 'PinCode', self.mCommander ).GetProp( )
		if self.mDataCache.mCacheReload :
			self.mListItems = None
			self.mDataCache.mCacheReload = False
			LOG_TRACE('NEW APPEND LIST reason by reload cache')

		#initialize get channel list
		self.InitSlideMenuHeader( )

		try :
			#first get is used cache, reason by fast load
			iChannel = self.mDataCache.Channel_GetCurrent( )
			if iChannel :
				self.mRecoveryChannel = iChannel
				self.mNavChannel = iChannel
				self.mCurrentChannel = iChannel.mNumber

				strType = self.UpdateServiceType( iChannel.mServiceType )
				label = '%s - %s'% (strType, iChannel.mName)
				self.UpdateLabelGUI( self.mCtrlChannelName.getId( ), label )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		self.InitChannelList( )

		#clear label
		self.ResetLabel( )

		#initialize get epg event
		self.InitEPGEvent( )
		self.UpdateLabelInfo( )

		#Event Register
		self.mEventBus.Register( self )

		#run thread
		self.mEnableThread = True
		self.CurrentTimeThread( )

		self.mAsyncTuneTimer = None

		#endtime = time.time( )
		#print '==================== TEST TIME[ONINIT] END[%s] loading[%s]'% (endtime, endtime-starttime )
		LOG_TRACE( 'Leave' )

	def onAction(self, aAction):
		#LOG_TRACE( 'Enter' )
		id = aAction.getId( )

		self.GlobalAction( id )		

		if id >= Action.REMOTE_0 and id <= Action.REMOTE_9:
			self.KeySearch( id-Action.REMOTE_0 )

		elif id >= Action.ACTION_JUMP_SMS2 and id <= Action.ACTION_JUMP_SMS9 :
			rKey = id - (Action.ACTION_JUMP_SMS2 - 2)
			self.KeySearch( rKey )

		elif id == Action.ACTION_PREVIOUS_MENU or id == Action.ACTION_PARENT_DIR:
			#LOG_TRACE( 'goto previous menu' )
			self.SetGoBackWindow( )

		elif id == Action.ACTION_SELECT_ITEM:
			self.GetFocusId( )
			#LOG_TRACE( 'item select, action ID[%s]'% id )

			if self.mFocusId == self.mCtrlListMainmenu.getId( ) :
				position = self.mCtrlListMainmenu.getSelectedPosition( )
				#LOG_TRACE( 'focus[%s] idx_main[%s]'% (self.mFocusId, position) )

				if position == E_SLIDE_MENU_BACK :
					self.mCtrlListCHList.setEnabled(True)
					self.setFocusId( self.mCtrlGropCHList.getId( ) )

				else :
					self.SubMenuAction( E_SLIDE_ACTION_MAIN, position )

		elif id == Action.ACTION_MOVE_RIGHT :
			pass

		elif id == Action.ACTION_MOVE_LEFT :
			self.GetFocusId( )
			if self.mFocusId == self.mCtrlListCHList.getId( ) :
				self.GetSlideMenuHeader( FLAG_SLIDE_OPEN )
				self.mSlideOpenFlag = True

		elif id == Action.ACTION_MOVE_UP or id == Action.ACTION_MOVE_DOWN or \
			 id == Action.ACTION_PAGE_UP or id == Action.ACTION_PAGE_DOWN :
			self.GetFocusId( )
			if self.mFocusId == self.mCtrlListCHList.getId( ) :
				if self.mMoveFlag :
					self.SetEditChanneltoMove( FLAG_OPT_MOVE_UPDOWN, id )
					return

				else :
					self.RestartAsyncEPG( )

			if self.mFocusId == self.mCtrlListMainmenu.getId( ) :
				position = self.mCtrlListMainmenu.getSelectedPosition( )
				self.SubMenuAction( E_SLIDE_ACTION_MAIN, position )

			elif self.mFocusId == self.mCtrlBtnOpt :
				self.mCtrlListCHList.setEnabled( True )
				self.setFocusId( self.mCtrlGropCHList.getId( ) )


		elif id == Action.ACTION_CONTEXT_MENU :
			#LOG_TRACE( 'popup opt' )
			self.PopupOpt( )


		elif id == 13: #'x'
			#this is test
			LOG_TRACE( 'language[%s]'% xbmc.getLanguage( ) )

		#LOG_TRACE( 'Leave' )

	def onClick(self, aControlId):
		LOG_TRACE( 'onclick focusID[%d]'% aControlId )

		if aControlId == self.mCtrlListCHList.getId( ) :
			if self.mViewMode == WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW :
				try:
					if self.mMoveFlag :
						self.SetEditChanneltoMove( FLAG_OPT_MOVE_OK )
						return

					#Mark mode
					if self.mIsMark == True :
						idx = self.mCtrlListCHList.getSelectedPosition( )
						self.SetEditMarkupGUI('mark', idx )

						GuiLock2( True )
						self.setFocusId( self.mCtrlGropCHList.getId( ) )
						self.mCtrlListCHList.selectItem( idx+1 )
						GuiLock2( False )

						self.mCtrlSelectItem.setLabel( str('%s'% (idx+1) ) )

					#Turn mode
					#else :
					#	self.SetChannelTune( )

				except Exception, e:
					LOG_TRACE( 'Error except[%s]'% e )

			else :
				if self.mChannelList :
					self.SetChannelTune( )

		elif aControlId == self.mCtrlBtnMenu.getId( ) or aControlId == self.mCtrlListMainmenu.getId( ) :
			#list view
			LOG_TRACE( '#############################' )

		elif aControlId == self.mCtrlListSubmenu.getId( ) :
			#list action
			position = self.mZappingMode
			self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )
			#LOG_TRACE( 'onclick focus[%s] idx_sub[%s]'% (aControlId, position) )

			#slide close
			GuiLock2( True )
			self.mCtrlListCHList.setEnabled(True)
			self.setFocusId( self.mCtrlGropCHList.getId( ) )
			GuiLock2( False )

		elif aControlId == self.mCtrlBtnOpt.getId( ):
			#LOG_TRACE( 'onclick Opt' )
			self.PopupOpt( )

		elif aControlId == self.mCtrlBtnEdit.getId( ):
			self.SetGoBackEdit( )

		elif aControlId == self.mCtrlBtnDelAll.getId( ):
			ret = self.SetDeleteAll( )

			if ret == E_DIALOG_STATE_YES :
				self.mListItems = None
				self.mChannelList = None
				self.mNavEpg = None
				self.mNavChannel = None

				self.InitSlideMenuHeader( )

				self.mCtrlListCHList.reset( )
				self.InitChannelList( )

				#clear label
				self.ResetLabel( )
				self.UpdateLabelInfo( )

				#slide close
				GuiLock2( True )
				self.mCtrlListCHList.setEnabled(True)
				self.setFocusId( self.mCtrlGropCHList.getId( ) )
				GuiLock2( False )


		elif aControlId == self.mCtrlRdoTV.getId( ):
			self.SetModeChanged( FLAG_MODE_TV )

		elif aControlId == self.mCtrlRdoRadio.getId( ):
			self.SetModeChanged( FLAG_MODE_RADIO )

		LOG_TRACE( 'Leave' )


	def onFocus(self, controlId):
		#LOG_TRACE( 'control %d' % controlId )
		pass

	def SetVideoSize( self ) :
		LOG_TRACE( 'Enter' )
		h = self.mCtrlImgVideoPos.getHeight( )
		w = self.mCtrlImgVideoPos.getWidth( )
		pos=list(self.mCtrlImgVideoPos.getPosition( ) )
		x = pos[0] - 20
		y = pos[1] + 10
		#LOG_TRACE('==========h[%s] w[%s] x[%s] y[%s]'% (h,w,x,y) )

		ret = self.mDataCache.Player_SetVIdeoSize( x, y, w, h ) 

		LOG_TRACE( 'Leave' )

	def SetDeleteAll( self ) :
		LOG_TRACE( 'Enter' )

		ret = E_DIALOG_STATE_NO

		#ask save question
		head =  Msg.Strings( MsgId.LANG_CONFIRM )
		line1 = Msg.Strings( MsgId.LANG_DELETE_ALL_CHANNEL )

		GuiLock2( True )
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( head, line1 )
		dialog.doModal( )
		GuiLock2( False )

		ret = dialog.IsOK( )

		#answer is yes
		if ret == E_DIALOG_STATE_YES :
			isBackup = self.mDataCache.Channel_Backup( )
			isDelete = self.mDataCache.Channel_DeleteAll( )
			if isDelete :
				self.mFlag_DeleteAll = True
				LOG_TRACE( 'DeleteAll[%s]'% isDelete )

		return ret

		LOG_TRACE( 'Leave' )

	def SetModeChanged( self, aType = FLAG_MODE_TV) :
		LOG_TRACE( 'Enter' )

		if self.mChannelListServiceType == aType :
			if self.mChannelListServiceType == FLAG_MODE_TV:
				self.UpdateLabelGUI( self.mCtrlRdoTV.getId(), True, True )

			elif self.mChannelListServiceType == FLAG_MODE_RADIO:
				self.UpdateLabelGUI( self.mCtrlRdoRadio.getId(), True, True )

		else :
			self.mFlag_EditChanged = True
			self.mChannelListServiceType = aType
			self.mElisZappingModeInfo.mServiceType = aType

			self.InitSlideMenuHeader( FLAG_ZAPPING_CHANGE )
			self.mCtrlListMainmenu.selectItem( E_SLIDE_ALLCHANNEL )
			xbmc.sleep( 50 )
			self.SubMenuAction(E_SLIDE_ACTION_MAIN, E_SLIDE_ALLCHANNEL)
			self.mCtrlListSubmenu.selectItem( 0 )
			xbmc.sleep( 50 )
			self.SubMenuAction(E_SLIDE_ACTION_SUB, ElisEnum.E_MODE_ALL, True)

			self.mCtrlListCHList.reset( )
			self.InitChannelList( )
			self.mFlag_EditChanged = False

			#### data cache re-load ####
			self.mDataCache.LoadChannelList( FLAG_ZAPPING_CHANGE, aType, ElisEnum.E_MODE_ALL, ElisEnum.E_SORT_BY_NUMBER  )

			if aType == FLAG_MODE_TV :
				self.mCurrentChannel = None
				#self.SetChannelTune( self.mLastChannel )
				self.mDataCache.Player_AVBlank( False, False )

			elif aType == FLAG_MODE_RADIO :
				if self.mCurrentChannel :
					self.mLastChannel = self.mCurrentChannel
				self.mDataCache.Player_AVBlank( True, False )

			#initialize get epg event
			self.mIsSelect = False
			self.InitEPGEvent( )


		#slide close
		self.mCtrlListCHList.setEnabled(True)
		self.setFocusId( self.mCtrlGropCHList.getId( ) )


		LOG_TRACE( 'Leave' )

	def SetGoBackEdit( self ) :
		LOG_TRACE( 'Enter' )

		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			self.mViewMode = WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW

			try :
				#Event UnRegister
				#self.mEventBus.Deregister( self )
				self.InitSlideMenuHeader( )
				self.mCtrlListMainmenu.selectItem( E_SLIDE_ALLCHANNEL )
				xbmc.sleep( 50 )
				self.SubMenuAction(E_SLIDE_ACTION_MAIN, E_SLIDE_ALLCHANNEL)

				self.mCtrlListSubmenu.selectItem( 0 )
				xbmc.sleep( 50 )
				self.SubMenuAction(E_SLIDE_ACTION_SUB, ElisEnum.E_MODE_ALL)

				#clear label
				self.ResetLabel( )
				self.UpdateLabelInfo( )

				self.mCtrlListCHList.reset( )
				self.InitChannelList( )

				ret = self.mDataCache.Channel_Backup( )
				#LOG_TRACE( 'channelBackup[%s]'% ret )

				#slide close
				GuiLock2( True )
				self.mCtrlListCHList.setEnabled(True)
				self.setFocusId( self.mCtrlGropCHList.getId( ) )
				GuiLock2( False )

			except Exception, e :
				LOG_TRACE( 'Error except[%s]'% e )

		else :
			self.SetGoBackWindow( )

		LOG_TRACE( 'Leave' )

	def SetGoBackWindow( self ) :
		LOG_TRACE( 'Enter' )

		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			ret = False
			ret = self.SaveSlideMenuHeader( )
			if ret != E_DIALOG_STATE_CANCEL :
				self.mEnableThread = False
				self.CurrentTimeThread( ).join( )
				self.mCtrlListCHList.reset( )
				self.Close( )

			LOG_TRACE( 'go out Cancel' )

		else :
			ret = False
			ret = self.SaveEditList( )
			if ret != E_DIALOG_STATE_CANCEL :
				self.mViewMode = WinMgr.WIN_ID_CHANNEL_LIST_WINDOW
				self.mListItems = None
				self.mCtrlListCHList.reset( )
				self.InitSlideMenuHeader( FLAG_ZAPPING_CHANGE )
				self.InitChannelList( )

				#initialize get epg event
				self.mIsSelect = False
				self.InitEPGEvent( )

				#clear label
				self.ResetLabel( )
				self.UpdateLabelInfo( )
				self.mFlag_EditChanged = False

				#slide close
				GuiLock2( True )
				self.mCtrlListCHList.setEnabled(True)
				self.setFocusId( self.mCtrlGropCHList.getId( ) )
				GuiLock2( False )

		LOG_TRACE( 'Leave' )

	@GuiLock
	def onEvent(self, aEvent):
		#LOG_TRACE( 'Enter' )
		#aEvent.printdebug( )

		if self.mWinId == xbmcgui.getCurrentWindowId( ) :
			if aEvent.getName( ) == ElisEventCurrentEITReceived.getName( ) :

				if self.mNavChannel == None:
					return -1

				if self.mNavChannel.mSid != aEvent.mSid or self.mNavChannel.mTsid != aEvent.mTsid or self.mNavChannel.mOnid != aEvent.mOnid :
					return -1
		
				#LOG_TRACE('1========event id[%s] old[%s]'% (aEvent.mEventId, self.mEventId) )
				if aEvent.mEventId != self.mEventId :
					if self.mIsSelect == True :
						#on select, clicked
						ret = None
						ret = self.mDataCache.Epgevent_GetPresent( )
						if ret and ret.mEventName != 'No Name':
							#LOG_TRACE('2========event id[%s] old[%s]'% (aEvent.mEventId, self.mEventId) )
							self.mEventId = aEvent.mEventId

							if not self.mNavEpg or \
							   ret.mEventId != self.mNavEpg.mEventId or \
							   ret.mSid != self.mNavEpg.mSid or \
							   ret.mTsid != self.mNavEpg.mTsid or \
							   ret.mOnid != self.mNavEpg.mOnid :

								LOG_TRACE('epg DIFFER')
								self.mNavEpg = ret

								#update label
								self.ResetLabel( )
								self.UpdateLabelInfo( )

							else:
								LOG_TRACE('epg SAME')
		else:
			LOG_TRACE( 'channellist winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId( ) ) )

		#LOG_TRACE( 'Leave' )


	def SetChannelTune( self, aJumpNumber = None ) :
		LOG_TRACE( 'Enter' )

		#Turn in
		self.mIsSelect = True

		if aJumpNumber:
			#detected to jump focus
			chindex = 0;
			for ch in self.mChannelList:
				if ch.mNumber == aJumpNumber :
					self.mNavChannel = ch
					self.ResetLabel( )
					self.UpdateLabelInfo( )
					self.PincodeDialogLimit( )
					break
				chindex += 1

			if self.mChannelList == None:
				label = 'Empty Channels'#Msg.Strings( MsgId.LANG_NO_CHANNELS )
				self.UpdateLabelGUI( self.mCtrlChannelName.getId( ), label )
				LOG_TRACE( 'empty channel, iChannel[%s]'% self.mChannelList )
				return 

			GuiLock2( True )
			self.mCtrlListCHList.selectItem( chindex )
			xbmc.sleep( 50 )
			GuiLock2( False )

			#chNumber = aJumpNumber
			iChannel = ElisIChannel( )
			iChannel.reset()
			iChannel.mNumber = int(aJumpNumber)
			iChannel.mServiceType = deepcopy(self.mChannelListServiceType)

			LOG_TRACE('JumpChannel: num[%s] type[%s]'% (iChannel.mNumber, iChannel.mServiceType) )

		else:
			if self.mChannelList == None:
				label = 'Empty Channels'#Msg.Strings( MsgId.LANG_NO_CHANNELS )
				self.UpdateLabelGUI( self.mCtrlChannelName.getId( ), label )
				LOG_TRACE( 'empty channel, iChannel[%s]'% self.mChannelList )
				return 

			#label = self.mCtrlListCHList.getSelectedItem( ).getLabel( )
			#chNumber = ParseLabelToCh( self.mViewMode, label )
			#LOG_TRACE( 'label[%s] ch[%d] mask[%s] type[%s]'% (label, chNumber, self.mPincodeEnter, self.mChannelListServiceType) )

			idx = self.mCtrlListCHList.getSelectedPosition( )
			iChannel = self.mChannelList[idx]
			LOG_TRACE('chinfo: num[%s] type[%s] name[%s]'% (iChannel.mNumber, iChannel.mServiceType, iChannel.mName) )

		ret = False
		#ret = self.mDataCache.Channel_SetCurrent( chNumber, self.mChannelListServiceType )
		ret = self.mDataCache.Channel_SetCurrent( iChannel.mNumber, iChannel.mServiceType )

		#LOG_TRACE( 'MASK[%s] ret[%s]'% (self.mPincodeEnter, ret) )
		if ret == True :
			if self.mPincodeEnter == FLAG_MASK_NONE :
				if self.mCurrentChannel == iChannel.mNumber :
					ret = False
					ret = self.SaveSlideMenuHeader( )
					#LOG_TRACE('============== ret[%s]'% ret )
					if ret != E_DIALOG_STATE_CANCEL :
						self.mEnableThread = False
						self.CurrentTimeThread( ).join( )
						self.Close( )

						WinMgr.GetInstance( ).ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )
						return

					LOG_TRACE( 'go out Cancel' )

		ch = None
		ch = self.mDataCache.Channel_GetCurrent( )
		if ch :
			self.mNavChannel = ch
			self.mCurrentChannel = self.mNavChannel.mNumber
			pos = self.mCtrlListCHList.getSelectedPosition( )+1
			self.mCtrlSelectItem.setLabel( str('%s'% pos ) )
			LOG_TRACE('chinfo: num[%s] type[%s] name[%s] pos[%s]'% (ch.mNumber, ch.mServiceType, ch.mName, pos) )

			self.ResetLabel( )
			self.UpdateLabelInfo( )
			self.PincodeDialogLimit( )

		LOG_TRACE( 'Leave' )


	@GuiLock
	def SubMenuAction(self, aAction, aMenuIndex, aForce = None):
		LOG_TRACE( 'Enter' )

		if self.mFlag_DeleteAll :
			return

		retPass = False

		if aAction == E_SLIDE_ACTION_MAIN:
			testlistItems = []
			if aMenuIndex == 0 :
				self.mZappingMode = ElisEnum.E_MODE_ALL
				for itemList in range( len(self.mListAllChannel) ) :
					testlistItems.append( xbmcgui.ListItem(self.mListAllChannel[itemList]) )

			elif aMenuIndex == 1 :
				self.mZappingMode = ElisEnum.E_MODE_SATELLITE
				if self.mListSatellite :
					for itemClass in self.mListSatellite:
						ret = GetSelectedLongitudeString( itemClass.mLongitude, itemClass.mName )
						testlistItems.append( xbmcgui.ListItem(ret) )

			elif aMenuIndex == 2 :
				self.mZappingMode = ElisEnum.E_MODE_CAS
				if self.mListCasList :
					for itemClass in self.mListCasList:
						ret = '%s(%s)'% ( itemClass.mName, itemClass.mChannelCount )
						testlistItems.append( xbmcgui.ListItem(ret) )

			elif aMenuIndex == 3 :
				self.mZappingMode = ElisEnum.E_MODE_FAVORITE
				if self.mListFavorite :
					for itemClass in self.mListFavorite:
						testlistItems.append( xbmcgui.ListItem(itemClass.mGroupName) )
				else:
					testlistItems.append( xbmcgui.ListItem( Msg.Strings(MsgId.LANG_NONE) ) )

			if testlistItems != [] :
				#submenu update
				self.mCtrlListSubmenu.reset( )
				self.mCtrlListSubmenu.addItems( testlistItems )

				if aMenuIndex == self.mSelectMainSlidePosition :
					self.mCtrlListSubmenu.selectItem( self.mSelectSubSlidePosition )

		elif aAction == E_SLIDE_ACTION_SUB:
			if aForce == None and self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
				if self.mSelectMainSlidePosition == self.mCtrlListMainmenu.getSelectedPosition( ) and \
				   self.mSelectSubSlidePosition == self.mCtrlListSubmenu.getSelectedPosition( ) :
				   LOG_TRACE( 'aready select!!!' )
				   return

			zappingName = ''
			if aMenuIndex == ElisEnum.E_MODE_ALL :
				position   = self.mCtrlListSubmenu.getSelectedPosition( )
				if position == 0:
					sortingMode = ElisEnum.E_SORT_BY_NUMBER
				elif position == 1:
					sortingMode = ElisEnum.E_SORT_BY_ALPHABET
				elif position == 2:
					sortingMode = ElisEnum.E_SORT_BY_HD

				self.mChannelListSortMode = sortingMode
				retPass = self.GetChannelList( self.mChannelListServiceType, self.mZappingMode, sortingMode, 0, 0, 0, '' )

			elif aMenuIndex == ElisEnum.E_MODE_SATELLITE:
				if self.mListSatellite :
					idx_Satellite = self.mCtrlListSubmenu.getSelectedPosition( )
					item = self.mListSatellite[idx_Satellite]
					zappingName = item.mName
					retPass = self.GetChannelList( self.mChannelListServiceType, self.mZappingMode, self.mChannelListSortMode, item.mLongitude, item.mBand, 0, '' )
					#LOG_TRACE( 'cmd[channel_GetListBySatellite] idx_Satellite[%s] mLongitude[%s] band[%s]'% ( idx_Satellite, item.mLongitude, item.mBand ) )
				else:
					LOG_TRACE( 'cmd[channel_GetListBySatellite] mListSatellite[%s]'% self.mListSatellite )

			elif aMenuIndex == ElisEnum.E_MODE_CAS:
				if self.mListCasList :
					idxFtaCas = self.mCtrlListSubmenu.getSelectedPosition( )
					zappingName = self.mListCasList[idxFtaCas].mName
					if idxFtaCas == 0 :
						caid = ElisEnum.E_FTA_CHANNEL
					elif idxFtaCas == 1 :
						caid = ElisEnum.E_MEDIAGUARD
					elif idxFtaCas == 2 :
						caid = ElisEnum.E_VIACCESS
					elif idxFtaCas == 3 :
						caid = ElisEnum.E_NAGRA
					elif idxFtaCas == 4 :
						caid = ElisEnum.E_IRDETO
					elif idxFtaCas == 5 :
						caid = ElisEnum.E_CRYPTOWORKS
					elif idxFtaCas == 6 :
						caid = ElisEnum.E_BETADIGITAL
					elif idxFtaCas == 7 :
						caid = ElisEnum.E_NDS
					elif idxFtaCas == 8 :
						caid = ElisEnum.E_CONAX
					else :
						caid = ElisEnum.E_OTHERS

					retPass = self.GetChannelList( self.mChannelListServiceType, self.mZappingMode, self.mChannelListSortMode, 0, 0, caid, '' )
					#LOG_TRACE( 'cmd[channel_GetListByFTACas] idxFtaCas[%s]'% idxFtaCas )
				else:
					LOG_TRACE( 'cmd[channel_GetListByFTA/CAS] mListCasList[%s]'% self.mListCasList )

			elif aMenuIndex == ElisEnum.E_MODE_FAVORITE:
				if self.mListFavorite : 
					idx_Favorite = self.mCtrlListSubmenu.getSelectedPosition( )
					item = self.mListFavorite[idx_Favorite]
					zappingName = item.mGroupName
					retPass = self.GetChannelList( self.mChannelListServiceType, self.mZappingMode, self.mChannelListSortMode, 0, 0, 0, item.mGroupName )
					#LOG_TRACE( 'cmd[channel_GetListByFavorite] idx_Favorite[%s] list_Favorite[%s]'% ( idx_Favorite, item.mGroupName ) )
				else:
					LOG_TRACE( 'cmd[channel_GetListByFavorite] mListFavorite[%s]'% self.mListFavorite )

			if retPass == False :
				return

			if self.mMoveFlag :
				#do not refresh UI
				return
			
			#channel list update
			self.mMarkList = []
			self.mListItems = None
			self.mCtrlListCHList.reset( )
			self.InitChannelList( )

			#path tree, Mainmenu/Submanu
			self.mSelectMainSlidePosition = self.mCtrlListMainmenu.getSelectedPosition( )
			self.mSelectSubSlidePosition = self.mCtrlListSubmenu.getSelectedPosition( )

			label = ''
			label1 = EnumToString('mode', self.mZappingMode)
			label2 = zappingName
			label3 = EnumToString('sort', self.mChannelListSortMode)

			if self.mZappingMode == ElisEnum.E_MODE_ALL :
				label = '%s [COLOR grey3]>[/COLOR] sort by %s'% (label1.upper( ),label3.title( ) )
			else :
				label = '%s [COLOR grey3]>[/COLOR] %s [COLOR grey2]/ sort by %s[/COLOR]'% (label1.upper( ),label2.title( ),label3.title( ) )
			self.mCtrlLblPath1.setLabel( label )

			#current zapping backup
			#self.mDataCache.Channel_Backup( )

		LOG_TRACE( 'Leave' )


	def GetChannelList(self, aType, aMode, aSort, aLongitude, aBand, aCAid, aFavName ):
		LOG_TRACE( 'Enter' )

		try :
			if aMode == ElisEnum.E_MODE_ALL :
				self.mChannelList = self.mDataCache.Channel_GetList( FLAG_ZAPPING_CHANGE, aType, aMode, aSort )

			elif aMode == ElisEnum.E_MODE_SATELLITE :
				self.mChannelList = self.mDataCache.Channel_GetListBySatellite( aType, aMode, aSort, aLongitude, aBand )

			elif aMode == ElisEnum.E_MODE_CAS :
				self.mChannelList = self.mDataCache.Channel_GetListByFTACas( aType, aMode, aSort, aCAid )
				
			elif aMode == ElisEnum.E_MODE_FAVORITE :
				self.mChannelList = self.mDataCache.Channel_GetListByFavorite( aType, aMode, aSort, aFavName )

			elif aMode == ElisEnum.E_MODE_NETWORK :
				pass


		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )
			return False


		LOG_TRACE( 'Leave' )
		return True

	def GetSlideMenuHeader(self, aMode) :
		LOG_TRACE( 'Enter' )

		idx1 = 0
		idx2 = 0

		if aMode == FLAG_SLIDE_INIT :

			#self.mElisZappingModeInfo.printdebug( )
			#LOG_TRACE( 'satellite[%s]'% ClassToList( 'convert', self.mListSatellite ) )
			#LOG_TRACE( 'ftacas[%s]'   % ClassToList( 'convert', self.mListCasList ) )
			#LOG_TRACE( 'favorite[%s]' % ClassToList( 'convert', self.mListFavorite ) )

			zInfo_mode = self.mElisZappingModeInfo.mMode
			zInfo_sort = self.mElisZappingModeInfo.mSortingMode
			zInfo_type = self.mElisZappingModeInfo.mServiceType
			zInfo_name = ''

			if zInfo_mode == ElisEnum.E_MODE_ALL :
				idx1 = 0
				if zInfo_sort == ElisEnum.E_SORT_BY_NUMBER :
					idx2 = 0
				elif zInfo_sort == ElisEnum.E_SORT_BY_ALPHABET :
					idx2 = 1
				elif zInfo_sort == ElisEnum.E_SORT_BY_HD :
					idx2 = 2
				else :
					idx2 = 0

			elif zInfo_mode == ElisEnum.E_MODE_SATELLITE :
				idx1 = 1
				zInfo_name = self.mElisZappingModeInfo.mSatelliteInfo.mName

				for item in self.mListSatellite :
					if zInfo_name == item.mName :
						break
					idx2 += 1

			elif zInfo_mode == ElisEnum.E_MODE_CAS :
				idx1 = 2
				zInfo_name = self.mElisZappingModeInfo.mCasInfo.mName

				for item in self.mListCasList :
					if zInfo_name == item.mName :
						break
					idx2 += 1

			elif zInfo_mode == ElisEnum.E_MODE_FAVORITE :
				idx1 = 3
				zInfo_name = self.mElisZappingModeInfo.mFavoriteGroup.mGroupName
				if self.mListFavorite :
					for item in self.mListFavorite :
						if zInfo_name == item.mGroupName :
							break
						idx2 += 1

			self.mZappingName = zInfo_name
			self.mSelectMainSlidePosition = idx1
			self.mSelectSubSlidePosition = idx2

		elif aMode == FLAG_SLIDE_OPEN :
			idx1 = self.mSelectMainSlidePosition
			idx2 = self.mSelectSubSlidePosition


		self.mCtrlListMainmenu.selectItem( idx1 )
		self.SubMenuAction(E_SLIDE_ACTION_MAIN, idx1)
		self.mCtrlListSubmenu.selectItem( idx2 )
		#self.setFocusId( self.mCtrlListSubmenu.getId( ) )

		LOG_TRACE( 'Leave' )


	def SaveSlideMenuHeader( self ) :
		LOG_TRACE( 'Enter' )

		"""
		LOG_TRACE( 'mode[%s] sort[%s] type[%s] mpos[%s] spos[%s]'% ( \
			self.mZappingMode,                \
			self.mChannelListSortMode,        \
			self.mChannelListServiceType,      \
			self.mSelectMainSlidePosition,    \
			self.mSelectSubSlidePosition      \
		)
		self.mListSatellite[self.mSelectSubSlidePosition].printdebug( )
		self.mListCasList[self.mSelectSubSlidePosition].printdebug( )
		self.mListFavorite[self.mSelectSubSlidePosition].printdebug( )
		"""

		changed = False
		answer = E_DIALOG_STATE_NO


		if self.mSelectMainSlidePosition != self.mLastMainSlidePosition or \
		   self.mSelectSubSlidePosition != self.mLastSubSlidePosition :
			changed = True

		if self.mElisSetZappingModeInfo.mServiceType != self.mChannelListServiceType :
			changed = True

		if self.mFlag_DeleteAll :
			changed = True

		#is change?
		if changed :
			try :
				GuiLock2( True )
				#ask save question
				label1 = EnumToString( 'mode', self.mZappingMode )
				label2 = self.mCtrlListSubmenu.getSelectedItem( ).getLabel( )

				head =  Msg.Strings( MsgId.LANG_SETTING_TO_CHANGE_ZAPPING_MODE )
				line1 = '%s / %s'% ( label1.title( ), label2.title( ) )
				line2 = Msg.Strings( MsgId.LANG_DO_YOU_WANT_TO_SAVE_CHANNELS )

				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( head, str('%s\n\n%s'% (line1,line2) ) )
				dialog.doModal( )
				GuiLock2( False )

				answer = dialog.IsOK( )

				#answer is yes
				if answer == E_DIALOG_STATE_YES :
					#re-configuration class
					self.mElisSetZappingModeInfo.reset( )
					self.mElisSetZappingModeInfo.mMode = self.mZappingMode
					self.mElisSetZappingModeInfo.mSortingMode = self.mChannelListSortMode
					self.mElisSetZappingModeInfo.mServiceType = self.mChannelListServiceType

					if self.mSelectMainSlidePosition == 1 :
						groupInfo = self.mListSatellite[self.mSelectSubSlidePosition]
						self.mElisSetZappingModeInfo.mSatelliteInfo = groupInfo
						
					elif self.mSelectMainSlidePosition == 2 :
						groupInfo = self.mListCasList[self.mSelectSubSlidePosition]
						self.mElisSetZappingModeInfo.mCasInfo = groupInfo
					
					elif self.mSelectMainSlidePosition == 3 :
						groupInfo = self.mListFavorite[self.mSelectSubSlidePosition]
						self.mElisSetZappingModeInfo.mFavoriteGroup = groupInfo

					iZappingList = []
					iZappingList.append( self.mElisSetZappingModeInfo )
					"""
					LOG_TRACE( '1. zappingMode[%s] sortMode[%s] serviceType[%s]'%  \
						( EnumToString('mode', self.mZappingMode),         \
						  EnumToString('sort', self.mChannelListSortMode), \
						  EnumToString('type', self.mChannelListServiceType) ) )
					LOG_TRACE( '2. zappingMode[%s] sortMode[%s] serviceType[%s]'%  \
						( EnumToString('mode', self.mElisSetZappingModeInfo.mMode),         \
						  EnumToString('sort', self.mElisSetZappingModeInfo.mSortingMode), \
						  EnumToString('type', self.mElisSetZappingModeInfo.mServiceType) ) )
					"""

					#save zapping mode
					self.mDataCache.Channel_Save( )
					ret = self.mDataCache.Zappingmode_SetCurrent( iZappingList )
					LOG_TRACE( 'set zappingmode_SetCurrent[%s]'% ret )
					if ret :
						#### data cache re-load ####
						self.mDataCache.LoadZappingmode( )
						self.mDataCache.LoadZappingList( )
						self.mDataCache.LoadChannelList( )
						LOG_TRACE ('===================== save yes: cache re-load')

				elif answer == E_DIALOG_STATE_NO :
					#zapping changed then will re-paint list items for cache
					self.mListItems = None
					if self.mFlag_DeleteAll : 
						#restore backup zapping
						isRestore = self.mDataCache.Channel_Restore( True )
						LOG_TRACE( 'Restore[%s]'% isRestore )


					#self.mDataCache.Channel_SetCurrent( self.mCurrentChannel.mNumber, self.mCurrentChannel.mServiceType )
					#### data cache re-load ####
					self.mDataCache.LoadZappingmode( )
					self.mDataCache.LoadZappingList( )
					self.mDataCache.LoadChannelList( )
					LOG_TRACE ('===================== save no: cache re-load')

					iChannel = self.mDataCache.Channel_GetCurrent( )
					if iChannel.mNumber != self.mCurrentChannel or iChannel.mServiceType != self.mChannelListServiceType :
						self.mDataCache.Channel_SetCurrent( iChannel.mNumber, iChannel.mServiceType )
						LOG_TRACE('tune: ch[%s] type[%s] name[%s]'% (iChannel.mNumber, iChannel.mServiceType, iChannel.mName) )

					if iChannel.mServiceType == ElisEnum.E_SERVICE_TYPE_TV :
						self.mDataCache.Player_AVBlank( False, False )

					elif iChannel.mServiceType == ElisEnum.E_SERVICE_TYPE_RADIO :
						self.mDataCache.Player_AVBlank( True, False )
						

			except Exception, e :
				LOG_TRACE( 'Error exception[%s]'% e )

		#else:
			#channel sync
			#self.mDataCache.mCurrentChannel = self.mNavChannel

		return answer

		LOG_TRACE( 'Leave' )


	def SaveEditList( self ) :
		LOG_TRACE( 'Enter' )

		answer = E_DIALOG_STATE_NO

		#is change?
		if self.mIsSave :
			#ask save question
			head =  Msg.Strings( MsgId.LANG_CONFIRM )
			line1 = Msg.Strings( MsgId.LANG_DO_YOU_WANT_TO_SAVE_CHANNELS )

			GuiLock2( True )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( head, line1 )
			dialog.doModal( )
			GuiLock2( False )

			answer = dialog.IsOK( )

			#answer is yes
			if answer == E_DIALOG_STATE_YES :
				self.mIsSave = FLAG_MASK_NONE
				self.mFlag_EditChanged = True
				isSave = self.mDataCache.Channel_Save( )
				LOG_TRACE( 'save[%s]'% isSave )

				#### data cache re-load ####
				self.mDataCache.LoadZappingmode( )
				self.mDataCache.LoadZappingList( )
				self.mDataCache.LoadChannelList( )
				LOG_TRACE ('cache re-load')

			elif answer == E_DIALOG_STATE_NO :
				self.mIsSave = FLAG_MASK_NONE
				isSave = self.mDataCache.Channel_Restore( True )
				LOG_TRACE( 'Restore[%s]'% isSave )


		return answer

		LOG_TRACE( 'Leave' )

	def InitSlideMenuHeader( self, aZappingMode = FLAG_ZAPPING_LOAD ) :
		LOG_TRACE( 'Enter' )

		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			#opt btn blind
			self.UpdateLabelGUI( self.mCtrlGropOpt.getId( ), False )
			self.UpdateLabelGUI( self.mCtrlRdoTV.getId( ), True )
			self.UpdateLabelGUI( self.mCtrlRdoRadio.getId( ), True )
		else :
			#opt btn visible
			self.UpdateLabelGUI( self.mCtrlGropOpt.getId( ), True )
			self.UpdateLabelGUI( self.mCtrlRdoTV.getId( ), False )
			self.UpdateLabelGUI( self.mCtrlRdoRadio.getId( ), False )
			return

		if self.mFlag_DeleteAll :
			self.mZappingMode           = ElisEnum.E_MODE_ALL
			self.mChannelListSortMode   = ElisEnum.E_SORT_BY_DEFAULT
			self.mChannelListServiceType = ElisEnum.E_SERVICE_TYPE_TV

			self.mCtrlListSubmenu.reset( )
			testlistItems = []
			testlistItems.append(xbmcgui.ListItem( Msg.Strings(MsgId.LANG_NONE) ) )
			self.mCtrlListSubmenu.addItems( testlistItems )

			return

		#main/sub menu init
		GuiLock2( True )
		self.mCtrlListMainmenu.reset( )
		self.mCtrlListSubmenu.reset( )
		GuiLock2( False )

		#get last zapping mode
		if aZappingMode == FLAG_ZAPPING_LOAD :
			try:
				if self.mFlag_EditChanged :
					zappingMode = self.mDataCache.Zappingmode_GetCurrent( FLAG_ZAPPING_CHANGE )
				else :
					zappingMode = self.mDataCache.Zappingmode_GetCurrent( )

				if zappingMode :
					self.mZappingMode           = zappingMode.mMode
					self.mChannelListSortMode   = zappingMode.mSortingMode
					self.mChannelListServiceType = zappingMode.mServiceType
					self.mElisZappingModeInfo   = zappingMode
				else :
					#set default
					self.mZappingMode           = ElisEnum.E_MODE_ALL
					self.mChannelListSortMode   = ElisEnum.E_SORT_BY_DEFAULT
					self.mChannelListServiceType = ElisEnum.E_SERVICE_TYPE_TV
					zappingMode                 = ElisIZappingMode()
					self.mElisZappingModeInfo   = zappingMode
					LOG_TRACE( 'Fail GetCurrent!!! [set default ZappingMode]' )

			except Exception, e:
				#set default
				self.mZappingMode           = ElisEnum.E_MODE_ALL
				self.mChannelListSortMode   = ElisEnum.E_SORT_BY_DEFAULT
				self.mChannelListServiceType = ElisEnum.E_SERVICE_TYPE_TV
				zappingMode                 = ElisIZappingMode()
				self.mElisZappingModeInfo   = zappingMode
				LOG_TRACE( 'Error exception[%s] [set default ZappingMode]'% e )


		list_Mainmenu = []
		list_Mainmenu.append( Msg.Strings(MsgId.LANG_ALL_CHANNELS) )
		list_Mainmenu.append( Msg.Strings(MsgId.LANG_SATELLITE)    )
		list_Mainmenu.append( Msg.Strings(MsgId.LANG_FTA)          )
		list_Mainmenu.append( Msg.Strings(MsgId.LANG_FAVORITE)     )
		list_Mainmenu.append( 'MODE' )
		list_Mainmenu.append( Msg.Strings(MsgId.LANG_BACK)     )
		testlistItems = []
		for item in range( len(list_Mainmenu) ) :
			testlistItems.append( xbmcgui.ListItem(list_Mainmenu[item]) )

		self.mCtrlListMainmenu.addItems( testlistItems )

		#sort list, This is fixed
		self.mListAllChannel = []
		self.mListAllChannel.append( 'sort by Number' )
		self.mListAllChannel.append( 'sort by Alphabet' )
		self.mListAllChannel.append( 'sort by HD/SD' )
		#LOG_TRACE( 'mListAllChannel[%s]'% self.mListAllChannel )

		try :
			if self.mFlag_EditChanged :
				#satellite longitude list
				self.mListSatellite = self.mDataCache.Satellite_GetConfiguredList( )
				#ClassToList( 'print', self.mListSatellite )

				#FTA list
				self.mListCasList = self.mDataCache.Fta_cas_GetList( self.mChannelListServiceType )
				#ClassToList( 'print', self.mListCasList )

				#Favorite list
				self.mListFavorite = self.mDataCache.Favorite_GetList(FLAG_ZAPPING_CHANGE, self.mChannelListServiceType )
				#ClassToList( 'print', self.mListFavorite )
			else:
				self.mListSatellite = self.mDataCache.Satellite_GetConfiguredList( )
				self.mListCasList = self.mDataCache.Fta_cas_GetList( )
				self.mListFavorite = self.mDataCache.Favorite_GetList( )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


		testlistItems = []
		if self.mZappingMode == ElisEnum.E_MODE_ALL :
			for item in range(len(self.mListAllChannel) ) :
				testlistItems.append(xbmcgui.ListItem(self.mListAllChannel[item]) )

		elif self.mZappingMode == ElisEnum.E_MODE_SATELLITE :
			if self.mListSatellite :
				for item in self.mListSatellite:
					ret = GetSelectedLongitudeString( item.mLongitude, item.mName )
					testlistItems.append(xbmcgui.ListItem(ret) )

		elif self.mZappingMode == ElisEnum.E_MODE_CAS :
			if self.mListCasList :
				for item in self.mListCasList:
					ret = '%s(%s)'% ( item.mName, item.mChannelCount )
					testlistItems.append(xbmcgui.ListItem( ret ) )

		elif self.mZappingMode == ElisEnum.E_MODE_FAVORITE :
			if self.mListFavorite :
				for item in self.mListFavorite:
					testlistItems.append(xbmcgui.ListItem( item.mGroupName ) )

		self.mCtrlListSubmenu.addItems( testlistItems )


		self.GetSlideMenuHeader( FLAG_SLIDE_INIT )
		self.mLastMainSlidePosition = self.mSelectMainSlidePosition
		self.mLastSubSlidePosition = self.mSelectSubSlidePosition

		#path tree, Mainmenu/Submanu
		label = ''
		label1 = EnumToString('mode', self.mZappingMode)
		label2 = self.mZappingName
		label3 = EnumToString('sort', self.mChannelListSortMode)
		if self.mZappingMode == ElisEnum.E_MODE_ALL :
			label = '%s [COLOR grey3]>[/COLOR] sort by %s'% ( label1.upper( ),label3.title( ) )
		else :
			label = '%s [COLOR grey3]>[/COLOR] %s [COLOR grey2]/ sort by %s[/COLOR]'% ( label1.upper( ),label2.title( ),label3.title( ) )
		self.UpdateLabelGUI( self.mCtrlLblPath1.getId( ), label )

		#get channel list by last on zapping mode, sorting, service type
		self.mNavChannel = None
		self.mChannelList = None

		if self.mFlag_EditChanged :
			self.mChannelList = self.mDataCache.Channel_GetList( self.mFlag_EditChanged, self.mChannelListServiceType, self.mZappingMode, self.mChannelListSortMode )
		else :
			#### first get is used cache, reason by fast load ###
			self.mChannelList = self.mDataCache.Channel_GetList( )


		"""
		if self.mChannelList :
			LOG_TRACE( 'zappingMode[%s] sortMode[%s] serviceType[%s]'%  \
				( EnumToString('mode', self.mZappingMode),         \
				  EnumToString('sort', self.mChannelListSortMode), \
				  EnumToString('type', self.mChannelListServiceType) ) )
			LOG_TRACE( 'len[%s] ch%s'% (len(self.mChannelList),ClassToList( 'convert', self.mChannelList ) ) )
		"""

		LOG_TRACE( 'Leave' )


	def InitChannelList(self):
		LOG_TRACE( 'Enter' )

		#starttime = time.time( )
		#print '==================== TEST TIME[LIST] START[%s]'% starttime

		#no channel is set Label comment
		if self.mChannelList == None:
			label = 'Empty Channels'#Msg.Strings( MsgId.LANG_NO_CHANNELS )
			self.UpdateLabelGUI( self.mCtrlChannelName.getId( ), label )

			LOG_TRACE( 'empty channel, iChannel[%s]'% self.mChannelList )
			return 

		lblColorS = E_TAG_COLOR_GREY
		lblColorE = E_TAG_COLOR_END
		#LOG_TRACE('listItems data[%s]'% (self.mListItems) )
		if self.mListItems == None :
			self.mListItems = []
			for iChannel in self.mChannelList:
				try:
					if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
						#skip ch
						if iChannel.mSkipped == True :
							continue
						listItem = xbmcgui.ListItem( '%04d %s'%( iChannel.mNumber, iChannel.mName ) )

					else :
						#skip ch
						if iChannel.mSkipped == True :
							lblColorS = E_TAG_COLOR_GREY3
						else:
							lblColorS = E_TAG_COLOR_GREY

						listItem = xbmcgui.ListItem( '%s%04d %s%s'%( lblColorS, iChannel.mNumber, iChannel.mName, lblColorE ) )

				except Exception, e:
					LOG_TRACE( '=========== except[%s]'% e )


				if iChannel.mLocked  : listItem.setProperty('lock', E_IMG_ICON_LOCK)
				if iChannel.mIsCA    : listItem.setProperty('icas', E_IMG_ICON_ICAS)
				if self.mRecCount :
					if self.mRecChannel1 :
						if iChannel.mNumber == self.mRecChannel1[0] : listItem.setProperty('rec', E_IMG_ICON_REC)
					if self.mRecChannel2 :
						if iChannel.mNumber == self.mRecChannel2[0] : listItem.setProperty('rec', E_IMG_ICON_REC)

				self.mListItems.append(listItem)

		GuiLock2( True )
		self.mCtrlListCHList.addItems( self.mListItems )
		GuiLock2( False )


		#get last channel
		iChannel = None
		if self.mListItems == None :
			iChannel = self.mDataCache.Channel_GetCurrent( FLAG_ZAPPING_CHANGE )
		else :
			iChannel = self.mDataCache.Channel_GetCurrent( )

		if iChannel :
			self.mNavChannel = iChannel
			self.mCurrentChannel = self.mNavChannel.mNumber

		#detected to last focus
		iChannelIdx = 0;
		for iChannel in self.mChannelList:
			if iChannel.mNumber == self.mCurrentChannel :
				break
			iChannelIdx += 1

		GuiLock2( True )
		self.mCtrlListCHList.selectItem( iChannelIdx )
		xbmc.sleep( 50 )

		#select item idx, print GUI of 'current / total'
		self.mCtrlSelectItem.setLabel( str('%s'% (self.mCtrlListCHList.getSelectedPosition( )+1) ) )
		GuiLock2( False )

		#endtime = time.time( )
		#print '==================== TEST TIME[LIST] END[%s] loading[%s]'% (endtime, endtime-starttime )
		LOG_TRACE( 'Leave' )


	def ResetLabel(self):
		LOG_TRACE( 'Enter' )

		if self.mChannelListServiceType == ElisEnum.E_SERVICE_TYPE_TV:
			self.mCtrlRdoTV.setSelected( True )
			self.mCtrlRdoRadio.setSelected( False )
		elif self.mChannelListServiceType == ElisEnum.E_SERVICE_TYPE_RADIO:
			self.mCtrlRdoTV.setSelected( False )
			self.mCtrlRdoRadio.setSelected( True )

		self.mCtrlProgress.setPercent(0)
		self.mCtrlProgress.setVisible(False)
		self.mPincodeEnter = FLAG_MASK_NONE

		self.mCtrlSelectItem.setLabel( str('%s'% (self.mCtrlListCHList.getSelectedPosition( )+1) ) )
		self.mCtrlEventName.setLabel('')
		self.mCtrlEventTime.setLabel('')
		self.mCtrlLongitudeInfo.setLabel('')
		self.mCtrlCareerInfo.setLabel('')
		self.mCtrlLockedInfo.setVisible(False)
		self.mCtrlServiceTypeImg1.setImage('')
		self.mCtrlServiceTypeImg2.setImage('')
		self.mCtrlServiceTypeImg3.setImage('')

		LOG_TRACE( 'Leave' )


	def InitEPGEvent( self ) :
		LOG_TRACE( 'Enter' )

		try :
			if self.mIsSelect == True :
				iEPG = None
				iEPG = self.mDataCache.Epgevent_GetPresent( )
				if iEPG and iEPG.mEventName != 'No Name':
					self.mNavEpg = iEPG
					#iEPG.printdebug( )

			else :
				if self.mChannelList :
					idx = self.mCtrlListCHList.getSelectedPosition( )
					chNumber = self.mChannelList[idx].mNumber
					#LOG_TRACE( 'label[%s] ch[%d]'% (label, chNumber) )

					for iChannel in self.mChannelList:
						if iChannel.mNumber == chNumber :
							self.mNavChannel = None
							self.mNavChannel = iChannel
							#LOG_TRACE( 'found ch: getlabel[%s] ch[%s]'% (chNumber, ch.mNumber ) )

							sid  = iChannel.mSid
							tsid = iChannel.mTsid
							onid = iChannel.mOnid
							iEPGList = None
							iEPGList = self.mDataCache.Epgevent_GetCurrent( sid, tsid, onid, True )
							#LOG_TRACE('=============epg len[%s] list[%s]'% (len(iEPGList),ClassToList('convert', iEPGList ) ) )
							if iEPGList :
								self.mNavEpg = iEPGList
							else :
								self.mNavEpg = 0
							
		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		LOG_TRACE( 'Leave' )


	def UpdateServiceType( self, aTvType ):
		LOG_TRACE( 'Enter' )

		label = ''
		if aTvType == ElisEnum.E_SERVICE_TYPE_TV:
			label = 'TV'
		elif aTvType == ElisEnum.E_SERVICE_TYPE_RADIO:
			label = 'RADIO'
		elif aTvType == ElisEnum.E_SERVICE_TYPE_DATA:
			label = 'DATA'
		else:
			label = 'etc'
			LOG_TRACE( 'unknown ElisEnum tvType[%s]'% aTvType )

		LOG_TRACE( 'Leave' )
		return label

	@GuiLock
	def UpdateLabelGUI( self, aCtrlID = None, aValue = None, aExtra = None ) :
		LOG_TRACE( 'Enter control[%s] value[%s]'% (aCtrlID, aValue) )

		if aCtrlID == self.mCtrlChannelName.getId( ) :
			self.mCtrlChannelName.setLabel( aValue )

		elif aCtrlID == self.mCtrlLongitudeInfo.getId( ) :
			self.mCtrlLongitudeInfo.setLabel( aValue )

		elif aCtrlID == self.mCtrlCareerInfo.getId( ) :
			self.mCtrlCareerInfo.setLabel( aValue )

		elif aCtrlID == self.mCtrlEventName.getId( ) :
			self.mCtrlEventName.setLabel( aValue )

		elif aCtrlID == self.mCtrlEventTime.getId( ) :
			self.mCtrlEventTime.setLabel( aValue )

		elif aCtrlID == self.mCtrlLockedInfo.getId( ) :
			self.mCtrlLockedInfo.setVisible( aValue )

		elif aCtrlID == self.mCtrlServiceTypeImg1.getId( ) :
			self.mCtrlServiceTypeImg1.setImage( aValue )

		elif aCtrlID == self.mCtrlServiceTypeImg2.getId( ) :
			self.mCtrlServiceTypeImg2.setImage( aValue )

		elif aCtrlID == self.mCtrlServiceTypeImg3.getId( ) :
			self.mCtrlServiceTypeImg3.setImage( aValue )

		elif aCtrlID == self.mCtrlGropOpt.getId( ) :
			self.mCtrlGropOpt.setVisible( aValue )

		elif aCtrlID == self.mCtrlLblPath1.getId( ) :
			self.mCtrlLblPath1.setLabel( aValue )

		elif aCtrlID == self.mCtrlRdoTV.getId( ) :
			if aExtra :
				self.mCtrlRdoTV.setSelected( aValue )
			else :
				self.mCtrlRdoTV.setEnabled( aValue )

		elif aCtrlID == self.mCtrlRdoRadio.getId( ) :
			if aExtra :
				self.mCtrlRdoRadio.setSelected( aValue )
			else :
				self.mCtrlRdoRadio.setEnabled( aValue )

		elif aCtrlID == self.mCtrlBtnEdit.getId( ) :
			self.mCtrlBtnEdit.setEnabled( aValue )

		"""
		elif aCtrlID == self.mCtrlLblRec1.getId( ) :
			self.mCtrlLblRec1.setLabel( aValue )

		elif aCtrlID == self.mCtrlImgRec1.getId( ) :
			self.mCtrlImgRec1.setVisible( aValue )

		elif aCtrlID == self.mCtrlLblRec2.getId( ) :
			self.mCtrlLblRec2.setLabel( aValue )

		elif aCtrlID == self.mCtrlImgRec2.getId( ) :
			self.mCtrlImgRec2.setVisible( aValue )
		"""


		LOG_TRACE( 'Leave' )

	
	def UpdateLabelInfo( self ):
		LOG_TRACE( 'Enter' )

		if self.mNavChannel :
			#update channel name
			if self.mIsSelect == True :
				strType = self.UpdateServiceType( self.mNavChannel.mServiceType )
				label = '%s - %s'% (strType, self.mNavChannel.mName)
				self.UpdateLabelGUI( self.mCtrlChannelName.getId( ), label )

			#update longitude info
			satellite = self.mDataCache.Satellite_GetByChannelNumber( self.mNavChannel.mNumber, -1, True )
			if not satellite :
				#LOG_TRACE('Fail GetByChannelNumber by Cache')
				satellite = self.mDataCache.Satellite_GetByChannelNumber( self.mNavChannel.mNumber, self.mNavChannel.mServiceType, -1, True )

			if satellite :
				label = GetSelectedLongitudeString( satellite.mLongitude, satellite.mName )
				self.UpdateLabelGUI( self.mCtrlLongitudeInfo.getId( ), label )
			else :
				self.UpdateLabelGUI( self.mCtrlLongitudeInfo.getId( ), '' )

			#update lock-icon visible
			if self.mNavChannel.mLocked :
					self.mPincodeEnter |= FLAG_MASK_ADD
					self.UpdateLabelGUI( self.mCtrlLockedInfo.getId( ), True )


			#update career info
			if self.mNavChannel.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBS:
				value1 = self.mNavChannel.mCarrier.mDVBS.mPolarization
				value2 = self.mNavChannel.mCarrier.mDVBS.mFrequency
				value3 = self.mNavChannel.mCarrier.mDVBS.mSymbolRate

				polarization = EnumToString( 'Polarization', value1 )
				careerLabel = '%s MHz, %s KS/S, %s'% (value2, value3, polarization)
				self.UpdateLabelGUI( self.mCtrlCareerInfo.getId( ), careerLabel )

			elif self.mNavChannel.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBT:
				pass
			elif self.mNavChannel.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBC:
				pass
			elif self.mNavChannel.mCarrierType == ElisEnum.E_CARRIER_TYPE_INVALID:
				pass
				
			"""
			#is cas?
			if self.mNavChannel.mIsCA == True:
				#scrambled
				self.mPincodeEnter |= FLAG_MASK_ADD
			"""


		#update epgName uiID(304)
		if self.mNavEpg :
			try :
				epgTime = EpgInfoTime( self.mLocalOffset, self.mNavEpg.mStartTime, self.mNavEpg.mDuration )
				label = '%s - %s'% (epgTime[0], epgTime[1])
				self.UpdateLabelGUI( self.mCtrlEventName.getId( ), self.mNavEpg.mEventName )
				self.UpdateLabelGUI( self.mCtrlEventTime.getId( ), label )
				self.mCtrlProgress.setVisible( True )

				#component
				imagelist = EpgInfoComponentImage( self.mNavEpg )				
				if len(imagelist) == 1:
					self.UpdateLabelGUI( self.mCtrlServiceTypeImg1.getId( ), imagelist[0] )
				elif len(imagelist) == 2:
					self.UpdateLabelGUI( self.mCtrlServiceTypeImg1.getId( ), imagelist[0] )
					self.UpdateLabelGUI( self.mCtrlServiceTypeImg2.getId( ), imagelist[1] )

				elif len(imagelist) == 3:
					self.UpdateLabelGUI( self.mCtrlServiceTypeImg1.getId( ), imagelist[0] )
					self.UpdateLabelGUI( self.mCtrlServiceTypeImg2.getId( ), imagelist[1] )
					self.UpdateLabelGUI( self.mCtrlServiceTypeImg3.getId( ), imagelist[2] )
				else:
					self.UpdateLabelGUI( self.mCtrlServiceTypeImg1.getId( ), '' )
					self.UpdateLabelGUI( self.mCtrlServiceTypeImg2.getId( ), '' )
					self.UpdateLabelGUI( self.mCtrlServiceTypeImg3.getId( ), '' )


				#is Age? agerating check
				isLimit = AgeLimit( self.mPropertyAge, self.mNavEpg.mAgeRating )
				if isLimit == True :
					self.mPincodeEnter |= FLAG_MASK_ADD
					LOG_TRACE( 'AgeLimit[%s]'% isLimit )

			except Exception, e:
				LOG_TRACE( 'Error exception[%s]'% e )


		else:
			LOG_TRACE( 'event null' )


		LOG_TRACE( 'Leave' )


	def PincodeDialogLimit( self ) :
		LOG_TRACE( 'Enter' )

		#popup pin-code dialog
		if self.mPincodeEnter > FLAG_MASK_NONE :
			try :
				msg = Msg.Strings(MsgId.LANG_INPUT_PIN_CODE)

				inputPin = ''
				self.mDataCache.Player_AVBlank( True, False )
				#self.mDataCache.Channel_SetInitialBlank( True )
				GuiLock2( True )
				dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
				dialog.SetDialogProperty( msg, '', 4, True )
	 			dialog.doModal( )
				GuiLock2( False )

	 			if dialog.IsOK( ) == E_DIALOG_STATE_YES :
	 				inputPin = dialog.GetString( )
				
				if inputPin == None or inputPin == '' :
					inputPin = ''
				LOG_TRACE( 'ch[%d] mask[%s] inputPin[%s] stbPin[%s]'% (self.mCurrentChannel, self.mPincodeEnter, inputPin, self.mPropertyPincode) )

				if inputPin == str('%s'% self.mPropertyPincode) :
					self.mPincodeEnter = FLAG_MASK_NONE
					WinMgr.GetInstance( ).GetWindow( WinMgr.WIN_ID_LIVE_PLATE ).SetLastChannelCertificationPinCode( True )

					ret = None
					ret = self.mDataCache.Channel_SetCurrent( self.mCurrentChannel, self.mChannelListServiceType)
					self.mDataCache.Player_AVBlank( False, False )
					LOG_TRACE( 'Pincode success' )

				else:
					msg1 = Msg.Strings(MsgId.LANG_ERROR)
					msg2 = Msg.Strings(MsgId.LANG_WRONG_PIN_CODE)
					GuiLock2( True )
					xbmcgui.Dialog( ).ok( msg1, msg2 )
					GuiLock2( False )

			except Exception, e:
				LOG_TRACE( 'Error exception[%s]'% e )


		LOG_TRACE( 'Leave' )


	@RunThread
	def CurrentTimeThread(self):
		LOG_TRACE( 'begin_start thread' )

		loop = 0
		while self.mEnableThread:
			#LOG_TRACE( 'repeat <<<<' )
			if  ( loop % 10 ) == 0 :
				self.UpdateLocalTime( )

			time.sleep(1)
			loop += 1

		LOG_TRACE( 'leave_end thread' )


	@GuiLock
	def UpdateLocalTime( self ) :
		#LOG_TRACE( 'Enter' )
		
		try:
			self.mLocalTime = self.mDataCache.Datetime_GetLocalTime( )

			if self.mNavEpg :
				startTime = self.mNavEpg.mStartTime + self.mLocalOffset
				endTime   = startTime + self.mNavEpg.mDuration
				pastDuration = endTime - self.mLocalTime

				if self.mLocalTime > endTime: #Already past
					self.mCtrlProgress.setPercent( 100 )
					return

				elif self.mLocalTime < startTime :
					self.mCtrlProgress.setPercent( 0 )
					return

				if pastDuration < 0 :
					pastDuration = 0

				if self.mNavEpg.mDuration > 0 :
					percent = 100 - (pastDuration * 100.0/self.mNavEpg.mDuration )
				else :
					percent = 0

				#LOG_TRACE( 'percent=%d'% percent )
				self.mCtrlProgress.setPercent( percent )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )
			#self.mLocalTime = 0

		#LOG_TRACE( 'Leave' )


	@GuiLock
	def SetEditChannelList( self, aCmd, aEnabled = True, aGroupName = '' ) :
		LOG_TRACE( 'Enter' )

		lastPos = self.mCtrlListCHList.getSelectedPosition( )

		try:
			#----------------> 1.set current position item <-------------
			if len(self.mMarkList) < 1 :
				#icon toggle
				if aCmd.lower( ) == 'lock' :
					listItem = self.mCtrlListCHList.getListItem(lastPos)

					if aEnabled :
						#enable lock
						listItem.setProperty('lock', E_IMG_ICON_LOCK)
						cmd = 'Lock'
					else :
						#disible lock
						listItem.setProperty('lock', '')
						cmd = 'UnLock'

					#mark remove
					listItem.setProperty('mark', '')

					retList = []
					retList.append( self.mChannelList[lastPos] )
					ret = self.mDataCache.Channel_Lock( aEnabled, retList )

				#label color
				elif aCmd.lower( ) == 'skip' :
					#remove tag [COLOR ...]label[/COLOR]
					label1 = self.mCtrlListCHList.getSelectedItem( ).getLabel( )
					label2 = re.findall('\](.*)\[', label1)
					cmd = ''

					if aEnabled :
						label3= str('%s%s%s'%( E_TAG_COLOR_GREY3, label2[0], E_TAG_COLOR_END ) )
						cmd = 'Skip'
					else :
						label3= str('%s%s%s'%( E_TAG_COLOR_GREY, label2[0], E_TAG_COLOR_END ) )
						cmd = 'UnSkip'
					self.mCtrlListCHList.getSelectedItem( ).setLabel(label3)

					retList = []
					retList.append( self.mChannelList[lastPos] )
					ret = self.mDataCache.Channel_Skip( aEnabled, retList )

				elif aCmd.lower( ) == 'add' :
					#strip tag [COLOR ...]label[/COLOR]
					number = self.mChannelList[lastPos].mNumber
					cmd = 'AddChannel to Group'
					if aGroupName :
						ret = self.mDataCache.Favoritegroup_AddChannel( aGroupName, number, self.mChannelListServiceType )
					else :
						ret = 'group None'

				elif aCmd.lower( ) == 'del' :
					#strip tag [COLOR ...]label[/COLOR]
					number = self.mChannelList[lastPos].mNumber
					cmd = 'RemoveChannel to Group'
					if aGroupName :
						ret = self.mDataCache.Favoritegroup_RemoveChannel( aGroupName, number, self.mChannelListServiceType )
					else :
						ret = 'group None'

				elif aCmd.lower( ) == 'delete' :
					cmd = aCmd.title( )
					retList = []
					retList.append( self.mChannelList[lastPos] )
					ret = self.mDataCache.Channel_Delete( retList )


				#LOG_TRACE( 'set[%s] idx[%s] ret[%s]'% (cmd,lastPos,ret) )

			else :
				#----------------> 2.set mark list all <-------------
				for idx in self.mMarkList :
				
					self.mCtrlListCHList.selectItem(idx)
					xbmc.sleep( 50 )

					listItem = self.mCtrlListCHList.getListItem(idx)
					cmd = ''
					ret = ''
					#icon toggle
					if aCmd.lower( ) == 'lock' :

						#lock toggle: disable
						if aEnabled :
							listItem.setProperty('lock', E_IMG_ICON_LOCK)
							cmd = 'Lock'
						else :
							listItem.setProperty('lock', '')
							cmd = 'UnLock'

						retList = []
						retList.append( self.mChannelList[idx] )
						ret = self.mDataCache.Channel_Lock( aEnabled, retList )


					#label color
					elif aCmd.lower( ) == 'skip' :
						#strip tag [COLOR ...]label[/COLOR]
						label1 = self.mCtrlListCHList.getSelectedItem( ).getLabel( )
						label2 = re.findall('\](.*)\[', label1)
						if aEnabled :
							label3= str('%s%s%s'%( E_TAG_COLOR_GREY3, label2[0], E_TAG_COLOR_END ) )
							cmd = 'Skip'
						else :
							label3= str('%s%s%s'%( E_TAG_COLOR_GREY, label2[0], E_TAG_COLOR_END ) )
							cmd = 'UnSkip'
						self.mCtrlListCHList.getSelectedItem( ).setLabel(label3)
						#LOG_TRACE( 'idx[%s] 1%s 2%s 3%s'% (idx, label1,label2,label3) )

						retList = []
						retList.append( self.mChannelList[idx] )
						ret = self.mDataCache.Channel_Skip( aEnabled, retList )

					elif aCmd.lower( ) == 'add' :
						number = self.mChannelList[idx].mNumber
						cmd = 'AddChannel to Group'
						if aGroupName :
							ret = self.mDataCache.Favoritegroup_AddChannel( aGroupName, number, self.mChannelListServiceType )
						else :
							ret = 'group None'

					elif aCmd.lower( ) == 'del' :
						number = self.mChannelList[idx].mNumber
						LOG_TRACE('delete by Fav grp[%s] ch[%s]'% (aGroupName, number) )
						cmd = 'RemoveChannel to Group'
						if aGroupName :
							ret = self.mDataCache.Favoritegroup_RemoveChannel( aGroupName, number, self.mChannelListServiceType )
						else :
							ret = 'group None'

					elif aCmd.lower( ) == 'move' :
						cmd = 'Move'
						idxM= idx + aEnabled
						if idxM < 0 : continue

						#exchange name
						labelM = self.mCtrlListCHList.getSelectedItem( ).getLabel( )
						name = self.mChannelList[idxM].mName
						number=self.mChannelList[idxM].mNumber
						label = str('%s%s %s%s'%( E_TAG_COLOR_GREY, number, name, E_TAG_COLOR_END ) )
						self.mCtrlListCHList.getSelectedItem( ).setLabel(label)

						self.mCtrlListCHList.selectItem(idxM)
						xbmc.sleep( 50 )
						self.mCtrlListCHList.getSelectedItem( ).setLabel(labelM)
						continue
					
					LOG_TRACE( 'set[%s] idx[%s] ret[%s]'% (cmd,idx,ret) )

					#mark remove
					listItem.setProperty('mark', '')

				#recovery last focus
				self.mCtrlListCHList.selectItem(lastPos)


		except Exception, e:
			LOG_TRACE( 'Error except[%s]'% e )

		LOG_TRACE( 'Leave' )

	def SetEditChanneltoMove(self, aMode, aMove = None, aGroupName = None ) :
		LOG_TRACE( 'Enter' )

		if aMode == FLAG_OPT_MOVE :
		
			number = 0
			retList = []
			markList= []

			if not self.mMarkList :
				lastPos = self.mCtrlListCHList.getSelectedPosition( )
				self.mMarkList.append( lastPos )
				#LOG_TRACE('last position[%s]'% lastPos )
			
			self.mMarkList.sort( )

			chidx = int(self.mMarkList[0])
			number = self.mChannelList[chidx].mNumber

			LOG_TRACE('1====mark[%s] ch[%s]'% (self.mMarkList, ClassToList('convert',self.mChannelList) ) )

			#2. make listing of ichannel in marked idx
			for idx in self.mMarkList :
				i = int(idx)
				retList.append( self.mChannelList[i] )

			#3. update mark list (sorted)
			for i in range(len(self.mMarkList) ) :
				markList.append( int(self.mMarkList[0])+i )
			LOG_TRACE('mark: new[%s] old[%s]'% (markList, self.mMarkList) )

			#4. init channel list
			ret = False
			if self.mZappingMode == ElisEnum.E_MODE_FAVORITE :
				if aGroupName :
					ret = self.mDataCache.FavoriteGroup_MoveChannels( aGroupName, chidx, self.mChannelListServiceType, retList )
					#LOG_TRACE( '==========group========' )
			else :
				ret = self.mDataCache.Channel_Move( self.mChannelListServiceType, number, retList )

			if ret :
				self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )

			self.mMarkList = []
			self.mMarkList = deepcopy(markList)

			LOG_TRACE('2====mark[%s] ch[%s]'% (self.mMarkList, ClassToList('convert',self.mChannelList) ) )
			self.mMoveFlag = True

			GuiLock2( True )
			for idx in self.mMarkList :
				i = int(idx)
				listItem = self.mCtrlListCHList.getListItem( i )
				listItem.setProperty('mark', E_IMG_ICON_MARK)

			self.mCtrlListCHList.selectItem(self.mMarkList[0])
			self.setFocusId( self.mCtrlGropCHList.getId( ) )

			self.mCtrlLblOpt1.setLabel('[B]OK[/B]')
			self.mCtrlLblOpt2.setLabel('[B]OK[/B]')
			GuiLock2( False )

			#LOG_TRACE ('========= move Init ===' )

		elif aMode == FLAG_OPT_MOVE_OK :
			self.mMoveFlag = False
			self.mCtrlLblOpt1.setLabel('[B]Opt Edit[/B]')
			self.mCtrlLblOpt2.setLabel('[B]Opt Edit[/B]')

			self.mMarkList = []
			self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )

			#LOG_TRACE ('========= move End ===' )

		elif aMode == FLAG_OPT_MOVE_UPDOWN :
			updown= 0
			loopS = 0
			loopE = 0
			retList = []
			markList= []
			lastmark = len(self.mMarkList) - 1
			oldmark = 0

			#1. get number
			if aMove == Action.ACTION_MOVE_UP :	
				updown = -1
				chidx = self.mMarkList[0] + updown
				loopS = chidx
				loopE = self.mMarkList[lastmark]
				oldmark = loopE

			elif aMove == Action.ACTION_MOVE_DOWN :	
				updown = 1
				chidx = self.mMarkList[0] + updown
				loopS = self.mMarkList[0]
				loopE = self.mMarkList[lastmark] + updown
				oldmark = loopS

			elif aMove == Action.ACTION_PAGE_UP :	
				updown = -13
				chidx = self.mMarkList[0] + updown
				loopS = chidx
				loopE = self.mMarkList[lastmark] + updown
				oldmark = self.mMarkList[0]

			elif aMove == Action.ACTION_PAGE_DOWN :	
				updown = 13
				chidx = self.mMarkList[0] + updown
				loopS = self.mMarkList[0] + updown
				loopE = self.mMarkList[lastmark] + updown
				oldmark = self.mMarkList[0]


			if chidx < 0 or chidx > ( (len(self.mListItems)-1) - len(self.mMarkList) ) :
				#LOG_TRACE('list limit, do not PAGE MOVE!! idx[%s]'% chidx)
				return
			number = self.mChannelList[chidx].mNumber

			if loopS < 0 : loopS = 0
			elif loopE > (len(self.mListItems) )-1 : loopE = len(self.mListItems)-1
			#LOG_TRACE('1====mark[%s] ch[%s]'% (self.mMarkList, ClassToList('convert',self.mChannelList) ) )

			#2. get retList
			for idx in self.mMarkList :
				i = int(idx)
				retList.append( self.mChannelList[i] )

			#3. update mark list
			if (int(self.mMarkList[0]) + updown) > (len(self.mListItems) )-1 :
				#LOG_TRACE('list limit, do not PAGE MOVE!! idx[%s]'% (int(self.mMarkList[0]) + updown) )
				return
			for idx in self.mMarkList :
				idxNew = int(idx) + updown
				markList.append( idxNew )
			self.mMarkList = []
			self.mMarkList = markList

			#4. init channel list
			answer = False
			if self.mZappingMode == ElisEnum.E_MODE_FAVORITE :
				if aGroupName :
					answer = self.mDataCache.FavoriteGroup_MoveChannels( aGroupName, chidx, self.mChannelListServiceType, retList )
					#LOG_TRACE( '==========group========' )
			else :
				answer = self.mDataCache.Channel_Move( self.mChannelListServiceType, number, retList )

			if answer :
				self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )
			#LOG_TRACE('2====mark[%s] ch[%s]'% (self.mMarkList, ClassToList('convert',self.mChannelList) ) )
			#LOG_TRACE('loopS[%s] loopE[%s]'% (loopS, loopE) )

			#5. refresh section, label move
			for i in range(loopS, loopE+1) :

				number = self.mChannelList[i].mNumber
				name = self.mChannelList[i].mName
				icas = self.mChannelList[i].mIsCA
				lock = self.mChannelList[i].mLocked

				GuiLock2( True )
				listItem = self.mCtrlListCHList.getListItem( i )
				xbmc.sleep( 50 )

				listItem.setProperty( 'lock', '' )
				listItem.setProperty( 'icas', '' )

				label = str('%s%04d %s%s'%( E_TAG_COLOR_GREY, number, name, E_TAG_COLOR_END ) )
				listItem.setLabel(label)

				if lock : listItem.setProperty( 'lock', E_IMG_ICON_LOCK )
				if icas : listItem.setProperty( 'icas', E_IMG_ICON_ICAS )
				listItem.setProperty( 'mark', E_IMG_ICON_MARK )
				xbmc.sleep( 50 )
				GuiLock2( False )

			#6. erase old mark
			GuiLock2( True )
			if aMove == Action.ACTION_MOVE_UP or aMove == Action.ACTION_MOVE_DOWN :
				listItem = self.mCtrlListCHList.getListItem(oldmark)
				xbmc.sleep( 50 )
				listItem.setProperty( 'mark', '' )
				self.setFocusId( self.mCtrlGropCHList.getId( ) )

			else:
				for idx in range(len(self.mMarkList) ) :
					idxOld = oldmark + idx
					if idxOld > (len(self.mListItems) )-1 : 
						LOG_TRACE('old idx[%s] i[%s]'% (oldmark, idx) )
						continue
					listItem = self.mCtrlListCHList.getListItem( idxOld )
					listItem.setProperty( 'mark', '' )
					self.setFocusId( self.mCtrlGropCHList.getId( ) )
					xbmc.sleep( 50 )
			GuiLock2( False )

		LOG_TRACE( 'Leave' )

	def SetEditMarkupGUI( self, aMode, aPos, aEnabled=True ) :
		LOG_TRACE( 'Enter' )

		if aMode.lower( ) == 'mark' :
			idx = 0
			isExist = False

			#aready mark is mark delete
			for i in self.mMarkList :
				if i == aPos :
					self.mMarkList.pop(idx)
					isExist = True
				idx += 1

			#do not exist is append mark
			if isExist == False : 
				self.mMarkList.append( aPos )

			listItem = self.mCtrlListCHList.getListItem(aPos)

			#mark toggle: disable
			if listItem.getProperty('mark') == E_IMG_ICON_MARK :
				listItem.setProperty('mark', '')

			#mark toggle: enable
			else :
				listItem.setProperty('mark', E_IMG_ICON_MARK)


		elif aMode.lower( ) == 'delete' :
			idx = 0
			isExist = False

			#aready exist check, do not append
			for i in self.mDeleteList :
				if i == aPos :
					isExist = True
					break
				idx += 1

			if aEnabled :
				#delete, append item when not exist
				if isExist == False : 
					self.mDeleteList.append( aPos )
			else :
				#undelete, remove item
				if isExist == True :
					self.mDeleteList.pop(idx)

		LOG_TRACE( 'Leave' )


	def GetFavoriteGroup( self ) :
		LOG_TRACE( 'Enter' )

		self.mListFavorite = self.mDataCache.Favorite_GetList( FLAG_ZAPPING_CHANGE, self.mChannelListServiceType )
		if self.mListFavorite :
			LOG_TRACE('reload FavGroup[%s]'% ClassToList( 'convert', self.mListFavorite ) )
		else :
			LOG_TRACE('reload FavGroup[None]')
		

		self.mEditFavorite = []
		if self.mListFavorite :
			for item in self.mListFavorite:
				#copy to favoriteGroup
				self.mEditFavorite.append( item.mGroupName )

		LOG_TRACE( 'Leave' )


	def DoContextAdtion( self, aMode, aContextAction, aGroupName = '' ) :
		LOG_TRACE( 'Enter' )

		if aContextAction == CONTEXT_ACTION_LOCK :
			cmd = 'lock'
			self.SetEditChannelList( cmd, True )

		elif aContextAction == CONTEXT_ACTION_UNLOCK :
			cmd = 'lock'
			self.SetEditChannelList( cmd, False)

		elif aContextAction == CONTEXT_ACTION_SKIP :
			cmd = 'skip'
			self.SetEditChannelList( cmd, True )

		elif aContextAction == CONTEXT_ACTION_UNSKIP :
			cmd = 'skip'
			self.SetEditChannelList( cmd, False )

		elif aContextAction == CONTEXT_ACTION_DELETE :
			if aMode == FLAG_OPT_LIST :
				cmd = 'delete'

				if self.mMarkList :
					try:
						retList = []
						for idx in self.mMarkList :
							#retList.append( self.mChannelList[idx] )
							chNum = ElisEInteger( )
							chNum.mParam = self.mChannelList[idx].mNumber
							retList.append( chNum )

						#ret = self.mDataCache.Channel_Delete( retList )
						ret = self.mDataCache.Channel_DeleteByNumber( int(self.mChannelListServiceType), retList )
						LOG_TRACE('ret[%s] len[%s] delete[%s]'% (ret, len(retList), ClassToList('convert', retList) ) )

					except Exception, e:
						LOG_TRACE( 'Error except[%s]'% e )
				else :
					self.SetEditChannelList( cmd, False )

				self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )
				self.mListItems = None

				self.mMarkList = []
				GuiLock2( True )
				self.setFocusId( self.mCtrlGropCHList.getId( ) )
				self.mCtrlSelectItem.setLabel( str('%s'% (self.mCtrlListCHList.getSelectedPosition( )+1) ) )
				GuiLock2( False )

				return

			else :
				cmd = 'del'
				#idxThisFavorite = self.mCtrlListSubmenu.getSelectedPosition( )
				#aGroupName = self.mListFavorite[idxThisFavorite].mGroupName
				aGroupName = self.mCtrlListSubmenu.getSelectedItem( ).getLabel( )

			self.SetEditChannelList( cmd, True, aGroupName )
			self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )

		elif aContextAction == CONTEXT_ACTION_MOVE :
			cmd = 'move'
			self.SetEditChanneltoMove(FLAG_OPT_MOVE, None, aGroupName )
			if self.mMarkList :
				idx = int(self.mMarkList[0])
				GuiLock2( True )
				#xbmc.executebuiltin('xbmc.Container.SetViewMode(50)')
				xbmc.executebuiltin('container.update')
				xbmc.sleep( 50 )
				self.mCtrlListCHList.selectItem(idx)
				self.setFocusId( self.mCtrlGropCHList.getId( ) )
				GuiLock2( False )
			return

		elif aContextAction == CONTEXT_ACTION_ADD_TO_FAV :
			cmd = 'add'
			self.SetEditChannelList( cmd, True, aGroupName )
			self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )

		elif aContextAction == CONTEXT_ACTION_CREATE_GROUP_FAV :
			cmd = 'Create'
			ret = self.mDataCache.Favoritegroup_Create( aGroupName, self.mChannelListServiceType )	#default : ElisEnum.E_SERVICE_TYPE_TV
			#LOG_TRACE( 'set[%s] name[%s] ret[%s]'% (cmd,aGroupName,ret) )				
			if ret :
				self.GetFavoriteGroup( )

		elif aContextAction == CONTEXT_ACTION_RENAME_FAV :
			cmd = 'Rename'
			name = re.split(':', aGroupName)
			ret = self.mDataCache.Favoritegroup_ChangeName( name[1], self.mChannelListServiceType, name[2] )
			if ret :
				self.GetFavoriteGroup( )

		elif aContextAction == CONTEXT_ACTION_DELETE_FAV :
			cmd = 'Remove'
			ret = self.mDataCache.Favoritegroup_Remove( aGroupName, self.mChannelListServiceType )
			if ret :
				self.GetFavoriteGroup( )


		self.mMarkList = []
		GuiLock2( True )
		self.setFocusId( self.mCtrlGropCHList.getId( ) )
		GuiLock2( False )

		LOG_TRACE( 'Leave' )


	def EditSettingWindowContext( self, aMode, aMove = None ) :
		LOG_TRACE( 'Enter' )

		#try:
		if self.mMoveFlag :
			self.SetEditChanneltoMove( FLAG_OPT_MOVE_OK )
			return

		self.GetFavoriteGroup( )

		#default context item
		context = []
		if self.mChannelList :
			context.append( ContextItem( Msg.Strings( MsgId.LANG_LOCK ),   CONTEXT_ACTION_LOCK ) )
			context.append( ContextItem( Msg.Strings( MsgId.LANG_UNLOCK ), CONTEXT_ACTION_UNLOCK ) )
			context.append( ContextItem( Msg.Strings( MsgId.LANG_SKIP ),   CONTEXT_ACTION_SKIP ) )
			context.append( ContextItem( Msg.Strings( MsgId.LANG_UNSKIP ), CONTEXT_ACTION_UNSKIP  ) )
			context.append( ContextItem( Msg.Strings( MsgId.LANG_DELETE ), CONTEXT_ACTION_DELETE ) )
			context.append( ContextItem( Msg.Strings( MsgId.LANG_MOVE ),   CONTEXT_ACTION_MOVE ) )


		if aMode == FLAG_OPT_LIST :

			if self.mChannelList :
				if self.mEditFavorite:
					lblItem = '%s'% Msg.Strings( MsgId.LANG_ADD_TO_FAV )
				else:
					label   = '%s\tNone'% Msg.Strings( MsgId.LANG_ADD_TO_FAV )
					lblItem = str('%s%s%s'%( E_TAG_COLOR_GREY3, label, E_TAG_COLOR_END ) )

				context.append( ContextItem( lblItem, CONTEXT_ACTION_ADD_TO_FAV  ) )

			else :
				head =  Msg.Strings( MsgId.LANG_INFOMATION )
				line1 = Msg.Strings( MsgId.LANG_NO_CHANNELS )

				xbmcgui.Dialog( ).ok(head, line1)
				return


		elif aMode == FLAG_OPT_GROUP :
			if not self.mChannelList :
				context = []

			context.append( ContextItem( Msg.Strings( MsgId.LANG_CREATE_NEW_GROUP ), CONTEXT_ACTION_CREATE_GROUP_FAV ) )

			if self.mEditFavorite:
				context.append( ContextItem( '%s'% Msg.Strings( MsgId.LANG_RENAME_FAV ), CONTEXT_ACTION_RENAME_FAV ) )
				context.append( ContextItem( '%s'% Msg.Strings( MsgId.LANG_DELETE_FAV ), CONTEXT_ACTION_DELETE_FAV ) )
				
				
			else:
				label1   = '%s\tNone'% Msg.Strings( MsgId.LANG_RENAME_FAV )
				label2   = '%s\tNone'% Msg.Strings( MsgId.LANG_DELETE_FAV )
				lblItem2 = str('%s%s%s'%( E_TAG_COLOR_GREY3, label1, E_TAG_COLOR_END ) )
				lblItem3 = str('%s%s%s'%( E_TAG_COLOR_GREY3, label2, E_TAG_COLOR_END ) )
				context.append( ContextItem( lblItem2 , CONTEXT_ACTION_RENAME_FAV ) )
				context.append( ContextItem( lblItem3, CONTEXT_ACTION_DELETE_FAV ) )


		GuiLock2( True )
		dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
		dialog.SetProperty( context )
 		dialog.doModal( )
 		GuiLock2( False )

		selectedAction = dialog.GetSelectedAction( )
		LOG_TRACE('selectedAction[%s]'% selectedAction )

		if selectedAction == -1 :
			LOG_TRACE('CANCEL by context dialog')
			return

		if (not self.mEditFavorite) and (selectedAction == CONTEXT_ACTION_ADD_TO_FAV) :
			#can not add to Fav : no favorite group
			LOG_TRACE('Disabled! Fav is empty, Can not add to Fav : selectedAction[%s]'% selectedAction)
			return

		if ((not self.mEditFavorite) and (selectedAction == CONTEXT_ACTION_RENAME_FAV) ) or \
		   ((not self.mEditFavorite) and (selectedAction == CONTEXT_ACTION_DELETE_FAV) ) :
			#can not rename / delete : no favorite group
			LOG_TRACE('Disabled Fav is empty, Can not Rename or Delete Fav : selectedAction[%s]'% selectedAction)
			return
		#--------------------------------------------------------------- section 1

		groupName = None

		# add Fav, Ren Fav, Del Fav ==> popup select group
		if selectedAction == CONTEXT_ACTION_ADD_TO_FAV or \
		   selectedAction == CONTEXT_ACTION_RENAME_FAV or \
		   selectedAction == CONTEXT_ACTION_DELETE_FAV :
		   	context = []
		   	idx = 0
   			for name in self.mEditFavorite:
				context.append( ContextItem( name, idx ) )
				idx += 1

			GuiLock2( True )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context )
 			dialog.doModal( )
 			GuiLock2( False )

 			grpIdx = dialog.GetSelectedAction( )
 			LOG_TRACE('---------------grpIdx[%s]'% grpIdx)
 			groupName = self.mEditFavorite[grpIdx]

			if grpIdx == -1 :
				LOG_TRACE('CANCEL by context dialog')
				return

		# Ren Fav, Del Fav ==> popup input group Name
		if selectedAction == CONTEXT_ACTION_CREATE_GROUP_FAV or \
		   selectedAction == CONTEXT_ACTION_RENAME_FAV :
			label = ''
			default = ''
			if selectedAction == CONTEXT_ACTION_CREATE_GROUP_FAV :
				#create
				result = ''
				label = Msg.Strings( MsgId.LANG_CREATE_NEW_GROUP )

			elif selectedAction == CONTEXT_ACTION_RENAME_FAV :
				#rename
				default = groupName
				result = '%d'%grpIdx + ':' + groupName + ':'
				label = Msg.Strings( MsgId.LANG_RENAME_FAV )

			kb = xbmc.Keyboard( default, label, False )
			kb.doModal( )

			name = ''
			name = kb.getText( )
			if name :
				groupName = result + name

		LOG_TRACE('mode[%s] btn[%s] groupName[%s]'% (aMode, selectedAction, groupName) )
		#--------------------------------------------------------------- section 2

		self.DoContextAdtion( aMode, selectedAction, groupName )

		self.mIsSave |= FLAG_MASK_ADD

		LOG_TRACE( 'Leave' )



	def PopupOpt( self ) :
		LOG_TRACE( 'Enter' )

		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW :
			mode = FLAG_OPT_LIST
			if self.mZappingMode == ElisEnum.E_MODE_FAVORITE :
				mode = FLAG_OPT_GROUP
			else :
				mode = FLAG_OPT_LIST

			self.EditSettingWindowContext( mode )

		LOG_TRACE( 'Leave' )


	def Close( self ):
		self.mEventBus.Deregister( self )
		self.StopAsyncEPG( )

		self.SetVideoRestore( )
		self.close( )

	def RestartAsyncEPG( self ) :
		self.StopAsyncEPG( )
		self.StartAsyncEPG( )


	def StartAsyncEPG( self ) :
		self.mAsyncTuneTimer = threading.Timer( 0.5, self.AsyncUpdateCurrentEPG ) 				
		self.mAsyncTuneTimer.start( )


	def StopAsyncEPG( self ) :
		if self.mAsyncTuneTimer	and self.mAsyncTuneTimer.isAlive( ) :
			self.mAsyncTuneTimer.cancel( )
			del self.mAsyncTuneTimer

		self.mAsyncTuneTimer  = None


	def AsyncUpdateCurrentEPG( self ) :
		try :
			self.mIsSelect = False
			self.InitEPGEvent( )
			self.ResetLabel( )
			self.UpdateLabelInfo( )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def KeySearch( self, aKey ) :
		LOG_TRACE( 'Enter' )

		if self.mChannelList == None:
			return -1

		if aKey == 0 :
			return -1

		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW:

			GuiLock2( True )
			dialog = DiaMgr.GetInstance( ).GetDialog( DiaMgr.DIALOG_ID_CHANNEL_JUMP )
			if self.mNavEpg:
				dialog.SetDialogProperty( str(aKey), E_INPUT_MAX, self.mChannelList, self.mNavEpg.mStartTime )
			else :
				dialog.SetDialogProperty( str(aKey), E_INPUT_MAX, self.mChannelList )
			dialog.doModal( )
			GuiLock2( False )

			isOK = dialog.IsOK( )
			if isOK == E_DIALOG_STATE_YES :
				inputNumber = dialog.GetChannelLast( )
				LOG_TRACE( 'Jump chNum[%s] currentCh[%s]'% (inputNumber,self.mCurrentChannel) )

				if int(self.mCurrentChannel) != int(inputNumber) :
					self.SetChannelTune( int(inputNumber) )


		LOG_TRACE( 'Leave' )

	def ShowRecording( self ) :
		LOG_TRACE('Enter')

		try:
			isRunRec = self.mDataCache.Record_GetRunningRecorderCount( )
			LOG_TRACE('isRunRecCount[%s]'% isRunRec)

			"""
			recLabel1 = ''
			recLabel2 = ''
			recImg1   = False
			recImg2   = False
			btnEdit   = True
			if isRunRec == 1 :
				btnEdit = False
				recImg1 = True
				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 0 )
				recLabel1 = '%04d %s'% (int(recInfo.mChannelNo), recInfo.mChannelName)

			elif isRunRec == 2 :
				btnEdit = False
				recImg1 = True
				recImg2 = True
				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 0 )
				recLabel1 = '%04d %s'% (int(recInfo.mChannelNo), recInfo.mChannelName)
				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 1 )
				recLabel2 = '%04d %s'% (int(recInfo.mChannelNo), recInfo.mChannelName)

			if self.mDataCache.GetChangeDBTableChannel( ) != -1 :
				if isRunRec > 0 :
					#use zapping table, in recording
					self.mDataCache.SetChangeDBTableChannel( E_TABLE_ZAPPING )
					self.mDataCache.Channel_GetZappingList( )
					self.mDataCache.LoadChannelList( )
					LOG_TRACE ('Recording changed: cache re-load')
				else :
					#use all channel table, not recording
					self.mDataCache.SetChangeDBTableChannel( E_TABLE_ALLCHANNEL )


			self.UpdateLabelGUI( self.mCtrlLblRec1.getId( ), recLabel1 )
			self.UpdateLabelGUI( self.mCtrlImgRec1.getId( ), recImg1 )
			self.UpdateLabelGUI( self.mCtrlLblRec2.getId( ), recLabel2 )
			self.UpdateLabelGUI( self.mCtrlImgRec2.getId( ), recImg2 )
			self.UpdateLabelGUI( self.mCtrlBtnEdit.getId( ), btnEdit )
			"""

			self.mRecCount = isRunRec

			if isRunRec == 1 :
				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 0 )
				recNum  = int(recInfo.mChannelNo)
				recName = recInfo.mChannelName
				self.mRecChannel1.append( recNum )
				self.mRecChannel1.append( recName )

			elif isRunRec == 2 :
				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 0 )
				recNum  = int(recInfo.mChannelNo)
				recName = recInfo.mChannelName
				self.mRecChannel1.append( recNum )
				self.mRecChannel1.append( recName )

				recInfo = self.mDataCache.Record_GetRunningRecordInfo( 1 )
				recNum  = int(recInfo.mChannelNo)
				recName = recInfo.mChannelName
				self.mRecChannel2.append( recNum )
				self.mRecChannel2.append( recName )

			if self.mDataCache.GetChangeDBTableChannel( ) != -1 :
				if isRunRec > 0 :
					#use zapping table, in recording
					self.mDataCache.SetChangeDBTableChannel( E_TABLE_ZAPPING )
					self.mDataCache.Channel_GetZappingList( )
					self.mDataCache.LoadChannelList( )
					LOG_TRACE ('Recording changed: cache re-load')
				else :
					#use all channel table, not recording
					self.mDataCache.SetChangeDBTableChannel( E_TABLE_ALLCHANNEL )


		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		LOG_TRACE('Leave')


