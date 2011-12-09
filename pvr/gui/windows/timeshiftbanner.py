import xbmc
import xbmcgui
import sys
import time

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import BaseWindow
from pvr.gui.basewindow import Action

import pvr.elismgr
'''
from pvr.elisevent import ElisAction, ElisEnum //by shinjh
'''
from pvr.elisaction import ElisAction
from pvr.elisenum import ElisEnum
from pvr.net.net import EventRequest

#from threading import Thread
from pvr.util import run_async, is_digit, Mutex, epgInfoTime, epgInfoClock, epgInfoComponentImage, GetSelectedLongitudeString #, synchronized, sync_instance
import thread

#debug log
import logging
from inspect import currentframe

log = logging.getLogger('mythbox.ui')
mlog = logging.getLogger('mythbox.method')


class TimeShiftBanner(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		print 'f_coname[%s] f_lineno[%d] co_filename[%s]' %(currentframe().f_code.co_name, currentframe().f_lineno, currentframe().f_code.co_filename)    
		print 'args[0]=[%s]' % args[0]
		print 'args[1]=[%s]' % args[1]

		self.lastFocusId = None
		self.eventBus = pvr.elismgr.getInstance().getEventBus()
		self.eventBus.register( self )
		self.commander = pvr.elismgr.getInstance().getCommander()

		self.currentChannel=[]

		#push push test test

		#time track


	def __del__(self):
		print '[%s():%s] destroyed ChannelBanner'% (currentframe().f_code.co_name, currentframe().f_lineno)

		# end thread updateLocalTime()
		self.untilThread = False

	def onInit(self):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		if not self.win:
			self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())

			self.imgTV    = 'confluence/tv.png'
			self.toggleFlag=False

		#get channel
		self.currentChannel = self.commander.channel_GetCurrent()

		self.initLabelInfo()
	
		if is_digit(self.currentChannel[3]):
			self.updateServiceType(int(self.currentChannel[3]))


		#run thread
		self.untilThread = True
		#self.updateLocalTime()



	def onAction(self, action):
		id = action.getId()
		focusid = self.getFocusId()
		
		if id == Action.ACTION_PREVIOUS_MENU:
			print 'youn check action menu'

		elif id == Action.ACTION_SELECT_ITEM:
			print '===== test youn: ID[%s]' % id
			log.debug('youn:%s' % id)
	
		elif id == Action.ACTION_PARENT_DIR:
			print 'youn check ation back'

			# end thread updateLocalTime()
			self.untilThread = False
			#self.updateLocalTime().join()

			self.close( )
#			winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_LIST_WINDOW )
#			winmgr.getInstance().showWindow( winmgr.WIN_ID_NULLWINDOW )
#			winmgr.shutdown()


		elif id == Action.ACTION_PAGE_UP:
			self.channelTune(id)

		elif id == Action.ACTION_PAGE_DOWN:
			self.channelTune(id)
		
		else:
			#print 'youn check action unknown id=%d' % id
			#self.channelTune(id)
			pass


	def onClick(self, controlId):
		print "onclick(): control %d" % controlId



	def onFocus(self, controlId):
		#print "onFocus(): control %d" % controlId
		pass

	def onEvent(self, event):
		self.eventCopy = event

		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		#print 'eventCopy[%s]'% self.eventCopy

		if xbmcgui.getCurrentWindowId() == 13009 :
			self.updateONEvent(self.eventCopy)
		else:
			print 'show screen is another windows page[%s]'% xbmcgui.getCurrentWindowId()

	def channelTune(self, actionID):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)		
		print 'tuneActionID[%s]'% actionID


	def updateONEvent(self, event):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'event[%s]'% event


	@run_async
	def updateLocalTime(self):
		print '[%s():%s]start thread <<<< begin'% (currentframe().f_code.co_name, currentframe().f_lineno)
		#print 'untilThread[%s] self.progress_max[%s]' % (self.untilThread, self.progress_max)

		while self.untilThread:
			time.sleep(1)

		print '[%s():%s]end thread <<<< begin'% (currentframe().f_code.co_name, currentframe().f_lineno)

	def initLabelInfo(self):
		print '[%s():%s]Initialize Label'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'currentChannel[%s]' % self.currentChannel
		
		# todo 
		# show message box : has no channnel


	def updateServiceType(self, tvType):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)
		print 'serviceType[%s]' % tvType


			

	def showEPGDescription(self, focusid, event):
		print '[%s():%s]'% (currentframe().f_code.co_name, currentframe().f_lineno)

		
		
		

