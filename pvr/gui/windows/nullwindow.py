import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import BaseWindow
from pvr.gui.basewindow import Action
from inspect import currentframe
import pvr.elismgr



class NullWindow(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		print 'lael98 check %d %s' %(currentframe().f_lineno, currentframe().f_code.co_filename)    
		print 'args=%s' % args[0]
		self.commander = pvr.elismgr.getInstance().getCommander()				
		self.lastFocusId = None

	def onInit(self):
		if not self.win:
			self.win = xbmcgui.Window(xbmcgui.getCurrentWindowId())

	def onAction(self, action):
		id = action.getId()

		if id == Action.ACTION_PREVIOUS_MENU:
			print 'lael98 check ation menu'
			winmgr.getInstance().showWindow( winmgr.WIN_ID_MAINMENU )

		elif id == Action.ACTION_PARENT_DIR:
			try :
				currentChannelInfo = self.commander.channel_GetCurrent()
				currentChannel = int( currentChannelInfo[0] )
				lastChannel = winmgr.getInstance().getWindow(winmgr.WIN_ID_CHANNEL_BANNER).getLastChannel( )
				if lastChannel > 0 and lastchannel != currentChannel :
					self.commander.channel_SetCurrent( lastChannel )
					winmgr.getInstance().getWindow(winmgr.WIN_ID_CHANNEL_BANNER).setLastChannel( currentChannel )
					winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_BANNER )

			except Exception, ex:
				print 'ERR prev channel'

		elif id == Action.ACTION_SELECT_ITEM:
			winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_LIST_WINDOW )
#			winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_BANNER )
			print 'lael98 check ation select'

		elif id == Action.ACTION_MOVE_LEFT:
			print 'youn check ation left'
			winmgr.getInstance().showWindow( winmgr.WIN_ID_TIMESHIFT_BANNER )

		elif id == Action.ACTION_SHOW_INFO	:
			winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_BANNER )
			
		elif id == Action.ACTION_PAGE_UP:
			channelInfo = self.commander.channel_GetCurrent()
			currentChannel = int( channelInfo[0] )
		
			channelInfo = self.commander.channel_GetPrev()
			prevChannel = int( channelInfo[0] )
			self.commander.channel_SetCurrent( prevChannel )
			
			winmgr.getInstance().getWindow(winmgr.WIN_ID_CHANNEL_BANNER).setLastChannel( currentChannel )
			winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_BANNER )		


		elif id == Action.ACTION_PAGE_DOWN:
			channelInfo = self.commander.channel_GetCurrent()
			currentChannel = int( channelInfo[0] )
		
			channelInfo = self.commander.channel_GetNext()
			nextChannel = int( channelInfo[0] )
			self.commander.channel_SetCurrent( nextChannel )
			
			winmgr.getInstance().getWindow(winmgr.WIN_ID_CHANNEL_BANNER).setLastChannel( currentChannel )
			winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_BANNER )		

		elif id == Action.REMOTE_2:
			winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_LIST2_WINDOW )

		else:
			print 'lael98 check ation unknown id=%d' %id


	def onClick(self, controlId):
		print "onclick(): control %s" % controlId


	def onFocus(self, controlId):
		print "onFocus(): control %s" % controlId
		self.lastFocusId = controlId


