#
#  MythBox for XBMC - http://mythbox.googlecode.com
#  Copyright (C) 2011 analogue@yahoo.com
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
import os
import sys
import xbmc
import xbmcgui
import xbmcaddon
import time

from inspect import currentframe
from pvr.bus import EventBus
import pvr.elismgr
import pvr.gui.windowmgr as windowmgr
from pvr.util import run_async, hasPendingWorkers, waitForWorkersToDie
from pvr.elistest import ElisTest

		
__launcher = None

def getInstance():
	global __launcher
	if not __launcher:
		__launcher = Launcher()
	return __launcher

class Launcher(object):

	def __init__(self):
		self.isFailed = False
		self.status = 'Init'
		self.shutdownReceived = False
		self.shutdowning = False		

	def run(self):
		try:
			try:
				time.sleep(1)
				self.initElisMgr()
				self.doElisTest()				
				self.initWindowMgr()
				time.sleep(1)
			except Exception, ex:
				if not self.isFailed:
					self.failure(ex)
		finally:
			print 'Launcher end'

	def failure(self, cause):
		msg = 'Status:%s - Error: %s' % (self.status, cause)
		print 'lael98 log %s' %msg
		xbmcgui.Dialog().ok('Error', 'Status: %s' % self.status, 'Exception: %s' % str(cause))

	def initElisMgr(self):
		self.stage = 'Init ElisMgr'
		pvr.elismgr.getInstance().run()
		print 'test lael98'
		self.commander = pvr.elismgr.getInstance().getCommander()
		self.commander.setElisReady()


	def initWindowMgr(self):
		pvr.gui.windowmgr.getInstance().showWindow( windowmgr.WIN_ID_NULLWINDOW )


	def powerOff( self ) :
		self.shutdown()
		xbmc.executebuiltin('xbmc.ShutDown')


	def shutdown(self):
		print '------------->shut down %d' %self.shutdowning
		if not self.shutdowning:
			self.shutdowning = True
			print '------------->shut shutdowning=%d abortRequested=%d' %(self.shutdowning,xbmc.abortRequested)
			
			pvr.elismgr.getInstance().shutdown()

			if hasPendingWorkers():
				waitForWorkersToDie(10.0) # in seconds
			
			print '------------->shut do end'
		print '<-------------shut down'

	def doElisTest(self):
		test = ElisTest()
		test.testAll()

