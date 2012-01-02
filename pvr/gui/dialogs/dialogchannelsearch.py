
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
		self.winId = xbmcgui.getCurrentWindowId()
		self.eventBus.register( self )		
		self.isFinished = False	

		self.satelliteFormatedName = 'Unknown'
		self.allSatelliteList = []
		
		self.newTVChannelList = []
		self.newRadioChannelList = []

		self.tvListItems = []
		self.radioListItems =[]

		self.getControl( E_TV_LIST_ID ).reset( )
		self.getControl( E_RADIO_LIST_ID ).reset( )

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

		#tvListItems = []
		#radioListItems =[]

		count = len( self.newTVChannelList )
		for i in range( count ) :
			listItem = xbmcgui.ListItem( self.newTVChannelList[i], "TV", "-", "-", "-" )
			self.tvListItems.append( listItem )

		if count > 0 :
			self.getControl( E_TV_LIST_ID ).addItems( self.tvListItems )
			lastPosition = len( self.tvListItems ) - 1
			self.getControl( E_TV_LIST_ID ).selectItem( lastPosition )

		count = len( self.newRadioChannelList )
		for i in range( count ) :
			listItem = xbmcgui.ListItem( self.newRadioChannelList[i], "Radio", "-", "-", "-" )
			self.radioListItems.append( listItem )

		if count > 0 :
			self.getControl( E_RADIO_LIST_ID ).addItems( self.radioListItems )
			lastPosition = len( self.radioListItems ) - 1			
			self.getControl( E_RADIO_LIST_ID ).selectItem( lastPosition  )


		self.newTVChannelList = []
		self.newRadioChannelList = []


	def setSatellite( self, satelliteList ) :
		print 'scanBySatellite=%s' %satelliteList
		self.satelliteList = satelliteList		
		satellite = self.satelliteList[0]
		self.longitude = int( satellite[2] )
		self.band = int( satellite[3] )
		self.scanMode = E_SCAN_SATELLITE 



	def setTransponder( self, longitude, band, transponderList ) :
		print 'scanByTransponder=%s' %transponderList
		self.scanMode = E_SCAN_TRANSPONDER	
		self.longitude = longitude
		self.band = band		
		self.transponderList = transponderList


	def scanStart( self ) :

		self.allSatelliteList = []
		self.allSatelliteList = self.commander.satellite_GetList( ElisEnum.E_SORT_INSERTED )
		self.satelliteFormatedName = self.getFormattedName( self.longitude , self.band  )		

		print 'scanMode=%d' %self.scanMode
		if self.scanMode == E_SCAN_SATELLITE :
			satellite = self.satelliteList[0] # ToDO send with satelliteList
			self.commander.channelscan_BySatellite( int(satellite[2]), int(satellite[3]) ) #longitude, band
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

		if xbmcgui.getCurrentWindowId() == self.winId :

			if event[0] == ElisEvent.ElisScanAddChannel :
				self.updateAddChannel( event )

			elif event[0] == ElisEvent.ElisScanProgress :
				self.updateScanProgress( event )



	def updateScanProgress(self, event ):
		print 'update progress'
		totalCount = int( event[1] )
		currentIndex = int( event[2] )
		finished = int( event[3] )
		carrierType = int( event[4] )

		logitude = int( event[5] )
		band = int( event[6] )		
		
		frequency = int( event[7] )
		symbolrate = int( event[8] )
		fecValude = int( event[9] )
		polarization =  int( event[10] )

		percent = int( currentIndex*100/totalCount )

		print 'currentIndex=%d total=%d percent=%d finish=%d' %(currentIndex, totalCount, percent, finished )

		if finished == 0 and ( totalCount < 10 ) and ( currentIndex == totalCount ) :
			self.ctrlProgress.setPercent( 90 )
		else:
			self.ctrlProgress.setPercent( percent )


		strPol = 'Vertical'
		if polarization == ElisEnum.E_LNB_HORIZONTAL or polarization == ElisEnum.E_LNB_LEFT :
			strPol = 'Horizontal'


		if self.longitude != logitude or self.band != band :
			self.longitude = logitude
			self.band = band
			self.satelliteFormatedName = self.getFormattedName( self.longitude , self.band  )
		
		strTransponderInfo = '%s - %d Mhz - %s - %d MS/s ' %( self.satelliteFormatedName, frequency, strPol, symbolrate )
		self.ctrlTransponderInfo.setLabel( strTransponderInfo )

		if finished and currentIndex >= totalCount :
			print 'finished'
			self.isFinished = True
			self.ctrlProgress.setPercent( 100 )

			tvCount = len( self.tvListItems )
			radioCount = len( self.radioListItems )
			searchResult = 'TV Channels : %d \nRadio Channels : %d' %( tvCount, radioCount )
			xbmcgui.Dialog( ).ok( 'Infomation', searchResult )


	def updateAddChannel(self, event ):

		print 'update addchnnel'
		channelName = event[3]
		serviceType = int( event[4] )
		print 'update addchnnel channelName=%s serviceType=%d' %( channelName, serviceType )
		if serviceType == ElisEnum.E_TYPE_TV :
			self.newTVChannelList.append( channelName )
		else :
			self.newRadioChannelList.append( channelName )

		self.drawItem( )


	def getFormattedName( self, longitude, band ) :

		found = False

		for satellite in self.allSatelliteList :
			if longitude == int( satellite[0]) and band == int( satellite[1] ) :
				found = True
				break

		if found == True :
			dir = 'E'

			tmpLongitude  = longitude
			if tmpLongitude > 1800 :
				dir = 'W'
				tmpLongitude = 3600 - longitude

			formattedName = '%d.%d %s %s' %( int( tmpLongitude/10 ), tmpLongitude%10, dir, satellite[2] )
			return formattedName

		return 'UnKnown'


