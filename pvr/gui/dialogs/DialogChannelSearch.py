
import xbmc
import xbmcgui
import time
import sys


from pvr.gui.BaseWindow import Action
from pvr.gui.BaseDialog import BaseDialog
from  pvr.TunerConfigMgr import *
from ElisEnum import ElisEnum

import pvr.ElisMgr
from pvr.Util import RunThread, GuiLock



# Control IDs
LABEL_ID_TRANSPONDER_INFO		= 104
PROGRESS_ID_SCAN				= 200
LIST_ID_TV						= 400
LIST_ID_RADIO					= 402
BUTTON_ID_CANCEL				= 300


# Scan MODE
E_SCAN_NONE					= 0
E_SCAN_SATELLITE			= 1
E_SCAN_TRANSPONDER			= 2



class DialogChannelSearch( BaseDialog ) :
	def __init__( self, *args, **kwargs ) :
		BaseDialog.__init__( self, *args, **kwargs )
		self.mCommander = pvr.ElisMgr.GetInstance( ).GetCommander( )
		self.mScanMode = E_SCAN_NONE
		self.mIsFinished = True
		self.mEventBus = pvr.ElisMgr.GetInstance().GetEventBus()
		self.mTransponderList = []
		self.mConfiguredSatelliteList = []
		self.mLongitude = 0
		self.mBand = 0

	def onInit( self ):
		self.mWinId = xbmcgui.getCurrentWindowId()
		self.mWin = xbmcgui.Window( self.mWinId  )
		self.mIsFinished = False	

		self.mSatelliteFormatedName = 'Unknown'
		self.mAllSatelliteList = []
		
		self.mNewTVChannelList = []
		self.mNewRadioChannelList = []

		self.mTvListItems = []
		self.mRadioListItems =[]

		self.getControl( LIST_ID_TV ).reset( )
		self.getControl( LIST_ID_RADIO ).reset( )

		self.mCtrlProgress = self.getControl( PROGRESS_ID_SCAN )
		self.mCtrlTransponderInfo = self.getControl( LABEL_ID_TRANSPONDER_INFO )		

		self.ScanStart( )
		self.DrawItem( )

		self.mEventBus.Register( self )		

	def onAction( self, aAction ):
		actionId = aAction.getId( )
		focusId = self.getFocusId( )
	
		if actionId == Action.ACTION_PREVIOUS_MENU :
			pass
		elif actionId == Action.ACTION_SELECT_ITEM :
			pass
				
		elif actionId == Action.ACTION_PARENT_DIR :
			self.ScanAbort( )

		elif actionId == Action.ACTION_MOVE_UP :
			pass
	
		elif actionId == Action.ACTION_MOVE_DOWN :
			pass

		elif actionId == Action.ACTION_MOVE_LEFT :
			pass
				
		elif actionId == Action.ACTION_MOVE_RIGHT :
			pass


	def onClick( self, aControlId ):
		focusId = self.getFocusId( )

		if focusId == BUTTON_ID_CANCEL :
			self.ScanAbort( )

	def onFocus( self, controlId ):
		pass


	def DrawItem( self ) :

		count = len( self.mNewTVChannelList )
		for i in range( count ) :
			listItem = xbmcgui.ListItem( self.mNewTVChannelList[i], "TV", "-", "-", "-" )
			self.mTvListItems.append( listItem )

		if count > 0 :
			self.getControl( LIST_ID_TV ).addItems( self.mTvListItems )
			lastPosition = len( self.mTvListItems ) - 1
			self.getControl( LIST_ID_TV ).selectItem( lastPosition )

		count = len( self.mNewRadioChannelList )
		for i in range( count ) :
			listItem = xbmcgui.ListItem( self.mNewRadioChannelList[i], "Radio", "-", "-", "-" )
			self.mRadioListItems.append( listItem )

		if count > 0 :
			self.getControl( LIST_ID_RADIO ).addItems( self.mRadioListItems )
			lastPosition = len( self.mRadioListItems ) - 1			
			self.getControl( LIST_ID_RADIO ).selectItem( lastPosition  )


		self.mNewTVChannelList = []
		self.mNewRadioChannelList = []


	def SetConfiguredSatellite( self, aSatelliteList ) :
		print 'scanBySatellite=%s' %aSatelliteList
		self.mConfiguredSatelliteList = aSatelliteList		
		satellite = self.mConfiguredSatelliteList[0]
		self.mLongitude = satellite.mSatelliteLongitude
		self.mBand = satellite.mBandType
		self.mScanMode = E_SCAN_SATELLITE 



	def SetTransponder( self, aLongitude, aBand, aTransponderList ) :
		print 'scanByTransponder=%s' %aTransponderList
		self.mScanMode = E_SCAN_TRANSPONDER	
		self.mLongitude = aLongitude
		self.mBand = aBand		
		self.mTransponderList = aTransponderList


	def ScanStart( self ) :

		self.mAllSatelliteList = []
		self.mAllSatelliteList = self.mCommander.Satellite_GetList( ElisEnum.E_SORT_INSERTED )
		self.mSatelliteFormatedName = self.GetFormattedName( self.mLongitude , self.mBand  )		

		print 'scanMode=%d' %self.mScanMode
		if self.mScanMode == E_SCAN_SATELLITE :
			config = self.mConfiguredSatelliteList[0] # ToDO send with satelliteList
			self.mCommander.Channelscan_BySatellite( config.mSatelliteLongitude, config.mBandType ) #longitude, band
		elif self.mScanMode == E_SCAN_TRANSPONDER :
			self.mCommander.Channel_SearchByCarrier( self.mLongitude, self.mBand, self.mTransponderList )
		else :
			self.mIsFinished == True


	def ScanAbort( self ) :
		if self.mIsFinished == False :
			if xbmcgui.Dialog( ).yesno('Confirm', 'Do you want abort channel scan?') == 1 :
				self.mCommander.Channelscan_Abort( )
				self.mIsFinished == True

		if self.mIsFinished == True :
			self.mEventBus.Deregister( self )
			self.close( )

	@GuiLock
	def onEvent( self, aEvent ):

		if xbmcgui.getCurrentWindowId() == self.mWinId :

			if aEvent.getName() == ElisEventScanAddChannel.getName():
				self.UpdateAddChannel( aEvent )

			elif aEvent.getName() == ElisEventScanProgress.getName():
				self.UpdateScanProgress( aEvent )



	def UpdateScanProgress(self, aEvent ):

		percent = 0
		
		if aEvent.mAllCount > 0 :
			percent = int( aEvent.mCurrentIndex*100/aEvent.mAllCount )
		

		print 'currentIndex=%d total=%d percent=%d finish=%d' %(aEvent.mCurrentIndex, aEvent.mAllCount, percent, aEvent.mFinished )

		if aEvent.mFinished == 0 and ( aEvent.mAllCount < 10 ) and ( aEvent.mCurrentIndex == aEvent.mAllCount ) :
			self.mCtrlProgress.setPercent( 90 )
		else:
			self.mCtrlProgress.setPercent( percent )


		if aEvent.mCarrier.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBS :
			strPol = 'Vertical'
			if aEvent.mCarrier.mDVBS.mPolarization == ElisEnum.E_LNB_HORIZONTAL or aEvent.mCarrier.mDVBS.mPolarization == ElisEnum.E_LNB_LEFT :
				strPol = 'Horizontal'

			if self.mLongitude != aEvent.mCarrier.mDVBS.mSatelliteLongitude or self.mBand != aEvent.mCarrier.mDVBS.mSatelliteBand :
				self.mLongitude = aEvent.mCarrier.mDVBS.mSatelliteLongitude
				self.mBand = aEvent.mCarrier.mDVBS.mSatelliteBand
				self.mSatelliteFormatedName = self.GetFormattedName( self.mLongitude , self.mBand  )
			
			strTransponderInfo = '%s - %d Mhz - %s - %d MS/s ' %( self.mSatelliteFormatedName, aEvent.mCarrier.mDVBS.mFrequency, strPol, aEvent.mCarrier.mDVBS.mSymbolRate )
			self.mCtrlTransponderInfo.setLabel( strTransponderInfo )

		elif aEvent.mCarrier.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBT :
			pass

		elif aEvent.mCarrier.mCarrierType == ElisEnum.E_CARRIER_TYPE_DVBC :
			pass


		if aEvent.mFinished and aEvent.mCurrentIndex >= aEvent.mAllCount :
			print 'finished'
			self.mIsFinished = True
			self.mCtrlProgress.setPercent( 100 )

			tvCount = len( self.mTvListItems )
			radioCount = len( self.mRadioListItems )
			searchResult = 'TV Channels : %d \nRadio Channels : %d' %( tvCount, radioCount )
			xbmcgui.Dialog( ).ok( 'Infomation', searchResult )


	def UpdateAddChannel(self, aEvent ):

		print 'update addchnnel channelName=%s serviceType=%d' %( aEvent.mIChannel.mName, aEvent.mIChannel.mServiceType )
		if serviceType == ElisEnum.E_TYPE_TV :
			self.mNewTVChannelList.append( aEvent.mIChannel.mName )
		else :
			self.mNewRadioChannelList.append( aEvent.mIChannel.mName )

		self.DrawItem( )


	def GetFormattedName( self, aLongitude, aBand ) :

		found = False

		for satellite in self.mAllSatelliteList :
			if aLongitude == satellite.mLongitude and aBand == satellite.mBand :
				found = True
				break

		if found == True :
			dir = 'E'

			tmpLongitude  = aLongitude
			if tmpLongitude > 1800 :
				dir = 'W'
				tmpLongitude = 3600 - aLongitude

			formattedName = '%d.%d %s %s' %( int( tmpLongitude/10 ), tmpLongitude%10, dir, satellite.mName )
			return formattedName

		return 'UnKnown'


