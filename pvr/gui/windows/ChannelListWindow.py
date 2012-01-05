import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as WinMgr
from pvr.gui.BaseWindow import BaseWindow, Action
from ElisEnum import ElisEnum
from ElisEventBus import ElisEventBus
from ElisEventClass import *
from pvr.Util import RunThread, GuiLock
import pvr.Util as Util
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

class ChannelListWindow(BaseWindow):

	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		self.mCommander = pvr.ElisMgr.GetInstance().GetCommander()		

		self.mEventBus = pvr.ElisMgr.GetInstance().GetEventBus()

		#summary
		self.__file__ = os.path.basename( currentframe().f_code.co_filename )

		#submenu list
		self.mListAllChannel= []
		self.mListSatellite = []
		self.mListCasList   = []
		self.mListFavorite  = []

		self.mEventId = 0
		self.mLocalTime = 0

		self.mPincodeEnter = FLAG_MASK_NONE
		
	def __del__(self):
		print '[%s:%s]destroyed ChannelBanner'% (self.__file__, currentframe().f_lineno)

		# end thread updateEPGProgress()
		self.mEnableThread = False


	def onInit(self):
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId )
		print '[%s:%s]winID[%d]'% (self.__file__, currentframe().f_lineno, self.mWinId)

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
		self.listEnableFlag = False

		#initialize get channel list
		self.InitSlideMenuHeader()
		#self.getSlideMenuHeader()


		try :
			#self.mCurrentChannel = self.mCommander.Channel_GetCurrent()
			self.mNavChannel = self.mCommander.Channel_GetCurrent()
			
		except Exception, e :
			print '[%s:%s] Error exception[%s]'% (	\
				self.__file__,						\
				currentframe().f_lineno,			\
				e )

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

	@GuiLock	
	def onAction(self, aAction):
		id = aAction.getId()
		focusId = self.getFocusId()
		#print '[%s:%s]aActionID[%d]'% (self.__file__, currentframe().f_lineno, id) 

		if id == Action.ACTION_PREVIOUS_MENU:
			print 'goto previous menu'

		elif id == Action.ACTION_SELECT_ITEM:
			print 'item select, action ID[%s]'% id


		elif id == Action.ACTION_PARENT_DIR :
			print 'goto action back'

			self.SaveSlideMenuHeader()
			
			self.mEnableThread = False
			self.CurrentTimeThread().join()
			self.mCtrlListCHList.reset()
			self.close()

		elif id == Action.ACTION_MOVE_RIGHT :
			if focusId == self.mCtrlListMainmenu.getId() :
				position = self.mCtrlListMainmenu.getSelectedPosition()

				#this position's 'Back'
				if position == 4 :
					self.mCtrlListCHList.setEnabled( True )
					self.setFocusId( self.mCtrlGropCHList.getId() )

				else :
					self.onClick( self.mCtrlListMainmenu.getId() )

			elif focusId == self.mCtrlListSubmenu.getId() :
				self.onClick( self.mCtrlListMainmenu.getId() )

		elif id == Action.ACTION_MOVE_UP or id == Action.ACTION_MOVE_DOWN :
			if focusId == self.mCtrlListCHList.getId() :
				self.mEpgRecvPermission = False
				self.InitEPGEvent()

				self.ResetLabel()
				self.UpdateLabelInfo()

			elif focusId >= self.mCtrlFooter1.getId() and focusId <= self.mCtrlFooter3.getId() :
				self.mCtrlListCHList.setEnabled( True )
				self.setFocusId( self.mCtrlGropCHList.getId() )
				

				

		elif id == 13: #'x'
			#pass
			#get setting language
			#name=''
			#ret=self.mCommander.enum_GetProp(name)
			#print 'language ret[%s] name[%s]'% (ret,name)

			import locale, codecs, os, xbmcaddon, gettext
			#lc=locale.normalize("fr")
			#lc = locale._build_localename(locale.getdefaultlocale())
			
			#print 'lc[%s]'% gettext.NullTranslations.info()
			#print 'lc[%s]'% lc
			#dlc = locale._print_locale()
			#print 'get[%s]'% dlc
			
			#dlc = ('ko_KR', 'cp949')
			#locale.setlocale(0, 'ISO8859-1')
			#locale.setlocale(0, locale._build_localename(dlc) )
			#locale.resetlocale(0)
			#self.mCtrlHeader2.setLabel(str('[%s]'% lc))
			#import gettext
			#LOCALE_DIR = os.path.dirname(__file__)
			#domain = gettext.bindtextdomain('imdbpy', LOCALE_DIR)			
			#gettext.translation(domain,None,None,None,None, lc)
			
			#print 'locale [%s]'% locale._setlocale(0, locale._build_localename( ('fr_FR.ISO8859-1') ) )
			#print 'locale[%s]'% locale.resetlocale()

			"""
			cwd='C:\Users\SERVER\AppData\Roaming\XBMC\userdata\guisettings.xml'
			print 'getcwd[%s]'% cwd
			f = open(cwd, 'r')
			import re
			for line in f.readlines():
				ret = re.search('<language>\w*</language>', line)
				if ret != None:
					print 'ret[%s]'% ret.group()
					retstr = ret.group()
					ll = retstr.find('<language>')
					rr = retstr.rfind('</language>')
					retlabel = retstr[10:rr]
					print 'retstr[%s]'% retlabel
					self.mCtrlBtn.setLabel(retlabel)
			f.close()
			"""
			print 'cwd[%s]'% xbmc.getLanguage()

			"""
			import re

			openFile = 'D:\project\elmo\doc\language tool\Language_Prime.csv'
			wFile1 = 'strings.xml'
			print openFile
			rf = open(openFile, 'r')
			#wf = open(wFile1, 'w')
			for line in rf.readlines():
				ret = re.search(',', line)
				print ret.group()


			rf.close()
			"""



	@GuiLock	
	def onClick(self, aControlId):
		print '[%s:%s]focusID[%d]'% (self.__file__, currentframe().f_lineno, aControlId) 

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

			position = self.mCtrlListMainmenu.getSelectedPosition()
			print 'focus[%s] idx_main[%s]'% (aControlId, position)

			if position == 4 :
				self.mCtrlListCHList.setEnabled(True)
				self.setFocusId( self.mCtrlGropCHList.getId() )

			else :
				self.SubMenuAction( 0, position )
				self.setFocusId( self.mCtrlListSubmenu.getId() )
				#self.setFocusId( self.mCtrlGropSubmenu.getId() )

		elif aControlId == self.mCtrlListSubmenu.getId() :
			#list action
			position = self.mZappingMode
			print 'focus[%s] idx_sub[%s]'% (aControlId, position)

			self.SubMenuAction( 1, self.mZappingMode )

		elif aControlId == self.mCtrlFooter1.getId() :
			print 'footer back'
			self.SaveSlideMenuHeader()

			self.mEnableThread = False
			self.CurrentTimeThread().join()
			self.mCtrlListCHList.reset()
			self.close( )

		elif aControlId == self.mCtrlFooter2.getId() :
			print 'footer ok'
			self.onClick( self.mCtrlListCHList.getId() )

		elif aControlId == self.mCtrlFooter3.getId() :
			print 'footer edit'
			self.SaveSlideMenuHeader()

			self.mEnableThread = False
			self.CurrentTimeThread().join()

			#ToDO: WinMgr.GetInstance().ShowWindow( WinMgr.WIN_ID_CHANNEL_EDIT_WINDOW )




	def onFocus(self, controlId):
		#print "onFocus(): control %d" % controlId
		pass

	@GuiLock
	def onEvent(self, aEvent):
		print '[%s:%s]'% (self.__file__, currentframe().f_lineno)
		print 'aEvent[%s]'% aEvent



		if self.mWinId == xbmcgui.getCurrentWindowId() :
			msg = aEvent[0]
			
			if msg == ElisEvent.ElisCurrentEITReceived :

				if int(event[4]) != self.mEventId :
					if self.mEpgRecvPermission == True :
						#on select, clicked

						#ret = self.mCommander.epgevent_Get(self.mEventId, int(event[1]), int(event[2]), int(event[3]), self.mLocalTime )
						ret = self.mCommander.Epgevent_GetPresent()
						if ret :
							self.mNavEpg = ret
							self.mEventId = int( event[4] )

						#not select, key up/down,
					else :
						ret = self.InitEPGEvent()

					#update label
					self.ResetLabel()
					self.UpdateLabelInfo()


			else :
				print 'event unknown[%s]'% event
		else:
			print 'channellist winID[%d] this winID[%d]'% (self.mWin, xbmcgui.getCurrentWindowId())



	def SubMenuAction(self, aAction, aMenuIndex):
		print '[%s:%s]'% (self.__file__, currentframe().f_lineno)
		retPass = False

		if aAction == 0:
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

				#path tree, Mainmenu/Submanu
				#label1 = self.mCtrlListMainmenu.getSelectedItem().getLabel()
				#label1 = enumToString('mode', self.mZappingMode)
				#self.mCtrlLblPath1.setLabel( label1.title() )


		elif aAction == 1:

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
				#print 'cmd[channel_GetList] idx_AllChannel[%s] sort[%s] ch_list[%s]'% (idx_AllChannel, self.mChannelListSortMode, self.mChannelList)

			elif aMenuIndex == ElisEnum.E_MODE_SATELLITE:
				idx_Satellite = self.mCtrlListSubmenu.getSelectedPosition()
				item = self.mListSatellite[idx_Satellite]
				retPass = self.GetChannelList( self.mChannelListServieType, self.mZappingMode, self.mChannelListSortMode, item.mLongitude, item.mBand, 0, '' )

				print 'cmd[channel_GetListBySatellite] idx_Satellite[%s] mLongitude[%s] band[%s]'% ( idx_Satellite, item.mLongitude, item.mBand )
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

				print 'cmd[channel_GetListByFTACas] idxFtaCas[%s]'% ( idxFtaCas )
				ClassToList( 'print', self.mChannelList )


			elif aMenuIndex == ElisEnum.E_MODE_FAVORITE:
				idx_Favorite = self.mCtrlListSubmenu.getSelectedPosition()
				item = self.mListFavorite[idx_Favorite]
				retPass = self.GetChannelList( self.mChannelListServieType, self.mZappingMode, self.mChannelListSortMode, 0, 0, 0, item.mGroupName )

				print 'cmd[channel_GetListByFavorite] idx_Favorite[%s] list_Favorite[%s]'% ( idx_Favorite, item.mGroupName )
				ClassToList( 'print', self.mChannelList )


			if retPass == False :
				return

			if len(self.mChannelList) > 0 :
				#channel list update
				#self.mCtrlListCHList.reset()
				self.InitChannelList()

				#path tree, Mainmenu/Submanu
				#label1 = self.mCtrlListMainmenu.getSelectedItem().getLabel()
				label1 = EnumToString('mode', self.mZappingMode)
				label2 = self.mCtrlListSubmenu.getSelectedItem().getLabel()
				label3 = EnumToString('sort', self.mChannelListSortMode)
				self.mCtrlLblPath1.setLabel( '%s'% label1.upper() )
				self.mCtrlLblPath2.setLabel( '%s'% label2.title() ) 
				self.mCtrlLblPath3.setLabel( 'sort by %s'% label3.title() ) 

				#save zapping mode
				#ret = self.mCommander.zappingmode_SetCurrent( self.mZappingMode, self.mChannelListSortMode, self.mChannelListServieType )
				#print 'set zappingmode_SetCurrent[%s]'% ret


	def GetChannelList(self, aType, aMode, aSort, aLongitude, aBand, aCAid, aFavName ):
		print '[%s:%s]'% (self.__file__, currentframe().f_lineno)

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
			print '[%s:%s] Error exception[%s]'% (	\
				self.__file__,						\
				currentframe().f_lineno,			\
				e )
			return False



		return True

	def GetSlideMenuHeader(self) :
		print '[%s:%s]'% (self.__file__, currentframe().f_lineno)

		#get zapping last mode
		lastMainMenu= 0
		lastSubMenu = 1


		self.mCtrlListMainmenu.selectItem( lastMainMenu )
		#self.mZappingMode = lastMainMenu
		#self.setFocusId( 102 )
		self.SubMenuAction(0, lastMainMenu)
		self.mCtrlListSubmenu.selectItem( lastSubMenu )
		self.setFocusId( self.mCtrlListSubmenu.getId() )

		
	def SaveSlideMenuHeader(self) :
		print '[%s :%s]'% (self.__file__, currentframe().f_lineno)

		return

		#is change?
		ret = False
		try :
			label1 = EnumToString('mode', self.mZappingMode)
			label2 = self.mCtrlListSubmenu.getSelectedItem().getLabel()

			head = m.strings(mm.LANG_TO_CHANGE_ZAPPING_MODE)
			line1 = '%s / %s'% (label1.title(), label2.title())
			line2 = m.strings(mm.LANG_DO_YOU_WANT_TO_SAVE_CHANNELS)

			ret = xbmcgui.Dialog().yesno(head, line1, '', line2)
			#print 'dialog ret[%s]' % ret

		except Exception, e :
			print '[%s:%s]Error exception[%s]'% (	\
				self.__file__,						\
				currentframe().f_lineno,			\
				e )
		

		if ret == True :
			#save zapping mode
			ret = self.mCommander.Zappingmode_SetCurrent( self.mZappingMode, self.mChannelListSortMode, self.mChannelListServieType )
			print 'set zappingmode_SetCurrent[%s]'% ret



	def InitSlideMenuHeader(self) :
		print '[%s:%s]'% (self.__file__, currentframe().f_lineno)

		#header init
		self.mCtrlHeader1.setImage('IconHeaderTitleSmall.png')
		#self.mCtrlHeader2.setLabel('TV-Channel List')
		self.mCtrlHeader2.setLabel(Msg.Strings(MsgId.LANG_TV_CHANNEL_LIST))

		#self.mCtrlLbl.setLabel( m.strings(mm.LANG_LANGUAGE) )
		ret = xbmc.getLanguage()
		print 'getLanguage[%s]'% ret
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
			#print 'zappingmode_GetCurrent len[%s]'% len(zappingMode)
			#ClassToList( 'print', zappingMode )
			#zappingMode.printdebug()

		except Exception, e:
			self.mZappingMode           = ElisEnum.E_MODE_ALL
			self.mChannelListSortMode   = ElisEnum.E_SORT_BY_DEFAULT
			self.mChannelListServieType = ElisEnum.E_SERVICE_TYPE_TV
			print '[%s:%s]Error exception[%s] zappingmode defaulted'% (	\
				self.__file__,							\
				currentframe().f_lineno,				\
				e )


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
		print 'mListAllChannel[%s]'% self.mListAllChannel

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

		except Exception, e :
			print '[%s:%s]Error exception[%s]'% (	\
				self.__file__,						\
				currentframe().f_lineno,			\
				e )

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


		#get channel list by last on zapping mode, sorting, service type
		self.mNavChannel = None
		self.mChannelList = None
		self.mChannelList = self.mCommander.Channel_GetList( self.mChannelListServieType, self.mZappingMode, self.mChannelListSortMode )
		#self.GetChannelList(self.mChannelListServieType, self.mZappingMode, self.mChannelListSortMode, 0, 0, 0, '')

		print 'zappingMode[%s] sortMode[%s] serviceType[%s]'%  \
			( EnumToString('mode', self.mZappingMode),         \
			  EnumToString('sort', self.mChannelListSortMode), \
			  EnumToString('type', self.mChannelListServieType) )
		ClassToList( 'print', self.mChannelList )


	def InitChannelList(self):
		print '[%s :%s]'% (self.__file__, currentframe().f_lineno)

		chList = ClassToList( 'convert', self.mChannelList )
		if len(chList) < 1 :
			print 'no data, self.mChannelList len[%s]'% ( len(self.mChannelList) )
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


	def ResetLabel(self):
		print '[%s:%s]'% (self.__file__, currentframe().f_lineno)
		#chListInfo = ClassToList( 'convert', self.mNavChannel )
		#print 'currentChannel[%s]'% chListInfo


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



	def InitEPGEvent( self ) :
		ret = []

		self.mNavEpg = None

		try :
			if self.mEpgRecvPermission == True :
				self.mNavEpg = self.mCommander.Epgevent_GetPresent()
				#ret=['epgevent_GetPresent'] + ret

			else :
				label = self.mCtrlListCHList.getSelectedItem().getLabel()
				channelNumbr = int(label[:4])

				for ch in self.mChannelList:
					if ch.mNumber == channelNumbr :
						self.mNavChannel = None
						self.mNavChannel = ch
						print 'found ch: getlabel[%s] ch[%s]'% (channelNumbr, ch.mNumber )

						gmtFrom = self.mLocalTime - self.mLocalOffset
						gmtUntil= 0
						maxCount= 1
						self.mNavEpg = self.mCommander.Epgevent_GetList( ch.mSid, ch.mTsid, ch.mOnid, gmtFrom, gmtUntil, maxCount )
						time.sleep(0.5)


		except Exception, e :
			print '[%s:%s] Error exception[%s]'% (	\
				self.__file__,						\
				currentframe().f_lineno,			\
				e )


	def UpdateServiceType( self, aTvType ):
		print '[%s:%s]'% (self.__file__, currentframe().f_lineno)
		print 'serviceType[%s]' % aTvType

		label = ''
		if aTvType == ElisEnum.E_SERVICE_TYPE_TV:
			label = 'TV'
		elif aTvType == ElisEnum.E_SERVICE_TYPE_RADIO:
			label = 'RADIO'
		elif aTvType == ElisEnum.E_SERVICE_TYPE_DATA:
			label = 'DATA'
		else:
			label = 'etc'
			print 'unknown ElisEnum tvType[%s]'% aTvType

		return label

	def UpdateLabelInfo( self ):
		print '[%s:%s]'% (self.__file__, currentframe().f_lineno)

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
				print 'AgeLimit[%s]'% isLimit

		else:
			print 'event null'



		#popup pin-code dialog
		if self.mPincodeEnter > 0 :
			msg1 = Msg.Strings(MsgId.LANG_INPUT_PIN_CODE)
			msg2 = Msg.Strings(MsgId.LANG_CURRENT_PIN_CODE)
			kb = xbmc.Keyboard( msg1, '1111', False )
			kb.doModal()
			if( kb.isConfirmed() ) :
				inputPass = kb.getText()
				#self.mPincodeEnter = FLAG_MASK_NONE
				print 'password[%s]'% inputPass


	@RunThread
	def CurrentTimeThread(self):
		print '[%s():%s]begin_start thread'% (self.__file__, currentframe().f_lineno)

		loop = 0
		#rLock = threading.RLock()
		while self.mEnableThread:
			#print '[%s:%s]repeat <<<<'% (self.__file__, currentframe().f_lineno)

			#progress

			if  ( loop % 10 ) == 0 :
				print 'loop=%d' %loop
				self.UpdateLocalTime( )


			#local clock
			ret = EpgInfoClock(1, self.mLocalTime, loop)
			self.mCtrlHeader3.setLabel(ret[0])
			self.mCtrlHeader4.setLabel(ret[1])

			#self.nowTime += 1
			time.sleep(1)
			loop += 1

		print '[%s:%s]leave_end thread'% (self.__file__, currentframe().f_lineno)


	@GuiLock
	def UpdateLocalTime( self ) :
		
		try:
			self.mLocalTime = self.mCommander.Datetime_GetLocalTime( )

		except Exception, e :
			print '[%s:%s] Error exception[%s]'% (	\
				self.__file__,						\
				currentframe().f_lineno,			\
				e )

			self.mLocalTime = 0

		if self.mNavEpg :
			endTime = self.mNavEpg.mStartTime + self.mNavEpg.mDuration
	
			pastDuration = endTime - self.mLocalTime
			if pastDuration < 0 :
				pastDuration = 0

			if self.mNavEpg.mDuration > 0 :
				percent = pastDuration * 100/self.mNavEpg.mDuration
			else :
				percent = 0

			#print 'percent=%d' %percent
			self.mCtrlProgress.setPercent( percent )

	
