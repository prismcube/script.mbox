
import xbmc
import xbmcgui
import time
import sys


from pvr.gui.basewindow import Action
from pvr.gui.basedialog import BaseDialog
from  pvr.tunerconfigmgr import *
import pvr.gui.dialogmgr as diamgr
from elisevent import ElisEvent
from elisenum import ElisEnum

import pvr.elismgr

#from pvr.util import run_async



# Control IDs
E_TRANSPONDER_INFO_ID		= 104
E_PROGRESS_ID				= 200
E_TV_LIST_ID				= 400
E_RADIO_LIST_ID				= 402
E_CANCEL_ID					= 300


# Scan MODE
E_SCAN_NONE					= 0
E_SCAN_SATELLITE			= 1
E_SCAN_TRANSPONDER			= 2



class DialogChannelSearch( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.commander = pvr.elismgr.getInstance( ).getCommander( )
		self.scanMode = E_SCAN_NONE
		self.isFinished = True
		self.eventBus = pvr.elismgr.getInstance().getEventBus()
		self.transponderList = []
		self.satelliteList = []
		self.longitude = 0
		self.band = 0

	def onInit( self ):
		self.eventBus.register( self )
		self.win = xbmcgui.getCurrentWindowId()
		self.isFinished = False	

		self.tvListItems = []
		self.radioListItems = []		

		self.ctrlProgress = self.getControl( E_PROGRESS_ID )
		self.ctrlTransponderInfo = self.getControl( E_TRANSPONDER_INFO_ID )		

		self.scanStart( )
		self.drawItem( )


	def onAction( self, action ):
		actionId = action.getId( )
		focusId = self.getFocusId( )
	
		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.scanAbort( )

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
			self.scanAbort( )

	def onFocus( self, controlId ):
		pass


	def drawItem( self ) :

		count = len( self.newTvChannels )
		for i in range( count ) :
			listItem = xbmcgui.ListItem( ' ', " ", "-", "-", "-" )
			self.tvListItems.append( listItem )


		count = len( self.newRadioChannels )
			
		self.getControl( E_TV_LIST_ID ).addItems( self.tvListItems )
		self.getControl( E_RADIO_LIST_ID ).addItems( self.radioListItems )


	def setSatellite( self, satelliteList ) :
		print 'scanBySatellite=%s' %satellite
		self.scanMode = E_SCAN_SATELLITE 
		self.satelliteList = satelliteList


	def setTransponder( self, longitude, band, transponderList ) :
		print 'scanByTransponder=%s' %transponderList
		self.scanMode = E_SCAN_TRANSPONDER	
		self.longitude = longitude
		self.band = band		
		self.transponderList = transponderList


	def scanStart( self ) :
		print 'scanMode=%d' %self.scanMode
		if self.scanMode == E_SCAN_SATELLITE :
			satellite = self.satelliteList[0] # ToDO send with satelliteList
			self.commander.channelscan_BySatellite( int(satellite[0]), int(satellite[1]) )
		elif self.scanMode == E_SCAN_TRANSPONDER :
			self.commander.channel_SearchByCarrier( self.longitude, self.band, self.transponderList )
		else :
			self.isFinished == True


	def scanAbort( self ) :
		if self.isFinished == False :
			if xbmcgui.Dialog( ).yesno('Confirm', 'Do you want abort channel scan?') == 1 :
				self.commander.channelscan_Abort( )
				self.isFinished == True

		if self.isFinished == True :
			self.eventBus.deregister( self )
			self.close( )
			

	def onEvent( self, event ):

		if xbmcgui.getCurrentWindowId() == self.win :
 
			if event[0] == ElisEvent.ElisScanAddChannel :
				self.updateAddChannel( event )
 
			elif event[0] == ElisEvent.ElisScanProgress :
				self.updateScanProgress( event )



	def updateScanProgress(self, event ):
		print 'update progress'
		allCount = int( event[1] )
		currentIndex = int( event[2] )
		finished = int( event[3] )
		carrierType = int( event[4] )

		logitude = int( event[5] )
		band = int( event[6] )		
		
		frequency = int( event[7] )
		symbolrate = int( event[8] )
		fecValude = int( event[9] )
		polarization =  int( event[10] )

		percent = int( currentIndex*100/allCount )
		self.ctrlProgress.setPercent( percent )	

		strPol = 'V'
		if polarization == ElisEnum.E_LNB_HORIZONTAL or polarization == ElisEnum.E_LNB_LEFT :
			strPol = 'H'

		strTransponderInfo = '%d Mhz/%d %s' %( frequency, symbolrate, strPol )
		self.ctrlTransponderInfo.setLabel( strTransponderInfo )

		if finish :
			self.isFinished == True
			xbmcgui.Dialog( ).ok('Confirm', 'Channel Search Finished')


	def updateAddChannel(self, event ):
		"""
		print 'update addchnnel'
		channelName = event[3]
		serviceType = int( event[4] )
		print 'update addchnnel channelName=%s serviceType=%d' %( channelName, serviceType )
		"""


