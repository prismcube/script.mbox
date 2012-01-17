import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
import pvr.gui.DialogMgr as DiaMgr
from pvr.gui.BaseWindow import BaseWindow, Action
from ElisEnum import ElisEnum
from ElisEventBus import ElisEventBus
from ElisEventClass import *
from pvr.Util import RunThread, GuiLock, GuiLock2, MLOG, LOG_WARN, LOG_TRACE, LOG_ERR
from pvr.PublicReference import GetSelectedLongitudeString, EpgInfoTime, EpgInfoClock, EpgInfoComponentImage, EnumToString, ClassToList, AgeLimit, PincodeLimit, ParseLabelToCh
import pvr.ElisMgr
from ElisProperty import ElisPropertyEnum, ElisPropertyInt

from inspect import currentframe
from pvr.gui.GuiConfig import FooterMask
from pvr.gui.GuiConfig import *
import threading, time, os, re

import pvr.Msg as Msg
import pvr.gui.windows.Define_string as MsgId

FLAG_MASK_ADD  = 0x01
FLAG_MASK_NONE = 0x00
FLAG_SLIDE_OPEN= 0
FLAG_SLIDE_INIT= 1
FLAG_OPT_LIST  = 0
FLAG_OPT_GROUP = 1
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
E_SLIDE_MENU_BACK       = 4

E_IMG_ICON_LOCK   = 'IconLockFocus.png'
E_IMG_ICON_ICAS   = 'IconCas.png'
E_IMG_ICON_MARK   = 'confluence/OverlayWatched.png'
E_IMG_ICON_TITLE1 = 'IconHeaderTitleSmall.png'
E_IMG_ICON_TITLE2 = 'icon_setting_focus.png'

E_TAG_COLOR_RED   = '[COLOR red]'
E_TAG_COLOR_GREY  = '[COLOR grey]'
E_TAG_COLOR_GREY3 = '[COLOR grey3]'
E_TAG_COLOR_END   = '[/COLOR]'

class ChannelListWindow(BaseWindow):

	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		self.mCommander = pvr.ElisMgr.GetInstance().GetCommander()		
		self.mEventBus = pvr.ElisMgr.GetInstance().GetEventBus()

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

		self.mEventId = 0
		self.mLocalTime = 0

		self.mPincodeEnter = FLAG_MASK_NONE
		self.mViewMode = WinMgr.WIN_ID_CHANNEL_LIST_WINDOW
		
	def __del__(self):
		LOG_TRACE( 'destroyed ChannelList' )

		# end thread updateEPGProgress()
		self.mEnableThread = False


	def onInit(self):
		LOG_TRACE( 'Enter' )

		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId )
		LOG_TRACE( 'winID[%d]'% self.mWinId)

		#header
		self.mCtrlHeader1            = self.getControl( 3000 )
		self.mCtrlHeader2            = self.getControl( 3001 )
		self.mCtrlHeader3            = self.getControl( 3002 )
		self.mCtrlHeader4            = self.getControl( 3003 )

		#footer
		self.mCtrlFooter1            = self.getControl( E_CTRL_GROP_FOOTER01 )
		self.mCtrlFooter2            = self.getControl( E_CTRL_GROP_FOOTER02 )
		self.mCtrlFooter3            = self.getControl( E_CTRL_GROP_FOOTER05 )
		self.mCtrlFooter4            = self.getControl( E_CTRL_GROP_FOOTER06 )
		self.mCtrlFooter5            = self.getControl( E_CTRL_GROP_FOOTER07 )
		self.mCtrlFooter6            = self.getControl( E_CTRL_GROP_FOOTER08 )


		self.mCtrlLblPath1           = self.getControl( 10 )
		#self.mCtrlLblPath2           = self.getControl( 11 )
		#self.mCtrlLblPath3           = self.getControl( 12 )
		self.mCtrlLblPath2            = self.getControl( 21 )

		#main menu
		self.mCtrlGropMainmenu       = self.getControl( 100 )
		self.mCtrlBtnMenu            = self.getControl( 101 )
		self.mCtrlListMainmenu       = self.getControl( 102 )
		
		#sub menu list
		self.mCtrlGropSubmenu        = self.getControl( 9001 )
		self.mCtrlListSubmenu        = self.getControl( 202 )

		#ch list
		self.mCtrlGropCHList         = self.getControl( 49 )
		self.mCtrlListCHList         = self.getControl( 50 )

		#info
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
		
		self.mCtrlHeader3.setLabel('')
		self.SetFooter( FooterMask.G_FOOTER_ICON_BACK_MASK | FooterMask.G_FOOTER_ICON_EDIT_MASK | FooterMask.G_FOOTER_ICON_OK_MASK | FooterMask.G_FOOTER_ICON_OPT_MASK | FooterMask.G_FOOTER_ICON_MARK_MASK | FooterMask.G_FOOTER_ICON_OPTGROUP_MASK )

		self.mIsSelect = False
		self.mIsMark = True
		self.mLocalOffset = self.mCommander.Datetime_GetLocalOffset()
		self.mChannelListServieType = ElisEnum.E_SERVICE_TYPE_INVALID
		self.mListItems = []
		self.mZappingMode = ElisEnum.E_MODE_ALL
		self.mChannelListSortMode = ElisEnum.E_SORT_BY_DEFAULT
		self.mChannelList = []
		self.mNavEpg = None
		self.mNavChannel = None
		self.mCurrentChannel = 0
		self.mSlideOpenFlag = False

		#edit mode
		self.mMarkList = []
		self.mDeleteList = []
		self.mSkipList = []
		self.mLockList = []
		self.mEditChannelList = []
		self.mEditFavorite = []
		self.mAddGroupFavorite = []
		self.mDelGroupFavorite = []
		self.mRenGroupFavorite = []


		#initialize get channel list
		self.InitSlideMenuHeader()
		#self.GetSlideMenuHeader( FLAG_SLIDE_INIT )

		try :
			self.mNavChannel = self.mCommander.Channel_GetCurrent()
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

		LOG_TRACE( 'Leave' )

	def onAction(self, aAction):
		#LOG_TRACE( 'Enter' )
		id = aAction.getId()

		if id == Action.ACTION_PREVIOUS_MENU:
			LOG_TRACE( 'goto previous menu' )

		elif id == Action.ACTION_SELECT_ITEM:
			self.GetFocusId()
			LOG_TRACE( 'item select, action ID[%s]'% id )

			if self.mFocusId == self.mCtrlListMainmenu.getId() :
				position = self.mCtrlListMainmenu.getSelectedPosition()
				LOG_TRACE( 'focus[%s] idx_main[%s]'% (self.mFocusId, position) )

				if position == E_SLIDE_MENU_BACK :
					self.mCtrlListCHList.setEnabled(True)
					self.setFocusId( self.mCtrlGropCHList.getId() )

				else :
					self.SubMenuAction( E_SLIDE_ACTION_MAIN, position )
					#self.setFocusId( self.mCtrlListSubmenu.getId() )
					#self.setFocusId( self.mCtrlGropSubmenu.getId() )


		elif id == Action.ACTION_PARENT_DIR :
			LOG_TRACE( 'goto action back' )
			self.onClick( E_CTRL_BTN_FOOTER01 )


		elif id == Action.ACTION_MOVE_RIGHT :
			pass

		elif id == Action.ACTION_MOVE_LEFT :
			self.GetFocusId()
			if self.mFocusId == self.mCtrlListCHList.getId() :
				self.GetSlideMenuHeader( FLAG_SLIDE_OPEN )
				self.mSlideOpenFlag = True


		elif id == Action.ACTION_MOVE_UP or id == Action.ACTION_MOVE_DOWN :
			self.GetFocusId()
			if self.mFocusId == self.mCtrlListCHList.getId() :
				self.mIsSelect = False
				self.InitEPGEvent()

				self.ResetLabel()
				self.UpdateLabelInfo()

			if self.mFocusId == self.mCtrlListMainmenu.getId() :
				#self.onClick( self.mCtrlListMainmenu.getId() )
				position = self.mCtrlListMainmenu.getSelectedPosition()
				self.SubMenuAction( E_SLIDE_ACTION_MAIN, position )

				#self.setFocusId( self.mCtrlListSubmenu.getId() )
				#self.mCtrlListMainmenu.selectItem( self.mSelectMainSlidePosition )
				#self.mCtrlListSubmenu.selectItem( self.mSelectSubSlidePosition )
				#self.setFocusId( self.mCtrlGropSubmenu.getId() )

			elif self.mFocusId >= E_CTRL_BTN_FOOTER01 and self.mFocusId <= E_CTRL_BTN_FOOTER07 :
				self.mCtrlListCHList.setEnabled( True )
				self.setFocusId( self.mCtrlGropCHList.getId() )
				

		elif id == 13: #'x'
			#pass
			#get setting language
			#name=''
			#ret=self.mCommander.enum_GetProp(name)
			#LOG_TRACE( 'language ret[%s] name[%s]'% (ret,name) )

			import locale, codecs, os, xbmcaddon, gettext
			#lc=locale.normalize("fr")
			#lc = locale._build_localename(locale.getdefaultlocale())
			
			#LOG_TRACE( 'lc[%s]'% gettext.NullTranslations.info() )
			#LOG_TRACE( 'lc[%s]'% lc )
			#dlc = locale._print_locale()
			#LOG_TRACE( 'get[%s]'% dlc )
			
			#dlc = ('ko_KR', 'cp949')
			#locale.setlocale(0, 'ISO8859-1')
			#locale.setlocale(0, locale._build_localename(dlc) )
			#locale.resetlocale(0)
			#self.mCtrlHeader2.setLabel(str('[%s]'% lc))
			#import gettext
			#LOCALE_DIR = os.path.dirname(__file__)
			#domain = gettext.bindtextdomain('imdbpy', LOCALE_DIR)			
			#gettext.translation(domain,None,None,None,None, lc)
			
			#LOG_TRACE( 'locale [%s]'% locale._setlocale(0, locale._build_localename( ('fr_FR.ISO8859-1') ) ) )
			#LOG_TRACE( 'locale[%s]'% locale.resetlocale() )

			"""
			cwd='C:\Users\SERVER\AppData\Roaming\XBMC\userdata\guisettings.xml'
			LOG_TRACE( 'getcwd[%s]'% cwd )
			f = open(cwd, 'r')
			import re
			for line in f.readlines():
				ret = re.search('<language>\w*</language>', line)
				if ret != None:
					LOG_TRACE( 'ret[%s]'% ret.group() )
					retstr = ret.group()
					ll = retstr.find('<language>')
					rr = retstr.rfind('</language>')
					retlabel = retstr[10:rr]
					LOG_TRACE( 'retstr[%s]'% retlabel )
					self.mCtrlBtn.setLabel(retlabel)
			f.close()
			"""
			LOG_TRACE( 'cwd[%s]'% xbmc.getLanguage() )

			"""
			import re

			openFile = 'D:\project\elmo\doc\language tool\Language_Prime.csv'
			wFile1 = 'strings.xml'
			LOG_TRACE( 'openFile[%s]'% openFile )
			rf = open(openFile, 'r')
			#wf = open(wFile1, 'w')
			for line in rf.readlines():
				ret = re.search(',', line)
				LOG_TRACE( 'line[%s]'% ret.group() )


			rf.close()
			"""

		#LOG_TRACE( 'Leave' )

	def onClick(self, aControlId):
		LOG_TRACE( 'onclick focusID[%d]'% aControlId )

		if aControlId == self.mCtrlListCHList.getId() :

			if self.mViewMode == WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW :
				try:
					#Mark mode
					if self.mIsMark == True :
						idx = self.mCtrlListCHList.getSelectedPosition()
						self.MarkAddDelete('mark', idx )

						GuiLock2( True )
						self.setFocusId( self.mCtrlGropCHList.getId() )
						self.mCtrlListCHList.selectItem( idx+1 )
						GuiLock2( False )

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
			LOG_TRACE( 'onclick focus[%s] idx_sub[%s]'% (aControlId, position) )

			self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )

		elif aControlId == E_CTRL_BTN_FOOTER01 :
			LOG_TRACE( 'onclick footer back' )

			if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
				self.SaveSlideMenuHeader()

				self.mEnableThread = False
				self.CurrentTimeThread().join()
				self.mCtrlListCHList.reset()
				self.close()

			else :
				self.SaveEditList()
				self.mViewMode = WinMgr.WIN_ID_CHANNEL_LIST_WINDOW
				self.mCtrlListCHList.reset()
				self.InitSlideMenuHeader()
				self.InitChannelList()

				#clear label
				self.ResetLabel()

				#initialize get epg event
				self.InitEPGEvent()
				self.UpdateLabelInfo()

				#Event Register
				#self.mEventBus.Register( self )

		elif aControlId == E_CTRL_BTN_FOOTER02 :
			LOG_TRACE( 'onclick footer ok' )
			if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
				self.SetChannelTune()

			else :
				if self.mIsMark == True :
					self.mIsMark = False
					self.mCtrlLblPath2.setLabel( 'Turn in' )
					self.mCtrlFooter2.setVisible( False )
					self.mCtrlFooter5.setVisible( True )
				else :
					self.mIsMark = True
					self.mCtrlLblPath2.setLabel( 'Mark ON' )
					self.mCtrlFooter2.setVisible( True )
					self.mCtrlFooter5.setVisible( False )


		elif aControlId == E_CTRL_BTN_FOOTER05 :
			LOG_TRACE( 'onclick footer edit' )
			"""
			if self.mIsMark :
				self.mIsMark = False
				self.mEditFavorite = []
				if self.mListFavorite :
					for item in self.mListFavorite:
						self.mEditFavorite.append( item.mGroupName )

			self.onClick(E_CTRL_BTN_FOOTER08)
			return
			"""

			if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
				self.mViewMode = WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW

				try :
					#Event UnRegister
					#self.mEventBus.Deregister( self )

					self.InitSlideMenuHeader()
					self.mCtrlListMainmenu.selectItem( E_SLIDE_ALLCHANNEL )
					#self.SubMenuAction(E_SLIDE_ACTION_MAIN, E_SLIDE_ALLCHANNEL)
					self.mCtrlListSubmenu.selectItem( 0 )
					xbmc.sleep(500)

					self.SubMenuAction(E_SLIDE_ACTION_SUB, ElisEnum.E_MODE_ALL)

					self.mCtrlListCHList.reset()
					self.InitChannelList()

					#copy channel list, use to edit
					self.mEditChannelList = self.mChannelList
					self.mEditFavorite = []
					if self.mListFavorite :
						for item in self.mListFavorite:
							self.mEditFavorite.append( item.mGroupName )


					#clear label
					self.ResetLabel()
					self.UpdateLabelInfo()

				except Exception, e :
					LOG_TRACE( 'Error except[%s]'% e )


		elif aControlId == E_CTRL_BTN_FOOTER06:
			LOG_TRACE( 'onclick footer Opt' )

			try:
				#dialog title
				#select one or one marked : title = channel name
				#select two more : title = 'Edit Channel'
				if len(self.mMarkList) > 1 :
					label3 = 'Edit Channel'

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
				dialog.SetValue( FLAG_OPT_LIST, label3, self.mEditFavorite )
	 			dialog.doModal()
	 			GuiLock2(False)

				idxDialog, idxFavorite, isOkDialog = dialog.GetValue( FLAG_OPT_LIST )

				if idxDialog == E_DialogInput01 :
					self.SetMarkDeleteCh( 'lock', True )
					self.mMarkList = []
					label = 'lock'

				elif idxDialog == E_DialogInput02 :
					self.SetMarkDeleteCh( 'lock', False )
					self.mMarkList = []
					label = 'unlock'

				elif idxDialog == E_DialogInput03 :
					self.SetMarkDeleteCh('skip', True)
					label = 'skip'

				elif idxDialog == E_DialogInput04 :
					self.SetMarkDeleteCh('skip', False)
					label = 'unskip'

				elif idxDialog == E_DialogInput05 :
					self.SetMarkDeleteCh('delete', True)
					label = 'delete'

				elif idxDialog == E_DialogInput06 :
					self.SetMarkDeleteCh('delete', False)
					label = 'undelete'

				GuiLock2( True )
				self.setFocusId( self.mCtrlGropCHList.getId() )
				GuiLock2( False )

				LOG_TRACE( 'ret=======cmd[%s] Mark[%s] Delete[%s] Skip[%s] Lock[%s]'% (label,self.mMarkList,self.mDeleteList,self.mSkipList,self.mLockList) )


			except Exception, e:
				LOG_TRACE( 'Error except[%s]'% e )

			#delete test
			#self.SetMarkDeleteCh('delete')
			#self.mMarkList=[]

		elif aControlId == E_CTRL_BTN_FOOTER08:
			LOG_TRACE( 'onclick footer OptGroup' )
			try:
				GuiLock2(True)
				dialog = DiaMgr.GetInstance().GetDialog( DiaMgr.DIALOG_ID_EDIT_CHANNEL_LIST )
				dialog.SetValue( FLAG_OPT_GROUP, Msg.Strings( MsgId.LANG_GROUP_NAME ), self.mEditFavorite )
	 			dialog.doModal()
	 			GuiLock2(False)

				idxDialog, groupName, isOkDialog = dialog.GetValue( FLAG_OPT_GROUP )
				self.GroupAddDelete( idxDialog, groupName )

			except Exception, e:
				LOG_TRACE( 'Error except[%s]'% e )


		elif aControlId == E_CTRL_BTN_FOOTER07:
			LOG_TRACE( 'onclick footer Mark' )
			if self.mIsMark == True :
				self.mIsMark = False
				self.mCtrlLblPath2.setLabel( 'Turn in' )
				self.mCtrlFooter2.setVisible( False )
				self.mCtrlFooter5.setVisible( True )
			else :
				self.mIsMark = True
				self.mCtrlLblPath2.setLabel( 'Mark ON' )
				self.mCtrlFooter2.setVisible( True )
				self.mCtrlFooter5.setVisible( False )


		LOG_TRACE( 'Leave' )


	def onFocus(self, controlId):
		#LOG_TRACE( 'control %d' % controlId )
		pass

	@GuiLock
	def onEvent(self, aEvent):
		LOG_TRACE( 'Enter' )
		#aEvent.printdebug()

		if self.mWinId == xbmcgui.getCurrentWindowId() :
			if aEvent.getName() == ElisEventCurrentEITReceived.getName() :

				if aEvent.mEventId != self.mEventId :
					if self.mIsSelect == True :
						#on select, clicked
						ret = None
						ret = self.mCommander.Epgevent_GetPresent()
						if ret :
							self.mNavEpg = ret
							self.mEventId = aEvent.mEventId

						#not select, key up/down,
					else :
						ret = self.InitEPGEvent()

					#update label
					self.ResetLabel()
					self.UpdateLabelInfo()


			else :
				LOG_TRACE( 'unknown event[%s]'% aEvent.getName() )
		else:
			LOG_TRACE( 'channellist winID[%d] this winID[%d]'% (self.mWinId, xbmcgui.getCurrentWindowId()) )

		LOG_TRACE( 'Leave' )



	def SetChannelTune( self ) :
		LOG_TRACE( 'Enter' )

		#Turn in
		self.mIsSelect = True

		label = self.mCtrlListCHList.getSelectedItem().getLabel()
		channelNumbr = ParseLabelToCh( self.mViewMode, label )
		LOG_TRACE( 'label[%s] ch[%d]'% (label, channelNumbr) )

		ret = self.mCommander.Channel_SetCurrent( channelNumbr, self.mChannelListServieType)
		#LOG_TRACE( 'MASK[%s] ret[%s]'% (self.mPincodeEnter, ret) )
		if ret == True :
			if self.mPincodeEnter == FLAG_MASK_NONE :
				if self.mCurrentChannel == channelNumbr :
					self.SaveSlideMenuHeader()
					self.mEnableThread = False
					self.CurrentTimeThread().join()
					self.close()

					WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_LIVE_PLATE )
					return

				else :
					pass
					#ToDO : WinMgr.GetInstance().getWindow(WinMgr.WIN_ID_LIVE_PLATE).setLastChannel( self.mCurrentChannel )

		ch = None
		ch = self.mCommander.Channel_GetCurrent()
		if ch :
			self.mNavChannel = ch
			self.mCurrentChannel = self.mNavChannel.mNumber
			self.mCtrlSelectItem.setLabel(str('%s / %s'% (self.mCtrlListCHList.getSelectedPosition()+1, len(self.mListItems))) )
			self.ResetLabel()
			self.UpdateLabelInfo()
			self.PincodeDialogLimit()


		LOG_TRACE( 'Leave' )


	@GuiLock
	def SubMenuAction(self, aAction, aMenuIndex):
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

				#path tree, Mainmenu/Submanu
				#label1 = self.mCtrlListMainmenu.getSelectedItem().getLabel()
				#label1 = enumToString('mode', self.mZappingMode)
				#self.mCtrlLblPath1.setLabel( label1.title() )

		elif aAction == E_SLIDE_ACTION_SUB:
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

				#idx_AllChannel = self.mCtrlListSubmenu.getSelectedPosition()
				#item = self.mListAllChannel[idx_AllChannel]
				#LOG_TRACE( 'cmd[channel_GetList] idx_AllChannel[%s] sort[%s] ch_list[%s]'% (idx_AllChannel, self.mChannelListSortMode, self.mChannelList) )

			elif aMenuIndex == ElisEnum.E_MODE_SATELLITE:
				idx_Satellite = self.mCtrlListSubmenu.getSelectedPosition()
				item = self.mListSatellite[idx_Satellite]
				retPass = self.GetChannelList( self.mChannelListServieType, self.mZappingMode, self.mChannelListSortMode, item.mLongitude, item.mBand, 0, '' )

				LOG_TRACE( 'cmd[channel_GetListBySatellite] idx_Satellite[%s] mLongitude[%s] band[%s]'% ( idx_Satellite, item.mLongitude, item.mBand ) )
				ClassToList( 'print', self.mChannelList )

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

				LOG_TRACE( 'cmd[channel_GetListByFTACas] idxFtaCas[%s]'% idxFtaCas )
				ClassToList( 'print', self.mChannelList )


			elif aMenuIndex == ElisEnum.E_MODE_FAVORITE:
				if self.mListFavorite : 
					idx_Favorite = self.mCtrlListSubmenu.getSelectedPosition()
					item = self.mListFavorite[idx_Favorite]
					retPass = self.GetChannelList( self.mChannelListServieType, self.mZappingMode, self.mChannelListSortMode, 0, 0, 0, item.mGroupName )
					LOG_TRACE( 'cmd[channel_GetListByFavorite] idx_Favorite[%s] list_Favorite[%s]'% ( idx_Favorite, item.mGroupName ) )
					ClassToList( 'print', self.mChannelList )
				else:
					LOG_TRACE( 'cmd[channel_GetListByFavorite] idx_Favorite[%s] list_Favorite[%s]'% ( idx_Favorite, self.mListFavorite ) )

			if retPass == False :
				return

			if len(self.mChannelList) > 0 :
				#channel list update
				#self.mCtrlListCHList.reset()
				self.InitChannelList()

				#path tree, Mainmenu/Submanu
				self.mSelectMainSlidePosition = self.mCtrlListMainmenu.getSelectedPosition()
				self.mSelectSubSlidePosition = self.mCtrlListSubmenu.getSelectedPosition()

				label1 = EnumToString('mode', self.mZappingMode)
				label2 = self.mCtrlListSubmenu.getSelectedItem().getLabel()
				label3 = EnumToString('sort', self.mChannelListSortMode)
				#self.mCtrlLblPath1.setLabel( '%s'% label1.upper() )
				#self.mCtrlLblPath2.setLabel( '%s'% label2.title() ) 
				#self.mCtrlLblPath3.setLabel( 'sort by %s'% label3.title() )
				self.mCtrlLblPath1.setLabel( '%s [COLOR grey3]>[/COLOR] %s [COLOR grey2]/ sort by %s[/COLOR]'% (label1.upper(),label2.title(),label3.title()) )


				#close slide : move to focus channel list
				#self.mCtrlListCHList.setEnabled(True)
				#self.setFocusId( self.mCtrlGropCHList.getId() )

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
			try :
				#LOG_TRACE( 'len[%s]'% len(self.mElisZappingModeInfo) )
				self.mElisZappingModeInfo.printdebug()
				LOG_TRACE( 'satellite[%s]'% ClassToList( 'convert', self.mListSatellite ) )
				LOG_TRACE( 'ftacas[%s]'   % ClassToList( 'convert', self.mListCasList ) )
				LOG_TRACE( 'favorite[%s]' % ClassToList( 'convert', self.mListFavorite ) )

			except Exception, e:
				LOG_TRACE( '[%s:%s]Error exception[%s]'% e )

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
		ret = False

		if self.mSelectMainSlidePosition == self.mLastMainSlidePosition and \
		   self.mSelectSubSlidePosition == self.mLastSubSlidePosition :
			changed = False
		else :
			changed = True

		#is change?
		if changed :
			try :
				#ask save question
				label1 = EnumToString( 'mode', self.mZappingMode )
				label2 = self.mCtrlListSubmenu.getSelectedItem().getLabel()

				head =  Msg.Strings( MsgId.LANG_SETTING_TO_CHANGE_ZAPPING_MODE )
				line1 = '%s / %s'% ( label1.title(), label2.title() )
				line2 = Msg.Strings( MsgId.LANG_DO_YOU_WANT_TO_SAVE_CHANNELS )

				ret = xbmcgui.Dialog().yesno(head, line1, '', line2)
				#LOG_TRACE( 'dialog ret[%s]' % ret )

				#anser is yes
				if ret == True :
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

					#save zapping mode
					ret = self.mCommander.Zappingmode_SetCurrent( retList )
					LOG_TRACE( 'set zappingmode_SetCurrent[%s]'% ret )

			except Exception, e :
				LOG_TRACE( 'Error exception[%s]'% e )

		LOG_TRACE( 'Leave' )


	def SaveEditList( self ) :
		LOG_TRACE( 'Enter' )

		#is change?
		isSetted = len(self.mLockList) + len(self.mSkipList) + len(self.mDeleteList)
		if isSetted > 0 :

			#ask save question
			head =  Msg.Strings( MsgId.LANG_CONFIRM )
			line1 = Msg.Strings( MsgId.LANG_DO_YOU_WANT_TO_SAVE_CHANNELS )

			ret = xbmcgui.Dialog().yesno(head, line1)

			#answer is yes
			if ret :
				for idx in self.mLockList :
					retList = []
					retList.append( self.mEditChannelList[idx] )
					ret = self.mCommander.Channel_Lock( True, retList )
					LOG_TRACE( '======= setLock idx[%s] ret[%s]'% (idx,ret) )

				for idx in self.mSkipList :
					retList = []
					retList.append( self.mEditChannelList[idx] )
					ret = self.mCommander.Channel_Skip( True, retList )
					LOG_TRACE( '======= setSkip idx[%s] ret[%s]'% (idx,ret) )

				for idx in self.mDeleteList :
					retList = []
					retList.append( self.mEditChannelList[idx] )
					ret = self.mCommander.Channel_Delete( retList )
					LOG_TRACE( '======= setDelete idx[%s] ret[%s]'% (idx,ret) )


		LOG_TRACE( 'Leave' )

	def InitSlideMenuHeader( self ) :
		LOG_TRACE( 'Enter' )

		ret = xbmc.getLanguage()
		LOG_TRACE( 'getLanguage[%s]'% ret )


		if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :

			#slide menu disable
			self.mCtrlGropMainmenu.setVisible( True )

			#header init		
			self.mCtrlHeader1.setImage( E_IMG_ICON_TITLE1 )
			self.mCtrlHeader2.setLabel( Msg.Strings(MsgId.LANG_TV_CHANNEL_LIST) )
			self.mCtrlHeader3.setLabel( '' )
			self.mCtrlHeader4.setLabel( '' )

			#footer init
			self.mCtrlFooter2.setVisible( True )
			self.mCtrlFooter3.setVisible( True  )
			self.mCtrlFooter4.setVisible( False )
			self.mCtrlFooter5.setVisible( False )
			self.mCtrlFooter6.setVisible( False )

		else :
			#slide menu disable
			self.mCtrlGropMainmenu.setVisible( False )

			#header init
			self.mCtrlHeader1.setImage( E_IMG_ICON_TITLE2 )
			self.mCtrlHeader2.setLabel( Msg.Strings(MsgId.LANG_TV_EDIT_CHANNEL_LIST) )
			self.mCtrlHeader3.setLabel( '' )
			self.mCtrlHeader4.setLabel( '' )

			#footer init
			self.mCtrlFooter2.setVisible( True )
			self.mCtrlFooter3.setVisible( False )
			self.mCtrlFooter4.setVisible( True )
			self.mCtrlFooter5.setVisible( False )
			self.mCtrlFooter6.setVisible( True )

			return


		#main/sub menu init
		self.mCtrlListMainmenu.reset()
		self.mCtrlListSubmenu.reset()

		#get last zapping mode
		try:
			zappingMode = self.mCommander.Zappingmode_GetCurrent()
			self.mZappingMode           = zappingMode.mMode
			self.mChannelListSortMode   = zappingMode.mSortingMode
			self.mChannelListServieType = zappingMode.mServiceType
			self.mElisZappingModeInfo   = zappingMode
			self.mElisSetZappingModeInfo= zappingMode
			
			#LOG_TRACE( 'zappingmode_GetCurrent len[%s]'% len(zappingMode) )
			#ClassToList( 'print', zappingMode )
			#zappingMode.printdebug()

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
		list_Mainmenu.append( Msg.Strings(MsgId.LANG_BACK)     )
		testlistItems = []
		for item in range( len(list_Mainmenu) ) :
			testlistItems.append( xbmcgui.ListItem(list_Mainmenu[item]) )

		self.mCtrlListMainmenu.addItems( testlistItems )


		#sort list, This is fixed
		self.mListAllChannel = []
		self.mListAllChannel.append( Msg.Strings(MsgId.LANG_ALL_CHANNEL_BY_NUMBER) )
		self.mListAllChannel.append( Msg.Strings(MsgId.LANG_ALL_CHANNEL_BY_ALPHABET) )
		self.mListAllChannel.append( 'All Channel by HD/SD' )
		LOG_TRACE( 'mListAllChannel[%s]'% self.mListAllChannel )

		try :
			#satellite longitude list
			self.mListSatellite = self.mCommander.Satellite_GetConfiguredList( ElisEnum.E_SORT_NAME )
			ClassToList( 'print', self.mListSatellite )

			#FTA list
			self.mListCasList = self.mCommander.Fta_cas_GetList( ElisEnum.E_SERVICE_TYPE_TV )
			ClassToList( 'print', self.mListCasList )

			#Favorite list
			self.mListFavorite = self.mCommander.Favorite_GetList( ElisEnum.E_SERVICE_TYPE_TV )
			ClassToList( 'print', self.mListFavorite )

			"""
			#print
			retList = []
			retList.append( self.mListSatellite )
			LOG_TRACE( 'Satellite_GetConfiguredList[%s]'% ClassToList( 'convert', retList ) )
			retList = []
			retList.append( self.mListCasList )
			LOG_TRACE( 'Fta_cas_GetList[%s]'% ClassToList( 'convert', retList ) )
			retList = []
			retList.append( self.mListFavorite )
			LOG_TRACE( 'Favorite_GetList[%s]'% ClassToList( 'convert', retList ) )
			"""

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

			#TODO
			#display dialog


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
		#label1 = self.mCtrlListMainmenu.getSelectedItem().getLabel()
		label1 = EnumToString('mode', self.mZappingMode)
		label2 = self.mCtrlListSubmenu.getSelectedItem().getLabel()
		label3 = EnumToString('sort', self.mChannelListSortMode)
		#self.mCtrlLblPath1.setLabel( '%s'% label1.upper() )
		#self.mCtrlLblPath2.setLabel( '%s'% label2.title() ) 
		#self.mCtrlLblPath3.setLabel( 'sort by %s'% label3.title() )
		self.mCtrlLblPath1.setLabel( '%s [COLOR grey3]>[/COLOR] %s [COLOR grey2]/ sort by %s[/COLOR]'% (label1.upper(),label2.title(),label3.title()) )
		
		self.GetSlideMenuHeader( FLAG_SLIDE_INIT )
		self.mLastMainSlidePosition = self.mSelectMainSlidePosition
		self.mLastSubSlidePosition = self.mSelectSubSlidePosition


		#get channel list by last on zapping mode, sorting, service type
		self.mNavChannel = None
		self.mChannelList = None
		self.mChannelList = self.mCommander.Channel_GetList( self.mChannelListServieType, self.mZappingMode, self.mChannelListSortMode )
		#self.GetChannelList(self.mChannelListServieType, self.mZappingMode, self.mChannelListSortMode, 0, 0, 0, '')

		if self.mChannelList :
			LOG_TRACE( 'zappingMode[%s] sortMode[%s] serviceType[%s]'%  \
				( EnumToString('mode', self.mZappingMode),         \
				  EnumToString('sort', self.mChannelListSortMode), \
				  EnumToString('type', self.mChannelListServieType)) )
			ClassToList( 'print', self.mChannelList )

		LOG_TRACE( 'Leave' )


	def InitChannelList(self):
		LOG_TRACE( 'Enter' )

		chList = ClassToList( 'convert', self.mChannelList )
		if len(chList) < 1 :
			LOG_TRACE( 'no data, self.mChannelList len[%s]'% len(self.mChannelList) )
			ClassToList( 'print', self.mChannelList )
			return 

		lblColorS = E_TAG_COLOR_GREY
		lblColorE = E_TAG_COLOR_END
		self.mListItems = []
		for ch in self.mChannelList:

			try:
				if self.mViewMode == WinMgr.WIN_ID_CHANNEL_LIST_WINDOW :
					#skip ch
					if ch.mSkipped == True :
						continue
					listItem = xbmcgui.ListItem( "%04d %s"%( ch.mNumber, ch.mName ), "-", "-", "-", "-" )

				else :
					#skip ch
					if ch.mSkipped == True :
						lblColorS = E_TAG_COLOR_GREY3
					else:
						lblColorS = E_TAG_COLOR_GREY

					listItem = xbmcgui.ListItem( "%s%04d %s%s"%( lblColorS, ch.mNumber, ch.mName, lblColorE ), "-", "-", "-", "-" )

			except Exception, e:
				LOG_TRACE( '=========== except[%s]'% e )


			if ch.mLocked  : listItem.setProperty('lock', E_IMG_ICON_LOCK)
			if ch.mIsCA    : listItem.setProperty('icas', E_IMG_ICON_ICAS)

			self.mListItems.append(listItem)

		self.mCtrlListCHList.addItems( self.mListItems )


		#get last channel
		ret = None
		ret = self.mCommander.Channel_GetCurrent()
		if ret :
			self.mNavChannel = ret
			self.mCurrentChannel = self.mNavChannel.mNumber

		#detected to last focus
		chindex = 0;
		for ch in self.mChannelList:
			if ch.mNumber == self.mNavChannel.mNumber :
				break
			chindex += 1

		self.mCtrlListCHList.selectItem( chindex )

		#select item idx, print GUI of 'current / total'
		self.mCtrlSelectItem.setLabel(str('%s / %s'% (self.mCtrlListCHList.getSelectedPosition()+1, len(self.mListItems))) )

		LOG_TRACE( 'Leave' )


	def ResetLabel(self):
		LOG_TRACE( 'Enter' )
		#chListInfo = ClassToList( 'convert', self.mNavChannel )
		#LOG_TRACE( 'currentChannel[%s]'% chListInfo )


		self.mCtrlProgress.setPercent(0)
		self.mCtrlProgress.setVisible(False)
		self.mPincodeEnter = FLAG_MASK_NONE

		self.mCtrlSelectItem.setLabel(str('%s / %s'% (self.mCtrlListCHList.getSelectedPosition()+1, len(self.mListItems))) )
		#self.mCtrlChannelName.setLabel('')
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

		ret = None

		try :
			if self.mIsSelect == True :
				ret = self.mCommander.Epgevent_GetPresent()
				xbmc.sleep(500)
				if ret :
					self.mNavEpg = ret
					ret.printdebug()

			else :
				label = self.mCtrlListCHList.getSelectedItem().getLabel()
				channelNumbr = ParseLabelToCh( self.mViewMode, label )
				LOG_TRACE( 'label[%s] ch[%d]'% (label, channelNumbr) )

				for ch in self.mChannelList:
					if ch.mNumber == channelNumbr :
						self.mNavChannel = None
						self.mNavChannel = ch
						LOG_TRACE( 'found ch: getlabel[%s] ch[%s]'% (channelNumbr, ch.mNumber ) )

						gmtFrom = self.mLocalTime - self.mLocalOffset
						gmtUntil= 0
						maxCount= 1
						ret = self.mCommander.Epgevent_GetList( ch.mSid, ch.mTsid, ch.mOnid, gmtFrom, gmtUntil, maxCount )
						xbmc.sleep(500)
						if ret :
							self.mNavEpg = ret
							ret.printdebug()


		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )

		LOG_TRACE( 'Leave' )


	def UpdateServiceType( self, aTvType ):
		LOG_TRACE( 'Enter' )
		LOG_TRACE( 'serviceType[%s]' % aTvType )

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
	def UpdateLabelInfo( self ):
		LOG_TRACE( 'Enter' )

		#update channel name
		if self.mIsSelect == True :
			label = self.UpdateServiceType( self.mNavChannel.mServiceType )
			self.mCtrlChannelName.setLabel( str('%s - %s'% (label, self.mNavChannel.mName )) )

		#update longitude info
		satellite = self.mCommander.Satellite_GetByChannelNumber( self.mNavChannel.mNumber, self.mNavChannel.mServiceType )
		ret = GetSelectedLongitudeString( satellite.mLongitude, satellite.mName )
		self.mCtrlLongitudeInfo.setLabel( ret )

		#update lock-icon visible
		if self.mNavChannel.mLocked :
				self.mCtrlLockedInfo.setVisible( True )
				self.mPincodeEnter |= FLAG_MASK_ADD


		#update career info
		if self.mNavChannel.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBS:
			value1 = self.mNavChannel.mCarrier.mDVBS.mPolarization
			value2 = self.mNavChannel.mCarrier.mDVBS.mFrequency
			value3 = self.mNavChannel.mCarrier.mDVBS.mSymbolRate

			polarization = EnumToString( 'Polarization', value1 )
			careerLabel = '%s MHz, %s KS/S, %s'% (value2, value3, polarization)
			self.mCtrlCareerInfo.setLabel(careerLabel)

		elif careerType == ElisEnum.E_CARRIER_TYPE_DVBT:
			pass
		elif careerType == ElisEnum.E_CARRIER_TYPE_DVBC:
			pass
		elif careerType == ElisEnum.E_CARRIER_TYPE_INVALID:
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
				#self.mNavEpg.printdebug()
				self.mCtrlEventName.setLabel( self.mNavEpg.mEventName )
				ret = EpgInfoTime( self.mLocalOffset, self.mNavEpg.mStartTime, self.mNavEpg.mDuration )
				self.mCtrlEventTime.setLabel( str('%s%s'% (ret[0], ret[1])) )

				#visible progress
				self.mCtrlProgress.setVisible( True )

				#component
				imagelist = EpgInfoComponentImage( self.mNavEpg )				
				if len(imagelist) == 1:
					self.mCtrlServiceTypeImg1.setImage(imagelist[0])
				elif len(imagelist) == 2:
					self.mCtrlServiceTypeImg1.setImage(imagelist[0])
					self.mCtrlServiceTypeImg2.setImage(imagelist[1])
				elif len(imagelist) == 3:
					self.mCtrlServiceTypeImg1.setImage(imagelist[0])
					self.mCtrlServiceTypeImg2.setImage(imagelist[1])
					self.mCtrlServiceTypeImg3.setImage(imagelist[2])
				else:
					self.mCtrlServiceTypeImg1.setImage('')
					self.mCtrlServiceTypeImg2.setImage('')
					self.mCtrlServiceTypeImg3.setImage('')


				#is Age? agerating check
				isLimit = AgeLimit( self.mCommander, self.mNavEpg.mAgeRating )
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
				msg1 = Msg.Strings(MsgId.LANG_INPUT_PIN_CODE)
				#msg2 = Msg.Strings(MsgId.LANG_CURRENT_PIN_CODE)

				inputPin = ''
				inputPin = xbmcgui.Dialog().numeric( 0, msg1 )
				stbPin = PincodeLimit( self.mCommander, inputPin )
				if inputPin == None or inputPin == '' :
					inputPin = ''

				#LOG_TRACE( 'mask[%s] inputPin[%s] stbPin[%s]'% (self.mPincodeEnter, inputPin, stbPin) )

				if inputPin == str('%s'% stbPin) :
					self.mPincodeEnter = FLAG_MASK_NONE
					LOG_TRACE( 'Pincode success' )

			except Exception, e:
				LOG_TRACE( 'Error exception[%s]'% e )


		LOG_TRACE( 'Leave' )

	"""
	def OptDialogLimit( self ) :
		LOG_TRACE( 'Enter' )

		try :
			msg1 = 'OPT CH number'
			msgList=[]
			msgList.append('Lock')
			msgList.append('Skip')
			msgList.append('Move')
			msgList.append('Delete')
			#msgList.append('Add to Fav.Group')
			msgList.append(self.mListFavorite)
			msgList.append('Start Block Selection')

			ret = xbmcgui.Dialog().select(msg1, msgList)

			LOG_TRACE('======== ret[%s]'% ret)
		
		except Exception, e:
			LOG_TRACE( 'Error exception[%s]'% e )


		LOG_TRACE( 'Leave' )
	"""

	@RunThread
	def CurrentTimeThread(self):
		LOG_TRACE( 'begin_start thread' )

		loop = 0
		#rLock = threading.RLock()
		while self.mEnableThread:
			#LOG_TRACE( 'repeat <<<<' )

			#progress

			if  ( loop % 10 ) == 0 :
				LOG_TRACE( 'loop=%d'% loop )
				self.UpdateLocalTime( )


			#local clock
			ret = EpgInfoClock(FLAG_CLOCKMODE_ADMYHM, self.mLocalTime, loop)
			self.mCtrlHeader3.setLabel(ret[0])
			self.mCtrlHeader4.setLabel(ret[1])

			#self.nowTime += 1
			xbmc.sleep(1000)
			loop += 1

		LOG_TRACE( 'leave_end thread' )


	@GuiLock
	def UpdateLocalTime( self ) :
		LOG_TRACE( 'Enter' )
		
		try:
			self.mLocalTime = self.mCommander.Datetime_GetLocalTime()


			if self.mNavEpg :
				endTime = self.mNavEpg.mStartTime + self.mNavEpg.mDuration
		
				pastDuration = endTime - self.mLocalTime
				if pastDuration < 0 :
					pastDuration = 0

				if self.mNavEpg.mDuration > 0 :
					percent = pastDuration * 100/self.mNavEpg.mDuration
				else :
					percent = 0

				#LOG_TRACE( 'percent=%d'% percent )
				self.mCtrlProgress.setPercent( percent )

		except Exception, e :
			LOG_TRACE( 'Error exception[%s]'% e )
			#self.mLocalTime = 0

		LOG_TRACE( 'Leave' )


	@GuiLock
	def SetMarkDeleteCh( self, aMode, aEnabled=True ) :
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
					else :
						#disible lock
						listItem.setProperty('lock', '')

					self.MarkAddDelete( 'lock', lastPos, aEnabled )

					#mark remove
					listItem.setProperty('mark', '')


				#label color
				else :
					#remove tag [COLOR ...]label[/COLOR]
					label1 = self.mCtrlListCHList.getSelectedItem().getLabel()
					label2 = re.findall('\](.*)\[', label1)

					if aMode.lower() == 'delete' :
						if aEnabled :
							label3= str('%s%s%s'%( E_TAG_COLOR_RED, label2[0], E_TAG_COLOR_END ) )
						else :
							label3= str('%s%s%s'%( E_TAG_COLOR_GREY, label2[0], E_TAG_COLOR_END ) )
						self.mCtrlListCHList.getSelectedItem().setLabel(label3)
						self.MarkAddDelete( 'delete', lastPos, aEnabled )

					elif aMode.lower() == 'skip' :
						if aEnabled :
							label3= str('%s%s%s'%( E_TAG_COLOR_GREY3, label2[0], E_TAG_COLOR_END ) )
						else :
							label3= str('%s%s%s'%( E_TAG_COLOR_GREY, label2[0], E_TAG_COLOR_END ) )
						self.mCtrlListCHList.getSelectedItem().setLabel(label3)
						self.MarkAddDelete( 'skip', lastPos, aEnabled )

			else :
				#----------------> 2.set mark list all <-------------
				for idx in self.mMarkList :
					self.mCtrlListCHList.selectItem(idx)
					xbmc.sleep(50)

					#icon toggle
					if aMode.lower() == 'lock' :
						listItem = self.mCtrlListCHList.getListItem(idx)

						#lock toggle: disable
						if aEnabled :
							listItem.setProperty('lock', E_IMG_ICON_LOCK)
						else :
							listItem.setProperty('lock', '')

						self.MarkAddDelete( 'lock', idx, aEnabled )

						#mark remove
						listItem.setProperty('mark', '')

					#label color
					else :
						#strip tag [COLOR ...]label[/COLOR]
						label1 = self.mCtrlListCHList.getSelectedItem().getLabel()
						label2 = re.findall('\](.*)\[', label1)

						if aMode.lower() == 'delete' :
							if aEnabled :
								label3= str('%s%s%s'%( E_TAG_COLOR_RED, label2[0], E_TAG_COLOR_END ) )
							else :
								label3= str('%s%s%s'%( E_TAG_COLOR_GREY, label2[0], E_TAG_COLOR_END ) )
							self.mCtrlListCHList.getSelectedItem().setLabel(label3)
							self.MarkAddDelete( 'delete', idx, aEnabled )

							LOG_TRACE( 'idx[%s] 1%s 2%s 3%s'% (idx, label1,label2,label3) )

						elif aMode.lower() == 'skip' :
							if aEnabled :
								label3= str('%s%s%s'%( E_TAG_COLOR_GREY3, label2[0], E_TAG_COLOR_END ) )
							else :
								label3= str('%s%s%s'%( E_TAG_COLOR_GREY, label2[0], E_TAG_COLOR_END ) )
							self.mCtrlListCHList.getSelectedItem().setLabel(label3)
							self.MarkAddDelete( 'skip', idx, aEnabled )

							LOG_TRACE( 'idx[%s] 1%s 2%s 3%s'% (idx, label1,label2,label3) )


				#recovery last focus
				self.mCtrlListCHList.selectItem(lastPos)


		except Exception, e:
			LOG_TRACE( '============except[%s]'% e )

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
				self.mDeleteList.pop(idx)

		elif aMode.lower() == 'skip' :
			idx = 0
			isExist = False

			#aready mark is mark delete
			for i in self.mSkipList :
				if i == aPos :
					isExist = True
					break
				idx += 1

			if aEnabled :
				#skip, append item when not exist
				if isExist == False : 
					self.mSkipList.append( aPos )
			else :
				#unskip, remove item
				self.mSkipList.pop(idx)

		elif aMode.lower() == 'lock' :
			idx = 0
			isExist = False

			#aready mark is mark delete
			for i in self.mLockList :
				if i == aPos :
					isExist = True
					break
				idx += 1

			if aEnabled :
				#Lock, append item when not exist
				if isExist == False : 
					self.mLockList.append( aPos )		
			else :
				#unLock, remove item
				self.mLockList.pop(idx)


		LOG_TRACE( 'MarkList[%s]'% self.mMarkList )
		LOG_TRACE( 'mDeleteList[%s]'% self.mDeleteList )
		LOG_TRACE( 'mSkipList[%s]'% self.mSkipList )
		LOG_TRACE( 'mLockList[%s]'% self.mLockList )

		LOG_TRACE( 'Leave' )


	def GroupAddDelete( self, aBtn, aGroupName ) :
		LOG_TRACE( 'Enter' )
		if aBtn == E_DialogInput01 :
			#create new group

			#find, edit list
			if self.mEditFavorite :
				isExist = False
				for idx in range(len(self.mEditFavorite)) :
					if aGroupName == self.mEditFavorite[idx] :
						isExist = True
						break

				#new group add ?
				if isExist == False :
					self.mEditFavorite.append( aGroupName )

					#find, orignal favorite group
					if self.mListFavorite :
						isExist = False
						for item in self.mListFavorite :
							if aGroupName == item.mGroupName :
								isExist = True
								break

						#new group add ?
						if isExist == False :
							self.mAddGroupFavorite.append( aGroupName )


					#find, add list
					if self.mAddGroupFavorite :
						isExist = False
						for idx in range(len(self.mAddGroupFavorite)) :
							if aGroupName == self.mAddGroupFavorite[idx] :
								isExist = True
								break

						#new group add ?
						if isExist == False :
							self.mAddGroupFavorite.append( aGroupName )

				else :
					LOG_TRACE ( 'Exist Group[%s], no append!!'% aGroupName )
			else :
				self.mEditFavorite.append( aGroupName )
				self.mAddGroupFavorite.append( aGroupName )


		elif aBtn == E_DialogInput02 :
			#rename group

			#parse idx, source name, rename
			name = re.split(':', aGroupName)

			#find, edit list
			if self.mEditFavorite :
				isExist = False
				for idx in range(len(self.mEditFavorite)) :
					if name[1] == self.mEditFavorite[idx] :
						isExist = True
						break

				#find yes? rename
				if isExist == True :
					self.mEditFavorite[idx] = name[2]

			#find, add list
			if self.mAddGroupFavorite :
				isExist = False	
				for idx in range(len(self.mAddGroupFavorite)) :
					if name[1] == self.mAddGroupFavorite[idx] :
						isExist = True
						break

				#find yes? rename
				if isExist == True :
					self.mAddGroupFavorite[idx] = name[2]


			#find, orignal favorite group
			if self.mListFavorite :
				isExist = False
				idx = 0
				for item in self.mListFavorite :
					if name[1] == item.mGroupName :
						isExist = True
						break
					idx += 1

				#find yes? add rename list
				if isExist == True :
					#find, del list
					if self.mDelGroupFavorite :
						isExist = False	
						for idx in range(len(self.mDelGroupFavorite)) :
							if name[1] == self.mDelGroupFavorite[idx] :
								isExist = True
								break

						#find yes? rename
						if isExist == False :
							self.mRenGroupFavorite.append( aGroupName )

					else :
						self.mRenGroupFavorite.append( aGroupName )


		elif aBtn == E_DialogInput03 :
			#delete group

			#find, edit list
			if self.mEditFavorite :
				isExist = False
				for idx in range(len(self.mEditFavorite)) :
					if aGroupName == self.mEditFavorite[idx] :
						isExist = True
						break

				#find yes? delete
				if isExist == True :
					self.mEditFavorite.pop(idx)

			#find, add list
			if self.mAddGroupFavorite :
				isExist = False	
				for idx in range(len(self.mAddGroupFavorite)) :
					if aGroupName == self.mAddGroupFavorite[idx] :
						isExist = True
						break

				#find yes? delete
				if isExist == True :
					self.mAddGroupFavorite.pop(idx)

			#find, ren list
			if self.mRenGroupFavorite :
				isExist = False
				for idx in range(len(self.mRenGroupFavorite)) :
					#parse idx, source name, rename
					name = re.split(':', self.mRenGroupFavorite[idx])

					if aGroupName == name[2] :
						isExist = True
						break

				#find yes? add delete list
				if isExist == True :
					self.mRenGroupFavorite.pop(idx)
					self.mDelGroupFavorite.append( name[1] )

			#find, orignal favorite group
			if self.mListFavorite :
				isExist = False
				for item in self.mListFavorite :
					if aGroupName == item.mGroupName :
						isExist = True
						break

				#find yes? add delete list
				if isExist == True :
					self.mDelGroupFavorite.append( aGroupName )

		LOG_TRACE( '=======result: edit[%s] add[%s] ren[%s] del[%s]'% (self.mEditFavorite, self.mAddGroupFavorite, self.mRenGroupFavorite, self.mDelGroupFavorite) )
		LOG_TRACE( 'Leave' )


