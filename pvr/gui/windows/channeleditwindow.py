import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import BaseWindow
from pvr.gui.basewindow import Action
from elisenum import ElisEnum
from elisevent import ElisEvent
from inspect import currentframe
from pvr.util import catchall, is_digit, run_async, epgInfoTime, epgInfoClock, epgInfoComponentImage, GetSelectedLongitudeString, enumToString, ui_locked2
import pvr.util as util
import pvr.elismgr
from elisproperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.guiconfig import FooterMask
import threading, time, os

import pvr.msg as m
import pvr.gui.windows.define_string as mm


class ChannelEditWindow(BaseWindow):

	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance().getCommander()		

		self.eventBus = pvr.elismgr.getInstance().getEventBus()

		#summary
		self.__file__ = os.path.basename( currentframe().f_code.co_filename )

		#submenu list
		self.list_AllChannel= []
		self.list_Satellite = []
		self.list_CasList   = []
		self.list_Favorite  = []

		self.execute_OnlyOne = True
		self.nowTime = 0
		self.eventID = 0
		self.win = 0
		self.localTime = 0

		self.pincodeEnter = 0x0
		self.chInfoArgument = 14
		self.epgArgument = 21
		
	def __del__(self):
		print '[%s():%s] destroyed ChannelBanner'% (currentframe().f_code.co_name, currentframe().f_lineno)

		# end thread updateEPGProgress()
		self.untilThread = False


	def onInit(self):
		self.epgRecvPermission = True
		self.epgStartTime = 0
		self.epgDuration = 0
		self.localOffset = int( self.commander.datetime_GetLocalOffset()[0] )

		self.winId = xbmcgui.getCurrentWindowId()
		self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
		print '[%s():%s]winID[%d]'% (currentframe().f_code.co_name, currentframe().f_lineno, self.winId)

		self.eventBus.register( self )		

		#header
		self.ctrlHeader1            = self.getControl( 3000 )
		self.ctrlHeader2            = self.getControl( 3001 )
		self.ctrlHeader3            = self.getControl( 3002 )
		self.ctrlHeader4            = self.getControl( 3003 )

		#footer
		self.ctrlFooter1            = self.getControl( 3101 )
		self.ctrlFooter2            = self.getControl( 3111 )
		self.ctrlFooter3            = self.getControl( 3141 )

		self.ctrlLblPath1           = self.getControl( 10 )
		self.ctrlLblPath2           = self.getControl( 11 )

		#main menu
		self.ctrlGrpMainmenu        = self.getControl( 100 )
		self.ctrlBtnMenu            = self.getControl( 101 )
		self.ctrlListMainmenu       = self.getControl( 102 )
		
		#sub menu list
		self.ctrlGrpSubmenu         = self.getControl( 9001 )
		self.ctrlListSubmenu        = self.getControl( 202 )

		#ch list
		self.ctrlGrpCHList          = self.getControl( 49 )
		self.ctrlListCHList         = self.getControl( 50 )

		#info
		self.ctrlChannelName        = self.getControl( 303 )
		self.ctrlEventName          = self.getControl( 304 )
		self.ctrlEventTime          = self.getControl( 305 )
		self.ctrlProgress           = self.getControl( 306 )
		self.ctrlLongitudeInfo      = self.getControl( 307 )
		self.ctrlCareerInfo         = self.getControl( 308 )
		self.ctrlLockedInfo         = self.getControl( 309 )
		self.ctrlServiceTypeImg1    = self.getControl( 310 )
		self.ctrlServiceTypeImg2    = self.getControl( 311 )
		self.ctrlServiceTypeImg3    = self.getControl( 312 )
		self.ctrlSelectItem         = self.getControl( 401 )
		
		#test ctrl
		#self.ctrlLbl                = self.getControl( 9001 )
		#self.ctrlBtn                = self.getControl( 9002 )


		#epg stb time
		self.ctrlHeader3.setLabel('')
		#etc
		self.listEnableFlag = False

		#initialize get channel list
		self.initSlideMenuHeader()

		
		#self.getSlideMenuHeader()

		try :
			channelInfo = self.commander.channel_GetCurrent()
			self.currentChannel = int ( channelInfo[0] )

		except Exception, e :
			print '[%s]%s():%s Error exception[%s]'% (	\
				self.__file__,							\
				currentframe().f_code.co_name,			\
				currentframe().f_lineno,				\
				e )


		self.initChannelList()

		#clear label
		self.initLabelInfo()

		#initialize get epg event
		ret = self.initEPGEvent()
		self.updateLabelInfo(ret, self.currentChannelInfo)

		#run thread
		self.untilThread = True
		self.currentTimeThread()

	@ui_locked2	
	def onAction(self, action):
		id = action.getId()
		focusId = self.getFocusId( )
		#print '[%s():%s]actionID[%d]'% (currentframe().f_code.co_name, currentframe().f_lineno, id) 

		if id == Action.ACTION_PREVIOUS_MENU:
			print 'goto previous menu'

		elif id == Action.ACTION_SELECT_ITEM:
			print 'item select, action ID[%s]' % id


		elif id == Action.ACTION_PARENT_DIR:
			print 'goto action back'

			self.untilThread = False
			self.currentTimeThread().join()
			self.ctrlListCHList.reset()

			self.close( )

		elif id == Action.ACTION_MOVE_RIGHT:
			#print 'ACTION_MOVE_RIGHT, getFocusId[%s]'% focusId

			if focusId == self.ctrlListMainmenu.getId() :
				idx_menu = self.ctrlListMainmenu.getSelectedPosition()

				#this position's 'Back'
				if idx_menu == 4 :
					self.ctrlListCHList.setEnabled( True )
					self.setFocusId( self.ctrlGrpCHList.getId() )
					self.saveSlideMenuHeader()

				else :
					self.onClick( self.ctrlListMainmenu.getId() )

			elif focusId == self.ctrlListSubmenu.getId() :
				self.onClick( self.ctrlListMainmenu.getId() )

		elif id == Action.ACTION_MOVE_UP or id == Action.ACTION_MOVE_DOWN:
			if focusId == self.ctrlListCHList.getId() :
				self.epgRecvPermission = False
				ret = self.initEPGEvent()

				self.initLabelInfo()
				self.updateLabelInfo( ret[0], ret[1] )

			elif focusId >= self.ctrlFooter1.getId() and focusId <= self.ctrlFooter3.getId() :
				self.ctrlListCHList.setEnabled( True )
				self.setFocusId( self.ctrlGrpCHList.getId() )
				

				

		elif id == 13: #'x'
			#pass
			#get setting language
			#name=''
			#ret=self.commander.enum_GetProp(name)
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
			#self.ctrlHeader2.setLabel(str('[%s]'% lc))
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
					self.ctrlBtn.setLabel(retlabel)
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


		else:
			pass
			#self.ctrlHeader2.setLabel(str('key[%s]'% action.getId()))
			#print'Unconsumed key: %s' % action.getId()

	@ui_locked2	
	def onClick(self, controlId):
		print '[%s():%s]focusID[%d]'% (currentframe().f_code.co_name, currentframe().f_lineno, controlId) 

		if controlId == self.ctrlListCHList.getId() :

			label = self.ctrlListCHList.getSelectedItem().getLabel()
			channelNumbr = int(label[:4])
			ret = self.commander.channel_SetCurrent( channelNumbr, self.chlist_serviceType)

			if ret[0].upper() == 'TRUE' :
				if self.pincodeEnter == 0x00 :
					if self.currentChannel == channelNumbr :
						self.untilThread = False
						self.currentTimeThread().join()

						winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_BANNER )

					else :
						winmgr.getInstance().getWindow(winmgr.WIN_ID_CHANNEL_BANNER).setLastChannel( self.currentChannel )

				self.currentChannel = channelNumbr
				self.currentChannelInfo = self.commander.channel_GetCurrent()

			self.epgRecvPermission = True
			self.ctrlSelectItem.setLabel(str('%s / %s'% (self.ctrlListCHList.getSelectedPosition()+1, len(self.listItems))) )
			self.initLabelInfo()
			self.updateLabelInfo([], self.currentChannelInfo)

		elif controlId == self.ctrlBtnMenu.getId() or controlId == self.ctrlListMainmenu.getId() :
			#list view

			idx_menu = self.ctrlListMainmenu.getSelectedPosition()
			print 'focus[%s] idx_main[%s]'% (controlId, idx_menu)

			if idx_menu == 4 :
				self.ctrlListCHList.setEnabled(True)
				self.setFocusId( self.ctrlGrpCHList.getId() )

			else :
				self.subMenuAction( 0, idx_menu )
				self.setFocusId( self.ctrlListSubmenu.getId() )
				#self.setFocusId( self.ctrlGrpSubmenu.getId() )

		elif controlId == self.ctrlListSubmenu.getId() :
			#list action
			idx_menu = self.chlist_zappingMode
			print 'focus[%s] idx_sub[%s]'% (controlId, idx_menu)

			self.subMenuAction( 1, self.chlist_zappingMode )

		elif controlId == self.ctrlFooter1.getId() :
			print 'footer back'
			self.untilThread = False
			self.currentTimeThread().join()
			self.ctrlListCHList.reset()

			self.close( )

		elif controlId == self.ctrlFooter2.getId() :
			print 'footer ok'
			self.onClick( self.ctrlListCHList.getId() )

		elif controlId == self.ctrlFooter3.getId() :
			print 'footer edit'
			pass



	def onFocus(self, controlId):
		#print "onFocus(): control %d" % controlId
		pass

	@ui_locked2
	def onEvent(self, event):
		print '[%s]%s():%s'% (self.__file__, currentframe().f_code.co_name, currentframe().f_lineno)
		print 'event[%s]'% event


		if len(event) != 5 :
			return

		if self.winId == xbmcgui.getCurrentWindowId() :
			msg = event[0]
			
			if msg == ElisEvent.ElisCurrentEITReceived :

				if int(event[4]) != self.eventID :
					if self.epgRecvPermission == True :
						#on select, clicked

						#ret = self.commander.epgevent_Get(self.eventID, int(event[1]), int(event[2]), int(event[3]), self.localTime )
						ret = self.commander.epgevent_GetPresent( )
						if len( ret ) > 0 :
							self.eventID = int( event[4] )
							self.initLabelInfo()
							self.updateLabelInfo( ret, self.currentChannelInfo )

						#not select, key up/down,
					else :
						ret = self.initEPGEvent()
						self.initLabelInfo()
						self.updateLabelInfo( ret[0], ret[1] )


			else :
				print 'event unknown[%s]'% event
		else:
			print 'channellist winID[%d] this winID[%d]'% (self.win, xbmcgui.getCurrentWindowId())


	def subMenuAction(self, action, idx_menu):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		retPass = False

		if action == 0:
			testlistItems = []
			if idx_menu == 0 :
				self.chlist_zappingMode = ElisEnum.E_MODE_ALL
				for item in range(len(self.list_AllChannel)) :
					testlistItems.append(xbmcgui.ListItem(self.list_AllChannel[item]))

			elif idx_menu == 1 :
				self.chlist_zappingMode = ElisEnum.E_MODE_SATELLITE
				for item in self.list_Satellite:
					ret = GetSelectedLongitudeString(item)
					testlistItems.append(xbmcgui.ListItem(ret))

			elif idx_menu == 2 :
				self.chlist_zappingMode = ElisEnum.E_MODE_CAS
				for item in self.list_CasList:
					ret = '%s(%s)'% (item[0], item[1])
					testlistItems.append(xbmcgui.ListItem( ret ))

			elif idx_menu == 3 :
				self.chlist_zappingMode = ElisEnum.E_MODE_FAVORITE
				for item in self.list_Favorite:
					testlistItems.append(xbmcgui.ListItem( item[0] ))

			if testlistItems != [] :
				#submenu update
				self.ctrlListSubmenu.reset()
				self.ctrlListSubmenu.addItems( testlistItems )

				#path tree, Mainmenu/Submanu
				#label1 = self.ctrlListMainmenu.getSelectedItem().getLabel()
				#label1 = enumToString('mode', self.chlist_zappingMode)
				#self.ctrlLblPath1.setLabel( label1.title() )


		elif action == 1:

			if idx_menu == ElisEnum.E_MODE_ALL :
				idx_Sorting   = self.ctrlListSubmenu.getSelectedPosition()
				if idx_Sorting == 0:
					sortingMode = ElisEnum.E_SORT_BY_NUMBER
				elif idx_Sorting == 1:
					sortingMode = ElisEnum.E_SORT_BY_ALPHABET
				elif idx_Sorting == 2:
					sortingMode = ElisEnum.E_SORT_BY_HD

				self.chlist_channelsortMode = sortingMode
				retPass = self.getChannelList( self.chlist_serviceType, self.chlist_zappingMode, sortingMode, 0, 0, 0, '' )

				#idx_AllChannel = self.ctrlListSubmenu.getSelectedPosition()
				#item = self.list_AllChannel[idx_AllChannel]
				#print 'cmd[channel_GetList] idx_AllChannel[%s] sort[%s] ch_list[%s]'% (idx_AllChannel, self.chlist_channelsortMode, self.channelList)

			elif idx_menu == ElisEnum.E_MODE_SATELLITE:
				idx_Satellite = self.ctrlListSubmenu.getSelectedPosition()
				item = self.list_Satellite[idx_Satellite]
				retPass = self.getChannelList( self.chlist_serviceType, self.chlist_zappingMode, self.chlist_channelsortMode, int(item[0]), int(item[1]), 0, '' )
				print 'cmd[channel_GetListBySatellite] idx_Satellite[%s] mLongitude[%s] band[%s] ch_list[%s]'% ( idx_Satellite, item[0], item[1], self.channelList )

			elif idx_menu == ElisEnum.E_MODE_CAS:
				idx_FtaCas = self.ctrlListSubmenu.getSelectedPosition()
				if idx_FtaCas == 0 :
					caid = ElisEnum.E_FTA_CHANNEL
				elif idx_FtaCas == 1 :
					caid = ElisEnum.E_MEDIAGUARD
				elif idx_FtaCas == 2 :
					caid = ElisEnum.E_VIACCESS
				elif idx_FtaCas == 3 :
					caid = ElisEnum.E_NAGRA
				elif idx_FtaCas == 4 :
					caid = ElisEnum.E_IRDETO
				elif idx_FtaCas == 5 :
					caid = ElisEnum.E_CRYPTOWORKS
				elif idx_FtaCas == 6 :
					caid = ElisEnum.E_BETADIGITAL
				elif idx_FtaCas == 7 :
					caid = ElisEnum.E_NDS
				elif idx_FtaCas == 8 :
					caid = ElisEnum.E_CONAX
				else :
					caid = ElisEnum.E_OTHERS

				retPass = self.getChannelList( self.chlist_serviceType, self.chlist_zappingMode, self.chlist_channelsortMode, 0, 0, caid, '' )

				item = self.list_CasList[idx_FtaCas]
				print 'cmd[channel_GetListByFTACas] idx_FtaCas[%s] list_CasList[%s] ch_list[%s]'% ( idx_FtaCas, item, self.channelList )

			elif idx_menu == ElisEnum.E_MODE_FAVORITE:
				idx_Favorite = self.ctrlListSubmenu.getSelectedPosition()
				item = self.list_Favorite[idx_Favorite]
				retPass = self.getChannelList( self.chlist_serviceType, self.chlist_zappingMode, self.chlist_channelsortMode, 0, 0, 0, item[0] )
				print 'cmd[channel_GetListByFavorite] idx_Favorite[%s] list_Favorite[%s] ch_list[%s]'% ( idx_Favorite, item, self.channelList )


			if retPass == False :
				return

			if len(self.channelList) > 0 and self.channelList != '' :
				#channel list update
				#self.ctrlListCHList.reset()
				self.initChannelList()

				#path tree, Mainmenu/Submanu
				#label1 = self.ctrlListMainmenu.getSelectedItem().getLabel()
				label1 = enumToString('mode', self.chlist_zappingMode)
				label2 = self.ctrlListSubmenu.getSelectedItem().getLabel()
				self.ctrlLblPath1.setLabel( '%s'% label1.upper() )
				self.ctrlLblPath2.setLabel( '%s'% label2.title() ) 

				#save zapping mode
				#ret = self.commander.zappingmode_SetCurrent( self.chlist_zappingMode, self.chlist_channelsortMode, self.chlist_serviceType )
				#print 'set zappingmode_SetCurrent[%s]'% ret


	def getChannelList(self, mType, mMode, mSort, mLongitude, mBand, mCAid, favName ):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		try :
			if mMode == ElisEnum.E_MODE_ALL :
				self.channelList = self.commander.channel_GetList( mType, mMode, mSort )

			elif mMode == ElisEnum.E_MODE_SATELLITE :
				self.channelList = self.commander.channel_GetListBySatellite( mType, mMode, mSort, mLongitude, mBand )

			elif mMode == ElisEnum.E_MODE_CAS :
				self.channelList = self.commander.channel_GetListByFTACas( mType, mMode, mSort, mCAid )
				
			elif mMode == ElisEnum.E_MODE_FAVORITE :
				self.channelList = self.commander.channel_GetListByFavorite( mType, mMode, mSort, favName )

			elif mMode == ElisEnum.E_MODE_NETWORK :
				pass

		except Exception, e:
			print 'Error[%s] getChannelList by zapping mode'% e
			return False


		return True

	def getSlideMenuHeader(self) :
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		#get zapping last mode
		lastMainMenu= 0
		lastSubMenu = 1


		self.ctrlListMainmenu.selectItem( lastMainMenu )
		#self.chlist_zappingMode = lastMainMenu
		#self.setFocusId( 102 )
		self.subMenuAction(0, lastMainMenu)
		self.ctrlListSubmenu.selectItem( lastSubMenu )
		self.setFocusId( self.ctrlListSubmenu.getId() )
		
	def saveSlideMenuHeader(self) :

		msg1 = 'zapping changed'
		msg2 = 'save ?'
		ret = xbmcgui.Dialog().yesno(msg1, msg2)
		print 'dialog ret[%s]' % ret


	def initSlideMenuHeader(self) :
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		#header init
		self.ctrlHeader1.setImage('IconHeaderTitleSmall.png')
		#self.ctrlHeader2.setLabel('TV-Channel List')
		self.ctrlHeader2.setLabel(m.strings(mm.LANG_TV_EDIT_CHANNEL_LIST))

		#self.ctrlLbl.setLabel( m.strings(mm.LANG_LANGUAGE) )
		ret = xbmc.getLanguage()
		print 'getLanguage[%s]'% ret
		#self.ctrlBtn.setLabel(ret)

		self.ctrlHeader3.setLabel('')		
		self.ctrlHeader4.setLabel('')

		#footer init
		#self.setProperty('WindowType', 'ChannelList')
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK | FooterMask.G_FOOTER_ICON_OK_MASK | FooterMask.G_FOOTER_ICON_EDIT_MASK )

		#main/sub menu init
		self.ctrlListMainmenu.reset()
		self.ctrlListSubmenu.reset()


		#get last zapping mode
		ret = []
		ret = self.commander.zappingmode_GetCurrent()
		if ret != [] :
			try:
				self.chlist_zappingMode     = int(ret[0])
				self.chlist_channelsortMode = int(ret[1])
				self.chlist_serviceType     = int(ret[2])
				print 'zappingmode_GetCurrent[True] ret[%s]'% ret

			except Exception, e:
				print 'zappingmode_GetCurrent Error[%s] = '% e
				self.chlist_serviceType     = ElisEnum.E_TYPE_TV
				self.chlist_zappingMode     = ElisEnum.E_MODE_ALL
				self.chlist_channelsortMode = ElisEnum.E_SORT_BY_DEFAULT
				print 'zappingmode_GetCurrent[False] default'
		else :
			#default init value for channel_GetList()
			self.chlist_serviceType     = ElisEnum.E_TYPE_TV
			self.chlist_zappingMode     = ElisEnum.E_MODE_ALL
			self.chlist_channelsortMode = ElisEnum.E_SORT_BY_DEFAULT
			print 'zappingmode_GetCurrent[False] default'


		list_Mainmenu = []
		list_Mainmenu.append( m.strings(mm.LANG_ALL_CHANNELS) )
		list_Mainmenu.append( m.strings(mm.LANG_SATELLITE)    )
		list_Mainmenu.append( m.strings(mm.LANG_FTA)          )
		list_Mainmenu.append( m.strings(mm.LANG_FAVORITE)     )
		list_Mainmenu.append( m.strings(mm.LANG_BACK)     )
		testlistItems = []
		for item in range( len(list_Mainmenu) ) :
			testlistItems.append( xbmcgui.ListItem(list_Mainmenu[item]) )

		self.ctrlListMainmenu.addItems( testlistItems )


		#sort list, This is fixed
		self.list_AllChannel = []
		self.list_AllChannel.append( 'All Channel by Number' )
		self.list_AllChannel.append( 'All Channel by Alphabet' )
		self.list_AllChannel.append( 'All Channel by HD/SD' )
		print 'list_AllChannel[%s]'% self.list_AllChannel

		try :
			#satellite longitude list
			self.list_Satellite = self.commander.satellite_GetConfiguredList( ElisEnum.E_SORT_NAME )
			print 'satellite_GetConfiguredList[%s]'% self.list_Satellite

			#FTA list
			self.list_CasList = self.commander.fta_cas_GetList( ElisEnum.E_TYPE_TV )
			print 'channel_GetFTACasList[%s]'% self.list_CasList

			#Favorite list
			self.list_Favorite = self.commander.favorite_GetList( ElisEnum.E_TYPE_TV )
			print 'channel_GetFavoriteList[%s]'% self.list_Favorite

		except Exception, e:
			print 'Error[e] get SubMenu'% e
			#TODO
			#display dialog

		testlistItems = []
		if self.chlist_zappingMode == ElisEnum.E_MODE_ALL :
			for item in range(len(self.list_AllChannel)) :
				testlistItems.append(xbmcgui.ListItem(self.list_AllChannel[item]))

		elif self.chlist_zappingMode == ElisEnum.E_MODE_SATELLITE :
			for item in self.list_Satellite:
				ret = GetSelectedLongitudeString(item)
				testlistItems.append(xbmcgui.ListItem(ret))

		elif self.chlist_zappingMode == ElisEnum.E_MODE_CAS :
			for item in self.list_CasList:
				ret = '%s(%s)'% (item[0], item[1])
				testlistItems.append(xbmcgui.ListItem( ret ))

		elif self.chlist_zappingMode == ElisEnum.E_MODE_FAVORITE :
			for item in self.list_Favorite:
				testlistItems.append(xbmcgui.ListItem( item[0] ))

		self.ctrlListSubmenu.addItems( testlistItems )


		#path tree, Mainmenu/Submanu
		#label1 = self.ctrlListMainmenu.getSelectedItem().getLabel()
		label1 = enumToString('mode', self.chlist_zappingMode)
		label2 = self.ctrlListSubmenu.getSelectedItem().getLabel()
		self.ctrlLblPath1.setLabel( '%s'% label1.upper() )
		self.ctrlLblPath2.setLabel( '%s'% label2.title() ) 


		#get channel list by last on zapping mode, sorting, service type
		self.currentChannel = -1
		self.channelList = []
		self.channelList = self.commander.channel_GetList( self.chlist_serviceType, self.chlist_zappingMode, self.chlist_channelsortMode )
		#self.getChannelList(self.chlist_serviceType, self.chlist_zappingMode, self.chlist_channelsortMode, 0, 0, 0, '')
		print 'zappingMode[%s] sortMode[%s] serviceType[%s] channellist[%s]'% \
			( enumToString('mode', self.chlist_zappingMode), \
			  enumToString('sort', self.chlist_channelsortMode), \
			  enumToString('type', self.chlist_serviceType), \
			  self.channelList )


	def initChannelList(self):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		if len(self.channelList) < 1 :
			print 'no data, self.channelList[%s]'% self.channelList
			return 

		self.listItems = []
		for ch in self.channelList:
			#skip ch
			if int(ch[12]) == 1 :
				continue

			listItem = xbmcgui.ListItem("%04d %s"%( int(ch[0]), ch[2]),"-", "-", "-", "-")

			thum=icas=''
			if int(ch[4]) == 1 : thum='IconLockFocus.png'#'OverlayLocked.png'
			if int(ch[5]) == 1 : icas='IconCas.png'
			listItem.setProperty('lock', thum)
			listItem.setProperty('icas', icas)
			self.listItems.append(listItem)

		self.ctrlListCHList.addItems( self.listItems )

		#detected to last focus
		self.currentChannelInfo = self.commander.channel_GetCurrent()
		self.currentChannel = int(self.currentChannelInfo[0])

		chindex = 0;
		if self.currentChannel > 0 :
			for ch in self.channelList:
				if int(ch[0]) == self.currentChannel :
					break
				chindex += 1

			self.ctrlListCHList.selectItem( chindex )

		#select item idx, print GUI of 'current / total'
		self.ctrlSelectItem.setLabel(str('%s / %s'% (self.ctrlListCHList.getSelectedPosition()+1, len(self.listItems))) )


	def initLabelInfo(self):
		print 'currentChannel[%s]' % self.currentChannel

		if( self.currentChannelInfo != [] ) :

			self.ctrlProgress.setPercent(0)
			self.ctrlProgress.setVisible(False)
			self.progress_idx = 0.0
			self.progress_max = 0.0
			self.pincodeEnter = 0x0

			self.ctrlSelectItem.setLabel(str('%s / %s'% (self.ctrlListCHList.getSelectedPosition()+1, len(self.listItems))) )
			#self.ctrlChannelName.setLabel('')
			self.ctrlEventName.setLabel('')
			self.ctrlEventTime.setLabel('')
			self.ctrlLongitudeInfo.setLabel('')
			self.ctrlCareerInfo.setLabel('')
			self.ctrlLockedInfo.setVisible(False)
			self.ctrlServiceTypeImg1.setImage('')
			self.ctrlServiceTypeImg2.setImage('')
			self.ctrlServiceTypeImg3.setImage('')

			#self.updateLabelInfo([], self.currentChannelInfo)
			#self.currentChannelInfo = []

		else:
			print 'has no channel'
		
			# todo 
			# show message box : has no channnel


	def initEPGEvent( self ) :
		ret = []

		try :
			if self.epgRecvPermission == True :
				ret = self.commander.epgevent_GetPresent()
				#ret=['epgevent_GetPresent'] + ret

				print 'epgevent_GetPresent[%s]'% ret

			else :
				label = self.ctrlListCHList.getSelectedItem().getLabel()
				channelNumbr = int(label[:4])

				for ch in self.channelList:
					if int(ch[0]) == channelNumbr :
						print 'found ch: getlabel[%s] ch[%s]'% (channelNumbr, ch[0])

						sid = int( ch[8] )
						tsid= int( ch[9] )
						onid= int( ch[10] )
						gmtFrom = self.localTime
						gmtUntil= 0
						maxCount= 1
						ret = self.commander.epgevent_GetList( sid, tsid, onid, gmtFrom, gmtUntil, maxCount )
						time.sleep(0.5)
						ret.append ( ch )
						#print 'ret[%s] len[%s]'% (ret[0], len(ret[0]) )
						print 'epgevent_GetList[%s]'% ret


		except Exception, e :
				print '[%s]%s():%s Error exception[%s]'% (	\
					self.__file__,							\
					currentframe().f_code.co_name,			\
					currentframe().f_lineno,				\
					e )

		return ret


	def updateServiceType(self, tvType):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'serviceType[%s]' % tvType


		if tvType == ElisEnum.E_TYPE_TV:
			return 'TV'
		elif tvType == ElisEnum.E_TYPE_RADIO:pass
		elif tvType == ElisEnum.E_TYPE_DATA:pass
		else:
			return 'etc'
			print 'unknown ElisEnum tvType[%s]'% tvType

	def updateLabelInfo(self, event, ch):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'ch info[%s]'% ch

		if len(ch) == self.chInfoArgument:

			if self.epgRecvPermission == True :
				#update channel name
				if is_digit(ch[3]):
					chName      = ch[2]
					serviceType = int(ch[3])
					ret = self.updateServiceType(serviceType)
					if ret != None:
						self.ctrlChannelName.setLabel( str('%s - %s'% (ret, chName)) )

			#update longitude info
			if is_digit(ch[3]) and is_digit(ch[0]) :
				chNumber    = int(ch[0])
				serviceType = int(ch[3])
				longitude = self.commander.satellite_GetByChannelNumber(chNumber, serviceType)
				if is_digit(longitude[0]):
					ret = GetSelectedLongitudeString(longitude)
					self.ctrlLongitudeInfo.setLabel(ret)

			#update lock-icon visible
			if is_digit(ch[4]) :
				mlock = int(ch[4])
				if mlock == 1:
					self.ctrlLockedInfo.setVisible(True)
					self.pincodeEnter |= 0x01

				
			#update career info
			if is_digit(ch[11]) :
				careerType = int(ch[11])
				if careerType == ElisEnum.E_CARRIER_TYPE_DVBS:
					ret = self.commander.channel_GetCarrierForDVBS()
					print 'channel_GetCarrierForDVBS[%s]'% ret
					if ret != []:
						polariztion = enumToString( 'Polarization', int(ret[5]) )
						careerLabel = '%s MHz, %s KS/S, %s'% (ret[2], ret[3], polariztion)
						self.ctrlCareerInfo.setLabel(careerLabel)

				elif careerType == ElisEnum.E_CARRIER_TYPE_DVBT:
					pass
				elif careerType == ElisEnum.E_CARRIER_TYPE_DVBC:
					pass
				elif careerType == ElisEnum.E_CARRIER_TYPE_INVALID:
					pass
				
			"""
			#is cas?
			if int(self.currentChannelInfo[5]) == 1:
				#scrambled
				self.pincodeEnter |= 0x01
			"""



		print 'event____[len:%s][%s]'% ( len(event), event )
		if len(event) == self.epgArgument:
			#update epgName uiID(304)
			self.ctrlEventName.setLabel(event[1])

			#update epgTime uiID(305)
			if is_digit(event[6]):
				self.progress_max = int(event[6])
				print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

				if is_digit(event[6]):
					self.epgStartTime = int( event[5] )
					self.epgDuration = int( event[6] )
					ret = epgInfoTime( self.localOffset, int(event[5]), int(event[6]))
					print 'epgInfoTime[%s]'% ret
					if ret != []:
						self.ctrlEventTime.setLabel(str('%s%s'% (ret[0], ret[1])))

				else:
					print 'value error EPGTime start[%s]' % event[5]
			else:
				print 'value error EPGTime duration[%s]' % event[6]

			#visible progress
			self.ctrlProgress.setVisible(True)

			#component
			component = event[8:17]
#			ret = epgInfoComponentImage(int(event[9]))
			ret = epgInfoComponentImage(component)				
			if len(ret) == 1:
				self.ctrlServiceTypeImg1.setImage(ret[0])
			elif len(ret) == 2:
				self.ctrlServiceTypeImg1.setImage(ret[0])
				self.ctrlServiceTypeImg2.setImage(ret[1])
			elif len(ret) == 3:
				self.ctrlServiceTypeImg1.setImage(ret[0])
				self.ctrlServiceTypeImg2.setImage(ret[1])
				self.ctrlServiceTypeImg3.setImage(ret[2])
			else:
				self.ctrlServiceTypeImg1.setImage('')
				self.ctrlServiceTypeImg2.setImage('')
				self.ctrlServiceTypeImg3.setImage('')


			#is Age? agerating check
			if is_digit(event[20]) :
				agerating = int(event[20])
				isLimit = util.ageLimit(self.commander, agerating)
				if isLimit == True :
					self.pincodeEnter |= 0x01
					print 'AgeLimit[%s]'% isLimit

		else:
			print 'event null'


		#popup pin-code dialog
		if self.pincodeEnter > 0 :
			msg1 = 'Enter PIN Code'
			msg2 = 'Current PIN Code'
			xbmcgui.Dialog().ok(msg1, msg2)


	@run_async
	def currentTimeThread(self):
		print '[%s():%s]begin_start thread'% (currentframe().f_code.co_name, currentframe().f_lineno)

		loop = 0
		#rLock = threading.RLock()
		while self.untilThread:
			#print '[%s():%s]repeat <<<<'% (currentframe().f_code.co_name, currentframe().f_lineno)

			#progress

			if  ( loop % 10 ) == 0 :
				print 'loop=%d' %loop
				self.updateLocalTime( )


			#local clock
			ret = epgInfoClock(1, self.localTime, loop)
			self.ctrlHeader3.setLabel(ret[0])
			self.ctrlHeader4.setLabel(ret[1])

			#self.nowTime += 1
			time.sleep(1)
			loop += 1

		print '[%s():%s]leave_end thread'% (currentframe().f_code.co_name, currentframe().f_lineno)


	@ui_locked2
	def updateLocalTime( self ) :
		
		try:
			ret = self.commander.datetime_GetLocalTime( )
			if len(ret) > 0 :
				self.localTime = int( ret[0] )
			else :
				self.localTime = 0

		except Exception, e:
			self.localTime = 0
			print 'Error datetime_GetLocalTime(), e[%s]'% e

		endTime = self.epgStartTime + self.epgDuration
		#endTime = self.epgStartTime + self.localOffset + self.epgDuration
		#print 'localoffset=%d localToime=%d epgStartTime=%d duration=%d' %(self.localOffset, self.localTime, self.epgStartTime, self.epgDuration )
		#print 'endtime=%d' %endTime

		pastDuration = endTime - self.localTime
		if pastDuration < 0 :
			pastDuration = 0

		if self.epgDuration > 0 :
			percent = pastDuration * 100/self.epgDuration
		else :
			percent = 0

		#print 'percent=%d' %percent
		self.ctrlProgress.setPercent( percent )

	
