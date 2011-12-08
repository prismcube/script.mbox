import xbmc
import xbmcgui
import sys

import pvr.gui.windowmgr as winmgr
from pvr.gui.basewindow import BaseWindow
from pvr.gui.basewindow import Action
from inspect import currentframe



class NullWindow(BaseWindow):
	def __init__(self, *args, **kwargs):
		BaseWindow.__init__(self, *args, **kwargs)
		print 'lael98 check %d %s' %(currentframe().f_lineno, currentframe().f_code.co_filename)    
		print 'args=%s' % args[0]
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
			print 'lael98 check ation parentdir'
		elif id == Action.ACTION_SELECT_ITEM:
			winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_LIST_WINDOW )
#			winmgr.getInstance().showWindow( winmgr.WIN_ID_CHANNEL_BANNER )
			print 'lael98 check ation select'
		elif id == Action.ACTION_MOVE_LEFT:
			print 'youn check ation left'
			winmgr.getInstance().showWindow( winmgr.WIN_ID_TIMESHIFT_BANNER )
		else:
			print 'lael98 check ation unknown id=%d' %id

	def onClick(self, controlId):
		print "onclick(): control %s" % controlId

	def onFocus(self, controlId):
		print "onFocus(): control %s" % controlId
		self.lastFocusId = controlId


