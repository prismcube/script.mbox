import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import BaseWindow, setWindowBusy
from pvr.gui.basewindow import Action
from pvr.elisenum import ElisEnum
from inspect import currentframe
from pvr.util import catchall, is_digit, run_async, epgInfoTime, epgInfoClock, epgInfoComponentImage, GetSelectedLongitudeString
import pvr.elismgr
from pvr.elisproperty import ElisPropertyEnum, ElisPropertyInt
from pvr.gui.guiconfig import FooterMask

import pvr.msg as m
import pvr.gui.windows.define_string as mm
import thread, time


class ChannelListWindow(BaseWindow):

	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		self.commander = pvr.elismgr.getInstance().getCommander()		

		self.eventBus = pvr.elismgr.getInstance().getEventBus()
		self.eventBus.register( self )

		#button flag isSelect
		self.flag11 = False # default, first time create this modal
		self.flag21 = False
		self.flag31 = False
		self.flag41 = False

		self.execute_OnlyOne = True
		
	def __del__(self):
		print '[%s():%s] destroyed ChannelBanner'% (currentframe().f_code.co_name, currentframe().f_lineno)

		# end thread updateEPGProgress()
		self.untilThread = False


	def onInit(self):
		print ' test init Channel List by shinjh333 '	
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		if not self.win:
			self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())

			self.listcontrol            = self.getControl( 50 )
			#self.ctrlEventClock         = self.getControl( 102 )
			self.ctrlHeader1            = self.getControl( 3000 )
			self.ctrlHeader2            = self.getControl( 3001 )
			self.ctrlHeader3            = self.getControl( 3002 )
			self.ctrlHeader4            = self.getControl( 3003 )
			
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

			#tab header group		
			self.ctrltabHeader10        = self.getControl( 210 )
			self.ctrltabHeader20        = self.getControl( 220 )
			self.ctrltabHeader30        = self.getControl( 230 )
			self.ctrltabHeader40        = self.getControl( 240 )
			
			#tab header button
			self.ctrltabHeader11        = self.getControl( 211 )
			self.ctrltabHeader21        = self.getControl( 221 )
			self.ctrltabHeader31        = self.getControl( 231 )
			self.ctrltabHeader41        = self.getControl( 241 )
			
			#tab header list
			self.ctrltabHeader12        = self.getControl( 212 )
			self.ctrltabHeader22        = self.getControl( 222 )
			self.ctrltabHeader32        = self.getControl( 232 )
			self.ctrltabHeader42        = self.getControl( 242 )

			#test ctrl
			#self.ctrlLbl                = self.getControl( 9001 )
			#self.ctrlBtn                = self.getControl( 9002 )

			#epg stb time
			self.ctrlHeader3.setLabel('')

			#tab header button label
			self.btnLabel_TabHeader11 = 'All Channel by Number'
			self.btnLabel_TabHeader21 = 'Satellite'
			self.btnLabel_TabHeader31 = 'FTA/CAS'
			self.btnLabel_TabHeader41 = 'Favorite'
			
			#etc
			self.listEnableFlag = False

		#initialize get channel list
		print ' test init Channel List by shinjh999 '	
		self.initTabHeader()

		#'All Channel' button click, only one when window open
		if self.execute_OnlyOne == True:
			self.execute_OnlyOne = False
			self.flag11 = True
			self.onClick(211)


		#self.getTabHeader()
		self.initChannelList()

		self.initLabelInfo()

		#run thread
		#elf.untilThread = True
		#self.updateLocalTime()

		#get epg event right now
		"""
		ret = []
		ret=self.commander.epgevent_GetPresent()
		if ret != []:
			ret=['epgevent_GetPresent'] + ret
			self.updateLabelInfo(ret)
		print 'epgevent_GetPresent[%s]'% ret
		"""

		channelInfo = self.commander.channel_GetCurrent()
		self.currentChannel = int ( channelInfo[0] )


	def onAction(self, action):

		id = action.getId()

		if id == Action.ACTION_PREVIOUS_MENU:
			print 'ChannelListWindow lael98 check action menu'
		elif id == Action.ACTION_SELECT_ITEM:
			print '<<<<< test youn: action ID[%s]' % id
			print 'tv_guide_last_selected[%s]' % action.getId()
			self.getTabHeader()
			
		elif id == Action.ACTION_PARENT_DIR:
			print 'lael98 check ation back'

			self.untilThread = False
			self.updateLocalTime().join()

			self.close( )
			self.listcontrol.reset()

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


	def onClick(self, controlId):
		print "ChannelListWindow onclick(): control %d" % controlId	
		if controlId == self.listcontrol.getId() :
			label = self.listcontrol.getSelectedItem().getLabel()
			channelNumbr = int(label[:4])
			ret = self.commander.channel_SetCurrent( channelNumbr, self.tabHeader_serviceType)

			if ret[0].upper() == 'TRUE' :
				if self.currentChannel == channelNumbr :
					self.untilThread = False
					self.updateLocalTime().join()

					winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_BANNER )

				else :
					winmgr.getInstance().getWindow(winmgr.WIN_ID_CHANNEL_BANNER).setLastChannel( self.currentChannel )


				self.currentChannel = channelNumbr
				self.currentChannelInfo = self.commander.channel_GetCurrent()

			self.ctrlSelectItem.setLabel(str('%s / %s'% (self.listcontrol.getSelectedPosition() + 1, len(self.listItems))) )
			self.initLabelInfo()

		elif controlId == self.ctrltabHeader11.getId():
			#group resize
			self.ctrltabHeader10.setPosition(200,120)
			self.ctrltabHeader20.setPosition(400+50,120)
			self.ctrltabHeader30.setPosition(600+50,120)
			self.ctrltabHeader40.setPosition(800+50,120)

			#button update label
			self.ctrltabHeader11.setLabel(self.ctrltabHeader12.getSelectedItem().getLabel())
			self.ctrltabHeader21.setLabel('Satellite')
			self.ctrltabHeader31.setLabel('FTA/CAS')
			self.ctrltabHeader41.setLabel('Favorite')

			self.ctrltabHeader11.setWidth(200)
			self.ctrltabHeader21.setWidth(150)
			self.ctrltabHeader31.setWidth(150)
			self.ctrltabHeader41.setWidth(150)

			#list select on visible, else list not visible
			if self.flag11 == False:
				self.flag11 = True
				self.flag21 = False
				self.flag31 = False
				self.flag41 = False
			else:
				self.flag11 = False

			self.ctrltabHeader12.setVisible(self.flag11)
			self.ctrltabHeader22.setVisible(False)
			self.ctrltabHeader32.setVisible(False)
			self.ctrltabHeader42.setVisible(False)


		elif controlId == self.ctrltabHeader21.getId():
			self.ctrltabHeader10.setPosition(200,120)
			self.ctrltabHeader20.setPosition(400,120)
			self.ctrltabHeader30.setPosition(600+50,120)
			self.ctrltabHeader40.setPosition(800+50,120)

			self.ctrltabHeader11.setLabel('All Channels')
			self.ctrltabHeader21.setLabel(self.ctrltabHeader22.getSelectedItem().getLabel())
			self.ctrltabHeader31.setLabel('FTA/CAS')
			self.ctrltabHeader41.setLabel('Favorite')
			self.ctrltabHeader11.setWidth(150)
			self.ctrltabHeader21.setWidth(200)
			self.ctrltabHeader31.setWidth(150)
			self.ctrltabHeader41.setWidth(150)

			if self.flag21 == False:
				self.flag21 = True
				self.flag11 = False
				self.flag31 = False
				self.flag41 = False
			else:
				self.flag21 = False

			self.ctrltabHeader12.setVisible(False)
			self.ctrltabHeader22.setVisible(self.flag21)
			self.ctrltabHeader32.setVisible(False)
			self.ctrltabHeader42.setVisible(False)

		elif controlId == self.ctrltabHeader31.getId():
			self.ctrltabHeader10.setPosition(200,120)
			self.ctrltabHeader20.setPosition(400,120)
			self.ctrltabHeader30.setPosition(600,120)
			self.ctrltabHeader40.setPosition(800+50,120)

			self.ctrltabHeader11.setLabel('All Channels')
			self.ctrltabHeader21.setLabel('Satellite')
			self.ctrltabHeader31.setLabel(self.ctrltabHeader32.getSelectedItem().getLabel())
			self.ctrltabHeader41.setLabel('Favorite')
			self.ctrltabHeader11.setWidth(150)
			self.ctrltabHeader21.setWidth(150)
			self.ctrltabHeader31.setWidth(200)
			self.ctrltabHeader41.setWidth(150)

			if self.flag31 == False:
				self.flag31 = True
				self.flag11 = False
				self.flag21 = False
				self.flag41 = False
			else:
				self.flag31 = False

			self.ctrltabHeader12.setVisible(False)
			self.ctrltabHeader22.setVisible(False)
			self.ctrltabHeader32.setVisible(self.flag31)
			self.ctrltabHeader42.setVisible(False)

		elif controlId == self.ctrltabHeader41.getId():
			self.ctrltabHeader10.setPosition(200,120)
			self.ctrltabHeader20.setPosition(400,120)
			self.ctrltabHeader30.setPosition(600,120)
			self.ctrltabHeader40.setPosition(800,120)

			self.ctrltabHeader11.setLabel('All Channels')
			self.ctrltabHeader21.setLabel('Satellite')
			self.ctrltabHeader31.setLabel('FTA/CAS')
			self.ctrltabHeader41.setLabel(self.ctrltabHeader42.getSelectedItem().getLabel())
			self.ctrltabHeader11.setWidth(150)
			self.ctrltabHeader21.setWidth(150)
			self.ctrltabHeader31.setWidth(150)
			self.ctrltabHeader41.setWidth(200)

			if self.flag41 == False:
				self.flag41 = True
				self.flag11 = False
				self.flag21 = False
				self.flag31 = False
			else:
				self.flag41 = False

			self.ctrltabHeader12.setVisible(False)
			self.ctrltabHeader22.setVisible(False)
			self.ctrltabHeader32.setVisible(False)
			self.ctrltabHeader42.setVisible(self.flag41)


	def onFocus(self, controlId):
		#print "onFocus(): control %d" % controlId
		"""
		if controlId == self.ctrltabHeader11.getId():
			self.listcontrol.setEnable(False)
			self.ctrltabHeader12.setVisible(True)
			self.ctrltabHeader22.setVisible(False)
			self.ctrltabHeader32.setVisible(False)
			self.ctrltabHeader42.setVisible(False)

		elif controlId == self.ctrltabHeader21.getId():
			self.listcontrol.setEnable(False)
			self.ctrltabHeader12.setVisible(False)
			self.ctrltabHeader32.setVisible(False)
			self.ctrltabHeader42.setVisible(False)

		elif controlId == self.ctrltabHeader31.getId():
			self.listcontrol.setEnable(False)
			self.ctrltabHeader12.setVisible(False)
			self.ctrltabHeader22.setVisible(False)
			self.ctrltabHeader42.setVisible(False)

		elif controlId == self.ctrltabHeader41.getId() :
			self.listcontrol.setEnable(False)
			self.ctrltabHeader12.setVisible(False)
			self.ctrltabHeader22.setVisible(False)
			self.ctrltabHeader32.setVisible(False)

		else:
			self.listcontrol.setEnable(True)
		"""



	def onEvent(self, event):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'event[%s]'% event
		
		if xbmcgui.getCurrentWindowId() == self.win :
			self.updateLabelInfo(event)
		else:
			print 'show screen is another windows page[%s]'% xbmcgui.getCurrentWindowId()
		

	def getTabHeader(self):
		"""
		self.flag11 = False
		self.flag21 = False
		self.flag31 = False
		self.flag41 = False
		self.ctrltabHeader12.setVisible(False)
		self.ctrltabHeader22.setVisible(False)
		self.ctrltabHeader32.setVisible(False)
		self.ctrltabHeader42.setVisible(False)
		"""

		idx_Sorting   = self.ctrltabHeader12.getSelectedPosition()
		idx_Satellite = self.ctrltabHeader22.getSelectedPosition()
		idx_FtaCas    = self.ctrltabHeader32.getSelectedPosition()
		idx_Favorite  = self.ctrltabHeader42.getSelectedPosition()


		if idx_Sorting == 0:
			self.tabHeader_channelsortMode = ElisEnum.E_SORT_BY_NUMBER
		elif idx_Sorting == 1:
			self.tabHeader_channelsortMode = ElisEnum.E_SORT_BY_ALPHABET
		elif idx_Sorting == 2:
			self.tabHeader_channelsortMode = ElisEnum.E_SORT_BY_HD

		print 'sort_idx[%s]'% self.tabHeader_channelsortMode


		#update button label from selected item at list
		if self.flag11:
			self.ctrltabHeader11.setLabel(self.ctrltabHeader12.getSelectedItem().getLabel())
		if self.flag21:
			self.ctrltabHeader21.setLabel(self.ctrltabHeader22.getSelectedItem().getLabel())
		if self.flag31:
			self.ctrltabHeader31.setLabel(self.ctrltabHeader32.getSelectedItem().getLabel())
		if self.flag41:
			self.ctrltabHeader41.setLabel(self.ctrltabHeader42.getSelectedItem().getLabel())

		#select and list hide
		if self.flag11 or self.flag21 or self.flag31 or self.flag41:
			#hide list
			self.flag11 = False
			self.flag21 = False
			self.flag31 = False
			self.flag41 = False
			self.ctrltabHeader12.setVisible(False)
			self.ctrltabHeader22.setVisible(False)
			self.ctrltabHeader32.setVisible(False)
			self.ctrltabHeader42.setVisible(False)

			#channel list update
			self.listcontrol.reset()
			self.initChannelList()
				

	def initTabHeader(self):
		print ' test init Channel List by shinjh44444'	
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		#header, footer init
		self.ctrlHeader1.setImage('IconHeaderTitleSmall.png')
		#self.ctrlHeader2.setLabel('TV-Channel List')
		self.ctrlHeader2.setLabel(m.strings(mm.LANG_TV_CHANNEL_LIST))


		#self.ctrlLbl.setLabel( m.strings(mm.LANG_LANGUAGE) )
		ret = xbmc.getLanguage()
		print 'getLanguage[%s]'% ret
		#self.ctrlBtn.setLabel(ret)



		self.ctrlHeader3.setLabel('')		
		self.ctrlHeader4.setLabel('')

		#self.setProperty('WindowType', 'ChannelList')
		self.setFooter( FooterMask.G_FOOTER_ICON_BACK_MASK | FooterMask.G_FOOTER_ICON_OK_MASK | FooterMask.G_FOOTER_ICON_RECORD_MASK )

		self.ctrltabHeader12.setVisible(self.flag11)
		self.ctrltabHeader22.setVisible(self.flag21)
		self.ctrltabHeader32.setVisible(self.flag31)
		self.ctrltabHeader42.setVisible(self.flag41)

		#sort list, This is fixed
		testlistItems = []
		testlistItems.append(xbmcgui.ListItem('All Channel by Number'))
		testlistItems.append(xbmcgui.ListItem('All Channel by Alphabet'))
		testlistItems.append(xbmcgui.ListItem('All Channel by HD/SD'))
		self.ctrltabHeader12.addItems( testlistItems )

		#satellite longitude list
		list_ = []
		testlistItems = []

		print ' test init Channel List by shinjh2 '
		list_ = self.commander.satellite_GetConfiguredList(1 )
		print 'satellite_GetConfiguredList[%s]'% list_
		for item in list_:
			ret = GetSelectedLongitudeString(item)
			testlistItems.append(xbmcgui.ListItem(ret))

		self.ctrltabHeader22.addItems( testlistItems )


		#FTA list
		testlistItems = []
		testlistItems.append(xbmcgui.ListItem('FTA(25)'))
		self.ctrltabHeader32.addItems( testlistItems )

		#Favorite list
		testlistItems = []
		testlistItems.append(xbmcgui.ListItem('1'))
		testlistItems.append(xbmcgui.ListItem('2'))
		testlistItems.append(xbmcgui.ListItem('3'))
		self.ctrltabHeader42.addItems( testlistItems )	


		#default init value for channel_GetList()
		self.tabHeader_serviceType     = ElisEnum.E_TYPE_TV
		self.tabHeader_zappingMode     = ElisEnum.E_MODE_ALL
		self.tabHeader_channelsortMode = ElisEnum.E_SORT_BY_DEFAULT

		"""
		#setting to tabHeader value
		self.tabHeader_Sorting_idx        = None
		self.tabHeader_Satellite_idx      = None
		self.tabHeader_FtaCas_idx         = None
		self.tabHeader_Favorite_idx       = None
		"""


	def initChannelList(self):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		self.currentChannel = -1
		self.channelList = []
		self.listItems = []
		#self.commander.channel_GetList( ElisEnum.E_TYPE_TV, ElisEnum.E_MODE_ALL, ElisEnum.E_SORT_BY_DEFAULT, self.channelList )
		print ' test init Channel List by shinjh1 '
		self.channelList = self.commander.channel_GetList( self.tabHeader_serviceType, self.tabHeader_zappingMode, self.tabHeader_channelsortMode )

		print 'sort[%s] channellist[%s]'% (self.tabHeader_channelsortMode, self.channelList)

		for ch in self.channelList:
			listItem = xbmcgui.ListItem("%04d %s"%( int(ch[0]), ch[2]),"-", "-", "-", "-")

			thum=icas=''
			if int(ch[4]) == 1 : thum='IconLockFocus.png'#'OverlayLocked.png'
			if int(ch[5]) == 1 : icas='IconCas.png'
			listItem.setProperty('lock', thum)
			listItem.setProperty('icas', icas)
			
			self.listItems.append(listItem)
		self.listcontrol.addItems( self.listItems )

		#detected to last focus
		self.currentChannelInfo = self.commander.channel_GetCurrent()
		self.currentChannel = int(self.currentChannelInfo[0])

		chindex = 0;
		if self.currentChannel > 0 :
			for ch in self.channelList:
				if int(ch[0]) == self.currentChannel :
					break
				chindex += 1

			self.listcontrol.selectItem( chindex )

		#select item idx, print GUI of 'current / total'
		self.ctrlSelectItem.setLabel(str('%s / %s'% (chindex + 1, len(self.listItems))) )



	def initLabelInfo(self):
		print 'currentChannel[%s]' % self.currentChannel
		
		if( self.currentChannelInfo != [] ) :

			self.ctrlProgress.setPercent(0)
			self.ctrlProgress.setVisible(False)
			self.progress_idx = 0.0
			self.progress_max = 0.0

			self.ctrlSelectItem.setLabel(str('%s / %s'% (self.listcontrol.getSelectedPosition() + 1, len(self.listItems))) )
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
			self.epgClock = self.commander.datetime_GetLocalTime()

			if is_digit(self.currentChannelInfo[3]):
				serviceType = int(self.currentChannelInfo[3])
				ret = self.updateServiceType(serviceType)
				if ret != None:
					self.ctrlChannelName.setLabel( str('%s - %s'% (ret, self.currentChannelInfo[2])) )

				#update longitude info
				longitude = self.commander.satellite_GetByChannelNumber(int(self.currentChannelInfo[0]), int(self.currentChannelInfo[3]))
				if is_digit(longitude[0]):
					ret = GetSelectedLongitudeString(longitude)
					self.ctrlLongitudeInfo.setLabel(ret)

				#update lock check
				if int(self.currentChannelInfo[4]) == 1:
					self.ctrlLockedInfo.setVisible(True)


		print 'event____[%s]'% event
		if event != [] and event[1] != 'NULL' and len(event) > 2:
			#update epgName uiID(304)
			self.ctrlEventName.setLabel(event[2])

			#update epgTime uiID(305)
			if is_digit(event[7]):
				self.progress_max = int(event[7])
				print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

				if is_digit(event[6]):
					timeZone = self.commander.datetime_GetLocalOffset()
					ret = epgInfoTime(timeZone[0], int(event[6]), int(event[7]))
					print 'epgInfoTime[%s]'% ret
					if ret != []:
						self.ctrlEventTime.setLabel(str('%s%s'% (ret[0], ret[1])))

				else:
					print 'value error EPGTime start[%s]' % event[6]
			else:
				print 'value error EPGTime duration[%s]' % event[7]

			#visible progress
			self.ctrlProgress.setVisible(True)

			#component
			component = event[9:18]
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

		else:
			print 'event null'


		
		#self.ctrlCareerInfo.setLabel()


		#list_ = []
		#ret = self.commander.satellite_GetConfiguredList(0, list_)
		#ret = self.commander.satellite_GetList(0, list_)
		#ret = self.commander.satellite_GetByChannelNumber(int(self.currentChannelInfo[0]), int(self.currentChannelInfo[3]))
		#ret = self.commander.satelliteconfig_GetList(0, list_)
		#ret = self.commander.satellite_Get(192, 1)
		#print 'ret[%s] list_[%s]'% (ret, list_)


	@run_async
	def updateLocalTime(self):
		print '[%s():%s]begin_start thread'% (currentframe().f_code.co_name, currentframe().f_lineno)

		nowTime = time.time()
		while self.untilThread:
			print '[%s():%s]repeat <<<<'% (currentframe().f_code.co_name, currentframe().f_lineno)

			#progress
			if self.progress_max > 0:
				print 'progress_idx[%s] getPercent[%s]' % (self.progress_idx, self.ctrlProgress.getPercent())

				self.ctrlProgress.setPercent(self.progress_idx)

				self.progress_idx += 100.0 / self.progress_max
				if self.progress_idx > 100:
					self.progress_idx = 100
			else:
				print 'value error progress_max[%s]' % self.progress_max


			#local clock
			if is_digit(self.epgClock[0]):
				ret = epgInfoClock(1, nowTime, int(self.epgClock[0]))
				self.ctrlHeader3.setLabel(ret[0])
				self.ctrlHeader4.setLabel(ret[1])

			else:
				print 'value error epgClock[%s]' % ret

			time.sleep(1)

		print '[%s():%s]leave_end thread'% (currentframe().f_code.co_name, currentframe().f_lineno)

