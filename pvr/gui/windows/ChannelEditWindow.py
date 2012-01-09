import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
from pvr.gui.BaseWindow import BaseWindow, Action
from ElisEnum import ElisEnum
from ElisEventBus import ElisEventBus
from ElisEventClass import *
from pvr.Util import RunThread, GuiLock, MLOG, LOG_WARN, LOG_TRACE, LOG_ERR
from pvr.PublicReference import GetSelectedLongitudeString, EpgInfoTime, EpgInfoClock, EpgInfoComponentImage, EnumToString, ClassToList, AgeLimit
import pvr.ElisMgr
from ElisProperty import ElisPropertyEnum, ElisPropertyInt

from inspect import currentframe
from pvr.gui.GuiConfig import FooterMask
import threading, time, os

import pvr.Msg as Msg
import pvr.gui.windows.Define_string as MsgId

FLAG_MASK_ADD  = 0x01
FLAG_MASK_NONE = 0x00
FLAG_SLIDE_OPEN= 0
FLAG_SLIDE_INIT= 1
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
		self.mCtrlFooter1            = self.getControl( 3101 )
		self.mCtrlFooter2            = self.getControl( 3111 )
		self.mCtrlFooter3            = self.getControl( 3141 )

		self.mCtrlLblPath1           = self.getControl( 10 )
		self.mCtrlLblPath2           = self.getControl( 11 )
		self.mCtrlLblPath3           = self.getControl( 12 )

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

		self.mEpgRecvPermission = True
		self.mLocalOffset = self.mCommander.Datetime_GetLocalOffset()
		self.mChannelListServieType = ElisEnum.E_SERVICE_TYPE_INVALID
		self.mListItems = []
		self.mZappingMode = ElisEnum.E_MODE_ALL
		self.mChannelListSortMode = ElisEnum.E_SORT_BY_DEFAULT
		self.mChannelList = []
		self.mNavEpg = None
		self.mNavChannel = None
		self.mSlideOpenFlag = False


		#initialize get channel list
		self.InitSlideMenuHeader()
		#self.GetSlideMenuHeader( FLAG_SLIDE_INIT )

		try :
			#self.mCurrentChannel = self.mCommander.Channel_GetCurrent()
			self.mNavChannel = self.mCommander.Channel_GetCurrent()
			
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
		focusId = self.getFocusId()
		#print '[%s:%s]aActionID[%d]'% (self.__file__, currentframe().f_lineno, id) 

		if id == Action.ACTION_PREVIOUS_MENU:
			LOG_TRACE( 'goto previous menu' )

		elif id == Action.ACTION_SELECT_ITEM:
			LOG_TRACE( 'item select, action ID[%s]'% id )

			if focusId == self.mCtrlListMainmenu.getId() :
				position = self.mCtrlListMainmenu.getSelectedPosition()
				LOG_TRACE( 'focus[%s] idx_main[%s]'% (focusId, position) )

				if position == E_SLIDE_MENU_BACK :
					self.mCtrlListCHList.setEnabled(True)
					self.setFocusId( self.mCtrlGropCHList.getId() )

				else :
					self.SubMenuAction( E_SLIDE_ACTION_MAIN, position )
					#self.setFocusId( self.mCtrlListSubmenu.getId() )
					#self.setFocusId( self.mCtrlGropSubmenu.getId() )


		elif id == Action.ACTION_PARENT_DIR :
			LOG_TRACE( 'goto action back' )

			self.SaveSlideMenuHeader()

			self.mEnableThread = False
			self.CurrentTimeThread().join()
			self.mCtrlListCHList.reset()
			self.close()


		elif id == Action.ACTION_MOVE_RIGHT :
			"""
			if focusId == self.mCtrlListMainmenu.getId() :
				position = self.mCtrlListMainmenu.getSelectedPosition()

				#this position's 'Back'
				if position == E_SLIDE_MENU_BACK :
					self.mCtrlListCHList.setEnabled( True )
					self.setFocusId( self.mCtrlGropCHList.getId() )

				else :
					self.onClick( self.mCtrlListMainmenu.getId() )

			elif focusId == self.mCtrlListSubmenu.getId() :
				self.onClick( self.mCtrlListMainmenu.getId() )
			"""
			pass
		elif id == Action.ACTION_MOVE_LEFT :
			if focusId == self.mCtrlListCHList.getId() :
				self.GetSlideMenuHeader( FLAG_SLIDE_OPEN )
				self.mSlideOpenFlag = True


		elif id == Action.ACTION_MOVE_UP or id == Action.ACTION_MOVE_DOWN :
			if focusId == self.mCtrlListCHList.getId() :
				self.mEpgRecvPermission = False
				self.InitEPGEvent()

				self.ResetLabel()
				self.UpdateLabelInfo()

			if focusId == self.mCtrlListMainmenu.getId() :
				#self.onClick( self.mCtrlListMainmenu.getId() )
				position = self.mCtrlListMainmenu.getSelectedPosition()
				self.SubMenuAction( E_SLIDE_ACTION_MAIN, position )

				#self.setFocusId( self.mCtrlListSubmenu.getId() )
				#self.mCtrlListMainmenu.selectItem( self.mSelectMainSlidePosition )
				#self.mCtrlListSubmenu.selectItem( self.mSelectSubSlidePosition )
				#self.setFocusId( self.mCtrlGropSubmenu.getId() )

			elif focusId >= self.mCtrlFooter1.getId() and focusId <= self.mCtrlFooter3.getId() :
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
			label = self.mCtrlListCHList.getSelectedItem().getLabel()
			channelNumbr = int(label[:4])
			ret = self.mCommander.Channel_SetCurrent( channelNumbr, self.mChannelListServieType)

			if ret == True :
				if self.mPincodeEnter == FLAG_MASK_NONE :
					#if self.mCurrentChannel.mNumber == channelNumbr :
					if self.mNavChannel.mNumber == channelNumbr :
						self.SaveSlideMenuHeader()
						self.mEnableThread = False
						self.CurrentTimeThread().join()
						self.close()

						WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CHANNEL_BANNER )

					else :
						pass
						#ToDO : WinMgr.GetInstance().getWindow(WinMgr.WIN_ID_CHANNEL_BANNER).setLastChannel( self.mCurrentChannel )

				#self.mCurrentChannel = self.mCommander.Channel_GetCurrent()
				self.mNavChannel = self.mCommander.Channel_GetCurrent()

			self.mEpgRecvPermission = True
			self.mCtrlSelectItem.setLabel(str('%s / %s'% (self.mCtrlListCHList.getSelectedPosition()+1, len(self.mListItems))) )
			self.ResetLabel()
			self.UpdateLabelInfo()

		elif aControlId == self.mCtrlBtnMenu.getId() or aControlId == self.mCtrlListMainmenu.getId() :
			#list view
			LOG_TRACE( '#############################' )

		elif aControlId == self.mCtrlListSubmenu.getId() :
			#list action
			position = self.mZappingMode
			LOG_TRACE( 'onclick focus[%s] idx_sub[%s]'% (aControlId, position) )

			self.SubMenuAction( E_SLIDE_ACTION_SUB, self.mZappingMode )

		elif aControlId == self.mCtrlFooter1.getId() :
			LOG_TRACE( 'onclick footer back' )
			self.SaveSlideMenuHeader()

			self.mEnableThread = False
			self.CurrentTimeThread().join()
			self.mCtrlListCHList.reset()
			self.close( )

		elif aControlId == self.mCtrlFooter2.getId() :
			LOG_TRACE( 'onclick footer ok' )
			self.onClick( self.mCtrlListCHList.getId() )

		elif aControlId == self.mCtrlFooter3.getId() :
			LOG_TRACE( 'onclick footer edit' )
			self.SaveSlideMenuHeader()

			self.mEnableThread = False
			self.CurrentTimeThread().join()

			#ToDO: WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW )

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
					if self.mEpgRecvPermission == True :
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
				for itemClass in self.mListFavorite:
					testlistItems.append( xbmcgui.ListItem(itemClass.mGroupName) )

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
				idx_Favorite = self.mCtrlListSubmenu.getSelectedPosition()
				item = self.mListFavorite[idx_Favorite]
				retPass = self.GetChannelList( self.mChannelListServieType, self.mZappingMode, self.mChannelListSortMode, 0, 0, 0, item.mGroupName )

				LOG_TRACE( 'cmd[channel_GetListByFavorite] idx_Favorite[%s] list_Favorite[%s]'% ( idx_Favorite, item.mGroupName ) )
				ClassToList( 'print', self.mChannelList )


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
				self.mCtrlLblPath1.setLabel( '%s'% label1.upper() )
				self.mCtrlLblPath2.setLabel( '%s'% label2.title() ) 
				self.mCtrlLblPath3.setLabel( 'sort by %s'% label3.title() ) 

				#close slide : move to focus channel list
				self.mCtrlListCHList.setEnabled(True)
				self.setFocusId( self.mCtrlGropCHList.getId() )

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

				head =  Msg.Strings( MsgId.LANG_TO_CHANGE_ZAPPING_MODE )
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


	def InitSlideMenuHeader(self) :
		LOG_TRACE( 'Enter' )

		#header init
		self.mCtrlHeader1.setImage('IconHeaderTitleSmall.png')
		#self.mCtrlHeader2.setLabel('TV-Channel List')
		self.mCtrlHeader2.setLabel(Msg.Strings(MsgId.LANG_TV_EDIT_CHANNEL_LIST))

		#self.mCtrlLbl.setLabel( m.strings(mm.LANG_LANGUAGE) )
		ret = xbmc.getLanguage()
		LOG_TRACE( 'getLanguage[%s]'% ret )
		#self.mCtrlBtn.setLabel(ret)

		self.mCtrlHeader3.setLabel('')		
		self.mCtrlHeader4.setLabel('')

		#footer init
		#self.setProperty('WindowType', 'ChannelList')
		self.SetFooter( FooterMask.G_FOOTER_ICON_BACK_MASK | FooterMask.G_FOOTER_ICON_OK_MASK | FooterMask.G_FOOTER_ICON_EDIT_MASK )

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
		self.mListAllChannel.append( 'All Channel by Number' )
		self.mListAllChannel.append( 'All Channel by Alphabet' )
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
		self.mCtrlLblPath1.setLabel( '%s'% label1.upper() )
		self.mCtrlLblPath2.setLabel( '%s'% label2.title() ) 
		self.mCtrlLblPath3.setLabel( 'sort by %s'% label3.title() ) 
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

		self.mListItems = []
		for ch in self.mChannelList:
			#skip ch
			if ch.mSkipped == True :
				continue

			listItem = xbmcgui.ListItem( "%04d %s"%( ch.mNumber, ch.mName ), "-", "-", "-", "-" )

			thum=icas=''
			if ch.mLocked  : thum='IconLockFocus.png'#'OverlayLocked.png'
			if ch.mIsCA    : icas='IconCas.png'
			listItem.setProperty('lock', thum)
			listItem.setProperty('icas', icas)
			self.mListItems.append(listItem)

		self.mCtrlListCHList.addItems( self.mListItems )

		#detected to last focus
		#self.mCurrentChannel = self.mCommander.Channel_GetCurrent()
		self.mNavChannel = self.mCommander.Channel_GetCurrent()

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
			if self.mEpgRecvPermission == True :
				ret = self.mCommander.Epgevent_GetPresent()
				time.sleep(0.5)
				if ret :
					self.mNavEpg = ret
					ret.printdebug()

			else :
				label = self.mCtrlListCHList.getSelectedItem().getLabel()
				channelNumbr = int(label[:4])

				for ch in self.mChannelList:
					if ch.mNumber == channelNumbr :
						self.mNavChannel = None
						self.mNavChannel = ch
						LOG_TRACE( 'found ch: getlabel[%s] ch[%s]'% (channelNumbr, ch.mNumber ) )

						gmtFrom = self.mLocalTime - self.mLocalOffset
						gmtUntil= 0
						maxCount= 1
						ret = self.mCommander.Epgevent_GetList( ch.mSid, ch.mTsid, ch.mOnid, gmtFrom, gmtUntil, maxCount )
						time.sleep(0.5)
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
		if self.mEpgRecvPermission == True :
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



		#popup pin-code dialog
		if self.mPincodeEnter > FLAG_MASK_NONE :
			msg1 = Msg.Strings(MsgId.LANG_INPUT_PIN_CODE)
			msg2 = Msg.Strings(MsgId.LANG_CURRENT_PIN_CODE)
			kb = xbmc.Keyboard( msg1, '1111', False )
			kb.doModal()
			if( kb.isConfirmed() ) :
				inputPass = kb.getText()
				#self.mPincodeEnter = FLAG_MASK_NONE
				LOG_TRACE( 'password[%s]'% inputPass )

		LOG_TRACE( 'Leave' )


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
			time.sleep(1)
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

			self.mLocalTime = 0

		LOG_TRACE( 'Leave' )

