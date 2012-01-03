import xbmc
import xbmcgui
import sys

import pvr.gui.WindowMgr as winmgr
from pvr.gui.BaseWindow import BaseWindow
from pvr.gui.BaseWindow import Action
from pvr.gui.BaseDialog import BaseDialog
from ElisEnum import ElisEnum
from inspect import currentframe
from pvr.Util import is_digit, RunThread, epgInfoTime, epgInfoClock, epgInfoComponentImage, GetSelectedLongitudeString, enumToString
import pvr.Util as util
import pvr.ElisMgr
from ElisProperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.guiconfig import FooterMask

import pvr.msg as m
import pvr.gui.windows.define_string as mm
import thread, time


class ChannelListWindow_a(BaseWindow):

	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		self.mCommander = pvr.ElisMgr.getInstance().getCommander()		

		self.mEventBus = pvr.ElisMgr.getInstance().getEventBus()
		#self.mEventBus.register( self )

		#submenu list
		self.list_AllChannel= []
		self.list_Satellite = []
		self.list_CasList   = []
		self.list_Favorite  = []

		self.execute_OnlyOne = True
		self.nowTime = 0
		self.eventID = 0

		self.pincodeEnter = 0x0
		
	def __del__(self):
		print '[%s():%s] destroyed ChannelBanner'% (currentframe().f_code.co_name, currentframe().f_lineno)

		# end thread updateEPGProgress()
		self.untilThread = False


	def onInit(self):
		self.win = xbmcgui.getCurrentWindowId()
		print '[%s():%s]winID[%d]'% (currentframe().f_code.co_name, currentframe().f_lineno, self.win)

		self.epgStartTime = 0
		self.epgDuration = 0
		self.localOffset = int( self.mCommander.datetime_GetLocalOffset()[0] )
		

		#header
		self.ctrlHeader1            = self.getControl( 3000 )
		self.ctrlHeader2            = self.getControl( 3001 )
		self.ctrlHeader3            = self.getControl( 3002 )
		self.ctrlHeader4            = self.getControl( 3003 )

		self.ctrlLblPath            = self.getControl( 10 )

		#main menu
		self.ctrlBtnMenu            = self.getControl( 101 )
		self.ctrlListMainmenu       = self.getControl( 102 )
		
		#sub menu list
		self.ctrlListSubmenu        = self.getControl( 202 )

		#ch list
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
		self.initTabHeader()

		"""
		#'All Channel' button click, only one when window open
		if self.execute_OnlyOne == True:
			self.execute_OnlyOne = False
			self.flag11 = True
			self.onClick(211)
		"""


		#self.getTabHeader()
		self.initChannelList()

		self.initLabelInfo()


		#get epg event right now
		ret = []
		ret=self.mCommander.epgevent_GetPresent()
		if ret != []:
			#ret=['epgevent_GetPresent'] + ret
			self.updateLabelInfo(ret)
		print 'epgevent_GetPresent[%s]'% ret

		channelInfo = self.mCommander.channel_GetCurrent()
		self.currentChannel = int ( channelInfo[0] )

		#run thread
		self.untilThread = True
		self.updateLocalTime()


	def onAction(self, action):

		id = action.getId()

		if id == Action.ACTION_PREVIOUS_MENU:
			print 'ChannelListWindow lael98 check action menu'
		elif id == Action.ACTION_SELECT_ITEM:
			print '<<<<< test youn: action ID[%s]' % id
			print 'tv_guide_last_selected[%s]' % action.getId()
			#self.getTabHeader()
			
		elif id == Action.ACTION_PARENT_DIR:
			print 'lael98 check ation back'

			self.untilThread = False
			self.updateLocalTime().join()
			self.ctrlListCHList.reset()

			self.close( )

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


	def onClick(self, controlId):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno), \
		      'ChannelListWindow onclick(): control %d' % controlId	
		if controlId == self.ctrlListCHList.getId() :

			label = self.ctrlListCHList.getSelectedItem().getLabel()
			channelNumbr = int(label[:4])
			ret = self.mCommander.channel_SetCurrent( channelNumbr, self.chlist_serviceType)

			if ret[0].upper() == 'TRUE' :
				if self.pincodeEnter == 0x00 :
					if self.currentChannel == channelNumbr :
						self.untilThread = False
						self.updateLocalTime().join()

						winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_BANNER )

					else :
						winmgr.getInstance().getWindow(winmgr.WIN_ID_CHANNEL_BANNER).setLastChannel( self.currentChannel )

				self.currentChannel = channelNumbr
				self.currentChannelInfo = self.mCommander.channel_GetCurrent()


			self.ctrlSelectItem.setLabel(str('%s / %s'% (self.ctrlListCHList.getSelectedPosition()+1, len(self.listItems))) )
			self.initLabelInfo()

		elif controlId == self.ctrlBtnMenu.getId() :
			#list view

			idx_menu = self.ctrlListMainmenu.getSelectedPosition()
			print 'focus[%s] idx_main[%s]'% (controlId, idx_menu)

			if idx_menu == 4 :
				self.untilThread = False
				self.updateLocalTime().join()
				self.ctrlListCHList.reset()

				self.close( )

			else :
				pass
				#self.subManuAction( 0, idx_menu )

		elif controlId == self.ctrlListSubmenu.getId() :
			#list action

			idx_menu = self.chlist_zappingMode
			print 'focus[%s] idx_sub[%s]'% (controlId, idx_menu)

			self.subManuAction( 1, self.chlist_zappingMode )


	def onFocus(self, controlId):
		#print "onFocus(): control %d" % controlId
		pass


	def onEvent(self, event):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'event[%s]'% event

		if self.win == xbmcgui.getCurrentWindowId():
			msg = event[0]
			
			if msg == 'Elis-CurrentEITReceived' :

				if int(event[4]) != self.eventID :			
					ret = self.mCommander.epgevent_GetPresent( )
					if len( ret ) > 0 :
						self.eventID = int( event[4] )
						self.updateLabelInfo( ret )

					#ret = self.mCommander.epgevent_Get(self.eventID, int(event[1]), int(event[2]), int(event[3]), int(self.epgClock[0]) )
			else :
				print 'event unknown[%s]'% event
		else:
			print 'channellist_a winID[%d] this winID[%d]'% (self.win, xbmcgui.getCurrentWindowId())


	def subManuAction(self, action, idx_menu):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

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
				label1 = enumToString('mode', self.chlist_zappingMode)
				self.ctrlLblPath.setLabel( label1.title() )


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
				self.getChannelList( self.chlist_serviceType, self.chlist_zappingMode, sortingMode, 0, 0, 0, '' )

				idx_AllChannel = self.ctrlListSubmenu.getSelectedPosition()
				item = self.list_AllChannel[idx_AllChannel]
				print 'cmd[channel_GetList] idx_AllChannel[%s] sort[%s] ch_list[%s]'% (idx_AllChannel, self.chlist_channelsortMode, self.channelList)

			elif idx_menu == ElisEnum.E_MODE_SATELLITE:
				idx_Satellite = self.ctrlListSubmenu.getSelectedPosition()
				item = self.list_Satellite[idx_Satellite]
				self.getChannelList( self.chlist_serviceType, self.chlist_zappingMode, self.chlist_channelsortMode, int(item[0]), int(item[1]), 0, '' )
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

				self.getChannelList( self.chlist_serviceType, self.chlist_zappingMode, self.chlist_channelsortMode, 0, 0, caid, '' )

				item = self.list_CasList[idx_FtaCas]
				print 'cmd[channel_GetListByFTACas] idx_FtaCas[%s] list_CasList[%s] ch_list[%s]'% ( idx_FtaCas, item, self.channelList )

			elif idx_menu == ElisEnum.E_MODE_FAVORITE:
				idx_Favorite = self.ctrlListSubmenu.getSelectedPosition()
				item = self.list_Favorite[idx_Favorite]
				self.getChannelList( self.chlist_serviceType, self.chlist_zappingMode, self.chlist_channelsortMode, 0, 0, 0, item[0] )
				print 'cmd[channel_GetListByFavorite] idx_Favorite[%s] list_Favorite[%s] ch_list[%s]'% ( idx_Favorite, item, self.channelList )


			if self.channelList != [] :
				#channel list update
				self.ctrlListCHList.reset()
				self.initChannelList()

				#path tree, Mainmenu/Submanu
				#label1 = self.ctrlListMainmenu.getSelectedItem().getLabel()
				label1 = enumToString('mode', self.chlist_zappingMode)
				label2 = self.ctrlListSubmenu.getSelectedItem().getLabel()
				self.ctrlLblPath.setLabel( '%s/%s'% (label1.title(), label2.title()) )

				#save zapping mode
				#ret = self.mCommander.zappingmode_SetCurrent( self.chlist_zappingMode, self.chlist_channelsortMode, self.chlist_serviceType )
				#print 'set zappingmode_SetCurrent[%s]'% ret


	def getChannelList(self, mType, mMode, mSort, mLongitude, mBand, mCAid, favName ):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		try :
			if mMode == ElisEnum.E_MODE_ALL :
				self.channelList = self.mCommander.channel_GetList( mType, mMode, mSort )

			elif mMode == ElisEnum.E_MODE_SATELLITE :
				self.channelList = self.mCommander.channel_GetListBySatellite( mType, mMode, mSort, mLongitude, mBand )

			elif mMode == ElisEnum.E_MODE_CAS :
				self.channelList = self.mCommander.channel_GetListByFTACas( mType, mMode, mSort, mCAid )
				
			elif mMode == ElisEnum.E_MODE_FAVORITE :
				self.channelList = self.mCommander.channel_GetListByFavorite( mType, mMode, mSort, favName )

			elif mMode == ElisEnum.E_MODE_NETWORK :
				pass

		except Exception, e:
			print 'getChannelList Error[%s]'% e


	def getTabHeader(self):
		pass

		#TODO
		#get zapping last mode

				

	def initTabHeader(self):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		#header init
		self.ctrlHeader1.setImage('IconHeaderTitleSmall.png')
		#self.ctrlHeader2.setLabel('TV-Channel List')
		self.ctrlHeader2.setLabel(m.strings(mm.LANG_TV_CHANNEL_LIST))

		#self.ctrlLbl.setLabel( m.strings(mm.LANG_LANGUAGE) )
		ret = xbmc.getLanguage()
		print 'getLanguage[%s]'% ret
		#self.ctrlBtn.setLabel(ret)

		self.ctrlHeader3.setLabel('')		
		self.ctrlHeader4.setLabel('')

		#footer init
		#self.setProperty('WindowType', 'ChannelList')
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK | FooterMask.G_FOOTER_ICON_OK_MASK | FooterMask.G_FOOTER_ICON_RECORD_MASK )

		#main/sub menu init
		self.ctrlListMainmenu.reset()
		self.ctrlListSubmenu.reset()


		#get last zapping mode
		ret = []
		ret = self.mCommander.zappingmode_GetCurrent()
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

		#satellite longitude list
		self.list_Satellite = self.mCommander.satellite_GetConfiguredList( ElisEnum.E_SORT_NAME )
		print 'satellite_GetConfiguredList[%s]'% self.list_Satellite

		#FTA list
		self.list_CasList = self.mCommander.fta_cas_GetList( ElisEnum.E_TYPE_TV )
		print 'channel_GetFTACasList[%s]'% self.list_CasList

		#Favorite list
		self.list_Favorite = self.mCommander.favorite_GetList( ElisEnum.E_TYPE_TV )
		print 'channel_GetFavoriteList[%s]'% self.list_Favorite

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
		self.ctrlLblPath.setLabel( '%s/%s'% (label1.title(), label2.title()) )


		#get channel list by last on zapping mode, sorting, service type
		self.currentChannel = -1
		self.channelList = []
		self.channelList = self.mCommander.channel_GetList( self.chlist_serviceType, self.chlist_zappingMode, self.chlist_channelsortMode )
		#self.getChannelList(self.chlist_serviceType, self.chlist_zappingMode, self.chlist_channelsortMode, 0, 0, 0, '')
		print 'zappingMode[%s] sortMode[%s] serviceType[%s] channellist[%s]'% \
			( enumToString('mode', self.chlist_zappingMode), \
			  enumToString('sort', self.chlist_channelsortMode), \
			  enumToString('type', self.chlist_serviceType), \
			  self.channelList )


	def initChannelList(self):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		self.listItems = []
		sublist = []
		for ch in self.channelList:
			#skip ch
			if int(ch[12]) == 1 :
				continue

			listItem = xbmcgui.ListItem("%04d %s"%( int(ch[0]), ch[2]),"-", "-", "-", "-")
			subItem  = xbmcgui.ListItem("%04d %s"%( int(ch[0]), ch[2]),"-", "-", "-", "-")

			thum=icas=''
			if int(ch[4]) == 1 : thum='IconLockFocus.png'#'OverlayLocked.png'
			if int(ch[5]) == 1 : icas='IconCas.png'
			listItem.setProperty('lock', thum)
			listItem.setProperty('icas', icas)
			self.listItems.append(listItem)

			sublist.append(subItem)

		self.ctrlListCHList.addItems( self.listItems )
		self.ctrlListSubmenu.addItems( sublist )

		#detected to last focus
		self.currentChannelInfo = self.mCommander.channel_GetCurrent()
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
			self.ctrlChannelName.setLabel('')
			self.ctrlEventName.setLabel('')
			self.ctrlEventTime.setLabel('')
			self.ctrlLongitudeInfo.setLabel('')
			self.ctrlCareerInfo.setLabel('')
			self.ctrlLockedInfo.setVisible(False)
			self.ctrlServiceTypeImg1.setImage('')
			self.ctrlServiceTypeImg2.setImage('')
			self.ctrlServiceTypeImg3.setImage('')

			self.updateLabelInfo([])
			#self.currentChannelInfo = []

		else:
			print 'has no channel'
		
			# todo 
			# show message box : has no channnel


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

	def updateLabelInfo(self, event):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'ch info[%s]'% self.currentChannelInfo

		if self.currentChannelInfo != []:
			self.epgClock = self.mCommander.datetime_GetLocalTime()

			#update channel name
			if is_digit(self.currentChannelInfo[3]):
				chName      = self.currentChannelInfo[2]
				serviceType = int(self.currentChannelInfo[3])
				ret = self.updateServiceType(serviceType)
				if ret != None:
					self.ctrlChannelName.setLabel( str('%s - %s'% (ret, chName)) )

			#update longitude info
			if is_digit(self.currentChannelInfo[3]) and is_digit(self.currentChannelInfo[0]) :
				chNumber    = int(self.currentChannelInfo[0])
				serviceType = int(self.currentChannelInfo[3])
				longitude = self.mCommander.satellite_GetByChannelNumber(chNumber, serviceType)
				if is_digit(longitude[0]):
					ret = GetSelectedLongitudeString(longitude)
					self.ctrlLongitudeInfo.setLabel(ret)

			#update lock-icon visible
			if is_digit(self.currentChannelInfo[4]) :
				mlock = int(self.currentChannelInfo[4])
				if mlock == 1:
					self.ctrlLockedInfo.setVisible(True)
					self.pincodeEnter |= 0x01

			#update career info
			if is_digit(self.currentChannelInfo[11]) :
				careerType = int(self.currentChannelInfo[11])
				if careerType == ElisEnum.E_CARRIER_TYPE_DVBS:
					ret = self.mCommander.channel_GetCarrierForDVBS()
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
		if len(event) == 21:
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
				isLimit = util.ageLimit(self.mCommander, agerating)
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


	@RunThread
	def updateLocalTime(self):
		print '[%s():%s]begin_start thread'% (currentframe().f_code.co_name, currentframe().f_lineno)

		loop = 0
		while self.untilThread:
			#print '[%s():%s]repeat <<<<'% (currentframe().f_code.co_name, currentframe().f_lineno)

			#progress
			if  ( loop % 10 ) == 0 :
				ret = self.mCommander.datetime_GetLocalTime( )
				localTime = int( ret[0] )

				endTime = self.epgStartTime + self.localOffset + self.epgDuration
				#print 'localoffset=%d localToime=%d epgStartTime=%d duration=%d' %(self.localOffset, localTime, self.epgStartTime, self.epgDuration )
				#print 'endtime=%d' %endTime

				pastDuration = endTime - localTime
				if pastDuration < 0 :
					pastDuration = 0

				if self.epgDuration > 0 :
					percent = pastDuration * 100/self.epgDuration
				else :
					percent = 0

				#print 'percent=%d' %percent
				self.ctrlProgress.setPercent( percent )



			#local clock
			ret = epgInfoClock(1, localTime, loop)
			self.ctrlHeader3.setLabel(ret[0])
			self.ctrlHeader4.setLabel(ret[1])

			#self.nowTime += 1
			time.sleep(1)
			loop += 1

		print '[%s():%s]leave_end thread'% (currentframe().f_code.co_name, currentframe().f_lineno)

