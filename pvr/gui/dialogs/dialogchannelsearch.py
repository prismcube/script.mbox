
import xbmc
import xbmcgui
import time
import sys


from pvr.gui.basewindow import Action
from pvr.gui.basedialog import BaseDialog
from  pvr.tunerconfigmgr import *
import pvr.gui.dialogmgr as diamgr
import pvr.elismgr
#from pvr.util import run_async


# Control IDs
E_TV_LIST_ID			= 400
E_RADIO_LIST_ID			= 402
E_CANCEL_ID				= 300


# Scan MODE
E_SCAN_NONE				= 0
E_SCAN_SATELLITE		= 1
E_SCAN_TRANSPONDER		= 2



class DialogChannelSearch( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.commander = pvr.elismgr.getInstance( ).getCommander( )
		self.scanMode = E_SCAN_NONE
		self.isFinished = True
		self.eventBus = pvr.elismgr.getInstance().getEventBus()

		
	def onInit( self ):
		self.eventBus.register( self )	
		self.win = xbmcgui.getCurrentWindowId()
		self.isFinished = False	
		
		self.drawItem( )


	def onAction( self, action ):
		actionId = action.getId( )
		focusId = self.getFocusId( )
	
		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.abortScan( )

		elif actionId == Action.ACTION_MOVE_UP :
			pass
	
		elif actionId == Action.ACTION_MOVE_DOWN :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT :
			pass
				
		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass


	def onClick( self, controlId ):
		focusId = self.getFocusId( )

		if focusId == E_CANCEL_ID :
			self.abortScan( )

	def onFocus( self, controlId ):
		pass


	def drawItem( self ) :
		tvListItems = []
		radioListItems = []		
		for i in range( 10 ) :
			listItem = xbmcgui.ListItem( ' ', " ", "-", "-", "-" )
			tvListItems.append( listItem )
			radioListItems.append( listItem )			
		
		self.getControl( E_TV_LIST_ID ).addItems( tvListItems )
		self.getControl( E_RADIO_LIST_ID ).addItems( radioListItems )		


	def scanBySatellite( self, satelliteList ) :
		satellite = satelliteList[0] # ToDO send with satelliteList
		print 'scanBySatellite=%s' %satellite
		self.commander.channelscan_BySatellite( int(satellite[E_CONFIGURE_SATELLITE_LONGITUDE]), int(satellite[E_CONFIGURE_SATELLITE_BANDTYPE]))


	def scanByTransponder( self, longitude, band, transponderList ) :
		self.commander.channel_SearchByCarrier( longitude, band, transponderList )


 	def abortScan( self ) :
		if self.isFinished == False :
			if xbmcgui.Dialog( ).yesno('Confirm', 'Do you want abort channel scan?') == 1 :
				self.commander.channelscan_Abort( )
				self.isFinished == True

		if self.isFinished == True :
			self.eventBus.deregister( self )
			self.close( )
			

	def onEvent(self, event):

		print '----------->event bbb = %s' %event		
		if xbmcgui.getCurrentWindowId() == self.win :
			print '----------->event = %s' %event

	def updateScanProgress(self):
		print 'update progress'

