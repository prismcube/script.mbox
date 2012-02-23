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

from pvr.Util import RunThread, GuiLock, GuiLock2, MLOG, LOG_WARN, LOG_TRACE, LOG_ERR
from pvr.PublicReference import GetSelectedLongitudeString, EpgInfoTime, EpgInfoClock, EpgInfoComponentImage, EnumToString, ClassToList, AgeLimit, ParseLabelToCh
import pvr.ElisMgr
from ElisProperty import ElisPropertyEnum, ElisPropertyInt

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

E_SLIDE_ACTION_MAIN     = 0
E_SLIDE_ACTION_SUB      = 1
E_SLIDE_ALLCHANNEL      = 0
E_SLIDE_MENU_SATELLITE  = 1
E_SLIDE_MENU_FTACAS     = 2
E_SLIDE_MENU_FAVORITE   = 3
#E_SLIDE_MENU_EDITMODE   = 4
#E_SLIDE_MENU_DELETEALL  = 5
E_SLIDE_MENU_BACK       = 5

E_IMG_ICON_LOCK   = 'IconLockFocus.png'
E_IMG_ICON_ICAS   = 'IconCas.png'
E_IMG_ICON_MARK   = 'confluence/OverlayWatched.png'
E_IMG_ICON_TITLE1 = 'IconHeaderTitleSmall.png'
E_IMG_ICON_TITLE2 = 'icon_setting_focus.png'
E_IMG_ICON_UPDOWN = 'DI_Cursor_UpDown'

E_TAG_COLOR_RED   = '[COLOR red]'
E_TAG_COLOR_GREY  = '[COLOR grey]'
E_TAG_COLOR_GREY3 = '[COLOR grey3]'
E_TAG_COLOR_END   = '[/COLOR]'

FLAG_MODE_JUMP   = True

class ChannelListWindow(BaseWindow):

	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)

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

		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId )
		LOG_TRACE( 'winID[%d]'% self.mWinId)

		starttime = time.time()
		print '==================== TEST TIME[ONINIT] START[%s]'% starttime

		#header
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
		self.mLocalOffset = self.mDataCache.Datetime_GetLocalOffset()
		self.mChannelListServieType = ElisEnum.E_SERVICE_TYPE_INVALID
		self.mZappingMode = ElisEnum.E_MODE_ALL
		self.mChannelListSortMode = ElisEnum.E_SORT_BY_DEFAULT
		self.mChannelList = []
		self.mNavEpg = None
		self.mNavChannel = None
		self.mCurrentChannel = None
		self.mSlideOpenFlag = False
		self.mFlag_EditChanged = False

		#edit mode
		self.mIsSave = FLAG_MASK_NONE
		self.mMarkList = []
		self.mEditFavorite = []
		self.mMoveFlag = False
		self.mMoveItem = []


		#initialize get channel list
		self.mPropertyAge = self.mDataCache.mPropertyAge
		self.mPropertyPincode = self.mDataCache.mPropertyPincode
		self.SetVideoSize()
		self.InitSlideMenuHeader()
		#self.GetSlideMenuHeader( FLAG_SLIDE_INIT )

		try :
			#first get is used cache, reason by fast load
			self.mNavChannel = self.mDataCache.Channel_GetCurrent()
			self.mCurrentChannel = self.mNavChannel.mNumber
			
		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		self.InitChannelList()

		#clear label
		self.ResetLabel()

		#initialize get epg event
		self.InitEPGEvent()
		self.UpdateLabelInfo()

		#Event Register
		self.mEventBus.Register( self )

		#run thread
		self.mEnableThread = True
		self.CurrentTimeThread()

		self.mAsyncTuneTimer = None

		endtime = time.time()
		print '==================== TEST TIME[ONINIT] END[%s] loading[%s]'% (endtime, endtime-starttime )
		LOG_TRACE( 'Leave' )

	def onAction(self, aAction):
		#LOG_TRACE( 'Enter' )
		id = aAction.getId()

		self.GlobalAction( id )		

		if id >= Action.REMOTE_0 and id <= Action.REMOTE_9:
			self.KeySearch( id-Action.REMOTE_0 )

		elif id >= Action.ACTION_JUMP_SMS2 and id <= Action.ACTION_JUMP_SMS9 :
			rKey = id - (Action.ACTION_JUMP_SMS2 - 2)
			self.KeySearch( rKey )

		elif id == Action.ACTION_PREVIOUS_MENU or id == Action.ACTION_PARENT_DIR:
			#LOG_TRACE( 'goto previous menu' )
			self.SetGoBackWindow()

		elif id == Action.ACTION_SELECT_ITEM:
			self.GetFocusId()
			#LOG_TRACE( 'item select, action ID[%s]'% id )

			if self.mFocusId == self.mCtrlListMainmenu.getId() :
				position = self.mCtrlListMainmenu.getSelectedPosition()
				#LOG_TRACE( 'focus[%s] idx_main[%s]'% (self.mFocusId, position) )

				if position == E_SLIDE_MENU_BACK :
					self.mCtrlListCHList.setEnabled(True)
					self.setFocusId( self.mCtrlGropCHList.getId() )

				else :
					self.SubMenuAction( E_SLIDE_ACTION_MAIN, position )

		elif id == Action.ACTION_MOVE_RIGHT :
			pass

		elif id == Action.ACTION_MOVE_LEFT :
			self.GetFocusId()
			if self.mFocusId == self.mCtrlListCHList.getId() :
				self.GetSlideMenuHeader( FLAG_SLIDE_OPEN )
				self.mSlideOpenFlag = True

		elif id == Action.ACTION_MOVE_UP or id == Action.ACTION_MOVE_DOWN or \
			 id == Action.ACTION_PAGE_UP or id == Action.ACTION_PAGE_DOWN :
			self.GetFocusId()
			if self.mFocusId == self.mCtrlListCHList.getId() :
				if self.mMoveFlag :
					self.SetMarkChanneltoMove( FLAG_OPT_MOVE_UPDOWN, id )
					return

				#TODO : must be need timeout schedule
				self.RestartAsyncEPG()

			if self.mFocusId == self.mCtrlListMainmenu.getId() :
				position = self.mCtrlListMainmenu.getSelectedPosition()
				self.SubMenuAction( E_SLIDE_ACTION_MAIN, position )

			elif self.mFocusId == self.mCtrlBtnOpt :
				self.mCtrlListCHList.setEnabled( True )
				self.setFocusId( self.mCtrlGropCHList.getId() )


		elif id == Action.ACTION_CONTEXT_MENU :
			#LOG_TRACE( 'popup opt' )
			self.PopupOpt()


		elif id == 13: #'x'
			#this is test
			LOG_TRACE( 'language[%s]'% xbmc.getLanguage() )

		#LOG_TRACE( 'Leave' )

	def onClick(self, aControlId):
		LOG_TRACE( 'onclick focusID[%d]'% aControlId )

		if aControlId == self.mCtrlListCHList.getId() :
			if self.mViewMode == WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW :
				try:
					if self.mMoveFlag :
						self.SetMarkChanneltoMove( FLAG_OPT_MOVE_OK )
						return

					#Mark mode
					if self.mIsMark == True :
						idx = self.mCtrlListCHList.getSelectedPosition()
						self.MarkAddDelete('mark', idx )

						GuiLock2( True )
						self.setFocusId( self.mCtrlGropCHList.getId() )
						self.mCtrlListCHList.selectItem( idx+1 )
						GuiLock2( False )

						self.mCtrlSelectItem.setLabel( str('%s'% (idx+1)) )

					#Turn mode
					else :
						self.SetChannelTune()

				except Exception, e:
					LOG_TRACE( 'Error except[%s]'% e )

			else :
				self.SetChannelTune()

		elif aControlId == self.mCtrlBtnMenu.getId() or aControlId == self.mCtrlListMainmenu.getId() :
			#list view
			LOG_TRACE( '#############################' )

		elif aControlId == self.mCtrlListSubmenu.getId() :
			#list action
			position = self.mZappingMode
			self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )
			#LOG_TRACE( 'onclick focus[%s] idx_sub[%s]'% (aControlId, position) )

			#slide close
			GuiLock2(True)
			self.mCtrlListCHList.setEnabled(True)
			self.setFocusId( self.mCtrlGropCHList.getId() )
			GuiLock2(False)

		elif aControlId == self.mCtrlBtnOpt.getId():
			#LOG_TRACE( 'onclick Opt' )
			self.PopupOpt()

		elif aControlId == self.mCtrlBtnEdit.getId():
			self.SetGoBackEdit()

		elif aControlId == self.mCtrlBtnDelAll.getId():
			self.SetDeleteAll()

			#clear label
			self.ResetLabel()
			self.UpdateLabelInfo()

			self.mCtrlListCHList.reset()
			self.InitChannelList()

		elif aControlId == self.mCtrlRdoTV.getId():
			self.SetModeChanged( FLAG_MODE_TV )

		elif aControlId == self.mCtrlRdoRadio.getId():
			self.SetModeChanged( FLAG_MODE_RADIO )

		LOG_TRACE( 'Leave' )


	def onFocus(self, controlId):
		#LOG_TRACE( 'control %d' % controlId )
		pass

	def SetVideoSize( self ) :
		LOG_TRACE( 'Enter' )
		h = self.mCtrlImgVideoPos.getHeight()
		w = self.mCtrlImgVideoPos.getWidth()
		pos=list(self.mCtrlImgVideoPos.getPosition())
		x = pos[0] - 20
		y = pos[1] + 10
		#LOG_TRACE('==========h[%s] w[%s] x[%s] y[%s]'% (h,w,x,y) )

		ret = self.mCommander.Player_SetVIdeoSize( x, y, w, h ) 

		LOG_TRACE( 'Leave' )

	def SetDeleteAll( self ) :
		LOG_TRACE( 'Enter' )

		ret = E_DIALOG_STATE_NO

		#ask save question
		head =  Msg.Strings( MsgId.LANG_CONFIRM )
		line1 = Msg.Strings( MsgId.LANG_DELETE_ALL_CHANNEL )

		GuiLock2( True )
		dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
		dialog.SetDialogProperty( head, line1 )
		dialog.doModal()
		GuiLock2( False )

		ret = dialog.IsOK()

		#answer is yes
		if ret == E_DIALOG_STATE_YES :
			isDelete = self.mCommander.Channel_DeleteAll()
			LOG_TRACE( 'DeleteAll[%s]'% isDelete )

		return ret

		LOG_TRACE( 'Leave' )

	def SetModeChanged( self, aType = FLAG_MODE_TV) :
		LOG_TRACE( 'Enter' )

		self.mChannelListServieType = aType

		GuiLock2(True)
		if aType == FLAG_MODE_TV :
			label = self.mCtrlListCHList.getSelectedItem().getLabel()
			channelNumbr = ParseLabelToCh( self.mViewMode, label )
			LOG_TRACE( '=======label[%s] ch[%d] tvmode[%s]'% (label, channelNumbr, self.mChannelListServieType) )
			ret = None
			ret = self.mCommander.Channel_SetCurrent( channelNumbr, self.mChannelListServieType)
			if ret:
				self.mCurrentChannel = channelNumbr

		elif aType == FLAG_MODE_RADIO :
			self.mCommander.Player_VideoBlank( True, True )
		GuiLock2(False)

		self.mCtrlListMainmenu.selectItem( E_SLIDE_ALLCHANNEL )
		xbmc.sleep(50)
		self.SubMenuAction(E_SLIDE_ACTION_MAIN, E_SLIDE_ALLCHANNEL)
		self.mCtrlListSubmenu.selectItem( 0 )
		xbmc.sleep(50)
		self.SubMenuAction(E_SLIDE_ACTION_SUB, ElisEnum.E_MODE_ALL, True)

		#clear label
		self.ResetLabel()
		self.UpdateLabelInfo()

		self.mCtrlListCHList.reset()
		self.InitChannelList()

		#initialize get epg event
		self.mIsSelect = False
		self.InitEPGEvent()

		#slide close
		self.mCtrlListCHList.setEnabled(True)
		self.setFocusId( self.mCtrlGropCHList.getId() )


		LOG_TRACE( 'Leave' )

	def SetGoBackEdit( self ) :
		LOG_TRACE( 'Enter' )

		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			self.mViewMode = WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW

			try :
				#Event UnRegister
				#self.mEventBus.Deregister( self )

				self.InitSlideMenuHeader()
				self.mCtrlListMainmenu.selectItem( E_SLIDE_ALLCHANNEL )
				xbmc.sleep(50)
				self.SubMenuAction(E_SLIDE_ACTION_MAIN, E_SLIDE_ALLCHANNEL)

				self.mCtrlListSubmenu.selectItem( 0 )
				xbmc.sleep(50)
				self.SubMenuAction(E_SLIDE_ACTION_SUB, ElisEnum.E_MODE_ALL)

				#clear label
				self.ResetLabel()
				self.UpdateLabelInfo()

				self.mCtrlListCHList.reset()
				self.InitChannelList()

				ret = self.mCommander.Channel_Backup()
				#LOG_TRACE( 'channelBackup[%s]'% ret )

				#slide close
				GuiLock2(True)
				self.mCtrlListCHList.setEnabled(True)
				self.setFocusId( self.mCtrlGropCHList.getId() )
				GuiLock2(False)

			except Exception, e :
				LOG_TRACE( 'Error except[%s]'% e )

		else :
			self.SetGoBackWindow()

		LOG_TRACE( 'Leave' )

	def SetGoBackWindow( self ) :
		LOG_TRACE( 'Enter' )

		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			ret = False
			ret = self.SaveSlideMenuHeader()
			if ret != E_DIALOG_STATE_CANCEL :
				self.mEnableThread = False
				self.CurrentTimeThread().join()
				self.mCtrlListCHList.reset()
				self.Close()

			LOG_TRACE( 'go out Cancel')

		else :
			ret = False
			ret = self.SaveEditList()
			if ret != E_DIALOG_STATE_CANCEL :
				self.mViewMode = WinMgr.WIN_ID_CHANNEL_LIST_WINDOW
				self.mCtrlListCHList.reset()
				self.InitSlideMenuHeader()
				self.InitChannelList()

				#initialize get epg event
				self.mIsSelect = False
				self.InitEPGEvent()

				#clear label
				self.ResetLabel()
				self.UpdateLabelInfo()
				#Event Register
				#self.mEventBus.Register( self )

		LOG_TRACE( 'Leave' )

	@GuiLock
	def onEvent(self, aEvent):
		#LOG_TRACE( 'Enter' )
		#aEvent.printdebug()

		if self.mWinId == xbmcgui.getCurrentWindowId() :
			if aEvent.getName() == ElisEventCurrentEITReceived.getName() :

				if self.mNavChannel == None:
					return -1

				if self.mNavChannel.mSid != aEvent.mSid or self.mNavChannel.mTsid != aEvent.mTsid or self.mNavChannel.mOnid != aEvent.mOnid :
					return -1
		
				#LOG_TRACE('1========event id[%s] old[%s]'% (aEvent.mEventId, self.mEventId) )
				if aEvent.mEventId != self.mEventId :
					if self.mIsSelect == True :
						#on select, clicked
						ret = None
						ret = self.mDataCache.Epgevent_GetPresent()
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
								self.ResetLabel()
								self.UpdateLabelInfo()

							else:
								LOG_TRACE('epg SAME')
		else:
			LOG_TRACE( 'channellist winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId()) )

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
					self.ResetLabel()
					self.UpdateLabelInfo()
					self.PincodeDialogLimit()
					break
				chindex += 1

			GuiLock2(True)
			self.mCtrlListCHList.selectItem( chindex )
			xbmc.sleep(50)
			GuiLock2(False)

			channelNumbr = aJumpNumber
			label = 'JumpChannel'

		else:
			label = self.mCtrlListCHList.getSelectedItem().getLabel()
			channelNumbr = ParseLabelToCh( self.mViewMode, label )
		LOG_TRACE( 'label[%s] ch[%d] pin[%s]'% (label, channelNumbr, self.mPincodeEnter) )

		ret = False
		ret = self.mCommander.Channel_SetCurrent( channelNumbr, self.mChannelListServieType )
		#LOG_TRACE( 'MASK[%s] ret[%s]'% (self.mPincodeEnter, ret) )
		if ret == True :
			if self.mPincodeEnter == FLAG_MASK_NONE :
				if self.mCurrentChannel == channelNumbr :
					ret = False
					ret = self.SaveSlideMenuHeader()
					#LOG_TRACE('============== ret[%s]'% ret )
					if ret != E_DIALOG_STATE_CANCEL :
						self.mEnableThread = False
						self.CurrentTimeThread().join()
						self.Close()

						WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )
						return

					LOG_TRACE( 'go out Cancel' )

		ch = None
		ch = self.mCommander.Channel_GetCurrent()
		if ch :
			self.mNavChannel = ch
			self.mCurrentChannel = self.mNavChannel.mNumber
			self.mCtrlSelectItem.setLabel( str('%s'% (self.mCtrlListCHList.getSelectedPosition()+1)) )

			if aJumpNumber :
				return 

			self.ResetLabel()
			self.UpdateLabelInfo()
			self.PincodeDialogLimit()

		LOG_TRACE( 'Leave' )


	@GuiLock
	def SubMenuAction(self, aAction, aMenuIndex, aForce = None):
		LOG_TRACE( 'Enter' )

		retPass = False

		if aAction == E_SLIDE_ACTION_MAIN:
			testlistItems = []
			if aMenuIndex == 0 :
				self.mZappingMode = ElisEnum.E_MODE_ALL
				for itemList in range( len(self.mListAllChannel) ) :
					testlistItems.append( xbmcgui.ListItem(self.mListAllChannel[itemList]) )

			elif aMenuIndex == 1 :
				self.mZappingMode = ElisEnum.E_MODE_SATELLITE
				for itemClass in self.mListSatellite:
					ret = GetSelectedLongitudeString( itemClass.mLongitude, itemClass.mName )
					testlistItems.append( xbmcgui.ListItem(ret) )

			elif aMenuIndex == 2 :
				self.mZappingMode = ElisEnum.E_MODE_CAS
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
				self.mCtrlListSubmenu.reset()
				self.mCtrlListSubmenu.addItems( testlistItems )

				if aMenuIndex == self.mSelectMainSlidePosition :
					self.mCtrlListSubmenu.selectItem( self.mSelectSubSlidePosition )

		elif aAction == E_SLIDE_ACTION_SUB:
			if aForce == None and self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
				if self.mSelectMainSlidePosition == self.mCtrlListMainmenu.getSelectedPosition() and \
				   self.mSelectSubSlidePosition == self.mCtrlListSubmenu.getSelectedPosition() :
				   LOG_TRACE( 'aready select!!!' )
				   return

			if aMenuIndex == ElisEnum.E_MODE_ALL :
				position   = self.mCtrlListSubmenu.getSelectedPosition()
				if position == 0:
					sortingMode = ElisEnum.E_SORT_BY_NUMBER
				elif position == 1:
					sortingMode = ElisEnum.E_SORT_BY_ALPHABET
				elif position == 2:
					sortingMode = ElisEnum.E_SORT_BY_HD

				self.mChannelListSortMode = sortingMode
				retPass = self.GetChannelList( self.mChannelListServieType, self.mZappingMode, sortingMode, 0, 0, 0, '' )

			elif aMenuIndex == ElisEnum.E_MODE_SATELLITE:
				idx_Satellite = self.mCtrlListSubmenu.getSelectedPosition()
				item = self.mListSatellite[idx_Satellite]
				retPass = self.GetChannelList( self.mChannelListServieType, self.mZappingMode, self.mChannelListSortMode, item.mLongitude, item.mBand, 0, '' )
				#LOG_TRACE( 'cmd[channel_GetListBySatellite] idx_Satellite[%s] mLongitude[%s] band[%s]'% ( idx_Satellite, item.mLongitude, item.mBand ) )

			elif aMenuIndex == ElisEnum.E_MODE_CAS:
				idxFtaCas = self.mCtrlListSubmenu.getSelectedPosition()
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

				retPass = self.GetChannelList( self.mChannelListServieType, self.mZappingMode, self.mChannelListSortMode, 0, 0, caid, '' )
				#LOG_TRACE( 'cmd[channel_GetListByFTACas] idxFtaCas[%s]'% idxFtaCas )

			elif aMenuIndex == ElisEnum.E_MODE_FAVORITE:
				if self.mListFavorite : 
					idx_Favorite = self.mCtrlListSubmenu.getSelectedPosition()
					item = self.mListFavorite[idx_Favorite]
					retPass = self.GetChannelList( self.mChannelListServieType, self.mZappingMode, self.mChannelListSortMode, 0, 0, 0, item.mGroupName )
					#LOG_TRACE( 'cmd[channel_GetListByFavorite] idx_Favorite[%s] list_Favorite[%s]'% ( idx_Favorite, item.mGroupName ) )

				else:
					LOG_TRACE( 'cmd[channel_GetListByFavorite] idx_Favorite[%s] list_Favorite[%s]'% ( idx_Favorite, self.mListFavorite ) )

			if retPass == False :
				return

			if self.mMoveFlag :
				#do not refresh UI
				return
			
			#channel list update
			self.mListItems = None
			self.mCtrlListCHList.reset()
			self.InitChannelList()

			#path tree, Mainmenu/Submanu
			self.mSelectMainSlidePosition = self.mCtrlListMainmenu.getSelectedPosition()
			self.mSelectSubSlidePosition = self.mCtrlListSubmenu.getSelectedPosition()

			label1 = EnumToString('mode', self.mZappingMode)
			label2 = self.mCtrlListSubmenu.getSelectedItem().getLabel()
			label3 = EnumToString('sort', self.mChannelListSortMode)

			if self.mZappingMode == ElisEnum.E_MODE_ALL :
				self.mCtrlLblPath1.setLabel( '%s [COLOR grey3]>[/COLOR] sort by %s'% (label1.upper(),label3.title()) )
			else :
				self.mCtrlLblPath1.setLabel( '%s [COLOR grey3]>[/COLOR] %s [COLOR grey2]/ sort by %s[/COLOR]'% (label1.upper(),label2.title(),label3.title()) )

			#current zapping backup
			#self.mCommander.Channel_Backup()

		LOG_TRACE( 'Leave' )


	def GetChannelList(self, aType, aMode, aSort, aLongitude, aBand, aCAid, aFavName ):
		LOG_TRACE( 'Enter' )

		try :
			if aMode == ElisEnum.E_MODE_ALL :
				self.mChannelList = self.mCommander.Channel_GetList( aType, aMode, aSort )

			elif aMode == ElisEnum.E_MODE_SATELLITE :
				self.mChannelList = self.mCommander.Channel_GetListBySatellite( aType, aMode, aSort, aLongitude, aBand )

			elif aMode == ElisEnum.E_MODE_CAS :
				self.mChannelList = self.mCommander.Channel_GetListByFTACas( aType, aMode, aSort, aCAid )
				
			elif aMode == ElisEnum.E_MODE_FAVORITE :
				self.mChannelList = self.mCommander.Channel_GetListByFavorite( aType, aMode, aSort, aFavName )

			elif aMode == ElisEnum.E_MODE_NETWORK :
				pass


		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )
			return False


		LOG_TRACE( 'Leave' )
		return True

	def GetSlideMenuHeader(self, mode) :
		LOG_TRACE( 'Enter' )

		idx1 = 0
		idx2 = 0

		if mode == FLAG_SLIDE_INIT :

			#self.mElisZappingModeInfo.printdebug()
			#LOG_TRACE( 'satellite[%s]'% ClassToList( 'convert', self.mListSatellite ) )
			#LOG_TRACE( 'ftacas[%s]'   % ClassToList( 'convert', self.mListCasList ) )
			#LOG_TRACE( 'favorite[%s]' % ClassToList( 'convert', self.mListFavorite ) )

			_mode = self.mElisZappingModeInfo.mMode
			_sort = self.mElisZappingModeInfo.mSortingMode
			_type = self.mElisZappingModeInfo.mServiceType
			_name = ''

			if _mode == ElisEnum.E_MODE_ALL :
				idx1 = 0
				if _sort == ElisEnum.E_SORT_BY_NUMBER :
					idx2 = 0
				elif _sort == ElisEnum.E_SORT_BY_ALPHABET :
					idx2 = 1
				elif _sort == ElisEnum.E_SORT_BY_HD :
					idx2 = 2
				else :
					idx2 = 0

			elif _mode == ElisEnum.E_MODE_SATELLITE :
				idx1 = 1
				_name = self.mElisZappingModeInfo.mSatelliteInfo.mName

				for item in self.mListSatellite :
					if _name == item.mName :
						break
					idx2 += 1

			elif _mode == ElisEnum.E_MODE_CAS :
				idx1 = 2
				_name = self.mElisZappingModeInfo.mCasInfo.mName

				for item in self.mListCasList :
					if _name == item.mName :
						break
					idx2 += 1

			elif _mode == ElisEnum.E_MODE_FAVORITE :
				idx1 = 3
				_name = self.mElisZappingModeInfo.mFavoriteGroup.mGroupName

				for item in self.mListFavorite :
					if _name == item.mGroupName :
						break
					idx2 += 1

			self.mSelectMainSlidePosition = idx1
			self.mSelectSubSlidePosition = idx2

		elif mode == FLAG_SLIDE_OPEN :
			idx1 = self.mSelectMainSlidePosition
			idx2 = self.mSelectSubSlidePosition


		self.mCtrlListMainmenu.selectItem( idx1 )
		self.SubMenuAction(E_SLIDE_ACTION_MAIN, idx1)
		self.mCtrlListSubmenu.selectItem( idx2 )
		#self.setFocusId( self.mCtrlListSubmenu.getId() )

		LOG_TRACE( 'Leave' )


	def SaveSlideMenuHeader(self) :
		LOG_TRACE( 'Enter' )

		"""
		LOG_TRACE( 'mode[%s] sort[%s] type[%s] mpos[%s] spos[%s]'% ( \
			self.mZappingMode,                \
			self.mChannelListSortMode,        \
			self.mChannelListServieType,      \
			self.mSelectMainSlidePosition,    \
			self.mSelectSubSlidePosition      \
		)
		self.mListSatellite[self.mSelectSubSlidePosition].printdebug()
		self.mListCasList[self.mSelectSubSlidePosition].printdebug()
		self.mListFavorite[self.mSelectSubSlidePosition].printdebug()

		array=[]
		self.mElisSetZappingModeInfo.reset()
		self.mElisSetZappingModeInfo.mMode = self.mZappingMode
		self.mElisSetZappingModeInfo.mSortingMode = self.mChannelListSortMode
		self.mElisSetZappingModeInfo.mServiceType = self.mChannelListServieType

		self.mElisSetZappingModeInfo.printdebug()

		array.append( self.mElisSetZappingModeInfo )
		ret = self.mCommander.Zappingmode_SetCurrent( array )
		"""

		changed = False
		answer = E_DIALOG_STATE_NO

		if self.mSelectMainSlidePosition != self.mLastMainSlidePosition or \
		   self.mSelectSubSlidePosition != self.mLastSubSlidePosition :
			changed = True

		if self.mElisZappingModeInfo.mServiceType != self.mChannelListServieType :
			changed = True

		#is change?
		if changed :
			try :
				GuiLock2( True )
				#ask save question
				label1 = EnumToString( 'mode', self.mZappingMode )
				label2 = self.mCtrlListSubmenu.getSelectedItem().getLabel()

				head =  Msg.Strings( MsgId.LANG_SETTING_TO_CHANGE_ZAPPING_MODE )
				line1 = '%s / %s'% ( label1.title(), label2.title() )
				line2 = Msg.Strings( MsgId.LANG_DO_YOU_WANT_TO_SAVE_CHANNELS )

				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
				dialog.SetDialogProperty( head, str('%s\n\n%s'% (line1,line2)) )
				dialog.doModal()
				GuiLock2( False )

				answer = dialog.IsOK()

				#answer is yes
				if answer == E_DIALOG_STATE_YES :
					#re-configuration class
					self.mElisSetZappingModeInfo.reset()
					self.mElisSetZappingModeInfo.mMode = self.mZappingMode
					self.mElisSetZappingModeInfo.mSortingMode = self.mChannelListSortMode
					self.mElisSetZappingModeInfo.mServiceType = self.mChannelListServieType

					if self.mSelectMainSlidePosition == 1 :
						groupInfo = self.mListSatellite[self.mSelectSubSlidePosition]
						self.mElisSetZappingModeInfo.mSatelliteInfo = groupInfo
						
					elif self.mSelectMainSlidePosition == 2 :
						groupInfo = self.mListCasList[self.mSelectSubSlidePosition]
						self.mElisSetZappingModeInfo.mCasInfo = groupInfo
					
					elif self.mSelectMainSlidePosition == 3 :
						groupInfo = self.mListFavorite[self.mSelectSubSlidePosition]
						self.mElisSetZappingModeInfo.mFavoriteGroup = groupInfo


					retList = []
					retList.append( self.mElisSetZappingModeInfo )
					#LOG_TRACE( 'mElisSetZappingModeInfo[%s]'% ClassToList( 'convert', retList ) )
					LOG_TRACE( '1. zappingMode[%s] sortMode[%s] serviceType[%s]'%  \
						( EnumToString('mode', self.mZappingMode),         \
						  EnumToString('sort', self.mChannelListSortMode), \
						  EnumToString('type', self.mChannelListServieType)) )
					LOG_TRACE( '2. zappingMode[%s] sortMode[%s] serviceType[%s]'%  \
						( EnumToString('mode', self.mElisSetZappingModeInfo.mMode),         \
						  EnumToString('sort', self.mElisSetZappingModeInfo.mSortingMode), \
						  EnumToString('type', self.mElisSetZappingModeInfo.mServiceType)) )

					#save zapping mode
					ret = self.mCommander.Zappingmode_SetCurrent( retList )
					LOG_TRACE( 'set zappingmode_SetCurrent[%s]'% ret )
					if ret :
						#### data cache re-load ####
						self.mDataCache.LoadZappingmode()
						self.mDataCache.LoadZappingList()
						self.mDataCache.LoadChannelList()
						LOG_TRACE ('=====================cache re-load')

					#save current zapping
					#isSave = self.mCommander.Channel_Save()
					#LOG_TRACE( 'save[%s]'% isSave )

				elif answer == E_DIALOG_STATE_NO :
					pass
					#restore backup zapping
					#isSave = self.mCommander.Channel_Restore( True )
					#LOG_TRACE( 'Restore[%s]'% isSave )

			except Exception, e :
				LOG_TRACE( 'Error exception[%s]'% e )

		else:
			#channel sync
			self.mDataCache.mCurrentChannel = self.mNavChannel

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
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_YES_NO_CANCEL )
			dialog.SetDialogProperty( head, line1 )
			dialog.doModal()
			GuiLock2( False )

			answer = dialog.IsOK()

			#answer is yes
			if answer == E_DIALOG_STATE_YES :
				self.mIsSave = FLAG_MASK_NONE
				self.mFlag_EditChanged = True
				isSave = self.mCommander.Channel_Save()
				LOG_TRACE( 'save[%s]'% isSave )

			elif answer == E_DIALOG_STATE_NO :
				self.mIsSave = FLAG_MASK_NONE
				isSave = self.mCommander.Channel_Restore( True )
				LOG_TRACE( 'Restore[%s]'% isSave )


		return answer

		LOG_TRACE( 'Leave' )

	def InitSlideMenuHeader( self ) :
		LOG_TRACE( 'Enter' )

		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
			#opt btn blind
			GuiLock2(True)
			self.mCtrlGropOpt.setVisible( False )
			GuiLock2(False)

		else :
			#opt btn visible
			GuiLock2(True)
			self.mCtrlGropOpt.setVisible( True )
			GuiLock2(False)
			return

		#main/sub menu init
		self.mCtrlListMainmenu.reset()
		self.mCtrlListSubmenu.reset()

		#get last zapping mode
		try:
			if self.mFlag_EditChanged :
				zappingMode = self.mCommander.Zappingmode_GetCurrent()
			else :
				zappingMode = self.mDataCache.Zappingmode_GetCurrent()
				
			self.mZappingMode           = zappingMode.mMode
			self.mChannelListSortMode   = zappingMode.mSortingMode
			self.mChannelListServieType = zappingMode.mServiceType
			self.mElisZappingModeInfo   = zappingMode
			self.mElisSetZappingModeInfo= zappingMode

		except Exception, e:
			self.mZappingMode           = ElisEnum.E_MODE_ALL
			self.mChannelListSortMode   = ElisEnum.E_SORT_BY_DEFAULT
			self.mChannelListServieType = ElisEnum.E_SERVICE_TYPE_TV
			LOG_TRACE( 'Error exception[%s] init default zappingmode'% e )

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
				self.mListSatellite = self.mCommander.Satellite_GetConfiguredList( ElisEnum.E_SORT_NAME )
				#ClassToList( 'print', self.mListSatellite )

				#FTA list
				self.mListCasList = self.mCommander.Fta_cas_GetList( self.mChannelListServieType )
				#ClassToList( 'print', self.mListCasList )

				#Favorite list
				self.mListFavorite = self.mCommander.Favorite_GetList( self.mChannelListServieType )
				#ClassToList( 'print', self.mListFavorite )
			else:
				self.mListSatellite = self.mDataCache.Satellite_GetConfiguredList()
				self.mListCasList = self.mDataCache.Fta_cas_GetList()
				self.mListFavorite = self.mDataCache.Favorite_GetList()

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


		testlistItems = []
		if self.mZappingMode == ElisEnum.E_MODE_ALL :
			for item in range(len(self.mListAllChannel)) :
				testlistItems.append(xbmcgui.ListItem(self.mListAllChannel[item]))

		elif self.mZappingMode == ElisEnum.E_MODE_SATELLITE :
			for item in self.mListSatellite:
				ret = GetSelectedLongitudeString( item.mLongitude, item.mName )
				testlistItems.append(xbmcgui.ListItem(ret))

		elif self.mZappingMode == ElisEnum.E_MODE_CAS :
			for item in self.mListCasList:
				ret = '%s(%s)'% ( item.mName, item.mChannelCount )
				testlistItems.append(xbmcgui.ListItem( ret ))

		elif self.mZappingMode == ElisEnum.E_MODE_FAVORITE :
			for item in self.mListFavorite:
				testlistItems.append(xbmcgui.ListItem( item.mGroupName ))

		self.mCtrlListSubmenu.addItems( testlistItems )


		#path tree, Mainmenu/Submanu
		label1 = EnumToString('mode', self.mZappingMode)
		label2 = self.mCtrlListSubmenu.getSelectedItem().getLabel()
		label3 = EnumToString('sort', self.mChannelListSortMode)
		if self.mZappingMode == ElisEnum.E_MODE_ALL :
			self.mCtrlLblPath1.setLabel( '%s [COLOR grey3]>[/COLOR] sort by %s'% (label1.upper(),label3.title()) )
		else :
			self.mCtrlLblPath1.setLabel( '%s [COLOR grey3]>[/COLOR] %s [COLOR grey2]/ sort by %s[/COLOR]'% (label1.upper(),label2.title(),label3.title()) )

		self.GetSlideMenuHeader( FLAG_SLIDE_INIT )
		self.mLastMainSlidePosition = self.mSelectMainSlidePosition
		self.mLastSubSlidePosition = self.mSelectSubSlidePosition


		#get channel list by last on zapping mode, sorting, service type
		self.mNavChannel = None
		self.mChannelList = None


		if self.mFlag_EditChanged :
			self.mChannelList = self.mCommander.Channel_GetList( self.mChannelListServieType, self.mZappingMode, self.mChannelListSortMode )
		else :
			#### first get is used cache, reason by fast load ###
			self.mChannelList = self.mDataCache.Channel_GetList()

		"""
		if self.mChannelList :
			LOG_TRACE( 'zappingMode[%s] sortMode[%s] serviceType[%s]'%  \
				( EnumToString('mode', self.mZappingMode),         \
				  EnumToString('sort', self.mChannelListSortMode), \
				  EnumToString('type', self.mChannelListServieType)) )
			LOG_TRACE( 'len[%s] ch%s'% (len(self.mChannelList),ClassToList( 'convert', self.mChannelList )) )
		"""
		LOG_TRACE( 'Leave' )


	def InitChannelList(self):
		LOG_TRACE( 'Enter' )

		#starttime = time.time()
		#print '==================== TEST TIME[LIST] START[%s]'% starttime

		#no channel is set Label comment
		if self.mChannelList == None:
			label = Msg.Strings( MsgId.LANG_NO_CHANNELS )
			self.mCtrlChannelName.setLabel( label )

			LOG_TRACE( 'no data, iChannel[%s]'% self.mChannelList )
			return 


		lblColorS = E_TAG_COLOR_GREY
		lblColorE = E_TAG_COLOR_END
		LOG_TRACE('listItems data[%s]'% (self.mListItems) )
		if self.mListItems == None :
			self.mListItems = []
			for iChannel in self.mChannelList:
				try:
					if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
						#skip ch
						if iChannel.mSkipped == True :
							continue
						listItem = xbmcgui.ListItem( "%04d %s"%( iChannel.mNumber, iChannel.mName ), "-", "-", "-", "-" )

					else :
						#skip ch
						if iChannel.mSkipped == True :
							lblColorS = E_TAG_COLOR_GREY3
						else:
							lblColorS = E_TAG_COLOR_GREY

						listItem = xbmcgui.ListItem( "%s%04d %s%s"%( lblColorS, iChannel.mNumber, iChannel.mName, lblColorE ), "-", "-", "-", "-" )

				except Exception, e:
					LOG_TRACE( '=========== except[%s]'% e )


				if iChannel.mLocked  : listItem.setProperty('lock', E_IMG_ICON_LOCK)
				if iChannel.mIsCA    : listItem.setProperty('icas', E_IMG_ICON_ICAS)

				self.mListItems.append(listItem)

		GuiLock2(True)
		self.mCtrlListCHList.addItems( self.mListItems )
		GuiLock2(False)


		#get last channel
		iChannel = None
		if self.mListItems == None :
			iChannel = self.mCommander.Channel_GetCurrent()
		else :
			iChannel = self.mDataCache.Channel_GetCurrent()

		if iChannel :
			self.mNavChannel = iChannel
			self.mCurrentChannel = self.mNavChannel.mNumber

		#detected to last focus
		iChannelIdx = 0;
		for iChannel in self.mChannelList:
			if iChannel.mNumber == self.mNavChannel.mNumber :
				break
			iChannelIdx += 1

		GuiLock2(True)
		self.mCtrlListCHList.selectItem( iChannelIdx )
		xbmc.sleep(50)

		#select item idx, print GUI of 'current / total'
		self.mCtrlSelectItem.setLabel( str('%s'% (self.mCtrlListCHList.getSelectedPosition()+1)) )
		GuiLock2(False)

		#endtime = time.time()
		#print '==================== TEST TIME[LIST] END[%s] loading[%s]'% (endtime, endtime-starttime )
		LOG_TRACE( 'Leave' )


	def ResetLabel(self):
		LOG_TRACE( 'Enter' )

		if self.mChannelListServieType == ElisEnum.E_SERVICE_TYPE_TV:
			self.mCtrlRdoTV.setSelected( True )
			self.mCtrlRdoRadio.setSelected( False )
		elif self.mChannelListServieType == ElisEnum.E_SERVICE_TYPE_RADIO:
			self.mCtrlRdoTV.setSelected( False )
			self.mCtrlRdoRadio.setSelected( True )

		self.mCtrlProgress.setPercent(0)
		self.mCtrlProgress.setVisible(False)
		self.mPincodeEnter = FLAG_MASK_NONE

		self.mCtrlSelectItem.setLabel( str('%s'% (self.mCtrlListCHList.getSelectedPosition()+1)) )
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
				iEPG = self.mDataCache.Epgevent_GetPresent()
				if iEPG and iEPG.mEventName != 'No Name':
					self.mNavEpg = iEPG
					#iEPG.printdebug()

			else :
				if self.mChannelList :
					label = self.mCtrlListCHList.getSelectedItem().getLabel()
					channelNumbr = ParseLabelToCh( self.mViewMode, label )
					#LOG_TRACE( 'label[%s] ch[%d]'% (label, channelNumbr) )

					for iChannel in self.mChannelList:
						if iChannel.mNumber == channelNumbr :
							self.mNavChannel = None
							self.mNavChannel = iChannel
							#LOG_TRACE( 'found ch: getlabel[%s] ch[%s]'% (channelNumbr, ch.mNumber ) )

							gmtime = self.mDataCache.Datetime_GetGMTTime()
							gmtFrom = gmtime
							gmtUntil= gmtime
							maxCount= 1
							iEPGList = None
							iEPGList = self.mCommander.Epgevent_GetList( iChannel.mSid, iChannel.mTsid, iChannel.mOnid, gmtFrom, gmtUntil, maxCount )

							#LOG_TRACE('=============epg len[%s] list[%s]'% (len(iEPGList),ClassToList('convert', iEPGList )) )
							if iEPGList :
								self.mNavEpg = iEPGList[0]
							else :
								#self.mNavEpg.reset()
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
	def UpdateLabelGUI( self, aCtrlID = None, aValue = None ) :
		LOG_TRACE( 'Enter' )

		if aCtrlID == self.mCtrlChannelName.getId() :
			self.mCtrlChannelName.setLabel( aValue )

		elif aCtrlID == self.mCtrlLongitudeInfo.getId() :
			self.mCtrlLongitudeInfo.setLabel( aValue )

		elif aCtrlID == self.mCtrlCareerInfo.getId() :
			self.mCtrlCareerInfo.setLabel( aValue )

		elif aCtrlID == self.mCtrlEventName.getId() :
			self.mCtrlEventName.setLabel( aValue )

		elif aCtrlID == self.mCtrlEventTime.getId() :
			self.mCtrlEventTime.setLabel( aValue )

		elif aCtrlID == self.mCtrlLockedInfo.getId() :
			self.mCtrlLockedInfo.setVisible( aValue )

		elif aCtrlID == self.mCtrlServiceTypeImg1.getId() :
			self.mCtrlServiceTypeImg1.setImage( aValue )

		elif aCtrlID == self.mCtrlServiceTypeImg2.getId() :
			self.mCtrlServiceTypeImg2.setImage( aValue )

		elif aCtrlID == self.mCtrlServiceTypeImg3.getId() :
			self.mCtrlServiceTypeImg3.setImage( aValue )

		LOG_TRACE( 'Leave' )

	
	def UpdateLabelInfo( self ):
		LOG_TRACE( 'Enter' )

		if self.mNavChannel :
			#update channel name
			if self.mIsSelect == True :
				strType = self.UpdateServiceType( self.mNavChannel.mServiceType )
				label = '%s - %s'% (strType, self.mNavChannel.mName)
				self.UpdateLabelGUI( self.mCtrlChannelName.getId(), label )

			#update longitude info
			satellite = self.mDataCache.Satellite_GetByChannelNumber( self.mNavChannel.mNumber )
			if not satellite :
				#LOG_TRACE('Fail GetByChannelNumber by Cache')
				satellite = self.mCommander.Satellite_GetByChannelNumber( self.mNavChannel.mNumber, self.mNavChannel.mServiceType )

			if satellite :
				label = GetSelectedLongitudeString( satellite.mLongitude, satellite.mName )
				self.UpdateLabelGUI( self.mCtrlLongitudeInfo.getId(), label )
			else :
				self.UpdateLabelGUI( self.mCtrlLongitudeInfo.getId(), '' )

			#update lock-icon visible
			if self.mNavChannel.mLocked :
					self.mPincodeEnter |= FLAG_MASK_ADD
					self.UpdateLabelGUI( self.mCtrlLockedInfo.getId(), True )


			#update career info
			if self.mNavChannel.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBS:
				value1 = self.mNavChannel.mCarrier.mDVBS.mPolarization
				value2 = self.mNavChannel.mCarrier.mDVBS.mFrequency
				value3 = self.mNavChannel.mCarrier.mDVBS.mSymbolRate

				polarization = EnumToString( 'Polarization', value1 )
				careerLabel = '%s MHz, %s KS/S, %s'% (value2, value3, polarization)
				self.UpdateLabelGUI( self.mCtrlCareerInfo.getId(), careerLabel )

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
				self.UpdateLabelGUI( self.mCtrlEventName.getId(), self.mNavEpg.mEventName )
				self.UpdateLabelGUI( self.mCtrlEventTime.getId(), label )
				self.mCtrlProgress.setVisible( True )

				#component
				imagelist = EpgInfoComponentImage( self.mNavEpg )				
				if len(imagelist) == 1:
					self.UpdateLabelGUI( self.mCtrlServiceTypeImg1.getId(), imagelist[0] )
				elif len(imagelist) == 2:
					self.UpdateLabelGUI( self.mCtrlServiceTypeImg1.getId(), imagelist[0] )
					self.UpdateLabelGUI( self.mCtrlServiceTypeImg2.getId(), imagelist[1] )

				elif len(imagelist) == 3:
					self.UpdateLabelGUI( self.mCtrlServiceTypeImg1.getId(), imagelist[0] )
					self.UpdateLabelGUI( self.mCtrlServiceTypeImg2.getId(), imagelist[1] )
					self.UpdateLabelGUI( self.mCtrlServiceTypeImg3.getId(), imagelist[2] )
				else:
					self.UpdateLabelGUI( self.mCtrlServiceTypeImg1.getId(), '' )
					self.UpdateLabelGUI( self.mCtrlServiceTypeImg2.getId(), '' )
					self.UpdateLabelGUI( self.mCtrlServiceTypeImg3.getId(), '' )


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
				self.mCommander.Player_AVBlank( True, True )
				#self.mCommander.Channel_SetInitialBlank( True )
				GuiLock2( True )
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_NUMERIC_KEYBOARD )
				dialog.SetDialogProperty( msg, '', 4, True )
	 			dialog.doModal()
				GuiLock2( False )

	 			if dialog.IsOK() == E_DIALOG_STATE_YES :
	 				inputPin = dialog.GetString()
				
				if inputPin == None or inputPin == '' :
					inputPin = ''
				LOG_TRACE( 'mask[%s] inputPin[%s] stbPin[%s]'% (self.mPincodeEnter, inputPin, self.mPropertyPincode) )

				if inputPin == str('%s'% self.mPropertyPincode) :
					GuiLock2(True)
					label = self.mCtrlListCHList.getSelectedItem().getLabel()
					GuiLock2(False)
					channelNumbr = ParseLabelToCh( self.mViewMode, label )
					LOG_TRACE( '=======label[%s] ch[%d] pin[%s]'% (label, channelNumbr, self.mPincodeEnter) )
					self.mPincodeEnter = FLAG_MASK_NONE
					ret = None
					ret = self.mCommander.Channel_SetCurrent( channelNumbr, self.mChannelListServieType)
					if ret:
						self.mCurrentChannel = channelNumbr

					LOG_TRACE( 'Pincode success' )
				else:
					msg1 = Msg.Strings(MsgId.LANG_ERROR)
					msg2 = Msg.Strings(MsgId.LANG_WRONG_PIN_CODE)
					GuiLock2( True )
					xbmcgui.Dialog().ok( msg1, msg2 )
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
		LOG_TRACE( 'Enter' )
		
		try:
			self.mLocalTime = self.mDataCache.Datetime_GetLocalTime()

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

		LOG_TRACE( 'Leave' )


	@GuiLock
	def SetMarkDeleteCh( self, aMode, aEnabled = True, aGroupName = '' ) :
		LOG_TRACE( 'Enter' )

		lastPos = self.mCtrlListCHList.getSelectedPosition()

		try:
			#----------------> 1.set current position item <-------------
			if len(self.mMarkList) < 1 :
				#icon toggle
				if aMode.lower() == 'lock' :
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
					ret = self.mCommander.Channel_Lock( aEnabled, retList )

				#label color
				elif aMode.lower() == 'skip' :
					#remove tag [COLOR ...]label[/COLOR]
					label1 = self.mCtrlListCHList.getSelectedItem().getLabel()
					label2 = re.findall('\](.*)\[', label1)
					cmd = ''

					if aEnabled :
						label3= str('%s%s%s'%( E_TAG_COLOR_GREY3, label2[0], E_TAG_COLOR_END ) )
						cmd = 'Skip'
					else :
						label3= str('%s%s%s'%( E_TAG_COLOR_GREY, label2[0], E_TAG_COLOR_END ) )
						cmd = 'UnSkip'
					self.mCtrlListCHList.getSelectedItem().setLabel(label3)

					retList = []
					retList.append( self.mChannelList[lastPos] )
					ret = self.mCommander.Channel_Skip( aEnabled, retList )

				elif aMode.lower() == 'delete' :
					cmd = aMode.title()
					retList = []
					retList.append( self.mChannelList[lastPos] )
					ret = self.mCommander.Channel_Delete( retList )

				elif aMode.lower() == 'add' :
					#strip tag [COLOR ...]label[/COLOR]
					number = self.mChannelList[lastPos].mNumber
					cmd = 'AddChannel to Group'
					if aGroupName :
						ret = self.mCommander.Favoritegroup_AddChannel( aGroupName, number, self.mChannelListServieType )
					else :
						ret = 'group None'

				elif aMode.lower() == 'del' :
					#strip tag [COLOR ...]label[/COLOR]
					number = self.mChannelList[lastPos].mNumber
					cmd = 'RemoveChannel to Group'
					if aGroupName :
						ret = self.mCommander.Favoritegroup_RemoveChannel( aGroupName, number, self.mChannelListServieType )
					else :
						ret = 'group None'

				#LOG_TRACE( 'set[%s] idx[%s] ret[%s]'% (cmd,lastPos,ret) )

			else :
				#----------------> 2.set mark list all <-------------
				for idx in self.mMarkList :
				
					self.mCtrlListCHList.selectItem(idx)
					xbmc.sleep(50)

					listItem = self.mCtrlListCHList.getListItem(idx)
					cmd = ''
					ret = ''
					#icon toggle
					if aMode.lower() == 'lock' :

						#lock toggle: disable
						if aEnabled :
							listItem.setProperty('lock', E_IMG_ICON_LOCK)
							cmd = 'Lock'
						else :
							listItem.setProperty('lock', '')
							cmd = 'UnLock'

						retList = []
						retList.append( self.mChannelList[idx] )
						ret = self.mCommander.Channel_Lock( aEnabled, retList )


					#label color
					elif aMode.lower() == 'skip' :
						#strip tag [COLOR ...]label[/COLOR]
						label1 = self.mCtrlListCHList.getSelectedItem().getLabel()
						label2 = re.findall('\](.*)\[', label1)
						if aEnabled :
							label3= str('%s%s%s'%( E_TAG_COLOR_GREY3, label2[0], E_TAG_COLOR_END ) )
							cmd = 'Skip'
						else :
							label3= str('%s%s%s'%( E_TAG_COLOR_GREY, label2[0], E_TAG_COLOR_END ) )
							cmd = 'UnSkip'
						self.mCtrlListCHList.getSelectedItem().setLabel(label3)
						#LOG_TRACE( 'idx[%s] 1%s 2%s 3%s'% (idx, label1,label2,label3) )

						retList = []
						retList.append( self.mChannelList[idx] )
						ret = self.mCommander.Channel_Skip( aEnabled, retList )

					elif aMode.lower() == 'delete' :
						cmd = 'Delete'
						retList = []
						retList.append( self.mChannelList[idx] )
						ret = self.mCommander.Channel_Delete( retList )

					elif aMode.lower() == 'add' :
						number = self.mChannelList[idx].mNumber
						cmd = 'AddChannel to Group'
						if aGroupName :
							ret = self.mCommander.Favoritegroup_AddChannel( aGroupName, number, self.mChannelListServieType )
						else :
							ret = 'group None'

					elif aMode.lower() == 'del' :
						number = self.mChannelList[idx].mNumber
						cmd = 'RemoveChannel to Group'
						if aGroupName :
							ret = self.mCommander.Favoritegroup_RemoveChannel( aGroupName, number, self.mChannelListServieType )
						else :
							ret = 'group None'

					elif aMode.lower() == 'move' :
						cmd = 'Move'
						idxM= idx + aEnabled
						if idxM < 0 : continue

						#exchange name
						labelM = self.mCtrlListCHList.getSelectedItem().getLabel()
						name = self.mChannelList[idxM].mName
						number=self.mChannelList[idxM].mNumber
						label = str('%s%s %s%s'%( E_TAG_COLOR_GREY, number, name, E_TAG_COLOR_END ) )
						self.mCtrlListCHList.getSelectedItem().setLabel(label)

						self.mCtrlListCHList.selectItem(idxM)
						xbmc.sleep(50)
						self.mCtrlListCHList.getSelectedItem().setLabel(labelM)

						continue
					
					elif aMode.lower() == 'gmove' :
						cmd = 'Move in Group'
						insertPosition = idx + aEnabled
						if aGroupName :
							ret = self.mCommander.FavoriteGroup_MoveChannels( aGroupName, insertPosition, self.mChannelListServieType, self.mChannelList[idx] )
						else :
							ret = 'group None'

					#LOG_TRACE( 'set[%s] idx[%s] ret[%s]'% (cmd,idx,ret) )

					#mark remove
					listItem.setProperty('mark', '')

				#recovery last focus
				self.mCtrlListCHList.selectItem(lastPos)


		except Exception, e:
			LOG_TRACE( 'Error except[%s]'% e )

		LOG_TRACE( 'Leave' )

	def MarkAddDelete( self, aMode, aPos, aEnabled=True ) :
		LOG_TRACE( 'Enter' )

		if aMode.lower() == 'mark' :
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


		elif aMode.lower() == 'delete' :
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


	def GroupAddDelete( self, aMode, aDialog = 0, aBtn = 0, aGroupName = '' ) :
		LOG_TRACE( 'Enter' )

		if aMode.lower() == 'get' :
			#Favorite list
			self.mListFavorite = self.mCommander.Favorite_GetList( self.mChannelListServieType )
			ClassToList( 'print', self.mListFavorite )

			self.mEditFavorite = []
			if self.mListFavorite :
				for item in self.mListFavorite:
					#copy to favoriteGroup
					self.mEditFavorite.append( item.mGroupName )

		elif aMode.lower() == 'set' :
			cmd = ''
			ret = ''

			if aBtn == E_DialogInput01 :
				cmd = 'lock'
				self.SetMarkDeleteCh( cmd, True )

			elif aBtn == E_DialogInput02 :
				cmd = 'lock'
				self.SetMarkDeleteCh( cmd, False)

			elif aBtn == E_DialogInput03 :
				cmd = 'skip'
				self.SetMarkDeleteCh( cmd, True )

			elif aBtn == E_DialogInput04 :
				cmd = 'skip'
				self.SetMarkDeleteCh( cmd, False )

			elif aBtn == E_DialogInput05 :
				if aDialog == FLAG_OPT_LIST :
					cmd = 'delete'
				else :
					cmd = 'del'

				self.SetMarkDeleteCh( cmd, True, aGroupName )
				self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )

			elif aBtn == E_DialogInput06 :
				cmd = 'move'
				self.SetMarkChanneltoMove(FLAG_OPT_MOVE, None, aGroupName )
				if self.mMarkList :
					idx = int(self.mMarkList[0])
					GuiLock2(True)
					xbmc.executebuiltin('xbmc.Container.PreviousViewMode')
					xbmc.sleep(50)
					self.mCtrlListCHList.selectItem(idx)
					self.setFocusId( self.mCtrlGropCHList.getId() )
					GuiLock2(False)
				return

			elif aBtn == E_DialogInput07 :
				if aDialog == FLAG_OPT_LIST :
					cmd = 'add'
					self.SetMarkDeleteCh( cmd, True, aGroupName )
					self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )
				else :
					cmd = 'Create'
					ret = self.mCommander.Favoritegroup_Create( aGroupName, self.mChannelListServieType )	#default : ElisEnum.E_SERVICE_TYPE_TV
					#LOG_TRACE( 'set[%s] name[%s] ret[%s]'% (cmd,aGroupName,ret) )				

			elif aBtn == E_DialogInput08 :
				#parse idx, source name, rename
				cmd = 'Rename'
				name = re.split(':', aGroupName)
				ret = self.mCommander.Favoritegroup_ChangeName( name[1], self.mChannelListServieType, name[2] )
				#LOG_TRACE( 'set[%s] name[%s] ret[%s]'% (cmd,aGroupName,ret) )

			elif aBtn == E_DialogInput09 :
				cmd = 'Remove'
				ret = self.mCommander.Favoritegroup_Remove( aGroupName, self.mChannelListServieType )
				#LOG_TRACE( 'set[%s] name[%s] ret[%s]'% (cmd,aGroupName,ret) )


			self.mMarkList = []
			GuiLock2( True )
			self.setFocusId( self.mCtrlGropCHList.getId() )
			GuiLock2( False )


			#group list
			if self.mEditFavorite :
				idx = 0
				for item in self.mListFavorite:
					retList = []
					retList.append( item )
					idx += 1
					#LOG_TRACE( 'group[%s] ch[%s]'% (self.mEditFavorite[idx], ClassToList('convert', retList)) )



		LOG_TRACE( 'Leave' )

	def SetMarkChanneltoMove(self, aMode, aMove = None, aGroupName = None ) :
		LOG_TRACE( 'Enter' )

		if aMode == FLAG_OPT_MOVE :
		
			number = 0
			retList = []
			markList= []

			if not self.mMarkList :
				lastPos = self.mCtrlListCHList.getSelectedPosition()
				self.mMarkList.append( lastPos )
				#LOG_TRACE('last position[%s]'% lastPos )
			
			self.mMarkList.sort()

			chidx = self.mMarkList[0]
			number = self.mChannelList[chidx].mNumber

			#LOG_TRACE('1====mark[%s] ch[%s]'% (self.mMarkList, ClassToList('convert',self.mChannelList)) )

			#2. get retList
			for idx in self.mMarkList :
				i = int(idx)
				retList.append( self.mChannelList[i] )

			#3. update mark list
			for i in range(len(self.mMarkList)) :
				markList.append( self.mMarkList[0]+i )

			self.mMarkList = []
			self.mMarkList = markList

			#4. init channel list
			ret = False
			if self.mZappingMode == ElisEnum.E_MODE_FAVORITE :
				if aGroupName :
					ret = self.mCommander.FavoriteGroup_MoveChannels( aGroupName, chidx, self.mChannelListServieType, retList )
					#LOG_TRACE( '==========group========' )
			else :
				ret = self.mCommander.Channel_Move( self.mChannelListServieType, number, retList )

			if ret :
				self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )

			#LOG_TRACE('2====mark[%s] ch[%s]'% (self.mMarkList, ClassToList('convert',self.mChannelList)) )
			self.mMoveFlag = True

			GuiLock2(True)
			for idx in self.mMarkList :
				i = int(idx)
				listItem = self.mCtrlListCHList.getListItem(i)
				listItem.setProperty('mark', E_IMG_ICON_MARK)

			self.mCtrlListCHList.selectItem(self.mMarkList[0])
			self.setFocusId( self.mCtrlGropCHList.getId() )

			self.mCtrlLblOpt1.setLabel('[B]OK[/B]')
			self.mCtrlLblOpt2.setLabel('[B]OK[/B]')
			GuiLock2(False)

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
			elif loopE > (len(self.mListItems))-1 : loopE = len(self.mListItems)-1
			#LOG_TRACE('1====mark[%s] ch[%s]'% (self.mMarkList, ClassToList('convert',self.mChannelList)) )

			#2. get retList
			for idx in self.mMarkList :
				i = int(idx)
				retList.append( self.mChannelList[i] )

			#3. update mark list
			if (int(self.mMarkList[0]) + updown) > (len(self.mListItems))-1 :
				#LOG_TRACE('list limit, do not PAGE MOVE!! idx[%s]'% (int(self.mMarkList[0]) + updown) )
				return
			for idx in self.mMarkList :
				idxNew = int(idx) + updown
				markList.append( idxNew )
			self.mMarkList = []
			self.mMarkList = markList

			#4. init channel list
			ret = False
			if self.mZappingMode == ElisEnum.E_MODE_FAVORITE :
				if aGroupName :
					ret = self.mCommander.FavoriteGroup_MoveChannels( aGroupName, chidx, self.mChannelListServieType, retList )
					#LOG_TRACE( '==========group========' )
			else :
				ret = self.mCommander.Channel_Move( self.mChannelListServieType, number, retList )

			if ret :
				self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )
			#LOG_TRACE('2====mark[%s] ch[%s]'% (self.mMarkList, ClassToList('convert',self.mChannelList)) )
			#LOG_TRACE('loopS[%s] loopE[%s]'% (loopS, loopE) )

			#5. refresh section, label move
			for i in range(loopS, loopE+1) :

				number = self.mChannelList[i].mNumber
				name = self.mChannelList[i].mName
				icas = self.mChannelList[i].mIsCA
				lock = self.mChannelList[i].mLocked

				GuiLock2(True)
				listItem = self.mCtrlListCHList.getListItem(i)
				xbmc.sleep(50)

				listItem.setProperty( 'lock', '' )
				listItem.setProperty( 'icas', '' )

				label = str('%s%s %s%s'%( E_TAG_COLOR_GREY, number, name, E_TAG_COLOR_END ) )
				listItem.setLabel(label)

				if lock : listItem.setProperty( 'lock', E_IMG_ICON_LOCK )
				if icas : listItem.setProperty( 'icas', E_IMG_ICON_ICAS )
				listItem.setProperty( 'mark', E_IMG_ICON_MARK )
				xbmc.sleep(50)
				GuiLock2(False)

			#6. erase old mark
			GuiLock2(True)
			if aMove == Action.ACTION_MOVE_UP or aMove == Action.ACTION_MOVE_DOWN :
				listItem = self.mCtrlListCHList.getListItem(oldmark)
				xbmc.sleep(50)
				listItem.setProperty( 'mark', '' )
				self.setFocusId( self.mCtrlGropCHList.getId() )

			else:
				for idx in range(len(self.mMarkList)) :
					idxOld = oldmark + idx
					if idxOld > (len(self.mListItems))-1 : 
						LOG_TRACE('old idx[%s] i[%s]'% (oldmark, idx) )
						continue
					listItem = self.mCtrlListCHList.getListItem( idxOld )
					listItem.setProperty( 'mark', '' )
					self.setFocusId( self.mCtrlGropCHList.getId() )
					xbmc.sleep(50)
			GuiLock2(False)

		LOG_TRACE( 'Leave' )


	def EditSettingWindow( self, aMode, aMove = None ) :
		LOG_TRACE( 'Enter' )

		try:
			if self.mMoveFlag :
				self.SetMarkChanneltoMove( FLAG_OPT_MOVE_OK )
				return

			self.GroupAddDelete( 'get' )

			if aMode == FLAG_OPT_LIST :

				#dialog title
				#select one or one marked : title = channel name
				#select two more : title = 'Edit Channel'
				if self.mChannelList :
					if len(self.mMarkList) > 1 :
						label3 = Msg.Strings( MsgId.LANG_EDIT_CHANNEL )

					else :
						if len(self.mMarkList) == 1 :
							idx = self.mMarkList[0]
							self.mCtrlListCHList.selectItem(idx)
							xbmc.sleep(20)

						label1 = self.mCtrlListCHList.getSelectedItem().getLabel()
						label2 = re.findall('\](.*)\[', label1)
						label3 = label2[0][5:]

					GuiLock2(True)
					dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_EDIT_CHANNEL_LIST )
					dialog.SetValue( FLAG_OPT_LIST, label3, self.mChannelList, self.mEditFavorite )
		 			dialog.doModal()
		 			GuiLock2(False)

		 		else :
					head =  Msg.Strings( MsgId.LANG_INFOMATION )
					line1 = Msg.Strings( MsgId.LANG_NO_CHANNELS )

					ret = xbmcgui.Dialog().ok(head, line1)
					return

			elif aMode == FLAG_OPT_GROUP :
				GuiLock2(True)
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_EDIT_CHANNEL_LIST )
				dialog.SetValue( FLAG_OPT_GROUP, Msg.Strings( MsgId.LANG_GROUP_NAME ), self.mChannelList, self.mEditFavorite )
	 			dialog.doModal()
	 			GuiLock2(False)


			#result editing action
			idxBtn, groupName, isOk = dialog.GetValue( aMode )
			if isOk :
				self.mIsSave |= FLAG_MASK_ADD
				self.GroupAddDelete( 'set', aMode, idxBtn, groupName )

		except Exception, e:
			LOG_TRACE( 'Error except[%s] OPTMODE[%s]'% (e, aMode) )


		LOG_TRACE( 'Leave' )

	def EditSettingWindowContext( self, aMode, aMove = None ) :
		LOG_TRACE( 'Enter' )

		#try:
		if self.mMoveFlag :
			self.SetMarkChanneltoMove( FLAG_OPT_MOVE_OK )
			return

		self.GroupAddDelete( 'get' )

		#default context item
		context1 = []
		context2 = []
		if self.mChannelList :
			context1.append( ContextItem( Msg.Strings( MsgId.LANG_LOCK ) ) )
			context1.append( ContextItem( Msg.Strings( MsgId.LANG_UNLOCK ) ) )
			context1.append( ContextItem( Msg.Strings( MsgId.LANG_SKIP ) ) )
			context1.append( ContextItem( Msg.Strings( MsgId.LANG_UNSKIP ) ) )
			context1.append( ContextItem( Msg.Strings( MsgId.LANG_DELETE ) ) )
			context1.append( ContextItem( Msg.Strings( MsgId.LANG_MOVE ) ) )

		for name in self.mEditFavorite:
			context2.append( ContextItem( name ) )


		if aMode == FLAG_OPT_LIST :

			if self.mChannelList :
				if self.mEditFavorite:
					lblItem = '%s'% Msg.Strings( MsgId.LANG_ADD_TO_FAV )
				else:
					label   = '%s\tNone'% Msg.Strings( MsgId.LANG_ADD_TO_FAV )
					lblItem = str('%s%s%s'%( E_TAG_COLOR_GREY3, label, E_TAG_COLOR_END ) )

				context1.append( ContextItem( lblItem ) )
				GuiLock2(True)
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
				dialog.SetProperty( context1 )
	 			dialog.doModal()
	 			GuiLock2(False)

	 		else :
				head =  Msg.Strings( MsgId.LANG_INFOMATION )
				line1 = Msg.Strings( MsgId.LANG_NO_CHANNELS )

				xbmcgui.Dialog().ok(head, line1)
				return


		elif aMode == FLAG_OPT_GROUP :
			if not self.mChannelList :
				context1 = []

			lblItem1 = '%s'% Msg.Strings( MsgId.LANG_CREATE_NEW_GROUP )

			if self.mEditFavorite:
				lblItem2 = '%s'% Msg.Strings( MsgId.LANG_RENAME_FAV )
				lblItem3 = '%s'% Msg.Strings( MsgId.LANG_DELETE_FAV )
			else:
				label1   = '%s\tNone'% Msg.Strings( MsgId.LANG_RENAME_FAV )
				label2   = '%s\tNone'% Msg.Strings( MsgId.LANG_DELETE_FAV )
				lblItem2 = str('%s%s%s'%( E_TAG_COLOR_GREY3, label1, E_TAG_COLOR_END ) )
				lblItem3 = str('%s%s%s'%( E_TAG_COLOR_GREY3, label2, E_TAG_COLOR_END ) )

			context1.append( ContextItem( lblItem1 ) )
			context1.append( ContextItem( lblItem2 ) )
			context1.append( ContextItem( lblItem3 ) )

			GuiLock2(True)
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context1 )
 			dialog.doModal()
 			GuiLock2(False)


		#result editing action
		selectIdx = dialog.GetSelectedIndex()
		LOG_TRACE('=======select idx[%s]'% selectIdx)

		if selectIdx == -1 :
			LOG_TRACE('CANCEL by context dialog')
			return

		if (aMode == FLAG_OPT_LIST) and (not self.mEditFavorite) and (selectIdx == 6) :
			#can not add to Fav : no favorite group
			LOG_TRACE('Disabled item : selectIdx[%s]'% selectIdx)
			return

		if ((aMode == FLAG_OPT_GROUP) and (not self.mEditFavorite) and (selectIdx == 7)) or \
		   ((aMode == FLAG_OPT_GROUP) and (not self.mEditFavorite) and (selectIdx == 8)) :
			#can not rename / delete : no favorite group
			LOG_TRACE('Disabled item : selectIdx[%s]'% selectIdx)
			return
		#--------------------------------------------------------------- section 1

		publicBtn = (selectIdx * 10) + E_DialogInput01
		groupName = None

		if aMode == FLAG_OPT_GROUP and (not self.mChannelList) :
			#if no Channel then
			#create Fav:7, rename Fav:8, delete Fav:9
			publicBtn = ((selectIdx+6) * 10) + E_DialogInput01

		# add Fav, Ren Fav, Del Fav ==> popup select group
		if aMode == FLAG_OPT_LIST and publicBtn == E_DialogInput07 or \
		   aMode == FLAG_OPT_GROUP and publicBtn == E_DialogInput08 or \
		   aMode == FLAG_OPT_GROUP and publicBtn == E_DialogInput09 :
			GuiLock2(True)
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CONTEXT )
			dialog.SetProperty( context2 )
 			dialog.doModal()
 			GuiLock2(False)

 			grpIdx = dialog.GetSelectedIndex()
 			groupName = self.mEditFavorite[grpIdx]

			if grpIdx == -1 :
				LOG_TRACE('CANCEL by context dialog')
				return

		# Ren Fav, Del Fav ==> popup input group Name
		if aMode == FLAG_OPT_GROUP and publicBtn == E_DialogInput07 or \
		   aMode == FLAG_OPT_GROUP and publicBtn == E_DialogInput08 :
			label = ''
			default = ''
			if publicBtn == E_DialogInput07 :
				#create
				result = ''
				label = Msg.Strings( MsgId.LANG_CREATE_NEW_GROUP )

			elif publicBtn == E_DialogInput08 :
				#rename
				default = groupName
				result = '%d'%grpIdx+':'+groupName+':'
				label = Msg.Strings( MsgId.LANG_RENAME_FAV )

			kb = xbmc.Keyboard( default, label, False )
			kb.doModal()

			name = ''
			name = kb.getText()
			if name :
				groupName = result + name

		LOG_TRACE('mode[%s] btn[%s] groupName[%s]'% (aMode, publicBtn, groupName) )
		#--------------------------------------------------------------- section 2

		self.GroupAddDelete( 'set', aMode, publicBtn, groupName )
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
			#self.EditSettingWindow( mode )        	 # dialog 1
			self.EditSettingWindowContext( mode )	 # dialog 2

		LOG_TRACE( 'Leave' )


	def Close( self ):
		self.mEventBus.Deregister( self )
		self.StopAsyncEPG()

		self.SetVideoRestore()
		self.close()

	def RestartAsyncEPG( self ) :
		self.StopAsyncEPG( )
		self.StartAsyncEPG( )


	def StartAsyncEPG( self ) :
		self.mAsyncTuneTimer = threading.Timer( 0.5, self.AsyncUpdateCurrentEPG ) 				
		self.mAsyncTuneTimer.start()


	def StopAsyncEPG( self ) :
		if self.mAsyncTuneTimer	and self.mAsyncTuneTimer.isAlive() :
			self.mAsyncTuneTimer.cancel()
			del self.mAsyncTuneTimer

		self.mAsyncTuneTimer  = None

	#TODO : must be need timeout schedule
	def AsyncUpdateCurrentEPG( self ) :
		try :
			self.mIsSelect = False
			self.InitEPGEvent()
			self.ResetLabel()
			self.UpdateLabelInfo()

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )


	def KeySearch( self, aKey ) :
		LOG_TRACE( 'Enter' )

		if self.mChannelList == None:
			return -1

		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW:

			GuiLock2(True)
			dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_CHANNEL_JUMP )
			if self.mNavEpg:
				dialog.SetDialogProperty( str(aKey), E_INPUT_MAX, self.mChannelList, self.mNavEpg.mStartTime )
			else :
				dialog.SetDialogProperty( str(aKey), E_INPUT_MAX, self.mChannelList)
			dialog.doModal()
			GuiLock2(False)

			isOK = dialog.IsOK()
			if isOK == E_DIALOG_STATE_YES :
				inputNumber = dialog.GetChannelLast()
				LOG_TRACE('=========== Jump chNum[%s]'% inputNumber)

				self.SetChannelTune( int(inputNumber) )


		LOG_TRACE( 'Leave' )

